"""Summarize immutable scene survey and draw an annotated local-XY planning map."""
import json, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'review'
d=json.loads((OUT/'spatial-survey.json').read_text())
zones={'Beijing wing':[-59,-28,-10,52], 'Guangzhou wing':[30,62,3,48], 'Back connector':[-44,44,33,66]}
def gap(point,box):
    x,y,z=point;x0,x1,y0,y1=box
    return math.hypot(max(x0-x,0,x-x1),max(y0-y,0,y-y1))
def bboxgap(b,box):
    x0,x1,y0,y1=box;lo=b['min'];hi=b['max']
    return math.hypot(max(x0-hi[0],0,lo[0]-x1),max(y0-hi[1],0,lo[1]-y1))
early=[p for p in d['paths']if p['frame']<=253]
clearance={n:{'camera_xy_min':min(gap(r['camera']['position'],box)for r in early),
              'hull_xy_min':min(bboxgap(r['ship']['hull_bounds'],box)for r in early)}for n,box in zones.items()}
waves={n:o['bounds']for n,o in d['objects'].items()if n.startswith('SF_OCEAN_WAVE')and not o['hidden']and any(bboxgap(o['bounds'],b)==0 for b in zones.values())}
outer=[[-56,-10],[-60,5],[-60,38],[-51,53],[-31,62],[0,66],[31,62],[53,53],[63,38],[63,8],[58,3],[30,3],[30,1.7],[-28,1.7],[-28,-10]]
summary={'source_sha256':d['sha256'],'coordinate_system':'SF_CN_LAYOUT local, meters; +Y behind Shanghai, front ship channel -Y',
         'recommended_envelopes':zones,'outer_land_polygon_xy':outer,
         'core_mask_note':'Do not blanket-fill existing city basin/river. Preserve old core and use extension geometry plus shoreline overlap only.',
         'front_exclusions':'Keep new additions y>=-10 west of x=-28, and y>=3 east of x=30. Never extend front shipping waterway.',
         'connector_note':'Right coast stops at x23.045; bridge remaining apron x20..33, y>=4. Back mainland stops y32.535; start added back shelf around31..35.',
         'terrain_placement':{'ocean_center':d['ocean_origin_local'],'nominal_radius':140,
              'nominal_surface':'z = -140 + sqrt(140**2 - x**2 - (y+4.6)**2)',
              'actual_sampling':'Use downward BVH ray against EARTH_CONTINUOUS_OCEAN in SF_CN_LAYOUT coordinates; eastern harbor is smoothly raised relative to nominal sphere.',
              'new_land_height':'actual ocean height plus land thickness, smoothly blended to existing shoreline top1.249988 near old land. Derive normals from final land gradient, not faceted water normals.',
              'normal':'normalize((-dz/dx,-dz/dy,1)); orient building local+Z to this normal, yaw in local tangent plane.',
              'reference_title_bounds':d['group_bounds']['title']},
         'sampled_clearances_early_native_frames_0_253':clearance,
         'sample_interval_frames':3,'caveat':'Envelope XY gaps are conservative plan-view checks, not a substitute for final mesh/camera swept verification.',
         'decorative_water_curves_in_new_region':waves,
         'left_cloud_keepout':{'x':[-29.261,-26.230],'y':[11.50,14.38],'z':[5.85,9.23]},
         'preservation_required':'Original objects, meshes, materials, actions, camera optics and all actor/camera evaluated matrices must remain identical unless explicitly scoped affected-wave visibility exceptions.'}
