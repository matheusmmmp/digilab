"""SOCIAL_PAR M1, o outro na decisao do modular (docs/ESPEC_SOCIAL_PAR_M1.md, secao 5): a subchave `unidades_sociais` da ConfigDigibrain.

O G2 (desligada, as vidas de hoje byte a byte contra tests/gabaritos/social_m1_de_hoje.json, gravado num commit proprio antes do codigo), o
G2b (ligada sem o outro), as unidades, o alvo, dois outros na mesma celula, o P1, o prox, o G-RECEPTOR-SOCIAL, as combinacoes, o
determinismo e a escolha so com o outro a vista."""
from __future__ import annotations

import ast
import inspect
import json
import sys
import textwrap
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "tests"))
sys.path.insert(0, str(RAIZ / "experiments"))

import gabarito_social_m1 as gab  # noqa: E402
from bancada import parceiro as pc  # noqa: E402
from digilab import mundo
from digilab.config import (CONFIG_DIGIBRAIN_LIGADA, CONFIG_GRUPO_LIGADA, CONFIG_MUNDO_LIGADA, CONFIG_PADRAO, NOV_SOCIAL,
                            PARAMETROS_SOCIAL_M1, TIPOS_ALVO_DIGIBRAIN, TIPOS_ALVO_SOCIAIS, W0_TIPO_SOCIAL, ConfigDigibrain)
from digilab.digibrain.adapt import DigiBrain, Intencao, intencao_da_unidade
from digilab.digibrain.impulso import Impulso
from digilab.digibrain.plast import CLASSES_DESFECHO, Plasticidade
from digilab.digibrain.sens import Sens
from digilab.events import AcaoPet
from digilab.grupo import PetDoGrupo, sementes_do_grupo, simular_grupo
from digilab.modelo_mundo import raiz_inteira
from digilab.mundo import Alvo, PercepcaoSocial, perceber_social

GABARITO = json.loads((RAIZ / "tests" / "gabaritos" / "social_m1_de_hoje.json").read_text(encoding="utf-8"))
LIGADA = {"unidades_sociais": True}


# ================================================================== a config
def test_tipos_sociais_sao_os_do_motor_e_ficam_fora_dos_de_hoje():
    assert TIPOS_ALVO_SOCIAIS == mundo.CANDIDATOS_SOCIAIS
    assert not set(TIPOS_ALVO_SOCIAIS) & set(TIPOS_ALVO_DIGIBRAIN)


def test_numeros_novos_com_status_e_fonte():
    assert W0_TIPO_SOCIAL == 0 and NOV_SOCIAL == 0
    assert set(PARAMETROS_SOCIAL_M1) == {"W0_TIPO_SOCIAL", "NOV_SOCIAL"}
    for status, fonte in PARAMETROS_SOCIAL_M1.values():
        assert status in ("PROPOSTO", "DECIDIDO") and fonte


def test_desligada_por_padrao():
    assert ConfigDigibrain().unidades_sociais is False
    assert CONFIG_DIGIBRAIN_LIGADA.unidades_sociais is False


@pytest.mark.parametrize("outra", ["fala_unidades", "olhar", "passeio"])
def test_combinacoes_levantam(outra):
    with pytest.raises(ValueError, match="unidades_sociais nao se combina"):
        ConfigDigibrain(ligada=True, unidades_sociais=True, **{outra: True})


def test_chave_e_bool():
    with pytest.raises(TypeError):
        ConfigDigibrain(ligada=True, unidades_sociais=1)


# ================================================================== o G2 e o G2b
def test_g2_desligada_as_vidas_de_hoje_byte_a_byte():
    assert gab.gerar() == GABARITO


