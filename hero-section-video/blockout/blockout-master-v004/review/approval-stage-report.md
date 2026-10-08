# S2 카메라 수정 검토 — v004

판정: **재작업/경계 승인 필요. 전체 수용 완료 아님.**

`master-v004.blend`는 S1/S3 경계를 보존하는 제한적 개선안이다. `s2-target-candidate-v004.blend`는 보드의 큰 후방 추적 구도를 우선한 **S2 전용 제안**이다. 후보의 f216→217에는 미접합 점프가 있으므로 본편 통합본으로 사용하지 않는다. 원본 v003은 그대로 보존했다.

## 기준과 입력

- main@6079b392d7de54509ed50454ddd2745273cc0078. 사용자 저장 v003에는 커밋 이후 변경이 있어 생성기로 재생성하지 않고 저장 파일을 복사했다.
- 원본 및 inputs/base-v003.blend SHA256: `ae1a8ea2dfbf8127b27ecd9ad999589575e87aac9eb578c970fd812e7063964e`.
- Blender 5.1.0 adfe2921d5f3, Workbench, 전체 0–1392f, 12fps. S2 96–216f, CAM_MASTER/CAM_LOOK_TARGET, 40mm. 실제 선박 +X 선수, -X 선미, -Y 해측.
- 입력 녹화: 사용자가 제공한 Documents/Bandicam 파일을 inputs/recording.mp4로 보존. ffprobe: 1576×880, 231프레임, 약 7.70초/30fps.
- 보드 5개를 inputs/boards에 보존. 비교에서는 테두리와 하단 메모를 제외한 영역만 비율 유지해 표시했다.
- 녹화의 시작/끝 컨테이너·크레인·선박 투영 관계는 저장본 f96/f216의 CAM_MASTER 출력과 시각적으로 대응한다. 녹화에는 랜덤 색상·가이드와 다른 뷰포트 표시가 있어 픽셀 동등성을 주장하지 않는다. 정확한 녹화 시각↔타임라인 프레임 대응은 확정하지 않았으며, 녹화 시간을 키프레임 번호로 환산하지 않았다. 마지막 정지 화면을 카메라 정지로 해석하지 않았다.
- 재현은 v001 생성 앵커가 아니라 현재 v003 실제 평가값을 기준으로 했다. 특히 f96–159에는 앞선 S1 접합 보정이 존재한다.

## 실제 변경

| 항목 | master-v004 / 경계 보존 | 별도 S2 후보 |
|---|---|---|
| 카메라·타깃 변경 | f98–214 | f98–216 |
| f96 및 S1 | 위치·회전·타깃·렌즈와 양쪽 인접 프레임 그대로 | 동일 |
| f216 및 S3 | 원본 그대로 | f216만 제안 변경, f217 이후 원본 그대로이므로 미접합 |
| 렌즈 | 기존 40mm 유지 | 기존 40mm 유지 |
| 비카메라 | 1393프레임 평가 상태 모두 일치 | 동일 |
| K5 선박 투영 폭 | 기존 약 45.1% | 약 64.2% |

초반의 급한 후퇴·상승을 줄이고 갑판과 컨테이너가 전경에 오래 남도록 했다. 각 관찰점에서 멈추지 않는 Hermite 위치·타깃 경로를 실제 선박 공간에서 평가하고, 정수 프레임으로 베이크했다. 베이크 키에는 LINEAR를 유지했다. 공유 spline, 선박 동작, 형상, 환경, 소재, 개수, 타임라인, 렌즈 키를 바꾸지 않았다. 재현 소스는 scripts/revise_s2.py다.

## 보드별 판정

비교: review/K1-K5-comparison.png. 열 순서는 보드 / 원본 / 경계 보존 / 별도 후보다.

| 관찰점 | 프레임 | 개선 또는 보존 | 남는 차이와 원인 |
|---|---:|---|---|
| K1 | 96 | S1에서 넘어오는 근경·속도 그대로 | 보드의 큰 좌측 선교와 긴 갑판 깊이 부족. 낮은 프록시 선교 및 고정 B12 구도 제약 |
| K2 | 124 | 선박 투영 폭이 화면 폭보다 커 전경 크롭 유지. 원본처럼 일찍 작은 전체 선박이 되지 않음 | 보드의 선교 높이와 긴 적재열은 형상 차이 |
| K3 | 148 | 카메라 선박 상대 높이 약 15.4→8m. 큰 적재부와 뒤의 크레인·도시 관계 유지 | 도시와 해안의 세부 밀도 부족. 보드의 넓은 수면 간격 및 선교 구도는 현재 배치·비례에서 미달 |
| K4 | 180 | 같은 해측에서 선미 방향으로 이동. 후보가 선박을 더 크게 유지 | 경계 보존안은 기존 먼 B23를 향해 계속 후퇴하므로 근접 추적 효과 제한 |
| K5 | 216 | 후보는 선미와 한쪽 선측, 선수로 이어지는 깊이를 크게 표시. 선수·선미 크롭 검사 통과 | 경계 보존안은 목표 미충족. 후보에서도 낮은 선교, 짧은 선체, 왼쪽 항구가 좁게 보이는 차이 존재 |

