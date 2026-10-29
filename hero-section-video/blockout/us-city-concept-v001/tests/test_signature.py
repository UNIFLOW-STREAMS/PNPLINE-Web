"""Saved data signature must ignore runtime addresses but catch camera edits."""
import bpy,ast,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
ns={'bpy':bpy,'hashlib':__import__('hashlib'),'json':__import__('json')}
tree=ast.parse((R/'scripts/verify_preservation.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['digest','scalar','props','node_data']],type_ignores=[]),'signature-functions','exec'),ns)
class SignatureTests(unittest.TestCase):
 def test_world_shader_value_edit_detected(self):
  self.assertIn('node_data',ns,'World shader contents are not signed')
  world=bpy.context.scene.world;before=ns['node_data'](world)
  nodes=world.node_tree.nodes;bg=next(n for n in nodes if n.type=='BACKGROUND')
  value=bg.inputs['Strength'].default_value;bg.inputs['Strength'].default_value=value+.5
  self.assertNotEqual(before,ns['node_data'](world));bg.inputs['Strength'].default_value=value
 def test_reopen_stability_and_real_edit_detection(self):
  path=bpy.data.filepath;before=ns['props'](bpy.context.scene.camera.data)
  bpy.ops.wm.open_mainfile(filepath=path);camera=bpy.context.scene.camera.data
  self.assertEqual(before,ns['props'](camera),'Runtime pointers must not masquerade as data edits')
  camera.lens+=1
  self.assertNotEqual(before,ns['props'](camera),'Lens change must be detected')
r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(SignatureTests))
if not r.wasSuccessful():raise AssertionError('Signature test failed')
