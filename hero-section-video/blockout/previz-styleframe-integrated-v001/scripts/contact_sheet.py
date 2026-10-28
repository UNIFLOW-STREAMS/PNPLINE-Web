from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
R=Path(__file__).resolve().parents[1];files=sorted((R/'review/stills').glob('*.png'));canvas=Image.new('RGB',(1440,4*((len(files)+3)//4)*0+((len(files)+3)//4)*225),(20,27,33));d=ImageDraw.Draw(canvas)
for i,p in enumerate(files):
 im=Image.open(p).convert('RGB');im.thumbnail((360,202));x=(i%4)*360;y=(i//4)*225;canvas.paste(im,(x,y));d.text((x+8,y+205),p.stem,fill='white')
canvas.save(R/'review/S1-S7-contact-sheet.jpg',quality=92)
