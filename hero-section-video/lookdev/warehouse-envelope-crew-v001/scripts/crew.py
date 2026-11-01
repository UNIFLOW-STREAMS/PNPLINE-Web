"""Painted scale figures. Rigid sculpted modules articulate at organic joints."""
import math,json,bpy
from pathlib import Path
from mathutils import Vector,Matrix,Quaternion
from shipkit import Parts,finish
from mathutils.geometry import tessellate_polygon
V=Vector
def mats():
 out={}
 for k,h,r,m in [
 ('Ocean twill','147DA0',.63,.02),('Blue seam','07546F',.68,0),('Ink navy','213444',.7,0),('Navy canvas','2F4858',.79,0),
 ('Piping','61D2E1',.49,.08),('Silver tape','C5D3CB',.49,.13),('Boot leather','413C37',.53,0),('Rubber outsole','273137',.78,0),
 ('Buckle','8F9A9D',.35,.55),('Warm skin','C89171',.64,0),('Golden skin','D5A384',.63,0),('Umber skin','AC775C',.64,0),
 ('Hair','3D302E',.71,0),('Espresso','443A34',.80,0),('Petrol glove','364D58',.79,0),('Light shell','E5E7D9',.38,.05),('White patch','ECF2EE',.57,0),
 ('Signal amber','F5BD5F',.45,0),('Screen','4E9AAB',.33,.17),('Label','E5D6AB',.74,0)]:
  a=finish(k,h,r,m);a.name='Crew | '+k;out[k]=a
 return out
def loft(p,levels,m,n=24,power=1):
 # z, half width, half depth, x offset, y offset
 vv=[];faces=[]
 for level in levels:
  z,w,d=level[:3];cx=level[3] if len(level)>3 else 0;cy=level[4] if len(level)>4 else 0
  for i in range(n):
   cs=math.cos(math.tau*i/n);sn=math.sin(math.tau*i/n)
   vv.append((cx+math.copysign(abs(cs)**power,cs)*w,cy+math.copysign(abs(sn)**power,sn)*d,z))
 for j in range(len(levels)-1):
  for i in range(n):
   a=j*n+i;b=j*n+(i+1)%n;faces.append((a,b,b+n,a+n))
 faces+=[tuple(reversed(range(n))),tuple(range(len(vv)-n,len(vv)))]
 p.add(vv,faces,m,True)
def graphic(p,curves,x,y,z,w,m0,m1,back=False):
 # Source logo outlines directly modelled as miniature cloth transfers.
 for i,curve in enumerate(curves):
  xy=[V(((a-749.5)/1401*w,0,(200-b)/1401*w)) for a,b in curve]
  pts=[(x+(-pt.x if back else pt.x),y,z+pt.z) for pt in xy]
  tris=tessellate_polygon([xy]);p.add(pts,tris,m0 if i<3 else m1)
def empty(name,parent,col):
 o=bpy.data.objects.new(name,None);col.objects.link(o);o.parent=parent;o.empty_display_size=.035;return o
def cap(p,M,role):
 # Hat brim is an extended elliptical bill; crew lead wears a ribbed short-peak hard hat.
 hard=role=='Load';top=M['Light shell'] if hard else M['Ocean twill'];edge=M['Ink navy']
 p.oval((0,-.059,.797),(.136,.177,.013),edge,32,8)
 p.oval((0,-.057,.804),(.138,.18,.012),top,32,8)
 loft(p,[(.786,.129,.118),(.80,.141,.131),(.84,.138,.13),(.884,.118,.106),(.908,.08,.071),(.918,.02,.027)],top,32)
 if hard:
  for x in [-.044,0,.044]:p.pipe([(x,-.097,.864),(x,-.053,.903),(x,.05,.903),(x,.10,.861)],.007,top,8)
 else:
  p.oval((0,0,.918),(.016,.016,.008),edge)
  for sg in [-1,1]:p.pipe([(sg*.102,-.084,.821),(sg*.083,-.067,.882),(sg*.01,-.014,.916)],.0029,M['Blue seam'],7)
 p.box((0,-.127,.837),(.073,.010,.027),edge)
 p.box((-.016,-.134,.837),(.029,.003,.009),M['Piping']);p.box((.016,-.134,.837),(.026,.003,.009),M['White patch'])
