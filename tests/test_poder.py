"""TAREFA_ANALISE_PODER, Etapa 0: ordem da normalizacao, sementes disjuntas, condicao neutra desligada."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

from digilab.combate_v2.v21.catalogo import Forma, com_treino, perfil, renormalizar, stats  # noqa: E402
from digilab.config import (CONFIG_ARENA_PESQUISA, CONFIG_CATALOGO, CONFIG_TREINO, STATS_V21,  # noqa: E402
                            ConfigArenaPesquisa)
from digilab.evolucao import condicao_na_arena  # noqa: E402

CFG = json.loads((RAIZ / "experiments" / "configs" / "poder_pesquisa.json").read_text(encoding="utf-8"))


def _norm(brutos: dict, total: float) -> dict:
    return renormalizar({k: v * total / sum(brutos.values()) for k, v in brutos.items()}, total,
                        CONFIG_CATALOGO.stat_min, CONFIG_CATALOGO.stat_max)


def test_peso_do_treino_entra_antes_da_normalizacao():
    """Pontos x peso_ponto_combate somam aos stats e SO DEPOIS o total volta ao orcamento da especie."""
    peso = CONFIG_TREINO.peso_ponto_combate
    assert peso == 3.0
    base = stats(Forma("brasa", "adulto", "sereno", "brigao", "duelista"))
    total = sum(base.values())
    treino = {"forca": 1.0, "mira": 0.5}                   # pequeno: nenhum stat bate no teto
    n = com_treino(base, treino, True)
    assert sum(n.values()) == pytest.approx(total)
    assert n == pytest.approx(_norm({k: base[k] + peso * treino.get(k, 0.0) for k in STATS_V21}, total))
    # a ordem inversa (normalizar com os pontos crus e depois multiplicar o ganho pelo peso) daria outro vetor,
    # que nem respeita o orcamento
    cru = _norm({k: base[k] + treino.get(k, 0.0) for k in STATS_V21}, total)
    invertido = {k: base[k] + peso * (cru[k] - base[k]) for k in STATS_V21}
    assert invertido != pytest.approx(n)
    assert sum(invertido.values()) == pytest.approx(total)   # (ganhos somam zero nos dois casos)
    assert n["forca"] - base["forca"] != pytest.approx(peso * (cru["forca"] - base["forca"]))


def test_sementes_piloto_confirmatorias_e_antigas_disjuntas():
    p, c, a = set(CFG["sementes_piloto"]), set(CFG["sementes_confirmatorias"]), set(CFG["sementes_antigas"])
    assert len(p) == len(CFG["sementes_piloto"]) == CFG["N0_ovos_piloto"]
    assert len(c) == len(CFG["sementes_confirmatorias"]) >= 160
    assert not (p & c) and not (p & a) and not (c & a)
    assert CFG["rotulo_partidas_piloto"] != CFG["rotulo_partidas_confirmatoria"]


def test_condicao_neutra_desligada_por_padrao():
    assert CONFIG_ARENA_PESQUISA.condicao_neutra is False
    assert condicao_na_arena(0.97) == 0.97
    assert condicao_na_arena(0.97, ConfigArenaPesquisa(condicao_neutra=True)) == 1.0


def test_lutador_da_arena_sem_a_chave_e_o_de_antes():
    """run_treino.lutador_pet com a chave desligada monta o mesmo perfil de antes (condicao do cuidado)."""
    from run_treino import lutador_pet
    f = Forma("ferrugem", "adulto", "sereno", "colosso", "tita")
    ev = SimpleNamespace(forma=f, temperamento=None, carater_adulto={"resistente": 0.5}, condicao=0.97)
    pontos = {"vigor": 3.0, "forca": 1.0}
    antes = perfil(f, None, {"resistente": 0.5}, 0.97, None, treino=pontos, normalizar_treino=True)
    assert lutador_pet("x", ev, pontos, False).perfil == antes
    neutro = lutador_pet("x", ev, pontos, False, ConfigArenaPesquisa(condicao_neutra=True)).perfil
    assert neutro == perfil(f, None, {"resistente": 0.5}, 1.0, None, treino=pontos, normalizar_treino=True)
    assert neutro != antes
    # na campanha (absoluto) a condicao continua a do cuidado, com ou sem a chave
    assert (lutador_pet("x", ev, pontos, True, ConfigArenaPesquisa(condicao_neutra=True)).perfil
            == lutador_pet("x", ev, pontos, True).perfil)
