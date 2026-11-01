"""Editable Beijing miniature landmarks, batched by material.

build(kind, name, parent, collection, materials, width, depth, height) returns
the created mesh objects. Local ground is z=0, centre is xy=0 and front is -Y.
All modelling is procedural mesh construction; no operators or source edits.
"""
import json
import math

import bpy
from mathutils import Vector

TAU = math.tau


def _variant(name, color, metallic=0.0, roughness=.45):
    name = 'BJ_' + name
    material = bpy.data.materials.get(name)
    if material is None:
        material = bpy.data.materials.new(name)
        material.diffuse_color = (*color, 1)
        material.use_nodes = True
        bsdf = material.node_tree.nodes.get('Principled BSDF')
        bsdf.inputs['Base Color'].default_value = (*color, 1)
        bsdf.inputs['Metallic'].default_value = metallic
        bsdf.inputs['Roughness'].default_value = roughness
    return material


class _Mesh:
    def __init__(self):
        self.vertices = []
        self.faces = []
        self.smooth = []

    def add(self, vertices, faces, smooth=False):
        start = len(self.vertices)
        self.vertices.extend(tuple(p) for p in vertices)
        self.faces.extend(tuple(start+i for i in f) for f in faces)
        self.smooth.extend([smooth]*len(faces))


class _Builder:
    def __init__(self, name, parent, collection, materials, size):
        self.name, self.parent, self.collection = name, parent, collection
        self.materials, self.size = dict(materials), size
        self.batches = {}
        self.materials.update({
            'bj_lattice': _variant('Silver_Lattice', (.59, .64, .68), .48, .35),
            'bj_mullion': _variant('Deep_Blue_Mullion', (.075, .16, .20), .38, .38),
            'bj_cctv_glass': _variant('CCTV_Silver_Blue_Glass', (.43, .54, .60), .43, .30),
            'bj_cctv_shadow': _variant('CCTV_Deep_Blue_Glass', (.27, .38, .45), .40, .32),
            'bj_blue': _variant('Temple_Glazed_Cobalt', (.018, .12, .29), .22, .31),
            'bj_blue_edge': _variant('Temple_Ceramic_Ridges', (.045, .24, .44), .28, .31),
            'bj_red': _variant('Imperial_Vermilion', (.47, .038, .026), .06, .49),
            'bj_gold': _variant('Palace_Glazed_Ochre', (.83, .43, .075), .18, .34),
            'bj_gold_edge': _variant('Palace_Ridge_Gold', (.98, .64, .19), .30, .32),
            'bj_marble': _variant('Warm_Marble', (.77, .76, .68), .03, .65),
            'bj_brick': _variant('Wall_Grey_Brick', (.38, .39, .37), .02, .8),
            'bj_mortar': _variant('Wall_Mortar', (.54, .53, .47), .0, .85),
            'bj_stadium': _variant('Stadium_Inner_Red', (.30, .045, .033), .08, .64),
        })

    def mesh(self, key):
        return self.batches.setdefault(key, _Mesh())

    def add(self, key, verts, faces, smooth=False):
        self.mesh(key).add(verts, faces, smooth)

    def box(self, key, center, size, angle=0):
        cx,cy,cz = center
        dx,dy,dz = [v/2 for v in size]
        co,si = math.cos(angle),math.sin(angle)
        verts=[(cx+x*co-y*si,cy+x*si+y*co,cz+z)
               for x,y,z in [(-dx,-dy,-dz),(dx,-dy,-dz),(dx,dy,-dz),(-dx,dy,-dz),
                             (-dx,-dy,dz),(dx,-dy,dz),(dx,dy,dz),(-dx,dy,dz)]]
        self.add(key,verts,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])

    def beam(self, key, a, b, width, depth=None):
        a,b=Vector(a),Vector(b)
        axis=b-a
        if axis.length < 1e-8:
            return
        axis.normalize()
        ref=Vector((0,0,1)) if abs(axis.z)<.95 else Vector((0,1,0))
        u=axis.cross(ref).normalized()*width/2
        v=axis.cross(u).normalized()*(depth if depth is not None else width)/2
        verts=[p+u*s+v*t for p in (a,b) for s,t in [(-1,-1),(1,-1),(1,1),(-1,1)]]
        self.add(key,verts,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])

    def chain(self, key, points, width, depth=None, closed=False):
        if closed:
            points=list(points)+[points[0]]
        for a,b in zip(points,points[1:]):
            self.beam(key,a,b,width,depth)

    def cylinder(self, key, center, radius, height, n=48, radius_top=None):
        x,y,z=center
        r2=radius if radius_top is None else radius_top
        verts=[(x+r*math.cos(TAU*i/n),y+r*math.sin(TAU*i/n),zz)
               for r,zz in [(radius,z-height/2),(r2,z+height/2)] for i in range(n)]
        self.add(key,verts,[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],True)
        self.add(key,verts,[tuple(reversed(range(n))),tuple(range(n,2*n))])

    def ring(self, key, radius, z, thickness=.008, ry=None, n=72, center=(0,0)):
        ry=radius if ry is None else ry
        points=[(center[0]+radius*math.cos(TAU*i/n),center[1]+ry*math.sin(TAU*i/n),z) for i in range(n)]
        self.chain(key,points,thickness,closed=True)

    def lathe(self, key, profile, n=72, center=(0,0), smooth=True):
        verts=[(center[0]+r*math.cos(TAU*i/n),center[1]+r*math.sin(TAU*i/n),z)
               for r,z in profile for i in range(n)]
        faces=[]
        for j in range(len(profile)-1):
            for i in range(n):
                k=(i+1)%n
                faces.append((j*n+i,j*n+k,(j+1)*n+k,(j+1)*n+i))
        self.add(key,verts,faces,smooth)

    def finish(self, kind):
        objects=[]
        for key,batch in self.batches.items():
            if not batch.faces:
                continue
            mesh=bpy.data.meshes.new(self.name+'_'+key+'_Mesh')
            mesh.from_pydata([(p[0]*self.size[0],p[1]*self.size[1],p[2]*self.size[2]) for p in batch.vertices],[],batch.faces)
            mesh.update()
            for polygon,smooth in zip(mesh.polygons,batch.smooth):
                polygon.use_smooth=smooth
            obj=bpy.data.objects.new(self.name+'_'+key,mesh)
            self.collection.objects.link(obj)
            obj.parent=self.parent
            obj['landmark_kind']=kind
            obj['landmark_batch_material']=key
            obj['front_direction']='local -Y'
            material=self.materials.get(key) or self.materials.get('stone')
            if material:
                mesh.materials.append(material)
            objects.append(obj)
        return objects


