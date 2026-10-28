import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1]
src=R.parent/'route-b-a-side-v001/city-rotation-proposal/candidate-city-rotation-v002.blend'
out=R/'master-previz-city-rotation-v001.blend'
audit=json.loads((R/'source-audit.json').read_text())
assert all(audit['checks'].values()),'Current disk save differs from reviewed content'
expected=audit['current_sha256']
assert not out.exists(),'Refuse overwrite'
assert hashlib.sha256(src.read_bytes()).hexdigest()==expected,'Selected candidate changed'
assert Path(bpy.data.filepath).resolve()==src.resolve()
s=bpy.context.scene
assert (s.frame_start,s.frame_end,s.render.fps,s.render.fps_base)==(0,1392,12,1.0)
s['route_b_status']='CITY ROTATION ADOPTED by user 2026-10-29; B route not selected'
s['previz_integration']='S1-S7 master: city rotation v002 adopted 2026-10-29'
s['previz_source_sha256']=expected
s['previz_known_issues']='Unresolved hull overlap: China folded coast f144-250; US terrace f427-477. Not collision-free final delivery.'
s.use_preview_range=False;s.frame_step=1;s.frame_set(156);s.render.filepath='//preview/frames/'
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   area.spaces.active.shading.type='SOLID';area.spaces.active.shading.color_type='MATERIAL';area.spaces.active.region_3d.view_perspective='CAMERA'
bpy.ops.wm.save_as_mainfile(filepath=str(out))
manifest={'adopted_on':'2026-10-29','user_instruction':'도시 회전안을 채택한다.','source':str(src),'source_sha256':expected,'file':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'scope':'Promote full S1-S7 selected candidate; only scene metadata/output path/playback UI adjusted. No geometry, camera, motion or event changes.','known_issues':['China folded coast / hull overlap f144-250','US terrace / hull overlap f427-477'],'release_status':'Adopted previz baseline; contact corrections pending'}
(R/'delivery.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8');print('PROMOTED',out)
