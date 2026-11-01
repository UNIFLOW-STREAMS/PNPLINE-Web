"""Deterministic, material-batched miniature American architecture for Blender.

The factories emit local geometry with the footprint centered on XY and its
lowest point at Z=0.  A caller-supplied parent owns placement on the globe.
Massing plans are separate from the mesh writer; no operators, actions, linked
assets, modifiers, or scene-global materials are created by this module.
"""

from __future__ import annotations

import json
import math
import random
from collections import defaultdict

import bpy
from mathutils import Vector


OWNER = "city-expansion-v001"
MATERIAL_KEYS = ("stone", "ivory", "dark", "glass", "metal", "brick", "roof", "cyan")


class _MeshCompiler:
    """One indexed mesh per used material; disconnected decorative islands are OK."""

    def __init__(self):
        self.vertices = defaultdict(list)
        self.faces = defaultdict(list)

    def mesh(self, material, vertices, faces):
        start = len(self.vertices[material])
        self.vertices[material].extend(tuple(float(c) for c in v) for v in vertices)
        self.faces[material].extend(tuple(start + i for i in f) for f in faces)

    def quad(self, material, points):
        self.mesh(material, points, [(0, 1, 2, 3)])

    def box(self, material, center, size):
        x, y, z = center
        w, d, h = (v * 0.5 for v in size)
        assert min(w, d, h) > 0, "Building boxes must have positive dimensions"
        verts = [(x-w,y-d,z-h), (x+w,y-d,z-h), (x+w,y+d,z-h), (x-w,y+d,z-h),
                 (x-w,y-d,z+h), (x+w,y-d,z+h), (x+w,y+d,z+h), (x-w,y+d,z+h)]
        self.mesh(material, verts, [(3,2,1,0), (4,5,6,7), (0,1,5,4),
                                    (1,2,6,5), (2,3,7,6), (3,0,4,7)])

    def frustum(self, material, z0, z1, width0, depth0, width1, depth1,
                center=(0.0, 0.0)):
        x, y = center
        verts = []
        for z, w, d in ((z0, width0, depth0), (z1, width1, depth1)):
            verts.extend([(x-w/2,y-d/2,z), (x+w/2,y-d/2,z),
                          (x+w/2,y+d/2,z), (x-w/2,y+d/2,z)])
        self.mesh(material, verts, [(3,2,1,0), (4,5,6,7), (0,1,5,4),
                                    (1,2,6,5), (2,3,7,6), (3,0,4,7)])

    def beam(self, material, start, end, width, depth=None):
        a, b = Vector(start), Vector(end)
        axis = b-a
        if axis.length < 1e-8:
            return
        axis.normalize()
        reference = Vector((0,0,1)) if abs(axis.z) < 0.9 else Vector((0,1,0))
        x = axis.cross(reference).normalized() * width * 0.5
        y = axis.cross(x).normalized() * (depth if depth else width) * 0.5
        verts = [a-x-y, a+x-y, a+x+y, a-x+y, b-x-y, b+x-y, b+x+y, b-x+y]
        self.mesh(material, verts, [(3,2,1,0), (4,5,6,7), (0,1,5,4),
                                    (1,2,6,5), (2,3,7,6), (3,0,4,7)])

    def cylinder(self, material, x, y, z0, z1, radius0, radius1=None, sides=12):
        radius1 = radius0 if radius1 is None else radius1
        verts = [(x + r*math.cos(i*math.tau/sides), y + r*math.sin(i*math.tau/sides), z)
                 for z, r in ((z0, radius0), (z1, radius1)) for i in range(sides)]
        faces = [tuple(range(sides-1, -1, -1)), tuple(range(sides, sides*2))]
        faces.extend((i, (i+1)%sides, (i+1)%sides+sides, i+sides) for i in range(sides))
        self.mesh(material, verts, faces)

    def finish(self, name, parent, collection, materials, plan):
        missing = set(self.vertices) - set(materials)
        if missing:
            raise KeyError(f"Missing building materials: {sorted(missing)}")
        objects = []
        for key in MATERIAL_KEYS:
            if not self.vertices[key]:
                continue
            obj_name = f"{name}__{key}"
            if bpy.data.objects.get(obj_name):
                raise ValueError(f"Architecture owner already exists: {obj_name}")
            mesh = bpy.data.meshes.new(obj_name + "_Mesh")
            mesh.from_pydata(self.vertices[key], [], self.faces[key])
            mesh.materials.append(materials[key])
            mesh.update()
            obj = bpy.data.objects.new(obj_name, mesh)
            collection.objects.link(obj)
            obj.parent = parent
            obj["ce_owner"] = OWNER
            obj["ce_role"] = "architecture"
            obj["ce_building"] = name
            obj["ce_material_slot"] = key
            obj["ce_kind"] = plan["kind"]
            objects.append(obj)
        if objects:
            objects[0]["ce_plan"] = json.dumps(plan, separators=(",", ":"))
            objects[0]["ce_object_count"] = len(objects)
            objects[0]["ce_face_count"] = sum(len(v) for v in self.faces.values())
        return objects


