"""V2, W-LIGA-GESTOS (rodada 22): a etapa 6 do corpo ligada na bancada (docs/TAREFA_V2_CORPO_DRIVES.md, secao 14, etapa 8;
docs/PLANO_ANALISE_V2_CORPO_DRIVES.md, secoes 2, 3 e 5 e adendos 1 e 2), com o #245 (o motor dos gestos e o DonoComGestos, do A) e o #247
(a quimica dos drives novos e dos gestos e o cerebro, do B) na main.

O que se confere:
- os bracos do plano rodam (P0-q, P1-q, P0-c, P1-c, o bloco do tapa, o bloco G e o P1-cw), com o G1 de toda vida (Bancada.vida);
- G-P0C: o P0-c decide igual ao P0-q, decisao a decisao, com o mesmo log, nos mundos do plano;
- o P1-c-frutas e o P1-c com outro rotulo (o P1-cw contra o P1-c fica em tests/test_bancada_pesos_janela.py);
- a bronca do modo sem tapa nos canais: o SemGesto gasta o orcamento e nao chega ao log (VidaBancada.retirados);
- o tapa chega ao cerebro em toda fonte que aprende e nao no P0; o carinho (mudanca_no_corpo) tambem;
- o tapa na fruta X (A1.1): a fruta pela rng propria, um tapa por consumo de X no passo do dono seguinte, dentro do orcamento;
- o filtro sem_gestos e os acoplados do plano (P1-q^ac e P1-c^ac do P0-q);
- os drives novos na medida e os receptores novos na sonda da deriva;
- o corpo no mundo fisico (o arranjo do #247) roda; os gestos ficam fora dele e do bola_a1;
- a config do plano com todos os bracos.
So as sementes dos testes.
"""
from __future__ import annotations

import random
import sys
from collections import Counter
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
from digilab.config import CONFIG_CONSEQUENCIA, CONFIG_DONOS  # noqa: E402
from digilab.donos import Visao  # noqa: E402
from digilab.events import FRUTAS, AcaoUsuario, LogDeEventos  # noqa: E402
from digilab.frutas import DonoPedinte  # noqa: E402
from digilab.gestos import DonoComGestos  # noqa: E402

SONDA = {"estados": 5, "amostras": 5, "semente": 101}
CC_CANAIS = replace(CONFIG_CONSEQUENCIA, canais_ligados=True)
DONOS = ("atencioso", "aleatorio", "relapso", "incoerente")
PASSO = CONFIG_DONOS.passo_ticks


def _bancada(montagem="simples", dias=2, cc=CONFIG_CONSEQUENCIA, **kw):
    if montagem == "completa":
        kw.update(cfg_lobos=bv.cfg_lobos_do_ponto("T3", {"memoria_ganho": 512, "w0_info": 256}), montagem="completa")
    return bv.Bancada(dias, 16 * dias, cfg_consequencia=cc, **kw)


def _no_log(v, valor: str) -> list[int]:
    return [e.tick for e in v.motor.log if e.tipo == "acao_usuario" and str(e.valor) == valor]


def _cerebro(v):
    return bv.do_braco(v.motor.politica).cerebro


# ------------------------------------------------------------------ 1. os bracos do plano rodam


PLANO = (("P0-q", "bola"), ("P1-q", "bola"), ("P0-c", "bola"), ("P1-c", "bola"), ("P0-c", "padrao"), ("P1-c", "padrao"),
         ("P0-c-tapa", "bola"), ("P1-c-tapa", "bola"), ("P1-c-tapaX", "iguais_frutas"), ("P1-c-frutas", "iguais_frutas"),
         ("P1-cw", "bola"))


def test_os_nos_do_corpo_sairam():
    assert bv.NOS_PENDENTES == {} and bv.FILTROS_PENDENTES == {}
    for braco, _ in PLANO:
        assert bv.braco_de(braco) is bv.BRACOS[braco]


