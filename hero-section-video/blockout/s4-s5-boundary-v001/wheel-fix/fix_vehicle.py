"""Repair initial support and intersecting truck proxy components from immutable backup."""
import bpy,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
import hashlib
assert Path(bpy.data.filepath).resolve()==(R/'wheel-fix/before-wheel-fix.blend').resolve(), 'Load the immutable pre-fix backup, not the current master'
assert hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()=='cdf33f07e10327c5ab3d1557f9721d37e4aca997108badf960fa5b19ec2cd3c6', 'Unexpected backup revision'
s=bpy.data.scenes['PNPLINE_MASTER_v005'];bpy.context.window.scene=s
sys.path.insert(0,str(R/'scripts'));from revise_boundary import curves
# The truck is stationary through f648. Extend the already grounded f620 pose
# back to f0 so it never rises out of the quay during loading.
s.frame_set(620)
positions={n:bpy.data.objects[n].location.copy() for n in ['A03_TRACTOR','A03_TRAILER']}
for n,p in positions.items():
 o=bpy.data.objects[n]
 for fc in curves(o):
  if fc.data_path!='location':continue
  protected={float(k.co.x):(tuple(k.handle_left),tuple(k.handle_right)) for k in fc.keyframe_points if k.co.x>=620}
  for k in reversed(list(fc.keyframe_points)):
   if k.co.x<620:fc.keyframe_points.remove(k,fast=True)
  k=fc.keyframe_points.insert(0,p[fc.array_index]);k.interpolation='LINEAR';fc.update()
  for k in fc.keyframe_points:
   if float(k.co.x) in protected:k.handle_left,k.handle_right=protected[float(k.co.x)]
# 0.8m diameter tires require more than the inherited 0.5m axle spacing.
for o in s.objects:
 if o.name.startswith('A03_TRAILER_WHEEL_'):o.location.x=.5 if o.location.x>0 else -.5
# Cab/chassis shared side faces formerly occupied the same plane over a 0.245m strip.
cab=bpy.data.objects['TRACTOR_CAB'];top=cab.location.z+cab.dimensions.z/2
chassis=bpy.data.objects['TRACTOR_CHASSIS'];bottom=chassis.location.z+chassis.dimensions.z/2
cab.dimensions.z=top-bottom;cab.location.z=(top+bottom)/2
# Resolve each axle's suspension height over the quay/road step. This changes
# wheels only: vehicle trajectory, coupling, payload and hoist remain intact.
from mathutils import Vector
from mathutils.bvhtree import BVHTree
I=bpy.data.objects['US_FRAME'].matrix_world.inverted();ground=[]
for name in ['US_QUAY','US_LAND_TERRACE','E07_INBOUND_ROAD','E09_MANEUVER_YARD']:
 o=bpy.data.objects[name];ground.append(BVHTree.FromPolygons([I@o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons]))
wheels=[o for o in s.objects if o.name.startswith('A03') and '_WHEEL_' in o.name]
rows={o.name:[] for o in wheels}
for j in range(648*16,1392*16+1):
 f=j/16;s.frame_set(int(f),subframe=f%1)
 for o in wheels:
  M=I@o.matrix_world;center=M.translation;bottom=min((M@v.co).z for v in o.data.vertices)
  axis=I.to_3x3()@o.parent.matrix_world.to_3x3()@o.matrix_parent_inverse.to_3x3()@Vector((0,0,1));dz=0
  for _ in range(3):
   c=center+axis*dz;hits=[b.ray_cast(c+Vector((0,0,5)),Vector((0,0,-1)),20)[0] for b in ground];height=max(v.z for v in hits if v is not None)
   dz=(height-bottom)/axis.z
  if abs(dz)<.0001:dz=0
  rows[o.name].append((f,o.location.z+dz))
for o in wheels:
 o.keyframe_insert('location',index=2,frame=0)
 samples=rows[o.name];keep={0,len(samples)-1};stack=[(0,len(samples)-1)]
 while stack:
  lo,hi=stack.pop()
  if hi-lo<2:continue
  f0,z0=samples[lo];f1,z1=samples[hi]
  error,k=max((abs(z-(z0+(z1-z0)*(f-f0)/(f1-f0))),i) for i,(f,z) in enumerate(samples[lo+1:hi],lo+1))
  if error>0.00001:keep.add(k);stack.extend([(lo,k),(k,hi)])
 for i in sorted(keep):
  f,z=samples[i];o.location.z=z;o.keyframe_insert('location',index=2,frame=f)
 for fc in curves(o):
  for k in fc.keyframe_points:k.interpolation='LINEAR'
s.frame_set(596)
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'master-s4-s5-boundary-v001.blend'))






