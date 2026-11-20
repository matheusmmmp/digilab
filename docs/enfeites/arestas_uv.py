# As faces e as arestas de uma malha da Meshy no espaco da textura (docs/TAREFA_V3_MUNDO_ENFEITES.md, secao 11), para o tracar_linhas.py:
#   - "triangulos": o triangulo de UV de cada face (u, v de 0 a 1, v para baixo, como a imagem), na ordem das faces trianguladas;
#   - "arestas": cada aresta da malha com os vertices da costura juntados: as faces dos dois lados, o angulo entre elas (graus; 180 numa
#     borda solta), o comprimento (no glb da Meshy, que tem ~1,9 de lado) e o segmento de UV da aresta em cada face (a costura dos UVs da a mesma aresta em lugares diferentes da imagem).
# uso (da raiz): blender -b --factory-startup --python docs/enfeites/arestas_uv.py -- <meshy.glb> <saida.json>
import json, math, sys, bpy, bmesh

ent, sai = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=ent)
o = next(p for p in bpy.context.scene.objects if p.type == "MESH")
bm = bmesh.new()
bm.from_mesh(o.data)
bm.transform(o.matrix_world)
bmesh.ops.triangulate(bm, faces=bm.faces[:])
uv = bm.loops.layers.uv.active
img = lambda c: [c.x, 1 - c.y]
tris = [[img(l[uv].uv) for l in f.loops] for f in bm.faces]
bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-4)
bm.faces.ensure_lookup_table()
if len(bm.faces) != len(tris):
    raise SystemExit("juntar os vertices mudou o numero de faces")
arestas = []
for e in bm.edges:
    fs = list(e.link_faces)
    if not fs:
        continue
    ang = 180.0 if len(fs) != 2 else math.degrees(e.calc_face_angle(0.0))
    segs = []
    for f in fs:
        ls = [l for l in f.loops if l.vert in e.verts]
        segs.append([img(ls[0][uv].uv), img(ls[1][uv].uv)])
    arestas.append({"faces": [f.index for f in fs], "angulo": round(ang, 2), "comp": round(e.calc_length(), 4), "segs": segs})
json.dump({"triangulos": tris, "arestas": arestas}, open(sai, "w"))
print("ARESTAS_UV", len(tris), "faces,", len(arestas), "arestas")
