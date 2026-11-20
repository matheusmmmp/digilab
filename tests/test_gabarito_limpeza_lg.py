"""A guarda da LIMPEZA (docs/TAREFA_V3_LIMPEZA.md, a LZ1): o gabarito tests/gabaritos/limpeza_lg_de_hoje.json, gravado com o codigo da main
antes da LZ2 num commit proprio, esta em dia com o Python byte a byte. As vidas do modular pelo caminho da LONGE_GEOMETRIA (o
MotorGravaCorpo, os quatro lugares longe, os quatro bracos e os quatro donos) saem as de antes da limpeza: o log, o estado interno do
cerebro, as medidas e os lugares. Sementes: so as dos testes."""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import bancada_v2 as bv  # noqa: E402
import gabarito_limpeza_lg as G  # noqa: E402

TEXTO = G.ARQUIVO.read_text(encoding="utf-8")


def test_o_gabarito_da_limpeza_esta_em_dia_byte_a_byte():
    assert TEXTO == json.dumps(G.gerar(), sort_keys=True, indent=1) + "\n"


def test_o_gabarito_cobre_os_bracos_os_donos_e_os_lugares_so_com_as_sementes_dos_testes():
    gravado = json.loads(TEXTO)
    assert len(gravado) == len(G.BRACOS) * len(G.SEMENTES) * 4 * len(G.LUGARES) == 128
    assert {k.split("|")[0] for k in gravado} == {"PAD", "M3", "M2", "M0"}
    assert {k.split("|")[2] for k in gravado} == {"longe_um", "longe_fixo", "longe_ancora", "longe"}
    assert {int(k.rsplit("|", 1)[1]) for k in gravado} <= set(bv.SEMENTES_TESTE)
    assert all(v["decisoes"] == G.DIAS * 96 for v in gravado.values())


def test_os_lugares_diferem_entre_si_na_mesma_vida():
    gravado = json.loads(TEXTO)
    for b in G.BRACOS:
        for s in G.SEMENTES:
            for dono in ("atencioso", "relapso", "aleatorio", "incoerente"):
                assert len({gravado[f"{b}|{dono}|{lugar}|{s}"]["lugares"] for lugar in G.LUGARES}) == len(G.LUGARES)
