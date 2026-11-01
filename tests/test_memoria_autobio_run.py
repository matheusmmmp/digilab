"""O orquestrador da C4 (experiments/run_v2_memoria_autobio.py; o adendo 9 do plano, A9.2 a A9.10): a config e a trava (o adendo 9
APROVADO; sem ele, a run e recusada; a faixa 77101...77505 em FAIXAS_RESERVADAS; as bases, o K, os dias; no maximo 4 processos; nada por
cima de uma pasta existente), os bracos, os fins conhecidos lidos da `estado.py` (a licao do #507), a conferencia da memoria de cada braco,
as medidas da lembranca e a conferencia da fala, a classe, o Holm do primario, as premissas, a leitura de A9.7, o artefato do poder, a
fumaca de ponta a ponta e o isolamento. Vidas so com as sementes dos testes (101...505): nenhuma da faixa 77xxx roda aqui.

A trava e testada com o cabecalho do adendo trocado no texto do plano (so no teste), nos dois sentidos: os testes passam com o adendo
PROPOSTO, como esta hoje, e com ele APROVADO, depois da marca do Matheus (a licao do #515). A faixa e testada do mesmo jeito: hoje ela nao
esta em FAIXAS_RESERVADAS (entra num commit proprio depois da aprovacao), e os testes passam antes e depois dele."""
from __future__ import annotations

import copy
import io
import json
import re
import sys
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402
import run_v2_longe_regular as lr  # noqa: E402
import run_v2_memoria_autobio as ma  # noqa: E402
from bancada.faixas import FAIXAS_QUEIMADAS, FAIXAS_RESERVADAS  # noqa: E402

CONFIGS = RAIZ / "experiments" / "configs" / "v2_memoria_autobio"
STATUS = re.compile(r"^\*\*Status: [^\n]*$", re.M)
PODER = RAIZ / "artifacts_v2_digibrain_prototipo" / "memoria_autobio" / "adendo9_poder.json"


def _cfg(nome: str = "memoria_autobio") -> dict:
    return json.loads((CONFIGS / f"{nome}.json").read_text(encoding="utf-8"))


def _plano_com_status(status: str) -> str:
    """o plano real com a linha do status do adendo 9 trocada (so o cabecalho do adendo 9; os outros adendos ficam como estao)"""
    plano = ma._plano()
    i = plano.index("\n## Adendo 9:")
    j = plano.index("\n### ", i)
    cab, n = STATUS.subn(status, plano[i:j])
    assert n == 1, "o cabecalho do adendo 9 tem de ter uma linha de status so"
    return plano[:i] + cab + plano[j:]


@pytest.fixture
def reservada(monkeypatch):
    """a faixa em FAIXAS_RESERVADAS (como fica depois do commit proprio da reserva; hoje so no teste)"""
    if not any((lo, hi_) == ma.FAIXA for lo, hi_, _ in ma.FAIXAS_RESERVADAS):
        monkeypatch.setattr(ma, "FAIXAS_RESERVADAS", ma.FAIXAS_RESERVADAS + ((*ma.FAIXA, "a C4 (so no teste)"),))


@pytest.fixture
def aprovado(monkeypatch, reservada):
    texto = _plano_com_status("**Status: APROVADO pelo Matheus em 2026-11-02 (so no teste).**")
    monkeypatch.setattr(ma, "_plano", lambda: texto)


@pytest.fixture
def proposto(monkeypatch, reservada):
    texto = _plano_com_status("**Status: PROPOSTO.** Só o Matheus o aprova.")
    monkeypatch.setattr(ma, "_plano", lambda: texto)