@pytest.mark.parametrize("braco,mundo", PLANO)
def test_os_bracos_do_plano_rodam_e_medem(braco, mundo):
    b = _bancada("completa", cc=CC_CANAIS)
    v = b.vida(bv.EspecVida("atencioso", braco, 202, None, mundo))       # Bancada.vida ja confere o G1
    regime = bv.BRACOS[braco].regime
    assert v.motor.cc.ligada and v.motor.cc.drives_novos == v.motor.cc.gestos == (regime == "corpo")
    assert set(v.gestos) >= {"acariciar", "tapa", "sem_gesto"} and v.gestos["acariciar"] == len(_no_log(v, "acariciar"))
    assert not _no_log(v, "elogiar") and not _no_log(v, "repreender")     # o DonoComGestos troca os dois
    assert bv.contar_acoes(v.motor.log)[0] + v.retirados == b.orcamento
    m = b.medir(v, SONDA)
    assert m["corpo"]["regime"] == regime and m["corpo"]["gestos"] == v.gestos
    assert m["corpo"]["drives_novos"]["disponivel"] == (regime == "corpo")
    assert m["dominancia"]["pelo_corpo"] and len(m["custo_da_plasticidade"]["deriva_por_dia"]) == b.dias


# ------------------------------------------------------------------ 2. G-P0C e o P1-c-frutas


@pytest.mark.parametrize("mundo,genoma", (("bola", None), ("padrao", None), ("padrao", 202), ("iguais_frutas", None)))
def test_g_p0c_o_p0_c_decide_igual_ao_p0_q(mundo, genoma):
    """G-P0C (plano, secao 8): o P0 continua o instinto de hoje; o instinto nao le os drives novos e o estresse nao muda outra funcao
    (CD-7), entao o P0-c e o P0-q com os quimicos novos acompanhados: as mesmas acoes, decisao a decisao, e o mesmo registro."""
    b = _bancada(dias=3)
    for dono in DONOS:
        for semente in (101, 202):
            q = b.vida(bv.EspecVida(dono, "P0-q", semente, genoma, mundo))
            c = b.vida(bv.EspecVida(dono, "P0-c", semente, genoma, mundo))
            assert c.motor.acoes_recentes(10**9) == q.motor.acoes_recentes(10**9), (dono, semente)
            assert c.motor.log.para_jsonl() == q.motor.log.para_jsonl() and c.gestos == q.gestos
            assert [m["regra"] for m in _cerebro(c).motivos] == [m["regra"] for m in _cerebro(q).motivos]


@pytest.mark.parametrize("montagem", ("simples", "completa"))
def test_o_p1_c_frutas_e_o_p1_c(montagem):
    b = _bancada(montagem, cc=CC_CANAIS)
    for dono in ("atencioso", "aleatorio"):
        for semente in (101, 202):
            f = b.vida(bv.EspecVida(dono, "P1-c-frutas", semente, None, "iguais_frutas"))
            c = b.vida(bv.EspecVida(dono, "P1-c", semente, None, "iguais_frutas"))
            assert bv.resumo_motor(f.motor) == bv.resumo_motor(c.motor)
            assert bv._interno(f.motor).replace('"braco": "P1-c-frutas"', '"braco": "P1-c"') == bv._interno(c.motor)


# ------------------------------------------------------------------ 3. a bronca do modo sem tapa nos canais


@pytest.mark.parametrize("mundo", ("bola", "padrao", "iguais_frutas"))
def test_a_bronca_sem_tapa_gasta_o_orcamento_fora_do_log(mundo):
    b = _bancada(dias=3)
    for dono in DONOS:
        v = b.vida(bv.EspecVida(dono, "P1-c", 303, None, mundo))
        assert v.retirados == v.gestos["sem_gesto"] and v.gestos["tapa"] == 0 and not _no_log(v, "tapa")
        assert bv.contar_acoes(v.motor.log)[0] + v.retirados == b.orcamento
        t = b.vida(bv.EspecVida(dono, "P1-c-tapa", 303, None, mundo))
        assert t.retirados == t.gestos["sem_gesto"] == 0 and len(_no_log(t, "tapa")) == t.gestos["tapa"]
        assert bv.contar_acoes(t.motor.log)[0] == b.orcamento
    # o atencioso e o incoerente reprendem: o modo sem tapa tem broncas a retirar
    assert b.vida(bv.EspecVida("atencioso", "P1-c", 303, None, mundo)).retirados > 0


