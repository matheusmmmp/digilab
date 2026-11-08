# O acabamento do cais retrabalhado no Blender (docs/TAREFA_V3_LUGARES_3D.md, secao 16; a regra nova de docs/objetos3d/REFERENCIAS.md, secao 5).
# Diferente do consertar_cais.py de antes: a textura pintada da Meshy FICA (nada de achatar cores; o retoque leve vem do textura_cais.py).
# Aqui: a malha como a Meshy deu (a frente em +z do glTF, como o cais de antes: o pier ao longo de x, o barco atras), a base no chao e o centro
# no meio, os vertices repetidos soldados e as faces degeneradas tiradas, as normais suavizadas (tudo liso + normais ponderadas, quinas vivas
# acima de ANGULO), o material so de cor e sem face dupla. Exporta o glTF separado e renderiza duas previas (Workbench).
# uso (da raiz): blender -b --factory-startup --python docs/objetos3d/cais/acabar_cais.py -- <meshy.glb> <cor.png> <saida.gltf> <previa.png>
import math, sys, bpy, bmesh
from mathutils import Matrix, Vector

ent, cor, sai, previa = sys.argv[sys.argv.index("--") + 1:][:4]
# o angulo das quinas vivas: as tabuas e os postes tem quinas de 90 graus, que ficam; as facetas da Meshy (menos que isso) somem no toon.
# PROPOSTO, SEM FONTE (o mesmo do portao)
ANGULO = 60
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=ent)
o = [p for p in bpy.context.scene.objects if p.type == "MESH"]
if len(o) != 1:
    raise SystemExit("a malha da Meshy devia ter 1 objeto: " + str(len(o)))
o = o[0]
o.data.transform(o.matrix_world)
o.matrix_world = Matrix.Identity(4)
o.parent = None
for p in [p for p in bpy.context.scene.objects if p != o]:
    bpy.data.objects.remove(p)
o.name = o.data.name = "cais"

# a base no chao e o centro no meio (o carregarVariante normaliza de novo; isto deixa o arquivo certo sozinho)
xs = [v.co for v in o.data.vertices]
mn = Vector((min(v.x for v in xs), min(v.y for v in xs), min(v.z for v in xs)))
mx = Vector((max(v.x for v in xs), max(v.y for v in xs), max(v.z for v in xs)))
o.data.transform(Matrix.Translation((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z)))

# a limpeza leve: soldar os vertices repetidos (as costuras de UV ficam, sao loops) e tirar as faces degeneradas
bm = bmesh.new()
bm.from_mesh(o.data)
antes = len(bm.verts)
bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-6)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
bm.to_mesh(o.data)
bm.free()
print("ACABAR verts", antes, "->", len(o.data.vertices))

# as normais suavizadas: tudo liso e o modificador de normais ponderadas (a face grande manda), as quinas vivas acima de ANGULO
for f in o.data.polygons:
    f.use_smooth = True
bpy.context.view_layer.objects.active = o
o.select_set(True)
bpy.ops.object.shade_auto_smooth(angle=math.radians(ANGULO))
wn = o.modifiers.new("normais", "WEIGHTED_NORMAL")
wn.keep_sharp = True
wn.weight = 50
for m in list(o.modifiers):
    bpy.ops.object.modifier_apply(modifier=m.name)
o.data.calc_loop_triangles()
print("ACABAR tri", len(o.data.loop_triangles))

mat = o.data.materials[0]
mat.name = "cais"
nos, ligs = mat.node_tree.nodes, mat.node_tree.links
bsdf = next(n for n in nos if n.type == "BSDF_PRINCIPLED")
for n in [n for n in nos if n.type == "TEX_IMAGE"]:
    nos.remove(n)
tex = nos.new("ShaderNodeTexImage")
img = bpy.data.images.load(cor)
img.name = "cais_cor"
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
cena.render.resolution_x = 768
cena.render.resolution_y = 512
cena.render.film_transparent = True
m = max(o.dimensions)
alvo = Vector((0, 0, o.dimensions.z / 2))
for ang, nome in ((-35, "frente"), (145, "tras")):
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    cena.collection.objects.link(cam)
    cena.camera = cam
    a = math.radians(ang)
    d = m * 1.9
    cam.location = alvo + Vector((math.sin(a) * d, -math.cos(a) * d, d * 0.6))
    cam.rotation_euler = (alvo - cam.location).to_track_quat("-Z", "Y").to_euler()
    cena.render.filepath = previa.replace(".png", f"_{nome}.png")
    bpy.ops.render.render(write_still=True)
print("ACABAR ok", sai, "dim", tuple(round(d, 3) for d in o.dimensions))
