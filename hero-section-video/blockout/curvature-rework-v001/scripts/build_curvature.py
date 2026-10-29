"""Rigid architecture on spherical terrain, with graded logistics and preserved actions."""
import bpy,bmesh,sys,math,json,hashlib,argparse,re,numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from mapping import surface,normal,rigid_at,graded,road_frame,WAREHOUSE,CENTER,smooth
p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
out=Path(a.output).resolve();source=R/'inputs/warehouse-v008.blend'
assert out.is_relative_to(R) and not out.is_relative_to(R/'inputs') and not out.exists()
assert hashlib.sha256(source.read_bytes()).hexdigest()=='98b171ca73e85b535ce6a9c7953eb0b686143715878919ba40ff5d7524f5bccd'
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;s.frame_set(1075);U=s.objects['US_FRAME'];UM=U.matrix_world.copy();UI=UM.inverted()
col=bpy.data.collections.new('CURVED_US_TERRAIN');s.collection.children.link(col)
old={o.name:o.matrix_world.copy() for o in s.objects};modified=set();removed=[];new=[];assigned=set();groups=[]
def points(o):
 if o.type=='MESH':return [UI@old[o.name]@v.co for v in o.data.vertices]
 if o.type=='CURVE':return [UI@old[o.name]@Vector(p.co[:3]) for sp in o.data.splines for p in sp.points]
 return [UI@old[o.name].translation]
def midpoint(o):
 v=points(o);return Vector([(min(p[k] for p in v)+max(p[k] for p in v))/2 for k in range(3)])
def hull(pts):
 ps=sorted(set((round(p[0],6),round(p[1],6)) for p in pts))
 def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
 halves=[]
 for seq in [ps,list(reversed(ps))]:
  h=[]
  for p in seq:
   while len(h)>1 and cross(h[-2],h[-1],p)<=0:h.pop()
   h.append(p)
  halves.append(h[:-1])
 return halves[0]+halves[1]
def empty(name,parent,matrix):
 o=bpy.data.objects.new(name,None);col.objects.link(o);o.parent=parent;o.matrix_basis=matrix;o['cv_owner']='curvature-v001';new.append(o.name);return o
def descendants(o):
 result={o}
 for c in o.children:result|=descendants(c)
 return result
def wrap(name,members,T,anchor=None):
 members=set(members);assert not (assigned&{o.name for o in members}),(name,'double assignment')
 roots=[o for o in members if o.parent not in members];frames={};Tw=UM@T@UI
 for o in roots:
  parent=o.parent;key=parent.name if parent else 'WORLD'
  if key not in frames:
   P=old[parent.name] if parent else Matrix.Identity(4)
   frame=empty('CV_'+name+'_'+key,parent,P.inverted()@Tw@P);frames[key]=frame
   if anchor is not None:frame['cv_anchor']=list(anchor)
  basis=o.matrix_basis.copy();inverse=o.matrix_parent_inverse.copy();o.parent=frames[key];o.matrix_parent_inverse=inverse;o.matrix_basis=basis;modified.add(o.name)
 assigned.update(o.name for o in members);groups.append({'name':name,'members':sorted(o.name for o in members),'anchor':list(anchor) if anchor is not None else None,'matrix_us':list(map(list,T))})
 return frames
def sheet(poly):
 bm=bmesh.new();vs=[bm.verts.new((x,y,0)) for x,y in poly];bm.faces.new(vs);bmesh.ops.triangulate(bm,faces=list(bm.faces))
 for _ in range(9):
  edges=[e for e in bm.edges if e.calc_length()>1.7]
  if not edges:break
  bmesh.ops.subdivide_edges(bm,edges=edges,cuts=1,use_grid_fill=True)
 bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.verts.ensure_lookup_table();bm.verts.index_update()
 pts=[(v.co.x,v.co.y) for v in bm.verts];faces=[tuple(v.index for v in f.verts) for f in bm.faces];boundary=[tuple(v.index for v in e.verts) for e in bm.edges if e.is_boundary];bm.free();return pts,faces,boundary
