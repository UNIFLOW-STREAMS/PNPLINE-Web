"""Extract the user's lithographic ink and extend colour beyond the cut contours for mipmaps."""
from pathlib import Path
from collections import deque
import sys
from PIL import Image,ImageFilter,ImageDraw
r=Path(__file__).resolve().parents[1]
im=Image.open(sys.argv[1]).convert('RGB')
assert im.size==(736,1040)
box=(98,18,354,792)
im=im.crop(box)
filtered=im.filter(ImageFilter.MedianFilter(5))
mask=Image.new('1',im.size)
draw=ImageDraw.Draw(mask)
# A narrow safety silhouette excludes lettering and the plane in the original poster.
poly=[(104,69),(118,67),(111,47),(120,28),(151,20),(144,48),(159,36),(156,55),(146,68),(158,68),(159,86),(141,94),(143,118),(136,134),(139,192),(147,232),(162,278),(179,258),(183,242),(141,241),(145,209),(178,221),(169,185),(201,215),(212,164),(218,215),(252,184),(237,218),(282,207),(246,229),(291,237),(287,241),(241,243),(246,284),(258,349),(266,391),(283,416),(290,426),(305,394),(351,415),(340,438),(343,447),(338,476),(325,478),(311,518),(300,536),(289,536),(275,516),(279,579),(302,791),(120,791),(120,95),(103,86)]
draw.polygon([(x-box[0],y-box[1]) for x,y in poly],fill=1)
w,h=im.size; src=im.load(); f=filtered.load(); m=mask.load()
out=Image.new('RGB',(w,h));dst=out.load();seen=bytearray(w*h);q=deque()
for y in range(h):
 for x in range(w):
  rr,g,b=f[x,y]
  gold=y+18<69 and rr-g>26
  if m[x,y] and ((g-rr>30 and g-b>12 and rr<182) or gold):
   dst[x,y]=src[x,y];seen[y*w+x]=1;q.append((x,y))
while q:
 x,y=q.popleft()
 for a,b in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
  if 0<=a<w and 0<=b<h and not seen[b*w+a]:
   dst[a,b]=dst[x,y];seen[b*w+a]=1;q.append((a,b))
out.save(r/'liberty-ink.png')
