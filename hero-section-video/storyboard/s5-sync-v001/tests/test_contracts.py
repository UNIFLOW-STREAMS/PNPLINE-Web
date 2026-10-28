import unittest,tempfile,json,sys,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from contracts import digest,validate_run,validate_selection,validate_panel,validate_role

class Contracts(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]/'logs');self.addCleanup(self.tmp.cleanup);self.r=Path(self.tmp.name)
  for n in ['master.blend','style.json','select.json','script.py','0010.png','0011.png']:(self.r/n).write_bytes(n.encode())
  self.rec={'status':'complete','run_id':'test','source':{'path':str(self.r/'master.blend'),'sha256':digest(self.r/'master.blend')},'scene':'Scene','camera':'Camera','fps':24,'fps_base':1.001,'preview_start':10,'frame_range':[0,100],'dependencies':{str(self.r/n):digest(self.r/n) for n in ['style.json','select.json','script.py']},'expected_frames':[10,11],'output_dir':str(self.r),'images':[{'frame':f,'subframe':0,'camera':'Camera','scene':'Scene','source_sha256':digest(self.r/'master.blend'),'path':str(self.r/f'{f:04d}.png'),'sha256':digest(self.r/f'{f:04d}.png'),'run_id':'test'} for f in [10,11]]}
  self.sel={'source_sha256':digest(self.r/'master.blend'),'fps':24,'fps_base':1.001,'preview_start':10,'panels':[{'id':'a','frame':10,'master_seconds':10*1.001/24,'preview_seconds':0},{'id':'b','frame':11,'master_seconds':11*1.001/24,'preview_seconds':1.001/24}]}
 def test_valid_record_and_noninteger_timebase(self):validate_run(self.rec);validate_selection(self.sel,self.rec)
 def test_incomplete_run_refuses_even_with_stale_png(self):
  self.rec['status']='rendering'
  with self.assertRaises(ValueError):validate_run(self.rec)
 def test_unrecorded_stale_png_refuses(self):
  (self.r/'0012.png').write_bytes(b'stale')
  with self.assertRaises(ValueError):validate_run(self.rec)
 def test_missing_frame_refuses(self):
  self.rec['images'].pop()
  with self.assertRaises(ValueError):validate_run(self.rec)
 def test_missing_camera_or_wrong_source_refuses(self):
  for key in ['camera','scene','frame','source_sha256']:
   r=copy.deepcopy(self.rec);r['images'][0].pop(key)
   with self.assertRaises(ValueError):validate_run(r)
  self.rec['images'][0]['source_sha256']='wrong'
  with self.assertRaises(ValueError):validate_run(self.rec)
 def test_changed_input_or_style_requires_review(self):
  for n in ['master.blend','style.json','select.json','script.py']:
   p=self.r/n;old=p.read_bytes();p.write_bytes(b'changed')
   with self.assertRaisesRegex(ValueError,'review required'):validate_run(self.rec)
   p.write_bytes(old)
 def test_changed_png_refuses(self):
  (self.r/'0010.png').write_bytes(b'other frame')
  with self.assertRaises(ValueError):validate_run(self.rec)
 def test_duplicate_id_or_reverse_order_refuses(self):
  for change in ['duplicate','reverse']:
   s=copy.deepcopy(self.sel)
   if change=='duplicate':s['panels'][1]['id']='a'
   else:s['panels'].reverse()
   with self.assertRaises(ValueError):validate_selection(s,self.rec)
 def test_wrong_fps_preview_start_or_seconds_refuses(self):
  for key,value in [('fps',12),('fps_base',1),('preview_start',0)]:
   s=copy.deepcopy(self.sel);s[key]=value
   with self.assertRaises(ValueError):validate_selection(s,self.rec)
  self.sel['panels'][1]['preview_seconds']=11/12
  with self.assertRaises(ValueError):validate_selection(self.sel,self.rec)
 def test_panel_requires_correct_parent_and_existing_file(self):
  p={'path':str(self.r/'panel.png'),'raw_path':self.rec['images'][0]['path'],'raw_sha256':self.rec['images'][0]['sha256'],'frame':10};(self.r/'panel.png').write_bytes(b'panel');p['sha256']=digest(self.r/'panel.png')
  validate_panel(p,self.rec)
  p['raw_path']=self.rec['images'][1]['path']
  with self.assertRaises(ValueError):validate_panel(p,self.rec)
  p['raw_path']=self.rec['images'][0]['path'];(self.r/'panel.png').unlink()
  with self.assertRaises(ValueError):validate_panel(p,self.rec)
 def test_stopped_aligned_frame_cannot_be_turning(self):
  state={'speed':0,'yaw':180,'yaw_change':0,'doors_closed':True,'doors_open':False,'dock_gap':5.2,'cargo_relative_error':0,'forward_dot':0}
  with self.assertRaises(ValueError):validate_role('S5-03A',state)
  state.update(speed=.3,yaw=95,yaw_change=5,forward_dot=.999)
  validate_role('S5-03A',state)
 def test_approach_and_open_door_roles_are_distinct(self):
  s={'speed':.4,'yaw':0,'yaw_change':0,'doors_closed':True,'doors_open':False,'dock_gap':9,'cargo_relative_error':0,'forward_dot':1}
  validate_role('S5-03',s)
  with self.assertRaises(ValueError):validate_role('S5-04',s)
  s.update(speed=0,yaw=180,doors_closed=False,doors_open=True,dock_gap=5.2)
  validate_role('S5-04',s)
  with self.assertRaises(ValueError):validate_role('S5-05',s)
  s['dock_gap']=0;validate_role('S5-05',s)
if __name__=='__main__':unittest.main(verbosity=2)
