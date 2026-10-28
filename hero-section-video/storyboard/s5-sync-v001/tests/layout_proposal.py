"""Saved-scene acceptance tests. Run against original first to reproduce mismatch."""
import bpy,sys,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;I=s.objects['US_FRAME'].matrix_world.inverted()
checks=[]
def check(name,ok,detail):
 checks.append({'name':name,'pass':bool(ok),'detail':detail});print(name, 'PASS' if ok else 'FAIL',detail,flush=True)
def center(o):return sum((o.matrix_world@Vector(v) for v in o.bound_box),Vector())/8
s.frame_set(648)
subjects=[s.objects[n] for n in ['SHIP_HULL','A01_CONTAINER','WAREHOUSE_FLOOR']]
points=[world_to_camera_view(s,s.camera,center(o) if o.type=='MESH' else o.matrix_world.translation) for o in subjects]
check('S4-05 ship left / truck middle / warehouse right',points[0].x<points[1].x<points[2].x and .35<points[1].x<.85,[list(v) for v in points])
check('Ship on +Y sea side; warehouse on -Y land side',(I@center(subjects[0])).y>12 and (I@center(subjects[2])).y<0,[(I@center(o)).y if o.type=='MESH' else (I@o.matrix_world.translation).y for o in subjects])
truck=s.objects['A03_TRAILER'];camera_local=truck.matrix_world.inverted()@s.camera.matrix_world.translation
check('Rear visible at departure',camera_local.x < -3,list(camera_local))
check('No mirrored vehicle or lettering transforms',all(s.objects[n].matrix_world.determinant()>0 for n in ['A03_TRAILER','A03_TRACTOR','A01_CONTAINER','PNPLINE_BRAND_SIDE_-0.776','PNPLINE_BRAND_SIDE_0.776']), 'positive determinants')
ground=[]
for n in ['US_QUAY','US_LAND_TERRACE','E07_INBOUND_ROAD','E09_MANEUVER_YARD']:
 o=s.objects[n];ground.append(BVHTree.FromPolygons([I@o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons]))
wheels=[o for o in s.objects if o.name.startswith('A03') and '_WHEEL_' in o.name]
worst=0;worst_at=None;missing=[];stationary={};hitch=0
for j in range(552*4,948*4+1):
 f=j/4;s.frame_set(int(f),subframe=f%1)
 for o in wheels:
  c=(I@o.matrix_world).translation
  hits=[b.ray_cast(c+Vector((0,0,5)),Vector((0,0,-1)),20)[0] for b in ground];valid=[v.z for v in hits if v is not None]
  if not valid:missing.append((f,o.name));continue
  bottom=min((I@o.matrix_world@v.co).z for v in o.data.vertices)
  if abs(bottom-max(valid))>worst:worst=abs(bottom-max(valid));worst_at=(f,o.name,bottom,max(valid),list(o.location))
 if f in [648,672,810,842,848,849,890,900]:stationary[str(int(f))]=list((I@truck.matrix_world).translation)
check('Every wheel supported, quarter-frame sweep',not missing and worst<.002,{'max_error_m':worst,'worst_at':worst_at,'missing_count':len(missing)})
check('Departure unchanged at f648',abs(Vector(stationary['648']).x)<.0001,stationary)
check('Aligned hold f810-848',(Vector(stationary['810'])-Vector(stationary['848'])).length<.0001,stationary)
check('Reverse distance 5.2m; stop f890-900',abs((Vector(stationary['890'])-Vector(stationary['848'])).length-5.2)<.001 and (Vector(stationary['900'])-Vector(stationary['890'])).length<.0001,stationary)
for f,target in [(810,0),(842,math.pi*1.5),(890,math.pi*1.5)]:
 s.frame_set(f);angles=[abs(s.objects[n].rotation_euler.z) for n in ['A01_DOOR_L','A01_DOOR_R']]
 check('Door timing '+str(f),all(abs(a-target)<.0001 for a in angles),angles)
for n in ['A01_DOOR_L','A01_DOOR_R']:
 check('Approved hinge rear offset '+n,abs(s.objects[n].location.x+1.65)<.0001,list(s.objects[n].location))
o=s.objects['DOCK_BRIDGE'];pts=[I@o.matrix_world@v.co for v in o.data.vertices];extent=[max(v[k] for v in pts)-min(v[k] for v in pts) for k in range(3)]
check('Approved dock bridge width/top',abs(extent[1]-1.34)<.001 and abs(max(v.z for v in pts)-1.92)<.001,extent)
report={'file':bpy.data.filepath,'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'checks':checks,'passed':all(x['pass'] for x in checks)}
out=Path(sys.argv[sys.argv.index('--')+1]) if '--' in sys.argv else R/'review/layout-test.json';out.write_text(json.dumps(report,indent=2),encoding='utf8')
if not report['passed']:raise AssertionError('Layout acceptance failed; see report')
