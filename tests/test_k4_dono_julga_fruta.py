"""V2, K4-DONO-JULGA-FRUTA (docs/TAREFA_V2_K4_DONO_JULGA_FRUTA.md; contrato K4 e decisao E7 de docs/PLANO_ANALISE_V2_EXPERIMENTO_MAIOR.md,
secao 1; decisao K-11 de docs/PLANO_CALIBRACAO_CONJUNTA_V2.md): o dono do P3 julga a escolha de fruta pelo efeito real vigente.

Gates: a vida de hoje byte a byte (gabarito gravado ANTES da mudanca, num commit proprio); G1 com o julgamento; o julgamento segue o efeito
real vigente (tambem dos dois lados da troca do mutavel), um por consumo, no passo seguinte; o P2 e o P3 da mesma unidade conhecem o mesmo
efeito.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
from digilab.config import CONFIG_FRUTAS_LIGADA, CONFIG_INFORMACAO_LIGADA, CONFIG_LOBOS_APRENDIZ, CONFIG_PEDIDO_LIGADA  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.frutas import (DonoInformante, DonoPedinte, OfertasFrutas, PoliticaInstintoFrutas, fabricas_frutas,  # noqa: E402
                            simular_vida_frutas)
from digilab.policies.lobos import PoliticaLobos  # noqa: E402

GABARITO = RAIZ / "tests" / "gabaritos" / "k4_vidas_de_hoje.json"
DONOS = ("atencioso", "relapso", "aleatorio", "incoerente")
MUNDOS = ("casado_frutas", "descasado", "mutavel")
BRACOS = ("P0", "P1", "P2", "P3")
SEMENTES_BANCADA = (101, 202)                 # so dos testes
SEMENTES = (11, 22, 33)
BANCADA = bv.Bancada(4, 64)
CF, CI, CP = CONFIG_FRUTAS_LIGADA, CONFIG_INFORMACAO_LIGADA, CONFIG_PEDIDO_LIGADA
CEREBROS = {
    "instinto": lambda cfg=None: PoliticaInstintoFrutas(cfg, None, CF),
    "lobos": lambda cfg=None: PoliticaLobos(cfg, CONFIG_LOBOS_APRENDIZ, None, CF),
}


def _sha(texto: str) -> str:
    return hashlib.sha256(texto.encode()).hexdigest()


def _impressao(motor) -> dict:
    """o que tem de ficar igual: log, estado final, estado() do motor, acoes, rngs, frutas e o estado interno da politica"""
    return {
        "log": _sha(motor.log.para_jsonl()),
        "estado": _sha(repr(motor._estado)),
        "estado_motor": _sha(json.dumps(motor.estado(), sort_keys=True, default=repr)),
        "acoes": _sha(repr(motor.acoes_recentes(10**9))),
        "rngs": _sha(repr((motor._rng_politica.getstate(), motor._rng_ambiente.getstate(), motor._rng_fruta.getstate()))),
        "frutas": _sha(json.dumps(motor.resumo_frutas(), sort_keys=True, default=repr)),
        "politica": _sha(json.dumps(motor.politica.estado_interno(), sort_keys=True, default=repr)),
    }


def _vida_frutas_de_hoje(cerebro: str, extra: str, dono: str, s: int):
    """a vida pelo simular_vida_frutas de hoje: sem nada, com o informante do N5 ou com o dono que pede do N7 (com bronca)"""
    kw = {"cfg_informacao": CI} if extra == "informa" else {"cfg_pedido": CP} if extra == "pede" else {}
    fp, fm = fabricas_frutas(cfg_frutas=CF, politica_fabrica=CEREBROS[cerebro], **kw)
    inf = DonoInformante.do_genoma("certo", s, CF) if extra == "informa" else None
    ped = DonoPedinte.da_semente(s, CP, bronca=True) if extra == "pede" else None
    return simular_vida_frutas(f"{dono}-k4", criar_dono(dono), fp(), s, 3, 48, fm, OfertasFrutas(CF), rotulo_dono=dono,
                               informante=inf, pedinte=ped)


def _casos():
    for mundo in MUNDOS:
        for braco in BRACOS:
            for dono in DONOS:
                for s in SEMENTES_BANCADA:
                    yield f"bancada|{mundo}|{braco}|{dono}|{s}", ("bancada", bv.EspecVida(dono, braco, s, None, mundo, "lobos"))
    for cerebro in CEREBROS:
        for extra in ("sem", "informa", "pede"):
            for dono in DONOS:
                for s in SEMENTES:
                    yield f"frutas|{cerebro}|{extra}|{dono}|{s}", ("frutas", (cerebro, extra, dono, s))


def _vida_de_hoje(tipo, caso):
    if tipo == "bancada":
        return BANCADA.vida(caso).motor
    return _vida_frutas_de_hoje(*caso).motor


def gerar_gabarito() -> dict:
    return {chave: _impressao(_vida_de_hoje(*caso)) for chave, caso in _casos()}


# ================================================================== depois da mudanca
import dataclasses  # noqa: E402

import pytest  # noqa: E402

import medir_k4_orcamento as k4  # noqa: E402
from digilab.config import (CONFIG_FRUTAS, CONFIG_JULGAMENTO_FRUTA, CONFIG_JULGAMENTO_FRUTA_LIGADA, CONFIG_PADRAO,  # noqa: E402
                            ConfigJulgamentoFruta)
from digilab.donos import Visao  # noqa: E402
from digilab.events import FRUTAS, AcaoPet, AcaoUsuario, LogDeEventos  # noqa: E402
from digilab.frutas import DonoJulgaFruta, JulgadorFruta, MotorFrutas, reproduzir_frutas  # noqa: E402
from digilab.protocol import julgamento_nao_referendados, validar_parametros_julgamento  # noqa: E402

CJ = CONFIG_JULGAMENTO_FRUTA_LIGADA
CJ_FORA = ConfigJulgamentoFruta(ligada=True, no_orcamento=False)
FEEDBACK = {AcaoUsuario.ELOGIAR.value, AcaoUsuario.REPREENDER.value}


def _espec(mundo, s, braco="P3", dono="atencioso"):
    return bv.EspecVida(dono, braco, s, None, mundo, "lobos")


def _nucleo(m) -> tuple:
    return (m._estado, tuple(m.acoes_recentes(10**9)), m._rng_politica.getstate(), m._rng_ambiente.getstate(),
            m._rng_fruta.getstate(), [dict(c) for c in m.consumos], m.politica.estado_interno())


# ------------------------------------------------------------------ G2


def test_g2_vidas_de_hoje_byte_a_byte():
    """168 vidas (a bancada nos tres mundos das frutas, P0 a P3, e o simular_vida_frutas com e sem informante e pedido) iguais ao
    gabarito gravado antes do julgamento existir (commit anterior a este codigo)."""
    gab = json.loads(GABARITO.read_text(encoding="utf-8"))
    casos = dict(_casos())
    assert set(gab) == set(casos) and len(gab) == 168
    for chave, caso in casos.items():
        assert _impressao(_vida_de_hoje(*caso)) == gab[chave], chave


@pytest.mark.parametrize("mundo", MUNDOS)
def test_chave_ligada_sem_o_julgamento_e_a_vida_de_hoje(mundo):
    """Com a chave ligada (o motor expoe os consumos) e o dono de sempre, sem o DonoJulgaFruta, a vida e a da bancada."""
    for s in SEMENTES_BANCADA:
        espec = _espec(mundo, s)
        hoje = BANCADA.vida(espec).motor
        fm = k4.fabrica_motor_com_julgamento(BANCADA, espec, CJ)
        lig = bv.simular_vida_mundo(criar_dono("atencioso"), bv.CalendarioFrutas(s, BANCADA.cfg_frutas),
                                    BANCADA.politica(espec, CONFIG_PADRAO), s, BANCADA.dias, BANCADA.orcamento, "atencioso", fm)
        assert lig.log.para_jsonl() == hoje.log.para_jsonl() and _nucleo(lig) == _nucleo(hoje)
        assert "consumos_frutas" in lig.estado() and "consumos_frutas" not in hoje.estado()


# ------------------------------------------------------------------ o julgamento


@pytest.mark.parametrize("mundo", MUNDOS)
def test_julgamento_segue_o_efeito_real_vigente_um_por_consumo_no_passo_seguinte(mundo):
    """Cada consumo e julgado uma vez, pelo efeito que o motor aplicou nele (o real vigente; no mutavel, dos dois lados da troca), no
    primeiro passo do dono depois dele; o julgamento abre as acoes daquele passo no log; o orcamento fecha igual."""
    lados = set()
    for s in SEMENTES_BANCADA:
        motor, j = k4.vida_p3_com_julgamento(BANCADA, _espec(mundo, s))
        assert len(j.julgados) == len(motor.consumos) > 0 and not j.descartados
        dono = [e for e in motor.log if e.tipo == "acao_usuario" and str(e.valor) not in bv.FORA_DO_ORCAMENTO]
        assert len(dono) == BANCADA.orcamento
        for (tc, f, sinal, tj), c in zip(j.julgados, motor.consumos):
            assert (tc, f) == (c["tick"], c["fruta"])
            efeito = c["efeito_humor"]
            assert sinal == (1 if efeito > 0 else -1 if efeito < 0 else 0)
            assert 0 < tj - tc <= 15 and tj % 15 == 0
            if mundo == "mutavel":
                lados.add(tc >= BANCADA.tick_troca)
        # no log, o julgamento vem primeiro entre as acoes do dono do passo
        por_tick: dict = {}
        for e in dono:
            por_tick.setdefault(e.tick, []).append(str(e.valor))
        julg_por_tick: dict = {}
        for _, _, sinal, tj in j.julgados:
            if sinal:
                julg_por_tick.setdefault(tj, []).append(AcaoUsuario.ELOGIAR.value if sinal > 0 else AcaoUsuario.REPREENDER.value)
        for tj, js in julg_por_tick.items():
            assert por_tick[tj][:len(js)] == js
    if mundo == "mutavel":
        assert lados == {False, True}                                   # consumos julgados antes e depois da troca


def test_o_feedback_e_creditado_a_decisao_de_comer():
    """Com uma decisao por passo do dono, a decisao anterior ao julgamento e sempre a de comer a fruta julgada (a janela da v1 credita
    a ultima decisao)."""
    for mundo in MUNDOS:
        motor, j = k4.vida_p3_com_julgamento(BANCADA, _espec(mundo, 101))
        acoes = motor.acoes_recentes(10**9)
        for tc, _, sinal, tj in j.julgados:
            ultima = [(t, a) for t, a in acoes if t < tj][-1]
            assert ultima == (tc, AcaoPet.COMER)


def test_p2_e_p3_da_mesma_unidade_conhecem_o_mesmo_efeito():
    """O julgador do P3 e o informante do P2 vem de `Bancada.efeitos_reais`: os mesmos efeitos, a mesma troca; e o P3 repreende
    exatamente o que o P2 diz que "faz mal"."""
    for mundo in MUNDOS:
        for s in SEMENTES_BANCADA:
            for genoma in (None, 7):
                p3 = bv.EspecVida("atencioso", "P3", s, genoma, mundo, "lobos")
                p2 = bv.EspecVida("atencioso", "P2", s, genoma, mundo, "lobos")
                j = k4.julgador_da_vida(BANCADA, p3)
                inf = BANCADA.informante(p2)
                assert j.efeitos_antes == inf.antes.efeito_humor and j.tick_troca == inf.tick_troca
                assert j.efeitos_depois == (inf.depois.efeito_humor if inf.depois is not None else None)
                ticks = (0, 1440) if inf.tick_troca is None else (inf.tick_troca - 15, inf.tick_troca, inf.tick_troca + 15)
                for t in ticks:
                    d = inf.depois if inf.depois is not None and t >= inf.tick_troca else inf.antes
                    for f in FRUTAS:
                        assert (j.sinal(f, t) < 0) == (d.conteudo(f) == "mal")


def test_g1_replay_com_o_julgamento():
    for mundo in MUNDOS:
        for s in SEMENTES_BANCADA:
            espec = _espec(mundo, s)
            motor, _ = k4.vida_p3_com_julgamento(BANCADA, espec)
            fm = k4.fabrica_motor_com_julgamento(BANCADA, espec, CJ)
            r = reproduzir_frutas(LogDeEventos.de_jsonl(motor.log.para_jsonl()), BANCADA.fabrica_politica(espec), semente=s,
                                  fabrica_motor=fm)
            assert _impressao(r) == _impressao(motor)
            assert _nucleo(BANCADA.rejogar(motor.log, espec)) == _nucleo(motor)       # o replay da bancada, sem a chave, e o mesmo


# ------------------------------------------------------------------ o orcamento e a alternativa


def test_no_orcamento_cabe_no_passo_e_descarta_o_que_nao_cabe():
    """O DonoJulgaFruta poe o julgamento na frente e da ao dono embrulhado o que sobra; o que passar do maximo do passo e descartado."""
    j = JulgadorFruta({"a": -0.1, "b": 0.0, "c": 0.1}, cfg_julgamento=CJ)
    dono = DonoJulgaFruta(criar_dono("atencioso"), j)
    estado = dict(BANCADA.vida(_espec("descasado", 101)).motor.estado(), consumos_frutas=((5, "a"), (5, "b"), (5, "c"), (6, "a")))
    visao = Visao(estado=estado, passo=0, passos_totais=10, orcamento=40, gasto=0, minimo_obrigatorio=0, maximo_permitido=2)
    acoes = dono.decidir(visao, None)
    assert acoes[:2] == [AcaoUsuario.REPREENDER, AcaoUsuario.ELOGIAR] and len(acoes) <= 2
    assert [d[:3] for d in j.descartados] == [(6, "a", -1)]
    assert [x[:3] for x in j.julgados] == [(5, "a", -1), (5, "b", 0), (5, "c", 1), (6, "a", -1)]


def test_fora_do_orcamento_a_alternativa_atras_da_opcao():
    """Fora do orcamento (no_orcamento False): o julgador entra pela vida, depois das acoes do dono do passo; o canal fecha o orcamento
    com o dono de sempre, e os julgamentos ficam por fora."""
    for dono in ("atencioso", "aleatorio"):
        for s in SEMENTES:
            fp, fm = fabricas_frutas(cfg_frutas=CF, politica_fabrica=CEREBROS["lobos"], cfg_julgamento=CJ_FORA)
            j = JulgadorFruta.do_genoma(s, CF, CJ_FORA)
            v = simular_vida_frutas(f"{dono}-k4", criar_dono(dono), fp(), s, 3, 48, fm, OfertasFrutas(CF), rotulo_dono=dono,
                                    julgador=j)
            com_sinal = [x for x in j.julgados if x[2] != 0]
            assert v.interacoes == 48 and v.julgamentos_fora == len(com_sinal) and len(j.julgados) == len(v.motor.consumos)
            fb = [e for e in v.motor.log if e.tipo == "acao_usuario" and str(e.valor) in FEEDBACK]
            assert len(fb) >= len(com_sinal)
            r = reproduzir_frutas(LogDeEventos.de_jsonl(v.motor.log.para_jsonl()), fp, semente=s, fabrica_motor=fm)
            assert _impressao(r) == _impressao(v.motor)


def test_falha_alto_fora_do_contrato():
    ef = {f: 0.0 for f in FRUTAS}
    with pytest.raises(ValueError):
        DonoJulgaFruta(criar_dono("atencioso"), JulgadorFruta(ef, cfg_julgamento=CJ_FORA))
    fp, fm = fabricas_frutas(cfg_frutas=CF, cfg_julgamento=CJ)
    with pytest.raises(ValueError):                                # no orcamento nao passa pelo julgador da vida
        simular_vida_frutas("x", criar_dono("atencioso"), fp(), 11, 1, 16, fm, OfertasFrutas(CF), julgador=JulgadorFruta(ef))
    fp0, fm0 = fabricas_frutas(cfg_frutas=CF)
    with pytest.raises(KeyError):                                  # o dono que julga num motor sem a chave
        simular_vida_frutas("x", DonoJulgaFruta(criar_dono("atencioso"), JulgadorFruta(ef)), fp0(), 11, 1, 16, fm0, OfertasFrutas(CF))
    with pytest.raises(ValueError):
        MotorFrutas(None, None, 11, cfg_frutas=CONFIG_FRUTAS, cfg_julgamento=CJ)
    with pytest.raises(ValueError):
        JulgadorFruta({"a": 0.0})
    with pytest.raises(ValueError):
        JulgadorFruta(ef, ef, None)
    with pytest.raises(ValueError):
        k4.vida_p3_com_julgamento(BANCADA, _espec("descasado", 101, braco="P2"))


def test_parametros_registrados():
    validar_parametros_julgamento()
    assert julgamento_nao_referendados() == ["ConfigJulgamentoFruta.no_orcamento"]
    assert CONFIG_JULGAMENTO_FRUTA == ConfigJulgamentoFruta() and not CONFIG_JULGAMENTO_FRUTA.ligada
    assert CONFIG_JULGAMENTO_FRUTA.no_orcamento and dataclasses.replace(CJ, ligada=False) == CONFIG_JULGAMENTO_FRUTA
