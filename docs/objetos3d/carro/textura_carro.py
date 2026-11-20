"""A textura do carro abandonado pela regra nova (docs/objetos3d/REFERENCIAS.md, secao 5; docs/TAREFA_V3_MUNDO_ENFEITES.md, secao 12).

Adaptado do textura_portao.py da sessao do portao, sem a mascara de luz (o carro nao acende). Sem achatar: a textura pintada da Meshy fica
(a ferrugem, as lascas, o musgo, o vidro, as rodas). So a limpeza leve:
  - as manchas brancas do portao NAO saem aqui: no carro elas sao o reflexo do vidro das janelas (os riscos brancos do esboco), conferido
    pintando-as na textura; so contam no print;
  - o fundo fora das ilhas de UV e preenchido pela vizinhanca, para o mipmap nao puxar o fundo para dentro da emenda.
Com as mascaras do mascaras_carro.py (opcional), o retoque leve pedido pelo revisor (APROVA COM RESSALVA, rodada 1), sem achatar nada:
  - o musgo e a grama (os verdes) mais vivos, para chegar ao verde do esboco (SAT_VERDE, VAL_VERDE);
  - flores rosa pequenas (FLORES discos, sementes fixas) sobre as laminas da grama do teto, que a malha da Meshy perdeu;
  - os farois (os bege da mascara da frente) puxados para o amarelo do esboco (COR_FAROL, MISTURA_FAROL).
Depois o lado cai para LADO e o PNG vai a paleta de 256 cores com difusao (o detalhe pintado fica; e so para caber no orcamento de 300 KB
do web/app/test/ilha_enfeites.test.ts, na mesma densidade do portao e da barraca).

uso (da raiz): python -I docs/objetos3d/carro/textura_carro.py <textura_base_color.png> <carro_cor.png> [<lado> [<mascaras.png>]]
"""
import sys
import numpy as np
from PIL import Image

# o retoque (PROPOSTO, SEM FONTE: ajustado olhando a vitrine contra o esboco)
SAT_VERDE, VAL_VERDE = 1.25, 1.15
FLORES, RAIO_FLOR, SEMENTE_FLORES = 60, 16, 20261108
ROSA, MIOLO = np.array([238, 122, 196], np.float32), np.array([255, 236, 150], np.float32)
COR_FAROL, MISTURA_FAROL = np.array([255, 222, 128], np.float32), 0.8


def hsv(rgb: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    f = rgb.astype(np.float32) / 255
    mx, mn = f.max(-1), f.min(-1)
    d = np.maximum(mx - mn, 1e-6)
    r, g, b = f[..., 0], f[..., 1], f[..., 2]
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) / 6
    return h, np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0), mx


def retocar(rgb: np.ndarray, mascaras: str) -> np.ndarray:
    m = np.asarray(Image.open(mascaras).convert("RGB").resize(rgb.shape[1::-1], Image.NEAREST))
    teto, frente = (m[..., 0] > 0) | (m[..., 2] > 0), m[..., 1] > 0
    out = rgb.astype(np.float32)
    h, s, v = hsv(rgb)
    farol = frente & (h > 0.05) & (h < 0.2) & (s > 0.08) & (s < 0.7) & (v > 0.45)
    verde = (h > 0.17) & (h < 0.45) & (s > 0.3) & (v < 0.9) & ~farol
    media = out[verde].mean(-1, keepdims=True)
    out[verde] = np.clip((media + (out[verde] - media) * SAT_VERDE) * VAL_VERDE, 0, 255)
    out[farol] = out[farol] * (1 - MISTURA_FAROL) + COR_FAROL * MISTURA_FAROL * (v[farol][:, None] / v[farol].max())
    ys, xs = np.nonzero(teto & verde)
    rng = np.random.default_rng(SEMENTE_FLORES)
    yy, xx = np.mgrid[-RAIO_FLOR:RAIO_FLOR + 1, -RAIO_FLOR:RAIO_FLOR + 1]
    disco, miolo = (yy ** 2 + xx ** 2) <= RAIO_FLOR ** 2, (yy ** 2 + xx ** 2) <= (RAIO_FLOR // 3) ** 2
    for i in rng.choice(len(ys), size=min(FLORES, len(ys)), replace=False):
        y, x = ys[i], xs[i]
        sl = (slice(max(0, y - RAIO_FLOR), y + RAIO_FLOR + 1), slice(max(0, x - RAIO_FLOR), x + RAIO_FLOR + 1))
        dy0, dx0 = sl[0].start - (y - RAIO_FLOR), sl[1].start - (x - RAIO_FLOR)
        alvo = out[sl]
        d = disco[dy0:dy0 + alvo.shape[0], dx0:dx0 + alvo.shape[1]] & teto[sl]
        c = miolo[dy0:dy0 + alvo.shape[0], dx0:dx0 + alvo.shape[1]] & teto[sl]
        alvo[d] = ROSA
        alvo[c] = MIOLO
    print("RETOQUE verdes", int(verde.sum()), "px; farois", int(farol.sum()), "px; flores", min(FLORES, len(ys)))
    return np.clip(out, 0, 255).astype(np.uint8)


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


def main(ent: str, sai: str, lado: int = 512, mascaras: str | None = None) -> None:
    a = np.asarray(Image.open(ent).convert("RGBA"))
    f = a[..., :3].astype(np.float32) / 255
    mx, mn = f.max(-1), f.min(-1)
    s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    fundo = (a[..., 3] < 8) | (mx < 0.02)
    branco = (s < 0.06) & (mx > 0.93) & ~fundo
    print("LIMPAR fundo", round(float(fundo.mean()) * 100, 1), "%; manchas brancas", int(branco.sum()), "px")
    rgb = crescer(a[..., :3], fundo, 16)
    rgb = np.clip(rgb, 0, 255).astype(np.uint8)
    if mascaras:
        rgb = retocar(rgb, mascaras)
    cor = Image.fromarray(rgb, "RGB").resize((lado, lado), Image.LANCZOS)
    q = cor.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG)
    q.save(sai, optimize=True)
    print("COR", lado, "px;", len(q.getpalette()) // 3, "cores na paleta")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 512, sys.argv[4] if len(sys.argv) > 4 else None)
