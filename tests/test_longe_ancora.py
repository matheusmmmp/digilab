"""LONGE_GEOMETRIA (docs/PLANO_ANALISE_V3_LONGE_GEOMETRIA.md, secoes 3.1, 3.2 e 4): o estilo `longe_ancora` do `DonoComLugar` e o nivel
`longe_um`. Cada racao do `longe_ancora` cai num ponto novo, sorteado como um ponto do `longe_fixo` (as mesmas direcoes viaveis, a mesma
faixa de distancia ao comedouro), com a rng propria; a distribuicao de um ponto e a mesma nos dois estilos (a conferencia da construcao); o
replay e bit a bit; os outros estilos nao mudam (o gabarito byte a byte esta em test_gabarito_lugar_estilos_lg.py). So as sementes dos testes."""
from __future__ import annotations

import math
import random
import statistics
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
from digilab.config import CONFIG_MUNDO_LIGADA, CONFIG_PADRAO, N_PONTOS_LONGE_UM  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.events import LogDeEventos  # noqa: E402
from digilab.mundo import (ESTILOS_LUGAR, DonoComLugar, centro_da_celula, distancia, fabricas_mundo,  # noqa: E402
                           reproduzir_mundo, simular_vida_mundo)

CM = CONFIG_MUNDO_LIGADA
SEMENTES = (101, 202, 303, 404, 505)
DONOS = ("atencioso", "relapso", "aleatorio", "incoerente")
EST = {"tick": 0, "mundo": {"pet": (500, 240)}}
N_SORTEIOS = 20000


def _dono(semente=101, rotulo="atencioso", estilo="longe_ancora", **kw):
    return DonoComLugar(criar_dono("atencioso"), estilo, semente, rotulo, **kw)


def _vida(semente, rotulo="atencioso", dias=3):
    fp, fm = fabricas_mundo(CM)
    d = DonoComLugar(criar_dono(rotulo), "longe_ancora", semente, rotulo)
    return simular_vida_mundo(rotulo, d, fp(CONFIG_PADRAO), semente, dias, 48, fm, rotulo_dono=rotulo), d, fp, fm


def _direcao(x, y):
    cx, cy = centro_da_celula(CM.layout.comedouro, CM)
    return round(-math.degrees(math.atan2(y - cy, x - cx)) / 22.5) % 16


def _dist(x, y):
    cx, cy = centro_da_celula(CM.layout.comedouro, CM)
    return distancia(x - cx, y - cy)


def test_o_estilo_esta_nos_estilos_e_o_longe_um_e_um_ponto():
    assert "longe_ancora" in ESTILOS_LUGAR and ESTILOS_LUGAR[-1] == "longe_ancora"
    assert N_PONTOS_LONGE_UM == 1 and len(_dono(estilo="longe_fixo", n_pontos=N_PONTOS_LONGE_UM).pontos_fixos) == 1
    d = _dono()
    assert d.pontos_fixos == () and d._viaveis_ancora == tuple(_dono(estilo="longe_fixo")._direcoes_viaveis())


@pytest.mark.parametrize("semente", SEMENTES)
def test_cada_ponto_fica_na_faixa_numa_direcao_viavel(semente):
    d = _dono(semente)
    lo, hi = CM.longe_min_celulas * CM.sub, CM.longe_max_celulas * CM.sub
    for _ in range(300):
        x, y = d.lugar(EST)
        assert 0 <= x < CM.celulas_x * CM.sub and 0 <= y < CM.celulas_y * CM.sub
        assert lo - 1 <= _dist(x, y) <= hi + 1
        assert _direcao(x, y) in d._viaveis_ancora


def test_os_pontos_nao_se_repetem_como_no_fixo_e_nao_dependem_do_pet():
    d = _dono(202)
    vistos = [d.lugar(EST) for _ in range(200)]
    assert len(set(vistos)) > 100                                   # a maioria e nova (o fixo usaria so 3; a grade inteira repete alguns)
    a, b = _dono(303), _dono(303)
    assert [a.lugar(EST) for _ in range(50)] == [b.lugar({"tick": 0, "mundo": {"pet": (10, 10)}}) for _ in range(50)]


