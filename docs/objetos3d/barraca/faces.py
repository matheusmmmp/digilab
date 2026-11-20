# As faces da malha da Meshy (centro, normal, area, UVs, vertices), no espaco do Blender, para textura_barraca.py e interior.py.
# uso: blender -b --python faces.py -- <meshy.glb> <faces.json>
import bpy, sys, json
arq, sai = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=arq)
o = [p for p in bpy.context.scene.objects if p.type == "MESH"][0]
o.data.transform(o.matrix_world); print("MW", [list(r) for r in o.matrix_world])
me = o.data
me.update()
uv = me.uv_layers.active.data
fs = []
for p in me.polygons:
    fs.append({"c": list(p.center), "n": list(p.normal), "a": p.area,
               "uv": [list(uv[li].uv) for li in p.loop_indices], "v": [list(me.vertices[vi].co) for vi in p.vertices]})
json.dump(fs, open(sai, "w"))
print("FACES", len(fs))
