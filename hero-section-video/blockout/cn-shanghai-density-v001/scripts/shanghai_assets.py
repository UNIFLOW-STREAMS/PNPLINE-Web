"""Editable Shanghai miniature buildings, material-batched inside true footprints.

build(kind, name, parent, collection, materials, w, d, h, variant=0)
returns meshes directly parented to parent. Ground Z0; front negative Y.
Kinds: tower, heritage, shikumen, cultural (midrise/bund/house/dome aliases).
The module never changes supplied materials, animation, cameras, or source files.
"""
import math
from collections import defaultdict
import bpy
from mathutils import Vector

TAU=math.tau
__all__=['build']


class _Batch:
    def __init__(self,name,parent,collection,materials,w,d,h,variant):
        self.name,self.parent,self.collection,self.materials=name,parent,collection,materials
        self.w,self.d,self.h=map(float,(w,d,h));self.variant=int(variant)
        assert min(self.w,self.d,self.h)>0
        self.parts=defaultdict(lambda:[[],[],[]])

    def mesh(self,mat,vertices,faces,smooth=False):
        vs,fs,sm=self.parts[mat];offset=len(vs)
        vs.extend(tuple(v)for v in vertices)
        fs.extend(tuple(offset+i for i in f)for f in faces)
        sm.extend([smooth]*len(faces))

    def box(self,mat,p,size):
        x,y,z=p;wx,dy,hz=[v/2 for v in size]
        v=[(x+a*wx,y+b*dy,z+c*hz)for a,b,c in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
        self.mesh(mat,v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])

    def tube(self,mat,points,r,sides=6,closed=False):
        ps=[Vector(p)for p in points];vs=[];fs=[]
        if len(ps)<2 or r<=0:return
        for i,p in enumerate(ps):
            previous=ps[(i-1)%len(ps)]if closed or i else ps[0]
            following=ps[(i+1)%len(ps)]if closed or i<len(ps)-1 else ps[-1]
            z=(following-previous).normalized();ref=Vector((0,0,1))if abs(z.z)<.9 else Vector((1,0,0))
            x=z.cross(ref).normalized();y=z.cross(x).normalized()
            vs.extend(p+r*(x*math.cos(j*TAU/sides)+y*math.sin(j*TAU/sides))for j in range(sides))
        for i in range(len(ps)if closed else len(ps)-1):
            ni=(i+1)%len(ps)
            fs.extend((i*sides+j,i*sides+(j+1)%sides,ni*sides+(j+1)%sides,ni*sides+j)for j in range(sides))
        if not closed:fs.extend([tuple(range(sides-1,-1,-1)),tuple((len(ps)-1)*sides+j for j in range(sides))])
        self.mesh(mat,vs,fs,True)

    def ring(self,mat,p,rx,ry,r,n=24):
        self.tube(mat,[(p[0]+rx*math.cos(j*TAU/n),p[1]+ry*math.sin(j*TAU/n),p[2])for j in range(n)],r,4,True)

    def loft(self,mat,rings,caps=True,smooth=False):
        n=len(rings[0]);vs=[p for ring in rings for p in ring]
        fs=[(i*n+j,i*n+(j+1)%n,(i+1)*n+(j+1)%n,(i+1)*n+j)for i in range(len(rings)-1)for j in range(n)]
        if caps:fs.extend([tuple(range(n-1,-1,-1)),tuple((len(rings)-1)*n+j for j in range(n))])
        self.mesh(mat,vs,fs,smooth)

    def arch(self,mat,x,y,z,w,h,depth,trim=0):
        r=w/2;rz=min(r,h*.95);spring=z+h-rz
        if trim<=0:
            profile=[(x-r,z),(x-r,spring)]+[(x+r*math.cos(math.pi-i*math.pi/12),spring+rz*math.sin(math.pi-i*math.pi/12))for i in range(1,13)]+[(x+r,z)]
            n=len(profile);vs=[(xx,yy,zz)for yy in [y-depth/2,y+depth/2]for xx,zz in profile]
            self.mesh(mat,vs,[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)])
            return
        for sign in [-1,1]:self.box(mat,(x+sign*(r+trim/2),y,(z+spring)/2),(trim,depth,spring-z))
        vs=[];fs=[]
        for yy in [y-depth/2,y+depth/2]:
            for rr in [r,r+trim]:vs.extend((x+rr*math.cos(j*math.pi/12),yy,spring+(rz+rr-r)*math.sin(j*math.pi/12))for j in range(13))
        for j in range(12):fs.extend([(j,j+1,j+14,j+13),(j+26,j+39,j+40,j+27),(j,j+26,j+27,j+1),(j+13,j+14,j+40,j+39)])
        fs.extend([(0,13,39,26),(12,38,51,25)])
        self.mesh(mat,vs,[tuple(reversed(f))for f in fs])

    def finish(self,kind):
        vertices=[p for vs,_,_ in self.parts.values()for p in vs]
        lo=[min(p[a]for p in vertices)for a in range(3)];hi=[max(p[a]for p in vertices)for a in range(3)]
        sx=min(1,self.w/(2*max(abs(lo[0]),abs(hi[0]),1e-8)))
        sy=min(1,self.d/(2*max(abs(lo[1]),abs(hi[1]),1e-8)))
        offset=-min(0,lo[2]);sz=min(1,self.h/max(hi[2]+offset,1e-8))
        result=[]
        for key,(vs,fs,smooth)in sorted(self.parts.items()):
            me=bpy.data.meshes.new(self.name+'__'+key+'_Mesh')
            me.from_pydata([(x*sx,y*sy,(z+offset)*sz)for x,y,z in vs],[],fs);me.update()
            me.materials.append(self.materials.get(key,self.materials['stone']))
            for p,value in zip(me.polygons,smooth):p.use_smooth=value
            o=bpy.data.objects.new(self.name+'__'+key,me);self.collection.objects.link(o);o.parent=self.parent
            o['shd_kind']=kind;o['shd_variant']=self.variant;o['shd_material_group']=key
            o['nominal_dimensions']=(self.w,self.d,self.h);o['front_axis']='-Y'
            result.append(o)
        return result


