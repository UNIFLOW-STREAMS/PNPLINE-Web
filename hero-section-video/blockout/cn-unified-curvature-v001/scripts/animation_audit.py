"""Read-only dependency/anchor audit of immutable c9da20 expansion source."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
scene=bpy.context.scene
source=Path(bpy.data.filepath)
source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
assert source_hash=='c9da20e19f2cf732245df77c178b1fa85dae00753884ea3c586327a63cbe75bb'
scene.frame_set(0)
D=scene.objects['SF_CN_LAYOUT'].matrix_world.copy();I=D.inverted()
names=['PORT_CRANE_PLACEMENT','PORT_HOIST_PLACEMENT','PORT_BERTH_PLACEMENT','PORT_SHIP_WATERLINE_CORRECTION',
       'INTEGRATED_CN_CARRIER','CV_CARRIER_WORLD','A02_SHIP','A01_CONTAINER','W01_NEW_PALLET','P01_SPREADER',
       'CR_COMPACT_GANTRY','CR_SLEW_JIB','CR_TROLLEY_CARRIAGE','CR_SUSPENSION_HEAD','CAM_MASTER','CAM_LOOK_TARGET',
       'INTEGRATED_CN_CAMERA','INTEGRATED_CN_CAMERA_TARGET']
names+=sorted(o.name for o in scene.objects if o.name.startswith(('CR_WORKING_CABLE','PORT_COMPANION_CRANE')))
objects={}
for name in names:
 o=scene.objects[name];ad=o.animation_data
 constraints=[]
 for c in o.constraints:
  constraints.append({'name':c.name,'type':c.type,'target':getattr(getattr(c,'target',None),'name',None),'influence':c.influence,'mute':c.mute})
 drivers=[]
 if ad:
  for fc in ad.drivers:
   drivers.append({'path':fc.data_path,'index':fc.array_index,'expression':fc.driver.expression,
                   'variables':[{'name':v.name,'type':v.type,'targets':[{'id':t.id.name if t.id else None,'path':t.data_path,'space':getattr(t,'transform_space',None)}for t in v.targets]}for v in fc.driver.variables]})
 local=I@o.matrix_world
 objects[name]={'parent':o.parent.name if o.parent else None,'location_local':list(local.translation),'up_local':list(local.to_quaternion()@Vector((0,0,1))),
                'matrix_local':[list(r)for r in local],'action':ad.action.name if ad and ad.action else None,'constraints':constraints,'drivers':drivers,
                'children':[c.name for c in o.children]}
feet={}
for o in scene.objects['CR_COMPACT_GANTRY'].children_recursive:
 if o.type=='MESH'and any(t in o.name.upper()for t in ['FOOT','LEG','BOGIE','BASE']):
  points=[I@o.matrix_world@v.co for v in o.data.vertices]
  feet[o.name]={'min':[min(v[i]for v in points)for i in range(3)],'max':[max(v[i]for v in points)for i in range(3)]}
frames=[]
for f in [0,24,48,57,75,108,118,137,165,180,190,210,230,243,252,253,275,315,465,720,989]:
 scene.frame_set(f)
 frames.append({'frame':f,'poses':{n:[list(r)for r in I@scene.objects[n].matrix_world]for n in ['A02_SHIP','A01_CONTAINER','W01_NEW_PALLET','P01_SPREADER','CR_TROLLEY_CARRIAGE','CR_SUSPENSION_HEAD','CAM_MASTER','CAM_LOOK_TARGET']}})
scene.frame_set(0)
ocean=scene.objects['EARTH_CONTINUOUS_OCEAN']
report={'source':str(source),'sha256':source_hash,'fps':scene.render.fps,'timeline':[scene.frame_start,scene.frame_end],
        'layout_world':[list(r)for r in D],'ocean_center_local':list((I@ocean.matrix_world).translation),
        'objects':objects,'crane_foot_bounds':feet,'frames':frames}
(ROOT/'review/animation-source-audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('ANIMATION_ANCHORS',json.dumps({'ocean_center_local':report['ocean_center_local'],'objects':{n:{k:v for k,v in r.items()if k in ['parent','location_local','up_local','constraints','drivers']}for n,r in objects.items()},'feet':feet}),flush=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==source_hash
