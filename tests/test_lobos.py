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
from digilab.config import CONFIG_LOBOS, CONFIG_LOBOS_APRENDIZ, ConfigLobos  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.obediencia import MotorPersonalidade  # noqa: E402
from digilab.policies import PoliticaLobos  # noqa: E402
from digilab.policies.lobos import (ENTRADAS, PARAMETROS_LOBOS, PARAMETROS_LOBOS_L0, PRIOR_INSTINTO, REGRAS, arred,  # noqa: E402
                                    ativacao, div_arred, impulsos, sortear, validar_parametros_lobos)
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
    assert all(status == "PROPOSTO" for status, _ in PARAMETROS_LOBOS.values())
    assert set(PARAMETROS_LOBOS_L0) <= set(PARAMETROS_LOBOS)
    assert CONFIG_LOBOS.aprendizado_ligado is False
    assert CONFIG_LOBOS.escala == 2 ** CONFIG_LOBOS.bits_ponto_fixo


def test_padrao_e_l0_e_parametros_invalidos_do_l1_falham_alto():
    assert not PoliticaLobos().aprende and CONFIG_LOBOS.aprendizado_ligado is False
    assert PoliticaLobos(cfg_lobos=CONFIG_LOBOS_APRENDIZ).aprende
    with pytest.raises(ValueError):
        PoliticaLobos(cfg_lobos=ConfigLobos(aprendizado_ligado=True, passo=0))
    with pytest.raises(TypeError):
        PoliticaLobos(cfg_lobos=ConfigLobos(aprendizado_ligado=True, teto=2048.0))


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
        assert set(c) == {"impulsos", "decisao", "memoria_emocao", "piso"}
        assert set(m["percepcao"]) == set(ENTRADAS)
        for a in m["candidatos"]:
            assert c["impulsos"][a] + c["decisao"][a] + c["memoria_emocao"][a] + c["piso"][a] == m["pesos"][a]
            assert c["decisao"][a] == 0.0 and c["memoria_emocao"][a] == 0.0 and c["piso"][a] == 0.0
        if len(m["candidatos"]) == 1:
            assert m["u"] is None and m["acao"] == m["candidatos"][0]
        else:
            assert 0.0 <= m["u"] < 1.0
            assert m["acao"] == m["candidatos"][sortear([m["pesos"][a] for a in m["candidatos"]], m["u"])]
        assert m["lobo_decisivo"] == "impulsos"
        assert m["acao"] in m["candidatos"] and m["regra"] in REGRAS


# ================================================================== L1: o lobo de decisao aprende


def _obs_tempo_livre(energia=0.7, humor=0.6):
    return Observacao(vetor_estado=(0.8, 0.9, energia, humor, 1.0, 0.0, 0.0, 0.5), ticks_desde_cuidado=10, total_cuidados=3)


def _decidir(p, obs, semente=1):
    acao = p.agir(obs, random.Random(semente))
    p.observar(Transicao(obs, acao, obs))
    return acao


def test_l1_arredondamentos_inteiros_simetricos():
    assert arred(2.5) == 3 and arred(-2.5) == -3 and arred(0.49) == 0 and arred(-0.49) == 0
    assert div_arred(7, 2) == 4 and div_arred(-7, 2) == -4 and div_arred(5, 4) == 1 and div_arred(-5, 4) == -1
    with pytest.raises(ValueError):
        div_arred(1, 0)


