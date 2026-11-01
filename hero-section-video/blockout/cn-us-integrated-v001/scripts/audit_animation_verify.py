"""Independent semantic-clock, camera and actor integration verification.

Load the corresponding source/candidate, then use -- us, -- cn, or -- verify.
Source caches are evaluated independently from the merge implementation.
"""
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Matrix, Quaternion, Vector

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT/'review'
sys.path.insert(0, str(ROOT.parent/'pacing-33s-v001/scripts'))
from timing import TimeMap
clock = TimeMap()
MODE = sys.argv[sys.argv.index('--')+1]
EXPECTED = {'cn': '19f68c0ccc16c18693df685b47d632d98dd1289cb4f19f744f11e1507e7e0864',
            'us': '3d011d3191df487a44bd96ddce803a436a5ca3f891f91b512550c52f91f001c8'}
STEP = .125
DENSE_END = 257
RIG = ['A02_SHIP', 'A01_CONTAINER', 'W01_NEW_PALLET', 'P01_SPREADER',
       'CR_COMPACT_GANTRY', 'CR_SLEW_JIB', 'CR_TROLLEY_CARRIAGE', 'CR_SUSPENSION_HEAD',
       'CR_WORKING_CABLE', 'CR_WORKING_CABLE.001', 'CR_WORKING_CABLE.002', 'CR_WORKING_CABLE.003']
PAYLOAD = {'A02_SHIP', 'A01_CONTAINER', 'W01_NEW_PALLET'}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def flat(m):
    return [v for row in m for v in row]


def err(a, b):
    return max(abs(x-y) for x,y in zip(a,b))


def set_frame(scene, frame):
    whole = math.floor(frame)
    scene.frame_set(whole, subframe=frame-whole)


def actions():
    result = {}
    for action in bpy.data.actions:
        bags = []
        for layer in action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    curves = [[fc.data_path, fc.array_index, fc.extrapolation,
                               [[*k.co, *k.handle_left, *k.handle_right, k.interpolation,
                                 k.handle_left_type, k.handle_right_type] for k in fc.keyframe_points]]
                              for fc in bag.fcurves]
                    bags.append([bag.slot_handle, curves])
        result[action.name] = hashlib.sha256(json.dumps(bags).encode()).hexdigest()
    return result


def bindings(scene):
    result = {}
    for o in scene.objects:
        ad = o.animation_data
        if ad and ad.action:
            result[o.name] = [ad.action.name, ad.action_slot.handle, ad.action_slot.identifier]
    ad = scene.camera.data.animation_data
    result['__CAMERA_DATA__'] = [ad.action.name, ad.action_slot.handle, ad.action_slot.identifier]
    return result


def optics(camera):
    d = camera.data
    return [d.type, d.lens, d.shift_x, d.shift_y, d.sensor_fit, d.sensor_width, d.sensor_height,
            d.clip_start, d.clip_end, d.ortho_scale, d.dof.use_dof]


def timeline(scene):
    return {'start': scene.frame_start, 'end': scene.frame_end, 'fps': scene.render.fps,
            'fps_base': scene.render.fps_base,
            'markers': sorted([m.frame, m.name] for m in scene.timeline_markers)}


def beneath(obj, names):
    while obj:
        if obj.name in names:
            return True
        obj = obj.parent
    return False


def camera_row(scene, frame):
    cm = scene.camera.matrix_world.copy()
    tm = scene.objects['CAM_LOOK_TARGET'].matrix_world.copy()
    return {'frame': frame, 'camera': flat(cm), 'target': flat(tm),
            'eye': list(cm.translation), 'q': list(cm.to_quaternion().normalized())}


