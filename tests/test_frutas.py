"""V2, N4: as frutas (digilab/frutas.py; docs/PLANO_ANALISE_V2_N4.md, secao 2).

G1: replay pelo log bit a bit (estado, acoes, rngs, frutas no cenario, registros derivados).
G2: (a) MotorFrutas desligado = MotorEducacao numa vida da V3 (educacao, lesoes e sparring), rejogada nos dois;
    (b) desligado com o instinto das frutas = MotorComFeedback com o PoliticaInstinto, nos 4 donos da arena v1;
    (c) ligado sem oferta no log = desligado; (d) a vida da A1 com a bola, pelo MotorFrutas com as frutas desligadas.
Regras: oferecer nao e contato e fica fora do orcamento; sub-decisao de comer pelo incentivo; avaliacao sem a fome e so da
fruta comida; neofobia so antes do primeiro contato; efeito no humor; genoma com rng propria; vocabulario (F2).
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

from digilab.ambiente import MotorAmbiente, fabricas_ambiente, reproduzir_ambiente  # noqa: E402
from digilab.config import (CONFIG_BOLA, CONFIG_EDUCACAO_LIGADA, CONFIG_FRUTAS, CONFIG_FRUTAS_LIGADA,  # noqa: E402
                            CONFIG_LESOES_LIGADA, CONFIG_PADRAO, ConfigBola)
from digilab.donos import criar_dono  # noqa: E402
from digilab.educacao import MotorEducacao, reproduzir_educacao  # noqa: E402
from digilab.events import ACOES_BOLA, ACOES_FRUTAS, ACOES_V1, FRUTAS, AcaoPet, AcaoUsuario, LogDeEventos, oferta_de  # noqa: E402
from digilab.frutas import (REGRA_FRUTA, FrutasSemChave, MotorFrutas, OfertasFrutas, PoliticaInstintoFrutas,  # noqa: E402
                            efeitos_humor, fabricas_frutas, genoma_frutas, reproduzir_frutas, simular_vida_frutas)
from digilab.metrics import comer_por_incentivo, escolha_por_incentivo, saciedade_especifica  # noqa: E402
from digilab.policies.bandit import ACOES as ACOES_BANDIT  # noqa: E402
from digilab.policy import Observacao, PoliticaInstinto  # noqa: E402
from digilab.protocol import frutas_nao_referendados, validar_parametros_frutas  # noqa: E402
from digilab.temperamento import sortear  # noqa: E402
from digilab.treino import MotorComFeedback, simular_vida  # noqa: E402

DONOS = ("atencioso", "relapso", "aleatorio", "incoerente")
SEMENTES = (11, 22, 33)                 # so dos testes: nao sao as de calibracao (10101...) nem de validacao (11101...)
CF = CONFIG_FRUTAS_LIGADA


def _nucleo(m) -> tuple:
    return (m._estado, tuple(m.acoes_recentes(10**9)), m.log.para_jsonl(), m._rng_politica.getstate(),
            m._rng_ambiente.getstate())


def _vida(dono: str, s: int, dias: int = 3, orc: int = 48, cf=CF, ofertas: bool = True):
    fp, fm = fabricas_frutas(cfg_frutas=cf)
    v = simular_vida_frutas(f"{dono}-frutas", criar_dono(dono), fp(), s, dias, orc, fm, OfertasFrutas(cf) if ofertas else None,
                            rotulo_dono=dono)
    return v, fp, fm


def _motor(cf=CF, s: int = 5) -> MotorFrutas:
    fp, fm = fabricas_frutas(cfg_frutas=cf)
    return fm(fp(CONFIG_PADRAO), CONFIG_PADRAO, s)


# ------------------------------------------------------------------ registro, enum e genoma


def test_parametros_registrados_e_nenhum_referendado():
    validar_parametros_frutas()
    assert len(frutas_nao_referendados()) == 13 and CONFIG_FRUTAS.ligada is False


def test_enum_cresce_no_fim_e_a_v1_nao_ve():
    # nas posicoes de quando entraram no fim do enum (17 a 19); depois delas so as de informacao (V2, N5)
    assert list(AcaoUsuario)[17:20] == list(ACOES_FRUTAS) and list(AcaoUsuario)[15:17] == list(ACOES_BOLA)
    assert len(ACOES_V1) == 6 and not set(ACOES_FRUTAS) & set(ACOES_V1)
    assert tuple(ACOES_BANDIT) == tuple(AcaoPet) and len(AcaoPet) == 7


def test_genoma_rng_propria_e_fora_do_temperamento():
    g1, g2 = genoma_frutas(101), genoma_frutas(101)
    assert g1 == g2 and genoma_frutas(202) != g1
    assert 0.0 <= g1.neofobia <= 1.0 and all(0.2 <= x <= 1.0 for x in g1.preferencia_inata.values())
    estado_antes = random.getstate()
    t = sortear(101)
    genoma_frutas(101)
    assert sortear(101) == t and random.getstate() == estado_antes


def test_efeitos_do_mundo():
    g = genoma_frutas(101)
    d = efeitos_humor(g, CF)
    assert d[g.fruta_preferida()] == CF.efeito_humor_ruim and sum(v == CF.efeito_humor_neutro for v in d.values()) == 2
    assert set(efeitos_humor(g, replace(CF, mundo="iguais")).values()) == {CF.efeito_humor_neutro}
    with pytest.raises(ValueError):
        efeitos_humor(g, replace(CF, mundo="mutavel"))


# ------------------------------------------------------------------ G1


@pytest.mark.parametrize("dono", DONOS)
def test_g1_replay_bit_a_bit(dono):
    for s in SEMENTES:
        v, fp, fm = _vida(dono, s)
        r = reproduzir_frutas(LogDeEventos.de_jsonl(v.motor.log.para_jsonl()), fp, semente=s, fabrica_motor=fm)
        assert _nucleo(r) == _nucleo(v.motor)
        assert r.resumo_frutas() == v.motor.resumo_frutas() and r._rng_fruta.getstate() == v.motor._rng_fruta.getstate()
        assert r.estado() == v.motor.estado()


def test_ofertas_fora_do_orcamento_e_o_pet_come():
    v, _, _ = _vida("atencioso", 11)
    assert v.interacoes == 48 and v.ofertas > 0
    n_log = sum(1 for e in v.motor.log if e.tipo == "acao_usuario")
    assert n_log == 48 + v.ofertas
    assert v.motor.contagem_frutas["comidas"] > 0


# ------------------------------------------------------------------ G2


@pytest.mark.parametrize("dono", DONOS)
def test_g2b_desligado_igual_ao_instinto_da_arena_v1(dono):
    for s in SEMENTES:
        a = simular_vida(dono, criar_dono(dono), PoliticaInstinto(), s, 3, 48, rotulo_dono=dono)
        fp, fm = fabricas_frutas(cfg_frutas=CONFIG_FRUTAS)
        b = simular_vida(dono, criar_dono(dono), fp(), s, 3, 48, rotulo_dono=dono, fabrica_motor=fm)
        assert isinstance(b.motor, MotorFrutas) and _nucleo(a.motor) == _nucleo(b.motor)
        assert "frutas" not in b.motor.estado()


@pytest.mark.parametrize("dono", DONOS)
def test_g2c_ligado_sem_oferta_igual_a_desligado(dono):
    for s in SEMENTES:
        a, _, _ = _vida(dono, s, cf=CONFIG_FRUTAS, ofertas=False)
        b, _, _ = _vida(dono, s, cf=CF, ofertas=False)
        assert _nucleo(a.motor) == _nucleo(b.motor)
        assert b.motor.contagem_frutas["oferecidas"] == 0 and b.motor.consumos == []


def test_g2a_desligado_igual_ao_motor_educacao_numa_vida_da_v3():
    import run_educacao as re_
    from digilab.donos_educacao import simular_vida_educacao
    from digilab.evolucao import ovo

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
    fm3 = (lambda politica, cfg, sem: MotorFrutas(politica, cfg, sem, tmp, esp, cfg_bola=CONFIG_BOLA, cfg_frutas=CONFIG_FRUTAS,  # noqa: E731
                                                   cfg_educacao=CONFIG_EDUCACAO_LIGADA, cfg_lesoes=CONFIG_LESOES_LIGADA,
                                                   lutador_do_pet=pet3.lutador, rival_por_nome=re_.rival_por_nome))
    r = reproduzir_frutas(log, fp3, semente=s, fabrica_motor=fm3)
    assert type(r_edu) is MotorEducacao and type(r) is MotorFrutas
    assert r_edu.estado() == r.estado() and r_edu.resumo_educacao() == r.resumo_educacao()
    assert r_edu.historico_lutas == r.historico_lutas and r_edu.vinculo.serie == r.vinculo.serie
    assert _nucleo(r_edu)[:2] == _nucleo(r)[:2]
    for rng in ("_rng_politica", "_rng_ambiente", "_rng_obediencia"):
        assert getattr(r_edu, rng).getstate() == getattr(r, rng).getstate()


def test_g2d_a_vida_da_a1_com_a_bola_pelo_motor_das_frutas():
    """A vida da validacao da A1 (com a bola), gravada em disco, rejogada no MotorAmbiente e no MotorFrutas com as frutas desligadas."""
    caminho = RAIZ / "artifacts_v2_a1" / "validacao" / "ponto" / "vidas" / "atencioso-bola@7101.jsonl"
    log = LogDeEventos.de_jsonl(caminho.read_text(encoding="utf-8"))
    cb = ConfigBola(ligada=True, duracao_min=120, ganho_humor_bola=0.15, w_bola=6.0, bolas_por_dia=4)
    fp_a, fm_a = fabricas_ambiente(cfg_bola=cb)
    a = reproduzir_ambiente(log, fp_a, semente=7101, fabrica_motor=fm_a)
    fp_f, fm_f = fabricas_frutas(cfg_frutas=CONFIG_FRUTAS, cfg_bola=cb)
    f = reproduzir_frutas(log, fp_f, semente=7101, fabrica_motor=fm_f)
    assert type(a) is MotorAmbiente and type(f) is MotorFrutas
    assert a.contagem_bola["usadas"] > 0
    assert _nucleo(a) == _nucleo(f) and a.resumo_bola() == f.resumo_bola() and a.estado() == f.estado()


# ------------------------------------------------------------------ regras


def test_oferta_sem_chave_ou_fora_do_motor_das_frutas_falha_alto():
    with pytest.raises(FrutasSemChave):
        _motor(CONFIG_FRUTAS).observar(AcaoUsuario.OFERECER_FRUTA_A)
    with pytest.raises(ValueError):
        MotorAmbiente(PoliticaInstinto(), CONFIG_PADRAO, 5).observar(AcaoUsuario.OFERECER_FRUTA_A)


def test_oferecer_nao_e_contato_renova_e_expira():
    m = _motor(replace(CF, w_fruta=0.0, duracao_min=30))
    m.avancar(30)
    antes = m._estado
    m.observar(AcaoUsuario.OFERECER_FRUTA_A)
    assert m._estado == antes and m.estado()["frutas"] == {"a": 30}
    m.avancar(10)
    m.observar(AcaoUsuario.OFERECER_FRUTA_A)
    assert m.contagem_frutas["renovadas"] == 1 and m.estado()["frutas"] == {"a": 30}
    m.avancar(60)
    assert m.estado()["frutas"] == {} and m.contagem_frutas["expiradas"] == 1


def test_instinto_com_fruta_consome_a_rng_igual_e_puxa_comer():
    pol = PoliticaInstintoFrutas(CONFIG_PADRAO, CONFIG_BOLA, CF)
    base = Observacao(vetor_estado=(0.8, 0.9, 0.7, 0.5, 1.0, 0.0, 0.0, 0.5), ticks_desde_cuidado=10, total_cuidados=3)
    com = replace(base, fruta=0.8)
    n_com = n_sem = 0
    for i in range(2000):
        r1, r2 = random.Random(i), random.Random(i)
        a_sem = pol.agir(base, r1)
        assert pol.ultima_regra == "tempo_livre" and a_sem is not AcaoPet.COMER
        a_com = pol.agir(com, r2)
        assert pol.ultima_regra == REGRA_FRUTA
        assert r1.getstate() == r2.getstate()
        n_com += a_com is AcaoPet.COMER
    assert n_com > 0
    inst = PoliticaInstinto(CONFIG_PADRAO)
    for i in range(500):
        r1, r2 = random.Random(i), random.Random(i)
        assert pol.agir(base, r1) is inst.agir(base, r2) and r1.getstate() == r2.getstate()


def test_necessidade_vem_antes_da_fruta():
    pol = PoliticaInstintoFrutas(CONFIG_PADRAO, CONFIG_BOLA, CF)
    exausto = Observacao(vetor_estado=(0.8, 0.9, 0.1, 0.5, 1.0, 0.0, 0.0, 0.5), ticks_desde_cuidado=10, total_cuidados=3, fruta=1.0)
    assert pol.agir(exausto, random.Random(1)) is AcaoPet.DORMIR and pol.ultima_regra == "sono_exaustao"


def _comer_forcado(m: MotorFrutas, frutas: tuple, vezes: int = 1) -> None:
    """Poe as frutas e forca decisoes de comer pelo caminho do motor (o mesmo de uma decisao real)."""
    from digilab.policy import Transicao
    for _ in range(vezes):
        for f in frutas:
            m.observar(oferta_de(f))
        m._frutas_na_proxima_decisao()
        obs = Observacao.de_estado(m._estado)
        m._decisao_observada(Transicao(observacao=obs, acao=AcaoPet.COMER, observacao_seguinte=obs))


def test_avaliacao_cai_com_o_consumo_recente_da_fruta_e_nao_com_a_fome():
    """H-HED-03: mesma fome, consumo recente diferente de a: a avaliacao de a difere; a das outras nao muda."""
    cf = replace(CF, k_saciedade=0.5)
    m1, m2 = _motor(cf, 7), _motor(cf, 7)
    _comer_forcado(m2, ("a",), vezes=2)               # m2 comeu a duas vezes antes
    for m in (m1, m2):
        m._estado = replace(m._estado, fome=0.6)
        m.cenario.clear()
    _comer_forcado(m1, ("a",))
    _comer_forcado(m2, ("a",))
    c1, c2 = m1.consumos[-1], m2.consumos[-1]
    assert c1["fome_antes"] == c2["fome_antes"] == 0.6
    assert c2["avaliacao"] < c1["avaliacao"] == m1.genoma.preferencia_inata["a"]
    assert m2.avaliacao["b"] == m1.avaliacao["b"] == m1.genoma.preferencia_inata["b"]
    # a fome nao entra: com outra fome, a mesma avaliacao
    m3 = _motor(cf, 7)
    m3._estado = replace(m3._estado, fome=0.2)
    _comer_forcado(m3, ("a",))
    assert m3.consumos[-1]["avaliacao"] == c1["avaliacao"]


def test_consumo_recente_decai_e_a_avaliacao_volta():
    cf = replace(CF, k_saciedade=0.5, w_fruta=0.0)
    m = _motor(cf, 7)
    _comer_forcado(m, ("a",), vezes=3)
    r = m.consumo_recente["a"]
    m.avancar(15 * 64)                                  # 64 decisoes = 4 meias-vidas
    assert m.consumo_recente["a"] < r / 8


def test_neofobia_so_antes_do_primeiro_contato():
    m = _motor(CF, 9)
    g = m.genoma
    assert m.incentivo["a"] == g.preferencia_inata["a"] * (1.0 - g.neofobia)
    _comer_forcado(m, ("a",))
    c = m.consumos[-1]
    assert m.primeiro_contato["a"] is not None and m.primeiro_contato["b"] is None
    assert c["incentivo_depois"] == c["incentivo_antes"] + CF.taxa_incentivo * (c["avaliacao"] - c["incentivo_antes"])
    assert m.incentivo["b"] == g.preferencia_inata["b"] * (1.0 - g.neofobia)


def test_efeito_no_corpo_separado_do_gosto():
    for s in range(30):
        m = _motor(CF, s)
        m._estado = replace(m._estado, fome=0.5, humor=0.5)
        ruim = m.genoma.fruta_preferida()
        _comer_forcado(m, (ruim,))
        assert m._estado.fome == pytest.approx(0.5 + CF.nutricao, abs=1e-15)
        assert m._estado.humor == pytest.approx(0.5 + CF.efeito_humor_ruim, abs=1e-15)


def test_escolha_proporcional_ao_incentivo_e_rng_sempre_consumida():
    m = _motor(CF, 3)
    m.incentivo = {"a": 0.0, "b": 1.0, "c": 0.0}
    _comer_forcado(m, ("a", "b", "c"))
    assert m.consumos[-1]["fruta"] == "b"
    # comer sem fruta tambem consome a rng_fruta
    m2 = _motor(CF, 3)
    estado = m2._rng_fruta.getstate()
    m2._frutas_na_proxima_decisao()
    from digilab.policy import Transicao
    obs = Observacao.de_estado(m2._estado)
    m2._decisao_observada(Transicao(observacao=obs, acao=AcaoPet.COMER, observacao_seguinte=obs))
    assert m2._rng_fruta.getstate() != estado and m2.contagem_frutas["comer_sem_fruta"] == 1


def test_ofertas_seguem_o_cronograma_e_pulam_o_sono():
    o = OfertasFrutas(CF)
    assert o.acoes({"tick": 541, "dormindo": False}) == []
    assert o.acoes({"tick": 540, "dormindo": True}) == [] and o.k == 0
    assert o.acoes({"tick": 540, "dormindo": False}) == [AcaoUsuario.OFERECER_FRUTA_A]
    assert o.acoes({"tick": 720, "dormindo": False}) == [AcaoUsuario.OFERECER_FRUTA_B, AcaoUsuario.OFERECER_FRUTA_C]
    assert sum(len(x) >= 2 for x in CF.rotacao_ofertas) == 4


def test_vocabulario_operacional():
    """F2: nada nos identificadores ou textos das frutas diz que o pet sente prazer."""
    texto = (RAIZ / "digilab" / "frutas.py").read_text(encoding="utf-8").lower()
    for palavra in ("prazer", "delicia", "gostoso", "saboroso", "adora"):
        assert palavra not in texto, palavra


# ------------------------------------------------------------------ metricas


def test_metricas_das_frutas():
    dec = [("fruta_no_cenario", True, 0.9, "comer"), ("fruta_no_cenario", True, 0.8, "comer"),
           ("fruta_no_cenario", True, 0.2, "ocioso"), ("fruta_no_cenario", True, 0.1, "comer"),
           ("tempo_livre", False, 0.0, "brincar"), ("sono_noite", True, 0.9, "dormir")]
    r = comer_por_incentivo(dec)
    assert r["n"] == 4 and r["p_alto"] == 1.0 and r["p_baixo"] == 0.5 and r["delta"] == 0.5
    assert comer_por_incentivo([])["delta"] is None
    e = escolha_por_incentivo([(["a", "b"], {"a": 0.9, "b": 0.1}, "a"), (["a", "b", "c"], {"a": 0.2, "b": 0.5, "c": 0.1}, "a"),
                               (["a"], {"a": 0.5}, "a"), (["a", "b"], {"a": 0.5, "b": 0.6}, None)])
    assert e["n"] == 2 and e["acerto"] == 0.5 and e["acaso"] == pytest.approx((0.5 + 1 / 3) / 2)
    with pytest.raises(ValueError):
        escolha_por_incentivo([(["a", "b"], {"a": 0.5, "b": 0.6}, "c")])
    s = saciedade_especifica([(1.0 - 0.5 * r, r, f) for r, f in ((0, 0.3), (1, 0.5), (2, 0.4), (0.5, 0.9), (1.5, 0.2))])
    assert s["beta_recente"] == pytest.approx(-0.5) and s["beta_fome"] == pytest.approx(0.0, abs=1e-12)
    with pytest.raises(ValueError):
        saciedade_especifica([(1.0, 0.0, 0.5)])
