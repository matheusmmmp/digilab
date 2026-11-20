"""A textura do poste de luz pela regra nova (docs/objetos3d/REFERENCIAS.md, secao 5; docs/TAREFA_V3_MUNDO_ENFEITES.md, secao 13).

Adaptado do textura_carro.py da sessao do carro. Sem achatar: a textura pintada da Meshy fica (o ferro verde descascado, o colar de latao,
a pedra e o musgo). So a limpeza leve e dois retoques para chegar ao esboco 1 (esbocos/esboco_1_ferro_hera.png), feitos no espaco 3D da
malha (cada texel ganha a posicao dele na superficie, rasterizando os triangulos no UV), para atravessar as emendas de UV sem corte:
  - o vidro: a Meshy pintou os vidros brancos (o esboco e a vista 1 os tem amarelos quentes); os texels claros e sem cor na faixa da
    lanterna (VIDRO_Y) vao para o amarelo quente (COR_VIDRO), guardando o claro e o escuro de cada pincelada (a luminancia);
  - a hera: a malha de ~460 triangulos (o teto de 554 dos repetidos) nao guarda as folhas soltas; a hera vira pintura no poste, um ramo
    que sobe em espiral (HERA) com folhas alternadas e contorno de nanquim, como no esboco.
A mascara da luz (o emissiveMap, poste_luz.png) sai dos mesmos texels do vidro: so os vidros acendem a noite.
Depois o lado cai para LADO e o PNG vai a paleta de 256 cores com difusao (o detalhe pintado fica; e so para caber nos 300 KB do
web/app/test/ilha_enfeites.test.ts, como o portao, a barraca, o carro e o trem).

uso (da raiz): python -I docs/objetos3d/poste/textura_poste.py <textura_base_color.png> <poste.gltf do acabar> <poste_cor.png> <poste_luz.png>
"""
import json, math, sys
from pathlib import Path
import numpy as np
from PIL import Image

TRABALHO, LADO, LADO_LUZ = 1024, 512, 256
# os retoques (PROPOSTOS, SEM FONTE: ajustados olhando as previas e a ilha contra o esboco; alturas em unidades do glTF, poste de ~1,9)
VIDRO_Y, VIDRO_SAT, VIDRO_VAL = (1.16, 1.70), 0.22, 0.5
COR_VIDRO, CENTRO_VIDRO, MISTURA_VIDRO = np.array([246, 196, 92], np.float32), np.array([255, 248, 210], np.float32), 0.92
# a rodada 2 do revisor (APROVA COM RESSALVA): a moldura de ferro mais grossa na lanterna (as quinas verticais e as bordas de baixo e de
# cima dos vidros), o ferro e a pedra mais claros (o braco e os blocos lerem a distancia), a hera mais clara, e a aba da hera que a Meshy
# deixou na frente de um vidro (o "dente" que o revisor leu como rachadura) em verde de folha
MOLDURA = {"quina": 0.022, "bordas": [(1.16, 1.195), (1.49, 1.525)], "cor": np.array([52, 104, 66], np.float32)}
FERRO = {"val": 1.28, "sat": 1.1}
PEDRA = {"y": 0.27, "val": 1.15, "sat_musgo": 1.25}
ABA_LANTERNA = {"y": (1.18, 1.5), "fator": 1.07}
# a rodada 3 do revisor: os riscos escuros que a Meshy pintou dentro dos vidros ficavam apagados a noite (a mascara so pega o claro):
# fechamento da mascara do vidro (FECHAR texels); a chama no meio de cada vidro (CHAMA: o raio na face e na altura); o colar de latao
LATAO = {"y": (1.0, 1.17), "r": 0.17, "val": 1.3, "sat": 1.35}
FECHAR, CHAMA = 5, {"y": 1.34, "ry": 0.13, "rx": 0.11, "forca": 0.85}
HERA = {"y": (0.24, 1.12), "r_max": 0.21, "voltas": 1.15, "theta0": 2.4, "onda": 0.35, "haste": 0.011,
        "passo": 0.042, "folha": (0.056, 0.036), "lado": 0.04, "semente": 20261108}
