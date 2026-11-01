"""Standalone source footprint maps, arc-distance XY, no Blender writes."""
import json,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'review';d=json.loads((OUT/'us-survey.json').read_text())
font='C:/Windows/Fonts/arial.ttf';bold='C:/Windows/Fonts/arialbd.ttf'
F=lambda n,b=False:ImageFont.truetype(bold if b else font,n)
def plot(filename,ext,size=(1700,1250)):
 im=Image.new('RGB',size,'#f1f5f5');g=ImageDraw.Draw(im);x0,x1,y0,y1=ext;L=100;T=105;W=size[0]-170;H=size[1]-190
 sx=W/(x1-x0);sy=H/(y1-y0)
 def xy(p):return (L+(p[0]-x0)*sx,T+(y1-p[1])*sy)
 def poly(points,fill,outline=None,width=1):
  if len(points)>2:g.polygon([xy(p)for p in points],fill=fill,outline=outline,width=width)
 for r in d['terrain']:
  loops=r.get('boundary_loops_parameter')or[r['footprint_hull_parameter']]
  for p in loops:poly(p,'#e0ded1','#a1a39b',2)
 for x in range(math.ceil(x0/10)*10,int(x1)+1,10):
  a,b=xy((x,y0)),xy((x,y1));g.line([a,b],fill='#c9cfcc');g.text((a[0]-12,a[1]+13),str(x),font=F(17),fill='#435362')
 for y in range(math.ceil(y0/10)*10,int(y1)+1,10):
  a,b=xy((x0,y)),xy((x1,y));g.line([a,b],fill='#c9cfcc');g.text((L-45,a[1]-8),str(y),font=F(17),fill='#435362')
 # Title plane footprints are pale violet; source buildings show physical height.
 for r in d['groups']:
  if r['category']=='other_static':continue
  h=r['height_above_surface'];cat=r['category']
  color='#e6d6ee'if cat=='title'else'#bdcebd'if cat in {'civic','liberty'}else'#d37c64'if h>24 else'#cfb98c'if h>14 else'#99b1bb'
  poly(r['footprint_parameter'],color,'#647481')
 for r in d['hero_candidates']:
  poly(r['footprint_parameter'],None,'#b82160',4)
  p=xy(r['anchor_parameter']);name='Rear One WTC'if r['root'].startswith('CE_')else'Empire State'if 'CENTRAL'in r['root']else'Core One WTC'
  tx,ty=(p[0]+20,p[1]-22)if name!='Core One WTC'else(p[0]+20,p[1]+30)
  g.line([p,(tx,ty+12)],fill='#8f1347',width=2);g.text((tx,ty),f'{name} {r["height_above_surface"]:.1f}m',font=F(22,True),fill='#8f1347')
 labels=[r for r in d['groups']if r['category']=='expansion_building'and r['height_above_surface']>24 and x0<r['anchor_parameter'][0]<x1 and y0<r['anchor_parameter'][1]<y1]
 for i,r in enumerate(sorted(labels,key=lambda a:a['anchor_parameter'][1])):
  p=xy(r['anchor_parameter']);name=r['root'].replace('CE_REAR_','').replace('_ROOT','');text=f'{name} {r["height_above_surface"]:.1f}'
  offset=-38 if i%2 else 19;g.text((p[0]-30,p[1]+offset),text,font=F(16,True),fill='#6f2725')
 for r in d['groups']:
  if r['category']=='title':
   p=xy(r['anchor_parameter']);g.text((p[0]-8,p[1]-12),r['root'].split('_')[2],font=F(34,True),fill='#7c6585')
 for r in d['free_2m_square_candidate_centers']:
  p=xy(r['xy']);g.ellipse((p[0]-2,p[1]-2,p[0]+2,p[1]+2),fill='#226c37')
 plot_crop=im.crop((L,T,L+W,T+H));im=Image.new('RGB',size,'#f1f5f5');im.paste(plot_crop,(L,T));g=ImageDraw.Draw(im)
 for x in range(math.ceil(x0/10)*10,int(x1)+1,10):
  a=xy((x,y0));g.text((a[0]-12,a[1]+13),str(x),font=F(17),fill='#435362')
 for y in range(math.ceil(y0/10)*10,int(y1)+1,10):
  a=xy((x0,y));g.text((L-45,a[1]-8),str(y),font=F(17),fill='#435362')
 g.rectangle((L,T,L+W,T+H),outline='#45616b',width=2)
 g.text((40,22),'US source: landmark hierarchy and actual radial footprints',font=F(29,True),fill='#182e3f')
 g.text((40,63),'Arc-distance XY in US_FRAME | source c0f7d784 | terrain radius140.68m | +Y rear',font=F(20),fill='#445c67')
 g.text((40,size[1]-48),'Blue-gray <14m   Sand14-24m   Red >24m   Violet USA letters   Magenta main/rear WTC + Empire   Green candidate centers',font=F(19),fill='#324a56')
 im.save(OUT/filename)
plot('us-core-height-map.png',(-40,65,15,85))
plot('us-all-districts-map.png',(-45,115,-95,100),(1550,1800))
