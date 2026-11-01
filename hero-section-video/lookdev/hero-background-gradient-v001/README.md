# PNPLINE Hero 背景 / background-gradient-v001

별도 파일: pnpline-hero-background-gradient-v001.blend
기준 파일: hero-lighting-daylight-v002/pnpline-hero-lighting-daylight-v002.blend

화면 상단 #DFEAF3, 하단 #F3F6F8의 부드러운 수직 그라데이션을 적용했습니다. 화면 좌표를 사용하므로 카메라가 이동해도 배경의 방향과 색 분포가 일정합니다. 별도 지평선이나 배경 지오메트리는 추가하지 않았습니다.

Cycles Film Transparent와 Compositor Alpha Over로 배경을 합성합니다. 기존 조명, World 셰이더, 형상, 재질, 카메라와 액션은 저장 후 다시 열어 동일함을 확인했습니다. 그라데이션은 현재 AgX / Medium High Contrast / 노출 +0.3을 역변환하여 지정한 출력 색을 유지합니다. float EXR 이미지는 Blender 파일에 내장했습니다. 노출이나 색 관리 설정을 변경하면 출력 배경색도 달라집니다.

Blender에서 F12 렌더로 결과를 확인할 수 있습니다. 카메라 뷰포트의 Compositor도 Camera로 설정했습니다. 일반 Solid 뷰에는 합성 배경이 표시되지 않습니다.

검토 이미지: review/after (110,200,332,820,930). 960x540 / Cycles OptiX /32 samples / OIDN / 고정 seed29. review/comparison은 동일 조명과 노출의 배경 전후 비교입니다. 전체 영상은 렌더하지 않았습니다. 마지막 출고 구간의 어두운 조명은 기준 v002 설정을 그대로 사용한 결과입니다.

verification.json: 원본 SHA256, 형상·재질·카메라·액션 및 조명·World 보존, 합성 노드와 이미지 내장 검사 결과.
background-settings.json: 배경 설정.
scripts/background.py: Blender5.1에서 build,render,verify 모드로 재현합니다. scripts/lighting_helpers.py는 검토 렌더와 장면 기록 도우미입니다.
