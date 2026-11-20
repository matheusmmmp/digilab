"""V2, A1: a bola (digilab/ambiente.py; docs/PLANO_ANALISE_V2_A1.md, secao 2).

G1: replay pelo log bit a bit (estado, acoes, rngs, contadores da bola).
G2: (a) MotorAmbiente desligado = MotorEducacao numa vida da V3 (educacao, lesoes e sparring ligados), rejogada nos dois;
    (b) MotorAmbiente desligado com o instinto da bola = MotorComFeedback com o PoliticaInstinto, nos 4 donos da arena v1;
    (c) chave ligada sem `por_bola` no log = chave desligada.
Regras da bola: por nao e contato, consequencia so em brincar, prazo, renovar, tirar, chave, nenhuma rng a mais.
"""
from __future__ import annotations

import random
import sys
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

from digilab.ambiente import (REGRA_BOLA, BolaSemChave, DonoComBola, MotorAmbiente, PoliticaInstintoBola,  # noqa: E402
                              fabricas_ambiente, reproduzir_ambiente)
from digilab.config import CONFIG_BOLA, CONFIG_BOLA_LIGADA, CONFIG_EDUCACAO_LIGADA, CONFIG_LESOES_LIGADA, CONFIG_PADRAO  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.educacao import MotorEducacao, reproduzir_educacao  # noqa: E402
from digilab.events import ACOES_PET_HOJE, ACOES_V1, AcaoPet, AcaoUsuario, LogDeEventos, acao_usuario, avanco  # noqa: E402
from digilab.metrics import privacao_nas_decisoes, resposta_a_bola  # noqa: E402
from digilab.policies.bandit import ACOES as ACOES_BANDIT  # noqa: E402
from digilab.policy import Observacao, PoliticaInstinto  # noqa: E402
from digilab.protocol import bola_nao_referendados, validar_parametros_bola  # noqa: E402
from digilab.treino import MotorComFeedback, simular_vida  # noqa: E402

DONOS = ("atencioso", "relapso", "aleatorio", "incoerente")
SEMENTES = (11, 22, 33)                 # so dos testes: nao sao as de calibracao (6101...) nem de validacao (7101...)


def _nucleo(m) -> tuple:
    """o que precisa ser igual byte a byte: estado da camada 1, acoes do pet, log e as rngs do motor"""
    return (m._estado, tuple(m.acoes_recentes(10**9)), m.log.para_jsonl(), m._rng_politica.getstate(),
            m._rng_ambiente.getstate())


def _vida_bola(dono: str, s: int, dias: int = 3, orc: int = 48, cb=CONFIG_BOLA_LIGADA):
    fp, fm = fabricas_ambiente(cfg_bola=cb)
    return simular_vida(f"{dono}-bola", DonoComBola(dono, cb), fp(), s, dias, orc, rotulo_dono=dono, fabrica_motor=fm), fp, fm


# ------------------------------------------------------------------ registro e canonica


def test_parametros_registrados_e_nenhum_referendado():
    validar_parametros_bola()
    assert set(bola_nao_referendados()) == {"ConfigBola.duracao_min", "ConfigBola.ganho_humor_bola", "ConfigBola.w_bola",
                                            "ConfigBola.bolas_por_dia"}
    assert CONFIG_BOLA.ligada is False


def test_enum_do_dono_cresce_no_fim_e_a_v1_nao_ve():
    # nas posicoes de quando entraram no fim do enum (15 e 16); depois delas so as ofertas de fruta (V2, N4)
    assert list(AcaoUsuario)[15:17] == [AcaoUsuario.POR_BOLA, AcaoUsuario.TIRAR_BOLA]
    assert len(ACOES_V1) == 6 and AcaoUsuario.POR_BOLA not in ACOES_V1
    assert tuple(ACOES_BANDIT) == ACOES_PET_HOJE and len(ACOES_PET_HOJE) == 7      # o bandit usa AcaoPet, que nao mudou


def test_observacao_da_v1_nao_tem_bola():
    from digilab.state import Estado
    assert Observacao.de_estado(Estado()).bola == 0.0


# ------------------------------------------------------------------ G1: replay


