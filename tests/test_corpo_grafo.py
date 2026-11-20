"""V2, corpo, secao 18: o grafo de reacoes validado antes da run (docs/TAREFA_V2_CORPO_DRIVES.md; decisao D-3).

A tabela unica (corpo.grafo_do_corpo, corpo_grafo.Grafo) passa as quatro checagens em toda combinacao de sub-chaves; o Corpo usa a tabela
(a lista dos quimicos, os receptores, as meias-vidas e o tick vem dela); cada checagem falha alto numa tabela feita para falhar; e o
relato lista os pares com meias-vidas na mesma ordem. O G2 (as vidas de hoje iguais com a quimica, a digestao e a Vida) e o da suite:
tests/test_corpo.py, tests/test_corpo_quimica.py e os gabaritos. So as sementes dos testes.
"""
from __future__ import annotations

import sys
from dataclasses import fields, replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab import corpo as cp  # noqa: E402
from digilab.config import CONFIG_PADRAO, ConfigCorpo  # noqa: E402
from digilab.corpo import Corpo, grafo_do_corpo, quimicos_de, taxas_de  # noqa: E402
from digilab.corpo_grafo import Emissor, Grafo, GrafoInvalido, Leitura, Quimico, Reacao, checar, ciclos  # noqa: E402
from digilab.state import Estado  # noqa: E402

CFG = CONFIG_PADRAO
C = ConfigCorpo().escala
CHAVES = {
    "quimica": ConfigCorpo(ligada=True),
    "digestao": ConfigCorpo(ligada=True, digestao=True),
    "vida": ConfigCorpo(ligada=True, digestao=True, vida=True),
    "novos": ConfigCorpo(ligada=True, digestao=True, vida=True, drives_novos=True),
    "gestos": ConfigCorpo(ligada=True, digestao=True, vida=True, drives_novos=True, gestos=True),
    "gestos_sem_medo": ConfigCorpo(ligada=True, digestao=True, vida=True, drives_novos=True, gestos=True, medo_da_mao=0),
}


def _grafo(nome: str, com_mundo: bool = False) -> Grafo:
    cc = CHAVES[nome]
    return grafo_do_corpo(CFG, cc, taxas_de(CFG, cc), com_mundo)


# ================================================================== a tabela de verdade passa
@pytest.mark.parametrize("com_mundo", [False, True])
@pytest.mark.parametrize("nome", list(CHAVES))
def test_as_quatro_checagens_passam_em_toda_combinacao(nome, com_mundo):
    g = _grafo(nome, com_mundo)
    relato = checar(g)
    assert g.nomes == quimicos_de(CHAVES[nome], com_mundo)
    assert relato["so_pelo_teto"] == []                     # todo quimico tem um sumidouro alem do corte
    assert all(n * 1 < d for c in relato["lacos"] for n, d in [c["ganho"]])
    gestos = CHAVES[nome].gestos
    # o relato: dor (60) e susto (30), emitidos juntos pelo tapa, tem meias-vidas na mesma ordem; o estresse (1440) nao
    assert relato["pares_meia_vida_mesma_ordem"] == ([["dor", "susto"]] if gestos else [])
    if CHAVES[nome].drives_novos:
        assert ("curiosidade" in g.nomes) is com_mundo     # CD-8
        le = {x.quimico for x in g.emissor("estresse_drives").le}
        assert le == {"fome", "desconforto", "cansaco", "tedio", "solidao"} | ({"curiosidade"} if com_mundo else set()) | (
            {"dor"} if gestos else set())


def test_o_grafo_de_hoje_e_aciclico_e_o_susto_entra_no_carinho():
    """sem laco nenhum hoje: o estresse le os drives e a dor, o dano le a privacao, o susto corta o carinho, e nada volta"""
    g = _grafo("gestos", com_mundo=True)
    from digilab.corpo_grafo import _arestas
    arestas = _arestas(g)
    assert ciclos(arestas) == []
    assert arestas[("susto", "estresse")] == (CHAVES["gestos"].carinho_estresse, C)          # o medo da mao: + susto, - alivio
    assert arestas[("dor", "estresse")] == (1, CHAVES["gestos"].estresse_divisor)
    assert arestas[("fome", "dano")] == (1, 1)                                                 # o degrau da privacao
    sem_medo = _grafo("gestos_sem_medo", com_mundo=True)
    assert _arestas(sem_medo)[("susto", "estresse")] == (0, C)


def test_tabela_e_a_mesma_que_o_corpo_usa():
    """o Corpo carrega a tabela, a confere na carga e tira dela os quimicos, os receptores e as meias-vidas"""
    cc = CHAVES["gestos"]
    corpo = Corpo.de_estado(Estado(), CFG, cc, com_mundo=True)
    assert corpo.quimicos == corpo.grafo.nomes
    assert set(corpo.receptores()) == {q.receptor for q in corpo.grafo.receptores()}
    assert {q.nome: q.k_meia_vida for q in corpo.grafo.quimicos if q.k_meia_vida} == {
        "estresse": cc.k_meia_vida_estresse, "dor": cc.k_meia_vida_dor, "susto": cc.k_meia_vida_susto}
    assert corpo.relato_grafo["pares_meia_vida_mesma_ordem"] == [["dor", "susto"]]


