"""Verificacoes pequenas da POC. Fora da suite principal (o nome nao casa `test_*.py` e o arquivo fica fora de `tests/`).

Rodar explicitamente:  python -m pytest poc/orgaos_genetica/verificar_poc.py -q
Sementes: so 1 a 9, locais desta POC; nenhuma faixa reservada de pesquisa.
"""
from __future__ import annotations

import dataclasses
import os
import subprocess
import sys
from pathlib import Path

import pytest

from .fisiologia import Fisiologia
from .genoma import ESCALA, GENES, NOMES, Genoma, cruzar, padrao, sortear
from .replay import entradas_sinteticas, evento_origem, reproduzir

POC = Path(__file__).resolve().parent.parent   # a pasta poc/


def _com(**troca: int) -> Genoma:
    d = padrao().como_dict()
    d.update(troca)
    return Genoma.de_dict(d)


# --- genes ---------------------------------------------------------------------------------------------------------------

def test_gene_fora_da_faixa_falha_alto():
    with pytest.raises(ValueError):
        _com(taxa_digestao=GENES[0].maximo + 1)
    with pytest.raises(TypeError):
        Genoma(tuple(float(g.padrao) for g in GENES))
    with pytest.raises(ValueError):
        Genoma.de_dict({**padrao().como_dict(), "gene_novo": 1})


def test_genoma_so_tem_genes_inatos():
    # o registro e so a tupla de genes declarados: nao ha campo para memoria, pesos ou estado vivido
    assert [f.name for f in dataclasses.fields(Genoma)] == ["valores"]
    assert set(padrao().como_dict()) == set(NOMES)


# --- orgao digestivo -----------------------------------------------------------------------------------------------------

def test_digestao_transforma_alimento_em_energia_e_tira_fome():
    c = Fisiologia(padrao())
    e0, f0 = c.energia, c.fome
    c.comer(3000)
    for _ in range(10):
        c.tick()
    assert c.estomago == 0
    assert c.energia > e0 and c.fome < f0
    # conservacao: tudo o que entrou esta no estomago, foi digerido ou foi descartado por teto
    assert c.contas["ingerido"] == c.estomago + c.contas["digerido"] + c.contas["descarte_estomago"]


def test_sem_comida_energia_cai_e_fome_sobe():
    c = Fisiologia(padrao())
    e0, f0 = c.energia, c.fome
    for _ in range(50):
        c.tick()
    assert c.energia == e0 - 50 * padrao()["gasto_basal"]
    assert c.fome == f0 + 50 * padrao()["ganho_fome"]
    assert c.saciedade == 0


def test_estomago_cheio_descarta_e_conta():
    c = Fisiologia(padrao())
    c.comer(ESCALA + 700)
    assert c.estomago == ESCALA and c.contas["descarte_estomago"] == 700


def test_taxa_digestao_e_gene_muda_o_fenotipo():
    lento, rapido = Fisiologia(_com(taxa_digestao=200)), Fisiologia(_com(taxa_digestao=2000))
    for c in (lento, rapido):
        c.comer(4000)
        c.tick()
    assert rapido.estomago < lento.estomago and rapido.energia > lento.energia


# --- hormonio --------------------------------------------------------------------------------------------------------------

def _fome_depois_da_refeicao(sens: int) -> int:
    c = Fisiologia(_com(sensibilidade_saciedade=sens))
    c.comer(2000)
    for _ in range(30):
        c.tick()
    return c.fome


def test_hormonio_corta_o_ganho_de_fome():
    assert _fome_depois_da_refeicao(1000) < _fome_depois_da_refeicao(500) < _fome_depois_da_refeicao(0)


def test_sem_receptor_o_hormonio_nao_tem_efeito():
    c = Fisiologia(_com(sensibilidade_saciedade=0))
    c.comer(2000)
    for _ in range(30):
        c.tick()
    assert c.contas["fome_cortada_hormonio"] == 0


def test_hormonio_decai_ate_zero():
    c = Fisiologia(padrao())
    c.comer(1000)
    for _ in range(400):
        c.tick()
    assert c.saciedade == 0


# --- cruzamento ----------------------------------------------------------------------------------------------------------

