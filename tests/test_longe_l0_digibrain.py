"""A etapa L0 (experiments/longe_l0_digibrain.py) numa vida dos testes (a semente 101, fora da 66xxx): o replay refaz as medidas e passa
no G1; uma medida gravada mudada faz o G1 falhar alto; a captura nao muda a vida; as contas pequenas (o angulo e a regra) dao o esperado.
As vidas da 66xxx nao rodam aqui."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import longe_l0_digibrain as l0  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402

SEMENTE = 101


@pytest.fixture(scope="module")
def vida(tmp_path_factory) -> tuple[str, dict]:
    """uma vida M3 no longe com a semente dos testes, gravada como a run grava (o log no disco e as medidas sem o custo)"""
    motor, registro, _fab = orq.viver("M3", "atencioso", "longe", SEMENTE, l0.DIAS, l0.ORCAMENTO, conserto=True)
    arquivo = tmp_path_factory.mktemp("vidas") / f"atencioso_longe_{SEMENTE}.jsonl"
    arquivo.write_text(motor.log.para_jsonl(), encoding="utf-8", newline="\n")
    gravada = {"vida": f"M3|atencioso|longe|{SEMENTE}", "braco": "M3", "dono": "atencioso", "lugar": "longe", "semente": SEMENTE,
               "base": 0, "k": 0, **orq.medidas(motor, registro, "M3", l0.DIAS, True), "custo": {"vida_cpu": 0.0}}
    return str(arquivo), gravada


def test_o_replay_refaz_a_vida_e_mede(vida):
    arquivo, gravada = vida
    s = l0.rejogar(("M3", "atencioso", "longe", SEMENTE, arquivo, gravada))
    assert s["vida"] == gravada["vida"]
    assert s["ml1"]["decisoes"] + s["ml1"]["direcao_0"] <= len(s["ml6"])
    assert len(s["ml3"]) == gravada["episodios_fome"]["n"]
    assert s["ml5"]["fechados"] == gravada["episodios_fome"]["fechados"]
    for t in ("busca", "comer"):
        c = s["ml2"][t]
        assert c["quebra"] == c["reflexo_sono"] + c["outra_com_racao_em_R"]
        assert c["trocadas"] == c["quebra"] + c["para_comer"] + c["outra_sem_racao_em_R"]
        assert sum(c["por_vencedora"].values()) == c["trocadas"]
    soma = l0.somar([s], [(e[1], e[4]) for e in gravada["episodios_fome"]["episodios"]])
    assert soma["vidas"] == 1 and soma["M-L6"]["decisoes"] == len(s["ml6"])


def test_o_g1_falha_alto_com_uma_medida_mudada(vida):
    arquivo, gravada = vida
    mudada = {**gravada, "d_fe": gravada["d_fe"] + 1e-9}
    with pytest.raises(RuntimeError, match="G1 da L0"):
        l0.rejogar(("M3", "atencioso", "longe", SEMENTE, arquivo, mudada))


def test_o_angulo():
    assert l0._angulo(10, 0, 1024, 0) == pytest.approx(0.0)
    assert l0._angulo(0, 10, 1024, 0) == pytest.approx(90.0)
    assert l0._angulo(-10, 0, 1024, 0) == pytest.approx(180.0)
    assert l0._angulo(10, 10, 1024, 0) == pytest.approx(45.0)
    assert l0._angulo(0, 0, 1024, 0) == 0.0


def _longe(p_gt, n1, quebra, trocadas):
    return {"M-L1": {"frac_a_mais_de_45_de_todas": p_gt / n1, "direcao_0": {"decisoes": 0}},
            "M-L2": {"busca": {"frac_quebra": quebra / trocadas, "trocadas": trocadas}}}


def test_a_regra_como_registrada():
    assert l0.regra(_longe(25, 100, 49, 100))["aponta"].startswith("L-1 (")
    assert l0.regra(_longe(24, 100, 50, 100))["aponta"].startswith("L-2")
    assert l0.regra(_longe(25, 100, 50, 100))["aponta"].startswith("L-1 e L-2")
    assert l0.regra(_longe(24, 100, 49, 100))["aponta"].startswith("nenhuma")
    assert l0.regra(_longe(1, 1, 1, 1))["limiares"] == {"angulo_graus": 45.0, "frac_percepcao": 0.25, "frac_decisao": 0.5,
                                                       "status": "PROPOSTOS, SEM FONTE (a secao 2 da proposta)"}


def test_o_codigo_de_hoje_e_o_da_run():
    import json
    meta = json.loads(l0.META.read_text(encoding="utf-8"))
    assert l0.conferir_codigo(meta)["iguais_ao_meta"]
    assert l0._sha(l0.MEDIDAS) == l0.SHA_MEDIDAS
