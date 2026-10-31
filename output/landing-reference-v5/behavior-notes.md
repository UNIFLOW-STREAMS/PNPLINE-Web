# V5 인터랙션 구현 기록

## 구현 범위

- main.js는 정적 HTML용 독립 스크립트이며 개인정보 페이지에서 히어로·폼이 없어도 동작한다.
- 영상은 data-src에서 정상 모드·히어로 진입 시에만 src를 설정한다. 초기 OS 모션 감소에서는 동영상 네트워크 요청을 시작하지 않는다.
- IntersectionObserver와 화면 안에서만 실행하는 requestAnimationFrame으로 스크롤 진행도를 읽는다. 직접 scroll 이벤트 리스너는 없다.
- 진행도에 현재 파일의 duration을 대응시켜 currentTime을 갱신한다. 진행도의 시작은 sticky pin의 계산된 top(고정 헤더 높이)이며, `(stickyTop - journeyRect.top) / (journeyHeight - pinHeight)`로 계산한다. 정방향·역방향 모두 같은 매핑이며 video는 항상 paused 상태다.
- 시킹 중 최신 목표 시점만 남기고 seeked 후 적용한다. 스크롤 정지 후 목표 프레임에 도달하면 같은 시점에 머문다.
- 메타데이터·초기 데이터 15초, 시킹 정체 8초 또는 실제 video error에서 정지 이미지·일반 콘텐츠 모드로 전환한다.
- body.is-reduced는 OS/사용자 감소 설정, 미디어 실패 또는 화면 높이·내용 크기의 정적 레이아웃 상태, body.media-failed는 실제 미디어 실패, body.media-ready는 표시할 프레임이 준비된 상태다.
- body.dataset.motionMode 및 journey.dataset.progress, video.dataset.targetTime은 실제 DOM 상태 확인용으로 기록한다.
- footer의 #reduce-motion은 사용자의 추가 감소 요청이다. OS 감소 설정은 우선하며 해당 상태에서는 체크박스를 checked·disabled 처리한다. 설정과 개인정보 입력을 storage에 저장하지 않는다.
- 화면 높이 540px 이하 또는 hero-content의 자연 높이가 viewport에서 헤더를 뺀 높이를 초과하면 data-motion-mode=static으로 전환한다. 원인은 data-motion-reason=compact-height 또는 content-overflow로 구분한다. 이 경우에도 body.is-reduced를 사용해 긴 구간과 sticky를 해제하고 동영상 소스를 제거한다. 사용자 체크박스는 실제 OS/사용자 선택만 반영한다.
- ResizeObserver, viewport resize, 높이 media query 변화, 폰트 로드 후 내용 크기를 다시 검사한다. 공간이 확보되면 정상 스크롤 모드로 복귀한다.
- 같은 페이지 앵커는 즉시 목적지로 이동하고 포커스를 옮긴다. 헤더 간격은 CSS의 scroll-margin에 따른다.
- 모바일 메뉴는 hidden/aria-expanded를 함께 갱신하며 Escape·바깥 클릭·다른 곳으로 포커스 이동·데스크톱 전환에서 닫힌다.
- 폼은 submit을 항상 막고 버튼도 preview 동작만 한다. 비어 있지 않은 잘못된 이메일과 동의 누락을 알린다. 필수 항목 정의는 임의로 확장하지 않았다. 결과는 ‘设计预览：信息未发送。’이며 접수 성공을 주장하지 않는다.

## 확인과 주의점

- node --check를 실행해 문법을 확인한다. 실제 브라우저 확인은 부모 에이전트가 담당한다.
- 작은 화면에서 hero-pin이 여정보다 커지지 않도록 CSS와 함께 검증해야 한다. 모션 감소에서는 긴 여정 높이와 sticky를 모두 해제해야 한다.
- 미디어 ready 클래스는 현재 목표 프레임이 준비된 경우에만 켜므로 초기 포스터와 영상의 급격한 전환을 줄인다. 포스터 첫 프레임 추출은 부모 에이전트의 자산 작업이다.
- 모션 감소를 footer에서 바꿀 때 체크박스의 화면 위치를 유지하도록 레이아웃 전후 차이를 보정한다. 실제 OS 설정 전환에서는 브라우저의 일반 스크롤 앵커 동작을 따른다.
- 영상 또는 JS가 실패해도 본문·실제 앵커는 HTML에 남는다. type=button과 method=dialog는 JS 실패 시 폼의 임의 외부 전송도 방지한다.
