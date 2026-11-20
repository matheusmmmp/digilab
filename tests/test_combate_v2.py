"""Combate V2: regras, gambits, partida, replay, bots."""

import ast
import random
import sys
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.combate_v2.bots import FIXOS, GAMBITS, TODOS, bot, permutar  # noqa: E402
from digilab.combate_v2.gambits import (  # noqa: E402
    Condicao as C,
    GambitInvalido,
    ListaGambits,
    Regra,
    decidir_gambits,
    lista,
    regra,
)
from digilab.combate_v2.lutador import CondicaoFisica, Estilo, Lutador  # noqa: E402
from digilab.combate_v2.partida import jogar, reproduzir, reproduzir_acoes, sementes_de_rng  # noqa: E402
from digilab.combate_v2.regras import (  # noqa: E402
    Acao as A,
    AcaoIlegal,
    Distancia as D,
    estado_inicial,
    resolver,
    resultado,
)
from digilab.config import CONFIG_COMBATE_V2 as CFG  # noqa: E402


def est(dist=D.PERTO, guts=(50, 50), hp=(100.0, 100.0), regen=(0, 0), preparando=(False, False)):
    """Estado de teste; regen 0 por padrao para os numeros de guts ficarem legiveis."""
    e = estado_inicial(hp, guts, regen)
    lados = tuple(replace(e.lados[i], preparando=preparando[i]) for i in (0, 1))
    return replace(e, distancia=dist, lados=lados)


def hp(e):
    return (e.lados[0].hp, e.lados[1].hp)


# ------------------------------------------------------------ pureza


def test_resolucao_e_pura_e_nao_consome_rng():
    e = est()
    estado_rng = random.getstate()
    r1 = resolver(e, A.GOLPE_RAPIDO, A.DEFENDER)
    r2 = resolver(e, A.GOLPE_RAPIDO, A.DEFENDER)
    assert r1 == r2
    assert random.getstate() == estado_rng
    arvore = ast.parse((RAIZ / "digilab" / "combate_v2" / "regras.py").read_text(encoding="utf-8"))
    importados = {n.names[0].name for n in ast.walk(arvore) if isinstance(n, ast.Import)}
    importados |= {n.module for n in ast.walk(arvore) if isinstance(n, ast.ImportFrom) and n.module}
    assert "random" not in importados


# ------------------------------------------------------------ tabela de acoes


def test_avancar_e_recuar_movem_e_limitam():
    assert resolver(est(D.MEDIO), A.AVANCAR, A.DEFENDER)[0].distancia is D.PERTO
    assert resolver(est(D.MEDIO), A.RECUAR, A.DEFENDER)[0].distancia is D.LONGE
    assert resolver(est(D.PERTO), A.AVANCAR, A.AVANCAR)[0].distancia is D.PERTO
    assert resolver(est(D.LONGE), A.RECUAR, A.RECUAR)[0].distancia is D.LONGE
    assert resolver(est(D.MEDIO), A.AVANCAR, A.RECUAR)[0].distancia is D.MEDIO


def test_golpe_rapido_custo_e_dano():
    e, _ = resolver(est(), A.GOLPE_RAPIDO, A.AVANCAR)
    assert e.lados[0].guts == 50 - CFG.custo_golpe_rapido
    assert hp(e) == (100.0, 100.0 - CFG.dano_golpe_rapido)


def test_preparar_e_executar_pesado():
    e, _ = resolver(est(), A.PREPARAR_PESADO, A.AVANCAR)
    assert e.lados[0].preparando and e.lados[0].guts == 50 - CFG.custo_preparar_pesado
    assert hp(e) == (100.0, 100.0)
    e2, _ = resolver(e, A.PESADO, A.AVANCAR)
    assert hp(e2) == (100.0, 100.0 - CFG.dano_pesado)
    assert not e2.lados[0].preparando


