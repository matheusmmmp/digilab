# As faces do corpo da lata gigante (docs/TAREFA_V3_MAPA_DIGITAL.md, etapa D4), para o pintar_corpo.py: para cada face, na mesma ordem
# das faces trianguladas do uv_faces.py, se ela e do corpo (a parede de lado, longe da tampa e do fundo de aluminio). O corpo e a face com a
# normal quase de lado (|nz| abaixo de NORMAL) e o centro entre as alturas da parede (a fracao MARGEM da altura cortada em cima e embaixo).
# Os numeros sao PROPOSTOS, SEM FONTE: tirados olhando a malha (a borda de aluminio ocupa ~12 % da altura em cima e ~8 % embaixo).
# uso (da raiz): blender -b --factory-startup --python docs/mapa_digital/lata/faces_corpo.py -- <meshy.glb> <saida.json>
import json, sys, bpy, bmesh

NORMAL = 0.45
MARGEM = (0.08, 0.12)  # (embaixo, em cima)

ent, sai = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=ent)
o = next(p for p in bpy.context.scene.objects if p.type == "MESH")
bm = bmesh.new()
bm.from_mesh(o.data)
bm.transform(o.matrix_world)
bmesh.ops.triangulate(bm, faces=bm.faces[:])
bm.faces.ensure_lookup_table()
zs = [v.co.z for v in bm.verts]
z0, z1 = min(zs), max(zs)
baixo, cima = z0 + MARGEM[0] * (z1 - z0), z1 - MARGEM[1] * (z1 - z0)
corpo = [abs(f.normal.z) < NORMAL and baixo < f.calc_center_median().z < cima for f in bm.faces]
json.dump({"corpo": corpo, "altura": [z0, z1]}, open(sai, "w"))
print("FACES_CORPO", sum(corpo), "de", len(corpo), "faces no corpo")
