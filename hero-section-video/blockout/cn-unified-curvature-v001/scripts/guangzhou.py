"""Editable Guangzhou-inspired miniature architecture, batched by material.

Public API: build(kind, name, parent, collection, materials, width, depth,
height). The returned list begins with an Empty root. All meshes live under
that root, are centered in XY, stand on local Z=0, and face negative Y.
No source scene, material, camera, or animation is modified.
"""
import hashlib
import math
from collections import defaultdict
import bpy
from mathutils import Vector

TAU = math.tau
__all__ = ['build']


class _Builder:
    def __init__(self, name, parent, collection, materials, width, depth, height):
        self.name, self.collection, self.materials = name, collection, materials
        self.w, self.d, self.h = map(float, (width, depth, height))
        assert min(self.w, self.d, self.h) > 0
        self.batches = defaultdict(lambda: [[], [], []])
        self.root = bpy.data.objects.new(name, None)
        collection.objects.link(self.root)
        self.root.parent = parent
        self.root.empty_display_type = 'PLAIN_AXES'
        self.root.empty_display_size = min(self.w, self.d) * .15

    def mesh(self, vertices, faces, material, smooth=False):
        batch = self.batches[material]
        offset = len(batch[0])
        batch[0].extend(tuple(v) for v in vertices)
        batch[1].extend(tuple(offset + i for i in face) for face in faces)
        batch[2].extend([smooth] * len(faces))

    def box(self, center, size, material, angle=0):
        cx, cy, cz = center
        sx, sy, sz = (x / 2 for x in size)
        c, s = math.cos(angle), math.sin(angle)
        verts = [(cx + c*x - s*y, cy + s*x + c*y, cz + z)
                 for x, y, z in [(-sx,-sy,-sz),(-sx,-sy,sz),(-sx,sy,-sz),(-sx,sy,sz),
                                 (sx,-sy,-sz),(sx,-sy,sz),(sx,sy,-sz),(sx,sy,sz)]]
        self.mesh(verts, [(2,6,4,0),(5,7,3,1),(4,5,1,0),(3,7,6,2),(1,3,2,0),(6,7,5,4)], material)

    def tube(self, points, radius, material, sides=6, closed=False):
        ps = [Vector(p) for p in points]
        if len(ps) < 2 or radius <= 0:
            return
        vertices, faces = [], []
        for i, p in enumerate(ps):
            before = ps[(i-1) % len(ps)] if closed or i else ps[0]
            after = ps[(i+1) % len(ps)] if closed or i < len(ps)-1 else ps[-1]
            tangent = (after-before).normalized()
            reference = Vector((0,0,1)) if abs(tangent.z) < .9 else Vector((1,0,0))
            a = tangent.cross(reference).normalized()
            b = tangent.cross(a).normalized()
            for j in range(sides):
                vertices.append(p + radius*(a*math.cos(TAU*j/sides)+b*math.sin(TAU*j/sides)))
        links = len(ps) if closed else len(ps)-1
        for i in range(links):
            ni = (i+1) % len(ps)
            for j in range(sides):
                nj = (j+1) % sides
                faces.append((i*sides+j,i*sides+nj,ni*sides+nj,ni*sides+j))
        if not closed:
            faces.extend([tuple(range(sides-1,-1,-1)), tuple((len(ps)-1)*sides+j for j in range(sides))])
        self.mesh(vertices, faces, material, smooth=True)

    def ring(self, center, rx, ry, radius, material, segments=32):
        self.tube([(center[0]+rx*math.cos(TAU*i/segments), center[1]+ry*math.sin(TAU*i/segments), center[2])
                   for i in range(segments)], radius, material, sides=4, closed=True)

    def cylinder(self, center, radius, height, material, sides=16):
        self.tube([(center[0],center[1],center[2]-height/2),
                   (center[0],center[1],center[2]+height/2)], radius, material, sides=sides)

    def loft(self, rings, material, caps=True, smooth=False):
        n = len(rings[0]); vertices = [p for ring in rings for p in ring]
        faces = [(i*n+j,i*n+(j+1)%n,(i+1)*n+(j+1)%n,(i+1)*n+j)
                 for i in range(len(rings)-1) for j in range(n)]
        if caps:
            faces += [tuple(range(n-1,-1,-1)), tuple((len(rings)-1)*n+j for j in range(n))]
        self.mesh(vertices, faces, material, smooth)

    def arch(self, x, y, bottom, width, height, depth, material, thickness=0):
        """Solid arch panel or a true open extruded arch surround."""
        radius = width/2
        radius_z = min(radius,height*.95)
        spring = bottom+height-radius_z
        profile = [(x-radius,bottom),(x-radius,spring)]
        profile += [(x+radius*math.cos(math.pi-i*math.pi/12),spring+radius_z*math.sin(math.pi-i*math.pi/12)) for i in range(1,13)]
        profile += [(x+radius,bottom)]
        if thickness <= 0:
            n = len(profile)
            vs = [(xx,yy,zz) for yy in [y-depth/2,y+depth/2] for xx,zz in profile]
            self.mesh(vs, [tuple(range(n-1,-1,-1)), tuple(range(n,2*n))] +
                      [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)], material)
            return
        # Vertical piers plus semicircular voussoirs leave the arcade open.
        pier_h = spring-bottom
        for side in [-1,1]:
            self.box((x+side*(radius+thickness/2),y,bottom+pier_h/2),
                     (thickness,depth,pier_h),material)
        vs=[]; fs=[]
        for yy in [y-depth/2,y+depth/2]:
            for rr in [radius,radius+thickness]:
                vs.extend((x+rr*math.cos(i*math.pi/16),yy,spring+(radius_z+rr-radius)*math.sin(i*math.pi/16)) for i in range(17))
        for i in range(16):
            fs.extend([(i,i+1,18+i,17+i),(34+i,51+i,52+i,35+i),
                       (i,34+i,35+i,i+1),(17+i,18+i,52+i,51+i)])
        fs += [(0,17,51,34),(16,50,67,33)]
        self.mesh(vs,[tuple(reversed(face))for face in fs],material)

    def finish(self, kind):
        self.root['guangzhou_kind'] = kind
        self.root['nominal_dimensions'] = (self.w,self.d,self.h)
        self.root['front_axis'] = '-Y'
        objects = [self.root]
        # Keep cornices and balconies inside the advertised placement footprint.
        all_vertices=[v for batch in self.batches.values()for v in batch[0]]
        lo=[min(v[i]for v in all_vertices)for i in range(3)]
        hi=[max(v[i]for v in all_vertices)for i in range(3)]
        xy_scale=[min(1.0,extent/(2*max(abs(lo[i]),abs(hi[i]),1e-9)))for i,extent in enumerate([self.w,self.d])]
        z_offset=-min(0.0,lo[2]); z_scale=min(1.0,self.h/max(hi[2]+z_offset,1e-9))
        for key, (vertices, faces, smooth) in sorted(self.batches.items()):
            if not faces:
                continue
            mesh = bpy.data.meshes.new(self.name+'__'+key)
            vertices=[(x*xy_scale[0],y*xy_scale[1],(z+z_offset)*z_scale)for x,y,z in vertices]
            mesh.from_pydata(vertices, [], faces); mesh.update()
            mesh.materials.append(self.materials.get(key, self.materials['stone']))
            for polygon, value in zip(mesh.polygons,smooth):
                polygon.use_smooth=value
            obj=bpy.data.objects.new(mesh.name,mesh); self.collection.objects.link(obj)
            obj.parent=self.root; obj['architectural_material_group']=key
            objects.append(obj)
        return objects