# ------------------------------------------------------------------ o que o adendo fixa
def test_o_desenho_e_o_do_adendo_9():
    assert ma.BASES == (77101, 77202, 77303, 77404, 77505) and ma.K_POR_BASE == 40 and ma.DIAS == 14 and ma.ORCAMENTO_POR_DIA == 16
    assert ma.PRIMARIO == "longe_fixo" and ma.GUARDA == "comedouro" and ma.LUGARES == ("longe_fixo", "comedouro", "longe")
    assert ma.BRACOS == ("REL", "SEM", "REC", "EMB", "RELsN", "REL+F") and len(ma.CELULAS) == 12
    assert ma.FAMILIA == (("REL", "SEM"), ("REL", "REC"), ("REL", "EMB")) and ma.ALFA_FAMILIA == 0.025
    assert ma.PREFIXO == "digibrain_prototipo" and ma.MARGEM == 0.032 and ma.MAX_PROCESSOS == 4
    assert ma.P_PESA_LIMIAR == 0.01 and ma.G_ELEGIVEL_EP == {"frac_vidas": 0.8, "episodios": 3}
    us = bv.unidades_derivadas(ma.BASES, ma.K_POR_BASE, ma.PREFIXO)
    assert len(us) == 200 and len(us) * len(ma.BRACOS) * len(ma.CELULAS) == 14400


def test_os_bracos_sao_o_m3_do_conserto_com_a_memoria_e_um_controle_cada():
    m3 = orq.config_do_braco("M3", conserto=True)
    for b in ma.BRACOS:
        c = orq.config_do_braco(b, conserto=True)
        assert c == replace(m3, memoria_autobio=True, controle_mem=ma.CONTROLE[b], **({"facetas_mem": True} if b == "REL+F" else {}))
        assert not c.intencao_suspensa and not c.credito_corrida and not c.redecidir_evento and c.cheiro_inato and c.intencao_cheiro
    assert {b: orq.config_do_braco(b, conserto=True).controle_mem for b in ma.BRACOS} == ma.CONTROLE
    assert [b for b in ma.BRACOS if orq.config_do_braco(b, conserto=True).facetas_mem] == list(ma.COM_FACETAS) == ["REL+F"]
    assert set(orq.SUBCHAVES_C4) == set(ma.BRACOS)


def test_os_bracos_da_c4_so_existem_nas_fases_do_conserto():
    for b in ma.BRACOS:
        with pytest.raises(ValueError, match="braco do modular"):
            orq.config_do_braco(b)


def test_a_faixa_proposta_nao_cruza_outra_reservada_nem_queimada():
    """hoje a faixa esta livre; depois do commit da reserva, a unica faixa que a cruza e ela mesma"""
    lo, hi_ = ma.FAIXA
    assert (lo, hi_) == (77101, 77505) and ma.BASES[0] == lo and ma.BASES[-1] == hi_
    for a, b, _ in FAIXAS_RESERVADAS + FAIXAS_QUEIMADAS:
        assert b < lo or a > hi_ or (a, b) == ma.FAIXA


# ------------------------------------------------------------------ a config e a trava
def test_a_trava_recusa_o_adendo_9_proposto(proposto):
    with pytest.raises(RuntimeError, match="nao esta APROVADO"):
        ma.modo_da_config(_cfg())
    assert ma.modo_da_config(_cfg("fumaca")) == "fumaca"                # a fumaca nao precisa do adendo


def test_o_plano_de_hoje_tem_o_adendo_9_e_a_trava_o_le():
    """hoje (o adendo 9 PROPOSTO e a faixa fora de FAIXAS_RESERVADAS) a run e recusada; depois da marca do Matheus e da reserva, ela segue
    o adendo"""
    plano = ma._plano()
    assert plano.count("\n## Adendo 9:") == 1
    aprovado_ = "**Status: APROVADO pelo Matheus" in plano[plano.index("\n## Adendo 9:"):]
    reservada_ = any((lo, hi_) == ma.FAIXA for lo, hi_, _ in FAIXAS_RESERVADAS)
    if aprovado_ and reservada_:
        assert ma.modo_da_config(_cfg()) == "memoria_autobio"
    else:
        with pytest.raises((RuntimeError, bv.SementeSemPlano)):
            ma.modo_da_config(_cfg())


def test_com_o_adendo_aprovado_e_a_faixa_reservada_a_config_segue_o_adendo(aprovado):
    assert ma.modo_da_config(_cfg()) == "memoria_autobio"


def test_a_trava_exige_a_faixa_reservada(monkeypatch, aprovado):
    monkeypatch.setattr(ma, "FAIXAS_RESERVADAS", tuple(f for f in ma.FAIXAS_RESERVADAS if f[0] != 77101))
    with pytest.raises(bv.SementeSemPlano, match="FAIXAS_RESERVADAS"):
        ma.modo_da_config(_cfg())


