"""V2, W-CORPO-QUIMICA (docs/TAREFA_V2_CORPO_DRIVES.md, etapa 1 da secao 14): a quimica dos drives de hoje, sem orgao, em inteiros.

O G-HOJE (a) em malha aberta: uma vida de hoje rejogada com as mesmas acoes forcadas, com o corpo ao lado, tick a tick. A derivacao dos
k_h, o exemplo do tick 660 (secao 3), as conversoes, a ConfigCorpo e o gabarito da paridade com o TS. So as sementes dos testes.
"""
from __future__ import annotations

import ast
import dataclasses
import json
import math
import random
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import exportar_gabarito_corpo as gab  # noqa: E402
from digilab import corpo as corpo_mod  # noqa: E402
from digilab.config import CONFIG_CORPO, CONFIG_PADRAO, ConfigCorpo, ConfigLobos  # noqa: E402
from digilab.corpo import (DRIVE_DO_QUIMICO, PARAMETROS_CORPO, QUIMICOS, Corpo, div_arred, k_meia_vida, na_grade,  # noqa: E402
                           passo_meia_vida, taxas_de)
from digilab.donos import criar_dono  # noqa: E402
from digilab.events import ACOES_PET_HOJE, AcaoPet, AcaoUsuario  # noqa: E402
from digilab.policies import lobos  # noqa: E402
from digilab.policy import PoliticaInstinto, efeito_da_acao_do_pet  # noqa: E402
from digilab.state import Estado, aplicar_acao_usuario, avancar_um_tick  # noqa: E402
from digilab.treino import simular_vida  # noqa: E402

CFG = CONFIG_PADRAO
CC = ConfigCorpo(ligada=True)
C = CC.escala
DONOS = ("atencioso", "relapso", "aleatorio", "incoerente")
SEMENTES = (101, 202, 303, 404, 505)
DIAS = 3
ORCAMENTO = 48
TOL = 1e-9                                  # secao 12, G-HOJE (a)
DRIVES = ("fome", "higiene", "energia", "humor")


# ------------------------------------------------------------------ ConfigCorpo

def test_config_corpo_desligada_por_padrao_e_registrada():
    assert CONFIG_CORPO.ligada is False
    assert set(PARAMETROS_CORPO) == {f.name for f in dataclasses.fields(ConfigCorpo)}
    assert all(status in ("PROPOSTO", "DECIDIDO") for status, _ in PARAMETROS_CORPO.values())


@pytest.mark.parametrize("chaves", [{"digestao": True, "vida": True, "drives_novos": True},
                                     {"digestao": True, "vida": True, "drives_novos": True, "gestos": True}])
def test_subchaves_da_etapa_6_existem(chaves):
    """desde a etapa 6 (CORPO-DRIVES) os drives novos e os gestos existem, cada um exigindo o anterior (antes falhavam alto)"""
    cc = ConfigCorpo(ligada=True, **chaves)
    assert cc.drives_novos and cc.gestos == chaves.get("gestos", False)


@pytest.mark.parametrize("chaves", [{"digestao": True}, {"ligada": True, "vida": True}, {"ligada": True, "digestao": True, "gestos": True}])
def test_subchave_sem_a_anterior_falha_alto(chaves):
    with pytest.raises(ValueError, match="exige"):
        ConfigCorpo(**chaves)


def test_corpo_com_a_chave_desligada_falha_alto():
    with pytest.raises(ValueError, match="desligada"):
        Corpo.de_estado(Estado(), CFG, CONFIG_CORPO)


# ------------------------------------------------------------------ escala e taxas

def test_taxas_de_hoje_na_escala_c_sao_os_da_secao_4():
    t = taxas_de(CFG, CC)
    assert (t.fome_por_tick, t.desconforto_por_tick, t.desconforto_por_sujeira, t.tristeza_por_tick) == (375, 300, 36, 375)
    assert (t.cansaco_acordado, t.cansaco_noite, t.cansaco_dormindo) == (500, 900, -1875)
    assert (t.dano_privacao, t.dano_cura, t.limiar_privacao) == (225, -150, C - 67500)
    assert t.dono == {AcaoUsuario.ALIMENTAR: {"fome": -202500}, AcaoUsuario.LIMPAR: {"desconforto": -270000},
                      AcaoUsuario.BRINCAR: {"tristeza": -112500, "cansaco": 36000, "fome": 22500},
                      AcaoUsuario.ACARICIAR: {"tristeza": -27000}, AcaoUsuario.ELOGIAR: {"tristeza": -45000},
                      AcaoUsuario.REPREENDER: {"tristeza": 54000}}
    assert t.pet[AcaoPet.BRINCAR] == {"tristeza": -56250, "cansaco": 9000}
    assert t.pet[AcaoPet.EXPLORAR] == {"cansaco": 6750, "tristeza": -4500}
    assert t.pet[AcaoPet.COMER] == {"fome": -22500}
    assert t.pet[AcaoPet.EMBURRAR] == {"tristeza": 4500}


