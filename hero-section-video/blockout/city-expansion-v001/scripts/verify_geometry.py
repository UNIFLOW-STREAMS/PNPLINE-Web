"""Read-only geometric QA; --layout-only works without Blender or a built scene."""
import argparse,ast,json,math,sys
from pathlib import Path

R=Path(__file__).resolve().parents[1]

def source_layout():
    dense=R/'scripts/dense_layout.json'
    if dense.exists():return json.loads(dense.read_text())
    tree=ast.parse((R/'scripts/build.py').read_text(encoding='utf-8'));env={};buildings=[];roads=[]
    def value(n):
        if isinstance(n,ast.Name):return env[n.id]
        return ast.literal_eval(n)
    for n in tree.body:
        if isinstance(n,ast.Assign):
            try:v=value(n.value)
            except (ValueError,TypeError,KeyError):continue
            for target in n.targets:
                if isinstance(target,ast.Name):env[target.id]=v
        if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Name):
            call=n.value;fn=call.func.id
            if fn=='road':
                try:args=[value(a) for a in call.args]
                except (ValueError,TypeError,KeyError):continue
                roads.append({'name':args[0],'points':args[1],'width':args[2] if len(args)>2 else 3.3})
            if fn=='building':
                try:args=[value(a) for a in call.args];kw={k.arg:value(k.value) for k in call.keywords}
                except (ValueError,TypeError,KeyError):continue
                buildings.append({'name':args[0],'xy':args[1:3],'size':args[3:6],'yaw':kw.get('yaw',0),'landmark':kw.get('landmark')})
    skipped={'ny':set(),'sf':set()}
    for n in tree.body:
        if not isinstance(n,ast.For) or not isinstance(n.iter,ast.Call) or not n.iter.args or not isinstance(n.iter.args[0],ast.Name):continue
        key=n.iter.args[0].id
        if key not in skipped:continue
        for test in n.body:
            if not isinstance(test,ast.If) or not isinstance(test.test,ast.Compare) or not any(isinstance(q,ast.Continue) for q in test.body):continue
            try:
                compare=test.test;rhs=ast.literal_eval(compare.comparators[0])
                if isinstance(compare.ops[0],ast.Eq):skipped[key].add(rhs)
                elif isinstance(compare.ops[0],ast.In):skipped[key].update(rhs)
            except (ValueError,TypeError):pass
    for prefix,rows,yaw in [('NY',env['ny'],-.25),('SF',env['sf'],.12)]:
        buildings.extend({'name':f'CE_{prefix}_BLOCK_{i:02}','xy':[x,y],'size':[w,d,h],'yaw':yaw,'landmark':None} for i,(x,y,w,d,h) in enumerate(rows) if i not in skipped[prefix.lower()])
    placement_file=R/'scripts/placements.json'
    if placement_file.exists():
        placements=json.loads(placement_file.read_text())
        for b in buildings:b['xy']=placements.get(b['name'],b['xy'])
    return {'buildings':buildings,'roads':roads,'terrain_polygons':{'left':env['LEFT'],'right':env['RIGHT']},'bridge_endpoints':env['bridge_points'],'bridge_width':3.8}

def rect(x,y,w,d,yaw=0):
    c,s=math.cos(yaw),math.sin(yaw)
    return [(x+a*c-b*s,y+a*s+b*c) for a,b in [(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)]]

def segment_rect(a,b,width):
    dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
    return rect((a[0]+b[0])/2,(a[1]+b[1])/2,length,width,math.atan2(dy,dx))

def overlap(a,b):
    depth=float('inf')
    for p in [a,b]:
        for u,v in zip(p,p[1:]+p[:1]):
            nx,ny=-(v[1]-u[1]),v[0]-u[0];length=math.hypot(nx,ny)
            if length<1e-12:continue
            nx/=length;ny/=length
            ap=[x*nx+y*ny for x,y in a];bp=[x*nx+y*ny for x,y in b]
            d=min(max(ap),max(bp))-max(min(ap),min(bp))
            if d<=0:return 0
            depth=min(depth,d)
    return depth

