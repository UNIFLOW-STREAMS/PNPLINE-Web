# S5 스토리보드 동기화 v002 — 최종 동기화 후보

사용자가 2026-10-09에 지정한 `s5-integration-v001/master-s5-integration-v001.blend`를 기준으로 한다. 현재 SHA256은 `8c76f0e184bc742309cf66dcf9f3f5fa7072e02b54b58e6985a91ff1ae57b665`다. 마스터는 수정하지 않았다. 앞서 만든 full-layout-master-v001은 별도로 보존되며 이번 스토리보드의 기준이 아니다.

## 기준과 실행 결과

Blender 5.1.0에서 실제 저장본을 새로 열었다. Scene PNPLINE_MASTER_v005, Camera CAM_MASTER, 12fps/fps_base 1, 전체 f0–1392, S5 시작648/S6 시작900을 확인했다. 작업 HEAD는 b56acf916901ce24be69686ef349ed61b437d608이다. 실행 모델·추론 설정은 미확인이다.

현재 원본과 기존 s5-sync-v001 추출 기준은 바이트가 같다. 과거 렌더의 원래 기록을 보존하고 325개 PNG·의존 파일 해시를 모두 확인했다. 실제 저장본에서 325프레임의 카메라와 주변 162개 객체 상태를 새로 평가한 결과 차이는 0이다. 검증된 원본 스틸·영상·표현 샘플을 재사용했으며 새로 렌더했다고 표시하지 않았다. 출처는 storyboard-manifest.json의 reuse_provenance와 review/source-revalidation.json에 연결된다.

이번 실행에서 기존 통합 5개, 마스터 24개, 차량 5개 검사(총34개)와 출처·역할 오류 거부 검사12개가 통과했다. 출발 후 바퀴 접지 오차는 최대0.0001003m다. 이는 기존 검사 재현이며 새 정밀 물리 검증을 했다는 의미가 아니다. 로그는 logs/source-revalidation.log와 logs/contracts.log다.

Notion 구간5 원문을 다시 조회한 결과 제공된 2026-10-01 수정본과 저장 텍스트가 같다. inputs/notion-s5-current.md에 보존했다. 외부 문서는 수정하지 않았다.

## 여섯 후보

| ID | 프레임 | 역할 | 기존 후보 처리 |
|---|---:|---|---|
| S5-01 | 672 | 부두 출발 | 유지 |
| S5-02 | 720 | 연결 도로 추적 | 유지 |
| S5-03 | 732 | 본격 선회 전 마당 접근 | 기존766에서 교체 |
| S5-03A | 766 | 실제 전진 선회·정렬 중 | 기존810에서 교체 |
| S5-04 | 842 | 정렬·정지, 문 개방 완료, 후진 전 | 유지 |
| S5-05 | 900 | 도크 접안·정지, 화물 내부, 창고로 시선 연결 | 유지 |

정지 상태인 f810을 선회 역할로 넣으면 검증에서 거부한다. 속도·선회 여부는 전후 프레임의 평가 상태로 판정하며 정지 스틸만으로 입증하지 않는다. 각 패널은 원본960×540 영역을 변경하지 않고 바깥에 테두리와 메모를 추가했다. 원본 픽셀과 패널 영상 영역의 바이트 일치를 6장 모두 확인했다.

## 표현과 선택 상태

사용자가 “6개 프레임과 선화 방향 채택”으로 f672·720·732·766·842·900과 흰 바탕·검은 윤곽을 선택했다. 실제 응답 출처는 review-decisions.json에 기록했다. 도구 실행 시간을 승인 시각으로 대체하지 않았다.

선택한 여섯 프레임 모두 별도 Blender 프로세스에서 EEVEE 흰 재질 오버라이드와 Freestyle 윤곽으로 새로 렌더했다. 새 선화 출처는 line-art-record.json이고, panels/에는 테두리와 하단 메모를 붙인6장이 있다. 손그림 상세 묘사를 추가하지 않았고 마스터의 재질·장면을 저장 변경하지 않았다.

6개 원본·선화 나란히 보기에서 운전석·차체 연결·컨테이너 후면·차륜·도로 경계·도크·창고 바닥의 위치와 비례를 대조했다. 표현에서 색과 그림자는 사라지고 가시 윤곽으로 대체된다. S5-04에서는 원본부터 후면 문과 도크 간격이 비스듬히 보여 자세한 상태가 약하게 읽히므로 실제 전후 동작과 함께 확인해야 한다. 이 가림을 새 선이나 가공한 자세로 보충하지 않았다. S5-05에서는 열린 후면·내부 화물·입고 바닥의 연결이 유지된다.

