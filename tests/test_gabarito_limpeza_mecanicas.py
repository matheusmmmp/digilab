"""A guarda da LIMPEZA, parte 2 (docs/TAREFA_V3_LIMPEZA.md, 3.1): o gabarito tests/gabaritos/limpeza_mecanicas_de_hoje.json, gravado com o
codigo da main antes da LZ2 num commit proprio, esta em dia com o Python byte a byte. As mecanicas do jogo que so tinham gabarito com o A
(a arvore que sacode, o banheiro, o metabolismo, o corpo da etapa 6, a fruta ao lado, o lance do dono) saem as de antes da limpeza com o
modular do jogo e com o instinto do mundo, inclusive as recusas de hoje. Sementes: so as dos testes."""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import bancada_v2 as bv  # noqa: E402
import gabarito_limpeza_mecanicas as G  # noqa: E402

TEXTO = G.ARQUIVO.read_text(encoding="utf-8")


def test_o_gabarito_das_mecanicas_esta_em_dia_byte_a_byte():
    assert TEXTO == json.dumps(G.gerar(), sort_keys=True, indent=1) + "\n"


def test_o_gabarito_cobre_as_mecanicas_e_os_cerebros_que_ficam_so_com_as_sementes_dos_testes():
    gravado = json.loads(TEXTO)
    assert len(gravado) == len(G.MECANICAS) * len(G.CEREBROS) * len(G.DONOS) * len(G.SEMENTES) + 2 * len(G.SEMENTES) == 60
    assert {int(k.rsplit("|", 1)[1]) for k in gravado} <= set(bv.SEMENTES_TESTE)
    assert set(G.CEREBROS) == {"REL", "instinto"}


def test_as_mecanicas_rodam_de_verdade():
    gravado = json.loads(TEXTO)
    # o dono sacudiu a arvore (o roteiro); o modular recusa o banheiro (os receptores fora do prototipo), e so ele
    assert all(v["sacudidas"] == 18 for k, v in gravado.items() if k.startswith("roteiro_sacudir|"))
    erros = {k for k, v in gravado.items() if "erro" in v}
    assert erros == {f"banheiro|REL|{d}|{s}" for d in G.DONOS for s in G.SEMENTES}
    # cada chave muda o motor da vida; o instinto nao tem o lance (so o motor o recebe), e com o atencioso a vida com o lance e a de base
    for c in G.CEREBROS:
        for dono in G.DONOS:
            mecs = [m for m in G.MECANICAS if "erro" not in gravado[f"{m}|{c}|{dono}|101"]
                    and not (c == "instinto" and dono == "atencioso" and m == "lance")]
            assert len({gravado[f"{m}|{c}|{dono}|101"]["estado_motor"] for m in mecs}) == len(mecs)
    assert gravado["lance|instinto|atencioso|101"] == gravado["base|instinto|atencioso|101"]
