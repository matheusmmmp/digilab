"""C3, etapa 2 (docs/TAREFA_V3_REDECIDIR_EVENTO.md, secoes 3.1 e 3.2; RD-1 a RD-9 DECIDIDAS em 2026-10-31; a espec em
docs/ESPEC_REDECIDIR_EVENTO_DIGIBRAIN_MODULAR.md): a subchave `redecidir_evento` do DigiBrain modular, a escolha segurada ate um evento,
antes de qualquer vida de pesquisa. So as sementes 101 a 505 e sequencias sinteticas.

  - G2: com ela desligada, as vidas de hoje saem byte a byte (tests/test_gabarito_redecidir_evento.py, o gabarito do M3* gravado antes, e
    tests/test_gabarito_habito_intencao.py, o do M2, mais os do conserto e do modular); aqui, o que a desligada nao cria (campo, estado);
  - G2-SEPARADO: ligada, ela muda so a vida do braco que a liga; nada fora do pacote `digibrain` e do orquestrador le a chave;
  - G1: o replay de cada vida com ela ligada, nas cinco sementes, com o M3* e o M2;
  - T-RD-1 a T-RD-4 (secao 3.2 da tarefa);
  - o `conferir_redecidir` do orquestrador falha alto;
  - G-MECANISMO e os testes de mecanismo de hoje com ela ligada; a rng."""
from __future__ import annotations

import inspect
import json
import sys
from dataclasses import fields, replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import run_v2_digibrain_prototipo as orq  # noqa: E402
import test_digibrain_mecanismo as tm  # noqa: E402

from digilab.config import (CONFIG_DIGIBRAIN, CONFIG_DIGIBRAIN_INATOS, CONFIG_DIGIBRAIN_LIGADA, CONFIG_PADRAO,  # noqa: E402
                            PARAMETROS_DIGIBRAIN_INATOS, ConfigDigibrain, ConfigDigibrainInatos)
from digilab.digibrain.arb import Arbitragem  # noqa: E402
from digilab.digibrain.estado import EVENTOS, EstadoDinamico  # noqa: E402
from digilab.digibrain.ganchos import CAMPOS_POR_MODULO  # noqa: E402

P = CONFIG_DIGIBRAIN_INATOS
S = P.escala
SEMENTES = (101, 202, 303, 404, 505)
BASE = replace(CONFIG_DIGIBRAIN_LIGADA, cheiro_inato=True, intencao_cheiro=True)
LIGADA = replace(BASE, redecidir_evento=True)
DEPOIS = {"visto": True, "d": None, "ha_cheiro": False, "comida_boa_vista": False}
SENS = {"objetos": [], "ha_cheiro": False}
AFETO = {"urgencias": {"fome": 300, "energia": 900}, "g_exp": 0}


def unidade(chave: tuple, a: int, d=None) -> dict:
    return {"chave": chave, "acao": chave[0], "tipo": chave[1], "a": a, "soma": a, "d": d,
            "termos": {"inato": a, "incentivo": 0, "habito": 0, "memoria": 0, "persistencia": 0}}


VAGAR = ("explorar", "vagar", None)
CHAMAR = ("chamar_atencao", None, None)
UNIDADES = [unidade(VAGAR, 1000), unidade(CHAMAR, 800), unidade(("dormir", None, None), 200), unidade(("ocioso", None, None), 0)]


class RngProibida:
    """a rng de politica que falha se for chamada"""

    def random(self):
        raise AssertionError("a rng de politica foi chamada numa decisao segurada")


class RngConta:
    def __init__(self, u: float = 0.0) -> None:
        self.u, self.chamadas = u, 0

    def random(self) -> float:
        self.chamadas += 1
        return self.u


