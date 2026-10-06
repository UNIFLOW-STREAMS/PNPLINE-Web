from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
files=sorted((ROOT/'review'/'playback').glob('playing-*.png'))
for start in range(0,len(files),20):
    chunk=files[start:start+20]
    canvas=Image.new('RGB',(1280,1000),(235,239,241));draw=ImageDraw.Draw(canvas)
    for i,f in enumerate(chunk):
        x=i%4*320;y=i//4*200
        with Image.open(f) as im:canvas.paste(im.resize((320,180)),(x,y+20))
        draw.text((x+5,y+3),f.stem+' seconds / actual 1x playback',fill=(20,30,40))
    canvas.save(ROOT/'review'/f'playback-sheet-{start//20+1:02}.jpg',quality=92)
print('playback screenshots:',len(files),'sheets:',(len(files)+19)//20)
