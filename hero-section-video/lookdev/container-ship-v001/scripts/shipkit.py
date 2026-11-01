import bpy,bmesh,math
from mathutils import Vector

def linear(v):
    v=int(v,16)/255
    return v/12.92 if v<.04045 else ((v+.055)/1.055)**2.4

def finish(name,hexcolor,rough=.4,metal=.0,coat=.0):
    c=[linear(hexcolor[i:i+2]) for i in (0,2,4)]+[1]
    m=bpy.data.materials.new('VSL • '+name);m.diffuse_color=c;m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    for k,v in [('Base Color',c),('Roughness',rough),('Metallic',metal),('Coat Weight',coat),('Coat Roughness',.27)]:p.inputs[k].default_value=v
    return m

class Parts:
    def __init__(self,name,parent,collection):
        self.name=name;self.parent=parent;self.col=collection
        self.v=[];self.f=[];self.ids=[];self.mats=[];self.smooth=[]
    def add(self,v,f,m,smooth=False):
        if m not in self.mats:self.mats.append(m)
        off=len(self.v);self.v.extend(tuple(p) for p in v)
        self.f.extend(tuple(off+i for i in face) for face in f)
        self.ids.extend([self.mats.index(m)]*len(f));self.smooth.extend([smooth]*len(f))
    def box(self,c,size,m):
        a=Vector(c);h=Vector(size)*.5
        self.add([a+Vector((x*h.x,y*h.y,z*h.z)) for x,y,z in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],m)
    def rod(self,a,b,r,m,n=10,r2=None):
        a,b=Vector(a),Vector(b);d=(b-a).normalized()
        u=d.cross(Vector((0,0,1)) if abs(d.z)<.95 else Vector((0,1,0))).normalized();v=d.cross(u)
        pts=[p+(u*math.cos(2*math.pi*i/n)+v*math.sin(2*math.pi*i/n))*radius for p,radius in [(a,r),(b,r if r2 is None else r2)] for i in range(n)]
        self.add(pts,[tuple(reversed(range(n))),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],m)
    def pipe(self,points,r,m,n=8):
        for a,b in zip(points,points[1:]):self.rod(a,b,r,m,n)
    def oval(self,c,scale,m,ns=24,bands=12):
        x,y,z=c;a,b,h=scale;vv=[(x,y,z-h)]
        for j in range(1,bands):
            lat=math.pi*j/bands-math.pi/2
            vv.extend((x+a*math.cos(lat)*math.cos(i*math.tau/ns),y+b*math.cos(lat)*math.sin(i*math.tau/ns),z+h*math.sin(lat)) for i in range(ns))
        vv.append((x,y,z+h));fs=[(0,1+(i+1)%ns,1+i) for i in range(ns)]
        for j in range(bands-2):
            k=1+j*ns;fs.extend((k+i,k+(i+1)%ns,k+ns+(i+1)%ns,k+ns+i) for i in range(ns))
        k=1+(bands-2)*ns;fs.extend((k+i,k+(i+1)%ns,len(vv)-1) for i in range(ns))
        self.add(vv,fs,m,True)
    def railing(self,points,height,mat,spacing=.39,r=.013):
        for a,b in zip(points,points[1:]):
            a,b=Vector(a),Vector(b);length=(b-a).length;count=max(1,math.ceil(length/spacing))
            for j in range(count):
                p=a.lerp(b,j/count);self.rod(p,p+Vector((0,0,height)),r,mat,7)
            for h in (height*.49,height):
                up=Vector((0,0,h));self.rod(a+up,b+up,r*(.74 if h<height else 1.1),mat,8)
        p=Vector(points[-1]);self.rod(p,p+Vector((0,0,height)),r,mat,7)
    def done(self,bevel=0):
        mesh=bpy.data.meshes.new(self.name);mesh.from_pydata(self.v,[],self.f)
        for m in self.mats:mesh.materials.append(m)
        for p,mi,sm in zip(mesh.polygons,self.ids,self.smooth):p.material_index=mi;p.use_smooth=sm
        mesh.update()
        ob=bpy.data.objects.new(self.name,mesh);self.col.objects.link(ob);ob.parent=self.parent
        if bevel:
            mod=ob.modifiers.new('Machined edge highlights','BEVEL');mod.width=bevel;mod.segments=2;mod.limit_method='ANGLE'
            norm=ob.modifiers.new('Face normals','WEIGHTED_NORMAL');norm.keep_sharp=True
        return ob