def test_disparo_so_de_longe():
    e, _ = resolver(est(D.MEDIO), A.DISPARO, A.AVANCAR)
    assert hp(e) == (100.0, 100.0 - CFG.dano_disparo)
    e, _ = resolver(est(D.LONGE), A.DISPARO, A.DEFENDER)
    assert hp(e)[1] == 100.0 - CFG.dano_disparo * CFG.mult_defender


def test_defender_reduz_dano_quebra_de_guarda_e_ganha_guts():
    e, _ = resolver(est(), A.GOLPE_RAPIDO, A.DEFENDER)
    assert hp(e)[1] == 100.0 - CFG.dano_golpe_rapido * CFG.mult_defender
    assert e.lados[1].guts == 50 + CFG.guts_extra_defender
    prep = est(preparando=(True, False))
    e, _ = resolver(prep, A.PESADO, A.DEFENDER)
    assert hp(e)[1] == 100.0 - CFG.dano_pesado * CFG.mult_defender_contra_pesado


def test_esquivar_anula_pesado_e_disparo_mas_falha_contra_rapido():
    e, _ = resolver(est(preparando=(True, False)), A.PESADO, A.ESQUIVAR)
    assert hp(e)[1] == 100.0 and e.lados[1].guts == 50 - CFG.custo_esquivar
    e, _ = resolver(est(D.MEDIO), A.DISPARO, A.ESQUIVAR)
    assert hp(e)[1] == 100.0
    e, _ = resolver(est(), A.GOLPE_RAPIDO, A.ESQUIVAR)
    assert hp(e)[1] == 100.0 - CFG.dano_golpe_rapido


def test_carregar_ganha_guts_e_toma_mais_dano():
    e, _ = resolver(est(), A.GOLPE_RAPIDO, A.CARREGAR)
    assert e.lados[1].guts == 50 + CFG.guts_carregar
    assert hp(e)[1] == 100.0 - CFG.dano_golpe_rapido * CFG.mult_carregar


def test_guts_limitado_ao_maximo_e_regeneracao():
    e, _ = resolver(est(guts=(95, 50), regen=(8, 8)), A.CARREGAR, A.DEFENDER)
    assert e.lados[0].guts == CFG.guts_max
    assert e.lados[1].guts == 50 + 8 + CFG.guts_extra_defender


# ------------------------------------------------------------ ordem de resolucao


def test_golpe_rapido_interrompe_quem_prepara():
    e, r = resolver(est(), A.GOLPE_RAPIDO, A.PREPARAR_PESADO)
    assert r.interrompido == (False, True)
    assert not e.lados[1].preparando
    assert hp(e)[1] == 100.0 - CFG.dano_golpe_rapido


def test_pesado_executando_tem_armadura():
    e, r = resolver(est(preparando=(False, True)), A.GOLPE_RAPIDO, A.PESADO)
    assert r.interrompido == (False, False)
    assert hp(e) == (100.0 - CFG.dano_pesado, 100.0 - CFG.dano_golpe_rapido)


def test_fuga_no_turno_da_preparacao_faz_o_pesado_errar():
    e, _ = resolver(est(), A.PREPARAR_PESADO, A.RECUAR)
    assert e.distancia is D.MEDIO
    e2, r = resolver(e, A.PESADO, A.DEFENDER)
    assert r.pesado_errou == (True, False) and hp(e2) == (100.0, 100.0)


def test_recuar_no_turno_da_execucao_nao_escapa():
    e, r = resolver(est(preparando=(True, False)), A.PESADO, A.RECUAR)
    assert hp(e)[1] == 100.0 - CFG.dano_pesado and e.distancia is D.MEDIO


def test_dano_simultaneo_e_ko_duplo_empata():
    e, _ = resolver(est(hp=(5.0, 5.0)), A.GOLPE_RAPIDO, A.GOLPE_RAPIDO)
    assert resultado(e) == (0.5, "ko")