def _octagon(w,d,z,c=.15,dx=0,dy=0):
    x,y=w/2,d/2;k=min(w,d)*c
    return [(dx+a,dy+b,z)for a,b in [(-x+k,-y),(x-k,-y),(x,-y+k),(x,y-k),(x-k,y),(-x+k,y),(-x,y-k),(-x,-y+k)]]


def _glass_block(b,cx,cy,w,d,z0,z1,variant=0,body='glass'):
    small=min(w,d);floors=max(3,min(19,round((z1-z0)/.28)));dz=(z1-z0)/floors
    b.loft(body,[_octagon(w,d,z0,dx=cx,dy=cy),_octagon(w,d,z1,dx=cx,dy=cy)])
    for j in range(floors+1):
        z=z0+dz*j;b.tube('ivory'if variant%3==0 else'metal',_octagon(w*1.015,d*1.015,z,dx=cx,dy=cy),small*.009,4,True)
    for sign in [-1,1]:
        for j in range(1,7):
            x=cx+w*(-.48+j*.137)
            b.box('metal'if variant%2 else'white',(x,cy+sign*(d*.502),(z0+z1)/2),(small*.012,small*.012,z1-z0))
        for j in range(1,5):
            y=cy+d*(-.46+j*.184)
            b.box('metal',(cx+sign*w*.502,y,(z0+z1)/2),(small*.012,small*.012,z1-z0))


