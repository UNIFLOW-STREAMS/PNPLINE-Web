"""Read-only widened inspection render; does not save camera changes."""
import bpy
from pathlib import Path
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;ver=Path(bpy.data.filepath).stem.rsplit('-',1)[-1];s.frame_set(156)
s.camera.data.animation_data_clear();s.camera.data.lens*=.8
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=32;s.cycles.use_denoising=True;s.render.threads_mode='FIXED';s.render.threads=8
s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100
s.render.filepath=str(R/f'review/coast-wide-{ver}.png');bpy.ops.render.render(write_still=True)