@pytest.mark.parametrize("semente", gab.SEMENTES)
def test_g2b_sozinho_ligada_sai_igual(semente):
    """o pet sozinho com a chave: o log, o motor, as decisoes e os motivos iguais; o estado do cerebro so ganha as duas classes sociais do
    desfecho e dos consumos, todas em 0 (D-SP-61)"""
    _, desl = gab.vida_sozinho(semente)
    motor, lig = gab.vida_sozinho(semente, LIGADA)
    imp = GABARITO[f"sozinho|{semente}"]
    assert gab._sha(gab._texto([ev.para_dict() for ev in motor.log])) == imp["log"]
    assert gab._sha(gab._texto(motor.estado())) == imp["estado"]
    assert lig.motivos == desl.motivos
    e_lig, e_desl = lig.estado_interno(), desl.estado_interno()
    plast = e_lig["modulos"]["plast"]
    for t in TIPOS_ALVO_SOCIAIS:
        assert plast["desfecho"].pop(t) == [0] * len(plast["receptores"])
        assert plast["consumos"].pop(t) == 0
    assert gab._texto(e_lig) == gab._texto(e_desl)


ENTRADA_B = CONFIG_PADRAO.intervalo_decisao_ticks * 96          # o B entra no dia 1 (o `exportar_gabarito_co6.grupo` com entrada_b = 1)


def _grupo_entrada(semente: int, extra: dict | None = None):
    """o grupo de dois pets do jogo da S, o A no tick 0 e o B no dia 1, 2 dias: o A vive sozinho antes (o G2b do grupo; no par da S os
    dois nascem juntos e se veem na primeira decisao)"""
    ss = sementes_do_grupo(semente, CONFIG_GRUPO_LIGADA.ids)
    pets = []
    for ident, entrada in (("A", 0), ("B", ENTRADA_B)):
        fp, fm = gab.fabricas(ss[ident], extra)
        pets.append(PetDoGrupo(ident, entrada, fp, fm, gab.a0._dono(ss[ident]), gab.a0.DONO, "digibrain"))
    return simular_grupo(gab.a0.CM, semente, pets, 2, cfg_cooperacao=gab.a0.CCO)


def _ticks(g) -> dict:
    """o tick de cada decisao de cada pet (a entrada mais k vezes o intervalo)"""
    passo = CONFIG_PADRAO.intervalo_decisao_ticks
    return {i: {m["k"]: (0 if i == "A" else ENTRADA_B) + m["k"] * passo for m in mm.politica.motivos} for i, mm in g.motores.items()}


@pytest.mark.parametrize("semente", gab.SEMENTES)
def test_g2b_grupo_igual_ate_a_primeira_decisao_social(semente):
    desl, lig = _grupo_entrada(semente), _grupo_entrada(semente, LIGADA)
    tk = _ticks(lig)
    sociais = [tk[i][m["k"]] for i, mm in lig.motores.items() for m in mm.politica.motivos
               if any(u["chave"][1] in TIPOS_ALVO_SOCIAIS for u in m["unidades"])]
    assert sociais, "os dois nunca se viram: o G2b do grupo nao testa nada"
    corte = min(sociais)
    assert corte > 0
    for i in ("A", "B"):
        a = [m for m in desl.motores[i].politica.motivos if tk[i][m["k"]] < corte]
        b = [m for m in lig.motores[i].politica.motivos if tk[i][m["k"]] < corte]
        assert a == b
    assert any(tk["A"][m["k"]] < corte for m in lig.motores["A"].politica.motivos)


# ================================================================== as unidades (3.3)
def _sens_sintetico(outros=(), onde_comeu=()):
    return {"pos": (100, 100), "objetos": [], "ha_cheiro": False, "outros": list(outros), "onde_comeu": list(onde_comeu)}


def _o(ident, classe="seguir", d=10):
    return {"id": ident, "classe": classe, "x": 100 + d, "y": 100, "d": d, "prox": 512}


