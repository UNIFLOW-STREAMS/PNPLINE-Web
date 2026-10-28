"""Checks only the final file and its fresh rebuild; older trials remain diagnostics."""
from pathlib import Path
from PIL import Image
import json,hashlib
R=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
frames=[96,144,156,170,213,214,215,216,278,456]
out={'final_sha256':sha(R/'master-s2-city-reveal-china-v001.blend'),'reproduced_sha256':sha(R/'review/reproduced.blend'),'rgb':{},'commands':{}}
for label,folder in [('reopened','review/final-reopened'),('reproduced','review/final-reproduced-frames')]:
 failed=[]
 for f in frames:
  a=Image.open(R/folder/f'{f:04}.png').convert('RGB');b=Image.open(R/'preview/final-frames'/f'{f:04}.png').convert('RGB')
  if a.tobytes()!=b.tobytes():failed.append(f)
 out['rgb'][label]={'frames':frames,'different':failed}
for label in ['fixed-build-2','rotation-green-2','fixed-preservation','fixed-movie','fixed-reproduce','fixed-reproduce-compare','fixed-reproduced-render','fixed-reopened-render','fixed-spatial','fixed-guards','fixed-features-2','fixed-title-visibility']:
 record=json.loads((R/'review'/f'{label}-command.json').read_text());out['commands'][label]=record['exit_code']
out['pass_all']=not any(v['different'] for v in out['rgb'].values()) and all(x==0 for x in out['commands'].values())
(R/'review/final-qa.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
assert out['pass_all']