def test_l1_elogio_sobe_a_escolhida_e_desce_as_outras_em_inteiros():
    p = PoliticaLobos(cfg_lobos=CONFIG_LOBOS_APRENDIZ)
    obs = _obs_tempo_livre()
    acao = _decidir(p, obs)
    antes = {a: list(v) for a, v in p._pesos["tempo_livre"].items()}
    p.receber_acao_dono(AcaoUsuario.ELOGIAR, 20)
    depois = p._pesos["tempo_livre"]
    S, x = CONFIG_LOBOS_APRENDIZ.escala, p.percepcao(obs)
    for a in PRIOR_INSTINTO["tempo_livre"]:
        for j, (w0, w1) in enumerate(zip(antes[a], depois[a])):
            assert type(w1) is int
            if arred(x[j] * S) == 0:
                assert w1 == w0                      # entrada zero nao mexe no peso
            elif a is acao:
                assert w1 >= w0 and (j != 0 or w1 > w0), (a, j)    # entrada pequena pode arredondar a zero; o vies nao
            else:
                assert w1 <= w0 and (j != 0 or w1 < w0), (a, j)
            assert abs(w1 - w0) <= CONFIG_LOBOS_APRENDIZ.passo
    for a in set(AcaoPet) - set(PRIOR_INSTINTO["tempo_livre"]):
        assert depois[a] == antes[a]                 # quem nao era candidato nao muda
    assert p.pesos_mudaram() and p.estado_interno()["aprendizado"]["n_atualizacoes"] == 1


def test_l1_bronca_inverte_o_sinal():
    p1 = PoliticaLobos(cfg_lobos=CONFIG_LOBOS_APRENDIZ)
    p2 = PoliticaLobos(cfg_lobos=CONFIG_LOBOS_APRENDIZ)
    obs = _obs_tempo_livre()
    a1, a2 = _decidir(p1, obs), _decidir(p2, obs)
    assert a1 is a2
    p1.receber_acao_dono(AcaoUsuario.ELOGIAR, 20)
    p2.receber_acao_dono(AcaoUsuario.REPREENDER, 20)
    for a in PRIOR_INSTINTO["tempo_livre"]:
        for w0, w_el, w_br in zip(p1._prior["tempo_livre"][a], p1._pesos["tempo_livre"][a], p2._pesos["tempo_livre"][a]):
            assert w_el - w0 == -(w_br - w0)
    reg = p1._ultima
    assert reg is not None and reg["acao"] is a1
    assert all(0 <= v <= CONFIG_LOBOS_APRENDIZ.escala for v in reg["P"].values())


def test_l1_passo_depende_da_politica_atual():
    """O mesmo elogio, a mesma acao: quanto mais provavel a acao ja e, menor o passo (termo 1 - p)."""
    cfg = ConfigLobos(aprendizado_ligado=True, passo=128, teto=1 << 20)     # sem teto, para medir so o termo (1 - p)
    S = cfg.escala
    p = PoliticaLobos(cfg_lobos=cfg)
    obs = _obs_tempo_livre()
    # forca OCIOSO como escolhida duas vezes: antes e depois de deixar OCIOSO muito mais provavel
    def passo_para_ocioso(pol):
        for s in range(200):
            if pol.agir(obs, random.Random(s)) is AcaoPet.OCIOSO:
                pol.observar(Transicao(obs, AcaoPet.OCIOSO, obs))
                antes = pol._pesos["tempo_livre"][AcaoPet.OCIOSO][0]
                pol.receber_acao_dono(AcaoUsuario.ELOGIAR, pol._tick_ultima_decisao + 1)
                return pol._pesos["tempo_livre"][AcaoPet.OCIOSO][0] - antes
        raise AssertionError("nenhuma semente deu ocioso")
    d1 = passo_para_ocioso(p)
    p._pesos["tempo_livre"][AcaoPet.OCIOSO][0] = 40 * S          # ocioso quase certo
    d2 = passo_para_ocioso(p)
    assert d1 > d2 >= 0


def test_l1_regra_determinista_nao_aprende():
    p = PoliticaLobos(cfg_lobos=CONFIG_LOBOS_APRENDIZ)
    obs = Observacao(vetor_estado=(0.8, 0.9, 0.1, 0.6, 1.0, 0.0, 0.0, 0.5), ticks_desde_cuidado=10, total_cuidados=3)
    assert _decidir(p, obs) is AcaoPet.DORMIR
    p.receber_acao_dono(AcaoUsuario.ELOGIAR, 20)
    p.receber_acao_dono(AcaoUsuario.REPREENDER, 21)
    assert not p.pesos_mudaram() and p.estado_interno()["aprendizado"]["n_atualizacoes"] == 2