def build_figure(role,base,C,M,curves):
 def part(label,parent=base):return Parts('Figure '+role+' | '+label,parent,C)
 def raw(label,parent):return empty('Figure '+role+' | '+label,parent,C)
 chest=raw('body pivot',base)
 p=part('Work shirt, vest and face',chest);s=M[{'Pick':'Golden skin','Pack':'Umber skin','Load':'Warm skin'}[role]]
 # Pelvis/seat and waistband, tapered zip work gilet over navy polo.
 loft(p,[(-.085,.13,.10),(-.02,.159,.117),(.075,.166,.119),(.12,.153,.106)],M['Navy canvas'],24,.85)
 loft(p,[(.055,.165,.12),(.084,.166,.119)],M['Ink navy'],24,.83)
 p.box((0,-.121,.072),(.058,.016,.029),M['Buckle'])
 torso=[(.092,.160,.112),(.15,.172,.119),(.25,.175,.117),(.37,.196,.135),(.431,.224,.133),(.472,.197,.105),(.491,.120,.085)]
 loft(p,torso,M['Ocean twill'],32,.83)
 loft(p,[(.096,.163,.115),(.113,.167,.117)],M['Blue seam'],32,.84)
 for x in [-.099,.099]:
  p.box((x,-.129,.223),(.086,.014,.071),M['Blue seam']);p.box((x,-.140,.253),(.09,.008,.012),M['Piping'])
 # Horizontal reflective band and dark shoulder yoke.
 loft(p,[(.296,.190,.13),(.312,.191,.131)],M['Silver tape'],32,.8)
 loft(p,[(.437,.224,.134),(.466,.204,.116),(.488,.124,.088)],M['Ink navy'],32,.84)
 p.pipe([(0,-.119,.112),(0,-.120,.24),(0,-.138,.36),(0,-.132,.43),(0,-.095,.474)],.006,M['Ink navy'],8)
 p.box((.002,-.14,.413),(.011,.012,.023),M['Buckle'])
 for sg in [-1,1]:
  p.add([(sg*.021,-.124,.432),(sg*.096,-.107,.489),(sg*.05,-.076,.50)],[(0,1,2)],M['Navy canvas'])
 # Sewn-on chest tab, plus larger official two-tone mark on rear yoke.
 p.box((-.099,-.133,.387),(.117,.012,.030),M['Ink navy'])
 graphic(p,curves,-.099,-.140,.387,.107,M['Piping'],M['White patch'])
 p.box((0,.135,.385),(.255,.014,.055),M['Ink navy'])
 graphic(p,curves,0,.143,.385,.234,M['Piping'],M['White patch'],True)
 p.rod((0,.003,.474),(0,.002,.575),.071,s,18)
 # Contoured jaw, cheeks, brow and brow-to-nose bridge. Deliberately painted-scale eyes.
 loft(p,[(.538,.048,.065,0,-.020),(.557,.077,.09,0,-.017),(.593,.103,.104,0,-.009),(.641,.118,.109),(.686,.126,.119),(.746,.12,.12),(.79,.109,.113),(.824,.094,.097),(.843,.05,.065)],s,32)
 for sg in [-1,1]:
  p.oval((sg*.12,-.001,.671),(.023,.026,.041),s,18,10)
  p.oval((sg*.050,-.112,.682),(.015,.006,.006),M['Espresso'],16,7)
  p.pipe([(sg*.032,-.116,.708),(sg*.056,-.111,.714),(sg*.073,-.103,.707)],.0038,M['Espresso'],8)
 p.oval((0,-.117,.654),(.026,.028,.031),s,20,10)
 p.pipe([(-.025,-.107,.605),(0,-.112,.603),(.025,-.107,.605)],.0024,M['Espresso'],6)
 p.oval((0,.057,.74),(.119,.08,.078),M['Hair'],24,12)
 if role=='Pack':p.oval((0,.125,.684),(.068,.066,.060),M['Hair'],20,12)
 cap(p,M,role);p.done()
 # Each limb is sculpted down its own positive Z; IK aims that axis between joints.
 def segment(label,shape,material,rings=None):
  p=part(label)
  if label.endswith('trouser calf'):p.oval((0,0,.021),(.077,.079,.175),material,20,12)
  if label.endswith('polo sleeve'):p.oval((0,0,.081),(.071,.074,.225),material,20,12)
  if label.endswith('cuff and forearm'):p.oval((0,0,.028),(.053,.053,.130),material,20,12)
  loft(p,shape,material,20,.90)
  if rings:
   for r,ma in rings:loft(p,r,ma,20,.9)
  return p.done()
 limbs={}
 for sg in (-1,1):
  l='L' if sg<0 else 'R'
  thigh=segment(l+' trouser thigh',[(0,.080,.087),(.14,.099,.104),(.42,.102,.095),(.72,.089,.084),(.99,.076,.075)],M['Navy canvas'])
  shin=segment(l+' trouser calf',[(0,.075,.073),(.12,.084,.081),(.33,.085,.085),(.81,.061,.065),(.98,.063,.069)],M['Ink navy'],[([(.86,.064,.067),(.91,.066,.068)],M['Blue seam'])])
  p=part(l+' lace-up safety boot')
  loft(p,[(.010,.086,.139,0,-.036),(.028,.091,.15,0,-.04),(.052,.089,.148,0,-.04)],M['Rubber outsole'],24,.68)
  loft(p,[(.048,.088,.148,0,-.04),(.08,.087,.145,0,-.04),(.106,.084,.13,0,-.025),(.127,.072,.081),(.168,.065,.068)],M['Boot leather'],24,.84)
  for jj in range(3):p.box((0,-.080-jj*.011,.124-jj*.004),(.058,.009,.007),M['Navy canvas'])
  boot=p.done()
  upper=segment(l+' polo sleeve',[(0,.060,.063),(.12,.082,.083),(.31,.083,.087),(.71,.069,.071),(.91,.056,.06),(1,.049,.05)],M['Ink navy'],[([(.63,.074,.075),(.68,.074,.075)],M['Piping'])])
  fore=segment(l+' cuff and forearm',[(0,.050,.049),(.16,.062,.058),(.38,.061,.057),(.85,.041,.039),(1,.037,.036)],s,[([(.78,.046,.047),(.97,.040,.04)],M['Petrol glove'])])
  p=part(l+' grip glove')
  p.oval((0,0,.005),(.048,.045,.065),M['Petrol glove'],20,10)
  p.oval((-sg*.040,-.006,.022),(.022,.024,.037),M['Petrol glove'],14,8)
  hand=p.done()
  limbs[sg]=(thigh,shin,boot,upper,fore,hand)
 if role=='Pick':
  p=part('Handheld RF reader');p.box((0,0,0),(.075,.079,.145),M['Ink navy']);p.box((0,-.015,.067),(.101,.128,.079),M['Petrol glove'])
  p.box((0,-.018,.108),(.065,.073,.005),M['Screen']);p.box((0,-.082,.079),(.067,.007,.017),M['Signal amber'])
  prop=p.done()
 elif role=='Pack':
  p=part('Tape gun');p.rod((-.036,0,0),(.036,0,0),.064,M['Label'],24);p.rod((-.038,0,0),(.038,0,0),.028,M['Ink navy'],20);p.box((0,-.055,-.035),(.081,.119,.044),M['Ocean twill']);p.box((0,-.102,-.058),(.080,.018,.019),M['Buckle'])
  prop=p.done()
 else:prop=None
 return chest,limbs,prop
