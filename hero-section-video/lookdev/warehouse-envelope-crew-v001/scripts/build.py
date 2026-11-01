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
import hashlib
sys.path.insert(0,str(R/'scripts'))
import crew,envelope
from shipkit import Parts
def digest(p):
 with open(p,'rb') as fp:return hashlib.file_digest(fp,'sha256').hexdigest()
record=json.loads((R.parent/'latest-lookdev.json').read_text())
assert digest(bpy.data.filepath)==record['sha256']==digest(record['versioned_copy'])
opened=S.frame_current;S.frame_set(0)
def group(n):
 c=bpy.data.collections.new(n);S.collection.children.link(c);return c
wall=group('Warehouse | weather envelope')
fig=group('Warehouse | PNPLINE miniature staff')
shell=envelope.build_shell(S,U,wall,sphere)
# The original white-on-white LINE vanishes once the facade is closed.
# Change only the sign substrate, not the supplied wordmark or its two brand colours.
back=S.objects['WH_LOGO_BACKPLATE']
back.material_slots[0].link='OBJECT';back.material_slots[0].material=bpy.data.materials['WHE | Powder coated graphite']
curves=json.loads((R.parent/'container-ship-v001/scripts/wordmark.json').read_text())
M=crew.mats();bodies={}
names={'Pick':'CH_PICKER','Pack':'CH_PACKER','Load':'CH_LOADER'}
removed=[]
for role,name in names.items():
 root=S.objects[name]
 old=[o for o in root.children if o.name.startswith(name) and o.type=='MESH'];assert len(old)==4
 for o in old:removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
 base=crew.empty('Figure '+role+' | surface anchor',root,fig)
 if role!='Load':
  pt=np.array([52.,31.05,1.86] if role=='Pick' else [55.36,31.52,1.86]);a=Matrix(basis(sphere,pt).tolist()).to_4x4();a.translation=Vector(sphere(pt))
  base.matrix_parent_inverse=root.matrix_world.inverted()@U.matrix_world@a@(Matrix.Rotation(1.04,4,'Z') if role=='Pack' else Matrix.Identity(4))
 bodies[role]=crew.build_figure(role,base,fig,M,curves)
 if role!='Load':crew.configure(role,bodies[role])
# Existing independent reach actions are kept as invisible transform carriers. The tray still
# moves with the original cargo contact; the two arm endpoint channels drive the new gloved hands.
for i in (0,1):
 o=S.objects['CH_LOAD_ARM_'+str(i)]
 o.data=bpy.data.meshes.new('Contact transform (no display geometry) '+str(i))
 q=o.modifiers
 for m in list(q):q.remove(m)
support=S.objects['CH_LOAD_SUPPORT'];p=Parts('Transfer cradle',None,fig)
p.box((0,0,0),(.60,.65,.058),M['Navy canvas'])
for x in (-.281,.281):p.box((x,0,.01),(.035,.645,.06),M['Buckle'])
for y in (-.323,.323):p.box((0,y,.003),(.57,.018,.049),M['Ocean twill'])
tmp=p.done();support.data=tmp.data;bpy.data.objects.remove(tmp,do_unlink=True)
s=S;contact_frames=[];lastvals=None;changes=[];lasttime=None
# Evaluate original animated contact matrices every frame; key only segments where the local relation changes.
tracks=[]
for f in range(990):
 s.frame_set(f)
 inv=s.objects['CH_LOADER'].matrix_world.inverted()
 q=inv@support.matrix_world.translation
 h=[inv@(s.objects['CH_LOAD_ARM_'+str(i)].matrix_world@Vector((0,0,.5))) for i in (1,0)]
 tracks.append(np.array([list(q),list(h[0]),list(h[1])]))
tracks=np.asarray(tracks);d=np.max(abs(np.diff(tracks,axis=0)),axis=(1,2))
keys=np.unique(np.r_[0,np.where(d>5e-5)[0],np.where(d>5e-5)[0]+1,989]).astype(int)
for f in keys:
 q,h1,h2=tracks[f]
 objs=crew.configure('Load',bodies['Load'],(Vector(q),[Vector(h1),Vector(h2)]),int(f))
for o in fig.objects:
 if 'prev_quat' in o:del o['prev_quat']
 if o.animation_data and o.animation_data.action:
  act=o.animation_data.action;act.name='Crew pose | '+o.name
  for layer in act.layers:
   for strip in layer.strips:
    for cb in strip.channelbags:
     for fc in cb.fcurves:
      for k in fc.keyframe_points:k.interpolation='LINEAR'
# Mid-aisle bounce from the hooded strip luminaires; link to the local warehouse sphere.
for x in (39.2,46.4,54.0,61.5,66.2):
 pt=np.array([x,28.1,8.93]);rot=Matrix(basis(sphere,pt).tolist()).to_4x4()
 d=bpy.data.lights.new('Aisle diffuse practical','AREA');d.shape='RECTANGLE';d.size=3.1;d.size_y=1.0;d.energy=340;d.color=(.91,.96,1)
 o=bpy.data.objects.new('WHE | Packing aisle light '+str(x),d);wall.objects.link(o);o.parent=U;rot.translation=Vector(sphere(pt));o.matrix_basis=rot
s['warehouse_envelope_revision']='warehouse-envelope-crew-v001'
s.frame_set(opened);bpy.context.view_layer.update()
out=R/'pnpline-warehouse-envelope-crew-v001.blend'
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
(R/'previous-latest-lookdev.json').write_text(json.dumps(record,indent=2))
(R/'review/build.json').write_text(json.dumps(dict(source=record['file'],sha_source=record['sha256'],archived_source=record['versioned_copy'],output=str(out),sha_result=digest(out),roles=names,removed=removed,original_animated_hand_carriers=['CH_LOAD_ARM_0','CH_LOAD_ARM_1','CH_LOAD_SUPPORT'],facade= shell,pose_key_frames=keys.tolist(),frame_start=s.frame_start,frame_end=s.frame_end),indent=2))
print('CREW AND ENVELOPE SAVED',out,flush=True)

