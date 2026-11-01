import bpy,json,sys,hashlib
from pathlib import Path
r=Path(__file__).resolve().parents[1];s=bpy.context.scene
pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='OPTIX';pref.get_devices()
for d in pref.devices:d.use=d.type=='OPTIX'
s.render.engine='CYCLES';s.cycles.device='GPU' if any(d.use for d in pref.devices) else 'CPU'
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.image_settings.color_depth='8'
s.cycles.samples=24;s.cycles.use_denoising=True;s.render.resolution_percentage=100
s.render.resolution_x=1280;s.render.resolution_y=720
tree=s.objects['EARTH_CONTINUOUS_OCEAN'].active_material.node_tree
assert all(bpy.data.images[name].packed_file for name in ['Wake - restrained cargo shoulders','Shelf - coastal falloff'])
assert all(name not in s.objects for name in ['SHIP_ROUTE','WAKE_RIBBON_0','WAKE_RIBBON_1'])
if 'clip' in sys.argv:
 s.cycles.samples=10;s.render.resolution_x=768;s.render.resolution_y=432
 s.render.use_persistent_data=True
 for f in range(199,244):
  s.frame_set(f);s.render.filepath=str(r/'review/frames'/f'{f:04d}.png');bpy.ops.render.render(write_still=True)
else:
 # Compare every crossing matrix to the checksummed source sample set.
 samples={}
 for f in range(150,318):
  s.frame_set(f);samples[f]=[[list(row) for row in s.objects[n].matrix_world] for n in ['A02_SHIP','CAM_MASTER']]+[s.camera.data.lens]
 motion=hashlib.sha256(json.dumps(samples).encode()).hexdigest()
 assert motion==(r.parent/'pacific-islands-v001/review/motion.sha').read_text()
 states={}
 for f in [0,130,201,225,245,340,410,989]:
  s.frame_set(f);states[f]=tree.nodes['Propeller wash strength'].outputs[0].default_value
 assert states[0]==states[989]==states[410]==0 and states[225]>.8
 (r/'review/checks.json').write_text(json.dumps(dict(motion_sha=motion,wash=states,packed_maps=2),indent=2))
 for f in [201,225,245]:
  s.frame_set(f);s.render.filepath=str(r/'review'/f'ocean-{f}.png');bpy.ops.render.render(write_still=True)




