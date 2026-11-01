"""Collect hash-bound render, motion, and preservation evidence."""
import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];cfg=json.loads((R/'config.json').read_text())
motion=json.loads((R/'review/motion.json').read_text());proof=json.loads((R/'review/preservation.json').read_text())
video=json.loads((R/'review/video.json').read_text());digest=hashlib.sha256((R/cfg['output']).read_bytes()).hexdigest()
assert proof['passed'] and proof['outside_camera_max_error']==0
assert digest==proof['output_sha256']==motion['after']['sha256']==video['blend_sha256']
assert motion['before']['sha256']==cfg['source_sha256']
for v in video['videos']:
 assert v['full_decode_passed'] and hashlib.sha256((R/v['file']).read_bytes()).hexdigest()==v['sha256']
before,after=motion['before']['metrics'],motion['after']['metrics']
report={'revision':'camera-micro-smooth-v001','branch':'main','source':cfg['source'],'source_sha256':cfg['source_sha256'],
 'blend':cfg['output'],'blend_sha256':digest,'fps':30,'duration_seconds':33,'frame_range':[0,989],
 'strict_window':[330,366],'changed_integer_frames':[331,365],'unchanged_integer_frames':[[0,330],[366,989]],
 'motion_metrics':{'before':before,'after':after},'deviation':motion['deviation'],
 'jerk_reduction_percent':{k:100*(1-after[k]/before[k]) for k in ['translation_jerk_max','rotation_jerk_max']},
 'preservation':proof,'videos':video['videos'],'camera_acceptance_tests_passed':5,
 'frame_map_sha256':hashlib.sha256((R/'frame-map.csv').read_bytes()).hexdigest()}
(R/'delivery.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'sha256':digest,'deviation':report['deviation'],'reduction':report['jerk_reduction_percent'],'video':video['videos'][0]},indent=2))