def _chamfer(w,d,z,cut=.16,dx=0,dy=0):
    x,y=w/2,d/2; c=min(w,d)*cut
    return [(dx+xx,dy+yy,z)for xx,yy in [(-x+c,-y),(x-c,-y),(x,-y+c),(x,y-c),
                                       (x-c,y),(-x+c,y),(-x,y-c),(-x,-y+c)]]


def _canton(b):
    w,d,h=b.w,b.d,b.h; small=min(w,d)
    b.loft([[(w*.49*math.cos(TAU*i/40),d*.49*math.sin(TAU*i/40),z)for i in range(40)]
            for z in [0,h*.025]],'stone',smooth=True)
    levels=36; strands=24; tower_top=.835*h
    def radius(t):
        return .13 + (.30*((t-.58)/.58)**2 if t<=.58 else .125*((t-.58)/.42)**2)
    def point(t,theta):
        return (w*radius(t)*math.cos(theta),d*radius(t)*math.sin(theta),h*.025+t*(tower_top-h*.025))
    core=[]
    for i in range(25):
        t=i/24; r=min(radius(t)*.57,.115)
        core.append([(w*r*math.cos(TAU*j/32),d*r*math.sin(TAU*j/32),h*.027+t*(tower_top-h*.035))for j in range(32)])
    b.loft(core,'dark_glass',smooth=True)
    for side in [-1,1]:
        for strand in range(strands):
            points=[point(i/levels,TAU*strand/strands+side*1.95*(i/levels-.5))for i in range(levels+1)]
            b.tube(points,small*.009,'white',sides=6)
    for i in range(43):
        t=i/42; p=point(t,0)
        b.ring((0,0,p[2]),w*radius(t),d*radius(t),small*.006,'white',segments=36)
    for t in [.70,.735,.78,.815]:
        b.ring((0,0,h*t),w*.14,d*.14,small*.018,'metal')
    b.cylinder((0,0,h*.855),small*.105,h*.04,'glass',32)
    b.ring((0,0,h*.875),small*.108,small*.108,small*.012,'white')
    b.cylinder((0,0,h*.9325),small*.022,h*.115,'metal',12)
    b.cylinder((0,0,h*.992),small*.009,h*.016,'white',8)
    for z in [.895,.918,.941,.964]:
        b.cylinder((0,0,h*z),small*.025,h*.006,'white',12)
    # A small pennant follows the reference without dominating the lattice.
    b.mesh([(small*.02,0,h*.977),(small*.36,-small*.018,h*.963),(small*.34,-small*.008,h*.921),(small*.02,0,h*.935)],[(0,1,2,3)],'red')
    points=[]
    for i in range(10):
        r=small*(.038 if i%2==0 else .016); a=math.pi/2+TAU*i/10
        points.append((small*.092+r*math.cos(a),-small*.024,h*.954+r*math.sin(a)))
    b.mesh(points,[tuple(range(10))],'gold')


