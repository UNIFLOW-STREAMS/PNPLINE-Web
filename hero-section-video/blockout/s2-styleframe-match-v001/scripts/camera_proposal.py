"""User-approved separate S2 viewpoint proposal; source actions outside S2 intact."""
import bpy,math,json
from mathutils import Vector,Quaternion
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def smooth(t):return t*t*t*(t*(t*6-15)+10)
def curves(o):return [fc for l in o.animation_data.action.layers for st in l.strips for bag in st.channelbags for fc in bag.fcurves]
def apply():
 s=bpy.context.scene;cam=s.camera;target=s.objects['CAM_LOOK_TARGET'];cn=s.objects['CN_FRAME'].matrix_world.copy();inv=cn.inverted();base={}
 for f in range(0,1393):
  s.frame_set(f);base[f]=(cam.matrix_world.translation.copy(),target.matrix_world.translation.copy(),cam.rotation_quaternion.copy())
 def aim(p,t):return cn.to_quaternion()@((inv@t)-(inv@p)).to_track_quat('-Z','Y')
 config=json.loads((R/'camera-settings.json').read_text()) if (R/'camera-settings.json').exists() else {'position':[22,47,32],'target':[4,-12,5]}
 def desired(f):return cn@(Vector(config['position'])+Vector((-.04*(f-156),-.02*(f-156),0))),cn@Vector(config['target'])
 def hermite(a,b,da,db,u,span):return (2*u**3-3*u*u+1)*a+(u**3-2*u*u+u)*span*da+(-2*u**3+3*u*u)*b+(u**3-u*u)*span*db
 velocity=cn.to_3x3()@Vector((-.04,-.02,0));zero=Vector((0,0,0))
 poses={};prev=base[97][2]
 for f in range(98,215):
  w=smooth((f-97)/47) if f<144 else 1 if f<=170 else smooth((215-f)/45)
  # New viewpoint sees the inherited ship's +X bow on screen left.
  dp,dt=desired(f);op,ot,oq=base[f]
  if f<144:
   u=(f-97)/47;endp,endt=desired(144)
   p=hermite(base[97][0],endp,base[97][0]-base[96][0],velocity,u,47)
   t=hermite(base[97][1],endt,base[97][1]-base[96][1],zero,u,47)
   p+=cn.to_3x3()@Vector((0,0,8*math.sin(math.pi*u)**2))
  elif f>170:
   u=(f-170)/45;startp,startt=desired(170)
   p=hermite(startp,base[215][0],velocity,base[216][0]-base[215][0],u,45)
   t=hermite(startt,base[215][1],zero,base[216][1]-base[215][1],u,45)
   p+=cn.to_3x3()@Vector((0,0,8*math.sin(math.pi*u)**2))
  else:p,t=dp,dt
  raw=aim(p,t);original_raw=aim(op,ot);residual=original_raw.rotation_difference(oq)
  if residual.w<0:residual.negate()
  q=raw@Quaternion((1,0,0,0)).slerp(residual,1-w)
  if q.dot(prev)<0:q.negate()
  poses[f]=(p,t,q);prev=q
 for o in (cam,target):
  for fc in curves(o):
   if fc.data_path not in ['location','rotation_quaternion']:continue
   for k in fc.keyframe_points:
    f=k.co.x
    if f in poses:
     p,t,q=poses[f];value=q if fc.data_path=='rotation_quaternion' else p if o==cam else t
     k.co.y=value[fc.array_index]
 s.frame_set(156)
 return {'approved':'user approved separate S2 camera/target proposal, not final adoption','changed_key_frames':[98,214],'lens':40,'cn_position_f156':config['position'],'cn_target_f156':config['target'],'new_city_frame':'CN_FRAME rotated 180 degrees around local Z; preliminary to match view','motion':'original non-camera actions untouched','status':'proposal; geometry, continuity and collisions require validation'}
if __name__=='__main__':
 import sys
 out=Path(sys.argv[sys.argv.index('--')+1]).resolve();assert not out.exists()
 cfg=apply();(R/'review/camera-proposal-config.json').write_text(json.dumps(cfg,indent=2))
 bpy.ops.wm.save_as_mainfile(filepath=str(out))
