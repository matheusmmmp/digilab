"""V2, L0 (docs/TAREFA_V2_L0_LOBOS.md): politica com lobos nomeados, aprendizado desligado.

Gates: G2 (vida byte a byte igual a do instinto, nos dois motores) e G1 (replay bit a bit pelo log).
Sementes: so as dos testes (101...505 e derivadas); nenhuma reservada."""

import ast
import json
import random
import sys
from collections import Counter
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab import AcaoPet, AcaoUsuario, Observacao, Politica, PoliticaInstinto  # noqa: E402
from digilab.config import CONFIG_LOBOS, ConfigLobos  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.obediencia import MotorPersonalidade  # noqa: E402
from digilab.policies import PoliticaLobos  # noqa: E402
from digilab.policies.lobos import (ENTRADAS, PARAMETROS_LOBOS_L0, PRIOR_INSTINTO, REGRAS, ativacao, impulsos,  # noqa: E402
                                    sortear, validar_parametros_lobos)
from digilab.policy import Transicao  # noqa: E402
from digilab.protocol import ENGINE_SHA256_V0, sha256_engine  # noqa: E402
from digilab.temperamento import sortear as sortear_temperamento  # noqa: E402
from digilab.treino import MotorComFeedback, PoliticaTreinavel, reproduzir_com_feedback, simular_vida  # noqa: E402

DONOS = ("atencioso", "relapso", "aleatorio", "incoerente")
SEMENTES = (101, 202, 303, 404, 505)
DIAS, ORC = 3, 48


class InstintoComGancho(PoliticaInstinto):
    """O instinto puro nao roda no MotorPersonalidade (o embrulho sempre repassa receber_acao_dono, que o
    instinto nao tem). O controle do G2 nesse motor e o instinto com o gancho vazio: decide igual, ignora o dono."""

    def receber_acao_dono(self, acao, tick) -> None:
        return None


def _fabrica_personalidade(politica, cfg, semente):
    return MotorPersonalidade(politica, cfg, semente, sortear_temperamento(semente))


def _resumo(motor):
    """Tudo que uma vida produz: log, estado final, acoes do pet e o estado das duas rngs do motor."""
    return (motor.log.para_jsonl(), motor.estado(), motor.acoes_recentes(10**9),
            motor._rng_politica.getstate(), motor._rng_ambiente.getstate())


def _obs_aleatoria(rng):
    return Observacao(
        vetor_estado=(rng.random(), rng.random(), rng.random(), rng.random(), rng.random(),
                      rng.randrange(6) / 5.0, float(rng.randrange(2)), rng.random()),
        ticks_desde_cuidado=rng.randrange(0, 600),
        total_cuidados=rng.randrange(0, 50),
    )


# ------------------------------------------------------------------ contrato e parametros


def test_cumpre_o_protocolo_e_engine_intocado():
    p = PoliticaLobos()
    assert isinstance(p, Politica) and isinstance(p, PoliticaTreinavel)
    assert sha256_engine() == ENGINE_SHA256_V0


def test_todo_parametro_tem_status_proposto():
    validar_parametros_lobos()
    assert all(status == "PROPOSTO" for status, _ in PARAMETROS_LOBOS_L0.values())
    assert CONFIG_LOBOS.aprendizado_ligado is False
    assert CONFIG_LOBOS.escala == 2 ** CONFIG_LOBOS.bits_ponto_fixo


def test_aprendizado_ligado_falha_alto():
    with pytest.raises(NotImplementedError, match="L1"):
        PoliticaLobos(cfg_lobos=ConfigLobos(aprendizado_ligado=True))


def test_so_stdlib_e_sem_funcoes_transcendentais():
    arvore = ast.parse((RAIZ / "digilab" / "policies" / "lobos.py").read_text(encoding="utf-8"))
    modulos = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            modulos |= {n.name.split(".")[0] for n in no.names}
        elif isinstance(no, ast.ImportFrom) and no.level == 0 and no.module:
            modulos.add(no.module.split(".")[0])
    assert modulos <= sys.stdlib_module_names, modulos
    assert "math" not in modulos


# ------------------------------------------------------------------ pesos


def test_pesos_sao_inteiros_iniciados_no_prior_e_abaixo_do_teto():
    p = PoliticaLobos()
    e = p.estado_interno()
    assert e["parametros_aprendidos"] == p.n_pesos() == len(REGRAS) * len(AcaoPet) * len(ENTRADAS) == 490
    assert e["parametros_aprendidos"] < CONFIG_LOBOS.maximo_pesos
    for regra, por_acao in e["pesos"].items():
        for acao, pesos in por_acao.items():
            assert all(type(w) is int for w in pesos), (regra, acao)
            assert pesos == e["pesos_prior"][regra][acao]
    S = CONFIG_LOBOS.escala
    assert e["pesos"]["tempo_livre"]["explorar"] == [2 * S, 0, 0, 2 * S, 0, 0, 0, 0, 0, 0]
    assert e["pesos"]["tempo_livre"]["brincar"] == [S, 0, 0, 0, 3 * S, 0, 0, 0, 0, 0]
    assert e["pesos"]["fome_moderada"]["comer"] == e["pesos"]["fome_moderada"]["chamar_atencao"] == [S] + [0] * 9


