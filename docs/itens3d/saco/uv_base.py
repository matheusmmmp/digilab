# Os triangulos de UV da pedra da base do saco (docs/TAREFA_V3_ITENS_3D.md, secao 12): as faces da malha da Meshy com o centro abaixo de
# CORTE_Z_BAIXO (o mesmo limite do consertar_saco.py), em UV de 0 a 1 com v para baixo (como a imagem), para o pintar_base.py.
# uso (da raiz): blender -b --factory-startup --python docs/itens3d/saco/uv_base.py -- <meshy.glb> <saida.json>
import json, sys, bpy, bmesh

ent, sai = sys.argv[sys.argv.index("--") + 1:]
CORTE_Z_BAIXO = -0.7
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=ent)
o = next(p for p in bpy.context.scene.objects if p.type == "MESH")
bm = bmesh.new()
bm.from_mesh(o.data)
bm.transform(o.matrix_world)
bmesh.ops.triangulate(bm, faces=bm.faces[:])
uv = bm.loops.layers.uv.active
tris = [[[l[uv].uv.x, 1 - l[uv].uv.y] for l in f.loops] for f in bm.faces if f.calc_center_median().z < CORTE_Z_BAIXO]
json.dump({"fonte": "faces com o centro em z < %s no glb da Meshy" % CORTE_Z_BAIXO, "triangulos": tris}, open(sai, "w"))
print("UV_BASE", len(tris), "triangulos")
