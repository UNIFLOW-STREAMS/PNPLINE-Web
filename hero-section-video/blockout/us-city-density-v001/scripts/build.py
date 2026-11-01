"""US core: reference-led landmark replacement, architecture infill and gap planting."""
import bpy,bmesh,json,math,random,hashlib,sys
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.geometry import convex_hull_2d
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
sys.path.append(str(ROOT.parent/'curvature-rework-v001/scripts'))
sys.path.append(str(ROOT.parent/'cn-shanghai-density-v001/scripts'))
import us_assets,citykit
from mapping import surface,normal,CENTER
SOURCE=ROOT.parent/'cn-shanghai-density-v001/pnpline-cn-shanghai-density-v001.blend'
OUT=ROOT/'pnpline-us-city-density-v001.blend'
SHA='c0f7d784dbb67562614cfd46cc3a493418de6f6712db2aef2d8933fbee5672ce'
YAW=math.radians(-32)

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def params(p):
    d=p-CENTER;r=d.length;h=math.hypot(d.x,d.y);a=math.atan2(h,d.z)
    return Vector((d.x/h*a*140,d.y/h*a*140,r-140))if h>1e-8 else Vector((0,0,r-140))
def frame(x,y,height=.84,yaw=YAW):
    q=Vector((0,0,1)).rotation_difference(normal(x,y))
    return Matrix.Translation(surface(x,y,height))@q.to_matrix().to_4x4()@Matrix.Rotation(yaw,4,'Z')
def design(x,y):return (.8480480909*x+.5299192667*y-19.6070099,-.5299192667*x+.8480480909*y+6.6222191)
def bbox(poly):return [min(p[0]for p in poly),min(p[1]for p in poly),max(p[0]for p in poly),max(p[1]for p in poly)]
def intersects(a,b,gap=.12):
    aa,bb=bbox(a),bbox(b)
    if aa[0]>bb[2]+gap or bb[0]>aa[2]+gap or aa[1]>bb[3]+gap or bb[1]>aa[3]+gap:return False
    for poly in [a,b]:
        for p,q in zip(poly,poly[1:]+poly[:1]):
            x,y=p[1]-q[1],q[0]-p[0];l=math.hypot(x,y)
            if l<1e-8:continue
            x/=l;y/=l;ap=[v[0]*x+v[1]*y for v in a];bp=[v[0]*x+v[1]*y for v in b]
            if max(ap)+gap<min(bp)or max(bp)+gap<min(ap):return False
    return True
def hull(pts):
    v=[Vector((p[0],p[1]))for p in pts]
    return [list(v[i])for i in convex_hull_2d(v)]
def rectangular_footprint(F,w,d):
    return hull([params(F@Vector((x*w/2,y*d/2,0)))for x,y in [(-1,-1),(1,-1),(1,1),(-1,1)]])

