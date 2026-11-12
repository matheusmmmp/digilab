"""A sonda das duas TVs (GOSTO_VISUAL, P1e; docs/ESPEC_GOSTO_VISUAL_P1.md, secao 7; docs/PLANO_ANALISE_V3_GOSTO_VISUAL.md).

- a segunda TV no motor: a ConfigDuasTVs desligada por padrao e com o status de cada campo; o `ligar_duas_tvs` falha alto sem a chave, sem
  a TV do jogo, sem o olhar no cerebro, duas vezes ou com perfis iguais; as duas a mesma distancia, em direcoes opostas, no raio da visao;
  a posicao pela rng propria `duas-tvs-posicao`, que nao toca nenhum outro fluxo; a TV da vida fora de cena;
- o G2: a vida com a sonda no meio (e no fim) sai igual, byte a byte, a vida sem a sonda (o log, o estado, o corpo, o mundo e o cerebro);
- a sonda em pets com genomas diferentes: o agrado lido segue o genoma, o controle tem o agrado inato igual nas duas, e o genoma muda o
  que a copia faz; a janela tick a tick e igual a janela inteira;
- as medidas (`metrics.medidas_duas_tvs`, `metrics.familiarizacao_tv`) e a falha alto delas;
- o orquestrador: a trava (o plano ainda PROPOSTO recusa o piloto e a run), a fumaca com as sementes dos testes e a faixa reservada.
Sementes: as dos testes (101, 202, 303) e as derivadas delas. Nenhuma vida da faixa roda aqui.
"""
from __future__ import annotations

import copy
import json
import sys
from dataclasses import fields
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v3_gosto_visual as R  # noqa: E402
import sonda_duas_tvs as sd  # noqa: E402
from digilab import metrics as M  # noqa: E402
from digilab.config import (CANAIS_TELA, CONFIG_DUAS_TVS, CONFIG_DUAS_TVS_LIGADA, CONFIG_PADRAO, CONFIG_TV_LIGADA,  # noqa: E402
                            PARAMETROS_DUAS_TVS, ConfigDuasTVs)
from digilab.genoma_visao import GenomaVisao, genoma_visao_vazio  # noqa: E402
from digilab.tv import IDS_DUAS_TVS, ID_TV, TVFixa, TVSemChave  # noqa: E402

