"""Additive detail overlays for the two existing outbound delivery vehicles.

All dimensions are in each original van root's local space (+X forward).
No existing data, transform, action, constraint or material is altered. The
small 0.003--0.009 surface clearances avoid coplanar overlay flicker. Calling
again returns the already-created detail objects without duplicating them.
"""
import math

from citykit import Batch


_ROOTS = ('A04_PRIMARY', 'A05_SECONDARY')
_OWNER = 'us-dispatch-outbound-detail-v001'


def _annulus(b, mat, x, y, z, r_outer, r_inner, side, n=32):
    """Shallow annular rim facing the outside of a wheel (local +/-Y)."""
    verts = []
    for r in (r_outer, r_inner):
        verts.extend((x+r*math.cos(i*math.tau/n), y,
                      z+r*math.sin(i*math.tau/n)) for i in range(n))
    faces = [(i, (i+1)%n, (i+1)%n+n, i+n) for i in range(n)]
    if side > 0:
        faces = [tuple(reversed(f)) for f in faces]
    b.add(mat, verts, faces)


def _tire(b, x, side):
    # A rounded shoulder and a dark sidewall conceal the coarse original
    # wheel cap. Preserve original r=.4 silhouette and z=.7 ground contact.
    n = 32
    rings = [(side*.913, .397), (side*1.015, .397),
             (side*1.034, .365), (side*1.037, .225)]
    verts = [(x+r*math.cos(i*math.tau/n), y,
              1.1+r*math.sin(i*math.tau/n))
             for y, r in rings for i in range(n)]
    faces = [(j*n+i, j*n+(i+1)%n, (j+1)*n+(i+1)%n, (j+1)*n+i)
             for j in range(len(rings)-1) for i in range(n)]
    if side > 0:
        faces = [tuple(reversed(f)) for f in faces]
    b.add('dark', verts, faces)
    # Concentric hub treatment does not introduce non-rotating spokes when
    # the source animates its wheels independently of the vehicle root.
    _annulus(b, 'metal', x, side*1.038, 1.1, .221, .173, side)
    _annulus(b, 'dark', x, side*1.039, 1.1, .171, .102, side)
    b.rod('metal', (x, side*1.025, 1.1), (x, side*1.039, 1.1), .100, 24)


def _details(root, col, M):
    name = 'DSP_OUTBOUND_DETAIL_' + root.name
    b = Batch(name, root, col, M)

    # Front and side glazing sit over the existing steel-colored glass bar.
    b.box('dark', (2.101, 0, 2.15), (.002, 1.60, .448))
    b.box('glass', (2.104, 0, 2.163), (.002, 1.46, .357))
    b.box('dark', (2.107, 0, 2.16), (.002, .024, .36))
    for sy in (-1, 1):
        b.box('dark', (1.60, sy*.818, 2.15), (1.00, .009, .448))
        b.box('glass', (1.61, sy*.825, 2.17), (.86, .006, .347))
        b.box('dark', (1.89, sy*.829, 2.17), (.025, .006, .35))
        # Window sill/door seams, handle and a shallow step.
        b.box('metal', (1.49, sy*.831, 1.914), (.99, .012, .025))
        b.box('dark', (1.03, sy*.805, 1.65), (.017, .012, .48))
        b.box('dark', (1.52, sy*.806, 1.385), (.96, .012, .018))
        b.box('metal', (1.17, sy*.826, 1.82), (.16, .035, .037))
        b.box('dark', (1.47, sy*.829, 1.29), (.84, .11, .065))
        # Mirror assemblies remain inside the original wheel-to-wheel width.
        b.rod('dark', (1.94, sy*.81, 2.10),
              (1.94, sy*.967, 2.22), .020, 8)
        b.box('dark', (1.94, sy*.975, 2.245), (.14, .087, .205))
        b.box('metal', (1.868, sy*.975, 2.245), (.008, .070, .17))

    # Cab face: recessed black grille, slender silver horizontal slats,
    # small white lamps and amber turn indicators. No text/logo replacement.
    b.box('dark', (2.081, 0, 1.655), (.014, .78, .285))
    for z in (1.566, 1.627, 1.688, 1.749):
        b.box('metal', (2.091, 0, z), (.008, .71, .018))
    for sy in (-1, 1):
        b.box('dark', (2.083, sy*.581, 1.675), (.018, .30, .232))
        b.box('white', (2.095, sy*.585, 1.695), (.010, .245, .148))
        b.box('yellow', (2.098, sy*.705, 1.603), (.009, .061, .060))
    b.box('dark', (2.077, 0, 1.335), (.048, 1.57, .12))
    b.box('metal', (2.100, 0, 1.355), (.008, 1.43, .040))
    b.box('white', (2.090, 0, 1.435), (.009, .27, .10))
    # Two wiper blades, kept broad enough to survive the hero output scale.
    for sy in (-1, 1):
        b.rod('dark', (2.107, sy*.16, 1.995),
              (2.107, sy*.57, 2.044), .006, 6)

    # Rear bumper and tail lamps are fixed body details below the animated
    # rear door leaves, leaving their hinge travel and cargo opening clear.
    b.box('dark', (-2.019, 0, 1.375), (.073, 1.62, .11))
    b.box('metal', (-2.054, 0, 1.40), (.004, 1.48, .026))
    for sy in (-1, 1):
        b.box('dark', (-2.025, sy*.735, 1.62), (.050, .135, .24))
        b.box('yellow', (-2.052, sy*.735, 1.68), (.004, .091, .07))
        b.box('white', (-2.052, sy*.735, 1.57), (.004, .091, .06))
    for x in (-1.3, 1.5):
        for sy in (-1, 1):
            _tire(b, x, sy)
    objects = b.finish()
    for obj in objects:
        obj['dispatch_owner'] = _OWNER
        obj['source_vehicle_root'] = root.name
        obj['detail_only_preserves_animation'] = True
        # Smooth only cylindrical tire/hub surfaces; rectangular cab trim
        # and glazing stay crisply shaded. No modifiers touch source meshes.
        if obj.name.endswith('_dark') or obj.name.endswith('_metal'):
            for p in obj.data.polygons:
                center = p.center
                if center.z < 1.51 and abs(center.y) > .90:
                    p.use_smooth = True
    return objects


def add_details(scene, col, M):
    """Return additive DSP_ meshes for A04_PRIMARY and A05_SECONDARY only.

    Requires caller's citykit module and palette. Fails before mutation if a
    required root/source part/material is absent, rather than guessing a van.
    """
    required_mats = ('glass', 'dark', 'metal', 'white', 'yellow')
    missing_mats = [key for key in required_mats if key not in M]
    if missing_mats:
        raise ValueError('Outbound detail materials missing: ' + ', '.join(missing_mats))
    roots = []
    for name in _ROOTS:
        root = scene.objects.get(name)
        if root is None:
            raise ValueError('Required outbound root missing: ' + name)
        for suffix in ('_CAB', '_GLASS', '_FLOOR'):
            source = scene.objects.get(name + suffix)
            if source is None or source.parent != root:
                raise ValueError('Unexpected outbound source hierarchy: ' + name + suffix)
        roots.append(root)
    result = []
    for root in roots:
        existing = [o for o in scene.objects
                    if o.get('dispatch_owner') == _OWNER
                    and o.get('source_vehicle_root') == root.name]
        if existing:
            result.extend(existing)
        else:
            result.extend(_details(root, col, M))
    return result
