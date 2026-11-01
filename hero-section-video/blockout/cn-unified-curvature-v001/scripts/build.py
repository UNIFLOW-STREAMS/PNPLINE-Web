"""Rearrange China landmarks and place the entire connected city on the globe."""
import bpy, bmesh, hashlib, json, math, sys
from pathlib import Path
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import terrain, city_district

SOURCE = ROOT.parent / 'cn-city-expansion-v001/pnpline-cn-city-expansion-v001.blend'
OUTPUT = ROOT / 'pnpline-cn-unified-curvature-v001.blend'
SOURCE_SHA = 'c9da20e19f2cf732245df77c178b1fa85dae00753884ea3c586327a63cbe75bb'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def mesh(name, verts, faces, parent, collection, material):
    data=bpy.data.meshes.new(name+'_Mesh'); data.from_pydata(verts, [], faces)
    data.materials.append(material); data.update()
    obj=bpy.data.objects.new(name,data); collection.objects.link(obj); obj.parent=parent
    return obj

def pedestal(cluster, delta, sphere, layout, collection):
    # A low fitted plinth supports each broad rigid footprint without bending it.
    if cluster['category'] not in {'original_building_or_structure','port_shed','port_office'}:
        return []
    if 'BRIDGE' in cluster['id'] or cluster['anchor'][2]<1.245:return []
    lo=cluster['bounds']['min']; hi=cluster['bounds']['max']
    if max(hi[0]-lo[0],hi[1]-lo[1])<2.5:return []
    z=cluster['anchor'][2]-.012
    corners=[Vector((lo[0]-.03,lo[1]-.03,z)),Vector((hi[0]+.03,lo[1]-.03,z)),Vector((hi[0]+.03,hi[1]+.03,z)),Vector((lo[0]-.03,hi[1]+.03,z))]
    top=[]; bottom=[]
    for a,b in zip(corners,corners[1:]+corners[:1]):
        for j in range(max(1,math.ceil((a-b).length/.35))):
            p=delta@a.lerp(b,j/max(1,math.ceil((a-b).length/.35)))
            top.append(p); bottom.append(sphere.project(p,-.035))
    n=len(top)
    obj=mesh('CNC_SUPPORT_'+cluster['id'],top+bottom,[tuple(range(n)),tuple(range(2*n-1,n-1,-1))]+[(i,n+i,n+(i+1)%n,(i+1)%n)for i in range(n)],layout,collection,bpy.data.materials.get('CNX_stone'))
    bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free()
    obj['cnc_role']='fitted_support';obj['cnc_cluster']=cluster['id']
    return [obj.name]

def reflow_cluster(cluster,sphere,layout,collection):
    I=layout.matrix_world.inverted()
    anchor=Vector(cluster['anchor']); old_up=Vector((0,0,1))
    # All original clusters were authored in the common flat CN tangent plane.
    # Root rotation/scale are preserved inside this common rigid correction.
    x,y=cluster.get('destination_xy',(anchor.x,anchor.y))
    new_up=sphere.normal(x,y)
    offset=anchor.z-1.249988
    target=sphere.point(x,y)+new_up*offset
    rotation=old_up.rotation_difference(new_up).to_matrix().to_4x4()
    delta=Matrix.Translation(target)@rotation@Matrix.Translation(-anchor)
    members=set(cluster['objects'])
    roots=[bpy.data.objects[n]for n in members if bpy.data.objects.get(n) and (not bpy.data.objects[n].parent or bpy.data.objects[n].parent.name not in members)]
    old={o.name:o.matrix_world.copy()for o in roots}
    for obj in roots:
        assert not obj.animation_data or not obj.animation_data.action,('Animated static root',obj.name)
        obj.matrix_world=layout.matrix_world@delta@I@old[obj.name]
        obj['cnc_cluster']=cluster['id'];obj['cnc_radial_anchor']=list(target)
    bpy.context.view_layer.update()
    supports=pedestal(cluster,delta,sphere,layout,collection)
    return {'id':cluster['id'],'category':cluster['category'],'roots':[o.name for o in roots],
            'source_anchor':list(anchor),'target_anchor':list(target),'target_normal':list(new_up),
            'delta_matrix':[list(row)for row in delta],'pedestals':supports,
            'skip_ground_contact':cluster['category']in{'floating_cloud','fender','title_letter'}}

