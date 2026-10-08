"""Original ellipse route with bounded C2 join repairs; metres in US_FRAME."""
import math,bisect
from functools import lru_cache
def smooth(t):
 t=max(0,min(1,t));return t*t*(3-2*t)
@lru_cache(None)
def table(rx,ry):
 angles=[math.pi*i/4000 for i in range(4001)];lengths=[0.]
 for a,b in zip(angles,angles[1:]):lengths.append(lengths[-1]+math.hypot(rx*(math.sin(b)-math.sin(a)),ry*(math.cos(b)-math.cos(a))))
 return angles,lengths
def raw(s,r):
 rx,ry=r['arc_rx'],r['arc_ry'];aa,ll=table(rx,ry);u=s-r['turn_x']
 if u<=0:return (s,9.),(1.,0.),(0.,0.)
 if u>=ll[-1]:return (r['turn_x']-(u-ll[-1]),29.),(-1.,0.),(0.,0.)
 i=bisect.bisect_left(ll,u);a=aa[i-1]+(aa[i]-aa[i-1])*(u-ll[i-1])/(ll[i]-ll[i-1])
 v=(rx*math.cos(a),ry*math.sin(a));speed=math.hypot(*v);f=tuple(x/speed for x in v);k=rx*ry/speed**3
 return (r['turn_x']+rx*math.sin(a),19-ry*math.cos(a)),f,(-k*f[1],k*f[0])
def extended(s,r):
 p,v,a=raw(s,r);before=raw(s-.001,r)[2];after=raw(s+.001,r)[2]
 return p,v,a,tuple((after[i]-before[i])/.002 for i in range(2))
def septic(s,lo,hi,left,right):
 t=(s-lo)/(hi-lo);h=hi-lo;out=[[],[],[]]
 for axis in range(2):
  p,v,a,j=[x[axis] for x in left];q,w,b,k=[x[axis] for x in right]
  c0=p;c1=v*h;c2=a*h*h/2;c3=j*h**3/6;A=q-c0-c1-c2-c3;B=w*h-c1-2*c2-3*c3;C=b*h*h-2*c2-6*c3;D=k*h**3-6*c3
  c=[c0,c1,c2,c3,35*A-15*B+2.5*C-D/6,-84*A+39*B-7*C+D/2,70*A-34*B+6.5*C-D/2,-20*A+10*B-2*C+D/6]
  out[0].append(sum(c[i]*t**i for i in range(8)))
  out[1].append(sum(i*c[i]*t**(i-1) for i in range(1,8))/h)
  out[2].append(sum(i*(i-1)*c[i]*t**(i-2) for i in range(2,8))/h**2)
 return out
def route(s,cfg):
 r=cfg['route'];end=r['turn_x']+table(r['arc_rx'],r['arc_ry'])[1][-1]+.2
 lo=r['turn_x']-r['entry_blend_m']/2;hi=r['turn_x']+r['entry_blend_m']/2
 if lo<s<hi:return septic(s,lo,hi,extended(lo,r),extended(hi,r))
 lo=end-r['exit_blend_m']
 if lo<s<end:return septic(s,lo,end,extended(lo,r),((r['aligned_x'],r['aligned_y']),(-1,0),(0,0),(0,0)))
 return raw(s,r)
def vehicle_state(frame,cfg):
 r=cfg['route'];f=cfg['frames'];end=r['turn_x']+table(r['arc_rx'],r['arc_ry'])[1][-1]+.2
 s=r['start_distance']+(end-r['start_distance'])*smooth((frame-f['forward_start'])/(f['aligned']-f['forward_start']))
 p,v,a=route(s,cfg);speed=math.hypot(*v);forward=[x/speed for x in v];yaw=math.atan2(v[1],v[0]);k=(v[0]*a[1]-v[1]*a[0])/speed**3
 if frame>=f['aligned']:
  p=(r['aligned_x']+(r['docked_x']-r['aligned_x'])*smooth((frame-f['reverse_start'])/(f['docked']-f['reverse_start'])),r['aligned_y']);yaw=math.pi;forward=(-1.,0.);k=0;speed=1
 h=cfg['rig']['hitch_from_trailer_axle'];tractor=(p[0]+h*forward[0],p[1]+h*forward[1]);tf=(forward[0]-h*k*forward[1],forward[1]+h*k*forward[0])
 return dict(trailer=p,tractor=tractor,trailer_yaw=yaw,tractor_yaw=math.atan2(tf[1],tf[0]),curvature=k)
