"""One closed, truly spherical China ground shell and scoped ocean restoration.

The accepted source file is never opened or saved by this module. Call against
the build scene. All coordinates and radii below are SF_CN_LAYOUT-local metres.
"""
import array
import hashlib
import math
from collections import Counter, defaultdict
from pathlib import Path

import bpy
import bmesh
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree


OCEAN_RADIUS = 140.0
TOP_RADIUS = 141.25
BOTTOM_RADIUS = 139.70
DEFAULT_OUTLINE = [
    (-28, -15), (30, -15), (30, 3), (60, 3), (64, 22), (60, 48),
    (40, 64), (8, 71), (-26, 72), (-40, 73), (-62, 65),
    (-64, 35), (-65, 5), (-58, -10), (-28, -10),
]
# Exact bounding region of the previous China-only harbor ocean deformation,
# padded by centimetres for the accumulated floating-point transforms.
HARBOR_REGION = (-34.02, 109.41, -62.12, 39.42)


class SphericalSurface:
    """Analytical top surface and radial placement helpers."""
    def __init__(self, center, radius=TOP_RADIUS):
        self.center = Vector(center)
        self.radius = float(radius)

    def point(self, x, y):
        """Return top-shell position at the supplied local X/Y."""
        dx, dy = float(x)-self.center.x, float(y)-self.center.y
        residual = self.radius*self.radius-dx*dx-dy*dy
        if residual <= 0:
            raise ValueError('Point outside upper spherical hemisphere: %r' % ((x, y),))
        return Vector((x, y, self.center.z+math.sqrt(residual)))

    def surface(self, x, y):
        """Scalar top-shell Z at supplied local X/Y."""
        return self.point(x, y).z

    height = surface

    def normal(self, x, y):
        return (self.point(x, y)-self.center).normalized()

    def frame(self, x, y, yaw=0.0, height=0.0):
        """Rigid frame; +Z radial, yaw radians, height along radial normal."""
        p = self.point(x, y)
        n = (p-self.center).normalized()
        rotation = Vector((0, 0, 1)).rotation_difference(n).to_matrix().to_4x4()
        return Matrix.Translation(p+n*height) @ rotation @ Matrix.Rotation(yaw, 4, 'Z')

    def project(self, point, radial_offset=0.0):
        """Project an arbitrary local point radially onto R+radial_offset."""
        direction = Vector(point)-self.center
        if direction.length < 1e-9:
            raise ValueError('Cannot radially project globe centre')
        return self.center+direction.normalized()*(self.radius+radial_offset)

    def metadata(self):
        return {'center': list(self.center), 'radius': self.radius,
                'coordinate_system': 'SF_CN_LAYOUT local metres',
                'frame_height_direction': 'radial outward normal', 'yaw_units': 'radians'}


def globe_surface(scene=None, layout=None, radius=TOP_RADIUS):
    scene = scene or bpy.context.scene
    layout = layout or scene.objects['SF_CN_LAYOUT']
    ocean = scene.objects['EARTH_CONTINUOUS_OCEAN']
    local = layout.matrix_world.inverted() @ ocean.matrix_world
    scale = local.to_scale()
    if max(abs(v-1.0) for v in scale) > 1e-5:
        raise ValueError('Ocean/layout must share metre scale: %r' % list(scale))
    return SphericalSurface(local.translation, radius)


def _material(name, color):
    material = bpy.data.materials.new(name)
    material.diffuse_color = (*color, 1)
    material.use_nodes = True
    node = material.node_tree.nodes.get('Principled BSDF')
    node.inputs['Base Color'].default_value = (*color, 1)
    node.inputs['Roughness'].default_value = .66
    return material


def _mesh_report(mesh, surface, top_count, bottom_radius):
    adjacency = defaultdict(set)
    edges = Counter()
    for p in mesh.polygons:
        ids = list(p.vertices)
        for a, b in zip(ids, ids[1:]+ids[:1]):
            edges[tuple(sorted((a, b)))] += 1
            adjacency[a].add(b); adjacency[b].add(a)
    unseen = set(range(len(mesh.vertices))); components = 0
    while unseen:
        components += 1; stack = [unseen.pop()]
        while stack:
            for n in adjacency[stack.pop()]:
                if n in unseen:
                    unseen.remove(n); stack.append(n)
    top_error = max(abs((v.co-surface.center).length-surface.radius)
                    for v in mesh.vertices[:top_count])
    bottom_error = max(abs((v.co-surface.center).length-bottom_radius)
                       for v in mesh.vertices[top_count:])
    bm = bmesh.new(); bm.from_mesh(mesh)
    volume = bm.calc_volume(signed=True)
    bm.free()
    return {'vertices': len(mesh.vertices), 'edges': len(mesh.edges),
            'polygons': len(mesh.polygons), 'top_vertices': top_count,
            'connected_components': components,
            'nonmanifold_edges': sum(count != 2 for count in edges.values()),
            'signed_volume': volume, 'top_radius_max_error': top_error,
            'bottom_radius_max_error': bottom_error}


