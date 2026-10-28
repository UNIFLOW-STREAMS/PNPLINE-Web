import json,sys,shutil,html,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
B=Path(__file__).resolve().parents[1];OLD=B.parent/'s5-sync-v001'
sys.path.insert(0,str(B/'scripts'))
from lineage import digest,require,validate_expression
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rec=load(B/'line-art-record.json');rawrec=load(OLD/'render-record.json');sel=load(B/'storyboard-selection.json')
validate_expression(rec,rawrec,B/'storyboard-selection.json')
require(digest(B/'scripts/render_line_art.py')==rec['render_script_sha256'],'render code changed')
require(digest(B/'scripts/lineage.py')==rec['lineage_script_sha256'],'lineage code changed')
require(digest(rec['source_path'])==rec['source_sha256'],'source changed')
draft=load(B/'storyboard-manifest.json')
if not (B/'review/structural-draft-manifest.json').exists():shutil.copy2(B/'storyboard-manifest.json',B/'review/structural-draft-manifest.json')
draft=load(B/'review/structural-draft-manifest.json')
font=lambda n,b=False:ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf' if b else 'C:/Windows/Fonts/malgun.ttf',n)
panels=[];comparisons=[]
for p in sel['panels']:
 e=next(e for e in rec['images'] if e['id']==p['id']);previous=next(e for e in draft['panels'] if e['id']==p['id'])
 im=Image.open(e['path']).convert('RGB');w,h=im.size
 panel=Image.new('RGB',(w+32,h+160),'white');panel.paste(im,(16,16));d=ImageDraw.Draw(panel);d.rectangle((15,15,w+16,h+16),outline='#202020',width=1)
 d.text((18,h+29),f"{p['id']}  /  {p['role']}",font=font(23,True),fill='#101010')
 d.text((18,h+66),p['action'],font=font(17),fill='#202020')
 d.text((18,h+98),f"f{p['frame']}  ·  본편 {p['master_seconds']:.3f}s  ·  프리뷰 {p['preview_seconds']:.3f}s  ·  CAM_MASTER",font=font(16),fill='#444444')
 d.text((18,h+124),'선택 프레임·표현 방향 반영 · 최종 콘티 승인 대기',font=font(15),fill='#555555')
 dest=B/'panels'/f"{p['id']}-f{p['frame']}.png";panel.save(dest)
 comp=Image.new('RGB',(w*2+48,h+74),'white');cd=ImageDraw.Draw(comp);cd.text((16,14),f"{p['id']} f{p['frame']} · 실제 본편",font=font(22,True),fill='black');cd.text((w+32,14),'같은 구도 · 흑백 윤곽',font=font(22,True),fill='black')
 comp.paste(Image.open(previous['raw_path']).convert('RGB'),(16,58));comp.paste(im,(w+32,58));cp=B/'review'/f"{p['id']}-comparison.png";comp.save(cp);comparisons.append(cp)
 item={**previous,**p,'source':{'path':rec['source_path'],'sha256':rec['source_sha256']},'path':str(dest),'sha256':digest(dest),'status':'selected frames; final panel approval pending','approved':False,'line_art':{'path':e['path'],'sha256':e['sha256'],'raw_parent_sha256':e['raw_sha256'],'record_path':str(B/'line-art-record.json'),'record_sha256':digest(B/'line-art-record.json')},'expression':{'method':rec['method'],'settings':rec['settings'],'scaling':[1,1],'crop':False,'image_region':[16,16,w,h]},'comparison':{'path':str(cp),'sha256':digest(cp)},'final_user_approval':None}
 panels.append(item)
contact=Image.new('RGB',(1440,1640),'#eeeee9');d=ImageDraw.Draw(contact);d.text((28,20),'S5 스토리보드 · 흑백 러프 콘티',font=font(32,True),fill='#202020');d.text((28,69),'s5-integration-v001 / 선택한 실제 프레임·표현 방향 반영 / 최종 승인 대기',font=font(19),fill='#505050')
for n,p in enumerate(panels):
 im=Image.open(p['path']);im.thumbnail((688,496));contact.paste(im,(24+(n%2)*716,112+(n//2)*504))
contact.save(B/'review/final-contact.png')
comparecontact=Image.new('RGB',(1440,6*462+60),'white');d=ImageDraw.Draw(comparecontact);d.text((20,12),'왼쪽 실제 본편 / 오른쪽 동일 구도 선화',font=font(25,True),fill='black')
for n,cp in enumerate(comparisons):
 im=Image.open(cp);im.thumbnail((1408,446));comparecontact.paste(im,(16,60+n*462))
comparecontact.save(B/'review/structure-comparison.png')
manifest={'status':'technical synchronization candidate; final user approval pending','source':panels[0]['source'],'selection_path':str(B/'storyboard-selection.json'),'selection_sha256':digest(B/'storyboard-selection.json'),'expression_record_path':str(B/'line-art-record.json'),'expression_record_sha256':digest(B/'line-art-record.json'),'reuse_provenance':draft['reuse_provenance'],'panels':panels,'packager_sha256':digest(__file__),'font_hashes':{p:digest(p) for p in ['C:/Windows/Fonts/malgun.ttf','C:/Windows/Fonts/malgunbd.ttf']}}
save(B/'storyboard-manifest.json',manifest)
dec=load(B/'review-decisions.json');dec['final_package']={'status':'awaiting final user review','manifest_sha256':digest(B/'storyboard-manifest.json'),'source_sha256':rec['source_sha256'],'expression_run_id':rec['run_id']};save(B/'review-decisions.json',dec)
page=(B/'review.html').read_text(encoding='utf-8');page=page.replace('구조 검토 후보','흑백 콘티 · 최종 검토');page=page.replace('여섯 관찰 지점','선택한 여섯 관찰 지점 · 흑백 콘티');page=page.replace('review/candidates.png','review/final-contact.png');page=page.replace('현재는 샘플 한 장이며, 프레임과 표현 방향 선택 후 여섯 장에 적용합니다.','사용자가 선택한 표현 방향을 아래 여섯 장에 적용했습니다. 최종 콘티 묶음은 사용자 검토 대기 상태입니다.')
for p in panels:
 page=page.replace(f"panels/{p['id']}-draft-f{p['frame']}.png",f"panels/{p['id']}-f{p['frame']}.png")
 page=page.replace(f"{p['id']} 구조 초안",f"{p['id']} 흑백 콘티")
 page=page.replace(f'<a href="review/{p["id"]}-raw.png">무주석 원본</a>',f'<a href="review/{p["id"]}-raw.png">무주석 원본</a> · <a href="review/{p["id"]}-comparison.png">원본·선화 대조</a>')
page=page.replace('<p><a href="#style">','<p>프레임과 선화 방향은 선택 완료했습니다. 마스터 무수정·동일 투영으로 6장을 제작했으며, 최종 묶음 승인은 별도입니다.</p><p><a href="review/structure-comparison.png">6장 원본·선화 전체 대조</a> · <a href="#style">')
(B/'review.html').write_text(page,encoding='utf-8')
print('PACKAGED FINAL',len(panels), 'panels; final artistic approval pending')
