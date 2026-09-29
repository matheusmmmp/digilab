"""educacao-v1, Fase 2 parte 1: configs, acoes novas e MotorEducacao vazio (docs/DESIGN_EDUCACAO_HERANCA_LESOES.md)."""
from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from digilab.config import CONFIG_EDUCACAO, CONFIG_LESOES  # noqa: E402
from digilab.educacao import MotorEducacao, fabricas_educacao  # noqa: E402
from digilab.events import ACOES_EDUCACAO, ACOES_TREINO, ACOES_V1, AcaoUsuario  # noqa: E402
from digilab.evolucao import ovo  # noqa: E402
from digilab.protocol import (PARAMETROS_EDUCACAO_V1, Campo, Status, hash_parametros_educacao,  # noqa: E402
                              validar_parametros_educacao)
from digilab.temperamento import sortear  # noqa: E402
from digilab.treino import reproduzir_com_feedback  # noqa: E402
from digilab.treino_vida import MotorTreino, simular_vida_treino  # noqa: E402


def _vida(braco: str, s: int = 3101, dias: int = 3):
    esp, _ = ovo(s)
    t = sortear(s)
    return simular_vida_treino(braco, s, dias, esp, t), esp, t


def test_acoes_novas_nao_mexem_nas_listas_antigas():
    assert [a.value for a in ACOES_V1] == ["alimentar", "limpar", "brincar", "acariciar", "elogiar", "repreender"]
    assert all(a.value.startswith("treinar_") for a in ACOES_TREINO) and len(ACOES_TREINO) == 6
    assert set(ACOES_EDUCACAO).isdisjoint(ACOES_V1) and set(ACOES_EDUCACAO).isdisjoint(ACOES_TREINO)
    assert list(AcaoUsuario)[-3:] == list(ACOES_EDUCACAO)      # no fim do enum


@pytest.mark.parametrize("braco", ["exigente", "aleatorio", "atencioso"])
def test_log_sem_acao_nova_rejoga_igual_ao_motor_treino(braco):
    v, esp, t = _vida(braco)
    fp, fm = fabricas_educacao(3101, esp, t)
    r = reproduzir_com_feedback(v.motor.log, fp, semente=3101, fabrica_motor=fm)
    assert isinstance(r, MotorEducacao)
    e_r, e_m = r.estado(), v.motor.estado()
    assert e_r.pop("educacao") == {"disciplina": 0, "lesionado": False, "janela": None}
    assert e_r == e_m
    assert r.resumo_treino() == v.motor.resumo_treino() and r.vinculo.serie == v.motor.vinculo.serie


@pytest.mark.parametrize("acao", ACOES_EDUCACAO)
def test_acao_nova_no_motor_antigo_falha_alto(acao):
    esp, _ = ovo(3101)
    fp, _ = fabricas_educacao(3101, esp, sortear(3101))
    antigo = MotorTreino(fp(None), None, 3101, sortear(3101), esp)
    with pytest.raises(Exception):
        antigo._aplicar_acao_usuario(acao)


def test_parametros_registrados_com_status_e_fonte():
    validar_parametros_educacao()
    for nome, c in PARAMETROS_EDUCACAO_V1.items():
        assert c.justificativa, nome
    propostos = {n for n, c in PARAMETROS_EDUCACAO_V1.items() if c.status is Status.PROPOSTO}
    assert "ConfigLesoes.limiar_taxa_vitoria" in propostos and "ConfigEducacao.janela_min" not in propostos
    assert PARAMETROS_EDUCACAO_V1["ConfigEducacao.passo_disciplina"].valor == CONFIG_EDUCACAO.passo_disciplina
    assert PARAMETROS_EDUCACAO_V1["ConfigLesoes.lesoes_para_morte"].valor == CONFIG_LESOES.lesoes_para_morte


def test_registro_divergente_de_config_falha_alto():
    ruim = dict(PARAMETROS_EDUCACAO_V1)
    c = ruim["ConfigEducacao.passo_disciplina"]
    ruim["ConfigEducacao.passo_disciplina"] = Campo(c.valor + 1, c.status, c.justificativa)
    with pytest.raises(ValueError):
        validar_parametros_educacao(ruim)
    del ruim["ConfigEducacao.passo_disciplina"]
    with pytest.raises(ValueError):
        validar_parametros_educacao(ruim)


