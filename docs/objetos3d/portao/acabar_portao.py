# O acabamento do portao da arena no Blender (docs/TAREFA_V3_LUGARES_3D.md, secao 14; a regra nova de docs/objetos3d/REFERENCIAS.md, secao 5).
# Diferente do consertar_portao.py de antes: a textura pintada da Meshy FICA (nada de achatar cores; os retoques vem do textura_portao.py).
# Aqui: a malha mais funda (PROFUNDIDADE, como o D-LG-4), os vertices repetidos soldados, a folha do portal plana e com a normal do plano,
# a ilha unica de UV do portal (o atlas apertado), as normais ponderadas, a base no chao e o centro no meio, a frente em +z do glTF.
# Grava os triangulos de UV do portal (<previa>_portal_uv.json), exporta o glTF separado e renderiza uma previa (Workbench).
# uso (da raiz): blender -b --factory-startup --python docs/objetos3d/portao/acabar_portao.py -- <meshy.glb> <cor.png> <saida.gltf> <previa.png> [profundidade]
#   (a deteccao do portal le a textura_base_color.png ao lado do meshy.glb)
import math, sys, bpy, bmesh
from mathutils import Matrix, Vector

args = sys.argv[sys.argv.index("--") + 1:]
ent, cor, sai, previa = args[:4]
PROFUNDIDADE = float(args[4]) if len(args) > 4 else 1.0
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=ent)
o = [p for p in bpy.context.scene.objects if p.type == "MESH"]
if len(o) != 1:
    raise SystemExit("a malha da Meshy devia ter 1 objeto: " + str(len(o)))
o = o[0]
o.data.transform(o.matrix_world)
o.data.transform(Matrix.Diagonal((1.0, PROFUNDIDADE, 1.0, 1.0)))
o.matrix_world = Matrix.Identity(4)
o.parent = None
for p in [p for p in bpy.context.scene.objects if p != o]:
    bpy.data.objects.remove(p)
o.name = o.data.name = "portao"

# a base no chao e o centro no meio (o carregarVariante normaliza de novo; isto deixa o arquivo certo sozinho)
xs = [v.co for v in o.data.vertices]
mn = Vector((min(v.x for v in xs), min(v.y for v in xs), min(v.z for v in xs)))
mx = Vector((max(v.x for v in xs), max(v.y for v in xs), max(v.z for v in xs)))
o.data.transform(Matrix.Translation((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z)))

# a limpeza leve da malha: soldar os vertices repetidos que nao sao costura de UV e tirar as faces degeneradas
bm = bmesh.new()
bm.from_mesh(o.data)
antes = len(bm.verts)
bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-6)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)

# o portal plano: a malha da Meshy dobra a folha do portal (uma ruga a esquerda, que o traco de nanquim desenha como um risco preto). As faces
# do portal sao as de textura ciano no centro de UV (o mesmo criterio da mascara, textura_portao.py); os vertices so do portal (sem face de
# pedra em volta) vao para o plano que melhor passa por eles. A borda com a pedra nao se mexe.
import numpy as np
# a deteccao usa sempre a textura crua da Meshy (textura_base_color.png ao lado do meshy.glb), e nao a cor retocada: assim o conjunto de faces
# do portal nao muda de uma rodada para outra (o retoque do textura_portao.py le os UVs daqui)
import os as _os
_img = bpy.data.images.load(_os.path.join(_os.path.dirname(ent), "textura_base_color.png"))
_w, _h = _img.size
_px = np.array(_img.pixels[:], dtype=np.float32).reshape(_h, _w, -1)
uv = bm.loops.layers.uv.active


def _ciano(f) -> bool:
    u = sum(l[uv].uv.x for l in f.loops) / len(f.loops)
    v = sum(l[uv].uv.y for l in f.loops) / len(f.loops)
    r, g, b = _px[min(int(v * _h), _h - 1), min(int(u * _w), _w - 1), :3]
    mx, mn = max(r, g, b), min(r, g, b)
    if mx < 0.55 or (mx - mn) / max(mx, 1e-6) < 0.30:
        return False
    d = max(mx - mn, 1e-6)
    hh = (((g - b) / d) % 6 if mx == r else ((b - r) / d + 2 if mx == g else (r - g) / d + 4)) / 6
    return 0.44 <= hh <= 0.56


