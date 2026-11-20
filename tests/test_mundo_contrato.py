"""P4, etapa 1 (docs/TAREFA_V2_P4_CEREBRO_MUNDO.md, secoes 3.1 e 4): o contrato sensorio-motor no mundo do motor em Python
(digilab/contrato.py e as chaves da ConfigContrato no digilab/mundo.py).

- As respostas conhecidas, feitas a mao: o cone, a oclusao (o tronco nao tapa a si mesmo), o A* (o empate, o canto, sem caminho), o
  bloqueio e o deslize, o contato, o controlador (chegou, bloqueado, a orientacao) e o empurrao da bola.
- O A* com o heap contra a versao de referencia (o minimo sobre o conjunto aberto, como no POC) em grades sorteadas.
- O DIR16 do contrato e o do mundo.
- O adaptador da percepcao: os vistos e os troncos com o contrato sao os de hoje que passam pelo cone e pela oclusao; o cerebro nao ganha
  entrada (os campos de hoje, mais a orientacao).
- G2: com a chave explicita desligada, as vidas do gabarito do mundo do J5 saem iguais (o gabarito da etapa 0 e o tests/test_p4_gabaritos.py).
- G1: o replay das vidas com as chaves (o instinto e o cerebro A; e a vida de 12 dias do J5 com o planejador, pela bancada).
- G-INT: nenhum float no digilab/contrato.py, pela AST.
- As recusas (a config, sem o mundo, no grupo).
Sementes: so as dos testes.
"""
from __future__ import annotations

import ast
import json
import random
import sys
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))
sys.path.insert(0, str(RAIZ / "tools"))

import gabarito_dois_pets as gdp  # noqa: E402
import gabarito_pqp_mundo as gq  # noqa: E402

from digilab import contrato as ct  # noqa: E402
from digilab import mundo as mm  # noqa: E402
from digilab.config import (CONFIG_CONTRATO, CONFIG_CONTRATO_LIGADO, CONFIG_PADRAO,  # noqa: E402
                            CONFIG_PQP_MUNDO_LIGADA, ConfigContrato)
from digilab.instinto_mundo import PoliticaInstintoMundo  # noqa: E402
from digilab.mundo import MotorMundo, PercepcaoContrato, PercepcaoMundo, reproduzir_mundo  # noqa: E402

CM = gq.LAYOUTS["padrao"]
PAREDE = ct.Solido(20, 0, 30, 40, "parede", True, True)


# ================================================================== a config
def test_a_config_desligada_e_as_falhas():
    c = CONFIG_CONTRATO
    assert not c.ligada and not c.sensores and not c.controlador and not c.paredes
    assert CONFIG_CONTRATO_LIGADO.sensores and CONFIG_CONTRATO_LIGADO.controlador and not CONFIG_CONTRATO_LIGADO.paredes
    assert (c.cos_meio_cone, c.raio_bigode, c.r_pet, c.ticks_bloqueado) == (512, 32, 6, 3)      # os do POC
    for kw in (dict(sensores=1), dict(controlador="sim"), dict(paredes=None)):
        with pytest.raises(TypeError):
            ConfigContrato(**kw)
    for kw in (dict(cos_meio_cone=0), dict(cos_meio_cone=1025), dict(r_pet=0), dict(ticks_bloqueado=0), dict(lado_tronco=0),
               dict(raio_bigode=-1), dict(cos_meio_cone=512.0)):
        with pytest.raises((TypeError, ValueError)):
            ConfigContrato(**kw)


def test_o_dir16_e_o_do_mundo():
    assert ct.DIR16 == mm.DIR16
    assert ct.setor_de(10, 0) == 0 and ct.setor_de(0, -10) == 4 and ct.setor_de(-10, 0) == 8 and ct.setor_de(0, 10) == 12
    assert ct.setor_de(10, -10) == 2 and ct.setor_de(0, 0) == 0
    assert ct.relativo(2, 14) == 4 and ct.relativo(14, 2) == 12


