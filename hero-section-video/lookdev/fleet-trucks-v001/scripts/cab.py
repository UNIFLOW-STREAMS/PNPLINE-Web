def build_cab(unit,tag,rear,length,zbase):
    body=P(tag+' cab lacquer',unit);trim=P(tag+' glazing and seals',unit)
    brightwork=P(tag+' lights and brightwork',unit)
    # Cabin slopes back at the windscreen, with a radiused plan and a raised crown.
    shapes=[(.405,.025,1.425,.753,.086),(.49,.005,1.465,.785,.103),(.74,0,1.465,.785,.105),
            (1.29,.014,1.310,.764,.107),(1.365,.033,1.275,.752,.12),(1.395,.09,1.233,.704,.13)]
    shell(body,[deckring(a,b,w,h,c) for h,a,b,w,c in shapes],ivory)
    is_tractor=tag=='Inbound'
    xback=-.55 if is_tractor else .072
    if is_tractor:
        shell(body,[deckring(-.56,.085,.739,.450,.066),deckring(-.56,.087,.758,.53,.067),
                    deckring(-.55,.087,.744,1.286,.068),deckring(-.52,.09,.704,1.390,.065)],ivory)
        for sy in (-1,1):
            trim.box((-.27,sy*.759,.760),(.411,.018,.270),pearl)
            for j in range(4):
                trim.box((-.27,sy*.772,.697+j*.039),(.265,.012,.013),steel)
            brightwork.box((-.24,sy*.760,1.117),(.297,.019,.035),navy)
    # Front of the deflector pitches down into the brow, with a broad, closed trailing edge.
    shell(body,[deckring(xback,1.20,.685,1.380,.080),deckring(xback+.01,1.10,.672,1.423,.078),
                deckring(xback+.025,.29,.634,1.574 if is_tractor else 1.506,.063)],ivory)
    # Bonnet is absent on this cab-over. The windscreen and corner glazing share the rake.
    def fx(z):return 1.465 if z<=.74 else 1.465-(z-.74)*(.155/.55)
    def wy(z):return .785 if z<=.74 else .785-(z-.74)*(.021/.55)
    def wind(profile,off,m):
        solid(trim,[(fx(z)+off,y,z) for y,z in profile],(-.007,0,0),m)
    wind([(-.655,.762),(.655,.762),(.677,.794),(.651,1.240),(.609,1.272),(-.61,1.272),(-.652,1.239),(-.677,.794)],.008,black)
    wind([(-.622,.795),(.622,.795),(.646,.815),(.619,1.217),(.589,1.240),(-.589,1.240),(-.619,1.217),(-.646,.815)],.013,glass)
    for sy in (-1,1):
        # Rubber reveal, door glass, fixed quarter-light and rear pillar.
        def sidepanel(poly,out,m):
            solid(trim,[(x,sy*(wy(z)+out),z) for x,z in poly],(0,-sy*.008,0),m)
        sidepanel([(.138,.858),(.818,.806),(1.311,.744),(1.345,.804),(1.210,1.246),(1.157,1.272),(.142,1.258)],.005,black)
        sidepanel([(.195,.891),(.420,.875),(.420,1.219),(.196,1.214)],.010,shade)
        sidepanel([(.454,.869),(.814,.838),(1.269,.786),(1.301,.816),(1.178,1.208),(1.14,1.229),(.454,1.220)],.012,glass)
        for path in [[(.119,1.263),(.104,.858),(.101,.495),(.745,.466)],
                     [(1.334,.775),(1.345,.692),(1.328,.508)]]:
            trim.pipe([(x,sy*(wy(z)+.006),z) for x,z in path],.0075,black,7)
        trim.box((.213,sy*.791,.761),(.187,.015,.052),black)
        brightwork.box((.223,sy*.801,.775),(.135,.020,.018),alloy)
        # Twin-arm mirrors, slightly inboard of the loaded vehicle's swept envelope.
        for z in (.842,1.100):
            trim.pipe([(1.239,sy*.773,z),(1.278,sy*.847,z+.018),(1.265,sy*.917,z+.026)],.014,black)
        brightwork.box((1.263,sy*.929,1.013),(.089,.074,.270),navy)
        brightwork.box((1.215,sy*.930,1.013),(.011,.061,.233),pearl)
        brightwork.box((.62,sy*.792,.574),(1.06,.014,.034),cyan)
        brightwork.box((1.15,sy*.791,.642),(.085,.017,.039),amber)
        # Wipers lie on the inclined glass; the front has two blades.
        u=sy*.30
        brightwork.rod((fx(.78)+.022,u-sy*.16,.78),(fx(.850)+.026,u+sy*.083,.850),.009,black,8)
        brightwork.rod((fx(.842)+.029,u-sy*.105,.842),(fx(.871)+.029,u+sy*.21,.871),.011,black,8)
    shell(body,[deckring(1.202,1.466,.727,.15,.070),deckring(1.205,1.492,.767,.213,.074),deckring(1.21,1.487,.770,.413,.081)],pearl)
    trim.box((1.477,0,.519),(.034,.878,.315),navy)
    for z,wide in [(.408,.711),(.457,.774),(.505,.814),(.553,.841)]:
        brightwork.box((1.497,0,z),(.016,wide,.017),alloy)
    brightwork.box((1.483,0,.648),(.030,.839,.041),cyan)
    trim.box((1.491,0,.247),(.026,.848,.087),black)
    brightwork.box((1.511,0,.245),(.018,.245,.072),ivory)
    for sy in (-1,1):
        brightwork.box((1.477,sy*.552,.484),(.048,.255,.134),black)
        brightwork.box((1.504,sy*.535,.501),(.018,.185,.071),lamp)
        brightwork.box((1.506,sy*.650,.501),(.018,.041,.076),amber)
        brightwork.box((1.502,sy*.553,.449),(.018,.221,.017),bright)
        brightwork.box((1.478,sy*.610,.254),(.034,.103,.046),lamp)
    for yy in (-.48,-.24,0,.24,.48):
        brightwork.box((1.207,yy,1.384),(.057,.052,.028),amber)
    # Transform designed parts into this chassis' longitudinal envelope.
    for p,b in [(body,.012),(trim,.004),(brightwork,.004)]:
        # The sleeper is shorter than the cab to clear the articulated trailer
        # at maximum steering lock on the final warehouse approach.
        p.v=[(rear+length*(x*.67 if is_tractor and x<0 else x)/1.50,y,zbase+z) for x,y,z in p.v]
        finishpart(p,b)

for n in ('TRACTOR_CAB','TRACTOR_GLASS','TRACTOR_CHASSIS','TRAILER_CHASSIS','TRAILER_COUPLING_TONGUE'):
    hide(w[n])
build_cab(w['A03_TRACTOR'],'Inbound',.577,1.52,1.18)
for unitname,tag in [('A04_PRIMARY','Dispatch'),('A05_SECONDARY','Relay')]:
    unit=w[unitname]
    for ob in unit.children:
        if ob.name.startswith('DSP_OUTBOUND_DETAIL_') or ob.name in (unitname+'_CAB',unitname+'_GLASS'):
            hide(ob)
    build_cab(unit,tag,1.020,1.196,1.135)