def test_limite_de_turnos_decide_por_fracao_de_hp():
    e = replace(est(hp=(100.0, 100.0)), turno=CFG.t_max)
    e = replace(e, lados=(replace(e.lados[0], hp=50.0), replace(e.lados[1], hp=60.0)))
    assert resultado(e) == (0.0, "limite")
    e = replace(e, lados=(replace(e.lados[0], hp=60.0), e.lados[1]))
    assert resultado(e) == (0.5, "limite")


# ------------------------------------------------------------ acoes ilegais


@pytest.mark.parametrize("dist,acao,guts", [
    (D.MEDIO, A.GOLPE_RAPIDO, 50),
    (D.PERTO, A.DISPARO, 50),
    (D.LONGE, A.PREPARAR_PESADO, 50),
    (D.PERTO, A.GOLPE_RAPIDO, 5),
    (D.PERTO, A.ESQUIVAR, 10),
    (D.PERTO, A.PESADO, 50),
])
def test_acao_ilegal_levanta_erro(dist, acao, guts):
    with pytest.raises(AcaoIlegal):
        resolver(est(dist, guts=(guts, 50)), acao, A.DEFENDER)


def test_quem_prepara_nao_pode_escolher_outra_acao():
    with pytest.raises(AcaoIlegal):
        resolver(est(preparando=(True, False)), A.DEFENDER, A.DEFENDER)


# ------------------------------------------------------------ gambits


def test_primeira_regra_valida_dispara_e_ilegal_e_pulada():
    g = lista([
        regra(C("distancia_eh", (D.LONGE,)), A.AVANCAR),       # condicao falsa
        regra(C("sempre"), A.DISPARO),                         # ilegal perto: pulada
        regra(C("guts_proprio_acima", (40,)), A.GOLPE_RAPIDO),  # dispara
        regra(C("sempre"), A.RECUAR),
    ], A.DEFENDER)
    assert decidir_gambits(g, 0.0, est(), 0, random.Random(1)) == (A.GOLPE_RAPIDO, 2)
    assert decidir_gambits(g, 0.0, est(guts=(5, 50)), 0, random.Random(1)) == (A.RECUAR, 3)


def test_regra_final_quando_nada_dispara():
    g = lista([regra(C("oponente_preparando"), A.ESQUIVAR)], A.CARREGAR)
    assert decidir_gambits(g, 0.0, est(), 0, random.Random(1)) == (A.CARREGAR, 1)


def test_lista_sem_regra_final_valida_levanta_erro():
    with pytest.raises(GambitInvalido):
        ListaGambits((), None)  # type: ignore[arg-type]
    with pytest.raises(GambitInvalido):
        ListaGambits((), Regra((C("sempre"),), A.GOLPE_RAPIDO))
    with pytest.raises(GambitInvalido):
        ListaGambits((), Regra((C("oponente_preparando"),), A.DEFENDER))


def test_limites_da_linguagem():
    with pytest.raises(GambitInvalido):
        lista([regra(C("sempre"), A.DEFENDER)] * (CFG.max_regras + 1), A.DEFENDER)
    with pytest.raises(GambitInvalido):
        lista([regra((C("sempre"), C("sempre"), C("sempre")), A.DEFENDER)], A.DEFENDER)
    with pytest.raises(GambitInvalido):
        lista([regra(C("hp_proprio_abaixo", (0.3,)), A.DEFENDER)], A.DEFENDER)
    with pytest.raises(GambitInvalido):
        lista([regra(C("inventada"), A.DEFENDER)], A.DEFENDER)
    with pytest.raises(GambitInvalido):
        lista([regra(C("oponente_repete", (A.DEFENDER, 1)), A.DEFENDER)], A.DEFENDER)