def solid_patch(name,poly,top_fn,bottom_fn,mat,existing=None):
 pts,faces,edges=sheet(poly);n=len(pts);top=[top_fn(x,y) for x,y in pts];bottom=[bottom_fn(p) for p in top]
 verts=top+bottom;allfaces=faces+[tuple(n+i for i in reversed(f)) for f in faces]+[(a,b,n+b,n+a) for a,b in edges]
 mesh=bpy.data.meshes.new('CV_'+name+'_MESH');mesh.from_pydata(verts,[],allfaces);mesh.materials.append(mat);mesh.update()
 if existing:o=existing;o.data=mesh;o.parent=U;o.matrix_parent_inverse=Matrix.Identity(4);o.matrix_basis=Matrix.Identity(4);modified.add(o.name)
 else:o=bpy.data.objects.new(name,mesh);col.objects.link(o);o.parent=U;new.append(o.name)
 o['cv_owner']='curvature-v001';o['cv_role']='terrain' if existing else 'foundation'
 for f in o.data.polygons:f.use_smooth=False
 return o
def radial_bottom(p,height=.66):return CENTER+(Vector(p)-CENTER).normalized()*(140+height)
def foundation(name,poly,z,T):
 mat=bpy.data.materials.get('UC_LIMESTONE') or s.objects['US_LAND_TERRACE'].data.materials[0]
 return solid_patch('CV_FOUNDATION_'+name,poly,lambda x,y:T@Vector((x,y,z)),lambda p:radial_bottom(p),mat)
def rigid_group(name,members,base=None,height=.8,podium=True,foot=None):
 members=set(members);allpts=[p for o in members if o.type=='MESH' for p in points(o)]
 if base is None:
  z=min(v.z for v in allpts);basepts=[v for v in allpts if v.z<z+.025];poly=hull(basepts)
  base=Vector((sum(p[0] for p in poly)/len(poly),sum(p[1] for p in poly)/len(poly),z))
 else:
  base=Vector(base);poly=foot or hull([v for v in allpts if abs(v.z-base.z)<.04])
 T=rigid_at(base,height);wrap(name,members,T,base)
 if podium and len(poly)>=3:foundation(name,poly,base.z,T)
 return T
def remove(name):
 o=s.objects.get(name)
 if o:removed.append(name);bpy.data.objects.remove(o,do_unlink=True)

# Capture only source roots needed for spatial frames; all original actions remain intact.
tracks={n:[] for n in ['A03_TRAILER','A04_PRIMARY','A05_SECONDARY','CAM_LOOK_TARGET']}
contacts={n:[] for n in ['A03_TRAILER','A04_PRIMARY','A05_SECONDARY']}
for f in range(1,1393):
 s.frame_set(f)
 for n in tracks:tracks[n].append(UI@s.objects[n].matrix_world.translation)
 for n in contacts:
  roots=[s.objects[n]]+([s.objects['A03_TRACTOR']] if n=='A03_TRAILER' else [])
  pp=[UI@o.matrix_world.translation for root in roots for o in root.children if 'WHEEL' in o.name]
  contacts[n].append([Vector((v.x,v.y,.735)) for v in pp])
s.frame_set(1075)

# Main land becomes a thin sphere-conforming skin, covering existing city footprints.
outline=[]
for name in ['US_LAND_TERRACE','UC_AR_CITY_FOUNDATION','UC_AR_FRONT_STREET_TERRACE','UC_CIVIC_PLAZA']:
 ps=points(s.objects[name]);z=max(v.z for v in ps);outline.extend(v for v in ps if v.z>z-.025)
land=s.objects['US_LAND_TERRACE'];poly=hull(outline)
solid_patch('US_LAND_TERRACE',poly,lambda x,y:surface(x,y,.68),lambda p:radial_bottom(p,-.1),land.data.materials[0],land);assigned.add(land.name)
for n in ['UC_AR_CITY_FOUNDATION','UC_AR_CIVIC_FOUNDATION','UC_AR_CIVIC_LOWER_TERRACE','UC_AR_FRONT_STREET_TERRACE']:remove(n)

# Architecture is transformed as complete rigid assemblies, including facade/roof details.
for o in list(s.objects):
 if re.fullmatch(r'UC_BLOCK_\d\d_\d\d',o.name):
  members=[q for q in s.objects if q.name==o.name or q.name.startswith(o.name+'_') or q.get('ar_source_block')==o.name]
  body=points(o);z=min(v.z for v in body);bottom=[v for v in body if v.z<z+.002]
  base=sum(bottom,Vector())/len(bottom)
  rigid_group(o.name,members,base)
