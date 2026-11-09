# As mascaras de regiao do carro, no espaco da textura (docs/TAREFA_V3_MUNDO_ENFEITES.md, secao 12), para o retoque leve do textura_carro.py
# pedido pelo revisor (APROVA COM RESSALVA): pela geometria da malha da Meshy (girada como no acabar_carro.py, a frente em -y do Blender),
# cada triangulo cai numa regiao e e pintado na mascara pelos UVs dele:
#   R: a grama do teto (o centro do triangulo acima de Z_GRAMA);
#   G: a frente na altura dos farois (o centro com y < Y_FRENTE e z entre Z_FAROL);
#   B: a boca do teto (o centro acima de Z_TETO e a menos de R_BOCA do pe da grama, no plano).
# Os limiares sao PROPOSTO, SEM FONTE: medidos no histograma das alturas desta malha (o teto em ~0,31 a 0,46, a grama acima).
# uso (da raiz): blender -b --factory-startup --python docs/objetos3d/carro/mascaras_carro.py -- <meshy.glb> <mascaras.png> [lado]
import math, sys, bpy
import numpy as np
from mathutils import Matrix

args = sys.argv[sys.argv.index("--") + 1:]
ent, sai = args[:2]
LADO = int(args[2]) if len(args) > 2 else 2048
Z_GRAMA, Z_TETO, R_BOCA, Y_FRENTE, Z_FAROL = 0.48, 0.38, 0.22, -0.80, (-0.55, -0.05)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=ent)
o = [p for p in bpy.context.scene.objects if p.type == "MESH"][0]
o.data.transform(o.matrix_world)
o.data.transform(Matrix.Rotation(math.radians(90), 4, "Z"))
me = o.data
me.calc_loop_triangles()
uv = me.uv_layers.active.data
pe = [v.co for v in me.vertices if v.co.z > Z_GRAMA]
cx, cy = sum(p.x for p in pe) / len(pe), sum(p.y for p in pe) / len(pe)
print("MASCARA pe da grama", round(cx, 3), round(cy, 3), len(pe), "vertices")
m = np.zeros((LADO, LADO, 3), np.uint8)
yy, xx = np.mgrid[0:LADO, 0:LADO]
cont = [0, 0, 0]
for t in me.loop_triangles:
    c = sum((me.vertices[i].co for i in t.vertices), me.vertices[t.vertices[0]].co * 0) / 3
    canais = []
    if c.z > Z_GRAMA:
        canais.append(0)
    if c.y < Y_FRENTE and Z_FAROL[0] < c.z < Z_FAROL[1]:
        canais.append(1)
    if Z_TETO < c.z <= Z_GRAMA and math.hypot(c.x - cx, c.y - cy) < R_BOCA:
        canais.append(2)
    if not canais:
        continue
    p = [(uv[l].uv[0] * LADO, (1 - uv[l].uv[1]) * LADO) for l in t.loops]
    x0, x1 = int(max(0, min(q[0] for q in p) - 1)), int(min(LADO - 1, max(q[0] for q in p) + 1))
    y0, y1 = int(max(0, min(q[1] for q in p) - 1)), int(min(LADO - 1, max(q[1] for q in p) + 1))
    (ax, ay), (bx, by), (qx, qy) = p
    d = (by - qy) * (ax - qx) + (qx - bx) * (ay - qy)
    if abs(d) < 1e-9:
        continue
    X, Y = xx[y0:y1 + 1, x0:x1 + 1] + 0.5, yy[y0:y1 + 1, x0:x1 + 1] + 0.5
    w1 = ((by - qy) * (X - qx) + (qx - bx) * (Y - qy)) / d
    w2 = ((qy - ay) * (X - qx) + (ax - qx) * (Y - qy)) / d
    dentro = (w1 >= -0.02) & (w2 >= -0.02) & (1 - w1 - w2 >= -0.02)
    for k in canais:
        m[y0:y1 + 1, x0:x1 + 1, k][dentro] = 255
        cont[k] += 1
print("MASCARA triangulos: grama", cont[0], "frente", cont[1], "boca", cont[2])
img = bpy.data.images.new("mascaras", LADO, LADO, alpha=False)
px = np.concatenate([m[::-1].astype(np.float32) / 255, np.ones((LADO, LADO, 1), np.float32)], axis=2)
img.pixels.foreach_set(px.ravel())
img.filepath_raw = sai
img.file_format = "PNG"
img.save()
print("MASCARA ok", sai)
