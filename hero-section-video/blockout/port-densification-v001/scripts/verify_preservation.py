"""Read-only audit of additive port scenery against the accepted 30 fps city.

Run with Blender after build.json and the final blend have been written. All
accepted objects are protected; only new PT-prefixed objects are permitted.
Nothing is saved to either blend file; only review/preservation.json is written.
"""
import hashlib
import importlib.util
import json
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT.parent
EXPECTED_SOURCE = (
    BASE / "city-expansion-v002/pnpline-city-expansion-v002.blend"
).resolve()
EXPECTED_SOURCE_SHA256 = "61c980107793a30b12a8d6d61f341bd233c864346e247b5c5d90cfb72c19afff"
EXPECTED_OUTPUT = (ROOT / "pnpline-port-densification-v001.blend").resolve()
FRAME_RANGE = range(990)

helper_path = BASE / "curvature-rework-v001/scripts/audit_preservation.py"
spec = importlib.util.spec_from_file_location("city_expansion_preservation_helpers", helper_path)
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)


def file_sha256(path):
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def manifest_path(value):
    path = Path(value)
    return (path if path.is_absolute() else ROOT / path).resolve()


def matrix(value):
    return [list(row) for row in value]


def id_properties(owner):
    return {key: helper.scalar(owner[key]) for key in sorted(owner.keys())}


def camera_samples():
    scene = bpy.context.scene
    camera = scene.objects.get("CAM_MASTER")
    assert camera is not None and camera.type == "CAMERA", "CAM_MASTER is missing"
    samples = []
    for frame in FRAME_RANGE:
        scene.frame_set(frame)
        samples.append({
            "world": helper.digest(matrix(camera.matrix_world)),
            "local": helper.digest(matrix(camera.matrix_local)),
            "basis": helper.digest(matrix(camera.matrix_basis)),
            "transform_channels": helper.digest({
                "location": list(camera.location),
                "rotation_mode": camera.rotation_mode,
                "rotation_euler": list(camera.rotation_euler),
                "rotation_quaternion": list(camera.rotation_quaternion),
                "rotation_axis_angle": list(camera.rotation_axis_angle),
                "scale": list(camera.scale),
                "delta_location": list(camera.delta_location),
                "delta_rotation_euler": list(camera.delta_rotation_euler),
                "delta_rotation_quaternion": list(camera.delta_rotation_quaternion),
                "delta_scale": list(camera.delta_scale),
            }),
            "data": helper.digest(helper.props(camera.data, ("animation_data",))),
            "lens": camera.data.lens,
        })
    return samples


def snapshot():
    result = helper.snap()
    scene = bpy.context.scene
    scene.frame_set(0)
    result["object_details"] = {}
    result["geometry_details"] = {}
    for obj in scene.objects:
        result["object_details"][obj.name] = helper.digest({
            "data": obj.data.name if obj.data else None,
            "parent_type": obj.parent_type,
            "parent_bone": obj.parent_bone,
            "world": matrix(obj.matrix_world),
            "local": matrix(obj.matrix_local),
            "basis": matrix(obj.matrix_basis),
            "rotation_mode": obj.rotation_mode,
            "hide_select": obj.hide_select,
            "hide_get": obj.hide_get(),
            "collections": sorted(collection.name for collection in obj.users_collection),
            "custom_properties": id_properties(obj),
            "action_name": obj.animation_data.action.name
            if obj.animation_data and obj.animation_data.action else None,
            "material_names": [slot.material.name if slot.material else None
                               for slot in obj.material_slots],
        })
        if obj.type == "MESH":
            mesh = obj.data
            result["geometry_details"][obj.name] = helper.digest({
                "edges": [list(edge.vertices) for edge in mesh.edges],
                "vertex_groups": [(group.name, group.lock_weight) for group in obj.vertex_groups],
                "weights": [[(group.group, group.weight) for group in vertex.groups]
                            for vertex in mesh.vertices],
                "uv_layers": [(layer.name, [list(loop.uv) for loop in layer.data])
                              for layer in mesh.uv_layers],
                "shape_keys": None if mesh.shape_keys is None else {
                    "name": mesh.shape_keys.name,
                    "use_relative": mesh.shape_keys.use_relative,
                    "keys": [(key.name, key.value, [list(point.co) for point in key.data])
                             for key in mesh.shape_keys.key_blocks],
                    "action": helper.action(mesh.shape_keys.animation_data.action)
                    if mesh.shape_keys.animation_data else None,
                },
            })
        elif obj.type in {"CURVE", "SURFACE"}:
            result["geometry_details"][obj.name] = helper.digest([
                {
                    "props": helper.props(spline),
                    "points": [helper.props(point) for point in spline.points],
                    "bezier_points": [helper.props(point) for point in spline.bezier_points],
                }
                for spline in obj.data.splines
            ])
    result["all_actions"] = {action.name: helper.action(action) for action in bpy.data.actions}
    result["all_materials"] = {
        material.name: helper.digest(helper.node_data(material))
        for material in bpy.data.materials
    }
    result["camera_samples"] = camera_samples()
    return result