rigid_group('CENTRAL_TOWER',[o for o in s.objects if o.name.startswith('UC_CENTRAL')])
rigid_group('GLASS_TOWER',[o for o in s.objects if o.name.startswith(('UC_GLASS_SPIRE','UC_AR_GLASS'))])
rigid_group('CIVIC',descendants(s.objects['UC_AR_CIVIC_GROUP']))
for ch in 'USA':rigid_group('LETTER_'+ch,[s.objects['UC_LETTER_'+ch],s.objects['UC_AR_LETTER_PLINTH_'+ch]])
lib=s.objects['UC_LIBERTY'];cap=s.objects['UC_LIBERTY_ISLAND_CAP'];ps=points(cap);base=midpoint(cap);base.z=max(v.z for v in ps)
rigid_group('LIBERTY',descendants(lib),base,.4,False)
rigid_group('BRIDGE',[o for o in s.objects if o.name.startswith('UC_BRIDGE')],(28,0,0),0,False)
cranes=[o for o in s.objects if o.name.startswith('UC_STATIC_CRANE_TOP')];centers=[midpoint(o) for o in cranes]
for i,c in enumerate(centers):
 members=[o for o in s.objects if o.name.startswith('UC_STATIC_CRANE') and min(range(len(centers)),key=lambda k:(midpoint(o).xy-centers[k].xy).length)==i]
 rigid_group('CRANE_'+str(i),members)
containers=[o for o in s.objects if re.fullmatch(r'UC_CONTAINER(?:\.\d+)?',o.name)];centers=sorted(set((round(midpoint(o).x,3),round(midpoint(o).y,3)) for o in containers))
for i,c in enumerate(centers):
 members=[o for o in s.objects if o.name.startswith('UC_CONTAINER') and min(range(len(centers)),key=lambda k:(midpoint(o).xy-Vector(centers[k])).length)==i]
 rigid_group('STACK_'+str(i),members)
for prefix in ['UC_RAIL_WAGON','UC_TAXI']:
 for o in [q for q in s.objects if re.fullmatch(prefix+r'(?:\.\d+)?',q.name)]:
  suffix=o.name[len(prefix):];companion=('UC_RAIL_LOAD' if prefix=='UC_RAIL_WAGON' else 'UC_TAXI_GLASS')+suffix
  rigid_group(o.name,[o]+([s.objects[companion]] if companion in s.objects else []))
for o in list(s.objects):
 if o.name.startswith(('UC_TREE_TRUNK','UC_SHORE_TREE_TRUNK')) and o.name not in assigned:
  c=midpoint(o);members=[o]
  prefixes=['UC_TREE_CROWN'] if o.name.startswith('UC_TREE_TRUNK') else ['UC_PALM_FROND','UC_SHORE_HILL']
  for q in s.objects:
   if q.name not in assigned and q.name.startswith(tuple(prefixes)) and (midpoint(q).xy-c.xy).length<3.5:members.append(q)
  rigid_group(o.name,members,Vector((c.x,c.y,.68)),.8,False)
for o in list(s.objects):
 if o.name.startswith('UC_STAR'):
  c=midpoint(o);rigid_group(o.name,[o],(c.x,c.y,.68),.8,False)
 if o.name.startswith(('E12_DESTINATION','US_YARD_STACK')):rigid_group(o.name,[o])

# Work-floor contents share a single tangent frame, so their relative contacts remain exact.
wh=set()
for o in s.objects:
 if o.name in assigned:continue
 if o.name.startswith(('WH_','WAREHOUSE_','W0','CH_','TABLE_LEG_','PACK_BOX_','LAST_BOX_','UC_WAREHOUSE')) or o.name in ['E08_WAREHOUSE','DOCK_TARGET','DOCK_BRIDGE','E10_OUTBOUND_YARD','E10_LOADING_BRIDGE']:
  wh|=descendants(o)
# Carrier-owned descendants must never also inherit the warehouse frame.
# Remaining cartons already live inside A01_CONTAINER, including their pallet.
for n in ['A01_CONTAINER','A03_TRAILER','A03_TRACTOR','A04_PRIMARY','A05_SECONDARY','W01_NEW_PALLET','W08_LAST_LOAD']:wh-=descendants(s.objects[n])
wrap('WH',wh,WAREHOUSE,(52,32,.68))
foundation('WAREHOUSE',[(29,22.9),(82,22.9),(82,39.4),(29,39.4)],.679,WAREHOUSE)

