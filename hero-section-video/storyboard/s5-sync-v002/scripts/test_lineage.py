import unittest, tempfile, json, hashlib, copy
from pathlib import Path
from lineage import validate_expression
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
class LineageTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]/'logs');self.addCleanup(self.tmp.cleanup);self.p=Path(self.tmp.name)
  self.sel=self.p/'selection.json';self.sel.write_text(json.dumps({'source_sha256':'source','panels':[{'id':'S5-01','frame':672}]}))
  self.out=self.p/'line.png';self.out.write_bytes(b'line')
  self.raw={'source':{'sha256':'source'},'scene':'Scene','camera':'Cam','render':{'resolution':[960,540],'pixel_aspect':[1,1]},'images':[{'frame':672,'sha256':'raw','camera_state':{'world_matrix':[[1]],'lens_mm':35,'shift':[0,0]}}]}
  self.rec={'status':'complete','source_sha256':'source','scene':'Scene','camera':'Cam','selection_sha256':sha(self.sel),'resolution':[960,540],'pixel_aspect':[1,1],'images':[{'id':'S5-01','frame':672,'raw_sha256':'raw','camera_state':{'world_matrix':[[1]],'lens_mm':35,'shift':[0,0]},'path':str(self.out),'sha256':sha(self.out)}]}
 def test_valid(self):validate_expression(self.rec,self.raw,self.sel)
 def test_incomplete(self):
  self.rec['status']='rendering'
  with self.assertRaises(ValueError):validate_expression(self.rec,self.raw,self.sel)
 def test_camera_projection_change(self):
  self.rec['images'][0]['camera_state']['lens_mm']=40
  with self.assertRaises(ValueError):validate_expression(self.rec,self.raw,self.sel)
 def test_wrong_parent(self):
  self.rec['images'][0]['raw_sha256']='different'
  with self.assertRaises(ValueError):validate_expression(self.rec,self.raw,self.sel)
 def test_wrong_dimensions(self):
  self.rec['resolution']=[960,600]
  with self.assertRaises(ValueError):validate_expression(self.rec,self.raw,self.sel)
 def test_missing_panel(self):
  self.rec['images']=[]
  with self.assertRaises(ValueError):validate_expression(self.rec,self.raw,self.sel)
 def test_changed_selection(self):
  self.sel.write_text('{}')
  with self.assertRaises(ValueError):validate_expression(self.rec,self.raw,self.sel)
 def test_changed_artwork(self):
  self.out.write_bytes(b'changed')
  with self.assertRaises(ValueError):validate_expression(self.rec,self.raw,self.sel)
 def test_wrong_scene(self):
  self.rec['scene']='Other'
  with self.assertRaises(ValueError):validate_expression(self.rec,self.raw,self.sel)
if __name__=='__main__':unittest.main(verbosity=2)
