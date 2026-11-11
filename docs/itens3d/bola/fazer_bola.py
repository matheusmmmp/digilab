# A bola de praia feita do zero no Blender, sem Meshy e sem IA (docs/TAREFA_V3_ITENS_3D.md, secao 14; o esboco:
# docs/objetos3d/bola/esbocos/esboco_1_praia_gomos.png). Um script so, que refaz a bola inteira:
#   1. a malha: uma esfera UV de SEG x ANEIS (o SEG multiplo de 6, para cada emenda de gomo cair numa coluna de vertices), sombreado
#      suave, centro na origem e o raio da bola de antes (a caixa igual nas tres medidas, G2); o eixo dos polos inclinado, aplicado na
#      malha, para a bola parada mostrar uma tampa, como no esboco;
#   2. os UVs, feitos aqui: a faixa dos gomos (as faces entre os dois leques dos polos) numa projecao equirretangular; cada leque de polo
#      (as faces que tocam o polo) num disco plano proprio, para a tampa sair um circulo liso, sem a distorcao do polo da equirretangular;
#   3. a textura, pintada por numpy por uma funcao so da posicao na esfera (u, latitude), usada nas duas regioes: seis gomos (as cores do
#      esboco, cada uma com 4 tons: sombra, base, luz e brilho), pinceladas leves, um brilho grande pintado de um lado, as linhas de
#      nanquim nas emendas (largura constante na superficie) e as tampas brancas com o contorno; o ruido e periodico em u;
#   4. a exportacao glTF separada (.gltf + .bin + .png, so a cor, sem Draco) e a marca de procedencia no asset.extras;
#   5. uma previa no Workbench, de tres lados e de baixo.
# uso (da raiz): blender -b --factory-startup --python docs/itens3d/bola/fazer_bola.py -- <saida.gltf> <previa.png>
import json, math, os, sys
import bpy
import numpy as np

sai, previa = (os.path.abspath(a) for a in sys.argv[sys.argv.index("--") + 1:])
SEG, ANEIS = 24, 12            # 528 triangulos, abaixo do teto de 554 da G1 (DECIDIDO, D-I3)
RAIO = 0.9218                  # o raio da bola de antes (a vista normaliza pela altura da tabela; o tamanho na tela nao muda)
LARG, ALT = 1024, 512          # a textura (potencias de 2; G3)
FAIXA_ALT = 384                # as linhas da faixa dos gomos (de baixo); acima, os dois discos das tampas
DISCO = 128                    # o lado do quadrado de cada disco; o leque ocupa o raio DISCO_R, e a margem segue a mesma pintura
DISCO_R = 56
LEQUE = math.pi / ANEIS        # o raio angular do leque de cada polo (o primeiro anel)
MARGEM_LAT = 4 / FAIXA_ALT * (math.pi - 2 * LEQUE)   # a faixa pinta 4 px alem do anel do leque, para o filtro nao pegar o vizinho
TAMPA = math.radians(11.5)     # o raio angular de cada tampa (dentro do leque: o contorno e um circulo liso no disco)
LINHA = 0.014                  # a meia largura da linha de nanquim, em fracao do raio
INCLINA = 32                   # graus: o eixo dos polos inclinado, para a tampa aparecer na bola parada
SEMENTE = 20261108             # o acaso das pinceladas, fixo (a bola sai igual a cada execucao)
# as cores do esboco, na volta da bola: azul, branco, azul claro, vermelho, branco, amarelo; cada uma em 4 tons (sombra, base, luz, brilho)
CORES = {
    "azul":     ["#2160c4", "#2f74d6", "#5594e4", "#a9cdf6"],
    "branco":   ["#d6d2e2", "#ecebf2", "#f8f7fb", "#ffffff"],
    "azulc":    ["#2d70c8", "#3f8ae0", "#69a6ec", "#bcdcfa"],
    "vermelho": ["#c22e2c", "#df3b36", "#ec5c50", "#fbb3a6"],
    "amarelo":  ["#e6a516", "#f6c51f", "#fad449", "#fff3b0"],
}
GOMOS = ["azul", "branco", "azulc", "vermelho", "branco", "amarelo"]
NANQUIM = np.array([0.11, 0.13, 0.22])
# o brilho grande: a direcao na esfera (u, latitude) e o raio angular
BRILHO_U, BRILHO_LAT, BRILHO_R = 0.10, math.radians(28), math.radians(38)