def build_unified_terrain(scene=None, layout=None, collection=None, *,
                          name='CNC_UNIFIED_GROUND', top_radius=TOP_RADIUS,
                          bottom_radius=BOTTOM_RADIUS, max_edge=.75,
                          material=None, side_material=None, outer_boundary=None):
    """Return (object, SphericalSurface, report); creates only a new shell.

    Covers the continuous outer China outline, including the complete original
    city/river core and the port front. There are no holes or internal cliffs;
    river and road markings should be surface inlays handled by the caller.
    """
    scene = scene or bpy.context.scene
    layout = layout or scene.objects['SF_CN_LAYOUT']
    collection = collection or scene.collection
    if bpy.data.objects.get(name):
        raise ValueError('Refusing to replace an existing terrain object: '+name)
    if not (0 < max_edge <= 5 and bottom_radius < top_radius):
        raise ValueError('Invalid tessellation size or shell radii')
    surface = globe_surface(scene, layout, top_radius)
    outline = [tuple(map(float, p)) for p in (outer_boundary or DEFAULT_OUTLINE)]
    area = sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(outline,outline[1:]+outline[:1]))*.5
    if area < 0: outline.reverse()
    bm = bmesh.new()
    verts = [bm.verts.new(surface.point(x, y)) for x,y in outline]
    bm.faces.new(verts)
    # Triangulate before each edge pass, so newly introduced diagonals are also
    # bounded. Reproject every midpoint onto the exact sphere after splitting.
    for iteration in range(14):
        bmesh.ops.triangulate(bm, faces=list(bm.faces))
        long_edges = [e for e in bm.edges if e.calc_length() > max_edge]
        if not long_edges: break
        bmesh.ops.subdivide_edges(bm, edges=long_edges, cuts=1, use_grid_fill=True)
        for v in bm.verts:
            v.co = surface.point(v.co.x, v.co.y)
    else:
        bm.free(); raise RuntimeError('Spherical tessellation did not converge')
    bmesh.ops.triangulate(bm, faces=list(bm.faces))
    bm.verts.ensure_lookup_table(); bm.verts.index_update()
    top = [v.co.copy() for v in bm.verts]
    faces = [tuple(v.index for v in f.verts) for f in bm.faces]
    # The input polygon is nonplanar; make all top triangles consistently radial
    # outward even if the tessellator selected an opposite initial winding.
    faces = [f if (top[f[1]]-top[f[0]]).cross(top[f[2]]-top[f[0]]).dot(
                (top[f[0]]+top[f[1]]+top[f[2]])/3-surface.center) > 0 else tuple(reversed(f))
             for f in faces]
    longest = max(e.calc_length() for e in bm.edges)
    bm.free()
    edge_faces = defaultdict(list)
    for f in faces:
        for a,b in zip(f,f[1:]+f[:1]): edge_faces[tuple(sorted((a,b)))].append((a,b))
    boundary = [directed[0] for directed in edge_faces.values() if len(directed)==1]
    n = len(top)
    # Radial extrusion gives constant shell thickness and radial outer walls;
    # a fixed-XY vertical extrusion would lean the outer edge off the globe.
    bottom = [surface.center+(v-surface.center)*(bottom_radius/top_radius) for v in top]
    bottom_faces = [tuple(n+i for i in reversed(f)) for f in faces]
    side_faces = [(a,a+n,b+n,b) for a,b in boundary]
    mesh = bpy.data.meshes.new(name+'_Mesh')
    mesh.from_pydata(top+bottom, [], faces+bottom_faces+side_faces)
    mesh.update()
    mesh.materials.append(material or _material(name+'_Paving', (.64,.64,.58)))
    mesh.materials.append(side_material or _material(name+'_Edge', (.73,.74,.69)))
    top_face_count = len(faces)
    custom = []
    for index,p in enumerate(mesh.polygons):
        is_top = index < top_face_count
        is_bottom = top_face_count <= index < 2*top_face_count
        p.use_smooth = is_top or is_bottom
        p.material_index = 0 if is_top else 1
        for vertex_index in p.vertices:
            if is_top: normal = (mesh.vertices[vertex_index].co-surface.center).normalized()
            elif is_bottom: normal = -(mesh.vertices[vertex_index].co-surface.center).normalized()
            else: normal = p.normal
            custom.append(tuple(normal))
    mesh.normals_split_custom_set(custom)
    obj = bpy.data.objects.new(name, mesh); collection.objects.link(obj); obj.parent=layout
    obj['cnc_owner']='cn-unified-curvature-v001'; obj['cnc_role']='unified_spherical_ground'
    obj['cnc_center']=list(surface.center); obj['cnc_top_radius']=top_radius
    obj['cnc_bottom_radius']=bottom_radius; obj['cnc_top_vertex_count']=n
    obj['cnc_top_face_count']=top_face_count
    report = _mesh_report(mesh, surface, n, bottom_radius)
    report.update(surface.metadata()); report.update({'bottom_radius':bottom_radius,
        'outer_boundary':outline, 'max_top_edge':longest, 'requested_max_edge':max_edge,
        'interior_walls':0, 'boundary_segments':len(boundary), 'tessellation_iterations':iteration,
        'radial_thickness':top_radius-bottom_radius})
    if report['connected_components']!=1 or report['nonmanifold_edges']!=0 or report['signed_volume']<=0:
        raise RuntimeError('Invalid unified spherical shell: '+str(report))
    if max(report['top_radius_max_error'],report['bottom_radius_max_error'])>.0001:
        raise RuntimeError('Spherical radius error exceeds0.1mm: '+str(report))
    return obj, surface, report


