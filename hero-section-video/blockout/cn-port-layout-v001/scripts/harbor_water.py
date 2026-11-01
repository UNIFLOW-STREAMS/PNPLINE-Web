"""Continuously reshape the existing ocean under the relocated loading berth.

The source ship actions stay untouched. This maps the original water surface
under the translated ship back beneath its new berth/departure position. The
correction fades into the same connected ocean mesh, never a second water plane.
Call after PORT_BERTH_PLACEMENT has received its final provisional keys.
"""
import json
import bpy
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree


def _smooth(x):
    x=max(0.0,min(1.0,x))
    return x*x*x*(10+x*(-15+6*x))


def build_harbor_water(scene, layout):
    ocean=scene.objects['EARTH_CONTINUOUS_OCEAN']
    placement=scene.objects['PORT_BERTH_PLACEMENT']
    ship=scene.objects['A02_SHIP']
    old_frame=scene.frame_current
    old_subframe=scene.frame_subframe
    scene.frame_set(0)
    to_layout=layout.matrix_world.inverted()
    ocean_to_layout=to_layout@ocean.matrix_world
    from_layout=ocean_to_layout.inverted()
    vertices=[ocean_to_layout@v.co for v in ocean.data.vertices]
    polygons=[tuple(p.vertices)for p in ocean.data.polygons]
    original=BVHTree.FromPolygons(vertices,polygons)

    def height(x,y):
        hit=original.ray_cast(Vector((x,y,120)),Vector((0,0,-1)))[0]
        return hit.z if hit else None

    # Reconstruct original position by removing only the new placement parent.
    # Keep the existing curved voyage and the ship's original orientation.
    samples=[]
    for frame in [0]+list(range(156,361,4)):
        scene.frame_set(frame)
        position=to_layout@ship.matrix_world.translation
        offset=to_layout.to_3x3()@placement.matrix_world.translation
        source_position=position-offset
        source_water=height(source_position.x,source_position.y)
        row={'frame':frame,'position':list(position),'offset':list(offset),
             'source_water_z':source_water}
        if not samples or position.x>samples[-1]['position'][0]+1e-5:
            samples.append(row)
    assert len(samples)>20,'Expected monotonic departure samples'
    assert max(abs(v)for v in samples[-1]['offset'])<1e-4,'Placement must return to source by f360'

    def path_at(x):
        if x<=samples[0]['position'][0]:return samples[0]
        if x>=samples[-1]['position'][0]:return samples[-1]
        # Linear interpolation preserves sampled source poses; 4-frame spacing
        # is much finer than the deformed water grid and avoids spline overshoot.
        for a,b in zip(samples,samples[1:]):
            ax=a['position'][0];bx=b['position'][0]
            if ax<=x<=bx:
                t=(x-ax)/(bx-ax)
                return {'position':[u+(v-u)*t for u,v in zip(a['position'],b['position'])],
                        'offset':[u+(v-u)*t for u,v in zip(a['offset'],b['offset'])]}

    # Blend the support into a broad part of the globe. A narrow track creates
    # a steep lateral ridge that reads as a trench in a city overview.
    lateral_plateau=8.0
    lateral_falloff=36.0
    longitudinal_falloff=40.0
    xmin=samples[0]['position'][0]-48
    xmax=samples[-1]['position'][0]+2
    ymin=min(r['position'][1]for r in samples)-lateral_plateau-lateral_falloff
    ymax=max(r['position'][1]for r in samples)+lateral_plateau+lateral_falloff
    ocean.data=ocean.data.copy()
    ocean.data.name='PORT_CONTINUOUS_OCEAN_SURFACE'
    bm=bmesh.new();bm.from_mesh(ocean.data)
    selected=[]
    for e in bm.edges:
        ps=[ocean_to_layout@v.co for v in e.verts]
        if all(xmin-8<p.x<xmax+8 and ymin-8<p.y<ymax+8 and p.z>-100 for p in ps):
            selected.append(e)
    # Eight subintervals on local original edges. Shared boundary edges are
    # split by BMesh too, so the result remains watertight and has no T-junction.
    bmesh.ops.subdivide_edges(bm,edges=selected,cuts=7,use_grid_fill=True)
    changed=0;maximum_raise=0.0;maximum_lower=0.0
    for v in bm.verts:
        p=ocean_to_layout@v.co
        if p.z<-100 or p.x<xmin or p.x>xmax:continue
        path=path_at(p.x)
        cross=abs(p.y-path['position'][1])
        lateral=1-_smooth((cross-lateral_plateau)/lateral_falloff)
        longitudinal=_smooth((p.x-xmin)/longitudinal_falloff)
        weight=lateral*longitudinal
        if weight<1e-8:continue
        offset=path['offset']
        if max(abs(x)for x in offset)<1e-7:continue
        before=height(p.x,p.y)
        after=height(p.x-offset[0],p.y-offset[1])
        if before is None or after is None or abs(p.z-before)>.3:continue
        # Supporting the relocated hull only requires raising this region.
        # A negative side-lobe from translating the original globe would dig
        # a broad depression and uncover old decorative wave ribbons.
        raise_amount=max(0.0,after+offset[2]-before)
        dz=raise_amount*_smooth(raise_amount/.03)*weight
        if abs(dz)<1e-7:continue
        p.z+=dz;v.co=from_layout@p
        changed+=1;maximum_raise=max(maximum_raise,dz);maximum_lower=min(maximum_lower,dz)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    nonmanifold=sum(not e.is_manifold for e in bm.edges)
    bm.to_mesh(ocean.data);bm.free();ocean.data.update()
    for polygon in ocean.data.polygons:polygon.use_smooth=True
    final_vertices=[ocean_to_layout@v.co for v in ocean.data.vertices]
    final=BVHTree.FromPolygons(final_vertices,[tuple(p.vertices)for p in ocean.data.polygons])
    checks=[]; footprint_errors=[]
    for row in samples:
        p=row['position'];off=row['offset']
        water=final.ray_cast(Vector((p[0],p[1],120)),Vector((0,0,-1)))[0]
        target=row['source_water_z']+off[2]
        checks.append({'frame':row['frame'],'actual_z':water.z if water else None,
                       'target_z':target,'error':water.z-target if water else None})
        for xshift in [-6,0,6]:
            for yshift in [-2,0,2]:
                x=p[0]+xshift;y=p[1]+yshift
                expected=height(x-off[0],y-off[1])+off[2]
                actual=final.ray_cast(Vector((x,y,120)),Vector((0,0,-1)))[0]
                footprint_errors.append({'frame':row['frame'],'offset_xy':[xshift,yshift],
                                         'error':actual.z-expected})
    report={'method':'Connected original ocean, locally subdivided and translated-source height field',
            'source_vertices':len(vertices),'final_vertices':len(final_vertices),
            'changed_vertices':changed,'max_raise':maximum_raise,'max_lower':maximum_lower,
            'nonmanifold_edges':nonmanifold,'region_layout_xy':[xmin,xmax,ymin,ymax],
            'blend_widths':{'lateral_plateau':lateral_plateau,'lateral_falloff':lateral_falloff,'longitudinal_falloff':longitudinal_falloff},
            'ship_center_water_samples':checks,
            'largest_footprint_error':max(footprint_errors,key=lambda r:abs(r['error'])),
            'max_center_water_error':max(abs(c['error'])for c in checks if c['error']is not None)}
    assert not nonmanifold,report
    assert report['max_center_water_error']<.06,report
    scene['cn_port_water_report']=json.dumps(report)
    scene.frame_set(old_frame,subframe=old_subframe)
    print('HARBOR_WATER',json.dumps(report),flush=True)
    return report


