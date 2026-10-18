"""A calibracao do carater do v11 (PW-4 opcao (b); experiments/calibrar_carater_v11.py): o artefato esta em dia e o leilao faz o que diz."""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "experiments"))

import calibrar_carater_v11 as cc  # noqa: E402


def test_artefato_em_dia():
    gravado = json.loads(cc.ARQUIVO.read_text(encoding="utf-8"))
    assert json.loads(json.dumps(cc.calibrar())) == gravado


def test_leilao_deixa_as_linhas_perto_de_um_quarto():
    pets = [p for p in json.loads(cc.MEDIDA.read_text(encoding="utf-8"))["pets"] if p["versao"] == "v11"]
    d, _ = cc.leilao_adolescente(pets, 0.015)
    linhas = [cc.dominante(cc.sem_corte(p["bruto_adolescente"], 0.015, d)) for p in pets]
    assert all(4 <= linhas.count(l) <= 6 for l in cc.LINHAS)


def test_dominante_desempata_pela_ordem_fixa():
    assert cc.dominante({e: 0.0 for e in cc.EIXOS}) == cc.LINHAS[0]