class Cerebro:
    """o M-ESTADO e o M-ARB na ordem do M-ADAPT (a espec, secao 2.3), com sequencias sinteticas"""

    def __init__(self, cd=LIGADA) -> None:
        self.cd = cd
        self.e = EstadoDinamico(CONFIG_PADRAO, cd, P)
        self.arb = Arbitragem(P)
        self.k = 0

    def decidir(self, rng, sens=SENS, afeto=AFETO, reflexo=False, dono=False, unidades=UNIDADES, r_n=0, ocorrido=None,
                depois=DEPOIS) -> tuple[dict, list, list]:
        ligada = self.cd.redecidir_evento
        ev, seg = self.e.eventos(sens, afeto, reflexo, dono) if ligada else ([], None)
        self.e.contexto()
        esc = self.arb.escolher(unidades, afeto, sens, rng, reflexo, seg)
        fins = self.e.escolhida(esc["unidade"], [1, 2, 3], 100, self.k, reflexo)
        if ligada:
            ev = ev + (["E-FIM"] if esc["fora"] else [])
            self.e.registrar_redecisao(esc["unidade"]["chave"], esc["segurada"], reflexo, ev)
        fins = fins + self.e.consequencia(r_n, ocorrido, depois)
        self.k += 1
        return esc, ev, fins


def segurado_uma_vez(**kw) -> Cerebro:
    """a decisao 0 (o sorteio) e a 1 (segurada), para o evento entrar na 2"""
    c = Cerebro()
    c.decidir(RngConta(), **kw)
    esc, ev, _ = c.decidir(RngProibida(), **kw)
    assert esc["segurada"] and ev == []
    return c


# ------------------------------------------------------------------ a subchave
def test_a_subchave_nasce_desligada_e_so_aceita_bool():
    assert CONFIG_DIGIBRAIN.redecidir_evento is False and CONFIG_DIGIBRAIN_LIGADA.redecidir_evento is False
    with pytest.raises(TypeError, match="redecidir_evento"):
        ConfigDigibrain(redecidir_evento=1)


@pytest.mark.parametrize("extra", [{"credito_corrida": True}, {"intencao_suspensa": True}, {"cheiro_inato": False},
                                   {"intencao_cheiro": False}])
def test_a_subchave_recusa_as_combinacoes_nao_previstas(extra):
    with pytest.raises(ValueError, match="redecidir_evento"):
        replace(LIGADA, **extra)


def test_o_teto_e_6_proposto_no_modulo_estado():
    assert P.n_seg_max == 6 == P.n_desiste_cheiro == P.n_suspensa_max
    assert "n_seg_max" in CAMPOS_POR_MODULO["estado"] and PARAMETROS_DIGIBRAIN_INATOS["n_seg_max"][0] == "PROPOSTO"
    assert {f.name for f in fields(ConfigDigibrainInatos)} == {c for cs in CAMPOS_POR_MODULO.values() for c in cs}
    with pytest.raises(ValueError, match="n_seg_max"):
        ConfigDigibrainInatos(n_seg_max=0)


def test_desligada_o_estado_e_o_motivo_nao_tem_campo_novo():
    c = Cerebro(BASE)
    esc, _, _ = c.decidir(RngConta())
    assert "redecidir" not in c.e.estado_interno() and esc["segurada"] is False and esc["fora"] is False
    with pytest.raises(RuntimeError, match="redecidir_evento"):
        c.e.eventos(SENS, AFETO, False, False)
    _, reg = _viver(101, ligada=False)
    m = orq.cerebro_de(reg)
    assert not any("segurada" in x or "evento" in x for x in m.motivos) and "redecidir" not in m.m.estado.estado_interno()


# ------------------------------------------------------------------ T-RD-1
def test_t_rd_1_sem_evento_a_escolha_fica_6_decisoes_sem_a_rng_e_o_teto_devolve_o_sorteio():
    c = Cerebro()
    rng = RngConta()
    esc, ev, _ = c.decidir(rng)
    assert rng.chamadas == 1 and esc["unidade"]["chave"] == VAGAR and ev == [] and not esc["segurada"]   # a 1.a decisao: o sorteio
    for n in range(1, P.n_seg_max + 1):
        esc, ev, _ = c.decidir(RngProibida())
        assert esc["segurada"] and esc["u"] is None and ev == [] and esc["unidade"]["chave"] == VAGAR and c.e.n_seg == n
        assert not any(v for k, v in esc["sondas"].items() if k.endswith("_decidiu"))      # como no reflexo, nenhum modulo decidiu
    rng = RngConta(0.99)                                                                    # o sorteio agora escolhe outra unidade
    esc, ev, _ = c.decidir(rng)
    assert ev == ["E-TETO"] and rng.chamadas == 1 and not esc["segurada"] and esc["unidade"]["chave"] != VAGAR and c.e.n_seg == 0
    assert c.e.tetos == 1 and c.e.seguradas == P.n_seg_max and c.arb.sorteios == 2


