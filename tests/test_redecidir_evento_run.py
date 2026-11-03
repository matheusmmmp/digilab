"""O orquestrador da C3 (experiments/run_v2_redecidir_evento.py; o adendo 8 do plano, A8.2 a A8.10): a config e a trava (o adendo 8
APROVADO; sem ele, a run e recusada; a faixa 76101...76505; as bases, o K, os dias; no maximo 4 processos; nada por cima de uma pasta
existente), os bracos, os fins conhecidos lidos da `estado.py` (a licao do #507), as trocas da LP-2, as medidas da escolha segurada, a
classe, a leitura de A8.7, o artefato do poder, a fumaca de ponta a ponta e o isolamento. Vidas so com as sementes dos testes (101...505):
nenhuma da faixa 76xxx roda aqui.

A trava e testada com o cabecalho do adendo trocado no texto do plano (so no teste), nos dois sentidos: os testes passam com o adendo
PROPOSTO, como esta hoje, e com ele APROVADO, depois da marca do Matheus (a licao do #515)."""
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
import run_v2_redecidir_evento as rd  # noqa: E402
from bancada.faixas import na_faixa_reservada  # noqa: E402

CONFIGS = RAIZ / "experiments" / "configs" / "v2_redecidir_evento"
STATUS = re.compile(r"^\*\*Status: [^\n]*$", re.M)


def _cfg(nome: str = "redecidir_evento") -> dict:
    return json.loads((CONFIGS / f"{nome}.json").read_text(encoding="utf-8"))


def _plano_com_status(status: str) -> str:
    """o plano real com a linha do status do adendo 8 trocada (so o cabecalho do adendo 8; os outros adendos ficam como estao)"""
    plano = rd._plano()
    i = plano.index("\n## Adendo 8:")
    j = plano.index("\n### ", i)
    cab, n = STATUS.subn(status, plano[i:j])
    assert n == 1, "o cabecalho do adendo 8 tem de ter uma linha de status so"
    return plano[:i] + cab + plano[j:]


@pytest.fixture
def aprovado(monkeypatch):
    texto = _plano_com_status("**Status: APROVADO pelo Matheus em 2026-11-02 (so no teste).**")
    monkeypatch.setattr(rd, "_plano", lambda: texto)


@pytest.fixture
def proposto(monkeypatch):
    texto = _plano_com_status("**Status: PROPOSTO.** Só o Matheus o aprova.")
    monkeypatch.setattr(rd, "_plano", lambda: texto)


# ------------------------------------------------------------------ o que o adendo fixa
def test_o_desenho_e_o_do_adendo_8():
    assert rd.BASES == (76101, 76202, 76303, 76404, 76505) and rd.K_POR_BASE == 30 and rd.DIAS == 14 and rd.ORCAMENTO_POR_DIA == 16
    assert rd.PRIMARIO == "longe_fixo" and rd.GUARDA == "comedouro" and rd.LUGARES == ("longe_fixo", "comedouro", "longe")
    assert rd.BRACOS == ("M3", "M3R", "M2", "M2R") and rd.PARES == (("M3R", "M3"), ("M2R", "M2")) and len(rd.CELULAS) == 12
    assert rd.PREFIXO == "digibrain_prototipo" and rd.MARGEM == 0.025 and rd.MAX_PROCESSOS == 4
    assert rd.P_SEGURA_LIMIAR == 0.10 and rd.P_EVENTO_LIMIAR == 0.25 and rd.G_ELEGIVEL_EP == {"frac_vidas": 0.8, "episodios": 3}
    us = bv.unidades_derivadas(rd.BASES, rd.K_POR_BASE, rd.PREFIXO)
    assert len(us) == 150 and len(us) * len(rd.BRACOS) * len(rd.CELULAS) == 7200


def test_os_bracos_r_sao_o_m3_e_o_m2_do_conserto_com_a_subchave_e_nada_mais():
    m3, m3r, m2, m2r = (orq.config_do_braco(b, conserto=True) for b in ("M3", "M3R", "M2", "M2R"))
    assert orq.SUBCHAVES_C3 == {"M3R": {**orq.SUBCHAVES_CONSERTO["M3"], "redecidir_evento": True},
                                "M2R": {**orq.SUBCHAVES_CONSERTO["M2"], "redecidir_evento": True}}
    assert m3r == replace(m3, redecidir_evento=True) and m2r == replace(m2, redecidir_evento=True)
    assert not m3.redecidir_evento and not m2.redecidir_evento
    for c in (m3, m3r, m2, m2r):
        assert not c.intencao_suspensa and not c.credito_corrida and c.cheiro_inato and c.intencao_cheiro
    assert m3r.m_mem and not m2r.m_mem


