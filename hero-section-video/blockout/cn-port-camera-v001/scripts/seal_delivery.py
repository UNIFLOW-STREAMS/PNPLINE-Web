"""Verify final model/report/media correspondence before marking delivery ready."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
review = root / 'review'
master = root / 'master-cn-port-camera-v001.blend'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
model_hash = sha(master)
delivery = json.loads((root / 'delivery.json').read_text(encoding='utf-8'))
assert delivery['sha256'] == model_hash
assert sha(Path(delivery['source'])) == delivery['source_sha256']
camera = json.loads((review / 'camera-verification.json').read_text(encoding='utf-8'))
assert camera['sha256'] == model_hash and camera['contracts_pass']
assert camera['geometry']['swept_eye_and_near_plane_rays_clear']
motion = camera['motion_metrics']
assert not motion['quaternion_raw_sign_change_frames']
assert not motion['ship_tracking_216_360']['behind_camera_frames']
assert not motion['ship_tracking_216_360']['center_outside_image_frames']
max_roll = max(segment['max'] for segment in motion['horizon_roll_relative_to_CN_then_ship_up'].values())
assert max_roll < 1.0
for frame, groups in camera['composition'].items():
    assert all(group['all_bounding_corners_in_frame'] for group in groups.values()), frame
support = delivery['ship_support']
assert support['subframe_min_immersion'] > .2
assert support['subframe_min_deck_freeboard'] > .4
assert not support['exposed_bottom_frames'] and not support['port_geometry_crossings']
assert delivery['port_normals']['coordinates_and_topology_membership_exact']
assert not delivery['port_normals']['remaining_negative_closed_components']

for name in ['after-frames/metadata.json', 'motion-a-frames/metadata.json',
             'motion-b-frames/metadata.json', 'motion-metadata.json']:
    record = json.loads((review / name).read_text(encoding='utf-8'))
    assert record['sha256'] == model_hash, name
    assert record['actual_scene_camera'], name
video = json.loads((review / 'motion-metadata.json').read_text(encoding='utf-8'))
assert video['frames'] == 401 and video['frame_range'] == [0, 400]
assert video['native_fps'] == 12 and video['interpolated_frames'] == 0
assert sha(review / video['video']) == video['video_sha256']
artifacts = {}
for name in ['camera-verification.json', 'after-contact-sheet.png',
             'reference-contact-sheet.png', 'cn-port-camera-review.mp4', 'review.html']:
    path = review / name
    assert path.is_file() and path.stat().st_size > 100
    artifacts[name] = {'sha256': sha(path), 'bytes': path.stat().st_size}
delivery.update({
    'status': 'Completed: expanded harbor camera retargeted and reviewed',
    'completed_on': '2026-10-31',
    'verification': {'contracts_passed': True, 'camera_path_clear': True,
                     'dense_samples': camera['geometry']['sample_count'],
                     'sample_step_frames': camera['geometry']['step_frames'],
                     'max_roll_degrees': max_roll,
                     'source_route_exact_from_frame': 360,
                     'full_reveal_framing_frames': [144,156,180]},
    'review_media': artifacts,
    'preview': {'file': str(review / video['video']), 'range': [0,400],
                'duration_seconds': 401/12, 'fps': 12, 'resolution': [960,540],
                'actual_camera': True, 'interpolation': False,
                'lighting': 'Workbench cast shadows off for review only; Cycles lights unchanged'},
})
(root / 'delivery.json').write_text(json.dumps(delivery,indent=2,ensure_ascii=False),encoding='utf-8')
print('SEALED_CAMERA',model_hash,'samples',camera['geometry']['sample_count'],'max_roll',max_roll)
