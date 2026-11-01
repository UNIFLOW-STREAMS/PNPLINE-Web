"""Reversible spherical reframe of the existing China loading mechanism.

All original actions, local channels and camera optics survive. The crane and
hoist share one rigid tangent transform. The moving berth and camera share that
same transform until the spreader has disengaged; only then is the vessel fitted
to the restored spherical water. The complete downstream US scene is exact from
native frame253. No source file is saved by this module.
"""
import hashlib
import json
import math
from pathlib import Path

import bpy
from mathutils import Matrix,Quaternion,Vector

ROOT=Path(__file__).resolve().parents[1]
EXCLUDED_ROOTS=('PORT_CRANE_PLACEMENT','PORT_HOIST_PLACEMENT','PORT_SHIP_WATERLINE_CORRECTION',
                'CAM_MASTER','CAM_LOOK_TARGET')
PROTECTED_GLOBAL_ROOTS=('CV_CARRIER_WORLD',)
RIG_NAMES=('CR_COMPACT_GANTRY','CR_SLEW_JIB','CR_TROLLEY_CARRIAGE','CR_SUSPENSION_HEAD',
           'CR_WORKING_CABLE','CR_WORKING_CABLE.001','CR_WORKING_CABLE.002','CR_WORKING_CABLE.003','P01_SPREADER')
ACTOR_NAMES=('A02_SHIP','A01_CONTAINER','W01_NEW_PALLET')
CAMERA_NAMES=('CAM_MASTER','CAM_LOOK_TARGET')
STEP=.125
LOAD_HOLD=75.0
RADIAL_FULL=108.0
CAMERA_ORIENTATION_RETURN=165.0
FADE_START=246.0
EXACT_US=253.0
WATER_RADIUS=140.0
FOOT_ANCHOR=Vector((15.829633951187134,-10.632938861846924,1.2499853372573853))


def _set(scene,t):
    whole=math.floor(t);scene.frame_set(whole,subframe=t-whole)


def _flat(m):return [float(v)for row in m for v in row]
def _error(a,b):return max(abs(x-y)for x,y in zip(_flat(a),_flat(b)))


def _ease(t):
    t=max(0,min(1,t));return t*t*t*(10+t*(-15+6*t))


def _blend(a,b,t):
    if t<=0:return a.copy()
    if t>=1:return b.copy()
    qa,qb=a.to_quaternion(),b.to_quaternion()
    if qa.dot(qb)<0:qb.negate()
    return Matrix.LocRotScale(a.translation.lerp(b.translation,t),qa.slerp(qb,t),Vector((1,1,1)))


def _camera_desired(source,ship_source,berth_correction,rig_world,frame):
    if frame>=EXACT_US:return source.copy()
    if frame<=LOAD_HOLD:return rig_world@source
    translated=source.copy()
    translated.translation+=(berth_correction@ship_source).translation-ship_source.translation
    return _blend(rig_world@source,translated,_ease((frame-LOAD_HOLD)/(CAMERA_ORIENTATION_RETURN-LOAD_HOLD)))


def _action_hashes():
    result={}
    for action in bpy.data.actions:
        data=[]
        for layer in action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    data.append([bag.slot_handle,[[fc.data_path,fc.array_index,fc.extrapolation,
                       [[*k.co,*k.handle_left,*k.handle_right,k.interpolation,k.handle_left_type,k.handle_right_type]for k in fc.keyframe_points]]for fc in bag.fcurves]])
        result[action.name]=hashlib.sha256(json.dumps(data).encode()).hexdigest()
    return result


def _ship_shape(scene):
    inverse=scene.objects['A02_SHIP'].matrix_world.inverted()
    hull=scene.objects['SF_HULL_RED']
    points=[inverse@hull.matrix_world@v.co for v in hull.data.vertices]
    low=min(p.z for p in points)
    bottom=[p for p in points if p.z<low+.001]
    deck=scene.objects['SF_BOW_DECK']
    deckpoints=[inverse@deck.matrix_world@v.co for v in deck.data.vertices]
    def dense(points):
        result=list(points)
        center=sum(points,Vector())/len(points)
        result.append(center)
        for i,a in enumerate(points):
            for b in points[i+1:]:
                result.extend([a.lerp(b,.25),a.lerp(b,.5),a.lerp(b,.75)])
        return result
    return dense(bottom),dense(deckpoints)


