from pathlib import Path
from PIL import Image,ImageDraw
import sys
R=Path(__file__).resolve().parents[1];folder=R/'review'/sys.argv[1];files=sorted(folder.glob('*.png'));files=[p for p in files if p.name!='contact-sheet.png']
im=Image.new('RGB',(1440,294*((len(files)+2)//3)),'white');d=ImageDraw.Draw(im)
for i,p in enumerate(files):
 x=i%3*480;y=i//3*294;im.paste(Image.open(p).resize((480,270)),(x,y+24));d.text((x+4,y+4),p.stem,fill='black')
im.save(folder/'contact-sheet.png')
