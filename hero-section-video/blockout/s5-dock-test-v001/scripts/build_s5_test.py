import bpy,sys,json,math,argparse
from pathlib import Path
from mathutils import Matrix,Vector
sys.path.insert(0,str(Path(__file__).parent))
from isolate_scene import clone_subset,_own
from kinematics import vehicle_state,smooth
def build(cfg):
 src=bpy.data.scenes[cfg['source_scene']];old_frame=src.frame_current
 bpy.context.window.scene=src;src.frame_set(890)
 roots=['US_FRAME','US_LAND_TERRACE','E07_INBOUND_ROAD','E09_MANEUVER_YARD','E08_WAREHOUSE','DOCK_TARGET','DOCK_BRIDGE','INBOUND_WAIT_ZONE','A03_TRAILER','A03_TRACTOR','A01_CONTAINER','W01_NEW_PALLET']
 names=set(roots)
 for n in roots:
  if n!='US_FRAME':names.update(o.name for o in src.objects[n].children_recursive)
 names.update(o.name for o in src.objects if o.name.startswith('RACK_'))
 scene,m=clone_subset(src,sorted(names),cfg['test_scene']);owner=scene['s5_owner'];coll=scene.collection.children[0]
 bpy.context.window.scene=scene;U=m['US_FRAME'].matrix_world.copy()
 def helper(name,kind=None):
  data=_own(bpy.data.cameras.new('S5T__'+name+'Data'),owner) if kind=='CAMERA' else None
  o=_own(bpy.data.objects.new('S5T__'+name,data),owner);coll.objects.link(o);o['instance_id']=o.name;return o
 cam=helper('CAM_OBLIQUE','CAMERA');top=helper('CAM_TOP','CAMERA');target=helper('LOOK_TARGET')
 cam.data.lens=40;cam.data.clip_end=500;top.data.type='ORTHO';top.data.ortho_scale=44;top.data.clip_end=500
 top.matrix_world=U@Matrix.Translation((32,20,60));top.rotation_euler=(U.to_quaternion()@Vector((0,0,-1)).to_track_quat('-Z','Y')).to_euler()
 def clear_owned_animation(o):
  action=o.animation_data.action if o.animation_data else None;o.animation_data_clear()
  if action and action.users==0 and action.get('s5_owner')==owner:bpy.data.actions.remove(action)
 for n in ['A03_TRAILER','A03_TRACTOR','A01_CONTAINER','W01_NEW_PALLET']:clear_owned_animation(m[n])
 for n in ['A03_TRAILER','A03_TRACTOR']:m[n].parent=m['US_FRAME'];m[n].matrix_parent_inverse=Matrix.Identity(4);m[n].rotation_mode='XYZ'
 m['A01_CONTAINER'].parent=m['A03_TRAILER'];m['A01_CONTAINER'].matrix_parent_inverse=Matrix.Identity(4);m['A01_CONTAINER'].matrix_basis=Matrix.Translation((0,0,2.55))
 m['W01_NEW_PALLET'].parent=m['A01_CONTAINER'];m['W01_NEW_PALLET'].matrix_parent_inverse=Matrix.Identity(4);m['W01_NEW_PALLET'].matrix_basis=Matrix.Translation((-.65,0,-.49))
 wheels=[o for n,o in m.items() if '_WHEEL_' in n];roll={o.name:0. for o in wheels};previous={};last_eulers={}
 for o in wheels:clear_owned_animation(o);o.rotation_mode='XYZ'
 repairs=cfg['proxy_repairs']
 for o in wheels:
  if 'TRAILER_WHEEL' in o.name:o.location.x=math.copysign(repairs['trailer_tandem_half_spacing'],o.location.x)
 for side,leaf in [('L','LEFT'),('R','RIGHT')]:
  m['A01_DOOR_'+side].location.x=repairs['door_hinge_x'];m['A01_DOOR_'+leaf+'_LEAF'].scale.z=repairs['door_leaf_height']/1.5
 m['DOCK_BRIDGE'].location.z=repairs['bridge_center_z'];m['DOCK_BRIDGE'].scale.y=repairs['bridge_width']/1.48
 def wheel_point(st,o):
  kind='tractor' if 'TRACTOR_WHEEL' in o.name else 'trailer';a=st[kind+'_yaw'];x,y=o.location[:2];p=st[kind]
  return (p[0]+math.cos(a)*x-math.sin(a)*y,p[1]+math.sin(a)*x+math.cos(a)*y)
 for i in range(cfg['frames']['start']*4,cfg['frames']['end']*4+1):
  f=i/4;st=vehicle_state(f,cfg);before=vehicle_state(max(648,f-.01),cfg);after=vehicle_state(min(900,f+.01),cfg)
  for n,kind in [('A03_TRAILER','trailer'),('A03_TRACTOR','tractor')]:
   o=m[n];o.location=(*st[kind],0);o.rotation_euler=(0,0,st[kind+'_yaw'])
   if o.name in last_eulers:o.rotation_euler.make_compatible(last_eulers[o.name])
   last_eulers[o.name]=o.rotation_euler.copy();o.keyframe_insert('location',frame=f);o.keyframe_insert('rotation_euler',frame=f)
  for o in wheels:
   kind='tractor' if 'TRACTOR_WHEEL' in o.name else 'trailer';a=st[kind+'_yaw'];p=wheel_point(st,o);pa=wheel_point(after,o);pb=wheel_point(before,o);v=Vector((pa[0]-pb[0],pa[1]-pb[1]));F=Vector((math.cos(a),math.sin(a)))
   steering=0.
   if kind=='tractor' and o.location.x>1 and v.length>1e-8:
    if v.dot(F)<0:v=-v
    steering=math.atan2(F.x*v.y-F.y*v.x,F.dot(v))
   if o.name in previous:
    delta=Vector((p[0]-previous[o.name][0],p[1]-previous[o.name][1]));roll[o.name]+=delta.length*(1 if delta.dot(F)>=0 else -1)/cfg['rig']['wheel_radius']
   previous[o.name]=p;o.rotation_euler=(math.pi/2,-roll[o.name],steering);o.keyframe_insert('rotation_euler',frame=f)
  # Continuous exterior south-side path, then gaze into the existing dock floor.
  t=smooth((f-648)/242);pos=Vector((17+26*t,1+18*t,9-t));focus=Vector((*st['trailer'],2.1));handoff=smooth((f-842)/58);focus=focus.lerp(Vector((36.5,29,2.1)),handoff)
  cam.matrix_world=U@Matrix.Translation(pos)@(focus-pos).to_track_quat('-Z','Y').to_matrix().to_4x4();target.location=U@focus
  for o in [cam,target]:
   if o.name in last_eulers:o.rotation_euler.make_compatible(last_eulers[o.name])
   last_eulers[o.name]=o.rotation_euler.copy();o.keyframe_insert('location',frame=f);o.keyframe_insert('rotation_euler',frame=f)
 # Keep original door keys/timing. Other changed actions are baked with linear interpolation.
 for o in [m['A03_TRAILER'],m['A03_TRACTOR'],cam,target,*wheels]:
  action=o.animation_data.action;action.name=o.name+'__Action';_own(action,owner)
  for layer in action.layers:
   for strip in layer.strips:
    for bag in strip.channelbags:
     for fc in bag.fcurves:
      for key in fc.keyframe_points:key.interpolation='LINEAR'
 # Diagnostic path is an independent Curve, not an animated master target.
 curve=_own(bpy.data.curves.new('S5T__AXLE_PATH','CURVE'),owner);curve.dimensions='3D';sp=curve.splines.new('POLY');sp.points.add(161)
 for j,p in enumerate(sp.points):p.co=(*vehicle_state(649+j,cfg)['trailer'],.79,1)
 path=_own(bpy.data.objects.new('S5T__AXLE_PATH',curve),owner);coll.objects.link(path);path.parent=m['US_FRAME'];path.hide_render=True
 scene.frame_start=648;scene.frame_end=900;scene.render.fps=12;scene.camera=cam;scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=960;scene.render.resolution_y=540;scene.render.resolution_percentage=100
 scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.background_type='WORLD'
 for label,f in [('A approach',648),('B forward turn',746),('C aligned',810),('Doors locked',842),('Reverse',849),('D docked',890)]:scene.timeline_markers.new(label,frame=f)
 src.frame_set(old_frame);scene.frame_set(648)
 return scene,m
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--output',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);out=Path(a.output)
 if Path(bpy.data.filepath).resolve()==out.resolve():raise ValueError('Input/output must differ')
 cfg=json.loads(Path(a.config).read_text(encoding='utf8'));s,m=build(cfg);out.parent.mkdir(parents=True,exist_ok=True)
 (out.parent/'source-map.json').write_text(json.dumps({n:dict(test_object=o.name,source_data=o.get('source_data',''),source_asset_id=o.get('source_asset_id',''),test_data=o.data.name if o.data else None) for n,o in m.items()},indent=2),encoding='utf8')
 bpy.ops.wm.save_as_mainfile(filepath=str(out));print('BUILT',out,'objects',len(s.objects))
