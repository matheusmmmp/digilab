"""Reequilibrio dos arquetipos do combate V21C, rodadas 1 e 2: mede os candidatos (chaves da ConfigCombateV21D) nas
sementes de CALIBRACAO e confere o gate proposto em docs/DIAGNOSTICO_ARQUETIPOS.md (secao 7).

    python experiments/calibrar_equilibrio.py --rodada 2 --etapa todas
    python experiments/calibrar_equilibrio.py --rodada 2 --etapa colaterais --variante a_c_e2v_v

    python experiments/calibrar_equilibrio.py --etapa todas --processos 8
    python experiments/calibrar_equilibrio.py --etapa matriz|painel|gate
    python experiments/calibrar_equilibrio.py --etapa colaterais --variante a

Variantes (regras da validacao V21C, experiments/configs/v21c/validacao.json, mais as chaves):
  v21c  sem chave nenhuma (ConfigCombateV21C: a de hoje)
  a     preparo_sob_pele_oculto
  c     muralha_lista_espelho
  a_c   as duas
Rodada 2 (docs/EQUILIBRIO_RODADA2.md, saida em artifacts_combate_v21c/equilibrio_rodada2/), sempre sobre a_c:
  d2    investida_erra_contra_recuo           e1   preparo_prende
  e2t   tita_bate_em_quem_recua               e2v  vigia_bate_em_quem_recua        e2 = e2t + e2v
  v     vigia_recua_do_preparo_sob_pele       d1   dano_parry 5 -> 8 (campo da base V2C: exige G1-G9 antes de adotar)
  e combinacoes (a_c_e2v_v, a_c_e2_v, ...). Etapa extra "mecanismo": o que acontece nos confrontos que as propostas
  miram (contagens por partida).

Sementes: SO as de calibracao (3101..3505). As de validacao (4101..4505) nao sao usadas em nada.

Etapas (saida em artifacts_combate_v21c/equilibrio_rodada1/):
  matriz      matriz 8x8 (100 partidas por par por semente e especie, lados trocados na metade), com o epsilon dos
              bots 0,05 (o de hoje) e 0,15, para cada variante. Mesmos nomes e sementes do diagnostico. Conferencias
              (falham alto): v21c = reproducao.json (eps 0,05) e epsilon.json (0,15); a = candidatos.json cand_a;
              a_c = candidatos.json cand_a_c; c: linha da muralha = atribuicao.json (alavanca d, gambits da irma).
  painel      forca contra o painel B (metodo do diagnostico e de run_educacao._painel_do_ovo), pet com epsilon 0,05;
              o painel tambem joga com as regras e os bots da variante. v21c confere com painel.json.
  gate        gate PROPOSTO A1-A6 em cada variante (le matriz.json e painel.json).
  colaterais  para uma variante (--variante) e para a v21c: S1 das sombrias (12 formas, metodo de
              run_bateria_sombria), E4 na escala (metodo de run_bateria_v21 com "escala") e a campanha na escala
              (metodo de calibrar_escala.medir, fatores de ConfigEscala). A v21c confere a campanha com
              experiments/configs/escala/calibracao.json.
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
from dataclasses import asdict, replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import diagnosticar_arquetipos as diag  # noqa: E402
import run_bateria_v21 as rb  # noqa: E402
from digilab.campanha import npc  # noqa: E402
from digilab.combate_v2.v21 import bots  # noqa: E402
from digilab.combate_v2.v21.bots import ADOLESCENTES, CRIANCAS, FORMAS, SOMBRIOS, gambits_adulto  # noqa: E402
from digilab.combate_v2.v21.catalogo import LINHA_DA_FORMA, Forma, carater_canonico, perfil  # noqa: E402
from digilab.combate_v2.v21.partida import Lutador, jogar  # noqa: E402
from digilab.combate_v2.v21.regras import Acao, Regras, estado_inicial, resolver  # noqa: E402
from digilab.config import (CONFIG_BATERIA_V21, CONFIG_CAMPANHA, CONFIG_CATALOGO, CONFIG_COMBATE_V2,  # noqa: E402
                            CONFIG_COMBATE_V2C, CONFIG_COMBATE_V21C, CONFIG_ESCALA_LIGADA, STATS_V21,
                            ConfigCombateV21D)
from digilab.metrics import equilibrio_simetrico, matriz_taxas, suporte  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402

RODADA = int(os.environ.get("EQ_RODADA", 1))
SAIDA = Path(os.environ.get("EQ_R1_SAIDA", RAIZ / "artifacts_combate_v21c" / f"equilibrio_rodada{RODADA}"))
N_POR_SEMENTE = int(os.environ.get("EQ_R1_N", 100))
M_PAINEL = int(os.environ.get("EQ_R1_M", 50))
N_CAMPANHA = int(os.environ.get("EQ_R1_NC", 10))     # = calibrar_escala (-n 10)
DIAG = RAIZ / "artifacts_combate_v21c" / "diagnostico_arquetipos"
R1 = RAIZ / "artifacts_combate_v21c" / "equilibrio_rodada1"
CALIB_ESCALA = RAIZ / "experiments" / "configs" / "escala" / "calibracao.json"
E3_V4 = RAIZ / "artifacts_combate_v21c" / "calibracao" / "v4" / "uso_tecnicas.json"

VARIANTES = {
    "v21c": {},
    "a": {"preparo_sob_pele_oculto": True},
    "c": {"muralha_lista_espelho": True},
    "a_c": {"preparo_sob_pele_oculto": True, "muralha_lista_espelho": True},
}
DESCRICAO = {
    "v21c": "V21C de hoje (sem chave)",
    "a": "A: o preparo do pesado feito sob pele_dura nao aparece em oponente_preparando (todos os bots)",
    "c": "C: a muralha luta com a lista de gambits do espelho",
    "a_c": "A + C",
}
# rodada 2: propostas sobre A + C (docs/EQUILIBRIO_RODADA2.md)
_AC = VARIANTES["a_c"]
_R2 = {
    "d2": ({"investida_erra_contra_recuo": True}, "D2: a investida erra quando o alvo recua da distancia media"),
    "e1": ({"preparo_prende": True}, "E1: recuar nao afasta de quem prepara o pesado no mesmo turno (regra)"),
    "e2t": ({"tita_bate_em_quem_recua": True}, "E2 so no tita: golpe rapido de perto contra quem recua (lista)"),
    "e2v": ({"vigia_bate_em_quem_recua": True}, "E2 so no vigia: golpe rapido de perto contra quem recua (lista)"),
    "v": ({"vigia_recua_do_preparo_sob_pele": True}, "V: o vigia recua do preparo de quem usa pele (lista)"),
}
# D1 mexe na base V2C (campo dano_parry, 5 na validacao): variante de regras_base, nao chave da V21D
BASE_VARIANTES: dict = {}
_COMBOS_R2 = (("d2",), ("e1",), ("e2t",), ("e2v",), ("e2t", "e2v"), ("v",), ("e2t", "e2v", "v"), ("e2v", "v"),
              ("e2v", "v", "d2"), ("e1", "v"), ("e2v", "v", "d1"), ("e2v", "v", "d1", "d2"))
for _combo in _COMBOS_R2:
    _nome = "a_c_" + "_".join(_combo).replace("e2t_e2v", "e2")
    VARIANTES[_nome] = {**_AC, **{k: x for c in _combo if c != "d1" for k, x in _R2[c][0].items()}}
    DESCRICAO[_nome] = "A + C + " + " + ".join("D1: dano_parry 5 -> 8 (base V2C)" if c == "d1" else _R2[c][1]
                                               for c in _combo)
    if "d1" in _combo:
        BASE_VARIANTES[_nome] = {"dano_parry": 8.0}
RODADAS = {1: ("v21c", "a", "c", "a_c"),
           2: ("v21c", "a_c") + tuple(v for v in VARIANTES if v.startswith("a_c_"))}


def variantes() -> tuple:
    """As variantes da rodada em curso (EQ_RODADA)."""
    return RODADAS[RODADA]
EPSILONS = (0.05, 0.15)
# gate PROPOSTO (docs/DIAGNOSTICO_ARQUETIPOS.md, secao 7)
FAIXA = (0.40, 0.60)
SUPORTE_MIN = 6
EXTREMOS_MAX = {0.05: 7, 0.15: 4}
AMPLITUDE_MAX = 0.20
VITORIAS_MIN = 2


def _dump(o) -> str:
    return json.dumps(o, ensure_ascii=False, indent=2, sort_keys=True)


def _gravar(nome: str, obj: dict) -> None:
    SAIDA.mkdir(parents=True, exist_ok=True)
    (SAIDA / nome).write_text(_dump(obj), encoding="utf-8", newline="\n")
    print(f"  gravado {SAIDA / nome}", flush=True)


def _ler(caminho: Path) -> dict:
    return json.loads(caminho.read_text(encoding="utf-8"))


def _media(xs) -> float:
    xs = list(xs)
    if not xs:
        raise ValueError("media de lista vazia")
    return sum(xs) / len(xs)


# ------------------------------------------------------------------ regras por variante
_CACHE: dict = {}


def cfg_variante(v: str) -> dict:
    if v not in VARIANTES:
        raise ValueError(f"variante desconhecida: {v!r}")
    c = diag.config_validacao()
    return {**c, "regras_base": {**c["regras_base"], **BASE_VARIANTES.get(v, {})},
            "regras_v21": {**c["regras_v21"], **VARIANTES[v]}}


def regras(v: str) -> Regras:
    """Arena (bateria): regras da validacao V21C + chaves da variante. v21c monta a ConfigCombateV21C de sempre."""
    if ("arena", v) not in _CACHE:
        r = rb.regras_de(cfg_variante(v))
        if (v == "v21c") != (not isinstance(r.v21, ConfigCombateV21D)):
            raise RuntimeError(f"classe de config inesperada para {v}: {type(r.v21).__name__}")
        _CACHE[("arena", v)] = r
    return _CACHE[("arena", v)]


def regras_campanha(v: str) -> Regras:
    """Campanha: campanha.REGRAS_CAMPANHA (V2C + V21C) + chaves da variante."""
    if ("campanha", v) not in _CACHE:
        v21 = CONFIG_COMBATE_V21C if v == "v21c" else ConfigCombateV21D(**{**asdict(CONFIG_COMBATE_V21C), **VARIANTES[v]})
        _CACHE[("campanha", v)] = Regras(base=replace(CONFIG_COMBATE_V2C, **BASE_VARIANTES.get(v, {})), v21=v21)
    return _CACHE[("campanha", v)]


def lutador(forma: str, especie: str, v: str, epsilon: float | None = None, nome: str | None = None,
            escala=None) -> Lutador:
    """Bot canonico da forma sob as regras da variante (a lista da muralha vem de bots.gambits_adulto). Nome = o do
    bot canonico (as sementes das partidas derivam dele)."""
    base = bots.lutador_adulto(forma, especie, regras(v).v21, nome=nome, escala=escala)
    return base if epsilon is None else replace(base, epsilon=epsilon)


def meta(extra: dict | None = None) -> dict:
    return {"regras_v21c": diag.conferir_regras(), "config_regras": "experiments/configs/v21c/validacao.json",
            "rodada": RODADA,
            "variantes": {v: {"chaves": VARIANTES[v], "base": BASE_VARIANTES.get(v, {}), "descricao": DESCRICAO[v],
                              "hashes": rb.hashes(cfg_variante(v))} for v in variantes()},
            "sementes": diag.sementes_calibracao(), "especies": list(CONFIG_CATALOGO.especies_ativas),
            "epsilon_bots_canonico": CONFIG_COMBATE_V2.epsilon_bots,
            "ambiente": {"python": platform.python_version(), "plataforma": platform.platform()},
            "aviso": f"rodada {RODADA} do reequilibrio, so sementes de calibracao; chaves da ConfigCombateV21D, "
                     "desligadas por padrao"} | (extra or {})


# ------------------------------------------------------------------ matriz
def _rr(args):
    v, eps, esp, n = args
    r = regras(v)
    lut = {f: lutador(f, esp, v, epsilon=eps) for f in FORMAS}
    conf = []
    for i, fa in enumerate(FORMAS):
        for fb in FORMAS[i:]:
            conf += [(fa, fb, x) for x in diag.jogar_par(lut[fa], lut[fb], f"e1|{esp}", diag.sementes_calibracao(), n, r)]
    return v, eps, esp, conf


def resumo(conf) -> dict:
    res = diag.resumo_matriz(conf)
    tx = res["taxa"]
    res["vitorias_contra_as_outras_7"] = {f: sorted(o for o in FORMAS if o != f and tx[f][o] > 0.5) for f in FORMAS}
    return res


def _igual(a, b) -> bool:
    return json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def etapa_matriz(pool) -> dict:
    esp = list(CONFIG_CATALOGO.especies_ativas)
    tarefas = [(v, eps, e, N_POR_SEMENTE) for v in variantes() for eps in EPSILONS for e in esp]
    conf = collections.defaultdict(list)
    for v, eps, e, c in sorted(pool.map(_rr, tarefas), key=lambda x: (x[0], x[1], x[2])):
        conf[(v, eps)] += c
    saida = {v: {f"{eps:.2f}": resumo(conf[(v, eps)]) for eps in EPSILONS} for v in variantes()}
    conferencias = {}
    if N_POR_SEMENTE == diag.N_POR_SEMENTE == 100 and RODADA == 2:
        rep = _ler(DIAG / "reproducao.json")["matriz_calibracao_n100"]["taxa"]
        eps = _ler(DIAG / "epsilon.json")["por_epsilon"]["0.15"]["taxa"]
        r1 = _ler(R1 / "matriz.json")["por_variante"]
        conferencias = {
            "v21c_0.05_igual_reproducao.json": _igual(saida["v21c"]["0.05"]["taxa"], rep),
            "v21c_0.15_igual_epsilon.json": _igual(saida["v21c"]["0.15"]["taxa"], eps),
            "a_c_igual_rodada1_matriz.json_a_c": _igual(saida["a_c"], r1["a_c"]),
            "v21c_igual_rodada1_matriz.json_v21c": _igual(saida["v21c"], r1["v21c"]),
        }
        falhas = [k for k, ok in conferencias.items() if not ok]
        if falhas:
            raise RuntimeError(f"conferencia com a rodada 1 / o diagnostico falhou: {falhas}")
    elif N_POR_SEMENTE == diag.N_POR_SEMENTE == 100:
        rep = _ler(DIAG / "reproducao.json")["matriz_calibracao_n100"]["taxa"]
        eps = _ler(DIAG / "epsilon.json")["por_epsilon"]["0.15"]["taxa"]
        cand = _ler(DIAG / "candidatos.json")["por_candidato"]
        irma = _ler(DIAG / "atribuicao.json")["taxa_contra_cada_oponente"]["muralha"]["gambits_irma"]
        conferencias = {
            "v21c_0.05_igual_reproducao.json": _igual(saida["v21c"]["0.05"]["taxa"], rep),
            "v21c_0.15_igual_epsilon.json": _igual(saida["v21c"]["0.15"]["taxa"], eps),
            "a_0.05_igual_candidatos.json_cand_a": _igual(saida["a"]["0.05"]["taxa"], cand["cand_a"]["taxa"]),
            "a_c_0.05_igual_candidatos.json_cand_a_c": _igual(saida["a_c"]["0.05"]["taxa"], cand["cand_a_c"]["taxa"]),
            "c_0.05_linha_da_muralha_igual_atribuicao.json_gambits_irma":
                _igual({o: saida["c"]["0.05"]["taxa"]["muralha"][o] for o in FORMAS if o != "muralha"}, irma),
        }
        falhas = [k for k, ok in conferencias.items() if not ok]
        if falhas:
            raise RuntimeError(f"conferencia com o diagnostico falhou: {falhas}")
    return {"meta": meta({"partidas_por_par_por_semente": N_POR_SEMENTE, "epsilons": list(EPSILONS),
                          "metodo": "round-robin das 8 formas, os dois lados da mesma especie, media das 4 especies; "
                                    "sementes derivar_semente('bateria-v21', 'e1|<especie>', semente, nome_a, nome_b, k) "
                                    "como run_bateria_v21.partidas_par; epsilon trocado nos 8 bots dos dois lados; "
                                    "forca = media contra as outras 7; vitorias = oponentes com taxa > 0,5"}),
            "conferencias_com_o_diagnostico": conferencias, "por_variante": saida}


# ------------------------------------------------------------------ painel B
def _painel(args):
    v, forma, esp_pet, m = args
    r = regras(v)
    pet = lutador(forma, esp_pet, v, nome=f"pet:{forma}@{esp_pet}")
    out = {}
    for s in diag.sementes_calibracao():
        for e in CONFIG_CATALOGO.especies_ativas:
            for f in FORMAS:
                bot = lutador(f, e, v, nome=f"painel:{f}@{e}")
                for k in range(m):
                    sp = derivar_semente(f"diag-arquetipos|B|{s}", bot.nome, k)     # como o diagnostico
                    out.setdefault(bot.nome, []).append(jogar(pet, bot, sp, r).pontos_a if k < m // 2
                                                        else 1.0 - jogar(bot, pet, sp, r).pontos_a)
    return v, forma, esp_pet, out


def etapa_painel(pool) -> dict:
    esp = list(CONFIG_CATALOGO.especies_ativas)
    res = {}
    for v, f, e, out in pool.map(_painel, [(v, f, e, M_PAINEL) for v in variantes() for f in FORMAS for e in esp]):
        res[(v, f, e)] = out
    saida = {}
    for v in variantes():
        tab = {}
        for f in FORMAS:
            por_esp = {e: _media(p for x in res[(v, f, e)].values() for p in x) for e in esp}
            tab[f] = {"taxa_painel": _media(por_esp.values()), "por_especie_do_pet": por_esp,
                      "contra_cada_forma_do_painel": {g: _media(p for e in esp for nome, x in res[(v, f, e)].items()
                                                                if nome.split(":")[1].split("@")[0] == g for p in x)
                                                      for g in FORMAS}}
        saida[v] = tab
    conferencia = None
    if M_PAINEL == diag.M_PAINEL == 50:
        gravado = _ler(DIAG / "painel.json")["por_epsilon_do_pet"]["0.05"]
        conferencia = _igual(saida["v21c"], gravado)
        if not conferencia:
            raise RuntimeError("painel da v21c difere de artifacts_combate_v21c/diagnostico_arquetipos/painel.json")
        if RODADA == 2 and not _igual(saida["a_c"], _ler(R1 / "painel.json")["por_variante"]["a_c"]):
            raise RuntimeError("painel da a_c difere de artifacts_combate_v21c/equilibrio_rodada1/painel.json")
    return {"meta": meta({"partidas_por_bot_por_semente": M_PAINEL, "epsilon_pet": CONFIG_COMBATE_V2.epsilon_bots,
                          "metodo": "pet = bot canonico da forma (epsilon 0,05, sem treino, condicao 1,0) sob as regras "
                                    "da variante; painel = os 32 bots canonicos (8 formas x 4 especies) sob as MESMAS "
                                    "regras e listas da variante; sementes derivar_semente('diag-arquetipos|B|<semente>', "
                                    "bot, k), lados trocados na metade (como diagnosticar_arquetipos.etapa_painel)"}),
            "v21c_igual_painel.json_eps_0.05": conferencia, "por_variante": saida}


# ------------------------------------------------------------------ gate proposto
def avaliar_gate(mat: dict, pain: dict) -> dict:
    m05, m15 = mat["0.05"], mat["0.15"]
    forca = m05["forca_media_contra_as_outras_7"]
    painel = {f: pain[f]["taxa_painel"] for f in FORMAS}
    fora = lambda d: {f: round(x, 3) for f, x in d.items() if not FAIXA[0] <= x <= FAIXA[1]}  # noqa: E731
    vit = {f: len(m05["vitorias_contra_as_outras_7"][f]) for f in FORMAS}
    itens = {
        "A1_forca_entre_formas": {"ok": not fora(forca), "dentro": 8 - len(fora(forca)), "fora": fora(forca)},
        "A2_forca_contra_painel": {"ok": not fora(painel), "dentro": 8 - len(fora(painel)), "fora": fora(painel)},
        "A3_suporte": {"ok": len(m05["suporte"]) >= SUPORTE_MIN, "suporte": m05["suporte"], "tamanho": len(m05["suporte"])},
        "A4_decisividade": {"ok": m05["pares_extremos_lt_0_1_ou_gt_0_9"] <= EXTREMOS_MAX[0.05]
                                  and m15["pares_extremos_lt_0_1_ou_gt_0_9"] <= EXTREMOS_MAX[0.15],
                            "extremos_eps_0.05": m05["pares_extremos_lt_0_1_ou_gt_0_9"],
                            "extremos_eps_0.15": m15["pares_extremos_lt_0_1_ou_gt_0_9"]},
        "A5_amplitude": {"ok": m05["amplitude_forca"] <= AMPLITUDE_MAX and m15["amplitude_forca"] <= AMPLITUDE_MAX,
                         "amplitude_eps_0.05": m05["amplitude_forca"], "amplitude_eps_0.15": m15["amplitude_forca"]},
        "A6_lugar_no_ciclo": {"ok": min(vit.values()) >= VITORIAS_MIN, "vitorias": vit,
                              "abaixo": {f: x for f, x in vit.items() if x < VITORIAS_MIN}},
    }
    # distancia ate o gate: quanto falta, em pontos de forca, para cada forma entrar na faixa (soma)
    falta = lambda d: sum(max(0.0, FAIXA[0] - x, x - FAIXA[1]) for x in d.values())  # noqa: E731
    return {"itens": itens, "passam": sorted(k for k, x in itens.items() if x["ok"]),
            "falham": sorted(k for k, x in itens.items() if not x["ok"]),
            "distancia_ate_a_faixa_forca": falta(forca), "distancia_ate_a_faixa_painel": falta(painel),
            "forca": forca, "painel": painel}


def etapa_gate() -> dict:
    mat = _ler(SAIDA / "matriz.json")["por_variante"]
    pain = _ler(SAIDA / "painel.json")["por_variante"]
    return {"meta": meta({"gate": {"faixa": FAIXA, "suporte_min": SUPORTE_MIN, "extremos_max": EXTREMOS_MAX,
                                   "amplitude_max": AMPLITUDE_MAX, "vitorias_min": VITORIAS_MIN,
                                   "fonte": "docs/DIAGNOSTICO_ARQUETIPOS.md, secao 7 (PROPOSTO); aqui nas sementes de "
                                            "CALIBRACAO, nao e o gate de validacao"}}),
            "por_variante": {v: avaliar_gate(mat[v], pain[v]) for v in variantes()}}


# ------------------------------------------------------------------ colaterais
TODAS = tuple(FORMAS) + tuple(SOMBRIOS)


def _s1(args):
    v, esp, n = args
    r = regras(v)
    lut = {f: lutador(f, esp, v) for f in TODAS}
    conf = []
    for i, fa in enumerate(TODAS):
        for fb in TODAS[i:]:
            conf += [(fa, fb, x) for _, _, x, _ in rb.partidas_par(lut[fa], lut[fb], f"sombria|{esp}",
                                                                 diag.sementes_calibracao(), n, r)]
    return v, esp, conf


def _e4(args):
    """E4 na escala (run_bateria_v21 com "escala": true): adulto sem treino x adolescente da linha sem treino ("e4")
    e com o treino maximo do estagio ("e4t")."""
    v, forma, esp = args
    r = regras(v)
    cb, esc = CONFIG_BATERIA_V21, CONFIG_ESCALA_LIGADA
    ad = lutador(forma, esp, v, escala=esc)
    tr = {k: esc.treino_e4 / len(STATS_V21) for k in STATS_V21}
    out = {}
    for rot, treino in (("e4", None), ("e4t", tr)):
        adol = bots.lutador_adolescente(LINHA_DA_FORMA[forma], esp, carater_canonico(forma), r.v21, escala=esc,
                                        treino=treino)
        out[rot] = [x for _, _, x, _ in rb.partidas_par(ad, adol, rot, diag.sementes_calibracao(),
                                                        cb.partidas_e4_por_semente, r)]
    return v, forma, esp, out


def _e3(args):
    """E3 de run_bateria_v21 (resposta declarada da tecnica, RESPOSTAS_V21C) sob as regras e listas da variante, numa
    especie; mesma ordem de laco e mesmas sementes da bateria."""
    v, tec, esp = args
    r = regras(v)
    usuarios = [f for f in FORMAS if rb.TECNICA_DA_LINHA[LINHA_DA_FORMA[f]] == tec]
    orig, resp = [], []
    por_usuario = {}
    for u in usuarios:
        n0 = len(orig)
        eu = lutador(u, esp, v)
        for op in FORMAS:
            base = lutador(op, esp, v, nome=f"{op}@{esp}#op")
            gl = bots.com_resposta(gambits_adulto(op, r.v21), tec, bots.RESPOSTAS_V21C)
            rsp = bots.lutador_adulto(op, esp, r.v21, gambits=gl, nome=f"{op}@{esp}#resp")
            orig += [x for _, _, x, _ in rb.partidas_par(eu, base, f"e3|{tec}", diag.sementes_calibracao(),
                                                         CONFIG_BATERIA_V21.partidas_e3_por_semente, r)]
            resp += [x for _, _, x, _ in rb.partidas_par(eu, rsp, f"e3|{tec}", diag.sementes_calibracao(),
                                                         CONFIG_BATERIA_V21.partidas_e3_por_semente, r)]
        por_usuario[u] = (orig[n0:], resp[n0:])
    return v, tec, esp, orig, resp, por_usuario


def _pet_campanha(est: str, nome: str, especie: str, nivel: int, v: str) -> Lutador:
    """calibrar_escala.lutador sob as regras de campanha da variante (lista da muralha por gambits_adulto)."""
    cfg = regras_campanha(v).v21
    tr = {k: nivel / len(STATS_V21) for k in STATS_V21} if nivel else None
    if est == "crianca":
        f, car, gl = Forma(especie, "crianca", nome), None, CRIANCAS[nome]
    elif est == "adolescente":
        f = Forma(especie, "adolescente", "sereno", nome)
        car, gl = carater_canonico(next(x for x in FORMAS if LINHA_DA_FORMA[x] == nome), cfg), ADOLESCENTES[nome]
    else:
        f, car, gl = Forma(especie, "adulto", "sereno", LINHA_DA_FORMA[nome], nome), carater_canonico(nome, cfg), \
            gambits_adulto(nome, cfg)
    p = perfil(f, None, car, 1.0, cfg, treino=tr, escala=CONFIG_ESCALA_LIGADA)
    return Lutador(f"{est}:{nome}+{nivel}@{especie}:escala", p, gl, CONFIG_COMBATE_V2.epsilon_bots)


def _campanha(args):
    v, tier, est, nome, nivel, n = args
    import calibrar_campanha
    r = regras_campanha(v)
    adv = npc(tier, escala=CONFIG_ESCALA_LIGADA)
    vals = []
    for e in CONFIG_CATALOGO.especies_ativas:
        a = _pet_campanha(est, nome, e, nivel, v)
        pts = []
        for s in calibrar_campanha.SEM_CALIBRACAO:
            for k in range(n):
                sp = derivar_semente("calib-campanha", s, a.nome, adv.nome, k)      # como calibrar_campanha.taxa
                pts.append(jogar(a, adv, sp, r).pontos_a if k < n // 2 else 1.0 - jogar(adv, a, sp, r).pontos_a)
        vals.append(sum(pts) / len(pts))
    return v, tier, est, nome, nivel, sum(vals) / len(vals)


def etapa_colaterais(pool, variante: str) -> dict:
    import calibrar_escala
    from calibrar_progressao import NOMES
    if calibrar_escala.META_SEM != 0.30 or calibrar_escala.META_COM != 0.80:
        raise RuntimeError("metas da campanha mudaram")
    esp = list(CONFIG_CATALOGO.especies_ativas)
    vs = ("v21c", variante) if variante != "v21c" else ("v21c",)
    out = {}
    # S1
    conf = collections.defaultdict(list)
    for v, e, c in sorted(pool.map(_s1, [(v, e, N_POR_SEMENTE) for v in vs for e in esp]), key=lambda x: (x[0], x[1])):
        conf[v] += c
    s1 = {}
    for v in vs:
        tx = matriz_taxas(conf[v])
        vence = {s: all(tx[s][x] > 0.5 for x in FORMAS) for s in SOMBRIOS}
        eq = equilibrio_simetrico(tx, list(TODAS), CONFIG_BATERIA_V21.iteracoes_fictitious_play)
        s1[v] = {"S1_ok": not any(vence.values()), "vence_todos_os_normais": vence,
                 "media_sombria_contra_normais": {s: _media(tx[s][x] for x in FORMAS) for s in SOMBRIOS},
                 "vitorias_contra_normais": {s: sorted(x for x in FORMAS if tx[s][x] > 0.5) for s in SOMBRIOS},
                 "sombria_x_normais": {s: {x: tx[s][x] for x in FORMAS} for s in SOMBRIOS},
                 "suporte_com_sombrias": suporte(eq["estrategia"], CONFIG_BATERIA_V21.peso_minimo_suporte)}
    out["S1"] = s1
    # E4 na escala
    e4 = collections.defaultdict(lambda: collections.defaultdict(list))
    for v, f, e, d in pool.map(_e4, [(v, f, e) for v in vs for f in FORMAS for e in esp]):
        for rot, pts in d.items():
            e4[v][(rot, f)] += pts
    out["E4_escala"] = {}
    for v in vs:
        t = {rot: {f: _media(e4[v][(rot, f)]) for f in FORMAS} for rot in ("e4", "e4t")}
        baixo = {f"{f} ({rot})": x for rot, d in t.items() for f, x in d.items() if x < CONFIG_ESCALA_LIGADA.taxa_min_e4}
        out["E4_escala"][v] = {"ok": not baixo, "taxa_sem_treino": t["e4"],
                               f"taxa_adolescente_+{CONFIG_ESCALA_LIGADA.treino_e4:g}": t["e4t"],
                               "abaixo_de_0.60": baixo, "menor": min(min(d.values()) for d in t.values())}
    # campanha na escala
    tarefas = []
    for tier in CONFIG_CAMPANHA.npcs:
        est, nv = calibrar_escala.nivel_tipico(tier)
        for nome in NOMES[est]:
            for nivel in (0, nv):
                tarefas += [(v, tier, est, nome, nivel, N_CAMPANHA) for v in vs]
    bruto = collections.defaultdict(dict)
    for v, tier, est, nome, nivel, x in pool.map(_campanha, tarefas):
        bruto[(v, tier)].setdefault(nome, {})[nivel] = round(x, 4)
    camp = {}
    for v in vs:
        camp[v] = {}
        for tier in CONFIG_CAMPANHA.npcs:
            est, nv = calibrar_escala.nivel_tipico(tier)
            pn = bruto[(v, tier)]
            sem, com = _media(x[0] for x in pn.values()), _media(x[nv] for x in pn.values())
            camp[v][tier] = {"fator": CONFIG_ESCALA_LIGADA.fator_npc[tier], "estagio": est, "nivel_tipico": nv,
                             "sem": round(sem, 4), "com": round(com, 4),
                             "passa": sem <= calibrar_escala.META_SEM and com >= calibrar_escala.META_COM,
                             "travados": sorted(k for k, x in pn.items() if x[nv] < 0.5), "por_forma": pn}
    conferencia = None
    if N_CAMPANHA == 10:
        gravado = _ler(CALIB_ESCALA)["medidas"]
        conferencia = all(gravado[t][str(d["fator"])]["sem"] == d["sem"] and gravado[t][str(d["fator"])]["com"] == d["com"]
                          for t, d in camp["v21c"].items())
        if not conferencia:
            raise RuntimeError("campanha da v21c difere de experiments/configs/escala/calibracao.json")
    out["campanha_escala"] = camp
    # E3 (so com a rodada 2): resposta declarada de cada tecnica sob a variante
    conferencia_e3 = None
    if RODADA == 2:
        tecs = sorted(bots.RESPOSTAS)
        res3 = {}
        for v, tec, e, o, rr, pu in pool.map(_e3, [(v, t, e) for v in vs for t in tecs for e in esp]):
            res3[(v, tec, e)] = (o, rr, pu)
        e3 = {}
        for v in vs:
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
        gravado = _ler(E3_V4)["resposta_declarada"]
        conferencia_e3 = all(gravado[t]["taxa_sem_resposta"] == e3["v21c"]["por_tecnica"][t]["taxa_sem_resposta"]
                             and gravado[t]["taxa_com_resposta"] == e3["v21c"]["por_tecnica"][t]["taxa_com_resposta"]
                             for t in tecs)
        if not conferencia_e3:
            raise RuntimeError("E3 da v21c difere de artifacts_combate_v21c/calibracao/v4/uso_tecnicas.json")
        out["E3"] = e3
    return {"meta": meta({"variante_medida": variante, "partidas_por_par_por_semente_S1": N_POR_SEMENTE,
                          "partidas_por_par_por_semente_E4": CONFIG_BATERIA_V21.partidas_e4_por_semente,
                          "partidas_por_par_por_semente_campanha": N_CAMPANHA,
                          "metodo": {"S1": "run_bateria_sombria: 12 formas (8 normais + 4 sombrias), mesma especie, "
                                           "rotulo 'sombria|<especie>'; S1 = nenhuma sombria vence (> 0,5) as 8 normais",
                                     "E4": "run_bateria_v21 com escala: adulto sem treino x adolescente da linha sem "
                                           "treino e com +22 (uniforme); ok = todos >= 0,60",
                                     "campanha": "calibrar_escala.medir com os fatores de ConfigEscala.fator_npc: pet "
                                                 "do estagio sugerido x NPC, sem treino e com o treino tipico; metas "
                                                 "sem <= 0,30 e com >= 0,80; regras = campanha.REGRAS_CAMPANHA + chaves"}}),
            "v21c_campanha_igual_calibracao_escala": conferencia,
            "v21c_E3_igual_calibracao_v4_uso_tecnicas": conferencia_e3, **out}


# ------------------------------------------------------------------ mecanismo (rodada 2)
PARES_MECANISMO = (("furioso", "sentinela"), ("furioso", "emboscador"), ("furioso", "duelista"), ("furioso", "tita"),
                   ("furioso", "vigia"), ("tita", "sentinela"), ("tita", "emboscador"), ("vigia", "sentinela"),
                   ("vigia", "emboscador"), ("vigia", "tita"))
VARIANTES_MECANISMO = ("a_c", "a_c_d2", "a_c_e2t", "a_c_e2v", "a_c_v", "a_c_e2v_v", "a_c_e2v_v_d1")


def _mec(args):
    """Refaz as partidas da matriz (mesmas sementes) turno a turno e conta, por lado (a = forma da linha, b = coluna):
    acoes, investida contra recuo (a condicao do D2), resposta do rival a investida, pesados que erraram por distancia,
    preparos interrompidos, dano recebido e quantas vezes as regras novas (E2, V) dispararam."""
    v, fa, fb, esp, n = args
    r = regras(v)
    a, b = lutador(fa, esp, v), lutador(fb, esp, v)
    # as mesmas partidas da matriz: o par e jogado na ordem de FORMAS (as sementes dependem da ordem dos nomes)
    x, y = (a, b) if FORMAS.index(fa) < FORMAS.index(fb) else (b, a)
    tot = collections.Counter()
    pontos = []
    for _, p, pts, _ in rb.partidas_par(x, y, f"e1|{esp}", diag.sementes_calibracao(), n, r):
        pontos.append(pts if x is a else 1.0 - pts)
        lut = (a, b) if p.nome_a == a.nome else (b, a)
        rot = ("a", "b") if lut[0] is a else ("b", "a")
        e = estado_inicial(lut[0].perfil, lut[1].perfil)
        for ev in p.log[1:-1]:
            ac, mot = (Acao(ev["a"]), Acao(ev["b"])), (ev["ma"], ev["mb"])
            e2, res = resolver(e, ac[0], ac[1], r)
            for i in (0, 1):
                q, j = rot[i], 1 - i
                tot[f"{q}|acao|{ac[i].value}"] += 1
                if ac[i] is Acao.INVESTIDA:
                    tot[f"{q}|rival_contra_a_investida|{ac[j].value}"] += 1
                if res.pesado_errou[i]:
                    tot[f"{q}|pesado_errou_por_distancia"] += 1
                if res.interrompido[i]:
                    tot[f"{q}|preparo_interrompido"] += 1
                tot[f"{q}|dano_recebido"] += res.dano_recebido[i]
                if isinstance(mot[i], int) and mot[i] < len(lut[i].gambits.regras):
                    rg = lut[i].gambits.regras[mot[i]]
                    if rg == bots.REGRA_BATE_EM_QUEM_RECUA:
                        tot[f"{q}|regra_nova_E2_golpe_em_quem_recua"] += 1
                    if rg == bots.REGRA_RECUA_DO_PREPARO_SOB_PELE:
                        tot[f"{q}|regra_nova_V_recua_do_preparo_sob_pele"] += 1
            e = e2
        fim = p.log[-1]
        if (e.lados[0].hp, e.lados[1].hp) != (fim["hp_a"], fim["hp_b"]):
            raise RuntimeError(f"refazer a partida {p.semente} nao deu o mesmo fim")
        tot["partidas"] += 1
        tot["turnos"] += p.turnos
        tot[f"fim|{p.motivo_fim}"] += 1
    return v, fa, fb, esp, dict(tot), pontos


def etapa_mecanismo(pool) -> dict:
    esp = list(CONFIG_CATALOGO.especies_ativas)
    vs = [v for v in VARIANTES_MECANISMO if v in variantes()]
    soma = collections.defaultdict(collections.Counter)
    pts = collections.defaultdict(list)
    for v, fa, fb, e, tot, pp in sorted(pool.map(_mec, [(v, fa, fb, e, N_POR_SEMENTE) for v in vs
                                                        for fa, fb in PARES_MECANISMO for e in esp]),
                                        key=lambda x: (x[0], x[1], x[2], x[3])):
        soma[(v, fa, fb)].update(tot)
        pts[(v, fa, fb)] += pp
    out = {}
    for (v, fa, fb), c in soma.items():
        n = c["partidas"]
        out.setdefault(v, {})[f"{fa}|{fb}"] = {
            "pontos_de_a": _media(pts[(v, fa, fb)]), "partidas": n,
            "por_partida": {k: x / n for k, x in sorted(c.items()) if k != "partidas"}}
    mat = _ler(SAIDA / "matriz.json")["por_variante"] if (SAIDA / "matriz.json").exists() else None
    if mat is not None:
        for v, d in out.items():
            for par, x in d.items():
                fa, fb = par.split("|")
                if abs(x["pontos_de_a"] - mat[v]["0.05"]["taxa"][fa][fb]) > 1e-12:
                    raise RuntimeError(f"mecanismo difere da matriz em {v} {par}")
    return {"meta": meta({"partidas_por_par_por_semente": N_POR_SEMENTE, "pares": [list(x) for x in PARES_MECANISMO],
                          "metodo": "as partidas da matriz (epsilon 0,05, mesmas sementes) refeitas turno a turno com "
                                    "regras.resolver; contagens medias por partida; a = forma da esquerda do par"}),
            "pontos_conferem_com_matriz.json": mat is not None, "por_variante": out}


# ------------------------------------------------------------------ main
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Reequilibrio dos arquetipos, rodadas 1 e 2 (so calibracao)")
    ap.add_argument("--etapa", default="todas", choices=("todas", "matriz", "painel", "gate", "colaterais", "mecanismo"))
    ap.add_argument("--rodada", type=int, default=1, choices=(1, 2))
    ap.add_argument("--variante", default="a_c", choices=tuple(VARIANTES))
    ap.add_argument("--processos", type=int, default=8)   # 18 derrubou o pool nesta maquina
    ap.add_argument("--rapido", type=Path, default=None, help="fumaca: N = 4, M = 4, campanha n = 2 (nao canonica)")
    a = ap.parse_args(argv)
    if a.processos > 8:
        raise ValueError("no maximo 8 processos nesta maquina")
    global RODADA, SAIDA
    if a.rodada != RODADA:
        # os processos do pool leem EQ_RODADA ao importar o modulo
        os.environ["EQ_RODADA"] = str(a.rodada)
        RODADA = a.rodada
        if "EQ_R1_SAIDA" not in os.environ:
            SAIDA = RAIZ / "artifacts_combate_v21c" / f"equilibrio_rodada{RODADA}"
    if a.variante not in variantes():
        raise ValueError(f"variante {a.variante!r} nao e da rodada {RODADA}: {variantes()}")
    if a.rapido is not None:
        global N_POR_SEMENTE, M_PAINEL, N_CAMPANHA
        os.environ.update(EQ_R1_N="4", EQ_R1_M="4", EQ_R1_NC="2", EQ_R1_SAIDA=str(a.rapido),
                          DIAG_ARQ_N="4", DIAG_ARQ_M="4")
        N_POR_SEMENTE, M_PAINEL, N_CAMPANHA, SAIDA = 4, 4, 2, a.rapido
    diag.conferir_regras()
    diag.sementes_calibracao()
    etapas = (("matriz", "painel", "gate") + (("mecanismo",) if RODADA == 2 else ())) if a.etapa == "todas" \
        else (a.etapa,)
    with ProcessPoolExecutor(max_workers=a.processos) as pool:
        for et in etapas:
            t0 = time.perf_counter()
            print(f"{et} ...", flush=True)
            if et == "matriz":
                _gravar("matriz.json", etapa_matriz(pool))
            elif et == "painel":
                _gravar("painel.json", etapa_painel(pool))
            elif et == "gate":
                _gravar("gate.json", etapa_gate())
            elif et == "mecanismo":
                _gravar("mecanismo.json", etapa_mecanismo(pool))
            else:
                _gravar(f"colaterais_{a.variante}.json", etapa_colaterais(pool, a.variante))
            print(f"  {et}: {time.perf_counter() - t0:.0f} s", flush=True)
    print({p.name: hashlib.sha256(p.read_bytes()).hexdigest()[:12] for p in sorted(SAIDA.glob("*.json"))})
    return 0


if __name__ == "__main__":
    sys.exit(main())
