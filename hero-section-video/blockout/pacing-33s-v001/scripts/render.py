"""Render unique output frames at the saved 30fps; no duplication/interpolation."""
import argparse, bpy, hashlib, json, sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--start',type=int,required=True);p.add_argument('--end',type=int,required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
s=bpy.context.scene
assert s.render.fps==30 and s.frame_end==989
folder=R/'preview/frames';folder.mkdir(exist_ok=True)
for f in range(a.start,a.end+1):
    path=folder/f'f{f:04}.png'
    assert not path.exists(), path
    s.frame_set(f);s.render.filepath=str(path)
    bpy.ops.render.render(write_still=True)
    if f%30==0:print('PROGRESS',f,flush=True)
(R/'review'/f'render-{a.start}-{a.end}.json').write_text(json.dumps({'blend_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'start':a.start,'end':a.end,'fps':s.render.fps,'resolution':[s.render.resolution_x,s.render.resolution_y]},indent=2))
