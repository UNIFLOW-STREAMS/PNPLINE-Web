from pathlib import Path
import json,csv,sys
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));from motion import TimeMap
cfg=json.loads((R/'config.json').read_text());boards={};scroll={};table=[]
for variant in ['A','B']:
 m=TimeMap(1392,cfg['easing'],cfg['compression_B'] if variant=='B' else []);tm=json.loads((R/f'time-map-{variant}.json').read_text())
 boards[variant]={'blend_sha256':tm['blend_sha256'],'panels':[{'panel':f'S5-{i+1:02d}','source_frame':f,'exact_output_frame':m.forward(f),'nearest_video_frame':round(m.forward(f)),'output_second':m.forward(f)/24,'note':'Exact composition comparison uses fractional output frame; integer video sample is nearest.'} for i,f in enumerate(cfg['storyboard_source_frames'])]}
 scroll[variant]={'blend_sha256':tm['blend_sha256'],'normalization':'0..1 across first-to-last frame time; final frame exposure adds1/24s to MP4 duration','rows':[{'source_frame':i,'output_frame':m.forward(i),'output_second':m.forward(i)/24,'scroll_progress':m.forward(i)/m.output_end} for i in range(1393)]}
 for name,f in cfg['events'].items():table.append({'variant':variant,'event':name,'source_frame':f,'original_second_12fps':f/12,'existing_second_24fps':f/24,'output_frame':m.forward(f),'output_second':m.forward(f)/24,'scroll_progress':m.forward(f)/m.output_end})
(R/'s5-storyboard-map.json').write_text(json.dumps(boards,indent=2),encoding='utf8');(R/'scroll-progress-map.json').write_text(json.dumps(scroll,indent=2),encoding='utf8')
with (R/'event-map.csv').open('w',newline='',encoding='utf-8-sig') as out:
 w=csv.DictWriter(out,fieldnames=list(table[0]));w.writeheader();w.writerows(table)
for variant in ['A','B']:
 tm=json.loads((R/f'time-map-{variant}.json').read_text())
 with (R/f'time-map-{variant}.csv').open('w',newline='',encoding='utf-8-sig') as out:
  w=csv.DictWriter(out,fieldnames=list(tm['rows'][0]));w.writeheader();w.writerows(tm['rows'])
print('Maps written; exact fractional frame and nearest video frame distinguished.')
