"""V2, N7-MUNDO (docs/TAREFA_V2_N7_MUNDO.md; docs/PLANO_ANALISE_V2_N7.md, decisoes N7-1, N7-6, N7-7, N7-8): o pedido "deixe a fruta X".

O pedido e um evento novo (`pedir_deixar_fruta_<f>`), separado da informacao do N5, fora do orcamento e sem mexer no estado; a percepcao e
`Observacao.pedido_frutas` (-1 na fruta com pedido vigente), injetada so pelo MotorFrutas com ConfigPedido ligada. O `DonoPedinte` sorteia
a fruta X por vida (rng propria `pedido-fruta`, independente da preferencia inata), pede logo depois de cada oferta que tem X nos dias 1-10
(extincao nos dias 11-14) e, so no braco P3+ped, da a bronca (`repreender`) no primeiro passo do dono depois de o pet comer X com pedido
vigente, fora do orcamento.
Gates: G2 (sem pedido no log = a vida de hoje, byte a byte, contra o gabarito gravado ANTES da mudanca; mais as 168 vidas da bancada de
tests/test_frutas_cenario.py); G1; o pedido nao altera o estado nem o orcamento; as fases e o sorteio da fruta; a rng do pedido nao mexe
nas outras.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.config import CONFIG_FRUTAS_LIGADA, CONFIG_INFORMACAO_LIGADA, CONFIG_LOBOS_APRENDIZ  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.frutas import DonoInformante, OfertasFrutas, PoliticaInstintoFrutas, fabricas_frutas, simular_vida_frutas  # noqa: E402
from digilab.policies.lobos import PoliticaLobos  # noqa: E402

GABARITO = RAIZ / "tests" / "gabaritos" / "n7_vidas_de_hoje.json"
DONOS = ("atencioso", "relapso", "aleatorio", "incoerente")
SEMENTES = (11, 22, 33)                       # so dos testes
DIAS, ORC = 3, 48
CF, CI = CONFIG_FRUTAS_LIGADA, CONFIG_INFORMACAO_LIGADA
CEREBROS = {
    "instinto": lambda cfg=None: PoliticaInstintoFrutas(cfg, None, CF),
    "lobos": lambda cfg=None: PoliticaLobos(cfg, CONFIG_LOBOS_APRENDIZ, None, CF),     # aprendendo com o dono (P3 que ve as frutas)
}


def _sha(texto: str) -> str:
    return hashlib.sha256(texto.encode()).hexdigest()


def _impressao(motor) -> dict:
    """o que tem de ficar igual: log, estado final, estado() do motor, ultimas acoes, rngs, frutas e o estado interno da politica"""
    return {
        "log": _sha(motor.log.para_jsonl()),
        "estado": _sha(repr(motor._estado)),
        "estado_motor": _sha(json.dumps(motor.estado(), sort_keys=True, default=repr)),
        "acoes": _sha(repr(motor.acoes_recentes(10**9))),
        "rngs": _sha(repr((motor._rng_politica.getstate(), motor._rng_ambiente.getstate(), motor._rng_fruta.getstate()))),
        "frutas": _sha(json.dumps(motor.resumo_frutas(), sort_keys=True, default=repr)),
        "politica": _sha(json.dumps(motor.politica.estado_interno(), sort_keys=True, default=repr)),
    }


def _vida_de_hoje(cerebro: str, informa: bool, dono: str, s: int, **kw):
    fp, fm = fabricas_frutas(cfg_frutas=CF, cfg_informacao=CI if informa else None, politica_fabrica=CEREBROS[cerebro], **kw)
    inf = DonoInformante.do_genoma("certo", s, CF) if informa else None
    v = simular_vida_frutas(f"{dono}-n7", criar_dono(dono), fp(), s, DIAS, ORC, fm, OfertasFrutas(CF), rotulo_dono=dono, informante=inf)
    return v, fp, fm


def _casos():
    for cerebro in CEREBROS:
        for informa in (False, True):
            for dono in DONOS:
                for s in SEMENTES:
                    yield f"{cerebro}|{'informa' if informa else 'sem'}|{dono}|{s}", (cerebro, informa, dono, s)


def gerar_gabarito() -> dict:
    return {chave: _impressao(_vida_de_hoje(*caso)[0].motor) for chave, caso in _casos()}


# ================================================================== depois da mudanca
import random  # noqa: E402

import pytest  # noqa: E402

from digilab.config import CONFIG_FRUTAS, CONFIG_PEDIDO, CONFIG_PEDIDO_LIGADA, TICKS_POR_DIA, ConfigPedido  # noqa: E402
from digilab.events import (ACOES_FRUTAS, ACOES_INFORMACAO, ACOES_PEDIDO, FRUTAS, AcaoUsuario, LogDeEventos,  # noqa: E402
                            pedido_de, pedir_deixar)
from digilab.frutas import DonoPedinte, MotorFrutas, PedidoSemChave, genoma_frutas, reproduzir_frutas  # noqa: E402
from digilab.policy import Observacao  # noqa: E402
from digilab.protocol import pedido_nao_referendados, validar_parametros_pedido  # noqa: E402

CP = CONFIG_PEDIDO_LIGADA
PEDIDOS = {a.value for a in ACOES_PEDIDO}


class _Espia:
    """politica que anota o que viu (com o tick do motor) e o que chegou por `receber_acao_dono`, e delega"""

    def __init__(self, interna, motor_ref: list) -> None:
        self.interna = interna
        self.motor_ref = motor_ref
        self.vistas: list[tuple[int, Observacao]] = []
        self.recebidas: list[tuple[str, int]] = []

    def agir(self, obs, rng):
        self.vistas.append((self.motor_ref[0]._estado.tick, obs))
        return self.interna.agir(obs, rng)

    def receber_acao_dono(self, acao, tick) -> None:
        self.recebidas.append((acao.value, tick))
        self.interna.receber_acao_dono(acao, tick)

    def __getattr__(self, nome):
        interna = self.__dict__.get("interna")
        if interna is None:
            raise AttributeError(nome)
        return getattr(interna, nome)


def _vida(cerebro="instinto", dono="atencioso", s=11, cp=CP, pedinte=None, dias=DIAS, orc=ORC, espiar=False, informa=False):
    motor_ref: list = []
    espias: list = []

    def fab(cfg=None):
        p = CEREBROS[cerebro](cfg)
        if espiar:
            p = _Espia(p, motor_ref)
            espias.append(p)
        return p

    fp, fm0 = fabricas_frutas(cfg_frutas=CF, cfg_informacao=CI if informa else None, politica_fabrica=fab, cfg_pedido=cp)

    def fm(politica, cfg, semente):
        m = fm0(politica, cfg, semente)
        motor_ref.append(m)
        return m

    inf = DonoInformante.do_genoma("certo", s, CF) if informa else None
    v = simular_vida_frutas(f"{dono}-n7", criar_dono(dono), fp(), s, dias, orc, fm, OfertasFrutas(CF), rotulo_dono=dono,
                            informante=inf, pedinte=pedinte)
    return v, fp, fm, (espias[0] if espias else None)


def _nucleo(m) -> tuple:
    return (m._estado, tuple(m.acoes_recentes(10**9)), m._rng_politica.getstate(), m._rng_ambiente.getstate(),
            m._rng_fruta.getstate(), [dict(c) for c in m.consumos], m.contagem_frutas)


def _log_sem_pedidos(m) -> str:
    return LogDeEventos([e for e in m.log if not (e.tipo == "acao_usuario" and str(e.valor) in PEDIDOS)]).para_jsonl()


# ------------------------------------------------------------------ G2


def test_g2_vidas_de_hoje_byte_a_byte():
    """48 vidas (instinto e lobos aprendendo, com e sem o informante do N5) iguais ao gabarito gravado antes do pedido existir
    (commit anterior a este codigo). As 168 vidas da bancada seguem em tests/test_frutas_cenario.py."""
    gab = json.loads(GABARITO.read_text(encoding="utf-8"))
    casos = dict(_casos())
    assert set(gab) == set(casos) and len(gab) == 48
    for chave, caso in casos.items():
        assert _impressao(_vida_de_hoje(*caso)[0].motor) == gab[chave], chave


@pytest.mark.parametrize("cerebro", ("instinto", "lobos"))
def test_g2_chave_ligada_sem_pedido_e_a_vida_de_hoje(cerebro):
    for dono in DONOS:
        lig, _, _, _ = _vida(cerebro, dono, 22, cp=CP)
        des, _, _, _ = _vida(cerebro, dono, 22, cp=None)
        assert lig.motor.log.para_jsonl() == des.motor.log.para_jsonl()
        assert _nucleo(lig.motor) == _nucleo(des.motor)
        assert lig.motor.politica.estado_interno() == des.motor.politica.estado_interno()
        assert lig.motor.pedidos == [] and lig.motor.decisoes_com_pedido == 0


def test_padrao_neutro_e_de_estado_nao_preenche():
    o = Observacao(vetor_estado=(0.5,) * 8, ticks_desde_cuidado=0, total_cuidados=0)
    assert o.pedido_frutas == (0.0,) * len(FRUTAS)
    v, _, _, espia = _vida("instinto", "atencioso", 11, cp=None, espiar=True)
    assert espia.vistas and all(o.pedido_frutas == (0.0,) * len(FRUTAS) for _, o in espia.vistas)


# ------------------------------------------------------------------ o pedido nao altera o estado nem o orcamento


@pytest.mark.parametrize("dono", DONOS)
def test_pedido_nao_muda_a_vida_do_instinto_nem_o_orcamento(dono):
    """O instinto nao le o pedido: com o dono que pede (sem bronca) a vida e a mesma (estado, acoes, rngs, consumos); o log so ganha os
    pedidos; o canal fecha os mesmos 48; e a rng do pedido nao mexe nas outras."""
    for s in SEMENTES:
        p = DonoPedinte.da_semente(s, CP)
        com, _, _, _ = _vida("instinto", dono, s, pedinte=p)
        sem, _, _, _ = _vida("instinto", dono, s)
        assert _nucleo(com.motor) == _nucleo(sem.motor)
        assert _log_sem_pedidos(com.motor) == sem.motor.log.para_jsonl()
        assert com.interacoes == sem.interacoes == ORC and com.pedidos == len(p.feitas) > 0 and com.broncas == 0


def test_evento_de_pedido_nao_mexe_no_estado_nem_e_contato():
    m = MotorFrutas(PoliticaInstintoFrutas(None, None, CF), None, 11, cfg_frutas=CF, cfg_pedido=CP)
    m.avancar(600)
    antes = m._estado
    for f in FRUTAS:
        m.observar(pedir_deixar(f))
    assert m._estado == antes                                   # nem fome, nem humor, nem tick_ultimo_cuidado, nem total_cuidados
    assert m.pedido_vigente() == (-1.0, -1.0, -1.0) and [p["fruta"] for p in m.pedidos] == list(FRUTAS)
    m.avancar(CP.janela_min - 1)
    assert m.pedido_vigente() == (-1.0, -1.0, -1.0)
    m.avancar(1)
    assert m.pedido_vigente() == (0.0, 0.0, 0.0)


def test_pedido_nao_chega_ao_aprendiz():
    for cerebro in ("instinto", "lobos"):
        v, _, _, espia = _vida(cerebro, "atencioso", 33, pedinte=DonoPedinte.da_semente(33, CP), espiar=True)
        assert v.pedidos > 0 and not any(a in PEDIDOS for a, _ in espia.recebidas)


# ------------------------------------------------------------------ a percepcao


@pytest.mark.parametrize("dono", DONOS)
def test_percepcao_do_pedido_decisao_a_decisao(dono):
    """`pedido_frutas` e -1 exatamente nas frutas com um pedido de tick <= t < tick + janela, no tick de cada decisao; pedir de novo
    renova (o prazo do ultimo pedido vale)."""
    for s in SEMENTES:
        v, _, _, espia = _vida("instinto", dono, s, pedinte=DonoPedinte.da_semente(s, CP), espiar=True)
        pedidos = v.motor.pedidos
        assert pedidos
        com_pedido = 0
        for t, obs in espia.vistas:
            esperado = tuple(-1.0 if any(p["fruta"] == f and p["tick"] <= t < p["prazo"] for p in pedidos) else 0.0 for f in FRUTAS)
            assert obs.pedido_frutas == esperado, t
            com_pedido += any(x != 0.0 for x in esperado)
        assert com_pedido == v.motor.decisoes_com_pedido > 0


# ------------------------------------------------------------------ as fases e o sorteio da fruta


def test_sorteio_da_fruta_pela_semente_independente_do_genoma():
    contagem = {f: 0 for f in FRUTAS}
    igual_a_preferida = 0
    antes = random.getstate()
    for s in range(1, 601):
        x = DonoPedinte.sortear_fruta(s)
        assert x == DonoPedinte.da_semente(s, CP).fruta == DonoPedinte.sortear_fruta(s)
        contagem[x] += 1
        igual_a_preferida += x == genoma_frutas(s, CF).fruta_preferida()
    assert random.getstate() == antes
    assert all(150 <= c <= 250 for c in contagem.values()), contagem          # uniforme: ~200 cada
    assert 150 <= igual_a_preferida <= 250                                     # nao segue a preferencia inata: ~1/3


def test_fases_pedidos_nos_dias_1_a_10_e_extincao_nos_11_a_14():
    """Vida de 14 dias, a configuracao do plano: um pedido logo depois de toda oferta que tem X ate o fim do dia 10 (no mesmo tick da
    oferta), e nenhum pedido nos dias 11-14, com ofertas de X continuando."""
    for s in (11, 22):
        p = DonoPedinte.da_semente(s, CP)
        v, _, _, _ = _vida("instinto", "atencioso", s, pedinte=p, dias=14, orc=224)
        ofertas_x = [e.tick for e in v.motor.log if e.tipo == "acao_usuario" and e.valor == f"oferecer_fruta_{p.fruta}"]
        pedidos = [e.tick for e in v.motor.log if e.tipo == "acao_usuario" and str(e.valor) in PEDIDOS]
        fim = CONFIG_PEDIDO.dias_pedido * TICKS_POR_DIA
        assert CONFIG_PEDIDO.dias_pedido == 10 and fim == 14400
        assert pedidos == [t for t in ofertas_x if t < fim] and pedidos
        assert any(t >= fim for t in ofertas_x) and all(t < fim for t in pedidos)
        assert all(f == p.fruta for _, f in p.feitas) and [t for t, _ in p.feitas] == pedidos
        # o pedido vem logo depois da oferta de X no log (so o informante poderia ficar no meio; aqui nao ha)
        evs = list(v.motor.log)
        for i, e in enumerate(evs):
            if e.tipo == "acao_usuario" and str(e.valor) in PEDIDOS:
                anteriores = [x for x in evs[:i] if x.tipo == "acao_usuario" and x.tick == e.tick]
                assert anteriores and str(anteriores[-1].valor).startswith("oferecer_fruta_")
        assert all(pr["prazo"] <= fim + CP.janela_min for pr in v.motor.pedidos)


# ------------------------------------------------------------------ a bronca (so no P3+ped)


@pytest.mark.parametrize("dono", DONOS)
def test_bronca_so_com_a_chave_e_no_primeiro_passo_depois_da_desobediencia(dono):
    """Com `bronca`, cada desobediencia (comer uma fruta com pedido vigente na decisao) leva uma `repreender` no primeiro passo do dono
    depois dela, fora do orcamento, e ela chega ao aprendiz; sem `bronca`, nenhuma."""
    total_desob = 0
    for s in SEMENTES:
        p = DonoPedinte.da_semente(s, CP, bronca=True)
        v, _, _, espia = _vida("lobos", dono, s, pedinte=p, espiar=True)
        desob = v.motor.desobediencias
        total_desob += len(desob)
        assert len(p.broncas) == len(desob) == v.broncas and v.interacoes == ORC
        for d, t in zip(desob, p.broncas):
            # a decisao do tick d vem no avanco que comeca depois do passo do dono em d: o primeiro passo depois dela e o seguinte
            assert 0 < t - d["tick"] <= 15 and t % 15 == 0
            assert d["fruta"] == p.fruta
            assert ("repreender", t) in espia.recebidas
        # sem bronca: nenhuma repreensao extra
        q = DonoPedinte.da_semente(s, CP, bronca=False)
        w, _, _, _ = _vida("instinto", dono, s, pedinte=q)
        assert w.broncas == 0 and q.broncas == []
    assert total_desob > 0


def test_desobediencia_e_a_percepcao_da_decisao():
    """A desobediencia e um consumo de fruta que tinha -1 em `pedido_frutas` na decisao em que o pet comeu."""
    v, _, _, espia = _vida("instinto", "atencioso", 11, pedinte=DonoPedinte.da_semente(11, CP), espiar=True)
    vistas = dict(espia.vistas)
    desob = {(d["tick"], d["fruta"]) for d in v.motor.desobediencias}
    assert desob
    for c in v.motor.consumos:
        obs = vistas[c["tick"]]
        assert ((c["tick"], c["fruta"]) in desob) == (obs.pedido_frutas[FRUTAS.index(c["fruta"])] < 0.0)


# ------------------------------------------------------------------ G1


def test_g1_replay_com_pedidos_e_broncas():
    for cerebro, bronca in (("instinto", False), ("lobos", True)):
        for dono in DONOS:
            v, fp, fm, _ = _vida(cerebro, dono, 22, pedinte=DonoPedinte.da_semente(22, CP, bronca=bronca), informa=True)
            r = reproduzir_frutas(LogDeEventos.de_jsonl(v.motor.log.para_jsonl()), fp, semente=22, fabrica_motor=fm)
            assert _impressao(r) == _impressao(v.motor)
            assert r.pedidos == v.motor.pedidos and r.desobediencias == v.motor.desobediencias


# ------------------------------------------------------------------ contrato


def test_falha_alto_fora_do_contrato():
    m = MotorFrutas(PoliticaInstintoFrutas(None, None, CF), None, 11, cfg_frutas=CF)
    with pytest.raises(PedidoSemChave):
        m.observar(pedir_deixar("a"))
    with pytest.raises(ValueError):
        MotorFrutas(None, None, 11, cfg_frutas=CONFIG_FRUTAS, cfg_pedido=CP)
    with pytest.raises(ValueError):
        DonoPedinte("d")
    with pytest.raises(ValueError):
        pedir_deixar("d")
    with pytest.raises(ValueError):
        pedido_de(AcaoUsuario.ALIMENTAR)
    with pytest.raises(KeyError):                                 # o dono que pede num motor sem a chave
        _vida("instinto", "atencioso", 11, cp=None, pedinte=DonoPedinte.da_semente(11, CP))


def test_enum_cresce_no_fim_e_parametros_registrados():
    todos = list(AcaoUsuario)
    assert todos[26:29] == list(ACOES_PEDIDO) and [pedido_de(a) for a in ACOES_PEDIDO] == list(FRUTAS)
    assert todos.index(ACOES_INFORMACAO[0]) == 20 and todos.index(ACOES_FRUTAS[0]) == 17     # as de antes nao andaram
    validar_parametros_pedido()
    assert pedido_nao_referendados() == ["ConfigPedido.janela_min", "ConfigPedido.dias_pedido"]
    assert CONFIG_PEDIDO.ligada is False and CONFIG_PEDIDO == ConfigPedido() and CP.janela_min == 240
