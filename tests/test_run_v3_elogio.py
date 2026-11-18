"""O orquestrador do ELOGIO (experiments/run_v3_elogio.py) e as medidas dele no digilab/metrics.py (docs/PLANO_ANALISE_V3_ELOGIO.md,
secoes 4 a 7): as frutas presentes (D-EL-19), o M1 (D-EL-24), a vista que so le, a regra da escolha (D-EL-21), as travas da config e a
fumaca das duas fases nas sementes dos testes."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import elogio as el  # noqa: E402
import run_v3_elogio as R  # noqa: E402

from bancada.faixas import FAIXAS_RESERVADAS  # noqa: E402
from digilab.config import CONFIG_ELOGIO_LIGADA  # noqa: E402
from digilab.metrics import consumos_com_presentes, decisao_do_criterio  # noqa: E402


def test_as_frutas_presentes_de_cada_consumo():
    vistas = [(15, {"a", "b"}), (30, {"a", "b", "c"}), (45, {"c"})]
    cons = [(10, "a"), (15, "b"), (40, "c"), (45, "a"), (99, "b")]
    assert consumos_com_presentes(cons, vistas) == [
        (10, "a", frozenset({"a"})),                        # antes da primeira vista: so a comida
        (15, "b", frozenset({"a", "b"})),
        (40, "c", frozenset({"a", "b", "c"})),
        (45, "a", frozenset({"a", "c"})),                   # a comida entra mesmo fora da vista
        (99, "b", frozenset({"b", "c"}))]
    with pytest.raises(ValueError):
        consumos_com_presentes(cons, [(30, {"a"}), (15, {"a"})])
    with pytest.raises(ValueError):
        consumos_com_presentes([(20, "a"), (10, "a")], vistas)


def test_o_m1_e_a_decisao_do_primeiro_consumo_que_fecha_o_criterio():
    cons = [(15 * k, "a" if k % 5 else "b") for k in range(1, 30)]
    assert decisao_do_criterio(cons, "a", 10, 8, 15) == 10              # 8 de a nas 10 primeiras ja fecha
    assert decisao_do_criterio(cons, "b", 10, 8, 15) is None            # censurada
    assert decisao_do_criterio(cons[:9], "a", 10, 1, 15) is None        # menos de 10 frutas
    with pytest.raises(ValueError):
        decisao_do_criterio(cons, "a", 10, 11, 15)


def test_a_vista_so_le_e_a_chave_sem_carinho_nao_muda_a_vida():
    com = el.viver_completo("E-imed", 101, 3, CONFIG_ELOGIO_LIGADA, vista=True)
    sem = el.viver_completo("E-imed", 101, 3, CONFIG_ELOGIO_LIGADA)
    assert com["motor"].log.para_jsonl() == sem["motor"].log.para_jsonl() and com["dono"].carinhos == sem["dono"].carinhos
    assert len(com["vista"].passos) == el.passos_da_vida(3) and all(t % 15 == 0 for t, _ in com["vista"].passos)
    e0 = el.viver_completo("E0", 101, 3, CONFIG_ELOGIO_LIGADA, vista=True)
    off = el.viver_completo("E0", 101, 3)
    assert e0["motor"].log.para_jsonl() == off["motor"].log.para_jsonl()


def test_a_grade_e_a_faixa_sao_as_do_plano():
    S = R.S
    assert R.CELULAS[0] == (S // 4, 1) and len(R.CELULAS) == 12 and R.CELULAS[-1] == (2 * S, 4)
    assert any((lo, hi) == R.FAIXA for lo, hi, _ in FAIXAS_RESERVADAS)
    assert R.FASES == {"calibracao": {"base": 25101, "n": 100}, "validacao": {"base": 25301, "n": 200}} and R.DIAS == 12
    cfg = json.loads((RAIZ / "experiments/configs/v3_elogio/calibracao.json").read_text(encoding="utf-8"))
    assert R.modo_da_config(cfg) == "calibracao"


def _reg(braco, s, celula, m2, priv=0.0, exa=0.0):
    return {"braco": braco, "semente": s, "celula": celula, "m2": m2, "privacao": priv, "exaustao": exa,
            "pref_1a": 0.3, "pref_2a": 0.3}


def test_a_escolha_e_o_menor_g_e_nele_o_menor_w_que_passa():
    regs = [_reg("E0", s, None, 0.3) for s in range(10)]
    bons = {(R.S // 2, 2), (R.S // 2, 4), (R.S, 1)}
    for c in R.CELULAS:
        for s in range(10):
            ganho = 0.2 + 0.01 * s if c in bons else (0.01 * s - 0.045)
            regs += [_reg("E-imed", s, list(c), 0.3 + ganho), _reg("E-sorteado", s, list(c), 0.3)]
    a = R.analisar_calibracao(regs)
    assert a["escolha"] == {"ganho": R.S // 2, "janela": 2}
    piora = [dict(r, privacao=0.1) if r["braco"] == "E-imed" else r for r in regs]
    assert R.analisar_calibracao(piora)["escolha"] is None              # a guarda da M4 barra todas


def test_as_travas_da_config():
    base = {"fase": "validacao", "plano": R.PLANO, "dias": 12, "unidades": {"bases": [25301], "n": 200}, "ganho": R.S, "janela": 1}
    assert R.modo_da_config(base) == "validacao"
    for errado in ({"ganho": 3}, {"janela": 3}, {"dias": 11}, {"unidades": {"bases": [25302], "n": 200}},
                   {"unidades": {"bases": [25301], "n": 199}}):
        with pytest.raises((ValueError, RuntimeError)):
            R.modo_da_config({**base, **errado})
    with pytest.raises(ValueError):
        R.modo_da_config({**base, "fase": "calibracao"})                # a calibracao nao fixa celula
    with pytest.raises(ValueError):
        R.modo_da_config({**base, "extra": 1})
    with pytest.raises(RuntimeError):
        R.exigir_aprovado("**Status: PROPOSTO**")


@pytest.mark.parametrize("fase,ganho,janela,por_unidade", [("calibracao", None, None, 25), ("validacao", R.S, 2, 6)])
def test_a_fumaca_das_duas_fases(tmp_path, fase, ganho, janela, por_unidade):
    cfg = {"fase": fase, "plano": R.PLANO, "dias": 2, "unidades": {"bases": [101], "n": 2}, "ganho": ganho, "janela": janela}
    r = R.rodar(cfg, tmp_path / fase, 2)
    assert r["modo"] == "fumaca" and r["vidas"] == 2 * por_unidade
    linhas = (tmp_path / fase / "vidas.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(linhas) == r["vidas"]
    meta = json.loads((tmp_path / fase / "meta.json").read_text(encoding="utf-8"))
    assert set(meta["artefatos_sha256"]) == {"vidas.jsonl", "resultado.json"} and meta["plano"] == R.PLANO
    if fase == "validacao":
        assert r["P0"]["log_igual"] is True
    with pytest.raises(FileExistsError):
        R.rodar(cfg, tmp_path / fase, 2)