@pytest.mark.parametrize("bases", [[77101, 77202, 77303, 77404], [77101, 77202, 77303, 77404, 77506], [77505, 77404, 77303, 77202, 77101],
                                   [76101, 76202, 76303, 76404, 76505], [71101, 71202, 71303, 71404, 71505], [101, 77101],
                                   [101, 77202, 77303, 77404, 77505]])
def test_recusa_outra_base_e_sementes_fora_da_faixa(bases, aprovado):
    c = _cfg()
    c["unidades"]["bases"] = bases
    with pytest.raises(bv.SementeSemPlano):
        ma.modo_da_config(c)


def test_recusa_outro_k_outros_dias_outro_orcamento_e_outro_plano(aprovado):
    for chave, valor in (("k", 39), ("k", 30), ("dias", 13), ("dias", 15), ("orcamento_por_dia", 15), ("plano", "outro.md")):
        c = _cfg()
        if chave == "k":
            c["unidades"]["k"] = valor
        else:
            c[chave] = valor
        with pytest.raises(ValueError):
            ma.modo_da_config(c)
    c = _cfg()
    c["unidades"]["prefixo"] = "outro"
    with pytest.raises(ValueError, match="prefixo"):
        ma.modo_da_config(c)


def test_recusa_chave_a_mais_fase_errada_e_fumaca_com_dias_demais():
    with pytest.raises(ValueError, match="sobram"):
        ma.modo_da_config({**_cfg(), "inatos": {}})
    with pytest.raises(ValueError, match="fase"):
        ma.modo_da_config({**_cfg(), "fase": "redecidir_evento"})
    c = _cfg("fumaca")
    c["dias"] = 15
    with pytest.raises(ValueError, match="fumaca"):
        ma.modo_da_config(c)


def test_recusa_mais_de_4_processos_e_pasta_existente(tmp_path):
    with pytest.raises(ValueError, match="4 processos"):
        ma.rodar(_cfg("fumaca"), tmp_path / "x", 5)
    with pytest.raises(FileExistsError):
        ma.rodar(_cfg("fumaca"), tmp_path, 1)
    assert not (tmp_path / "x").exists()


def test_a_saida_da_run_nao_e_a_pasta_do_poder():
    assert ma.SAIDA == "artifacts_v2_digibrain_prototipo/memoria_autobio/run"
    assert (RAIZ / ma.SAIDA).parent == PODER.parent and (RAIZ / ma.SAIDA).name == "run"     # a licao do #531: nada sobre a pasta existir


def test_a_config_da_run_diz_o_k_e_as_bases_do_adendo():
    c = _cfg()
    assert c["unidades"] == {"bases": list(ma.BASES), "k": ma.K_POR_BASE, "prefixo": ma.PREFIXO} and c["dias"] == ma.DIAS
    assert c["plano"] == ma.PLANO and c["fase"] == ma.FASE and c["orcamento_por_dia"] == ma.ORCAMENTO_POR_DIA


# ------------------------------------------------------------------ os fins (a licao do #507)
def test_os_fins_conhecidos_sao_os_do_estado_com_a_config_de_cada_braco():
    for b in ma.BRACOS:
        assert ma.fins_conhecidos(b) == orq.fins_do_estado(b) == {"meta", "trocou", "sumiu", "desistiu", "achou"}


# ------------------------------------------------------------------ a memoria de cada braco (A9.10) e as medidas (A9.8)
_VIDAS: dict = {}


def _viver(braco: str, semente: int = 303, lugar: str = "longe_fixo", dias: int = 3):
    chave = (braco, semente, lugar, dias)
    if chave not in _VIDAS:
        _VIDAS[chave] = ma.viver(braco, "relapso", lugar, semente, dias, 16)
    return _VIDAS[chave]


def test_o_coletor_das_categorias_so_le_e_cobre_todo_episodio():
    """a vida com o coletor e a do `lr.viver` (o mesmo log e o mesmo estado interno, bit a bit), e o coletor tem a categoria de todo
    episodio codificado, inclusive dos que sairam antes do fim"""
    motor, reg, _, cats = _viver("REL")
    m2, r2, _ = lr.viver("REL", "relapso", "longe_fixo", 303, 3, 16)
    assert motor.log.para_jsonl() == m2.log.para_jsonl()
    assert json.dumps(reg.estado_interno(), sort_keys=True) == json.dumps(r2.estado_interno(), sort_keys=True)
    c = orq.cerebro_de(reg)
    ids = [m["consequencia"]["autobio"] for m in c.motivos if m["consequencia"] and m["consequencia"]["autobio"] is not None]
    assert set(cats) == set(ids) and len(ids) == c.m.mem.estado_interno()["autobio"]["proximo_id"]
    assert "agir" not in vars(c)                                       # o cerebro volta a ser o da fabrica