@pytest.mark.parametrize("dono", DONOS)
def test_g1_replay_bit_a_bit(dono):
    for s in SEMENTES:
        v, fp, fm = _vida_bola(dono, s)
        r = reproduzir_ambiente(LogDeEventos.de_jsonl(v.motor.log.para_jsonl()), fp, semente=s, fabrica_motor=fm)
        assert _nucleo(r) == _nucleo(v.motor)
        assert r.resumo_bola() == v.motor.resumo_bola()
        assert r.estado() == v.motor.estado()


def test_g1_os_donos_coerentes_poem_e_o_pet_usa():
    v, _, _ = _vida_bola("atencioso", 11)
    c = v.motor.contagem_bola
    assert c["postas"] > 0 and c["usadas"] > 0 and c["decisoes_com_bola"] >= c["usadas"]
    assert v.interacoes == 48                                     # a bola cabe no orcamento de sempre


# ------------------------------------------------------------------ G2: equivalencia


@pytest.mark.parametrize("dono", DONOS)
def test_g2b_desligado_igual_ao_instinto_da_arena_v1(dono):
    for s in SEMENTES:
        a = simular_vida(dono, criar_dono(dono), PoliticaInstinto(), s, 3, 48, rotulo_dono=dono)
        fp, fm = fabricas_ambiente(cfg_bola=CONFIG_BOLA)
        b = simular_vida(dono, criar_dono(dono), fp(), s, 3, 48, rotulo_dono=dono, fabrica_motor=fm)
        assert isinstance(b.motor, MotorAmbiente) and isinstance(a.motor, MotorComFeedback)
        assert _nucleo(a.motor) == _nucleo(b.motor)


@pytest.mark.parametrize("dono", DONOS)
def test_g2c_ligada_sem_bola_no_log_igual_a_desligada(dono):
    for s in SEMENTES:
        fp0, fm0 = fabricas_ambiente(cfg_bola=CONFIG_BOLA)
        fp1, fm1 = fabricas_ambiente(cfg_bola=CONFIG_BOLA_LIGADA)
        a = simular_vida(dono, criar_dono(dono), fp0(), s, 3, 48, rotulo_dono=dono, fabrica_motor=fm0)
        b = simular_vida(dono, criar_dono(dono), fp1(), s, 3, 48, rotulo_dono=dono, fabrica_motor=fm1)
        assert _nucleo(a.motor) == _nucleo(b.motor)
        assert b.motor.contagem_bola["postas"] == 0 and b.motor.estado()["bola"] is None


def test_g2a_desligado_igual_ao_motor_educacao_numa_vida_da_v3():
    """Uma vida da V3 (educacao, lesoes e sparring ligados, bandit da personalidade), rejogada no MotorEducacao e no
    MotorAmbiente desligado, com as mesmas fabricas: tudo igual, inclusive lutas, educacao e vinculo."""
    import run_educacao as re_
    from digilab.donos_educacao import simular_vida_educacao
    from digilab.evolucao import ovo
    from digilab.temperamento import sortear

    b, s, dias = "atencioso", 70001, 3
    esp, temp_ovo = ovo(s)
    tmp = sortear(s)
    fp, fm_base, fm, pet = re_._fabricas(b, s, esp, tmp, temp_ovo)
    v = simular_vida_educacao(b, s, dias, esp, tmp, cl=CONFIG_LESOES_LIGADA, sparring=re_.ticks_sparring(b),
                              rival_sparring=pet.rival, lutador_do_pet=pet.lutador, rival_por_nome=re_.rival_por_nome)
    log = LogDeEventos.de_jsonl(v.motor.log.para_jsonl())
    assert any(e.tipo == "luta" for e in log)
    fp2, _, fm2, _ = re_._fabricas(b, s, esp, tmp, temp_ovo)
    r_edu = reproduzir_educacao(log, fp2, semente=s, fabrica_motor=fm2)
    fp3, _, _, pet3 = re_._fabricas(b, s, esp, tmp, temp_ovo)
    fm3 = (lambda politica, cfg, sem: MotorAmbiente(politica, cfg, sem, tmp, esp, cfg_bola=CONFIG_BOLA,  # noqa: E731
                                                     cfg_educacao=CONFIG_EDUCACAO_LIGADA, cfg_lesoes=CONFIG_LESOES_LIGADA,
                                                     lutador_do_pet=pet3.lutador, rival_por_nome=re_.rival_por_nome))
    r_amb = reproduzir_ambiente(log, fp3, semente=s, fabrica_motor=fm3)
    assert type(r_edu) is MotorEducacao and type(r_amb) is MotorAmbiente
    assert r_edu.estado() == r_amb.estado()
    assert r_edu.resumo_educacao() == r_amb.resumo_educacao()
    assert r_edu.historico_lutas == r_amb.historico_lutas
    assert r_edu.vinculo.serie == r_amb.vinculo.serie and r_edu.transicoes == r_amb.transicoes
    assert _nucleo(r_edu)[:2] == _nucleo(r_amb)[:2]
    assert r_edu._rng_politica.getstate() == r_amb._rng_politica.getstate()
    assert r_edu._rng_ambiente.getstate() == r_amb._rng_ambiente.getstate()
    assert r_edu._rng_obediencia.getstate() == r_amb._rng_obediencia.getstate()