def source_cache(mode):
    scene = bpy.context.scene
    file = Path(bpy.data.filepath)
    assert sha(file) == EXPECTED[mode]
    result = {'file': str(file), 'sha256': EXPECTED[mode], 'timeline': timeline(scene)}
    if mode == 'us':
        audit = json.loads((REVIEW/'animation-source-us.json').read_text())
        names = sorted(audit['objects'])
        result['actions'] = actions()
        result['bindings'] = bindings(scene)
        result['china_mechanism_names'] = [n for n in names if n.startswith('CR_') and not n.startswith('CR_REVEAL_')
                                           or beneath(scene.objects[n], {'P01_SPREADER', 'CR_COMPACT_GANTRY'})]
        result['integer'] = []
        for f in range(990):
            scene.frame_set(f)
            result['integer'].append({'frame': f, 'optics': optics(scene.camera),
                                      'objects': {n: flat(scene.objects[n].matrix_world) for n in names},
                                      'visibility': {n: scene.objects[n].hide_render for n in names}})
    dense = []
    for tick in range(DENSE_END*8+1):
        output_frame = tick/8
        frame = clock.source(output_frame) if mode == 'cn' else output_frame
        set_frame(scene, frame)
        row = camera_row(scene, output_frame)
        if mode == 'cn':
            row['rig'] = {n: flat(scene.objects[n].matrix_world) for n in RIG}
            ship_i = scene.objects['A02_SHIP'].matrix_world.inverted()
            row['relative_load'] = {n: flat(ship_i@scene.objects[n].matrix_world)
                                   for n in ['A01_CONTAINER', 'W01_NEW_PALLET', 'P01_SPREADER']}
        dense.append(row)
        if tick%800 == 0:
            print('CAPTURE', mode, output_frame, flush=True)
    result['dense'] = dense
    (REVIEW/f'animation-source-{mode}-contract.json').write_text(json.dumps(result), encoding='utf-8')
    assert sha(file) == EXPECTED[mode]
    print('CAPTURE_READY', mode, len(dense), flush=True)


def peak(values, times):
    if not values:
        return {'max': 0, 'frame': None}
    idx = max(range(len(values)), key=values.__getitem__)
    order = sorted(values)
    return {'max': values[idx], 'frame': times[idx], 'p95': order[round(.95*(len(order)-1))]}


def motion(rows):
    dt = STEP/30
    p = [Vector(r['eye']) for r in rows]
    q = [Quaternion(r['q']).normalized() for r in rows]
    velocity = [(b-a)/dt for a,b in zip(p,p[1:])]
    acceleration = [(b-a)/dt for a,b in zip(velocity,velocity[1:])]
    jerk = [(b-a)/dt for a,b in zip(acceleration,acceleration[1:])]
    av = []
    flips = []
    for i,(a,b) in enumerate(zip(q,q[1:])):
        if a.dot(b) < 0:
            flips.append(rows[i+1]['frame'])
            b = -b
        delta = (b@a.inverted()).normalized()
        if delta.w < 0:
            delta = -delta
        length = math.sqrt(delta.x*delta.x+delta.y*delta.y+delta.z*delta.z)
        angle = 2*math.atan2(length,delta.w)
        av.append(Vector((delta.x,delta.y,delta.z))*(math.degrees(angle)/(dt*length)) if length > 1e-12 else Vector())
    aa = [(b-a)/dt for a,b in zip(av,av[1:])]
    aj = [(b-a)/dt for a,b in zip(aa,aa[1:])]
    metrics = {}
    for n,values,skip in [('speed_m_s',velocity,1), ('acceleration_m_s2',acceleration,2),
                          ('jerk_m_s3',jerk,3), ('angular_speed_deg_s',av,1),
                          ('angular_acceleration_deg_s2',aa,2), ('angular_jerk_deg_s3',aj,3)]:
        times = [r['frame'] for r in rows[skip:]]
        metrics[n] = peak([v.length for v in values], times)
    return {'metrics': metrics, 'raw_quaternion_sign_change_frames': flips}


