"""AN2 (docs/TAREFA_V3_ACOES_NOVAS.md, secao 11): a subchave `passeio` entra na `ConfigDigibrain` desligada, e as oito vidas do gabarito do
modular (web/app/test/gabaritos/digibrain_modular_*) nao mudam um byte. O unico arquivo regravado e o `digibrain_modular_constantes.json`, com a
diferenca exata de `"passeio": false` (decisao do Matheus, 2026-11-04). Os sha256 abaixo sao os das vidas de antes da subchave."""
from __future__ import annotations

import hashlib
import gzip
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import exportar_gabarito_digibrain_modular as E  # noqa: E402

from digilab.config import ConfigDigibrain  # noqa: E402

# o sha256 do texto das vidas, gravado na `main` antes da AN2 (digibrain_modular_constantes.json, "arquivos")
SHA_VIDAS_ANTES = {
    "digibrain_modular_comedouro.json": "e09d42be0b3e2edc917b28793021790ea180ac38b28584bac42a851c842acac8",
    "digibrain_modular_longe_fixo.json": "e53fbea4e06ee89fc3fb1fdf8bf7bc96d0a804ab7379d255a7a522e47d229783",
}


def test_as_oito_vidas_gravadas_sao_as_de_antes_da_subchave_byte_a_byte():
    for nome, sha in SHA_VIDAS_ANTES.items():
        bruto = gzip.decompress((E.PASTA / (nome + ".gz")).read_bytes())
        assert hashlib.sha256(bruto).hexdigest() == sha, nome
    c = json.loads(E.ARQUIVO_CONSTANTES.read_text(encoding="utf-8"))
    assert {n: i["sha256"] for n, i in c["arquivos"].items()} == SHA_VIDAS_ANTES
    assert len(c["vidas"]) == 8


def test_uma_execucao_nova_das_oito_vidas_sai_igual_ao_gravado_com_a_subchave_no_padrao():
    novo = E.arquivos()
    for nome, sha in SHA_VIDAS_ANTES.items():
        assert hashlib.sha256(E.texto_original(nome + ".gz", novo[nome + ".gz"])).hexdigest() == sha, nome
        # o texto, nao os bytes do gzip: o zlib do CI comprime diferente (o padrao do test_gabarito_digibrain_modular_web.py)
        assert gzip.decompress(novo[nome + ".gz"]) == gzip.decompress((E.PASTA / (nome + ".gz")).read_bytes()), nome


def test_a_subchave_passeio_e_so_o_acrescimo_nas_constantes_e_vem_desligada():
    c = json.loads(E.ARQUIVO_CONSTANTES.read_text(encoding="utf-8"))
    assert c["config_digibrain"]["passeio"] is False and "passeio" in c["desligadas"] and "passeio" not in c["ligadas"]
    assert ConfigDigibrain().passeio is False