def test_condicoes_de_historico_do_oponente():
    e = est()
    e = replace(e, lados=(e.lados[0], replace(e.lados[1], historico=(A.AVANCAR, A.DEFENDER, A.DEFENDER))))
    assert C("oponente_repete", (A.DEFENDER, 2)).vale(e, 0, CFG)
    assert not C("oponente_repete", (A.DEFENDER, 3)).vale(e, 0, CFG)
    assert C("oponente_frequente", (A.DEFENDER,)).vale(e, 0, CFG)      # 2/5 = 0.4
    assert not C("oponente_frequente", (A.AVANCAR,)).vale(e, 0, CFG)   # 1/5


def test_pesado_automatico_nao_consome_rng_e_exploracao_so_legal():
    g = GAMBITS["agressivo"]
    rng = random.Random(3)
    antes = rng.getstate()
    assert decidir_gambits(g, 1.0, est(preparando=(True, False)), 0, rng) == (A.PESADO, "pesado_automatico")
    assert rng.getstate() == antes
    for s in range(200):
        acao, motivo = decidir_gambits(g, 1.0, est(D.MEDIO, guts=(12, 50)), 0, random.Random(s))
        assert motivo == "exploracao" and acao in (A.AVANCAR, A.RECUAR, A.DEFENDER, A.CARREGAR)


# ------------------------------------------------------------ partida, replay, espelho


def test_replay_bit_a_bit_de_todos_os_pares():
    for a in TODOS:
        for b in TODOS:
            p = jogar(bot(a), bot(b), 99)
            r = reproduzir(list(p.log), bot(a), bot(b))
            assert r.log == p.log
            assert reproduzir_acoes(list(p.log)) == p.estado_final


def test_evento_desconhecido_no_log_levanta_erro():
    p = jogar(bot("agressivo"), bot("atirador"), 5)
    log = list(p.log) + [{"tipo": "clima"}]
    with pytest.raises(ValueError, match="desconhecido"):
        reproduzir(log, bot("agressivo"), bot("atirador"))
    with pytest.raises(ValueError, match="desconhecido"):
        reproduzir_acoes(log)


def test_trocar_os_lados_espelha_o_resultado():
    for a, b in [("agressivo", "atirador"), ("adaptativo", "aleatorio"), ("contragolpe", "oraculo")]:
        for s in range(10):
            sa, sb = sementes_de_rng(s)
            p = jogar(bot(a), bot(b), s)
            q = jogar(bot(b), bot(a), s, sementes_rng=(sb, sa))
            assert q.pontos_a == 1.0 - p.pontos_a
            assert q.estado_final == p.estado_final.espelhado()
            ta = [(e["a"], e["b"]) for e in p.log if e["tipo"] == "turno"]
            tb = [(e["b"], e["a"]) for e in q.log if e["tipo"] == "turno"]
            assert ta == tb


def test_condicao_e_estilo_sao_independentes():
    forte = CondicaoFisica(CFG.hp_neutro * 2, 90, 20)
    x = Lutador("x", forte, bot("tartaruga").estilo)
    assert x.estilo is bot("tartaruga").estilo or x.estilo == bot("tartaruga").estilo
    assert x.hash() != bot("tartaruga").hash()
    with pytest.raises(ValueError):
        CondicaoFisica(0, 50, 8)


def test_bots_fixos_e_adaptativo_sao_gambits_e_oraculo_nao():
    for nome in FIXOS + ("adaptativo",):
        e = bot(nome).estilo
        assert isinstance(e, Estilo) and not e.fora_da_linguagem
    assert bot("oraculo").estilo.fora_da_linguagem
    assert bot("aleatorio").estilo.epsilon == 1.0
    assert {bot(n).estilo.epsilon for n in FIXOS if n != "aleatorio"} == {CFG.epsilon_bots}


def test_permutacoes_sao_distintas_e_mantem_a_regra_final():
    perms = permutar("adaptativo", 7007, 5)
    ordens = [o for o, _ in perms]
    assert len(set(ordens)) == 5 and tuple(range(len(ordens[0]))) not in ordens
    for _, g in perms:
        assert g.final == GAMBITS["adaptativo"].final
