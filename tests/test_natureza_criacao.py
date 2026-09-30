"""E1 da linhagem (docs/PLANO_ANALISE_LINHAGEM.md): genoma separado do ambiente e a decomposicao cruzada."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

from digilab.config import CONFIG_CATALOGO  # noqa: E402
from digilab.evolucao import ovo  # noqa: E402
from digilab.metrics import (bootstrap_cruzado, componentes_cruzados, decomposicao_cruzada,  # noqa: E402
                             ic_percentil, tabela_cruzada)
from digilab.temperamento import sortear  # noqa: E402
import run_educacao  # noqa: E402
from run_natureza_criacao import especie_da_rodada, genoma, vida_com_genoma  # noqa: E402

S = 69001          # ovo da fumaca da V3


def test_com_sementes_iguais_a_vida_e_a_da_v3(tmp_path):
    """g = r: o mesmo log byte a byte, os mesmos dados e o mesmo pet do painel que run_educacao._vida."""
    b = "atencioso"
    (_, s), spec_v3, dados_v3, _ = run_educacao._vida((b, S, 14, str(tmp_path / "v3"), {}))
    esp, temp_ovo, tmp = genoma(S)
    spec, dados = vida_com_genoma(b, S, S, esp, temp_ovo, tmp, 14, str(tmp_path / "e1"), f"{b}@{S}")
    log_v3 = (tmp_path / "v3" / "vidas" / f"{b}@{S}.jsonl").read_bytes()
    log_e1 = (tmp_path / "e1" / "vidas" / f"{b}@{S}.jsonl").read_bytes()
    assert log_e1 == log_v3
    assert json.dumps(spec, sort_keys=True) == json.dumps(spec_v3, sort_keys=True)
    for k in ("especie", "morta", "morte", "sparring", "adulto_liberado", "disciplina_final", "saude_final",
              "vinculo_final", "sombria", "treino_total", "forma"):
        assert dados[k] == dados_v3[k], k


def test_genoma_vem_so_da_semente_do_genoma():
    esp, temp_ovo, tmp = genoma(81001)
    assert (esp, temp_ovo) == ovo(81001) and tmp == sortear(81001)
    esp2, temp_ovo2, tmp2 = genoma(81001, "limo")
    assert esp2 == "limo" and temp_ovo2 == temp_ovo and tmp2 == tmp      # a especie fixa nao mexe nos temperamentos


def test_especies_balanceadas_e_fixa():
    ativas = CONFIG_CATALOGO.especies_ativas
    esp = [especie_da_rodada("rodizio", i) for i in range(40)]
    assert all(esp.count(e) == 10 for e in ativas)
    assert especie_da_rodada("brasa", 7) == "brasa"
    with pytest.raises(ValueError):
        especie_da_rodada("dragao", 0)


def _aditivo(ruido=None):
    G, D, R = [0.0, 1.0, 3.0, -1.0, 2.0], [0.0, 0.5, 1.5], [0.2, -0.2, 0.4, 0.0]
    return [[[G[i] + D[j] + R[k] + (ruido(i, j, k) if ruido else 0.0) for k in range(4)] for j in range(3)] for i in range(5)]


def test_componentes_cruzados_no_aditivo_exato():
    c = componentes_cruzados(_aditivo())["componentes"]
    var = lambda xs: sum((x - sum(xs) / len(xs)) ** 2 for x in xs) / (len(xs) - 1)  # noqa: E731
    assert c["G"] == pytest.approx(var([0.0, 1.0, 3.0, -1.0, 2.0]))
    assert c["D"] == pytest.approx(var([0.0, 0.5, 1.5]))
    assert c["R"] == pytest.approx(var([0.2, -0.2, 0.4, 0.0]))
    for k in ("GD", "GR", "DR", "e"):
        assert c[k] == pytest.approx(0.0, abs=1e-12)


def test_somas_de_quadrados_fecham_e_tabela_incompleta_falha():
    y = _aditivo(lambda i, j, k: ((i * 7 + j * 3 + k * 5) % 11) / 20)
    c = componentes_cruzados(y)
    assert sum(c["ss"].values()) == pytest.approx(c["ss_total"])
    valor = {(f"g{i}", f"d{j}", f"r{k}"): y[i][j][k] for i in range(5) for j in range(3) for k in range(4)}
    assert decomposicao_cruzada(valor)["componentes"]["G"] == pytest.approx(c["componentes"]["G"])
    del valor[("g0", "d0", "r0")]
    with pytest.raises(ValueError):
        tabela_cruzada(valor)


def test_bootstrap_cruzado_deterministico():
    y = _aditivo(lambda i, j, k: ((i + 2 * j + 3 * k) % 5) / 10)
    f = lambda t: componentes_cruzados(t)["componentes"]["G"]  # noqa: E731
    a = bootstrap_cruzado(y, f, 200, 7)
    assert a == bootstrap_cruzado(y, f, 200, 7)
    so_g = bootstrap_cruzado(y, f, 200, 7, reamostrar="G")
    assert so_g != a and len(ic_percentil(a)) == 2
    with pytest.raises(ValueError):
        bootstrap_cruzado(y, f, 10, 7, reamostrar="D")
