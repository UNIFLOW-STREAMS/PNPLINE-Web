"""Match the recorded viewport to output frames using cyan geometry contours."""
import numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[1]
a=np.fromfile(R/'review/current.rgb',dtype=np.uint8).reshape(-1,90,160,3).astype(float)
b=np.fromfile(R/'review/user.rgb',dtype=np.uint8).reshape(-1,90,160,3).astype(float)
def mask(p):
 r,g,b=p[...,0],p[...,1],p[...,2]
 m=((b>r*1.22)&(g>r*1.12)&(b-r>15)).astype(float)
 m[:,:5]=0
 return m
a,b=mask(a),mask(b)
for i,x in enumerate(b):
 losses=((a-x)**2).mean(axis=(1,2));rank=losses.argsort()[:3]
 print(round(i/3,3),[(int(k)+300,round(float(losses[k]),4)) for k in rank])