def test_unidades_no_fim_do_explorar_na_ordem_da_percepcao():
    sens = _sens_sintetico([_o("B"), _o("C")], [_o("C", "onde_comeu"), _o("B", "onde_comeu")])
    lista = Impulso.alvos(sens, None, social=True)
    explorar = [u["chave"] for u in lista if u["acao"] == "explorar"]
    assert explorar == [("explorar", "vagar", None), ("explorar", "seguir", "B"), ("explorar", "seguir", "C"),
                        ("explorar", "onde_comeu", "C"), ("explorar", "onde_comeu", "B")]
    hoje = Impulso.alvos(sens, None)
    assert [u for u in lista if u["tipo"] not in TIPOS_ALVO_SOCIAIS] == hoje


def test_sem_o_outro_nenhuma_unidade_social():
    assert Impulso.alvos(_sens_sintetico(), None, social=True) == Impulso.alvos(_sens_sintetico(), None)


def test_termos_da_unidade_social(vida_b1):
    """na vida: o inato da unidade social e o do vagar mais 0 (M1-2), a novidade 0 (M1-3), o habito e o da linha do explorar"""
    vistas = 0
    for m in vida_b1.grupo.motores.values():
        for mot in m.politica.motivos:
            us = {u["chave"][1]: u["termos"] for u in mot["unidades"] if u["chave"][0] == "explorar"}
            if "vagar" not in us:
                continue
            for t in TIPOS_ALVO_SOCIAIS:
                if t in us:
                    vistas += 1
                    assert us[t]["inato"] == us["vagar"]["inato"] + W0_TIPO_SOCIAL
                    assert us[t]["nov"] == 0 and us[t]["habito"] == us["vagar"]["habito"]
    assert vistas > 0


# ================================================================== o alvo (3.5)
def _cerebro_com_intencao(intencao: Intencao) -> DigiBrain:
    c = DigiBrain(CONFIG_PADRAO, replace(CONFIG_DIGIBRAIN_LIGADA, **LIGADA), CONFIG_MUNDO_LIGADA, semente=101)
    c.motivos = [{}]
    c._pendencia = {"k": 0, "intencao": intencao, "unidade": None, "sens": None, "g_apr": 0, "pediu": False, "alvo": None,
                    "corpo": None, "transicao": None, "mundo": None}
    return c


def test_intencao_social_guarda_tipo_e_ponto():
    u = {"chave": ("explorar", "seguir", "B"), "acao": "explorar", "tipo": "seguir", "objeto": _o("B"), "d": 10}
    assert intencao_da_unidade(u) == Intencao(AcaoPet.EXPLORAR, "seguir", None, (110, 100))


def test_alvo_social_acha_o_candidato_por_tipo_e_ponto():
    cands = [Alvo("vagar", 5, 5), Alvo("seguir", 110, 100), Alvo("onde_comeu", 110, 100)]
    c = _cerebro_com_intencao(Intencao(AcaoPet.EXPLORAR, "onde_comeu", None, (110, 100)))
    assert c.escolher_alvo(AcaoPet.EXPLORAR, cands, None, 0) == Alvo("onde_comeu", 110, 100)


def test_alvo_social_fora_dos_candidatos_levanta():
    c = _cerebro_com_intencao(Intencao(AcaoPet.EXPLORAR, "seguir", None, (111, 100)))
    with pytest.raises(ValueError, match="o alvo social"):
        c.escolher_alvo(AcaoPet.EXPLORAR, [Alvo("seguir", 110, 100)], None, 0)


def test_dois_na_mesma_celula_e_deterministico():
    cands = [Alvo("seguir", 110, 100), Alvo("seguir", 110, 100)]
    a = _cerebro_com_intencao(Intencao(AcaoPet.EXPLORAR, "seguir", None, (110, 100))).escolher_alvo(AcaoPet.EXPLORAR, cands, None, 0)
    b = _cerebro_com_intencao(Intencao(AcaoPet.EXPLORAR, "seguir", None, (110, 100))).escolher_alvo(AcaoPet.EXPLORAR, cands, None, 0)
    assert a == b == cands[0]