if __name__=='__main__':
    # Read-only Blender invocation for a diagnostic in-memory build.
    scene=bpy.context.scene
    import sys
    from pathlib import Path
    if '--baseline-water' in sys.argv:
        baseline=Path(__file__).resolve().parents[1]/'inputs/base.blend'
        with bpy.data.libraries.load(str(baseline),link=False)as (source,target):
            target.objects=['EARTH_CONTINUOUS_OCEAN']
        imported=target.objects[0]
        scene.objects['EARTH_CONTINUOUS_OCEAN'].data=imported.data.copy()
        bpy.data.objects.remove(imported,do_unlink=True)
    if '--hold252' in sys.argv:
        scene.frame_set(0)
        placement=scene.objects['PORT_BERTH_PLACEMENT']
        shift=placement.location.copy()
        placement.animation_data_clear()
        for frame in range(361):
            placement.location=shift*(1-_smooth((frame-252)/108))
            placement.keyframe_insert('location',frame=frame)
        for layer in placement.animation_data.action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for fc in bag.fcurves:
                        for key in fc.keyframe_points:key.interpolation='LINEAR'
    build_harbor_water(scene,scene.objects['SF_CN_LAYOUT'])
    if '--preview' in sys.argv:
        from mathutils import Matrix
        root=Path(__file__).resolve().parents[1]
        spec=json.loads((root/'review/camera-framing.json').read_text())['views']['overview']
        scene.frame_set(0)
        camera=bpy.data.objects.new('TEMP_WIDE_WATER_REVIEW',bpy.data.cameras.new('TEMP_WIDE_WATER_REVIEW'))
        scene.collection.objects.link(camera);scene.camera=camera
        position=Vector(spec['position']);target=Vector(spec['target'])
        camera.matrix_world=scene.objects['SF_CN_LAYOUT'].matrix_world@Matrix.LocRotScale(position,(target-position).to_track_quat('-Z','Y'),Vector((1,1,1)))
        camera.data.type='ORTHO';camera.data.ortho_scale=spec['scale'];camera.data.clip_end=5000
        scene.render.engine='BLENDER_WORKBENCH'
        scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL'
        scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True
        scene.display.shading.cavity_type='BOTH';scene.display.shading.show_specular_highlight=True
        scene.display.shading.background_type='WORLD'
        scene.render.resolution_x=1600;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
        scene.render.use_border=False;scene.render.image_settings.file_format='PNG'
        scene.render.filepath=str(root/'review/water-wide-preview.png')
        bpy.ops.render.render(write_still=True)
