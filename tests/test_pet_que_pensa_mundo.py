"""V2, o pet que pensa (J5), o mundo e as classes por arvore (docs/TAREFA_V2_PET_QUE_PENSA.md, secao 2.3 e 2.4, etapas 3 e 2b; PP-1, PP-2
e PP-5 do docs/PLANO_ANALISE_V2_PET_QUE_PENSA.md). So as sementes dos testes. Gates:
- G2: as chaves desligadas (ConfigPetQuePensaMundo e ConfigLobos.alvo_por_arvore) sao a vida de hoje: as 48 vidas de
  tests/gabaritos/pqp_mundo_vidas_de_hoje.json, gravado antes da mudanca (tests/gabarito_pqp_mundo.py, commit proprio);
- os eventos no fim do enum, e os motores de hoje que os recusam;
- os troncos vistos e a percepcao deles; os candidatos `arvore:<id>` so de troncos vistos, depois dos de hoje (PP-1); o padrao e o instinto
  nunca os escolhem;
- G-SEM-CREDITO: a fruta na mao chega so ao gancho `fruta_na_mao` (com o corpo), nao ao `receber_acao_dono`, ao `fruta_comida`, ao
  `consequencia_mundo`, ao `mudanca_no_corpo` nem ao `consequencia_corpo`, e nao mexe em peso do A; a conta exata da mao;
- a troca de tipo no tick, com as quedas antes no tipo velho e depois no novo, e o chao como estava;
- as classes por arvore no alvo aprendido (PP-2): a contagem, a falha alta, o P0 no prior e a conta exata pela consequencia;
- G1: o replay refaz a vida com tudo ligado, sem e com o corpo.
"""
from __future__ import annotations

import copy
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

import bancada_v2 as bv  # noqa: E402
import gabarito_pqp_mundo as g  # noqa: E402
from digilab.config import (CONFIG_DONOS, CONFIG_GRUPO_LIGADA, CONFIG_LOBOS, CONFIG_PADRAO, CONFIG_PQP_MUNDO,  # noqa: E402
                            CONFIG_PQP_MUNDO_LIGADA, TICKS_POR_DIA, ConfigLobos, ConfigPetQuePensaMundo)
from digilab.donos import Visao, criar_dono  # noqa: E402
from digilab.events import (ACOES_CORPO, ACOES_MAO, ACOES_TROCA_ARVORES, FRUTAS, AcaoPet, AcaoUsuario, dar_fruta,  # noqa: E402
                            fruta_dada, par_da_troca, trocar_arvores)
from digilab.grupo import Grupo  # noqa: E402
from digilab.instinto_mundo import PoliticaInstintoMundo  # noqa: E402
from digilab.mundo import (Alvo, CanalMundo, DonoComLugar, MotorMundo, PercepcaoMundo, PetQuePensaSemChave,  # noqa: E402
                           alvo_padrao_de, distancia, reproduzir_mundo)
from digilab.policies import lobos as lb  # noqa: E402
from digilab.policies.lobos import PoliticaLobos, sinal_homeostatico  # noqa: E402
from digilab.policy import Observacao, PoliticaInstinto, Transicao  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402
from digilab.treino import MotorComFeedback  # noqa: E402

CM = g.LAYOUTS["padrao"]
S = CONFIG_LOBOS.escala
P1_ARV = replace(g.P1_ALVO, alvo_por_arvore=True)
P0_ARV = replace(g.P0_ALVO, alvo_por_arvore=True)
ARVORES = tuple(f"arvore:{a[0]}" for a in CM.layout.arvores)
DIAS = 4


# ================================================================== ajudas
class Espiao:
    """embrulha o cerebro e anota os ganchos (repassa tudo)"""

    def __init__(self, base) -> None:
        self.base = base
        self.chamadas: list[tuple] = []
        self.maos: list[tuple] = []

    def fruta_na_mao(self, f, antes, depois) -> None:
        self.maos.append((f, antes, depois))

    def receber_acao_dono(self, acao, tick) -> None:
        self.chamadas.append(("receber_acao_dono", acao, tick))
        self.base.receber_acao_dono(acao, tick)

    def __getattr__(self, nome):
        atributo = getattr(self.base, nome)
        if nome in ("fruta_comida", "consequencia_mundo", "mudanca_no_corpo", "consequencia_corpo") and callable(atributo):
            def anotado(*a, **kw):
                self.chamadas.append((nome,) + a[:1])
                return atributo(*a, **kw)
            return anotado
        return atributo


