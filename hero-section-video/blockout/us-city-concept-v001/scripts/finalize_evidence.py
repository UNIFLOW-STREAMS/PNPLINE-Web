"""Record final read-only integrity, metadata and local review link checks."""
from pathlib import Path
import hashlib,json,subprocess
from html.parser import HTMLParser
R=Path(__file__).resolve().parents[1]
repo=R.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,d):p.write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf-8')
def git(*args):return subprocess.check_output(['git','-c','safe.directory=F:/pnpline-landing',*args],cwd=repo,text=True)
original=R.parent/'previz-crane-height-v002/master-previz-crane-height-v002.blend'
candidate=R/'candidate-us-city-concept-v004.blend'
info={'source_sha256':sha(original),'input_copy_sha256':sha(R/'inputs/base.blend'),'candidate_sha256':sha(candidate),'head':git('rev-parse','HEAD').strip(),'tracked_diff':git('diff','HEAD','--stat'),'staged_diff':git('diff','--cached','--stat')}
assert info['source_sha256']==info['input_copy_sha256']=='e29fe506211d1b7f647f3eee01e066e49319aaae29dffebc6e4ed82aca371af3'
assert not info['tracked_diff'] and not info['staged_diff']
put(R/'review/source-integrity.json',info)
(R/'review/git-status-after.txt').write_text(git('status','--short'),encoding='utf-8')
scale=R/'review/statue-scale-comparison-final/metadata.json'
if scale.exists():
 d=json.loads(scale.read_text());d['source_sha256']=sha(candidate);put(scale,d)
put(R/'review/playback-review.json',{'source_sha256':sha(candidate),'frames':[300,720],'fps':12,'frame_count':421,'duration':35.083333,'browser':'Codex in-app browser / local HTTP only','rate':1,'both_ended_at':35.083333,'observations':['Paired videos started at 0 and reached ended=true at 35.083333, rate 1, no video error.','Screenshots observed at start, around 14.4s and 25s, and end; these are discrete visual observations, not continuous human vision.','Actual arrival statue and city title clipping remain.','Working crane/ship remain visible in sampled docking playback; late f900,1200,1392 stills show protected truck/warehouse area.'],'limits':['No all-timeline normal playback.','No proof of every-frame occlusion or artistic acceptance.']})
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[]
 def handle_starttag(self,tag,attrs):
  for k,v in attrs:
   if k in ('href','src') and v and not v.startswith(('http:','https:','#','data:')):self.links.append(v)
parser=Links();parser.feed((R/'review.html').read_text(encoding='utf-8'))
missing=[x for x in parser.links if not (R/x).is_file() and x!='hashes.json']
assert not missing,missing
put(R/'review/package-check.json',{'candidate_sha256':sha(candidate),'review_links':len(parser.links),'missing':missing,'source_integrity':True})
print('FINAL_EVIDENCE_OK',info)
