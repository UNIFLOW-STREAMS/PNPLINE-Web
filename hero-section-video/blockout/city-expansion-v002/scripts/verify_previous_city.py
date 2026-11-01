"""Verify that v002 preserves all 151 accepted v001 building assemblies.

Run after pnpline-city-expansion-v002.blend exists. This audit only reads both
blend files and writes review/previous-city-preservation.json. The separate
verify_preservation.py owns the original scene/camera preservation audit.
"""
import hashlib
import importlib.util
import json
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[1]
PREVIOUS = ROOT.parent / "city-expansion-v001"
BASELINE = PREVIOUS / "pnpline-city-expansion-v001.blend"
BASELINE_SHA256 = "48f6a6f7c99f34b42d1cb7b71930da56f07f52a2324f73ee513045e3c504bbb4"
CANDIDATE = ROOT / "pnpline-city-expansion-v002.blend"
REPORT = ROOT / "review/previous-city-preservation.json"
EXPECTED_BUILDINGS = 151
SAMPLE_FRAMES = (0, 349, 497, 989)

spec = importlib.util.spec_from_file_location(
    "previous_city_audit_helpers",
    ROOT.parent / "curvature-rework-v001/scripts/audit_preservation.py",
)
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)


def sha256(path):
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def matrix(value):
    return [list(row) for row in value]


def collect_building_objects(building_names):
    """Determine membership from accepted names, never from mutable owner tags."""
    scene = bpy.context.scene
    groups = {}
    for name in building_names:
        root_name = name + "_ROOT"
        foundation_name = name + "_FOUNDATION"
        root = scene.objects.get(root_name)
        foundation = scene.objects.get(foundation_name)
        assert root is not None, f"Baseline building root missing: {root_name}"
        assert foundation is not None, f"Baseline foundation missing: {foundation_name}"
        children = [obj for obj in scene.objects if obj.name.startswith(name + "__")]
        assert children, f"Baseline architecture missing: {name}"
        assert all(obj.parent == root for obj in children), f"Unexpected baseline hierarchy: {name}"
        groups[name] = sorted([root_name, foundation_name] + [obj.name for obj in children])
    return groups


def mesh_signature(mesh):
    """Hash actual modeled shape/topology/shading, excluding ID bookkeeping."""
    return helper.digest({
        "vertices": [list(vertex.co) for vertex in mesh.vertices],
        "edges": [list(edge.vertices) for edge in mesh.edges],
        "polygons": [(list(face.vertices), face.material_index, face.use_smooth)
                     for face in mesh.polygons],
        "loops": [(loop.vertex_index, loop.edge_index) for loop in mesh.loops],
        "uv_layers": [(layer.name, [list(loop.uv) for loop in layer.data])
                      for layer in mesh.uv_layers],
        "shape_keys": None if mesh.shape_keys is None else {
            "use_relative": mesh.shape_keys.use_relative,
            "keys": [(key.name, key.value, [list(point.co) for point in key.data])
                     for key in mesh.shape_keys.key_blocks],
        },
    })


def snapshot(protected_names):
    scene = bpy.context.scene
    scene.frame_set(0)
    result = {"objects": {}, "data": {}, "geometry": {}, "materials": {}, "world": {}}
    for name in protected_names:
        obj = scene.objects.get(name)
        if obj is None:
            continue
        result["objects"][name] = helper.digest({
            "type": obj.type,
            "parent": obj.parent.name if obj.parent else None,
            "parent_type": obj.parent_type,
            "parent_bone": obj.parent_bone,
            "matrix_parent_inverse": matrix(obj.matrix_parent_inverse),
            "matrix_basis": matrix(obj.matrix_basis),
            "matrix_local": matrix(obj.matrix_local),
            "rotation_mode": obj.rotation_mode,
            "visibility": [obj.hide_render, obj.hide_viewport, obj.hide_get()],
            "visible_shadow": obj.visible_shadow,
            "constraints": [helper.props(constraint) for constraint in obj.constraints],
            "modifiers": [helper.props(modifier) for modifier in obj.modifiers],
            "animation": helper.action(obj.animation_data.action) if obj.animation_data else None,
        })
        result["data"][name] = helper.digest({
            "data_name": obj.data.name if obj.data else None,
            "material_slots": [(slot.link, slot.material.name if slot.material else None)
                               for slot in obj.material_slots],
            "active_material_index": obj.active_material_index,
            "vertex_groups": [(group.name, group.lock_weight) for group in obj.vertex_groups],
            "data_animation": helper.action(obj.data.animation_data.action)
            if obj.data and obj.data.animation_data else None,
        })
        if obj.type == "MESH":
            result["geometry"][name] = mesh_signature(obj.data)
        else:
            assert obj.type == "EMPTY", f"Unexpected protected object type: {name}: {obj.type}"
        for slot in obj.material_slots:
            material = slot.material
            if material and material.name not in result["materials"]:
                result["materials"][material.name] = helper.digest(helper.node_data(material))
    for frame in SAMPLE_FRAMES:
        scene.frame_set(frame)
        result["world"][frame] = {
            name: helper.digest(matrix(scene.objects[name].matrix_world))
            for name in protected_names if scene.objects.get(name) is not None
        }
    result["all_object_names"] = set(scene.objects.keys())
    return result


