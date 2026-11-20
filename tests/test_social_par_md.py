"""SOCIAL_PAR MD1, o codigo da medida do M1 e do M2 (docs/PLANO_ANALISE_V3_SOCIAL_PAR_MD.md, secao 8).

A subchave `incentivo_social_zero` (o G2 contra tests/gabaritos/social_md_de_hoje.json, gravado num commit proprio antes do codigo; o
incentivo social em 0; o P1 que segue aprendendo) e o orquestrador `experiments/run_v3_social_par_md.py` (as travas, as unidades, o
G-S3-IGUAL, o G-GRAV-COMP, o retrato do t0 e a PM-1, a fumaca de ponta a ponta e o determinismo)."""
from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "tests"))
sys.path.insert(0, str(RAIZ / "experiments"))

import gabarito_social_md as gab  # noqa: E402
import gabarito_social_m2 as m2  # noqa: E402
import run_v3_social_par_a0 as a0  # noqa: E402
import run_v3_social_par_md as md  # noqa: E402
import run_v3_social_par_s as s  # noqa: E402
from bancada.faixas import FAIXAS_RESERVADAS, PREFIXOS_UNIDADES, SementeSemPlano, unidades_derivadas  # noqa: E402
from digilab.config import CONFIG_DIGIBRAIN_LIGADA, TIPOS_ALVO_SOCIAIS, ConfigDigibrain  # noqa: E402

GABARITO = json.loads((RAIZ / "tests" / "gabaritos" / "social_md_de_hoje.json").read_text(encoding="utf-8"))
CFG = RAIZ / "experiments" / "configs" / "v3_social_par_md"


# ================================================================== a subchave
def test_subchave_desligada_por_padrao_e_so_com_as_unidades_sociais():
    assert ConfigDigibrain().incentivo_social_zero is False
    with pytest.raises(ValueError, match="so vale com a unidades_sociais"):
        ConfigDigibrain(incentivo_social_zero=True)
    with pytest.raises(TypeError):
        ConfigDigibrain(unidades_sociais=True, incentivo_social_zero=1)
    ConfigDigibrain(unidades_sociais=True, incentivo_social_zero=True)


def test_g2_desligada_as_vidas_de_hoje_byte_a_byte():
    assert gab.gerar() == GABARITO


def test_constantes_da_web_sem_a_subchave_desligada():
    import exportar_gabarito_digibrain_modular as E
    assert "incentivo_social_zero" not in E.config_digibrain_json(CONFIG_DIGIBRAIN_LIGADA)


def _incentivos_sociais(vida) -> list[int]:
    out = []
    for m in vida.grupo.motores.values():
        for mot in m.politica.motivos:
            out += [u["termos"]["incentivo"] for u in mot["unidades"] if u["chave"][1] in TIPOS_ALVO_SOCIAIS]
    return out


@pytest.fixture(scope="module")
def vidas_b1():
    return {n: m2.vida_par("B1", 101, cd, None) for n, cd in (("M1", md.M1), ("INC0", md.INC0))}


def test_incentivo_social_em_zero_e_o_p1_segue_aprendendo(vidas_b1):
    """com a subchave, todo incentivo de unidade social e 0 (no M1 ha incentivo > 0, e a subchave muda algo); o desfecho social segue
    aprendendo (o P1 nao para)"""
    com, sem = _incentivos_sociais(vidas_b1["INC0"]), _incentivos_sociais(vidas_b1["M1"])
    assert com and all(x == 0 for x in com)
    assert any(x > 0 for x in sem)
    assert any(any(m.politica.m.plast.desfecho[c]) for m in vidas_b1["INC0"].grupo.motores.values() for c in TIPOS_ALVO_SOCIAIS)


def test_incentivo_zero_so_muda_o_incentivo_social(vidas_b1):
    """os outros termos das unidades sociais e todos os termos das outras unidades seguem a mesma regra: na primeira decisao em que o
    M1 e o INC0 diferem, so o incentivo de uma unidade social difere"""
    a, b = vidas_b1["M1"].grupo.motores["A"].politica.motivos, vidas_b1["INC0"].grupo.motores["A"].politica.motivos
    for x, y in zip(a, b):
        if x == y:
            continue
        ux, uy = ({tuple(u["chave"]): u["termos"] for u in x["unidades"]}, {tuple(u["chave"]): u["termos"] for u in y["unidades"]})
        assert set(ux) == set(uy)
        dif = {(k, t) for k in ux for t in ux[k] if ux[k][t] != uy[k][t]}
        assert dif and all(k[1] in TIPOS_ALVO_SOCIAIS and t == "incentivo" for k, t in dif)
        return
    pytest.fail("o M1 e o INC0 nao diferem em nenhuma decisao")


# ================================================================== as travas e as unidades
def _cfg(nome: str) -> dict:
    return json.loads((CFG / f"{nome}.json").read_text(encoding="utf-8"))


def test_faixa_e_prefixos_reservados():
    assert any((lo, hi) == md.FAIXA for lo, hi, _ in FAIXAS_RESERVADAS)
    assert {"social_par_md", "social_par_md_det"} <= set(PREFIXOS_UNIDADES)


def test_configs_conferem_com_o_plano():
    assert md.modo_da_config(_cfg("fumaca")) == "fumaca"
    assert md.modo_da_config(_cfg("run")) == "run"
    tt = md.trabalhos(_cfg("run"))
    assert len(tt) == 4 * 2 * 200 + 4 * 2 * 50
    assert len({(u["mecanismo"], u["braco"], u["det"], u["semente"]) for u in tt}) == len(tt)


@pytest.mark.parametrize("muda", [{"mecanismos": ["M1", "M1-inc0", "M1+M2", "M1-inc0+M2", "HOJE"]}, {"mecanismos": ["M1"]},
                                  {"bracos": ["B1", "C", "B2"]}, {"bracos": ["C", "B1"]}])
