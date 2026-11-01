"""Independent read-only animation, loading and camera-clearance audit.

Run on the saved curvature candidate. Every report is bound to its file hash.
Numerical motion evidence is compared with the immutable accepted source.
"""
import argparse
import ast
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Matrix,Quaternion,Vector
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[1]
REVIEW=ROOT/'review'
SOURCE=ROOT.parent/'cn-city-expansion-v001/pnpline-cn-city-expansion-v001.blend'
SOURCE_SHA='c9da20e19f2cf732245df77c178b1fa85dae00753884ea3c586327a63cbe75bb'
ACTORS=('A02_SHIP','A01_CONTAINER','W01_NEW_PALLET')
CAMERAS=('CAM_MASTER','CAM_LOOK_TARGET')
RIG=('CR_COMPACT_GANTRY','CR_SLEW_JIB','CR_TROLLEY_CARRIAGE','CR_SUSPENSION_HEAD',
     'CR_WORKING_CABLE','CR_WORKING_CABLE.001','CR_WORKING_CABLE.002','CR_WORKING_CABLE.003','P01_SPREADER')
MOVING=set(ACTORS)|set(RIG)


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def matrix(v):return Matrix([v[i:i+4]for i in range(0,16,4)])
def flat(m):return [float(v)for row in m for v in row]
def error(a,b):return max(abs(x-y)for x,y in zip(flat(a),flat(b)))
def set_frame(s,t):s.frame_set(math.floor(t),subframe=t%1)
def beneath(o,names):
    while o:
        if o.name in names:return True
        o=o.parent
    return False
def visible(o):return not o.hide_render and not all(c.hide_render for c in o.users_collection)
def ease(t):
    t=max(0,min(1,t));return t*t*t*(10+t*(-15+6*t))
def blend(a,b,t):
    if t<=0:return a.copy()
    if t>=1:return b.copy()
    qa,qb=a.to_quaternion(),b.to_quaternion()
    if qa.dot(qb)<0:qb.negate()
    return Matrix.LocRotScale(a.translation.lerp(b.translation,t),qa.slerp(qb,t),Vector((1,1,1)))
def action_hashes():
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


