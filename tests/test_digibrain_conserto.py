"""Os testes do conserto do DigiBrain modular (docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md, adendo 3, A3.7; APROVADO pelo
Matheus em 2026-10-26), antes de qualquer vida das faixas 65xxx e 66xxx. So as sementes dos testes e sequencias sinteticas.

  - G2: com as duas subchaves desligadas, as vidas do modular de hoje saem byte a byte (tests/test_gabarito_digibrain_modular.py, contra o
    gabarito gravado antes das subchaves; as 196 vidas e as do MVP seguem em tests/test_gabarito_digibrain.py e
    tests/test_gabarito_mvp_produto_web.py); aqui, o M3-420 das fases do conserto e o M3 do prototipo, byte a byte;
  - G2-SEPARADO: cada subchave sozinha muda so os bracos que a ligam, e nada fora do pacote e do orquestrador le a chave;
  - G1: o replay com as subchaves ligadas, em cada braco do conserto;
  - G-MECANISMO, G-SEM-DIRECAO, G-INT, G-RECEPTOR: os testes de mecanismo de hoje com as duas ligadas; a DX-4 sem a distancia nem a
    direcao do cheiro, pela AST;
  - T-CADEIA-1 com as duas ligadas; T-ALCANCE-1; T-JANELA-IGUAL; T-VISITA-1; T-EPISODIO-1 a 5; T-CENARIO-1; T-CHEIRO-1;
    T-PERS-CHEIRO-1 a 3; T-HABITO-1;
  - o sha256 dos artefatos do #420 (`avaliacao/medidas.json` e `avaliacao/resultado.json`) sem mudar."""
from __future__ import annotations

import ast
import hashlib
import inspect
import json
import sys
import textwrap
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import bancada_v2 as bv  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402
import test_digibrain_mecanismo as tm  # noqa: E402

from digilab.config import CARACTERISTICAS_DIGIBRAIN, CONFIG_DIGIBRAIN_INATOS, CONFIG_DIGIBRAIN_LIGADA, CONFIG_PADRAO  # noqa: E402
from digilab.digibrain import DigiBrain  # noqa: E402
from digilab.digibrain import adapt, estado  # noqa: E402
from digilab.digibrain._comum import chave_unidade, mul  # noqa: E402
from digilab.digibrain.estado import EstadoDinamico  # noqa: E402
from digilab.digibrain.plast import Plasticidade  # noqa: E402
from digilab.events import AcaoPet  # noqa: E402
from digilab.metrics import (ACOES_R_POSSIVEL, cadeia_comida_corpo, episodios_de_fome, janela_w, n_min_decisoes,  # noqa: E402
                             repeticao_apos_alivio, visitas_vazias, visitas_vazias_v1)
from digilab.mundo import Alvo  # noqa: E402

P = CONFIG_DIGIBRAIN_INATOS
S = P.escala
LIGADAS = replace(CONFIG_DIGIBRAIN_LIGADA, cheiro_inato=True, intencao_cheiro=True)
CONFIGS = RAIZ / "experiments" / "configs" / "v2_digibrain_prototipo"
SHA_420 = {"avaliacao/medidas.json": "76e1d6cda42dda93cf6fad9be9766d0ef686a54c05bff751b2cc6b1ac33db7ba",
           "avaliacao/resultado.json": "4045961acbd73a019c6646eff73caaece74e481dba4f2b664312c240d3d4413a"}
W8, RAIO, PASSO = 8, 16, 60


def _cfg(nome: str) -> dict:
    return json.loads((CONFIGS / nome).read_text(encoding="utf-8"))


# ================================================================== o #420 e a config
def test_os_artefatos_do_420_nao_mudam():
    for nome, sha in SHA_420.items():
        assert hashlib.sha256((RAIZ / "artifacts_v2_digibrain_prototipo" / nome).read_bytes()).hexdigest() == sha, nome


