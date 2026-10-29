"""US tangent coordinates -> spherical landscape and locally graded logistics."""
import math
from mathutils import Vector,Matrix
RADIUS=140.0
CENTER=Vector((0,0,-RADIUS))
def smooth(x,a,b):
 t=max(0.,min(1.,(x-a)/(b-a)));return t*t*(3-2*t)
def surface(x,y,height=.68):
 r=math.hypot(x,y);a=r/RADIUS
 n=Vector((x/r*math.sin(a),y/r*math.sin(a),math.cos(a))) if r>1e-9 else Vector((0,0,1))
 return CENTER+n*(RADIUS+height)
def normal(x,y):return (surface(x,y,0)-CENTER).normalized()
def rigid_at(anchor,height=.8):
 anchor=Vector(anchor);q=Vector((0,0,1)).rotation_difference(normal(anchor.x,anchor.y))
 return Matrix.Translation(surface(anchor.x,anchor.y,height))@q.to_matrix().to_4x4()@Matrix.Translation(-anchor)
WAREHOUSE=rigid_at((52,32,.68),.8)
def graded(p):
 p=Vector(p);x,y,z=p
 w=smooth(x,18,29)*smooth(y,14,24)*(1-smooth(x,82,98))
 port=(1-smooth(x,16,29))*(1-smooth(y,14,24))
 return (WAREHOUSE@p)*w+p*port+surface(x,y,z+.12)*(1-w-port)
def road_frame(p):
 p=Vector(p);h=.02;ground=Vector((p.x,p.y,.735))
 dx=(graded(ground+Vector((h,0,0)))-graded(ground-Vector((h,0,0)))).normalized()
 dy=(graded(ground+Vector((0,h,0)))-graded(ground-Vector((0,h,0)))).normalized()
 n=dx.cross(dy).normalized();dy=n.cross(dx).normalized()
 basis=Matrix((dx,dy,n)).transposed().to_4x4()
 # Contact point is defined at road height; root origins can be below the tires.
 pos=graded(ground)+n*(p.z-.735)
 return Matrix.Translation(pos)@basis@Matrix.Translation(-p)
