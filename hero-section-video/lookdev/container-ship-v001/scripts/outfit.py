# Accommodation block, glazing and bridge wings, all in vessel-local coordinates.
house=part('Accommodation · decks and enclosed bridge')
trim=part('Accommodation · doors glazing and external stairs')
def deckhouse(x,y,z0,z1,L,W,rake=0):
    # Chamfered forward corners and raked front windows on the wheelhouse.
    a,b=L/2,W/2;c=min(.18,W*.1)
    shape=[(-a,-b+c),(-a+c,-b),(a-c,-b),(a,-b+c),(a,b-c),(a-c,b),(-a+c,b),(-a,b-c)]
    vs=[(x+u+(rake if u>0 and h==z1 else 0),y+v,h) for h in [z0,z1] for u,v in shape]
    house.add(vs,[tuple(reversed(range(8))),tuple(range(8,16))]+[(i,(i+1)%8,(i+1)%8+8,i+8) for i in range(8)],white)
cx=-5.69
deckhouse(cx,cy,1.33,3.41,2.24,3.12)
deckhouse(cx+.02,cy,3.39,4.12,2.04,2.88)
deckhouse(cx+.05,cy,4.105,4.68,1.85,2.88,.10)
for z,l,w in [(1.46,2.42,3.33),(2.15,2.41,3.31),(2.84,2.40,3.31),(3.44,2.49,3.59),(4.125,2.30,3.86),(4.70,2.28,3.42)]:
    house.box((cx,cy,z),(l,w,.083),pearl)
    if z in (3.44,4.125):
        for sy in (-1,1):
            xa=cx-l*.46;xf=cx+l*.46;y=cy+sy*(w/2-.04)
            trim.railing([(xa,cy+sy*1.34,z+.041),(xa,y,z+.041),(xf,y,z+.041),(xf,cy+sy*1.34,z+.041)],.20,white,.31,.011)
for z in (1.78,2.49,3.13,3.79):
    L,W=(2.24,3.12) if z<3.41 else (2.04,2.88)
    for sy in (-1,1):
        for j in range(5):
            x=cx-.82+j*.40;y=cy+sy*(W/2+.008)
            trim.box((x,y,z),(.188,.023,.235),M['grate'])
            trim.box((x,y+sy*.014,z+.005),(.142,.012,.183),glass)
        if z<3.41:
            x=cx-.29;y=cy+sy*(W/2+.02)
            trim.box((x,y,z-.055),(.15,.024,.42),deck)
            trim.box((x,y+sy*.018,z+.06),(.075,.016,.09),glass)
    for sx in (-1,1):
        x=cx+sx*(L/2+.010)+(0 if z<3.41 else .02)
        for j in range(7):
            y=cy-.99+j*.33
            trim.box((x,y,z),(.02,.17,.19),M['grate'])
            trim.box((x+sx*.011,y,z),(.013,.13,.15),glass)
# Wheelhouse navigation glazing with white mullions and an overhanging visor.
for sy in (-1,1):
    for k in range(5):
        trim.box((cx-.66+k*.365,cy+sy*1.451,4.413),(.316,.022,.274),M['glint'] if k in (0,3) else glass)
for j in range(8):
    y=cy-1.13+j*.32
    x=cx+1.007
    trim.add([(x,y-.136,4.27),(x,y+.136,4.27),(x+.051,y+.136,4.56),(x+.051,y-.136,4.56)],[(0,1,2,3)],glass if j%3 else M['glint'])
    trim.box((cx-.888,y,4.43),(.026,.258,.242),glass)
house.box((cx+.05,cy,4.754),(2.16,3.21,.046),deck)
# Two exterior inclined companionways on the after face of the block.
for i in range(3):
    z=1.49+i*.66;x=cx-1.27
    for k in range(7):
        trim.box((x,cy-.92+k*.14,z+k*.09),(.27,.145,.036),deck)
    for dx in (-.15,.15):
        trim.rod((x+dx,cy-.99,z),(x+dx,cy+.01,z+.65),.023,steel)
        trim.rod((x+dx,cy-.99,z+.21),(x+dx,cy+.01,z+.86),.015,white)
        for k in (0,3,6):trim.rod((x+dx,cy-.92+k*.14,z+k*.09),(x+dx,cy-.92+k*.14,z+k*.09+.21),.012,white)
house.done(.018);trim.done()

rig=part('Bridge roof · signal mast radar and exhaust')
rig.box((cx-.55,cy+.63,4.97),(.54,.55,.45),white)
rig.box((cx-.55,cy+.63,5.17),(.56,.57,.105),blue)
for y in (cy+.52,cy+.75):
    rig.rod((cx-.55,y,5.18),(cx-.58,y,5.38),.103,iron,16)