def _ifc(b):
    w,d,h=b.w,b.d,b.h; small=min(w,d); n=36
    b.box((0,0,h*.018),(w*.96,d*.96,h*.036),'stone')
    levels=44
    def point(t,j):
        angle=TAU*j/n; factor=1-.13*t+.025*math.sin(math.pi*t)
        radius=.41*(1+.065*math.cos(3*angle))
        return (w*radius*factor*math.cos(angle),d*radius*factor*math.sin(angle),h*(.035+.93*t))
    rings=[[point(i/levels,j)for j in range(n)]for i in range(levels+1)]
    b.loft(rings,'dark_glass',smooth=True)
    for j in range(n):
        b.tube([point(i/levels,j)for i in range(levels+1)],small*.004,'metal',sides=4)
    for i in range(1,levels+1):
        b.tube(rings[i],small*.0035,'glass',sides=4,closed=True)
    for t in [.23,.48,.72,.955]:
        b.tube([point(t,j)for j in range(n)],small*.008,'metal',sides=4,closed=True)
    b.loft([[tuple((p[0]*.92,p[1]*.92,h*z))for p in rings[-1]]for z in [.965,.985]],'metal',smooth=True)
    b.ring((0,0,h*.987),w*.29,d*.29,small*.012,'white')
    b.cylinder((0,0,h*.991),small*.065,h*.018,'dark',12)


