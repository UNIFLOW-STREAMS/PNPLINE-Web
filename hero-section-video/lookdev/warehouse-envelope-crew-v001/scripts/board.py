from PIL import Image,ImageOps,ImageDraw,ImageFont
from pathlib import Path
R=Path(__file__).resolve().parents[1]/'review'
im=Image.new('RGB',(1600,550),'#F5F6F5');d=ImageDraw.Draw(im)
font=ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',22)
for x,num,label,fn in [(16,'01','미국 PNPLINE 창고','exterior.png'),(808,'02','피킹 · 포장 · 상차 피겨','crew-maquettes.png')]:
 p=Image.open(R/fn).convert('RGB');p=ImageOps.fit(p,(776,467),method=Image.Resampling.LANCZOS)
 im.paste(p,(x,14));d.text((x+4,494),num,font=font,fill='#007E9B');d.text((x+54,492),label,font=font,fill='#1B3441')
im.save(R/'warehouse-and-crew.jpg',quality=92,subsampling=0)

