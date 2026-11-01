# PNPLINE Hero Section A / B · adopted 2026-11-02

최신 작업 파일:
- `F:/pnpline-landing/hero-section-video/hero-section-A.blend`: 원래 컬러 재질.
- `F:/pnpline-landing/hero-section-video/hero-section-B.blend`: 최신 White & Cyan v005. 랜드마크와 중국 항만 크레인 3대 상부의 청록색을 포함한다.

두 파일의 공통 라이팅·DOF·배경은 “hero section 영상 라이팅 제안” 세션의 최종 `hero-focus-v006` 파일에서 그대로 가져왔다. daylight-v002 라이팅, v006 DOF(최초 v004 조리개 지름의 40%), 화면 상단 #DFEAF3·하단 #F3F6F8 그라데이션이다. AgX / Medium High Contrast / exposure +0.3도 동일하다.

기존 컬러 및 흰색 버전과 형상·재질·슬롯·배치·리그·비 DOF 액션을 대조했다. 카메라 위치·회전·렌즈와 DOF는 각각 0–989프레임 전체를 검증했고, 최종 파일을 다시 열어서 검사를 반복했다. 라이팅·월드·합성 노드·배경 이미지 내장도 대조했다. 두 버전은 재질 외에는 동일하다.

review/index.html에 같은 실제 카메라의 6개 프레임을 나란히 비교할 수 있다. 이미지를 HTML에 포함했다. 검토 렌더는 Cycles OPTIX / 40 samples / 1280×720이다. 저장된 제작 설정은 원래의 Cycles / 128 samples / 1920×1080이다. 전체 990프레임 영상은 이 통합 작업에서 렌더하지 않았다.

원본 lookdev 및 모든 실험 파일을 보존했다. 이 폴더는 채택 시점의 버전 보관본이다. `latest-hero-section.json`에 A/B 경로를 기록했고, `lookdev/latest-lookdev.json`의 기본 파일은 A이며 variants.B에 B를 기록했다. blockout/latest-previz.json은 블록아웃 이력으로 남겨두었다.

렌더 명령 예시(PowerShell, A):
```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe' -b 'F:/pnpline-landing/hero-section-video/hero-section-A.blend' -E CYCLES -o 'F:/pnpline-landing/hero-section-video/renders/A/hero-' -F PNG -s 0 -e 989 -a
```
B는 파일명과 출력 폴더의 A를 B로 바꾸면 된다. GPU가 필요하면 Blender Preferences의 Cycles Render Devices에서 OptiX GPU를 선택한다. 검토 렌더의 GPU 선택은 scripts/review.py에 명시되어 있다.
