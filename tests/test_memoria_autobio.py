"""C4, M0 e M1 (docs/ESPEC_MEMORIA_AUTOBIOGRAFICA_DIGIBRAIN_MODULAR.md, secoes 3, 8 e 9; MA-1 a MA-8 DECIDIDAS em 2026-11-01): a subchave
`memoria_autobio` do DigiBrain modular, o episodio completo e a codificacao, antes de qualquer vida de pesquisa. So as sementes 101 a 505
e sequencias sinteticas.

  - G2: com ela desligada, as vidas de hoje saem byte a byte (tests/test_gabarito_memoria_autobio.py, o gabarito do M3* gravado antes,
    mais os da C3, da C2, do conserto e do modular); aqui, o que a desligada nao cria (campo, estado);
  - G2-SEPARADO: ligada, ela muda so a vida do braco que a liga, e nas M0 e M1 nem a escolha (o log sai o mesmo); nada fora do pacote
    `digibrain` le a chave;
  - G1: o replay de cada vida com ela ligada, nas cinco sementes;
  - T-ME-0: o episodio sai igual no replay; o M-MEM so recebe o que o cerebro recebeu (pela AST); nenhum campo de fora da Observacao;
  - T-ME-1: um evento forte vira episodio e um neutro nao; o mesmo log codifica os mesmos episodios; a visita vazia com sigma = min(0, r
    da ida);
  - a rng; G-MECANISMO, G-INT, G-SEM-DIRECAO e G-RECEPTOR com ela ligada."""
from __future__ import annotations

import ast
import inspect
import json
import sys
from dataclasses import fields, replace
from pathlib import Path
from types import SimpleNamespace

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import run_v2_digibrain_prototipo as orq  # noqa: E402
import test_digibrain_mecanismo as tm  # noqa: E402

from digilab.config import (CONFIG_DIGIBRAIN, CONFIG_DIGIBRAIN_INATOS, CONFIG_DIGIBRAIN_LIGADA, CONFIG_MUNDO_LIGADA,  # noqa: E402
                            PARAMETROS_DIGIBRAIN_INATOS, RECEPTORES_DIGIBRAIN, TICKS_POR_DIA, ConfigDigibrain, ConfigDigibrainInatos)
from digilab.digibrain import mem as M  # noqa: E402
from digilab.digibrain.ganchos import CAMPOS_POR_MODULO  # noqa: E402

P = CONFIG_DIGIBRAIN_INATOS
S = P.escala
SEMENTES = (101, 202, 303, 404, 505)
BASE = replace(CONFIG_DIGIBRAIN_LIGADA, cheiro_inato=True, intencao_cheiro=True)
LIGADA = replace(BASE, memoria_autobio=True)
# os campos do episodio (a tabela 3.1 da espec, sem os da M3 que a M0 so cria) e os que o M-MEM poe ao guardar
CAMPOS_EPISODIO = {"decisao", "tick", "ponto", "regiao", "vista", "cheiro", "noite", "acao", "objeto", "dono", "outro", "corpo_antes",
                   "corpo_depois", "delta", "V_antes", "V_depois", "E_antes", "E_depois", "r", "r_n", "sigma", "classe", "origem",
                   "categoria", "fome_antes", "hora", "rep", "rec", "memoria"}
CAMPOS_GUARDADOS = CAMPOS_EPISODIO | {"id", "lugar"}


# ------------------------------------------------------------------ as pecas sinteticas
def sens(objetos=(), ha_cheiro=False, noite=0, fome=300) -> dict:
    return {"objetos": list(objetos), "ha_cheiro": ha_cheiro, "contexto": {"noite": noite}, "falta": {"fome": fome}, "minuto": 600}


def leituras(**kw) -> list:
    return [kw.get(r, 0) for r in RECEPTORES_DIGIBRAIN]


PM1 = SimpleNamespace(x=40, y=72, regiao=1)
COMIDA = {"id": 7, "tipo": "a", "classe": "a", "dx": 1, "dy": 0, "d": 30, "prox": 900, "nov": 0}
BOLA = {"id": 3, "tipo": "bola", "classe": "bola", "dx": 0, "dy": 2, "d": 50, "prox": 800, "nov": 0}


def unidade(chave: tuple, objeto=None) -> dict:
    return {"chave": chave, "acao": chave[0], "tipo": chave[1], "objeto": objeto, "d": None}