보드의 우측→좌측 항구 변화 자체는 오류라고 단정하지 않았다. 실제 동일 해측 경로에서도 후방으로 돌면 부두가 왼쪽으로 이동한다. 다만 후보에서는 가까운 선박이 화면을 차지하고 크레인은 왼쪽 가장자리에 남아 보드의 넓은 항구 배경과는 다르다. 세계를 이동하거나 반전하지 않았다. review/camera-path-top.png는 고정 중국 지역 좌표에 투영한 실제 경로와 시선이다. 환경 footprint는 생략되어 있으므로 이 도표만으로 보드 전체의 공간 양립성을 증명하지 않는다.

형상 보강이 필요하다면 최소 별도 제안은 선교의 높이/위치를 다시 정하는 것이다. 이번에는 구현하지 않았다. 선체 길이·도시 확장은 별도 디자인 범위다.

## 경계 변경 제안 — 승인 전 미적용

후보 f216의 선박 상대 카메라는 (-17,-10,8), 타깃은 (-1.5,0,0.6)이다. 원본 카메라 (-17,-26,19)와 월드 위치 차이는 약 19.4165m다. 기존 f217로 바로 이어지면 약 19.7293m의 점프가 발생한다. 실제 전체 타임라인 검사 `test_full_timeline_camera_continuity`가 이 프레임에서 실패했다.

후보를 채택하려면 **B23 f216 및 S3 초반 f217–251의 카메라·타깃 수정**을 제안한다. f252에서 원래 경로와 속도로 복귀하고 f252 이후는 그대로 보존하는 접합 계산이다. S1 및 선박/환경은 바꿀 필요가 없다.

계산한 Hermite 접합 계열에서 기존 이동/각도 검사와 0.15m/f² 가속도 한계를 만족하는 가장 이른 복귀 프레임은 f250이었다. 여유를 둔 f252안은 최대 이동 약 1.609m/f, 각도 약 1.4358°/f, 가속도 약 0.1369m/f²다. 이는 이 접합 계열의 정수 프레임 수치 가능성 조사이며, 전역 최소 구간이나 완성된 연출을 뜻하지 않는다. 승인 후 서브프레임 충돌·가림·정상 속도 연결 렌더를 다시 검증해야 한다. 소스 scripts/propose_join.py, 수치 review/s3-join-proposal.json.

## 검증과 AC

| 기준 | 상태 | 증거와 한계 |
|---|---|---|
| AC-1 입력/기준 | 조건부 확인 | 원본 해시·소스·녹화·보드 확보, 실제 카메라와 시각 대응. 녹화의 정확한 타임코드는 미확정 |
| AC-2 목표 구도 | 부분 충족 | K2/K3 개선, 후보 K5 개선. 경계 보존안 K5 및 프록시 형상 관련 차이 미충족 |
| AC-3 연속성 | 제한안 통과 / 후보 S2 내부 통과 | 0.25프레임 샘플. 최대 이동 제한안 0.4831m/f, 후보 0.3366m/f. 최대 각속도 1.2562/1.5905°/f. 후보→S3는 제외했고 별도로 실패를 기록 |
| AC-4 환경 보존 | 통과 | 304개 오브젝트 유지. 비카메라 302개 상태, 메쉬/재질/애니메이션 서명, 1393프레임 평가 변환 일치 |
| AC-5 관통/가림 | 샘플 범위 확인 | S2 전체 0.25f 간격, 0.12m 여유를 둔 스케일 반영 OBB 검사 0건. near/far clip 유지. 실제 크기와 관찰 스틸 확인. 정확한 연속 swept mesh 충돌이나 모든 표면의 가시성 증명은 아님 |
| AC-6 범위/접합 | 제한안 통과 / 후보 보류 | 제한안 f0–97 및 f215–1392 정확 보존, 양 경계 인접 상태 그대로. 후보는 S3 접합 승인 대기 |
| AC-7 재현 | 현재 두 산출물 확인 | 새 프로세스 재개방 f96/148/216 RGB 일치. 소스/경로/검사/해시 제공. 제안 접합 자체는 미적용 |

