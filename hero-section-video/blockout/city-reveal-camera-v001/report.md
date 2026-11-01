# 도시 전경 카메라 수정 v003

최종 모델: `candidate-city-reveal-v003.blend`  
원본: `../curvature-rework-v001/candidate-curvature-v004.blend`  
작업공간/브랜치: 기존 F:/pnpline-landing / main. 커밋·push는 실행하지 않았습니다.

479프레임부터 급격히 선박에 접근하며 도시 상단이 잘리던 구간을 수정했습니다. 카메라의 기존 위치·회전·렌즈 키는 보존하고 카메라/주시점에만 부모 보정 레이어 두 개를 추가했습니다.

| 프레임 | 카메라 구성 |
| --- | --- |
| 440 이전 | 기존 구도와 동작 유지 |
| 440–479 | 천천히 물러나 곡면 도시 전경 확보 |
| 479–552 | USA 조형물, 주요 건물, 자유의 여신상, 창고와 부두가 함께 보이는 전경 유지. 완전 정지 대신 느린 이동 |
| 552–648 | 주시점·거리·방향을 함께 보간하여 하역 컨테이너를 화면에 유지하며 접근 |
| 648 이후 | 기존 트럭·창고 구간 카메라로 정확히 복귀 |

파일의 실제 설정은 **12fps**이며 변경하지 않았습니다. 전경 유지 구간은 약6.1초입니다. 이전 곡면 작업 보고서의24fps 설명은 잘못된 설명이었으며, 이번 미리보기는 원본12fps와 같은 시간으로 재생합니다. 미리보기는408–672프레임265장을 빠짐없이 포함한960×540 Workbench 영상입니다. 실제 모델의 렌더 해상도1280×720와 타임라인은 유지했습니다.

## 검증

- 신규 카메라3개 검사 통과: 전경 구간의 주요 랜드마크 화면 경계,440–648의 급격한 회전 방지,576–648의 하역 컨테이너 화면 유지.
- 기존 곡면·차량·컨테이너 화물·창고 작업16개 검사 통과. 총19개 통과.
- 보호 대상10,085개 원본 객체, 원본 메시·재질·동작·월드·타임라인 차이0.
- 수정 구간 밖 카메라 행렬 비교 오차0.0. 구간 내부에서도 비카메라 객체의 평가된 월드 변환 차이0.
- 479/509/552 비교 렌더와 전환부600/624/648 실제 카메라 화면 확인.

화면 경계 검사는 프러스텀 기준이며, 장면 가림은 실제 렌더를 함께 검토했습니다. 기존 곡면 모델의 알려진 부두 기단 내부 면 교차는 이 카메라 변경에서 다루지 않았습니다.

## 재생성

```powershell
$b = 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe'
$r = 'F:/pnpline-landing/hero-section-video/blockout/city-reveal-camera-v001'
& $b --background --factory-startup --python-exit-code 1 --python "$r/scripts/build_camera.py" -- --output "$r/rebuilt-camera.blend"
& $b --background --factory-startup "$r/rebuilt-camera.blend" --python-exit-code 1 --python "$r/tests/test_city_reveal.py" --python "$r/scripts/verify_preservation.py"
```

출력은 작업 폴더 안의 새 파일명이어야 합니다. 기존 파일은 덮어쓰지 않습니다.

원본 SHA256: `7fdfe45379eab1e3fc53262610dd7872461983bdb590348c1fe7052407278b1a`  
최종 SHA256: `7986cd4a6aa08b959722a5d2b3e5aff81d69ceb1a3393a436bc8b114f7d01fd3`