def test_os_bracos_r_so_existem_nas_fases_do_conserto():
    for b in ("M3R", "M2R"):
        with pytest.raises(ValueError, match="braco do modular"):
            orq.config_do_braco(b)


def test_a_faixa_esta_reservada():
    assert na_faixa_reservada(76101) and na_faixa_reservada(76505) and not na_faixa_reservada(76506) and not na_faixa_reservada(76100)
    rd.exigir_faixa_reservada()


# ------------------------------------------------------------------ a config e a trava
def test_a_trava_recusa_o_adendo_8_proposto(proposto):
    with pytest.raises(RuntimeError, match="nao esta APROVADO"):
        rd.modo_da_config(_cfg())
    assert rd.modo_da_config(_cfg("fumaca")) == "fumaca"                # a fumaca nao precisa do adendo


def test_o_plano_de_hoje_tem_o_adendo_8_e_a_trava_le_o_cabecalho_dele():
    """com o adendo 8 PROPOSTO (hoje), a run e recusada; depois da marca do Matheus, ela segue o adendo"""
    plano = rd._plano()
    assert plano.count("\n## Adendo 8:") == 1
    if "**Status: APROVADO pelo Matheus" in plano[plano.index("\n## Adendo 8:"):]:
        assert rd.modo_da_config(_cfg()) == "redecidir_evento"
    else:
        with pytest.raises(RuntimeError, match="nao esta APROVADO"):
            rd.modo_da_config(_cfg())


def test_com_o_adendo_aprovado_a_config_segue_o_adendo(aprovado):
    assert rd.modo_da_config(_cfg()) == "redecidir_evento"


@pytest.mark.parametrize("bases", [[76101, 76202, 76303, 76404], [76101, 76202, 76303, 76404, 76506], [76505, 76404, 76303, 76202, 76101],
                                   [75101, 75202, 75303, 75404, 75505], [71101, 71202, 71303, 71404, 71505], [101, 76101],
                                   [101, 76202, 76303, 76404, 76505]])
def test_recusa_outra_base_e_sementes_fora_da_faixa(bases, aprovado):
    c = _cfg()
    c["unidades"]["bases"] = bases
    with pytest.raises(bv.SementeSemPlano):
        rd.modo_da_config(c)


def test_recusa_outro_k_outros_dias_outro_orcamento_e_outro_plano(aprovado):
    for chave, valor in (("k", 29), ("k", 60), ("dias", 13), ("dias", 15), ("orcamento_por_dia", 15), ("plano", "outro.md")):
        c = _cfg()
        if chave == "k":
            c["unidades"]["k"] = valor
        else:
            c[chave] = valor
        with pytest.raises(ValueError):
            rd.modo_da_config(c)
    c = _cfg()
    c["unidades"]["prefixo"] = "outro"
    with pytest.raises(ValueError, match="prefixo"):
        rd.modo_da_config(c)


def test_recusa_chave_a_mais_fase_errada_e_fumaca_com_dias_demais():
    with pytest.raises(ValueError, match="sobram"):
        rd.modo_da_config({**_cfg(), "inatos": {}})
    with pytest.raises(ValueError, match="fase"):
        rd.modo_da_config({**_cfg(), "fase": "habito_intencao"})
    c = _cfg("fumaca")
    c["dias"] = 15
    with pytest.raises(ValueError, match="fumaca"):
        rd.modo_da_config(c)


def test_a_trava_exige_a_faixa_reservada(monkeypatch, aprovado):
    monkeypatch.setattr(rd, "FAIXAS_RESERVADAS", tuple(f for f in rd.FAIXAS_RESERVADAS if f[0] != 76101))
    with pytest.raises(bv.SementeSemPlano, match="FAIXAS_RESERVADAS"):
        rd.modo_da_config(_cfg())


def test_recusa_mais_de_4_processos_e_pasta_existente(tmp_path):
    with pytest.raises(ValueError, match="4 processos"):
        rd.rodar(_cfg("fumaca"), tmp_path / "x", 5)
    with pytest.raises(FileExistsError):
        rd.rodar(_cfg("fumaca"), tmp_path, 1)
    assert not (tmp_path / "x").exists()