def _tower(b):
    w,d,h=b.w,b.d,b.h;v=b.variant%6;small=min(w,d)
    b.box('stone',(0,0,h*.022),(w*.98,d*.98,h*.044))
    podium=.14*h
    b.box('ivory',(0,0,podium/2),(w*.90,d*.88,podium))
    for j in range(5):
        x=w*(-.34+j*.17);b.box('dark_glass',(x,-d*.445,podium*.53),(w*.12,d*.025,podium*.68))
    b.box('white',(0,0,podium),(w*.94,d*.92,h*.028))
    if v==0:
        for ww,dd,z0,z1 in [(.82,.80,.15,.57),(.68,.68,.57,.80),(.52,.54,.80,.965)]:
            _glass_block(b,0,0,w*ww,d*dd,h*z0,h*z1,b.variant)
        b.box('metal',(0,0,h*.976),(w*.50,d*.52,h*.022))
    elif v==1:
        n=28;rings=[]
        for t in [0,.32,.66,1]:
            factor=1-.12*t;rings.append([(w*.40*factor*math.cos(j*TAU/n),d*.39*factor*math.sin(j*TAU/n),h*(.15+.80*t))for j in range(n)])
        b.loft('dark_glass',rings,smooth=True)
        for j in range(21):
            t=j/20;b.ring('metal',(0,0,h*(.15+.80*t)),w*.402*(1-.12*t),d*.392*(1-.12*t),small*.007,n)
        for j in range(n):
            a=j*TAU/n;b.tube('white'if j%4==0 else'metal',[(w*.402*math.cos(a),d*.392*math.sin(a),h*.15),(w*.354*math.cos(a),d*.345*math.sin(a),h*.95)],small*.008,4)
        b.ring('ivory',(0,0,h*.965),w*.355,d*.346,small*.035,n)
        b.loft('roof',[[(w*.33*math.cos(j*TAU/n),d*.32*math.sin(j*TAU/n),h*.963)for j in range(n)],[(w*.29*math.cos(j*TAU/n),d*.28*math.sin(j*TAU/n),h*.985)for j in range(n)]])
    elif v==2:
        _glass_block(b,-w*.17,d*.08,w*.48,d*.68,h*.15,h*.96,b.variant)
        _glass_block(b,w*.24,-d*.1,w*.34,d*.67,h*.15,h*.73,b.variant+1,'dark_glass')
        b.box('ivory',(-w*.17,d*.08,h*.97),(w*.50,d*.70,h*.03))
        b.box('roof',(w*.24,-d*.1,h*.742),(w*.36,d*.69,h*.024))
        for j in range(5):b.box('stone',(w*.16+j*w*.04,-d*.1,h*.78),(w*.018,d*.55,h*.056))
    elif v==3:
        rings=[_octagon(w*.79,d*.78,h*.15,.20),_octagon(w*.70,d*.70,h*.94,.22,dx=w*.035)]
        b.loft('dark_glass',rings)
        for j in range(8):
            b.tube('white',[rings[0][j],rings[1][j]],small*.012,5)
            if j%2==0:
                for k in range(3):
                    a=k/3;c=(k+1)/3
                    b.tube('metal',[Vector(rings[0][j]).lerp(Vector(rings[1][j]),a),Vector(rings[0][(j+1)%8]).lerp(Vector(rings[1][(j+1)%8]),c)],small*.009,4)
        for j in range(17):
            t=j/16;rr=[Vector(a).lerp(Vector(c),t)for a,c in zip(rings[0],rings[1])];b.tube('metal',rr,small*.005,4,True)
        b.loft('ivory',[_octagon(w*.72,d*.72,h*.95,.22,dx=w*.035),_octagon(w*.58,d*.58,h*.99,.22,dx=w*.035)])
    elif v==4:
        for ww,dd,z0,z1 in [(.82,.80,.15,.58),(.70,.70,.58,.80),(.51,.56,.80,.95)]:
            b.box('ivory',(0,0,h*(z0+z1)/2),(w*ww,d*dd,h*(z1-z0)))
            for sign in [-1,1]:
                for j in range(5):
                    x=w*ww*(-.36+j*.18)
                    b.box('dark_glass',(x,sign*d*dd*.505,h*(z0+z1)/2),(w*.085,d*.012,h*(z1-z0)*.85))
                    b.box('stone',(x+w*.055,sign*d*dd*.515,h*(z0+z1)/2),(w*.017,d*.025,h*(z1-z0)))
            for j in range(3):b.box('white',(0,0,h*(z1-.012*j)),(w*(ww+.025),d*(dd+.025),h*.008))
        b.box('gold',(0,0,h*.971),(w*.12,d*.18,h*.042))
    else:
        _glass_block(b,0,d*.045,w*.80,d*.66,h*.15,h*.87,b.variant,'glass')
        _glass_block(b,-w*.12,d*.09,w*.54,d*.48,h*.87,h*.97,b.variant+1)
        for z in [.31,.50,.69]:
            b.box('ivory',(0,-d*.35,h*z),(w*.82,d*.14,h*.045))
            b.box('green',(0,-d*.368,h*(z+.026)),(w*.69,d*.08,h*.018))
        b.box('roof',(-w*.12,d*.09,h*.98),(w*.56,d*.50,h*.02))
    # A recessed entrance and small canopy make the support towers read at street level.
    b.box('dark_glass',(0,-d*.462,h*.062),(w*.20,d*.025,h*.105))
    b.box('metal',(0,-d*.464,h*.125),(w*.30,d*.06,h*.018))


