"""Diagnostico do desequilibrio entre as 8 formas adultas (arquetipos) do combate V21C. So leitura: nenhuma regra muda.

    python experiments/diagnosticar_arquetipos.py --etapa todas --processos 8
    python experiments/diagnosticar_arquetipos.py --etapa reproducao|mecanismo|atribuicao|epsilon|painel

Regras: as da validacao V21C (experiments/configs/v21c/validacao.json, montadas por run_bateria_v21.regras_de; o
config_sha256 tem de ser o gravado em artifacts_combate_v21c/validacao/gates.json). Sementes: SO as de calibracao
(sementes_calibracao do mesmo config, 3101..3505); as de validacao (4101..4505) nao sao usadas em nada.

Etapas (saida em artifacts_combate_v21c/diagnostico_arquetipos/):
  reproducao  (1) matriz 8x8 nas sementes de calibracao. Confere byte a byte a matriz de
              artifacts_combate_v21c/calibracao/v4 (mesmas regras, N = 40) e roda a de N = 100 que serve de base.
  mecanismo   (2) as mesmas partidas da matriz N = 100, instrumentadas turno a turno (um laco igual ao de
              partida.jogar; os pontos de cada partida sao conferidos contra a matriz da etapa 1). Por dupla ordenada:
              acoes, dano por tipo de acao, golpe pesado, guts, turnos, fim, disparos e dano da passiva e da tecnica.
  atribuicao  (3) forca de cada forma (media contra as outras 7) com UMA alavanca mudada por vez, so na forma medida
              (os 7 oponentes sao os canonicos). Mesmos nomes e sementes da matriz: numeros aleatorios comuns.
  epsilon     (4) a matriz com epsilon dos bots 0; 0,05 (o de hoje); 0,15; 0,30.
  painel      (5) forca de cada forma contra o painel B da pesquisa (8 formas x 4 especies), mesmo metodo de
              run_educacao._painel_do_ovo, com o bot canonico no lugar do pet.
"""

from __future__ import annotations

import argparse
import collections
import copy
import hashlib
import json
import os
import platform
import random
import statistics
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import run_bateria_v21 as rb  # noqa: E402
from digilab.combate_v2.v21.bots import ADULTOS, FORMAS, lutador_adulto  # noqa: E402
from digilab.combate_v2.v21.catalogo import LINHA_DA_FORMA, Forma, carater_canonico, perfil  # noqa: E402
from digilab.combate_v2.v21.gambits import CONDICAO_DO_VIGIA, GambitInvalido  # noqa: E402
from digilab.combate_v2.v21.partida import Lutador, jogar, sementes_de_rng  # noqa: E402
from digilab.combate_v2.v21.regras import (CORPO_A_CORPO, POSTURAS, TECNICAS, Acao, Distancia,  # noqa: E402
                                           estado_inicial, resolver, resultado)
from digilab.config import CONFIG_BATERIA_V21, CONFIG_CATALOGO  # noqa: E402
from digilab.metrics import equilibrio_simetrico, matriz_taxas, suporte  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402

CFG_VALIDACAO = RAIZ / "experiments" / "configs" / "v21c" / "validacao.json"
CFG_V4 = RAIZ / "experiments" / "configs" / "v21c" / "v4.json"
ART_VALIDACAO = RAIZ / "artifacts_combate_v21c" / "validacao"
ART_V4 = RAIZ / "artifacts_combate_v21c" / "calibracao" / "v4"
# --rapido (fumaca) troca N, M e a saida pelo ambiente, para os processos filhos verem o mesmo
SAIDA = Path(os.environ.get("DIAG_ARQ_SAIDA", RAIZ / "artifacts_combate_v21c" / "diagnostico_arquetipos"))
N_POR_SEMENTE = int(os.environ.get("DIAG_ARQ_N", 100))   # partidas por par por semente (= validacao: 500 por par por especie)
M_PAINEL = int(os.environ.get("DIAG_ARQ_M", 50))         # partidas por bot do painel por semente (= M_B_por_bot da V3)
EPSILONS = (0.0, 0.05, 0.15, 0.30)
IRMA = {"duelista": "furioso", "furioso": "duelista", "espelho": "muralha", "muralha": "espelho",
        "sentinela": "emboscador", "emboscador": "sentinela", "vigia": "tita", "tita": "vigia"}
ATAQUES = (Acao.GOLPE_RAPIDO, Acao.FINTAR, Acao.PESADO, Acao.INVESTIDA, Acao.DISPARO)
CATEGORIAS_DANO = tuple(a.value for a in ATAQUES) + ("reflexo_contra_golpe", "parry")
VARIANTES = {
    "sem_passiva": "(a) passiva desligada na forma medida (Perfil.passiva = None)",
    "sem_tecnica": "(b) tecnica da linha desligada (Perfil.tecnica = None: a acao fica ilegal e a regra que a pede "
                   "nunca dispara; a lista cai na regra seguinte)",
    "stats_sem_forma": "(c) stats sem o delta da forma adulta (catalogo com os modificadores da forma zerados; "
                       "especie, estagio, linha e carater canonico mantidos)",
    "stats_so_especie": "(c') stats so da especie e do estagio (sem ramo, linha, forma e carater)",
    "gambits_irma": "(d) lista de gambits da forma irma da mesma linha, mantendo a passiva",
    "passiva_irma": "(e) passiva da forma irma, mantendo a lista de gambits",
}


