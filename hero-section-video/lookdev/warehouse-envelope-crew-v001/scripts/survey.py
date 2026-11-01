import bpy,sys,math,json,numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1]
B=R.parents[1]/'blockout'
sys.path[:0]=[str(R.parent/'us-warehouse-curvature-v001/scripts'),str(B/'curvature-rework-v001/scripts'),str(R.parent/'container-ship-v001/scripts')]
from surface_site import sphere,arc,basis
S=bpy.context.scene
U=S.objects['US_FRAME']
def flat(p):return arc(np.array(U.matrix_world.inverted()@Vector(p)))
def loc(o):return flat(o.matrix_world.translation).round(3).tolist()
import re
s=S;s.frame_set(0)
res={}
for o in s.objects:
 if (o.name.startswith(('CH_','WH_FACADE','WH_SIDE','WH_PARTIAL','WH_TRUSS_36','WH_END','WH_INBOUND','DSP_WH','WH_ROOF','WH_INTERIOR')) or re.search(r'(?i)(worker|person|staff|human|figure|operator|driver|pedestrian|laborer|crew|torso|packer|picker|loader|foreman|forklift)',o.name)) and not o.name.startswith('SURF_'):
  pts=np.array([flat(o.matrix_world@v.co) for v in o.data.vertices]) if o.type=='MESH' else None
  res[o.name]=[o.parent.name if o.parent else None,o.type,loc(o),[pts.min(0).round(2).tolist(),pts.max(0).round(2).tolist()] if pts is not None and len(pts) else None,o.hide_render, [m.name for m in o.data.materials] if o.type=='MESH' else None]
frames={}
for f in list(range(600,990,10))+[725,815,835,855]:
 s.frame_set(f)
 l=s.objects['CH_LOADER'];im=l.matrix_world.inverted()
 frames[f]=dict(cam=loc(s.camera),target=loc(s.objects['CAM_LOOK_TARGET']),loader=loc(l),support=list(np.array(im@s.objects['CH_LOAD_SUPPORT'].matrix_world.translation).round(3)),arms=[[(list(np.array(im@(o.matrix_world@Vector((0,0,i)))).round(3))) for i in [-.5,.5]] for o in [s.objects['CH_LOAD_ARM_0'],s.objects['CH_LOAD_ARM_1']]])
(R/'review/survey.json').write_text(json.dumps(dict(objects=res,frames=frames,markers=[(m.frame,m.name) for m in s.timeline_markers]),indent=1,default=float))
print('SURVEY COMPLETE')