C = CONFIG_TV_LIGADA.escala
GOSTA_A = GenomaVisao({c: C // 5 for c in CANAIS_TELA}, {c: C // 3 for c in CANAIS_TELA})
GOSTA_B = GenomaVisao({c: 4 * C // 5 for c in CANAIS_TELA}, {c: C // 3 for c in CANAIS_TELA})


def _j(x) -> str:
    return json.dumps(x, sort_keys=True, default=str)


def _foto(m) -> dict:
    c = sd.cerebro_da_copia(m)
    return {"log": m.log.para_jsonl(), "estado": _j(m.estado()), "corpo": _j(m.corpo.para_dict()), "mundo": _j(m.resumo_mundo_fisico()),
            "cerebro": _j(c.estado_interno()), "motivos": _j(c.motivos), "rng": _j(m._rng_politica.getstate())}


def _unidade(semente: int) -> dict:
    return R.unidades([semente], 1)[0]


def _copia(semente: int = 202, dono: str = "agitado", dias: int = 3, genoma=None):
    """a vida de teste e a copia dela no momento da sonda do ultimo dia (pelo replay)"""
    u = _unidade(semente)
    if genoma is None:
        m, fab, _ = R.viver("proprio", dono, u, dias)
    else:
        fab = R.fabricas(u["semente"], genoma)
        fp, fm = fab
        m = fm(fp(CONFIG_PADRAO), CONFIG_PADRAO, u["semente"])
        _cuidar(m, dias)
    t = dict(sd.si.momentos(m, dias))[dias - 1]
    return m, fab, u, sd.copia_em(m, fab, u["semente"], t)


def _cuidar(m, dias: int) -> None:
    """o dono `nenhum` da vida do plano, para um genoma dado"""
    from digilab.events import AcaoUsuario
    from digilab.mundo import centro_da_celula
    x, y = centro_da_celula(R.orq.CM.layout.comedouro, R.orq.CM)
    for h in range(dias * 24):
        m.avancar(R.HORA)
        if h % 3 == 0:
            m.deixar_comida("racao", x, y)
        if h % 5 == 2 and not m.estado()["dormindo"]:
            m.observar(AcaoUsuario.ACARICIAR)


@pytest.fixture(scope="module")
def copia_202():
    return _copia()


# ================================================================== a config e a segunda TV no motor
def test_a_config_das_duas_tvs_e_desligada_e_cada_campo_tem_status():
    assert not CONFIG_DUAS_TVS.ligada and CONFIG_DUAS_TVS_LIGADA.ligada
    assert set(PARAMETROS_DUAS_TVS) == {f.name for f in fields(ConfigDuasTVs)}
    assert all(st == "PROPOSTO" and "SEM FONTE" in fonte for st, fonte in PARAMETROS_DUAS_TVS.values())
    for ruim in ({"ligada": 1}, {"distancia_celulas": 0}, {"tentativas": 17}, {"tentativas": -1}):
        with pytest.raises((TypeError, ValueError)):
            ConfigDuasTVs(**ruim)
    assert CONFIG_DUAS_TVS_LIGADA.distancia_celulas * R.orq.CM.sub <= R.orq.CM.raio_visao_celulas * R.orq.CM.sub


def test_a_tv_fixa_passa_sempre_o_perfil_e_falha_alto_fora_da_escala():
    tv = TVFixa(sd.PERFIL_A, C, 10, 20)
    assert tv.em(0) == tv.em(9999) == dict(zip(CANAIS_TELA, sd.PERFIL_A)) and tv.programa_em(5) is None
    assert tv.resumo() == {"x": 10, "y": 20, "fonte": "fixa", "perfil": list(sd.PERFIL_A)}
    for ruim in ((C + 1,) * 7, (0,) * 6, (0.5,) * 7):
        with pytest.raises(ValueError):
            TVFixa(ruim, C, 0, 0)
    with pytest.raises(ValueError):
        tv.em(-1)


def test_ligar_duas_tvs_falha_alto_sem_a_chave_duas_vezes_e_com_perfis_iguais(copia_202):
    _, _, _, base = copia_202
    m = copy.deepcopy(base)
    with pytest.raises(TVSemChave):
        m.ligar_duas_tvs(CONFIG_DUAS_TVS, (sd.PERFIL_A, sd.PERFIL_B), 0)
    with pytest.raises(ValueError):
        m.ligar_duas_tvs(CONFIG_DUAS_TVS_LIGADA, (sd.PERFIL_A, sd.PERFIL_A), 0)
    with pytest.raises(ValueError):
        m.ligar_duas_tvs(CONFIG_DUAS_TVS_LIGADA, (sd.PERFIL_A, sd.PERFIL_B), -1)
    m.ligar_duas_tvs(CONFIG_DUAS_TVS_LIGADA, (sd.PERFIL_A, sd.PERFIL_B), 0)
    with pytest.raises(TVSemChave):
        m.ligar_duas_tvs(CONFIG_DUAS_TVS_LIGADA, (sd.PERFIL_A, sd.PERFIL_B), 1)


def test_ligar_duas_tvs_exige_o_olhar_no_cerebro_e_a_tv_do_jogo():
    import test_gosto_visual_mundo as T
    m = T.fabrica()(T.Fixa(), T.CFG, 101)                      # um pet sem o gancho `olhando_tela`
    m.avancar(30)
    with pytest.raises(TVSemChave, match="olhar"):
        m.ligar_duas_tvs(CONFIG_DUAS_TVS_LIGADA, (sd.PERFIL_A, sd.PERFIL_B), 0)
    livre = T.fabrica(T.TV_LIVRE)(T.Fixa(), T.CFG, 101)
    with pytest.raises(TVSemChave, match="grade"):
        livre.ligar_duas_tvs(CONFIG_DUAS_TVS_LIGADA, (sd.PERFIL_A, sd.PERFIL_B), 0)
    sem_tv = T.fabrica(T.CONFIG_TV, T.CONFIG_TELA)(T.Fixa(), T.CFG, 101)
    with pytest.raises(TVSemChave):
        sem_tv.ligar_duas_tvs(CONFIG_DUAS_TVS_LIGADA, (sd.PERFIL_A, sd.PERFIL_B), 0)


def test_as_duas_tvs_a_mesma_distancia_opostas_a_vista_e_a_tv_da_vida_fora(copia_202):
    _, _, _, base = copia_202
    m = copy.deepcopy(base)
    pos = m.ligar_duas_tvs(CONFIG_DUAS_TVS_LIGADA, (sd.PERFIL_A, sd.PERFIL_B), 0)
    px, py = m.pet
    a, b = (pos["tvs"][i] for i in IDS_DUAS_TVS)
    assert a["perfil"] == list(sd.PERFIL_A) and b["perfil"] == list(sd.PERFIL_B)
    assert (a["x"] - px, a["y"] - py) == (px - b["x"], py - b["y"])                     # opostas, a mesma distancia
    linhas = m._linhas_tela()
    assert [x[0] for x in linhas] == list(IDS_DUAS_TVS) and linhas[0][3] == linhas[1][3] <= m._raio_visao
    assert ID_TV not in [x[0] for x in linhas]
    for _ in range(sd.JANELA_TICKS):
        m.avancar(1)
        assert m.tv_olhada() in (None, *IDS_DUAS_TVS)
    assert set(m.resumo_mundo_fisico()["duas_tvs"]) == set(IDS_DUAS_TVS)
    assert m.estado()["tv"]["duas_tvs"] == list(IDS_DUAS_TVS)


def test_a_posicao_pela_rng_propria_nao_toca_outro_fluxo(copia_202):
    _, _, _, base = copia_202
    vistas = set()
    for r in range(6):
        m1, m2 = copy.deepcopy(base), copy.deepcopy(base)
        antes = (_j(m1.resumo_mundo_fisico()["rngs"]), _j(m1._rng_politica.getstate()), _j(m1.mundo.tv.rng.getstate()))
        p1 = m1.ligar_duas_tvs(CONFIG_DUAS_TVS_LIGADA, (sd.PERFIL_A, sd.PERFIL_B), r)
        p2 = m2.ligar_duas_tvs(CONFIG_DUAS_TVS_LIGADA, (sd.PERFIL_A, sd.PERFIL_B), r)
        assert p1 == p2                                                                      # a mesma replica, a mesma posicao
        assert antes == (_j(m1.resumo_mundo_fisico()["rngs"]), _j(m1._rng_politica.getstate()), _j(m1.mundo.tv.rng.getstate()))
        vistas.add(p1["direcao_sorteada"])
    assert len(vistas) > 1                                                                   # replicas diferentes, posicoes diferentes


def test_a_janela_tick_a_tick_e_a_janela_inteira(copia_202):
    _, _, _, base = copia_202
    fotos = []
    for passo in (1, sd.JANELA_TICKS):
        m = copy.deepcopy(base)
        m.ligar_duas_tvs(CONFIG_DUAS_TVS_LIGADA, (sd.PERFIL_A, sd.PERFIL_B), 0)
        for _ in range(sd.JANELA_TICKS // passo):
            m.avancar(passo)
        f = _foto(m)
        f.pop("log")                                                                         # um avanco por tick no log da copia
        fotos.append(f)
    assert fotos[0] == fotos[1]


# ================================================================== o G2
def test_g2_a_vida_com_a_sonda_no_meio_e_no_fim_sai_igual_byte_a_byte():
    u = _unidade(303)
    sem, _, _ = R.viver("proprio", "calmo", u, 3)
    sondas = []

    def no_fim_do_dia(dia, m, fab):
        if dia >= 1:
            sondas.append(sd.sonda(m, fab, u["semente"], (dia,), 2))
    com, fab, _ = R.viver("proprio", "calmo", u, 3, fim_do_dia=no_fim_do_dia)
    assert len(sondas) == 2 and all(len(s["por_dia"][0]["replicas"]) == 2 for s in sondas if s["por_dia"][0]["tick"] is not None)
    final = sd.sonda(com, fab, u["semente"], (1, 2), 2)
    assert _foto(com) == _foto(sem)
    assert final["por_dia"][1] == sondas[1]["por_dia"][0]                                    # a sonda le o mesmo pet, no meio ou no fim
    assert _j(final) == _j(sd.sonda(com, fab, u["semente"], (1, 2), 2))                      # e e deterministica


def test_a_sonda_falha_alto_se_o_log_da_vida_mudar(monkeypatch):
    u = _unidade(101)
    vida, fab, _ = R.viver("proprio", "nenhum", u, 2)
    original = sd.ler_replica

    def mexe(c, r):
        vida.log.anexar(vida.log[-1])                                                         # a regra quebrada: a sonda tocou a vida
        return original(c, r)
    monkeypatch.setattr(sd, "ler_replica", mexe)
    with pytest.raises(RuntimeError, match="G2"):
        sd.sonda(vida, fab, u["semente"], (1,), 1)


# ================================================================== a sonda em genomas diferentes
@pytest.mark.parametrize("semente", [101, 202])
def test_o_agrado_lido_segue_o_genoma_e_o_controle_e_simetrico(semente):
    lidos = {}
    for nome, g in (("A", GOSTA_A), ("B", GOSTA_B), ("vazio", genoma_visao_vazio())):
        m, fab, u, _ = _copia(semente, genoma=g, dias=2)
        s = sd.sonda(m, fab, u["semente"], (1,), 3)
        reps = s["por_dia"][0]["replicas"]
        assert reps, "a sonda do dia 1 rodou"
        lidos[nome] = reps
        ag = reps[0]["agrado"]
        assert all(r["agrado"] == ag for r in reps)                                          # a sonda le sem andar o cerebro
        for r in reps:
            mm = M.medidas_duas_tvs(r, sd.JANELA_TICKS)
            assert mm["tempo_total"] == (r["ticks"]["A"] + r["ticks"]["B"]) / sd.JANELA_TICKS
        if nome == "A":
            assert ag["A"]["inato"] > ag["B"]["inato"]
        elif nome == "B":
            assert ag["B"]["inato"] > ag["A"]["inato"]
        else:
            assert ag["A"]["inato"] == ag["B"]["inato"]                                       # os perfis simetricos em volta do otimo vazio
    assert _j(lidos["A"]) != _j(lidos["B"])                                                  # o genoma muda o que a copia faz


def test_a_sonda_le_o_genoma_da_vida_proprio_ou_vazio():
    """o agrado que a sonda grava e o de um cerebro novo com o mesmo genoma (o inato nao anda na vida)"""
    from digilab.genoma_visao import genoma_visao
    u = _unidade(101)
    for tipo, g in (("proprio", genoma_visao(u["genoma"])), ("vazio", genoma_visao_vazio())):
        m, fab, _ = R.viver(tipo, "nenhum", u, 2)
        s = sd.sonda(m, fab, u["semente"], (1,), 1)
        novo = sd.agrados(R.fabricas(u["semente"], g)[0]())
        assert {k: v["inato"] for k, v in s["por_dia"][0]["replicas"][0]["agrado"].items()} == {k: v["inato"] for k, v in novo.items()}
        if tipo == "vazio":
            assert novo["A"]["inato"] == novo["B"]["inato"]


def test_os_perfis_da_sonda_nunca_passam_na_grade():
    from digilab.tv import TV
    for s in (101, 202, 303, 404, 505, _unidade(101)["semente"]):
        progs = TV(CONFIG_TV_LIGADA, s, 0, 0).programas
        assert sd.PERFIL_A not in progs and sd.PERFIL_B not in progs


# ================================================================== as medidas
def test_medidas_duas_tvs():
    assert M.medidas_duas_tvs({"ticks": {"A": 0, "B": 0}, "primeira": None}, 240) == \
        {"escolha": None, "tempo_relativo": None, "tempo_total": 0.0}
    assert M.medidas_duas_tvs({"ticks": {"A": 30, "B": 15}, "primeira": "B"}, 240) == \
        {"escolha": 0.0, "tempo_relativo": 30 / 45, "tempo_total": 45 / 240}
    for ruim in ({"ticks": {"A": 0, "B": 0}, "primeira": "A"}, {"ticks": {"A": 15, "B": 0}, "primeira": None},
                 {"ticks": {"A": 0, "B": 15}, "primeira": "A"}, {"ticks": {"A": 200, "B": 100}, "primeira": "A"},
                 {"ticks": {"A": -1, "B": 0}, "primeira": None}, {"ticks": {"A": 15, "B": 0}, "primeira": "C"}):
        with pytest.raises(ValueError):
            M.medidas_duas_tvs(ruim, 240)


def test_familiarizacao_tv():
    f = M.familiarizacao_tv([0.1, 0.05, 0.04, 0.05, 0.05, 0.04, 0.05], 0.02)
    assert f["estavel"] and abs(f["diferenca"]) < 1e-12 + 0.005
    assert not M.familiarizacao_tv([0.0, 0.0, 0.0, 0.0, 0.1, 0.1], 0.02)["estavel"]
    with pytest.raises(ValueError):
        M.familiarizacao_tv([0.1, 0.1, 0.1], 0.02)
    with pytest.raises(ValueError):
        M.familiarizacao_tv([0.1, 0.1, 0.1, 1.5], 0.02)


# ================================================================== o orquestrador e a faixa
def test_o_programa_do_dono_e_o_mais_perto_do_perfil_dele():
    progs = ((0,) * 7, (C,) * 7, (C // 5 + 1,) * 7)
    assert R.programa_do_dono("nenhum", progs) is None
    assert R.programa_do_dono("calmo", progs) == 2 and R.programa_do_dono("agitado", progs) == 1
    with pytest.raises(ValueError):
        R.programa_do_dono("outro", progs)


def test_a_faixa_esta_reservada_confirmada_e_nao_cruza_outra_nem_uma_queimada():
    faixas = [(lo, hi, f) for lo, hi, f in bv.FAIXAS_RESERVADAS if (lo, hi) == R.FAIXA]
    assert len(faixas) == 1 and "confirmada pelo coordenador, 2026-11-11" in faixas[0][2] and "PLANO_ANALISE_V3_GOSTO_VISUAL" in faixas[0][2]
    lo, hi = R.FAIXA
    for a, b, _ in bv.FAIXAS_RESERVADAS:
        if (a, b) != R.FAIXA:
            assert b < lo or a > hi, f"a faixa cruza {a}...{b}"
    for a, b, _ in bv.FAIXAS_QUEIMADAS:
        assert b < lo or a > hi
    assert all(lo <= b <= 89202 for b in R.BASES_PILOTO) and all(89303 <= b <= hi for b in R.BASES_RUN)
    us = R.unidades(R.BASES_PILOTO, R.K_PILOTO) + R.unidades(R.BASES_RUN, R.K_RUN)
    assert len({u["semente"] for u in us} | {u["genoma"] for u in us}) == 2 * len(us)
    for nome, bases in (("piloto.json", R.BASES_PILOTO), ("gosto_visual.json", R.BASES_RUN)):
        cfg = json.loads((RAIZ / "experiments" / "configs" / "v3_gosto_visual" / nome).read_text(encoding="utf-8"))
        assert tuple(cfg["unidades"]["bases"]) == bases and cfg["plano"] == R.PLANO


def test_a_trava_recusa_o_piloto_e_a_run_sem_o_plano_aprovado():
    texto = R._plano()
    assert not texto.splitlines()[2].startswith(R.MARCA_APROVADO)                            # o plano ainda e PROPOSTO
    for nome in ("piloto.json", "gosto_visual.json"):
        cfg = json.loads((RAIZ / "experiments" / "configs" / "v3_gosto_visual" / nome).read_text(encoding="utf-8"))
        with pytest.raises(RuntimeError, match="APROVADO"):
            R.modo_da_config(cfg)
    aprovado = texto.replace("**Status: PROPOSTO", "**Status: APROVADO pelo Matheus", 1)
    cfg = json.loads((RAIZ / "experiments" / "configs" / "v3_gosto_visual" / "piloto.json").read_text(encoding="utf-8"))
    assert R.modo_da_config(cfg, aprovado) == "piloto"
    with pytest.raises(ValueError):
        R.modo_da_config({**cfg, "dias": 13}, aprovado)
    with pytest.raises(bv.SementeSemPlano):
        R.modo_da_config({**cfg, "unidades": {"bases": [89101], "k": 2}}, aprovado)


def test_a_fumaca_do_orquestrador_com_as_sementes_dos_testes(tmp_path):
    cfg = {"fase": "gosto_visual", "plano": R.PLANO, "unidades": {"bases": [101], "k": 1}, "dias": 2}
    assert R.modo_da_config(cfg) == "fumaca"
    with pytest.raises(ValueError):
        R.rodar(cfg, tmp_path / "x", 5)
    out = R.rodar(cfg, tmp_path / "fumaca", 1, boot=20)
    r = out["resultado"]
    assert r["modo"] == "fumaca" and r["vidas"] == len(R.GENOMAS) * len(R.DONOS)
    assert set(r["principal"]["celulas"]) == {f"{g}|{d}" for g in R.GENOMAS for d in R.DONOS}
    for nome in ("meta.json", "medidas.json", "analise.json", "custo.json"):
        assert (tmp_path / "fumaca" / nome).exists()
    assert len(list((tmp_path / "fumaca" / "vidas").glob("*_sonda.json"))) == 6
    with pytest.raises(FileExistsError):
        R.rodar(cfg, tmp_path / "fumaca", 1, boot=20)
