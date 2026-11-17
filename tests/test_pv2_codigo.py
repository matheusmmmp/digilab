"""O codigo do PV-2 (docs/PLANO_ANALISE_V3_PET_VIVO_PV2.md, secoes 3 e 6; docs/futuro/integracao_cadeia_digibrain.md, secao 8.3): as
conferencias que falham alto. O byte a byte desligado fica em tests/test_gabarito_pv2.py."""
from __future__ import annotations

import sys
from dataclasses import fields, replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import pv2  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402
from digilab.config import (BRACOS_PV2, CONFIG_CORPO, CONFIG_PADRAO, CONFIG_PV2, PARAMETROS_PV2, ConfigOlfato,  # noqa: E402
                            ConfigPV2)
from digilab.corpo import leitura_orgao  # noqa: E402
from digilab.digibrain import DigiBrain  # noqa: E402
from digilab.digibrain.impulso import Impulso  # noqa: E402
from digilab.digibrain.sens import RECEPTORES_OLFATO_COMIDA, Sens, leitura_do_orgao  # noqa: E402
from digilab.mundo import Alvo  # noqa: E402

DIAS = 2


# ------------------------------------------------------------------ a config
def test_a_config_do_pv2_tem_status_em_todo_campo_e_falha_alto():
    assert set(PARAMETROS_PV2) == {f.name for f in fields(ConfigPV2)}
    assert all(s in ("PROPOSTO", "DECIDIDO") and fonte for s, fonte in PARAMETROS_PV2.values())
    assert CONFIG_PV2.ligada is False and CONFIG_PV2.g0 == 64
    for kw in ({"braco": "OLF-X"}, {"l_pirueta": 0}, {"taxa_placebo": 257}, {"w0_dc": -1}, {"g0": 0}):
        with pytest.raises(ValueError):
            ConfigPV2(**kw)
    with pytest.raises(TypeError):
        ConfigPV2(ligada=1)


def test_o_cerebro_pede_o_orgao_com_o_pv2_e_so_com_ele():
    cd = orq.config_do_braco("REL", None, True)
    ligada = replace(CONFIG_PV2, ligada=True)
    with pytest.raises(ValueError):
        DigiBrain(CONFIG_PADRAO, cd, orq.CM, cfg_pv2=ligada)
    with pytest.raises(ValueError):
        DigiBrain(CONFIG_PADRAO, cd, orq.CM, cfg_pv2=ligada, cfg_olfato=ConfigOlfato(ligada=True, comida=True, narinas=1))
    with pytest.raises(ValueError):
        DigiBrain(CONFIG_PADRAO, cd, orq.CM, cfg_olfato=pv2.OLFATO)
    DigiBrain(CONFIG_PADRAO, cd, orq.CM, cfg_pv2=ligada, cfg_olfato=pv2.OLFATO)


def test_a_leitura_do_orgao_no_cerebro_e_a_do_corpo():
    co = pv2.OLFATO
    for i in list(range(0, 200)) + [500, 1000, 4096]:
        assert leitura_do_orgao(i, co, 1024) == leitura_orgao(i, 0, co.limiar, co.meia_saturacao, CONFIG_CORPO.escala_receptor)


# ------------------------------------------------------------------ o M-SENS
class _Pc:
    def __init__(self, esq: int, dir_: int) -> None:
        self.olfato_comida_esq, self.olfato_comida_dir = esq, dir_


def test_o_cerebro_nunca_le_a_diferenca_entre_as_narinas():
    """PV2-3: trocar as narinas (esquerda e direita) nao muda nada do que o M-SENS entrega"""
    pares = [(0, 0), (10, 30), (200, 50), (7, 8), (300, 300), (0, 90)]
    for (a, b), (c, d) in zip(pares, pares[1:]):
        s1, s2 = Sens(CONFIG_PADRAO, orq.CM), Sens(CONFIG_PADRAO, orq.CM)
        s1.ligar_olfato(12)
        s2.ligar_olfato(12)
        assert s1._ler_olfato(_Pc(a, b)) == s2._ler_olfato(_Pc(b, a))
        assert s1._ler_olfato(_Pc(c, d)) == s2._ler_olfato(_Pc(d, c))


