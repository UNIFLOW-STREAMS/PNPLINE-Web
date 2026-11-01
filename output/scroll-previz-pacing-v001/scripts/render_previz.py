import bpy,sys,json,time,hashlib,math,numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[1];s=bpy.context.scene
def sha(p):
 with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
source=Path(bpy.data.filepath);digest=sha(source)
saved=s.frame_current
meta=dict(source=str(source),sha256=digest,fps=s.render.fps/s.render.fps_base,frame_start=s.frame_start,frame_end=s.frame_end,camera=s.camera.name,markers=[dict(name=m.name,frame=m.frame,camera=m.camera.name if m.camera else None)for m in s.timeline_markers],objects=len(s.objects),source_engine=s.render.engine,source_resolution=[s.render.resolution_x,s.render.resolution_y],camera_samples=[])
assert meta['fps']==30 and meta['frame_start']==0 and meta['frame_end']==989 and meta['camera']=='CAM_MASTER'
cfg=json.loads((R/'pacing.json').read_text(encoding='utf-8'));marks={m.name:m.frame for m in s.timeline_markers}
assert all(marks.get(section['id'])==section['startFrame']for section in cfg['sections']),'Source markers changed: review pacing config before rendering'
last=None
for f in range(990):
 s.frame_set(f);m=s.camera.evaluated_get(bpy.context.evaluated_depsgraph_get()).matrix_world.copy();q=m.to_quaternion();p=m.translation
 meta['camera_samples'].append(dict(frame=f,position=list(p),step=(p-last[0]).length if last else 0,angle=q.rotation_difference(last[1]).angle if last else 0));last=(p.copy(),q.copy())
(R/'data/source-scene.json').write_text(json.dumps(meta,indent=2))
s.render.engine='BLENDER_WORKBENCH';s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100;s.render.use_compositing=False;s.render.use_sequencer=False;s.render.use_border=False
s.display.shading.light='STUDIO';s.display.shading.studiolight_rotate_z=.3;s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.shading.curvature_ridge_factor=1.15;s.display.shading.curvature_valley_factor=.8;s.display.shading.show_specular_highlight=True;s.display.shading.background_type='WORLD';s.display.shading.show_object_outline=False;s.display.render_aa='8'
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.image_settings.color_depth='8';s.render.image_settings.compression=15;s.render.film_transparent=False
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['sample']
if 'batch' in args:
 # Render-only consolidation of rigid, static mesh leaves. Animated ancestors
 # remain live. No scene or blend file is saved by this script.
 s.frame_set(0);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();groups={};excluded=0
 def animated(o):return bool(o.animation_data or o.constraints)
 for o in list(s.objects):
  if o.type!='MESH' or o.hide_render:continue
  if animated(o) or o.data.shape_keys or any(m.type not in {'BEVEL','WEIGHTED_NORMAL','ARRAY','SOLIDIFY','SUBSURF','TRIANGULATE','EDGE_SPLIT'} for m in o.modifiers):excluded+=1;continue
  p=o.parent
  while p and not animated(p):p=p.parent
  groups.setdefault(p.name if p else None,[]).append(o)
 counts=[]
 for anchor,names in groups.items():
  if len(names)<8:continue
  parent=s.objects.get(anchor) if anchor else None;inv=parent.matrix_world.inverted() if parent else None;verts=[];loops=[];starts=[];totals=[];mi=[];mats=[];matmap={};nv=nl=0
  for o in names:
   e=o.evaluated_get(dg);me=e.to_mesh();a=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',a);a=a.reshape(-1,3);T=np.array(inv@o.matrix_world if inv else o.matrix_world,dtype=np.float32);verts.append(a@T[:3,:3].T+T[:3,3]);ll=np.empty(len(me.loops),dtype=np.int32);me.loops.foreach_get('vertex_index',ll);loops.append(ll+nv);ss=np.empty(len(me.polygons),dtype=np.int32);tt=ss.copy();mm=ss.copy();me.polygons.foreach_get('loop_start',ss);me.polygons.foreach_get('loop_total',tt);me.polygons.foreach_get('material_index',mm);starts.append(ss+nl);totals.append(tt);lut=[]
   for slot in o.material_slots:
    mat=slot.material
    key=mat.name if mat else None
    if key not in matmap:matmap[key]=len(mats);mats.append(mat)
    lut.append(matmap[key])
   if not lut:
    if None not in matmap:matmap[None]=len(mats);mats.append(None)
    lut=[matmap[None]]
   mi.append(np.array(lut)[np.minimum(mm,len(lut)-1)]);nv+=len(me.vertices);nl+=len(me.loops);e.to_mesh_clear();o.hide_render=True
  me=bpy.data.meshes.new('REVIEW_BATCH_'+str(anchor));me.vertices.add(nv);me.vertices.foreach_set('co',np.concatenate(verts).ravel());me.loops.add(nl);me.loops.foreach_set('vertex_index',np.concatenate(loops));me.polygons.add(sum(len(a)for a in starts));me.polygons.foreach_set('loop_start',np.concatenate(starts));me.polygons.foreach_set('loop_total',np.concatenate(totals));me.polygons.foreach_set('material_index',np.concatenate(mi))
  for mat in mats:me.materials.append(mat)
  me.update();ob=bpy.data.objects.new(me.name,me);s.collection.objects.link(ob);ob.parent=parent;counts.append(dict(anchor=anchor,objects=len(names),vertices=nv))
 (R/'review/render-proxy.json').write_text(json.dumps(dict(groups=counts,excluded_dynamic=excluded,policy='In-memory rigid mesh consolidation only. Original file never saved.'),indent=2));print('BATCHED',counts,flush=True)
frames=[0,110,240,390,570,740,920,989] if 'sample' in args else range(990)
if 'animation' in args:
 s.render.use_persistent_data=True;s.render.filepath=str(R/'frames'/'f');s.frame_start=0;s.frame_end=989;s.frame_step=1
 if 'bench' in args:s.frame_end=29
 def done(scene,*rest):print('ANIM_FRAME',scene.frame_current,time.perf_counter(),flush=True)
 bpy.app.handlers.render_post.append(done);bpy.ops.render.render(animation=True)
 assert sha(source)==digest
 print('SOURCE_UNMODIFIED',digest,flush=True);sys.exit(0)
times=[]
for f in frames:
 dest=R/'frames'/f'f{f:04}.png'
 if 'batch' in args and 'sample' in args:dest=R/'review'/f'batch-f{f:04}.png'
 if dest.exists():continue
 s.frame_set(f);s.render.filepath=str(dest);t=time.perf_counter();bpy.ops.render.render(write_still=True);times.append(dict(frame=f,seconds=time.perf_counter()-t));print('DONE',f,times[-1]['seconds'],flush=True)
 (R/'review/render-timings.json').write_text(json.dumps(times,indent=2))
s.frame_set(saved)
assert sha(source)==digest
print('SOURCE_UNMODIFIED',digest,flush=True)
