"""Densify Shanghai while preserving the authored spherical waterway and animation."""
import bpy,bmesh,json,math,random,hashlib,sys
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.geometry import convex_hull_2d
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
sys.path.append(str(ROOT.parent/'cn-unified-curvature-v001/scripts'))
import citykit,shanghai_assets
from terrain import globe_surface
SOURCE=ROOT.parent/'cn-unified-curvature-v001/pnpline-cn-unified-curvature-v001.blend'
OUT=ROOT/'pnpline-cn-shanghai-density-v001.blend'
SHA='f0f07fcbbd00f9f3c2d3402092684e6326610ffcf65678a33490ad5d86f4b978'

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def point_inside(p,poly):
    x,y=p;inside=False
    for a,b in zip(poly,poly[1:]+poly[:1]):
        if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:inside=not inside
    return inside
def bounds(poly):return(min(p[0]for p in poly),min(p[1]for p in poly),max(p[0]for p in poly),max(p[1]for p in poly))
def overlaps(a,b,gap=.10):
    aa,bb=bounds(a),bounds(b)
    if aa[0]>bb[2]+gap or bb[0]>aa[2]+gap or aa[1]>bb[3]+gap or bb[1]>aa[3]+gap:return False
    for poly in [a,b]:
        for p,q in zip(poly,poly[1:]+poly[:1]):
            x,y=-(q[1]-p[1]),q[0]-p[0];length=math.hypot(x,y)
            if length<1e-8:continue
            x/=length;y/=length
            ap=[v[0]*x+v[1]*y for v in a];bp=[v[0]*x+v[1]*y for v in b]
            if max(ap)+gap<min(bp)or max(bp)+gap<min(ap):return False
    return True
def boxpoly(x,y,w,d):return[(x-w/2,y-d/2),(x+w/2,y-d/2),(x+w/2,y+d/2),(x-w/2,y+d/2)]

