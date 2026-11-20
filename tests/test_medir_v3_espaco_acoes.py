"""A medicao do espaco de acoes do V3 (experiments/medir_v3_espaco_acoes.py, artifacts_v2_v3/espaco_acoes.json; docs/futuro/v3_espaco_acoes.md):
a reconstrucao das regras do instinto e a do instinto de verdade, e o artefato se refaz igual."""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import medir_v3_espaco_acoes as m  # noqa: E402

from digilab.config import CONFIG_LOBOS, CONFIG_PADRAO  # noqa: E402
from digilab.policies.lobos import ENTRADAS, percepcao  # noqa: E402
from digilab.policy import Observacao, PoliticaInstinto  # noqa: E402


def test_as_regras_refeitas_sao_as_do_instinto():
    """em 20.000 observacoes aleatorias, a primeira regra que vale (pela percepcao dos lobos) e a do PoliticaInstinto, e os candidatos
    refeitos contem a acao que ele escolhe"""
    rng = random.Random(7)
    inst = PoliticaInstinto(CONFIG_PADRAO)
    for _ in range(20_000):
        v = (rng.random(), rng.random(), rng.random(), rng.random(), rng.random(), rng.randrange(6) / 5, float(rng.random() < 0.4),
             rng.random())
        obs = Observacao(vetor_estado=v, ticks_desde_cuidado=rng.randrange(0, 600), total_cuidados=0)
        p = dict(zip(ENTRADAS, percepcao(obs, CONFIG_LOBOS.escala_ticks_desde_cuidado)))
        acao = inst.agir(obs, random.Random(1))
        valem = m.regras_que_valem(p)
        assert valem[0] == inst.ultima_regra
        assert acao.value in m.candidatos_da_regra(valem[0], p)
        assert valem[-1] == "tempo_livre" and valem == [r for r in m.ORDEM_INSTINTO if r in valem]


def test_o_artefato_se_refaz_igual():
    gravado = json.loads(m.ARQUIVO.read_text(encoding="utf-8"))
    m.main()
    assert json.loads(m.ARQUIVO.read_text(encoding="utf-8")) == gravado
    v = gravado["v11"]
    assert v["n_decisoes"] == 26880 and abs(v["frac_forcadas"] - 0.5525) < 1e-3          # o mesmo E0
    assert v["credito"]["forcadas"]["com_peso_mudado"] == 0                               # o credito nas forcadas nao muda peso