def warp(o,fn):
 modified.add(o.name);assigned.add(o.name);m=UI@old[o.name]
 if o.type=='MESH':
  bm=bmesh.new();bm.from_mesh(o.data)
  for v in bm.verts:v.co=m@v.co
  bmesh.ops.triangulate(bm,faces=list(bm.faces))
  for _ in range(8):
   edges=[e for e in bm.edges if e.calc_length()>1.5]
   if not edges:break
   bmesh.ops.subdivide_edges(bm,edges=edges,cuts=1,use_grid_fill=True)
  bmesh.ops.triangulate(bm,faces=list(bm.faces))
  for v in bm.verts:v.co=fn(v.co)
  data=o.data.copy();bm.to_mesh(data);bm.free();o.data=data
 elif o.type=='CURVE':
  data=o.data.copy();samples=[]
  for sp in data.splines:
   pp=[m@Vector(p.co[:3]) for p in sp.points];out=[]
   for a,b in zip(pp,pp[1:]):
    count=max(1,math.ceil((b-a).length));out.extend(fn(a.lerp(b,i/count)) for i in range(count))
   out.append(fn(pp[-1]));samples.append((out,sp.use_cyclic_u))
  data.splines.clear()
  for pp,cyclic in samples:
   sp=data.splines.new('POLY');sp.points.add(len(pp)-1);sp.use_cyclic_u=cyclic
   for p,v in zip(sp.points,pp):p.co=(*v,1)
  o.data=data
 else:raise AssertionError(o.name)
 o.parent=U;o.matrix_parent_inverse=Matrix.Identity(4);o.matrix_basis=Matrix.Identity(4);o['cv_role']='surface'
for o in list(s.objects):
 if o.name in ['E07_INBOUND_ROAD','E11_ROUTE_1','E11_ROUTE_-1','A05_WAIT_MERGE']:
  # Source ribbons have paired vertices; add shoulder clearance for rigid wheel paths.
  o.data=o.data.copy();vv=o.data.vertices
  for i in range(0,len(vv)-1,2):
   a,b=vv[i].co.copy(),vv[i+1].co.copy();delta=(a-b).normalized()*.8;vv[i].co+=delta;vv[i+1].co-=delta
  if o.name.startswith('E11_ROUTE'):
   for i,j in [(0,2),(1,3),(len(vv)-2,len(vv)-4),(len(vv)-1,len(vv)-3)]:
    vv[i].co+=(vv[i].co-vv[j].co).normalized()*3.2
 if o.name.startswith(('E07_','E11_','A05_WAIT_MERGE','E09_MANEUVER','US_YARD_ROAD')):warp(o,graded)
 elif o.name.startswith(('UC_CITY_STREET','UC_CITY_AVENUE','UC_RAIL_SLEEPER')) or o.name in ['UC_RAIL','UC_RAIL.001']:warp(o,lambda p:surface(p.x,p.y,p.z+.12))

# Short supporting road embankments meet the actual spherical ground.
for name in ['E07_INBOUND_ROAD','E11_ROUTE_1','E11_ROUTE_-1','A05_WAIT_MERGE','E09_MANEUVER_YARD','US_YARD_ROAD']:
 o=s.objects[name];data=o.data;bm=bmesh.new();bm.from_mesh(data);bm.verts.ensure_lookup_table();bm.verts.index_update()
 edges=[tuple(v.index for v in e.verts) for e in bm.edges if e.is_boundary];vs=[v.co.copy() for v in bm.verts];n=len(vs)
 faces=[tuple(v.index for v in f.verts) for f in bm.faces];bm.free()
 if edges:
  mesh=bpy.data.meshes.new('CV_SUPPORT_'+name);mesh.from_pydata(vs+[radial_bottom(p) for p in vs],[],[(b,a,n+a,n+b) for a,b in edges]+[tuple(n+i for i in reversed(f)) for f in faces]);mesh.materials.append(land.data.materials[0]);mesh.update()
  support=bpy.data.objects.new('CV_SUPPORT_'+name,mesh);col.objects.link(support);support.parent=U;new.append(support.name)
