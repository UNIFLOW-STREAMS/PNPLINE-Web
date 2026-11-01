"""Read-only independent harbor clearance and terrain audit."""
import bpy, json, hashlib
import statistics
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

R=Path(__file__).resolve().parents[1]
s=bpy.context.scene
s.frame_set(0)
source=Path(bpy.data.filepath)
I=s.objects['SF_CN_LAYOUT'].matrix_world.inverted()

def under(o,name):
    while o:
        if o.name==name:return True
        o=o.parent
    return False

def bounds(o):
    ps=[I@o.matrix_world@Vector(p) for p in o.bound_box]
    return [tuple(min(p[k] for p in ps) for k in range(3)),tuple(max(p[k] for p in ps) for k in range(3))]

def intersects(a,b,eps=.002):
    return all(min(a[1][k],b[1][k])-max(a[0][k],b[0][k])>eps for k in range(3))

def tree(obs):
    vs=[];fs=[];ns=[]
    for o in obs:
        k=len(vs);vs.extend(I@o.matrix_world@v.co for v in o.data.vertices)
        fs.extend(tuple(k+i for i in p.vertices)for p in o.data.polygons)
        ns.extend([o.name]*len(o.data.polygons))
    return BVHTree.FromPolygons(vs,fs),ns

visible=[o for o in s.objects if o.type=='MESH' and not o.hide_render]
bs={o.name:bounds(o)for o in visible}
port=[o for o in visible if under(o,'PORT_MODEL_ROOT')]
old=[o for o in visible if not under(o,'PORT_MODEL_ROOT') and not any(under(o,n)for n in ['A02_SHIP','A01_CONTAINER','P01_SPREADER','W01_NEW_PALLET','PORT_CRANE_PLACEMENT'])]
region=[(-28,-15,1.3),(30,1.7,12)]
near=[o for o in old if intersects(bs[o.name],region)]
report={'source':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'quay_bounds':bs['CN_QUAY'],'old_objects_near_port':[{'name':o.name,'bounds':bs[o.name]}for o in near]}
# Test visible new above-deck geometry against old visible above-deck objects.
new=[o for o in port if bs[o.name][1][2]>1.4 and not o.name.startswith(('PORT_APRON','PORT_ACCESS_ROAD','PORT_YARD_CROSS_LANE','PORT_EDGE_FRONT','PORT_FENDER','PORT_BOLLARD'))]
old_above=[o for o in near if bs[o.name][1][2]>1.4 and not any(q in o.name.upper() for q in ['WATER','WAVE','SEA','TERRACE','GROUND','COAST'])]
oldtree,on=tree(old_above)
newtree,nn=tree(new)
hits={}
for i,j in newtree.overlap(oldtree):
    pair=nn[i]+' | '+on[j]
    hits[pair]=hits.get(pair,0)+1
report['new_vs_old_surface_crossings']=hits

# Internal crossings between independent modules, excluding intended deck, rail, and road contacts.
roots=[o for o in s.objects if o.name.startswith('PORT_CONTAINER_') and o.type=='EMPTY']
roots += [o for o in s.objects if o.name.startswith(('PORT_TRUCK','PORT_COMPANION_CRANE')) and o.type=='EMPTY']
roots += [s.objects['CR_COMPACT_GANTRY']]
groups=[]
for root in roots:
    obs=[o for o in root.children_recursive if o.type=='MESH' and not o.hide_render]
    if not obs:continue
    lo=tuple(min(bs[o.name][0][k]for o in obs)for k in range(3))
    hi=tuple(max(bs[o.name][1][k]for o in obs)for k in range(3))
    groups.append((root.name,(lo,hi),obs))
modulehits=[];cache={}
for a,(an,ab,ao)in enumerate(groups):
    for bn,bb,bo in groups[a+1:]:
        if not intersects(ab,bb):continue
        if an not in cache:cache[an]=tree(ao)
        if bn not in cache:cache[bn]=tree(bo)
        at,ans=cache[an];bt,bns=cache[bn];cross=at.overlap(bt)
        if cross:modulehits.append({'a':an,'b':bn,'a_bounds':ab,'b_bounds':bb,'pairs':sorted(set((ans[i],bns[j])for i,j in cross))[:20]})
report['module_crossings']=modulehits
report['terrain']=[{'name':o.name,'bounds':bs[o.name]}for o in visible if any(q in o.name.upper() for q in ['WATER','OCEAN','TERRACE','COAST','LAND'])]
# Below-water/front terrain contact and ship transition at representative frames.
terrain=[o for o in old if any(q in o.name.upper()for q in ['TERRACE','COAST','LAND'])]
terr,tn=tree(terrain)
ocean,_=tree([s.objects['EARTH_CONTINUOUS_OCEAN']])
land,_=tree([s.objects['SF_FRONT_LAND']])
report['mainland_connection_samples']=[]
for x in range(-28,31,2):
    hit=land.ray_cast(Vector((x,1.69,10)),Vector((0,0,-1)))[0]
    first=None
    for j in range(100):
        y=1.7+j*.1
        if land.ray_cast(Vector((x,y,10)),Vector((0,0,-1)))[0]:first=round(y,2);break
    report['mainland_connection_samples'].append({'x':x,'mainland_under_back_edge':bool(hit),'first_mainland_y_behind_port':first})
