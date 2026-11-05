"""Validate all Cycles frames and make seek-friendly, versioned web media."""
import hashlib, json, struct, subprocess, time
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'assets'; REVIEW=ROOT/'review'
SOURCE=Path('F:/pnpline-landing/hero-section-video/hero-section-B.blend')
EXPECTED='65299a8273754bade3a47cc7dbf4f21e92a8e28ac4d6b0e48747a6e5556c55bb'
def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def run(args,name):
    with (REVIEW/name).open('w',encoding='utf-8') as log:
        subprocess.run(args,check=True,stdout=log,stderr=subprocess.STDOUT)
def probe(path):
    return json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(path)]))
def faststart(path):
    boxes=[]
    with path.open('rb') as stream:
        while True:
            head=stream.read(8)
            if len(head)<8:break
            length,kind=struct.unpack('>I4s',head);extra=0
            if length==1:length=struct.unpack('>Q',stream.read(8))[0];extra=8
            boxes.append(kind.decode('ascii'))
            if length==0:break
            stream.seek(length-8-extra,1)
    return boxes.index('moov')<boxes.index('mdat')
assert sha(SOURCE)==EXPECTED,'Adopted B changed during render; inspect before delivery'
for frame in range(990):
    path=ROOT/'frames'/f'f{frame:04}.png'
    with path.open('rb') as stream:head=stream.read(29)
    assert head[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',head[16:24])==(1920,1080) and head[24]==16
    with Image.open(path) as image:image.verify()
print('Validated 990 native 1080p / 16-bit Cycles frames',flush=True)
base=['ffmpeg','-hide_banner','-loglevel','warning','-y']
conversion='flags=lanczos+accurate_rnd+full_chroma_int:out_color_matrix=bt709:out_range=tv:sws_dither=ed'
color=['-color_range','tv','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709']
manifest={'version':'B-cycles-web-v002','source':str(SOURCE),'source_sha256':EXPECTED,'frame_start':0,'frame_end':989,'fps':30,'duration':33,'animation_retimed':False,'renderer':'Cycles / OptiX / RTX 4070','samples':96,'color':{'view':'AgX','look':'AgX - Medium High Contrast','exposure':.3,'web':'BT.709 limited-range 8-bit YUV420 with error-diffusion dithering'},'videos':{}}
for width,height,gop,crfs,budget in [(1920,1080,8,[20.5,21,22],32*1024**2),(1280,720,4,[26,27,28],12*1024**2)]:
    path=ASSETS/f'hero-b-v002-{height}p.mp4'
    t=time.perf_counter()
    for crf in crfs:
        run(base+['-framerate','30','-start_number','0','-i',str(ROOT/'frames/f%04d.png'),'-frames:v','990',
            '-vf',f'scale={width}:{height}:{conversion},format=yuv420p','-c:v','libx264','-preset','slow','-crf',str(crf),
            '-g',str(gop),'-keyint_min',str(gop),'-sc_threshold','0','-bf','0','-profile:v','high','-level:v','4.1',
            '-an','-movflags','+faststart']+color+[str(path)],f'encode-{height}-crf{crf}.log')
        if path.stat().st_size<=budget:break
    assert path.stat().st_size<=budget, f'{height}p exceeds web budget'
    info=probe(path);stream=info['streams'][0]
    assert stream['codec_name']=='h264' and stream['pix_fmt']=='yuv420p' and stream['r_frame_rate']=='30/1'
    assert int(stream['nb_read_frames'])==990 and abs(float(info['format']['duration'])-33)<.001
    assert not any(v['codec_type']=='audio' for v in info['streams'])
    assert faststart(path)
    keys=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v','-skip_frame','nokey','-show_entries','frame=pts_time','-of','json',str(path)]))['frames']
    gaps=[float(b['pts_time'])-float(a['pts_time']) for a,b in zip(keys,keys[1:])]
    assert max(gaps)<=(gop+.01)/30
    entry={'file':path.name,'bytes':path.stat().st_size,'sha256':sha(path),'width':width,'height':height,'frames':990,'seconds':33,'crf':crf,'gop':gop,'b_frames':0,'faststart':True,'encode_seconds':time.perf_counter()-t}
    manifest['videos'][f'{height}p']=entry
    (REVIEW/f'ffprobe-{height}.json').write_text(json.dumps(info,indent=2))
    print('ENCODE_COMPLETE',json.dumps(entry),flush=True)
    # Compare decoded output against the identical color conversion, every fifth frame.
    score=REVIEW/f'vmaf-{height}.json'
    filt=f'[0:v]setpts=PTS-STARTPTS[dist];[1:v]scale={width}:{height}:{conversion},format=yuv420p,setpts=PTS-STARTPTS[ref];[dist][ref]libvmaf=log_fmt=json:log_path={score.name}:n_threads=6:n_subsample=5'
    with (REVIEW/f'vmaf-{height}.log').open('w') as log:
        subprocess.run(base+['-i',str(path),'-framerate','30','-start_number','0','-i',str(ROOT/'frames/f%04d.png'),'-filter_complex',filt,'-frames:v','990','-f','null','-'],cwd=REVIEW,stdout=log,stderr=subprocess.STDOUT,check=True)
    entry['vmaf']=json.loads(score.read_text())['pooled_metrics']['vmaf']
    assert entry['vmaf']['mean']>=95, 'Review encoder quality before publication'
for name,frame in [('poster',0),('final',989)]:
    run(base+['-i',str(ROOT/'frames'/f'f{frame:04}.png'),'-frames:v','1','-c:v','libwebp','-quality','88',str(ASSETS/f'hero-b-v002-{name}.webp')],f'{name}.log')
for name,start in [('ocean',180),('us-port',340),('warehouse',750)]:
    run(base+['-ss',str(start/30),'-i',str(ASSETS/'hero-b-v002-1080p.mp4'),'-t','2','-c:v','copy','-an',str(REVIEW/f'{name}-30fps.mp4')],f'clip-{name}.log')
times=[json.loads(line)['seconds'] for line in (REVIEW/'frame-times.jsonl').read_text().splitlines()]
manifest['render_seconds']=sum(times)
manifest['mean_frame_seconds']=sum(times)/len(times)
manifest['frame_times_count']=len(times)
manifest['source_unchanged']=sha(SOURCE)==EXPECTED
manifest['budgets_bytes']={'1080p':32*1024**2,'720p':12*1024**2}
(ASSETS/'hero-b-v002-manifest.json').write_text(json.dumps(manifest,indent=2))
print('WEB_MEDIA_READY',json.dumps(manifest),flush=True)
