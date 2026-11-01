"""Trace the supplied wordmark's seven alpha silhouettes in source pixels."""
from PIL import Image
from pathlib import Path
import json, math
R=Path(__file__).resolve().parents[1]
im=Image.open(R.parents[2]/'resources/logo/PNP-LINE.webp').convert('RGBA')
a=im.getchannel('A').point(lambda x:255 if x>=128 else 0)
p=a.load();edges={}
def edge(s,t):edges[s]=t
for y in range(1,im.height-1):
    for x in range(1,im.width-1):
        if not p[x,y]:continue
        if not p[x,y-1]:edge((x,y),(x+1,y))
        if not p[x+1,y]:edge((x+1,y),(x+1,y+1))
        if not p[x,y+1]:edge((x+1,y+1),(x,y+1))
        if not p[x-1,y]:edge((x,y+1),(x,y))
def reduce(points,tolerance=.77):
    x,y=points[0];u,v=points[-1];dx=u-x;dy=v-y
    denom=max(dx*dx+dy*dy,1e-9)
    best=0;cut=None
    for i,(px,py) in enumerate(points[1:-1],1):
        t=max(0,min(1,((px-x)*dx+(py-y)*dy)/denom))
        d=math.hypot(px-x-t*dx,py-y-t*dy)
        if d>best:cut=i;best=d
    if best<=tolerance:return [points[0],points[-1]]
    return reduce(points[:cut+1],tolerance)[:-1]+reduce(points[cut:],tolerance)
loops=[]
while edges:
    start=next(iter(edges));seq=[start];v=edges.pop(start)
    while v!=start:
        seq.append(v);v=edges.pop(v)
    amax=max(range(len(seq)),key=lambda i:(seq[i][0]-start[0])**2+(seq[i][1]-start[1])**2)
    loops.append(reduce(seq[:amax+1])[:-1]+reduce(seq[amax:]+[start])[:-1])
loops.sort(key=lambda a:min(x for x,y in a))
assert len(loops)==7
(R/'scripts/wordmark.json').write_text(json.dumps(loops,separators=(',',':')))
print([len(a) for a in loops],im.size)
