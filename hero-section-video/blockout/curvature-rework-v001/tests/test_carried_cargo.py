"""Remaining cargo must retain its source position inside the animated container."""
import bpy,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1];candidate=Path(bpy.data.filepath)
def relative_snapshot():
 s=bpy.context.scene;result={}
 for f in [1,360,640,768,842,930,1075,1392]:
  s.frame_set(f);inverse=s.objects['A01_CONTAINER'].matrix_world.inverted()
  result[f]={o.name:list(map(list,inverse@o.matrix_world)) for o in s.objects if o.name.startswith('W01_REMAINING_CONTAINER_CARGO')}
 return result
actual=relative_snapshot();bpy.ops.wm.open_mainfile(filepath=str(R/'inputs/warehouse-v008.blend'));expected=relative_snapshot();bpy.ops.wm.open_mainfile(filepath=str(candidate))
class CarriedCargo(unittest.TestCase):
 def test_remaining_cartons_stay_in_their_source_container_slots(self):
  self.assertTrue(expected[1075])
  for f,objects in expected.items():
   self.assertEqual(set(objects),set(actual[f]))
   for name,matrix in objects.items():
    error=max(abs(matrix[i][j]-actual[f][name][i][j]) for i in range(4) for j in range(4))
    self.assertLess(error,.0001,(f,name,'received a second transform',error))
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(CarriedCargo))
 if not result.wasSuccessful():raise AssertionError('Carried cargo regression')
