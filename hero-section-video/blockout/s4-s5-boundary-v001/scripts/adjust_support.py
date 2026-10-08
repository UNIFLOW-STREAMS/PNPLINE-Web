"""Approved local height/pitch correction; no XY route, timing or geometry edits."""
import bpy,math
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree

def apply(s,cfg,curves,smooth):
 U=bpy.data.objects['US_FRAME'].matrix_world.copy();I=U.inverted();up=U.to_3x3()@Vector((0,0,1));ground=[]
 for name in ['US_QUAY','US_LAND_TERRACE','E07_INBOUND_ROAD','E09_MANEUVER_YARD']:
  o=bpy.data.objects[name];ground.append(BVHTree.FromPolygons([I@o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons]))
 roots=['A03_TRACTOR','A03_TRAILER','A01_CONTAINER','W01_NEW_PALLET'];hoist=['P02_SPREADER']+[f'P02_CABLE_{i}' for i in range(4)];start,end=cfg['support_start'],cfg['support_end'];samples={n:[] for n in roots+hoist};wheels=[o for o in s.objects if o.name.startswith('A03') and '_WHEEL_' in o.name];max_pitch=0
 for j in range(start*4+1,end*4):
  f=j/4;s.frame_set(math.floor(f),subframe=f%1);pivot=(I@bpy.data.objects['A03_TRAILER'].matrix_world).translation
  wheelverts=[[I@o.matrix_world@v.co for v in o.data.vertices] for o in wheels];centers=[(I@o.matrix_world).translation for o in wheels]
  best=None
  for k in range(81):
   angle=k*.001;rot=Matrix.Rotation(angle,4,'Y');needs=[]
   for vs,center in zip(wheelverts,centers):
    cc=pivot+rot@(center-pivot);hits=[tr.ray_cast(cc+Vector((0,0,3)),Vector((0,0,-1)),10)[0] for tr in ground];height=max(h.z for h in hits if h is not None);bottom=min((pivot+rot@(v-pivot)).z for v in vs);needs.append(height-bottom)
   low,high=min(needs),max(needs);candidate=((high-low)/2,angle,(high+low)/2)
   if best is None or candidate[0]<best[0]-1e-7:best=candidate
  _,angle,z=best;weight=smooth((f-start)/12)*(1-smooth((f-712)/8));angle*=weight;z*=weight;max_pitch=max(max_pitch,math.degrees(angle));D=U@Matrix.Translation(Vector((0,0,z)))@Matrix.Translation(pivot)@Matrix.Rotation(angle,4,'Y')@Matrix.Translation(-pivot)@I
  for name in roots:
   o=bpy.data.objects[name]
   if name in ['A01_CONTAINER','W01_NEW_PALLET'] and f<632:m=Matrix.Translation(up*(.2*smooth((f-start)/(632-start))))@o.matrix_world
   else:
    original=o.matrix_world.copy()
    if name=='A03_TRACTOR':original.translation+=bpy.data.objects['TRAILER_HITCH'].matrix_world.translation-bpy.data.objects['TRACTOR_HITCH'].matrix_world.translation
    m=D@original
   q=m.to_quaternion()
   if q.dot(o.rotation_quaternion)<0:q.negate()
   samples[name].append((f,m.translation.copy(),q,o.scale.copy()))
  if f<666:
   dz=.2*smooth((f-start)/(632-start))*(1-smooth((f-637)/29))
   for name in hoist:
    o=bpy.data.objects[name];m=o.matrix_world.copy();sc=o.scale.copy()
    if name=='P02_SPREADER':m.translation+=up*dz
    else:
     length=(o.matrix_world.to_3x3()@Vector((0,0,max(v[2] for v in o.bound_box)-min(v[2] for v in o.bound_box)))).length
     m.translation+=up*(dz/2);sc.z*=max(.001,(length-dz)/length)
    q=m.to_quaternion()
    samples[name].append((f,m.translation.copy(),q,sc))
 for name,rows in samples.items():
  o=bpy.data.objects[name];finish=end if name in roots else 666;protected=[]
  for fc in curves(o):
   protected.append((fc,{float(k.co.x):(tuple(k.handle_left),tuple(k.handle_right)) for k in fc.keyframe_points if k.co.x<=start or k.co.x>=finish}))
   for key in list(fc.keyframe_points):
    if start<key.co.x<finish:fc.keyframe_points.remove(key,fast=True)
   fc.update()
  for f,pos,q,scale in rows:
   o.location=pos;o.scale=scale
   if o.rotation_mode=='QUATERNION':
    o.rotation_quaternion=q;o.keyframe_insert('rotation_quaternion',frame=f)
   else:
    o.rotation_euler=q.to_euler(o.rotation_mode,o.rotation_euler);o.keyframe_insert('rotation_euler',frame=f)
   o.keyframe_insert('location',frame=f)
   if 'CABLE' in name:o.keyframe_insert('scale',frame=f)
  for fc in curves(o):
   for key in fc.keyframe_points:
    if start<key.co.x<finish:key.interpolation='LINEAR'
  for fc,keys in protected:
   for key in fc.keyframe_points:
    if float(key.co.x) in keys:key.handle_left,key.handle_right=keys[float(key.co.x)]
 print('SUPPORT_MAX_PITCH_DEG',max_pitch)