선화의 투영/원본 연결 검사는 9개를 추가했다. 미완료 출력, 다른 카메라/렌즈/Scene/해상도, 잘못된 부모 프레임, 누락 패널, 변경된 선택/이미지를 거부하는8개 실패를 먼저 확인한 뒤 구현하여9개 모두 통과했다. 최초 테스트 임시 디렉터리의 Windows 접근 오류는 작업 폴더 안에 테스트 임시 폴더를 두어 해결했고, 그 후의 의미 있는 RED와 GREEN 로그를 보존했다.

기존 S4-05 그림과 이 원본의 좌우 배치는 다르다. 이번 사용자의 명시적인 원본 선택에 따라 현재 Blender 구도를 콘티로 옮기며, 원본 카메라나 공간을 이전 그림에 맞추어 다시 변경하지 않는다. 그림과의 불일치를 해결했다고 주장하지 않는다.

T1 프레임·표현 선택은 완료되었다. 이번 결과의 여섯 완성 패널은 지시서 §6 T5에 따라 최종 사용자 검토 대기 상태다. 기술 검사 통과를 최종 연출 승인으로 바꾸지 않았다.

## AC 상태

| AC | 현재 판정 | 근거 |
|---|---|---|
| 1 기준·승인 구분 | 통과 | source.json, review-decisions.json, 실제 재개방·34개 검사 |
| 2 역할·시간 | 선택 완료·기술 검사 통과 | selection, 실제 상태, 사용자 선택 응답, 원본/영상 |
| 3 구조 일치 | 6장 원본·선화 구조 대조 완료 | 개별 comparison, 동일 투영, 패널 선화 영역 픽셀 보존 |
| 4 표현·가독성 | 선택한 표현으로6장 제작 | final-contact, 개별 패널. 최종 연출 검토 대기 |
| 5 최소 변경 | 통과 | 마스터 SHA 동일 |
| 6 원테이크 | 실제 원속도 재생 완료 | 325연속프레임/27.083333초, 재생 오류 없음, review/playback.json |
| 7 출처 동기화 | 최종 후보 동기화 검사 통과 | 원래 렌더 기록·새 선화 기록·manifest·final-validation |
| 8 재현·확정 | 재개방·재생 통과, 최종 확정 대기 | 프레임·표현 선택 기록 있음. 최종 묶음 승인은 아직 없음 |

## 재현

레포 루트 PowerShell에서 실행한다. 원본에는 저장하지 않으며 출력은 s5-sync-v002에 쓴다.

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe' --factory-startup -b 'F:/pnpline-landing/hero-section-video/blockout/s5-integration-v001/master-s5-integration-v001.blend' --python-exit-code 1 --python 'F:/pnpline-landing/hero-section-video/storyboard/s5-sync-v002/scripts/revalidate_source.py'
& 'C:/ProgramData/miniconda3/python.exe' -X utf8 'hero-section-video/storyboard/s5-sync-v001/tests/test_contracts.py'
& 'C:/ProgramData/miniconda3/python.exe' -X utf8 'hero-section-video/storyboard/s5-sync-v002/scripts/package_candidates.py'
```

재사용 패키저는 기존 s5-sync-v001 원본 렌더·기록·contracts.py를 명시적 의존성으로 사용하고, 출처/상태/파일 해시가 다르면 실패한다. 옛 자료가 없으면 임의로 대체하지 않는다. 기준 입력의 바이트 동일성 때문에 마스터 복사본을 새로 만들지 않고 원본 경로와 해시를 명시한다.

## 선화와 최종 묶음 재현

아래 명령은 새 run ID로 선화를 만들고 최종 후보 묶음을 패키징한다. 최종 승인된 버전에는 재실행하지 않고 새 출력 버전을 만들어야 한다.

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe' --factory-startup -b 'F:/pnpline-landing/hero-section-video/blockout/s5-integration-v001/master-s5-integration-v001.blend' --python-exit-code 1 --python 'F:/pnpline-landing/hero-section-video/storyboard/s5-sync-v002/scripts/render_line_art.py' -- --input 'F:/pnpline-landing/hero-section-video/blockout/s5-integration-v001/master-s5-integration-v001.blend' --scene PNPLINE_MASTER_v005 --camera CAM_MASTER --selection 'F:/pnpline-landing/hero-section-video/storyboard/s5-sync-v002/storyboard-selection.json' --raw-record 'F:/pnpline-landing/hero-section-video/storyboard/s5-sync-v001/render-record.json' --output 'F:/pnpline-landing/hero-section-video/storyboard/s5-sync-v002'
& 'C:/ProgramData/miniconda3/python.exe' -X utf8 'hero-section-video/storyboard/s5-sync-v002/scripts/test_lineage.py'
& 'C:/ProgramData/miniconda3/python.exe' -X utf8 'hero-section-video/storyboard/s5-sync-v002/scripts/package_final.py'
& 'C:/ProgramData/miniconda3/python.exe' -X utf8 'hero-section-video/storyboard/s5-sync-v002/scripts/verify_final.py'
```

