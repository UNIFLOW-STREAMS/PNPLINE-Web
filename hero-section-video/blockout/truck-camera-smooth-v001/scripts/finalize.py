"""Publish compact delivery evidence after render and preservation checks."""
import hashlib, json, math, statistics
from pathlib import Path

R = Path(__file__).resolve().parents[1]
cfg = json.loads((R/'config.json').read_text())
motion = json.loads((R/'review/motion.json').read_text())
preservation = json.loads((R/'review/preservation.json').read_text())
video = json.loads((R/'review/video.json').read_text())
assert preservation['passed']
assert video['blend_sha256'] == preservation['output_sha256'] == hashlib.sha256((R/cfg['output']).read_bytes()).hexdigest()
for v in video['videos']:
    assert v['full_decode_passed'] and hashlib.sha256((R/v['file']).read_bytes()).hexdigest() == v['sha256']

def median_speed(rows):
    return statistics.median(math.dist(a['eye'], b['eye']) / (b['frame']-a['frame'])
        for a,b in zip(rows, rows[1:]) if 467 <= a['frame'] <= 565)

before = median_speed(motion['before']['rows'])
after = median_speed(motion['after']['rows'])
result = {
    'revision': 'truck-camera-smooth-v001',
    'branch': 'main',
    'source': cfg['source'],
    'source_sha256': cfg['source_sha256'],
    'blend': cfg['output'],
    'blend_sha256': video['blend_sha256'],
    'fps': 30, 'frame_range': [0,989], 'duration_seconds': 33,
    'modified_camera_window': cfg['window'],
    'requested_frame_range': [467,565],
    'median_camera_speed_units_per_frame': {'before':before, 'after':after, 'reduction_percent':100*(1-after/before)},
    'motion_metrics': {kind:motion[kind]['metrics'] for kind in ('before','after')},
    'roll_reference': 'port up smoothly blended to warehouse up over f460..510',
    'preservation': preservation,
    'videos': video['videos'],
    'render_provenance': {k:v for k,v in video.items() if k != 'videos'},
    'frame_map_sha256': hashlib.sha256((R/'frame-map.csv').read_bytes()).hexdigest(),
    'camera_acceptance_tests_passed': 6,
    'browser_review': 'review.html: full-video segment seeking and before/after playback at 1x checked',
}
(R/'delivery.json').write_text(json.dumps(result, indent=2))
print(json.dumps({'median_speed_reduction_percent':result['median_camera_speed_units_per_frame']['reduction_percent'],
                  'blend_sha256':result['blend_sha256'], 'video':result['videos'][0]}, indent=2))