# as abas que a Meshy fez da hera (folhas soltas, finas): os texels do trecho do poste bem mais longe do eixo que o fuste naquela altura
ABAS = {"y": [(0.30, 0.88), (1.03, 1.14)], "fator": 1.3}
VERDE_FOLHA, VERDE_CLARO, NANQUIM = np.array([104, 176, 66]), np.array([172, 222, 104]), np.array([30, 56, 28])
HASTE = np.array([92, 112, 48])


def ler_gltf(arq: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    g = json.loads(Path(arq).read_text(encoding="utf-8"))
    b = (Path(arq).parent / g["buffers"][0]["uri"]).read_bytes()

    def acc(i: int) -> np.ndarray:
        a = g["accessors"][i]; v = g["bufferViews"][a["bufferView"]]
        n = {"SCALAR": 1, "VEC2": 2, "VEC3": 3}[a["type"]]
        dt = {5126: np.float32, 5123: np.uint16, 5125: np.uint32}[a["componentType"]]
        x = np.frombuffer(b, dt, a["count"] * n, v.get("byteOffset", 0) + a.get("byteOffset", 0))
        return x.reshape(a["count"], n) if n > 1 else x
    if len(g["meshes"]) != 1 or len(g["meshes"][0]["primitives"]) != 1:
        raise SystemExit("o poste devia ter 1 malha com 1 primitiva")
    p = g["meshes"][0]["primitives"][0]
    return acc(p["attributes"]["POSITION"]), acc(p["attributes"]["TEXCOORD_0"]), acc(p["indices"]).reshape(-1, 3)


def posicoes(pos: np.ndarray, uv: np.ndarray, tri: np.ndarray, lado: int) -> tuple[np.ndarray, np.ndarray]:
    """a posicao 3D de cada texel coberto (rasteriza os triangulos no UV, baricentrico), e a cobertura"""
    P = np.zeros((lado, lado, 3), np.float32); cob = np.zeros((lado, lado), bool)
    for t in tri:
        q = uv[t] * lado - 0.5
        x0, y0 = np.floor(q.min(0)).astype(int); x1, y1 = np.ceil(q.max(0)).astype(int)
        x0, y0, x1, y1 = max(x0, 0), max(y0, 0), min(x1, lado - 1), min(y1, lado - 1)
        if x1 < x0 or y1 < y0:
            continue
        yy, xx = np.mgrid[y0:y1 + 1, x0:x1 + 1]
        (ax, ay), (bx, by), (cx, cy) = q
        den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
        if abs(den) < 1e-12:
            continue
        l1 = ((by - cy) * (xx - cx) + (cx - bx) * (yy - cy)) / den
        l2 = ((cy - ay) * (xx - cx) + (ax - cx) * (yy - cy)) / den
        l3 = 1 - l1 - l2
        dentro = (l1 >= -0.02) & (l2 >= -0.02) & (l3 >= -0.02)
        w = np.stack([l1, l2, l3], -1)[dentro]
        P[yy[dentro], xx[dentro]] = w @ pos[t]
        cob[yy[dentro], xx[dentro]] = True
    return P, cob


def hsv_h(rgb: np.ndarray) -> np.ndarray:
    f = rgb.astype(np.float32) / 255
    mx, mn = f.max(-1), f.min(-1)
    d = np.maximum(mx - mn, 1e-6)
    r, g, b = f[..., 0], f[..., 1], f[..., 2]
    return np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) / 6


def fechar(m: np.ndarray, n: int) -> np.ndarray:
    """o fechamento (dilata e erode n texels): tapa os riscos finos dentro da mascara"""
    def passo(x, op):
        y = x.copy()
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                y = op(y, np.roll(np.roll(x, dy, 0), dx, 1))
        return y
    for _ in range(n):
        m = passo(m, np.logical_or)
    for _ in range(n):
        m = passo(m, np.logical_and)
    return m