def fabricas(corpo: str = "sem", cerebro: str = "P1", cl: ConfigLobos = P1_ARV, x: str = "b", cpq=CONFIG_PQP_MUNDO_LIGADA,
             espiao: list | None = None):
    cm, cc = CM, g.CORPOS[corpo]
    if cerebro == "instinto":
        def fp(cfg=None):
            return PoliticaInstintoMundo(cfg or CONFIG_PADRAO)
    elif cerebro == "P0":
        def fp(cfg=None):
            return PoliticaLobos(cfg or CONFIG_PADRAO, cl, cfg_mundo=cm)
    else:
        def fp(cfg=None):
            p = bv.PoliticaDoBraco(PoliticaLobos(cfg or CONFIG_PADRAO, cl, cfg_mundo=cm, cfg_corpo=cc), bv.braco_de("P1"), g.CC_CANAIS)
            if espiao is not None:
                p = Espiao(p)
                espiao.append(p)
            return p
    _, fm = g.fabricas("padrao", corpo, "instinto", x, cfg_pqp=cpq)
    return fp, fm


def vida(fp, fm, semente=101, lugar="comedouro", dias=DIAS, eventos=None):
    """a vida com o atencioso; `eventos(motor)` e chamado depois das acoes do dono de cada passo (o canal do mundo, fora do orcamento)"""
    m = fm(fp(CONFIG_PADRAO), CONFIG_PADRAO, semente)
    dono = DonoComLugar(criar_dono("atencioso"), lugar, semente, "atencioso", CM)
    rng = random.Random(derivar_semente("dono", semente, "atencioso"))
    orcamento = 16 * dias
    canal = CanalMundo(m, orcamento, CONFIG_DONOS.max_interacoes_por_passo)
    passos = dias * TICKS_POR_DIA // CONFIG_DONOS.passo_ticks
    for passo in range(passos):
        m.avancar(CONFIG_DONOS.passo_ticks)
        mi, ma = canal.limites(passo, passos)
        canal.aplicar(dono.decidir(Visao(estado=m.estado(), passo=passo, passos_totais=passos, orcamento=orcamento, gasto=canal.gasto,
                                         minimo_obrigatorio=mi, maximo_permitido=ma), rng), passo, passos)
        if eventos is not None:
            eventos(m)
    canal.fechar()
    return m, canal.gasto


def mao_e_troca(dia=3, x="b", y="c", n_mao=2):
    """o protocolo do plano: no primeiro passo do dono depois das 8 h do dia com o pet acordado, a x na mao n vezes e a troca"""
    feito = {"tick": None}

    def eventos(m):
        t = m._estado.tick
        if feito["tick"] is None and t >= dia * TICKS_POR_DIA + 8 * 60 and not m._estado.dormindo:
            for _ in range(n_mao):
                m.observar(dar_fruta(x))
            if y is not None:
                m.observar(trocar_arvores(x, y))
            feito["tick"] = t
    return eventos, feito


def resumo(m) -> dict:
    return {"fisico": json.dumps(m.resumo_mundo_fisico(), sort_keys=True, default=repr), "estado": repr(m._estado),
            "log": m.log.para_jsonl(), "politica": json.dumps(m.politica.estado_interno(), sort_keys=True, default=repr)}


# ================================================================== G2
def test_g2_chaves_desligadas_sao_a_vida_de_hoje():
    gab = json.loads(g.ARQUIVO.read_text(encoding="utf-8"))
    casos = list(g.casos())
    assert len(casos) == len(gab) == 48
    for chave, caso in casos:
        assert g.impressao_de(caso) == gab[chave], chave
    for chave, caso in casos[:12]:                          # com a chave dada desligada, a mesma coisa
        assert g.impressao_de(caso, cfg_pqp=CONFIG_PQP_MUNDO) == gab[chave], chave