def _window(b,x,y,z,w,h,small,arched=False):
    if arched:
        b.arch('dark_glass',x,y,z,w,h,small*.018)
        b.arch('ivory',x,y-small*.012,z,w,h,small*.035,small*.026)
    else:
        b.box('dark_glass',(x,y,z+h/2),(w,small*.018,h))
        for sign in [-1,1]:b.box('ivory',(x+sign*w*.56,y-small*.012,z+h/2),(small*.032,small*.035,h*1.08))
        b.box('ivory',(x,y-small*.014,z+h),(w*1.15,small*.045,small*.033))
    b.box('stone',(x,y-small*.025,z-small*.015),(w*1.25,small*.075,small*.04))
    b.box('ivory',(x,y-small*.025,z+h*.42),(w,small*.018,small*.018))
    b.box('ivory',(x,y-small*.028,z+h*.47),(small*.018,small*.018,h*.86))
    if not arched:b.box('white',(x,y-small*.028,z+h+small*.052),(w*1.29,small*.065,small*.024))


def _dome(b,cx,cy,z,rx,ry,h,mat='stone',ribs='ivory',n=24):
    rings=[]
    for k in range(13):
        t=k/12;angle=t*math.pi/2;r=max(.001,math.cos(angle))
        rings.append([(cx+rx*r*math.cos(j*TAU/n),cy+ry*r*math.sin(j*TAU/n),z+h*math.sin(angle))for j in range(n)])
    b.loft(mat,rings,smooth=True)
    for j in range(0,n,2):b.tube(ribs,[ring[j]for ring in rings],min(rx,ry)*.025,5)
    b.ring(ribs,(cx,cy,z),rx,ry,min(rx,ry)*.045,n)


def _clock(b,x,y,z,r,small):
    b.tube('stone',[(x,y+small*.02,z),(x,y-small*.025,z)],r*1.16,24)
    b.tube('white',[(x,y-small*.026,z),(x,y-small*.035,z)],r,24)
    face=y-small*.042
    for j in range(12):
        a=j*TAU/12;b.tube('dark',[(x+r*.77*math.sin(a),face,z+r*.77*math.cos(a)),(x+r*.89*math.sin(a),face,z+r*.89*math.cos(a))],small*.006,4)
    b.tube('dark',[(x-r*.46,face-small*.01,z+r*.15),(x,face-small*.01,z),(x+r*.1,face-small*.01,z+r*.69)],small*.012,4)