def episodio(r_n=0, depois=None, unid=None, comeu=None, chegou=False, r_ida=None, objetos=(), gestos=()):
    return M.episodio_autobio(sens(objetos), PM1, RECEPTORES_DIGIBRAIN, leituras(), depois or leituras(), {"V": 5, "E": 9},
                              {"r": 2 * r_n, "r_n": r_n, "V": 6, "E": 10}, list(gestos), unid or unidade(("ocioso", None, None)),
                              {"comeu": comeu, "chegou": chegou, "r_ida": r_ida}, 4, 75, P)


def _sem_float(x) -> bool:
    if isinstance(x, float):
        return False
    if isinstance(x, dict):
        return all(isinstance(k, str) and _sem_float(v) for k, v in x.items())
    if isinstance(x, (list, tuple)):
        return all(_sem_float(v) for v in x)
    return x is None or isinstance(x, (int, str))


# ------------------------------------------------------------------ a subchave e os campos
def test_a_subchave_nasce_desligada_e_so_aceita_bool():
    assert CONFIG_DIGIBRAIN.memoria_autobio is False and CONFIG_DIGIBRAIN_LIGADA.memoria_autobio is False
    with pytest.raises(TypeError, match="memoria_autobio"):
        ConfigDigibrain(memoria_autobio=1)


@pytest.mark.parametrize("extra", [{"m_mem": False}, {"credito_corrida": True}, {"intencao_suspensa": True},
                                   {"redecidir_evento": True}, {"cheiro_inato": False}, {"intencao_cheiro": False}])
def test_a_subchave_recusa_as_combinacoes_da_ma_7(extra):
    with pytest.raises(ValueError, match="memoria_autobio"):
        replace(LIGADA, **extra)


