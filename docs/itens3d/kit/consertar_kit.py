# O conserto do kit medico no Blender (docs/TAREFA_V3_ITENS_3D.md, secao 13). A malha da Meshy fica (513 triangulos; teto 554), mas a
# textura dela nao tem a cruz vermelha (nenhum pixel vermelho), e a cruz e o que faz o kit ser lido como kit. O que o script faz:
#   1. encolhe os UVs para 96 % (em volta de u = v = 0), como o prepara_textura_kit.py encolheu a imagem: o mapeamento nao muda e sobra
#      uma faixa livre na borda, onde esta o quadrado vermelho;
#   2. poe uma cruz plana (dois retangulos, 4 triangulos) sobre a tampa, na metade da frente (-y no Blender, +z no jogo, o lado da
#      camera; a alca de corda passa no meio, em y ~ 0, e cobria a cruz no centro), um pouco acima do ponto mais alto da tampa sob ela (raios de cima
#      para baixo, de Z_RAIO, que passam pela alca de corda ate a tampa, abaixo de Z_TAMPA; as fatias da secao 13 poem a tampa em z ~ 0,5), com os UVs no quadrado vermelho;
#   3. a textura chapada, um material so de cor, sem face dupla; exporta o glTF separado e renderiza uma previa.
# uso (da raiz): blender -b --factory-startup --python docs/itens3d/kit/consertar_kit.py -- <meshy.glb> <cor_chapada.png> <saida.gltf> <previa.png>
import math, sys, bpy, bmesh
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

ent, cor, sai, previa = sys.argv[sys.argv.index("--") + 1:]
ENCOLHE = 0.96
VERMELHO_UV = (1006 / 1024, 1 - 18 / 1024)   # o centro do quadrado vermelho (prepara_textura_kit.py), v para cima
CENTRO, BRACO, LARGURA, ACIMA, Z_RAIO, Z_TAMPA = (0.0, -0.36), 0.30, 0.14, 0.012, 0.95, 0.6

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=ent)
o = [p for p in bpy.context.scene.objects if p.type == "MESH"]
if len(o) != 1:
    raise SystemExit("a malha da Meshy devia ter 1 objeto: " + str(len(o)))
o = o[0]
o.data.transform(o.matrix_world)
o.matrix_world = Matrix.Identity(4)
o.parent = None

bm = bmesh.new()
bm.from_mesh(o.data)
uv = bm.loops.layers.uv.active
for f in bm.faces:
    for l in f.loops:
        l[uv].uv = l[uv].uv * ENCOLHE

# a altura da tampa sob a cruz
arvore = BVHTree.FromBMesh(bm)
zs = []
for dx in (-BRACO, -BRACO / 2, 0, BRACO / 2, BRACO):
    for dy in (-LARGURA, 0, LARGURA):
        for x, y in ((CENTRO[0] + dx, CENTRO[1] + dy), (CENTRO[0] + dy, CENTRO[1] + dx)):
            hit, z0 = (None,), Z_RAIO
            while True:   # o raio atravessa a alca de corda (acima de Z_TAMPA) ate a tampa
                hit = arvore.ray_cast(Vector((x, y, z0)), Vector((0, 0, -1)))
                if hit[0] is None:
                    raise SystemExit(f"o raio em ({x:.2f}, {y:.2f}) nao achou a tampa")
                if hit[0].z < Z_TAMPA:
                    break
                z0 = hit[0].z - 1e-3
            zs.append(hit[0].z)
if max(zs) - min(zs) > 0.2:
    raise SystemExit(f"a cruz sai da tampa: os raios vao de {min(zs):.3f} a {max(zs):.3f}")
z = max(zs) + ACIMA
print("TAMPA z", round(min(zs), 3), "a", round(max(zs), 3), "; cruz em", round(z, 3))

cx, cy = CENTRO
for (ax, ay) in ((BRACO, LARGURA), (LARGURA, BRACO)):
    vs = [bm.verts.new((cx + sx * ax, cy + sy * ay, z)) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    f = bm.faces.new(vs)
    f.material_index = 0
    for l in f.loops:
        l[uv].uv = VERMELHO_UV
bm.normal_update()
bm.to_mesh(o.data)
o.data.update()
o.data.calc_loop_triangles()
print("KIT tri", len(o.data.loop_triangles))

mat = o.data.materials[0]
mat.name = "kit"
nos, ligs = mat.node_tree.nodes, mat.node_tree.links
bsdf = next(n for n in nos if n.type == "BSDF_PRINCIPLED")
for n in [n for n in nos if n.type == "TEX_IMAGE"]:
    nos.remove(n)
tex = nos.new("ShaderNodeTexImage")
img = bpy.data.images.load(cor)
img.name = "kit_cor"
tex.image = img
for entrada in ("Normal", "Metallic", "Roughness", "Emission Color", "Alpha"):
    for lig in list(bsdf.inputs[entrada].links):
        ligs.remove(lig)
ligs.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
bsdf.inputs["Metallic"].default_value = 0.0
bsdf.inputs["Roughness"].default_value = 1.0
mat.use_backface_culling = True
o.name = o.data.name = "kit"

bpy.ops.object.select_all(action="DESELECT")
o.select_set(True)
bpy.context.view_layer.objects.active = o
bpy.ops.export_scene.gltf(filepath=sai, export_format="GLTF_SEPARATE", use_selection=True, export_apply=True,
                          export_image_format="AUTO", export_materials="EXPORT", export_yup=True)
cena = bpy.context.scene
cena.render.engine = "BLENDER_WORKBENCH"
cena.display.shading.light = "FLAT"
cena.display.shading.color_type = "TEXTURE"
cena.render.resolution_x = cena.render.resolution_y = 512
cena.render.film_transparent = True
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
cena.collection.objects.link(cam)
cena.camera = cam
cam.location = (2.6, -3.4, 3.4)
cam.rotation_euler = (math.radians(52), 0, math.radians(37))
cena.render.filepath = previa
bpy.ops.render.render(write_still=True)
print("EXPORTAR ok", sai)
