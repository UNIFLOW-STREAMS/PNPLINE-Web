# 최종 읽기 전용 검토

검토자: GPT-6 Astra/high, fresh context, 1회. 구현/파일 쓰기/추가 에이전트 없음.

검토 시 판정: 재작업 필요 — Important1건, Critical0건, 미해결 Minor0건.

Important: 기존 isolate_scene.py의 외부 Scene 검사는 Object/Data/Action만 보므로, 원본 observer.parent가 테스트 객체를 참조하는 경우 재실행 삭제에서 부모가 None으로 바뀐다. constraint/modifier/driver 타깃을 포함한 모든 외부 ID 사용자를 삭제 전에 거부해야 한다. 검토자는 별도 메모리 fixture에서 재현했고 파일은 저장하지 않았다.

부모 에이전트의 수정: parent, constraint, modifier, driver 네 외부 참조 fixture 모두 RED(4failures,0errors)를 확인했다. bpy.data.user_map으로 삭제 대상 테스트 ID의 모든 외부 사용자를 변경 전에 거부하도록 보완했다. 결과와 전체 관련 검사 종료 코드는 check-runs.json에 있다. 추가 리뷰 라운드 없이 부모 에이전트가 이 한 차례의 수정과 검증을 판정한다. 제출 blend의 시각/동작은 바뀌지 않았다.

검토 확인: 원본/후보 해시, 원본304객체·1393프레임, 기존24회귀 검사, 재생성 의미·개수 동일,1009개 동작 표본,2,177,422충돌 쌍, 재개방RGB16쌍/S1 RGB3쌍, 253프레임 정상속도 영상2개(드롭0), f890 열린 후면/도크/입고 바닥의 시각 관계.

검증 한계: saved-motion validator 하나가 문 개방 완료각, 후진 중 완전한 방향 고정, 모든 화물 유지 조건을 각각 독립 assertion으로 다루지는 않는다. 해당 조건은 보존/복사된 원본 Action, 재생성 동일성, 저장된 상태와 직접 확인한 이미지·영상으로 함께 뒷받침한다. validator 하나만으로 전체 AC를 증명했다고 주장하지 않는다.

검토자가 대신 승인하지 않은 판단: ① 원본f720→테스트f648 진입 범위 ② 문·경첩·tandem·bridge 보정의 최종 자산 적용 ③ bridge0.08m 지정 겹침/바닥0.06m 단차 허용 ④ 단일 도크와 사선 구도의 시각적 충분성 ⑤ S5/S6 마스터 통합. 부모 에이전트의 각 Ruling은 progress.md에 있다.

Minor 문구: 원본 bridge0.06m와 보정 후0.08m의 구분을 검토 중 고쳤으며 미해결 항목으로 남지 않았다.
