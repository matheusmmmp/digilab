"""O mundo como componente (docs/TAREFA_V2_DOIS_PETS.md, etapa 1; docs/futuro/dois_pets.md, secoes 2 e 10).

- G2: com um pet, a vida e a de antes byte a byte. As 276 vidas do gabarito da etapa 0 (tests/gabaritos/dois_pets_vidas_de_hoje.json,
  gravado com o codigo da main antes da separacao: o mundo fisico com e sem o corpo, nos dois layouts). Os outros dois gabaritos do G2
  (`mundo_vidas_de_hoje.json` e `corpo_mundo_vidas_de_hoje.json`) ficam com os testes de sempre (test_gabaritos_mundo_corpo.py,
  test_mundo.py e test_corpo_no_mundo.py), na suite.
- G-ENGINE: engine.py com o sha256 de sempre.
- O componente: o MotorMundo ligado e dono do proprio Mundo (a semente do pet), o que e do mundo mora nele e o que e do pet fica no motor;
  o Mundo nao sabe de pet.
- A atualizacao idempotente por tick: a segunda chamada no mesmo tick nao muda nada (nem as rngs), o tick para tras falha alto, e o
  resultado so le o tick e o fluxo `mundo-arvores`.
- G1 com o estado do Mundo: o replay refaz o mundo bit a bit.
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import gabarito_dois_pets as gdp  # noqa: E402
from digilab.config import CONFIG_MUNDO, CONFIG_MUNDO_LIGADA, CONFIG_PADRAO, ConfigMundo  # noqa: E402
from digilab.mundo import Mundo, MundoSemChave, reproduzir_mundo  # noqa: E402
from digilab.protocol import ENGINE_SHA256_V0, derivar_semente, sha256_engine  # noqa: E402

CM = CONFIG_MUNDO_LIGADA
DO_MUNDO = ("comidas", "arvores", "bola_mundo", "comedouro", "quedas", "sumidas", "rolagens", "bolas_deixadas")
DO_PET = ("pet", "_pendente", "_percepcao", "_fome_antes", "_rng_sujeira", "_rng_alvo", "consumos_mundo", "deixadas",
          "decisoes_mundo", "regioes", "visitas", "_manchas_abertas")


def _resumo(m: Mundo) -> str:
    return json.dumps(m.resumo(), sort_keys=True, default=repr)


# ================================================================== G2 e G-ENGINE
def test_g2_vidas_do_mundo_fisico_de_hoje_com_um_pet():
    """as 276 vidas do gabarito da etapa 0, byte a byte: o log, o estado, o estado() (com o corpo), as acoes, as rngs, a politica, o
    resumo do mundo fisico inteiro e o registro da novidade"""
    gravado = json.loads(gdp.ARQUIVO.read_text(encoding="utf-8"))
    assert len(gravado) == 276
    vistos, difs = 0, []
    for chave, caso in gdp.casos():
        vistos += 1
        if gdp.vida_de_hoje(chave, caso) != gravado[chave]:
            difs.append(chave)
    assert vistos == len(gravado) and difs == []


def test_g2_o_gabarito_cobre_o_que_a_etapa_pede():
    """com e sem o corpo (o corpo inteiro da etapa 6 incluido), nos dois layouts, pela bancada e direto"""
    chaves = list(json.loads(gdp.ARQUIVO.read_text(encoding="utf-8")))
    assert {c.split("|")[2] for c in chaves if c.startswith("bancada|")} == {"fisico", "fisico_afastado"}
    assert {c.split("|")[1] for c in chaves if c.startswith("direta|")} == {"padrao", "afastado"}
    assert {c.split("|")[2] for c in chaves if c.startswith("direta|")} == {"sem", "quimica", "drives"}
    assert any("-quimica~" in c for c in chaves) and any("-hoje~" in c for c in chaves)


def test_g_engine():
    assert sha256_engine() == ENGINE_SHA256_V0


# ================================================================== o componente
def _vida(corpo: str = "drives", layout: str = "padrao", semente: int = 101):
    return gdp.vida_direta(layout, corpo, "lobos", "perto", semente)


def test_o_motor_e_dono_do_proprio_mundo():
    v = _vida()
    m = v.motor
    assert isinstance(m.mundo, Mundo) and m.mundo.semente == m.semente and m.mundo.cmf is m.cmf
    # o que e do mundo mora no Mundo: os atributos de antes leem os mesmos objetos
    assert m.comidas is m.mundo.comidas and m.arvores is m.mundo.arvores and m.bola_mundo is m.mundo.bola
    assert m.quedas is m.mundo.quedas and m.sumidas is m.mundo.sumidas and m.rolagens is m.mundo.rolagens
    assert m.bolas_deixadas is m.mundo.bolas_deixadas and m.comedouro == m.mundo.comedouro
    assert m._rng_arvores is m.mundo.rng_arvores and m._rng_bola is m.mundo.rng_bola
    assert (m._prox_id, m._passo_mundo) == (m.mundo.prox_id, m.mundo.passo_mundo)
    # os fluxos do mundo sao os de sempre, pela semente do pet
    novo = Mundo(m.cmf, m.semente)
    for nome, r in (("mundo-arvores", novo.rng_arvores), ("mundo-bola", novo.rng_bola)):
        assert r.getstate() == random.Random(derivar_semente(nome, m.semente)).getstate()
    # a vida exercitou as duas metades
    assert m.quedas and m.rolagens and m.consumos_mundo and m.deixadas and m.bolas_deixadas and m.decisoes_mundo


def test_o_mundo_nao_sabe_de_pet():
    """nenhum atributo do Mundo e do pet; os atributos do pet ficam no motor (o que a etapa 2 vai duplicar por pet)"""
    m = _vida().motor
    assert not set(vars(m.mundo)) & {"pet", "_pendente", "pendente", "_percepcao", "percepcao", "rng_alvo", "rng_sujeira",
                                     "consumos", "consumos_mundo", "deixadas", "decisoes", "decisoes_mundo", "regioes", "visitas"}
    for nome in DO_PET:
        assert nome in vars(m), nome
    for nome in DO_MUNDO:
        assert nome not in vars(m), nome


def test_o_mundo_so_existe_ligado_e_o_motor_desligado_nao_o_tem():
    with pytest.raises(MundoSemChave):
        Mundo(CONFIG_MUNDO, 101)
    fp, fm = gdp.fabricas_diretas("padrao", "sem", "instinto")
    desligado = gdp.MotorMundo(fp(CONFIG_PADRAO), CONFIG_PADRAO, 101, obediencia_desligada=True, cfg_mundo=CONFIG_MUNDO)
    assert not hasattr(desligado, "mundo") and not hasattr(desligado, "comidas")


def test_os_gestos_validam_no_mundo():
    m = Mundo(CM, 101)
    with pytest.raises(ValueError, match="deixar_comida invalido"):
        m.deixar_comida("pedra", 10, 10, 0)
    with pytest.raises(ValueError, match="deixar_comida invalido"):
        m.deixar_comida("racao", 5000, 10, 0)
    with pytest.raises(ValueError, match="fora do mapa"):
        m.deixar_bola(-1, 10, 0)
    c = m.deixar_comida("racao", 10, 10, 0)
    assert c["origem"] == "dono" and m.comidas[c["id"]] is c
    m.deixar_bola(20, 30, 5)
    assert m.bola_em(5) == (20, 30) and m.bolas_deixadas == [{"tick": 5, "x": 20, "y": 30}]
    assert m.retirar_comida(c["id"]) is c and not m.comidas
    with pytest.raises(KeyError):
        m.retirar_comida(c["id"])


# ================================================================== a atualizacao idempotente por tick
def _ticks(dias: int = 3, passo: int = 15) -> list[int]:
    return list(range(0, dias * 1440, passo))


def test_atualizar_duas_vezes_no_mesmo_tick_nao_muda_nada():
    """quem decide primeiro dispara; o segundo no mesmo tick nao sorteia nem remove nada"""
    a, b = Mundo(CM, 202), Mundo(CM, 202)
    for t in _ticks():
        a.atualizar(t)
        b.atualizar(t)
        antes = _resumo(b)
        b.atualizar(t)
        assert _resumo(b) == antes
    assert _resumo(a) == _resumo(b)
    assert a.quedas and a.sumidas and a.tick_atualizado == _ticks()[-1]


def test_o_mundo_nao_volta_no_tempo():
    m = Mundo(CM, 101)
    m.atualizar(300)
    with pytest.raises(ValueError, match="nao volta no tempo"):
        m.atualizar(299)


def test_o_resultado_so_le_o_tick_e_o_fluxo_das_arvores():
    """atualizar so em alguns ticks ou em todos da as mesmas quedas e o mesmo chao no fim (as sumidas, na ordem em que sairam)"""
    todos, alguns = Mundo(CM, 303), Mundo(CM, 303)
    for t in _ticks():
        todos.atualizar(t)
        if t % 600 == 0:
            alguns.atualizar(t)
    fim = _ticks()[-1]
    alguns.atualizar(fim)
    assert todos.quedas == alguns.quedas and todos.quedas
    assert todos.comidas == alguns.comidas and todos.rng_arvores.getstate() == alguns.rng_arvores.getstate()
    assert sorted(s["id"] for s in todos.sumidas) == sorted(s["id"] for s in alguns.sumidas)


def test_as_quedas_nao_dependem_de_quem_come():
    """o pet que come muda o chao, nao as quedas sorteadas (G-NUMS): a vida com o corpo e sem o corpo, e o mundo sem pet"""
    sem_pet = Mundo(CM, 101)
    v = _vida("sem", semente=101)
    for t in range(0, v.motor._estado.tick + 1, 15):
        sem_pet.atualizar(t)
    sorteios = lambda qs: [(q["tick"], q["arvore"], q["sorteadas"], q["pontos"]) for q in qs]  # noqa: E731
    pos = sorteios(sem_pet.quedas)
    assert sorteios(v.motor.quedas) == pos[:len(v.motor.quedas)] and v.motor.quedas


# ================================================================== G1 com o Mundo
@pytest.mark.parametrize("corpo", ["sem", "quimica", "drives"])
@pytest.mark.parametrize("layout", ["padrao", "afastado"])
def test_g1_o_replay_refaz_o_mundo(corpo, layout):
    v = _vida(corpo, layout, 202)
    fp, fm = gdp.fabricas_diretas(layout, corpo, "lobos")
    r = reproduzir_mundo(v.motor.log, fp, CONFIG_PADRAO, 202, fm)
    assert _resumo(r.mundo) == _resumo(v.motor.mundo)
    assert json.dumps(r.resumo_mundo_fisico(), sort_keys=True, default=repr) == json.dumps(v.motor.resumo_mundo_fisico(),
                                                                                          sort_keys=True, default=repr)
    assert r.log.para_jsonl() == v.motor.log.para_jsonl() and repr(r._estado) == repr(v.motor._estado)
    assert r.mundo.tick_atualizado == v.motor.mundo.tick_atualizado is not None


def test_config_do_mundo_e_a_do_motor():
    cm = ConfigMundo(ligada=True, mult_queda=2.0)
    m = Mundo(cm, 7)
    assert m.cmf is cm and all(a["p"] in (cm.p_queda_jardim * 2.0, cm.p_queda_mata * 2.0) for a in m.arvores)
