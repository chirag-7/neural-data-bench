"""
script for evaluating 3d stardist segmentation models against a training set 
"""

import os
from matplotlib import pyplot as plt
import seaborn as sns
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
import test

matplotlib.rcParams["image.interpolation"] = "nearest"
import gc
from tqdm import tqdm
from tifffile import imread
import tensorflow as tf
import pickle
import itertools
import sys
from skimage import filters
from typing import Optional, Callable

from SynAPSeg.utils import utils_image_processing as uip
from SynAPSeg.utils import utils_plotting as up
from SynAPSeg.utils import utils_general as ug
from SynAPSeg.utils import utils_ML as uML
from SynAPSeg.IO.env import verify_and_set_env_dirs
from SynAPSeg.IO.writers import write_array
from SynAPSeg.Train.deepd3_prediction_3d import deepd3_predictor
import SynAPSeg.Train.benchmark as Bench
import SynAPSeg.Train.evaluate as Eval
from SynAPSeg.Segmentation.classical_methods_optimizer import (
    ThreshSegMethod, run_3d_watershed, batch_classic_seg, run_optimize_classic_seg,
    optimize_watershed_params, get_auto_thresh_methods, get_best_result
)

rng = np.random.RandomState(42)
print(uML.check_gpu())
from SynAPSeg.Train.benchmark import get_benchmark_dataset_as_testset
from SynAPSeg.Train.evaluate import create_cellpose_predictor, create_stardist_model
import re


def classic_thresh(img, gt=None, param_grid=None):

    trymethods = get_auto_thresh_methods()
    best_func, best_thresh_iou, mask = get_best_result(trymethods, img, gt)
    mask = mask>0
    
    # 3. Run Optimization
    param_grid = param_grid or {
        'sigma': [0.25, 0.5, 1.0, 1.5, 2.0],
        'min_distance': [1, 3, 5, 8]
    }

    best_params, best_iou, best_pred = optimize_watershed_params(mask, gt, param_grid)
    return best_pred


def mipl(listOf3dArrs):
    """ helper to get mip of 3d arrays in list for display. if 2d array, just return as is. """
    return [uip.mip(a,0) if a.ndim==3 else a for a in listOf3dArrs]
    


