"""O G2 do DigiBrain modular e do candidato `lembranca` (docs/TAREFA_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md, etapa 0;
docs/ESPEC_DIGIBRAIN_MODULAR.md, secao 11): o gabarito tests/gabaritos/digibrain_vidas_de_hoje.json, gravado antes da chave, esta em dia
com o Python byte a byte.

- O arquivo em disco e o que o tests/gabarito_digibrain.py gera hoje (as vidas e os candidatos de cada sub-decisao do mundo).
- As vidas que vem de um gabarito de antes sao as dele: a impressao de cada uma e a que o gabarito da fonte guarda (gravar os candidatos
  nao muda a vida, e o caso e o mesmo).
- O gabarito cobre as fontes de candidato do explorar de hoje, e nenhum candidato `lembranca` existe ainda.
Sementes: so as dos testes.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import bancada_v2 as bv  # noqa: E402
import gabarito_digibrain as G  # noqa: E402

TEXTO = G.ARQUIVO.read_text(encoding="utf-8")
GRAVADO = json.loads(TEXTO)
TIPOS_DE_HOJE = {"arvore", "casa", "cheiro", "cheiro_seguir", "cheiro_virar", "continuar", "onde_comeu", "seguir", "vagar"}


def test_o_gabarito_esta_em_dia_byte_a_byte():
    assert TEXTO == json.dumps(G.gerar(), sort_keys=True, indent=1) + "\n"


def test_as_vidas_das_fontes_sao_as_dos_gabaritos_delas():
    for fonte, (arquivo, parte) in G.FONTES.items():
        origem = json.loads(arquivo.read_text(encoding="utf-8"))
        origem = origem[parte] if parte is not None else origem
        nossas = {k.split("|", 1)[1]: v for k, v in GRAVADO.items() if k.split("|", 1)[0] == fonte}
        assert nossas and set(nossas) <= set(origem), fonte
        for chave, v in nossas.items():
            assert v["impressao"] == G._sha(G._texto(origem[chave])), f"{fonte}|{chave}"


def test_o_gabarito_cobre_os_candidatos_do_explorar_de_hoje():
    fontes = Counter(k.split("|", 1)[0] for k in GRAVADO)
    assert fontes == {"p4_j1": 36, "dois_pets_direta": 48, "pqp_plano": 36, "sentidos_direto": 64, "olfato_vida": 8, "olfato_grupo": 4}
    tipos = Counter()
    for k, v in GRAVADO.items():
        # o P0z (o instinto do mundo "sem_explorar") nao explora: as vidas dele ficam pelos candidatos do comer e do brincar
        assert (v["n"].get("explorar", 0) > 0) == ("|P0z|" not in k), k
        tipos.update(v["tipos_explorar"])
    assert set(tipos) == TIPOS_DE_HOJE and "lembranca" not in tipos
    assert all(n >= 30 for n in tipos.values()), tipos
    # cada fonte traz o que so ela cobre
    por_fonte = {f: Counter() for f in fontes}
    for k, v in GRAVADO.items():
        por_fonte[k.split("|", 1)[0]].update(v["tipos_explorar"])
    assert por_fonte["pqp_plano"]["arvore"] > 0 and por_fonte["sentidos_direto"]["seguir"] > 0
    assert por_fonte["olfato_vida"]["cheiro_seguir"] > 0 and por_fonte["olfato_vida"]["cheiro"] == 0


def test_so_as_sementes_dos_testes():
    sementes = {int(k.rsplit("|", 1)[1]) for k in GRAVADO}
    assert sementes <= set(bv.SEMENTES_TESTE), sementes