def _dump(o) -> str:
    return json.dumps(o, ensure_ascii=False, indent=2, sort_keys=True)


def _gravar(nome: str, obj: dict) -> None:
    SAIDA.mkdir(parents=True, exist_ok=True)
    (SAIDA / nome).write_text(_dump(obj), encoding="utf-8", newline="\n")
    print(f"  gravado {SAIDA / nome}", flush=True)


def _media(xs) -> float:
    xs = list(xs)
    if not xs:
        raise ValueError("media de lista vazia")
    return sum(xs) / len(xs)


# ------------------------------------------------------------------ regras e sementes
_CFG = None
_R = None


def config_validacao() -> dict:
    global _CFG
    if _CFG is None:
        _CFG = rb.carregar(CFG_VALIDACAO)
    return _CFG


def regras():
    """Mesma montagem da validacao V21C (run_bateria_v21.regras_de sobre validacao.json)."""
    global _R
    if _R is None:
        _R = rb.regras_de(config_validacao())
    return _R


def sementes_calibracao() -> list[int]:
    cfg = config_validacao()
    sem = list(cfg["sementes_calibracao"])
    if set(sem) & set(cfg["sementes_validacao"]):
        raise ValueError("sementes de calibracao e validacao se sobrepoem")
    if sem != [3101, 3202, 3303, 3404, 3505]:
        raise ValueError(f"sementes de calibracao inesperadas: {sem}")
    return sem


def conferir_regras() -> dict:
    """O diagnostico usa as regras da validacao: config_sha256 igual ao gravado. O regras_sha256 (fontes de v21/) e
    registrado; se diferir do gravado, a reproducao byte a byte da etapa 1 e que garante o mesmo comportamento."""
    h = rb.hashes(config_validacao())
    gravado = json.loads((ART_VALIDACAO / "gates.json").read_text(encoding="utf-8"))["hashes"]
    if h["config_sha256"] != gravado["config_sha256"]:
        raise RuntimeError(f"config das regras difere da validacao: {h['config_sha256']} != {gravado['config_sha256']}")
    return {"atual": h, "validacao_gravado": gravado,
            "fontes_iguais_a_validacao": h["regras_sha256"] == gravado["regras_sha256"]}


def meta(extra: dict | None = None) -> dict:
    return {"regras": conferir_regras(), "config_regras": str(CFG_VALIDACAO.relative_to(RAIZ)).replace("\\", "/"),
            "sementes": sementes_calibracao(), "especies": list(CONFIG_CATALOGO.especies_ativas),
            "epsilon_bots": regras().base.epsilon_bots,
            "ambiente": {"python": platform.python_version(), "plataforma": platform.platform()},
            "aviso": "diagnostico, so sementes de calibracao; nenhuma regra mudou"} | (extra or {})


# ------------------------------------------------------------------ lutadores (variantes montadas aqui)
@dataclass(frozen=True)
class LutadorDiag(Lutador):
    """Lutador para os contrafactuais. Igual ao Lutador, sem duas travas de construcao:
    - tecnica fora da linha na lista: a acao e ilegal (regras.eh_legal), entao a regra nunca dispara;
    - oponente_vai_preparar sem a passiva do vigia: o contexto so e dado com passiva 'vigia' (Lutador.decidir,
      herdado), entao a condicao nunca vale.
    A decisao e a resolucao sao as do pacote, sem mudanca."""

    def __post_init__(self) -> None:
        if not 0.0 <= self.epsilon <= 1.0:
            raise ValueError(f"epsilon fora de [0, 1]: {self.epsilon}")
        if self.gambits.estagio != self.perfil.estagio:
            raise GambitInvalido(f"{self.nome}: gambits de {self.gambits.estagio} num {self.perfil.estagio}")


def _catalogo_sem(forma: str, tudo: bool):
    cat = CONFIG_CATALOGO
    linha = LINHA_DA_FORMA[forma]
    ad = copy.deepcopy(cat.arquetipos_adulto)
    ad[linha]["formas"][forma]["stats"] = {}
    kw = {"arquetipos_adulto": ad}
    if tudo:
        adol = copy.deepcopy(cat.arquetipos_adolescente)
        adol[linha]["stats"] = {}
        cr = copy.deepcopy(cat.arquetipos_crianca)
        cr["sereno"] = {}
        kw |= {"arquetipos_adolescente": adol, "arquetipos_crianca": cr}
    return replace(cat, **kw)


def lutador(forma: str, especie: str, variante: str = "original", epsilon: float | None = None,
            nome: str | None = None) -> Lutador:
    """Bot canonico da forma (bots.lutador_adulto com as regras da validacao) ou uma variante. O NOME e o do bot
    canonico: as sementes das partidas derivam dele, entao o contrafactual joga as mesmas sementes da matriz."""
    r = regras()
    base = lutador_adulto(forma, especie, r.v21, nome=nome)
    if base.perfil.escala is not None:
        raise RuntimeError("escala ligada: o diagnostico e o da arena, sem escala")
    p, g = base.perfil, base.gambits
    eps = base.epsilon if epsilon is None else epsilon
    if variante == "original":
        return replace(base, epsilon=eps)
    f = Forma(especie, "adulto", "sereno", LINHA_DA_FORMA[forma], forma)
    if variante == "sem_passiva":
        p = replace(p, passiva=None)
    elif variante == "sem_tecnica":
        p = replace(p, tecnica=None)
    elif variante == "stats_sem_forma":
        p = perfil(f, None, carater_canonico(forma, r.v21), 1.0, r.v21, _catalogo_sem(forma, tudo=False))
    elif variante == "stats_so_especie":
        p = perfil(f, None, {}, 1.0, r.v21, _catalogo_sem(forma, tudo=True))
    elif variante == "gambits_irma":
        g = ADULTOS[IRMA[forma]]
    elif variante == "passiva_irma":
        p = replace(p, passiva=IRMA[forma])
    else:
        raise ValueError(f"variante desconhecida: {variante!r}")
    if (p.passiva, p.tecnica) != (base.perfil.passiva, base.perfil.tecnica) and variante.startswith("stats"):
        raise RuntimeError("variante de stats mudou passiva ou tecnica")
    return LutadorDiag(base.nome, p, g, eps)


