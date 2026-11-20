"""BANCADA-N6-N7 (docs/TAREFA_V2_BANCADA_N6_N7.md): as faixas do N7, o mundo iguais_frutas (N7-5), os bracos do N6 e do N7 (que falham
alto com o no enquanto a memoria e o pedido nao estao na main), o desarranjo do ME (N6-6), o prefixo das unidades derivadas e as medidas
dos dois planos em dados sinteticos. So as sementes dos testes."""

import random
import sys
from collections import Counter
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
from digilab.config import CONFIG_FRUTAS_LIGADA, TICKS_POR_DIA  # noqa: E402
from digilab.events import FRUTAS, LogDeEventos  # noqa: E402
from digilab.metrics import (ZONAS_CONFLITO, deferencia_ao_pedido, dia_cruza_zero, fracao_da_fruta,  # noqa: E402
                             memoria_nas_subdecisoes, ocupacao_espacos_frutas, quem_decidiu_conflito)
from digilab.protocol import derivar_semente  # noqa: E402

DIAS, ORC = 4, 64
BANCADA = bv.Bancada(DIAS, ORC)
DONOS = ("atencioso", "relapso", "aleatorio", "incoerente")
MUNDOS_FRUTAS = ("casado_frutas", "descasado", "mutavel", "iguais_frutas")
SONDA = {"estados": 5, "amostras": 5, "semente": 101}


def _vida(dono="atencioso", braco="P0", s=101, mundo="iguais_frutas", genoma=None, cerebro="lobos"):
    return BANCADA.vida(bv.EspecVida(dono, braco, s, genoma, mundo, cerebro))


def _ofertas(log):
    return [(e.tick, str(e.valor)) for e in log if e.tipo == "acao_usuario" and str(e.valor).startswith("oferecer_fruta_")]


# ------------------------------------------------------------------ faixas e unidades


def test_faixas_do_n7_e_prefixos_das_unidades():
    for s in (21101, 21505, 22101, 22505):
        assert "N7" in bv.na_faixa_reservada(s)
    los = sorted((lo, hi) for lo, hi, _ in bv.FAIXAS_RESERVADAS)
    assert all(a[1] < b[0] for a, b in zip(los, los[1:]))                                  # disjuntas
    for bases in (bv.BASES_N6, bv.BASES_N7, bv.BASES_EXPERIMENTO_MAIOR):
        assert all(bv.na_faixa_reservada(b) for bs in bases.values() for b in bs)
    # a regra E3 com o prefixo de cada plano (N6 e N7, secao 12.2); o padrao continua o do experimento maior
    u = bv.unidades_derivadas((19101,), 3, "n6")[2]
    assert (u["semente"], u["genoma"]) == (derivar_semente("n6", 19101, 2), derivar_semente("n6-genoma", 19101, 2))
    u = bv.unidades_derivadas((21101,), 1, "n7")[0]
    assert (u["semente"], u["genoma"]) == (derivar_semente("n7", 21101, 0), derivar_semente("n7-genoma", 21101, 0))
    assert bv.unidades_derivadas((14101,), 2) == bv.unidades_derivadas((14101,), 2, "experimento-maior")
    todos = []
    for prefixo, bases in (("n6", bv.BASES_N6), ("n7", bv.BASES_N7), ("experimento-maior", bv.BASES_EXPERIMENTO_MAIOR)):
        for fase in ("calibracao", "validacao"):
            for x in bv.unidades_derivadas(bases[fase], 40, prefixo):
                todos += [x["semente"], x["genoma"]]
    assert len(set(todos)) == len(todos)                                                    # nenhuma colisao entre planos e fases
    assert not any(bv.na_faixa_reservada(v) or v in bv.SEMENTES_TESTE for v in todos)
    with pytest.raises(ValueError):
        bv.unidades_derivadas((19101,), 1, "n8")
    cfg = {"bracos": ["P0"], "donos": ["atencioso"], "unidades": {"bases": [101], "k": 1, "prefixo": "n7"}, "dias": 1,
           "orcamento": 16, "sonda": SONDA, "bootstrap": {}, "mundos": ["iguais_frutas"]}
    bv.validar_config(cfg)
    with pytest.raises(ValueError):
        bv.validar_config({**cfg, "unidades": {"bases": [101], "k": 1, "prefixo": "xx"}})
    with pytest.raises(bv.SementeSemPlano):                                                 # a fumaca recusa as faixas sem plano
        bv.validar_config({**cfg, "unidades": {"bases": [21101], "k": 1, "prefixo": "n7"}})


