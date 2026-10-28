import bpy,json,hashlib,math,ast
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];candidate=Path(bpy.data.filepath);ver=candidate.stem.rsplit('-',1)[-1]
# Reuse pure fingerprint helpers, not the title/water verification execution.
tree=ast.parse((R/'scripts/verify_title_water.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in {'digest','actions','objects','protected_samples','inside','cross','crosses','dist'}],type_ignores=[]),'<verification helpers>','exec'))
cfg=json.loads((R/f'review/bridge-change-{ver}.json').read_text())
def inspect():
 s=bpy.context.scene;s.frame_set(156);di=s.objects['SF_CN_LAYOUT'].matrix_world.inverted()
 def points(name):
  o=s.objects[name];return [di@o.matrix_world@v.co for v in o.data.vertices]
 water=points('SF_BASIN_WATER_SURFACE');n=len(water)//2;outer=water[:n];inner=water[n:]
 def wet(p):return inside(p,outer)and not inside(p,inner)
 support={}
 for name in ['DT_LEFT','DT_LEFT_REAR','DT_CENTER','DT_FACADE','DT_RIGHT','DT_PAVILION','DT_TRADITIONAL','DT_TRADITIONAL_REAR']:
  root=s.objects[name];feet=[p for o in root.children_recursive if o.type=='MESH'and not o.hide_render for p in points(o.name)if 1.20<=p.z<=1.40]
  support[name]=sum(wet(p)for p in feet)
 a,b=map(Vector,cfg['bridge_endpoints_local']);side=Vector((-(b-a).y,(b-a).x,0)).normalized()
 samples=[a.lerp(b,t)+side*off for t in [.2,.3,.4,.5,.6,.7,.8]for off in [-.25,0,.25]]
 seam=max(math.hypot(p.x-q.x,p.y-q.y)for ring in [points('SF_FRONT_LAND')[n:],points('SF_BASIN_OUTER_WALL')[:n],points('SF_BASIN_OUTER_WALL')[n:]]for p,q in zip(outer,ring))
 return {'building_foot_samples_in_water':support,'channel_samples_under_bridge':len(samples),'water_under_bridge_samples':sum(wet(p)for p in samples),'abutment_centers_on_land':[not wet(p)for p in [a,b]],'outer_bank_crossings':crosses(outer),'seam_error':seam,'island_contained':all(inside(p,outer)for p in inner)}
after=inspect();aa=actions();ao=objects();am=protected_samples()
s=bpy.context.scene;s.frame_set(156);bridge=s.objects['WB_ARCH_MASONRY'];edges={}
for face in bridge.data.polygons:
 for a,b in zip(list(face.vertices),list(face.vertices)[1:]+[face.vertices[0]]):
  e=tuple(sorted((a,b)));edges[e]=edges.get(e,0)+1
newobjects=[o.name for o in s.objects if o.get('bridge_revision_owner')=='bridge-v029']
bpy.ops.wm.open_mainfile(filepath=str(R/'review/layout-proposal-v028.blend'));before=inspect();ba=actions();bo=objects();bm=protected_samples()
changed=[n for n in bo.keys()|ao.keys()if bo.get(n)!=ao.get(n)]
allowed=set(cfg['hidden_old_bridge'])|set(newobjects)|{'SF_BASIN_WATER_SURFACE','SF_FRONT_LAND','SF_BASIN_OUTER_WALL'}
unexpected=[n for n in changed if n not in allowed]
tests={'all_67_actions_preserved':aa==ba,'all_frame_camera_ship_cargo_crane_transforms_preserved':am==bm,'only_bridge_and_forebay_changed':not unexpected,'continuous_water_below_bridge':after['water_under_bridge_samples']==after['channel_samples_under_bridge'],'both_abutments_on_land':all(after['abutment_centers_on_land']),'no_new_building_foot_flooding':all(v<=before['building_foot_samples_in_water'][k]for k,v in after['building_foot_samples_in_water'].items()),'closed_arch_masonry_mesh':all(v==2 for v in edges.values()),'arch_opening_above_water':cfg['arch_opening_crown']-cfg['water_height']>1,'bank_no_self_intersections':not after['outer_bank_crossings'],'bank_water_seams_match':after['seam_error']<.0001,'island_contained':after['island_contained']}
result={'file':str(candidate),'sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'tests':tests,'after':after,'before':before,'new_bridge_objects':len(newobjects),'changed_existing_objects':[n for n in changed if n in bo],'unexpected_changes':unexpected,'arch_clearance_above_water_m':cfg['arch_opening_crown']-cfg['water_height'],'scope':'All actions and all integer-frame camera/ship/cargo/spreader/jib transforms; 21 water samples under the central span; lower-vertex building support checks, not full scene physics'}
(R/f'review/bridge-verified-{ver}.json').write_text(json.dumps(result,indent=2));print(json.dumps(result));assert all(tests.values())
