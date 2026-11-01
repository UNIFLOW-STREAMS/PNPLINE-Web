from pathlib import Path
import numpy as np, bpy, math
from mathutils import Vector
D=Path(__file__).resolve().parents[1]
def data_image(name,array,fp=False):
 h,w,_=array.shape
 image=bpy.data.images.new(name,w,h,alpha=False,float_buffer=fp,is_data=True)
 rgba=np.ones((h,w,4),np.float32);rgba[:,:,:3]=array
 image.colorspace_settings.name='Non-Color'
 image.file_format='OPEN_EXR' if fp else 'PNG'
 image.filepath_raw=str(D/'resources'/(name+('.exr' if fp else '.png')));image.pixels.foreach_set(rgba.ravel());image.update();image.save()
 path=image.filepath_raw;bpy.data.images.remove(image);image=bpy.data.images.load(path);image.name=name;image.colorspace_settings.name='Non-Color';image.pack()
 verify=np.empty(w*h*4,np.float32);image.pixels.foreach_get(verify);assert np.ptp(verify.reshape(h,w,4)[:,:,0])>.1,name
 return image
def ease(a,b,v):
 t=np.clip((v-a)/(b-a),0,1);return t*t*(3-2*t)
def chart(point):
 x,y,z=point;return (140*math.atan2(x,z),140*math.atan2(y,math.hypot(x,z)))
def wake_atlas():
 # Individual tapered swells break away from a pair of rolling shoulders;
 # the screw wash contains warped, stretched Voronoi bubbles.
 H,W=448,896
 aft,y=np.meshgrid((np.arange(W)+.5)*26/W-1,(np.arange(H)+.5)*16/H-8)
 side=np.sign(y);ay=np.abs(y);fwd=ease(-.8,.2,aft);tail=1-ease(13.8,24.4,aft)
 def gauss(x):return np.exp(-x*x)
 shape=1.28+.19*aft+.24*np.sin(aft*.62+side*.9)+.09*np.sin(1.9*aft+side)
 def bands(a,b):return np.clip(a+b,0,1)
 edge=ay-shape
 lace= .5+.29*np.sin(aft*1.65+1.2*y)+.16*np.sin(aft*.78-y*3.5)+.08*np.cos(aft*4.2+y*3.6)
 edgefoam=gauss(edge/(.24+.010*np.maximum(aft,0)))*ease(.13,.67,lace)
 fan=0*aft
 for i in range(6):
  peak=1.4+3.05*i+.52*side*np.sin(i*1.9+.3)
  crest=peak+.72*(ay-shape)+.23*(ay-shape)**2
  fan=np.maximum(fan,gauss((aft-crest)/(.19+.016*i))*gauss((edge+.28)/(.77+.065*i))*ease(-.25,.56,lace+.25))
 width=1.15+.105*np.maximum(aft,0)
 wash=gauss((y-.20*np.sin(.72*aft))/width)**.7
 u=aft*1.17+.57*np.sin(y*1.8+aft*.5)
 v=y*2.45+.6*np.sin(aft*.69-y*.7)+.22*np.cos(1.72*aft)
 ix,iy=np.floor(u),np.floor(v);d1=np.full_like(u,999.);d2=d1.copy()
 def rand(a,b,k):
  a=np.sin(a*127.1+b*311.7+k)*43758.5453;return a-np.floor(a)
 for j in [-1,0,1]:
  for i in [-1,0,1]:
   X=ix+i;Y=iy+j
   d=(X+.1+.8*rand(X,Y,3.4)-u)**2+(Y+.1+.8*rand(X,Y,77.7)-v)**2
   d2=np.minimum(d2,np.maximum(d1,d));d1=np.minimum(d1,d)
 cells=1-ease(.055,.32,np.sqrt(d2)-np.sqrt(d1))
 eddy=gauss((y-.38*np.sin(aft*1.18))/(.76+.069*np.maximum(aft,0)))
 center=eddy*(.24+.72*cells)*(.67+.25*np.cos(.95*aft-1.2*y))*(1-.83*ease(4,20,aft))
 milk=np.clip(.72*wash*(1-.45*ease(2,18,aft))+.40*gauss(edge/1.0),0,1)
 rgb=np.stack([milk, np.clip(.92*edgefoam+.72*fan+center,0,1),np.clip(.85*fan+.5*edgefoam+.43*center,0,1)],axis=2)
 return data_image('Wake - foam and aeration',rgb*(fwd*tail)[:,:,None])