def _support(local_matrix,bottom,deck,center):
    depths=[WATER_RADIUS-(local_matrix@p-center).length for p in bottom]
    freeboard=[(local_matrix@p-center).length-WATER_RADIUS for p in deck]
    return {'min_immersion':min(depths),'max_immersion':max(depths),'min_deck_freeboard':min(freeboard)}


def _water_transform(source,center):
    """Rigidly fit source vessel to its XY on the analytic ocean, preserving heading."""
    p=source.translation.copy()
    dx,dy=p.x-center.x,p.y-center.y
    rest=WATER_RADIUS*WATER_RADIUS-dx*dx-dy*dy
    assert rest>0,'CN support left the upper water hemisphere before handoff'
    target=Vector((p.x,p.y,center.z+math.sqrt(rest)))
    normal=(target-center).normalized()
    old_up=source.to_quaternion()@Vector((0,0,1))
    delta=old_up.rotation_difference(normal)
    return Matrix.Translation(target)@delta.to_matrix().to_4x4()@Matrix.Translation(-p)


def _insert(scene,obj,name,collection):
    assert scene.objects.get(name)is None,'Animation reflow already exists'
    assert all(c.mute or c.influence==0 for c in obj.constraints),'Active constraint needs evaluated post-constraint placement'
    parent=obj.parent
    inverse=obj.matrix_parent_inverse.copy()
    basis=obj.matrix_basis.copy()
    helper=bpy.data.objects.new(name,None);collection.objects.link(helper)
    helper.parent=parent;helper.matrix_parent_inverse=Matrix.Identity(4)
    helper.rotation_mode='QUATERNION'
    helper['curvature_owner']='cn-unified-curvature-v001'
    obj.parent=helper;obj.matrix_parent_inverse=inverse
    assert _error(obj.matrix_basis,basis)==0,'Parent adapter changed original local channels'
    return helper,{'name':obj.name,'parent_before':parent.name if parent else None,'parent_after':name,
                   'matrix_parent_inverse_preserved':True,'local_channels_preserved':True}


def _assign(helper,matrix):
    helper.location=matrix.translation
    helper.rotation_quaternion=matrix.to_quaternion().normalized()
    helper.scale=(1,1,1)


def _bulk_action(helper,frames,matrices):
    # Initial insertion uses Blender's current action/slot API, then curves are
    # filled in bulk rather than repeatedly inserting thousands of sorted keys.
    helper.keyframe_insert('location',frame=frames[0])
    helper.keyframe_insert('rotation_quaternion',frame=frames[0])
    positions=[];rotations=[];previous=None
    for matrix in matrices:
        q=matrix.to_quaternion().normalized()
        if previous is not None and previous.dot(q)<0:q.negate()
        previous=q.copy();positions.append(list(matrix.translation));rotations.append(list(q))
    for layer in helper.animation_data.action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for curve in bag.fcurves:
                    values=positions if curve.data_path=='location'else rotations
                    curve.keyframe_points.clear();curve.keyframe_points.add(len(frames))
                    coords=[v for t,row in zip(frames,values)for v in(t,row[curve.array_index])]
                    curve.keyframe_points.foreach_set('co',coords)
                    for key in curve.keyframe_points:key.interpolation='LINEAR'
                    curve.extrapolation='CONSTANT';curve.update()
    helper['identity_from_frame']=EXACT_US


