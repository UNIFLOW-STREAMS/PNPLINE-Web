from pathlib import Path
import numpy as np,json,itertools
R=Path(__file__).resolve().parents[1]
def box(lo,hi):return np.array(list(itertools.product(*zip(lo,hi))))
points=[box([-7,-2.6,-.65],[7,2.6,4.6]),box([-1.6,7.9,.2],[5.7,10.1,3.5]),box([36,25,1.86],[68,39,10.5])]
targets=np.array([[.02,.12,.40,1.02],[.44,.48,.69,.79],[.71,.12,.98,.37]])
def projection(v):
 cam=np.array(v[:3]);aim=np.array(v[3:6]);forward=aim-cam;forward/=np.linalg.norm(forward);right=np.cross(forward,[0,0,1]);right/=np.linalg.norm(right);up=np.cross(right,forward);rows=[];bad=0
 for p in points:
  q=p-cam;z=q@forward
  if min(z)<1:bad+=(1-min(z))**2
  z=np.maximum(z,1);x=.5+(q@right)*v[6]/(36*z);y=.5-(q@up)*v[6]/(20.25*z);rows.append([min(x),min(y),max(x),max(y)])
 return np.array(rows),bad
def objective(v):
 a,bad=projection(v);err=np.sum((a-targets)**2*np.array([[1,1,2,1],[4,4,4,4],[3,3,3,3]]));outside=np.maximum(-a[1:,:2],0).sum()+np.maximum(a[1:,2:]-1,0).sum()
 return err+100*bad+outside*20
lo=np.array([-25,-120,5,-5,7,1,16]);hi=np.array([-.01,8,65,28,30,6,100]);rng=np.random.default_rng(42);pop=rng.uniform(lo,hi,(80,7));velocity=np.zeros_like(pop);best=pop.copy();scores=np.array([objective(v) for v in pop]);gbest=best[np.argmin(scores)].copy()
for j in range(240):
 velocity=.65*velocity+1.4*rng.random(pop.shape)*(best-pop)+1.4*rng.random(pop.shape)*(gbest-pop);pop=np.clip(pop+velocity,lo,hi);now=np.array([objective(v) for v in pop]);mask=now<scores;best[mask]=pop[mask];scores[mask]=now[mask];gbest=best[np.argmin(scores)].copy()
v=gbest;out={'camera_us':v[:3].tolist(),'aim_us':v[3:6].tolist(),'lens':v[6],'projection_bounds':projection(v)[0].tolist(),'target_bounds':targets.tolist(),'objective':objective(v),'limitations':'coarse bounds approximate composition only; no geometry or source changes; visual review required'}
(R/'review/s4-s5-recheck/solved-rear-framing.json').write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(out,indent=2))
