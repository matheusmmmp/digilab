"""V2, K4-DONO-JULGA-FRUTA (docs/TAREFA_V2_K4_DONO_JULGA_FRUTA.md; contrato K4 e decisao E7 de docs/PLANO_ANALISE_V2_EXPERIMENTO_MAIOR.md,
secao 1; decisao K-11 de docs/PLANO_CALIBRACAO_CONJUNTA_V2.md): o dono do P3 julga a escolha de fruta pelo efeito real vigente.

Gates: a vida de hoje byte a byte (gabarito gravado ANTES da mudanca, num commit proprio); G1 com o julgamento; o julgamento segue o efeito
real vigente (tambem dos dois lados da troca do mutavel), um por consumo, no passo seguinte; o P2 e o P3 da mesma unidade conhecem o mesmo
efeito.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
from digilab.config import CONFIG_FRUTAS_LIGADA, CONFIG_INFORMACAO_LIGADA, CONFIG_LOBOS_APRENDIZ, CONFIG_PEDIDO_LIGADA  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.frutas import (DonoInformante, DonoPedinte, OfertasFrutas, PoliticaInstintoFrutas, fabricas_frutas,  # noqa: E402
                            simular_vida_frutas)
from digilab.policies.lobos import PoliticaLobos  # noqa: E402

GABARITO = RAIZ / "tests" / "gabaritos" / "k4_vidas_de_hoje.json"
DONOS = ("atencioso", "relapso", "aleatorio", "incoerente")
MUNDOS = ("casado_frutas", "descasado", "mutavel")
BRACOS = ("P0", "P1", "P2", "P3")
SEMENTES_BANCADA = (101, 202)                 # so dos testes
SEMENTES = (11, 22, 33)
BANCADA = bv.Bancada(4, 64)
CF, CI, CP = CONFIG_FRUTAS_LIGADA, CONFIG_INFORMACAO_LIGADA, CONFIG_PEDIDO_LIGADA
CEREBROS = {
    "instinto": lambda cfg=None: PoliticaInstintoFrutas(cfg, None, CF),
    "lobos": lambda cfg=None: PoliticaLobos(cfg, CONFIG_LOBOS_APRENDIZ, None, CF),
}


def _sha(texto: str) -> str:
    return hashlib.sha256(texto.encode()).hexdigest()


def _impressao(motor) -> dict:
    """o que tem de ficar igual: log, estado final, estado() do motor, acoes, rngs, frutas e o estado interno da politica"""
    return {
        "log": _sha(motor.log.para_jsonl()),
        "estado": _sha(repr(motor._estado)),
        "estado_motor": _sha(json.dumps(motor.estado(), sort_keys=True, default=repr)),
        "acoes": _sha(repr(motor.acoes_recentes(10**9))),
        "rngs": _sha(repr((motor._rng_politica.getstate(), motor._rng_ambiente.getstate(), motor._rng_fruta.getstate()))),
        "frutas": _sha(json.dumps(motor.resumo_frutas(), sort_keys=True, default=repr)),
        "politica": _sha(json.dumps(motor.politica.estado_interno(), sort_keys=True, default=repr)),
    }


def _vida_frutas_de_hoje(cerebro: str, extra: str, dono: str, s: int):
    """a vida pelo simular_vida_frutas de hoje: sem nada, com o informante do N5 ou com o dono que pede do N7 (com bronca)"""
    kw = {"cfg_informacao": CI} if extra == "informa" else {"cfg_pedido": CP} if extra == "pede" else {}
    fp, fm = fabricas_frutas(cfg_frutas=CF, politica_fabrica=CEREBROS[cerebro], **kw)
    inf = DonoInformante.do_genoma("certo", s, CF) if extra == "informa" else None
    ped = DonoPedinte.da_semente(s, CP, bronca=True) if extra == "pede" else None
    return simular_vida_frutas(f"{dono}-k4", criar_dono(dono), fp(), s, 3, 48, fm, OfertasFrutas(CF), rotulo_dono=dono,
                               informante=inf, pedinte=ped)


def _casos():
    for mundo in MUNDOS:
        for braco in BRACOS:
            for dono in DONOS:
                for s in SEMENTES_BANCADA:
                    yield f"bancada|{mundo}|{braco}|{dono}|{s}", ("bancada", bv.EspecVida(dono, braco, s, None, mundo, "lobos"))
    for cerebro in CEREBROS:
        for extra in ("sem", "informa", "pede"):
            for dono in DONOS:
                for s in SEMENTES:
                    yield f"frutas|{cerebro}|{extra}|{dono}|{s}", ("frutas", (cerebro, extra, dono, s))


def _vida_de_hoje(tipo, caso):
    if tipo == "bancada":
        return BANCADA.vida(caso).motor
    return _vida_frutas_de_hoje(*caso).motor


def gerar_gabarito() -> dict:
    return {chave: _impressao(_vida_de_hoje(*caso)) for chave, caso in _casos()}