def test_cruzamento_deterministico_e_dentro_das_faixas():
    pai, mae = sortear(1), sortear(2)
    a, b = cruzar(pai, mae, 5), cruzar(pai, mae, 5)
    assert a == b
    for g, p, m, f in zip(GENES, pai.valores, mae.valores, a.filho.valores):
        assert g.minimo <= f <= g.maximo
        assert min(p, m) - g.passo_mutacao <= f <= max(p, m) + g.passo_mutacao


def test_sem_mutacao_o_filho_e_a_media():
    pai, mae = sortear(1), sortear(2)
    cz = cruzar(pai, mae, 5, mutacao_por_mil=0)
    assert cz.mutacoes == ()
    for p, m, f in zip(pai.valores, mae.valores, cz.filho.valores):
        assert abs(2 * f - (p + m)) <= 1


def test_mutacao_e_pequena_e_registrada():
    pai, mae = sortear(1), sortear(2)
    base = cruzar(pai, mae, 5, mutacao_por_mil=0).filho
    for s in range(1, 10):
        cz = cruzar(pai, mae, s, mutacao_por_mil=1000)
        assert cz.mutacoes   # com chance total, ao menos um gene muda (os que batem no teto podem nao mudar)
        for nome, delta in cz.mutacoes:
            g = GENES[NOMES.index(nome)]
            assert abs(delta) <= g.passo_mutacao
            assert cz.filho[nome] - base[nome] == delta


def test_cruzar_recusa_estado_vivido():
    vivido = Fisiologia(sortear(1))
    vivido.comer(1000)
    vivido.tick()
    with pytest.raises(TypeError):
        cruzar(vivido, sortear(2), 5)   # type: ignore[arg-type]


def test_a_vida_nao_muda_o_genoma():
    g = sortear(1)
    sha = g.sha256()
    c = Fisiologia(g)
    for ev in entradas_sinteticas(1):
        c.comer(ev["q"]) if ev["t"] == "comer" else [c.tick() for _ in range(ev["n"])]
    assert c.genoma.sha256() == sha and cruzar(g, g, 7, 0).filho == g


# --- replay ----------------------------------------------------------------------------------------------------------------

def _log() -> list[dict]:
    pai, mae = sortear(1), sortear(2)
    cz = cruzar(pai, mae, 3, 150)
    return [evento_origem(cz.filho, pai, mae, 3, 150)] + entradas_sinteticas(4)


# gabarito gravado na primeira execucao desta POC; muda so se a fisiologia, os genes ou o cruzamento mudarem de proposito
GABARITO_SHA = "ed4a68bb798ce7b8d5e8f43f6521be229a5a7877c45945e46e49d60a06544d87"


def test_replay_mesmo_log_mesma_trajetoria():
    _, t1, s1 = reproduzir(_log())
    _, t2, s2 = reproduzir(_log())
    assert t1 == t2 and s1 == s2
    assert s1 == GABARITO_SHA


def test_replay_em_outro_processo_com_outro_hash_seed():
    codigo = ("from orgaos_genetica.verificar_poc import _log; from orgaos_genetica.replay import reproduzir; "
              "print(reproduzir(_log())[2])")
    shas = set()
    for hs in ("0", "123"):
        env = {**os.environ, "PYTHONHASHSEED": hs}
        out = subprocess.run([sys.executable, "-c", codigo], cwd=POC, env=env, capture_output=True, text=True, check=True)
        shas.add(out.stdout.strip())
    assert shas == {reproduzir(_log())[2]}


def test_replay_entradas_diferentes_dao_trajetorias_diferentes():
    log = _log()
    outro = log[:1] + entradas_sinteticas(5)
    assert reproduzir(log)[2] != reproduzir(outro)[2]


def test_replay_falha_alto():
    log = _log()
    with pytest.raises(ValueError):
        reproduzir(log + [{"t": "voar"}])
    adulterado = [dict(log[0], genoma={**log[0]["genoma"], "gasto_basal": 6})] + log[1:]
    with pytest.raises(ValueError):
        reproduzir(adulterado)
    with pytest.raises(ValueError):
        reproduzir(log[1:])
    filho_trocado = dict(log[0])
    g = sortear(9)
    filho_trocado.update(genoma=g.como_dict(), sha256=g.sha256())
    with pytest.raises(ValueError):
        reproduzir([filho_trocado] + log[1:])
