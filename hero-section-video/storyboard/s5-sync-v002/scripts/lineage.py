import json, hashlib
from pathlib import Path
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def require(condition,message):
    if not condition:raise ValueError(message)
def validate_expression(record, raw_record, selection_path):
    require(record['status']=='complete','incomplete expression run')
    require(record['selection_sha256']==digest(selection_path),'selection changed; review required')
    selection=json.loads(Path(selection_path).read_text(encoding='utf-8'))
    require(record['source_sha256']==raw_record['source']['sha256']==selection['source_sha256'],'wrong source')
    for k in ['scene','camera']:require(record[k]==raw_record[k],f'wrong {k}')
    for k in ['resolution','pixel_aspect']:require(record[k]==raw_record['render'][k],f'wrong {k}')
    expected=[(p['id'],p['frame']) for p in selection['panels']]
    actual=[(p['id'],p['frame']) for p in record['images']]
    require(actual==expected,'missing, duplicate or reordered expression panel')
    raw={p['frame']:p for p in raw_record['images']}
    for p in record['images']:
        parent=raw[p['frame']]
        require(p['raw_sha256']==parent['sha256'],'wrong raw parent')
        require(p['camera_state']==parent['camera_state'],'camera projection changed')
        require(Path(p['path']).is_file() and digest(p['path'])==p['sha256'],'artwork missing/changed; review required')