def aba_lanterna(P: np.ndarray, cob: np.ndarray) -> np.ndarray:
    """a aba da hera na altura dos vidros: os texels bem mais longe do centro (em max(|x|, |z|), a caixa da lanterna) que a caixa ali"""
    y, L = P[..., 1], np.maximum(np.abs(P[..., 0]), np.abs(P[..., 2]))
    out = np.zeros(cob.shape, bool)
    for a in np.arange(ABA_LANTERNA["y"][0], ABA_LANTERNA["y"][1], 0.03):
        m = cob & (y >= a) & (y < a + 0.03)
        if m.sum() < 20:
            continue
        out |= m & (L > np.percentile(L[m], 60) * ABA_LANTERNA["fator"])
    return out


def hsv(rgb: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    f = rgb.astype(np.float32) / 255
    mx, mn = f.max(-1), f.min(-1)
    return np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0), mx


def pintar_hera(out: np.ndarray, P: np.ndarray, cob: np.ndarray) -> int:
    H = HERA
    y, r = P[..., 1], np.hypot(P[..., 0], P[..., 2])
    th = np.arctan2(P[..., 2], P[..., 0])
    zona = cob & (y >= H["y"][0] - 0.05) & (y <= H["y"][1] + 0.05) & (r <= H["r_max"]) & (r > 0.02)
    alto = H["y"][1] - H["y"][0]

    def angulo(yv):
        return H["theta0"] + 2 * math.pi * H["voltas"] * (yv - H["y"][0]) / alto + H["onda"] * np.sin(9 * yv)

    def arco(a, b):  # a diferenca de angulo em (-pi, pi]
        return (a - b + np.pi) % (2 * np.pi) - np.pi
    pintado = np.zeros(cob.shape, bool)
    # a haste: a distancia em arco ate o ramo na mesma altura
    em = zona & (y >= H["y"][0]) & (y <= H["y"][1])
    d_haste = np.abs(arco(th, angulo(y))) * r
    haste = em & (d_haste < H["haste"])
    out[haste] = HASTE * 0.7 + out[haste] * 0.3
    pintado |= haste
    # as folhas: ao longo do ramo, alternando de lado, inclinadas para fora; elipse com contorno e nervura
    rng = np.random.default_rng(H["semente"])
    n = int(alto / H["passo"])
    for i in range(n + 1):
        yc = H["y"][0] + i * H["passo"] + rng.uniform(-0.01, 0.01)
        s = 1 if i % 2 else -1
        a, b = H["folha"]
        esc = rng.uniform(0.8, 1.2) * (1.15 - 0.35 * i / n)  # maiores embaixo, como no esboco
        a, b = a * esc, b * esc
        inc = s * rng.uniform(0.5, 0.9)  # o giro da folha (radianos)
        tc = angulo(yc)
        m = zona & (np.abs(y - yc) < a * 1.3)
        if not m.any():
            continue
        rr = r[m]
        u = arco(th[m], tc) * rr - s * H["lado"]  # o arco (horizontal na superficie), com a folha para um lado do ramo
        v = y[m] - yc
        cu, su = math.cos(inc), math.sin(inc)
        lu, lv = u * cu + v * su, -u * su + v * cu  # nos eixos da folha
        e = (lu / a) ** 2 + (lv / (b * np.clip(1 - 0.55 * lu / a, 0.25, 2))) ** 2  # a gota: ponta fina para fora
        dentro = e <= 1
        idx = np.argwhere(m)[dentro]
        if not len(idx):
            continue
        ee, llv, llu = e[dentro], lv[dentro], lu[dentro]
        cor = np.where((llv > 0)[:, None], VERDE_CLARO, VERDE_FOLHA).astype(np.float32)
        cor = np.where((ee > 0.62)[:, None], NANQUIM, cor)
        cor = np.where(((np.abs(llv) < b * 0.1) & (np.abs(llu) < a * 0.75))[:, None], NANQUIM * 0.5 + VERDE_FOLHA * 0.5, cor)
        out[idx[:, 0], idx[:, 1]] = cor
        pintado[idx[:, 0], idx[:, 1]] = True
        # o pecíolo: um trecho curto da haste ate a folha
    return int(pintado.sum())


