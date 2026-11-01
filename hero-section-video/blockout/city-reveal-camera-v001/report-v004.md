# 가까운 도시 전경 카메라 v004

최종 모델: `candidate-city-reveal-v004.blend`  
미리보기: `preview/city-reveal-v004.mp4`  
비교 페이지: `review-v004.html`

f455–f521에서 선박과 미국 상징 도시가 지나치게 작아지고, 이후 하역 장면으로 돌아오는 회전이 커진다는 피드백을 반영했습니다. 기존 main 작업공간에서 수정했습니다.

기존 v003은 먼 전경 위치에 렌즈 값에 비례한 거리 보정을 적용해 최대 주시점 거리가 165.1까지 늘어났습니다. v004에서는 더 낮고 측면에 가까운 시점을 사용해 USA 조형물과 자유의 여신상, 선박을 함께 크게 담습니다. 렌즈 애니메이션은 그대로 유지합니다. 진입부도 주시점·방향·거리를 함께 보간하여 시선과 위치가 따로 움직이지 않게 했습니다.

| 측정 항목 | v003 | v004 |
| --- | ---: | ---: |
| f455–f552 최대 카메라–주시점 거리 | 165.10 | 106.25 |
| f509 카메라–주시점 거리 | 161.51 | 101.79 |
| f509 선박 선체의 화면 폭 비율 | 11.65% | 13.90% |
| f552→f648 회전량 | 60.88° | 39.68° |
| f440–f648 프레임 간 최대 회전 | 1.19° | 0.77° |

거리는 Blender 장면 단위입니다. 회전량은 카메라 방향 쿼터니언의 짧은 호 각도로 측정했습니다. f479–f552의 도시 전경 유지 시간과 f648의 기존 카메라 복귀 시점은 유지했습니다.

## 검증 기록

`tests/test_close_city.py`의 거리 제한, 선박 화면 크기, 하역 연결 회전 검사 3개가 이전 v003에서 모두 실패한 뒤, v004에서 통과했습니다. 기존 전경 프레이밍·회전 연속성·컨테이너 화면 유지 검사도 통과했습니다.

첫 전체 검사에서는 평면 좌표용 창고 검사를 직접 실행하여 `test_cyan_conveyor_has_physical_continuous_support`와 `test_header_frames_open_working_interior`가 실패했습니다. 이 모델에 필요한 기존 곡면 창고 검사 실행기 `curvature-rework-v001/scripts/test_warehouse_frame.py`를 사용하여 다시 실행한 전체 검사 22개는 모두 통과했습니다. 최초 로그는 `review/tests-v004-full.log`, 올바른 곡면 좌표계에서 실행한 최종 로그는 `review/tests-v004-curved-suite.log`에 남겼습니다.

보존 비교에서는 카메라 부모 관계 두 개만 예외로 두고, 원본 객체 10,085개·메시·재질·동작·렌즈·월드·타임라인에 차이가 없음을 확인했습니다. 수정 구간 밖 카메라 행렬 오차는 0.0입니다. 렌더는 원본과 같은 12fps, f408–f672의 265프레임을 사용합니다. 미리보기는 960×540 Workbench이며 최종 모델의 원래 해상도 설정은 유지합니다. 기존 검사 도우미에서 향후 Blender 6.0 API 변경에 대한 경고가 출력되었지만, 실행 중인 Blender 5.1에서 검사와 저장은 정상 완료되었습니다.

## 재생성

```powershell
$blender = 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe'
$root = 'F:/pnpline-landing/hero-section-video/blockout/city-reveal-camera-v001'
& $blender --background --factory-startup --python-exit-code 1 --python "$root/scripts/build_close_camera.py" -- --output "$root/rebuilt-close-camera.blend"
& $blender --background --factory-startup "$root/rebuilt-close-camera.blend" --python-exit-code 1 --python "$root/tests/test_close_city.py" --python "$root/tests/test_city_reveal.py" --python "$root/scripts/verify_preservation.py"
```

원본 곡면 모델 SHA256: `7fdfe45379eab1e3fc53262610dd7872461983bdb590348c1fe7052407278b1a`  
최종 v004 SHA256: `f7a7de58087a634678ab2100915c862ce1db61d8a320562def8c318b9c7b45f6`

브라우저에서 최종 영상을 재생하여 22.083333초 끝까지 재생되고 미디어 오류가 없음을 확인했습니다. 비교 페이지의 521프레임 전후 이미지도 정상적으로 전환됩니다.
