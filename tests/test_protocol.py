"""Etapa 1 - protocolo congelado."""

import dataclasses
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from digilab.protocol import (  # noqa: E402
    ENGINE_SHA256_V0,
    PROTOCOLO_ARENA_V1,
    PROTOCOLO_ARENA_V1_ABLACAO,
    PROTOCOLOS,
    Status,
    bracos_do_protocolo,
    derivar_semente,
    sha256_engine,
)


def test_engine_nao_foi_alterado():
    assert sha256_engine() == ENGINE_SHA256_V0


def test_protocolo_canonico_valida():
    PROTOCOLO_ARENA_V1.validar()


def test_protocolo_e_imutavel():
    with pytest.raises(dataclasses.FrozenInstanceError):
        PROTOCOLO_ARENA_V1.dias_simulados = None  # type: ignore[misc]


def test_todo_campo_tem_status():
    for nome, campo in PROTOCOLO_ARENA_V1.campos().items():
        assert isinstance(campo.status, Status), nome
        assert campo.justificativa, nome


def test_hash_estavel_e_sensivel():
    h = PROTOCOLO_ARENA_V1.hash()
    assert h == PROTOCOLO_ARENA_V1.hash()
    outro = PROTOCOLO_ARENA_V1.com_substituicoes({"dias_simulados": 3})
    assert outro.hash() != h
    assert "dias_simulados" in outro.campos_propostos()


def test_menos_de_cinco_sementes_falha():
    with pytest.raises(ValueError, match="5 sementes"):
        PROTOCOLO_ARENA_V1.com_substituicoes({"sementes_coorte": [1, 2, 3]})


def test_substituicao_de_campo_inexistente_falha():
    with pytest.raises(KeyError):
        PROTOCOLO_ARENA_V1.com_substituicoes({"clima": 1})


def test_orcamento_inalcancavel_falha():
    with pytest.raises(ValueError, match="inalcancavel"):
        PROTOCOLO_ARENA_V1.com_substituicoes({"dias_simulados": 1, "orcamento_interacoes": 10**6})


def test_derivar_semente_deterministica():
    assert derivar_semente(1, "a") == derivar_semente(1, "a")
    assert derivar_semente(1, "a") != derivar_semente(1, "b")


# ------------------------------------------------------------ ablacao

HASH_CANONICO_V1 = "adce99fc3fdc"  # prefixo gravado em artifacts/metrics.json


def test_hash_v1_nao_mudou_com_a_ablacao():
    assert PROTOCOLO_ARENA_V1.hash().startswith(HASH_CANONICO_V1)
    assert "politicas" not in PROTOCOLO_ARENA_V1.campos()


def test_ablacao_herda_tudo_de_v1_menos_politicas():
    PROTOCOLO_ARENA_V1_ABLACAO.validar()
    v1, ab = PROTOCOLO_ARENA_V1.campos(), PROTOCOLO_ARENA_V1_ABLACAO.campos()
    assert set(ab) - set(v1) == {"politicas"}
    for nome in v1:
        assert ab[nome] == v1[nome], nome
    pol = ab["politicas"]
    assert pol.valor == ("bandit", "instinto")
    assert pol.status is Status.PROPOSTO
    assert PROTOCOLO_ARENA_V1_ABLACAO.hash() != PROTOCOLO_ARENA_V1.hash()


def test_ablacao_tem_oito_bracos_dono_x_politica():
    bracos = bracos_do_protocolo(PROTOCOLO_ARENA_V1_ABLACAO)
    assert len(bracos) == 8
    assert len({r for r, _, _ in bracos}) == 8
    assert {(d, p) for _, d, p in bracos} == {
        (d, p) for d in PROTOCOLO_ARENA_V1.v("bracos") for p in ("bandit", "instinto")
    }


def test_v1_continua_com_bracos_so_bandit_e_rotulo_igual_ao_dono():
    assert bracos_do_protocolo(PROTOCOLO_ARENA_V1) == [(d, d, "bandit") for d in PROTOCOLO_ARENA_V1.v("bracos")]


def test_ablacao_sem_instinto_falha():
    with pytest.raises(ValueError, match="instinto"):
        PROTOCOLO_ARENA_V1_ABLACAO.com_substituicoes({"politicas": ["bandit"]})


def test_ablacao_com_politica_desconhecida_falha():
    with pytest.raises(ValueError, match="desconhecida"):
        PROTOCOLO_ARENA_V1_ABLACAO.com_substituicoes({"politicas": ["bandit", "instinto", "q"]})


def test_registro_de_protocolos():
    assert PROTOCOLOS["arena-v1"] is PROTOCOLO_ARENA_V1
    assert PROTOCOLOS["arena-v1-ablacao"] is PROTOCOLO_ARENA_V1_ABLACAO


def test_referendo_cobre_os_propostos_de_hoje_sem_mudar_hashes():
    from digilab.protocol import (PARAMETROS_EDUCACAO_V1, PROTOCOLOS, Campo, educacao_nao_referendados,
                                  propostos_nao_referendados, referendado)
    for p in PROTOCOLOS.values():
        assert propostos_nao_referendados(p) == [], p.versao
        assert p.campos_propostos()                     # o status dentro do protocolo nao mudou (hash intacto)
    assert educacao_nao_referendados() == []
    outro = dict(PARAMETROS_EDUCACAO_V1)
    c = outro["ConfigLesoes.prob_lesao_derrota"]
    outro["ConfigLesoes.prob_lesao_derrota"] = Campo(0.3, c.status, c.justificativa)
    assert educacao_nao_referendados(outro) == ["ConfigLesoes.prob_lesao_derrota"]   # valor novo: nao referendado
    assert not referendado("protocolo.dias_simulados", 15) and referendado("protocolo.dias_simulados", 14)
