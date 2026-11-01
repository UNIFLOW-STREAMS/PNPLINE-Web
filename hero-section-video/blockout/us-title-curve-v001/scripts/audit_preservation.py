"""Read-only modeling-only preservation audit and new-geometry clearance.

Blender --background --factory-startup --python audit_preservation.py -- --capture-source
Blender --background --factory-startup --python audit_preservation.py
Original files are never saved. Native-frame evaluation uses a dependency-complete
minimal scene; object/data snapshots are taken before that temporary reduction.
"""
import argparse,ast,array,hashlib,json,math,sys
from collections import Counter
from pathlib import Path

import bpy
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'review';OUT.mkdir(parents=True,exist_ok=True)
BLOCKOUT=ROOT.parent
SOURCE=BLOCKOUT/'us-city-density-v001/pnpline-us-city-density-v001.blend'
SOURCE_SHA='90cf22b0693b0d3702236f88a3871da371491090c7b9a2d1d70d58047f22da9a'
CANDIDATE=ROOT/'pnpline-us-title-curve-v001.blend'
ACTORS={'A02_SHIP','A01_CONTAINER','W01_NEW_PALLET','P01_SPREADER','A03_TRACTOR','A03_TRAILER','A04_PRIMARY','A05_SECONDARY'}
EXPLICIT_MOTION=ACTORS|{'CAM_MASTER','CAM_LOOK_TARGET','CR_COMPACT_GANTRY','CR_SLEW_JIB','CR_TROLLEY_CARRIAGE','CR_SUSPENSION_HEAD'}


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


defs=ast.parse((BLOCKOUT/'cn-us-integrated-v001/scripts/audit_geometry.py').read_text())
exec(compile(ast.Module(body=[n for n in defs.body if isinstance(n,ast.FunctionDef)and n.name in{'geometry','digest','simple','material_signature','rna_dependency'}],type_ignores=[]),'source_geometry_fingerprints','exec'),globals())
tree_defs=ast.parse((BLOCKOUT/'cn-port-camera-v001/scripts/verify_camera.py').read_text())
exec(compile(ast.Module(body=[n for n in tree_defs.body if isinstance(n,ast.ClassDef)and n.name=='GeometryTree'],type_ignores=[]),'audited_geometry_tree','exec'),globals())


def stable(v):
    if isinstance(v,(str,bool,int,float))or v is None:return v
    if isinstance(v,bpy.types.ID):return {'id':v.name,'type':v.bl_rna.identifier}
    if hasattr(v,'items'):return {k:stable(x)for k,x in v.items()}
    try:return [stable(x)for x in v]
    except TypeError:return str(v)


def matrix(m):return [list(row)for row in m]
def flat(m):return [x for row in m for x in row]
def error(a,b):return max(abs(x-y)for x,y in zip(flat(a),flat(b)))
def under(o,names):
    while o:
        if o.name in names:return True
        o=o.parent
    return False
def visible(o):return not o.hide_render and not all(c.hide_render for c in o.users_collection)


def action_signature(a):
    curves=[]
    for layer in a.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for fc in bag.fcurves:
                    curves.append([bag.slot_handle,fc.data_path,fc.array_index,fc.extrapolation,fc.mute,
                         [[*k.co,*k.handle_left,*k.handle_right,k.interpolation,k.handle_left_type,k.handle_right_type,k.easing,k.amplitude,k.back,k.period]for k in fc.keyframe_points],
                         [rna_dependency(m)for m in fc.modifiers]])
    return digest(curves)


def drivers(o):
    if not o.animation_data:return []
    return [[f.data_path,f.array_index,f.driver.expression,f.driver.type,
       [[v.name,v.type,[[t.id.name if t.id else None,t.data_path,t.bone_target,t.transform_type,t.transform_space]for t in v.targets]]for v in f.driver.variables]]for f in o.animation_data.drivers]


def animation_binding(o):
    ad=o.animation_data
    if not ad:return None
    return {'action':ad.action.name if ad.action else None,'slot':ad.action_slot_handle,
            'blend':ad.action_blend_type,'influence':ad.action_influence,'extrapolation':ad.action_extrapolation,
            'nla':[[track.name,track.mute,track.is_solo,[[strip.name,strip.action.name if strip.action else None,strip.frame_start,strip.frame_end,strip.action_frame_start,strip.action_frame_end,strip.scale,strip.repeat,strip.blend_type,strip.extrapolation,strip.influence,strip.mute]for strip in track.strips]]for track in ad.nla_tracks]}


