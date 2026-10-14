"""O cheiro pelo orgao: os candidatos `cheiro_seguir` e `cheiro_virar` e o G-SEM-DIRECAO (docs/futuro/dois_pets.md, secao 5.6; DP-13 e
DP-14; docs/TAREFA_V2_DOIS_PETS.md, etapa 8b, o lado do A).

- G2: sem o orgao do Olfato da comida, a vida de hoje (os gabaritos de sempre, na suite); os grupos com o Olfato social e a Audicao (sem
  o da comida) iguais ao gabarito gravado antes (tests/gabaritos/orgao_sem_direcao_vidas_de_hoje.json).
- A mecanica exata de `alvos_do_olfato` (duas narinas e uma), da leitura e do limiar do explorar.
- G-SEM-DIRECAO: por AST, as funcoes do orgao nao leem o mundo; por espiao, em vidas com o orgao, a percepcao nunca tem cheiro nem direcao,
  o candidato `cheiro` nunca aparece, os candidatos do orgao sao refeitos so do que o pet sente, o alvo padrao e o da regra da opcao, e a
  direcao do cheiro nem e calculada (a funcao trocada por uma que falha). No grupo, com o Olfato social e a Audicao, a percepcao dos
  sentidos fica sem o cheiro e sem os sons do mundo.
- O instinto do mundo na fome urgente le so as narinas; o cerebro A le os dois candidatos como a classe `cheiro`.
- G1: o replay refaz as vidas e os grupos com o orgao.
Sementes: so as dos testes.
"""
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
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "tests"))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import gabarito_dois_pets as gdp  # noqa: E402
import gabarito_orgao_sem_direcao as gosd  # noqa: E402

import digilab.instinto_mundo as im  # noqa: E402
import digilab.mundo as mundo  # noqa: E402
from digilab.config import (CONFIG_CONSEQUENCIA, CONFIG_CORPO_DRIVES, CONFIG_GRUPO_LIGADA, CONFIG_LOBOS, CONFIG_OLFATO,  # noqa: E402
                            CONFIG_OUVIDO, CONFIG_PADRAO, CONFIG_SENTIDOS_LIGADA, TICKS_POR_DIA)
from digilab.corpo import leitura_orgao  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.events import AcaoPet, LogDeEventos  # noqa: E402
from digilab.grupo import PetDoGrupo, RegistroGrupo, reproduzir_grupo, sementes_do_grupo, simular_grupo  # noqa: E402
from digilab.instinto_mundo import PoliticaInstintoMundo, para_onde_comer, sente_cheiro_comida  # noqa: E402
from digilab.motor_corpo import PercepcaoCorpo, com_corpo  # noqa: E402
from digilab.mundo import (CANDIDATOS_CHEIRO_ORGAO, DIR16, Alvo, DonoComLugar, MotorMundo, PercepcaoMundo,  # noqa: E402
                           alvo_padrao_de, alvos_do_olfato, deslocar, leitura_do_olfato, olfato_forte, reproduzir_mundo,
                           simular_vida_mundo)
from digilab.policies import lobos as lb  # noqa: E402
from digilab.policies.lobos import PoliticaLobos  # noqa: E402

CM = gdp.LAYOUTS["padrao"]
SUB = CM.sub
DIST = CM.passo_cheiro_celulas * SUB
S = CONFIG_CORPO_DRIVES.escala_receptor
OLFATO = {n: replace(CONFIG_OLFATO, ligada=True, comida=True, narinas=n) for n in (1, 2)}
TODOS = replace(CONFIG_OLFATO, ligada=True, comida=True, outro_pet=True)
OUVIDO = replace(CONFIG_OUVIDO, ligada=True)
MotorMundoCorpo = com_corpo(MotorMundo)
DIAS = 3
CL_T3 = bv.cfg_lobos_do_ponto("T3")


# ================================================================== as ajudas
def _texto(obj) -> str:
    return json.dumps(obj, sort_keys=True, default=repr)


def fabrica(co=OLFATO[2], cv=CONFIG_OUVIDO, cc=CONFIG_CORPO_DRIVES):
    def fm(p, cfg, s, **kw):
        m = MotorMundoCorpo(p, cfg, s, obediencia_desligada=True, cfg_mundo=CM, cfg_corpo=cc, cfg_olfato=co, cfg_ouvido=cv, **kw)
        alvo = getattr(p, "_espiao", p)
        if isinstance(alvo, Espiao):
            alvo.motor = m
        return m
    return fm