def test_l1_teto_corta_e_conta():
    cfg = ConfigLobos(aprendizado_ligado=True, passo=1 << 20, teto=100)
    p = PoliticaLobos(cfg_lobos=cfg)
    obs = _obs_tempo_livre()
    for k in range(5):
        _decidir(p, obs, semente=k)
        p.receber_acao_dono(AcaoUsuario.ELOGIAR, p._tick_ultima_decisao + 3)
        p._tick_ultimo_cuidado = 0                                  # (so para a obs fixa dar ticks crescentes)
        obs = Observacao(obs.vetor_estado, obs.ticks_desde_cuidado + 15, 3)
    assert p.desvio_maximo() == 100 and p.pesos_no_teto() > 0
    assert p.estado_interno()["aprendizado"]["cortes_teto"] > 0
    for a in AcaoPet:
        for w, w0 in zip(p._pesos["tempo_livre"][a], p._prior["tempo_livre"][a]):
            assert abs(w - w0) <= 100


def test_l1_chamado_atendido_paga_latencia_e_ignorado_paga_negativo():
    cfg = CONFIG_LOBOS_APRENDIZ
    obs = Observacao(vetor_estado=(0.4, 0.9, 0.7, 0.6, 1.0, 0.0, 0.0, 0.5), ticks_desde_cuidado=10, total_cuidados=3)
    semente = next(s for s in range(50) if PoliticaLobos(cfg_lobos=cfg).agir(obs, random.Random(s)) is AcaoPet.CHAMAR_ATENCAO)
    atendido, ignorado = PoliticaLobos(cfg_lobos=cfg), PoliticaLobos(cfg_lobos=cfg)
    for p in (atendido, ignorado):
        assert _decidir(p, obs, semente) is AcaoPet.CHAMAR_ATENCAO
        assert len(p._pendentes) == 1
    atendido.receber_acao_dono(AcaoUsuario.ALIMENTAR, 10 + 30)       # latencia 30 de 120
    assert atendido._n_recompensas["latencia"] == 1 and not atendido._pendentes
    w_at = atendido._pesos["fome_moderada"][AcaoPet.CHAMAR_ATENCAO][0]
    assert w_at > atendido._prior["fome_moderada"][AcaoPet.CHAMAR_ATENCAO][0]
    ignorado.receber_acao_dono(AcaoUsuario.ELOGIAR, 10 + 200)         # passou a janela: expira antes de creditar o elogio
    assert ignorado._n_recompensas["ignorado"] == 1
    assert ignorado._pesos["fome_moderada"][AcaoPet.CHAMAR_ATENCAO][0] < w_at


def test_l1_relogio_inconsistente_falha_alto():
    p = PoliticaLobos(cfg_lobos=CONFIG_LOBOS_APRENDIZ)
    obs = _obs_tempo_livre()
    _decidir(p, obs)
    with pytest.raises(RuntimeError, match="relogio"):
        _decidir(p, obs)
    with pytest.raises(RuntimeError, match="passado"):
        p.receber_acao_dono(AcaoUsuario.ELOGIAR, -1)