def optics(cam):
    d=cam.data
    return [d.type,d.lens,d.shift_x,d.shift_y,d.clip_start,d.clip_end,d.sensor_width,d.sensor_height,d.sensor_fit,d.ortho_scale,
            d.dof.use_dof,d.dof.focus_distance,d.dof.focus_object.name if d.dof.focus_object else None,d.dof.aperture_fstop]


def snapshot(path):
    bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;s.frame_set(0)
    data={};objects={}
    for o in s.objects:
        key=(o.type,o.data.name)if o.data else None
        if key and key not in data:
            data[key]=geometry(o.data)if o.type in{'MESH','CURVE','FONT'}else rna_dependency(o.data)if o.type in{'CAMERA','LIGHT'}else None
        objects[o.name]={'type':o.type,'parent':o.parent.name if o.parent else None,
            'matrix_basis':matrix(o.matrix_basis),'matrix_parent_inverse':matrix(o.matrix_parent_inverse),'matrix_world':matrix(o.matrix_world),
            'data':o.data.name if o.data else None,'geometry':data.get(key),
            'materials':[m.name if m else None for m in o.data.materials]if o.data and hasattr(o.data,'materials')else[],
            'hide_render':o.hide_render,'hide_viewport':o.hide_viewport,'hide_layer':o.hide_get(),'display_type':o.display_type,
            'collections':sorted(c.name for c in o.users_collection),'constraints':[rna_dependency(c)for c in o.constraints],
            'modifiers':[rna_dependency(m)for m in o.modifiers],'animation':animation_binding(o),'drivers':drivers(o),
            'data_animation':animation_binding(o.data)if o.data and hasattr(o.data,'animation_data')else None,
            'data_drivers':drivers(o.data)if o.data and hasattr(o.data,'animation_data')else[],
            'properties':{k:stable(v)for k,v in o.items()}}
    # Water/river group names are explicit audit evidence; every original object
    # is protected by the general state comparison in addition to this list.
    waterways=sorted(n for n in objects if n.startswith(('SF_BASIN_','SF_ISLAND_'))or any(word in n.upper()for word in('RIVER','BRIDGE','WATERWAY')))
    moving_roots={o.name for o in s.objects if o.animation_data and(o.animation_data.action or o.animation_data.drivers or o.animation_data.nla_tracks)}|EXPLICIT_MOTION
    us_port_roots={o.name for o in s.objects if o.name.startswith(('CV_CRANE_','CV_STACK_','CV_PORT_','CV_PT_'))}|{'US_QUAY','US_YARD_ROAD','E07_INBOUND_ROAD','E11_ROUTE_1','E11_ROUTE_-1','E09_MANEUVER_YARD','A05_WAIT_MERGE'}
    protected={'waterway':waterways,
        'China':sorted(o.name for o in s.objects if under(o,{'CN_FRAME','SF_CN_LAYOUT','PORT_MODEL_ROOT'})or o.name.startswith(('SHD_','CNX_','CNC_'))),
        'port':sorted(o.name for o in s.objects if under(o,{'PORT_MODEL_ROOT','PORT_CRANE_PLACEMENT','PORT_HOIST_PLACEMENT'})or o.name.startswith(('PORT_','CR_'))),
        'US_port_roads':sorted(o.name for o in s.objects if under(o,us_port_roots)or o.name.startswith(('PT_','P02_'))),
        'animated_actors_camera':sorted(o.name for o in s.objects if under(o,moving_roots)),
        'warehouse':sorted(o.name for o in s.objects if o.name.startswith(('WH_','WAREHOUSE_'))or under(o,{'US_WAREHOUSE','WAREHOUSE_ROOT','CV_WH_US_FRAME','E08_WAREHOUSE'})),
        'ground_ocean':[n for n in('CNC_UNIFIED_GROUND','EARTH_CONTINUOUS_OCEAN','SF_BASIN_WATER_SURFACE','US_LAND_TERRACE')if n in objects]}
    survey_path=OUT/'us-survey.json'
    if survey_path.exists():
        survey=json.loads(survey_path.read_text())
        assert survey['sha256']==SOURCE_SHA
        protected['survey_logistics']=sorted(r['name']for r in survey['protected_road_port_objects'])
    result={'file':str(path),'sha256':sha(path),'objects':objects,'actions':{a.name:action_signature(a)for a in bpy.data.actions},
        'materials':{m.name:material_signature(m)['digest']for m in bpy.data.materials},'protected_groups':protected,
        'scene':{'name':s.name,'camera':s.camera.name,'fps':s.render.fps,'fps_base':s.render.fps_base,'start':s.frame_start,'end':s.frame_end,
                 'markers':sorted([m.frame,m.name,m.camera.name if m.camera else None]for m in s.timeline_markers),
                 'resolution':[s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage],
                 'pixel_aspect':[s.render.pixel_aspect_x,s.render.pixel_aspect_y]},
        'collections':{c.name:{'hide_render':c.hide_render,'hide_viewport':c.hide_viewport,'objects':sorted(o.name for o in c.objects),'children':sorted(x.name for x in c.children)}for c in bpy.data.collections}}
    print('FULL_OBJECT_SNAPSHOT',len(objects),len(result['actions']),'waterway_objects',len(waterways),flush=True)
    return result


