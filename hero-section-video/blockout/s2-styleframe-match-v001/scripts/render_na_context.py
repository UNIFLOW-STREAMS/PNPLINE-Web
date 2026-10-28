import bpy
from pathlib import Path
R=Path(__file__).resolve().parents[1];s=bpy.context.scene
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=16;s.cycles.use_denoising=True;s.render.threads_mode='FIXED';s.render.threads=10
s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100;s.render.use_border=False;s.render.image_settings.file_format='PNG'
for f in [96,216]:
 s.frame_set(f);s.render.filepath=str(R/f'review/na-context-v017-f{f}.png');bpy.ops.render.render(write_still=True)
