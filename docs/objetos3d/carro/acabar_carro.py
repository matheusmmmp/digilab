# O acabamento do carro abandonado no Blender (docs/TAREFA_V3_MUNDO_ENFEITES.md, secao 12; a regra nova de docs/objetos3d/REFERENCIAS.md,
# secao 5). Adaptado do acabar_portao.py da sessao do portao. Diferente do docs/enfeites/carro/consertar_carro.py de antes: a textura pintada
# da Meshy FICA (nada de achatar cores; a limpeza leve e a do textura_carro.py). Aqui: a malha como veio, girada em GIRO graus no eixo vertical
# para a frente do carro ficar em +z do glTF, os vertices repetidos soldados (as emendas da Meshy), as normais suavizadas por peso de face (o
# toon de dois tons sem manchas por face), a base no y = 0 e o centro no x = z = 0. Exporta o glTF separado com as normais e renderiza previas.
# uso (da raiz): blender -b --factory-startup --python docs/objetos3d/carro/acabar_carro.py -- <meshy.glb> <cor.png> <saida.gltf> <previa.png> [giro]
import math, sys, bpy, bmesh
from mathutils import Matrix, Vector

args = sys.argv[sys.argv.index("--") + 1:]
ent, cor, sai, previa = args[:4]
GIRO = float(args[4]) if len(args) > 4 else 0.0
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=ent)
o = [p for p in bpy.context.scene.objects if p.type == "MESH"]
if len(o) != 1:
    raise SystemExit("a malha da Meshy devia ter 1 objeto: " + str(len(o)))
o = o[0]
o.data.transform(o.matrix_world)
o.data.transform(Matrix.Rotation(math.radians(GIRO), 4, "Z"))
o.matrix_world = Matrix.Identity(4)
o.parent = None
for p in [p for p in bpy.context.scene.objects if p != o]:
    bpy.data.objects.remove(p)
o.name = o.data.name = "carro"

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
o.data.calc_loop_triangles()
print("ACABAR tri", len(o.data.loop_triangles))

mat = o.data.materials[0]
mat.name = "carro"
nos, ligs = mat.node_tree.nodes, mat.node_tree.links
bsdf = next(n for n in nos if n.type == "BSDF_PRINCIPLED")
for n in [n for n in nos if n.type == "TEX_IMAGE"]:
    nos.remove(n)
tex = nos.new("ShaderNodeTexImage")
img = bpy.data.images.load(cor)
img.name = "carro_cor"
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
for i, (ang, nome) in enumerate(((25, "frente"), (90, "lado"), (180, "tras"))):
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