def rgb(h):
    return np.array([int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)])


def ruido(g, u, v):
    """ruido de valor suave sobre a grade g (linhas em v, colunas em u), periodico em u, interpolado com suavizacao"""
    nv, nu = g.shape[0] - 1, g.shape[1]
    x, y = (u % 1.0) * nu, np.clip(v, 0, 0.999999) * nv
    x0, y0 = np.floor(x).astype(int), np.floor(y).astype(int)
    fx, fy = x - x0, y - y0
    fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    x0, x1 = x0 % nu, (x0 + 1) % nu
    a = g[y0, x0] * (1 - fx) + g[y0, x1] * fx
    b = g[y0 + 1, x0] * (1 - fx) + g[y0 + 1, x1] * fx
    return a * (1 - fy) + b * fy


RNG = np.random.default_rng(SEMENTE)
GRADES = [RNG.random((6, 90)), RNG.random((10, 240)), RNG.random((41, 480))]


def cor_em(u, lat):
    """a cor da bola no ponto (u de 0 a 1 na volta, latitude em radianos), em arrays de mesma forma"""
    v = lat / math.pi + 0.5
    cl = np.cos(lat)
    k = np.floor(u * 6).astype(int) % 6
    dentro = u * 6 - np.floor(u * 6)
    d_emenda = np.minimum(dentro, 1 - dentro) * (2 * math.pi / 6) * cl
    # as pinceladas leves: ruido longo no comprimento do gomo e um pouco inclinado
    p = (0.5 * ruido(GRADES[0], u + 0.12 * v, v) + 0.35 * ruido(GRADES[1], u - 0.08 * v, v) + 0.15 * ruido(GRADES[2], u, v)) - 0.5
    # o brilho grande, de um lado so: o angulo ate a direcao do brilho, quebrado pelas pinceladas
    a = 2 * math.pi * u
    n = np.stack([cl * np.cos(a), cl * np.sin(a), np.sin(lat)])
    bl = np.array([math.cos(BRILHO_LAT) * math.cos(2 * math.pi * BRILHO_U), math.cos(BRILHO_LAT) * math.sin(2 * math.pi * BRILHO_U),
                   math.sin(BRILHO_LAT)])
    ang = np.arccos(np.clip(np.tensordot(bl, n, 1), -1, 1))
    brilho = np.clip(1 - ang / BRILHO_R, 0, 1) ** 1.3
    # a sombra pintada perto das emendas e embaixo (o lado oposto ao brilho)
    borda = np.clip(1 - d_emenda / 0.07, 0, 1)
    longe = np.clip((ang - math.radians(110)) / math.radians(50), 0, 1)
    s = 0.45 + 0.34 * p + 0.75 * brilho * (0.75 + p) - 0.30 * borda - 0.28 * longe
    out = np.zeros(u.shape + (3,))
    for i, nome in enumerate(GOMOS):
        tons = [rgb(h) for h in CORES[nome]]
        m = k == i
        si = s[m]
        c = np.repeat(tons[0][None], si.size, 0)
        for t, lim in zip(tons[1:], (0.20, 0.62, 0.90)):
            w = np.clip((si - lim) / 0.05 + 0.5, 0, 1)[:, None]
            c = c * (1 - w) + t[None] * w
        out[m] = c
    # as linhas das emendas (nanquim, com a borda suave)
    w = np.clip((LINHA - d_emenda) / 0.005 + 0.5, 0, 1)[..., None]
    out = out * (1 - w) + NANQUIM * w
    # as tampas: um disco branco liso, com a sombra fina na borda, um brilho pequeno de lado e o contorno de nanquim
    ang_polo = math.pi / 2 - np.abs(lat)
    tb = [rgb(h) for h in CORES["branco"]]
    r = ang_polo / TAMPA
    bx, by = r * np.cos(a), r * np.sin(a)
    real = np.clip(1 - np.hypot(bx + 0.30, by - 0.30) / 0.38, 0, 1)
    ct = np.where((r > 0.80)[..., None], tb[0], tb[1])
    ct = np.where((real > 0.25)[..., None], tb[3], ct)
    wt = np.clip((1 - r) / 0.03 + 0.5, 0, 1)[..., None]
    out = out * (1 - wt) + ct * wt
    lc = np.clip((LINHA - np.abs(ang_polo - TAMPA)) / 0.005 + 0.5, 0, 1)[..., None]
    out = out * (1 - lc) + NANQUIM * lc
    return np.clip(out, 0, 1)


