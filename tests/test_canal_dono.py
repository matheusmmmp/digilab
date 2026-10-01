"""Etapa B do canal do dono (docs/PLANO_ANALISE_CANAL_DONO.md, adendo B): peso do carater nos stats so no pet do
painel; com o padrao 1,0 nada muda."""
from __future__ import annotations

import json
import sys
from dataclasses import replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

from digilab.combate_v2.v21.catalogo import Forma, stats  # noqa: E402
from digilab.config import CONFIG_CATALOGO  # noqa: E402
from run_natureza_criacao import catalogo_do_painel  # noqa: E402

CFG = RAIZ / "experiments" / "configs" / "linhagem"
FORMA = Forma("brasa", "adulto", "arisco", "guardiao", "muralha")
CAR = {"atento": 0.3, "impetuoso": -0.4, "paciente": 0.6, "resistente": -0.5}


def test_peso_padrao_e_um_e_nao_muda_os_stats():
    assert CONFIG_CATALOGO.peso_carater_stats == 1.0
    assert stats(FORMA, None, CAR, replace(CONFIG_CATALOGO, peso_carater_stats=1.0)) == stats(FORMA, None, CAR)


def test_peso_maior_afasta_os_stats_do_carater_neutro():
    neutro = stats(FORMA, None, None)

    def dist(k):
        s = stats(FORMA, None, CAR, replace(CONFIG_CATALOGO, peso_carater_stats=k))
        return sum(abs(s[x] - neutro[x]) for x in s)
    assert dist(1.0) < dist(3.0) < dist(9.0)
    assert sum(stats(FORMA, None, CAR, replace(CONFIG_CATALOGO, peso_carater_stats=9.0)).values()) == \
        sum(neutro.values())                       # o orcamento renormalizado nao muda


def test_catalogo_do_painel():
    e1 = json.loads((CFG / "natureza_criacao.json").read_text(encoding="utf-8"))
    assert catalogo_do_painel(e1) is None
    for k in (3, 8):
        c = json.loads((CFG / f"natureza_criacao_canal_k{k}.json").read_text(encoding="utf-8"))
        assert catalogo_do_painel(c).peso_carater_stats == float(k)
        assert {x: c[x] for x in ("rodadas", "rotulo_partidas", "M_B_por_bot", "bootstrap", "combate", "donos", "dias")} == \
            {x: e1[x] if x != "rodadas" else {r: e1["rodadas"][r] for r in ("piloto", "especie_fixa")}
             for x in ("rodadas", "rotulo_partidas", "M_B_por_bot", "bootstrap", "combate", "donos", "dias")}
