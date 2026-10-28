import json,hashlib,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads((R/p).read_text(encoding='utf-8'))
master=R/'master-s2-city-reveal-china-v001.blend';h=sha(master);p=load('review/final-preservation.json');qa=load('review/final-qa.json');sp=load('review/spatial.json');features=load('review/features-master-s2-city-reveal-china-v001.json')
assert p['pass_all'] and qa['pass_all'] and sp['pass_all']
assert p['candidate_sha256']==qa['final_sha256']==sp['sha256']==features['sha256']==h
assert sha(R/'inputs/base.blend')==sha(R.parent/'cn-city-proxy-v001/master-cn-city-proxy-v001.blend')=='dc5e44237ba4eba2022096f078f6c39c5d162538dc954542f927a5a2dc69f7eb'
play=load('review/playback-evidence.json');assert play['final_blend_sha256']==h and play['normal']['ended'] and play['slow']['ended']
play['video_sha256']=sha(R/'preview/final.mp4');play['seek']['corrected_f170']={'time':7.208333,'reported_frame':170,'error':None,'observed_utc':'2026-10-28T09:40:30.637Z'}
(R/'review/playback-evidence.json').write_text(json.dumps(play,indent=2),encoding='utf-8')
report=f'''# S2 중국 도시 공개 + CHINA — 검증 보고서

**판정: 수용 가능.** 요청한 프리비즈 구현과 기술 검증을 완료했다. 사용자 미술 승인·운영 공개 승인은 별개다.

## 파일과 실행 기준

- 결과: `master-s2-city-reveal-china-v001.blend` / SHA256 `{h}`.
- 입력: `cn-city-proxy-v001/master-cn-city-proxy-v001.blend` / SHA256 `{p['base_sha256']}`. inputs/base.blend와 원본 해시가 여전히 같다.
- 같은 문자 + 기존 카메라 비교본: `baseline-with-title.blend` / SHA256 `{sha(R/'baseline-with-title.blend')}`.
- Git main@74f1b91ede4656041cf78f9882a1f98d9f190145. 기존 수정·미추적 자료를 보존했고 커밋·설치·외부 업로드는 하지 않았다.
- Blender 5.1.0, build adfe2921d5f3, Windows. 기존 Python/Pillow/ffmpeg, Blender 내장 numpy 사용. 외부 Python에 numpy가 없어서 RGB 비교는 Pillow의 RGB 바이트 비교로 수행했다.
- 시작 때 런타임 모델/추론은 unknown으로 기록했다. 이후 앱 화면에서 **GPT-6 Astra / High 선택기 표시**를 확인했다. 서버 측 실제 실행 모델은 별도로 검증하지 않았다. 독립 검토자는 GPT-6 Astra/High로 실행했다.
- PowerShell 프로세스 조회는 GUI를 열거하지 못했다. 후속 Windows 창 목록에서 원본 `* master-cn-city-proxy-v001`의 미저장 창과 새 결과 창을 확인했으며 원본 GUI를 저장·닫지 않았다. 최종 결과 창에서 f156 구도를 확인했다.

## 구현 범위

기존 도시·항구·선박을 유지하고 **문자 메시 5개 + 독립 기초 5개 + Empty 1개**를 새 컬렉션 S2_CHINA_TITLE_V001에 추가했다. 기존 438개를 포함한 결과는 449개 객체다. 각 신규 객체는 s2_reveal_owner로 구분한다.

CHINA는 CN_FRAME의 +Z를 up으로 삼아 도시 뒤 y=38.5, 바닥 z=.82에 고정했다. 폭 합계 40.1, 높이20, 두께1.2는 이 장면의 가상 프록시 단위다. 각 기초 하단은 기존 경사 지형의 실제 광선 교차점에 맞췄다. 새 큰 전시판·바다·건물 이동은 없다.

내장 Bfont를 글자별 폭·높이로 조정한 근사이며 원본 콘셉트와 정확한 서체는 다르다. 금색 외곽·두께와 붉은 전면을 메시로 결합했다. 원문/서체/설정은 title-config.json에 있다. 외부 폰트 파일을 재배포하지 않으며, 최종 표시에는 폰트가 필요 없다. 문자 애니메이션·빌보드·표시 토글은 없다.

카메라와 타깃의 **f98–214 키**만 수정했다. 선형 보간을 포함한 평가 변화는 f97 초과~f215 미만이며 0.25f 측정 범위는 f97.25–214.75다. **f96/216의 위치·방향·시선·속도와 S2 외 평가값은 원본과 정확히 같다.** 40mm, sensor/shift/clip, 전체 f0–1392,12fps, 모든 구간 마커·선박/화물 타이밍을 유지했다. S1/S3 추가 변경이나 과거 승인 범위 재사용은 없었다.

## 구도 선택과 실제 공개

동일 f156에서 전방 A와 선미 측 B 두 방향을 시험했다. A는 선박 하단 크롭과 방송탑 하부 가림이 컸다. B는 같은 방향에서 거리·시선을 조절해 선박 전체와 두 구체를 확보했다. review/directions.json과 view-A/B.png는 탐색 이력이다. 최종 f156은 preview/final-frames/0156.png를 기준으로 한다.

**공개 구간 f144–170: 27프레임, 2.25초.** 투영상 모든 지정 특징이 들어오는 더 넓은 구간은 f{features['fully_inframe_frames'][0]}–{features['fully_inframe_frames'][-1]}다. 공개의 시작/중간/끝 f144·156·170 실제 CAM_MASTER 렌더에서 CHINA, 두 구체·첨탑, 상부 개구부, 고층·수변군, 항구와 선박을 함께 확인했다. 건물은 일부 글자 하단과 겹친다. 자동 투영과 폴리곤 중심 광선은 가독성 보조 자료이며 화면 점유율이나 미술 승인의 대체가 아니다.

카메라는 컨테이너 근경에서 후퇴하며 선미 측으로 횡이동하고, 공개 후 출항하는 같은 선박에 접근한다. 카메라 정지 컷·180도 회전·도시를 다시 보러 돌아가는 움직임은 없다. 기존 가까운 B23을 유지하므로 공개 뒤 선박이 커졌다가 기존 S3에서 다시 점차 멀어지는 거리 변화는 남는다. 이를 숨기지 않고 12fps 연결 영상에 포함했다. 최종 속도/각속도 표본은 features-master-s2-city-reveal-china-v001.json에 있다.

## 검증 결과

| 검사 | 결과 | 증거 |
|---|---|---|
| 원본 RED | 새 문자/공동 특징/정적 문자 3개 실패, 기존 30개 통과 | baseline-tests.log |
| 최종 행동·도시·문자·회전 | **35/35 통과** | rotation-green-2.log |
| 경로/중복/덮어쓰기 보호 | **6/6 통과** | fixed-guards.log |
| 원본 보호 | **5,569시점(0.25f), 비카메라436개 평가/데이터 일치** | final-preservation.json |
| 카메라 보호 | 외부 평가·외부 키 데이터 및 f96/216 속도 일치 | final-preservation.json |
| 정적 신규 문자·기초 | 전 구간 위치/표시 고정 | final-preservation.json |
| 관통·지지 | **표본 통과**, 카메라/원본 형상과 신규 제목 교차 없음 | spatial.json |
| 재생성 구조 | **449개 객체, 데이터/Action/선정 평가값 동일** | reproduced-structure.json |
| 재개방·재생성 RGB | **10장씩 총20/20 정확 일치** | final-qa.json |
| 정상·느린 재생 | 원래12fps/1× 전체 완료, 별도0.5× 완료 | playback-evidence.json |
| 독립 검토 | 발견한 회전 접합 P1 수정 후 해소 확인 | independent-review.md |

40mm 렌즈는 그대로다. 0.25f 충돌 검사는 유한 표본이며 연속시간 전체 무충돌 증명은 아니다. 실제 월드 메시 BVH로 교차를 확인하고, 기초와 지형의 의도한 지지 접촉은 명시적으로 분리했다. 기초 하단 네 모서리의 지형 오차는 최대 약 0.00002m로 float 정밀도 수준이다.

## 발견한 실패와 해결

1. FCurve.update()가 범위 밖 AUTO 핸들을 재계산했다. 선형 키의 값만 변경하는 방식으로 해결했으며 보호 기준을 완화하지 않았다.
2. 독립 검토에서 f214→215 회전이2.637도/프레임으로 튀는 문제를 찾았다. 원본 구형 수면/선박 up의 회전 잔차를 f188..215에 점진적으로 반영하고 마지막 위치·시선 감속 구간을2프레임 늘렸다. 최종 f214/215/216 각변위는 **.5882/.3733/.2654도**다. 새 종단 회귀는 수정 전 RED, 첫 수정 .2675도/프레임²로 FAIL, 최종 .2149로 PASS(상한 .25 유지)였다.
3. 저장 보호 검사 중 기존 출력 사례가 입력과 같은 경로를 사용한 테스트 구성 오류를 서로 다른 기존 파일로 교정했다. 안전 규칙은 그대로다.
4. 옛 제한안과 첫 보호키 수정본 비교는 f147에서1픽셀 차이가 있었다(RGB 최대8/9/10). 이것은 최종 동일 원본 재현 검사가 아니다. image_compare.py/rgb-comparison.json은 이 이전 실패 진단 이력으로 남겼다. 최종 재현 판정은 새 파일의 final-qa.json만 사용한다.

사용자 설치 애드온의 등록/해제 경고가 배경 실행 로그에 있다. 관련 애드온 설정을 바꾸지 않았으며 작업 스크립트의 성공/실패는 대응 *-command.json의 종료 코드로 구분했다. 필요한 최종 명령은 모두 exit0이다. 이전 실패 로그는 삭제하지 않았다.

## 실제 영상·S1/S3 영향

원본/같은 문자+기존 카메라/최종 수정본을 각각 Workbench960×540,12fps,f84–480 포함397프레임으로 새 출력했다. MP4는33.083초이며 FFprobe와 전체 디코딩도 확인했다. 최종 영상은 preview/final.mp4, 비교 페이지는 http://127.0.0.1:8773/review.html 이다. 정상 재생·느린 재생·정지/왕복 탐색을 구분해 기록했다. 브라우저의 ended/played와 선택 화면을 확인했으며 모든 영상 순간을 눈으로 관찰했다고 과장하지 않는다. 드롭프레임 수는 해당 브라우저에서 확인되지 않았다.

정적 문자의 일부가 S1부터 배경에 보인다. f0/24/48/72를 새로 열어 확인했고 컨테이너·인양 동작을 막는 새 가림은 없었다. 이는 원본과 픽셀이 같다는 뜻이 아니다. title-visibility.json의1,393개 정수 프레임 광선 표본에서 문자 표면은 마지막 f203까지 검출되고 S3 이후에는 검출되지 않았다. 표본 검출을 모든 픽셀 가시성의 증명으로 쓰지 않는다. 기존 카메라에 문자만 추가한 비교는 f84–196 중111개 프레임에서 RGB 차이가 있었으며 f197–480은 같았다. 최종 카메라의 실제 상태 보존과 영상의 픽셀 변화는 분리했다.

## AC 판정

| 기준 | 판정 | 최종 근거 |
|---|---|---|
| AC-1 문자·형태·정적 배치 | 통과 | 다섯 글자 메시, 붉은 전면/금색 입체, 지형 지지, 전 구간 정적 검사, 폰트 없는 재개방 |
| AC-2 공동 공개 | 통과 | f144/156/170 실제 출력과2.25초 구간, 투영·가림 표본, 영상 검토 |
| AC-3 물류 중심 연속 연출 | 통과 | 연속 경로, 이동 유지, 회전 펄스 수정 및 독립 확인. 기존 B23에 따른 거리 변화 명시 |
| AC-4 S1→S2→S3 접합 | 통과 | f96/216 상태·속도/외부 키 정확 보존, 내부f215 회전 회귀, 연결 영상 |
| AC-5 기존 세계·행동 보존 | 통과 | 438개 원본 보호의 명시적 카메라 예외, 기존30검사, 새 충돌/가림 표본 |
| AC-6 안전 재현 | 통과 | 경로/해시/중복 보호, 새 프로세스 재개방·재생성,449개 구조와20장RGB 일치 |
| AC-7 증거와 상태 | 통과 | 최종 해시 연결, 실제 명령/종료코드/실패 이력, 재생 기록, hashes.json |

## 재현과 인계

scripts/build.py는 inputs/base.blend, title-config.json, camera-config.json, review/baseline.json에 의존한다. 모든 파일은 함께 보존한다. 소스 해시가 다르거나 출력이 이미 있거나 제목이 이미 적용돼 있으면 거부한다. 재현 실행 예와 실제 인자는 review/fixed-reproduce-command.json에 있다. 기존 출력 파일에 그대로 재실행하면 보호 오류가 정상이다.

최종 확인 명령은 scripts/final_qa.py이며, 실제 Blender 명령은 review/*-command.json과 대응 *.log에 있다. 과거 scripts/preservation.py·render.py와 원본 테스트는 읽기 전용으로 참조했고 수정하지 않았다. 과거 실패 비교 스크립트를 최종 검사 대신 실행하지 않는다. 외부 핸들러 없이 저장본을 새 Blender에서 열어 렌더했다.

`limited-s2-reveal.blend`, review/*trial.blend, reproduced-round1.blend, preview/rotation-pulse-frames 및 예전 final-* 로그는 **탈락·수정 이력**이다. 사용자 확인 대상은 상단 최종 파일과 preview/final.mp4다. 기존 도시 재모델링·미국 변경·최종 미술/스타일프레임·Higgsfield 제작은 수행하지 않았다.
'''
(R/'report.md').write_text(report,encoding='utf-8')
with (R/'decision-log.md').open('a',encoding='utf-8') as f:f.write('''
- T1 완료: 실제 원본/참조 해시 확인, 원본9장 출력, 기존30개 회귀 통과와 신규3개 RED 기록.
- T2 완료: 고정 CHINA5글자+기초5+Empty1; 동일f156에서 A/B 두 방향 비교 후 선미 측B 선택. 높이/거리를 조정한 동일 방향의 개선은 새 세 번째 방향이 아니다.
- T3 완료: 위치/시선/Quaternion 베이크, 기존B12/B23 유지. 독립검토 회전 펄스 수정 후 내부 종단 회귀35개 통과. 신규S1/S3 승인 불필요.
- T4 완료: 최종0.25f 보존5,569시점, 외부키·카메라·기존436개 비카메라, 신규 정적성과 관통/지지 검사 통과.
- T5 완료: 12fps397프레임 세 상태 비교, 최종 정상/느린 재생과 탐색 확인. S1 배경의 부분 문자는 기록하고 숨김으로 해결하지 않았다.
- T6 완료: 재개방/재생성 구조 및20장RGB 일치, 단일 읽기전용 독립검토의P1 해소, 최종해시 보고서 및 manifest 연결.
- 초기 PowerShell 프로세스 미검출은 GUI 부재 증거가 아니었다. Windows 창 조회에서 기존 원본의 미저장 창을 발견했고 그대로 보존했다. 새 최종 파일은 별도 창으로 열었다.
- 앱 선택기 표시 GPT-6 Astra/High를 후속 관찰했다. 서버 런타임 값은 독립 확인 불가다.
''')
files={}
for file in sorted(R.rglob('*')):
 if file.is_file() and file.name!='hashes.json' and '__pycache__' not in file.parts:files[str(file.relative_to(R)).replace('\\','/')]={'sha256':sha(file),'bytes':file.stat().st_size}
(R/'hashes.json').write_text(json.dumps({'final_blend_sha256':h,'files':files},indent=2),encoding='utf-8')
print('SEALED',len(files),'FILES',h)
