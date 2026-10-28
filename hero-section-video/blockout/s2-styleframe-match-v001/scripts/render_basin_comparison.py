"""Same camera, resolution and lighting for before/after basin comparison."""
import bpy,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;ver=Path(bpy.data.filepath).stem.rsplit('-',1)[-1]
s.frame_set(156);s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=32;s.cycles.use_denoising=True
s.render.threads_mode='FIXED';s.render.threads=12;s.render.resolution_x=2560;s.render.resolution_y=1440;s.render.resolution_percentage=100
s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=.225;s.render.border_max_x=.70;s.render.border_min_y=.355;s.render.border_max_y=.59
s.render.filepath=str(R/f'review/basin-detail-{ver}.png');bpy.ops.render.render(write_still=True)
