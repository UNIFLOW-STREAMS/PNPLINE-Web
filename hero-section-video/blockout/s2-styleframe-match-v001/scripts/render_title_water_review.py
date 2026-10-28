import bpy,runpy
from pathlib import Path
R=Path(__file__).resolve().parents[1]
for ver in ['v024','v021','v027']:
 bpy.ops.wm.open_mainfile(filepath=str(R/f'review/layout-proposal-{ver}.blend'))
 runpy.run_path(str(R/'scripts/render_basin_comparison.py'),run_name='__main__')
s=bpy.context.scene;s.render.use_border=False;s.render.use_crop_to_border=False;s.render.resolution_x=1280;s.render.resolution_y=720;s.cycles.samples=24
for f in [156,96,216]:
 s.frame_set(f);s.render.filepath=str(R/f'review/title-water-v027-f{f:04d}.png');bpy.ops.render.render(write_still=True)
