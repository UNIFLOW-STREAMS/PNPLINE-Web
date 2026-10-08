"""Feasibility calculation only. Does not alter or save any .blend."""
import bpy,json,math,sys
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[1];S=bpy.context.scene
base=json.loads((ROOT/'review/baseline-full.json').read_text())['frames'];cand=json.loads((ROOT/'review/states-candidate.json').read_text())['frames']
def pos(r):return Matrix(r['camera']).translation
def tar(r):return Vector(r['target'])
def h(a,b,va,vb,u,n):return (2*u**3-3*u*u+1)*a+(u**3-2*u*u+u)*n*va+(-2*u**3+3*u*u)*b+(u**3-u*u)*n*vb
found=[]
for end in range(218,301):
    ps=[pos(cand[215]),pos(cand[216])];qs=[Matrix(cand[f]['camera']).to_quaternion() for f in [215,216]];ts=[tar(cand[f]) for f in [215,216]]
    for f in range(217,end):
      u=(f-216)/(end-216);n=end-216
      p=h(pos(cand[216]),pos(base[end]),pos(cand[216])-pos(cand[215]),(pos(base[end+1])-pos(base[end-1]))/2,u,n)
      t=h(tar(cand[216]),tar(base[end]),tar(cand[216])-tar(cand[215]),(tar(base[end+1])-tar(base[end-1]))/2,u,n)
      up=Matrix(base[f]['ship']).to_3x3()@Vector((0,0,1));z=(p-t).normalized();x=up.cross(z).normalized();y=z.cross(x).normalized()
      ps.append(p);qs.append(Matrix((x,y,z)).transposed().to_quaternion());ts.append(t)
    for f in [end,end+1]:ps.append(pos(base[f]));qs.append(Matrix(base[f]['camera']).to_quaternion());ts.append(tar(base[f]))
    step=max((ps[i+1]-ps[i]).length for i in range(len(ps)-1));acc=max((ps[i+2]-2*ps[i+1]+ps[i]).length for i in range(len(ps)-2));ang=max(math.degrees(qs[i+1].rotation_difference(qs[i]).angle) for i in range(len(qs)-1));tacc=max((ts[i+2]-2*ts[i+1]+ts[i]).length for i in range(len(ts)-2))
    if step<2.5 and acc<.15 and ang<8 and tacc<.15:found.append({'rejoin_frame':end,'last_changed_frame':end-1,'max_step':step,'max_acceleration':acc,'max_angle_deg':ang,'max_target_acceleration':tacc})
result={'status':'UNAPPLIED feasibility proposal; requires approval, new collision/subframe/render verification','family':'Cubic Hermite in world position and target; match candidate f216 incoming finite-difference and baseline endpoint central derivative','search_endpoints':[218,300],'accepted':found,'recommended':next((r for r in found if r['rejoin_frame']>=252),found[0] if found else None),'minimum_tested':found[0] if found else None,'warning':'Minimum within this family and these numerical bounds, not a proof of globally minimal or visually acceptable joining range.'}
(ROOT/'review/s3-join-proposal.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
