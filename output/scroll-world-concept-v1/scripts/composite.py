from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
import numpy as np
import json,hashlib
OUT=Path(__file__).resolve().parents[1]
ROOT=OUT.parents[1]
LOGO=ROOT/'docs/plan/issue-61-brand-miniature/references/PNP-LINE.webp'
placements=json.loads((OUT/'data/logo-placements.json').read_text(encoding='utf-8-sig'))
source=Image.open(LOGO).convert('RGBA'); crop=source.getchannel('A').getbbox();logo=source.crop(crop)
logo.save(OUT/'branding/derived/PNP-LINE-trimmed.png')
def hmatrix(dst,src):
 A=[];B=[]
 for (x,y),(u,v) in zip(dst,src):
  A.extend([[x,y,1,0,0,0,-u*x,-u*y],[0,0,0,x,y,1,-v*x,-v*y]]);B.extend([u,v])
 return np.linalg.solve(np.asarray(A),np.asarray(B))
assets=[]
for p in placements['placements']:
 path=OUT/p['base_path']
 if not path.exists():continue
 base=Image.open(path).convert('RGBA');W,H=p['export_size'];
 # Preserve the original and all glyph proportions. Any generated alpha is flattened
 # onto a recorded neutral review background; no scene pixels are painted over.
 fitted=ImageOps.contain(base,(W,H),Image.Resampling.LANCZOS)
 canvas=Image.new('RGBA',(W,H),tuple(p.get('flatten_background',[243,245,242]))+(255,));canvas.alpha_composite(fitted,((W-fitted.width)//2,(H-fitted.height)//2))
 dst=[(x*W,y*H) for x,y in p['logo_quad']]
 coeff=hmatrix(dst,[(0,0),(logo.width,0),(logo.width,logo.height),(0,logo.height)])
 layer=logo.transform((W,H),Image.Transform.PERSPECTIVE,coeff,Image.Resampling.BICUBIC)
 canvas=Image.alpha_composite(canvas,layer)
 target=OUT/p['output_path'];canvas.convert('RGB').save(target,quality=95,subsampling=0)
 p['source_crop_pixels']=list(crop);p['source_trimmed_size']=list(logo.size);p['base_size']=list(base.size);p['fitted_size']=list(fitted.size);p['fit_offset']=[(W-fitted.width)//2,(H-fitted.height)//2];p['homography_inverse']=coeff.tolist();p['logo_source_sha256']=hashlib.sha256(LOGO.read_bytes()).hexdigest();p['composited']=True
 sid=p['scene_id'];o=p['orientation'];quad=p['logo_quad'];xs=[q[0] for q in quad];ys=[q[1] for q in quad]
 # Mask protection follows actual applied artwork with a small review clearance.
 rect=[max(0,min(xs)-.012),max(0,min(ys)-.015),min(1,max(xs)+.012)-max(0,min(xs)-.012),min(1,max(ys)+.015)-max(0,min(ys)-.015)]
 if p['variant']=='A':
  mp=OUT/f'masks/{o}/{sid}.json';m=json.loads(mp.read_text());m['basis']='review_layout_measured_against_export';m['reference_size']=[W,H]
  for r in m['regions']:
   if r['id']=='logo':r['rect']=rect
   if r['id'] in p.get('mask_overrides',{}):r['rect']=p['mask_overrides'][r['id']]
  mp.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  colors={'text_allowed':'#007fa8','protect_object':'#bf6f1d','protect_logo':'#9652c2','protect_route':'#00abe1','ui_interference':'#b83a36'}
  svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000" preserveAspectRatio="none">'
  for r in m['regions']:
   x,y,w,h=r['rect'];c=colors[r['role']];svg+=f'<rect x="{x*1000}" y="{y*1000}" width="{w*1000}" height="{h*1000}" fill="{c}" fill-opacity=".10" stroke="{c}" stroke-width="2"/>'
  (OUT/f'masks/{o}/{sid}.svg').write_text(svg+'</svg>',encoding='utf-8')
 # Comparison: exact source at top, actual output crop below, neither invented.
 x0=max(0,int(min(xs)*W)-15);y0=max(0,int(min(ys)*H)-15);x1=min(W,int(max(xs)*W)+15);y1=min(H,int(max(ys)*H)+15)
 detail=canvas.crop((x0,y0,x1,y1)).convert('RGB');detail.thumbnail((760,230))
 sheet=Image.new('RGB',(800,350),'white');mark=logo.copy();mark.thumbnail((700,120));sheet.paste(mark,(50,35),mark);sheet.paste(detail,((800-detail.width)//2,170))
 sheet.save(OUT/f"qa/logo-comparisons/{p['id']}.jpg",quality=95)
 kind='clean-branded' if p['variant']=='A' else 'styleframe'
 a={'asset_id':p['id'],'scene_id':sid,'variant':p['variant'],'direction':'daylight logistics' if p['variant']=='A' else ('dusk cinematic' if p['variant']=='B' else 'top-down technical'),'orientation':o,'path':p['output_path'],'width':W,'height':H,'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'kind':kind,'prompt_path':'prompts/'+p['prompt_id'],'base_path':p['base_path'],'logo_placement_id':p['id'],'logo_source_id':'REF-LOGO-01','logo_source_sha256':p['logo_source_sha256'],'prompt_id':p['prompt_id'],'reference_ids':['REF-STYLE-01','REF-LOGO-01'],'image_reference_delivery':'see execution receipt; art direction reference is not necessarily tool image input','generation_tool':'image_gen.imagegen','generation_model':'unknown_not_exposed','compositing_tool':'Pillow 11.1.0 + NumPy 2.2.4','generation_status':'generated','composite_status':'composited','review_status':'coordinator_review_with_findings_pending_human','visual_findings':'qa/visual-decisions.json','approval_status':'not_approved','mask_path':f'masks/{o}/{sid}.json' if p['variant']=='A' else None}
 assets.append(a)
 if sid=='S01' and p['variant']=='A' and o=='desktop':
  import shutil
  shutil.copyfile(target,OUT/'styleframes/S01-A.jpg')
  assets.append({**a,'asset_id':'styleframe-A','kind':'styleframe','path':'styleframes/S01-A.jpg','reuses_asset_id':p['id']})
for f in sorted((OUT/'base-scenes').glob('*.png')):
 im=Image.open(f);sid=f.stem[:3];o='mobile' if 'mobile' in f.stem else 'desktop';variant='B' if 'S01-B' in f.stem else ('C' if 'S01-C' in f.stem else 'A');prompt=('execution-S01-'+variant+'.json') if sid=='S01' and o=='desktop' else ('execution-'+sid+'-'+o+'.json');assets.append({'scene_id':sid,'orientation':o,'variant':variant,'prompt_path':'prompts/'+(('execution-'+f.stem+'.json') if (OUT/'prompts'/('execution-'+f.stem+'.json')).exists() else prompt),'selected_by':[x['asset_id'] for x in assets if x.get('base_path')==str(f.relative_to(OUT)).replace('\\','/')],'reference_ids':['REF-STYLE-01'],'reference_usage':'art direction only; see exact tool inputs in receipt','generation_tool':'image_gen.imagegen','cost':'unknown','seed':'not_available','asset_id':'base-'+f.stem,'kind':'base','path':str(f.relative_to(OUT)).replace('\\','/'),'width':im.width,'height':im.height,'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'generation_status':'generated','review_status':'see_execution_receipt','approval_status':'not_approved','model':'unknown_not_exposed'})
counts={'generated_unique':len({a['sha256'] for a in assets if a['kind']=='base'}),'desktop_clean':sum(a['kind']=='clean-branded' and a['orientation']=='desktop' for a in assets),'mobile_clean':sum(a['kind']=='clean-branded' and a['orientation']=='mobile' for a in assets),'styleframes':sum(a['kind']=='styleframe' for a in assets),'reused_styleframes':1,'video_generation_calls':0}
manifest={'purpose':'concept-review_not_production_manifest','art_direction_compliance':'partial_pending_visual_review','human_visual_approval':'not_approved','production_release_approval':'not_approved','status':'ready_for_review' if counts['desktop_clean']==6 and counts['mobile_clean']==6 and counts['styleframes']==3 else 'partial','counts':counts,'cost':'unknown','seed':'not_available','assets':assets}
(OUT/'data/assets.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/'data/logo-placements.json').write_text(json.dumps(placements,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Own-generated material study; never incorporates the user's style-reference pixels.
if assets:
 mat=Image.new('RGB',(1200,800),(242,244,241));draw=ImageDraw.Draw(mat)
 src=Image.open(OUT/'keyframes/desktop/S01.jpg')
 boxes=[(.45,.18,.72,.47),(.70,.38,.98,.67),(.45,.60,.77,.95),(.60,.04,.99,.32)]
 for i,(x,y,w,h) in enumerate(boxes):
  tile=src.crop((int(x*src.width),int(y*src.height),int(w*src.width),int(h*src.height)));tile=ImageOps.fit(tile,(580,370));mat.paste(tile,(10+(i%2)*600,10+(i//2)*400));draw.text((20+(i%2)*600,383+(i//2)*400),['METAL / STRUCTURE','PROCESS / SCALE','WRAP / KRAFT','LIGHT / BRAND SURFACE'][i],fill='#182c39')
 mat.save(OUT/'moodboard/material-study.jpg',quality=91)
print(json.dumps(counts))
