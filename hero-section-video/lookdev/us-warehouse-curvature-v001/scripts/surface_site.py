import numpy as np
from mathutils import Matrix
from mapping import WAREHOUSE

C=np.array([0.,0.,-140.])
W=np.asarray(WAREHOUSE,dtype=float)
WI=np.linalg.inv(W)

def transform(m,p):
    return np.asarray(p)@m[:3,:3].T+m[:3,3]

def smooth(x,a,b):
    t=np.clip((x-a)/(b-a),0,1)
    return t*t*(3-2*t)

def sphere(p):
    r=np.linalg.norm(p[...,:2],axis=-1,keepdims=True)
    n=np.concatenate((p[...,:2]*np.sinc(r/(140*np.pi))/140,np.cos(r/140)),axis=-1)
    return C+n*(140+p[...,2:3])

def arc(v):
    q=v-C
    r=np.linalg.norm(q[...,:2],axis=-1,keepdims=True)
    return np.concatenate((q[...,:2]*140*np.arctan2(r,q[...,2:3])/np.maximum(r,1.e-10),np.linalg.norm(q,axis=-1,keepdims=True)-140),axis=-1)

def old_grade(p):
    x,y=p[...,0:1],p[...,1:2]
    w=smooth(x,18,29)*smooth(y,14,24)*(1-smooth(x,82,98))
    port=(1-smooth(x,16,29))*(1-smooth(y,14,24))
    return transform(W,p)*w+p*port+sphere(p+[0,0,.12])*(1-w-port)

def recover(v):
    p=arc(v)
    for _ in range(8):
        e=v-old_grade(p)
        if np.max(abs(e))<1.e-9:break
        j=np.stack([(old_grade(p+d)-old_grade(p-d))/.002 for d in np.eye(3)*.001],axis=-1)
        p=p+np.linalg.solve(j,e[...,None])[...,0]
    assert np.max(abs(v-old_grade(p)))<.00005,('grade inversion',np.max(abs(v-old_grade(p))))
    return p

def new_grade(p):
    q=p.copy()
    q[...,2]+=.12*smooth(p[...,0],89,98)
    blend=1-(1-smooth(p[...,0:1],16,29))*(1-smooth(p[...,1:2],13,24))
    return old_grade(p)*(1-blend)+sphere(q)*blend

def unit(a):
    return a/np.maximum(np.linalg.norm(a,axis=-1,keepdims=True),1.e-10)

def basis(fn,p):
    dx=unit(fn(p+[.01,0,0])-fn(p-[.01,0,0]))
    dy=fn(p+[0,.01,0])-fn(p-[0,.01,0])
    n=unit(np.cross(dx,dy))
    return np.stack((dx,unit(np.cross(n,dx)),n),axis=-1)

def correction(rot,old,new):
    out=np.zeros((*old.shape[:-1],4,4));out[...,3,3]=1
    out[...,:3,:3]=rot;out[...,:3,3]=new-(rot@old[...,None])[...,0]
    return out

def warehouse(v):
    return sphere(transform(WI,v))

def wh_rigid(v):
    p=transform(WI,v)
    return correction(basis(sphere,p)@WI[:3,:3],v,sphere(p))

def grade_rigid(v,raise_by=0):
    p=recover(v)
    rot=basis(new_grade,p)@np.swapaxes(basis(old_grade,p),-1,-2)
    p[...,2]+=raise_by
    return correction(rot,v,new_grade(p))

def wheel_fit(wheels,dispatch=False):
    # Use the original tire footprints, including wheelbase and axle track.
    # A single rigid transformation couples the tractor and trailer.
    p=recover(wheels)
    if dispatch:
        p[...,2]=.74+.02*(1-smooth(p[...,0],81.7,82.3))
    new=new_grade(p)
    a=wheels.mean(axis=1);b=new.mean(axis=1)
    u,_,vt=np.linalg.svd(np.swapaxes(wheels-a[:,None,:],1,2)@(new-b[:,None,:]))
    # Coplanar tires leave SVD free to reverse the normal. Enforce a proper
    # rotation before encoding this fit as a quaternion.
    reflection=np.linalg.det(vt.transpose(0,2,1)@u.transpose(0,2,1))<0
    vt[reflection,-1,:]*=-1
    rot=vt.transpose(0,2,1)@u.transpose(0,2,1)
    assert np.min(np.linalg.det(rot))>.99999
    return correction(rot,a,b)
