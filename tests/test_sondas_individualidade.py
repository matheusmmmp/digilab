"""A bateria de sondas da INDIVIDUALIDADE (experiments/sondas_individualidade.py; docs/TAREFA_V3_INDIVIDUALIDADE.md, etapa I1): o G2 (a
vida sai a mesma com e sem a bateria), o determinismo, a copia no tick certo, o tapa so na copia, a sonda desconhecida falhando alto e o
gabarito da bateria. Vidas so com as sementes dos testes (101...505)."""
from __future__ import annotations

import hashlib
import json
import random
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v2_memoria_autobio as ma  # noqa: E402
import sondas_individualidade as si  # noqa: E402

GABARITO = RAIZ / "tests" / "gabaritos" / "sondas_individualidade.json"
VIDA = ("REL+F", "atencioso", "comedouro", 101, 2, 16)      # braco, dono, lugar, semente, dias, orcamento por dia


def _texto(b: dict) -> str:
    return json.dumps(b, sort_keys=True, separators=(",", ":"))


@pytest.fixture(scope="module")
def vida():
    return si.vida_com_bateria(*VIDA)


def test_g2_a_bateria_nao_muda_a_vida(vida):
    motor, _, _, _ = vida
    limpo, _, _, _ = ma.viver(*VIDA)
    assert motor.log.para_jsonl() == limpo.log.para_jsonl()
    assert bv.resumo_motor(motor) == bv.resumo_motor(limpo)


def test_o_tapa_so_na_copia(vida):
    motor, _, _, b = vida
    assert '"tapa"' not in motor.log.para_jsonl()
    assert any(d["tick"] is not None and d["janelas"]["susto"] for d in b["por_dia"])


def test_determinismo(vida):
    motor, _, fab, b = vida
    assert _texto(si.bateria(motor, fab, VIDA[3], VIDA[4])) == _texto(b)


def test_a_copia_para_no_tick(vida):
    motor, _, fab, b = vida
    tick = next(d["tick"] for d in b["por_dia"] if d["tick"] is not None)
    m = si.copia_em(motor, fab, VIDA[3], tick)
    assert m.estado()["tick"] == tick
    assert motor.log.para_jsonl().startswith("\n".join(m.log.para_jsonl().splitlines()[:-1]))


def test_todas_as_janelas_e_replicas(vida):
    _, _, _, b = vida
    for d in b["por_dia"]:
        if d["tick"] is None:
            continue
        assert set(d["janelas"]) == set(si.JANELAS)
        for reps in d["janelas"].values():
            assert len(reps) == si.REPLICAS
            assert all(r["n"] > 0 and len(r["acoes"]) == r["n"] for r in reps)


def test_momento_e_decisao_acordada(vida):
    motor, _, _, b = vida
    acordadas = {t - t % si.PASSO_DONO for t, a in motor._acoes_pet if a is not si.AcaoPet.DORMIR}
    for d in b["por_dia"]:
        if d["tick"] is not None:
            assert d["tick"] in acordadas
            assert d["tick"] >= d["dia"] * si.TICKS_POR_DIA + si.HORA_SONDA - si.PASSO_DONO


def test_sonda_desconhecida_falha_alto(vida):
    motor, _, fab, b = vida
    tick = next(d["tick"] for d in b["por_dia"] if d["tick"] is not None)
    with pytest.raises(si.SondaDesconhecida):
        si.aplicar("carinho", si.copia_em(motor, fab, VIDA[3], tick), random.Random(0))


def test_gabarito(vida):
    """o sha256 da bateria da vida de teste; mudar a bateria, o cerebro ou o motor muda o gabarito, que so se regrava num commit proprio"""
    _, _, _, b = vida
    atual = hashlib.sha256(_texto(b).encode("utf-8")).hexdigest()
    gravado = json.loads(GABARITO.read_text(encoding="utf-8"))
    assert gravado["vida"] == list(VIDA)
    assert gravado["sha256"] == atual
