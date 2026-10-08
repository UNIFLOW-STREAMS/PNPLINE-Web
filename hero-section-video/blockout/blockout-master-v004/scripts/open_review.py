import bpy
import sys
bpy.context.scene.frame_set(96)
if '--' in sys.argv and 'candidate' in sys.argv[sys.argv.index('--')+1:]:
    bpy.context.scene.frame_set(216)
    bpy.context.scene.use_preview_range=True
    bpy.context.scene.frame_preview_start=96
    bpy.context.scene.frame_preview_end=216
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.region_3d.view_perspective='CAMERA'
            area.spaces.active.shading.type='SOLID'
            area.spaces.active.shading.color_type='MATERIAL'
            area.spaces.active.overlay.show_overlays=False
            area.spaces.active.region_3d.view_camera_zoom=0
print('Initial v004 working copy; S2 not revised yet. View at frame 96; no save performed.')
