"""Emocao, extremos e habituacao (docs/ADENDO_MEMORIA_EMOCAO_DF.md, Parte 2, secao 2.5)."""

from __future__ import annotations

import json
import sys
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.config import CONFIG_EMOCAO, CONFIG_EXPRESSAO, CONFIG_HABITUACAO  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.emocao import EMOCOES, TabelaEmocaoIncompleta, emocao_de, emocoes_da_memoria, validar_emocoes  # noqa: E402
from digilab.events import AcaoUsuario as U  # noqa: E402
from digilab.expressao import ESTAGIOS, EMOCAO_TXT, TOM_CARATER, carateres_citados, emocoes_citadas, \
    expressar_carater, expressar_emocao, expressar_temperamento, marcadores_citados, tons_citados, \
    validar_tabelas_personalidade  # noqa: E402
from digilab.memoria_espacos import MemoriaEspacos  # noqa: E402
from digilab.obediencia import MotorPersonalidade, PoliticaBanditPersonalidade  # noqa: E402
from digilab.protocol import PROTOCOLO_ARENA_V1_HABITUACAO, PROTOCOLO_ARENA_V1_PERSONALIDADE, \
    PROTOCOLO_ARENA_V1_SEM_HABITUACAO, hash_protocolo  # noqa: E402
from digilab.temperamento import EIXOS, NEUTRO, Temperamento, sortear  # noqa: E402
from digilab.treino import reproduzir_com_feedback, simular_vida  # noqa: E402


def _vida(dono, semente, t, hab, dias=3, orc=48):
    fm = lambda politica, cfg, s: MotorPersonalidade(politica, cfg, s, t)  # noqa: E731
    fp = lambda: PoliticaBanditPersonalidade(temperamento=t, habituacao_ligada=hab)  # noqa: E731
    v = simular_vida(dono, criar_dono(dono), fp(), semente, dias, orc, rotulo_dono=dono, fabrica_motor=fm)
    return v, fm, fp


# ------------------------------------------------------------------ emocao (2.1)
def test_tabela_de_emocoes_cobre_toda_categoria_ativa_e_falta_levanta():
    validar_emocoes()
    validar_tabelas_personalidade()
    sem_demora = {k: v for k, v in EMOCOES.items() if k != "demora"}
    with pytest.raises(TabelaEmocaoIncompleta):
        validar_emocoes(sem_demora)
    with pytest.raises(TabelaEmocaoIncompleta):
        validar_emocoes({**EMOCOES, "demora": {"regras": (("coragem", "+", "x", 0.5),), "padrao": ("y", 0)}})
    # toda combinacao de temperamento da uma emocao com texto (padrao cobre o resto)
    for ovo in range(1, 80):
        t = sortear(ovo)
        for cat in EMOCOES:
            e = emocao_de(cat, t)
            assert e.nome in EMOCAO_TXT and -1 <= e.valencia <= 1


def test_emocao_segue_o_eixo_de_maior_modulo_e_o_limiar():
    lim = CONFIG_EMOCAO.limiar_eixo
    assert emocao_de("demora", NEUTRO).nome == "incomodo"
    assert emocao_de("demora", Temperamento(rancor=lim)).nome == "incomodo"        # precisa PASSAR do limiar
    assert emocao_de("demora", Temperamento(rancor=0.5)).nome == "raiva"
    assert emocao_de("demora", Temperamento(sensibilidade=0.5)).nome == "tristeza"
    assert emocao_de("demora", Temperamento(rancor=0.3, sensibilidade=0.6)).nome == "tristeza"
    assert emocao_de("demora", Temperamento(rancor=0.6, sensibilidade=0.3)).eixo == "rancor"
    assert emocao_de("bronca", Temperamento(sensibilidade=-0.7)).nome == "ferido"
    with pytest.raises(TabelaEmocaoIncompleta):
        emocao_de("sujeira", NEUTRO)


