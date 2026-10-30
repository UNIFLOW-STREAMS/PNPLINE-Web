import json,hashlib,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];paths=[R/'preview'/f'v013-sequence-{k}' for k in 'ab'];metas=[json.loads((p/'metadata.json').read_text()) for p in paths]
assert len({m['sha256'] for m in metas})==1
frames=sorted([(f,p/f'f{f:04}.png') for p,m in zip(paths,metas) for f in m['frames']]);assert [f for f,_ in frames]==list(range(408,697))
fps=metas[0]['source_fps'];assert fps==12
concat=R/'preview/concat-v013.txt';concat.write_text(''.join(f"file '{p.as_posix()}'\nduration {1/fps:.12f}\n" for _,p in frames))
out=R/'preview/city-reveal-v013.mp4';assert not out.exists()
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-f','concat','-safe','0','-i',str(concat),'-r',str(fps),'-frames:v',str(len(frames)),'-an','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(out)],check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(out)]))
assert int(probe['streams'][0]['nb_frames'])==289
(R/'review/video-v013.json').write_text(json.dumps({'candidate_sha256':metas[0]['sha256'],'video_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'frames':len(frames),'fps':fps,'probe':probe},indent=2));print(out,probe['format']['duration'])