def motion_names(s):
    return sorted({o.name for o in s.objects if o.animation_data and(o.animation_data.action or o.animation_data.drivers or o.animation_data.nla_tracks)}|{n for n in EXPLICIT_MOTION if n in s.objects})


def minimize_scene(s,tracked,extra=()):
    keep=set(tracked)|set(extra)
    changed=True
    while changed:
        changed=False
        for name in list(keep):
            o=s.objects[name];deps=[]
            if o.parent:deps.append(o.parent)
            for con in o.constraints:
                for p in con.bl_rna.properties:
                    if p.type=='POINTER':
                        target=getattr(con,p.identifier,None)
                        if isinstance(target,bpy.types.Object):deps.append(target)
            for idblock in[o,o.data]:
                if idblock and hasattr(idblock,'animation_data')and idblock.animation_data:
                    for fc in idblock.animation_data.drivers:
                        for var in fc.driver.variables:
                            deps.extend(t.id for t in var.targets if isinstance(t.id,bpy.types.Object))
            for dep in deps:
                if dep.name not in keep:keep.add(dep.name);changed=True
    full_world={n:s.objects[n].matrix_world.copy()for n in tracked}
    bpy.data.batch_remove(ids=[o for o in bpy.data.objects if o.name not in keep])
    s.frame_set(0)
    difference=max(error(s.objects[n].matrix_world,m)for n,m in full_world.items())
    assert difference==0,('Minimal dependency closure changed frame0',difference)
    print('MINIMAL_SCENE',len(keep),'tracked',len(tracked),flush=True)


def capture_motion(s,names):
    result={'objects':{n:[]for n in names},'optics':[]}
    for f in range(990):
        s.frame_set(f)
        for n in names:result['objects'][n].append(matrix(s.objects[n].matrix_world))
        result['optics'].append(optics(s.objects['CAM_MASTER']))
    s.frame_set(0)
    return result


def mesh_world(o):
    ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
    vs=[o.matrix_world@v.co for v in mesh.vertices];fs=[tuple(p.vertices)for p in mesh.polygons]
    ev.to_mesh_clear();return vs,fs


def combine(objects):
    vertices=[];polys=[];names=[]
    for o in objects:
        vs,fs=mesh_world(o);offset=len(vertices);vertices.extend(vs);polys.extend(tuple(i+offset for i in p)for p in fs);names.extend([o.name]*len(fs))
    return BVHTree.FromPolygons(vertices,polys)if polys else None,names


