import itertools
from copy import deepcopy
from param import bind
import tifffile
import os
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
from pathlib import Path
import sys
import skimage
from skimage.measure import regionprops
import glob
import re
from skimage import io


from SynAPSeg.utils import utils_image_processing as uip
from SynAPSeg.utils import utils_plotting as up
from SynAPSeg.utils import utils_general as ug
from SynAPSeg.utils import utils_colocalization as uc

# FINAL VERSION 

def format_annot(arr, error_check=True, force2d=True):
    """ raw annotation pre-processing. force 2d used for displaying images """
    # mip
    if arr.ndim == 2:
        pass
    elif arr.ndim == 3:
        if force2d:
            arr = uip.mip(arr, axis=0)
    else: 
        raise ValueError(uip.pai(arr))
    
    # label connected components
    uLblB4 = len(uip.unique_nonzero(arr))
    lbld = uip.relabel(arr, connectivity=arr.ndim)
    c1 = len(uip.unique_nonzero(lbld))

    # remove accidental tiny lbls
    lbld = skimage.morphology.remove_small_objects(lbld, min_size=4)

    if error_check:
        if c1 < uLblB4: 
            raise ValueError(f'labeling resulting in less labels than before {uLblB4} --> {c1}')
    
    return(lbld.astype('int32'))

def display_image_and_annotation_overlays(folder_path, write_outputs=False):
    """
    Load the image and each annotator's segmentation from the specified folder,
    then display the original image and the overlay of each annotator's segmentation
    arranged in a grid.
    
    Folder structure assumed:
      folder_path/
          image.tiff
          annotations/
              annotated_<annotator1>_(.*).tiff
              ...
    """
    # Load the original image
    image_file = os.path.join(folder_path, 'image.tiff')
    image_raw = io.imread(image_file)
    image_raw = uip.norm_percentile(image_raw, norm=(1,99.9), ch_axis=None)
    image = uip.mip(image_raw, axis=0) if image_raw.ndim ==3 else image_raw

    
    # Locate annotation files in the annotations subfolder
    annotation_dir = os.path.join(folder_path, 'annotations')
    annotation_files = glob.glob(os.path.join(annotation_dir, 'annotated_*_*.tiff'))
    
    # Extract annotator name and load their mask
    overlays = []
    pattern = re.compile(r"annotated_(.*?)_.*\.tiff", re.IGNORECASE)
    for ann_file in annotation_files:
        basename = os.path.basename(ann_file)
        match = pattern.search(basename)
        if match:
            annotator_name = match.group(1)
            mask = io.imread(ann_file)
            mask = format_annot(mask)
            overlays.append((annotator_name, mask))
    
    # Total number of images to display: one original + one per annotator
    total_images = 1 + len(overlays)
    
    # Determine grid dimensions (attempt a square-ish layout)
    n_cols = int(np.ceil(np.sqrt(total_images)))
    n_rows = int(np.ceil(total_images / n_cols))
    
    # Create the figure and axes
    h_aspect = image.shape[0]/image.shape[1] # rows/cols so if wide img --> <1
    w_aspect = image.shape[1]/image.shape[0] # cols/rows so if wide img --> >1
    # ensure the large one maxes at 1
    h_aspect = (1) if h_aspect>w_aspect else h_aspect
    h_aspect = (1) if w_aspect>h_aspect else w_aspect
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(5 * n_cols * w_aspect, 5 * n_rows * h_aspect))
    
    # Flatten axes array for easier iteration, regardless of grid shape.
    if isinstance(axes, np.ndarray):
        axes = axes.flatten()
    else:
        axes = [axes]
    
    # Plot the original image in the first subplot.
    axes[0].imshow(image, cmap='gray')
    axes[0].set_title("Original Image")
    axes[0].axis('off')
    
    # For each annotator, overlay their segmentation on the original image.
    for i, (annotator, mask) in enumerate(overlays):
        ax = axes[i + 1]
        # up.overlay_colored_outlines(mask, image, )
        up.mask_to_outline_contours(
            image, mask, iterations=1, alpha=1, ax=ax,
            label_cmap=True,
            c_func = lambda x: (1,0,0,0.7),
            # linewidth=0.5
            
        )
        # ax.imshow(image, cmap='gray')  # show the original image
        # Overlay the segmentation mask in red with 50% transparency.
        # ax.imshow(mask, cmap='Reds', alpha=0.5)
        ax.set_title(f"Annotation: {annotator}")
        ax.axis('off')
    
    # Hide any extra subplots (if grid size > number of images)
    for j in range(total_images, len(axes)):
        axes[j].axis('off')
    
    plt.tight_layout()
    if write_outputs: up.save_fig(os.path.join(FIGOUTDIR, f"image_and_annotation_overlays_{Path(folder_path).name}.svg"), dpi=300)
    plt.show()

    annotations = {el[0]:el[1] for el in overlays}
    return image, annotations




def compute_pairwise_dice(data):
    """
    Compute pairwise Dice coefficients for every example folder and return a DataFrame.
    The DataFrame contains columns: Folder, Annotator1, Annotator2, Dice.
    """
    results = []
    for folder, content in data.items():
        annotations = content["annotations"]
        annotators = list(annotations.keys())
        if len(annotators) < 2:
            continue
        for i in range(len(annotators)):
            for j in range(i + 1, len(annotators)):
                a1 = annotators[i]
                a2 = annotators[j]
                mask1 = annotations[a1]
                mask2 = annotations[a2]
                dice = dice_coefficient(mask1, mask2)
                results.append({
                    "Folder": folder,
                    "Annotator1": a1,
                    "Annotator2": a2,
                    "Dice": dice
                })
    dice_df = pd.DataFrame(results)
    matricies = dicedf_to_matrix(dice_df)
    return dice_df, matricies

def dice_coefficient(mask1, mask2):
    """
    Compute the Dice coefficient between two binary masks.
    """
    mask1 = mask1.astype(bool)
    mask2 = mask2.astype(bool)
    intersection = np.logical_and(mask1, mask2).sum()
    sum_masks = mask1.sum() + mask2.sum()
    if sum_masks == 0:
        return np.nan
    return 2 * intersection / sum_masks

def dicedf_to_matrix(dice_df):
    datasets, annotators = list(dice_df['Folder'].unique()), sorted(list(set(dice_df[['Annotator1', 'Annotator2']].values.flatten())))
    annotator2idx = dict(zip(annotators, range(len(annotators))))
    matricies = {}
    for ds in datasets:
        matricies[ds] = np.full((len(annotators), len(annotators)), np.nan)
        _df = dice_df[dice_df['Folder']==ds]
        for rowi, row in _df.iterrows():
            a1, a2, val = row[['Annotator1', 'Annotator2', 'Dice']]
            val = np.nan if val == 0 else val
            matricies[ds][annotator2idx[a1], annotator2idx[a2]] = val
            matricies[ds][annotator2idx[a2], annotator2idx[a1]] = val

        matricies[ds] = pd.DataFrame(matricies[ds], index=annotators, columns=annotators)
    return matricies
    
    
def compute_annotation_counts(data):
    """
    For each example folder and each annotator, count the number of segmented (nonzero) pixels.
    Returns a DataFrame with columns: Folder, Annotator, Count.
    """
    rps_to_get = [
        'label', 'area', 'bbox', 'centroid', 'intensity_mean', 'intensity_min', 'intensity_max'
    ]
    results, rpdfs = [], []
    for folder, content in data.items():
        annotations = content["annotations"]
        for annotator, mask in annotations.items():
            
            count = len(uip.unique_nonzero(mask))
            
            img = content['image']
            if mask.ndim==3:
                mask = np.expand_dims(mask,-1)
                img = np.expand_dims(img,-1)

            rpdf = uc.get_rp_table(mask, img, rps_to_get=rps_to_get, get_object_coords=True)
            rpdf = rpdf.assign(folder=folder, annotator=annotator)
            rpdfs.append(rpdf)
            results.append({
                "Folder": folder,
                "Annotator": annotator,
                "Count": count,
            })
    return pd.DataFrame(results), pd.concat(rpdfs, ignore_index=True)


def load_annotation_data(base_dir, examples=None, deidentify_annotators=False, assign_aliases=None):
    """
    Load data from the base directory and return a dictionary where each key is an example folder
    and the value is a dictionary with the image and a sub-dictionary of annotation masks.
    
    Expected folder structure:
    base_dir/
        Example_1/
            image.tiff
            annotations/
                annotated_<annotator>_labels.tiff
        Example_2/
            image.tiff
            annotations/
                annotated_<annotator>_labels.tiff
        ...
    """
    if examples is not None:
        folders_to_analyze = examples
    else:
        folders_to_analyze = os.listdir(base_dir)


    data, all_annotators = {}, set()
    for folder in folders_to_analyze:
        folder_path = os.path.join(base_dir, folder)
        if not os.path.isdir(folder_path):
            continue

        image_file = os.path.join(folder_path, "image.tiff")
        annotations_dir = os.path.join(folder_path, "annotations")
        if not os.path.exists(image_file) or not os.path.isdir(annotations_dir):
            print(f"Skipping {folder} due to missing image or annotations folder.")
            continue

        # Load the main image.
        image = io.imread(image_file)
        # normalize pixel intensities to [0,1]
        image = uip.normalize_01(image)
        n_dim = image.ndim
        # Build a dictionary of annotation masks.
        annotations, raw_annotations = {}, {}
        pattern = re.compile(r"annotated_(.*?)_.*\.tiff", re.IGNORECASE)
        annotation_files = glob.glob(os.path.join(annotations_dir, "annotated_*_*.tiff"))
        for ann_file in annotation_files:
            basename = os.path.basename(ann_file)
            match = pattern.search(basename)
            if match:
                annotator = match.group(1)
                mask = io.imread(ann_file)
                raw_annotations[annotator] = mask

                mask = format_annot(mask, force2d=False)
                if mask.ndim==3 and n_dim == 2:
                    mask = uip.mip(mask, axis=0)
                annotations[annotator] = mask
                all_annotators.add(annotator)
        
        folder_alias = dirNameMap[folder]
        data[folder_alias] = {"image": image, "annotations": annotations, "raw_annotations": raw_annotations}
    
    deid_map = ug.sort_dict_by_list({k:k for k in all_annotators}, [i for i in sorted(all_annotators) if not PREDIDSTRING in i])
    if deidentify_annotators:
        data, deid_map = deidentify_data(data, except_annotators = ['predStardist'], assign_aliases=assign_aliases)
    return data, deid_map

