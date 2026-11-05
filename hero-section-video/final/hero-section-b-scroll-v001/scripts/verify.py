import bpy,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R.parent/'hero-section-ab-v001/scripts'))
from state import hashed,curves,sha
v=json.loads((R/'verification.json').read_text());assert sha(bpy.data.filepath)==v['sha256'];assert sha(v['source'])==v['source_sha256'];candidate={a.name:hashed(curves(a)) for a in bpy.data.actions}
with bpy.data.libraries.load(v['source'],link=False) as (available,loaded):
 names=list(available.actions);loaded.actions=names[:]
assert len(candidate)==len(names)
for name,a in zip(names,loaded.actions):assert candidate[name]==hashed(curves(a)),name
cfg=json.loads(bpy.data.texts['PNPLINE_SCROLL_PACING.json'].as_string());assert sum(s['scrollVh'] for s in cfg['sections'])==13;assert bpy.context.scene.frame_start==0 and bpy.context.scene.frame_end==989 and bpy.context.scene.render.fps==30
v.update(reopened_verified=True,all_actions_exact=True,config_embedded=True,total_viewport_heights=13);(R/'verification.json').write_text(json.dumps(v,indent=2));print('REOPEN VERIFIED every action identical to source; embedded mapping present',flush=True)