report['front_quay_water_samples']=[]
for x in [-28,-20,-10,0,10,20,30]:
    hit=ocean.ray_cast(Vector((x,-15,100)),Vector((0,0,-1)))[0]
    report['front_quay_water_samples'].append({'x':x,'water_z':hit.z if hit else None,'foundation_bottom':bs['CN_QUAY'][0][2]})
report['ship_mesh_names']=[o.name for o in s.objects['A02_SHIP'].children_recursive if o.type=='MESH']
samples=[]
for f in [0,24,48,72,120,156,180,216,240,264,288,312,336,360]:
    s.frame_set(f)
    ship=[o for o in s.objects['A02_SHIP'].children_recursive if o.type=='MESH'and not o.hide_render]
    st,sn=tree(ship)
    collisions=sorted(set(sn[i]+' | '+tn[j]for i,j in st.overlap(terr)))
    pts=[I@o.matrix_world@Vector(p)for o in ship for p in o.bound_box]
    lo=Vector([min(p[k]for p in pts)for k in range(3)]);hi=Vector([max(p[k]for p in pts)for k in range(3)])
    center=(lo+hi)/2
    water=ocean.ray_cast(Vector((center.x,center.y,100)),Vector((0,0,-1)))[0]
    samples.append({'frame':f,'ship_bounds':[tuple(lo),tuple(hi)],'terrain_crossings':collisions,'ocean_at_ship_center':list(water)if water else None,'hull_bottom_to_water_z':lo.z-water.z if water else None})
report['ship_samples']=samples

def hull_water_sample(scene,water_bvh,frame):
    scene.frame_set(frame)
    hulls=[o for o in scene.objects['A02_SHIP'].children_recursive if o.type=='MESH' and not o.hide_render and o.name in {'SF_HULL_BLUE','SF_HULL_RED','SHIP_HULL'}]
    ship=scene.objects['A02_SHIP'];red=scene.objects['SF_HULL_RED']
    ri=ship.matrix_world.inverted()@red.matrix_world
    rootpoints=[ri@v.co for v in red.data.vertices]
    bottomz=min(p.z for p in rootpoints)
    ring=[p for p in rootpoints if p.z<bottomz+.01]
    center=sum(ring,Vector())/len(ring)
    ship_to_layout=I@ship.matrix_world
    bottompoints=[center]
    for a,b in zip(ring,ring[1:]+ring[:1]):
        for i in range(8):
            p=a.lerp(b,i/8)
            bottompoints.extend([p,p.lerp(center,.5)])
    depths=[];positions=[]
    for bp in bottompoints:
        bottom=ship_to_layout@bp;x=bottom.x;y=bottom.y
        water=water_bvh.ray_cast(Vector((x,y,120)),Vector((0,0,-1)))[0]
        if water:
            depth=water.z-bottom.z
            depths.append(depth);positions.append({'x':x,'y':y,'hull_bottom_z':bottom.z,'water_z':water.z,'depth':depth})
    return {'frame':frame,'hulls':[o.name for o in hulls],'min_immersion':min(depths),'median_immersion':statistics.median(depths),'max_immersion':max(depths),'wet_samples':sum(x>0 for x in depths),'total_samples':len(depths),'lowest_immersion_sample':min(positions,key=lambda p:p['depth']),'highest_immersion_sample':max(positions,key=lambda p:p['depth'])}

frames=list(range(0,157,12))+list(range(160,361,4))
report['hull_water_samples']=[hull_water_sample(s,ocean,f)for f in frames]
s.frame_set(0)
water_region=json.loads(s.get('cn_port_water_report','{}')).get('region_layout_xy',[-34,110,-63,40])
deck,_=tree([s.objects['CN_QUAY']])
supports=[]
for o in visible:
    if not o.name.startswith(('CR_FOOT_','PORT_CRANE_BOGIE')):continue
    bounds_now=bounds(o)
    cx=(bounds_now[0][0]+bounds_now[1][0])/2;cy=(bounds_now[0][1]+bounds_now[1][1])/2
    surface=deck.ray_cast(Vector((cx,cy,10)),Vector((0,0,-1)))[0]
    supports.append({'name':o.name,'bottom_z':bounds_now[0][2],'deck_z':surface.z if surface else None,'gap':bounds_now[0][2]-surface.z if surface else None})
