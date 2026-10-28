"""CPU fallback after EEVEE driver crash. Read-only render, no save."""
import bpy,sys,json,hashlib
from pathlib import Path
out=Path(sys.argv[sys.argv.index('--')+1]);s=bpy.context.scene
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=24;s.cycles.use_denoising=True
s.render.threads_mode='FIXED';s.render.threads=12
s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100
s.frame_set(156);s.render.filepath=str(out);bpy.ops.render.render(write_still=True)
out.with_suffix('.json').write_text(json.dumps({'blend':bpy.data.filepath,'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'engine':'Cycles CPU','samples':24,'frame':156,'camera':s.camera.name,'lens':s.camera.data.lens,'color':'AgX','purpose':'design proposal render, not accepted final'},indent=2))
