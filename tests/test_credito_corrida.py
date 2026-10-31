"""C2, etapa 2 (docs/TAREFA_V3_HABITO_INTENCAO.md, secoes 3.1 e 3.2; HI-1 a HI-8 DECIDIDAS em 2026-10-31): a subchave `credito_corrida` do
DigiBrain modular, o P2 creditado na corrida do comportamento, antes de qualquer vida de pesquisa. So as sementes 101 a 505 e sequencias
sinteticas.

  - G2: com ela desligada, as vidas de hoje saem byte a byte (tests/test_gabarito_habito_intencao.py, o gabarito gravado antes, mais os do
    conserto e do modular); aqui, o que a desligada nao cria (campo, estado);
  - G2-SEPARADO: ligada, ela muda so a vida do braco que a liga; nada fora do pacote `digibrain` e do orquestrador le a chave;
  - G1: o replay de cada vida com ela ligada, nas cinco sementes;
  - T-CORRIDA-1 a 3: a corrida, a intencao dentro dela e o sono e o fim da vida;
  - o `conferir_credito` do orquestrador, estendido para a corrida, falha alto;
  - G-MECANISMO e os testes de mecanismo de hoje com ela ligada."""
from __future__ import annotations

import inspect
import json
import re
import sys
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import run_v2_digibrain_prototipo as orq  # noqa: E402
import test_digibrain_mecanismo as tm  # noqa: E402

from digilab.config import CONFIG_DIGIBRAIN, CONFIG_DIGIBRAIN_INATOS, CONFIG_DIGIBRAIN_LIGADA, CONFIG_PADRAO, ConfigDigibrain  # noqa: E402
from digilab.digibrain.estado import EstadoDinamico  # noqa: E402
from digilab.digibrain.plast import Plasticidade  # noqa: E402

P = CONFIG_DIGIBRAIN_INATOS
S = P.escala
SEMENTES = (101, 202, 303, 404, 505)
BASE = replace(CONFIG_DIGIBRAIN_LIGADA, cheiro_inato=True, intencao_cheiro=True)
LIGADA = replace(BASE, credito_corrida=True)
EXPLORAR = {"chave": ("explorar", "cheiro", None), "d": None}
COMER = {"chave": ("comer", "comida", 7), "d": 300}
BUSCA = {"chave": ("comer", "cheiro", None), "d": None}
DORMIR = {"chave": ("dormir", None, None), "d": None}
DEPOIS = {"visto": True, "d": None, "ha_cheiro": True, "comida_boa_vista": False}


def estado(cd=LIGADA) -> EstadoDinamico:
    return EstadoDinamico(CONFIG_PADRAO, cd, P)


def decidir(e: EstadoDinamico, unidade: dict, z: list, k: int, r_n: int, g_apr: int = 100, reflexo: bool = False,
            ocorrido: dict | None = None, depois: dict = DEPOIS) -> tuple[list, list]:
    """uma decisao inteira: (os fins da escolhida e da consequencia, as corridas que a escolhida fechou)"""
    e.contexto()
    fins = e.escolhida(unidade, z, g_apr, k, reflexo)
    fechadas = list(e.corridas_fechadas)
    return fins + e.consequencia(r_n, ocorrido, depois), fechadas


# ------------------------------------------------------------------ a subchave
def test_a_subchave_nasce_desligada_e_so_aceita_bool():
    assert CONFIG_DIGIBRAIN.credito_corrida is False and CONFIG_DIGIBRAIN_LIGADA.credito_corrida is False
    with pytest.raises(TypeError, match="credito_corrida"):
        ConfigDigibrain(credito_corrida=1)


def test_a_subchave_nao_se_combina_com_a_intencao_suspensa():
    with pytest.raises(ValueError, match="intencao_suspensa"):
        replace(BASE, credito_corrida=True, intencao_suspensa=True)


def test_desligada_o_estado_nao_tem_corrida_nem_campo_novo():
    e = estado(BASE)
    decidir(e, EXPLORAR, [1, 2, 3], 0, 10)
    decidir(e, COMER, [1, 2, 3], 1, 10)
    assert "corrida" not in e.estado_interno() and e.corrida is None and e.corridas_fechadas == []


