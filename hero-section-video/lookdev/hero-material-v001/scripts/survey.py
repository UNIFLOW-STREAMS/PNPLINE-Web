import bpy,json,hashlib
from pathlib import Path
from collections import Counter
R=Path(__file__).resolve().parents[1];(R/'review').mkdir(exist_ok=True)
s=bpy.context.scene
p=bpy.context.preferences.addons['cycles'].preferences
p.compute_device_type='OPTIX';p.get_devices()
materials=[]
for m in bpy.data.materials:
 users=[o.name for o in s.objects if any(slot.material==m for slot in o.material_slots)]
 nodes=[]
 if m.node_tree:
  for n in m.node_tree.nodes:
   if n.type=='BSDF_PRINCIPLED':nodes.append({i.name:list(i.default_value) if i.type=='RGBA' else i.default_value for i in n.inputs if i.name in ['Base Color','Metallic','Roughness','Transmission Weight','Emission Strength']})
 materials.append(dict(name=m.name,color=list(m.diffuse_color),users=len(users),examples=users[:7],nodes=nodes))
cameras=[]
for f in [0,45,110,200,315,390,530,720,820,900,989]:
 s.frame_set(f);cameras.append(dict(frame=f,position=list(s.camera.matrix_world.translation),rotation=list(s.camera.matrix_world.to_quaternion())))
out=dict(file=bpy.data.filepath,sha256=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),blender=bpy.app.version_string,devices=[(d.name,d.type,d.use) for d in p.devices],objects=len(s.objects),meshes=len(bpy.data.meshes),shared_meshes=sum(m.users>1 for m in bpy.data.meshes),uv_meshes=sum(bool(m.uv_layers) for m in bpy.data.meshes),materials=materials,images=[dict(name=i.name,path=i.filepath,packed=bool(i.packed_file),colorspace=i.colorspace_settings.name) for i in bpy.data.images],lights=[dict(name=o.name,type=o.data.type,energy=o.data.energy,location=list(o.matrix_world.translation)) for o in s.objects if o.type=='LIGHT'],cameras=cameras,world=s.world.name if s.world else None,engine=s.render.engine,view=s.view_settings.view_transform,exposure=s.view_settings.exposure)
(R/'review/survey.json').write_text(json.dumps(out,indent=2),encoding='utf8')
print('SURVEY',out['objects'],len(materials),out['devices'],flush=True)