@pytest.mark.parametrize("mundo", ("bola", "padrao"))
def test_o_mesmo_dono_nos_dois_modos(mundo):
    """Com a mesma rng do dono e um P0 que nao aprende, o tapa entra onde a bronca sumia (os donos que o estado do contato nao muda: o
    aleatorio e o relapso; o tapa e contato, CD-6, e o atencioso o le)."""
    b = _bancada(dias=3)
    for dono in ("aleatorio", "relapso"):
        c = b.vida(bv.EspecVida(dono, "P0-c", 101, None, mundo))
        t = b.vida(bv.EspecVida(dono, "P0-c-tapa", 101, None, mundo))
        assert bv.filtrar_log(t.motor.log, frozenset({"tapa"})).para_jsonl() == c.motor.log.para_jsonl()
        assert t.gestos["tapa"] == c.gestos["sem_gesto"] > 0


# ------------------------------------------------------------------ 4. o tapa e o carinho no cerebro, pela fonte


@pytest.mark.parametrize("mundo", ("bola", "padrao"))
def test_o_tapa_e_o_carinho_chegam_as_fontes_que_aprendem_e_nao_ao_p0(mundo):
    b = _bancada("completa", dias=3, cc=CC_CANAIS)
    for dono in ("atencioso", "incoerente"):
        p1 = b.vida(bv.EspecVida(dono, "P1-c-tapa", 101, None, mundo))
        tapas, carinhos = len(_no_log(p1, "tapa")), len(_no_log(p1, "acariciar"))
        assert tapas > 0 and carinhos > 0 and p1.motor.mudancas == carinhos
        cer = _cerebro(p1)
        assert cer._n_recompensas["tapa"] == tapas and cer._n_recompensas["carinho"] == carinhos
        mem = cer.memoria                         # so o tapa e o carinho do dono chegaram; o resto do cuidado nao
        assert mem.elogios == mem.broncas == 0 and mem.cuidados + mem.outras_acoes_dono == tapas + carinhos
        assert bv.do_braco(p1.motor.politica).sinais_entregues == tapas
        p0 = b.vida(bv.EspecVida(dono, "P0-c-tapa", 101, None, mundo))
        assert len(_no_log(p0, "tapa")) > 0 and p0.motor.mudancas == len(_no_log(p0, "acariciar")) > 0
        mem0 = _cerebro(p0).memoria               # no P0 nada chega (nem a memoria conta)
        assert mem0.elogios == mem0.broncas == mem0.cuidados == mem0.outras_acoes_dono == 0
        assert bv.do_braco(p0.motor.politica).sinais_entregues == 0


def test_o_tapa_ate_na_fonte_informacao(monkeypatch):
    """CD-10: o tapa e o sinal direto em toda fonte que aprende, inclusive a informacao (P2); o resto do dono nao chega."""
    pol = bv.PoliticaDoBraco(_Cerebro(), bv.BRACOS["P2"])
    for acao in (AcaoUsuario.ALIMENTAR, AcaoUsuario.ACARICIAR, AcaoUsuario.TAPA, AcaoUsuario.ELOGIAR):
        pol.receber_acao_dono(acao, 10)
    pol.mudanca_no_corpo("antes", "depois")
    assert pol.cerebro.recebidas == [AcaoUsuario.TAPA] and pol.cerebro.mudancas == [("antes", "depois")]
    assert pol.sinais_entregues == 1
    p0 = bv.PoliticaDoBraco(_Cerebro(), bv.BRACOS["P0"])
    p0.receber_acao_dono(AcaoUsuario.TAPA, 10)
    p0.mudanca_no_corpo("antes", "depois")
    assert p0.cerebro.recebidas == [] and p0.cerebro.mudancas == []
    p3 = bv.PoliticaDoBraco(_Cerebro(), bv.BRACOS["P3"])
    for acao in (AcaoUsuario.ALIMENTAR, AcaoUsuario.TAPA, AcaoUsuario.ELOGIAR):
        p3.receber_acao_dono(acao, 10)
    p3.mudanca_no_corpo("antes", "depois")
    assert p3.cerebro.recebidas == [AcaoUsuario.ALIMENTAR, AcaoUsuario.TAPA, AcaoUsuario.ELOGIAR] and p3.sinais_entregues == 2
    assert p3.cerebro.mudancas == [("antes", "depois")]