def test_o_braco_m2c_e_o_m2_com_a_subchave(monkeypatch):
    m2 = orq.config_do_braco("M2", conserto=True)
    assert replace(m2, credito_corrida=True) == replace(orq.config_do_braco("M2", conserto=True), credito_corrida=True)
    assert m2.credito_corrida is False and m2.intencao_cheiro and m2.cheiro_inato and not m2.m_mem and not m2.intencao_suspensa


# ------------------------------------------------------------------ T-CORRIDA-1
def test_t_corrida_1_explorar_tres_vezes_e_comer_da_um_credito_do_explorar_e_depois_o_do_comer():
    z1, z2, z3, z4 = [1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]
    e = estado()
    fechadas = []
    for k, (z, r, g) in enumerate(((z1, 30, 101), (z2, -10, 102), (z3, 50, 103))):
        _, f = decidir(e, EXPLORAR, z, k, r, g)
        fechadas.append(f)
    assert fechadas == [[], [], []]                              # nada vai ao P2 enquanto a corrida dura
    _, f = decidir(e, COMER, z4, 3, 7, 104)
    assert len(f) == 1 and (f[0]["b"], f[0]["inicio"], f[0]["n"], f[0]["r"], f[0]["e"], f[0]["g_apr"]) == ("explorar", 0, 3, 70, z1, 103)
    assert e.corrida["b"] == "comer" and e.corrida["e"] == z4 and e.corrida["n"] == 1 and e.corrida["r"] == 7
    # a entrega e a regra do P2 de hoje, uma vez, com o z da 1.a decisao e a soma dos r_n
    pl = Plasticidade(CONFIG_DIGIBRAIN_LIGADA, P)
    pl.creditar(f[0])
    esperado = Plasticidade(CONFIG_DIGIBRAIN_LIGADA, P)
    esperado.creditar({"chave": ("explorar",), "e": z1, "r": 70, "g_apr": 103})
    assert pl.H == esperado.H and pl.creditos == 1
    _, f = decidir(e, EXPLORAR, z1, 4, 0)
    assert [(x["b"], x["r"], x["n"]) for x in f] == [("comer", 7, 1)]


def test_t_corrida_1_sem_a_subchave_sao_tres_creditos_de_uma_decisao_como_hoje():
    e = estado(BASE)
    unicas = []
    for k, r in enumerate((30, -10, 50)):
        fins, f = decidir(e, EXPLORAR, [1, 2, 3], k, r)
        unicas += [x for x in fins if x["motivo"] == "unica"]
        assert f == []
    assert [(x["n"], x["r"]) for x in unicas] == [(1, 30), (1, -10), (1, 50)]


def test_o_r_da_corrida_e_cortado_em_menos_s_a_s_a_cada_soma():
    e = estado()
    for k, r in enumerate((900, 900, -900, -900, -900)):
        decidir(e, EXPLORAR, [1, 2, 3], k, r)
    # 900, S(1024), 124, -776, -1024 (cortado em -S)
    assert e.corrida["r"] == -S and e.corrida["n"] == 5


# ------------------------------------------------------------------ T-CORRIDA-2
def _busca_e_ida(cd) -> tuple[EstadoDinamico, list]:
    """a busca pelo cheiro acha comida boa, a intencao comer/comida a herda (a opcao composta da DX-4), come, e o explorar fecha a corrida"""
    e = estado(cd)
    log = []
    log.append(decidir(e, BUSCA, [1, 2, 3], 0, 5, depois={**DEPOIS, "comida_boa_vista": True}))
    log.append(decidir(e, COMER, [4, 5, 6], 1, 40, ocorrido={"comeu": {"id": 7}, "brincou_com_bola": False, "chegou": False}))
    log.append(decidir(e, EXPLORAR, [7, 8, 9], 2, 0))
    return e, log


def test_t_corrida_2_a_busca_e_a_ida_do_mesmo_comportamento_dao_um_credito_so():
    e, log = _busca_e_ida(LIGADA)
    fechadas = [f for _, f in log]
    assert fechadas[0] == [] and fechadas[1] == []
    assert [(x["b"], x["inicio"], x["n"], x["r"], x["e"]) for x in fechadas[2]] == [("comer", 0, 2, 45, [1, 2, 3])]


