"""Escala de stats (TAREFA_PLANILHA_PROGRESSAO, Parte C): chave desligada nao muda nada; invariancia de escala.

Invariancia (requisito duro da Parte B): multiplicar a escala dos DOIS lutadores pelo mesmo fator da exatamente a
mesma luta. Conferido nas sementes de validacao da bateria V21C, com fatores 2, 10 e 37, em lutas do mesmo estagio,
entre estagios (adulto x adolescente treinado) e pet x NPC da campanha.
"""
from dataclasses import replace
from fractions import Fraction

import pytest

from digilab.campanha import REGRAS_CAMPANHA, npc
from digilab.combate_v2.v21.bots import FORMAS, lutador_adolescente, lutador_adulto
from digilab.combate_v2.v21.catalogo import LINHA_DA_FORMA, Forma, carater_canonico, escala_de, perfil
from digilab.combate_v2.v21.partida import Lutador, jogar
from digilab.config import (CONFIG_BATERIA_V21, CONFIG_COMBATE_V21C, CONFIG_ESCALA, CONFIG_ESCALA_LIGADA, STATS_V21)
from digilab.protocol import derivar_semente

SEMENTES_V21C = (4101, 4202, 4303, 4404, 4505)      # validacao da bateria V21C (artifacts_combate_v21c/validacao)
FATORES = (2, 10, 37)
R = REGRAS_CAMPANHA


def _escalado(lut: Lutador, k) -> Lutador:
    return replace(lut, perfil=replace(lut.perfil, escala=lut.perfil.escala * k))


def _luta(p):
    """o que a luta e: turnos (acoes e motivos) e o fim (resultado e vida de cada lado); sem o cabecalho, que traz a escala"""
    return [e for e in p.log if e["tipo"] != "cabecalho"]


def _pares():
    cfg = CONFIG_COMBATE_V21C
    e = CONFIG_ESCALA_LIGADA
    tr22 = {k: CONFIG_ESCALA_LIGADA.treino_e4 / len(STATS_V21) for k in STATS_V21}
    for esp in ("brasa", "ferrugem"):
        for f in FORMAS[:4]:
            ad = lutador_adulto(f, esp, cfg, escala=e)
            yield "mesmo estagio", ad, lutador_adulto(FORMAS[-1], esp, cfg, escala=e)
            yield "entre estagios", ad, lutador_adolescente(LINHA_DA_FORMA[f], esp, carater_canonico(f, cfg), cfg,
                                                            escala=e, treino=tr22)
    pet = Lutador("pet", perfil(Forma("brasa", "crianca", "sereno"), None, None, 1.0, cfg,
                                treino={"forca": 4.0, "vigor": 4.0}, escala=e), npc("tier1_brutamontes").gambits, 0.05)
    yield "pet x NPC", pet, npc("tier1_brutamontes", escala=e)


@pytest.mark.parametrize("k", FATORES)
def test_invariancia_de_escala(k):
    n = 0
    for tipo, a, b in _pares():
        for s in SEMENTES_V21C:
            sp = derivar_semente("teste-escala", tipo, s, a.nome, b.nome)
            p0 = jogar(a, b, sp, R)
            pk = jogar(_escalado(a, k), _escalado(b, k), sp, R)
            assert _luta(p0) == _luta(pk), f"{tipo}: {a.nome} x {b.nome}, semente {s}, fator {k}"
            n += 1
    assert n >= 50


def test_fator_racional_tambem():
    a = lutador_adulto("tita", "limo", CONFIG_COMBATE_V21C, escala=CONFIG_ESCALA_LIGADA)
    b = lutador_adolescente("colosso", "limo", carater_canonico("tita"), CONFIG_COMBATE_V21C, escala=CONFIG_ESCALA_LIGADA)
    k = Fraction(7, 3)
    assert _luta(jogar(a, b, 99, R)) == _luta(jogar(_escalado(a, k), _escalado(b, k), 99, R))


def test_desligada_nao_muda_nada():
    """ConfigEscala(ligada=False) = sem escala: mesmo perfil, mesmo dicionario, mesma luta."""
    cfg = CONFIG_COMBATE_V21C
    for f in FORMAS:
        a0, a1 = lutador_adulto(f, "cirro", cfg), lutador_adulto(f, "cirro", cfg, escala=CONFIG_ESCALA)
        assert a0.perfil == a1.perfil and a1.perfil.escala is None and "escala" not in a1.perfil.para_dict()
    ad = lutador_adulto("furioso", "brasa", cfg, escala=CONFIG_ESCALA)
    adol = lutador_adolescente("brigao", "brasa", carater_canonico("furioso"), cfg, escala=CONFIG_ESCALA)
    for s in SEMENTES_V21C:
        assert jogar(ad, adol, s, R).log == jogar(lutador_adulto("furioso", "brasa", cfg),
                                                   lutador_adolescente("brigao", "brasa", carater_canonico("furioso"), cfg), s, R).log
    assert npc("tier2_porteiro", escala=CONFIG_ESCALA) == npc("tier2_porteiro")


def test_mesmo_estagio_sem_treino_razao_um():
    """Dois adultos sem treino: E igual, razao 1 exata, a luta e a de sempre (a bateria V21C nao muda entre adultos)."""
    cfg = CONFIG_COMBATE_V21C
    for s in SEMENTES_V21C:
        a, b = lutador_adulto("espelho", "limo", cfg), lutador_adulto("muralha", "limo", cfg)
        ae, be = (lutador_adulto(x, "limo", cfg, escala=CONFIG_ESCALA_LIGADA) for x in ("espelho", "muralha"))
        assert _luta(jogar(a, b, s, R)) == _luta(jogar(ae, be, s, R))


def test_escala_e_vida():
    e = CONFIG_ESCALA_LIGADA
    assert escala_de("adulto", 0, e) == 1500
    assert escala_de("crianca", 8, e) == Fraction(248)
    assert escala_de("adulto", 36, e) == Fraction(1500) * Fraction("2.08")
    # com a escala a vida perde o multiplicador de estagio (0,6 na crianca); o guts continua com ele
    f = Forma("brasa", "crianca", "sereno")
    p0, p1 = perfil(f, cfg=CONFIG_COMBATE_V21C), perfil(f, cfg=CONFIG_COMBATE_V21C, escala=e)
    assert p1.hp_max == pytest.approx(p0.hp_max / 0.6) and p1.guts_max == p0.guts_max
    assert CONFIG_BATERIA_V21.taxa_min_e4 == e.taxa_min_e4    # E4' usa a mesma faixa do E4
