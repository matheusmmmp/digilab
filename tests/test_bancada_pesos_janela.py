"""V2, W-LIGA-PESOS-JANELA (rodada 18) e W-BANCADA-CORPO (rodada 21): o mecanismo do braco P1-cw na bancada, com a chave `pesos_janela`
da ConfigConsequencia do cerebro A (#236; PLANO_ANALISE_V2_CORPO_DRIVES, adendo 2, A2.4).

Desde a W-BANCADA-CORPO o P1-cw do plano e o P1-c (o regime "corpo") com a chave; roda desde a W-LIGA-GESTOS (a etapa 6 na main). O
mecanismo da bancada (a chave chegando ao cerebro, os pesos da janela na dominancia e a conferencia com os canais) e conferido em tres
origens, cada uma com o P1-cw posto como ela com a chave (na terceira, o proprio P1-cw do plano):
- o P1 com a chave (o P1-cw da W-LIGA-PESOS-JANELA): o sinal do N3 pelo vetor de estado;
- o P1-quimica com a chave: o sinal pelo corpo (os receptores da quimica, `sinal_corpo`);
- o P1-c com a chave, o P1-cw do plano (o corpo com os drives novos e o DonoComGestos sem tapa): o P1-cw contra o P1-c.
Em cada um: o gate (a chave desligada e o braco de origem byte a byte), a vida que muda com a chave e o G1, o peso pela falta media da
janela refeito por fora decisao a decisao e a dominancia com esses pesos, conferida contra os canais do cerebro.
So as sementes dos testes.
"""
from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
from digilab.config import CONFIG_CONSEQUENCIA  # noqa: E402
from digilab.events import LogDeEventos  # noqa: E402
from digilab.policies.lobos import CANAL_DO_DRIVE, INDICE_HUMOR, div_arred, pesos_da_janela  # noqa: E402
from digilab.treino import reproduzir_com_feedback  # noqa: E402

SONDA = {"estados": 5, "amostras": 5, "semente": 101}
MUNDOS = (("padrao", None), ("bola", None), ("descasado", None), ("mutavel", None), ("fisico", "perto"), ("fisico_afastado", "longe"))
MUNDOS_CORPO = (("padrao", None), ("bola", None), ("descasado", None), ("mutavel", None), ("fisico", "perto"))   # o #247 no fisico
MUNDOS_GESTOS = (("padrao", None), ("bola", None), ("descasado", None), ("iguais_frutas", None))   # os gestos ficam fora do fisico
CC_CANAIS = replace(CONFIG_CONSEQUENCIA, canais_ligados=True)
ORIGENS = {"P1": MUNDOS, "P1-quimica": MUNDOS_CORPO, "P1-c": MUNDOS_GESTOS}


def _bancada(montagem="simples", dias=2, cc=CONFIG_CONSEQUENCIA):
    kw = {} if montagem == "simples" else {"cfg_lobos": bv.cfg_lobos_do_ponto("T3"), "montagem": "completa"}
    return bv.Bancada(dias, 16 * dias, cfg_consequencia=cc, **kw)


def _p1_cw_de(origem: str, monkeypatch, chave: bool = True) -> None:
    """O P1-cw de teste: o braco `origem` com a chave pesos_janela (com `origem` P1-c e a chave ligada, o proprio P1-cw do plano)."""
    monkeypatch.setitem(bv.BRACOS, "P1-cw", replace(bv.BRACOS[origem], rotulo="P1-cw", no="corpo-A2.4", pesos_janela=chave))


def test_o_p1_cw_do_plano_e_o_p1_c_com_a_chave_e_roda():
    b = bv.BRACOS["P1-cw"]
    assert b == replace(bv.BRACOS["P1-c"], rotulo="P1-cw", no="corpo-A2.4", pesos_janela=True) and bv.braco_de("P1-cw") is b
    v = _bancada().vida(bv.EspecVida("atencioso", "P1-cw", 101, None, "bola"))       # com o G1
    assert bv.do_braco(v.motor.politica).cfg_consequencia.pesos_janela and v.motor.cc.drives_novos and v.motor.cc.gestos


# ------------------------------------------------------------------ o gate: chave desligada = o braco de origem byte a byte