# ------------------------------------------------------------------ o mundo iguais_frutas (N7-5)


def test_iguais_frutas_tem_as_mesmas_ofertas_dos_outros_mundos_das_frutas():
    assert bv.mundo_de("iguais_frutas").condicao == "iguais" and bv.mundo_de("iguais_frutas").frutas
    for dono in DONOS:
        for s, g in ((101, None), (303, 303)):
            ofertas = {m: _ofertas(_vida(dono, "P0", s, m, g).motor.log) for m in MUNDOS_FRUTAS}
            assert ofertas["iguais_frutas"] and all(o == ofertas["iguais_frutas"] for o in ofertas.values()), (dono, s)
    # e em todos os bracos que rodam
    o = {b: _ofertas(_vida("atencioso", b, 202).motor.log) for b in ("P0", "P1", "P2", "P2e", "P2a", "P3")}
    assert all(x == o["P0"] for x in o.values())


def test_iguais_frutas_todas_com_o_efeito_neutro():
    v = _vida("atencioso", "P1", 202, "iguais_frutas", 202)
    neutro = CONFIG_FRUTAS_LIGADA.efeito_humor_neutro
    assert v.motor.resumo_mundo()["efeitos"] == {"iguais": {f: neutro for f in FRUTAS}}
    assert v.motor.consumos and all(c["efeito_humor"] == neutro for c in v.motor.consumos)
    assert BANCADA.efeitos_reais(v.espec) == {"antes": {f: neutro for f in FRUTAS}, "depois": None}
    # o informante do P2 diz "bem" de toda fruta (nenhuma faz mal); o P2e, "mal"
    p2, p2e = _vida("atencioso", "P2", 202, "iguais_frutas"), _vida("atencioso", "P2e", 202, "iguais_frutas")
    info = lambda v: [str(e.valor) for e in v.motor.log if str(e.valor).startswith("informar_")]  # noqa: E731
    assert info(p2) and all(x.endswith("_bem") for x in info(p2)) and all(x.endswith("_mal") for x in info(p2e))
    # so o mutavel troca; o iguais com tick_troca falha alto
    with pytest.raises(ValueError):
        bv.efeitos_da_condicao(v.motor.genoma, CONFIG_FRUTAS_LIGADA, "outra")
    m = BANCADA.medir(v, SONDA)
    assert m["condicao"] == "iguais" and m["frutas"]["taxa_fruta_ruim"]["total"]["taxa"] == 0.0
    assert m["frutas"]["consumos_ate_metade"]["sem_referencia"]                               # sem fruta ruim, sem caminho


def test_iguais_frutas_p0_lobos_e_o_instinto_e_g1():
    for dono in DONOS:
        for s, g in ((101, None), (404, 404)):
            lob, ins = _vida(dono, "P0", s, "iguais_frutas", g), _vida(dono, "P0", s, "iguais_frutas", g, "instinto")
            assert bv.resumo_motor(lob.motor) == bv.resumo_motor(ins.motor), (dono, s)
    vidas = [_vida(d, b, s, "iguais_frutas", g) for d in ("atencioso", "aleatorio") for s, g in ((101, None), (202, 202))
             for b in ("P0", "P1", "P2", "P2a", "P3")]
    acop = [BANCADA.acoplar(v, "P0", "sem_ensino") for v in vidas if v.espec.braco in ("P2", "P3")]
    for v in vidas + acop:
        BANCADA.conferir_replay(v)                                                            # G1
        r = BANCADA.rejogar(LogDeEventos.de_jsonl(v.motor.log.para_jsonl()), v.espec)
        assert bv.resumo_motor(r) == bv.resumo_motor(v.motor)
    for a in acop:                                                                            # o acoplado guarda as ofertas
        assert _ofertas(a.motor.log) == _ofertas(next(v for v in vidas if v.nome == a.origem).motor.log)