def test_t_rd_1_depois_do_teto_a_mesma_unidade_sorteada_pode_ser_segurada_de_novo():
    c = Cerebro()
    c.decidir(RngConta())
    for _ in range(P.n_seg_max):
        c.decidir(RngProibida())
    esc, ev, _ = c.decidir(RngConta(0.0))
    assert ev == ["E-TETO"] and esc["unidade"]["chave"] == VAGAR and not esc["segurada"]
    esc, ev, _ = c.decidir(RngProibida())
    assert esc["segurada"] and c.e.n_seg == 1


# ------------------------------------------------------------------ T-RD-2
def test_t_rd_2_o_reflexo_devolve_o_sorteio_nele_e_na_decisao_seguinte():
    c = segurado_uma_vez()
    esc, ev, _ = c.decidir(RngProibida(), reflexo=True)          # o reflexo nao sorteia: dormir
    assert ev == ["E-REFLEXO"] and esc["unidade"]["acao"] == "dormir" and not esc["segurada"] and c.e.candidato is None
    rng = RngConta()
    esc, ev, _ = c.decidir(rng)                                  # ao acordar, o sorteio de hoje (RE-1)
    assert ev == ["E-REFLEXO"] and rng.chamadas == 1 and not esc["segurada"]
    esc, ev, _ = c.decidir(RngProibida())
    assert esc["segurada"] and ev == []


