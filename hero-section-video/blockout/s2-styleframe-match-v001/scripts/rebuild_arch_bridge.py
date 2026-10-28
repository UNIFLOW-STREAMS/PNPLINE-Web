"""Open the bridge forebay and replace the thin proxy bridge with stone arch geometry."""
import bpy,math,json,sys,ast
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;s.frame_set(156);out=Path(sys.argv[sys.argv.index('--')+1]);assert not out.exists()
D=s.objects['SF_CN_LAYOUT'];DM=D.matrix_world.copy();DI=DM.inverted();center=Vector((-5,23));N=512
col=bpy.data.collections.new('WATERFRONT_ARCH_BRIDGE');s.collection.children.link(col)
def tag(o):o['bridge_revision_owner']='bridge-v029';return o
tree=ast.parse((R/'scripts/build_layout_proposal.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in {'empty','mesh','box','tube','uvpoint'}],type_ignores=[]),'<bridge geometry>','exec'))
tree=ast.parse((R/'scripts/trace_s_basin.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in {'periodic_bspline','cross','intersect','update_mesh','ring3'}],type_ignores=[]),'<bank geometry>','exec'))
M={k:bpy.data.materials['SF_'+k]for k in ['stone','cream','white','water']}
old=s.objects['SF_ARCH_BRIDGE'];hidden=[]
for o in old.children_recursive:o.hide_render=True;o.hide_set(True);hidden.append(o.name)
# The enlarged left forebay lies below the bridge, behind the pavilion and
# beside the domed building. Both bridge abutments remain on opposite banks.
controls=[(479,583),(476,630),(490,672),(510,706),(535,741),(577,766),(615,765),(640,744),(646,710),(680,700),(750,710),(900,711),(1040,694),(1150,660),(1230,634),(1320,610),(1380,580),(1370,550),(1310,524),(1260,522),(1100,502),(1010,505),(800,503),(620,520),(520,545)]
raw=periodic_bspline(controls);outer=[intersect(raw,math.tau*i/N)for i in range(N)]
water=s.objects['SF_BASIN_WATER_SURFACE'];inner=[v.co.copy()for v in list(water.data.vertices)[N:]]
land=s.objects['SF_FRONT_LAND'];coast=[v.co.copy()for v in list(land.data.vertices)[:N]]
quads=[(i,(i+1)%N,N+(i+1)%N,N+i)for i in range(N)]
update_mesh('SF_BASIN_WATER_SURFACE',ring3(outer,.92)+ring3(inner,.92),quads)
update_mesh('SF_FRONT_LAND',ring3(coast,1.25)+ring3(outer,1.25),quads)
update_mesh('SF_BASIN_OUTER_WALL',ring3(outer,1.25)+ring3(outer,-.2),quads)
root=empty('WB_STONE_ARCH_BRIDGE',D)
a=uvpoint(486,689);b=uvpoint(665,720);b+=(b-a).normalized()*.7;axis=b-a;u=axis.normalized();side=Vector((-u.y,u.x,0));width=1.05
def deck(t):return 1.35+.95*math.sin(math.pi*t)
def intrados(t):
 q=(t-.5)/.42
 return .94+1.10*math.sqrt(max(0,1-q*q))if abs(q)<1 else .55
def point(t,off,z):
 p=a.lerp(b,t)+side*off;p.z=z;return p
segments=96;vs=[]
for i in range(segments+1):
 t=i/segments
 for off,z in [(-width/2,deck(t)),(width/2,deck(t)),(-width/2,intrados(t)),(width/2,intrados(t))]:vs.append(point(t,off,z))
faces=[]
for i in range(segments):
 j=i*4;k=j+4;faces += [(j,j+1,k+1,k),(j+2,k+2,k+3,j+3),(j,k,k+2,j+2),(j+1,j+3,k+3,k+1)]
faces += [(0,2,3,1),(segments*4,segments*4+1,segments*4+3,segments*4+2)]
bridge=mesh('WB_ARCH_MASONRY',vs,faces,M['stone'],root)
# Radial voussoirs on both faces give the arch its recognizable stone outline.
for sign in [-1,1]:
 for j in range(27):
  t0=.08+.84*(j+.06)/27;t1=.08+.84*(j+.94)/27
  pts=[point(t,sign*(width/2+.008),intrados(t)+z)for t,z in [(t0,0),(t1,0),(t1,.19),(t0,.19)]]
  mesh('WB_ARCH_STONE',pts,[(0,1,2,3)],M['cream'],root)
 # Curb, square posts and rectangular handrails follow the deck continuously.
 for offset,height,depth,name in [(sign*(width/2-.045),.06,.10,'CURB'),(sign*(width/2-.045),.53,.075,'HANDRAIL')]:
  vertices=[]
  for i in range(segments+1):
   t=i/segments
   for off,z in [(offset-.055,deck(t)+height-depth/2),(offset+.055,deck(t)+height-depth/2),(offset-.055,deck(t)+height+depth/2),(offset+.055,deck(t)+height+depth/2)]:vertices.append(point(t,off,z))
  fs=[]
  for i in range(segments):
   j=i*4;k=j+4;fs.extend([(j,j+1,k+1,k),(j+2,k+2,k+3,j+3),(j,k,k+2,j+2),(j+1,j+3,k+3,k+1)])
  mesh('WB_'+name,vertices,fs,M['cream'],root)
 for i in range(17):
  t=i/16;p=point(t,sign*(width/2-.045),deck(t)+.29)
  post=box('WB_BALUSTER',p,(.07,.07,.43),M['stone'],root)
  box('WB_POST_CAP',p+Vector((0,0,.21)),(.115,.115,.075),M['cream'],root)
for i in range(1,40):
 t=i/40;tube('WB_PAVING_JOINT',[point(t,-width*.42,deck(t)+.006),point(t,width*.42,deck(t)+.006)],.006,M['stone'],root)
for t in [0,1]:
 p=point(t,0,.81);box('WB_ABUTMENT',p,(1.1,1.1,.88),M['stone'],root)
bpy.context.view_layer.update()
ver=out.stem.rsplit('-',1)[-1]
(R/f'review/bridge-change-{ver}.json').write_text(json.dumps({'source':bpy.data.filepath,'output':str(out),'hidden_old_bridge':hidden,'bridge_endpoints_local':[list(a),list(b)],'width':width,'deck_crown':deck(.5),'arch_opening_crown':intrados(.5),'water_height':.92,'outer_bank_controls':controls,'scope':'Bridge visual geometry and left outer-basin forebay only; inner island, title, buildings, camera and actions retained'},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(out))
