import json,hashlib,subprocess,statistics,re
from pathlib import Path
R=Path(__file__).resolve().parents[1];scene=json.loads((R/'data/source-scene.json').read_text(encoding='utf-8'))
def sha(p):
 with open(p,'rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=codec_name,width,height,r_frame_rate,avg_frame_rate,nb_frames,nb_read_frames,duration:format=duration,size','-of','json',str(p)],text=True))
videos=[]
for name,gop,crf in [('previz-source.mp4',60,16),('previz-scrub.mp4',8,20)]:
 p=R/'assets'/name;q=probe(p);v=q['streams'][0];assert int(v['nb_frames'])==990;assert v['r_frame_rate']=='30/1';assert abs(float(v['duration'])-33)<1e-6
 videos.append(dict(path=str(p.resolve()),relative='assets/'+name,sha256=sha(p),bytes=p.stat().st_size,probe=q,gop=gop,crf=crf,pixel_format='yuv420p',audio=False,faststart=True))
source_sha_now=sha(Path(scene['source']));assert source_sha_now==scene['sha256'],'Source changed externally during task; inspect before signing off'
log=(R/'review/final-render.log').read_text(encoding='utf-8');entries=[(int(f),float(t))for f,t in re.findall(r'ANIM_FRAME (\d+) ([\d.]+)',log)];assert len(entries)==990
durations=[b[1]-a[1]for a,b in zip(entries,entries[1:])]
out=dict(source_blend=scene['source'],source_sha256=scene['sha256'],source_sha256_after=source_sha_now,source_unchanged=True,camera=scene['camera'],fps=30,frame_start=0,frame_end=989,frame_count=990,duration_seconds=33,last_frame_timestamp=989/30,renderer='BLENDER_WORKBENCH',resolution=[1280,720],render_aa=8,render_proxy='In-memory consolidation of static rigid meshes, evaluated modifiers and object material slots. Animated parents retained. No blend saved.',limitations=['Not a Cycles lookdev/final render: shader nodes, transparency, water response, DOF and production lighting not represented.','Rigid mesh consolidation can change shading normals; visual timing and camera review only.','Landscape 16:9 full frame shown on phones; no new portrait film.'],render_seconds_first_to_last=entries[-1][1]-entries[0][1],median_interframe_render_seconds=statistics.median(durations),videos=videos,posters=[dict(path=str((R/'assets'/f's{i}.jpg').resolve()),frame=f,sha256=sha(R/'assets'/f's{i}.jpg'))for i,f in enumerate([0,110,240,390,570,740,920],1)],old_24fps_map_reused=False,new_ai_media=False,external_services_used=False)
(R/'data/media-manifest.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(dict(source_unchanged=True,frame_count=990,duration=33,video_bytes=[v['bytes']for v in videos],render_seconds=out['render_seconds_first_to_last'])))