@pytest.mark.parametrize("braco", ma.BRACOS)
def test_a_conferencia_da_memoria_passa_em_cada_braco(braco):
    motor, reg, fab, cats = _viver(braco)
    c = orq.cerebro_de(reg)
    ma.conferir_memoria(braco, c)
    orq.conferir_replay(motor, fab, 303, motor.log.para_jsonl())
    med = ma.medidas_memoria(reg, 3, cats)
    assert med["decisoes"] == len(c.motivos) and 0 <= med["com_lembranca"] <= 1
    assert (med["facetas"] is not None) == (braco == "REL+F") and ("faceta" in med["decidiu"]) == (braco == "REL+F")
    if braco == "SEM":
        assert med["com_lembranca"] == 0 and med["decidiu"]["memoria"] == 0 and med["decidiu"]["lembranca"] == 0
    else:
        assert med["com_lembranca"] > 0
    if braco == "RELsN":
        assert med["episodios"]["negativos_guardados"] == 0 and med["lembrou_negativo"] == 0
    assert med["episodios"]["codificados"] > 0 and med["episodios"]["consolidacoes"] >= 2


def test_a_conferencia_da_memoria_falha_alto(monkeypatch):
    _, reg, _, _ = _viver("REL")
    c = orq.cerebro_de(reg)
    with pytest.raises(RuntimeError, match="subchaves"):
        ma.conferir_memoria("SEM", c)                                   # o REL lido como o SEM: o controle_mem nao e o do braco
    falso = SimpleNamespace(cd=replace(c.cd, controle_mem="sem"), inatos=c.inatos, m=c.m, motivos=copy.deepcopy(c.motivos))
    with pytest.raises(RuntimeError, match="SEM: a decisao"):
        ma.conferir_memoria("SEM", falso)                               # o registro do REL tem lembranca: o SEM nao pode ter
    m = next(x for x in falso.motivos if x["lembranca"]["recuperado"] is not None)
    falso.cd = c.cd
    m["sondas"]["lembranca_decidiu"], m["lembranca"]["L"] = True, None
    with pytest.raises(RuntimeError, match="sem a lembranca, o L ou a unidade"):
        ma.conferir_memoria("REL", falso)
    falso.motivos = copy.deepcopy(c.motivos)
    m = next(x for x in falso.motivos if x["lembranca"]["recuperado"] is not None)
    m["lembranca"]["sim"] = 0
    with pytest.raises(RuntimeError, match="abaixo de sim_min"):
        ma.conferir_memoria("REL", falso)
    falso.motivos = copy.deepcopy(c.motivos)
    falso.motivos[0].pop("lembranca")
    with pytest.raises(RuntimeError, match="sem a lembranca no motivo"):
        ma.conferir_memoria("REL", falso)


def test_a_conferencia_da_memoria_falha_alto_no_rel_sem_neg_e_no_rec():
    _, reg, _, _ = _viver("RELsN")
    c = orq.cerebro_de(reg)
    falso = SimpleNamespace(cd=c.cd, inatos=c.inatos, m=c.m, motivos=copy.deepcopy(c.motivos))
    next(x for x in falso.motivos if x["lembranca"]["recuperado"] is not None)["lembranca"]["sigma"] = -1
    with pytest.raises(RuntimeError, match="sigma < 0"):
        ma.conferir_memoria("RELsN", falso)
    _, reg, _, _ = _viver("REC")
    c = orq.cerebro_de(reg)
    falso = SimpleNamespace(cd=c.cd, inatos=c.inatos, m=c.m, motivos=copy.deepcopy(c.motivos))
    next(x for x in falso.motivos if x["lembranca"]["recuperado"] is not None)["lembranca"]["sim"] = 900
    with pytest.raises(RuntimeError, match="nao olha o contexto"):
        ma.conferir_memoria("REC", falso)