def main():
    assert sha(SOURCE)==SHA
    survey=json.loads((ROOT/'review/us-survey.json').read_text());assert survey['sha256']==SHA
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s=bpy.context.scene;s.frame_set(349)
    U=s.objects['US_FRAME'];I=U.matrix_world.inverted();groups={r['root']:r for r in survey['groups']}
    col=bpy.data.collections.new('USD_US_CITY_DENSITY');s.collection.children.link(col)
    palette={'stone':(.60,.57,.49),'ivory':(.82,.79,.69),'red':(.34,.18,.12),'gold':(.63,.44,.19),
     'roof':(.12,.15,.16),'glass':(.10,.26,.34),'dark_glass':(.035,.105,.15),'metal':(.57,.65,.68),
     'white':(.86,.86,.80),'dark':(.025,.042,.05),'wood':(.20,.12,.07),'green':(.12,.28,.08),
     'paving':(.62,.62,.56),'leaf_light':(.23,.37,.12),'leaf_deep':(.075,.20,.075)}
    M={}
    for name,color in palette.items():
        m=bpy.data.materials.new('USD_'+name);m.diffuse_color=(*color,1);m.use_nodes=True
        bsdf=m.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Base Color'].default_value=(*color,1);bsdf.inputs['Roughness'].default_value=.48
        if name in {'glass','metal','dark_glass'}:bsdf.inputs['Metallic'].default_value=.32
        M[name]=m
    allowed={};hidden=[];height_changes=[];relocations=[];replacements=[];sites=[];tree_sites=[]
    def hide(name):
        obj=s.objects.get(name)
        if obj is None:return
        obj.hide_render=True;obj.hide_viewport=True;allowed[name]=['hide_render','hide_viewport'];hidden.append(name)
    def declare(root):
        allowed[root.name]=['matrix_basis','matrix_world']
        for obj in root.children_recursive:allowed[obj.name]=['matrix_world']
    def old_footprint(names):
        pts=[]
        for name in names:
            ob=s.objects[name]
            if ob.hide_render or ob.type not in {'MESH','CURVE','FONT'}:continue
            T=I@ob.matrix_world
            pts.extend(params(T@Vector(p))for p in ob.bound_box)
        return hull(pts)if pts else []
    # Preserve source geometry as hidden editable alternatives, replacing only
    # the two deliberately selected central landmark designs.
    hero_names=['CV_CENTRAL_TOWER_UC_CITY_DISTRICT','CV_GLASS_TOWER_UC_CITY_DISTRICT']
    for name in hero_names:
        for member in groups[name]['members']:hide(member)
        token='CENTRAL_TOWER'if'CENTRAL'in name else'GLASS_TOWER'
        for obj in list(s.objects):
            if obj.name.startswith('CV_FOUNDATION_')and token in obj.name:hide(obj.name)
    # The enlarged previous rear skyline was taller than the focal pair.
    # Restore the reference hierarchy without deleting the rear city district.
    for row in groups.values():
        x,y=row['anchor_parameter'][:2];h=row['height_above_surface']
        if not(row['root'].startswith('CE_')and -35<x<65 and 40<=y<=75 and h>24):continue
        root=s.objects[row['root']];declare(root);target=19.0 if any(t in root.name for t in ['WTC','NEEDLE','ROCKEFELLER'])else 16.5+(len(height_changes)%3)
        factor=(target-.28)/(h-.28);uniform='NEEDLE'in root.name
        root.matrix_basis=root.matrix_basis@Matrix.Diagonal((factor if uniform else 1,factor if uniform else 1,factor,1))
        height_changes.append({'root':root.name,'source_height':h,'target_height':target,'scale_z':factor,'uniform':uniform,'members':row['all_descendants'],'anchor_parameter':row['anchor_parameter']})
    bpy.context.view_layer.update()
    for row in groups.values():
        if row['root']not in hero_names:row['footprint_parameter']=old_footprint(row['members'])
    print('HIERARCHY',len(height_changes),flush=True)
    def evaluated_mesh(obj):
        ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();T=I@ev.matrix_world
        vv=[T@v.co for v in me.vertices];ff=[tuple(f.vertices)for f in me.polygons];ev.to_mesh_clear();return vv,ff
    ground=[]
    for name in ['US_LAND_TERRACE','CE_NY_CURVED_LAND']:
        vv,ff=evaluated_mesh(s.objects[name]);ground.append(BVHTree.FromPolygons(vv,ff))
    # Keep exact street/port geometry clear using radial rays, avoiding the
    # convex-hull shortcut that would close the interiors of curved roads.
    protected=[]
    for row in survey['protected_road_port_objects']:
        b=row['bounds_parameter']
        if b['max'][0]<-36 or b['min'][0]>30 or b['max'][1]<14 or b['min'][1]>66:continue
        obj=s.objects[row['name']]
        if obj.hide_render:continue
        vv,ff=evaluated_mesh(obj);protected.append((bbox(row['footprint_parameter']),BVHTree.FromPolygons(vv,ff),obj.name))
    for obj in s.objects:
        if obj.hide_render or obj.type!='MESH' or not obj.name.startswith(('UC_TREE','CE_NY_TREE')):continue
        vv,ff=evaluated_mesh(obj);pp=[params(p)for p in vv]
        if pp:protected.append((bbox(pp),BVHTree.FromPolygons(vv,ff),obj.name))
    def dry_and_accessible(poly,allow_roads=False):
        samples=[]
        for a,b in zip(poly,poly[1:]+poly[:1]):
            count=max(2,math.ceil(math.dist(a,b)/.38))
            samples.extend((a[0]+(b[0]-a[0])*k/count,a[1]+(b[1]-a[1])*k/count)for k in range(count))
        samples.append((sum(p[0]for p in poly)/len(poly),sum(p[1]for p in poly)/len(poly)))
        for x,y in samples:
            n=normal(x,y);origin=surface(x,y,80)
            heights=[(b.ray_cast(origin,-n,100)[0])for b in ground];heights=[(p-CENTER).length-140 for p in heights if p is not None]
            if not heights or abs(max(heights)-.68)>.035:return False
            if not allow_roads:
                for bb,bvh,name in protected:
                    if bb[0]-.10<=x<=bb[2]+.10 and bb[1]-.10<=y<=bb[3]+.10:
                        if bvh.ray_cast(origin,-n,100)[0]is not None:return False
        return True
    obstacles=[{'id':r['root'],'poly':r['footprint_parameter']}for r in groups.values()if r['root']not in hero_names and len(r['footprint_parameter'])>2]
    def clear(poly,gap=.16):return not any(intersects(poly,r['poly'],gap)for r in obstacles)
    def root_at(name,x,y,height=.84,yaw=YAW):
        ob=bpy.data.objects.new(name,None);col.objects.link(ob);ob.parent=U;ob.matrix_basis=frame(x,y,height,yaw);ob['usd_anchor']=[x,y,height];return ob
    def support(name,F,w,d):
        corners=[Vector((x*w/2,y*d/2,-.008))for x,y in [(-1,-1),(1,-1),(1,1),(-1,1)]];top=[];bottom=[]
        for a,b in zip(corners,corners[1:]+corners[:1]):
            count=max(1,math.ceil((b-a).length/.3))
            for k in range(count):
                p=F@a.lerp(b,k/count);top.append(p);bottom.append(CENTER+(p-CENTER).normalized()*140.65)
        n=len(top);me=bpy.data.meshes.new(name+'_MESH');me.from_pydata(top+bottom,[],[tuple(range(n)),tuple(range(2*n-1,n-1,-1))]+[(i,n+i,n+(i+1)%n,(i+1)%n)for i in range(n)])
        me.materials.append(M['stone']);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
        ob=bpy.data.objects.new(name,me);col.objects.link(ob);ob.parent=U;ob['usd_role']='foundation';return ob.name
    for old,kind,w,d,h in [(hero_names[0],'empire',5,4.7,32),(hero_names[1],'onewtc',4.8,4.8,36)]:
        x,y=groups[old]['anchor_parameter'][:2]
        if kind=='onewtc':x,y=design(10,44.8)
        name='USD_'+kind.upper();root=root_at(name+'_ROOT',x,y)
        objs=us_assets.build(kind,name,root,col,M,w,d,h);foundation=support(name+'_FOUNDATION',root.matrix_basis,w+.08,d+.08)
        poly=rectangular_footprint(root.matrix_basis,w+.08,d+.08)
        assert dry_and_accessible(poly),('Hero unsupported or on street',kind)
        replacements.append({'root':root.name,'kind':kind,'source_root':old,'objects':[o.name for o in objs],'foundation':foundation,'anchor_parameter':[x,y,.84],'size':[w,d,h],'footprint_parameter':poly})
        obstacles.append({'id':root.name,'poly':poly})
    # Refine the existing lower commercial street wall in place. Cornices,
    # arched shopfronts, fire escapes and rooftop tanks mirror the reference.
    for row in groups.values():
        if not row['root'].startswith(('CV_UC_BLOCK_00_','CV_UC_BLOCK_01_')):continue
        x,y=row['anchor_parameter'][:2];F=frame(x,y)
        pts=[F.inverted()@I@s.objects[n].matrix_world@Vector(p)for n in row['members']for p in s.objects[n].bound_box]
        w=(max(p.x for p in pts)-min(p.x for p in pts))*.94;d=(max(p.y for p in pts)-min(p.y for p in pts))*.94
        h=row['height_above_surface']-.16;poly=rectangular_footprint(F,w+.12,d+.12)
        own=next(r for r in obstacles if r['id']==row['root']);obstacles.remove(own)
        if not clear(poly,.12)or not dry_and_accessible(poly):obstacles.append(own);continue
        for member in row['members']:hide(member)
        token=row['root'].replace('CV_','').replace('_UC_CITY_DISTRICT','')
        for obj in list(s.objects):
            if obj.name.startswith('CV_FOUNDATION_')and token in obj.name:hide(obj.name)
        number=len(replacements)-2;kind='masonry'if number%3==0 else'brownstone';name=f'USD_REFINED_FRONTAGE_{number:02d}';root=root_at(name+'_ROOT',x,y)
        objs=us_assets.build(kind,name,root,col,M,w,d,h,number);foundation=support(name+'_FOUNDATION',F,w+.08,d+.08)
        replacements.append({'root':root.name,'kind':kind,'source_root':row['root'],'objects':[o.name for o in objs],'foundation':foundation,'anchor_parameter':[x,y,.84],'size':[w,d,h],'footprint_parameter':poly})
        obstacles.append({'id':root.name,'poly':poly})
    print('REPLACEMENTS',len(replacements),flush=True)
    rng=random.Random(92351)
    def add(kind,xd,yd,w,d,h,variant):
        x,y=design(xd,yd);F=frame(x,y);poly=rectangular_footprint(F,w+.12,d+.12)
        if not(-33<x<28 and 16<y<64)or not clear(poly)or not dry_and_accessible(poly):return False
        name=f'USD_CORE_{kind.upper()}_{len(sites):03d}';root=root_at(name+'_ROOT',x,y)
        objects=us_assets.build(kind,name,root,col,M,w,d,h,variant);foundation=support(name+'_FOUNDATION',F,w+.08,d+.08)
        sites.append({'root':root.name,'kind':kind,'objects':[o.name for o in objects],'foundation':foundation,'anchor_parameter':[x,y,.84],'design_xy':[xd,yd],'size':[w,d,h],'footprint_parameter':poly})
        obstacles.append({'id':root.name,'poly':poly});return True
    # A dense lower street wall, then glass/stone midrises around the hero pair.
    for j in range(17):
        yd=23+j*1.72
        for k in range(27):
            xd=-25.7+k*1.88+(j%2)*.18
            w=rng.uniform(1.35,1.65);d=rng.uniform(1.30,1.55)
            kind='brownstone'if yd<32 and k%3 else'masonry'if yd<37 or k%3==0 else'glass'
            h=rng.uniform(3.0,5.1)if yd<32 else rng.uniform(4.7,8.5)if kind=='masonry'else rng.uniform(6.2,12.0)
            add(kind,xd,yd,w,d,h,j*29+k)
    # Narrow secondary infill closes suitable inter-building gaps.
    for j in range(23):
        yd=24+j*1.21
        for k in range(36):
            xd=-25+k*1.35+(j%2)*.43
            kind='masonry'if yd<35 else'glass';h=rng.uniform(2.8,4.8)if yd<35 else rng.uniform(4.1,7.0)
            add(kind,xd,yd,.94,.91,h,k+3*j)
    print('NEW_BUILDINGS',len(sites),flush=True)
    # Jittered, size-varied groups in architectural gaps only. No field planting.
    architecture=[r['poly']for r in obstacles if not any(t in r['id']for t in ['TREE','STAR','LETTER','TAXI','LAMP'])]
    def edge_distance(p,poly):
        best=1e9
        for a,b in zip(poly,poly[1:]+poly[:1]):
            dx,dy=b[0]-a[0],b[1]-a[1];den=dx*dx+dy*dy;t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/den))if den else 0
            best=min(best,math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy))
        return best
    for j in range(40):
        for k in range(65):
            xd=-26+k*.79+rng.uniform(-.18,.18);yd=23+j*.73+rng.uniform(-.17,.17);x,y=design(xd,yd)
            if not(-33<x<28 and 16<y<64):continue
            if min(edge_distance((x,y),p)for p in architecture)>1.25:continue
            radius=rng.uniform(.23,.36);F=frame(x,y,.69);poly=rectangular_footprint(F,2*radius,2*radius)
            if not clear(poly,.12)or not dry_and_accessible(poly):continue
            name=f'USD_GAP_TREE_{len(tree_sites):03d}';root=root_at(name+'_ROOT',x,y,.69);h=rng.uniform(.95,1.65)
            b=citykit.Batch(name,root,col,M);b.rod('wood',(0,0,0),(0,0,h*.8),.035,7)
            for i in range(3):
                a=i*math.tau/3;b.ellipsoid(['green','leaf_light','leaf_deep'][(i+len(tree_sites))%3],(math.cos(a)*radius*.3,math.sin(a)*radius*.3,h*.76),(radius*.67,radius*.67,h*.30),10,6)
            objs=b.finish()
            for ob in objs:ob['usd_role']='gap_tree'
            tree_sites.append({'root':root.name,'objects':[o.name for o in objs],'anchor_parameter':[x,y,.69],'height':h,'radius':radius,'footprint_parameter':poly})
            obstacles.append({'id':root.name,'poly':poly})
    print('NEW_TREES',len(tree_sites),flush=True)
    s['us_city_density_revision']='Reference-led Empire State and One WTC, subordinate rear towers, dense city architecture and gap trees. Logistics and motion preserved.'
    s.frame_set(390)
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                rv=area.spaces.active.region_3d;target=Vector((1,39,10));eye=Vector((46,-35,69))
                rv.view_location=U.matrix_world@target;rv.view_rotation=U.matrix_world.to_quaternion()@(target-eye).to_track_quat('-Z','Y');rv.view_distance=85;rv.view_perspective='PERSP'
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
    report={'source':str(SOURCE),'source_sha256':SHA,'file':str(OUT),'sha256':sha(OUT),'allowed_original_changes':allowed,'hidden_original_objects':hidden,
       'replacements':replacements,'height_changes':height_changes,'relocations':relocations,'sites':sites,'tree_sites':tree_sites,
       'building_count':len(sites),'tree_count':len(tree_sites),'replacement_count':len(replacements),'building_counts':{k:sum(r['kind']==k for r in sites)for k in ['masonry','brownstone','glass']},
       'timeline':[0,989,30],'camera_changed':False,'terrain_changed':False,'status':'Pending independent geometry, preservation and visual checks'}
    (ROOT/'delivery.json').write_text(json.dumps(report,indent=2),encoding='utf-8');(ROOT/'review/build.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    assert sha(SOURCE)==SHA
    print('US_CITY_SAVED',report['sha256'],flush=True)

if __name__=='__main__':main()
