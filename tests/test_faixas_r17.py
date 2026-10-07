"""V2, W-FAIXAS-R17 (docs/V2_RODADA_17.md): as faixas e os prefixos das unidades do mundo físico (docs/PLANO_ANALISE_V2_MUNDO_FISICO.md,
seção 11) e do corpo com drives (docs/PLANO_ANALISE_V2_CORPO_DRIVES.md, seção 10).

O que se confere: as quatro faixas novas estão em FAIXAS_RESERVADAS com a fonte e não colidem com as de antes, com as queimadas nem com as
sementes e bases das configs de experiments/configs/; os prefixos "mundo" e "corpo" seguem a regra E3; as unidades derivadas deles não colidem
entre si, entre calibração e validação, nem com as dos outros planos, nem caem numa faixa reservada.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402

# as bases dos dois planos (a mesma regra das outras: b101, b202, b303, b404, b505)
BASES_MUNDO = {"calibracao": (31101, 31202, 31303, 31404, 31505), "validacao": (32101, 32202, 32303, 32404, 32505)}
BASES_CORPO = {"calibracao": (33101, 33202, 33303, 33404, 33505), "validacao": (34101, 34202, 34303, 34404, 34505)}
NOVAS = {(31101, 31505): "mundo fisico", (32101, 32505): "mundo fisico", (33101, 33505): "corpo e drives", (34101, 34505): "corpo e drives"}
# as unidades de cada plano (prefixo, bases) para o teste de colisão entre planos
PLANOS = (("experimento-maior", bv.BASES_EXPERIMENTO_MAIOR), ("n6", bv.BASES_N6), ("n7", bv.BASES_N7),
          ("comparacao-cerebros", bv.BASES_COMPARACAO), ("mundo", BASES_MUNDO), ("corpo", BASES_CORPO))
K = 40


def _numeros_das_configs() -> set[int]:
    """Todo inteiro sob uma chave de semente ou de bases nas configs de experiments/configs/ (as listas inteiras entram)."""
    achados: set[int] = set()

    def andar(o, chave=""):
        marca = "semente" in chave.lower() or "base" in chave.lower()
        if isinstance(o, dict):
            for k, v in o.items():
                andar(v, k)
        elif isinstance(o, list):
            for v in o:
                andar(v, chave)
        elif isinstance(o, int) and not isinstance(o, bool) and marca:
            achados.add(o)

    for p in (RAIZ / "experiments" / "configs").rglob("*.json"):
        andar(json.loads(p.read_text(encoding="utf-8")))
    return achados


def test_faixas_novas_reservadas_com_fonte():
    faixas = {(lo, hi): fonte for lo, hi, fonte in bv.FAIXAS_RESERVADAS}
    for (lo, hi), plano in NOVAS.items():
        assert plano in faixas[(lo, hi)]
        assert ("PLANO_ANALISE_V2_MUNDO_FISICO" if plano == "mundo fisico" else "PLANO_ANALISE_V2_CORPO_DRIVES") in faixas[(lo, hi)]
    for bases in (BASES_MUNDO, BASES_CORPO):
        for fase, bs in bases.items():
            for b in bs:
                fonte = bv.na_faixa_reservada(b)
                assert fonte is not None and ("calibracao" in fonte) == (fase == "calibracao"), (b, fonte)


def test_faixas_disjuntas_e_fora_das_queimadas():
    los = sorted((lo, hi) for lo, hi, _ in bv.FAIXAS_RESERVADAS)
    assert all(a[1] < b[0] for a, b in zip(los, los[1:]))                      # nenhuma faixa colide com outra
    for lo, hi in NOVAS:
        assert not any(q_lo <= hi and lo <= q_hi for q_lo, q_hi, _ in bv.FAIXAS_QUEIMADAS)


def test_faixas_novas_fora_das_configs():
    numeros = _numeros_das_configs()
    assert numeros                                                               # a varredura acha alguma coisa
    for lo, hi in NOVAS:
        assert not [n for n in numeros if lo <= n <= hi], (lo, hi)


def test_prefixos_novos_seguem_a_regra():
    assert {"mundo", "corpo"} <= set(bv.PREFIXOS_UNIDADES)
    for prefixo, bases in (("mundo", BASES_MUNDO), ("corpo", BASES_CORPO)):
        u = bv.unidades_derivadas(bases["calibracao"], 4, prefixo)[6]
        assert (u["base"], u["k"]) == (bases["calibracao"][1], 2)
        assert u["semente"] == derivar_semente(prefixo, u["base"], 2)
        assert u["genoma"] == derivar_semente(f"{prefixo}-genoma", u["base"], 2)
    with pytest.raises(ValueError):
        bv.unidades_derivadas((31101,), 1, "mundo-fisico")


def test_unidades_sem_colisao_entre_planos_e_fases():
    por_plano = {}
    for prefixo, bases in PLANOS:
        for fase in ("calibracao", "validacao"):
            us = bv.unidades_derivadas(bases[fase], K, prefixo)
            por_plano[(prefixo, fase)] = [x["semente"] for x in us] + [x["genoma"] for x in us]
    todos = [v for vs in por_plano.values() for v in vs]
    assert len(set(todos)) == len(todos)                                         # nem entre planos, nem entre fases, nem semente x genoma
    novos = [v for (p, _), vs in por_plano.items() if p in ("mundo", "corpo") for v in vs]
    numeros = _numeros_das_configs()
    for v in novos:
        assert bv.na_faixa_reservada(v) is None, v
        assert v not in numeros and v not in bv.SEMENTES_TESTE, v


def test_config_com_os_prefixos_novos_passa_e_pede_plano():
    cfg = {"bracos": ["P0"], "donos": ["atencioso"], "unidades": {"bases": [101], "k": 1, "prefixo": "mundo"}, "dias": 1,
           "orcamento": 16, "sonda": {"estados": 5, "amostras": 5, "semente": 101}, "bootstrap": {}, "mundos": ["descasado"]}
    bv.validar_config(cfg)
    bv.validar_config({**cfg, "unidades": {"bases": [101], "k": 1, "prefixo": "corpo"}})
    for b in (31101, 34505):                                                     # fora das sementes dos testes, só com plano
        with pytest.raises(bv.SementeSemPlano):
            bv.validar_config({**cfg, "unidades": {"bases": [b], "k": 1, "prefixo": "mundo"}})
