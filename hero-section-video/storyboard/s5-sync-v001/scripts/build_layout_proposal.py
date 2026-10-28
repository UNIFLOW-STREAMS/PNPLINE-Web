"""Separate, bounded Stage2 rework proposal. Never writes the source master."""
import bpy, json, sys, hashlib
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];P=R/'layout-proposal-v001';P.mkdir(exist_ok=True)
source=Path(bpy.data.filepath);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(source)=='8c76f0e184bc742309cf66dcf9f3f5fa7072e02b54b58e6985a91ff1ae57b665'
s=bpy.context.scene;U=s.objects['US_FRAME'].matrix_world.copy();I=U.inverted();S=Matrix.Diagonal((1,-1,1,1));A=U@Matrix.Translation((0,18,0))@S@I
env=list(s.objects['US_FRAME'].children_recursive)
def animated(o):return bool(o.animation_data and o.animation_data.action) or bool(o.parent and animated(o.parent))
dynamic_env=[o for o in env if animated(o)];static_env=[o for o in env if not animated(o)]
roots=[o for o in s.objects if o.parent is None and o.animation_data and o.animation_data.action and o.name not in ['CAM_MASTER','CAM_LOOK_TARGET'] and not o.name.startswith('P01_')]
wheels=[o for o in s.objects if o.name.startswith('A03') and '_WHEEL_' in o.name]
frames=[i/4 for i in range(552*4,948*4+1)]
cache={o.name:[] for o in roots+dynamic_env};wheelstates={o.name:[] for o in wheels};wheellocations={o.name:[] for o in wheels};cameras=[]
for f in frames:
 s.frame_set(int(f),subframe=f%1)
 for o in roots+dynamic_env:cache[o.name].append(o.matrix_world.copy())
 for o in wheels:
  wheelstates[o.name].append(o.rotation_euler.copy());wheellocations[o.name].append(o.location.copy())
 cameras.append((I@s.camera.matrix_world.translation,I@s.objects['CAM_LOOK_TARGET'].matrix_world.translation,s.camera.data.lens,(I@s.objects['A03_TRAILER'].matrix_world).translation.x))
s.frame_set(648);envstates={o.name:o.matrix_world.copy() for o in env}
# Environment geography is genuinely rebuilt in 3D. Actors retain original meshes,
# readable lettering, positive scales and handedness; no render/image reflection.
for o in env:
 o.parent=None;o.animation_data_clear();o.matrix_world=A@envstates[o.name]@S
 if o.type=='MESH':
  o.data=o.data.copy();o.data.transform(S);o.data.flip_normals();o.data.update()
for o in roots+dynamic_env+wheels:o.animation_data_clear()
cam=s.camera;target=s.objects['CAM_LOOK_TARGET'];cam.animation_data_clear();cam.data.animation_data_clear();target.animation_data_clear()
def fc(o,path,index,values):
 # Create a channel once through supported bpy key insertion, then bulk fill it.
 o.keyframe_insert(data_path=path,index=-1 if path=='lens' else index,frame=frames[0])
 ad=o.animation_data;action=ad.action
 curves=action.layers[0].strips[0].channelbag(ad.action_slot).fcurves
 curve=next(c for c in curves if c.data_path==path and c.array_index==index)
 curve.keyframe_points.clear();curve.keyframe_points.add(len(values));curve.keyframe_points.foreach_set('co',[v for f,y in zip(frames,values) for v in (f,y)])
 for k in curve.keyframe_points:k.interpolation='LINEAR'
 curve.update()
def bake(o,matrices):
 o.rotation_mode='QUATERNION';ls=[];qs=[];sc=[];prev=None
 for m in matrices:
  l,q,z=m.decompose()
  if prev and q.dot(prev)<0:q.negate()
  prev=q.copy();ls.append(l);qs.append(q);sc.append(z)
 for path,arr,num in [('location',ls,3),('rotation_quaternion',qs,4),('scale',sc,3)]:
  for k in range(num):fc(o,path,k,[v[k] for v in arr])
for o in roots+dynamic_env:bake(o,[A@m@S for m in cache[o.name]])
for o in wheels:
 opposite=next(w for w in wheels if w.parent==o.parent and abs(wheellocations[w.name][0].x-wheellocations[o.name][0].x)<.001 and abs(wheellocations[w.name][0].y+wheellocations[o.name][0].y)<.001)
 for k in range(3):fc(o,'rotation_euler',k,[(-v[k] if k==2 else v[k]) for v in wheelstates[opposite.name]])
 for k in range(3):fc(o,'location',k,[(-v[k] if k==1 else v[k]) for v in wheellocations[opposite.name]])
