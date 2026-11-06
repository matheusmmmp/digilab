# O conserto do saco no Blender (docs/TAREFA_V3_ITENS_3D.md, secao 4.1, etapas 4 a 7). Ao contrario da bola, a malha da Meshy fica: ela
# saiu com a forma do concept e abaixo do teto (2 082 triangulos; teto de 2 414). O que o script faz:
#   1. corta a malha em duas pecas pelo vao entre o poste e o saco: o `saco` (a corrente e o saco) sao as faces com o centro do lado do
#      saco (x < CORTE_X, no glb da Meshy), abaixo do braco (z < CORTE_Z) e acima da pedra da base (z > CORTE_Z_BAIXO); o resto e o `suporte` (a base, o poste e o braco). As fatias
#      por altura (docs/TAREFA_V3_ITENS_3D.md, secao 12) mostram o vao em toda a altura do saco: o saco so toca o suporte pela corrente, no braco;
#   2. gira 180 graus em volta da vertical, para o poste ficar do lado -x, como no saco procedural de antes (itens.ts, SACO_PENDURADO);
#   3. troca a textura pela chapada (achatar_cores.py), com o material so de cor (sem metal, rugosidade 1);
#   4. exporta o glTF separado (.gltf + .bin + .png) com os dois nos, e renderiza uma previa no Workbench.
# A marca de origem (G8) entra depois, pelo marcar_origem.py.
# uso (da raiz): blender -b --factory-startup --python docs/itens3d/saco/consertar_saco.py -- <meshy.glb> <cor_chapada.png> <saida.gltf> <previa.png>
import math, sys, bpy, bmesh
from mathutils import Matrix

ent, cor, sai, previa = sys.argv[sys.argv.index("--") + 1:]
CORTE_X, CORTE_Z, CORTE_Z_BAIXO = 0.05, 0.63, -0.7

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=ent)
fonte = [o for o in bpy.context.scene.objects if o.type == "MESH"]
if len(fonte) != 1:
    raise SystemExit(f"a malha da Meshy devia ter 1 objeto: {len(fonte)}")
o = fonte[0]
for p in list(o.users_collection[0].objects):
    if p != o and p.type != "MESH":
        bpy.data.objects.remove(p)
bpy.context.view_layer.objects.active = o
o.select_set(True)
o.parent = None
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# 1. o corte, pelo centro de cada face
bpy.ops.object.mode_set(mode="EDIT")
bm = bmesh.from_edit_mesh(o.data)
bpy.ops.mesh.select_all(action="DESELECT")
n = 0
for f in bm.faces:
    c = f.calc_center_median()
    f.select = c.x < CORTE_X and CORTE_Z_BAIXO < c.z < CORTE_Z
    n += f.select
bmesh.update_edit_mesh(o.data)
print("CORTE faces do saco", n, "de", len(bm.faces))
bpy.ops.mesh.separate(type="SELECTED")
bpy.ops.object.mode_set(mode="OBJECT")
pecas = [p for p in bpy.context.scene.objects if p.type == "MESH"]
if len(pecas) != 2:
    raise SystemExit("o corte devia dar duas pecas: " + str(len(pecas)))
saco = next(p for p in pecas if p != o)
o.name, o.data.name, saco.name, saco.data.name = "suporte", "suporte", "saco", "saco"

# 2. o giro de 180 graus e a base no chao, centrada
for p in pecas:
    p.data.transform(Matrix.Rotation(math.pi, 4, "Z"))
vs = [v.co for p in pecas for v in p.data.vertices]
cx = (min(v.x for v in vs) + max(v.x for v in vs)) / 2
cy = (min(v.y for v in vs) + max(v.y for v in vs)) / 2
z0 = min(v.z for v in vs)
for p in pecas:
    p.data.transform(Matrix.Translation((-cx, -cy, -z0)))
    p.data.update()
for p in pecas:
    xs = [v.co.x for v in p.data.vertices]
    p.data.calc_loop_triangles()
    print("PECA", p.name, "tri", len(p.data.loop_triangles), "x", round(min(xs), 3), round(max(xs), 3))

# 3. a textura chapada, um material so de cor
mats = {m for p in pecas for m in p.data.materials}
if len(mats) != 1:
    raise SystemExit("o saco devia ter um material: " + str(len(mats)))
mat = mats.pop()
mat.name = "saco"
nos, ligs = mat.node_tree.nodes, mat.node_tree.links
bsdf = next(n for n in nos if n.type == "BSDF_PRINCIPLED")
for n in [n for n in nos if n.type == "TEX_IMAGE"]:
    nos.remove(n)
tex = nos.new("ShaderNodeTexImage")
img = bpy.data.images.load(cor)
img.name = "saco_cor"
tex.image = img
for entrada in ("Normal", "Metallic", "Roughness", "Emission Color", "Alpha"):
    for lig in list(bsdf.inputs[entrada].links):
        ligs.remove(lig)
ligs.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
bsdf.inputs["Metallic"].default_value = 0.0
bsdf.inputs["Roughness"].default_value = 1.0
mat.use_backface_culling = True  # a malha e fechada: uma face so (doubleSided falso no glTF)

# 4. a exportacao e a previa
bpy.ops.object.select_all(action="SELECT")
bpy.ops.export_scene.gltf(filepath=sai, export_format="GLTF_SEPARATE", use_selection=True, export_apply=True,
                          export_image_format="AUTO", export_materials="EXPORT", export_yup=True)
cena = bpy.context.scene
cena.render.engine = "BLENDER_WORKBENCH"
cena.display.shading.light = "STUDIO"
cena.display.shading.color_type = "TEXTURE"
cena.render.resolution_x = cena.render.resolution_y = 512
cena.render.film_transparent = True
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
cena.collection.objects.link(cam)
cena.camera = cam
d = 4.2
cam.location = (d * math.cos(math.radians(-60)), d * math.sin(math.radians(-60)), 1.0 + d * 0.35)
cam.rotation_euler = (math.radians(75), 0, math.radians(30))
cena.render.filepath = previa
bpy.ops.render.render(write_still=True)
print("EXPORTAR ok", sai)