def main():
    assert digest(SOURCE)==SHA
    survey=json.loads((ROOT/'review/shanghai-survey.json').read_text());assert survey['sha256']==SHA
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s=bpy.context.scene;s.frame_set(0)
    D=s.objects['SF_CN_LAYOUT'];I=D.matrix_world.inverted();sphere=globe_surface(s,D)
    col=bpy.data.collections.new('SHD_SHANGHAI_DENSITY');s.collection.children.link(col)
    random.seed(13117)
    palette={'stone':(.61,.59,.53),'ivory':(.82,.80,.70),'red':(.52,.095,.06),'gold':(.88,.55,.16),
      'roof':(.095,.13,.15),'blue_roof':(.025,.24,.38),'glass':(.12,.30,.39),'dark_glass':(.04,.12,.17),
      'metal':(.58,.67,.69),'white':(.88,.87,.80),'dark':(.035,.047,.05),'wood':(.24,.13,.075),
      'green':(.17,.33,.12),'water':(.06,.24,.28),'road':(.22,.25,.24),'paving':(.64,.64,.58),
      'leaf_light':(.25,.40,.15),'leaf_deep':(.10,.25,.10)}
    M={}
    for name,color in palette.items():
        m=bpy.data.materials.new('SHD_'+name);m.diffuse_color=(*color,1);m.use_nodes=True
        bsdf=m.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Base Color'].default_value=(*color,1);bsdf.inputs['Roughness'].default_value=.58
        if name in {'glass','metal','gold','dark_glass'}:bsdf.inputs['Metallic'].default_value=.25
        M[name]=m
    allowed={};heroes=[];relocations=[];sites=[];tree_sites=[]
    rows={row['id']:row for row in survey['all_rigid_cluster_footprints']}
    inner=survey['water']['dry_island_boundary_xy'];outer=survey['water']['outer_boundary_xy']
    border=KDTree(len(inner)+len(outer))
    for k,p in enumerate(inner+outer):border.insert((p[0],p[1],0),k)
    border.balance()
    def dry(poly,region,bank_margin=.12):
        samples=[]
        for a,b in zip(poly,poly[1:]+poly[:1]):
            samples.extend([(a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t)for t in [0,.25,.5,.75]])
        samples.append((sum(p[0]for p in poly)/len(poly),sum(p[1]for p in poly)/len(poly)))
        for x,y in samples:
            if region=='island':
                if not point_inside((x,y),inner):return False
            elif point_inside((x,y),outer):return False
            if border.find((x,y,0))[2]<bank_margin:return False
        return True
    def footprint(names):
        pts=[]
        for name in names:
            obj=s.objects.get(name)
            if obj and obj.type in {'MESH','CURVE','FONT'}and not obj.hide_render:
                T=I@obj.matrix_world
                for corner in obj.bound_box:
                    p=sphere.project(T@Vector(corner));pts.append(Vector((p.x,p.y)))
        return [list(pts[i])for i in convex_hull_2d(pts)]
    def declare(root):
        allowed[root.name]=['matrix_basis','matrix_world']
        for obj in root.children_recursive:allowed[obj.name]=['matrix_world']
    def move(name,x,y,sxy=1,sz=1):
        row=rows[name];obj=s.objects[name];declare(obj)
        old=Vector(row['ground_anchor']);oldF=sphere.frame(old.x,old.y);oldF.translation=old
        newF=sphere.frame(x,y,height=.03)
        delta=newF@Matrix.Diagonal((sxy,sxy,sz,1))@oldF.inverted()
        obj.matrix_world=D.matrix_world@delta@I@obj.matrix_world;bpy.context.view_layer.update()
        row['ground_anchor']=list(newF.translation);row['normal']=list(sphere.normal(x,y));row['radial_footprint_xy']=footprint(row['members'])
        return {'root':name,'source_anchor':list(old),'target_anchor':list(newF.translation),'scale_xy':sxy,'scale_z':sz,
                'members':[obj.name]+[o.name for o in obj.children_recursive],'footprint':row['radial_footprint_xy']}
    for name,x,y,sxy in [('SF_OPEN_TOWER',-6.4,24,1.3),('SF_STEP_TOWER',-3.5,22,1.25),('SF_TALLEST_TOWER',.1,22.8,1.35)]:
        rec=move(name,x,y,sxy,1.6);assert dry(rec['footprint'],'island',.05),('Hero outside island',name);heroes.append(rec)
    # Source SWFC/Jin Mao shared a footprint. Keep all support towers, moving
    # only two caught by the enlarged Shanghai Tower into rear island pockets.
    pending={'SF_HIGHRISE_8','SF_HIGHRISE_9'}
    obstacles=[{'id':r['id'],'poly':r['radial_footprint_xy'],'category':r['category']}for r in rows.values()if r['id']not in pending and len(r['radial_footprint_xy'])>2]
    def clear(poly,gap=.10):return not any(overlaps(poly,r['poly'],gap)for r in obstacles)
    for name in sorted(pending):
        row=rows[name];old=Vector(row['ground_anchor']);base=s.objects[name].matrix_world.copy();original=dict(row)
        candidates=survey['candidate_fill_samples_for_1m_by_0_8m_footprints']['island']
        candidates=sorted(candidates,key=lambda p:(p[1]<24,abs(p[0]-(-11 if name.endswith('8')else 4))+abs(p[1]-25)))
        placed=False
        for x,y in candidates:
            s.objects[name].matrix_world=base;row.update(original);bpy.context.view_layer.update()
            rec=move(name,x,y)
            if dry(rec['footprint'],'island',.10)and clear(rec['footprint'],.12):
                relocations.append(rec);obstacles.append({'id':name,'poly':rec['footprint'],'category':row['category']});placed=True;break
        assert placed,('No support-tower relocation slot',name)
    print('HEROES_AND_SUPPORTS_PLACED',flush=True)
    # Preserve the garden, bridge landing and port rear access instead of
    # filling every walkable square metre with architecture.
    protected=[boxpoly(-21.1,7.1,9.3,8.0),boxpoly(-16.8,14.9,6.8,5.3)]
    def viable(x,y,w,d,region,trees=False):
        poly=boxpoly(x,y,w,d)
        if region!='island'and(y-d/2<2.15 or x-w/2<-28.0 or x+w/2>21.0 or y+d/2>28):return False
        if not dry(poly,region,.14 if not trees else .08):return False
        if not trees and any(overlaps(poly,p,.08)for p in protected):return False
        if not clear(poly,.11 if not trees else .06):return False
        return poly
    def create_root(name,x,y,height=.04):
        root=bpy.data.objects.new(name,None);col.objects.link(root);root.parent=D;root.matrix_basis=sphere.frame(x,y,height=height)
        root['shd_anchor']=[x,y];return root
    def support(name,frame,w,d):
        top=[];bottom=[];corners=[Vector(p)for p in [(-w/2,-d/2,-.006),(w/2,-d/2,-.006),(w/2,d/2,-.006),(-w/2,d/2,-.006)]]
        for a,b in zip(corners,corners[1:]+corners[:1]):
            count=max(1,math.ceil((b-a).length/.25))
            for j in range(count):
                p=frame@a.lerp(b,j/count);top.append(p);bottom.append(sphere.project(p,-.025))
        n=len(top);me=bpy.data.meshes.new(name+'_Mesh')
        me.from_pydata(top+bottom,[],[tuple(range(n)),tuple(range(2*n-1,n-1,-1))]+[(i,n+i,n+(i+1)%n,(i+1)%n)for i in range(n)])
        me.materials.append(M['stone']);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
        obj=bpy.data.objects.new(name,me);col.objects.link(obj);obj.parent=D;obj['shd_role']='foundation';return obj.name
    for rec in heroes:
        # Exact edited-base footprint, supported by a sphere-following skirt.
        a=Vector(rec['target_anchor']);frame=sphere.frame(a.x,a.y);frame.translation=a
        obj=s.objects[rec['root']];coords=[]
        for child in [obj]+list(obj.children_recursive):
            if child.type=='MESH':coords.extend(frame.inverted()@I@child.matrix_world@Vector(p)for p in child.bound_box)
        w=max(p.x for p in coords)-min(p.x for p in coords);d=max(p.y for p in coords)-min(p.y for p in coords)
        rec['foundation']=support('SHD_'+rec['root']+'_SUPPORT',frame,w+.04,d+.04)
    def add(kind,x,y,w,d,h,region,variant):
        poly=viable(x,y,w+.06,d+.06,region)
        if not poly:return False
        name=f'SHD_{region.upper()}_{kind.upper()}_{len(sites):03d}';root=create_root(name+'_ROOT',x,y)
        objects=shanghai_assets.build(kind,name,root,col,M,w,d,h,variant)
        foundation=support(name+'_SUPPORT',root.matrix_basis,w+.04,d+.04)
        sites.append({'name':name,'root':root.name,'kind':kind,'region':region,'anchor':[x,y],'size':[w,d,h],
                      'objects':[o.name for o in objects],'foundation':foundation,'footprint':poly})
        obstacles.append({'id':name,'poly':poly,'category':'new_building'});return True
    # A low cultural pavilion reads in front of the enlarged modern skyline.
    for x,y in sorted(survey['candidate_fill_samples_for_1m_by_0_8m_footprints']['island'],key=lambda p:(p[0]-3.0)**2+(p[1]-20.0)**2):
        if add('cultural',x,y,2.5,1.35,1.45,'island',0):break
    # Irregular height and footprint cadence gives dense city blocks, with
    # substantially lower silhouettes around the three enlarged landmarks.
    for region,kind,w,d,spacing in [('island','tower',.95,.78,1.18),('bund','heritage',1.7,1.35,1.95),('oldtown','shikumen',1.28,1.02,1.53)]:
        xr,yr=((-13.7,7.0),(18.4,27.8))if region=='island'else((-27.4,-9.0),(2.7,24.5))if region=='bund'else((-9.4,20.0),(2.8,18.0))
        points=[];j=0;y=yr[0]
        while y<=yr[1]:
            x=xr[0]+(j%2)*spacing*.43
            while x<=xr[1]:points.append((x,y));x+=spacing
            y+=spacing*.82;j+=1
        if region=='island':points.sort(key=lambda p:-p[1])
        for index,(x,y)in enumerate(points):
            ww=w*random.uniform(.92,1.10);dd=d*random.uniform(.94,1.08)
            h=random.uniform(2.3,5.2)if region=='island'else random.uniform(2.2,3.8)if region=='bund'else random.uniform(1.25,1.95)
            add(kind,x,y,ww,dd,h,region,index)
    # Smaller buildings close selected narrow gaps while retaining alleys.
    for region,kind in [('island','tower'),('bund','heritage'),('oldtown','shikumen')]:
        candidates=survey['candidate_fill_samples_for_1m_by_0_8m_footprints'][region]
        for index,(x,y)in enumerate(candidates):
            w,d=(.66,.58)if region=='island'else(1.0,.85)if region=='bund'else(.88,.72)
            h=random.uniform(1.7,3.7)if region=='island'else random.uniform(1.8,2.8)if region=='bund'else random.uniform(1.0,1.5)
            add(kind,x,y,w,d,h,region,index+21)
    print('NEW_BUILDINGS',len(sites),flush=True)
    # Plant complete upright tree groups in remaining dry inter-building gaps.
    for j in range(43):
        y=2.7+j*.64
        for k in range(78):
            x=-27.3+k*.62+(j%2)*.27
            region='island'if point_inside((x,y),inner)else'oldtown'
            if not(-28<x<20.7 and 2.2<y<29.8):continue
            if x<-17 and y>23.5:continue
            radius=random.uniform(.20,.30);poly=viable(x,y,radius*2,radius*2,region,True)
            if not poly:continue
            name=f'SHD_GAP_TREE_{len(tree_sites):03d}';root=create_root(name+'_ROOT',x,y,.015)
            h=random.uniform(.65,1.15);b=citykit.Batch(name,root,col,M)
            b.rod('wood',(0,0,0),(0,0,h*.75),.025,6)
            for i in range(3):
                a=i*math.tau/3;cx=math.cos(a)*radius*.34;cy=math.sin(a)*radius*.34
                b.ellipsoid(['green','leaf_light','leaf_deep'][(i+len(tree_sites))%3],(cx,cy,h*.76),(radius*.66,radius*.66,h*.30),8,5)
            objects=b.finish();tree_sites.append({'root':root.name,'anchor':[x,y],'height':h,'radius':radius,'objects':[o.name for o in objects]})
            obstacles.append({'id':name,'poly':poly,'category':'new_tree'})
    # Keep planting in architectural gaps, not an evenly planted empty field
    # east of the title. Omit seven trees crossing the preserved garden paths.
    path_crossings={2,28,46,47,57,72,85}
    architecture=[r['radial_footprint_xy']for r in rows.values()if r['category']=='original_building_or_structure']+[r['footprint']for r in sites]
    def edge_distance(p,poly):
        if point_inside(p,poly):return 0.0
        best=1e9
        for a,b in zip(poly,poly[1:]+poly[:1]):
            dx,dy=b[0]-a[0],b[1]-a[1];den=dx*dx+dy*dy
            t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/den))if den else 0
            best=min(best,math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy))
        return best
    removed_trees=[];retained_trees=[]
    for tree in tree_sites:
        x,y=tree['anchor'];number=int(tree['root'].split('_')[3])
        empty_east_patch=x>5 and y>17 and not point_inside((x,y),inner) and min(edge_distance((x,y),p)for p in architecture)>1.6
        if number in path_crossings or empty_east_patch:
            root=s.objects[tree['root']]
            for obj in list(root.children_recursive)+[root]:bpy.data.objects.remove(obj,do_unlink=True)
            removed_trees.append({'root':tree['root'],'reason':'preserved garden path'if number in path_crossings else'outside building gaps'})
        else:retained_trees.append(tree)
    tree_sites=retained_trees
    print('NEW_TREES',len(tree_sites),'OMITTED',len(removed_trees),flush=True)
    s['shanghai_density_revision']='Reference-inspired dense modern skyline, Bund facades and Shikumen quarters; waterway and original animation unchanged.'
    s.frame_set(132)
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                v=area.spaces.active.region_3d;v.view_perspective='PERSP';v.view_location=D.matrix_world@Vector((-3,14,3));v.view_distance=68
                v.view_rotation=D.matrix_world.to_quaternion()@(Vector((-3,14,3))-Vector((27,-44,42))).to_track_quat('-Z','Y')
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
    report={'source':str(SOURCE),'source_sha256':SHA,'file':str(OUT),'sha256':digest(OUT),'allowed_original_changes':allowed,
            'hero_changes':heroes,'relocations':relocations,'sites':sites,'tree_sites':tree_sites,'removed_trees':removed_trees,'building_count':len(sites),'tree_count':len(tree_sites),
            'building_counts':{kind:sum(row['kind']==kind for row in sites)for kind in ['tower','heritage','shikumen','cultural']},
            'sphere':sphere.metadata(),'timeline':[0,989,30],'waterway_changed':False,'camera_changed':False,'status':'Pending visual and independent checks'}
    (ROOT/'delivery.json').write_text(json.dumps(report,indent=2),encoding='utf-8');(ROOT/'review/build.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    assert digest(SOURCE)==SHA
    print('SHANGHAI_DENSITY_SAVED',report['sha256'],flush=True)

if __name__=='__main__':main()