# ================================================================== a vida do par com a chave (o espiao so le)
class Espiao(DigiBrain):
    """o modular com a chave, que guarda o que viu (a percepcao social de cada decisao) e o id que o motor deu a cada alvo social"""

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.vistos: list = []
        self.ids_do_motor: dict = {}
        self.motor = None

    def agir(self, obs, rng):
        ps = obs.social
        self.vistos.append((None, None) if ps is None else
                           ({o[0]: (obs.mundo.x + o[1], obs.mundo.y + o[2]) for o in ps.outros}, {o[0]: (o[1], o[2]) for o in ps.onde_comeu}))
        return super().agir(obs, rng)

    def escolher_alvo(self, acao, candidatos, percepcao, u):
        alvo = super().escolher_alvo(acao, candidatos, percepcao, u)
        if alvo is not None and alvo.tipo in TIPOS_ALVO_SOCIAIS:
            self.ids_do_motor[self.k - 1] = self.motor._cands_sociais[alvo]
        return alvo


def _vida_espiao(braco: str, semente: int):
    ss = sementes_do_grupo(semente, CONFIG_GRUPO_LIGADA.ids)
    membros = []
    for i in ("A", "B"):
        _, fm0 = gab.fabricas(ss[i])
        cd = replace(gab.orq.config_do_braco(gab.a0.e6.BRACO, conserto=True), **LIGADA)

        def fp(cfg=None, _s=ss[i], _cd=cd):
            return Espiao(cfg or CONFIG_PADRAO, _cd, gab.a0.e6.CM, semente=_s, cfg_cooperacao=gab.a0.CCO)

        def fm(pol, cfg, s, _fm=fm0, **kw):
            motor = _fm(pol, cfg, s, **kw)
            pol.motor = motor
            return motor
        membros.append(pc.Membro(i, "vivo", fm, fp, gab.a0._dono(ss[i]), gab.a0.DONO, "digibrain"))
    return gab.s.viver(semente, membros, gab.s.contexto(braco, semente), base=False)


@pytest.fixture(scope="module")
def vida_b1():
    return _vida_espiao("B1", 101)


def test_escolha_social_so_com_o_outro_a_vista_e_o_motor_da_o_id_certo(vida_b1):
    n = {"seguir": 0, "onde_comeu": 0}
    for i, m in vida_b1.grupo.motores.items():
        c = m.politica
        for mot in c.motivos:
            acao, tipo, ident = mot["escolha"]
            if tipo not in TIPOS_ALVO_SOCIAIS:
                continue
            n[tipo] += 1
            outros, comeu = c.vistos[mot["k"]]
            ponto = (outros if tipo == "seguir" else comeu)[ident]
            assert (mot["alvo"]["x"], mot["alvo"]["y"]) == ponto
            assert c.ids_do_motor[mot["k"]] == ident
    assert n["seguir"] > 0 and n["onde_comeu"] > 0


def test_p1_das_classes_sociais_anda_so_com_a_chave(vida_b1):
    for m in vida_b1.grupo.motores.values():
        pl = m.politica.m.plast
        assert pl.classes == CLASSES_DESFECHO + TIPOS_ALVO_SOCIAIS
        escolhas = [x["escolha"][1] for x in m.politica.motivos]
        for t in TIPOS_ALVO_SOCIAIS:
            assert (pl.consumos[t] > 0) == (t in escolhas)


