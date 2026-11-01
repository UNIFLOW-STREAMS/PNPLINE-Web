"""Read-only three-way geometry/hierarchy/material transplant inventory."""
import bpy
import json
import hashlib
import array
from pathlib import Path
from collections import defaultdict,Counter
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
REVIEW=ROOT/'review';REVIEW.mkdir(parents=True,exist_ok=True)
BLOCKOUT=ROOT.parent
SOURCES={
 'baseline':BLOCKOUT/'cn-port-layout-v001/inputs/base.blend',
 'cn':BLOCKOUT/'cn-port-camera-v001/master-cn-port-camera-v001.blend',
 'us':BLOCKOUT/'port-densification-v001/pnpline-port-densification-v001.blend',
}


def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def matrix(value):return [list(row)for row in value]


def simple(value):
    if isinstance(value,(str,int,float,bool))or value is None:return value
    if isinstance(value,bpy.types.ID):return {'id':value.name,'type':value.bl_rna.identifier}
    try:return [simple(v)for v in value]
    except TypeError:return str(value)


def material_signature(mat):
    data={'name':mat.name,'diffuse':list(mat.diffuse_color),'use_nodes':mat.use_nodes,'metallic':mat.metallic,'roughness':mat.roughness}
    if mat.use_nodes and mat.node_tree:
        data['nodes']=[{'name':n.name,'type':n.bl_idname,'inputs':[(i.name,simple(i.default_value))for i in n.inputs if hasattr(i,'default_value')],
                        'image':n.image.filepath if hasattr(n,'image')and n.image else None,
                        'object':n.object.name if hasattr(n,'object')and n.object else None,
                        'operation':getattr(n,'operation',None)}for n in mat.node_tree.nodes]
        data['links']=[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name)for l in mat.node_tree.links]
    return {'digest':digest(data),'data':data}


def geometry(data):
    if isinstance(data,bpy.types.Mesh):
        v=array.array('f',[0])*(len(data.vertices)*3);data.vertices.foreach_get('co',v)
        indices=array.array('i',[0])*len(data.loops);data.loops.foreach_get('vertex_index',indices)
        counts=array.array('i',[0])*len(data.polygons);data.polygons.foreach_get('loop_total',counts)
        matidx=array.array('i',[0])*len(data.polygons);data.polygons.foreach_get('material_index',matidx)
        smooth=[p.use_smooth for p in data.polygons]
        return {'kind':'MESH','vertices':len(data.vertices),'edges':len(data.edges),'polygons':len(data.polygons),
                'coordinates':hashlib.sha256(v.tobytes()).hexdigest(),
                'topology':hashlib.sha256(indices.tobytes()+counts.tobytes()).hexdigest(),
                'face_materials':hashlib.sha256(matidx.tobytes()).hexdigest(),'smooth':digest(smooth)}
    if isinstance(data,bpy.types.Curve):
        content={'type':data.bl_rna.identifier,'dimensions':data.dimensions,'resolution':data.resolution_u,
                 'bevel':data.bevel_depth,'extrude':data.extrude,
                 'body':getattr(data,'body',None),'size':getattr(data,'size',None)}
        content['splines']=[{'type':sp.type,'cyclic':sp.use_cyclic_u,'points':[list(p.co)for p in sp.points],
                            'bezier':[(list(p.co),list(p.handle_left),list(p.handle_right))for p in sp.bezier_points]}for sp in data.splines]
        return {'kind':'CURVE','digest':digest(content)}
    return None


def rna_dependency(item):
    data={'type':item.type,'name':item.name}
    for p in item.bl_rna.properties:
        if p.identifier in {'rna_type','name','type'}or p.is_readonly:continue
        try:
            value=getattr(item,p.identifier)
            if p.type=='POINTER':data[p.identifier]=value.name if isinstance(value,bpy.types.ID)else None
            elif p.type in {'STRING','ENUM','FLOAT','INT','BOOLEAN'}:data[p.identifier]=simple(value)
        except (AttributeError,TypeError,RuntimeError):pass
    return data


def snapshot(label,path):
    bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;s.frame_set(0)
    geom={};objects={}
    for o in s.objects:
        if o.data and o.data.name not in geom:geom[o.data.name]=geometry(o.data)
        objects[o.name]={'type':o.type,'parent':o.parent.name if o.parent else None,
                         'basis':matrix(o.matrix_basis),'parent_inverse':matrix(o.matrix_parent_inverse),
                         'world_f0':matrix(o.matrix_world),'collections':sorted(c.name for c in o.users_collection),
                         'data':o.data.name if o.data else None,'geometry':geom.get(o.data.name)if o.data else None,
                         'materials':[m.name if m else None for m in o.data.materials]if o.data and hasattr(o.data,'materials')else [],
                         'hide_render':o.hide_render,'hide_viewport':o.hide_viewport,'hide_layer':o.hide_get(),
                         'display_type':o.display_type,'action':o.animation_data.action.name if o.animation_data and o.animation_data.action else None,
                         'constraints':[rna_dependency(c)for c in o.constraints],
                         'modifiers':[rna_dependency(m)for m in o.modifiers],
                         'properties':{k:simple(v)for k,v in o.items()}}
    result={'file':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'fps':s.render.fps,'fps_base':s.render.fps_base,'frame_start':s.frame_start,'frame_end':s.frame_end,
            'scene_name':s.name,'camera':s.camera.name if s.camera else None,'objects':objects,
            'collections':{c.name:{'objects':sorted(o.name for o in c.objects),'children':sorted(ch.name for ch in c.children),'hide_render':c.hide_render,'hide_viewport':c.hide_viewport}for c in bpy.data.collections},
            'materials':{m.name:material_signature(m)for m in bpy.data.materials}}
    ocean=s.objects['EARTH_CONTINUOUS_OCEAN'];I=s.objects['SF_CN_LAYOUT'].matrix_world.inverted()
    result['ocean_native_vertices']=[list(v.co)for v in ocean.data.vertices]
    result['ocean_native_faces']=[list(p.vertices)for p in ocean.data.polygons]
    result['ocean_world_matrix']=matrix(ocean.matrix_world)
    result['layout_world_matrix']=matrix(s.objects['SF_CN_LAYOUT'].matrix_world)
    result['ocean_CN_bounds']=[[min((I@ocean.matrix_world@v.co)[i]for v in ocean.data.vertices)for i in range(3)],
                               [max((I@ocean.matrix_world@v.co)[i]for v in ocean.data.vertices)for i in range(3)]]
    (REVIEW/f'geometry-{label}.json').write_text(json.dumps(result,separators=(',',':')))
    print('SNAPSHOT',label,len(objects),len(result['materials']),flush=True)
    return result