def test_iguais_frutas_na_tabela(tmp_path):
    cfg = {"bracos": ["P0", "P1"], "donos": ["atencioso"], "sementes": [101, 202], "mundos": ["iguais_frutas", "descasado"],
           "dias": 2, "orcamento": 32, "sonda": SONDA, "bootstrap": {"reamostragens": 200, "semente": 101, "nivel": 0.95}}
    r = bv.rodar(cfg, tmp_path)
    t = r["tabelas"]["atencioso"]
    assert "iguais/iguais_frutas" in t["saude_media"]["condicoes"] and "descasado/descasado" in t["saude_media"]["condicoes"]
    assert t["consumos_ate_metade"]["celulas"]["P1"]["iguais/iguais_frutas"]["sem_valor"] == 2


# ------------------------------------------------------------------ os bracos do N6 e do N7 (desde a BANCADA-LIGA-N6-N7 eles rodam)


@pytest.mark.parametrize("braco,no", [("M0", "N6"), ("MR", "N6"), ("MT", "N6"), ("ME", "N6"),
                                      ("P0+ped", "N7"), ("P1+ped", "N7"), ("P3+ped", "N7")])
def test_bracos_do_n6_e_do_n7_rodam_e_a_trava_falha_alto_com_o_no(braco, no, monkeypatch):
    """A memoria e o pedido estao na main (#166, #167): os bracos se resolvem, na config e na vida. A trava continua sendo uma
    tabela so (NOS_PENDENTES): com a entrada de volta, o braco falha alto com o no (tests/test_bancada_liga_n6_n7.py roda os bracos)."""
    b = bv.BRACOS[braco]
    assert b.no == no and bv.braco_de(braco) is b and not {"memoria", "pedido"} & set(bv.NOS_PENDENTES)   # W-BANCADA-MUNDO: o do mundo
    cfg = {"bracos": ["P0", braco], "donos": ["atencioso"], "sementes": [101], "dias": 1, "orcamento": 16, "sonda": SONDA,
           "bootstrap": {}, "mundos": ["iguais_frutas" if no == "N7" else "descasado"]}
    bv.validar_config(cfg)
    peca = "pedido" if no == "N7" else "memoria"
    monkeypatch.setattr(bv, "NOS_PENDENTES", {peca: f"{no}: peca de outro chat"})
    with pytest.raises(NotImplementedError, match=no):
        bv.braco_de(braco)
    with pytest.raises(NotImplementedError, match=no):
        bv.validar_config(cfg)


def test_os_bracos_seguem_o_plano():
    """Os campos dos bracos dizem o que o plano diz: N6 sem aprendizado do lobo de decisao (fonte nenhuma) e uma memoria por braco;
    N7 com o pedido e a fonte do braco de origem."""
    mem = {b: bv.BRACOS[b].memoria for b in ("M0", "MR", "MT", "ME")}
    assert mem == {"M0": "nenhuma", "MR": "relevante", "MT": "recencia", "ME": "embaralhada"}
    assert all(bv.BRACOS[b].fonte == "nenhuma" for b in mem)
    assert {b: bv.BRACOS[b].fonte for b in ("P0+ped", "P1+ped", "P3+ped")} == {"P0+ped": "nenhuma", "P1+ped": "consequencia",
                                                                                 "P3+ped": "dono"}
    assert all(bv.BRACOS[b].pedido for b in ("P0+ped", "P1+ped", "P3+ped")) and not bv.BRACOS["P3"].pedido


