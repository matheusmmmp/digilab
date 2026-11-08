# O cais em voxel (docs/TAREFA_V3_LUGARES_3D.md, secao 17): o pedido do Matheus (2026-11-08), "mais digital, mais pixelado". A forma e a cor
# vem do cais retrabalhado (a malha da Meshy e a textura pintada com o realce, secao 16); daqui sai um modelo de blocos, como num editor de voxel.
#   1. a grade: N blocos no comprido (x); o bloco e cheio quando a superficie da malha passa a menos de LIMIAR lados de bloco do centro dele;
#   2. a cor de cada bloco: a media da textura nos pontos da malha mais perto do centro e de 6 pontos em volta (AMOSTRAS; uma cor por bloco);
#   2b. os grupos soltos de ate SOLTO blocos saem;
#   3. as faces: so as que dao para um bloco vazio, juntadas em retangulos por plano (o "greedy meshing"), sem olhar a cor: cada retangulo
#      leva um bloco de texels (um texel por face de bloco) num atlas quadrado, com 1 texel de borda repetida;
#   4. as normais: as do plano (cubo de verdade), a textura com o filtro Closest (o glTF sai com o sampler NEAREST: pixel duro na tela).
# Exporta o glTF separado e uma previa (Workbench). O atlas sai em RGB, sem paleta (uma cor por face de bloco ja e o pixel).
# uso (da raiz): blender -b --factory-startup --python docs/objetos3d/cais/voxel_cais.py -- <meshy.glb> <cor com o realce.png> <saida.gltf> <previa.png> <N>
import math, sys, bpy, bmesh
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import barycentric_transform

ent, cor, sai, previa, n_txt = sys.argv[sys.argv.index("--") + 1:][:5]
N = int(n_txt)
# o limiar (em lados de bloco): 0,5 deixa buraco nas tabuas finas e na diagonal; 0,6 fecha sem engordar muito. PROPOSTO, SEM FONTE
LIMIAR = 0.6
# a cor do bloco e a media de 7 amostras (o centro e um terco de bloco para cada lado nos 3 eixos): com uma so, o veio pintado da Meshy virava
# ruido de bloco a bloco. PROPOSTO, SEM FONTE
AMOSTRAS = [Vector((0, 0, 0))] + [Vector(v) / 3 for v in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))]

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=ent)
o = [p for p in bpy.context.scene.objects if p.type == "MESH"]
if len(o) != 1:
    raise SystemExit("a malha da Meshy devia ter 1 objeto: " + str(len(o)))
o = o[0]
o.data.transform(o.matrix_world)
o.matrix_world = Matrix.Identity(4)
xs = [v.co for v in o.data.vertices]
mn = Vector((min(v.x for v in xs), min(v.y for v in xs), min(v.z for v in xs)))
mx = Vector((max(v.x for v in xs), max(v.y for v in xs), max(v.z for v in xs)))
o.data.transform(Matrix.Translation((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z)))
mn, mx = Vector((-(mx.x - mn.x) / 2, -(mx.y - mn.y) / 2, 0)), Vector(((mx.x - mn.x) / 2, (mx.y - mn.y) / 2, mx.z - mn.z))

bm = bmesh.new()
bm.from_mesh(o.data)
bmesh.ops.triangulate(bm, faces=bm.faces)
bm.faces.ensure_lookup_table()
uvl = bm.loops.layers.uv.active
bvh = BVHTree.FromBMesh(bm)
img = bpy.data.images.load(cor)
W, H = img.size
px = list(img.pixels[:])

