# As previas do poste em blocos no Blender 4.5 (frente, lado, tres-quartos), com a textura sem filtro, como no jogo.
# uso (da raiz): blender -b --factory-startup --python docs/objetos3d/poste/blocos/previa_blocos.py -- <poste.gltf absoluto> <previa.png absoluto>
import math, sys, bpy
from mathutils import Vector

gl, previa = sys.argv[sys.argv.index("--") + 1:][:2]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=gl)
o = next(x for x in bpy.context.scene.objects if x.type == "MESH")
for n in o.data.materials[0].node_tree.nodes:
    if n.type == "TEX_IMAGE":
        n.interpolation = "Closest"
cena = bpy.context.scene
cena.render.engine = "BLENDER_WORKBENCH"
cena.display.shading.light = "STUDIO"
cena.display.shading.color_type = "TEXTURE"
cena.view_settings.view_transform = "Standard"
cena.render.film_transparent = True
cena.render.resolution_x, cena.render.resolution_y = 520, 900
alto = o.dimensions.z
alvo = Vector((0, 0, alto / 2))
for ang, nome in ((30, "tq"), (0, "frente"), (90, "lado")):
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); cena.collection.objects.link(cam); cena.camera = cam
    a = math.radians(ang); d = alto * 1.7
    cam.location = alvo + Vector((math.sin(a) * d, -math.cos(a) * d, d * 0.32))
    cam.rotation_euler = (alvo - cam.location).to_track_quat("-Z", "Y").to_euler()
    cena.render.filepath = previa.replace(".png", f"_{nome}.png")
    bpy.ops.render.render(write_still=True)
print("PREVIA ok", tuple(round(d, 3) for d in o.dimensions))