def jogar_par(a: Lutador, b: Lutador, rotulo: str, sementes, n: int, r):
    """Pontos de `a` (lados trocados na metade), sementes iguais as de run_bateria_v21.partidas_par."""
    return [pts for _, _, pts, _ in rb.partidas_par(a, b, rotulo, sementes, n, r)]


# ------------------------------------------------------------------ 1. reproducao
def _rr_especie(args):
    esp, n, eps = args
    r = regras()
    lut = {f: lutador(f, esp, epsilon=eps) for f in FORMAS}
    conf = []
    for i, fa in enumerate(FORMAS):
        for fb in FORMAS[i:]:
            conf += [(fa, fb, x) for x in jogar_par(lut[fa], lut[fb], f"e1|{esp}", sementes_calibracao(), n, r)]
    return esp, conf


def _rr_oficial(args):
    """A funcao da bateria, sem mudar nada (para a conferencia byte a byte)."""
    esp, n = args
    r = regras()
    return esp, rb.round_robin_arquetipos([esp], sementes_calibracao(), n, r, r.v21)


def resumo_matriz(conf) -> dict:
    tx = matriz_taxas(conf)
    eq = equilibrio_simetrico(tx, list(FORMAS), CONFIG_BATERIA_V21.iteracoes_fictitious_play)
    pares = [(a, b) for i, a in enumerate(FORMAS) for b in FORMAS[i + 1:]]
    forca = {f: _media(tx[f][o] for o in FORMAS if o != f) for f in FORMAS}
    return {"taxa": tx, "forca_media_contra_as_outras_7": forca,
            "estrategia_equilibrio": eq["estrategia"],
            "suporte": suporte(eq["estrategia"], CONFIG_BATERIA_V21.peso_minimo_suporte),
            "dominantes": [x for x in FORMAS if all(tx[x][y] > 0.5 for y in FORMAS if y != x)],
            "pares_extremos_lt_0_1_ou_gt_0_9": sum(tx[a][b] < 0.1 or tx[a][b] > 0.9 for a, b in pares),
            "pares_acima_0_9_ou_abaixo_0_1_fracao": sum(tx[a][b] < 0.1 or tx[a][b] > 0.9 for a, b in pares) / len(pares),
            "distancia_media_de_0_5": _media(abs(tx[a][b] - 0.5) for a, b in pares),
            "amplitude_forca": max(forca.values()) - min(forca.values()),
            "n_partidas": len(conf)}


def etapa_reproducao(pool) -> dict:
    esp = list(CONFIG_CATALOGO.especies_ativas)
    # (a) byte a byte contra a calibracao v4 (mesmas regras que a validacao, N = 40, sementes de calibracao)
    cfg_v4 = rb.carregar(CFG_V4)
    if rb.hashes(cfg_v4)["config_sha256"] != json.loads((ART_V4 / "gates.json").read_text(encoding="utf-8"))["hashes"]["config_sha256"]:
        raise RuntimeError("config da v4 mudou")
    if {k: cfg_v4[k] for k in ("regras_base", "regras_v21")} != {k: config_validacao()[k] for k in ("regras_base", "regras_v21")}:
        raise RuntimeError("a v4 nao tem as regras da validacao")
    conf40 = []
    for _, c in sorted(pool.map(_rr_oficial, [(e, cfg_v4["partidas_por_par_por_semente"]) for e in esp])):
        conf40 += c
    tx40 = matriz_taxas(conf40)
    gravada = json.loads((ART_V4 / "matriz_arquetipos.json").read_text(encoding="utf-8"))
    if gravada["sementes"] != sementes_calibracao():
        raise RuntimeError("a v4 nao usou as sementes de calibracao")
    igual = json.dumps(tx40, sort_keys=True) == json.dumps(gravada["taxa"], sort_keys=True)
    if not igual:
        raise RuntimeError("a matriz reproduzida difere de artifacts_combate_v21c/calibracao/v4 (regras mudaram?)")
    # (b) a base do diagnostico: N = 100 nas sementes de calibracao, com o lutador deste script (variante original)
    conf = []
    for _, c in sorted(pool.map(_rr_especie, [(e, N_POR_SEMENTE, None) for e in esp])):
        conf += c
    base = resumo_matriz(conf)
    val = json.loads((ART_VALIDACAO / "matriz_arquetipos.json").read_text(encoding="utf-8"))["taxa"]
    forca_val = {f: _media(val[f][o] for o in FORMAS if o != f) for f in FORMAS}
    dif = {f"{a}|{b}": base["taxa"][a][b] - val[a][b] for a in FORMAS for b in FORMAS if a != b}
    return {"meta": meta({"partidas_por_par_por_semente": N_POR_SEMENTE}),
            "conferencia_v4": {"fonte": "artifacts_combate_v21c/calibracao/v4/matriz_arquetipos.json",
                               "partidas_por_par_por_semente": cfg_v4["partidas_por_par_por_semente"],
                               "taxa_identica_byte_a_byte": igual, "n_partidas": len(conf40)},
            "matriz_calibracao_n100": base,
            "comparacao_validacao": {"fonte": "artifacts_combate_v21c/validacao/matriz_arquetipos.json (so leitura)",
                                     "forca_validacao": forca_val,
                                     "forca_calibracao_menos_validacao": {f: base["forca_media_contra_as_outras_7"][f] - forca_val[f] for f in FORMAS},
                                     "maior_diferenca_absoluta_de_par": max(abs(x) for x in dif.values()),
                                     "par_da_maior_diferenca": max(dif, key=lambda k: abs(dif[k]))}}