def deidentify_data(data, except_annotators = ['predStardist'], assign_aliases=None):
    """ replace individuals names with a string, except for predictions """
    aliases = [el for el in 'ABCDEFGHIJK']
    # get all annotators
    annotators2alias = assign_aliases or {}
    new_data = {}
    for folder, d in data.items():
        new_data[folder] = {}
        for k, v in d.items():
            if k == 'annotations':  
                deid = {}
                for antr, mask in v.items():
                    
                    if antr not in annotators2alias:
                        if antr in except_annotators:
                            annotators2alias[antr] = antr
                        elif ug.any_isin(antr, except_annotators): # match string 
                            annotators2alias[antr] = antr
                        else:
                            annotators2alias[antr] = aliases.pop(0)
                    
                    
                    alias = annotators2alias[antr]
                    deid[alias] = mask
                v = deid
            new_data[folder][k] = v
    return new_data, {v:k for k,v in annotators2alias.items()}
            




def pixelwise_correlation(mask1, mask2):
    """
    Calculate the pixelwise Pearson correlation between two masks.
    
    Parameters:
        mask1 (np.ndarray): First mask array.
        mask2 (np.ndarray): Second mask array.
        
    Returns:
        float: Pearson correlation coefficient between the two masks.
    """
    if mask1.shape != mask2.shape:
        raise ValueError("Both masks must have the same dimensions.")

    flat1 = mask1.flatten()
    flat2 = mask2.flatten()
    
    # Calculate the correlation matrix and extract the correlation coefficient.
    correlation_matrix = np.corrcoef(flat1, flat2)
    return correlation_matrix[0, 1]

def visualize_pixelwise_correlations(data):
    """ not sure if provides novel info over iou heatmap """
    # pixel-wise correlations
    ds = all_ex_dirs[-1]
    d = data[ds]
    ans = d['annotations']
    antrs = list(ans.keys())
    antr2idx = dict(zip(antrs, range(len(antrs))))

    pxcorr = np.full((len(antrs), len(antrs)), np.nan)
    for antr1, mask1 in ans.items():
        for antr2, mask2 in ans.items():
            # if antr1 == antr2: 
            #     continue
            pxc = pixelwise_correlation(mask1.astype(bool), mask2.astype(bool))
            pxcorr[antr2idx[antr1], antr2idx[antr2]] = pxc
    pxc_df = pd.DataFrame(pxcorr, columns=antrs, index=antrs)


    sns.heatmap(data=pxc_df, square=True, vmin=0, vmax=1, cmap='RdYlGn', annot=True)


def visualize_dice_results(df):
    """
    Generate a boxplot with overlaid scatter points of Dice coefficients for each example folder.
    Each scatter point is annotated with "Annotator1 vs Annotator2".
    """
    plt.figure(figsize=(10, 6))
    folders = df["Folder"].unique()
    # Prepare data for boxplot.
    data = [df[df["Folder"] == folder]["Dice"].dropna() for folder in folders]
    positions = np.arange(1, len(folders) + 1)
    
    plt.boxplot(data, labels=folders, positions=positions)
    
    # Overlay scatter points with annotation labels.
    for i, folder in enumerate(folders):
        folder_df = df[df["Folder"] == folder]
        x = np.full(len(folder_df), i + 1)
        y = folder_df["Dice"].values
        plt.scatter(x, y, color="black", zorder=3)
        for xi, yi, a1, a2 in zip(x, y, folder_df["Annotator1"], folder_df["Annotator2"]):
            plt.annotate(f"{a1} vs {a2}", (xi, yi),
                         textcoords="offset points", xytext=(5, 5),
                         fontsize=8, color="blue")
    
    plt.xlabel("Example Folder")
    plt.ylabel("Dice Coefficient")
    plt.title("Inter-Annotator Variability Analysis (Dice)")
    plt.tight_layout()
    if WRITE_OUPUTS: up.save_fig(os.path.join(FIGOUTDIR, "dice_result_labeledBar.svg"), dpi=300)
    plt.show()


def visualize_dice_corr(dice_matricies, figsize=(1.6*3, 1.8)):
    """visualize dice scores as heatmap"""
    datasets = list(dice_matricies.keys())
    fig,axs = plt.subplots(nrows=1, ncols=len(datasets), figsize=figsize, sharey=True)
    for iii, (ds, corrdf) in enumerate(dice_matricies.items()):
        
        corrdfplot = corrdf.copy(deep=True)
        # add diag
        basediag = np.where(np.diag(np.arange(len(corrdf)))>0, 1, np.nan)
        basediag[0,0] = 1
        # remove missing annotators
        for i, r in enumerate(corrdf.values):
            if all(pd.isnull(r)):
                basediag[i,i] = np.nan
        # bdf = pd.DataFrame(data=basediag, index=corrdf.index, columns=corrdf.columns)
        for i in range(basediag.shape[0]):
            for j in range(basediag.shape[1]):
                if pd.isnull(basediag[i,j]):
                    continue
                else:
                    corrdfplot.iloc[i,j] = basediag[i,j]

        ax = axs[datasets.index(ds)]
        sns.heatmap(corrdfplot, ax=ax, square=True, vmin=0, vmax=1, cmap="PiYG", cbar=False)
        ax.set_title(f"{iii+1}")
        ax.tick_params(axis='x', rotation=30)
        for label in ax.get_xticklabels():
            label.set_horizontalalignment('right')
        
    if WRITE_OUPUTS: up.save_fig(os.path.join(FIGOUTDIR, "dice_corr.svg"), dpi=300)
    plt.show()

def visualize_dice_annotator_avg(dice_matricies, figsize=(2,4)):
    "calculate average of each annotators agreement with the others"
    datasets = list(dice_matricies.keys())
    avg_ious = []
    for ds in datasets:
        for antr in dice_matricies[ds].columns:
            vals = dice_matricies[ds][antr]
            avg = np.mean(vals)
            is_pred = True if PREDIDSTRING in antr else False
            avg_ious.append({
                'Folder':ds,
                'Annotator': antr,
                'mean IOU': avg,
            })
    avgIou_df = pd.DataFrame(avg_ious)

    fig,ax= plt.subplots(figsize=figsize)
    
    sns.boxplot(**ug.merge_dicts(dict(
        data=avgIou_df, 
        x='Folder', 
        y='mean IOU', 
        ax=ax), 
        BOXPROPS, 
    ))
    

    up.jittered_scatterplot(
        data=avgIou_df,
        x='Folder',
        order = FOLDER_ORDER,
        y='mean IOU',
        hue='Annotator',
        palette=ANNOTATOR_PALETTE,
        style='Annotator',       # Use the 'marker' column for different markers
        markers=MARKER_PALETTE,         # Let seaborn handle marker styles or define a dict
        ax=ax,         # Avoid double legend
        jitter_strength=0.1,
        legend=False,
        **JITTERSCATTERPROPS
    )
    plt.xticks([0,1,2], ['1','2','3'])
    plt.ylabel("mean IoU score")
    ax.set_ylim(0.0, 0.85)
    plt.xlabel("Dataset")
    sns.despine()
    if WRITE_OUPUTS: up.save_fig(os.path.join(FIGOUTDIR, "avg_annotator_dice_scores.svg"), dpi=300)
    plt.show()

# visualize_dice_annotator_avg(dice_matricies)


def visualize_annotation_counts(counts_df, figsize=(1.5, 4)):
    """
    Generate a grouped bar chart comparing annotation counts for each example folder.
    """
    # Pivot the DataFrame to have folders as rows and annotators as columns.
    fig,axs = plt.subplots(figsize=figsize)
    pivot_df = counts_df.copy(deep=True) #.pivot(index="Folder", columns="Annotator", values="Count")
    
    if bool(0):
        trfd = [] # adjust counts so centered around median
        for _ds, adf in pivot_df.groupby(['Folder']):
            median  = adf.query("Annotator.str.startswith(\'expert\')")['Count'].median()
            adf['Count'] = ((adf['Count']-median)/median *100) + 100
            trfd.append(adf)
        pivot_df = pd.concat(trfd, ignore_index=True)
    
    _order = ['1','2','3']
    pivot_df['dataset'] = pivot_df['Folder'].map(dict(zip(FOLDER_ORDER, _order)))

    sns.boxplot(
        **ug.merge_dicts(dict(
        data=pivot_df, 
        x='dataset', 
        y='Count', 
        order = _order,
        ax=axs, 
        legend=False,
    ), BOXPROPS))


    up.jittered_scatterplot(
        data=pivot_df,
        x='dataset',
        order = _order,
        y='Count',
        hue='Annotator',
        hue_order=sorted(list(ANNOTATOR_PALETTE.keys())),
        palette=ANNOTATOR_PALETTE,
        style='Annotator',       # Use the 'marker' column for different markers
        markers=MARKER_PALETTE,         # Let seaborn handle marker styles or define a dict
        ax=axs,
        legend=False,         # Avoid double legend
        jitter_strength=0.1,
        **JITTERSCATTERPROPS
    )

    # Define positions and labels
    tick_positions = [30, 40, 50, 60, 70]
    tick_labels = [str(el) for el in tick_positions]

    # Set the positions first
    axs.set_yticks(tick_positions)

    # Set the labels (optional: you can also rotate them)
    axs.set_yticklabels(tick_labels)
    
    plt.xlabel("Dataset")
    plt.ylabel("Count")
    plt.title("")
    if axs.get_legend() is not None: 
        axs.get_legend().remove()
    plt.tight_layout()
    axs.spines[['right', 'top']].set_visible(False)
    plt.ylim(21, 79)
    if WRITE_OUPUTS: up.save_fig(os.path.join(FIGOUTDIR, "annotation_counts_raw2.svg"), dpi=300)
    plt.show()