def test_hash_estavel_e_sensivel():
    h = hash_parametros_educacao()
    assert h == hash_parametros_educacao() and len(h) == 64
    outro = dict(PARAMETROS_EDUCACAO_V1)
    c = outro["ConfigHeranca.sigma_temperamento"]
    outro["ConfigHeranca.sigma_temperamento"] = replace(c, status=Status.DECIDIDO)
    assert hash_parametros_educacao(outro) != h


# ================================================================ parte 2: chamado falso, disciplina, permissivo
from digilab.config import CONFIG_EDUCACAO_LIGADA, CONFIG_EVOLUCAO_PESQUISA  # noqa: E402
from digilab.donos_educacao import BRACOS_EDUCACAO, simular_vida_educacao  # noqa: E402

S_EDU = 4201


def _vida_edu(braco: str, s: int = S_EDU, dias: int = 3):
    esp, _ = ovo(s)
    t = sortear(s)
    return simular_vida_educacao(braco, s, dias, esp, t), esp, t


@pytest.fixture(scope="module")
def vidas_edu():
    return {b: _vida_edu(b) for b in BRACOS_EDUCACAO}


def _motor_ligado(s: int = S_EDU):
    esp, _ = ovo(s)
    fp, fm = fabricas_educacao(s, esp, sortear(s), ce=CONFIG_EDUCACAO_LIGADA)
    return fm(fp(None), None, s)


def test_replay_bit_a_bit_com_educacao_ligada(vidas_edu):
    for b in ("atencioso", "permissivo", "incoerente"):
        v, esp, t = vidas_edu[b]
        fp, fm = fabricas_educacao(S_EDU, esp, t, ce=CONFIG_EDUCACAO_LIGADA)
        r = reproduzir_com_feedback(v.motor.log, fp, semente=S_EDU, fabrica_motor=fm)
        assert r.estado() == v.motor.estado()
        assert r.resumo_educacao() == v.motor.resumo_educacao()
        assert r.historico_janelas == v.motor.historico_janelas
        assert r.vinculo.serie == v.motor.vinculo.serie


def test_orcamento_igual_e_mesmos_sorteios_de_travessura_entre_bracos(vidas_edu):
    gastos = {b: v.interacoes for b, (v, _, _) in vidas_edu.items()}
    assert len(set(gastos.values())) == 1, gastos
    estados = {b: v.motor._rng_travessura.getstate() for b, (v, _, _) in vidas_edu.items()}
    assert len(set(map(str, estados.values()))) == 1


def test_chamados_so_da_crianca_em_diante(vidas_edu):
    for v, _, _ in vidas_edu.values():
        assert v.motor.historico_janelas
        assert min(j["inicio"] for j in v.motor.historico_janelas) >= CONFIG_EVOLUCAO_PESQUISA.dur_bebe_min


def test_permissivo_cede_e_nao_educa_atencioso_corrige(vidas_edu):
    at = vidas_edu["atencioso"][0].motor.resumo_educacao()
    pe = vidas_edu["permissivo"][0].motor.resumo_educacao()
    assert pe["contagem"]["falsos_cedidos"] > 0 and pe["contagem"]["falsos_corrigidos"] == 0 and pe["disciplina"] == 0
    assert at["contagem"]["falsos_corrigidos"] > 0 and at["contagem"]["falsos_cedidos"] == 0
    assert at["disciplina"] > pe["disciplina"]
    assert pe["contagem"]["falsos"] > at["contagem"]["falsos"]          # ceder reforca o chamado falso
    assert vidas_edu["permissivo"][0].dono.respostas["bronca"] == 0


def test_fracao_falso_zera_com_disciplina_cheia_ou_aprendizado():
    m = _motor_ligado()
    c = CONFIG_EDUCACAO_LIGADA
    assert m.fracao_falso() == c.fracao_falso_base
    m.petiscos_cedidos = 100
    assert m.fracao_falso() == c.teto_falso
    m.disciplina = c.disciplina_max
    assert m.fracao_falso() == 0.0
    m.disciplina, m.acertos = 0, c.acertos_para_aprender
    assert m.fracao_falso() == 0.0


def _abrir_falso(m, tick_rel: int = 0):
    t = m._estado.tick + tick_rel
    m.janela = {"tipo": "chamado", "pedido": "fome", "inicio": t, "prazo": t + CONFIG_EDUCACAO_LIGADA.janela_min,
                "falso": True}


