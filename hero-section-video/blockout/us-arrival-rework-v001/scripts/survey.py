import bpy,sys,ast,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];D=R.parent/'us-city-concept-v001'
allow=json.loads((D/'allowed-changes.json').read_text())
helpers=ast.parse((D/'scripts/verify_preservation.py').read_text())
exec(compile(ast.Module(body=[n for n in helpers.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'inherited-signatures','exec'))
sys.argv.append('--diagnostic')
def owned():
 out={}
 for o in bpy.context.scene.objects:
  if not o.get('uc_owner'):continue
  row={'matrix':list(map(list,o.matrix_world)),'parent':o.parent.name if o.parent else None,'visibility':[o.hide_render,o.hide_viewport], 'modifiers':[props(m) for m in o.modifiers]}
  if o.type=='MESH':row['mesh']=[[list(v.co) for v in o.data.vertices],[[list(p.vertices),p.material_index,p.use_smooth] for p in o.data.polygons]]
  if o.type=='CURVE':row['curve']=[[[list(p.co) for p in sp.points] for sp in o.data.splines],o.data.bevel_depth]
  if hasattr(o.data,'materials'):row['materials']=[node_data(m) for m in o.data.materials]
  out[o.name]=digest(row)
 return out
data={}
for label in ['current-v004','verified-v004']:
 bpy.ops.wm.open_mainfile(filepath=str(R/'inputs'/f'{label}.blend'))
 s=bpy.context.scene
 a=snapshot();a.pop('debug');a['owned']=owned();data[label]=a
diff={}
for k in data['current-v004']:
 a,b=data['current-v004'][k],data['verified-v004'][k]
 diff[k]=[n for n in a.keys()|b.keys() if a.get(n)!=b.get(n)] if isinstance(a,dict) else (a!=b)
(R/'review/input-comparison.json').write_text(json.dumps(diff,indent=2))
# Actual coordinates and bow geometry; both remain read-only.
rows=[]
for f in [216,240,264,288,300,330,360,390,421,456,480,510,540,576,600,648,720]:
 s.frame_set(f);u=s.objects['US_FRAME'].matrix_world;inv=u.inverted();ship=s.objects['A02_SHIP'];cam=s.objects['CAM_MASTER']
 rows.append({'frame':f,'ship':list(inv@ship.matrix_world.translation),'ship_axes':[list(inv.to_3x3()@ship.matrix_world.to_3x3().col[i]) for i in range(3)],'cam':list(inv@cam.matrix_world.translation),'target':list(inv@s.objects['CAM_LOOK_TARGET'].matrix_world.translation),'lens':cam.data.lens})
names=['CAM_MASTER','CAM_LOOK_TARGET','A02_SHIP','US_FRAME','UC_LIBERTY']
details={o.name:{'parent':o.parent.name if o.parent else None,'constraints':[props(c) for c in o.constraints],'location':list(o.location),'rotation':list(o.rotation_euler),'data':o.data.name if o.data else None,'children':[c.name for c in o.children]} for o in s.objects if o.name in names}
shipgeom={o.name:{'bounds':[list(v) for v in o.bound_box],'local':list(map(list,o.matrix_local))} for o in s.objects if o.parent and o.parent.name=='A02_SHIP'}
(R/'review/survey.json').write_text(json.dumps({'rows':rows,'details':details,'ship_children':shipgeom,'p02':[o.name for o in s.objects if o.name.startswith(('P02','CR_US'))]},indent=2))
print('INPUT_DIFFERENCES',json.dumps(diff));print('ROUTE',json.dumps(rows))
