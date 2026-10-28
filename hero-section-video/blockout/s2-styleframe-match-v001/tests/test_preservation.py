"""Mutation probes for real Blender state, without saving mutations.
Changing a camera key, root action, or unrelated material must be detected.
An explicitly allowed mesh-only edit must remain permitted.
"""
import bpy,sys,unittest,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
import protection
class ProtectionTests(unittest.TestCase):
 def setUp(self):
  bpy.ops.wm.open_mainfile(filepath=str(R/'inputs/base.blend'))
  self.before=protection.capture(frames=[0,96,156,216,456,648,900,1392])
 def changed(self):return protection.changed(self.before,protection.capture(frames=[0,96,156,216,456,648,900,1392]))
 def first_key(self,o):
  return next(fc for l in o.animation_data.action.layers for s in l.strips for b in s.channelbags for fc in b.fcurves).keyframe_points[0]
 def test_identity(self):self.assertEqual(self.changed(),[])
 def test_camera_key_edit_detected(self):
  self.first_key(bpy.data.objects['CAM_MASTER']).co.y+=.2
  self.assertIn('actions',self.changed())
 def test_ship_motion_key_edit_detected(self):
  self.first_key(bpy.data.objects['A02_SHIP']).co.y+=.2
  self.assertIn('actions',self.changed())
 def test_camera_lens_edit_detected(self):
  # The source lens is animated; mutating its evaluated scalar is overwritten
  # by frame_set. Mutate the persistent curve to represent a real saved edit.
  data=bpy.data.objects['CAM_MASTER'].data
  for l in data.animation_data.action.layers:
   for st in l.strips:
    for bag in st.channelbags:
     for fc in bag.fcurves:
      if fc.data_path=='lens':
       for k in fc.keyframe_points:k.co.y+=1
  self.assertIn('cameras',self.changed())
 def test_unrelated_shared_material_edit_detected(self):
  bpy.data.materials['white'].diffuse_color[0]=.19
  self.assertIn('materials',self.changed())
 def test_allowed_static_hull_vertex_edit_permitted(self):
  bpy.data.objects['SHIP_HULL'].data.vertices[0].co.x+=.2
  self.assertEqual(self.changed(),[])
if __name__=='__main__':
 r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ProtectionTests))
 suffix=sys.argv[sys.argv.index('--')+1] if '--'in sys.argv else 'green'
 (R/f'review/protection-{suffix}.json').write_text(json.dumps({'tests':r.testsRun,'failures':[(str(t),trace) for t,trace in r.failures],'errors':[(str(t),trace) for t,trace in r.errors]},indent=2))
 if not r.wasSuccessful():raise SystemExit(1)
