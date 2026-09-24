"""Etapa 1 - protocolo congelado."""

import dataclasses
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from digilab.protocol import (  # noqa: E402
    ENGINE_SHA256_V0,
    PROTOCOLO_ARENA_V1,
    Status,
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
