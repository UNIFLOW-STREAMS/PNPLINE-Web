from pathlib import Path
import subprocess,json,hashlib
R=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
record=json.loads((R/'render-record.json').read_text());assert record['status']=='complete'
assert sha(record['source'])==record['source_sha256'] and sha(record['output'])==record['blend_sha256']
for item in record['images']:assert sha(R/'frames'/f"{item['frame']:04d}.png")==item['sha256']
out=R/'previz-s1-s7-3p5x-v001.mp4'
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-framerate','42','-start_number','0','-i',str(R/'frames/%04d.png'),'-frames:v','1393','-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(out)],check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(out)]))
v=probe['streams'][0];assert int(v['nb_read_frames'])==1393 and v['r_frame_rate']=='42/1' and v['width']==960 and v['height']==540
assert abs(float(probe['format']['duration'])-1393/42)<.002
subprocess.run(['ffmpeg','-v','error','-i',str(out),'-f','null','-'],check=True)
record.update(video_path=str(out),video_sha256=sha(out),video_frame_count=1393,video_duration=float(probe['format']['duration']),video_fps=42,full_decode='PASS',encoder_script_sha256=sha(__file__))
(R/'render-record.json').write_text(json.dumps(record,indent=2),encoding='utf8');(R/'ffprobe.json').write_text(json.dumps(probe,indent=2),encoding='utf8')
(R/'README.md').write_text('''# PNPLINE S1–S7 3.5배속 프리비즈

검증된 모션 폴리싱 A 기준. 원본12fps 대비3.5배속이며, A24fps 영상 대비1.75배속입니다.
42fps /1,393프레임 /33.166667초 /960×540. 모든 프레임을 새로 렌더링했습니다.

- master-previz-s1-s7-3p5x-v001.blend: 별도 편집 가능한 Blender 파일
- previz-s1-s7-3p5x-v001.mp4: 전체 S1–S7 영상
- time-map-3p5x.json: 원본 프레임과 새 출력 시간 대응
- render-record.json: 원본·출력·스크립트·PNG·MP4 해시 및 검증

원본 A를 수정하지 않았습니다. 독립 재개방 후 전체1,393프레임의 모든 오브젝트 행렬·카메라 렌즈 해시가 A와 동일함을 확인했습니다. FPS만24→42로 변경하여 접지·동선·문·화물의 프레임별 관계를 보존했습니다. 영상 전체 디코드와 프레임 수/속도/길이 검사 통과. 이 버전은 속도 비교용이며 기존 A/B 최종 리듬 선택을 대체하지 않습니다.
''',encoding='utf8')
print('VIDEO_VERIFIED',str(out),record['video_duration'])

