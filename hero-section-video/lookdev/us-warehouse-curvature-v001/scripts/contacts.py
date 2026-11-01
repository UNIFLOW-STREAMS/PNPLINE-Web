"""Ray-test evaluated tire meshes against the visible driving surfaces."""
import sys,json,bpy,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];B=R.parents[1]/'blockout'
sys.path.insert(0,str(B/'us-title-curve-v001/scripts'))
from audit_preservation import minimize_scene
C=np.array([0,0,-140.])
def run(path):
    bpy.ops.wm.open_mainfile(filepath=str(path))
    s=bpy.context.scene;s.frame_set(0)
    w=s.objects;ui=w['US_FRAME'].matrix_world.inverted()
    verts=[];faces=[]
    for n in ('E07_INBOUND_ROAD','E09_MANEUVER_YARD','E10_OUTBOUND_YARD','DSP_ROAD_STEM','DSP_ROAD_BRANCH_-1','DSP_ROAD_BRANCH_1','US_YARD_ROAD'):
        o=w[n];offset=len(verts);m=ui@o.matrix_world;verts.extend(m@v.co for v in o.data.vertices)
        faces.extend(tuple(i+offset for i in f.vertices) for f in o.data.polygons)
    tree=BVHTree.FromPolygons(verts,faces)
    wheels=[o for n in ['A03_TRACTOR','A03_TRAILER','A04_PRIMARY','A05_SECONDARY'] for o in w[n].children if 'WHEEL' in o.name]
    raw={o.name:np.array([v.co[:] for v in o.data.vertices]) for o in wheels}
    minimize_scene(s,[o.name for o in wheels])
    result={}
    for f in list(range(560,990,2))+[989]:
        s.frame_set(f)
        for o in wheels:
            m=np.array(ui@o.matrix_world);p=raw[o.name]@m[:3,:3].T+m[:3,3]
            q=p-C;rad=np.linalg.norm(q,axis=1);i=np.argmin(rad)
            normal=q[i]/rad[i]
            loc,_,_,_=tree.ray_cast(Vector(p[i]+normal*4),Vector(-normal),8)
            if loc is not None:result[f,o.name]=rad[i]-np.linalg.norm(np.array(loc)-C)
    return result
old=run(R/'before.blend');new=run(R/'pnpline-us-warehouse-curvature-v001.blend')
match=sorted(set(old)&set(new))
report={}
for name in ('A03_TRACTOR','A03_TRAILER','A04_PRIMARY','A05_SECONDARY'):
    keys=[k for k in match if k[1].startswith(name)]
    a=np.array([old[k] for k in keys]);b=np.array([new[k] for k in keys]);i=np.argmax(abs(b))
    report[name]=dict(comparisons=len(keys),original_range=[a.min(),a.max()],result_range=[b.min(),b.max()],p95_abs=float(np.percentile(abs(b),95)),worst=keys[i],largest_deviation=float(max(abs(b-a))))
(R/'review/tire-contact.json').write_text(json.dumps(report,indent=2))
print(report)