def test_expressao_da_emocao_so_cita_a_emocao_e_nenhum_fator():
    for cat in EMOCOES:
        for t in (NEUTRO, Temperamento(rancor=0.9), Temperamento(sensibilidade=0.9), Temperamento(sensibilidade=-0.9)):
            e = emocao_de(cat, t, 5, 2)
            for est in ESTAGIOS:
                c = expressar_emocao(e, est).conteudo
                if est == "bebe":
                    assert emocoes_citadas(c) == set()
                else:
                    assert emocoes_citadas(c) == {e.nome}, c
                assert marcadores_citados(c) == set(), c    # causa = evento, nunca um fator inventado


# ------------------------------------------------------------------ extremos (2.2)
def test_so_eixo_extremo_e_descrito():
    lim = CONFIG_EXPRESSAO.limiar_extremo
    assert lim == 0.2
    abaixo = Temperamento(**{e: lim * 0.99 for e in EIXOS})
    assert all(tons_citados(expressar_temperamento(abaixo, est).conteudo) == set() for est in ESTAGIOS)
    assert tons_citados(expressar_temperamento(Temperamento(rancor=-lim), "adulto").conteudo) == {("rancor", "-")}
    car = {"impetuoso": 0.19, "paciente": -0.5, "atento": 0.25, "resistente": 0.0}
    assert carateres_citados(expressar_carater(car, "adulto").conteudo) == {("paciente", "-"), ("atento", "+")}
    assert carateres_citados(expressar_carater(car, "adolescente").conteudo) == {("paciente", "-")}
    assert carateres_citados(expressar_carater({k: 0.1 for k in car}, "adulto").conteudo) == set()
    assert {e for e, _ in TOM_CARATER} == set(car)
    with pytest.raises(ValueError):
        expressar_carater(car, "crianca")


# ------------------------------------------------------------------ habituacao (2.3)
def test_habituacao_segue_a_formula_e_a_teimosia_acelera_broncas():
    h = CONFIG_HABITUACAO.h
    j = CONFIG_HABITUACAO.janela_ticks
    m = MemoriaEspacos(habituacao=CONFIG_HABITUACAO)
    for i, t in enumerate((10, 20, 30)):
        assert m.fator_habituacao("bronca", t) == pytest.approx(h ** i)     # repeticoes antes deste evento
        m.acao_dono(U.REPREENDER, t)
    assert [ev[2] for ev in m.eventos] == [1.0, 1.0, 1.0]                     # bruto guardado
    # a memoria mais fraca da mesma categoria e descartada: fica a primeira, com forca 1
    assert [x.intensidade for x in m.curto] == [1.0] and m.contagem["descartada"] == 2
    assert m.fator_habituacao("bronca", 10 + j) == pytest.approx(h ** 2)      # a de 10 saiu da janela
    assert m.fator_habituacao("bronca", 30 + j) == 1.0
    # passada a promocao, uma bronca habituada ainda entra num prazo vazio com a forca reduzida
    m.acao_dono(U.REPREENDER, 31)                                           # h**3: descartada tambem
    m.avancar(10 + 12 * 60)                                                  # a de 10 vai para o longo prazo
    assert m.curto == [] and [x.criada for x in m.longo] == [10]
    m.acao_dono(U.REPREENDER, 745)                                           # na janela: as de 30 e 31
    assert [x.intensidade for x in m.curto] == [pytest.approx(h ** 2)]
    assert m.fator_habituacao("elogio", 40) == 1.0                           # categoria positiva: sem habituacao
    teimoso = MemoriaEspacos(habituacao=CONFIG_HABITUACAO, temperamento=Temperamento(teimosia=1.0))
    assert teimoso.h_de("bronca") == pytest.approx(h * (1 - CONFIG_HABITUACAO.k_teimosia_bronca))
    assert teimoso.h_de("demora") == h
    docil = MemoriaEspacos(habituacao=CONFIG_HABITUACAO, temperamento=Temperamento(teimosia=-1.0))
    assert docil.h_de("bronca") == h
    desligada = MemoriaEspacos()
    for t in (10, 20, 30):
        desligada.acao_dono(U.REPREENDER, t)
    assert desligada.curto[0].intensidade == 1.0 and desligada.fator_habituacao("bronca", 30) == 1.0


