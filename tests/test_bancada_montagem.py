"""BANCADA-MONTAGEM (docs/TAREFA_V2_BANCADA_MONTAGEM.md): a chave "montagem" da config da bancada. "simples" (e sem a chave) e a bancada
de antes; "completa" monta em cada braco o cerebro A da secao 1 do PLANO_CALIBRACAO_CONJUNTA_V2. Gates: simples e sem chave byte a byte
pelo gabarito gravado antes (tests/gabarito_bancada_montagem.py, commit proprio); na completa, o P0 e o instinto byte a byte, cada braco
tem exatamente as chaves da tabela no estado interno, o P3 sem canais, o w0_info so nos P2; as ablacoes da K-7 sao o P1 completo menos
uma peca; G1 de toda vida e acoplado na completa.
"""
from __future__ import annotations

import json
import sys
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import bancada_v2 as bv  # noqa: E402
import gabarito_bancada_montagem as gab  # noqa: E402
import run_v2_experimento_maior as em  # noqa: E402
from digilab.events import LogDeEventos  # noqa: E402

DIAS, ORC = 4, 64
G, W_INFO, W_PEDIDO = 512, 768, 256          # valores distintos, para cada um ser reconhecido no estado interno
PECAS = {"memoria_ganho": G, "w0_info": W_INFO, "w0_pedido": W_PEDIDO}
BASE = {"dias": DIAS, "orcamento": ORC, "ponto": "T3", "lobos": PECAS, "julgamento_fruta": True}
COMPLETA = bv.bancada_da_config({**BASE, "montagem": "completa"})
SIMPLES = bv.bancada_da_config({**BASE, "montagem": "simples"})
FRUTAS_MUNDOS = ("casado_frutas", "descasado", "mutavel", "iguais_frutas")
PRINCIPAIS = ("P0", "P1", "P2", "P2e", "P2a", "P3")
ABLACOES = ("P1c", "P1c-mem", "P1c-can")
PECAS_ESTADO = ("memoria", "canais", "peso_info", "peso_pedido")
# a tabela da tarefa (secao 2): memoria (ganho), canais, w0_info e w0_pedido por braco, na montagem completa e no mundo das frutas
TABELA = {"P0": (None, False, None, None),
          "P1": (G, True, None, None),
          "P2": (G, True, W_INFO, None), "P2e": (G, True, W_INFO, None), "P2a": (G, True, W_INFO, None),
          "P3": (G, False, None, None),
          "P0+ped": (None, False, None, W_PEDIDO), "P1+ped": (G, True, None, W_PEDIDO), "P3+ped": (G, False, None, W_PEDIDO),
          "P1c": (G, True, None, None), "P1c-mem": (0, True, None, None), "P1c-can": (G, False, None, None),
          "M0": (0, False, None, None), "MR": (G, False, None, None), "MT": (G, False, None, None), "ME": (G, False, None, None)}


def _vida(bancada, braco, s=101, mundo="descasado", dono="atencioso", genoma=None, cerebro="lobos"):
    return bancada.vida(bv.EspecVida(dono, braco, s, genoma, mundo, cerebro=cerebro))


def _sem_rotulo(vida) -> dict:
    e = vida.motor.politica.estado_interno()
    e.pop("bancada")
    return e


# ------------------------------------------------------------------ simples = a bancada de antes


def test_simples_e_sem_chave_byte_a_byte_pelo_gabarito():
    """As 516 vidas do gabarito (gravado com o codigo da main antes desta tarefa) saem iguais com "montagem": "simples"; sem a chave,
    as 120 primeiras da bancada L1 (o caminho padrao da config)."""
    gabarito = json.loads(gab.ARQUIVO.read_text(encoding="utf-8"))
    vistos = {nome: gab.impressao(v) for nome, v in gab.casos({"montagem": "simples"})}
    assert len(vistos) == len(gabarito) == 516
    assert {n for n in vistos if vistos[n] != gabarito[n]} == set()
    n = 0
    for nome, v in gab.casos():
        if not nome.startswith("L1|") or n == 120:
            break
        assert gab.impressao(v) == gabarito[nome], nome
        n += 1
    assert n == 120
    assert bv.Bancada(DIAS, ORC).montagem == "simples" and bv.bancada_da_config({"dias": 1, "orcamento": 1}).montagem == "simples"


