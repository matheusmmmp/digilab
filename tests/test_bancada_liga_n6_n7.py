"""BANCADA-LIGA-N6-N7 (docs/TAREFA_V2_BANCADA_LIGA_N6_N7.md): a memoria (N6) e o pedido (N7) ligados na bancada. Gates: G1 de toda vida
dos bracos novos e dos acoplados; os bracos antigos byte a byte (gabarito gravado antes); o M0 e o P0 nas decisoes; o pedido nao muda o
orcamento do dono; o so cuidado do P3+ped tira pedidos e broncas e guarda as ofertas; as medidas saem de vidas reais. So as sementes dos
testes."""

import json
import math
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import bancada_v2 as bv  # noqa: E402
import gabarito_bancada_liga as gab  # noqa: E402
from digilab.config import CONFIG_PADRAO, TICKS_POR_DIA  # noqa: E402
from digilab.events import ACOES_FRUTAS, FRUTAS, AcaoUsuario, LogDeEventos  # noqa: E402
from digilab.frutas import DonoPedinte  # noqa: E402
from digilab.policies.lobos import desarranjo_n6 as desarranjo_dos_lobos  # noqa: E402

DIAS, ORC = 4, 64
LOBOS = {"memoria_ganho": 512, "w0_pedido": 512}
BANCADA = bv.bancada_da_config({"dias": DIAS, "orcamento": ORC, "ponto": "T3", "lobos": LOBOS})
SONDA = {"estados": 5, "amostras": 5, "semente": 101}
DONOS = ("atencioso", "relapso", "aleatorio", "incoerente")
N6 = ("M0", "MR", "MT", "ME")
N7 = ("P0+ped", "P1+ped", "P3+ped")
REPREENDER = AcaoUsuario.REPREENDER.value


def _vida(braco, s=101, mundo="descasado", dono="atencioso", genoma=None, bancada=BANCADA):
    return bancada.vida(bv.EspecVida(dono, braco, s, genoma, mundo))


def _acoes(log, valores):
    return [(e.tick, str(e.valor)) for e in log if e.tipo == "acao_usuario" and str(e.valor) in valores]


OFERTAS = frozenset(a.value for a in ACOES_FRUTAS)


# ------------------------------------------------------------------ bracos antigos byte a byte


def test_bracos_antigos_byte_a_byte_pelo_gabarito():
    """As 312 vidas do gabarito (gravado com o codigo da main antes desta tarefa, tests/gabarito_bancada_liga.py) saem iguais."""
    gravado = json.loads(gab.ARQUIVO.read_text(encoding="utf-8"))
    vistos = 0
    for nome, v in gab.casos():
        assert gab.impressao(v) == gravado[nome], nome
        vistos += 1
    assert vistos == len(gravado)


def test_bracos_antigos_iguais_mesmo_com_as_chaves_novas_na_config():
    """Com memoria_ganho e w0_pedido na config, os bracos antigos nao veem nada: as chaves voltam ao padrao fora dos bracos novos."""
    gravado = json.loads(gab.ARQUIVO.read_text(encoding="utf-8"))
    com = bv.Bancada(4, 64, cfg_lobos=bv.cfg_lobos_do_ponto("T3", {"w0_info": 512, **LOBOS}))
    for mundo in ("descasado", "iguais_frutas", "padrao"):
        bracos = ("P0", "P1", "P2", "P3") if mundo != "padrao" else ("P0", "P1", "P3")
        for b in bracos:
            v = com.vida(bv.EspecVida("atencioso", b, 101, None, mundo))
            assert gab.impressao(v) == gravado[f"T3|{v.nome}"], v.nome


# ------------------------------------------------------------------ N6


