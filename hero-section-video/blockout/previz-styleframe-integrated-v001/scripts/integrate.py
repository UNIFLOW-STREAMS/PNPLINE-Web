import bpy,json,hashlib,ast
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];B=R.parent;src=R/'inputs/layout-proposal-v032.blend';out=R/'master-previz-styleframe-v001.blend'
assert not out.exists()
bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene
assert (s.frame_start,s.frame_end,s.render.fps)==(0,1392,12)
source_hash=hashlib.sha256(src.read_bytes()).hexdigest()
s.use_preview_range=False;s.frame_step=1;s.frame_set(156)
s.render.filepath='//preview/frames/'
s['previz_integration']='S1-S7 master: approved layout-proposal-v032 adopted 2026-10-28'
s['previz_source_sha256']=source_hash
s['previz_timing']='Original 12fps; speed-comparison variants not merged'
for screen in bpy.data.screens:
 for ar in screen.areas:
  if ar.type=='VIEW_3D':
   ar.spaces.active.shading.type='SOLID';ar.spaces.active.shading.color_type='MATERIAL';ar.spaces.active.region_3d.view_perspective='CAMERA'
bpy.ops.wm.save_as_mainfile(filepath=str(out))
(R/'inputs/manifest.json').write_text(json.dumps({'adopted_source':str(B/'s2-styleframe-match-v001/review/layout-proposal-v032.blend'),'source_sha256':source_hash,'base_master':str(B/'s2-city-reveal-china-v001/master-s2-city-reveal-china-v001.blend'),'base_sha256':hashlib.sha256((B/'s2-city-reveal-china-v001/master-s2-city-reveal-china-v001.blend').read_bytes()).hexdigest(),'output':str(out),'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'method':'Promote the full-scene v032 descendant of the latest base master. No object append/duplicate and no time retiming.','markers':[[m.name,m.frame]for m in s.timeline_markers]},indent=2))
print('INTEGRATED',str(out),'objects',len(s.objects),'actions',len(bpy.data.actions))