def wrap_surface(row,sphere,layout):
    obj=bpy.data.objects[row['object']]
    T=layout.matrix_world.inverted()@obj.matrix_world; Ti=T.inverted()
    if row.get('new_name'):
        old=obj;obj=bpy.data.objects.new(row['new_name'],old.data.copy())
        for collection in old.users_collection:collection.objects.link(obj)
        obj.matrix_world=old.matrix_world
    elif obj.type!='MESH':
        deps=bpy.context.evaluated_depsgraph_get()
        data=bpy.data.meshes.new_from_object(obj.evaluated_get(deps),depsgraph=deps)
        old=obj; obj=bpy.data.objects.new(old.name+'_CURVED',data)
        for collection in old.users_collection:collection.objects.link(obj)
        obj.matrix_world=old.matrix_world;old.hide_render=True;old.hide_viewport=True
    else:obj.data=obj.data.copy()
    bm=bmesh.new();bm.from_mesh(obj.data)
    for v in bm.verts:v.co=T@v.co
    # Uniformly tessellate broad panels so their edges also follow curvature.
    bmesh.ops.triangulate(bm,faces=list(bm.faces))
    for _ in range(12):
        edges=[e for e in bm.edges if e.calc_length()>.60]
        if not edges:break
        bmesh.ops.subdivide_edges(bm,edges=edges,cuts=1,use_grid_fill=True)
    bmesh.ops.triangulate(bm,faces=list(bm.faces))
    for v in bm.verts:
        p=v.co.copy();height=p.z-row['old_ground_reference']
        if row['object']=='SF_BASIN_WATER_SURFACE':height=.018
        if row['object']=='SF_ISLAND_TOP':height=.040
        v.co=Ti@(sphere.point(p.x,p.y)+sphere.normal(p.x,p.y)*height)
    bm.to_mesh(obj.data);bm.free();obj.data.update()
    for polygon in obj.data.polygons:polygon.use_smooth=True
    obj['cnc_role']='spherical_surface_inlay'
    return {'source':row['object'],'object':obj.name,'vertices':len(obj.data.vertices)}

def main():
    assert sha(SOURCE)==SOURCE_SHA
    survey=json.loads((ROOT/'review/static-original-clusters.json').read_text())
    assert survey['sha256']==SOURCE_SHA
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE));scene=bpy.context.scene;scene.frame_set(0)
    layout=scene.objects['SF_CN_LAYOUT'];col=bpy.data.collections.new('CNC_UNIFIED_CHINA');scene.collection.children.link(col)
    # Rebuild only the explicitly added districts. Original source stays on disk.
    old_names=[o.name for o in bpy.data.objects if o.name.startswith('CNX_')]
    for name in old_names:bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
    print('REMOVED_OLD_DISTRICT',len(old_names),flush=True)
    ocean_report=terrain.restore_cn_ocean(scene,layout)
    ground,sphere,terrain_report=terrain.build_unified_terrain(scene,layout,col)
    for row in survey['replace_ground_objects']:
        obj=bpy.data.objects[row['object']];obj.hide_render=True;obj.hide_viewport=True
        obj['cnc_replaced_by']=ground.name
    print('UNIFIED_GROUND_READY',flush=True)
    for row in survey['rigid_clusters']:
        if row['id']=='DT_GARDEN_ROCK.012':row['destination_xy']=[-26,2.5]
    static=[reflow_cluster(row,sphere,layout,col)for row in survey['rigid_clusters']]
    print('STATIC_REFLOWED',len(static),flush=True)
    wrapped=[wrap_surface(row,sphere,layout)for row in survey['wrap_surfaces']]
    print('SURFACES_WRAPPED',len(wrapped),flush=True)
    districts=city_district.build_districts(scene,layout,col,sphere,ground)
    print('DISTRICTS_REBUILT',districts['building_counts'],flush=True)
    # No decorative wave loops may run across the new continuous land plate.
    outline=terrain.DEFAULT_OUTLINE
    def inside(x,y):
        result=False
        for a,b in zip(outline,outline[1:]+outline[:1]):
            if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:result=not result
        return result
    I=layout.matrix_world.inverted();hidden=[]
    for obj in list(scene.objects):
        if not obj.name.startswith('SF_OCEAN_WAVE'):continue
        points=[I@obj.matrix_world@Vector(p)for p in obj.bound_box]
        center=sum(points,Vector())/8
        if inside(center.x,center.y):obj.hide_viewport=True;obj.hide_render=True;hidden.append(obj.name)
    from animation_reflow import apply_animation_reflow
    animation=apply_animation_reflow(scene,layout,sphere,col)
    report={'source':str(SOURCE),'source_sha256':SOURCE_SHA,'file':str(OUTPUT),
            'sphere':sphere.metadata(),'ground':ground.name,'terrain':terrain_report,'ocean':ocean_report,
            'static_clusters':static,'wrapped_surfaces':wrapped,'replaced_ground':[r['object']for r in survey['replace_ground_objects']],
            'hidden_land_waves':hidden,'districts':districts,'animation':animation,
            'landmark_moves':{'cctv':[[-39,38],[31,26]],'heaven':[[-46,17],[-39,38]],'palace':[[-45,1],[43,10]],'lingnan':[[43,10],[-45,1]]},
            'temple_of_heaven_scale':1.5,'timeline':[0,989,30],'status':'Pending final review'}
    scene['cn_unified_curvature']='All CN regions share one radius141.25 spherical shell; rigid architecture follows radial normals.'
    scene['cn_unified_source_sha256']=SOURCE_SHA
    scene.frame_set(132)
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                view=area.spaces.active.region_3d;view.view_perspective='PERSP'
                view.view_location=layout.matrix_world@Vector((0,24,-6));view.view_distance=155
                view.view_rotation=layout.matrix_world.to_quaternion()@(Vector((0,24,-6))-Vector((55,-100,115))).to_track_quat('-Z','Y')
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT),compress=True)
    report['sha256']=sha(OUTPUT);report['object_count']=len(scene.objects)
    (ROOT/'delivery.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    (ROOT/'review/build.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    assert sha(SOURCE)==SOURCE_SHA
    print('CURVATURE_BUILD_COMPLETE',report['sha256'],flush=True)

if __name__=='__main__':main()
