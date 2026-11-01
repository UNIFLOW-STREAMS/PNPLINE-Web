import bpy,math,json,sys
from pathlib import Path
from mathutils import Vector,geometry
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from shipkit import Parts,finish
s=bpy.context.scene;ship=s.objects['A02_SHIP']
col=bpy.data.collections.new('PNPLINE • container vessel');s.collection.children.link(col)
def part(name,parent=None):return Parts('VSL_'+name,parent or ship,col)
M={}
for key,color,rough,metal,coat in [
 ('blue','075D91',.31,.25,.32),('boot','202E3A',.48,.16,0),('red','A73836',.53,.12,0),
 ('white','EAECE6',.42,.15,.18),('pearl','FAF7E9',.32,.23,.2),('deck','A1AEA9',.68,.12,0),
 ('grate','50636A',.55,.34,0),('steel','9DAEB1',.3,.72,.1),('iron','273B43',.41,.51,0),
 ('glass','183B4D',.17,.35,.5),('glint','315B70',.19,.41,.5),('reveal','23383F',.44,.16,0),
 ('orange','DD662C',.44,.12,.17),('green','208B79',.48,.18,0),('brass','AB8152',.42,.61,0),
 ('cobalt','116FA7',.42,.2,.14),('azure','008FC0',.4,.19,.18),('teal','147691',.46,.18,.15),
 ('ivory','D9DDD5',.53,.12,.12),('mist','B7CBD0',.5,.17,.12),('logo cyan','00ABE1',.29,.29,.25),('logo silver','787879',.3,.35,.26)]:
    M[key]=finish(key,color,rough,metal,coat)
blue,red,white,pearl,deck,steel,iron,glass=[M[k] for k in ('blue','red','white','pearl','deck','steel','iron','glass')]
hidden=[]
for o in ship.children_recursive:
    if o.name.startswith(('SHIP_','SF_HULL','SF_BOW_DECK','SF_BRIDGE','SF_CARGO_CORRUGATION','P03_')):
        o.hide_render=True;o.hide_viewport=True;hidden.append(o.name)

# Offset table. X points forward; the crown rises to the bow and stern.
stations=[(-8.05,1.38,1.52),(-7.80,1.72,1.49),(-7.24,2.05,1.43),(-6.38,2.30,1.38),(-4.9,2.46,1.34),(-3.65,2.48,1.33),(3.80,2.48,1.33),(5.05,2.46,1.345),(5.82,2.37,1.38),(6.46,2.13,1.43),(7.10,1.78,1.49),(7.82,1.23,1.55),(8.45,.64,1.61),(8.90,.19,1.65),(9.04,.012,1.66)]
cy=-.17
def slope(i,k):
    if i==0 or i==len(stations)-1:
        a,b=stations[:2] if i==0 else stations[-2:];return (b[k]-a[k])/(b[0]-a[0])
    a,b,c=stations[i-1:i+2];l=(b[k]-a[k])/(b[0]-a[0]);r=(c[k]-b[k])/(c[0]-b[0])
    return 2*l*r/(l+r) if l*r>0 else 0.
def attr(x,k):
    i=next((i for i in range(len(stations)-1) if x<=stations[i+1][0]),len(stations)-2)
    a,b=stations[i:i+2];h=b[0]-a[0];t=max(0,min(1,(x-a[0])/h))
    return (1+2*t)*(1-t)**2*a[k]+t*(1-t)**2*h*slope(i,k)+t*t*(3-2*t)*b[k]+t*t*(t-1)*h*slope(i+1,k)
def width(x):return attr(x,1)
def sheer(x):return attr(x,2)
levels=[(-1.28,.13,-1.18),(-1.20,.45,-.94),(-.99,.72,-.85),(-.65,.87,-.8),(-.40,.936,-.75),(-.30,.949,-.70),(-.235,.956,-.665),(.16,.975,-.49),(.80,.994,-.29),(None,1.,0)]
def skin(x,side,i):
    z,fac,shift=levels[i];tip=max(0,(x-5.5)/(9.04-5.5))**1.6;stern=max(0,(-5.5-x)/2.55)**2
    return (x+tip*shift-stern*shift*.52,cy+side*width(x)*fac,sheer(x) if z is None else z)
xx=[a[0]+(b[0]-a[0])*k/max(2,math.ceil((b[0]-a[0])/.25)) for a,b in zip(stations,stations[1:]) for k in range(max(2,math.ceil((b[0]-a[0])/.25)))]+[stations[-1][0]]
hull=part('Shell · faired plating')
# Shared section vertices keep specular highlights continuous along the hull.
for sign in (-1,1):
    nv=len(levels);v=[skin(x,sign,i) for x in xx for i in range(nv)]
    first=len(hull.f)
    fs=[tuple((k,k+nv,k+nv+1,k+1) if sign<0 else (k+1,k+nv+1,k+nv,k)) for j in range(len(xx)-1) for i in range(nv-1) for k in [j*nv+i]]
    hull.add(v,fs,blue,True)
    for mat in [red,M['boot']]:
        if mat not in hull.mats:hull.mats.append(mat)
    for j in range(len(xx)-1):
        for i in range(nv-1):
            if i<=5:hull.ids[first+j*(nv-1)+i]=hull.mats.index(red if i<5 else M['boot'])
