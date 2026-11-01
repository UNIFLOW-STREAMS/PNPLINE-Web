import bpy,sys,math,json,hashlib
from pathlib import Path
r=Path(__file__).resolve().parents[1];sys.path.insert(0,str(r/'scripts'))
from resources import wake_atlas,ripple_atlas,travel,shelves,np
s=bpy.context.scene;initial=s.frame_current;sea=s.objects['EARTH_CONTINUOUS_OCEAN'];ship=s.objects['A02_SHIP']
ptr=r.parent/'latest-lookdev.json';prev=json.loads(ptr.read_text())
def hashfile(path):
 with open(path,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert prev['sha256']==hashfile(bpy.data.filepath)==hashfile(prev['versioned_copy'])
(r/'previous-latest-lookdev.json').write_bytes(ptr.read_bytes())
imgs=[wake_atlas(),ripple_atlas(),shelves(s)]
frames,dist,lut=travel(s,ship);imgs.append(lut)
for name in ['WAKE_RIBBON_0','WAKE_RIBBON_1']:
 o=s.objects[name];assert o.parent==ship and not o.children;bpy.data.objects.remove(o,do_unlink=True)
m=bpy.data.materials.new('Pacific | painted swells and aerated wake');m.use_nodes=True;m.diffuse_color=(.025,.135,.21,1);sea.data.materials[0]=m
tree=m.node_tree;tree.nodes.clear()
def node(kind,label=''):
 n=tree.nodes.new(kind);n.label=label;return n
def put(n,key,value):
 sock=n.inputs[key]
 if isinstance(value,bpy.types.NodeSocket):tree.links.new(value,sock)
 else:sock.default_value=value
def op(typ,a,b=None,label=''):
 n=node('ShaderNodeMath',label);n.operation=typ;put(n,0,a)
 if b is not None:put(n,1,b)
 return n.outputs[0]
def add(a,b):return op('ADD',a,b)
def sub(a,b):return op('SUBTRACT',a,b)
def mul(a,b):return op('MULTIPLY',a,b)
def vec(x,y,z=0):
 n=node('ShaderNodeCombineXYZ')
 for i,v in enumerate((x,y,z)):put(n,i,v)
 return n.outputs[0]
def sep(sock):
 n=node('ShaderNodeSeparateXYZ');put(n,0,sock);return n.outputs
def value(label):
 n=node('ShaderNodeValue',label);n.name=label;return n.outputs[0]
def ramp(sock,low,high):
 n=node('ShaderNodeMapRange');n.interpolation_type='SMOOTHERSTEP';put(n,'Value',sock);put(n,'From Min',low);put(n,'From Max',high);return n.outputs[0]
def tex(im,coord,repeat=False):
 n=node('ShaderNodeTexImage',im.name);n.image=im;n.extension='REPEAT' if repeat else 'EXTEND';put(n,0,coord);return n.outputs[0]
def color(h):
 rgb=[int(h[k:k+2],16)/255 for k in (0,2,4)]
 return tuple(((v+.055)/1.055)**2.4 if v>.04045 else v/12.92 for v in rgb)+(1,)
def mix(f,a,b,label=''):
 n=node('ShaderNodeMixRGB',label);put(n,0,f);put(n,1,color(a) if isinstance(a,str) else a);put(n,2,color(b) if isinstance(b,str) else b);return n.outputs[0]
def noise(coord,scale,detail=2):
 n=node('ShaderNodeTexNoise');put(n,'Vector',coord);put(n,'Scale',scale);put(n,'Detail',detail);return n.outputs['Fac']
def group(name,inputs,outputs):
 global tree
 tree=bpy.data.node_groups.new('Pacific | '+name,'ShaderNodeTree')
 for io,ports in [('INPUT',inputs),('OUTPUT',outputs)]:
  for key,typ in ports:tree.interface.new_socket(name=key,in_out=io,socket_type='NodeSocket'+typ)
 i=node('NodeGroupInput');return tree,i.outputs
def done(outputs):
 n=node('NodeGroupOutput')
 for key,val in outputs.items():put(n,key,val)
 arrange(tree,n);return tree
def arrange(t,end):
 layers={}
 def visit(n,d):
  if layers.get(n,-1)>=d:return
  layers[n]=d
  for ip in n.inputs:
   for l in ip.links:visit(l.from_node,d+1)
 visit(end,0);counts={}
 for n,d in layers.items():
  n.location=(-d*255,-counts.get(d,0)*335);counts[d]=counts.get(d,0)+1
def inst(t,inputs):
 n=node('ShaderNodeGroup');n.node_tree=t;n.width=230
 for k,v in inputs.items():put(n,k,v)
 return n.outputs
F='Float';V='Vector';C='Color'
_,i=group('Spherical chart',[('Position',V)],[('East',F),('North',F),('Atlas',V)])
p=i['Position'];x,y,z=sep(p)
e=mul(op('ARCTAN2',x,z),140);lat=mul(op('ARCTAN2',y,op('SQRT',add(mul(x,x),mul(z,z)))),140)
chart=done(dict(East=e,North=lat,Atlas=vec(mul(add(e,230),1/355),mul(add(lat,63),1/144))))
_,i=group('Wind and shallow water',[('Position',V),('East',F),('North',F),('Atlas',V),('Seconds',F)],[('Sea colour',C),('Height',F),('Roughness',F),('Breakup',F)])
e=i['East'];lat=i['North'];t=i['Seconds'];p=i['Position'];shelf=tex(imgs[2],i['Atlas'])
slow=noise(p,.073,1.8);warp=mul(sub(slow,.5),2.4)
u=mul(add(add(e,mul(lat,.29)),mul(t,.21)),.071);v=mul(add(add(lat,warp),mul(t,-.15)),.071)
st=sep(tex(imgs[1],vec(u,v),True))
# Elongated disturbances drift independently of the larger paint strokes.
surf=noise(vec(mul(e,.67),add(mul(lat,2.85),mul(t,-.31)),mul(t,.045)),.81,1.65)
crest=mul(st[0],add(.13,mul(surf,.46)))
water=mix(ramp(slow,.13,.90),'1F586E','307788','Offshore petrol blue')
water=mix(shelf,water,'67A99C','Jade shelf around islands')
water=mix(crest,water,'79AAA9','Broken sky reflection')
wind=done({'Sea colour':water,'Height':add(mul(surf,.74),mul(st[2],.32)),'Roughness':add(.37,mul(slow,.10)),'Breakup':surf})
_,i=group('Stern wash',[('East',F),('North',F),('Progress',F),('Power',F),('Breakup',F),('Seconds',F)],[('Cloud',F),('Lace',F),('Ridge',F)])
e=i['East'];lat=i['North'];t=i['Seconds'];tr=sep(tex(lut,vec(mul(add(e,230),1/355),.5)))
track_d=sub(mul(tr[0],384),64);track_y=sub(mul(tr[1],64),32)
dy=sub(lat,track_y);sn=sub(mul(tr[2],2),1);across=mul(dy,op('SQRT',sub(1,mul(sn,sn))));aft=sub(sub(i['Progress'],track_d),mul(dy,sn))
strength=i['Power'];stretch=add(.52,mul(.48,strength));aft=op('DIVIDE',aft,stretch)
curl=noise(vec(mul(e,.48),mul(lat,.86),mul(t,.33)),1,1.5)
drift=mul(sub(curl,.5),add(.36,mul(.60,ramp(aft,1,18))))
uv=vec(mul(add(aft,1),1/26),mul(add(add(across,drift),8),1/16))
cloud,lace,ridge=sep(tex(imgs[0],uv))
fade=mul(strength,ramp(track_d,-.6,1.5))
modulate=add(.58,mul(.60,curl))
wake=done({'Cloud':mul(cloud,fade),'Lace':mul(mul(lace,fade),modulate),'Ridge':mul(ridge,fade)})
tree=m.node_tree
coord=node('ShaderNodeTexCoord').outputs['Object'];ch=inst(chart,{'Position':coord})
clock=value('Ocean seconds');progress=value('Baked stern distance');power=value('Propeller wash strength')
clock.default_value=0;clock.keyframe_insert('default_value',frame=0);clock.default_value=989/30;clock.keyframe_insert('default_value',frame=989)
speed=np.gradient(dist);speed=np.convolve(speed,np.ones(7)/7,mode='same')
powers=np.clip((speed-.007)/.65,0,1)**.66
# Retain a short, diminishing plume during deceleration and after mooring.
for j in range(1,len(powers)):powers[j]=max(powers[j],powers[j-1]*.924)
for j,f in enumerate(frames):
 for sock,val in [(progress,dist[j]),(power,0 if j==len(frames)-1 else powers[j])]:
  sock.default_value=float(val);sock.keyframe_insert('default_value',frame=int(f))
for layer in tree.animation_data.action.layers:
 for strip in layer.strips:
  for bag in strip.channelbags:
   for fc in bag.fcurves:
    for k in fc.keyframe_points:k.interpolation='LINEAR'
o=inst(wind,{'Position':coord,'East':ch['East'],'North':ch['North'],'Atlas':ch['Atlas'],'Seconds':clock})
w=inst(wake,{'East':ch['East'],'North':ch['North'],'Progress':progress,'Power':power,'Breakup':o['Breakup'],'Seconds':clock})
surface=mix(mul(w['Cloud'],.79),o['Sea colour'],'71B5B6','Suspended aeration');surface=mix(w['Lace'],surface,'F0F2E8','Broken foam')
bump=node('ShaderNodeBump','Wavelet relief');put(bump,'Height',add(o['Height'],mul(w['Ridge'],.47)));put(bump,'Strength',.26);put(bump,'Distance',.095)
p=node('ShaderNodeBsdfPrincipled');put(p,'Base Color',surface);put(p,'IOR',1.333);put(p,'Roughness',add(o['Roughness'],mul(w['Lace'],.21)));put(p,'Normal',bump.outputs[0]);put(p,'Metallic',.035)
# Give the globe one continuous sea normal, irrespective of harbour mesh tessellation.
def vector_math(operation,a,b=None):
 n=node('ShaderNodeVectorMath');n.operation=operation;put(n,0,a)
 if b is not None:put(n,1,b)
 return n.outputs['Value'] if operation=='DOT_PRODUCT' else n.outputs['Vector']
radial=vector_math('NORMALIZE',node('ShaderNodeNewGeometry','Globe radius').outputs['Position'])
incoming=node('ShaderNodeNewGeometry','View direction').outputs['Incoming']
incidence=op('ABSOLUTE',vector_math('DOT_PRODUCT',incoming,radial))
put(bump,'Normal',radial)
# Reduce sub-pixel relief near silhouette. Paint a continuous soft glancing-sky reflection
# where a microfacet BSDF is sensitive to the underlying geometric tangent.
put(bump,'Strength',mul(.26,ramp(incidence,.12,.58)))
sky= mix(mul(.68,sub(1,ramp(incidence,0,.40))),o['Sea colour'],'9BACAF','Continuous sky wash')
horizon=node('ShaderNodeEmission','Soft horizon reflection');put(horizon,'Color',sky);put(horizon,'Strength',.96)
finish=node('ShaderNodeMixShader','Grazing-angle transition');put(finish,0,ramp(incidence,.23,.52));put(finish,1,horizon.outputs[0]);put(finish,2,p.outputs[0])
end=node('ShaderNodeOutputMaterial');put(end,'Surface',finish.outputs[0]);arrange(tree,end)
s.frame_set(initial);bpy.context.preferences.filepaths.save_version=0
out=r/'pnpline-ocean-foam-v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
print('SAVED',out,[(im.name,im.size[:],bool(im.packed_file)) for im in imgs],flush=True)



