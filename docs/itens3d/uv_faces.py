# Os triangulos de UV e os vizinhos de cada face de uma malha da Meshy (docs/TAREFA_V3_ITENS_3D.md, secao 13), para o limpar_faces.py.
# Os vizinhos sao pelas arestas, com os vertices repetidos da costura dos UVs juntados (a malha da Meshy vem com eles separados).
# uso (da raiz): blender -b --factory-startup --python docs/itens3d/uv_faces.py -- <meshy.glb> <saida.json>
import json, sys, bpy, bmesh

ent, sai = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=ent)
o = next(p for p in bpy.context.scene.objects if p.type == "MESH")
bm = bmesh.new()
bm.from_mesh(o.data)
bmesh.ops.triangulate(bm, faces=bm.faces[:])
uv = bm.loops.layers.uv.active
tris = [[[l[uv].uv.x, 1 - l[uv].uv.y] for l in f.loops] for f in bm.faces]
bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-4)
bm.faces.ensure_lookup_table()
viz = [sorted({g.index for e in f.edges for g in e.link_faces if g.index != f.index}) for f in bm.faces]
if len(viz) != len(tris):
    raise SystemExit("juntar os vertices mudou o numero de faces")
json.dump({"triangulos": tris, "vizinhos": viz}, open(sai, "w"))
print("UV_FACES", len(tris), "faces")