def test_a_saida_da_run_nao_e_a_pasta_do_poder():
    assert rd.SAIDA == "artifacts_v2_digibrain_prototipo/redecidir_evento/run"
    assert (RAIZ / rd.SAIDA).parent == (RAIZ / "artifacts_v2_digibrain_prototipo" / "redecidir_evento")
    # a run da C3 (#527) esta na main: a SAIDA e a pasta `run`, separada da pasta-mae do adendo8_poder.json
    assert (RAIZ / rd.SAIDA).name == "run"
    assert (RAIZ / rd.SAIDA).parent.name == "redecidir_evento"
    assert (RAIZ / rd.SAIDA) != (RAIZ / rd.SAIDA).parent


# ------------------------------------------------------------------ os fins (a licao do #507)
def test_os_fins_conhecidos_sao_os_do_estado_com_a_config_de_cada_braco():
    for b in rd.BRACOS:
        assert rd.fins_conhecidos(b) == orq.fins_do_estado(b) == {"meta", "trocou", "sumiu", "desistiu", "achou"}


# ------------------------------------------------------------------ as trocas da LP-2 e a escolha segurada
def _mot(escolha, reflexo=False, acao="comer"):
    return {"escolha": escolha, "reflexo": reflexo, "acao": "dormir" if reflexo else acao}


def test_as_trocas_por_decisao_nao_contam_a_retomada_e_separam_o_dormir_sorteado():
    busca, dormir, chamar = ["comer", "cheiro", None], ["dormir", None, None], ["chamar", None, None]
    ms = [_mot(busca), _mot(dormir, True), _mot(dormir, True), _mot(busca)]       # o T-RD-3: zero trocas
    assert rd.trocas_lp2(ms) == {"total": 0, "dormir_sorteio": 0, "outra_unidade": 0}
    ms += [_mot(dormir, acao="dormir"), _mot(chamar, acao="chamar"), _mot(chamar, acao="chamar")]
    assert rd.trocas_lp2(ms) == {"total": 2, "dormir_sorteio": 1, "outra_unidade": 1} and orq.trocas_por_decisao(ms) == 2


def _viver(braco: str, semente: int = 303, dias: int = 2):
    return lr.viver(braco, "relapso", "longe_fixo", semente, dias, 16)


def test_as_medidas_da_escolha_segurada_numa_vida_de_teste():
    motor, reg, _ = _viver("M3R")
    m = rd.medidas_redecidir(reg, 2)
    c = orq.cerebro_de(reg)
    assert m["ligada"] and m["decisoes"] == len(c.motivos) and m["seguradas"] == c.m.estado.seguradas > 0
    assert m["frac_seguradas"] == m["seguradas"] / m["sem_reflexo"] and 0 < m["frac_seguradas"] < 1
    s = m["sequencias"]
    assert s["tetos"] == c.m.estado.tetos and s["decisoes_nas_fechadas"] + s["aberta_no_fim"] == m["seguradas"] and s["fechadas"] > 0
    ev = m["eventos"]
    assert ev["sorteadas_depois_da_primeira"] == len(c.motivos) - 1 - m["seguradas"]
    assert ev["por_evento"]["E-TETO"]["decisoes"] == s["tetos"]
    assert all(ev["por_evento"][e]["decisoes"] == c.m.estado.com_evento[e] for e in rd.EVENTOS)
    assert set(m["influencia_sorteadas"]) == set(rd.MODULOS)
    rd.conferir_fins("M3R", reg)


def test_nos_controles_os_campos_da_escolha_segurada_sao_none():
    _, reg, _ = _viver("M3")
    m = rd.medidas_redecidir(reg, 2)
    assert m["ligada"] is False and m["seguradas"] is None and m["sequencias"] is None and m["influencia_sorteadas"] is None
    assert m["trocas"]["total"] == orq.trocas_por_decisao(orq.cerebro_de(reg).motivos)


def test_as_medidas_falham_alto_com_o_teto_fora_do_m_estado():
    _, reg, _ = _viver("M2R")
    orq.cerebro_de(reg).m.estado.tetos += 1
    with pytest.raises(RuntimeError, match="teto"):
        rd.medidas_redecidir(reg, 2)


def test_a_vida_falha_alto_com_a_subchave_fora_do_braco(monkeypatch, tmp_path):
    original = orq.config_do_braco
    monkeypatch.setattr(orq, "config_do_braco", lambda b, g=None, c=False: replace(original(b, g, c), redecidir_evento=False))
    u = bv.unidades_derivadas([101], 1, rd.PREFIXO)[0]
    with pytest.raises(RuntimeError, match="nao e a do braco"):
        rd._vida({"dias": 1, "orcamento_por_dia": 16}, "M3R", "relapso", "longe_fixo", u, str(tmp_path))


