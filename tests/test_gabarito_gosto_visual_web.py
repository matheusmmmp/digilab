"""GOSTO_VISUAL, P1f: o gabarito do gosto visual para a web (web/app/test/gabaritos/gosto_visual.json.gz,
experiments/exportar_gosto_visual.py) e o que o Python de hoje produz, igual em duas execucoes; a config da vida e a do laboratorio com a
subchave `olhar`; e o conserto da D-GV-P1f-1 (o episodio completo de olhar, classe `tela`, so com a subchave). O TS confere o mesmo arquivo
em web/app/test/gosto_visual_paridade.test.ts. Sementes: as dos testes."""
from __future__ import annotations

import gzip
import json
import sys
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import exportar_gabarito_digibrain_modular as E  # noqa: E402
import exportar_gosto_visual as X  # noqa: E402

from digilab.config import CONFIG_MUNDO_MVP  # noqa: E402
from digilab.digibrain.mem import CLASSES_AUTOBIO, Memoria  # noqa: E402


@pytest.fixture(scope="module")
def texto() -> bytes:
    return X.texto()


def test_uma_execucao_nova_sai_igual_ao_gravado(texto):
    # o texto, nao os bytes do gzip (o padrao do test_gabarito_digibrain_modular_web.py)
    assert texto == gzip.decompress(X.ARQUIVO.read_bytes())


def test_duas_execucoes_saem_iguais(texto):
    assert X.texto() == texto


def test_a_config_e_o_laboratorio_com_o_olhar_e_as_vidas(texto):
    g = json.loads(texto)
    assert X.config_vida() == replace(E.config_laboratorio(), olhar=True)
    assert g["config_digibrain"]["olhar"] is True
    hoje = json.loads(E.ARQUIVO_CONSTANTES.read_text(encoding="utf-8"))["config_digibrain"]
    assert "olhar" not in hoje                                     # as constantes do modular nao foram regravadas
    assert {k: v for k, v in g["config_digibrain"].items() if k != "olhar"} == hoje
    assert len(g["vidas"]) == 6 and all(len(v["decisoes"]) == 288 for v in g["vidas"])
    assert all(v["olhares"] > 0 and v["assistir"] == v["olhares"] for v in g["vidas"])
    assert all(v["agrados"] == (v["olhares"] if v["fonte"] == "evento" else 0) for v in g["vidas"])


def test_a_vida_com_o_olhar_guarda_episodios_da_tela():
    """o laboratorio tem a memoria_autobio: a opcao de olhar vira episodio completo de classe `tela` (D-GV-P1f-1)"""
    _, cerebro, _, _ = X.viver("evento", 202, gravar=False)
    m = cerebro.m.mem
    a = m.estado_interno()["autobio"]
    classes = {e["classe"] for e in a["recente"] + a["duradoura"] + a["central"]}
    assert "tela" in classes


def test_o_episodio_de_olhar_so_com_a_subchave():
    """D-GV-P1f-1: a classe `tela` do episodio completo so e aceita pelo M-MEM com a subchave `olhar`; a lista de hoje nao muda"""
    assert "tela" not in CLASSES_AUTOBIO
    assert Memoria(CONFIG_MUNDO_MVP, autobio=True).classes_autobio == CLASSES_AUTOBIO
    assert Memoria(CONFIG_MUNDO_MVP, autobio=True, olhar=True).classes_autobio == CLASSES_AUTOBIO + ("tela",)


# ================================================================== o enjoo da imagem (D-GV-ENJOO-CER), num arquivo novo
@pytest.fixture(scope="module")
def texto_enjoo() -> bytes:
    return X.texto_enjoo()


def test_o_gabarito_do_enjoo_sai_igual_de_uma_execucao_nova(texto_enjoo):
    """web/app/test/gabaritos/gosto_visual_enjoo.json.gz, conferido pelo TS em web/app/test/gosto_visual_enjoo_paridade.test.ts"""
    assert texto_enjoo == gzip.decompress(X.ARQUIVO_ENJOO.read_bytes())


def test_o_gabarito_do_enjoo_sai_igual_em_duas_execucoes(texto_enjoo):
    assert X.texto_enjoo() == texto_enjoo


def test_o_gabarito_do_enjoo_tem_a_chave_ligada_e_as_vidas(texto_enjoo):
    from dataclasses import asdict
    from digilab.config import CONFIG_ENJOO_TELA_LIGADA
    g = json.loads(texto_enjoo)
    assert g["config_enjoo_tela"] == asdict(CONFIG_ENJOO_TELA_LIGADA) and g["config_enjoo_tela"]["ligada"] is True
    assert len(g["vidas"]) == 9 and all(len(v["decisoes"]) == 288 and v["olhares"] > 0 for v in g["vidas"])
    assert sum(1 for v in g["vidas"] if "imagem" in v) == 3
    # a chave ligada: o corpo guarda a memoria, e o motivo do olhar le o enjoo
    assert all("memoria" in v["corpo"]["tela"] for v in g["vidas"])
    assert all("enjoo" in d["motivo"]["olhar"] for v in g["vidas"] for d in v["decisoes"])