def test_o_tick_sai_da_tabela():
    """um emissor tirado da tabela some do tick: o Corpo nao tem uma segunda lista"""
    cc = CHAVES["quimica"]
    a, b = Corpo.de_estado(Estado(), CFG, cc), Corpo.de_estado(Estado(), CFG, cc)
    b.grafo = replace(b.grafo, emissores=tuple(e for e in b.grafo.emissores if e.nome != "tristeza_tick"))
    a.passo(Estado())
    b.passo(Estado())
    assert a.q["tristeza"] == b.q["tristeza"] + a.t.tristeza_por_tick and a.q["fome"] == b.q["fome"]


def test_a_carga_do_corpo_confere_o_grafo(monkeypatch):
    ruim = _grafo("quimica")
    ruim = replace(ruim, emissores=ruim.emissores + (Emissor("fantasma", "tick", 1, (("ectoplasma", 1),)),))
    monkeypatch.setattr(cp, "grafo_do_corpo", lambda *a, **k: ruim)
    with pytest.raises(GrafoInvalido, match="nao fechado"):
        Corpo.de_estado(Estado(), CFG, CHAVES["quimica"])


# ================================================================== cada checagem falha alto
def _q(nome, teto=C, descarte=True, **kw):
    return Quimico(nome, teto, descarte, **kw)


def test_fechado():
    g = Grafo((_q("a"),), (Reacao("r", ("a",), ("b",), 10),), ())
    with pytest.raises(GrafoInvalido, match="nao fechado"):
        checar(g)
    g = Grafo((_q("a"),), (), (Emissor("e", "limiar", 2, (("a", 1),), (Leitura("x", 1, 2),), 0, 2, True),))
    with pytest.raises(GrafoInvalido, match="nao fechado"):
        checar(g)


def test_sumidouro():
    # sem reacao que o gaste, sem emissor que o reduza, sem meia-vida e sem teto com descarte
    g = Grafo((_q("a", teto=C, descarte=False),), (), (Emissor("sobe", "tick", 1, (("a", 5),)),))
    with pytest.raises(GrafoInvalido, match="sem sumidouro"):
        checar(g)
    # a meia-vida, sozinha, basta
    checar(Grafo((_q("a", descarte=False, meia_vida=30, k_meia_vida=1497),), (), (Emissor("sobe", "tick", 1, (("a", 5),)),)))


def test_automantido():
    # consumido por uma reacao, sem nada que o reponha e sem teto declarado
    g = Grafo((_q("a", teto=0, descarte=False), _q("b")), (Reacao("r", ("a", "b"), (), 10),), (Emissor("sobe_b", "tick", 1, (("b", 1),)),))
    with pytest.raises(GrafoInvalido, match="automantido"):
        checar(g)
    # com o teto declarado, passa
    checar(Grafo((_q("a"), _q("b")), (Reacao("r", ("a", "b"), (), 10),), (Emissor("sobe_b", "tick", 1, (("b", 1),)),)))


def _laco(ganho_ab, ganho_ba):
    return Grafo((_q("a"), _q("b")), (), (
        Emissor("a_faz_b", "limiar", 2, (("b", 1),), (Leitura("a", *ganho_ab),), 0, 2, True),
        Emissor("b_faz_a", "limiar", 2, (("a", 1),), (Leitura("b", *ganho_ba),), 0, 2, True),
        Emissor("tira_a", "estimulo", 0, (("a", -1),)), Emissor("tira_b", "estimulo", 0, (("b", -1),))))


def test_laco_de_ganho():
    with pytest.raises(GrafoInvalido, match="ganho >= 1"):
        checar(_laco((1, 1), (1, 1)))                     # 1 x 1 = 1
    with pytest.raises(GrafoInvalido, match="ganho >= 1"):
        checar(_laco((3, 2), (2, 3)))                     # 3/2 x 2/3 = 1, em inteiros
    relato = checar(_laco((1, 2), (3, 4)))                # 3/8 < 1: passa e sai no relato
    assert relato["lacos"] == [{"ciclo": ["a", "b"], "ganho": [3, 8]}]
    # o susto que corta um consumo e influencia positiva (o sinal da leitura vezes o do efeito)
    g = Grafo((_q("a"), _q("b")), (), (
        Emissor("b_corta_tira_a", "estimulo", 0, (("a", -10),), (Leitura("b", 1, 1, -1),)),
        Emissor("a_faz_b", "limiar", 2, (("b", 1),), (Leitura("a", 1, 1),), 0, 2, True),
        Emissor("tira_b", "estimulo", 0, (("b", -1),))))
    with pytest.raises(GrafoInvalido, match="ganho >= 1"):
        checar(g)


def test_forma_da_tabela():
    with pytest.raises(GrafoInvalido, match="repetido"):
        checar(Grafo((_q("a"), _q("a")), (), ()))
    with pytest.raises(GrafoInvalido, match="meia-vida e k"):
        checar(Grafo((_q("a", meia_vida=30),), (), ()))
    with pytest.raises(GrafoInvalido, match="gatilho"):
        checar(Grafo((_q("a"),), (), (Emissor("e", "lua_cheia", 1, (("a", 1),)),)))
    with pytest.raises(GrafoInvalido, match="efeitos"):
        checar(Grafo((_q("a"),), (), (Emissor("e", "tick", 1, (("a", 0),)),)))
    with pytest.raises(GrafoInvalido, match="fase"):
        checar(Grafo((_q("a"),), (), (Emissor("e", "estimulo", 1, (("a", -1),)),)))


def test_campos_da_config_registrados():
    assert set(cp.PARAMETROS_CORPO) == {f.name for f in fields(ConfigCorpo)}
