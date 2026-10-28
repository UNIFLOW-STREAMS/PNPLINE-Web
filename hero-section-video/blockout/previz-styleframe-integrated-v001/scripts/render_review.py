import bpy,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;mode=sys.argv[sys.argv.index('--')+1]if '--'in sys.argv else 'stills'
s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.render.resolution_x=960 if mode=='stills'else 640;s.render.resolution_y=540 if mode=='stills'else 360;s.render.resolution_percentage=100;s.render.use_border=False;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
frames=[0,24,72,96,124,144,156,170,180,216,278,330,450,456,532,600,648,672,720,766,842,900,912,1008,1152,1200,1296,1392]if mode=='stills'else list(range(0,1393,2))
folder=R/('review/stills'if mode=='stills'else 'preview/frames');folder.mkdir(exist_ok=True,parents=True)
for f in frames:
 s.frame_set(f);s.render.filepath=str(folder/f'f{f:04d}.png');bpy.ops.render.render(write_still=True)
(folder/'metadata.json').write_text(json.dumps({'blend':bpy.data.filepath,'frames':frames,'source_fps':12,'preview_fps':6 if mode!='stills'else None,'engine':'Workbench','purpose':'geometry and motion inspection, not final material render'},indent=2))