def _check_dimensions(height, width, depth):
    if not all(math.isfinite(v) and v > 0 for v in (height, width, depth)):
        raise ValueError("Building height, width, and depth must be finite and positive")


def _point(side, u, z, width, depth, relief=0.0):
    """CCW facade frame: horizontal tangent cross up equals outward normal."""
    if side == 0:
        return (u, -depth/2-relief, z)
    if side == 1:
        return (width/2+relief, u, z)
    if side == 2:
        return (-u, depth/2+relief, z)
    return (-width/2-relief, -u, z)


def _panel(writer, material, side, u, z, w, h, width, depth, relief):
    writer.quad(material, [_point(side, u-w/2, z-h/2, width, depth, relief),
                           _point(side, u+w/2, z-h/2, width, depth, relief),
                           _point(side, u+w/2, z+h/2, width, depth, relief),
                           _point(side, u-w/2, z+h/2, width, depth, relief)])


def _facade_box(writer, material, side, u, z, w, h, width, depth, relief, thickness):
    p = _point(side, u, z, width, depth, relief)
    writer.box(material, p, (w, thickness, h) if side%2 == 0 else (thickness, w, h))


def _rim(writer, material, width, depth, z, rail, height):
    """A four-edge parapet with corners owned by front/back, no duplicate boxes."""
    writer.box(material, (0,-depth/2+rail/2,z), (width,rail,height))
    writer.box(material, (0, depth/2-rail/2,z), (width,rail,height))
    if depth > rail*2:
        for sign in (-1,1):
            writer.box(material, (sign*(width/2-rail/2),0,z), (rail,depth-rail*2,height))


def _flat_roof(writer, width, depth, z, unit, seed, mechanical=True):
    rail = unit*.11
    writer.box("roof", (0,0,z+.018*unit), (width-.22*unit,depth-.22*unit,.036*unit))
    _rim(writer, "ivory", width, depth, z+.12*unit, rail, .24*unit)
    if mechanical:
        rng = random.Random(seed)
        writer.box("metal", (-width*.22, depth*.15, z+.21*unit),
                   (width*.24,depth*.22,.38*unit))
        for k in (-1,1):
            writer.cylinder("dark", -width*.22+k*width*.06, depth*.15,
                            z+.4*unit,z+.425*unit,width*.04,sides=10)
        writer.box("stone", (width*.24,-depth*.19,z+.29*unit),
                   (width*.18,depth*.2,.54*unit))
        writer.box("roof", (width*.24,-depth*.19,z+.57*unit),
                   (width*.2,depth*.22,.04*unit))
        if rng.random() > .55:
            writer.cylinder("brick", width*.24,depth*.26,z,z+.65*unit,.12*unit,sides=6)
            writer.cylinder("metal", width*.24,depth*.26,z+.65*unit,z+.7*unit,.16*unit,sides=6)


def _shaft_facade(writer, width, depth, z0, z1, floor_height, unit,
                  facade="stone", vertical=False, base_doors=False):
    """Decorate only each tier's exposed perimeter, never its hidden roof overlap."""
    rows = max(1, int((z1-z0)/floor_height))
    step_z = (z1-z0)/rows
    for side in range(4):
        span = width if side%2 == 0 else depth
        bays = max(2, int(span/(unit*.56)))
        step = span/bays
        for row in range(rows):
            z = z0+(row+.53)*step_z
            for bay in range(bays):
                u = -span/2+(bay+.5)*step
                if base_doors and side == 0 and row == 0 and abs(u) < span*.22:
                    _panel(writer, "dark", side,u,z0+step_z*.48,step*.72,step_z*.9,width,depth,.018*unit)
                    _facade_box(writer,"metal",side,u,z0+step_z*.48,.025*unit,step_z*.9,width,depth,.03*unit,.025*unit)
                else:
                    _panel(writer,"glass",side,u,z,step*.58,step_z*.65,width,depth,.012*unit)
                    if not vertical:
                        _facade_box(writer,"ivory",side,u,z-step_z*.35,step*.7,.035*unit,width,depth,.04*unit,.09*unit)
        if vertical:
            for bay in range(1,bays):
                u=-span/2+bay*step
                _facade_box(writer,"ivory",side,u,(z0+z1)/2,.05*unit,z1-z0,width,depth,.045*unit,.09*unit)
        else:
            for row in range(1,rows):
                _facade_box(writer,facade,side,0,z0+row*step_z,span,.045*unit,width,depth,.025*unit,.05*unit)


