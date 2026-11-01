contours=json.loads((shipkit/'wordmark.json').read_text())

def offset_poly(poly,amount):
    sign=1 if sum(a.x*b.y-b.x*a.y for a,b in zip(poly,poly[1:]+poly[:1]))>0 else -1
    normals=[]
    for a,b in zip(poly,poly[1:]+poly[:1]):
        d=(b-a).normalized();normals.append(Vector((d.y,-d.x,0))*sign)
    expanded=[]
    for i,point in enumerate(poly):
        mid=normals[i-1]+normals[i]
        expanded.append(point+mid*min(amount/max(mid.dot(normals[i]),.1),amount*3))
    return expanded

def wordmark(parent,tag,span,mid,zmid,side,wall):
    scale=span/1401
    for i,original in enumerate(contours):
        p=P(f'{tag} raised {side:+d} {i+1}-'+'PNPLINE'[i],parent)
        xy=[Vector(((x-749.5)*scale,(200-y)*scale,0)) for x,y in original]
        edge=offset_poly(xy,.006)
        # Thin machined edge stays legible against both blue paint finishes.
        for arr,depth,relief,mat in [(edge,-.003,.006,bright),(xy,.004,.023,logo_c if i<3 else logo_g)]:
            surface=[(mid-side*q.x,side*(wall+relief),zmid+q.y) for q in arr]
            solid(p,surface,(0,side*(depth-relief),0),mat)
        obj=finishpart(p,.0012)
        obj['source_outline']='PNP-LINE.webp';obj['glyph_index']=i;obj['side']=side

def rib(p,x,side,wall,low,hi,mat,depth=.014):
    if hi-low<.03:return
    profile=[(-.038,0),(-.025,depth),(.024,depth),(.040,0)]
    vs=[(x+a,side*(wall+b),h) for a,b in profile for h in (low,hi)]
    p.add(vs,[(k,k+2,k+3,k+1) if side<0 else (k+1,k+3,k+2,k) for k in (0,2,4)],mat)

