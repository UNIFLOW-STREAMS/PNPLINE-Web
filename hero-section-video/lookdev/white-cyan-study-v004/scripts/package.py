import importlib.util,re,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];old=R.parent/'white-cyan-study-v003'
spec=importlib.util.spec_from_file_location('package_review',R.parent/'white-cyan-study-v002/scripts/package_review.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p);p.SHOTS=('0132',)
p.build(R/'review/index.html','PNPLINE · 두 타워 브랜드 배색','상하이 타워와 광저우 타워를 브랜드 청록색으로 조정했습니다. 타워 유리의 반사·거칠기와 기존 회색 지붕 설정은 유지했습니다.','이전 v003','타워 배색 v004',old/'review','after',R/'review','after','../pnpline-white-cyan-study-v004.blend','../study.json')
path=R/'review/index.html';text=path.read_text(encoding='utf-8');text=re.sub(r'<nav aria-label="비교 장면">.*?</nav>','<nav aria-label="비교 장면"><button data-shot="0132">중국 전경 · CAM_MASTER 132</button></nav>',text);path.write_text(text,encoding='utf-8')
s=json.loads((R/'study.json').read_text())
for k in ['source','output']:
 with open(s[k],'rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==s[k+'_sha256']
(R/'README.md').write_text('''# White & Cyan v004

v003에서 상하이 타워(SF_TALLEST_TOWER), 광저우 타워(CNX_GZ_CANTON_ROOT)에 브랜드 청록색을 추가했다. 두 타워의 유리는 Base Color만 청록색으로 바꾸고 v002의 roughness, metallic, coat 설정을 유지했다. 구조체도 기존 랜드마크용 청록 도장을 적용했다.

다른 건물의 유리와 건축 지붕, 창고 지붕, 수면은 그대로다. 모델·카메라·애니메이션은 수정하지 않았다. 별도 실험 파일로 저장했다.

review/index.html은 동일 CAM_MASTER 132 프레임의 v003/v004 비교이며 이미지를 내부에 포함한다. Cycles OPTIX, 40 samples, 1600×900. 정확한 슬롯 및 파일 해시는 study.json에 기록했다.
''',encoding='utf-8')
print('Packaged review; source and result hashes verified.')