portal = {f for f in bm.faces if _ciano(f)}
ciano = len(portal)
# a ruga tem a textura escura (o risco pintado pela Meshy), entao as faces dela nao passam no criterio da cor: o portal cresce pelas faces
# que tocam pelo menos duas faces do portal em aresta (fecha os buracos sem subir para a pedra), FECHAR_BURACOS vezes
FECHAR_BURACOS = 3
for _ in range(FECHAR_BURACOS):
    portal |= {f for f in bm.faces if f not in portal and sum(1 for e in f.edges for g in e.link_faces if g is not f and g in portal) >= 2}
print("ACABAR portal: ciano", ciano, "faces; com os buracos fechados", len(portal))
so_portal = [v for v in bm.verts if v.link_faces and all(f in portal for f in v.link_faces)]
if len(so_portal) >= 3:
    P = np.array([v.co[:] for v in so_portal])
    c = P.mean(0)
    n = np.linalg.svd(P - c)[2][2]
    dist = (P - c) @ n
    for v, d in zip(so_portal, dist):
        v.co = Vector(np.array(v.co[:]) - d * n)
    print("ACABAR portal", len(portal), "faces;", len(so_portal), "vertices aplainados; o maior desvio era", round(float(abs(dist).max()), 4),
          "; a normal do plano", tuple(round(float(x), 3) for x in n))
# a normal do portal: a do plano, para a frente (-y do Blender, que vira +z no glTF)
N_PORTAL = None
if len(so_portal) >= 3:
    N_PORTAL = Vector(n.tolist())
    if N_PORTAL.y > 0:
        N_PORTAL = -N_PORTAL
FACES_PORTAL = {f.index for f in portal}
# a ilha unica do portal: na Meshy o portal vinha em dezenas de ilhas pequenas de UV, encostadas em ilhas de pedra no atlas, e a filtragem
# na tela puxava a pedra para as emendas (linhas finas na diagonal no portal). O atlas inteiro aperta para APERTO da largura (o u * APERTO;
# o textura_portao.py aperta a imagem igual) e, na faixa livre a direita, o portal ganha uma ilha so, projetada de frente (x e z do
# Blender), com a proporcao do portal. O textura_portao.py pinta essa ilha com o portal da multivista (vistas/vista_1.png).
APERTO, MARGEM = 0.80, 0.012
for f in bm.faces:
    if f not in portal:
        for l in f.loops:
            l[uv].uv.x *= APERTO
_vs = {v for f in portal for v in f.verts}
_x0, _x1 = min(v.co.x for v in _vs), max(v.co.x for v in _vs)
_z0, _z1 = min(v.co.z for v in _vs), max(v.co.z for v in _vs)
_sw = 1 - APERTO - 2 * MARGEM
_sh = _sw * (_z1 - _z0) / (_x1 - _x0)
if _sh > 1 - 2 * MARGEM:
    _sh = 1 - 2 * MARGEM
    _sw = _sh * (_x1 - _x0) / (_z1 - _z0)
RANHURA = (APERTO + MARGEM, 1 - MARGEM - _sh, APERTO + MARGEM + _sw, 1 - MARGEM)
for f in portal:
    for l in f.loops:
        c = l.vert.co
        l[uv].uv = (RANHURA[0] + (c.x - _x0) / (_x1 - _x0) * _sw, RANHURA[1] + (c.z - _z0) / (_z1 - _z0) * _sh)
print("ACABAR ilha do portal: o atlas a", APERTO, "da largura; a ranhura (u0, v0, u1, v1)", tuple(round(r, 4) for r in RANHURA))
# os triangulos de UV das faces do portal (na ranhura), para o textura_portao.py tirar deles a mascara de luz: ao lado da previa,
# previa_portal_uv.json
import json as _json
_tris = []
for f in portal:
    us = [(l[uv].uv.x, l[uv].uv.y) for l in f.loops]
    for k in range(1, len(us) - 1):
        _tris.append([us[0], us[k], us[k + 1]])
