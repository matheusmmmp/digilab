"""SPRITES_GERACAO, etapa G1, E5 (docs/TAREFA_V3_SPRITES_GERACAO.md, secao 4.1): os gates numericos por clipe.

Cada gate roda quadro a quadro sobre um export (o Comer e o Comer_objeto) e levanta `GateFalhou` se qualquer quadro falhar. O `rodar`
roda todos, grava o gates.json (passou/falhou por gate, com o medido) e o CLI sai com 1 se algum falhou. Roda no clipe gerado e no
derivado (a linha de base). Os numeros da regra sao PROPOSTOS, SEM FONTE; um gate que reprova o derivado volta ao Matheus, nao se
ajusta aqui. Os gates NAO aprovam anatomia nem movimento (so o revisor e a leitura cega aprovam).

Interpretacoes de leitura (registradas no registro/2026-11.md): "acima da linha do pe" = linhas < pe_idle; a sombra e comparada nas
linhas > pe_idle (abaixo do pe so ha sombra); o personagem e todo pixel com alfa 255 do export principal; a area da carne se mede contra a
menor area do Idle.

Uso: python tools/sprites_geracao/gates.py --nome Agumon --export DIR [--derivado] [--saida gates.json] [--contato contato_x4.png]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ficha as F  # noqa: E402

GATES = ["G-PAL", "G-CAIXA", "G-PE", "G-ALFA", "G-AREA", "G-MS"]


class GateFalhou(AssertionError):
    pass


def _rgb_int(px: np.ndarray) -> np.ndarray:
    return (px[:, 0].astype(np.int64) << 16) | (px[:, 1].astype(np.int64) << 8) | px[:, 2].astype(np.int64)


def _hex_int(hexes: list[str]) -> np.ndarray:
    return np.array([int(h, 16) for h in hexes], dtype=np.int64)


def _fora_da_paleta(q: np.ndarray, paleta: np.ndarray) -> int:
    px = q[q[..., 3] == 255]
    return int((~np.isin(_rgb_int(px), paleta)).sum()) if len(px) else 0


def _ultima_linha(q: np.ndarray) -> int:
    linhas = np.where((q[..., 3] == 255).any(axis=1))[0]
    if len(linhas) == 0:
        raise GateFalhou("quadro sem pixel opaco")
    return int(linhas.max())


def g_pal(clipe: F.Clipe, objeto: F.Clipe, ficha: dict) -> dict:
    """Todo pixel opaco do personagem na paleta do sprite; o da carne na paleta da carne. Zero fora."""
    pal, pal_c = _hex_int(ficha["paleta"]), _hex_int(ficha["carne"]["paleta"])
    fora = [_fora_da_paleta(q, pal) for q in clipe.quadros]
    fora_c = [_fora_da_paleta(q, pal_c) for q in objeto.quadros]
    medido = {"fora_personagem": fora, "fora_carne": fora_c, "cores_do_clipe": len({tuple(p) for q in clipe.quadros
              for p in q[q[..., 3] == 255][:, :3]})}
    if any(fora) or any(fora_c):
        raise GateFalhou(f"G-PAL: pixels fora da paleta (personagem {fora}, carne {fora_c})")
    return medido


def g_caixa(clipe: F.Clipe, objeto: F.Clipe, ficha: dict) -> dict:
    """sourceSize igual a caixa do UP, sem trim nem rotacao, e nenhum pixel opaco na borda."""
    W, H = ficha["caixa"]
    borda = []
    for c in (clipe, objeto):
        for i, q in enumerate(c.quadros):
            if tuple(c.fonte_caixa[i]) != (W, H) or q.shape[:2] != (H, W):
                raise GateFalhou(f"G-CAIXA: {c.nome} quadro {i} com sourceSize {c.fonte_caixa[i]} e imagem {q.shape[1]}x{q.shape[0]}, "
                                 f"a caixa do UP e {W}x{H}")
            if c.cortado[i] or c.rotacionado[i]:
                raise GateFalhou(f"G-CAIXA: {c.nome} quadro {i} com trim ou rotacao")
            op = q[..., 3] == 255
            n = int(op[0].sum() + op[-1].sum() + op[:, 0].sum() + op[:, -1].sum())
            borda.append(n)
            if n:
                raise GateFalhou(f"G-CAIXA: {c.nome} quadro {i} com {n} pixel(s) opaco(s) na borda (cortado pela caixa)")
    return {"caixa": [W, H], "quadros": len(clipe.quadros) + len(objeto.quadros), "opacos_na_borda": borda}


def g_pe(clipe: F.Clipe, ficha: dict, idle0: np.ndarray) -> dict:
    """A ultima linha opaca e o pe_idle; nada opaco abaixo; sombra = a do Idle (byte a byte, abaixo do pe); centro x dos pes."""
    pe = ficha["pe_idle"]
    ref_x = F.centro_x_pe(idle0, pe)
    ult, dx, sombra = [], [], []
    for i, q in enumerate(clipe.quadros):
        u = _ultima_linha(q)
        ult.append(u)
        if u != pe:
            raise GateFalhou(f"G-PE: quadro {i} acaba na linha {u}, o pe_idle e {pe}")
        if (q[pe + 1:, :, 3] == 255).any():
            raise GateFalhou(f"G-PE: quadro {i} tem pixel opaco abaixo do pe")
        dif = int((q[pe + 1:] != idle0[pe + 1:]).any(axis=2).sum())
        sombra.append(dif)
        if dif:
            raise GateFalhou(f"G-PE: quadro {i}: a sombra difere da do Idle em {dif} pixel(s)")
        d = F.centro_x_pe(q, pe) - ref_x
        dx.append(round(d, 3))
        if abs(d) > ficha["tolerancias"]["centro_x_px"]:
            raise GateFalhou(f"G-PE: quadro {i}: o centro x dos pes anda {d:.2f} px (limite {ficha['tolerancias']['centro_x_px']})")
    return {"pe_idle": pe, "ultima_linha": ult, "centro_x_ref": ref_x, "desvio_centro_x": dx, "sombra_dif": sombra}


def g_alfa(clipe: F.Clipe, objeto: F.Clipe, ficha: dict) -> dict:
    """Acima do pe (linhas < pe_idle), no maximo `alfa_semi_max` (2, D-SG-E) pixels com alfa intermediario por quadro; a carne, 0."""
    pe = ficha["pe_idle"]
    semi = []
    for i, q in enumerate(clipe.quadros):
        a = q[:pe, :, 3]
        n = int(((a > 0) & (a < 255)).sum())
        semi.append(n)
    semi_c = []
    for q in objeto.quadros:
        a = q[..., 3]
        semi_c.append(int(((a > 0) & (a < 255)).sum()))
    lim = ficha["tolerancias"]["alfa_semi_max"]
    medido = {"semitransparentes_acima_do_pe": semi, "limite_por_quadro": lim, "semitransparentes_carne": semi_c}
    if max(semi) > lim or any(semi_c):
        raise GateFalhou(f"G-ALFA: mais de {lim} pixel(s) semitransparente(s) acima do pe por quadro (personagem {semi}), ou alfa "
                         f"intermediario na carne ({semi_c})")
    return medido


def g_area(clipe: F.Clipe, objeto: F.Clipe, ficha: dict) -> dict:
    lo, hi = ficha["area"]["faixa"]
    areas = [F.area_opaca(q) for q in clipe.quadros]
    carnes = [F.area_opaca(q) for q in objeto.quadros]
    medido = {"area": areas, "faixa": [lo, hi], "carne": carnes, "carne_max": ficha["area"]["carne_max"]}
    for i, a in enumerate(areas):
        if not lo <= a <= hi:
            raise GateFalhou(f"G-AREA: quadro {i} com area {a}, faixa [{lo:.1f}; {hi:.1f}]")
    for i, a in enumerate(carnes):
        if a > ficha["area"]["carne_max"]:
            raise GateFalhou(f"G-AREA: carne do quadro {i} com {a} px, limite {ficha['area']['carne_max']:.1f}")
    return medido


def g_ms(clipe: F.Clipe, objeto: F.Clipe, ficha: dict, so_comer: bool) -> dict:
    lim = ficha["ms_limites"]
    for c in (clipe, objeto):
        if c.nome != "Comer":
            raise GateFalhou(f"G-MS: o clipe lido e {c.nome}, deve ser Comer")
        if c.tag["direction"] != "forward":
            raise GateFalhou(f"G-MS: {c.nome} com direcao {c.tag['direction']}, deve ser forward")
        rep = c.tag.get("repeat")
        if rep not in (None, "", 0, "0"):
            raise GateFalhou(f"G-MS: a tag Comer tem repeat={rep}, deve ter laco (sem repeat)")
        if so_comer and c.tags_do_arquivo != ["Comer"]:
            raise GateFalhou(f"G-MS: tags do arquivo {c.tags_do_arquivo}, so Comer e aceita no export gerado")
        if len(c.ms) != len(c.quadros) or not c.ms:
            raise GateFalhou("G-MS: ms e quadros nao casam")
        for m in c.ms:
            if not isinstance(m, int) or isinstance(m, bool) or m <= 0:
                raise GateFalhou(f"G-MS: ms invalido {m!r}")
            if m > lim["quadro_max"]:
                raise GateFalhou(f"G-MS: quadro com {m} ms, o maximo e {lim['quadro_max']}")
    if len(objeto.quadros) != len(clipe.quadros) or objeto.ms != clipe.ms:
        raise GateFalhou(f"G-MS: Comer_objeto ({len(objeto.quadros)} quadros, {objeto.ms}) nao casa com o Comer "
                         f"({len(clipe.quadros)}, {clipe.ms})")
    ciclo = sum(clipe.ms)
    if not lim["ciclo_min"] <= ciclo <= lim["ciclo_max"]:
        raise GateFalhou(f"G-MS: ciclo de {ciclo} ms fora de [{lim['ciclo_min']}; {lim['ciclo_max']}]")
    return {"ms": clipe.ms, "ciclo_ms": ciclo, "quadros": len(clipe.quadros)}


def gate_carga(export: Path, saida: Path, script: Path, remaster: Path | None = None) -> dict:
    """G-CARGA: o gerar_atlas_up_clipes.py roda sem erro sobre o candidato e o clipe Comer entra no atlas. Roda na E6 (so com o candidato)."""
    saida.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, str(script), "--acoes", str(export), "--saida", str(saida)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise GateFalhou(f"G-CARGA: o gerador do atlas saiu com {r.returncode}: {(r.stderr or r.stdout).strip()[-400:]}")
    js = saida / "digilab_atlas_up_clipes.json"
    if not js.exists():
        raise GateFalhou("G-CARGA: o atlas nao foi gravado")
    nomes = json.loads(js.read_text(encoding="utf-8")).get("clipes_nomes", [])
    if "Comer" not in nomes:
        raise GateFalhou(f"G-CARGA: o atlas nao tem o clipe Comer (clipes {nomes})")
    return {"atlas": str(js), "clipes_nomes": nomes}


def rodar(nome: str, export: Path, ficha: dict, idle0: np.ndarray, so_comer: bool) -> dict:
    """Roda os seis gates do export (<export>/<nome> e <nome>_objeto). Nao levanta por gate: o resultado diz passou ou falhou."""
    clipe = F.ler_export(export / nome, "Comer")
    objeto = F.ler_export(export / f"{nome}_objeto", "Comer")
    exec_ = {
        "G-PAL": lambda: g_pal(clipe, objeto, ficha),
        "G-CAIXA": lambda: g_caixa(clipe, objeto, ficha),
        "G-PE": lambda: g_pe(clipe, ficha, idle0),
        "G-ALFA": lambda: g_alfa(clipe, objeto, ficha),
        "G-AREA": lambda: g_area(clipe, objeto, ficha),
        "G-MS": lambda: g_ms(clipe, objeto, ficha, so_comer),
    }
    res = {}
    for g, f in exec_.items():
        try:
            res[g] = {"passou": True, "medido": f()}
        except GateFalhou as e:
            res[g] = {"passou": False, "erro": str(e)}
    return {"digimon": nome, "clipe": "Comer", "export": str(export), "status_faixas": "PROPOSTO, SEM FONTE",
            "gates": res, "passou": all(v["passou"] for v in res.values()), "nao_rodados": ["G-CARGA (E6, so com o candidato)"]}


def folha_contato(clipes: list[tuple[str, F.Clipe]], saida: Path, escala: int = 4) -> None:
    """Folha de contato a `escala`x: uma linha por clipe, quadro a quadro, com os ms embaixo, sobre fundo cinza."""
    fundo = (96, 96, 96, 255)
    h, w = clipes[0][1].quadros[0].shape[:2]
    n = max(len(c.quadros) for _, c in clipes)
    cel_w, cel_h = w * escala, h * escala + 14
    folha = Image.new("RGBA", (n * cel_w, len(clipes) * cel_h), fundo)
    d = ImageDraw.Draw(folha)
    for r, (rotulo, c) in enumerate(clipes):
        for i, q in enumerate(c.quadros):
            im = Image.fromarray(q).resize((w * escala, h * escala), Image.NEAREST)
            folha.alpha_composite(im, (i * cel_w, r * cel_h))
            d.text((i * cel_w + 2, r * cel_h + h * escala + 1), f"{rotulo} {i} {c.ms[i]}ms", fill=(255, 255, 255, 255))
    saida.parent.mkdir(parents=True, exist_ok=True)
    folha.save(saida)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="E5: os gates da secao 4.1 sobre um export")
    ap.add_argument("--nome", required=True)
    ap.add_argument("--export", type=Path, required=True, help="pasta com <Nome>.png/.json e <Nome>_objeto.png/.json")
    ap.add_argument("--derivado", action="store_true", help="e o Comer derivado (a linha de base): ignora as outras tags do arquivo")
    ap.add_argument("--remaster", type=Path, default=F.REMASTER)
    ap.add_argument("--saida", type=Path, required=True, help="o gates.json ou gates_derivado.json")
    ap.add_argument("--contato", type=Path, default=None)
    ap.add_argument("--carga", nargs=3, type=Path, metavar=("EXPORT_CANDIDATO", "ATLAS_SAIDA", "SCRIPT_ATLAS"), default=None,
                    help="roda tambem o G-CARGA sobre um candidato ja montado (na E6)")
    a = ap.parse_args(argv)
    ficha = F.montar_ficha(a.nome, a.remaster)
    idle0 = F.carregar_idle0(a.nome, a.remaster)
    res = rodar(a.nome, a.export, ficha, idle0, so_comer=not a.derivado)
    if a.carga:
        try:
            res["gates"]["G-CARGA"] = {"passou": True, "medido": gate_carga(*a.carga)}
        except GateFalhou as e:
            res["gates"]["G-CARGA"] = {"passou": False, "erro": str(e)}
        res["nao_rodados"] = []
        res["passou"] = all(v["passou"] for v in res["gates"].values())
    a.saida.parent.mkdir(parents=True, exist_ok=True)
    a.saida.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    if a.contato:
        folha_contato([(("derivado" if a.derivado else "gerado"), F.ler_export(a.export / a.nome, "Comer"))], a.contato)
    for g, v in res["gates"].items():
        print(g, "passou" if v["passou"] else "FALHOU: " + v["erro"])
    print(a.saida)
    return 0 if res["passou"] else 1


if __name__ == "__main__":
    sys.exit(main())
