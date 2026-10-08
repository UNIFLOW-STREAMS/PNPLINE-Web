"""Conservative per-mesh OBB SAT; wheel vertex hulls retain true radius."""
from mathutils import Vector
def overlap(a,aa,b,bb):
 centers=sum(a,Vector())/len(a)-sum(b,Vector())/len(b)
 axes=aa+bb+[x.cross(y) for x in aa for y in bb]+[centers];depth=float('inf')
 for axis in axes:
  if axis.length<1e-6:continue
  n=axis.normalized();av=[v.dot(n) for v in a];bv=[v.dot(n) for v in b];d=min(max(av),max(bv))-max(min(av),min(bv))
  if d<=0:return 0.
  depth=min(depth,d)
 return depth
def hull(o):
 matrix=o.matrix_world;axes=[matrix.to_3x3().col[i].normalized() for i in range(3)]
 return [matrix@v.co for v in o.data.vertices],axes
def point_distance(o,p):
 # Exact for the box meshes in this scene, conservative for wheel hulls.
 q=o.matrix_world.inverted()@p;lo=[min(v[i] for v in o.bound_box) for i in range(3)];hi=[max(v[i] for v in o.bound_box) for i in range(3)]
 return sum(max(lo[i]-q[i],0,q[i]-hi[i])**2 for i in range(3))**.5