def V3(p):return V(tuple(p))
def RR(a):return Matrix.Rotation(a,3,'Z')
def solve(a,b,L1,L2,hint):
 d=b-a;n=d.normalized();hh=hint-n*hint.dot(n)
 if hh.length<1e-5:hh=V((1,0,0))-n*n.x
 D=max(.01,d.length)
 aa=max(.015,min(D-.006,(D*D+L1*L1-L2*L2)/(2*D)));bb=math.sqrt(max(.00014,L1*L1-aa*aa))
 return a+n*aa+hh.normalized()*bb
def orient(obj,p,q,sc=None):
 obj.location=p;obj.rotation_mode='QUATERNION';q=q.copy()
 if obj.get('prev_quat') is not None:q.make_compatible(Quaternion(obj['prev_quat']))
 obj.rotation_quaternion=q;obj['prev_quat']=list(q)
 if sc is not None:obj.scale=sc
def segmentpose(o,a,b):
 v=b-a;orient(o,a,v.to_track_quat('Z','Y'),(1,1,max(v.length,.01)))
def configure(role,bundle,target=None,frame=None):
 chest,limbs,prop=bundle
 # Canonical figurine faces -Y. The loader turns and rocks forward with the old support.
 if role=='Load':
  tgt,hands=target
  front=V((tgt.x,tgt.y,0));dist=max(.01,front.length);front.normalize()
  yaw=math.atan2(front.x,-front.y)
  rt=RR(yaw);side=rt@V((1,0,0))
  hh=min(h.z for h in hands);reach=min(1.2,max(0,(dist-.44)/.94));low=min(1.,max(0,(.745-hh)/.70))
  pelvis=front*(.10+max(0,dist-.51)*.77)+V((0,0,.82-.39*low))
  tilt=.20+.69*low+.08*reach
  feet=[front*(.04+max(0,dist-.66)*.77+sg*(.082+.072*reach))+side*sg*.136 for sg in (-1,1)]
  # Anatomical palm centers sit on top of the two original carrier grip positions.
  goals=[h+V((0,0,.067)) for h in hands]
 elif role=='Pick':
  yaw=math.pi-.27;rt=RR(yaw);front=rt@V((0,-1,0));side=rt@V((1,0,0));tilt=.22;pelvis=rt@V((-.018,-.01,.834))
  feet=[rt@V((sg*.144,sg*.09,0)) for sg in (-1,1)]
  goals=[rt@V((-.17,-.35,1.03)),rt@V((.11,-.48,1.14))]
 else:
  yaw=.51;rt=RR(yaw);front=rt@V((0,-1,0));side=rt@V((1,0,0));tilt=.25;pelvis=rt@V((-.01,-.025,.843))
  feet=[rt@V((sg*.124,-sg*.057,0)) for sg in (-1,1)]
  goals=[rt@V((-.12,-.50,1.36)),rt@V((.15,-.50,1.48))]
 torso=rt@Matrix.Rotation(tilt,3,'X')
 orient(chest,pelvis,torso.to_quaternion())
 for idx,sg in enumerate((-1,1)):
  thigh,shin,boot,upper,fore,hand=limbs[sg];foot=feet[idx];ank=foot+V((0,0,.12))
  hip=pelvis+rt@V((sg*.091,0,-.018));knee=solve(hip,ank,.395,.378,front+side*sg*.09);segmentpose(thigh,hip,knee);segmentpose(shin,knee,ank)
  orient(boot,foot,(rt@Matrix.Rotation(sg*.08,3,'Z')).to_quaternion())
  shoulder=pelvis+torso@V((sg*.187,0,.419));goal=goals[idx]
  elbow=solve(shoulder,goal,.309,.298,side*sg*.68-front*.36+V((0,0,-.88)))
  segmentpose(upper,shoulder,elbow);segmentpose(fore,elbow,goal);orient(hand,goal,(goal-elbow).to_track_quat('Z','Y'))
 if prop:orient(prop,goals[1]+front*.046+V((0,0,.022)),rt.to_quaternion())
 objs=[chest,*[o for row in limbs.values() for o in row]]+([prop] if prop else [])
 if frame is not None:
  for o in objs:
   for k in (['location','rotation_quaternion','scale'] if o in [k for row in limbs.values() for k in (row[0],row[1],row[3],row[4])] else ['location','rotation_quaternion']):
    o.keyframe_insert(k,frame=frame,group='Hand transfer fit')
 return objs