def test_os_padroes_das_chaves():
    assert CONFIG_PQP_MUNDO == ConfigPetQuePensaMundo() and not CONFIG_PQP_MUNDO.ligada
    assert CONFIG_LOBOS.alvo_por_arvore is False
    lb.validar_parametros_lobos()
    assert lb.PARAMETROS_LOBOS["alvo_por_arvore"][0] == "PROPOSTO"


# ================================================================== o enum e as recusas
def test_eventos_no_fim_do_enum_e_os_de_antes_nao_andaram():
    todos = list(AcaoUsuario)
    assert todos.index(ACOES_CORPO[0]) == 29 and len(todos) == 36
    assert todos[30:33] == list(ACOES_MAO) and todos[33:36] == list(ACOES_TROCA_ARVORES)
    assert [fruta_dada(a) for a in ACOES_MAO] == list(FRUTAS) and dar_fruta("c") is AcaoUsuario.DAR_FRUTA_C
    assert [par_da_troca(a) for a in ACOES_TROCA_ARVORES] == [("a", "b"), ("a", "c"), ("b", "c")]
    assert trocar_arvores("c", "a") is AcaoUsuario.TROCAR_ARVORES_A_C
    for erro in (lambda: fruta_dada(AcaoUsuario.TAPA), lambda: dar_fruta("d"), lambda: trocar_arvores("a", "a"),
                 lambda: par_da_troca(AcaoUsuario.TAPA)):
        with pytest.raises(ValueError):
            erro()


@pytest.mark.parametrize("acao", ACOES_MAO + ACOES_TROCA_ARVORES)
def test_motores_de_hoje_e_sem_a_chave_recusam(acao):
    m = MotorComFeedback(PoliticaInstinto(CONFIG_PADRAO), CONFIG_PADRAO, 101)
    with pytest.raises(ValueError):
        m.observar(acao)
    fp, fm = fabricas(cerebro="instinto", cpq=CONFIG_PQP_MUNDO)        # o mundo sem a chave do J5
    m2 = fm(fp(CONFIG_PADRAO), CONFIG_PADRAO, 101)
    m2.avancar(30)
    with pytest.raises(PetQuePensaSemChave):
        m2.observar(acao)


def test_a_chave_exige_o_mundo_e_um_pet():
    with pytest.raises(PetQuePensaSemChave):
        MotorMundo(PoliticaInstinto(CONFIG_PADRAO), CONFIG_PADRAO, 101, obediencia_desligada=True, cfg_pqp=CONFIG_PQP_MUNDO_LIGADA)
    grupo = Grupo(CM, 101, CONFIG_GRUPO_LIGADA)
    fm = lambda p, cfg, s, **kw: MotorMundo(p, cfg, s, obediencia_desligada=True, cfg_mundo=CM, cfg_pqp=CONFIG_PQP_MUNDO_LIGADA, **kw)  # noqa: E731
    with pytest.raises(PetQuePensaSemChave):
        grupo.entrar("A", PoliticaInstintoMundo(CONFIG_PADRAO), fm, "instinto", "atencioso")


def test_fruta_na_mao_com_o_pet_dormindo_falha_alto():
    fp, fm = fabricas(cerebro="instinto")
    m = fm(fp(CONFIG_PADRAO), CONFIG_PADRAO, 101)
    while not m._estado.dormindo:
        m.avancar(15)
    with pytest.raises(RuntimeError):
        m.observar(dar_fruta("a"))


# ================================================================== os troncos e os candidatos (PP-1)
def test_troncos_vistos_e_a_percepcao():
    fp, fm = fabricas(cerebro="instinto")
    m, _ = vida(fp, fm, semente=202, lugar="longe")
    raio = CM.raio_visao_celulas * CM.sub
    arv = {a["id"]: (a["x"], a["y"]) for a in m.mundo.arvores}
    esperado = {}
    posicoes = [(d["tick"], d["antes"]) for d in m.decisoes_mundo] + [(d["tick"], (d["x"], d["y"])) for d in m.decisoes_mundo]
    for t, (x, y) in sorted(posicoes, key=lambda p: p[0]):
        for ident, (ax, ay) in arv.items():
            if distancia(ax - x, ay - y) <= raio:
                esperado.setdefault(ident, t)
    assert m.troncos_vistos == esperado and esperado            # ao menos um tronco visto
    p = m._perceber(m._estado.tick)
    assert p.troncos == tuple(sorted(((i, ax - p.x, ay - p.y, distancia(ax - p.x, ay - p.y)) for i, (ax, ay) in arv.items()
                                      if distancia(ax - p.x, ay - p.y) <= raio), key=lambda t: (t[3], t[0])))
    fp0, fm0 = fabricas(cerebro="instinto", cpq=CONFIG_PQP_MUNDO)
    m0 = fm0(fp0(CONFIG_PADRAO), CONFIG_PADRAO, 202)
    assert m0._perceber(0).troncos == () and not hasattr(m0, "troncos_vistos")


