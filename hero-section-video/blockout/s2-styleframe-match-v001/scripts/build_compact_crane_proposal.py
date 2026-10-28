"""Reference-shaped crane study. Not an animation-ready master: see collision report."""
import bpy,math,ast,json,sys
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;s.frame_set(156);out=Path(sys.argv[sys.argv.index('--')+1]);assert not out.exists()
version=out.stem.rsplit('-',1)[-1]
D=s.objects['SF_CN_LAYOUT'];DM=D.matrix_world.copy();DI=DM.inverted();col=bpy.data.collections.new('CRANE_STYLE_PROPOSAL');s.collection.children.link(col)
def tag(o):o['crane_revision_owner']='crane-v018';return o
t=ast.parse((R/'scripts/build_layout_proposal.py').read_text());exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef)and n.name in {'empty','mesh','box','tube','lathe','sphere','uvpoint'}],type_ignores=[]),'helpers','exec'))
M={k:bpy.data.materials['SF_'+k]for k in ['blue','white','navy','silver','gold','roof','cream']}
hidden=[]
for o in s.objects:
 if o.name.startswith('SF_CRANE') or o.name=='P01_TROLLEY' or o.name.startswith('P01_CABLE_') or o.name=='P01_SPREADER_FRAME':
  o.hide_render=True;o.hide_set(True);hidden.append(o.name)
root=empty('CR_COMPACT_GANTRY',D);root['status']='style proposal; S1 rig retarget approval required'
z=6.5;A=uvpoint(1240,600,z);B=uvpoint(1460,653,z);axis=B-A;side=Vector((-axis.y,axis.x,0)).normalized();width=1.50
def beam(n,a,b,w,h,material):
 delta=b-a;o=box(n,(0,0,0),(w,h,delta.length),material,root);o.location=(a+b)/2;o.rotation_euler=delta.to_track_quat('Z','Y').to_euler();return o
def pt(t,off=0,zvalue=None):
 p=A+axis*t+side*off
 if zvalue is not None:p.z=zvalue
 return p
land=s.objects['SF_FRONT_LAND'];LI=land.matrix_world.inverted();down=(LI.to_3x3()@DM.to_3x3()@Vector((0,0,-1))).normalized()
def polyof(o):return [Vector(tuple(o['footprint'][j:j+2]))for j in range(0,8,2)]
def overlaps(a,b,gap=.08):
 for poly in (a,b):
  for j,p in enumerate(poly):
   e=poly[(j+1)%len(poly)]-p;axis=Vector((-e.y,e.x)).normalized();aa=[p.dot(axis)for p in a];bb=[p.dot(axis)for p in b]
   if max(aa)+gap<min(bb)or max(bb)+gap<min(aa):return False
 return True
def landok(poly):
 return all(land.ray_cast(LI@(DM@Vector((p.x,p.y,4))),down)[0]for p in poly+[(poly[j]+poly[(j+1)%len(poly)])/2 for j in range(len(poly))])
courtyard=[Vector(tuple(pt(tt,off)[:2]))for tt,off in [(-.02,-.35),(.52,-.35),(.52,width+.35),(-.02,width+.35)]]
houses=[o for o in s.objects if o.get('na_district_owner')and 'footprint'in o]
protected=[]
for name in ['DT_LEFT','DT_LEFT_REAR','DT_CENTER','DT_FACADE','DT_RIGHT','DT_PAVILION','DT_TRADITIONAL','DT_TRADITIONAL_REAR']:
 o=s.objects.get(name)
 if not o:continue
 vs=[DI@ch.matrix_world@Vector(v)for ch in o.children_recursive if ch.type=='MESH'for v in ch.bound_box]
 if vs:
  x0,x1=min(v.x for v in vs)-.1,max(v.x for v in vs)+.1;y0,y1=min(v.y for v in vs)-.1,max(v.y for v in vs)+.1;protected.append([Vector(p)for p in [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]])
relocated=[]
for o in houses:
 old=polyof(o)
 if not overlaps(old,courtyard):continue
 choices=sorted([(x*.25,y*.25)for x in range(-24,25)for y in range(-24,25)],key=lambda p:p[0]**2+p[1]**2)
 for dx,dy in choices:
  new=[p+Vector((dx,dy))for p in old]
  if min(p.y for p in new)<2.6 or not landok(new)or overlaps(new,courtyard):continue
  if any(overlaps(new,polyof(q))for q in houses if q!=o)or any(overlaps(new,p)for p in protected):continue
  before=list(o.location);o.location.x+=dx;o.location.y+=dy;o['footprint']=[v for p in new for v in p];relocated.append({'name':o.name,'before':before,'after':list(o.location),'delta':[dx,dy]});break
 else:raise RuntimeError('Cannot clear crane courtyard: '+o.name)
tree_moves=[]
for o in s.objects:
 if o.name.startswith('NA_TREE')and o.type=='EMPTY':
  x,y=o.location[:2];square=[Vector(p)for p in [(x-.35,y-.35),(x+.35,y-.35),(x+.35,y+.35),(x-.35,y+.35)]]
  if not overlaps(square,courtyard)and not any(overlaps(square,polyof(q),0)for q in houses):continue
  for dx,dy in sorted([(a*.3,b*.3)for a in range(-14,15)for b in range(-14,15)],key=lambda p:p[0]**2+p[1]**2):
   new=[p+Vector((dx,dy))for p in square]
   if landok(new)and not overlaps(new,courtyard)and not any(overlaps(new,polyof(q))for q in houses)and not any(overlaps(new,p)for p in protected):
    o.location.x+=dx;o.location.y+=dy;tree_moves.append({'name':o.name,'delta':[dx,dy]});break