def test_m0_e_o_p0_nas_decisoes_e_codifica_todo_consumo():
    for mundo in ("descasado", "mutavel", "iguais_frutas"):
        for dono in DONOS:
            for s, g in ((101, None), (303, 303)):
                m0, p0 = _vida("M0", s, mundo, dono, g), _vida("P0", s, mundo, dono, g)
                assert bv.resumo_motor(m0.motor) == bv.resumo_motor(p0.motor), (mundo, dono, s)
                mem = m0.motor.politica.estado_interno()["memoria"]
                assert mem["ganho"] == 0 and [e["fruta"] for e in mem["episodios"]] == [c["fruta"] for c in m0.motor.consumos]


def test_bracos_de_memoria_montados_por_cima_do_ponto():
    for b, modo in (("M0", "relevante"), ("MR", "relevante"), ("MT", "recencia"), ("ME", "embaralhada")):
        pol = BANCADA.politica(bv.EspecVida("atencioso", b, 202, mundo="descasado"))
        cl = pol.cerebro.cl
        assert cl.memoria_ligada and cl.memoria_modo == modo and cl.teto == 16384 and not cl.aprendizado_ligado
        assert cl.memoria_ganho == (0 if b == "M0" else 512) and cl.w0_pedido == 0
        assert cl.memoria_permutacao == (desarranjo_dos_lobos(202) if b == "ME" else ())
    assert tuple(bv.desarranjo_n6(202)[f] for f in FRUTAS) == desarranjo_dos_lobos(202)
    # nos bracos antigos e nos do pedido a memoria fica desligada
    for b in ("P0", "P1", "P3", "P1+ped"):
        cl = BANCADA.politica(bv.EspecVida("atencioso", b, 202, mundo="iguais_frutas")).cerebro.cl
        assert not cl.memoria_ligada and cl.memoria_ganho == 0 and cl.memoria_permutacao == ()
    with pytest.raises(ValueError, match="mundo das frutas"):
        BANCADA.vida(bv.EspecVida("atencioso", "MR", 101, mundo="padrao"))
    with pytest.raises(ValueError, match="instinto"):
        BANCADA.politica(bv.EspecVida("atencioso", "MR", 101, mundo="descasado", cerebro="instinto"))


# ------------------------------------------------------------------ N7


def test_o_pedido_nao_muda_o_orcamento_do_dono():
    for mundo in ("iguais_frutas", "descasado"):
        for dono in DONOS:
            for b in N7:
                v = _vida(b, 101, mundo, dono)
                dono_no_log, _ = bv.contar_acoes(v.motor.log)
                assert v.interacoes == ORC == dono_no_log - v.broncas, (mundo, dono, b)
                assert v.pedidos == len(_acoes(v.motor.log, bv.PEDIDOS))
                assert v.broncas == (v.motor.estado()["desobediencias"] if b == "P3+ped" else 0)
    # com w0_pedido 0 o pedido nao age: o P0+ped e o P0 com os pedidos no registro, e o acoplado sem eles e o P0
    zero = bv.bancada_da_config({"dias": DIAS, "orcamento": ORC, "ponto": "T3", "lobos": {"w0_pedido": 0}})
    for dono in DONOS:
        com, sem = _vida("P0+ped", 202, "iguais_frutas", dono, bancada=zero), _vida("P0", 202, "iguais_frutas", dono, bancada=zero)
        assert com.pedidos > 0
        assert bv.filtrar_log(com.motor.log, bv.PEDIDOS).para_jsonl() == sem.motor.log.para_jsonl()
        assert com.motor.consumos == sem.motor.consumos
        a = zero.acoplar(com, "P0", "sem_pedido")
        assert bv.resumo_motor(a.motor) == bv.resumo_motor(sem.motor) and a.interacoes == ORC