with open(previa.replace(".png", "") + "_portal_uv.json", "w", encoding="utf-8") as _a:
    _json.dump({"faces": len(portal), "aperto": APERTO, "ranhura": RANHURA, "triangulos_uv": _tris}, _a)
bm.to_mesh(o.data)
bm.free()
print("ACABAR verts", antes, "->", len(o.data.vertices))

# as normais suavizadas: tudo liso e o modificador de normais ponderadas (a face grande manda), mantendo as quinas vivas acima de 60 graus
for f in o.data.polygons:
    f.use_smooth = True
bpy.context.view_layer.objects.active = o
o.select_set(True)
try:
    bpy.ops.object.shade_auto_smooth(angle=math.radians(60))
except Exception as e:  # noqa: BLE001
    print("ACABAR auto smooth falhou:", e)
wn = o.modifiers.new("normais", "WEIGHTED_NORMAL")
wn.keep_sharp = True
wn.weight = 50
for m in list(o.modifiers):
    bpy.ops.object.modifier_apply(modifier=m.name)
# o portal liso para o toon: as faces da borda do portal (que tocam a pedra e nao foram aplainadas) davam o tom escuro em manchas, num anel
# junto ao arco. Os cantos das faces do portal recebem a normal do plano; os outros cantos guardam a normal ponderada.
if N_PORTAL is not None:
    me = o.data
    cantos = [Vector(c.vector) for c in me.corner_normals]
    for f in me.polygons:
        if f.index in FACES_PORTAL:
            for li in f.loop_indices:
                cantos[li] = N_PORTAL
    me.normals_split_custom_set(cantos)
    print("ACABAR normais do portal:", len(FACES_PORTAL), "faces com a normal do plano")
o.data.calc_loop_triangles()
print("ACABAR tri", len(o.data.loop_triangles))

mat = o.data.materials[0]
mat.name = "portao"
nos, ligs = mat.node_tree.nodes, mat.node_tree.links
bsdf = next(n for n in nos if n.type == "BSDF_PRINCIPLED")
for n in [n for n in nos if n.type == "TEX_IMAGE"]:
    nos.remove(n)
tex = nos.new("ShaderNodeTexImage")
img = bpy.data.images.load(cor)
img.name = "portao_cor"
tex.image = img
for entrada in ("Normal", "Metallic", "Roughness", "Emission Color", "Alpha"):
    for lig in list(bsdf.inputs[entrada].links):
        ligs.remove(lig)
ligs.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
bsdf.inputs["Metallic"].default_value = 0.0
bsdf.inputs["Roughness"].default_value = 1.0
mat.use_backface_culling = True

bpy.ops.object.select_all(action="DESELECT")
o.select_set(True)
bpy.context.view_layer.objects.active = o
bpy.ops.export_scene.gltf(filepath=sai, export_format="GLTF_SEPARATE", use_selection=True, export_apply=True, export_normals=True,
                          export_image_format="AUTO", export_materials="EXPORT", export_yup=True)
cena = bpy.context.scene
cena.render.engine = "BLENDER_WORKBENCH"
cena.display.shading.light = "STUDIO"
cena.display.shading.color_type = "TEXTURE"
cena.render.resolution_x = 1024
cena.render.resolution_y = 512
cena.render.film_transparent = True
mx = max(o.dimensions)
alvo = Vector((0, 0, o.dimensions.z / 2))
for i, (ang, nome) in enumerate(((25, "frente"), (90, "lado"))):
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    cena.collection.objects.link(cam)
    cena.camera = cam
    a = math.radians(ang)
    d = mx * 2.6
    cam.location = alvo + Vector((math.sin(a) * d, -math.cos(a) * d, d * 0.35))
    dirv = alvo - cam.location
    cam.rotation_euler = dirv.to_track_quat("-Z", "Y").to_euler()
    cena.render.resolution_x = 512
    cena.render.filepath = previa.replace(".png", f"_{nome}.png")
    bpy.ops.render.render(write_still=True)
print("ACABAR ok", sai, "dim", tuple(round(d, 3) for d in o.dimensions))
