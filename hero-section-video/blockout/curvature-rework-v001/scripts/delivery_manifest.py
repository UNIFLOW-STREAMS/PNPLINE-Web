import json,hashlib,re
from pathlib import Path
R=Path(__file__).resolve().parents[1];candidate=R/'candidate-curvature-v004.blend'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
hash=sha(candidate)
checks=['candidate-curvature-v004-build.json','candidate-curvature-v004-clearance.json','candidate-curvature-v004-preservation.json','video-v004.json']
for name in checks:assert json.loads((R/'review'/name).read_text())['candidate_sha256']==hash,name
assert json.loads((R/'review/reproduction.json').read_text())['first_sha256']==hash
assert json.loads((R/'review/final-v004/metadata.json').read_text())['sha256']==hash
html=(R/'review.html').read_text(encoding='utf-8-sig')
for target in re.findall(r'(?:src|href)="([^"]+)"',html):
 if not target.startswith(('http','data:','#')):assert (R/target).is_file(),target
files=[candidate,R/'preview/us-curvature-v004.mp4',R/'review.html',R/'report.md',R/'README.md']
files+=list((R/'scripts').glob('*.py'))+list((R/'tests').glob('*.py'))+[R/'review'/n for n in checks]
files+=[R/'review/reproduction.json',R/'review/tests-v004.log',R/'review/audits-v004.log',R/'review/final-review.md']
result={'candidate':candidate.name,'candidate_sha256':hash,'branch':'main','tests':16,'clearance_samples':3126,'deferred_minor':'Concealed port foundation section inversion; see report.md.','files':{str(p.relative_to(R)).replace('\\','/'):sha(p) for p in files}}
(R/'delivery-manifest.json').write_text(json.dumps(result,indent=2));print('DELIVERY',len(files),'files, candidate',hash)