# visualize_annotation_counts(counts_df, figsize=(1.4, 1.8))


def visualize_annotation_props(rpdfs, mean_val=True, figsize=(8,6)):
    """ plot avg properties for each annotators """
    plot_props = ['area', 'intensity_mean']
    grp_by = ['folder', 'annotator']
    
    if mean_val:
        plt_df = rpdfs.groupby(grp_by).mean(numeric_only=True).reset_index()
        plot_fxn = up.jittered_scatterplot
        kwargs = dict(
            order = ['1', '2', '3'],
            palette=ANNOTATOR_PALETTE,
            style='annotator',       # Use the 'marker' column for different markers
            markers=MARKER_PALETTE,         # Let seaborn handle marker styles or define a dict
            # edgecolor='black',    # Optional: make the points easier to see
            # linewidth=0.5,
            # s=60,                  # Adjust size for visibility
            jitter_strength=0.1,
        )
    else:
        plt_df = rpdfs.copy(deep=True)
        plot_fxn = sns.boxplot
        kwargs = {}
    
    asstrs = [str(el) for el in list(range(1, len(FOLDER_ORDER)+1))]
    plt_df['dataset'] = plt_df['folder'].map(dict(zip(FOLDER_ORDER, asstrs)))

    

    fig, axs= plt.subplots(1,2, figsize=figsize)
    for axi, ax in enumerate(axs.flatten()):
        sns.boxplot(
            **ug.merge_dicts(dict(
            data=plt_df, x='dataset', y=plot_props[axi], 
            ax=ax, 
            legend=False,
            fill=False,
            **{k:v for k,v in kwargs.items() if k not in ['palette', 'style', 'markers', 's', 'jitter_strength', 'edgecolor', 'alpha', 'zorder', 'facecolor']}
        ), BOXPROPS, {'boxprops': {'color':'gray','linewidth': 2}}))
        plot_fxn(
            data=plt_df, x='dataset', y=plot_props[axi], hue='annotator', 
            ax=ax, 
            legend=False,
            **kwargs,
            **JITTERSCATTERPROPS
        )

        if ax.get_legend() is not None: 
            ax.get_legend().remove()
        
        ax.set_xlabel('Dataset')
    
    sns.despine()
    
    plt.tight_layout()
    
    if WRITE_OUPUTS: up.save_fig(os.path.join(FIGOUTDIR, "annotation_props.svg"), dpi=300)
    plt.show()



##############################
# Spine Consensus Analysis Module
##############################
def compute_spine_consensus(_data):
    """
    For each example folder, compute the consensus for each spine (i.e. connected component in the union
    of all annotators' binary masks). For each spine, determine how many annotators identified it.
    
    Returns a DataFrame with columns: Folder, Spine_Label, Consensus_Count, Area.
    """
    # _data = {k:v for k,v in data.items() if k=='easy2D'}
    # _data = data
    consensus_data = []
    for folder, content in _data.items():
        annotations = content["annotations"]
        if not annotations:
            continue

        num_annotators = len(annotations) - 1

        # Assume all annotations have the same shape.
        shape = next(iter(annotations.values())).shape
        binary_masks = {}
        votes = np.zeros(shape, dtype=int)
        for annotator, mask in annotations.items():
            # Create a binary mask (any nonzero pixel is part of a spine)
            binary = (mask > 0).astype(int)
            binary_masks[annotator] = binary
            votes += binary
        # Create a union mask (where any annotator marked a pixel)
        union_mask = votes > 0
        labeled_union = skimage.morphology.label(union_mask)
        regions = skimage.measure.regionprops(labeled_union, content['image'])
        for region in regions:
            consensus_count = 0
            agreeing_annotators = []
            model_found = 0
            for annotator, binary in binary_masks.items():
                # Check if any pixel in the region is marked in this annotator's binary mask.
                coords = region.coords
                if np.any(binary[coords[:, 0], coords[:, 1]]):
                    
                    if annotator in [PREDIDSTRING, 'model']:
                        model_found = 1
                    else:
                        consensus_count += 1
                        agreeing_annotators.append(annotator)

            if len(EXPERTS) > 0:
                percent_of_experts = len([an for an in agreeing_annotators if an in EXPERTS or an.startswith('Annotator')])/float(len(EXPERTS))
            else:
                percent_of_experts = len([an for an in agreeing_annotators])/num_annotators

            consensus_data.append({
                "Folder": folder,
                "Spine_Label": region.label,
                "Consensus_Count": consensus_count,
                "Consensus_Percent": consensus_count/num_annotators,
                "Area": region.area,
                "intensity_mean": region.intensity_mean,
                "agreeing_annotators": agreeing_annotators,
                "model_found": model_found,
                "percent_of_experts": percent_of_experts,
            })
    consensus_df = pd.DataFrame(consensus_data)

    consensus_summary = (
        consensus_df
        .groupby(['percent_of_experts'])
        .agg(
            num_synapses=('Spine_Label', 'size'),
            model_synapses=('model_found', 'sum'),
            intensity=('intensity_mean', 'mean'),
            area=('Area', 'mean'),
            model_percent=('model_found', 'mean'),
            consensus_percent=('Consensus_Percent', lambda s: np.round(np.mean(s), 2)),
        )
        .reset_index()
        .melt(id_vars=['percent_of_experts', 'intensity', 'area', 'model_percent', 'consensus_percent'], 
            value_vars=['num_synapses', 'model_synapses'], var_name='identified_by', value_name='synapse count'
        )
        .assign(
            N_experts = lambda df: (df['percent_of_experts']*4).astype('int'),
        )
    )

    return consensus_df, consensus_summary


def compute_pixelwise_votes(_data, include_model=False):
    """
    For each example folder, sum all binary annotation masks
    
    Returns a list with an array for each example 
    """
    # _data = {k:v for k,v in data.items() if k=='easy2D'}
    # _data = data
    all_data = []
    for folder, content in _data.items():
        annotations = content["annotations"]
        if not annotations:
            continue
        
        if not include_model:
            annotators = [k for k in annotations.keys() if k.lower().startswith('annotator')]
        else:
            annotators = list(annotations.keys())

        # Assume all annotations have the same shape.
        all_binmasks = np.stack(list([annotations[k] for k in annotators])).astype('bool')*1
        votes = all_binmasks.sum(axis=0)/len(all_binmasks)

        all_data.append(votes)
    return all_data


