"""V2, W-LIGA-PESOS-JANELA (rodada 18): o braco P1-cw ligado na bancada, com a chave `pesos_janela` da ConfigConsequencia do cerebro A
(#236; PLANO_ANALISE_V2_CORPO_DRIVES, adendo 2, A2.4). Sem o NOS_PENDENTES["pesos_janela"], o NOS_PENDENTES fica vazio.

O que se confere:
- o gate: o P1-cw com a chave desligada e o P1 byte a byte (os bracos do corpo, P1-c, ainda nao existem na bancada: o P1-cw e o P1 com
  a chave), nos mundos de hoje e no fisico, nas duas montagens;
- com a chave ligada a vida muda, e o G1 passa;
- o peso de cada drive e o da falta media nas J decisoes anteriores, refeito por fora decisao a decisao, e algum peso cai;
- a dominancia do P1-cw usa esses pesos (w_d da A2.2) e confere com os canais do cerebro.
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
CC_CANAIS = replace(CONFIG_CONSEQUENCIA, canais_ligados=True)


def _bancada(montagem="simples", dias=2, cc=CONFIG_CONSEQUENCIA):
    kw = {} if montagem == "simples" else {"cfg_lobos": bv.cfg_lobos_do_ponto("T3"), "montagem": "completa"}
    return bv.Bancada(dias, 16 * dias, cfg_consequencia=cc, **kw)


# ------------------------------------------------------------------ o gate: chave desligada = o P1 byte a byte


@pytest.mark.parametrize("montagem", ("simples", "completa"))
def test_p1_cw_com_a_chave_desligada_e_o_p1_byte_a_byte(monkeypatch, montagem):
    monkeypatch.setitem(bv.BRACOS, "P1-cw", replace(bv.BRACOS["P1-cw"], pesos_janela=False))
    b = _bancada(montagem, cc=CC_CANAIS)
    for mundo, lugar in MUNDOS:
        for dono in ("atencioso", "aleatorio"):
            for semente in (101, 202):
                vw = b.vida(bv.EspecVida(dono, "P1-cw", semente, None, mundo, lugar=lugar))
                v1 = b.vida(bv.EspecVida(dono, "P1", semente, None, mundo, lugar=lugar))
                assert bv.resumo_motor(vw.motor) == bv.resumo_motor(v1.motor), (mundo, dono, semente)
                # o estado interno so difere no rotulo do braco
                assert bv._interno(vw.motor).replace('"braco": "P1-cw"', '"braco": "P1"') == bv._interno(v1.motor), (mundo, semente)


# ------------------------------------------------------------------ ligada: a vida muda, G1, a chave chega ao cerebro


@pytest.mark.parametrize("montagem", ("simples", "completa"))
def test_p1_cw_ligado_muda_a_vida_e_passa_o_g1(montagem):
    b = _bancada(montagem, dias=3)
    mudou = 0
    for mundo, lugar in MUNDOS:
        vw = b.vida(bv.EspecVida("relapso", "P1-cw", 303, None, mundo, lugar=lugar))     # Bancada.vida ja confere o G1
        assert bv.do_braco(vw.motor.politica).cfg_consequencia.pesos_janela
        assert not bv.do_braco(b.vida(bv.EspecVida("relapso", "P1", 303, None, mundo, lugar=lugar)).motor.politica
                               ).cfg_consequencia.pesos_janela
        r = b.rejogar(LogDeEventos.de_jsonl(vw.motor.log.para_jsonl()), vw.espec)
        assert bv.resumo_motor(r) == bv.resumo_motor(vw.motor) and bv._interno(r) == bv._interno(vw.motor)
        v1 = b.vida(bv.EspecVida("relapso", "P1", 303, None, mundo, lugar=lugar))
        mudou += bv._interno(vw.motor) != bv._interno(v1.motor)
    assert mudou == len(MUNDOS)                          # os pesos aprendidos saem outros em todo mundo


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
def test_o_peso_e_o_da_falta_media_da_janela(mundo, lugar):
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


# ------------------------------------------------------------------ a dominancia do P1-cw com os pesos da janela


def test_a_dominancia_do_p1_cw_usa_os_pesos_e_confere_com_os_canais(monkeypatch):
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


def test_nos_pendentes_vazio():
    assert bv.NOS_PENDENTES == {} and bv.braco_de("P1-cw") is bv.BRACOS["P1-cw"]
