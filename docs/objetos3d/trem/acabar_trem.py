# O acabamento do vagao no trilho no Blender (docs/objetos3d/REFERENCIAS.md, secoes 1 e 5; o retrabalho dos objetos, 2026-11-07).
# A regra nova: a textura pintada da Meshy fica (nada de achatar cores); o conserto das manchas do toon e pelas normais.
#   1. a malha da Meshy, com os vertices repetidos soldados (as costuras da UV ficam, so a posicao e soldada para a normal ser continua);
#   2. as normais: copiadas (Data Transfer) de uma copia suavizada da propria malha (remesh em voxel + Smooth), o jeito das "normais
#      limpas" do toon: as superficies grandes (o teto, as paredes, os dormentes) ganham luz e sombra em areas grandes; depois as quinas
#      que a forma pede (mais de QUINA graus) ficam duras, para o teto nao "derreter" na parede;
#   3. o material so de cor, sem face dupla; o glTF separado, com a frente em +z (o exportador poe -y do Blender em +z) e o pivo na base.
# uso: blender -b --factory-startup --python acabar_trem.py -- <meshy.glb> <textura.png> <saida.gltf> <previa.png> [mistura] [quina]
import math, sys, bpy, bmesh
from mathutils import Matrix, Vector

args = sys.argv[sys.argv.index("--") + 1:]
ent, cor, sai, previa = args[:4]
MISTURA = float(args[4]) if len(args) > 4 else 1.0   # quanto da normal suavizada entra (1 = toda)
QUINA = float(args[5]) if len(args) > 5 else 180.0   # graus: acima disso a aresta fica dura (180 = nenhuma, a escolha do trem)
PASSOS = int(args[6]) if len(args) > 6 else 30   # as passadas do Smooth na copia (12 na rodada 1; 30 desde o revisor: o teto sem vincos)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=ent)
o = [p for p in bpy.context.scene.objects if p.type == "MESH"]
if len(o) != 1:
    raise SystemExit("a malha da Meshy devia ter 1 objeto: " + str(len(o)))
o = o[0]
o.data.transform(o.matrix_world)
o.matrix_world = Matrix.Identity(4)
o.parent = None
for p in [p for p in bpy.context.scene.objects if p is not o]:
    bpy.data.objects.remove(p)
o.name = o.data.name = "trilho"
me = o.data

# 1. solda as posicoes repetidas (a Meshy ja vem indexada; isto pega so as repeticoes exatas)
bm = bmesh.new(); bm.from_mesh(me)
antes = len(bm.verts)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
bm.to_mesh(me); bm.free()
me.calc_loop_triangles()
print("TREM vertices", antes, "->", len(me.vertices), "tri", len(me.loop_triangles))

# a base no chao e o centro em x/z (o jogo normaliza de novo; isto e so para a previa)
mn = Vector((min(v.co.x for v in me.vertices), min(v.co.y for v in me.vertices), min(v.co.z for v in me.vertices)))
mx = Vector((max(v.co.x for v in me.vertices), max(v.co.y for v in me.vertices), max(v.co.z for v in me.vertices)))
me.transform(Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
tam = mx - mn
print("TREM caixa", tuple(round(c, 3) for c in tam))

bpy.context.view_layer.objects.active = o
o.select_set(True)
bpy.ops.object.shade_smooth()

# 2. a copia suavizada, fonte das normais
if MISTURA > 0:
    fonte = o.copy(); fonte.data = me.copy(); fonte.name = "fonte_normais"
    bpy.context.scene.collection.objects.link(fonte)
    rm = fonte.modifiers.new("remesh", "REMESH"); rm.mode = "VOXEL"; rm.voxel_size = max(tam) / 90
    sm = fonte.modifiers.new("suave", "SMOOTH"); sm.factor = 1.0; sm.iterations = PASSOS
    bpy.ops.object.select_all(action="DESELECT")
    fonte.select_set(True); bpy.context.view_layer.objects.active = fonte
    for m in list(fonte.modifiers):
        bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.ops.object.shade_smooth()
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True); bpy.context.view_layer.objects.active = o
    dt = o.modifiers.new("normais", "DATA_TRANSFER")
    dt.object = fonte
    dt.use_loop_data = True
    dt.data_types_loops = {"CUSTOM_NORMAL"}
    dt.loop_mapping = "POLYINTERP_NEAREST"
    dt.mix_factor = MISTURA
    bpy.ops.object.modifier_apply(modifier=dt.name)
    bpy.data.objects.remove(fonte)

# as quinas duras: so onde a forma pede (o angulo entre as faces passa de QUINA)
if QUINA < 180:
    bm = bmesh.new(); bm.from_mesh(me)
    duras = 0
    for e in bm.edges:
        if len(e.link_faces) == 2 and math.degrees(e.calc_face_angle(0)) > QUINA:
            e.smooth = False; duras += 1
    bm.to_mesh(me); bm.free()
    print("TREM quinas duras", duras)
    if MISTURA <= 0:
        wn = o.modifiers.new("peso", "WEIGHTED_NORMAL"); wn.keep_sharp = True; wn.weight = 50
        bpy.ops.object.modifier_apply(modifier=wn.name)

# 3. o material so de cor
mat = me.materials[0]
mat.name = "trilho"
nos, ligs = mat.node_tree.nodes, mat.node_tree.links
bsdf = next(n for n in nos if n.type == "BSDF_PRINCIPLED")
for n in [n for n in nos if n.type == "TEX_IMAGE"]:
    nos.remove(n)
tex = nos.new("ShaderNodeTexImage")
img = bpy.data.images.load(cor)
img.name = "trilho_cor"
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
                          export_image_format="AUTO", export_materials="EXPORT", export_yup=True, export_normals=True)

cena = bpy.context.scene
cena.render.engine = "BLENDER_WORKBENCH"
cena.display.shading.light = "STUDIO"
cena.display.shading.color_type = "TEXTURE"
cena.render.resolution_x = cena.render.resolution_y = 512
cena.render.film_transparent = True
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
cena.collection.objects.link(cam)
cena.camera = cam
d = max(tam) * 1.9
cam.location = (d * 0.75, -d * 0.95, d * 0.75)
cam.rotation_euler = (math.radians(60), 0, math.radians(38))
cena.render.filepath = previa
bpy.ops.render.render(write_still=True)
print("EXPORTAR ok", sai)
