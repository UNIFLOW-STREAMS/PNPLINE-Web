import bpy
s=bpy.context.scene;s.frame_set(456);s.use_preview_range=True;s.frame_preview_start=444;s.frame_preview_end=672
for screen in bpy.data.screens:
 for a in screen.areas:
  if a.type=='VIEW_3D':
   a.spaces.active.region_3d.view_perspective='CAMERA';a.spaces.active.overlay.show_overlays=False;a.spaces.active.shading.type='SOLID';a.spaces.active.shading.color_type='MATERIAL'
# Visible UI setup only; never saves or changes authored animation.
