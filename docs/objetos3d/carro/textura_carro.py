"""A textura do carro abandonado pela regra nova (docs/objetos3d/REFERENCIAS.md, secao 5; docs/TAREFA_V3_MUNDO_ENFEITES.md, secao 12).

Adaptado do textura_portao.py da sessao do portao, sem a mascara de luz (o carro nao acende). Sem achatar: a textura pintada da Meshy fica
(a ferrugem, as lascas, o musgo, o vidro, as rodas). So a limpeza leve:
  - as manchas brancas do portao NAO saem aqui: no carro elas sao o reflexo do vidro das janelas (os riscos brancos do esboco), conferido
    pintando-as na textura; so contam no print;
  - o fundo fora das ilhas de UV e preenchido pela vizinhanca, para o mipmap nao puxar o fundo para dentro da emenda.
Depois o lado cai para LADO e o PNG vai a paleta de 256 cores com difusao (o detalhe pintado fica; e so para caber no orcamento de 300 KB
do web/app/test/ilha_enfeites.test.ts, na mesma densidade do portao e da barraca).

uso (da raiz): python -I docs/objetos3d/carro/textura_carro.py <textura_base_color.png> <carro_cor.png> [<lado>]
"""
import sys
import numpy as np
from PIL import Image


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


def main(ent: str, sai: str, lado: int = 512) -> None:
    a = np.asarray(Image.open(ent).convert("RGBA"))
    f = a[..., :3].astype(np.float32) / 255
    mx, mn = f.max(-1), f.min(-1)
    s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    fundo = (a[..., 3] < 8) | (mx < 0.02)
    branco = (s < 0.06) & (mx > 0.93) & ~fundo
    print("LIMPAR fundo", round(float(fundo.mean()) * 100, 1), "%; manchas brancas", int(branco.sum()), "px")
    rgb = crescer(a[..., :3], fundo, 16)
    rgb = np.clip(rgb, 0, 255).astype(np.uint8)
    cor = Image.fromarray(rgb, "RGB").resize((lado, lado), Image.LANCZOS)
    q = cor.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG)
    q.save(sai, optimize=True)
    print("COR", lado, "px;", len(q.getpalette()) // 3, "cores na paleta")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 512)
