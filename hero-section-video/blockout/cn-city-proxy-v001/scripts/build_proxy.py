"""Add only owned static geometry; safe output, immutable baseline, no handlers."""
import bpy,sys,json,math,argparse,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from guards import validate_paths
def build(base,output,config):
 c=json.loads(Path(config).read_text());validate_paths(base,output,R,c['base_sha256'])
 bpy.ops.wm.open_mainfile(filepath=str(Path(base).resolve()))
 if any(o.get('cn_proxy_owner')==c['owner'] for o in bpy.data.objects):raise ValueError('Proxy already applied')
 for n in ['CN_PROXY_ROOT']+[x['name'] for x in c['landmarks']]:
  if n in bpy.data.objects:raise ValueError('Name collision: '+n)
 s=bpy.context.scene;col=bpy.data.collections.new('CN_CITY_PROXY_V001');s.collection.children.link(col)
 mats={}
 for n,color in c['materials'].items():
  m=bpy.data.materials.new('CN_PROXY_MAT_'+n);m.diffuse_color=color;m.use_nodes=True
  m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=color
  m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.85;mats[n]=m
 def obj(name,data,parent,loc=(0,0,0),mat=None):
  o=bpy.data.objects.new(name,data);col.objects.link(o);o.parent=parent;o.location=loc
  o['cn_proxy_owner']=c['owner'];o['asset_id']='E-01' if name.startswith('CN_SITE') else 'E-04';o['instance_id']='cnproxy:'+name;o['environment']=True;o['representation']='symbolic_proxy'
  if mat and data:data.materials.append(mats[mat])
  return o
 root=obj('CN_PROXY_ROOT',None,s.objects[c['region']])
 groups={n:obj(n,None,root) for n in ['CN_HIGHRISE_GROUP','CN_WATERFRONT_GROUP','CN_LOWRISE_GROUP','CN_SITE_CONNECTOR']}
 box_cache={}
 def mesh(name,verts,faces,parent,loc=(0,0,0),mat='glass'):
  d=bpy.data.meshes.new(name+'_mesh');d.from_pydata(verts,[],faces);d.update();return obj(name,d,parent,loc,mat)
 def box(name,parent,loc,size,mat):
  key=mat
  if key not in box_cache:
   d=bpy.data.meshes.new('CN_PROXY_BOX_'+mat);d.from_pydata([(x,y,z) for z in [-.5,.5] for y in [-.5,.5] for x in [-.5,.5]],[],[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]);d.materials.append(mats[mat]);box_cache[key]=d
  o=obj(name,box_cache[key],parent,loc);o.scale=size;return o
 def radial(name,parent,loc,rings,mat,segments=16):
  v=[(rad*math.cos(2*math.pi*i/segments),rad*math.sin(2*math.pi*i/segments),z) for z,rad in rings for i in range(segments)]
  f=[tuple(reversed(range(segments))),tuple((len(rings)-1)*segments+i for i in range(segments))]
  for j in range(len(rings)-1):
   for i in range(segments):f.append((j*segments+i,j*segments+(i+1)%segments,(j+1)*segments+(i+1)%segments,(j+1)*segments+i))
  return mesh(name,v,f,parent,loc,mat)
 def sphere(name,parent,z,r,mat):
  rings=[(z+r*math.sin(-math.pi/2+math.pi*j/12),max(.001,r*math.cos(-math.pi/2+math.pi*j/12))) for j in range(13)]
  return radial(name,parent,(0,0,0),rings,mat,24)
 def foundation(name,x,y,w,d):
  o=box('CN_SITE_BASE_'+name,groups['CN_SITE_CONNECTOR'],(x,y,.75),(w,d,.14),'base');o['cn_foundation']=True
 def beam(name,parent,a,b,r,mat):
  a,b=Vector(a),Vector(b);o=radial(name,parent,(a+b)/2,[(-(b-a).length/2,r),((b-a).length/2,r)],mat,12)
  o.rotation_mode='QUATERNION';o.rotation_quaternion=(b-a).to_track_quat('Z','Y')
 zbase=c['support']['foundation_top']
 for item in c['landmarks']:
  name=item['name'];x,y=item['xy'];h=item['height'];w=item['width'];g=obj(name,None,root,(x,y,zbase));g['height']=h;groups[name]=g
  foundation(name,x,y,w+1.0,w+1.0)
  if item['kind']=='sphere':
   radial(name+'_stem',g,(0,0,0),[(0,w*.22),(h*.83,w*.065)],'stem')
   for i in range(3):
    a=i*2*math.pi/3;beam(name+'_leg'+str(i),g,(math.cos(a)*w*.42,math.sin(a)*w*.42,.05),(0,0,h*.3),w*.06,'stem')
   sphere(name+'_lower_sphere',g,h*.26,w*.45,'sphere');sphere(name+'_upper_sphere',g,h*.67,w*.37,'sphere');sphere(name+'_tip_sphere',g,h*.89,w*.13,'sphere')
   radial(name+'_spire',g,(0,0,0),[(h*.78,w*.06),(h,0.015)],'stem')
   for z,r in [(h*.26,w*.46),(h*.67,w*.38)]:radial(name+'_belt'+str(z),g,(0,0,0),[(z-.1,r),(z+.1,r)],'trim')
  elif item['kind']=='taper':
   radial(name+'_body',g,(0,0,0),[(0,w*.5),(h*.3,w*.46),(h*.68,w*.36),(h*.94,w*.28),(h,w*.24)],'glass_light',24)
   for j in [1,2,3,4]:
    z=h*j/5;r=w*(.5-.24*j/5);radial(name+'_band'+str(j),g,(0,0,0),[(z-.06,r+.03),(z+.06,r+.03)],'glass',24)
  elif item['kind']=='open':
   # Lower tapered prism; separated sloping side pylons and lintel leave a real hole.
   ww=w*.37
   v=[(xx,yy,zz) for zz,half in [(0,w/2),(h*.79,ww)] for yy in [-w*.32,w*.32] for xx in [-half,half]]
   mesh(name+'_body',v,[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)],g,mat='glass')
   for sign in [-1,1]:
    # opening widens toward lintel: trapezoid, not painted rectangle
    verts=[(sign*xx,yy,zz) for zz,inner,outer in [(h*.79,w*.19,w*.37),(h*.98,w*.27,w*.43)] for yy in [-w*.32,w*.32] for xx in [inner,outer]]
    mesh(name+'_pylon'+str(sign),verts,[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)],g,mat='glass')
   box(name+'_lintel',g,(0,0,h*.99),(w*.86,w*.64,h*.04),'glass_light')
  else:
   for i in range(6):
    bottom=h*.12*i;hh=h*.12;ww=w*(1-.105*i);box(name+'_tier'+str(i),g,(0,0,bottom+hh/2),(ww,ww,hh),'glass' if i%2==0 else 'glass_light')
   radial(name+'_crown',g,(0,0,0),[(h*.72,w*.24),(h*.89,.10),(h,.012)],'stem',8)
 for i,(x,y,h,w,d) in enumerate(c['highrises']):
  foundation('HIGH_'+str(i),x,y,w+.35,d+.35);g=groups['CN_HIGHRISE_GROUP']
  box('CN_HIGH_'+str(i),g,(x,y,zbase+h/2),(w,d,h),'glass_light' if i%3 else 'glass')
  box('CN_HIGH_CAP_'+str(i),g,(x,y,zbase+h+.10),(w*.8,d*.8,.2),'stem')
 for i,(x,y,h,w,d) in enumerate(c['waterfront']):
  foundation('WATER_'+str(i),x,y,w+.35,d+.35);g=groups['CN_WATERFRONT_GROUP'];box('CN_WATER_'+str(i),g,(x,y,zbase+h/2),(w,d,h),'stone')
  for j in [.3,.65,1]:box('CN_WATER_CORNICE_'+str(i)+'_'+str(j),g,(x,y,zbase+h*j),(w+.12,d+.12,.12),'trim')
  if i==1:
   radial('CN_WATER_DOME',g,(x,y,zbase+h),[(0,.75),(.2,.75),(.65,.5),(.92,.03)],'roof',20)
  if i==3:
   box('CN_WATER_CLOCK_MASS',g,(x,y,zbase+h+.6),(.85,.9,1.2),'stone');radial('CN_WATER_SPIRE',g,(x,y,zbase+h+1.2),[(0,.5),(.7,.03)],'roof',4)
 for i,(x,y,h) in enumerate(c['lowrise']):
  g=groups['CN_LOWRISE_GROUP'];w,d=2.7,2.4;foundation('LOW_'+str(i),x,y,w+.4,d+.4);box('CN_LOW_'+str(i),g,(x,y,zbase+h/2),(w,d,h),'stone')
  v=[(-w*.56,-d*.56,0),(w*.56,-d*.56,0),(w*.56,d*.56,0),(-w*.56,d*.56,0),(-w*.56,0,.7),(w*.56,0,.7)]
  mesh('CN_LOW_ROOF_'+str(i),v,[(0,1,5,4),(3,4,5,2),(0,4,3),(1,2,5),(0,3,2,1)],g,(x,y,zbase+h),'roof')
 x,y=c['pavilion'];g=groups['CN_LOWRISE_GROUP'];foundation('PAVILION',x,y,3.4,3.4)
 for i,(a,b) in enumerate([(-1,-1),(1,-1),(-1,1),(1,1)]):box('CN_PAV_POST_'+str(i),g,(x+a,y+b,zbase+.9),(.15,.15,1.8),'stone')
 radial('CN_PAV_ROOF',g,(x,y,zbase),[(1.7,2.1),(1.85,1.6),(2.6,.15),(2.9,.015)],'roof',4)
 for n in c['hide_original']:
  o=s.objects[n]
  if o.type!='MESH' or o.parent.name!='CN_FRAME' or o.animation_data:raise ValueError('Unexpected replacement object '+n)
  o.hide_render=True;o.hide_set(True)
 s['cn_proxy_version']=c['version'];s['cn_proxy_source_sha256']=c['base_sha256'];s['cn_proxy_config_sha256']=hashlib.sha256(Path(config).read_bytes()).hexdigest()
 bpy.context.view_layer.update();s.frame_set(148)
 # Saved viewport only: preserve render camera, all timeline settings and actual scene shading.
 for screen in bpy.data.screens:
  for area in screen.areas:
   if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
 output=Path(output).resolve();output.parent.mkdir(parents=True,exist_ok=True)
 bpy.ops.wm.save_as_mainfile(filepath=str(output))
 assert hashlib.sha256(Path(base).read_bytes()).hexdigest()==c['base_sha256']
 print('PROXY_SAVED',output,'OWNED',len([o for o in s.objects if o.get('cn_proxy_owner')]))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--base',required=True);p.add_argument('--output',required=True);p.add_argument('--config',required=True)
 a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);build(a.base,a.output,a.config)