# ------------------------------------------------------------------ a classe e a leitura (A8.6 e A8.7)
def _ic(lo, hi_):
    return {"ic_inferior": lo, "ic_superior": hi_, "motivo": None}


@pytest.mark.parametrize("lo,hi_,esperada", [(-0.02, 0.02, "≈ 0"), (0.001, 0.024, "≈ 0"), (0.001, 0.026, "> 0"), (-0.05, -0.026, "< 0"),
                                             (-0.026, 0.005, "indeterminado"), (-0.03, -0.001, "< 0")])
def test_a_classe_usa_a_margem_do_adendo_8(lo, hi_, esperada):
    assert rd.classe(_ic(lo, hi_))["classe"] == esperada


def _prim(passa: bool, classe: str) -> dict:
    return {"passa": passa, "classe": {"classe": classe}, "ressalva_assimetria": None}


def _gua(classe: str) -> dict:
    return {"classe": {"classe": classe}, "menor_que_0": classe == "< 0"}


@pytest.mark.parametrize("passa,cl_pr,cl_gua,cl_s1,conclusivo,trecho", [
    (True, "> 0", "≈ 0", "> 0", True, "nao precisa da memoria"), (True, "≈ 0", "indeterminado", "≈ 0", True, "passa pelo M-MEM"),
    (True, "> 0", "> 0", "indeterminado", True, "o S1 nao diz"), (True, "> 0", "< 0", "> 0", True, "atrapalha perto"),
    (False, "≈ 0", "< 0", "> 0", True, "nao e a causa"), (False, "< 0", "≈ 0", "> 0", True, "piora o pet"),
    (False, "indeterminado", "≈ 0", "> 0", True, "indeterminado"), (True, "> 0", "≈ 0", "> 0", False, "inconclusivo por premissa")])
def test_a_leitura_de_a8_7(passa, cl_pr, cl_gua, cl_s1, conclusivo, trecho):
    r = rd.leitura(_prim(passa, cl_pr), {"conclusivo": conclusivo}, _gua(cl_gua), {"classe": {"classe": cl_s1}})
    assert trecho in r["linha"]


def _registros_falsos(frac_seg: list[float], frac_teto: list[float], episodios: int = 5) -> list[dict]:
    out = []
    for k, (s, t) in enumerate(zip(frac_seg, frac_teto)):
        for d in rd.DONOS:
            for b in ("M3", "M3R"):
                out.append({"braco": b, "dono": d, "lugar": "longe_fixo", "semente": 1000 + k, "base": 101, "episodios_fome": {"n": episodios},
                            "redecidir": {"frac_seguradas": s if b == "M3R" else None,
                                          "sequencias": None if b == "M3" else {"frac_teto": t}}})
    return out


def test_as_premissas_de_a8_5():
    ok = rd.premissas(_registros_falsos([0.30, 0.32, 0.31, 0.29], [0.10, 0.12, 0.11, 0.09]))
    assert ok["P-SEGURA"]["passa"] and ok["P-EVENTO"]["passa"] and ok["G-ELEGIVEL-EP"]["passa"] and ok["conclusivo"]
    assert not rd.premissas(_registros_falsos([0.09, 0.10, 0.11, 0.10], [0.10, 0.12, 0.11, 0.09]))["P-SEGURA"]["passa"]
    assert not rd.premissas(_registros_falsos([0.30, 0.32, 0.31, 0.29], [0.24, 0.26, 0.25, 0.25]))["P-EVENTO"]["passa"]
    assert not rd.premissas(_registros_falsos([0.30, 0.32, 0.31, 0.29], [0.10, 0.12, 0.11, 0.09], episodios=2))["conclusivo"]


def test_a_margem_e_a_do_artefato_do_poder():
    d = json.loads((RAIZ / "artifacts_v2_digibrain_prototipo" / "redecidir_evento" / "adendo8_poder.json").read_text(encoding="utf-8"))
    assert round(d["por_k"]["K=150"]["margem"], 3) == rd.MARGEM
    assert lr.margem_efetiva(d["sigma_planejamento"], 150) == pytest.approx(d["por_k"]["K=150"]["margem"], abs=5e-4)
    assert d["por_k"]["K=150"]["vidas"] == 7200 and d["vidas_por_unidade_c3"] == 48
    fontes = {Path(p).parent.parent.name + "/" + Path(p).name: sha for p, sha in d["fonte"].items()}
    assert fontes["longe_regular/medidas.json"].startswith("5a4fb207") and fontes["habito_intencao/medidas.json"].startswith("93b136d6")


