"""V2, W-LIGA-MUNDO (rodada 18): o instinto do mundo ligado na bancada (docs/TAREFA_V2_MUNDO_FISICO.md, secao 9, etapa 3; os quatro
passos do #231): sem o NOS_PENDENTES["instinto_mundo"], o cerebro "instinto" e o P0z sao a PoliticaInstintoMundo, e os lobos veem o mundo
pela chave dele (PoliticaLobos(..., cfg_mundo=)).

O que se confere:
- o gate do P0: com lobos e o instinto do mundo byte a byte, nos dois layouts, 4 donos x 3 lugares x sementes, nas duas montagens;
- os lobos veem o mundo (a percepcao chega e as regras do mundo disparam) e o escolher_alvo deles e o padrao do motor;
- o P0z: nenhuma acao explorar, o mesmo com qualquer cerebro da config, G1;
- os acoplados P0^ac (P0 <- P0z) e P1^ac (P1 <- P0z) do adendo 1: os mesmos gestos nos mesmos ticks, G1;
- o P1 aprende pela consequencia no mundo (o gancho consequencia_mundo);
- a config com plano no mundo fisico valida.
So as sementes dos testes.
"""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
from digilab.events import AcaoPet, LogDeEventos  # noqa: E402
from digilab.instinto_mundo import PoliticaInstintoMundo  # noqa: E402
from digilab.mundo import ESTILOS_LUGAR  # noqa: E402
from digilab.policies.lobos import PoliticaLobos  # noqa: E402

DONOS = ("atencioso", "relapso", "aleatorio", "incoerente")
MUNDOS_FISICOS = ("fisico", "fisico_afastado")
SONDA = {"estados": 5, "amostras": 5, "semente": 101}


def _bancada(dias=2, montagem="simples"):
    kw = {} if montagem == "simples" else {"cfg_lobos": bv.cfg_lobos_do_ponto("T3"), "montagem": "completa"}
    return bv.Bancada(dias, 16 * dias, **kw)


def _acoes(motor) -> Counter:
    return Counter(a.value for _, a in motor._acoes_pet)


def _g1(b: bv.Bancada, v: bv.VidaBancada) -> None:
    r = b.rejogar(LogDeEventos.de_jsonl(v.motor.log.para_jsonl()), v.espec)
    assert bv.resumo_motor(r) == bv.resumo_motor(v.motor)
    assert bv._interno(r) == bv._interno(v.motor)


# ------------------------------------------------------------------ 1. o gate: P0 com lobos = o instinto do mundo


@pytest.mark.parametrize("mundo", MUNDOS_FISICOS)
@pytest.mark.parametrize("montagem", ("simples", "completa"))
def test_p0_com_lobos_e_o_instinto_do_mundo_byte_a_byte(mundo, montagem):
    b = _bancada(montagem=montagem)
    for dono in DONOS:
        for lugar in ESTILOS_LUGAR:
            for semente in (101, 202):
                vi = b.vida(bv.EspecVida(dono, "P0", semente, None, mundo, "instinto", lugar))
                vl = b.vida(bv.EspecVida(dono, "P0", semente, None, mundo, "lobos", lugar))
                assert isinstance(bv.do_braco(vi.motor.politica).cerebro, PoliticaInstintoMundo)
                assert isinstance(bv.do_braco(vl.motor.politica).cerebro, PoliticaLobos)
                # log, estado, acoes do pet, rngs (ambiente, politica, os fluxos do mundo) e o registro do mundo
                assert bv.resumo_motor(vl.motor) == bv.resumo_motor(vi.motor), (dono, lugar, semente)
                assert vl.interacoes == vi.interacoes and vl.retirados == vi.retirados


def test_os_lobos_veem_o_mundo_e_deixam_o_alvo_ao_motor():
    b = _bancada(dias=3)
    regras, ganchos = Counter(), 0
    for dono in ("aleatorio", "relapso"):
        for lugar in ESTILOS_LUGAR:
            v = b.vida(bv.EspecVida(dono, "P0", 303, None, "fisico", "lobos", lugar))
            lobos = bv.do_braco(v.motor.politica).cerebro
            assert lobos.entradas[-2:] == ("bola", "fruta")
            ei = lobos.estado_interno()
            regras.update(m["regra"] for m in ei["motivos"])
            # o motor perguntou o alvo (o gancho anota os candidatos no motivo) e ficou com o padrao: o gate acima e byte a byte
            ganchos += sum("mundo" in m for m in ei["motivos"])
    # a regra que so existe com a percepcao do mundo dispara (comida boa vista; a bola vista depende de onde ela rolou)
    assert regras["fruta_no_cenario"] > 0 and ganchos > 0