class Espiao:
    """embrulha um cerebro e guarda, a cada decisao, a observacao (o mundo, o corpo e o social) e, a cada alvo, o que o motor ofereceu e o
    que o pet sentia (a leitura das narinas, a direcao do ultimo passo e a leitura da decisao anterior), sem mudar nada"""

    def __init__(self, p) -> None:
        self._p = p
        self.motor = None
        self.obs: list = []
        self.alvos: list = []

    def agir(self, obs, rng):
        self.obs.append(obs)
        return self._p.agir(obs, rng)

    def escolher_alvo(self, acao, cands, percepcao, u):
        m = self.motor
        self.alvos.append({"acao": acao, "cands": list(cands), "p": percepcao, "u": u, "passo": m._passo, "anterior": m._olfato_anterior,
                           "corpo": m._obs_decisao.corpo, "k": len(self.obs) - 1})
        escolher = getattr(self._p, "escolher_alvo", None)
        return escolher(acao, cands, percepcao, u) if escolher is not None else None

    def __getattr__(self, nome):
        return getattr(self._p, nome)


def cerebro(nome: str, cc=CONFIG_CORPO_DRIVES):
    if nome == "instinto":
        return lambda cfg=None: Espiao(PoliticaInstintoMundo(cfg or CONFIG_PADRAO))  # noqa: E731
    if nome == "lobos":
        return lambda cfg=None: Espiao(PoliticaLobos(cfg or CONFIG_PADRAO, lb.CONFIG_LOBOS_APRENDIZ if hasattr(lb, "CONFIG_LOBOS_APRENDIZ")  # noqa: E731
                                                     else CL_T3, cfg_mundo=CM, cfg_corpo=cc))
    if nome == "p1_alvo":
        cl = replace(CL_T3, alvo_aprendido=True)
        return lambda cfg=None: Espiao(bv.PoliticaDoBraco(PoliticaLobos(cfg or CONFIG_PADRAO, cl, cfg_mundo=CM, cfg_corpo=cc),  # noqa: E731
                                                          bv.braco_de("P1"), CONFIG_CONSEQUENCIA))
    if nome == "p0_alvo":
        cl = replace(CONFIG_LOBOS, alvo_aprendido=True)
        return lambda cfg=None: Espiao(PoliticaLobos(cfg or CONFIG_PADRAO, cl, cfg_mundo=CM, cfg_corpo=cc))  # noqa: E731
    raise ValueError(nome)


def vida(nome="instinto", co=OLFATO[2], s=101, dono="aleatorio", lugar="longe", dias=DIAS):
    fp = cerebro(nome)
    fm = fabrica(co)
    dl = DonoComLugar(criar_dono(dono), lugar, s, dono, CM)
    v = simular_vida_mundo(dono, dl, fp(CONFIG_PADRAO), s, dias, 16 * dias, fm, rotulo_dono=dono)
    return v, fp, fm


def _esp(motor) -> Espiao:
    return motor.politica._pm


