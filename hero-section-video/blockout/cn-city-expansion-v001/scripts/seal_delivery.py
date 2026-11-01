"""Publish the verified immutable model as the current working-file pointer."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / 'review'
EXPECTED = 'c9da20e19f2cf732245df77c178b1fa85dae00753884ea3c586327a63cbe75bb'
SOURCE = '1aee6c14eb4140614ffa650141eed3ada783c416397fbb938a5105a8df70a7d8'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    delivery = read(ROOT / 'delivery.json')
    candidate = Path(delivery['file'])
    source = Path(delivery['source'])
    assert sha(candidate) == delivery['sha256'] == EXPECTED
    assert sha(source) == delivery['source_sha256'] == SOURCE
    summary = read(REVIEW / 'verification-summary.json')
    assert summary['candidate_sha256'] == EXPECTED and summary['source_sha256'] == SOURCE
    assert summary['all_checks_pass'] and all(summary['checks'].values())
    contacts = read(REVIEW / 'contact-verification.json')
    sites = read(REVIEW / 'site-verification.json')
    assert contacts['sha256'] == sites['sha256'] == EXPECTED
    assert contacts['file_unchanged'] and sites['file_unchanged']
    assert not contacts['foundation_edge_gaps_above_0_08']
    assert not contacts['wave_protrusions'] and not sites['conflicts']
    package = read(REVIEW / 'package.json')
    assert package['candidate_sha256'] == EXPECTED and package['source_sha256'] == SOURCE
    assert package['all_13_sampled_camera_states_exact'] and package['all_scene_checks_pass']
    assert package['source_blend_unchanged'] and package['support_buildings'] == 247
    assert (ROOT / 'review.html').is_file()
    camera = read(REVIEW / 'render-camera-preservation.json')
    assert camera['candidate_sha256'] == EXPECTED and camera['all_sampled_camera_poses_optics_exact']

    # Preserve the established source-to-native-frame mapping verbatim.
    time_map = read(source.parent / 'time-map.json')
    time_map['output_sha256'] = EXPECTED
    time_map['geometry_expansion_base'] = str(source)
    time_map['geometry_expansion_base_sha256'] = SOURCE
    time_map['geometry_expansion_note'] = 'Beijing and Guangzhou geometry added; every native frame and all original animation are unchanged.'
    write(ROOT / 'time-map.json', time_map)

    delivery.update({
        'status': 'Complete: final visual review and all 16 independent preservation/clearance checks passed',
        'completed_at_utc': datetime.now(timezone.utc).isoformat(),
        'support_building_count': 247,
        'total_objects': summary['total_objects'],
        'verification': str(REVIEW / 'verification-summary.json'),
        'review': str(ROOT / 'review.html'),
        'preview': str(REVIEW / 'after-hero-diagnostic/hero.png'),
        'time_map': str(ROOT / 'time-map.json'),
        'source_file_preserved': True,
        'original_camera_and_animation_preserved': True,
        'native_frames_verified': 990,
        'review_note': 'Workbench modeling previews; overview uses a temporary review camera. The saved original animation camera remains unchanged.',
        'visibility_note': 'Nine decorative ocean-wave objects under the new land are hidden; their geometry, transforms and animation remain intact.',
        'checks': summary['checks'],
    })
    artifacts = [ROOT / 'README.md', ROOT / 'review.html', ROOT / 'time-map.json']
    artifacts += [REVIEW / name for name in ['verification-summary.json', 'expansion-verification.json', 'contact-verification.json', 'site-verification.json', 'render-camera-preservation.json', 'package.json', 'actual-camera-contact.jpg']]
    for directory in ['after-diagnostic', 'after-actual', 'after-hero-diagnostic', 'before-hero-diagnostic']:
        artifacts.extend(sorted((REVIEW / directory).glob('*.png')))
        artifacts.append(REVIEW / directory / 'metadata.json')
    delivery['artifact_sha256'] = {str(path.relative_to(ROOT)).replace('\\', '/'): sha(path) for path in artifacts}
    write(ROOT / 'delivery.json', delivery)

    latest = ROOT.parent / 'latest-previz.json'
    backup = REVIEW / 'previous-latest-previz.json'
    if not backup.exists():
        backup.write_bytes(latest.read_bytes())
    previous = read(backup)
    preserved = dict(previous.get('source_files_preserved', {}))
    preserved['integrated_base'] = str(source)
    write(latest, {
        'file': str(candidate), 'sha256': EXPECTED,
        'adopted_on': datetime.now().date().isoformat(),
        'choice': 'User-requested Beijing and Guangzhou landmark and surrounding-city expansion of the integrated CN/US master',
        'delivery': str(ROOT / 'delivery.json'),
        'verification': str(REVIEW / 'verification-summary.json'),
        'review': str(ROOT / 'review.html'),
        'fps': 30, 'frame_start': 0, 'frame_end': 989, 'duration_seconds': 33,
        'source_files_preserved': preserved,
        'status': 'Current working master; 13 new landmark groups and 247 surrounding buildings; camera and animation preserved across 990 frames',
    })
    assert sha(candidate) == EXPECTED and sha(source) == SOURCE
    assert read(latest)['file'] == str(candidate)
    print(json.dumps({'file': str(candidate), 'sha256': EXPECTED, 'all_checks_pass': True, 'landmarks': 13, 'surrounding_buildings': 247, 'latest_pointer_updated': str(latest)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