def freight(n,tag,hero=False):
    unit=w[n];p=P(tag+' pressed freight body',unit);hardware=P(tag+' cargo fittings',unit)
    if hero:
        xa,xb,wall,low,hi=-1.60,1.60,.770,-.750,.750
        mid,span,zmid=.275,1.96,.006
        bodypaint=blue
        for o in unit.children:
            if o.name.startswith(('PNPLINE_BRAND_SIDE_','VSL_Traveling box')):hide(o)
        for k in ('SIDE_L','SIDE_R','FRONT','DOOR_LEFT_LEAF','DOOR_RIGHT_LEAF'):matset(w['A01_'+k],bodypaint)
        # Stamp the original roof panel downward, leaving the edge rails and three
        # spreader support strips exactly at the original roof height.
        roof=w['A01_ROOF'];stamping=P('Intermodal stamped roof',unit)
        xs=[(-1.6,0),(-1.51,0)]
        for j in range(20):
            x=-1.485+j*.15
            for d,drop in [(0,0),(.022,0),(.044,-.018),(.110,-.018),(.131,0)]:
                xs.append((x+d,0 if abs(x)<.155 or abs(x)>1.35 else drop))
        xs+=[(1.51,0),(1.6,0)]
        ys=[(-.75,0),(-.66,0),(-.623,1),(.623,1),(.66,0),(.75,0)]
        vert=[(x,y,.75+drop*factor) for x,drop in xs for y,factor in ys]
        faces=[(i*6+j,(i+1)*6+j,(i+1)*6+j+1,i*6+j+1) for i in range(len(xs)-1) for j in range(5)]
        stamping.add(vert,faces,roofpaint)
        # Full thickness and original lower plane stay in place.
        stamping.box((0,0,.668),(3.2,1.5,.076),bodypaint)
        for sy in (-1,1):stamping.box((0,sy*.739,.721),(3.2,.022,.050),bodypaint)
        for sx in (-1,1):stamping.box((sx*1.587,0,.721),(.026,1.48,.050),bodypaint)
        repl=stamping.done();me=repl.data
        me.transform(roof.matrix_world.inverted()@unit.matrix_world)
        roof.data=me;bpy.data.objects.remove(repl,do_unlink=True)
    else:
        xa,xb,wall,low,hi=-2.,1.,.86,1.50,3.08
        mid,span,zmid=-.055,1.81,2.301
        bodypaint=blue if n=='A04_PRIMARY' else blue2
        for o in unit.children:
            if 'CARGO_SHELL' in o.name:matset(o,roofpaint if o.name.endswith('.002') else bodypaint)
        for k in ('LEFT_LEAF','RIGHT_LEAF'):matset(w[n+'_'+k],bodypaint)
        p.box((xb-.032,0,(hi+low)/2),(.059,1.66,hi-low-.055),bodypaint)
    # A flat field is pressed into the side to carry the lettering without covering it with grooves.
    for sy in (-1,1):
        for j in range(21):
            x=xa+.105+j*(xb-xa-.21)/20
            depth=.008 if x<xa+.98 else .014
            if abs(x-mid)<span/2+.087:
                rib(p,x,sy,wall,low+.069,zmid-.168,bodypaint,depth)
                rib(p,x,sy,wall,zmid+.165,hi-.074,bodypaint,depth)
            else:rib(p,x,sy,wall,low+.069,hi-.074,bodypaint,depth)
        for h in (low+.030,hi-.033):
            p.box(((xa+xb)/2,sy*(wall+.001),h),(xb-xa-.035,.012,.054),bodypaint)
        for x in (xa+.034,xb-.034):
            p.box((x,sy*(wall+.002),(hi+low)/2),(.063,.012,hi-low-.024),bodypaint)
            for h in (low+.042,hi-.041):
                hardware.box((x,sy*(wall+.009),h),(.060,.012,.072),pearl)
                hardware.box((x,sy*(wall+.016),h),(.028,.004,.021),black)
        if not hero:
            for j in range(5):
                x=xa+.30+j*.585;hardware.box((x,sy*(wall+.009),low+.035),(.119,.016,.023),bright if j%2 else amber)
        wordmark(unit,tag,span,mid,zmid,sy,wall)
    # Keep the upper corner lifting plane of the working container entirely free.
    if not hero:
        for j in range(20):
            x=xa+.115+j*(xb-xa-.23)/19;p.box((x,0,hi+.004),(.045,wall*2-.115,.021),roofpaint)
        for sy in (-1,1):p.box(((xa+xb)/2,sy*(wall-.035),hi+.006),(xb-xa-.017,.06,.024),pearl)
    for j in range(9):
        yy=-.56+j*.14
        vs=[(xb+dx,yy+dy,z) for dy,dx in [(-.037,0),(-.023,.014),(.024,.014),(.039,0)] for z in (low+.083,hi-.082)]
        p.add(vs,[(i,i+2,i+3,i+1) for i in (0,2,4)],bodypaint)
    p.done();finishpart(hardware,.0017)
    # Door hardware follows each existing hinge through unloading and dispatch.
    for lr in 'LR':
        hinge=w[('A01' if hero else n)+'_DOOR_'+lr]
        leaf=next(o for o in hinge.children if o.type=='MESH')
        points=[hinge.matrix_world.inverted()@leaf.matrix_world@Vector(c) for c in leaf.bound_box]
        xmin=min(p.x for p in points);y0=min(p.y for p in points);y1=max(p.y for p in points)
        z0=min(p.z for p in points);z1=max(p.z for p in points)
        b=P(tag+' rear door gear '+lr,hinge)
        for t in (.25,.73):
            y=y0+(y1-y0)*t
            b.rod((xmin-.001,y,z0+.062),(xmin-.001,y,z1-.065),.009,alloy,10)
            for fraction in (.12,.38,.81):
                b.box((xmin-.003,y,z0+(z1-z0)*fraction),(.014,.047,.024),bright)
            b.box((xmin-.006,y+.035,z0+.51),(.012,.088,.021),alloy)
        hside=y1 if lr=='L' else y0
        for fraction in (.17,.50,.84):
            y=hside+(-.078 if lr=='L' else .078)
            b.box((xmin-.003,y,z0+(z1-z0)*fraction),(.014,.109,.038),alloy)
        finishpart(b,.0018)

freight('A01_CONTAINER','Intermodal',True)
freight('A04_PRIMARY','Dispatch')
freight('A05_SECONDARY','Relay')