def test_prior_reproduz_os_floats_do_instinto():
    """Com S potencia de dois, a ativacao do prior devolve os MESMOS floats que PoliticaInstinto.agir escreve."""
    p = PoliticaLobos()
    rng = random.Random(7)
    for _ in range(500):
        obs = _obs_aleatoria(rng)
        energia, humor = obs.vetor_estado[2], obs.vetor_estado[3]
        x = p.percepcao(obs)
        c = p.contribuicoes("tempo_livre", tuple(PRIOR_INSTINTO["tempo_livre"]), x)["impulsos"]
        assert c[AcaoPet.OCIOSO] == 3.0
        assert c[AcaoPet.EXPLORAR] == 2.0 + 2.0 * energia
        assert c[AcaoPet.BRINCAR] == 1.0 + 3.0 * humor
        assert c[AcaoPet.CHAMAR_ATENCAO] == 1.0


def test_ativacao_e_laco_simples_sem_somatorio_compensado():
    assert ativacao([3 * 1024, 0, 2 * 1024], [1.0, 0.3, 0.7], 1024) == (3.0 + 0.0) + 2.0 * 0.7
    with pytest.raises(ValueError):
        ativacao([1, 2], [1.0], 1024)


# ------------------------------------------------------------------ impulsos e sorteio


def test_impulsos_cobrem_todas_as_regras_do_instinto_sem_consumir_rng():
    inst = PoliticaInstinto()
    rng = random.Random(11)
    vistas = Counter()
    for _ in range(3000):
        obs = _obs_aleatoria(rng)
        regra, candidatos = impulsos(inst, obs)
        vistas[regra] += 1
        assert regra in REGRAS
        assert set(candidatos) <= set(PRIOR_INSTINTO[regra]), (regra, candidatos)
        assert len(candidatos) == len(set(candidatos)) >= 1
    assert set(vistas) == set(REGRAS), vistas


def test_sorteio_replica_random_choices():
    rng = random.Random(3)
    for _ in range(2000):
        n = rng.randrange(1, 6)
        pesos = [rng.random() * 4 for _ in range(n)]
        if sum(pesos) <= 0.0:
            continue
        semente = rng.randrange(10**9)
        esperado = random.Random(semente).choices(list(range(n)), weights=pesos, k=1)[0]
        assert sortear(pesos, random.Random(semente).random()) == esperado
    assert sortear([1.0, 1.0], 0.4999999999999999) == 0 and sortear([1.0, 1.0], 0.5) == 1
    with pytest.raises(ValueError):
        sortear([0.0, 0.0], 0.3)


def test_decisao_a_decisao_igual_ao_instinto_em_todas_as_regras():
    """Mesma observacao e mesma rng: mesma acao e mesmo estado da rng depois (nenhuma chamada a mais ou a menos)."""
    inst, lobos = PoliticaInstinto(), PoliticaLobos()
    rng = random.Random(5)
    regras = Counter()
    for i in range(3000):
        obs = _obs_aleatoria(rng)
        r1, r2 = random.Random(i), random.Random(i)
        assert inst.agir(obs, r1) is lobos.agir(obs, r2), (i, obs)
        assert r1.getstate() == r2.getstate(), (i, obs)
        assert lobos.ultima_regra == inst.ultima_regra
        regras[lobos.ultima_regra] += 1
    assert set(regras) == set(REGRAS)
    assert not lobos.pesos_mudaram()


# ------------------------------------------------------------------ G2: vida byte a byte


@pytest.mark.parametrize("dono", DONOS)
def test_g2_motor_com_feedback_byte_a_byte(dono):
    for s in SEMENTES:
        a = simular_vida(dono, criar_dono(dono), PoliticaInstinto(), s, DIAS, ORC)
        b = simular_vida(dono, criar_dono(dono), PoliticaLobos(), s, DIAS, ORC)
        assert isinstance(b.motor, MotorComFeedback)
        assert _resumo(a.motor) == _resumo(b.motor), (dono, s)
        assert not b.motor.politica.pesos_mudaram()


