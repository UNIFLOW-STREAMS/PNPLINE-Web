import importlib.util,re,shutil,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];old=R.parent/'white-cyan-study-v002'
spec=importlib.util.spec_from_file_location('package_review',old/'scripts/package_review.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
for key in ['0132','skyline']:shutil.copy2(old/'review'/f'white-{key}.png',R/'review'/f'before-{key}.png')
p.SHOTS=('0132','skyline','usa')
p.build(R/'review/index.html','PNPLINE · 랜드마크 브랜드 배색', '백색 도시에서 랜드마크 일부의 외벽·구조체에 브랜드 청록색을 적용했습니다. 짙은 청회색 유리와 회색 지붕, 밝은 은회색 창고 지붕은 유지했습니다.', 'v002 백색 중심', 'v003 브랜드 배색', R/'review','before',R/'review','after','../pnpline-white-cyan-study-v003.blend','../study.json')
path=R/'review/index.html';text=path.read_text(encoding='utf-8');text=re.sub(r'<nav aria-label="비교 장면">.*?</nav>','<nav aria-label="비교 장면"><button data-shot="0132">중국 전경 · CAM_MASTER 132</button><button data-shot="skyline">상하이 확대 · 검토 시점</button><button data-shot="usa">미국 랜드마크 · 검토 시점</button></nav>',text);text=text.replace("key==='skyline'?'8/5':'16/9'","key==='0132'?'16/9':'8/5'");path.write_text(text,encoding='utf-8')
study=json.loads((R/'study.json').read_text())
def sha(path):
 with open(path,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert sha(study['output'])==study['output_sha256']
assert sha(study['source'])==study['source_sha256']
(R/'README.md').write_text('''# 랜드마크 브랜드 배색 실험 v003

v002의 백색·회색 도시에서 중국 9개, 미국 2개 랜드마크를 선택해 불투명 외벽·구조체에 브랜드 청록색을 적용했다. 도시별로 분산해서 선택했고 seed 20261102를 고정했다. 프레임별 색 변화는 없다.

- 동방명주, 상하이 금융센터의 구조체, 중국 전통 건축의 벽·기둥, 광저우 일부 랜드마크, 미국 엠파이어스테이트와 국회의사당형 건물의 기둥에 청록색을 배정했다.
- 유리·지붕·창고 지붕의 v002 재질과 슬롯을 유지했다. 건물 부지, 가로수, 받침, 수면은 배색 대상에서 제외했다.
- 카메라·메시·지형·트랜스폼·기존 애니메이션을 수정하지 않았다. 검토용 카메라는 렌더 프로세스에서만 생성하고 blend에는 저장하지 않았다.
- Cycles OPTIX, 40 samples, 1600 px로 중국 CAM_MASTER 132, 상하이 확대, 미국 랜드마크 검토 시점을 렌더링했다. 미국 검토 시점은 동일 카메라에서 전후를 렌더링했다.
- review/index.html은 비교 이미지가 내부에 포함된 단일 HTML이다. PNG 원본도 review 폴더에 있다.
- 원본 통합 마스터와 v002는 덮어쓰지 않았다. 이 파일은 별도 실험본이다.

정확한 랜드마크 목록·변경 슬롯·파일 해시는 study.json, 렌더 시간은 review/render.json에 기록했다.
''',encoding='utf-8')
print('Packaged three matched views. Source and output hashes verified.')