def test_filtros_do_pedido(monkeypatch):
    assert bv.filtro_de("sem_pedido") == bv.PEDIDOS and bv.PEDIDOS
    assert bv.filtro_de("sem_ensino_sem_pedido") == bv.FILTROS["sem_ensino"] == bv.SINAIS | bv.INFORMACOES | bv.PEDIDOS
    with pytest.raises(KeyError):
        bv.filtro_de("nao_existe")
    cfg = {"bracos": ["P3"], "donos": ["atencioso"], "sementes": [101], "dias": 1, "orcamento": 16, "sonda": SONDA, "bootstrap": {},
           "mundos": ["iguais_frutas"], "acoplados": [{"origem": "P3", "destino": "P0", "filtro": "sem_ensino_sem_pedido"}]}
    bv.validar_config(cfg)
    with pytest.raises(ValueError):
        bv.validar_config({**cfg, "acoplados": [{"origem": "P3", "destino": "P0", "filtro": "nao_existe"}]})
    # a trava dos filtros continua: um filtro pendente falha alto com o no
    monkeypatch.setattr(bv, "NOS_PENDENTES", {"pedido": "N7: peca de outro chat"})
    monkeypatch.setattr(bv, "FILTROS_PENDENTES", {"sem_pedido": "pedido"})
    with pytest.raises(NotImplementedError, match="N7"):
        bv.filtro_de("sem_pedido")


def test_desarranjo_do_me():
    estado = random.getstate()
    pis = [bv.desarranjo_n6(s) for s in range(1, 200)]
    assert random.getstate() == estado                                                        # rng propria
    for pi in pis:
        assert sorted(pi) == sorted(pi.values()) == sorted(FRUTAS)                             # uma permutacao
        assert all(pi[f] != f for f in FRUTAS)                                                 # sem ponto fixo
    assert len({tuple(sorted(p.items())) for p in pis}) == 2                                   # os dois desarranjos aparecem
    assert bv.desarranjo_n6(101) == bv.desarranjo_n6(101)
    rng = random.Random(derivar_semente("n6-embaralha", 101))
    passo = 1 + rng.randrange(2)
    assert bv.desarranjo_n6(101) == {f: FRUTAS[(i + passo) % 3] for i, f in enumerate(FRUTAS)}


# ------------------------------------------------------------------ medidas do N6 em dados sinteticos


def test_memoria_nas_subdecisoes():
    sub = [(1, "a", "a", 1),                                       # uma fruta so: a memoria nao pode agir
           (2, "a", "b", 2), (2, "b", "b", 1), (3, "c", "a", 0),   # 2+: mudou 2 de 3; uma sem recuperacao mudou (impossivel na
           (2, "a", "a", 0)]                                       # pratica, mas a medida so conta)
    r = memoria_nas_subdecisoes(sub, total_decisoes=100)
    assert (r["subdecisoes"], r["subdecisoes_2_mais"], r["mudou"]) == (5, 4, 2)
    assert r["fracao_decidida"] == 0.5 and r["cobertura"] == 0.5
    assert r["decisivas_entre_recuperadas"] == 0.5 and r["fracao_motivos_total"] == 0.02
    assert memoria_nas_subdecisoes([(1, "a", "a", 0)], 10)["fracao_decidida"] is None
    with pytest.raises(ValueError):
        memoria_nas_subdecisoes([(1, "a", "b", 1)], 10)                                       # com uma fruta nao muda
    with pytest.raises(ValueError):
        memoria_nas_subdecisoes([(2, "a", "b", 1)] * 3, 2)


def test_ocupacao_dos_espacos():
    inst = [(["a", "b"], ["c"]), (["a"], ["b", "c"]), ([], ["c"]), (["b"], [])]
    r = ocupacao_espacos_frutas(inst, FRUTAS)
    assert r["curto_medio"] == 1.0 and r["longo_medio"] == 1.0
    assert r["na_memoria"] == {"a": 0.5, "b": 0.75, "c": 0.75} and r["no_longo"] == {"a": 0.0, "b": 0.25, "c": 0.75}
    with pytest.raises(ValueError):
        ocupacao_espacos_frutas([(["a", "a"], [])], FRUTAS)
    with pytest.raises(ValueError):
        ocupacao_espacos_frutas([(["z"], [])], FRUTAS)


