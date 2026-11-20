"""O alcance da memoria de lugar na ilha grande (docs/TAREFA_V3_ILHA_AGUA.md, secao 12.16, IG6; a IG-6 do Matheus: 128 celulas).

- O numero: `D_MAX_ILHA_GRANDE` e o dobro do `d_max` de sempre, a proporcao do mapa de 128 x 60; o padrao dos inatos nao muda.
- A troca do parametro (`Memoria.alcance`): so o `d_max` muda; os episodios ficam como estao; valor invalido falha alto.
- A troca no meio da vida (`DigiBrain.alcance_da_memoria`): duas vidas do gabarito nascem com o alcance de hoje e trocam numa decisao.
- O gabarito do G-PAR do TS (web/app/test/gabaritos/digibrain_modular_alcance.json.gz) esta em dia byte a byte, e as vidas dele diferem
  das mesmas vidas com o alcance de hoje.
Sementes: so as dos testes.
"""
from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import exportar_gabarito_digibrain_modular as G  # noqa: E402

from digilab.config import CONFIG_DIGIBRAIN_INATOS, CONFIG_MUNDO_GRANDE, CONFIG_MUNDO_MVP_AGUA, D_MAX_ILHA_GRANDE  # noqa: E402
from digilab.digibrain.mem import Memoria  # noqa: E402


def test_o_alcance_da_ilha_grande_e_o_do_mapa_novo_e_o_padrao_nao_muda():
    assert CONFIG_DIGIBRAIN_INATOS.d_max == 1024 == CONFIG_MUNDO_MVP_AGUA.celulas_x * CONFIG_MUNDO_MVP_AGUA.sub
    assert D_MAX_ILHA_GRANDE == 2048 == CONFIG_MUNDO_GRANDE.celulas_x * CONFIG_MUNDO_GRANDE.sub == 2 * CONFIG_DIGIBRAIN_INATOS.d_max


def test_a_troca_do_alcance_so_muda_o_parametro():
    mem = Memoria.__new__(Memoria)
    mem.p, mem.episodios = CONFIG_DIGIBRAIN_INATOS, [{"id": 0, "ponto": (300, 240), "lugar": (18, 15), "regiao": 1, "r": 5}]
    antes = [dict(e) for e in mem.episodios]
    mem.alcance(D_MAX_ILHA_GRANDE)
    assert mem.p.d_max == D_MAX_ILHA_GRANDE and mem.episodios == antes
    assert mem.p == type(mem.p)(**{**{f: getattr(CONFIG_DIGIBRAIN_INATOS, f) for f in CONFIG_DIGIBRAIN_INATOS.__dataclass_fields__}, "d_max": D_MAX_ILHA_GRANDE})
    assert CONFIG_DIGIBRAIN_INATOS.d_max == 1024                      # o padrao e imutavel: a troca fez uma copia
    for ruim in (0, -5, 2048.0, "2048", None, True):
        with pytest.raises(ValueError, match="alcance"):
            mem.alcance(ruim)
    assert mem.p.d_max == D_MAX_ILHA_GRANDE


def test_o_gabarito_do_ts_esta_em_dia_e_as_vidas_diferem_das_de_hoje():
    dados = G.alcance()
    # o conteudo, nao os bytes do .gz: outro zlib (o Python 3.12 do CI) comprime o mesmo texto em bytes diferentes
    assert gzip.decompress(dados) == gzip.decompress((G.PASTA / G.ARQUIVO_ALCANCE).read_bytes())
    g = json.loads(gzip.decompress(dados))
    n = len(G.VIDAS_ALCANCE)
    assert [(v["dono"], v["lugar"], v["semente"]) for v in g["vidas"][:n]] == [v[:3] for v in G.VIDAS_ALCANCE]
    for v in g["vidas"][:n]:
        assert v["inatos"] == {"d_max": D_MAX_ILHA_GRANDE} and len(v["decisoes"]) == 384 and v["difere_de_hoje"] is True
    # a troca no meio da vida (o `DigiBrain.alcance_da_memoria`, o evento "ma" do jogo): nasce com o alcance de hoje e troca numa decisao
    meio = g["vidas"][n:]
    assert [(v["dono"], v["lugar"], v["semente"], v["troca_na_decisao"]) for v in meio] == [tuple(v) for v in G.VIDAS_ALCANCE_NO_MEIO]
    assert all(v["inatos"] == {} and len(v["decisoes"]) == 384 for v in meio)
    assert any(v["troca_na_decisao"] > 1 and v["difere_de_hoje"] and v["difere_do_ovo"] for v in meio)
