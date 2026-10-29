"""O conserto da conferencia do credito por opcao com a intencao suspensa (o piloto da L-2 caiu nela em 2026-10-29; o registro
"DIGIBRAIN-MODULAR-L2-CREDITO"). O caso: a busca pelo cheiro suspensa pelo reflexo do sono, que ao acordar acha a comida e e herdada pela
ida na mesma decisao (a opcao composta). As decisoes do cochilo depois da ultima decisao propria da busca sao da busca suspensa, e a
conferencia so aceitava o buraco com a chave da unidade esperada (a da ida).

  - a regressao: a semente 202, M3+S, atencioso, longe (decisoes 148 a 150), que reproduz o caso;
  - a varredura: toda vida +S das sementes dos testes, 14 dias, nas 12 celulas, com a conferencia inteira (o T-CENARIO-1, o G-MECANISMO e o
    credito) e as medidas da L-2;
  - a vida do piloto que caiu (M0+S, aleatorio, longe, a semente 5389789043081588068 da base 67202), vivida em memoria, sem gravar nada:
    o log e o do disco do piloto (o sha) e ela passa com o conserto. E a unica vida da 67xxx num teste, a pedido do Gerente."""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import run_v2_digibrain_l2 as l2  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402

DIAS = orq.DIAS
VIDA_DO_PILOTO = {"braco": "M0+S", "dono": "aleatorio", "lugar": "longe", "semente": 5389789043081588068}
SHA_LOG_DO_PILOTO = "82f298060d48e9bbc20ff017b95ca042d4c5d6ae154f80d85e9d3b3be3f202c0"   # o log gravado pelo piloto caido


def _busca_suspensa_herdada(ms: list) -> list[int]:
    """as decisoes em que a ida herda (a opcao composta) uma busca que foi suspensa"""
    return [k for k, m in enumerate(ms) for f in m["fins"]
            if f.get("composta") and any(g["motivo"] == "achou" and g["inicio"] == f["inicio"] and "n_susp" in g
                                         for mm in ms[:k + 1] for g in mm["fins"])]


def test_a_regressao_da_semente_202():
    _motor, reg, _ = orq.viver("M3+S", "atencioso", "longe", 202, DIAS, orq.ORCAMENTO_POR_DIA, conserto=True)
    ms = orq.cerebro_de(reg).motivos
    assert ms[148]["escolha"] == ["comer", "cheiro", None]
    assert ms[149]["reflexo"] and ms[149]["suspensa"] == {"chave": ["comer", "cheiro", None], "n_susp": 1}
    assert [f["motivo"] for f in ms[150]["fins"]] == ["achou", "meta"] and ms[150]["fins"][1].get("composta")
    assert _busca_suspensa_herdada(ms)
    orq.conferir_mecanismo("M3+S", reg, None)


@pytest.mark.parametrize("semente", [101, 202, 303, 404, 505])
def test_a_varredura_das_vidas_mais_s_nas_sementes_dos_testes(semente):
    for braco in ("M3+S", "M0+S"):
        for dono, lugar in orq.CELULAS:
            motor, reg, _ = orq.viver(braco, dono, lugar, semente, DIAS, orq.ORCAMENTO_POR_DIA, conserto=True)
            orq.conferir_cenario(motor, reg)
            orq.conferir_mecanismo(braco, reg, None)
            med = orq.medidas(motor, reg, braco, DIAS, True)
            l2.medidas_l2(motor, reg, med["episodios_fome"]["episodios"])


def test_o_caso_aparece_na_varredura():
    """a varredura cobre o caso que caiu (sem ele, ela nao provaria o conserto)"""
    _motor, reg, _ = orq.viver("M0+S", "incoerente", "longe", 303, DIAS, orq.ORCAMENTO_POR_DIA, conserto=True)
    assert _busca_suspensa_herdada(orq.cerebro_de(reg).motivos)
    orq.conferir_mecanismo("M0+S", reg, None)


def test_a_vida_do_piloto_que_caiu_passa_com_o_conserto_sem_gravar_nada():
    """a vida e vivida em memoria (o `viver`, que nao grava): o log e o do disco do piloto, byte a byte, pelo sha"""
    v = VIDA_DO_PILOTO
    motor, reg, _ = orq.viver(v["braco"], v["dono"], v["lugar"], v["semente"], DIAS, orq.ORCAMENTO_POR_DIA, conserto=True)
    assert hashlib.sha256(motor.log.para_jsonl().encode("utf-8")).hexdigest() == SHA_LOG_DO_PILOTO
    assert _busca_suspensa_herdada(orq.cerebro_de(reg).motivos)
    orq.conferir_cenario(motor, reg)
    orq.conferir_mecanismo(v["braco"], reg, None)