def test_a_rng_e_propria_e_varia_com_a_semente_e_o_dono():
    assert [_dono(101).lugar(EST) for _ in range(1)] != [_dono(202).lugar(EST) for _ in range(1)]
    s = lambda rot: [d.lugar(EST) for d in [_dono(101, rot)] for _ in range(20)]        # noqa: E731
    assert s("relapso") != s("atencioso")
    # o estilo novo nao toca na rng dos outros: o longe sorteado da mesma semente sai igual com ou sem um longe_ancora construido antes
    b, c = _dono(101, estilo="longe"), (_dono(101), _dono(101, estilo="longe"))[1]
    assert [b.lugar(EST) for _ in range(20)] == [c.lugar(EST) for _ in range(20)]


def test_a_distribuicao_de_um_ponto_e_a_do_longe_fixo():
    """a conferencia da construcao (3.2): a direcao e a distancia de uma racao do longe_ancora contra as de um ponto do longe_fixo (o
    primeiro ponto de um sorteio sem reposicao e uniforme nas viaveis; a distancia sai do mesmo jeito)"""
    d = _dono(404)
    anc = [d.lugar(EST) for _ in range(N_SORTEIOS)]
    rng = random.Random(4242)
    fix = [_dono(rng.randrange(10 ** 9), estilo="longe_fixo", n_pontos=1).pontos_fixos[0] for _ in range(N_SORTEIOS)]
    viaveis = d._viaveis_ancora
    for amostra in (anc, fix):
        cont = {v: 0 for v in viaveis}
        for x, y in amostra:
            cont[_direcao(x, y)] += 1
        esperado = N_SORTEIOS / len(viaveis)
        assert all(abs(n - esperado) < 6 * math.sqrt(esperado) for n in cont.values()), cont
    qa = statistics.quantiles([_dist(*p) for p in anc], n=10)
    qf = statistics.quantiles([_dist(*p) for p in fix], n=10)
    assert all(abs(a - b) <= 3 for a, b in zip(qa, qf)), (qa, qf)   # em subunidades (16 por celula)


@pytest.mark.parametrize("semente", SEMENTES[:3])
@pytest.mark.parametrize("rotulo", DONOS)
def test_toda_racao_cai_num_ponto_novo_na_faixa(semente, rotulo):
    v, d, _, _ = _vida(semente, rotulo)
    assert v.interacoes == 48 and d.lugares
    lo, hi = CM.longe_min_celulas * CM.sub, CM.longe_max_celulas * CM.sub
    assert all(lo - 1 <= _dist(lg["x"], lg["y"]) <= hi + 1 for lg in d.lugares)


@pytest.mark.parametrize("semente", SEMENTES[:3])
def test_o_replay_e_bit_a_bit(semente):
    v, d, fp, fm = _vida(semente)
    r = reproduzir_mundo(LogDeEventos.de_jsonl(v.motor.log.para_jsonl()), fp, semente=semente, fabrica_motor=fm)
    assert r.log.para_jsonl() == v.motor.log.para_jsonl()
    assert repr(r._estado) == repr(v.motor._estado) and r.estado() == v.motor.estado()
    v2, d2, _, _ = _vida(semente)
    assert d2.lugares == d.lugares and v2.motor.log.para_jsonl() == v.motor.log.para_jsonl()


def test_falha_alto_sem_direcao_que_caiba(monkeypatch):
    monkeypatch.setattr(DonoComLugar, "_direcoes_viaveis", lambda self: [])
    with pytest.raises(ValueError, match="nenhuma direcao cabe"):
        _dono()


def test_a_bancada_aceita_o_estilo_novo():
    cfg = {"bracos": ["P0", "P1"], "donos": ["atencioso"], "unidades": {"bases": [101], "k": 1, "prefixo": "mundo"}, "dias": 2,
           "orcamento": 32, "sonda": {"estados": 5, "amostras": 5, "semente": 101}, "bootstrap": {}, "mundos": ["fisico"],
           "lugares": ["longe_ancora", "longe"]}
    bv.validar_config(cfg)
    b = bv.Bancada(2, 32)
    v = b.vida(bv.EspecVida("atencioso", "P0", 101, None, "fisico", "instinto", "longe_ancora"))
    r = b.rejogar(LogDeEventos.de_jsonl(v.motor.log.para_jsonl()), v.espec)
    assert bv.resumo_motor(r) == bv.resumo_motor(v.motor)