# ================================================================== o cone e a oclusao
def test_o_cone():
    # orientacao 0 (leste), o meio cone de 60 graus (512/1024)
    assert ct.no_cone(10, 0, 0, 512) and ct.no_cone(0, 0, 0, 512)
    assert ct.no_cone(10, 17, 0, 512)            # d = 19: 10240 >= 9728
    assert not ct.no_cone(10, 20, 0, 512)        # d = 22: 10240 < 11264
    assert not ct.no_cone(-10, 0, 0, 512) and not ct.no_cone(0, 10, 0, 512)
    # orientacao 4 (norte, y para cima)
    assert ct.no_cone(0, -10, 4, 512) and not ct.no_cone(0, 10, 4, 512)
    # o raio
    assert ct.visivel(0, 0, 30, 0, 0, 30, 512, ()) and not ct.visivel(0, 0, 31, 0, 0, 30, 512, ())


def test_a_oclusao():
    tronco = ct.Solido(9, -1, 11, 2, "tronco", False, True)
    assert ct.tapado(0, 0, 20, 0, (tronco,))
    assert not ct.tapado(0, 0, 20, 0, (ct.Solido(9, -1, 11, 2, "obstaculo", True, False),))   # baixo nao tapa
    assert not ct.tapado(0, 0, 20, 0, (ct.Solido(9, 5, 11, 8, "tronco", False, True),))       # fora da linha
    assert not ct.tapado(0, 0, 8, 0, (tronco,))                                             # antes do tronco
    # o ponto final nao conta, mas o tronco em volta do alvo tapa o caminho ate ele: por isso o mundo tira o proprio tronco
    em_volta = ct.Solido(16, -4, 24, 4, "tronco", False, True)
    assert ct.tapado(0, 0, 20, 0, (em_volta,)) and not ct.tapado(0, 0, 20, 0, ())
    assert not ct.visivel(0, 0, 20, 0, 0, 60, 512, (tronco,)) and ct.visivel(0, 0, 20, 0, 0, 60, 512, ())