def test_p1_onde_comeu_que_leva_a_comer_sai_do_zero_e_seguir_parado_fica_em_zero(vida_b1):
    """sintetico, com o corpo de uma decisao da vida: N decisoes `onde_comeu` em que a fome cai (o pet comeu la) tiram o incentivo da
    classe do 0; N decisoes `seguir` sem mudanca no corpo deixam o desfecho e o incentivo em 0"""
    c = vida_b1.grupo.motores["A"].politica
    recs = c.m.sens.receptores
    pc_corpo = c._pendencia["sens"]["pc"]                 # o corpo da ultima decisao da vida (a pendencia que nao fechou)
    pl = Plasticidade(replace(CONFIG_DIGIBRAIN_LIGADA, **LIGADA))
    pl.montar(recs)
    S = c.S
    i_fome = recs.index("fome")
    l0 = [S // 2] * len(recs)
    l1 = list(l0)
    l1[i_fome] += S // 4                         # a leitura da fome sobe: menos fome (a leitura e o quanto o receptor esta satisfeito)
    drives = c.m.afeto.drives(recs)
    for _ in range(20):
        pl.consequencia_p1("explorar", "onde_comeu", l0, l1, (0, 0), (0, 0), S)
        pl.consequencia_p1("explorar", "seguir", l0, list(l0), (0, 0), (0, 0), S)
    assert pl.desfecho["seguir"] == [0] * len(recs)
    assert pl.incentivo(pc_corpo, "seguir", drives) == 0
    assert pl.desfecho["onde_comeu"][i_fome] > 0
    assert pl.incentivo(pc_corpo, "onde_comeu", drives) > 0


def test_determinismo_com_a_chave():
    a = gab.impressao_par("C", 202, LIGADA)
    b = gab.impressao_par("C", 202, LIGADA)
    assert a == b


# ================================================================== o M-SENS (3.2)
def _sens() -> Sens:
    return Sens(CONFIG_PADRAO, CONFIG_MUNDO_LIGADA, social=True)


def test_sem_percepcao_social_listas_vazias():
    assert _sens().ler_outros(None, (0, 0)) == ([], [])


def test_prox_do_outro_e_o_de_um_objeto_na_mesma_posicao():
    """o d da PercepcaoSocial (o motor) esta na mesma unidade do d dos objetos (subunidades): um outro e um objeto na mesma posicao
    relativa dao o mesmo d e o mesmo prox"""
    s = _sens()
    x, y, dx, dy = 1000, 1000, 70, -40
    ps = perceber_social(x, y, 0, [("B", x + dx, y + dy, "ocioso")], {"B": (x + dx, y + dy, 0)}, {}, s.raio)
    outros, comeu = s.ler_outros(ps, (x, y))
    d_objeto = mundo.distancia(dx, dy)               # a conta dos `vistos` do motor
    assert outros[0]["d"] == comeu[0]["d"] == d_objeto == raiz_inteira(dx * dx + dy * dy)
    assert outros[0]["prox"] == comeu[0]["prox"] == s.proximidade(d_objeto)
    assert (outros[0]["x"], outros[0]["y"]) == (comeu[0]["x"], comeu[0]["y"]) == (x + dx, y + dy)


def test_desligada_nenhum_campo_novo():
    c = DigiBrain(CONFIG_PADRAO, CONFIG_DIGIBRAIN_LIGADA, CONFIG_MUNDO_LIGADA, semente=101)
    assert c.m.sens.le_outro is False
    assert c.m.plast.classes == CLASSES_DESFECHO


def test_outro_malformado_levanta():
    with pytest.raises(ValueError):
        _sens().ler_outros(PercepcaoSocial((("B", 1, 2, -3, "ocioso"),), (), ()), (0, 0))


def test_g_receptor_social_so_le_outros_e_onde_comeu():
    """pela AST: no `ler_outros`, o unico atributo lido da percepcao social (`ps`) e `outros` e `onde_comeu`; no `codificar`, a percepcao
    social so vai ao `ler_outros` (e ao `_ler_social` da CO6, e ao `dever.social` da CO7, que sao de antes)"""
    arvore = ast.parse(textwrap.dedent(inspect.getsource(Sens.ler_outros)))
    lidos = {n.attr for n in ast.walk(arvore) if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id == "ps"}
    assert lidos == {"outros", "onde_comeu"}
    for campo in ("reputacao", "peso_dever", "sentidos", "toque"):
        assert campo not in inspect.getsource(Sens.ler_outros)
