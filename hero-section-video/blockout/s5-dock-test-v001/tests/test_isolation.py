"""Controlled Blender fixtures: catches shared actions/data and unsafe cleanup."""
import bpy,sys,unittest,importlib.util
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
class IsolationContract(unittest.TestCase):
 def test_clone_is_independent_and_idempotent(self):
  # A linked Object/Action/Camera would leak these mutations to the source.
  spec=importlib.util.find_spec('isolate_scene')
  self.assertIsNotNone(spec,'Missing independent scene clone implementation')
  from isolate_scene import clone_subset
  src=bpy.data.scenes.new('fixture-master');bpy.context.window.scene=src
  root=bpy.data.objects.new('fixture-root',None);src.collection.objects.link(root)
  root.location.x=2;root.keyframe_insert('location',frame=1);root.location.x=6;root.keyframe_insert('location',frame=10)
  data=bpy.data.cameras.new('fixture-lens');data.lens=40;data.keyframe_insert('lens',frame=1)
  cam=bpy.data.objects.new('fixture-camera',data);src.collection.objects.link(cam);cam.parent=root;src.camera=cam
  child=bpy.data.objects.new('fixture-door',None);src.collection.objects.link(child);child.parent=root
  child.rotation_euler.z=.5;child.keyframe_insert('rotation_euler',frame=1)
  scene,mapping=clone_subset(src,[o.name for o in src.objects],'fixture-test')
  self.assertEqual(set(mapping),{o.name for o in src.objects})
  self.assertIs(mapping[cam.name].parent,mapping[root.name])
  self.assertIsNot(mapping[root.name].animation_data.action,root.animation_data.action)
  self.assertIsNot(mapping[cam.name].data,data)
  self.assertIsNot(mapping[cam.name].data.animation_data.action,data.animation_data.action)
  mapping[root.name].location.x=90;mapping[root.name].keyframe_insert('location',frame=1)
  mapping[child.name].rotation_euler.z=2;mapping[child.name].keyframe_insert('rotation_euler',frame=1)
  mapping[cam.name].data.lens=90;mapping[cam.name].data.keyframe_insert('lens',frame=1)
  src.frame_set(1);self.assertAlmostEqual(root.location.x,2);self.assertAlmostEqual(child.rotation_euler.z,.5);self.assertAlmostEqual(data.lens,40)
  counts=(len(bpy.data.objects),len(bpy.data.actions),len(bpy.data.cameras),len(bpy.data.scenes))
  scene,mapping=clone_subset(src,[o.name for o in src.objects],'fixture-test')
  self.assertEqual(counts,(len(bpy.data.objects),len(bpy.data.actions),len(bpy.data.cameras),len(bpy.data.scenes)))
  self.assertEqual(len(scene.objects),3)
  # A later user link into the master must be refused, never deleted on rerun.
  external=mapping[root.name];src.collection.objects.link(external)
  with self.assertRaisesRegex(ValueError,'outside'):
   clone_subset(src,[root.name,cam.name,child.name],'fixture-test')
  self.assertIn(external.name,src.objects)
  src.collection.objects.unlink(external)
  # Regression for final review: all external ID users, not just Scene links.
  observer=bpy.data.objects.new('original-observer',bpy.data.meshes.new('observer-mesh'));src.collection.objects.link(observer)
  for kind in ['parent','constraint','modifier','driver']:
   with self.subTest(external_reference=kind):
    target=bpy.data.objects['S5T__'+root.name]
    if kind=='parent':observer.parent=target
    elif kind=='constraint':ref=observer.constraints.new('COPY_LOCATION');ref.target=target
    elif kind=='modifier':ref=observer.modifiers.new('external-reference','MIRROR');ref.mirror_object=target
    else:
     fc=observer.driver_add('location',0);var=fc.driver.variables.new();var.name='x';var.type='SINGLE_PROP';var.targets[0].id=target;var.targets[0].data_path='location[0]';fc.driver.expression='x'
    before=(len(bpy.data.objects),len(bpy.data.scenes),len(bpy.data.actions))
    with self.assertRaisesRegex(ValueError,'outside'):
     clone_subset(src,[root.name,cam.name,child.name],'fixture-test')
    self.assertEqual(before,(len(bpy.data.objects),len(bpy.data.scenes),len(bpy.data.actions)))
    if kind=='parent':self.assertIs(observer.parent,target);observer.parent=None
    elif kind=='constraint':self.assertIs(ref.target,target);observer.constraints.remove(ref)
    elif kind=='modifier':self.assertIs(ref.mirror_object,target);observer.modifiers.remove(ref)
    else:self.assertIs(var.targets[0].id,target);observer.driver_remove('location',0)
 def test_foreign_name_collision_is_refused_before_mutation(self):
  spec=importlib.util.find_spec('isolate_scene');self.assertIsNotNone(spec,'Missing collision guard')
  from isolate_scene import clone_subset
  src=bpy.data.scenes.new('collision-source');o=bpy.data.objects.new('collision-object',None);src.collection.objects.link(o)
  foreign=bpy.data.objects.new('S5T__collision-object',None);src.collection.objects.link(foreign)
  counts=(len(bpy.data.objects),len(bpy.data.scenes))
  with self.assertRaisesRegex(ValueError,'collision'):
   clone_subset(src,[o.name],'collision-test')
  self.assertEqual(counts,(len(bpy.data.objects),len(bpy.data.scenes)))
 def test_unhandled_driver_is_refused_without_leaking(self):
  spec=importlib.util.find_spec('isolate_scene');self.assertIsNotNone(spec,'Missing unsupported-reference guard')
  from isolate_scene import clone_subset
  src=bpy.data.scenes.new('driver-source');o=bpy.data.objects.new('driver-object',None);src.collection.objects.link(o);o.driver_add('location',0)
  counts=(len(bpy.data.objects),len(bpy.data.scenes))
  with self.assertRaisesRegex(ValueError,'driver|NLA|constraint'):
   clone_subset(src,[o.name],'driver-test')
  self.assertEqual(counts,(len(bpy.data.objects),len(bpy.data.scenes)))
if __name__=='__main__':
 r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(IsolationContract))
 if not r.wasSuccessful():raise SystemExit(1)
