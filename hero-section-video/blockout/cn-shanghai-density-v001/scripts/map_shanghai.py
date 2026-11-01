"""Annotated radial footprint/water-mask diagram from the read-only survey."""
import json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'review';d=json.loads((OUT/'shanghai-survey.json').read_text())
im=Image.new('RGB',(1600,1370),'#f5f4ee');draw=ImageDraw.Draw(im)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',19);small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',14)
def p(x,y):return (int(90+(x+29)*31),int(110+(34-y)*31))
draw.text((65,25),'Shanghai density planning — exact current river and radial footprints',font=font,fill='#25384a')
draw.text((65,56),'Source f0f07fcb | cream = dry land; blue = protected water; red = CHINA title; purple = 3 hero towers',font=small,fill='#506070')
for x in range(-25,16,5):
 draw.line([p(x,0),p(x,34)],fill='#dedfd9');draw.text(p(x,-.7),str(x),font=small,fill='#506070')
for y in range(0,35,5):
 draw.line([p(-29,y),p(16,y)],fill='#dedfd9');draw.text(p(-30.5,y),str(y),font=small,fill='#506070')
draw.polygon([p(*q)for q in d['water']['outer_boundary_xy']],fill='#224c63')
draw.polygon([p(*q)for q in d['water']['dry_island_boundary_xy']],fill='#eee9d8',outline='#e8d8ae',width=2)
heroes={'SF_OPEN_TOWER','SF_STEP_TOWER','SF_TALLEST_TOWER'}
for r in d['all_rigid_cluster_footprints']:
 poly=r['radial_footprint_xy']
 if max(q[0]for q in poly)<-29 or min(q[0]for q in poly)>16 or max(q[1]for q in poly)<0 or min(q[1]for q in poly)>34:continue
 n=r['id'];cat=r['category']
 color='#9ca69d'if cat in {'tree','shrub'}else '#8d9498'
 if n.startswith('SF_CHINA_'):color='#a75340'
 elif n in heroes:color='#7d4a9e'
 elif n=='SF_SPHERE_TOWER':color='#199aa8'
 elif cat=='floating_cloud':color='#d2d7d7'
 draw.polygon([p(*q)for q in poly],fill=color)
for zone,points in d['candidate_fill_samples_for_1m_by_0_8m_footprints'].items():
 for xy in points:
  x,y=p(*xy);draw.ellipse((x-1,y-1,x+1,y+1),fill='#b98a22')
labels={'SF_SPHERE_TOWER':('Oriental Pearl (preserve)',(-14,18.8)),'SF_OPEN_TOWER':('SWFC',(-8.5,24.5)),
 'SF_STEP_TOWER':('Jin Mao',(-5.8,17.8)),'SF_TALLEST_TOWER':('Shanghai Tower',(1.0,24.2))}
for r in d['selected_architecture']:
 if r['id']not in labels:continue
 text,xy=labels[r['id']];anchor=r['ground_anchor'];draw.line([p(*anchor[:2]),p(*xy)],fill='#403d51',width=2);draw.text(p(*xy),text,font=font,fill='#403d51')
draw.line([p(-29,1.7),p(16,1.7)],fill='#b1643e',width=2)
draw.text(p(-27,1.5),'Existing port boundary — keep new footprints north of y=2.1',font=small,fill='#9e5033')
draw.text((65,1240),'Gold dots: surveyed candidate centres for 1.0 × 0.8m footprints; do not place every dot.',font=font,fill='#5c5034')
draw.text((65,1274),'Use actual water BVH + architecture masks for final footprints. Buildings and trees must retain radial up.',font=font,fill='#25384a')
draw.text((65,1310),'X → and Y ↑ are SF_CN_LAYOUT local metres; geometry is projected radially to the shared spherical ground.',font=small,fill='#506070')
im.save(OUT/'shanghai-water-footprints.png')
print(OUT/'shanghai-water-footprints.png')
