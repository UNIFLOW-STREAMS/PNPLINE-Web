from pathlib import Path
import json,hashlib
B=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
review={'reviewer':'/root/s5_storyboard_v002_final_review','model':'gpt-6-astra','reasoning_effort':'high','mode':'fresh-context read-only','verdict':'Ready as final synchronization candidate; final user artistic approval pending','critical':[],'important':[],'minor_deferred':[{'file':'scripts/verify_final.py','finding':'Final verification command could also call validate_selection and recheck all provenance dependency hashes. Current values independently checked and match.','impact':'Future verification completeness; no current artifact mismatch.'},{'file':'scripts/package_final.py','finding':'Repeated package runs append duplicate HTML comparison links. Current page has no duplicate.','impact':'Repeat-run presentation polish.'}],'review_checks':['Read-only final verification logic rerun;325raws and6line-art/panels pass','Additional selection timing and render/script/source-revalidation hashes checked','Actual source8c76f0e1 matches; existing git dirty state predates this task','Contact sheet and04/05comparisons preserve structure;04visibility limitation accurately disclosed'],'not_reexecuted':['Blender regressions','browser playback'],'declined_to_judge':['final artistic approval','hidden doors solely from stills','new precise physics','full-layout-master suitability outside selected baseline'],'manifest_sha256':sha(B/'storyboard-manifest.json')}
save(B/'review/final-review.json',review)
with (B/'progress.md').open('a',encoding='utf-8') as f:
 f.write('''
Final review: fresh gpt-6-astra/high reviewer found no Critical/Important current-output issue. Independently rechecked all current provenance hashes and validation logic read-only.
Final: minor (deferred): verify_final.py can strengthen future-run completeness by invoking validate_selection and all dependency checks already independently verified for this bundle.
Final: minor (deferred): package_final.py repeat execution duplicates HTML comparison links; current page is unaffected.
Final: Ruling: Final artistic judgment remains the user's T5 decision — technical tests cannot grant it — cost if wrong: final adoption remains pending.
Final: Ruling: Do not infer hidden door visibility from the S5-04 still; rely on actual neighbor motion and existing door tests for state — user selected this frame and camera remains unchanged — cost if wrong: still-only door readability remains limited.
Final: Ruling: No new precise physics claim — the plan calls for existing regression reproduction with an unmodified master — cost if wrong: behavior beyond those tested conditions remains unverified.
Final: Ruling: full-layout-master suitability is outside this task — user explicitly selected s5-integration-v001 — cost if wrong: these boards will not match the separately integrated layout master.
T4 technical synchronization passed. T5 exact final package awaiting actual user approval; do not overwrite approved panel files.
''')
with (B/'report.md').open('a',encoding='utf-8') as f:
 f.write('''
## 독립 최종 검토

새 컨텍스트의 gpt-6-astra/high 읽기 전용 검토에서 현재 산출물의 Critical/Important 지적은 없었다. 리뷰어는 검증 로직과 추가 출처 해시를 독립 확인했고, 원본/선화 대조도 확인했다. Blender 검사·실제 재생은 이번 작업의 실행 기록을 검토했으며 리뷰어가 반복 실행한 것은 아니다.

보류한 경미한 개선2건: (1) verify_final.py 한 명령에 선택 시간과 모든 의존 해시 검사를 추가하면 향후 재검증이 더 완결적이다. 현재 값은 독립 검토에서 별도 확인되어 모두 일치했다. (2) package_final.py를 반복 실행하면 HTML 대조 링크가 중복된다. 현재 제출 페이지에는 중복이 없다. 재실행 시점의 도구 개선으로 남겼다.

사용자 최종 연출 판단, S5-04의 가려진 문 상태를 스틸만으로 입증하는 일, 새 정밀 물리 검증, 별도 full-layout 마스터 적합성은 이번 기술 완료 판정에 포함하지 않는다. 선택된 기준과 프레임을 유지했으므로 이 결과가 다른 마스터 구도와 같다고 주장하지 않는다. 두 Ruling(동일 출처 재사용, 별도 출력 폴더) 및 검토 경계 판단은 progress.md에 남겼다. 재사용 결과는 기존 원본 기록에 의존하고 별도 Git 브랜치가 아닌 같은 작업트리의 전용 폴더로 격리했다.

최종 판정: **최종 동기화 검사 통과 — 사용자 최종 승인 대기**. 현재 최종 패널6장과 manifest 해시에 대한 사용자 응답이 있어야 콘티 확정 상태로 기록한다.
''')
paths=[p for p in B.rglob('*') if p.is_file() and p.suffix not in ['.pyc','.log'] and '__pycache__' not in p.parts and p.name!='hashes.json']
save(B/'hashes.json',{str(p.relative_to(B)).replace('\\','/'):sha(p) for p in paths})
print('SEALED',len(paths),'files; manifest',sha(B/'storyboard-manifest.json'))
