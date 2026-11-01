"""Support the shared departing ship group on the existing harbor water.

Original actor/cargo/pallet actions and the static ocean are left untouched.
The new shared parent is identity through f216 and from f360 onward.
"""
import bpy
import json
import math
import statistics
from pathlib import Path
from mathutils import Vector, Matrix, Quaternion
from mathutils.bvhtree import BVHTree


ACTORS=('A02_SHIP','A01_CONTAINER','W01_NEW_PALLET')


def smooth(t):
    t=max(0.0,min(1.0,t))
    return t*t*t*(10+t*(-15+6*t))


def ocean_tree(scene,inverse):
    ocean=scene.objects['EARTH_CONTINUOUS_OCEAN']
    matrix=inverse@ocean.matrix_world
    return BVHTree.FromPolygons([matrix@v.co for v in ocean.data.vertices],
                                [tuple(p.vertices)for p in ocean.data.polygons])


def water_at(tree,p):
    hit=tree.ray_cast(Vector((p.x,p.y,120)),Vector((0,0,-1)))[0]
    if hit is None:raise RuntimeError('No ocean under ship sample '+str(p))
    return hit.z


def perimeter_points(points):
    center=sum(points,Vector())/len(points)
    result=[center]
    for a,b in zip(points,points[1:]+points[:1]):
        for i in range(8):
            p=a.lerp(b,i/8)
            result.extend([p,p.lerp(center,.5)])
    return result


def ship_geometry(scene):
    ship=scene.objects['A02_SHIP'];inverse=ship.matrix_world.inverted()
    red=scene.objects['SF_HULL_RED']
    points=[inverse@red.matrix_world@v.co for v in red.data.vertices]
    low=min(v.z for v in points)
    bottom=perimeter_points([v for v in points if v.z<low+.01])
    deck=scene.objects['SF_BOW_DECK']
    deckpoints=[inverse@deck.matrix_world@v.co for v in deck.data.vertices]
    return bottom,perimeter_points(deckpoints)


def support_measure(matrix,bottom,deck,water):
    bottom_world=[matrix@p for p in bottom]
    depths=[water_at(water,p)-p.z for p in bottom_world]
    freeboard=[p.z-water_at(water,p)for p in (matrix@v for v in deck)]
    return {'min_immersion':min(depths),'median_immersion':statistics.median(depths),
            'max_immersion':max(depths),'min_deck_freeboard':min(freeboard),
            'wet_samples':sum(v>0 for v in depths),'total_samples':len(depths)}


def mesh_tree(objects,inverse):
    vertices=[];polygons=[];names=[]
    for obj in objects:
        offset=len(vertices);matrix=inverse@obj.matrix_world
        vertices.extend(matrix@v.co for v in obj.data.vertices)
        polygons.extend(tuple(offset+i for i in p.vertices)for p in obj.data.polygons)
        names.extend([obj.name]*len(obj.data.polygons))
    return BVHTree.FromPolygons(vertices,polygons),names


def descendant(obj,names):
    while obj:
        if obj.name in names:return True
        obj=obj.parent
    return False


def fit_rotation(matrix,water):
    p=matrix.translation
    heading=Vector((matrix[0][0],matrix[1][0],0)).normalized()
    side=Vector((-heading.y,heading.x,0))
    # A symmetric 15-point footprint fit suppresses individual ocean facets.
    samples=[]
    for x in [-6,-3,0,3,6]:
        for y in [-2,0,2]:
            h=water_at(water,p+heading*x+side*y)
            samples.append((x,y,h))
    ax=sum(x*h for x,y,h in samples)/sum(x*x for x,y,h in samples)
    ay=sum(y*h for x,y,h in samples)/sum(y*y for x,y,h in samples)
    target_up=Vector((-heading.x*ax-side.x*ay,-heading.y*ax-side.y*ay,1)).normalized()
    current_up=matrix.to_quaternion()@Vector((0,0,1))
    q=current_up.rotation_difference(target_up)
    if q.w<0:q.negate()
    return q


