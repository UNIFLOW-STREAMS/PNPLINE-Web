"""Per-frame surface occlusion evidence, not an artistic acceptance substitute."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;file=Path(bpy.data.filepath)
def visible(point,allowed,dg):
 p=world_to_camera_view(s,s.camera,point)
 if not (.025<p.x<.975 and .025<p.y<.975 and p.z>0):return False
 origin=s.camera.matrix_world.translation;delta=point-origin
 hit,loc,n,i,o,m=s.ray_cast(dg,origin,delta.normalized(),distance=delta.length+.1)
 return bool(hit and o.name in allowed)
letter_samples={}
for ch in 'USA':
 o=s.objects['UC_LETTER_'+ch]
 faces=[p for p in o.data.polygons if o.data.materials[p.material_index].name=='UC_NAVY']
 letter_samples[o.name]=[faces[round(i*(len(faces)-1)/29)].center.copy() for i in range(30)]
lib=s.objects['UC_LIBERTY'];libnames={lib.name,*[o.name for o in lib.children_recursive]}
shipnames={'A02_SHIP',*[o.name for o in s.objects['A02_SHIP'].children_recursive],'A01_CONTAINER',*[o.name for o in s.objects['A01_CONTAINER'].children_recursive]}
rows=[]
for f in range(390,491):
 s.frame_set(f);dg=bpy.context.evaluated_depsgraph_get();ratios={}
 for name,pts in letter_samples.items():
  o=s.objects[name];ratios[name]=sum(visible(o.matrix_world@p,{name},dg) for p in pts)/len(pts)
 landmark={}
 for name in ['UC_LIBERTY_FLAME','UC_LIBERTY_CROWN','UC_LIBERTY_ROBE']:
  o=s.objects[name];p=sum((Vector(v) for v in o.bound_box),Vector())/8
  landmark[name]=visible(o.matrix_world@p,libnames,dg)
 stars={side:sum(visible(o.matrix_world@(sum((Vector(v) for v in o.bound_box),Vector())/8),{o.name},dg) for o in s.objects if o.name.startswith('UC_STAR_'+side)) for side in ['L','R']}
 bridge=s.objects['SHIP_BRIDGE'];ship=visible(bridge.matrix_world.translation,shipnames,dg)
 ok=all(v>=.7 for v in ratios.values()) and all(landmark.values()) and all(v>=3 for v in stars.values()) and ship
 rows.append({'f':f,'letters':ratios,'statue':landmark,'visible_stars':stars,'ship_bridge_visible':ship,'technical_co_visibility':ok})
intervals=[]
for row in rows:
 if row['technical_co_visibility']:
  if not intervals or intervals[-1][1]!=row['f']-1:intervals.append([row['f'],row['f']])
  else:intervals[-1][1]=row['f']
out={'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'intervals':[{'first':a,'middle':(a+b)//2,'last':b,'seconds':(b-a+1)/12} for a,b in intervals],'rows':rows,'limitations':'30 navy surface samples per letter; statue keypoint first-surface rays; >=3 stars each side. Continuous technical visibility is necessary but not sufficient artistic evidence.'}
(R/'review'/f'{file.stem}-visibility.json').write_text(json.dumps(out,indent=2));print('VISIBILITY_INTERVALS',out['intervals'])
