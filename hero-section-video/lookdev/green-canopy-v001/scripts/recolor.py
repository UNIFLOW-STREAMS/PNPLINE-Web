"""Use the established foliage palette on both faceted street tree assets."""
import bpy
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
scene = bpy.context.scene
source = Path(bpy.data.filepath)
pointer = root.parent / 'latest-lookdev.json'
record = json.loads(pointer.read_text())

def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

assert digest(source) == record['sha256']
assignments = {'Broad crown': 'DSP_leaf1', 'Oval crown': 'DSP_leaf2'}
counts = {}
for mesh_name, material_name in assignments.items():
    mesh = bpy.data.meshes[mesh_name]
    material = bpy.data.materials[material_name]
    assert mesh.materials[1].name == 'Street tree | warm porcelain'
    mesh.materials[1] = material
    counts[mesh_name] = sum(obj.data == mesh for obj in scene.objects if obj.type == 'MESH')
assert sum(counts.values()) == 1163

output = root / 'pnpline-green-canopy-v001.blend'
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(output), compress=True)
report = {
    'source': str(source),
    'source_sha256': record['sha256'],
    'versioned_source': record['versioned_copy'],
    'output': str(output),
    'sha256': digest(output),
    'mesh_material_assignments': assignments,
    'tree_counts': counts,
    'only_intended_edits': 'Two existing canopy mesh material slots reassigned to the original DSP green foliage materials.',
}
(root / 'delivery.json').write_text(json.dumps(report, indent=2))
(root / 'previous-latest-lookdev.json').write_text(json.dumps(record, indent=2))

# Review camera reproduces the preceding waterfront proof.
from mathutils import Matrix, Vector
prefs = bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type = 'OPTIX'
prefs.get_devices()
for device in prefs.devices:
    device.use = device.type == 'OPTIX'
scene.render.engine = 'CYCLES'
scene.cycles.device = 'GPU' if any(d.use for d in prefs.devices) else 'CPU'
scene.cycles.samples = 40
scene.cycles.use_denoising = True
scene.cycles.adaptive_threshold = .03
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.frame_set(890)
camera = bpy.data.objects.new('Green canopy proof', bpy.data.cameras.new('Green canopy proof'))
scene.collection.objects.link(camera)
origin = Vector((-5, -9, 6))
aim = Vector((0, 0, 1.4))
rotation = (aim - origin).to_track_quat('-Z', 'Y')
camera.matrix_world = scene.objects['DSP_TREE_042'].matrix_world @ Matrix.Translation(origin) @ rotation.to_matrix().to_4x4()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 13
camera.data.clip_end = 1500
scene.camera = camera
scene.render.filepath = str(root / 'review/waterfront-green.png')
bpy.ops.render.render(write_still=True)
print(json.dumps(report))
