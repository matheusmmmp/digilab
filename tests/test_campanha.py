"""Campanha contra NPCs (regras V21C, escada rebalanceada)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.campanha import REGRAS_CAMPANHA, gambit_npc, npc, perfil_de_stats, traduzir  # noqa: E402
from digilab.combate_v2.bots import GAMBITS as GAMBITS_V2  # noqa: E402
from digilab.combate_v2.v21.bots import ADULTOS  # noqa: E402
from digilab.combate_v2.v21.regras import TECNICAS  # noqa: E402
from digilab.combate_v2.v21.catalogo import Forma, perfil, stats  # noqa: E402
from digilab.combate_v2.v21.partida import jogar, reproduzir  # noqa: E402
from digilab.config import CONFIG_CAMPANHA, CONFIG_CATALOGO, CONFIG_COMBATE_V2C, CONFIG_COMBATE_V21C, STATS_V21  # noqa: E402


def test_npcs_da_escada_de_progressao():
    for tier, d in CONFIG_CAMPANHA.npcs.items():
        p = npc(tier).perfil
        est = d.get("estagio", "adulto")
        assert sum(p.stats.values()) == pytest.approx(d["total_stats"])
        assert p.tecnica is None and p.passiva is None and p.estagio == est
        assert p.hp_max == pytest.approx((CONFIG_COMBATE_V21C.hp_base + CONFIG_COMBATE_V21C.hp_por_vigor * d["total_stats"] / 6)
                                         * CONFIG_CATALOGO.mult_estagio[est])
    assert [(d["lugar"], d["total_stats"], d["estilo"], d.get("estagio", "adulto")) for d in CONFIG_CAMPANHA.npcs.values()] == [
        (1, 96, "crianca:arisco", "crianca"), (2, 72, "v2c:tartaruga", "adulto"), (2, 90, "v21:espelho", "adulto"),
        (2, 90, "v2c:agressivo", "adulto"), (3, 110, "v2c:agressivo", "adulto")]
    assert [d["epsilon"] for d in CONFIG_CAMPANHA.npcs.values()] == [0.5, 0.4, 0.5, 0.5, 0.5]
    assert all(npc(t).epsilon == d["epsilon"] for t, d in CONFIG_CAMPANHA.npcs.items())


def test_ponto_de_treino_vale_o_peso_no_combate():
    from digilab.combate_v2.v21.catalogo import com_treino
    from digilab.config import CONFIG_TREINO
    base = {k: 10.0 for k in STATS_V21}
    s = com_treino(base, {"forca": 2.0}, normalizar=False)
    assert s["forca"] == pytest.approx(10.0 + 2.0 * CONFIG_TREINO.peso_ponto_combate) and CONFIG_TREINO.peso_ponto_combate == 3.0


def test_campanha_luta_com_as_regras_v21c():
    assert REGRAS_CAMPANHA.base == CONFIG_COMBATE_V2C and REGRAS_CAMPANHA.v21 == CONFIG_COMBATE_V21C
    assert CONFIG_COMBATE_V2C.finta and CONFIG_COMBATE_V2C.fuga_condicionada and CONFIG_COMBATE_V21C.marca_fragil


def test_estilo_v21_do_npc_perde_so_as_regras_de_tecnica_e_do_vigia():
    for forma, g in ADULTOS.items():
        n = gambit_npc(f"v21:{forma}")
        assert all(r in g.regras for r in n.regras) and n.final == g.final
        assert not any(r.acao in TECNICAS.values() or any(c.nome == "oponente_vai_preparar" for c in r.condicoes)
                       for r in n.regras)
    assert gambit_npc("agressivo") == gambit_npc("v2:agressivo")
    with pytest.raises(ValueError):
        gambit_npc("v9:agressivo")


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
    p = jogar(a, b, 7, REGRAS_CAMPANHA)
    assert reproduzir(list(p.log), a, b, REGRAS_CAMPANHA).log == p.log
    assert set(STATS_V21) == set(a.perfil.stats)
