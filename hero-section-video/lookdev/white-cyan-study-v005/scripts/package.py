import importlib.util,re,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];old=R.parent/'white-cyan-study-v004'
spec=importlib.util.spec_from_file_location('package_review',R.parent/'white-cyan-study-v002/scripts/package_review.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p);p.SHOTS=('0132',)
p.build(R/'review/index.html','PNPLINE · 크레인 상부 브랜드 배색','중국 항만 크레인 세 대의 상부 붐·트러스에 브랜드 청록색을 적용했습니다.','이전 v004','크레인 상부 v005',old/'review','after',R/'review','after','../pnpline-white-cyan-study-v005.blend','../study.json')
path=R/'review/index.html';text=path.read_text(encoding='utf-8');text=re.sub(r'<nav aria-label="비교 장면">.*?</nav>','<nav aria-label="비교 장면"><button data-shot="0132">중국 전경 · CAM_MASTER 132</button></nav>',text);path.write_text(text,encoding='utf-8')
s=json.loads((R/'study.json').read_text())
for k in ['source','output']:
 with open(s[k],'rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==s[k+'_sha256']
(R/'README.md').write_text('''# White & Cyan v005

v004에서 중국 항만 크레인 세 대의 상부에만 기존 브랜드 청록색을 적용했다.

- 보조 크레인 2대: 상부 횡보, 붐, 파일런, 스테이, 백스테이, 붐 연결재.
- 작업 크레인 1대: CR_SLEW_JIB의 상부 붐·트러스·기계실·운전실 도장. 유리·회전 베어링은 제외.
- 하부 다리·버팀대·대차·케이블과 모든 비대상 재질 슬롯은 보존했다.
- 지형·모델·카메라·애니메이션은 수정하지 않았다. v004를 보존하고 별도 실험본에 저장했다.

Cycles OPTIX, 40 samples, CAM_MASTER 132 프레임을 1600×900으로 렌더링했다. review/index.html은 전후 이미지를 내부에 포함한다. 변경 슬롯·해시는 study.json, 렌더 시간은 review/render.json에 기록했다.
''',encoding='utf-8')
print('Packaged review; source and result hashes verified.')
