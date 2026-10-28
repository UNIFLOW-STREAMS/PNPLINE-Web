import bpy,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
arg=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'master-motion-polish-A.blend'
bpy.ops.wm.open_mainfile(filepath=str(R/arg));s=bpy.context.scene;road=s.objects['MP_CONTINUOUS_ROAD'];I=s.objects['US_FRAME'].matrix_world.inverted()
vertices=[I@road.matrix_world@v.co for v in road.data.vertices]
bounds={'xmin':min(p.x for p in vertices),'ymax':max(p.y for p in vertices)}
print(json.dumps(bounds),flush=True)
assert bounds['xmin']>=17-.0001 and bounds['ymax']<=26+.0001,'Road overlaps coplanar quay/yard top'
