def wheel_geometry(p,half,side,front):
    n=64
    # Turn the tyre shoulder, sidewall, recessed bead and pressed alloy rim about the live axle.
    def lathe(profile,materials,smooth=True):
        rings=[[(radius*cos(t*2*pi/n),radius*sin(t*2*pi/n),side*ax) for t in range(n)] for radius,ax in profile]
        v=[co for ring in rings for co in ring]
        fs=[(j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k) for j in range(len(profile)-1) for k in range(n)]
        first=len(p.ids);p.add(v,fs,materials[0],smooth)
        for mat in materials:
            if mat not in p.mats:p.mats.append(mat)
        for j,mat in enumerate(materials):
            for k in range(n):p.ids[first+j*n+k]=p.mats.index(mat)
    prof=[(.212,-half+.011),(.315,-half),(.37,-half+.011),(.392,-half+.028),(.400,-half+.045),
          (.400,-.033),(.394,-.030),(.394,-.023),(.400,-.019),(.400,.019),(.394,.023),(.394,.030),(.400,.033),
          (.400,half-.045),(.392,half-.028),(.370,half-.011),(.323,half),(.315,half+.002),(.299,half-.002),(.228,half-.013),(.211,half-.014)]
    lathe(prof,[tread if i in (5,6,9,10) else rubber for i in range(len(prof)-1)])
    prof=[(.001,-half+.012),(.223,-half+.012),(.223,half-.012),(.231,half-.007),(.232,half+.006),(.214,half+.012),(.194,half-.001),(.174,half-.024),(.142,half-.039),(.086,half-.027),(.001,half-.027)]
    lathe(prof,[steel,steel,alloy,alloy,bright,alloy,alloy,alloy,alloy,alloy])
    p.rod((0,0,side*(half-.030)),(0,0,side*(half+.018)),.097,steel,32,.088)
    p.rod((0,0,side*(half+.018)),(0,0,side*(half+.028)),.077,alloy if front else steel,32,.072)
    for i in range(10):
        a=2*pi*i/10;x=.120*cos(a);y=.120*sin(a)
        p.rod((x,y,side*(half-.026)),(x,y,side*(half-.004)),.013,bright,6)
        a+=pi/10;x=.170*cos(a);y=.170*sin(a)
        p.rod((x,y,side*(half-.033)),(x,y,side*(half-.018)),.018,black,14)

wheel_names=[];shared={}
for n in ('A03_TRACTOR','A03_TRAILER','A04_PRIMARY','A05_SECONDARY'):
    parent=w[n]
    for o in list(parent.children):
        if 'WHEEL' not in o.name:continue
        side=-1 if o.location.y>0 else 1
        h=max(abs(v.co.z) for v in o.data.vertices)
        radius=max(math.hypot(v.co.x,v.co.y) for v in o.data.vertices)
        assert abs(radius-.4)<.0003 and .10<h<.14,(o.name,radius,h)
        key=(round(h,5),side,o.location.x>.9)
        if key not in shared:
            p=P('machined road wheel '+str(key),None);wheel_geometry(p,h,side,key[2])
            temporary=p.done();shared[key]=temporary.data
            bpy.data.objects.remove(temporary,do_unlink=True)
        o.data=shared[key]
        wheel_names.append(o.name)

def axle(p,x,z):
    p.rod((x,-.82,z),(x,.82,z),.077,steel,16)
def fender(p,x,z,sy,colour):
    # The lip follows the tyre, exposing its face and preserving suspension travel.
    aa=[math.radians(9+i*162/26) for i in range(27)]
    r=.438
    vs=[(x+cos(a)*(r+dr),sy*y,z+sin(a)*(r+dr)) for a in aa for y,dr in [(.746,0),(.984,0),(.984,.032),(.746,.032)]]
    p.add(vs,[(4*i+j,4*i+(j+1)%4,4*i+4+(j+1)%4,4*i+4+j) for i in range(26) for j in range(4)],colour)
def bumper(p,x,z):
    p.box((x,0,z),(.083,1.53,.108),alloy)
    for sy in (-1,1):
        p.box((x,sy*.655,z+.116),(.087,.276,.108),black)
        for k,mat in enumerate((red,amber,lamp)):
            p.box((x-.048,sy*(.573+k*.079),z+.116),(.016,.066,.064),mat)
    p.box((x-.05,0,z+.011),(.012,.247,.065),ivory)

for n,tag,xs,rear,front in [('A03_TRACTOR','Inbound tractor',[0,1.65],-.53,1.99),('A03_TRAILER','Container chassis',[-.5,.5],-1.60,1.6),
                              ('A04_PRIMARY','Dispatch',[-1.3,1.5],-1.99,2.15),('A05_SECONDARY','Relay',[-1.3,1.5],-1.99,2.15)]:
    unit=w[n];p=P(tag+' ladder frame and running gear',unit);tractor=n=='A03_TRACTOR';trailer=n=='A03_TRAILER'
    z=1.10
    for sy in (-1,1):
        p.box(((rear+front)/2,sy*.49,1.30),(front-rear,.106,.208),steel)
        p.box(((rear+front)/2,sy*.49,1.39),(front-rear,.166,.032),steel)
        if trailer:
            p.box((0,sy*.676,1.612),(3.19,.093,.235),navy)
            p.box((0,sy*.676,1.741),(3.19,.126,.035),alloy)
            for a in (-1.49,1.49):p.box((a,sy*.681,1.774),(.212,.138,.052),amber)
        if not tractor:
            for x in (-1.32,-.84,-.36,.12,.60):
                p.box((x,sy*(.727 if trailer else .845),1.684 if trailer else 1.461),(.188,.012,.035),red if x<-.6 else bright)
        if not trailer:
            for h in (1.105,1.251):
                p.box((.60 if tractor else .90,sy*.811,h),(.31 if tractor else .30,.174,.044),alloy)
                for j in range(5):p.box(((.47 if tractor else .77)+j*.058,sy*.82,h+.025),(.018,.132,.009),black)
            tx=.66 if tractor else -.15
            p.rod((tx-.30,sy*.57,1.14),(tx+.29,sy*.57,1.14),.153,alloy,28)
            for dx in (-.19,.18):p.rod((tx+dx,sy*.57,1.14),(tx+dx+.039,sy*.57,1.14),.158,steel,28)
        for k,x in enumerate(xs):
            fender(p,x,z+.008,sy,navy if tractor or k==len(xs)-1 and not trailer else steel)
        p.box((xs[0]-.441,sy*.858,.969),(.026,.255,.362),rubber)
    for x in xs:axle(p,x,z)
    for j in range(4):
        x=rear+(front-rear)*(j+.28)/4;p.box((x,0,1.33),(.076,.98,.13),steel)
    if trailer:
        p.box((1.77,0,1.408),(.72,.56,.155),steel)
        p.box((0,0,1.783),(3.18,1.40,.034),navy)
    if tractor:
        p.rod((0,0,1.398),(0,0,1.481),.326,black,36)
        for yy in (-.24,.24):p.box((.21,yy,1.464),(.36,.11,.033),alloy)
    else:bumper(p,rear-.018,1.17)
    finishpart(p)
