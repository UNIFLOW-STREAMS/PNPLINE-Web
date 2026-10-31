"""Material-batched US masonry shop blocks. Local frontage is -Y.

No scene/file orchestration: the caller supplies the Batch implementation,
root, collection and materials. All geometry remains editable by material.
"""
import math


def building(Batch, name, parent, col, M, w, d, h, variant=0):
    b = Batch(name, parent, col, M)
    floors = max(2, min(4, round(h / 1.8)))
    floor_h = h / floors
    body = 'brick' if variant % 3 != 1 else 'cream'
    trim = 'cream' if body == 'brick' else 'stone'
    b.box(body, (0, 0, h / 2), (w, d, h))
    b.box('stone', (0, 0, .12), (w + .10, d + .10, .24))

    # Projecting courses and a three-step cornice make the silhouette read
    # at miniature scale without a dense field of isolated brick objects.
    for z in [floor_h, h - .22]:
        b.box(trim, (0, 0, z), (w + .14, d + .14, .12))
    for z, over, thick in [(h - .06, .14, .14), (h + .07, .30, .12),
                          (h + .18, .38, .10)]:
        b.box(trim, (0, 0, z), (w + over, d + over, thick))
    b.box('roof', (0, 0, h + .25), (w -.20, d -.20, .10))
    # Hollow parapet: the roof deck remains visible inside its wall.
    parapet = .40 if variant % 2 == 0 else .30
    for sy in [-1, 1]:
        b.box(body, (0, sy * (d / 2 - .07), h + .25 + parapet / 2),
              (w, .18, parapet))
        b.box(trim, (0, sy * (d / 2 - .07), h + .28 + parapet),
              (w + .08, .27, .09))
    for sx in [-1, 1]:
        b.box(body, (sx * (w / 2 - .07), 0, h + .25 + parapet / 2),
              (.18, d, parapet))
        b.box(trim, (sx * (w / 2 - .07), 0, h + .28 + parapet),
              (.27, d + .08, .09))

    # Each facade is parameterized by its tangent/outward basis.
    facades = [((1, 0), (0, -1), w, d / 2),
               ((0, 1), (1, 0), d, w / 2),
               ((-1, 0), (0, 1), w, d / 2),
               ((0, -1), (-1, 0), d, w / 2)]
    def panel(side, u, z, width, height, depth, offset, mat):
        tangent, normal, span, distance = facades[side]
        p = (tangent[0]*u + normal[0]*(distance + offset),
             tangent[1]*u + normal[1]*(distance + offset), z)
        size = (width, depth, height) if tangent[0] else (depth, width, height)
        b.box(mat, p, size)

    for side, (_, _, span, _) in enumerate(facades):
        bays = max(3, round(span / 1.35))
        gap = span / bays
        ww = gap * .55
        # Delicate alternating masonry piers; avoid writing geometry for
        # every brick, letting the material carry the fine mortar pattern.
        for u in [-span / 2 + .11, span / 2 - .11]:
            panel(side, u, h / 2, .18, h - .25, .11, .045, trim)
            if body == 'brick':
                for k in range(int(h / .36)):
                    panel(side, u, .3 + k*.36, .26, .13, .10, .09, trim)
        for level in range(1, floors):
            z = level * floor_h + floor_h * .48
            wh = floor_h * .63
            for j in range(bays):
                u = -span / 2 + gap * (j + .5)
                # Dark recess followed by reflective glazing and deeper
                # surrounds; robust depth separation avoids z-fighting.
                panel(side, u, z, ww + .15, wh + .14, .045, .025, 'dark')
                panel(side, u, z, ww, wh, .035, .055, 'glass')
                for edge in [-1, 1]:
                    panel(side, u + edge * (ww/2 + .04), z,
                          .08, wh + .12, .13, .10, trim)
                panel(side, u, z + wh/2 + .10, ww + .26, .13, .18, .12, trim)
                panel(side, u, z - wh/2 - .08, ww + .28, .12, .24, .14, trim)
                panel(side, u, z, .04, wh, .05, .085, 'metal')
                panel(side, u, z + wh*.08, ww, .045, .05, .085, 'metal')
                if variant % 3 == 1 and side == 0 and level == 1 and j % 2 == 0:
                    # Shallow wrought-metal Juliet balcony.
                    y = -d/2 - .30
                    b.box('stone', (u, y, z-wh/2-.09), (ww+.32, .46, .10))
                    b.rod('dark', (u-ww/2-.10, y-.20, z-wh/2+.45),
                          (u+ww/2+.10, y-.20, z-wh/2+.45), .025)
                    for k in range(6):
                        xx=u-ww/2 + ww*k/5
                        b.rod('dark', (xx,y-.20,z-wh/2),
                              (xx,y-.20,z-wh/2+.45), .016, 5)

        # Retail frontage on front and selected side; service treatment
        # at rear keeps orientation and use distinguishable.
        retail = side == 0 or (side == 1 and variant % 2 == 0)
        if retail:
            for j in range(bays):
                u=-span/2 + gap*(j+.5)
                shopw=gap*.78; shoph=floor_h*.70
                panel(side,u,shoph/2+.20,shopw+.12,shoph+.12,.065,.04,'dark')
                panel(side,u,shoph/2+.20,shopw,shoph,.045,.085,'glass')
                for k in [-1,0,1]:
                    panel(side,u+k*shopw*.5,shoph/2+.20,.045,shoph,.08,.12,'metal')
                panel(side,u,.20,shopw,.08,.10,.12,trim)
                panel(side,u,shoph*.80,.025,.13,.10,.17,'metal')
            # Fascia is intentionally blank: branding is left to existing
            # approved wordmark assets rather than synthesized typography.
            panel(side,0,floor_h-.32,span-.45,.22,.16,.14,'green')
            # Sloped canvas roof and vertical valance.
            tangent,normal,span,distance=facades[side]
            a=span/2-.22; z0=floor_h-.24; z1=floor_h-.58
            points=[]
            for u,off,z in [(-a,.13,z0),(a,.13,z0),(a,.76,z1),(-a,.76,z1)]:
                points.append((tangent[0]*u+normal[0]*(distance+off),
                               tangent[1]*u+normal[1]*(distance+off),z))
            b.add('green',points,[(0,1,2,3)])
            panel(side,0,z1-.065,span-.44,.13,.045,.76,'green')
            for u in [-a,a]:
                p=(tangent[0]*u+normal[0]*(distance+.13),tangent[1]*u+normal[1]*(distance+.13),z0)
                q=(tangent[0]*u+normal[0]*(distance+.76),tangent[1]*u+normal[1]*(distance+.76),z1)
                b.rod('dark',p,q,.025)
        else:
            for j in range(bays):
                u=-span/2+gap*(j+.5)
                panel(side,u,.95,gap*.55,1.25,.07,.06,'glass')
                panel(side,u,1.62,gap*.72,.12,.16,.10,trim)
            if side==2:
                panel(side,0,.77,.82,1.48,.10,.12,'dark')
                panel(side,0,.77,.68,1.36,.08,.19,'metal')
                panel(side,-.23,.81,.045,.18,.06,.25,'dark')
                panel(side,0,.10,1.05,.16,.40,.20,'stone')

    # Three different rooftop objects keep the blocks from reading as
    # repeated boxes; functional louvres and fans are separate geometry.
    for idx,(x,y,sw,sd) in enumerate([(-w*.22,d*.18,w*.24,d*.24),(w*.23,-d*.08,w*.17,d*.18)]):
        rz=h+.30
        b.box('dark',(x,y,rz+.08),(sw+.12,sd+.12,.16))
        b.box('metal',(x,y,rz+.38),(sw,sd,.60))
        b.box('cream',(x,y,rz+.70),(sw+.10,sd+.10,.08))
        for sy in [-1,1]:
            b.box('dark',(x,y+sy*(sd/2+.012),rz+.39),(sw*.80,.025,.40))
            for k in range(6):
                b.box('metal',(x,y+sy*(sd/2+.035),rz+.22+k*.065),(sw*.84,.035,.025))
        # Fan housing with four visible cross blades under a ring.
        rr=min(sw,sd)*.27; fz=rz+.76
        b.ellipsoid('dark',(x,y,fz),(rr,rr,.035),n=16,m=4)
        for k in range(16):
            a=k*math.tau/16; c=(k+1)*math.tau/16
            b.rod('metal',(x+rr*math.cos(a),y+rr*math.sin(a),fz+.025),
                  (x+rr*math.cos(c),y+rr*math.sin(c),fz+.025),.012,5)
        for k in range(4):
            a=k*math.pi/2
            b.rod('metal',(x,y,fz+.035),(x+rr*.85*math.cos(a),y+rr*.85*math.sin(a),fz+.035),.025,5)
    b.box('stone',(w*.22,d*.30,h+.34),(.88,.80,.18))
    b.box('dark',(w*.22,d*.30,h+.45),(.75,.68,.06))
    for x,y in [(-w*.36,-d*.28),(w*.34,d*.34)]:
        b.rod('metal',(x,y,h+.30),(x,y,h+.85),.075,8)
        b.ellipsoid('metal',(x,y,h+.87),(.12,.12,.06),n=8,m=4)

    objects=b.finish()
    for o in objects:
        o['dispatch_asset']='US lowrise street building'
        o['dispatch_variant']=variant
        o['dispatch_floors']=floors
        if not any(token in o.name for token in ['glass','green']):
            mod=o.modifiers.new('Small masonry edge highlights','BEVEL')
            mod.width=.015;mod.segments=1;mod.limit_method='ANGLE'
    return objects