report['crane_foundation_support']=supports
report['mainland_connection_sample_scope']='Original SF_FRONT_LAND footprint at quay back edge; these values describe the original coast taper, not a standalone connectivity failure.'
sea=s.objects['EARTH_CONTINUOUS_OCEAN']
ocean_new_coords={tuple(v.co)for v in sea.data.vertices}
ocean_new_matrix=list(map(list,sea.matrix_world))
ocean_new_materials=[(m.name,list(m.diffuse_color))for m in sea.data.materials]
ocean_new_smooth=[p.use_smooth for p in sea.data.polygons]
bpy.ops.wm.open_mainfile(filepath=str(R/'inputs/base.blend'))
bsrc=bpy.context.scene;bsrc.frame_set(0)
bocean,_=tree([bsrc.objects['EARTH_CONTINUOUS_OCEAN']])
bship=[o for o in bsrc.objects['A02_SHIP'].children_recursive if o.type=='MESH'and not o.hide_render]
bpts=[I@o.matrix_world@Vector(p)for o in bship for p in o.bound_box]
blo=Vector([min(p[k]for p in bpts)for k in range(3)]);bhi=Vector([max(p[k]for p in bpts)for k in range(3)])
bc=(blo+bhi)/2
bwater=bocean.ray_cast(Vector((bc.x,bc.y,100)),Vector((0,0,-1)))[0]
report['baseline_ship_at_f0']={'bounds':[list(blo),list(bhi)],'water_at_center':list(bwater),'hull_bottom_to_water_z':blo.z-bwater.z}
report['baseline_hull_water_samples']=[hull_water_sample(bsrc,bocean,f)for f in frames]
oldsea=bsrc.objects['EARTH_CONTINUOUS_OCEAN']
far=[];us=[]
for v in oldsea.data.vertices:
    p=I@oldsea.matrix_world@v.co
    if p.x<water_region[0]-.01 or p.x>water_region[1]+.01 or p.y<water_region[2]-.01 or p.y>water_region[3]+.01 or p.z<-100:far.append(tuple(v.co)in ocean_new_coords)
    if p.z<-100:us.append(tuple(v.co)in ocean_new_coords)
report['ocean_preservation']={'excluded_legitimate_deformation_region_xy':water_region,'far_original_vertices_present_exact':all(far),'far_vertices_checked':len(far),'opposite_US_hemisphere_original_vertices_present_exact':all(us),'opposite_vertices_checked':len(us),'object_matrix_unchanged':ocean_new_matrix==list(map(list,oldsea.matrix_world)),'material_slots_and_colors_unchanged':ocean_new_materials==[(m.name,list(m.diffuse_color))for m in oldsea.data.materials],'baseline_smooth_faces':sum(p.use_smooth for p in oldsea.data.polygons),'baseline_total_faces':len(oldsea.data.polygons),'new_smooth_faces':sum(ocean_new_smooth),'new_total_faces':len(ocean_new_smooth)}
loading=[r for r in report['hull_water_samples']if r['frame']<=156]
exposed=[r for r in report['hull_water_samples']if r['min_immersion']<0]
report['provisional_departure_note']={'first_sample_with_exposed_bottom':exposed[0]['frame']if exposed else None,'last_sample_with_exposed_bottom':exposed[-1]['frame']if exposed else None,'worst_sample':min(exposed,key=lambda r:r['min_immersion'])if exposed else None,'entire_hull_floating_samples':[r['frame']for r in report['hull_water_samples']if r['wet_samples']==0],'interpretation':'Partial bow exposure during temporary berth-to-source route blend remains for the explicitly deferred route/motion task. Loading support remains preserved.'}
report['checks']={'new_vs_old_above_deck_clear':not report['new_vs_old_surface_crossings'],'independent_port_modules_clear':not report['module_crossings'],'loading_hull_all_samples_immersed':all(r['min_immersion']>0 for r in loading),'working_and_companion_crane_feet_supported':len(supports)==12 and all(r['gap']is not None and abs(r['gap'])<.04 for r in supports),'far_ocean_geometry_exact':all(far),'opposite_ocean_geometry_exact':all(us),'ocean_matrix_and_material_slots_preserved':report['ocean_preservation']['object_matrix_unchanged']and report['ocean_preservation']['material_slots_and_colors_unchanged'],'no_entire_hull_floating_sample':not report['provisional_departure_note']['entire_hull_floating_samples']}
(report['scope'])={'scene_saved':False,'surface_collision_pairs':'new above-deck modules versus old above-deck objects near port; independent container/truck/crane groups','caveat':'BVH surface intersections cannot detect fully enclosed objects. Ship sample bounds include visible wake meshes.'}
(R/'review/static-audit.json').write_text(json.dumps(report,indent=2))
print('STATIC_AUDIT',json.dumps({'near_count':len(near),'new_old_hits':hits,'module_hits':modulehits,'ship_samples':samples}))