def test_run_recusa_o_que_o_plano_nao_tem(muda):
    with pytest.raises((ValueError, SementeSemPlano)):
        md.modo_da_config({**_cfg("run"), **muda})


def test_fumaca_so_com_as_bases_dos_testes():
    with pytest.raises(SementeSemPlano):
        md.modo_da_config({**_cfg("fumaca"), "unidades": {"bases": [105001], "k": 1}})


# ================================================================== o G-S3-IGUAL (8)
def _u(base: int, braco: str, det: bool, mec: str) -> dict:
    u = unidades_derivadas([base], 1, s.PREFIXO["det" if det else "run"])[0]
    return {**u, "braco": braco, "det": det, "mecanismo": mec}


@pytest.mark.parametrize("base, braco, det", [(101, "C", False), (202, "C", False), (101, "B1", False), (202, "B1", False),
                                              (303, "C", True)])
def test_g_s3_igual_o_hoje_refaz_as_vidas_da_s3(base, braco, det, tmp_path):
    """com o HOJE, as vidas do orquestrador novo (o C pela IntervencaoT0, o retrato no gancho, a VIVO de P com o Gravador) saem com o
    sha256 das vidas do orquestrador da S"""
    r = s.par(_u(base, braco, det, "HOJE"), str(tmp_path))
    with gzip.open(tmp_path / "vidas" / f"{r['par']}.json.gz", "rt", encoding="utf-8") as f:
        da_s = json.load(f)["sha256"]
    v = md.vidas(_u(base, braco, det, "HOJE"))
    assert {c: a0._sha_vida(w) for c, w in v["condicoes"].items()} == da_s
    assert v["retrato"] == {}                                  # o pet de hoje nao tem o P1 social


# ================================================================== o par com os mecanismos
@pytest.fixture(scope="module")
def par_m2(tmp_path_factory):
    return md.par(_u(101, "B1", False, "M1+M2"), str(tmp_path_factory.mktemp("md")))


def test_g_grav_comp_a_grav_tem_a_companhia_e_se_refaz_do_disco():
    """na GRAV com o M2, os dois motores tem a companhia ligada (o gravado sai da mesma fabrica), e o `par` refaz a GRAV da gravacao lida
    do disco (o G1, dentro do `par`)"""
    v = md.vidas(_u(101, "B1", False, "M1+M2"))
    grav = v["condicoes"]["GRAV"].grupo
    assert all(m.ccp.ligada for m in grav.motores.values())
    assert grav.motores["B"].politica.nome == "gravada"


def test_retrato_do_t0_e_a_pm1(par_m2):
    r = par_m2
    assert r["g_instr"] and r["g1"]
    assert set(r["retrato_t0"]) == {"A", "B"}
    p = r["retrato_t0"]["B"]
    assert set(p["desfecho"]) == set(TIPOS_ALVO_SOCIAIS) and "solidao" in p["receptores"] and p["solidao"] is not None
    x = md.pm1([r])
    assert x["n_pares"] == 1 and x["passa"] == (p["desfecho"]["seguir"][p["receptores"].index("solidao")] < 0)
    f = r["frequencia_social_P"]
    assert f["antes_do_t0"]["decisoes"] > 0 and f["janela_VIVO"]["decisoes"] == s.JANELA


def test_pm1_sem_retrato_levanta():
    with pytest.raises(RuntimeError, match="sem o retrato"):
        md.pm1([{"par": "x", "retrato_t0": {}}])


@pytest.mark.parametrize("mec, prem, cl, gd, p1, esperado", [
    ("M1+M2", True, "≈ 0", False, False, "cego"),
    ("M1+M2", False, "≈ 0", True, False, "inconclusivo por premissa"),
    ("M1+M2", True, "≈ 0", True, False, "inconclusivo por premissa (PM-1)"),
    ("M1+M2", True, "< 0", True, False, "< 0"),
    ("M1", True, "≈ 0", True, None, "≈ 0"),
])
def test_leitura_da_celula_na_ordem_da_secao_7(mec, prem, cl, gd, p1, esperado):
    l = md.leitura_celula(mec, {"A_conclusivo": prem}, {"classe": cl}, {"passa": gd}, None if p1 is None else {"passa": p1})
    assert l["classe"] == esperado


# ================================================================== de ponta a ponta
def test_fumaca_de_ponta_a_ponta(tmp_path):
    cfg = {"modo": "fumaca", "mecanismos": ["M1+M2", "M1-inc0+M2"], "bracos": ["B1"], "unidades": {"bases": [101], "k": 1},
           "det": {"bases": [303], "k": 1}}
    r = md.rodar(cfg, tmp_path / "f", 2)["resultado"]
    assert set(r["celulas"]) == {"M1+M2|B1", "M1-inc0+M2|B1"}
    assert r["celulas"]["M1+M2|B1"]["pm1"]["n_pares"] == 1 and r["celulas"]["M1-inc0+M2|B1"]["pm1"] is not None
    assert set(r["contrastes"]) == {"C-APR|B1"} and r["contrastes"]["C-APR|B1"]["pares"] == 1
    assert "texto" in r["conjunto"]
    with pytest.raises(FileExistsError):
        md.rodar(cfg, tmp_path / "f", 1)


def test_determinismo_do_par(tmp_path):
    u = _u(303, "C", True, "M1-inc0+M2")
    a, b = md.par(u, str(tmp_path / "a")), md.par(u, str(tmp_path / "b"))
    assert a["arquivo_sha256"] == b["arquivo_sha256"] and a == {**b, "arquivo_sha256": a["arquivo_sha256"]}