def _ctf(b):
    w,d,h=b.w,b.d,b.h; small=min(w,d)
    b.box((0,0,h*.018),(w,d,h*.036),'stone')
    stages=[(.035,.32,1),(.32,.62,.93),(.62,.84,.84),(.84,.95,.72)]
    for bottom,top,factor in stages:
        ww,dd=w*.84*factor,d*.84*factor
        b.loft([_chamfer(ww,dd,h*bottom),_chamfer(ww,dd,h*top)],'glass')
        floors=max(3,round((top-bottom)*60))
        for level in range(floors+1):
            z=h*(bottom+(top-bottom)*level/floors)
            b.tube(_chamfer(ww*1.012,dd*1.012,z),small*.005,'ivory',sides=4,closed=True)
        for side in [-1,1]:
            for j in range(9):
                x=ww*(-.4+j*.1)
                b.box((x,side*(dd/2+.005*small),h*(bottom+top)/2),(small*.014,small*.018,h*(top-bottom)),'white')
            for j in range(7):
                y=dd*(-.375+j*.125)
                b.box((side*(ww/2+.005*small),y,h*(bottom+top)/2),(small*.018,small*.014,h*(top-bottom)),'white')
        b.tube(_chamfer(ww*1.025,dd*1.025,h*top),small*.013,'ivory',sides=4,closed=True)
    b.box((0,0,h*.956),(w*.54,d*.54,h*.012),'dark')
    for side in [-1,1]:
        b.box((side*w*.29,0,h*.974),(w*.035,d*.61,h*.052),'ivory')
        b.box((0,side*d*.29,h*.974),(w*.61,d*.035,h*.052),'ivory')
    for x in [-.16,0,.16]:
        b.box((x*w,0,h*.971),(w*.09,d*.22,h*.024),'metal')


def _faceted(b):
    w,d,h=b.w,b.d,b.h; small=min(w,d)
    b.box((0,0,h*.022),(w*.95,d*.95,h*.044),'stone')
    levels=[.045,.27,.52,.76,.96]
    rings=[]
    for t in levels:
        ring=_chamfer(w*(.84-.14*t),d*(.84-.10*t),h*t,cut=.20,dx=w*.07*t)
        if t==levels[-1]:
            ring=[(x,y,z+h*.032*x/w-h*.025*y/d)for x,y,z in ring]
        rings.append(ring)
    for i in range(len(rings)-1):
        for j in range(8):
            a,bp,c,dv=rings[i][j],rings[i][(j+1)%8],rings[i+1][(j+1)%8],rings[i+1][j]
            b.mesh([a,bp,c,dv],[(0,1,2)],'glass' if (i+j)%2 else 'dark_glass')
            b.mesh([a,bp,c,dv],[(0,2,3)],'dark_glass' if (i+j)%2 else 'glass')
    b.mesh(rings[-1],[tuple(range(8))],'metal')
    for j in range(8):
        b.tube([ring[j]for ring in rings],small*.009,'metal',sides=5)
    for i in range(len(rings)-1):
        for j in [0,2,4,6]:
            b.tube([rings[i][j],rings[i+1][(j+1)%8]],small*.008,'white',sides=5)
            b.tube([rings[i][(j+1)%8],rings[i+1][j]],small*.008,'white',sides=5)
    for step in range(1,42):
        t=step/42; z=h*(.045+.91*t)
        b.tube(_chamfer(w*(.84-.14*t),d*(.84-.10*t),z,cut=.20,dx=w*.07*t),small*.0028,'metal',sides=4,closed=True)
    b.tube(rings[-1],small*.014,'white',sides=5,closed=True)


