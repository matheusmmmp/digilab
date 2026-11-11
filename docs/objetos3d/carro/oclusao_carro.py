# A oclusao ambiente do carro assada na UV (rodada 3 do carro, docs/TAREFA_V3_MUNDO_ENFEITES.md, secao 12).
# O Matheus achou o carro sem detalhe no jogo: a textura da Meshy e pintada mole, e o toon do jogo nao escurece as cavidades. A oclusao
# assada a partir da propria malha escurece as caixas de roda, o vao entre a roda e a lataria, a moldura das janelas e a base do tufo do
# teto; o estilizar_carro.py a multiplica na cor. Nao muda a malha nem a UV. Assada em LADO e gravada em SAI_LADO (cinza), que basta
# para a sombra borrada e cabe no repositorio.
#
# uso: blender --background --python docs/objetos3d/carro/oclusao_carro.py -- <carro.gltf> <oclusao.png> [lado] [amostras]
# (caminhos absolutos: o Blender grava relativo a pasta dele)
import sys, bpy

args = sys.argv[sys.argv.index("--") + 1:]
ent, sai = args[0], args[1]
LADO = int(args[2]) if len(args) > 2 else 2048
AMOSTRAS = int(args[3]) if len(args) > 3 else 128
SAI_LADO = 1024

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=ent)
objs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
if len(objs) != 1:
    raise SystemExit(f"esperava 1 malha, achei {len(objs)}")
ob = objs[0]
img = bpy.data.images.new("oclusao", LADO, LADO, alpha=False)
img.colorspace_settings.name = "Non-Color"
for mat in ob.data.materials:
    nos = mat.node_tree.nodes
    alvo = nos.new("ShaderNodeTexImage")
    alvo.image = img
    nos.active = alvo
cena = bpy.context.scene
cena.render.engine = "CYCLES"
cena.cycles.device = "CPU"
cena.cycles.samples = AMOSTRAS
cena.render.bake.margin = 16
bpy.context.view_layer.objects.active = ob
ob.select_set(True)
bpy.ops.object.bake(type="AO")
img.scale(SAI_LADO, SAI_LADO)
img.filepath_raw = sai
img.file_format = "PNG"
img.save()
print("OCLUSAO", LADO, "px,", AMOSTRAS, "amostras, gravada em", SAI_LADO, "px ->", sai)
