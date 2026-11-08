# O acabamento da barraca refeita no Blender (docs/TAREFA_V3_LUGARES_3D.md, secao do retrabalho; docs/objetos3d/REFERENCIAS.md, secao 5).
# A forma da Meshy fica como veio (o vao da porta ja e um recuo na malha). O script funde os vertices repetidos (as UVs ficam por canto),
# suaviza as normais pelo angulo (para o toon de dois tons nao manchar por face), poe o pivo no centro da base e a frente (a porta) em +z
# do glTF, troca a textura pela pintada (textura_barraca.py), deixa o material so de cor e exporta o glTF separado.
# A Meshy nao fez chao por dentro: o script poe um chao de 2 triangulos logo acima da lona, com as UVs de <chao_uv.json>.
# O forro de dentro (o parecer do revisor, item 1): no jogo a camera ve a porta de lado e de baixo, e o olhar saia por uma fresta da
# parede da Meshy (o fundo aparecia pela porta). Um tronco de piramide escuro, virado para dentro, logo dentro da lona: as duas laterais,
# o fundo e o teto (8 triangulos), com a UV no escuro do fundo do chao. Medidas por raios: a lona vai de x = +-0,58 no chao a +-0,45 a
# z = 0,58, o fundo de y = 0,52 a 0,43, o teto dos cantos a z ~0,6. O fundo do forro fica mais a frente (y = 0,30 no chao, 0,24 no
# teto), e a parede esquerda em diagonal, do batente esquerdo da porta (x = -0,32) ao fundo perto do meio (x = -0,10): no ponto da
# barraca, as pedras do barranco atras dela entram ~1 celula pelo canto do fundo a esquerda da lona, e a camera do jogo ve a porta pela
# direita, olhando para esse canto; o forro fica na frente das pedras e as esconde.
# uso: blender -b --factory-startup --python acabar_barraca.py -- <meshy.glb> <cor.png> <chao_uv.json> <saida.gltf> <angulo_suave_graus>
import json, math, sys, bpy, bmesh
from mathutils import Matrix, Vector

ent, cor, chao_uv, sai, ang = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=ent)
obs = [p for p in bpy.context.scene.objects if p.type == "MESH"]
if len(obs) != 1:
    raise SystemExit("a malha da Meshy devia ter 1 objeto: " + str(len(obs)))
o = obs[0]
o.data.transform(o.matrix_world)
o.parent = None
o.matrix_world = Matrix.Identity(4)
for p in [p for p in bpy.context.scene.objects if p != o]:
    bpy.data.objects.remove(p)
o.name = o.data.name = "barraca"

bm = bmesh.new()
bm.from_mesh(o.data)
antes = len(bm.verts)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
# a porta da Meshy ja olha para -y do Blender (+z do glTF); o pivo vai para o centro da caixa no chao
xs, ys, zs = ([v.co[i] for v in bm.verts] for i in range(3))
desl = Vector((-(min(xs) + max(xs)) / 2, -(min(ys) + max(ys)) / 2, -min(zs)))
for v in bm.verts:
    v.co += desl
# o chao de dentro (coordenadas ja com o pivo na base), medido por raios: o interior vai de x = +-0,60 e de y = -0,57 (a porta) a 0,52
# (a parede do fundo, com a face de fora em 0,54), e as paredes comecam a z = 0,035; o chao fica a 0,042, de x = +-0,59, da soleira
# (-0,59) ate o fundo do forro (0,32, um pouco atras dele, para nao abrir fresta)
Z = 0.042
cantos = [(-0.59, -0.59), (0.59, -0.59), (0.59, 0.32), (-0.59, 0.32)]
vs = [bm.verts.new((x, y, Z)) for x, y in cantos]
uvs = json.load(open(chao_uv))["cantos"]
camada = bm.loops.layers.uv.active
for tri in ((0, 1, 2), (0, 2, 3)):
    f = bm.faces.new([vs[i] for i in tri])
    f.material_index = 0
    f.smooth = False
    for lo, i in zip(f.loops, tri):
        lo[camada].uv = uvs[i]
Zf, Zt = 0.045, 0.56
base = [(-0.32, -0.56), (0.575, -0.56), (0.575, 0.30), (-0.10, 0.30)]          # frente-esq., frente-dir., fundo-dir., fundo-esq.
topo = [(-0.26, -0.46), (0.40, -0.46), (0.40, 0.24), (-0.08, 0.24)]
vb = [bm.verts.new((x, y, Zf)) for x, y in base]
vt = [bm.verts.new((x, y, Zt)) for x, y in topo]
uv_escuro = [(uvs[2][0] + uvs[3][0]) / 2, (uvs[2][1] + uvs[3][1]) / 2]
centro = Vector((0, -0.03, 0.3))
for quad in ((vb[0], vb[3], vt[3], vt[0]), (vb[1], vb[2], vt[2], vt[1]), (vb[3], vb[2], vt[2], vt[3]), tuple(vt)):
    for tri in ((0, 1, 2), (0, 2, 3)):
        f = bm.faces.new([quad[i] for i in tri])
        f.normal_update()
        if f.normal.dot(centro - f.calc_center_median()) < 0:  # virada para dentro
            f.normal_flip()
        f.material_index = 0
        f.smooth = False
        for lo in f.loops:
            lo[camada].uv = uv_escuro
bm.normal_update()
bm.to_mesh(o.data)
bm.free()
print("FUNDIR", antes, "->", len(o.data.vertices))
o.data.calc_loop_triangles()
print("TRI", len(o.data.loop_triangles))

bpy.ops.object.select_all(action="DESELECT")
o.select_set(True)
bpy.context.view_layer.objects.active = o
bpy.ops.object.shade_smooth_by_angle(angle=math.radians(float(ang)), keep_sharp_edges=False)

mat = o.data.materials[0]
mat.name = "barraca"
nos, ligs = mat.node_tree.nodes, mat.node_tree.links
bsdf = next(n for n in nos if n.type == "BSDF_PRINCIPLED")
for n in [n for n in nos if n.type == "TEX_IMAGE"]:
    nos.remove(n)
tex = nos.new("ShaderNodeTexImage")
img = bpy.data.images.load(cor)
img.name = "barraca_cor"
tex.image = img
for entrada in ("Normal", "Metallic", "Roughness", "Emission Color", "Alpha"):
    for lig in list(bsdf.inputs[entrada].links):
        ligs.remove(lig)
ligs.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
bsdf.inputs["Metallic"].default_value = 0.0
bsdf.inputs["Roughness"].default_value = 1.0
mat.use_backface_culling = True

bpy.ops.export_scene.gltf(filepath=sai, export_format="GLTF_SEPARATE", use_selection=True, export_apply=True,
                          export_image_format="AUTO", export_materials="EXPORT", export_yup=True, export_normals=True,
                          export_texcoords=True, export_tangents=False)
print("EXPORTAR ok", sai)