def test_chave_validada():
    with pytest.raises(ValueError, match="montagem"):
        bv.Bancada(DIAS, ORC, montagem="cheia")
    with pytest.raises(ValueError, match="montagem"):
        bv.validar_config({"bracos": ["P0"], "donos": ["atencioso"], "sementes": [101], "dias": 1, "orcamento": 1, "sonda": {},
                           "bootstrap": {}, "montagem": "cheia"})
    assert "montagem" in bv.CHAVES_CONFIG and bv.MONTAGENS == ("simples", "completa")
    with pytest.raises(ValueError, match="montagem"):
        bv.braco_montado(bv.BRACOS["P1"], "cheia", True)


# ------------------------------------------------------------------ completa: o P0 e o instinto


@pytest.mark.parametrize("mundo", FRUTAS_MUNDOS + ("padrao",))
def test_completa_p0_e_o_instinto_byte_a_byte(mundo):
    """K-1: na completa o P0 nao tem nada ligado; com as pecas, os canais e o K4 na config, a vida e a do instinto, byte a byte, e o
    estado interno do cerebro e o do P0 sem as pecas na config."""
    nua = bv.bancada_da_config({"dias": DIAS, "orcamento": ORC, "ponto": "T3"})
    cfg_canais = bv.bancada_da_config({**BASE, "consequencia": {"canais_ligados": True}, "montagem": "completa"})
    for s, g in ((101, None), (202, 202)):
        ins = _vida(COMPLETA, "P0", s, mundo, genoma=g, cerebro="instinto")
        for bancada in (COMPLETA, cfg_canais):
            p0 = _vida(bancada, "P0", s, mundo, genoma=g)
            assert bv.resumo_motor(p0.motor) == bv.resumo_motor(ins.motor)
            assert bv._interno(p0.motor) == bv._interno(_vida(nua, "P0", s, mundo, genoma=g).motor)
            assert not set(PECAS_ESTADO) & set(p0.motor.politica.estado_interno())
            assert p0.motor.politica.cfg_consequencia.canais_ligados is False


# ------------------------------------------------------------------ completa: as chaves de cada braco


@pytest.mark.parametrize("canais_cfg", (False, True))
def test_completa_cada_braco_com_as_chaves_da_tabela(canais_cfg):
    """No estado interno do cerebro: a memoria com o ganho g (ou nenhuma), os canais, o w0_info e o w0_pedido de cada braco sao os da
    tabela, seja qual for a chave dos canais na config. O P3 sem canais; o w0_info so nos P2; o pedido so nos bracos com pedido."""
    bancada = bv.bancada_da_config({**BASE, "consequencia": {"canais_ligados": canais_cfg}, "montagem": "completa"})
    for braco, (g, canais, w_info, w_pedido) in TABELA.items():
        v = _vida(bancada, braco, 101, "iguais_frutas" if braco.endswith("+ped") else "descasado")
        e = v.motor.politica.estado_interno()
        esperado = {k for k, x in zip(("memoria", "peso_info", "peso_pedido"), (g, w_info, w_pedido)) if x is not None}
        if canais:
            esperado.add("canais")          # o estado dos canais aparece depois do 1o credito, que toda vida destas tem
        assert set(PECAS_ESTADO) & set(e) == esperado, braco
        assert v.motor.politica.cfg_consequencia.canais_ligados is canais, braco
        if g is not None:
            assert e["memoria"]["ganho"] == g and e["memoria"]["modo"] == bv.MODO_MEMORIA[bv.BRACOS[braco].memoria or "relevante"], braco
        if w_info is not None:
            assert e["peso_info_prior"] == w_info, braco
        if w_pedido is not None:
            assert e["peso_pedido_prior"] == w_pedido, braco
        assert v.motor.politica.cerebro.cl.w0_info == (w_info or 0), braco