Freestyle은 일부 겹친 가시 에지에 대해 “appears twice, correcting” 경고를 남겼다. 렌더는 정상 종료되었고6장을 직접 대조했으며 메시를 수정·저장하지 않았다. 이전 선화 시험 run은 참고 기록으로 보존하고 현재 line-art-record.json이 지정하는 run만 최종 후보에 사용한다.

## 독립 최종 검토

새 컨텍스트의 gpt-6-astra/high 읽기 전용 검토에서 현재 산출물의 Critical/Important 지적은 없었다. 리뷰어는 검증 로직과 추가 출처 해시를 독립 확인했고, 원본/선화 대조도 확인했다. Blender 검사·실제 재생은 이번 작업의 실행 기록을 검토했으며 리뷰어가 반복 실행한 것은 아니다.

보류한 경미한 개선2건: (1) verify_final.py 한 명령에 선택 시간과 모든 의존 해시 검사를 추가하면 향후 재검증이 더 완결적이다. 현재 값은 독립 검토에서 별도 확인되어 모두 일치했다. (2) package_final.py를 반복 실행하면 HTML 대조 링크가 중복된다. 현재 제출 페이지에는 중복이 없다. 재실행 시점의 도구 개선으로 남겼다.

사용자 최종 연출 판단, S5-04의 가려진 문 상태를 스틸만으로 입증하는 일, 새 정밀 물리 검증, 별도 full-layout 마스터 적합성은 이번 기술 완료 판정에 포함하지 않는다. 선택된 기준과 프레임을 유지했으므로 이 결과가 다른 마스터 구도와 같다고 주장하지 않는다. 두 Ruling(동일 출처 재사용, 별도 출력 폴더) 및 검토 경계 판단은 progress.md에 남겼다. 재사용 결과는 기존 원본 기록에 의존하고 별도 Git 브랜치가 아닌 같은 작업트리의 전용 폴더로 격리했다.

최종 판정: **최종 동기화 검사 통과 — 사용자 최종 승인 대기**. 현재 최종 패널6장과 manifest 해시에 대한 사용자 응답이 있어야 콘티 확정 상태로 기록한다.

## 프리뷰 속도 조정

사용자는 “프리뷰 재생만 빠르게”를 선택했다. 동일한 f624–948의325프레임을 24fps로 재인코딩한 2배속 검토 영상(`preview/main-2x.mp4`)을 추가했다. 길이는13.541667초이며 누락 프레임이 없다. 검토 페이지에서 2배속·1.5배속·원속도를 선택할 수 있다. 원본 12fps 영상, Blender 키프레임·동작, 선택된 여섯 프레임과 manifest의 원속도 시간은 그대로다. 재생만 빠른 영상의 시각은 `(master_frame-624)/24`로 환산한다. 증거는 `preview/quick-video-record.json`과 브라우저 재생 기록을 따른다.

출처 추가 확인: 현재 기준 경로의 저장본 SHA는 `cc2dec40e69d97064710e3397598925f700d8dfda61ff2a3cd031995fe2514b5`로 바뀌었고 저장 프레임은 907에서 521로 바뀌었다. 검토 영상은 SHA `8c76f0e184bc742309cf66dcf9f3f5fa7072e02b54b58e6985a91ff1ae57b665`의 보존 사본에서 출력되었다. Blender에서 전체 S5 프리뷰 f624–948의 325프레임에 대해 카메라·렌즈·304객체 월드 행렬 및 메시 형상을 직접 대조했으며 차이가 없었다. 따라서 이 구간의 영상 내용은 현재 저장본과 같다. 두 파일의 경로와 해시, 검증 항목은 `review/current-master-comparison.json`에 기록했다.
