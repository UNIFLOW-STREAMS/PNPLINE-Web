# 확인 근거와 확인 범위

확인일: 2026-10-28. 아래는 지시서 작성 시의 읽기 전용 확인 기록이다.

## 레포

원격 main HEAD: `74f1b91ede4656041cf78f9882a1f98d9f190145`.
연결된 GitHub 도구로 다음을 읽었다. 실제 .blend를 열거나 검사를 재실행한 것은 아니다.

- `hero-section-video/blockout/cn-city-proxy-v001/report.md`: 현재 프록시 파일·해시·시간축, 도시 크롭 실패, 기존 검증 및 한계.
- `hero-section-video/blockout/cn-city-proxy-v001/scripts/preservation.py`: 전체 카메라 불변 및 STEP 1 추가 목록을 전제로 하는 보존 계약.
- `hero-section-video/blockout/cn-city-proxy-v001/scripts/render.py`: CAM_MASTER/진단 카메라 분리, 지원 인자와 end 제외 범위.
- `hero-section-video/blockout/cn-city-proxy-v001/tests/test_proxy.py`: 고정 도시·유일 ID·형상/지지·데이터 격리 검사.
- `hero-section-video/blockout/blockout-master-v004/scripts/revise_s2.py`: 위치/타깃 경로와 Quaternion 키 베이크, 과거 원본 의존.
- `hero-section-video/blockout/blockout-master-v005/report-s3-camera.md`: 후속 S3 수정 범위와 경계 상태.

레포 기준 주소:
`https://github.com/UNIFLOW-STREAMS/PNPLINE-Web/tree/74f1b91ede4656041cf78f9882a1f98d9f190145`

## 외부 확인 — 모델/설정만

OpenAI 공식 검색 결과에서 GPT-6 Astra와 High/xhigh 지원, Codex 계정별 가용성 차이를 확인했다. 모델 선택은 이번 작업에 대한 권고이며 사용자 계정·실제 런타임은 확인하지 않았다.

`https://developers.openai.com/api/docs/models/gpt-6-astra`
`https://help.openai.com/en/articles/20001516-managing-usage-with-gpt-6-astra-in-work-and-codex`
`https://openai.com/index/practical-guide-building-gpt-6/`

## 입력 이미지

사용자가 이번 대화에 제공한 중국 도시·항구 이미지 원본을 복사했다. 해시·크기는 manifest.json 참조.
이전 제외 항목인 CHINA 추가는 이번 사용자 요청이다. 장식 구름·미국 도시·선박 대형 로고 등의 신규 제작으로 확대하지 않는다.

## 수행하지 않은 것

레포 수정, 커밋/push/PR, Blender 장면 편집, 영상 생성, 테스트·렌더·실제 재생 검증은 수행하지 않았다.