def test_o_pedinte_da_bancada_e_o_do_n7_mundo():
    for s in (101, 202, 303):
        v = _vida("P3+ped", s, "iguais_frutas")
        x = DonoPedinte.sortear_fruta(s)
        pedidos = _acoes(v.motor.log, bv.PEDIDOS)
        ofertas_x = sorted({t for t, a in _acoes(v.motor.log, OFERTAS) if a.endswith(f"_{x}")})
        assert [t for t, _ in pedidos] == ofertas_x and all(a.endswith(f"_{x}") for _, a in pedidos)   # logo depois de cada oferta de X
        assert BANCADA.pedinte(v.espec).bronca and not BANCADA.pedinte(bv.EspecVida("atencioso", "P1+ped", s)).bronca
        assert BANCADA.politica(v.espec).cerebro.cl.w0_pedido == 512
    with pytest.raises(ValueError):
        BANCADA.pedinte(bv.EspecVida("atencioso", "P3", 101))
    with pytest.raises(ValueError, match="mundo das frutas"):
        BANCADA.vida(bv.EspecVida("atencioso", "P3+ped", 101, mundo="bola"))


def test_so_cuidado_do_p3ped_tira_pedidos_e_broncas_e_guarda_as_ofertas():
    for dono in ("atencioso", "incoerente"):
        for s in (101, 202):
            v = _vida("P3+ped", s, "iguais_frutas", dono)
            a = BANCADA.acoplar(v, "P0", "sem_ensino")
            assert not _acoes(a.motor.log, bv.PEDIDOS) and not _acoes(a.motor.log, {REPREENDER})
            assert _acoes(a.motor.log, OFERTAS) == _acoes(v.motor.log, OFERTAS)
            assert a.broncas == 0 and a.interacoes == bv.contar_acoes(a.motor.log)[0]
            # sem filtro, as broncas ficam no registro e fora do orcamento
            n = BANCADA.acoplar(v, "P3+ped", "nenhum")
            assert n.broncas == v.broncas and n.interacoes == ORC
            assert bv.resumo_motor(n.motor) == bv.resumo_motor(v.motor)


# ------------------------------------------------------------------ G1


def test_g1_bracos_novos_e_acoplados():
    vidas = [_vida(b, s, m, d, g) for d in ("atencioso", "aleatorio") for s, g in ((101, None), (202, 202))
             for b, m in [(b, "descasado") for b in N6] + [(b, "mutavel") for b in ("MR", "ME")] +
             [(b, "iguais_frutas") for b in N7] + [("P3+ped", "descasado")]]
    acop = []
    for v in vidas:
        if v.espec.braco == "MR":
            acop += [BANCADA.acoplar(v, b, "nenhum") for b in ("M0", "MT", "ME")]
        if v.espec.braco == "P3+ped":
            acop += [BANCADA.acoplar(v, "P0", "sem_ensino"), BANCADA.acoplar(v, "P3", "sem_pedido")]
        if v.espec.braco == "P0+ped":
            acop.append(BANCADA.acoplar(v, "P0", "sem_pedido"))
    for v in vidas + acop:
        texto = v.motor.log.para_jsonl()
        BANCADA.conferir_replay(v, texto)
        r = BANCADA.rejogar(LogDeEventos.de_jsonl(texto), v.espec)
        assert bv.resumo_motor(r) == bv.resumo_motor(v.motor) and bv._interno(r) == bv._interno(v.motor)
    with pytest.raises(bv.ReplayDivergiu):
        BANCADA.conferir_replay(bv.VidaBancada(vidas[1].espec, vidas[2].motor, ORC))


# ------------------------------------------------------------------ medidas de vidas reais


def _finito(x):
    return isinstance(x, float) and math.isfinite(x)


