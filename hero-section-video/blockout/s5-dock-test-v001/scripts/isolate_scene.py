"""Clone an explicit subset with independent mutable objects and animations."""
import bpy
PREFIX='S5T__'
def _unsupported(id_block):
 ad=getattr(id_block,'animation_data',None)
 return bool((ad and (len(ad.drivers) or len(ad.nla_tracks))) or len(getattr(id_block,'constraints',[])))
def _own(block,owner):block['s5_owner']=owner;return block
def _copy_action(source,target,name,owner):
 ad=getattr(source,'animation_data',None)
 if ad and ad.action:
  action=ad.action.copy();action.name=name;_own(action,owner)
  target.animation_data_create();target.animation_data.action=action
def clone_subset(source,names,scene_name):
 owner='pnpline-s5-test:'+scene_name;objects=[source.objects[n] for n in names];selected=set(objects)
 for o in objects:
  if o.parent and o.parent not in selected:raise ValueError('Missing independent parent for '+o.name)
  if _unsupported(o) or (o.data and _unsupported(o.data)):raise ValueError('Unsupported driver/NLA/constraint: '+o.name)
  if getattr(o.data,'shape_keys',None):raise ValueError('Unsupported animated shape keys: '+o.name)
 existing=bpy.data.scenes.get(scene_name)
 if existing and existing.get('s5_owner')!=owner:raise ValueError('Scene name collision: '+scene_name)
 # Fail before cleanup or creation if a prefix belongs to someone else.
 for pool in [bpy.data.objects,bpy.data.collections,bpy.data.actions,bpy.data.cameras,bpy.data.curves,bpy.data.armatures]:
  for item in pool:
   if item.name.startswith(PREFIX) and item.get('s5_owner')!=owner:raise ValueError('Foreign prefix collision: '+item.name)
 if existing:
  # ID user_map follows parent, constraint/modifier targets, driver IDs and
  # other Blender ID references, including objects not linked to any Scene.
  owned={v for pool in [bpy.data.objects,bpy.data.collections,bpy.data.cameras,bpy.data.curves,bpy.data.armatures,bpy.data.actions] for v in pool if v.get('s5_owner')==owner}
  for block,users in bpy.data.user_map(subset=owned).items():
   for user in users:
    if user.get('s5_owner')!=owner:raise ValueError('Owned data referenced outside test ownership: '+block.name+' by '+user.name)
  for other in bpy.data.scenes:
   if other==existing:continue
   for o in other.objects:
    refs=[o,o.data]
    for block in [o,o.data]:
     ad=getattr(block,'animation_data',None)
     if ad and ad.action:refs.append(ad.action)
    if any(block is not None and block.get('s5_owner')==owner for block in refs):raise ValueError('Owned data referenced outside test scene: '+o.name)
  for o in existing.objects:
   if o.get('s5_owner')!=owner:raise ValueError('Foreign object in owned scene: '+o.name)
  bpy.data.scenes.remove(existing)
  for o in list(bpy.data.objects):
   if o.get('s5_owner')==owner:bpy.data.objects.remove(o,do_unlink=True)
  for pool in [bpy.data.collections,bpy.data.cameras,bpy.data.curves,bpy.data.armatures,bpy.data.actions]:
   for item in list(pool):
    if item.get('s5_owner')==owner and item.users==0:pool.remove(item)
 scene=_own(bpy.data.scenes.new(scene_name),owner)
 collection=_own(bpy.data.collections.new(PREFIX+'ROOT'),owner);scene.collection.children.link(collection)
 mapping={}
 for old in objects:
  new=_own(old.copy(),owner);new.name=PREFIX+old.name;collection.objects.link(new)
  new['source_object']=old.name;new['source_data']=old.data.name if old.data else ''
  new['source_asset_id']=old.get('asset_id','');new['instance_id']=PREFIX+old.name
  _copy_action(old,new,PREFIX+old.name+'__Action',owner)
  if old.data and old.type in {'CAMERA','CURVE','ARMATURE'}:
   new.data=_own(old.data.copy(),owner);new.data.name=PREFIX+old.data.name
   _copy_action(old.data,new.data,PREFIX+old.name+'__DataAction',owner)
  mapping[old.name]=new
 for old in objects:mapping[old.name].parent=mapping.get(old.parent.name) if old.parent else None
 scene.world=source.world
 scene.camera=mapping.get(source.camera.name) if source.camera else None
 scene.render.engine=source.render.engine
 for key in ['fps','fps_base','resolution_x','resolution_y','resolution_percentage','film_transparent']:
  setattr(scene.render,key,getattr(source.render,key))
 for key in ['light','studio_light','color_type','show_shadows','show_cavity','cavity_type','background_type','background_color','show_specular_highlight']:
  setattr(scene.display.shading,key,getattr(source.display.shading,key))
 scene.frame_start=source.frame_start;scene.frame_end=source.frame_end;scene.frame_set(source.frame_current)
 return scene,mapping