def _shells(b):
    w,d,h=b.w,b.d,b.h; small=min(w,d)
    b.loft([[(w*.49*math.cos(TAU*i/40),d*.49*math.sin(TAU*i/40),z)for i in range(40)]for z in [0,.045*h]],'paving',smooth=True)
    for index,(cx,cy,ww,dd,hh)in enumerate([(-.245*w,-.065*d,.43*w,.67*d,.78*h),(.22*w,.055*d,.46*w,.78*d,.94*h)]):
        n=40; levels=24; lower=-.72
        def point(i,j):
            t=i/levels; phi=math.asin(lower)+(math.pi/2-math.asin(lower))*t
            z=hh*(math.sin(phi)-lower)/(1-lower)+h*.045
            radius=max(.002,math.cos(phi))**.88
            angle=TAU*j/n
            return (cx+ww*.5*radius*math.cos(angle)+ww*.11*t*t,cy+dd*.5*radius*math.sin(angle),z)
        rings=[[point(i,j)for j in range(n)]for i in range(levels+1)]
        b.loft(rings,'metal',smooth=True)
        for i in range(1,levels):
            b.tube(rings[i],small*.003,'white',sides=4,closed=True)
        for j in range(0,n,5):
            b.tube([point(i,j)for i in range(levels)],small*.0035,'ivory',sides=4)
        front=cy-dd*.35
        b.arch(cx,front,h*.055,ww*.45,hh*.19,dd*.055,'dark_glass')
        b.arch(cx,front-dd*.01,h*.055,ww*.45,hh*.19,dd*.065,'white',thickness=small*.016)
    for i in range(3):
        b.box((0,-d*(.46-.035*i),h*(.008+.012*i)),(w*.34,d*.07,h*(.016+.024*i)),'ivory')


def _roof(b,cx,cy,width,depth,eave,rise,material='roof',ornate=False):
    """Swept tiled roof with raised corners, ridge and visible rafter fascia."""
    nx,ny=12,12
    def point(ix,iy):
        x=-width/2+width*ix/nx; y=-depth/2+depth*iy/ny
        t=abs(y)/(depth/2); edge=abs(x)/(width/2)
        z=eave+rise*(1-t**.68+.22*t**8+.15*edge**8*t**4)
        return (cx+x,cy+y,z)
    vs=[point(ix,iy)for ix in range(nx+1)for iy in range(ny+1)]
    fs=[]
    for ix in range(nx):
        for iy in range(ny):
            a=ix*(ny+1)+iy; fs.append((a,a+ny+1,a+ny+2,a+1))
    b.mesh(vs,fs,material)
    thick=min(width,depth)*.012
    for iy in [0,ny]:
        ps=[point(ix,iy)for ix in range(nx+1)]
        b.tube(ps,thick*1.5,'red',sides=5)
        b.tube([(x,y,z+thick*1.5)for x,y,z in ps],thick,'stone',sides=5)
    for ix in range(nx+1):
        b.tube([point(ix,iy)for iy in range(ny+1)],thick*.48,'stone',sides=4)
    for ix in [0,nx]:
        b.tube([(x,y,z+thick*1.5)for x,y,z in [point(ix,iy)for iy in range(ny+1)]],thick*2,'stone',sides=6)
    b.tube([(cx-width*.48,cy,eave+rise*1.025),(cx,cy,eave+rise*1.045),(cx+width*.48,cy,eave+rise*1.025)],thick*2.3,'stone',sides=6)
    if ornate:
        for j in range(9):
            x=cx+width*(-.42+j*.105)
            b.cylinder((x,cy,eave+rise*1.14),thick*2.3,rise*.18,'ivory',8)
            b.box((x,cy,eave+rise*1.23),(thick*4,thick*4,rise*.07),'red')
        for side in [-1,1]:
            # Curving ridge-end dragons/finials read clearly at miniature scale.
            b.tube([(cx+side*width*.38,cy,eave+rise*1.04),
                    (cx+side*width*.47,cy,eave+rise*1.12),
                    (cx+side*width*.5,cy,eave+rise*1.32)],thick*2,'stone',sides=6)