def test_medidas_do_n6_saem_de_vidas_reais():
    fracoes, consumos = [], 0
    for s in (101, 202, 303):
        for b in ("MR", "MT", "ME", "M0"):
            m = BANCADA.medir(_vida(b, s), SONDA)["n6"]
            assert m["marcos"]["episodio_por_consumo"] and m["marcos"]["episodios"] == m["marcos"]["consumos"]
            consumos += m["marcos"]["consumos"]                         # uma vida curta pode nao comer (neofobia)
            assert m["subdecisoes"] >= m["subdecisoes_2_mais"] and m["total_decisoes"] == DIAS * TICKS_POR_DIA // \
                CONFIG_PADRAO.intervalo_decisao_ticks
            assert _finito(m["fracao_motivos_total"]) and _finito(m["ocupacao"]["curto_medio"])
            if b == "M0":
                assert m["mudou"] == 0                                  # ganho 0: a memoria nunca muda a escolha
            if m["fracao_decidida"] is not None:
                fracoes.append(m["fracao_decidida"])
    assert consumos > 0 and fracoes and all(_finito(f) for f in fracoes) and max(fracoes) > 0   # a memoria decide alguma escolha
    assert BANCADA.medir(_vida("P1", 101), SONDA)["n6"] is None


def test_medidas_do_n7_saem_de_vidas_reais():
    for b in N7:
        for s in (101, 202):
            v = _vida(b, s, "iguais_frutas")
            m = BANCADA.medir(v, SONDA)["n7"]
            assert m["fruta_x"] == DonoPedinte.sortear_fruta(s) and m["pedidos"] == v.pedidos
            tot = m["deferencia"]["por_janela"]["inicial"]["total"]
            assert tot["conflitos"] > 0 and _finito(tot["deferencia"]) and m["deferencia"]["violacoes_urgentes"] == 0
            assert _finito(m["fracao_x"]["inicial"]["taxa"]) or m["fracao_x"]["inicial"]["n"] == 0
            assert len(m["w_pedido_por_dia"]) == DIAS and all(isinstance(w, int) for w in m["w_pedido_por_dia"])
            if b == "P0+ped":
                assert set(m["w_pedido_por_dia"]) == {512}                 # o P0 nao aprende
            assert m["desobediencias"] == v.motor.estado()["desobediencias"]
    # o acoplado do P3+ped tambem mede a fracao de X (o G-MARCA do plano usa o so cuidado)
    a = BANCADA.acoplar(_vida("P3+ped", 101, "iguais_frutas"), "P0", "sem_ensino")
    m = BANCADA.medir(a, SONDA)["n7"]
    assert m is not None and m["pedidos"] == 0 and m["fruta_x"] == DonoPedinte.sortear_fruta(101)
    assert BANCADA.medir(_vida("P3", 101, "iguais_frutas"), SONDA)["n7"] is None


def test_rodar_com_os_blocos_n6_e_n7(tmp_path):
    base = {"donos": ["atencioso"], "sementes": [101, 202], "dias": 2, "orcamento": 32, "ponto": "T3", "lobos": LOBOS,
            "sonda": SONDA, "bootstrap": {"reamostragens": 200, "semente": 101, "nivel": 0.95}}
    r6 = bv.rodar({**base, "bracos": ["P0", *N6], "mundos": ["descasado"],
                   "acoplados": [{"origem": "MR", "destino": d, "filtro": "nenhum"} for d in ("M0", "MT", "ME")]}, tmp_path / "n6")
    r7 = bv.rodar({**base, "bracos": ["P0", *N7, "P3"], "mundos": ["iguais_frutas"],
                   "acoplados": [{"origem": "P3+ped", "destino": "P0", "filtro": "sem_ensino"},
                                 {"origem": "P0+ped", "destino": "P0", "filtro": "sem_pedido"}]}, tmp_path / "n7")
    assert len(r6["vidas"]) == 2 * (5 + 3) and len(r7["vidas"]) == 2 * (5 + 2)
    med6 = json.loads((tmp_path / "n6" / "medidas.json").read_text(encoding="utf-8"))
    med7 = json.loads((tmp_path / "n7" / "medidas.json").read_text(encoding="utf-8"))
    assert all(m["n6"] is not None for m in med6.values() if m["braco"] != "P0")
    assert all(m["n7"] is not None for m in med7.values() if m["braco"] in N7 or "+ped" in m["braco"])
    assert all(m["interacoes"] == 32 for m in med7.values() if m["origem"] is None)