def _triangle_prism(writer, material, points, inward):
    verts = list(points) + [tuple(Vector(p)+Vector(inward)) for p in points]
    writer.mesh(material, verts, [(0,1,2),(5,4,3),(0,3,4,1),(1,4,5,2),(2,5,3,0)])


def _chrysler_crown(writer, width, depth, z0, height, unit):
    """Seven stainless sunburst arches on a gently bowed, four-sided crown."""
    def profile(z):
        t=min(1.0,max(0.0,(z-z0)/height))
        return max(.045,math.cos(t*math.pi*.5)**.68)

    def surface(side,u,z,relief):
        scale=profile(z)
        return _point(side,u,z,width*scale,depth*scale,relief)

    # A 28-section envelope gives the steel crown curved shoulders. It remains
    # structurally separate from the straight Transamerica pyramid silhouette.
    for section in range(28):
        za=z0+height*section/28
        zb=z0+height*(section+1)/28
        sa,sb=profile(za),profile(zb)
        writer.frustum("metal",za,zb,width*sa,depth*sa,width*sb,depth*sb)
    for tier in range(7):
        base=z0+height*tier*.122
        rise=height*(.205-.012*tier)
        for side in range(4):
            span=(width if side%2==0 else depth)*profile(base)
            radius=span*.47
            # Half-elliptical bright ribbons are fitted to the common facade,
            # rather than being cylinders or disks stuck through the tower.
            for seg in range(24):
                aa=math.pi*seg/24
                ab=math.pi*(seg+1)/24
                points=[]
                for angle,offset in ((aa,0),(ab,0),(ab,.065*unit),(aa,.065*unit)):
                    z=base+rise*math.sin(angle)+offset
                    u=radius*math.cos(angle)
                    points.append(surface(side,u,z,.025*unit))
                writer.quad("ivory",list(reversed(points)))
            # Triangular glazing follows the arch: middle windows rise higher
            # than the side windows, visibly forming a stainless sunburst.
            count=max(3,7-tier//2)
            for win in range(count):
                angle=math.pi*(.12+.76*(win+.5)/count)
                x=radius*.83*math.cos(angle)
                bottom=base+rise*(.10+.30*math.sin(angle))
                tip=base+rise*(.10+.70*math.sin(angle))
                half=span*(.040 if tier<5 else .050)
                points=[surface(side,x-half,bottom,.031*unit),
                        surface(side,x+half,bottom,.031*unit),
                        surface(side,x,tip,.031*unit)]
                writer.mesh("dark",points,[(0,1,2)])
    writer.cylinder("metal",0,0,z0+height-.03*unit,z0+height+.11*unit,
                    width*.045,width*.028,12)


def create_chrysler(name, parent, collection, materials, height=24, width=5.4, depth=5.4):
    """Art Deco landmark: setback tower, four sunburst crowns, and steel needle."""
    _check_dimensions(height,width,depth)
    writer=_MeshCompiler()
    unit=width/5.4
    # All mass tiers meet at their end planes; none enclose another mass tier.
    tiers=[(0,.105,1.0,1.0),(.105,.49,.80,.82),(.49,.59,.69,.72),
           (.59,.68,.59,.62),(.68,.735,.49,.52)]
    for i,(a,b,w,d) in enumerate(tiers):
        za,zb=height*a,height*b
        writer.box("stone",(0,0,(za+zb)/2),(width*w,depth*d,zb-za))
        _shaft_facade(writer,width*w,depth*d,za,zb,height*.034,unit,
                      vertical=True,base_doors=i==0)
        # Exposed cornice sits just outside the mass, with no roof slab spanning
        # across the next tier's solid footprint.
        _rim(writer,"ivory",width*w+.075*unit,depth*d+.075*unit,
             zb-.045*unit,.075*unit,.09*unit)
    # Ground-level polished entry portal and three steps.
    for i in range(3):
        writer.box("ivory",(0,-depth/2-(.12+.11*i)*unit,(.035+.045*i)*unit),
                   (width*.48,(.66-.18*i)*unit,.07*unit))
    writer.box("metal",(0,-depth/2-.15*unit,height*.082),(width*.43,.42*unit,.075*unit))
    # Chrysler's outward-facing steel corner eagles at the upper setback.
    for sx in (-1,1):
        for sy in (-1,1):
            x,y=sx*width*.365,sy*depth*.365
            z=height*.485
            writer.box("metal",(x,y,z),(.3*unit,.3*unit,.3*unit))
            nose=(x+sx*.45*unit,y+sy*.45*unit,z-.06*unit)
            writer.beam("metal",(x,y,z+.1*unit),nose,.19*unit,.15*unit)
            writer.beam("metal",(x-sy*.2*unit,y+sx*.2*unit,z),
                        (x+sy*.2*unit,y-sx*.2*unit,z),.11*unit,.12*unit)
    crown_z=height*.735
    crown_h=height*.205
    _chrysler_crown(writer,width*.49,depth*.52,crown_z,crown_h,unit)
    writer.cylinder("metal",0,0,height*.94,height*.985,width*.026,width*.009,12)
    writer.cylinder("ivory",0,0,height*.985,height,width*.009,.002*unit,8)
    plan={"kind":"chrysler","dimensions":[width,depth,height],"tiers":tiers,
          "crown_arches":7,"seed":0,"local_base_z":0}
    return writer.finish(name,parent,collection,materials,plan)


def create_transamerica(name, parent, collection, materials, height=22, width=6, depth=6):
    """Four-sided San Francisco pyramid with elevated arcade and mechanical ears."""
    _check_dimensions(height,width,depth)
    writer=_MeshCompiler()
    unit=width/6
    base=height*.075
    top=height*.94
    w0,d0=width*.91,depth*.91
    w1,d1=width*.055,depth*.055
    writer.box("ivory",(0,0,.07*unit),(width,depth,.14*unit))
    # Open street-level arcade: inclined perimeter supports and a central core.
    writer.box("glass",(0,0,base*.5+.07*unit),(width*.35,depth*.35,base-.14*unit))
    for side in range(4):
        span=w0 if side%2==0 else d0
        for bay in (-1,0,1):
            p0=_point(side,bay*span*.28,.14*unit,w0,d0,-.08*unit)
            p1=_point(side,bay*span*.23,base,w0,d0,-.02*unit)
            writer.beam("ivory",p0,p1,.18*unit,.21*unit)
    writer.frustum("stone",base,top,w0,d0,w1,d1)
    # Window grid follows actual taper at each row, with narrow pale mullions.
    rows=29
    row_h=(top-base)/rows
    for side in range(4):
        initial_span=w0 if side%2==0 else d0
        for row in range(rows):
            za=base+(row+.14)*row_h
            zb=base+(row+.83)*row_h
            ta=(za-base)/(top-base)
            tb=(zb-base)/(top-base)
            wa,da=w0+(w1-w0)*ta,d0+(d1-d0)*ta
            wb,db=w0+(w1-w0)*tb,d0+(d1-d0)*tb
            span_a=wa if side%2==0 else da
            span_b=wb if side%2==0 else db
            cols=max(1,int((span_a+span_b)/(.63*unit)))
            for col in range(cols):
                a=-.5+(col+.18)/cols
                b=-.5+(col+.82)/cols
                writer.quad("glass",[_point(side,a*span_a,za,wa,da,.014*unit),
                                     _point(side,b*span_a,za,wa,da,.014*unit),
                                     _point(side,b*span_b,zb,wb,db,.014*unit),
                                     _point(side,a*span_b,zb,wb,db,.014*unit)])
        # Continuous structural ribs give the pyramid its slender vertical grid.
        for rib in range(11):
            t=-.5+rib/10
            p0=_point(side,t*initial_span,base,w0,d0,.03*unit)
            p1=_point(side,t*(w1 if side%2==0 else d1),top,w1,d1,.03*unit)
            writer.beam("ivory",p0,p1,.034*unit,.038*unit)
    # Two real, narrow service wings emerge from opposite sides of the taper.
    # Their inner edge meets the taper; only exposed wing volume is emitted.
    ear_z0,ear_z1=height*.56,height*.76
    for sx in (-1,1):
        inner0=(w0+(w1-w0)*(ear_z0-base)/(top-base))/2
        inner1=(w0+(w1-w0)*(ear_z1-base)/(top-base))/2
        outer=inner0+.35*unit
        y=depth*.105
        verts=[(sx*inner0,-y,ear_z0),(sx*outer,-y,ear_z0),
               (sx*outer,y,ear_z0),(sx*inner0,y,ear_z0),
               (sx*inner1,-y,ear_z1),(sx*outer,-y,ear_z1),
               (sx*outer,y,ear_z1),(sx*inner1,y,ear_z1)]
        faces=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
        if sx<0:
            faces=[tuple(reversed(f)) for f in faces]
        writer.mesh("ivory",verts,faces)
        for zz in (height*.61,height*.66,height*.71):
            writer.box("dark",(sx*(outer+.008*unit),0,zz),(.016*unit,depth*.16,.06*unit))
    writer.frustum("metal",top,height*.985,w1,d1,width*.012,depth*.012)
    writer.cylinder("ivory",0,0,height*.985,height,width*.009,.001*unit,sides=8)
    plan={"kind":"transamerica","dimensions":[width,depth,height],
          "base_arcade_height":base,"grid_rows":rows,"service_wings":2,"seed":0,"local_base_z":0}
    return writer.finish(name,parent,collection,materials,plan)


def create_block(name, parent, collection, materials, width, depth, height,
                 kind="masonry", seed=0):
    """A 3–8 story supporting building with street frontage and a finished roof.

    Supported kinds are masonry, office, rowhouse; other kinds raise an error.
    Height measures the primary facade, with small parapet/mechanical features
    up to roughly one floor above it. Width/depth describe the main footprint.
    """
    _check_dimensions(height,width,depth)
    if kind not in ("masonry","office","rowhouse"):
        raise ValueError(f"Unknown supporting architecture kind: {kind}")
    rng=random.Random(seed)
    writer=_MeshCompiler()
    floors=max(3,min(8,round(height/.9)))
    floor_h=height/floors
    unit=floor_h
    body_key="glass" if kind=="office" else ("brick" if seed%3 else "stone")
    writer.box(body_key,(0,0,height/2),(width,depth,height))
    # Solid, contrasting plinth gives thin facade details a convincing base.
    _rim(writer,"stone",width+.025*unit,depth+.025*unit,.11*unit,.045*unit,.22*unit)
    if kind=="office":
        for side in range(4):
            span=width if side%2==0 else depth
            bays=max(3,round(span/(floor_h*.5)))
            for bay in range(bays+1):
                u=-span/2+span*bay/bays
                _facade_box(writer,"metal",side,u,height/2,.035*unit,height,width,depth,.03*unit,.055*unit)
            for floor in range(floors+1):
                _facade_box(writer,"ivory",side,0,floor*floor_h+.033*unit,span,.065*unit,width,depth,.035*unit,.07*unit)
            for floor in range(floors):
                for bay in range(bays):
                    if (floor*7+bay*3+side+seed)%6==0:
                        u=-span/2+(bay+.5)*span/bays
                        _panel(writer,"dark",side,u,(floor+.53)*floor_h,span/bays*.86,floor_h*.78,width,depth,.012*unit)
        _panel(writer,"dark",0,0,floor_h*.46,width*.36,floor_h*.86,width,depth,.055*unit)
        writer.box("metal",(0,-depth/2-.25*unit,floor_h*.96),(width*.49,.55*unit,.055*unit))
        _flat_roof(writer,width,depth,height,unit,seed)
    else:
        _shaft_facade(writer,width,depth,0,height,floor_h,unit,
                      facade=body_key,base_doors=True)
        # Classical cornice uses two discrete ledges above the shaft.
        _rim(writer,"ivory",width+.10*unit,depth+.10*unit,height-.025*unit,.10*unit,.13*unit)
        _rim(writer,"stone",width+.17*unit,depth+.17*unit,height+.055*unit,.10*unit,.06*unit)
        for step in range(3):
            writer.box("stone",(0,-depth/2-(.13+step*.10)*unit,(.03+step*.035)*unit),
                       (width*.38,(.65-step*.17)*unit,.06*unit))
        for sx in (-1,1):
            writer.box("ivory",(sx*width*.22,-depth/2-.055*unit,floor_h*.48),
                       (.10*unit,.11*unit,floor_h*.96))
        writer.box("ivory",(0,-depth/2-.065*unit,floor_h*.98),(width*.52,.13*unit,.12*unit))
        if kind=="rowhouse":
            # A dark mansard cap, light ridge, and three front dormers give
            # brownstone neighbors a recognizable roof silhouette.
            roof_h=floor_h*.58
            writer.frustum("roof",height+.085*unit,height+roof_h,
                           width+.12*unit,depth+.12*unit,width*.72,depth*.76)
            writer.box("metal",(0,0,height+roof_h+.035*unit),(width*.74,depth*.78,.07*unit))
            dormers=max(2,min(4,round(width/(unit*.8))))
            for d in range(dormers):
                x=(d-(dormers-1)/2)*width*.65/dormers
                z=height+roof_h*.38
                writer.box("ivory",(x,-depth/2+.07*unit,z),(.34*unit,.26*unit,.31*unit))
                _panel(writer,"glass",0,x,z,.21*unit,.22*unit,width,depth,.061*unit)
                points=[(x-.21*unit,-depth/2-.09*unit,z+.15*unit),
                        (x+.21*unit,-depth/2-.09*unit,z+.15*unit),
                        (x,-depth/2-.09*unit,z+.31*unit)]
                _triangle_prism(writer,"roof",points,(0,.37*unit,0))
            writer.box("brick",(width*.29,depth*.25,height+roof_h*.8),(.20*unit,.22*unit,roof_h*.9))
        else:
            _flat_roof(writer,width,depth,height+.085*unit,unit,seed)
            # Some buildings receive rear fire-escape balconies; a fixed seed
            # determines placement, keeping the street-facing facade readable.
            if rng.random()>.55:
                for floor in range(1,floors):
                    z=floor*floor_h+.12*unit
                    writer.box("metal",(width*.2,depth/2+.17*unit,z),
                               (width*.36,.36*unit,.045*unit))
                    writer.beam("dark",(width*.02,depth/2+.32*unit,z+.2*unit),
                                (width*.38,depth/2+.32*unit,z+.2*unit),.025*unit)
                    for t in (0,.5,1):
                        x=width*(.02+.36*t)
                        writer.beam("dark",(x,depth/2+.32*unit,z),
                                    (x,depth/2+.32*unit,z+.2*unit),.018*unit)
    plan={"kind":kind,"dimensions":[width,depth,height],"floors":floors,
          "seed":int(seed),"local_base_z":0}
    return writer.finish(name,parent,collection,materials,plan)


def create_willis(name, parent, collection, materials, height=27, width=7.2, depth=7.2):
    """Chicago bundled-tube landmark, with two antenna masts inside total height.

    The nine-square-tube grammar follows SOM's published structural description;
    step proportions and facade density are deliberately simplified for miniature
    readability. Only exposed faces above an adjacent tube receive facade detail.
    """
    _check_dimensions(height,width,depth)
    writer=_MeshCompiler()
    unit=width/7.2
    base=.16*unit
    body_top=height*.855
    tube_w,tube_d=width/3,depth/3
    # Front-to-back rows: nine touching tubes, then a 7/5/2 stepped skyline.
    fractions=((.49,.66,.49),(.84,1.0,.66),(.84,1.0,.84))
    tubes={(ix,iy):base+(body_top-base)*fractions[iy][ix]
           for iy in range(3) for ix in range(3)}
    writer.box("stone",(0,0,base/2),(width+.28*unit,depth+.28*unit,base))
    directions=((0,-1),(1,0),(0,1),(-1,0))
    floor_h=(body_top-base)/48
    for (ix,iy),roof_z in tubes.items():
        x,y=(ix-1)*tube_w,(iy-1)*tube_d
        writer.box("dark",(x,y,(base+roof_z)/2),(tube_w,tube_d,roof_z-base))
        # Dark recessed flat rooftops, a fine silver coping, and mechanical cap.
        writer.box("roof",(x,y,roof_z+.012*unit),(tube_w-.08*unit,tube_d-.08*unit,.024*unit))
        for side,(dx,dy) in enumerate(directions):
            adjacent=tubes.get((ix+dx,iy+dy),base)
            exposed_z=max(base,adjacent)
            if exposed_z>=roof_z-1e-6:
                continue
            span=tube_w if side%2==0 else tube_d
            def point(u,z,relief):
                p=_point(side,u,z,tube_w,tube_d,relief)
                return (p[0]+x,p[1]+y,p[2])
            # Thin pale vertical columns continue uninterrupted between setbacks.
            bays=5
            for col in range(bays+1):
                u=-span/2+span*col/bays
                # Shared same-height exterior tube edges get a single column.
                if col==0 and ((side in (0,2) and ix>0) or (side in (1,3) and iy>0)):
                    u+=.015*unit
                writer.beam("metal",point(u,exposed_z,.027*unit),
                            point(u,roof_z,.027*unit),.035*unit,.045*unit)
            start_row=max(0,math.floor((exposed_z-base)/floor_h))
            last_row=math.ceil((roof_z-base)/floor_h)
            for row in range(start_row,last_row):
                za=max(exposed_z+.025*unit,base+(row+.14)*floor_h)
                zb=min(roof_z-.045*unit,base+(row+.81)*floor_h)
                if zb<=za:
                    continue
                for col in range(bays):
                    ua=-span/2+(col+.13)*span/bays
                    ub=-span/2+(col+.87)*span/bays
                    writer.quad("glass",[point(ua,za,.012*unit),point(ub,za,.012*unit),
                                         point(ub,zb,.012*unit),point(ua,zb,.012*unit)])
                zz=base+(row+1)*floor_h
                if exposed_z+.02*unit<zz<roof_z-.04*unit:
                    writer.beam("metal",point(-span/2,zz,.022*unit),
                                point(span/2,zz,.022*unit),.016*unit,.022*unit)
            writer.beam("metal",point(-span/2,roof_z,.025*unit),
                        point(span/2,roof_z,.025*unit),.075*unit,.07*unit)
        # Small setbacks receive louvered rooftop mechanical enclosures.
        if fractions[iy][ix]<1:
            writer.box("roof",(x,y,roof_z+.13*unit),(.55*unit,.65*unit,.22*unit))
            for vent in (-1,0,1):
                writer.box("metal",(x+vent*.12*unit,y,roof_z+.247*unit),
                           (.045*unit,.58*unit,.014*unit))
    # Low street canopy and five glazed entry doors along the visible front.
    for door in range(5):
        xx=(door-2)*width*.105
        writer.quad("glass",[(xx-width*.038,-depth/2-.018*unit,base),
                             (xx+width*.038,-depth/2-.018*unit,base),
                             (xx+width*.038,-depth/2-.018*unit,base+height*.044),
                             (xx-width*.038,-depth/2-.018*unit,base+height*.044)])
    writer.box("metal",(0,-depth/2-.26*unit,base+height*.047),
               (width*.66,.65*unit,.075*unit))
    # Two separated, bright antenna masts on the two surviving tallest tubes.
    # The maximum tip is exactly the caller's architectural height.
    for iy,tip in ((1,height),(2,height*.987)):
        y=(iy-1)*tube_d
        writer.box("roof",(0,y,body_top+.14*unit),(.65*unit,.65*unit,.28*unit))
        mast_base=body_top+.28*unit
        writer.cylinder("metal",0,y,mast_base,body_top+(tip-body_top)*.62,
                        .085*unit,.052*unit,sides=10)
        writer.cylinder("ivory",0,y,body_top+(tip-body_top)*.62,tip,
                        .052*unit,.014*unit,sides=10)
        for level in (.18,.36,.54):
            z=body_top+(tip-body_top)*level
            writer.cylinder("ivory",0,y,z,z+.035*unit,.12*unit,sides=10)
    plan={"kind":"willis","dimensions":[width,depth,height],"tube_grid":fractions,
          "tube_count":9,"antenna_count":2,"body_top":body_top,"seed":0,"local_base_z":0,
          "reference":"https://www.som.com/projects/willis-tower-formerly-sears-tower/"}
    objects=writer.finish(name,parent,collection,materials,plan)
    # Workbench shadow volumes are stable for the closed structural mass.
    # Glazing consists of open quads; fine relief must not cast striping shadows.
    for obj in objects:
        obj.display.show_shadows=obj["ce_material_slot"]=="dark"
        obj["ce_shadow_role"]="closed_mass" if obj.display.show_shadows else "facade_detail"
    return objects
