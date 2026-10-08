import json,math
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
frames=[96,124,148,180,216]
sheet=Image.new('RGB',(1440,5*300+40),'#e9eef2');d=ImageDraw.Draw(sheet)
for i,title in enumerate(['STORYBOARD (scene area)','BASELINE v003','MASTER v004 / APPROVED S3 JOIN']):d.text((i*480+10,10),title,fill='black')
for row,f in enumerate(frames):
    y=40+row*300
    board=Image.open(ROOT/'inputs/boards'/f's2-0{row+1}.png').convert('RGB')
    board=board.crop((18,12,board.width-18,855))
    imgs=[board]+[Image.open(ROOT/'review'/mode/f'f{f:04}.png').convert('RGB') for mode in ['before','integrated']]
    for col,im in enumerate(imgs):
        cell=ImageOps.pad(im,(480,270),color='#17222a');sheet.paste(cell,(col*480,y));d.text((col*480+8,y+276),f'K{row+1} / frame {f}',fill='black')
sheet.save(ROOT/'review/K1-K5-comparison.png')
base=json.loads((ROOT/'review/baseline-full.json').read_text());cn=base['frames'][96]['ship']
def origin(m):return [m[i][3] for i in range(3)]
def xy(p):return [sum(cn[j][i]*(p[j]-cn[j][3]) for j in range(3)) for i in range(2)]
def transform(m,p):return [sum(m[i][j]*p[j] for j in range(3))+m[i][3] for i in range(3)]
canvas=Image.new('RGB',(1300,950),'#e6eff4');draw=ImageDraw.Draw(canvas)
def project(p):return (int(650+p[0]*11),int(400-p[1]*11))
for x in range(-30,36,5):draw.line([project((x,-43)),project((x,20))],fill='#ccd8df');draw.text(project((x,-44)),str(x),fill='black')
for y in range(-40,21,5):draw.line([project((-33,y)),project((35,y))],fill='#ccd8df');draw.text(project((-35,y)),str(y),fill='black')
draw.text((20,15),'ACTUAL WORLD PATH projected into fixed China port plane (metres)',fill='black')
draw.text((20,36),'Bow +X / stern -X; sea side -Y. Hull outlines at f96 and f216. No world relocation.',fill='black')
for f in [96,216]:
    sm=base['frames'][f]['ship']
    pts=[project(xy(transform(sm,[x,y,0]))) for x,y in [(-7,-2.6),(5.6,-2.6),(7,0),(5.6,2.6),(-7,2.6)]]
    draw.polygon(pts,fill='#bcc8cf',outline='black');draw.text(pts[0],f'SHIP {f}',fill='black')
for label,col in [('before','#77818b'),('limited','#d67728'),('integrated','#107fa6')]:
    data=base if label=='before' else json.loads((ROOT/'review'/f'states-{label}.json').read_text())
    pts=[project(xy(origin(r['camera']))) for r in data['frames'][96:253]]
    draw.line(pts,fill=col,width=4)
    for f in frames+[252]:
        r=data['frames'][f];p=xy(origin(r['camera']));t=xy(r['target']);a=project(p)
        draw.ellipse((a[0]-4,a[1]-4,a[0]+4,a[1]+4),fill=col);draw.text((a[0]+5,a[1]+3),f'{label} {f}',fill=col)
        if f in [148,216]:draw.line([a,project(t)],fill=col,width=1)
draw.text((20,910),'Lines to subject: sight direction at K3 and K5. Environment footprint is not drawn; scene is unchanged.',fill='black')
canvas.save(ROOT/'review/camera-path-top.png')
oblique=Image.new('RGB',(1300,950),'#e6eff4');od=ImageDraw.Draw(oblique)
def local3(p):return [sum(cn[j][i]*(p[j]-cn[j][3]) for j in range(3)) for i in range(3)]
def iso(p):return (int(490+17*(p[0]-.65*p[1])),int(670+8*(.35*p[0]+.6*p[1])-9*p[2]))
for x in range(-30,31,5):od.line([iso((x,-30,0)),iso((x,15,0))],fill='#c8d7df')
for y in range(-30,16,5):od.line([iso((-30,y,0)),iso((30,y,0))],fill='#c8d7df')
for f in [96,216]:
 sm=base['frames'][f]['ship']
 pts=[iso(local3(transform(sm,[x,y,.8]))) for x,y in [(-7,-2.6),(5.6,-2.6),(7,0),(5.6,2.6),(-7,2.6)]]
 od.polygon(pts,fill='#bdcbd3',outline='black');od.text(pts[0],f'SHIP {f}',fill='black')
for label,col in [('before','#77818b'),('limited','#d67728'),('integrated','#107fa6')]:
 data=base if label=='before' else json.loads((ROOT/'review'/f'states-{label}.json').read_text())
 pts=[iso(local3(origin(r['camera']))) for r in data['frames'][96:253]];od.line(pts,fill=col,width=4)
 for f in frames+[252]:
  r=data['frames'][f];a=iso(local3(origin(r['camera'])));od.ellipse((a[0]-4,a[1]-4,a[0]+4,a[1]+4),fill=col);od.text((a[0]+5,a[1]),f'{label} {f}',fill=col)
od.text((25,20),'OBLIQUE PATH VIEW / fixed China coordinates, including actual camera altitude',fill='black')
od.text((25,44),'Grey = baseline; orange = limited; blue = integrated. Includes approved join to f252. Grid is a reference plane.',fill='black')
oblique.save(ROOT/'review/camera-path-oblique.png')
data={mode:json.loads((ROOT/'review'/f'motion-{mode}.json').read_text()) for mode in ['limited','candidate','integrated']}
report={}
for mode,values in data.items():
    states=json.loads((ROOT/'review'/f'states-{mode}.json').read_text())
    changed=[a['frame'] for a,b in zip(base['frames'],states['frames']) if a['camera']!=b['camera'] or a['target']!=b['target']]
    report[mode]={'changed_frames':changed,'noncamera_equal':all(a['noncamera']==b['noncamera'] for a,b in zip(base['frames'],states['frames'])),'observations':values['observations'],'boundary':{}}
    for f in [96,216,252]:
        a=base['frames'][f];b=states['frames'][f]
        report[mode]['boundary'][f]={'position_delta':math.dist(origin(a['camera']),origin(b['camera'])),'target_delta':math.dist(a['target'],b['target']),'before':a,'after':b}
(ROOT/'review/camera-before-after.json').write_text(json.dumps(report,indent=2))
print(json.dumps({m:{'changed_range':[v['changed_frames'][0],v['changed_frames'][-1]],'noncamera_equal':v['noncamera_equal'],'B23_position_delta':v['boundary'][216]['position_delta']} for m,v in report.items()},indent=2))
