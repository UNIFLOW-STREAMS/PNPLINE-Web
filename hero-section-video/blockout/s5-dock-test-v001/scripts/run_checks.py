"""Portable runner; explicit input, logs, and nonzero exit propagation."""
import argparse,subprocess,json,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--blender',required=True);p.add_argument('--source',required=True);p.add_argument('--candidate',required=True);a=p.parse_args();r=Path(__file__).resolve().parents[1];records=[]
def run(label,script,blend=None,args=(),pure=False):
 command=([sys.executable,'-X','utf8',str(script)] if pure else [a.blender,'--background','--factory-startup']+([str(blend)] if blend else [])+['--python-exit-code','1','--python',str(script)]+(['--',*map(str,args)] if args else []))
 with (r/'logs'/f'{label}.log').open('w',encoding='utf8') as out:result=subprocess.run(command,stdout=out,stderr=subprocess.STDOUT)
 records.append(dict(label=label,command=command,exit_code=result.returncode));(r/'review/check-runs.json').write_text(json.dumps(records,indent=2),encoding='utf8');print(label,result.returncode,flush=True)
 if result.returncode:raise SystemExit(result.returncode)
run('kinematics-green',r/'tests/test_kinematics.py',pure=True)
run('isolation-green',r/'tests/test_isolation.py');run('geometry-green',r/'tests/test_geometry.py')
run('saved-motion',r/'scripts/validate_s5_test.py',a.candidate,['--config',r/'config.json','--scene','S5_DOCK_TEST_v01','--output-dir',r/'review'])
run('space',r/'scripts/validate_space.py',a.candidate,['--config',r/'config.json','--output-dir',r/'review'])
run('reproduction',r/'scripts/check_reproduction.py',a.candidate,['--config',r/'config.json','--output-dir',r/'review'])
for label,blend in [('baseline',a.source),('after',a.candidate)]:
 run('signature-'+label,r/'scripts/preservation.py',blend,['--scene','PNPLINE_MASTER_v005','--output',r/f'review/master-{label}-signature.json'])
run('master-regression-after',r/'scripts/master_regression_adapter.py',a.candidate,['--scene','PNPLINE_MASTER_v005','--test',r/'baseline-regression/scripts/test_scene.py'])
run('boundaries',r/'scripts/capture_boundaries.py',a.candidate,['--config',r/'config.json','--output',r/'review/boundary-states.json'])
before=json.loads((r/'review/master-baseline-signature.json').read_text());after=json.loads((r/'review/master-after-signature.json').read_text());equal=before==after
(r/'review/preservation-comparison.json').write_text(json.dumps(dict(equal=equal,objects=len(before['objects']),frames=len(before['frames']),changed_sections=[k for k in before if before[k]!=after[k]]),indent=2));assert equal
print('ALL CHECKS PASS',flush=True)