class _Cerebro:
    nome = "espiao"

    def __init__(self) -> None:
        self.recebidas, self.mudancas = [], []

    def receber_acao_dono(self, acao, tick) -> None:
        self.recebidas.append(acao)

    def mudanca_no_corpo(self, antes, depois) -> None:
        self.mudancas.append((antes, depois))


# ------------------------------------------------------------------ 5. o tapa na fruta X (A1.1)


def test_a_fruta_x_e_uniforme_pela_rng_propria():
    estado = random.getstate()
    xs = [bv.fruta_tapa(s) for s in range(600)]
    assert random.getstate() == estado
    c = Counter(xs)
    assert set(c) == set(FRUTAS) and all(150 <= n <= 250 for n in c.values())
    assert xs != [DonoPedinte.sortear_fruta(s) for s in range(600)]          # a regra do N7-6, com outra rng
    assert all(bv.fruta_tapa(s) == x for s, x in zip(range(600), xs))


def test_um_tapa_por_consumo_de_x_no_passo_seguinte():
    b = _bancada("completa", dias=3, cc=CC_CANAIS)
    total = 0
    for dono in DONOS:
        for semente in (101, 202, 303):
            v = b.vida(bv.EspecVida(dono, "P1-c-tapaX", semente, None, "iguais_frutas"))
            x = bv.fruta_tapa(semente)
            assert v.gestos["fruta_x"] == x and v.gestos["descartados"] == 0 and v.gestos["tapa"] == 0
            consumos = [c["tick"] for c in v.motor.consumos if c["fruta"] == x]
            assert _no_log(v, "tapa") == [(t // PASSO + 1) * PASSO for t in consumos] and v.gestos["tapas_fruta"] == len(consumos)
            assert bv.contar_acoes(v.motor.log)[0] + v.retirados == b.orcamento              # dentro do orcamento
            assert _cerebro(v)._n_recompensas.get("tapa", 0) == len(consumos)
            total += len(consumos)
    assert total > 0


def test_o_tapa_na_fruta_que_nao_cabe_no_passo_e_descartado():
    class Parado:
        nome = "parado"

        def decidir(self, visao, rng):
            self.visao = visao
            return []

    base = DonoComGestos(Parado(), "sem_tapa")
    d = bv.DonoTapaFruta(base, "b")
    estado = {"tick": 30, "consumos_frutas": ((15, "b"), (15, "a"), (20, "b"), (25, "b"))}
    visao = Visao(estado=estado, passo=1, passos_totais=10, orcamento=20, gasto=3, minimo_obrigatorio=2, maximo_permitido=2)
    assert d.decidir(visao, random.Random(1)) == [AcaoUsuario.TAPA, AcaoUsuario.TAPA]
    assert d.tapas == [(15, 30), (20, 30)] and d.descartados == [25]
    v = base.base.visao
    assert (v.gasto, v.minimo_obrigatorio, v.maximo_permitido) == (5, 0, 0)
    assert d.decidir(replace(visao, estado={**estado, "tick": 45}), random.Random(1)) == []      # os vistos nao voltam
    with pytest.raises(ValueError):
        bv.DonoTapaFruta(DonoComGestos(Parado(), "tapa"), "b")
    with pytest.raises(ValueError):
        bv.DonoTapaFruta(base, "z")


# ------------------------------------------------------------------ 6. o filtro sem_gestos e os acoplados do plano


def test_o_filtro_sem_gestos():
    assert bv.filtro_de("sem_gestos") == frozenset({"tapa", "acariciar"})
    b = _bancada(dias=3)
    for mundo in ("bola", "iguais_frutas"):
        braco = "P1-c-tapa" if mundo == "bola" else "P1-c-tapaX"
        o = b.vida(bv.EspecVida("atencioso", braco, 202, None, mundo))
        a = b.acoplar(o, "P0-c", "sem_gestos")                        # acoplar confere o G1
        assert not _no_log(a, "tapa") and not _no_log(a, "acariciar") and a.eventos_mundo == o.eventos_mundo
        tira = len(_no_log(o, "tapa")) + len(_no_log(o, "acariciar"))
        assert tira > 0 and len(a.motor.log) == len(o.motor.log) - tira
        mesmo = b.acoplar(o, braco, "nenhum")
        assert bv.resumo_motor(mesmo.motor) == bv.resumo_motor(o.motor)


@pytest.mark.parametrize("mundo", ("bola", "padrao"))
def test_os_acoplados_do_plano_saem_do_p0_q(mundo):
    """P1-q^ac e P1-c^ac (plano, 3.2 e 3.5): o mesmo registro do P0-q da celula, sem filtro (o carinho fica: e estimulo do corpo)."""
    b = _bancada(dias=3)
    for dono in ("atencioso", "aleatorio"):
        o = b.vida(bv.EspecVida(dono, "P0-q", 101, None, mundo))
        for destino in ("P1-q", "P1-c"):
            a = b.acoplar(o, destino, "nenhum")
            assert a.motor.log.para_jsonl() == o.motor.log.para_jsonl() and a.rotulo_braco == f"{destino}<P0-q:nenhum"
        q, c = b.acoplar(o, "P1-q", "nenhum"), b.acoplar(o, "P1-c", "nenhum")
        assert bv._interno(q.motor) != bv._interno(c.motor)                    # o corpo muda o que se aprende com o mesmo cuidado


# ------------------------------------------------------------------ 7. os drives novos na medida e na sonda


def test_os_drives_novos_na_medida():
    b = _bancada(dias=3)
    m = b.medir(b.vida(bv.EspecVida("atencioso", "P1-c", 202, None, "bola")), SONDA)
    d = m["corpo"]["drives_novos"]
    assert d["disponivel"] and set(d["janela"]["drives"]) == {"tedio", "solidao", "estresse", "dor"}
    for x in list(d["janela"]["drives"].values()) + list(d["vida_toda"]["drives"].values()):
        assert 0.0 <= x["media"] <= 1.0
    q = b.medir(b.vida(bv.EspecVida("atencioso", "P1-q", 202, None, "bola")), SONDA)["corpo"]["drives_novos"]
    assert q["disponivel"] is False


def test_a_sonda_com_os_receptores_novos():
    q = bv.CONFIG_CORPO_QUIMICA
    c = replace(q, drives_novos=True, gestos=True)
    assert bv.receptores_novos_de(q) == ()
    assert bv.receptores_novos_de(c) == ("tedio", "solidao", "estresse", "dor", "susto")
    assert bv.receptores_novos_de(c, com_mundo=True) == ("tedio", "curiosidade", "solidao", "estresse", "dor", "susto")
    estados = bv.estados_sonda(20, 101)
    S = c.escala_receptor
    um = [bv.percepcao_da_sonda(o, c, random.Random(7)) for o in estados]
    outro = [bv.percepcao_da_sonda(o, c, random.Random(7)) for o in estados]
    assert um == outro
    for p, o in zip(um, estados):
        hoje = bv.percepcao_da_sonda(o, q)
        assert (p.fome, p.higiene, p.energia, p.humor, p.saude) == (hoje.fome, hoje.higiene, hoje.energia, hoje.humor, hoje.saude)
        assert all(0 <= getattr(p, r) <= S for r in bv.receptores_novos_de(c)) and p.curiosidade is None
    rng = random.Random(3)
    seq = [bv.percepcao_da_sonda(o, c, rng) for o in estados]
    assert len({(p.tedio, p.solidao, p.estresse, p.dor, p.susto) for p in seq}) == len(seq)      # cada estado com os seus
    with pytest.raises(ValueError, match="rng"):
        bv.percepcao_da_sonda(estados[0], c)


# ------------------------------------------------------------------ 8. o corpo no mundo fisico e onde os gestos nao vao


def test_o_corpo_no_mundo_fisico_roda():
    """O arranjo do #247 (o consequencia_mundo credita, o consequencia_corpo fecha a decisao): o regime quimica roda no mundo fisico,
    com o G1 (Bancada.vida), as medidas e a dominancia pelo corpo conferida contra o motivo e os canais."""
    b = _bancada(dias=2, cc=CC_CANAIS)
    for mundo, lugar in (("fisico", "perto"), ("fisico_afastado", "longe")):
        for braco, origem in (("P0-quimica", "sonda"), ("P1-quimica", "sinal"), ("P3-quimica", "sonda")):
            v = b.vida(bv.EspecVida("atencioso", braco, 101, None, mundo, lugar=lugar))
            assert v.motor.cc.ligada and v.motor.cmf.ligada
            m = b.medir(v, SONDA)
            assert m["corpo"]["regime"] == "quimica" and m["mundo_fisico"] is not None
            d = m["dominancia"]
            assert d["pelo_corpo"] and d["origem"] == origem and d["conferido_com_canais"] == (origem == "sinal")
    bv.validar_config({"bracos": ["P0-quimica", "P1-quimica"], "donos": ["atencioso"], "sementes": [101], "dias": 1,
                       "orcamento": 16, "sonda": SONDA, "bootstrap": {}, "mundos": ["fisico"], "lugares": ["perto"]})


def test_os_gestos_ficam_fora_do_mundo_fisico_e_do_bola_a1():
    b = _bancada()
    with pytest.raises(ValueError, match="gestos"):
        b.vida(bv.EspecVida("atencioso", "P1-c", 101, None, "fisico", lugar="perto"))
    with pytest.raises(ValueError, match="gestos"):
        b.vida(bv.EspecVida("atencioso", "P0-q", 101, None, "bola_a1"))
    with pytest.raises(ValueError, match="fruta X"):
        b.vida(bv.EspecVida("atencioso", "P1-c-tapaX", 101, None, "bola"))
    base = {"donos": ["atencioso"], "sementes": [101], "dias": 1, "orcamento": 16, "sonda": SONDA, "bootstrap": {}}
    with pytest.raises(ValueError, match="gestos"):
        bv.validar_config({**base, "bracos": ["P1-c"], "mundos": ["fisico"], "lugares": ["perto"]})
    with pytest.raises(ValueError, match="gestos"):
        bv.validar_config({**base, "bracos": ["P0-q"], "mundos": ["bola_a1"]})
    with pytest.raises(ValueError, match="fruta X"):
        bv.validar_config({**base, "bracos": ["P1-c-tapaX"], "mundos": ["bola"]})


def test_o_tapa_so_com_o_corpo(monkeypatch):
    monkeypatch.setitem(bv.BRACOS, "P1-x", replace(bv.BRACOS["P1-q"], rotulo="P1-x", gestos="tapa"))
    with pytest.raises(ValueError, match="tapa so existe"):
        bv.braco_de("P1-x")


# ------------------------------------------------------------------ 9. a config do plano


def test_a_config_do_plano_com_todos_os_bracos_valida():
    comum = {"donos": ["aleatorio", "relapso", "atencioso", "incoerente"], "dias": 14, "orcamento": 224, "sonda": SONDA,
             "bootstrap": {}, "unidades": {"bases": [33101], "k": 1, "prefixo": "corpo"},
             "plano": "docs/PLANO_ANALISE_V2_CORPO_DRIVES.md"}
    bv.validar_config({**comum, "mundos": ["bola", "padrao"],
                       "bracos": ["P0-hoje", "P1-hoje", "P3-hoje", "P0-quimica", "P1-quimica", "P3-quimica", "P0-q", "P1-q", "P0-c",
                                  "P1-c", "P0-c-tapa", "P1-c-tapa", "P1-cw"],
                       "acoplados": [{"origem": "P0-q", "destino": "P1-q", "filtro": "nenhum"},
                                     {"origem": "P0-q", "destino": "P1-c", "filtro": "nenhum"},
                                     {"origem": "P1-c-tapa", "destino": "P0-c", "filtro": "sem_gestos"}]})
    bv.validar_config({**comum, "mundos": ["iguais_frutas"], "bracos": ["P1-c-tapaX", "P1-c-frutas"]})


def test_o_replay_do_disco_com_os_gestos():
    b = _bancada(dias=2)
    for braco, mundo in (("P1-c-tapa", "bola"), ("P1-c-tapaX", "iguais_frutas"), ("P1-q", "padrao")):
        v = b.vida(bv.EspecVida("incoerente", braco, 404, None, mundo))
        b.conferir_replay(v, v.motor.log.para_jsonl())
        r = b.rejogar(LogDeEventos.de_jsonl(v.motor.log.para_jsonl()), v.espec)
        assert bv.resumo_motor(r) == bv.resumo_motor(v.motor) and bv._interno(r) == bv._interno(v.motor)