def visualize_spine_consensus(consensus_df):
    """
    Visualize the distribution of spine consensus counts.
    This function produces a grouped bar chart showing, for each folder, 
    the number of spines identified by a given number of annotators.
    """
    _AS_PERCENT_COUNT = bool(1)

    folders = sorted(consensus_df["Folder"].unique())
    # Determine the possible consensus counts.
    max_consensus = consensus_df["Consensus_Count"].max()
    consensus_range = np.arange(1, max_consensus + 1)
    
    # Set up the bar chart.
    fig, ax = plt.subplots(figsize=(10, 6))
    bar_width = 0.8 / len(folders)
    positions = np.arange(len(consensus_range))
    
    for i, folder in enumerate(folders):
        folder_df = consensus_df[consensus_df["Folder"] == folder]
        counts = [ (folder_df["Consensus_Count"] == c).sum() for c in consensus_range ]
        if _AS_PERCENT_COUNT:
            counts = np.array(counts)/np.sum(counts)
        x_positions = positions + i * bar_width
        ax.bar(x_positions, counts, width=bar_width, label=folder)
    
    y_label = 'Percent of Synapses' if _AS_PERCENT_COUNT else "Number of Synapses"

    ax.set_xlabel("Consensus Count (# of annotators that identified the synapse)")
    ax.set_ylabel(y_label)
    ax.set_title("Spine Consensus Analysis")
    ax.set_xticks(positions + bar_width * (len(folders) - 1) / 2)
    ax.set_xticklabels(consensus_range)
    ax.legend(title="Folder", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    if WRITE_OUPUTS: up.save_fig(os.path.join(FIGOUTDIR, "spine_consensus.svg"), dpi=300)
    plt.show()

def visualize_spine_consensus_summary(consensus_summary):
    sns.barplot(data=consensus_summary, x='N_experts', y='synapse count', hue='identified_by')
    if WRITE_OUPUTS: up.save_fig(os.path.join(FIGOUTDIR, "spine_consensus_summary_byExperts.svg"), dpi=300)
    plt.show()
    sns.barplot(data=consensus_summary, x='consensus_percent', y='synapse count', hue='identified_by')
    if WRITE_OUPUTS: up.save_fig(os.path.join(FIGOUTDIR, "spine_consensus_summary_byAll.svg"), dpi=300)
    plt.show()


def visualize_experts_consensus_ranks(consensus_df):
    experts_consensus_rankings = {assign_aliases[expert]:[] for expert in EXPERTS}
    pcents = sorted(consensus_df['Consensus_Percent'].unique())
    cluster_map = dict(zip(pcents,range(1, len(pcents)+1) ))
    for rowi, row in consensus_df.iterrows():
        for expert in EXPERTS:
            alias = assign_aliases[expert]
            if alias in row['agreeing_annotators']:
                experts_consensus_rankings[alias].append(cluster_map[row['Consensus_Percent']])
    
    from collections import Counter
    expert_ranks_df = []
    for alias, ranks in experts_consensus_rankings.items():
        print(alias, np.mean(ranks))
        clust_cnts = dict(sorted(dict(Counter(ranks)).items()))
        vals = np.array(list(clust_cnts.values()))
        clust_pcents = vals/np.sum(vals)
        clusts_dict = dict(zip(clust_cnts.keys(), clust_pcents))
        for rnk, pcent in clusts_dict.items():
            expert_ranks_df.append({
                'alias':alias,
                'cluster size': rnk,
                'relative percentage of annotated synapses': pcent
            })
    
    expert_ranks_df = pd.DataFrame(expert_ranks_df)
    sns.barplot(data=expert_ranks_df, x='cluster size', y='relative percentage of annotated synapses', hue='alias')
    plt.show()
    
    return experts_consensus_rankings


def visualize_nRaters(consensus_df):
    """ plot number of synapses found by n raters, split by human/model 
            req's df with 'Consensus_Count' and 'model_found' cols
    """
    cbins = [str(el) for el in range(1, consensus_df['Consensus_Count'].max()+1)][::-1]
    bins = cbins + ['human-only', 'model-only']
    bins_humans = dict(zip(bins,[0]*len(bins)))
    bins_humans.update({'annotator':'human'})
    bins_model = deepcopy(bins_humans)
    bins_model.update({'annotator':'model'})

    for rowi, row in consensus_df.iterrows():
        cc = row['Consensus_Count']
        mf = row['model_found']
        if cc == 0 and mf==1:
            bins_model['model-only'] +=1
        elif mf == 0:
            bins_humans[str(cc)] += 1
            bins_humans['human-only'] += 1

        elif mf == 1:
            bins_model[str(cc)] += 1
            bins_humans[str(cc)] += 1

        else: 
            raise ValueError
    bindfs_df = pd.DataFrame([bins_humans, bins_model])
    bindfs_melt = bindfs_df.melt(id_vars=['annotator'], value_vars=bins, var_name='N raters', value_name='synapse count')

    sns.barplot(data=bindfs_melt, x='N raters', y='synapse count', hue='annotator', order=bins)
    return bindfs_melt


#################################################################
# cluster based analysis functions
#################################################################

def extract_coms_from_labels(
    labels: np.ndarray,
    voxel_size_um=(1.0, 1.0, 1.0),
    model_is_last: bool = True,
) -> pd.DataFrame:
    """
    Compute center-of-mass for each labeled object in each rater.

    Parameters
    ----------
    labels : np.ndarray
        Shape (n_raters, Y, X) or (n_raters, Z, Y, X).
    voxel_size_um : tuple
        (dz, dy, dx) voxel size in µm. For 2D, only (dy, dx) is used.
    model_is_last : bool
        If True, treats the last rater as the model.

    Returns
    -------
    df : pd.DataFrame
        One row per object with columns:
        ['rater', 'label', 'z_um', 'y_um', 'x_um', 'is_model'].
        For 2D, z_um is 0.
    """
    arr = np.asarray(labels)
    n_raters = arr.shape[0]
    spatial_shape = arr.shape[1:]
    ndim = len(spatial_shape)
    assert ndim in (2, 3), "labels must be (N,Y,X) or (N,Z,Y,X)"

    if ndim == 2:
        dy, dx = voxel_size_um[-2:]
        dz = 1.0
    else:
        dz, dy, dx = voxel_size_um

    rows = []
    for r in range(n_raters):
        lab = arr[r]
        for prop in regionprops(lab):
            com = prop.centroid  # (y,x) or (z,y,x)
            if ndim == 2:
                y, x = com
                z = 1.0
            else:
                z, y, x = com

            rows.append(
                dict(
                    rater=r,
                    label=int(prop.label),
                    z_um=z * dz,
                    y_um=y * dy,
                    x_um=x * dx,
                )
            )

    df = pd.DataFrame(rows)
    if model_is_last:
        df["is_model"] = df["rater"] == (n_raters - 1)
    else:
        df["is_model"] = False
    return df


from sklearn.cluster import DBSCAN, KMeans

def dbscan_initial(df_pts, xy_radius_um=0.85, z_radius_um=2.5,
                   eps=1.0, min_samples=1):
    """DBSCAN on anisotropically scaled coordinates."""
    coords = df_pts[["z_um", "y_um", "x_um"]].to_numpy()
    scaled = np.empty_like(coords, dtype=float)
    scaled[:, 0] = coords[:, 0] #/ z_radius_um
    scaled[:, 1] = coords[:, 1] #/ xy_radius_um
    scaled[:, 2] = coords[:, 2] #/ xy_radius_um

    db = DBSCAN(eps=eps, min_samples=min_samples)
    cluster_labels = db.fit_predict(scaled)  # -1 is noise

    df = df_pts.copy()
    df["cluster"] = cluster_labels
    return df


def prune_far_points(df, xy_radius_um=0.85, z_radius_um=2.5,
                     cluster_col="cluster"):
    """(i) Remove points too far from their cluster center."""
    df = df.copy()
    keep = np.zeros(len(df), dtype=bool)

    for cid, grp in df.groupby(cluster_col):
        if cid == -1:
            continue  # drop DBSCAN noise
        center = grp[["z_um", "y_um", "x_um"]].mean().to_numpy()
        diffs = grp[["z_um", "y_um", "x_um"]].to_numpy() - center
        dz = np.abs(diffs[:, 0])
        dy = np.abs(diffs[:, 1])
        dx = np.abs(diffs[:, 2])
        mask = (dz <= z_radius_um) & (dy <= xy_radius_um) & (dx <= xy_radius_um)
        keep[grp.index.values[mask]] = True

    return df[keep].copy()


def split_big_clusters(df, max_points_per_cluster=7, cluster_col="cluster"):
    """(ii) Split clusters with > max_points_per_cluster using KMeans."""
    df = df[df[cluster_col] != -1].copy()  # drop noise
    # re-label clusters sequentially
    uniq = sorted(df[cluster_col].unique())
    df[cluster_col] = df[cluster_col].map({c: i for i, c in enumerate(uniq)})
    next_id = df[cluster_col].max() + 1

    changed = True
    while changed:
        changed = False
        for cid in sorted(df[cluster_col].unique()):
            idx = df.index[df[cluster_col] == cid]
            if len(idx) <= max_points_per_cluster:
                continue

            coords = df.loc[idx, ["z_um", "y_um", "x_um"]].to_numpy()
            km = KMeans(n_clusters=2, n_init=10, random_state=0)
            labels = km.fit_predict(coords)

            new_cid = next_id
            next_id += 1
            df.loc[idx[labels == 0], cluster_col] = cid
            df.loc[idx[labels == 1], cluster_col] = new_cid
            changed = True
            break  # restart the while-loop, cluster set changed

    return df


def merge_close_clusters(df, xy_radius_um=0.85, z_radius_um=2.5,
                         max_points_per_cluster=7, cluster_col="cluster"):
    """(iii) Merge clusters if their centers are within thresholds and
    the merged cluster would not exceed max_points_per_cluster."""
    df = df.copy()

    while True:
        grp_mean = df.groupby(cluster_col)[["z_um", "y_um", "x_um"]].mean()
        grp_size = df.groupby(cluster_col).size()
        clusters = list(grp_mean.index)

        merged_any = False
        for i, ci in enumerate(clusters):
            for cj in clusters[i+1:]:
                new_size = grp_size[ci] + grp_size[cj]
                if new_size > max_points_per_cluster:
                    continue

                c1 = grp_mean.loc[ci].to_numpy()
                c2 = grp_mean.loc[cj].to_numpy()
                dz, dy, dx = np.abs(c1 - c2)

                if dz <= z_radius_um and dy <= xy_radius_um and dx <= xy_radius_um:
                    # merge cj into ci (use smaller id to keep things tidy)
                    tgt, src = sorted((ci, cj))
                    df.loc[df[cluster_col] == src, cluster_col] = tgt
                    merged_any = True
                    break
            if merged_any:
                break

        if not merged_any:
            break

        # normalize labels to compact integer range
        uniq = sorted(df[cluster_col].unique())
        df[cluster_col] = df[cluster_col].map({c: i for i, c in enumerate(uniq)})

    return df


def build_consensus_clusters(
    df_pts,
    xy_radius_um=0.85,
    z_radius_um=2.5,
    max_points_per_cluster=7,
    dbscan_eps=1.0,
    dbscan_min_samples=1,
):
    """Full pipeline: DBSCAN + rules (i)-(iii)."""
    df = dbscan_initial(df_pts,
                        xy_radius_um=xy_radius_um,
                        z_radius_um=z_radius_um,
                        eps=dbscan_eps,
                        min_samples=dbscan_min_samples)
    df = prune_far_points(df, xy_radius_um, z_radius_um)
    df = split_big_clusters(df, max_points_per_cluster)
    df = merge_close_clusters(df, xy_radius_um, z_radius_um,
                              max_points_per_cluster)
    return df


def summarize_clusters_vs_model(df_clustered, n_humans: int):
    """
    Build cluster-level summary to reproduce DeepD3-style barplots.

    Parameters
    ----------
    df_clustered : pd.DataFrame
        Output of build_consensus_clusters; must contain columns
        ['cluster', 'rater', 'is_model'].
    n_humans : int
        Number of human raters (model is assumed to be the rest).

    Returns
    -------
    cluster_summary : pd.DataFrame
        One row per cluster with columns:
        ['n_annotations', 'human_raters', 'n_humans', 'has_model'].
    bar_summary : pd.DataFrame
        Aggregate suitable for plotting:
        columns ['n_humans', 'identified_by_model', 'not_identified',
                 'total_clusters', 'model_unique'].
    """
    model_idx = df_clustered["rater"].max()

    grp = df_clustered.groupby("cluster")
    cluster_summary = pd.DataFrame({
        "n_annotations": grp["rater"].size(),
        "raters_set": grp["rater"].apply(set),
        "z_um": grp["z_um"].mean(),
        "y_um": grp["y_um"].mean(),
        "x_um": grp["x_um"].mean(),
    })
    cluster_summary["human_raters"] = cluster_summary["raters_set"].apply(
        lambda s: {r for r in s if r < n_humans}
    )
    cluster_summary["n_humans"] = cluster_summary["human_raters"].apply(len)
    cluster_summary["has_model"] = cluster_summary["raters_set"].apply(
        lambda s: model_idx in s
    )

    # aggregate for N = 1..n_humans
    rows = []
    for n in range(1, n_humans + 1):
        sub = cluster_summary[cluster_summary["n_humans"] == n]
        total = len(sub)
        with_model = int(sub["has_model"].sum())
        without_model = total - with_model
        rows.append(dict(
            n_humans=n,
            total_clusters=total,
            identified_by_model=with_model,
            not_identified=without_model,
        ))

    # clusters only annotated by the model
    model_unique = cluster_summary[
        (cluster_summary["n_humans"] == 0) & (cluster_summary["has_model"])
    ]
    model_unique_count = len(model_unique)

    bar_summary = pd.DataFrame(rows)
    bar_summary["model_unique"] = model_unique_count
    return cluster_summary, bar_summary



def plot_deepd3_style_bar(bar_summary, aspercent=False, orientation='h', figsize=(3, 5)):
    """
    Make a horizontal bar plot similar to Fig. 3D from the DeepD3 paper.

    Expects bar_summary with columns:
    ['n_humans', 'identified_by_model', 'not_identified', 'model_unique'].
    """
    # add n-humans == 0 as model only
    model_unique = int(bar_summary["model_unique"].iloc[0])
    df = pd.concat([
        pd.DataFrame([{
            "n_humans": 0,
            "identified_by_model": model_unique,
            "not_identified": 0,
            "total_clusters": model_unique,
            "model_unique": model_unique,
        }]),
        bar_summary
    ], ignore_index=True)

    df = df.sort_values("n_humans", ascending=True)
    y = df["n_humans"].to_numpy()

    fig, ax = plt.subplots(figsize=figsize)
    
    xlabel = "% of all clusters"
    ylabel = "Cluster of N annotators"
    
    total = df["total_clusters"].sum()
    ax.set_title(f"total clusters: {total}")

    if aspercent:
        df["identified_by_model"] = df["identified_by_model"] / total * 100.0
        df["not_identified"] = df["not_identified"] / total * 100.0
        model_unique = model_unique / total * 100.0
    else:
        xlabel = "PSD count"

    width_ident = df["identified_by_model"].to_numpy()
    width_not = df["not_identified"].to_numpy()

    
    # pink: not identified, green: identified
    cnot = sns.color_palette("PiYG", as_cmap=False, n_colors=6)[1]
    cyes = sns.color_palette("PiYG", as_cmap=False, n_colors=6)[-1]

    barplotf = ax.barh if orientation == 'h' else ax.bar
    bpkwargs = dict(left=width_not) if orientation == 'h' else dict(bottom=width_not)
    barplotf(y, width_not, color=cnot, label="Not identified by model")
    barplotf(y, width_ident, color=cyes, label="Identified by model", **bpkwargs)


    if orientation == 'v':
        t_inds = range(bar_summary['n_humans'].max()+1)
        ax.set_xticks(t_inds, [str(t) for t in t_inds])

    ax.set_xlabel(xlabel if orientation == 'h' else ylabel)
    ax.set_ylabel(ylabel if orientation == 'h' else xlabel)
    # ax.invert_yaxis()  # so N=7 is on top

    # extra bar for "model unique"
    if model_unique > 0:
        barplotf(max(y) if orientation == 'h' else 0, model_unique, color=cyes)  # position 0 below N=1
        # textloc = [model_unique+0.5, 0] if orientation == 'h' else [0, model_unique+0.5]
        # ax.text(*textloc, "Model unique", va="center", ha="left")
    
    # ax.legend(loc="lower right" if orientation == 'h' else "upper left")
    if ax.get_legend() is not None:
        ax.get_legend().remove()
    
    # plt.tight_layout()
    sns.despine(ax=ax)
    return fig, ax


def make_cluster_summary(df_clustered: pd.DataFrame, n_humans: int) -> pd.DataFrame:
    """
    Make a per-cluster summary: how many human raters, whether model is present, etc.

    Parameters
    ----------
    df_clustered : pd.DataFrame
        Output of build_consensus_clusters; must contain columns:
        ['cluster', 'rater', 'z_um', 'y_um', 'x_um'].
    n_humans : int
        Number of human raters (model is assumed to be the rest).

    Returns
    -------
    cluster_summary : pd.DataFrame
        Index: cluster id.
        Columns:
            'n_points'      : total annotations in cluster
            'human_raters'  : python set of human rater indices in this cluster
            'n_humans'      : number of unique human raters
            'has_model'     : True if model rater is present
            'z_um', 'y_um', 'x_um' : cluster center in µm
    """
    model_idx = df_clustered["rater"].max()

    grp = df_clustered.groupby("cluster")

    cluster_summary = pd.DataFrame({
        "n_points": grp["rater"].size(),
        "raters_set": grp["rater"].apply(set),
        "z_um": grp["z_um"].mean(),
        "y_um": grp["y_um"].mean(),
        "x_um": grp["x_um"].mean(),
    })

    cluster_summary["human_raters"] = cluster_summary["raters_set"].apply(
        lambda s: {r for r in s if r < n_humans}
    )
    cluster_summary["n_humans"] = cluster_summary["human_raters"].apply(len)
    cluster_summary["has_model"] = cluster_summary["raters_set"].apply(
        lambda s: model_idx in s
    )

    return cluster_summary

import matplotlib.pyplot as plt
from matplotlib.cm import get_cmap

def debug_plot_clusters(
    df_clustered: pd.DataFrame,
    n_humans: int,
    view: str = "xy",
    max_clusters: int | None = None,
    figsize=(10, 4),
):
    """
    Visualize cluster organization in space and the number of annotators per cluster.

    Parameters
    ----------
    df_clustered : pd.DataFrame
        Output of build_consensus_clusters; must contain columns:
        ['cluster', 'rater', 'z_um', 'y_um', 'x_um'].
    n_humans : int
        Number of human raters (model is assumed to be the last rater index).
    view : {'xy', 'xz', 'yz'}, optional
        2D projection to use for the spatial scatter.
    max_clusters : int or None
        If set, only the first N clusters (sorted by id) are shown to avoid
        overplotting. Useful when there are many spines in one field of view.
    figsize : tuple
        Matplotlib figure size.

    Returns
    -------
    fig, (ax_scatter, ax_bar) : matplotlib Figure and Axes.
    """
    cluster_summary = make_cluster_summary(df_clustered, n_humans=n_humans)

    # Optionally restrict to a subset of clusters
    clusters = sorted(cluster_summary.index.tolist())
    if max_clusters is not None:
        clusters = clusters[:max_clusters]
        df = df_clustered[df_clustered["cluster"].isin(clusters)].copy()
        cs = cluster_summary.loc[clusters]
    else:
        df = df_clustered.copy()
        cs = cluster_summary

    # Choose projection
    if view == "xy":
        xcol, ycol = "x_um", "y_um"
        xlabel, ylabel = "x (µm)", "y (µm)"
    elif view == "xz":
        xcol, ycol = "x_um", "z_um"
        xlabel, ylabel = "x (µm)", "z (µm)"
    elif view == "yz":
        xcol, ycol = "y_um", "z_um"
        xlabel, ylabel = "y (µm)", "z (µm)"
    else:
        raise ValueError("view must be one of {'xy', 'xz', 'yz'}")

    # Basic info
    n_raters = df["rater"].max() + 1
    model_idx = n_raters - 1

    cmap = get_cmap("tab20")
    markers = ["o", "s", "D", "^", "v", "P", "X", "*", "H", "<", ">"]

    fig, (ax_scatter, ax_bar) = plt.subplots(1, 2, figsize=figsize)

    # ---- Left: spatial scatter ----
    # Plot per rater so markers encode annotator and colors encode cluster.
    for r in sorted(df["rater"].unique()):
        sub = df[df["rater"] == r]
        colors = [cmap(c % 20) for c in sub["cluster"]]
        marker = markers[r % len(markers)]
        label = f"Rater {r}" if r < n_humans else "Model"

        ax_scatter.scatter(
            sub[xcol],
            sub[ycol],
            c=colors,
            marker=marker,
            s=40,
            alpha=0.8,
            edgecolors="k",
            linewidths=0.4,
            label=label,
        )

    # Overlay cluster centers with text showing cluster id and #humans
    for cid, row in cs.iterrows():
        cx, cy = row[xcol], row[ycol]
        text = f"{cid}\n(n={row['n_humans']}{'+M' if row['has_model'] else ''})"
        ax_scatter.scatter(
            cx,
            cy,
            marker="x",
            s=80,
            c="k",
            linewidths=1.2,
        )
        ax_scatter.text(
            cx,
            cy,
            text,
            fontsize=7,
            ha="center",
            va="bottom",
            color="k",
        )

    ax_scatter.set_xlabel(xlabel)
    ax_scatter.set_ylabel(ylabel)
    ax_scatter.set_title("Annotation centers by cluster\n(color=cluster, marker=rater)")
    ax_scatter.legend(fontsize=7, loc="best")

    # ---- Right: per-cluster bar plot ----
    # Each bar: # human raters; green overlay if the model also annotated.
    cid_order = sorted(cs.index)
    y_pos = np.arange(len(cid_order))
    human_counts = cs.loc[cid_order, "n_humans"].to_numpy()
    model_present = cs.loc[cid_order, "has_model"].to_numpy().astype(int)

    ax_bar.barh(y_pos, human_counts, color="0.7", label="# human raters")
    # Overlay a small green bar for model presence (0 or 1).
    ax_bar.barh(y_pos, model_present, left=human_counts, color="g", label="Model")

    ax_bar.set_yticks(y_pos)
    ax_bar.set_yticklabels(cid_order)
    ax_bar.set_xlabel("# annotators in cluster")
    ax_bar.set_ylabel("Cluster ID")
    ax_bar.set_title("Annotator count per cluster")
    ax_bar.legend(fontsize=7, loc="lower right")

    fig.tight_layout()
    return fig, (ax_scatter, ax_bar)

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.cm import get_cmap
import matplotlib.ticker as ticker

def overlay_clusters_on_raw_slice(
    raw_img: np.ndarray,
    df_clustered,
    voxel_size_um=(1.0, 1.0, 1.0),
    n_humans: int | None = None,
    z_index: int | None = None,
    z_thickness_um: float | None = None,
    cmap_img="gray",
    alpha_img: float = 0.9,
    figsize=(6, 6),
    show_cluster_labels: bool = True,
):
    """
    Overlay clustered COM points on top of a raw image slice.

    Parameters
    ----------
    raw_img : np.ndarray
        Either 2D array (Y, X) or 3D array (Z, Y, X).
    df_clustered : pd.DataFrame
        Output of `build_consensus_clusters`, must contain:
        ['cluster', 'rater', 'z_um', 'y_um', 'x_um'].
    voxel_size_um : tuple
        (dz, dy, dx) in µm. For 2D images, only (dy, dx) are used.
    n_humans : int or None
        Number of human raters. If None, assumes last rater is model and
        sets n_humans = max_rater_index.
    z_index : int or None
        For 3D data: index of the z-slice (0-based) to display.
        If None and raw_img is 3D, uses the middle slice.
        Ignored for 2D images.
    z_thickness_um : float or None
        When 3D, points whose z is within +/- (z_thickness_um / 2) of the
        selected slice will be shown. If None, defaults to dz (one slice).
    cmap_img : str
        Matplotlib colormap for the background image.
    alpha_img : float
        Alpha for the background image (0–1).
    figsize : tuple
        Figure size.
    show_cluster_labels : bool
        If True, draw cluster centers + text labels.

    Returns
    -------
    fig, ax : matplotlib Figure and Axes
    """
    raw = np.asarray(raw_img)
    ndim = raw.ndim
    assert ndim in (2, 3), "raw_img must be 2D or 3D (Z,Y,X)"

    if ndim == 2:
        # 2D: ignore z completely; all points are projected into the plane.
        img_slice = raw
        dz, dy, dx = 1.0, *voxel_size_um[-2:]
        z_index = 0
        z_thickness_um = np.inf  # show all points
    else:
        # 3D: choose slice
        dz, dy, dx = voxel_size_um
        if z_index is None:
            z_index = raw.shape[0] // 2
        if z_thickness_um is None:
            z_thickness_um = dz  # roughly one slice thick
        img_slice = raw[z_index]

    # Figure and base image
    fig, ax = plt.subplots(figsize=figsize)
    vmin, vmax = np.percentile(img_slice, [1, 99])
    ax.imshow(img_slice, cmap=cmap_img, vmin=vmin, vmax=vmax, alpha=alpha_img)
    ax.set_title(f"Z slice {z_index} with cluster COMs")
    ax.set_xlabel("X (pixels)")
    ax.set_ylabel("Y (pixels)")

    # Determine rater info
    max_rater = int(df_clustered["rater"].max())
    if n_humans is None:
        n_humans = max_rater  # last index = model
    model_idx = max_rater

    # Convert COM coordinates (µm) -> voxel indices
    df = df_clustered.copy()
    df["z_vox"] = df["z_um"] / dz
    df["y_vox"] = df["y_um"] / dy
    df["x_vox"] = df["x_um"] / dx

    # Filter to points near the chosen z slice (3D case)
    if ndim == 3:
        # physical z coordinate of chosen slice
        z_slice_um = z_index * dz
        half_thick = z_thickness_um / 2.0
        df = df[np.abs(df["z_um"] - z_slice_um) <= half_thick].copy()

    if df.empty:
        ax.text(
            0.5,
            0.5,
            "No cluster points on this slice\n(adjust z_index / z_thickness_um)",
            transform=ax.transAxes,
            ha="center",
            va="center",
            color="r",
            fontsize=10,
        )
        fig.tight_layout()
        return fig, ax

    # Colormap for clusters, markers for raters
    cmap = get_cmap("tab20")
    markers = ["o", "s", "D", "^", "v", "P", "X", "*", "H", "<", ">"]

    # Draw points per rater so marker encodes annotator
    for r in sorted(df["rater"].unique()):
        sub = df[df["rater"] == r]
        colors = [cmap(int(c) % 20) for c in sub["cluster"]]
        marker = markers[int(r) % len(markers)]
        label = f"Rater {r}" if r < n_humans else "Model"

        ax.scatter(
            sub["x_vox"],
            sub["y_vox"],
            c=colors,
            marker=marker,
            s=40,
            alpha=0.9,
            edgecolors="k",
            linewidths=0.4,
            label=label,
        )

    # Optionally overlay cluster centers + text
    if show_cluster_labels:
        # cluster-level summary just for this slice
        grp = df.groupby("cluster")
        centers = grp[["z_vox", "y_vox", "x_vox"]].mean()
        human_counts = grp["rater"].apply(lambda s: len({i for i in s if i < n_humans}))
        has_model = grp["rater"].apply(lambda s: model_idx in set(s))

        for cid in centers.index:
            cx = centers.loc[cid, "x_vox"]
            cy = centers.loc[cid, "y_vox"]
            n_h = int(human_counts.loc[cid])
            m_flag = "+M" if bool(has_model.loc[cid]) else ""
            text = f"{cid}\n(n={n_h}{m_flag})"
            ax.scatter(cx, cy, marker="x", s=80, c="y", linewidths=1.5)
            ax.text(
                cx,
                cy,
                text,
                fontsize=7,
                ha="center",
                va="bottom",
                color="y",
                bbox=dict(boxstyle="round,pad=0.15", fc="k", ec="none", alpha=0.4),
            )

    ax.legend(fontsize=7, loc="lower right")
    ax.set_xlim(0, img_slice.shape[1])
    ax.set_ylim(img_slice.shape[0], 0)  # flip y to image coordinates
    fig.tight_layout()
    return fig, ax



plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.serif': ['Arial'],
    'axes.titlesize': 8,
    'axes.labelsize': 8,
    'xtick.labelsize': 8,
    'ytick.labelsize': 8,
    'legend.fontsize': 8,
    'figure.titlesize': 8,
})


