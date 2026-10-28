import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;s.frame_set(156);inv=s.objects['SF_CN_LAYOUT'].matrix_world.inverted()
def pts(o):return [inv@o.matrix_world@v.co for v in o.data.vertices]
water=pts(s.objects['SF_BASIN_WATER_SURFACE']);outer=water[:96];inner=water[96:]
def distance(p,a,b):
 p,a,b=[Vector((v.x,v.y))for v in (p,a,b)];d=b-a;t=max(0,min(1,(p-a).dot(d)/d.length_squared));return (p-a-t*d).length
def within(p,poly):
 inside=False
 for i,a in enumerate(poly):
  b=poly[(i+1)%len(poly)]
  if (a.y>p.y)!=(b.y>p.y) and p.x<(b.x-a.x)*(p.y-a.y)/(b.y-a.y)+a.x:inside=not inside
 return inside
def inwater(p):return within(p,outer) and not within(p,inner)
tip=[p for p in inner if p.x>6 and 18<p.y<20]
widths=[min(distance(p,outer[i],outer[(i+1)%96])for i in range(96))for p in tip]
letters={}
for ch in 'NA':
 ps=pts(s.objects['SF_CHINA_GOLD_'+ch]);z=min(p.z for p in ps);feet=[p for p in ps if p.z<z+.15]
 letters[ch]=sum(inwater(p)for p in feet)
result={'rightmost_water_x':max(p.x for p in outer),'right_bend_min_width':min(widths),'letter_foot_samples_in_water':letters}
result['width_samples']=[{'point':list(p),'width':width}for p,width in zip(tip,widths)]
result['crane_foot_samples_in_water']={o.name:sum(inwater(inv@o.matrix_world@Vector(p))for p in o.bound_box if p[2]==min(v[2]for v in o.bound_box)) for o in s.objects if o.name.startswith('SF_CRANE_LEG')}
wall=pts(s.objects['SF_BASIN_OUTER_WALL']);land=pts(s.objects['SF_FRONT_LAND'])[96:]
result['edge_seam_error']=max(math.hypot(p.x-q.x,p.y-q.y)for ring in [wall[:96],wall[96:],land]for p,q in zip(outer,ring))
coastline=pts(s.objects['SF_FRONT_LAND'])[:96]
result['opening_inside_coast']=all(within(p,coastline)for p in outer)
suffix=sys.argv[sys.argv.index('--')+1]
if suffix!='baseline':
 base=json.loads((R/'review/waterway-baseline.json').read_text())
 result['tests']={'extends_toward_na':result['rightmost_water_x']>10.5,'visible_turn_remains_wide':min(widths)>2.0,'seamless':result['edge_seam_error']<.001,'no_new_letter_foot_flooding':all(letters[k]<=base['letter_foot_samples_in_water'][k]for k in letters),'no_new_crane_foot_flooding':all(n<=base['crane_foot_samples_in_water'][k]for k,n in result['crane_foot_samples_in_water'].items())}
 result['tests']['opening_inside_coast']=result['opening_inside_coast']
(R/f'review/waterway-{suffix}.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if suffix!='baseline':assert all(result['tests'].values()),'Waterway must extend toward NA, remain wide, join banks and preserve letter footing'