def test_o_nivel_e_a_variacao_do_cheiro():
    s = Sens(CONFIG_PADRAO, orq.CM)
    s.ligar_olfato(12)
    assert s._ler_olfato(_Pc(10, 30)) == {"c": 20, "dC": 0, "ha": True, "forte": True}      # a primeira decisao: dC = 0
    assert s._ler_olfato(_Pc(4, 6)) == {"c": 5, "dC": -15, "ha": True, "forte": False}
    assert s._ler_olfato(_Pc(0, 0)) == {"c": 0, "dC": -5, "ha": False, "forte": False}
    assert s.estado_interno()["olfato"] == {"c_ant": 0}
    assert RECEPTORES_OLFATO_COMIDA == ("olfato_comida_esq", "olfato_comida_dir")


def test_o_orgao_ligado_sem_o_pv2_continua_falhando_alto():
    """o M-SENS de hoje rejeita o receptor do orgao: so o PV-2 abre a porta"""
    fp, _ = pv2.fabricas("HOJE", "atencioso", 101, 1, orq.ORCAMENTO_POR_DIA)
    from bancada.regras_mundo import simular_vida_fisico
    from digilab.donos import criar_dono
    from digilab.motor_corpo import com_corpo
    from digilab.mundo import DonoComLugar, MotorMundo
    from digilab.temperamento import NEUTRO
    cc = orq.bancada(1, orq.ORCAMENTO_POR_DIA).cfg_corpo_de(orq.bv.EspecVida("atencioso", orq.gl.BRACO_V11, 101))

    def fm_orgao(politica, cfg, s):
        return com_corpo(MotorMundo)(politica, cfg, s, NEUTRO, "brasa", obediencia_desligada=True, cfg_mundo=orq.CM, cfg_corpo=cc,
                                     cfg_olfato=pv2.OLFATO)

    with pytest.raises(ValueError, match="fora do prototipo"):
        simular_vida_fisico(DonoComLugar(criar_dono("atencioso"), "longe", 101, "atencioso", orq.CM), fp(CONFIG_PADRAO), 101, 1,
                            orq.ORCAMENTO_POR_DIA, "atencioso", fm_orgao)


# ------------------------------------------------------------------ o executor
def _cerebro(braco: str, **kw) -> DigiBrain:
    return DigiBrain(CONFIG_PADRAO, orq.config_do_braco("REL", None, True), orq.CM,
                     cfg_pv2=replace(CONFIG_PV2, ligada=True, braco=braco, **kw), cfg_olfato=pv2.OLFATO)


def _exec(c: DigiBrain, ordem: tuple, dc: int, u: int = 0x100) -> str:
    c.motivos.append({})
    cands = [Alvo(t, 0, 0) for t in ordem]
    return c._executar_cheiro(cands, dc, u).tipo


def test_o_olf0_toma_o_preferido_do_motor():
    c = _cerebro("OLF-0")
    assert _exec(c, ("cheiro_virar", "cheiro_seguir"), 0) == "cheiro_virar"
    assert _exec(c, ("cheiro_seguir", "cheiro_virar"), -500) == "cheiro_seguir"


def test_a_pirueta_vem_da_queda_acumulada_e_a_varredura_a_continua():
    for braco, varre in (("OLF-DC", 0), ("OLF-DCV", 2), ("OLF-G", 2)):
        c = _cerebro(braco, l_pirueta=20, n_varredura=2)
        ordem = ("cheiro_virar", "cheiro_seguir")         # o motor prefere virar: o executor so vira na pirueta
        assert _exec(c, ordem, -8) == "cheiro_seguir" and c.executor["A"] == 8
        assert _exec(c, ordem, 5) == "cheiro_seguir" and c.executor["A"] == 0       # subir zera a queda
        assert _exec(c, ordem, -12) == "cheiro_seguir" and c.executor["A"] == 12
        assert _exec(c, ordem, -9) == "cheiro_virar" and c.executor["A"] == 0       # 21 >= L: a pirueta
        assert c.executor["varrer"] == varre and c.executor["piruetas"] == 1
        for _ in range(varre):
            assert _exec(c, ordem, 40) == "cheiro_virar"
        assert _exec(c, ordem, 0) == "cheiro_seguir"


def test_o_placebo_vira_pelos_bits_baixos_do_u_sem_ler_a_queda():
    c = _cerebro("OLF-PLA", taxa_placebo=32, n_varredura=1)
    ordem = ("cheiro_seguir", "cheiro_virar")
    assert _exec(c, ordem, -900, u=0x1FF) == "cheiro_seguir"                     # a queda grande nao vira o placebo
    assert _exec(c, ordem, 0, u=0x31F) == "cheiro_virar"                         # 0x1F = 31 < 32: vira
    assert _exec(c, ordem, 0, u=0x3FF) == "cheiro_virar"                         # a varredura de 1
    assert _exec(c, ordem, 0, u=0x3FF) == "cheiro_seguir"


