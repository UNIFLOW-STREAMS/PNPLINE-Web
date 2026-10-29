import bpy,json
s=bpy.context.scene;c=s.objects['CAM_MASTER'];a=c.animation_data.action
print('CAMERA',c.rotation_mode,list(c.scale),'NLA',[(t.name,len(t.strips)) for t in c.animation_data.nla_tracks])
for l in a.layers:
 for st in l.strips:
  for bag in st.channelbags:
   for f in bag.fcurves:
    if f.data_path=='rotation_quaternion':print('CURVE',f.array_index,'MODS',[(m.type,m.name) for m in f.modifiers],'KEYS',[(list(k.co),k.interpolation) for k in f.keyframe_points if 467.75<=k.co.x<=468.5])
for f in [467.75,468,468.25,468.5]:
 s.frame_set(int(f),subframe=f%1);print('AT',f,list(c.rotation_quaternion),list(c.matrix_world.to_quaternion()))
