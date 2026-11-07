"""DC3d da CONVERSA_PET: o gabarito da `fala_unidades` para a web (web/app/test/gabaritos/digibrain_fala_unidades.json.gz,
experiments/exportar_gabarito_fala_unidades.py) e o que o Python de hoje produz, e a config da vida e a do laboratorio com a subchave ligada.
O TS confere o mesmo arquivo em web/app/test/digibrain_fala_unidades.test.ts."""
from __future__ import annotations

import gzip
import json
import sys
from dataclasses import replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import exportar_gabarito_digibrain_modular as E  # noqa: E402
import exportar_gabarito_fala_unidades as F  # noqa: E402

from digilab.config import CONFIG_FALA_UNIDADES, CONTEUDOS_FALA  # noqa: E402


def test_uma_execucao_nova_sai_igual_ao_gravado():
    # o texto, nao os bytes do gzip: o zlib do CI comprime diferente (o padrao do test_gabarito_digibrain_modular_web.py)
    assert F.texto() == gzip.decompress(F.ARQUIVO.read_bytes())


def test_a_config_e_o_laboratorio_com_a_fala_unidades_e_as_constantes_da_fala():
    g = json.loads(gzip.decompress(F.ARQUIVO.read_bytes()))
    assert F.config_fala() == replace(E.config_laboratorio(), fala_unidades=True)
    assert g["config_digibrain"]["fala_unidades"] is True
    assert {k: v for k, v in g["config_digibrain"].items() if k != "fala_unidades"} == \
        {k: v for k, v in json.loads(E.ARQUIVO_CONSTANTES.read_text(encoding="utf-8"))["config_digibrain"].items() if k != "fala_unidades"}
    assert g["conteudos_fala"] == list(CONTEUDOS_FALA)
    assert g["config_fala_unidades"] == {"ganho_conteudo": CONFIG_FALA_UNIDADES.ganho_conteudo}
    assert len(g["vidas"]) == 20 and all(len(v["decisoes"]) == 288 for v in g["vidas"])
    assert all(sum(v["falas"].values()) > 0 for v in g["vidas"])
