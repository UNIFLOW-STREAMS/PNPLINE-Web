"""Behavioral acceptance probes. Run inside Blender after opening the master.

Breaks caught: absent routes, duplicate instance roots, changing environment,
teleporting handoff, drifting trailer coupling, closed-door unloading,
outbound early departure, or a boundary camera reset.
"""
import bpy, json, math, unittest
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

ROOT = Path(__file__).resolve().parents[1]
S = bpy.context.scene

class MasterTests(unittest.TestCase):
    def root(self, name):
        obj = bpy.data.objects.get(name)
        self.assertIsNotNone(obj, 'Required scene instance missing: '+name)
        return obj

    def at(self, name, frame):
        S.frame_set(frame)
        return self.root(name).matrix_world.copy()

    def test_single_camera_and_six_boundaries(self):
        self.assertEqual(S.get('master_version'), 'v004', 'Master scene not built')
        self.assertEqual(S.camera.name, 'CAM_MASTER')
        markers={m.name:m.frame for m in S.timeline_markers}
        self.assertTrue(all(b in markers for b in ['B12','B23','B34','B45','B56','B67']))
        for m in S.timeline_markers:
            self.assertIsNone(m.camera, 'Timeline camera cut')

    def test_all_inventory_ids_mapped_and_unique_instances(self):
        expected={f'A-{n:02}' for n in range(1,6)}|{f'E-{n:02}' for n in range(1,13)}|{f'P-{n:02}' for n in range(1,4)}|{f'W-{n:02}' for n in range(1,11)}|{'CH-01','FX-01'}
        ids={o.get('asset_id') for o in S.objects}
        self.assertFalse(expected-ids, str(expected-ids))
        instances=[o['instance_id'] for o in S.objects if 'instance_id' in o]
        self.assertEqual(len(instances),len(set(instances)))
        for name in ['A01_CONTAINER','A02_SHIP','A03_TRAILER','A03_TRACTOR','A04_PRIMARY','A05_SECONDARY']:
            self.root(name)

    def test_fixed_environment(self):
        env=[o for o in S.objects if o.get('environment')]
        self.assertGreater(len(env),15)
        for o in env:
            self.assertIsNone(o.animation_data, o.name)
        before={o.name:self.at(o.name,1) for o in env}
        for f in [216,456,648,900,1200,1392]:
            S.frame_set(f)
            for o in env:
                self.assertLess(max(abs(o.matrix_world[r][c]-before[o.name][r][c]) for r in range(4) for c in range(4)),1e-6,o.name)

    def test_container_keeps_ship_and_trailer_support(self):
        for start,end,support in [(85,510,'A02_SHIP'),(637,1392,'A03_TRAILER')]:
            S.frame_set(start)
            rel=self.root(support).matrix_world.inverted() @ self.root('A01_CONTAINER').matrix_world
            for f in range(start,end+1,7):
                S.frame_set(f)
                now=self.root(support).matrix_world.inverted() @ self.root('A01_CONTAINER').matrix_world
                self.assertLess((now.translation-rel.translation).length,0.002, f'{support} f{f}')
                self.assertLess(now.to_quaternion().rotation_difference(rel.to_quaternion()).angle,0.002)

    def test_dock_alignment_doors_and_stationary_inbound(self):
        S.frame_set(899)
        c=self.root('A01_CONTAINER').matrix_world
        dock=self.root('DOCK_TARGET').matrix_world
        rear=c @ Vector((-1.6,0,-0.75))
        self.assertLess((rear-dock.translation).length,0.12)
        rear_axis=c.to_3x3() @ Vector((-1,0,0))
        self.assertGreater(rear_axis.normalized().dot(dock.to_3x3() @ Vector((1,0,0))),0.999)
        self.assertGreater(abs(self.root('A01_DOOR_L').rotation_euler.z),math.radians(265))
        self.assertGreater(abs(self.root('A01_DOOR_R').rotation_euler.z),math.radians(265))
        p=self.at('A03_TRAILER',899)
        self.assertLess((self.at('A03_TRAILER',1392).translation-p.translation).length,0.001)

    def test_tractor_trailer_hitch_does_not_separate(self):
        for f in range(648,901):
            S.frame_set(f)
            a=self.root('TRACTOR_HITCH').matrix_world.translation
            b=self.root('TRAILER_HITCH').matrix_world.translation
            self.assertLess((a-b).length,0.002,f'hitch f{f}')

    def test_separate_cargo_and_outbound_timing(self):
        self.root('W01_NEW_PALLET'); self.root('W01_STORED_PALLET')
        p=self.at('W01_NEW_PALLET',970).translation
        self.assertLess((self.at('W01_NEW_PALLET',1392).translation-p).length,0.002)
        for name,start in [('A04_PRIMARY',1201),('A05_SECONDARY',1261)]:
            p=self.at(name,1).translation
            self.assertLess((self.at(name,start-1).translation-p).length,0.001)
            self.assertGreater((self.at(name,1392).translation-p).length,10)

    def test_full_timeline_camera_continuity(self):
        cam=self.root('CAM_MASTER')
        prev=None
        for f in range(1,1393):
            S.frame_set(f)
            m=cam.matrix_world.copy()
            self.assertTrue(all(math.isfinite(v) for row in m for v in row))
            if prev:
                self.assertLess((m.translation-prev.translation).length,2.5,f'camera jump f{f}')
                # q and -q encode the same physical rotation. Use shortest arc.
                q=m.to_quaternion();pq=prev.to_quaternion()
                angle=2*math.acos(min(1,abs(q.dot(pq))))
                self.assertLess(angle,math.radians(8),f'camera rotation f{f}')
            prev=m
        for f in [96,216,456,648,900,1200]:
            a=self.at(cam.name,f-1).translation; b=self.at(cam.name,f).translation; c=self.at(cam.name,f+1).translation
            self.assertGreater((c-a).length,0.001,f'boundary unintended stop {f}')
            self.assertLess((c-2*b+a).length,0.15,f'boundary acceleration {f}')

    def test_ship_never_jumps_and_bow_stern_contact_water(self):
        prev=None
        radius=S['radius']
        for f in range(1,1393):
            m=self.at('A02_SHIP',f)
            if prev:self.assertLess((m.translation-prev).length,1.6,f'ship teleport f{f}')
            prev=m.translation.copy()
            for x in [-6.8,0,6.8]:
                keel=m@Vector((x,0,-.65))
                deck=m@Vector((x,0,.8))
                self.assertLess(keel.length-radius,-.15,f'hull floating at {f}/{x}')
                self.assertGreater(deck.length-radius,.6,f'deck submerged at {f}/{x}')

    def test_road_is_flat_enough_for_wheels(self):
        road=self.root('E07_INBOUND_ROAD')
        dg=bpy.context.evaluated_depsgraph_get()
        eo=road.evaluated_get(dg);mesh=eo.to_mesh()
        zs=[v.co.z for v in mesh.vertices]
        self.assertLess(max(zs)-min(zs),.10,'Round pipe road buries wheels')
        eo.to_mesh_clear()

    def test_dock_opening_in_front_of_camera(self):
        S.frame_set(900)
        c=self.root('A01_CONTAINER').matrix_world
        rear=c@Vector((-1.6,0,0))
        axis=(c.to_3x3()@Vector((-1,0,0))).normalized()
        self.assertGreater((S.camera.matrix_world.translation-rear).dot(axis),1.0,'Camera cannot see open rear')

    def test_final_frame_keeps_both_deliveries_visible(self):
        S.frame_set(1392)
        for name in ['A04_PRIMARY','A05_SECONDARY']:
            p=self.root(name).matrix_world@Vector((0,0,1.5))
            ndc=world_to_camera_view(S,S.camera,p)
            self.assertGreater(ndc.z,0,name)
            self.assertTrue(.04<ndc.x<.96 and .04<ndc.y<.96,f'{name}: {tuple(ndc)}')

    def test_outbound_cart_stays_on_warehouse_floor(self):
        U=self.root('US_FRAME').matrix_world.inverted()
        for f in range(1090,1201):
            S.frame_set(f);p=U@self.root('W09_OUT_CART').matrix_world.translation
            self.assertLess(p.x+.63,68,'Cart beyond supported floor')
            self.assertAlmostEqual(p.z,1.86,delta=.03)
            worker=U@self.root('CH_LOADER').matrix_world.translation
            self.assertGreater(Vector((p.x-worker.x,p.y-worker.y)).length,.8,f'Cart intersects loader f{f}')

    def test_last_load_has_support_and_clear_cargo_slot(self):
        U=self.root('US_FRAME').matrix_world.inverted()
        self.root('CH_LOAD_SUPPORT')
        for f in range(1151,1167):
            S.frame_set(f)
            box=self.root('LAST_BOX_BODY');bottom=min((U@box.matrix_world@Vector(c)).z for c in box.bound_box)
            hand=self.root('CH_LOAD_SUPPORT');top=max((U@hand.matrix_world@Vector(c)).z for c in hand.bound_box)
            self.assertAlmostEqual(bottom,top,delta=.035)
        S.frame_set(1200)
        inv=self.root('A04_PRIMARY').matrix_world.inverted()
        body=self.root('LAST_BOX_BODY')
        corners=[inv@body.matrix_world@Vector(c) for c in body.bound_box]
        self.assertAlmostEqual(min(c.z for c in corners),1.54,delta=.025)
        self.assertLess(max(c.x for c in corners),-1.2,'Last box overlaps existing rear cargo')

    def test_delivery_vehicle_envelopes_clear_destination_buildings(self):
        inv=self.root('US_FRAME').matrix_world.inverted()
        buildings=[o for o in S.objects if o.name.startswith('E12_DESTINATION_')]
        for f in range(1200,1393):
            S.frame_set(f)
            for name in ['A04_PRIMARY','A05_SECONDARY']:
                root=self.root(name)
                body=[o for o in S.objects if o.parent==root and o.type=='MESH']
                pts=[inv@o.matrix_world@Vector(c) for o in body for c in o.bound_box]
                lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
                for ob in buildings:
                    q=[inv@ob.matrix_world@Vector(c) for c in ob.bound_box]
                    blo=[min(p[i] for p in q) for i in range(3)];bhi=[max(p[i] for p in q) for i in range(3)]
                    overlap=all(min(hi[i],bhi[i])-max(lo[i],blo[i])>.01 for i in range(3))
                    self.assertFalse(overlap,f'{name} hits {ob.name} at {f}')

    def test_picking_bin_product_has_support(self):
        S.frame_set(1060)
        inv=self.root('US_FRAME').matrix_world.inverted()
        prod=self.root('W04_PICK_BIN_PRODUCT');shelf=self.root('W04_PICK_BIN_SUPPORT')
        p=[inv@prod.matrix_world@Vector(c) for c in prod.bound_box]
        s=[inv@shelf.matrix_world@Vector(c) for c in shelf.bound_box]
        self.assertAlmostEqual(min(c.z for c in p),max(c.z for c in s),delta=.02)

    def test_crane_cables_have_overhead_trolley_support(self):
        for prefix,frame in [('P01',50),('P02',575)]:
            S.frame_set(frame)
            trolley=self.root(prefix+'_TROLLEY')
            inv=trolley.matrix_world.inverted()
            lo=[min(c[i] for c in trolley.bound_box) for i in range(3)]
            hi=[max(c[i] for c in trolley.bound_box) for i in range(3)]
            for n in range(4):
                cable=self.root(prefix+'_CABLE_'+str(n))
                top=inv@cable.matrix_world@Vector((0,0,.5))
                self.assertTrue(all(lo[i]-.04<=top[i]<=hi[i]+.04 for i in range(3)),f'{prefix} cable {n} unsupported')

    def test_secondary_heading_matches_merge_motion(self):
        root=self.root('A05_SECONDARY')
        for f in range(1263,1309):
            a=self.at(root.name,f-1).translation;b=self.at(root.name,f+1).translation
            self.at(root.name,f)
            forward=root.matrix_world.to_3x3()@Vector((1,0,0))
            self.assertGreater(forward.normalized().dot((b-a).normalized()),.999,f'lateral slide f{f}')

    def test_folded_container_doors_clear_side_panels(self):
        S.frame_set(842)
        inv=self.root('A01_CONTAINER').matrix_world.inverted()
        for name in ['A01_DOOR_LEFT_LEAF','A01_DOOR_RIGHT_LEAF']:
            o=self.root(name)
            corners=[inv@o.matrix_world@Vector(c) for c in o.bound_box]
            self.assertGreater(min(abs(c.y) for c in corners),.785,'Folded door penetrates side panel')

    def test_trailer_frame_does_not_penetrate_dock_wall(self):
        S.frame_set(899)
        inv=self.root('US_FRAME').matrix_world.inverted();o=self.root('TRAILER_CHASSIS')
        self.assertLessEqual(max((inv@o.matrix_world@Vector(c)).x for c in o.bound_box),36.01)

    def test_delivery_vehicles_do_not_overlap_during_merge(self):
        inv=self.root('US_FRAME').matrix_world.inverted()
        for f in range(1200,1393):
            S.frame_set(f);rects=[]
            for name in ['A04_PRIMARY','A05_SECONDARY']:
                r=self.root(name)
                pts=[inv@r.matrix_world@Vector((x,y,1.5)) for x,y in [(-2.1,-1.04),(2.1,-1.04),(2.1,1.04),(-2.1,1.04)]]
                rects.append([Vector((p.x,p.y)) for p in pts])
            separated=False
            for poly in rects:
                for i in range(4):
                    edge=poly[(i+1)%4]-poly[i];axis=Vector((-edge.y,edge.x)).normalized()
                    a=[p.dot(axis) for p in rects[0]];b=[p.dot(axis) for p in rects[1]]
                    if max(a)<min(b) or max(b)<min(a):separated=True
            self.assertTrue(separated,f'Outbound vehicle overlap at {f}')

    def test_unloading_container_stays_inside_vertical_frame(self):
        for f in range(533,633):
            S.frame_set(f);o=self.root('A01_ROOF')
            pts=[world_to_camera_view(S,S.camera,o.matrix_world@Vector(c)) for c in o.bound_box]
            self.assertLess(max(p.y for p in pts),.98,f'Load cropped at frame {f}')

    def test_dock_reverse_is_short_after_doors_open(self):
        start=self.at('A03_TRAILER',849).translation
        end=self.at('A03_TRAILER',890).translation
        self.assertLessEqual((end-start).length,5.5,'Reverse exceeds one proxy vehicle length')
        self.assertLess((self.at('A03_TRAILER',811).translation-start).length,.002)

    def test_inbound_vehicle_clears_raised_warehouse_floor(self):
        inv=self.root('US_FRAME').matrix_world.inverted()
        parts=[o for o in S.objects if o.type=='MESH' and o.parent and o.parent.name in ['A03_TRACTOR','A03_TRAILER']]
        for f in range(649,900):
            S.frame_set(f)
            for o in parts:
                p=[inv@o.matrix_world@Vector(c) for c in o.bound_box]
                lo=[min(c[i] for c in p) for i in range(3)]; hi=[max(c[i] for c in p) for i in range(3)]
                overlap=all(min(hi[i],(68,39,1.86)[i])-max(lo[i],(36,25,.68)[i])>.01 for i in range(3))
                self.assertFalse(overlap,f'{o.name} enters raised floor at {f}')

if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(MasterTests))
    (ROOT/'logs'/('test-result-'+Path(bpy.data.filepath).stem+'.json')).write_text(json.dumps({'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors)},indent=2))
    if not result.wasSuccessful():
        raise SystemExit(1)