# ------------------------------------------------------------------ regras da bola


def _motor(cb=CONFIG_BOLA_LIGADA, s: int = 5) -> MotorAmbiente:
    fp, fm = fabricas_ambiente(cfg_bola=cb)
    return fm(fp(CONFIG_PADRAO), CONFIG_PADRAO, s)


def test_acao_da_bola_sem_chave_ou_fora_do_motor_ambiente_falha_alto():
    m = _motor(CONFIG_BOLA)
    with pytest.raises(BolaSemChave):
        m.observar(AcaoUsuario.POR_BOLA)
    e = MotorEducacao(PoliticaInstintoBola(), CONFIG_PADRAO, 5)
    with pytest.raises(ValueError):
        e.observar(AcaoUsuario.POR_BOLA)


def test_por_a_bola_nao_e_contato():
    m = _motor()
    m.avancar(30)
    antes = m._estado
    m.observar(AcaoUsuario.POR_BOLA)
    assert m._estado == antes                                       # nem tempo sem cuidado, nem total de cuidados
    assert m.estado()["bola"]["prazo"] == antes.tick + CONFIG_BOLA_LIGADA.duracao_min


def test_renovar_tirar_e_prazo():
    cb = replace(CONFIG_BOLA_LIGADA, w_bola=0.0)                   # o pet quase nunca usa: o prazo decide
    m = _motor(cb)
    m.observar(AcaoUsuario.POR_BOLA)
    m.avancar(10)
    m.observar(AcaoUsuario.POR_BOLA)
    assert m.contagem_bola["renovadas"] == 1 and m.estado()["bola"]["prazo"] == 10 + cb.duracao_min
    m.observar(AcaoUsuario.TIRAR_BOLA)
    assert m.estado()["bola"] is None and m.contagem_bola["tiradas"] == 1
    with pytest.raises(ValueError):
        m.observar(AcaoUsuario.TIRAR_BOLA)


def test_bola_expira_no_prazo_se_ninguem_usa():
    cb = replace(CONFIG_BOLA_LIGADA, w_bola=0.0, duracao_min=30)
    for s in range(40):
        m = _motor(cb, s)
        m.avancar(1)
        m.observar(AcaoUsuario.POR_BOLA)
        m.avancar(60)
        c = m.contagem_bola
        assert c["postas"] == 1 and c["usadas"] + c["expiradas"] == 1 and m.estado()["bola"] is None


def test_consequencia_so_em_brincar_e_a_bola_some():
    """Com a bola no cenario: brincar = humor do brincar de sempre + ganho, e a bola some; outra acao a deixa la."""
    usou = ignorou = 0
    for s in range(60):
        m = _motor(s=s)
        m.avancar(1)
        m.observar(AcaoUsuario.POR_BOLA)
        humor_antes = m._estado.humor
        m.avancar(15)                                               # a decisao do tick 15 ve a bola
        hist = m.acoes_recentes(1)[-1][1]
        if hist is AcaoPet.BRINCAR:
            usou += 1
            assert m.contagem_bola["usadas"] == 1 and m.estado()["bola"] is None
            assert m._estado.humor > humor_antes
        else:
            ignorou += 1
            assert m.contagem_bola["ignoradas"] == 1 and m.estado()["bola"] is not None
    assert usou > 0 and ignorou > 0


