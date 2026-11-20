"""A medida do carater do v11 (PW-4; experiments/medir_carater_v11.py, artifacts_v2_w_porte/carater_v11.json): as constantes sao as do jogo, o
metodo e o de `caraterPolitica`, e o artefato se refaz igual."""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import medir_carater_v11 as m  # noqa: E402


def test_as_constantes_sao_as_do_jogo():
    ccp, desloc = m.constantes_web()
    assert ccp == {"estados": 32, "amostras": 100, "semente": 9001, "escala": 0.05}
    assert set(desloc) == {"adolescente", "adulto"} and all(set(d) == {"atento", "impetuoso", "paciente", "resistente"}
                                                           for d in desloc.values())
    assert (m.T_ADOL, m.T_ADUL) == (900, 1980)


def test_o_artefato_se_refaz_igual():
    gravado = json.loads(m.ARQUIVO.read_text(encoding="utf-8"))
    agora = json.loads(json.dumps(m.medir(), ensure_ascii=False))
    assert {k: v for k, v in agora.items() if k != "codigo"} == {k: v for k, v in gravado.items() if k != "codigo"}
    assert len(agora["pets"]) == 2 * len(m.DONOS) * len(m.SEMENTES)
    c = agora["criterio"]
    assert c["perto"] == (c["linhas"]["perto"] and c["formas"]["perto"] and c["escala"]["perto"])
