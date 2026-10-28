"""O prototipo do DigiBrain modular, a avaliacao (docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md, secoes 2 a 6 e 10; as PPM-1 a
PPM-9 DECIDIDAS em 2026-10-25). O cenario do MVP na bancada Python (secao 3): o corpo quimico do v11 (`com_corpo(MotorMundo)`, a
ConfigCorpo do braco P1-c-tapa), o mundo do produto (o layout padrao sem arvores, so a racao do dono; a PPM-3 permite a este
orquestrador o layout do MVP), o contrato da P4 desligado, o pet sozinho, os quatro donos da v1 so com o cuidado (o filtro sem_ensino
ao vivo, `simular_vida_fisico`) e o lugar da racao (`DonoComLugar`: comedouro, perto, longe), 14 dias, 16 interacoes por dia.

Os bracos (secao 2), a mesma semente e o mesmo mundo em todos; o cerebro so consome a rng de politica:
    M0       a chave ligada; p1, p2 e m_mem desligados; a persistencia ligada; g_apr = g0 (o inato sozinho)
    M1       M0 + p1                         M2   M1 + p2              M3   M2 + m_mem (o braco principal)
    M3-sp    M3 sem a persistencia           M4   M3 + modula_g_apr (a excitacao modula o g_apr)
    M4-emb   M4 com a excitacao de outra vida: a serie E da vida M4 da unidade seguinte da mesma base, na mesma celula (a ultima unidade
             usa a primeira)
    M4-con   M3 com o g_apr fixo na media do g_apr das vidas M4 do piloto (o adendo 2; no piloto e na fumaca, a das vidas M4 da propria
             run)
    A11      o A v11 (P1-c-tapa, o alvo padrao do motor): o baseline, so na avaliacao (secao 7)
As celulas: dono x lugar, 4 x 3 = 12. A unidade: `unidades_derivadas(bases, K, "digibrain_prototipo")`.

As fases (o campo "fase" da config; a faixa 63101...63505 para a calibracao e o piloto, a 64101...64505 para a avaliacao):
    calibracao  bases 63101 e 63202, K = 2, so o M3 (secao 6.1): os quatro criterios, uma rodada por run (no maximo tres, registradas)
    piloto      bases 63303 a 63505, K = 2, os 8 bracos do modular (secao 6.2): o efeito, as premissas, a media do g_apr do M4, o K pelo
                poder (secao 6.3) e o custo; exige o adendo 1 no plano. Os numeros nao sao evidencia
    avaliacao   bases 64101 a 64505, o K e o g_apr do M4-con do adendo 2, os 9 bracos, uma vez so (a run se recusa a gravar por cima)
Na fumaca (as sementes dos testes) as fases rodam sem a faixa nem os adendos, e com menos dias se a config pedir.

O conserto (o adendo 3 do plano, APROVADO pelo Matheus em 2026-10-26): as fases `calibracao_conserto` (bases 65101 e 65202, K = 2, so o
M3*), `piloto_conserto` (65303 a 65505, K = 2, os 12 bracos) e `reavaliacao` (66101 a 66505, o K e o g_apr do M4-con do adendo 4, os 12
bracos, uma vez so). Nelas os bracos sao os de SUBCHAVES_CONSERTO: os 8 do modular com as duas subchaves do cheiro ligadas (o "M3" e o
M3* do adendo), mais o M3-sem-inato (so a `intencao_cheiro`), o M3-sem-intencao (so o `cheiro_inato`) e o M3-420 (as duas desligadas),
e o A11. As medidas ganham as do adendo (`_medidas_conserto_mundo` e `_medidas_conserto_cerebro`): o episodio de fome com a W(d) (a
primaria, A3.3), a medida por racao com a W(d), a DX-1 (com a `visitas_vazias_v1` ao lado), a DX-5 e o mecanismo do cheiro; e a analise,
o G-MVP por episodio como o primario, o de hoje como secundario obrigatorio, e a familia G-DX (Holm com 2). A reavaliacao e por estimativa
(o adendo 4, A4.7; `analisar_conserto`): os dois G-MVP sem "passa", com o IC pelo t e a posicao em relacao a 0,8; o Holm das tres familias
pelo p do t sobre as unidades (o G-MOD-EMB, pelas medias de base), com o g1 e a ressalva; o bootstrap ao lado, rotulado; a leitura de A4.6.
Ela exige o adendo 4 APROVADO pelo Matheus no cabecalho (`exigir_adendo_aprovado`). Em toda vida (de toda fase), o
T-CENARIO-1 (`conferir_cenario`) e o credito por opcao (`conferir_credito`) falham alto. Nas fases do prototipo (63xxx e 64xxx), as vidas
e as medidas sao as de hoje, byte a byte (tests/gabaritos/digibrain_modular_de_hoje.json).

Os gates (secao 5.2; por unidade, a media das 12 celulas, salvo a G-ABLA-MEM, so no comedouro; o bootstrap agrupado por base, 10.000
reamostragens, semente 4242): o G-MVP (o limite inferior do IC95 da fracao de vidas do M3 com a cadeia >= 0,8); a familia G-ABLA (P1,
P2, MEM, PERS), pelo Holm a 0,05 sobre o `p_unilateral` (secao 5.2.1); a familia G-MOD (CON, EMB), idem; as premissas G-PESA e
G-ELEGIVEL (secao 5.3). Toda vida e gravada e rejogada do disco bit a bit (G1), e as falhas altas da secao 6.4 valem em toda vida.

    python experiments/run_v2_digibrain_prototipo.py --config experiments/configs/v2_digibrain_prototipo/piloto.json --processos 8
    python experiments/run_v2_digibrain_prototipo.py --config experiments/configs/v2_digibrain_prototipo/fumaca_reavaliacao.json \
        --saida <pasta fora de artifacts_v2_digibrain_prototipo/> --processos 8
"""

from __future__ import annotations

import argparse
import bisect
import json
import math
import platform
import random
import statistics
import sys
import time
from dataclasses import replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import exportar_gabarito_lobos as gl  # noqa: E402
import run_v2_calibracao_mundo as rc  # noqa: E402
from bancada.regras_mundo import simular_vida_fisico  # noqa: E402
from digilab.config import (CONFIG_DIGIBRAIN_INATOS, CONFIG_DIGIBRAIN_LIGADA, CONFIG_MUNDO_MVP, CONFIG_PADRAO,  # noqa: E402
                            TICKS_POR_DIA, ConfigDigibrain, ConfigDigibrainInatos)
from digilab.digibrain import DigiBrain  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.events import LogDeEventos  # noqa: E402
from digilab.metrics import (ACOES_R_POSSIVEL, JANELA_8_14, MODULOS_SONDA, MOTIVOS_EPISODIO, assimetria_g1, cadeia_comida_corpo,  # noqa: E402
                             centro_temporal, contraste_pareado, deficit_fome_energia, entropia_acoes, episodios_de_fome,
                             exaustao_nas_decisoes, falta_ao_comer, holm, ic_percentil, ic_t, influencia_por_modulo, intencoes_com_meta,
                             janela_dias, janela_w, media_absoluta, pesos_no_teto, privacao_nas_decisoes, repeticao_apos_alivio,
                             t_medias_de_grupo, visitas_vazias, visitas_vazias_v1)
from digilab.motor_corpo import com_corpo  # noqa: E402
from digilab.mundo import ESTILOS_LUGAR, DonoComLugar, MotorMundo, reproduzir_mundo  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402
from digilab.temperamento import NEUTRO  # noqa: E402

PLANO = "docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md"
PREFIXO = "digibrain_prototipo"                                      # secao 3 (PREFIXOS_UNIDADES)
CM = CONFIG_MUNDO_MVP                                                # o mundo do produto (PPM-3)
BASES = {"calibracao": (63101, 63202), "piloto": (63303, 63404, 63505), "avaliacao": (64101, 64202, 64303, 64404, 64505),
         "calibracao_conserto": (65101, 65202), "piloto_conserto": (65303, 65404, 65505),        # o adendo 3, A3.9
         "reavaliacao": (66101, 66202, 66303, 66404, 66505)}
K_FIXO = {"calibracao": 2, "piloto": 2, "calibracao_conserto": 2, "piloto_conserto": 2}   # 6.1, 6.2 e A3.8; avaliacao e reavaliacao: os adendos 2 e 4
SAIDA = {"calibracao": "artifacts_v2_digibrain_prototipo/calibracao", "piloto": "artifacts_v2_digibrain_prototipo/piloto",
         "avaliacao": "artifacts_v2_digibrain_prototipo/avaliacao",
         "calibracao_conserto": "artifacts_v2_digibrain_prototipo/conserto/calibracao",
         "piloto_conserto": "artifacts_v2_digibrain_prototipo/conserto/piloto",
         "reavaliacao": "artifacts_v2_digibrain_prototipo/reavaliacao"}
FASES_CONSERTO = ("calibracao_conserto", "piloto_conserto", "reavaliacao")
FASES_CALIBRACAO = ("calibracao", "calibracao_conserto")
DONOS = ("atencioso", "relapso", "aleatorio", "incoerente")         # secao 3: as celulas, dono x lugar
LUGARES = ESTILOS_LUGAR                                              # comedouro, perto, longe
CELULAS = tuple((d, lugar) for d in DONOS for lugar in LUGARES)
DIAS, ORCAMENTO_POR_DIA = 14, 16                                     # secao 3
LIMIAR_PRIVACAO, LIMIAR_EXAUSTAO = 0.15, 0.25                        # secao 4 (o plano do corpo; o sono_exaustao)
SUBCHAVES = {"M0": {"p1": False, "p2": False, "m_mem": False}, "M1": {"p2": False, "m_mem": False}, "M2": {"m_mem": False}, "M3": {},
             "M3-sp": {"persistencia": False}, "M4": {"modula_g_apr": True},
             "M4-emb": {"modula_g_apr": True, "controle_g_apr": "embaralhado"}, "M4-con": {"controle_g_apr": "constante"}}
BRACOS_MODULAR = tuple(SUBCHAVES)
BRACOS = BRACOS_MODULAR + ("A11",)
BRACOS_DA_FASE = {"calibracao": ("M3",), "piloto": BRACOS_MODULAR, "avaliacao": BRACOS}
SEGUNDA_PASSADA = ("M4-emb", "M4-con")                               # dependem das vidas M4 (a serie E; a media do g_apr)
# o conserto (o adendo 3, A3.4): os 8 do modular com as duas subchaves do cheiro (o "M3" e o M3*), e os tres do 2 x 2
SUBCHAVES_CONSERTO = {**{b: {**s, "cheiro_inato": True, "intencao_cheiro": True} for b, s in SUBCHAVES.items()},
                      "M3-sem-inato": {"intencao_cheiro": True}, "M3-sem-intencao": {"cheiro_inato": True}, "M3-420": {}}
BRACOS_MODULAR_CONSERTO = tuple(SUBCHAVES_CONSERTO)
BRACOS_CONSERTO = BRACOS_MODULAR_CONSERTO + ("A11",)
BRACOS_DA_FASE.update({"calibracao_conserto": ("M3",), "piloto_conserto": BRACOS_CONSERTO, "reavaliacao": BRACOS_CONSERTO})
G_MVP_EP = {"w_decisoes": 8, "fome_elegivel": 0.5, "taxa_vida": 0.5, "limiar": 0.8}         # A3.3: os numeros da PPM-4, por episodio
G_ELEGIVEL_EP = {"frac_vidas": 0.8, "episodios": 3}                                          # A3.3: a premissa G-ELEGIVEL-EP
# as constantes do motor com que o adendo fixou a W(d), o R_lugar e o corte do d0 (A3.1 e A3.2), em subunidades
GEOMETRIA_DO_ADENDO = {"raio_pegar": 16, "passo": 60, "r_lugar": 76, "raio_visao": 96, "corte_d0": 384}

BOOTSTRAP = {"reamostragens": 10000, "semente": 4242, "nivel": 0.95}
PODER = {"k_min": 4, "k_max": 10, "replicas": 2000, "reamostragens_internas": 1000, "alvo": 0.8, "alfa_abla": 0.0125,
         "alfa_mod": 0.025, "semente": 4242, "n_bases": 5}            # secao 6.3
HOLM = {"alfa": 0.05}
G_MVP = {"w_decisoes": 8, "fome_elegivel": 0.5, "taxa_vida": 0.5, "limiar": 0.8}             # PPM-4
G_ELEGIVEL = {"frac_vidas": 0.8, "racoes": 3}                                                # PPM-4
G_PESA = {"limiar": 0.01, "bracos": {"incentivo": "M1", "habito": "M2", "memoria": "M3", "persistencia": "M3"}}   # PPM-5
FAMILIA_ABLA = ("G-ABLA-P1", "G-ABLA-P2", "G-ABLA-MEM", "G-ABLA-PERS")
FAMILIA_MOD = ("G-MOD-CON", "G-MOD-EMB")
MODULO_DO_GATE = {"G-ABLA-P1": "incentivo", "G-ABLA-P2": "habito", "G-ABLA-MEM": "memoria", "G-ABLA-PERS": "persistencia"}
CHAVES_CONFIG = {"descricao", "plano", "fase", "unidades", "dias", "orcamento_por_dia", "bootstrap", "poder", "holm", "g_mvp",
                 "g_elegivel", "g_pesa", "rodada"}
