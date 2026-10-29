import bpy,ast,json,hashlib,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
ns={'bpy':bpy,'json':json,'hashlib':hashlib}
helpers=ast.parse((R/'scripts/verify_preservation.py').read_text())
exec(compile(ast.Module(body=[n for n in helpers.body if isinstance(n,ast.FunctionDef) and n.name in ['scalar','props','node_data']],type_ignores=[]),'stable-signatures','exec'),ns)
tree=ast.parse((R/'scripts/compare_reproduction.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'reproduction-functions','exec'),ns)
class ReproductionTests(unittest.TestCase):
 def test_visual_edits_change_signature(self):
  o=bpy.context.scene.objects['UC_CIVIC_WING'];mod=o.modifiers[0];mat=o.data.materials[0]
  o.data.materials.append(bpy.data.materials['UC_NAVY']);poly=o.data.polygons[0]
  baseline=ns['snap']()
  for target,key,value in [(mod,'width',mod.width+.1),(mat,'diffuse_color',(.12,.34,.56,1))]:
   old=getattr(target,key);old=tuple(old) if key=='diffuse_color' else old
   with self.subTest(key=key):
    setattr(target,key,value);self.assertFalse(baseline==ns['snap'](),key+' omitted from visual reproduction signature')
   setattr(target,key,old)
  before=ns['snap']();o.data.polygons[0].material_index=1;o.data.update()
  print('POLYGON_MUTATION',o.data.polygons[0].material_index,len(o.data.materials))
  after=ns['snap']();print('POLYGON_AFTER_SNAPSHOT',o.data.polygons[0].material_index)
  self.assertFalse(before==after,'Polygon material assignment omitted')
r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ReproductionTests))
if not r.wasSuccessful():raise AssertionError('Incomplete reproduction signature')
