# 선박 측면 도착과 트럭 후면 연결 v008

최종 모델: `candidate-city-reveal-v008.blend`  
비교 페이지: `review-v008.html`  
미리보기: `preview/city-reveal-v008.mp4`

f504 이전에 선박 측면을 확보하도록 카메라 도착 시점을 앞당겼습니다. 도시 앞에서 멀리 머무르던 v006 동선 대신, 선박 측면과 트럭 뒤쪽을 잇는 직선 구간으로 구성했습니다. 기존 main 작업공간에서 작업했습니다.

## 변경한 동선

| 프레임 | 구도와 이동 |
| --- | --- |
| f440 이전 | 기존 도시 진입 카메라 |
| f440–f500 | 도시 전경에서 선박 측면까지 직선 접근. 진입 피치·롤 유지 |
| f500–f504 | 선박 측면 구도 유지 |
| f504–f596 | 트럭 뒤쪽으로 직선 접근. 이동 속도를 완만하게 가감속 |
| f596–f648 | 트럭 후면에서 컨테이너 하강을 보며 기존 추적 위치에 연결 |
| f648 이후 | 기존 트럭 추적 카메라 |

원본 물류 동작에서는 f504 이후 스프레더가 화물에 접근하고, f528 이후 화물을 들어 올립니다. f560–f600에 트럭 쪽으로 이동한 뒤 f600 무렵부터 내려갑니다. 새 카메라는 f504부터 후면으로 이동하며, 실제 하강 전에 후면 구도를 확보합니다. 물류 동작의 시점은 변경하지 않았습니다.

이전 요청의 도시 전경 유지 구간은 이번 요청에 맞춰 앞당겼습니다. 따라서 과거 v006의 f440–f552 피치·롤 고정과 f479–f552 전체 도시 프레이밍은 이번 버전의 조건이 아닙니다. 새 고정 구간은 f440–f504이며, 이후에는 후면 구도로 완만하게 연결됩니다.

## 검증

- 새로운 카메라 검사 6개와 곡면·화물·트럭·창고 검사 16개, 총 22개 통과.
- 원본 v006에서는 측면 도착, 직선 이동, 하강 전 후면 도착 검사 3개가 실패했습니다. 수정본에서는 모두 통과합니다.
- 선박의 정확한 측면과 카메라 위치의 차이: f500에서 약 15.75°, f504에서 약 16.77°. f504 전에 거의 측면인 구도를 확보했습니다.
- 세 이동 구간의 실제 경로 길이 ÷ 시작·끝 직선거리: 모두 약 1.00000001. 공간상 큰 원호를 사용하지 않았습니다.
- 0.5프레임 간격으로 측정한 최대 회전 속도: 약 1.962°/프레임. 초기 v007의 빠른 중간 회전을 줄였습니다.
- f440–f504의 피치 변화 폭 0.0075°, 롤 변화 폭 0.0015° 미만. 정수 사이 프레임까지 검사했습니다.
- f504–f648의 하역 컨테이너가 화면 안에 유지되는지 검사하고, 측면·인양·트럭 후면·하강 렌더를 직접 확인했습니다.
- 원본 초점거리 애니메이션은 동일하며, 수정 구간 밖 렌즈 시프트를 포함한 투영 값 오차는 0.0입니다.
- 보호 객체 10,085개와 원본 메시·재질·애니메이션·월드·타임라인이 동일합니다. 수정 구간 밖 카메라 행렬 오차도 0.0입니다. `review/candidate-city-reveal-v008-preservation.json`에 기록했습니다.

## 재생성

```powershell
$blender = 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe'
$root = 'F:/pnpline-landing/hero-section-video/blockout/city-reveal-camera-v001'
& $blender --background --factory-startup --python-exit-code 1 --python "$root/scripts/build_side_handoff_camera.py" -- --output "$root/rebuilt-side-handoff.blend"
& $blender --background --factory-startup "$root/rebuilt-side-handoff.blend" --python-exit-code 1 --python "$root/tests/test_side_handoff.py" --python "$root/scripts/audit_side_handoff.py"
& $blender --background --factory-startup "$root/rebuilt-side-handoff.blend" --python-exit-code 1 --python "$root/scripts/verify_preservation.py"
```

최종 v008 SHA256: `99f3ba32b84e864fc0162432b7cde09840733bffe09a36e23216bd956f88d030`

검증 기록은 `review/tests-v008-full.log`, `review/candidate-city-reveal-v008-side-audit.json`에 있습니다. 카메라 방향 스킬의 측면·후면 전환과 투영 보존 기준을 Blender 장면에 적용했습니다.

미리보기는 최종 v008 파일에서 f408–f672의 265프레임을 모두 렌더한 960×540 Workbench 영상입니다. 원본과 같은 12fps로 인코딩했으며 길이는 22.083333초입니다. 비교 페이지는 동일한 프레임의 v006과 v008을 전환해 볼 수 있습니다.

브라우저에서 비교 이미지 전환과 정상 로딩을 확인했습니다. 영상은 22.083333초 끝까지 재생되었으며 미디어 오류가 없었습니다. 커밋·푸시는 하지 않았습니다.