@pytest.mark.parametrize("fabrica", [None, _fabrica_personalidade], ids=["feedback", "personalidade"])
def test_l1_vida_aprende_e_rejoga_bit_a_bit(fabrica):
    fp = lambda cfg=None: PoliticaLobos(cfg, CONFIG_LOBOS_APRENDIZ)  # noqa: E731
    for dono, s in (("atencioso", 101), ("aleatorio", 303)):
        vida = simular_vida(dono, criar_dono(dono), fp(), s, DIAS, ORC, fabrica_motor=fabrica)
        p = vida.motor.politica
        assert p.pesos_mudaram() and p.desvio_maximo() > 0
        e = p.estado_interno()
        assert e["aprendizado"]["n_atualizacoes"] > 0 and sum(e["aprendizado"]["recompensas"].values()) > 0
        assert all(type(w) is int for r in e["pesos"].values() for v in r.values() for w in v)
        log = type(vida.motor.log).de_jsonl(vida.motor.log.para_jsonl())
        replay = reproduzir_com_feedback(log, fp, semente=s, fabrica_motor=fabrica)
        assert _resumo(replay) == _resumo(vida.motor)
        assert json.dumps(replay.politica.estado_interno(), sort_keys=True) == json.dumps(e, sort_keys=True)
        inst = simular_vida(dono, criar_dono(dono), PoliticaInstinto() if fabrica is None else InstintoComGancho(),
                            s, DIAS, ORC, fabrica_motor=fabrica)
        assert inst.motor.acoes_recentes(10**9) != vida.motor.acoes_recentes(10**9)


def test_l1_nao_muda_a_l0():
    """Com o aprendizado desligado nada do L1 roda: a vida e a do instinto (G2) e os pesos ficam no prior."""
    a = simular_vida("atencioso", criar_dono("atencioso"), PoliticaInstinto(), 202, DIAS, ORC)
    b = simular_vida("atencioso", criar_dono("atencioso"), PoliticaLobos(), 202, DIAS, ORC)
    assert _resumo(a.motor) == _resumo(b.motor)
    e = b.motor.politica.estado_interno()["aprendizado"]
    assert e["n_atualizacoes"] == 0 and e["pendentes"] == [] and e["ultima"] is None and not b.motor.politica.pesos_mudaram()


def test_l1_motivo_honesto_e_embrulho_nao_muda_a_vida():
    from digilab.motivo import FATORES_VIDA, PoliticaComMotivo, motivos_de_vida

    fp = lambda cfg=None: PoliticaLobos(cfg, CONFIG_LOBOS_APRENDIZ)  # noqa: E731
    vida = simular_vida("atencioso", criar_dono("atencioso"), fp(), 404, DIAS, ORC)
    com = simular_vida("atencioso", criar_dono("atencioso"), PoliticaComMotivo(fp()), 404, DIAS, ORC)
    assert _resumo(com.motor) == _resumo(vida.motor)
    motor, emb = motivos_de_vida(vida.motor.log, fp, 404)
    assert len(emb.motivos) == len(vida.motor.acoes_recentes(10**9)) == len(emb.diagnosticos)
    lobos = Counter(d["lobo"] for d in emb.diagnosticos)
    assert set(lobos) <= {"impulsos", "decisao"} and lobos["impulsos"] > 0
    for m, d in zip(emb.motivos, emb.diagnosticos):
        assert set(m.fatores) <= set(FATORES_VIDA) and len(m.fatores) <= 2
        assert d["valor_decidiu"] == (d["lobo"] == "decisao")
        if d["lobo"] == "impulsos" and m.fatores:
            assert set(m.fatores) <= {"energia", "dormindo", "hora", "fome", "higiene", "tempo_sem_cuidado", "humor"}
    # sem aprendizado o embrulho da exatamente os motivos do instinto
    log0 = simular_vida("atencioso", criar_dono("atencioso"), PoliticaLobos(), 404, DIAS, ORC).motor.log
    _, emb0 = motivos_de_vida(log0, lambda cfg=None: PoliticaLobos(cfg), 404)
    _, embi = motivos_de_vida(log0, lambda cfg=None: PoliticaInstinto(cfg), 404)
    assert [m.para_dict() for m in emb0.motivos] == [m.para_dict() for m in embi.motivos]


def test_fabricas_educacao_padrao_intacto():
    from digilab.educacao import fabricas_educacao
    from digilab.obediencia import PoliticaBanditPersonalidade
    from digilab.temperamento import NEUTRO

    fp, _ = fabricas_educacao(1, "brasa", NEUTRO)
    assert isinstance(fp(), PoliticaBanditPersonalidade)
    fp2, _ = fabricas_educacao(1, "brasa", NEUTRO, politica_fabrica=lambda cfg=None: PoliticaLobos(cfg, CONFIG_LOBOS_APRENDIZ))
    assert isinstance(fp2(), PoliticaLobos) and fp2().aprende