def pintar_abas(out: np.ndarray, P: np.ndarray, cob: np.ndarray) -> int:
    """as abas soltas da hera da Meshy saem verde-escuras do ferro; viram folha (o verde da hera com o claro e o escuro da pincelada)"""
    y, r = P[..., 1], np.hypot(P[..., 0], P[..., 2])
    total = np.zeros(cob.shape, bool)
    for y0, y1 in ABAS["y"]:
        for a in np.arange(y0, y1, 0.04):
            m = cob & (y >= a) & (y < a + 0.04)
            if m.sum() < 20:
                continue
            fuste = np.percentile(r[m], 40)
            total |= m & (r > fuste * ABAS["fator"])
    lum = out[total].mean(-1, keepdims=True) / 255
    out[total] = VERDE_FOLHA * (0.6 + 0.8 * lum) * 0.8 + out[total] * 0.2
    return int(total.sum())


def crescer(rgb: np.ndarray, vazio: np.ndarray, passos: int) -> np.ndarray:
    """preenche os pixels vazios com a media dos vizinhos cheios, um anel por passo"""
    rgb, vazio = rgb.astype(np.float32).copy(), vazio.copy()
    for _ in range(passos):
        soma = np.zeros_like(rgb); n = np.zeros(vazio.shape, np.float32)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == dy == 0:
                    continue
                c = np.roll(np.roll(~vazio, dy, 0), dx, 1)
                soma += np.roll(np.roll(rgb, dy, 0), dx, 1) * c[..., None]
                n += c
        novo = vazio & (n > 0)
        rgb[novo] = soma[novo] / n[novo][:, None]
        vazio = vazio & ~novo
        if not vazio.any():
            break
    return rgb


