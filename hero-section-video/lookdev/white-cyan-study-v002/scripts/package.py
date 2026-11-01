from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];old=R.parent/'white-cyan-study-v001'
s=(old/'review/index.html').read_text(encoding='utf-8')
replacements={
 'White & Cyan material study':'White & Cyan · Glass and roof contrast',
 '기존 컬러 재질과 흰색·회색 중심의 실험 재질을 같은 카메라·조명으로 비교합니다. 바다 재질은 유지했습니다.':'이전 백색 실험본과 유리·지붕의 명암을 개선한 결과를 같은 카메라·조명으로 비교합니다.',
 '기존 재질':'이전 실험', 'White & Cyan 실험':'유리·지붕 명암 개선',
 '기존 컬러 재질':'이전 백색 실험 재질','기존만':'이전 실험','실험만':'개선 결과',
 'pnpline-white-cyan-study-v001.blend':'pnpline-white-cyan-study-v002.blend',
 "'original-'+key+'.png'":"'../../white-cyan-study-v001/review/white-'+key+'.png'",
}
for a,b in replacements.items():s=s.replace(a,b)
(R/'review/index.html').write_text(s,encoding='utf-8')
d=json.loads((R/'study.json').read_text())
def sha(p):
 with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert sha(d['output'])==d['output_sha256']
for shot in ['0057','0132','0390','0600','0780','skyline']:
 p=R/'review'/f'white-{shot}.png'
 assert p.stat().st_size>10000 and p.stat().st_mtime>=Path(d['output']).stat().st_mtime
 assert (old/'review'/p.name).exists()
assert sha(d['source'])==d['source_sha256']
print('Verified study, source preservation, and six matched review pairs')