def test_os_campos_da_m1_sao_os_da_secao_8_decididos_no_modulo_mem():
    assert (P.theta_sig, P.theta_afeto, P.n_rec) == (S // 8, S // 2, 16) == (128, 512, P.n_ep)
    for c in ("theta_sig", "theta_afeto", "n_rec"):
        assert c in CAMPOS_POR_MODULO["mem"] and PARAMETROS_DIGIBRAIN_INATOS[c][0] == "DECIDIDO"
        assert "SEM FONTE" in PARAMETROS_DIGIBRAIN_INATOS[c][1]
    assert {f.name for f in fields(ConfigDigibrainInatos)} == {c for cs in CAMPOS_POR_MODULO.values() for c in cs}
    for kw in ({"n_rec": 0}, {"theta_sig": 0}, {"theta_afeto": S + 1}):
        with pytest.raises(ValueError, match="theta_sig"):
            ConfigDigibrainInatos(**kw)


def test_desligada_o_estado_e_o_motivo_nao_tem_campo_novo():
    mem = M.Memoria(CONFIG_MUNDO_LIGADA)
    assert "autobio" not in mem.estado_interno() and not hasattr(mem, "recente")
    with pytest.raises(RuntimeError, match="memoria_autobio"):
        mem.relogio(0)
    with pytest.raises(RuntimeError, match="memoria_autobio"):
        mem.codificar_autobio(episodio(r_n=500))
    c = orq.cerebro_de(_viver(101, ligada=False)[1])
    assert "autobio" not in c.m.mem.estado_interno()
    assert not any("autobio" in m["consequencia"] for m in c.motivos if m["consequencia"])


# ------------------------------------------------------------------ T-ME-0: o formato
def test_t_me_0_o_episodio_tem_os_campos_da_tabela_3_1_sem_float():
    ep = episodio(r_n=300, unid=unidade(("comer", "comida", 7), COMIDA), objetos=[COMIDA, BOLA], gestos=[["carinho", 30], ["tapa", 40]])
    assert set(ep) == CAMPOS_EPISODIO and _sem_float(ep)
    assert ep["vista"] == ["a", "bola"] and ep["objeto"] == {"id": 7, "classe": "a"} and ep["dono"] == ["carinho", "tapa"]
    assert ep["outro"] is None and ep["acao"] == ["comer", "comida", 7] and ep["tick"] == 75 and ep["decisao"] == 4
    assert set(ep["corpo_antes"]) == set(ep["corpo_depois"]) == set(ep["delta"]) == set(RECEPTORES_DIGIBRAIN)
    assert (ep["V_antes"], ep["V_depois"], ep["E_antes"], ep["E_depois"]) == (5, 6, 9, 10)
    assert (ep["rep"], ep["rec"], ep["memoria"]) == (0, 0, "recente")


def test_t_me_0_o_m_mem_so_recebe_o_que_o_cerebro_recebeu():
    """pela AST: o mem.py importa so a config, a geometria inteira, a conta inteira do A e o _comum (nenhum objeto do motor), e o
    episodio so tem os parametros da Observacao, dos receptores, do afeto, dos gestos, da unidade e do desfecho que o M-ADAPT ja le"""
    arvore = ast.parse(inspect.getsource(M))
    origens = {n.module for n in ast.walk(arvore) if isinstance(n, ast.ImportFrom)}
    assert origens == {"__future__", "config", "modelo_mundo", "policies.lobos", "_comum"}
    assert not any(isinstance(n, ast.Import) for n in ast.walk(arvore))
    assert list(inspect.signature(M.episodio_autobio).parameters) == [
        "sens", "pm1", "recs", "l0", "l1", "afeto_antes", "cons", "gestos", "unidade", "desfecho", "k", "tick", "p"]
    fonte = inspect.getsource(M.episodio_autobio)
    assert "pc" not in {n.attr for n in ast.walk(ast.parse(fonte.strip())) if isinstance(n, ast.Attribute)}
    assert "direcao" not in fonte and "random" not in inspect.getsource(M)


def test_t_me_0_nenhum_campo_do_estado_privado_nas_vidas():
    for c in (orq.cerebro_de(_viver(s)[1]) for s in (101, 303)):
        recente = c.m.mem.estado_interno()["autobio"]["recente"]
        assert recente and all(set(e) == CAMPOS_GUARDADOS and _sem_float(e) for e in recente)
        assert all(set(e["corpo_antes"]) == set(c.m.sens.receptores) for e in recente)
        json.dumps(recente)


# ------------------------------------------------------------------ T-ME-1: a codificacao
def test_t_me_1_um_evento_forte_vira_episodio_e_um_neutro_nao():
    assert episodio(r_n=P.theta_sig - 1) is None and episodio(r_n=-(P.theta_sig - 1)) is None
    assert episodio(r_n=0, depois=leituras(estresse=P.theta_afeto - 1, dor=10, fome=S)) is None   # a fome nao e afetiva
    forte = episodio(r_n=P.theta_sig)
    assert forte["origem"] == "evento" and forte["sigma"] == P.theta_sig and forte["categoria"] == ["ocioso", "sem_alvo", 1]
    ruim = episodio(r_n=-P.theta_sig, unid=unidade(("brincar", "bola", 3), BOLA), objetos=[BOLA])
    assert ruim["classe"] == "bola" and ruim["categoria"] == ["brincar", "bola", -1]
    for r in ("dor", "susto", "estresse"):
        susto = episodio(r_n=0, depois=leituras(**{r: P.theta_afeto}))
        assert susto["origem"] == "evento" and susto["sigma"] == 0 and susto["categoria"] == ["ocioso", "sem_alvo", 0]


def test_t_me_1_o_consumo_vira_episodio_sempre_com_a_classe_comida():
    ep = episodio(r_n=5, unid=unidade(("comer", "comida", 7), COMIDA), comeu="a", objetos=[COMIDA])
    assert ep["origem"] == "consumo" and ep["classe"] == "a" and ep["sigma"] == ep["r_n"] == 5 and ep["ponto"] == (40, 72)
    podre = episodio(r_n=-400, unid=unidade(("explorar", "cheiro", None)), comeu="podre")
    assert podre["categoria"] == ["explorar", "podre", -1] and podre["objeto"] is None


def test_t_me_1_a_visita_vazia_tem_sigma_min_0_r_da_ida():
    ponto = unidade(("explorar", "ponto", (100, 200)))
    cara = episodio(r_n=-30, unid=ponto, chegou=True, r_ida=-300)
    assert cara["origem"] == "visita" and cara["classe"] == "nao_havia" and cara["sigma"] == -300 and cara["ponto"] == (100, 200)
    assert cara["categoria"] == ["explorar", "nao_havia", -1] and cara["r"] == cara["r_n"] == 0          # o r de hoje, forcado a 0
    boa = episodio(r_n=200, unid=ponto, chegou=True, r_ida=150)                     # nada se achou: nunca positivo (MA-1)
    assert boa["sigma"] == 0 and boa["categoria"] == ["explorar", "nao_havia", 0]
    with pytest.raises(ValueError, match="r da ida"):
        episodio(unid=ponto, chegou=True, r_ida=None)
    assert episodio(r_n=0, unid=ponto, chegou=False) is None                        # a ida sem chegar e um evento como os outros


def test_t_me_1_a_recente_cheia_descarta_o_de_menor_sigma_e_registra():
    mem = M.Memoria(CONFIG_MUNDO_LIGADA, autobio=True)
    sigmas = [300, -200, 500, 200] + [400] * (P.n_rec - 4)
    for k, s in enumerate(sigmas):
        mem.codificar_autobio({**episodio(r_n=s), "decisao": k})
    mem.codificar_autobio({**episodio(r_n=900), "decisao": P.n_rec})
    assert mem.saidas_autobio == [{"id": 1, "sigma": -200}]                         # |-200| = |200|: sai o mais antigo
    mem.codificar_autobio({**episodio(r_n=900), "decisao": P.n_rec + 1})
    assert mem.saidas_autobio[-1] == {"id": 3, "sigma": 200} and len(mem.recente) == P.n_rec
    with pytest.raises(ValueError, match="visita"):
        mem.codificar_autobio({**episodio(r_n=500), "origem": "visita", "classe": "nao_havia", "sigma": 1})


def test_o_relogio_avanca_o_dia_quando_a_hora_volta():
    mem = M.Memoria(CONFIG_MUNDO_LIGADA, autobio=True)
    assert [mem.relogio(m) for m in (0, 15, TICKS_POR_DIA - 15, 0, 30)] == [0, 15, TICKS_POR_DIA - 15, TICKS_POR_DIA,
                                                                              TICKS_POR_DIA + 30]
    with pytest.raises(ValueError, match="hora"):
        mem.relogio(TICKS_POR_DIA)


# ------------------------------------------------------------------ as vidas: G1, G2-SEPARADO, T-ME-0 e T-ME-1 no replay
def _viver(semente: int, lugar: str = "longe_fixo", dono: str = "relapso", ligada: bool = True):
    original = orq.config_do_braco
    orq.config_do_braco = lambda b, g=None, c=False: replace(original(b, g, c), memoria_autobio=ligada)
    try:
        motor, reg, fab = orq.viver("M3", dono, lugar, semente, 3, 16, conserto=True)
    finally:
        orq.config_do_braco = original
    _viver.fab = (motor, fab)
    return motor, reg


@pytest.mark.parametrize("semente", SEMENTES)
def test_g1_o_replay_com_a_subchave_ligada_e_o_mesmo_log_da_desligada(semente):
    motor, reg = _viver(semente)
    orq.conferir_replay(motor, _viver.fab[1], semente, motor.log.para_jsonl())   # o estado interno, com a recente, bit a bit
    orq.conferir_mecanismo("M3", reg, None)
    orq.conferir_cenario(motor, reg)
    c = orq.cerebro_de(reg)
    assert c.cd.memoria_autobio and all("autobio" in m["consequencia"] for m in c.motivos if m["consequencia"])
    assert c.m.mem.estado_interno()["autobio"]["proximo_id"] > 0
    # nas M0 e M1 a recente nao muda nenhuma escolha: o log e a rng de politica sao os da vida desligada
    motor0, reg0 = _viver(semente, ligada=False)
    assert motor.log.para_jsonl() == motor0.log.para_jsonl()
    assert c.m.arb.sorteios == orq.cerebro_de(reg0).m.arb.sorteios
    # a referencia ao log: o tick do episodio e o da decisao (k x o intervalo, a Observacao do Registro)
    assert all(e["tick"] == e["decisao"] * 15 for e in c.m.mem.estado_interno()["autobio"]["recente"])


def test_t_me_1_o_mesmo_log_codifica_os_mesmos_episodios(monkeypatch):
    todos: list = []
    original = M.Memoria.codificar_autobio
    monkeypatch.setattr(M.Memoria, "codificar_autobio", lambda self, ep: (todos.append(json.dumps(ep, sort_keys=True)),
                                                                            original(self, ep))[1])
    motor, _ = _viver(202, "comedouro")
    n = len(todos)
    assert n > 0
    orq.conferir_replay(motor, _viver.fab[1], 202, motor.log.para_jsonl())
    assert todos[n:] == todos[:n]                                                # o replay codificou os mesmos, na mesma ordem


def test_t_me_1_a_visita_vazia_na_vida_tem_o_custo_da_ida(monkeypatch):
    todos: list = []
    original = M.Memoria.codificar_autobio
    monkeypatch.setattr(M.Memoria, "codificar_autobio", lambda self, ep: (todos.append(ep), original(self, ep))[1])
    _, reg = _viver(101, "comedouro")
    c = orq.cerebro_de(reg)
    visitas = [e for e in todos if e["origem"] == "visita"]
    assert visitas
    for e in visitas:
        m = c.motivos[e["decisao"]]
        assert m["consequencia"]["chegou"] and m["consequencia"]["comeu"] is None and m["escolha"][1] == "ponto"
        ida = next(f["r"] for f in m["fins"] if f["chave"] == m["escolha"])
        assert e["sigma"] == min(0, ida) and e["categoria"][2] == (e["sigma"] < 0) * -1
    # todo consumo vira episodio de consumo; nenhuma decisao sem consumo nem visita vira episodio sem passar o limiar
    consumos = [m for m in c.motivos if m["consequencia"] and m["consequencia"]["comeu"] is not None]
    assert len([e for e in todos if e["origem"] == "consumo"]) == len(consumos)
    for e in todos:
        if e["origem"] == "evento":
            afetivo = max(e["corpo_depois"][r] for r in M.AFETIVOS)
            assert abs(e["sigma"]) >= P.theta_sig or afetivo >= P.theta_afeto


def test_g2_separado_ligada_muda_so_a_vida_do_braco_que_a_liga():
    desligada = orq.viver("M3", "relapso", "longe_fixo", 101, 3, 16, conserto=True)
    ligada = _viver(101)
    estado = lambda v: json.dumps(orq.cerebro_de(v[1]).estado_interno(), sort_keys=True)   # noqa: E731
    assert estado(desligada) != estado(ligada)
    assert estado(desligada) == estado(orq.viver("M3", "relapso", "longe_fixo", 101, 3, 16, conserto=True))
    m2 = orq.viver("M2", "relapso", "longe_fixo", 101, 3, 16, conserto=True)
    assert orq.cerebro_de(m2[1]).cd.memoria_autobio is False and "autobio" not in orq.cerebro_de(m2[1]).m.mem.estado_interno()


def test_g2_separado_nada_fora_do_pacote_le_a_chave():
    donos_da_chave = {"digilab/config.py", "digilab/digibrain/adapt.py", "digilab/digibrain/mem.py"}
    achados = set()
    for pasta in ("digilab", "experiments", "web", "tools", "servidor", "digilab_fala_livre"):
        if not (RAIZ / pasta).exists():
            continue
        for f in (RAIZ / pasta).rglob("*"):
            if f.suffix in (".py", ".ts", ".tsx", ".js") and "node_modules" not in f.parts and "memoria_autobio" in f.read_text(
                    encoding="utf-8", errors="ignore"):
                achados.add(f.relative_to(RAIZ).as_posix())
    assert achados == donos_da_chave


# ------------------------------------------------------------------ G-MECANISMO, G-INT, G-SEM-DIRECAO, G-RECEPTOR
_DE_HOJE = [n for n, f in inspect.getmembers(tm, inspect.isfunction) if n.startswith("test_")]


@pytest.mark.parametrize("nome", _DE_HOJE)
def test_g_mecanismo_os_de_hoje_com_a_subchave_ligada(nome, monkeypatch):
    """cada teste de mecanismo de hoje (tests/test_digibrain_mecanismo.py) com as duas subchaves do cheiro e a `memoria_autobio`; o M-MEM
    que um teste monta a mao e poe no cerebro (o T-MOTIVO-1) nasce com a recente, como o do cerebro ligado (sem ela, o relogio falha alto)"""
    monkeypatch.setattr(tm, "CONFIG_DIGIBRAIN_LIGADA", LIGADA)
    monkeypatch.setattr(tm, "Memoria", lambda cm, inatos=None: M.Memoria(cm, inatos, autobio=True))
    getattr(tm, nome)()


def test_g_int_e_g_receptor_as_intencoes_e_os_receptores_de_hoje_na_vida_ligada():
    c = orq.cerebro_de(_viver(505)[1])
    fins = c.m.estado.fins
    assert set(fins) == set(orq.fins_do_estado("M3")) and fins["meta"] > 0
    assert all(set(m["afeto"]["urgencias"]) == set(c.m.sens.receptores) for m in c.motivos)
