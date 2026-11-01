"""Read-only spatial inventory of accepted integrated scene in SF_CN_LAYOUT space."""
import bpy, json, math, hashlib
from pathlib import Path
from collections import defaultdict
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'review'; OUT.mkdir(exist_ok=True)
SOURCE=ROOT.parent/'cn-us-integrated-v001/pnpline-cn-us-integrated-v001.blend'
sha=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
assert sha=='1aee6c14eb4140614ffa650141eed3ada783c416397fbb938a5105a8df70a7d8'
if Path(bpy.data.filepath)!=SOURCE:bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
s=bpy.context.scene;s.frame_set(0)
layout=s.objects['SF_CN_LAYOUT'];I=layout.matrix_world.inverted()

def vlist(v):return [round(float(x),6)for x in v]
def bounds(points):
    return {'min':vlist(Vector(tuple(min(p[a]for p in points)for a in range(3)))),
            'max':vlist(Vector(tuple(max(p[a]for p in points)for a in range(3))))}
def chain(o):
    names=[]
    while o:names.append(o.name);o=o.parent
    return names
def localbounds(o):
    M=I@o.matrix_world
    pts=[M@v.co for v in o.data.vertices]if o.type=='MESH'else [M@Vector(v)for v in o.bound_box]
    return bounds(pts)
def merged(rows):
    return bounds([Vector(r[k])for r in rows for k in ('min','max')])if rows else None

inventory={};groups=defaultdict(list)
for o in s.objects:
    if o.type not in {'MESH','CURVE','FONT'}:continue
    lineage=chain(o)
    b=localbounds(o)
    if b['min'][2]<-70 or max(abs(b[k][a])for k in ('min','max')for a in (0,1))>140:continue
    if not any(n in lineage for n in ('CN_FRAME','SF_CN_LAYOUT','A02_SHIP','A01_CONTAINER','W01_NEW_PALLET','PORT_MODEL_ROOT')):continue
    row={'bounds':b,'type':o.type,'parent':o.parent.name if o.parent else None,'lineage':lineage,
         'hidden':o.hide_render or o.hide_viewport or o.hide_get()}
    inventory[o.name]=row
    if row['hidden']:group='hidden'
    elif o.name.startswith('SF_CHINA_'):group='title'
    elif any(x in lineage for x in ('A02_SHIP','A01_CONTAINER','W01_NEW_PALLET')):group='moving_payload'
    elif o.name.startswith('PORT_')or o.name=='CN_QUAY':group='terminal'
    elif any(x in o.name for x in ('LAND','COAST','ISLAND','BASIN')):group='terrain'
    else:group='existing_city'
    groups[group].append(b)

ocean=s.objects['EARTH_CONTINUOUS_OCEAN'];OM=I@ocean.matrix_world
verts=[OM@v.co for v in ocean.data.vertices]
water=BVHTree.FromPolygons(verts,[tuple(p.vertices)for p in ocean.data.polygons])
def height(x,y):
    hit,normal,face,dist=water.ray_cast(Vector((x,y,120)),Vector((0,0,-1)))
    return {'xy':[x,y],'z':round(hit.z,6)if hit else None,'normal':vlist(normal)if normal else None}
grid=[height(x,y)for y in range(-30,81,5)for x in range(-75,76,5)]
camera=s.camera
paths=[]
for f in sorted(set(range(0,990,3))|{0,48,72,104,156,165,180,200,216,230,240,250,252,253,272,300,336,360,989}):
    s.frame_set(f)
    row={'frame':f,'seconds':round(f/s.render.fps,6)}
    for label,name in [('camera',camera.name),('ship','A02_SHIP'),('cargo','A01_CONTAINER'),('pallet','W01_NEW_PALLET'),('look_target','CAM_LOOK_TARGET')]:
        obj=s.objects[name];M=I@obj.matrix_world
        row[label]={'position':vlist(M.translation),'matrix':[[float(v)for v in r]for r in M]}
    cm=I@camera.matrix_world
    row['camera']['forward']=vlist((cm.to_quaternion()@Vector((0,0,-1))).normalized())
    row['camera']['near_corners']=[vlist(cm@(v*(camera.data.clip_start/-v.z)))for v in camera.data.view_frame(scene=s)]
    row['ship']['hull_bounds']=localbounds(s.objects['SF_HULL_RED'])
    paths.append(row)
s.frame_set(0)
keynames=['SF_CN_LAYOUT','CN_FRAME','CN_LAND_TERRACE','SF_FRONT_LAND','SF_COAST_FOLDED_FACE','SF_ISLAND_TOP','SF_BASIN_WATER_SURFACE','CN_QUAY']
key={n:{'matrix':[[float(v)for v in r]for r in I@s.objects[n].matrix_world],
        'bounds':localbounds(s.objects[n])if s.objects[n].type=='MESH'else None}for n in keynames}
report={'source':str(SOURCE),'sha256':sha,'frame_range':[s.frame_start,s.frame_end],'fps':s.render.fps,
        'layout_world':[[float(v)for v in r]for r in layout.matrix_world],
        'ocean_origin_local':vlist(OM.translation),'ocean_native_radius_range':[min(v.co.length for v in ocean.data.vertices),max(v.co.length for v in ocean.data.vertices)],
        'group_bounds':{g:merged(rows)for g,rows in groups.items()},'key_objects':key,
        'objects':inventory,'water_height_grid':grid,'paths':paths}
(OUT/'spatial-survey.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('SURVEY SUMMARY '+json.dumps({k:report[k]for k in ('sha256','ocean_origin_local','ocean_native_radius_range','group_bounds','key_objects')},indent=2),flush=True)
print('PATH KEY '+json.dumps([r for r in paths if r['frame']in [0,48,104,156,165,200,216,240,252,253,272,300,336,360]]),flush=True)
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==sha
