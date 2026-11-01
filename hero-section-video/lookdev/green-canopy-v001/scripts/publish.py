import hashlib
import json
import os
import shutil
from pathlib import Path

root = Path(__file__).resolve().parents[1]
report = json.loads((root / 'delivery.json').read_text())
pointer = root.parent / 'latest-lookdev.json'
record = json.loads(pointer.read_text())
master = Path(record['file'])
candidate = Path(report['output'])

def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

assert digest(master) == record['sha256'] == report['source_sha256']
assert digest(Path(report['versioned_source'])) == report['source_sha256']
assert digest(candidate) == report['sha256']
assert (root / 'review/waterfront-green.png').stat().st_size > 20000
stage = master.with_name('green-canopy-staged.blend')
assert not stage.exists()
shutil.copyfile(candidate, stage)
assert digest(stage) == report['sha256']
assert digest(master) == report['source_sha256']
os.replace(stage, master)
assert digest(master) == report['sha256']
updated = dict(
    file=str(master), versioned_copy=str(candidate), sha256=report['sha256'],
    source=report['versioned_source'], source_sha256=report['source_sha256'],
    previous_lookdev_record=str(root / 'previous-latest-lookdev.json'),
    fps=30, frame_start=0, frame_end=989,
    review=str(root / 'review/waterfront-green.png'),
    delivery=str(root / 'delivery.json'),
    status='Both faceted US and China street tree assets now use the established green foliage palette.'
)
temp = pointer.with_suffix('.green-staged.tmp')
temp.write_text(json.dumps(updated, indent=2))
os.replace(temp, pointer)
print('Published', master, report['sha256'])
