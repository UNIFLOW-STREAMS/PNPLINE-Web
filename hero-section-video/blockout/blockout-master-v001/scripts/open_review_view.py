import bpy

bpy.context.scene.frame_set(1)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.region_3d.view_perspective='CAMERA'
            area.spaces.active.shading.type='SOLID'
            area.spaces.active.shading.color_type='MATERIAL'
            area.spaces.active.overlay.show_overlays=False
            area.spaces.active.region_3d.view_camera_zoom=0
print('Review window opened; press Space to play; no scene changes saved.')
