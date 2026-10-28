import bpy,json,hashlib
from pathlib import Path
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;objs=[o for o in s.objects if o.get('letter') in list('CHINA') and o.get('s2_reveal_owner')];visible={}
for f in range(1393):
 s.frame_set(f);dg=bpy.context.evaluated_depsgraph_get();p=s.camera.matrix_world.translation;row={}
 for o in objs:
  polys=list(o.data.polygons);count=0
  for poly in polys[::max(1,len(polys)//48)]:
   wp=o.matrix_world@poly.center;v=world_to_camera_view(s,s.camera,wp)
   if v.z<=0 or not 0<v.x<1 or not 0<v.y<1:continue
   hit,loc,normal,index,obj,matrix=s.ray_cast(dg,p,(wp-p).normalized(),distance=(wp-p).length+.01)
   if hit and obj.original==o.original:count+=1
  if count:row[o.name]=count
 if row:visible[f]=row
(R/'review/title-visibility.json').write_text(json.dumps({'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'sampled_frames':1393,'visible_polygon_samples':visible,'note':'Polygon-centre samples include side/back surfaces; counts do not equal readable words or screen area.'},indent=2));print('TITLE VISIBLE FRAMES',list(visible))