def ref_alvos(x, y, passo, leitura, anterior, u):
    """a regra da secao 5.6 escrita de novo, pela tabela DIR16: (tipo, direcao) na ordem do motor"""
    if max(leitura) == 0:
        return []
    if len(leitura) == 2:
        esq, dir_ = leitura
        if esq > dir_:
            v = (passo + 2) % 16
        elif dir_ > esq:
            v = (passo + 14) % 16
        else:
            v = (passo + 2) % 16 if ((u // 256) % 2) == 0 else (passo + 14) % 16
        prefere = esq != dir_
    else:
        v = (passo + 1 + (u // 256) % 15) % 16
        prefere = anterior is not None and leitura[0] < anterior[0]
    seguir = Alvo("cheiro_seguir", *deslocar(x, y, passo, DIST, CM))
    vira = Alvo("cheiro_virar", *deslocar(x, y, v, DIST, CM))
    return [vira, seguir] if prefere else [seguir, vira]


def pc(**kw) -> PercepcaoCorpo:
    return PercepcaoCorpo(fome=S, higiene=S, energia=S, humor=S, saude=S, **kw)


def perc(cheiro=0, direcao=0, vistos=()) -> PercepcaoMundo:
    return PercepcaoMundo(200, 240, 0, tuple(vistos), cheiro, direcao, None)


# ================================================================== G2
def test_g2_os_grupos_com_o_olfato_social_e_a_audicao_sao_os_de_antes():
    """sem o Olfato da comida, a percepcao do mundo e os candidatos sao os de hoje; o Olfato social e a Audicao so tiram a direcao da
    percepcao dos sentidos, que nenhum cerebro le: os 16 grupos do gabarito, byte a byte"""
    gravado = json.loads(gosd.ARQUIVO.read_text(encoding="utf-8"))
    casos = dict(gosd.casos())
    assert set(gravado) == set(casos) and len(gravado) == 16
    for chave, caso in casos.items():
        assert gosd.impressao(gosd.grupo(*caso)) == gravado[chave], chave


def test_g2_sem_o_orgao_nada_do_orgao():
    """sem o orgao (sem o corpo, ou o corpo sem o Olfato da comida): a percepcao com o cheiro de hoje e nenhum candidato do orgao"""
    for co in (CONFIG_OLFATO, replace(CONFIG_OLFATO, ligada=True, outro_pet=True)):
        v, _, _ = vida("instinto", co if co.ligada else CONFIG_OLFATO, 202, "aleatorio", "longe", 2)
        esp = _esp(v.motor)
        assert not v.motor._olfato_comida() and v.motor._olfato_anterior is None
        assert any(o.mundo.direcao_cheiro for o in esp.obs)
        assert not any(a.tipo in CANDIDATOS_CHEIRO_ORGAO for r in esp.alvos for a in r["cands"])
        assert any(a.tipo == "cheiro" for r in esp.alvos for a in r["cands"])
    sem_corpo = MotorMundo(PoliticaInstintoMundo(CONFIG_PADRAO), CONFIG_PADRAO, 1, obediencia_desligada=True, cfg_mundo=CM)
    assert not (sem_corpo._olfato_comida() or sem_corpo._olfato_outro() or sem_corpo._audicao())


# ================================================================== a mecanica exata
@pytest.mark.parametrize("passo", [0, 3, 8, 15])
def test_duas_narinas_virar_para_a_mais_forte(passo):
    x, y = 300, 240
    esq = alvos_do_olfato(x, y, passo, (50, 10), None, 0, CM)
    dir_ = alvos_do_olfato(x, y, passo, (10, 50), None, 0, CM)
    assert [a.tipo for a in esq] == [a.tipo for a in dir_] == ["cheiro_virar", "cheiro_seguir"]       # diferentes: virar na frente
    assert esq[0] == Alvo("cheiro_virar", *deslocar(x, y, (passo + 2) % 16, DIST, CM))                  # 45 graus para a esquerda
    assert dir_[0] == Alvo("cheiro_virar", *deslocar(x, y, (passo - 2) % 16, DIST, CM))                 # e para a direita
    assert esq[1] == dir_[1] == Alvo("cheiro_seguir", *deslocar(x, y, passo, DIST, CM))
    # empatadas: seguir na frente, e o lado do virar sai do bit 8 do u
    for u, lado in ((0, 2), (255, 2), (256, -2), (511, -2), (512, 2), (65535, -2)):
        par = alvos_do_olfato(x, y, passo, (30, 30), None, u, CM)
        assert [a.tipo for a in par] == ["cheiro_seguir", "cheiro_virar"]
        assert par[1] == Alvo("cheiro_virar", *deslocar(x, y, (passo + lado) % 16, DIST, CM))


def test_a_esquerda_e_anti_horaria():
    """a narina esquerda fica a passo + 4 (pontos_laterais) e o virar para ela e passo + 2: os dois do mesmo lado do passo"""
    for passo in range(16):
        e, d = mundo.pontos_laterais(0, 0, passo, 64)
        cx, cy = DIR16[passo]
        vx, vy = DIR16[(passo + 2) % 16]
        assert cx * e[1] - cy * e[0] < 0 and cx * vy - cy * vx < 0          # y cresce para o sul: o mesmo sinal do produto vetorial
        assert cx * d[1] - cy * d[0] > 0


def test_uma_narina_subiu_ou_caiu():
    x, y, passo = 500, 100, 5
    primeira = alvos_do_olfato(x, y, passo, (40,), None, 0, CM)
    assert [a.tipo for a in primeira] == ["cheiro_seguir", "cheiro_virar"]
    assert [a.tipo for a in alvos_do_olfato(x, y, passo, (40,), (40,), 0, CM)] == ["cheiro_seguir", "cheiro_virar"]   # ficou
    assert [a.tipo for a in alvos_do_olfato(x, y, passo, (41,), (40,), 0, CM)] == ["cheiro_seguir", "cheiro_virar"]   # subiu
    assert [a.tipo for a in alvos_do_olfato(x, y, passo, (39,), (40,), 0, CM)] == ["cheiro_virar", "cheiro_seguir"]   # caiu
    # o virar de uma narina: uma das outras 15 direcoes, pelos bits altos do u, nunca a do passo
    vistas = set()
    for u in range(0, 1 << 16, 256):
        v = alvos_do_olfato(x, y, passo, (40,), None, u, CM)[1]
        d = (passo + 1 + (u >> 8) % 15) % 16
        assert v == Alvo("cheiro_virar", *deslocar(x, y, d, DIST, CM)) and d != passo
        vistas.add(d)
    assert vistas == set(range(16)) - {passo}


def test_sem_cheiro_nenhum_candidato_e_as_falhas_altas():
    assert alvos_do_olfato(1, 1, 0, (0, 0), None, 0, CM) == [] == alvos_do_olfato(1, 1, 0, (0,), (9,), 0, CM)
    for args in (dict(passo=16), dict(passo=-1), dict(u=1 << 16), dict(u=-1)):
        kw = {"passo": 0, "u": 0, **args}
        with pytest.raises(ValueError):
            alvos_do_olfato(1, 1, kw["passo"], (5, 5), None, kw["u"], CM)
    with pytest.raises(ValueError, match="narinas"):
        alvos_do_olfato(1, 1, 0, (5, 5, 5), None, 0, CM)


def test_a_leitura_e_o_limiar_do_explorar():
    assert leitura_do_olfato(pc(olfato_comida_esq=7, olfato_comida_dir=0), 2) == (7, 0)
    assert leitura_do_olfato(pc(olfato_comida=9), 1) == (9,)
    with pytest.raises(ValueError, match="sem o receptor"):
        leitura_do_olfato(pc(olfato_comida=9), 2)
    with pytest.raises(ValueError, match="narinas"):
        leitura_do_olfato(pc(), 3)
    # o limiar de hoje (intensidade 16) lido pelo receptor sem adaptacao: e = 16 - 4 = 12; r = div_arred(1024 x 12, 12 + 32) = 279
    m = MotorMundoCorpo(PoliticaInstintoMundo(CONFIG_PADRAO), CONFIG_PADRAO, 1, obediencia_desligada=True, cfg_mundo=CM,
                        cfg_corpo=CONFIG_CORPO_DRIVES, cfg_olfato=OLFATO[2])
    assert CM.limiar_cheiro_explorar == 16 and m._limiar_olfato_explorar() == leitura_orgao(16, 0, 4, 32, S) == 279
    assert not olfato_forte((279, 0), 279) and olfato_forte((0, 280), 279)


def test_o_alvo_padrao_com_os_candidatos_do_orgao():
    seg, vir = Alvo("cheiro_seguir", 10, 10), Alvo("cheiro_virar", 12, 8)
    vagar, casa = Alvo("vagar", 50, 50), Alvo("casa", 160, 240)
    p = perc()
    assert alvo_padrao_de(AcaoPet.COMER, [vir, seg], p, CM) is vir
    assert alvo_padrao_de(AcaoPet.COMER, [seg, vir], p, CM) is seg
    comida = Alvo("comida", 3, 3, 7)
    assert alvo_padrao_de(AcaoPet.COMER, [comida, seg, vir], perc(vistos=((7, "racao", 1, 1, 1),)), CM) is comida
    assert alvo_padrao_de(AcaoPet.EXPLORAR, [seg, vir, vagar, casa], p, CM) is seg
    assert alvo_padrao_de(AcaoPet.EXPLORAR, [vagar, casa], p, CM) is vagar
    cont = Alvo("continuar", 1, 1, None, "vagar")
    assert alvo_padrao_de(AcaoPet.EXPLORAR, [seg, vir, vagar, casa, cont], p, CM) is cont


# ================================================================== G-SEM-DIRECAO por AST
PROIBIDOS = {"direcao_cheiro", "cheiro", "direcao_do_cheiro", "direcao_do_campo", "cheiro_em", "campo_em", "fontes_de_cheiro",
             "comidas", "mundo", "perceber", "cheiro_do_pet", "fontes_do_pet", "vistos", "arvores", "_percepcao"}


def _nomes(obj) -> set:
    arvore = ast.parse(textwrap.dedent(inspect.getsource(obj)))
    nomes = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Name):
            nomes.add(no.id)
        elif isinstance(no, ast.Attribute):
            nomes.add(no.attr)
    return nomes


@pytest.mark.parametrize("obj", [leitura_do_olfato, olfato_forte, alvos_do_olfato, sente_cheiro_comida,
                                 MotorMundo._leitura_olfato_decisao, MotorMundo._limiar_olfato_explorar, MotorMundo._alvos_olfato])
def test_g_sem_direcao_ast_o_orgao_nao_le_o_mundo(obj):
    """as funcoes do caminho do orgao so leem o que o pet sente (os receptores, o ultimo passo, a leitura anterior, o u) e os numeros
    da config; nenhuma le o cheiro, a direcao, as comidas ou a percepcao do mundo"""
    assert not (_nomes(obj) & PROIBIDOS), _nomes(obj) & PROIBIDOS


def test_g_sem_direcao_ast_a_percepcao_so_calcula_a_direcao_sem_o_orgao():
    """no Mundo.perceber, a unica chamada a direcao do cheiro esta no ramo de `cheiro` verdadeiro"""
    fonte = textwrap.dedent(inspect.getsource(mundo.Mundo.perceber))
    chamadas = [n for n in ast.walk(ast.parse(fonte)) if isinstance(n, ast.IfExp)
                and any(isinstance(c, ast.Call) and getattr(c.func, "id", None) == "direcao_do_cheiro" for c in ast.walk(n.body))]
    assert len(chamadas) == 1 and isinstance(chamadas[0].test, ast.Name) and chamadas[0].test.id == "cheiro"
    assert fonte.count("direcao_do_cheiro(") == 1


# ================================================================== G-SEM-DIRECAO por espiao
@pytest.mark.parametrize("narinas", [1, 2])
@pytest.mark.parametrize("nome", ["instinto", "lobos"])
def test_g_sem_direcao_espiao_a_vida_so_com_o_que_o_pet_sente(nome, narinas):
    for s, lugar in ((101, "longe"), (202, "perto")):
        v, _, _ = vida(nome, OLFATO[narinas], s, "aleatorio", lugar)
        m, esp = v.motor, _esp(v.motor)
        assert all(o.mundo.cheiro == 0 and o.mundo.direcao_cheiro == 0 for o in esp.obs)
        leituras = [leitura_do_olfato(o.corpo, narinas) for o in esp.obs]
        oferecidos, sentidos = 0, 0
        for r in esp.alvos:
            assert all(a.tipo != "cheiro" for a in r["cands"])
            k = r["k"]
            leitura = leituras[k]
            assert leitura == leitura_do_olfato(r["corpo"], narinas)
            assert r["anterior"] == (leituras[k - 1] if k > 0 else None)          # a leitura da decisao anterior, qualquer acao
            assert r["passo"] is not None
            p = r["p"]
            if r["acao"] is AcaoPet.EXPLORAR and not max(leitura) > m._limiar_olfato_explorar():
                esperado = []
            elif r["acao"] in (AcaoPet.COMER, AcaoPet.EXPLORAR):
                esperado = ref_alvos(p.x, p.y, r["passo"], leitura, r["anterior"], r["u"])
            else:
                esperado = []
            achados = [a for a in r["cands"] if a.tipo in CANDIDATOS_CHEIRO_ORGAO]
            assert achados == esperado
            oferecidos += bool(achados)
            sentidos += max(leitura) > 0
        assert oferecidos > 0 and sentidos > 0
        # o alvo padrao (o instinto nao tem escolher_alvo; os lobos do P3 devolvem None): o do motor e o da regra
        com_alvo = [d for d in m.decisoes_mundo if d["acao"] in ("explorar", "comer", "brincar")]
        assert len(com_alvo) == len(esp.alvos)
        for d, r in zip(com_alvo, esp.alvos):
            padrao = alvo_padrao_de(r["acao"], r["cands"], r["p"], CM)
            assert d["alvo"] == (None if padrao is None else padrao.tipo)


def test_g_sem_direcao_espiao_a_direcao_nem_e_calculada(monkeypatch):
    """com o Olfato da comida, a direcao do cheiro nunca e calculada: trocada por uma funcao que falha, a vida roda; sem o orgao, falha"""
    def falha(*a, **k):
        raise AssertionError("direcao do cheiro calculada")
    monkeypatch.setattr(mundo, "direcao_do_cheiro", falha)
    monkeypatch.setattr(mundo, "direcao_do_campo", falha)
    for n in (1, 2):
        vida("instinto", OLFATO[n], 303, "aleatorio", "longe", 2)
    with pytest.raises(AssertionError, match="direcao do cheiro"):
        vida("instinto", replace(CONFIG_OLFATO, ligada=True, outro_pet=True), 303, "aleatorio", "longe", 2)


def test_o_instinto_na_fome_urgente_le_so_as_narinas():
    """com o orgao, a fome urgente come se ha comida vista ou se alguma narina sente; o cheiro e a direcao do mundo nao contam"""
    assert sente_cheiro_comida(None) is None and sente_cheiro_comida(pc()) is None
    assert sente_cheiro_comida(pc(olfato_comida_esq=0, olfato_comida_dir=3)) is True
    assert sente_cheiro_comida(pc(olfato_comida=0)) is False
    assert para_onde_comer(perc(7, 3)) and not para_onde_comer(perc(7, 0))                       # sem o orgao, a regra de hoje
    assert not para_onde_comer(perc(7, 3), pc(olfato_comida_esq=0, olfato_comida_dir=0))          # com o orgao: o mundo nao conta
    assert para_onde_comer(perc(0, 0), pc(olfato_comida_esq=1, olfato_comida_dir=0))
    assert para_onde_comer(perc(0, 0, ((5, "a", 1, 1, 1),)), pc(olfato_comida=0))                  # a comida vista continua vista


# ================================================================== o cerebro A
def test_o_cerebro_a_le_os_dois_candidatos_como_a_classe_cheiro():
    assert set(lb.CLASSE_DO_CANDIDATO) == set(CANDIDATOS_CHEIRO_ORGAO)
    assert all(c in lb.CLASSES_ALVO[AcaoPet.COMER] and c in lb.CLASSES_ALVO[AcaoPet.EXPLORAR] for c in lb.CLASSE_DO_CANDIDATO.values())


@pytest.mark.parametrize("narinas", [1, 2])
def test_o_p1_com_o_alvo_aprendido_escolhe_entre_as_classes(narinas):
    """o P1 com o alvo aprendido vive com o orgao: o representante da classe `cheiro` e o primeiro candidato do orgao (o padrao, quando
    o padrao e cheiro), e a classe `cheiro` aparece nas escolhas"""
    classes = set()
    for s in (101, 202, 303):
        v, _, _ = vida("p1_alvo", OLFATO[narinas], s, "aleatorio", "longe")
        for mot in v.motor.politica.estado_interno()["motivos"]:
            al = mot.get("alvo_aprendido")
            if al:
                classes.update(al["classes"])
    assert "cheiro" in classes and not (classes & set(CANDIDATOS_CHEIRO_ORGAO))


@pytest.mark.parametrize("narinas", [1, 2])
def test_o_p0_com_o_alvo_aprendido_e_o_instinto_com_o_orgao(narinas):
    for s in (101, 202):
        a, _, _ = vida("p0_alvo", OLFATO[narinas], s)
        b, _, _ = vida("instinto", OLFATO[narinas], s)
        assert gdp.impressao(a.motor) | {"politica": None} == gdp.impressao(b.motor) | {"politica": None}
        assert a.motor.corpo.para_dict() == b.motor.corpo.para_dict()


# ================================================================== G1
@pytest.mark.parametrize("narinas", [1, 2])
@pytest.mark.parametrize("nome", ["instinto", "p1_alvo"])
def test_g1_o_replay_refaz_a_vida_com_o_orgao(nome, narinas):
    v, fp, fm = vida(nome, OLFATO[narinas], 202)
    r = reproduzir_mundo(LogDeEventos.de_jsonl(v.motor.log.para_jsonl()), fp, CONFIG_PADRAO, 202, fabrica_motor=fm)
    assert gdp.impressao(r) == gdp.impressao(v.motor)
    assert r.corpo.para_dict() == v.motor.corpo.para_dict()
    assert _texto(r.politica.estado_interno()) == _texto(v.motor.politica.estado_interno())
    assert r._olfato_anterior == v.motor._olfato_anterior and r._passo == v.motor._passo


# ================================================================== o grupo: o Olfato social e a Audicao
def _pets_grupo(s, co, cv, entrada_b=0, dono="aleatorio"):
    sementes = sementes_do_grupo(s, CONFIG_GRUPO_LIGADA.ids)
    pets = []
    for ident in ("A", "B"):
        fp = cerebro("instinto")
        fm = fabrica(co, cv)
        d = DonoComLugar(criar_dono(dono), "perto", sementes[ident], dono, CM)
        pets.append(PetDoGrupo(ident, 0 if ident == "A" else entrada_b * TICKS_POR_DIA, fp, fm, d, dono, "instinto"))
    return pets


def test_g_sem_direcao_no_grupo_os_sentidos_sem_o_mundo(monkeypatch):
    """com o Olfato social e a Audicao, a percepcao dos sentidos nunca traz o cheiro nem os sons do mundo (so o proprio passo); sem os
    orgaos, ela os traz (o controle). Com os tres orgaos, a direcao do cheiro do mundo nem e calculada."""
    s = 202
    sem = simular_grupo(CM, s, _pets_grupo(s, CONFIG_OLFATO, CONFIG_OUVIDO), DIAS, cfg_sentidos=CONFIG_SENTIDOS_LIGADA)
    obs_sem = [o.social.sentidos for m in sem.motores.values() for o in _esp(m).obs if o.social is not None]
    assert any(x.cheiro for x in obs_sem) and any(x.sons for x in obs_sem)

    def falha(*a, **k):
        raise AssertionError("direcao do cheiro calculada")
    monkeypatch.setattr(mundo, "direcao_do_campo", falha)
    monkeypatch.setattr(mundo, "direcao_do_cheiro", falha)
    import digilab.grupo as grupo_mod
    monkeypatch.setattr(grupo_mod, "cheiro_do_pet", falha)
    com = simular_grupo(CM, s, _pets_grupo(s, TODOS, OUVIDO), DIAS, cfg_sentidos=CONFIG_SENTIDOS_LIGADA)
    obs_com = [o for m in com.motores.values() for o in _esp(m).obs if o.social is not None]
    assert obs_com and all(o.social.sentidos.cheiro == () and o.social.sentidos.sons == () for o in obs_com)
    assert all(0 <= o.social.sentidos.passo < 16 for o in obs_com)
    assert com.sons                                                    # os sons soaram (o registro do grupo) e chegaram so pelo ouvido
    assert any(getattr(o.corpo, f"ouvido_{som}_esq") for o in obs_com for som in ("comendo", "bola", "chamado", "emburrado"))
    assert any(o.corpo.olfato_outro_esq for o in obs_com)


def test_g1_o_replay_refaz_o_grupo_com_os_orgaos():
    s = 303
    g = simular_grupo(CM, s, _pets_grupo(s, TODOS, OUVIDO, 1), DIAS, cfg_sentidos=CONFIG_SENTIDOS_LIGADA)
    fabricas = {p.ident: (p.politica_fabrica, p.fabrica_motor) for p in _pets_grupo(s, TODOS, OUVIDO, 1)}
    r = reproduzir_grupo(RegistroGrupo.de_jsonl(g.registro.para_jsonl()), fabricas, CM, cfg_sentidos=CONFIG_SENTIDOS_LIGADA)
    assert _texto(r.resumo()) == _texto(g.resumo())
    assert {i: m.corpo.para_dict() for i, m in r.motores.items()} == {i: m.corpo.para_dict() for i, m in g.motores.items()}
    assert {i: m._olfato_anterior for i, m in r.motores.items()} == {i: m._olfato_anterior for i, m in g.motores.items()}