def test_habituacao_enfraquece_a_repreensao_que_chega_ao_bandit():
    t = Temperamento(teimosia=0.5)
    ligada = PoliticaBanditPersonalidade(temperamento=t, habituacao_ligada=True)
    desl = PoliticaBanditPersonalidade(temperamento=t)
    for p in (ligada, desl):
        p.memoria.acao_dono(U.REPREENDER, 5)
        p.memoria.acao_dono(U.REPREENDER, 6)
    assert desl._peso_recompensa("bronca", 7) == 1.0
    esperado = CONFIG_HABITUACAO.h * (1 - CONFIG_HABITUACAO.k_teimosia_bronca * 0.5)
    assert ligada._peso_recompensa("bronca", 7) == pytest.approx(esperado ** 2)
    assert ligada._peso_recompensa("elogio", 7) == 1.0


def test_modula_memoria_desligada_por_padrao_e_ligada_escala_pela_valencia():
    assert CONFIG_EMOCAO.modula_memoria is False
    t = Temperamento(rancor=0.9)
    m = MemoriaEspacos(temperamento=t, cfg_emocao=replace(CONFIG_EMOCAO, modula_memoria=True))
    m.acao_dono(U.REPREENDER, 3)
    assert m.curto[0].intensidade == pytest.approx(abs(emocao_de("bronca", t).valencia))


# ------------------------------------------------------------------ equivalencia e replay (2.5)
def test_sem_habituacao_reproduz_a_personalidade_completa_bit_a_bit():
    """Emocao e extremos sao somente leitura: habituacao desligada = run gravada da personalidade."""
    p = PROTOCOLO_ARENA_V1_PERSONALIDADE
    t = sortear(101)
    v, _, _ = _vida("atencioso", 101, t, False, p.v("dias_simulados"), p.v("orcamento_interacoes"))
    pasta = RAIZ / "artifacts_v1_personalidade" / "completa" / "vidas"
    assert v.motor.log.para_jsonl() == (pasta / "atencioso@101.jsonl").read_text(encoding="utf-8")
    assert json.loads(json.dumps(v.motor.politica.estado_interno(), sort_keys=True)) == \
        json.loads((pasta / "atencioso@101.politica.json").read_text(encoding="utf-8"))


def test_replay_bit_a_bit_com_habituacao_e_ela_muda_o_aprendizado():
    t = sortear(303)
    v, fm, fp = _vida("incoerente", 303, t, True)
    r = reproduzir_com_feedback(v.motor.log, lambda c: PoliticaBanditPersonalidade(c, t, habituacao_ligada=True),
                                semente=303, fabrica_motor=fm)
    assert r.estado() == v.motor.estado()
    assert r.politica.estado_interno() == v.motor.politica.estado_interno()
    assert [e.para_dict() for e in emocoes_da_memoria(r.politica.memoria, t)] == \
        [e.para_dict() for e in emocoes_da_memoria(v.motor.politica.memoria, t)]
    sem, _, _ = _vida("incoerente", 303, t, False)
    assert sem.motor.politica.estado_interno() != v.motor.politica.estado_interno()


def test_protocolos_da_parte2_nao_mexem_no_da_personalidade():
    assert hash_protocolo(PROTOCOLO_ARENA_V1_PERSONALIDADE).startswith("d986ff1b9308")
    assert PROTOCOLO_ARENA_V1_HABITUACAO.v("habituacao_ligada") is True
    assert PROTOCOLO_ARENA_V1_SEM_HABITUACAO.v("habituacao_ligada") is False
    assert PROTOCOLO_ARENA_V1_HABITUACAO.v("sementes_coorte") == PROTOCOLO_ARENA_V1_PERSONALIDADE.v("sementes_coorte")
    for p in (PROTOCOLO_ARENA_V1_HABITUACAO, PROTOCOLO_ARENA_V1_SEM_HABITUACAO):
        p.validar()
