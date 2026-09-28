"""educacao-v1, Fase 2 parte 1: configs, acoes novas e MotorEducacao vazio (docs/DESIGN_EDUCACAO_HERANCA_LESOES.md)."""
from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from digilab.config import CONFIG_EDUCACAO, CONFIG_LESOES  # noqa: E402
from digilab.educacao import AcaoAindaSemEfeito, MotorEducacao, fabricas_educacao  # noqa: E402
from digilab.events import ACOES_EDUCACAO, ACOES_TREINO, ACOES_V1, AcaoUsuario  # noqa: E402
from digilab.evolucao import ovo  # noqa: E402
from digilab.protocol import (PARAMETROS_EDUCACAO_V1, Campo, Status, hash_parametros_educacao,  # noqa: E402
                              validar_parametros_educacao)
from digilab.temperamento import sortear  # noqa: E402
from digilab.treino import reproduzir_com_feedback  # noqa: E402
from digilab.treino_vida import MotorTreino, simular_vida_treino  # noqa: E402


def _vida(braco: str, s: int = 3101, dias: int = 3):
    esp, _ = ovo(s)
    t = sortear(s)
    return simular_vida_treino(braco, s, dias, esp, t), esp, t


def test_acoes_novas_nao_mexem_nas_listas_antigas():
    assert [a.value for a in ACOES_V1] == ["alimentar", "limpar", "brincar", "acariciar", "elogiar", "repreender"]
    assert all(a.value.startswith("treinar_") for a in ACOES_TREINO) and len(ACOES_TREINO) == 6
    assert set(ACOES_EDUCACAO).isdisjoint(ACOES_V1) and set(ACOES_EDUCACAO).isdisjoint(ACOES_TREINO)
    assert list(AcaoUsuario)[-3:] == list(ACOES_EDUCACAO)      # no fim do enum


@pytest.mark.parametrize("braco", ["exigente", "aleatorio", "atencioso"])
def test_log_sem_acao_nova_rejoga_igual_ao_motor_treino(braco):
    v, esp, t = _vida(braco)
    fp, fm = fabricas_educacao(3101, esp, t)
    r = reproduzir_com_feedback(v.motor.log, fp, semente=3101, fabrica_motor=fm)
    assert isinstance(r, MotorEducacao)
    e_r, e_m = r.estado(), v.motor.estado()
    assert e_r.pop("educacao") == {"disciplina": 0, "janela": None}
    assert e_r == e_m
    assert r.resumo_treino() == v.motor.resumo_treino() and r.vinculo.serie == v.motor.vinculo.serie


@pytest.mark.parametrize("acao", ACOES_EDUCACAO)
def test_acao_nova_falha_alto(acao):
    esp, _ = ovo(3101)
    fp, fm = fabricas_educacao(3101, esp, sortear(3101))
    with pytest.raises(AcaoAindaSemEfeito):
        fm(fp(None), None, 3101)._aplicar_acao_usuario(acao)
    antigo = MotorTreino(fp(None), None, 3101, sortear(3101), esp)
    with pytest.raises(Exception):
        antigo._aplicar_acao_usuario(acao)


def test_parametros_registrados_com_status_e_fonte():
    validar_parametros_educacao()
    for nome, c in PARAMETROS_EDUCACAO_V1.items():
        assert c.justificativa, nome
    propostos = {n for n, c in PARAMETROS_EDUCACAO_V1.items() if c.status is Status.PROPOSTO}
    assert "ConfigLesoes.limiar_taxa_vitoria" in propostos and "ConfigEducacao.janela_min" not in propostos
    assert PARAMETROS_EDUCACAO_V1["ConfigEducacao.passo_disciplina"].valor == CONFIG_EDUCACAO.passo_disciplina
    assert PARAMETROS_EDUCACAO_V1["ConfigLesoes.lesoes_para_morte"].valor == CONFIG_LESOES.lesoes_para_morte


def test_registro_divergente_de_config_falha_alto():
    ruim = dict(PARAMETROS_EDUCACAO_V1)
    c = ruim["ConfigEducacao.passo_disciplina"]
    ruim["ConfigEducacao.passo_disciplina"] = Campo(c.valor + 1, c.status, c.justificativa)
    with pytest.raises(ValueError):
        validar_parametros_educacao(ruim)
    del ruim["ConfigEducacao.passo_disciplina"]
    with pytest.raises(ValueError):
        validar_parametros_educacao(ruim)


def test_hash_estavel_e_sensivel():
    h = hash_parametros_educacao()
    assert h == hash_parametros_educacao() and len(h) == 64
    outro = dict(PARAMETROS_EDUCACAO_V1)
    c = outro["ConfigHeranca.sigma_temperamento"]
    outro["ConfigHeranca.sigma_temperamento"] = replace(c, status=Status.DECIDIDO)
    assert hash_parametros_educacao(outro) != h