def inside(p,poly):
    x,y=p;found=False
    for (ax,ay),(bx,by) in zip(poly,poly[1:]+poly[:1]):
        if (ay>y)!=(by>y) and x<(bx-ax)*(y-ay)/(by-ay)+ax:found=not found
    return found

def polygon_distance(a,b):
    if overlap(a,b)>0:return 0.0
    def distance(p,u,v):
        dx,dy=v[0]-u[0],v[1]-u[1];l2=dx*dx+dy*dy
        t=max(0,min(1,((p[0]-u[0])*dx+(p[1]-u[1])*dy)/l2)) if l2 else 0
        return math.hypot(p[0]-u[0]-t*dx,p[1]-u[1]-t*dy)
    return min(distance(p,u,v) for left,right in [(a,b),(b,a)] for p in left for u,v in zip(right,right[1:]+right[:1]))

def layout_report(data):
    bb=[(b,rect(*b['xy'],b['size'][0]+.44,b['size'][1]+.44,b['yaw'])) for b in data['buildings']]
    neighbor=[];road_hits=[];protected_hits=[];outside=[];road_outside=[];clearances=[];park_hits=[];source_hits=[];allowed_outside=[]
    min_clearance=data.get('minimum_building_clearance',0)
    mainland=[(-35.896,18.6),(-23,5),(111,5),(111,56),(-9.438,75.735),(-23,56),(-35.896,29.4)]
    polys=[mainland]+list(data['terrain_polygons'].values())
    for i,(a,ap) in enumerate(bb):
        for b,bp in bb[i+1:]:
            dep=overlap(ap,bp)
            if dep>.10:neighbor.append({'a':a['name'],'b':b['name'],'penetration':round(dep,3)})
            gap=polygon_distance(ap,bp)
            if min_clearance and gap<min_clearance-.001:clearances.append({'a':a['name'],'b':b['name'],'type':'neighbor','gap':round(gap,4)})
        for road in data['roads']:
            roadpoly=[segment_rect(x,y,road['width']+road.get('sidewalk_extra',data.get('sidewalk_extra',1.35))) for x,y in zip(road['points'],road['points'][1:])]
            dep=max(overlap(ap,q) for q in roadpoly)
            if dep>.10:road_hits.append({'building':a['name'],'road':road['name'],'penetration':round(dep,3)})
            gap=min(polygon_distance(ap,q) for q in roadpoly)
            if min_clearance and gap<min_clearance-.001:clearances.append({'a':a['name'],'b':road['name'],'type':'road','gap':round(gap,4)})
        for name,poly in [('warehouse',rect(55.5,31.15,53,16.5)),('port',rect(0,8.2,34.4,8.4)),('inbound_maneuver',rect(27,29.5,24,7)),('inbound_turn',rect(33,19,14,22)),('outbound',rect(90,29,42,28))]:
            dep=overlap(ap,poly)
            if dep>.10:protected_hits.append({'building':a['name'],'protected':name,'penetration':round(dep,3)})
        bad=[list(p) for p in ap if not any(inside(p,poly) for poly in polys)]
        if bad:outside.append({'building':a['name'],'corners':bad})
        for source in data.get('protected_source_foundations',[]):
            dep=overlap(ap,source['poly'])
            if dep>.01:source_hits.append({'building':a['name'],'source':source['name'],'penetration':round(dep,4)})
        if not a.get('landmark'):
            for park in data.get('reserved_plazas',[]):
                dep=overlap(ap,park['poly'])
                if dep>.01:park_hits.append({'building':a['name'],'park':park['name'],'penetration':round(dep,4)})
            relocated={r['name'] for r in data.get('relocated_existing_buildings',[])}
            region=a.get('district') or ('CHI' if a['name'].startswith('CE_CHI_') or a['name'] in relocated else ('NY' if a['xy'][1]>0 else 'SF'))
            allowed=data.get('allowed_building_regions',{}).get(region)
            if allowed and any(not inside(p,allowed) for p in ap):allowed_outside.append(a['name'])
    for road in data['roads']:
        bad=[]
        for a,b in zip(road['points'],road['points'][1:]):
            bad.extend(list(p) for p in segment_rect(a,b,road['width']+road.get('sidewalk_extra',data.get('sidewalk_extra',1.35))) if not any(inside(p,poly) for poly in polys))
        if bad:road_outside.append({'road':road['name'],'corners':bad})
    return {'neighbor_overlaps':neighbor,'road_overlaps':road_hits,'protected_overlaps':protected_hits,'outside_land':outside,'road_outside_land':road_outside,'clearance_violations':clearances,'park_overlaps':park_hits,'source_foundation_overlaps':source_hits,'outside_allowed_district':allowed_outside,'overlap_threshold':.10,'footprint_includes_foundation_margin':.22,'minimum_clearance':min_clearance}

