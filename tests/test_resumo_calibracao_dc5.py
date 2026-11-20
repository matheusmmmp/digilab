"""O resumo descritivo da calibracao da DC5 (experiments/resumo_calibracao_dc5.py)."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
import resumo_calibracao_dc5 as rc  # noqa: E402


def _reg(celula, conjunto, item, fala, erro=None, nao_sup=()):
    return {"celula": celula, "conjunto": conjunto, "item": item, "fala": fala, "erro": erro, "pedido_rede": None, "versao_prompt": "voz-v4",
            "chamada_voz": {"modelo_devolvido": "falso"}, "latencia_voz_s": 1.0,
            "verificacao": {"nao_suportadas": list(nao_sup), "cita_mentira": False, "manipulacao": False, "erro": None}}


FRASES = {"jogo": ["Que fome, quero comer agora."], "v3b": ["Fica comigo um pouco."]}


def test_contagens_e_sequencias():
    regs = [_reg("A", "ES", "S0-f0", "eu quero comer agora mesmo"), _reg("A", "ES", "S0-f1", "eu quero comer agora de novo"),
            _reg("A", "R", "K1-Q0-t0", "oi tudo bem", nao_sup=["x"]), _reg("A", "E3", "E3-000", "x", erro="generica"),
            _reg("B", "E3", "E3-000", "que fome quero comer agora sim")]
    r = rc.resumo(regs, FRASES)
    a, b = r["celulas"]["A"], r["celulas"]["B"]
    assert a["genericas"] == 1 and a["fracao_genericas"] == 0.25 and a["acima_do_limiar_formato"]
    assert a["repeticao"] == {"sequencias": 2, "consideradas": 1, "repetem": 1}
    assert a["verificador"]["com_nao_suportada"] == 1
    assert b["com_frase_modelo_jogo"] == 1 and a["com_frase_modelo_jogo"] == 0
    assert rc.sequencia_de(regs[2]) == "K1-Q0" and rc.sequencia_de(regs[4]) is None


def test_fica_comigo():
    assert rc.fica_comigo("Você podia ficar um pouquinho comigo?")
    assert rc.fica_comigo("Não vai embora!") and rc.fica_comigo("fica comigo")
    assert not rc.fica_comigo("vem brincar comigo")


def test_falha_alto_sem_falas():
    with pytest.raises(ValueError):
        rc.resumo([], FRASES)
