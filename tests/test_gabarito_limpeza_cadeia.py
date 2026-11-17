"""A guarda da LIMPEZA, LZ2b (docs/TAREFA_V3_LIMPEZA.md, 3.3): o gabarito tests/gabaritos/limpeza_cadeia_de_hoje.json, gravado com o codigo
da LZ2a antes da LZ2b num commit proprio, esta em dia com o Python byte a byte. As vidas pelo `MotorPersonalidade` (o vinculo, o desejo,
a recusa) e pelo `MotorTreino` (o treino do combate), com o instinto, saem as de antes. Sementes: so as dos testes."""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import bancada_v2 as bv  # noqa: E402
import gabarito_limpeza_cadeia as G  # noqa: E402

TEXTO = G.ARQUIVO.read_text(encoding="utf-8")


def test_o_gabarito_da_cadeia_esta_em_dia_byte_a_byte():
    assert TEXTO == json.dumps(G.gerar(), sort_keys=True, indent=1) + "\n"


def test_o_gabarito_cobre_a_cadeia_so_com_as_sementes_dos_testes():
    gravado = json.loads(TEXTO)
    n = len(G.OBEDIENCIAS) * len(G.TEMPERAMENTOS) * len(G.DONOS) * len(G.SEMENTES) + len(G.BRACOS_TREINO) * len(G.SEMENTES)
    assert len(gravado) == n == 26
    assert {int(k.rsplit("|", 1)[1]) for k in gravado} <= set(bv.SEMENTES_TESTE)


def test_a_cadeia_roda_de_verdade():
    gravado = json.loads(TEXTO)
    assert not any("erro" in v for v in gravado.values())
    # a obediencia ligada muda a vida; o motor do treino e o MotorTreino, e o dono treinou
    for t in G.TEMPERAMENTOS:
        for d in G.DONOS:
            for s in G.SEMENTES:
                assert gravado[f"personalidade|ligada|{t}|{d}|{s}"]["log"] != gravado[f"personalidade|desligada|{t}|{d}|{s}"]["log"] \
                    or gravado[f"personalidade|ligada|{t}|{d}|{s}"]["recusas"] != gravado[f"personalidade|desligada|{t}|{d}|{s}"]["recusas"]
    assert all(v["motor"] == "MotorTreino" and v["dono"]["treino"] > 0 for k, v in gravado.items() if k.startswith("treino|"))