def _lingnan(b):
    w,d,h=b.w,b.d,b.h; small=min(w,d)
    b.box((0,0,h*.025),(w,d,h*.05),'stone')
    b.box((0,0,h*.055),(w*.92,d*.91,h*.03),'paving')
    halls=[(0,-d*.285,w*.88,d*.245,h*.43,h*.26),
           (0,d*.04,w*.72,d*.23,h*.53,h*.29),
           (0,d*.325,w*.78,d*.235,h*.59,h*.28)]
    for index,(x,y,ww,dd,wall,roofrise)in enumerate(halls):
        bottom=h*.07
        b.box((x,y,(bottom+wall)/2),(ww*.9,dd*.84,wall-bottom),'ivory')
        b.box((x,y,h*.105),(ww*.94,dd*.92,h*.07),'stone')
        for j in range(7):
            xx=x+ww*(-.38+j*.1266667)
            b.box((xx,y-dd*.435,(bottom+wall)/2),(ww*.034,dd*.055,wall-bottom),'red')
            if j<6:
                bx=xx+ww*.0633
                b.arch(bx,y-dd*.438,h*.12,ww*.085,wall*.62,dd*.045,'dark')
                b.arch(bx,y-dd*.456,h*.12,ww*.085,wall*.62,dd*.03,'stone',thickness=ww*.012)
        b.box((x,y-dd*.46,wall*.92),(ww*.88,dd*.055,h*.042),'red')
        _roof(b,x,y,ww,dd,wall,roofrise,ornate=True)
        # Tall flanking fire walls and paired curled gable crests.
        for side in [-1,1]:
            xx=x+side*ww*.455
            b.box((xx,y,wall*.63),(ww*.035,dd*.87,wall*1.04),'stone')
            crest=[(xx,y-dd*.48,wall+roofrise*.36),(xx,y-dd*.32,wall+roofrise*.82),
                   (xx,y-dd*.18,wall+roofrise*.65),(xx,y,wall+roofrise*1.08),
                   (xx,y+dd*.18,wall+roofrise*.65),(xx,y+dd*.32,wall+roofrise*.82),(xx,y+dd*.48,wall+roofrise*.36)]
            b.tube(crest,small*.011,'ivory',sides=6)
    for side in [-1,1]:
        xx=side*w*.42
        b.box((xx,d*.06,h*.215),(w*.12,d*.43,h*.29),'ivory')
        _roof(b,xx,d*.06,w*.15,d*.46,h*.36,h*.15)
    for step in range(3):
        b.box((0,-d*(.48-.018*step),h*(.0125+.015*step)),(w*.28,d*.05,h*(.025+.03*step)),'ivory')


