"""Editable New York miniature buildings, material-batched inside true footprints.

build(kind, name, parent, collection, materials, w, d, h, variant=0)
returns meshes directly parented to parent. Ground Z0; front negative Y.
Kinds: empire, onewtc, masonry, brownstone, glass. Total height includes antennas.
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
            o['usd_kind']=kind;o['usd_variant']=self.variant;o['usd_material_group']=key
            o['nominal_dimensions']=(self.w,self.d,self.h);o['front_axis']='-Y'
            result.append(o)
        return result


def _rect(w,d,z,cx=0,cy=0):
    return [(cx-w/2,cy-d/2,z),(cx+w/2,cy-d/2,z),(cx+w/2,cy+d/2,z),(cx-w/2,cy+d/2,z)]


def _cylinder(b,mat,cx,cy,z0,z1,rx,ry=None,top=1,n=20):
    ry=rx if ry is None else ry
    b.loft(mat,[[(cx+rx*math.cos(j*TAU/n),cy+ry*math.sin(j*TAU/n),z0)for j in range(n)],
                [(cx+rx*top*math.cos(j*TAU/n),cy+ry*top*math.sin(j*TAU/n),z1)for j in range(n)]],smooth=True)


def _four_faces(w,d):
    # Points on each outer wall with tangents following the perimeter CCW.
    return [(Vector((0,-d/2,0)),Vector((1,0,0)),Vector((0,-1,0)),w),
            (Vector((w/2,0,0)),Vector((0,1,0)),Vector((1,0,0)),d),
            (Vector((0,d/2,0)),Vector((-1,0,0)),Vector((0,1,0)),w),
            (Vector((-w/2,0,0)),Vector((0,-1,0)),Vector((-1,0,0)),d)]


def _wall_box(b,mat,point,tangent,size_u,depth,height):
    b.box(mat,point,(size_u,depth,height)if abs(tangent.x)>.5 else(depth,size_u,height))


def _deco_mass(b,w,d,z0,z1,bays,base_mat='stone',floors=None,cx=0,cy=0):
    h=b.h;s=min(b.w,b.d);height=z1-z0
    b.box(base_mat,(cx,cy,(z0+z1)/2),(w,d,height))
    levels=floors or max(3,round(height/h*82))
    floor_h=height/levels
    for face_i,(center,tangent,normal,span)in enumerate(_four_faces(w,d)):
        center+=Vector((cx,cy,0))
        count=max(3,round(bays*span/w));pitch=span*.91/count
        for j in range(count):
            u=-span*.455+(j+.5)*pitch
            c=center+tangent*u+normal*s*.003
            _wall_box(b,'dark_glass',c+Vector((0,0,(z0+z1)/2)),tangent,pitch*.46,s*.012,height*.965)
            # Raised limestone piers and dark spandrels create the vertical Art Deco rhythm.
            pier=center+tangent*(u+pitch*.41)+normal*s*.012
            _wall_box(b,'ivory',pier+Vector((0,0,(z0+z1)/2)),tangent,pitch*.18,s*.032,height)
            for k in range(1,levels):
                p=c+normal*s*.007+Vector((0,0,z0+k*floor_h))
                _wall_box(b,'stone',p,tangent,pitch*.48,s*.013,floor_h*.25)
            if face_i<2:
                _wall_box(b,'gold',c+normal*s*.009+Vector((0,0,z1-floor_h*.45)),tangent,pitch*.24,s*.013,floor_h*.25)
    # Restrained setbacks: thin stone coping, little horizontal interruption.
    b.box('ivory',(cx,cy,z1-height*.008),(w+s*.018,d+s*.018,height*.018))
    b.box('roof',(cx,cy,z1+h*.0015),(w*.965,d*.965,h*.003))


def _empire(b):
    w,d,h=b.w,b.d,b.h;s=min(w,d)
    b.box('stone',(0,0,h*.016),(w*.98,d*.98,h*.032))
    _deco_mass(b,w*.92,d*.88,h*.032,h*.15,13,floors=10)
    # Long lower wings and their stepped shoulders are deliberately independent of the central shaft.
    for sign in [-1,1]:
        x=sign*w*.34
        _deco_mass(b,w*.23,d*.75,h*.15,h*.26,4,cx=x)
        b.box('ivory',(x,0,h*.26),(w*.245,d*.77,h*.014))
    for ww,dd,z0,z1,bays in [(.70,.69,.15,.30,11),(.59,.58,.30,.64,9),(.48,.47,.64,.755,8),(.36,.36,.755,.805,6)]:
        _deco_mass(b,w*ww,d*dd,h*z0,h*z1,bays)
    # Observation deck crown, projecting limestone ribs, and Art Deco transition to the mooring mast.
    for i,(f,z)in enumerate([(.35,.81),(.30,.821),(.25,.831),(.21,.841)]):
        b.box('ivory',(0,0,h*z),(w*f,d*f,h*.012))
    _deco_mass(b,w*.18,d*.18,h*.842,h*.895,4,'metal',floors=5)
    for sign in [-1,1]:
        b.box('ivory',(sign*w*.104,0,h*.866),(w*.018,d*.19,h*.055))
        b.box('ivory',(0,sign*d*.104,h*.866),(w*.19,d*.018,h*.055))
    _cylinder(b,'metal',0,0,h*.895,h*.917,s*.075,top=.70,n=16)
    for z,r in [(.898,.078),(.907,.067),(.918,.052),(.932,.038),(.955,.024)]:
        b.ring('white',(0,0,h*z),s*r,s*r,s*.008,20)
    _cylinder(b,'metal',0,0,h*.917,h*.956,s*.044,top=.48,n=12)
    _cylinder(b,'white',0,0,h*.956,h*.998,s*.019,top=.10,n=10)
    # Street portal, bronze lintel, and paired side entrances.
    for x in [-w*.29,0,w*.29]:
        b.box('dark_glass',(x,-d*.448,h*.071),(w*.12,s*.025,h*.085))
        for sign in [-1,1]:b.box('ivory',(x+sign*w*.07,-d*.463,h*.073),(w*.018,s*.055,h*.098))
        b.box('gold',(x,-d*.467,h*.124),(w*.16,s*.06,h*.014))
    _us_flag(b)


def _us_flag(b):
    # A small thirteen-stripe flag with fifty stars, below the existing mast tip.
    w,d,h=b.w,b.d,b.h;s=min(w,d)
    length=min(w*.42,h*.035*1.9);height=length/1.9
    x0=s*.015;top=h*.961;thickness=s*.0025
    def position(x,z,front=True):
        t=(x-x0)/length
        return (x,-d*.018-d*.021*math.sin(t*math.pi*1.7)-(thickness if front else 0),z+h*.0025*math.sin(t*math.pi*1.3))
    def ribbon(mat,left,right,bottom,upper):
        for j in range(10):
            xa=left+(right-left)*j/10;xc=left+(right-left)*(j+1)/10
            corners=[(xa,bottom),(xc,bottom),(xc,upper),(xa,upper)]
            vs=[position(x,z,front)for front in [True,False]for x,z in corners]
            b.mesh(mat,vs,[(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)])
    for j in range(13):
        ribbon('red'if j%2==0 else'white',x0,x0+length,top-height*(j+1)/13,top-height*j/13)
    canton_w=length*.40;canton_h=height*7/13
    # Slightly forward overlay follows the same shallow fabric wave.
    original_thickness=thickness;thickness*=2.2
    ribbon('blue_roof',x0,x0+canton_w,top-canton_h,top)
    thickness=original_thickness*3.2
    for row in range(9):
        count=6 if row%2==0 else 5
        for col in range(count):
            x=x0+canton_w*((col+.5)/6 if count==6 else(col+1)/6)
            z=top-canton_h*(row+1)/10;r=min(canton_w/13,canton_h/11)*.50
            ring=[(x+(r if j%2==0 else r*.40)*math.cos(math.pi/2+j*TAU/10),
                   z+(r if j%2==0 else r*.40)*math.sin(math.pi/2+j*TAU/10))for j in range(10)]
            vs=[position(xx,zz,front)for front in [True,False]for xx,zz in ring]
            b.mesh('white',vs,[tuple(range(10)),tuple(range(19,9,-1))]+[(j,j+10,(j+1)%10+10,(j+1)%10)for j in range(10)])
    b.tube('metal',[(0,-d*.018,top-height),(0,-d*.018,top+h*.006)],s*.009,6)


def _triangle_scan(triangle,value,axis):
    hits=[]
    for a,c in zip(triangle,triangle[1:]+triangle[:1]):
        av=axis(a);cv=axis(c)
        if abs(cv-av)<1e-10:continue
        t=(value-av)/(cv-av)
        if -1e-8<=t<=1+1e-8:
            p=a.lerp(c,max(0,min(1,t)))
            if not any((p-q).length<1e-7 for q in hits):hits.append(p)
    return hits[:2]if len(hits)>=2 else[]


def _onewtc(b):
    w,d,h=b.w,b.d,b.h;s=min(w,d)
    b.box('stone',(0,0,h*.009),(w*.98,d*.98,h*.018))
    b.box('dark_glass',(0,0,h*.061),(w*.88,d*.88,h*.104))
    # Prismatic security podium with vertical fluted, reflective fins.
    for center,tangent,normal,span in _four_faces(w*.88,d*.88):
        for j in range(26):
            p=center+tangent*(span*(-.475+j*.95/25))+normal*s*.005
            _wall_box(b,'metal',p+Vector((0,0,h*.060)),tangent,span*.009,s*.02,h*.099)
    b.box('metal',(0,0,h*.114),(w*.895,d*.895,h*.009))
    bottom=[Vector(p)for p in _rect(w*.88,d*.88,h*.119)]
    top=[Vector(p)for p in [(0,-d*.415,h*.782),(w*.415,0,h*.782),(0,d*.415,h*.782),(-w*.415,0,h*.782)]]
    triangles=[];faces=[]
    for j in range(4):
        faces.extend([(j,(j+1)%4,4+j),(j,4+j,4+(j-1)%4)])
        triangles.extend([[bottom[j],bottom[(j+1)%4],top[j]],[bottom[j],top[j],top[(j-1)%4]]])
    b.mesh('glass',bottom+top,faces+[(3,2,1,0),(4,5,6,7)])
    # Planar clipped grids preserve the eight triangular facets: no cylindrical facade substitution.
    for triangle in triangles:
        a,c,e=triangle;normal=(c-a).cross(e-a).normalized()
        hz=(c-a)if abs(c.z-a.z)<1e-6 else(e-c)
        hz=Vector((hz.x,hz.y,0)).normalized()
        floor_count=70
        for j in range(1,floor_count):
            z=h*(.119+(.782-.119)*j/floor_count)
            segment=_triangle_scan(triangle,z,lambda p:p.z)
            if segment:b.tube('metal',[p+normal*s*.0015 for p in segment],s*.0017,4)
        coords=[p.dot(hz)for p in triangle];mn,mx=min(coords),max(coords)
        for j in range(1,17):
            segment=_triangle_scan(triangle,mn+(mx-mn)*j/17,lambda p:p.dot(hz))
            if segment:b.tube('metal',[p+normal*s*.002 for p in segment],s*.0021,4)
    for j in range(4):
        b.tube('white',[bottom[j],top[j]],s*.010,6)
        b.tube('white',[bottom[j],top[(j-1)%4]],s*.010,6)
    b.tube('metal',top,s*.018,6,True)
    roof=[(p.x*.97,p.y*.97,h*.783)for p in top]
    b.loft('roof',[roof,[(x,y,h*.788)for x,y,z in roof]])
    # Circular rooftop communications ring and a visible open mast support, with no box penthouse.
    for z,r in [(.792,.235),(.802,.215),(.811,.185)]:b.ring('metal',(0,0,h*z),w*r,d*r,s*.012,32)
    for j in range(12):
        a=j*TAU/12
        b.tube('metal',[(w*.233*math.cos(a),d*.233*math.sin(a),h*.79),(w*.181*math.cos(a),d*.181*math.sin(a),h*.812)],s*.006,4)
    _cylinder(b,'dark',0,0,h*.789,h*.815,s*.085,top=.7,n=16)
    segments=[(.81,.84,.039),(.84,.88,.029),(.88,.915,.021),(.915,.949,.015),(.949,.978,.010),(.978,.999,.005)]
    for z0,z1,r in segments:
        _cylinder(b,'metal',0,0,h*z0,h*z1,s*r,top=.82,n=12)
        b.ring('white',(0,0,h*z0),s*r*1.4,s*r*1.4,s*.005,12)
    for j in range(4):
        a=j*TAU/4
        b.tube('metal',[(w*.12*math.cos(a),d*.12*math.sin(a),h*.802),(0,0,h*.862)],s*.003,4)
    b.box('dark_glass',(0,-d*.449,h*.040),(w*.20,s*.02,h*.06))
    b.box('metal',(0,-d*.468,h*.074),(w*.33,d*.045,h*.007))


def _window(b,x,y,z,w,h,s,arched=False):
    if arched:
        b.arch('dark_glass',x,y,z,w,h,s*.016)
        b.arch('ivory',x,y-s*.008,z,w,h,s*.038,s*.018)
    else:
        b.box('dark_glass',(x,y,z+h/2),(w,s*.018,h))
        for dx in [-w*.55,w*.55]:b.box('stone',(x+dx,y-s*.011,z+h/2),(w*.12,s*.04,h*1.08))
        b.box('ivory',(x,y-s*.014,z+h),(w*1.20,s*.05,s*.032))
    b.box('ivory',(x,y-s*.022,z-s*.014),(w*1.26,s*.08,s*.035))
    b.box('metal',(x,y-s*.026,z+h*.50),(w,s*.015,s*.012))
    b.box('metal',(x,y-s*.027,z+h*.50),(s*.012,s*.015,h*.94))


def _parapet(b,w,d,z,height,mat='stone'):
    s=min(w,d)
    for sign in [-1,1]:
        b.box(mat,(0,sign*d*.47,z+height/2),(w*.96,s*.04,height))
        b.box(mat,(sign*w*.47,0,z+height/2),(s*.04,d*.96,height))
    b.tube('ivory',_rect(w*.97,d*.97,z+height),s*.022,4,True)


def _roof_equipment(b,z,variant=0,water_tank=False):
    w,d,h=b.w,b.d,b.h;s=min(w,d)
    for i in range(2):
        cx=w*(-.20+i*.32);cy=d*.20
        b.box('metal',(cx,cy,z+h*.018),(w*.15,d*.16,h*.036))
        b.box('dark',(cx,cy,z+h*.037),(w*.12,d*.13,h*.004))
        for k in range(4):b.box('white',(cx-w*.047+k*w*.031,cy,z+h*.041),(w*.009,d*.12,h*.005))
    if water_tank:
        cx=w*.21;cy=-d*.13;rz=s*.105;z0=z+h*.035;z1=z+h*.11
        for sx in [-1,1]:
            for sy in [-1,1]:
                b.tube('metal',[(cx+sx*rz*.66,cy+sy*rz*.66,z),(cx+sx*rz*.66,cy+sy*rz*.66,z0)],s*.012,4)
        _cylinder(b,'wood',cx,cy,z0,z1,rz,n=18)
        for j in range(18):
            a=j*TAU/18;b.tube('stone',[(cx+rz*math.cos(a),cy+rz*math.sin(a),z0),(cx+rz*math.cos(a),cy+rz*math.sin(a),z1)],s*.004,4)
        for zz in [z0+h*.01,z1-h*.012]:b.ring('metal',(cx,cy,zz),rz*1.02,rz*1.02,s*.008,18)
        _cylinder(b,'roof',cx,cy,z1,z1+h*.036,rz*1.08,top=.03,n=18)
    else:
        b.box('stone',(-w*.24,-d*.21,z+h*.055),(w*.17,d*.17,h*.11))
        b.box('ivory',(-w*.24,-d*.21,z+h*.114),(w*.20,d*.20,h*.012))


def _masonry(b,brownstone=False):
    w,d,h=b.w,b.d,b.h;s=min(w,d);v=b.variant%6
    wall=h*(.80 if brownstone else .81);floors=4 if brownstone else 4+v%3
    front=-d*.40;bays=3 if brownstone else 3+v%3;pitch=w*.80/bays
    material='wood'if brownstone and v%2==0 else('red'if v in [1,4]else'ivory')
    b.box('stone',(0,0,h*.021),(w*.97,d*.97,h*.042))
    b.box(material,(0,0,wall/2+h*.02),(w*.88,d*.80,wall))
    floor_h=wall/floors
    for level in range(floors):
        z=h*.075+level*floor_h;wh=floor_h*.62
        for j in range(bays):
            x=-w*.40+pitch*(j+.5)
            if level==0 and brownstone and j==0:continue
            _window(b,x,front-d*.006,z,pitch*.57,wh,s,arched=(level==0 or (v==3 and level==floors-1)))
        # Side and back windows are equally modelled so radial placement can face any direction.
        for sign in [-1,1]:
            for j in range(3):
                y=d*(-.28+j*.28)
                b.box('dark_glass',(sign*w*.446,y,z+wh/2),(s*.016,d*.14,wh))
                b.box('ivory',(sign*w*.46,y,z-s*.009),(s*.06,d*.17,s*.028))
            for j in range(bays):
                x=-w*.4+pitch*(j+.5)
                b.box('dark_glass',(x,d*.406,z+wh/2),(pitch*.56,s*.015,wh))
        b.box('stone',(0,0,z+wh+s*.03),(w*.91,d*.85,s*.026))
    # Pilasters and corner quoins frame a richly shadowed street facade.
    for j in range(bays+1):
        x=-w*.40+pitch*j
        b.box('stone',(x,front-d*.025,wall*.51),(pitch*.075,d*.055,wall*.94))
        b.box('ivory',(x,front-d*.038,wall*.93),(pitch*.18,d*.07,s*.06))
    for sign in [-1,1]:
        for j in range(floors*4):
            z=h*.05+(j+.5)*(wall-h*.04)/(floors*4)
            b.box('stone',(sign*w*.439,front,z),(w*.055,d*.07,wall/(floors*4)*.65))
    for z,ww,dd,hh in [(wall+h*.023,.92,.85,.025),(wall+h*.042,.97,.90,.018),(wall+h*.056,.95,.88,.012)]:
        b.box('ivory',(0,0,z),(w*ww,d*dd,h*hh))
    for j in range(2*bays+3):
        x=w*(-.45+j*.90/(2*bays+2))
        b.box('stone',(x,-d*.437,wall+h*.018),(w*.03,d*.08,h*.025))
    roof=wall+h*.068;b.box('roof',(0,0,roof),(w*.87,d*.79,h*.014))
    _parapet(b,w*.93,d*.88,roof,h*.039)
    _roof_equipment(b,roof,b.variant,water_tank=not brownstone and v%2==0)
    if brownstone:
        # Raised entrance stoop, six tread levels, and cast iron railings stay inside the declared depth.
        x=-w*.28
        for j in range(6):
            z=h*.010*(j+1)
            b.box('stone',(x,-d*.405-d*.012*(6-j),z/2),(w*.21,d*.025,z))
        b.arch('dark',x,-d*.415,h*.07,w*.145,floor_h*.66,d*.025)
        b.arch('ivory',x,-d*.426,h*.07,w*.145,floor_h*.66,d*.04,s*.024)
        for sign in [-1,1]:
            xx=x+sign*w*.115
            b.tube('dark',[(xx,-d*.485,h*.052),(xx,-d*.415,h*.114)],s*.009,5)
            for j in range(4):
                yy=-d*.478+j*d*.018
                b.tube('dark',[(xx,yy,h*.012+j*h*.011),(xx,yy,h*.058+j*h*.016)],s*.005,4)
    elif v%3==1:
        # Fine fire escape: open platforms, diagonal stair flights, front guard rails.
        x=w*.20
        for level in range(1,floors):
            z=h*.065+level*floor_h
            b.box('metal',(x,-d*.452,z),(w*.28,d*.085,h*.009))
            b.tube('dark',[(x-w*.14,-d*.487,z+h*.05),(x+w*.14,-d*.487,z+h*.05)],s*.006,4)
            for dx in [-.13,0,.13]:b.tube('dark',[(x+w*dx,-d*.487,z),(x+w*dx,-d*.487,z+h*.05)],s*.006,4)
            if level<floors-1:
                for dx in [-.045,.045]:b.tube('metal',[(x-w*.10+w*dx,-d*.47,z),(x+w*.10+w*dx,-d*.47,z+floor_h)],s*.008,4)
                for j in range(9):b.box('metal',(x-w*.10+j*w*.025,-d*.47,z+j*floor_h/8),(w*.10,d*.025,h*.005))


def _glass_mass(b,cx,cy,w,d,z0,z1,bays=10,body='glass'):
    s=min(b.w,b.d);height=z1-z0
    b.box(body,(cx,cy,(z0+z1)/2),(w,d,height))
    levels=max(5,min(35,round(height/b.h*31)))
    for center,tangent,normal,span in _four_faces(w,d):
        center+=Vector((cx,cy,0));count=max(4,round(bays*span/w))
        for j in range(count+1):
            p=center+tangent*(span*(-.49+j*.98/count))+normal*s*.004
            _wall_box(b,'metal',p+Vector((0,0,(z0+z1)/2)),tangent,s*.009,s*.015,height)
        for j in range(1,levels):
            p=center+normal*s*.004+Vector((0,0,z0+j*height/levels))
            _wall_box(b,'metal',p,tangent,span,s*.014,b.h*.0028)
    b.box('ivory',(cx,cy,z1),(w*1.025,d*1.025,b.h*.009))


def _glass(b):
    w,d,h=b.w,b.d,b.h;s=min(w,d);v=b.variant%5
    b.box('stone',(0,0,h*.025),(w*.98,d*.98,h*.05))
    _glass_mass(b,0,0,w*.90,d*.88,h*.05,h*.17,8,'dark_glass')
    if v==0:
        for ww,dd,z0,z1 in [(.84,.80,.17,.61),(.68,.65,.61,.80),(.49,.48,.80,.94)]:_glass_mass(b,0,0,w*ww,d*dd,h*z0,h*z1,11)
        roof=h*.95
    elif v==1:
        _glass_mass(b,-w*.08,d*.04,w*.71,d*.76,h*.17,h*.93,12,'dark_glass')
        for j in range(8):b.box('white',(-w*.41+j*w*.094,-d*.347,h*.55),(w*.014,d*.027,h*.77))
        roof=h*.94
    elif v==2:
        _glass_mass(b,-w*.18,d*.08,w*.45,d*.66,h*.17,h*.94,7)
        _glass_mass(b,w*.24,-d*.08,w*.32,d*.65,h*.17,h*.74,6,'dark_glass')
        for z in [.35,.57]:b.box('ivory',(w*.24,-d*.08,h*z),(w*.35,d*.69,h*.018))
        roof=h*.95
    elif v==3:
        _glass_mass(b,0,0,w*.77,d*.75,h*.17,h*.91,10)
        for j in range(5):
            z=h*(.24+j*.14);b.box('ivory',(0,-d*.396,z),(w*.80,d*.09,h*.022))
            b.box('green',(0,-d*.415,z+h*.016),(w*.71,d*.045,h*.011))
        b.box('stone',(0,0,h*.94),(w*.72,d*.70,h*.055));roof=h*.97
    else:
        n=28;rings=[]
        for z,f in [(h*.17,1),(h*.94,.86)]:rings.append([(w*.40*f*math.cos(j*TAU/n),d*.39*f*math.sin(j*TAU/n),z)for j in range(n)])
        b.loft('dark_glass',rings,smooth=True)
        for j in range(n):b.tube('metal',[rings[0][j],rings[1][j]],s*.006,4)
        for j in range(26):
            t=j/25;b.ring('metal',(0,0,h*(.17+.77*t)),w*.40*(1-.14*t),d*.39*(1-.14*t),s*.005,28)
        b.ring('ivory',(0,0,h*.946),w*.348,d*.339,s*.018,28);roof=h*.95
    # Small rooftop equipment is contained by the uppermost roof footprint.
    roof_x=-w*.18 if v==2 else 0
    b.box('roof',(roof_x,d*.08,roof+h*.005),(w*.25,d*.23,h*.01))
    for x in [roof_x-w*.07,roof_x+w*.07]:
        b.box('metal',(x,d*.08,roof+h*.023),(w*.10,d*.15,h*.035))
        for k in range(3):b.box('dark',(x-w*.032+k*w*.032,d*.08,roof+h*.042),(w*.012,d*.11,h*.004))
    b.box('dark_glass',(0,-d*.451,h*.10),(w*.21,d*.019,h*.14))
    b.box('metal',(0,-d*.468,h*.175),(w*.36,d*.055,h*.010))


def build(kind,name,parent,collection,materials,w,d,h,variant=0):
    aliases={'empire_state':'empire','empire_state_building':'empire','one_wtc':'onewtc','world_trade':'onewtc',
             'commercial':'masonry','heritage':'masonry','rowhouse':'brownstone','midrise':'glass','tower':'glass'}
    kind=aliases.get(kind,kind)
    assert kind in {'empire','onewtc','masonry','brownstone','glass'},kind
    b=_Batch(name,parent,collection,materials,w,d,h,variant)
    if kind=='empire':_empire(b)
    elif kind=='onewtc':_onewtc(b)
    elif kind=='masonry':_masonry(b)
    elif kind=='brownstone':_masonry(b,True)
    else:_glass(b)
    return b.finish(kind)

