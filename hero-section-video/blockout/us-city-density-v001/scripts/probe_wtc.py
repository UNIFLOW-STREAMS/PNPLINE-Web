"""Read-only baseline WTC contacts and nearest dry road-free replacement pockets."""
import bpy,ast,json,math,sys
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'review';SOURCE=ROOT.parent/'cn-shanghai-density-v001/pnpline-cn-shanghai-density-v001.blend';CANDIDATE=ROOT/'pnpline-us-city-density-v001.blend'
for path,names in [(ROOT/'scripts/verify_geometry.py',{'visible','under','params','surface','bounds','boxhit','mesh_data','combine'}),
 (ROOT.parent/'cn-shanghai-density-v001/scripts/survey_shanghai.py',{'hull'}),
 (ROOT.parent/'cn-shanghai-density-v001/scripts/build.py',{'bounds','overlaps'})]:
 tree=ast.parse(path.read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in names],type_ignores=[]),str(path),'exec'),globals())
# Restore a 3D bounds helper separately: overlaps uses a 2D polygon bounds helper.
def bbox(vs):return ([min(v[i]for v in vs)for i in range(3)],[max(v[i]for v in vs)for i in range(3)])if vs else None
def comb(objects):
 vs=[];fs=[]
 for o in objects:
  if not visible(o):continue
  v,f=mesh_data(o);off=len(vs);vs.extend(v);fs.extend(tuple(off+i for i in p)for p in f)
 return BVHTree.FromPolygons(vs,fs),vs
C=Vector((0,0,-140));report={}
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s=bpy.context.scene;s.frame_set(349);I=s.objects['US_FRAME'].matrix_world.inverted()
oldroot=s.objects['CV_GLASS_TOWER_UC_CITY_DISTRICT'];tree,vs=comb([o for o in oldroot.children_recursive if visible(o)])
contacts={}
for name in ['CV_SUPPORT_MANEUVER','E09_MANEUVER_YARD','UC_CITY_AVENUE.003','UC_CITY_STREET.002']:
 t,_=comb([s.objects[name]]);contacts[name]=len(t.overlap(tree))
report['original_glass_contacts']=contacts
bpy.ops.wm.open_mainfile(filepath=str(CANDIDATE));s=bpy.context.scene;s.frame_set(349);I=s.objects['US_FRAME'].matrix_world.inverted()
survey=json.loads((OUT/'us-survey.json').read_text());delivery=json.loads((ROOT/'delivery.json').read_text())
groups=[]
for row in survey['groups']:
 objs=[s.objects[n]for n in row['members']if n in s.objects and visible(s.objects[n])]
 if not objs:continue
 pp=[params(p)for o in objs for p in mesh_data(o)[0]]
 if pp:groups.append({'id':row['root'],'poly':hull(pp)})
for row in delivery['replacements']+delivery['sites']+delivery['tree_sites']:
 if row['root']=='USD_ONEWTC_ROOT':continue
 objs=[s.objects[n]for n in row['objects']if n in s.objects and visible(s.objects[n])]
 pp=[params(p)for o in objs for p in mesh_data(o)[0]]
 if pp:groups.append({'id':row['root'],'poly':hull(pp)})