supports=[]
for i,t0 in enumerate([.08,.42]):
 for j,off in enumerate([0,width]):
  p=pt(t0,off,1.25);supports.append(list(p));assert land.ray_cast(LI@(DM@(p+Vector((0,0,2)))),down)[0]
  box(f'CR_FOOT_{i}{j}',(p.x,p.y,1.33),(.42,.54,.16),M['blue'],root)
  box(f'CR_LEG_{i}{j}',(p.x,p.y,(1.41+z)/2),(.24,.28,z-1.41),M['white'],root)
  # Blue rail bogie plinths with small wheel pairs.
  for dx in [-.13,.13]:sphere('CR_BOGIE_WHEEL',(p.x+dx,p.y,1.35),.09,M['roof'],root)
for off in [0,width]:
 beam('CR_HORIZONTAL_BOOM',pt(-.04,off),pt(1.02,off),.25,.32,M['blue'])
 # Narrow top rail and repeated structure make the member read as a beam.
 tube('CR_TROLLEY_RAIL',[tuple(pt(-.02,off)+Vector((0,0,.18))),tuple(pt(1,off)+Vector((0,0,.18)))],.035,M['silver'],root)
for tt in [-.04,.08,.42,1.02]:beam('CR_CROSS_MEMBER',pt(tt),pt(tt,width),.22,.25,M['blue'])
for off in [0,width]:
 # X bracing stays inside the ground-supported portal.
 beam('CR_PORTAL_BRACE',pt(.08,off,1.6),pt(.42,off,4.7),.10,.12,M['blue'])
 beam('CR_PORTAL_BRACE',pt(.42,off,1.6),pt(.08,off,4.7),.10,.12,M['blue'])
 beam('CR_PORTAL_TIE',pt(.08,off,2.6),pt(.42,off,2.6),.15,.15,M['blue'])
for tt in [.08,.42]:beam('CR_LOWER_CROSS',pt(tt,0,2.6),pt(tt,width,2.6),.16,.18,M['blue'])
peak=pt(.26,width*.5,8.1)
for off in [0,width]:
 beam('CR_PYLON',pt(.26,off),peak,.15,.16,M['blue'])
 for tt in [-.04,1.02]:beam('CR_STAY',peak,pt(tt,off),.085,.09,M['blue'])
# Side truss braces follow the short, horizontal boom.
for off in [0,width]:
 for j in range(6):
  p=pt(j/6,off)+Vector((0,0,.20));q=pt((j+1)/6,off)+Vector((0,0,-.06));beam('CR_BOOM_WEB',p,q,.035,.035,M['white'])
# Machinery and small operator cabin.
p=pt(.10,width*.5,z+.25);box('CR_MACHINERY',p,(.75,.55,.35),M['white'],root)
p=pt(.40,width*.5,z-.46);box('CR_CAB',p,(.58,.55,.60),M['white'],root);box('CR_CAB_GLASS',p+Vector((.30,0,.07)),(.025,.45,.32),M['navy'],root)
# Static inspection hook at the reference pose. It is explicitly separate from
# the original preserved animated spreader, pending S1 motion authorization.
p=pt(.72,width*.5,z-.22);box('CR_REVIEW_TROLLEY',p,(.65,.55,.22),M['blue'],root)
for off in [-.18,.18]:tube('CR_REVIEW_HOIST',[(p.x+off,p.y,p.z-.1),(p.x+off,p.y,3.0)],.018,M['roof'],root)
box('CR_REVIEW_HOOK_BLOCK',(p.x,p.y,3.0),(.32,.28,.44),M['gold'],root)
hook=[]
for j in range(22):
 a=math.pi*.1+j/21*math.pi*1.6;hook.append((p.x+.15*math.cos(a),p.y,2.68+.15*math.sin(a)))
tube('CR_REVIEW_HOOK',hook,.045,M['gold'],root)
# Measure legacy hoist incompatibility; do not alter protected actor actions.
conflict=[]
for f in [0,24,48,72,96,124,156]:
 s.frame_set(f);q=DI@s.objects['P01_SPREADER'].matrix_world.translation
 conflict.append({'frame':f,'original_spreader_z':q.z,'new_beam_underside':z-.16,'clearance':z-.16-(q.z+.09)})
s.frame_set(156);bpy.context.view_layer.update()
scene_issues=[]
for p in supports:
 for o in s.objects:
  if o.get('na_district_owner')and 'footprint'in o:
   pts=[Vector(tuple(o['footprint'][j:j+2]))for j in range(0,8,2)];v=Vector(p[:2]);signs=[]
   for i,a in enumerate(pts):
    b=pts[(i+1)%4];signs.append((b.x-a.x)*(v.y-a.y)-(b.y-a.y)*(v.x-a.x))
   if all(x>=0 for x in signs)or all(x<=0 for x in signs):scene_issues.append({'support':p,'building':o.name})
report={'file':str(out),'source':bpy.data.filepath,'type':'static crane design proposal, not animation-ready','supports':supports,'beam_endpoints':[list(A),list(B)],'height':{'base':1.25,'beam':z,'pylon':8.1},'hidden_original_crane_visuals':hidden,'original_spreader_clearance':conflict,'support_building_overlaps':scene_issues,'relocated_houses':relocated,'relocated_trees':tree_moves,'protected_actions_changed':False,'approval_needed':'Retarget S1 crane/hoist and any affected initial suspended-container height while preserving landing frame and later voyage.'}
(R/f'review/crane-style-proposal-{version}.json').write_text(json.dumps(report,indent=2))
s['crane_v018_status']='STATIC STYLE PROPOSAL ONLY: S1 hoist retarget pending'
bpy.ops.wm.save_as_mainfile(filepath=str(out));print(json.dumps(report))
