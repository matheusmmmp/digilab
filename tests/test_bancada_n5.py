"""V2, BANCADA-N5 (docs/TAREFA_V2_BANCADA_N5.md): os lobos vendo o mundo pela bancada e a fonte `informacao` (P2, P2e, P2a).

Gates: G1 de toda vida nova; aprendizado desligado nos mundos da bola e das frutas = o instinto que ve o mundo, byte a byte pela
bancada; P2 sem nenhuma informacao no registro = P1 byte a byte (G2 do plano do N5); P2 e P2e com informacoes nos mesmos ticks; o
aprendiz nunca recebe a informacao como sinal (espiao). Sementes: so as dos testes (101...505)."""

import json
import sys
from collections import Counter
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
from digilab.config import CONFIG_FRUTAS_LIGADA, TICKS_POR_DIA  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.events import ACOES_INFORMACAO, FRUTAS, LogDeEventos  # noqa: E402
from digilab.metrics import consumos_ate_metade, tabela_braco_condicao_parcial  # noqa: E402
from digilab.policies import PoliticaLobos  # noqa: E402

DONOS = ("atencioso", "relapso", "aleatorio", "incoerente")
DIAS, ORC = 4, 64
BANCADA = bv.Bancada(DIAS, ORC)
SONDA = {"estados": 20, "amostras": 20, "semente": 101}
MUNDOS_FRUTAS = ("casado_frutas", "descasado", "mutavel")
INFO = {a.value for a in ACOES_INFORMACAO}


def _info(log) -> list[tuple[int, str]]:
    return [(e.tick, str(e.valor)) for e in log if e.tipo == "acao_usuario" and str(e.valor) in INFO]


def _ofertas(log) -> list[tuple[int, str]]:
    return [(e.tick, str(e.valor)) for e in log if e.tipo == "acao_usuario" and str(e.valor).startswith("oferecer_fruta_")]


def _interno_cerebro(motor) -> str:
    return json.dumps(bv.do_braco(motor.politica).cerebro.estado_interno(), sort_keys=True)


def _vida(dono="atencioso", braco="P2", s=101, mundo="descasado", genoma=None, cerebro="lobos"):
    return BANCADA.vida(bv.EspecVida(dono, braco, s, genoma, mundo, cerebro))


# ------------------------------------------------------------------ gate: os lobos veem o mundo pela bancada


@pytest.mark.parametrize("mundo", ["bola", "bola_a1"] + list(MUNDOS_FRUTAS))
def test_p0_lobos_e_o_instinto_que_ve_o_mundo_byte_a_byte(mundo):
    """Aprendizado desligado = o instinto que ve a bola (PoliticaInstintoBola) ou as frutas (PoliticaInstintoFrutas), pela bancada:
    log, estado, acoes, rngs e, nas frutas, as escolhas, os consumos, os incentivos e a rng da fruta (resumo_frutas)."""
    for dono in DONOS:
        for s, g in ((101, None), (303, 303)):
            lob = _vida(dono, "P0", s, mundo, g, "lobos")
            ins = _vida(dono, "P0", s, mundo, g, "instinto")
            assert bv.resumo_motor(lob.motor) == bv.resumo_motor(ins.motor), (mundo, dono, s)
            cer = bv.do_braco(lob.motor.politica).cerebro
            assert cer._ve_mundo and not cer.pesos_mudaram()


def test_no_mundo_padrao_os_lobos_continuam_sem_o_mundo():
    v = _vida("atencioso", "P3", 101, "padrao")
    cer = bv.do_braco(v.motor.politica).cerebro
    assert not cer._ve_mundo and cer.estado_interno()["entradas"] == list(PoliticaLobos().estado_interno()["entradas"])
    ref = bv.simular_vida("atencioso-P3", criar_dono("atencioso"), PoliticaLobos(None, BANCADA.cfg_lobos), 101, DIAS, ORC,
                          rotulo_dono="atencioso")
    assert bv.resumo_motor(ref.motor) == bv.resumo_motor(v.motor)


