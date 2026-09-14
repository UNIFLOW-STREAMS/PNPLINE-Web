from pathlib import Path
from PIL import Image,ImageDraw
p=Path(__file__).resolve().parents[1]
d=Image.new('RGB',(1800,744),'#f7f8f5');m=Image.new('RGB',(1440,457),'#f7f8f5')
for i in range(6):
 sid=f'S0{i+1}';im=Image.open(p/f'keyframes/desktop/{sid}.jpg');im.thumbnail((580,326));x=(i%3)*600+10;y=(i//3)*372+30;d.paste(im,(x,y));ImageDraw.Draw(d).text((x,y-22),sid+' / DESKTOP',fill='#182c39')
 im=Image.open(p/f'keyframes/mobile/{sid}.jpg');im.thumbnail((230,409));x=i*240+5;m.paste(im,(x,30));ImageDraw.Draw(m).text((x,8),sid+' / MOBILE',fill='#182c39')
d.save(p/'qa/contact-desktop.jpg',quality=94);m.save(p/'qa/contact-mobile.jpg',quality=94)