# 1 e 2: a grade e a cor de cada bloco
lado = (mx.x - mn.x) / N
dim = [max(1, math.ceil((mx[i] - mn[i]) / lado)) for i in range(3)]
cheio = {}
for i in range(dim[0]):
    for j in range(dim[1]):
        for k in range(dim[2]):
            c = Vector((mn.x + (i + 0.5) * lado, mn.y + (j + 0.5) * lado, mn.z + (k + 0.5) * lado))
            loc, _n, idx, dist = bvh.find_nearest(c, LIMIAR * lado)
            if loc is None:
                continue
            soma, n_am = [0.0, 0.0, 0.0], 0
            for dv in AMOSTRAS:
                loc2, _n2, idx2, _d2 = bvh.find_nearest(c + dv * lado)
                t = bm.faces[idx2]
                uv = barycentric_transform(loc2, *[l.vert.co for l in t.loops], *[l[uvl].uv.to_3d() for l in t.loops])
                x = min(max(int(uv.x * W), 0), W - 1)
                y = min(max(int(uv.y * H), 0), H - 1)
                b = (y * W + x) * 4
                soma = [soma[0] + px[b], soma[1] + px[b + 1], soma[2] + px[b + 2]]
                n_am += 1
            cheio[(i, j, k)] = tuple(v / n_am for v in soma)
# os blocos soltos (o revisor, rodada 1: "dentes e blocos pendurados"): saem os grupos ligados por face com ate SOLTO blocos. PROPOSTO, SEM FONTE
SOLTO = 3
VIZ = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))
visto, sair = set(), []
for p0 in list(cheio):
    if p0 in visto:
        continue
    grupo, pilha = [], [p0]
    visto.add(p0)
    while pilha:
        p = pilha.pop()
        grupo.append(p)
        for d in VIZ:
            q = (p[0] + d[0], p[1] + d[1], p[2] + d[2])
            if q in cheio and q not in visto:
                visto.add(q)
                pilha.append(q)
    if len(grupo) <= SOLTO:
        sair += grupo
for p in sair:
    del cheio[p]
print("VOXEL grade", dim, "lado", round(lado, 4), "blocos", len(cheio), "soltos tirados", len(sair))

# 3: as faces expostas, juntadas em retangulos por plano. Eixo a, lado s; (u, v) os outros dois eixos em ordem ciclica (u x v = +a)
EIXOS = {0: (1, 2), 1: (2, 0), 2: (0, 1)}
retangulos = []  # (a, s, k, u0, v0, w, h, cores[w][h])
for a in range(3):
    ua, va = EIXOS[a]
    for s in (1, -1):
        for k in range(dim[a]):
            mascara = {}
            for u in range(dim[ua]):
                for v in range(dim[va]):
                    p = [0, 0, 0]
                    p[a], p[ua], p[va] = k, u, v
                    p = tuple(p)
                    if p not in cheio:
                        continue
                    q = list(p)
                    q[a] += s
                    if tuple(q) in cheio:
                        continue
                    mascara[(u, v)] = cheio[p]
            usado = set()
            for u in range(dim[ua]):
                for v in range(dim[va]):
                    if (u, v) not in mascara or (u, v) in usado:
                        continue
                    w = 1
                    while (u + w, v) in mascara and (u + w, v) not in usado:
                        w += 1
                    h = 1
                    while all((u + d, v + h) in mascara and (u + d, v + h) not in usado for d in range(w)):
                        h += 1
                    for d in range(w):
                        for e in range(h):
                            usado.add((u + d, v + e))
                    retangulos.append((a, s, k, u, v, w, h, [[mascara[(u + d, v + e)] for e in range(h)] for d in range(w)]))
print("VOXEL retangulos", len(retangulos), "triangulos", 2 * len(retangulos))

# o atlas: prateleiras, do mais alto ao mais baixo, num quadrado potencia de 2; 1 texel de borda repetida em volta de cada bloco
ordem = sorted(range(len(retangulos)), key=lambda r: -retangulos[r][6])
S = 32
while True:
    pos, x, y, alt, ok = {}, 0, 0, 0, True
    for r in ordem:
        w, h = retangulos[r][5] + 2, retangulos[r][6] + 2
        if x + w > S:
            x, y, alt = 0, y + alt, 0
        if y + h > S or w > S:
            ok = False
            break
        pos[r] = (x + 1, y + 1)
        x += w
        alt = max(alt, h)
    if ok:
        break
    S *= 2
