from pathlib import Path
import json, hashlib
B=Path(__file__).resolve().parents[1]
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
answer='6개 프레임과 선화 방향 채택'
evidence={'answer':answer,'source':'actual user question reply in current conversation','question_item_id':'["request_user_input_async","call_9b5e681d37f54ba4b14bda8d7889dd82",0]','client_date':'2026-10-09','exact_response_timestamp':None,'scope':'six frames and white background/black contour Freestyle direction; final rendered package not yet approved'}
selection=load(B/'storyboard-selection.json')
for p in selection['panels']:p.update(status='selected',user_approval=evidence)
save(B/'storyboard-selection.json',selection)
d=load(B/'review-decisions.json');d['frames']={'status':'selected','frames':[p['frame'] for p in selection['panels']],'evidence':evidence};d['style']={'status':'selected','method':'same as f766 Freestyle sample','evidence':evidence};save(B/'review-decisions.json',d)
video=load(B/'preview/video-record.json')
save(B/'review/playback.json',{'pass':True,'video_sha256':video['sha256'],'current_time_s':27.083333,'duration_s':27.083333,'playback_rate':1,'ended':True,'elapsed_wall_seconds':27.13060000000149,'media_error':None,'method':'CUA button click and read-only video element observations; no seeking'})
with (B/'progress.md').open('a',encoding='utf-8') as f:f.write('\nT0 complete: fresh actual source reopen/state equality and all34 regression tests pass. T1 selected by actual user reply: “'+answer+'”. Raw 325-frame preview played to27.083333s at1x with no media error. New expression lineage tests8 failures RED (valid case passes), implementation GREEN pending.\n')
