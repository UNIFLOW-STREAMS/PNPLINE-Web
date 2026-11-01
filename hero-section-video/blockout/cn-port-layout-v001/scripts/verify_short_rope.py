import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;s.frame_set(0)
label=sys.argv[sys.argv.index('--')+1]if '--'in sys.argv else 'after'
I=s.objects['SF_CN_LAYOUT'].matrix_world.inverted()
cables=[o for o in s.objects if o.name.startswith('CR_WORKING_CABLE')]
lengths={o.name:o.scale.z for o in cables}
height=(I@s.objects['A01_CONTAINER'].matrix_world.translation).z
checks={'four_short_start_ropes':len(lengths)==4 and all(.15<x<.21 for x in lengths.values()),'container_start_above_7_94':height>7.94}
r={'file':bpy.data.filepath,'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'checks':checks,'lengths_m':lengths,'container_height':height}
(R/'review'/f'{label}-short-rope.json').write_text(json.dumps(r,indent=2));print(r);assert all(checks.values())
