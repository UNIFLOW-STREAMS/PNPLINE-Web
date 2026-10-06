"""Extract evaluated evidence, not authored intentions. Conservative sampling only."""
import bpy, json, csv, math, hashlib
from pathlib import Path
from mathutils import Vector, Quaternion
from bpy_extras.object_utils import world_to_camera_view

ROOT=Path(__file__).resolve().parents[1];S=bpy.context.scene
def vec(v):return [round(float(x),6) for x in v]
def mat(m):return [vec(row) for row in m]
def angle(a,b):return 2*math.acos(min(1,abs(a.dot(b))))
def at(f):
    i=int(f);S.frame_set(i,subframe=f-i)
def transform(o):
    return {'world':mat(o.matrix_world),'position':vec(o.matrix_world.translation),'quaternion_wxyz':vec(o.matrix_world.to_quaternion()),'scale':vec(o.matrix_world.to_scale())}
NAMES=['A01_CONTAINER','A02_SHIP','A03_TRAILER','A03_TRACTOR','A04_PRIMARY','A05_SECONDARY','W01_NEW_PALLET','W01_STORED_PALLET','P01_SPREADER','P02_SPREADER']
OBS={n:bpy.data.objects[n] for n in NAMES}
cam=S.camera;U=bpy.data.objects['US_FRAME'].matrix_world.copy();Ui=U.inverted()
def support(f):
    if f<72:return 'P01_SPREADER'
    if f<=532:return 'A02_SHIP'
    if f<632:return 'P02_SPREADER'
    return 'A03_TRAILER'
def state(f):
    at(f)
    return {'frame':f,'seconds':(f-1)/S.render.fps,'camera':{**transform(cam),'look_target':vec(bpy.data.objects['CAM_LOOK_TARGET'].matrix_world.translation),'forward':vec(cam.matrix_world.to_3x3()@Vector((0,0,-1))),'lens_mm':cam.data.lens,'horizontal_fov_deg':math.degrees(cam.data.angle_x)},'instances':{n:{**transform(o),'instance_id':o.get('instance_id',n)} for n,o in OBS.items()},'container_support':support(f),'container_door_deg':[math.degrees(bpy.data.objects[n].rotation_euler.z) for n in ['A01_DOOR_L','A01_DOOR_R']]}
boundaries=[]
for name,f in [('B12',96),('B23',216),('B34',456),('B45',648),('B56',900),('B67',1200)]:
    a=state(f-1);b=state(f);c=state(f+1)
    p0=Vector(a['camera']['position']);p1=Vector(b['camera']['position']);p2=Vector(c['camera']['position'])
    for objname in NAMES:
        pa=Vector(a['instances'][objname]['position']);pc=Vector(c['instances'][objname]['position'])
        speed=(pc-pa).length*S.render.fps/2
        b['instances'][objname]['speed_m_per_s']=speed
        b['instances'][objname]['motion']='stationary' if speed<.001 else 'moving'
    at(f)
    cm=OBS['A01_CONTAINER'].matrix_world
    b['support_evidence']={'label_basis':'kinematic support phase in saved scene; no physics simulation','relative_to_labelled_support':mat(OBS[support(f)].matrix_world.inverted()@cm),'contact_gaps':{}}
    cup=cm.to_3x3()@Vector((0,0,1));cbot=cm@Vector((0,0,-.75));ctop=cm@Vector((0,0,.75))
    for label,objname in [('ship_seat','P03_DECK_0.8_-1.25'),('trailer_seat','TRAILER_CHASSIS')]:
        seat=bpy.data.objects[objname];top=max((seat.matrix_world@Vector(c)).dot(cup) for c in seat.bound_box)
        b['support_evidence']['contact_gaps'][label+'_vertical_gap']=cbot.dot(cup)-top
    for label in ['P01','P02']:
        spread=bpy.data.objects[label+'_SPREADER_FRAME'];bottom=min((spread.matrix_world@Vector(c)).dot(cup) for c in spread.bound_box)
        b['support_evidence']['contact_gaps'][label+'_bottom_above_container_top']=bottom-ctop.dot(cup)
    q0,q1,q2=[Quaternion(x['camera']['quaternion_wxyz']) for x in [a,b,c]]
    next_target={'B12':'ship / China port','B23':'ship / spherical ocean','B34':'ship / US port','B45':'container / inbound tractor trailer','B56':'open container / inbound waiting area','B67':'primary delivery van / route branches'}[name]
    boundaries.append({'id':name,'state':b,'before':a,'after':c,'velocity_before_m_per_s':vec((p1-p0)*S.render.fps),'velocity_after_m_per_s':vec((p2-p1)*S.render.fps),'rotation_before_deg_per_s':math.degrees(angle(q0,q1))*S.render.fps,'rotation_after_deg_per_s':math.degrees(angle(q1,q2))*S.render.fps,'lens_delta_before_mm':b['camera']['lens_mm']-a['camera']['lens_mm'],'lens_delta_after_mm':c['camera']['lens_mm']-b['camera']['lens_mm'],'next_observer_target_authored_label':next_target,'preview':'preview/master-v001.mp4','stills':[f'review/boundary-{f}-f{x:04}.png' for x in [f-1,f,f+1]]})
