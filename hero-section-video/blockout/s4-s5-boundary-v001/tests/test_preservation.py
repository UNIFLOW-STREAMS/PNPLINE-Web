import json,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1];cfg=json.loads((R/'config.json').read_text(encoding='utf-8-sig'))
class Preservation(unittest.TestCase):
 def setUp(self):
  self.a=json.loads((R/'review/before-signature.json').read_text());self.b=json.loads((R/'review/after-signature.json').read_text())
 def test_protected_keys_and_handles_exact(self):self.assertEqual(self.a['outside_keys'],self.b['outside_keys'])
 def test_protected_environment_all_frames_exact(self):self.assertEqual(self.a['protected_environment_frames'],self.b['protected_environment_frames'])
 def test_each_group_outside_its_window_exact(self):self.assertEqual(self.a['group_frames'],self.b['group_frames'])
 def test_protected_frames_exact(self):self.assertEqual([r for r in self.a['frames'] if r['frame']<=cfg['edit_start'] or r['frame']>=cfg['edit_end']],[r for r in self.b['frames'] if r['frame']<=cfg['edit_start'] or r['frame']>=cfg['edit_end']])
 def test_protected_subframes_exact(self):self.assertEqual(self.a['join_subframes'],self.b['join_subframes'])
 def test_only_authorized_channels_changed(self):self.assertEqual(sorted(k for k in self.a['objects'] if self.a['objects'][k]!=self.b['objects'][k]),sorted(['CAM_LOOK_TARGET','CAM_MASTER','A03_TRACTOR','A03_TRAILER','A01_CONTAINER','W01_NEW_PALLET','P02_SPREADER']+[f'P02_CABLE_{i}' for i in range(4)]))
 def test_scene_and_material_settings_exact(self):
  for k in ['materials','render','display','world','markers','range','metadata','camera']:self.assertEqual(self.a[k],self.b[k],k)
if __name__=='__main__':unittest.main(verbosity=2)
