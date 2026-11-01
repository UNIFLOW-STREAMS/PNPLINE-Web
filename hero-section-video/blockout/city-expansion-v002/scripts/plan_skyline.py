"""Add an authored rear-city skyline without moving the accepted 151 buildings."""
import copy,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'scripts'))
from verify_geometry import rect,segment_rect,polygon_distance,inside,overlap,layout_report
base=json.loads((R.parent/'city-expansion-v001/scripts/dense_layout.json').read_text())
data=copy.deepcopy(base)
region=[(-38,53),(-40,73),(-23,91),(3,95),(30,92),(57,79),(82,64),(83,45),(70,40),(30,40),(25,39),(-10,60),(-25,52)]
data['allowed_building_regions']['REAR']=region
data['schema']='city-expansion-skyline-v3'
occupied=[rect(*b['xy'],b['size'][0]+.44,b['size'][1]+.44,b['yaw']) for b in base['buildings']]
roads=[segment_rect(a,b,r['width']+.7) for r in data['roads'] for a,b in zip(r['points'],r['points'][1:])]
protected=[x['poly'] for x in base['protected_source_foundations']]
protected += [rect(55.5,31.15,53,16.5),rect(0,8.2,34.4,8.4),rect(27,29.5,24,7),rect(33,19,14,22),rect(90,29,42,28)]
parks=[p['poly'] for p in data['reserved_plazas']]
added=[]
def acceptable(x,y,w,d,yaw=0,landmark=False):
    p=rect(x,y,w+.44,d+.44,yaw)
    return (all(inside(v,region) for v in p)
            and all(polygon_distance(p,q)>=.5 for q in occupied+roads+protected)
            and all(overlap(p,q)<.001 for q in parks))
def add(name,x,y,w,d,h,kind='office',yaw=0,landmark=None):
    if not acceptable(x,y,w,d,yaw,landmark):return False
    spec={'name':name,'xy':[x,y],'size':[w,d,h],'kind':kind,'yaw':yaw,'landmark':landmark,'district':'REAR'}
    data['buildings'].append(spec);added.append(spec);occupied.append(rect(x,y,w+.44,d+.44,yaw));return True
landmarks=[('CE_REAR_ONE_WTC',35,44,7,7,50,'one_world_trade_center'),
           ('CE_REAR_SPACE_NEEDLE',-13,67,6,6,36,'space_needle'),
           ('CE_REAR_ROCKEFELLER',50,44,7,5,36,'rockefeller_plaza')]
for name,x,y,w,d,h,kind in landmarks:
    assert add(name,x,y,w,d,h,landmark=kind),f'Authored landmark footprint invalid: {name}'
    parks.append(rect(x,y,w+1.2,d+1.2))
    data['reserved_plazas'].append({'name':name+'_PLAZA','poly':parks[-1]})
# Small blocks fill available plots beside existing streets. The first pass is
# a regular street grid; a second offset grid fills remaining larger parcels.
# Heights form a lower supporting tier around the three distinct landmarks.
for offset in [0,2.7]:
    for row in range(9):
        y=46+row*5.4+offset
        for column in range(21):
            x=-28+column*5.4+offset
            k=row*21+column
            w,d=[(3.5,3.6),(3.9,3.35),(3.4,4.0),(3.8,3.7)][k%4]
            h=round(10.5+(k*7%11)*.67,2)
            if x>25 and y<65:h+=2.5
            if x<-15:h-=1.5
            if y>78:h-=2
            name=f'CE_REAR_BLOCK_{len(added)-3:02}'
            add(name,round(x,2),round(y,2),w,d,h,kind='masonry' if k%3==0 else 'office',yaw=-.25 if x>10 else -.12)
            if len(added)>=51:break
        if len(added)>=51:break
    if len(added)>=51:break
# Secondary towers occupy specific letter gaps verified by ray tests from
# f300/315. Nearby support remains lower than the landmark crowns.
heights={1:28,6:24,8:42,9:36,12:37,15:40,20:25}
for b in added:
    if b['name'].startswith('CE_REAR_BLOCK_'):
        index=int(b['name'].rsplit('_',1)[-1])
        if index in heights:b['size'][2]=heights[index]
data['counts']['REAR']=len(added)
coast=json.loads((R/'scripts/left_skyline_candidates.json').read_text())
assert coast['status']=='FINAL' and coast['qa']['passed']
data['allowed_building_regions']['COAST']=[(-38,40),(-20,40),(-20,65),(-38,65)]
for candidate in coast['candidates']:
    spec={key:candidate[key] for key in ['name','xy','size','yaw','kind','landmark','district']}
    data['buildings'].append(spec);added.append(spec)
data['counts']['COAST']=len(coast['candidates'])
data['skyline_additions']={'baseline_buildings':151,'new_buildings':len(added),'landmarks':3,'surrounding_buildings':len(added)-3,'coast_buildings':len(coast['candidates']),'camera_validation_frames':[300,315,330,349],'placement_contract':'New skyline frames USA; all accepted building placements and all six roads remain exact.'}
report=layout_report(data)
issues={k:v for k,v in report.items() if isinstance(v,list) and v}
assert not issues,json.dumps(issues,indent=2)
(R/'scripts/dense_layout.json').write_text(json.dumps(data,indent=2))
(R/'review/skyline-layout.json').write_text(json.dumps({'added':added,'layout':report},indent=2))
print(json.dumps(data['skyline_additions'],indent=2))
