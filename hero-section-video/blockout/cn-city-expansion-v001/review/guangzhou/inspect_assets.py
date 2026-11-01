import bpy,sys,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R.parents[1]/'scripts'))
import guangzhou
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
c=bpy.data.collections.new('GZ_DIAGNOSTIC_ASSETS');bpy.context.scene.collection.children.link(c)
colors={'stone':(.49,.50,.47),'ivory':(.78,.76,.66),'red':(.56,.035,.025),'gold':(.69,.45,.11),
'roof':(.10,.13,.14),'blue_roof':(.03,.18,.25),'glass':(.11,.34,.43),'dark_glass':(.035,.15,.20),
'metal':(.58,.64,.66),'white':(.88,.89,.84),'dark':(.025,.03,.028),'wood':(.20,.07,.035),
'green':(.16,.25,.08),'water':(.04,.13,.17),'road':(.23,.25,.25),'paving':(.65,.66,.62)}
materials={}
for k,color in colors.items():
 m=bpy.data.materials.new(k);m.diffuse_color=(*color,1);materials[k]=m
rows=[]
specs=[('canton',(3.6,3.6,18),(0,8,0)),('ifc',(3.6,3,14),(6,8,0)),
 ('ctf',(3.6,3,13),(12,8,0)),('faceted',(3.6,3,12),(18,8,0)),
 ('shells',(7,5,4.5),(26,8,0)),('lingnan',(9,7,5),(1,-3,0)),
 ('pagoda',(3.2,3.2,8),(9,-3,0)),('qilou',(4,3.5,5),(15,-3,0)),
 ('qilou',(4,3.5,5),(19.1,-3,0)),('qilou',(4,3.5,5),(23.2,-3,0))]
for i,(kind,dims,position)in enumerate(specs):
 obs=guangzhou.build(kind,f'GZ_TEST_{kind}_{i}',None,c,materials,*dims)
 root=obs[0];assert root.type=='EMPTY';root.location=position
 verts=[v.co for o in obs if o.type=='MESH'for v in o.data.vertices]
 lo=[min(p[a]for p in verts)for a in range(3)];hi=[max(p[a]for p in verts)for a in range(3)]
 assert lo[2]>=-1e-6 and hi[2]<=dims[2]+1e-6,(kind,lo,hi)
 assert lo[0]>=-dims[0]/2-1e-6 and hi[0]<=dims[0]/2+1e-6
 assert lo[1]>=-dims[1]/2-1e-6 and hi[1]<=dims[1]/2+1e-6
 for o in obs:
  if o.type=='MESH':assert not o.data.validate(),o.name
 rows.append({'kind':kind,'objects':len(obs),'vertices':len(verts),'bounds':[lo,hi]})
s=bpy.context.scene
camera=bpy.data.objects.new('GZ_DIAGNOSTIC_CAMERA',bpy.data.cameras.new('GZ_DIAGNOSTIC_CAMERA'));s.collection.objects.link(camera)
camera.location=(43,-53,37);target=Vector((12,3,8));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=48;s.camera=camera
s.render.engine='BLENDER_WORKBENCH';sh=s.display.shading;sh.light='STUDIO';sh.color_type='MATERIAL';sh.show_shadows=False;sh.show_cavity=True;sh.cavity_type='BOTH';sh.show_specular_highlight=True;sh.background_type='WORLD'
s.render.resolution_x=1800;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.filepath=str(R/'guangzhou-assets.png')
bpy.ops.wm.save_as_mainfile(filepath=str(R/'guangzhou-assets.blend'))
bpy.ops.render.render(write_still=True)
(R/'asset-report.json').write_text(json.dumps(rows,indent=2))
print('ASSET_REPORT',json.dumps(rows))