def smooth(t):return t*t*t*(10+t*(-15+6*t))
def reflected(v):return Vector((v.x,18-v.y,v.z))
anchors=[(552,(18,29,16),(1,15,3.4),40),(576,(15,32,16),(0,13,3.3),38),(600,(1,30,14),(2,11,3),33),(624,(-13,15,10),(7,10,2.8),29)]
def catmull(f,k):
 j=next((j for j in range(len(anchors)-1) if f<=anchors[j+1][0]),len(anchors)-2);a=anchors[j];b=anchors[j+1];t=(f-a[0])/(b[0]-a[0])
 p0=Vector(anchors[max(0,j-1)][k]) if k<3 else anchors[max(0,j-1)][k];p1=Vector(a[k]) if k<3 else a[k];p2=Vector(b[k]) if k<3 else b[k];p3=Vector(anchors[min(len(anchors)-1,j+2)][k]) if k<3 else anchors[min(len(anchors)-1,j+2)][k]
 # Zero endpoint velocity at departure hold.
 m1=(p2-p0)/2 if j>0 else p2-p1;m2=(p3-p1)/2 if j+1<len(anchors)-1 else p2*0
 return p1*(2*t**3-3*t*t+1)+m1*(t**3-2*t*t+t)+p2*(-2*t**3+3*t*t)+m2*(t**3-t*t)
cm=[];tm=[];lenses=[]
for f,(origloc,origaim,origlens,x) in zip(frames,cameras):
 if f<624:loc=catmull(f,1);aim=catmull(f,2);lens=catmull(f,3)
 else:
  loc=Vector((-13+x,15,10));aim=Vector((7+x,10,2.8));lens=29
  if f>720:
   # Stay behind/on the sea side until clear of the final crane leg.
   w=smooth(min((f-720)/46,1));loc=loc.lerp(reflected(origloc),w);aim=aim.lerp(reflected(origaim),w);lens=lens*(1-w)+origlens*w
 q=U.to_quaternion()@(aim-loc).to_track_quat('-Z','Y');cm.append(Matrix.LocRotScale(U@loc,q,Vector((1,1,1))));tm.append(Matrix.Translation(U@aim));lenses.append(lens)
bake(cam,cm);bake(target,tm);fc(cam.data,'lens',0,lenses)
s.frame_start=552;s.frame_end=948;s.use_preview_range=True;s.frame_preview_start=552;s.frame_preview_end=948;s.frame_set(648)
s['proposal_status']='Separate layout/route proposal; final master adoption pending';s['valid_review_range']='552-948 ONLY; upstream S1-S3 and downstream S6-S7 not integrated';s['input_sha256']=sha(source)
s.render.engine='BLENDER_WORKBENCH';s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.use_border=False;s.render.use_crop_to_border=False
s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.background_type='WORLD';s.world.color=(.18,.18,.18)
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.region_3d.view_camera_zoom=0
out=P/'s4-s5-layout-proposal-v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out))
record={'source':str(source),'source_sha256':sha(source),'proposal':str(out),'proposal_sha256':sha(out),'builder_sha256':sha(__file__),'range':[552,948],'sample_step':.25,'geography':'US local y becomes 18-y; actors use proper rotations and unchanged meshes','camera':'New late-S4 orbit, rear departure framing, continuous blend to relocated S5 camera by f766','animated_roots':[o.name for o in roots],'flattened_environment':[o.name for o in env],'limitations':['Review range only; no upstream/downstream full-master continuity claim.','Scene is structural blockout; detailed ship/warehouse silhouettes are not recreated.'],'adoption':'pending user review'}
(P/'build-record.json').write_text(json.dumps(record,indent=2),encoding='utf8')
d=json.loads((R/'review-decisions.json').read_text(encoding='utf8'));d['layout_rework_authorization']={'answer':'승인: 별도 배치·동선 재작업 제안본 작성','scope':'late S4 and S5 cameras including before720; ship/crane/vehicle relative layout and departure direction; road/warehouse approach; original preserved; final adoption separate','source':'actual user reply in current conversation'};d['current_question']='Authorized proposal being built; final adoption pending';(R/'review-decisions.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
with (R/'progress.md').open('a',encoding='utf8') as h:h.write('\nUser explicitly approved separate layout/route proposal. Implemented bounded f552–948 proposal; original master read-only. Final adoption and upstream/downstream integration remain separate.\n')
print('PROPOSAL_SAVED',out,flush=True)