# ------------------------------------------------------------------ 2. mecanismo (partidas instrumentadas)
def _novo_lado() -> dict:
    return {"partidas": 0, "pontos": 0.0, "turnos": 0, "decisoes": 0, "exploracao": 0, "guts_soma": 0.0,
            "hp_final_fracao_soma": 0.0, "fim": collections.Counter(), "acoes": collections.Counter(),
            "dano": collections.Counter(), "pesado": collections.Counter(), "passiva": collections.Counter(),
            "tecnica": collections.Counter()}


def _somar(a: dict, b: dict) -> None:
    for k, v in b.items():
        if isinstance(v, collections.Counter):
            a[k].update(v)
        else:
            a[k] += v


def _registrar_turno(e, esc, res, lut, lados, r) -> None:
    """Decompoe o dano do turno e conta os eventos de cada lado. O dano que o lado i causa e: o ataque dele, o reflexo
    do contra_golpe dele e o parry dele. O resto (resolver) e a regra do pacote; aqui so se le o resultado."""
    b, v = r.base, r.v21
    acoes = (esc[0][0], esc[1][0])
    d0 = e.distancia
    t_ms = getattr(b, "turno_morte_subita", 0)
    ms = b.mult_morte_subita if t_ms and e.turno + 1 >= t_ms else 1.0
    parry = getattr(b, "dano_parry", 0.0)
    pele = [acoes[i] is Acao.PELE_DURA or e.lados[i].pele > 0 for i in (0, 1)]
    golpe_acerta = [acoes[i] is Acao.GOLPE_RAPIDO or (acoes[i] is Acao.FINTAR and d0 is Distancia.PERTO) for i in (0, 1)]
    refl = [res.devolvido[i] * (v.mult_pele_dura if pele[1 - i] else 1.0) * ms for i in (0, 1)]
    parry_de = [parry * ms if (golpe_acerta[1 - i] and acoes[i] is Acao.DEFENDER) else 0.0 for i in (0, 1)]
    ataque = [res.dano_recebido[1 - i] - refl[i] - parry_de[i] for i in (0, 1)]
    for i in (0, 1):
        if acoes[i] not in ATAQUES and abs(ataque[i]) > 1e-9:
            raise RuntimeError(f"decomposicao do dano falhou: {acoes} {res}")
        if ataque[i] < -1e-9:
            raise RuntimeError(f"dano de ataque negativo: {acoes} {res}")
    for i in (0, 1):
        L, j = lados[i], 1 - i
        eu, p = e.lados[i], lut[i].perfil
        acao, motivo = esc[i]
        L["acoes"][acao.value] += 1
        if motivo != "pesado_automatico":
            L["decisoes"] += 1
            L["exploracao"] += motivo == "exploracao"
        L["guts_soma"] += eu.guts
        if acao in ATAQUES:
            L["dano"][acao.value] += ataque[i]
        L["dano"]["reflexo_contra_golpe"] += refl[i]
        L["dano"]["parry"] += parry_de[i]
        # golpe pesado
        if acao is Acao.PREPARAR_PESADO:
            L["pesado"]["tentativas"] += 1
            if res.interrompido[i]:
                L["pesado"]["interrompidos"] += 1
            elif pele[i] and acoes[j] in (Acao.GOLPE_RAPIDO, Acao.INVESTIDA, Acao.FINTAR):
                L["pesado"]["protegido_pela_pele"] += 1
        if acao is Acao.FINTAR:
            L["pesado"]["fintas"] += 1
        if acao is Acao.PESADO:
            L["pesado"]["executados"] += 1
            if res.pesado_errou[i]:
                L["pesado"]["errou_distancia"] += 1
            elif acoes[j] is Acao.ESQUIVAR:
                L["pesado"]["esquivados"] += 1
            elif acoes[j] in POSTURAS:
                L["pesado"]["defendidos"] += 1
                L["pesado"]["dano_defendido"] += ataque[i]
            else:
                L["pesado"]["acertos"] += 1
                L["pesado"]["dano_acertos"] += ataque[i]
        # passiva
        pas = p.passiva
        P = L["passiva"]
        if pas == "duelista" and acao is Acao.PESADO and not res.pesado_errou[i] and acoes[j] is Acao.ESQUIVAR:
            P["disparos"] += 1
            P["dano"] += ataque[i]
            P["guts_devolvido"] += b.custo_preparar_pesado
        elif pas == "furioso":
            if eu.fracao_hp < v.limiar_hp_furioso:
                P["turnos_abaixo_do_limiar"] += 1
                if acao in CORPO_A_CORPO and ataque[i] > 0.0:
                    P["disparos"] += 1
                    P["dano"] += ataque[i] * (1.0 - 1.0 / v.mult_furioso)
        elif pas == "espelho":
            if acao is Acao.CONTRA_GOLPE and d0 is not Distancia.PERTO:
                P["contra_golpe_fora_de_perto"] += 1
            if acao is Acao.CONTRA_GOLPE and acoes[j] is Acao.DISPARO:
                P["disparos"] += 1
                P["dano"] += refl[i]
        elif pas == "muralha" and acao is Acao.DEFENDER:
            P["disparos"] += 1
            P["guts_extra"] += v.guts_extra_muralha
        elif pas == "sentinela" and acao is Acao.RECUAR and eu.recarga == 0 and acoes[j] in (Acao.AVANCAR, Acao.INVESTIDA) \
                and not (acoes[j] is Acao.INVESTIDA and acao is Acao.DEFENDER):
            P["disparos"] += 1
        elif pas == "emboscador" and acao is Acao.DISPARO and not eu.disparou:
            P["disparos"] += 1
            P["dano"] += ataque[i] * (1.0 - 1.0 / v.mult_emboscador)
        elif pas == "vigia" and isinstance(motivo, int) and motivo < len(lut[i].gambits.regras) and \
                any(c.nome == CONDICAO_DO_VIGIA for c in lut[i].gambits.regras[motivo].condicoes):
            P["disparos"] += 1
            P["dano"] += ataque[i]
            P["interrompeu_preparo"] += res.interrompido[j]
        elif pas == "tita" and acao is Acao.PESADO and ataque[i] > 0.0:
            P["disparos"] += 1
            P["dano"] += ataque[i] * (1.0 - 1.0 / v.mult_tita)
        # tecnica
        tec = TECNICAS.get(p.tecnica or "")
        T = L["tecnica"]
        if tec is not None and acao is tec:
            T["usos"] += 1
        if tec is Acao.INVESTIDA and acao is Acao.INVESTIDA:
            T["dano"] += ataque[i]
            T["aparadas_pelo_defender"] += acoes[j] is Acao.DEFENDER
        elif tec is Acao.CONTRA_GOLPE:
            T["dano"] += refl[i]
        elif tec is Acao.MARCAR and res.marca_usada[i]:
            T["disparos_marcados"] += 1
            T["dano"] += ataque[i]
        elif tec is Acao.PELE_DURA and pele[i]:
            T["turnos_com_pele"] += 1
            T["dano_evitado"] += (ataque[j] + refl[j]) * (1.0 / v.mult_pele_dura - 1.0)


