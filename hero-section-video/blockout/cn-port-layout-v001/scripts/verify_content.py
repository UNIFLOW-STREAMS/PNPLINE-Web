import bpy,json,sys,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;label=sys.argv[sys.argv.index('--')+1]if '--'in sys.argv else 'after'
checks={'terminal_root':'PORT_MODEL_ROOT'in s.objects,'dense_container_yard':len([o for o in s.objects if o.name.startswith('PORT_CONTAINER_')and o.type=='EMPTY'])>=40,'two_companion_cranes':len([o for o in s.objects if o.name.startswith('PORT_COMPANION_CRANE_')])==2,'original_working_crane_present':'CR_COMPACT_GANTRY'in s.objects,'relocated_berth':'PORT_BERTH_PLACEMENT'in s.objects}
(R/'review'/f'{label}-content.json').write_text(json.dumps({'checks':checks,'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()},indent=2));print(checks);assert all(checks.values())
