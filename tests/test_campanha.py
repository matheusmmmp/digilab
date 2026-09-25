"""Campanha contra NPCs no combate V2.1 (sem treino)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.campanha import gambit_npc, npc, perfil_de_stats, traduzir  # noqa: E402
from digilab.combate_v2.bots import GAMBITS as GAMBITS_V2  # noqa: E402
from digilab.combate_v2.v21.catalogo import Forma, perfil, stats  # noqa: E402
from digilab.combate_v2.v21.partida import jogar, reproduzir  # noqa: E402
from digilab.config import CONFIG_CAMPANHA, STATS_V21  # noqa: E402


def test_npcs_tem_o_total_de_stats_do_pve_treino():
    for tier, d in CONFIG_CAMPANHA.npcs.items():
        p = npc(tier).perfil
        assert sum(p.stats.values()) == pytest.approx(d["total_stats"])
        assert p.tecnica is None and p.passiva is None and p.estagio == "adulto"
    assert [d["total_stats"] for d in CONFIG_CAMPANHA.npcs.values()] == [72, 80, 90]


def test_perfil_de_stats_e_a_mesma_conversao_do_catalogo():
    f = Forma("ferrugem", "adulto", "sereno", "colosso", "tita")
    a, b = perfil(f), perfil_de_stats("x", stats(f))
    for campo in ("hp_max", "guts_inicial", "guts_max", "regen", "mult_perto", "mult_disparo", "mult_guarda"):
        assert getattr(a, campo) == pytest.approx(getattr(b, campo))
    with pytest.raises(ValueError):
        perfil_de_stats("x", {"vigor": 10})


def test_traducao_v2_para_v21_preserva_as_regras():
    for nome in ("agressivo", "contragolpe", "adaptativo"):
        v2, v21 = GAMBITS_V2[nome], traduzir(GAMBITS_V2[nome])
        assert len(v2.regras) == len(v21.regras) and v2.final.acao.value == v21.final.acao.value
        for r2, r21 in zip(v2.regras, v21.regras):
            assert r2.acao.value == r21.acao.value
            assert [c.nome for c in r2.condicoes] == [c.nome for c in r21.condicoes]
    assert gambit_npc("soberano_resposta_longe") is not gambit_npc("adaptativo")


def test_partida_contra_npc_rejoga_bit_a_bit():
    a, b = npc("tier1_brutamontes"), npc("tier3_soberano")
    p = jogar(a, b, 7)
    assert reproduzir(list(p.log), a, b).log == p.log
    assert set(STATS_V21) == set(a.perfil.stats)