for x,end in [(xx[0],-1),(xx[-1],1)]:
    for i in range(len(levels)-1):
        v=[skin(x,-1,i),skin(x,1,i),skin(x,1,i+1),skin(x,-1,i+1)]
        hull.add(v,[(0,1,2,3) if end>0 else (3,2,1,0)],red if i<5 else M['boot'] if i==5 else blue)
for a,b in zip(xx,xx[1:]):
    hull.add([skin(a,-1,0),skin(a,1,0),skin(b,1,0),skin(b,-1,0)],[(0,1,2,3)],red)
hull.done()
bulb=part('Bulbous forefoot');bulb.oval((8.16,cy,-.82),(.92,.37,.33),red,32,16);bulb.done()
deckpart=part('Weather decks and recessed hold')
def ribbon_surface(xs,ys,z,m):
    vs=[(x,y(x),z(x)) for x in xs for y in ys]
    deckpart.add(vs,[(i,i+2,i+3,i+1) for i in range(0,len(vs)-2,2)],m)
for side in (-1,1):
    edge=lambda x:cy+side*width(x);inside=lambda x:cy+side*max(0,width(x)-.21)
    ribbon_surface(xx,sorted([edge,inside],key=lambda fn:fn(0)),sheer,pearl)
    # Two faces at the top of the blue shell form a painted bulwark, not a decal.
    vs=[Vector(skin(x,side,-1)).lerp(Vector(skin(x,side,-2)),d/(sheer(x)-.80)) for x in xx for d in (.0,.082)]
    deckpart.add([(x,y+side*.004,z) for x,y,z in vs],[(i,i+1,i+3,i+2) for i in range(0,len(vs)-2,2)],white)
    hold=[-4.36]+[x for x in xx if -4.36<x<5.91]+[5.91]
    vs=[(x,inside(x),z) for x in hold for z in (.83,sheer(x))]
    deckpart.add(vs,[(i,i+2,i+3,i+1) for i in range(0,len(vs)-2,2)],deck)
for a,b in [(xx[0],-4.36),(5.91,xx[-1])]:
    xs=[a]+[x for x in xx if a<x<b]+[b]
    ribbon_surface(xs,[lambda x:cy-max(0,width(x)-.055),lambda x:cy+max(0,width(x)-.055)],lambda x:sheer(x)-.035,white)
    x=b if b<0 else a
    deckpart.box((x,cy,(.83+sheer(x)-.065)/2),(.025,2*width(x)-.06,sheer(x)-.065-.83),deck)
ribbon_surface([-4.37,5.92],[lambda x:cy-width(x)+.12,lambda x:cy+width(x)-.12],lambda x:.833,deck)
deckpart.done()

# Exact alpha-traced, closed solids in contact with the plating on each side.
contours=json.loads((R/'scripts/wordmark.json').read_text())
def ylogo(x,z,sgn):
    frac=.975+(z-.16)/.64*(.994-.975) if z<=.8 else .994+(z-.8)/(sheer(x)-.8)*.006
    return cy+sgn*width(x)*frac
for sign in (-1,1):
    for i,loop in enumerate(contours):
        word=part('Raised logo %s %s-%s'%('starboard' if sign<0 else 'port',i+1,'PNPLINE'[i]))
        pts=[Vector(((x-749.5)*.00504,(200-y)*.00504,0)) for x,y in loop]
        # Front faces are triangulated; back face is inset in the hull skin.
        triangles=geometry.tessellate_polygon([pts]);count=len(pts);v=[]
        for relief in (-.014,.034):
            for p in pts:
                x=.15-sign*p.x;z=.713+p.y
                v.append((x,ylogo(x,z,sign)+sign*relief,z))
        fs=[tuple(reversed(t)) for t in triangles]+[tuple(count+j for j in t) for t in triangles]+[(j,(j+1)%count,(j+1)%count+count,j+count) for j in range(count)]
        word.add(v,fs,M['logo cyan' if i<3 else 'logo silver'])
        ob=word.done(.004)
        import bmesh
        bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
        ob['relief_depth']=.048;ob['outline_source']='PNP-LINE.webp / alpha silhouette';ob['glyph']='PNPLINE'[i]

# Steel hatch covers; fixed and mobile cargo meet at z=2.35 in bay 02.
covers=part('Hatch coamings and cargo sockets')
for x in [-2.6,.8,4.2]:
    covers.box((x,-.02,.8415),(3.28,4.00,.017),M['grate'])
covers.done()
exec(compile((R/'scripts/cargo.py').read_text(encoding='utf-8'),'cargo.py','exec'))
exec(compile((R/'scripts/outfit.py').read_text(encoding='utf-8'),'outfit.py','exec'))
for ob in col.objects:
    if ob.name.startswith(('VSL_Accommodation','VSL_Bridge roof')):
        for v in ob.data.vertices:
            v.co.z+=.43*max(0,min(1,(v.co.z-3.44)/.68))
        ob.data.update()
s['vessel_design_revision']='container-ship-v001'
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(R/'pnpline-container-ship-v001.blend'),compress=True)
(R/'review/build.json').write_text(json.dumps(dict(new_objects=[o.name for o in col.objects],replaced=hidden,static_containers=len(units),working_bay=[.8,-1.25,2.35],raised_glyphs=14),indent=2))
print('BUILT',len(col.objects),'items',len(units),'containers',flush=True)