def test_os_lobos_que_aprendem_escolhem_a_fruta():
    """Com os lobos vendo as frutas, o P1 (consequencia com a E2) come fruta e credita o sinal da fruta."""
    v = _vida("atencioso", "P1", 202, "descasado")
    rec = bv.do_braco(v.motor.politica).cerebro.estado_interno()["aprendizado"]["recompensas"]
    assert v.motor.consumos and rec.get("consequencia_fruta", 0) == len(v.motor.consumos)


# ------------------------------------------------------------------ gate: G2 do plano do N5


@pytest.mark.parametrize("braco", ["P2", "P2e", "P2a"])
def test_p2_sem_nenhuma_informacao_no_registro_e_o_p1(braco):
    """O braco de informacao sem informante (nenhum evento de informar) e o P1 byte a byte: mesmo aprendiz, mesmo sinal, a entrada
    da informacao em zero."""
    for dono, s, g, mundo in (("atencioso", 101, None, "descasado"), ("aleatorio", 404, 404, "mutavel"),
                              ("incoerente", 202, None, "casado_frutas")):
        p1 = _vida(dono, "P1", s, mundo, g)
        espec = bv.EspecVida(dono, braco, s, g, mundo)
        sem = bv.simular_vida_mundo(criar_dono(dono), bv.CalendarioFrutas(s, CONFIG_FRUTAS_LIGADA), BANCADA.politica(espec),
                                    s, DIAS, ORC, dono, BANCADA.fabrica_motor(espec))
        assert not _info(sem.log)
        assert bv.resumo_motor(sem) == bv.resumo_motor(p1.motor), (braco, dono, s)
        assert _interno_cerebro(sem) == _interno_cerebro(p1.motor)


# ------------------------------------------------------------------ gate: P2 e P2e nos mesmos ticks


@pytest.mark.parametrize("mundo", MUNDOS_FRUTAS)
def test_p2_e_p2e_informam_nos_mesmos_ticks_com_conteudo_oposto(mundo):
    for dono, s, g in (("atencioso", 101, None), ("relapso", 505, 505)):
        v = {b: _vida(dono, b, s, mundo, g) for b in ("P1", "P2", "P2e", "P2a")}
        ofertas = _ofertas(v["P1"].motor.log)
        assert all(_ofertas(x.motor.log) == ofertas for x in v.values())           # as mesmas ofertas em todos os bracos
        i2, i2e, i2a = (_info(v[b].motor.log) for b in ("P2", "P2e", "P2a"))
        n_frutas = sum(1 for _ in ofertas)
        assert len(i2) == len(i2e) == len(i2a) == n_frutas > 0                      # uma informacao por fruta oferecida
        assert [t for t, _ in i2] == [t for t, _ in i2e] == [t for t, _ in ofertas]  # logo depois de cada oferta, mesmos ticks
        assert [a.split("_")[2] for _, a in i2] == [a.split("_")[2] for _, a in i2e] == [o.split("_")[2] for _, o in ofertas]
        oposto = {"bem": "mal", "mal": "bem"}
        assert all(oposto[a.split("_")[3]] == b.split("_")[3] for (_, a), (_, b) in zip(i2, i2e))
        # o P2 diz a verdade NAQUELE tick (no mutavel ela troca em tick_troca)
        ef = BANCADA.efeitos_reais(v["P2"].espec)
        for t, a in i2:
            f, c = a.split("_")[2:]
            real = ef["depois"] if ef["depois"] is not None and t >= BANCADA.tick_troca else ef["antes"]
            assert c == ("mal" if real[f] < 0 else "bem")
        # o P2a: o mesmo multiconjunto do P2, em outros ticks (sorteados pela rng propria)
        assert Counter(a for _, a in i2a) == Counter(a for _, a in i2)
        assert [t for t, _ in i2a] != [t for t, _ in i2]
        assert v["P2a"].motor.decisoes_com_informacao > 0


