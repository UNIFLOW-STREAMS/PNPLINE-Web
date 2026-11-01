"""Merge the accepted CN harbor delta into the accepted 33s US master.

Source files are immutable. Existing US actions are never rewritten. Added CN
correction actions are evaluated through the original shared nonlinear clock.
"""
import hashlib
import json
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Matrix

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT.parent
REVIEW = ROOT / 'review'
sys.path.insert(0, str(BASE / 'pacing-33s-v001/scripts'))
sys.path.insert(0, str(ROOT / 'scripts'))
from timing import TimeMap

CN = BASE / 'cn-port-camera-v001/master-cn-port-camera-v001.blend'
US = BASE / 'port-densification-v001/pnpline-port-densification-v001.blend'
OUT = ROOT / 'pnpline-cn-us-integrated-v001.blend'
EXPECTED = {'cn':'19f68c0ccc16c18693df685b47d632d98dd1289cb4f19f744f11e1507e7e0864',
            'us':'3d011d3191df487a44bd96ddce803a436a5ca3f891f91b512550c52f91f001c8'}

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

assert sha(CN) == EXPECTED['cn'] and sha(US) == EXPECTED['us']
manifest = json.loads((REVIEW / 'geometry-manifest.json').read_text())
assert manifest['US_ocean_geometry_exact_baseline']
assert not manifest['new_object_name_collisions']
assert not manifest['cn_changed_common_materials']
clock = TimeMap()
CAMERA_SKIPPED = {'PORT_CAMERA_RETARGET', 'PORT_CAMERA_TARGET_RETARGET'}
CONFLICTS = {'CAM_MASTER','CAM_LOOK_TARGET','A01_CONTAINER','W01_NEW_PALLET'}
new_names = sorted(set(manifest['cn_added_objects']) - CAMERA_SKIPPED)

bpy.ops.wm.open_mainfile(filepath=str(CN))
scene = bpy.context.scene
scene.frame_set(0)
from camera_merge import capture_times, capture_cn, install_camera
camera_samples = capture_cn(scene, capture_times(clock))
scene.frame_set(0)
meshes = {n: scene.objects[n].data.name for n in ['CN_QUAY','EARTH_CONTINUOUS_OCEAN']}
payload = {scene.objects[n] for n in new_names}
payload.update(scene.objects[n].data for n in meshes)
cn_properties = {k: scene[k] for k in scene.keys() if k.startswith('cn_port')}
# A labelled dependency cannot accidentally be confused with an existing US ID.
dependencies = set()
for n in manifest['cn_external_object_dependencies']:
    obj = scene.objects[n]
    while obj:
        dependencies.add(obj)
        obj = obj.parent
for obj in dependencies:
    obj.name = '__CN_DEP__' + obj.name
payload_path = REVIEW / 'cn-payload.blend'
bpy.data.libraries.write(str(payload_path), payload, fake_user=True, compress=True)

bpy.ops.wm.open_mainfile(filepath=str(US))
scene = bpy.context.scene
scene.frame_set(0)
before_objects = set(bpy.data.objects)
before_materials = set(bpy.data.materials)
original_materials = {m.name:m for m in bpy.data.materials}
original_actions = set(bpy.data.actions)
original_meshes = set(bpy.data.meshes)
with bpy.data.libraries.load(str(payload_path), link=False) as (available, loaded):
    loaded.objects = list(new_names)
    loaded.meshes = list(meshes.values())
imported = dict(zip(new_names, loaded.objects))
donor_meshes = dict(zip(meshes.keys(), loaded.meshes))
collection = bpy.data.collections.new('CN_PORT_TERMINAL')
scene.collection.children.link(collection)
for name, obj in imported.items():
    assert obj is not None and obj.name == name, name
    collection.objects.link(obj)
    if obj.parent and obj.parent.name.startswith('__CN_DEP__'):
        inverse = obj.matrix_parent_inverse.copy()
        obj.parent = scene.objects[obj.parent.name[len('__CN_DEP__'):]]
        obj.matrix_parent_inverse = inverse

# Canonicalize unchanged source materials; PORT materials are new named assets.
for mesh in set(bpy.data.meshes) - original_meshes:
    for i, material in enumerate(mesh.materials):
        if material and material not in before_materials:
            name = material.name
            stem = name.rsplit('.',1)[0] if name.rsplit('.',1)[-1].isdigit() else name
            if stem in original_materials:
                mesh.materials[i] = original_materials[stem]

