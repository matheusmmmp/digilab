"""O diagnostico da calibracao da DC5 (experiments/diagnostico_calibracao_dc5.py)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
import diagnostico_calibracao_dc5 as dg  # noqa: E402


def test_frases_e_limite():
    assert dg.frases("Hmm... tô com fome. Me dá comida?") == 2
    assert dg.acima_do_limite("Um. Dois. Três. Quatro.", "adulto") and not dg.acima_do_limite("Um. Dois. Três.", "adulto")
    assert dg.acima_do_limite("fome fome fome", "bebe") and not dg.acima_do_limite("nhã!", "bebe")


def test_funcionais_pedido_e_trecho():
    assert dg.so_funcionais(("to", "meio", "pouco")) and not dg.so_funcionais(("to", "meio", "agitado"))
    assert dg.tem_pedido("Me dá um banho?", "higiene") and not dg.tem_pedido("Quero brincar!", "higiene")
    assert dg.maior_trecho("eu lembro da bola azul hoje", ["ontem eu lembro da bola azul"]) == 5


def _r(i, fala):
    return {"id": f"X/S0-f{i}", "item": f"S0-f{i}", "entrada": f"S0-f{i}", "fala": fala}


def test_classes():
    c = {"versao": "dec-v2", "k": 1, "intencao": "agitacao", "conceitos": [{"nome": "agitacao", "valor": 500, "confianca": 500}]}
    d = {"versao": "dec-v2", "k": 1, "intencao": "sono", "conceitos": [{"nome": "sono", "valor": 500, "confianca": 500}]}
    ent = {"S0-f0": {"conceitos": c, "estagio": "adulto"}, "S0-f1": {"conceitos": c, "estagio": "adulto"},
           "S0-f2": {"conceitos": d, "estagio": "adulto"}, "S0-f3": {"conceitos": d, "estagio": "adulto"}}
    seq = [_r(0, "tô meio agitado hoje"), _r(1, "tô meio agitado sim"), _r(2, "hoje tô meio agitado"), _r(3, "um pouco de sono")]
    cls = {x["id"]: x["classe"] for x in dg.classificar_repeticao(seq, ent)}
    assert cls == {"X/S0-f1": "a", "X/S0-f2": "b"}
