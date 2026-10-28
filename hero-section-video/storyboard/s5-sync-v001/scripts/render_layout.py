import bpy,json,uuid,hashlib,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=R/'layout-proposal-v001';s=bpy.context.scene;sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
full='--full' in sys.argv;frames=list(range(552,949)) if full else [552,576,600,624,648,672,696,720,732,752,766,780,810,842,870,890,900,924,948]
out=P/('raw-'+uuid.uuid4().hex[:8]);out.mkdir();rec={'status':'rendering','blend':bpy.data.filepath,'blend_sha256':sha(bpy.data.filepath),'script_sha256':sha(__file__),'scene':s.name,'camera':s.camera.name,'fps':s.render.fps,'fps_base':s.render.fps_base,'frames':[]}
for f in frames:
 s.frame_set(f);p=out/f'{f:04d}.png';s.render.filepath=str(p);bpy.ops.render.render(write_still=True)
 rec['frames'].append({'frame':f,'path':str(p),'sha256':sha(p),'camera_matrix':list(map(list,s.camera.matrix_world)),'lens':s.camera.data.lens})
rec['status']='complete';(out/'record.json').write_text(json.dumps(rec,indent=2),encoding='utf8');(P/('render-full.json' if full else 'render-stills.json')).write_text(json.dumps(rec,indent=2),encoding='utf8');print('RENDER_COMPLETE',out)
