import bpy,json,hashlib,ast
from pathlib import Path
R=Path(__file__).resolve().parents[1];m=json.loads((R/'delivery.json').read_text(encoding='utf-8'));master=Path(bpy.data.filepath)
assert master.resolve()==Path(m['file']).resolve()
tree=ast.parse((R.parent/'s2-styleframe-match-v001/scripts/verify_title_water.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in {'digest','actions','objects'}],type_ignores=[]),'<comparison helpers>','exec'))
def snap():
 s=bpy.context.scene;s.frame_set(156)
 def link(o):
  a=o.animation_data
  return [a.action.name if a and a.action else None,getattr(getattr(a,'action_slot',None),'identifier',None)]
 result={'objects':objects(),'actions':actions(),'links':{o.name:link(o)for o in s.objects},'collections':{c.name:sorted(o.name for o in c.objects)for c in bpy.data.collections},'timeline':[s.frame_start,s.frame_end,s.render.fps,s.render.fps_base,sorted((x.name,x.frame)for x in s.timeline_markers)]}
 names=sorted(o.name for o in s.objects if o.animation_data or o.constraints);h=hashlib.sha256()
 for f in range(1393):
  s.frame_set(f);h.update(json.dumps([[list(row)for row in s.objects[n].matrix_world]for n in names]).encode());h.update(str(s.camera.data.lens).encode())
 result['animated_world_transforms_all_integer_frames']=h.hexdigest();return result
a=snap();bpy.ops.wm.open_mainfile(filepath=m['source']);b=snap();checks={key:a[key]==b[key]for key in a};checks['source_hash_unchanged']=hashlib.sha256(Path(m['source']).read_bytes()).hexdigest()==m['source_sha256'];checks['master_hash_matches']=hashlib.sha256(master.read_bytes()).hexdigest()==m['sha256']
result={'file':str(master),'sha256':m['sha256'],'checks':checks,'meaning':'Exact adoption fidelity, not collision clearance','frame_range':[0,1392],'step':1}
(R/'verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result));assert all(checks.values())
# Reopen delivered master and render selected overview without modifying saved scene.
bpy.ops.wm.open_mainfile(filepath=str(master));s=bpy.context.scene;s.frame_set(156);s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.render.resolution_x=640;s.render.resolution_y=360;s.render.resolution_percentage=100;s.render.use_border=False;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.filepath=str(R/'review/f0156.png');bpy.ops.render.render(write_still=True)
