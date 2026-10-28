"""Measure C's lower rim against the actual water edge and preserve other objects."""
import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;s.frame_set(156)
inv=s.objects['SF_CN_LAYOUT'].matrix_world.inverted()
o=s.objects['SF_CHINA_GOLD_C'];points=[inv@o.matrix_world@v.co for v in o.data.vertices]
low=min(p.z for p in points);rim=[p for p in points if p.z<low+.45]
w=s.objects['SF_BASIN_WATER_SURFACE'];edge=[inv@w.matrix_world@v.co for v in w.data.vertices[:96]]
def distance(p,a,b):
 p,a,b=[Vector((v.x,v.y))for v in (p,a,b)];d=b-a;t=max(0,min(1,(p-a).dot(d)/d.length_squared));return (p-a-t*d).length
gap=min(distance(p,edge[i],edge[(i+1)%len(edge)])for p in rim for i in range(len(edge)))
root=s.objects['SF_CHINA_C'];result={'c_water_gap':gap,'c_position':list(root.location)}
args=sys.argv[sys.argv.index('--')+1:]
if args[0]=='baseline':
 (R/'review/c-wrap-baseline.json').write_text(json.dumps(result,indent=2))
else:
 old=json.loads((R/'review/c-wrap-baseline.json').read_text());result['old_gap']=old['c_water_gap']
 result['closer']=gap<old['c_water_gap']*.75
 result['forward_shift']=root.location.y<old['c_position'][1]-4
 (R/f'review/c-wrap-{args[0]}.json').write_text(json.dumps(result,indent=2))
 print(json.dumps(result));assert result['closer'] and result['forward_shift'],'C must move forward and close at least 25% of its water gap'