road,rv=comb([s.objects[r['name']]for r in survey['protected_road_port_objects']])
ground,gv=comb([s.objects[n]for n in ['US_LAND_TERRACE','CE_NY_CURVED_LAND']])
accepted=[];blocked=[];source=Vector((20.670398712158203,33.337947845458984))
def exact_probe(x,y,scale=1):
 n=(surface(x,y,.84)-C).normalized();F=Matrix.Translation(surface(x,y,.84))@Vector((0,0,1)).rotation_difference(n).to_matrix().to_4x4()@Matrix.Rotation(math.radians(-32),4,'Z')
 poly=[params(F@Vector((a*2.57*scale,b*2.57*scale,0)))[:2]for a,b in [(-1,-1),(1,-1),(1,1),(-1,1)]]
 hits=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  for t in range(25):
   x1=a[0]+(b[0]-a[0])*t/25;y1=a[1]+(b[1]-a[1])*t/25;p=surface(x1,y1);n=(p-C).normalized()
   if road.ray_cast(p+n*80,-n,85)[0]is not None:hits.append([x1,y1])
 conflicts=[r['id']for r in groups if overlaps(poly,r['poly'],.10)]
 delta=F@Matrix.Diagonal((scale,scale,1,1))@(I@s.objects['USD_ONEWTC_ROOT'].matrix_world).inverted();vs=[];fs=[]
 for o in list(s.objects['USD_ONEWTC_ROOT'].children_recursive)+[s.objects['USD_ONEWTC_FOUNDATION']]:
  if not visible(o):continue
  ov,of=mesh_data(o);off=len(vs);vs.extend(delta@v for v in ov);fs.extend(tuple(off+i for i in f)for f in of)
 moving=BVHTree.FromPolygons(vs,fs);actual={};detail={}
 for name in conflicts:
  o=s.objects[name];fixed,_=comb([o]+list(o.children_recursive));count=len(moving.overlap(fixed))
  if count:
   actual[name]=count
   if 'LETTER'in name:
    detail[name]={}
    for child in [o]+list(o.children_recursive):
     if not visible(child):continue
     t,_=comb([child]);count=len(moving.overlap(t))
     if count:detail[name][child.name]=count
 return {'xy':[x,y],'width_depth':5*scale,'footprint_parameter':poly,'conflicts':conflicts,'road_hit_samples':hits,'actual_architecture_contact_pairs':actual,'letter_contact_detail':detail}
design_x,design_y=10,45.5
report['requested_design_10_45_5']=exact_probe(.8480480909347534*design_x+.5299192667007446*design_y-19.607009887695312,-.5299192667007446*design_x+.8480480909347534*design_y+6.622219085693359)
report['nearby_design_tests']=[]
for xd,yd,scale in [(10,44.75,.96),(10,44.8,.96),(10,44.85,.96),(9.5,44.85,.96),(10,44.85,.94)]:
 row=exact_probe(.8480480909347534*xd+.5299192667007446*yd-19.607009887695312,-.5299192667007446*xd+.8480480909347534*yd+6.622219085693359,scale);row['design_xy']=[xd,yd];report['nearby_design_tests'].append(row)
if '--target-only'in sys.argv:
 (OUT/'wtc-placement-probe.json').write_text(json.dumps(report,indent=2));print('TARGET_PROBES_COMPLETE',flush=True);sys.exit(0)
for yi in range(40):
 y=28+yi*.5
 for xi in range(56):
  x=10+xi*.5;n=(surface(x,y,.84)-C).normalized();F=Matrix.Translation(surface(x,y,.84))@Vector((0,0,1)).rotation_difference(n).to_matrix().to_4x4()@Matrix.Rotation(math.radians(-32),4,'Z')
  points=[F@Vector((a*2.57,b*2.57,0))for a,b in [(-1,-1),(1,-1),(1,1),(-1,1)]];poly=[params(p)[:2]for p in points]
  conflict=[r['id']for r in groups if overlaps(poly,r['poly'],.15)]
  if conflict:
   if len(conflict)<=2:blocked.append({'xy':[x,y],'distance':math.hypot(x-source.x,y-source.y),'conflicts':conflict})
   continue
  samples=[]
  for a,b in zip(poly,poly[1:]+poly[:1]):samples.extend([(a[0]+(b[0]-a[0])*t/20,a[1]+(b[1]-a[1])*t/20)for t in range(20)])
  dry=True
  for xx,yy in samples:
   p=surface(xx,yy);n=(p-C).normalized()
   if ground.ray_cast(p+n*20,-n,30)[0]is None or road.ray_cast(p+n*80,-n,85)[0]is not None:dry=False;break
  if dry:accepted.append({'xy':[x,y],'distance':math.hypot(x-source.x,y-source.y),'footprint_parameter':poly})
accepted.sort(key=lambda r:r['distance']);blocked.sort(key=lambda r:r['distance'])
report['safe_5m_square_candidates']=accepted[:25];report['architecture_conflicts_near_source']=blocked[:30]
(OUT/'wtc-placement-probe.json').write_text(json.dumps(report,indent=2))
print('WTC_PROBE',json.dumps({'baseline_contacts':contacts,'safe_slots':[(r['xy'],r['distance'])for r in accepted[:10]]}),flush=True)