def verify():
    scene = bpy.context.scene
    candidate = Path(bpy.data.filepath)
    candidate_hash = sha(candidate)
    us = json.loads((REVIEW/'animation-source-us-contract.json').read_text())
    cn = json.loads((REVIEW/'animation-source-cn-contract.json').read_text())
    assert us['sha256'] == EXPECTED['us'] and cn['sha256'] == EXPECTED['cn']
    now_actions = actions()
    now_bindings = bindings(scene)
    action_changes = [n for n,h in us['actions'].items() if now_actions.get(n) != h]
    binding_changes = [n for n,b in us['bindings'].items() if now_bindings.get(n) != b]
    camera_names = {'CAM_MASTER','CAM_LOOK_TARGET'}
    china = set(us['china_mechanism_names'])
    payload_names = {n for n in us['integer'][0]['objects'] if beneath(scene.objects[n], PAYLOAD)}
    protected_errors = {}
    later_payload_errors = {}
    camera_later_error = 0.0
    target_later_error = 0.0
    optics_changed = []
    visibility_changed = []
    for old in us['integer']:
        f = old['frame']
        scene.frame_set(f)
        if optics(scene.camera) != old['optics']:
            optics_changed.append(f)
        for name, before in old['objects'].items():
            obj = scene.objects[name]
            if obj.hide_render != old['visibility'][name]:
                visibility_changed.append([f,name])
            difference = err(flat(obj.matrix_world), before)
            if name in camera_names:
                if f>=253:
                    if name=='CAM_MASTER': camera_later_error=max(camera_later_error,difference)
                    else: target_later_error=max(target_later_error,difference)
            elif name in payload_names:
                if f>=253 and difference:
                    later_payload_errors[name] = max(later_payload_errors.get(name,0),difference)
            elif name not in china and difference:
                protected_errors[name] = max(protected_errors.get(name,0),difference)
    scene.frame_set(0)
    # Reuse the independently reviewed BVH implementation, not the merge code.
    sys.path.insert(0, str(ROOT.parent/'cn-port-camera-v001/scripts'))
    from verify_camera import GeometryTree, geometry_scope
    static_objects,dynamic_objects = geometry_scope(scene)
    static = GeometryTree(static_objects)
    moving = GeometryTree(dynamic_objects)
    min_distance = {'static': [float('inf'),None,None], 'moving': [float('inf'),None,None]}
    crossings = {}
    dense = []
    cn_camera_error = 0.0
    cn_target_error = 0.0
    cn_rig_errors = {n:0.0 for n in RIG}
    cn_relative_errors = {n:0.0 for n in ['A01_CONTAINER','W01_NEW_PALLET','P01_SPREADER']}
    dense_us_camera_error = 0.0
    dense_us_target_error = 0.0
    ship_outside = []
    ship_behind = []
    previous_eye = None
    for tick, oldcn in enumerate(cn['dense']):
        f = tick/8
        set_frame(scene,f)
        row = camera_row(scene,f)
        dense.append(row)
        if f <= 165:
            cn_camera_error=max(cn_camera_error,err(row['camera'],oldcn['camera']))
            cn_target_error=max(cn_target_error,err(row['target'],oldcn['target']))
        if f>=253:
            dense_us_camera_error=max(dense_us_camera_error,err(row['camera'],us['dense'][tick]['camera']))
            dense_us_target_error=max(dense_us_target_error,err(row['target'],us['dense'][tick]['target']))
        if f <= 252.25:
            for name in RIG:
                cn_rig_errors[name]=max(cn_rig_errors[name],err(flat(scene.objects[name].matrix_world),oldcn['rig'][name]))
        if f<=57:
            inverse=scene.objects['A02_SHIP'].matrix_world.inverted()
            for name in cn_relative_errors:
                cn_relative_errors[name]=max(cn_relative_errors[name],err(flat(inverse@scene.objects[name].matrix_world),oldcn['relative_load'][name]))
        ship=scene.objects['A02_SHIP']
        screen=world_to_camera_view(scene,scene.camera,ship.matrix_world@Vector((0,0,2)))
        if f>=165:
            if screen.z<=0:ship_behind.append(f)
            if not(0<=screen.x<=1 and 0<=screen.y<=1):ship_outside.append(f)
        eye=scene.camera.matrix_world.translation.copy()
        corners=[scene.camera.matrix_world@(p*(scene.camera.data.clip_start/abs(p.z)))
                 for p in scene.camera.data.view_frame(scene=scene)]
        rays=[('near',eye,p)for p in corners]+[('near_center',eye,sum(corners,Vector())/4)]
        if previous_eye is not None:rays.append(('swept',previous_eye,eye))
        previous_eye=eye
        points=[p for kind,a,b in rays for p in[a,b]]
        bounds=([min(p[i]for p in points)for i in range(3)],[max(p[i]for p in points)for i in range(3)])
        moving.update(bounds,eye,min_distance['moving'][0])
        for label,tree in [('static',static),('moving',moving)]:
            for kind,a,b in rays:
                name=tree.ray(a,b)
                if name:crossings.setdefault(label+'|'+kind+'|'+name,[]).append(f)
            nearest=tree.nearest(eye)
            if nearest and nearest[1]<min_distance[label][0]:min_distance[label]=[nearest[1],f,nearest[0]]
        if tick%640==0:print('INTEGRATED_DENSE',f,len(crossings),flush=True)
    join_metrics={}
    for boundary in [165,253]:
        select=lambda rows:[r for r in rows if boundary-4<=r['frame']<=boundary+4]
        join_metrics[str(boundary)]={'integrated':motion(select(dense)), 'cn':motion(select(cn['dense'])),
                                    'us':motion(select(us['dense']))}
    checks={'all_US_actions_exact':not action_changes,'all_original_US_action_slots_exact':not binding_changes,
            'US_timeline_markers_exact':timeline(scene)==us['timeline'],
            'US_optics_all_990_frames_exact':not optics_changed,
            'US_visibility_all_990_frames_exact':not visibility_changed,
            'US_unaffected_animated_roots_all_frames_exact':not protected_errors,
            'US_ship_and_payload_from253_exact':not later_payload_errors,
            'US_camera_target_from253_integer_and_subframe_exact':max(camera_later_error,target_later_error,dense_us_camera_error,dense_us_target_error)==0,
            'CN_camera_target_through165_under_1e_minus4':max(cn_camera_error,cn_target_error)<1e-4,
            'CN_rig_retiming_under_1mm':max(cn_rig_errors.values())<.001,
            'CN_loading_relative_pose_retiming_under_1mm':max(cn_relative_errors.values())<.001,
            'camera_swept_eye_nearplane_clear':not crossings,
            'ship_in_front_during_camera_handoff':not ship_behind}
    report={'file':str(candidate),'sha256':candidate_hash,'source_sha256':EXPECTED,
            'checks':checks,'pass':all(checks.values()),'actions_changed':action_changes,'bindings_changed':binding_changes,
            'protected_root_errors':protected_errors,'later_payload_errors':later_payload_errors,
            'payload_names_including_children':sorted(payload_names),
            'camera_errors':{'CN_early_camera':cn_camera_error,'CN_early_target':cn_target_error,
                             'US_later_camera':camera_later_error,'US_later_target':target_later_error,
                             'US_dense_handoff_camera':dense_us_camera_error,'US_dense_handoff_target':dense_us_target_error},
            'CN_rig_errors':cn_rig_errors,'CN_load_relative_errors':cn_relative_errors,
            'optics_changed_frames':optics_changed,'visibility_changes':visibility_changed,
            'join_motion_metrics':join_metrics,'motion_full':motion(dense),
            'ship_center_outside_frame_during_handoff':ship_outside,'ship_behind_camera_frames':ship_behind,
            'geometry':{'scope':'China static meshes and China crane/ship/cargo moving meshes; water and curve-only geometry excluded',
                        'static_mesh_count':len(static_objects),'dynamic_mesh_count':len(dynamic_objects),
                        'sample_count':len(dense),'step':STEP,'crossings':crossings,'minimum_eye_surface_distance':min_distance},
            'measurement_policy':'Camera/actor agreement tolerances cover float32 retiming interpolation (audit fractional actor error <=0.00055). Join speed/acceleration/jerk are source-comparative measurements, not arbitrary artistic pass gates.'}
    (REVIEW/'animation-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    (REVIEW/'animation-integrated-camera-samples.json').write_text(json.dumps({'sha256':candidate_hash,'rows':dense}),encoding='utf-8')
    assert sha(candidate)==candidate_hash
    print('INTEGRATED_ANIMATION_CHECKS',json.dumps(checks),flush=True)
    assert report['pass'],'Integration animation verification failed; see report'


def refresh_integer_classification():
    """Recheck the corrected payload-descendant scope; reuse dense evidence only at identical hash."""
    scene=bpy.context.scene
    report=json.loads((REVIEW/'animation-verification.json').read_text())
    assert sha(bpy.data.filepath)==report['sha256'], 'Dense evidence belongs to a different file'
    us=json.loads((REVIEW/'animation-source-us-contract.json').read_text())
    china=set(us['china_mechanism_names'])
    payload={n for n in us['integer'][0]['objects'] if beneath(scene.objects[n],PAYLOAD)}
    protected={}
    later={}
    for old in us['integer']:
        frame=old['frame']
        scene.frame_set(frame)
        for name,before in old['objects'].items():
            if name in {'CAM_MASTER','CAM_LOOK_TARGET'} or name in china:
                continue
            difference=err(flat(scene.objects[name].matrix_world),before)
            if name in payload:
                if frame>=253 and difference:
                    later[name]=max(later.get(name,0),difference)
            elif difference:
                protected[name]=max(protected.get(name,0),difference)
    report['protected_root_errors']=protected
    report['later_payload_errors']=later
    report['payload_names_including_children']=sorted(payload)
    report['checks']['US_unaffected_animated_roots_all_frames_exact']=not protected
    report['checks']['US_ship_and_payload_from253_exact']=not later
    report['pass']=all(report['checks'].values())
    report['verification_note']='The payload preservation scope includes all original animated descendants (container doors and ship wake). Corrected scope rerun across all 990 integer frames; unchanged dense camera/rig/collision evidence retained only after identical candidate SHA256 assertion.'
    (REVIEW/'animation-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print('INTEGER_SCOPE_RECHECK',json.dumps({'payload_names':sorted(payload),'protected_errors':protected,'later_errors':later,'pass':report['pass']}),flush=True)
    assert report['pass']


if __name__ == '__main__':
    if MODE in {'cn','us'}:
        source_cache(MODE)
    elif MODE=='verify':
        verify()
    elif MODE=='refresh_integer':
        refresh_integer_classification()
    else:
        raise ValueError(MODE)