def main(ent: str, gl: str, sai_cor: str, sai_luz: str) -> None:
    a = np.asarray(Image.open(ent).convert("RGB").resize((TRABALHO, TRABALHO), Image.LANCZOS)).astype(np.float32)
    pos, uv, tri = ler_gltf(gl)
    P, cob = posicoes(pos, uv, tri, TRABALHO)
    print("COBERTURA", round(float(cob.mean()) * 100, 1), "% dos texels;", len(tri), "triangulos")
    s, v = hsv(a)
    y = P[..., 1]
    vidro = cob & (y >= VIDRO_Y[0]) & (y <= VIDRO_Y[1]) & (s < VIDRO_SAT) & (v > VIDRO_VAL)
    vidro = fechar(vidro, FECHAR) & cob & (y >= VIDRO_Y[0]) & (y <= VIDRO_Y[1])
    vidro_cru = vidro.copy()
    lum = a.mean(-1, keepdims=True) / 255
    # o miolo de cada vidro mais claro (a chama do esboco): pela distancia ao eixo e ao meio da faixa da lanterna
    meio = 1 - np.clip(np.abs(y - 1.36) / 0.2, 0, 1)
    alvo = (COR_VIDRO * (1 - meio[..., None] * 0.6) + CENTRO_VIDRO * meio[..., None] * 0.6) * (0.8 + 0.2 * lum)
    # a chama: um miolo claro no meio de cada face (perto do meio da face em min(|x|, |z|) e da altura CHAMA["y"])
    face = np.minimum(np.abs(P[..., 0]), np.abs(P[..., 2]))
    ch = np.clip(1 - (face / CHAMA["rx"]) ** 2 - ((y - CHAMA["y"]) / CHAMA["ry"]) ** 2, 0, 1)[..., None] * CHAMA["forca"]
    alvo = alvo * (1 - ch) + CENTRO_VIDRO * ch
    out = a.copy()
    # o ferro (os verdes que nao sao vidro) e a pedra da base mais claros, sem achatar: escala o valor, guarda a pincelada
    h = hsv_h(a)
    verde = cob & ~vidro & (h > 0.25) & (h < 0.55) & (s > 0.15)
    media = out[verde].mean(-1, keepdims=True)
    out[verde] = np.clip((media + (out[verde] - media) * FERRO["sat"]) * FERRO["val"], 0, 255)
    base = cob & (y < PEDRA["y"])
    musgo = base & (h > 0.15) & (h < 0.3) & (s > 0.3)
    out[base] = np.clip(out[base] * PEDRA["val"], 0, 255)
    mm = out[musgo].mean(-1, keepdims=True)
    out[musgo] = np.clip(mm + (out[musgo] - mm) * PEDRA["sat_musgo"], 0, 255)
    out[vidro] = out[vidro] * (1 - MISTURA_VIDRO) + alvo[vidro] * MISTURA_VIDRO
    r_eixo = np.hypot(P[..., 0], P[..., 2])
    latao = cob & ~vidro & (y >= LATAO["y"][0]) & (y <= LATAO["y"][1]) & (r_eixo < LATAO["r"]) & (h > 0.05) & (h < 0.2) & (s > 0.12)
    ml = out[latao].mean(-1, keepdims=True)
    out[latao] = np.clip((ml + (out[latao] - ml) * LATAO["sat"]) * LATAO["val"], 0, 255)
    print("LATAO", int(latao.sum()), "texels")
    # a moldura: as quinas verticais da caixa (|x| ~ |z|) e as bordas de baixo e de cima dos vidros, em ferro verde, por cima do vidro
    ax, az = np.abs(P[..., 0]), np.abs(P[..., 2])
    lant = cob & (y >= VIDRO_Y[0]) & (y <= 1.53)
    moldura = lant & ((np.abs(ax - az) < MOLDURA["quina"] * 1.414) | np.any([(y >= b0) & (y <= b1) for b0, b1 in MOLDURA["bordas"]], 0))
    lm = out[moldura].mean(-1, keepdims=True) / 255
    out[moldura] = MOLDURA["cor"] * (0.75 + 0.5 * lm)
    vidro = vidro & ~moldura
    print("VIDRO", int(vidro.sum()), "texels; MOLDURA", int(moldura.sum()), "; FERRO", int(verde.sum()), "; BASE", int(base.sum()))
    print("HERA", pintar_hera(out, P, cob), "texels")
    print("ABAS", pintar_abas(out, P, cob), "texels")
    aba = aba_lanterna(P, cob) & ~moldura & ~vidro_cru  # so o que a Meshy pintou de ferro (o vidro inclinado nao entra)
    lum2 = out[aba].mean(-1, keepdims=True) / 255
    out[aba] = VERDE_FOLHA * (0.6 + 0.8 * lum2)
    vidro = vidro & ~aba
    print("ABA_LANTERNA", int(aba.sum()), "texels")
    # fora das ilhas: a vizinhanca (o mipmap nao puxa outra cor para a emenda)
    out = crescer(out, ~cob, 24)
    cor = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGB").resize((LADO, LADO), Image.LANCZOS)
    q = cor.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG)
    q.save(sai_cor, optimize=True)
    m = Image.fromarray((vidro * 255).astype(np.uint8), "L").resize((LADO_LUZ, LADO_LUZ), Image.BILINEAR)
    m.save(sai_luz, optimize=True)
    print("COR", LADO, "px;", len(q.getpalette()) // 3, "cores; LUZ", LADO_LUZ, "px")


if __name__ == "__main__":
    main(*sys.argv[1:5])
