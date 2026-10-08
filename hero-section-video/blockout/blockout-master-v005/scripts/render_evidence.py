import bpy,sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
args=sys.argv[sys.argv.index('--')+1:];label=args[0]
frames=list(range(*[int(x) for x in args[1].split(':')])) if ':' in args[1] else [int(x) for x in args[1].split(',')]
s=bpy.context.scene;s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100
folder=ROOT/'review'/label;folder.mkdir(exist_ok=True)
print('RENDER_ENGINE',s.render.engine)
for f in frames:
    s.frame_set(f);s.render.filepath=str(folder/f'f{f:04}.png');bpy.ops.render.render(write_still=True)
