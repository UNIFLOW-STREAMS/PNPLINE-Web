# 도시 진입 구간 피치·롤 고정 v006

최종 모델: `candidate-city-reveal-v006.blend`  
비교 페이지: `review-v006.html`  
미리보기: `preview/city-reveal-v006.mp4`

첨부 영상의 도시 진입부에서 카메라가 아래를 향하면서 화면도 옆으로 기울어지는 문제를 수정했습니다. 기존 main 작업공간에서 작업했습니다.

## 변경

v004의 f440–f552에서는 월드 기준 피치가 약 −14.58°에서 −26.34°로, 롤이 −5.87°에서 약 −17.95°까지 변했습니다. 곡면 도시의 로컬 방향으로 카메라를 정렬하면서 생긴 약 11.76°의 피치 변화와 12.08°의 롤 변화가 원인이었습니다.

v006에서는 **f440–f552의 피치와 롤을 진입 시점에 고정**했습니다. 위치와 좌우 회전은 계속 움직입니다. 카메라를 낮추면 도시가 지구 곡면 뒤로 가려지므로, v004의 카메라 위치와 초점거리를 보존하고 렌즈 시프트로 화면 중심을 보정했습니다. 시프트는 카메라 보정 객체의 키프레임과 단순 드라이버 두 개로 제어합니다.

| 구간 | 동작 |
| --- | --- |
| f440 이전 | 기존 카메라 유지 |
| f440–f552 | 피치 −14.58162°, 롤 −5.86704° 고정. 가까운 도시 전경 유지 |
| f552–f648 | 피치·롤·좌우 회전을 각각 완만하게 보간하여 기존 하역 카메라에 연결. 이 구간은 피치 고정 구간이 아님 |
| f648 이후 | 기존 카메라와 렌즈 시프트 값으로 복귀 |

## 검증

- 피치 고정·롤 고정·경계에서의 급격한 변화 방지 검사 3개는 v004에서 실패하고 v006에서 통과했습니다. 고정 구간은 정수 프레임뿐 아니라 0.5프레임 간격으로 검사했으며, 피치·롤 변화 폭이 각각 0.02° 미만입니다.
- 기존 거리·회전량·선박 크기·랜드마크 프레이밍·하역 컨테이너 프레이밍 검사도 통과했습니다.
- 곡면·트럭·화물·창고 검사를 포함한 전체 검사는 `review/tests-v006-full.log`에 기록했습니다. 창고 검사는 기존 곡면 좌표계 실행기를 사용합니다.
- 원본 보호 객체 10,085개, 메시·재질·동작·월드·타임라인은 그대로입니다. 수정 구간 밖 카메라 행렬 오차는 0.0입니다.
- v004 대비 카메라 위치의 최대 성분 오차는 0.0000458 장면 단위이며 부동소수점 계산 오차 범위입니다. 초점거리 애니메이션은 동일하며, 수정 구간 밖 렌즈 시프트를 포함한 투영 값의 오차는 0.0입니다.
- 최종 모델은 원본 12fps와 해상도 설정을 유지합니다. 영상은 f408–f672의 265프레임을 원래 속도로 재생하는 960×540 Workbench 미리보기입니다.

검토 중 피치만 고정하고 시선축을 따라 위치를 다시 계산한 v005는 수치 검사에는 통과했지만 도시 일부가 지구 곡면에 가려져 채택하지 않았습니다. 최종 결과는 v006입니다.

## 재생성

```powershell
$blender = 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe'
$root = 'F:/pnpline-landing/hero-section-video/blockout/city-reveal-camera-v001'
& $blender --background --factory-startup --python-exit-code 1 --python "$root/scripts/build_pitch_locked_camera.py" -- --output "$root/rebuilt-pitch-camera.blend"
& $blender --background --factory-startup "$root/rebuilt-pitch-camera.blend" --python-exit-code 1 --python "$root/tests/test_pitch_lock.py" --python "$root/tests/test_close_city.py" --python "$root/tests/test_city_reveal.py" --python "$root/scripts/verify_preservation.py"
& $blender --background --factory-startup "$root/rebuilt-pitch-camera.blend" --python-exit-code 1 --python "$root/scripts/verify_pitch_projection.py"
```

최종 v006 SHA256: `97396d0a00f4f6cf770567d2d1e5ee71b254e837ce9c84b97994771fe8aa4386`

최종 전체 검사 결과: 25개 통과. 보존 검사 두 종류와 영상의 입력 모델 해시가 최종 v006 파일과 일치합니다.

브라우저에서 479프레임 비교 이미지가 정상 전환되고, 최종 영상이 미디어 오류 없이 22.083333초 끝까지 재생되는 것을 확인했습니다.
