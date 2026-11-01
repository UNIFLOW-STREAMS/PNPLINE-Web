"""Flip proven inward closed components in generated port meshes only.

The harbor primitive builder used reversed cube face winding. Keep vertex
coordinates, polygon membership, materials, transforms, and animation intact.
"""
import bpy
import json
import hashlib
from collections import Counter,defaultdict
from pathlib import Path
from mathutils import Vector


def components(mesh):
    edge_faces=defaultdict(list)
    for face in mesh.polygons:
        ids=list(face.vertices)
        for a,b in zip(ids,ids[1:]+ids[:1]):edge_faces[tuple(sorted((a,b)))].append(face.index)
    neighbors=defaultdict(set)
    for faces in edge_faces.values():
        for index in faces:neighbors[index].update(faces)
    unseen=set(range(len(mesh.polygons)))
    output=[]
    while unseen:
        seed=unseen.pop();faces={seed};pending=[seed]
        while pending:
            for other in neighbors[pending.pop()]:
                if other in unseen:
                    unseen.remove(other);faces.add(other);pending.append(other)
        used_edges=set()
        volume=0.0
        for index in faces:
            ids=list(mesh.polygons[index].vertices)
            used_edges.update(tuple(sorted((a,b)))for a,b in zip(ids,ids[1:]+ids[:1]))
            first=mesh.vertices[ids[0]].co
            for j in range(1,len(ids)-1):
                a=mesh.vertices[ids[j]].co;b=mesh.vertices[ids[j+1]].co
                volume+=first.dot(a.cross(b))/6
        closed=all(len(edge_faces[e])==2 for e in used_edges)
        output.append({'faces':faces,'closed':closed,'signed_volume':volume})
    return output


def signature(mesh):
    return (tuple(tuple(v.co)for v in mesh.vertices),
            tuple(sorted(tuple(sorted(e.vertices))for e in mesh.edges)),
            tuple(tuple(sorted(p.vertices))for p in mesh.polygons))


def fix_port_normals(scene):
    eligible=[o for o in scene.objects if o.type=='MESH'and(o.name.startswith('PORT_')or o.name=='CN_QUAY')]
    eligible_names={o.name for o in eligible}
    by_mesh=defaultdict(list)
    for o in eligible:by_mesh[o.data].append(o)
    outside_users=defaultdict(list)
    for o in bpy.data.objects:
        if o.type=='MESH'and o.name not in eligible_names:outside_users[o.data].append(o.name)
    fixed=0;fixed_components=0;negative=[];open_count=0;positive_count=0
    unchanged=True;remaining=[];prefix_counts=Counter()
    for mesh,objects in by_mesh.items():
        parts=components(mesh)
        bad=[p for p in parts if p['closed']and p['signed_volume']< -1e-9]
        open_count+=sum(not p['closed']for p in parts)
        positive_count+=sum(p['closed']and p['signed_volume']>1e-9 for p in parts)
        if not bad:continue
        outside=outside_users.get(mesh,[])
        assert not outside,'Generated port mesh also used outside scope: '+str(outside)
        before=signature(mesh)
        for part in bad:
            for index in part['faces']:mesh.polygons[index].flip()
            fixed_components+=1
            if len(negative)<40:negative.append({'mesh':mesh.name,'object':objects[0].name,'volume_before':part['signed_volume'],'faces_flipped':len(part['faces'])})
        mesh.update()
        unchanged=unchanged and before==signature(mesh)
        after=components(mesh)
        remaining.extend(mesh.name for p in after if p['closed']and p['signed_volume']< -1e-9)
        fixed+=1
        for o in objects:prefix_counts[o.name.split('.')[0]]+=1
    report={'eligible_objects':len(eligible),'eligible_meshes':len(by_mesh),'fixed_meshes':fixed,
            'fixed_closed_components':fixed_components,'already_outward_components':positive_count,
            'open_components_left_untouched':open_count,'coordinates_and_topology_membership_exact':unchanged,
            'remaining_negative_closed_components':remaining,'negative_examples':negative,
            'fixed_object_counts':dict(prefix_counts),
            'scope':'Generated PORT_* mesh objects and CN_QUAY only; polygon winding only'}
    assert unchanged and not remaining,report
    scene['cn_port_normals_report']=json.dumps(report)
    print('PORT_NORMALS',json.dumps({k:v for k,v in report.items()if k not in {'negative_examples','fixed_object_counts'}}),flush=True)
    return report


if __name__=='__main__':
    import sys
    scene=bpy.context.scene
    root=Path(__file__).resolve().parents[1]
    folder=root/'review'/'normals-check';folder.mkdir(parents=True,exist_ok=True)
    source=Path(bpy.data.filepath);source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
    scene.render.engine='BLENDER_WORKBENCH';shading=scene.display.shading
    shading.light='STUDIO';shading.color_type='MATERIAL';shading.show_shadows=True
    shading.show_cavity=True;shading.cavity_type='BOTH';shading.show_specular_highlight=True
    shading.background_type='WORLD';scene.render.resolution_percentage=100
    scene.render.resolution_x=1200;scene.render.resolution_y=675;scene.render.use_border=False
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB'
    def render(label):
        for f in [48,336]:
            scene.frame_set(f);scene.render.filepath=str(folder/f'{label}-f{f:04d}.png')
            bpy.ops.render.render(write_still=True)
    if '--renders' in sys.argv:render('before')
    report=fix_port_normals(scene)
    if '--renders' in sys.argv:render('after')
    if '--lighting' in sys.argv:
        shading.show_shadows=False
        render('shadows-off')
        shading.show_shadows=True
        direction=(scene.objects['SF_CN_LAYOUT'].matrix_world.to_3x3()@Vector((-.3,-.5,1))).normalized()
        scene.display.light_direction=direction
        render('cn-local-light')
        report['diagnostic_CN_local_light_direction_world']=list(direction)
    if '--overhead'in sys.argv:
        scene.display.light_direction=(scene.objects['SF_CN_LAYOUT'].matrix_world.to_3x3()@Vector((0,0,1))).normalized()
        render('cn-up-light')
    assert hashlib.sha256(source.read_bytes()).hexdigest()==source_hash
    report.update({'source':str(source),'source_sha256':source_hash,'source_saved':False,'actual_camera_render_frames':[48,336]if '--renders'in sys.argv else []})
    (folder/'audit.json').write_text(json.dumps(report,indent=2))
