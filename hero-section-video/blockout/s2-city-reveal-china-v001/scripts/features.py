import bpy,json,math,hashlib,sys
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];s=bpy.context.scene
names=['CN_LM_SPHERE_TOWER_upper_sphere','CN_LM_SPHERE_TOWER_lower_sphere','CN_LM_SPHERE_TOWER_spire','CN_LM_OPEN_TOP_TOWER_lintel']+[f'CHINA_{i}_{c}' for i,c in enumerate('CHINA')]
out={};valid=[];speeds=[];prev=None
for f in range(84,481):
 s.frame_set(f);cam=s.camera;pos=cam.matrix_world.translation.copy();q=cam.matrix_world.to_quaternion();row={}
 if prev:speeds.append([f,(pos-prev[0]).length,math.degrees(2*math.acos(min(1,abs(q.dot(prev[1])))))])
 prev=(pos,q)
 if not 96<=f<=216:continue
 dg=bpy.context.evaluated_depsgraph_get();all_inside=True
 for n in names:
  o=s.objects.get(n)
  if not o:row[n]={'missing':True};all_inside=False;continue
  pts=[world_to_camera_view(s,cam,o.matrix_world@v.co) for v in o.data.vertices]
  inside=all(p.z>0 and 0<=p.x<=1 and 0<=p.y<=1 for p in pts);all_inside &= inside
  # Front red face / feature polygon centres: ray samples, not readable area.
  polys=[p for p in o.data.polygons if not n.startswith('CHINA') or p.material_index==1]
  samples=polys[::max(1,len(polys)//32)];vis=0;inframe=0
  for poly in samples:
   wp=o.matrix_world@poly.center;ndc=world_to_camera_view(s,cam,wp)
   if ndc.z<=0 or not 0<=ndc.x<=1 or not 0<=ndc.y<=1:continue
   inframe+=1;direction=(wp-pos).normalized();hit,loc,normal,index,obj,matrix=s.ray_cast(dg,pos,direction,distance=(wp-pos).length+.01)
   if hit and obj.original==o.original:vis+=1
  row[n]={'inside':inside,'min_xy':[min(p[i] for p in pts) for i in range(2)],'max_xy':[max(p[i] for p in pts) for i in range(2)],'visible_polygon_samples':vis,'inframe_samples':inframe,'samples':len(samples)}
 if all_inside:valid.append(f)
 out[f]=row
result={'blend':bpy.data.filepath,'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'fully_inframe_frames':valid,'features':out,'motion':speeds,'max_m_per_frame':max(x[1] for x in speeds),'max_deg_per_frame':max(x[2] for x in speeds),'note':'Projection and polygon-centre ray samples supplement, do not replace, visual legibility review.'}
(R/'review'/('features-'+Path(bpy.data.filepath).stem+'.json')).write_text(json.dumps(result,indent=2));print('INFRAME',valid,'SPEED',result['max_m_per_frame'],result['max_deg_per_frame'])
