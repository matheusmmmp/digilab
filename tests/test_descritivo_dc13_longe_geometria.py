"""O script da decomposicao da D-C1-3 na LONGE_GEOMETRIA (experiments/descritivo_dc13_longe_geometria.py; o plano, secao 8, item 3;
D-LG-3): as travas. O replay das vidas precisa da worktree do 58a22928 e roda fora dos testes (uma vez); aqui so as conferencias que
falham alto antes dele: as fontes da run, o medidas.json comprimido e o codigo de outra pasta."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "experiments"))

import descritivo_dc13_longe_geometria as dc  # noqa: E402


def test_o_script_nao_importa_o_pacote_no_topo():
    """o pacote vem so da worktree de --codigo: o modulo nao o importa por conta propria"""
    assert "digilab" not in vars(dc) and "orq" not in vars(dc)


def test_as_fontes_da_run_sao_as_do_meta():
    fontes = dc.ler_fontes()
    meta = json.loads((dc.RUN / "meta.json").read_text(encoding="utf-8"))
    assert set(fontes) == {"meta.json", "resultado.json", "medidas.json.gz", "vidas.tar.gz"}
    assert meta["git_head"] == dc.COMMIT_DA_RUN and meta["artefatos_sha256"]["medidas.json"] == dc.SHA_MEDIDAS


def test_o_codigo_de_outra_pasta_falha_alto(tmp_path):
    meta = json.loads((dc.RUN / "meta.json").read_text(encoding="utf-8"))
    with pytest.raises(RuntimeError, match="nao e o da run"):
        dc.conferir_codigo(tmp_path, meta)


def test_o_desenho_e_o_do_plano():
    assert dc.LUGARES == ("longe_fixo", "longe_ancora")
    assert dc.CONTRASTES == (("M3", "M2"), ("PAD", "M2"))
    assert dc.MAX_PROCESSOS == 4 and dc.COM_IDAS == ("PAD", "M3")


def test_a_saida_ja_existente_falha_alto(tmp_path):
    saida = tmp_path / "descritivo.json"
    saida.write_text("{}", encoding="utf-8")
    with pytest.raises(FileExistsError):
        dc.principal(tmp_path, {}, {}, tmp_path / "x.tar.gz", saida, 1, {}, None)