(OUT/'spatial-recommendations.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
try:
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 from matplotlib.patches import Rectangle,Polygon
 fig,ax=plt.subplots(figsize=(15,12),dpi=150)
 grid=d['water_height_grid'];xs=sorted(set(p['xy'][0]for p in grid));ys=sorted(set(p['xy'][1]for p in grid))
 z=[[next(p['z']for p in grid if p['xy']==[x,y])for x in xs]for y in ys]
 cs=ax.contour(xs,ys,z,levels=[-35,-30,-25,-20,-15,-10,-5,0],colors='#acbccc',linewidths=.65);ax.clabel(cs,fontsize=8)
 ax.add_patch(Polygon(outer,facecolor='#e8ddb0',edgecolor='#aa8431',alpha=.45,lw=2,label='Proposed outer land envelope'))
 for n,o in d['objects'].items():
  if o['hidden']or n.startswith('SF_OCEAN_WAVE')or any(k in o['lineage']for k in ['A02_SHIP','A01_CONTAINER','W01_NEW_PALLET']):continue
  b=o['bounds'];a=b['min'];c=b['max']
  if c[2]<-20:continue
  color='#a32936'if n.startswith('SF_CHINA_')else '#44949f'if n.startswith('PORT_')else '#626a72'
  ax.add_patch(Rectangle((a[0],a[1]),c[0]-a[0],c[1]-a[1],color=color,alpha=.18,lw=0))
 for n,b in waves.items():
  a=b['min'];c=b['max'];ax.add_patch(Rectangle((a[0],a[1]),c[0]-a[0],c[1]-a[1],fill=False,ec='#38a5d3',ls=':',lw=.8))
 for n,b in zones.items():
  ax.add_patch(Rectangle((b[0],b[2]),b[1]-b[0],b[3]-b[2],fill=False,ec='#997429',ls='--',lw=1))
  ax.text((b[0]+b[1])/2,(b[2]+b[3])/2,n,ha='center',va='center',fontsize=11,color='#634b18',bbox={'fc':'white','alpha':.65,'ec':'none'})
 ax.plot([p['camera']['position'][0]for p in early],[p['camera']['position'][1]for p in early],color='#9b47ad',lw=2,label='Existing camera path f0–253')
 ax.plot([p['ship']['position'][0]for p in early],[p['ship']['position'][1]for p in early],color='#115699',lw=2,label='Existing ship path f0–253')
 for f in [0,104,165,216,253]:
  p=next(r for r in early if r['frame']==f)
  for label,col in [('camera','#9b47ad'),('ship','#115699')]:
   x,y,z=p[label]['position'];ax.plot(x,y,'o',ms=3,color=col);ax.annotate(str(f),(x,y),xytext=(4,-10),textcoords='offset points',fontsize=8,color=col)
 ax.axhline(-15,color='#a94a3c',ls=':',lw=1);ax.text(-65,-18,'Front ship channel: keep open',fontsize=10,color='#a94a3c')
 ax.set(xlim=(-70,120),ylim=(-82,75),xlabel='SF_CN_LAYOUT local X (m)',ylabel='SF_CN_LAYOUT local Y (m)',title='China expansion spatial survey — immutable integrated scene 1aee6c14\nWater contours are actual static ocean heights; red = CHINA title, cyan = terminal')
 ax.set_aspect('equal');ax.grid(alpha=.2);ax.legend(loc='lower left');fig.tight_layout();fig.savefig(OUT/'spatial-topmap.png');plt.close(fig)
except ImportError:
 from PIL import Image,ImageDraw,ImageFont
 im=Image.new('RGB',(1600,1450),'#f7f8fa');draw=ImageDraw.Draw(im)
 def pt(x,y):return (int(90+(x+70)*7.4),int(110+(75-y)*7.4))
 font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',19)
 small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',14)
 draw.text((70,30),'China expansion — local XY survey | immutable scene 1aee6c14',font=font,fill='#20334b')
 draw.text((70,60),'Yellow: proposed land  |  Red: CHINA title  |  Cyan: terminal  |  Blue: ship  |  Purple: camera',font=small,fill='#40536b')
 draw.polygon([pt(*p)for p in outer],fill='#eee4bb',outline='#a68b41',width=3)
 for x in range(-70,121,10):
  draw.line([pt(x,-82),pt(x,75)],fill='#dee2e7');draw.text(pt(x,-84),str(x),font=small,fill='#586779')
 for y in range(-80,76,10):
  draw.line([pt(-70,y),pt(120,y)],fill='#dee2e7');p=pt(-75,y);draw.text(p,str(y),font=small,fill='#586779')
 for n,o in d['objects'].items():
  if o['hidden']or n.startswith('SF_OCEAN_WAVE')or any(k in o['lineage']for k in ['A02_SHIP','A01_CONTAINER','W01_NEW_PALLET']):continue
  b=o['bounds'];a=b['min'];c=b['max']
  color='#ac4657'if n.startswith('SF_CHINA_')else '#49949f'if n.startswith('PORT_')else '#7d8792'
  if c[2]<-20:continue
  draw.rectangle([pt(a[0],c[1]),pt(c[0],a[1])],outline=color)
 for n,b in waves.items():
  a=b['min'];c=b['max'];draw.rectangle([pt(a[0],c[1]),pt(c[0],a[1])],outline='#70bce0')
 for n,b in zones.items():
  draw.rectangle([pt(b[0],b[3]),pt(b[1],b[2])],outline='#a68b41',width=2)
  draw.text(pt(b[0]+1,(b[2]+b[3])/2),n,font=font,fill='#594c28')
 for label,color in [('camera','#9947ab'),('ship','#145e9d')]:
  draw.line([pt(*p[label]['position'][:2])for p in early],fill=color,width=4)
  for f in [0,104,165,216,253]:
   p=next(r for r in early if r['frame']==f);x,y=pt(*p[label]['position'][:2]);draw.ellipse((x-3,y-3,x+3,y+3),fill=color);draw.text((x+5,y+3),str(f),font=small,fill=color)
 draw.text(pt(-65,-18),'Keep front shipping channel open',font=font,fill='#a64b3c')
 draw.text((70,1370),'X → metres. Y ↑ behind city. Paths use native 30fps f0–253 (sampled every3 frames).',font=font,fill='#20334b')
 im.save(OUT/'spatial-topmap.png')
print(json.dumps({'clearances':clearance,'waves':list(waves),'summary':str(OUT/'spatial-recommendations.json')},indent=2))
