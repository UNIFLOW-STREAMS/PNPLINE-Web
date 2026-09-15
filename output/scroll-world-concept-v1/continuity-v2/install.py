"""Install the new viewer after all 12 images are available; retain local V1 links."""
from pathlib import Path
import shutil,json
HERE=Path(__file__).resolve().parent
OUT=HERE.parent
manifest=json.loads((HERE/'manifest.json').read_text(encoding='utf-8'))
assert len(manifest['assets'])==12
for name in ['ko','index']:
 target=OUT/f'{name}.html'
 archive=OUT/f'{name}-v1.html'
 if not archive.exists():shutil.copyfile(target,archive)
 html=archive.read_text(encoding='utf-8')
 html=html.replace('<link rel="stylesheet" href="review.css">','<link rel="stylesheet" href="review.css"><link rel="stylesheet" href="continuity-v2/review.css">')
 html=html.replace('<script src="review.js" defer></script>','<script src="continuity-v2/data.js" defer></script><script src="continuity-v2/review.js" defer></script>')
 if name=='ko':
  replacements={
   '모든 여정을,<br><em>선명하게.</em>':'중국에서 미국까지,<br><em>같은 화물을 따라.</em>',
   '구도 방향 선정 완료 / 개별 자산은 시각 승인 전':'V2 지리·카메라 수정안 / 개별 자산 시각 검토 중',
   '중국 출발부터 미국 풀필먼트까지. 밝은 산업 미니어처 세계로 여섯 물류 장면을 연결합니다.':'중국의 선적 부두, 태평양의 선박, 미국의 창고와 배송 도로. 같은 파란 컨테이너와 화물의 이동을 여섯 시점으로 따라갑니다.',
   '밝음으로 신뢰를 만듭니다.':'초기 미술 방향과 수정 기준.',
   'A는 선정한 방향입니다. B는 해 질 녘 조명, C는 하이 앵글 시점을 비교하기 위한 안이며, 여섯 장면의 시각 원칙에 섞지 않습니다.':'기존 A의 밝은 주광과 브랜드 색을 유지하면서, 국가 구분·카메라 방향·미니어처 축척감을 수정했습니다. 아래 세 이미지는 초기 비교안입니다.',
   '모든 장면에 분명한 동작이 있습니다.':'출발지와 도착지가 보이는 여섯 시점.',
   '데스크톱에서는 공간을 가로로 펼치고, 모바일에서는 깊이, 브랜드 표면, 문구 여백을 다시 구성합니다. 아래 한국어는 모두 검토용 임시 문구입니다.':'데스크톱은 왼쪽에서 오른쪽으로, 모바일은 가까운 화물에서 먼 목적지로 시선을 연결합니다. 각 장면에서 이전 공간과 다음 목적지를 함께 보여 줍니다.',
   '전진과 가림으로 여정을 연결합니다.':'같은 화물을 따라, 중국에서 미국으로.',
   '슬라이더를 끌거나 방향키로 진행률을 조절할 수 있습니다. 30초는 검토용 가상 시간이며, 정지 이미지 이동과 전경 마스크는 전환 의도만 보여 줍니다.':'30초 러프 재생, 슬라이더, 장면 버튼으로 흐름을 확인하세요. 중국의 육지에서 바다로 나가고, 미국의 바다에서 내륙으로 들어온 뒤 창고를 지나 출고합니다.',
   ' 안전 영역':' 로고 보호 영역',
  }
 else:
  replacements={
   '让每一程，<br><em>清晰可见。</em>':'从中国到美国，<br><em>跟随同一批货。</em>',
   '构图方向已确定 / 单张素材待视觉批准':'V2 地理与镜头修改案 / 单张素材待视觉评审',
   '从中国发运到美国履约。以明亮的工业微缩世界，串联六个物流场景。':'从中国码头到太平洋货船，再到美国仓库与配送道路。用六个视点跟随同一蓝色集装箱与货物。',
   '以明亮，建立信任。':'初期美术方向与修改依据。',
   'A 为选定方向。B 仅比较暮色照明，C 仅比较俯视镜头；不混入六场景的视觉常量。':'保留A的明亮日光与品牌色，强化国家区分、镜头方向和微缩比例。下方三张为初期比较案。',
   '每一个场景，都有明确的动作。':'六个视点，看见出发地与目的地。',
   '桌面横向展开空间；移动端重新组织纵深、品牌表面与文案留白。下列中文均为评审临时文案。':'桌面视线从左到右，移动端从近处货物延伸至远方目的地。每一帧同时交代来处与下一步去向。',
   '用前进与遮挡，连接旅程。':'跟随同一批货，从中国到美国。',
   '拖动或用方向键调整进度。30 秒为评审虚拟时间；静帧位移与前景遮罩只说明过渡意图。':'播放30秒粗剪，或用滑块及场景按钮检查旅程。从中国陆地驶向大海，在美国由海向内陆，经过仓库进入配送。',
   ' 安全区域':' 标志保护区域',
  }
 for old,new in replacements.items():
  if old not in html:raise ValueError(f'Missing expected text: {old}')
  html=html.replace(old,new)
 html=html.replace('src="qa/logo-comparisons/S01-desktop.jpg"','src="continuity-v2/qa/S01-desktop-logo.jpg"')
 for old,new in {'qa/validation.md':'continuity-v2/qa/browser-results.json','data/assets.json':'continuity-v2/manifest.json','data/storyboard.json':'continuity-v2/manifest.json','data/timeline.json':'continuity-v2/manifest.json','prompts/master.md':'continuity-v2/prompts.md','branding/logo-placement-guide.md':'continuity-v2/README.md'}.items():
  html=html.replace('href="'+old+'"','href="'+new+'"')
 for i in range(1,7):
  html=html.replace(f'href="keyframes/mobile/S{i:02d}.jpg"',f'href="continuity-v2/keyframes/S{i:02d}-mobile.webp"')
 target.write_text(html,encoding='utf-8')
print('Installed V2 in ko.html and index.html. V1 archives preserved.')