def test_candidatos_de_arvore_lembrada_depois_dos_de_hoje():
    fp, fm = fabricas(cerebro="instinto")
    m, _ = vida(fp, fm, semente=202, lugar="longe", dias=2)
    m._antes_da_decisao()
    cands = m.candidatos(AcaoPet.EXPLORAR, 12345)
    tipos = [a.tipo for a in cands]
    k = next(i for i, t in enumerate(tipos) if t.startswith("arvore:"))
    assert all(not t.startswith("arvore:") for t in tipos[:k]) and all(t.startswith("arvore:") for t in tipos[k:])
    vistos = [a["id"] for a in m.mundo.arvores if a["id"] in m.troncos_vistos]
    assert tipos[k:] == [f"arvore:{i}" for i in vistos]
    for a in cands[k:]:
        tronco = next(t for t in m.mundo.arvores if f"arvore:{t['id']}" == a.tipo)
        assert (a.x, a.y) == (tronco["x"], tronco["y"]) and a.id is None and a.de is None
    assert [a.tipo for a in m.candidatos(AcaoPet.COMER, 1)] == [a.tipo for a in m.candidatos(AcaoPet.COMER, 1) if
                                                                 not a.tipo.startswith("arvore:")]
    assert alvo_padrao_de(AcaoPet.EXPLORAR, cands, m._percepcao, CM).tipo in ("cheiro", "vagar", "continuar")


@pytest.mark.parametrize("semente", (101, 202))
def test_o_instinto_e_o_p0_nunca_vao_a_arvore_lembrada(semente):
    """o padrao do motor e o instinto nunca os escolhem; o P0 com as classes por arvore no prior usa o padrao: o instinto byte a byte"""
    fi, fmi = fabricas(cerebro="instinto")
    mi, _ = vida(fi, fmi, semente=semente, lugar="longe")
    assert mi.troncos_vistos
    assert not [d for d in mi.decisoes_mundo if d["alvo"] and "arvore" in d["alvo"]]
    f0, fm0 = fabricas(cerebro="P0", cl=P0_ARV)
    m0, _ = vida(f0, fm0, semente=semente, lugar="longe")
    for chave in ("fisico", "estado", "log"):
        assert resumo(m0)[chave] == resumo(mi)[chave]


# ================================================================== a fruta na mao (G-SEM-CREDITO) e a troca
@pytest.mark.parametrize("corpo", ("sem", "quimica"))
def test_g_sem_credito_e_a_conta_exata_da_mao(corpo):
    espiao: list = []
    fp, fm = fabricas(corpo=corpo, espiao=espiao)
    estado = {}

    def eventos(m):
        t = m._estado.tick
        if not estado and t >= 3 * TICKS_POR_DIA + 8 * 60 and not m._estado.dormindo:
            e = espiao[0]
            cerebro = e.base.cerebro
            pesos = json.dumps(cerebro.estado_interno(), sort_keys=True, default=repr)
            chamadas = len(e.chamadas)
            e0 = m._estado
            corpo_antes = copy.deepcopy(m.corpo) if corpo != "sem" else None
            n_consumos = len(m.consumos_mundo)
            m.observar(dar_fruta("b"))
            estado.update(tick=t, e0=e0, e1=m._estado, pesos=pesos, chamadas=chamadas, corpo_antes=corpo_antes, n=n_consumos)
            assert json.dumps(cerebro.estado_interno(), sort_keys=True, default=repr) == pesos   # o A inteiro nao mexeu
            assert e.chamadas[chamadas:] == []                                        # nenhum gancho de credito
    m, gasto = vida(fp, fm, eventos=eventos)
    assert estado
    e0, e1 = estado["e0"], estado["e1"]
    ef = g.efeito_do_plano("b")["b"]
    assert e1.tick_ultimo_cuidado == e0.tick_ultimo_cuidado and e1.total_cuidados == e0.total_cuidados   # nao e contato
    if corpo == "sem":
        assert e1.fome == min(1.0, e0.fome + CM.nutricao_fruta) and e1.humor == min(1.0, max(0.0, e0.humor + ef))
    else:
        c = estado["corpo_antes"]
        c.estimulo_consumo_mundo("b", "madura", CM, ef)
        assert e1 == c.no_estado(e0)
    reg = m.consumos_mundo[estado["n"]]
    assert reg["como"] == "mao" and reg["tipo"] == "b" and reg["id"] is None and reg["tick"] == estado["tick"]
    (f, antes, depois), = espiao[0].maos
    assert f == "b" and antes.mundo is not None and depois.mundo is not None
    assert depois.vetor_estado[0] > antes.vetor_estado[0] or e0.fome == 1.0
    if corpo != "sem":
        assert antes.corpo is not None and depois.corpo is not None and depois.corpo.fome >= antes.corpo.fome
    assert gasto == 16 * DIAS                                                         # o orcamento do dono fecha igual