def faixa_v(lat):
    """a latitude na linha da faixa (0 a FAIXA_ALT/ALT em v), com a margem alem do anel do leque"""
    lim = math.pi / 2 - LEQUE + MARGEM_LAT
    return (np.asarray(lat) + lim) / (2 * lim) * (FAIXA_ALT / ALT)


def disco_centro(norte):
    """o centro do disco do polo, em pixels (x da esquerda, y de baixo)"""
    return (DISCO / 2 + (0 if norte else DISCO), FAIXA_ALT + DISCO / 2)


def pintar():
    img = np.ones((ALT, LARG, 3))
    # a faixa: cada linha e uma latitude, cada coluna um u
    lim = math.pi / 2 - LEQUE + MARGEM_LAT
    u = (np.arange(LARG) + 0.5) / LARG
    lat = ((np.arange(FAIXA_ALT) + 0.5) / FAIXA_ALT * 2 - 1) * lim
    U, LAT = np.meshgrid(u, lat)
    img[:FAIXA_ALT] = cor_em(U, LAT)
    # os discos: o pixel a distancia d do centro e o angulo a2 e o ponto de u = a2/2pi e de angulo ao polo d/DISCO_R * LEQUE
    yy, xx = np.mgrid[0:DISCO, 0:DISCO] + 0.5
    for norte in (True, False):
        cx, cy = disco_centro(norte)
        x0, y0 = int(cx - DISCO / 2), int(cy - DISCO / 2)
        dx, dy = xx - DISCO / 2, yy - DISCO / 2
        uu = (np.arctan2(dy, dx) / (2 * math.pi)) % 1.0
        ap = np.minimum(np.hypot(dx, dy) / DISCO_R * LEQUE, math.pi / 2)
        la = (math.pi / 2 - ap) * (1 if norte else -1)
        img[y0:y0 + DISCO, x0:x0 + DISCO] = cor_em(uu, la)
    # o resto da tira de cima repete os dois discos: sem branco solto, que o mipmap misturava na borda da tampa (o anel claro da revisao)
    par = img[FAIXA_ALT:, :2 * DISCO].copy()
    for x in range(2 * DISCO, LARG, 2 * DISCO):
        img[FAIXA_ALT:, x:x + 2 * DISCO] = par
    return img


bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.mesh.primitive_uv_sphere_add(segments=SEG, ring_count=ANEIS, radius=RAIO, location=(0, 0, 0))
bola = bpy.context.active_object
bola.name = "bola"
me = bola.data
me.name = "bola"
bpy.ops.object.shade_smooth()

# os UVs: o u de cada vertice pelo angulo em volta do eixo dos polos (a origem na primeira coluna de vertices, para as emendas cairem
# nelas); a faixa em equirretangular, com a emenda u=0/1 desfeita por face; os leques nos discos
ang0 = min((math.atan2(v.co.y, v.co.x)) % (2 * math.pi / SEG) for v in me.vertices if abs(v.co.z) < RAIO * 0.999)
uvs = me.uv_layers.active.data
for f in me.polygons:
    vs = [me.vertices[me.loops[li].vertex_index].co for li in f.loop_indices]
    polo = [abs(c.z) > RAIO * 0.9999 for c in vs]
    if any(polo):
        norte = max(vs, key=lambda c: abs(c.z)).z > 0
        cx, cy = disco_centro(norte)
        for li, c in zip(f.loop_indices, vs):
            ap = math.acos(max(-1.0, min(1.0, abs(c.z) / RAIO)))
            a = math.atan2(c.y, c.x) - ang0
            rr = ap / LEQUE * DISCO_R
            uvs[li].uv = ((cx + rr * math.cos(a)) / LARG, (cy + rr * math.sin(a)) / ALT)
    else:
        us = [((math.atan2(c.y, c.x) - ang0) / (2 * math.pi)) % 1.0 for c in vs]
        us = [round(x * SEG) / SEG for x in us]
        if max(us) - min(us) > 0.5:
            us = [x + 1.0 if x < 0.5 else x for x in us]
        for li, c, x in zip(f.loop_indices, vs, us):
            uvs[li].uv = (x, float(faixa_v(math.asin(max(-1.0, min(1.0, c.z / RAIO))))))