@pytest.mark.parametrize("origem", ("P1", "P1-quimica", "P1-c"))
@pytest.mark.parametrize("montagem", ("simples", "completa"))
def test_p1_cw_com_a_chave_desligada_e_a_origem_byte_a_byte(monkeypatch, origem, montagem):
    _p1_cw_de(origem, monkeypatch, chave=False)
    b = _bancada(montagem, cc=CC_CANAIS)
    for mundo, lugar in ORIGENS[origem]:
        for dono in ("atencioso", "aleatorio"):
            for semente in (101, 202):
                vw = b.vida(bv.EspecVida(dono, "P1-cw", semente, None, mundo, lugar=lugar))
                v1 = b.vida(bv.EspecVida(dono, origem, semente, None, mundo, lugar=lugar))
                assert bv.resumo_motor(vw.motor) == bv.resumo_motor(v1.motor), (mundo, dono, semente)
                # o estado interno so difere no rotulo do braco
                interno = bv._interno(vw.motor).replace('"braco": "P1-cw"', f'"braco": "{origem}"')
                assert interno == bv._interno(v1.motor), (mundo, semente)


# ------------------------------------------------------------------ ligada: a vida muda, G1, a chave chega ao cerebro


@pytest.mark.parametrize("origem", ("P1", "P1-quimica", "P1-c"))
@pytest.mark.parametrize("montagem", ("simples", "completa"))
def test_p1_cw_ligado_muda_a_vida_e_passa_o_g1(monkeypatch, origem, montagem):
    _p1_cw_de(origem, monkeypatch)
    b = _bancada(montagem, dias=3)
    mudou = 0
    for mundo, lugar in ORIGENS[origem]:
        vw = b.vida(bv.EspecVida("relapso", "P1-cw", 303, None, mundo, lugar=lugar))     # Bancada.vida ja confere o G1
        v1 = b.vida(bv.EspecVida("relapso", origem, 303, None, mundo, lugar=lugar))
        assert bv.do_braco(vw.motor.politica).cfg_consequencia.pesos_janela
        assert not bv.do_braco(v1.motor.politica).cfg_consequencia.pesos_janela
        r = b.rejogar(LogDeEventos.de_jsonl(vw.motor.log.para_jsonl()), vw.espec)
        assert bv.resumo_motor(r) == bv.resumo_motor(vw.motor) and bv._interno(r) == bv._interno(vw.motor)
        mudou += bv._interno(vw.motor) != bv._interno(v1.motor)
    assert mudou == len(ORIGENS[origem])                 # os pesos aprendidos saem outros em todo mundo


# ------------------------------------------------------------------ o peso pela falta media da janela


def _replay_com_registro(b: bv.Bancada, v: bv.VidaBancada) -> bv._Registro:
    regs = []

    def fab(cfg=None):
        reg = bv._Registro(b.politica(v.espec, cfg))
        regs.append(reg)
        return reg

    fisico = bv.mundo_de(v.espec.mundo).fisico is not None
    repro = bv.reproduzir_mundo if fisico else reproduzir_com_feedback
    m = repro(LogDeEventos.de_jsonl(v.motor.log.para_jsonl()), fab, semente=v.espec.semente, fabrica_motor=b.fabrica_motor(v.espec))
    assert bv.resumo_motor(m) == bv.resumo_motor(v.motor)
    return regs[-1]


@pytest.mark.parametrize("mundo,lugar", (("padrao", None), ("descasado", None), ("fisico", "perto")))
def test_o_peso_e_o_da_falta_media_da_janela(monkeypatch, mundo, lugar):
    _p1_cw_de("P1", monkeypatch)
    b = _bancada(dias=3)
    v = b.vida(bv.EspecVida("aleatorio", "P1-cw", 101, None, mundo, lugar=lugar))
    reg = _replay_com_registro(b, v)
    cerebro = reg.interna.cerebro
    S, J = cerebro._escala, CONFIG_CONSEQUENCIA.janela_pesos
    drives = tuple(CONFIG_CONSEQUENCIA.drives) + (INDICE_HUMOR,)        # os da E2: o cerebro pesa todos em toda decisao
    faltas, abaixo = [], 0
    for p in reg.passos_sinal:
        esperado = pesos_da_janela(faltas[-J:], drives, S)
        anotado = cerebro.motivos[p["k"]]["pesos_janela"]
        assert anotado == {CANAL_DO_DRIVE[i]: w for i, w in esperado.items()}, p["k"]
        abaixo += any(w < S for w in esperado.values())
        assert all(div_arred(S, 4) <= w <= S for w in esperado.values())
        faltas.append({i: S - bv.arred(p["antes"][i] * S) for i in drives})       # a janela anda depois da decisao
    assert len(reg.passos_sinal) == len(cerebro.motivos) and abaixo > 0      # a falta recente baixou algum peso