def test_completa_p3_sem_canais_e_w0_info_so_nos_p2_em_todo_mundo():
    for mundo in FRUTAS_MUNDOS:
        for braco in PRINCIPAIS:
            v = _vida(COMPLETA, braco, 202, mundo, genoma=202)
            e = v.motor.politica.estado_interno()
            assert ("peso_info" in e) == braco.startswith("P2"), (braco, mundo)
            assert ("memoria" in e) == (braco != "P0"), (braco, mundo)
            if braco in ("P0", "P3"):
                assert "canais" not in e and v.motor.politica.cfg_consequencia.canais_ligados is False


def test_completa_no_mundo_padrao_sem_as_pecas_das_frutas():
    """Fora das frutas o cerebro nao tem memoria, informacao nem pedido: o P1 completo fica com os canais, o P3 sem nada."""
    for braco, canais in (("P0", False), ("P1", True), ("P3", False)):
        v = _vida(COMPLETA, braco, 101, "padrao")
        assert COMPLETA.braco(v.espec).memoria is None
        assert not {"memoria", "peso_info", "peso_pedido"} & set(v.motor.politica.estado_interno())
        assert v.motor.politica.cfg_consequencia.canais_ligados is canais


# ------------------------------------------------------------------ completa: as ablacoes da K-7 e os blocos N6 e N7


def test_ablacoes_da_k7_sao_o_p1_completo_menos_uma_peca():
    """Na completa: o P1c e o P1 (so o rotulo muda); o P1c-mem e o P1 completo com g = 0 (o P1 de uma config com g = 0); o P1c-can e o
    P1 completo sem os canais, e o braco montado difere do P1 montado so nessa peca."""
    g0 = bv.bancada_da_config({**BASE, "lobos": {**PECAS, "memoria_ganho": 0}, "montagem": "completa"})
    p1 = bv.braco_montado(bv.BRACOS["P1"], "completa", True)
    for s, mundo in ((101, "descasado"), (202, "mutavel"), (303, "casado_frutas")):
        um = _vida(COMPLETA, "P1", s, mundo)
        c = _vida(COMPLETA, "P1c", s, mundo)
        assert bv.resumo_motor(c.motor) == bv.resumo_motor(um.motor) and _sem_rotulo(c) == _sem_rotulo(um)
        mem = _vida(COMPLETA, "P1c-mem", s, mundo)
        um0 = _vida(g0, "P1", s, mundo)
        assert bv.resumo_motor(mem.motor) == bv.resumo_motor(um0.motor) and _sem_rotulo(mem) == _sem_rotulo(um0)
    campos = ("fonte", "informacao", "memoria", "pedido", "canais")
    for ablacao, peca, valor in (("P1c", None, None), ("P1c-mem", "memoria", "nenhuma"), ("P1c-can", "canais", False)):
        a = bv.braco_montado(bv.BRACOS[ablacao], "completa", True)
        difere = {k for k in campos if getattr(a, k) != getattr(p1, k)}
        assert difere == (set() if peca is None else {peca}) and (peca is None or getattr(a, peca) == valor), ablacao
    # o P1c-can e o P1 completo quando o P1 completo perde os canais (a mesma vida, pela politica)
    sem = replace(COMPLETA.politica(bv.EspecVida("atencioso", "P1", 101, mundo="descasado")).cfg_consequencia, canais_ligados=False)
    assert COMPLETA.politica(bv.EspecVida("atencioso", "P1c-can", 101, mundo="descasado")).cfg_consequencia == sem


def test_blocos_n6_e_n7_sao_os_de_antes_sem_o_w0_info():
    """Os bracos dos blocos fixam a memoria e o pedido: na completa sao os da simples com o w0_info so nos P2 (o P0+ped e o M0 a ME
    nao ganham canais nem memoria; o P1+ped e o P3+ped ganham as pecas do P1 e do P3)."""
    sem_info = bv.bancada_da_config({**BASE, "lobos": {**PECAS, "w0_info": 0}, "montagem": "simples"})
    for braco, mundo in (("M0", "descasado"), ("MR", "descasado"), ("MT", "mutavel"), ("ME", "mutavel"), ("P0+ped", "iguais_frutas")):
        a, b = _vida(COMPLETA, braco, 101, mundo), _vida(sem_info, braco, 101, mundo)
        assert bv.resumo_motor(a.motor) == bv.resumo_motor(b.motor) and bv._interno(a.motor) == bv._interno(b.motor), braco
    for braco, base in (("P1+ped", "P1"), ("P3+ped", "P3")):
        a = bv.braco_montado(bv.BRACOS[braco], "completa", True)
        assert (a.memoria, a.canais) == (bv.braco_montado(bv.BRACOS[base], "completa", True).memoria,
                                         bv.braco_montado(bv.BRACOS[base], "completa", True).canais) and a.pedido


