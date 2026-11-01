"""Record durable delivery evidence without committing render intermediates."""
import hashlib,json,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1];cfg=json.loads((R/'config.json').read_text())
motion=json.loads((R/'review/motion.json').read_text());preservation=json.loads((R/'review/preservation.json').read_text())
video=json.loads((R/'review/video.json').read_text());digest=hashlib.sha256((R/cfg['output']).read_bytes()).hexdigest()
assert preservation['passed']
assert digest==video['blend_sha256']==preservation['output_sha256']==motion['after']['sha256']
assert motion['before']['sha256']==cfg['source_sha256']
for v in video['videos']:
 assert v['full_decode_passed'] and hashlib.sha256((R/v['file']).read_bytes()).hexdigest()==v['sha256']
suite=unittest.defaultTestLoader.discover(str(R/'tests'))
test_result=unittest.TextTestRunner(verbosity=2).run(suite)
assert test_result.wasSuccessful()
report={'revision':'ship-camera-continuity-v001','branch':'main','source':cfg['source'],'source_sha256':cfg['source_sha256'],
 'blend':cfg['output'],'blend_sha256':digest,'fps':30,'frame_range':[0,989],'duration_seconds':33,
 'modified_camera_window':cfg['window'],'full_ship_follow_window':cfg['full_weight'],
 'camera_model':'single ship-relative mount; continuous offset and view direction; C2 entry/exit blending',
 'motion_metrics':{k:motion[k]['metrics'] for k in ('before','after')},'roll_reference':'moving ship radial up',
 'preservation':preservation,'videos':video['videos'],'render_provenance':video['verified_reused_frames'],
 'rerendered_frames':video['rerendered_frames'],'camera_acceptance_tests_passed':test_result.testsRun,
 'frame_map_sha256':hashlib.sha256((R/'frame-map.csv').read_bytes()).hexdigest()}
(R/'delivery.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'blend_sha256':digest,'tests_passed':test_result.testsRun,'video':video['videos'][0]},indent=2),flush=True)