def test_a_conferencia_da_fala_sustenta_o_verdadeiro_e_recusa_a_causa_sem_a_sonda():
    _, reg, _, cats = _viver("REL")
    f = ma.conferencia_da_fala(orq.cerebro_de(reg), cats)
    a = f["alegacoes"]
    assert a["verdadeira"]["n"] > 0 and a["verdadeira"]["sustentadas"] == a["verdadeira"]["n"]
    assert a["causa_falsa"]["n"] > 0 and a["causa_falsa"]["sustentadas"] == 0           # a causa sem a sonda nunca e sustentada
    assert a["causa_verdadeira"]["sustentadas"] == a["causa_verdadeira"]["n"]
    assert a["causa_verdadeira"]["n"] + a["causa_falsa"]["n"] == a["verdadeira"]["n"]
    assert a["faceta_verdadeira"]["n"] == a["faceta_falsa"]["n"] == 0                   # sem as facetas, nenhuma alegacao de faceta


def test_a_conferencia_da_fala_nas_facetas():
    _, reg, _, cats = _viver("REL+F", 101)
    c = orq.cerebro_de(reg)
    a = ma.conferencia_da_fala(c, cats)["alegacoes"]
    assert a["faceta_verdadeira"]["n"] == len(c.m.pers.mudancas) > 0
    assert a["faceta_verdadeira"]["sustentadas"] == a["faceta_verdadeira"]["n"] and a["faceta_falsa"]["sustentadas"] == 0


def test_a_conferencia_da_fala_falha_alto_sem_a_categoria():
    _, reg, _, cats = _viver("REL")
    c = orq.cerebro_de(reg)
    rid = next(m["lembranca"]["recuperado"] for m in c.motivos if m["lembranca"]["recuperado"] is not None)
    with pytest.raises(RuntimeError, match="fora do coletor"):
        ma.conferencia_da_fala(c, {i: x for i, x in cats.items() if i != rid})


def test_a_conferencia_da_fala_no_sem_so_tem_alegacao_falsa():
    _, reg, _, cats = _viver("SEM")
    a = ma.conferencia_da_fala(orq.cerebro_de(reg), cats)["alegacoes"]
    assert a["verdadeira"]["n"] == 0 and a["falsa"]["n"] > 0 and a["falsa"]["sustentadas"] == 0


# ------------------------------------------------------------------ a classe, o Holm, as premissas e a leitura (A9.4 a A9.7)
def _ic(lo, hi_):
    return {"ic_inferior": lo, "ic_superior": hi_, "motivo": None}


@pytest.mark.parametrize("lo,hi_,esperada", [(-0.03, 0.03, "≈ 0"), (0.001, 0.031, "≈ 0"), (0.001, 0.033, "> 0"), (-0.05, -0.033, "< 0"),
                                             (-0.033, 0.005, "indeterminado"), (-0.04, -0.001, "< 0")])
def test_a_classe_usa_a_margem_do_adendo_9(lo, hi_, esperada):
    assert ma.classe(_ic(lo, hi_))["classe"] == esperada


def _registros(efeitos: dict, n: int = 12, lugar: str = "longe_fixo", episodios: int = 5, pesa: float = 0.1) -> list[dict]:
    """vidas falsas: a taxa por episodio do REL e 0,5 + o efeito do braco contra ele, com um ruido fixo por unidade"""
    out = []
    for k in range(n):
        ruido = ((k * 37) % 11 - 5) / 1000
        for d in ma.DONOS:
            for b in ("REL",) + tuple(efeitos):
                taxa = 0.5 + ruido * (k % 3) if b == "REL" else 0.5 - efeitos[b] + ruido
                out.append({"braco": b, "dono": d, "lugar": lugar, "semente": 1000 + k, "base": (101, 202, 303, 404, 505)[k % 5],
                            "episodios_fome": {"n": episodios, "taxa": taxa},
                            "memoria": {"decidiu": {"memoria": pesa + ruido}}})
    return out


BOOT = {"reamostragens": 200, "semente": 4242, "nivel": 0.95}