def test_falso_ignorado_derruba_disciplina_e_o_pet_nao_resolve_sozinho():
    m = _motor_ligado()
    m.disciplina = 50
    _abrir_falso(m)
    m.avancar(CONFIG_EDUCACAO_LIGADA.janela_min + 16)   # proxima decisao depois do prazo
    assert m.janela is None or m.janela["inicio"] > 0
    assert m.historico_janelas[0]["desfecho"] == "ignorado"
    assert m.disciplina == 50 - CONFIG_EDUCACAO_LIGADA.passo_disciplina


def test_bronca_certa_petisco_e_refeicao_recusada():
    m = _motor_ligado()
    _abrir_falso(m)
    fome = m._estado.fome
    m.observar(AcaoUsuario.ALIMENTAR)
    assert m._estado.fome == fome and m.janela is not None and m.contagem["refeicoes_recusadas"] == 1
    m.observar(AcaoUsuario.REPREENDER)
    assert m.janela is None and m.disciplina == CONFIG_EDUCACAO_LIGADA.passo_disciplina and m.acertos == 1
    _abrir_falso(m)
    m.observar(AcaoUsuario.PETISCO)
    assert m.janela is None and m.petiscos_cedidos == 1 and m.acertos == 0 and m._estado.fome > fome


def test_refeicao_recusada_consome_a_rng_de_ambiente_como_aceita():
    a, b = _motor_ligado(), _motor_ligado()
    _abrir_falso(a)
    a.observar(AcaoUsuario.ALIMENTAR)
    b._estado = replace(b._estado)
    from digilab.state import aplicar_acao_usuario
    aplicar_acao_usuario(b._estado, AcaoUsuario.ALIMENTAR, b.cfg, b._rng_ambiente)
    assert a._rng_ambiente.getstate() == b._rng_ambiente.getstate()


def test_disciplina_cai_para_metade_ao_evoluir():
    m = _motor_ligado()
    m.disciplina, m.acertos = 75, 2
    m._evoluiu("adolescente", 900)
    assert m.disciplina == 37 and m.acertos == 0


# ================================================================ parte 3: aviso, mau humor, resolvem sozinhas
def _abrir(m, tipo: str, pedido: str, falso: bool = False):
    t = m._estado.tick
    m.janela = {"tipo": tipo, "pedido": pedido, "inicio": t, "prazo": t + CONFIG_EDUCACAO_LIGADA.janela_min,
                "falso": falso}


def test_aviso_atendido_nao_suja_e_ignorado_suja():
    m = _motor_ligado()
    _abrir(m, "aviso", "banheiro")
    m.observar(AcaoUsuario.LEVAR_AO_BANHEIRO)
    assert m.janela is None and m.contagem["avisos_atendidos"] == 1
    assert m.disciplina == CONFIG_EDUCACAO_LIGADA.disciplina_por_banheiro
    _abrir(m, "aviso", "banheiro")
    antes = m._estado.sujeira
    m._expirar(m._estado.tick + CONFIG_EDUCACAO_LIGADA.janela_min + 1)
    assert m._estado.sujeira == min(m.cfg.sujeira_maxima, antes + 1) and m.contagem["avisos_ignorados"] == 1


def test_mau_humor_elogio_resolve_e_bronca_sem_motivo_derruba_vinculo():
    m = _motor_ligado()
    _abrir(m, "chamado", "carinho")
    m.observar(AcaoUsuario.ELOGIAR)
    assert m.janela is None and m.contagem["reais_atendidos"] == 1
    _abrir(m, "chamado", "carinho")
    v = m.vinculo.valor
    m.observar(AcaoUsuario.REPREENDER)
    assert m.contagem["broncas_sem_motivo"] == 1 and m.janela is not None
    assert m.vinculo.valor < v and m.vinculo.serie[-1][2] == "bronca_sem_motivo"


def test_acordar_dormindo_custa_humor():
    m = _motor_ligado()
    m._estado = replace(m._estado, dormindo=True, humor=0.8)
    m.observar(AcaoUsuario.BRINCAR)
    assert not m._estado.dormindo and m.contagem["acordado"] == 1