CHAVES_CONFIG_CONSERTO = CHAVES_CONFIG | {"g_mvp_ep", "g_elegivel_ep"}
# A3.8 e A3.11: o que a calibracao do conserto pode mudar (o campo opcional "inatos" da config, so nela), com a faixa de cada valor.
# O peso do cheiro de S/8 a S/2 e o N_desiste_cheiro de 5 a 8 (A3.8); da lista da secao 6.1, os escalares: as curvas a_r, b_r e
# lambda_r, os tau (>= Delta = 15 ticks, secao 1 da espec), os eta, o w_mem, o w_pers, o H_max e o g0 (o N_desiste fica na regra da PE-6,
# e os W0 sao tuplas: entram so por uma revisao deste orquestrador). O digilab/config.py nao muda na calibracao.
_S_INATOS = CONFIG_DIGIBRAIN_INATOS.escala
FAIXAS_INATOS_CONSERTO = {"w0_tipo_cheiro": (_S_INATOS // 8, _S_INATOS // 2), "n_desiste_cheiro": (5, 8)} | {
    n: (1, None) for n in ("urgencia_a", "urgencia_b", "urgencia_lambda", "eta_d", "eta_h", "w_mem", "w_pers", "h_max", "g0")} | {
    n: (CONFIG_PADRAO.intervalo_decisao_ticks, None) for n in ("tau_hab", "tau_v", "tau_e", "tau_c", "tau_f_sobe", "tau_f_desce")}


# ================================================================== a config
def _sem_rodada(cfg: dict) -> set:
    chaves = CHAVES_CONFIG_CONSERTO if cfg.get("fase") in FASES_CONSERTO else CHAVES_CONFIG
    return chaves - ({"rodada"} if cfg.get("fase") not in FASES_CALIBRACAO else set())


def adendo_do_piloto() -> dict:
    """O K e o g_apr do M4-con da avaliacao: os do piloto (artifacts_v2_digibrain_prototipo/piloto/resultado.json), que o adendo 2 do plano
    registra num commit antes da avaliacao."""
    caminho = RAIZ / SAIDA["piloto"] / "resultado.json"
    if not caminho.exists():
        raise FileNotFoundError("a avaliacao precisa do piloto e do adendo 2 (secao 6.3): rode o piloto antes")
    if "## Adendo 2" not in (RAIZ / PLANO).read_text(encoding="utf-8"):
        raise RuntimeError("o adendo 2 (o K, o poder, as premissas do piloto, o valor do M4-con e o custo) nao esta no plano: commit antes")
    r = json.loads(caminho.read_text(encoding="utf-8"))
    return {"k": r["n"]["k"], "g_apr_m4_con": r["g_apr_m4"]["m4_con"]}


def exigir_adendo_aprovado(plano: str, n: int) -> None:
    """a trava de A4.7: o adendo n tem de estar no plano E com o status "APROVADO pelo Matheus" no cabecalho dele (o titulo e o paragrafo
    do status, antes da primeira subsecao); so o titulo, ou um status PROPOSTO, nao libera vidas"""
    linhas = plano.splitlines()
    titulo = [i for i, x in enumerate(linhas) if x.startswith(f"## Adendo {n}:") or x == f"## Adendo {n}"]
    if len(titulo) != 1:
        raise RuntimeError(f"o adendo {n} nao esta no plano (ou esta mais de uma vez): {len(titulo)} titulos")
    cabecalho = []
    for x in linhas[titulo[0] + 1:]:
        if x.startswith("## ") or x.startswith("### "):
            break
        cabecalho.append(x)
    status = [x for x in cabecalho if x.startswith("**Status:")]
    if len(status) != 1 or not status[0].startswith("**Status: APROVADO pelo Matheus"):
        raise RuntimeError(f"o adendo {n} nao esta APROVADO pelo Matheus no cabecalho (A4.7): {status or 'sem a linha do status'}")


def adendo_do_piloto_conserto() -> dict:
    """O K e o g_apr do M4-con da reavaliacao: os do piloto do conserto (A3.8), que o adendo 4 do plano registra num commit antes dela."""
    caminho = RAIZ / SAIDA["piloto_conserto"] / "resultado.json"
    if not caminho.exists():
        raise FileNotFoundError("a reavaliacao precisa do piloto do conserto e do adendo 4 (A3.8): rode o piloto antes")
    exigir_adendo_aprovado((RAIZ / PLANO).read_text(encoding="utf-8"), 4)
    r = json.loads(caminho.read_text(encoding="utf-8"))
    return {"k": r["n"]["k"], "g_apr_m4_con": r["g_apr_m4"]["m4_con"]}


def inatos_da_config(cfg: dict) -> ConfigDigibrainInatos:
    """os valores da run: os de hoje (CONFIG_DIGIBRAIN_INATOS) com o campo "inatos" da config por cima, so na calibracao do conserto e so
    nos campos e nas faixas de FAIXAS_INATOS_CONSERTO (A3.8); fora disso, falha alto"""
    mudar = cfg.get("inatos", {})
    if not mudar:
        return CONFIG_DIGIBRAIN_INATOS
    if cfg.get("fase") != "calibracao_conserto":
        raise ValueError("o campo inatos da config e so da calibracao do conserto (A3.8)")
    for nome, valor in mudar.items():
        if nome not in FAIXAS_INATOS_CONSERTO:
            raise ValueError(f"inatos.{nome}: a calibracao do conserto so muda {sorted(FAIXAS_INATOS_CONSERTO)} (A3.8)")
        lo, hi = FAIXAS_INATOS_CONSERTO[nome]
        if type(valor) is not int or valor < lo or (hi is not None and valor > hi):
            raise ValueError(f"inatos.{nome} = {valor!r}: fora da faixa [{lo}, {hi}] (A3.8)")
    return replace(CONFIG_DIGIBRAIN_INATOS, **mudar)


def modo_da_config(cfg: dict) -> str:
    """'fumaca' (as sementes dos testes) ou a fase ('calibracao', 'piloto', 'avaliacao'), que segue o plano a letra."""
    esperadas = _sem_rodada(cfg) - {"descricao"}
    faltam, sobram = esperadas - set(cfg), set(cfg) - _sem_rodada(cfg) - {"inatos"}
    if faltam or sobram:
        raise ValueError(f"config: faltam {sorted(faltam)}, sobram {sorted(sobram)}")
    fase = cfg["fase"]
    if fase not in SAIDA:
        raise ValueError(f"fase {fase!r}: so {sorted(SAIDA)}")
    u = cfg["unidades"]
    bases = tuple(u["bases"])
    erros = []
    if u.get("prefixo") != PREFIXO:
        erros.append("prefixo")
    if cfg["orcamento_por_dia"] != ORCAMENTO_POR_DIA:
        erros.append("orcamento (secao 3)")
    fumaca = set(bases) <= bv.SEMENTES_TESTE
    if (cfg["bootstrap"] != BOOTSTRAP or cfg["holm"] != HOLM or cfg["g_mvp"] != G_MVP or cfg["g_elegivel"] != G_ELEGIVEL
            or cfg["g_pesa"] != G_PESA):
        erros.append("bootstrap, holm, g_mvp, g_elegivel ou g_pesa (secoes 5 e 6)")
    if cfg["poder"] != PODER and not (fumaca and set(cfg["poder"]) == set(PODER)):
        erros.append("poder (secao 6.3; so a fumaca pode pedir menos replicas)")
    if fase in FASES_CALIBRACAO and cfg.get("rodada") not in (1, 2, 3):
        erros.append("rodada da calibracao: 1, 2 ou 3 (secao 6.1; A3.8)")
    if fase in FASES_CONSERTO and (cfg["g_mvp_ep"] != G_MVP_EP or cfg["g_elegivel_ep"] != G_ELEGIVEL_EP):
        erros.append("g_mvp_ep ou g_elegivel_ep (adendo 3, A3.3)")
    inatos_da_config(cfg)
    if erros:
        raise ValueError(f"config fora do plano: {erros}")
    outras = set().union(*(range(BASES[f][0], BASES[f][-1] + 1) for f in BASES if f != fase))
    if set(bases) & outras:
        raise bv.SementeSemPlano(f"a {fase} recusa as sementes das outras fases (secao 9)")
    if fumaca:
        if not 1 <= cfg["dias"] <= DIAS:
            raise ValueError(f"fumaca com {cfg['dias']} dias: de 1 a {DIAS}")
        return "fumaca"
    if bases != BASES[fase]:
        raise bv.SementeSemPlano(f"bases {list(bases)}: so as dos testes (fumaca) ou {list(BASES[fase])} ({fase}, secao 9)")
    if cfg["dias"] != DIAS:
        erros.append(f"dias {cfg['dias']} (o plano: {DIAS})")
    if fase == "piloto" and "## Adendo 1" not in (RAIZ / PLANO).read_text(encoding="utf-8"):
        raise RuntimeError("o piloto precisa do adendo 1 no plano (os valores de partida congelados, secao 6.1): commit antes")
    if fase in FASES_CONSERTO and "## Adendo 3" not in (RAIZ / PLANO).read_text(encoding="utf-8"):
        raise RuntimeError("as fases do conserto precisam do adendo 3 no plano: commit antes")
    if fase in K_FIXO:
        k = K_FIXO[fase]
    else:
        k = (adendo_do_piloto_conserto() if fase == "reavaliacao" else adendo_do_piloto())["k"]
    if cfg.get("plano") != PLANO:
        erros.append(f"plano {cfg.get('plano')!r}")
    if u["k"] != k:
        erros.append(f"K {u['k']} (o plano: {k})")
    if erros:
        raise ValueError(f"a {fase} segue o plano a letra: {erros}")
    return fase


# ================================================================== as vidas
_BANCADAS: dict = {}


def bancada(dias: int, orcamento_por_dia: int) -> bv.Bancada:
    """a bancada do v11 (o corpo do P1-c-tapa, o ponto do adendo 4): so a ConfigCorpo e o cerebro do A11 saem dela"""
    chave = (dias, orcamento_por_dia)
    if chave not in _BANCADAS:
        _BANCADAS[chave] = gl.bancada_v11(dias, orcamento_por_dia * dias)
    return _BANCADAS[chave]


def config_do_braco(braco: str, g_apr_con: int | None = None, conserto: bool = False) -> ConfigDigibrain:
    """a ConfigDigibrain do braco: a do prototipo (SUBCHAVES) ou, nas fases do conserto, a do adendo 3 (SUBCHAVES_CONSERTO)"""
    tabela = SUBCHAVES_CONSERTO if conserto else SUBCHAVES
    if braco not in tabela:
        raise ValueError(f"braco do modular {braco!r}: so {tuple(tabela)}")
    extra = {"g_apr_constante": g_apr_con} if braco == "M4-con" else {}
    if braco == "M4-con" and (type(g_apr_con) is not int or g_apr_con <= 0):
        raise ValueError(f"o M4-con precisa do g_apr fixo (inteiro > 0): {g_apr_con!r}")
    return replace(CONFIG_DIGIBRAIN_LIGADA, **tabela[braco], **extra)


class Registro:
    """Embrulho que so le: o estado de cada decisao (o da Observacao, no tick k x intervalo) e a falta da fome logo depois da
    consequencia no corpo (o gancho `consequencia_corpo`, que o A e o DigiBrain tem). Repassa todo o resto; nao toca em rng."""

    def __init__(self, interna, S: int) -> None:
        self._interna = interna
        self._S = S
        self.estados: list[tuple] = []
        self.falta_depois: list[int] = []

    def agir(self, obs, rng):
        v = obs.vetor_estado
        self.estados.append((v[0], v[1], v[2], v[3], v[4], self._S - obs.corpo.fome))
        return self._interna.agir(obs, rng)

    def consequencia_corpo(self, acao, ocorrido, obs_depois) -> None:
        self.falta_depois.append(self._S - obs_depois.corpo.fome)
        self._interna.consequencia_corpo(acao, ocorrido, obs_depois)

    def observar(self, transicao) -> None:
        self._interna.observar(transicao)

    def estado_interno(self) -> dict:
        return self._interna.estado_interno()

    def __getattr__(self, nome: str):
        interna = self.__dict__.get("_interna")
        if interna is None:
            raise AttributeError(nome)
        return getattr(interna, nome)


def _tuplas(v):
    return tuple(_tuplas(x) for x in v) if isinstance(v, list) else v


def inatos_do_meta(meta: dict) -> ConfigDigibrainInatos:
    """os valores de partida de uma run, do meta.json dela (o JSON troca as tuplas por listas): para rejogar as vidas de uma rodada antiga
    da calibracao com os valores dela"""
    return ConfigDigibrainInatos(**{k: _tuplas(v) for k, v in meta["inatos"].items()})


def fabricas(braco: str, dono: str, semente: int, dias: int, orcamento_por_dia: int, serie_e: tuple | None = None,
             g_apr_con: int | None = None, inatos: ConfigDigibrainInatos | None = None, conserto: bool = False):
    """(a fabrica do cerebro, a do motor) da vida: o motor e o mesmo em todo braco. `inatos` (so para rejogar uma rodada antiga): os
    valores daquela rodada; None, os de hoje (CONFIG_DIGIBRAIN_INATOS)"""
    b = bancada(dias, orcamento_por_dia)
    espec = bv.EspecVida(dono, gl.BRACO_V11, semente)
    cc = b.cfg_corpo_de(espec)

    def fm(politica, cfg, s):
        return com_corpo(MotorMundo)(politica, cfg, s, NEUTRO, "brasa", obediencia_desligada=True, cfg_mundo=CM, cfg_corpo=cc)

    if braco == "A11":
        def fp(cfg=None):
            return Registro(b.politica(espec, cfg or CONFIG_PADRAO), CONFIG_DIGIBRAIN_INATOS.escala)
    else:
        cd = config_do_braco(braco, g_apr_con, conserto)

        def fp(cfg=None):
            return Registro(DigiBrain(cfg or CONFIG_PADRAO, cd, CM, inatos=inatos, serie_e_doadora=serie_e), CONFIG_DIGIBRAIN_INATOS.escala)
    return fp, fm


def viver(braco: str, dono: str, lugar: str, semente: int, dias: int, orcamento_por_dia: int, serie_e: tuple | None = None,
          g_apr_con: int | None = None, conserto: bool = False, inatos: ConfigDigibrainInatos | None = None):
    """uma vida: (o motor, o registro, as fabricas); `conserto`, os bracos do adendo 3; `inatos`, os da calibracao do conserto (A3.11)"""
    fp, fm = fabricas(braco, dono, semente, dias, orcamento_por_dia, serie_e, g_apr_con, inatos=inatos, conserto=conserto)
    registro = fp(CONFIG_PADRAO)
    d = DonoComLugar(criar_dono(dono), lugar, semente, dono, CM)
    motor, _ = simular_vida_fisico(d, registro, semente, dias, orcamento_por_dia * dias, dono, fm)
    return motor, registro, (fp, fm)


def conferir_replay(motor, fabricas_vida: tuple, semente: int, texto: str) -> None:
    """G1: a vida rejogada do log do disco, comparada bit a bit (o resumo do motor e o estado interno do cerebro)"""
    if texto != motor.log.para_jsonl():
        raise bv.ReplayDivergiu("o log do disco nao e o da vida")
    fp, fm = fabricas_vida
    r = reproduzir_mundo(LogDeEventos.de_jsonl(texto), fp, semente=semente, fabrica_motor=fm)
    if bv.resumo_motor(r) != bv.resumo_motor(motor):
        raise bv.ReplayDivergiu("log, estado, acoes ou rngs divergem no replay")
    if json.dumps(r.politica.estado_interno(), sort_keys=True) != json.dumps(motor.politica.estado_interno(), sort_keys=True):
        raise bv.ReplayDivergiu("o estado interno do cerebro diverge no replay")


def cerebro_de(registro: Registro):
    return registro._interna


def conferir_mecanismo(braco: str, registro: Registro, serie_e: tuple | None) -> None:
    """As falhas altas da secao 6.4, em toda vida do modular: com uma subchave desligada, o termo do modulo e 0 em toda decisao (o
    DigiBrain ja levanta erro decisao a decisao; aqui, o fim); o M0 com o desfecho, o habito e a memoria em 0 a vida inteira; o M4-emb leu
    a serie E inteira do doador; o reflexo do sono nunca sorteia."""
    c = cerebro_de(registro)
    cd = c.cd
    for m in c.motivos:
        if m["reflexo"] and (m["u"] is not None or m["acao"] != "dormir"):
            raise RuntimeError(f"{braco}: o reflexo do sono sorteou ou nao dormiu (decisao {m['k']})")
        for termo, ligada in (("incentivo", cd.p1), ("habito", cd.p2), ("memoria", cd.m_mem), ("persistencia", cd.persistencia)):
            if not ligada and any(u["termos"][termo] for u in m["unidades"]):
                raise RuntimeError(f"{braco}: o termo {termo!r} com a subchave desligada (decisao {m['k']})")
    if braco == "M0" and not (c.m.plast.desfecho_zero() and c.m.plast.habito_zero() and not c.m.mem.episodios):
        raise RuntimeError("M0: o desfecho, o habito ou a memoria sairam de 0")
    if braco == "M4-emb":
        if [m["afeto"]["e_usada"] for m in c.motivos] != list(serie_e[:len(c.motivos)]) or len(serie_e) != len(c.motivos):
            raise RuntimeError("M4-emb: a serie E usada nao e a do doador, decisao a decisao, inteira")
    conferir_credito(braco, c)


def conferir_credito(braco: str, c) -> None:
    """O credito por opcao (PE-3; a opcao composta da DX-4, A3.4), em toda vida do modular, pelo registro do cerebro: cada opcao entregue
    ao P2 cobre decisoes seguidas da propria unidade (a composta: as da busca pelo cheiro, depois as do `comer/comida`); o r dela e a soma
    (cortada em [-S, S], decisao a decisao) dos r_n dessas decisoes; nenhuma decisao, e com ela nenhuma refeicao, entra em duas opcoes
    entregues; e a busca guardada no "achou" e entregue uma vez so, pela composta ou sozinha na decisao seguinte. Falha alto."""
    S, ms = c.S, c.motivos
    rn = [None if m["consequencia"] is None else m["consequencia"]["r_n"] for m in ms]
    guardadas, entregues = {}, []
    for m in ms:
        for f in m["fins"]:
            if f["motivo"] == "achou":
                guardadas[f["inicio"]] = f
            elif f.get("composta"):
                if f["inicio"] not in guardadas:
                    raise RuntimeError(f"{braco}: a opcao composta da decisao {f['inicio']} sem a busca guardada")
                entregues.append((f, guardadas.pop(f["inicio"])))
            else:
                entregues.append((f, None))
        for f in m.get("busca_entregue", []):
            if guardadas.pop(f["inicio"], None) != f:
                raise RuntimeError(f"{braco}: a busca entregue na decisao {m['k']} nao e a guardada no achou")
            entregues.append((f, None))
    I = c.m.estado.I
    for g in guardadas.values():               # so a composta ainda aberta no fim da vida
        if I is None or not I.get("composta") or I["inicio"] != g["inicio"]:
            raise RuntimeError(f"{braco}: a busca guardada na decisao {g['inicio']} nunca foi entregue")
    coberta = set()
    for f, g in entregues:
        k0, n = f["inicio"], f["n"]
        r = 0
        for k in range(k0, k0 + n):
            if k >= len(ms) or rn[k] is None:
                raise RuntimeError(f"{braco}: a opcao da decisao {k0} entregue sem a consequencia da decisao {k}")
            if k in coberta:
                raise RuntimeError(f"{braco}: a decisao {k} em duas opcoes entregues")
            coberta.add(k)
            busca = g is not None and k < k0 + g["n"]
            if ms[k]["escolha"] != (["comer", "cheiro", None] if busca else f["chave"]):
                raise RuntimeError(f"{braco}: a decisao {k} nao e da unidade da opcao {f['chave']}")
            r = max(-S, min(S, r + rn[k]))
            if g is not None and k == k0 + g["n"] - 1 and r != g["r"]:
                raise RuntimeError(f"{braco}: o r da busca guardada na decisao {k0} nao e a soma das decisoes dela")
        if r != f["r"]:
            raise RuntimeError(f"{braco}: o r da opcao da decisao {k0} ({f['r']}) nao e a soma das decisoes dela ({r})")
    if c.m.estado.guardada is not None:
        raise RuntimeError(f"{braco}: a busca guardada passou da decisao seguinte")


def conferir_cenario(motor, registro: Registro) -> None:
    """O T-CENARIO-1 (o adendo 3, A3.3, A3.7 e A3.8), em toda vida: o cenario que o episodio de fome pressupoe, sem exclusao do
    denominador. (i) Toda comida do mundo e racao do dono, sem arvore, e todo consumo e de racao do dono; (ii) a fome nunca sobe numa
    decisao sem consumo; (iii) toda racao sai do chao so pelo consumo do pet ou pela idade; (iv) um pet so. Falha alto: pelo criterio de
    parada de A3.8, volta ao Matheus (nenhuma exclusao e criada para isso)."""
    passo = CONFIG_PADRAO.intervalo_decisao_ticks
    mundo = motor.mundo
    if motor.entrada_mundo != 0 or motor._grupo is not None:
        raise RuntimeError("T-CENARIO-1 (iv): mais de um pet no mundo")
    if mundo.arvores:
        raise RuntimeError("T-CENARIO-1 (i): arvores no mundo")
    dono = {d["id"]: d for d in motor.deixadas}
    if any(d["tipo"] != "racao" for d in dono.values()):
        raise RuntimeError("T-CENARIO-1 (i): o dono deixou outra comida")
    comidas, sumidas, no_chao = [c["id"] for c in motor.consumos_mundo], [s["id"] for s in mundo.sumidas], list(mundo.comidas)
    if set(comidas + sumidas + no_chao) - set(dono):
        raise RuntimeError("T-CENARIO-1 (i): comida no mundo que nao e racao do dono")
    if any(c["tipo"] != "racao" for c in motor.consumos_mundo):
        raise RuntimeError("T-CENARIO-1 (i): consumo que nao e racao")
    if len(comidas + sumidas + no_chao) != len(dono) or set(comidas + sumidas + no_chao) != set(dono):
        raise RuntimeError("T-CENARIO-1 (iii): racao saiu do chao por outra via (ou duas vezes)")
    es = registro.estados
    comeu = {(c["tick"] - motor.entrada_mundo) // passo for c in motor.consumos_mundo}
    for k in range(len(es) - 1):
        if es[k + 1][0] > es[k][0] and k not in comeu:
            raise RuntimeError(f"T-CENARIO-1 (ii): a fome subiu na decisao {k} sem consumo ({es[k][0]!r} -> {es[k + 1][0]!r})")


def geometria() -> dict:
    """As constantes do motor que a W(d), o R_lugar e o corte do d0 usam (A3.1 e A3.2), lidas do mundo do produto e do Config. O adendo
    as fixou com GEOMETRIA_DO_ADENDO; uma constante diferente falha alto (o T-EPISODIO-5): a W(d) teria de voltar ao Matheus."""
    sub = CM.sub
    g = {"raio_pegar": CM.raio_pegar_celulas * sub, "passo": CM.velocidade * CONFIG_PADRAO.intervalo_decisao_ticks}
    g.update({"r_lugar": g["passo"] + g["raio_pegar"], "raio_visao": CM.raio_visao_celulas * sub, "corte_d0": CM.raio_cheiro_celulas * sub})
    if g != GEOMETRIA_DO_ADENDO:
        raise RuntimeError(f"as constantes do motor {g} nao sao as do adendo 3 {GEOMETRIA_DO_ADENDO}: a W(d) volta ao Matheus")
    return g


def w_de(d0: int) -> int:
    """a W(d0) do adendo (A3.2), em decisoes depois da k0: a mesma em todo braco e lugar (o T-JANELA-IGUAL)"""
    g = geometria()
    return janela_w(d0, G_MVP_EP["w_decisoes"], g["raio_pegar"], g["passo"])


def _contexto_ganhou_fica(m: dict) -> tuple:
    c = m["contexto"]
    return (c["drive"], c["comida_vista"], c["noite"])


def medidas(motor, registro: Registro, braco: str, dias: int, conserto: bool = False) -> dict:
    """As medidas da secao 4, pelas funcoes de metrics.py (o estado de cada decisao e o da Observacao; a decisao k no tick k x 15). Nas
    fases do conserto (`conserto`), tambem as do adendo 3 (`_medidas_conserto`); nas do prototipo, so as de hoje, byte a byte."""
    passo = CONFIG_PADRAO.intervalo_decisao_ticks
    es = registro.estados
    if len(es) * passo != dias * TICKS_POR_DIA:
        raise RuntimeError(f"{len(es)} decisoes em {dias} dias: o relogio da decisao nao e k x {passo}")
    if len(registro.falta_depois) != len(es):
        raise RuntimeError("o gancho consequencia_corpo nao veio em toda decisao")
    janela = JANELA_8_14 if dias >= 14 else janela_dias(1, dias)
    vida = janela_dias(1, dias)
    ticks = [k * passo for k in range(len(es))]
    fe = [(t, e[0], e[2]) for t, e in zip(ticks, es)]
    # a cadeia comida -> corpo: as racoes postas pelo dono, a fome da primeira decisao em ou depois, e os consumos do pet
    entrada = motor.entrada_mundo                       # o relogio do mundo e o do pet mais a entrada (0 com um pet so)
    racoes = []
    for d in motor.deixadas:
        if d["tipo"] != "racao":
            continue
        t0 = d["tick"] - entrada
        k = -(-t0 // passo)
        racoes.append((d["id"], t0, es[k][0] if k < len(es) else None))
    consumos = []
    for c in motor.consumos_mundo:
        t = c["tick"] - entrada
        if t % passo:
            raise RuntimeError(f"consumo fora do tick de uma decisao: {t}")
        consumos.append((c["id"], t, c["tipo"], es[t // passo][5], registro.falta_depois[t // passo]))
    cadeia = cadeia_comida_corpo(racoes, consumos, dias, G_MVP["w_decisoes"] * passo, G_MVP["fome_elegivel"])
    out = {"d_fe": deficit_fome_energia(fe, janela)["d_fe"], "d_fe_vida": deficit_fome_energia(fe, vida)["d_fe"],
           "privacao": privacao_nas_decisoes([(t, e[0], e[1], e[2], e[3]) for t, e in zip(ticks, es)
                                              if janela[0] <= t < janela[1]], LIMIAR_PRIVACAO)["fracao_privacao"],
           "exaustao": exaustao_nas_decisoes([(t, e[2]) for t, e in zip(ticks, es)], janela, LIMIAR_EXAUSTAO)["frac"],
           "cadeia": {k: v for k, v in cadeia.items() if k != "latencias"},
           "latencia_media": statistics.fmean(cadeia["latencias"]) if cadeia["latencias"] else None,
           "acoes": dict(sorted(_contar(a.value for _, a in motor.acoes_recentes(10**9)).items()))}
    out["com_cadeia"] = None if cadeia["taxa"] is None else cadeia["taxa"] >= G_MVP["taxa_vida"]
    conserto_mundo = _medidas_conserto_mundo(motor, registro, dias, consumos) if conserto else None
    if conserto:
        out.update({k: v for k, v in conserto_mundo.items() if not k.startswith("_")})
    if braco == "A11":
        return out
    c = cerebro_de(registro)
    ms = c.motivos
    if len(ms) != len(es):
        raise RuntimeError("o registro do cerebro e o do motor com numeros de decisoes diferentes")
    S = c.S
    sondas = [(t, {mod: m["sondas"][f"{mod}_decidiu"] for mod in MODULOS_SONDA + ("aprendido",)}) for t, m in zip(ticks, ms)]
    infl = influencia_por_modulo(sondas, janela, MODULOS_SONDA + ("aprendido",))
    infl_vida = influencia_por_modulo(sondas, vida, MODULOS_SONDA + ("aprendido",))
    comer_racao = [(t, m["acao"] == "comer" and m["tipo_escolha"] == "racao", m["falta_fome"] / S) for t, m in zip(ticks, ms)]
    rep = [(t, _contexto_ganhou_fica(m), m["acao"], None if m["consequencia"] is None else m["consequencia"]["r"])
           for t, m in zip(ticks, ms)]
    # a G-ABLA-PERS: as intencoes do comer numa comida vista (no prototipo, as unicas do comer; com a DX-4, a busca pelo cheiro fica fora)
    intencoes = [(f["inicio"] * passo, bool(f["meta"])) for m in ms for f in m["fins"] if f["chave"][:2] == ["comer", "comida"]]
    H = [v for linha in c.m.plast.H.values() for v in linha]
    fins = _contar(f["motivo"] for m in ms for f in m["fins"])
    episodios = c.m.mem.estado_interno()
    visitas = [m for m in ms if m["consequencia"] is not None and m["consequencia"]["episodio"] is not None
               and tuple(m["escolha"][:2]) == ("explorar", "ponto")]
    acoes_dia = [[m["acao"] for t, m in zip(ticks, ms) if t // TICKS_POR_DIA == d] for d in range(dias)]
    out.update({
        "influencia": infl["frac"], "influencia_vida": infl_vida["frac"], "influencia_por_dia": infl_vida["por_dia"],
        "falta_ao_comer": falta_ao_comer(comer_racao, janela)["media"],
        "repeticao": repeticao_apos_alivio(rep, janela),
        "intencoes_com_meta": intencoes_com_meta(intencoes, janela)["frac"],
        "pesos_no_teto": pesos_no_teto(H, c.inatos.h_max),
        "g_apr_media": statistics.fmean(m["afeto"]["g_apr"] for m in ms),
        "exploracao": sum(1 for m in ms if m["acao"] == "explorar") / len(ms),
        "entropia_dia": statistics.fmean(e for e in (entropia_acoes(a) for a in acoes_dia) if e is not None),
        "taxa_p1": media_absoluta([m["consequencia"]["p1"]["abs"] for m in ms if m["consequencia"] and m["consequencia"]["p1"]]),
        "taxa_p2": media_absoluta([cr["abs"] for m in ms for cr in m["creditos"] + (m["consequencia"] or {}).get("creditos", [])]),
        "fins": dict(sorted(fins.items())), "reflexos": sum(1 for m in ms if m["reflexo"]),
        "nada_a_fazer": sum(1 for m in ms if m["nada_a_fazer"]),
        "episodios": {"codificados": episodios["proximo_id"], "sairam": len(episodios["saidas"]),
                      "sairam_r_pos": sum(1 for s in episodios["saidas"] if s["r"] > 0), "no_fim": len(episodios["episodios"])},
        "visitas_lugar_lembrado": len(visitas),
        "visitas_vazias": visitas_vazias_v1([m["consequencia"]["comeu"] is not None for m in visitas])})
    if conserto:
        out.update(_medidas_conserto_cerebro(motor, ms, rep, janela, conserto_mundo, len(visitas)))
    return out


def _no_chao(t0: int, k_comida: int | None, k: int, passo: int, prazo: int) -> bool:
    """a comida posta no tick t0 (e comida na decisao k_comida, ou nunca) esta no chao na decisao k, com menos de `prazo` ticks de idade
    (a decisao do consumo ainda a ve: o pet decide antes de comer)"""
    t = k * passo
    return t0 <= t and t - t0 < prazo and (k_comida is None or k_comida >= k)


def _medidas_conserto_mundo(motor, registro: Registro, dias: int, consumos: list) -> dict:
    """As medidas do adendo 3 que so leem o motor (em todo braco, o A11 tambem): o episodio de fome (a DX-2, A3.3, a primaria), a medida
    por racao com a W(d) e a racao na janela (as que ja estavam na visao em k0, as que entram nela, a menor distancia), descritivas. A
    oferta de cada decisao: as racoes do dono maduras e nao comidas no chao (as comidas do mundo sao as do dono: o T-CENARIO-1)."""
    g = geometria()
    passo = CONFIG_PADRAO.intervalo_decisao_ticks
    es = registro.estados
    n = len(es)
    entrada = motor.entrada_mundo
    dm = motor.decisoes_mundo
    if len(dm) != n or any(d["tick"] - entrada != k * passo for k, d in enumerate(dm)):
        raise RuntimeError("as decisoes do mundo nao sao as do pet, uma por decisao, no tick k x 15")
    pos = [tuple(d["antes"]) for d in dm]
    k_comida = {c["id"]: (c["tick"] - entrada) // passo for c in motor.consumos_mundo}
    racoes = sorted((d for d in motor.deixadas if d["tipo"] == "racao"), key=lambda d: (d["tick"], d["id"]))
    t0s = [d["tick"] - entrada for d in racoes]
    maduro, idade_max = CM.maduro_racao_min, CM.maduro_racao_min + CM.prazo_podre_min

    def dist(k: int, d: dict) -> int:
        x, y = pos[k]
        return math.isqrt((d["x"] - x) * (d["x"] - x) + (d["y"] - y) * (d["y"] - y))

    decs = []
    for k in range(n):
        t = k * passo
        oferta = {d["id"]: dist(k, d) for d in racoes[bisect.bisect_left(t0s, t - maduro + 1):bisect.bisect_right(t0s, t)]
                  if _no_chao(d["tick"] - entrada, k_comida.get(d["id"]), k, passo, maduro)}
        decs.append((k, es[k][0], min(oferta.values()) if oferta else None, frozenset(oferta)))
    ids_dono = {d["id"] for d in racoes}
    refeicoes = []
    for c in motor.consumos_mundo:
        k = (c["tick"] - entrada) // passo
        refeicoes.append((k, c["id"] in ids_dono, c["situacao"] == "madura", es[k][5], registro.falta_depois[k]))
    ep = episodios_de_fome(decs, refeicoes, G_MVP_EP["w_decisoes"], g["raio_pegar"], g["passo"], G_MVP_EP["fome_elegivel"],
                           g["corte_d0"])
    ep["com_cadeia"] = None if ep["taxa"] is None else ep["taxa"] >= G_MVP_EP["taxa_vida"]
    ep["latencia_media"] = statistics.fmean(ep["latencias"]) if ep["latencias"] else None
    # a medida por racao com a W(d) (descritiva) e a racao na janela W(d) de cada racao elegivel
    rac, w_por = [], {}
    na_janela = {"elegiveis": 0, "visiveis_em_k0": 0, "entraram_na_visao": 0}
    d_min = []
    for d in racoes:
        t0 = d["tick"] - entrada
        k0 = -(-t0 // passo)
        fome = es[k0][0] if k0 < n else None
        rac.append((d["id"], t0, fome))
        if k0 >= n:
            continue
        w = w_de(dist(k0, d))
        w_por[d["id"]] = w * passo
        if fome >= G_MVP["fome_elegivel"]:
            continue
        ds = [dist(k, d) for k in range(k0, min(n, k0 + w + 1)) if _no_chao(t0, k_comida.get(d["id"]), k, passo, idade_max)]
        na_janela["elegiveis"] += 1
        na_janela["visiveis_em_k0"] += ds[0] <= g["raio_visao"]
        na_janela["entraram_na_visao"] += ds[0] > g["raio_visao"] and min(ds) <= g["raio_visao"]
        d_min.append(min(ds))
    cw = cadeia_comida_corpo(rac, consumos, dias, G_MVP["w_decisoes"] * passo, G_MVP["fome_elegivel"], w_ticks_por_racao=w_por)
    na_janela["d_min_media_celulas"] = statistics.fmean(d_min) / CM.sub if d_min else None
    return {"episodios_fome": ep, "cadeia_w": {k: v for k, v in cw.items() if k != "latencias"}, "racao_na_janela": na_janela,
            "_janelas": sorted({k for e in ep["episodios"] for k in range(e[0], e[3] + 1)})}


def _rep_curto(r: dict) -> dict:
    return {"indice": r["indice"], "n_pos": r["n_pos"], "n_nao_pos": r["n_nao_pos"]}


def _medidas_conserto_cerebro(motor, ms: list, rep: list, janela: tuple, mundo: dict, n_visitas: int) -> dict:
    """As medidas do adendo 3 que leem o registro do cerebro: a DX-1 (A3.1; a `visitas_vazias` corrigida, com a `visitas_vazias_v1` ao
    lado), a DX-5 (A3.5; o "ganhou, fica" so nas acoes com r > 0 possivel, no total e por acao) e o mecanismo do cheiro (A3.4) nas
    decisoes dos episodios de fome, descritivos."""
    g = geometria()
    passo = CONFIG_PADRAO.intervalo_decisao_ticks
    entrada = motor.entrada_mundo
    k_comida = {c["id"]: (c["tick"] - entrada) // passo for c in motor.consumos_mundo}
    visitas = [(k, m) for k, m in enumerate(ms) if m["escolha"][:2] == ["explorar", "ponto"] and m["consequencia"] is not None
               and m["consequencia"]["chegou"]]
    if len(visitas) != n_visitas:
        raise RuntimeError("as visitas da DX-1 nao sao as do prototipo (a opcao do explorar/ponto que chegou)")

    def maduras_no_chao(k: int) -> list:
        return [(d["id"], d["x"], d["y"]) for d in motor.deixadas
                if _no_chao(d["tick"] - entrada, k_comida.get(d["id"]), k, passo, CM.maduro_racao_min)]

    dx1 = visitas_vazias([(k, m["escolha"][2][0], m["escolha"][2][1], maduras_no_chao(k)) for k, m in visitas],
                         sorted((k, i) for i, k in k_comida.items()), g["r_lugar"])
    v1 = visitas_vazias_v1([m["consequencia"]["comeu"] is not None for _, m in visitas])
    dx5 = {"total": _rep_curto(repeticao_apos_alivio(rep, janela, ACOES_R_POSSIVEL)),
           "por_acao": {a: _rep_curto(repeticao_apos_alivio(rep, janela, (a,))) for a in ACOES_R_POSSIVEL}}
    js = mundo["_janelas"]
    buscas = [f for m in ms for f in m["fins"] if f["chave"][:2] == ["comer", "cheiro"]]
    compostas = [f for m in ms for f in m["fins"] if f.get("composta")]
    fins = _contar(f["motivo"] for f in buscas)
    cheiro = {"episodios": mundo["episodios_fome"]["n"],
              "decisoes_comer_cheiro": sum(1 for k in js if ms[k]["escolha"][:2] == ["comer", "cheiro"]),
              "decisoes_explorar_cheiro": sum(1 for k in js if ms[k]["escolha"][:2] == ["explorar", "cheiro"]),
              "decisoes_dormir": sum(1 for k in js if ms[k]["acao"] == "dormir"), "decisoes_nos_episodios": len(js),
              "fins_busca": dict(sorted(fins.items())), "achou": fins.get("achou", 0), "compostas": len(compostas),
              "compostas_com_refeicao": sum(1 for f in compostas if f["meta"]),
              "busca_entregue_sozinha": sum(len(m.get("busca_entregue", [])) for m in ms)}
    return {"visitas_vazias": dx1["vazias"], "visitas_vazias_v1": v1, "repeticao_r_possivel": dx5, "cheiro": cheiro}



def _contar(xs) -> dict:
    out: dict = {}
    for x in xs:
        out[x] = out.get(x, 0) + 1
    return out


def _vida_gravada(cfg: dict, braco: str, dono: str, lugar: str, unidade: dict, pasta: str, serie_e: tuple | None = None,
                  g_apr_con: int | None = None) -> dict:
    """uma vida: vivida, gravada, rejogada do disco (G1), conferida (as falhas altas) e medida"""
    c0, p0 = time.process_time(), time.perf_counter()
    conserto = cfg["fase"] in FASES_CONSERTO
    inatos = inatos_da_config(cfg)
    motor, registro, fab = viver(braco, dono, lugar, unidade["semente"], cfg["dias"], cfg["orcamento_por_dia"], serie_e, g_apr_con,
                                 conserto=conserto, inatos=None if inatos is CONFIG_DIGIBRAIN_INATOS else inatos)
    nome = f"{braco}|{dono}|{lugar}|{unidade['semente']}"
    arquivo = Path(pasta) / "vidas" / braco / f"{dono}_{lugar}_{unidade['semente']}.jsonl"
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    arquivo.write_text(motor.log.para_jsonl(), encoding="utf-8", newline="\n")
    conferir_replay(motor, fab, unidade["semente"], arquivo.read_text(encoding="utf-8"))
    conferir_cenario(motor, registro)
    if braco != "A11":
        conferir_mecanismo(braco, registro, serie_e)
    out = {"vida": nome, "braco": braco, "dono": dono, "lugar": lugar, "semente": unidade["semente"], "base": unidade["base"],
           "k": unidade["k"], **medidas(motor, registro, braco, cfg["dias"], conserto),
           "custo": {"vida_cpu": time.process_time() - c0, "vida_parede": time.perf_counter() - p0}}
    if braco == "M4":
        out["serie_e"] = list(cerebro_de(registro).m.afeto.serie_e)
    return out


def tarefa_primeira(cfg: dict, unidade: dict, pasta: str, bracos: tuple) -> list[dict]:
    """as vidas de uma unidade dos bracos que nao dependem de outras vidas (todas as celulas)"""
    return [_vida_gravada(cfg, b, dono, lugar, unidade, pasta) for b in bracos for dono, lugar in CELULAS]


def tarefa_segunda(cfg: dict, unidade: dict, pasta: str, series: dict, g_apr_con: int) -> list[dict]:
    """o M4-emb (a serie E do doador de cada celula) e o M4-con (o g_apr fixo) de uma unidade"""
    out = []
    for dono, lugar in CELULAS:
        out.append(_vida_gravada(cfg, "M4-emb", dono, lugar, unidade, pasta, serie_e=tuple(series[(dono, lugar)])))
        out.append(_vida_gravada(cfg, "M4-con", dono, lugar, unidade, pasta, g_apr_con=g_apr_con))
    return out


def doadores(unidades: list[dict]) -> dict:
    """a unidade doadora de cada unidade (secao 2): a seguinte da mesma base, e a ultima usa a primeira"""
    por_base: dict = {}
    for u in unidades:
        por_base.setdefault(u["base"], []).append(u)
    out = {}
    for us in por_base.values():
        us = sorted(us, key=lambda u: u["k"])
        for i, u in enumerate(us):
            out[u["semente"]] = us[(i + 1) % len(us)]["semente"]
    return out


# ================================================================== a analise (funcoes puras)
def _idx(registros: list[dict]) -> dict:
    idx = {}
    for r in registros:
        chave = (r["semente"], r["dono"], r["lugar"], r["braco"])
        if chave in idx:
            raise RuntimeError(f"vida repetida: {chave}")
        idx[chave] = r
    return idx


def _ler(medida):
    if callable(medida):
        return medida
    return lambda r: r[medida]


def por_unidade(registros: list[dict], braco_a: str, braco_b: str | None, medida, celulas=CELULAS) -> dict:
    """{(base, semente): a media nas celulas de medida(a) - medida(b)} (b None: o nivel de a). As celulas com valor None num dos bracos
    ficam fora; a unidade sem celula com valor fica fora (a familia nao encolhe: o contraste sai sem p)."""
    ler, idx = _ler(medida), _idx(registros)
    out = {}
    for s, base in sorted({(r["semente"], r["base"]) for r in registros}):
        ds = []
        for dono, lugar in celulas:
            a = idx.get((s, dono, lugar, braco_a))
            if a is None:
                raise RuntimeError(f"unidade {s}, celula {dono}/{lugar}: falta o {braco_a}")
            va = ler(a)
            if braco_b is None:
                if va is not None:
                    ds.append(va)
                continue
            b = idx.get((s, dono, lugar, braco_b))
            if b is None:
                raise RuntimeError(f"unidade {s}, celula {dono}/{lugar}: falta o {braco_b}")
            vb = ler(b)
            if va is not None and vb is not None:
                ds.append(va - vb)
        if ds:
            out[(base, s)] = sum(ds) / len(ds)
    return out


def contraste(difs: dict, boot: dict) -> dict:
    """o contraste_pareado agrupado por base (secao 5.2.1): {base: [as unidades dela]}"""
    grupos: dict = {}
    for (base, _), d in sorted(difs.items()):
        grupos.setdefault(base, []).append(d)
    return contraste_pareado(grupos, boot["reamostragens"], boot["semente"])


CELULAS_COMEDOURO = tuple(c for c in CELULAS if c[1] == "comedouro")
CONTRASTES_ABLA = {"G-ABLA-P1": ("M0", "M1", "falta_ao_comer", CELULAS), "G-ABLA-P2": ("M2", "M1", lambda r: r["repeticao"]["indice"], CELULAS),
                   "G-ABLA-MEM": ("M3", "M2", lambda r: r["cadeia"]["taxa"], CELULAS_COMEDOURO),
                   "G-ABLA-PERS": ("M3", "M3-sp", "intencoes_com_meta", CELULAS)}
CONTRASTES_MOD = {"G-MOD-CON": ("M4-con", "M4", "d_fe", CELULAS), "G-MOD-EMB": ("M4-emb", "M4", "d_fe", CELULAS)}


def g_pesa(registros: list[dict], boot: dict, cfg_pesa: dict) -> dict:
    """a premissa por modulo (secao 5.3): no braco em que o modulo entra, a fracao das decisoes (dias 8 a 14) com `<modulo>_decidiu`; o
    limite inferior do IC95 > 0,01"""
    out = {}
    for mod, braco in cfg_pesa["bracos"].items():
        r = contraste(por_unidade(registros, braco, None, lambda x, mod=mod: x["influencia"][mod]), boot)
        out[mod] = {"braco": braco, **r, "passa": r["ic95"] is not None and r["ic95"]["ic_inferior"] > cfg_pesa["limiar"]}
    return out


def familia(registros: list[dict], contrastes: dict, boot: dict, alfa: float) -> dict:
    """os contrastes de uma familia, orientados (positivo = a direcao da espec), com o Holm sobre o p_unilateral (secao 5.2.1); o IC95 so
    descritivo"""
    out = {}
    for nome, (a, b, med, celulas) in contrastes.items():
        out[nome] = {"contraste": f"{med if isinstance(med, str) else 'medida'}({a}) - ({b})", "celulas": len(celulas),
                     **contraste(por_unidade(registros, a, b, med, celulas), boot)}
    h = holm({n: out[n]["p_unilateral"] for n in contrastes}, alfa)
    for n in contrastes:
        out[n]["holm"] = h[n]
        out[n]["passa"] = h[n]["rejeita"]
    return out


def fracao_com_cadeia(registros: list[dict], braco: str = "M3") -> dict:
    """{(base, semente): a fracao das vidas (celulas) com a cadeia}, so as vidas com racao elegivel; e as vidas sem elegivel"""
    fr = por_unidade(registros, braco, None, lambda r: None if r["com_cadeia"] is None else float(r["com_cadeia"]))
    sem = sum(1 for r in registros if r["braco"] == braco and r["com_cadeia"] is None)
    return {"por_unidade": fr, "vidas_sem_elegivel": sem}


def g_mvp(registros: list[dict], boot: dict, cfg_mvp: dict) -> dict:
    fc = fracao_com_cadeia(registros)
    r = contraste(fc["por_unidade"], boot)
    return {"medida": "a fracao de vidas do M3 com a taxa de fechamento >= 0,5 (media das celulas por unidade)", **r,
            "vidas_sem_elegivel": fc["vidas_sem_elegivel"], "limiar": cfg_mvp["limiar"],
            "passa": r["ic95"] is not None and r["ic95"]["ic_inferior"] >= cfg_mvp["limiar"]}


def g_elegivel(registros: list[dict], cfg_el: dict) -> dict:
    vs = [r for r in registros if r["braco"] == "M3"]
    frac = sum(1 for r in vs if r["cadeia"]["elegiveis"] >= cfg_el["racoes"]) / len(vs)
    return {"frac_vidas": frac, "vidas": len(vs), "passa": frac >= cfg_el["frac_vidas"]}


def comparacao_com_o_a(registros: list[dict], boot: dict, conserto: bool = False, est=contraste) -> dict:
    """a comparacao descritiva com o A (secao 7, o D6): M3 - A11 e M0 - A11, sem Holm e sem margem; no conserto, tambem o episodio. `est`:
    o contraste (na reavaliacao, o contraste_t de A4.4.6)"""
    meds = {"d_fe": "d_fe", "privacao": "privacao", "refeicoes_por_dia": lambda r: r["cadeia"]["refeicoes_por_dia"],
            "taxa": lambda r: r["cadeia"]["taxa"], "com_cadeia": lambda r: None if r["com_cadeia"] is None else float(r["com_cadeia"])}
    if conserto:
        meds.update({"taxa_ep": lambda r: r["episodios_fome"]["taxa"],
                     "com_cadeia_ep": lambda r: None if r["episodios_fome"]["com_cadeia"] is None else float(r["episodios_fome"]["com_cadeia"])})
    return {f"{b} - A11": {n: est(por_unidade(registros, b, "A11", m), boot) for n, m in meds.items()} for b in ("M3", "M0")}


def leitura_d2(registros: list[dict], boot: dict, est=contraste) -> dict:
    """D-2 (secao 8): centro_temporal(habito) - centro_temporal(memoria) no M3, por unidade; positiva e a ordem prevista. Sem gate. `est`:
    o contraste (na reavaliacao, o contraste_t de A4.4.6)"""
    def dif(r):
        h, m = (centro_temporal([0.0 if f is None else f for f in r["influencia_por_dia"][x]]) for x in ("habito", "memoria"))
        return None if h is None or m is None else h - m
    por_lugar = {lugar: est(por_unidade(registros, "M3", None, dif, tuple(c for c in CELULAS if c[1] == lugar)), boot)
                 for lugar in LUGARES}
    return {"habito_menos_memoria": est(por_unidade(registros, "M3", None, dif), boot), "por_lugar": por_lugar}


def leitura_d1(registros: list[dict], boot: dict, est=contraste) -> dict:
    """D-1 (secao 8): M4 - M4-con na exploracao (a fracao e a entropia das acoes por dia) e na taxa de aprendizado (|delta d| e |delta H|),
    cada diferenca pelo desvio padrao das unidades do M4-con. Sem gate."""
    out = {}
    for nome in ("exploracao", "entropia_dia", "taxa_p1", "taxa_p2"):
        difs = por_unidade(registros, "M4", "M4-con", nome)
        nivel = list(por_unidade(registros, "M4-con", None, nome).values())
        dp = statistics.stdev(nivel) if len(nivel) > 1 else None
        padr = {k: v / dp for k, v in difs.items()} if dp else {}
        out[nome] = {"bruto": est(difs, boot), "dp_m4_con": dp, "padronizado": est(padr, boot) if padr else None}
    return out


def descritivos(registros: list[dict]) -> dict:
    out = {}
    for b in sorted({r["braco"] for r in registros}):
        rs = [r for r in registros if r["braco"] == b]
        out[b] = {"d_fe": statistics.fmean(r["d_fe"] for r in rs), "privacao": statistics.fmean(r["privacao"] for r in rs),
                  "exaustao": statistics.fmean(r["exaustao"] for r in rs),
                  "refeicoes_por_dia": statistics.fmean(r["cadeia"]["refeicoes_por_dia"] for r in rs),
                  "por_celula": {f"{d}|{lugar}": {"d_fe": statistics.fmean(r["d_fe"] for r in rs if r["dono"] == d and r["lugar"] == lugar)}
                                 for d, lugar in CELULAS}}
        if b != "A11":
            out[b]["influencia"] = {m: statistics.fmean(r["influencia"][m] for r in rs) for m in rs[0]["influencia"]}
            out[b]["fins"] = _somar(r["fins"] for r in rs)
            out[b]["visitas_lugar_lembrado"] = sum(r["visitas_lugar_lembrado"] for r in rs)
            out[b]["visitas_vazias"] = sum(r["visitas_vazias"] for r in rs)
            out[b]["episodios_sairam"] = sum(r["episodios"]["sairam"] for r in rs)
            out[b]["pesos_no_teto"] = statistics.fmean(r["pesos_no_teto"] for r in rs)
    return out


def _somar(dicts) -> dict:
    out: dict = {}
    for d in dicts:
        for k, v in d.items():
            out[k] = out.get(k, 0) + v
    return dict(sorted(out.items()))


def leitura(mecanismo_passa: bool, mvp: dict, elegivel: dict, abla: dict, pesa: dict, conserto: bool = False) -> str:
    """a tabela da secao 5.5 (a G-MOD e lida a parte); no conserto, com o G-MVP por episodio e a G-ELEGIVEL-EP (A3.3)"""
    if not mecanismo_passa:
        return "falha de implementacao (D1): o G-MECANISMO nao passa"
    if not elegivel["passa"]:
        if conserto:
            return "G-MVP (por episodio) inconclusivo por premissa (G-ELEGIVEL-EP): menos de 80 % das vidas do M3 com 3 episodios"
        return "G-MVP inconclusivo por premissa (G-ELEGIVEL): os donos quase nao deram racao com o pet com fome"
    inconclusivos = [g for g in FAMILIA_ABLA if not pesa[MODULO_DO_GATE[g]]["passa"]]
    todos = all(abla[g]["passa"] for g in FAMILIA_ABLA) and not inconclusivos
    if mvp["passa"]:
        if todos:
            return "o modular vai a comida pelos proprios modulos, e cada um pesa no sentido previsto (na pesquisa Python)"
        return ("o produto funciona na pesquisa Python; os modulos que nao pesaram vao ao diagnostico da fiacao (D2): "
                + ", ".join(g for g in FAMILIA_ABLA if not abla[g]["passa"] or g in inconclusivos))
    return "o G-MVP falha: com o oraculo passando, a aprendizagem nao chega la (D4), falha de implementacao ou de calibracao"


CELULA_DUPLICADA = ("incoerente", "comedouro")    # com o sem_ensino, a vida e byte a byte a do atencioso no comedouro (adendo 2)
CELULAS_11 = tuple(c for c in CELULAS if c != CELULA_DUPLICADA)


# ------------------------------------------------------------------ o conserto (o adendo 3)
CELULAS_LONGE = tuple(c for c in CELULAS if c[1] == "longe")
FAMILIA_DX = ("G-DX-INATO", "G-DX-INTENCAO")
BRACOS_DX = {"G-DX-INATO": ("M3", "M3-sem-inato"), "G-DX-INTENCAO": ("M3", "M3-sem-intencao")}
BRACOS_2X2 = ("M3", "M3-sem-inato", "M3-sem-intencao", "M3-420")


def _taxa_ep(r: dict):
    return r["episodios_fome"]["taxa"]


def _com_cadeia_ep(r: dict):
    return None if r["episodios_fome"]["com_cadeia"] is None else float(r["episodios_fome"]["com_cadeia"])


def _media(vs) -> float | None:
    vs = [v for v in vs if v is not None]
    return statistics.fmean(vs) if vs else None


def contrastes_dx(celulas: tuple) -> dict:
    """a familia G-DX (A3.4): M3* - M3*-inato e M3* - M3*-intencao, na taxa de fechamento por episodio de cada vida (a medida primaria de
    A3.3), a media das celulas por unidade"""
    return {n: (a, b, _taxa_ep, celulas) for n, (a, b) in BRACOS_DX.items()}


def _interacao(registros: list[dict], celulas: tuple) -> dict:
    """M3* - M3*-inato - M3*-intencao + M3-420, por unidade (os niveis, a media das celulas)"""
    a, b, c, d = (por_unidade(registros, x, None, _taxa_ep, celulas) for x in BRACOS_2X2)
    return {k: a[k] - b[k] - c[k] + d[k] for k in a if k in b and k in c and k in d}


def familia_dx(registros: list[dict], boot: dict, alfa: float, fam=None, est=contraste) -> dict:
    """a familia G-DX (secundaria, Holm com 2): a leitura principal nas celulas do longe; a de todas as celulas ao lado, com o seu Holm; a
    interacao do 2 x 2 e os quatro bracos lado a lado, descritivos. `fam` e `est`: a familia e o contraste (na reavaliacao, os de A4.4.6)"""
    fam = familia if fam is None else fam
    out = {"principal": "longe"}
    for nome, celulas in (("longe", CELULAS_LONGE), ("todas", CELULAS)):
        out[nome] = {"contrastes": fam(registros, contrastes_dx(celulas), boot, alfa),
                     "interacao": est(_interacao(registros, celulas), boot),
                     "quatro_bracos": {b: est(por_unidade(registros, b, None, _taxa_ep, celulas), boot) for b in BRACOS_2X2}}
    return out


def fracao_com_cadeia_ep(registros: list[dict], braco: str = "M3") -> dict:
    """{(base, semente): a fracao das vidas (celulas) com a cadeia por episodio}, so as vidas com episodio; e as vidas sem episodio"""
    fr = por_unidade(registros, braco, None, _com_cadeia_ep)
    sem = sum(1 for r in registros if r["braco"] == braco and r["episodios_fome"]["com_cadeia"] is None)
    return {"por_unidade": fr, "vidas_sem_episodio": sem}


def g_mvp_ep(registros: list[dict], boot: dict, cfg_ep: dict) -> dict:
    """o G-MVP por episodio (A3.3, o primario): o limite inferior do IC95 da fracao de vidas do M3* com a taxa dos episodios >= 0,5"""
    fc = fracao_com_cadeia_ep(registros)
    r = contraste(fc["por_unidade"], boot)
    return {"medida": "a fracao de vidas do M3 com a taxa de fechamento dos episodios de fome >= 0,5 (media das celulas por unidade; "
                      "A3.3)", **r, "vidas_sem_episodio": fc["vidas_sem_episodio"], "limiar": cfg_ep["limiar"],
            "passa": r["ic95"] is not None and r["ic95"]["ic_inferior"] >= cfg_ep["limiar"]}


def g_elegivel_ep(registros: list[dict], cfg_el: dict) -> dict:
    """a premissa G-ELEGIVEL-EP (A3.3): >= 80 % das vidas do M3* com 3 episodios ou mais"""
    vs = [r for r in registros if r["braco"] == "M3"]
    frac = sum(1 for r in vs if r["episodios_fome"]["n"] >= cfg_el["episodios"]) / len(vs)
    return {"frac_vidas": frac, "vidas": len(vs), "passa": frac >= cfg_el["frac_vidas"]}


def episodios_por_vida(registros: list[dict]) -> dict:
    """quantos episodios as vidas tem, por braco (A3.8: o adendo 4 traz)"""
    out = {}
    for b in sorted({r["braco"] for r in registros}):
        ns = [r["episodios_fome"]["n"] for r in registros if r["braco"] == b]
        out[b] = {"media": statistics.fmean(ns), "mediana": statistics.median(ns), "minimo": min(ns),
                  "frac_3_ou_mais": sum(1 for x in ns if x >= 3) / len(ns)}
    return out


def leitura_dx5(registros: list[dict], boot: dict, est=contraste) -> dict:
    """A DX-5 (A3.5), exploratoria, sem gate, sem Holm e sem sinal esperado: o "ganhou, fica" so nas acoes com r > 0 possivel, M2 - M1 (ao
    lado do indice de hoje, que fica no G-ABLA-P2), no total, por lugar e por acao; e o nivel de cada braco"""
    def med(acao: str | None = None):
        if acao is None:
            return lambda r: r["repeticao_r_possivel"]["total"]["indice"]
        return lambda r: r["repeticao_r_possivel"]["por_acao"][acao]["indice"]
    modulares = sorted({r["braco"] for r in registros} - {"A11"})
    return {"aviso": "exploratoria (A3.5): sem gate, sem Holm, sem sinal esperado; o G-ABLA-P2 usa o indice de hoje",
            "M2 - M1": {"total": est(por_unidade(registros, "M2", "M1", med()), boot),
                        "por_lugar": {lugar: est(por_unidade(registros, "M2", "M1", med(), tuple(c for c in CELULAS if c[1] == lugar)),
                                                       boot) for lugar in LUGARES},
                        "por_acao": {a: est(por_unidade(registros, "M2", "M1", med(a)), boot) for a in ACOES_R_POSSIVEL}},
            "indice_de_hoje, M2 - M1": est(por_unidade(registros, "M2", "M1", lambda r: r["repeticao"]["indice"]), boot),
            "nivel": {b: {"total": _media(med()(r) for r in registros if r["braco"] == b),
                          "por_acao": {a: _media(med(a)(r) for r in registros if r["braco"] == b) for a in ACOES_R_POSSIVEL}}
                      for b in modulares}}


def descritivos_conserto(registros: list[dict]) -> dict:
    """os descritivos do adendo 3, por braco e lugar (e todos os lugares): o episodio (os motivos das falhas, o estrato por d0, a oferta
    que mudou, as refeicoes fora de episodio, as latencias), a medida por racao com a W(d) e a de hoje, a racao na janela e, no modular, a
    DX-1 e o mecanismo do cheiro"""
    out = {}
    for b in sorted({r["braco"] for r in registros}):
        for lugar in LUGARES + ("todos",):
            rs = [r for r in registros if r["braco"] == b and (lugar == "todos" or r["lugar"] == lugar)]
            eps = [r["episodios_fome"] for r in rs]
            n_ep = sum(e["n"] for e in eps)
            fech = sum(e["fechados"] for e in eps)
            el_w, fe_w = sum(r["cadeia_w"]["elegiveis"] for r in rs), sum(r["cadeia_w"]["fechadas"] for r in rs)
            el, fe = sum(r["cadeia"]["elegiveis"] for r in rs), sum(r["cadeia"]["fechadas"] for r in rs)
            nj = [r["racao_na_janela"] for r in rs]
            el_j = sum(x["elegiveis"] for x in nj)
            d = {"vidas": len(rs), "episodios": n_ep, "fechados": fech, "taxa_agregada": fech / n_ep if n_ep else None,
                 "taxa_media_das_vidas": _media(e["taxa"] for e in eps), "com_cadeia_ep": _media(_com_cadeia_ep(r) for r in rs),
                 "motivos": _somar(e["motivos"] for e in eps), "oferta_mudou": sum(e["oferta_mudou"] for e in eps),
                 "fora_de_episodio": sum(e["fora_de_episodio"] for e in eps),
                 "no_episodio_sem_fechar": sum(e["no_episodio_sem_fechar"] for e in eps),
                 "latencia_media": _media(x for e in eps for x in e["latencias"]),
                 "latencia_depois_da_janela": _media(x for e in eps for x in e["latencias_depois_da_janela"]),
                 "por_d0": {s: {"n": sum(e["por_d0"][s]["n"] for e in eps), "fechados": sum(e["por_d0"][s]["fechados"] for e in eps)}
                            for s in ("ate_corte", "alem_do_corte")},
                 "por_racao_w": {"elegiveis": el_w, "fechadas": fe_w, "taxa_agregada": fe_w / el_w if el_w else None},
                 "por_racao_hoje": {"elegiveis": el, "fechadas": fe, "taxa_agregada": fe / el if el else None},
                 "racao_na_janela": {"elegiveis": el_j, "visiveis_em_k0": sum(x["visiveis_em_k0"] for x in nj),
                                     "entraram_na_visao": sum(x["entraram_na_visao"] for x in nj),
                                     "d_min_media_celulas": _media(x["d_min_media_celulas"] for x in nj)}}
            if b != "A11":
                ch = [r["cheiro"] for r in rs]
                soma = {k: sum(x[k] for x in ch) for k in ("episodios", "decisoes_comer_cheiro", "decisoes_explorar_cheiro",
                                                          "decisoes_dormir", "decisoes_nos_episodios", "achou", "compostas",
                                                          "compostas_com_refeicao", "busca_entregue_sozinha")}
                d["cheiro"] = {**soma, "fins_busca": _somar(x["fins_busca"] for x in ch),
                               "comer_cheiro_por_episodio": soma["decisoes_comer_cheiro"] / soma["episodios"] if soma["episodios"] else None,
                               "frac_achou_com_refeicao": soma["compostas_com_refeicao"] / soma["achou"] if soma["achou"] else None,
                               "sono_na_janela": (soma["decisoes_dormir"] / soma["decisoes_nos_episodios"]
                                                  if soma["decisoes_nos_episodios"] else None)}
                d["visitas"] = {"lugar_lembrado": sum(r["visitas_lugar_lembrado"] for r in rs),
                                "vazias": sum(r["visitas_vazias"] for r in rs), "vazias_v1": sum(r["visitas_vazias_v1"] for r in rs)}
            out[f"{b}|{lugar}"] = d
    return out


# ------------------------------------------------------------------ a reavaliacao por estimativa (o adendo 4: A4.2, A4.4.6, A4.6 e A4.7)
ROTULO_BOOTSTRAP = "a convencao da secao 5.2.1, anticonservadora com 5 bases (A4.4)"
POR_MEDIAS_DE_BASE = ("G-MOD-EMB",)       # A4.4.2: o M4-emb le a serie E da outra unidade da base, em anel; a base e o grupo independente
LIMIAR_G1 = -0.5                          # PROPOSTO (A4.4.6, A4.9), sem fonte externa: a forma mais branda em que o t passa do nominal
RESSALVA_G1 = "assimetria negativa: o erro do tipo I do t pode passar do nominal (A4.4.5; com g1 = -1, cerca de 1,8 vez)"
NAO_DEMONSTRA = ("a prontidao do prototipo: o G-MVP e parte do gate de prontidao (secao 5.6, ii), e sem passa esse gate nao e cumprido; "
                 "o A segue como o cerebro do MVP (A4.2)",
                 "a superioridade modular: a comparacao com o A11 (secao 7) segue descritiva; os contrastes sao entre os bracos do proprio "
                 "modular e medem modulos, nao arquiteturas (A4.2)")


def contraste_t(difs: dict, boot: dict, por_base: bool = False) -> dict:
    """o contraste da reavaliacao (A4.4.6): o p e o IC95 pelo t sobre as unidades (o t_pareado do contraste_pareado e o ic_t), ou, com
    `por_base`, pelo t sobre as medias de base (o G-MOD-EMB, A4.4.2); a assimetria g1 das diferencas por unidade e, com g1 <= LIMIAR_G1, a
    ressalva (ela nao muda o p nem a decisao); o p do bootstrap e o IC percentil ao lado, rotulados (o `contraste` de hoje, sem mudanca)"""
    b = contraste(difs, boot)
    grupos: dict = {}
    for (base, _), d in sorted(difs.items()):
        grupos.setdefault(base, []).append(d)
    valores = [d for _, d in sorted(difs.items())]
    if por_base:
        t = t_medias_de_grupo(grupos)
        teste = {"teste": "t sobre as medias de base (A4.4.2)", "p_unilateral": t["p_unilateral"], "ic95": t["ic"], "t": t["t"],
                 "gl": t["gl"], "medias_base": t["medias_grupo"], "motivo": t["motivo"]}
    else:
        ic = ic_t(valores)
        tp = b["t_pareado"]
        motivo = ic["motivo"] or b["motivo"] or (None if tp is not None else "sem variacao entre as unidades")
        teste = {"teste": "t sobre as unidades (A4.4.6)", "p_unilateral": None if tp is None else tp["p_unilateral"],
                 "ic95": {"ic_inferior": ic["ic_inferior"], "ic_superior": ic["ic_superior"], "nivel": ic["nivel"]},
                 "t": None if tp is None else tp["t"], "gl": ic["gl"], "motivo": motivo}
    g1 = assimetria_g1(valores)
    return {"n": b["n"], "n_grupos": b["n_grupos"], "media": b["media"], **teste, "g1": g1,
            "ressalva_assimetria": RESSALVA_G1 if g1 is not None and g1 <= LIMIAR_G1 else None,
            "bootstrap": {"rotulo": ROTULO_BOOTSTRAP, "p_unilateral": b["p_unilateral"], "ic95": b["ic95"], "ic90": b["ic90"],
                          "motivo": b["motivo"]}}


def familia_t(registros: list[dict], contrastes: dict, boot: dict, alfa: float) -> dict:
    """uma familia da reavaliacao (A4.4.6): o Holm de hoje (as mesmas familias, ordem e alfa) sobre o p do t; sem chave "passa" (a leitura
    e a de A4.6)"""
    out = {}
    for nome, (a, b, med, celulas) in contrastes.items():
        out[nome] = {"contraste": f"{med if isinstance(med, str) else 'medida'}({a}) - ({b})", "celulas": len(celulas),
                     **contraste_t(por_unidade(registros, a, b, med, celulas), boot, nome in POR_MEDIAS_DE_BASE)}
    h = holm({n: out[n]["p_unilateral"] for n in contrastes}, alfa)
    for n in contrastes:
        out[n]["holm"] = h[n]
    return out


def g_pesa_t(registros: list[dict], boot: dict, cfg_pesa: dict) -> dict:
    """a premissa por modulo (secao 5.3) na reavaliacao: o limite inferior do IC95 pelo t > 0,01 (A4.4.6, item 5)"""
    out = {}
    for mod, braco in cfg_pesa["bracos"].items():
        r = contraste_t(por_unidade(registros, braco, None, lambda x, mod=mod: x["influencia"][mod]), boot)
        out[mod] = {"braco": braco, **r, "passa": r["ic95"]["ic_inferior"] is not None and r["ic95"]["ic_inferior"] > cfg_pesa["limiar"]}
    return out


def posicao_do_ic(ic: dict, referencia: float) -> str | None:
    """a posicao do IC95 em relacao a referencia, numa das tres frases de A4.2 (nenhuma e aprovacao ou reprovacao)"""
    if ic["ic_inferior"] is None:
        return None
    ref = f"{referencia:g}".replace(".", ",")
    if ic["ic_inferior"] > referencia:
        return f"o IC95 inteiro acima de {ref}"
    if ic["ic_superior"] < referencia:
        return f"o IC95 inteiro abaixo de {ref}"
    return f"o IC95 contem {ref}"


def g_mvp_estimativa(fracoes: dict, boot: dict, referencia: float, medida: str) -> dict:
    """o G-MVP da reavaliacao como estimativa (A4.2): a fracao, o IC95 pelo t sobre as unidades, o IC percentil do bootstrap (descritivo) e
    a posicao do IC em relacao a referencia. Sem "passa" e sem "falha"."""
    b = contraste(fracoes, boot)
    ic = ic_t([v for _, v in sorted(fracoes.items())])
    ic95 = {"ic_inferior": ic["ic_inferior"], "ic_superior": ic["ic_superior"], "nivel": ic["nivel"]}
    return {"medida": medida, "n": ic["n"], "n_grupos": b["n_grupos"], "estimativa": ic["media"], "ic95": ic95,
            "ic95_metodo": "t sobre as unidades (A4.4.6)", "ic95_percentil": b["ic95"], "ic95_percentil_rotulo": ROTULO_BOOTSTRAP,
            "referencia": referencia, "posicao": posicao_do_ic(ic95, referencia), "motivo": ic["motivo"],
            "aviso": "estimativa, sem passa nem falha (A4.2); a referencia nao e gate"}


def _leitura_contraste(c: dict, inconclusivo: bool = False) -> str:
    if inconclusivo:
        return "inconclusivo por premissa: o modulo nao pesa (secao 5.3; A4.0)"
    if not c["holm"]["rejeita"]:
        return "o Holm nao rejeita"
    frase = "o Holm rejeita: o modulo pesa no sentido previsto dentro do M3*, nestas condicoes (A4.6)"
    if c["ressalva_assimetria"] is not None:
        frase += f"; {c['ressalva_assimetria']}: a rejeicao nao e lida como confirmacao (A4.4.6)"
    return frase


def leitura_reavaliacao(mecanismo_passa: bool, mvp_ep: dict, el_ep: dict, abla: dict, mod: dict, dx: dict, pesa: dict) -> dict:
    """a leitura de A4.6, no lugar da tabela da secao 5.5 (que condiciona o G-ABLA ao G-MVP passar, e aqui o G-MVP nao tem passa nem
    falha). O G-MECANISMO continua binario; o G-ABLA-PERS e inconclusivo por premissa qualquer que seja o p (A4.0)."""
    if not mecanismo_passa:
        return {"G-MECANISMO": "falha de implementacao (D1): o G-MECANISMO nao passa; nenhuma leitura vale"}
    inconclusivos = {g for g in FAMILIA_ABLA if g == "G-ABLA-PERS" or not pesa[MODULO_DO_GATE[g]]["passa"]}
    return {"tabela_5_5": "nao se aplica (A4.6): a leitura e esta",
            "G-MVP-EP": (f"estimativa {mvp_ep['estimativa']}, {mvp_ep['posicao']}; sem passa nem falha (A4.2)" if el_ep["passa"] else
                         "inconclusivo por premissa (G-ELEGIVEL-EP): menos de 80 % das vidas do M3 com 3 episodios"),
            "G-ABLA": {g: _leitura_contraste(abla[g], g in inconclusivos) for g in FAMILIA_ABLA},
            "G-MOD": {"contrastes": {g: _leitura_contraste(mod[g]) for g in FAMILIA_MOD},
                      "ressalva_da_familia": "o erro de familia da G-MOD fica um pouco acima de 5 % (5,9 % na nula global; A4.4.6, item 4); "
                                             "secundaria, lida a parte (secao 5.5)"},
            "G-DX": {nome: {g: _leitura_contraste(dx[nome]["contrastes"][g]) for g in FAMILIA_DX} for nome in ("longe", "todas")},
            "nao_se_le_como": "um contraste rejeitado nao se le como 'o modular vai a comida pelos proprios modulos' (exige o G-MVP passar, "
                              "secao 5.5) nem como superioridade da arquitetura (A4.6)",
            "nao_demonstra": list(NAO_DEMONSTRA)}


def analisar_conserto(registros: list[dict], cfg: dict, mecanismo_passa: bool = True) -> dict:
    """a reavaliacao (o adendo 3; o adendo 4, a estimativa): o G-MVP por episodio (o primario, A3.3) e o por racao (o secundario
    obrigatorio) como estimativas com IC, sem "passa" (A4.2); as familias G-ABLA, G-MOD e G-DX com o Holm sobre o p do t (o G-MOD-EMB pelas
    medias de base), o g1 e a ressalva (A4.4.6); a G-PESA com o IC t; as premissas de elegibilidade; a DX-5 (A3.5, exploratoria), os
    descritivos e o A11 so na comparacao descritiva, com os IC de A4.4; e a leitura de A4.6 no lugar da tabela da secao 5.5"""
    boot, alfa = cfg["bootstrap"], cfg["holm"]["alfa"]
    pesa = g_pesa_t(registros, boot, cfg["g_pesa"])
    abla = familia_t(registros, CONTRASTES_ABLA, boot, alfa)
    for g in FAMILIA_ABLA:
        abla[g]["premissa_g_pesa"] = pesa[MODULO_DO_GATE[g]]["passa"]
    mod = familia_t(registros, CONTRASTES_MOD, boot, alfa)
    dx = familia_dx(registros, boot, alfa, fam=familia_t, est=contraste_t)
    fc_ep, fc = fracao_com_cadeia_ep(registros), fracao_com_cadeia(registros)
    mvp_ep = {**g_mvp_estimativa(fc_ep["por_unidade"], boot, cfg["g_mvp_ep"]["limiar"],
                                 "a fracao de vidas do M3 com a taxa de fechamento dos episodios de fome >= 0,5 (media das celulas por "
                                 "unidade; A3.3)"), "vidas_sem_episodio": fc_ep["vidas_sem_episodio"]}
    mvp = {**g_mvp_estimativa(fc["por_unidade"], boot, cfg["g_mvp"]["limiar"],
                              "a fracao de vidas do M3 com a taxa de fechamento >= 0,5 (media das celulas por unidade)"),
           "vidas_sem_elegivel": fc["vidas_sem_elegivel"],
           "papel": "secundaria obrigatoria (A3.3): o G-MVP pre-registrado, por racao, como estimativa (A4.2)"}
    el_ep, el = g_elegivel_ep(registros, cfg["g_elegivel_ep"]), g_elegivel(registros, cfg["g_elegivel"])
    d11 = descritivo_11_celulas(registros, cfg, est=contraste_t)
    d11["G-MVP-EP"] = contraste_t(por_unidade(registros, "M3", None, _com_cadeia_ep, CELULAS_11), boot)
    out = {"pergunta": "estimativa (A4.1): quanto o prototipo fecha, com que incerteza", "primaria": "G-MVP-EP", "G-MVP-EP": mvp_ep,
           "G-ELEGIVEL-EP": el_ep, "G-MVP": mvp, "G-ELEGIVEL": el, "G-ABLA": abla, "G-PESA": pesa, "G-MOD": mod, "G-DX": dx,
           "holm_alfa": alfa,
           "metodo": {"holm": "o p do t sobre as unidades; no G-MOD-EMB, o do t sobre as medias de base (A4.4.6)",
                      "ic95": "pelo t (A4.4.6); o percentil do bootstrap ao lado, descritivo", "bootstrap": ROTULO_BOOTSTRAP,
                      "limiar_g1": LIMIAR_G1, "ressalva_g1": RESSALVA_G1},
           "leitura": leitura_reavaliacao(mecanismo_passa, mvp_ep, el_ep, abla, mod, dx, pesa),
           "D-2": leitura_d2(registros, boot, est=contraste_t), "D-1": leitura_d1(registros, boot, est=contraste_t),
           "DX-5": leitura_dx5(registros, boot, est=contraste_t), "episodios_por_vida": episodios_por_vida(registros),
           "descritivos": descritivos(registros), "descritivos_conserto": descritivos_conserto(registros), "descritivo_11_celulas": d11}
    if any(r["braco"] == "A11" for r in registros):
        out["comparacao_com_o_a"] = comparacao_com_o_a(registros, boot, conserto=True, est=contraste_t)
    return out


def descritivo_11_celulas(registros: list[dict], cfg: dict, est=contraste) -> dict:
    """a leitura com 11 celulas, sem a duplicata do comedouro (a decisao do Matheus no fim do adendo 2): os mesmos contrastes, premissas e
    a fracao do G-MVP sobre as mesmas vidas, so sem a celula incoerente/comedouro. So descritiva: sem Holm, sem "passa", sem gate."""
    boot = cfg["bootstrap"]
    fc = por_unidade(registros, "M3", None, lambda r: None if r["com_cadeia"] is None else float(r["com_cadeia"]), CELULAS_11)
    contrastes = {}
    for nome, (a, b, med, celulas) in {**CONTRASTES_ABLA, **CONTRASTES_MOD}.items():
        cs = tuple(c for c in celulas if c != CELULA_DUPLICADA)
        por_base = {"por_base": True} if est is not contraste and nome in POR_MEDIAS_DE_BASE else {}     # o G-MOD-EMB (A4.4.2)
        contrastes[nome] = {"celulas": len(cs), **est(por_unidade(registros, a, b, med, cs), boot, **por_base)}
    pesa = {mod: {"braco": braco, **est(por_unidade(registros, braco, None, lambda x, mod=mod: x["influencia"][mod], CELULAS_11), boot)}
            for mod, braco in cfg["g_pesa"]["bracos"].items()}
    m3 = [r for r in registros if r["braco"] == "M3" and (r["dono"], r["lugar"]) != CELULA_DUPLICADA]
    return {"aviso": "descritivo, sem gate: a analise principal e a das 12 celulas (decisao do Matheus, 2026-10-26)",
            "fora": list(CELULA_DUPLICADA), "celulas": len(CELULAS_11), "G-MVP": est(fc, boot), "contrastes": contrastes,
            "G-PESA": pesa, "G-ELEGIVEL": {"frac_vidas": sum(1 for r in m3 if r["cadeia"]["elegiveis"] >= cfg["g_elegivel"]["racoes"])
                                                         / len(m3), "vidas": len(m3)}}


def analisar(registros: list[dict], cfg: dict, mecanismo_passa: bool = True, conserto: bool = False) -> dict:
    """a avaliacao (secao 5): os gates, as premissas e as leituras; o A11, se veio, so descritivo. Com `conserto` (a reavaliacao, o
    adendo 3): o G-MVP por episodio como o primario, o G-MVP e a G-ELEGIVEL de hoje como secundarios obrigatorios, a familia G-DX, a DX-5
    e os descritivos do conserto"""
    if conserto:
        return analisar_conserto(registros, cfg, mecanismo_passa)
    boot, alfa = cfg["bootstrap"], cfg["holm"]["alfa"]
    abla = familia(registros, CONTRASTES_ABLA, boot, alfa)
    pesa = g_pesa(registros, boot, cfg["g_pesa"])
    for g in FAMILIA_ABLA:
        abla[g]["premissa_g_pesa"] = pesa[MODULO_DO_GATE[g]]["passa"]
        abla[g]["leitura"] = ("inconclusivo por premissa: o modulo nao pesa" if not abla[g]["premissa_g_pesa"]
                              else ("passa" if abla[g]["passa"] else "nao passa"))
    mod = familia(registros, CONTRASTES_MOD, boot, alfa)
    mvp, el = g_mvp(registros, boot, cfg["g_mvp"]), g_elegivel(registros, cfg["g_elegivel"])
    out = {"G-MVP": mvp, "G-ELEGIVEL": el, "G-ABLA": abla, "G-PESA": pesa, "G-MOD": mod, "holm_alfa": alfa,
           "leitura": leitura(mecanismo_passa, mvp, el, abla, pesa), "D-2": leitura_d2(registros, boot), "D-1": leitura_d1(registros, boot),
           "descritivos": descritivos(registros), "descritivo_11_celulas": descritivo_11_celulas(registros, cfg)}
    if any(r["braco"] == "A11" for r in registros):
        out["comparacao_com_o_a"] = comparacao_com_o_a(registros, boot)
    return out


# ------------------------------------------------------------------ o piloto: o poder e o K (secao 6.3)
def _p_bootstrap(somas: list[float], contagens: list[int], reamostragens: int, rng: random.Random) -> float:
    """o p unilateral do bootstrap agrupado por base (a conta do `contraste_pareado`, pela soma e a contagem de cada base): a fracao das
    medias reamostradas <= 0"""
    n = len(somas)
    abaixo = 0
    for _ in range(reamostragens):
        s, c = 0.0, 0
        for _ in range(n):
            i = rng.randrange(n)
            s += somas[i]
            c += contagens[i]
        abaixo += s / c <= 0.0
    return abaixo / reamostragens


def _ic_inferior(somas: list[float], contagens: list[int], reamostragens: int, rng: random.Random) -> float:
    n = len(somas)
    medias = []
    for _ in range(reamostragens):
        s, c = 0.0, 0
        for _ in range(n):
            i = rng.randrange(n)
            s += somas[i]
            c += contagens[i]
        medias.append(s / c)
    return ic_percentil(medias, 0.95)[0]


def poder_por_k(unidades: list[dict], planos: dict, k: int, poder: dict, alfas: dict, mvp_plano: float | None) -> dict:
    """o poder de cada contraste num K (secao 6.3): `unidades` = [{contraste: a diferenca da unidade}], cada diferenca centrada e
    deslocada para o efeito de planejamento dela (as diferencas da mesma unidade juntas, a correlacao fica); K x n_bases unidades por
    replica, divididas em n_bases bases de K; o teste da replica e o p unilateral do bootstrap agrupado por base (as reamostragens
    internas); o poder e a fracao das replicas com p <= alfa. O G-MVP: o limite inferior do IC95 >= o limiar."""
    rng = random.Random(derivar_semente("poder-digibrain", poder["semente"], k))
    medias = {c: statistics.fmean(u[c] for u in unidades if u.get(c) is not None) for c in planos}
    n_bases = poder["n_bases"]
    acertos = {c: 0 for c in planos}
    acertos_mvp, conjunto = 0, 0
    for _ in range(poder["replicas"]):
        sorteadas = [unidades[rng.randrange(len(unidades))] for _ in range(k * n_bases)]
        rejeita = {}
        for c, efeito in planos.items():
            somas, cont = [], []
            for b in range(n_bases):
                vs = [u[c] - medias[c] + efeito for u in sorteadas[b * k:(b + 1) * k] if u.get(c) is not None]
                if vs:
                    somas.append(sum(vs))
                    cont.append(len(vs))
            p = _p_bootstrap(somas, cont, poder["reamostragens_internas"], rng) if len(somas) >= 2 else 1.0
            rejeita[c] = p <= alfas[c]
            acertos[c] += rejeita[c]
        conjunto += all(rejeita[c] for c in planos if c in FAMILIA_ABLA)
        if mvp_plano is not None:
            somas, cont = [], []
            media_mvp = statistics.fmean(u["G-MVP"] for u in unidades)
            for b in range(n_bases):
                vs = [u["G-MVP"] - media_mvp + mvp_plano for u in sorteadas[b * k:(b + 1) * k]]
                somas.append(sum(vs))
                cont.append(len(vs))
            acertos_mvp += _ic_inferior(somas, cont, poder["reamostragens_internas"], rng) >= G_MVP["limiar"]
    r = poder["replicas"]
    return {"k": k, "n": k * n_bases, "poder": {c: acertos[c] / r for c in planos},
            "poder_mvp": None if mvp_plano is None else acertos_mvp / r, "poder_conjunto_abla": conjunto / r}


def analisar_piloto(registros: list[dict], cfg: dict, conserto: bool = False) -> dict:
    """o piloto (secoes 6.2 e 6.3): os contrastes so como relato, as premissas, a media do g_apr do M4 (o valor do M4-con), o K pelo poder
    e o custo. Nenhum numero dele e evidencia. Com `conserto` (o piloto do conserto, A3.8): o G-MVP por episodio no lugar do de hoje no
    poder, a familia G-DX no relato e no poder (fora da conta do K), quantos episodios as vidas tem, os motivos das falhas e o A11 so na
    comparacao descritiva."""
    a11 = [r for r in registros if r["braco"] == "A11"]
    registros = [r for r in registros if r["braco"] != "A11"]
    boot, poder = cfg["bootstrap"], cfg["poder"]
    abla = familia(registros, CONTRASTES_ABLA, boot, cfg["holm"]["alfa"])
    mod = familia(registros, CONTRASTES_MOD, boot, cfg["holm"]["alfa"])
    contrastes = {**CONTRASTES_ABLA, **CONTRASTES_MOD, **(contrastes_dx(CELULAS_LONGE) if conserto else {})}
    difs = {n: por_unidade(registros, a, b, med, cel) for n, (a, b, med, cel) in contrastes.items()}
    fc = (fracao_com_cadeia_ep if conserto else fracao_com_cadeia)(registros)["por_unidade"]
    chaves = sorted({k for d in difs.values() for k in d} | set(fc))
    unidades = [{**{n: difs[n].get(k) for n in difs}, "G-MVP": fc.get(k)} for k in chaves]
    planos, fora = {}, {}
    for n in FAMILIA_ABLA + FAMILIA_MOD + (FAMILIA_DX if conserto else ()):
        vs = [v for v in difs[n].values()]
        if not vs:
            fora[n] = "sem valor no piloto"
            continue
        efeito = statistics.fmean(vs) / 2
        if efeito <= 0:
            fora[n] = "o efeito do piloto tem o sinal contrario ao previsto (ou e 0): fora da conta do K"
            continue
        planos[n] = efeito
    mvp_frac = statistics.fmean(v for v in fc.values()) if fc else None
    mvp_plano = None if mvp_frac is None or mvp_frac <= G_MVP["limiar"] else G_MVP["limiar"] + (mvp_frac - G_MVP["limiar"]) / 2
    alfas = {n: poder["alfa_abla"] if n in FAMILIA_ABLA else poder["alfa_mod"] for n in planos}
    unidades_com_mvp = [u for u in unidades if u["G-MVP"] is not None] if mvp_plano is not None else unidades
    tabela = [poder_por_k(unidades_com_mvp, planos, k, poder, alfas, mvp_plano) for k in range(poder["k_min"], poder["k_max"] + 1)]
    no_k = [c for c in planos if c in FAMILIA_ABLA]

    def chega(t):
        return all(t["poder"][c] >= poder["alvo"] for c in no_k) and (t["poder_mvp"] is None or t["poder_mvp"] >= poder["alvo"])
    escolhido = next((t for t in tabela if chega(t)), tabela[-1])
    m4 = [r["g_apr_media"] for r in registros if r["braco"] == "M4"]
    out = {"contrastes_so_relato": {"G-ABLA": abla, "G-MOD": mod}, "premissas": {"G-PESA": g_pesa(registros, boot, cfg["g_pesa"]),
                                                                             "G-ELEGIVEL": g_elegivel(registros, cfg["g_elegivel"])},
           "G-MVP_piloto": {"fracao": mvp_frac, "plano": mvp_plano, "fora_do_k": mvp_plano is None},
           "n": {"k": escolhido["k"], "chega_ao_alvo": chega(escolhido), "planos": planos, "fora_do_k": fora, "tabela": tabela},
           "g_apr_m4": {"media": statistics.fmean(m4) if m4 else None, "m4_con": round(statistics.fmean(m4)) if m4 else None},
           "descritivos": descritivos(registros),
           "aviso": "o piloto serve so para o efeito, as premissas, o valor do M4-con, o K e o custo (secao 6.2): nenhum numero e evidencia"}
    if conserto:
        out["contrastes_so_relato"]["G-DX"] = familia_dx(registros, boot, cfg["holm"]["alfa"])
        out["premissas"]["G-ELEGIVEL-EP"] = g_elegivel_ep(registros, cfg["g_elegivel_ep"])
        out["premissas"]["episodios_por_vida"] = episodios_por_vida(registros)
        out["G-MVP_piloto"]["medida"] = "por episodio (A3.3), a primaria do conserto"
        out["G-MVP_racao_piloto"] = {"fracao": statistics.fmean(fracao_com_cadeia(registros)["por_unidade"].values())
                                     if fracao_com_cadeia(registros)["por_unidade"] else None}
        out["descritivos_conserto"] = descritivos_conserto(registros + a11)
        out["DX-5"] = leitura_dx5(registros, boot)
        if a11:
            out["comparacao_com_o_a"] = comparacao_com_o_a(registros + a11, boot, conserto=True)
    return out


def analisar_calibracao(registros: list[dict], cfg: dict, conserto: bool = False) -> dict:
    """a calibracao (secao 6.1), so o M3: o T-CADEIA-1 (o oraculo, conferido pelo teste), a taxa de fechamento na mediana das vidas >= 0,5,
    nenhum H no teto e a G-PESA de cada modulo do M3 com a fracao >= 0,01. Com `conserto` (A3.8), a taxa e a do episodio (A3.3)."""
    vs = [r for r in registros if r["braco"] == "M3"]
    taxas = [(r["episodios_fome"] if conserto else r["cadeia"])["taxa"] for r in vs]
    taxas = [x for x in taxas if x is not None]
    mediana = statistics.median(taxas) if taxas else None
    teto = max(r["pesos_no_teto"] for r in vs)
    pesa = {m: statistics.fmean(r["influencia"][m] for r in vs) for m in ("incentivo", "habito", "memoria", "persistencia")}
    criterios = {"taxa_mediana": {"valor": mediana, "passa": mediana is not None and mediana >= 0.5},
                 "pesos_no_teto": {"valor": teto, "passa": teto == 0},
                 "g_pesa": {m: {"valor": v, "passa": v >= cfg["g_pesa"]["limiar"]} for m, v in pesa.items()}}
    fecha = criterios["taxa_mediana"]["passa"] and criterios["pesos_no_teto"]["passa"] and all(x["passa"] for x in criterios["g_pesa"].values())
    out = {"rodada": cfg.get("rodada"), "criterios": criterios, "fecha": fecha, "descritivos": descritivos(registros),
           "aviso": "o T-CADEIA-1 e conferido por tests/test_digibrain_vidas.py antes da run; os bracos da ablacao nao sao olhados"}
    if conserto:
        out["criterios"]["taxa_mediana"]["medida"] = "a taxa de fechamento por episodio (A3.3)"
        out["descritivos_conserto"] = descritivos_conserto(registros)
    return out


def custo(registros: list[dict], k: int | None, n_bases: int, n_bracos: int = len(BRACOS)) -> dict:
    por = {b: statistics.fmean(r["custo"]["vida_cpu"] for r in registros if r["braco"] == b) for b in sorted({r["braco"] for r in registros})}
    por_unidade_cpu = sum(por.values()) * len(CELULAS)
    return {"cpu_por_vida": por, "cpu_por_unidade": por_unidade_cpu,
            "avaliacao_estimada": None if k is None else {"k": k, "vidas": n_bases * k * len(CELULAS) * n_bracos,
                                                         "cpu_s": n_bases * k * por_unidade_cpu * n_bracos / max(1, len(por))}}


# ================================================================== a run
def rodar(cfg: dict, pasta: Path, processos: int, caminho_config: Path | None = None) -> dict:
    modo = modo_da_config(cfg)
    fase = cfg["fase"]
    if pasta.exists():
        raise FileExistsError(f"{pasta} ja existe: a run se recusa a gravar por cima (secao 6.4)")
    unidades = bv.unidades_derivadas(cfg["unidades"]["bases"], int(cfg["unidades"]["k"]), PREFIXO)
    pasta.mkdir(parents=True)
    inicio = time.time()
    meta = {"modo": modo, "fase": fase, "plano": PLANO, "plano_sha256": rc._sha_arquivo(RAIZ / PLANO), "config": cfg,
            "config_arquivo": None if caminho_config is None else rc._relativo(caminho_config),
            "config_sha256": None if caminho_config is None else rc._sha_arquivo(caminho_config),
            "orquestrador_sha256": rc._sha_arquivo(Path(__file__)), "git_head": rc._git("rev-parse", "HEAD"),
            "git_limpo": rc._git("status", "--porcelain") == "", "processos": processos, "unidades": unidades,
            "bracos": {b: (None if b == "A11" else (SUBCHAVES_CONSERTO if fase in FASES_CONSERTO else SUBCHAVES)[b])
                       for b in BRACOS_DA_FASE[fase]},
            "inatos": json.loads(json.dumps(inatos_da_config(cfg).__dict__)),
            "sha256": {n: rc._sha_arquivo(RAIZ / "digilab" / n) for n in ("config.py", "engine.py", "metrics.py")}
            | {f"digibrain/{p.name}": rc._sha_arquivo(p) for p in sorted((RAIZ / "digilab" / "digibrain").glob("*.py"))},
            "inicio": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(inicio))}
    g_apr_con = None
    if fase == "avaliacao" and modo == "avaliacao":
        ad = adendo_do_piloto()
        g_apr_con = ad["g_apr_m4_con"]
        meta["adendo_2"] = ad
        meta["piloto_resultado_sha256"] = rc._sha_arquivo(RAIZ / SAIDA["piloto"] / "resultado.json")
    if fase == "reavaliacao" and modo == "reavaliacao":
        ad = adendo_do_piloto_conserto()
        g_apr_con = ad["g_apr_m4_con"]
        meta["adendo_4"] = ad
        meta["piloto_resultado_sha256"] = rc._sha_arquivo(RAIZ / SAIDA["piloto_conserto"] / "resultado.json")
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    t0 = time.perf_counter()
    primeira = tuple(b for b in BRACOS_DA_FASE[fase] if b not in SEGUNDA_PASSADA)
    saidas = rc._executar([(tarefa_primeira, (cfg, u, str(pasta), primeira)) for u in unidades], processos)
    registros = [r for s in saidas for r in s]
    if any(b in BRACOS_DA_FASE[fase] for b in SEGUNDA_PASSADA):
        series = {(r["semente"], r["dono"], r["lugar"]): r["serie_e"] for r in registros if r["braco"] == "M4"}
        if g_apr_con is None:                       # o piloto e a fumaca: a media do g_apr das vidas M4 da propria run
            g_apr_con = round(statistics.fmean(r["g_apr_media"] for r in registros if r["braco"] == "M4"))
        meta["g_apr_m4_con"] = g_apr_con
        doa = doadores(unidades)
        tarefas = [(tarefa_segunda, (cfg, u, str(pasta), {(d, lugar): series[(doa[u["semente"]], d, lugar)] for d, lugar in CELULAS},
                                     g_apr_con)) for u in unidades]
        registros += [r for s in rc._executar(tarefas, processos) for r in s]
    for r in registros:
        r.pop("serie_e", None)
    meta["vidas_parede_s"] = time.perf_counter() - t0
    n_bases = len(cfg["unidades"]["bases"])
    conserto = fase in FASES_CONSERTO
    if fase in FASES_CALIBRACAO:
        resultado = {"modo": modo, "fase": fase, "plano": PLANO, **analisar_calibracao(registros, cfg, conserto)}
    elif fase in ("piloto", "piloto_conserto"):
        resultado = {"modo": modo, "fase": fase, "plano": PLANO, **analisar_piloto(registros, cfg, conserto)}
        if conserto:
            resultado["custo"] = custo(registros, resultado["n"]["k"], len(BASES["reavaliacao"]), len(BRACOS_CONSERTO))
        else:
            resultado["custo"] = custo(registros, resultado["n"]["k"], len(BASES["avaliacao"]))
    else:
        resultado = {"modo": modo, "fase": fase, "plano": PLANO, **analisar(registros, cfg, conserto=conserto),
                     "custo": custo(registros, None, n_bases, len(BRACOS_DA_FASE[fase]))}
    meta["fim"] = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
    meta["duracao_s"] = time.time() - inicio
    meta["python"] = platform.python_version()
    bv._gravar(pasta / "medidas.json", bv._dump({r["vida"]: r for r in sorted(registros, key=lambda r: r["vida"])}))
    bv._gravar(pasta / "resultado.json", bv._dump(resultado))
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    return {"meta": meta, "registros": registros, "resultado": resultado}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--config", required=True)
    ap.add_argument("--saida", default=None)
    ap.add_argument("--processos", type=int, default=1)
    a = ap.parse_args()
    caminho = Path(a.config)
    cfg = json.loads(caminho.read_text(encoding="utf-8"))
    modo = modo_da_config(cfg)
    if modo == "fumaca" and a.saida is None:
        raise SystemExit("a fumaca precisa de --saida (fora de artifacts_v2_digibrain_prototipo/)")
    saida = Path(a.saida) if a.saida else RAIZ / SAIDA[cfg["fase"]]
    if cfg["fase"] in FASES_CALIBRACAO and a.saida is None:
        saida = saida / f"rodada_{cfg['rodada']}"
    r = rodar(cfg, saida, a.processos, caminho)["resultado"]
    print(json.dumps({k: v for k, v in r.items() if k not in ("descritivos", "D-1", "D-2")}, indent=1, ensure_ascii=False,
                     default=str)[:4000])


if __name__ == "__main__":
    main()
