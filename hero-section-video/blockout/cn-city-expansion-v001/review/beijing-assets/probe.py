import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import beijing
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene
M={}
colors={'stone':(.57,.55,.50),'ivory':(.87,.83,.71),'red':(.52,.04,.02),'gold':(.85,.56,.08),'roof':(.04,.06,.07),'blue_roof':(.02,.12,.29),'glass':(.18,.35,.42),'dark_glass':(.08,.20,.27),'metal':(.54,.59,.62),'white':(.9,.91,.86),'dark':(.025,.04,.045),'wood':(.24,.11,.05),'green':(.12,.24,.08),'water':(.025,.12,.19),'road':(.2,.21,.20),'paving':(.58,.58,.54)}
for k,v in colors.items():
 m=bpy.data.materials.new('PROBE_'+k);m.diffuse_color=(*v,1);M[k]=m
specs=[('cctv',(13,9,22)),('zun',(8,8,32)),('stadium',(18,14,6)),('heaven',(13,13,12)),('palace',(22,20,10)),('great_wall',(28,18,10))]
assets=[];report={}
for kind,size in specs:
 root=bpy.data.objects.new('PROBE_'+kind,None);s.collection.objects.link(root)
 objs=beijing.build(kind,'BJ_'+kind,root,s.collection,M,*size)
 assets.append((kind,size,root,objs))
 report[kind]={'objects':len(objs),'vertices':sum(len(o.data.vertices)for o in objs),'faces':sum(len(o.data.polygons)for o in objs),'invalid_changes':sum(o.data.validate(verbose=True)for o in objs),'bounds':[[min(v.co[i]for o in objs for v in o.data.vertices),max(v.co[i]for o in objs for v in o.data.vertices)]for i in range(3)]}
cam_data=bpy.data.cameras.new('ProbeCamera');cam=bpy.data.objects.new('ProbeCamera',cam_data);s.collection.objects.link(cam);s.camera=cam
s.render.engine='BLENDER_WORKBENCH';s.render.resolution_x=700;s.render.resolution_y=700;s.render.resolution_percentage=100
s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.shading.show_object_outline=False;s.display.shading.background_type='WORLD';s.world.color=(.075,.075,.075)
for kind,size,root,objs in assets:
 for _,_,_,other in assets:
  for obj in other:obj.hide_render=obj not in objs
 target=Vector((0,0,size[2]*.43));cam.location=target+Vector((size[0]*1.4,-max(size)*1.7,max(size)*.95));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam_data.type='ORTHO';cam_data.ortho_scale=max(size)*1.35
 s.render.filepath=str(Path(__file__).parent/(kind+'.png'));bpy.ops.render.render(write_still=True)
for _,_,_,objs in assets:
 for obj in objs:obj.hide_render=False
(Path(__file__).parent/'assets.json').write_text(json.dumps(report,indent=2))
print('BEIJING_ASSET_REPORT',json.dumps(report),flush=True)
