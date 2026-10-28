"""Publish registry only after hash-bound checks and media have completed."""
import json,hashlib,datetime
from pathlib import Path
R=Path(__file__).resolve().parents[1];d=json.loads((R/'delivery.json').read_text());master=Path(d['file']);sha=hashlib.sha256(master.read_bytes()).hexdigest();assert sha==d['sha256'];stem=master.stem
reports={'shore_and_cab':'final-gate.json','crane_vs_environment_ship_cargo':f'{stem}-dense.json','crane_internal':f'{stem}-internal.json','scope_and_timing':f'{stem}-scope.json','coast_connection': 'final-coast-connection.json'};results={}
for name,path in reports.items():
 data=json.loads((R/'review'/path).read_text());assert data['sha256']==sha,(name,'stale evidence');passed=data.get('pass',all(data.get('checks',{}).values()));assert passed,name
 results[name]={'passed':passed,'report':'review/'+path,'checks':data.get('checks'),'samples':data.get('samples',data.get('frames'))}
metadata=json.loads((R/'review/after-final/metadata.json').read_text());assert metadata['sha256']==sha;assert metadata['frames']==list(range(0,673,3))
for label in ['before','after']:
 media=json.loads((R/f'preview/{label}-metadata.json').read_text());assert abs(float(media['ffprobe']['format']['duration'])-673/12)<.05
 assert hashlib.sha256((R/f'preview/{label}.mp4').read_bytes()).hexdigest()==media['file_sha256']
raw=json.loads((R/'review/candidate-v003-coarse-collisions.json').read_text());legacy={k:{'first':min(v),'last':max(v),'samples':len(v)} for k,v in raw.items() if not any(x in k for x in ['CR_','SF_','CN_','SHIP','P03'])}
(R/'review/preserved-warehouse-contact-audit.json').write_text(json.dumps({'meaning':'Unchanged baseline S4-S7 contacts, not claimed collision-free by this city-rotation correction. Includes intended floor/rail/landing tangency and inherited forklift/support geometry. Whole-frame original transforms and geometry are verified unchanged.','raw_contacts':legacy},indent=2))
summary={'file':str(master),'sha256':sha,'results':results,'normal_connections':['engaged twistlocks f0-81','slew bearing','container seating surfaces on ship and trailer'],'preserved_baseline_contacts':'review/preserved-warehouse-contact-audit.json','preview':{'frames':[0,672],'step':3,'source_fps':12,'display_default_speed':3.5},'independent_review':{'blocking_finding':'Stay/trolley-wheel interference','resolution':'Outboard stay anchors and supporting end cross-members; internal regression failed before and passed after; six bad pairs removed','baseline_internal_report':'review/master-previz-city-rotation-fix-v001-internal.json'},'scope':'City rotation collision/interference correction, not a new S4-S7 warehouse redesign'}
(R/'verification-summary.json').write_text(json.dumps(summary,indent=2))
d.update(status='Verified: city-rotation collision correction complete',verification=str(R/'verification-summary.json'),review_page='http://127.0.0.1:18777/review.html',supersedes=str(R.parent/'previz-city-rotation-v001/master-previz-city-rotation-v001.blend'),scope=summary['scope']);(R/'delivery.json').write_text(json.dumps(d,indent=2))
registry=R.parent/'latest-previz.json';old=json.loads(registry.read_text(encoding='utf-8-sig'));expected='ce36841b9e3418efe1611fdbd9645b6ed9d332ff5db4278974024274d9d6cebb';assert old['sha256'] in [expected,sha],'Latest registry changed independently'
if old['sha256']!=sha:(R/'inputs/previous-latest-previz.json').write_text(json.dumps(old,indent=2))
registry.write_text(json.dumps({'file':str(master),'sha256':sha,'adopted_on':'2026-10-29','choice':'city rotation, collision corrected','delivery':str(R/'delivery.json'),'verification':str(R/'verification-summary.json'),'known_issues':['Pre-existing S4-S7 warehouse contact geometry preserved; see scoped audit'],'status':'Adopted; city-rotation collision gates passed'},indent=2))
print('VERIFIED_AND_REGISTERED',master,sha)