def _skew_prism(b, key, bottom, top, wx, wy):
    bottom,top=Vector(bottom),Vector(top)
    corners=[Vector((-wx/2,-wy/2,0)),Vector((wx/2,-wy/2,0)),Vector((wx/2,wy/2,0)),Vector((-wx/2,wy/2,0))]
    verts=[p+c for p in (bottom,top) for c in corners]
    b.add(key,verts,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
    return verts


def _diamond_facade(b, verts, levels=17, columns=4, thickness=.0025):
    """Cross-bracing lies directly on each planar skew tower face."""
    for face in [(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:
        p0,p1,p2,p3=[Vector(verts[i]) for i in face]
        normal=(p1-p0).cross(p3-p0).normalized()*.0008
        at=lambda u,v:p0.lerp(p1,u).lerp(p3.lerp(p2,u),v)+normal
        for row in range(levels):
            v0,v1=row/levels,(row+1)/levels
            for col in range(columns):
                u0,u1=col/columns,(col+1)/columns
                b.beam('bj_mullion',at(u0,v0),at(u1,v1),thickness)
                b.beam('bj_mullion',at(u1,v0),at(u0,v1),thickness)
        for v in [i/(levels*2) for i in range(levels*2+1)]:
            b.beam('metal',at(0,v),at(1,v),thickness*.42)
    for i in range(4):
        b.beam('bj_lattice',verts[i],verts[i+4],thickness*2.2)


def _cctv(b):
    b.box('paving',(0,0,.018),(.97,.77,.036))
    # Two differently inclined towers and the cantilever form a true open loop.
    left=_skew_prism(b,'bj_cctv_glass',(-.32,-.10,.036),(-.18,-.04,.94),.25,.32)
    right=_skew_prism(b,'bj_cctv_shadow',(.31,.12,.036),(.20,.07,.82),.25,.32)
    _diamond_facade(b,left,18,4)
    _diamond_facade(b,right,16,4)
    # Folded bridge: upper and lower edges slope together, preserving the void.
    xa,xb=-.305,.325
    ya,yb=-.20,.23
    verts=[(xa,ya,.72),(xb,ya,.65),(xb,yb,.65),(xa,yb,.72),
           (xa,ya,.96),(xb,ya,.84),(xb,yb,.84),(xa,yb,.96)]
    b.add('bj_cctv_glass',verts,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
    _diamond_facade(b,verts,4,10,.0025)
    for z in [.018,.039]:
        b.box('ivory',(0,-.30,z),(.67,.12,.016))
    # Low connecting podium remains well below the large negative space.
    b.box('dark_glass',(0,.19,.085),(.48,.26,.10))
    b.box('stone',(0,.19,.142),(.49,.27,.014))
    for x in [-.16,-.07,.04,.13]:
        b.cylinder('metal',(x,.19,.161),.027,.026,16)
    for x in [-.10,0,.10]:
        b.box('dark_glass',(x,-.116,.052),(.065,.006,.035))
    b.box('metal',(-.21,-.02,.975),(.12,.12,.03))
    b.cylinder('dark',(-.21,-.02,.994),.044,.007,32)


def _zun_radius(t):
    # Vessel-like flared foot/crown and a long, visibly pinched middle.
    return .355+.105*(abs(2*t-1)**1.65)+.018*math.exp(-((t-.96)/.08)**2)


def _square_ring(radius,z,n=64):
    points=[]
    for i in range(n):
        theta=TAU*i/n
        co,si=math.cos(theta),math.sin(theta)
        points.append((radius*math.copysign(abs(co)**.53,co),radius*math.copysign(abs(si)**.53,si),z))
    return points


def _zun(b):
    b.box('paving',(0,0,.008),(.99,.99,.016))
    profiles=[(_zun_radius(i/80),.022+.948*i/80) for i in range(81)]
    verts=[p for r,z in profiles for p in _square_ring(r,z)]
    b.add('glass',verts,[(j*64+i,j*64+(i+1)%64,(j+1)*64+(i+1)%64,(j+1)*64+i) for j in range(80) for i in range(64)],True)
    for j,(r,z) in enumerate(profiles):
        b.chain('metal' if j%8 else 'ivory',_square_ring(r+.0015,z),.0016 if j%8 else .0032,closed=True)
    for i in range(64):
        points=[_square_ring(r+.002,z)[i] for r,z in profiles]
        b.chain('bj_lattice' if i%4==0 else 'bj_mullion',points,.0028 if i%4==0 else .0016)
    # Crown has an open rim and recessed service roof, as in the concept.
    outer=_square_ring(_zun_radius(1),.97)
    inner=_square_ring(_zun_radius(1)-.042,.97)
    b.add('ivory',outer+inner,[(i,(i+1)%64,(i+1)%64+64,i+64) for i in range(64)])
    b.chain('metal',outer,.008,closed=True)
    b.box('dark',(0,0,.942),(.60,.60,.009))
    b.box('metal',(0,0,.954),(.17,.13,.018))
    for x in [-.30,.30]:
        b.box('dark_glass',(x,-.45,.045),(.15,.02,.055))
    for x in [-.12,-.04,.04,.12]:
        b.beam('ivory',(x,-.468,.022),(x,-.455,.10),.004)


def _stadium_point(theta,z):
    radius=.445+.045*math.sin(math.pi*min(1,max(0,z)))
    return (radius*math.cos(theta),radius*.80*math.sin(theta),.12+.78*z)


def _stadium(b):
    b.box('paving',(0,0,.012),(.995,.91,.024))
    # A stepped elliptical bowl is visible through the roof opening.
    n=96
    for j in range(12):
        r0=.24+j*.0122
        r1=r0+.0125
        z=.10+j*.038
        profile=[(r0,z),(r1,z),(r1,z+.028)]
        verts=[(r*math.cos(TAU*i/n),r*.76*math.sin(TAU*i/n),zz) for r,zz in profile for i in range(n)]
        b.add('bj_stadium' if j%3 else 'stone',verts,[(a*n+i,(a+1)*n+i,(a+1)*n+(i+1)%n,a*n+(i+1)%n) for a in range(2) for i in range(n)])
    b.box('green',(0,0,.101),(.365,.215,.012))
    for a,c in [((-.17,-.095,.109),(.17,-.095,.109)),((-.17,.095,.109),(.17,.095,.109)),
                ((-.17,-.095,.109),(-.17,.095,.109)),((.17,-.095,.109),(.17,.095,.109)),((0,-.095,.109),(0,.095,.109))]:
        b.beam('white',a,c,.002)
    b.ring('white',.035,.110,.0018,ry=.028,n=40)
    # Dark recessed envelope, ventilated exterior and independent silver weave.
    rings=[]
    for z in [0,.35,.72,1]:
        rings.extend(_stadium_point(TAU*i/n,z) for i in range(n))
    b.add('dark_glass',rings,[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(3) for i in range(n)],True)
    for i in range(64):
        t=TAU*i/64
        for direction in [-1,1]:
            points=[]
            for k in range(10):
                z=k/9
                angle=t+direction*(.43*z+.045*math.sin(z*TAU+i*.71))
                x,y,zz=_stadium_point(angle,z)
                points.append((x*1.012,y*1.012,zz+.006*math.sin(i*1.3)))
            b.chain('bj_lattice',points,.009 if i%4 else .012,.006)
    for z in [.06,.36,.67,.96]:
        b.chain('bj_lattice',[_stadium_point(TAU*i/n,z) for i in range(n)],.009,closed=True)
    # Roof is an elliptical annulus, never a solid disk: the bowl stays open.
    for i in range(80):
        t=TAU*i/80
        for direction in [-1,1]:
            points=[]
            for j in range(7):
                v=j/6
                rr=.445*(1-v)+.275*v
                theta=t+direction*.30*v
                z=.90+.065*math.sin(math.pi*v)+.022*math.cos(2*theta)
                points.append((rr*math.cos(theta),rr*.80*math.sin(theta),z))
            b.chain('bj_lattice',points,.0075,.005)
    b.ring('ivory',.275,.902,.013,ry=.220,n=96)
    for i in range(32):
        t=TAU*i/32
        x,y,z=_stadium_point(t,.02)
        b.beam('stone',(x,y,.025),(x,y,z),.015)


def _balustrade(b,r,z,posts=40,gate=True):
    for i in range(posts):
        theta=TAU*i/posts
        if gate and abs(math.cos(theta))<.16:
            continue
        x,y=r*math.cos(theta),r*math.sin(theta)
        b.cylinder('bj_marble',(x,y,z+.029),.006,.058,8)
        b.cylinder('bj_marble',(x,y,z+.061),.008,.011,8,radius_top=.004)
        next_theta=theta+TAU/posts
        if gate and abs(math.cos(next_theta))<.16:
            continue
        for dz in [.018,.045]:
            b.beam('bj_marble',(x,y,z+dz),(r*math.cos(next_theta),r*math.sin(next_theta),z+dz),.005)


def _circular_roof(b,r,z,h):
    profile=[(r,z+.014*h),(r*.97,z),(r*.86,z+.10*h),(r*.64,z+.38*h),
             (r*.36,z+.70*h),(r*.11,z+.96*h),(r*.06,z+h)]
    b.lathe('bj_blue',profile,n=96)
    b.ring('bj_gold_edge',r,z+.014*h,.004,n=96)
    for i in range(96):
        t=TAU*i/96
        points=[(rr*math.cos(t),rr*math.sin(t),zz+.002) for rr,zz in profile]
        b.chain('bj_blue_edge',points,.0027,.002)
    for rr,zz in profile[1:-1]:
        b.ring('bj_blue_edge',rr,zz,.0015,n=96)


def _heaven(b):
    for r,z,h in [(.47,.026,.052),(.415,.077,.050),(.36,.126,.048)]:
        b.cylinder('bj_marble',(0,0,z),r,h,96)
        b.ring('ivory',r,z+h/2,.006,n=96)
        _balustrade(b,r-.016,z+h/2,40)
    # Four ceremonial stairways cross the concentric marble terraces.
    for angle in [0,math.pi/2,math.pi,3*math.pi/2]:
        for step in range(13):
            radial=.47-step*.014
            z=.009+step*.0108
            b.box('bj_marble',(radial*math.cos(angle),radial*math.sin(angle),z/2),(.037,.11,z),angle)
    b.cylinder('bj_red',(0,0,.264),.262,.218,72)
    for i in range(28):
        theta=TAU*i/28
        x,y=.264*math.cos(theta),.264*math.sin(theta)
        b.cylinder('bj_red',(x,y,.265),.009,.223,10)
        theta2=theta+TAU/56
        a=(.264*math.cos(theta2),.264*math.sin(theta2),.260)
        b.box('dark_glass',a,(.031,.006,.137),theta2-math.pi/2)
        for dz in [-.065,.065]:
            b.box('bj_gold_edge',(a[0],a[1],a[2]+dz),(.033,.008,.006),theta2-math.pi/2)
    for r,z in [(.266,.18),(.267,.345),(.268,.365),(.217,.574),(.158,.76)]:
        b.ring('bj_gold_edge',r,z,.008,n=72)
    _circular_roof(b,.343,.366,.210)
    b.cylinder('bj_red',(0,0,.575),.213,.076,72)
    _circular_roof(b,.270,.578,.190)
    b.cylinder('bj_red',(0,0,.766),.147,.065,72)
    _circular_roof(b,.197,.764,.190)
    b.cylinder('bj_gold_edge',(0,0,.963),.021,.035,24,radius_top=.011)
    b.cylinder('bj_gold_edge',(0,0,.989),.009,.022,20,radius_top=.002)
    for i in range(32):
        t=TAU*i/32
        for r,z in [(.275,.352),(.218,.564),(.151,.749)]:
            b.box('bj_blue_edge',(r*math.cos(t),r*math.sin(t),z),(.022,.018,.026),t)


def _hip_roof(b,cx,cy,z,wx,wy,h,key='bj_gold'):
    # Rounded sweep from raised eaves into a narrow, horizontal ridge.
    profile=[(1,1,.09),(.96,.94,.015),(.78,.69,.23),(.58,.34,.60),(.45,.025,.88)]
    per_side=12
    perimeter=[]
    for side in range(4):
        for i in range(per_side):
            t=-1+2*i/per_side
            perimeter.append((t,-1) if side==0 else (1,t) if side==1 else (-t,1) if side==2 else (-1,-t))
    n=len(perimeter)
    verts=[]
    for a,c,zz in profile:
        for x,y in perimeter:
            lift=.14*(abs(x*y)**5)*(1-zz)**3
            verts.append((cx+x*wx*a/2,cy+y*wy*c/2,z+h*(zz+lift)))
    b.add(key,verts,[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(len(profile)-1) for i in range(n)],True)
    b.add(key,verts,[tuple((len(profile)-1)*n+i for i in range(n))])
    b.chain('bj_gold_edge',[Vector(v)+Vector((0,0,.001)) for v in verts[:n]],.004,closed=True)
    b.beam('bj_gold_edge',(cx-wx*.24,cy,z+h*.90),(cx+wx*.24,cy,z+h*.90),.007)
    for side in [-1,1]:
        x=cx+side*wx*.24
        b.chain('bj_gold_edge',[(x-side*.025,cy,z+h*.90),(x,cy,z+h*.94),(x+side*.018,cy,z+h*1.02)],.006)
    # Ceramic rows are real raised strips, batched rather than individual objects.
    for i in range(n):
        points=[Vector(verts[j*n+i])+Vector((0,0,.0015)) for j in range(len(profile))]
        b.chain('bj_gold_edge',points,.0018,.0014)
    for corner in [0,per_side,per_side*2,per_side*3]:
        b.chain('bj_gold_edge',[verts[j*n+corner] for j in range(len(profile))],.005)


def _palace_hall(b,x,y,z,w,d,h,double=True):
    b.box('bj_marble',(x,y,z+.025*h),(w*.91,d*.86,.05*h))
    wall_h=.40*h if double else .50*h
    b.box('bj_red',(x,y,z+.05*h+wall_h/2),(w*.72,d*.68,wall_h))
    for side in [-1,1]:
        for i in range(9):
            xx=x+w*.32*(-1+2*i/8)
            yy=y+side*d*.35
            b.cylinder('bj_red',(xx,yy,z+.05*h+wall_h/2),.0055,wall_h,8)
            if i<8:
                b.box('dark',(xx+w*.04,yy,z+.05*h+wall_h*.48),(w*.053,.003,wall_h*.70))
                b.box('bj_gold_edge',(xx+w*.04,yy-side*.002,z+.05*h+wall_h*.75),(w*.052,.004,.006))
                for division in [-.017,0,.017]:
                    b.box('bj_red',(xx+w*(.04+division),yy+side*.003,z+.05*h+wall_h*.48),(.0022,.004,wall_h*.70))
                for level in [.24,.41,.58,.70]:
                    b.box('bj_red',(xx+w*.04,yy+side*.003,z+.05*h+wall_h*level),(w*.053,.004,.0028))
    for side in [-1,1]:
        for i in range(5):
            yy=y+d*.28*(-1+2*i/4)
            b.cylinder('bj_red',(x+side*w*.365,yy,z+.05*h+wall_h/2),.005,wall_h,8)
    roof_z=z+.05*h+wall_h
    _hip_roof(b,x,y,roof_z,w,d,h*.30 if double else h*.44)
    if double:
        b.box('bj_red',(x,y,z+h*.71),(w*.59,d*.47,h*.12))
        _hip_roof(b,x,y,z+h*.76,w*.84,d*.77,h*.24)


def _arched_gate(b,x,y,bottom,width,height,depth):
    r=width/2
    spring=bottom+height-r
    # Recessed dark arch with stone voussoirs and an actual curved opening shape.
    points=[(x-r,y,bottom),(x+r,y,bottom),(x+r,y,spring)]
    points.extend((x+r*math.cos(i*math.pi/16),y,spring+r*math.sin(i*math.pi/16)) for i in range(1,17))
    b.add('dark',points,[tuple(range(len(points)))])
    arc=[(x+r*math.cos(i*math.pi/16),y-.001,spring+r*math.sin(i*math.pi/16)) for i in range(17)]
    b.chain('bj_marble',arc,.006)
    b.beam('bj_marble',(x-r,y,bottom),(x-r,y,spring),.006)
    b.beam('bj_marble',(x+r,y,bottom),(x+r,y,spring),.006)


def _palace(b):
    b.box('paving',(0,0,.018),(.99,.99,.036))
    # Walled courts, front Tiananmen gate and a dominant double-eaved rear hall.
    for x in [-.473,.473]:
        b.box('bj_red',(x,0,.095),(.025,.97,.155))
        _hip_roof(b,x,0,.174,.047,.99,.025)
    b.box('bj_red',(0,.473,.095),(.96,.025,.155))
    _hip_roof(b,0,.473,.174,.99,.047,.025)
    b.box('bj_red',(0,-.373,.111),(.94,.22,.185))
    b.box('bj_marble',(0,-.373,.210),(.96,.23,.020))
    for x in [-.34,-.17,0,.17,.34]:
        _arched_gate(b,x,-.485,.035,.046,.095,.22)
    _palace_hall(b,0,-.367,.222,.72,.23,.35,True)
    # Rear Hall of Supreme Harmony on a triple white terrace.
    for j in range(3):
        b.box('bj_marble',(0,.195,.052+j*.023),(.58-j*.035,.36-j*.025,.024))
    _palace_hall(b,0,.19,.091,.64,.38,.85,True)
    for side in [-1,1]:
        _palace_hall(b,side*.35,.10,.036,.205,.27,.36,False)
        _palace_hall(b,side*.35,.365,.036,.205,.13,.25,False)
    # White processional steps, terrace rails, and courtyard paving paths.
    for j in range(7):
        b.box('bj_marble',(0,-.020-j*.013,.040+j*.008),(.16,.014,.014))
    for x in [-.27,.27]:
        for j in range(12):
            y=.04+j*.027
            b.box('bj_marble',(x,y,.143),(.008,.008,.075))
        for z in [.132,.164]:
            b.beam('bj_marble',(x,.035,z),(x,.36,z),.005)
    b.box('ivory',(0,-.087,.039),(.12,.28,.006))
    for x in [-.22,.22]:
        for y in [-.16,-.065]:
            b.cylinder('bj_gold',(x,y,.068),.014,.062,16,radius_top=.020)
            b.cylinder('bj_gold_edge',(x,y,.102),.023,.011,16)
    # Finials and vermilion lanterns articulate the long gate frontage.
    for x in [-.28,-.14,0,.14,.28]:
        b.cylinder('bj_gold_edge',(x,-.493,.061),.003,.051,8)
        b.cylinder('bj_red',(x,-.493,.097),.010,.018,12)


def great_wall_profile(samples=81):
    """Normalized route for optional terrain matching by the scene assembler."""
    result=[]
    for i in range(samples):
        t=i/(samples-1)
        x=-.45+.90*t
        y=.14*math.sin(TAU*t-.3)+.075*math.sin(2*TAU*t+.5)
        z=.10+.43*math.sin(math.pi*t)**2+.075*math.sin(3*math.pi*t)**2
        result.append((x,y,z))
    return result


def _wall_tower(b,p,angle):
    x,y,z=p
    b.box('bj_brick',(x,y,z+.12),(.115,.13,.24),angle)
    b.box('bj_mortar',(x,y,z+.243),(.130,.145,.019),angle)
    b.box('dark',(x,y,z+.258),(.107,.122,.012),angle)
    co,si=math.cos(angle),math.sin(angle)
    local=lambda a,c,zz:(x+a*co-c*si,y+a*si+c*co,zz)
    for side in [-1,1]:
        for i in range(5):
            b.box('bj_brick',local(-.053+i*.0265,side*.069,z+.289),(.014,.014,.055),angle)
            b.box('bj_brick',local(side*.061,-.052+i*.026,z+.289),(.014,.014,.055),angle)
        # Deep arrow slits have recessed dark centres and pale brick lintels.
        for i in [-1,1]:
            b.box('dark',local(i*.028,side*.0654,z+.16),(.014,.003,.047),angle)
            b.box('bj_mortar',local(i*.028,side*.067,z+.186),(.022,.005,.006),angle)
    for j in range(5):
        zline=z+.024+j*.043
        for side in [-1,1]:
            b.beam('bj_mortar',local(-.058,side*.0655,zline),local(.058,side*.0655,zline),.0017)
            b.beam('bj_mortar',local(side*.058,-.065,zline),local(side*.058,.065,zline),.0017)


def _great_wall(b):
    route=great_wall_profile()
    half=.024
    for i,(a,c) in enumerate(zip(route,route[1:])):
        a,c=Vector(a),Vector(c)
        direction=(c-a).normalized()
        across=Vector((-direction.y,direction.x,0)).normalized()*half
        # Solid retaining masonry extends to local ground; terrain can overlap it.
        verts=[(a-across).xy[:]+(0,), (c-across).xy[:]+(0,), (c+across).xy[:]+(0,), (a+across).xy[:]+(0,),
               tuple(a-across),tuple(c-across),tuple(c+across),tuple(a+across)]
        b.add('bj_brick',verts,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
        b.beam('bj_mortar',a,c,.048,.008)
        for side in [-1,1]:
            p,q=a+across*side,c+across*side
            b.beam('bj_brick',p+Vector((0,0,.027)),q+Vector((0,0,.027)),.011,.054)
            for j in range(1,6):
                b.beam('bj_mortar',(p.x,p.y,a.z*j/6),(q.x,q.y,c.z*j/6),.0014)
            if i%2==0:
                mid=(p+q)/2
                angle=math.atan2(direction.y,direction.x)
                b.box('bj_brick',(mid.x,mid.y,mid.z+.069),(.016,.014,.045),angle)
        if i%2==0:
            b.beam('bj_mortar',a-across*.78,a+across*.78,.002,.003)
    for index in [4,25,48,74]:
        p=route[index]
        a,c=Vector(route[index-1]),Vector(route[index+1])
        _wall_tower(b,p,math.atan2(c.y-a.y,c.x-a.x))
    if b.parent is not None:
        b.parent['bj_wall_profile_normalized']=json.dumps(route)
        b.parent['bj_wall_profile_world_scale']=list(b.size)


def build(kind, name, parent, collection, materials, width, depth, height):
    """Build a landmark as a small collection of editable, material-batched meshes."""
    functions={'cctv':_cctv,'zun':_zun,'stadium':_stadium,'heaven':_heaven,'palace':_palace,'great_wall':_great_wall}
    if kind not in functions:
        raise ValueError('Unsupported Beijing landmark: '+str(kind))
    if min(width,depth,height)<=0:
        raise ValueError('Landmark dimensions must be positive')
    builder=_Builder(name,parent,collection,materials,(width,depth,height))
    functions[kind](builder)
    return builder.finish(kind)
