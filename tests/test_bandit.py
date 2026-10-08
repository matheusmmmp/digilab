"""Etapa 3 - bandit contextual sob o Protocol Politica."""

import json
import random
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from digilab import AcaoPet, Observacao, Politica, PoliticaInstinto  # noqa: E402
from digilab.events import ACOES_PET_HOJE  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.policies import PoliticaBandit  # noqa: E402
from digilab.policies.bandit import distribuicao_instinto  # noqa: E402
from digilab.protocol import ENGINE_SHA256_V0, sha256_engine  # noqa: E402
from digilab.treino import reproduzir_com_feedback, simular_vida  # noqa: E402


def _obs(fome=0.6, higiene=0.8, energia=0.7, humor=0.6, hora=0.5, tdc=10):
    return Observacao(
        vetor_estado=(fome, higiene, energia, humor, 1.0, 0.0, 0.0, hora),
        ticks_desde_cuidado=tdc,
        total_cuidados=3,
    )


def test_cumpre_o_protocolo_e_engine_intocado():
    assert isinstance(PoliticaBandit(), Politica)
    assert sha256_engine() == ENGINE_SHA256_V0


def test_prior_por_sonda_bate_com_amostragem_do_instinto():
    inst = PoliticaInstinto()
    for obs in (_obs(), _obs(fome=0.40), _obs(energia=0.1), _obs(fome=0.2)):
        exata = distribuicao_instinto(inst, obs, 40)
        rng = random.Random(0)
        n = 20000
        cont = Counter(inst.agir(obs, rng) for _ in range(n))
        for a in ACOES_PET_HOJE:
            assert abs(cont[a] / n - exata[a]) < 0.015, (obs, a)


def test_recem_nascido_se_comporta_como_o_prior():
    b = PoliticaBandit()
    obs = _obs()
    p0 = b.prior(obs)
    rng = random.Random(1)
    n = 6000
    cont = Counter(b.agir(obs, rng) for _ in range(n))
    # com theta = 0 sobra so a variancia de Thompson; o grosso do prior se mantem
    mais_provavel = max(p0, key=p0.get)
    assert cont.most_common(1)[0][0] is mais_provavel


def test_elogio_desloca_a_preferencia():
    obs = _obs()
    b = PoliticaBandit()
    from digilab.policy import Transicao
    from digilab import AcaoUsuario

    for i in range(60):
        o = Observacao(obs.vetor_estado, ticks_desde_cuidado=5, total_cuidados=0)
        b.observar(Transicao(o, AcaoPet.EXPLORAR, o))
        b.receber_acao_dono(AcaoUsuario.ELOGIAR, 15 * (i + 1))
    rng1, rng0 = random.Random(3), random.Random(3)
    novo = PoliticaBandit()
    n = 3000
    treinado = sum(b.agir(obs, rng1) is AcaoPet.EXPLORAR for _ in range(n))
    base = sum(novo.agir(obs, rng0) is AcaoPet.EXPLORAR for _ in range(n))
    assert treinado > base


def test_vida_com_bandit_reproduz_bit_a_bit_inclusive_parametros():
    vida = simular_vida("atencioso", criar_dono("atencioso"), PoliticaBandit(), 101, 3, 48)
    r = reproduzir_com_feedback(vida.motor.log, lambda cfg: PoliticaBandit(cfg), semente=101)
    assert r.estado() == vida.motor.estado()
    assert r.acoes_recentes(10**9) == vida.motor.acoes_recentes(10**9)
    assert r.politica.estado_interno() == vida.motor.politica.estado_interno()


def test_estado_interno_serializavel_e_recarregavel():
    vida = simular_vida("incoerente", criar_dono("incoerente"), PoliticaBandit(), 202, 2, 32)
    d = vida.motor.politica.estado_interno()
    texto = json.dumps(d)
    p2 = PoliticaBandit.de_estado_interno(json.loads(texto))
    assert p2.estado_interno() == d
    obs = _obs()
    assert [vida.motor.politica.agir(obs, random.Random(k)) for k in range(50)] == [
        p2.agir(obs, random.Random(k)) for k in range(50)
    ]


def test_aprende_de_fato():
    vida = simular_vida("atencioso", criar_dono("atencioso"), PoliticaBandit(), 303, 3, 48)
    info = vida.motor.politica.estado_interno()
    assert sum(info["atualizacoes_por_acao"].values()) > 0
    assert info["parametros_aprendidos"] > 0
