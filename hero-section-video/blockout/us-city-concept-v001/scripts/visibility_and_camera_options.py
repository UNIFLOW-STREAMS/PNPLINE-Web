"""Read-only visibility audit and unsaved diagnostic camera alternatives."""
import bpy,json,math,hashlib,sys
from pathlib import Path
from mathutils import Vector,Matrix
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;file=Path(bpy.data.filepath)
def observed(name):
 o=s.objects[name];dg=bpy.context.evaluated_depsgraph_get();p=o.matrix_world@Vector(tuple(sum(v.co[i] for v in o.data.vertices)/len(o.data.vertices) for i in range(3)))
 uv=world_to_camera_view(s,s.camera,p);origin=s.camera.matrix_world.translation;direction=p-origin
 hit,loc,normal,index,obj,matrix=s.ray_cast(dg,origin,direction.normalized(),distance=direction.length+.05)
 return {'uv':list(uv),'in_frame':0.03<uv.x<.97 and .03<uv.y<.97 and uv.z>0,'first_surface':obj.name if hit else None,'landmark_hit':bool(hit and obj.name.startswith('UC_LIBERTY'))}
rows=[]
for f in range(300,541):
 s.frame_set(f);points={part:observed('UC_LIBERTY_'+part) for part in ['FLAME','CROWN','ROBE']}
 rows.append({'frame':f,'parts':points,'all_keypoints_visible':all(v['in_frame'] and v['landmark_hit'] for v in points.values())})
runs=[];run=[]
for row in rows:
 if row['all_keypoints_visible']:run.append(row['frame'])
 elif run:runs.append(run);run=[]
if run:runs.append(run)
report={'file':str(file),'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'body_height':s.objects['UC_LIBERTY']['selected_body_height'],'reference_body_height':s.objects['UC_LIBERTY']['reference_body_height'],'continuous_keypoint_runs':[{'start':r[0],'middle':r[len(r)//2],'end':r[-1],'seconds':len(r)/12} for r in runs],'frames':rows,'caution':'Keypoint ray hits are only necessary evidence, not sufficient recognition of torch/crown/robe. Render and playback judgement separate.'}
(R/'review/visibility-audit.json').write_text(json.dumps(report,indent=2))
folder=R/'review/camera-options-final';folder.mkdir(exist_ok=False)
s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100;s.render.use_border=False;s.render.image_settings.file_format='PNG'
options=[];original_camera=s.camera
diag_data=original_camera.data.copy();diag_data.animation_data_clear()
diag_camera=bpy.data.objects.new('DIAGNOSTIC_UNSAVED_CAMERA',diag_data);s.collection.objects.link(diag_camera)
for f in [390,421,495]:
 s.camera=original_camera;s.frame_set(f);lens=original_camera.data.lens
 diag_camera.matrix_world=original_camera.matrix_world.copy();s.camera=diag_camera
 for ratio in [1.0,.55,.45]:
  s.camera.data.lens=lens*ratio;s.render.filepath=str(folder/f'f{f:04d}-lens-{ratio:.2f}.png');bpy.ops.render.render(write_still=True)
  assert abs(s.camera.data.lens-lens*ratio)<.0001,'Diagnostic lens was reset by original camera animation'
  options.append({'frame':f,'ratio':ratio,'original_lens':lens,'diagnostic_lens':s.camera.data.lens,'camera_position_and_orientation':'unchanged','applied_to_candidate':False})
 s.camera.data.lens=lens
s.camera=original_camera
(folder/'options.json').write_text(json.dumps({'options':options,'saved_blend':False,'status':'Diagnostic alternatives requiring user approval; no camera edits in candidate'},indent=2))
print('VISIBILITY_RUNS',report['continuous_keypoint_runs'])