def jogar_instrumentado(a: Lutador, b: Lutador, semente: int, r):
    """O laco de partida.jogar (mesmas rngs, mesmas decisoes, mesma resolucao) com o registro por turno."""
    sa, sb = sementes_de_rng(semente)
    rngs = (random.Random(sa), random.Random(sb))
    lut = (a, b)
    e = estado_inicial(a.perfil, b.perfil)
    lados = (_novo_lado(), _novo_lado())
    while (fim := resultado(e, r)) is None:
        esc = [lut[i].decidir(e, i, rngs[i], lut[1 - i], r) for i in (0, 1)]
        e2, res = resolver(e, esc[0][0], esc[1][0], r)
        _registrar_turno(e, esc, res, lut, lados, r)
        e = e2
    pontos, motivo = fim
    t_ms = getattr(r.base, "turno_morte_subita", 0)
    tipo_fim = "limite" if motivo == "limite" else ("ko_morte_subita" if t_ms and e.turno >= t_ms else "ko")
    for i in (0, 1):
        L = lados[i]
        L["partidas"] = 1
        L["pontos"] = pontos if i == 0 else 1.0 - pontos
        L["turnos"] = e.turno
        L["fim"][tipo_fim] += 1
        L["hp_final_fracao_soma"] = max(0.0, e.lados[i].fracao_hp)
    return pontos, lados


def _mec_par(args):
    esp, fa, fb, n = args
    r = regras()
    a, b = lutador(fa, esp), lutador(fb, esp)
    acc = {(fa, fb): _novo_lado(), (fb, fa): _novo_lado()}
    pts_a = []
    for s in sementes_calibracao():
        for k in range(n):
            sp = derivar_semente("bateria-v21", f"e1|{esp}", s, a.nome, b.nome, k)
            if k < n // 2:
                pts, lados = jogar_instrumentado(a, b, sp, r)
                pts_a.append(pts)
                la, lb = lados
            else:
                pts, lados = jogar_instrumentado(b, a, sp, r)
                pts_a.append(1.0 - pts)
                lb, la = lados
            if fa != fb:
                _somar(acc[(fa, fb)], la)
                _somar(acc[(fb, fa)], lb)
    return esp, fa, fb, pts_a, ({} if fa == fb else acc)


