"""Fresh final checks with exit-code ledger; seal all submitted evidence hashes."""
import subprocess,json,hashlib,importlib.util,sys
from pathlib import Path
from PIL import Image,ImageChops
R=Path(__file__).resolve().parents[1];B='C:/Program Files/Blender Foundation/Blender 5.1/blender.exe'
commands=[]
def run(name,args,expected=0):
 with (R/'review/logs'/f'final-{name}.log').open('w',encoding='utf8') as f:p=subprocess.run(args,stdout=f,stderr=subprocess.STDOUT)
 commands.append({'name':name,'command':args,'exit_code':p.returncode,'expected_exit':expected,'log':f'review/logs/final-{name}.log'})
 (R/'review/final-commands.json').write_text(json.dumps(commands,indent=2))
 assert p.returncode==expected,(name,p.returncode)
run('guards',[sys.executable,'-X','utf8',str(R/'tests/test_guards.py')])
run('baseline-missing-proxy',[B,'-b','--factory-startup',str(R/'inputs/base.blend'),'--python-exit-code','1','--python',str(R/'tests/test_proxy.py')],1)
run('proxy-and-master',[B,'-b','--factory-startup',str(R/'master-cn-city-proxy-v001.blend'),'--python-exit-code','1','--python',str(R/'tests/test_proxy.py'),'--python',str(R/'scripts/regression.py')])
run('original-behavior',[B,'-b','--factory-startup',str(R/'inputs/base.blend'),'--python-exit-code','1','--python',str(R/'scripts/inspect_scene.py')])
run('reproduction-structure',[B,'-b','--factory-startup','--python-exit-code','1','--python',str(R/'scripts/check_reproduced_structure.py')])
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
master=R/'master-cn-city-proxy-v001.blend';masterhash=sha(master)
assert sha(R/'inputs/base.blend')==sha(R.parent/'s5-integration-v001/master-s5-integration-v001.blend')=='8cf66b7713b85fbe175229ab87456d40b420b866d222b28d8a712d60e4511412'
for file in ['preservation.json','collisions.json','visibility.json']:
 d=json.loads((R/'review'/file).read_text());assert d.get('candidate_sha256',d.get('sha256'))==masterhash
assert json.loads((R/'review/preservation.json').read_text())['pass_all']
coll=json.loads((R/'review/collisions.json').read_text());assert not coll['aabb_overlap_candidates'] and not coll['camera_hits']
for p in [R/'preview/after-frames/render-record.json',R/'review/diagnostic/render-record.json',R/'review/reopened-render/render-record.json']:
 d=json.loads(p.read_text());assert d['sha256']==masterhash
 for frame,digest in d['images'].items():
  file=p.parent/(f'{int(frame):04}.png' if frame.isdigit() else frame+'.png');assert sha(file)==digest,str(file)
baseline={'blend_sha256':sha(R/'inputs/base.blend'),'engine':'BLENDER_WORKBENCH','resolution':[960,540],'fps':12,'range':[84,480],'command_script':'../s5-integration-v001/scripts/render_review.py','images':{p.name:sha(p) for p in sorted((R/'preview/before-frames').glob('*.png'))}}
(R/'review/baseline-render-record.json').write_text(json.dumps(baseline,indent=2))
media=json.loads((R/'review/media.json').read_text());assert all(sha(R/'preview'/n)==d['sha256'] for n,d in media.items())
re=json.loads((R/'review/structural-reproduction.json').read_text());assert re['master_sha256']==masterhash and re['all_object_mesh_material_action_scene_signatures_equal']
out={'master_sha256':masterhash,'source_sha256':sha(R/'inputs/base.blend'),'source_unchanged':True,'evidence_hashes_match_master':True,'tests':{'guards':5,'proxy':6,'original_behavior':24},'technical_checks':'PASS','overall_acceptance':'REWORK_REQUIRED_CAMERA_REDESIGN','AC1':'FAIL','AC2':'PASS_PROXY_ONLY','AC3':'PASS','AC4':'PASS','AC5':'PASS_SAMPLED','AC6':'PASS','AC7':'SEE_REPORT'}
(R/'review/final-verification.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