@pytest.mark.parametrize("corpo", ("sem", "quimica"))
def test_troca_de_tipo_no_tick_e_as_quedas(corpo):
    fp, fm = fabricas(corpo=corpo, cerebro="instinto")
    eventos, feito = mao_e_troca(n_mao=0)
    m, _ = vida(fp, fm, semente=202, lugar="longe", dias=6, eventos=eventos)
    t = feito["tick"]
    (troca,) = m.mundo.trocas_tipo
    assert troca["tick"] == t and (troca["x"], troca["y"]) == ("b", "c")
    velho = {a[0]: a[3] for a in CM.layout.arvores}
    novo = {i: ({"b": "c", "c": "b"}.get(f, f)) for i, f in velho.items()}
    assert {a["id"]: a["fruta"] for a in m.mundo.arvores} == novo
    assert troca["arvores"] == {i: f for i, f in novo.items() if velho[i] != f}
    comidas = {c["id"]: c for c in m.mundo.comidas.values()}
    todas = {**{c["id"]: c for c in m.mundo.sumidas}, **{c["id"]: c for c in m.consumos_mundo if c["id"] is not None}, **comidas}
    antes = depois = 0
    for q in m.mundo.quedas:
        tipo_certo = velho[q["arvore"]] if q["tick"] <= t else novo[q["arvore"]]
        for i in q["colocadas"]:
            if i in todas:
                assert todas[i]["tipo"] == tipo_certo
        antes += q["tick"] <= t
        depois += q["tick"] > t
    assert antes and depois


@pytest.mark.parametrize("corpo", ("sem", "quimica"))
def test_g1_com_tudo_ligado(corpo):
    """o P1 com as classes por arvore e os candidatos, a x na mao duas vezes e a troca: o replay do log refaz tudo bit a bit"""
    fp, fm = fabricas(corpo=corpo)
    eventos, feito = mao_e_troca()
    m, _ = vida(fp, fm, eventos=eventos)
    assert feito["tick"] is not None
    assert [c for c in m.consumos_mundo if c["como"] == "mao"] and m.mundo.trocas_tipo
    r = reproduzir_mundo(m.log, fp, CONFIG_PADRAO, 101, fm)
    assert resumo(r) == resumo(m)


# ================================================================== as classes por arvore (PP-2)
def test_classes_por_arvore_contagem_e_falhas():
    sem = PoliticaLobos(CONFIG_PADRAO, g.P1_ALVO, cfg_mundo=CM)
    com = PoliticaLobos(CONFIG_PADRAO, P1_ARV, cfg_mundo=CM)
    assert com.n_pesos() - sem.n_pesos() == 27
    for chave, tab in com._pesos_alvo_mundo.items():
        base = list(sem._pesos_alvo_mundo[chave])
        if chave.endswith(":explorar"):
            assert list(tab) == base + list(ARVORES) and all(tab[a] == P1_ARV.w0_alvo for a in ARVORES)
        else:
            assert list(tab) == base
    with pytest.raises(ValueError):
        PoliticaLobos(CONFIG_PADRAO, replace(CONFIG_LOBOS, alvo_por_arvore=True), cfg_mundo=CM)
    with pytest.raises(TypeError):
        PoliticaLobos(CONFIG_PADRAO, replace(P1_ARV, alvo_por_arvore=1), cfg_mundo=CM)
    # sem a chave das classes, um candidato de arvore no alvo aprendido falha alto
    p = PoliticaLobos(CONFIG_PADRAO, g.P1_ALVO, cfg_mundo=CM)
    a = p.agir(_obs(), _U(0.5))
    assert a is AcaoPet.EXPLORAR
    with pytest.raises(ValueError):
        p.escolher_alvo(a, [Alvo("vagar", 300, 240), Alvo("arvore:J2", 40, 40)], _perc(), 1)


