import bpy,argparse,hashlib,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--start',type=int);p.add_argument('--end',type=int);p.add_argument('--frames');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
s=bpy.context.scene
source_path=Path(bpy.data.filepath);source_hash=hashlib.sha256(source_path.read_bytes()).hexdigest()
folder=R/('review/stills' if a.frames else 'preview/frames');folder.mkdir(parents=True,exist_ok=True)
frames=[int(x) for x in a.frames.split(',')] if a.frames else range(a.start,a.end+1)
for f in frames:
 path=folder/f'f{f:04}.png';assert not path.exists()
 s.frame_set(f);s.render.filepath=str(path);bpy.ops.render.render(write_still=True)
assert hashlib.sha256(source_path.read_bytes()).hexdigest()==source_hash,'Source changed during render'
(R/'review'/('stills.json' if a.frames else f'render-{a.start}-{a.end}.json')).write_text(json.dumps({'source':bpy.data.filepath,'sha256':source_hash,'frames':list(frames),'fps':s.render.fps,'resolution':[s.render.resolution_x,s.render.resolution_y]},indent=2))
