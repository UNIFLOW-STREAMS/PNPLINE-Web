"""Rebuild two configurations in fresh processes; verify deterministic structure
and safe rejection of duplicates/overwrites. No baseline writes."""
import subprocess,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];B='C:/Program Files/Blender Foundation/Blender 5.1/blender.exe'
records=[]
def call(name,args,expected=0):
 cmd=[B,'--background','--factory-startup','--python-exit-code','1']+args
 with (R/'review/logs'/f'{name}.log').open('w',encoding='utf8') as f:p=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
 records.append({'name':name,'command':cmd,'exit_code':p.returncode,'expected_success':expected==0})
 (R/'review/reproduce-commands.json').write_text(json.dumps(records,indent=2))
 assert (p.returncode==0)==(expected==0),name
base=R/'inputs/base.blend';config=R/'proxy-config.json';out=R/'review/reproduced.blend';script=R/'scripts/build_proxy.py'
args=['--python',str(script),'--','--base',str(base),'--output',str(out),'--config',str(config)]
call('reproduce-build',args);before=hashlib.sha256(out.read_bytes()).hexdigest();call('overwrite-refused',args,1);assert before==hashlib.sha256(out.read_bytes()).hexdigest()
c=json.loads(config.read_text());c['base_sha256']=before;dup=R/'review/duplicate-test-config.json';dup.write_text(json.dumps(c))
call('duplicate-refused',['--python',str(script),'--','--base',str(out),'--output',str(R/'review/duplicate-must-not-exist.blend'),'--config',str(dup)],1)
assert not(R/'review/duplicate-must-not-exist.blend').exists()
call('reproduced-render',[str(out),'--python',str(R/'scripts/render.py'),'--','--output',str(R/'review/reproduced-render'),'--frames','96,148,216,278,456'])
call('reopened-render',[str(R/'master-cn-city-proxy-v001.blend'),'--python',str(R/'scripts/render.py'),'--','--output',str(R/'review/reopened-render'),'--frames','96,148,216,278,456'])
from PIL import Image,ImageChops
comparisons={}
for f in [96,148,216,278,456]:
 a=Image.open(R/'preview/after-frames'/f'{f:04}.png').convert('RGB')
 for kind in ['reproduced','reopened']:
  b=Image.open(R/'review'/f'{kind}-render'/f'{f:04}.png').convert('RGB');equal=ImageChops.difference(a,b).getbbox() is None
  comparisons[f'{kind}-{f}']=equal;assert equal
(R/'review/render-reproduction.json').write_text(json.dumps({'pixel_equal':comparisons,'reproduced_sha256':before,'master_sha256':hashlib.sha256((R/'master-cn-city-proxy-v001.blend').read_bytes()).hexdigest()},indent=2));print('REPRODUCE_RGB_PASS',len(comparisons))