# ------------------------------------------------------------------ a fumaca de ponta a ponta
def test_a_fumaca_roda_de_ponta_a_ponta(tmp_path):
    cfg = copy.deepcopy(_cfg("fumaca"))
    cfg["unidades"] = {"bases": [101], "k": 1, "prefixo": "digibrain_prototipo"}
    cfg["dias"] = 1
    pasta = tmp_path / "fumaca"
    r = rd.rodar(cfg, pasta, 1, CONFIGS / "fumaca.json")
    assert r["meta"]["modo"] == "fumaca" and len(r["registros"]) == 48 and r["resultado"]["vidas"] == 48
    meta = json.loads((pasta / "meta.json").read_text(encoding="utf-8"))
    assert set(meta["artefatos_sha256"]) == {"medidas.json", "resultado.json"}
    for nome, sha in meta["artefatos_sha256"].items():
        assert bv._sha(pasta / nome) == sha
    assert meta["bracos"]["M3R"]["redecidir_evento"] is True and "redecidir_evento" not in meta["bracos"]["M3"]
    assert meta["fins_conhecidos"]["M3R"] == sorted(rd.fins_conhecidos("M3R"))
    assert len(list((pasta / "vidas").rglob("*.jsonl"))) == 48
    res = json.loads((pasta / "resultado.json").read_text(encoding="utf-8"))
    assert {"primario", "guarda", "secundarias", "premissas", "leitura", "descritivo"} <= set(res)
    assert set(res["descritivo"]) == {"trocas", "mecanismo", "corpo", "faixas_d0", "outros"}
    med = json.loads((pasta / "medidas.json").read_text(encoding="utf-8"))
    assert all(v["redecidir"]["ligada"] == (v["braco"] in rd.BRACOS_R) for v in med.values())
    with pytest.raises(FileExistsError):
        rd.rodar(cfg, pasta, 1)


def test_resumo_no_console_cp1252_nao_quebra(monkeypatch):
    """o print do resumo com '≈' num stdout cp1252 (console Windows) nao levanta (o #518)"""
    r = {"modo": "m", "vidas": 1, "primario": {}, "guarda": {}, "secundarias": {}, "premissas": {}, "leitura": "≈ 0,5"}
    buf = io.TextIOWrapper(io.BytesIO(), encoding="cp1252", errors="strict")
    monkeypatch.setattr("sys.stdout", buf)
    rd._imprimir_resumo(r)
    buf.flush()
    assert "2248" in buf.buffer.getvalue().decode("ascii")


# ------------------------------------------------------------------ o isolamento (a licao do #515)
def test_o_orquestrador_e_o_poder_nao_montam_o_digibrain():
    """so o orquestrador do prototipo cita o pacote do DigiBrain e a ConfigDigibrain (tests/test_digibrain_etapa0.py e
    tests/test_digibrain_vidas.py); os dois arquivos novos passam por ele"""
    nomes = re.compile(r"\b(ConfigDigibrain\w*|CONFIG_DIGIBRAIN\w*)\b|digilab\.digibrain|from \.digibrain|from \.\.digibrain|import digibrain")
    for f in ("experiments/run_v2_redecidir_evento.py", "experiments/adendo8_poder_redecidir_evento.py"):
        assert not nomes.search((RAIZ / f).read_text(encoding="utf-8")), f


def test_o_orquestrador_nao_cita_a_corrida_da_c2():
    """o G2-SEPARADO da C2 (tests/test_credito_corrida.py) lista quem cita a subchave dela; a C3 nao a combina (D-C2-4)"""
    for f in ("experiments/run_v2_redecidir_evento.py", "experiments/adendo8_poder_redecidir_evento.py"):
        assert "credito_corrida" not in (RAIZ / f).read_text(encoding="utf-8"), f


def _cerebro_falso(motivos: list, fins_estado: dict):
    estado = SimpleNamespace(fins=fins_estado)
    c = SimpleNamespace(cd=SimpleNamespace(intencao_suspensa=False), motivos=motivos, m=SimpleNamespace(estado=estado))
    return SimpleNamespace(_interna=c)


def test_conferir_fins_falha_alto_com_um_fim_desconhecido():
    m = {"fins": [{"chave": ["comer", "cheiro", None], "motivo": "inventado"}]}
    with pytest.raises(RuntimeError, match="dos conhecidos"):
        rd.conferir_fins("M3R", _cerebro_falso([m], {}))