# ------------------------------------------------------------------ 2. o P0z


@pytest.mark.parametrize("mundo", MUNDOS_FISICOS)
def test_o_p0z_nao_explora_e_passa_o_g1(mundo):
    b = _bancada(dias=3)
    for dono in DONOS:
        for lugar in ESTILOS_LUGAR:
            vz = b.vida(bv.EspecVida(dono, "P0z", 101, None, mundo, "lobos", lugar))        # Bancada.vida ja confere o G1
            assert AcaoPet.EXPLORAR.value not in _acoes(vz.motor)
            assert bv.do_braco(vz.motor.politica).cerebro.sem_explorar
            # em qualquer cerebro da config o P0z e o mesmo (os lobos nao tem o modo)
            vi = b.vida(bv.EspecVida(dono, "P0z", 101, None, mundo, "instinto", lugar))
            assert bv.resumo_motor(vi.motor) == bv.resumo_motor(vz.motor)
            _g1(b, vz)


def test_o_p0_explora_e_o_p0z_nao():
    """O controle da premissa: na mesma semente o P0 explora e o P0z, nao; o resto do tempo livre do P0z vai ao ocioso."""
    b = _bancada(dias=3)
    p0, p0z = Counter(), Counter()
    for dono in DONOS:
        p0 += _acoes(b.vida(bv.EspecVida(dono, "P0", 202, None, "fisico", lugar="perto")).motor)
        p0z += _acoes(b.vida(bv.EspecVida(dono, "P0z", 202, None, "fisico", lugar="perto")).motor)
    assert p0[AcaoPet.EXPLORAR.value] > 0 and p0z[AcaoPet.EXPLORAR.value] == 0


# ------------------------------------------------------------------ 3. os acoplados P0^ac e P1^ac


@pytest.mark.parametrize("destino", ("P0", "P1"))
def test_os_acoplados_do_registro_do_p0z(destino):
    b = _bancada(dias=3)
    gestos = lambda log: [(e.tick, e.tipo, e.valor) for e in log if e.tipo in ("deixar_comida", "deixar_bola")]  # noqa: E731
    for dono in ("atencioso", "aleatorio"):
        for lugar in ESTILOS_LUGAR:
            vz = b.vida(bv.EspecVida(dono, "P0z", 101, None, "fisico", lugar=lugar))
            ac = b.acoplar(vz, destino, "nenhum")                    # acoplar ja rejoga o registro bit a bit (G1)
            assert ac.rotulo_braco == f"{destino}<P0z:nenhum" and ac.espec.lugar == lugar
            assert gestos(ac.motor.log) == gestos(vz.motor.log) and gestos(vz.motor.log)
            assert ac.interacoes == vz.interacoes
            assert isinstance(bv.do_braco(ac.motor.politica).cerebro, PoliticaLobos)
            _g1(b, ac)


# ------------------------------------------------------------------ 4. o P1 aprende no mundo; a config com plano


def test_o_p1_aprende_pela_consequencia_no_mundo():
    b = _bancada(dias=3)
    v = b.vida(bv.EspecVida("relapso", "P1", 101, None, "fisico", lugar="longe"))
    lobos = bv.do_braco(v.motor.politica).cerebro
    rec = lobos.estado_interno()["aprendizado"]["recompensas"]
    assert rec.get("consequencia", 0) + rec.get("consequencia_fruta", 0) > 0
    assert bv.do_braco(v.motor.politica).consequencias > 0
    m = b.medir(v, SONDA)
    assert m["dominancia"]["origem"] == "sinal"


def test_a_config_com_plano_no_mundo_fisico_valida():
    cfg = {"bracos": ["P0", "P0z", "P1", "P3"], "donos": ["atencioso"], "unidades": {"bases": [31101], "k": 1, "prefixo": "mundo"},
           "plano": "docs/PLANO_ANALISE_V2_MUNDO_FISICO.md", "dias": 14, "orcamento": 224, "sonda": SONDA, "bootstrap": {},
           "mundos": ["fisico", "fisico_afastado"], "lugares": list(ESTILOS_LUGAR),
           "acoplados": [{"origem": "P0z", "destino": "P0", "filtro": "nenhum"}, {"origem": "P0z", "destino": "P1", "filtro": "nenhum"}]}
    bv.validar_config(cfg)
    assert "instinto_mundo" not in bv.NOS_PENDENTES