def test_superalimentacao_custa_saude_e_recusa_nao_conta():
    m = _motor_ligado()
    m._estado = replace(m._estado, fome=0.95, saude=0.9)
    m.observar(AcaoUsuario.PETISCO)
    assert m.contagem["superalimentacao"] == 1
    assert m._estado.saude == pytest.approx(0.9 - CONFIG_EDUCACAO_LIGADA.custo_saude_superalimentacao)
    _abrir_falso(m)
    m.observar(AcaoUsuario.ALIMENTAR)                  # recusada: nao come, nao faz mal
    assert m.contagem["superalimentacao"] == 1


def test_desligada_nada_de_travessura_nem_consequencia():
    esp, _ = ovo(S_EDU)
    fp, fm = fabricas_educacao(S_EDU, esp, sortear(S_EDU))
    m = fm(fp(None), None, S_EDU)
    m._estado = replace(m._estado, dormindo=True, fome=0.95)
    m.observar(AcaoUsuario.BRINCAR)
    m.observar(AcaoUsuario.PETISCO)
    m.avancar(3 * 24 * 60)
    assert m.historico_janelas == [] and all(v == 0 for v in m.contagem.values())


# ================================================================ parte 4: lutas, lesoes e evolucao por vitorias
from digilab.combate_v2.v21.bots import lutador_adulto  # noqa: E402
from digilab.config import CONFIG_LESOES_LIGADA  # noqa: E402
from digilab.educacao import PetMorto, reproduzir_educacao  # noqa: E402
from digilab.events import ler_luta  # noqa: E402


def _fabricas_luta(s: int = S_EDU, cl=CONFIG_LESOES_LIGADA, forma: str = "duelista"):
    esp, _ = ovo(s)
    return fabricas_educacao(s, esp, sortear(s), ce=CONFIG_EDUCACAO_LIGADA, cl=cl,
                             lutador_do_pet=lambda m: lutador_adulto(forma, esp)), esp


def test_luta_exige_chave_e_lutador():
    m = _motor_ligado()
    with pytest.raises(ValueError):
        m.lutar("npc:tier1_brutamontes", 1)
    esp, _ = ovo(S_EDU)
    fp, fm = fabricas_educacao(S_EDU, esp, sortear(S_EDU), cl=CONFIG_LESOES_LIGADA)
    with pytest.raises(ValueError):
        fm(fp(None), None, S_EDU).lutar("npc:tier1_brutamontes", 1)


def test_lutas_no_log_rejogam_bit_a_bit_e_replay_antigo_recusa():
    (fp, fm), _ = _fabricas_luta()
    m = fm(fp(None), None, S_EDU)
    for i in range(6):
        m.avancar(60)
        m.lutar("npc:tier2_sentinela" if i % 2 else "bot:furioso@brasa", 9000 + i)
        m.observar(AcaoUsuario.TRATAR_LESAO)
    lutas = [e for e in m.log if e.tipo == "luta"]
    assert [ler_luta(e) for e in lutas] == [(h["rival"], h["semente"]) for h in m.historico_lutas]
    r = reproduzir_educacao(m.log, fp, semente=S_EDU, fabrica_motor=fm)
    assert r.historico_lutas == m.historico_lutas and r.estado() == m.estado()
    assert r.resumo_educacao() == m.resumo_educacao() and r.vinculo.serie == m.vinculo.serie
    with pytest.raises(ValueError):
        reproduzir_com_feedback(m.log, fp, semente=S_EDU, fabrica_motor=fm)


def test_lesao_depende_so_da_semente_da_luta():
    (fp, fm), _ = _fabricas_luta(cl=replace(CONFIG_LESOES_LIGADA, prob_lesao_derrota=0.5))
    a, b = fm(fp(None), None, S_EDU), fm(fp(None), None, S_EDU)
    b.avancar(300)
    ra = [a.lutar("npc:tier3_soberano", 7000 + i) for i in range(8)]
    rb = [b.lutar("npc:tier3_soberano", 7000 + i) for i in range(8)]
    for x, y in zip(ra, rb):
        if x["resultado"] == y["resultado"] == "derrota":
            assert x["lesao"] == y["lesao"]