def ripple_atlas():
 rng=np.random.default_rng(515);n=512
 x,y=np.meshgrid((np.arange(n)+.5)/n,(np.arange(n)+.5)/n)
 ink=x*0;under=ink.copy()
 for i in range(66):
  ox,oy=rng.uniform(0,1,2);dx=(x-ox+.5)%1-.5;dy=(y-oy+.5)%1-.5
  length=rng.uniform(.015,.085);w=rng.uniform(.0023,.0045)
  q=dx/length
  line=dy-.14*dx-.004*np.sin(2.1*q+i)-.0035*q*q
  env=np.maximum(0,1-q*q)
  crest=np.exp(-(line/(w*(.32+.68*env)))**2)*env**.65
  ink=np.maximum(ink,crest*rng.uniform(.48,1))
  under=np.maximum(under,np.exp(-((line+.005)/(.008+w))**2)*env*.78)
 return data_image('Swell - broken brush crests',np.stack([ink,under,np.maximum(ink,under*.62)],axis=2))
def travel(s,ship):
 frames=np.arange(70,386);positions=[]
 for f in frames:
  s.frame_set(int(f));positions.append(chart(ship.matrix_world@Vector((-7.15,-.17,0))))
 xy=np.array(positions);dist=np.r_[0,np.cumsum(np.linalg.norm(np.diff(xy,axis=0),axis=1))]
 # The longitudinal coordinate increases strictly on the crossing. Trim the stationary docked samples.
 keep=np.r_[True,np.diff(xy[:,0])>.003]
 xx=xy[keep,0];yy=xy[keep,1];dd=dist[keep]
 keep=np.r_[True,xx[1:]>np.maximum.accumulate(xx[:-1])]
 xx,yy,dd=xx[keep],yy[keep],dd[keep]
 xx=np.r_[xx[0]-50,xx,xx[-1]+50];yy=np.r_[yy[0],yy,yy[-1]];dd=np.r_[dd[0]-50,dd,dd[-1]+50]
 grid=-230+(np.arange(2048)+.5)*355/2048
 # A packed float strip stores distance travelled, centre latitude, and sin of the local steering angle.
 data=np.stack([np.interp(grid,xx,dd),np.interp(grid,xx,yy),np.interp(grid,xx,np.gradient(yy,dd))],axis=-1)
 data=(data+np.array([64.,32.,1.]))/np.array([384.,64.,2.])
 assert data.min()>=0 and data.max()<=1
 lut=data_image('Voyage - stern track metres',np.tile(data[None,:,:],(4,1,1)),True)
 return frames,dist,lut
def shelves(s):
 w,h=1408,576
 x,y=np.meshgrid(-230+(np.arange(w)+.5)*355/w,-63+(np.arange(h)+.5)*144/h)
 water=x*0
 for o in s.objects:
  if o.name.startswith('Pacific |') and 'shoreline' in o.name:
   p=np.array([chart(o.matrix_world@v.co) for v in list(o.data.vertices)[-48:]])
   select=(abs(x-p[:,0].mean())<np.ptp(p[:,0])+8)&(abs(y-p[:,1].mean())<np.ptp(p[:,1])+8)
   X=x[select];Y=y[select];ds=np.full_like(X,1e7)
   for (a,b),(c,d) in zip(p,np.roll(p,-1,axis=0)):
    u=c-a;v=d-b;t=np.clip(((X-a)*u+(Y-b)*v)/(u*u+v*v),0,1)
    ds=np.minimum(ds,(X-a-u*t)**2+(Y-b-v*t)**2)
   water[select]=np.maximum(water[select],np.exp(-np.sqrt(ds)/2.25))
 # Broad near-port shelves at either berth.
 for o in [s.objects['CN_QUAY'],s.objects['US_QUAY']]:
  q=np.mean([chart(o.matrix_world@Vector(v)) for v in o.bound_box],axis=0)
  water=np.maximum(water,.62*np.exp(-((x-q[0])/18)**2-((y-q[1])/10)**2))
 return data_image('Shelf - coastal falloff',np.repeat(water[:,:,None],3,axis=2))



