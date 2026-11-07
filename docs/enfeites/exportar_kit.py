# Um modelo de kit CC0 para a pasta dos enfeites (docs/TAREFA_V3_MUNDO_ENFEITES.md, secao 4.2): abre o .glb do kit e exporta o glTF
# separado (.gltf + .bin + a textura), um no so com o nome do enfeite, a malha como veio. Imprime os triangulos, para o gate E-G1.
# uso (da raiz): blender -b --factory-startup --python docs/enfeites/exportar_kit.py -- <modelo.glb> <nome> <saida.gltf>
import sys, bpy

ent, nome, sai = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=ent)
obs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
if len(obs) != 1:
    raise SystemExit(f"o modelo do kit devia ter 1 malha: {len(obs)}")
o = obs[0]
o.name = o.data.name = nome
for m in o.data.materials:
    m.use_backface_culling = True
o.data.calc_loop_triangles()
print("KIT", nome, "tri", len(o.data.loop_triangles))
bpy.ops.object.select_all(action="DESELECT")
o.select_set(True)
bpy.context.view_layer.objects.active = o
bpy.ops.export_scene.gltf(filepath=sai, export_format="GLTF_SEPARATE", use_selection=True, export_apply=True,
                          export_image_format="AUTO", export_materials="EXPORT", export_yup=True)
print("EXPORTAR ok", sai)