def _pagoda(b):
    w,d,h=b.w,b.d,b.h; radius=min(w,d)*.45
    levels=7; base=h*.065; pitch=h*.115
    b.cylinder((0,0,h*.023),radius*1.08,h*.046,'stone',8)
    b.cylinder((0,0,h*.052),radius*.94,h*.024,'ivory',8)
    for level in range(levels):
        r=radius*(1-.074*level); z=base+level*pitch
        inner=r*.64
        b.cylinder((0,0,z+pitch*.32),inner,pitch*.64,'red',8)
        b.cylinder((0,0,z+pitch*.045),r*.89,pitch*.09,'wood',8)
        # Dark inset windows and pale jambs on each octagonal wall.
        for j in range(8):
            a=TAU*(j+.5)/8; tangent=Vector((-math.sin(a),math.cos(a),0)); normal=Vector((math.cos(a),math.sin(a),0))
            center=normal*(inner*math.cos(math.pi/8)+.002)
            ww=r*.25; hh=pitch*.35; zz=z+pitch*.34
            points=[center+tangent*x+Vector((0,0,zz+dz))for x,dz in [(-ww/2,-hh/2),(ww/2,-hh/2),(ww/2,hh/2),(-ww/2,hh/2)]]
            b.mesh(points,[(0,1,2,3)],'dark')
            b.tube(points, r*.013,'ivory',sides=4,closed=True)
            for t in [-.34,0,.34]:
                p=center+tangent*(ww*t)
                b.tube([(p.x,p.y,zz-hh/2),(p.x,p.y,zz+hh/2)],r*.009,'gold',sides=4)
        roof=[]
        for t in [0,.28,.55,.8,1]:
            rr=r*(.30+.70*t); zz=z+pitch*(.95-.35*t+.16*t**6)
            ring=[]
            for j in range(32):
                a=TAU*j/32; local=(a+math.pi/8)%(math.pi/4)-math.pi/8
                radial=rr*math.cos(math.pi/8)/math.cos(local)
                lift=pitch*.07*abs(math.cos(4*a))**8*t**4
                ring.append((radial*math.cos(a),radial*math.sin(a),zz+lift))
            roof.append(ring)
        # Build from outer eave toward ridge so the open roof faces upward.
        b.loft(list(reversed(roof)),'roof',caps=False)
        b.tube(roof[-1],r*.021,'red',sides=5,closed=True)
        b.tube([(x*.91,y*.91,z+pitch*.22)for x,y,_ in roof[-1]],r*.012,'gold',sides=4,closed=True)
        for j in range(16):
            a=TAU*j/16; rr=r*.84
            b.tube([(rr*math.cos(a),rr*math.sin(a),z+pitch*.04),(rr*math.cos(a),rr*math.sin(a),z+pitch*.22)],r*.011,'red',sides=5)
    z=base+(levels-1)*pitch+pitch*.95
    b.cylinder((0,0,(z+h*.98)/2),radius*.032,h*.98-z,'gold',12)
    for t,rr in [(0,.10),(.27,.075),(.53,.052),(.78,.03)]:
        b.cylinder((0,0,z+(h*.98-z)*t),radius*rr,h*.012,'gold',12)
    b.cylinder((0,0,h*.991),radius*.015,h*.018,'gold',8)