atlas = [0.0] * (S * S * 4)
for r, (bx, by) in pos.items():
    cores = retangulos[r][7]
    w, h = retangulos[r][5], retangulos[r][6]
    for d in range(-1, w + 1):
        for e in range(-1, h + 1):
            c = cores[min(max(d, 0), w - 1)][min(max(e, 0), h - 1)]
            b = ((by + e) * S + (bx + d)) * 4
            atlas[b:b + 4] = [c[0], c[1], c[2], 1.0]
print("VOXEL atlas", S, "px")
arq_atlas = sai.replace(".gltf", "_cor.png")
im = bpy.data.images.new("cais_cor", S, S, alpha=False)
im.pixels = atlas
im.filepath_raw = arq_atlas
im.file_format = "PNG"
im.save()

# a malha: 4 vertices por retangulo, a UV no bloco do atlas
verts, faces, uvs = [], [], []
for r, (a, s, k, u, v, w, h, _c) in enumerate(retangulos):
    ua, va = EIXOS[a]
    plano = k + 1 if s > 0 else k
    cantos = [(u, v), (u + w, v), (u + w, v + h), (u, v + h)]
    if s < 0:
        cantos = cantos[::-1]
    bx, by = pos[r]
    base = len(verts)
    for (cu, cv) in cantos:
        p = [0.0, 0.0, 0.0]
        p[a], p[ua], p[va] = plano, cu, cv
        verts.append(Vector((mn.x + p[0] * lado, mn.y + p[1] * lado, mn.z + p[2] * lado)))
        uvs.append(((bx + cu - u) / S, (by + cv - v) / S))
    faces.append(tuple(range(base, base + 4)))
me = bpy.data.meshes.new("cais")
me.from_pydata(verts, [], faces)
camada = me.uv_layers.new(name="UVMap")
for li, lo in enumerate(me.loops):
    camada.data[li].uv = uvs[lo.vertex_index]
bm2 = bmesh.new()
bm2.from_mesh(me)
bmesh.ops.triangulate(bm2, faces=bm2.faces)
bm2.to_mesh(me)
bm2.free()
for f in me.polygons:
    f.use_smooth = False
bpy.data.objects.remove(o)
vo = bpy.data.objects.new("cais", me)
bpy.context.scene.collection.objects.link(vo)

mat = bpy.data.materials.new("cais")
mat.use_nodes = True
nos, ligs = mat.node_tree.nodes, mat.node_tree.links
bsdf = next(n for n in nos if n.type == "BSDF_PRINCIPLED")
tex = nos.new("ShaderNodeTexImage")
tex.image = im
tex.interpolation = "Closest"
ligs.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
bsdf.inputs["Metallic"].default_value = 0.0
bsdf.inputs["Roughness"].default_value = 1.0
mat.use_backface_culling = True
me.materials.append(mat)

bpy.ops.object.select_all(action="DESELECT")
vo.select_set(True)
bpy.context.view_layer.objects.active = vo
bpy.ops.export_scene.gltf(filepath=sai, export_format="GLTF_SEPARATE", use_selection=True, export_normals=True,
                          export_image_format="AUTO", export_materials="EXPORT", export_yup=True)
cena = bpy.context.scene
cena.render.engine = "BLENDER_WORKBENCH"
cena.display.shading.light = "STUDIO"
cena.display.shading.color_type = "TEXTURE"
cena.render.resolution_x, cena.render.resolution_y = 768, 512
cena.render.film_transparent = True
m = max(vo.dimensions)
alvo = Vector((0, 0, vo.dimensions.z / 2))
for ang, nome in ((-35, "frente"), (145, "tras")):
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    cena.collection.objects.link(cam)
    cena.camera = cam
    an = math.radians(ang)
    d = m * 1.9
    cam.location = alvo + Vector((math.sin(an) * d, -math.cos(an) * d, d * 0.6))
    cam.rotation_euler = (alvo - cam.location).to_track_quat("-Z", "Y").to_euler()
    cena.render.filepath = previa.replace(".png", f"_{nome}.png")
    bpy.ops.render.render(write_still=True)
me.calc_loop_triangles()
print("VOXEL ok", sai, "tri", len(me.loop_triangles), "dim", tuple(round(d, 3) for d in vo.dimensions))
