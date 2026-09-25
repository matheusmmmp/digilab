"""Redesenho das formas sombrias para o gate S2 (TAREFA_TREINO_SOMBRIO). So rotulos de CALIBRACAO.

    python experiments/calibrar_sombrias.py --candidatos experiments/configs/sombrias/r0.json --saida ...

S2 (mesma medida de run_treino.gate_s2, com outro rotulo de sementes): por linha, a sombria e cada
forma normal da linha, com treino uniforme 0..36 (stats absolutos), contra o tier 1 e o tier 2 da
campanha (regras V21C):
  (a) treino minimo para vencer o tier 1 (>= 0,5) da sombria <= o de cada normal da linha;
  (b) media contra o tier 2 (nos 7 niveis) da sombria <= a de cada normal da linha.
Junto, uma checagem rapida do S1 (a sombria nao vence as 8 formas normais) com as regras V2.1 e V21C.
A decisao final e das runs canonicas: run_treino.py (S2) e run_bateria_sombria.py (S1 e E1).

Candidato = {sombria: {"stats": {...}, "gambits": "<nome>", "passiva": {campo_ConfigSombrio: valor}}};
o que faltar fica como esta. Gambits: "base" (os da forma normal de GAMBIT_BASE_SOMBRIA, o desenho original),
"sem_leitura" (base sem as regras que leem o oponente), "pesado" (fecha e solta o pesado sempre que
pode; nao le o oponente), "pesado_esquiva" e "base-i,j" (base sem as regras i, j). O candidato e aplicado trocando CONFIG_SOMBRIO e bots.SOMBRIOS no processo
do calculo (so aqui; o pacote nao muda).
"""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab import campanha  # noqa: E402
from digilab.combate_v2.v21 import bots, catalogo, regras  # noqa: E402
from digilab.combate_v2.v21.bots import ADULTOS, FORMAS, GAMBIT_BASE_SOMBRIA, PREP, _d, _ga, lutador_adulto  # noqa: E402
from digilab.combate_v2.v21.catalogo import LINHA_DA_FORMA, LINHAS, SOMBRIA_DA_LINHA, Forma, carater_canonico, perfil  # noqa: E402
from digilab.combate_v2.v21.gambits import ListaGambits, lista, regra, se  # noqa: E402
from digilab.combate_v2.v21.partida import Lutador, jogar  # noqa: E402
from digilab.combate_v2.v21.regras import REGRAS_PADRAO, Acao as A, Distancia  # noqa: E402
from digilab.config import CONFIG_CATALOGO, CONFIG_SOMBRIO, STATS_V21  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402

NIVEIS = (0, 6, 12, 18, 24, 30, 36)
PERTO, MEDIO, LONGE = Distancia.PERTO, Distancia.MEDIO, Distancia.LONGE
R = campanha.REGRAS_CAMPANHA
# os candidatos partem do desenho ORIGINAL (antes do redesenho), para as rodadas se reproduzirem
ORIGINAL = replace(CONFIG_SOMBRIO, mult_devastador=1.3, mult_regen_colosso_partido=0.5)


def _gambits(sombria: str, nome: str) -> ListaGambits:
    base = ADULTOS[GAMBIT_BASE_SOMBRIA[sombria]]
    if nome == "base":
        return base
    if nome == "sem_leitura":
        return ListaGambits(tuple(r for r in base.regras if not any(c.nome.startswith("oponente_") for c in r.condicoes)),
                            base.final, base.estagio)
    if nome == "pesado":
        return lista([regra(_d(LONGE), A.AVANCAR), regra(_d(MEDIO), A.AVANCAR),
                      regra(se(_d(PERTO), _ga(20)), A.PREPARAR_PESADO), regra(_d(PERTO), A.GOLPE_RAPIDO)], A.CARREGAR)
    if nome == "pesado_esquiva":            # como "pesado", mas foge do pesado do oponente (so le isso)
        return lista([regra(PREP, A.ESQUIVAR), regra(_d(LONGE), A.AVANCAR), regra(_d(MEDIO), A.AVANCAR),
                      regra(se(_d(PERTO), _ga(20)), A.PREPARAR_PESADO), regra(_d(PERTO), A.GOLPE_RAPIDO)], A.CARREGAR)
    if nome.startswith("base-"):             # base sem as regras destes indices (ex.: "base-2,3")
        fora = {int(i) for i in nome[5:].split(",")}
        return ListaGambits(tuple(r for i, r in enumerate(base.regras) if i not in fora), base.final, base.estagio)
    raise ValueError(nome)


def aplicar(cand: dict) -> None:
    """Troca CONFIG_SOMBRIO e bots.SOMBRIOS neste processo."""
    formas = {l: dict(v) for l, v in CONFIG_SOMBRIO.formas.items()}
    campos = {}
    for s, spec in cand.items():
        linha = next(l for l in LINHAS if SOMBRIA_DA_LINHA[l] == s)
        if "stats" in spec:
            formas[linha] = {**formas[linha], "stats": dict(spec["stats"])}
        campos.update(spec.get("passiva", {}))
    cs = replace(ORIGINAL, formas=formas, **campos)
    for mod in (regras, catalogo, bots):
        mod.CONFIG_SOMBRIO = cs
    for s in GAMBIT_BASE_SOMBRIA:
        bots.SOMBRIOS[s] = _gambits(s, cand.get(s, {}).get("gambits", "base"))


