"""SPRITES_GERACAO, etapa G2, E3 (docs/TAREFA_V3_SPRITES_GERACAO.md, secao 3.4): os quadros do clipe viram quadros na grade do UP.

A reserva da E3 (registro D-SG-N): o pixel-mcp aceita paletas de ate 256 cores e nao tem a operacao "levar uma imagem a uma paleta"
(o snap em LAB dele so existe nas ferramentas de desenho); a paleta do sprite tem milhares de cores. Este script faz o mesmo papel:

1. Amostragem por vizinho mais proximo na grade do UP. O still mestre e o quadro do UP ampliado (`escala` vezes, com o canto em
   `origem` no PNG de referencia) e o master do Sprite Forge e `master = s * referencia + o` (o `transform` do `master.json`). Os
   quadros registrados do Sprite Forge estao nas coordenadas do master. O pixel (u, v) da caixa do UP e lido no centro dele:
   x = s * (origem_x + escala * (u + 0,5)) + o_x, e o mesmo em y.
2. Alfa binario: alfa >= 128 vira 255; o resto vira 0 (o pixel some).
3. Snap a paleta do sprite: cada pixel opaco vai para a cor da paleta (a ficha, `paleta`) mais proxima em CIELAB (D65).

Entrada: a pasta `registered/frames` do take, o `selection.json` do corte (sourceIndices e durations_ms) e o `master.json`.
Saida: `<saida>/f00.png ...` (RGBA, na caixa do UP, sem a sombra) e `<saida>/quadros.json`, o contrato do `converter.py`.
Falha alto: quadro ausente, ms invalido, quadro sem pixel opaco, transformacao que sai do canvas.

Uso: python tools/sprites_geracao/limpar.py --nome Agumon --registrados DIR --selecao selection.json --master master.json
     --ref-escala 10 --ref-origem 42,172 --saida DIR [--remaster DIR]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ficha as F  # noqa: E402

ALFA_CORTE = 128  # PROPOSTO, SEM FONTE: o meio da faixa de alfa


def _srgb_para_lab(rgb: np.ndarray) -> np.ndarray:
    """(N, 3) uint8 sRGB -> (N, 3) CIELAB D65."""
    c = rgb.astype(np.float64) / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    m = np.array([[0.4124564, 0.3575761, 0.1804375],
                  [0.2126729, 0.7151522, 0.0721750],
                  [0.0193339, 0.1191920, 0.9503041]])
    xyz = c @ m.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > (6 / 29) ** 3, np.cbrt(xyz), xyz / (3 * (6 / 29) ** 2) + 4 / 29)
    return np.stack([116 * f[:, 1] - 16, 500 * (f[:, 0] - f[:, 1]), 200 * (f[:, 1] - f[:, 2])], axis=1)


def paleta_rgb(ficha: dict) -> np.ndarray:
    pal = np.array([[int(h.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)] for h in ficha["paleta"]], dtype=np.uint8)
    if len(pal) == 0:
        raise ValueError("ficha sem paleta")
    return pal


def snap(q: np.ndarray, pal: np.ndarray) -> np.ndarray:
    """Leva cada pixel opaco (alfa 255) a cor da paleta mais proxima em CIELAB; o alfa nao muda."""
    out = q.copy()
    m = q[..., 3] == 255
    if not m.any():
        return out
    px = q[m][:, :3]
    lab_px = _srgb_para_lab(px)
    lab_pal = _srgb_para_lab(pal)
    d = ((lab_px[:, None, :] - lab_pal[None, :, :]) ** 2).sum(axis=2)
    out[m, :3] = pal[d.argmin(axis=1)]
    return out


def amostrar(frame: np.ndarray, caixa: tuple[int, int], s: float, o: tuple[float, float], escala: float,
             origem: tuple[float, float], onde: str) -> np.ndarray:
    """Le o quadro registrado no centro de cada pixel da caixa do UP (vizinho mais proximo) e binariza o alfa."""
    w, h = caixa
    u = np.arange(w)
    v = np.arange(h)
    xs = np.floor(s * (origem[0] + escala * (u + 0.5)) + o[0]).astype(int)
    ys = np.floor(s * (origem[1] + escala * (v + 0.5)) + o[1]).astype(int)
    H, W = frame.shape[:2]
    # a caixa do UP e maior que o canvas do master: o que cai fora do canvas fica transparente, mas nenhum pixel
    # opaco do quadro pode ficar fora da parte da grade que cai dentro dele
    dx, dy = (xs >= 0) & (xs < W), (ys >= 0) & (ys < H)
    # as bordas da grade (a celula de cada pixel do UP, nao so o centro dela), em coordenadas do quadro
    gx0, gx1 = s * origem[0] + o[0], s * (origem[0] + escala * w) + o[0]
    gy0, gy1 = s * origem[1] + o[1], s * (origem[1] + escala * h) + o[1]
    ys_in, xs_in = np.where(frame[..., 3] >= ALFA_CORTE)
    if len(ys_in) and (xs_in.min() < gx0 or xs_in.max() + 1 > gx1 or ys_in.min() < gy0 or ys_in.max() + 1 > gy1):
        raise ValueError(f"{onde}: ha pixel opaco do quadro fora da grade do UP")
    q = np.zeros((h, w, 4), dtype=frame.dtype)
    q[np.ix_(dy, dx)] = frame[np.ix_(ys[dy], xs[dx])]
    opaco = q[..., 3] >= ALFA_CORTE
    q[..., 3] = np.where(opaco, 255, 0)
    q[~opaco] = 0
    return q


def limpar(nome: str, registrados: Path, selecao: Path, master: Path, ref_escala: float, ref_origem: tuple[float, float],
           saida: Path, remaster: Path = F.REMASTER) -> Path:
    ficha = json.loads((remaster / "geracao" / nome / "ficha.json").read_text(encoding="utf-8"))
    sel = json.loads(selecao.read_text(encoding="utf-8"))
    tr = json.loads(master.read_text(encoding="utf-8"))["transform"]
    s, o = float(tr["scale"]), (float(tr["offset"][0]), float(tr["offset"][1]))
    idx, ms = sel["sourceIndices"], sel["durations_ms"]
    if len(idx) != len(ms) or not idx:
        raise ValueError("selection: sourceIndices e durations_ms nao casam")
    if any((not isinstance(x, int)) or x <= 0 for x in ms):
        raise ValueError(f"selection: ms invalido {ms}")
    pal = paleta_rgb(ficha)
    caixa = tuple(ficha["caixa"])
    saida.mkdir(parents=True, exist_ok=False)
    quadros = []
    for k, (i, d) in enumerate(zip(idx, ms)):
        p = registrados / f"frame_{i:06d}.png"
        if not p.exists():
            raise FileNotFoundError(p)
        fr = np.array(Image.open(p).convert("RGBA"))
        q = snap(amostrar(fr, caixa, s, o, ref_escala, ref_origem, p.name), pal)
        if not (q[..., 3] == 255).any():
            raise ValueError(f"{p.name}: quadro sem pixel opaco")
        arq = f"f{k:02d}.png"
        Image.fromarray(q).save(saida / arq)
        quadros.append({"arquivo": arq, "ms": int(d), "fonte": p.name})
    (saida / "quadros.json").write_text(json.dumps({"quadros": quadros}, indent=2, ensure_ascii=False), encoding="utf-8")
    return saida


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="E3: quadros do clipe na grade do UP, alfa binario e snap a paleta")
    ap.add_argument("--nome", required=True)
    ap.add_argument("--registrados", type=Path, required=True)
    ap.add_argument("--selecao", type=Path, required=True)
    ap.add_argument("--master", type=Path, required=True)
    ap.add_argument("--ref-escala", type=float, required=True)
    ap.add_argument("--ref-origem", required=True, help="x,y do canto do quadro do UP no PNG de referencia")
    ap.add_argument("--saida", type=Path, required=True)
    ap.add_argument("--remaster", type=Path, default=F.REMASTER)
    a = ap.parse_args(argv)
    ox, oy = (float(t) for t in a.ref_origem.split(","))
    out = limpar(a.nome, a.registrados, a.selecao, a.master, a.ref_escala, (ox, oy), a.saida, a.remaster)
    print(json.dumps({"status": "ok", "saida": str(out)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