def changed_originals(before, after, removed=()):
    excluded = set(removed)
    return sorted(name for name, signature in before.items()
                  if name not in excluded and after.get(name) != signature)


def main():
    manifest = json.loads((ROOT / "review/build.json").read_text(encoding="utf-8"))
    source = manifest_path(manifest["source"])
    output = manifest_path(manifest["output"])
    removed = set(manifest["removed"])
    assert source == EXPECTED_SOURCE, f"Unexpected source: {source}"
    assert output == EXPECTED_OUTPUT, f"Unexpected candidate: {output}"
    assert source != output, "Candidate must be separate from the immutable source"
    assert manifest["source_sha256"] == EXPECTED_SOURCE_SHA256, "Manifest source hash differs"
    assert file_sha256(source) == EXPECTED_SOURCE_SHA256, "Accepted source changed on disk"
    assert not removed, \
        "No accepted source objects may be removed"
    assert output.is_file(), "Build the final candidate before running this audit"

    bpy.ops.wm.open_mainfile(filepath=str(output))
    after = snapshot()
    bpy.ops.wm.open_mainfile(filepath=str(source))
    before = snapshot()
    original_names = set(before["objects"])
    candidate_names = set(after["objects"])
    added = candidate_names - original_names
    actual_removed = original_names - candidate_names
    differences = {
        "unknown_allowed_removals": sorted(removed - original_names),
        "removals_not_in_manifest": sorted(actual_removed - removed),
        "manifest_removals_still_present": sorted(removed & candidate_names),
        "new_objects_without_pt_prefix": sorted(name for name in added if not name.startswith("PT_")),
    }
    for key in ("objects", "object_details", "geometry", "geometry_details", "actions"):
        differences[key] = changed_originals(before[key], after[key], removed)
    for key in ("all_actions", "all_materials"):
        differences[key] = changed_originals(before[key], after[key])
    for key in ("early_camera", "world", "timeline", "camera", "view"):
        differences[key] = before[key] != after[key]
    sample_fields = ("world", "local", "basis", "transform_channels", "data", "lens")
    for field in sample_fields:
        differences[f"camera_{field}_frames"] = [
            frame for frame in FRAME_RANGE
            if before["camera_samples"][frame][field] != after["camera_samples"][frame][field]
        ]
    differences["expected_output_timing"] = after["timeline"][:4] != [0, 989, 30, 1.0]
    report = {
        "source": str(source),
        "source_sha256": EXPECTED_SOURCE_SHA256,
        "output": str(output),
        "output_sha256": file_sha256(output),
        "protected_original_objects": len(original_names - removed),
        "allowed_removed_objects": sorted(removed),
        "added_object_count": len(added),
        "protected_action_count": len(before["all_actions"]),
        "protected_material_count": len(before["all_materials"]),
        "camera_sample_count": len(FRAME_RANGE),
        "camera_frame_range": [0, 989],
        "exact_camera_comparison": True,
        "differences": differences,
        "passed": not any(bool(value) for value in differences.values()),
        "scope": "Original data and animation preservation; spatial placement and visual quality require separate review.",
    }
    (ROOT / "review/preservation.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    print(json.dumps({
        "passed": report["passed"],
        "protected_objects": report["protected_original_objects"],
        "new_objects": len(added),
        "removed_objects": len(removed),
        "exact_camera_frames": len(FRAME_RANGE),
        "difference_counts": {key: len(value) if isinstance(value, list) else int(value)
                              for key, value in differences.items()},
    }))
    assert report["passed"], "Preservation failed; see review/preservation.json"


if __name__ == "__main__":
    main()
