"""Analise do painel do E1 com a V21D contra o E1 (V21C), pelo plano registrado antes (docs/PLANO_ANALISE_V21D.md).

    python experiments/analisar_v21d.py

Le o que as duas runs gravaram; nenhuma vida nem partida nova:
  - V21C: artifacts_linhagem/natureza_criacao/especie_fixa/ (pets.json, resultado.json -> taxa_por_celula, meta.json);
  - V21D: artifacts_linhagem/natureza_criacao_v21d/especie_fixa/ (os mesmos arquivos e as vidas);
  - as vidas do E1, arquivadas fora do repo (--vidas-e1), para a conferencia byte a byte.
Conferencias da secao 9 (falham alto), estimandos primarios e secundarios, gate da secao 7 e QD da secao 8.
Saida: artifacts_linhagem/natureza_criacao_v21d/especie_fixa/analise_plano.json.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.metrics import (bootstrap_cruzado, componentes_cruzados, ic_percentil, icc_um_fator,  # noqa: E402
                             kappa_fleiss, qualidade_diversidade, r2_por_categoria)

E1 = RAIZ / "artifacts_linhagem" / "natureza_criacao" / "especie_fixa"
V21D = RAIZ / "artifacts_linhagem" / "natureza_criacao_v21d" / "especie_fixa"
VIDAS_E1 = Path("D:/Trab/digilab/arquivo/artifacts_linhagem_E1_vidas/natureza_criacao/especie_fixa/vidas")
VALIDACAO = RAIZ / "artifacts_combate_v21c" / "validacao_v21d" / "criterios.json"

# fixados no plano (secoes 4, 5, 7 e 8)
DONOS_PRIMARIO = ("atencioso", "permissivo")
REAMOSTRAS, SEMENTE = 10000, 20260930
DELTA = 0.05
NICHOS = ("duelista", "emboscador", "espelho", "furioso", "muralha", "sentinela", "tita", "vigia")
COMPONENTES = ("G", "D", "R", "GD", "GR", "DR", "e")


def forma_de(p: dict) -> str:
    """categoria da forma final (a mesma de analisar_dono_ambiente): morto, forma adulta/sombria ou adolescente"""
    if p["morta"]:
        return "morto"
    f = p["forma"]
    return f["adulta"] if f["adulta"] else f"adolescente:{f['linha']}"


def carregar(pasta: Path) -> tuple[dict, dict, dict]:
    pets = json.loads((pasta / "pets.json").read_text(encoding="utf-8"))
    res = json.loads((pasta / "resultado.json").read_text(encoding="utf-8"))
    meta = json.loads((pasta / "meta.json").read_text(encoding="utf-8"))
    taxa = {}
    for k, v in res["taxa_por_celula"].items():
        g, b, r = k.split("|")
        taxa[(int(g), b, int(r))] = v
    return pets, taxa, meta


# ------------------------------------------------------------------ conferencias (secao 9)
def conferir(pets_c, pets_d, meta_c, meta_d, taxa_c, taxa_d, vidas_e1: Path) -> dict:
    if pets_c != pets_d:
        raise RuntimeError("pets.json da V21D diferente do E1: a vida mudou, run invalida")
    if meta_c["hash_parametros_educacao"] != meta_d["hash_parametros_educacao"]:
        raise RuntimeError("hash_parametros_educacao diferente do E1")
    cfg_c, cfg_d = meta_c["config"], meta_d["config"]
    for k in ("rotulo_partidas", "M_B_por_bot", "bootstrap", "donos", "dias"):
        if cfg_c[k] != cfg_d[k]:
            raise RuntimeError(f"config da V21D difere do E1 em {k}")
    if cfg_c["rodadas"]["especie_fixa"] != cfg_d["rodadas"]["especie_fixa"]:
        raise RuntimeError("sementes da rodada especie_fixa diferentes do E1")
    if set(taxa_c) != set(taxa_d) or len(taxa_c) != 640:
        raise RuntimeError("celulas das duas condicoes nao batem")
    arqs = sorted((V21D / "vidas").glob("*.jsonl"))
    if len(arqs) != 640:
        raise RuntimeError(f"esperadas 640 vidas da V21D, achei {len(arqs)}")
    for a in arqs:
        if a.read_bytes() != (vidas_e1 / a.name).read_bytes():
            raise RuntimeError(f"vida {a.name} diferente da do E1")
    mortes_prim = [k for k, p in pets_d.items() if p["dono"] in DONOS_PRIMARIO and p["morta"]]
    if mortes_prim:
        raise RuntimeError(f"morte no subconjunto primario: {mortes_prim}")
    return {"pets_iguais_ao_e1": True, "hash_parametros_educacao_igual": True, "config_igual_fora_das_chaves": True,
            "vidas_byte_a_byte_iguais": len(arqs), "mortes_no_subconjunto_primario": 0}


# ------------------------------------------------------------------ estatisticas
def _comp(y, idx: int) -> dict:
    c = componentes_cruzados([[[cel[idx] for cel in yd] for yd in yg] for yg in y])
    return c


def _celulas(y):
    return [cel for yg in y for yd in yg for cel in yd]


def _r2(cels, idx: int, filtro=None) -> float:
    xs = [c for c in cels if filtro is None or filtro(c[2])]
    return r2_por_categoria([c[idx] for c in xs], [c[2] for c in xs])["r2"]


def _media_contraste(y, j1: int, j2: int, idx: int) -> float:
    vals = [yg[j1][k][idx] - yg[j2][k][idx] for yg in y for k in range(len(yg[0]))]
    return sum(vals) / len(vals)


def estatistica(donos: list[str], contrastes: list[tuple[str, str]], r2s: dict):
    """devolve f(y) -> dict; y[g][d][r] = (Y_V21C, Y_V21D, forma)"""
    idx = {d: j for j, d in enumerate(donos)}

    def f(y) -> dict:
        out = {}
        for nome, i in (("v21c", 0), ("v21d", 1)):
            c = _comp(y, i)
            for k in COMPONENTES:
                out[f"frac_{k}|{nome}"] = c["fracao"][k]
                out[f"var_{k}|{nome}"] = c["componentes"][k]
            for x, z in contrastes:
                out[f"{x}-{z}|{nome}"] = _media_contraste(y, idx[x], idx[z], i)
            cels = _celulas(y)
            for rot, filtro in r2s.items():
                out[f"r2_{rot}|{nome}"] = _r2(cels, i, filtro)
        for k in list(out):
            if k.endswith("|v21c"):
                base = k[:-5]
                out[f"{base}|delta"] = out[f"{base}|v21d"] - out[k]
        return out
    return f


def com_ic(y, f) -> dict:
    pontual = f(y)
    ics = {}
    for modo in ("GR", "G"):
        boots = bootstrap_cruzado(y, f, REAMOSTRAS, SEMENTE, reamostrar=modo)
        ics[modo] = {k: ic_percentil([b[k] for b in boots]) for k in pontual}
    return {k: {"estimativa": pontual[k], "ic95_pigeonhole_GR": ics["GR"][k], "ic95_so_genomas": ics["G"][k]}
            for k in sorted(pontual)}


def gate(prim: dict) -> dict:
    dr2 = prim["r2_forma|delta"]
    dfd = prim["frac_D|delta"]
    passo1 = "COMPRESSAO VERIFICADA" if dr2["ic95_pigeonhole_GR"][1] < 0 else "COMPRESSAO NAO VERIFICADA"
    passo2 = None
    if passo1 == "COMPRESSAO VERIFICADA":
        lo, hi = dfd["ic95_pigeonhole_GR"]
        passo2 = ("PREDICAO CONFIRMADA" if lo > 0 else "PREDICAO REFUTADA (arquitetura)" if hi < DELTA
                  else "INCONCLUSIVO")
    return {"criterios": {"passo1": "limite superior do IC95 pigeonhole de delta r2_forma < 0",
                          "passo2": f"CONFIRMADA: limite inferior do IC95 de delta frac_D > 0; REFUTADA: limite superior < {DELTA}; senao INCONCLUSIVO"},
            "delta_r2_forma": dr2, "delta_frac_D": dfd, "passo1": passo1, "passo2": passo2,
            "resultado": passo2 or passo1}


# ------------------------------------------------------------------ QD (secao 8)
def qd(y, donos: list[str]) -> dict:
    """por dono: cobertura e QD-score nas duas condicoes, kappa de Fleiss e concordancia da forma entre ambientes, ICC
    da taxa entre ambientes"""
    out = {}
    for j, d in enumerate(donos):
        cels = [yg[j][k] for yg in y for k in range(len(yg[0]))]
        itens = [[yg[j][k][2] for k in range(len(yg[0]))] for yg in y]
        kf = kappa_fleiss(itens)
        o = {"kappa_fleiss": kf["kappa"], "concordancia_pares": kf["concordancia_pares"]}
        for nome, i in (("v21c", 0), ("v21d", 1)):
            q = qualidade_diversidade([c[i] for c in cels], [c[2] for c in cels], NICHOS)
            o[f"cobertura|{nome}"] = q["cobertura"]
            o[f"qd_score|{nome}"] = q["qd_score"]
            o[f"icc_taxa|{nome}"] = icc_um_fator([[yg[j][k][i] for k in range(len(yg[0]))] for yg in y])
        o["qd_score|delta"] = o["qd_score|v21d"] - o["qd_score|v21c"]
        o["icc_taxa|delta"] = o["icc_taxa|v21d"] - o["icc_taxa|v21c"]
        if o["cobertura|v21c"] != o["cobertura|v21d"]:
            raise RuntimeError(f"cobertura de {d} difere entre as condicoes com as mesmas formas")
        out.update({f"{d}:{k}": v for k, v in o.items()})
    return out


def qd_com_ic(y, donos: list[str]) -> dict:
    f = lambda t: qd(t, donos)  # noqa: E731
    pontual = f(y)
    boots = bootstrap_cruzado(y, f, REAMOSTRAS, SEMENTE, reamostrar="GR")
    return {k: {"estimativa": v, "ic95_pigeonhole_GR": ic_percentil([b[k] for b in boots])} for k, v in sorted(pontual.items())}


# ------------------------------------------------------------------ descritivos
def por_forma(pets: dict, taxa_c: dict, taxa_d: dict) -> dict:
    chaves = sorted(taxa_c)
    cats = [forma_de(pets[f"{b}@g{g}r{r}"]) for g, b, r in chaves]
    rc = r2_por_categoria([taxa_c[k] for k in chaves], cats)["media_por_categoria"]
    rd = r2_por_categoria([taxa_d[k] for k in chaves], cats)["media_por_categoria"]
    tab = {c: {"n": rc[c]["n"], "v21c": rc[c]["media"], "v21d": rd[c]["media"], "delta": rd[c]["media"] - rc[c]["media"]}
           for c in rc}
    adultas = [c for c in NICHOS if c in tab]
    amp = {nome: max(tab[c][nome] for c in adultas) - min(tab[c][nome] for c in adultas) for nome in ("v21c", "v21d")}
    return {"taxa_media_por_forma": tab, "amplitude_entre_formas_adultas": amp, "formas_adultas_presentes": adultas}


def validacao() -> dict:
    c = json.loads(VALIDACAO.read_text(encoding="utf-8"))
    return {"fonte": str(VALIDACAO.relative_to(RAIZ)).replace("\\", "/"),
            "forca_v21c": c["v21c_nas_mesmas_sementes"]["forca"], "painel_v21c": c["v21c_nas_mesmas_sementes"]["painel"],
            "forca_v21d": c["variante"]["itens"]["A1_forca_entre_formas_sem_o_furioso"]["forca"],
            "painel_v21d": c["variante"]["itens"]["A2_forca_contra_painel_sem_o_furioso"]["painel"]}


def tabela(pets, taxa_c, taxa_d, donos) -> tuple[list, list, list]:
    gs = sorted({g for g, _, _ in taxa_c})
    rs = sorted({r for _, _, r in taxa_c})
    y = [[[(taxa_c[(g, d, r)], taxa_d[(g, d, r)], forma_de(pets[f"{d}@g{g}r{r}"])) for r in rs] for d in donos] for g in gs]
    return y, gs, rs


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--vidas-e1", default=str(VIDAS_E1))
    a = ap.parse_args(argv)
    pets_c, taxa_c, meta_c = carregar(E1)
    pets_d, taxa_d, meta_d = carregar(V21D)
    conf = conferir(pets_c, pets_d, meta_c, meta_d, taxa_c, taxa_d, Path(a.vidas_e1))
    todos = sorted({p["dono"] for p in pets_c.values()})

    y1, _, _ = tabela(pets_c, taxa_c, taxa_d, list(DONOS_PRIMARIO))
    prim = com_ic(y1, estatistica(list(DONOS_PRIMARIO), [("atencioso", "permissivo")],
                                  {"forma": None, "8_formas_adultas": lambda c: c in NICHOS}))
    y4, _, _ = tabela(pets_c, taxa_c, taxa_d, todos)
    comp = com_ic(y4, estatistica(todos, [("atencioso", "aleatorio"), ("atencioso", "permissivo")],
                                  {"vivos_13": lambda c: c != "morto", "com_morto_14": None,
                                   "8_formas_adultas": lambda c: c in NICHOS}))
    mortes = {f"{d}|{r}": sum(1 for p in pets_c.values() if p["dono"] == d and p["ambiente"] == r and p["morta"])
              for d in todos for r in sorted({p["ambiente"] for p in pets_c.values()})}
    out = {"plano": "docs/PLANO_ANALISE_V21D.md", "bootstrap": {"reamostragens": REAMOSTRAS, "semente": SEMENTE,
                                                                  "tipo": "pigeonhole (GR principal; G secundario), pareado"},
           "conferencias": conf, "subconjunto_primario": list(DONOS_PRIMARIO), "delta": DELTA,
           "gate": gate(prim), "primario": prim, "completa_4_donos": comp,
           "qd": qd_com_ic(y4, todos), "mortes_por_dono_e_ambiente": mortes,
           "formas": por_forma(pets_c, taxa_c, taxa_d), "validacao_v21d_bot_x_bot": validacao()}
    arq = V21D / "analise_plano.json"
    arq.write_text(json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    g = out["gate"]
    print(f"conferencias: {conf}")
    for k in ("r2_forma", "frac_D", "frac_G", "frac_DR", "frac_e"):
        for c in ("v21c", "v21d", "delta"):
            v = prim[f"{k}|{c}"]
            print(f"  {k}|{c}: {v['estimativa']:+.4f} {[round(x, 4) for x in v['ic95_pigeonhole_GR']]}")
    print(f"GATE: {g['resultado']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
