"""Avaliador rapido da V21C (TAREFA_CORRECAO_COMBATE, Etapa 3): E1, E2, E3 (so o marcar) e E4.

So sementes de CALIBRACAO (3101..3505) e poucas partidas: serve para escolher ajustes (vetor da
Ferrugem, resposta ao marcar, multiplicador do adolescente). A bateria completa vem depois.
"""

from __future__ import annotations

import sys
from dataclasses import asdict, replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.combate_v2.v21 import partida as p21  # noqa: E402
from digilab.combate_v2.v21.bots import ADULTOS, FORMAS, RESPOSTAS, lutador_adolescente, lutador_adulto  # noqa: E402
from digilab.combate_v2.v21.catalogo import LINHA_DA_FORMA, carater_canonico  # noqa: E402
from digilab.combate_v2.v21.gambits import ListaGambits  # noqa: E402
from digilab.combate_v2.v21.regras import Regras  # noqa: E402
from digilab.config import (CONFIG_BATERIA_V21, CONFIG_CATALOGO, CONFIG_COMBATE_V2, CONFIG_COMBATE_V21,  # noqa: E402
                            ConfigCombateV2C, ConfigCombateV21C)
from digilab.metrics import equilibrio_simetrico, suporte  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402

SEM = (3101, 3202, 3303, 3404, 3505)
BASE_V2C = {"finta": True, "dano_parry": 5.0, "fuga_condicionada": True, "turno_morte_subita": 25, "mult_morte_subita": 1.5}


def regras(v21: dict | None = None) -> Regras:
    return Regras(base=ConfigCombateV2C(**{**asdict(CONFIG_COMBATE_V2), **BASE_V2C}),
                  v21=ConfigCombateV21C(**{**asdict(CONFIG_COMBATE_V21), **(v21 or {})}))


def taxa(a, b, rot, n, r):
    pts = []
    for s in SEM:
        for k in range(n):
            sp = derivar_semente("av21c", rot, s, a.nome, b.nome, k)
            pts.append(p21.jogar(a, b, sp, r).pontos_a if k < n // 2 else 1.0 - p21.jogar(b, a, sp, r).pontos_a)
    return sum(pts) / len(pts)


def com_resposta(gl: ListaGambits, regras_resp) -> ListaGambits:
    return ListaGambits((tuple(regras_resp) + gl.regras)[:CONFIG_COMBATE_V21.max_regras_adulto], gl.final, gl.estagio)


def avaliar(r: Regras, cat=None, n: int = 10, resposta_marcar=None, so=("E1", "E2", "E3", "E4")) -> dict:
    cat = cat or CONFIG_CATALOGO
    esp = list(cat.especies_ativas)
    out = {}
    if "E1" in so:
        soma = {f: {g: [] for g in FORMAS} for f in FORMAS}
        for e in esp:
            lut = {f: lutador_adulto(f, e, r.v21, cat=cat) for f in FORMAS}
            for i, a in enumerate(FORMAS):
                for b in FORMAS[i:]:
                    t = taxa(lut[a], lut[b], f"e1|{e}", n, r)
                    soma[a][b].append(t)
                    soma[b][a].append(1 - t)
        tx = {a: {b: sum(v) / len(v) for b, v in row.items()} for a, row in soma.items()}
        eq = equilibrio_simetrico(tx, list(FORMAS), CONFIG_BATERIA_V21.iteracoes_fictitious_play)
        sup = suporte(eq["estrategia"], CONFIG_BATERIA_V21.peso_minimo_suporte)
        dom = [x for x in FORMAS if all(tx[x][y] > 0.5 for y in FORMAS if y != x)]
        out["E1"] = (not dom and len(sup) >= CONFIG_BATERIA_V21.suporte_minimo_e1, dom, sup)
    if "E2" in so:
        m = {a: {b: [] for b in esp} for a in esp}
        for f in FORMAS:
            lut = {e: lutador_adulto(f, e, r.v21, cat=cat) for e in esp}
            for i, a in enumerate(esp):
                for b in esp[i + 1:]:
                    t = taxa(lut[a], lut[b], f"e2|{f}", n, r)
                    m[a][b].append(t)
                    m[b][a].append(1 - t)
        ag = {a: {b: sum(v) / len(v) for b, v in row.items() if v} for a, row in m.items()}
        dom = [a for a in esp if all(ag[a][b] > 0.5 for b in esp if b != a)]
        out["E2"] = (not dom, dom, {a: {b: round(x, 3) for b, x in row.items()} for a, row in ag.items()})
    if "E3" in so:
        resp = RESPOSTAS["marcar"] if resposta_marcar is None else resposta_marcar
        usuarios = [f for f in FORMAS if LINHA_DA_FORMA[f] == "cacador"]
        orig, com = [], []
        for e in esp:
            for u in usuarios:
                eu = lutador_adulto(u, e, r.v21, cat=cat)
                for op in FORMAS:
                    base = lutador_adulto(op, e, r.v21, nome=f"{op}@{e}#op", cat=cat)
                    rp = lutador_adulto(op, e, r.v21, gambits=com_resposta(ADULTOS[op], resp), nome=f"{op}@{e}#resp", cat=cat)
                    orig.append(taxa(eu, base, "e3", n, r))
                    com.append(taxa(eu, rp, "e3", n, r))
        o, c = sum(orig) / len(orig), sum(com) / len(com)
        out["E3_marcar"] = (c < o, round(o, 3), round(c, 3))
    if "E4" in so:
        e4 = {}
        for f in FORMAS:
            linha = LINHA_DA_FORMA[f]
            vals = [taxa(lutador_adulto(f, e, r.v21, cat=cat), lutador_adolescente(linha, e, carater_canonico(f), r.v21, cat=cat),
                         "e4", n, r) for e in esp]
            e4[f] = round(sum(vals) / len(vals), 3)
        lo, hi = CONFIG_BATERIA_V21.taxa_min_e4, CONFIG_BATERIA_V21.taxa_max_e4
        fora = {f: v for f, v in e4.items() if not lo <= v <= hi}
        out["E4"] = (not fora, fora, e4)
    return out


def catalogo_com(especies: dict | None = None, mult_estagio: dict | None = None):
    c = CONFIG_CATALOGO
    if especies:
        c = replace(c, especies={**c.especies, **especies})
    if mult_estagio:
        c = replace(c, mult_estagio={**c.mult_estagio, **mult_estagio})
    return c