# ------------------------------------------------------------------ as vidas
@pytest.mark.parametrize("braco", pv2.BRACOS)
def test_o_replay_de_cada_braco(braco):
    """o G1 do replay (conferido dentro de `medir`) e as medidas basicas de uma vida no `longe`"""
    r = pv2.medir(braco, "atencioso", "longe", 101, DIAS)
    assert r["decisoes"] == DIAS * 96
    if braco != "HOJE":
        assert r["decisoes_com_cheiro"] > 0 and r["executor"] == r["viradas"] + r["seguidas"]


def test_g_unidades_os_bracos_com_o_orgao_nao_criam_unidades():
    """G-UNIDADES: decisao a decisao, as unidades de cada braco com o orgao sao as do OLF-0 no mesmo estado (o braco so muda o executor e,
    no OLF-G, a proximidade do cheiro)"""
    for braco in BRACOS_PV2:
        fp, fm = pv2.fabricas(braco, "atencioso", 202, DIAS, orq.ORCAMENTO_POR_DIA)
        registro = fp(CONFIG_PADRAO)
        cerebro = orq.cerebro_de(registro)
        ref = Impulso(cerebro.inatos, cerebro.cd, cfg_pv2=replace(CONFIG_PV2, ligada=True, braco="OLF-0"))
        original = cerebro.m.impulso.unidades
        vistas = []

        def conferir(*a, **kw):
            out = original(*a, **kw)
            outra = ref.unidades(*a, **kw)
            assert [u["chave"] for u in out[0]] == [u["chave"] for u in outra[0]]
            vistas.append(len(out[0]))
            return out

        cerebro.m.impulso.unidades = conferir
        from bancada.regras_mundo import simular_vida_fisico
        from digilab.donos import criar_dono
        from digilab.mundo import DonoComLugar
        simular_vida_fisico(DonoComLugar(criar_dono("atencioso"), "longe", 202, "atencioso", orq.CM), registro, 202, DIAS,
                            orq.ORCAMENTO_POR_DIA * DIAS, "atencioso", fm)
        assert len(vistas) == DIAS * 96


class _ContaRng:
    def __init__(self, rng) -> None:
        self.rng, self.n = rng, 0

    def random(self):
        self.n += 1
        return self.rng.random()


@pytest.mark.parametrize("braco", ("OLF-DCV", "OLF-PLA"))
def test_o_executor_nao_chama_rng(braco):
    """o cerebro so chama a rng de politica no sorteio do M-ARB: uma vez por decisao com u, o placebo inclusive (ele le o u do motor)"""
    fp, fm = pv2.fabricas(braco, "atencioso", 303, DIAS, orq.ORCAMENTO_POR_DIA)
    registro = fp(CONFIG_PADRAO)
    cerebro = orq.cerebro_de(registro)
    contas = []
    agir = cerebro.agir

    def agir_contado(obs, rng):
        c = _ContaRng(rng)
        out = agir(obs, c)
        contas.append(c.n)
        return out

    cerebro.agir = agir_contado
    from bancada.regras_mundo import simular_vida_fisico
    from digilab.donos import criar_dono
    from digilab.mundo import DonoComLugar
    simular_vida_fisico(DonoComLugar(criar_dono("atencioso"), "longe", 303, "atencioso", orq.CM), registro, 303, DIAS,
                        orq.ORCAMENTO_POR_DIA * DIAS, "atencioso", fm)
    assert contas == [0 if m["u"] is None else 1 for m in cerebro.motivos]
    assert any("pv2" in m for m in cerebro.motivos)


def test_o_cenario_da_racao_longe_o_olf_dcv_come_nas_cinco_sementes():
    """o cenario da secao 8.3: a racao no `longe`, sem o oraculo; o OLF-DCV come nas 5 sementes. As decisoes ate comer ficam so
    registradas (o artefato da medicao), sem corte"""
    for s in (101, 202, 303, 404, 505):
        r = pv2.medir("OLF-DCV", "atencioso", "longe", s, DIAS, replay=False)
        assert r["racao"] > 0