def test_ganho_de_humor_e_exatamente_o_parametro():
    """A mesma decisao com ganho 0 e com ganho g: o humor difere de g (cortado em 1,0)."""
    for s in range(60):
        hs = []
        for g in (0.0, 0.15):
            m = _motor(replace(CONFIG_BOLA_LIGADA, ganho_humor_bola=g), s)
            m._estado = replace(m._estado, humor=0.2)
            m.observar(AcaoUsuario.POR_BOLA)
            m.avancar(1)
            hs.append((m.acoes_recentes(1)[-1][1], m._estado.humor))
        if hs[0][0] is AcaoPet.BRINCAR:
            assert hs[1][1] == pytest.approx(min(1.0, hs[0][1] + 0.15), abs=1e-15)
            return
    pytest.fail("nenhuma semente brincou na primeira decisao")


def test_instinto_com_bola_consome_a_rng_igual_e_puxa_brincar():
    pol = PoliticaInstintoBola(CONFIG_PADRAO, CONFIG_BOLA_LIGADA)
    base = Observacao(vetor_estado=(0.8, 0.9, 0.7, 0.5, 1.0, 0.0, 0.0, 0.5), ticks_desde_cuidado=10, total_cuidados=3)
    com = replace(base, bola=1.0)
    n_com = n_sem = 0
    for i in range(2000):
        r1, r2 = random.Random(i), random.Random(i)
        a_sem = pol.agir(base, r1)
        assert pol.ultima_regra == "tempo_livre"
        a_com = pol.agir(com, r2)
        assert pol.ultima_regra == REGRA_BOLA
        assert r1.getstate() == r2.getstate()                     # uma chamada de rng nos dois casos
        n_sem += a_sem is AcaoPet.BRINCAR
        n_com += a_com is AcaoPet.BRINCAR
    assert n_com > n_sem
    # sem bola, o instinto da bola e o instinto da v1, decisao a decisao
    inst = PoliticaInstinto(CONFIG_PADRAO)
    for i in range(500):
        r1, r2 = random.Random(i), random.Random(i)
        assert pol.agir(base, r1) is inst.agir(base, r2) and r1.getstate() == r2.getstate()


def test_necessidade_vem_antes_da_bola():
    pol = PoliticaInstintoBola(CONFIG_PADRAO, CONFIG_BOLA_LIGADA)
    exausto = Observacao(vetor_estado=(0.8, 0.9, 0.1, 0.5, 1.0, 0.0, 0.0, 0.5), ticks_desde_cuidado=10, total_cuidados=3, bola=1.0)
    assert pol.agir(exausto, random.Random(1)) is AcaoPet.DORMIR and pol.ultima_regra == "sono_exaustao"


# ------------------------------------------------------------------ metricas


def test_resposta_a_bola_e_privacao():
    dec = [(0, True, "bola_no_cenario", "brincar"), (15, True, "bola_no_cenario", "ocioso"),
           (30, False, "tempo_livre", "brincar"), (45, False, "tempo_livre", "explorar"), (60, False, "tempo_livre", "ocioso"),
           (75, True, "sono_exaustao", "dormir")]
    r = resposta_a_bola(dec)
    assert r["p_com_bola"] == 0.5 and r["p_sem_bola"] == pytest.approx(1 / 3) and r["n_com_bola"] == 3
    assert r["delta"] == pytest.approx(0.5 - 1 / 3)
    assert resposta_a_bola([(0, False, "tempo_livre", "brincar")])["delta"] is None
    p = privacao_nas_decisoes([(0, 0.1, 0.9, 0.9, 0.5), (15, 0.5, 0.5, 0.5, 0.7)], 0.15)
    assert p["fracao_privacao"] == 0.5 and p["humor_medio"] == pytest.approx(0.6)
    with pytest.raises(ValueError):
        privacao_nas_decisoes([], 0.15)
