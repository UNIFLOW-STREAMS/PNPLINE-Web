import bpy,json,hashlib,math,ast
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];candidate=Path(bpy.data.filepath)
tree=ast.parse((R/'scripts/verify_title_water.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in {'digest','actions','objects','protected_samples','cross','crosses'}],type_ignores=[]),'<helpers>','exec'))
s=bpy.context.scene;s.frame_set(156);o=s.objects['SF_COAST_FOLDED_FACE'];n=512;ps=[v.co.copy()for v in o.data.vertices];faces=[list(p.vertices)for p in o.data.polygons];cfg=json.loads((R/'review/coast-change-v032.json').read_text());w=cfg['width_by_vertex']
seam=max((p.co-q).length for p,q in zip(s.objects['SF_FRONT_LAND'].data.vertices[:n],ps[:n]))
ring_crossings=[crosses(ps[j*n:(j+1)*n])for j in range(len(ps)//n)]
zeroareas=sum(p.area<1e-9 for p in o.data.polygons)
# Compare collisions at every source frame, restricted to newly expanded lateral surface.
changedfaces=[f for f in faces if any(abs(w[v%n])>.001 for v in f)]
bv=BVHTree.FromPolygons(ps,changedfaces)
collisions=[]
for f in range(s.frame_start,s.frame_end+1):
 s.frame_set(f);di=s.objects['SF_CN_LAYOUT'].matrix_world.inverted()
 for name in ['SF_HULL_BLUE','SF_HULL_RED']:
  hull=s.objects[name];hp=[di@hull.matrix_world@v.co for v in hull.data.vertices];hb=BVHTree.FromPolygons(hp,[list(p.vertices)for p in hull.data.polygons])
  if bv.overlap(hb):collisions.append([f,name])
s.frame_set(156)
aa=actions();ao=objects();am=protected_samples()
bpy.ops.wm.open_mainfile(filepath=str(R/'review/layout-proposal-v031.blend'));s=bpy.context.scene;s.frame_set(156);ba=actions();bo=objects();bm=protected_samples()
changed=[k for k in bo.keys()|ao.keys()if bo.get(k)!=ao.get(k)]
old=[v.co.copy()for v in s.objects['SF_COAST_FOLDED_FACE'].data.vertices];berth=[i for i,p in enumerate(old[:n])if -19<=p.x<=7.5]
err=max((ps[-n+i]-old[n+i]).length for i in berth)
checks={'all_actions_preserved':aa==ba,'all_integer_frame_camera_and_actor_transforms_preserved':am==bm,'only_outer_coast_mesh_changed':changed==['SF_COAST_FOLDED_FACE'],'upper_land_seam_zero':seam<1e-5,'front_berth_toe_unchanged':err<1e-5,'left_slope_outset_above_5m':cfg['left_max_outset_m']>5,'right_slope_outset_above_7m':cfg['right_max_outset_m']>7,'all_21_rings_no_self_intersection':not any(ring_crossings),'no_degenerate_faces':zeroareas==0,'no_ship_hull_intersection_with_new_slopes_all_frames':not collisions}
report={'file':str(candidate),'sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'checks':checks,'changed_objects':changed,'seam_error_m':seam,'berth_error_m':err,'ship_intersection_frames':collisions,'scope':'67 actions; camera/target/cargo/ship/spreader/jib matrices and ship surface intersection at every integer source frame; coast ring crossings and seams. Materials and optical wave effects unchanged.'}
(R/'review/coast-verified-v032.json').write_text(json.dumps(report,indent=2));print(json.dumps(report));assert all(checks.values())
