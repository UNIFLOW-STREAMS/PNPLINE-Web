"""Encode sampled source frames at their original elapsed timing; bind output to candidate hash."""
import json,hashlib,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];version=sys.argv[1]
groups=[R/'preview'/f'sequence-{part}-{version}' for part in 'ab'];metadata=[json.loads((p/'metadata.json').read_text()) for p in groups]
assert len({m['sha256'] for m in metadata})==1
candidate=R/f'candidate-curvature-{version}.blend';assert metadata[0]['sha256']==hashlib.sha256(candidate.read_bytes()).hexdigest()
frames=sorted((p/f'f{f:04}.png',f) for p,m in zip(groups,metadata) for f in m['frames'])
frames.sort(key=lambda item:item[1]);assert [f for _,f in frames]==list(range(380,1393,4))
manifest=R/'preview'/f'concat-{version}.txt';manifest.write_text(''.join(f"file '{p.as_posix()}'\nduration 0.1666666667\n" for p,f in frames))
out=R/'preview'/f'us-curvature-{version}.mp4';assert not out.exists()
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-f','concat','-safe','0','-i',str(manifest),'-r','6','-frames:v',str(len(frames)),'-an','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(out)],check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(out)]))
info={'candidate_sha256':metadata[0]['sha256'],'video_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'frames':len(frames),'sample_step':4,'preview_fps':6,'source_fps':24,'probe':probe}
(R/'review'/f'video-{version}.json').write_text(json.dumps(info,indent=2));print(out,info['frames'],probe['format']['duration'])
