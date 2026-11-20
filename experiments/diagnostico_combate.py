"""Etapa 0 da TAREFA_CORRECAO_COMBATE: diagnostico antes de mudar qualquer regra.

    python experiments/diagnostico_combate.py

So sementes de CALIBRACAO (V2: 1101..1505; V2.1: 3101..3505). Nada aqui muda regra.
  1. G4: pares de bots da V2 que terminam no limite de turnos (de artifacts_combate_v2/partidas.csv,
     a run canonica; so leitura).
  2. G5: em que situacoes a esquiva e legal e nao e escolhida, e o que e escolhido no lugar
     (decisoes dos bots da V2, exceto aleatorio e oraculo).
  3. Ferrugem: ablacao por stat (cada stat da especie trocado pelo neutro 10, o resto igual) e
     ablacao de formula (o coeficiente por ponto de cada conversao zerado, para todas as especies);
     taxa da Ferrugem contra as outras especies com o mesmo arquetipo e o mesmo estilo.
  4. marcar: 3 partidas do cacador contra oponentes com a resposta declarada (avancar), rastreadas
     turno a turno (distancia, acoes, marca, dano).
Saida em artifacts_combate_v2c/diagnostico/.
"""

from __future__ import annotations

import collections
import csv
import json
import random
import sys
from dataclasses import replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.combate_v2 import bots as bots_v2  # noqa: E402
from digilab.combate_v2.gambits import PESADO_AUTOMATICO  # noqa: E402
from digilab.combate_v2.partida import sementes_de_rng  # noqa: E402
from digilab.combate_v2.regras import Acao, eh_legal, estado_inicial, resolver, resultado  # noqa: E402
from digilab.combate_v2.v21 import partida as p21  # noqa: E402
from digilab.combate_v2.v21.bots import ADULTOS, FORMAS, com_resposta, lutador_adulto  # noqa: E402
from digilab.combate_v2.v21.regras import Regras, estado_inicial as ei21, resolver as res21, resultado as fim21  # noqa: E402
from digilab.config import CONFIG_CATALOGO, CONFIG_COMBATE_V2, CONFIG_COMBATE_V21, STATS_V21  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402

SAIDA = RAIZ / "artifacts_combate_v2c" / "diagnostico"
SEM_V2 = (1101, 1202, 1303, 1404, 1505)
SEM_V21 = (3101, 3202, 3303, 3404, 3505)


def _dump(o) -> str:
    return json.dumps(o, ensure_ascii=False, indent=2, sort_keys=True)


def g4() -> dict:
    c = collections.defaultdict(lambda: [0, 0])
    for r in csv.DictReader(open(RAIZ / "artifacts_combate_v2" / "partidas.csv", encoding="utf-8")):
        par = "|".join(sorted((r["lado_a"], r["lado_b"])))
        c[par][0] += 1
        c[par][1] += r["fim"] == "limite"
    tot, lim = sum(v[0] for v in c.values()), sum(v[1] for v in c.values())
    pares = {p: {"partidas": n, "limite": l, "fracao": l / n, "parte_dos_limites": l / lim} for p, (n, l) in c.items()}
    com_passivo = sum(v["limite"] for p, v in pares.items() if "tartaruga" in p or "contragolpe" in p)
    return {"fonte": "artifacts_combate_v2/partidas.csv (validacao, so leitura)", "fracao_limite_total": lim / tot,
            "limites_com_tartaruga_ou_contragolpe": com_passivo / lim,
            "pares": dict(sorted(pares.items(), key=lambda x: -x[1]["fracao"]))}


def g5(n: int = 20) -> dict:
    nomes = ("agressivo", "tartaruga", "atirador", "contragolpe", "adaptativo")
    cfg = CONFIG_COMBATE_V2
    situ = collections.Counter()
    no_lugar = collections.defaultdict(collections.Counter)
    for i, x in enumerate(nomes):
        for y in nomes[i:]:
            for s in SEM_V2:
                for k in range(n):
                    semente = derivar_semente("diag-g5", s, x, y, k)
                    lut = (bots_v2.bot(x), bots_v2.bot(y))
                    rngs = [random.Random(z) for z in sementes_de_rng(semente)]
                    e = estado_inicial((lut[0].condicao.hp_max, lut[1].condicao.hp_max),
                                       (lut[0].condicao.guts_inicial, lut[1].condicao.guts_inicial),
                                       (lut[0].condicao.regen_guts, lut[1].condicao.regen_guts))
                    while resultado(e, cfg) is None:
                        esc = [lut[j].estilo.decidir(e, j, rngs[j], cfg) for j in (0, 1)]
                        for j in (0, 1):
                            acao, mot = esc[j]
                            if mot == PESADO_AUTOMATICO or not eh_legal(e, j, Acao.ESQUIVAR, cfg):
                                continue
                            op = e.oponente(j)
                            ctx = "oponente_preparando" if op.preparando else \
                                  f"oponente_livre@{e.distancia.name.lower()}"
                            situ[(ctx, acao is Acao.ESQUIVAR)] += 1
                            if acao is not Acao.ESQUIVAR:
                                no_lugar[ctx][acao.value] += 1
                        e, _ = resolver(e, esc[0][0], esc[1][0], cfg)
    contextos = sorted({c for c, _ in situ})
    resumo = {c: {"esquiva_legal": situ[(c, True)] + situ[(c, False)], "escolheu_esquiva": situ[(c, True)],
                  "fracao_esquiva": situ[(c, True)] / max(1, situ[(c, True)] + situ[(c, False)]),
                  "escolhido_no_lugar": dict(no_lugar[c].most_common())} for c in contextos}
    return {"sementes": SEM_V2, "partidas_por_par_por_semente": n, "bots": nomes,
            "nota": "decisoes em que ESQUIVAR era legal (guts suficiente); pesado automatico fora", "por_contexto": resumo}