def _normalizar(L: dict) -> dict:
    n = L["partidas"]
    tot_acoes = sum(L["acoes"].values())
    pes = L["pesado"]
    return {
        "partidas": n, "pontos": L["pontos"] / n, "turnos_medios": L["turnos"] / n,
        "fim": {k: L["fim"][k] / n for k in ("ko", "ko_morte_subita", "limite")},
        "acoes_fracao": {k: c / tot_acoes for k, c in sorted(L["acoes"].items())},
        "exploracao_fracao_das_decisoes": L["exploracao"] / L["decisoes"],
        "guts_medio": L["guts_soma"] / L["turnos"],
        "hp_final_fracao_media": L["hp_final_fracao_soma"] / n,
        "dano_causado_por_partida": {k: L["dano"][k] / n for k in CATEGORIAS_DANO},
        "dano_causado_total_por_partida": sum(L["dano"].values()) / n,
        "pesado_por_partida": {k: pes[k] / n for k in ("tentativas", "interrompidos", "protegido_pela_pele", "executados",
                                                        "acertos", "defendidos", "esquivados", "errou_distancia",
                                                        "fintas", "dano_acertos", "dano_defendido")},
        "passiva_por_partida": {k: c / n for k, c in sorted(L["passiva"].items())},
        "tecnica_por_partida": {k: c / n for k, c in sorted(L["tecnica"].items())},
    }


def etapa_mecanismo(pool, base_rep: dict) -> dict:
    esp = list(CONFIG_CATALOGO.especies_ativas)
    tarefas = [(e, fa, fb, N_POR_SEMENTE) for e in esp for i, fa in enumerate(FORMAS) for fb in FORMAS[i:]]
    acc = {(x, y): _novo_lado() for x in FORMAS for y in FORMAS if x != y}
    acc_esp = {(e, x, y): _novo_lado() for e in esp for x in FORMAS for y in FORMAS if x != y}
    conf = []
    for e, fa, fb, pts_a, parcial in pool.map(_mec_par, tarefas):
        conf += [(fa, fb, x) for x in pts_a]
        for k, L in parcial.items():
            _somar(acc[k], L)
            _somar(acc_esp[(e,) + k], L)
    tx = matriz_taxas(conf)
    if json.dumps(tx, sort_keys=True) != json.dumps(base_rep["matriz_calibracao_n100"]["taxa"], sort_keys=True):
        raise RuntimeError("o laco instrumentado nao reproduz a matriz da etapa 1")
    pares = {f"{x}|{y}": _normalizar(acc[(x, y)]) for x in FORMAS for y in FORMAS if x != y}
    por_especie = {f"{e}|{x}|{y}": {"pontos": acc_esp[(e, x, y)]["pontos"] / acc_esp[(e, x, y)]["partidas"]}
                   for e in esp for x in FORMAS for y in FORMAS if x != y}
    por_forma = {}
    for f in FORMAS:
        L = _novo_lado()
        for o in FORMAS:
            if o != f:
                _somar(L, acc[(f, o)])
        por_forma[f] = _normalizar(L)

    def linha_destaque(x, y):
        pr = pares[f"{x}|{y}"]
        op = pares[f"{y}|{x}"]
        return {"par": f"{x}|{y}", "pontos": pr["pontos"], "turnos": pr["turnos_medios"], "fim": pr["fim"],
                "dano_causado": pr["dano_causado_total_por_partida"], "dano_sofrido": op["dano_causado_total_por_partida"],
                "dano_causado_por_tipo": pr["dano_causado_por_partida"], "dano_sofrido_por_tipo": op["dano_causado_por_partida"],
                "pesado": pr["pesado_por_partida"], "pesado_do_oponente": op["pesado_por_partida"],
                "acoes": pr["acoes_fracao"], "acoes_do_oponente": op["acoes_fracao"],
                "guts_medio": pr["guts_medio"], "guts_medio_oponente": op["guts_medio"],
                "passiva": pr["passiva_por_partida"], "tecnica": pr["tecnica_por_partida"],
                "passiva_oponente": op["passiva_por_partida"], "tecnica_oponente": op["tecnica_por_partida"]}

    destaques = {
        "furioso_vence": [linha_destaque("furioso", y) for y in FORMAS if y != "furioso" and tx["furioso"][y] > 0.9],
        "furioso_perde": [linha_destaque("furioso", y) for y in FORMAS if y != "furioso" and tx["furioso"][y] < 0.5],
        "tita_perde": [linha_destaque("tita", y) for y in FORMAS if y != "tita" and tx["tita"][y] < 0.1],
        "vigia_perde": [linha_destaque("vigia", y) for y in FORMAS if y != "vigia" and tx["vigia"][y] < 0.1],
        "tita_e_vigia_nao_perdem": [linha_destaque(x, y) for x in ("tita", "vigia") for y in FORMAS
                                    if y != x and tx[x][y] >= 0.1],
    }
    return {"meta": meta({"partidas_por_par_por_semente": N_POR_SEMENTE,
                          "conferencia": "pontos de cada partida iguais aos da matriz N = 100 da etapa 1 (reproducao.json)",
                          "unidades": "tudo por partida do lado da LINHA do par (x|y = x contra y), agregado sobre as "
                                      "4 especies e as 5 sementes; acoes_fracao sobre todas as acoes do lado (inclui o "
                                      "pesado automatico); guts_medio no inicio de cada turno; fim: ko antes do turno "
                                      "da morte subita, ko na morte subita, limite de turnos",
                          "passiva": "disparos e dano gerado pela passiva: duelista = pesado contra esquiva (dano extra e "
                                     "guts devolvido); furioso = golpe corpo a corpo abaixo do limiar (dano = parte extra "
                                     "do multiplicador); espelho = contra_golpe contra disparo (dano refletido) e "
                                     "contra_golpe fora de perto; muralha = defender (guts extra); sentinela = recuo que "
                                     "vale contra avanco ou investida; emboscador = primeiro disparo (parte extra); vigia = "
                                     "regra oponente_vai_preparar (dano do golpe e preparos interrompidos); tita = pesado "
                                     "que causa dano (parte extra)",
                          "tecnica": "usos e dano: investida = dano da investida; contra_golpe = dano refletido; marcar = "
                                     "disparos marcados e dano deles; pele_dura = turnos com pele e dano evitado"}),
            "matriz_confere": True, "pares": pares, "pontos_por_especie": por_especie,
            "por_forma_contra_as_outras_7": por_forma, "destaques": destaques}


