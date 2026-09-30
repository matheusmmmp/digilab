"""Etapa A do canal do dono (docs/PLANO_ANALISE_CANAL_DONO.md): o replay de uma vida gravada da o mesmo carater em
T_ADOL, a mesma linha e os mesmos dados da simulacao."""
from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

from digilab.donos_educacao import simular_vida_educacao  # noqa: E402
from digilab.config import CONFIG_LESOES_LIGADA  # noqa: E402
from run_educacao import _fabricas, rival_por_nome, ticks_sparring  # noqa: E402
from run_natureza_criacao import chave, genoma, vida_com_genoma  # noqa: E402
from sinal_dono import CAMPOS_CONFERIDOS, medir  # noqa: E402


def test_replay_da_o_carater_da_simulacao(tmp_path):
    b, g, r = "aleatorio", 81001, 82003
    esp, temp_ovo, tmp = genoma(g, "brasa")
    _, dados_sim = vida_com_genoma(b, g, r, esp, temp_ovo, tmp, 14, str(tmp_path), chave(b, g, r))
    fp, fm_base, _, pet = _fabricas(b, r, esp, tmp, temp_ovo)
    simular_vida_educacao(b, r, 14, esp, tmp, cl=CONFIG_LESOES_LIGADA, sparring=ticks_sparring(b),
                          rival_sparring=pet.rival, lutador_do_pet=pet.lutador, rival_por_nome=rival_por_nome)
    nome, dados, port = medir((b, g, r, "brasa", str(tmp_path / "vidas")))
    assert nome == chave(b, g, r)
    assert port["carater_adol"] == pet.adol[0] and port["linha"] == pet.adol[1]
    for k in CAMPOS_CONFERIDOS:
        assert dados.get(k) == dados_sim.get(k), k
