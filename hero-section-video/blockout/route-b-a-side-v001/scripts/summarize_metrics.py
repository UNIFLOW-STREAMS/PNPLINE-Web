import json,math,statistics
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def angle(a,b):
 d=abs(sum(x*y for x,y in zip(a,b)))/math.sqrt(sum(x*x for x in a)*sum(x*x for x in b))
 return math.degrees(2*math.acos(min(1,d)))
def dist(a,b):return math.sqrt(sum((x-y)**2 for x,y in zip(a,b)))
def percentile(a,p):return sorted(a)[round((len(a)-1)*p)]
def intervals(values):
 out=[]
 for f in values:
  if out and f==out[-1][1]+1:out[-1][1]=f
  else:out.append([f,f])
 return out
reports={}
for label in ['current','candidate-b','city-final']:
 data=json.loads((R/'review'/f'{label}-metrics-raw.json').read_text());rows=[r for r in data['rows']if int(r['frame'])==r['frame']];windows={}
 for name,lo,hi in [('all',96,672),('problem_transition',171,340),('S3',216,456),('arrival',340,510),('city_reveal',96,170)]:
  rs=[r for r in rows if lo<=r['frame']<=hi];rot=[angle(a['q'],b['q'])for a,b in zip(rs,rs[1:])];speeds=[v*12 for v in rot]
  phi=[math.atan2(r['camera_ship_local'][1],r['camera_ship_local'][0])for r in rs];delta=[math.degrees((b-a+math.pi)%math.tau-math.pi)for a,b in zip(phi,phi[1:])];signs=[1 if v>0 else -1 for v in delta if abs(v)>.2]
  windows[name]={'frames':[lo,hi],'camera_rotation_total_deg':sum(rot),'peak_deg_s':max(speeds),'p95_deg_s':percentile(speeds,.95),'peak_angular_accel_deg_s2':max(abs(b-a)*12 for a,b in zip(speeds,speeds[1:])),'ship_relative_azimuth_travel_deg':sum(abs(d)for d in delta),'azimuth_reversals_over_0_2_deg_step':sum(a!=b for a,b in zip(signs,signs[1:])),'max_camera_step_m':max(dist(a['camera'],b['camera'])for a,b in zip(rs,rs[1:]))}
 blocked=[r['frame']for r in rows if any(r['occluders'])];full=[r['frame']for r in rows if all(r['occluders'])];off=[r['frame']for r in rows if not any(0<=u[0]<=1 and 0<=u[1]<=1 and u[2]>0 for u in r['uv'])]
 collisions={}
 for r in rows:
  for n in r['hull_environment_collisions']:collisions.setdefault(n,[]).append(r['frame'])
 motion=[r for r in rows if 145<=r['frame']<=510];vs=[dist(a['ship'],b['ship'])*12 for a,b in zip(motion,motion[1:])]
 reports[label]={'file':data['file'],'sha256':data['sha256'],'windows':windows,'any_occlusion_intervals':intervals(blocked),'all_points_occluded_intervals':intervals(full),'all_ship_samples_offscreen':intervals(off),'hull_triangle_overlap_intervals':{k:intervals(v)for k,v in collisions.items()},'min_camera_static_distance_m':min(r['nearest_environment_distance']for r in rows),'min_camera_radial_height_m':min(r['camera_radial_height']for r in rows),'peak_ship_speed_m_s':max(vs),'peak_ship_accel_m_s2':max(abs(b-a)*12 for a,b in zip(vs,vs[1:])),'peak_ship_rotation_deg_s':max(angle(a['ship_q'],b['ship_q'])*12 for a,b in zip(motion,motion[1:]))}
(R/'review/metrics-summary.json').write_text(json.dumps(reports,indent=2));print(json.dumps(reports,indent=2))