# ------------------------------------------------------------------ 3. atribuicao
def _forca_variante(args):
    variante, forma, esp, n = args
    r = regras()
    eu = lutador(forma, esp, variante)
    linha = {}
    for o in FORMAS:
        if o == forma:
            continue
        op = lutador(o, esp)
        if FORMAS.index(forma) < FORMAS.index(o):
            pts = jogar_par(eu, op, f"e1|{esp}", sementes_calibracao(), n, r)
        else:
            pts = [1.0 - x for x in jogar_par(op, eu, f"e1|{esp}", sementes_calibracao(), n, r)]
        linha[o] = pts
    return variante, forma, esp, linha


def _por_semente(pts: list, n: int) -> list:
    k = len(sementes_calibracao())
    if len(pts) != k * n:
        raise ValueError("tamanho inesperado")
    return [_media(pts[i * n:(i + 1) * n]) for i in range(k)]


def etapa_atribuicao(pool, base_rep: dict) -> dict:
    esp = list(CONFIG_CATALOGO.especies_ativas)
    tarefas = [(v, f, e, N_POR_SEMENTE) for v in ("original",) + tuple(VARIANTES) for f in FORMAS for e in esp]
    linhas = collections.defaultdict(dict)
    for v, f, e, linha in pool.map(_forca_variante, tarefas):
        linhas[(v, f)][e] = linha
    tx_base = base_rep["matriz_calibracao_n100"]["taxa"]

    def taxa_contra(v, f):
        return {o: _media(x for e in esp for x in linhas[(v, f)][e][o]) for o in FORMAS if o != f}

    def forca_por_semente(v, f):
        # media contra as 7 por semente (especies e oponentes juntos)
        k = len(sementes_calibracao())
        acum = [[] for _ in range(k)]
        for e in esp:
            for o, pts in linhas[(v, f)][e].items():
                for i, m in enumerate(_por_semente(pts, N_POR_SEMENTE)):
                    acum[i].append(m)
        return [_media(a) for a in acum]

    # conferencia: a variante original reproduz a linha da matriz da etapa 1
    for f in FORMAS:
        orig = taxa_contra("original", f)
        for o, t in orig.items():
            if t != tx_base[f][o]:
                raise RuntimeError(f"variante original de {f} x {o} nao reproduz a matriz: {t} != {tx_base[f][o]}")
    tabela, detalhe = {}, {}
    for f in FORMAS:
        fs0 = forca_por_semente("original", f)
        f0 = _media(taxa_contra("original", f).values())
        tabela[f] = {"original": f0}
        detalhe[f] = {"original": taxa_contra("original", f)}
        for v in VARIANTES:
            tc = taxa_contra(v, f)
            fv = _media(tc.values())
            difs = [a - b for a, b in zip(forca_por_semente(v, f), fs0)]
            # matriz com a linha/coluna da forma trocadas pela variante: equilibrio e suporte
            tx = copy.deepcopy(tx_base)
            for o, t in tc.items():
                tx[f][o], tx[o][f] = t, 1.0 - t
            eq = equilibrio_simetrico(tx, list(FORMAS), CONFIG_BATERIA_V21.iteracoes_fictitious_play)
            tabela[f][v] = {"forca": fv, "variacao": fv - f0,
                            "ep_entre_sementes": statistics.stdev(difs) / len(difs) ** 0.5,
                            "suporte_com_a_variante": suporte(eq["estrategia"], CONFIG_BATERIA_V21.peso_minimo_suporte)}
            detalhe[f][v] = tc
    return {"meta": meta({"partidas_por_par_por_semente": N_POR_SEMENTE, "variantes": VARIANTES, "irma": IRMA,
                          "metodo": "so a forma medida muda; os 7 oponentes sao os bots canonicos; mesmos nomes e "
                                    "sementes da matriz (numeros aleatorios comuns); forca = media dos pontos contra as "
                                    "outras 7 (4 especies, 5 sementes, 100 partidas por semente); ep_entre_sementes = "
                                    "desvio padrao da variacao entre as 5 sementes / raiz de 5 (so indicativo)"}),
            "tabela": tabela, "taxa_contra_cada_oponente": detalhe}


