import json,statistics,hashlib,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads((R/p).read_text(encoding='utf-8'))
def sha(p):
 with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def q(a,p):return sorted(a)[min(len(a)-1,int(p*(len(a)-1)))]
qa=read('review/browser/results.json');mobile=read('review/mobile-extra.json');record=read('review/recording-states.json');media=read('data/media-manifest.json');mapping=read('review/mapping-verification.json');record_duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(R/'review/scroll-review.mp4')],text=True))
assert qa['pass'] and not qa['fixture'] and mobile['pass'] and mapping['pass']
frames=[c for c in qa['checks']if 'targetFrame'in c];settle=[c['settleMs']for c in frames];natural=record['naturalSamples'];lat=[s['seekLatencyMs']for s in natural if s['seekLatencyMs']is not None];error=[s['errorFrames']for s in natural]
summary=dict(pass_all=True,browser_checks=len(qa['checks']),settled_max_error_frames=max(abs(c['targetFrame']-c['displayFrame'])for c in frames),settle_p95_ms=q(settle,.95),settle_max_ms=max(settle),continuous_wheel_samples=len(natural),continuous_wheel_error_median=statistics.median(error),continuous_wheel_error_p95=q(error,.95),continuous_wheel_error_max=max(error),seek_to_paint_median_ms=statistics.median(lat),seek_to_paint_p95_ms=q(lat,.95),seek_to_paint_max_ms=max(lat),first_paint_ms=frames[0]['loadMs'],mobile_extra=mobile,source_unchanged=media['source_unchanged'],scroll_vh=mapping['totalVh'],scroll_px_1080=mapping['scrollPxAt1080'],render_seconds=media['render_seconds_first_to_last'],web_bytes=media['videos'][1]['bytes'],record_duration_seconds=record_duration,limitations=['Measured in local headless Chromium, not physical iOS Safari.','Continuous recording is controlled wheel input (16px per 32ms plus reverse); metrics are callback samples, not a guarantee for arbitrary input/network/hardware.','Programmatic boundary jumps can transiently display an older frame while a seek resolves; settled frame error is measured separately.','1280x720 Workbench timing review, not final Cycles material/lighting/DOF approval.','Full Blob fetch is 40.8MB; this is a production performance-budget decision still to be made.'])
(R/'review/validation-summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
lines=[
'# 최종 검증 결과',
'',
'## 결과',
f"최신 lookdev 장면의 7개 마커와 990개 원본 프레임을 사용했다. 실제 Chrome {qa['browser']}에서 {len(qa['checks'])}개 검사가 통과했다. `review/fixture` 결과는 최종 판정에서 제외했다.",
'',
'| 항목 | 측정 결과 |',
'|---|---|',
f"| 전체 스크롤 거리 | 13H · 높이1080 기준14,040px |",
f"| 수학 검사 | 20,001지점 · 양의 C1 매핑 · 역함수 최대오차 {mapping['maxInverseError']:.2g} |",
f"| 안정화 뒤 프레임 오차 | 최대 {summary['settled_max_error_frames']}프레임 |",
f"| 검사별 안정화 대기 시간 | P95 {summary['settle_p95_ms']}ms · 최대 {summary['settle_max_ms']}ms (로딩·키보드·모드·점프 포함) |",
f"| 첫 프레임 표시 | {summary['first_paint_ms']:.1f}ms · 로컬 캐시/디스크 환경 |",
f"| 연속 휠 녹화 | {len(natural)} 표시 콜백 · 프레임 오차 중앙/P95/최대 {statistics.median(error)}/{q(error,.95)}/{max(error)} |",
f"| 요청→표시 지연 | 중앙 {statistics.median(lat):.1f}ms · P95 {q(lat,.95):.1f}ms · 최대 {max(lat):.1f}ms |",
f"| 미디어 | 1280×720 · 30fps · 990프레임 · 33초 · H.264 GOP8 · {summary['web_bytes']/1e6:.1f}MB |",
f"| 렌더 측정 | 첫 완료~마지막 완료 {summary['render_seconds']:.1f}초 · 준비 시간 별도 |",
'| 원본 보존 | SHA256 작업 전후 동일 · Blender 저장 호출 없음 |',
'',
'안정화 시간은 입력 후 스크롤 이벤트 반영을 기다린 뒤 표시 프레임 일치를 관찰한 대기 시간이다. 요청→표시 지연은 rVFC 콜백 기준이다. 두 숫자는 서로 다른 측정이며, 모든 하드웨어에서 같은 지연을 보장하지 않는다.',
'',
'## 확인한 동작',
'',
'느린 휠, 큰 입력과 즉시 역방향, 급정지 후 지연 이동 없음, 모든 장면 경계와 감속 진입/중앙/이탈, 7개 장면 버튼, 선형/감속 전환 시 프레임 유지, 데스크톱 리사이즈, 중간 위치 새로고침, PageDown/Home/End, 시작0과 종료989, 일반 본문 연결을 검사했다.',
'',
'HTTP Range는206/100bytes로 확인했다. Blob은33초 전체가 seekable하다. 잘못된 미디어 경로는 정적 장면/본문으로 복구하며, 처음부터 모션 감소 설정이면 영상 요청이0회다. 별도 모바일 추가 검사에서 CPU4배 저속과4회 실제 CDP 터치 스크롤 제스처, 높이 변경 후 장면 버튼 표시, 런타임 모션 감소 전환을 확인했다. iOS 실기기 검증은 수행하지 않았다.',
'',
'## 녹화와 증거',
'',
f'- [스크롤 조작 녹화 MP4](scroll-review.mp4): {record_duration:.1f}초, 일정 휠 입력 후 역방향·급정지·선형 전환. 원본 영화 자체의 자동재생 녹화와 구별한다.',
'- [표시 콜백/조작 기록](recording-states.json)',
'- [Chrome79개 검사 원자료](browser/results.json)',
'- [모바일 추가 검사](mobile-extra.json)',
'- [수학 검사](mapping-verification.json) / [곡선](mapping.svg)',
'- [중국](browser/china.png) / [미국 항만](browser/us-port.png) / [도크](browser/dock.png) / [창고](browser/warehouse.png) / [출고](browser/dispatch.png) / [모바일](browser/mobile.png)',
'',
'## 제한과 남은 제작 결정',
'',
'Workbench의 메모리 내 강체 메시 합치기는 원본 카메라·시간을 그대로 평가하지만 제작용 셰이더·법선·투명도·수면·DOF와 다를 수 있다. 원본 프리비즈에서도 보였던 중첩 포장면의 줄무늬와 Workbench 광택은 남아 있으며, 웹 시간 매핑 오류와 구별한다. 이 결과는 스크롤 페이싱 검토용이며 최종 룩 승인 자료가 아니다. 가로 영상 전체를 표시하므로 모바일 레터박스가 존재한다. 별도 세로 영상은 제작하지 않았다. 로컬 Chrome 에뮬레이션 외 Safari/Firefox/실기기는 미검증이다.',
'',
'40.8MB 전체 Blob 다운로드와 해상도는 검토 편의성을 위한 선택이다. 운영 네트워크 예산·분할 로딩·모바일 전용 자산 선정은 이후 단계에서 결정해야 한다. 운영 배포나 기존 사이트 수정은 수행하지 않았다.',
'',
'기존 문서에서 권장한 분할 영상 계약 대신 이번 요청에 따라 단일 영상 어댑터를 사용했다. 과거24fps 매핑과 빠른 배속 프리비즈는 현재 원본으로 사용하지 않았다. 각 감속점은 `pacing.json`에 이유와 범위를 기록했다.',
]
(R/'review/validation.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
files=[p for p in R.rglob('*')if p.is_file() and not any(t in p.parts for t in ['node_modules','frames','tools','fixture','recording-raw'])]
manifest=dict(root=str(R),entry='index.html',review_url='http://127.0.0.1:3096/',run='npm start',source_blend=media['source_blend'],source_sha256=media['source_sha256'],original_blend_modified=False,existing_site_modified=False,files=[dict(path=str(p.relative_to(R)).replace('\\','/'),sha256=sha(p),bytes=p.stat().st_size)for p in files if p.name!='delivery.json'])
(R/'delivery.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8');print(json.dumps(summary,ensure_ascii=True))
