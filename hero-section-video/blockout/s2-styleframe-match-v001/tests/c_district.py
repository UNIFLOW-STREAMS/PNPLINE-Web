"""Reference-specific checks for the C-front historic waterfront district."""
import bpy,json,sys,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1];s=bpy.context.scene
class DistrictTests(unittest.TestCase):
 def test_pavilion_has_radial_roof_and_eight_columns(self):
  roof=s.objects.get('DT_PAVILION_ROOF_UPPER');self.assertIsNotNone(roof)
  self.assertEqual(roof.get('sides'),8)
  self.assertEqual(len([o for o in s.objects if o.name.split('.')[0]=='DT_PAVILION_COLUMN']),8)
 def test_domes_are_raised_over_windowed_drums(self):
  for name in ['LEFT','CENTER']:
   dome=s.objects.get('DT_'+name+'_DOME');self.assertIsNotNone(dome)
   self.assertGreater(dome.dimensions.z/dome.dimensions.x,.42)
   self.assertGreaterEqual(len([o for o in s.objects if o.name.startswith('DT_'+name+'_DRUM_WINDOW')]),8)
 def test_garden_has_layered_vegetation_and_paths(self):
  self.assertGreaterEqual(len([o for o in s.objects if o.name.startswith('DT_TREE_TRUNK')]),14)
  self.assertGreaterEqual(len([o for o in s.objects if o.name.startswith('DT_SHRUB')]),30)
  self.assertIsNotNone(s.objects.get('DT_GARDEN_PATH'))
 def test_traditional_foreground_has_two_eaves(self):
  self.assertIsNotNone(s.objects.get('DT_TRADITIONAL_LOWER_ROOF'))
  self.assertIsNotNone(s.objects.get('DT_TRADITIONAL_UPPER_ROOF'))
 def test_street_trucks_have_separate_cab_and_load(self):
  for n in [0,1]:
   self.assertIsNotNone(s.objects.get(f'DT_TRUCK_{n}_CAB'))
   self.assertIsNotNone(s.objects.get(f'DT_TRUCK_{n}_LOAD'))
 def test_new_district_is_static(self):
  objects=[o for o in s.objects if o.get('district_owner')]
  self.assertTrue(objects)
  self.assertFalse(any(o.animation_data for o in objects))
if __name__=='__main__':
 r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(DistrictTests));suffix=sys.argv[sys.argv.index('--')+1]
 (R/f'review/c-district-{suffix}.json').write_text(json.dumps({'tests':r.testsRun,'failures':[(str(t),v)for t,v in r.failures],'errors':[(str(t),v)for t,v in r.errors]},indent=2))
 if not r.wasSuccessful():raise SystemExit(1)