# ================================================================== o A*
def _caminho_referencia(g, cx_n, cy_n, de, para):
    """o A* do POC (controlador.ts) como estava: o aberto e um conjunto e a escolha e o min de (f, h, indice)"""
    ini, fim = de[1] * cx_n + de[0], para[1] * cx_n + para[0]
    if not g[fim]:
        return None
    custo, veio, aberto, fechado = {ini: 0}, {}, {ini}, set()

    def h(i):
        return ct.octil(i % cx_n, i // cx_n, para[0], para[1])
    while aberto:
        atual = min(aberto, key=lambda i: (custo[i] + h(i), h(i), i))
        if atual == fim:
            cam, i = [], fim
            while True:
                cam.append((i % cx_n, i // cx_n))
                if i not in veio:
                    break
                i = veio[i]
            return cam[::-1]
        aberto.discard(atual)
        fechado.add(atual)
        ax, ay = atual % cx_n, atual // cx_n
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if (dx, dy) == (0, 0):
                    continue
                nx, ny = ax + dx, ay + dy
                if not (0 <= nx < cx_n and 0 <= ny < cy_n):
                    continue
                n = ny * cx_n + nx
                if not g[n] or n in fechado:
                    continue
                if dx and dy and (not g[ay * cx_n + nx] or not g[ny * cx_n + ax]):
                    continue
                c = custo[atual] + (14 if dx and dy else 10)
                if n not in custo or c < custo[n]:
                    custo[n], veio[n] = c, atual
                    aberto.add(n)
    return None


def test_o_a_estrela_respostas_conhecidas():
    livre = (True,) * 25
    assert ct.caminho(livre, 5, 5, (0, 0), (4, 4)) == [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)]
    assert ct.caminho(livre, 5, 5, (0, 0), (2, 0)) == [(0, 0), (1, 0), (2, 0)]
    assert ct.caminho(livre, 5, 5, (2, 2), (2, 2)) == [(2, 2)]
    # sem cortar o canto: (1, 0) ocupada, a diagonal (0, 0) -> (1, 1) nao vale
    g = list(livre)
    g[0 * 5 + 1] = False
    assert ct.caminho(tuple(g), 5, 5, (0, 0), (1, 1)) == [(0, 0), (0, 1), (1, 1)]
    # o destino ocupado e o muro inteiro: sem caminho
    assert ct.caminho(tuple(g), 5, 5, (0, 0), (1, 0)) is None
    muro = tuple(not (x == 2) for _y in range(5) for x in range(5))
    assert ct.caminho(muro, 5, 5, (0, 0), (4, 4)) is None
    # a celula livre mais perto, no empate a de menor indice
    so_um = tuple(i in (3, 21) for i in range(25))
    assert ct.livre_mais_perto(so_um, 5, (2, 2)) == (3, 0)


def test_o_a_estrela_com_heap_e_o_de_referencia():
    rng = random.Random(101)
    for _ in range(300):
        cx_n, cy_n = rng.randint(2, 12), rng.randint(2, 12)
        g = tuple(rng.random() < 0.72 for _ in range(cx_n * cy_n))
        de = (rng.randrange(cx_n), rng.randrange(cy_n))
        para = (rng.randrange(cx_n), rng.randrange(cy_n))
        assert ct.caminho(g, cx_n, cy_n, de, para) == _caminho_referencia(g, cx_n, cy_n, de, para), (cx_n, cy_n, de, para)


def test_a_grade():
    # um muro de 16 x 16 na celula (1, 0): o centro dela (24, 8) fica dentro; os vizinhos, a 8 do muro, ficam livres com r = 6
    g = ct.grade(3, 2, 16, 6, (ct.Solido(16, 0, 32, 16, "obstaculo", True, True),))
    assert g == (True, False, True, True, True, True)
    assert ct.grade(3, 2, 16, 6, (ct.Solido(16, 0, 32, 16, "tronco", False, True),)) == (True,) * 6     # o tronco nao colide


# ================================================================== o bloqueio, o deslize e o contato
def test_o_bloqueio_e_o_deslize():
    # o circulo (r 6) encosta no muro em x = 14 ((20 - 14)^2 = 36, nao e < 36) e bate em x = 15
    assert ct.bloqueio_em(14, 10, 6, (PAREDE,)) is None and ct.bloqueio_em(15, 10, 6, (PAREDE,)) == ("solido", 0)
    assert ct.mover(10, 10, 6, 4, 0, (PAREDE,)) == (14, 10, None, None)
    assert ct.mover(14, 10, 6, 4, 0, (PAREDE,)) == (14, 10, ("solido", 0), None)
    assert ct.mover(14, 10, 6, 4, 3, (PAREDE,)) == (14, 13, ("solido", 0), None)        # desliza no y
    assert ct.mover(10, 10, 6, 4, 0, (ct.Solido(20, 0, 30, 40, "tronco", False, True),)) == (14, 10, None, None)
    assert ct.mover(0, 0, 6, 0, 0, ()) == (0, 0, None, None)
    # os circulos (outro corpo)
    assert ct.bloqueio_em(0, 0, 6, (), ((12, 0, 6),)) is None and ct.bloqueio_em(1, 0, 6, (), ((12, 0, 6),)) == ("circulo", 0)


def test_os_bigodes():
    # orientacao 0: o bigode 0 (leste) para em 3 (x = 14 + 1 ja bate em 15... o circulo em 11 + t: bate em t = 4), os outros livres
    b = ct.bigodes(11, 20, 6, 0, (PAREDE,), 32)
    assert b[0] == 3 and b[4] == 32 and len(b) == 8
    assert ct.bigodes(11, 20, 6, 0, (), 32) == [32] * 8


def test_o_controlador_chega_no_aberto():
    a = ct.controlar(100, 100, 160, 100, 8, 15, 4, 6, (), 64, 30, 16, 3, 7)
    assert a.parou_por == "chegou" and ct.distancia(160 - a.x, 100 - a.y) <= 8
    assert a.andado <= 15 * 4 and all(ct.distancia(q[0] - p[0], q[1] - p[1]) <= 4 for p, q in zip(((100, 100),) + a.trajetoria,
                                                                                                    a.trajetoria))
    assert a.contatos == () and a.orientacao == ct.setor_de(a.trajetoria[-1][0] - a.trajetoria[-2][0],
                                                            a.trajetoria[-1][1] - a.trajetoria[-2][1])
    # longe: acabam os ticks, 15 x 4 andados em linha reta
    a = ct.controlar(40, 40, 900, 40, 8, 15, 4, 6, (), 64, 30, 16, 3, 7)
    assert a.parou_por == "hora" and (a.x, a.y) == (100, 40) and a.andado == 60 and a.orientacao == 0
    # ja no alvo: nem anda, e a orientacao fica
    a = ct.controlar(40, 40, 42, 40, 8, 15, 4, 6, (), 64, 30, 16, 3, 9)
    assert a.parou_por == "chegou" and a.trajetoria == () and a.andado == 0 and a.orientacao == 9


def test_o_controlador_bloqueado_com_contato():
    # um muro fino em y 110..112: os centros das celulas (y 104 e 120) ficam livres, mas o corpo nao passa. De (40, 88) para o sul: 4
    # ticks ate y = 104, 3 parado contra o muro, e para bloqueado; o contato e com o obstaculo ao sul (setor 12)
    muro = ct.Solido(0, 110, 1024, 112, "obstaculo", True, True)
    a = ct.controlar(40, 88, 40, 200, 8, 15, 4, 6, (muro,), 64, 30, 16, 3, 0)
    assert a.parou_por == "bloqueado" and (a.x, a.y) == (40, 104) and a.andado == 16
    assert a.trajetoria == ((40, 92), (40, 96), (40, 100), (40, 104), (40, 104), (40, 104), (40, 104))
    assert a.contatos == (("obstaculo", 12),) and a.orientacao == 12


def test_o_controlador_contorna_o_muro():
    muro = ct.Solido(0, 100, 600, 116, "obstaculo", True, True)
    x, y = 560, 60
    for _ in range(8):
        a = ct.controlar(x, y, 560, 200, 8, 15, 4, 6, (muro,), 64, 30, 16, 3, 0)
        assert all(ct.bloqueio_em(px, py, 6, (muro,)) is None for px, py in a.trajetoria)
        x, y = a.x, a.y
        if a.parou_por == "chegou":
            break
    assert a.parou_por == "chegou" and ct.distancia(560 - x, 200 - y) <= 8


# ================================================================== o empurrao (portado; o J5 nao usa)
def test_o_empurrao_da_bola():
    assert ct.empurrar(0, 0, 10, 0) == (10, 0) and ct.empurrar(0, 0, 3, 4) == (6, 8)
    with pytest.raises(ValueError):
        ct.empurrar(5, 5, 5, 5)
    assert ct.passo_bola(100, 100, 4, 10, 0, ()) == (110, 100, 9, 0)             # o atrito tira 1 do modulo
    # o muro em x = 112: a bola (r 4) para em 108, reflete 3/4 truncado (-7) e perde 1 (-6)
    muro = ct.Solido(112, 0, 200, 200, "parede", True, True)
    assert ct.passo_bola(100, 100, 4, 10, 0, (muro,)) == (108, 100, -6, 0)
    assert ct.passo_bola(0, 0, 4, 1, 0, ()) == (1, 0, 0, 0)                       # devagar: para


# ================================================================== G-INT
def test_g_int_nenhum_float_no_contrato():
    arvore = ast.parse((RAIZ / "digilab" / "contrato.py").read_text(encoding="utf-8"))
    ruins = []
    for no in ast.walk(arvore):
        if isinstance(no, ast.Constant) and isinstance(no.value, float):
            ruins.append(("float", no.lineno))
        elif isinstance(no, (ast.BinOp, ast.AugAssign)) and isinstance(no.op, ast.Div):
            ruins.append(("divisao /", no.lineno))
        elif isinstance(no, ast.Call) and isinstance(no.func, ast.Name) and no.func.id in ("float", "round"):
            ruins.append((no.func.id, no.lineno))
        elif isinstance(no, ast.Attribute) and isinstance(no.value, ast.Name) and no.value.id == "math" and no.attr != "isqrt":
            ruins.append((f"math.{no.attr}", no.lineno))
        elif isinstance(no, ast.Name) and no.id == "random":
            ruins.append(("random", no.lineno))
    assert ruins == []


# ================================================================== o adaptador da percepcao
def _motor(contrato=CONFIG_CONTRATO_LIGADO, s=101):
    return MotorMundo(PoliticaInstintoMundo(CONFIG_PADRAO), CONFIG_PADRAO, s, obediencia_desligada=True, cfg_mundo=CM,
                      cfg_pqp=CONFIG_PQP_MUNDO_LIGADA, cfg_contrato=contrato)


def test_o_tronco_nao_tapa_a_si_mesmo_e_o_cone_vale_para_ele():
    m = _motor()
    a = m.mundo.arvores[0]
    meio = CONFIG_CONTRATO.lado_tronco // 2
    q = m._quadrados_troncos[a["id"]]
    assert (q.x0, q.y0, q.x1, q.y1) == (a["x"] - meio, a["y"] - meio, a["x"] + meio, a["y"] + meio) and q.alto and not q.colide
    px, py = a["x"] - 30, a["y"]
    for orientacao, ve in ((0, True), (8, False), (4, False)):
        p = m.mundo.perceber(px, py, 0, troncos=True, contrato=(orientacao, 512, m._opacos, m._quadrados_troncos))
        assert isinstance(p, PercepcaoContrato) and p.orientacao == orientacao
        assert (a["id"] in [t[0] for t in p.troncos]) == ve, orientacao
    # um tronco atras de outro, na mesma linha: o de tras some
    atras = ct.Solido(a["x"] - 15 - meio, a["y"] - meio, a["x"] - 15 + meio, a["y"] + meio, "tronco", False, True)
    p = m.mundo.perceber(px, py, 0, troncos=True, contrato=(0, 512, m._opacos + (atras,), m._quadrados_troncos))
    assert a["id"] not in [t[0] for t in p.troncos]


def test_o_adaptador_so_filtra_e_nao_cria_entrada():
    v = gq.vida("padrao", "sem", "instinto", "comedouro", 101, cfg_pqp=CONFIG_PQP_MUNDO_LIGADA, cfg_contrato=CONFIG_CONTRATO_LIGADO)
    m = v.motor
    t = m._tm(m._estado.tick)
    campos = {f for f in PercepcaoMundo.__dataclass_fields__}
    assert set(PercepcaoContrato.__dataclass_fields__) == campos | {"orientacao"}
    rng = random.Random(202)
    largura, altura = CM.celulas_x * CM.sub, CM.celulas_y * CM.sub
    for _ in range(60):
        x, y, o = rng.randrange(largura), rng.randrange(altura), rng.randrange(16)
        hoje = m.mundo.perceber(x, y, t, troncos=True)
        com = m.mundo.perceber(x, y, t, troncos=True, contrato=(o, 512, m._opacos, m._quadrados_troncos))
        for f in campos - {"vistos", "troncos"}:
            assert getattr(com, f) == getattr(hoje, f), f
        assert set(com.troncos) <= set(hoje.troncos)
        for tr in hoje.troncos:
            opacos = tuple(q for q in m._opacos if q is not m._quadrados_troncos[tr[0]])
            assert (tr in com.troncos) == ct.visivel(x, y, x + tr[1], y + tr[2], o, m.mundo.raio_visao, 512, opacos)
        if len(hoje.vistos) < CM.max_vistos:
            assert set(com.vistos) <= set(hoje.vistos)
            for vi in hoje.vistos:
                assert (vi in com.vistos) == ct.visivel(x, y, x + vi[2], y + vi[3], o, m.mundo.raio_visao, 512, m._opacos)


def test_so_o_controlador_nao_muda_a_percepcao():
    m = _motor(ConfigContrato(controlador=True))
    assert m._contrato_da_percepcao() is None
    assert type(m._perceber(0)) is PercepcaoMundo


def test_o_registro_do_contrato():
    v = gq.vida("padrao", "sem", "instinto", "comedouro", 202, cfg_pqp=CONFIG_PQP_MUNDO_LIGADA, cfg_contrato=CONFIG_CONTRATO_LIGADO)
    r = v.motor.resumo_mundo_fisico()
    regs = r["contrato_decisoes"]
    assert regs and r["orientacao"] == regs[-1]["orientacao"]
    com_alvo = [d for d in r["decisoes"] if d["alvo"] is not None]
    assert len(com_alvo) == len(regs)
    for d, reg in zip(com_alvo, regs):
        assert reg["parou_por"] in ("chegou", "bloqueado", "hora") and (reg["parou_por"] == "chegou") == d["chegou"]
        assert reg["contato"] == [] and reg["obstaculos"] == [CONFIG_CONTRATO.raio_bigode] * 8      # sem paredes, nada colide
        assert reg["resultado"] == {"parou_por": reg["parou_por"], "comeu": d["comeu"] is not None, "empurrou": False,
                                    "bola_afastou": None}
        assert d["deslocamento"] == sum(ct.distancia(q[0] - p[0], q[1] - p[1])
                                        for p, q in zip([list(d["antes"])] + reg["trajetoria"], reg["trajetoria"]))
        assert len(reg["trajetoria"]) <= CONFIG_PADRAO.intervalo_decisao_ticks
    assert "orientacao" not in gq.vida("padrao", "sem", "instinto", "comedouro", 202).motor.resumo_mundo_fisico()


def test_o_modelo_do_mundo_ve_as_arvores_pelo_cone():
    """o mapa do planejador (ModeloMundo): com a percepcao do contrato, as arvores vistas sao os troncos dela; o comedouro, pelo raio"""
    from digilab.config import CONFIG_MODELO_MUNDO_LIGADA
    from digilab.modelo_mundo import COMEDOURO, ModeloMundo
    m = _motor()
    a = m.mundo.arvores[0]
    px, py = a["x"] - 30, a["y"]
    mod = ModeloMundo(CONFIG_MODELO_MUNDO_LIGADA, CM)
    nomes = {n for n, _x, _y in mod.lugares}
    assert a["id"] in nomes
    de_costas = m.mundo.perceber(px, py, 0, troncos=True, contrato=(8, 512, m._opacos, m._quadrados_troncos))
    mod._ver_lugares(de_costas, 1)
    assert a["id"] not in mod.lugares_vistos            # no raio, mas fora do cone: a conta do disco o veria
    de_frente = m.mundo.perceber(px, py, 0, troncos=True, contrato=(0, 512, m._opacos, m._quadrados_troncos))
    mod._ver_lugares(de_frente, 2)
    assert mod.lugares_vistos[a["id"]] == 2
    assert set(mod.lugares_vistos) - {COMEDOURO} == {t[0] for t in de_frente.troncos}
    cx, cy = m.mundo.comedouro
    mod2 = ModeloMundo(CONFIG_MODELO_MUNDO_LIGADA, CM)
    mod2._ver_lugares(m.mundo.perceber(cx, cy, 0, troncos=True, contrato=(8, 512, m._opacos, m._quadrados_troncos)), 3)
    assert mod2.lugares_vistos.get(COMEDOURO) == 3       # o comedouro fica com a conta do raio, de costas ou de frente
    with pytest.raises(RuntimeError, match="fora do layout"):
        mod._ver_lugares(replace(de_frente, troncos=((a["id"], 31, 0, 31),)), 4)


# ================================================================== G2: a chave explicita desligada
def test_g2_a_chave_explicita_desligada():
    gravado = json.loads(gq.ARQUIVO.read_text(encoding="utf-8"))
    casos = dict(gq.casos())
    assert set(casos) == set(gravado)
    for chave, caso in casos.items():
        assert gq.impressao_de(caso, cfg_contrato=CONFIG_CONTRATO) == gravado[chave], chave


# ================================================================== G1
@pytest.mark.parametrize("cerebro,corpo,pqp,contrato", [
    ("instinto", "sem", True, CONFIG_CONTRATO_LIGADO),
    ("instinto", "quimica", True, CONFIG_CONTRATO_LIGADO),
    ("P1-alvo", "quimica", False, CONFIG_CONTRATO_LIGADO),
    ("instinto", "sem", True, ConfigContrato(sensores=True, controlador=True, paredes=True)),
    ("instinto", "sem", True, ConfigContrato(sensores=True)),
    ("instinto", "sem", True, ConfigContrato(controlador=True)),
])
def test_g1_o_replay_com_as_chaves(cerebro, corpo, pqp, contrato):
    kw = {"cfg_contrato": contrato, **({"cfg_pqp": CONFIG_PQP_MUNDO_LIGADA} if pqp else {})}
    for s in (101, 202):
        v = gq.vida("padrao", corpo, cerebro, "comedouro", s, **kw)
        fp, fm = gq.fabricas("padrao", corpo, cerebro, gq.x_do_caso("comedouro", s), **kw)
        r = reproduzir_mundo(v.motor.log, fp, CONFIG_PADRAO, s, fm)
        assert gdp.impressao(r, v.interacoes) == gdp.impressao(v.motor, v.interacoes)
        assert r.resumo_mundo_fisico() == v.motor.resumo_mundo_fisico() and r.orientacao == v.motor.orientacao


def test_g1_a_vida_do_j5_com_o_planejador():
    import bancada_v2 as bv
    import custo_p4_contrato as cpc
    bp = cpc.bancada(True)
    v = bp.vida(bv.EspecPQP("P1-plan", "T1", 101))
    assert v.motor.cct == CONFIG_CONTRATO_LIGADO and v.motor.contrato_decisoes
    bp.conferir_replay(v)


# ================================================================== as recusas
def test_as_recusas():
    with pytest.raises(TypeError):
        _motor(contrato={"sensores": True})
    with pytest.raises(ValueError):
        MotorMundo(PoliticaInstintoMundo(CONFIG_PADRAO), CONFIG_PADRAO, 101, obediencia_desligada=True, cfg_contrato=CONFIG_CONTRATO_LIGADO)
    # desligada, o motor sem o mundo aceita a chave (nada muda)
    MotorMundo(PoliticaInstintoMundo(CONFIG_PADRAO), CONFIG_PADRAO, 101, obediencia_desligada=True, cfg_contrato=CONFIG_CONTRATO)
    with pytest.raises(ValueError, match="fora do grupo"):
        MotorMundo(PoliticaInstintoMundo(CONFIG_PADRAO), CONFIG_PADRAO, 101, obediencia_desligada=True, cfg_mundo=CM,
                   mundo=mm.Mundo(CM, 101), cfg_contrato=CONFIG_CONTRATO_LIGADO)