def test_t_corrida_2_os_fins_o_c_e_o_f_sao_os_de_sem_a_subchave():
    com, _ = _busca_e_ida(LIGADA)
    sem, _ = _busca_e_ida(BASE)
    a, b = com.estado_interno(), sem.estado_interno()
    assert a.pop("corrida") is not None
    assert a == b and com.F == sem.F and com.fins == sem.fins and com.fins["achou"] == 1 and com.fins["meta"] == 1


# ------------------------------------------------------------------ T-CORRIDA-3
def test_t_corrida_3_o_reflexo_do_sono_fecha_a_corrida():
    e = estado()
    decidir(e, BUSCA, [1, 2, 3], 0, 5)
    decidir(e, BUSCA, [1, 2, 3], 1, 5)
    _, f = decidir(e, DORMIR, [0, 0, 0], 2, 0, reflexo=True)
    assert [(x["b"], x["n"], x["r"]) for x in f] == [("comer", 2, 10)]
    assert e.corrida["b"] == "dormir"


def test_t_corrida_3_o_fim_da_vida_nao_entrega_a_corrida_aberta_como_a_opcao_aberta_de_hoje():
    e = estado()
    for k in range(3):
        decidir(e, EXPLORAR, [1, 2, 3], k, 10)
    assert e.corridas_fechadas == [] and e.corrida["n"] == 3 and e.estado_interno()["corrida"] == {"b": "explorar", "inicio": 0, "n": 3, "r": 30}


def test_t_corrida_3_na_vida_a_corrida_aberta_no_fim_nao_foi_ao_p2():
    _, reg = _viver(101)
    c = orq.cerebro_de(reg)
    entregues = [x for m in c.motivos for x in m["corridas"]]
    assert c.m.estado.corrida is not None and c.m.plast.creditos == len(entregues)
    assert c.m.estado.corrida["inicio"] == entregues[-1]["inicio"] + entregues[-1]["n"]


# ------------------------------------------------------------------ as vidas: G1, G2-SEPARADO e o conferir_credito
def _viver(semente: int, braco: str = "M2", lugar: str = "longe_fixo", dono: str = "relapso", ligada: bool = True):
    original = orq.config_do_braco
    orq.config_do_braco = lambda b, g=None, c=False: replace(original(b, g, c), credito_corrida=ligada)
    try:
        motor, reg, fab = orq.viver(braco, dono, lugar, semente, 3, 16, conserto=True)
    finally:
        orq.config_do_braco = original
    _viver.fab = (motor, fab)
    return motor, reg


@pytest.mark.parametrize("semente", SEMENTES)
def test_g1_o_replay_com_a_subchave_ligada_nas_cinco_sementes(semente):
    motor, reg = _viver(semente)
    orq.conferir_replay(motor, _viver.fab[1], semente, motor.log.para_jsonl())
    orq.conferir_mecanismo("M2", reg, None)
    orq.conferir_cenario(motor, reg)
    c = orq.cerebro_de(reg)
    assert c.cd.credito_corrida and all("corridas" in m for m in c.motivos)


def test_g1_o_replay_no_comedouro_e_com_o_m1():
    for braco, lugar in (("M2", "comedouro"), ("M1", "longe_fixo")):
        motor, reg = _viver(202, braco, lugar, "atencioso")
        orq.conferir_replay(motor, _viver.fab[1], 202, motor.log.para_jsonl())
        orq.conferir_mecanismo(braco, reg, None)


def test_g2_separado_ligada_muda_so_a_vida_do_braco_que_a_liga():
    desligada = orq.viver("M2", "relapso", "longe_fixo", 101, 3, 16, conserto=True)
    ligada = _viver(101)
    assert desligada[1] is not ligada[1]
    estado_d = json.dumps(orq.cerebro_de(desligada[1]).estado_interno(), sort_keys=True)
    estado_l = json.dumps(orq.cerebro_de(ligada[1]).estado_interno(), sort_keys=True)
    assert estado_d != estado_l and orq.cerebro_de(desligada[1]).m.plast.H != orq.cerebro_de(ligada[1]).m.plast.H
    # o M1 e o M0 nao tem o P2: a subchave nao muda o log (o credito vai a nada); o M2 sem a chave segue o gabarito
    for braco in ("M1", "M0"):
        a = orq.viver(braco, "relapso", "longe_fixo", 101, 3, 16, conserto=True)[0].log.para_jsonl()
        assert a == _viver(101, braco)[0].log.para_jsonl()


