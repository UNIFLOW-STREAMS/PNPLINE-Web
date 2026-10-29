import bpy,unittest,math
from mathutils import Vector
S=bpy.context.scene;U=S.objects['US_FRAME'].matrix_world.copy();I=U.inverted()
class Operations(unittest.TestCase):
 def test_stored_cartons_rest_on_physical_pallet_slats(self):
  S.frame_set(1075)
  supports=[o for o in S.objects if o.name.startswith('WH_STOCK_PALLET_')]
  cartons=[o for o in S.objects if o.get('wh_role')=='stock' and not o.name.startswith('WH_STOCK_PALLET_')]
  self.assertGreater(len(cartons),50,'Missing dense stocked bays')
  def boxpoints(o):return [I@o.matrix_world@Vector(c) for c in o.bound_box]
  slabs=[]
  for o in supports:
   p=boxpoints(o);slabs.append(([min(v[k] for v in p) for k in range(3)],[max(v[k] for v in p) for k in range(3)]))
  for o in cartons:
   p=boxpoints(o);z=min(v.z for v in p);center=I@o.matrix_world.translation
   self.assertTrue(any(a[0]<=center.x<=b[0] and a[1]<=center.y<=b[1] and abs(z-b[2])<.004 for a,b in slabs),o.name+' has no physical support')
 def test_inbound_pallet_is_visible_during_transfer(self):
  # Literal baseline counts: doors already mask the pallet before it leaves the container.
  for f,minimum in [(908,1),(912,1),(916,3),(920,4),(930,4),(952,4)]:
   S.frame_set(f);deps=bpy.context.evaluated_depsgraph_get();origin=S.objects['CAM_MASTER'].matrix_world.translation
   root=S.objects['W01_NEW_PALLET'];visible=0;blocked=[]
   for child in root.children:
    if '_BOX_' not in child.name:continue
    target=child.matrix_world.translation;d=target-origin
    hit,point,n,face,obj,m=S.ray_cast(deps,origin,d.normalized(),distance=d.length+.1)
    if hit and (obj.name.startswith('W01_NEW_PALLET') or obj.name.startswith('WH_W01_NEW_PALLET')):visible+=1
    elif hit:blocked.append(obj.name)
   self.assertGreaterEqual(visible,minimum,(f,'inbound pallet hidden',blocked))
 def test_storage_jack_and_pallet_components_clear_rack(self):
  jack=S.objects['W02_STORAGE_JACK'];pallet=S.objects['W01_STORED_PALLET'];moving=[o for o in list(jack.children)+list(pallet.children) if o.type=='MESH']
  rack=[o for o in S.objects if o.type=='MESH' and o.name.startswith(('WH_RACK_')) and '_44_32.5_' in o.name]
  self.assertTrue(rack,'Missing storage destination rack')
  def bb(o):
   points=[I@o.matrix_world@Vector(c) for c in o.bound_box]
   return [min(p[k] for p in points) for k in range(3)],[max(p[k] for p in points) for k in range(3)]
  for tick in range(980*4,1055*4+1):
   f=tick/4;S.frame_set(int(f),subframe=f%1)
   for o in moving:
    lo,hi=bb(o)
    for fixed in rack:
     a,b=bb(fixed);overlap=[min(hi[k],b[k])-max(lo[k],a[k]) for k in range(3)]
     self.assertLessEqual(min(overlap),.004,(f,o.name,fixed.name,'handling assembly penetrates rack'))
 def test_jack_wheels_clear_pallet_runners(self):
  def bb(o):
   points=[I@o.matrix_world@Vector(c) for c in o.bound_box]
   return [min(p[k] for p in points) for k in range(3)],[max(p[k] for p in points) for k in range(3)]
  for f in range(909,1056):
   S.frame_set(f)
   for jack,pallet in [('W02_INBOUND_JACK','W01_NEW_PALLET'),('W02_STORAGE_JACK','W01_STORED_PALLET')]:
    wheels=[o for o in S.objects[jack].children if '_WHEEL_' in o.name]
    runners=[o for o in S.objects[pallet].children if '_RUNNER_' in o.name]
    self.assertEqual(len(wheels),4);self.assertEqual(len(runners),2)
    for wheel in wheels:
     lo,hi=bb(wheel)
     for runner in runners:
      a,b=bb(runner);self.assertLessEqual(min(min(hi[k],b[k])-max(lo[k],a[k]) for k in range(3)),.004,(f,wheel.name,runner.name))
 def test_storage_lift_keeps_forks_under_pallet_deck(self):
  for f in range(985,1026):
   S.frame_set(f);deck=S.objects['WH_W01_STORED_PALLET_DECK'];bottom=min((I@deck.matrix_world@Vector(c)).z for c in deck.bound_box)
   for fork in S.objects['W02_STORAGE_JACK'].children:
    if fork.get('wh_role')=='fork':
     top=max((I@fork.matrix_world@Vector(c)).z for c in fork.bound_box)
     self.assertAlmostEqual(top,bottom,delta=.004,msg=(f,fork.name,'fork lost pallet support'))
 def test_lifting_forks_remain_parallel_to_warehouse_floor(self):
  for f in [900,985,994,1018,1043,1150]:
   S.frame_set(f)
   for n in ['W02_STORAGE_JACK','W02_INBOUND_JACK']:
    up=(I@S.objects[n].matrix_world).to_3x3()@Vector((0,0,1))
    self.assertGreater(up.normalized().z,math.cos(math.radians(.25)),(f,n,'fork platform tilted'))
 def test_loading_cargo_keeps_cart_hand_and_van_support(self):
  for f in range(1090,1201):
   S.frame_set(f);load=I@S.objects['W08_LAST_LOAD'].matrix_world.translation
   if f<=1150:
    cart=I@S.objects['W09_OUT_CART'].matrix_world.translation
    self.assertLess((load.xy-cart.xy).length,.01)
    self.assertAlmostEqual(load.z-.275,cart.z+.57,delta=.005)
   elif f<=1166:
    hand=I@S.objects['CH_LOAD_SUPPORT'].matrix_world.translation
    self.assertLess((load.xy-hand.xy).length,.01)
    self.assertAlmostEqual(load.z-.275,hand.z+.03,delta=.005)
   else:self.assertAlmostEqual(load.z-.275,1.54,delta=.005)
 def test_conveyor_parcels_do_not_jump_or_leave_the_belt(self):
  parcels=[o for o in S.objects if o.get('wh_role')=='flow_parcel']
  self.assertTrue(parcels,'Missing moving conveyor parcels')
  last={}
  for f in range(899,1393):
   S.frame_set(f)
   for o in parcels:
    p=I@o.matrix_world.translation
    self.assertAlmostEqual(p.z,2.65,delta=.002)
    body=next(c for c in o.children if c.get('wh_role')=='parcel_body')
    bottom=min((I@body.matrix_world@Vector(c)).z for c in body.bound_box)
    self.assertAlmostEqual(bottom,2.65,delta=.003)
    lane_error=min(abs(p.y-26),abs(p.y-28)) if 43<=p.x<=62 else abs(math.hypot(p.x-(43 if p.x<43 else 62),p.y-27)-1)
    self.assertLess(lane_error,.015,(f,o.name,'parcel left belt surface'))
    if o.name in last:self.assertLess((p-last[o.name]).length,.2,(f,o.name,'jump'))
    last[o.name]=p
if __name__=='__main__':
 r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Operations))
 if not r.wasSuccessful():raise AssertionError('Operations tests failed')
