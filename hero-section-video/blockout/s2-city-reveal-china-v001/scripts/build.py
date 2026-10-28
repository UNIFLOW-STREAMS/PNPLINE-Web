import bpy,sys,json,math,hashlib,argparse
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1]
def guard(source,output,expected):
 source=Path(source).resolve();output=Path(output).resolve()
 if source==output or not output.is_relative_to(R) or output.is_relative_to(R/'inputs'):raise ValueError('Unsafe output path')
 if output.exists():raise FileExistsError('Refuse existing output')
 if hashlib.sha256(source.read_bytes()).hexdigest()!=expected:raise ValueError('Source hash mismatch')
 if any(o.get('s2_reveal_owner') for o in bpy.data.objects):raise ValueError('Title already applied')
def title(cfg):
 s=bpy.context.scene;s.frame_set(0);cn=s.objects['CN_FRAME'];C=cn.matrix_world.copy()
 col=bpy.data.collections.new('S2_CHINA_TITLE_V001');s.collection.children.link(col)
 root=bpy.data.objects.new('S2_CHINA_ROOT',None);col.objects.link(root);root.parent=cn
 root['s2_reveal_owner']=cfg['owner'];root['environment']=True;root['text']=cfg['text'];root['font']=cfg['font']
 mats={}
 for k in ['red','gold','base']:
  m=bpy.data.materials.new('S2_CHINA_'+k);m.diffuse_color=cfg[k];mats[k]=m
 def own(o):
  for c in list(o.users_collection):c.objects.unlink(o)
  col.objects.link(o);o.parent=root;o['s2_reveal_owner']=cfg['owner'];o['environment']=True;o['instance_id']='s2china:'+o.name
 widths=cfg['widths'];x=-(sum(widths)+cfg['gap']*4)/2
 for i,(letter,width) in enumerate(zip('CHINA',widths)):
  parts=[];bounds=None
  for layer,offset,depth,z in [('gold',cfg['gold_offset'],cfg['depth']/2,0),('red',cfg['red_offset'],0,cfg['depth']/2+.015)]:
   curve=bpy.data.curves.new(f'CHINA_{letter}_{layer}','FONT');curve.body=letter;curve.size=1;curve.offset=offset;curve.extrude=0;curve.bevel_depth=0;curve.resolution_u=8
   o=bpy.data.objects.new('temp_letter',curve);col.objects.link(o)
   bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH')
   vs=o.data.vertices
   if bounds is None:bounds=(min(v.co.x for v in vs),max(v.co.x for v in vs),min(v.co.y for v in vs),max(v.co.y for v in vs))
   lo,hi,bottom,top=bounds
   # Shared normalization preserves gold outline around the inset red face.
   for v in vs:v.co.x=(v.co.x-lo)/(hi-lo)*width;v.co.y=(v.co.y-bottom)/(top-bottom)*cfg['height'];v.co.z=0
   if layer=='gold':
    # Extrude a closed solid with Solidify; bevel applied after metric normalization.
    mod=o.modifiers.new('Title thickness','SOLIDIFY');mod.thickness=cfg['depth'];mod.offset=0
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bevel=o.modifiers.new('Gold edge','BEVEL');bevel.width=.09;bevel.segments=2;bpy.ops.object.modifier_apply(modifier=bevel.name)
   else:
    for v in vs:v.co.z=z
   o.data.materials.append(mats[layer]);parts.append(o)
  bpy.ops.object.select_all(action='DESELECT')
  for o in parts:o.select_set(True)
  bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();o=parts[0];o.name=f'CHINA_{i}_{letter}';own(o);o['letter']=letter
  o.location=(x,cfg['y'],cfg['bottom']);o.rotation_euler=(math.pi/2,0,0)
  # A separate small plinth under each letter follows the existing sloping terrain.
  pts=[]
  for level in [0,1]:
   for px,py in [(x-.1,cfg['y']-.8),(x+width+.1,cfg['y']-.8),(x+width+.1,cfg['y']+.8),(x-.1,cfg['y']+.8)]:
    top=cfg['bottom']
    if not level:
     terrain=s.objects['CN_LAND_TERRACE'];inv=terrain.matrix_world.inverted();origin=inv@(C@Vector((px,py,30)));direction=(inv.to_3x3()@(C.to_3x3()@Vector((0,0,-1)))).normalized();hit,loc,*_=terrain.ray_cast(origin,direction,distance=80)
     if not hit:raise RuntimeError('Unsupported title foundation '+str((px,py)))
     top=(C.inverted()@terrain.matrix_world@loc).z
    pts.append((px,py,top))
  mesh=bpy.data.meshes.new('CHINA_base_mesh');mesh.from_pydata(pts,[],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);mesh.materials.append(mats['base'])
  base=bpy.data.objects.new(f'CHINA_base_{i}',mesh);col.objects.link(base);own(base);base['title_foundation']=True
  x+=width+cfg['gap']
 bpy.context.view_layer.update()
 return root
def pose(p,t):
 C=bpy.data.objects['CN_FRAME'].matrix_world
 p=C@Vector(p);t=C@Vector(t);up=C.to_3x3()@Vector((0,0,1));z=(p-t).normalized();x=up.cross(z).normalized();y=z.cross(x);q=Matrix((x,y,z)).transposed().to_quaternion()
 return p,t,q
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);ap.add_argument('--camera');args=ap.parse_args(sys.argv[sys.argv.index('--')+1:]);cfg=json.loads((R/'title-config.json').read_text())
 guard(bpy.data.filepath,args.output,cfg['base_sha256']);title(cfg)
 if args.camera:
  sys.path.insert(0,str(R/'scripts'));from camera import apply;apply(json.loads(Path(args.camera).read_text()))
 s=bpy.context.scene;s.frame_set(156)
 for screen in bpy.data.screens:
  for area in screen.areas:
   if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.overlay.show_overlays=False;area.spaces.active.shading.color_type='MATERIAL'
 bpy.ops.wm.save_as_mainfile(filepath=str(Path(args.output).resolve()))
if __name__=='__main__':main()
