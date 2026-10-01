"""Etapa B do canal do dono (docs/PLANO_ANALISE_CANAL_DONO.md, adendo B): os modificadores do carater nos stats
multiplicados por k, so no pet do painel; sem `catalogo_painel` nada muda."""
from __future__ import annotations

import json
import sys
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
CAMPOS = ("rotulo_partidas", "M_B_por_bot", "bootstrap", "combate", "donos", "dias")


def _cfg(nome):
    return json.loads((CFG / nome).read_text(encoding="utf-8"))


def test_e1_sem_catalogo_do_painel():
    assert catalogo_do_painel(_cfg("natureza_criacao.json")) is None


def test_k_multiplica_so_os_modificadores_do_carater():
    for k in (3, 8):
        c = _cfg(f"natureza_criacao_canal_k{k}.json")
        cat = catalogo_do_painel(c)
        assert cat.carater == {e: {s: m * k for s, m in mods.items()} for e, mods in CONFIG_CATALOGO.carater.items()}
        for campo in ("temperamento", "especies", "arquetipos_crianca", "arquetipos_adolescente", "arquetipos_adulto",
                      "stat_min", "stat_max"):
            assert getattr(cat, campo) == getattr(CONFIG_CATALOGO, campo), campo
        e1 = _cfg("natureza_criacao.json")
        assert {x: c[x] for x in CAMPOS} == {x: e1[x] for x in CAMPOS}
        assert c["rodadas"]["especie_fixa"] == e1["rodadas"]["especie_fixa"]


def test_peso_maior_afasta_os_stats_do_neutro():
    neutro = stats(FORMA, None, None)

    def dist(k):
        s = stats(FORMA, None, CAR, catalogo_do_painel({"catalogo_painel": {"peso_carater_stats": k}}))
        return sum(abs(s[x] - neutro[x]) for x in s)
    assert stats(FORMA, None, CAR, catalogo_do_painel({"catalogo_painel": {"peso_carater_stats": 1.0}})) == stats(FORMA, None, CAR)
    assert dist(1.0) < dist(3.0) < dist(8.0)
