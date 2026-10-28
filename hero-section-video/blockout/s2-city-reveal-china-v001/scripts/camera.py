"""Bounded Hermite path. Outside keys and boundary neighbourhood untouched."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector,Quaternion
R=Path(__file__).resolve().parents[1]
def apply(cfg):
 from build import pose
 s=bpy.context.scene;cam=s.camera;target=s.objects['CAM_LOOK_TARGET']
 assert cam.parent is None and target.parent is None and not cam.constraints
 base=json.loads((R/'review/baseline.json').read_text())['frames']
 nodes=cfg['nodes'];frames=[x[0] for x in nodes]
 vals=[[Vector(node[col] if node[col] is not None else base[str(node[0])][key]) for node in nodes] for col,key in [(1,'p'),(2,'t')]]
 deriv=[]
 for vs,key in zip(vals,['p','t']):
  ds=[Vector(base[str(frames[0])][key])-Vector(base[str(frames[0]-1)][key])]
  for i in range(1,len(nodes)-1):ds.append((vs[i+1]-vs[i-1])/(frames[i+1]-frames[i-1]))
  if nodes[-1][1] is None:ds.append(Vector(base[str(frames[-1]+1)][key])-Vector(base[str(frames[-1])][key]))
  else:ds.append((vs[-1]-vs[-2])/(frames[-1]-frames[-2]))
  deriv.append(ds)
 def evaluate(v,d,f):
  i=next(i for i in range(len(frames)-1) if frames[i]<=f<=frames[i+1]);span=frames[i+1]-frames[i];u=(f-frames[i])/span
  return (2*u**3-3*u*u+1)*v[i]+(u**3-2*u*u+u)*span*d[i]+(-2*u**3+3*u*u)*v[i+1]+(u**3-u*u)*span*d[i+1]
 s.frame_set(frames[0]);prev=cam.rotation_quaternion.copy()
 poses={}
 blend_start,blend_end=cfg.get('orientation_residual_blend',[188,215])
 for f in range(frames[0]+1,frames[-1]+(0 if nodes[-1][1] is None else 1)):
  p,t,q=pose(evaluate(vals[0],deriv[0],f),evaluate(vals[1],deriv[1],f))
  # The inherited S3 camera has a ship/sphere-up roll, different from CN up.
  # Blend its small orientation residual, not its distant viewing direction,
  # into the last internal arc. At the endpoint raw pose and residual compose
  # to the original quaternion and its moving residual supplies the endpoint rate.
  if f>blend_start and nodes[-1][1] is None:
   raw_base=pose(base[str(f)]['p'],base[str(f)]['t'])[2]
   residual=raw_base.rotation_difference(Quaternion(base[str(f)]['q']))
   if residual.w<0:residual.negate()
   u=min(1,(f-blend_start)/(blend_end-blend_start));w=u*u*(3-2*u)
   q=q@Quaternion((1,0,0,0)).slerp(residual,w)
  if q.dot(prev)<0:q.negate()
  poses[f]=(p,t,q);prev=q
 # Modify only existing keyed values. LINEAR neighbours outside the open interval are unchanged.
 for o in [cam,target]:
  for layer in o.animation_data.action.layers:
   for strip in layer.strips:
    for bag in strip.channelbags:
     for fc in bag.fcurves:
      if fc.data_path not in ['location','rotation_quaternion']:continue
      for kp in fc.keyframe_points:
       f=float(kp.co.x)
       if f in poses:
        p,t,q=poses[f];v=q if fc.data_path=='rotation_quaternion' else p if o==cam else t
        kp.co.y=v[fc.array_index];kp.interpolation='LINEAR'
      # Values changed in place; key ordering and LINEAR interpolation already valid.
      # Do not call update(): it recalculates AUTO handles on protected outer keys.
 s.frame_set(156)