# ================================================================== L1, revisao 2: controle sem lobos, acoplado, metricas


def test_controle_sem_lobos_tem_a_mesma_capacidade_e_a_mesma_regra():
    from digilab.policies import PoliticaCamadaUnica
    from digilab.policies.camada_unica import CONTEXTOS, contexto

    c = PoliticaCamadaUnica(cfg_lobos=CONFIG_LOBOS_APRENDIZ)
    l = PoliticaLobos(cfg_lobos=CONFIG_LOBOS_APRENDIZ)
    assert c.n_pesos() == l.n_pesos() == 490 and isinstance(c, Politica) and isinstance(c, PoliticaTreinavel)
    assert set(c.estado_interno()["pesos"]) == set(CONTEXTOS)
    obs = _obs_tempo_livre()
    assert contexto(obs) == "contexto_3"               # hora 0.5 -> setimo 3
    # toda acao e candidata e o prior e o tempo livre + 1.0 nas acoes de regra
    acao = _decidir(c, obs)
    m = c.ultimo_motivo
    assert set(m["candidatos"]) == {a.value for a in AcaoPet} and m["sem_impulsos"]
    assert m["contribuicoes"]["impulsos"]["dormir"] == 1.0 and m["contribuicoes"]["impulsos"]["ocioso"] == 3.0
    c.receber_acao_dono(AcaoUsuario.ELOGIAR, 20)
    assert c.pesos_mudaram() and c.estado_interno()["aprendizado"]["n_atualizacoes"] == 1
    # o mesmo sinal nao toca os outros contextos
    for k in CONTEXTOS:
        if k != "contexto_3":
            assert c._pesos[k] == c._prior[k]
    # nao conhece as regras: com energia baixa nao dorme por regra (dormir e candidato com peso 1.0, nao certeza)
    obs2 = Observacao(vetor_estado=(0.8, 0.9, 0.1, 0.6, 1.0, 0.0, 0.0, 0.5), ticks_desde_cuidado=10, total_cuidados=3)
    acoes = {PoliticaCamadaUnica(cfg_lobos=CONFIG_LOBOS_APRENDIZ).agir(obs2, random.Random(s)) for s in range(200)}
    assert len(acoes) > 1


def test_controle_vida_rejoga_bit_a_bit_e_motivo_sem_regra_nao_cita_fator():
    from digilab.motivo import motivos_de_vida
    from digilab.policies import PoliticaCamadaUnica

    fp = lambda cfg=None: PoliticaCamadaUnica(cfg, CONFIG_LOBOS_APRENDIZ)  # noqa: E731
    vida = simular_vida("atencioso", criar_dono("atencioso"), fp(), 101, DIAS, ORC)
    log = type(vida.motor.log).de_jsonl(vida.motor.log.para_jsonl())
    replay = reproduzir_com_feedback(log, fp, semente=101)
    assert _resumo(replay) == _resumo(vida.motor)
    assert json.dumps(replay.politica.estado_interno(), sort_keys=True) == json.dumps(vida.motor.politica.estado_interno(), sort_keys=True)
    _, emb = motivos_de_vida(log, fp, 101)
    assert len(emb.motivos) == len(vida.motor.acoes_recentes(10**9))
    lobos = Counter(d["lobo"] for d in emb.diagnosticos)
    assert set(lobos) <= {"prior", "decisao"} and lobos["prior"] > 0
    for m, d in zip(emb.motivos, emb.diagnosticos):
        if d["lobo"] == "prior":
            assert m.fatores == ()
        assert d["valor_decidiu"] == (d["lobo"] == "decisao")


