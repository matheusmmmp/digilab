"""V2, V1-LIGAR: o adendo 4 do experimento maior (a faixa de validacao nova, a 15101...15505 queimada, a leitura do 4.2). So as sementes
dos testes."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v2_experimento_maior as em  # noqa: E402
from digilab.config import TICKS_POR_DIA  # noqa: E402
from digilab.evolucao import politica_no_tick  # noqa: E402

FUMACA = json.loads((RAIZ / "experiments/configs/v2_experimento_maior/fumaca.json").read_text(encoding="utf-8"))
VALIDACAO = json.loads((RAIZ / "experiments/configs/v2_experimento_maior/validacao.json").read_text(encoding="utf-8"))
NOVA = [30101, 30202, 30303, 30404, 30505]


def test_a_faixa_de_validacao_e_a_nova():
    assert list(bv.BASES_EXPERIMENTO_MAIOR["validacao"]) == NOVA == VALIDACAO["unidades"]["bases"]
    modo, unidades = em.modo_e_unidades(VALIDACAO)
    assert modo == "validacao" and len(unidades) == 30
    assert unidades == bv.unidades_derivadas(NOVA, 6)                     # a regra das unidades e a mesma (adendo 4.1)
    faixas = {(a, b): f for a, b, f in bv.FAIXAS_RESERVADAS}
    assert "QUEIMADA" in faixas[(15101, 15505)] and (30101, 30505) in faixas
    assert [(a, b) for a, b, _ in bv.FAIXAS_QUEIMADAS] == [(15101, 15505)]


@pytest.mark.parametrize("bases", [[15101, 15202, 15303, 15404, 15505], [15303]])
def test_a_faixa_queimada_e_recusada_mesmo_com_plano(bases, tmp_path):
    cfg = {**VALIDACAO, "unidades": {"bases": bases, "k": 6}}
    with pytest.raises(bv.SementeSemPlano):
        em.modo_e_unidades(cfg)
    cb = em.config_da_bancada(cfg, ("P0",), ("descasado",), [])
    with pytest.raises(bv.SementeSemPlano, match="queimada"):
        bv.validar_config(cb)
    with pytest.raises(bv.SementeSemPlano, match="queimada"):
        bv.validar_config({**{k: v for k, v in cb.items() if k != "unidades"}, "sementes": [15404]})
    with pytest.raises(bv.SementeSemPlano):
        em.rodar(cfg, tmp_path / "x")
    assert not (tmp_path / "x").exists()


def test_w_info_no_fim_de_cada_dia_num_replay_so_e_o_do_replay_ate_cada_dia(tmp_path):
    cfg = {**FUMACA, "unidades": {"bases": [101, 202], "k": 1}, "dias": 4, "orcamento": 64}
    cb = em.config_da_bancada(cfg, ("P2e",), ("descasado", "mutavel"), [])
    r = bv.rodar(cb, tmp_path)
    bancada = bv.bancada_da_config(cb)
    ler = lambda p: bv.do_braco(p).cerebro.estado_interno()["peso_info"]  # noqa: E731
    vistas = 0
    for v in r["vidas"].values():
        fab, fm = bancada.fabrica_politica(v.espec), bancada.fabrica_motor(v.espec)
        serie = em.serie_no_fim_de_cada_dia(v.motor.log, fab, v.espec.semente, 4, fm, ler)
        um_a_um = [ler(politica_no_tick(v.motor.log, fab, v.espec.semente, d * TICKS_POR_DIA, fm)) for d in range(1, 5)]
        assert serie == um_a_um and serie[-1] == ler(v.motor.politica)
        vistas += len(set(serie)) > 1
    assert vistas, "nenhuma vida com o w_info mudando: o teste nao confere nada"
