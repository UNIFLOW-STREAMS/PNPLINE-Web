import bpy
s=bpy.context.scene;s.frame_set(216);s.use_preview_range=True;s.frame_preview_start=204;s.frame_preview_end=480
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.region_3d.view_camera_zoom=0
   area.spaces.active.shading.type='SOLID';area.spaces.active.shading.color_type='MATERIAL';area.spaces.active.overlay.show_overlays=False
print('S3 review view; no save performed.')
