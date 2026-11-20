"""Validacao da variante a_c_e2v_v do reequilibrio (docs/VALIDACAO_V21D.md; config experiments/configs/v21d/validacao.json).

    python experiments/validar_v21d.py --conjunto calibracao     # conferencia do script: refaz a rodada 2 (a_c_e2v_v e v21c)
    python experiments/validar_v21d.py --conjunto validacao      # a validacao (uma vez, depois do registro)

Mesmos metodos de experiments/calibrar_equilibrio.py (rodada 2), com as sementes como parametro:
  matriz      8 formas, os dois lados da mesma especie, 100 partidas por par por semente e especie, epsilon dos bots 0,05
              e 0,15; forca = media contra as outras 7.
  painel      pet canonico (epsilon 0,05) contra os 32 bots do painel B, 50 partidas por bot por semente.
  colaterais  S1 (12 formas), E4 na escala, campanha na escala (fatores de ConfigEscala) e E3 (resposta declarada).
Cada etapa roda a V21C (sem chave) e a variante nas MESMAS sementes.

--conjunto calibracao: sementes 3101..3505; exige que tudo saia igual a artifacts_combate_v21c/equilibrio_rodada2/
(matriz, painel e colaterais_a_c_e2v_v), falha alto se nao; grava so conferencia_calibracao.json.
--conjunto validacao: sementes 4101..4505; grava matriz.json, painel.json, colaterais.json e criterios.json em
artifacts_combate_v21c/validacao_v21d/. As conferencias da V21C com os artefatos de validacao gravados (matriz, E3, E4,
campanha, S1) sao registradas, nao interrompem a run: a validacao roda uma vez so.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import platform
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

os.environ.setdefault("EQ_RODADA", "2")            # as variantes da rodada 2 (as regras nao dependem da rodada)
import calibrar_equilibrio as ce  # noqa: E402
import diagnosticar_arquetipos as diag  # noqa: E402
import run_bateria_v21 as rb  # noqa: E402
from digilab.campanha import npc  # noqa: E402
from digilab.combate_v2.v21 import bots  # noqa: E402
from digilab.combate_v2.v21.bots import FORMAS, SOMBRIOS, gambits_adulto  # noqa: E402
from digilab.combate_v2.v21.catalogo import LINHA_DA_FORMA, carater_canonico  # noqa: E402
from digilab.combate_v2.v21.partida import jogar  # noqa: E402
from digilab.config import (CONFIG_BATERIA_V21, CONFIG_CAMPANHA, CONFIG_CATALOGO, CONFIG_ESCALA_LIGADA,  # noqa: E402
                            STATS_V21, ConfigCombateV21C, ConfigCombateV21D)
from digilab.metrics import equilibrio_simetrico, matriz_taxas, suporte  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402

CFG = RAIZ / "experiments" / "configs" / "v21d" / "validacao.json"
R2 = RAIZ / "artifacts_combate_v21c" / "equilibrio_rodada2"
ART_V21C = RAIZ / "artifacts_combate_v21c"
VARIANTE = "a_c_e2v_v"
VS = ("v21c", VARIANTE)
TODAS = tuple(FORMAS) + tuple(SOMBRIOS)


def _ler(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def _media(xs) -> float:
    xs = list(xs)
    if not xs:
        raise ValueError("media de lista vazia")
    return sum(xs) / len(xs)


def _igual(a, b) -> bool:
    return json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def config() -> dict:
    """O registro: a variante do config tem de ser exatamente a_c_e2v_v da rodada 2, e as chaves que o config nao liga
    tem de ser todas as outras da ConfigCombateV21D, desligadas."""
    c = _ler(CFG)
    if c["variante"] != VARIANTE:
        raise ValueError(f"variante do config: {c['variante']!r}")
    ligadas = {k for k, x in c["regras_v21"].items() if x}
    if {k: True for k in ligadas} != ce.VARIANTES[VARIANTE]:
        raise ValueError(f"chaves ligadas do config {sorted(ligadas)} != variante {ce.VARIANTES[VARIANTE]}")
    novas = set(ConfigCombateV21D.__dataclass_fields__) - set(ConfigCombateV21C.__dataclass_fields__)
    if set(c["regras_v21"]) != novas:
        raise ValueError(f"o config precisa listar todas as chaves da V21D: {sorted(novas)}")
    if ce.BASE_VARIANTES.get(VARIANTE):
        raise ValueError("a variante nao pode mexer na base V2C")
    v = diag.config_validacao()
    if (c["sementes_calibracao"], c["sementes_validacao"]) != (v["sementes_calibracao"], v["sementes_validacao"]):
        raise ValueError("sementes do config diferem das da validacao V21C")
    if set(c["sementes_calibracao"]) & set(c["sementes_validacao"]):
        raise ValueError("sementes de calibracao e validacao se sobrepoem")
    if (c["partidas_por_par_por_semente"], c["partidas_por_bot_por_semente_painel"], c["partidas_por_semente_campanha"]) \
            != (ce.N_POR_SEMENTE, ce.M_PAINEL, ce.N_CAMPANHA) or tuple(c["epsilons"]) != ce.EPSILONS:
        raise ValueError("N, M, n da campanha ou epsilons do config diferem dos da rodada 2")
    return c


# ------------------------------------------------------------------ trabalhadores (sementes como parametro)
def _rr(args):
    v, eps, esp, n, sem = args
    r = ce.regras(v)
    lut = {f: ce.lutador(f, esp, v, epsilon=eps) for f in FORMAS}
    conf = []
    for i, fa in enumerate(FORMAS):
        for fb in FORMAS[i:]:
            conf += [(fa, fb, x) for x in diag.jogar_par(lut[fa], lut[fb], f"e1|{esp}", sem, n, r)]
    return v, eps, esp, conf


def _painel(args):
    v, forma, esp_pet, m, sem = args
    r = ce.regras(v)
    pet = ce.lutador(forma, esp_pet, v, nome=f"pet:{forma}@{esp_pet}")
    out = {}
    for s in sem:
        for e in CONFIG_CATALOGO.especies_ativas:
            for f in FORMAS:
                bot = ce.lutador(f, e, v, nome=f"painel:{f}@{e}")
                for k in range(m):
                    sp = derivar_semente(f"diag-arquetipos|B|{s}", bot.nome, k)
                    out.setdefault(bot.nome, []).append(jogar(pet, bot, sp, r).pontos_a if k < m // 2
                                                        else 1.0 - jogar(bot, pet, sp, r).pontos_a)
    return v, forma, esp_pet, out


def _s1(args):
    v, esp, n, sem = args
    r = ce.regras(v)
    lut = {f: ce.lutador(f, esp, v) for f in TODAS}
    conf = []
    for i, fa in enumerate(TODAS):
        for fb in TODAS[i:]:
            conf += [(fa, fb, x) for _, _, x, _ in rb.partidas_par(lut[fa], lut[fb], f"sombria|{esp}", sem, n, r)]
    return v, esp, conf


def _e4(args):
    v, forma, esp, sem = args
    r = ce.regras(v)
    cb, esc = CONFIG_BATERIA_V21, CONFIG_ESCALA_LIGADA
    ad = ce.lutador(forma, esp, v, escala=esc)
    tr = {k: esc.treino_e4 / len(STATS_V21) for k in STATS_V21}
    out = {}
    for rot, treino in (("e4", None), ("e4t", tr)):
        adol = bots.lutador_adolescente(LINHA_DA_FORMA[forma], esp, carater_canonico(forma), r.v21, escala=esc,
                                        treino=treino)
        out[rot] = [x for _, _, x, _ in rb.partidas_par(ad, adol, rot, sem, cb.partidas_e4_por_semente, r)]
    return v, forma, esp, out


def _e3(args):
    v, tec, esp, sem = args
    r = ce.regras(v)
    usuarios = [f for f in FORMAS if rb.TECNICA_DA_LINHA[LINHA_DA_FORMA[f]] == tec]
    orig, resp, por_usuario = [], [], {}
    for u in usuarios:
        n0 = len(orig)
        eu = ce.lutador(u, esp, v)
        for op in FORMAS:
            base = ce.lutador(op, esp, v, nome=f"{op}@{esp}#op")
            gl = bots.com_resposta(gambits_adulto(op, r.v21), tec, bots.RESPOSTAS_V21C)
            rsp = bots.lutador_adulto(op, esp, r.v21, gambits=gl, nome=f"{op}@{esp}#resp")
            orig += [x for _, _, x, _ in rb.partidas_par(eu, base, f"e3|{tec}", sem,
                                                         CONFIG_BATERIA_V21.partidas_e3_por_semente, r)]
            resp += [x for _, _, x, _ in rb.partidas_par(eu, rsp, f"e3|{tec}", sem,
                                                         CONFIG_BATERIA_V21.partidas_e3_por_semente, r)]
        por_usuario[u] = (orig[n0:], resp[n0:])
    return v, tec, esp, orig, resp, por_usuario


def _campanha(args):
    v, tier, est, nome, nivel, n, sem = args
    r = ce.regras_campanha(v)
    adv = npc(tier, escala=CONFIG_ESCALA_LIGADA)
    vals = []
    for e in CONFIG_CATALOGO.especies_ativas:
        a = ce._pet_campanha(est, nome, e, nivel, v)
        pts = []
        for s in sem:
            for k in range(n):
                sp = derivar_semente("calib-campanha", s, a.nome, adv.nome, k)      # como calibrar_campanha.taxa
                pts.append(jogar(a, adv, sp, r).pontos_a if k < n // 2 else 1.0 - jogar(adv, a, sp, r).pontos_a)
        vals.append(sum(pts) / len(pts))
    return v, tier, est, nome, nivel, sum(vals) / len(vals)


# ------------------------------------------------------------------ etapas
def etapa_matriz(pool, sem) -> dict:
    esp = list(CONFIG_CATALOGO.especies_ativas)
    conf = collections.defaultdict(list)
    tarefas = [(v, eps, e, ce.N_POR_SEMENTE, sem) for v in VS for eps in ce.EPSILONS for e in esp]
    for v, eps, e, c in sorted(pool.map(_rr, tarefas), key=lambda x: (x[0], x[1], x[2])):
        conf[(v, eps)] += c
    return {v: {f"{eps:.2f}": ce.resumo(conf[(v, eps)]) for eps in ce.EPSILONS} for v in VS}


def etapa_painel(pool, sem) -> dict:
    esp = list(CONFIG_CATALOGO.especies_ativas)
    res = {}
    for v, f, e, out in pool.map(_painel, [(v, f, e, ce.M_PAINEL, sem) for v in VS for f in FORMAS for e in esp]):
        res[(v, f, e)] = out
    saida = {}
    for v in VS:
        tab = {}
        for f in FORMAS:
            por_esp = {e: _media(p for x in res[(v, f, e)].values() for p in x) for e in esp}
            tab[f] = {"taxa_painel": _media(por_esp.values()), "por_especie_do_pet": por_esp,
                      "contra_cada_forma_do_painel": {g: _media(p for e in esp for nome, x in res[(v, f, e)].items()
                                                                if nome.split(":")[1].split("@")[0] == g for p in x)
                                                      for g in FORMAS}}
        saida[v] = tab
    return saida


def etapa_colaterais(pool, sem, sem_campanha) -> dict:
    """S1, E4 na escala, campanha na escala e E3, como calibrar_equilibrio.etapa_colaterais (rodada 2)."""
    import calibrar_escala
    from calibrar_progressao import NOMES
    if calibrar_escala.META_SEM != 0.30 or calibrar_escala.META_COM != 0.80:
        raise RuntimeError("metas da campanha mudaram")
    esp = list(CONFIG_CATALOGO.especies_ativas)
    out = {}
    conf = collections.defaultdict(list)
    for v, e, c in sorted(pool.map(_s1, [(v, e, ce.N_POR_SEMENTE, sem) for v in VS for e in esp]), key=lambda x: (x[0], x[1])):
        conf[v] += c
    s1 = {}
    for v in VS:
        tx = matriz_taxas(conf[v])
        vence = {s: all(tx[s][x] > 0.5 for x in FORMAS) for s in SOMBRIOS}
        eq = equilibrio_simetrico(tx, list(TODAS), CONFIG_BATERIA_V21.iteracoes_fictitious_play)
        s1[v] = {"S1_ok": not any(vence.values()), "vence_todos_os_normais": vence,
                 "media_sombria_contra_normais": {s: _media(tx[s][x] for x in FORMAS) for s in SOMBRIOS},
                 "vitorias_contra_normais": {s: sorted(x for x in FORMAS if tx[s][x] > 0.5) for s in SOMBRIOS},
                 "sombria_x_normais": {s: {x: tx[s][x] for x in FORMAS} for s in SOMBRIOS},
                 "suporte_com_sombrias": suporte(eq["estrategia"], CONFIG_BATERIA_V21.peso_minimo_suporte)}
    out["S1"] = s1
    e4 = collections.defaultdict(lambda: collections.defaultdict(list))
    for v, f, e, d in pool.map(_e4, [(v, f, e, sem) for v in VS for f in FORMAS for e in esp]):
        for rot, pts in d.items():
            e4[v][(rot, f)] += pts
    out["E4_escala"] = {}
    for v in VS:
        t = {rot: {f: _media(e4[v][(rot, f)]) for f in FORMAS} for rot in ("e4", "e4t")}
        baixo = {f"{f} ({rot})": x for rot, d in t.items() for f, x in d.items() if x < CONFIG_ESCALA_LIGADA.taxa_min_e4}
        out["E4_escala"][v] = {"ok": not baixo, "taxa_sem_treino": t["e4"],
                               f"taxa_adolescente_+{CONFIG_ESCALA_LIGADA.treino_e4:g}": t["e4t"],
                               "abaixo_de_0.60": baixo, "menor": min(min(d.values()) for d in t.values())}
    tarefas = []
    for tier in CONFIG_CAMPANHA.npcs:
        est, nv = calibrar_escala.nivel_tipico(tier)
        for nome in NOMES[est]:
            for nivel in (0, nv):
                tarefas += [(v, tier, est, nome, nivel, ce.N_CAMPANHA, sem_campanha) for v in VS]
    bruto = collections.defaultdict(dict)
    for v, tier, est, nome, nivel, x in pool.map(_campanha, tarefas):
        bruto[(v, tier)].setdefault(nome, {})[nivel] = round(x, 4)
    camp = {}
    for v in VS:
        camp[v] = {}
        for tier in CONFIG_CAMPANHA.npcs:
            est, nv = calibrar_escala.nivel_tipico(tier)
            pn = bruto[(v, tier)]
            s0, c1 = _media(x[0] for x in pn.values()), _media(x[nv] for x in pn.values())
            camp[v][tier] = {"fator": CONFIG_ESCALA_LIGADA.fator_npc[tier], "estagio": est, "nivel_tipico": nv,
                             "sem": round(s0, 4), "com": round(c1, 4),
                             "passa": s0 <= calibrar_escala.META_SEM and c1 >= calibrar_escala.META_COM,
                             "travados": sorted(k for k, x in pn.items() if x[nv] < 0.5), "por_forma": pn}
    out["campanha_escala"] = camp
    tecs = sorted(bots.RESPOSTAS)
    res3 = {}
    for v, tec, e, o, rr, pu in pool.map(_e3, [(v, t, e, sem) for v in VS for t in tecs for e in esp]):
        res3[(v, tec, e)] = (o, rr, pu)
    e3 = {}
    for v in VS:
        e3[v] = {}
        for tec in tecs:
            o = [x for e in esp for x in res3[(v, tec, e)][0]]
            rr = [x for e in esp for x in res3[(v, tec, e)][1]]
            e3[v][tec] = {"taxa_sem_resposta": sum(o) / len(o), "taxa_com_resposta": sum(rr) / len(rr),
                          "reducao": sum(o) / len(o) - sum(rr) / len(rr),
                          "usuarios": [f for f in FORMAS if rb.TECNICA_DA_LINHA[LINHA_DA_FORMA[f]] == tec],
                          "por_usuario": {u: {"taxa_sem_resposta": _media(x for e in esp for x in res3[(v, tec, e)][2][u][0]),
                                              "taxa_com_resposta": _media(x for e in esp for x in res3[(v, tec, e)][2][u][1])}
                                          for u in res3[(v, tec, esp[0])][2]}}
        e3[v] = {"ok": all(x["reducao"] > 0.0 for x in e3[v].values()), "por_tecnica": e3[v]}
    out["E3"] = e3
    return out


# ------------------------------------------------------------------ criterios registrados (docs/VALIDACAO_V21D.md)
def criterios(mat: dict, pain: dict, col: dict, c: dict) -> dict:
    k = c["criterios"]
    lo, hi = k["faixa_forca"]
    exc = k["excecao_declarada"]
    m05, m15 = mat["0.05"], mat["0.15"]
    forca = m05["forca_media_contra_as_outras_7"]
    painel = {f: pain[f]["taxa_painel"] for f in FORMAS}
    fora = lambda d: {f: x for f, x in d.items() if f != exc and not lo <= x <= hi}  # noqa: E731
    vit = {f: len(m05["vitorias_contra_as_outras_7"][f]) for f in FORMAS}
    s1 = col["S1"][VARIANTE]
    e4 = col["E4_escala"][VARIANTE]
    camp = col["campanha_escala"][VARIANTE]
    e3 = col["E3"][VARIANTE]["por_tecnica"]
    npcs_meta = {t: d for t, d in camp.items() if t != k["campanha_excecao_aceita"]}
    itens = {
        "A1_forca_entre_formas_sem_o_furioso": {"ok": not fora(forca), "fora": fora(forca),
                                                "forca": forca},
        "A2_forca_contra_painel_sem_o_furioso": {"ok": not fora(painel), "fora": fora(painel), "painel": painel},
        "A6_lugar_no_ciclo": {"ok": min(vit.values()) >= k["vitorias_min_A6"], "vitorias": vit,
                              "abaixo": {f: x for f, x in vit.items() if x < k["vitorias_min_A6"]}},
        "S1_sombrias": {"ok": s1["S1_ok"], "vence_todos_os_normais": s1["vence_todos_os_normais"],
                        "media_sombria_contra_normais": s1["media_sombria_contra_normais"],
                        "vitorias_contra_normais": s1["vitorias_contra_normais"]},
        "E4_escala": {"ok": all(x >= k["taxa_min_E4"] for d in (e4["taxa_sem_treino"],
                                                                 e4[f"taxa_adolescente_+{CONFIG_ESCALA_LIGADA.treino_e4:g}"])
                                for x in d.values()), "menor": e4["menor"], "abaixo_de_0.60": e4["abaixo_de_0.60"]},
        "campanha_escala_sem_a_sentinela": {
            "ok": all(d["sem"] <= k["campanha_sem_treino_max"] and d["com"] >= k["campanha_com_treino_min"]
                      for d in npcs_meta.values()),
            "por_npc": {t: {"sem": d["sem"], "com": d["com"], "passa": d["passa"], "travados": d["travados"]}
                        for t, d in camp.items()}},
        "E3_pele_dura": {"ok": e3["pele_dura"]["reducao"] > 0.0, "taxa_sem_resposta": e3["pele_dura"]["taxa_sem_resposta"],
                         "taxa_com_resposta": e3["pele_dura"]["taxa_com_resposta"],
                         "por_usuario": e3["pele_dura"]["por_usuario"]},
    }
    rel = k["relatados"]
    relatados = {
        "furioso": {"forca": forca[exc], "painel": painel[exc], "vitorias": vit[exc],
                    "dentro_da_faixa_forca": lo <= forca[exc] <= hi, "dentro_da_faixa_painel": lo <= painel[exc] <= hi},
        "A3_suporte": {"passaria": len(m05["suporte"]) >= rel["A3_suporte_min"], "suporte": m05["suporte"],
                       "estrategia": m05["estrategia_equilibrio"]},
        "A4_decisividade": {"passaria": m05["pares_extremos_lt_0_1_ou_gt_0_9"] <= rel["A4_extremos_max"]["0.05"]
                                        and m15["pares_extremos_lt_0_1_ou_gt_0_9"] <= rel["A4_extremos_max"]["0.15"],
                            "extremos_eps_0.05": m05["pares_extremos_lt_0_1_ou_gt_0_9"],
                            "extremos_eps_0.15": m15["pares_extremos_lt_0_1_ou_gt_0_9"]},
        "A5_amplitude": {"passaria": m05["amplitude_forca"] <= rel["A5_amplitude_max"]
                                     and m15["amplitude_forca"] <= rel["A5_amplitude_max"],
                         "amplitude_eps_0.05": m05["amplitude_forca"], "amplitude_eps_0.15": m15["amplitude_forca"]},
        "A1_A2_com_o_furioso": {"forca_8_na_faixa": all(lo <= x <= hi for x in forca.values()),
                                "painel_8_na_faixa": all(lo <= x <= hi for x in painel.values())},
        "E3_outras_tecnicas": {t: {"taxa_sem_resposta": x["taxa_sem_resposta"], "taxa_com_resposta": x["taxa_com_resposta"],
                                   "reducao": x["reducao"]} for t, x in e3.items() if t != "pele_dura"},
        "campanha_sentinela_excecao_aceita": camp[k["campanha_excecao_aceita"]],
    }
    return {"itens": itens, "passam": sorted(x for x, d in itens.items() if d["ok"]),
            "falham": sorted(x for x, d in itens.items() if not d["ok"]),
            "status": "APROVADA" if all(d["ok"] for d in itens.values()) else "REPROVADA",
            "relatados_nao_reprovam": relatados}


# ------------------------------------------------------------------ conferencias
def conferir_calibracao(mat: dict, pain: dict, col: dict) -> dict:
    """Calibracao: tudo igual ao que a rodada 2 gravou (mesmo metodo, mesmas sementes). Falha alto."""
    m2 = _ler(R2 / "matriz.json")["por_variante"]
    p2 = _ler(R2 / "painel.json")["por_variante"]
    c2 = _ler(R2 / f"colaterais_{VARIANTE}.json")
    out = {f"matriz_{v}": _igual(mat[v], m2[v]) for v in VS}
    out.update({f"painel_{v}": _igual(pain[v], p2[v]) for v in VS})
    for chave in ("S1", "E4_escala", "campanha_escala", "E3"):
        out[f"colaterais_{chave}"] = _igual(col[chave], c2[chave])
    falhas = [k for k, ok in out.items() if not ok]
    if falhas:
        raise RuntimeError(f"o script nao refaz a rodada 2 na calibracao: {falhas}")
    return out


def conferir_validacao_v21c(mat: dict, col: dict) -> dict:
    """Validacao: a V21C destas sementes contra os artefatos de validacao V21C gravados. Registrado, nao interrompe."""
    out = {}
    mv = _ler(ART_V21C / "validacao" / "matriz_arquetipos.json")
    out["matriz_v21c_igual_validacao/matriz_arquetipos.json"] = _igual(mat["v21c"]["0.05"]["taxa"], mv["taxa"])
    uso = _ler(ART_V21C / "validacao" / "uso_tecnicas.json")["resposta_declarada"]
    out["E3_v21c_igual_validacao/uso_tecnicas.json"] = all(
        uso[t]["taxa_sem_resposta"] == x["taxa_sem_resposta"] and uso[t]["taxa_com_resposta"] == x["taxa_com_resposta"]
        for t, x in col["E3"]["v21c"]["por_tecnica"].items())
    ge = {g["gate"]: g for g in _ler(ART_V21C / "validacao_escala" / "gates.json")["gates"]}["E4_escala_estagio_importa"]["valores"]
    e4 = col["E4_escala"]["v21c"]
    out["E4_v21c_igual_validacao_escala/gates.json"] = (
        _igual(e4["taxa_sem_treino"], ge["taxa_sem_treino"])
        and _igual(e4[f"taxa_adolescente_+{CONFIG_ESCALA_LIGADA.treino_e4:g}"], ge["taxa_adolescente_treinado"]))
    ce_val = _ler(RAIZ / "experiments" / "configs" / "escala" / "validacao.json")["resultado"]
    out["campanha_v21c_igual_configs/escala/validacao.json"] = all(
        ce_val[t]["sem"] == d["sem"] and ce_val[t]["com"] == d["com"] for t, d in col["campanha_escala"]["v21c"].items())
    sb = _ler(ART_V21C / "bateria_sombria" / "gates.json")
    out["S1_v21c_igual_bateria_sombria/gates.json (outra config de regras: informativo)"] = _igual(
        col["S1"]["v21c"]["sombria_x_normais"], sb["sombria_x_normais"])
    return out


def _dump(o) -> str:
    return json.dumps(o, ensure_ascii=False, indent=2, sort_keys=True)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Validacao da variante a_c_e2v_v (docs/VALIDACAO_V21D.md)")
    ap.add_argument("--conjunto", required=True, choices=("calibracao", "validacao"))
    ap.add_argument("--processos", type=int, default=8)
    a = ap.parse_args(argv)
    if a.processos > 8:
        raise ValueError("no maximo 8 processos nesta maquina")
    c = config()
    diag.conferir_regras()
    import calibrar_campanha
    if a.conjunto == "calibracao":
        sem, sem_camp = list(c["sementes_calibracao"]), list(calibrar_campanha.SEM_CALIBRACAO)
    else:
        sem, sem_camp = list(c["sementes_validacao"]), list(calibrar_campanha.SEM_VALIDACAO)
    if sem != sem_camp:
        raise ValueError("sementes da campanha diferem das do combate")
    saida = RAIZ / c["saida"]
    if a.conjunto == "validacao" and (saida / "criterios.json").exists():
        raise RuntimeError(f"a validacao ja rodou ({saida / 'criterios.json'}): ela roda uma vez so")
    t0 = time.perf_counter()
    with ProcessPoolExecutor(max_workers=a.processos) as pool:
        print("matriz ...", flush=True)
        mat = etapa_matriz(pool, sem)
        print(f"  {time.perf_counter() - t0:.0f} s; painel ...", flush=True)
        pain = etapa_painel(pool, sem)
        print(f"  {time.perf_counter() - t0:.0f} s; colaterais ...", flush=True)
        col = etapa_colaterais(pool, sem, sem_camp)
        print(f"  {time.perf_counter() - t0:.0f} s", flush=True)
    meta = {"config": str(CFG.relative_to(RAIZ)).replace("\\", "/"), "config_sha256": hashlib.sha256(CFG.read_bytes()).hexdigest(),
            "conjunto": a.conjunto, "sementes": sem, "variante": VARIANTE, "chaves": ce.VARIANTES[VARIANTE],
            "hashes": {v: rb.hashes(ce.cfg_variante(v)) for v in VS}, "regras_v21c": diag.conferir_regras(),
            "especies": list(CONFIG_CATALOGO.especies_ativas),
            "partidas_por_par_por_semente": ce.N_POR_SEMENTE, "partidas_por_bot_por_semente_painel": ce.M_PAINEL,
            "partidas_por_semente_campanha": ce.N_CAMPANHA, "partidas_e4_por_semente": CONFIG_BATERIA_V21.partidas_e4_por_semente,
            "partidas_e3_por_semente": CONFIG_BATERIA_V21.partidas_e3_por_semente, "epsilons": list(ce.EPSILONS),
            "ambiente": {"python": platform.python_version(), "plataforma": platform.platform()},
            "segundos": round(time.perf_counter() - t0)}
    if a.conjunto == "calibracao":
        conf = conferir_calibracao(mat, pain, col)
        saida.mkdir(parents=True, exist_ok=True)
        (saida / "conferencia_calibracao.json").write_text(_dump({"meta": meta, "iguais_a_equilibrio_rodada2": conf}),
                                                             encoding="utf-8", newline="\n")
        print("calibracao: igual a rodada 2 em", sorted(conf))
        return 0
    conf = conferir_validacao_v21c(mat, col)
    saida.mkdir(parents=True, exist_ok=True)
    arquivos = {"matriz.json": {"meta": meta, "por_variante": mat}, "painel.json": {"meta": meta, "por_variante": pain},
                "colaterais.json": {"meta": meta, **col}}
    for nome, obj in arquivos.items():
        (saida / nome).write_text(_dump(obj), encoding="utf-8", newline="\n")
    crit = {"meta": meta, "conferencias_v21c_com_artefatos_de_validacao": conf,
            "variante": criterios(mat[VARIANTE], pain[VARIANTE], col, c),
            "v21c_nas_mesmas_sementes": {"forca": mat["v21c"]["0.05"]["forca_media_contra_as_outras_7"],
                                         "painel": {f: pain["v21c"][f]["taxa_painel"] for f in FORMAS}}}
    (saida / "criterios.json").write_text(_dump(crit), encoding="utf-8", newline="\n")
    print(crit["variante"]["status"], "falham:", crit["variante"]["falham"])
    print({p.name: hashlib.sha256(p.read_bytes()).hexdigest()[:12] for p in sorted(saida.glob("*.json"))})
    return 0


if __name__ == "__main__":
    sys.exit(main())