def test_t_rd_2_a_urgencia_que_muda_de_quarto_devolve_o_sorteio_e_dentro_do_quarto_nao():
    c = segurado_uma_vez()
    esc, ev, _ = c.decidir(RngProibida(), afeto={**AFETO, "urgencias": {"fome": 500, "energia": 900}})   # 300 -> 500: o mesmo quarto
    assert esc["segurada"] and ev == []
    for fome in (S // 2, S // 4 - 1, 3 * S // 4):                # os limites S/2, S/4 e 3S/4
        rng = RngConta()
        esc, ev, _ = c.decidir(rng, afeto={**AFETO, "urgencias": {"fome": fome, "energia": 900}})
        assert ev == ["E-RECEPTOR"] and rng.chamadas == 1 and not esc["segurada"]


@pytest.mark.parametrize("mudanca", ["comida_boa", "cheiro", "dono"])
def test_t_rd_2_o_mundo_devolve_o_sorteio(mudanca):
    c = segurado_uma_vez()
    kw = {"comida_boa": {"sens": {**SENS, "objetos": [{"id": 5, "classe": "racao"}]}},
          "cheiro": {"sens": {**SENS, "ha_cheiro": True}}, "dono": {"dono": True}}[mudanca]
    rng = RngConta()
    esc, ev, _ = c.decidir(rng, **kw)
    assert ev == ["E-MUNDO"] and rng.chamadas == 1 and not esc["segurada"]


def test_t_rd_2_um_objeto_que_nao_e_comida_boa_nao_e_evento_mas_o_alvo_que_sai_e():
    bola = ("brincar", "bola", 9)
    us = [unidade(bola, 1000, d=300), unidade(VAGAR, 500), unidade(("dormir", None, None), 100), unidade(("ocioso", None, None), 0)]
    com_bola = {**SENS, "objetos": [{"id": 9, "classe": "bola"}]}
    perto = {**DEPOIS, "d": 200}                                 # a distancia cai: a I* da bola nao desiste
    c = segurado_uma_vez(sens=com_bola, unidades=us, depois=perto)
    esc, ev, _ = c.decidir(RngProibida(), sens={**SENS, "objetos": [{"id": 9, "classe": "bola"}, {"id": 4, "classe": "podre"}]},
                           unidades=us, depois=perto)
    assert esc["segurada"] and esc["unidade"]["chave"] == bola       # a podre entrou na vista: nao e comida boa
    rng = RngConta()
    esc, ev, _ = c.decidir(rng, sens={**SENS, "objetos": [{"id": 4, "classe": "podre"}]}, unidades=us, depois=perto)
    assert ev == ["E-MUNDO"] and rng.chamadas == 1                   # o alvo da unidade segurada saiu da vista


def test_t_rd_2_o_fim_da_opcao_devolve_o_sorteio_e_o_fim_unica_nao():
    comida = ("comer", "comida", 7)
    us = [unidade(comida, 3000, d=300), unidade(VAGAR, 100), unidade(("dormir", None, None), 100), unidade(("ocioso", None, None), 0)]
    sens = {**SENS, "objetos": [{"id": 7, "classe": "racao"}]}
    c = segurado_uma_vez(sens=sens, unidades=us)                 # a I* comer/comida 7 segurada; nada acabou (o fim `unica` nao conta)
    comeu = {"comeu": {"id": 7}, "brincou_com_bola": False, "chegou": False}
    _, _, fins = c.decidir(RngProibida(), sens=sens, unidades=us, ocorrido=comeu)
    assert [f["motivo"] for f in fins] == ["meta"]
    rng = RngConta()
    esc, ev, _ = c.decidir(rng, sens=sens, unidades=us)
    assert ev == ["E-FIM"] and rng.chamadas == 1 and not esc["segurada"]


def test_t_rd_2_o_candidato_fora_da_lista_ou_com_peso_0_devolve_o_sorteio_com_o_e_fim():
    for sem in ([UNIDADES[1], UNIDADES[2], UNIDADES[3]], [unidade(VAGAR, 0)] + UNIDADES[1:]):   # fora da lista; com a = 0 (RE-2)
        c = segurado_uma_vez()
        rng = RngConta()
        esc, ev, _ = c.decidir(rng, unidades=sem)
        assert ev == ["E-FIM"] and esc["fora"] and rng.chamadas == 1 and esc["unidade"]["chave"] == CHAMAR


def test_os_eventos_sao_os_da_rd_3_e_rd_4_e_a_escolha_segurada_com_o_reflexo_falha_alto():
    assert EVENTOS == ("E-REFLEXO", "E-RECEPTOR", "E-MUNDO", "E-FIM", "E-TETO")
    with pytest.raises(RuntimeError, match="reflexo"):
        Arbitragem(P).escolher(UNIDADES, AFETO, SENS, RngProibida(), True, VAGAR)
    c = segurado_uma_vez()
    with pytest.raises(RuntimeError, match="segurada"):
        c.e.registrar_redecisao(CHAMAR, True, False, [])


# ------------------------------------------------------------------ T-RD-3
BUSCA_M = {"reflexo": False, "escolha": ["comer", "cheiro", None]}
SONO_M = {"reflexo": True, "escolha": ["dormir", None, None]}


def test_t_rd_3_a_busca_o_reflexo_o_reflexo_e_a_mesma_busca_dao_zero_trocas_nos_dois_bracos():
    seq = [BUSCA_M, SONO_M, SONO_M, BUSCA_M]
    assert orq.trocas_por_decisao(seq) == 0                                    # o braco de hoje (sem os campos da C3)
    com_c3 = [{**m, "segurada": False, "evento": ["E-REFLEXO"] if i else []} for i, m in enumerate(seq)]
    assert orq.trocas_por_decisao(com_c3) == 0                                 # o braco R
    explorar = {"reflexo": False, "escolha": ["explorar", "vagar", None]}
    assert orq.trocas_por_decisao([BUSCA_M, SONO_M, explorar, explorar, BUSCA_M]) == 2


def test_t_rd_3_nas_vidas_a_contagem_le_so_as_decisoes_sem_o_reflexo():
    for ligada in (False, True):
        ms = orq.cerebro_de(_viver(101, ligada=ligada)[1]).motivos
        livres = [m["escolha"] for m in ms if not m["reflexo"]]
        assert orq.trocas_por_decisao(ms) == sum(a != b for a, b in zip(livres, livres[1:]))


# ------------------------------------------------------------------ T-RD-4
def test_t_rd_4_a_i_segurada_sobe_o_c_e_o_n_como_a_mesma_escolha_sorteada():
    comida = ("comer", "comida", 7)
    us = [unidade(comida, 3000, d=300), unidade(VAGAR, 100), unidade(("dormir", None, None), 100), unidade(("ocioso", None, None), 0)]
    sens = {**SENS, "objetos": [{"id": 7, "classe": "racao"}]}
    com, sem = Cerebro(LIGADA), Cerebro(BASE)
    comeu = {"comeu": {"id": 7}, "brincou_com_bola": False, "chegou": False}
    for k in range(4):
        oc = comeu if k == 3 else None
        a, ev, fins_a = com.decidir(RngConta() if k == 0 else RngProibida(), sens=sens, unidades=us, r_n=10 * k, ocorrido=oc,
                                    depois={**DEPOIS, "d": 300 - 10 * k})
        b, _, fins_b = sem.decidir(RngConta(), sens=sens, unidades=us, r_n=10 * k, ocorrido=oc, depois={**DEPOIS, "d": 300 - 10 * k})
        assert a["unidade"]["chave"] == b["unidade"]["chave"] == comida and a["segurada"] == (k > 0)
        ea, eb = com.e.estado_interno(), sem.e.estado_interno()
        assert ea.pop("redecidir") is not None and ea == eb               # o C, o n, o F, os fins: os de sem a subchave
        assert fins_a == fins_b                                           # a opcao entregue ao P2 (o credito) e a mesma
    assert fins_a[0]["motivo"] == "meta" and fins_a[0]["n"] == 4 and fins_a[0]["r"] == 60 and fins_a[0]["e"] == [1, 2, 3]


# ------------------------------------------------------------------ as vidas: G1, G2-SEPARADO e o conferir_redecidir
def _viver(semente: int, braco: str = "M3", lugar: str = "longe_fixo", dono: str = "relapso", ligada: bool = True):
    original = orq.config_do_braco
    orq.config_do_braco = lambda b, g=None, c=False: replace(original(b, g, c), redecidir_evento=ligada)
    try:
        motor, reg, fab = orq.viver(braco, dono, lugar, semente, 3, 16, conserto=True)
    finally:
        orq.config_do_braco = original
    _viver.fab = (motor, fab)
    return motor, reg


@pytest.mark.parametrize("braco", ["M3", "M2"])
@pytest.mark.parametrize("semente", SEMENTES)
def test_g1_o_replay_com_a_subchave_ligada_nas_cinco_sementes(semente, braco):
    motor, reg = _viver(semente, braco)
    orq.conferir_replay(motor, _viver.fab[1], semente, motor.log.para_jsonl())
    orq.conferir_mecanismo(braco, reg, None)                     # o credito, os fins e o conferir_redecidir
    orq.conferir_cenario(motor, reg)
    c = orq.cerebro_de(reg)
    assert c.cd.redecidir_evento and all("segurada" in m and "evento" in m for m in c.motivos)
    assert 0 < c.m.estado.seguradas < len(c.motivos)
    # a rng de politica: um sorteio por decisao com u, nenhum nas seguradas
    assert c.m.arb.sorteios == sum(m["u"] is not None for m in c.motivos)
    assert not any(m["segurada"] and m["u"] is not None for m in c.motivos)


def test_g1_o_replay_no_comedouro_com_os_donos():
    for braco, dono in (("M3", "atencioso"), ("M2", "aleatorio")):
        motor, reg = _viver(202, braco, "comedouro", dono)
        orq.conferir_replay(motor, _viver.fab[1], 202, motor.log.para_jsonl())
        orq.conferir_mecanismo(braco, reg, None)


def test_g2_separado_ligada_muda_so_a_vida_do_braco_que_a_liga():
    desligada = orq.viver("M3", "relapso", "longe_fixo", 101, 3, 16, conserto=True)
    ligada = _viver(101)
    estado = lambda v: json.dumps(orq.cerebro_de(v[1]).estado_interno(), sort_keys=True)   # noqa: E731
    assert estado(desligada) != estado(ligada)
    # viver o braco ligado nao muda a vida desligada de depois (ela segue o gabarito)
    assert estado(desligada) == estado(orq.viver("M3", "relapso", "longe_fixo", 101, 3, 16, conserto=True))
    # o M2 sem a chave nao muda por o M3 a ter ligado
    m2 = orq.viver("M2", "relapso", "longe_fixo", 101, 3, 16, conserto=True)
    assert orq.cerebro_de(m2[1]).cd.redecidir_evento is False and "redecidir" not in orq.cerebro_de(m2[1]).m.estado.estado_interno()


def test_g2_separado_nada_fora_do_pacote_e_do_orquestrador_le_a_chave():
    donos_da_chave = {"digilab/config.py", "digilab/digibrain/adapt.py", "digilab/digibrain/arb.py", "digilab/digibrain/estado.py",
                      "experiments/run_v2_digibrain_prototipo.py",
                      "experiments/run_v2_redecidir_evento.py", "experiments/adendo8_poder_redecidir_evento.py",   # a run e o poder da C3 (adendo 8)
                      "experiments/adendo9_poder_memoria_autobio.py"}   # o poder da C4 (adendo 9): so le o artefato da run da C3, pelo caminho
    achados = set()
    for pasta in ("digilab", "experiments", "web", "tools", "servidor"):
        if not (RAIZ / pasta).exists():
            continue
        for f in (RAIZ / pasta).rglob("*"):
            if f.suffix in (".py", ".ts", ".tsx", ".js") and "node_modules" not in f.parts and "redecidir_evento" in f.read_text(
                    encoding="utf-8", errors="ignore"):
                achados.add(f.relative_to(RAIZ).as_posix())
    assert achados == donos_da_chave


def test_o_conferir_redecidir_aceita_a_vida_e_falha_alto():
    _, reg = _viver(303)
    c = orq.cerebro_de(reg)
    orq.conferir_redecidir("M3R", c)
    i = next(i for i, m in enumerate(c.motivos) if m["segurada"])
    m = c.motivos[i]
    for campo, valor, msg in (("evento", ["E-MUNDO"], "segurada"), ("escolha", ["nenhuma", None, None], "segurada"),
                              ("u", 0.5, "segurada")):
        antigo = m[campo]
        m[campo] = valor
        try:
            with pytest.raises(RuntimeError, match=msg):
                orq.conferir_redecidir("M3R", c)
        finally:
            m[campo] = antigo
    j = next(j for j, x in enumerate(c.motivos) if j > 0 and not x["segurada"])
    antigo = c.motivos[j]["evento"]
    c.motivos[j]["evento"] = []
    try:
        with pytest.raises(RuntimeError, match="nao tem evento"):
            orq.conferir_redecidir("M3R", c)
    finally:
        c.motivos[j]["evento"] = antigo
    c.m.estado.seguradas += 1
    try:
        with pytest.raises(RuntimeError, match="contagens"):
            orq.conferir_redecidir("M3R", c)
    finally:
        c.m.estado.seguradas -= 1
    orq.conferir_redecidir("M3R", c)


def test_o_conferir_redecidir_pega_mais_seguradas_seguidas_que_o_teto():
    _, reg = _viver(404)
    c = orq.cerebro_de(reg)
    falsas = [{**c.motivos[0], "k": k, "reflexo": False, "segurada": k > 0, "evento": [], "u": None} for k in range(P.n_seg_max + 2)]
    c.motivos[:] = falsas
    with pytest.raises(RuntimeError, match="o teto e"):
        orq.conferir_redecidir("M3R", c)


# ------------------------------------------------------------------ G-MECANISMO, G-INT, G-SEM-DIRECAO, G-RECEPTOR
_DE_HOJE = [n for n, f in inspect.getmembers(tm, inspect.isfunction) if n.startswith("test_")]


@pytest.mark.parametrize("nome", _DE_HOJE)
def test_g_mecanismo_os_de_hoje_com_a_subchave_ligada(nome, monkeypatch):
    """cada teste de mecanismo de hoje (tests/test_digibrain_mecanismo.py) com as duas subchaves do cheiro e a `redecidir_evento`"""
    monkeypatch.setattr(tm, "CONFIG_DIGIBRAIN_LIGADA", LIGADA)
    getattr(tm, nome)()


def test_g_sem_direcao_os_eventos_nao_leem_a_direcao_nem_a_distancia_do_cheiro():
    fonte = inspect.getsource(EstadoDinamico.eventos) + inspect.getsource(EstadoDinamico.registrar_redecisao)
    assert "direcao" not in fonte and '"d"' not in fonte and "random" not in fonte
    assert "rng" not in inspect.signature(EstadoDinamico.eventos).parameters
    json.dumps(Cerebro().e.estado_interno())


def test_g_int_e_g_receptor_as_intencoes_e_os_receptores_de_hoje_na_vida_ligada():
    """as intencoes abrem e acabam pelos fins de hoje (o G-INT) e todo receptor do prototipo tem urgencia no registro (o G-RECEPTOR)"""
    c = orq.cerebro_de(_viver(505)[1])
    fins = c.m.estado.fins
    assert set(fins) == set(orq.fins_do_estado("M3")) and fins["meta"] > 0
    assert all(set(m["afeto"]["urgencias"]) == set(c.m.sens.receptores) for m in c.motivos)
