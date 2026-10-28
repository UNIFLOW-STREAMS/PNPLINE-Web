"""Breaks caught: missing landmarks, duplicated ownership, animated environment,
unparented city, shared original data, or unsupported footprint. Visual AC is manual.
Run against baseline first to demonstrate missing-proxy RED.
"""
import bpy, unittest, json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
GROUPS=['CN_LM_SPHERE_TOWER','CN_LM_TAPERED_TOWER','CN_LM_OPEN_TOP_TOWER','CN_LM_STEPPED_TOWER','CN_HIGHRISE_GROUP','CN_WATERFRONT_GROUP','CN_LOWRISE_GROUP','CN_SITE_CONNECTOR']
class ProxyTests(unittest.TestCase):
 def test_editable_landmark_groups(self):
  for n in GROUPS:
   self.assertIn(n,bpy.data.objects,'Missing editable proxy group: '+n)
   self.assertTrue(any(o.type=='MESH' for o in bpy.data.objects[n].children_recursive),n)
 def test_owned_static_unique_instances(self):
  owned=[o for o in bpy.context.scene.objects if o.get('cn_proxy_owner')=='cn-city-proxy-v001']
  self.assertGreater(len(owned),20,'No city proxy geometry')
  ids=[o.get('instance_id') for o in owned]; self.assertNotIn(None,ids);self.assertEqual(len(ids),len(set(ids)))
  for o in owned:
   self.assertIsNone(o.animation_data,o.name);self.assertEqual(len(o.constraints),0,o.name)
   if o.data:self.assertIsNone(o.data.animation_data,o.name)
   self.assertFalse(o.hide_render,o.name)
 def test_separate_meshes_and_materials(self):
  original=json.loads((R/'review/scene-inventory.json').read_text())['objects']
  olddata={bpy.data.objects[n].data for n in original if bpy.data.objects[n].data}
  oldmats={m for n in original if bpy.data.objects[n].type=='MESH' for m in bpy.data.objects[n].data.materials}
  for o in bpy.context.scene.objects:
   if not o.get('cn_proxy_owner'):continue
   self.assertNotIn(o.data,olddata)
   if o.type=='MESH':
    for m in o.data.materials:self.assertNotIn(m,oldmats)
 def test_site_and_fixed_parent(self):
  self.assertIn('CN_PROXY_ROOT',bpy.data.objects)
  root=bpy.data.objects['CN_PROXY_ROOT'];self.assertEqual(root.parent.name,'CN_FRAME')
  for n in GROUPS:self.assertEqual(bpy.data.objects[n].parent,root)
  bpy.context.scene.frame_set(0);saved={o.name:o.matrix_world.copy() for o in root.children_recursive}
  for f in [96,216,456,648,900,1200,1392]:
   bpy.context.scene.frame_set(f)
   for n,m in saved.items():self.assertEqual(bpy.data.objects[n].matrix_world,m,n)
 def test_open_top_is_a_real_aperture(self):
  self.assertIn('CN_LM_OPEN_TOP_TOWER',bpy.data.objects)
  root=bpy.data.objects['CN_LM_OPEN_TOP_TOWER'];bpy.context.view_layer.update()
  # The opening centre is 89% of the designed height, along the local Y ray.
  height=root['height'];p=root.matrix_world@Vector((0,-4,height*.89))
  direction=root.matrix_world.to_3x3()@Vector((0,1,0))
  hits=[]
  for o in root.children_recursive:
   if o.type!='MESH':continue
   inv=o.matrix_world.inverted();hit,*_=o.ray_cast(inv@p,(inv.to_3x3()@direction).normalized(),distance=8)
   if hit:hits.append(o.name)
  self.assertEqual(hits,[],'Opening filled by solid geometry')
 def test_building_foundations_rest_on_existing_terrace(self):
  foundations=[o for o in bpy.context.scene.objects if o.get('cn_foundation')]
  self.assertGreater(len(foundations),10)
  inv=bpy.data.objects['CN_FRAME'].matrix_world.inverted()
  for o in foundations:
   pts=[inv@o.matrix_world@Vector(c) for c in o.bound_box]
   self.assertAlmostEqual(min(p.z for p in pts),.68,delta=.0001,msg=o.name)
   self.assertTrue(all(-25<=p.x<=24 and 5<=p.y<=36 for p in pts),o.name)
if __name__=='__main__':
 r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ProxyTests))
 if not r.wasSuccessful():raise SystemExit(1)
