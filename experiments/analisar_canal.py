"""Analise da Etapa B do canal do dono (docs/PLANO_ANALISE_CANAL_DONO.md, secao 4 e adendo B).

    python experiments/analisar_canal.py

Le o que as runs gravaram; nenhuma vida nem partida nova:
  - k = 1: o E1 (artifacts_linhagem/natureza_criacao/especie_fixa/);
  - k = 3 e k = 8: artifacts_linhagem/natureza_criacao_canal/k3/ e k8/ (pets.json, resultado.json, meta.json, vidas);
  - as vidas do E1 arquivadas, para a conferencia byte a byte;
  - artifacts_linhagem/sinal_dono/ (frac D do eixo resistente e o carater adulto por pet, para a transmissao e o corte).
Pareado: cada celula leva (Y_k1, Y_k3, Y_k8, forma). Saida: artifacts_linhagem/natureza_criacao_canal/analise_plano.json.
"""
from __future__ import annotations

import json
import sys
from dataclasses import replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

from digilab.combate_v2.v21.catalogo import Forma, stats  # noqa: E402
from digilab.config import CONFIG_CATALOGO  # noqa: E402
from digilab.metrics import bootstrap_cruzado, ic_percentil  # noqa: E402
from analisar_v21d import (COMPONENTES, DELTA, NICHOS, REAMOSTRAS, SEMENTE, VIDAS_E1, _celulas, _comp,  # noqa: E402
                           _media_contraste, _r2, carregar, forma_de)
from run_natureza_criacao import genoma  # noqa: E402

E1 = RAIZ / "artifacts_linhagem" / "natureza_criacao" / "especie_fixa"
CANAL = RAIZ / "artifacts_linhagem" / "natureza_criacao_canal"
SINAL = RAIZ / "artifacts_linhagem" / "sinal_dono"
NIVEIS = (1, 3, 8)                       # adendo B e o desvio k = 9 -> 8
EIXO_GATE_A = "resistente"
SUBCONJUNTO = ("atencioso", "permissivo")


def conferir(pets_e1, meta_e1, pets_k, meta_k, taxa_e1, taxa_k, k: int) -> dict:
    if pets_k != pets_e1:
        raise RuntimeError(f"k={k}: pets.json diferente do E1 (a vida mudou)")
    if meta_k["hash_parametros_educacao"] != meta_e1["hash_parametros_educacao"]:
        raise RuntimeError(f"k={k}: hash_parametros_educacao diferente")
    c1, ck = meta_e1["config"], meta_k["config"]
    for x in ("rotulo_partidas", "M_B_por_bot", "bootstrap", "donos", "dias", "combate"):
        if c1[x] != ck[x]:
            raise RuntimeError(f"k={k}: config difere do E1 em {x}")
    if c1["rodadas"]["especie_fixa"] != ck["rodadas"]["especie_fixa"]:
        raise RuntimeError(f"k={k}: sementes diferentes")
    if ck["catalogo_painel"] != {"peso_carater_stats": float(k)}:
        raise RuntimeError(f"k={k}: catalogo_painel inesperado {ck['catalogo_painel']}")
    if set(taxa_k) != set(taxa_e1) or len(taxa_k) != 640:
        raise RuntimeError(f"k={k}: celulas nao batem")
    arqs = sorted((CANAL / f"k{k}" / "vidas").glob("*.jsonl"))
    if len(arqs) != 640:
        raise RuntimeError(f"k={k}: esperadas 640 vidas, achei {len(arqs)}")
    for a in arqs:
        if a.read_bytes() != (VIDAS_E1 / a.name).read_bytes():
            raise RuntimeError(f"k={k}: vida {a.name} diferente da do E1")
    return {"pets_iguais_ao_e1": True, "hash_igual": True, "config_igual_fora_do_catalogo": True, "vidas_iguais": len(arqs)}


def estatistica(donos: list[str], contrastes: list, r2s: dict):
    """y[g][d][r] = (Y_k1, Y_k3, Y_k8, forma)"""
    idx = {d: j for j, d in enumerate(donos)}

    def f(y) -> dict:
        out = {}
        cels = _celulas(y)
        for i, k in enumerate(NIVEIS):
            nome = f"k{k}"
            c = _comp(y, i)
            for x in COMPONENTES:
                out[f"frac_{x}|{nome}"] = c["fracao"][x]
                out[f"var_{x}|{nome}"] = c["componentes"][x]
            for a, b in contrastes:
                out[f"{a}-{b}|{nome}"] = _media_contraste(y, idx[a], idx[b], i)
            for rot, filtro in r2s.items():
                out[f"r2_{rot}|{nome}"] = _r2([(c_[i], None, c_[3]) for c_ in cels], 0, filtro)
        for key in list(out):
            if key.endswith("|k1"):
                base = key[:-3]
                for k in NIVEIS[1:]:
                    out[f"{base}|delta_k{k}"] = out[f"{base}|k{k}"] - out[key]
        return out
    return f


def com_ic(y, f) -> dict:
    pontual = f(y)
    ics = {}
    for modo in ("GR", "G"):
        boots = bootstrap_cruzado(y, f, REAMOSTRAS, SEMENTE, reamostrar=modo)
        ics[modo] = {x: ic_percentil([b[x] for b in boots]) for x in pontual}
    return {x: {"estimativa": pontual[x], "ic95_pigeonhole_GR": ics["GR"][x], "ic95_so_genomas": ics["G"][x]}
            for x in sorted(pontual)}