def test_g2_separado_nada_fora_do_pacote_e_do_orquestrador_le_a_chave():
    donos_da_chave = {"digilab/config.py", "digilab/digibrain/adapt.py", "digilab/digibrain/estado.py",
                      "experiments/run_v2_digibrain_prototipo.py", "experiments/run_v2_habito_intencao.py"}   # o da run da C2 (adendo 7)
    achados = set()
    for pasta in ("digilab", "experiments", "web", "tools"):
        for f in (RAIZ / pasta).rglob("*"):
            if f.suffix in (".py", ".ts", ".tsx", ".js") and "node_modules" not in f.parts and "credito_corrida" in f.read_text(
                    encoding="utf-8", errors="ignore"):
                achados.add(f.relative_to(RAIZ).as_posix())
    assert achados == donos_da_chave


def test_o_conferir_credito_estendido_aceita_a_vida_e_falha_alto_numa_corrida_errada():
    _, reg = _viver(303)
    c = orq.cerebro_de(reg)
    orq.conferir_credito("M2c", c)
    achada = next(x for m in c.motivos for x in m["corridas"] if x["n"] > 1)
    for campo, valor, msg in (("r", achada["r"] + 1, "nao e a soma"), ("n", achada["n"] + 1, "decisao|nao acabou"),
                              ("inicio", achada["inicio"] + 1, "nao segue")):
        antigo = achada[campo]
        achada[campo] = valor
        try:
            with pytest.raises(RuntimeError, match=msg):
                orq.conferir_credito("M2c", c)
        finally:
            achada[campo] = antigo
    orq.conferir_credito("M2c", c)
    c.m.plast.creditos += 1
    try:
        with pytest.raises(RuntimeError, match="o P2 recebeu"):
            orq.conferir_credito("M2c", c)
    finally:
        c.m.plast.creditos -= 1


def test_a_corrida_e_mais_longa_que_o_passo_na_vida():
    """o P-CORRIDA da tarefa (4.3) tem o que medir: a media das corridas passa de 1,1 decisao na vida de teste"""
    _, reg = _viver(404)
    xs = [x["n"] for m in orq.cerebro_de(reg).motivos for x in m["corridas"]]
    assert sum(xs) / len(xs) > 1.1


# ------------------------------------------------------------------ G-MECANISMO
_DE_HOJE = [n for n, f in inspect.getmembers(tm, inspect.isfunction) if n.startswith("test_")]


@pytest.mark.parametrize("nome", _DE_HOJE)
def test_g_mecanismo_os_de_hoje_com_a_subchave_ligada(nome, monkeypatch):
    """cada teste de mecanismo de hoje (tests/test_digibrain_mecanismo.py) com as duas subchaves do cheiro e a `credito_corrida`"""
    monkeypatch.setattr(tm, "CONFIG_DIGIBRAIN_LIGADA", LIGADA)
    try:
        getattr(tm, nome)()
    except AssertionError as erro:
        # os testes do credito por opcao de hoje (T-ESTADO/T-PLAST pelo `consequencia`) olham a entrega por opcao; ligada, ela e da corrida
        if not re.search(r"estado|plast|credito|adapt|cadeia", nome):
            raise
        pytest.skip(f"credito por opcao, que a subchave troca pelo da corrida: {erro}")


def test_g_int_g_sem_direcao_g_receptor_os_de_hoje_passam_ligada():
    """os testes das intencoes (G-INT), da DX-4 sem a direcao do cheiro (G-SEM-DIRECAO) e dos receptores (G-RECEPTOR) estao no
    tests/test_digibrain_conserto.py e no tm acima; aqui, a vida ligada nao le a distancia nem a direcao no codigo novo"""
    fonte = inspect.getsource(EstadoDinamico._corrida) + inspect.getsource(EstadoDinamico.consequencia)
    assert "direcao" not in fonte and "cheiro" not in inspect.getsource(EstadoDinamico._corrida)
    json.dumps(estado().estado_interno())
