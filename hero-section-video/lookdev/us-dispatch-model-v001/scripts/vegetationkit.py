"""Deterministic, material-batched broadleaf trees for a miniature district."""
import math
import random


def tree(Batch, name, parent, col, M, seed=0, height=3.0):
    """Build a branched trunk and 78 softly shaded leaf sprays, frontage free.

    At height=3 the canopy is approximately 2.2 units across.  Individual
    clusters vary in shape and direction; no single ellipsoid is the crown.
    """
    rng=random.Random(seed)
    s=height/3.0
    b=Batch(name,parent,col,M)
    def p(v):return tuple(x*s for x in v)
    def rod(a,c,r):b.rod('wood',p(a),p(c),r*s,7)
    lean=(rng.uniform(-.10,.10),rng.uniform(-.09,.09))
    trunk=[(0,0,.015),(lean[0]*.3,lean[1]*.3,.6),
           (lean[0],lean[1],1.22),(lean[0]*.8,lean[1]*1.5,1.85),
           (lean[0]*1.3,lean[1],2.48)]
    for i in range(len(trunk)-1):rod(trunk[i],trunk[i+1],[.075,.058,.039,.020][i])
    # Small buttress roots pin the trunk visually to the planting bed.
    for i in range(5):
        angle=i*math.tau/5+rng.uniform(-.16,.16)
        rod((0,0,.14),(.17*math.cos(angle),.17*math.sin(angle),.025),.027)
    centers=[]
    phase=rng.uniform(0,math.tau)
    for i in range(6):
        a=phase+i*math.tau/6+rng.uniform(-.18,.18)
        dist=rng.uniform(.43,.68)
        z=rng.uniform(1.72,2.16)
        start=trunk[2] if i%2==0 else trunk[3]
        mid=(math.cos(a)*dist*.60,math.sin(a)*dist*.60,z-.20)
        center=(math.cos(a)*dist,math.sin(a)*dist,z)
        rod(start,mid,.030);rod(mid,center,.020)
        centers.append(center)
        for j in range(3):
            aa=a+(j-1)*.62
            tip=(center[0]+.28*math.cos(aa),center[1]+.28*math.sin(aa),z+.23+j*.035)
            rod(mid,tip,.011)
    centers.append((lean[0]*1.1,lean[1],2.47))
    # Sprays accumulate around branch tips.  Spiral distributed positions
    # avoid obvious bands or a perfectly spherical, lollipop outline.
    for ci,c in enumerate(centers):
        count=12 if ci<6 else 6
        for j in range(count):
            a=j*2.399963229728653+ci*.87+rng.uniform(-.33,.33)
            radial=rng.uniform(.12,.40)
            xx=c[0]+math.cos(a)*radial
            yy=c[1]+math.sin(a)*radial
            zz=c[2]+rng.uniform(-.23,.32)
            # Keep the requested height and broad spread, allowing an
            # irregular edge instead of clipping clusters against a cage.
            rr=rng.uniform(.16,.255)
            rx=rr*rng.uniform(.85,1.18);ry=rr*rng.uniform(.78,1.18)
            rz=rr*rng.uniform(.72,1.26)
            zz=min(2.96-rz,zz)
            color=['leaf1','leaf2','leaf3'][(j+ci*2)%3]
            up=(rng.uniform(-.55,.55),rng.uniform(-.55,.55),1.0)
            b.ellipsoid(color,p((xx,yy,zz)),p((rx,ry,rz)),n=8,m=5,up=up)
    objects=b.finish()
    for obj in objects:
        obj['dispatch_asset']='Branched broadleaf tree'
        obj['dispatch_tree_seed']=seed
        if any(k in obj.name for k in ['leaf1','leaf2','leaf3']):
            for poly in obj.data.polygons:poly.use_smooth=True
    return objects


def shrub(Batch,name,parent,col,M,seed=0,width=.8,height=.5):
    """A modest low shrub, suitable for clear fork-apex sightlines."""
    rng=random.Random(seed);b=Batch(name,parent,col,M)
    for i in range(17):
        a=i*2.399963229728653
        radial=width*.33*math.sqrt((i+.5)/17)
        rx=width*rng.uniform(.13,.19)
        rz=height*rng.uniform(.27,.40)
        z=height*.48+height*.17*(1-radial/max(.001,width*.33))
        b.ellipsoid(['leaf1','leaf2','leaf3'][i%3],
                    (math.cos(a)*radial,math.sin(a)*radial,z),
                    (rx,rx*rng.uniform(.8,1.1),rz),n=8,m=5)
    objects=b.finish()
    for obj in objects:
        obj['dispatch_asset']='Low broadleaf shrub'
        for poly in obj.data.polygons:poly.use_smooth=True
    return objects
