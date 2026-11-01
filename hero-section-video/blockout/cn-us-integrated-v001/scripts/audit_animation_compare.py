"""Compare evaluated semantic samples; no .blend is opened or changed."""
import json
import math
from pathlib import Path
from mathutils import Matrix

ROOT = Path(__file__).resolve().parents[1]
c = json.loads((ROOT/'review/animation-source-cn.json').read_text())
u = json.loads((ROOT/'review/animation-source-us.json').read_text())
rows = []
for cr, ur in zip(c['samples'], u['samples']):
    assert abs(cr['cn_frame']-ur['cn_frame']) < 1e-8
    row = {'cn_frame': cr['cn_frame'], 'us_frame': cr['us_frame'], 'actors': {}}
    for name in ['A02_SHIP', 'A01_CONTAINER', 'W01_NEW_PALLET', 'P01_SPREADER']:
        cm = Matrix(cr['objects'][name]['world'])
        um = Matrix(ur['objects'][name]['world'])
        placement = 'PORT_HOIST_PLACEMENT' if name == 'P01_SPREADER' else 'PORT_BERTH_PLACEMENT'
        original = Matrix(cr['objects'][placement]['world']).inverted() @ cm
        row['actors'][name] = {
            'without_CN_helpers_max_matrix_error': max(abs(original[i][j]-um[i][j]) for i in range(4) for j in range(4)),
            'without_CN_helpers_position_error': (original.translation-um.translation).length,
            'with_CN_helpers_position_error': (cm.translation-um.translation).length,
            'cn_original_position': list(original.translation), 'us_position': list(um.translation),
            'without_CN_helpers_rotation_degrees': math.degrees(original.to_quaternion().rotation_difference(um.to_quaternion()).angle),
        }
    cm, um = Matrix(cr['camera']), Matrix(ur['camera'])
    q1, q2 = cm.to_quaternion(), um.to_quaternion()
    row['camera'] = {'eye_distance': (cm.translation-um.translation).length,
                     'angle_degrees': math.degrees(2*math.acos(min(1, abs(sum(a*b for a,b in zip(q1,q2)))/math.sqrt(sum(a*a for a in q1)*sum(b*b for b in q2))))),
                     'lens_difference': cr['lens']-ur['lens'],
                     'shift_difference': [a-b for a,b in zip(cr['shift'], ur['shift'])]}
    rows.append(row)
summary = {}
for start, end in [(0, 72), (72, 156), (156, 360), (360, 456), (456, 648), (648, 1392)]:
    subset = [r for r in rows if start <= r['cn_frame'] <= end]
    summary[f'{start}-{end}'] = {n: max(r['actors'][n]['without_CN_helpers_max_matrix_error'] for r in subset)
                                for n in ['A02_SHIP', 'A01_CONTAINER', 'W01_NEW_PALLET', 'P01_SPREADER']}
result = {'cn_sha256': c['sha256'], 'us_sha256': u['sha256'], 'without_CN_helper_matrix_errors': summary, 'rows': rows}
(ROOT/'review/animation-source-comparison.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print('ACTOR_INTERVALS', json.dumps(summary))
for row in rows:
    if row['cn_frame'] in [0, 36, 72, 96, 156, 216, 252, 288, 320, 340, 360, 408, 456, 532, 632, 648, 900]:
        print('KEY_DIFFERENCES', row['cn_frame'], row['us_frame'],
              {n: round(a['without_CN_helpers_position_error'], 6) for n,a in row['actors'].items()}, row['camera'])
