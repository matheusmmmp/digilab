"""SPRITES_GERACAO, etapa G1, E0 (docs/TAREFA_V3_SPRITES_GERACAO.md, secoes 3.1 e 3.4): a ficha do sprite de um Digimon.

Le o export do UP (remaster/export/<Nome>.png/.json) e as ancoras da M1 (tools/sprites_acoes/ancoras.json) e grava, fora do git, em
remaster/geracao/<Nome>/:
  ficha.json   caixa W x H, pe_idle, paleta (todas as cores RGB opacas do export inteiro), faixa de area, ms do derivado (o alvo),
               a sequencia da carne e o texto da acao
  paleta.gpl   a mesma paleta no formato do Aseprite

Tambem e a casa do que os outros scripts dividem: o `Clipe` (quadros, ms e marcas de um export) e o `ler_export`.
Biblioteca padrao + Pillow + numpy. Falha alto: qualquer inconsistencia levanta, nada e corrigido em silencio.
Todo numero novo aqui (0,90, 1,10, 0,15, 800 a 1000 ms, 200 ms, 2 px) e PROPOSTO e SEM FONTE (secao 4.1 da tarefa).

Uso: python tools/sprites_geracao/ficha.py Agumon [--remaster DIR] [--saida DIR]
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from PIL import Image

AQUI = Path(__file__).resolve().parent
ANCORAS = AQUI.parent / "sprites_acoes" / "ancoras.json"
REMASTER = AQUI.parents[2] / "remaster"          # D:\Trab\digilab\remaster, ao lado das worktrees

# PROPOSTOS, SEM FONTE (secao 4.1 da tarefa)
FATOR_AREA_MIN = 0.90
FATOR_AREA_MAX = 1.10
FATOR_CARNE_MAX = 0.15
CICLO_MIN_MS, CICLO_MAX_MS, QUADRO_MAX_MS = 800, 1000, 200
CENTRO_X_MAX = 2.0                                # px, o centro x das 3 linhas de baixo contra o do Idle
LINHAS_PE = 3

# A carne e arte propria da M1 (tools/sprites_acoes/gerar.lua, tabela `cor`): a paleta dela vale para a camada comida.
CARNE_PALETA = [(58, 31, 20), (181, 83, 47), (233, 138, 92), (243, 234, 210)]
CARNE = ["..kkkk......", ".kMMMMk.....", "kMHMMMMk....", "kMMMMMMkkk.k", "kMMMMMMkBBBk", "kMMMMMMkkk.k", ".kMMMMk.....", "..kkkk......"]
CARNE_COR = {"k": CARNE_PALETA[0], "M": CARNE_PALETA[1], "H": CARNE_PALETA[2], "B": CARNE_PALETA[3]}
CORTE = [0, 2, 4, 5]

ACAO = ("inclina para a comida, abre e fecha a boca duas vezes (duas mordidas, com farelo na segunda de cada), volta ao quadro "
        "inicial parado; o inicio e o fim sao o mesmo quadro")


@dataclass
class Clipe:
    """Os quadros de uma tag de um export (json_array do Aseprite): RGBA (H, W, 4) uint8, ms e as marcas de cada quadro."""
    nome: str
    quadros: list[np.ndarray]
    ms: list
    fonte_caixa: list[tuple[int, int]]            # sourceSize de cada quadro
    cortado: list[bool]
    rotacionado: list[bool]
    tag: dict
    tags_do_arquivo: list[str] = field(default_factory=list)


def ler_export(base: Path, tag: str = "Comer") -> Clipe:
    """Le <base>.png/.json e devolve so a tag pedida. Falha alto se faltar arquivo, tag ou se a tag sair dos quadros."""
    jp, pp = Path(f"{base}.json"), Path(f"{base}.png")
    if not jp.exists() or not pp.exists():
        raise FileNotFoundError(f"export incompleto: {jp} / {pp}")
    j = json.loads(jp.read_text(encoding="utf-8"))
    folha = np.array(Image.open(pp).convert("RGBA"))
    frames = j["frames"]
    tags = {t["name"]: t for t in j["meta"]["frameTags"]}
    if tag not in tags:
        raise ValueError(f"{jp.name}: sem a tag {tag} (tem {list(tags)})")
    t = tags[tag]
    if not 0 <= t["from"] <= t["to"] < len(frames):
        raise ValueError(f"{jp.name}: tag {tag} fora dos quadros: {t}")
    qs, ms, caixa, cort, rot = [], [], [], [], []
    for f in frames[t["from"]:t["to"] + 1]:
        r = f["frame"]
        if r["x"] < 0 or r["y"] < 0 or r["x"] + r["w"] > folha.shape[1] or r["y"] + r["h"] > folha.shape[0]:
            raise ValueError(f"{jp.name}: quadro {f['filename']} fora da folha")
        qs.append(folha[r["y"]:r["y"] + r["h"], r["x"]:r["x"] + r["w"]].copy())
        ms.append(f["duration"])
        caixa.append((f["sourceSize"]["w"], f["sourceSize"]["h"]))
        cort.append(bool(f["trimmed"]))
        rot.append(bool(f["rotated"]))
    return Clipe(tag, qs, ms, caixa, cort, rot, t, list(tags))


def paleta_do_export(png: Path) -> list[tuple[int, int, int]]:
    """Todas as cores RGB com alfa 255 da folha inteira, em ordem fixa."""
    a = np.array(Image.open(png).convert("RGBA"))
    op = a[a[..., 3] == 255][:, :3]
    if len(op) == 0:
        raise ValueError(f"{png}: nenhum pixel opaco")
    return sorted({tuple(int(v) for v in c) for c in np.unique(op, axis=0)})


def area_opaca(q: np.ndarray) -> int:
    return int((q[..., 3] == 255).sum())


def carne_sequencia(e: dict, anc: dict) -> list[dict]:
    """A sequencia de mordidas e farelo do derivado, uma entrada por quadro: ms, mordidas acumuladas e farelo 0/1."""
    if e["modo"] == "par":
        seq, mord = [], 0
        for _q, ms, mo, fa in e["seq"]:
            mord += 1 if mo == 1 else 0
            seq.append({"ms": ms, "mordidas": mord, "farelo": fa})
        return seq
    if e["modo"] in ("prova1", "desenhar"):
        return [{"ms": r[5], "mordidas": r[3], "farelo": r[4]} for r in anc["prova1"]]
    raise ValueError(f"modo desconhecido: {e['modo']}")


def carne_canto(e: dict, anc: dict) -> tuple[list[int], bool]:
    """O canto da carne e se e aproximado. No par e o campo `carne`; nos outros modos a gerar.lua leva a boca pela inclinacao, e aqui
    fica o ponto sem inclinacao (aproximado)."""
    if e["modo"] == "par":
        return list(e["carne"]), False
    dx, dy = anc["carne_deslocamento"][e["orientacao"]]
    return [e["boca"][0] + dx + e["recuo_carne"], e["boca"][1] + dy], True


def montar_ficha(nome: str, remaster: Path = REMASTER, ancoras: Path = ANCORAS) -> dict:
    anc = json.loads(Path(ancoras).read_text(encoding="utf-8"))
    if nome not in anc["digimon"]:
        raise KeyError(f"{nome} nao esta no ancoras.json")
    e = anc["digimon"][nome]
    up = remaster / "export" / nome
    idle = ler_export(up, "Idle")
    caixa = list(e["caixa"])
    if any(list(c) != caixa for c in idle.fonte_caixa):
        raise ValueError(f"{nome}: o Idle do UP tem caixa {sorted(set(idle.fonte_caixa))}, o ancoras diz {caixa}")
    areas = [area_opaca(q) for q in idle.quadros]
    ult = [int(np.where((q[..., 3] == 255).any(axis=1))[0].max()) for q in idle.quadros]
    pe = e["pe_idle"]
    if ult[0] != pe:
        raise ValueError(f"{nome}: o quadro 0 do Idle acaba na linha {ult[0]}, o ancoras diz pe_idle={pe}")
    derivado = ler_export(remaster / "acoes" / "export" / nome, "Comer")
    seq = carne_sequencia(e, anc)
    if [s["ms"] for s in seq] != derivado.ms:
        raise ValueError(f"{nome}: a sequencia do ancoras ({[s['ms'] for s in seq]}) nao casa com os ms do derivado ({derivado.ms})")
    canto, aprox = carne_canto(e, anc)
    paleta = paleta_do_export(Path(f"{up}.png"))
    return {
        "versao": 1, "status": "PROPOSTO", "digimon": nome,
        "fonte": f"remaster/export/{nome}.png/.json (UP), tools/sprites_acoes/ancoras.json, remaster/acoes/export/{nome} (derivado)",
        "caixa": caixa, "pe_idle": pe, "orientacao": e["orientacao"], "modo_derivado": e["modo"],
        "idle_ultima_linha": ult,
        "paleta": ["%02x%02x%02x" % c for c in paleta],
        "area": {"idle": areas, "idle_min": min(areas), "idle_max": max(areas),
                 "fator_min": FATOR_AREA_MIN, "fator_max": FATOR_AREA_MAX,
                 "faixa": [FATOR_AREA_MIN * min(areas), FATOR_AREA_MAX * max(areas)],
                 "carne_max": FATOR_CARNE_MAX * min(areas), "carne_fator": FATOR_CARNE_MAX,
                 "carne_base": "menor area do Idle (leitura estrita da secao 4.1)"},
        "idle0_centro_x": centro_x_pe(idle.quadros[0], pe),
        "ms_alvo": derivado.ms, "ciclo_alvo_ms": sum(derivado.ms),
        "ms_limites": {"ciclo_min": CICLO_MIN_MS, "ciclo_max": CICLO_MAX_MS, "quadro_max": QUADRO_MAX_MS},
        "carne": {"paleta": ["%02x%02x%02x" % c for c in CARNE_PALETA], "canto": canto, "canto_aproximado": aprox,
                  "sequencia": seq, "fonte": "tools/sprites_acoes/gerar.lua (arte propria da M1)"},
        "acao": ACAO,
        "tolerancias": {"centro_x_px": CENTRO_X_MAX, "linhas_pe": LINHAS_PE},
    }


def centro_x_pe(q: np.ndarray, pe: int) -> float:
    """O centro x dos pixels opacos nas LINHAS_PE linhas de baixo do personagem (a partir do pe)."""
    sub = q[pe - LINHAS_PE + 1:pe + 1, :, 3] == 255
    xs = np.where(sub)[1]
    if len(xs) == 0:
        raise ValueError("nenhum pixel opaco nas linhas do pe")
    return float(xs.mean())


def carregar_idle0(nome: str, remaster: Path = REMASTER) -> np.ndarray:
    """O quadro 0 do Idle do UP (RGBA): a sombra e o centro dos pes de referencia."""
    return ler_export(remaster / "export" / nome, "Idle").quadros[0]


def escrever_ficha(ficha: dict, pasta: Path) -> None:
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / "ficha.json").write_text(json.dumps(ficha, ensure_ascii=False, indent=1), encoding="utf-8")
    linhas = ["GIMP Palette", f"Name: {ficha['digimon']} (UP)", "Columns: 0", "#"]
    for h in ficha["paleta"]:
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        linhas.append(f"{r:3d} {g:3d} {b:3d} {h}")
    (pasta / "paleta.gpl").write_text("\n".join(linhas) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="E0: a ficha do sprite de um Digimon")
    ap.add_argument("nome")
    ap.add_argument("--remaster", type=Path, default=REMASTER)
    ap.add_argument("--saida", type=Path, default=None, help="padrao: <remaster>/geracao/<Nome>")
    a = ap.parse_args(argv)
    ficha = montar_ficha(a.nome, a.remaster)
    saida = a.saida or a.remaster / "geracao" / a.nome
    escrever_ficha(ficha, saida)
    print(f"{saida}: caixa {ficha['caixa']}, pe {ficha['pe_idle']}, {len(ficha['paleta'])} cores, "
          f"area {ficha['area']['faixa']}, ms {ficha['ms_alvo']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