def changed(before, after):
    return sorted(name for name, signature in before.items() if after.get(name) != signature)


def main():
    assert BASELINE.is_file(), f"Accepted baseline is missing: {BASELINE}"
    assert sha256(BASELINE) == BASELINE_SHA256, "Accepted v001 baseline hash does not match"
    assert CANDIDATE.is_file(), "Build the final v002 blend before running this audit"
    manifest = json.loads((PREVIOUS / "review/build.json").read_text(encoding="utf-8"))
    names = [building["name"] for building in manifest["buildings"]]
    assert len(names) == len(set(names)) == EXPECTED_BUILDINGS, \
        f"Expected {EXPECTED_BUILDINGS} unique accepted buildings"
    assert all(name.startswith("CE_") for name in names)

    bpy.ops.wm.open_mainfile(filepath=str(BASELINE))
    groups = collect_building_objects(names)
    protected = sorted({name for members in groups.values() for name in members})
    before = snapshot(protected)
    bpy.ops.wm.open_mainfile(filepath=str(CANDIDATE))
    after = snapshot(protected)
    added = after["all_object_names"] - before["all_object_names"]
    differences = {
        "missing_previous_objects": sorted(set(protected) - after["all_object_names"]),
        "new_objects_without_ce_prefix": sorted(name for name in added if not name.startswith("CE_")),
    }
    for key in ("objects", "data", "geometry", "materials"):
        differences[key] = changed(before[key], after[key])
    world_differences = {
        str(frame): changed(before["world"][frame], after["world"][frame])
        for frame in SAMPLE_FRAMES
    }
    differences["world_transforms"] = sorted({
        name for changed_names in world_differences.values() for name in changed_names
    })
    changed_objects = set().union(*(
        set(differences[key]) for key in ("missing_previous_objects", "objects", "data", "geometry", "world_transforms")
    ))
    affected_buildings = sorted(name for name, members in groups.items()
                                if changed_objects.intersection(members))
    report = {
        "baseline": str(BASELINE.resolve()),
        "baseline_sha256": BASELINE_SHA256,
        "candidate": str(CANDIDATE.resolve()),
        "candidate_sha256": sha256(CANDIDATE),
        "previous_building_count": len(groups),
        "protected_object_count": len(protected),
        "protected_mesh_count": len(before["geometry"]),
        "protected_material_count": len(before["materials"]),
        "added_object_count": len(added),
        "world_sample_frames": list(SAMPLE_FRAMES),
        "exact_geometry_and_transform_comparison": True,
        "ignored": ["custom production metadata including ce_owner", "collection membership", "material ID user counts"],
        "differences": differences,
        "world_differences_by_frame": world_differences,
        "affected_buildings": affected_buildings,
        "passed": not any(differences.values()),
        "scope": "All 151 v001 building roots, architecture batches and foundations; the separate original-scene audit protects the camera and earlier animation.",
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({
        "passed": report["passed"],
        "previous_buildings": len(groups),
        "protected_objects": len(protected),
        "added_objects": len(added),
        "affected_buildings": len(affected_buildings),
        "difference_counts": {key: len(value) for key, value in differences.items()},
        "report": str(REPORT),
    }))
    assert report["passed"], "Previous city preservation failed; inspect the JSON report"


if __name__ == "__main__":
    main()