# a bola parada mostra uma tampa, como no esboco: o eixo dos polos inclinado, aplicado na malha (o no fica sem transformacao, G2)
bola.rotation_euler = (math.radians(INCLINA), 0, math.radians(25))
bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

cor = pintar()
px = np.concatenate([cor, np.ones((ALT, LARG, 1))], axis=2).astype(np.float32).ravel()
img = bpy.data.images.new("bola_cor", LARG, ALT, alpha=False)
img.pixels.foreach_set(px)
img.filepath_raw = os.path.join(os.path.dirname(sai), "bola_cor.png")
img.file_format = "PNG"
img.save()

mat = bpy.data.materials.new("bola")
mat.use_nodes = True
nos, ligs = mat.node_tree.nodes, mat.node_tree.links
bsdf = next(n for n in nos if n.type == "BSDF_PRINCIPLED")
tex = nos.new("ShaderNodeTexImage")
tex.image = img
ligs.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
bsdf.inputs["Metallic"].default_value = 0.0
bsdf.inputs["Roughness"].default_value = 1.0
me.materials.append(mat)

bpy.ops.object.select_all(action="DESELECT")
bola.select_set(True)
bpy.context.view_layer.objects.active = bola
bpy.ops.export_scene.gltf(filepath=sai, export_format="GLTF_SEPARATE", use_selection=True, export_apply=True,
                          export_image_format="AUTO", export_materials="EXPORT", export_yup=True)

# a marca de procedencia (G8): feita por script, sem IA; o License.txt ao lado
with open(sai, encoding="utf8") as f:
    g = json.load(f)
g["asset"]["extras"] = {
    "gerado_por_ia": False,
    "gerador": "Blender 4.5 LTS por script (docs/itens3d/bola/fazer_bola.py), sem IA e sem Meshy",
    "pipeline": "esfera UV de 24 x 12 com sombreado suave, polos inclinados 32 graus; UVs em faixa e dois discos; "
                "textura pintada por numpy (6 gomos em 4 tons, emendas, tampas, um brilho)",
    "licenca": "License.txt ao lado",
}
with open(sai, "w", encoding="utf8") as f:
    json.dump(g, f, indent=1, ensure_ascii=False)
    f.write("\n")

me.calc_loop_triangles()
print("BOLA tri", len(me.loop_triangles), "dim", tuple(round(d, 4) for d in bola.dimensions))

# a previa: Workbench com a textura, tres lados e uma de baixo (a tampa de baixo)
cena = bpy.context.scene
cena.render.engine = "BLENDER_WORKBENCH"
cena.display.shading.light = "STUDIO"
cena.display.shading.color_type = "TEXTURE"
cena.render.resolution_x, cena.render.resolution_y = 384, 384
cena.render.film_transparent = True
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
cena.collection.objects.link(cam)
cena.camera = cam
base, ext = os.path.splitext(previa)
for i, (az, alto) in enumerate(((-30, 0.55), (90, 0.55), (210, 0.55), (150, -0.9))):
    d = RAIO * 2 * 1.9
    a = math.radians(az)
    cam.location = (d * math.cos(a) * 0.85, d * math.sin(a) * 0.85, d * alto)
    cam.rotation_euler = (-cam.location.normalized()).to_track_quat("-Z", "Y").to_euler()
    cena.render.filepath = f"{base}_{i}{ext}"
    bpy.ops.render.render(write_still=True)
print("FAZER_BOLA ok", sai)