@pytest.mark.parametrize("origem", ("P1-quimica", "P1-c"))
@pytest.mark.parametrize("mundo", ("padrao", "descasado"))
def test_no_corpo_o_peso_e_o_da_falta_media_dos_receptores(monkeypatch, mundo, origem):
    _p1_cw_de(origem, monkeypatch)
    b = _bancada(dias=3)
    v = b.vida(bv.EspecVida("aleatorio", "P1-cw", 101, None, mundo))
    reg = _replay_com_registro(b, v)
    cerebro = reg.interna.cerebro
    S, J = cerebro._escala, CONFIG_CONSEQUENCIA.janela_pesos
    # os do N3 e o humor (E2), pelos nomes dos receptores; no P1-c, mais os drives novos do sinal (o susto fora)
    drives = ("fome", "higiene", "energia", "humor")
    if origem == "P1-c":
        drives = drives + tuple(r for r in ("tedio", "solidao", "estresse", "dor") if r in cerebro.motivos[0]["pesos_janela"])
        assert {"tedio", "solidao", "estresse"} <= set(drives)
    novos = {"tedio", "solidao", "estresse", "dor"}
    faltas, abaixo = [], 0
    for p in reg.passos_sinal:
        esperado = pesos_da_janela(faltas[-J:], drives, S)
        assert cerebro.motivos[p["k"]]["pesos_janela"] == esperado, p["k"]
        abaixo += any(w < S for w in esperado.values())
        # a falta lida pelo receptor: S - leitura nos drives de hoje, a propria leitura nos novos
        faltas.append({d: getattr(p["antes_corpo"], d) if d in novos else S - getattr(p["antes_corpo"], d) for d in drives})
    assert len(reg.passos_sinal) == len(cerebro.motivos) and abaixo > 0


# ------------------------------------------------------------------ a dominancia do P1-cw com os pesos da janela


def test_a_dominancia_do_p1_cw_usa_os_pesos_e_confere_com_os_canais(monkeypatch):
    _p1_cw_de("P1", monkeypatch)
    b = _bancada(dias=3, cc=CC_CANAIS)
    vidas = []
    for mundo, lugar in (("bola", None), ("descasado", None), ("fisico", "perto")):
        v = b.vida(bv.EspecVida("aleatorio", "P1-cw", 202, None, mundo, lugar=lugar))
        d = b.medir(v, SONDA)["dominancia"]
        assert d["origem"] == "sinal" and d["conferido_com_canais"]       # os totais por canal do cerebro sao os ponderados
        vidas.append(v)
    # medida com peso 1 (o sinal recalculado sem os pesos da janela): os totais divergem dos canais do cerebro, e falha alto
    original = bv.sinal_por_canal
    monkeypatch.setattr(bv, "sinal_por_canal", lambda antes, depois, ds, ganho, S, pesos=None: original(antes, depois, ds, ganho, S))
    with pytest.raises(RuntimeError, match="divergem"):
        b.medir(vidas[0], SONDA)


@pytest.mark.parametrize("origem", ("P1-quimica", "P1-c"))
def test_no_corpo_a_dominancia_usa_os_pesos_dos_receptores(monkeypatch, origem):
    _p1_cw_de(origem, monkeypatch)
    b = _bancada(dias=3, cc=CC_CANAIS)
    vidas = []
    for mundo in ("bola", "descasado"):
        v = b.vida(bv.EspecVida("aleatorio", "P1-cw", 202, None, mundo))
        d = b.medir(v, SONDA)["dominancia"]
        assert d["pelo_corpo"] and d["origem"] == "sinal" and d["conferido_com_canais"] and d["conferido_com_motivo"]
        vidas.append(v)
    # sem os pesos da janela, a contribuicao da medida diverge da do cerebro (o motivo), e falha alto
    original = bv.contribuicoes_corpo
    monkeypatch.setattr(bv, "contribuicoes_corpo", lambda a, d, ds, S, pd=None, pj=None: original(a, d, ds, S, pd))
    with pytest.raises(RuntimeError, match="divergem"):
        b.medir(vidas[0], SONDA)