all_data={k:snapshot(k,p)for k,p in SOURCES.items()}
B=all_data['baseline'];C=all_data['cn'];U=all_data['us']
b=B['objects'];c=C['objects'];u=U['objects']
fields=['type','parent','basis','parent_inverse','geometry','materials','hide_render','hide_viewport','hide_layer','display_type','constraints','modifiers','properties','collections']
cn_delta={};us_delta={};conflicts={}
for n in sorted(set(b)&set(c)):
    changed=[f for f in fields if b[n][f]!=c[n][f]]
    if changed:
        cn_delta[n]={'fields':changed,'cn':{f:c[n][f]for f in changed},'baseline':{f:b[n][f]for f in changed}}
        both=[f for f in changed if n in u and b[n][f]!=u[n][f]and c[n][f]!=u[n][f]]
        if both:conflicts[n]={'fields':both,'us':{f:u[n][f]for f in both},'cn':{f:c[n][f]for f in both}}
for n in sorted(set(b)&set(u)):
    changed=[f for f in fields if b[n][f]!=u[n][f]]
    if changed:us_delta[n]=changed
cn_new=sorted(set(c)-set(b));us_new=sorted(set(u)-set(b))
cn_material_new=sorted(set(C['materials'])-set(B['materials']))
cn_material_changed=sorted(n for n in set(B['materials'])&set(C['materials'])if B['materials'][n]['digest']!=C['materials'][n]['digest'])
us_material_changed=sorted(n for n in set(B['materials'])&set(U['materials'])if B['materials'][n]['digest']!=U['materials'][n]['digest'])
dependencies=set()
for n in cn_new:
    o=c[n]
    if o['parent']and o['parent']not in cn_new:dependencies.add(o['parent'])
    for group in [o['constraints'],o['modifiers']]:
        for entry in group:
            for value in entry.values():
                if isinstance(value,str)and value in c and value not in cn_new:dependencies.add(value)
material_conflicts=sorted(n for n in cn_material_new if n in U['materials']and C['materials'][n]['digest']!=U['materials'][n]['digest'])
roots=['SF_CN_LAYOUT','CN_FRAME','US_FRAME','EARTH_CONTINUOUS_OCEAN','A02_SHIP','CN_QUAY','US_QUAY']
root_compat={n:{'baseline':b[n]['world_f0'],'cn':c[n]['world_f0'],'us':u[n]['world_f0'],
                'CN_vs_US_exact':c[n]['world_f0']==u[n]['world_f0']}for n in roots if n in b and n in c and n in u}
ocean_same=B['objects']['EARTH_CONTINUOUS_OCEAN']['geometry']==U['objects']['EARTH_CONTINUOUS_OCEAN']['geometry']
result={'source_hashes':{k:v['sha256']for k,v in all_data.items()},'counts':{k:len(v['objects'])for k,v in all_data.items()},
        'cn_added_objects':cn_new,'us_added_objects':us_new,'cn_deleted_objects':sorted(set(b)-set(c)),
        'new_object_name_collisions':sorted(set(cn_new)&set(us_new)),
        'cn_common_deltas':cn_delta,'us_common_changed_fields':us_delta,'three_way_conflicts':conflicts,
        'cn_added_collections':{n:C['collections'][n]for n in sorted(set(C['collections'])-set(B['collections']))},
        'cn_external_object_dependencies':sorted(dependencies),
        'cn_added_materials':cn_material_new,'cn_changed_common_materials':cn_material_changed,
        'us_changed_common_materials':us_material_changed,'cn_new_material_name_conflicts_in_US':material_conflicts,
        'root_compatibility':root_compat,'US_ocean_geometry_exact_baseline':ocean_same,
        'ocean_recommendation':'Replace US ocean mesh data with CN ocean mesh data; US geometry equals baseline, so CN change is the sole geometry delta. Preserve target object transform and material canonicalization.'if ocean_same else 'Do not replace whole ocean until the US-specific mesh delta is resolved.',
        'scene_settings':{k:{f:v[f]for f in ['fps','fps_base','frame_start','frame_end','scene_name','camera']}for k,v in all_data.items()}}
(REVIEW/'geometry-manifest.json').write_text(json.dumps(result,indent=2))
summary={'counts':result['counts'],'cn_added':len(cn_new),'us_added':len(us_new),'cn_common_changed':len(cn_delta),'conflicts':{n:d['fields']for n,d in conflicts.items()},'cn_geometry_changed':[n for n,d in cn_delta.items()if 'geometry'in d['fields']],'cn_material_changed':cn_material_changed,'us_material_changed':us_material_changed,'external_dependencies':sorted(dependencies),'ocean_baseline_US_same':ocean_same}
(REVIEW/'geometry-summary.json').write_text(json.dumps(summary,indent=2))
print('GEOMETRY_SUMMARY',json.dumps(summary),flush=True)