rig.rod((cx+.16,cy,4.755),(cx+.16,cy,5.98),.055,white,14,.026)
rig.rod((cx+.16,cy,5.94),(cx+.16,cy,6.46),.020,steel,10,.009)
for z,span in [(5.30,.65),(5.73,.39)]:
    rig.rod((cx+.16,cy-span,z),(cx+.16,cy+span,z),.025,white,9)
    for sy in (-1,1):rig.rod((cx+.16,cy,z-.21),(cx+.16,cy+sy*span,z),.014,white)
rig.rod((cx+.16,cy,5.88),(cx+.16,cy,6.02),.082,white,14)
rig.box((cx+.16,cy,6.035),(.069,.77,.062),pearl)
rig.oval((cx-.22,cy-.75,4.99),(.168,.168,.17),pearl)
rig.rod((cx-.22,cy-.75,4.74),(cx-.22,cy-.75,4.87),.103,white,14)
for sy in (-1,1):
    rig.rod((cx-.56,cy+sy*1.02,4.73),(cx-.49,cy+sy*1.04,5.48),.014,steel,8,.007)
    rig.oval((cx+.73,cy+sy*1.72,4.33),(.045,.05,.048),M['green'] if sy<0 else red)
rig.done()

life=part('Rescue boats and davits')
for sy in (-1,1):
    yy=cy+sy*1.85
    life.oval((cx-.19,yy,2.62),(.64,.19,.166),M['orange'],24,9)
    life.oval((cx-.19,yy,2.70),(.42,.152,.139),M['orange'],24,9)
    for k in (-.16,.01,.18):life.box((cx-.19+k,yy+sy*.135,2.72),(.088,.014,.087),glass)
    for dx in (-.49,.49):
        x=cx-.19+dx
        life.pipe([(x,cy+sy*1.50,2.88),(x,cy+sy*1.61,3.07),(x,yy,3.06),(x,yy,2.80)],.025,pearl)
life.done()

# Perimeter walkways and foredeck fittings. The working bay stays open above.
rails=part('Guardrails · bulwark and catwalks')
for sy in (-1,1):
    xs=[-7.86,-7.58,-7.22,-6.72,-6.1,-5.3,-4.5,-3.65,-2,0,2,3.8,4.7,5.4,5.86,6.22,6.64,7.02,7.40,7.75,8.04,8.36,8.63,8.85]
    pts=[(x,cy+sy*(width(x)-.075),sheer(x)+.003) for x in xs]
    rails.railing(pts,.245,white,.39,.013)
rails.railing([(xx[0]+.08,cy-1.35,1.52),(xx[0]+.08,cy+1.35,1.52)],.23,white,.40,.013)
rails.done()
gear=part('Forecastle · anchoring and mooring gear')
gear.rod((8.08,cy,1.55),(8.08,cy,2.79),.042,pearl,12,.017)
gear.rod((8.08,cy-.28,2.53),(8.08,cy+.28,2.53),.018,white)
gear.oval((8.08,cy,2.83),(.042,.042,.039),M['brass'],12,6)
for sg in (-1,1):
    y=cy+sg*.66
    for xc,scale in ((6.70,1.),(-7.26,.82)):
        z=sheer(xc)-.047
        gear.box((xc,y,z+.035),(.52*scale,.58*scale,.069),M['grate'])
        for off in (-.19,.19):
            gear.box((xc,y+off*scale,z+.125*scale),(.26*scale,.055*scale,.219*scale),deck)
        gear.rod((xc,y-.237*scale,z+.22*scale),(xc,y+.237*scale,z+.22*scale),.13*scale,iron,18)
        for j in range(8):
            yy=y+(-.13+j*.036)*scale
            gear.rod((xc,yy,z+.22*scale),(xc,yy+.018*scale,z+.22*scale),.145*scale,M['brass'],16)
        for off in (-.163,.161):
            gear.rod((xc,y+off*scale,z+.22*scale),(xc,y+(off+.027)*scale,z+.22*scale),.171*scale,steel,18)
    for x in (6.15,7.49,-7.45):
        y=cy+sg*(width(x)-.37);z=sheer(x)-.047
        gear.box((x,y,z+.016),(.36,.17,.05),M['grate'])
        for dx in (-.093,.093):
            gear.rod((x+dx,y,z+.02),(x+dx,y,z+.18),.054,iron,12)
            gear.rod((x+dx,y,z+.164),(x+dx,y,z+.193),.069,steel,12)
    # Hawse pipe and an angled stockless anchor against each bow shoulder.
    x=7.32;y=cy+sg*(width(x)*.967);z=.77
    gear.oval((x,y,z),(.152,.077,.125),iron,18,10)
    gear.rod((x+.025,y+sg*.036,z+.01),(x-.20,y+sg*.085,z-.36),.038,iron,10)
    for dx in (-.12,.15):
        gear.pipe([(x-.20,y+sg*.085,z-.36),(x-.20+dx,y+sg*.096,z-.32),(x-.17+dx,y+sg*.09,z-.227)],.032,iron)
gear.done()