(ROOT/'boundary-states.json').write_text(json.dumps(boundaries,ensure_ascii=False,indent=2),encoding='utf-8')

env=[o for o in S.objects if o.get('environment')]
def env_signature():
    h=hashlib.sha256()
    for o in env:
        h.update(o.name.encode());h.update(json.dumps(mat(o.matrix_world)).encode());h.update(str(o.hide_render).encode())
        if o.type=='MESH':
            for v in o.data.vertices:h.update(json.dumps(vec(v.co)).encode())
    return h.hexdigest()
at(1);baseenv=env_signature()
errors=[];records=[];camera_hits=[];proj=[];previous=None;prevship=None
mins={'camera_globe_clearance':1e9,'ship_keel_radius_offset_min':1e9,'ship_keel_radius_offset_max':-1e9,'trailer_hitch_distance_max':0,'camera_step_max':0,'camera_rotation_deg_max':0,'ship_step_max':0}
# Mesh bounding boxes: conservative camera-point + 0.12m clearance. The ocean
# is tested analytically; intended hull/wheel/support contact is not masked.
colliders=[o for o in S.objects if o.type=='MESH' and o.name!='EARTH_CONTINUOUS_OCEAN' and not o.name.startswith('WAKE_')]
localbounds={o.name:([min(v[i] for v in o.bound_box) for i in range(3)],[max(v[i] for v in o.bound_box) for i in range(3)]) for o in colliders}
for f in range(1,S.frame_end+1):
    at(f);cp=cam.matrix_world.translation.copy();cq=cam.matrix_world.to_quaternion()
    ship=OBS['A02_SHIP'].matrix_world
    c=OBS['A01_CONTAINER'].matrix_world
    hitch=(bpy.data.objects['TRACTOR_HITCH'].matrix_world.translation-bpy.data.objects['TRAILER_HITCH'].matrix_world.translation).length
    mins['trailer_hitch_distance_max']=max(mins['trailer_hitch_distance_max'],hitch)
    mins['camera_globe_clearance']=min(mins['camera_globe_clearance'],cp.length-S['radius'])
    if previous:
        mins['camera_step_max']=max(mins['camera_step_max'],(cp-previous[0]).length)
        mins['camera_rotation_deg_max']=max(mins['camera_rotation_deg_max'],math.degrees(angle(cq,previous[1])))
        mins['ship_step_max']=max(mins['ship_step_max'],(ship.translation-prevship).length)
    previous=(cp,cq);prevship=ship.translation.copy()
    for o in colliders:
        if o.hide_render:continue
        p=o.matrix_world.inverted()@cp;lo,hi=localbounds[o.name]
        if all(lo[i]-.12<p[i]<hi[i]+.12 for i in range(3)):
            camera_hits.append({'frame':f,'object':o.name,'local_camera':vec(p)})
    keel=[(ship@Vector((x,0,-.65))).length-S['radius'] for x in [-6.8,0,6.8]]
    mins['ship_keel_radius_offset_min']=min(mins['ship_keel_radius_offset_min'],min(keel))
    mins['ship_keel_radius_offset_max']=max(mins['ship_keel_radius_offset_max'],max(keel))
    record={'frame':f,'camera':vec(cp),'camera_q':vec(cq),'container':vec(c.translation),'container_q':vec(c.to_quaternion()),'support':support(f),'ship':vec(ship.translation),'keel_bow_mid_stern':keel,'trailer':vec(OBS['A03_TRAILER'].matrix_world.translation),'tractor':vec(OBS['A03_TRACTOR'].matrix_world.translation),'outbound_primary':vec(OBS['A04_PRIMARY'].matrix_world.translation),'outbound_secondary':vec(OBS['A05_SECONDARY'].matrix_world.translation),'hitch_error':hitch}
    records.append(record)
    if f in [96,216,456,648,900,1200,1392] and env_signature()!=baseenv:errors.append('Environment changed at '+str(f))
    if 216<=f<=456:
        local=ship.inverted()@cp
        if local.y>=-3:errors.append('Ship camera changed sea side at '+str(f))
    if f in [1,72,160,216,325,380,420,456,510,552,599,632,648,842,900,935,966,1015,1060,1105,1158,1200,1260,1320,1392]:
        for name in ['A02_SHIP','A01_CONTAINER','A03_TRAILER','A04_PRIMARY','A05_SECONDARY','E08_WAREHOUSE']:
            o=bpy.data.objects[name]
            points=[]
            children=[x for x in S.objects if x.type=='MESH' and x.parent==o]
            for child in children:
                points.extend(world_to_camera_view(S,cam,child.matrix_world@Vector(corner)) for corner in child.bound_box)
            if points:
                proj.append({'frame':f,'object':name,'x_min':min(p.x for p in points),'x_max':max(p.x for p in points),'y_min':min(p.y for p in points),'y_max':max(p.y for p in points),'width_pixels':(max(p.x for p in points)-min(p.x for p in points))*S.render.resolution_x})