def test_informante_acoplado_segue_a_regra_do_plano():
    espec = bv.EspecVida("atencioso", "P2a", 303, mundo="descasado")
    a = BANCADA.informante(espec)
    b = BANCADA.informante(espec)
    assert a.agenda == b.agenda and isinstance(a, bv.InformanteAcoplado)          # deterministico pela semente
    certo = BANCADA.informante(bv.EspecVida("atencioso", "P2", 303, mundo="descasado"))
    passos = DIAS * TICKS_POR_DIA // bv.CONFIG_DONOS.passo_ticks
    # o multiconjunto do acoplado e o que o certo diria nas ofertas do calendario
    cal = bv.CalendarioFrutas(303, CONFIG_FRUTAS_LIGADA)
    for p in range(passos):
        t = (p + 1) * bv.CONFIG_DONOS.passo_ticks
        ofertas = cal.decidir(bv.Visao(estado={"tick": t}, passo=p, passos_totais=passos, orcamento=0, gasto=0,
                                       minimo_obrigatorio=0, maximo_permitido=0), [])
        certo.acoes(t, [bv.fruta_de(o) for o in ofertas])
    assert Counter((f, c) for _, f, c in certo.feitas) == Counter((f, c) for _, f, c in a.itens)
    assert all(t % bv.CONFIG_DONOS.passo_ticks == 0 and 0 < t <= DIAS * TICKS_POR_DIA for t in a.agenda)
    with pytest.raises(ValueError):
        BANCADA.informante(bv.EspecVida("atencioso", "P1", 303, mundo="descasado"))


# ------------------------------------------------------------------ gate: a informacao nunca chega ao aprendiz


@pytest.mark.parametrize("braco", ["P2", "P2e", "P2a"])
def test_a_informacao_nunca_chega_ao_aprendiz_como_sinal(braco):
    for dono, s in (("atencioso", 101), ("incoerente", 303)):
        espec = bv.EspecVida(dono, braco, s, mundo="descasado")
        espiao = bv._Espiao(BANCADA.politica(espec))
        regra = bv.RegraFrutasComInformante(bv.CalendarioFrutas(s, CONFIG_FRUTAS_LIGADA), BANCADA.informante(espec))
        m = bv.simular_vida_mundo(criar_dono(dono), regra, espiao, s, DIAS, ORC, dono, BANCADA.fabrica_motor(espec))
        assert _info(m.log)
        assert espiao.recebidas and not any(a in INFO for a, _ in espiao.recebidas)   # o gancho do dono so ve o cuidado
        v = BANCADA.vida(espec)
        assert bv.resumo_motor(m) == bv.resumo_motor(v.motor)                         # o espiao nao muda nada
        rec = bv.do_braco(v.motor.politica).cerebro.estado_interno()["aprendizado"]["recompensas"]
        assert rec["elogio"] == rec["repreensao"] == rec["latencia"] == rec["ignorado"] == 0   # nada do dono chega
        assert rec["consequencia"] > 0


# ------------------------------------------------------------------ G1, acoplado, orcamento


def test_g1_e_acoplado_com_a_informacao():
    vidas = [_vida(d, b, s, m, g) for m in MUNDOS_FRUTAS for d in ("atencioso", "aleatorio") for s, g in ((101, None), (202, 202))
             for b in ("P1", "P2", "P2e", "P2a")]
    acop = []
    for v in vidas:
        if v.espec.braco == "P2":
            acop.append(BANCADA.acoplar(v, "P2", "sem_ensino"))
            acop.append(BANCADA.acoplar(v, "P1", "nenhum"))                     # o P1 no registro com a informacao
    for v in vidas + acop:
        BANCADA.conferir_replay(v)
        r = BANCADA.rejogar(LogDeEventos.de_jsonl(v.motor.log.para_jsonl()), v.espec)
        assert bv.resumo_motor(r) == bv.resumo_motor(v.motor) and r.estado() == v.motor.estado()
    for v in vidas:
        n_dono, n_mundo = bv.contar_acoes(v.motor.log)
        assert n_dono == ORC == v.interacoes                                        # a informacao fica fora do orcamento
        assert v.informacoes == len(_info(v.motor.log)) == (0 if v.espec.braco == "P1" else n_mundo)
    so_cuidado = [a for a in acop if a.filtro == "sem_ensino"]
    for a in so_cuidado:
        assert not _info(a.motor.log) and _ofertas(a.motor.log) and a.rotulo_braco == "P2<P2:sem_ensino"
    with pytest.raises(bv.ReplayDivergiu):
        BANCADA.conferir_replay(bv.VidaBancada(vidas[2].espec, vidas[1].motor, ORC))


