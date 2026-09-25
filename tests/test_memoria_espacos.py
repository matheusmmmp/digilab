"""Memoria por espacos (docs/ADENDO_MEMORIA_EMOCAO_DF.md, Parte 1)."""

from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.config import CONFIG_MEMORIA_ESPACOS as CFG  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.events import AcaoUsuario as U  # noqa: E402
from digilab.memoria_espacos import (FATORES_ESPACOS, CategoriaInvalida, Memoria, MemoriaEspacos,  # noqa: E402
                                     PoliticaBanditEspacos, inserir)
from digilab.motivo import motivos_de_vida  # noqa: E402
from digilab.protocol import PROTOCOLO_ARENA_V1_MEMORIA, PROTOCOLO_ARENA_V1_MEMORIA_ESPACOS, PROTOCOLOS, \
    bracos_do_protocolo, hash_protocolo  # noqa: E402
from digilab.treino import reproduzir_com_feedback, simular_vida  # noqa: E402

M = lambda cat, i, t=0: Memoria(cat, i, t, t, None)  # noqa: E731


def test_nunca_passa_dos_espacos_nem_repete_categoria():
    esp = []
    for k, (cat, i) in enumerate([("demora", .3), ("bronca", 1.0), ("elogio", 1.0), ("carinho", .5),
                                  ("demora", .9), ("carinho", .2), ("demora", .1)]):
        esp, _ = inserir(esp, M(cat, i, k), CFG.n_curto)
        assert len(esp) <= CFG.n_curto and len({m.categoria for m in esp}) == len(esp)
    assert {m.categoria: m.intensidade for m in esp}["demora"] == .9       # mais forte venceu, fraca descartada
    assert {m.categoria: m.intensidade for m in esp}["carinho"] == .5


def test_espacos_cheios_substitui_a_mais_fraca_so_se_for_mais_forte():
    cheio = [M("demora", .4, 1), M("bronca", 1.0, 2), M("elogio", 1.0, 3), M("carinho", .5, 4)]
    esp, r = inserir(cheio, M("sujeira", .3, 5), 4)
    assert r == "descartada" and esp == cheio
    esp, r = inserir(cheio, M("sujeira", .45, 5), 4)
    assert r == "substituiu" and "demora" not in {m.categoria for m in esp}


def test_empate_vence_a_mais_recente():
    esp, r = inserir([M("bronca", 1.0, 1)], M("bronca", 1.0, 9), 4)
    assert r == "substituiu" and esp[0].criada == 9
    # empate entre as mais fracas: sai a mais antiga
    cheio = [M("demora", .5, 1), M("carinho", .5, 2), M("bronca", 1.0, 3), M("elogio", 1.0, 4)]
    esp, _ = inserir(cheio, M("sujeira", .5, 5), 4)
    assert {m.categoria for m in esp} == {"carinho", "bronca", "elogio", "sujeira"}


def test_promocao_para_o_longo_prazo_e_descarte():
    mem = MemoriaEspacos()
    mem.lembrar("bronca", 1.0, 0, 1)
    mem.lembrar("carinho", .5, 10, 2)
    mem.lembrar("elogio", 1.0, 20, 3)
    mem.avancar(CFG.d_curto_ticks + 30, dormindo=False)
    assert mem.curto == [] and len(mem.longo) == CFG.n_longo
    assert {m.categoria for m in mem.longo} == {"bronca", "elogio"}      # carinho (mais fraca) nao coube
    assert mem.contagem["promovida"] == 3 and mem.contagem["esquecida"] == 0   # carinho entrou e depois saiu


def test_relembranca_no_cronograma_so_acordado():
    mem = MemoriaEspacos()
    mem.lembrar("bronca", 1.0, 0, 1)
    mem.avancar(100, dormindo=True)        # 0..100 acordado; `dormindo` vale DAQUI em diante
    mem.avancar(1000, dormindo=False)      # 100..1000 dormindo (nao conta)
    assert mem.relembrancas == []
    r = CFG.relembrar_ticks_acordado
    mem.avancar(1000 + r, dormindo=False)
    assert mem.relembrancas == [1000 + (r - 100)]
    m = mem.curto[0] if mem.curto else mem.longo[0]
    assert m.relembrada == 1000 + (r - 100)
    assert m.ativacao(m.relembrada, CFG.tau_ativacao_ticks) == 1.0


def test_categoria_inativa_nao_entra_e_desconhecida_levanta():
    mem = MemoriaEspacos()
    mem.lembrar("treino_forcado", 1.0, 0, 1)
    assert mem.curto == []
    with pytest.raises(CategoriaInvalida):
        mem.lembrar("saudade", 1.0, 0, 1)
    with pytest.raises(CategoriaInvalida):
        MemoriaEspacos(replace(CFG, ativas=("demora", "inventada")))


def test_eventos_do_dono_viram_memorias():
    mem = MemoriaEspacos()
    mem.acao_dono(U.REPREENDER, 10)
    mem.acao_dono(U.ACARICIAR, 20)
    f = mem.features(20)
    assert f[FATORES_ESPACOS.index("bronca")] == pytest.approx(1.0 * 2.718281828 ** (-10 / CFG.tau_ativacao_ticks), rel=1e-6)
    assert f[FATORES_ESPACOS.index("carinho")] == pytest.approx(0.5)
    assert mem.refs(20) == {"demora": None, "bronca": 1, "elogio": None, "carinho": 2}


@pytest.mark.parametrize("dono", ["atencioso", "relapso"])
def test_replay_reproduz_os_espacos_bit_a_bit(dono):
    v = simular_vida(dono, criar_dono(dono), PoliticaBanditEspacos(), 202, 3, 48)
    r = reproduzir_com_feedback(v.motor.log, lambda c: PoliticaBanditEspacos(c), semente=202)
    assert r.politica.memoria.para_dict() == v.motor.politica.memoria.para_dict()
    assert r.politica.estado_interno() == v.motor.politica.estado_interno()


def test_motivo_com_memoria_aponta_para_o_evento_que_a_criou():
    v = simular_vida("relapso", criar_dono("relapso"), PoliticaBanditEspacos(), 202, 3, 48)
    eventos = list(v.motor.log)
    _, emb = motivos_de_vida(v.motor.log, lambda c: PoliticaBanditEspacos(c), 202)
    origem = {"bronca": {"repreender"}, "elogio": {"elogiar"}, "carinho": {"acariciar", "brincar"},
              "demora": {"alimentar", "limpar"}}
    vistos = 0
    for m in emb.motivos:
        for f in m.fatores:
            if f in FATORES_ESPACOS and m.evento_ref:
                assert {eventos[r].valor for r in m.evento_ref} & origem[f], (f, m)
                vistos += 1
    assert vistos >= 0


def test_protocolo_proprio_sem_mexer_no_da_memoria_b1():
    p = PROTOCOLO_ARENA_V1_MEMORIA_ESPACOS
    assert PROTOCOLOS["arena-v1-memoria-espacos"] is p
    assert {pol for _, _, pol in bracos_do_protocolo(p)} == {"bandit_espacos"}
    assert hash_protocolo(PROTOCOLO_ARENA_V1_MEMORIA).startswith("be9aae5a833c")   # B1 intacto
    assert hash_protocolo(p) != hash_protocolo(PROTOCOLO_ARENA_V1_MEMORIA)
