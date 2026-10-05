"""V2, N7-MUNDO (docs/TAREFA_V2_N7_MUNDO.md; docs/PLANO_ANALISE_V2_N7.md, decisoes N7-1, N7-6, N7-7, N7-8): o pedido "deixe a fruta X".

O pedido e um evento novo (`pedir_deixar_fruta_<f>`), separado da informacao do N5, fora do orcamento e sem mexer no estado; a percepcao e
`Observacao.pedido_frutas` (-1 na fruta com pedido vigente), injetada so pelo MotorFrutas com ConfigPedido ligada. O `DonoPedinte` sorteia
a fruta X por vida (rng propria `pedido-fruta`, independente da preferencia inata), pede logo depois de cada oferta que tem X nos dias 1-10
(extincao nos dias 11-14) e, so no braco P3+ped, da a bronca (`repreender`) no primeiro passo do dono depois de o pet comer X com pedido
vigente, fora do orcamento.
Gates: G2 (sem pedido no log = a vida de hoje, byte a byte, contra o gabarito gravado ANTES da mudanca; mais as 168 vidas da bancada de
tests/test_frutas_cenario.py); G1; o pedido nao altera o estado nem o orcamento; as fases e o sorteio da fruta; a rng do pedido nao mexe
nas outras.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.config import CONFIG_FRUTAS_LIGADA, CONFIG_INFORMACAO_LIGADA, CONFIG_LOBOS_APRENDIZ  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.frutas import DonoInformante, OfertasFrutas, PoliticaInstintoFrutas, fabricas_frutas, simular_vida_frutas  # noqa: E402
from digilab.policies.lobos import PoliticaLobos  # noqa: E402

GABARITO = RAIZ / "tests" / "gabaritos" / "n7_vidas_de_hoje.json"
DONOS = ("atencioso", "relapso", "aleatorio", "incoerente")
SEMENTES = (11, 22, 33)                       # so dos testes
DIAS, ORC = 3, 48
CF, CI = CONFIG_FRUTAS_LIGADA, CONFIG_INFORMACAO_LIGADA
CEREBROS = {
    "instinto": lambda cfg=None: PoliticaInstintoFrutas(cfg, None, CF),
    "lobos": lambda cfg=None: PoliticaLobos(cfg, CONFIG_LOBOS_APRENDIZ, None, CF),     # aprendendo com o dono (P3 que ve as frutas)
}


def _sha(texto: str) -> str:
    return hashlib.sha256(texto.encode()).hexdigest()


def _impressao(motor) -> dict:
    """o que tem de ficar igual: log, estado final, estado() do motor, ultimas acoes, rngs, frutas e o estado interno da politica"""
    return {
        "log": _sha(motor.log.para_jsonl()),
        "estado": _sha(repr(motor._estado)),
        "estado_motor": _sha(json.dumps(motor.estado(), sort_keys=True, default=repr)),
        "acoes": _sha(repr(motor.acoes_recentes(10**9))),
        "rngs": _sha(repr((motor._rng_politica.getstate(), motor._rng_ambiente.getstate(), motor._rng_fruta.getstate()))),
        "frutas": _sha(json.dumps(motor.resumo_frutas(), sort_keys=True, default=repr)),
        "politica": _sha(json.dumps(motor.politica.estado_interno(), sort_keys=True, default=repr)),
    }


def _vida_de_hoje(cerebro: str, informa: bool, dono: str, s: int, **kw):
    fp, fm = fabricas_frutas(cfg_frutas=CF, cfg_informacao=CI if informa else None, politica_fabrica=CEREBROS[cerebro], **kw)
    inf = DonoInformante.do_genoma("certo", s, CF) if informa else None
    v = simular_vida_frutas(f"{dono}-n7", criar_dono(dono), fp(), s, DIAS, ORC, fm, OfertasFrutas(CF), rotulo_dono=dono, informante=inf)
    return v, fp, fm


def _casos():
    for cerebro in CEREBROS:
        for informa in (False, True):
            for dono in DONOS:
                for s in SEMENTES:
                    yield f"{cerebro}|{'informa' if informa else 'sem'}|{dono}|{s}", (cerebro, informa, dono, s)


def gerar_gabarito() -> dict:
    return {chave: _impressao(_vida_de_hoje(*caso)[0].motor) for chave, caso in _casos()}
