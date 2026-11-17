"""Testes da baseline trivial (experiments/bancada/baseline_trivial.py; docs/PLANO_ANALISE_V3_BASELINE_TRIVIAL.md, seção 3): unitários,
sem vida."""
from __future__ import annotations

import random
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
from bancada.baseline_trivial import BaselineTrivial, LimiaresTriviais  # noqa: E402
from digilab.events import AcaoPet  # noqa: E402
from digilab.policy import Politica  # noqa: E402

S = 1024


@dataclass(frozen=True)
class _Corpo:
    tedio: int | None


@dataclass(frozen=True)
class _Obs:
    vetor_estado: tuple
    corpo: _Corpo | None


def _obs(fome: float, energia: float, tedio: int | None) -> _Obs:
    return _Obs((fome, 0.9, energia, 0.5, 0.9, 0.0, 0.0, 0.5), _Corpo(tedio))


B = BaselineTrivial(LimiaresTriviais(fome=0.5, energia=0.3, tedio=0.7), S)


def test_cumpre_o_protocol():
    assert isinstance(B, Politica)


@pytest.mark.parametrize("fome, energia, tedio, acao", [
    (0.49, 0.9, 0, AcaoPet.COMER),            # a fome vem primeiro, mesmo com energia e tedio tambem fora
    (0.10, 0.10, 1024, AcaoPet.COMER),
    (0.50, 0.29, 1024, AcaoPet.DORMIR),        # no limiar exato a regra nao dispara (o "<" estrito)
    (0.90, 0.30, 1024, AcaoPet.BRINCAR),
    (0.90, 0.90, 717, AcaoPet.BRINCAR),        # 717 > 0,7 x 1024 = 716,8
    (0.90, 0.90, 716, AcaoPet.EXPLORAR),
    (0.90, 0.90, 0, AcaoPet.EXPLORAR),
])
def test_as_quatro_regras_na_ordem(fome, energia, tedio, acao):
    assert B.agir(_obs(fome, energia, tedio), random.Random(0)) is acao


def test_nao_le_a_rng_nem_guarda_estado():
    rng = random.Random(7)
    antes = rng.getstate()
    for o in (_obs(0.1, 0.9, 0), _obs(0.9, 0.1, 0), _obs(0.9, 0.9, 1000), _obs(0.9, 0.9, 0)):
        B.agir(o, rng)
    assert rng.getstate() == antes
    assert B.estado_interno() == {"limiares": {"fome": 0.5, "energia": 0.3, "tedio": 0.7}}


def test_sem_o_tedio_falha_alto():
    with pytest.raises(RuntimeError, match="tedio"):
        B.agir(_obs(0.9, 0.9, None), random.Random(0))
    with pytest.raises(RuntimeError, match="tedio"):
        B.agir(_Obs((0.9,) * 8, None), random.Random(0))


@pytest.mark.parametrize("kw", [{"fome": 1.5, "energia": 0.3, "tedio": 0.7}, {"fome": 0.5, "energia": -0.1, "tedio": 0.7},
                                {"fome": 0.5, "energia": 0.3, "tedio": 1}])
def test_limiar_fora_falha_alto(kw):
    with pytest.raises(ValueError):
        LimiaresTriviais(**kw)


def test_s_invalido_falha_alto():
    with pytest.raises(ValueError):
        BaselineTrivial(LimiaresTriviais(0.5, 0.3, 0.7), 0)
