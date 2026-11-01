import bpy,sys,math,json,numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1]
B=R.parents[1]/'blockout'
sys.path[:0]=[str(R.parent/'us-warehouse-curvature-v001/scripts'),str(B/'curvature-rework-v001/scripts'),str(R.parent/'container-ship-v001/scripts')]
from surface_site import sphere,arc,basis
S=bpy.context.scene
U=S.objects['US_FRAME']
def flat(p):return arc(np.array(U.matrix_world.inverted()@Vector(p)))
def loc(o):return flat(o.matrix_world.translation).round(3).tolist()
s=S
pref=bpy.context.preferences.addons['cycles'].preferences
pref.compute_device_type='OPTIX';pref.get_devices()
for d in pref.devices:d.use=d.type=='OPTIX'
s.render.engine='CYCLES';s.cycles.device='GPU' if any(d.use for d in pref.devices) else 'CPU'
s.cycles.samples=36;s.cycles.adaptive_min_samples=12;s.cycles.adaptive_threshold=.028;s.cycles.use_denoising=True
s.render.resolution_x=1280;s.render.resolution_y=800;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8'
cam=bpy.data.objects.new('Review only camera',bpy.data.cameras.new('Review only camera'));s.collection.objects.link(cam)
master=s.camera
def run(fn):
 s.render.filepath=str(R/'review'/fn);bpy.ops.render.render(write_still=True);print('REVIEW',fn,flush=True)
def custom(aim,delta,width,ref):
 aim=Vector(aim);delta=Vector(delta)
 cam.matrix_world=ref@Matrix.Translation(aim+delta)@(-delta).to_track_quat('-Z','Y').to_matrix().to_4x4()
 cam.data.type='ORTHO';cam.data.ortho_scale=width;cam.data.clip_end=1000;s.camera=cam
for shot in sys.argv[sys.argv.index('--')+1:]:
 if shot=='exterior' or shot=='receiving':
  s.frame_set(850 if shot=='exterior' else 655);pt=np.array([52.,32.,1.86]);mat=Matrix(basis(sphere,pt).tolist()).to_4x4();mat.translation=Vector(sphere(pt));ref=U.matrix_world@mat
  if shot=='exterior':custom((0,0,4.1),(24,-45,29),47,ref)
  else:custom((-8,-.6,5),(-28,-20,18),36,ref)
  run(shot+'.png')
 elif shot.isdigit():
  s.camera=master;s.frame_set(int(shot));s.render.resolution_y=720;run('cam-'+shot+'.png')
 elif shot=='staff':
  # Non-saved product plate made from the evaluated meshes of the three actual employees.
  s.frame_set(820);dg=bpy.context.evaluated_depsgraph_get();new=bpy.data.scenes.new('Review | employee maquettes')
  new.render.engine='CYCLES';new.cycles.device=s.cycles.device;new.cycles.samples=64;new.cycles.use_denoising=True;new.world=s.world
  new.render.resolution_x=1440;new.render.resolution_y=800;new.render.resolution_percentage=100;new.render.image_settings.file_format='PNG'
  new.view_settings.view_transform=s.view_settings.view_transform;new.view_settings.look=s.view_settings.look
  for role,x,ang in [('Pick',-1.04,math.pi+.40),('Pack',0,.5),('Load',1.04,math.pi-.75)]:
   basis0=s.objects['Figure '+role+' | surface anchor'].matrix_world.inverted()
   for orig in s.objects:
    if (orig.name.startswith('Figure '+role+' | ') and orig.type=='MESH') or (orig.name=='CH_LOAD_SUPPORT' and role=='Load'):
     ev=orig.evaluated_get(dg);mesh=bpy.data.meshes.new_from_object(ev,depsgraph=dg);o=bpy.data.objects.new('Plate '+orig.name,mesh);new.collection.objects.link(o)
     o.matrix_world=Matrix.Translation((x,0,0))@Matrix.Rotation(ang,4,'Z')@basis0@ev.matrix_world
  # Paper sweep floor.
  m=bpy.data.materials.new('Stone studio stock');m.diffuse_color=(.40,.47,.49,1);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.40,.47,.49,1)
  mesh=bpy.data.meshes.new('Sweep');mesh.from_pydata([(-200,-200,0),(200,-200,0),(200,200,0),(-200,200,0)],[],[(0,1,2,3)]);mesh.materials.append(m);ob=bpy.data.objects.new('Sweep',mesh);new.collection.objects.link(ob)
  def lamp(pos,watts,size,color):
   l=bpy.data.lights.new('Softbox','AREA');l.energy=watts;l.shape='DISK';l.size=size;l.color=color
   ob=bpy.data.objects.new('Softbox',l);new.collection.objects.link(ob);ob.location=pos;ob.rotation_euler=(Vector((0,0,.82))-Vector(pos)).to_track_quat('-Z','Y').to_euler()
  lamp((-3,-4,5),370,4,(1,.91,.80));lamp((3,-3,3.2),200,4,(.83,.94,1));lamp((1.5,2.2,3.6),255,3,(1,1,1))
  c=bpy.data.objects.new('Plate camera',bpy.data.cameras.new('Plate camera'));new.collection.objects.link(c);c.data.type='ORTHO';c.data.ortho_scale=3.82;c.location=(.1,-6.2,2.12);c.rotation_euler=(Vector((0,0,.86))-c.location).to_track_quat('-Z','Y').to_euler();new.camera=c
  new.render.filepath=str(R/'review/crew-maquettes.png');bpy.ops.render.render(write_still=True,scene=new.name);print('REVIEW staff',flush=True)

