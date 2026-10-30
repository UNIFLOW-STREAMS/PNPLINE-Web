"""Level the port side shot using a pure optical-axis roll on the accepted v008 path."""
import argparse, hashlib, json, math, sys
from pathlib import Path
import bpy
from mathutils import Matrix, Quaternion, Vector

R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--output',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);out=Path(a.output).resolve()
assert out.is_relative_to(R) and not out.exists()
source=R/'candidate-city-reveal-v008.blend'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='99f3ba32b84e864fc0162432b7cde09840733bffe09a36e23216bd956f88d030'
bpy.ops.wm.open_mainfile(filepath=str(source))
s=bpy.context.scene;c=s.camera
U=s.objects['US_FRAME'].matrix_world.copy()
quay=[U@Vector(p) for p in [(-10,4,.4),(10,4,.4)]]
records={}
for tick in range(1760,2593):
    f=tick/4
    s.frame_set(int(f),subframe=f%1)
    records[f]=(c.matrix_world.copy(),c.parent.matrix_world.copy(),(c.data.shift_x,c.data.shift_y))

def ease(t):
    t=max(0,min(1,t));return t*t*t*(10+t*(-15+6*t))

basis=c.matrix_basis.copy();inverse=c.matrix_parent_inverse.copy()
layer=bpy.data.objects.new('CR_ROLL_LEVEL_CAMERA',None);s.collection.objects.link(layer)
layer.parent=c.parent;layer.rotation_mode='QUATERNION';layer['role']='camera_port_roll_correction'
c.parent=layer;c.matrix_basis=basis;c.matrix_parent_inverse=inverse
last=None;angles={}
for f in [0,439,*sorted(records),649,1392]:
    correction=Matrix.Identity(4);shift=(0.0,0.0);angle=0.0
    if f in records:
        original,P,shift=records[f]
        weight=ease((f-440)/39)*(1-ease((f-600)/48))
        if weight>0:
            q=original.to_quaternion();eye=original.translation
            pa,pb=[q.inverted()@(point-eye) for point in quay]
            dx=pb.x/-pb.z-pa.x/-pa.z;dy=pb.y/-pb.z-pa.y/-pa.z
            quay_angle=(math.atan2(dy,dx)+math.pi/2)%math.pi-math.pi/2
            port_up=(U.to_quaternion()@Vector((0,0,1))).normalized()
            up_angle=-math.atan2(port_up.dot(q@Vector((1,0,0))),port_up.dot(q@Vector((0,1,0))))
            # The long quay edge foreshortens in the rear shot. Hand off to
            # the port normal before that edge becomes a degenerate reference.
            blend=ease((f-512)/40)
            angle=quay_angle if f<=512 else (quay_angle+(up_angle-quay_angle)*blend if f<552 else up_angle)
            angle*=weight
            q=q@Quaternion((0,0,1),angle)
            desired=Matrix.LocRotScale(eye,q,original.to_scale())
            correction=P.inverted()@desired@original.inverted()@P
            x,y=shift;co,si=math.cos(angle),math.sin(angle)
            # Rotate lens offsets with the image so the center viewing ray stays put.
            shift=(co*x+si*y,-si*x+co*y)
    angles[f]=math.degrees(angle)
    layer.location=correction.translation;layer.rotation_quaternion=correction.to_quaternion()
    if last is not None and layer.rotation_quaternion.dot(last)<0:layer.rotation_quaternion.negate()
    last=layer.rotation_quaternion.copy()
    layer.keyframe_insert('location',frame=f);layer.keyframe_insert('rotation_quaternion',frame=f)
    for axis,value in zip(('x','y'),shift):
        layer['lens_shift_'+axis]=float(value);layer.keyframe_insert('['+json.dumps('lens_shift_'+axis)+']',frame=f)
for axis in ('x','y'):
    driver=c.data.driver_add('shift_'+axis).driver
    driver.type='SCRIPTED';driver.expression='offset'
    driver.variables[0].targets[0].id=layer
    driver.variables[0].targets[0].data_path='['+json.dumps('lens_shift_'+axis)+']'
for l in layer.animation_data.action.layers:
    for st in l.strips:
        for bag in st.channelbags:
            for fc in bag.fcurves:
                for key in fc.keyframe_points:key.interpolation='LINEAR'
s.frame_set(497)
s['city_reveal_camera']='v011: v008 eye/forward/timing retained; quay level479-512, port-up handoff512-552, restore600-648'
bpy.ops.wm.save_as_mainfile(filepath=str(out))
info={'source':str(source),'candidate':str(out),'candidate_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'roll_window':[440,648],'quay_level_window':[479,512],'port_up_window':[552,600],'roll_correction_at497_degrees':angles[497],'eye_path':'unchanged from v008','optical_forward':'unchanged from v008','center_view_ray':'unchanged from v008'}
(R/'review'/f'{out.stem}-build.json').write_text(json.dumps(info,indent=2));print(json.dumps(info,indent=2))
