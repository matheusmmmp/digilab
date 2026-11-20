"""V2, P2D-P3I, parte A (docs/TAREFA_V2_P2D_P3I.md, secao 2; adendo 3, secao 3.3, de docs/PLANO_ANALISE_V2_EXPERIMENTO_MAIOR.md): o
julgador da fruta com a saida "informacao", que emite informar_fruta_<f>_<bem|mal> sobre a fruta consumida, no primeiro passo do dono
depois do consumo, fora do orcamento, com o efeito real vigente.

Gates: o modo desligado (a saida "feedback", o K4 de hoje) byte a byte pelo gabarito gravado antes (tests/gabarito_p2d_p3i.py, commit
proprio); uma informacao por consumo, no passo seguinte, com o conteudo do efeito vigente (dos dois lados da troca do mutavel), a neutra
incluida; nada chega ao aprendiz como sinal (espiao no receber_acao_dono); G1.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import bancada_v2 as bv  # noqa: E402
import gabarito_p2d_p3i as gab  # noqa: E402
import medir_k4_orcamento as k4  # noqa: E402
from digilab.config import (CONFIG_FRUTAS_LIGADA, CONFIG_INFORMACAO_LIGADA, CONFIG_JULGAMENTO_FRUTA_LIGADA, CONFIG_PADRAO,  # noqa: E402
                            ConfigJulgamentoFruta)
from digilab.donos import criar_dono  # noqa: E402
from digilab.events import ACOES_INFORMACAO, FRUTAS, LogDeEventos, informar  # noqa: E402
from digilab.frutas import (DonoJulgaFruta, InformacaoSemChave, JulgadorFruta, OfertasFrutas, fabricas_frutas,  # noqa: E402
                            reproduzir_frutas, simular_vida_frutas)

CF, CI = CONFIG_FRUTAS_LIGADA, CONFIG_INFORMACAO_LIGADA
CJ_FORA = ConfigJulgamentoFruta(ligada=True, no_orcamento=False)
MUNDOS = ("casado_frutas", "descasado", "mutavel")
SEMENTES = ((101, None), (202, 202))                      # so dos testes
BANCADA = bv.Bancada(4, 64, cfg_lobos=bv.cfg_lobos_do_ponto("T3", {"w0_info": 256}))
INFORMACOES = frozenset(a.value for a in ACOES_INFORMACAO)


def _julgador_info(espec: bv.EspecVida) -> JulgadorFruta:
    """o conhecimento do K4 (os efeitos reais da bancada, os do informante do P2, a troca do mutavel), com a saida informacao"""
    j = k4.julgador_da_vida(BANCADA, espec, CJ_FORA)
    return JulgadorFruta(j.efeitos_antes, j.efeitos_depois, j.tick_troca, CJ_FORA, saida="informacao")


def _vida(espec: bv.EspecVida, espiao: bool = True):
    """(motor, julgador, espiao): o braco do espec (P2 = o P2d sem o informante da oferta; P3 = o P3i) no mundo da bancada, com as ofertas
    do calendario e o julgamento como informacao pela regra do mundo, fora do orcamento"""
    j = _julgador_info(espec)
    pol = BANCADA.politica(espec, CONFIG_PADRAO)
    esp = bv._Espiao(pol) if espiao else None
    regra = bv.RegraFrutasComJulgador(bv.CalendarioFrutas(espec.semente, BANCADA.cfg_frutas), j)
    fm = k4.fabrica_motor_com_julgamento(BANCADA, espec, CJ_FORA)
    motor = bv.simular_vida_mundo(criar_dono(espec.dono), regra, esp or pol, espec.semente, BANCADA.dias, BANCADA.orcamento,
                                  espec.dono, fm)
    return motor, j, esp


# ------------------------------------------------------------------ G2: o modo desligado e o de hoje


def test_g2_saida_feedback_e_a_vida_de_hoje_byte_a_byte():
    """144 vidas (a bancada com o K4, montagem simples e completa, e o simular_vida_frutas com o julgador fora do orcamento, com e sem o
    canal da informacao) iguais ao gabarito gravado antes da saida "informacao" existir (commit anterior a este codigo)."""
    g = json.loads(gab.ARQUIVO.read_text(encoding="utf-8"))
    casos = dict(gab.casos())
    assert set(g) == set(casos) and len(g) == 144
    for chave, caso in casos.items():
        assert gab.vida_de_hoje(*caso) == g[chave], chave


def test_feedback_e_o_padrao():
    ef = {f: 0.0 for f in FRUTAS}
    assert JulgadorFruta(ef).saida == "feedback" and JulgadorFruta.do_genoma(11, CF, CJ_FORA).saida == "feedback"
    assert JulgadorFruta.do_genoma(11, CF, CJ_FORA, saida="informacao").saida == "informacao"


# ------------------------------------------------------------------ a informacao sobre a fruta consumida


@pytest.mark.parametrize("braco", ["P2", "P3"])
@pytest.mark.parametrize("mundo", MUNDOS)
def test_uma_informacao_por_consumo_no_passo_seguinte_com_o_efeito_vigente(mundo, braco):
    """Cada consumo vira uma informacao sobre a fruta consumida, no primeiro passo do dono depois dele, com o conteudo do efeito que o
    motor aplicou (o real vigente; no mutavel, dos dois lados da troca); so o julgador informa; o orcamento do
    dono fecha igual."""
    lados = set()
    for s, g in SEMENTES:
        motor, j, _ = _vida(bv.EspecVida("atencioso", braco, s, g, mundo))
        assert len(j.informadas) == len(j.julgados) == len(motor.consumos) > 0
        for (tj, f, c, tc), consumo in zip(j.informadas, motor.consumos):
            assert (tc, f) == (consumo["tick"], consumo["fruta"])
            assert c == ("mal" if consumo["efeito_humor"] < 0 else "bem")
            assert 0 < tj - tc <= 15 and tj % 15 == 0
            if mundo == "mutavel":
                lados.add(tc >= BANCADA.tick_troca)
        infos = [(e.tick, str(e.valor)) for e in motor.log if e.tipo == "acao_usuario" and str(e.valor) in INFORMACOES]
        assert infos == [(tj, informar(f, c).value) for tj, f, c, _ in j.informadas]      # so o julgador informa, na ordem
        dono = [e for e in motor.log if e.tipo == "acao_usuario" and str(e.valor) not in bv.FORA_DO_ORCAMENTO]
        assert len(dono) == BANCADA.orcamento
    if mundo == "mutavel":
        assert lados == {False, True}


def test_a_neutra_tambem_e_informada_como_bem():
    """A fruta do meio (efeito 0) entra: "bem", como no DonoInformante; o feedback do K4 nada faria com ela."""
    neutras = 0
    for mundo in ("casado_frutas", "descasado"):
        for s, g in SEMENTES:
            motor, j, _ = _vida(bv.EspecVida("atencioso", "P3", s, g, mundo))
            for (_, _, c, _), (_, _, sinal, _), consumo in zip(j.informadas, j.julgados, motor.consumos):
                if consumo["efeito_humor"] == 0.0:
                    assert sinal == 0 and c == "bem"
                    neutras += 1
    assert neutras > 0


def test_a_informacao_entra_na_percepcao_e_nao_chega_ao_aprendiz():
    """Espiao no receber_acao_dono: nenhum informar_* chega ao cerebro. No P3i o que chega e so o feedback do dono de sempre; no P2d nada
    (a fonte informacao nao repassa o dono). A informacao entra na percepcao (decisoes com informacao vigente)."""
    for mundo in MUNDOS:
        for braco in ("P2", "P3"):
            motor, j, esp = _vida(bv.EspecVida("atencioso", braco, 101, None, mundo))
            assert not any(a in INFORMACOES for a, _ in esp.recebidas)
            assert motor.decisoes_com_informacao > 0 and len(motor.informacoes) == len(j.informadas)


def test_a_mesma_informacao_no_p2_com_ou_sem_o_cerebro_que_le():
    """O julgador so le os consumos: com o mesmo cerebro e a mesma vida, P2 e P3 recebem a informacao do mesmo efeito vigente
    (o mesmo conhecimento do informante do P2 da unidade)."""
    for mundo in MUNDOS:
        p2 = bv.EspecVida("atencioso", "P2", 101, None, mundo)
        j = _julgador_info(p2)
        inf = BANCADA.informante(p2)
        for t in (0, 1440, BANCADA.tick_troca, BANCADA.tick_troca + 15):
            d = inf.depois if inf.depois is not None and t >= inf.tick_troca else inf.antes
            for f in FRUTAS:
                assert j.conteudo(f, t) == d.conteudo(f)


# ------------------------------------------------------------------ G1 e erros de uso


def test_g1_replay_com_a_informacao():
    for mundo in MUNDOS:
        for braco in ("P2", "P3"):
            for s, g in SEMENTES:
                espec = bv.EspecVida("atencioso", braco, s, g, mundo)
                motor, _, _ = _vida(espec, espiao=False)
                fm = k4.fabrica_motor_com_julgamento(BANCADA, espec, CJ_FORA)
                r = reproduzir_frutas(LogDeEventos.de_jsonl(motor.log.para_jsonl()), BANCADA.fabrica_politica(espec), semente=s,
                                      fabrica_motor=fm)
                assert gab.impressao(r, 0) == gab.impressao(motor, 0)


def test_simular_vida_frutas_conta_as_informacoes_do_julgador():
    """Fora da bancada (o simular_vida_frutas): as informacoes do julgador contam em `informacoes`, nao em `julgamentos_fora`; replay
    bit a bit."""
    for s in (11, 22):
        fp, fm = fabricas_frutas(cfg_frutas=CF, politica_fabrica=gab.CEREBROS["lobos"], cfg_julgamento=CJ_FORA, cfg_informacao=CI)
        j = JulgadorFruta.do_genoma(s, CF, CJ_FORA, saida="informacao")
        v = simular_vida_frutas("atencioso-p3i", criar_dono("atencioso"), fp(), s, 3, 48, fm, OfertasFrutas(CF), rotulo_dono="atencioso",
                                julgador=j)
        assert v.interacoes == 48 and v.julgamentos_fora == 0 and v.informacoes == len(j.informadas) == len(v.motor.consumos)
        r = reproduzir_frutas(LogDeEventos.de_jsonl(v.motor.log.para_jsonl()), fp, semente=s, fabrica_motor=fm)
        assert gab.impressao(r, 0) == gab.impressao(v.motor, 0)


def test_falha_alto_fora_do_contrato():
    ef = {f: 0.0 for f in FRUTAS}
    with pytest.raises(ValueError):
        JulgadorFruta(ef, cfg_julgamento=CJ_FORA, saida="bronca")
    with pytest.raises(ValueError):                                    # a informacao e so fora do orcamento
        JulgadorFruta(ef, cfg_julgamento=CONFIG_JULGAMENTO_FRUTA_LIGADA, saida="informacao")
    with pytest.raises(ValueError):
        DonoJulgaFruta(criar_dono("atencioso"), JulgadorFruta(ef, cfg_julgamento=CJ_FORA, saida="informacao"))
    fp, fm = fabricas_frutas(cfg_frutas=CF, cfg_julgamento=CJ_FORA)    # o motor sem o canal da informacao
    with pytest.raises(InformacaoSemChave):
        simular_vida_frutas("x", criar_dono("atencioso"), fp(), 11, 3, 48, fm, OfertasFrutas(CF),
                            julgador=JulgadorFruta.do_genoma(11, CF, CJ_FORA, saida="informacao"))