def test_c_e_o_menor_que_deixa_as_taxas_de_hoje_inteiras():
    """CD-1: 450000 = 2^4 . 3^2 . 5^5. Tirar qualquer fator primo tira algum numero de hoje da grade."""
    assert C == 2 ** 4 * 3 ** 2 * 5 ** 5
    for p in (2, 3, 5):
        with pytest.raises(ValueError, match="nao cai na grade"):
            taxas_de(CFG, ConfigCorpo(ligada=True, escala=C // p))


def test_numero_fora_da_grade_falha_alto():
    with pytest.raises(ValueError, match="nao cai na grade"):
        na_grade(0.1234567, C, "x")
    corpo = Corpo.de_estado(Estado(), CFG, CC)
    with pytest.raises(ValueError, match="nao cai na grade"):
        corpo.estimulo_fruta(0.1234567, 0.0)
    with pytest.raises(ValueError, match="nao cai na grade"):
        Corpo.de_estado(Estado(fome=0.1234567), CFG, CC)
    with pytest.raises(ValueError, match="fora de"):
        Corpo({**corpo.q, "fome": C + 1}, CFG, CC)
    with pytest.raises(ValueError, match="sem estimulo"):
        corpo.acao_dono(AcaoUsuario.POR_BOLA)


# ------------------------------------------------------------------ secao 3: o tick 660 e as meias-vidas

def test_exemplo_do_tick_660_da_secao_3():
    """A fome de 0,80, sem comer, chega a 0,25 exato em inteiros no tick 660; o float de hoje passa um pouco abaixo e a comparacao vira."""
    corpo = Corpo.de_estado(Estado(), CFG, CC)
    e = Estado()
    rng = random.Random(0)
    for _ in range(660):
        antes = e
        e = avancar_um_tick(e, CFG, rng)
        corpo.passo(antes)
    assert corpo.q["fome"] == 337500
    assert corpo.drives()["fome"] == 0.25 and not corpo.drives()["fome"] < 0.25
    assert e.fome == 0.24999999999998737 and e.fome < 0.25
    x = 0.8
    for _ in range(660):
        x -= 1 / 1200
    assert x == e.fome


@pytest.mark.parametrize("h, campo, k", [(30, "k_meia_vida_susto", 1497), (60, "k_meia_vida_dor", 753),
                                         (1440, "k_meia_vida_estresse", 32)])
def test_derivacao_dos_k_h(h, campo, k):
    assert k_meia_vida(h, CC.bits_meia_vida) == k == getattr(CC, campo)
    efetiva = math.log(2) / -math.log(1 - k / 2 ** CC.bits_meia_vida)
    q, ticks = C, 0
    while q > C // 2:
        q = passo_meia_vida(q, k, CC.bits_meia_vida)
        ticks += 1
    assert abs(ticks - efetiva) <= 1.0
    if h < 1440:
        assert abs(efetiva - h) < 0.1
    else:
        assert abs(efetiva - 1419) < 1.0                  # a tabela da secao 3: 1419 com k = 32


def test_meia_vida_tem_decremento_minimo_e_para_em_zero():
    k = CC.k_meia_vida_estresse
    q = 100
    for esperado in range(99, -1, -1):
        q = passo_meia_vida(q, k)
        assert q == esperado
    assert passo_meia_vida(0, k) == 0


# ------------------------------------------------------------------ receptores e div_arred

def test_div_arred_igual_ao_dos_lobos():
    rng = random.Random(7)
    for _ in range(3000):
        n, d = rng.randrange(-10 ** 9, 10 ** 9), rng.randrange(1, 10 ** 6)
        assert div_arred(n, d) == lobos.div_arred(n, d)


def test_receptores_na_escala_s():
    assert CC.escala_receptor == 2 ** ConfigLobos().bits_ponto_fixo
    rng = random.Random(11)
    for _ in range(500):
        q = {n: rng.randrange(C + 1) for n in QUIMICOS}
        corpo = Corpo(q, CFG, CC)
        rec = corpo.receptores()
        for nome in QUIMICOS:
            falta = div_arred(q[nome] * CC.escala_receptor, C)
            assert corpo.falta(nome) == falta
            assert rec[DRIVE_DO_QUIMICO[nome]] == CC.escala_receptor - falta
            assert isinstance(rec[DRIVE_DO_QUIMICO[nome]], int)


# ------------------------------------------------------------------ os estimulos de hoje, um a um

def _estado_da_grade(rng: random.Random) -> Estado:
    extremos = (0, C, rng.randrange(C + 1))
    v = {d: (C - rng.choice(extremos)) / C for d in ("fome", "higiene", "energia", "humor", "saude")}
    return Estado(tick=rng.randrange(4320), sujeira=rng.randrange(6), dormindo=rng.random() < 0.3, **v)


def _confere(corpo: Corpo, e: Estado) -> None:
    d = corpo.drives()
    for drive in ("fome", "higiene", "energia", "humor", "saude"):
        assert abs(d[drive] - getattr(e, drive)) <= TOL, drive


def test_acoes_do_dono_e_do_pet_iguais_as_de_hoje_na_grade():
    rng = random.Random(23)
    for _ in range(400):
        e = _estado_da_grade(rng)
        for acao in gab.ACOES_DONO:
            corpo = Corpo.de_estado(e, CFG, CC)
            corpo.acao_dono(acao)
            _confere(corpo, aplicar_acao_usuario(e, acao, CFG, random.Random(0)))
        for acao in ACOES_PET_HOJE:
            corpo = Corpo.de_estado(e, CFG, CC)
            corpo.acao_pet(acao)
            _confere(corpo, efeito_da_acao_do_pet(e, acao, CFG, CFG.intervalo_decisao_ticks))


def test_bola_e_fruta_iguais_as_de_hoje_na_grade():
    """As contas de ambiente.MotorAmbiente (humor + ganho, cortado em 1) e de frutas.MotorFrutas (fome + nutricao, humor + efeito)."""
    rng = random.Random(29)
    for _ in range(400):
        e = _estado_da_grade(rng)
        corpo = Corpo.de_estado(e, CFG, CC)
        corpo.estimulo_bola(0.15)
        _confere(corpo, dataclasses.replace(e, humor=min(1.0, e.humor + 0.15)))
        for efeito in (-0.10, 0.0, 0.10):
            corpo = Corpo.de_estado(e, CFG, CC)
            corpo.estimulo_fruta(0.10, efeito)
            _confere(corpo, dataclasses.replace(e, fome=min(1.0, e.fome + 0.10), humor=min(1.0, max(0.0, e.humor + efeito))))


def test_um_tick_igual_ao_de_hoje_na_grade():
    rng = random.Random(31)
    for _ in range(2000):
        e = _estado_da_grade(rng)
        corpo = Corpo.de_estado(e, CFG, CC)
        corpo.passo(e)
        depois = avancar_um_tick(e, CFG, random.Random(1))
        if depois.em_privacao(CFG) == corpo.em_privacao():
            _confere(corpo, depois)


# ------------------------------------------------------------------ G-HOJE (a): malha aberta

def _malha_aberta(dono: str, semente: int, cc: ConfigCorpo = CC, conferir: bool = True) -> dict:
    """Uma vida de hoje rejogada com as acoes do pet e do dono forcadas: o Estado de hoje (floats) e o corpo (inteiros) lado a lado.
    Com a digestao na taxa C (etapa 3), o estomago fica vazio depois de toda operacao e a comida se conserva (digerida + descartada)."""
    motor = simular_vida(dono, criar_dono(dono), PoliticaInstinto(CFG), semente, DIAS, ORCAMENTO).motor
    acoes_pet = dict(motor._acoes_pet)
    rng = random.Random(semente)
    e = Estado()
    corpo = Corpo.de_estado(e, CFG, cc)
    t = corpo.t
    erro = {d: 0.0 for d in DRIVES + ("saude",)}
    viradas = []
    comida = 0

    def estomago() -> None:
        if cc.digestao and cc.taxa_digestao >= C:
            assert corpo.q["alimento"] == 0, "na taxa C o estomago esvazia na hora"

    def confere(no_tick: bool) -> None:
        d = corpo.drives()
        for drive in erro:
            erro[drive] = max(erro[drive], abs(d[drive] - getattr(e, drive)))
        if no_tick and e.em_privacao(CFG) != corpo.em_privacao():
            viradas.append((e.tick, dict(corpo.q)))

    for ev in motor.log:
        if ev.tipo == "avanco":
            for _ in range(int(ev.valor)):
                if e.tick in acoes_pet:
                    a = acoes_pet[e.tick]
                    e = efeito_da_acao_do_pet(e, a, CFG, CFG.intervalo_decisao_ticks)
                    corpo.acao_pet(a)
                    comida += -t.pet[a].get("fome", 0) if a is AcaoPet.COMER else 0
                    confere(False)
                    estomago()
                antes = e
                e = avancar_um_tick(e, CFG, rng)
                corpo.passo(antes)
                confere(True)
                estomago()
                for drive in DRIVES if conferir else ():
                    assert abs(corpo.drives()[drive] - getattr(e, drive)) <= TOL, (dono, semente, e.tick, drive)
                limite = TOL + len(viradas) * (t.dano_privacao - t.dano_cura) / C
                assert not conferir or abs(corpo.drives()["saude"] - e.saude) <= limite, (dono, semente, e.tick)
        elif ev.tipo == "acao_usuario":
            a = AcaoUsuario(ev.valor)
            e = aplicar_acao_usuario(e, a, CFG, rng)
            corpo.acao_dono(a)
            comida += -t.dono[a]["fome"] if a is AcaoUsuario.ALIMENTAR else 0
            confere(False)
            estomago()
        else:
            raise ValueError(ev.tipo)
    assert e == motor._estado, "a malha aberta tem de reproduzir o Estado de hoje"
    assert rng.getstate() == motor._rng_ambiente.getstate(), "o corpo nao sorteia: a rng de ambiente e so a de hoje"
    if cc.digestao:
        assert corpo.digerido_total + corpo.descartado_total + corpo.q["alimento"] == comida, "a comida se conserva"
    return {"erro": erro, "viradas": viradas, "limiar": t.limiar_privacao, "corpo": corpo, "comida": comida}


@pytest.mark.parametrize("dono", DONOS)
def test_g_hoje_a_malha_aberta(dono):
    for semente in SEMENTES:
        r = _malha_aberta(dono, semente)
        _confere_g_hoje(r)


def _confere_g_hoje(r: dict) -> None:
    assert all(r["erro"][d] <= TOL for d in DRIVES), r["erro"]
    # toda virada do receptor de privacao e um quimico exatamente no limiar (o 0,15 de hoje): a grade inteira cai em cima dele, o
    # float de hoje passa um pouco abaixo (secao 3)
    for _, q in r["viradas"]:
        assert any(q[n] == r["limiar"] for n in corpo_mod.QUIMICOS_DA_PRIVACAO), q


def test_g_hoje_a_tem_viradas_so_onde_ha_privacao():
    """Os donos coerentes nunca deixam o pet perto da privacao: nenhuma virada. Relapso e aleatorio chegam ao limiar e viram."""
    for dono in ("atencioso", "incoerente"):
        assert all(not _malha_aberta(dono, s)["viradas"] for s in SEMENTES)
    assert any(_malha_aberta(d, s)["viradas"] for d in ("relapso", "aleatorio") for s in SEMENTES)


# ------------------------------------------------------------------ sem motor, sem rng

def _importados(arquivo: str) -> set:
    arvore = ast.parse((RAIZ / "digilab" / arquivo).read_text(encoding="utf-8"))
    importados = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            importados |= {a.name for a in no.names}
        elif isinstance(no, ast.ImportFrom):
            importados.add(("." * no.level) + (no.module or ""))
    return importados


def test_corpo_nao_importa_motor_nem_rng():
    # a etapa 6 trouxe o grafo da secao 18 num modulo ao lado (so dados e checagens, so biblioteca padrao)
    importados = _importados("corpo.py")
    assert importados <= {"__future__", "dataclasses", ".config", ".corpo_grafo", ".events", ".state"}, importados
    assert _importados("corpo_grafo.py") <= {"__future__", "dataclasses"}


# ------------------------------------------------------------------ o gabarito da paridade

def test_gabarito_da_paridade_reproduz():
    assert gab.ARQUIVO.read_text(encoding="utf-8") == gab.texto()
    g = json.loads(gab.texto())
    assert g["escala"] == C and len(g["vidas"]) == 3 and all(len(v["ticks"]) == DIAS * 1440 for v in g["vidas"])
    # versao 5 (etapa 7, o corpo em TS): a config, o grafo em toda combinacao de sub-chaves, o corpo que nasce de um Estado e o mundo
    # fisico no corpo da etapa 6; a web le este mesmo arquivo (web/app/test/corpo.test.ts)
    assert g["versao"] == 5 and g["config"]["escala"] == C
    assert len(g["grafo"]) == 2 * len(gab.CHAVES_V5) and len(g["de_estado"]) == 2 * len(gab.CHAVES_V5) * len(gab.ESTADOS_V5)
    assert {c["op"][0] for c in g["etapa6_mundo"]["casos"]} == {"pet_mundo", "andar", "consumo"}