def test_filtros_da_informacao():
    assert bv.FILTROS["sem_informacao"] == bv.INFORMACOES and bv.FILTROS["sem_ensino"] == bv.SINAIS | bv.INFORMACOES | bv.PEDIDOS
    assert not any(f & bv.EVENTOS_DO_MUNDO for f in bv.FILTROS.values())
    assert bv.INFORMACOES <= bv.FORA_DO_ORCAMENTO and not bv.INFORMACOES & bv.EVENTOS_DO_MUNDO


# ------------------------------------------------------------------ medidas do N5


def test_consumos_ate_metade():
    r = consumos_ate_metade([0.6, None, 0.2, 0.1], [5, 0, 4, 6], 0.5)
    assert r["dia"] == 2 and r["consumos"] == 9 and not r["censurado"] and abs(r["alvo"] - 0.25) < 1e-12
    c = consumos_ate_metade([0.6, 0.5, None], [3, 4, 0], 0.5)
    assert c["censurado"] and c["consumos"] == 7 == c["total"] and c["dia"] is None
    assert consumos_ate_metade([0.2], [3], None)["sem_referencia"]
    with pytest.raises(ValueError):
        consumos_ate_metade([0.2], [3, 4], 0.5)
    with pytest.raises(ValueError):
        consumos_ate_metade([0.2], [3], 1.5)


def test_tabela_parcial():
    t = tabela_braco_condicao_parcial({("P1", "d"): [0.2, None, 0.4], ("P2", "d"): [0.1, None]}, 200, 1, 0.95)
    assert t["celulas"]["P1"]["d"]["n"] == 2 and t["celulas"]["P1"]["d"]["sem_valor"] == 1 and t["celulas"]["P1"]["d"]["ic"]
    assert t["celulas"]["P2"]["d"]["ic"] is None and t["celulas"]["P2"]["d"]["media"] == 0.1
    with pytest.raises(ValueError, match="incompleta"):
        tabela_braco_condicao_parcial({("P1", "a"): [1.0], ("P2", "b"): [1.0]}, 200, 1, 0.95)


def test_rodar_com_os_bracos_do_n5(tmp_path):
    cfg = {"descricao": "fumaca de teste, nao canonica", "bracos": ["P0", "P1", "P2", "P2e", "P2a"], "donos": ["atencioso"],
           "unidades": {"bases": [101, 202, 303], "k": 1}, "mundos": ["descasado"], "dias": DIAS, "orcamento": ORC,
           "sonda": {"estados": 10, "amostras": 10, "semente": 101},
           "bootstrap": {"reamostragens": 200, "semente": 101, "nivel": 0.95},
           "acoplados": [{"origem": "P2", "destino": "P2", "filtro": "sem_ensino"}]}
    r = bv.rodar(cfg, tmp_path)
    t = json.loads((tmp_path / "tabelas.json").read_text(encoding="utf-8"))["atencioso"]
    for medida in bv.MEDIDAS_FRUTAS:
        assert t[medida]["bracos"] == ["P0", "P1", "P2", "P2<P2:sem_ensino", "P2a", "P2e"]
        assert t[medida]["condicoes"] == ["descasado/descasado"]
    p0 = {(m["semente"], m["genoma"]): m for m in r["medidas"].values() if m["braco"] == "P0"}
    for m in r["medidas"].values():
        cm = m["frutas"]["consumos_ate_metade"]
        ref = p0[(m["semente"], m["genoma"])]["frutas"]["taxa_fruta_ruim"]["total"]["taxa"]
        if ref is None:
            assert cm["sem_referencia"]
        else:                                                  # metade do caminho entre o P0 da mesma unidade e 0
            assert abs(cm["alvo"] - ref / 2) < 1e-12 and cm["consumos"] <= cm["total"]
        assert m["informacoes"] == len(m["frutas"]["informacoes"])
        assert m["unidade"] is not None
