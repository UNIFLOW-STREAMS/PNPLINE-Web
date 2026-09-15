"""Build only the v2 assets; preserve every v1 source and original logo."""
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw
import numpy as np
import json, hashlib
HERE=Path(__file__).resolve().parent
OUT=HERE.parent
ROOT=OUT.parents[1]
SOURCE=ROOT/'docs/plan/issue-61-brand-miniature/references/PNP-LINE.webp'
logo_full=Image.open(SOURCE).convert('RGBA')
logo=logo_full.crop(logo_full.getchannel('A').getbbox())
def fit_logo_quad(points,width,height):
 """Inset artwork in a measured surface so a taller blank panel does not stretch the wordmark."""
 q=np.asarray(points,dtype=float)*np.array([width,height])
 edge_width=(np.linalg.norm(q[1]-q[0])+np.linalg.norm(q[2]-q[3]))/2
 edge_height=(np.linalg.norm(q[3]-q[0])+np.linalg.norm(q[2]-q[1]))/2
 art_ratio=logo.width/logo.height
 surface_ratio=edge_width/edge_height
 u=min(1,art_ratio/surface_ratio);v=min(1,surface_ratio/art_ratio)
 def point(a,b):
  return ((1-a)*(1-b)*q[0]+a*(1-b)*q[1]+a*b*q[2]+(1-a)*b*q[3])/np.array([width,height])
 return [point((1-u)/2,(1-v)/2).tolist(),point((1+u)/2,(1-v)/2).tolist(),point((1+u)/2,(1+v)/2).tolist(),point((1-u)/2,(1+v)/2).tolist()]