def build_ship_support(scene,layout=None):
    layout=layout or scene.objects['SF_CN_LAYOUT']
    old_frame=scene.frame_current;old_subframe=scene.frame_subframe
    scene.frame_set(0)
    D=layout.matrix_world.copy();I=D.inverted();rotation=D.to_quaternion()
    water=ocean_tree(scene,I)
    bottom,deck=ship_geometry(scene)
    raw=[];source=[]
    anchor_frames=[0,72,156,216,360,400,648,1392]
    anchors={}
    for f in anchor_frames:
        scene.frame_set(f)
        anchors[f]={n:scene.objects[n].matrix_world.copy()for n in ACTORS}
    for f in range(361):
        scene.frame_set(f)
        matrix=I@scene.objects['A02_SHIP'].matrix_world
        q=fit_rotation(matrix,water)
        rv=q.axis*q.angle if abs(q.angle)>1e-8 else Vector()
        pivot=matrix.translation
        adjusted=Matrix.Translation(pivot)@q.to_matrix().to_4x4()@Matrix.Translation(-pivot)@matrix
        measure=support_measure(adjusted,bottom,deck,water)
        # Tiny downward draft adjustment only when the fitted pose needs it.
        dz=min(0.0,max(-.4,measure['min_immersion']-.38))
        raw.append((rv,dz))
        source.append({'matrix':matrix.copy(),'world_pivot':scene.objects['A02_SHIP'].matrix_world.translation.copy(),
                       'relative':[scene.objects['A02_SHIP'].matrix_world.inverted()@scene.objects[n].matrix_world for n in ACTORS[1:]]})
    parent=scene.objects['PORT_BERTH_PLACEMENT']
    assert parent.parent is None,'Expected the berth placement to be a root'
    assert 'PORT_SHIP_WATERLINE_CORRECTION'not in scene.objects
    helper=bpy.data.objects.new('PORT_SHIP_WATERLINE_CORRECTION',None)
    scene.collection.objects.link(helper);helper.rotation_mode='QUATERNION'
    parent.parent=helper
    parent.matrix_parent_inverse=Matrix.Identity(4)
    corrections=[]
    for f in [0]+list(range(216,361)):
        weight=smooth((f-216)/48)*(1-smooth((f-336)/24))
        rv=Vector();dz=0.0;total=0.0
        for k in range(-9,10):
            index=max(0,min(360,f+k));w=math.exp(-k*k/(2*3*3))
            rv+=raw[index][0]*w;dz+=raw[index][1]*w;total+=w
        rv*=weight/total;dz*=weight/total
        qlocal=Quaternion(rv.normalized(),rv.length)if rv.length>1e-9 else Quaternion()
        qworld=rotation@qlocal@rotation.inverted()
        pivot=source[f]['world_pivot']
        shift=D.to_3x3()@Vector((0,0,dz))
        matrix=Matrix.Translation(pivot+shift)@qworld.to_matrix().to_4x4()@Matrix.Translation(-pivot)
        if weight==0:matrix=Matrix.Identity(4)
        helper.matrix_world=matrix
        helper.keyframe_insert('location',frame=f)
        helper.keyframe_insert('rotation_quaternion',frame=f)
        corrections.append({'frame':f,'rotation_degrees':math.degrees(rv.length),'vertical_shift':dz})
    for layer in helper.animation_data.action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for curve in bag.fcurves:
                    curve.extrapolation='CONSTANT'
                    for key in curve.keyframe_points:
                        key.interpolation='BEZIER'
                        key.handle_left_type='AUTO_CLAMPED';key.handle_right_type='AUTO_CLAMPED'
    anchors_exact={}
    for f,poses in anchors.items():
        scene.frame_set(f)
        anchors_exact[f]=max(abs(scene.objects[n].matrix_world[i][j]-m[i][j])for n,m in poses.items()for i in range(4)for j in range(4))
    samples=[];relative_error=0.0
    for f in range(0,361,2):
        scene.frame_set(f)
        mat=I@scene.objects['A02_SHIP'].matrix_world
        measure=support_measure(mat,bottom,deck,water)
        measure['frame']=f;samples.append(measure)
        shipinv=scene.objects['A02_SHIP'].matrix_world.inverted()
        for n,old in zip(ACTORS[1:],source[f]['relative']):
            now=shipinv@scene.objects[n].matrix_world
            relative_error=max(relative_error,max(abs(now[i][j]-old[i][j])for i in range(4)for j in range(4)))
    # Independent subframe coverage and actual moving-geometry/port BVH check.
    scene.frame_set(216)
    env=[o for o in scene.objects if o.type=='MESH' and not o.hide_render and
         (o.name=='CN_QUAY'or descendant(o,{'PORT_MODEL_ROOT','PORT_CRANE_PLACEMENT'}))]
    env_tree,env_names=mesh_tree(env,I)
    moving=[o for o in scene.objects if o.type=='MESH'and not o.hide_render and descendant(o,set(ACTORS))]
    subframe_min_depth=1e9;subframe_min_freeboard=1e9;collisions={}
    for index in range(216*4,360*4+1):
        t=index/4;scene.frame_set(int(t),subframe=t%1)
        mat=I@scene.objects['A02_SHIP'].matrix_world
        measured=support_measure(mat,bottom,deck,water)
        subframe_min_depth=min(subframe_min_depth,measured['min_immersion'])
        subframe_min_freeboard=min(subframe_min_freeboard,measured['min_deck_freeboard'])
        if index%4==0:
            actor_tree,actor_names=mesh_tree(moving,I)
            for a,b in actor_tree.overlap(env_tree):
                collisions.setdefault(actor_names[a]+' | '+env_names[b],[]).append(t)
    report={'identity_anchors_error':anchors_exact,'max_relative_ship_cargo_pallet_error':relative_error,
            'max_correction_rotation_degrees':max(r['rotation_degrees']for r in corrections),
            'max_downward_draft_correction':min(r['vertical_shift']for r in corrections),
            'min_hull_immersion':min(r['min_immersion']for r in samples),
            'min_deck_freeboard':min(r['min_deck_freeboard']for r in samples),
            'exposed_bottom_frames':[r['frame']for r in samples if r['min_immersion']<=0],
            'subframe_min_immersion':subframe_min_depth,
            'subframe_min_deck_freeboard':subframe_min_freeboard,
            'subframe_support_samples':577,'support_frame_step':.25,
            'port_geometry_crossings':{n:sorted(set(fs))for n,fs in collisions.items()},
            'max_correction_angle_step_deg':max(abs(b['rotation_degrees']-a['rotation_degrees'])for a,b in zip(corrections,corrections[1:])),
            'samples':samples,'corrections':corrections,
            'method':'Shared parent, fitted static-water normal, Gaussian-smoothed rotation and draft, identity through216/from360'}
    assert max(anchors_exact.values())<.0001,report
    assert relative_error<.0001,report
    assert subframe_min_depth>.2 and subframe_min_freeboard>.4,report
    assert not collisions,report
    scene['cn_port_ship_support_report']=json.dumps(report)
    scene.frame_set(old_frame,subframe=old_subframe)
    print('SHIP_SUPPORT',json.dumps({k:v for k,v in report.items()if k not in {'samples','corrections'}}),flush=True)
    return helper,report


if __name__=='__main__':
    scene=bpy.context.scene
    helper,report=build_ship_support(scene)
    folder=Path(__file__).resolve().parents[1]/'review';folder.mkdir(exist_ok=True)
    (folder/'ship-support-audit.json').write_text(json.dumps(report,indent=2))
