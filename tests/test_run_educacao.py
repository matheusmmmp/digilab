"""Fase 3 (PLANO_ANALISE_V3): integracao da vida de pesquisa com educacao, lesoes e sparring."""
from __future__ import annotations

import random
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

from digilab.config import CONFIG_EDUCACAO_LIGADA, CONFIG_LESOES_LIGADA, CONFIG_SPARRING  # noqa: E402
from digilab.donos import Visao  # noqa: E402
from digilab.donos_educacao import DonoComEducacao, simular_vida_educacao  # noqa: E402
from digilab.educacao import epsilon_disciplina, politica_no_tick_educacao, reproduzir_educacao  # noqa: E402
from digilab.events import ACOES_EDUCACAO, AcaoUsuario  # noqa: E402
from digilab.evolucao import ovo  # noqa: E402
from digilab.temperamento import sortear  # noqa: E402
from run_educacao import T_ADOL, _fabricas, rival_por_nome, ticks_sparring  # noqa: E402

S = 69001


def test_epsilon_pela_disciplina():
    assert epsilon_disciplina(100) == pytest.approx(CONFIG_EDUCACAO_LIGADA.epsilon_base_pet)
    assert epsilon_disciplina(0) == pytest.approx(CONFIG_EDUCACAO_LIGADA.epsilon_base_pet
                                                  + CONFIG_EDUCACAO_LIGADA.delta_epsilon_indisciplina)


def test_sparring_no_adolescente_e_lutador_faz_mais():
    assert len(ticks_sparring("atencioso")) == CONFIG_SPARRING.lutas
    assert len(ticks_sparring("lutador")) == CONFIG_SPARRING.lutas_braco_lutador
    assert all(T_ADOL < t < T_ADOL + 1080 and t % 15 == 0 for t in ticks_sparring("lutador"))
    assert rival_por_nome("sparring:brigao@brasa").nome.startswith("adolescente-brigao")
    with pytest.raises(ValueError):
        rival_por_nome("npc:tier1_brutamontes")


@pytest.fixture(scope="module")
def vida():
    esp, t_ovo = ovo(S)
    tmp = sortear(S)
    fp, fm_base, fm, pet = _fabricas("atencioso", S, esp, tmp, t_ovo)
    v = simular_vida_educacao("atencioso", S, 3, esp, tmp, cl=CONFIG_LESOES_LIGADA, sparring=ticks_sparring("atencioso"),
                              rival_sparring=pet.rival, lutador_do_pet=pet.lutador, rival_por_nome=rival_por_nome)
    return v, esp, tmp, t_ovo, fp, fm_base


def test_vida_com_sparring_rejoga_e_qualificacao_gravada(vida):
    v, esp, tmp, t_ovo, fp, fm_base = vida
    m = v.motor
    assert len(m.historico_lutas) == CONFIG_SPARRING.lutas and all(h["estagio"] == "adolescente" for h in m.historico_lutas)
    fp2, _, fm2, _ = _fabricas("atencioso", S, esp, tmp, t_ovo)
    r = reproduzir_educacao(m.log, fp2, semente=S, fabrica_motor=fm2)
    assert r.historico_lutas == m.historico_lutas and r.estado() == m.estado() and r.transicoes == m.transicoes
    q = m.transicoes["adulto"]["vitorias"]
    assert q["lutas"] == CONFIG_SPARRING.lutas and m.adulto_liberado == q["qualifica"]


def test_politica_parcial_ignora_lutas_e_corta_no_tick(vida):
    v, esp, tmp, t_ovo, fp, fm_base = vida
    r = reproduzir_educacao(v.motor.log, fp, semente=S, fabrica_motor=fm_base, ate_tick=T_ADOL, pular_lutas=True)
    assert r.estado()["tick"] == T_ADOL and all(e.tick < T_ADOL for e in r.log)
    assert politica_no_tick_educacao(v.motor.log, fp, S, T_ADOL, fm_base) is not None


def _visao(estado):
    return Visao(estado=estado, passo=10, passos_totais=288, orcamento=67, gasto=0, minimo_obrigatorio=0,
                 maximo_permitido=6)


def test_dono_trata_lesao_antes_da_janela_e_aleatorio_usa_todos_os_botoes(vida):
    v = vida[0]
    e = v.motor.estado()
    e["educacao"] = {"disciplina": 0, "lesionado": True, "janela": {"tipo": "aviso", "pedido": "banheiro",
                                                                  "inicio": 0, "prazo": 15}}
    d = DonoComEducacao("atencioso", 3)
    assert d._resposta(_visao(e), random.Random(1)) == (AcaoUsuario.TRATAR_LESAO, "lesao")
    a = DonoComEducacao("aleatorio", 3)
    rng = random.Random(3)
    vistas = set()
    for _ in range(300):
        vistas.update(a._todos_os_botoes([AcaoUsuario.ALIMENTAR] * 3, rng))
    assert set(ACOES_EDUCACAO) <= vistas and AcaoUsuario.ALIMENTAR in vistas
