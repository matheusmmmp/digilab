# A exportacao da bola (docs/TAREFA_V3_ITENS_3D.md, secao 4.1, etapa 7): abre o .blend do conserto, liga a textura chapada a cor base,
# exporta o glTF separado (.gltf + .bin + .png, sem Draco, sem PBR alem da cor) e renderiza uma previa no Workbench com a textura.
# A marca de origem (G8; termos da Meshy, secao 2.4) entra depois, no asset.extras, pelo marcar_origem.py.
# uso (da raiz): blender -b <bola.blend> --python docs/itens3d/bola/exportar_bola.py -- <cor_chapada.png> <saida.gltf> <previa.png>
import math, sys, bpy

cor, sai, previa = sys.argv[sys.argv.index("--") + 1:]
bola = bpy.data.objects["bola"]
mat = bola.data.materials[0]
nos, ligs = mat.node_tree.nodes, mat.node_tree.links
tex = next(n for n in nos if n.type == "TEX_IMAGE")
img = bpy.data.images.load(cor)
img.name = "bola_cor"
tex.image = img
bsdf = next(n for n in nos if n.type == "BSDF_PRINCIPLED")
ligs.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
bsdf.inputs["Metallic"].default_value = 0.0
bsdf.inputs["Roughness"].default_value = 1.0
bola.location = (0, 0, 0)

bpy.ops.object.select_all(action="DESELECT")
bola.select_set(True)
bpy.context.view_layer.objects.active = bola
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
d = bola.dimensions.x * 1.9
cam.location = (d * math.cos(math.radians(-30)), d * math.sin(math.radians(-30)), d * 0.55)
cam.rotation_euler = (math.radians(62), 0, math.radians(60))
cena.render.filepath = previa
bpy.ops.render.render(write_still=True)
print("EXPORTAR ok", sai)