def test_as_subchaves_desligadas_por_padrao_e_os_valores_propostos():
    c = CONFIG_DIGIBRAIN_LIGADA
    assert (c.cheiro_inato, c.intencao_cheiro) == (False, False)
    for nome in ("cheiro_inato", "intencao_cheiro"):
        with pytest.raises(TypeError):
            replace(c, **{nome: 1})
    assert (P.w0_tipo_cheiro, P.n_desiste_cheiro) == (S // 4, 6)
    assert P.n_desiste_cheiro == -(-(24 * 16 - 6 * 16) // 60) + 1                  # a regra da PE-6 (A3.4)
    assert "cheiro" not in dict(dict(P.w0_tipo)["comer"])                            # desligada, o W0_tipo de hoje


def test_as_fases_do_conserto_seguem_o_adendo():
    assert orq.SUBCHAVES_CONSERTO["M3"] == {"cheiro_inato": True, "intencao_cheiro": True}
    assert all(orq.SUBCHAVES_CONSERTO[b] == {**orq.SUBCHAVES[b], "cheiro_inato": True, "intencao_cheiro": True} for b in orq.SUBCHAVES)
    assert {b: orq.SUBCHAVES_CONSERTO[b] for b in ("M3-sem-inato", "M3-sem-intencao", "M3-420")} == {
        "M3-sem-inato": {"intencao_cheiro": True}, "M3-sem-intencao": {"cheiro_inato": True}, "M3-420": {}}
    assert len(orq.BRACOS_CONSERTO) == 12 and orq.BRACOS_DA_FASE["piloto_conserto"] == orq.BRACOS_CONSERTO
    assert orq.BRACOS_DA_FASE["calibracao_conserto"] == ("M3",)
    assert orq.BASES["calibracao_conserto"] == (65101, 65202) and orq.BASES["piloto_conserto"] == (65303, 65404, 65505)
    assert orq.BASES["reavaliacao"] == (66101, 66202, 66303, 66404, 66505)
    assert orq.modo_da_config(_cfg("calibracao_conserto.json")) == "calibracao_conserto"
    assert orq.modo_da_config(_cfg("piloto_conserto.json")) == "piloto_conserto"
    for nome in ("fumaca_calibracao_conserto.json", "fumaca_piloto_conserto.json", "fumaca_reavaliacao.json"):
        assert orq.modo_da_config(_cfg(nome)) == "fumaca"
    with pytest.raises(ValueError, match="g_mvp_ep"):
        orq.modo_da_config({**_cfg("piloto_conserto.json"), "g_mvp_ep": {**orq.G_MVP_EP, "limiar": 0.7}})
    with pytest.raises(ValueError, match="faltam"):
        orq.modo_da_config({k: v for k, v in _cfg("piloto_conserto.json").items() if k != "g_elegivel_ep"})
    with pytest.raises(bv.SementeSemPlano):
        orq.modo_da_config({**_cfg("piloto_conserto.json"), "unidades": {"bases": [64101, 64202, 64303], "k": 2, "prefixo": orq.PREFIXO}})
    with pytest.raises(bv.SementeSemPlano):
        orq.modo_da_config({**_cfg("calibracao_conserto.json"), "unidades": {"bases": [65303, 65404], "k": 2, "prefixo": orq.PREFIXO}})
    if not (RAIZ / orq.SAIDA["piloto_conserto"] / "resultado.json").exists():   # a reavaliacao espera o piloto e o adendo 4
        cfg = {**{k: v for k, v in _cfg("piloto_conserto.json").items()}, "fase": "reavaliacao",
               "unidades": {"bases": list(orq.BASES["reavaliacao"]), "k": 4, "prefixo": orq.PREFIXO}}
        with pytest.raises(FileNotFoundError):
            orq.modo_da_config(cfg)


def test_os_inatos_da_calibracao_do_conserto_so_nos_campos_e_faixas_de_a3_8(tmp_path):
    """o campo "inatos" da config (A3.11): sem ele, os de hoje; com ele, so na calibracao do conserto e so nas faixas de A3.8; a vida usa
    os valores, o replay do disco os refaz (G1) e o meta da run os grava"""
    cal = {k: v for k, v in _cfg("calibracao_conserto.json").items() if k != "inatos"}      # a config de cada rodada pode trazer o campo
    assert orq.inatos_da_config(cal) is CONFIG_DIGIBRAIN_INATOS and orq.inatos_da_config({**cal, "inatos": {}}) is CONFIG_DIGIBRAIN_INATOS
    novo = orq.inatos_da_config({**cal, "inatos": {"w_pers": 4 * S, "eta_h": S // 256, "w0_tipo_cheiro": S // 8}})
    assert (novo.w_pers, novo.eta_h, novo.w0_tipo_cheiro) == (4 * S, S // 256, S // 8) and novo.tau_c == P.tau_c
    assert orq.modo_da_config({**cal, "inatos": {"n_desiste_cheiro": 8}}) == "calibracao_conserto"
    for ruim, msg in (({"w0_tipo_cheiro": S // 16}, "faixa"), ({"w0_tipo_cheiro": S}, "faixa"), ({"n_desiste_cheiro": 4}, "faixa"),
                      ({"n_desiste_cheiro": 9}, "faixa"), ({"tau_c": 14}, "faixa"), ({"w_pers": 0}, "faixa"), ({"eta_h": 8.0}, "faixa"),
                      ({"n_desiste": 4}, "so muda"), ({"c_g": 2 * S}, "so muda"), ({"w0": ()}, "so muda")):
        with pytest.raises(ValueError, match=msg):
            orq.modo_da_config({**cal, "inatos": ruim})
    for nome in ("piloto_conserto.json", "fumaca_piloto_conserto.json"):
        with pytest.raises(ValueError, match="so da calibracao do conserto"):
            orq.modo_da_config({**_cfg(nome), "inatos": {"w_pers": 4 * S}})
    # os valores de antes do congelamento da rodada 3 do #427 (2S e S/128), diferentes dos de hoje
    fum = {**_cfg("fumaca_calibracao_conserto.json"), "dias": 1, "inatos": {"w_pers": 2 * S, "eta_h": S // 128}}
    assert (P.w_pers, P.eta_h) != (2 * S, S // 128)
    assert orq.modo_da_config(fum) == "fumaca"
    run = orq.rodar(fum, tmp_path / "r", 1)
    assert run["meta"]["inatos"]["w_pers"] == 2 * S and run["meta"]["inatos"]["eta_h"] == S // 128
    hoje = orq.rodar({**fum, "inatos": {}}, tmp_path / "h", 1)
    assert run["registros"] and [r["vida"] for r in run["registros"]] == [r["vida"] for r in hoje["registros"]]
    assert any(a != b for a, b in zip(run["registros"], hoje["registros"]))       # os valores chegam a vida


# ================================================================== G2, G2-SEPARADO e G1
def test_g2_separado_cada_subchave_muda_so_os_bracos_que_a_ligam():
    """o M3-420 do conserto e o M3 do prototipo byte a byte (as duas desligadas); cada subchave sozinha muda a vida; o A11 nao muda"""
    vidas = {}
    for braco, conserto in (("M3", False), ("M3-420", True), ("M3-sem-inato", True), ("M3-sem-intencao", True), ("M3", True)):
        motor, reg, _ = orq.viver(braco, "relapso", "longe", 101, 3, 16, conserto=conserto)
        vidas[(braco, conserto)] = (motor.log.para_jsonl(), json.dumps(orq.cerebro_de(reg).estado_interno(), sort_keys=True))
    assert vidas[("M3-420", True)] == vidas[("M3", False)]
    for b in ("M3-sem-inato", "M3-sem-intencao", "M3"):
        assert vidas[(b, True)][1] != vidas[("M3-420", True)][1], b
    a_hoje = orq.viver("A11", "relapso", "longe", 101, 2, 16)[0].log.para_jsonl()
    assert orq.viver("A11", "relapso", "longe", 101, 2, 16, conserto=True)[0].log.para_jsonl() == a_hoje
    # a DX-3 sozinha nao abre intencao no cheiro; a DX-4 sozinha nao muda o inato do cheiro
    _, reg, _ = orq.viver("M3-sem-intencao", "relapso", "longe", 101, 3, 16, conserto=True)
    assert not any(f["chave"][:2] == ["comer", "cheiro"] for m in orq.cerebro_de(reg).motivos for f in m["fins"])
    _, reg, _ = orq.viver("M3-sem-inato", "relapso", "longe", 101, 3, 16, conserto=True)
    assert any(f["chave"][:2] == ["comer", "cheiro"] for m in orq.cerebro_de(reg).motivos for f in m["fins"])
    assert orq.cerebro_de(reg).m.impulso.w0_tipo["comer"].get("cheiro") is None


@pytest.mark.parametrize("braco", ["M0", "M3", "M3-sp", "M4", "M3-sem-inato", "M3-sem-intencao", "M3-420"])
def test_g1_o_replay_com_as_subchaves_ligadas(braco):
    motor, reg, fab = orq.viver(braco, "atencioso", "longe", 202, 3, 16, conserto=True)
    orq.conferir_replay(motor, fab, 202, motor.log.para_jsonl())
    orq.conferir_mecanismo(braco, reg, None)
    orq.conferir_cenario(motor, reg)


def test_g1_o_m4_emb_e_o_m4_con_do_conserto():
    _, reg, _ = orq.viver("M4", "relapso", "longe", 202, 2, 16, conserto=True)
    serie = tuple(orq.cerebro_de(reg).m.afeto.serie_e)
    for braco, kw in (("M4-emb", {"serie_e": serie}), ("M4-con", {"g_apr_con": 1300})):
        motor, reg, fab = orq.viver(braco, "relapso", "longe", 101, 2, 16, conserto=True, **kw)
        orq.conferir_replay(motor, fab, 101, motor.log.para_jsonl())
        orq.conferir_mecanismo(braco, reg, kw.get("serie_e"))
        assert orq.cerebro_de(reg).cd.cheiro_inato and orq.cerebro_de(reg).cd.intencao_cheiro


# ================================================================== G-MECANISMO, G-SEM-DIRECAO
_COM_A_CHAVE_NOS_TESTES = [n for n, f in inspect.getmembers(tm, inspect.isfunction) if n.startswith("test_")]


@pytest.mark.parametrize("nome", _COM_A_CHAVE_NOS_TESTES)
def test_g_mecanismo_os_de_hoje_com_as_duas_ligadas(nome, monkeypatch):
    """cada teste de mecanismo de hoje (tests/test_digibrain_mecanismo.py) com a CONFIG_DIGIBRAIN_LIGADA das duas subchaves"""
    monkeypatch.setattr(tm, "CONFIG_DIGIBRAIN_LIGADA", LIGADAS)
    getattr(tm, nome)()


def _funcao(modulo, nome: str) -> ast.FunctionDef:
    arvore = ast.parse(textwrap.dedent(inspect.getsource(getattr(modulo, nome) if hasattr(modulo, nome)
                                                         else getattr(modulo.EstadoDinamico, nome))))
    return arvore.body[0]


def test_g_sem_direcao_a_dx4_nao_le_a_distancia_nem_a_direcao_do_cheiro():
    """pela AST: o fim da busca le so o consumo, as comidas boas a vista, se ha cheiro e as contagens da opcao; a composta so herda a
    opcao guardada e le a distancia da comida vista (a da unidade `comer/comida`, como as intencoes de hoje), nunca a do cheiro"""
    busca = _funcao(estado, "_consequencia_busca")
    chaves = {no.slice.value for no in ast.walk(busca) if isinstance(no, ast.Subscript) and isinstance(no.slice, ast.Constant)}
    assert chaves == {"comeu", "comida_boa_vista", "ha_cheiro", "n_sp", "n"}
    nomes = {no.id for no in ast.walk(busca) if isinstance(no, ast.Name)} | {no.attr for no in ast.walk(busca) if isinstance(no, ast.Attribute)}
    assert not {x for x in nomes if "direcao" in x or "dist" in x or "cheiro" in x and x != "n_desiste_cheiro"}
    herdar = _funcao(estado, "_herdar_busca")
    leituras_d = [no for no in ast.walk(herdar) if isinstance(no, ast.Subscript) and isinstance(no.slice, ast.Constant) and no.slice.value == "d"]
    assert len(leituras_d) == 1 and leituras_d[0].value.id == "unidade"
    # o M-ADAPT entrega ao M-ESTADO so a presenca: se ha cheiro (direcao_cheiro != 0, a leitura de hoje) e o tipo dos `vistos`
    fechar = ast.unparse(_funcao(adapt.DigiBrain, "_fechar"))
    assert "classe_do_tipo(v[1]) in COMIDAS_BOAS for v in pm1.vistos" in fechar and fechar.count("direcao_cheiro") == 1


# ================================================================== T-CHEIRO-1 (DX-3)
def test_t_cheiro_1_o_inato_do_cheiro_so_com_a_subchave():
    o = tm.obs(corpo=tm.pc(fome=600), direcao=3)
    hoje, *_ = tm.unidades_de(tm.cerebro(), o)
    dx3, *_ = tm.unidades_de(tm.cerebro(cheiro_inato=True), o)
    cheiro = chave_unidade("comer", "cheiro")
    assert dx3[cheiro]["termos"]["inato"] == hoje[cheiro]["termos"]["inato"] + P.w0_tipo_cheiro
    assert all(dx3[k]["termos"] == hoje[k]["termos"] for k in hoje if k != cheiro)
    assert dx3[chave_unidade("explorar", "cheiro")]["termos"] == hoje[chave_unidade("explorar", "cheiro")]["termos"]
    so4, *_ = tm.unidades_de(tm.cerebro(intencao_cheiro=True), o)
    assert so4 == hoje                                                              # a DX-4 sozinha nao muda o inato
    with pytest.raises(ValueError, match="w0_tipo_cheiro"):
        DigiBrain(CONFIG_PADRAO, CONFIG_DIGIBRAIN_LIGADA, tm.CM,
                  inatos=replace(P, w0_tipo=(("comer", dict(P.w0_tipo)["comer"] + (("cheiro", 1),)),)))


# ================================================================== T-PERS-CHEIRO-1 a 3 (DX-4)
Z0 = [S] + [0] * (len(CARACTERISTICAS_DIGIBRAIN) - 1)
Z1 = [S // 2] * len(CARACTERISTICAS_DIGIBRAIN)
NADA = {"comeu": None, "brincou_com_bola": False, "chegou": False}
BUSCA = chave_unidade("comer", "cheiro")


def _depois(cheiro=True, comida=False, visto=True, d=None):
    return {"visto": visto, "d": d, "ha_cheiro": cheiro, "comida_boa_vista": comida}


def _est(**kw):
    return EstadoDinamico(CONFIG_PADRAO, replace(CONFIG_DIGIBRAIN_LIGADA, intencao_cheiro=True, **kw))


def test_t_pers_cheiro_1_a_busca_abre_e_acaba():
    est = _est()
    est.contexto()
    assert est.escolhida(tm._unidade(BUSCA), Z0, S, 0) == [] and est.I["chave"] == BUSCA
    assert est.consequencia(-10, NADA, _depois()) == []
    assert est.contexto()["persistencia"] == {BUSCA: mul(P.w_pers, est.I["C"], S)}            # a persistencia, como as outras
    # "meta": come numa decisao da busca
    est.escolhida(tm._unidade(BUSCA), Z0, S, 1)
    f0 = est.F
    fins = est.consequencia(300, {**NADA, "comeu": {"id": 9}}, _depois())
    assert [(f["motivo"], f["meta"], f["r"]) for f in fins] == [("meta", True, 290)] and est.F == f0 and est.I is None
    # "achou": comida boa a vista depois de andar (guardada: sem credito agora); o F nao sobe (decisao do Matheus de 2026-10-26)
    est.F = S // 4                                                                             # um F nao nulo, para ver que nao muda
    est.contexto()
    est.escolhida(tm._unidade(BUSCA), Z0, S, 2)
    f0 = est.F
    fins = est.consequencia(-5, NADA, _depois(comida=True))
    assert [(f["motivo"], f["credito"], f["meta"]) for f in fins] == [("achou", False, False)] and est.guardada is not None and est.I is None
    assert est.F == f0
    est.contexto()
    est.escolhida(tm._unidade(chave_unidade("dormir")), Z0, S, 3)
    est.consequencia(0, None, _depois())
    # "sumiu": sem cheiro e sem comida boa a vista
    est.contexto()
    est.escolhida(tm._unidade(BUSCA), Z0, S, 4)
    f0 = est.F
    assert [f["motivo"] for f in est.consequencia(-5, NADA, _depois(cheiro=False))] == ["sumiu"]
    assert est.F == f0 + mul(est.k_f_sobe, S - f0, S) > f0                                    # o "sumiu" continua subindo o F
    # "desistiu": N_desiste_cheiro decisoes sem meta nem achou
    fins = []
    for i in range(P.n_desiste_cheiro):
        est.contexto()
        est.escolhida(tm._unidade(BUSCA), Z0, S, 5 + i)
        assert not fins
        f0 = est.F
        fins = est.consequencia(-1, NADA, _depois())
    assert [(f["motivo"], f["n"]) for f in fins] == [("desistiu", P.n_desiste_cheiro)]
    assert est.F == f0 + mul(est.k_f_sobe, S - f0, S) > f0                                    # o "desistiu" continua subindo o F
    assert est.estado_interno()["fins"] == {"meta": 1, "trocou": 0, "sumiu": 1, "desistiu": 1, "achou": 1}
    # sem a subchave, a busca e uma opcao de uma decisao, como hoje
    hoje = EstadoDinamico(CONFIG_PADRAO, CONFIG_DIGIBRAIN_LIGADA)
    hoje.contexto()
    hoje.escolhida(tm._unidade(BUSCA), Z0, S, 0)
    assert hoje.I is None and [f["motivo"] for f in hoje.consequencia(-1, NADA, _depois(comida=True))] == ["unica"]
    assert "achou" not in hoje.estado_interno()["fins"] and "guardada" not in hoje.estado_interno()


def _plast():
    pl = Plasticidade(CONFIG_DIGIBRAIN_LIGADA)
    pl.montar(tm.HOJE + tm.NOVOS)
    return pl


def test_t_pers_cheiro_2_a_busca_que_come_e_uma_opcao_so():
    """busca, "achou", `comer/comida` na decisao seguinte, consumo: o P2 recebe UMA opcao, com o z do comeco da busca e o r = a soma das
    consequencias da busca, da ida e da refeicao"""
    est, pl = _est(), _plast()
    comida = chave_unidade("comer", "comida", 7)
    entregues = []
    est.contexto()
    entregues += est.escolhida(tm._unidade(BUSCA), Z0, S, 0)
    entregues += est.consequencia(-20, NADA, _depois())
    est.contexto()
    entregues += est.escolhida(tm._unidade(BUSCA), Z1, S, 1)
    entregues += est.consequencia(-15, NADA, _depois(comida=True))                         # achou
    est.contexto()
    entregues += est.escolhida(tm._unidade(comida, 80), Z1, S, 2)                          # herda a busca
    assert est.I["composta"] and est.I["inicio"] == 0 and est.I["e"] == Z0 and est.I["r"] == -35
    entregues += est.consequencia(-10, NADA, _depois(d=30))                                 # a ida
    est.contexto()
    entregues += est.escolhida(tm._unidade(comida, 30), Z1, S, 3)
    entregues += est.consequencia(400, {**NADA, "comeu": {"id": 7}}, _depois(visto=False))  # a refeicao
    creditadas = [f for f in entregues if f.get("credito", True) and f["motivo"] != "unica"]
    assert [(f["motivo"], f["chave"], f["inicio"], f["n"], f["r"], f["e"], f.get("composta")) for f in creditadas] == \
        [("meta", comida, 0, 4, -35 - 10 + 400, Z0, True)]
    registros = adapt._creditar(pl, entregues)
    assert len(registros) == 1 and registros[0]["b"] == "comer" and registros[0]["r_n"] == 355 and pl.creditos == 1
    assert [f["motivo"] for f in entregues] == ["achou", "meta"]                           # a refeicao aparece uma vez


def test_t_pers_cheiro_3_a_busca_que_nao_come():
    """a busca que desiste ou some, e a busca "achou" seguida de outra unidade ou de um `comer/comida` que acaba sem comer: o r entregue e
    so a soma das consequencias das proprias decisoes"""
    comida = chave_unidade("comer", "comida", 7)
    for fim, depois in (("desistiu", _depois()), ("sumiu", _depois(cheiro=False))):
        est, entregues = _est(), []
        for i in range(P.n_desiste_cheiro):
            est.contexto()
            entregues += est.escolhida(tm._unidade(BUSCA), Z0, S, i)
            entregues += est.consequencia(-3, NADA, depois)
            if entregues:
                break
        assert [(f["motivo"], f["r"]) for f in entregues] == [(fim, -3 * entregues[0]["n"])]
    # "achou" e depois outra unidade: a busca e entregue nessa decisao, so com o r dela (registrada no achou, nao de novo)
    est, pl = _est(), _plast()
    est.contexto()
    e1 = est.escolhida(tm._unidade(BUSCA), Z0, S, 0) + est.consequencia(-7, NADA, _depois(comida=True))
    est.contexto()
    e2 = est.escolhida(tm._unidade(chave_unidade("dormir")), Z1, S, 1)
    assert [(f["motivo"], f.get("credito", True), f.get("registro", True)) for f in e1] == [("achou", False, True)]
    assert [(f["motivo"], f["r"], f["e"], f.get("registro", True)) for f in e2] == [("achou", -7, Z0, False)]
    assert len(adapt._creditar(pl, e1)) == 0 and len(adapt._creditar(pl, e2)) == 1 and not adapt._registrados(e2)
    # "achou" e depois o `comer/comida` que acaba sem comer (trocou): a composta, so com o r das decisoes dela
    est = _est()
    est.contexto()
    est.escolhida(tm._unidade(BUSCA), Z0, S, 0)
    est.consequencia(-7, NADA, _depois(comida=True))
    est.contexto()
    est.escolhida(tm._unidade(comida, 80), Z1, S, 1)
    est.consequencia(-4, NADA, _depois(d=40))
    est.contexto()
    fins = est.escolhida(tm._unidade(chave_unidade("ocioso")), Z1, S, 2)
    assert [(f["motivo"], f["r"], f["n"], f["e"], f.get("composta")) for f in fins] == [("trocou", -11, 2, Z0, True)]


def test_t_pers_cheiro_3_nas_vidas_a_busca_sem_refeicao_nao_e_positiva():
    """nas vidas de teste com a DX-4: toda opcao entregue com decisoes da busca e sem consumo tem r <= 0 (o andar custa energia e o comer
    sem comida nao da fome, MF-2); a composta que come tem a refeicao uma vez (o `conferir_credito` confere a soma e a cobertura)"""
    vistas = {"sem_refeicao": 0, "com_refeicao": 0}
    for dono, lugar, s in (("atencioso", "longe", 101), ("relapso", "longe", 202), ("aleatorio", "perto", 101), ("incoerente", "longe", 101)):
        _, reg, _ = orq.viver("M3", dono, lugar, s, 4, 16, conserto=True)
        c = orq.cerebro_de(reg)
        orq.conferir_credito("M3", c)
        ms = c.motivos
        opcoes = [f for m in ms for f in m["fins"] if f["motivo"] != "achou"] + [f for m in ms for f in m.get("busca_entregue", [])]
        for f in opcoes:
            ks = range(f["inicio"], f["inicio"] + f["n"])
            if not any(ms[k]["escolha"][:2] == ["comer", "cheiro"] for k in ks):
                continue
            comeu = any(ms[k]["consequencia"]["comeu"] is not None for k in ks)
            vistas["com_refeicao" if comeu else "sem_refeicao"] += 1
            if not comeu:
                assert f["r"] <= 0, (dono, lugar, s, f)
            else:
                assert sum(1 for k in ks if ms[k]["consequencia"]["comeu"] is not None) == 1
    assert vistas["sem_refeicao"] > 0 and vistas["com_refeicao"] > 0, vistas


# ================================================================== T-CADEIA-1 com as duas ligadas
def test_t_cadeia_1_o_oraculo_com_as_duas_subchaves(monkeypatch):
    """o oraculo de hoje (tests/test_digibrain_vidas.py) com os bracos do conserto: o M0 com as duas subchaves"""
    import test_digibrain_vidas as tv
    fabricas = orq.fabricas
    monkeypatch.setattr(tv.orq, "fabricas", lambda *a, **kw: fabricas(*a, **{**kw, "conserto": True}))
    tv.test_t_cadeia_1_o_oraculo_no_mvp()
    c = tv._faminto()[2]
    assert c.cd.cheiro_inato and c.cd.intencao_cheiro


# ================================================================== T-HABITO-1 e T-ALCANCE-1 (a regra do motor)
class _Forcada:
    """um cerebro de teste: a acao e o alvo de cada decisao vem de `plano(k, obs, motor)`; guarda o corpo na decisao e logo depois do
    gancho `consequencia_corpo` (o r do DigiBrain: o sinal_corpo entre os dois, adapt.py)"""

    nome = "forcada"

    def __init__(self, plano) -> None:
        self.plano, self.motor, self.k = plano, None, 0
        self.decisoes: list[dict] = []

    def agir(self, obs, rng):
        acao, alvo = self.plano(self.k, obs, self.motor)
        self.decisoes.append({"k": self.k, "tick": self.motor._estado.tick, "obs": obs, "acao": acao, "alvo": alvo, "corpo_depois": None})
        self.k += 1
        return acao

    def escolher_alvo(self, acao, candidatos, percepcao, u):
        alvo = self.decisoes[-1]["alvo"]
        return alvo(candidatos) if callable(alvo) else alvo

    def consequencia_corpo(self, acao, ocorrido, obs_depois) -> None:
        self.decisoes[-1]["corpo_depois"] = obs_depois.corpo

    def consequencia_mundo(self, acao, ocorrido, obs_depois) -> None:
        self.decisoes[-1]["ocorrido"] = ocorrido

    def observar(self, transicao) -> None:
        return None

    def receber_acao_dono(self, acao, tick) -> None:
        return None

    def estado_interno(self) -> dict:
        return {}


def _motor(plano, semente=101):
    _, fm = orq.fabricas("M3", "atencioso", semente, 3, 16)
    pol = _Forcada(plano)
    motor = fm(pol, CONFIG_PADRAO, semente)
    pol.motor = motor
    return motor, pol


def _comida(ident):
    return lambda cands: next((c for c in cands if c.tipo == "comida" and c.id == ident), None)


def test_t_habito_1_a_classificacao_da_dx5_pela_regra_do_motor():
    """em estados de teste (tres dias de um pet do cenario, as acoes em ciclo, comida posta ao lado antes de cada comer e ate onde o
    explorar vai): dormir, ocioso e chamar a atencao dao r = 0; emburrar, r <= 0; comer, brincar e explorar, r > 0 em algum"""
    ciclo = (AcaoPet.OCIOSO, AcaoPet.DORMIR, AcaoPet.COMER, AcaoPet.CHAMAR_ATENCAO, AcaoPet.BRINCAR, AcaoPet.EMBURRAR, AcaoPet.EXPLORAR)
    postas = {}

    def plano(k, obs, motor):
        acao = ciclo[k % len(ciclo)]
        if acao in (AcaoPet.COMER, AcaoPet.EXPLORAR):
            ident = postas.get(k)
            if ident is None:
                return acao, None
            x, y = next((c["x"], c["y"]) for c in motor.mundo.comidas.values() if c["id"] == ident)
            return acao, (_comida(ident) if acao is AcaoPet.COMER else Alvo.ponto(x, y))
        return acao, None

    motor, pol = _motor(plano)
    c = DigiBrain(CONFIG_PADRAO, CONFIG_DIGIBRAIN_LIGADA, tm.CM)
    rs: dict = {a.value: [] for a in ciclo}
    for k in range(3 * 96):
        if ciclo[k % len(ciclo)] in (AcaoPet.COMER, AcaoPet.EXPLORAR) and k % 2:
            x, y = motor.pet
            motor.deixar_comida("racao", min(x + 40, 1000), y)
            postas[k] = motor.deixadas[-1]["id"]
        motor.avancar(15)
        d = pol.decisoes[-1]
        recs = c.m.sens._receptores(d["obs"].corpo)
        rs[d["acao"].value].append(c.m.afeto.consequencia(d["obs"].corpo, d["corpo_depois"], recs)["r"])
    assert all(r == 0 for a in ("dormir", "ocioso", "chamar_atencao") for r in rs[a]), {a: set(rs[a]) for a in rs}
    assert all(r <= 0 for r in rs["emburrar"])
    assert all(any(r > 0 for r in rs[a]) for a in ("comer", "brincar", "explorar")), {a: max(rs[a]) for a in rs}
    assert set(ACOES_R_POSSIVEL) == {"comer", "brincar", "explorar", "aliviar"}


@pytest.mark.parametrize("d", [0, 10, 16, 17, 76, 77, 96, 320, 384, 480])
def test_t_alcance_1_a_janela_pela_regra_do_motor(d):
    """uma racao a d subunidades do pet, posta no tick de uma decisao; o pet anda reto para ela desde a decisao da posta (o lugar dela, e
    a racao quando a ve): (i) a decisao k0 e a do tick da posta e ja tem a racao no chao (e na visao, ate 6 celulas); (ii) o consumo sai na
    decisao k0 + n_min(d) - 1 (k0 com n_min = 0); (iii) a medida de hoje aceita de k0 a k0 + 8, e a W(d) de k0 a k0 + 8 + n_min(d)"""
    g = orq.geometria()
    alvo = {}

    def plano(k, obs, motor):
        if "id" not in alvo:
            return AcaoPet.OCIOSO, None
        if any(v[0] == alvo["id"] for v in obs.mundo.vistos):
            return AcaoPet.COMER, _comida(alvo["id"])
        return AcaoPet.EXPLORAR, Alvo.ponto(*alvo["xy"])

    motor, pol = _motor(plano)
    for _ in range(3):
        motor.avancar(15)
    x, y = motor.pet
    t0 = motor._estado.tick
    motor.deixar_comida("racao", x + d, y)
    alvo.update(id=motor.deixadas[-1]["id"], xy=(x + d, y))
    n = n_min_decisoes(d, g["raio_pegar"], g["passo"])
    while not motor.consumos_mundo:
        motor.avancar(15)
        assert len(pol.decisoes) < 30
    k0 = -(-t0 // 15)
    dec = pol.decisoes[k0]
    assert dec["tick"] == t0 == 15 * k0                                                    # (i)
    assert any(v[0] == alvo["id"] for v in dec["obs"].mundo.vistos) == (d <= g["raio_visao"])
    c = motor.consumos_mundo[0]
    assert c["id"] == alvo["id"] and c["tick"] // 15 == (k0 + n - 1 if n >= 1 else k0)        # (ii)
    # (iii) a medida de hoje e a W(d), pelas funcoes de metrics.py
    w = janela_w(d, W8, g["raio_pegar"], g["passo"])
    assert w == 8 + n and orq.w_de(d) == w
    for k, hoje, wd in ((k0 + 8, True, True), (k0 + 9, False, n >= 1), (k0 + 8 + n, n == 0, True), (k0 + 9 + n, False, False)):
        cons = [(1, 15 * k, "racao", 600, 200)]
        assert cadeia_comida_corpo([(1, t0, 0.3)], cons, 1)["fechadas"] == int(hoje), (k, "hoje")
        assert cadeia_comida_corpo([(1, t0, 0.3)], cons, 1, w_ticks_por_racao={1: 15 * w})["fechadas"] == int(wd), (k, "W(d)")


def test_t_alcance_1_a_posta_cai_no_tick_de_uma_decisao_no_cenario():
    """no cenario do orquestrador, toda racao e posta no tick de uma decisao, antes do avanco desse tick (a convencao de A3.2)"""
    for dono, lugar in orq.CELULAS:
        motor, _, _ = orq.viver("M3", dono, lugar, 101, 2, 16, conserto=True)
        linhas = [json.loads(x) for x in motor.log.para_jsonl().splitlines()]
        for i, e in enumerate(linhas):
            if e["tipo"] == "deixar_comida":
                j = next(j for j in range(i, len(linhas)) if linhas[j]["tipo"] == "avanco")
                assert e["tick"] % 15 == 0 and all(x["tick"] == e["tick"] for x in linhas[i:j + 1]), (dono, lugar, e)


# ================================================================== T-JANELA-IGUAL e T-EPISODIO-5
def test_t_janela_igual_a_w_e_a_mesma_em_todo_braco_e_lugar():
    ds = (0, 16, 50, 96, 320, 384, 480, 700)
    ws = [orq.w_de(d) for d in ds]
    assert ws == [8, 8, 9, 10, 14, 15, 16, 20]
    assert "braco" not in inspect.signature(orq.w_de).parameters and "lugar" not in inspect.signature(orq.w_de).parameters
    for braco in ("M3", "M3-420", "A11"):
        for lugar in ("perto", "longe"):
            motor, reg, _ = orq.viver(braco, "atencioso", lugar, 202, 3, 16, conserto=True)
            ep = orq.medidas(motor, reg, braco, 3, True)["episodios_fome"]
            assert all(w == orq.w_de(d0) for _, d0, w, _, _ in ep["episodios"]), (braco, lugar)


def test_t_episodio_5_a_w_sai_das_constantes_do_motor(monkeypatch):
    assert orq.geometria() == orq.GEOMETRIA_DO_ADENDO
    assert n_min_decisoes(480, 16, 60) == 8 and n_min_decisoes(480, 16, 80) == 6 and janela_w(480, 8, 32, 60) == 16
    for campo, valor in (("velocidade", 5), ("raio_pegar_celulas", 2), ("raio_cheiro_celulas", 20), ("raio_visao_celulas", 5)):
        monkeypatch.setattr(orq, "CM", replace(orq.CM, **{campo: valor}))
        with pytest.raises(RuntimeError, match="volta ao Matheus"):
            orq.w_de(100)
        monkeypatch.undo()
    with pytest.raises(ValueError):
        n_min_decisoes(-1, 16, 60)
    with pytest.raises(ValueError):
        janela_w(10, 0, 16, 60)


# ================================================================== T-VISITA-1 (DX-1)
def test_t_visita_1_o_lugar_visitado():
    P_ = (500, 200)
    dentro, fora = (7, 500 + 70, 200), (8, 500 + 80, 200)            # a 70 e a 80 subunidades de P (R_lugar = 76)
    comidas = [dentro, fora]
    v = [(10, *P_, comidas)]
    assert visitas_vazias(v, [(10, 7)], 76) == {"visitas": 1, "vazias": 0, "acharam": 1}          # na chegada
    assert visitas_vazias(v, [(11, 7)], 76)["acharam"] == 1                                        # na decisao seguinte
    assert visitas_vazias(v, [(11, 8)], 76)["vazias"] == 1                                         # fora do lugar
    assert visitas_vazias(v, [(12, 7)], 76)["vazias"] == 1                                         # depois da k + 1
    assert visitas_vazias(v, [(11, 9)], 76)["vazias"] == 1                                         # outra comida, que nao estava la
    assert visitas_vazias([(10, *P_, [fora])], [(10, 8)], 76)["vazias"] == 1
    assert visitas_vazias([(10, *P_, comidas), (20, 0, 0, [])], [(10, 7), (11, 8)], 76) == {"visitas": 2, "vazias": 1, "acharam": 1}
    assert orq.GEOMETRIA_DO_ADENDO["r_lugar"] == 60 + 16 == 76
    # a v1 da o numero de hoje: a visita cuja propria decisao nao comeu
    assert visitas_vazias_v1([False, True, False]) == 2
    with pytest.raises(ValueError):
        visitas_vazias(v, [(10, 7), (10, 8)], 76)
    for braco in ("M3", "M3-sem-inato"):
        motor, reg, _ = orq.viver(braco, "relapso", "longe", 101, 4, 16, conserto=True)
        x = orq.medidas(motor, reg, braco, 4, True)
        hoje = orq.medidas(motor, reg, braco, 4, False)
        assert x["visitas_vazias_v1"] == hoje["visitas_vazias"] and x["visitas_vazias"] <= x["visitas_vazias_v1"]
        assert x["visitas_lugar_lembrado"] == hoje["visitas_lugar_lembrado"] > 0


# ================================================================== T-EPISODIO-1 a 4 (DX-2)
def _decs(fomes, ofertas):
    """decisoes sinteticas: a fome e a oferta {id: d} de cada decisao"""
    return [(k, f, min(o.values()) if o else None, frozenset(o)) for k, (f, o) in enumerate(zip(fomes, ofertas))]


def _ep(decs, refeicoes):
    return episodios_de_fome(decs, refeicoes, W8, RAIO, PASSO, 0.5, 384)


def test_t_episodio_1_abre_e_fecha():
    # tres racoes postas com a fome continua, uma comida: um episodio, fechado; a medida (a) da 1 de 3
    fomes = [0.8, 0.4, 0.4, 0.4, 0.4, 0.4, 0.9]
    ofertas = [{}, {}, {1: 100}, {1: 90, 2: 300}, {1: 40, 2: 300, 3: 200}, {2: 300, 3: 200}, {2: 300, 3: 200}]
    r = _ep(_decs(fomes, ofertas), [(4, True, True, 700, 300)])
    assert (r["n"], r["fechados"], r["taxa"]) == (1, 1, 1.0) and r["episodios"] == [[2, 100, 8 + n_min_decisoes(100, 16, 60), 4, "fechou"]]
    assert r["latencias"] == [2]
    racoes = [(1, 30, 0.4), (2, 45, 0.4), (3, 60, 0.4)]
    assert cadeia_comida_corpo(racoes, [(1, 60, "racao", 700, 300)], 1)["fechadas"] == 1
    assert cadeia_comida_corpo(racoes, [(1, 60, "racao", 700, 300)], 1)["elegiveis"] == 3
    # a fome comeca ja com racao no chao: abre na primeira decisao da fome
    r = _ep(_decs([0.9, 0.3, 0.3], [{5: 50}, {5: 50}, {5: 50}]), [])
    assert r["episodios"][0][:2] == [1, 50] and r["motivos"]["vida_acabou"] == 1
    # sem queda da falta, nao fecha
    r = _ep(_decs([0.3] * 12, [{5: 10}] * 12), [(1, True, True, 700, 700)])
    assert r["fechados"] == 0 and r["no_episodio_sem_fechar"] == 1 and r["motivos"]["janela_vencida"] == 1


def test_t_episodio_2_sem_repeticao_nem_sobreposicao():
    # a janela vence com a fome continuando e o dono pondo mais racao: nao abre outro na mesma fome
    n = 40
    ofertas = [{1: 500}] * 10 + [{1: 500, k: 500} for k in range(2, n - 9)]
    r = _ep(_decs([0.3] * n, ofertas), [])
    w = 8 + n_min_decisoes(500, 16, 60)
    assert r["n"] == 1 and r["episodios"] == [[0, 500, w, w, "janela_vencida"]]
    # fechou e a fome continua (uma racao nao basta): a mesma fome, sem episodio novo
    r = _ep(_decs([0.1] * 20, [{1: 10, 2: 10}] * 20), [(1, True, True, 900, 700)])
    assert r["n"] == 1 and r["motivos"]["fechou"] == 1
    # um episodio novo so depois de F deixar de valer em ao menos uma decisao
    fomes = [0.3] * 12 + [0.6] + [0.3] * 12
    r = _ep(_decs(fomes, [{1: 10}] * 25), [])
    assert [e[0] for e in r["episodios"]] == [0, 13] and r["n"] == 2
    ks = [(e[0], e[3]) for e in r["episodios"]]
    assert all(a[1] < b[0] for a, b in zip(ks, ks[1:]))                                   # disjuntos no tempo


def test_t_episodio_3_a_refeicao_conta_uma_vez():
    # duas refeicoes na mesma janela: a primeira fecha; a segunda e fora de episodio
    r = _ep(_decs([0.1] * 12, [{1: 10, 2: 20}] * 12), [(2, True, True, 900, 800), (4, True, True, 800, 700)])
    assert (r["n"], r["fechados"], r["fora_de_episodio"]) == (1, 1, 1)
    # uma refeicao sem fome nao entra na taxa
    r = _ep(_decs([0.9] * 5, [{1: 10}] * 5), [(2, True, True, 100, 50)])
    assert (r["n"], r["taxa"], r["fora_de_episodio"]) == (0, None, 1)
    # a refeicao depois da janela vencida, na mesma fome: fora de episodio, com a latencia contada a parte
    r = _ep(_decs([0.3] * 15, [{1: 10}] * 15), [(12, True, True, 700, 300)])
    assert r["motivos"]["janela_vencida"] == 1 and r["fora_de_episodio"] == 1 and r["latencias_depois_da_janela"] == [12]
    with pytest.raises(ValueError, match="duas refeicoes"):
        _ep(_decs([0.3] * 3, [{1: 10}] * 3), [(1, True, True, 700, 300), (1, True, True, 700, 300)])


def test_t_episodio_4_sem_exclusao_do_denominador():
    # a fome que acaba por outra comida dentro da janela: falha, no denominador
    r = _ep(_decs([0.3, 0.3, 0.3, 0.7, 0.7], [{1: 200}] * 5), [(2, False, True, 700, 300)])
    assert r["motivos"]["saciado_por_outra_comida"] == 1 and (r["n"], r["fechados"], r["taxa"]) == (1, 0, 0.0)
    # a racao que apodrece ou some na janela nao encerra o episodio; a janela vencida e falha
    ofertas = [{1: 200}] * 3 + [{}] * 12
    r = _ep(_decs([0.3] * 15, ofertas), [])
    w = 8 + n_min_decisoes(200, 16, 60)
    assert r["episodios"] == [[0, 200, w, w, "janela_vencida"]] and r["oferta_mudou"] == 1 and r["taxa"] == 0.0
    # a correcao de 2026-10-26 (#424): a racao podre comida na janela nao fecha (no motor a falta nao cai; mesmo com a falta caindo, a
    # podre nao conta), nao encerra o episodio e, sem outra racao que reduza a fome ate o fim da janela, e falha no denominador
    for podre in ((5, True, False, 700, 700), (5, True, False, 700, 650)):
        r = _ep(_decs([0.3] * 15, ofertas), [podre])
        assert r["episodios"] == [[0, 200, w, w, "janela_vencida"]] and r["no_episodio_sem_fechar"] == 1 and r["taxa"] == 0.0
    # uma racao madura comida depois da podre, ainda na janela, fecha
    ofertas2 = [{1: 200}] * 3 + [{2: 40}] * 12
    r = _ep(_decs([0.3] * 15, ofertas2), [(5, True, False, 700, 700), (7, True, True, 700, 300)])
    assert r["episodios"] == [[0, 200, w, 7, "fechou"]] and r["taxa"] == 1.0 and r["no_episodio_sem_fechar"] == 1
    # o denominador e sempre o numero de episodios
    fomes = [0.3] * 12 + [0.7] + [0.3] * 3 + [0.7] + [0.3] * 12
    r = _ep(_decs(fomes, [{1: 30}] * len(fomes)), [(1, True, True, 900, 500), (14, False, True, 900, 600)])
    assert r["n"] == sum(r["motivos"].values()) == 3 and r["taxa"] == 1 / 3
    assert r["por_d0"] == {"ate_corte": {"n": 3, "fechados": 1}, "alem_do_corte": {"n": 0, "fechados": 0}}


# ================================================================== T-CENARIO-1 e a fumaca de ponta a ponta
def test_t_cenario_1_e_a_fumaca_da_reavaliacao(tmp_path):
    """a fumaca da reavaliacao (2 unidades x 12 bracos x 12 celulas, 2 dias): o T-CENARIO-1 e o credito em toda vida (falham alto no
    orquestrador), o replay do disco, as medidas e a analise do conserto; o piloto e a calibracao do conserto sobre os mesmos registros"""
    cfg = _cfg("fumaca_reavaliacao.json")
    r = orq.rodar(cfg, tmp_path / "reavaliacao", processos=2)
    regs = r["registros"]
    assert len(regs) == 2 * len(orq.CELULAS) * 12 and {x["braco"] for x in regs} == set(orq.BRACOS_CONSERTO)
    res = r["resultado"]
    assert res["primaria"] == "G-MVP-EP" and {"G-MVP", "G-ELEGIVEL", "G-MVP-EP", "G-ELEGIVEL-EP", "G-DX", "DX-5"} <= set(res)
    assert set(res["G-DX"]["longe"]["contrastes"]) == set(orq.FAMILIA_DX) == set(res["G-DX"]["todas"]["contrastes"])
    assert sorted(x["holm"]["limiar"] for x in res["G-DX"]["longe"]["contrastes"].values()) == [0.05 / 2, 0.05]
    assert res["G-DX"]["longe"]["contrastes"]["G-DX-INATO"]["celulas"] == 4
    assert res["G-ABLA"]["G-ABLA-P2"]["contraste"].startswith("medida(M2)")            # o indice de hoje, sem mudanca
    for x in regs:
        ep = x["episodios_fome"]
        assert ep["n"] == sum(ep["motivos"].values()) and all(w == orq.w_de(d0) for _, d0, w, _, _ in ep["episodios"])
        assert x["cadeia_w"]["elegiveis"] == x["cadeia"]["elegiveis"] and x["cadeia_w"]["fechadas"] >= x["cadeia"]["fechadas"]
        if x["braco"] != "A11":
            assert x["visitas_vazias"] <= x["visitas_vazias_v1"] and set(x["repeticao_r_possivel"]["por_acao"]) == set(ACOES_R_POSSIVEL)
    assert any(x["cheiro"]["achou"] for x in regs if x["braco"] == "M3")
    assert not any(x["cheiro"]["achou"] or x["cheiro"]["fins_busca"] for x in regs if x["braco"] in ("M3-420", "M3-sem-intencao"))
    pil = orq.analisar_piloto(regs, {**cfg, "poder": {**orq.PODER, "replicas": 10, "reamostragens_internas": 20, "k_max": 4}}, True)
    assert pil["n"]["k"] == 4 and "G-DX" in pil["contrastes_so_relato"] and "G-ELEGIVEL-EP" in pil["premissas"]
    assert set(pil["premissas"]["episodios_por_vida"]) == set(orq.BRACOS_MODULAR_CONSERTO)
    cal = orq.analisar_calibracao(regs, {**cfg, "rodada": 1}, True)
    assert cal["criterios"]["taxa_mediana"]["medida"].startswith("a taxa de fechamento por episodio")


def test_t_cenario_1_falha_alto_fora_do_cenario():
    motor, reg, _ = orq.viver("M3", "atencioso", "perto", 101, 1, 16, conserto=True)
    orq.conferir_cenario(motor, reg)
    motor.mundo.nova_comida("a", 100, 100, 0, "arvore")                     # outra comida no mundo
    with pytest.raises(RuntimeError, match=r"T-CENARIO-1 \(i\)"):
        orq.conferir_cenario(motor, reg)
    motor, reg, _ = orq.viver("M3", "atencioso", "perto", 101, 1, 16, conserto=True)
    motor.consumos_mundo.pop()                                                # a racao sai do chao sem consumo nem idade
    with pytest.raises(RuntimeError, match=r"T-CENARIO-1 \(iii\)"):
        orq.conferir_cenario(motor, reg)
    motor, reg, _ = orq.viver("M3", "atencioso", "perto", 101, 1, 16, conserto=True)
    k = next(k for k in range(len(reg.estados) - 1) if k not in {c["tick"] // 15 for c in motor.consumos_mundo})
    reg.estados[k + 1] = (reg.estados[k][0] + 0.1,) + tuple(reg.estados[k + 1][1:])     # a fome sobe sem consumo
    with pytest.raises(RuntimeError, match=r"T-CENARIO-1 \(ii\)"):
        orq.conferir_cenario(motor, reg)


# ================================================================== DX-5 (A3.5)
def test_dx5_o_indice_so_nas_acoes_com_r_possivel():
    ds = [(0, "a", "comer", 10), (15, "a", "comer", -5), (30, "a", "dormir", 0), (45, "a", "dormir", 0), (60, "a", "comer", 3),
          (75, "a", "comer", None)]
    hoje = repeticao_apos_alivio(ds, (0, 90))
    dx5 = repeticao_apos_alivio(ds, (0, 90), ACOES_R_POSSIVEL)
    assert (hoje["n_pos"], hoje["n_nao_pos"]) == (2, 3) and (dx5["n_pos"], dx5["n_nao_pos"]) == (2, 1)
    assert dx5["indice"] == 1.0 - 0.0
    por = {a: repeticao_apos_alivio(ds, (0, 90), (a,)) for a in ("comer", "dormir")}
    assert por["comer"]["n_pos"] + por["dormir"]["n_pos"] == hoje["n_pos"]
    assert por["comer"]["n_nao_pos"] + por["dormir"]["n_nao_pos"] == hoje["n_nao_pos"]
