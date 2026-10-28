import bpy,json,math,hashlib,ast
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
s=bpy.context.scene
def mat(m):return [list(x)for x in m]
def curves(o):
 a=o.animation_data.action if o.animation_data else None
 return [[f.data_path,f.array_index,len(f.keyframe_points),[[round(k.co.x,3),round(k.co.y,5)]for k in f.keyframe_points][::max(1,len(f.keyframe_points)//12)]]for l in a.layers for st in l.strips for b in st.channelbags for f in b.fcurves]if a else []
s.frame_set(156)
rows={o.name:{'type':o.type,'parent':o.parent.name if o.parent else None,'collections':[c.name for c in o.users_collection],'world':mat(o.matrix_world),'dimensions':list(o.dimensions),'hide':o.hide_render,'constraints':[{'type':c.type,'target':getattr(getattr(c,'target',None),'name',None),'influence':c.influence}for c in o.constraints],'action':o.animation_data.action.name if o.animation_data and o.animation_data.action else None,'drivers':len(o.animation_data.drivers)if o.animation_data else 0}for o in s.objects}
roots=[o.name for o in s.objects if o.parent is None]
names=['CN_FRAME','US_FRAME','SF_CN_LAYOUT','SF_CHINA_C','SF_CHINA_A','A02_SHIP','A01_CONTAINER','A03_TRUCK','A04_PALLET','CAM_MASTER','CAM_LOOK_TARGET']
samples={}
for f in [0,72,96,144,156,170,178,192,216,240,300,360,420,456,480,532,600,648,672,720,842,900,1008,1200,1392]:
 s.frame_set(f);samples[f]={n:mat(s.objects[n].matrix_world)for n in names if n in s.objects}
out={'file':bpy.data.filepath,'version':bpy.app.version_string,'timeline':[s.frame_start,s.frame_end,s.render.fps,s.render.fps_base],'markers':[(m.name,m.frame)for m in s.timeline_markers],'camera':s.camera.name,'roots':roots,'objects':rows,'samples':samples,'curves':{n:curves(s.objects[n])for n in names if n in s.objects}}
(R/'review/baseline-inspection.json').write_text(json.dumps(out,indent=2))
# Pure comparison helpers only: never execute historical builders.
t=ast.parse((R.parent/'s2-styleframe-match-v001/scripts/verify_title_water.py').read_text())
exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef)and n.name in {'digest','actions','objects'}],type_ignores=[]),'<pure snapshot helpers>','exec'))
s.frame_set(156);current={'objects':objects(),'actions':actions()}
bpy.ops.wm.open_mainfile(filepath=str(R.parent/'previz-styleframe-integrated-v001/inputs/layout-proposal-v032.blend'))
bpy.context.scene.frame_set(156);old={'objects':objects(),'actions':actions()}
diff={k:[n for n in current[k].keys()|old[k].keys()if current[k].get(n)!=old[k].get(n)]for k in current}
(R/'review/source-differences.json').write_text(json.dumps(diff,indent=2));print('SOURCE_DIFF',diff)
print('INSPECTION',len(rows),'objects','roots',roots)
