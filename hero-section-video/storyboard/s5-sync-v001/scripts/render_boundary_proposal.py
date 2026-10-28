import bpy,sys,json,uuid,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));from contracts import digest
s=bpy.context.scene;U=s.objects['US_FRAME'].matrix_world.copy();I=U.inverted();cam=s.camera;tar=s.objects['CAM_LOOK_TARGET'];trial=json.loads((R/'review/s4-s5-recheck/solved-rear-framing.json').read_text())
out=R/'review/s4-s5-recheck'/('camera-only-'+uuid.uuid4().hex[:8]);out.mkdir();(out/'before').mkdir();(out/'after').mkdir()
s.render.engine='BLENDER_WORKBENCH';s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.use_border=False;s.render.use_crop_to_border=False
s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.background_type='WORLD';s.world.color=(.18,.18,.18)
original={}
for f in range(551,842):
 s.frame_set(f);original[f]={'loc':I@cam.matrix_world.translation,'aim':I@tar.matrix_world.translation,'lens':cam.data.lens,'q':cam.matrix_world.to_quaternion(),'truck':(I@s.objects['A03_TRAILER'].matrix_world).translation.x}
# A diagnostic, not an accepted fix: bounded camera-only comparison.
def smooth(t):return 6*t**5-15*t**4+10*t**3
def hermite(a,b,va,vb,t,d):
 # Quintic zero endpoint acceleration, with endpoint velocity constraints.
 return a*(1-10*t**3+15*t**4-6*t**5)+b*(10*t**3-15*t**4+6*t**5)+va*d*(t-6*t**3+8*t**4-3*t**5)+vb*d*(-4*t**3+7*t**4-3*t**5)
def propose(f):
 o=original[f];loc=Vector(trial['camera_us'])+Vector((o['truck'],0,0));aim=Vector(trial['aim_us'])+Vector((o['truck'],0,0));lens=trial['lens']
 if f<648:
  t=(f-552)/96
  for key,value in [('loc',loc),('aim',aim),('lens',lens)]:
   a=original[552][key];v=(original[553][key]-original[551][key])/2;new=hermite(a,value,v,v*0,t,96)
   if key=='loc':loc=new
   elif key=='aim':aim=new
   else:lens=new
 elif f>672:
  w=smooth(min((f-672)/138,1));loc=loc.lerp(o['loc'],w);aim=aim.lerp(o['aim'],w);lens=lens*(1-w)+o['lens']*w
 if f>=810:return o['loc'],o['aim'],o['lens']
 return loc,aim,lens
record={'status':'rendering','purpose':'diagnostic camera-only attempt; NOT accepted storyboard match or master revision','input_base_sha256':digest(bpy.data.filepath),'script_sha256':digest(__file__),'trial':trial,'scene':s.name,'camera':cam.name,'range':[552,840],'fps':s.render.fps,'proposed_channels':'CAM_MASTER position/rotation/lens and aim trajectory, f553-809; no source save','limitations':['Cannot restore exact storyboard spatial relationships/subject scale with this camera-only attempt.','User approval for protected f<=720 modification has not been requested; diagnostic renders only.'],'frames':[]}
(out/'record.json').write_text(json.dumps(record,indent=2),encoding='utf8')
cam.animation_data_clear();cam.data.animation_data_clear()
for f in range(552,841):
 s.frame_set(f);o=original[f];cam.location=U@o['loc'];cam.rotation_mode='QUATERNION';cam.rotation_quaternion=o['q'];cam.data.lens=o['lens'];bpy.context.view_layer.update()
 p=out/'before'/f'{f:04d}.png';s.render.filepath=str(p);bpy.ops.render.render(write_still=True)
 loc,aim,lens=propose(f);cam.location=U@loc;cam.rotation_quaternion=U.to_quaternion()@(aim-loc).to_track_quat('-Z','Y');cam.data.lens=lens;bpy.context.view_layer.update()
 q=out/'after'/f'{f:04d}.png';s.render.filepath=str(q);bpy.ops.render.render(write_still=True);assert (cam.matrix_world.translation-U@loc).length<.0001
 record['frames'].append({'frame':f,'before':str(p),'before_sha256':digest(p),'after':str(q),'after_sha256':digest(q),'camera_us':list(loc),'aim_us':list(aim),'lens':lens})
record['status']='complete';(out/'record.json').write_text(json.dumps(record,indent=2),encoding='utf8');(R/'review/s4-s5-recheck/camera-only-record.json').write_text(json.dumps(record,indent=2),encoding='utf8');print('PROPOSAL_DIAGNOSTIC',out,flush=True)