class _U:
    def __init__(self, u: float) -> None:
        self.u = u

    def random(self) -> float:
        return self.u


def _perc() -> PercepcaoMundo:
    return PercepcaoMundo(200, 240, 0, (), 0, 0, None)


def _obs(fome=0.8, energia=0.7, humor=0.5) -> Observacao:
    return Observacao(vetor_estado=(fome, 0.8, energia, humor, 1.0, 0.0, 0.0, 0.5), ticks_desde_cuidado=30, total_cuidados=0,
                      mundo=_perc())


def test_classes_por_arvore_conta_exata_pela_consequencia():
    """a arvore (a classe que o padrao nao usa) sorteada no fim da roleta; a consequencia sobe ou desce o peso dela pela regra da fruta;
    o sinal do dono nao mexe nele"""
    p = PoliticaLobos(CONFIG_PADRAO, P1_ARV, cfg_mundo=CM)
    cands = [Alvo("vagar", 300, 240), Alvo("arvore:J2", 464, 328)]
    a = p.agir(_obs(), _U(0.5))
    assert a is AcaoPet.EXPLORAR and p.ultima_regra == "tempo_livre"
    # pesos: vagar 1 + 64/1024 = 1,0625; arvore:J2 0,0625. u / 2^16 x 1,125 >= 1,0625 desde u = 61896
    alvo = p.escolher_alvo(a, cands, _perc(), 61896)
    assert alvo.tipo == "arvore:J2"
    sub = p._registro_decisao["alvo_mundo"]
    assert sub["candidatos"] == ("vagar", "arvore:J2") and sub["acao"] == "arvore:J2"
    antes, depois = _obs(), _obs(energia=0.66)
    t = Transicao(antes, AcaoPet.EXPLORAR, depois)
    f = sinal_homeostatico(t, S, g.CC_CANAIS)
    p.observar_consequencia(t, f, g.CC_CANAIS)
    p.consequencia_mundo(AcaoPet.EXPLORAR, {"acao": "explorar", "alvo": {"tipo": "arvore:J2"}, "chegou": False, "deslocamento": 0,
                                            "comeu": None, "brincou_com_bola": False}, depois)
    assert f < 0
    tab = p._pesos_alvo_mundo["tempo_livre:explorar"]
    esperado = dict(p._prior_alvo_mundo["tempo_livre:explorar"])
    for c in sub["candidatos"]:
        fator = (S if c == "arvore:J2" else 0) - sub["P"][c]
        esperado[c] += lb.div_arred(f * P1_ARV.passo * S * fator, S * S * sub["W"][c])
    assert tab == esperado and tab["arvore:J2"] < P1_ARV.w0_alvo
    # o dono nao ensina o alvo
    q = PoliticaLobos(CONFIG_PADRAO, P1_ARV, cfg_mundo=CM)
    q.agir(_obs(), _U(0.5))
    q.escolher_alvo(AcaoPet.EXPLORAR, cands, _perc(), 61896)
    q.receber_acao_dono(AcaoUsuario.ELOGIAR, 15)
    assert q._pesos_alvo_mundo == q._prior_alvo_mundo


def test_o_p1_vai_as_arvores_lembradas():
    fp, fm = fabricas()
    m, _ = vida(fp, fm, semente=101)
    idas = [d["alvo"] for d in m.decisoes_mundo if d["alvo"] and d["alvo"].startswith("arvore:")]
    assert idas and set(idas) <= {f"arvore:{i}" for i in m.troncos_vistos}
