"""J5, etapa 1 (docs/TAREFA_V2_PET_QUE_PENSA.md, secao 2.1 e a tabela das etapas): os modelos do mundo, so observando.

- G-INT: o modulo so faz conta em inteiros (AST: nenhuma constante float, nenhuma divisao `/`, nenhum `math`, `random`, `float` ou
  `round`), e so importa `config` e `events`;
- G-TETO-MODELO: a contagem (76 no regime quimica) e o teto que falha alto;
- G-RECEPTOR-MM: so a percepcao; um quimico sem receptor, o Estado, o registro do mundo (o resto do `ocorrido`) e a fruta de cada arvore no
  layout nao mudam os modelos;
- a conta exata de um passo de cada: o mapa, o custo de andar, o desfecho (com a energia corrigida pelo andar previsto);
- G-OBS-MM: com os modelos observando, as vidas da etapa 0 (`tests/gabaritos/pet_que_pensa_vidas_de_hoje.json`) saem byte a byte iguais;
- G1: o replay refaz os modelos bit a bit.
So as sementes dos testes.
"""
from __future__ import annotations

import ast
import json
import math
import random
import sys
from dataclasses import fields, replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import bancada_v2 as bv  # noqa: E402
import gabarito_pet_que_pensa as gp  # noqa: E402
from digilab import modelo_mundo as mm  # noqa: E402
from digilab.config import (CONFIG_CORPO_DRIVES, CONFIG_MODELO_MUNDO, CONFIG_MODELO_MUNDO_LIGADA, CONFIG_MUNDO_LIGADA,  # noqa: E402
                            CONFIG_PADRAO, LAYOUT_MUNDO_AFASTADO, ConfigModeloMundo)
from digilab.corpo import Corpo  # noqa: E402
from digilab.corpo import div_arred as div_corpo  # noqa: E402
from digilab.events import AcaoPet  # noqa: E402
from digilab.modelo_mundo import TIPOS, ModeloMundo, PoliticaComModelo, n_valores  # noqa: E402
from digilab.motor_corpo import PercepcaoCorpo  # noqa: E402
from digilab.mundo import PercepcaoMundo  # noqa: E402
from digilab.policies.lobos import div_arred as div_lobos  # noqa: E402
from digilab.policy import Observacao  # noqa: E402
from digilab.state import Estado  # noqa: E402

CM = CONFIG_MODELO_MUNDO_LIGADA
S = CM.escala
CMUNDO = CONFIG_MUNDO_LIGADA
SUB = CMUNDO.sub
GABARITO = json.loads(gp.ARQUIVO.read_text(encoding="utf-8"))
CASOS = dict(gp.casos())
SEM_CORPO = sorted(k for k in CASOS if "~instinto|" in k and k.startswith("bancada|"))      # o P0 do instinto: braco sem regime
COM_CORPO = sorted(k for k in CASOS if k not in SEM_CORPO)


def lugar(nome: str) -> tuple[int, int]:
    return next((x, y) for n, x, y in mm.lugares_do_layout(CMUNDO) if n == nome)


def pc(fome=S, higiene=S, energia=S, humor=S, saude=S, **novos) -> PercepcaoCorpo:
    return PercepcaoCorpo(fome=fome, higiene=higiene, energia=energia, humor=humor, saude=saude, **novos)


def pm(x: int, y: int, vistos=()) -> PercepcaoMundo:
    return PercepcaoMundo(x=x, y=y, regiao=0, vistos=tuple(vistos), cheiro=0, direcao_cheiro=0, alvo_pendente=None)


def obs_de(corpo: PercepcaoCorpo, mundo: PercepcaoMundo, **kw) -> Observacao:
    return Observacao(vetor_estado=(0.8,) * 6 + (0.0, 0.5), ticks_desde_cuidado=0, total_cuidados=0, corpo=corpo, mundo=mundo, **kw)


def modelo(**kw) -> ModeloMundo:
    return ModeloMundo(replace(CM, **kw), CMUNDO)


def comeu(tipo: str, situacao: str = "madura", **resto) -> dict:
    return {"comeu": {"id": 7, "tipo": tipo, "situacao": situacao, "como": "comer", **resto}}