# Subframe evidence around support switches, doors, tight turns and docking.
subs=[]
for f in [72,77,145,216,510,529,532,555,599,632,637,760,810,811,842,849,890,900,908,952,966,1166,1193,1200]:
    subs.append({'event_frame':f,'samples':[state(f+x) for x in [-.5,-.25,0,.25,.5]]})
(ROOT/'review'/'subframe-states.json').write_text(json.dumps(subs,indent=2),encoding='utf-8')
(ROOT/'review'/'all-frame-states.json').write_text(json.dumps(records,separators=(',',':')),encoding='utf-8')
(ROOT/'review'/'screen-projections.json').write_text(json.dumps(proj,indent=2),encoding='utf-8')
summary={'version':'v001','frames_checked':S.frame_end,'subframe_interval':.25,'environment_objects':len(env),'environment_signature':baseenv,'environment_and_ship_side_errors':errors,'camera_obb_hits':camera_hits,'metrics':mins,'method_limits':['Camera point expanded 0.12m vs object local bounding boxes; not exact mesh collision or continuous swept volume','Ship hull tested bow/mid/stern sample points against exact sphere; no fluid simulation','Dense integer frame keys plus selected quarter-frame samples; no safety certification','Screen projections are visibility bounds, not semantic or occlusion proof'],'source_blend':str(Path(bpy.data.filepath).name)}
(ROOT/'validation.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
inventory=[]
for o in S.objects:
    root=o
    while not root.get('asset_id') and root.parent:root=root.parent
    inventory.append({'object':o.name,'type':o.type,'asset_id':root.get('asset_id'),'instance_id':root.get('instance_id',root.name),'parent':o.parent.name if o.parent else None,'collections':[x.name for x in o.users_collection],'environment':bool(o.get('environment'))})
(ROOT/'review'/'scene-inventory.json').write_text(json.dumps(inventory,indent=2),encoding='utf-8')
print(json.dumps({'frames':S.frame_end,'camera_hits':len(camera_hits),'errors':errors,'metrics':mins},indent=2))
