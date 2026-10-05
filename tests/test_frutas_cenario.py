"""V2, FRUTA-NO-CENARIO, parte A (docs/TAREFA_V2_FRUTA_NO_CENARIO.md; decisao R2): `Observacao.frutas_cenario`, a presenca de cada fruta.

O campo novo so e preenchido pelo MotorFrutas com as frutas ligadas, na ordem de events.FRUTAS (1.0 presente, 0.0 ausente), com as mesmas
frutas que a sub-decisao de comer considera. Ninguem o le ainda (a decisao de comer que o le e a parte B, do chat B).
Gates: G2, nenhuma vida de hoje muda (gabarito gravado com o codigo da main ANTES do campo: os bracos P0 a P3 da bancada nos tres mundos
das frutas); G1 com o campo; a presenca certa a cada decisao.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
from digilab.config import CONFIG_FRUTAS, CONFIG_FRUTAS_LIGADA, CONFIG_INFORMACAO_LIGADA  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.events import FRUTAS, LogDeEventos  # noqa: E402
from digilab.frutas import DonoInformante, MotorFrutas, OfertasFrutas, fabricas_frutas, reproduzir_frutas, simular_vida_frutas  # noqa: E402
from digilab.policy import Observacao  # noqa: E402

GABARITO = RAIZ / "tests" / "gabaritos" / "frutas_cenario_vidas_de_hoje.json"
DONOS = ("atencioso", "relapso", "aleatorio", "incoerente")
MUNDOS = ("casado_frutas", "descasado", "mutavel")
BRACOS = (("P0", "lobos"), ("P0", "instinto"), ("P1", "lobos"), ("P2", "lobos"), ("P2e", "lobos"), ("P2a", "lobos"), ("P3", "lobos"))
SEMENTES = (101, 202)                       # so dos testes
BANCADA = bv.Bancada(4, 64)
CF, CI = CONFIG_FRUTAS_LIGADA, CONFIG_INFORMACAO_LIGADA


def _sha(texto: str) -> str:
    return hashlib.sha256(texto.encode()).hexdigest()


def _impressao(motor) -> dict:
    """o que tem de ficar igual: log, estado final, ultimas acoes, rngs, frutas e o estado interno da politica"""
    return {
        "log": _sha(motor.log.para_jsonl()),
        "estado": _sha(repr(motor._estado)),
        "acoes": _sha(repr(motor.acoes_recentes(10**9))),
        "rngs": _sha(repr((motor._rng_politica.getstate(), motor._rng_ambiente.getstate(), motor._rng_fruta.getstate()))),
        "frutas": _sha(json.dumps(motor.resumo_frutas(), sort_keys=True, default=repr)),
        "politica": _sha(json.dumps(motor.politica.estado_interno(), sort_keys=True, default=repr)),
    }


def _casos():
    for mundo in MUNDOS:
        for braco, cerebro in BRACOS:
            for dono in DONOS:
                for s in SEMENTES:
                    yield f"{mundo}|{braco}|{cerebro}|{dono}|{s}", bv.EspecVida(dono, braco, s, None, mundo, cerebro)


def gerar_gabarito() -> dict:
    return {chave: _impressao(BANCADA.vida(espec).motor) for chave, espec in _casos()}


# ------------------------------------------------------------------ G2: nenhuma vida de hoje muda


def test_g2_vidas_de_hoje_byte_a_byte():
    """168 vidas da bancada (P0 lobos e instinto, P1, P2, P2e, P2a, P3; 3 mundos das frutas; 4 donos; 2 sementes), gravadas antes do
    campo novo. Os lobos daqui veem a bola e as frutas, o P1 tem a E2 e o P2/P2e/P2a a informacao do dono."""
    gab = json.loads(GABARITO.read_text(encoding="utf-8"))
    casos = dict(_casos())
    assert set(gab) == set(casos) and len(gab) == 168
    for chave, espec in casos.items():
        assert _impressao(BANCADA.vida(espec).motor) == gab[chave], chave


def test_padrao_e_de_estado_nao_preenchem():
    o = Observacao(vetor_estado=(0.5,) * 8, ticks_desde_cuidado=0, total_cuidados=0)
    assert o.frutas_cenario == (0.0,) * len(FRUTAS)


# ------------------------------------------------------------------ a presenca certa a cada decisao


class _Espia:
    """politica que anota o que viu e delega (o embrulho do motor fica por fora, como com os lobos)"""

    def __init__(self, interna) -> None:
        self.interna = interna
        self.vistas: list[Observacao] = []

    def agir(self, obs, rng):
        self.vistas.append(obs)
        return self.interna.agir(obs, rng)

    def __getattr__(self, nome):
        return getattr(self.interna, nome)


def _vida_espiada(dono: str, s: int, cf=CF, informante: bool = False):
    espias = []

    def fab(cfg=None):
        from digilab.frutas import PoliticaInstintoFrutas
        e = _Espia(PoliticaInstintoFrutas(cfg, None, cf))
        espias.append(e)
        return e

    fp, fm = fabricas_frutas(cfg_frutas=cf, cfg_informacao=CI if informante else None, politica_fabrica=fab)
    inf = DonoInformante.do_genoma("certo", s, cf) if informante else None
    ofertas = OfertasFrutas(cf) if cf.ligada else None     # desligadas, a oferta falha alto: a vida e a de sempre
    v = simular_vida_frutas(f"{dono}-cenario", criar_dono(dono), fp(), s, 3, 48, fm, ofertas, rotulo_dono=dono,
                            informante=inf)
    return v, espias[0], fp, fm


@pytest.mark.parametrize("dono", DONOS)
def test_presenca_certa_a_cada_decisao(dono):
    """A cada decisao, frutas_cenario e a presenca das frutas que a sub-decisao de comer considera (os `presentes` do registro de
    ofertas), na ordem de FRUTAS; `fruta` continua o maior incentivo entre elas."""
    varias = 0
    for s in (11, 22, 33):
        v, espia, _, _ = _vida_espiada(dono, s, informante=(s == 22))
        m = v.motor
        assert len(espia.vistas) > 0
        registros = iter(m.ofertas)
        com_fruta = 0
        for obs in espia.vistas:
            assert len(obs.frutas_cenario) == len(FRUTAS) and set(obs.frutas_cenario) <= {0.0, 1.0}
            presentes = [f for f, p in zip(FRUTAS, obs.frutas_cenario) if p == 1.0]
            if presentes:
                com_fruta += 1
                varias += len(presentes) >= 2
                reg = next(registros)
                assert reg["presentes"] == presentes and reg["visto"] == obs.fruta
                assert obs.fruta == max(reg["incentivos"][f] for f in presentes)
            else:
                assert obs.fruta == 0.0
        assert next(registros, None) is None
        assert com_fruta == m.contagem_frutas["decisoes_com_fruta"] > 0
    assert varias > 0                                  # decisoes com duas frutas ou mais no cenario


def test_frutas_desligadas_nao_preenchem():
    v, espia, _, _ = _vida_espiada("atencioso", 11, cf=CONFIG_FRUTAS)
    assert espia.vistas and all(o.frutas_cenario == (0.0,) * len(FRUTAS) and o.fruta == 0.0 for o in espia.vistas)


def test_g1_replay_com_o_campo():
    for dono in DONOS:
        v, _, fp, fm = _vida_espiada(dono, 33, informante=True)
        r = reproduzir_frutas(LogDeEventos.de_jsonl(v.motor.log.para_jsonl()), fp, semente=33, fabrica_motor=fm)
        assert _impressao(r) == _impressao(v.motor)
