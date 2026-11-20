"""Testes do D-COMIDA da DC4 (experiments/d_comida_dc4.py; plano da DC4, secao 6): as contas por pedido e o resumo, com um cerebro falso.
A conferencia contra a run da DC3 (o log e as medidas de cada vida) roda na propria execucao, que falha alto."""
from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(RAIZ), str(RAIZ / "experiments")]

import d_comida_dc4 as dc  # noqa: E402
import run_v3_conversa_dc3 as d3  # noqa: E402


class AfetoFalso:
    """o r_n e o corpo de depois menos o de antes (os corpos sao inteiros)"""

    def sigma_luta(self, pc0, pc1, recs):
        return {"r": pc1 - pc0, "r_n": pc1 - pc0}


def _motivo(k, acao, fome, solidao, r_n, comeu=False, aberta=False):
    cons = None if aberta else {"r_n": r_n, "comeu": {"id": 1} if comeu else None}
    return {"k": k, "acao": acao, "afeto": {"urgencias": {"fome": fome, "solidao": solidao}}, "consequencia": cons}


def _cerebro():
    F = d3.FALA
    ms = [_motivo(0, F, 100, 50, 2 - 0),            # pede comida: a fome so cai na decisao 3
          _motivo(1, "explorar", 100, 40, 1),
          _motivo(2, "comer", 100, 40, 5, comeu=True),
          _motivo(3, F, 80, 60, 4 - 3),             # pede companhia: a solidao cai na decisao 4
          _motivo(4, "ocioso", 80, 30, 0, aberta=True)]
    pc_decisao = [0, 2, 3, 3, 4]
    pc_acao = [1, 3, 8, 3, 4]
    c = SimpleNamespace(motivos=ms, m=SimpleNamespace(sens=SimpleNamespace(receptores=("fome",)), afeto=AfetoFalso()))
    return c, pc_decisao, pc_acao


def test_conferir_r_n_aceita_a_conta_certa_e_falha_alto_com_outra():
    c, pd, pa = _cerebro()
    dc.conferir_r_n(c, pd, pa)
    c.motivos[1]["consequencia"]["r_n"] = 99
    with pytest.raises(RuntimeError, match="decisao 1"):
        dc.conferir_r_n(c, pd, pa)
    with pytest.raises(RuntimeError, match="corpos"):
        dc.conferir_r_n(c, pd[:-1], pa)


def test_pedidos_da_vida_mede_ate_cair_e_ate_comer():
    c, pd, pa = _cerebro()
    atende = SimpleNamespace(atendimentos=[{"k": 0, "conteudo": "fome"}, {"k": 3, "conteudo": "solidao"},
                                           {"k": 4, "conteudo": "fome"}])          # o da ultima decisao fica fora
    ps = dc.pedidos_da_vida(c, atende, pd, pa)
    assert len(ps) == 2
    fome, comp = ps
    assert fome["decisoes_ate_cair"] == 3 and fome["ticks_ate_cair"] == 3 * dc.CONFIG_PADRAO.intervalo_decisao_ticks
    assert fome["come_na_janela"] is False and fome["decisoes_ate_comer"] == 2
    assert fome["r_n_hoje"] == 2 and fome["r_n_ate_comer"] == pa[2] - pd[0]
    assert comp["decisoes_ate_cair"] == 1 and "r_n_ate_comer" not in comp


def test_resumir_conta_o_sinal_e_os_censurados():
    ps = [{"conteudo": "fome", "ticks_ate_cair": 30, "come_na_janela": False, "decisoes_ate_comer": 1, "r_n_hoje": -5, "r_n_ate_comer": 7},
          {"conteudo": "fome", "ticks_ate_cair": None, "come_na_janela": False, "decisoes_ate_comer": None, "r_n_hoje": 3,
           "r_n_ate_comer": None},
          {"conteudo": "solidao", "ticks_ate_cair": 15}]
    r = dc.resumir(ps)
    assert r["fome"]["pedidos"] == 2 and r["fome"]["ticks_ate_cair"]["censurados"] == 1
    assert r["fome"]["come_na_decisao_seguinte"] == 1
    assert r["fome"]["pareado"] == {"n": 1, "sinal_muda": 1, "de_nao_positivo_a_positivo": 1, "media_hoje": -5, "media_ate_comer": 7}
    assert r["fome"]["r_n_ate_comer"]["nenhum"] == 1
    assert r["solidao"] == {"pedidos": 1, "ticks_ate_cair": {"n": 1, "censurados": 0, "media": 15, "mediana": 15, "p90": None}}


def test_importar_nao_mexe_na_dc3_e_a_leitura_so_troca_as_fabricas_e_o_dono(monkeypatch):
    assert d3.fabricas is dc._fabricas_dc3 and d3.DonoQueAtende is dc._DonoQueAtendeGuardado.__mro__[1]
    monkeypatch.setattr(d3, "fabricas", d3.fabricas)
    monkeypatch.setattr(d3, "DonoQueAtende", d3.DonoQueAtende)
    dc.ligar_leitura()
    assert d3.fabricas is dc._fabricas_que_leem and d3.DonoQueAtende is dc._DonoQueAtendeGuardado
    assert dc.MAX_PROCESSOS == 4
    with pytest.raises(ValueError):
        dc.rodar(5, Path("."))
