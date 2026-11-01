"""Seal passed integration evidence and designate one local working master."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / 'review'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

delivery = json.loads((ROOT/'delivery.json').read_text(encoding='utf-8'))
master = Path(delivery['file'])
assert sha(master) == delivery['sha256']
geometry = json.loads((REVIEW/'geometry-verification.json').read_text())
animation = json.loads((REVIEW/'animation-verification.json').read_text())
assert geometry['sha256'] == animation['sha256'] == delivery['sha256']
assert all(geometry['checks'].values()) and all(animation['checks'].values())
media = json.loads((REVIEW/'motion-metadata.json').read_text())
video_check = json.loads((REVIEW/'video-validation.json').read_text())
pixel_check = json.loads((REVIEW/'us-live-pixel-comparison.json').read_text())
assert media['sha256'] == video_check['candidate_sha256'] == pixel_check['candidate_sha256'] == delivery['sha256']
assert video_check['pass'] and all(r['camera_exact'] and r['pixels_exact'] for r in pixel_check['checks'])
for key, path in delivery['source_files'].items():
    assert sha(path) == delivery['source_sha256'][key]
delivery['status'] = 'Completed: China harbor and camera integrated with accepted US city and logistics master'
delivery['completed_on'] = '2026-10-31'
delivery['verification'] = {
    'geometry_checks': geometry['checks'], 'animation_checks': animation['checks'],
    'protected_US_objects': geometry['original_US_count'],
    'integrated_objects': geometry['integrated_count'],
    'camera_errors': animation['camera_errors'],
    'camera_clearance_samples': animation['geometry']['sample_count'],
    'ship_support_samples': geometry['support_samples'],
    'minimum_hull_immersion': geometry['min_hull_immersion'],
    'minimum_deck_freeboard': geometry['min_deck_freeboard'],
    'US_identical_live_render_frames': len(pixel_check['checks']),
}
delivery['preview'] = {'file':str(REVIEW/media['video']),'duration_seconds':9,
    'fps':15,'actual_rendered_frames':135,'scope':'Opening and camera transition only; full master remains33s30fps'}
assets = [master, ROOT/'README.md', REVIEW/'geometry-verification.json',
          REVIEW/'animation-verification.json', REVIEW/'after-contact-sheet.png',
          REVIEW/'us-live-pixel-comparison.json', REVIEW/'us-reference-live-contact-sheet.png']
for p in [REVIEW/'review.html', REVIEW/media['video'], REVIEW/'motion-metadata.json', REVIEW/'video-validation.json']:
    if p.exists():
        assets.append(p)
delivery['files'] = [{'path':str(p.relative_to(ROOT)), 'bytes':p.stat().st_size,
                      'sha256':sha(p)} for p in assets]
(ROOT/'delivery.json').write_text(json.dumps(delivery,ensure_ascii=False,indent=2),encoding='utf-8')

# The inherited metadata points here, so include the exact clock beside the file.
mapping = json.loads((ROOT.parent/'pacing-33s-v001/time-map.json').read_text(encoding='utf-8'))
mapping['output_sha256'] = delivery['sha256']
mapping['source'] = delivery['source_files']['cn']
mapping['source_sha256'] = delivery['source_sha256']['cn']
mapping['integration_note'] = 'Mapping applies to CN additions. All accepted US actions retain their existing native 30fps clock.'
(ROOT/'time-map.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2),encoding='utf-8')

summary = REVIEW/'verification-summary.json'
summary.write_text(json.dumps({'file':str(master),'sha256':delivery['sha256'],'passed':True,
    'checks_passed':sum(geometry['checks'].values())+sum(animation['checks'].values()),
    'reports':[str(REVIEW/'geometry-verification.json'),str(REVIEW/'animation-verification.json')],
    'US_live_render_comparison':str(REVIEW/'us-live-pixel-comparison.json')
},ensure_ascii=False,indent=2),encoding='utf-8')

pointer = ROOT.parent/'latest-previz.json'
previous = REVIEW/'previous-latest-previz.json'
if pointer.exists() and not previous.exists():
    previous.write_bytes(pointer.read_bytes())
pointer.write_text(json.dumps({
    'file':str(master),'sha256':delivery['sha256'],'adopted_on':'2026-10-31',
    'choice':'User-requested integration of US city/port/camera improvements and CN harbor/camera improvements',
    'delivery':str(ROOT/'delivery.json'),
    'verification':str(summary),
    'fps':30,'frame_start':0,'frame_end':989,'duration_seconds':33,
    'source_files_preserved':delivery['source_files'],
    'status':'Integrated working master; independent preservation, timing, camera and harbor clearance checks passed'
},ensure_ascii=False,indent=2),encoding='utf-8')
print('SEALED_INTEGRATION',delivery['sha256'],sum(geometry['checks'].values())+sum(animation['checks'].values()))
