from pathlib import Path
import json,hashlib,html
R=Path(__file__).resolve().parents[1];q=json.loads((R/'review/integration-verified.json').read_text());assert all(q['checks'].values());b=R/'master-previz-styleframe-v001.blend';assert hashlib.sha256(b.read_bytes()).hexdigest()==q['sha256'];m=json.loads((R/'inputs/manifest.json').read_text())
report=f'''# PNPLINE S1–S7 스타일프레임 통합 프리비즈 v001

작업 파일: master-previz-styleframe-v001.blend
판정: 사용자 지정 v032의 전체 마스터 통합 완료. 별도 미술·카메라 개선 사항은 아래와 같이 남음.

## 기준과 통합 방법
최신 기본 마스터 master-s2-city-reveal-china-v001.blend → 누적 수정 layout-proposal-v032.blend → 이번 통합 마스터.
v032가 이미 S1–S7 전체 장면을 포함하므로 객체를 중복 append하지 않고 전체 장면을 새 마스터로 승격했다.
사용자가 지정한 현재 디스크 저장본 v032 SHA256: {m['source_sha256']}
통합 마스터 SHA256: {q['sha256']}
이전 원본·제안본과 미저장 창은 보존했다. 현재 v032 저장 해시는 직전 작업 당시 기록과 달라 현재 저장본을 inputs/에 복사·고정한 뒤 새로 검증했다.

## 포함 사항
CHINA 곡률, 구름, 양측 도시 건축·조경, S형 수로, 석조 아치교, 크레인 및 승인된 S1 인양 연결, 선박 외형, 양측 해안 경사면까지 v032의 누적 수정 전체.
7,262개 객체·67개 액션. f0–1392 / 12fps / 원래 S1–S7 마커 유지. 3.5배속·4배속 출력용 파생본이나 미선택 모션 A/B를 합치지 않았다.
저장 경로·출력 경로·통합 상태 메타데이터와 전체 재생 범위 설정만 정리했다. 형상·카메라·동작을 추가 변경하지 않았다.

## 새 검증
8개 통합 검사 모두 통과. 현재 v032와 모든 객체의 형상·표시·부모·재질 배정, 컬렉션 및 액션 비교 일치. 전체 정수 프레임과 경계 소수 프레임을 합친 1,513시점에서 애니메이션/제약 객체의 월드 변환과 렌즈 일치.
최신 기본 마스터의 비승인 액션 변경 없음. 기존 승인 범위를 제외한 카메라·시선·컨테이너·선박 변환 오차 0.
S1–S7 대표 28장 Workbench 렌더와 S2 f156 Cycles 렌더를 새 저장본에서 생성하고 확인했다. 전체 연속 동영상 렌더는 이번 통합 작업에서 생성하지 않았다.

## 기존 v032에서 이어지는 검토 사항
f216 부근의 S2→S3 연결에서 크레인·건물이 화면을 크게 가리는 근접 구도가 남아 있다. 통합 중 발생한 데이터 손실이 아니라 v032의 동일 카메라/공간 상태다. review/stills/f0216.png에 공개했다. 이번 요청은 v032 통합이므로 추가 카메라 경로 변경은 하지 않았다.
이번 검사 통과는 원본 대비 충실한 통합과 지정 동작 보존을 뜻하며, 전체 미술 정합·모든 연속시간 물리 충돌·최종 공개 승인을 뜻하지 않는다.

## 사용과 재현
Blender에서 master-previz-styleframe-v001.blend를 열고 전체 범위로 재생한다. f156에서 열린다.
입력 복사본에 scripts/integrate.py를 실행하면 새 마스터가 만들어진다(기존 출력 덮어쓰기 거부). scripts/verify.py는 새 프로세스에서 다시 열어 비교한다. 검사에는 인접한 s2-styleframe-match-v001/scripts/verify_title_water.py의 순수 비교 함수와 원본 기본 마스터가 필요하다.
커밋·push·외부 업로드는 수행하지 않았다.
'''
(R/'README.md').write_text(report,encoding='utf-8')
figs=''.join(f'<figure><a href="review/stills/{p.name}"><img loading="lazy" src="review/stills/{p.name}" alt="{p.stem}"></a><figcaption>{p.stem}</figcaption></figure>'for p in sorted((R/'review/stills').glob('*.png')))
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><title>PNPLINE S1–S7 통합 마스터 v001</title><style>body{font:16px/1.6 system-ui;background:#eef2f4;color:#172d37;margin:0;padding:32px}main{max-width:1400px;margin:auto}h1{font-size:30px}a{color:#086880}.hero{width:100%}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}figure{margin:0;background:white;padding:10px}img{width:100%;height:auto}.note{border-left:5px solid #d19c23;background:#fff9e5;padding:18px;margin:24px 0}.links{padding:18px;background:white}@media(max-width:800px){.grid{grid-template-columns:1fr}}</style><main><h1>PNPLINE S1–S7 통합 마스터</h1><p>v032 누적 수정 전체 · 0–1392 프레임 · 12fps · 7,262개 객체 · 67개 액션</p><div class="links"><a href="master-previz-styleframe-v001.blend"><b>master-previz-styleframe-v001.blend</b></a> · <a href="review/integration-verified.json">새 통합 검증 8/8</a> · <a href="README.md">통합 기록</a></div><h2>S2 디자인 렌더 · f156</h2><img class="hero" src="review/S2-f0156.png"><div class="note"><b>기존 v032의 연결 구도 검토 사항</b><p>f216 부근에서 크레인과 건물이 화면을 크게 가리는 구도가 남아 있습니다. 이번 통합에서는 v032의 카메라를 그대로 유지했습니다.</p><a href="review/stills/f0216.png">f216 확인 이미지</a></div><h2>S1–S7 전체 구간 확인</h2><p>새 통합 저장본의 대표 28장입니다. Workbench 형상·동작 확인용이며 연속 동영상은 아닙니다.</p><div class="grid">'''+figs+'</div></main></html>'
(R/'review.html').write_text(page,encoding='utf-8')
(R/'delivery.json').write_text(json.dumps({'file':str(b),'sha256':q['sha256'],'checks':q['checks'],'source':m,'stills':28,'continuous_video_rendered':False,'known_visual_issue':'Inherited v032 S2-S3 f216 foreground crane/building obstruction; camera unchanged.'},indent=2))
print('INTEGRATION PACKAGED: 8/8 checks, 28 stills')
