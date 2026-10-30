"""C1, etapa 1 (docs/TAREFA_V2_LONGE_REGULAR.md, secoes 3.1 e 7): o estilo `longe_fixo` do `DonoComLugar`. Os pontos sao sorteados uma vez
na vida, com a rng propria; toda racao cai num deles; eles ficam a 20 a 30 celulas do comedouro, em direcoes distintas; o replay e bit a bit;
os outros estilos nao consomem nenhum sorteio novo (o gabarito byte a byte esta em test_gabarito_lugar_estilos.py). So as sementes dos testes."""
from __future__ import annotations

import math
import sys
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
from digilab.config import CONFIG_MUNDO_LIGADA, CONFIG_PADRAO, ConfigMundo  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.events import LogDeEventos  # noqa: E402
from digilab.mundo import (ESTILOS_LUGAR, ESTILOS_LUGAR_V2, DonoComLugar, centro_da_celula, distancia,  # noqa: E402
                           fabricas_mundo, reproduzir_mundo, simular_vida_mundo)

CM = CONFIG_MUNDO_LIGADA
SEMENTES = (101, 202, 303, 404, 505)
DONOS = ("atencioso", "relapso", "aleatorio", "incoerente")


def _dono(semente=101, rotulo="atencioso", cm=None):
    return DonoComLugar(criar_dono("atencioso"), "longe_fixo", semente, rotulo, cm)


def _vida(semente, rotulo="atencioso", dias=3):
    fp, fm = fabricas_mundo(CM)
    d = DonoComLugar(criar_dono(rotulo), "longe_fixo", semente, rotulo)
    return simular_vida_mundo(rotulo, d, fp(CONFIG_PADRAO), semente, dias, 48, fm, rotulo_dono=rotulo), d, fp, fm


def test_o_estilo_esta_nos_estilos_e_as_runs_de_antes_iteram_os_tres():
    assert ESTILOS_LUGAR == ESTILOS_LUGAR_V2 + ("longe_fixo",) and ESTILOS_LUGAR_V2 == ("comedouro", "perto", "longe")
    assert ConfigMundo().n_pontos_longe_fixo == 3
    with pytest.raises(ValueError):
        ConfigMundo(n_pontos_longe_fixo=0)
    with pytest.raises(ValueError):
        ConfigMundo(n_pontos_longe_fixo=17)


@pytest.mark.parametrize("semente", SEMENTES)
def test_os_pontos_ficam_na_faixa_e_em_direcoes_distintas(semente):
    d = _dono(semente)
    cx, cy = centro_da_celula(CM.layout.comedouro, CM)
    assert len(d.pontos_fixos) == CM.n_pontos_longe_fixo == len(set(d.pontos_fixos))
    lo, hi = CM.longe_min_celulas * CM.sub, CM.longe_max_celulas * CM.sub
    for x, y in d.pontos_fixos:
        assert 0 <= x < CM.celulas_x * CM.sub and 0 <= y < CM.celulas_y * CM.sub
        assert lo - 1 <= distancia(x - cx, y - cy) <= hi + 1
    # direcoes distintas: cada ponto tem uma das 16 (o angulo mais proximo; o DIR16 gira no sentido do y que cresce para baixo)
    dirs = {round(-math.degrees(math.atan2(y - cy, x - cx)) / 22.5) % 16 for x, y in d.pontos_fixos}
    assert len(dirs) == CM.n_pontos_longe_fixo


def test_os_pontos_variam_com_a_semente_e_com_o_dono_e_nao_com_o_braco():
    p = {s: _dono(s).pontos_fixos for s in SEMENTES}
    assert len(set(p.values())) == len(SEMENTES)
    assert _dono(101).pontos_fixos == _dono(101).pontos_fixos
    assert _dono(101, "relapso").pontos_fixos != _dono(101, "atencioso").pontos_fixos
    # a rng do estilo antigo nao e tocada pela construcao do novo
    a, b = _dono(101), DonoComLugar(criar_dono("atencioso"), "longe", 101, "atencioso")
    c = DonoComLugar(criar_dono("atencioso"), "longe", 101, "atencioso")
    est = {"tick": 0, "mundo": {"pet": (500, 240)}}
    assert [b.lugar(est) for _ in range(20)] == [c.lugar(est) for _ in range(20)] and a.pontos_fixos


@pytest.mark.parametrize("semente", SEMENTES)
@pytest.mark.parametrize("rotulo", DONOS)
def test_toda_racao_cai_num_dos_pontos_e_os_pontos_se_repetem(semente, rotulo):
    v, d, _, _ = _vida(semente, rotulo)
    assert v.interacoes == 48 and d.lugares
    pontos = set(d.pontos_fixos)
    assert all((lg["x"], lg["y"]) in pontos for lg in d.lugares)
    if len(d.lugares) >= 10:
        assert len({(lg["x"], lg["y"]) for lg in d.lugares}) > 1        # o sorteio uniforme usa mais de um ponto


def test_o_sorteio_por_racao_e_uniforme_nos_pontos():
    d = _dono(202)
    est = {"tick": 0, "mundo": {"pet": (500, 240)}}
    vistos = [d.lugar(est) for _ in range(900)]
    contagem = {p: vistos.count(p) for p in d.pontos_fixos}
    assert set(vistos) == set(d.pontos_fixos) and all(200 < n < 400 for n in contagem.values()), contagem


@pytest.mark.parametrize("semente", SEMENTES[:3])
def test_o_replay_e_bit_a_bit_e_os_pontos_sao_os_mesmos(semente):
    v, d, fp, fm = _vida(semente)
    r = reproduzir_mundo(LogDeEventos.de_jsonl(v.motor.log.para_jsonl()), fp, semente=semente, fabrica_motor=fm)
    assert r.log.para_jsonl() == v.motor.log.para_jsonl()
    assert repr(r._estado) == repr(v.motor._estado) and r.estado() == v.motor.estado()
    assert d.pontos_fixos == _dono(semente).pontos_fixos            # os mesmos pontos numa construcao nova
    v2, d2, _, _ = _vida(semente)
    assert d2.lugares == d.lugares and v2.motor.log.para_jsonl() == v.motor.log.para_jsonl()


def test_n_pontos_configuravel_e_falha_alto_sem_direcoes():
    for n in (1, 5):
        assert len(_dono(101, cm=replace(CM, n_pontos_longe_fixo=n)).pontos_fixos) == n
    with pytest.raises(ValueError, match="direcoes cabem"):
        _dono(101, cm=replace(CM, n_pontos_longe_fixo=16))


def test_a_bancada_aceita_o_estilo_novo():
    cfg = {"bracos": ["P0", "P1"], "donos": ["atencioso"], "unidades": {"bases": [101], "k": 1, "prefixo": "mundo"}, "dias": 2,
           "orcamento": 32, "sonda": {"estados": 5, "amostras": 5, "semente": 101}, "bootstrap": {}, "mundos": ["fisico"],
           "lugares": ["longe_fixo", "longe"]}
    bv.validar_config(cfg)
    with pytest.raises(ValueError):
        bv.validar_config({**cfg, "lugares": ["longe_fixo", "lugar_que_nao_existe"]})
    b = bv.Bancada(2, 32)
    v = b.vida(bv.EspecVida("atencioso", "P0", 101, None, "fisico", "instinto", "longe_fixo"))
    r = b.rejogar(LogDeEventos.de_jsonl(v.motor.log.para_jsonl()), v.espec)
    assert bv.resumo_motor(r) == bv.resumo_motor(v.motor)
