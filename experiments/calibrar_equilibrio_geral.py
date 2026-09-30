"""Rodada de equilibrio geral do combate, FASE 1: as formas (docs/PLANO_EQUILIBRIO_GERAL.md, metas M-A1..M-A4; relatorio em
docs/EQUILIBRIO_GERAL.md). So sementes de CALIBRACAO (3101..3505); as de validacao ficam para a fase 4.

    python experiments/calibrar_equilibrio_geral.py --etapa todas            # ~25 min com 8 processos
    python experiments/calibrar_equilibrio_geral.py --etapa matriz|painel|metas|e3|s1|mecanismo

Variantes (regras da validacao V21C, experiments/configs/v21c/validacao.json, mais as chaves; parte sempre da V21D
validada, a_c_e2v_v, que e o combate dos pets v6-v8):
  v21d                         a V21D validada (experiments/configs/v21d/validacao.json)
  v21d_golpe12/15/20           base: custo do golpe rapido 10 -> 12, 15, 20        (campo da ConfigCombateV2C)
  v21d_parry8/12               base: dano do parry 5 -> 8, 12                      (campo da ConfigCombateV2C)
  v21d_sem_c3                  base: sem a fuga condicionada (C3)                  (campo da ConfigCombateV2C)
  v21d_duelista, v21d_tita, v21d_duelista_tita, v21d_duelista_tita_guardias
                               listas da ConfigCombateV21E, uma a uma e acumuladas
  v21e                         a escolhida (experiments/configs/v21e/calibracao.json): as cinco chaves da V21E
  v21e_espelho_disparo_08      v21e + passiva do espelho devolvendo 0,8 do disparo (o E3 do contra-golpe)

Etapas (saida em artifacts_equilibrio_geral/fase1/):
  matriz     8 formas, os dois lados da mesma especie, 100 partidas por par por semente e especie, lados trocados na
             metade, epsilon dos bots 0,05 e 0,15 (mesmos nomes e sementes do diagnostico e das rodadas 1 e 2). Conferencia
             que falha alto: v21d = equilibrio_rodada2/matriz.json (a_c_e2v_v).
  painel     pet = bot canonico da forma (epsilon 0,05) contra os 32 bots do painel B, 50 partidas por bot por semente, com
             as regras e as listas da variante dos dois lados. Conferencia: v21d = equilibrio_rodada2/painel.json.
  metas      M-A1..M-A4 em cada variante (le matriz.json e painel.json); relata tambem o gate antigo (suporte, extremos) e
             o epsilon 0,15.
  e3         resposta declarada de cada tecnica (RESPOSTAS_V21C, metodo do E3 da bateria), para v21d, v21e e
             v21e_espelho_disparo_08. Conferencia: v21d = equilibrio_rodada2/colaterais_a_c_e2v_v.json (E3).
  s1         as 4 sombrias contra as 8 normais (run_bateria_sombria), v21d e v21e. Conferencia: v21d = rodada 2 (S1).
  mecanismo  as partidas da matriz refeitas turno a turno nos confrontos que mudam (contagens por partida).
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

os.environ.setdefault("EQ_RODADA", "2")
import calibrar_equilibrio as ce  # noqa: E402
import diagnosticar_arquetipos as diag  # noqa: E402
import run_bateria_v21 as rb  # noqa: E402
from digilab.combate_v2.v21 import bots  # noqa: E402
from digilab.combate_v2.v21.bots import FORMAS, SOMBRIOS, gambits_adulto  # noqa: E402
from digilab.combate_v2.v21.catalogo import LINHA_DA_FORMA  # noqa: E402
from digilab.combate_v2.v21.partida import jogar  # noqa: E402
from digilab.combate_v2.v21.regras import Acao, Regras, estado_inicial, resolver  # noqa: E402
from digilab.config import (CONFIG_BATERIA_V21, CONFIG_CATALOGO, CONFIG_COMBATE_V2, ConfigCombateV21C,  # noqa: E402
                            ConfigCombateV21D, ConfigCombateV21E)
from digilab.metrics import equilibrio_simetrico, matriz_taxas, suporte  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402

CFG = RAIZ / "experiments" / "configs" / "v21e" / "calibracao.json"
CFG_V21D = RAIZ / "experiments" / "configs" / "v21d" / "validacao.json"
SAIDA = Path(os.environ.get("EG_SAIDA", RAIZ / "artifacts_equilibrio_geral" / "fase1"))
R2 = RAIZ / "artifacts_combate_v21c" / "equilibrio_rodada2"
N_POR_SEMENTE = int(os.environ.get("EG_N", 100))
M_PAINEL = int(os.environ.get("EG_M", 50))
EPSILONS = (0.05, 0.15)
TODAS = tuple(FORMAS) + tuple(SOMBRIOS)


def _ler(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def _dump(o) -> str:
    return json.dumps(o, ensure_ascii=False, indent=2, sort_keys=True)


def _media(xs) -> float:
    xs = list(xs)
    if not xs:
        raise ValueError("media de lista vazia")
    return sum(xs) / len(xs)


def _igual(a, b) -> bool:
    return json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def _gravar(nome: str, obj: dict) -> None:
    SAIDA.mkdir(parents=True, exist_ok=True)
    (SAIDA / nome).write_text(_dump(obj), encoding="utf-8", newline="\n")
    print(f"  gravado {SAIDA / nome}", flush=True)


# ------------------------------------------------------------------ o registro da variante e as variantes medidas
def config() -> dict:
    """experiments/configs/v21e/calibracao.json: as chaves da V21D tem de ser as da V21D validada, o config lista todas
    as chaves da V21D e da V21E, e as sementes sao as da validacao V21C (so as de calibracao sao usadas)."""
    c = _ler(CFG)
    d = _ler(CFG_V21D)["regras_v21"]
    if {k: c["regras_v21"][k] for k in d} != d:
        raise ValueError("as chaves da V21D do config v21e diferem das da V21D validada")
    novas = set(ConfigCombateV21E.__dataclass_fields__) - set(ConfigCombateV21C.__dataclass_fields__)
    if set(c["regras_v21"]) != novas:
        raise ValueError(f"o config precisa listar todas as chaves da V21D e da V21E: {sorted(novas)}")
    v = diag.config_validacao()
    if (c["sementes_calibracao"], c["sementes_validacao"]) != (v["sementes_calibracao"], v["sementes_validacao"]):
        raise ValueError("sementes do config diferem das da validacao V21C")
    if (c["partidas_por_par_por_semente"], c["partidas_por_bot_por_semente_painel"], tuple(c["epsilons"])) \
            != (100, 50, EPSILONS):
        raise ValueError("N, M ou epsilons do config diferem dos das rodadas 1 e 2")
    return c


def _chaves_v21d() -> dict:
    return dict(_ler(CFG_V21D)["regras_v21"])


def _chaves_v21e(**ligadas) -> dict:
    novas = sorted(set(ConfigCombateV21E.__dataclass_fields__) - set(ConfigCombateV21D.__dataclass_fields__))
    if set(ligadas) - set(novas):
        raise KeyError(f"chaves desconhecidas da V21E: {sorted(set(ligadas) - set(novas))}")
    return {k: bool(ligadas.get(k, False)) for k in novas}


def _variantes() -> dict:
    """nome -> (base V2C, regras_v21, descricao)."""
    v21d = _chaves_v21d()
    v21e = dict(config()["regras_v21"])
    out = {"v21d": ({}, v21d, "V21D validada (a_c_e2v_v): o combate dos pets v6-v8")}
    for nome, base, desc in (("v21d_golpe12", {"custo_golpe_rapido": 12}, "custo do golpe rapido 10 -> 12"),
                             ("v21d_golpe15", {"custo_golpe_rapido": 15}, "custo do golpe rapido 10 -> 15"),
                             ("v21d_golpe20", {"custo_golpe_rapido": 20}, "custo do golpe rapido 10 -> 20"),
                             ("v21d_parry8", {"dano_parry": 8.0}, "dano do parry 5 -> 8"),
                             ("v21d_parry12", {"dano_parry": 12.0}, "dano do parry 5 -> 12"),
                             ("v21d_sem_c3", {"fuga_condicionada": False}, "sem a fuga condicionada (C3)")):
        out[nome] = (base, v21d, f"V21D + base: {desc}")
    listas = (("v21d_duelista", {"duelista_defende_do_golpe": True}, "duelista defende do golpe"),
              ("v21d_tita", {"tita_defende_do_golpe": True}, "tita defende do golpe"),
              ("v21d_duelista_tita", {"duelista_defende_do_golpe": True, "tita_defende_do_golpe": True},
               "duelista e tita defendem do golpe"),
              ("v21d_duelista_tita_guardias", {"duelista_defende_do_golpe": True, "tita_defende_do_golpe": True,
                                               "espelho_sem_carregar": True, "muralha_sem_carregar": True},
               "duelista e tita defendem do golpe; espelho e muralha sem carregar"))
    for nome, lig, desc in listas:
        out[nome] = ({}, {**v21d, **_chaves_v21e(**lig)}, f"V21D + listas: {desc}")
    out["v21e"] = ({}, v21e, "V21E escolhida (experiments/configs/v21e/calibracao.json): as cinco chaves da V21E")
    out["v21e_espelho_disparo_08"] = ({}, {**v21e, "fracao_espelho_disparo": 0.8},
                                      "V21E + passiva do espelho: devolve 0,8 do disparo (era 1,0; o E3 do contra-golpe)")
    return out


VARIANTES = _variantes()


def cfg_variante(v: str) -> dict:
    base, v21, _ = VARIANTES[v]
    c = diag.config_validacao()
    return {**c, "regras_base": {**c["regras_base"], **base}, "regras_v21": {**c["regras_v21"], **v21}}


_CACHE: dict = {}


def regras(v: str) -> Regras:
    if v not in _CACHE:
        r = rb.regras_de(cfg_variante(v))
        esperado = ConfigCombateV21D if v.startswith("v21d") and not any(
            VARIANTES[v][1].get(k) for k in bots.CHAVES_LISTAS_V21E) else ConfigCombateV21E
        if type(r.v21) is not esperado:
            raise RuntimeError(f"classe de config inesperada para {v}: {type(r.v21).__name__}")
        _CACHE[v] = r
    return _CACHE[v]


def lutador(forma: str, especie: str, v: str, epsilon: float | None = None, nome: str | None = None):
    """Bot canonico da forma sob as regras da variante (as listas vem de bots.gambits_adulto); nome = o do bot canonico
    (as sementes das partidas derivam dele)."""
    from dataclasses import replace
    b = bots.lutador_adulto(forma, especie, regras(v).v21, nome=nome)
    return b if epsilon is None else replace(b, epsilon=epsilon)


def sementes() -> list[int]:
    s = diag.sementes_calibracao()
    if s != list(config()["sementes_calibracao"]):
        raise ValueError("sementes de calibracao divergem")
    return s


def meta(extra: dict | None = None) -> dict:
    return {"fase": 1, "config": str(CFG.relative_to(RAIZ)).replace("\\", "/"),
            "config_sha256": hashlib.sha256(CFG.read_bytes()).hexdigest(),
            "regras_v21c": diag.conferir_regras(),
            "variantes": {v: {"base": b, "regras_v21": k, "descricao": d, "hashes": rb.hashes(cfg_variante(v))}
                          for v, (b, k, d) in VARIANTES.items()},
            "sementes": sementes(), "especies": list(CONFIG_CATALOGO.especies_ativas),
            "epsilon_bots_canonico": CONFIG_COMBATE_V2.epsilon_bots,
            "ambiente": {"python": platform.python_version(), "plataforma": platform.platform()},
            "aviso": "fase 1 da rodada de equilibrio geral: so sementes de calibracao; chaves da ConfigCombateV21E "
                     "desligadas por padrao"} | (extra or {})


# ------------------------------------------------------------------ matriz
def _rr(args):
    v, eps, esp, n = args
    r = regras(v)
    lut = {f: lutador(f, esp, v, epsilon=eps) for f in FORMAS}
    conf, lim = [], 0
    for i, fa in enumerate(FORMAS):
        for fb in FORMAS[i:]:
            for _, p, x, _ in rb.partidas_par(lut[fa], lut[fb], f"e1|{esp}", sementes(), n, r):
                conf.append((fa, fb, x))
                lim += p.motivo_fim == "limite"
    return v, eps, esp, conf, lim


def etapa_matriz(pool) -> dict:
    esp = list(CONFIG_CATALOGO.especies_ativas)
    conf, lim = collections.defaultdict(list), collections.Counter()
    for v, eps, e, c, nl in sorted(pool.map(_rr, [(v, eps, e, N_POR_SEMENTE) for v in VARIANTES for eps in EPSILONS
                                                  for e in esp]), key=lambda x: (x[0], x[1], x[2])):
        conf[(v, eps)] += c
        lim[(v, eps)] += nl
    saida = {}
    for v in VARIANTES:
        saida[v] = {}
        for eps in EPSILONS:
            res = ce.resumo(conf[(v, eps)])
            saida[v][f"{eps:.2f}"] = {**res, "fracao_no_limite_de_turnos": lim[(v, eps)] / len(conf[(v, eps)])}
    conferencia = None
    if N_POR_SEMENTE == 100:
        gravado = _ler(R2 / "matriz.json")["por_variante"]["a_c_e2v_v"]
        sem_limite = {e: {k: x for k, x in d.items() if k != "fracao_no_limite_de_turnos"} for e, d in saida["v21d"].items()}
        conferencia = _igual(sem_limite, gravado)
        if not conferencia:
            raise RuntimeError("matriz da v21d difere de artifacts_combate_v21c/equilibrio_rodada2/matriz.json (a_c_e2v_v)")
    return {"meta": meta({"partidas_por_par_por_semente": N_POR_SEMENTE, "epsilons": list(EPSILONS),
                          "metodo": "round-robin das 8 formas, os dois lados da mesma especie, media das 4 especies; "
                                    "sementes derivar_semente('bateria-v21', 'e1|<especie>', semente, nome_a, nome_b, k) "
                                    "(run_bateria_v21.partidas_par); epsilon trocado nos 8 bots dos dois lados; limite "
                                    "de turnos pela fracao de vida (a regra do Python); forca = media contra as outras 7; "
                                    "vitorias = oponentes com taxa > 0,5"}),
            "v21d_igual_equilibrio_rodada2_a_c_e2v_v": conferencia, "por_variante": saida}


# ------------------------------------------------------------------ painel B
def _painel(args):
    v, forma, esp_pet, m = args
    r = regras(v)
    pet = lutador(forma, esp_pet, v, nome=f"pet:{forma}@{esp_pet}")
    out = {}
    for s in sementes():
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
    for v, f, e, out in pool.map(_painel, [(v, f, e, M_PAINEL) for v in VARIANTES for f in FORMAS for e in esp]):
        res[(v, f, e)] = out
    saida = {}
    for v in VARIANTES:
        tab = {}
        for f in FORMAS:
            por_esp = {e: _media(p for x in res[(v, f, e)].values() for p in x) for e in esp}
            tab[f] = {"taxa_painel": _media(por_esp.values()), "por_especie_do_pet": por_esp,
                      "contra_cada_forma_do_painel": {g: _media(p for e in esp for nome, x in res[(v, f, e)].items()
                                                                if nome.split(":")[1].split("@")[0] == g for p in x)
                                                      for g in FORMAS}}
        saida[v] = tab
    conferencia = None
    if M_PAINEL == 50:
        conferencia = _igual(saida["v21d"], _ler(R2 / "painel.json")["por_variante"]["a_c_e2v_v"])
        if not conferencia:
            raise RuntimeError("painel da v21d difere de artifacts_combate_v21c/equilibrio_rodada2/painel.json")
    return {"meta": meta({"partidas_por_bot_por_semente": M_PAINEL, "epsilon_pet": CONFIG_COMBATE_V2.epsilon_bots,
                          "metodo": "pet = bot canonico da forma (epsilon 0,05, sem treino, condicao 1,0) sob as regras "
                                    "da variante; painel = os 32 bots canonicos (8 formas x 4 especies) sob as MESMAS "
                                    "regras e listas; sementes derivar_semente('diag-arquetipos|B|<semente>', bot, k), "
                                    "lados trocados na metade (diagnosticar_arquetipos.etapa_painel)"}),
            "v21d_igual_equilibrio_rodada2_a_c_e2v_v": conferencia, "por_variante": saida}


# ------------------------------------------------------------------ metas M-A1..M-A4
def avaliar_metas(mat: dict, pain: dict, c: dict) -> dict:
    mt = c["metas"]
    lo, hi = mt["M_A1_faixa_forca"]
    plo, phi = mt["M_A2_faixa_painel"]
    m05, m15 = mat["0.05"], mat["0.15"]
    forca = m05["forca_media_contra_as_outras_7"]
    painel = {f: pain[f]["taxa_painel"] for f in FORMAS}
    vit = {f: len(m05["vitorias_contra_as_outras_7"][f]) for f in FORMAS}
    fora = lambda d, a, b: {f: x for f, x in d.items() if not a <= x <= b}  # noqa: E731
    itens = {
        "M_A1_forca_contra_as_outras_7": {"ok": not fora(forca, lo, hi), "fora": fora(forca, lo, hi), "forca": forca,
                                          "margem_ate_a_borda": min(min(x - lo, hi - x) for x in forca.values())},
        "M_A2_forca_contra_o_painel": {"ok": not fora(painel, plo, phi), "fora": fora(painel, plo, phi), "painel": painel,
                                       "margem_ate_a_borda": min(min(x - plo, phi - x) for x in painel.values())},
        "M_A3_amplitude": {"ok": m05["amplitude_forca"] <= mt["M_A3_amplitude_max"],
                           "amplitude": m05["amplitude_forca"],
                           "mais_forte": max(forca, key=forca.get), "mais_fraca": min(forca, key=forca.get)},
        "M_A4_lugar_no_ciclo": {"ok": min(vit.values()) >= mt["M_A4_vitorias_min"], "vitorias": vit,
                                "vence": m05["vitorias_contra_as_outras_7"],
                                "abaixo": {f: x for f, x in vit.items() if x < mt["M_A4_vitorias_min"]}},
    }
    informativo = {
        "suporte_eps_0.05": m05["suporte"], "suporte_eps_0.15": m15["suporte"],
        "pares_extremos_eps_0.05": m05["pares_extremos_lt_0_1_ou_gt_0_9"],
        "pares_extremos_eps_0.15": m15["pares_extremos_lt_0_1_ou_gt_0_9"],
        "forca_eps_0.15": m15["forca_media_contra_as_outras_7"], "amplitude_eps_0.15": m15["amplitude_forca"],
        "fracao_no_limite_de_turnos_eps_0.05": m05["fracao_no_limite_de_turnos"],
        "dominantes": m05["dominantes"],
    }
    return {"itens": itens, "passam": sorted(k for k, x in itens.items() if x["ok"]),
            "falham": sorted(k for k, x in itens.items() if not x["ok"]), "informativo_nao_e_meta": informativo}


def etapa_metas() -> dict:
    c = config()
    mat = _ler(SAIDA / "matriz.json")["por_variante"]
    pain = _ler(SAIDA / "painel.json")["por_variante"]
    return {"meta": meta({"metas": c["metas"], "fonte": "docs/PLANO_EQUILIBRIO_GERAL.md, secao 2 (M-A1..M-A4); aqui "
                                                        "nas sementes de CALIBRACAO (a validacao e a fase 4)"}),
            "por_variante": {v: avaliar_metas(mat[v], pain[v], c) for v in VARIANTES}}


# ------------------------------------------------------------------ E3 (resposta declarada)
VARIANTES_E3 = ("v21d", "v21e", "v21e_espelho_disparo_08")


def _e3(args):
    v, tec, esp = args
    r = regras(v)
    usuarios = [f for f in FORMAS if rb.TECNICA_DA_LINHA[LINHA_DA_FORMA[f]] == tec]
    orig, resp, por_usuario = [], [], {}
    for u in usuarios:
        n0 = len(orig)
        eu = lutador(u, esp, v)
        for op in FORMAS:
            base = lutador(op, esp, v, nome=f"{op}@{esp}#op")
            gl = bots.com_resposta(gambits_adulto(op, r.v21), tec, bots.RESPOSTAS_V21C)
            rsp = bots.lutador_adulto(op, esp, r.v21, gambits=gl, nome=f"{op}@{esp}#resp")
            orig += [x for _, _, x, _ in rb.partidas_par(eu, base, f"e3|{tec}", sementes(),
                                                         CONFIG_BATERIA_V21.partidas_e3_por_semente, r)]
            resp += [x for _, _, x, _ in rb.partidas_par(eu, rsp, f"e3|{tec}", sementes(),
                                                         CONFIG_BATERIA_V21.partidas_e3_por_semente, r)]
        por_usuario[u] = (orig[n0:], resp[n0:])
    return v, tec, esp, orig, resp, por_usuario


def etapa_e3(pool) -> dict:
    esp = list(CONFIG_CATALOGO.especies_ativas)
    tecs = sorted(bots.RESPOSTAS)
    res = {}
    for v, tec, e, o, rr, pu in pool.map(_e3, [(v, t, e) for v in VARIANTES_E3 for t in tecs for e in esp]):
        res[(v, tec, e)] = (o, rr, pu)
    e3 = {}
    for v in VARIANTES_E3:
        e3[v] = {}
        for tec in tecs:
            o = [x for e in esp for x in res[(v, tec, e)][0]]
            rr = [x for e in esp for x in res[(v, tec, e)][1]]
            e3[v][tec] = {"taxa_sem_resposta": sum(o) / len(o), "taxa_com_resposta": sum(rr) / len(rr),
                          "reducao": sum(o) / len(o) - sum(rr) / len(rr),
                          "usuarios": [f for f in FORMAS if rb.TECNICA_DA_LINHA[LINHA_DA_FORMA[f]] == tec],
                          "por_usuario": {u: {"taxa_sem_resposta": _media(x for e in esp for x in res[(v, tec, e)][2][u][0]),
                                              "taxa_com_resposta": _media(x for e in esp for x in res[(v, tec, e)][2][u][1])}
                                          for u in res[(v, tec, esp[0])][2]}}
        e3[v] = {"ok": all(x["reducao"] > 0.0 for x in e3[v].values()), "por_tecnica": e3[v]}
    conferencia = _igual(e3["v21d"], _ler(R2 / "colaterais_a_c_e2v_v.json")["E3"]["a_c_e2v_v"])
    if not conferencia:
        raise RuntimeError("E3 da v21d difere de equilibrio_rodada2/colaterais_a_c_e2v_v.json")
    return {"meta": meta({"partidas_por_par_por_semente": CONFIG_BATERIA_V21.partidas_e3_por_semente,
                          "metodo": "E3 de run_bateria_v21: o usuario da tecnica contra as 8 formas, sem e com a "
                                    "resposta declarada (RESPOSTAS_V21C) no topo da lista do oponente; ok = a resposta "
                                    "reduz a taxa media dos usuarios"}),
            "v21d_igual_equilibrio_rodada2": conferencia, "por_variante": e3}


# ------------------------------------------------------------------ S1 (sombrias)
VARIANTES_S1 = ("v21d", "v21e")


def _s1(args):
    v, esp, n = args
    r = regras(v)
    lut = {f: lutador(f, esp, v) for f in TODAS}
    conf = []
    for i, fa in enumerate(TODAS):
        for fb in TODAS[i:]:
            conf += [(fa, fb, x) for _, _, x, _ in rb.partidas_par(lut[fa], lut[fb], f"sombria|{esp}", sementes(), n, r)]
    return v, esp, conf


def etapa_s1(pool) -> dict:
    esp = list(CONFIG_CATALOGO.especies_ativas)
    conf = collections.defaultdict(list)
    for v, e, c in sorted(pool.map(_s1, [(v, e, N_POR_SEMENTE) for v in VARIANTES_S1 for e in esp]),
                          key=lambda x: (x[0], x[1])):
        conf[v] += c
    s1 = {}
    for v in VARIANTES_S1:
        tx = matriz_taxas(conf[v])
        vence = {s: all(tx[s][x] > 0.5 for x in FORMAS) for s in SOMBRIOS}
        eq = equilibrio_simetrico(tx, list(TODAS), CONFIG_BATERIA_V21.iteracoes_fictitious_play)
        s1[v] = {"S1_ok": not any(vence.values()), "vence_todos_os_normais": vence,
                 "media_sombria_contra_normais": {s: _media(tx[s][x] for x in FORMAS) for s in SOMBRIOS},
                 "vitorias_contra_normais": {s: sorted(x for x in FORMAS if tx[s][x] > 0.5) for s in SOMBRIOS},
                 "sombria_x_normais": {s: {x: tx[s][x] for x in FORMAS} for s in SOMBRIOS},
                 "suporte_com_sombrias": suporte(eq["estrategia"], CONFIG_BATERIA_V21.peso_minimo_suporte)}
    conferencia = None
    if N_POR_SEMENTE == 100:
        conferencia = _igual(s1["v21d"], _ler(R2 / "colaterais_a_c_e2v_v.json")["S1"]["a_c_e2v_v"])
        if not conferencia:
            raise RuntimeError("S1 da v21d difere de equilibrio_rodada2/colaterais_a_c_e2v_v.json")
    return {"meta": meta({"partidas_por_par_por_semente": N_POR_SEMENTE,
                          "metodo": "run_bateria_sombria: 12 formas (8 normais + 4 sombrias), mesma especie, rotulo "
                                    "'sombria|<especie>'; S1 = nenhuma sombria vence (> 0,5) as 8 normais"}),
            "v21d_igual_equilibrio_rodada2": conferencia, "por_variante": s1}


# ------------------------------------------------------------------ mecanismo
PARES_MECANISMO = (("furioso", "duelista"), ("furioso", "tita"), ("furioso", "espelho"), ("furioso", "muralha"),
                   ("furioso", "vigia"), ("furioso", "sentinela"), ("duelista", "espelho"), ("muralha", "vigia"),
                   ("tita", "vigia"), ("sentinela", "muralha"))
VARIANTES_MECANISMO = ("v21d", "v21e")


def _mec(args):
    """As partidas da matriz (mesmas sementes) refeitas turno a turno: acoes por distancia, golpes defendidos (parry) e o
    dano do parry, dano causado por acao, preparos interrompidos e as regras novas da V21E que dispararam."""
    v, fa, fb, esp, n = args
    r = regras(v)
    a, b = lutador(fa, esp, v), lutador(fb, esp, v)
    x, y = (a, b) if FORMAS.index(fa) < FORMAS.index(fb) else (b, a)
    novas = {bots.REGRA_DEFENDE_DO_GOLPE: "regra_nova_defende_do_golpe",
             bots.REGRA_CONTRA_GOLPE_NA_PELE: "regra_nova_contra_golpe_na_pele"}
    tot = collections.Counter()
    pontos = []
    for _, p, pts, _ in rb.partidas_par(x, y, f"e1|{esp}", sementes(), n, r):
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
                tot[f"{q}|dano_causado|{ac[i].value}"] += res.dano_recebido[j] if ac[i] is not Acao.DEFENDER else 0.0
                if ac[i] in (Acao.GOLPE_RAPIDO, Acao.FINTAR) and ac[j] is Acao.DEFENDER and e.distancia.value == 0:
                    tot[f"{q}|golpe_defendido_pelo_rival"] += 1
                    tot[f"{q}|dano_de_parry_recebido"] += r.base.dano_parry
                if res.interrompido[i]:
                    tot[f"{q}|preparo_interrompido"] += 1
                if res.pesado_errou[i]:
                    tot[f"{q}|pesado_errou_por_distancia"] += 1
                tot[f"{q}|dano_recebido"] += res.dano_recebido[i]
                if isinstance(mot[i], int) and mot[i] < len(lut[i].gambits.regras):
                    rg = lut[i].gambits.regras[mot[i]]
                    if rg in novas:
                        tot[f"{q}|{novas[rg]}"] += 1
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
    soma = collections.defaultdict(collections.Counter)
    pts = collections.defaultdict(list)
    for v, fa, fb, e, tot, pp in sorted(pool.map(_mec, [(v, fa, fb, e, N_POR_SEMENTE) for v in VARIANTES_MECANISMO
                                                        for fa, fb in PARES_MECANISMO for e in esp]),
                                        key=lambda x: (x[0], x[1], x[2], x[3])):
        soma[(v, fa, fb)].update(tot)
        pts[(v, fa, fb)] += pp
    out = {}
    for (v, fa, fb), c in soma.items():
        n = c["partidas"]
        out.setdefault(v, {})[f"{fa}|{fb}"] = {"pontos_de_a": _media(pts[(v, fa, fb)]), "partidas": n,
                                               "por_partida": {k: x / n for k, x in sorted(c.items()) if k != "partidas"}}
    mat = _ler(SAIDA / "matriz.json")["por_variante"] if (SAIDA / "matriz.json").exists() else None
    if mat is not None:
        for v, d in out.items():
            for par, x in d.items():
                fa, fb = par.split("|")
                if abs(x["pontos_de_a"] - mat[v]["0.05"]["taxa"][fa][fb]) > 1e-12:
                    raise RuntimeError(f"mecanismo difere da matriz em {v} {par}")
    return {"meta": meta({"partidas_por_par_por_semente": N_POR_SEMENTE, "pares": [list(x) for x in PARES_MECANISMO],
                          "metodo": "as partidas da matriz (epsilon 0,05, mesmas sementes) refeitas turno a turno; "
                                    "contagens medias por partida; a = forma da esquerda do par"}),
            "pontos_conferem_com_matriz.json": mat is not None, "por_variante": out}


# ------------------------------------------------------------------ main
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Equilibrio geral, fase 1: as formas (so calibracao)")
    ap.add_argument("--etapa", default="todas", choices=("todas", "matriz", "painel", "metas", "e3", "s1", "mecanismo"))
    ap.add_argument("--processos", type=int, default=8)
    a = ap.parse_args(argv)
    if a.processos > 8:
        raise ValueError("no maximo 8 processos nesta maquina")
    config()
    diag.conferir_regras()
    etapas = ("matriz", "painel", "metas", "e3", "s1", "mecanismo") if a.etapa == "todas" else (a.etapa,)
    with ProcessPoolExecutor(max_workers=a.processos) as pool:
        for et in etapas:
            t0 = time.perf_counter()
            print(f"{et} ...", flush=True)
            if et == "matriz":
                _gravar("matriz.json", etapa_matriz(pool))
            elif et == "painel":
                _gravar("painel.json", etapa_painel(pool))
            elif et == "metas":
                _gravar("metas.json", etapa_metas())
            elif et == "e3":
                _gravar("e3.json", etapa_e3(pool))
            elif et == "s1":
                _gravar("s1.json", etapa_s1(pool))
            else:
                _gravar("mecanismo.json", etapa_mecanismo(pool))
            print(f"  {et}: {time.perf_counter() - t0:.0f} s", flush=True)
    print({p.name: hashlib.sha256(p.read_bytes()).hexdigest()[:12] for p in sorted(SAIDA.glob("*.json"))})
    return 0


if __name__ == "__main__":
    sys.exit(main())