def test_o_primario_e_o_holm_sobre_os_tres():
    p = ma.primario(_registros({"SEM": 0.08, "REC": 0.06, "EMB": 0.0}), BOOT)
    assert set(p) == {"REL - SEM", "REL - REC", "REL - EMB"}
    assert p["REL - SEM"]["passa"] and p["REL - REC"]["passa"] and not p["REL - EMB"]["passa"]
    assert sorted(x["holm"]["ordem"] for x in p.values()) == [1, 2, 3]
    assert all(x["holm"]["limiar"] in (0.025 / 3, 0.025 / 2, 0.025) for x in p.values())


def test_as_premissas_de_a9_5():
    ok = ma.premissas(_registros({"SEM": 0.0, "REC": 0.0, "EMB": 0.0}))
    assert ok["P-PESA"]["passa"] and ok["G-ELEGIVEL-EP"]["passa"] and ok["conclusivo"]
    assert not ma.premissas(_registros({"SEM": 0.0, "REC": 0.0, "EMB": 0.0}, pesa=0.005))["P-PESA"]["passa"]
    assert not ma.premissas(_registros({"SEM": 0.0, "REC": 0.0, "EMB": 0.0}, episodios=2))["conclusivo"]


def _prim(sem: tuple, rec: tuple, emb: tuple) -> dict:
    return {f"REL - {b}": {"passa": p, "classe": {"classe": c}, "ressalva_assimetria": None}
            for b, (p, c) in (("SEM", sem), ("REC", rec), ("EMB", emb))}


def _gua(classe: str) -> dict:
    return {"classe": {"classe": classe}, "menor_que_0": classe == "< 0"}


@pytest.mark.parametrize("sem,rec,emb,gua,conclusivo,linha", [
    ((True, "> 0"), (True, "> 0"), (True, "> 0"), "≈ 0", False, 1),
    ((True, "> 0"), (False, "≈ 0"), (False, "≈ 0"), "< 0", True, 2),
    ((True, "> 0"), (True, "≈ 0"), (True, "> 0"), "indeterminado", True, 3),          # o Holm manda: "passa" le "> 0"
    ((True, "> 0"), (False, "≈ 0"), (True, "> 0"), "≈ 0", True, 4),
    ((True, "> 0"), (False, "indeterminado"), (False, "indeterminado"), "> 0", True, 4),
    ((False, "≈ 0"), (False, "≈ 0"), (False, "≈ 0"), "≈ 0", True, 5),
    ((False, "≈ 0"), (True, "> 0"), (False, "≈ 0"), "< 0", True, 2),
    ((False, "< 0"), (False, "< 0"), (False, "≈ 0"), "≈ 0", True, 6),
    ((False, "indeterminado"), (False, "> 0"), (False, "≈ 0"), "≈ 0", True, 7)])
def test_a_leitura_de_a9_7(sem, rec, emb, gua, conclusivo, linha):
    r = ma.leitura(_prim(sem, rec, emb), {"conclusivo": conclusivo}, _gua(gua))
    assert r["linha"] == linha and r["o_que_se_faz"]


def test_a_margem_e_o_k_sao_os_do_artefato_do_poder():
    d = json.loads(PODER.read_text(encoding="utf-8"))
    k = len(ma.BASES) * ma.K_POR_BASE
    assert round(d["por_k"][f"K={k}"]["margem"], 3) == ma.MARGEM
    assert d["por_k"][f"K={k}"]["vidas"] == k * len(ma.BRACOS) * len(ma.CELULAS) and d["vidas_por_unidade_c4"] == 72
    assert d["bracos_c4"] == list(ma.BRACOS) and d["alfa_familia"] == ma.ALFA_FAMILIA and d["n_familia"] == len(ma.FAMILIA)
    fontes = {Path(p).parent.parent.name + "/" + Path(p).name: sha for p, sha in d["fonte"].items()}
    assert fontes["longe_regular/medidas.json"].startswith("5a4fb207") and fontes["redecidir_evento/medidas.json"].startswith("d5b7c974")


