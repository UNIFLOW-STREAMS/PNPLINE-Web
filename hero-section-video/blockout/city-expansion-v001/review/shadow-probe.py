import bpy,bmesh
from pathlib import Path
s=bpy.context.scene;count=0
for o in s.objects:
 if not o.name.startswith('CE_') or o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data)
 bad=any(not e.is_manifold for e in bm.edges) or any(f.calc_area()<1e-10 for f in bm.faces)
 bm.free()
 if bad:o.display.show_shadows=False;count+=1
s.frame_set(900);s.render.filepath='F:/pnpline-landing/hero-section-video/blockout/city-expansion-v001/review/shadow-probe.png';bpy.ops.render.render(write_still=True)
print('OPEN_SURFACES_NO_SHADOW',count)
