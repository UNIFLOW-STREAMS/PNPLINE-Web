"""Read-only tests of actual saved source against prior render provenance."""
import bpy, sys, json, hashlib
from pathlib import Path
from mathutils import Vector
B=Path(__file__).resolve().parents[1]
OLD=B.parent/'s5-sync-v001'
S2=B.parents[1]/'blockout/s5-integration-v001'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
r=json.loads((OLD/'render-record.json').read_text(encoding='utf-8'))
assert sha(bpy.data.filepath)==r['source']['sha256']
s=bpy.context.scene
assert s.name==r['scene'] and s.camera.name==r['camera']
assert s.render.fps==r['fps'] and s.render.fps_base==r['fps_base']
worst=0; states=0
for image in r['images']:
 s.frame_set(image['frame'])
 actual=list(map(list,s.camera.matrix_world));expected=image['camera_state']['world_matrix']
 worst=max(worst,max(abs(a-b) for ar,br in zip(actual,expected) for a,b in zip(ar,br)),abs(s.camera.data.lens-image['camera_state']['lens_mm']))
 if image['state']:
  for name, neighbors in image['state']['neighbors'].items():
   for offset,state in neighbors.items():
    s.frame_set(image['frame']+int(offset));actual=list(map(list,s.objects[name].matrix_world));expected=state['world_matrix']
    worst=max(worst,max(abs(a-b) for ar,br in zip(actual,expected) for a,b in zip(ar,br)));states+=1
assert worst<1e-7, f'Saved source state differs from render provenance: {worst}'
result={'pass':True,'source':str(Path(bpy.data.filepath)),'source_sha256':sha(bpy.data.filepath),'blender':bpy.app.version_string,'scene':s.name,'camera':s.camera.name,'fps':s.render.fps,'fps_base':s.render.fps_base,'range':[s.frame_start,s.frame_end],'markers':{m.name:m.frame for m in s.timeline_markers},'camera_frames_checked':len(r['images']),'neighbor_object_states_checked':states,'max_difference':worst,'reuse_render_record':str(OLD/'render-record.json'),'render_record_sha256':sha(OLD/'render-record.json')}
(B/'review/source-revalidation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
sys.path.insert(0,str(S2.parent/'s5-dock-test-v001/scripts'))
for name in ['integration.py','master_regression.py','wheel_regression.py']:
 p=S2/'tests'/name
 print('REGRESSION',name,flush=True)
 exec(compile(p.read_text(encoding='utf-8'),str(p),'exec'),{'__name__':'__main__','__file__':str(B/'tests'/name)})
assert sha(bpy.data.filepath)==r['source']['sha256']
print('SOURCE_REVALIDATED',json.dumps(result),flush=True)
