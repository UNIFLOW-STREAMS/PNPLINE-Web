import bpy,json,uuid,hashlib,sys
from pathlib import Path
s=bpy.context.scene;B=Path(bpy.data.filepath).parent;sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
full='--full' in sys.argv
frames=list(range(1393)) if full else [0,96,216,300,360,408,432,456,480,504,528,551,552,576,600,624,648,672,696,720,766,842,900,947,948,949,960,1008,1020,1090,1158,1200,1230,1260,1296,1344,1392]
out=B/('raw-'+uuid.uuid4().hex[:8]);out.mkdir();rec={'status':'rendering','blend':bpy.data.filepath,'blend_sha256':sha(bpy.data.filepath),'script_sha256':sha(__file__),'scene':s.name,'camera':s.camera.name,'fps':s.render.fps,'fps_base':s.render.fps_base,'frames':[]}
s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100
for f in frames:
 s.frame_set(f);p=out/f'{f:04d}.png';s.render.filepath=str(p);bpy.ops.render.render(write_still=True)
 rec['frames'].append({'frame':f,'path':str(p),'sha256':sha(p),'camera_matrix':list(map(list,s.camera.matrix_world)),'lens':s.camera.data.lens})
rec['status']='complete';(out/'record.json').write_text(json.dumps(rec,indent=2),encoding='utf8');(B/('render-full.json' if full else 'render-stills.json')).write_text(json.dumps(rec,indent=2),encoding='utf8');print('RENDER_COMPLETE',out)
