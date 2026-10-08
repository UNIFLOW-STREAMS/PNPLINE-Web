import bpy,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R.parent/'s5-dock-test-v001/scripts'));from geometry import hull,overlap
s=bpy.data.scenes['PNPLINE_MASTER_v005'];bpy.context.window.scene=s
body=[bpy.data.objects['A01_'+n] for n in ['FLOOR','ROOF','SIDE_L','SIDE_R','FRONT']];doors=[bpy.data.objects['A01_DOOR_'+n+'_LEAF'] for n in ['LEFT','RIGHT']];bridge=bpy.data.objects['DOCK_BRIDGE'];pairs=[(x,y) for x in doors for y in body+[bridge]]
maxima={};samples=[]
for j in range(810*4,901*4):
 f=j/4;s.frame_set(int(f),subframe=f%1)
 for x,y in pairs:
  d=overlap(*hull(x),*hull(y));key=x.name+' / '+y.name
  if d>maxima.get(key,{}).get('depth',0):maxima[key]={'frame':f,'depth':d}
  if d>.01 and f in [810,820,826,832,842,890,900]:samples.append({'frame':f,'pair':key,'depth':d})
out={'maximums':maxima,'selected':samples};(R/'review/proxy-conflicts.json').write_text(json.dumps(out,indent=2));print(json.dumps(maxima,indent=2))
