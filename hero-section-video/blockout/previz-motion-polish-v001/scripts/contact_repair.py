"""Approved continuous road and world-vertical tyre support, baked and editable."""
import bpy,math,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

GROUND=['US_QUAY','US_LAND_TERRACE','E09_MANEUVER_YARD','MP_CONTINUOUS_ROAD']
def curves(o):
 ad=o.animation_data
 return [f for l in ad.action.layers for st in l.strips for b in st.channelbags if b.slot_handle==ad.action_slot.handle for f in b.fcurves]
def repair(s,m):
 U=s.objects['US_FRAME'].matrix_world.copy();I=U.inverted();old=s.objects['E07_INBOUND_ROAD'];verts=[]
 for k in range(0,len(old.data.vertices),2):
  a,b=[I@old.matrix_world@old.data.vertices[k+j].co for j in [0,1]];c=(a+b)/2
  for p in [c+2*(a-c),c+2*(b-c)]:
   z=.7349905
   if p.y<12:z=.8999958+(.7349905-.8999958)*max(0,min(1,(p.x-17)/2))
   if p.y>25.5:z=.7349905+(.7599974-.7349905)*min(1,(p.y-25.5)/.5)
   verts.append((p.x,p.y,z))
 # Insert exact ramp break edges. Interpolating heights on the old sparse
 # road rings leaves a small step at x17/y26 that tyres cannot continuously cross.
 def clip(poly,axis,edge,side):
  result=[]
  for a,b in zip(poly,poly[1:]+poly[:1]):
   ia=side*(a[axis]-edge)>=-1e-9;ib=side*(b[axis]-edge)>=-1e-9
   if ia:result.append(a)
   if ia!=ib:
    t=(edge-a[axis])/(b[axis]-a[axis]);result.append(tuple(a[j]+t*(b[j]-a[j]) for j in range(3)))
  return result
 meshverts=[];faces=[]
 for face in old.data.polygons:
  polys=[[verts[i] for i in face.vertices]]
  for axis,edge in [(0,17),(0,19),(1,25.5),(1,26)]:
   polys=[q for p in polys for side in [-1,1] if len(q:=clip(p,axis,edge,side))>=3]
  for p in polys:
   # Keep only the connecting road. Coplanar overlays on existing quay/yard
   # produce visible z-fighting despite satisfying the geometric contact test.
   p=clip(clip(p,0,17,1),1,26,-1)
   if len(p)<3 or abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(p,p[1:]+p[:1])))<1e-8:continue
   indices=[]
   for x,y,_ in p:
    z=max(.8999958+(.7349905-.8999958)*max(0,min(1,(x-17)/2)),.7349905+(.7599974-.7349905)*max(0,min(1,(y-25.5)/.5)))
    indices.append(len(meshverts));meshverts.append((x,y,z))
   faces.append(indices)
 mesh=bpy.data.meshes.new('MP_CONTINUOUS_ROAD');mesh.from_pydata(meshverts,[],faces);road=bpy.data.objects.new(mesh.name,mesh);s.collection.objects.link(road);road.matrix_world=U
 for mat in old.data.materials:mesh.materials.append(mat)
 old.hide_render=True;old.hide_set(True);road['approval']='User approved S5 road/contact extension; source road preserved'
 ground=[]
 for name in GROUND:
  o=s.objects[name];ground.append(BVHTree.FromPolygons([I@o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons]))
 wheels=[o for o in s.objects if o.name.startswith('A03') and '_WHEEL_' in o.name]
 # Include every parent/channel breakpoint: a uniform grid alone aliases the
 # inherited narrow suspension adjustments at road boundaries.
 lo,hi=m.forward(648),m.forward(900);times=set(np.arange(lo,hi,1/128).tolist()+[hi])
 for o in list(wheels)+[s.objects['A03_TRACTOR'],s.objects['A03_TRAILER']]:
  for fc in curves(o):times.update(float(k.co.x) for k in fc.keyframe_points if lo<=k.co.x<=hi)
 times=sorted(set(float(np.float32(t)) for t in times));rows={o.name:[] for o in wheels};maxcor=0
 for k,t in enumerate(times):
  s.frame_set(int(t),subframe=t%1)
  for o in wheels:
   wm=I@o.matrix_world;c=wm.translation;dz=-1000
   for v in o.data.vertices:
    p=wm@v.co
    if p.z>c.z:continue
    hits=[tree.ray_cast(p+Vector((0,0,5)),Vector((0,0,-1)),20)[0] for tree in ground]
    dz=max(dz,max(h.z for h in hits if h is not None)-p.z)
   # Parent can pitch as well as yaw. Apply the displacement in US vertical,
   # compensating all local axes so the approved world XY trajectory is exact.
   basis=I.to_3x3()@o.parent.matrix_world.to_3x3()@o.matrix_parent_inverse.to_3x3()
   pos=o.location+basis.inverted()@Vector((0,0,dz));rows[o.name].append((t,*pos));maxcor=max(maxcor,abs(dz))
  if k%8000==0:print('CONTACT_BAKE',k,len(times),flush=True)
 for o in wheels:
  oldfc={f.array_index:f for f in curves(o) if f.data_path=='location'}
  for axis in range(3):
   fc=oldfc.get(axis)
   if fc is None:
    o.keyframe_insert(data_path='location',index=axis,frame=0)
    fc=next(f for f in curves(o) if f.data_path=='location' and f.array_index==axis)
   points=[tuple(k.co) for k in fc.keyframe_points if k.co.x<lo or k.co.x>hi]+[(r[0],r[axis+1]) for r in rows[o.name]]
   points.sort();fc.keyframe_points.clear();fc.keyframe_points.add(len(points));fc.keyframe_points.foreach_set('co',np.asarray(points,dtype=np.float32).ravel())
   for p in fc.keyframe_points:p.interpolation='LINEAR'
   # Already strictly sorted/unique float32 times and LINEAR interpolation.
   # fc.update() removes distinct keys closer than Blender's key dedup epsilon;
   # that silently drops parent breakpoints and aliases sharp inherited pitch.
 return {'max_vertical_correction_m':maxcor,'samples':len(times),'road_width_m':5,'road_name':road.name,'mode':'world vertical; preserve wheel XY and rotation; actual lower tyre mesh vertices; 1/128 output frames plus parent breakpoints'}