기존 저장본의 기준 검사 32/32 통과. 경계 보존안은 기존 장면 24/24, S1 4/4, 적용 S2 검사 4/4 통과. 후보 전용 K5 검사 2개는 제한안에서는 적용하지 않으며 K5 미충족을 위 표에 남겼다. 후보 S2 검사는 6/6 통과하지만 전체 장면 검사는 23/24: 위 f217 점프 1건 실패다. 후보 실패를 삭제하거나 기준을 완화하지 않았다.

기존 v003의 “f96 이후 카메라 전부 그대로” 검사는 이번 S2 변경 요청과 충돌하므로 현재 요구의 미승인 범위 보존 검사로 대체했다. S1 동작과 f215 이후 제한안 카메라는 별도로 검증했다. test_scene.py의 버전 기대값만 v003→v004로 명시 변경했으며 기존 행동 기준은 유지했다.

프리뷰는 모두 960×540/12fps. S2 비교는 96–216 양 끝 포함 121프레임/10.0833초, 연결 영상은 84–240f/157프레임/13.0833초다. 정상 1배속 실제 Chrome 재생에서 생성 영상 4개 모두 끝까지 재생되고 각 0프레임 드롭이었다. 입력 녹화는 231프레임 디코드, 3프레임 드롭이 기록되어 표본 화면과 정지 프레임으로 보완했다. review/playback-check.json 참조.

## 파일과 재현

- master-v004.blend: 경계 보존안. s2-target-candidate-v004.blend: 승인용 S2 후보.
- preview/s2-before.mp4, s2-after.mp4, s2-target-candidate.mp4, s1-tail_s2_s3-head.mp4.
- review/K1-K5-comparison.png, camera-path-top.png, camera-before-after.json, motion-*.json, states-*.json, reopen-check.json.
- inputs/base-v003.blend, recording.mp4, recording-probe.json, boards/, task-spec.md.
- scripts/revise_s2.py, test_s2.py, test_scene.py, test_s1_camera.py, scene_evidence.py, validate_motion.py, render_evidence.py, propose_join.py, playback_review.cjs, reopen_check.py.

기본 재현 명령(작업 폴더에서 PowerShell):

```powershell
$blender = 'C:\Program Files\Blender Foundation\Blender 5.1\blender.exe'
& $blender --background --factory-startup inputs/base-v003.blend --python-exit-code 1 --python scripts/revise_s2.py -- limited
& $blender --background --factory-startup inputs/base-v003.blend --python-exit-code 1 --python scripts/revise_s2.py -- candidate
& $blender --background --factory-startup master-v004.blend --python-exit-code 1 --python scripts/test_scene.py --python scripts/test_s1_camera.py --python scripts/test_s2.py -- limited
& $blender --background --factory-startup master-v004.blend --python-exit-code 1 --python scripts/validate_motion.py -- limited
& $blender --background --factory-startup s2-target-candidate-v004.blend --python-exit-code 1 --python scripts/test_s2.py -- candidate
```

범용 Python 증거 제작에서 numpy/cv2가 설치되어 있지 않음을 확인했다. 설치하지 않고 PIL·표준 라이브러리로 비교표를 생성했다. 기존 CAMERA_PATH 오브젝트는 비카메라 보존을 위해 원본 그대로이며 새 카메라 경로 가이드가 아니다. 새 도표와 scene metadata에 이 한계를 명시했다. 프리뷰와 작업 창에서는 가이드를 숨겼다.

최종 파일 해시는 hashes.json 및 review/reopen-check.json 참조. 커밋·push·PR·외부 서비스 변경은 수행하지 않았다.

## 독립 검토

새 맥락의 검토자가 원본 및 두 산출물을 새 Blender 프로세스로 열어 1393개 프레임과 정적/재질 서명을 메모리에서 재계산했고 기록과 일치함을 확인했다. 승인용 비교 패키지에 Critical/Important 지적은 없었다. 전체 연출 완료 승인과는 별개다.

경미 사항 1개는 보류했다. 후보 파일 자체에는 S2 preview range가 저장되어 있지 않으므로 파일을 직접 다시 열면 96–216 범위를 수동으로 지정해야 한다. 현재 열린 후보 창은 open_review.py가 이 범위를 메모리에 설정했다. 검토자의 판단 유보 항목과 적용 판단은 progress.md에 모두 기록했다. 추가 구현이나 두 번째 리뷰는 수행하지 않았다.
