# As faces de cima do cais (docs/TAREFA_V3_LUGARES_3D.md, secao 11; a ressalva do revisor: "as tabuas e os postes quase da mesma cor").
# Saem os indices das faces cuja normal aponta para cima (z do Blender > CIMA), na ordem do uv_faces.py (a mesma triangulacao), para o
# pintar_tabuas.py pintar a madeira delas com a cor da tabua. Limiar PROPOSTO, SEM FONTE.
# uso (da raiz): blender -b --factory-startup --python docs/lugares3d/cais/faces_tabuas.py -- <meshy.glb> <saida.json>
import json, sys, bpy, bmesh

ent, sai = sys.argv[sys.argv.index("--") + 1:]
CIMA = 0.7
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=ent)
o = next(p for p in bpy.context.scene.objects if p.type == "MESH")
o.data.transform(o.matrix_world)
bm = bmesh.new()
bm.from_mesh(o.data)
bmesh.ops.triangulate(bm, faces=bm.faces[:])
bm.normal_update()
cima = [i for i, f in enumerate(bm.faces) if f.normal.z > CIMA]
json.dump({"cima": cima}, open(sai, "w"))
print("TABUAS", len(cima), "faces de cima de", len(bm.faces))