def _snapshot(scene,frames):
    names=RIG_NAMES+ACTOR_NAMES+CAMERA_NAMES
    rows=[]
    camera=scene.objects['CAM_MASTER'];target=scene.objects['CAM_LOOK_TARGET']
    for tick,t in enumerate(frames):
        _set(scene,t)
        rows.append({'frame':t,'world':{n:scene.objects[n].matrix_world.copy()for n in names},
                     'camera_parent':camera.parent.matrix_world.copy()if camera.parent else Matrix.Identity(4),
                     'target_parent':target.parent.matrix_world.copy()if target.parent else Matrix.Identity(4),
                     'lens':camera.data.lens,'shift':[camera.data.shift_x,camera.data.shift_y]})
        if tick%800==0:print('CURVATURE_CAPTURE',t,flush=True)
    late=[]
    for t in range(253,990):
        scene.frame_set(t)
        late.append({'frame':t,'world':{n:scene.objects[n].matrix_world.copy()for n in ACTOR_NAMES+CAMERA_NAMES},
                     'lens':camera.data.lens,'shift':[camera.data.shift_x,camera.data.shift_y]})
    return rows,late


def apply_animation_reflow(scene,layout,helpers,collection):
    """Apply tangent rig adapters using a terrain.SphericalSurface instance.

    Must run while the excluded animated roots and their children still have
    their accepted source transforms. Static geometry may already be reflowed.
    Returns only JSON-serializable provenance and measured safety contracts.
    """
    assert scene.render.fps==30 and scene.frame_end==989
    saved=scene.frame_current+scene.frame_subframe
    _set(scene,0)
    D=layout.matrix_world.copy();I=D.inverted();center=Vector(helpers.center)
    old_actions=_action_hashes()
    shape=_ship_shape(scene)
    anchor=FOOT_ANCHOR.copy()
    target=Vector((anchor.x,anchor.y,helpers.surface(anchor.x,anchor.y)))
    normal=Vector(helpers.normal(anchor.x,anchor.y)).normalized()
    q=Vector((0,0,1)).rotation_difference(normal)
    rig_local=Matrix.Translation(target)@q.to_matrix().to_4x4()@Matrix.Translation(-anchor)
    rig_world=D@rig_local@I
    frames=[i/8 for i in range(int(EXACT_US*8)+1)]
    rows,late=_snapshot(scene,frames)
    corrections=[];support=[]
    for row in rows:
        t=row['frame'];source=I@row['world']['A02_SHIP']
        water=_water_transform(source,center)
        local=_blend(rig_local,water,_ease((t-LOAD_HOLD)/(RADIAL_FULL-LOAD_HOLD)))
        local=_blend(local,Matrix.Identity(4),_ease((t-FADE_START)/(EXACT_US-FADE_START)))
        if t>=EXACT_US:local=Matrix.Identity(4)
        corrections.append(D@local@I if t<EXACT_US else Matrix.Identity(4))
        measure=_support(local@source,*shape,center)
        measure['frame']=t;support.append(measure)
    _set(scene,0)
    changed=[];new_helpers=[]
    for name,new in [('PORT_CRANE_PLACEMENT','CNC_WORKING_CRANE_FRAME'),('PORT_HOIST_PLACEMENT','CNC_HOIST_FRAME')]:
        obj=scene.objects[name];parent=obj.parent.matrix_world.copy()if obj.parent else Matrix.Identity(4)
        helper,change=_insert(scene,obj,new,collection)
        _assign(helper,parent.inverted()@rig_world@parent)
        changed.append(change);new_helpers.append(helper.name)
    moving,change=_insert(scene,scene.objects['PORT_SHIP_WATERLINE_CORRECTION'],'CNC_BERTH_REFLOW',collection)
    changed.append(change);new_helpers.append(moving.name)
    _bulk_action(moving,frames+[989.0],corrections+[Matrix.Identity(4)])
    for name,new,key in [('CAM_MASTER','CNC_CAMERA_REFLOW','camera_parent'),('CAM_LOOK_TARGET','CNC_CAMERA_TARGET_REFLOW','target_parent')]:
        obj=scene.objects[name];helper,change=_insert(scene,obj,new,collection)
        matrices=[row[key].inverted()@_camera_desired(row['world'][name],row['world']['A02_SHIP'],correction,rig_world,row['frame'])@row['world'][name].inverted()@row[key]if row['frame']<EXACT_US else Matrix.Identity(4)
                  for row,correction in zip(rows,corrections)]
        _bulk_action(helper,frames+[989.0],matrices+[Matrix.Identity(4)])
        changed.append(change);new_helpers.append(helper.name)
    # Verify exact same loading-space poses and the complete US tail in-memory.
    rig_error=0.;relative_error=0.;loading_error=0.;camera_error=0.;lens_changes=[]
    samples=[]
    for tick,(row,H)in enumerate(zip(rows,corrections)):
        _set(scene,row['frame'])
        ship=scene.objects['A02_SHIP'].matrix_world.copy()
        for name in RIG_NAMES:
            rig_error=max(rig_error,_error(scene.objects[name].matrix_world,rig_world@row['world'][name]))
        for name in ACTOR_NAMES:
            relative_error=max(relative_error,_error(scene.objects[name].matrix_world,H@row['world'][name]))
        for name in CAMERA_NAMES:
            desired=_camera_desired(row['world'][name],row['world']['A02_SHIP'],H,rig_world,row['frame'])
            camera_error=max(camera_error,_error(scene.objects[name].matrix_world,desired))
        if row['frame']<=LOAD_HOLD:
            for name in ('P01_SPREADER','A01_CONTAINER','W01_NEW_PALLET')+CAMERA_NAMES:
                loading_error=max(loading_error,_error(ship.inverted()@scene.objects[name].matrix_world,
                              row['world']['A02_SHIP'].inverted()@row['world'][name]))
        camera=scene.objects['CAM_MASTER']
        if camera.data.lens!=row['lens']or[camera.data.shift_x,camera.data.shift_y]!=row['shift']:lens_changes.append(row['frame'])
        samples.append({'frame':row['frame'],'eye':list(camera.matrix_world.translation),'q':list(camera.matrix_world.to_quaternion()),
                        'source_eye':list(row['world']['CAM_MASTER'].translation),'source_q':list(row['world']['CAM_MASTER'].to_quaternion()),
                        'ship_eye':list(ship.translation),'ship_q':list(ship.to_quaternion()),
                        'source_ship_eye':list(row['world']['A02_SHIP'].translation),'source_ship_q':list(row['world']['A02_SHIP'].to_quaternion())})
        if tick%800==0:print('CURVATURE_VERIFY',row['frame'],relative_error,flush=True)
    late_error=0.
    for row in late:
        scene.frame_set(row['frame'])
        for name in ACTOR_NAMES+CAMERA_NAMES:
            late_error=max(late_error,_error(scene.objects[name].matrix_world,row['world'][name]))
        camera=scene.objects['CAM_MASTER']
        if camera.data.lens!=row['lens']or[camera.data.shift_x,camera.data.shift_y]!=row['shift']:lens_changes.append(row['frame'])
    new_actions=_action_hashes()
    modified_actions=[n for n,h in old_actions.items()if new_actions.get(n)!=h]
    checks={'original_actions_exact':not modified_actions,'original_camera_optics_exact':not lens_changes,
            'working_rig_shared_rigid_transform':rig_error<.0002,'ship_cargo_shared_transform':relative_error<.0003,
            'camera_compensation_matches_plan':camera_error<.0003,
            'loading_relative_pose_preserved_through75':loading_error<.0002,
            'US_actor_camera_every_frame253_989_exact':late_error==0,
            'all_keel_samples_submerged':min(r['min_immersion']for r in support)>0,
            'deck_above_spherical_water':min(r['min_deck_freeboard']for r in support)>0}
    report={'method':'Rigid radial crane placement; shared berth/camera loading compensation; post-release spherical water support',
            'source_file':bpy.data.filepath,'source_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),
            'ground_radius':helpers.radius,'water_radius':WATER_RADIUS,'sphere_center_local':list(center),
            'working_crane_anchor_old_local':list(anchor),'working_crane_anchor_new_local':list(target),
            'working_crane_radial_up_local':list(normal),'working_crane_rotation_degrees':math.degrees(q.angle),
            'rig_transform_world':_flat(rig_world),'rig_transform_local':_flat(rig_local),
            'loading_shared_rigid_through':LOAD_HOLD,'water_radial_full_from':RADIAL_FULL,
            'camera_orientation_return_window':[LOAD_HOLD,CAMERA_ORIENTATION_RETURN],
            'camera_compensation':'Rigid loading opening; C2 return to original orientation then ship-center translation only; source exact from253',
            'identity_transition':[FADE_START,EXACT_US],'US_exact_from':EXACT_US,'sample_step':STEP,
            'changed_objects':[r['name']for r in changed],'changed_parents':changed,
            'excluded_roots':list(EXCLUDED_ROOTS),'protected_global_roots':list(PROTECTED_GLOBAL_ROOTS),
            'new_helpers':new_helpers,'checks':checks,'pass':all(checks.values()),'modified_original_actions':modified_actions,
            'rig_max_matrix_error':rig_error,'shared_transform_max_matrix_error':relative_error,
            'camera_compensation_max_matrix_error':camera_error,
            'loading_relative_max_matrix_error':loading_error,'US_tail_max_matrix_error':late_error,
            'minimum_hull_immersion':min(support,key=lambda r:r['min_immersion']),
            'minimum_deck_freeboard':min(support,key=lambda r:r['min_deck_freeboard']),
            'water_support_samples':support,
            'loading_note':'Ship/cargo remain one rigid system with the crane until spreader clearance at75, then become strictly radial at108. This preserves the authored lowering motion and its physical contacts.'}
    review=ROOT/'review';review.mkdir(exist_ok=True)
    (review/'animation-reflow.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    (review/'animation-reflow-camera-samples.json').write_text(json.dumps(samples),encoding='utf-8')
    baseline={'source_sha256':report['source_sha256'],'frames':[{'frame':r['frame'],'world':{n:_flat(m)for n,m in r['world'].items()},'lens':r['lens'],'shift':r['shift']}for r in rows],
              'tail':[{'frame':r['frame'],'world':{n:_flat(m)for n,m in r['world'].items()},'lens':r['lens'],'shift':r['shift']}for r in late],
              'source_actions':old_actions}
    (review/'animation-reflow-source.json').write_text(json.dumps(baseline),encoding='utf-8')
    _set(scene,saved)
    print('ANIMATION_REFLOW_RESULT',json.dumps({k:v for k,v in report.items()if k not in ['water_support_samples']}),flush=True)
    assert report['pass'],'Animation reflow preservation failed; see animation-reflow.json'
    return report


def refine_camera_reflow(scene,layout=None):
    """Patch only the two new CNC camera actions on a provisional build.

    The accepted source camera/target matrices come from the immutable source
    cache made before adapter installation. No original action or ship/rig
    adapter is edited. Caller saves the resulting candidate separately.
    """
    review=ROOT/'review'
    baseline=json.loads((review/'animation-reflow-source.json').read_text())
    report=json.loads((review/'animation-reflow.json').read_text())
    assert baseline['source_sha256']==report['source_sha256']
    matrix=lambda values:Matrix([values[i:i+4]for i in range(0,16,4)])
    rig_world=matrix(report['rig_transform_world'])
    saved=scene.frame_current+scene.frame_subframe
    input_sha=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()
    input_actions=_action_hashes()
    records=[];matrices={n:[]for n in CAMERA_NAMES}
    helpers={n:scene.objects['CNC_CAMERA_REFLOW'if n=='CAM_MASTER'else'CNC_CAMERA_TARGET_REFLOW']for n in CAMERA_NAMES}
    frames=[r['frame']for r in baseline['frames']]
    for tick,row in enumerate(baseline['frames']):
        t=row['frame'];_set(scene,t)
        H=scene.objects['CNC_BERTH_REFLOW'].matrix_world.copy()
        ship_source=matrix(row['world']['A02_SHIP'])
        desireds={}
        for name in CAMERA_NAMES:
            source=matrix(row['world'][name])
            desired=_camera_desired(source,ship_source,H,rig_world,t)
            parent=helpers[name].parent.matrix_world.copy()if helpers[name].parent else Matrix.Identity(4)
            correction=parent.inverted()@desired@source.inverted()@parent if t<EXACT_US else Matrix.Identity(4)
            matrices[name].append(correction);desireds[name]=desired
        records.append({'source':row,'desired':desireds})
        if tick%800==0:print('CAMERA_REFINE_PREPARE',t,flush=True)
    for name in CAMERA_NAMES:
        _bulk_action(helpers[name],frames+[989.0],matrices[name]+[Matrix.Identity(4)])
    error=0.;opening_relative_error=0.;samples=[];lens_changes=[]
    validation_samples=[]
    for tick,record in enumerate(records):
        row=record['source'];t=row['frame'];_set(scene,t)
        camera=scene.objects['CAM_MASTER'];ship=scene.objects['A02_SHIP']
        source_camera=matrix(row['world']['CAM_MASTER']);source_ship=matrix(row['world']['A02_SHIP'])
        for name in CAMERA_NAMES:error=max(error,_error(scene.objects[name].matrix_world,record['desired'][name]))
        if t<=LOAD_HOLD:
            opening_relative_error=max(opening_relative_error,_error(ship.matrix_world.inverted()@camera.matrix_world,source_ship.inverted()@source_camera))
        if camera.data.lens!=row['lens']or[camera.data.shift_x,camera.data.shift_y]!=row['shift']:lens_changes.append(t)
        samples.append({'frame':t,'eye':list(camera.matrix_world.translation),'q':list(camera.matrix_world.to_quaternion()),
                        'source_eye':list(source_camera.translation),'source_q':list(source_camera.to_quaternion()),
                        'ship_eye':list(ship.matrix_world.translation),'ship_q':list(ship.matrix_world.to_quaternion()),
                        'source_ship_eye':list(source_ship.translation),'source_ship_q':list(source_ship.to_quaternion())})
        if t in {0.,57.,75.,84.,108.,132.,165.,185.,210.,235.,246.,250.,252.,253.}:
            validation_samples.append({'frame':t,'world':{n:_flat(scene.objects[n].matrix_world)for n in CAMERA_NAMES}})
        if tick%800==0:print('CAMERA_REFINE_VALIDATE',t,error,flush=True)
    late_error=0.
    for row in baseline['tail']:
        _set(scene,row['frame'])
        for name in CAMERA_NAMES:late_error=max(late_error,_error(scene.objects[name].matrix_world,matrix(row['world'][name])))
    current=_action_hashes()
    modified=[n for n,h in baseline['source_actions'].items()if current.get(n)!=h]
    patch={'patched_actions':[helpers[n].animation_data.action.name for n in CAMERA_NAMES],
           'source_sha256':baseline['source_sha256'],'orientation_return_window':[LOAD_HOLD,CAMERA_ORIENTATION_RETURN],
           'compensation_plan':'Preserve exact rigid opening through75; smooth pose blend to original orientation with ship-center translation by165; original camera exact253+',
           'plan_max_matrix_error':error,'opening_relative_max_matrix_error':opening_relative_error,'US_tail_max_matrix_error':late_error,
           'original_actions_changed':modified,'optics_changed_frames':lens_changes,
           'pass':error<.0003 and opening_relative_error<.0003 and late_error==0 and not modified and not lens_changes}
    cached_actions={}
    for name,helper in helpers.items():
        curves=[]
        for layer in helper.animation_data.action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for fc in bag.fcurves:
                        curves.append({'path':fc.data_path,'index':fc.array_index,'co':[[*k.co]for k in fc.keyframe_points]})
        cached_actions[helper.name]={'action_name':helper.animation_data.action.name,'before_hash':input_actions[helper.animation_data.action.name],
                                    'after_hash':current[helper.animation_data.action.name],'curves':curves}
    cache={'input_sha256':input_sha,'source_sha256':baseline['source_sha256'],'actions':cached_actions,
           'validation_samples':validation_samples,'validation_report':patch}
    if patch['pass']:(review/'validated-camera-action-cache.json').write_text(json.dumps(cache),encoding='utf-8')
    report['checks'].pop('ship_cargo_camera_shared_transform',None)
    report['checks']['ship_cargo_shared_transform']=report['shared_transform_max_matrix_error']<.0003
    report['checks']['camera_compensation_matches_plan']=patch['pass']
    report['camera_refinement']=patch
    report['camera_orientation_return_window']=[LOAD_HOLD,CAMERA_ORIENTATION_RETURN]
    report['camera_compensation']=patch['compensation_plan']
    report['method']='Rigid radial crane/loading alignment; post-release spherical vessel support; independently stabilized camera compensation'
    report['pass']=all(report['checks'].values())
    (review/'animation-reflow.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    (review/'animation-camera-refinement.json').write_text(json.dumps(patch,indent=2),encoding='utf-8')
    (review/'animation-reflow-camera-samples.json').write_text(json.dumps(samples),encoding='utf-8')
    _set(scene,saved)
    print('CAMERA_REFINEMENT_RESULT',json.dumps(patch),flush=True)
    assert patch['pass'],'Camera-only refinement failed'
    return patch


def apply_validated_camera_refinement(scene,layout=None):
    """Install the hash-bound, already evaluated two-action patch in seconds."""
    review=ROOT/'review'
    cache=json.loads((review/'validated-camera-action-cache.json').read_text())
    baseline=json.loads((review/'animation-reflow-source.json').read_text())
    assert cache['validation_report']['pass']
    assert hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()==cache['input_sha256']
    assert cache['source_sha256']==baseline['source_sha256']
    before=_action_hashes()
    assert all(before.get(n)==h for n,h in baseline['source_actions'].items()),'Original action changed'
    for name,record in cache['actions'].items():
        helper=scene.objects[name];action=helper.animation_data.action
        assert action.name==record['action_name']and before[action.name]==record['before_hash']
        curves={(fc.data_path,fc.array_index):fc for layer in action.layers for strip in layer.strips for bag in strip.channelbags for fc in bag.fcurves}
        assert len(curves)==len(record['curves'])
        for source in record['curves']:
            curve=curves[(source['path'],source['index'])]
            curve.keyframe_points.clear();curve.keyframe_points.add(len(source['co']))
            curve.keyframe_points.foreach_set('co',[v for pair in source['co']for v in pair])
            for key in curve.keyframe_points:key.interpolation='LINEAR'
            curve.extrapolation='CONSTANT';curve.update()
    after=_action_hashes()
    allowed={record['action_name']for record in cache['actions'].values()}
    changed={n for n,h in before.items()if after.get(n)!=h}
    assert changed==allowed,(changed,allowed)
    assert all(after[record['action_name']]==record['after_hash']for record in cache['actions'].values())
    saved=scene.frame_current+scene.frame_subframe;err=0.
    for row in cache['validation_samples']:
        _set(scene,row['frame'])
        for name,values in row['world'].items():
            expected=Matrix([values[i:i+4]for i in range(0,16,4)])
            err=max(err,_error(scene.objects[name].matrix_world,expected))
    _set(scene,saved)
    assert err<.0003,err
    report=dict(cache['validation_report'])
    report.update({'fast_apply':True,'validated_input_sha256':cache['input_sha256'],
                   'action_hashes_match_validated_cache':True,'sample_pose_error':err,
                   'only_changed_actions':sorted(changed)})
    main=json.loads((review/'animation-reflow.json').read_text())
    main['method']='Rigid radial crane/loading alignment; post-release spherical vessel support; independently stabilized camera compensation'
    main['camera_refinement']=report
    (review/'animation-reflow.json').write_text(json.dumps(main,indent=2),encoding='utf-8')
    (review/'camera-fast-apply.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print('CAMERA_FAST_APPLY',json.dumps(report),flush=True)
    return report
