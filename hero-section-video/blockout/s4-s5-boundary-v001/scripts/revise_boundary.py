"""Bounded camera and user-approved landing/support review. Fresh process required."""
import bpy, sys, json, math, hashlib, argparse
from pathlib import Path
from mathutils import Vector, Matrix

def curves(block):
    ad=block.animation_data
    return [fc for layer in ad.action.layers for strip in layer.strips for bag in strip.channelbags for fc in bag.fcurves] if ad and ad.action else []

def smooth(t):
    t=max(0.,min(1.,t)); return t*t*t*(10+t*(-15+6*t))

def main():
    p=argparse.ArgumentParser(); p.add_argument('--input',required=True); p.add_argument('--output',required=True); p.add_argument('--config',required=True); p.add_argument('--scene',required=True)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]); src=Path(a.input).resolve(); dst=Path(a.output).resolve()
    assert src != dst and Path(bpy.data.filepath).resolve()==src, 'Input/output collision or wrong loaded file'
    cfg=json.loads(Path(a.config).read_text(encoding='utf-8-sig')); assert hashlib.sha256(src.read_bytes()).hexdigest()==cfg['source_sha256']
    s=bpy.data.scenes[a.scene]; bpy.context.window.scene=s; c=s.camera; target=bpy.data.objects['CAM_LOOK_TARGET']; U=bpy.data.objects['US_FRAME'].matrix_world.copy(); inv=U.inverted()
    start,end,boundary=cfg['edit_start'],cfg['edit_end'],cfg['boundary']; anchor=cfg['camera_anchor']; samples=[]
    # Read every source sample before any key edits. Endpoint and outside keys stay untouched.
    for j in range(start*4+1,end*4):
        f=j/4; s.frame_set(math.floor(f),subframe=f%1)
        weight=smooth((f-start)/(boundary-start)) if f<boundary else 1-smooth((f-cfg['return_start'])/(end-cfg['return_start']))
        travel=(inv@bpy.data.objects['A03_TRAILER'].matrix_world).translation-Vector((0,9,0));travel.z=0
        desired=Vector(anchor['position'])+travel; aim=Vector(anchor['target'])+travel
        clearance=smooth((f-660)/24)
        desired.y-=2*clearance;desired.z+=clearance
        # Once beyond the last crane leg, resume a clearer side-quarter follow.
        rejoin=smooth((f-708)/24)
        desired.y+=5*rejoin;desired.z-=rejoin
        # Reveal more of the same warehouse as it grows along the departure road.
        aim.y+=cfg.get('departure_aim_y',0)*smooth((f-boundary)/(cfg['handoff']-boundary))*(1-smooth((f-cfg['handoff'])/32))
        aim.z-=.6*clearance
        pos=(inv@c.matrix_world).translation.lerp(desired,weight); aim=(inv@target.matrix_world).translation.lerp(aim,weight)
        z=(pos-aim).normalized(); x=Vector((0,0,1)).cross(z).normalized(); y=z.cross(x)
        q=(U.to_3x3()@Matrix((x,y,z)).transposed()).to_quaternion()
        # Preserve component hemisphere to avoid interpolation through zero quaternion.
        if q.dot(c.rotation_quaternion)<0:q.negate()
        samples.append((f,U@pos,U@aim,q,c.data.lens*(1-weight)+anchor['lens']*weight))
    protected=[]
    for block in (c,target,c.data):
        for fc in curves(block):
            protected.append((fc, {float(k.co.x):(tuple(k.handle_left),tuple(k.handle_right)) for k in fc.keyframe_points if k.co.x<=start or k.co.x>=end}))
    for block in (c,target,c.data):
        for fc in curves(block):
            for key in list(fc.keyframe_points):
                if start<key.co.x<end:fc.keyframe_points.remove(key,fast=True)
            fc.update()
    for f,pos,aim,q,lens in samples:
        c.location=pos; c.rotation_quaternion=q; target.location=aim; c.data.lens=lens
        c.keyframe_insert('location',frame=f); c.keyframe_insert('rotation_quaternion',frame=f); target.keyframe_insert('location',frame=f); c.data.keyframe_insert('lens',frame=f)
    for block in (c,target,c.data):
        for fc in curves(block):
            for key in fc.keyframe_points:
                if start<key.co.x<end:key.interpolation='LINEAR'
    # Blender recalculates AUTO handles beyond the edited interval even on LINEAR
    # keys. Restore their exact stored coordinates after all insertion/update calls.
    for fc,keys in protected:
        for key in fc.keyframe_points:
            if float(key.co.x) in keys:
                left,right=keys[float(key.co.x)];key.handle_left=left;key.handle_right=right
    if cfg.get('support_correction'):
        sys.path.insert(0,str(Path(__file__).parent));from adjust_support import apply
        apply(s,cfg,curves,smooth)
    s.frame_set(boundary)
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
    bpy.ops.wm.save_as_mainfile(filepath=str(dst)); print('BOUNDARY_SAVED',dst,'samples',len(samples))

if __name__=='__main__':main()
