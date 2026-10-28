import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;s.frame_set(156);file=Path(bpy.data.filepath);o=s.objects['SF_COAST_FOLDED_FACE'];I=o.matrix_world.inverted();sea=s.objects['EARTH_CONTINUOUS_OCEAN'];e=sea.evaluated_get(bpy.context.evaluated_depsgraph_get());me=e.to_mesh();bv=BVHTree.FromPolygons([I@e.matrix_world@v.co for v in me.vertices],[list(p.vertices) for p in me.polygons]);e.to_mesh_clear();pts=[v.co.copy() for v in o.data.vertices];errors=[]
for p in pts[-512:]:
 hit=bv.ray_cast(Vector((p.x,p.y,80)),Vector((0,0,-1)),160)[0];assert hit is not None;errors.append(p.z-hit.z)
cn=s.objects['CN_FRAME'].matrix_world.copy();layout=s.objects['SF_CN_LAYOUT'].matrix_local.copy()
def moving(o):
 while o:
  if o.animation_data and o.animation_data.action:return True
  o=o.parent
 return False
def under(o,n):
 while o:
  if o.name==n:return True
  o=o.parent
 return False
vs=[];fs=[]
for o in s.objects:
 if o.type!='MESH' or o.hide_render or moving(o) or not under(o,'CN_FRAME'):continue
 k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([tuple(k+i for i in p.vertices) for p in o.data.polygons])
env=BVHTree.FromPolygons(vs,fs);clear=[]
for f in range(341):
 s.frame_set(f);p=s.camera.matrix_world.translation;hit=env.find_nearest(p);clear.append(hit[3])
bpy.ops.wm.open_mainfile(filepath=str(R/'inputs/base.blend'));s=bpy.context.scene;s.frame_set(156);old=s.objects['SF_COAST_FOLDED_FACE'];maxxy=max((Vector((p.x,p.y))-Vector(tuple(v.co[:2]))).length for p,v in zip(pts,old.data.vertices));rim=max((p-v.co).length for p,v in zip(pts[:512],list(old.data.vertices)[:512]))
checks={'all_512_toes_submerged_6cm':max(abs(x+.06) for x in errors)<.0001,'coast_xy_contour_unchanged':maxxy<.00001,'upper_city_rim_unchanged':rim<.00001,'chosen_CN_rotation_unchanged':cn==s.objects['CN_FRAME'].matrix_world,'layout_rotation_unchanged':layout.to_3x3()==s.objects['SF_CN_LAYOUT'].matrix_local.to_3x3(),'camera_clear_of_static_city_surfaces':min(clear)>.1}
report={'file':str(file),'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'checks':checks,'toe_clearance_minmax': [min(errors),max(errors)],'camera_min_surface_distance_m':min(clear),'camera_min_frame':clear.index(min(clear)),'rim_max_error_m':rim,'xy_max_error_m':maxxy}
(R/'review/final-coast-connection.json').write_text(json.dumps(report,indent=2));print(json.dumps(report));assert all(checks.values())
