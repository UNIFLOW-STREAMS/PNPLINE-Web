units=[]
def container(x,y,z,L,W,H,key,working=False):
    idx=len(units)+1;paint=M[key];b=part('Freight %02d · %s'%(idx,key))
    l=L/2;w=W/2;top=z+H
    b.box((x,y,z+H/2),(L-.065,W-.07,H-.08),paint)
    # A folded profile gives both sides recessed valleys with sloping flanks.
    for sg in (-1,1):
        a=x-l+.07;span=L-.14;nn=max(7,round(span/.151));pitch=span/nn
        profile=[(a+j*pitch+pitch*t,y+sg*(w-d)) for j in range(nn) for t,d in [(0,.04),(.19,.04),(.34,.012),(.73,.012),(.87,.04)]]
        profile.append((a+span,y+sg*(w-.04)))
        v=[(u,v,h) for u,v in profile for h in (z+.065,top-.069)]
        b.add(v,[(j,j+2,j+3,j+1) if sg<0 else (j+1,j+3,j+2,j) for j in range(0,len(v)-2,2)],paint)
        for h in (z+.04,top-.04):b.box((x,y+sg*(w-.022),h),(L-.048,.044,.073),paint)
    for sx in (-1,1):
        for sy in (-1,1):
            b.box((x+sx*(l-.035),y+sy*(w-.032),z+H/2),(.067,.065,H-.035),paint)
            for h in (z+.032,top-.032):
                b.box((x+sx*(l-.045),y+sy*(w-.041),h),(.087,.081,.064),M['steel'] if key=='ivory' else paint)
                b.box((x+sx*(l-.049),y+sy*(w+.0007),h),(.035,.003,.014),M['grate'])
    b.box((x,y,top-.046),(L-.09,W-.085,.026),paint)
    if working:
        # Flat contact patch is identical in footprint and elevation to the source.
        b.box((x,y,top-.013),(L,W,.026),paint)
    else:
        for j in range(max(8,int((L-.22)/.15))):
            b.box((x-l+.14+j*.15,y,top-.026),(.045,W-.14,.044),paint)
    # Split doors, locking bars, hinges and an identification plate.
    sx=1;end=x+l
    for sy in (-1,1):
        b.box((end-.019,y+sy*w*.48,z+H*.5),(.038,w-.045,H-.12),paint)
        for frac in (.19,.70):
            yy=y+sy*w*frac
            b.rod((end+.006,yy,z+.078),(end+.006,yy,top-.079),.012,M['steel'],7)
            b.box((end+.018,yy-sy*.029,z+H*.38),(.017,.079,.019),iron)
        for h in (.19,.50,.81):b.box((end+.008,y+sy*(w-.065),z+H*h),(.014,.079,.032),M['steel'])
    b.box((end+.003,y+w*.31,z+H*.70),(.007,.135,.057),M['ivory'])
    b.done()
    units.append((x,y,z,L,W,H,key))

for ix,xc in enumerate((-2.6,.8,4.2)):
    for row,(yc,w,h) in enumerate([(-1.25,1.45,1.50),(.145,1.13,1.23),(1.36,1.14,1.19)]):
        pieces=2 if (ix,row) in ((0,2),(1,2),(2,0),(2,1)) else 1
        colors=[['cobalt','ivory','azure'],['ivory','azure','mist'],['azure','ivory','cobalt']]
        tiers=1 if (ix,row)==(1,0) else 3 if (ix,row) in ((0,1),(0,2)) else 2
        for j in range(pieces):
            for tier in range(tiers):
                color=colors[ix][row]
                if j and (ix,row)==(2,1):color='teal'
                if (ix,row,tier,j)==(0,2,2,0):color='green'
                if (ix,row,tier)==(0,0,1):color='ivory'
                if (ix,row,tier)==(1,2,1):color='cobalt' if j else 'ivory'
                container(xc+(j-(pieces-1)/2)*(3.2/pieces),yc,.85+tier*h,3.2 if pieces==1 else 1.56,w,h,color,(ix,row)==(1,0))

# The hero container's roof, floor, doors and rig retain their source meshes.
# Pressed side ribs stay clear of the existing lettering and lifting contacts.
o=s.objects['A01_CONTAINER'];p=part('Traveling box · pressed side panels',o)
paint=s.objects['A01_SIDE_R'].data.materials[0]
for sy in (-1,1):
    for k in range(17):
        x=-1.45+k*.181
        spans=[(-.666,-.18),(.21,.664)] if -.77<x<.77 else [(-.666,.664)]
        for a,b in spans:
            y=sy*.770
            v=[(x+dx,y+sy*d,h) for dx,d in [(-.036,0),(-.020,.014),(.020,.014),(.036,0)] for h in (a,b)]
            p.add(v,[(i,i+2,i+3,i+1) if sy<0 else (i+1,i+3,i+2,i) for i in (0,2,4)],paint)
p.done()
