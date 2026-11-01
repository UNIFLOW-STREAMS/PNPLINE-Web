"""Seal only a saved model whose scoped checks and review media match its hash."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
review = root / 'review'
master = root / 'master-cn-port-layout-v001.blend'
digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
sha = digest(master)
delivery = json.loads((root / 'delivery.json').read_text(encoding='utf-8'))
assert delivery['sha256'] == sha
reports = {}
for name in ['verification.json', 'connections.json', 'master-cn-port-layout-v001-lift.json',
             'master-cn-port-layout-v001-internal.json', 'after-content.json', 'static-audit.json']:
    report = json.loads((review / name).read_text(encoding='utf-8'))
    assert report['sha256'] == sha, (name, 'stale report')
    if 'checks' in report:
        assert all(report['checks'].values()), (name, report['checks'])
    if 'pass' in report:
        assert report['pass'], name
    if name == 'static-audit.json':
        assert not report['new_vs_old_surface_crossings']
        assert not report['module_crossings']
        preservation = report['ocean_preservation']
        for key in ['far_original_vertices_present_exact',
                    'opposite_US_hemisphere_original_vertices_present_exact',
                    'object_matrix_unchanged', 'material_slots_and_colors_unchanged']:
            assert preservation[key], key
    reports[name] = {'sha256': digest(review / name), 'model_sha256': sha}

for name in ['after-all-metadata.json', 'after-hoist-frames/metadata.json', 'camera-framing.json']:
    assert json.loads((review / name).read_text(encoding='utf-8'))['sha256'] == sha, name
media = {}
for name in ['after-overview.png', 'after-port.png', 'after-top.png',
             'after-hoist.mp4', 'after-hoist-contact-sheet.png', 'review.html']:
    path = review / name
    assert path.is_file() and path.stat().st_size > 100
    media[name] = {'sha256': digest(path), 'bytes': path.stat().st_size}

delivery.update({
    'status': 'Harbor layout complete; scoped geometry and lowering checks passed; camera/route direction deferred',
    'completed_on': '2026-10-31',
    'timeline': {'fps': 12, 'frame_start': 0, 'frame_end': 1392},
    'camera_modified': False,
    'source_actions_modified': False,
    'verification_reports': reports,
    'review_media': media,
    'review_camera': 'Temporary diagnostic camera only; not saved in Blender master',
    'next_task': 'Camera motion, angle, and final voyage route. Temporary berth offset holds through f252 and rejoins source at f360.',
    'known_limitations': [
        'The provisional departure return can expose part of the bow above the reshaped water before f348; refine water contact with the next route pass. Loading frames f0–156 remain immersed and preserved.',
        'This continues the interrupted China 12fps scene. Separate US-city/33-second master branches remain separate.'
    ],
})
(root / 'delivery.json').write_text(json.dumps(delivery, indent=2, ensure_ascii=False), encoding='utf-8')
print('SEALED', sha, len(reports), 'reports', len(media), 'media files')