def test_acoplado_so_cuidado_mesmos_ticks_sem_sinais():
    sys.path.insert(0, str(RAIZ / "experiments"))
    from run_v2_l1 import log_so_cuidado

    fp = lambda cfg=None: PoliticaLobos(cfg, CONFIG_LOBOS_APRENDIZ)  # noqa: E731
    vida = simular_vida("atencioso", criar_dono("atencioso"), fp(), 202, DIAS, ORC)
    log = log_so_cuidado(vida.motor.log)
    sinais = {AcaoUsuario.ELOGIAR.value, AcaoUsuario.REPREENDER.value}
    assert not any(e.tipo == "acao_usuario" and str(e.valor) in sinais for e in log)
    cuidados_origem = [(e.tick, str(e.valor)) for e in vida.motor.log if e.tipo == "acao_usuario" and str(e.valor) not in sinais]
    assert [(e.tick, str(e.valor)) for e in log if e.tipo == "acao_usuario"] == cuidados_origem
    assert [e for e in log if e.tipo == "avanco"] == [e for e in vida.motor.log if e.tipo == "avanco"]
    m = reproduzir_com_feedback(log, fp, semente=202)
    rec = m.politica.estado_interno()["aprendizado"]["recompensas"]
    assert rec["elogio"] == 0 and rec["repreensao"] == 0 and rec["latencia"] + rec["ignorado"] > 0
    assert m.estado()["tick"] == vida.motor.estado()["tick"]
    sem = log_so_cuidado(vida.motor.log, sem_carinho=True)
    assert not any(e.tipo == "acao_usuario" and str(e.valor) == AcaoUsuario.ACARICIAR.value for e in sem)


def test_metricas_tarefa_e_norma_de_reacao():
    from digilab.config import CONFIG_DONOS
    from digilab.donos import julgar_acao
    from digilab.metrics import acerto_na_tarefa, eficiencia_amostral, norma_de_reacao

    julgar = lambda e, a: julgar_acao({**e, "acao_atual": a}, CONFIG_DONOS)  # noqa: E731
    cansado = {"fome": 0.8, "higiene": 0.8, "energia": 0.1, "tick_do_dia": 600}
    decisoes = [(0, cansado, "dormir"), (15, cansado, "brincar"), (1440, cansado, "dormir"), (1455, cansado, "ocioso")]
    c = acerto_na_tarefa(decisoes, julgar, [a.value for a in AcaoPet], 1440)
    assert c["dias"] == [0, 1] and c["acerto"] == [0.5, 0.5] and c["teto"] == [1.0, 1.0] and c["acerto_total"] == 0.5
    e = eficiencia_amostral([0.2, 0.4, 0.6, 0.6], [3, 7, 12, 20], piso=0.2)
    assert e["alvo"] == 0.4 and e["dia"] == 1 and e["sinais"] == 7
    assert eficiencia_amostral([0.2, 0.2], [1, 2], piso=0.2, maximo=0.9)["dia"] is None
    with pytest.raises(ValueError):
        acerto_na_tarefa([], julgar, [], 1440)
    y = {"ensino": {"g1": {"a": 1.0, "b": 2.0, "c": 3.0}, "g2": {"a": 2.0, "b": 3.0, "c": 4.0}},
         "cuidado": {"g1": {"a": 1.0, "b": 1.0, "c": 1.0}, "g2": {"a": 0.0, "b": 2.0, "c": 4.0}}}
    n = norma_de_reacao(y, "ensino", "cuidado")
    assert abs(sum(n["z"].values())) < 1e-12
    assert abs(n["celulas"]["ensino"]["g1"]["alpha"] - 2.0) < 1e-12 and abs(n["celulas"]["cuidado"]["g1"]["beta"]) < 1e-12
    assert n["celulas"]["ensino"]["g1"]["beta"] > 0 and n["celulas"]["cuidado"]["g2"]["beta"] > n["celulas"]["ensino"]["g2"]["beta"]
    assert n["diferenca_por_ovo"]["g1"]["alpha"] == 1.0
    with pytest.raises(ValueError):
        norma_de_reacao({"a": {"g": {"x": 1.0, "y": 1.0}}, "b": {"g": {"x": 1.0, "y": 1.0}}}, "a", "b")