scenes=[
 ('S01','CN','중국 · 출항 부두','中国 · 出发港','중국에서 출발','从中国出发','같은 파란 컨테이너를 선박에 싣습니다.','同一蓝色集装箱装上货船。','육지에서 바다로','陆地 → 海洋','왼쪽 집하장 → 중앙 컨테이너 → 오른쪽 선박','左侧集货区 → 中部集装箱 → 右侧货船','중국 국기 · 밀집한 항만 배후 도시 · 선적 크레인','中国国旗 · 密集港区城市 · 装船起重机','가까운 화물 → 뒤쪽 선적 크레인과 바다','近处货物 → 后方装船起重机与海面'),
 ('S02','PACIFIC','태평양 · 해상 운송','太平洋 · 海运','태평양을 건너','跨越太平洋','출발 항만을 뒤로 두고 미국으로 향합니다.','驶离出发港，向美国前进。','선미에서 선수로','船尾 → 船首','선미의 항적 → 파란 컨테이너 → 오른쪽 선수와 수평선','船尾航迹 → 蓝色集装箱 → 右侧船首与地平线','넓은 해면 · 뒤로 멀어지는 육지 · 전진하는 동일 선박','开阔海面 · 逐渐远去的陆地 · 同一艘船','아래쪽 선미와 항적 → 위쪽 선수와 수평선','下方船尾航迹 → 上方船首与地平线'),
 ('S03','US','미국 · 도착 항만','美国 · 到达港','미국 항만에 도착','抵达美国港口','내린 컨테이너가 미국 내륙 창고로 이동합니다.','卸船后的集装箱转往美国内陆仓库。','바다에서 내륙으로','海洋 → 内陆','왼쪽 선박 → 하역된 컨테이너 → 오른쪽 미국 트럭과 창고','左侧货船 → 卸下的集装箱 → 右侧美式卡车与仓库','미국 국기 · 긴 보닛 트럭 · 저층 산업지와 넓은 도로','美国国旗 · 长头卡车 · 低层工业区与宽阔道路','가까운 하역 화물 → 트럭 → 뒤쪽 미국 창고','近处卸货区 → 卡车 → 后方美国仓库'),
 ('S04','US','미국 · 입고 및 보관','美国 · 入库与保管','도크에서 보관 랙으로','从月台进入货架','도착한 화물을 창고 안으로 옮겨 보관합니다.','将到达的货物移入仓库并上架。','밖에서 안으로','室外 → 室内','왼쪽 입고 도크 → 지게차 → 오른쪽 보관 랙','左侧入库月台 → 叉车 → 右侧货架','같은 미국 창고 · 남색 프레임 · 도크 밖 파란 컨테이너','同一美国仓库 · 海军蓝框架 · 月台外蓝色集装箱','아래쪽 입고 도크 → 안쪽 깊은 랙 통로','下方入库月台 → 内部纵深货架通道'),
 ('S05','US','미국 · 피킹 및 포장','美国 · 拣选与包装','보관에서 출고 준비로','从保管到出库准备','파란 띠의 상자가 피킹과 포장을 거칩니다.','带蓝色束带的纸箱经过拣选与包装。','랙에서 출고문으로','货架 → 出库门','왼쪽 랙 → 중앙 포장 작업 → 오른쪽 출고문','左侧货架 → 中部包装工位 → 右侧出库门','같은 창고 내부 · 반복되는 파란 띠 화물 · 바깥의 미국 풍경','同一仓库内部 · 蓝色束带货物 · 门外美国环境','가까운 포장 작업 → 컨베이어 → 뒤쪽 열린 출고문','近处包装工作 → 输送线 → 后方敞开的出库门'),
 ('S06','US','미국 · 분기 출고','美国 · 分流出库','미국 배송으로 이어집니다','进入美国配送','팔레트 운송 또는 택배 배송으로 나뉩니다.','分为托盘运输或包裹配送。','창고에서 배송 도로로','仓库 → 配送道路','왼쪽 출고 도크 → 운송 차량 → 오른쪽 미국 배송 도로','左侧出库月台 → 运输车辆 → 右侧美国配送道路','미국 국기 · 미국식 트랙터 · 저층 주거지와 배송 도로','美国国旗 · 美式牵引车 · 低层住宅与配送道路','가까운 출고 화물 → 분기 차량 → 멀어지는 배송 도로','近处出库货物 → 分流车辆 → 远方配送道路')
]
data={'revision':2,'purpose':'still-frame-camera-study','duration':30,'video_generation_calls':0,'scenes':[],'assets':[]}
for row in scenes:
 sid,phase,koPlace,zhPlace,koTitle,zhTitle,koBody,zhBody,koCamera,zhCamera,koFlow,zhFlow,koProof,zhProof,koMobile,zhMobile=row
 data['scenes'].append({'id':sid,'phase':phase,'ko':{'place':koPlace,'title':koTitle,'body':koBody,'camera':koCamera,'flow':koFlow,'proof':koProof,'mobileFlow':koMobile},'zh':{'place':zhPlace,'title':zhTitle,'body':zhBody,'camera':zhCamera,'flow':zhFlow,'proof':zhProof,'mobileFlow':zhMobile}})
 for orientation in ['desktop','mobile']:
  name=f'{sid}-{orientation}'
  receipt_path=HERE/f'receipts/{name}.json'
  source_path=HERE/f'base/{name}.png'
  if not receipt_path.exists() or not source_path.exists():
   raise RuntimeError(f'Missing image/receipt: {name}')
  receipt=json.loads(receipt_path.read_text(encoding='utf-8-sig'))
  base=Image.open(source_path).convert('RGBA')
  W,H=base.size
  quad=fit_logo_quad(receipt['logo_quad'],W,H)
  secondary_quads=[fit_logo_quad(q,W,H) for q in receipt.get('secondary_logo_quads',[])]
  dst=[(x*W,y*H) for x,y in quad]
  src=[(0,0),(logo.width,0),(logo.width,logo.height),(0,logo.height)]
  A=[];B=[]
  for (x,y),(u,v) in zip(dst,src):
   A.extend([[x,y,1,0,0,0,-u*x,-u*y],[0,0,0,x,y,1,-v*x,-v*y]]);B.extend([u,v])
  coefficients=np.linalg.solve(np.asarray(A),np.asarray(B))
  layer=logo.transform((W,H),Image.Transform.PERSPECTIVE,coefficients,Image.Resampling.BICUBIC)
  base.alpha_composite(layer)
  for secondary in secondary_quads:
   secondary_dst=[(x*W,y*H) for x,y in secondary]
   sec_A=[];sec_B=[]
   for (x,y),(u,v) in zip(secondary_dst,src):
    sec_A.extend([[x,y,1,0,0,0,-u*x,-u*y],[0,0,0,x,y,1,-v*x,-v*y]]);sec_B.extend([u,v])
   sec_coefficients=np.linalg.solve(np.asarray(sec_A),np.asarray(sec_B))
   base.alpha_composite(logo.transform((W,H),Image.Transform.PERSPECTIVE,sec_coefficients,Image.Resampling.BICUBIC))
  (HERE/'keyframes').mkdir(exist_ok=True)
  target=HERE/f'keyframes/{name}.webp'
  base.convert('RGB').save(target,format='WEBP',quality=85,method=6)
  xs=[p[0] for p in quad];ys=[p[1] for p in quad]
  rect=[max(0,min(xs)-.01),max(0,min(ys)-.01),min(1,max(xs)+.01)-max(0,min(xs)-.01),min(1,max(ys)+.01)-max(0,min(ys)-.01)]
  data['assets'].append({'id':name,'scene':sid,'orientation':orientation,'path':f'continuity-v2/keyframes/{name}.webp','width':W,'height':H,'logo_quad':quad,'protect_logo':rect,'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(source_path.read_bytes()).hexdigest(),'receipt':f'continuity-v2/receipts/{name}.json','logo_source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'approval_status':'pending_user_visual_review'})
  data['assets'][-1]['secondary_logo_quads']=secondary_quads
  data['assets'][-1]['logo_source_trimmed_size']=list(logo.size)
  data['assets'][-1]['logo_fit']='aspect-contained within measured panel before perspective'
  data['assets'][-1]['protect_logos']=[rect]
  for secondary in secondary_quads:
   sx=[p[0] for p in secondary];sy=[p[1] for p in secondary]
   data['assets'][-1]['protect_logos'].append([min(sx)-.005,min(sy)-.005,max(sx)-min(sx)+.01,max(sy)-min(sy)+.01])
  crop=base.crop((int(min(xs)*W)-8,int(min(ys)*H)-8,int(max(xs)*W)+8,int(max(ys)*H)+8)).convert('RGB')
  crop.thumbnail((650,160))
  board=Image.new('RGB',(700,280),'white')
  stamp=logo.copy();stamp.thumbnail((600,105))
  board.paste(stamp,(50,15),stamp);board.paste(crop,((700-crop.width)//2,125))
  (HERE/'qa').mkdir(exist_ok=True)
  board.save(HERE/f'qa/{name}-logo.jpg',quality=94)
data['generated_unique']=len({a['source_sha256'] for a in data['assets']})
(HERE/'manifest.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(HERE/'data.js').write_text('window.CONTINUITY_V2 = '+json.dumps(data,ensure_ascii=False)+';\n',encoding='utf-8')
(HERE/'prompts.md').write_text('# V2 generation receipts\n\n'+'\n'.join('- ['+a['id']+'](receipts/'+a['id']+'.json)' for a in data['assets'])+'\n',encoding='utf-8')
for orientation in ['desktop','mobile']:
 tile=(560,315) if orientation=='desktop' else (252,448)
 board=Image.new('RGB',(tile[0]*3,tile[1]*2+64),(247,248,245));draw=ImageDraw.Draw(board)
 for index in range(6):
  sid=f'S{index+1:02d}'
  source=Image.open(HERE/f'keyframes/{sid}-{orientation}.webp')
  thumb=ImageOps.fit(source,tile)
  x=(index%3)*tile[0];y=(index//3)*(tile[1]+32)
  draw.text((x+10,y+8),f'{sid} / '+['CHINA','PACIFIC','USA ARRIVAL','USA STORAGE','USA PACKING','USA OUTBOUND'][index],fill='#182c39')
  board.paste(thumb,(x,y+32))
 board.save(HERE/f'qa/contact-{orientation}.jpg',quality=92)
print(json.dumps({'assets':len(data['assets']),'generated_unique':data['generated_unique'],'video_calls':0}))