def scene_report(data):
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    sys.path.insert(0,str(R.parent/'curvature-rework-v001/scripts'))
    from mapping import surface,normal,CENTER
    s=bpy.context.scene;ui=s.objects['US_FRAME'].matrix_world.inverted();terrain=[];frames=[]
    for o in s.objects:
        if o.get('ce_role')=='curved_terrain':
            n=o['ce_top_vertices'];h=o['ce_height'];m=ui@o.matrix_world
            errors=[abs(((m@v.co)-CENTER).length-(140+h)) for v in o.data.vertices[:n]]
            terrain.append({'name':o.name,'top_vertices':n,'target_radius':140+h,'max_error':max(errors),'passed':max(errors)<=1e-4})
        if o.get('ce_role')=='building_root':
            m=ui@o.matrix_world;x,y,z=o['ce_anchor'];up=(m.to_3x3()@Vector((0,0,1))).normalized();dot=up.dot(normal(x,y));err=(m.translation-surface(x,y,z)).length
            frames.append({'name':o.name,'normal_dot':dot,'position_error':err,'passed':dot>1-1e-6 and err<1e-4})
    bridge=s.objects['CE_BRIDGE_DECK'];m=ui@bridge.matrix_world;endpoints=[]
    for i,p in enumerate(data['bridge_endpoints']):
        pair=list(bridge.data.vertices[:2] if i==0 else bridge.data.vertices[-2:]);x,y=p
        expected=[surface(x+sign*data['bridge_width']/2,y,.88) for sign in [-1,1]]
        errors=[(m@v.co-q).length for v,q in zip(pair,expected)]
        center=(m@pair[0].co+m@pair[1].co)/2
        roadname='E07_INBOUND_ROAD' if i==0 else 'CE_SF_BRIDGE_BOULEVARD_ASPHALT';road=s.objects[roadname];rm=ui@road.matrix_world
        bvh=BVHTree.FromPolygons([rm@v.co for v in road.data.vertices],[tuple(f.vertices) for f in road.data.polygons])
        hit=bvh.find_nearest(center);gap=hit[3] if hit else None
        endpoints.append({'xy':p,'vertex_mapping_error':max(errors),'road':roadname,'road_surface_gap':gap,'passed':max(errors)<1e-4 and gap is not None and gap<.13})
    return {'terrain':terrain,'building_frames':frames,'bridge_contacts':endpoints,'passed':all(r['passed'] for r in terrain+frames+endpoints)}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--layout-only',action='store_true');parser.add_argument('--output')
    argv=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ([] if '--python' in sys.argv else sys.argv[1:])
    args=parser.parse_args(argv)
    manifest=R/'review/build.json';data=source_layout() if args.layout_only or not manifest.exists() else json.loads(manifest.read_text())
    if not args.layout_only and any('_DENSE_' in b['name'] for b in data['buildings']):
        metadata=json.loads((R/'scripts/dense_layout.json').read_text());metadata.update(data);data=metadata
    report={'layout':layout_report(data)}
    if not args.layout_only:report['scene']=scene_report(data)
    report['passed']=not any(report['layout'][k] for k in ['neighbor_overlaps','road_overlaps','protected_overlaps','outside_land','road_outside_land','clearance_violations','park_overlaps','source_foundation_overlaps','outside_allowed_district']) and report.get('scene',{}).get('passed',True)
    path=Path(args.output) if args.output else R/'review'/('layout-geometry.json' if args.layout_only else 'geometry.json');path.write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
    if not report['passed']:sys.exit(1)

if __name__=='__main__':main()
