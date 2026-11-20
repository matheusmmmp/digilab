"""A proveniencia das figuras e tabelas do artigo A1 (etapa A1-4): cada numero da tabela 1 e igual ao do artefato.

Roda sem o matplotlib e sem o git (so a leitura dos artefatos): confere
- o sha256 de cada arquivo citado na proveniencia;
- que cada entrada (arquivo, campo) devolve o valor registrado, lendo o artefato de novo, por conta propria;
- que cada numero da tabela 1 (o CSV gravado no repositorio) e o valor do artefato arredondado nas casas da tabela;
- que a tabela 1 gerada de novo e o CSV gravado sao a mesma;
- que nenhum numero do plano ficou sem conferencia (ou que o que nao bateu esta declarado em `lacunas`).
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import figuras_artigo_a1 as F  # noqa: E402

SAIDA = RAIZ / F.SAIDA_PADRAO


def _doc():
    return json.loads((SAIDA / F.PROVENIENCIA).read_text(encoding="utf-8"))


def test_cada_entrada_da_proveniencia_e_o_artefato(tmp_path):
    doc = _doc()
    com_arquivo = [e for e in doc["entradas"] if "arquivo" in e]
    assert len(com_arquivo) > 100
    for e in com_arquivo:
        caminho = RAIZ / e["arquivo"]
        assert F.sha256_arquivo(caminho) == e["sha256"], e["id"]
        assert F.seguir(F.ler_json(caminho), e["campo"]) == e["valor"], e["id"]


def test_os_derivados_apontam_para_entradas_que_existem():
    doc = _doc()
    ids = {e["id"] for e in doc["entradas"]}
    for e in doc["entradas"]:
        for d in e.get("derivado_de", []):
            assert d in ids, (e["id"], d)


def test_cada_numero_da_tabela1_e_igual_ao_do_artefato():
    doc = _doc()
    por_id = {e["id"]: e for e in doc["entradas"]}
    casas = {t["teste"]: t["casas"] for t in doc["tabela1_ids"]}
    liga = {t["teste"]: t["ids"] for t in doc["tabela1_ids"]}
    linhas = list(csv.DictReader(open(SAIDA / "tabela1_serie_T0_T6.csv", encoding="utf-8")))
    assert [l["test"] for l in linhas] == list(liga)
    for l in linhas:
        c = casas[l["test"]]
        for coluna, ident in zip(("effect", "ci95_low", "ci95_high"), liga[l["test"]]):
            e = por_id[ident]
            assert "arquivo" in e, ident  # a tabela 1 so usa valor lido de artefato, nunca derivado
            valor = F.seguir(F.ler_json(RAIZ / e["arquivo"]), e["campo"])
            assert float(l[coluna]) == round(valor, c), (l["test"], coluna)


def test_a_tabela1_gerada_de_novo_e_a_gravada():
    p = F.Prov(RAIZ)
    linhas = F.tabela1(p)
    gravada = list(csv.DictReader(open(SAIDA / "tabela1_serie_T0_T6.csv", encoding="utf-8")))
    for l, g in zip(linhas, gravada):
        c = l["casas"]
        assert g["test"] == l["id"]
        assert g["effect"] == f"{l['effect']:.{c}f}"
        assert g["ci95_low"] == f"{l['ci_low']:.{c}f}"
        assert g["ci95_high"] == f"{l['ci_high']:.{c}f}"
    assert len(linhas) == len(gravada)


def test_o_que_nao_bateu_com_os_resultados_esta_declarado():
    doc = _doc()
    nao_bateu = [i for i, c in doc["conferencia_com_os_resultados"].items() if c["resultado"] == "nao_bateu"]
    declarados = [l for l in doc["lacunas"] if "nao bateu" in l]
    assert len(declarados) == len(nao_bateu)