# ------------------------------------------------------------------ medidas do N7 em dados sinteticos


def test_quem_decidiu_e_a_deferencia_por_zona():
    assert quem_decidiu_conflito(True, True) == quem_decidiu_conflito(True, False) == "necessidade"
    assert quem_decidiu_conflito(False, True) == "pedido" and quem_decidiu_conflito(False, False) == "ninguem"
    d1, d6 = 0, 5 * TICKS_POR_DIA
    dec = [  # (tick, regra, conflito, comeu, comeria_sem_pedido)
        (d1 + 15, "fome_moderada", True, False, True),     # pedido
        (d1 + 30, "fome_moderada", True, True, True),      # necessidade
        (d1 + 45, "fruta_no_cenario", True, False, True),  # pedido
        (d1 + 60, "fruta_no_cenario", True, False, False),  # ninguem
        (d1 + 75, "tempo_livre", False, False, False),     # fora de conflito
        (d6 + 15, "fome_moderada", True, True, True),      # necessidade (janela final)
        (d6 + 30, "fruta_no_cenario", True, False, True),  # pedido
        (d6 + 45, "pedido_necessidade", False, False, False),  # urgente, o pedido nao mudou nada
    ]
    jan = {"inicial": (0, 5 * TICKS_POR_DIA), "final": (5 * TICKS_POR_DIA, 10 * TICKS_POR_DIA)}
    r = deferencia_ao_pedido(dec, jan)
    ini, fin = r["por_janela"]["inicial"], r["por_janela"]["final"]
    assert ini["fome_moderada"]["deferencia"] == 0.5 and ini["fruta_no_cenario"]["deferencia"] == 0.5
    assert ini["total"] == {"conflitos": 4, "pelo_pedido": 2, "pela_necessidade": 1, "deferencia": 0.5}
    assert fin["fome_moderada"]["deferencia"] == 0.0 and fin["fruta_no_cenario"]["deferencia"] == 1.0
    assert r["conflitos"] == 6 and r["violacoes_urgentes"] == 0
    # G-URG: o pedido mudando uma decisao urgente conta como violacao
    assert deferencia_ao_pedido(dec + [(d6 + 60, "sono_noite", False, False, True)], jan)["violacoes_urgentes"] == 1
    assert deferencia_ao_pedido([], jan)["por_janela"]["final"]["total"]["deferencia"] is None
    with pytest.raises(ValueError):
        deferencia_ao_pedido([(0, "abandono", True, False, True)], jan)                      # conflito so nas zonas
    assert ZONAS_CONFLITO == ("fome_moderada", "fruta_no_cenario")


def test_fracao_de_x_e_cruzamento_do_zero():
    dia = TICKS_POR_DIA
    cons = [(10, "a", ["a", "b"]), (20, "b", ["a", "b"]), (30, "a", ["a"]),         # X sozinha nao conta
            (40, "c", ["b", "c"]),                                                    # oferta sem X nao conta
            (11 * dia, "b", ["a", "b", "c"]), (11 * dia + 5, "b", ["a", "b"])]
    jan = {"pedido": (0, 10 * dia), "extincao": (10 * dia, 14 * dia), "vazia": (14 * dia, 15 * dia)}
    r = fracao_da_fruta(cons, "a", jan)
    assert (r["pedido"]["n"], r["pedido"]["de_x"], r["pedido"]["taxa"]) == (2, 1, 0.5)
    assert (r["extincao"]["n"], r["extincao"]["taxa"]) == (2, 0.0)
    assert r["vazia"]["taxa"] is None
    with pytest.raises(ValueError):
        fracao_da_fruta([(1, "c", ["a", "b"])], "a", jan)
    assert dia_cruza_zero([512, 300, 40, -10, 5]) == 4
    assert dia_cruza_zero([512, 400]) is None and dia_cruza_zero([0]) == 1
    assert Counter(quem_decidiu_conflito(c, s) for c in (True, False) for s in (True, False)) == {"necessidade": 2, "pedido": 1,
                                                                                                  "ninguem": 1}
