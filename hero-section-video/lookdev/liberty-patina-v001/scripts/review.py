import bpy,json,sys,math,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
r=Path(__file__).resolve().parents[1]
scene=bpy.context.scene
body=bpy.data.objects['UC_LIBERTY_BODY']
def freeze():
 lib=body.parent
 def sign(o):
  return [o.name,list(map(list,o.matrix_world)),[tuple(v.co) for v in o.data.vertices], [list(f.vertices) for f in o.data.polygons], [m.name for m in o.data.materials]]
 return hashlib.sha256(json.dumps([sign(o) for o in sorted(lib.children,key=lambda o:o.name) if o.type=='MESH']).encode()).hexdigest()
def audit():
 desc=set(body.children)
 return dict(base_hash=freeze(),siblings=len(body.parent.children)-1,external_objects=sorted(o.name for o in bpy.data.objects if o not in desc),camera=scene.camera.name,actions=sorted((a.name,list(a.frame_range)) for a in bpy.data.actions),frame=[scene.frame_start,scene.frame_end,scene.render.fps])
old=json.loads((r/'previous-latest-lookdev.json').read_text())
test=audit()
if 'baseline' in sys.argv:
 (r/'review/baseline.json').write_text(json.dumps(test));sys.exit(0)
base=json.loads((r/'review/baseline.json').read_text())
assert json.loads(json.dumps(test))==base
assert bpy.data.images['Liberty | isolated lithograph inks (sRGB)'].packed_file
(r/'review/checks.json').write_text(json.dumps(dict(pedestal_island_signature=test['base_hash'],base_objects=test['siblings'],figure_parts=len(body.children),other_scene_objects=len(test['external_objects']),camera=test['camera'],timing=test['frame'],packed_texture=True),indent=2))
scene.frame_set(360)
ref=body.matrix_world.copy()
pref=bpy.context.preferences.addons['cycles'].preferences
pref.compute_device_type='OPTIX';pref.get_devices()
for d in pref.devices:d.use=d.type=='OPTIX'
scene.render.engine='CYCLES';scene.cycles.device='GPU' if any(d.use for d in pref.devices) else 'CPU'
scene.cycles.samples=18;scene.cycles.use_denoising=True;scene.render.resolution_x=640;scene.render.resolution_y=850;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
cam=bpy.data.objects.new('Inspection',bpy.data.cameras.new('Inspection'));scene.collection.objects.link(cam);scene.camera=cam;cam.data.type='ORTHO'
for name,delta in [('front',(0,-23,1.5)),('quarter',(11,-22,6.2))]:
 aim=Vector((0,0,3.28));delta=Vector(delta);cam.matrix_world=ref@Matrix.Translation(aim+delta)@(-delta).to_track_quat('-Z','Y').to_matrix().to_4x4();cam.data.ortho_scale=12.05*ref.to_scale().x
 scene.render.filepath=str(r/'review'/f'{name}.png');bpy.ops.render.render(write_still=True)
