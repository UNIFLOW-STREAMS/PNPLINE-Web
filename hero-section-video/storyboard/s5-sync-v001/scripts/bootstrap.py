from pathlib import Path
import hashlib,json,subprocess,shutil
R=Path(__file__).resolve().parents[1]; repo=R.parents[2]
source=repo/'hero-section-video/blockout/s5-integration-v001'
for name in ['inputs','master','tests','logs','review','raw','line-art','panels','preview']:(R/name).mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
master=source/'master-s5-integration-v001.blend'
snapshot=R/'master/source-current.blend';assert not snapshot.exists();shutil.copy2(master,snapshot)
old=R/'inputs/committed-stage2.blend'
old.write_bytes(subprocess.check_output(['git','-c',f'safe.directory={repo}','show','HEAD:hero-section-video/blockout/s5-integration-v001/master-s5-integration-v001.blend'],cwd=repo))
meta={'source':str(master),'source_sha256':sha(master),'snapshot':str(snapshot),'snapshot_sha256':sha(snapshot),'committed_sha256':sha(old),'git_head':subprocess.check_output(['git','-c',f'safe.directory={repo}','rev-parse','HEAD'],cwd=repo,text=True).strip(),'git_status':subprocess.check_output(['git','-c',f'safe.directory={repo}','status','--short'],cwd=repo,text=True),'model':'unconfirmed','reasoning_effort':'unconfirmed'}
(R/'inputs/source.json').write_text(json.dumps(meta,indent=2),encoding='utf8')
for name in ['README.md','report.md','config.json','frame-manifest.json','time-map.json','hashes.json','boundary-states.json','source-map.json']:
 shutil.copy2(source/name,R/'inputs'/('stage2-'+name))
for name in ['notion-s5.md','notion-s6.md']:shutil.copy2(source/'inputs'/name,R/'inputs'/name)
print(json.dumps(meta,indent=2))
