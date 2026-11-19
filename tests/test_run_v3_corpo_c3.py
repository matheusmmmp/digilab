"""O orquestrador da C3, a ponte com teto (experiments/run_v3_corpo_c3.py; docs/PLANO_ANALISE_V3_CORPO_C3.md): os bracos mudam so a sua
chave, o CTRL e a D sao as vidas da C2, a conferencia falha alto, a regra de leitura escrita antes (com a guarda da saude), a trava da
config e uma fumaca dos dois blocos, nas sementes dos testes."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v3_corpo as C2  # noqa: E402
import run_v3_corpo_c3 as R  # noqa: E402
from digilab.config import CONFIG_TETO_FOME_BAIXO, CONFIG_TETO_FOME_CORPO, CONFIG_TETO_FOME_LIMIAR  # noqa: E402

FUMACA = json.loads((RAIZ / "experiments/configs/v3_corpo_c3/fumaca.json").read_text(encoding="utf-8"))
RUN = json.loads((RAIZ / "experiments/configs/v3_corpo_c3/run.json").read_text(encoding="utf-8"))


def test_cada_braco_muda_so_a_sua_chave():
    for b in ("CTRL", "D"):
        assert {k: v for k, v in R.montar(b).items() if k != "teto"} == C2.montar(b)
        assert R.montar(b)["teto"] == CONFIG_TETO_FOME_CORPO
    assert R.montar("DTL") == {**R.montar("D"), "teto": CONFIG_TETO_FOME_LIMIAR}
    assert R.montar("DTB") == {**R.montar("D"), "teto": CONFIG_TETO_FOME_BAIXO}
    with pytest.raises(ValueError):
        R.montar("DE")


@pytest.mark.parametrize("braco", ["CTRL", "D"])
def test_o_ctrl_e_a_d_sao_as_vidas_da_c2(braco):
    a = R.viver(braco, "relapso", "comedouro", 101, 2, 16)[0]
    b = C2.viver(braco, "relapso", "comedouro", 101, 2, 16)[0]
    assert a.log.para_jsonl() == b.log.para_jsonl()


def test_a_conferencia_pega_a_chave_errada():
    motor, registro, _, _, baixas = R.viver("DTL", "relapso", "comedouro", 101, 2, 16)
    assert motor.corpo.ticks_teto > 0
    for errado in ("CTRL", "D", "DTB"):
        with pytest.raises(RuntimeError):
            R.conferir_vida(errado, motor, registro, baixas)
    R.conferir_vida("DTL", motor, registro, baixas)


def test_as_celulas_da_saude_e_do_incoerente():
    assert len(R.CELULAS_SEM_COMIDA) == 6 and {d for d, _ in R.CELULAS_SEM_COMIDA} == {"relapso", "aleatorio"}
    assert len(R.CELULAS_DISTINTAS) == 11 and R.CELULA_COPIA not in R.CELULAS_DISTINTAS


def _cb(classe_f, rejeita, b_passa=True, s_passa=True):
    return {"F": {"classe": {"classe": classe_f}, "holm": {"rejeita": rejeita}},
            "B": {"saude_sem_comida": {"passa": b_passa}}, "S": {"S2_tempo_ate_o_reencontro": {"passa": s_passa}}}


@pytest.mark.parametrize("cb, leitura", [(_cb("> 0", True), "ganho"), (_cb("> 0", True, b_passa=False), "perda"),
                                         (_cb("> 0", True, s_passa=False), "perda"), (_cb("> 0", False), "nulo"),
                                         (_cb("≈ 0", False), "nulo"), (_cb("indeterminado", False), "indeterminado")])
def test_a_regra_de_leitura_escrita_antes(cb, leitura):
    assert R.leitura_do_braco(cb)["leitura"] == leitura


def test_a_trava_e_a_config():
    assert R.modo_da_config(FUMACA) == "fumaca"
    assert tuple(RUN["unidades"]["bases"]) == R.BASES_I and tuple(RUN["pares"]["bases"]) == R.BASES_II
    assert RUN["unidades"]["k"] == RUN["pares"]["k"] == R.K_POR_BASE == 1
    assert any((lo, hi) == R.FAIXA for lo, hi, _ in bv.FAIXAS_RESERVADAS)
    errada = {**RUN, "unidades": {**RUN["unidades"], "bases": RUN["unidades"]["bases"][:-1]}}
    with pytest.raises(bv.SementeSemPlano):
        R.modo_da_config(errada)
    with pytest.raises(ValueError):
        R.modo_da_config({**FUMACA, "fase": "corpo"})


def test_a_fumaca_roda_os_dois_blocos(tmp_path):
    cfg = {**FUMACA, "unidades": {**FUMACA["unidades"], "bases": [101]}, "pares": {**FUMACA["pares"], "bases": [101], "dias": 1}}
    r = R.rodar(cfg, tmp_path / "f", 1)
    res = r["resultado"]
    assert res["vidas"] == len(R.BRACOS) * len(R.CELULAS) and res["pares"] == len(R.BRACOS)
    assert set(res["veredito"]["bracos"]) == set(R.COM_TETO)
    assert res["criterios"]["D"]["F"]["holm"] is None
    assert set(res["criterios"]["DTL"]["B"]) >= {"saude_12_celulas", "saude_sem_comida", "privacao_comedouro"}
    assert set(res["criterios"]["DTL"]["S"]) == {"S2_tempo_ate_o_reencontro"}
    assert res["descritivo"]["incoerente"]["vidas_iguais_ao_atencioso"]["CTRL|comedouro"]["vidas"] == 1
    for n in ("medidas.json", "pares.json", "resultado.json", "vidas.tar.gz", "pares.tar.gz", "meta.json"):
        assert (tmp_path / "f" / n).exists()
    with pytest.raises(FileExistsError):
        R.rodar(cfg, tmp_path / "f", 1)
