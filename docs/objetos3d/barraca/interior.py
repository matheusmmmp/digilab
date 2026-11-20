"""As faces de dentro da barraca vistas pelo vao: raios de varios angulos pela janela da porta; fica a face atingida que tem teto
em cima (um raio para cima a partir dela bate na lona). Grava os indices."""
import bpy, sys, json, math
from mathutils import Vector
arq, sai = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=arq)
o = [p for p in bpy.context.scene.objects if p.type == "MESH"][0]
dg = bpy.context.evaluated_depsgraph_get()
cena = bpy.context.scene
me = o.data
def teto(idx):
    p = me.polygons[idx]
    ok, loc, *_ = cena.ray_cast(dg, p.center + p.normal * 0.003 + Vector((0, 0, 0.003)), Vector((0, 0, 1)))
    return ok and loc.z < 0.5
achadas = set()
for az in (-50, -30, -15, 0, 15, 30, 50):
    for el in (0, 15, 30, 45, 60):
        d = Vector((math.sin(math.radians(az)) * math.cos(math.radians(el)), math.cos(math.radians(az)) * math.cos(math.radians(el)), -math.sin(math.radians(el))))
        for i in range(31):
            for k in range(31):
                alvo = Vector((-0.28 + 0.56 * i / 30, -0.55, -0.6 + 0.6 * k / 30))  # a janela da porta
                ok, loc, nor, idx, *_ = cena.ray_cast(dg, alvo - d * 4, d)
                if ok and loc.y > -0.43 and idx not in achadas and teto(idx):
                    achadas.add(idx)
print("INTERIOR", len(achadas))
json.dump(sorted(achadas), open(sai, "w"))
