# 작성 근거와 확인 한계

## 사용자 제공 기준

사용자가 이번 대화에서 제시한 5단계 제작안 중 STEP 1과, 다음 최종 완료 조건을 보존했다.

> S2에서 선박이 중국 항구를 출항하는 동안 중국을 상징하는 미니어처 도시가 충분히 드러나고, 카메라가 그 공간을 떠나 S3의 구형 지구 항해로 끊김 없이 이어지는가?

이번 첨부 이미지는 건축 형상 참고이며 정확한 실측 공간·최종 배치·운영 사실을 증명하지 않는다. 이전 답변에 끼어든 외부 검색 이미지는 입력으로 채택하지 않았다.

## 레포 확인

2026-10-28 연결된 GitHub에서 읽기 전용으로 조회했다.

```text
Repository: https://github.com/UNIFLOW-STREAMS/PNPLINE-Web
main: 4993e2f5ce299e7e119eb7b57a4098d7922a7c1f
CONTEXT.md
docs/wayfinder/design-system-v1.md
hero-section-video/blockout/s5-integration-v001/README.md
hero-section-video/blockout/previz-s1-s7-2x-v001/render-record.json
hero-section-video/blockout/blockout-master-v004/report-s2-camera.md
hero-section-video/blockout/blockout-master-v005/report-s3-camera.md
hero-section-video/blockout/blockout-master-v001/scripts/build_master.py
hero-section-video/blockout/s5-integration-v001/tests/master_regression.py
hero-section-video/blockout/s5-integration-v001/scripts/check_preservation.py
hero-section-video/blockout/s5-integration-v001/scripts/render_review.py
```

확인한 것은 해당 파일의 관련 본문·코드·기록이다. 이 환경에서 .blend를 직접 열어 지오메트리나 타임라인을 재실행한 것은 아니다. 로컬 미저장·미커밋 변경과 실제 작업 환경의 도구 가용성은 미확인이다.

구체적인 보완점:
- S2 v004 후 S3 수정 이력이 존재하므로 v004 단독본으로 되돌리지 않는다.
- 통합 렌더 기록은 S5 통합 .blend와 원래 12fps 시간축을 지목한다.
- v001 생성 코드의 지형은 평면 작업대+구면 연결 해안이다. 현재 통합본에서 재확인하며 부두까지 임의로 구면 변형하지 않는다.
- 기존 S5 보존 스크립트는 신규 프록시 추가 비교용으로 그대로 사용할 수 없다.
- 기존 렌더 스크립트의 --top은 US_FRAME 기준이다.

## 공식 모델 자료 — 외부 확인

아래 공식 자료에서 모델 ID·지원 노력 단계·Codex에서의 사용 설명을 확인했다. Astra/High 권고 자체는 이번 3D 공간·보존 검증 작업에 대한 작업 설계 판단이다. 일반적인 성능 보장이나 사용자의 계정 가용성 확인을 뜻하지 않는다.

```text
https://developers.openai.com/api/docs/models/gpt-6-astra
https://learn.chatgpt.com/docs/models
https://developers.openai.com/api/docs/guides/reasoning
https://developers.openai.com/blog/architectural-visualization-with-astra
```

스킬은 ChatGPT 환경의 설치 카탈로그와 관련 지침을 확인했다. Codex 환경에 동일하게 설치돼 있다고 가정하지 않는다. Blender 전용 스킬은 확인되지 않았다.
