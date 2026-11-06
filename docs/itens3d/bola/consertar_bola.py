# O conserto da bola no Blender (docs/TAREFA_V3_ITENS_3D.md, secao 4.1, etapas 4 a 6; decisao do Matheus em 2026-11-06: consertar no
# Blender, sem gerar de novo). A malha da Meshy saiu facetada e amassada; aqui ela vira so a fonte da cor:
#   1. uma esfera UV limpa (SEG x ANEIS, ~440 triangulos, abaixo do teto de 554 da G1), com sombreado suave e os UVs da propria esfera;
#   2. a cor da malha da Meshy passa para ela pelo bake de cor difusa (Cycles, "selecionado para ativo", so a cor, sem luz);
#   3. a imagem sai em LADO px, para o achatar_cores.py tirar a sombra embutida e os borroes.
# uso (da raiz): blender -b --factory-startup --python docs/itens3d/bola/consertar_bola.py -- <meshy.glb> <saida.png> <saida.blend>
import sys, bpy

ent, png, blend = sys.argv[sys.argv.index("--") + 1:]
SEG, ANEIS, LADO = 20, 12, 1024

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=ent)
fonte = [o for o in bpy.context.scene.objects if o.type == "MESH"]
if len(fonte) != 1:
    raise SystemExit(f"a malha da Meshy devia ter 1 objeto: {len(fonte)}")
fonte = fonte[0]
bpy.context.view_layer.update()
# o raio medio da fonte (a caixa ja e ~1,9 de lado); a esfera nova fica um pouco por dentro, e o bake procura para fora
xs = [fonte.matrix_world @ v.co for v in fonte.data.vertices]
cx, cy, cz = (sum(c[i] for c in xs) / len(xs) for i in range(3))
r = sum(((c[0] - cx) ** 2 + (c[1] - cy) ** 2 + (c[2] - cz) ** 2) ** 0.5 for c in xs) / len(xs)

bpy.ops.mesh.primitive_uv_sphere_add(segments=SEG, ring_count=ANEIS, radius=r * 0.97, location=(cx, cy, cz))
bola = bpy.context.active_object
bola.name = "bola"
bpy.ops.object.shade_smooth()
img = bpy.data.images.new("bola_cor", LADO, LADO)
mat = bpy.data.materials.new("bola")
mat.use_nodes = True
nos = mat.node_tree.nodes
tex = nos.new("ShaderNodeTexImage")
tex.image = img
nos.active = tex
bola.data.materials.append(mat)

cena = bpy.context.scene
cena.render.engine = "CYCLES"
cena.cycles.device = "CPU"
cena.cycles.samples = 16
bk = cena.render.bake
bk.use_selected_to_active = True
bk.cage_extrusion = r * 0.15
bk.max_ray_distance = r * 0.4
bk.margin = 8
bk.use_pass_direct = False
bk.use_pass_indirect = False
bk.use_pass_color = True
bpy.ops.object.select_all(action="DESELECT")
fonte.select_set(True)
bola.select_set(True)
bpy.context.view_layer.objects.active = bola
bpy.ops.object.bake(type="DIFFUSE")
img.filepath_raw = png
img.file_format = "PNG"
img.save()

bpy.data.objects.remove(fonte)
me = bola.data
me.calc_loop_triangles()
print("CONSERTO tri", len(me.loop_triangles), "raio", round(r, 4))
bpy.ops.wm.save_as_mainfile(filepath=blend)
