import hashlib
from pathlib import Path
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def require(ok,message):
 if not ok:raise ValueError(message)
def checked_file(path,sha):
 require(Path(path).is_file(),f'missing file: {path}')
 require(digest(path)==sha,f'review required: changed file {path}')
def validate_run(r):
 try:
  require(r['status']=='complete','incomplete render')
  checked_file(r['source']['path'],r['source']['sha256'])
  for p,h in r['dependencies'].items():checked_file(p,h)
  require(r['fps']>0 and r['fps_base']>0,'invalid fps')
  frames=[];paths=[]
  for i in r['images']:
   require(i['scene']==r['scene'] and i['camera']==r['camera'],'wrong scene/camera')
   require(i['source_sha256']==r['source']['sha256'],'wrong source SHA')
   require(i['run_id']==r['run_id'],'wrong render run')
   require(i['subframe']==0,'unsupported subframe')
   checked_file(i['path'],i['sha256']);frames.append(i['frame']);paths.append(str(Path(i['path']).resolve()))
  require(sorted(frames)==sorted(r['expected_frames']) and len(set(frames))==len(frames),'incomplete or duplicate frame set')
  require(set(paths)=={str(p.resolve()) for p in Path(r['output_dir']).glob('*.png')},'unrecorded/stale PNG in run')
 except (KeyError,TypeError) as e:raise ValueError(f'incomplete render record: {e}') from e
def validate_selection(s,r):
 try:
  require(s['source_sha256']==r['source']['sha256'],'selection source mismatch')
  for k in ['fps','fps_base','preview_start']:require(s[k]==r[k],f'wrong {k}')
  ids=[];frames=[]
  for p in s['panels']:
   ids.append(p['id']);f=p['frame'];frames.append(f)
   require(f in r['expected_frames'],'unrendered selection')
   require(abs(p['master_seconds']-f*r['fps_base']/r['fps'])<1e-8,'wrong master time')
   require(abs(p['preview_seconds']-(f-r['preview_start'])*r['fps_base']/r['fps'])<1e-8,'wrong preview time')
  require(len(ids)==len(set(ids)),'duplicate ID')
  require(all(a<b for a,b in zip(frames,frames[1:])),'nonchronological frames')
 except (KeyError,TypeError) as e:raise ValueError(f'incomplete selection: {e}') from e
def validate_panel(p,r):
 try:
  checked_file(p['path'],p['sha256'])
  matches=[i for i in r['images'] if i['frame']==p['frame']]
  require(len(matches)==1,'missing parent frame');i=matches[0]
  require(Path(p['raw_path']).resolve()==Path(i['path']).resolve() and p['raw_sha256']==i['sha256'],'wrong raw parent')
  checked_file(p['raw_path'],p['raw_sha256'])
 except (KeyError,TypeError) as e:raise ValueError(f'incomplete panel: {e}') from e
def validate_role(role,s):
 # Conservative state checks supplement image/continuous playback review;
 # they do not certify artistic readability from a numerical threshold.
 try:
  moving=s['speed']>.002;stopped=s['speed']<.002;yaw=abs(s['yaw'])
  closed=s['doors_closed'];opened=s['doors_open']
  if role in ['S5-01','S5-02']:ok=moving and closed and s['forward_dot']>.98
  elif role=='S5-03':ok=moving and closed and yaw<5 and s['forward_dot']>.98
  elif role=='S5-03A':ok=moving and closed and 10<yaw<175 and abs(s['yaw_change'])>.05 and s['forward_dot']>.98
  elif role=='S5-04':ok=stopped and opened and abs(yaw-180)<1 and s['dock_gap']>1
  elif role=='S5-05':ok=stopped and opened and abs(yaw-180)<1 and abs(s['dock_gap'])<.05 and s['cargo_relative_error']<.002
  else:raise ValueError('unknown role')
  require(ok,f'actual motion state does not satisfy {role}')
 except (KeyError,TypeError) as e:raise ValueError(f'incomplete state: {e}') from e
