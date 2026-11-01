"""Check continuous camera travel between quarter-frame samples against new solids."""
import bpy,json,hashlib
from pathlib import Path
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;s.frame_set(349);I=s.objects['US_FRAME'].matrix_world.inverted()
vertices=[];faces=[];names=[]
for o in s.objects:
 if o.type!='MESH' or o.get('pt_role') not in ['container','crane','quay_fixture']:continue
 T=I@o.matrix_world;n=len(vertices);vertices.extend(T@v.co for v in o.data.vertices)
 faces.extend(tuple(i+n for i in p.vertices) for p in o.data.polygons);names.extend([o.name]*len(o.data.polygons))
tree=BVHTree.FromPolygons(vertices,faces);previous=None;hits=[];minimum=(1e9,None,None)
for q in range(989*4+1):
 f=q/4;s.frame_set(int(f),subframe=f-int(f));p=I@s.camera.matrix_world.translation
 nearest=tree.find_nearest(p)
 if nearest[0] is not None and nearest[3]<minimum[0]:minimum=(nearest[3],f,names[nearest[2]])
 if previous is not None:
  delta=p-previous
  if delta.length>1e-8:
   hit=tree.ray_cast(previous,delta.normalized(),delta.length)
   if hit[0] is not None:hits.append({'frame':f,'object':names[hit[2]]})
 previous=p
report={'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'quarter_frame_samples':989*4+1,'crossings':hits,'minimum_camera_surface_distance':minimum,'passed':not hits and minimum[0]>=.15}
(R/'review/camera-passage.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert report['passed']
