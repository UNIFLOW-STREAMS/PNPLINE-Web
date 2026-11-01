"""Disposable read-only-source terrain module test; never saves a blend."""
import bpy,sys,json,hashlib,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from terrain import build_unified_terrain,restore_cn_ocean
SOURCE=ROOT.parent/'cn-city-expansion-v001/pnpline-cn-city-expansion-v001.blend'
sha=hashlib.sha256(SOURCE.read_bytes()).hexdigest();assert sha=='c9da20e19f2cf732245df77c178b1fa85dae00753884ea3c586327a63cbe75bb'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s=bpy.context.scene;s.frame_set(0);D=s.objects['SF_CN_LAYOUT']
before_objects=set(s.objects.keys());before_mats=set(bpy.data.materials.keys());before_actions=set(bpy.data.actions.keys())
ocean=restore_cn_ocean(s,D)
assert set(s.objects.keys())==before_objects
assert set(bpy.data.materials.keys())==before_mats
assert set(bpy.data.actions.keys())==before_actions
col=bpy.data.collections.new('CNC_TERRAIN_TEST');s.collection.children.link(col)
obj,surface,report=build_unified_terrain(s,D,col)
top_faces=obj.data.polygons[:int(obj['cnc_top_face_count'])]
radial_dots=[p.normal.dot((p.center-surface.center).normalized())for p in top_faces if p.area>1e-10]
report['minimum_top_face_radial_dot']=min(radial_dots)
report['degenerate_top_faces']=sum(p.area<=1e-10 for p in top_faces)
checks={'one_component':report['connected_components']==1,'closed_manifold':report['nonmanifold_edges']==0,
 'outward_closed_volume':report['signed_volume']>0,'sphere_radius_accuracy':report['top_radius_max_error']<.0001,
 'all_top_edges_bounded':report['max_top_edge']<=report['requested_max_edge']+.0001,
 'ocean_US_untouched':ocean['far_and_US_coordinates_exact'],'original_smooth_flags':ocean['polygon_smooth_flags_exact'],
 'source_file_unchanged':hashlib.sha256(SOURCE.read_bytes()).hexdigest()==sha,
 'no_degenerate_top_faces':report['degenerate_top_faces']==0,
 'top_face_radial_normals':report['minimum_top_face_radial_dot']>.99998}
samples=[]
for x,y in [(-28,-15),(30,-15),(0,0),(-45,1),(45,32),(-41,58),(0,71),(-62,65)]:
 p=surface.point(x,y);n=surface.normal(x,y);F=surface.frame(x,y,.25);fz=F.to_3x3()@Vector((0,0,1))
 samples.append({'xy':[x,y],'z':surface.surface(x,y),'point':list(p),'normal':list(n),
                 'normal_frame_error':(n-fz).length,'radius_error':abs((p-surface.center).length-surface.radius)})
result={'source':str(SOURCE),'source_sha256':sha,'checks':checks,'terrain':report,
        'ocean':{k:v for k,v in ocean.items()if k!='changed_indices'},'samples':samples}
(ROOT/'review').mkdir(exist_ok=True)
(ROOT/'review/terrain-module-test.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('TERRAIN_TEST '+json.dumps(result,indent=2),flush=True)
