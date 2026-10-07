"""Rodada 17, W-GABARITOS: as vidas de hoje do mundo fisico (docs/TAREFA_V2_MUNDO_FISICO.md, secao 10, G2) e do corpo
(docs/TAREFA_V2_CORPO_DRIVES.md, secao 12, G2), conferidas contra o codigo atual.

Os dois gabaritos foram gravados com o codigo da main, antes de qualquer mudanca do mundo ou do corpo, num commit proprio
(`tests/gabarito_mundo.py`, `tests/gabarito_corpo.py`). Enquanto nada mudou, estas vidas saem iguais byte a byte; depois, com a chave do
mundo ou do corpo desligada, tambem tem de sair. So as sementes dos testes (101, 202).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "tests"))

import gabarito_corpo as gc  # noqa: E402
import gabarito_mundo as gm  # noqa: E402

SEMENTES_DOS_TESTES = range(101, 506)


def _diferencas(gravado: dict, atual: dict) -> list[str]:
    faltam = sorted(set(gravado) ^ set(atual))
    if faltam:
        return [f"casos diferentes: {faltam[:5]}"]
    return [f"{k}: {c}" for k in sorted(gravado) for c in gravado[k] if gravado[k][c] != atual[k][c]]


@pytest.mark.parametrize("modulo", [gm, gc], ids=["mundo", "corpo"])
def test_vidas_de_hoje_byte_a_byte(modulo):
    gravado = json.loads(modulo.ARQUIVO.read_text(encoding="utf-8"))
    atual = json.loads(json.dumps(modulo.gerar(), sort_keys=True))
    dif = _diferencas(gravado, atual)
    assert not dif, f"{len(dif)} diferencas; primeiras: {dif[:10]}"


@pytest.mark.parametrize("modulo", [gm, gc], ids=["mundo", "corpo"])
def test_so_sementes_dos_testes(modulo):
    for chave in json.loads(modulo.ARQUIVO.read_text(encoding="utf-8")):
        assert int(chave.rsplit("|", 1)[1]) in SEMENTES_DOS_TESTES, chave


def test_mundo_cobre_bracos_mundos_e_montagens():
    chaves = [k.split("|") for k in json.loads(gm.ARQUIVO.read_text(encoding="utf-8"))]
    assert len(chaves) == 96
    assert {c[0] for c in chaves} == {"simples", "completa"}
    assert {c[1] for c in chaves} == set(gm.MUNDOS) == {"padrao", "bola", "descasado", "iguais_frutas"}
    assert {c[2] for c in chaves} == set(gm.BRACOS) == {"P0", "P1", "P3"}


def test_corpo_cobre_os_tres_motores():
    """secao 2 da tarefa do corpo: os motores que o corpo vai tocar, todos no gabarito, com P0 a P3 e o so cuidado"""
    g = json.loads(gc.ARQUIVO.read_text(encoding="utf-8"))
    assert {v["motor"] for v in g.values()} == set(gc.MOTORES) == {"MotorComFeedback", "MotorAmbiente", "MotorFrutasMundo"}
    chaves = [k.split("|") for k in g]
    assert {c[1] for c in chaves} == {"padrao", "bola", "descasado", "mutavel", "iguais_frutas"}
    assert {c[2] for c in chaves} >= {"P0", "P1", "P2", "P3", "P0<P3:sem_ensino"}
    assert {c[0] for c in chaves} == {"simples", "completa"}
    assert len(g) == 156
