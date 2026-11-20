"""A comparacao pareada das calibracoes da DC5 (experiments/comparar_calibracoes_dc5.py)."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
import comparar_calibracoes_dc5 as cc  # noqa: E402


class _Esp:
    citacoes = ({"pt": "Eu sou o mais forte de todos aqui"},)


def _r(celula, item, fala, conjunto="E3", pedido="solidao", estagio="adulto", erro=None, especie=None):
    return {"celula": celula, "item": item, "entrada": item, "semente": 1, "fala_jogador": None, "fala": fala, "conjunto": conjunto,
            "pedido_rede": pedido, "estagio": estagio, "erro": erro, "especie_corpus": especie}


def test_limite_da_v4b():
    assert cc.acima_v4b(_r("x", "i", "Um. Dois. Três."))
    assert not cc.acima_v4b(_r("x", "i", "Hmm... vem brincar comigo? Tô agitado."))
    assert cc.acima_v4b(_r("x", "i", "fome fome fome", estagio="bebe"))


def test_coluna():
    regs = [_r("G-v4b", "E3-0", "Fica um pouquinho comigo?"), _r("G-v4b", "E3-1", "Vem brincar junto!"),
            _r("G-v4b", "E3-2", "x", erro="repete_citacao: ..."),
            _r("G-v4b", "E3-3", "eu sou o mais forte de todos, vem brincar", especie="Agumon")]
    c = cc.coluna(regs, {"Agumon": _Esp()})
    assert c["fica_comigo"] == 1 and c["e3_solidao_fica_comigo"] == 1 and c["genericas_do_filtro"] == 1
    assert c["e3_sem_pedido"] == 0 and c["com_citacoes"] == 1 and c["copiam_citacao"] == 1


def test_falha_alto_sem_pareamento():
    a = [_r(f"{b}-{v}", "E3-0", "oi") for b in "GH" for v in ("jogo", "v4")]
    b = [_r(f"{x}-{v}", "E3-9", "oi") for x in "GH" for v in ("jogo", "v4b")]
    with pytest.raises(RuntimeError):
        cc.comparar({"dc5b": a, "v4b": b}, {})
