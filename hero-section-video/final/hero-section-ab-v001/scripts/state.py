import bpy,json,hashlib,numpy as np

def sha(path):
 with open(path,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def clean(v):
 if isinstance(v,(str,int,bool)) or v is None:return v
 if isinstance(v,float):return round(v,7)
 if isinstance(v,bpy.types.ID):return v.name
 if hasattr(v,'bl_rna'):
  out={}
  for prop in v.bl_rna.properties:
   k=prop.identifier
   if k in {'rna_type','id_data'}:continue
   try:out[k]=clean(getattr(v,k))
   except (AttributeError,TypeError):pass
  return out
 try:return [clean(x) for x in v]
 except TypeError:return str(v)

def hashed(v):return hashlib.sha256(json.dumps(v,sort_keys=True).encode()).hexdigest()

def tree(t):
 if not t:return None
 nodes=[]
 for n in t.nodes:
  props={}
  for prop in n.bl_rna.properties:
   k=prop.identifier
   if k in {'rna_type','location','width','height','dimensions','select','parent','internal_links','inputs','outputs'} or prop.type=='COLLECTION':continue
   try:props[k]=clean(getattr(n,k))
   except (AttributeError,TypeError):pass
  nodes.append([n.name,n.bl_idname,props,[(i.identifier,clean(i.default_value)) for i in n.inputs if hasattr(i,'default_value')]])
 return dict(nodes=nodes,links=[(l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in t.links])

def curves(action,skip_dof=False):
 rows=[]
 if not action:return rows
 for layer in action.layers:
  for strip in layer.strips:
   for bag in strip.channelbags:
    for f in bag.fcurves:
     if skip_dof and f.data_path.startswith('dof.'):continue
     rows.append([f.data_path,f.array_index,f.extrapolation,[(clean(k.co),clean(k.handle_left),clean(k.handle_right),k.interpolation,k.handle_left_type,k.handle_right_type) for k in f.keyframe_points]])
 return rows

def snapshot(motion=True):
 s=bpy.context.scene;opened=s.frame_current;s.frame_set(0)
 objects={o.name:[o.type,o.data.name if o.data else None,o.parent.name if o.parent else None,clean(o.matrix_basis),clean(o.matrix_parent_inverse),o.hide_render,[(c.name,c.type,c.influence,c.mute,getattr(getattr(c,'target',None),'name',None)) for c in o.constraints],[(m.name,m.type,m.show_render) for m in o.modifiers]] for o in s.objects if o.type!='LIGHT'}
 geometry={}
 for m in bpy.data.meshes:
  h=hashlib.sha256()
  for coll,attr,n,dtype in [(m.vertices,'co',3,np.float32),(m.loops,'vertex_index',1,np.int32),(m.polygons,'loop_total',1,np.int32),(m.polygons,'material_index',1,np.int32)]:
   a=np.empty(len(coll)*n,dtype=dtype);coll.foreach_get(attr,a);h.update(a.tobytes())
  geometry[m.name]=h.hexdigest()
 for c in bpy.data.curves:
  geometry[c.name]=hashed([c.bl_rna.identifier,c.dimensions,c.resolution_u,c.bevel_depth,c.bevel_resolution,[(sp.type,sp.use_cyclic_u,[(clean(p.co),clean(p.handle_left),clean(p.handle_right)) for p in sp.bezier_points],[clean(p.co) for p in sp.points]) for sp in c.splines]])
 actions={a.name:hashed(rows) for a in bpy.data.actions if (rows:=curves(a,True))}
 slots={o.name:[(sl.link,sl.material.name if sl.material else None) for sl in o.material_slots] for o in s.objects if o.material_slots}
 used={sl.material for o in s.objects for sl in o.material_slots if sl.material}
 materials={m.name:hashed([clean(m.diffuse_color),tree(m.node_tree)]) for m in used}
 camera=[];dof=[]
 if motion:
  c=s.camera
  for f in range(990):
   s.frame_set(f);d=c.data
   camera.append(clean([c.matrix_world,d.type,d.lens,d.sensor_width,d.sensor_height,d.sensor_fit,d.clip_start,d.clip_end,d.shift_x,d.shift_y,d.ortho_scale]))
   dof.append(clean([d.dof.use_dof,d.dof.focus_distance,d.dof.aperture_fstop,d.dof.aperture_blades,d.dof.aperture_rotation,d.dof.aperture_ratio,getattr(d.dof.focus_object,'name',None)]))
 s.frame_set(opened)
 return dict(objects=objects,geometry=geometry,non_dof_actions=actions,slots=slots,materials=materials,camera_990=camera,dof_990=dof,timing=dict(start=s.frame_start,end=s.frame_end,fps=s.render.fps,fps_base=s.render.fps_base,markers=[(m.name,m.frame) for m in s.timeline_markers]))

def presentation():
 s=bpy.context.scene;opened=s.frame_current;s.frame_set(0)
 lights={}
 for o in s.objects:
  if o.type!='LIGHT':continue
  props={p.identifier:clean(getattr(o.data,p.identifier)) for p in o.data.bl_rna.properties if p.identifier!='rna_type' and p.type not in {'COLLECTION','POINTER'}}
  lights[o.name]=[o.parent.name if o.parent else None,clean(o.matrix_basis),clean(o.matrix_parent_inverse),props,tree(o.data.node_tree),o.hide_render]
 view={k:clean(getattr(s.view_settings,k)) for k in ['view_transform','look','exposure','gamma','view_settings'] if hasattr(s.view_settings,k)}
 result=dict(lights=lights,world=tree(s.world.node_tree),compositor=tree(s.compositing_node_group),view=view,film_transparent=s.render.film_transparent,use_compositing=s.render.use_compositing,gradient=[dict(name=i.name,packed=bool(i.packed_file),size=list(i.size)) for i in bpy.data.images if i.name.startswith('BG |')])
 s.frame_set(opened);return result
