from pathlib import Path
import json
B=Path(__file__).resolve().parents[1]
p=B/'report.md';t=p.read_text(encoding='utf-8')
t=t.replace('# S5 스토리보드 동기화 v002 — 구조 후보','# S5 스토리보드 동기화 v002 — 최종 동기화 후보')
a=t.index('현재 결과는 컬러 원본 기반');b=t.index('기존 S4-05 그림',a)
t=t[:a]+'''사용자가 “6개 프레임과 선화 방향 채택”으로 f672·720·732·766·842·900과 흰 바탕·검은 윤곽을 선택했다. 실제 응답 출처는 review-decisions.json에 기록했다. 도구 실행 시간을 승인 시각으로 대체하지 않았다.

선택한 여섯 프레임 모두 별도 Blender 프로세스에서 EEVEE 흰 재질 오버라이드와 Freestyle 윤곽으로 새로 렌더했다. 새 선화 출처는 line-art-record.json이고, panels/에는 테두리와 하단 메모를 붙인6장이 있다. 손그림 상세 묘사를 추가하지 않았고 마스터의 재질·장면을 저장 변경하지 않았다.

6개 원본·선화 나란히 보기에서 운전석·차체 연결·컨테이너 후면·차륜·도로 경계·도크·창고 바닥의 위치와 비례를 대조했다. 표현에서 색과 그림자는 사라지고 가시 윤곽으로 대체된다. S5-04에서는 원본부터 후면 문과 도크 간격이 비스듬히 보여 자세한 상태가 약하게 읽히므로 실제 전후 동작과 함께 확인해야 한다. 이 가림을 새 선이나 가공한 자세로 보충하지 않았다. S5-05에서는 열린 후면·내부 화물·입고 바닥의 연결이 유지된다.

선화의 투영/원본 연결 검사는 9개를 추가했다. 미완료 출력, 다른 카메라/렌즈/Scene/해상도, 잘못된 부모 프레임, 누락 패널, 변경된 선택/이미지를 거부하는8개 실패를 먼저 확인한 뒤 구현하여9개 모두 통과했다. 최초 테스트 임시 디렉터리의 Windows 접근 오류는 작업 폴더 안에 테스트 임시 폴더를 두어 해결했고, 그 후의 의미 있는 RED와 GREEN 로그를 보존했다.

''' +t[b:]
a=t.index('지시서 §6 T1의');b=t.index('## AC 상태',a)
t=t[:a]+'''T1 프레임·표현 선택은 완료되었다. 이번 결과의 여섯 완성 패널은 지시서 §6 T5에 따라 최종 사용자 검토 대기 상태다. 기술 검사 통과를 최종 연출 승인으로 바꾸지 않았다.

'''+t[b:]
t=t.replace('후보 기술 검사 통과 | selection, 실제 상태, 원본/영상. 사용자 선택 대기','선택 완료·기술 검사 통과 | selection, 실제 상태, 사용자 선택 응답, 원본/영상')
t=t.replace('원본 초안6장·선화 샘플1장 확인 | 픽셀 보존 검사, style-comparison. 최종6장 미제작','6장 원본·선화 구조 대조 완료 | 개별 comparison, 동일 투영, 패널 선화 영역 픽셀 보존')
t=t.replace('샘플 검토 대기 | Freestyle1장. 전체 선화 완료 아님','선택한 표현으로6장 제작 | final-contact, 개별 패널. 최종 연출 검토 대기')
t=t.replace('동일 CAM_MASTER의325연속프레임 | 실제 재생 결과는 review/playback.json에 추가','실제 원속도 재생 완료 | 325연속프레임/27.083333초, 재생 오류 없음, review/playback.json')
t=t.replace('구조 후보 묶음 검사 통과 | 원래 렌더 기록·재사용 검증·manifest. 최종 선화 묶음 대기','최종 후보 동기화 검사 통과 | 원래 렌더 기록·새 선화 기록·manifest·final-validation')
t=t.replace('재개방 통과, 최종 확정 대기 | 선택·최종 승인 기록 없음','재개방·재생 통과, 최종 확정 대기 | 프레임·표현 선택 기록 있음. 최종 묶음 승인은 아직 없음')
t+='''
## 선화와 최종 묶음 재현

아래 명령은 새 run ID로 선화를 만들고 최종 후보 묶음을 패키징한다. 최종 승인된 버전에는 재실행하지 않고 새 출력 버전을 만들어야 한다.

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe' --factory-startup -b 'F:/pnpline-landing/hero-section-video/blockout/s5-integration-v001/master-s5-integration-v001.blend' --python-exit-code 1 --python 'F:/pnpline-landing/hero-section-video/storyboard/s5-sync-v002/scripts/render_line_art.py' -- --input 'F:/pnpline-landing/hero-section-video/blockout/s5-integration-v001/master-s5-integration-v001.blend' --scene PNPLINE_MASTER_v005 --camera CAM_MASTER --selection 'F:/pnpline-landing/hero-section-video/storyboard/s5-sync-v002/storyboard-selection.json' --raw-record 'F:/pnpline-landing/hero-section-video/storyboard/s5-sync-v001/render-record.json' --output 'F:/pnpline-landing/hero-section-video/storyboard/s5-sync-v002'
& 'C:/ProgramData/miniconda3/python.exe' -X utf8 'hero-section-video/storyboard/s5-sync-v002/scripts/test_lineage.py'
& 'C:/ProgramData/miniconda3/python.exe' -X utf8 'hero-section-video/storyboard/s5-sync-v002/scripts/package_final.py'
& 'C:/ProgramData/miniconda3/python.exe' -X utf8 'hero-section-video/storyboard/s5-sync-v002/scripts/verify_final.py'
```

Freestyle은 일부 겹친 가시 에지에 대해 “appears twice, correcting” 경고를 남겼다. 렌더는 정상 종료되었고6장을 직접 대조했으며 메시를 수정·저장하지 않았다. 이전 선화 시험 run은 참고 기록으로 보존하고 현재 line-art-record.json이 지정하는 run만 최종 후보에 사용한다.
'''
p.write_text(t,encoding='utf-8')
(B/'README.md').write_text('''# S5 스토리보드 동기화 v002

기준: `F:/pnpline-landing/hero-section-video/blockout/s5-integration-v001/master-s5-integration-v001.blend` (SHA256 8c76f0e184bc742309cf66dcf9f3f5fa7072e02b54b58e6985a91ff1ae57b665). 마스터 무수정.

- [검토 페이지](http://127.0.0.1:8769/review.html): 개별6장, 원본 대조, 연속 영상.
- [전체 흑백 콘티](review/final-contact.png)
- [6장 원본·선화 대조](review/structure-comparison.png)
- [원속도 연속 영상](preview/main.mp4)
- [검증 보고서·재현 명령](report.md)

사용자가 프레임6개와 표현 방향을 선택했고, 해당 프레임으로 흑백 콘티6장을 제작했다. 단계: **최종 동기화 검사 통과 — 사용자 최종 승인 대기**.

원본 스틸·영상은 s5-sync-v001의 동일 출처 자료를 전체 해시와 새 평가 상태 검사 후 재사용했다. 선화6장은 새로 렌더했다. line-art-record.json과 storyboard-manifest.json이 현재 후보를 지정한다. 이전 draft 패널·선화 시험 run은 과거 검토 자료다.
''',encoding='utf-8')
with (B/'progress.md').open('a',encoding='utf-8') as f:f.write('\nT2/T4 technical complete: six selected frames freshly rendered as Freestyle in separate Blender process; full source unchanged. Expression lineage8 RED failures ->9/9 GREEN. All6 raw/line-art comparisons visually inspected, all6 same camera projections and all6 expression-to-panel regions verified. Playback27.083333s at1x complete. Final user approval remains separate. Freestyle duplicate-visible-edge warnings auto-corrected by renderer; inspected output retained. Final read-only review next.\n')
visual={'source_sha256':'8c76f0e184bc742309cf66dcf9f3f5fa7072e02b54b58e6985a91ff1ae57b665','method':'Six individually opened side-by-side source and expression images, equal image regions. No pixel-identical claim across different render styles.','panels':{k:{'reviewed':['cab/trailer/container silhouette','visible wheel placement','road and floor boundaries','visible warehouse/dock elements','door state where visible'],'structure_preserved':True} for k in ['S5-01','S5-02','S5-03','S5-03A','S5-04','S5-05']},'limitations':['White contours omit source color and shadows.','S5-04 rear doors/dock gap are oblique and partially hidden in both source and expression; state also established with actual neighbor motion/geometry.','Original S4-05 drawing spatial left/right differs from selected s5-integration source; no new master-layout claim.'],'final_artistic_approval':None}
(B/'review/structure-visual-review.json').write_text(json.dumps(visual,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
