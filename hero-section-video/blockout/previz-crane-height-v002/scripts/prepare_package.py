from pathlib import Path
R=Path(__file__).resolve().parents[1]
src=(R.parent/'previz-crane-height-v001/scripts/package_review.py').read_text(encoding='utf-8')
src=src.replace('previz-crane-height-v001','previz-crane-height-v002')
src=src.replace('크레인 높이·내부 화물 수정','첫 프레임 인양 줄 길이 수정')
src=src.replace('크레인 상부 <b>+3m</b> · 컨테이너 시작 높이 <b>+2.5m</b> · 기존 f72 안착 시점 유지.<br>초록색 상자는 컨테이너 내부 화물입니다. 하강하는 동안 내부 위치를 유지하도록 수정했습니다.','첫 프레임의 줄 길이 <b>70cm → 20cm</b> · 컨테이너 시작점 <b>50cm 추가 상승</b>.<br>카메라와 크레인 높이는 그대로입니다. 컨테이너가 크레인에 더 가까이 붙은 상태에서 출발하며 기존 f72 안착으로 이어집니다.')
src=src.replace('내부 화물·크레인 간섭·지지부 접지·안착 이후 동작 보존','줄 연결·인양 장치 간섭·내부 화물·카메라 및 안착 이후 동작 보존')
(R/'scripts/package_review.py').write_text(src,encoding='utf-8')