# ================================================================== a config e o registro
def test_config_e_registro():
    assert set(mm.PARAMETROS_MODELO_MUNDO) == {f.name for f in fields(ConfigModeloMundo)}
    assert all(st in ("PROPOSTO", "DECIDIDO") and fonte for st, fonte in mm.PARAMETROS_MODELO_MUNDO.values())
    assert not CONFIG_MODELO_MUNDO.ligada and CM.ligada
    assert (CM.passo_desfecho, CM.passo_mapa, CM.raio_ancora_celulas, CM.teto_modelo) == (S // 4, S // 8, 2, 200)   # PP-6
    for ruim in ({"passo_desfecho": S + 1}, {"passo_mapa": -1}, {"raio_ancora_celulas": 0}, {"teto_modelo": 0}, {"escala": 1.0}):
        with pytest.raises(ValueError):
            replace(CM, **ruim)


# ================================================================== G-INT e G-RECEPTOR-MM (o modulo)
ARVORE = ast.parse((RAIZ / "digilab" / "modelo_mundo.py").read_text(encoding="utf-8"))


def test_g_int_so_inteiros():
    for no in ast.walk(ARVORE):
        assert not (isinstance(no, ast.Constant) and isinstance(no.value, float)), f"constante float na linha {no.lineno}"
        assert not isinstance(no, ast.Div), "divisao `/` no modulo dos modelos"
        if isinstance(no, ast.Name):
            assert no.id not in ("float", "math", "random", "round"), no.id


def test_g_receptor_mm_so_importa_config_e_events():
    importados = set()
    for no in ast.walk(ARVORE):
        if isinstance(no, ast.ImportFrom):
            importados.add(("." * no.level) + (no.module or ""))
        elif isinstance(no, ast.Import):
            importados |= {a.name for a in no.names}
    assert importados == {"__future__", "dataclasses", ".config", ".events"}


def test_as_contas_inteiras_sao_as_de_sempre():
    rng = random.Random(11)
    for n in list(range(200)) + [rng.randrange(10 ** 12) for _ in range(2000)]:
        assert mm.raiz_inteira(n) == math.isqrt(n)
    for _ in range(3000):
        n, d = rng.randint(-10 ** 6, 10 ** 6), rng.randint(1, 5000)
        assert mm.div_arred(n, d) == div_corpo(n, d) == div_lobos(n, d)
    for _ in range(3000):
        dx, dy, r = rng.randint(-300, 300), rng.randint(-300, 300), rng.randint(0, 200)
        assert mm.dentro(dx, dy, r) == (math.isqrt(dx * dx + dy * dy) <= r)
    with pytest.raises(ValueError):
        mm.raiz_inteira(-1)


# ================================================================== G-TETO-MODELO
def test_g_teto_modelo():
    assert len(mm.lugares_do_layout(CMUNDO)) == 10 and mm.lugares_do_layout(CMUNDO)[-1][0] == mm.COMEDOURO
    assert n_valores(5, 10) == 5 * 5 + 1 + 10 * 5 == 76 < CM.teto_modelo            # o regime quimica (PP-6)
    m = modelo()
    m.decisao(obs_de(pc(), pm(*lugar("J1"))))
    assert m.n_valores() == 76
    assert all(type(v) is int for vs in list(m.desfecho.values()) + list(m.mapa.values()) for v in vs) and type(m.andar) is int
    corpo = Corpo.de_estado(Estado(), CONFIG_PADRAO, CONFIG_CORPO_DRIVES).receptores()   # os drives novos: 10 receptores
    m10 = modelo()
    m10.decisao(obs_de(PercepcaoCorpo(**corpo), pm(0, 0)))
    assert m10.n_valores() == n_valores(10, 10) == 101
    with pytest.raises(ValueError, match="G-TETO-MODELO"):
        modelo(teto_modelo=76).decisao(obs_de(pc(), pm(0, 0)))
    modelo(teto_modelo=77).decisao(obs_de(pc(), pm(0, 0)))


# ================================================================== a conta exata de um passo de cada
def test_um_passo_do_mapa():
    jx, jy = lugar("J1")
    m = modelo()
    # o pet ainda nao viu o tronco: a fruta perto dele fica solta
    m.decisao(obs_de(pc(), pm(jx + 200, jy, [(1, "a", -200 + 5, 0, 195)])))
    assert m.vistas_soltas == 1 and "J1" not in m.lugares_vistos and not any(m.mapa["J1"])
    # visto (a 96 subunidades, o raio da visao), a fruta madura a 30 dele conta; a podre e a bola nao
    m.decisao(obs_de(pc(), pm(jx + 96, jy, [(2, "a", -96 + 30, 0, 66), (3, "b_podre", -96, 0, 96), (0, "bola", -90, 0, 90)])))
    assert m.lugares_vistos["J1"] == 1
    assert m.mapa["J1"] == [0, S // 8, 0, 0, 0]                                       # div_arred(1024 x 128, 1024)
    m.decisao(obs_de(pc(), pm(jx, jy, [(2, "a", 0, 0, 0)])))
    assert m.mapa["J1"] == [0, 128 + mm.div_arred((S - 128) * 128, S), 0, 0, 0] == [0, 240, 0, 0, 0]
    m.decisao(obs_de(pc(), pm(jx, jy, [(4, "racao", 3, 0, 3)])))                    # outro tipo: o "a" esquece
    assert m.mapa["J1"] == [128, 240 + mm.div_arred(-240 * 128, S), 0, 0, 0] == [128, 210, 0, 0, 0]
    # a ancora: ate 2 celulas (32) do tronco; a 33, solta
    soltas = m.vistas_soltas
    m.decisao(obs_de(pc(), pm(jx, jy, [(5, "c", 33, 0, 33)])))
    assert m.vistas_soltas == soltas + 1 and m.mapa["J1"][3] == 0
    assert m.vistas_ancoradas == 3


def test_a_ancora_vai_ao_lugar_visto_mais_perto():
    m = modelo(raio_ancora_celulas=40)                         # um raio grande, para dois lugares disputarem
    (ax, ay), (bx, by) = lugar("J1"), lugar("J3")
    m.decisao(obs_de(pc(), pm(ax, ay)))
    m.decisao(obs_de(pc(), pm(bx, by)))
    assert {"J1", "J3"} <= set(m.lugares_vistos)
    m.decisao(obs_de(pc(), pm(bx, by, [(1, "b", 2, 0, 2)])))       # bem perto do J3
    assert m.mapa["J3"][2] == S // 8 and m.mapa["J1"][2] == 0


def test_um_passo_do_andar_e_do_desfecho():
    m = modelo()
    m.decisao(obs_de(pc(fome=500, energia=1000), pm(100, 100)))
    m.consequencia(AcaoPet.COMER, comeu("a"), obs_de(pc(fome=600, energia=990, humor=1000), pm(160, 100)))
    amostra = mm.div_arred(-10 * S, 60)
    assert amostra == -171
    assert m.andar == mm.div_arred(amostra * CM.passo_desfecho, S) == -43 and m.amostras_andar == 1
    previsto = mm.div_arred(-43 * 60, S)
    assert previsto == -3
    delta = [100, 0, -10 - previsto, 1000 - S, 0]                                    # a energia corrigida pelo andar previsto
    assert m.desfecho["a"] == [mm.div_arred(v * CM.passo_desfecho, S) for v in delta] == [25, 0, -2, -6, 0]
    assert m.consumos["a"] == 1 and all(not any(v) for t, v in m.desfecho.items() if t != "a")
    # o segundo passo anda em direcao ao novo delta
    m.decisao(obs_de(pc(fome=500), pm(160, 100)))
    m.consequencia(AcaoPet.COMER, comeu("a"), obs_de(pc(fome=600), pm(160, 100)))   # sem andar: o custo nao aprende
    assert m.amostras_andar == 1 and m.desfecho["a"][0] == 25 + mm.div_arred((100 - 25) * CM.passo_desfecho, S) == 44


def test_a_podre_o_achou_e_comeu_e_o_comer_sem_comida():
    m = modelo()
    m.decisao(obs_de(pc(humor=800), pm(0, 0)))
    m.consequencia(AcaoPet.COMER, comeu("b", "podre"), obs_de(pc(humor=700), pm(0, 0)))
    assert m.desfecho["podre"][3] == mm.div_arred(-100 * CM.passo_desfecho, S) == -25 and m.consumos["podre"] == 1
    m.decisao(obs_de(pc(fome=500), pm(0, 0)))
    m.consequencia(AcaoPet.EXPLORAR, comeu("c"), obs_de(pc(fome=600), pm(30, 0)))    # o achou e comeu: so contado
    assert m.consumos_nao_usados["c"] == 1 and not any(m.desfecho["c"]) and m.amostras_andar == 0
    m.decisao(obs_de(pc(energia=1000), pm(0, 0)))
    m.consequencia(AcaoPet.COMER, {"comeu": None}, obs_de(pc(energia=990), pm(60, 0)))   # andou e nao comeu: o andar aprende
    assert m.amostras_andar == 1 and sum(m.consumos.values()) == 1
    m.decisao(obs_de(pc(), pm(0, 0)))
    m.consequencia(AcaoPet.BRINCAR, {"comeu": None}, obs_de(pc(energia=900), pm(60, 0)))   # brincar: nada
    assert m.amostras_andar == 1


# ================================================================== G-RECEPTOR-MM (a percepcao so)
def test_quimico_sem_receptor_nao_muda_a_percepcao():
    c = Corpo.de_estado(Estado(), CONFIG_PADRAO, CONFIG_CORPO_DRIVES)
    antes = PercepcaoCorpo(**c.receptores())
    c.q["alimento"], c.q["vida"] = 300000, 1000
    assert PercepcaoCorpo(**c.receptores()) == antes


def _sequencia(m: ModeloMundo, rng: random.Random, ruido: bool) -> None:
    """a mesma sequencia de percepcoes; com `ruido`, muda tudo o que os modelos nao leem: o Estado, o relogio do cuidado, a informacao do
    dono e o resto do `ocorrido` (o registro do motor: a distancia que ele anota, a energia gasta, a fome antes e depois, o alvo)"""
    r2 = random.Random(rng.random())
    for _ in range(300):
        x, y = rng.randint(0, 1000), rng.randint(0, 470)
        vistos = [(i, rng.choice(["a", "b", "c", "racao", "a_podre", "bola"]), rng.randint(-90, 90), rng.randint(-90, 90), 0)
                  for i in range(rng.randint(0, 4))]
        kw = {}
        if ruido:
            kw = dict(vetor_estado=tuple(r2.random() for _ in range(8)), ticks_desde_cuidado=r2.randint(0, 900),
                      total_cuidados=r2.randint(0, 50), info_frutas=(1.0, -1.0, 0.0))
        corpo = pc(fome=rng.randint(0, S), energia=rng.randint(0, S), humor=rng.randint(0, S))
        o = obs_de(corpo, pm(x, y, vistos))
        if kw:
            o = replace(o, **kw)
        m.decisao(o)
        acao = rng.choice([AcaoPet.COMER, AcaoPet.EXPLORAR, AcaoPet.BRINCAR])
        oc = {"comeu": None} if rng.random() < 0.4 else comeu(rng.choice(["racao", "a", "b", "c"]), rng.choice(["madura", "podre"]))
        if ruido:
            oc = {**oc, "deslocamento": r2.randint(0, 999), "energia_gasta": r2.random(), "chegou": r2.random() < 0.5,
                  "alvo": {"tipo": "comida", "x": r2.randint(0, 9)}}
            if oc["comeu"] is not None:
                oc["comeu"] = {**oc["comeu"], "fome_antes": r2.random(), "humor_depois": r2.random(), "id": r2.randint(0, 99)}
        m.consequencia(acao, oc, obs_de(pc(fome=rng.randint(0, S), energia=rng.randint(0, S)),
                                        pm(x + rng.randint(-60, 60), y + rng.randint(-60, 60))))


def test_g_receptor_mm_o_que_os_modelos_nao_leem_nao_os_muda():
    a, b = modelo(), modelo()
    _sequencia(a, random.Random(22), False)
    _sequencia(b, random.Random(22), True)
    assert json.dumps(a.para_dict(), sort_keys=True) == json.dumps(b.para_dict(), sort_keys=True)
    assert sum(a.consumos.values()) > 0 and a.amostras_andar > 0 and a.vistas_ancoradas > 0


def test_a_fruta_de_cada_arvore_no_layout_nao_entra():
    trocadas = tuple((i, x, y, {"a": "c", "b": "a", "c": "b"}[f]) for i, x, y, f in CMUNDO.layout.arvores)
    cm2 = replace(CMUNDO, layout=replace(CMUNDO.layout, arvores=trocadas))
    assert mm.lugares_do_layout(cm2) == mm.lugares_do_layout(CMUNDO)
    a, b = ModeloMundo(CM, CMUNDO), ModeloMundo(CM, cm2)
    _sequencia(a, random.Random(5), False)
    _sequencia(b, random.Random(5), False)
    assert a.para_dict() == b.para_dict()


# ================================================================== as falhas altas
def test_falhas_altas():
    with pytest.raises(ValueError, match="desligada"):
        ModeloMundo(CONFIG_MODELO_MUNDO, CMUNDO)
    with pytest.raises(ValueError, match="mundo fisico"):
        ModeloMundo(CM, replace(CMUNDO, ligada=False))
    m = modelo()
    with pytest.raises(RuntimeError, match="sem o corpo"):
        m.decisao(Observacao(vetor_estado=(0.8,) * 8, ticks_desde_cuidado=0, total_cuidados=0, mundo=pm(0, 0)))
    with pytest.raises(RuntimeError, match="sem o mundo"):
        m.decisao(obs_de(pc(), None))
    with pytest.raises(RuntimeError, match="sem a decisao"):
        m.consequencia(AcaoPet.COMER, {"comeu": None}, obs_de(pc(), pm(0, 0)))
    m.decisao(obs_de(pc(), pm(0, 0)))
    with pytest.raises(ValueError, match="receptores"):
        m.consequencia(AcaoPet.COMER, {"comeu": None}, obs_de(pc(tedio=0), pm(0, 0)))
    with pytest.raises(ValueError, match="fora de inteiros"):
        m.decisao(obs_de(pc(fome=S + 1), pm(0, 0)))
    m.decisao(obs_de(pc(), pm(0, 0)))
    with pytest.raises(ValueError, match="comida desconhecida"):
        m.consequencia(AcaoPet.COMER, comeu("bola"), obs_de(pc(), pm(0, 0)))
    with pytest.raises(ValueError):
        m.consumo("pedra", [0] * 5)


# ================================================================== G-OBS-MM e G1 (as vidas)
class BancadaComModelo(bv.Bancada):
    """a bancada com a politica de cada vida embrulhada pelos modelos (so para os testes; a chave da bancada e da etapa 4, do D)"""

    def politica(self, espec, cfg=None):
        p = PoliticaComModelo(super().politica(espec, cfg), self.cfg_mundo_de(bv.mundo_de(espec.mundo)), CM)
        CRIADAS.append(p)
        return p


def _embrulho(cm_mundo):
    def embrulha(p):
        w = PoliticaComModelo(p, cm_mundo, CM)
        CRIADAS.append(w)
        return w
    return embrulha


CRIADAS: list[PoliticaComModelo] = []
BANCADAS = gp.bancadas(BancadaComModelo)


@pytest.mark.parametrize("chave", COM_CORPO)
def test_g_obs_mm_a_vida_com_os_modelos_e_a_de_hoje(chave):
    CRIADAS.clear()
    caso = CASOS[chave]
    emb = None if chave.startswith("bancada|") else _embrulho(gp.LAYOUTS[caso[0]])
    assert gp.vida_de_hoje(chave, caso, BANCADAS, emb) == GABARITO[chave]
    m = CRIADAS[0].modelo                                       # a vida (o replay conferido da bancada cria outro embrulho depois)
    assert m.k > 0 and m.n_valores() == 76 and m.lugares_vistos     # os modelos observaram a vida inteira


@pytest.mark.parametrize("chave", SEM_CORPO)
def test_sem_corpo_os_modelos_falham_alto(chave):
    montagem, espec = CASOS[chave]
    with pytest.raises(RuntimeError, match="sem o corpo"):
        BANCADAS[montagem].vida(espec)


def test_os_modelos_aprendem_numa_vida():
    """mecanismo, sem gate de pesquisa: numa vida de 3 dias a racao mata a fome no desfecho, andar gasta energia e o mapa aprende o tipo
    de alguma arvore"""
    CRIADAS.clear()
    gp.vida_direta("padrao", "lobos", 101, _embrulho(gp.LAYOUTS["padrao"]))
    m = CRIADAS[0].modelo
    assert m.desfecho["racao"][m.receptores.index("fome")] > 0 and m.consumos["racao"] > 0
    assert m.andar < 0 and m.amostras_andar > 0
    assert any(max(v[1:4]) > S // 2 for nome, v in m.mapa.items() if nome != mm.COMEDOURO)


G1_CASOS = [c for c in COM_CORPO if c.startswith("bancada|") and c.endswith("|101") and "atencioso|comedouro" in c]


@pytest.mark.parametrize("chave", G1_CASOS)
def test_g1_o_replay_refaz_os_modelos(chave):
    montagem, espec = CASOS[chave]
    b = BANCADAS[montagem]
    CRIADAS.clear()
    v = b.vida(espec)
    original = CRIADAS[0]
    CRIADAS.clear()
    b.rejogar(v.motor.log, espec)
    refeita = CRIADAS[-1]
    assert json.dumps(refeita.modelo.para_dict(), sort_keys=True) == json.dumps(original.modelo.para_dict(), sort_keys=True)
    assert original.modelo.k > 0


def test_o_afastado_usa_o_layout_dele():
    cm2 = replace(CMUNDO, layout=LAYOUT_MUNDO_AFASTADO)
    assert mm.lugares_do_layout(cm2) != mm.lugares_do_layout(CMUNDO)
    CRIADAS.clear()
    BANCADAS["simples"].vida(bv.EspecVida("atencioso", "P1-quimica", 101, None, "fisico_afastado", "lobos", "comedouro"))
    assert CRIADAS[0].modelo.lugares == mm.lugares_do_layout(cm2)


def test_o_embrulho_repassa_o_que_o_cerebro_tem():
    from digilab.config import CONFIG_LOBOS
    from digilab.instinto_mundo import PoliticaInstintoMundo
    from digilab.policies.lobos import PoliticaLobos
    cerebro = PoliticaLobos(CONFIG_PADRAO, CONFIG_LOBOS, cfg_mundo=CMUNDO, cfg_corpo=CONFIG_CORPO_DRIVES)
    p = PoliticaComModelo(cerebro, CMUNDO, CM)
    for nome in ("observar", "receber_acao_dono", "escolher_alvo", "escolher_fruta", "consequencia_corpo", "mudanca_no_corpo",
                 "ultima_regra", "gancho_que_nao_existe"):
        assert hasattr(p, nome) == hasattr(cerebro, nome)
    assert hasattr(p, "consequencia_mundo") and p.estado_interno() == cerebro.estado_interno()
    # o cerebro sem o gancho: os modelos aprendem e nada chega a ele
    inst = PoliticaInstintoMundo(CONFIG_PADRAO)
    q = PoliticaComModelo(inst, CMUNDO, CM)
    assert not hasattr(inst, "consequencia_mundo")
    q.modelo.decisao(obs_de(pc(fome=500), pm(0, 0)))
    q.consequencia_mundo(AcaoPet.COMER, comeu("racao"), obs_de(pc(fome=700), pm(0, 0)))
    assert q.modelo.consumos["racao"] == 1
    assert TIPOS == ("racao", "a", "b", "c", "podre")


@pytest.mark.parametrize("chave", SEM_CORPO)
def test_g2_as_vidas_sem_corpo_sao_as_do_gabarito(chave):
    """o P0 do instinto nao tem corpo (os modelos nao o embrulham): a vida de hoje, pelo codigo atual, e a do gabarito"""
    assert gp.vida_de_hoje(chave, CASOS[chave]) == GABARITO[chave]
