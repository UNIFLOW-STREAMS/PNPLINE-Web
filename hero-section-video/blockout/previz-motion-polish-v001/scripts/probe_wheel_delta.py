import bpy,json,sys,numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));from motion import TimeMap
c=json.loads((R/'config.json').read_text());m=TimeMap(1392,c['easing']);times=np.arange(m.forward(649),m.forward(890),1/128);src=[m.inverse(t) for t in times]
def zcurves():return {o.name:next(fc for l in o.animation_data.action.layers for st in l.strips for b in st.channelbags if b.slot_handle==o.animation_data.action_slot.handle for fc in b.fcurves if fc.data_path=='location' and fc.array_index==2) for o in bpy.context.scene.objects if o.name.startswith('A03') and '_WHEEL_' in o.name}
bpy.ops.wm.open_mainfile(filepath=str(R/'inputs/source.blend'));values={n:np.array([fc.evaluate(t) for t in src]) for n,fc in zcurves().items()}
bpy.ops.wm.open_mainfile(filepath=str(R/'master-motion-polish-A.blend'));rows=[]
for n,fc in zcurves().items():
 d=np.array([fc.evaluate(t) for t in times])-values[n];i=np.argmax(np.abs(d));rows.append({'wheel':n,'max_delta':float(d[i]),'output':float(times[i]),'source':src[i]})
(R/'review/wheel-delta.json').write_text(json.dumps(rows,indent=2));print('DELTAS',json.dumps(rows),flush=True)
