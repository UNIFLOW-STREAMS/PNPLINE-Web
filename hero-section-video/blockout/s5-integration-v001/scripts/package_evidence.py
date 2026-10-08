"""Package actual rendered frames and evaluated motion metadata; no scene edits."""
import json,hashlib,shutil,subprocess
from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,v):(R/n).write_text(json.dumps(v,indent=2,ensure_ascii=False),encoding='utf8')
blend=R/'master-s5-integration-v001.blend';revision=sha(blend);base=json.loads((R/'review/base-survey.json').read_text());donor=json.loads((R/'review/donor-current.json').read_text());motion=json.loads((R/'review/motion-audit.json').read_text());cfg=json.loads((R/'config.json').read_text())
assert revision==motion['candidate_sha256']
candidate_frames=[('S5-01',672,'부두 출발'),('S5-02',720,'연결도로·목적지 접근 / 보호 경계'),('S5-03',766,'선택된 전진 선회'),('S5-03A',810,'정렬·정지'),('S5-04',842,'문 개방·고정 완료, 후진 전'),('S5-05',900,'접안·정지, 입고 전')]
manifest=[]
for label,f,event in candidate_frames:
 target=R/'review'/f'{label}-f{f}.png';shutil.copyfile(R/'preview/main-frames'/f'{f:04d}.png',target)
 manifest.append({'label':label,'frame':f,'master_time_seconds':f/12,'preview_time_seconds':(f-624)/12,'event':event,'camera':'CAM_MASTER','blend_sha256':revision,'file':target.relative_to(R).as_posix(),'sha256':sha(target)})
save('frame-manifest.json',{'blend_sha256':revision,'fps':12,'candidates':manifest,'selection':'③ final storyboard choice remains with user'})
mapping=[];dmap={o['name']:o for o in donor['inventory']};bmap={o['name']:o for o in base['inventory']}
names=['A03_TRACTOR','A03_TRAILER','TRACTOR_HITCH','TRAILER_HITCH','A01_CONTAINER','A01_DOOR_L','A01_DOOR_R','W01_NEW_PALLET','W01_REMAINING_CONTAINER_CARGO','DOCK_TARGET','DOCK_BRIDGE','CAM_MASTER','CAM_LOOK_TARGET']+[n for n in bmap if n.startswith('A03') and '_WHEEL_' in n]
for n in names:
 b=bmap[n];d=dmap.get('S5T__'+n)
 mapping.append({'destination':n,'donor':d['name'] if d else None,'base_parent':b['parent'],'base_rotation':b['rotation'],'donor_parent':d['parent'] if d else None,'donor_rotation':d['rotation'] if d else None,'constraints':b['constraints'],'drivers':b['drivers'],'nla':b['nla'],'treatment':'Existing object retained; evaluated world/quaternion bake for roots; selected route logic verified against donor evaluation. Static environment unchanged except separately approved bridge. Existing master camera independently connected; donor camera not copied.'})
save('source-map.json',{'base_sha256':cfg['base_sha256'],'donor_sha256':cfg['donor_sha256'],'objects':mapping,'proxy_policy':{'tandem_spacing':1,'door_height':1.43,'hinge_x':-1.65,'bridge_width':1.34,'bridge_center_z':1.88,'approval':'Explicit user replies for hinge and bridge/lower-door repair; all static across timeline.'}})
events=[{'donor_frame':648,'master_frame':720,'event':'H position; master already moving, donor stationary start not copied'},{'donor_frame':746,'master_frame':None,'event':'B representative turn state'}]
dp=next(r for r in donor['rows'] if r['frame']==746)['objects']['A03_TRAILER']['p'];nearest=min(motion['motion'],key=lambda r:sum((r['trailer'][i]-dp[i])**2 for i in [0,1]));events[1]['master_frame']=nearest['frame'];events[1]['position_error_m']=sum((nearest['trailer'][i]-dp[i])**2 for i in [0,1])**.5
events += [{'donor_frame':f,'master_frame':f,'event':label} for f,label in [(810,'aligned and stopped'),(811,'doors start'),(842,'doors fixed'),(849,'reverse starts'),(890,'docked'),(900,'S5 end / S6 start')]]
save('time-map.json',{'fps':12,'F_lock':720,'F_rejoin':948,'delta_frames':0,'events':events,'approach_mapping':'Monotone quintic distance progress from current f720 velocity to selected route end f810; master starts already in motion. Donor time is not linearly copied. Spatial path and hitch geometry reused.'})
grid=Image.new('RGB',(1440,540),'#222222');draw=ImageDraw.Draw(grid)
for i,row in enumerate(manifest):
 im=Image.open(R/row['file']).resize((480,270));grid.paste(im,(i%3*480,i//3*270));draw.text((i%3*480+6,i//3*270+6),row['label']+' / f'+str(row['frame']),fill='white',stroke_width=2,stroke_fill='black')
grid.save(R/'review/candidates.jpg')
probes={}
for n in ['main','top']:
 p=R/'preview'/f'{n}.mp4';j=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,nb_read_frames,duration','-of','json',str(p)]));subprocess.run(['ffmpeg','-v','error','-i',str(p),'-f','null','-'],check=True);probes[n]={'file_sha256':sha(p),'blend_sha256':revision,'probe':j,'decode_exit':0,'frames':[624,948],'speed':'12fps original timeline, no cuts or retiming'}
save('review/video-probe.json',probes)
points=' '.join(f'{40+r["trailer"][0]*10:.2f},{450-r["trailer"][1]*10:.2f}' for r in motion['motion'] if r['frame']<=890)
svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="800" height="500"><rect width="800" height="500" fill="#f7f7f2"/><rect x="400" y="60" width="320" height="140" fill="#b5cfc5"/><text x="480" y="90">Existing warehouse</text><polyline points="{points}" fill="none" stroke="#086aab" stroke-width="3"/><text x="50" y="475">US local coordinates; evaluated trailer axle path f720–890</text><circle cx="400" cy="160" r="5" fill="#cc5522"/><text x="410" y="180">Dock x36,y29</text></svg>'
(R/'review/evaluated-path.svg').write_text(svg)
hashes={'base':{'path':str(R.parent/'s4-s5-boundary-v001/master-s4-s5-boundary-v001.blend'),'sha256':sha(R.parent/'s4-s5-boundary-v001/master-s4-s5-boundary-v001.blend')},'donor':{'path':str(R.parent/'s5-dock-test-v001/master-with-s5-test-v001.blend'),'sha256':sha(R.parent/'s5-dock-test-v001/master-with-s5-test-v001.blend')},'outputs':{str(p.relative_to(R)).replace('\\','/'):sha(p) for p in [blend,R/'config.json',R/'preview/main.mp4',R/'preview/top.mp4',*[R/m['file'] for m in manifest]]}}
assert hashes['base']['sha256']==cfg['base_sha256'];assert hashes['donor']['sha256']==cfg['donor_sha256'];save('hashes.json',hashes);print('PACKAGED',revision)