def gate(prim: dict) -> dict:
    dr2 = prim["r2_vivos_13|delta_k8"]
    dfd = prim["frac_D|delta_k8"]
    passo1 = "CANAL ABERTO" if dr2["ic95_pigeonhole_GR"][1] < 0 else "CANAL NAO ABERTO"
    passo2 = None
    if passo1 == "CANAL ABERTO":
        lo, hi = dfd["ic95_pigeonhole_GR"]
        passo2 = ("O DONO PASSA PELO CANAL" if lo > 0 else "O DONO NAO PASSA" if hi < DELTA else "INCONCLUSIVO")
    return {"criterios": {"passo1": "IC95 pigeonhole de delta r2_vivos (k=8 - k=1) todo abaixo de 0 (= 1 - r2 sobe)",
                          "passo2": f"PASSA: limite inferior do IC95 de delta frac_D (k=8) > 0; NAO PASSA: limite superior < {DELTA}"},
            "delta_r2_vivos_k8": dr2, "delta_frac_D_k8": dfd, "passo1": passo1, "passo2": passo2,
            "resultado": passo2 or passo1}


def corte_dos_stats(pets: dict, port: dict) -> dict:
    """fracao dos stats (6 por pet vivo) presos em stat_min ou stat_max em cada k (so stats(), antes do treino)"""
    out = {}
    for k in NIVEIS:
        cat = replace(CONFIG_CATALOGO, peso_carater_stats=float(k))
        presos = total = 0
        for nome, p in pets.items():
            if p["morta"]:
                continue
            esp, temp_ovo, _ = genoma(p["genoma"], p["especie"])
            f = p["forma"]
            s = stats(Forma(esp, f["estagio"], f["ramo"], f["linha"], f["adulta"]), temp_ovo, port[nome]["carater_adul"], cat)
            presos += sum(v in (cat.stat_min, cat.stat_max) for v in s.values())
            total += len(s)
        out[f"k{k}"] = {"presos": presos, "total": total, "fracao": presos / total}
    return out


def tabela(pets, taxas: list[dict], donos) -> list:
    gs = sorted({g for g, _, _ in taxas[0]})
    rs = sorted({r for _, _, r in taxas[0]})
    return [[[tuple(t[(g, d, r)] for t in taxas) + (forma_de(pets[f"{d}@g{g}r{r}"]),) for r in rs] for d in donos] for g in gs]


def main() -> int:
    pets, taxa1, meta1 = carregar(E1)
    taxas, conf = [taxa1], {}
    for k in NIVEIS[1:]:
        pk, tk, mk = carregar(CANAL / f"k{k}")
        conf[f"k{k}"] = conferir(pets, meta1, pk, mk, taxa1, tk, k)
        taxas.append(tk)
    sinal = json.loads((SINAL / "resultado.json").read_text(encoding="utf-8"))
    port = json.loads((SINAL / "portadores_por_pet.json").read_text(encoding="utf-8"))
    frac_d_eixo = sinal["portadores"][f"carater_adol:{EIXO_GATE_A}"]["fracao"]["D"]["estimativa"]
    todos = sorted({p["dono"] for p in pets.values()})
    r2s = {"vivos_13": lambda c: c != "morto", "com_morto_14": None, "8_formas_adultas": lambda c: c in NICHOS}
    y4 = tabela(pets, taxas, todos)
    prim = com_ic(y4, estatistica(todos, [("atencioso", "aleatorio"), ("atencioso", "permissivo")], r2s))
    y2 = tabela(pets, taxas, list(SUBCONJUNTO))
    sec = com_ic(y2, estatistica(list(SUBCONJUNTO), [("atencioso", "permissivo")], {"forma": None}))
    transm = {f"k{k}": prim[f"frac_D|k{k}"]["estimativa"] / frac_d_eixo for k in NIVEIS}
    por_forma = {}
    chaves = sorted(taxa1)
    for i, k in enumerate(NIVEIS):
        grupos = {}
        for c in chaves:
            grupos.setdefault(forma_de(pets[f"{c[1]}@g{c[0]}r{c[2]}"]), []).append(taxas[i][c])
        por_forma[f"k{k}"] = {f: {"n": len(v), "media": sum(v) / len(v)} for f, v in sorted(grupos.items())}
    out = {"plano": "docs/PLANO_ANALISE_CANAL_DONO.md (secao 4 e adendo B)",
           "bootstrap": {"reamostragens": REAMOSTRAS, "semente": SEMENTE, "tipo": "pigeonhole (GR principal; G secundario), pareado"},
           "conferencias": conf, "delta": DELTA, "gate": gate(prim), "primario_4_donos": prim,
           "secundario_atencioso_permissivo": sec,
           "transmissao": {"frac_D_do_eixo_resistente": frac_d_eixo, "frac_D_taxa_sobre_eixo": transm},
           "corte_dos_stats": corte_dos_stats(pets, port), "taxa_media_por_forma": por_forma}
    arq = CANAL / "analise_plano.json"
    arq.write_text(json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print("conferencias:", conf)
    for x in ("r2_vivos_13", "frac_D", "frac_DR", "frac_e", "atencioso-aleatorio"):
        for n in ("k1", "k3", "k8", "delta_k3", "delta_k8"):
            v = prim[f"{x}|{n}"]
            print(f"  {x}|{n}: {v['estimativa']:+.4f} {[round(z, 4) for z in v['ic95_pigeonhole_GR']]}")
    print("corte:", out["corte_dos_stats"])
    print("transmissao:", transm)
    print(f"GATE B: {out['gate']['resultado']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
