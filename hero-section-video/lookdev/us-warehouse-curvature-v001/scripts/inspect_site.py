import bpy, json, math, collections
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
s=bpy.context.scene
print('saved-frame',s.frame_current,'camera',s.camera.name,'counts',len(s.objects))
s.frame_set(880)
U=s.objects['US_FRAME']; I=U.matrix_world.inverted(); C=Vector((0,0,-140))
def arc(p):
    q=p-C; r=q.length; a=math.atan2(math.hypot(q.x,q.y),q.z)*140; f=a/max(1e-9,math.hypot(q.x,q.y))
    return [round(q.x*f,3),round(q.y*f,3),round(r-140,4)]
def chain(o):
    seq=[]
    while o:seq.append(o.name);o=o.parent
    return seq
rows=[];hier=collections.Counter()
for o in s.objects:
    if o.type not in {'MESH','CURVE','FONT','EMPTY'}:continue
    m=I@o.matrix_world
    if o.type=='EMPTY':points=[m.translation]
    else:points=[m@Vector(v) for v in o.bound_box]
    center=sum(points,Vector())/len(points);x,y,h=arc(center)
    if not (15<x<116 and 9<y<68 and -8<h<60):continue
    path=chain(o)
    rows.append(dict(name=o.name,t=o.type,path=path,cen=[x,y,h],h=[min(arc(p)[2] for p in points),max(arc(p)[2] for p in points)],n=len(o.data.vertices) if o.type=='MESH' else 0,mod=[q.type for q in o.modifiers],anim=bool(o.animation_data),constraints=[q.type for q in o.constraints],hidden=o.hide_render))
    hier[path[-2] if len(path)>1 else path[0]]+=1
print('root counts',hier.most_common(60))
for n in ['CV_WH_US_FRAME','CV_WH_WORLD','E08_WAREHOUSE','WH_FLOOR','A03_TRACTOR','A03_TRAILER','A01_CONTAINER','W01_NEW_PALLET','W08_LAST_LOAD','CAM_MASTER','CAM_LOOK_TARGET','CV_CARRIER_WORLD','A04_PRIMARY','DOCK_TARGET','E10_OUTBOUND_YARD','DSP_WAREHOUSE_DETAIL_ROOT']:
    o=s.objects.get(n)
    if o:print(n,chain(o),o.type,'action',o.animation_data.action.name if o.animation_data and o.animation_data.action else None,'cons',[(q.type,getattr(getattr(q,'target',None),'name','')) for q in o.constraints],len(o.children))
(R/'site.json').write_text(json.dumps(rows))