# assign aliases to annotators
MODEL_ALIAS = 'StarDist (custom)'
assign_aliases = {
    'Annotator-1': 'A',
    'Annotator-2': 'B',
    'Annotator-3': 'C',
    'Annotator-4': 'D',
    'Annotator-5': 'E',
    MODEL_ALIAS: 'predStardist'
}
assign_aliases = {v:k for k,v in assign_aliases.items()}

# list names of human annotators
EXPERTS = list(assign_aliases.keys())[:-1]


if __name__ == "__main__":
    BASE_DIR = r"J:\SEGMENTATION_DATASETS\benchmarks"
    FIGOUTDIR = os.path.join(BASE_DIR, "ANALYSIS", "2026_0309")
    base_dir = os.path.join(BASE_DIR, "datasets")
    
    all_ex_dirs = ["Dataset1", "Dataset2", "Dataset3"]
    dirNameMap = dict(zip(all_ex_dirs, ['easy2D', 'hard2D', '3D']))
    DATASET_ID_MAP = {'easy2D': '1', 'hard2D': '2', '3D': '3'}
    PREDIDSTRING = 'predStardist' # treat annotations with this string as predictions
    FOLDER_ORDER = [v for v in dirNameMap.values()]
    
    WRITE_OUPUTS = bool(0)
    
    if WRITE_OUPUTS: 
        ug.verify_outputdir(FIGOUTDIR)
    
    # plot images with annotations overlayed for each annotator
    if bool(0):
        for example_folder_name in all_ex_dirs:
            example_folder_path = os.path.join(base_dir, example_folder_name)
            img, annotations = display_image_and_annotation_overlays(
                example_folder_path,
                write_outputs = WRITE_OUPUTS,
            )
    
    if bool(0): # plot raw images with scalebars
        for example_folder_name in all_ex_dirs:
            example_folder_path = os.path.join(base_dir, example_folder_name)   
            image_file = os.path.join(example_folder_path, 'image.tiff')
            img = uip.read_img(image_file)
            fig,ax = plt.subplots(figsize=(5,5))
            up.show(img, ax=ax, hide_axis=True, interpolation='bilinear', cmap='gray')
            up.add_scalebar(ax, pixel_to_unit=0.085, length_units=2)
            if WRITE_OUPUTS: up.save_fig(os.path.join(FIGOUTDIR, f"{example_folder_name}_raw_image.svg"))
            plt.show()
        
        


    # load and prep data for analysis 
    ##########################################
    data, deid_map = load_annotation_data(
        base_dir, examples=all_ex_dirs, 
        deidentify_annotators=bool(1), assign_aliases=assign_aliases
    )


    if bool(0): # display image and all annotations
        _farr = lambda a: None if not isinstance(a, np.ndarray) else uip.mip(a) if a.ndim==3 else a
        for ds, imgdata in data.items():
            disp_imgs = [imgdata['image']] * (1+len(imgdata['annotations']))
            lbl_imgs = [None]
            titles = ['raw_data']
            for k, lbls in imgdata['annotations'].items():
                lbl_imgs.append(lbls)
                titles.append(k)
            
            disp_imgs = [_farr(a) for a in disp_imgs]
            lbl_imgs = [_farr(a) for a in lbl_imgs]
            
            
            up.plot_image_grid(
                disp_imgs, lbl_imgs, n_cols=4, titles=titles,
                outpath=os.path.join(FIGOUTDIR, f"all_annotations_Dataset{DATASET_ID_MAP[ds]}.svg") if WRITE_OUPUTS else None

            )

       
    # global vars for figure formatting
    #########################################
    _bp_color = 'gray'
    BOXPROPS = {
        'showfliers':False, 
        'width':0.8, 
        'gap':0.2, 
        'linewidth':2, 
        'zorder':0,
        'fill':False,
        'boxprops':{'color':_bp_color, 'linewidth':2},
        'medianprops':{'color':_bp_color, 'linewidth':2},
        'whiskerprops':{'color':_bp_color, 'linewidth':2},
        'capprops':{'color':_bp_color, 'linewidth':2}
    }
    JITTERSCATTERPROPS = {
        'linewidth':0.5, 
        'edgecolor':'k', 
        's':50, 
        'alpha':1,
        'zorder':999,
    }

    annotator_source_palette = {
        'Annotator-1': '#1f78b4',
        'Annotator-2': '#a6cee3',
        'Annotator-3': '#EBEBEB',
        'Annotator-4': '#fdbf6f',
        'Annotator-5': '#ff7f00',
        MODEL_ALIAS:    'k',
    }
    ANNOTATOR_PALETTE = annotator_source_palette

    MARKER_PALETTE = {
        'Annotator-1': 'o',
        'Annotator-2': 'o',
        'Annotator-3': 'o',
        'Annotator-4': 'o',
        'Annotator-5': 'o',
        MODEL_ALIAS:    'D'
    }

    # plot legend alone
    ########################################################################
    # 1. Create a figure and axis
    fig, ax = plt.subplots(figsize=(1.4, 1.8))

    # 2. Create "dummy" plots for each entry
    # We use empty lists for data so nothing actually appears on the plot
    legend_elements = []
    for label, color in annotator_source_palette.items():
        if MODEL_ALIAS in label:
            continue
        marker = MARKER_PALETTE.get(label, 'o')
        line = ax.scatter([], [], c=color, marker=marker, label=label, edgecolors='k', linewidth=0.5)
    
    line = ax.scatter([], [], c='k', marker='D', label='2D StarDist (custom)', edgecolors='k', linewidth=0.5)
    line = ax.scatter([], [], c='w', marker='D', label='3D StarDist (custom)', edgecolors='k', linewidth=0.5)

    # 3. Add the legend to the center
    legend = ax.legend(loc='center', frameon=True, title="Expert\nModel")

    # 4. Hide the axes entirely
    ax.axis('off')

    # 5. Adjust the layout to fit the legend exactly
    plt.tight_layout()
    if WRITE_OUPUTS: plt.savefig(os.path.join(FIGOUTDIR, "annotator_legend.svg"), dpi=300, bbox_inches='tight')
    plt.show()



    # Analysis Module 1: Pairwise Dice coefficient.
    ########################################################################
    dice_df, dice_matricies = compute_pairwise_dice(data)
    dice_df = dice_df.assign(dataset = dice_df['Folder'].map(DATASET_ID_MAP))
           
    visualize_dice_corr(dice_matricies, figsize=(1.6*3, 1.8))
    visualize_dice_annotator_avg(dice_matricies, figsize=(1.4, 1.8))

    if WRITE_OUPUTS:
        dice_df.to_excel(os.path.join(FIGOUTDIR, "dice_scores.xlsx"), index=False)
    
    # Analysis Module 2: Annotation counts and props
    ########################################################################
    counts_df, rpdfs = compute_annotation_counts(data)
        
    # plot counts
    visualize_annotation_counts(counts_df, figsize=(1.4, 1.8))

    # plot avg properties for each annotators
    visualize_annotation_props(rpdfs, mean_val=True, figsize=(1.4*2, 1.8))
    
    # clean up columns and merge
    counts_df = (
            counts_df.assign(dataset = counts_df['Folder'].map(DATASET_ID_MAP))
            .drop(columns = ['Folder'])
            .rename(columns={'Annotator':'annotator', 'Count':'count'})
    )

    props_df = counts_df.merge(
        # agg props 
        (rpdfs
        .assign(dataset = rpdfs['folder'].map(DATASET_ID_MAP))
        .drop(columns = ['folder', 'colocal_id', 'label', 'intensity_min', 'intensity_max'])
        .groupby(['dataset', 'annotator'])
        .mean(numeric_only=True)
        .reset_index()
        .rename(columns={'area':'size'})
        ), 
        on=['dataset', 'annotator']
    )[['dataset', 'annotator', 'count', 'size', 'intensity_mean']]
    
    
    if WRITE_OUPUTS:
        props_df.to_excel(os.path.join(FIGOUTDIR, "compare_object_features.xlsx"), index=False)
        
        

    # Analysis Module 3: Spine pixel sum consensus (votes)
    ########################################################################
    consensus_df, consensus_summary = compute_spine_consensus(data)
    
    votes = compute_pixelwise_votes(data, include_model=False)
    up.plot_image_grid(
        [_farr(a) for a in votes],
        outpath=os.path.join(FIGOUTDIR, "pixelwise_expert_agreement.svg") if WRITE_OUPUTS else None
    )


    # Analysis Module 4: clustering based analysis
    ################################################################################################################################################
    
    dsnames = ['easy2D', 'hard2D','3D']              # 3D shape (n_raters, Z, Y, X)
    consensus_clusters_df = []
    for dsname in dsnames:
        
        # build clusters for this dataset
        ###########################################################################
        img = data[dsname]['image']
        labels = np.stack(list(data[dsname]['annotations'].values()), 0)
        
        voxel_size_um = (1,1,1)

        df_pts = extract_coms_from_labels(labels, voxel_size_um=voxel_size_um)
        
        df_clustered = build_consensus_clusters(df_pts,
                                                xy_radius_um=3,  # since voxel size is 1 this is really pixels not um
                                                z_radius_um=3,
                                                max_points_per_cluster=labels.shape[0],
                                                dbscan_eps=2.5,
        )
        
        cluster_summary, bar_summary = summarize_clusters_vs_model(
            df_clustered, n_humans=labels.shape[0]-1
        )

        print(f"ulbls per annotator: {[len(uip.unique_nonzero(lbls)) for lbls in labels]}")
        print(f"n clusters: {df_clustered['cluster'].nunique()} | n points: {len(df_clustered)}")


        # visualize annotation clusters overlayed on image. colored by num experts.
        ###########################################################################
        fig,ax =plt.subplots(figsize=np.array([8,6])*2)

        up.show(img, cmap='gray', ax=ax) # show img

        palette_n_annot = sns.color_palette("PiYG", as_cmap=False, n_colors=labels.shape[0])
        palette_n_annot = dict(zip(range(0, labels.shape[0]), palette_n_annot))
        palette_n_annot[0] = (1,0,0)

        cluster_summary = cluster_summary.assign(
            model_unique=lambda d: ([int(el) for el in d['has_model'] & (d['n_humans'] == 0)]),
            # annotation_cluster=lambda d: d['annotation_cluster'] ,
            model_missed_consensus=lambda d: ([int(el) for el in (~d['has_model']) & (d['n_humans'] > 2)]),
            dsname=dsname,
        )
        g = sns.scatterplot(
            data=cluster_summary,
            x='x_um', y='y_um', 
            hue='n_humans',
            alpha=1.0,
            ax=ax,
            palette=palette_n_annot,
            legend=True,
            s=2*32000/img.shape[-1],
        )
        
        path_collection = ax.collections[0]
        face_colors = path_collection.get_facecolors()
        path_collection.set_edgecolors(face_colors)
        path_collection.set_facecolors('none')
        lw = 1.5 if dsname == 'easy2D' else 2.5 
        path_collection.set_linewidth(lw)

        # plot model misses as red squares overlaid on top
        model_miss_df = cluster_summary.query("(has_model==False) & (n_humans>2)")
        if len(model_miss_df) > 0:
            g = sns.scatterplot(
                data=model_miss_df,
                x='x_um', y='y_um', 
                hue='model_missed_consensus',
                style='model_missed_consensus',
                markers={1: 's', 0: 'o'},
                # linewidth=4,
                alpha=1.0,
                ax=ax,
                # palette=palette_n_annot,
                palette={1:'r', 0:'g'},
                legend=False,
                s=(2*32000/img.shape[-1])*0.45,
            )

            path_collection = ax.collections[1]
            face_colors = path_collection.get_facecolors()
            path_collection.set_edgecolors(face_colors)
            path_collection.set_facecolors('none')
            lw = 1.5 if dsname == 'easy2D' else 2.5 
            path_collection.set_linewidth(lw)

        plt.axis('off')
        plt.title(f"n clusters: {df_clustered['cluster'].nunique()}")
        if WRITE_OUPUTS: up.save_fig(os.path.join(FIGOUTDIR, f"visualize_raters_clusters_as_points_{dsname}.svg"), dpi=300)
        plt.show()


        # compare model % in consensus clusters
        ########################################
        fig, ax = plot_deepd3_style_bar(bar_summary, aspercent=bool(1), orientation='v', figsize=(1.4,1.8))
        if WRITE_OUPUTS: up.save_fig(os.path.join(FIGOUTDIR, f"deepd3_style_barplot_{dsname}.svg"), dpi=300)
        plt.show()
        
        consensus_clusters_df.append(cluster_summary)

    # concat results from all datasets
    all_consensus_clusters = pd.concat(consensus_clusters_df).reset_index()
    all_consensus_clusters = all_consensus_clusters.assign(dataset = all_consensus_clusters['dsname'].map(DATASET_ID_MAP))
    all_consensus_clusters['human_unique'] = (
        (all_consensus_clusters['n_humans'] == 1) & (all_consensus_clusters['n_annotations'] == 1))
    
    # agg clusters to generate summary - Group by the 'dataset' column and aggregate
    consensus_clust_summ = all_consensus_clusters.groupby('dataset').agg(
        unique_clusters=('cluster', 'nunique'),
        consensus_clusters=('n_humans', lambda x: (x > 2).sum()),
        sum_model_missed_consensus=('model_missed_consensus', 'sum'),
        sum_model_unique=('model_unique', 'sum'),
        sum_human_unique=('human_unique', 'sum'),
    ).reset_index()
    
    if WRITE_OUPUTS:
        all_consensus_clusters.to_excel(os.path.join(FIGOUTDIR, "all_consensus_clusters.xlsx"), index=True)
        consensus_clust_summ.to_excel(os.path.join(FIGOUTDIR, "all_consensus_clusters_summary.xlsx"), index=False)




    # calculate per-annotator performance metrics - using consensus as ground truth
    #########################################################
    from sklearn.metrics import cohen_kappa_score

    RATER_IDS = [0,1,2,3,4,'model']
    n_human_raters = 5  
    consensus_thresh = 2           # (n_humans > thresh) = consensus

    all_performance_metrics = []
    for adf in consensus_clusters_df:
        dsname = adf['dsname'].iloc[0]
        
        # Define the Ground Truth (The Consensus)
        is_consensus = (adf['n_humans'] > consensus_thresh).astype('int').values

        # Calculate metrics for each Rater
        for rater_id in RATER_IDS:

            # which of the rater's labels are part of the consensus?
            if rater_id == 'model':
                y_rater = adf['has_model'].astype('int').values
            else:
                y_rater = adf['human_raters'].apply(lambda x: 1 if rater_id in x else 0).values
            
            tp = (y_rater & is_consensus).sum()
            fp = (y_rater & ~is_consensus).sum()
            fn = (~y_rater & is_consensus).sum()

            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            
            kappa_score = cohen_kappa_score(is_consensus, y_rater)

            # IRR via correlation
            from scipy.stats import spearmanr, pearsonr
            pearson_R, pearson_P = pearsonr(is_consensus, y_rater)

            # IRR via % agreement on all labels for each cluster (e.g. is consensus & is NOT consensus)
            percent_consensus = np.equal(is_consensus, y_rater).sum()/is_consensus.size


            all_performance_metrics.append({
                'dsname': dsname,
                'dataset': DATASET_ID_MAP[dsname],
                'source': MODEL_ALIAS if rater_id=='model' else f'Annotator-{rater_id+1}',
                'is_model': rater_id == 'model',
                'tp': tp, 'fp': fp, 'fn': fn,
                'percent_tp': tp/np.sum(is_consensus),
                'precision': precision, 'recall': recall, 'f1': f1,
                'kappa': kappa_score,
                'pearson_R': pearson_R,
                'percent_consensus': percent_consensus,
            })


    df_performance = pd.DataFrame(all_performance_metrics)
    
    if WRITE_OUPUTS: 
        df_performance.to_excel(os.path.join(FIGOUTDIR, "clustering_performance_metrics.xlsx"), index=False)


    pltdf = (
        df_performance.melt(id_vars=['dsname', 'dataset', 'source', 'is_model'], var_name='Metric', value_name='Score') 
        .query("Metric in ['precision', 'recall', 'f1', 'percent_tp', 'tp', 'fp', 'fn', 'kappa', 'pearson_R', 'percent_consensus']")
    )  
    # print model performance summary
    performance_summary = pd.pivot_table(
        pltdf.groupby(['dataset', 'Metric', 'is_model'])['Score'].mean().reset_index(),
        index=['dataset', 'Metric'],
        columns=['is_model']
    )


    # plot acc, recall, F1 scores 
    ###############################################################
    PLOT_METRICS = ['precision', 'recall', 'f1']
    fig, axes = plt.subplots(1,3,figsize=(1.4*3, 1.8), sharey=True)
    for i, ax in enumerate(axes):
        _pltdf = pltdf.query(f"dsname==@dsnames[{i}]")
        _pltdf = _pltdf[_pltdf['Metric'].isin(PLOT_METRICS)]
        sns.boxplot(
            data=_pltdf.query("is_model==False"), 
            x="Metric", y="Score", ax=ax, 
            legend=False,
            **BOXPROPS
        )
        
        # make model marker white for 3d dataset
        _annotator_source_palette = deepcopy(annotator_source_palette)
        if i==2: 
            _annotator_source_palette[MODEL_ALIAS] = 'w'
            
        up.jittered_scatterplot(
            data=_pltdf, 
            x="Metric", y="Score", ax=ax, 
            hue='source', 
            palette=_annotator_source_palette,
            style='source',
            markers=MARKER_PALETTE,
            legend = False,
            **JITTERSCATTERPROPS
        )
        ax.set_ylim(0, 1.05)
        ax.set_title(f"Dataset {i+1}")
        ax.tick_params(axis='x', rotation=45)
        ax.set_xlabel("")
        ax.axhline(1, color='k', linestyle='--', linewidth=1, zorder=0, alpha=0.5)
    sns.despine()
    if WRITE_OUPUTS: up.save_fig(os.path.join(FIGOUTDIR, f"consensus_boxplot_alldatasets.svg"), dpi=300)
    plt.show()
    
    
    # kappa score boxplot 
    ################################################################
    fig,ax = plt.subplots(figsize=(1.4, 1.8))

    # Plot Humans
    kappa_plot_df = df_performance[df_performance['is_model']==False]

    sns.boxplot(
        data=kappa_plot_df,
        x='dataset', y='kappa', 
        ax=ax, 
        legend=False,
        **BOXPROPS
    )
    up.jittered_scatterplot(
        data=kappa_plot_df,
        x='dataset', y='kappa', ax=ax, 
        hue='source', 
        palette=annotator_source_palette,
        style='source',
        markers=MARKER_PALETTE,
        legend=False,
        **JITTERSCATTERPROPS
    )

    sns.despine()
    plt.axhline(0.6, ls='--', color='gray', alpha=0.5) # "Substantial" threshold
    plt.title("Inter-Rater Reliability (Cohen's Kappa)")
    plt.ylabel("Kappa Score")
    plt.ylim(0, 1.05)
    if WRITE_OUPUTS: up.save_fig(os.path.join(FIGOUTDIR, f"inter_rater_kappa_boxplot.svg"), dpi=300)
    plt.show()





    # measure IRR via kappa scores - compare raters pairwise
    #############################################################################
    kappa_results = []
    n_human_raters = 5
    consensus_thresh = 2

    # Every row in adf is a unique cluster location.
    for adf in consensus_clusters_df:
        dsname = adf['dsname'].iloc[0]
        
        # 1. Define the Ground Truth array (the 'Consensus')
        y_consensus = (adf['n_humans'] > consensus_thresh).astype(int).values

        # 2. Calculate Kappa for each Human Rater
        for rater_id in RATER_IDS: #range(n_human_raters):

            rater_name = rater_id if isinstance(rater_id, str) else f'Annotator-{rater_id+1}'

        def get_rater_clusts(rater_id, adf):
            # Was this specific rater part of this cluster?
            if rater_id == 'model':
                y_rater = adf['has_model'].astype('int').values
            else:
                y_rater = adf['human_raters'].apply(lambda x: 1 if rater_id in x else 0).values
            return y_rater
        
        
        measured = [] # track already performed measures 
        kdf = []
        for rid in RATER_IDS:
            y1 = get_rater_clusts(rid, adf).astype('bool')
            for rid2 in RATER_IDS:
                if rid == rid2: 
                    continue
                if [rid2, rid] in measured:
                    continue
                y2 = get_rater_clusts(rid2, adf).astype('bool')

                agree = np.equal(y1, y2)
                percent_agree = agree.sum()/agree.size
            
                tp = (y1 & y2).sum()
                fn = (~y1 & y2).sum()
                recall = tp / (tp + fn) if (tp + fn) > 0 else 0

                measured.append([rid, rid2])
                kappa_score = cohen_kappa_score(y1, y2)
                kdf.append(dict(
                    rater1=MODEL_ALIAS if rid=='model' else f'Annotator-{rid+1}', 
                    rater2=MODEL_ALIAS if rid2=='model' else f'Annotator-{rid2+1}', 
                    kappa_score=kappa_score, recall=recall,
                    tp=tp, fn=fn,
                    percent_agree=percent_agree,
                    is_model = 'model' in [rid, rid2],
                ))
        kdf = pd.DataFrame(kdf).assign(
            dataset={'easy2D': '1', 'hard2D': '2', '3D': '3'}[dsname])
        
        
        kappa_results.append(kdf)
            
        print((kdf.groupby('is_model')['kappa_score']).mean().reset_index())
        print((kdf.groupby('is_model')['recall']).mean().reset_index())
        
    df_kappa = pd.concat(kappa_results,ignore_index=True)