def _qilou(b):
    w,d,h=b.w,b.d,b.h; small=min(w,d)
    seed=int(hashlib.sha256(b.name.encode('utf-8')).hexdigest()[:8],16)
    bays=3+(seed%2); upper=2+(seed//3%2); floor=h*.79/(upper+1)
    b.root['qilou_variant']=seed%12
    b.box((0,0,h*.02),(w,d,h*.04),'stone')
    b.box((0,d*.13,floor/2+h*.035),(w*.92,d*.66,floor),'ivory')
    b.box((0,0,(floor+h*.86)/2),(w*.92,d*.88,h*.86-floor),'ivory' if seed%3 else 'stone')
    spacing=w*.84/bays; arch_width=spacing*.63
    for j in range(bays):
        x=-w*.42+spacing*(j+.5)
        b.arch(x,-d*.435,h*.04,arch_width,floor*.84,d*.17,'ivory',thickness=spacing*.11)
        b.arch(x,-d*.21,h*.04,arch_width*.88,floor*.78,d*.025,'dark_glass')
        for side in [-1,1]:
            xx=x+side*(arch_width/2+spacing*.06)
            b.box((xx,-d*.435,h*.075),(spacing*.16,d*.2,h*.07),'stone')
            b.box((xx,-d*.435,floor*.69),(spacing*.18,d*.19,h*.035),'ivory')
    for level in range(upper):
        bottom=floor*(level+1)+h*.04; window_h=floor*.64
        for j in range(bays):
            x=-w*.42+spacing*(j+.5); ww=spacing*.57
            if (seed+level)%2:
                b.arch(x,-d*.45,bottom,ww,window_h,d*.018,'dark_glass')
                b.arch(x,-d*.463,bottom,ww,window_h,d*.028,'white',thickness=spacing*.045)
            else:
                b.box((x,-d*.45,bottom+window_h/2),(ww,d*.018,window_h),'dark_glass')
                for sx in [-1,1]:b.box((x+sx*ww*.55,-d*.463,bottom+window_h/2),(spacing*.045,d*.035,window_h*1.07),'white')
                for zz in [bottom,bottom+window_h]:b.box((x,-d*.463,zz),(ww*1.18,d*.045,h*.025),'white')
            b.box((x,-d*.477,bottom+window_h*.48),(ww,d*.025,h*.012),'ivory')
            b.box((x,-d*.477,bottom+window_h*.48),(spacing*.027,d*.025,window_h),'ivory')
            b.box((x,-d*.483,bottom-h*.018),(ww*1.3,d*.085,h*.032),'stone')
            b.box((x,-d*.483,bottom+window_h+h*.022),(ww*1.35,d*.075,h*.027),'ivory')
            if level==0 and (j+seed)%2==0:
                b.box((x,-d*.49,bottom-h*.02),(ww*1.32,d*.15,h*.025),'ivory')
                b.box((x,-d*.55,bottom+h*.07),(ww*1.3,d*.022,h*.018),'metal')
                for post in range(6):b.box((x+ww*(-.56+post*.224),-d*.55,bottom+h*.033),(w*.012,d*.016,h*.075),'metal')
        # Side elevations have separate recessed windows and projecting sills.
        for side in [-1,1]:
            for j in range(3):
                y=d*(-.25+j*.25)
                b.box((side*w*.467,y,bottom+window_h/2),(w*.016,d*.14,window_h),'dark_glass')
                for yy in [y-d*.081,y+d*.081]:b.box((side*w*.48,yy,bottom+window_h/2),(w*.028,d*.018,window_h*1.07),'white')
                b.box((side*w*.48,y,bottom-h*.012),(w*.045,d*.19,h*.025),'ivory')
    for j in range(bays+1):
        x=-w*.42+spacing*j
        b.box((x,-d*.46,h*.52),(spacing*.065,d*.04,h*.64),'stone')
        for z in [floor+h*.035,h*.82]:b.box((x,-d*.475,z),(spacing*.13,d*.065,h*.032),'ivory')
    for z,sz in [(floor+h*.025,.027),(.855*h,.045),(.885*h,.025)]:
        b.box((0,0,z),(w*.98,d*.96,h*sz),'ivory')
    b.box((0,0,h*.895),(w*.86,d*.82,h*.022),'roof')
    # Perimeter rooftop balustrade and sculpted central pediment.
    for side in [-1,1]:
        b.box((0,side*d*.43,h*.943),(w*.94,d*.035,h*.023),'ivory')
        for j in range(bays*3+1):
            x=w*(-.44+.88*j/(bays*3))
            b.box((x,side*d*.43,h*.916),(w*.021,d*.025,h*.055),'ivory')
        b.box((side*w*.45,0,h*.943),(w*.035,d*.88,h*.023),'ivory')
        for j in range(7):b.box((side*w*.45,d*(-.4+.8*j/6),h*.916),(w*.025,d*.025,h*.055),'ivory')
    if seed%2:
        ped=[(-w*.19,-d*.455,h*.94),(w*.19,-d*.455,h*.94),(0,-d*.455,h*.998)]
        b.mesh(ped,[(0,1,2)],'ivory'); b.tube(ped,small*.012,'white',sides=5,closed=True)
    else:
        b.arch(0,-d*.452,h*.93,w*.29,h*.068,d*.045,'ivory')
    for side in [-1,1]:
        x=side*w*.42
        b.cylinder((x,-d*.42,h*.974),small*.032,h*.042,'stone',10)
        b.cylinder((x,-d*.42,h*.995),small*.043,h*.01,'ivory',10)


_KINDS={'canton':_canton,'ifc':_ifc,'ctf':_ctf,'faceted':_faceted,
        'shells':_shells,'lingnan':_lingnan,'pagoda':_pagoda,'qilou':_qilou}


def build(kind, name, parent, collection, materials, width, depth, height):
    """Build one independent editable asset; callers place its returned root."""
    if kind not in _KINDS:
        raise ValueError('Unknown Guangzhou kind: '+str(kind))
    builder=_Builder(name,parent,collection,materials,width,depth,height)
    _KINDS[kind](builder)
    return builder.finish(kind)
