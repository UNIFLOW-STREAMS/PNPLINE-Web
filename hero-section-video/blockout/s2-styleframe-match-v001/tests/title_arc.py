"""Regression for detached A, independent planar letters and undersized cloud."""
import bpy,math,json,unittest,sys
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;s.frame_set(156)
version=Path(bpy.data.filepath).stem.rsplit('-',1)[-1]
config=R/f'review/title-arc-{version}-config.json'
C=json.loads((config if config.exists() else R/'title-arc-config.json').read_text());a=math.radians(C['yaw_degrees']);radius=C['radius']
centre=Vector((C['midpoint'][0]+radius*math.sin(a),C['midpoint'][1]-radius*math.cos(a),0))
inv=s.objects['SF_CN_LAYOUT'].matrix_world.inverted()
def points(ch):
 o=s.objects['SF_CHINA_GOLD_'+ch];return [inv@o.matrix_world@v.co for v in o.data.vertices]
class TitleArcTests(unittest.TestCase):
 def test_all_five_letters_share_one_curved_band(self):
  # Envelope follows physical front/back thickness, including bevels. A set
  # of separately placed flat glyphs cannot satisfy the shared-radius band.
  for ch in 'CHINA':
   radii=[math.hypot(p.x-centre.x,p.y-centre.y)for p in points(ch)]
   self.assertGreater(min(radii),radius-1.35,ch+' detached from shared arc')
   self.assertLess(max(radii),radius+1.0,ch+' detached from shared arc')
 def test_a_has_no_abrupt_forward_step_from_n(self):
  mid={ch:(min(p.y for p in points(ch))+max(p.y for p in points(ch)))/2 for ch in 'NA'}
  self.assertLess(mid['N']-mid['A'],6.0,'A jumps forward instead of continuing the arc')
 def test_right_cloud_larger_than_previous_trial(self):
  root=s.objects['SF_CLOUD_RIGHT'];ps=[]
  for o in root.children_recursive:
   if o.type not in ['MESH','CURVE']:continue
   ps += [world_to_camera_view(s,s.camera,o.matrix_world@Vector(v)) for v in o.bound_box]
  width=max(p.x for p in ps)-min(p.x for p in ps)
  old=json.loads((R/'review/cloud-before.json').read_text())['width']
  self.assertGreater(width,old*1.45,'Right cloud must be visibly larger than the rejected trial (at least 45% wider)')
if __name__=='__main__':
 r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(TitleArcTests))
 suffix=sys.argv[sys.argv.index('--')+1] if '--'in sys.argv else 'result'
 (R/f'review/title-arc-{suffix}.json').write_text(json.dumps({'tests':r.testsRun,'failures':[(str(t),tr)for t,tr in r.failures],'errors':[(str(t),tr)for t,tr in r.errors]},indent=2))
 if not r.wasSuccessful():raise SystemExit(1)
