"""Rescore fixed archived references on exact frozen examples; never select best test run."""
from pathlib import Path
import hashlib,json,shutil
import numpy as np
import pandas as pd
from sklearn.metrics import balanced_accuracy_score,f1_score
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=R/'results/A09.json';records=[r for r in json.loads(p.read_text()) if not r['model'].startswith('vassi-')]
 for f in sorted((R/'experiments/A09/archived-vassi').glob('vassi-run-*.scores.json')):
  s=json.loads(f.read_text());src=f.with_name(f.name.replace('.scores.json','.predictions.npz'));dest=R/f'results/predictions/A09/archived--{s["model_id"]}.npz';shutil.copyfile(src,dest)
  records.append(dict(benchmark_id='A09',slice_id='expansion-v1',model=s['model_id'],status='measured',score=s['primary_score'],metric='macro_f1',direction='higher',date='2026-10-30',track='reference',reference_type='archived_predictions_rescored',primary_reference=s['primary_reference'],superiority_eligible=False,superiority_reason=s['comparison_tier'],n_units=s['evaluation_examples'],prediction_file=str(dest.relative_to(R)),prediction_sha256=sha(dest),source_url=s['source_url'],input_sha256={'data/cache/A09/data.npz':sha(R/'data/cache/A09/data.npz')},source_score_file=str(f.relative_to(R)),group_results=s['per_recording'],seconds=None))
 p.write_text(json.dumps(records,indent=2))
 # Published MRIQC CSV uses exclude1, exactly the original binary loader convention.
 cache=R/'data/cache/I10';archive=cache/'mclf_run-20170703-190702_mod-rfc_ver-0.9.7.clf-3.3_class-2_cv-loso_data-test_pred.csv';table=pd.read_csv(archive)
 with np.load(cache/'data.npz') as a:
  ids=a['test_unit_ids'];truth=a['test_y'];assert table.subject_id.is_unique
  aligned=pd.DataFrame({'subject_id':ids}).merge(table,on='subject_id',how='left',validate='one_to_one');assert aligned.pred_y.notna().all();pred=aligned.pred_y.to_numpy(int);assert len(pred)==len(truth)==265
 dest=R/'results/predictions/I10/archived--mriqc-rfc-2017.npz';np.savez_compressed(dest,predictions=pred)
 r=dict(benchmark_id='I10',slice_id='expansion-v1',model='mriqc-rfc-2017',status='measured',score=float(balanced_accuracy_score(truth,pred)),macro_f1=float(f1_score(truth,pred,average='macro')),metric='balanced_accuracy',direction='higher',date='2026-10-30',track='reference',reference_type='archived_predictions_rescored',n_units=len(truth),prediction_file=str(dest.relative_to(R)),prediction_sha256=sha(dest),input_sha256={str(archive.relative_to(R)):sha(archive),'data/cache/I10/data.npz':sha(cache/'data.npz')},superiority_eligible=False,superiority_reason='Archived MRIQC classifier: different merged-rater training labels/features, sample size and tuning history; same DS030 examples and rater1 scoring',source_url='https://github.com/nipreps/mriqc/tree/c5767827abba6c1c01f7cc26b5fb1d0cd32a7fe8/mriqc/data/csv',seconds=None)
 p=R/'results/I10.json';rows=[v for v in json.loads(p.read_text()) if v['model']!='mriqc-rfc-2017'];rows.append(r);p.write_text(json.dumps(rows,indent=2))
 (R/'experiments/I10/archived-reference-alignment.json').write_text(json.dumps(dict(date='2026-10-30',source_sha256=sha(archive),join='one-to-one cohort-local subject_id, all265 frozen DS030 examples, sorted prepared-array order',label_mapping='pred_y1exclude vs rater1<0;0include otherwise',missing_predictions=0,score=r['score'],metric=r['metric'],limitations=r['superiority_reason']),indent=2));print('Archived references:20 VASSI runs, primary00; MRIQC',r['score'])
if __name__=='__main__':main()
