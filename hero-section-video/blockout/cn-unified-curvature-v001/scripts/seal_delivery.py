"""Seal passed reports and point the workspace at the final revised master."""
import hashlib,json
from pathlib import Path
from datetime import datetime,timezone

ROOT=Path(__file__).resolve().parents[1];REVIEW=ROOT/'review'
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def write(path,data):path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(path):
    with path.open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()

def main():
    delivery=read(ROOT/'delivery.json');path=Path(delivery['file']);source=Path(delivery['source'])
    digest=sha(path);assert digest==delivery['sha256'];assert sha(source)==delivery['source_sha256']
    geo=read(REVIEW/'curvature-verification.json');anim=read(REVIEW/'animation-verification.json');package=read(REVIEW/'package.json')
    for report in [geo,anim,package]:assert report.get('candidate_sha256',report.get('sha256'))==digest
    assert all(geo['checks'].values()) and all(anim['checks'].values())
    assert package['curvature_verification_passed'] and not package['draft']
    assert package['matching_diagnostic_camera_poses'] and package['source_unchanged']
    time_map=read(source.parent/'time-map.json');time_map['output_sha256']=digest
    time_map['curvature_base']=str(source);time_map['curvature_base_sha256']=delivery['source_sha256']
    time_map['curvature_note']='Timing unchanged. China layout is spherical; opening camera and loading system are spatially compensated. Original US timing and transforms are retained.'
    write(ROOT/'time-map.json',time_map)
    checks={'geometry_'+k:v for k,v in geo['checks'].items()};checks.update({'animation_'+k:v for k,v in anim['checks'].items()})
    counts=delivery['districts']['building_counts'];buildings=sum(counts[k]for k in ['hutong_roof_buildings','lowrise_houses','qilou','midrise'])
    summary={'file':str(path),'candidate_sha256':digest,'source_sha256':delivery['source_sha256'],
             'all_checks_pass':True,'checks':checks,'ground':geo['ground'],
             'original_static_groups_radially_aligned':len(delivery['static_clusters']),
             'protected_US_objects':geo['US_protected_count'],'landmark_count':13,'surrounding_buildings':buildings,
             'temple_of_heaven_scale':1.5,'reports':['curvature-verification.json','animation-verification.json'],
             'review':str(ROOT/'review.html')}
    write(REVIEW/'verification-summary.json',summary)
    delivery.update({'status':'Complete: visual review, connected spherical ground, radial structures and animation checks passed',
                     'completed_at_utc':datetime.now(timezone.utc).isoformat(),'checks':checks,'all_checks_pass':True,
                     'verification':str(REVIEW/'verification-summary.json'),'review':str(ROOT/'review.html'),
                     'preview':str(REVIEW/'after-diagnostic/hero.png'),'time_map':str(ROOT/'time-map.json'),
                     'surrounding_building_count':buildings,'source_preserved':True,
                     'camera_note':'Only spatial compensation required by spherical China terrain; original shot timing and lenses retained. Original camera/actors exact from frame253.'})
    artifacts=[ROOT/'README.md',ROOT/'review.html',ROOT/'time-map.json']
    artifacts += [REVIEW/n for n in ['verification-summary.json','curvature-verification.json','animation-verification.json','package.json','actual-camera-contact.jpg','diagnostic-contact.jpg']]
    for folder in ['after-diagnostic','after-actual','before-diagnostic','before-actual']:
        artifacts.extend(sorted((REVIEW/folder).glob('*.png')));artifacts.append(REVIEW/folder/'metadata.json')
    delivery['artifact_sha256']={p.relative_to(ROOT).as_posix():sha(p)for p in artifacts}
    write(ROOT/'delivery.json',delivery)
    latest=ROOT.parent/'latest-previz.json';backup=REVIEW/'previous-latest-previz.json'
    if not backup.exists():backup.write_bytes(latest.read_bytes())
    previous=read(backup);preserved=previous.get('source_files_preserved',{});preserved['city_expansion']=str(source)
    write(latest,{'file':str(path),'sha256':digest,'adopted_on':datetime.now().date().isoformat(),
                  'choice':'User-requested landmark relocation, larger Temple of Heaven and unified spherical China ground',
                  'delivery':str(ROOT/'delivery.json'),'verification':str(REVIEW/'verification-summary.json'),'review':str(ROOT/'review.html'),
                  'fps':30,'frame_start':0,'frame_end':989,'duration_seconds':33,'source_files_preserved':preserved,
                  'status':'Current working master; curved China ground and radial structures verified, loading preserved and camera compensation smooth'})
    assert sha(path)==digest and sha(source)==delivery['source_sha256']
    print(json.dumps({'file':str(path),'sha256':digest,'checks':len(checks),'all_checks_pass':True,'latest_updated':True,'buildings':buildings}))

if __name__=='__main__':main()