# Transfer source-only static/parent edits after the audit resolved each field.
changed = []
for name, delta in manifest['cn_common_deltas'].items():
    if name in CONFLICTS:
        continue
    obj = scene.objects[name]
    values = delta['cn']
    assert set(values) <= {'parent','basis','parent_inverse','geometry','materials',
                            'hide_render','hide_viewport'}, (name,values.keys())
    inverse = obj.matrix_parent_inverse.copy()
    if 'parent' in values:
        obj.parent = scene.objects[values['parent']] if values['parent'] else None
        obj.matrix_parent_inverse = inverse
    if 'basis' in values:
        obj.matrix_basis = Matrix(values['basis'])
    if 'parent_inverse' in values:
        obj.matrix_parent_inverse = Matrix(values['parent_inverse'])
    if 'geometry' in values:
        obj.data = donor_meshes[name]
    for field in ['hide_render','hide_viewport']:
        if field in values:
            setattr(obj, field, values[field])
    changed.append(name)

# Preserve the US curvature carrier/action, but leave its tractor/trailer alone.
# The clone evaluates C(t); the new parent evaluates H(t), giving H*C*local.
carrier = scene.objects['CV_CARRIER_WORLD']
assert carrier.parent is None and not carrier.constraints
wrapper = carrier.copy()
wrapper.name = 'INTEGRATED_CN_CARRIER'
collection.objects.link(wrapper)
wrapper.parent = scene.objects['PORT_BERTH_PLACEMENT']
wrapper.matrix_parent_inverse = Matrix.Identity(4)
for name in ['A01_CONTAINER','W01_NEW_PALLET']:
    obj = scene.objects[name]
    assert obj.parent == carrier
    inverse = obj.matrix_parent_inverse.copy()
    obj.parent = wrapper
    obj.matrix_parent_inverse = inverse
    changed.append(name)

# Only newly imported actions use the old CN clock. All US action datablocks
# remain bit-for-bit intact, including those shared by the carrier clone.
grid = np.arange(0, 989.00001, .125)
source_grid = [clock.source(float(f)) for f in grid]
retimed = []
for action in set(bpy.data.actions) - original_actions:
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for fc in bag.fcurves:
                    assert not fc.modifiers and not fc.sampled_points
                    values = np.array([fc.evaluate(f) for f in source_grid])
                    keep = np.ones(len(grid), dtype=bool)
                    keep[1:-1] = (values[1:-1] != values[:-2]) | (values[1:-1] != values[2:])
                    coords = np.column_stack((grid[keep], values[keep])).astype(np.float32).ravel()
                    fc.keyframe_points.clear()
                    fc.keyframe_points.add(int(keep.sum()))
                    fc.keyframe_points.foreach_set('co', coords)
                    for key in fc.keyframe_points:
                        key.interpolation = 'LINEAR'
                    fc.update()
    retimed.append(action.name)

# Loaded parent dependencies have been redirected to the accepted US objects.
for obj in set(bpy.data.objects) - before_objects - set(imported.values()) - {wrapper}:
    assert obj.name.startswith('__CN_DEP__'), obj.name
    assert not any(o.parent == obj for o in imported.values())
    bpy.data.objects.remove(obj, do_unlink=True)

camera_report = install_camera(scene, camera_samples, clock)
for key, value in cn_properties.items():
    scene[key] = value
scene['integrated_version'] = 'cn-us-integrated-v001'
scene['integrated_US_source_sha256'] = EXPECTED['us']
scene['integrated_CN_source_sha256'] = EXPECTED['cn']
scene['integrated_clock'] = 'Original US 33s/30fps nonlinear clock; CN changes retimed through pacing TimeMap'
scene['cn_port_camera_revision'] = 'CN harbor staging joined to accepted US camera; see review/camera-merge.json'
assert (scene.frame_start,scene.frame_end,scene.render.fps) == (0,989,30)
scene.frame_set(132)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.region_3d.view_perspective = 'CAMERA'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT), compress=True)
report = {'file':str(OUT),'sha256':sha(OUT),'source_files':{'us':str(US),'cn':str(CN)},
          'source_sha256':EXPECTED,'base':'US','timing':{'fps':30,'start':0,'end':989,'duration_seconds':33},
          'new_CN_objects':new_names,'new_CN_count':len(new_names),
          'modified_original_objects':sorted(changed),'cargo_carrier_clone':wrapper.name,
          'new_actions_retimed':sorted(retimed),'original_US_actions_rewritten':False,
          'camera':camera_report,'status':'Pending independent preservation and media review'}
(ROOT/'delivery.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
(REVIEW/'build.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
assert sha(CN) == EXPECTED['cn'] and sha(US) == EXPECTED['us']
print('BUILT_INTEGRATED',report['sha256'],len(scene.objects),flush=True)
