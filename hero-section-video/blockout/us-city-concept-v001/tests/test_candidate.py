"""Detect missing design parts, animated decorations, changed timeline or shared data."""
import bpy,unittest,sys
from mathutils import Vector
S=bpy.context.scene
class CityTests(unittest.TestCase):
 def test_editable_three_letters(self):
  for ch in 'USA':
   o=S.objects.get('UC_LETTER_'+ch)
   self.assertIsNotNone(o,'Missing independent 3D letter '+ch)
   self.assertEqual(o.type,'MESH');self.assertGreater(len(o.data.vertices),30)
   self.assertGreater(o.dimensions.y,.2)
 def test_ten_thick_stars(self):
  stars=[o for o in S.objects if o.get('uc_role')=='star']
  self.assertEqual(len(stars),10)
  for o in stars:self.assertEqual(o.type,'MESH');self.assertGreater(len(o.data.polygons),10)
 def test_title_extends_above_main_skyline(self):
  S.frame_set(510);inv=S.objects['US_FRAME'].matrix_world.inverted()
  tower=S.objects.get('UC_GLASS_SPIRE_TOWER')
  self.assertIsNotNone(tower)
  tower_top=max((inv@tower.matrix_world@v.co).z for v in tower.data.vertices)
  for ch in 'USA':
   o=S.objects['UC_LETTER_'+ch]
   self.assertGreater(max((inv@o.matrix_world@v.co).z for v in o.data.vertices),tower_top,'Title is buried behind skyline: '+ch)
 def test_statue_recognizable_parts_and_enlargement(self):
  for part in ['ROBE','HEAD','CROWN','TABLET','RAISED_ARM','FLAME','ISLAND','PEDESTAL']:
   self.assertIsNotNone(S.objects.get('UC_LIBERTY_'+part),part)
  root=S.objects.get('UC_LIBERTY')
  self.assertIsNotNone(root)
  self.assertGreater(root.get('selected_body_height',0),root.get('reference_body_height',1))
 def test_owned_static_world_geometry(self):
  owned=[o for o in S.objects if o.get('uc_owner')=='us-city-concept-v001']
  self.assertGreater(len(owned),100)
  for o in owned:
   self.assertIsNone(o.animation_data,o.name)
   self.assertEqual(len(o.constraints),0,o.name)
   p=o
   while p.parent:p=p.parent
   self.assertEqual(p.name,'US_FRAME',o.name)
 def test_preserved_timeline(self):
  self.assertEqual((S.frame_start,S.frame_end,S.render.fps),(0,1392,12))
  self.assertEqual(S.camera.name,'CAM_MASTER')
suite=unittest.defaultTestLoader.loadTestsFromTestCase(CityTests)
result=unittest.TextTestRunner(verbosity=2).run(suite)
if not result.wasSuccessful():raise AssertionError('Candidate acceptance failures')
