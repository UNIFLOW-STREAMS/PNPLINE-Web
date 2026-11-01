"""Spherical-coordinate metal skin and low-reflection show frontage.
All dimensions use the same authoring chart as the original warehouse surfaces."""
from shipkit import Parts,finish
def build_shell(S,U,C,sphere):
 import numpy as np,math,bpy
 M={n:bpy.data.materials['WH_'+n] for n in ['navy','white','steel','gray','cyan']}
 def mat(k,h,r,m=0):
  v=finish(k,h,r,m);v.name='WHE | '+k;M[k]=v;return v
 mat('Powder coated graphite','344653',.42,.4);mat('Weather seal','232E33',.68)
 mat('Satin aluminium','B9C4C7',.36,.60);mat('Opal daylight panel','C3D9D9',.37,.13)
 p=M['Opal daylight panel'].node_tree.nodes.get('Principled BSDF');p.inputs['Transmission Weight'].default_value=.32
 g=mat('Low iron observation glass','B1CFD4',.13)
 g.diffuse_color=(.36,.65,.71,.18)
 nt=g.node_tree;ns=nt.nodes;lk=nt.links
 trans=ns.new('ShaderNodeBsdfTransparent');trans.inputs[0].default_value=(.976,.991,.995,1)
 glossy=ns.new('ShaderNodeBsdfGlossy');glossy.inputs['Roughness'].default_value=.075
 fres=ns.new('ShaderNodeFresnel');fres.inputs['IOR'].default_value=1.46
 mul=ns.new('ShaderNodeMath');mul.operation='MULTIPLY';mul.inputs[1].default_value=.42;lk.new(fres.outputs[0],mul.inputs[0])
 mix=ns.new('ShaderNodeMixShader');lk.new(mul.outputs[0],mix.inputs[0]);lk.new(trans.outputs[0],mix.inputs[1]);lk.new(glossy.outputs[0],mix.inputs[2]);lk.new(mix.outputs[0],ns.get('Material Output').inputs['Surface'])
 items={}
 def get(name):
  if name not in items:items[name]=Parts('WHE | '+name,U,C)
  return items[name]
 # Sample each surface grid on the true globe. Manifold welded duplicate edges per solid.
 def prism(group,x0,x1,y0,y1,z0,z1,material):
  pts=[];faces=[];ind={};dims=(x1-x0,y1-y0,1)
  def q(x,y,t):
   z=lambda k:k(x,y) if callable(k) else k
   pt=(round(x,7),round(y,7),round(z(z0)*(1-t)+z(z1)*t,7))
   if pt not in ind:ind[pt]=len(pts);pts.append(pt)
   return ind[pt]
  xs=np.linspace(x0,x1,1+max(1,math.ceil((x1-x0)/.75)));ys=np.linspace(y0,y1,1+max(1,math.ceil((y1-y0)/.75)))
  for a,b in zip(xs,xs[1:]):
   for c,d in zip(ys,ys[1:]):
    faces.extend([(q(a,c,0),q(a,d,0),q(b,d,0),q(b,c,0)),(q(a,c,1),q(b,c,1),q(b,d,1),q(a,d,1))])
   faces.extend([(q(a,y0,0),q(b,y0,0),q(b,y0,1),q(a,y0,1)),(q(b,y1,0),q(a,y1,0),q(a,y1,1),q(b,y1,1))])
  for c,d in zip(ys,ys[1:]):
   faces.extend([(q(x0,d,0),q(x0,c,0),q(x0,c,1),q(x0,d,1)),(q(x1,c,0),q(x1,d,0),q(x1,d,1),q(x1,c,1))])
  get(group).add(sphere(np.asarray(pts)),faces,M[material])
 def top(x,y):return 11.61+.15*(36.5-y)/11.75
 def deck(name,a,b,c,d,t0,t1,m):
  prism(name,a,b,c,d,lambda x,y:top(x,y)+t0,lambda x,y:top(x,y)+t1,m)
 # Two flush bands of sealed translucent multiwall glazing set in aluminium curbs.
 a,b=35.7,68.3;c,d=24.72,36.50
 roof='01 | Insulated standing seam roof';light='02 | Sealed daylight monitors';seam='03 | Folded joints and flashings'
 windows=[(39.0,49.45),(54.55,65.0)];ly,hy=31.6,33.15
 for ya,yb in [(c,ly),(hy,d)]:deck(roof,a,b,ya,yb,-.19,0,'white')
 for xa,xb in [(a,windows[0][0]),(windows[0][1],windows[1][0]),(windows[1][1],b)]:deck(roof,xa,xb,ly,hy,-.19,0,'white')
 for xa,xb in windows:
  deck(light,xa,xb,ly,hy,-.025,.07,'Opal daylight panel')
  for y in (ly,hy):deck(light,xa-.055,xb+.055,y-.055,y+.055,-.20,.12,'Satin aluminium')
  for x in np.linspace(xa,xb,8):deck(light,x-.038,x+.038,ly,hy,-.19,.11,'Satin aluminium')
 for x in [36.2+i*.7 for i in range(46)]:
  for y0,y1 in ([(c+.06,ly-.05),(hy+.05,d)] if any(xa<=x<=xb for xa,xb in windows) else [(c+.06,d)]):deck(seam,x-.016,x+.016,y0,y1,0,.042,'Satin aluminium')
 for x in [36.4,40,44,48,52,56,60,64,67.6]:
  for y0,y1 in ([(c,ly-.055),(hy+.055,d)] if any(xa<=x<=xb for xa,xb in windows) else [(c,d)]):deck(seam,x-.048,x+.048,y0,y1,.001,.085,'steel')
 deck(seam,a,b,c,c+.13,-.26,.07,'navy')
 for x in (a,b):deck(seam,x-.035,x+.035,c,39.3,-.16,.06,'navy')
 prism('04 | Rear eave closure',35.85,68.15,38.84,39.13,11.27,11.53,'navy')
 # End walls: new cladding and door reveals; keep the two original loading mouths clear.
 for x in [36,68]:
  gname=('05 | Receiving' if x==36 else '06 | Dispatch')+' end cladding'
  cap=lambda x,y:top(x,y)-.065
  a0,a1=x-.17,x+.17
  prism(gname,a0,a1,25.10,26.72,9.41 if x==68 else 1.86,cap,'navy')
  prism(gname,a0,a1,31.38,31.52,1.86,cap,'navy')
  prism(gname,a0,a1,31.49,39.08,11.231,cap,'navy')
  prism(gname,a0,a1,26.68,26.80,1.86,cap,'navy')
  prism(gname,a0,a1,26.70,31.405,11.49,cap,'navy')
  out=x+(-.185 if x==36 else .185)
  for y in (25.6,26.03,26.46):
   prism(gname,out-.014,out+.014,y-.018,y+.018,1.9,11.48,'Powder coated graphite')
  prism(gname,x-.20,x+.20,31.09,31.52,5.69,11.53,'navy')
 # Unbroken glazed curtain wall with a metal kick wall; door routes are on the SHORT ends.
 face='07 | Curtain wall sill and jambs';pan='08 | Low iron viewing bays';trim='09 | Facade reveals'
 prism(face,35.81,68.18,25.03,25.23,1.86,2.92,'navy')
 prism(trim,35.8,68.18,25.00,25.24,2.90,2.982,'Satin aluminium')
 xx=np.linspace(35.88,68.12,9)
 for a,b in zip(xx,xx[1:]):prism(pan,a,b,25.095,25.12,2.953,9.225,'Low iron observation glass')
 for x in xx:
  if xx[0]<x<xx[-1]:
   # Frameless structural glazing: transparent fins and a bonded butt joint
   # do not wipe across the close moving camera like heavy opaque mullions.
   prism(pan,x-.012,x+.012,25.12,25.25,2.96,9.14,'Low iron observation glass')
   continue
  prism(face,x-.055,x+.055,25.015,25.22,2.91,9.22,'Powder coated graphite')
  prism(trim,x-.012,x+.012,24.998,25.014,2.94,9.21,'Satin aluminium')
 prism(face,35.82,68.18,25.01,25.22,9.115,9.24,'Powder coated graphite')
 # Thin protective laminated sections with one high rail above the main action sightline.
 prism(face,35.84,68.16,25.045,25.17,8.13,8.19,'Powder coated graphite')
 # Keep door margins on both short ends where there were small open slits above the bumpers.
 for x in (36,68):
  prism('10 | Dock seals',x-.12,x+.12,31.16,31.51,1.86,5.69,'Weather seal')
  prism('10 | Dock seals',x-.12,x+.12,26.65,26.83,1.86,5.69,'Weather seal')
 for name,data in items.items():
  ob=data.done();ob['envelope_role']=name
 return [i.name for i in items.values()]

