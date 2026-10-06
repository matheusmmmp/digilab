"""V2, V1-ADENDO3: o adendo 3 do experimento maior no orquestrador (o bloco de duracoes, o lugar do P2d e do P3i, a referencia do P0 nos
blocos) e o custo. So as sementes dos testes."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import custo_adendo3 as ca  # noqa: E402
import run_v2_experimento_maior as em  # noqa: E402

FUMACA = json.loads((RAIZ / "experiments/configs/v2_experimento_maior/fumaca.json").read_text(encoding="utf-8"))
VALIDACAO = json.loads((RAIZ / "experiments/configs/v2_experimento_maior/validacao.json").read_text(encoding="utf-8"))
CUSTO = json.loads((RAIZ / "artifacts_v2_v1_adendo3/custo.json").read_text(encoding="utf-8"))
BOOT = {"reamostragens": 400, "semente": 7, "nivel": 0.95}


def _curva(f, sementes=range(1, 9)):
    """{dias: {(None, semente): valor}} com o valor f(dias, semente)."""
    return {d: {(None, s): f(d, s) for s in sementes} for d in (7, 14, 28)}


@pytest.mark.parametrize("f,sinal,forma", [
    (lambda d, s: 0.01 * d + 0.001 * s, 1.0, "crescente"),
    (lambda d, s: {7: 0.1, 14: 0.5, 28: 0.2}[d] + 0.001 * (s % 3), 1.0, "otimo_interior"),
    (lambda d, s: {7: 0.5, 14: 0.4, 28: 0.1}[d] + 0.001 * (s % 3), 1.0, "decrescente"),
    (lambda d, s: {7: 0.1, 14: 0.4, 28: 0.4}[d] + 0.002 * ((s * d) % 3 - 1), 1.0, "plato"),
    (lambda d, s: 0.5 - 0.01 * d + 0.001 * s, -1.0, "crescente"),          # a taxa cai: com o sinal -1, melhora
])
def test_forma_da_curva_em_dados_com_resposta_conhecida(f, sinal, forma):
    r = em.forma_da_curva(_curva(f), sinal, 0.2, BOOT)
    assert r["forma"] == forma and r["duracoes"] == [7, 14, 28] and r["sem_valor"] == 0


def test_forma_da_curva_conta_unidade_sem_valor_e_fica_indeterminada_com_ruido():
    c = _curva(lambda d, s: (0.4 if s % 2 else -0.4) * (d / 14) if s != 3 else None)
    r = em.forma_da_curva(c, 1.0, 0.05, BOOT)
    assert r["sem_valor"] == 1 and r["forma"] == "indeterminado"


def test_mesmas_interacoes_por_dia_em_toda_duracao():
    assert em.dias_e_orcamento(VALIDACAO, 7) == {"dias": 7, "orcamento": 112}
    assert em.dias_e_orcamento(VALIDACAO, 28) == {"dias": 28, "orcamento": 448}
    with pytest.raises(ValueError):
        em.dias_e_orcamento({"dias": 14, "orcamento": 225}, 7)


def test_a_validacao_pede_o_adendo_3():
    assert VALIDACAO["duracoes"] == {"menor": 7, "maior": CUSTO["duracao_maior"]} and VALIDACAO["p2d_p3i"] is True
    em.modo_e_unidades(VALIDACAO)
    for ruim in ({k: v for k, v in VALIDACAO.items() if k != "duracoes"}, {**VALIDACAO, "duracoes": {"menor": 7, "maior": 35}},
                 {**VALIDACAO, "duracoes": {"menor": 5, "maior": 28}}, {k: v for k, v in VALIDACAO.items() if k != "p2d_p3i"}):
        with pytest.raises(ValueError):
            em.modo_e_unidades(ruim)


def test_o_custo_escolhe_a_maior_que_cabe_no_teto():
    assert CUSTO["duracao_maior"] in (28, 21) and CUSTO["teto_horas"] == 12.0
    escolhida = CUSTO["opcoes"][str(CUSTO["duracao_maior"])]
    assert escolhida["cabe"] and escolhida["total_horas"] <= 12.0
    if CUSTO["duracao_maior"] == 21:
        assert not CUSTO["opcoes"]["28"]["cabe"]
    # a conta se refaz das razoes gravadas e do tempo por vida da K2
    k2 = json.loads((RAIZ / "artifacts_v2_calibracao_conjunta/D/resultado.json").read_text(encoding="utf-8"))
    tempos = {int(d): t for d, t in CUSTO["medida_da_razao"]["por_duracao"].items()}
    refeito = ca.custo(VALIDACAO, k2, tempos, CUSTO["unidades"])
    assert refeito["opcoes"] == CUSTO["opcoes"] and refeito["duracao_maior"] == CUSTO["duracao_maior"]
    assert CUSTO["vidas_por_unidade_sem_o_adendo3"]["total"] == 44 and CUSTO["unidades"] == 30


def test_p2d_p3i_falha_alto_antes_de_qualquer_vida_enquanto_a_bancada_nao_tem_os_bracos(tmp_path):
    if not em.bracos_p2d_p3i_faltando():
        pytest.skip("os bracos P2d e P3i ja estao na bancada")
    with pytest.raises(NotImplementedError, match="TAREFA_V2_P2D_P3I"):
        em.rodar({**FUMACA, "p2d_p3i": True}, tmp_path)
    assert not any(tmp_path.iterdir())


def test_bloco_sem_p0_ganha_a_referencia_do_p0_do_principal(tmp_path):
    """A correcao do #183: um bloco sem o P0 na mesma run da bancada grava os consumos ate a metade sem referencia; com a referencia do
    P0 do bloco principal, a conta da o mesmo numero que a vida daria rodando junto com o P0."""
    base = {k: FUMACA[k] for k in ("dias", "orcamento", "sonda", "lobos")}
    base.update({"unidades": {"bases": [101, 202], "k": 1}, "dias": 4, "orcamento": 64})
    junto = bv.rodar(em.config_da_bancada(base, ("P0", "P2a"), ("descasado",), []), tmp_path / "junto")
    so = bv.rodar(em.config_da_bancada(base, ("P2a",), ("descasado",), []), tmp_path / "so")
    ij, iso = em.indice(junto["medidas"]), em.indice(so["medidas"])
    _, unidades = em.modo_e_unidades({**base, "dias": 4})
    for u in unidades:
        ku = (u["genoma"], u["semente"])
        assert iso[("P2a", "descasado", ku)]["frutas"]["consumos_ate_metade"]["sem_referencia"]
        p0 = ij[("P0", "descasado", ku)]["frutas"]["taxa_fruta_ruim"]["total"]["taxa"]
        assert em.consumos_com_referencia(iso[("P2a", "descasado", ku)], p0) == \
            ij[("P2a", "descasado", ku)]["frutas"]["consumos_ate_metade"]["consumos"]


def test_fumaca_com_o_bloco_de_duracoes(tmp_path):
    cfg = {**FUMACA, "dias": 4, "orcamento": 64, "unidades": {"bases": [101, 202, 303], "k": 1},
           "duracoes": {"menor": 2, "maior": 6}, "referencia_padrao": False, "replicas_poder": 20,
           "bootstrap": {"reamostragens": 200, "semente": 101, "nivel": 0.95}}
    r = em.rodar(cfg, tmp_path)
    assert r["resumo"]["vidas"]["duracoes"] == 2 * 2 * 2 * 3        # 2 bracos x 2 mundos x 2 duracoes x 3 unidades
    d = json.loads((tmp_path / "duracoes.json").read_text(encoding="utf-8"))
    for mundo in ("descasado", "mutavel"):
        assert set(d[mundo]["por_duracao"]) == {"2", "4", "6"}
        assert set(d[mundo]["forma"]) == {"P0", "P1", "ganho_P0_menos_P1"}
        assert all(f["forma"] in ("crescente", "otimo_interior", "decrescente", "plato", "indeterminado")
                   for f in d[mundo]["forma"].values())
    assert "confusao_declarada" in d["mutavel"]
    assert set(r["resumo"]["duracoes"]) == {"descasado", "mutavel"}
    # o apoio teorico e a limitacao do mutavel ficam na leitura, sem mudar a regra
    pred = r["resumo"]["predicoes"]
    assert {k: p["apoio_teorico"] for k, p in pred.items()} == em.APOIO_TEORICO
    assert pred["2"]["limitacao_mutavel"] == em.LIMITACAO_MUTAVEL and "Kozielska" in em.LIMITACAO_MUTAVEL
    for dias in (2, 6):                                              # toda vida gravada e rejogada do disco (G1, pela bancada)
        pasta = tmp_path / "duracoes" / f"dias_{dias}"
        assert len(list((pasta / "vidas").glob("*.jsonl"))) == 12
        meta = json.loads((pasta / "meta.json").read_text(encoding="utf-8"))
        assert meta["config"]["dias"] == dias and meta["config"]["orcamento"] == 16 * dias
