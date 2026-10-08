from pathlib import Path
from PIL import Image,ImageDraw,ImageOps
import json,math,subprocess
R=Path(__file__).resolve().parents[1];H=R/'pnpline-s3-camera-revision-handoff-v0.1';V=R/'review'
K=[216,278,330,380,422,450]
sheet=Image.new('RGB',(1440,310*6),'#edf0f3');d=ImageDraw.Draw(sheet)
for i,f in enumerate(K):
 y=i*310;d.text((8,y+5),f'K{i+1}: frame {f}, S3 +{(f-216)/12:.2f}s | Board / Before / After',fill='black')
 board=Image.open(H/f'references/s3-{i+1:02}.png').convert('RGB');boxes=[(18,85,1473,951),(18,85,1429,967),(18,84,1429,983),(18,84,1429,983),(18,115,1429,982),(18,115,1429,982)]
 images=[board.crop(boxes[i]),Image.open(V/f'before/f{f:04}.png'),Image.open(V/f'after/f{f:04}.png')]
 for j,im in enumerate(images):sheet.paste(ImageOps.pad(im,(480,280),color='#edf0f3'),(j*480,y+26))
sheet.save(V/'K1-K6-comparison.png')
for label,frames in [('destination-sequence',list(range(360,397,4))),('overtake-sequence',list(range(398,457,6)))]:
 im=Image.new('RGB',(1440,294*((len(frames)+2)//3)),'white');dd=ImageDraw.Draw(im)
 for i,f in enumerate(frames):
  x=i%3*480;y=i//3*294;dd.text((x+5,y+4),f'f{f} / S3 +{(f-216)/12:.2f}s',fill='black');im.paste(Image.open(V/f'after/f{f:04}.png').resize((480,270)),(x,y+24))
 im.save(V/(label+'.png'))
m=json.loads((R/'camera-before-after.json').read_text());base=json.loads((V/'baseline-full.json').read_text())['frames'];after=json.loads((V/'states-after.json').read_text())['frames']
im=Image.new('RGB',(1400,800),'#f5f7f9');dd=ImageDraw.Draw(im)
dd.text((25,15),'Camera paths: before orange / after blue / ship black. Fixed world, no asset edits.',fill='black')
for idx,(a,b,title) in enumerate([(0,2,'World X/Z (side)'),(0,1,'World X/Y (top)')]):
 x0=idx*700+30;y0=70;w=630;h=650
 allp=[[s[f][k][a][3],s[f][k][b][3]] for s in [base,after] for f in range(216,457) for k in ['camera','ship']]
 lo=[min(p[i] for p in allp) for i in range(2)];hi=[max(p[i] for p in allp) for i in range(2)];scale=min(w/(hi[0]-lo[0]),h/(hi[1]-lo[1]))
 def screen(p):return (x0+(p[0]-lo[0])*scale,y0+h-(p[1]-lo[1])*scale)
 for s,k,col in [(base,'camera','#cf7a22'),(after,'camera','#006dbe'),(after,'ship','#222222')]:dd.line([screen([s[f][k][a][3],s[f][k][b][3]]) for f in range(216,457)],fill=col,width=3)
 dd.text((x0,y0-24),title,fill='black')
 for i,f in enumerate(K):
  p=screen([after[f]['camera'][a][3],after[f]['camera'][b][3]]);dd.ellipse((p[0]-4,p[1]-4,p[0]+4,p[1]+4),fill='#006dbe');dd.text((p[0]+5,p[1]),f'K{i+1}',fill='#006dbe')
im.save(V/'camera-path.png')
im=Image.new('RGB',(1200,640),'white');dd=ImageDraw.Draw(im)
for j,(key,maxv,title) in enumerate([('distance',130,'Camera / ship distance (m)'),('ship_width',.8,'Ship projected horizontal span')]):
 y0=50+j*300;dd.text((30,y0-25),title,fill='black');dd.rectangle((50,y0,1150,y0+240),outline='#999999')
 vals=m['observations'];dd.line([(50+(v['frame']-216)/240*1100,y0+240-v[key]/maxv*240) for v in vals],fill='#006dbe',width=3)
 for f in [216,278,338,380,422,456]:x=50+(f-216)/240*1100;dd.line((x,y0,x,y0+240),fill='#dddddd');dd.text((x,y0+245),str(f),fill='black')
im.save(V/'tracking-metrics.png')
print('Review sheets and path plots created')
