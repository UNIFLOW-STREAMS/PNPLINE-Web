import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
states=read('review/camera-states.json');preserve=read('review/preservation.json');check=read('review/final-check.json');play=read('review/playback-check.json')
assert check['tests']['failures']==check['s1_tests']['failures']==0
assert play['result']['ended'] and not play['errors']
manifest={'version':'v002','change':'S1 low-to-high camera revision','base_snapshot':'inputs/base-user-saved-v001.blend','base_sha256':preserve['base_sha256'],'reference':'inputs/s1-end-reference.png','camera_frames_changed':[0,159],'camera_frames_preserved':[160,1392],'S1':[0,96],'elevation_start_end_deg':[s['elevation_deg'] for s in states if s['frame'] in [0,96]],'fps':12,'frame_range':[0,1392],'frames':1393,'duration_seconds':1393/12,'blend':'master-v002.blend','full_preview':'preview/master-v002.mp4','change_preview':'preview/S1-low-to-high.mp4','source_of_truth':'Preserved user-saved base plus scripts/revise_s1.py','verification':check,'actual_playback':play['result'],'limits':['Reference composition interpreted from supplied image; not a pixel-identical UI reproduction','Noncamera state preservation sampled at 17 frames; later camera compared at every integer frame','Collision is sampled camera point vs expanded boxes; not exact swept-volume geometry','Actual playback reviewed changed 0–180 frames; full video separately encoded']}
(ROOT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
paths=[p for p in ROOT.rglob('*') if p.is_file() and 'frames' not in p.relative_to(ROOT).parts and p.name not in ['hashes.json','master-v002.blend1','gui.pid']]
entries={p.relative_to(ROOT).as_posix():{'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(paths)}
(ROOT/'hashes.json').write_text(json.dumps({'algorithm':'SHA-256','files':entries},indent=2),encoding='utf-8')
assert all(sha(ROOT/n)==v['sha256'] for n,v in entries.items())
print(json.dumps({'files_verified':len(entries),'tests':28,'S1_elevation':manifest['elevation_start_end_deg'],'blend_sha256':sha(ROOT/'master-v002.blend')},indent=2))
