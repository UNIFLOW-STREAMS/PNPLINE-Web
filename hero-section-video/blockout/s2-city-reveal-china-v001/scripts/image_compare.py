from PIL import Image
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];comparisons={}
for label,a,b,frames in [('limited_vs_final','preview/limited-frames','preview/final-frames',range(84,481)),('reproduced_vs_final','review/reproduced-frames','preview/final-frames',[96,144,156,170,216,278,456])]:
 changed=[]
 for f in frames:
  if Image.open(R/a/f'{f:04}.png').convert('RGB').tobytes()!=Image.open(R/b/f'{f:04}.png').convert('RGB').tobytes():changed.append(f)
 comparisons[label]={'frames':list(frames),'changed_rgb_frames':changed}
changed=[]
for f in range(84,481):
 if Image.open(R/'preview/source-frames'/f'{f:04}.png').convert('RGB').tobytes()!=Image.open(R/'preview/titlebase-frames'/f'{f:04}.png').convert('RGB').tobytes():changed.append(f)
comparisons['title_added_old_camera']={'changed_rgb_frames':changed}
comparisons['final_sha256']=hashlib.sha256((R/'master-s2-city-reveal-china-v001.blend').read_bytes()).hexdigest()
(R/'review/rgb-comparison.json').write_text(json.dumps(comparisons,indent=2));print({k:len(v.get('changed_rgb_frames',[])) if isinstance(v,dict) else v for k,v in comparisons.items()})
assert not comparisons['limited_vs_final']['changed_rgb_frames'] and not comparisons['reproduced_vs_final']['changed_rgb_frames']
