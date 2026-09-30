"""Exploratoria (pos hoc) sobre o E1 da linhagem: de onde vem a interacao dono x ambiente (22% da variancia).

    python experiments/analisar_dono_ambiente.py --entrada D:/Trab/digilab/arquivo/artifacts_linhagem_E1_vidas/natureza_criacao

Le so o que o E1 ja gravou (pets.json e resultado.json de cada rodada); nenhuma vida nem partida nova. Pergunta: a
interacao dono x ambiente e comportamento aprendido ou a combinacao de duas coisas que o simulador ja fixa, o sorteio
de lesoes do ambiente (a semente da lesao deriva da semente da luta, que deriva da semente do ambiente) e a regra de
cada dono sintetico para tratar lesao (donos_educacao: o aleatorio nunca responde a lesao; o relapso so na visita)?

Mede, por rodada:
  - mortes, causa, lesoes e pets lesionados por dono x ambiente; P(morte | pelo menos uma lesao) por dono;
  - a decomposicao cruzada (metrics.componentes_cruzados) da taxa, da morte, das lesoes e da saude final;
  - a mesma decomposicao da taxa so com os donos que nunca deixaram o pet morrer (atencioso e permissivo);
  - o desvio padrao, entre ambientes, da taxa media de cada dono, com IC pelo bootstrap pigeonhole;
  - quanto da taxa a forma final explica sozinha (R2 entre formas; morto conta como forma), os qualificados, e a
    decomposicao do que sobra dentro da forma (taxa menos a media da forma).
Saida: artifacts_linhagem/dono_ambiente/resultado.json. Exploratoria: nenhum gate, nenhuma conclusao confirmatoria.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.metrics import bootstrap_cruzado, componentes_cruzados, ic_percentil  # noqa: E402

RODADAS = ("especie_fixa", "especies_balanceadas")
BOOT, SEMENTE = 2000, 20260930


def tabela(Y: dict, gs, ds, rs) -> list:
    return [[[Y[(g, d, r)] for r in rs] for d in ds] for g in gs]


def fracoes(y) -> dict:
    c = componentes_cruzados(y)
    return {"componentes": c["componentes"], "fracao": c["fracao"]}


def dp_entre_ambientes(y, j: int) -> float:
    """desvio padrao, entre ambientes, da media (sobre genomas) do dono j"""
    medias = [sum(y[i][j][k] for i in range(len(y))) / len(y) for k in range(len(y[0][0]))]
    m = sum(medias) / len(medias)
    return math.sqrt(sum((x - m) ** 2 for x in medias) / (len(medias) - 1))


def analisar_rodada(pasta: Path) -> dict:
    pets = json.loads((pasta / "pets.json").read_text(encoding="utf-8"))
    res = json.loads((pasta / "resultado.json").read_text(encoding="utf-8"))
    gs = sorted({d["genoma"] for d in pets.values()})
    ds = sorted({d["dono"] for d in pets.values()})
    rs = sorted({d["ambiente"] for d in pets.values()})
    por = {(d["genoma"], d["dono"], d["ambiente"]): d for d in pets.values()}
    if len(por) != len(gs) * len(ds) * len(rs):
        raise ValueError(f"{pasta}: tabela incompleta")
    taxa = {}
    for k, v in res["taxa_por_celula"].items():
        g, b, r = k.split("|")
        taxa[(int(g), b, int(r))] = v
    if set(taxa) != set(por):
        raise ValueError(f"{pasta}: taxa_por_celula nao bate com pets.json")

    celulas = {}
    for b in ds:
        for r in rs:
            xs = [por[(g, b, r)] for g in gs]
            celulas[f"{b}|{r}"] = {
                "n": len(xs), "mortes": sum(x["morta"] for x in xs),
                "lesoes": sum(x["sparring"]["lesoes"] for x in xs),
                "lesionados": sum(x["sparring"]["lesoes"] > 0 for x in xs),
                "derrotas_sparring": sum(x["sparring"]["lutas"] - x["sparring"]["vitorias"] for x in xs),
                "taxa_media": sum(taxa[(g, b, r)] for g in gs) / len(gs)}
    causas: dict = {}
    for x in pets.values():
        if x["morte"]:
            causas[x["morte"]["causa"]] = causas.get(x["morte"]["causa"], 0) + 1
    morte_dado_lesao = {}
    for b in ds:
        les = [x for x in pets.values() if x["dono"] == b and x["sparring"]["lesoes"] > 0]
        morte_dado_lesao[b] = {"lesionados": len(les), "mortos": sum(x["morta"] for x in les),
                               "p": (sum(x["morta"] for x in les) / len(les)) if les else None}
    mortos_sem_lesao = sum(1 for x in pets.values() if x["morta"] and x["sparring"]["lesoes"] == 0)
    exposicao = {str(r): sum(celulas[f"{b}|{r}"]["lesoes"] for b in ds) for r in rs}

    Y = {
        "taxa": taxa,
        "morte": {k: float(v["morta"]) for k, v in por.items()},
        "lesoes": {k: float(v["sparring"]["lesoes"]) for k, v in por.items()},
        "saude_final": {k: float(v["saude_final"]) for k, v in por.items()},
    }
    decomp = {nome: fracoes(tabela(v, gs, ds, rs)) for nome, v in Y.items()}
    sobreviventes = [b for b in ds if all(not por[(g, b, r)]["morta"] for g in gs for r in rs)]
    decomp_sem_mortes = None
    if len(sobreviventes) >= 2:
        decomp_sem_mortes = {"donos": sobreviventes, **fracoes(tabela(taxa, gs, sobreviventes, rs))}

    # quanto da taxa a forma final explica sozinha (fracao da soma de quadrados entre formas; morto = categoria)
    def forma_de(x: dict) -> str:
        if x["morta"]:
            return "morto"
        f = x["forma"]
        return f["adulta"] if f["adulta"] else f"adolescente:{f['linha']}"
    def r2_forma(chaves: list) -> dict:
        vals = [taxa[k] for k in chaves]
        m = sum(vals) / len(vals)
        grupos: dict = {}
        for k in chaves:
            grupos.setdefault(forma_de(por[k]), []).append(taxa[k])
        ss_tot = sum((v - m) ** 2 for v in vals)
        ss_ent = sum(len(v) * (sum(v) / len(v) - m) ** 2 for v in grupos.values())
        return {"r2": ss_ent / ss_tot if ss_tot > 0 else 0.0, "n_formas": len(grupos),
                "taxa_media_por_forma": {f: {"n": len(v), "taxa": sum(v) / len(v)} for f, v in sorted(grupos.items())}}
    todos = sorted(por)
    forma = {"todos": r2_forma(todos), "so_donos_sem_mortes": r2_forma([k for k in todos if k[1] in sobreviventes])}
    # o que sobra dentro da forma: taxa menos a media da forma dela, decomposta como a taxa
    media_forma = {f: v["taxa"] for f, v in forma["todos"]["taxa_media_por_forma"].items()}
    residuo = {k: taxa[k] - media_forma[forma_de(por[k])] for k in todos}
    forma["residuo_dentro_da_forma"] = {"ss_total": sum(v * v for v in residuo.values()),
                                        **fracoes(tabela(residuo, gs, ds, rs))}
    vivos = {b: [residuo[k] for k in todos if k[1] == b and not por[k]["morta"]] for b in ds}
    forma["residuo_medio_por_dono_vivos"] = {b: {"n": len(v), "media": sum(v) / len(v)} for b, v in vivos.items() if v}
    qualificados = {f"{b}|{r}": sum(1 for g in gs if not por[(g, b, r)]["morta"] and por[(g, b, r)]["adulto_liberado"])
                    for b in ds for r in rs}

    y = tabela(taxa, gs, ds, rs)
    pontual = {b: dp_entre_ambientes(y, j) for j, b in enumerate(ds)}
    boots = bootstrap_cruzado(y, lambda t: [dp_entre_ambientes(t, j) for j in range(len(ds))], BOOT, SEMENTE)
    dp = {b: {"estimativa": pontual[b], "ic95": ic_percentil([x[j] for x in boots])} for j, b in enumerate(ds)}
    return {"donos": ds, "ambientes": rs, "n_genomas": len(gs), "celulas": celulas, "causas_de_morte": causas,
            "mortos_sem_lesao": mortos_sem_lesao, "morte_dado_lesao": morte_dado_lesao,
            "exposicao_a_lesao_por_ambiente": exposicao, "decomposicao": decomp,
            "decomposicao_taxa_so_donos_sem_mortes": decomp_sem_mortes, "dp_taxa_entre_ambientes": dp,
            "forma_final": forma, "qualificados_adulto": qualificados}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--entrada", required=True, help="pasta natureza_criacao do E1 (com as rodadas)")
    ap.add_argument("--saida", default=str(RAIZ / "artifacts_linhagem" / "dono_ambiente"))
    a = ap.parse_args(argv)
    ent = Path(a.entrada)
    out = {"descricao": __doc__.strip().splitlines()[0], "natureza": "exploratoria, pos hoc; sem gate",
           "entrada": str(ent), "bootstrap": {"reamostragens": BOOT, "semente": SEMENTE, "tipo": "pigeonhole GR"},
           "rodadas": {r: analisar_rodada(ent / r) for r in RODADAS}}
    saida = Path(a.saida)
    saida.mkdir(parents=True, exist_ok=True)
    (saida / "resultado.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
                                          encoding="utf-8", newline="\n")
    for r, d in out["rodadas"].items():
        print(f"== {r}: causas {d['causas_de_morte']}, mortos sem lesao {d['mortos_sem_lesao']}")
        print("   exposicao a lesao por ambiente:", d["exposicao_a_lesao_por_ambiente"])
        print("   P(morte | lesionado):", {b: (v["mortos"], v["lesionados"]) for b, v in d["morte_dado_lesao"].items()})
        for nome, dec in d["decomposicao"].items():
            f = dec["fracao"]
            print(f"   {nome:12s} G {f['G']:.3f}  D {f['D']:.3f}  R {f['R']:.3f}  DR {f['DR']:.3f}  e {f['e']:.3f}")
        s = d["decomposicao_taxa_so_donos_sem_mortes"]
        if s:
            print(f"   taxa so {s['donos']}: G {s['fracao']['G']:.3f} D {s['fracao']['D']:.3f} DR {s['fracao']['DR']:.3f} e {s['fracao']['e']:.3f}")
        print(f"   R2 da forma final: todos {d['forma_final']['todos']['r2']:.3f}, "
              f"so donos sem mortes {d['forma_final']['so_donos_sem_mortes']['r2']:.3f}")
        rd = d["forma_final"]["residuo_dentro_da_forma"]["fracao"]
        print(f"   residuo dentro da forma: G {rd['G']:.3f} D {rd['D']:.3f} R {rd['R']:.3f} DR {rd['DR']:.3f} "
              f"GD {rd['GD']:.3f} e {rd['e']:.3f}")
        print("   dp da taxa entre ambientes:", {b: (round(v["estimativa"], 4), [round(x, 4) for x in v["ic95"]])
                                                for b, v in d["dp_taxa_entre_ambientes"].items()})
    return 0


if __name__ == "__main__":
    sys.exit(main())