def _taxa(a, b, rot, n, r):
    pts = []
    for k in range(n):
        sp = derivar_semente("calib-sombrias", rot, a.nome, b.nome, k)
        pts.append(jogar(a, b, sp, r).pontos_a if k < n // 2 else 1.0 - jogar(b, a, sp, r).pontos_a)
    return sum(pts) / len(pts)


def _curva(args):
    cand, forma, n = args
    aplicar(cand)
    t1, t2 = campanha.npc("tier1_brutamontes"), campanha.npc("tier2_sentinela")
    esp = list(CONFIG_CATALOGO.especies_ativas)
    por_nivel = {}
    for nivel in NIVEIS:
        tr = {k: nivel / len(STATS_V21) for k in STATS_V21} if nivel else None
        v1, v2 = [], []
        for e in esp:
            base = lutador_adulto(forma, e, R.v21)
            f = Forma(e, "adulto", "sereno", LINHA_DA_FORMA[forma], forma)
            p = perfil(f, None, carater_canonico(forma, R.v21), 1.0, R.v21, treino=tr, normalizar_treino=False)
            lut = Lutador(f"{forma}+{nivel}@{e}", p, base.gambits, base.epsilon)
            v1.append(_taxa(lut, t1, "t1", n, R))
            v2.append(_taxa(lut, t2, "t2", n, R))
        por_nivel[nivel] = {"tier1": sum(v1) / len(v1), "tier2": sum(v2) / len(v2)}
    minimo = next((nv for nv in NIVEIS if por_nivel[nv]["tier1"] >= 0.5), None)
    return forma, {"por_nivel": por_nivel, "treino_minimo_tier1": minimo,
                   "tier2_media": sum(x["tier2"] for x in por_nivel.values()) / len(NIVEIS)}


def _s1(args):
    """Media da sombria contra as 8 normais e se vence todas, nas regras V2.1 original e V21C."""
    cand, sombria, n = args
    aplicar(cand)
    out = {}
    for rot, r in (("v21", REGRAS_PADRAO), ("v21c", R)):
        tx = {}
        for x in FORMAS:
            v = [_taxa(lutador_adulto(sombria, e, r.v21), lutador_adulto(x, e, r.v21), f"s1|{rot}", n, r)
                 for e in CONFIG_CATALOGO.especies_ativas]
            tx[x] = sum(v) / len(v)
        out[rot] = {"media": sum(tx.values()) / len(tx), "vence_todos": all(t > 0.5 for t in tx.values()),
                    "por_forma": tx}
    return sombria, out


def avaliar(cand: dict, normais: dict, n: int, pool) -> dict:
    sombrias = list(GAMBIT_BASE_SOMBRIA)
    curvas = dict(pool.map(_curva, [(cand, s, n) for s in sombrias]))
    s1 = dict(pool.map(_s1, [(cand, s, n) for s in sombrias]))
    res, ok = {}, True
    for linha in LINHAS:
        s = SOMBRIA_DA_LINHA[linha]
        comp = {}
        for nf in CONFIG_CATALOGO.arquetipos_adulto[linha]["formas"]:
            ms, mn = curvas[s]["treino_minimo_tier1"], normais[nf]["treino_minimo_tier1"]
            a = (999 if ms is None else ms) <= (999 if mn is None else mn)
            b = curvas[s]["tier2_media"] <= normais[nf]["tier2_media"]
            comp[nf] = {"a": a, "b": b}
            ok = ok and a and b
        res[s] = {"comparacao": comp, "minimo_t1": curvas[s]["treino_minimo_tier1"],
                  "t2_media": round(curvas[s]["tier2_media"], 3), "t1_0": round(curvas[s]["por_nivel"][0]["tier1"], 3),
                  "s1": {k: (round(v["media"], 3), v["vence_todos"]) for k, v in s1[s].items()}}
    return {"S2_ok": ok, "S1_ok": not any(v[k]["vence_todos"] for v in s1.values() for k in v),
            "por_sombria": res, "curvas": curvas, "s1": s1}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidatos", required=True)
    ap.add_argument("--saida")
    ap.add_argument("-n", type=int, default=40)
    a = ap.parse_args()
    cand = json.loads(Path(a.candidatos).read_text(encoding="utf-8"))
    with ProcessPoolExecutor() as pool:
        normais = dict(pool.map(_curva, [({}, f, a.n) for f in FORMAS]))
        print("normais", {f: (c["treino_minimo_tier1"], round(c["tier2_media"], 3)) for f, c in normais.items()}, flush=True)
        out = {}
        for nome, c in cand["candidatos"].items():
            out[nome] = avaliar(c, normais, a.n, pool)
            print(nome, "S2", out[nome]["S2_ok"], "S1", out[nome]["S1_ok"],
                  json.dumps({s: {k: v[k] for k in ("comparacao", "minimo_t1", "t1_0", "t2_media", "s1")}
                              for s, v in out[nome]["por_sombria"].items()}, ensure_ascii=False), flush=True)
    if a.saida:
        Path(a.saida).parent.mkdir(parents=True, exist_ok=True)
        Path(a.saida).write_text(json.dumps({"descricao": __doc__.strip().splitlines()[0], "n": a.n, "niveis": NIVEIS,
                                             "candidatos": cand["candidatos"], "normais": normais, "resultados": out},
                                            ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