def _coord_hash(coords):
    values=array.array('f')
    for p in coords: values.extend(p)
    return hashlib.sha256(values.tobytes()).hexdigest()


def restore_cn_ocean(scene=None, layout=None, *, baseline_file=None,
                     baseline_mesh_name='Sphere.004', region=HARBOR_REGION,
                     minimum_local_z=-100.0, tolerance=.0001):
    """Undo only the old China harbor bulge, preserving far/US vertices exactly.

    Restores the existing refined mesh vertices to the original ocean surface at
    the same CN X/Y. Baseline triangles retain the original slight faceting, so
    no new seam is introduced at the patch boundary. Topology, materials and
    polygon smooth flags remain untouched. The mesh donor is removed afterward.
    """
    scene=scene or bpy.context.scene; layout=layout or scene.objects['SF_CN_LAYOUT']
    baseline_file=Path(baseline_file) if baseline_file else Path(__file__).resolve().parents[2]/'cn-port-layout-v001/inputs/base.blend'
    if not baseline_file.exists(): raise FileNotFoundError(baseline_file)
    expected='e29fe506211d1b7f647f3eee01e066e49319aaae29dffebc6e4ed82aca371af3'
    if hashlib.sha256(baseline_file.read_bytes()).hexdigest()!=expected:
        raise ValueError('Unexpected immutable ocean baseline hash')
    before_materials=set(bpy.data.materials); before_images=set(bpy.data.images)
    with bpy.data.libraries.load(str(baseline_file),link=False) as (src,dst):
        if baseline_mesh_name not in src.meshes: raise KeyError(baseline_mesh_name)
        dst.meshes=[baseline_mesh_name]
    donor=dst.meshes[0]
    inverse=layout.matrix_world.inverted()
    # The immutable baseline ocean object has identity world transform.
    base=BVHTree.FromPolygons([inverse@v.co for v in donor.vertices],
                             [tuple(p.vertices)for p in donor.polygons])
    bpy.data.meshes.remove(donor)
    for mat in list(bpy.data.materials):
        if mat not in before_materials and mat.users==0:bpy.data.materials.remove(mat)
    for image in list(bpy.data.images):
        if image not in before_images and image.users==0:bpy.data.images.remove(image)
    ocean=scene.objects['EARTH_CONTINUOUS_OCEAN']; mesh=ocean.data
    local=inverse@ocean.matrix_world; native=local.inverted()
    x0,x1,y0,y1=region; changed=[]; protected=[]; max_lower=0.0
    initial_flags=[p.use_smooth for p in mesh.polygons]
    for v in mesh.vertices:
        p=local@v.co
        if not(x0<=p.x<=x1 and y0<=p.y<=y1 and p.z>minimum_local_z):
            protected.append((v.index,v.co.copy()));continue
        hit=base.ray_cast(Vector((p.x,p.y,120)),Vector((0,0,-1)))[0]
        if hit is None:raise RuntimeError('No baseline ocean under harbor vertex')
        lower=p.z-hit.z
        if lower>tolerance:
            old=v.co.copy();v.co=native@Vector((p.x,p.y,hit.z))
            changed.append(v.index);max_lower=max(max_lower,lower)
    mesh.update()
    before_hash=_coord_hash([p for i,p in protected])
    after_hash=_coord_hash([mesh.vertices[i].co for i,p in protected])
    report={'baseline':str(baseline_file),'baseline_sha256':expected,
        'changed_vertices':len(changed),'changed_indices':changed,
        'protected_vertices':len(protected),'max_local_z_lowering':max_lower,
        'region_xy':list(region),'minimum_local_z':minimum_local_z,
        'protected_coordinates_before':before_hash,'protected_coordinates_after':after_hash,
        'far_and_US_coordinates_exact':before_hash==after_hash,
        'polygon_smooth_flags_exact':initial_flags==[p.use_smooth for p in mesh.polygons],
        'mesh_vertices':len(mesh.vertices),'mesh_polygons':len(mesh.polygons)}
    if not report['far_and_US_coordinates_exact']or not report['polygon_smooth_flags_exact']:
        raise RuntimeError('Ocean restoration changed protected data')
    return report
