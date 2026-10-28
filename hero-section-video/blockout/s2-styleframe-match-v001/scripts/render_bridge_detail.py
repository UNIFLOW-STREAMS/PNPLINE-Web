import bpy
from pathlib import Path
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;ver=Path(bpy.data.filepath).stem.rsplit('-',1)[-1]
s.frame_set(156);s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=40;s.cycles.use_denoising=True;s.render.threads_mode='FIXED';s.render.threads=12
s.render.resolution_x=3200;s.render.resolution_y=1800;s.render.resolution_percentage=100;s.render.use_border=True;s.render.use_crop_to_border=True
s.render.border_min_x=.17;s.render.border_max_x=.43;s.render.border_min_y=.23;s.render.border_max_y=.49
s.render.filepath=str(R/f'review/bridge-detail-{ver}.png');bpy.ops.render.render(write_still=True)