# ------------------------------------------------------------------ 4. epsilon
def etapa_epsilon(pool) -> dict:
    esp = list(CONFIG_CATALOGO.especies_ativas)
    saida = {}
    for eps in EPSILONS:
        conf = []
        for _, c in sorted(pool.map(_rr_especie, [(e, N_POR_SEMENTE, eps) for e in esp])):
            conf += c
        saida[f"{eps:.2f}"] = resumo_matriz(conf)
    return {"meta": meta({"partidas_por_par_por_semente": N_POR_SEMENTE, "epsilons": list(EPSILONS),
                          "metodo": "epsilon trocado nos 8 bots dos dois lados; mesmas sementes da matriz. Com "
                                    "epsilon 0 nao ha acaso nenhum (a resolucao nao usa rng): cada par por especie tem "
                                    "um so resultado por ordem de lados"}),
            "por_epsilon": saida}


# ------------------------------------------------------------------ 5. painel B
def _painel_forma(args):
    forma, esp_pet, m, eps_pet = args
    r = regras()
    pet = lutador(forma, esp_pet, epsilon=eps_pet, nome=f"pet:{forma}@{esp_pet}")
    out = {}
    for s in sementes_calibracao():
        for e in CONFIG_CATALOGO.especies_ativas:
            for f in FORMAS:
                bot = lutador(f, e, nome=f"painel:{f}@{e}")
                pts = []
                for k in range(m):
                    sp = derivar_semente(f"diag-arquetipos|B|{s}", bot.nome, k)     # como run_educacao._painel_do_ovo
                    pts.append(jogar(pet, bot, sp, r).pontos_a if k < m // 2 else 1.0 - jogar(bot, pet, sp, r).pontos_a)
                out.setdefault(bot.nome, []).extend(pts)
    return forma, esp_pet, eps_pet, out


def etapa_painel(pool) -> dict:
    esp = list(CONFIG_CATALOGO.especies_ativas)
    eps_pet = (regras().base.epsilon_bots, 0.15)
    tarefas = [(f, e, M_PAINEL, x) for x in eps_pet for f in FORMAS for e in esp]
    res = {}
    for f, e, x, out in pool.map(_painel_forma, tarefas):
        res[(f, e, x)] = out
    saida = {}
    for x in eps_pet:
        tab = {}
        for f in FORMAS:
            por_esp = {e: _media(p for v in res[(f, e, x)].values() for p in v) for e in esp}
            por_bot_forma = {g: _media(p for e in esp for nome, v in res[(f, e, x)].items()
                                       if nome.split(":")[1].split("@")[0] == g for p in v) for g in FORMAS}
            tab[f] = {"taxa_painel": _media(por_esp.values()), "por_especie_do_pet": por_esp,
                      "contra_cada_forma_do_painel": por_bot_forma}
        saida[f"{x:.2f}"] = tab
    return {"meta": meta({"partidas_por_bot_por_semente": M_PAINEL, "epsilon_pet": list(eps_pet),
                          "metodo": "pet = bot canonico da forma (lutador_adulto, carater canonico, condicao 1,0, sem "
                                    "treino); painel = os 32 bots canonicos (8 formas x 4 especies), inclusive o espelho "
                                    "da propria forma; sementes derivar_semente('diag-arquetipos|B|<semente>', bot, k), "
                                    "lados trocados na metade, como run_educacao._painel_do_ovo. epsilon 0,15 = pet "
                                    "sem disciplina (epsilon_disciplina com disciplina 0)"}),
            "por_epsilon_do_pet": saida}


# ------------------------------------------------------------------ main
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Diagnostico dos arquetipos do combate V21C (so leitura)")
    ap.add_argument("--etapa", default="todas",
                    choices=("todas", "reproducao", "mecanismo", "atribuicao", "epsilon", "painel"))
    ap.add_argument("--processos", type=int, default=8)   # 18 derrubou o pool nesta maquina
    ap.add_argument("--rapido", type=Path, default=None, help="fumaca: N = 4, M = 4, saida nesta pasta (nao canonica)")
    a = ap.parse_args(argv)
    if a.rapido is not None:
        global N_POR_SEMENTE, M_PAINEL, SAIDA
        os.environ.update(DIAG_ARQ_N="4", DIAG_ARQ_M="4", DIAG_ARQ_SAIDA=str(a.rapido))
        N_POR_SEMENTE, M_PAINEL, SAIDA = 4, 4, a.rapido
    conferir_regras()
    sementes_calibracao()
    etapas = ("reproducao", "mecanismo", "atribuicao", "epsilon", "painel") if a.etapa == "todas" else (a.etapa,)
    with ProcessPoolExecutor(max_workers=a.processos) as pool:
        rep = None
        for et in etapas:
            t0 = time.perf_counter()
            print(f"{et} ...", flush=True)
            if et == "reproducao":
                rep = etapa_reproducao(pool)
                _gravar("reproducao.json", rep)
            else:
                if et in ("mecanismo", "atribuicao") and rep is None:
                    rep = json.loads((SAIDA / "reproducao.json").read_text(encoding="utf-8"))
                obj = {"mecanismo": lambda: etapa_mecanismo(pool, rep), "atribuicao": lambda: etapa_atribuicao(pool, rep),
                       "epsilon": lambda: etapa_epsilon(pool), "painel": lambda: etapa_painel(pool)}[et]()
                _gravar(f"{et}.json", obj)
            print(f"  {et}: {time.perf_counter() - t0:.0f} s", flush=True)
    arqs = sorted(SAIDA.glob("*.json"))
    print({p.name: hashlib.sha256(p.read_bytes()).hexdigest()[:12] for p in arqs})
    return 0


if __name__ == "__main__":
    sys.exit(main())
