# 선박 측면 롤 보정 v011

최종 파일: `candidate-city-reveal-v011.blend`  
비교 페이지: `review-v011.html`  
미리보기: `preview/city-reveal-v011.mp4`

사용자가 승인한 v008의 카메라 경로와 타이밍을 유지하면서 f497 전후의 화면 기울기를 보정했습니다. main 작업공간에서 작업했으며 커밋·푸시는 하지 않았습니다.

## 결과

f497에서 화면에 투영된 부두 앞쪽 수평선의 각도는 **−14.3347° → 약 0°**, 선박의 긴 측면 하단선은 **−12.5553° → +1.7794°**로 바뀌었습니다. 원근 때문에 모든 선을 동시에 정확한 수평으로 만들 수는 없으므로 부두를 주 기준으로 삼았습니다. 이는 Blender의 전역 Euler 롤 값을 0으로 설정했다는 뜻이 아니라, 첨부 이미지에서 지적한 화면 기울기를 실제 항만 기준으로 바로잡았다는 뜻입니다.

원인은 전역 좌표의 롤 고정과 곡면 지구에 배치된 항만 좌표계가 서로 다르기 때문이었습니다. 기존 전역 롤 고정 검사는 이 차이를 검출하지 못했습니다. 새 검사는 실제 부두와 선박 선분의 화면 각도를 측정합니다.

| 구간 | 롤 보정 |
| --- | --- |
| f440–f479 | 부두 수평 기준으로 완만하게 진입 |
| f479–f512 | 부두 앞쪽 선을 수평으로 유지 |
| f512–f552 | 후면으로 회전하며 부두 선이 짧아지기 전에 항만 수직축 기준으로 전환 |
| f552–f600 | 항만 수직축을 기준으로 안정된 하역 구도 유지 |
| f600–f648 | 기존 카메라 자세로 완만하게 복귀 |
| 그 밖 | v008 그대로 |

롤은 광축 주위의 회전만 추가하며, 렌즈 시프트도 같은 기준으로 회전시켜 화면 중앙의 시선을 유지합니다. 카메라 위치·앞쪽 방향·타깃·초점거리·물류 애니메이션은 유지됩니다. 0.25프레임 간격으로 보정을 기록해 키 사이의 위치 오차도 줄였습니다.

## 검증

- 기존 v008에서 부두 수평·선박 측면 수평 검사 2개가 실패하고, 최종 v011에서 통과했습니다.
- 기존 측면 도착·직선 경로·후면 접근·급격한 회전 방지·화물 프레이밍 검사와 새 수평·피치 검사, 총 8개 통과. 이전의 전역 롤 고정 조건은 이번 요청에 따라 화면 수평 검사로 대체했습니다.
- 0.5프레임 간격 비교에서 v008 대비 위치 최대 성분 오차는 0.0000611 장면 단위, 카메라 앞쪽 방향 오차는 0.000000418, 화면 중앙 시선 방향 오차는 0.000000388입니다. 부동소수점 계산 오차 범위입니다.
- 타깃 위치와 초점거리는 동일합니다. f440 이전과 f648 이후의 카메라 행렬·렌즈 시프트 오차는 0.0입니다.
- f497·f528·f552의 실제 렌더에서 수평 보정과 화물 프레이밍을 확인했습니다.
- 곡면·트럭·화물·창고 검사 16개도 통과해 총 24개 검사를 통과했습니다. 보호 객체 10,085개와 원본 메시·재질·애니메이션·월드·타임라인이 그대로 유지됩니다.

## 재생성

```powershell
$blender = 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe'
$root = 'F:/pnpline-landing/hero-section-video/blockout/city-reveal-camera-v001'
& $blender --background --factory-startup --python-exit-code 1 --python "$root/scripts/build_level_roll_camera.py" -- --output "$root/rebuilt-level-camera.blend"
& $blender --background --factory-startup "$root/rebuilt-level-camera.blend" --python-exit-code 1 --python "$root/tests/test_level_handoff.py" --python "$root/scripts/audit_level_camera.py"
& $blender --background --factory-startup "$root/rebuilt-level-camera.blend" --python-exit-code 1 --python "$root/scripts/verify_level_preservation.py"
```

최종 모델 SHA256: `2de8a9c973e84db01b4bd557820b3ef714ca1ac5baa300cb65d081cfb2c169f2`

최종 결과는 v011입니다. v009와 v010은 전환과 투영 검증 중의 중간 산출물입니다.

최종 모델에서 f408–f672의 265프레임을 모두 렌더해 원본과 같은 12fps로 인코딩했습니다. Workbench 미리보기 해상도는 960×540, 길이는 22.083333초입니다. 최종 모델 해시와 영상 입력 해시가 일치합니다.

브라우저의 비교 이미지 전환과 영상의 끝까지 재생을 확인했습니다. 종료 시간은 22.083333초이며 미디어 오류는 없습니다.