def _taxa21(a, b, rot, sementes, n, r):
    pts = []
    for s in sementes:
        for k in range(n):
            sp = derivar_semente("diag-v21", rot, s, a.nome, b.nome, k)
            pts.append(p21.jogar(a, b, sp, r).pontos_a if k < n // 2 else 1.0 - p21.jogar(b, a, sp, r).pontos_a)
    return sum(pts) / len(pts)


def ferrugem(n: int = 20) -> dict:
    outras = [e for e in CONFIG_CATALOGO.especies_ativas if e != "ferrugem"]

    def medir(cat=None, cfg21=None) -> dict:
        r = Regras(v21=cfg21) if cfg21 else Regras()
        por_forma = {}
        for f in FORMAS:
            fe = lutador_adulto(f, "ferrugem", cfg21, cat=cat)
            vals = [_taxa21(fe, lutador_adulto(f, o, cfg21, cat=cat), f"ferr|{f}", SEM_V21, n, r) for o in outras]
            por_forma[f] = sum(vals) / len(vals)
        return {"media": sum(por_forma.values()) / len(por_forma), "por_forma": por_forma}

    base = medir()
    stats = {}
    for k in STATS_V21:
        esp = dict(CONFIG_CATALOGO.especies)
        esp["ferrugem"] = {**esp["ferrugem"], k: 10}
        stats[k] = {"valor_original": CONFIG_CATALOGO.especies["ferrugem"][k], **medir(cat=replace(CONFIG_CATALOGO, especies=esp))}
    formulas = {}
    for campo in ("hp_por_vigor", "guts_inicial_por_folego", "guts_max_por_folego", "regen_por_recuperacao",
                  "mult_por_ponto", "guarda_por_ponto"):
        formulas[campo] = {"valor_original": getattr(CONFIG_COMBATE_V21, campo),
                           **medir(cfg21=replace(CONFIG_COMBATE_V21, **{campo: 0.0}))}
    return {"sementes": SEM_V21, "partidas_por_par_por_semente": n, "especies": dict(CONFIG_CATALOGO.especies),
            "unidade": "pontos da Ferrugem contra as outras 3 especies ativas, mesmo arquetipo e mesmo estilo",
            "base": base, "ablacao_stat_para_10": stats, "ablacao_formula_zerada": formulas}


def marcar(n_partidas: int = 3) -> dict:
    r = Regras()
    rastros = []
    candidatos = [("emboscador", op) for op in ("duelista", "furioso", "muralha", "tita")] + \
                 [("sentinela", op) for op in ("duelista", "espelho")]
    for cac, op in candidatos:
        if len(rastros) >= n_partidas:
            break
        a = lutador_adulto(cac, "cirro")
        b = lutador_adulto(op, "cirro", gambits=com_resposta(ADULTOS[op], "marcar"), nome=f"{op}#resp")
        for k in range(30):
            sp = derivar_semente("diag-marcar", cac, op, k)
            rngs = [random.Random(z) for z in p21.sementes_de_rng(sp)]
            e = ei21(a.perfil, b.perfil)
            turnos = []
            while (fim := fim21(e, r)) is None:
                esc = [(a, b)[j].decidir(e, j, rngs[j], (b, a)[j], r) for j in (0, 1)]
                antes = (e.distancia.name, round(e.lados[0].hp, 1), round(e.lados[1].hp, 1), e.lados[0].marca)
                e2, res = res21(e, esc[0][0], esc[1][0], r)
                turnos.append({"t": e2.turno, "dist_inicio": antes[0], "cacador": esc[0][0].value, "resposta": esc[1][0].value,
                               "marca_antes": antes[3], "marca_usada": res.marca_usada[0],
                               "dano_no_cacador": round(res.dano_recebido[0], 2), "dano_no_oponente": round(res.dano_recebido[1], 2),
                               "dist_fim": e2.distancia.name})
                e = e2
            if fim[0] == 1.0:        # partida representativa: o cacador venceu mesmo com a resposta
                cont = collections.Counter(t["dist_inicio"] for t in turnos)
                rastros.append({"cacador": cac, "oponente_com_resposta": op, "semente": sp, "resultado": fim,
                                "turnos_por_distancia": dict(cont), "marca_usada": sum(t["marca_usada"] for t in turnos),
                                "turnos": turnos})
                break
    return {"resposta_declarada": "avancar quando longe ou medio (bots.RESPOSTAS['marcar'])", "partidas": rastros}


def main() -> int:
    SAIDA.mkdir(parents=True, exist_ok=True)
    print("G4 ..."); (SAIDA / "g4.json").write_text(_dump(g4()), encoding="utf-8", newline="\n")
    print("G5 ..."); (SAIDA / "g5.json").write_text(_dump(g5()), encoding="utf-8", newline="\n")
    print("marcar ..."); (SAIDA / "marcar.json").write_text(_dump(marcar()), encoding="utf-8", newline="\n")
    print("ferrugem ..."); (SAIDA / "ferrugem.json").write_text(_dump(ferrugem()), encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