# ------------------------------------------------------------------ a fumaca de ponta a ponta
def test_a_fumaca_roda_de_ponta_a_ponta(tmp_path):
    cfg = copy.deepcopy(_cfg("fumaca"))
    cfg["unidades"] = {"bases": [101], "k": 1, "prefixo": "digibrain_prototipo"}
    cfg["dias"] = 1
    pasta = tmp_path / "fumaca"
    r = ma.rodar(cfg, pasta, 1, CONFIGS / "fumaca.json")
    assert r["meta"]["modo"] == "fumaca" and len(r["registros"]) == 72 and r["resultado"]["vidas"] == 72
    meta = json.loads((pasta / "meta.json").read_text(encoding="utf-8"))
    assert set(meta["artefatos_sha256"]) == {"medidas.json", "resultado.json"}
    for nome, sha in meta["artefatos_sha256"].items():
        assert bv._sha(pasta / nome) == sha
    assert meta["bracos"]["SEM"]["controle_mem"] == "sem" and meta["bracos"]["REL+F"]["memoria_autobio"] is True
    assert meta["fins_conhecidos"]["REL"] == sorted(ma.fins_conhecidos("REL"))
    assert len(list((pasta / "vidas").rglob("*.jsonl"))) == 72
    res = json.loads((pasta / "resultado.json").read_text(encoding="utf-8"))
    assert {"primario", "guarda", "secundarias", "premissas", "leitura", "descritivo"} <= set(res)
    assert set(res["primario"]) == {"REL - SEM", "REL - REC", "REL - EMB"}
    assert set(res["descritivo"]) == {"lembranca", "episodios", "facetas", "fala", "corpo", "outros"}
    med = json.loads((pasta / "medidas.json").read_text(encoding="utf-8"))
    assert all((v["memoria"]["facetas"] is not None) == (v["braco"] == "REL+F") for v in med.values())
    with pytest.raises(FileExistsError):
        ma.rodar(cfg, pasta, 1)


def test_resumo_no_console_cp1252_nao_quebra(monkeypatch):
    """o print do resumo com '≈' num stdout cp1252 (console Windows) nao levanta (o #518)"""
    r = {"modo": "m", "vidas": 1, "primario": {}, "guarda": {}, "secundarias": {}, "premissas": {}, "leitura": "≈ 0,5"}
    buf = io.TextIOWrapper(io.BytesIO(), encoding="cp1252", errors="strict")
    monkeypatch.setattr("sys.stdout", buf)
    ma._imprimir_resumo(r)
    buf.flush()
    assert "2248" in buf.buffer.getvalue().decode("ascii")


# ------------------------------------------------------------------ o isolamento (a licao do #515)
def test_o_orquestrador_e_o_poder_nao_montam_o_digibrain():
    """so o orquestrador do prototipo cita o pacote do DigiBrain e a ConfigDigibrain; os dois arquivos novos passam por ele"""
    nomes = re.compile(r"\b(ConfigDigibrain\w*|CONFIG_DIGIBRAIN\w*)\b|digilab\.digibrain|from \.digibrain|from \.\.digibrain|import digibrain")
    for f in ("experiments/run_v2_memoria_autobio.py", "experiments/adendo9_poder_memoria_autobio.py"):
        assert not nomes.search((RAIZ / f).read_text(encoding="utf-8")), f


def test_o_orquestrador_nao_combina_a_c4_com_a_c2_nem_com_a_c3():
    """a MA-7: a C4 roda sem a corrida da C2 e sem a escolha segurada da C3 (o poder so le o artefato da run da C3, pelo caminho)"""
    texto = (RAIZ / "experiments/run_v2_memoria_autobio.py").read_text(encoding="utf-8")
    assert "credito_corrida" not in texto and "redecidir_evento" not in texto and "SUBCHAVES_C3" not in texto
    assert "credito_corrida" not in (RAIZ / "experiments/adendo9_poder_memoria_autobio.py").read_text(encoding="utf-8")


def _cerebro_falso(motivos: list, fins_estado: dict):
    estado = SimpleNamespace(fins=fins_estado)
    c = SimpleNamespace(cd=SimpleNamespace(intencao_suspensa=False), motivos=motivos, m=SimpleNamespace(estado=estado))
    return SimpleNamespace(_interna=c)


def test_conferir_fins_falha_alto_com_um_fim_desconhecido():
    m = {"fins": [{"chave": ["comer", "cheiro", None], "motivo": "inventado"}]}
    with pytest.raises(RuntimeError, match="dos conhecidos"):
        ma.conferir_fins("REL", _cerebro_falso([m], {}))
