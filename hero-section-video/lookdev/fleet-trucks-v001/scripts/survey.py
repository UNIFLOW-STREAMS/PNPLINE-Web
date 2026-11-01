import bpy,json
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[1]
review=root/'review';review.mkdir(exist_ok=True)
s=bpy.context.scene;s.frame_set(617)
def row(o,ancestor):
    m=ancestor.matrix_world.inverted()@o.matrix_world
    pts=[m@Vector(p) for p in o.bound_box]
    bounds=[[round(fn(p[i] for p in pts),3) for i in range(3)] for fn in (min,max)]
    return dict(n=o.name,p=o.parent.name if o.parent else None,b=bounds,cen=[round(v,3) for v in m.translation],
                axes=[[round(z,3) for z in a] for a in m.to_3x3()],type=o.type,hide=o.hide_render,ad=bool(o.animation_data))
data={}
for n in ['A01_CONTAINER','A03_TRACTOR','A03_TRAILER','A04_PRIMARY','A05_SECONDARY']:
    o=s.objects[n];data[n]=[row(k,o) for k in sorted(o.children_recursive,key=lambda x:x.name)]
data['cranes']=[row(k,s.objects['US_FRAME']) for k in s.objects if ('CRANE' in k.name or k.name.startswith('P02_BOOM')) and ('CN' not in k.name and 'PORT_' not in k.name)]
for t in (48,375,450,520,617,800,880,912,940,989):
    s.frame_set(t)
    data[str(t)]={n:row(s.objects[n],s.objects['US_FRAME']) for n in ('A03_TRACTOR','A03_TRAILER','A04_PRIMARY','A05_SECONDARY','A01_CONTAINER')}
(review/'survey.json').write_text(json.dumps(data,indent=1))
for n in list(data)[:5]:
    print(n,len(data[n]))
    for r in data[n]: print(r['n'],r['p'],r['b'],r['hide'])
for r in data['cranes']:
    if 'LEG' not in r['n'] and 'STAY' not in r['n']: print(r['n'],r['p'],r['b'],r['hide'])
