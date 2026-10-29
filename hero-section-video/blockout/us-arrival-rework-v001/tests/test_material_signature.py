import bpy,ast,json,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1];D=R.parent/'us-city-concept-v001'
exec(compile(ast.Module(body=[n for n in ast.parse((D/'scripts/verify_preservation.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name in ['scalar','props','node_data']],type_ignores=[]),'signature','exec'))
p=R/'scripts/material_signature.py'
if p.exists():exec(compile(p.read_text(),str(p),'exec'))
class MaterialTest(unittest.TestCase):
 def test_reference_count_does_not_change_material_content(self):
  m=bpy.data.materials['UC_WHITE'];a=node_data(m);m.use_fake_user=not m.use_fake_user
  self.assertEqual(a,node_data(m))
 def test_real_color_change_is_detected(self):
  m=bpy.data.materials['UC_WHITE'];a=node_data(m);m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(1,0,0,1)
  self.assertNotEqual(a,node_data(m))
r=unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(MaterialTest))
if not r.wasSuccessful():raise SystemExit(1)
