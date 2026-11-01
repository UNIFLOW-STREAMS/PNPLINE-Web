"""Editable, material-batched miniature architecture and street details."""
import math
from mathutils import Vector, Matrix
import bpy

class Batch:
    def __init__(self, name, parent, collection, materials):
        self.name, self.parent, self.collection, self.materials = name,parent,collection,materials
        self.parts = {}
    def add(self, mat, vertices, faces):
        vs,fs = self.parts.setdefault(mat,([],[])); n=len(vs)
        vs.extend(tuple(v) for v in vertices);fs.extend(tuple(n+i for i in f) for f in faces)
    def box(self, mat, p, size, T=None):
        p=Vector(p);h=Vector(size)*.5
        v=[p+Vector((x*h.x,y*h.y,z*h.z)) for x,y,z in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
        if T is not None:v=[T@q for q in v]
        self.add(mat,v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
    def rod(self,mat,a,b,r=.035,n=6):
        a,b=Vector(a),Vector(b);z=(b-a).normalized();x=z.cross(Vector((0,0,1)))
        if x.length<.01:x=z.cross(Vector((0,1,0)))
        x.normalize();y=z.cross(x)
        v=[p+r*(x*math.cos(i*math.tau/n)+y*math.sin(i*math.tau/n)) for p in [a,b]for i in range(n)]
        self.add(mat,v,[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)])
    def ellipsoid(self,mat,p,r,n=10,m=6,up=None):
        rotation=Vector((0,0,1)).rotation_difference(Vector(up).normalized()).to_matrix() if up is not None else Matrix.Identity(3)
        v=[Vector(p)+rotation@Vector((r[0]*math.sin(j*math.pi/m)*math.cos(i*math.tau/n),r[1]*math.sin(j*math.pi/m)*math.sin(i*math.tau/n),r[2]*math.cos(j*math.pi/m)))for j in range(m+1)for i in range(n)]
        self.add(mat,v,[(j*n+i,(j+1)*n+i,(j+1)*n+(i+1)%n,j*n+(i+1)%n)for j in range(m)for i in range(n)])
    def finish(self):
        result=[]
        for mat,(v,f) in self.parts.items():
            me=bpy.data.meshes.new(self.name+'_'+mat+'_Mesh');me.from_pydata(v,[],f);me.materials.append(self.materials[mat]);me.update()
            o=bpy.data.objects.new(self.name+'_'+mat,me);self.collection.objects.link(o);o.parent=self.parent
            o['cnx_owner']='cn-city-expansion-v001';result.append(o)
        return result

def roof(b,x,y,z,w,d,h,mat='roof'):
    # Four layered curved hip slopes with lifted corners and a long ridge.
    rings=[]
    for t,zf in [(0,.16),(.28,.27),(.62,.63),(1,1)]:
        hx=w*.58*(1-.58*t);hy=d*.60*(1-.97*t)
        rings.append([(x-hx,y-hy,z+h*zf),(x+hx,y-hy,z+h*zf),(x+hx,y+hy,z+h*zf),(x-hx,y+hy,z+h*zf)])
    for a,c in zip(rings,rings[1:]):b.add(mat,a+c,[(i,(i+1)%4,(i+1)%4+4,i+4)for i in range(4)])
    b.add(mat,rings[-1],[(0,1,2,3)])
    for a,c in zip(rings[0],rings[0][1:]+rings[0][:1]):b.rod('dark',a,c,.045)
    b.rod('stone',(x-w*.25,y,z+h*1.02),(x+w*.25,y,z+h*1.02),.045)
    for xx in [-1,1]:
        for yy in [-1,1]:
            p=Vector((x+xx*w*.58,y+yy*d*.60,z+h*.16))
            b.rod(mat,p,p+Vector((xx*.12,yy*.12,.16)),.045)
    for i in range(max(5,int(w/.18))):
        xx=-w*.48+w*.96*i/max(1,int(w/.18)-1)
        for sy in [-1,1]:
            a=(x+xx*.48,y,z+h);c=(x+xx,y+sy*d*.59,z+h*.17)
            b.rod(mat,a,c,.017,4)

def house(b,x,y,w,d,h,body='stone',roofmat='roof'):
    b.box(body,(x,y,h*.5),(w,d,h));b.box('dark',(x,y-d*.505,h*.48),(w*.72,.025,h*.72))
    for xx in [-.35,0,.35]:
        b.box('wood',(x+w*xx,y-d*.523,h*.48),(.045,.05,h*.78))
    b.box('stone',(x,y-d*.55,.09),(w*1.06,.22,.18))
    roof(b,x,y,h,w,d,min(.75,w*.27),roofmat)

def courtyard(name,parent,collection,M,w,d,h,variant=0):
    b=Batch(name,parent,collection,M)
    b.box('paving',(0,0,.035),(w,d,.07))
    house(b,0,d*.30,w*.9,d*.3,h,'ivory' if variant%3==0 else 'stone')
    house(b,-w*.37,-d*.02,w*.23,d*.5,h*.76)
    house(b,w*.37,-d*.02,w*.23,d*.5,h*.76)
    house(b,0,-d*.39,w*.55,d*.2,h*.66,'red' if variant%4==0 else 'stone')
    b.box('green',(0,0,.075),(w*.19,d*.24,.08))
    b.rod('wood',(.12,.08,.08),(.12,.08,h*.62),.035)
    b.ellipsoid('green',(.12,.08,h*.7),(.32,.32,.38))
    return b.finish()

def block(name,parent,collection,M,w,d,h,variant=0):
    b=Batch(name,parent,collection,M)
    body=['ivory','stone','ivory','red','glass','dark_glass'][variant%6]
    floor=max(3,round(h/.55));dz=h/floor
    for j in range(floor):
        taper=(.79 if j>floor*.65 else 1) if variant%4==0 else (.88 if j>floor*.82 else 1) if variant%4==1 else 1
        ww,dd=w*taper,d*taper
        z=(j+.5)*dz
        b.box(body,(0,0,z),(ww,dd,dz))
        for side in [-1,1]:
            for i in range(max(2,round(w/.42))):
                n=max(2,round(w/.42));x=-ww*.42+(i+.5)*ww*.84/n
                b.box('dark_glass',(x,side*(dd*.5+.012),z),(ww*.62/n,.025,dz*.62))
            for i in range(max(2,round(d/.46))):
                n=max(2,round(d/.46));y=-dd*.42+(i+.5)*dd*.84/n
                b.box('dark_glass',(side*(ww*.5+.012),y,z),(.025,dd*.62/n,dz*.62))
        if variant%3!=1 or j%2==0:
            b.box('white',(0,0,(j+1)*dz-.035),(ww*1.025,dd*1.025,.045))
        for x in [-ww*.5,ww*.5]:
            for y in [-dd*.5,dd*.5]:b.box('stone',(x,y,z),(.07,.07,dz+.025))
    b.box('roof',(0,0,h+.035),(ww*1.04,dd*1.04,.09))
    for sy in [-1,1]:b.box('stone',(0,sy*dd*.5,h+.14),(ww*1.05,.08,.23))
    for sx in [-1,1]:b.box('stone',(sx*ww*.5,0,h+.14),(.08,dd,.23))
    b.box('metal',(-w*.18,d*.12,h+.28),(w*.33,d*.29,.4))
    b.box('dark',(0,-d*.511,.27),(w*.24,.04,.54))
    b.box('stone',(0,-d*.6,.6),(w*.37,.3,.06))
    return b.finish()
