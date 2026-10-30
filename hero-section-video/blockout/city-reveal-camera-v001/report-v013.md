# 정지 없이 연결되는 카메라 v013

최종 모델: `candidate-city-reveal-v013.blend`  
비교 페이지: `review-v013.html`  
미리보기: `preview/city-reveal-v013.mp4`

첨부한 7.7초 영상의 도시 진입과 선박 측면 접근 구간을 확인하고, 카메라의 구간별 속도를 측정했습니다. v011에서는 f440에서 이동 속도가 0.2619에서 약 0.0024 장면 단위/프레임으로 떨어졌습니다. f500–f504에는 정지 구간이 있었고 f596, f648에서도 감속 후 다시 출발했습니다. 각 구간이 독립적으로 정지까지 감속하도록 보간된 것이 원인이었습니다.

## 변경

기존 주요 구도와 도착 시점을 유지하면서, 연결점의 속도를 공유하는 Hermite 보간으로 바꿨습니다. 측면에 잠시 정지하는 구간을 제거하고, 방향이 바뀌는 부분만 작게 둥글게 이어 붙였습니다. 길게 돌아가는 궤도는 추가하지 않았습니다. 기존 경로 직선성 검사도 통과합니다.

- f440: 이전 진입 속도를 이어받아 측면으로 계속 이동합니다.
- f500: 선박 측면을 통과하며 바로 후면 접근을 이어갑니다.
- f596: 트럭 뒤쪽에 도착한 뒤에도 하역 구도를 유지하며 이동합니다.
- f648: 트럭 출발 때 다시 감속하지 않도록 기존 위치보다 1 장면 단위 뒤에서 연결합니다.
- f672: 원래 추적 카메라의 위치와 속도에 연결합니다.

f497 부두 수평 보정, 초기 피치 유지, 화물의 화면 내 유지 조건은 그대로 적용합니다. 물류 동작과 애니메이션 타이밍, 초점거리 키는 바꾸지 않았습니다. 이번 작업은 main에서 진행했으며 커밋·푸시는 하지 않았습니다.

## 검증

새 연속 이동 검사 2개는 v011에서 실패하고 v013에서 통과했습니다. 기존 카메라 검사 8개, 곡면·물류·창고 검사 16개를 포함해 총 26개 검사를 통과했습니다.

0.5프레임 간격으로 측정한 연결점 전후 속도는 다음과 같습니다. 단위는 장면 단위/프레임이며, 완전히 일정한 속도를 강제한 것이 아니라 멈춤 없이 완만하게 가감속하도록 설계했습니다.

| 프레임 | 직전 속도 | 직후 속도 |
| --- | ---: | ---: |
| 440 | 0.26195 | 0.27666 |
| 500 | 0.32654 | 0.32011 |
| 596 | 0.20110 | 0.19909 |
| 648 | 0.17160 | 0.16818 |
| 672 | 0.30090 | 0.30989 |

f438–f672의 최소 이동 속도는 0.14138이며 정지 구간이 없습니다. 최대 가속도는 0.07208 장면 단위/프레임², 최대 회전 속도는 1.8693°/프레임 미만입니다. 수정 구간은 f440–f672이며, 그 밖의 카메라와 투영 값은 원본과 동일합니다. 원본 보호 객체 10,085개, 메시·재질·애니메이션·월드·타임라인의 보존도 확인했습니다.

검증 로그는 `review/continuous-v013-tests.log`, `review/continuous-v013-operations.log`에, 수치 요약은 `review/candidate-city-reveal-v013-continuous-audit.json`에 있습니다.

## 재생성

중간 v008/v011 Blender 파일 없이 기존 곡면 최종 모델에서 직접 생성합니다.

```powershell
$blender = 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe'
$root = 'F:/pnpline-landing/hero-section-video/blockout/city-reveal-camera-v001'
& $blender --background --factory-startup --python-exit-code 1 --python "$root/scripts/build_continuous_camera.py" -- --output "$root/rebuilt-continuous-camera.blend"
& $blender --background --factory-startup "$root/rebuilt-continuous-camera.blend" --python-exit-code 1 --python "$root/tests/test_continuous_motion.py" --python "$root/tests/test_level_handoff.py" --python "$root/scripts/audit_continuous_camera.py"
& $blender --background --factory-startup "$root/rebuilt-continuous-camera.blend" --python-exit-code 1 --python "$root/scripts/verify_continuous_preservation.py"
```

최종 SHA256: `99361028c1463fe4fdeb085146e0f00e64df1f9796e5b4b3dfe79bdf0815d6cf`

최종 모델에서 f408–f696의 289프레임을 렌더해 12fps, 960×540 Workbench 영상으로 인코딩했습니다. 길이는 24.083333초입니다. 비교 페이지에서 v011과 동시 재생을 실행했고, 두 영상 모두 미디어 오류 없이 끝까지 재생됐습니다. 최종 모델·검증 결과·영상 입력 해시가 일치합니다.
