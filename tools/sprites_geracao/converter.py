"""SPRITES_GERACAO, etapa G1, E4 (docs/TAREFA_V3_SPRITES_GERACAO.md, secoes 3.1 e 3.4): o resultado do gerador vira um export.

Entrada (pasta `--quadros`, o contrato PROPOSTO do conversor; o JSON real do Sprite Forge e adaptado na G2, SEM FONTE):
  quadros.json  {"quadros": [{"arquivo": "f00.png", "ms": 133, "comida": "c00.png" (opcional),
                              "mordidas": 0..3 (opcional), "farelo": 0|1 (opcional)}, ...]}
  f00.png ...   o personagem, RGBA, ja na paleta do sprite e com alfa binario (o snap e do pixel-mcp, E3), SEM a sombra
Para cada quadro: recorta o personagem, poe o pe na linha `pe_idle` e o centro x das 3 linhas de baixo no centro do Idle, junta por baixo a
sombra do quadro 0 do Idle (sem mudanca, como na M1) e, na camada comida, a carne (a do quadro, ou a de arte propria da M1 pelo
`carne` da ficha, com mordidas e farelo vindos do quadro ou da sequencia do derivado por fracao do tempo).
Saida: <saida>/<Nome>.png/.json e <Nome>_objeto.png/.json, json_array do Aseprite, uma linha de quadros, sem trim e sem rotacao, na caixa do
UP, tag Comer forward. O export e gravado aqui mesmo (o Aseprite nao e preciso para gravar); o `gates.py` e o gerador do atlas conferem o formato.
Falha alto: pixel fora da caixa, personagem abaixo do pe, ms invalido, quadro sem pixel opaco, arquivo ausente.

Uso: python tools/sprites_geracao/converter.py --nome Agumon --quadros DIR --saida DIR [--remaster DIR]
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


def recortar(q: np.ndarray, onde: str) -> tuple[np.ndarray, int, int]:
    """O retangulo do personagem (alfa > 0); devolve o recorte e o canto (x, y) dele no quadro de entrada."""
    ys, xs = np.where(q[..., 3] > 0)
    if len(ys) == 0:
        raise ValueError(f"{onde}: quadro sem pixel opaco")
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    return q[y0:y1, x0:x1], int(x0), int(y0)


def sombra_do_idle(idle0: np.ndarray, pe: int) -> np.ndarray:
    """A camada de sombra reconstruida do quadro 0 do Idle: tudo abaixo do pe e, na linha do pe, so os pixels semitransparentes."""
    s = np.zeros_like(idle0)
    s[pe + 1:] = idle0[pe + 1:]
    linha = idle0[pe]
    semi = (linha[:, 3] > 0) & (linha[:, 3] < 255)
    s[pe][semi] = linha[semi]
    return s


def _sobre(base: np.ndarray, topo: np.ndarray) -> np.ndarray:
    """alfa sobre alfa, com o topo de alfa 0 ou 255 (o personagem e binario); um alfa intermediario no topo levanta."""
    a = topo[..., 3]
    if ((a > 0) & (a < 255)).any():
        raise ValueError("o personagem tem alfa intermediario: o snap da E3 (alfa binario) nao foi feito")
    out = base.copy()
    out[a == 255] = topo[a == 255]
    return out


def colocar(q: np.ndarray, ficha: dict, onde: str) -> tuple[np.ndarray, int, int]:
    """Poe o personagem do quadro na caixa do UP; devolve a camada (H, W, 4) e o deslocamento (dx, dy) aplicado."""
    W, H = ficha["caixa"]
    pe = ficha["pe_idle"]
    rec, x0, y0 = recortar(q, onde)
    op = rec[..., 3] == 255
    linhas = np.where(op.any(axis=1))[0]
    if len(linhas) == 0:
        raise ValueError(f"{onde}: sem pixel de alfa 255")
    ult = int(linhas.max())                                   # linha do pe dentro do recorte
    sub = op[max(0, ult - F.LINHAS_PE + 1):ult + 1]
    cx_rec = float(np.where(sub)[1].mean())
    dy = pe - ult - y0                                        # o pe cai em pe_idle
    dx = int(round(ficha["idle0_centro_x"] - (cx_rec + x0)))   # o centro dos pes cai no do Idle
    cam = np.zeros((H, W, 4), np.uint8)
    h, w = rec.shape[:2]
    X, Y = x0 + dx, y0 + dy
    if X < 0 or Y < 0 or X + w > W or Y + h > H:
        raise ValueError(f"{onde}: o personagem ({w}x{h}) posto no pe fica fora da caixa {W}x{H} (canto {X},{Y})")
    cam[Y:Y + h, X:X + w] = rec
    return cam, dx, dy


def _ponto(img: np.ndarray, x: int, y: int, cor: tuple[int, int, int], onde: str) -> None:
    h, w = img.shape[:2]
    if x < 0 or y < 0 or x >= w or y >= h:
        raise ValueError(f"{onde}: pixel opaco da carne fora da caixa em ({x},{y})")
    img[y, x] = (*cor, 255)


def desenhar_carne(img: np.ndarray, mordidas: int, ox: int, oy: int, farelo: bool, frente: bool, onde: str) -> None:
    """Porta da `carne` e do `farelo` do gerar.lua (arte propria da M1): 12x8, o osso para a direita, a mordida corta colunas da esquerda."""
    corte = F.CORTE[min(mordidas, 3)]
    for r, linha in enumerate(F.CARNE, start=1):
        for c, chv in enumerate(linha, start=1):
            if chv != "." and not ((c - 1) < corte and 2 <= r <= 7):
                _ponto(img, ox + c - 1, oy + r - 1, F.CARNE_COR[chv], onde)
    if corte > 0:
        for r in range(2, 8):
            if F.CARNE[r - 1][corte] != ".":
                _ponto(img, ox + corte, oy + r - 1, F.CARNE_COR["k"], onde)
    if farelo:
        M, H = F.CARNE_COR["M"], F.CARNE_COR["H"]
        pts = ([(-2, 3, M), (-1, 5, H), (-3, 7, M)] if frente else [(-1, 9, M), (1, 11, H), (-2, 13, M)])
        for dx, dy, cor in pts:
            _ponto(img, ox + dx, oy + dy, cor, onde)


def sequencia_por_tempo(ficha: dict, ms: list[int]) -> list[dict]:
    """Mordidas e farelo de cada quadro novo, tirados da sequencia do derivado pela fracao do tempo (o meio do quadro)."""
    seq = ficha["carne"]["sequencia"]
    total_d = sum(s["ms"] for s in seq)
    total = sum(ms)
    out, t = [], 0
    for m in ms:
        f = (t + m / 2) / total * total_d
        acc = 0
        for s in seq:
            acc += s["ms"]
            if f < acc:
                out.append(s)
                break
        else:
            out.append(seq[-1])
        t += m
    return out


def converter(nome: str, quadros_dir: Path, saida: Path, remaster: Path = F.REMASTER) -> Path:
    return converter_com_ficha(nome, F.montar_ficha(nome, remaster), F.carregar_idle0(nome, remaster), quadros_dir, saida)


def converter_com_ficha(nome: str, ficha: dict, idle0: np.ndarray, quadros_dir: Path, saida: Path) -> Path:
    W, H = ficha["caixa"]
    pe = ficha["pe_idle"]
    spec = json.loads((quadros_dir / "quadros.json").read_text(encoding="utf-8"))
    itens = spec["quadros"]
    if not itens:
        raise ValueError("quadros.json sem quadros")
    ms = []
    for i, it in enumerate(itens):
        if not isinstance(it["ms"], int) or isinstance(it["ms"], bool) or it["ms"] <= 0:
            raise ValueError(f"quadro {i}: ms invalido {it['ms']!r}")
        ms.append(it["ms"])
    sombra = sombra_do_idle(idle0, pe)
    seq = sequencia_por_tempo(ficha, ms)
    canto = ficha["carne"]["canto"]
    frente = ficha["orientacao"] == "frente"
    principais, objetos = [], []
    for i, it in enumerate(itens):
        onde = f"{nome} quadro {i} ({it['arquivo']})"
        arq = quadros_dir / it["arquivo"]
        if not arq.exists():
            raise FileNotFoundError(arq)
        q = np.array(Image.open(arq).convert("RGBA"))
        cam, dx, dy = colocar(q, ficha, onde)
        if (cam[pe + 1:, :, 3] > 0).any():
            raise ValueError(f"{onde}: o personagem passa abaixo do pe (linha {pe})")
        principais.append(_sobre(sombra, cam))
        obj = np.zeros((H, W, 4), np.uint8)
        if it.get("comida"):
            c = np.array(Image.open(quadros_dir / it["comida"]).convert("RGBA"))
            if c.shape[:2] != q.shape[:2]:
                raise ValueError(f"{onde}: a comida tem tamanho diferente do personagem")
            ys, xs = np.where(c[..., 3] > 0)
            if len(ys):
                Y, X = ys + dy, xs + dx
                if Y.min() < 0 or X.min() < 0 or Y.max() >= H or X.max() >= W:
                    raise ValueError(f"{onde}: a comida cai fora da caixa")
                obj[Y, X] = c[ys, xs]
        else:
            s = seq[i]
            mord = it.get("mordidas", s["mordidas"])
            far = it.get("farelo", s["farelo"])
            desenhar_carne(obj, mord, canto[0], canto[1], bool(far), frente, onde)
        objetos.append(obj)
    gravar(saida, nome, principais, ms)
    gravar(saida, nome + "_objeto", objetos, ms)
    return saida


def gravar(saida: Path, nome: str, quadros: list[np.ndarray], ms: list[int]) -> None:
    """json_array do Aseprite: uma linha de quadros, sem trim e sem rotacao, tag Comer forward, filename Comer_NN."""
    saida.mkdir(parents=True, exist_ok=True)
    h, w = quadros[0].shape[:2]
    n = len(quadros)
    folha = np.zeros((h, w * n, 4), np.uint8)
    frames = []
    for i, q in enumerate(quadros):
        if q.shape[:2] != (h, w):
            raise ValueError("quadros de tamanhos diferentes")
        folha[:, i * w:(i + 1) * w] = q
        frames.append({"filename": f"Comer_{i:02d}", "frame": {"x": i * w, "y": 0, "w": w, "h": h}, "rotated": False, "trimmed": False,
                       "spriteSourceSize": {"x": 0, "y": 0, "w": w, "h": h}, "sourceSize": {"w": w, "h": h}, "duration": ms[i]})
    Image.fromarray(folha).save(saida / f"{nome}.png")
    meta = {"app": "tools/sprites_geracao/converter.py (formato json_array do Aseprite)", "version": "1", "image": f"{nome}.png",
            "format": "RGBA8888", "size": {"w": w * n, "h": h}, "scale": "1",
            "frameTags": [{"name": "Comer", "from": 0, "to": n - 1, "direction": "forward", "color": "#000000ff"}]}
    (saida / f"{nome}.json").write_text(json.dumps({"frames": frames, "meta": meta}, ensure_ascii=False), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="E4: quadros do gerador para o export do formato do remaster/acoes/export")
    ap.add_argument("--nome", required=True)
    ap.add_argument("--quadros", type=Path, required=True)
    ap.add_argument("--saida", type=Path, required=True)
    ap.add_argument("--remaster", type=Path, default=F.REMASTER)
    a = ap.parse_args(argv)
    if "acoes" in [p.name for p in a.saida.resolve().parents] or a.saida.resolve().name == "acoes":
        raise SystemExit("o conversor nunca escreve em remaster/acoes: use remaster/geracao")
    print(converter(a.nome, a.quadros, a.saida, a.remaster))
    return 0


if __name__ == "__main__":
    sys.exit(main())