def _heritage(b):
    w,d,h=b.w,b.d,b.h;small=min(w,d);v=b.variant%5
    wall=h*(.69 if v in [1,2,3]else .83);floors=3+(b.variant//5%2);pitch=wall/floors
    bays=max(3,min(7,round(w/.55)));space=w*.80/bays
    b.box('stone',(0,0,h*.023),(w*.98,d*.98,h*.046))
    b.box('ivory',(0,0,(wall+h*.04)/2),(w*.88,d*.84,wall-h*.04))
    # Projecting corner pavilions and central entrance risalit.
    for x in [-w*.36,0,w*.36]:b.box('ivory',(x,-d*.40,wall*.48),(w*(.18 if x else .25),d*.08,wall*.88))
    for level in range(floors):
        bottom=h*.065+pitch*level;wh=pitch*.64
        for j in range(bays):
            x=-w*.40+space*(j+.5)
            _window(b,x,-d*.445,bottom,space*.56,wh,small,arched=level==0 or(level==floors-1 and v%2==0))
        for sign in [-1,1]:
            for j in range(3):
                y=d*(-.27+j*.27)
                b.box('dark_glass',(sign*w*.446,y,bottom+wh/2),(small*.018,d*.13,wh))
                for dy in [-.078,.078]:b.box('ivory',(sign*w*.458,y+d*dy,bottom+wh/2),(small*.034,small*.028,wh*1.05))
                b.box('stone',(sign*w*.458,y,bottom-small*.015),(small*.065,d*.18,small*.04))
        for offset,width in [(0,.93),(.024,.95)]:b.box('ivory',(0,0,bottom+wh+small*offset),(w*width,d*(width-.02),small*.028))
    # Pilasters, capitals, quoins and a multi-step crowning cornice.
    for j in range(bays+1):
        x=-w*.40+j*space
        b.box('stone',(x,-d*.457,wall*.50),(space*.105,small*.04,wall*.83))
        for zz in [h*.12,wall*.83]:
            b.box('white',(x,-d*.474,zz),(space*.22,small*.07,small*.045))
    for x in [-w*.445,w*.445]:
        for j in range(max(7,floors*4)):
            z=h*.06+(wall-h*.08)*(j+.5)/max(7,floors*4)
            b.box('stone',(x,-d*.438,z),(w*.075,small*.075,wall/max(7,floors*4)*.72))
    for z,width,thick in [(wall,.94,.035),(wall+h*.021,.98,.025),(wall+h*.043,.95,.018)]:
        b.box('ivory',(0,0,z),(w*width,d*width,h*thick))
    b.box('roof',(0,0,wall+h*.049),(w*.86,d*.84,h*.022))
    parapet=wall+h*.082
    for sign in [-1,1]:
        b.box('ivory',(0,sign*d*.445,parapet),(w*.92,small*.045,h*.028))
        for j in range(bays*3+1):b.box('ivory',(w*(-.43+.86*j/(bays*3)),sign*d*.445,parapet-h*.035),(small*.026,small*.026,h*.062))
        b.box('ivory',(sign*w*.44,0,parapet),(small*.045,d*.88,h*.028))
        for j in range(7):b.box('ivory',(sign*w*.44,d*(-.4+j*.1333),parapet-h*.035),(small*.026,small*.026,h*.062))
    # Monumental stone-framed front doorway and entrance steps.
    b.arch('dark',0,-d*.467,h*.045,w*.12,pitch*.86,small*.03)
    b.arch('ivory',0,-d*.475,h*.045,w*.12,pitch*.86,small*.05,small*.036)
    for j in range(3):b.box('stone',(0,-d*(.465+.008*j),h*(.015+.009*j)),(w*(.24-.025*j),d*.035,h*(.03+.018*j)))
    if v==1:
        rz=wall+h*.05;rx=w*.165;ry=d*.235
        b.loft('ivory',[[(rx*math.cos(j*TAU/24),ry*math.sin(j*TAU/24),z)for j in range(24)]for z in [rz,h*.80]])
        for j in range(12):
            a=j*TAU/12;b.tube('stone',[(rx*math.cos(a),ry*math.sin(a),rz),(rx*math.cos(a),ry*math.sin(a),h*.805)],small*.018,5)
        _dome(b,0,0,h*.80,rx*1.06,ry*1.06,h*.15)
        b.tube('ivory',[(0,0,h*.945),(0,0,h*.995)],small*.018,8)
    elif v==2:
        b.box('ivory',(0,-d*.03,h*.82),(w*.22,d*.29,h*.25))
        for sign in [-1,1]:b.box('stone',(sign*w*.115,-d*.03,h*.82),(w*.025,d*.31,h*.26))
        _clock(b,0,-d*.185,h*.827,min(w*.075,h*.063),small)
        for z,ww,dd in [(.94,.28,.35),(.965,.22,.29),(.985,.14,.21)]:b.box('ivory',(0,-d*.03,h*z),(w*ww,d*dd,h*.025))
        b.tube('gold',[(0,-d*.03,h*.984),(0,-d*.03,h)],small*.008,6)
    elif v==3:
        for x in [-w*.31,w*.31]:
            b.loft('ivory',[[(x+w*.11*math.cos(j*TAU/20),d*.18*math.sin(j*TAU/20),z)for j in range(20)]for z in [wall+h*.045,h*.82]])
            _dome(b,x,0,h*.82,w*.12,d*.19,h*.13,n=20)
            b.tube('stone',[(x,0,h*.94),(x,0,h*.995)],small*.014,6)
        b.mesh('ivory',[(-w*.19,-d*.46,parapet),(w*.19,-d*.46,parapet),(0,-d*.46,h*.91)],[(0,1,2)])
    elif v==4:
        b.loft('roof',[_octagon(w*.86,d*.84,wall+h*.06,.05),_octagon(w*.70,d*.68,h*.985,.05)])
        for j in range(bays):
            x=-w*.37+w*.74*(j+.5)/bays
            b.box('ivory',(x,-d*.38,h*.923),(space*.62,d*.12,h*.095))
            b.arch('dark_glass',x,-d*.447,h*.884,space*.38,h*.071,small*.022)
            b.mesh('stone',[(x-space*.37,-d*.45,h*.96),(x+space*.37,-d*.45,h*.96),(x,-d*.45,h*.992)],[(0,1,2)])
    else:
        b.mesh('ivory',[(-w*.22,-d*.46,parapet),(w*.22,-d*.46,parapet),(0,-d*.46,h*.995)],[(0,1,2)])
        b.tube('stone',[(-w*.23,-d*.465,parapet),(0,-d*.465,h*.995),(w*.23,-d*.465,parapet)],small*.02,5)


def _pitched_roof(b,cx,cy,w,d,eave,rise,variant):
    # Y-axis ridge, curved tile slopes and thick terracotta-grey eaves.
    nx,ny=10,8;vs=[];fs=[]
    def point(i,j):
        x=w*(i/nx-.5);y=d*(j/ny-.5);t=abs(x)/(w/2)
        return (cx+x,cy+y,eave+rise*(1-t**.8+.09*t**8))
    for i in range(nx+1):
        for j in range(ny+1):vs.append(point(i,j))
    for i in range(nx):
        for j in range(ny):a=i*(ny+1)+j;fs.append((a,a+ny+1,a+ny+2,a+1))
    b.mesh('roof',vs,fs)
    small=min(w,d)
    for i in [0,nx]:b.tube('dark',[point(i,j)for j in range(ny+1)],small*.018,5)
    for j in range(ny+1):b.tube('stone'if j in [0,ny]else'roof',[point(i,j)for i in range(nx+1)],small*(.018 if j in [0,ny]else .008),5)
    b.tube('stone',[(cx,cy-d*.49,eave+rise*1.025),(cx,cy+d*.49,eave+rise*1.025)],small*.025,6)
    for side in [-1,1]:
        # White gable wall and stepped stone cap at the street-facing ends.
        y=cy+side*d*.46
        b.mesh('ivory',[(cx-w*.43,y,eave),(cx+w*.43,y,eave),(cx,y,eave+rise*.93)],[(0,1,2)]if side<0 else[(2,1,0)])
        b.tube('stone',[(cx-w*.45,y,eave+rise*.12),(cx,y,eave+rise*1.03),(cx+w*.45,y,eave+rise*.12)],small*.022,5)
        if variant%3==2:
            for j in [-1,0,1]:b.box('ivory',(cx+j*w*.15,y,eave+rise*(.91-.24*abs(j))),(w*.18,small*.04,rise*.17))


def _shikumen_unit(b,cx,cy,w,d,h,variant):
    small=min(w,d);wall=h*.70;floor=wall*.48
    b.box('stone',(cx,cy,h*.025),(w*.98,d*.98,h*.05))
    b.box('ivory'if variant%4!=3 else'stone',(cx,cy,(wall+h*.05)/2),(w*.85,d*.86,wall-h*.05))
    b.box('stone',(cx,cy,h*.075),(w*.89,d*.90,h*.09))
    bays=2 if w<1.6 else 3
    for level in range(2):
        z=h*.10+level*floor
        for j in range(bays):
            x=cx+w*(-.34+.68*(j+.5)/bays);ww=w*.45/bays;hh=floor*.59
            b.box('dark_glass',(x,cy-d*.44,z+hh/2),(ww,small*.02,hh))
            for side in [-1,1]:
                b.box('wood',(x+side*ww*.55,cy-d*.452,z+hh/2),(small*.028,small*.035,hh*1.1))
                if variant%2:b.box('wood',(x+side*ww*.74,cy-d*.446,z+hh/2),(ww*.25,small*.024,hh))
            for zz in [z,z+hh]:b.box('stone',(x,cy-d*.456,zz),(ww*1.25,small*.06,small*.03))
            b.box('wood',(x,cy-d*.459,z+hh*.48),(ww,small*.025,small*.02))
            b.box('wood',(x,cy-d*.46,z+hh*.5),(small*.018,small*.02,hh))
        for side in [-1,1]:
            for j in range(2):
                y=cy+d*(-.19+j*.38)
                b.box('dark_glass',(cx+side*w*.43,y,z+floor*.31),(small*.022,d*.16,floor*.53))
                for yy in [y-d*.095,y+d*.095]:b.box('stone',(cx+side*w*.44,yy,z+floor*.31),(small*.032,small*.026,floor*.60))
    for z in [floor+h*.06,wall-h*.025]:b.box('stone',(cx,cy,z),(w*.90,d*.90,h*.026))
    # Characteristic heavy stone gate with a darker timber door and fanlight.
    x=cx+(w*.23 if variant%2 else 0)
    b.arch('dark',x,cy-d*.465,h*.05,w*.20,floor*.78,small*.03)
    b.arch('stone',x,cy-d*.48,h*.05,w*.20,floor*.78,small*.05,small*.04)
    b.box('ivory',(x,cy-d*.477,floor*.82+h*.05),(w*.32,small*.07,h*.035))
    b.box('stone',(x,cy-d*.47,h*.035),(w*.35,d*.05,h*.05))
    _pitched_roof(b,cx,cy,w*.95,d*.94,wall,h*.265,variant)
    if variant%3==1:b.box('stone',(cx-w*.24,cy+d*.22,h*.91),(w*.09,d*.11,h*.16))


def _shikumen(b):
    w,d,h=b.w,b.d,b.h;v=b.variant%4
    if v==1 and w>1.5:
        for sign in [-1,1]:_shikumen_unit(b,sign*w*.245,0,w*.48,d*.98,h*(1 if sign<0 else .91),b.variant+sign)
    elif v==2 and min(w,d)>1.6:
        _shikumen_unit(b,0,d*.18,w*.94,d*.60,h,b.variant)
        _shikumen_unit(b,-w*.31,-d*.27,w*.33,d*.38,h*.70,b.variant+1)
        b.box('paving',(w*.12,-d*.27,h*.018),(w*.54,d*.38,h*.036))
        b.box('ivory',(w*.30,-d*.42,h*.25),(w*.33,d*.035,h*.50))
        b.arch('dark',w*.30,-d*.442,h*.04,w*.12,h*.32,min(w,d)*.02)
    else:_shikumen_unit(b,0,0,w,d,h,b.variant)


def _cultural(b):
    w,d,h=b.w,b.d,b.h;small=min(w,d);v=b.variant%3
    b.loft('stone',[[(w*.49*math.cos(j*TAU/32),d*.49*math.sin(j*TAU/32),z)for j in range(32)]for z in [0,h*.055]],smooth=True)
    centers=[(0,d*.05,w*.215,d*.32,h*.42,h*.51),(-w*.335,d*.08,w*.135,d*.245,h*.29,h*.31),(w*.335,d*.08,w*.135,d*.245,h*.29,h*.31)]
    if v==1:centers=centers[:2]+[(w*.32,d*.08,w*.14,d*.245,h*.34,h*.38)]
    for cx,cy,rx,ry,wall,rise in centers:
        n=28
        b.loft('glass',[[(cx+rx*math.cos(j*TAU/n),cy+ry*math.sin(j*TAU/n),z)for j in range(n)]for z in [h*.055,wall]],smooth=True)
        for j in range(n):
            a=j*TAU/n;b.tube('white',[(cx+rx*math.cos(a),cy+ry*math.sin(a),h*.055),(cx+rx*math.cos(a),cy+ry*math.sin(a),wall)],small*.009,5)
        for z in [h*.08,wall*.62,wall]:b.ring('ivory',(cx,cy,z),rx,ry,small*.02,n)
        _dome(b,cx,cy,wall,rx,ry,rise,'glass'if v!=2 else'metal','white',n)
    for sign in [-1,1]:
        b.box('ivory',(sign*w*.25,d*.05,h*.20),(w*.17,d*.30,h*.28))
        b.box('roof',(sign*w*.25,d*.05,h*.35),(w*.20,d*.33,h*.025))
    # Low classical entrance portico, canopy and broad curving approach steps.
    for j in range(5):
        x=w*(-.15+j*.075);b.tube('ivory',[(x,-d*.34,h*.055),(x,-d*.34,h*.40)],small*.023,8)
        b.box('white',(x,-d*.34,h*.39),(small*.07,small*.07,h*.025))
    b.box('ivory',(0,-d*.31,h*.425),(w*.38,d*.22,h*.055))
    b.mesh('white',[(-w*.19,-d*.425,h*.45),(w*.19,-d*.425,h*.45),(0,-d*.425,h*.56)],[(0,1,2)])
    for j in range(3):b.box('stone',(0,-d*(.43-.02*j),h*(.016+.016*j)),(w*(.39-.025*j),d*.065,h*(.032+.032*j)))


_KINDS={'tower':_tower,'heritage':_heritage,'shikumen':_shikumen,'cultural':_cultural}
_ALIASES={'midrise':'tower','glass':'tower','bund':'heritage','house':'shikumen','traditional':'shikumen','dome':'cultural'}


def build(kind,name,parent,collection,materials,w,d,h,variant=0):
    kind=_ALIASES.get(kind,kind)
    if kind not in _KINDS:raise ValueError('Unknown Shanghai asset kind: '+str(kind))
    batch=_Batch(name,parent,collection,materials,w,d,h,variant)
    _KINDS[kind](batch)
    return batch.finish(kind)