# Reuse the independently audited BVH utility, not the implementation under test.
tree=ast.parse((ROOT.parent/'cn-port-camera-v001/scripts/verify_camera.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef)and n.name=='GeometryTree'],type_ignores=[]),'camera_bvh_utility','exec'),globals())
motion_tree=ast.parse((ROOT/'scripts/audit_animation_motion.py').read_text())
exec(compile(ast.Module(body=[n for n in motion_tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'motion_metrics_utility','exec'),globals())


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--skip-geometry',action='store_true')
    parser.add_argument('--full-dense',action='store_true')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]if '--'in sys.argv else[])
    scene=bpy.context.scene;candidate=Path(bpy.data.filepath)
    candidate_sha=sha(candidate)
    assert sha(SOURCE)==SOURCE_SHA,'Immutable source file changed'
    baseline=json.loads((REVIEW/'animation-reflow-source.json').read_text())
    plan=json.loads((REVIEW/'animation-reflow.json').read_text())
    assert baseline['source_sha256']==SOURCE_SHA
    original_actions=baseline['source_actions'];current_actions=action_hashes()
    modified_actions=[n for n,h in original_actions.items()if current_actions.get(n)!=h]
    cache=json.loads((REVIEW/'validated-camera-action-cache.json').read_text())
    camera_cache_exact=all(current_actions.get(r['action_name'])==r['after_hash']for r in cache['actions'].values())
    scene.frame_set(0)
    D=scene.objects['SF_CN_LAYOUT'].matrix_world.copy();I=D.inverted()
    C=Vector(plan['sphere_center_local']);rig_world=matrix(plan['rig_transform_world'])
    camera=scene.objects['CAM_MASTER'];ship=scene.objects['A02_SHIP']
    ship_inverse=ship.matrix_world.inverted()
    hull=scene.objects['SF_HULL_RED'];deck=scene.objects['SF_BOW_DECK']
    hp=[ship_inverse@hull.matrix_world@v.co for v in hull.data.vertices]
    lowest=min(p.z for p in hp);bottom=[p for p in hp if p.z<lowest+.001]
    dp=[ship_inverse@deck.matrix_world@v.co for v in deck.data.vertices]
    def interior_samples(points):
        result=list(points);result.append(sum(points,Vector())/len(points))
        for i,a in enumerate(points):
            for b in points[i+1:]:result.extend([a.lerp(b,t)for t in(.25,.5,.75)])
        return result
    bottom=interior_samples(bottom);dp=interior_samples(dp)
    static_objects=[];dynamic_objects=[]
    for obj in scene.objects:
        if obj.type not in{'MESH','CURVE','FONT'}or not visible(obj):continue
        if any(word in obj.name.upper()for word in('WATER','OCEAN','WAVE','CAMERA_PATH','ROUTE_GUIDE')):continue
        if beneath(obj,MOVING):dynamic_objects.append(obj)
        elif beneath(obj,{'CN_FRAME','SF_CN_LAYOUT','PORT_MODEL_ROOT'})or obj.name.startswith('CNC_'):static_objects.append(obj)
    static=moving=None
    if not args.skip_geometry:
        print('ANIMATION_GEOMETRY_SCOPE',len(static_objects),len(dynamic_objects),flush=True)
        static=GeometryTree(static_objects);moving=GeometryTree(dynamic_objects)
    errors={'rig_shared_transform':0.,'actors_shared_transform':0.,'loading_relative':0.,'camera_plan':0.,'US_tail':0.,'US_dense_handoff':0.}
    optics_changes=[];camera_rows=[];ship_rows=[];old_camera_rows=[];old_ship_rows=[]
    support=[];crossings={};actor_contacts={};screen=[]
    nearest={'static':{'distance':1e30},'moving':{'distance':1e30}}
    previous_eye=None;late_orientation_error=0.
    for index,row in enumerate(baseline['frames']):
        t=row['frame']
        if not args.full_dense and index%4!=0 and not any(abs(t-b)<=4 for b in(75,108,165,246,253)):continue
        set_frame(scene,t)
        old={n:matrix(m)for n,m in row['world'].items()}
        H=scene.objects['CNC_BERTH_REFLOW'].matrix_world.copy()
        for name in RIG:errors['rig_shared_transform']=max(errors['rig_shared_transform'],error(scene.objects[name].matrix_world,rig_world@old[name]))
        for name in ACTORS:errors['actors_shared_transform']=max(errors['actors_shared_transform'],error(scene.objects[name].matrix_world,H@old[name]))
        for name in CAMERAS:
            source=old[name]
            if t<=75:desired=rig_world@source
            elif t>=253:desired=source
            else:
                translated=source.copy();translated.translation+=(H@old['A02_SHIP']).translation-old['A02_SHIP'].translation
                desired=blend(rig_world@source,translated,ease((t-75)/90))
            errors['camera_plan']=max(errors['camera_plan'],error(scene.objects[name].matrix_world,desired))
        if t<=75:
            for name in('P01_SPREADER','A01_CONTAINER','W01_NEW_PALLET')+CAMERAS:
                errors['loading_relative']=max(errors['loading_relative'],error(ship.matrix_world.inverted()@scene.objects[name].matrix_world,old['A02_SHIP'].inverted()@old[name]))
        if camera.data.lens!=row['lens']or[camera.data.shift_x,camera.data.shift_y]!=row['shift']:optics_changes.append(t)
        cm=camera.matrix_world.copy();sm=ship.matrix_world.copy()
        camera_rows.append({'frame':t,'eye':list(cm.translation),'q':list(cm.to_quaternion())})
        ship_rows.append({'frame':t,'eye':list(sm.translation),'q':list(sm.to_quaternion())})
        old_camera_rows.append({'frame':t,'eye':list(old['CAM_MASTER'].translation),'q':list(old['CAM_MASTER'].to_quaternion())})
        old_ship_rows.append({'frame':t,'eye':list(old['A02_SHIP'].translation),'q':list(old['A02_SHIP'].to_quaternion())})
        if t>=165:late_orientation_error=max(late_orientation_error,norm(deltaq(list(old['CAM_MASTER'].to_quaternion()),list(cm.to_quaternion()))))
        local_ship=I@sm
        support.append({'frame':t,'min_immersion':min(140-(local_ship@p-C).length for p in bottom),
                        'min_freeboard':min((local_ship@p-C).length-140 for p in dp),
                        'radial_angle_degrees':math.degrees((local_ship.to_quaternion()@Vector((0,0,1))).angle((local_ship.translation-C).normalized()))})
        if t>=117:
            p=world_to_camera_view(scene,camera,sm@Vector((0,0,2)))
            screen.append({'frame':t,'xyz':list(p)})
        if static is not None:
            eye=cm.translation.copy()
            corners=[cm@(p*(camera.data.clip_start/abs(p.z)))for p in camera.data.view_frame(scene=scene)]
            rays=[('near_center',eye,sum(corners,Vector())/4)]+[('near_corner',eye,p)for p in corners]
            if previous_eye is not None:rays.append(('swept_eye',previous_eye,eye))
            ps=[p for kind,a,b in rays for p in(a,b)]
            bounds=([min(p[i]for p in ps)for i in range(3)],[max(p[i]for p in ps)for i in range(3)])
            moving.update(bounds,eye,nearest['moving']['distance'])
            for label,geo in [('static',static),('moving',moving)]:
                for kind,a,b in rays:
                    name=geo.ray(a,b)
                    if name:crossings.setdefault(label+' | '+kind+' | '+name,[]).append(t)
                near=geo.nearest(eye)
                if near and near[1]<nearest[label]['distance']:nearest[label]={'distance':near[1],'frame':t,'object':near[0]}
            previous_eye=eye
            # Actor/terrain penetration sweep every half frame. Rebuild only
            # mesh objects within the broadphase of the non-crane actor group.
            if index%4==0:
                actor_objects=[o for o in dynamic_objects if beneath(o,set(ACTORS)|{'P01_SPREADER'})]
                ps=[o.matrix_world@Vector(p)for o in actor_objects for p in o.bound_box]
                ab=([min(p[i]for p in ps)for i in range(3)],[max(p[i]for p in ps)for i in range(3)])
                moving.update(ab,sm.translation,0)
                if moving.tree and static.tree:
                    for a,b in static.tree.overlap(moving.tree):
                        an,bn=static.names[a],moving.names[b]
                        if beneath(scene.objects[bn],set(ACTORS)|{'P01_SPREADER'}):actor_contacts.setdefault(an+' | '+bn,set()).add(t)
        if index%400==0:print('ANIMATION_DENSE',t,errors,'camera_crossings',len(crossings),'actor_pairs',len(actor_contacts),flush=True)
    extra=json.loads((REVIEW/'animation-source-handoff-dense.json').read_text())
    for row in extra:
        t=row['frame']
        if t<=253:continue
        set_frame(scene,t)
        for name,key,rows,olds in [('CAM_MASTER','camera',camera_rows,old_camera_rows),('A02_SHIP','ship',ship_rows,old_ship_rows)]:
            m=scene.objects[name].matrix_world
            rows.append({'frame':t,'eye':list(m.translation),'q':list(m.to_quaternion())});olds.append(row[key])
            errors['US_dense_handoff']=max(errors['US_dense_handoff'],max(abs(a-b)for a,b in zip(m.translation,row[key]['eye'])),norm(deltaq(list(m.to_quaternion()),row[key]['q'])))
    for row in baseline['tail']:
        set_frame(scene,row['frame'])
        for name in ACTORS+CAMERAS:errors['US_tail']=max(errors['US_tail'],error(scene.objects[name].matrix_world,matrix(row['world'][name])))
        if camera.data.lens!=row['lens']or[camera.data.shift_x,camera.data.shift_y]!=row['shift']:optics_changes.append(row['frame'])
    joins={}
    for boundary in(75,108,165,246,253):
        joins[str(boundary)]={}
        for name,rows in [('camera',camera_rows),('source_camera',old_camera_rows),('ship',ship_rows),('source_ship',old_ship_rows)]:
            select=[r for r in rows if boundary-4<=r['frame']<=boundary+4]
            joins[str(boundary)][name+'_dense']=metrics(select,.125)
            joins[str(boundary)][name+'_native']=metrics([r for r in select if r['frame'].is_integer()],1)
    checks={'original_actions_exact':not modified_actions,'original_camera_optics_all_frames_exact':not optics_changes,
            'camera_actions_match_full_dense_validated_cache':camera_cache_exact,
            'rig_rigid_transform_preserved':errors['rig_shared_transform']<.0003,
            'ship_cargo_shared_transform_preserved':errors['actors_shared_transform']<.0003,
            'crane_loading_and_opening_relative_pose_preserved_through75':errors['loading_relative']<.0003,
            'camera_compensation_matches_revised_plan':errors['camera_plan']<.0003,
            'US_actors_camera_target_all_frames253_989_exact':errors['US_tail']==0,
            'US_dense_camera_ship_handoff_exact':errors['US_dense_handoff']<1e-10,
            'keel_remains_submerged':min(r['min_immersion']for r in support)>0,
            'deck_remains_above_water':min(r['min_freeboard']for r in support)>0,
            'camera_added_rotation_exactly_released_by165':late_orientation_error<.001,
            'camera_late_angular_acceleration_no_new_spike':all(joins[str(b)]['camera_native']['angular_acceleration_deg_s2']['max']<=joins[str(b)]['source_camera_native']['angular_acceleration_deg_s2']['max']+.1 for b in(246,253)),
            'camera_does_not_cross_visible_geometry':not crossings if static is not None else False,
            'moving_actors_do_not_intersect_static_geometry':not actor_contacts if static is not None else False}
    report={'file':str(candidate),'sha256':candidate_sha,'source_sha256':SOURCE_SHA,
            'checks':checks,'pass':all(checks.values()),'matrix_errors':errors,'source_actions_changed':modified_actions,
            'optics_changed_frames':optics_changes,'world_sampling':'Every half frame plus 1/8 frame in +-4-frame boundary windows; dense cache tied to exact final camera-action hashes'if not args.full_dense else'Every 1/8 frame',
            'actor_collision_interval':.5,'dense_boundary_frames':[75,108,165,246,253],'US_tail_frames':[253,989],
            'maximum_camera_orientation_difference_from165_degrees':late_orientation_error,
            'minimum_immersion':min(support,key=lambda r:r['min_immersion']),
            'minimum_freeboard':min(support,key=lambda r:r['min_freeboard']),
            'maximum_post108_radial_angle':max(r['radial_angle_degrees']for r in support if 108<=r['frame']<=246),
            'camera_geometry_clearance':nearest,'camera_geometry_crossings':crossings,
            'actor_static_contacts':{k:sorted(v)for k,v in actor_contacts.items()},
            'motion_joins':joins,'motion_review_note':'Source-comparative native-frame derivatives determine visual changes; dense derivatives additionally expose the original float32 transform quantization. No arbitrary derivative threshold is treated as a creative-quality verdict.',
            'ship_tracking':{'bounds':[[min(r['xyz'][i]for r in screen),max(r['xyz'][i]for r in screen)]for i in range(3)],
                             'behind_camera_frames':[r['frame']for r in screen if r['xyz'][2]<=0],
                             'center_outside_frames':[r['frame']for r in screen if not(0<=r['xyz'][0]<=1 and 0<=r['xyz'][1]<=1)]},
            'geometry_scope':{'static_objects':len(static_objects),'moving_objects':len(dynamic_objects),
                              'excluded':'Ocean/water/waves and hidden geometry. Camera rays cover near plane and continuous eye motion; actor sweep covers vessel, carried container, pallet and spreader against static China ground and structures.'}}
    assert sha(candidate)==candidate_sha,'Candidate file changed during the audit'
    (REVIEW/'animation-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    (REVIEW/'animation-verified-camera-samples.json').write_text(json.dumps({'sha256':candidate_sha,'camera':camera_rows,'source_camera':old_camera_rows,'ship':ship_rows,'source_ship':old_ship_rows}),encoding='utf-8')
    print('ANIMATION_VERIFICATION',json.dumps({'sha256':candidate_sha,'checks':checks,'errors':errors,'camera_clearance':nearest,'contacts':len(actor_contacts)}),flush=True)
    assert report['pass'],'See animation-verification.json for failed checks'


if __name__=='__main__':main()
