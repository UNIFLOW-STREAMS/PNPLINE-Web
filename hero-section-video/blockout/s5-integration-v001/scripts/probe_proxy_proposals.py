import bpy,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R.parent/'s5-dock-test-v001/scripts'));from geometry import hull,overlap
s=bpy.data.scenes['PNPLINE_MASTER_v005'];bpy.context.window.scene=s
body=[bpy.data.objects['A01_'+n] for n in ['FLOOR','ROOF','SIDE_L','SIDE_R','FRONT']];doors=[bpy.data.objects['A01_DOOR_'+n+'_LEAF'] for n in ['LEFT','RIGHT']];hinges=[bpy.data.objects['A01_DOOR_'+n] for n in ['L','R']];results={}
for name,x,height in [('original',-1.6,1.5),('hinge_only',-1.65,1.5),('test_repairs',-1.65,1.24)]:
 for o in hinges:o.location.x=x
 for o in doors:o.scale.z=height/1.5
 maxima={}
 for j in range(810*4,901*4):
  f=j/4;s.frame_set(int(f),subframe=f%1)
  for a in doors:
   for b in body+[bpy.data.objects['DOCK_BRIDGE']]:
    d=overlap(*hull(a),*hull(b));key=a.name+'/'+b.name
    if d>maxima.get(key,{}).get('depth',0):maxima[key]={'frame':f,'depth':d}
 results[name]=maxima
print(json.dumps(results,indent=2));(R/'review/proxy-proposals.json').write_text(json.dumps(results,indent=2))