@pytest.mark.parametrize("dono", DONOS)
def test_g2_motor_personalidade_byte_a_byte(dono):
    for s in SEMENTES:
        a = simular_vida(dono, criar_dono(dono), InstintoComGancho(), s, DIAS, ORC, fabrica_motor=_fabrica_personalidade)
        b = simular_vida(dono, criar_dono(dono), PoliticaLobos(), s, DIAS, ORC, fabrica_motor=_fabrica_personalidade)
        assert _resumo(a.motor) == _resumo(b.motor), (dono, s)
        assert a.motor._rng_obediencia.getstate() == b.motor._rng_obediencia.getstate()
        assert [r.para_dict() for r in a.motor.recusas] == [r.para_dict() for r in b.motor.recusas]
        assert [d.para_dict() for d in a.motor.desejos] == [d.para_dict() for d in b.motor.desejos]
        assert a.motor.vinculo.para_dict() == b.motor.vinculo.para_dict()
        assert not b.motor.politica.pesos_mudaram()


def test_g2_vida_com_todas_as_regras():
    """Orcamento baixo com o aleatorio: as sete regras (inclusive fome moderada, a unica com random() < t, e
    abandono) disparam na vida, nao so na observacao aleatoria."""
    a = simular_vida("aleatorio", criar_dono("aleatorio"), PoliticaInstinto(), 101, DIAS, 24)
    b = simular_vida("aleatorio", criar_dono("aleatorio"), PoliticaLobos(), 101, DIAS, 24)
    assert _resumo(a.motor) == _resumo(b.motor)
    regras = Counter(m["regra"] for m in b.motor.politica.motivos)
    assert set(regras) == set(REGRAS), regras


# ------------------------------------------------------------------ G1: replay


@pytest.mark.parametrize("fabrica", [None, _fabrica_personalidade], ids=["feedback", "personalidade"])
def test_g1_replay_bit_a_bit(fabrica):
    for dono, s in (("atencioso", 101), ("aleatorio", 303)):
        vida = simular_vida(dono, criar_dono(dono), PoliticaLobos(), s, DIAS, ORC, fabrica_motor=fabrica)
        log = type(vida.motor.log).de_jsonl(vida.motor.log.para_jsonl())
        replay = reproduzir_com_feedback(log, lambda cfg: PoliticaLobos(cfg), semente=s, fabrica_motor=fabrica)
        assert _resumo(replay) == _resumo(vida.motor)
        original = json.dumps(vida.motor.politica.estado_interno(), sort_keys=True)
        assert json.dumps(replay.politica.estado_interno(), sort_keys=True) == original


# ------------------------------------------------------------------ feedback e motivo


def test_feedback_do_dono_nao_muda_os_pesos():
    vida = simular_vida("atencioso", criar_dono("atencioso"), PoliticaLobos(), 202, DIAS, ORC)
    p = vida.motor.politica
    mem = p.memoria.para_dict()
    assert mem["elogios"] + mem["broncas"] > 0 and mem["cuidados"] > 0
    assert mem["decisoes"] == len(p.motivos) == DIAS * 1440 // vida.motor.cfg.intervalo_decisao_ticks
    assert not p.pesos_mudaram()
    # feedback direto, fora da vida: tambem nao muda
    obs = _obs_aleatoria(random.Random(1))
    p.observar(Transicao(obs, AcaoPet.BRINCAR, obs))
    for acao in AcaoUsuario:
        p.receber_acao_dono(acao, 10**6)
    assert not p.pesos_mudaram()
    assert p.estado_interno()["pesos"] == p.estado_interno()["pesos_prior"]


def test_motivo_fecha_com_a_decisao():
    vida = simular_vida("aleatorio", criar_dono("aleatorio"), PoliticaLobos(), 202, DIAS, 24)
    motivos = vida.motor.politica.estado_interno()["motivos"]
    assert len(motivos) == vida.motor.politica.memoria.decisoes
    for m in motivos:
        c = m["contribuicoes"]
        assert set(c) == {"impulsos", "decisao", "memoria_emocao"}
        assert set(m["percepcao"]) == set(ENTRADAS)
        for a in m["candidatos"]:
            assert c["impulsos"][a] + c["decisao"][a] + c["memoria_emocao"][a] == m["pesos"][a]
            assert c["decisao"][a] == 0.0 and c["memoria_emocao"][a] == 0.0
        if len(m["candidatos"]) == 1:
            assert m["u"] is None and m["acao"] == m["candidatos"][0]
        else:
            assert 0.0 <= m["u"] < 1.0
            assert m["acao"] == m["candidatos"][sortear([m["pesos"][a] for a in m["candidatos"]], m["u"])]
        assert m["lobo_decisivo"] == "impulsos"
        assert m["acao"] in m["candidatos"] and m["regra"] in REGRAS
