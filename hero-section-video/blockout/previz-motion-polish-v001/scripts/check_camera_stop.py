import bpy,sys,json,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];s=bpy.context.scene
sys.path.insert(0,str(R/'scripts'));from motion import TimeMap
cfg=json.loads((R/'config.json').read_text());variant=s.get('motion_polish_variant')
m=TimeMap(1392,cfg['easing'],cfg['compression_B'] if variant=='B' else []) if variant else TimeMap(1392)
rows=[]
for source in [96,216,456,648,900,1200]:
 f=m.forward(source);points=[]
 for x in [f-.25,f,f+.25]:
  s.frame_set(int(x),subframe=x%1);points.append(s.camera.matrix_world.translation.copy())
 speeds=[(b-a).length/.25 for a,b in zip(points,points[1:])]
 rows.append({'source':source,'output':f,'speeds':speeds})
print('CAMERA_JOINS',json.dumps(rows),flush=True)
assert all(min(r['speeds'])>.001 for r in rows),'Camera stops at a scene boundary'