def test_lesao_sem_tratar_mata_e_depois_nada_funciona():
    (fp, fm), _ = _fabricas_luta()
    m = fm(fp(None), None, S_EDU)
    m.lesionado_desde = m._estado.tick
    m.avancar(CONFIG_LESOES_LIGADA.horas_sem_tratar_morte * 60 + 15)
    assert m.morte is not None and m.morte["causa"] == "lesao_sem_tratar"
    with pytest.raises(PetMorto):
        m.observar(AcaoUsuario.ALIMENTAR)
    with pytest.raises(PetMorto):
        m.lutar("npc:tier1_brutamontes", 1)


def test_tratar_a_tempo_salva():
    (fp, fm), _ = _fabricas_luta()
    m = fm(fp(None), None, S_EDU)
    m.lesionado_desde = m._estado.tick
    m.avancar(CONFIG_LESOES_LIGADA.horas_sem_tratar_morte * 60 - 30)
    m.observar(AcaoUsuario.TRATAR_LESAO)
    m.avancar(12 * 60)
    assert m.morte is None and m.lesionado_desde is None      # (contador "tratadas" zera ao evoluir)


def test_lesoes_demais_matam():
    (fp, fm), _ = _fabricas_luta(cl=replace(CONFIG_LESOES_LIGADA, prob_lesao_derrota=1.0, lesoes_para_morte=2),
                                 forma="vigia")
    m = fm(fp(None), None, S_EDU)
    for i in range(60):
        if m.morte:
            break
        m.lutar("npc:tier3_soberano", 100 + i)
    assert m.morte is not None and m.morte["causa"] == "lesoes" and m.lutas["lesoes"] == 2


def test_contadores_zeram_e_qualificacao_gravada_na_passagem_para_adulto():
    (fp, fm), _ = _fabricas_luta()
    m = fm(fp(None), None, S_EDU)
    m.avancar(CONFIG_EVOLUCAO_PESQUISA.dur_bebe_min + CONFIG_EVOLUCAO_PESQUISA.dur_crianca_min + 30)
    assert m.treino.estagio == "adolescente"
    for i in range(CONFIG_LESOES_LIGADA.lutas_minimas_taxa):
        m.lutar("bot:muralha@limo", 500 + i)
        m.observar(AcaoUsuario.TRATAR_LESAO)
        m.avancar(15)
    n, v = m.lutas["lutas"], m.lutas["vitorias"]
    m.avancar(CONFIG_EVOLUCAO_PESQUISA.dur_adolescente_min)
    q = m.transicoes["adulto"]["vitorias"]
    assert q["lutas"] == n == CONFIG_LESOES_LIGADA.lutas_minimas_taxa and q["vitorias"] == v
    assert q["qualifica"] == (v / n >= CONFIG_LESOES_LIGADA.limiar_taxa_vitoria)
    assert m.lutas == m._lutas_zeradas() or m.lutas["lutas"] == 0


# ================================================================ parte 5: heranca e evento origem
from digilab.config import CONFIG_HERANCA  # noqa: E402
from digilab.educacao import fabricas_filho  # noqa: E402
from digilab.heranca import HerancaInvalida, conferir_pais, cruzar, genitor, ler_origem  # noqa: E402
from digilab.temperamento import EIXOS  # noqa: E402


@pytest.fixture(scope="module")
def pais():
    out = []
    for s, b in ((5101, "atencioso"), (5202, "permissivo")):
        esp, t_ovo = ovo(s)
        v = simular_vida_educacao(b, s, 2, esp, sortear(s))
        out.append((v, genitor(v.motor.log, esp, sortear(s), t_ovo, v.motor.treino.estagio, b)))
    return out


def test_cruzar_e_deterministico_e_herda_dos_pais(pais):
    (_, p), (_, m) = pais
    assert p.estagio == m.estagio == "adulto"
    o1, o2 = cruzar(p, m, 31, "matheus"), cruzar(p, m, 31, "matheus")
    assert o1 == o2 and o1.especie in (p.especie, m.especie)
    zero = cruzar(p, m, 31, "matheus", replace(CONFIG_HERANCA, sigma_temperamento=0.0))
    for e in EIXOS:
        assert getattr(zero.temperamento, e) == pytest.approx((p.temperamento[e] + m.temperamento[e]) / 2)
    assert {cruzar(p, m, s, "x").especie for s in range(40)} == {p.especie, m.especie} or p.especie == m.especie


def test_pai_que_nao_e_adulto_nao_cruza(pais):
    (_, p), (_, m) = pais
    with pytest.raises(HerancaInvalida):
        cruzar(replace(p, estagio="adolescente"), m, 1, "x")


