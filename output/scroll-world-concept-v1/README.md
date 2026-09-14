# #61 브랜드 강조형 산업 미니어처 콘셉트

현재 검토 페이지는 지리·카메라·미니어처 표현을 수정한 V2다. 변경 근거와 재현 방법은 [V2 기록](continuity-v2/README.md)을 참고한다. 기존 키프레임·데이터는 V1 기록으로 유지하며, 수정 전 페이지는 ko-v1.html, index-v1.html이다. 현재 버전 검사는 node output/scroll-world-concept-v1/continuity-v2/qa.cjs로 실행한다.

상태와 실제 제작 수량은 `data/assets.json`, 검증 결과는 `qa/validation.md`에 기록한다. 미술 방향 승인과 개별 이미지의 시각 승인은 별개다. 공개 배포용 패키지가 아니다.

## 검토 페이지

저장소 루트 `F:/pnpline-landing`에서 다음 명령을 실행한다.

```powershell
python -m http.server 8761 --bind 127.0.0.1
```

브라우저에서 중국어 페이지는 `http://127.0.0.1:8761/output/scroll-world-concept-v1/`, 한국어 페이지는 `http://127.0.0.1:8761/output/scroll-world-concept-v1/ko.html`을 연다. 두 페이지의 머리말에서도 언어를 전환할 수 있다. HTML을 file URL로 직접 열면 JSON fetch가 제한될 수 있다.

무드보드 → 3안 비교 → 공식 로고 대비 → 데스크톱/모바일 6장면 → 안전 영역 → animatic → 인계 기준 순서다. 6장면은 일반 문서 흐름으로도 모두 읽을 수 있다. animatic은 키보드 방향키·Home·End로 조작하는 기본 range 입력이다. 휠이나 터치를 가로채지 않는다.

## 파일과 재현

- `base-scenes/`: 실제 생성 원본. 생성 도구가 반환한 원본 크기를 보존한다.
- `keyframes/`: 공식 로고를 원본에서 합성한 최종 정지 이미지. UI 문구를 굽지 않는다.
- `styleframes/`: A/B/C 비교 이미지. A는 데스크톱 S01과 재사용 관계다.
- `masks/`: 이미지와 프리뷰가 공유하는 정규화 JSON, 대응 SVG.
- `data/`: 출처·자산·합성좌표·스토리보드·타임라인.
- `prompts/execution-*.json`: 실제 생성 호출과 노출된 도구 정보. 모델·비용·seed 미노출은 추측하지 않는다.
- `scripts/composite.py`: 실제 합성좌표를 사용해 공식 로고를 다시 적용한다. 기존 Python Pillow/NumPy만 사용한다.
- `qa/`: 자동 검사·실제 브라우저 화면·시각적 한계와 파일럿 기준.

원본 입력은 `docs/plan/issue-61-brand-miniature/references/`에서 읽으며 수정하지 않는다. 공개 재배포 권한은 확인되지 않았으므로 원본을 새 output 폴더에 복제하지 않는다. 토큰은 `output/design-concept-v1/design-tokens.css`를 참조한다.

30초 animatic, 검토 해상도와 마스크 좌표는 concept-review/preview-only이다. 실제 영상 생성·시킹 성능·코덱·대역폭·제작비·3D 연속성 검증이 아니다. #24의 S01+S02 2장면 파일럿 이후 #62에서 실제 전달 계약을 정한다. #42 서비스 통합은 포함하지 않는다.

## 검사 재실행

로컬 서버를 실행한 상태에서 저장소 루트에서 실행한다. 기존 설치 경로가 다른 컴퓨터에서는 browser-qa.cjs의 Playwright/Chrome 경로를 해당 환경에 맞게 지정한다.

```powershell
python output/scroll-world-concept-v1/scripts/composite.py
python output/scroll-world-concept-v1/scripts/contact-sheet.py
python output/scroll-world-concept-v1/scripts/validate.py
node output/scroll-world-concept-v1/scripts/browser-qa.cjs
python output/scroll-world-concept-v1/scripts/final-report.py
```

`build-package.py`는 초안 설계와 기본 마스크를 만드는 스크립트이다. 실제 최종 좌표는 logo-placements.json에 있으므로 기본 설계를 다시 만든 경우 반드시 composite.py로 실제 마스크를 다시 적용한다. 모든 경로는 현재 저장소 내 로컬 검토용이며 공개 업로드 명령이 아니다.