def test_simples_continua_dando_w0_info_a_todos():
    """Comportamento de antes, guardado pelo gabarito: na simples o w0_info da config vale em todo braco (por isso a completa existe)."""
    assert "peso_info" in _vida(SIMPLES, "P1").motor.politica.estado_interno()
    assert "memoria" not in _vida(SIMPLES, "P1").motor.politica.estado_interno()


# ------------------------------------------------------------------ G1 e rodar


def test_g1_toda_vida_e_acoplado_na_completa():
    vidas = [_vida(COMPLETA, b, s, m, d, g) for b in PRINCIPAIS + ABLACOES for m in ("descasado", "mutavel")
             for d in ("atencioso", "aleatorio") for s, g in ((101, None), (202, 202))]
    vidas += [_vida(COMPLETA, b, 101, "iguais_frutas") for b in ("P0+ped", "P1+ped", "P3+ped")]
    vidas += [_vida(COMPLETA, b, 101, "descasado") for b in ("M0", "MR", "MT", "ME")]
    vidas += [_vida(COMPLETA, b, 101, "padrao") for b in ("P0", "P1", "P3")]
    acop = []
    for v in vidas:
        b, m = v.espec.braco, v.espec.mundo
        if m != "padrao" and b in ("P2", "P2e", "P2a", "P3", "P3+ped"):
            acop.append(COMPLETA.acoplar(v, "P0", "sem_ensino"))
        if m != "padrao" and b == "P3":
            acop += [COMPLETA.acoplar(v, "P1", "sem_sinais"), COMPLETA.acoplar(v, "P3", "nenhum")]
        if b == "P1c":
            acop.append(COMPLETA.acoplar(v, "P1c-can", "nenhum"))
    assert len(vidas) == 82 and len(acop) == 57
    for v in vidas + acop:
        texto = v.motor.log.para_jsonl()
        COMPLETA.conferir_replay(v, texto)
        r = COMPLETA.rejogar(LogDeEventos.de_jsonl(texto), v.espec)
        assert bv.resumo_motor(r) == bv.resumo_motor(v.motor) and bv._interno(r) == bv._interno(v.motor)


def test_rodar_na_completa_com_as_medidas_da_memoria(tmp_path):
    cfg = {"bracos": list(PRINCIPAIS), "donos": ["atencioso"], "sementes": [101, 202], "mundos": ["descasado"], "dias": 2, "orcamento": 32,
           "ponto": "T3", "lobos": PECAS, "julgamento_fruta": True, "montagem": "completa",
           "sonda": {"estados": 5, "amostras": 5, "semente": 101}, "bootstrap": {"reamostragens": 200, "semente": 101, "nivel": 0.95},
           "acoplados": [{"origem": "P3", "destino": "P0", "filtro": "sem_ensino"}]}
    r = bv.rodar(cfg, tmp_path)
    assert len(r["vidas"]) == 2 * (6 + 1)
    med = json.loads((tmp_path / "medidas.json").read_text(encoding="utf-8"))
    # as medidas da memoria (N6) saem nos bracos que a montagem liga; no P0 e no acoplado para o P0, nao
    assert {m["braco"] for m in med.values() if m["n6"] is not None} == {"P1", "P2", "P2e", "P2a", "P3"}
    meta = json.loads((tmp_path / "meta.json").read_text(encoding="utf-8"))
    assert meta["config"]["montagem"] == "completa"


def test_experimento_maior_usa_a_completa():
    cfg = {"dias": 14, "orcamento": 64, "sementes": [101]}
    cb = em.config_da_bancada(cfg, em.BRACOS, em.MUNDOS, [])
    assert em.MONTAGEM == "completa" and cb["montagem"] == "completa"
    assert bv.bancada_da_config(cb).montagem == "completa"
