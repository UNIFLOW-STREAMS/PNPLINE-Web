"""Render the A/cloud area directly from the saved Blender camera."""
import bpy,sys
s=bpy.context.scene;s.frame_set(156);s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=32;s.cycles.use_denoising=True
s.render.threads_mode='FIXED';s.render.threads=12;s.render.resolution_x=2560;s.render.resolution_y=1440;s.render.resolution_percentage=100
s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=.64;s.render.border_max_x=.80;s.render.border_min_y=.46;s.render.border_max_y=.75
s.render.image_settings.file_format='PNG';s.render.filepath=sys.argv[sys.argv.index('--')+1];bpy.ops.render.render(write_still=True)
