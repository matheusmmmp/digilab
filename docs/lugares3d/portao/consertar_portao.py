# O conserto do lugar portao (o portao da arena) no Blender (docs/TAREFA_V3_LUGARES_3D.md, etapa P1). A malha da Meshy fica como veio (teto 2 414 dos marcos),
# so mais funda: a multivista deu o lado fino (o revisor: "o lado e uma torre estreita"), e a profundidade (o y do Blender) cresce PROFUNDIDADE
# vezes (PROPOSTO, SEM FONTE). O script tambem troca a textura pela chapada (achatar_cores.py), deixa o material so de cor e sem face dupla, exporta o glTF separado e
# renderiza uma previa.
# uso (da raiz): blender -b --factory-startup --python docs/lugares3d/portao/consertar_portao.py -- <meshy.glb> <cor_chapada.png> <saida.gltf> <previa.png>
import math, sys, bpy
from mathutils import Matrix

ent, cor, sai, previa = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=ent)
o = [p for p in bpy.context.scene.objects if p.type == "MESH"]
if len(o) != 1:
    raise SystemExit("a malha da Meshy devia ter 1 objeto: " + str(len(o)))
o = o[0]
o.data.transform(o.matrix_world)
PROFUNDIDADE = 1.5
o.data.transform(Matrix.Diagonal((1.0, PROFUNDIDADE, 1.0, 1.0)))
o.matrix_world = Matrix.Identity(4)
o.parent = None
o.name = o.data.name = "portao"
o.data.calc_loop_triangles()
print("ENFEITE tri", len(o.data.loop_triangles))

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
cam.location = (3.0, -3.8, 2.4)
cam.rotation_euler = (math.radians(62), 0, math.radians(38))
cena.render.filepath = previa
bpy.ops.render.render(write_still=True)
print("EXPORTAR ok", sai)
