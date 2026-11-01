import bpy,sys,numpy as np
from mathutils import Vector,Quaternion,Matrix
from pathlib import Path
R=Path(__file__).resolve().parents[1];B=R.parents[1]/'blockout'
sys.path[:0]=[str(R/'scripts'),str(B/'us-title-curve-v001/scripts'),str(B/'curvature-rework-v001/scripts')]
from surface_site import *
from audit_preservation import minimize_scene

s=bpy.context.scene;s.frame_set(0)
def has_motion(o):
    ad=o.animation_data
    return bool(ad and (ad.action or len(ad.nla_tracks) or len(ad.drivers)))
wh=[]
for group in ('CV_WH_US_FRAME','CV_WH_WORLD'):
    for o in s.objects[group].children_recursive:
        if not has_motion(o):continue
        par=o.parent
        while par and par.name!=group and not has_motion(par):par=par.parent
        if par and par.name==group:wh.append(o.name)
vehicles=['A03_TRAILER','A03_TRACTOR','A04_PRIMARY','A05_SECONDARY']
cargo=['A01_CONTAINER','W01_NEW_PALLET','W08_LAST_LOAD']
allroots=wh+vehicles+cargo
wheelmap={v:[o.name for o in s.objects[v].children if 'WHEEL' in o.name] for v in vehicles}
wheelpts={}
for v,ns in wheelmap.items():
    for n in ns:
        o=s.objects[n];to=s.objects[v].matrix_world.inverted()@o.matrix_world
        vv=np.array([to@vtx.co for vtx in o.data.vertices]);mid=(vv.max(0)+vv.min(0))/2;mid[2]=vv[:,2].min()
        wheelpts[n]=mid
parents={n:s.objects[n].parent.name for n in allroots}
tracked=sorted(set(allroots+list(parents.values())+['US_FRAME','CAM_MASTER','CAM_LOOK_TARGET']))
minimize_scene(s,tracked)
tracks={n:np.empty((990,4,4)) for n in tracked};optics=[]
for f in range(990):
    s.frame_set(f)
    for n in tracked:tracks[n][f]=np.array(s.objects[n].matrix_world)
    cam=s.camera.data;optics.append([cam.lens,cam.dof.focus_distance,cam.dof.aperture_fstop])
U=tracks['US_FRAME'];UI=np.linalg.inv(U)
def pos(n):return (UI@tracks[n])[:,:3,3]
def tire_points(v):
    m=UI@tracks[v];vv=np.array([wheelpts[n] for n in wheelmap[v]])
    return vv@m[:,:3,:3].transpose(0,2,1)+m[:,None,:3,3]
cor={n:wh_rigid(pos(n)) for n in wh}
for group in (vehicles[:2],vehicles[2:3],vehicles[3:]):
    d=wheel_fit(np.concatenate([tire_points(v) for v in group],axis=1),dispatch=len(group)==1)
    for n in group:cor[n]=d

def mix(a,b,weight,at):
    result=np.empty_like(a)
    for i,t in enumerate(weight):
        if t<=0:result[i]=a[i];continue
        if t>=1:result[i]=b[i];continue
        qa=Matrix(a[i,:3,:3]).to_quaternion();qb=Matrix(b[i,:3,:3]).to_quaternion()
        m=np.array(qa.slerp(qb,float(t)).to_matrix())
        result[i]=correction(m,at[i],transform(a[i],at[i])*(1-t)+transform(b[i],at[i])*t)
    return result
identity=np.tile(np.eye(4),(990,1,1))
for n,truck in zip(cargo,['A03_TRAILER','A03_TRAILER','A04_PRIMARY']):
    v=pos(n);pc=transform(WI,v);delta=np.linalg.norm(v-pos(truck),axis=1)
    at_wh=smooth(pc[:,0],30,37)*(1-smooth(pc[:,0],68,74))*smooth(pc[:,1],19,24)*(1-smooth(pc[:,1],37,43))
    d=mix(identity,wh_rigid(v),at_wh,v)
    # Docked payload and trailer move as one. The warehouse frame takes
    # over as the pallet travels away from the vehicle into the building.
    near=(1-smooth(delta,4.8,8.5))
    if n=='W01_NEW_PALLET':
        near*=1-smooth(pc[:,0],35.9,38.7)*smooth(pc[:,1],26,28)*(1-smooth(pc[:,1],34,36))
    cor[n]=mix(d,cor[truck],near,v)
out={n:np.linalg.inv(tracks[parents[n]])@U@d@UI@tracks[parents[n]] for n,d in cor.items()}
np.savez_compressed(R/'review/motion-fit.npz',**out)
np.savez_compressed(R/'review/motion-baseline.npz',camera=tracks['CAM_MASTER'],target=tracks['CAM_LOOK_TARGET'],optics=optics,
                    **{n:U@d@UI@tracks[n] for n,d in cor.items()})
for n in cargo:print(n,[(f,arc(pos(n)[f]).round(1).tolist()) for f in (0,300,400,500,600,700,800,900,989)])
print('Fit',len(out),'rigid correction tracks',len(wh),'warehouse actors',flush=True)