if bool(1) and __name__=='__main__':
    # setup 
    ########################################################################################
    verify_and_set_env_dirs(dict(
        MODELS_BASE_DIR = r"J:\SynAPSeg_dataset\Models",
    ))
    SYNAPSEG_DATASET_PATH = r"J:\SynAPSeg_dataset\TrainingDatasets"
    FIGOUTDIR = ""
    
    do_3D = bool(1)
    dataset = ['train', 'val'][1]
    get_ds_inds = None
    outfn_suffix = '_'.join([('3D'if do_3D else '2D'), dataset])
    thedate = ug.get_datetime()
    
    sd_load_params = {
        'load_model_kwargs': {'weights_filename':'weights_best.h5'}
    }
    cellPose_params = dict(
        do_3D=do_3D,        # enable 3D segmentation
        z_axis=0 if do_3D else None,          # axis in volume for Z
        min_size=5,
        normalize=True, # for some reason better when true, even though it's trained on the already normalized data
    )
    
    eval_params = dict(
        pred_padding=8, 
        taus=[0.5],
        centroid_match_max_dist=4,
    )
    viz_model_comp_params = dict(
        image_indices=None,
        n_examples = 3,
        # outpath=os.path.join(FIGOUTDIR, f'{thedate}_evaluateModels_{outfn_suffix}_visualize_model_comparison_contours.svg'),
    )


    ########################################################################################
    # dataset-specific configs
    ########################################################################################

    # load data
    nD = '3D' if do_3D else '2D'
    data_imgs_fn = f'{dataset}_patches_{nD}_images.tiff'
    data_lbls_fn = f'{dataset}_patches_{nD}_labels.tiff'
    testX = uip.read_img(os.path.join(SYNAPSEG_DATASET_PATH, nD, 'patches', data_imgs_fn)).astype('float32')
    testY = uip.read_img(os.path.join(SYNAPSEG_DATASET_PATH, nD, 'patches', data_lbls_fn)).astype('int32')
    testX, testY = uip.unpack_array_axis(testX, 0), uip.unpack_array_axis(testY, 0)
    
    
    # 3d datasets
    ########################################################################
    if do_3D:
        if dataset == 'train':
            viz_model_comp_params.update({'n_examples':3})
                    
        elif dataset == 'val':
            viz_model_comp_params.update({'n_examples':None, 'image_indices':None})

    # 2d Datasets
    ########################################################################
    else:
        # pre-process - unpadding
        prefunc = lambda x: uip.unpad(x, 8)
        testX, testY = list(map(prefunc, testX)), list(map(prefunc, testY))
        
        if dataset == 'train':
            viz_model_comp_params.update({'n_examples':7, 'image_indices':None})
            
        elif dataset == 'val':         
            viz_model_comp_params.update({'n_examples':7, 'image_indices':None})
        
    
    # data summary and show
    #######################################################################
    print(
        f"n imgs: {len(testX)}. n ulbls total: {np.sum([len(uip.unique_nonzero(a)) for a in testY])}\n",
        f"{uip.pai(testX[0], asstr=True)}",
        f"{uip.pai(testY[0], asstr=True)}",
        sep='',
    )
    _plt_img_i = 0
    up.plot_image_grid(mipl([testX[_plt_img_i], testY[_plt_img_i]]))
    
    # show all 
    if bool(0):
        up.plot_image_grid(
            mipl(testX), masks=mipl(testY),
            titles = [f'img_{i}' for i in range(len(testX))],
            # outpath=os.path.join(FIGOUTDIR, f'{thedate}_evaluateModels_{outfn_suffix}_testXY.svg'),
        )    
 

    # setup and load methods/models
    ########################################################################################
    models_dict = {
        "threshold + watershed": classic_thresh,
        "deepd3": deepd3_predictor(
            r"D:\BygraveLab\segmentation\synapse_datasets\online_datasets\deepd3\models\DeepD3_32F_94nm.h5",
            pred_thresh = 0.238 if not do_3D else 0.325
        ),
    }

    if not do_3D: # 2d models
        models_dict.update({ # ty:ignore[no-matching-overload]
        'cellpose_default': create_cellpose_predictor(flow_threshold=0.8, **cellPose_params),
        'cellpose_custom': create_cellpose_predictor(model_path=os.path.join(os.environ['MODELS_BASE_DIR'], r"Cellpose_custom_2D\cellpose_2D_v2.1.0"), **cellPose_params),
        'stardist_default': create_stardist_model(model_name='2D_versatile_fluo', preprocessing_kwargs={"norm":None}),
        'stardist_custom': create_stardist_model(model_name='StarDist_custom_2D', preprocessing_kwargs={"norm":None}, **sd_load_params),
        })
    else: # MODELS_3D
        models_dict.update({ # ty:ignore[no-matching-overload]
        'cellpose_default': create_cellpose_predictor(flow_threshold=0.6, **cellPose_params),
        'cellpose_custom': create_cellpose_predictor(model_path=os.path.join(os.environ['MODELS_BASE_DIR'], r"Cellpose_custom_3D\cellpose3D_v4"), **cellPose_params),
        "stardist_default": create_stardist_model(model_name='3D_demo', fmt='ZYX', preprocessing_kwargs={"norm":None}),
        "stardist_custom": create_stardist_model(model_name='StarDist_custom_3D', fmt='ZYX', preprocessing_kwargs={"norm":None}, **sd_load_params),
        })  
    
    
    
    ########################################################################################
    # get predictions
    ########################################################################################
    
    # results is list[dict] of len(n_models), each subdict has keys 'predictions', 'image_metrics', 'overall_metrics', 'model_name'
    results, comparison = Eval.evaluate_models(
        testX, testY, models_dict, **eval_params
    )
    
    # compile and update by img results with multirater info
    img_results = Eval.get_by_img_results(results)
    
    
    # update comparison summary to include full set of metrics (averaged over all examples)
    ########################################################################################
    comp = (comparison).merge(
        img_results.groupby(["model_name", "dataset_name"]).mean().reset_index(),
        left_on=["model_name", "dataset_name"] if "dataset_name" in comparison.columns else ["model_name"],
        right_on=["model_name", "dataset_name"] if "dataset_name" in comparison.columns else ["model_name"],
        how="outer",
    )
    print(comp[["model_name", "overall_f1", "avg_iou_mean", "percent_true_positives"]])

    # params for metrics plots
    maybe_search_group = lambda m, default: m.group() if m is not None else default
    hue_var_params = dict(
        results_key="model_name",
        plot_as="model",
        transform_func=lambda s: maybe_search_group(re.search('(v\d\.\d\.\d(\.\d)?)', s), s),
        palette=['#737373', "#c994c7",'#92c5de', "#2166ac", '#fcbba1', '#dd1c77'],
        grpby_keys = (),
    )
    # apply transformations to metrics for plotting
    sumdf, compiled_img_metrics = Eval.compile4plotting(results, hue_var_params)

    
    
    # plotting 
    ########################################################################################    
    
    # visual comparison
    ######################
    Eval.visualize_model_comparison(testX, testY, results, **viz_model_comp_params)

    # bar plots 
    ######################    
    Eval.visualize_model_all_metrics(
        img_results.rename(columns={
            'precision':'overall_precision','recall':'overall_recall','f1_score':'overall_f1',
            **{f"centroid_{c}":f"centroid_{c}_mean" for c in ["precision","recall","f1_score"]},
            **{c:f"{c}_mean" for c in ['hausdorff_mean','hausdorff_max','centroid_mean','centroid_max']}
        }),
        hue_var_params, 
        FIGOUTDIR=FIGOUTDIR, 
        OUTNAME_PREFIX=f"{thedate}_evaluateModels_{outfn_suffix}"
    )
    
    if FIGOUTDIR:
        sumdf.to_excel(
            os.path.join(FIGOUTDIR, f"{thedate}_evaluateModels_{outfn_suffix}_metrics.xlsx"), index=False
        )

    # iou thresholds curve
    ######################
    sdmetric_scores = Eval.compile_eval_over_iou_thresholds(
            results, testY, 
            taus = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
            get_ks = ['model_name', 'dataset_name'], # id info 
    )
    sdmetric_scores['% true positives'] = sdmetric_scores['tp'] / sdmetric_scores['n_true']
    
    Eval.plot_eval_over_iou_thresholds(
        sdmetric_scores, 
        FIGOUTDIR, thedate, outfn_suffix, 
        hue_var_params,
        plt_metrics=['recall', 'f1'],
    )
    
    if FIGOUTDIR:
        sdmetric_scores.to_excel(
            os.path.join(FIGOUTDIR, f"{thedate}_evaluateModels_{outfn_suffix}_metrics_iouThresholds.xlsx"), index=False
        )