solid_patch('CV_SUPPORT_MANEUVER',[(15,26),(39,26),(39,32),(15,32)],lambda x,y:graded(Vector((x,y,.68))),lambda p:radial_bottom(p),land.data.materials[0])
foundation('PORT',[(-17.2,4),(17.2,4),(17.2,12.4),(-17.2,12.4)],.4,Matrix.Identity(4))

# Variable parent frames deform trajectories as rigid vehicles, retaining every source action.
variable=[]
for group,roots,key in [('CARRIER',['A03_TRAILER','A03_TRACTOR','A01_CONTAINER','W01_NEW_PALLET'],'A03_TRAILER'),('PRIMARY',['A04_PRIMARY','W08_LAST_LOAD'],'A04_PRIMARY'),('SECONDARY',['A05_SECONDARY'],'A05_SECONDARY'),('CAMERA',['CAM_MASTER','CAM_LOOK_TARGET'],'CAM_LOOK_TARGET')]:
 frame=empty('CV_'+group+'_WORLD',None,Matrix.Identity(4));frame.rotation_mode='QUATERNION';variable.append((group,frame,key))
 for n in roots:
  o=s.objects[n];assert o.parent is None,n;basis=o.matrix_basis.copy();o.parent=frame;o.matrix_parent_inverse=Matrix.Identity(4);o.matrix_basis=basis;modified.add(n);assigned.update(q.name for q in descendants(o))
last={}
def contact_frame(pp):
 # A rigid least-squares fit to all tire contact points supports the entire wheelbase.
 aa=np.array([tuple(p) for p in pp]);bb=np.array([tuple(graded(p)) for p in pp]);ac=aa.mean(axis=0);bc=bb.mean(axis=0)
 u,_,vt=np.linalg.svd((aa-ac).T@(bb-bc));rot=vt.T@u.T
 if np.linalg.det(rot)<0:vt[-1,:]*=-1;rot=vt.T@u.T
 T=Matrix(rot.tolist()).to_4x4();T.translation=Vector(bc-rot@ac);return T
for f in range(1,1393):
 for group,frame,key in variable:
  pt=tracks[key][f-1];T=contact_frame(contacts[key][f-1]) if key in contacts else road_frame(pt)
  if group=='CAMERA':
   # Fade only the new regional frame during the US reveal; early China/voyage untouched.
   weight=smooth(f,380,430)
   loc=T.translation*weight;q=Matrix.Identity(3).to_quaternion().slerp(T.to_quaternion(),weight);T=Matrix.LocRotScale(loc,q,Vector((1,1,1)))
  Tw=Matrix.Identity(4) if group=='CAMERA' and f<=380 else UM@T@UI;frame.location=Tw.translation;frame.rotation_quaternion=Tw.to_quaternion()
  if group in last and frame.rotation_quaternion.dot(last[group])<0:frame.rotation_quaternion.negate()
  last[group]=frame.rotation_quaternion.copy()
  frame.keyframe_insert('location',frame=f);frame.keyframe_insert('rotation_quaternion',frame=f)
for _,o,_ in variable:
 for layer in o.animation_data.action.layers:
  for strip in layer.strips:
   for bag in strip.channelbags:
    for fc in bag.fcurves:
     for k in fc.keyframe_points:k.interpolation='LINEAR'
# All visible authored US pieces must belong to an explicit transformed group/surface.
unassigned=[o.name for o in s.objects if o.name.startswith('UC_') and o.name not in assigned and o.name not in removed and o.type in ['MESH','CURVE','FONT'] and not o.hide_render]
assert not unassigned,unassigned
s['curvature_revision']='curvature-v001';s.frame_set(1075);bpy.ops.wm.save_as_mainfile(filepath=str(out))
report={'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'candidate_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'modified':sorted(modified),'removed':removed,'new':new,'groups':groups,'radius':140,'land_top_radius':140.68,'warehouse_matrix_us':list(map(list,WAREHOUSE)),'source_actions_preserved':True,'frame_wrappers':[o.name for _,o,_ in variable]}
(R/'review'/f'{out.stem}-build.json').write_text(json.dumps(report,indent=2));print('BUILT',out,'groups',len(groups),'modified',len(modified),'new',len(new))