def candidates_clearance(s,changed_geometry,tracked):
    geos=[s.objects[n]for n in changed_geometry if n in s.objects and s.objects[n].type in{'MESH','CURVE','FONT'}and visible(s.objects[n])]
    tree,names=combine(geos)
    points=[o.matrix_world@Vector(p)for o in geos for p in o.bound_box]
    bounds=([min(p[i]for p in points)for i in range(3)],[max(p[i]for p in points)for i in range(3)])if points else None
    moving_roots=set(tracked)
    actor_objects=[o for o in s.objects if o.type in{'MESH','CURVE','FONT'}and under(o,moving_roots)and not all(c.hide_render for c in o.users_collection)and not any(w in o.name.upper()for w in('WAKE','WAVE','WATER'))]
    moving=GeometryTree(actor_objects)
    minimize_scene(s,tracked,[o.name for o in actor_objects])
    camera_crossings={};actor_contacts={};nearest={'distance':1e30};previous=None
    # All frames are checked, with half-frame sampling during the US segment.
    frame_values=list(range(253))+[i/2 for i in range(506,1979)]
    native={'objects':{n:[]for n in tracked},'optics':[]}
    for tick,f in enumerate(frame_values):
        s.frame_set(math.floor(f),subframe=f%1)
        if f%1==0:
            for n in tracked:native['objects'][n].append(matrix(s.objects[n].matrix_world))
            native['optics'].append(optics(s.objects['CAM_MASTER']))
        cam=s.objects['CAM_MASTER'];eye=cam.matrix_world.translation.copy()
        if tree:
            corners=[cam.matrix_world@(p*(cam.data.clip_start/abs(p.z)))for p in cam.data.view_frame(scene=s)]
            segments=[('near',eye,p)for p in corners]+[('near_edge',corners[i],corners[(i+1)%4])for i in range(4)]
            if previous is not None:segments.append(('swept_eye',previous,eye))
            for kind,a,b in segments:
                v=b-a;length=v.length
                if length<1e-9:continue
                hit,normal,index,distance=tree.ray_cast(a,v/length,length)
                if hit is not None:camera_crossings.setdefault(kind+' | '+names[index],[]).append(f)
            p,normal,index,distance=tree.find_nearest(eye)
            if p is not None and distance<nearest['distance']:nearest={'distance':distance,'frame':f,'object':names[index]}
            if f>=253:
                moving.update(bounds,Vector((0,0,0)),0)
                if moving.tree:
                    for a,b in tree.overlap(moving.tree):actor_contacts.setdefault(names[a]+' | '+moving.names[b],set()).add(f)
        previous=eye
        if tick%300==0:print('PRESERVATION_AND_CLEARANCE',f,'camera_hits',len(camera_crossings),'actor_pairs',len(actor_contacts),flush=True)
    assert len(native['optics'])==990
    return native,{'static_geometry_objects':len(geos),'moving_geometry_objects':len(actor_objects),
          'camera_crossings':camera_crossings,'actor_contacts':{k:sorted(v)for k,v in actor_contacts.items()},
          'nearest_camera_geometry':nearest,'sampling':'Every native frame0–252, half frame253–989; all animated actor descendants, swept camera eye and complete near-plane edge rays.'}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--capture-source',action='store_true')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]if '--'in sys.argv else[])
    assert sha(SOURCE)==SOURCE_SHA
    if args.capture_source:
        before=snapshot(SOURCE);s=bpy.context.scene;names=motion_names(s)
        minimize_scene(s,names);before['motion']=capture_motion(s,names)
        assert sha(SOURCE)==SOURCE_SHA
        (OUT/'preservation-source.json').write_text(json.dumps(before,separators=(',',':')),encoding='utf-8')
        (OUT/'waterway-source.json').write_text(json.dumps({'sha256':SOURCE_SHA,'objects':{n:before['objects'][n]for n in before['protected_groups']['waterway']}},indent=2),encoding='utf-8')
        print('SOURCE_CAPTURED',len(names),'objects990frames',flush=True);return
    before=json.loads((OUT/'preservation-source.json').read_text());assert before['sha256']==SOURCE_SHA
    delivery=json.loads((ROOT/'delivery.json').read_text());allowed=delivery.get('allowed_original_changes',{})
    allowed={n:[('hide_layer'if f=='hidden'else f)for f in fields]for n,fields in allowed.items()}
    after=snapshot(CANDIDATE);s=bpy.context.scene
    assert delivery.get('source_sha256',SOURCE_SHA)==SOURCE_SHA
    assert delivery.get('sha256',after['sha256'])==after['sha256'],'Delivery manifest does not match current candidate'
    old=set(before['objects']);now=set(after['objects']);added=sorted(now-old);deleted=sorted(old-now)
    changed=[];forbidden=[];protected_violations=[];hidden_transform_caches=[]
    protected=set().union(*(set(names)for names in before['protected_groups'].values()))
    def unchanged_authored_chain(name):
        while name:
            a,b=before['objects'].get(name),after['objects'].get(name)
            if not a or not b:return False
            if any(a[field]!=b[field]for field in('parent','matrix_basis','matrix_parent_inverse','animation','constraints','drivers')):return False
            name=a['parent']
        return True
    for name in sorted(old&now):
        fields=[field for field,value in before['objects'][name].items()if after['objects'][name][field]!=value]
        if 'matrix_world'in fields and after['objects'][name]['hide_viewport']and unchanged_authored_chain(name):
            # Blender can leave a viewport-disabled object's world cache empty;
            # unchanged authored transforms and ancestors prove exact placement.
            fields.remove('matrix_world');hidden_transform_caches.append(name)
        if not fields:continue
        changed.append({'object':name,'fields':fields})
        unallowed=[f for f in fields if f not in allowed.get(name,[])]
        if unallowed:forbidden.append({'object':name,'fields':unallowed})
        if name in protected:protected_violations.append({'object':name,'fields':fields})
    material_errors=[n for n,h in before['materials'].items()if after['materials'].get(n)!=h]
    action_errors=[n for n,h in before['actions'].items()if after['actions'].get(n)!=h]
    collection_errors=[]
    for n,oldcol in before['collections'].items():
        col=after['collections'].get(n)
        if col is None:collection_errors.append({'name':n,'field':'missing'});continue
        for field in('hide_render','hide_viewport'):
            if col[field]!=oldcol[field]:collection_errors.append({'name':n,'field':field})
        for field in('objects','children'):
            if not set(oldcol[field])<=set(col[field]):collection_errors.append({'name':n,'field':'removed_'+field})
    changed_geometry=set(added)|{r['object']for r in changed if set(r['fields'])&{'matrix_world','geometry','modifiers','hide_render'}}
    tracked=list(before['motion']['objects'])
    motion,clearance=candidates_clearance(s,changed_geometry,tracked)
    motion_errors={n:max(error(a,b)for a,b in zip(motion['objects'][n],poses))for n,poses in before['motion']['objects'].items()}
    checks={'source_file_immutable':sha(SOURCE)==SOURCE_SHA,'no_original_objects_removed':not deleted,
        'only_declared_original_object_fields_changed':not forbidden,'China_waterway_port_warehouse_actors_ground_ocean_exact':not protected_violations,
        'all_original_actions_exact':not action_errors,'all_original_materials_exact':not material_errors,
        'all_original_990_frame_motion_exact':max(motion_errors.values())==0,
        'camera_optics_990_frames_exact':motion['optics']==before['motion']['optics'],
        'timeline_camera_render_contract_exact':before['scene']==after['scene'],
        'original_collection_membership_visibility_preserved':not collection_errors,
        'new_objects_all_UST_prefix':all(n.startswith('UST_')for n in added),
        'new_changed_geometry_clear_of_camera_path':not clearance['camera_crossings'],
        'new_changed_geometry_clear_of_loading_actors':not clearance['actor_contacts']}
    report={'file':str(CANDIDATE),'sha256':after['sha256'],'source_sha256':SOURCE_SHA,'checks':checks,'pass':all(checks.values()),
       'source_object_count':len(old),'added_object_count':len(added),'added_objects':added,'deleted_objects':deleted,
       'changed_original_objects':changed,'undeclared_changes':forbidden,'protected_group_violations':protected_violations,
       'protected_group_counts':{n:len(v)for n,v in before['protected_groups'].items()},
       'source_action_errors':action_errors,'source_material_errors':material_errors,'collection_errors':collection_errors,
       'hidden_static_transform_cache_exceptions':hidden_transform_caches,
       'motion_max_errors':motion_errors,'camera_and_actor_clearance':clearance,
       'waterway_object_names':before['protected_groups']['waterway']}
    assert sha(CANDIDATE)==after['sha256'],'Candidate changed during audit'
    (OUT/'preservation-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print('PRESERVATION_RESULT',json.dumps({'sha256':report['sha256'],'checks':checks,'changes':len(changed),'added':len(added),'undeclared':forbidden,'protected':protected_violations,'clearance':clearance}),flush=True)
    assert report['pass'],'See preservation-verification.json'


if __name__=='__main__':main()