def test_filho_rejoga_com_origem_e_confere_os_pais(pais):
    (vp, p), (vm, m) = pais
    o = cruzar(p, m, 77, "matheus")
    fp, fm = fabricas_filho(o, ce=CONFIG_EDUCACAO_LIGADA)
    f = fm(fp(None), None, 6001)
    f.registrar_origem(o)
    f.avancar(600)
    f.observar(AcaoUsuario.ALIMENTAR)
    f.avancar(600)
    assert f.log[0].tipo == "origem"
    r = reproduzir_educacao(f.log, fp, semente=6001, fabrica_motor=fm)
    assert r.origem == o and r.estado() == f.estado() and r.historico_janelas == f.historico_janelas
    assert ler_origem(f.log[0]) == o
    conferir_pais(o, vp.motor.log, vm.motor.log)
    with pytest.raises(HerancaInvalida):
        conferir_pais(o, vm.motor.log, vp.motor.log)
    with pytest.raises(ValueError):
        reproduzir_com_feedback(f.log, fp, semente=6001, fabrica_motor=fm)


def test_origem_so_na_primeira_posicao_e_com_os_tracos_herdados(pais):
    (_, p), (_, m) = pais
    o = cruzar(p, m, 77, "matheus")
    fp, fm = fabricas_filho(o, ce=CONFIG_EDUCACAO_LIGADA)
    f = fm(fp(None), None, 6001)
    f.avancar(15)
    with pytest.raises(HerancaInvalida):
        f.registrar_origem(o)
    esp, _ = ovo(9)
    fp2, fm2 = fabricas_educacao(9, esp, sortear(9), ce=CONFIG_EDUCACAO_LIGADA)
    with pytest.raises(HerancaInvalida):
        fm2(fp2(None), None, 6001).registrar_origem(o)


# ================================================================ parte 6: duracoes
from digilab.config import CONFIG_DURACOES  # noqa: E402


def test_duracao_teste_e_a_de_hoje():
    t = CONFIG_DURACOES.cfg_evo("teste")
    assert t == CONFIG_EVOLUCAO_PESQUISA
    with pytest.raises(KeyError):
        CONFIG_DURACOES.cfg_evo("rapida")


def test_duracao_teste_explicita_bit_a_bit_igual_ao_padrao(vidas_edu):
    esp, _ = ovo(S_EDU)
    v = simular_vida_educacao("atencioso", S_EDU, 3, esp, sortear(S_EDU), duracao="teste")
    assert v.motor.log.para_jsonl() == vidas_edu["atencioso"][0].motor.log.para_jsonl()


def test_duracao_canonica_estagios_chamados_orcamento_e_replay():
    ce = CONFIG_DURACOES.cfg_evo("canonica")
    esp, _ = ovo(S_EDU)
    t = sortear(S_EDU)
    vidas = {b: simular_vida_educacao(b, S_EDU, 4, esp, t, duracao="canonica") for b in ("atencioso", "permissivo")}
    m = vidas["atencioso"].motor
    assert {e: d["tick"] for e, d in m.transicoes.items()} == {
        "crianca": ce.dur_bebe_min, "adolescente": ce.dur_bebe_min + ce.dur_crianca_min,
        "adulto": ce.dur_bebe_min + ce.dur_crianca_min + ce.dur_adolescente_min}
    assert min(j["inicio"] for j in m.historico_janelas) >= ce.dur_bebe_min
    assert vidas["atencioso"].interacoes == vidas["permissivo"].interacoes
    fp, fm = fabricas_educacao(S_EDU, esp, t, ce=CONFIG_EDUCACAO_LIGADA, cfg_evo=ce)
    r = reproduzir_educacao(m.log, fp, semente=S_EDU, fabrica_motor=fm)
    assert r.estado() == m.estado() and r.transicoes == m.transicoes


def test_morte_no_fim_do_avanco_antes_do_dono_agir():
    (fp, fm), _ = _fabricas_luta()
    m = fm(fp(None), None, S_EDU)
    m.avancar(15)
    m.lesionado_desde = m._estado.tick
    m.avancar(CONFIG_LESOES_LIGADA.horas_sem_tratar_morte * 60)     # termina exatamente no prazo
    assert m.morte is not None and m.morte["tick"] == m._estado.tick   # antes do passo do dono nesse tick
