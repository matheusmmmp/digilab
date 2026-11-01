"""O orquestrador da C2 (experiments/run_v2_habito_intencao.py; o adendo 7 do plano, A7.2 a A7.10): a config e a trava (o adendo 7
APROVADO (sem ele, a run e recusada); a faixa 75101...75505; as bases, o K, os dias; no maximo 4 processos; nada por cima de
uma pasta existente), os bracos, os fins conhecidos lidos da `estado.py` (a licao do #507), as corridas, a classe, a leitura de A7.7, o
artefato do poder e a fumaca de ponta a ponta. Vidas so com as sementes dos testes (101...505): nenhuma da faixa 75xxx roda aqui."""
from __future__ import annotations

import copy
import json
import re
import sys
from pathlib import Path
from dataclasses import replace
from types import SimpleNamespace

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402
import run_v2_habito_intencao as hi  # noqa: E402
import run_v2_longe_regular as lr  # noqa: E402
from bancada.faixas import na_faixa_reservada  # noqa: E402
from digilab.digibrain import estado as mod_estado  # noqa: E402

CONFIGS = RAIZ / "experiments" / "configs" / "v2_habito_intencao"
MARCA_APROVADO = "**Status: APROVADO pelo Matheus em 2026-10-31,** com as AD7-1 a AD7-5"


def _cfg(nome: str = "habito_intencao") -> dict:
    return json.loads((CONFIGS / f"{nome}.json").read_text(encoding="utf-8"))


# ------------------------------------------------------------------ o que o adendo fixa
def test_o_desenho_e_o_do_adendo_7():
    assert hi.BASES == (75101, 75202, 75303, 75404, 75505) and hi.K_POR_BASE == 30 and hi.DIAS == 14 and hi.ORCAMENTO_POR_DIA == 16
    assert hi.PRIMARIOS == ("longe_fixo", "comedouro") and hi.LUGARES == ("longe_fixo", "comedouro", "longe")
    assert len(hi.CELULAS) == 12 and len(hi.CELULAS_PRIMARIO) == 8 and hi.BRACOS == ("M1", "M2", "M2c")
    assert hi.PREFIXO == "digibrain_prototipo" and hi.MARGEM == 0.011 and hi.MAX_PROCESSOS == 4 and hi.P_CORRIDA_LIMIAR == 1.1
    us = bv.unidades_derivadas(hi.BASES, hi.K_POR_BASE, hi.PREFIXO)
    assert len(us) == 150 and len(us) * len(hi.BRACOS) * len(hi.CELULAS) == 5400


def test_o_m2c_e_o_m2_do_conserto_com_a_corrida_e_nenhum_braco_tem_a_suspensa_nem_a_memoria():
    m2, m2c, m1 = (orq.config_do_braco(b, conserto=True) for b in ("M2", "M2c", "M1"))
    assert orq.SUBCHAVES_C2 == {"M2c": {**orq.SUBCHAVES_CONSERTO["M2"], "credito_corrida": True}}
    assert m2c.credito_corrida and not m2.credito_corrida and not m1.credito_corrida
    assert m2c == replace(m2, credito_corrida=True)
    for c in (m1, m2, m2c):
        assert not c.intencao_suspensa and not c.m_mem and c.cheiro_inato and c.intencao_cheiro
    assert m1.p1 and not m1.p2 and m2.p2


def test_o_m2c_so_existe_nas_fases_do_conserto():
    with pytest.raises(ValueError, match="braco do modular"):
        orq.config_do_braco("M2c")


def test_a_faixa_esta_reservada():
    assert na_faixa_reservada(75101) and na_faixa_reservada(75505) and not na_faixa_reservada(75506) and not na_faixa_reservada(75100)
    hi.exigir_faixa_reservada()


# ------------------------------------------------------------------ a config e a trava
def test_a_trava_exige_o_adendo_7_aprovado(monkeypatch):
    """o plano real tem o adendo 7 APROVADO; com o cabecalho trocado por PROPOSTO (so neste teste), a run e recusada"""
    plano = hi._plano()
    assert MARCA_APROVADO in plano
    monkeypatch.setattr(hi, "_plano", lambda: plano.replace(MARCA_APROVADO, "**Status: PROPOSTO.** Só o Matheus o aprova"))
    with pytest.raises(RuntimeError, match="nao esta APROVADO"):
        hi.modo_da_config(_cfg())
    assert hi.modo_da_config(_cfg("fumaca")) == "fumaca"                # a fumaca nao precisa do adendo


def test_com_o_adendo_aprovado_a_config_segue_o_adendo():
    assert MARCA_APROVADO in hi._plano()
    assert hi.modo_da_config(_cfg()) == "habito_intencao"


@pytest.mark.parametrize("bases", [[75101, 75202, 75303, 75404], [75101, 75202, 75303, 75404, 75506], [75505, 75404, 75303, 75202, 75101],
                                   [71101, 71202, 71303, 71404, 71505], [66101, 66202, 66303, 66404, 66505], [101, 75101],
                                   [101, 75202, 75303, 75404, 75505]])
def test_recusa_outra_base_e_sementes_fora_da_faixa(bases):
    c = _cfg()
    c["unidades"]["bases"] = bases
    with pytest.raises(bv.SementeSemPlano):
        hi.modo_da_config(c)


def test_recusa_outro_k_outros_dias_outro_orcamento_e_outro_plano():
    for chave, valor in (("k", 29), ("k", 10), ("dias", 13), ("dias", 15), ("orcamento_por_dia", 15), ("plano", "outro.md")):
        c = _cfg()
        if chave == "k":
            c["unidades"]["k"] = valor
        else:
            c[chave] = valor
        with pytest.raises(ValueError):
            hi.modo_da_config(c)
    c = _cfg()
    c["unidades"]["prefixo"] = "outro"
    with pytest.raises(ValueError, match="prefixo"):
        hi.modo_da_config(c)


def test_recusa_chave_a_mais_fase_errada_e_fumaca_com_dias_demais():
    with pytest.raises(ValueError, match="sobram"):
        hi.modo_da_config({**_cfg(), "inatos": {}})
    with pytest.raises(ValueError, match="fase"):
        hi.modo_da_config({**_cfg(), "fase": "longe_regular"})
    c = _cfg("fumaca")
    c["dias"] = 15
    with pytest.raises(ValueError, match="fumaca"):
        hi.modo_da_config(c)


def test_a_trava_exige_a_faixa_reservada(monkeypatch):
    monkeypatch.setattr(hi, "FAIXAS_RESERVADAS", tuple(f for f in hi.FAIXAS_RESERVADAS if f[0] != 75101))
    with pytest.raises(bv.SementeSemPlano, match="FAIXAS_RESERVADAS"):
        hi.modo_da_config(_cfg())


def test_recusa_mais_de_4_processos_e_pasta_existente(tmp_path):
    with pytest.raises(ValueError, match="4 processos"):
        hi.rodar(_cfg("fumaca"), tmp_path / "x", 5)
    with pytest.raises(FileExistsError):
        hi.rodar(_cfg("fumaca"), tmp_path, 1)


def test_a_saida_da_run_nao_e_a_pasta_do_poder():
    assert hi.SAIDA == "artifacts_v2_digibrain_prototipo/habito_intencao/run"
    # a run da C2 (#517) ja gravou a pasta; ela nao pode ser a pasta-mae, onde ficam os arquivos do poder
    assert (RAIZ / hi.SAIDA).name == "run"
    assert (RAIZ / hi.SAIDA).parent.name == "habito_intencao"


# ------------------------------------------------------------------ os fins (a licao do #507)
def _literais_de_fim() -> set:
    texto = Path(mod_estado.__file__).read_text(encoding="utf-8")
    return set(re.findall(r"_acabar(?:_suspensa)?\(\"([a-z_]+)\"", texto))


def test_os_fins_conhecidos_sao_os_do_estado_com_a_config_de_cada_braco():
    for b in hi.BRACOS:
        assert hi.fins_conhecidos(b) == {"meta", "trocou", "sumiu", "desistiu", "achou"}


def test_todo_fim_que_a_estado_py_escreve_e_conhecido_ou_e_da_l2_desligada():
    literais = _literais_de_fim()
    assert {"meta", "trocou", "sumiu", "desistiu", "achou"} <= literais
    conhecidos = hi.fins_conhecidos("M2c")
    assert literais - conhecidos == set(mod_estado.FINS_SUSPENSA)          # o resto e da L-2, que fica desligada nos tres bracos
    assert not set(mod_estado.FINS_SUSPENSA) & conhecidos


def _cerebro_falso(motivos: list, fins_estado: dict, suspensa: bool = False):
    estado = SimpleNamespace(fins=fins_estado)
    c = SimpleNamespace(cd=SimpleNamespace(intencao_suspensa=suspensa), motivos=motivos, m=SimpleNamespace(estado=estado))
    return SimpleNamespace(_interna=c)


def _m(fins=(), **extra):
    return {"fins": [{"chave": ["comer", "cheiro", None], "motivo": f} for f in fins], **extra}


def test_conferir_fins_conta_e_compara_com_o_estado():
    zero = {m: 0 for m in ("meta", "trocou", "sumiu", "desistiu", "achou")}
    reg = _cerebro_falso([_m(["meta", "trocou"]), _m(["desistiu"])], {**zero, "meta": 1, "trocou": 1, "desistiu": 1})
    assert hi.conferir_fins("M2", reg) == {**zero, "meta": 1, "trocou": 1, "desistiu": 1}


@pytest.mark.parametrize("motivos,fins_estado,msg", [
    ([_m(["inventado"])], {}, "dos conhecidos"),
    ([_m(["expirou"])], {}, "dos conhecidos"),
    ([_m(["meta"])], {"meta": 2, "trocou": 0, "sumiu": 0, "desistiu": 0, "achou": 0}, "nao sao os do estado"),
    ([_m(retomou=True)], {}, "retomada"),
])
def test_conferir_fins_falha_alto(motivos, fins_estado, msg):
    with pytest.raises(RuntimeError, match=msg):
        hi.conferir_fins("M2", _cerebro_falso(motivos, fins_estado))


def test_conferir_fins_falha_alto_com_n_susp_e_com_a_suspensa_ligada():
    m = {"fins": [{"chave": ["comer", "cheiro", None], "motivo": "trocou", "n_susp": 1}]}
    with pytest.raises(RuntimeError, match="n_susp"):
        hi.conferir_fins("M2", _cerebro_falso([m], {}))
    with pytest.raises(RuntimeError, match="ligada"):
        hi.conferir_fins("M2", _cerebro_falso([], {}, suspensa=True))


# ------------------------------------------------------------------ as corridas
@pytest.mark.parametrize("braco", hi.BRACOS)
def test_as_corridas_da_vida_e_os_fins_numa_vida_de_teste(braco):
    _, registro, _ = lr.viver(braco, "relapso", "longe_fixo", 303, 2, 16)
    cs = hi.corridas_da_vida(registro)
    ms = orq.cerebro_de(registro).motivos
    assert sum(x["n"] for x in cs) < len(ms) and cs[0]["inicio"] == 0
    assert all(cs[i]["b"] != cs[i + 1]["b"] and cs[i]["inicio"] + cs[i]["n"] == cs[i + 1]["inicio"] for i in range(len(cs) - 1))
    med = hi.medidas_corridas(registro, 2)
    assert med["n"] == len(cs) and med["media_n"] >= 1
    assert med["creditos_p2"] == (len(cs) if braco == "M2c" else (0 if braco == "M1" else med["creditos_p2"]))
    hi.conferir_fins(braco, registro)


def test_no_m2c_as_corridas_tem_de_ser_as_entregues_ao_p2():
    _, registro, _ = lr.viver("M2c", "atencioso", "comedouro", 202, 2, 16)
    c = orq.cerebro_de(registro)
    x = next(x for m in c.motivos for x in m["corridas"] if x["n"] > 1)
    x["r"] += 1
    with pytest.raises(RuntimeError, match="uma a uma"):
        hi.corridas_da_vida(registro)


def test_uma_decisao_sem_consequencia_fora_do_fim_falha_alto():
    _, registro, _ = lr.viver("M2", "atencioso", "comedouro", 101, 1, 16)
    orq.cerebro_de(registro).motivos[3]["consequencia"] = None
    with pytest.raises(RuntimeError, match="sem a consequencia"):
        hi.corridas_da_vida(registro)


# ------------------------------------------------------------------ a classe e a leitura (A7.6 e A7.7)
def _ic(lo, hi_):
    return {"ic_inferior": lo, "ic_superior": hi_, "motivo": None}


@pytest.mark.parametrize("lo,hi_,esperada", [(-0.01, 0.01, "≈ 0"), (0.001, 0.0105, "≈ 0"), (0.001, 0.012, "> 0"), (-0.03, -0.012, "< 0"),
                                             (-0.012, 0.005, "indeterminado")])
def test_a_classe_usa_a_margem_do_adendo_7(lo, hi_, esperada):
    assert hi.classe(_ic(lo, hi_))["classe"] == esperada


def _prim(passa: bool, classe: str) -> dict:
    return {"passa": passa, "classe": {"classe": classe}, "ressalva_assimetria": None}


@pytest.mark.parametrize("passa,cl_pa,cl_s1,conclusivo,trecho", [
    (True, "> 0", "> 0", True, "explica a falha"), (True, "≈ 0", "> 0", True, "explica a falha"),
    (True, "> 0", "≈ 0", True, "explica parte"), (True, "> 0", "indeterminado", True, "explica parte"), (True, "> 0", "< 0", True, "explica parte"),
    (False, "≈ 0", "> 0", True, "nao e a causa"), (False, "< 0", "> 0", True, "piora"), (False, "indeterminado", "> 0", True, "indeterminado"),
    (True, "> 0", "> 0", False, "inconclusivo por premissa")])
def test_a_leitura_de_a7_7(passa, cl_pa, cl_s1, conclusivo, trecho):
    r = hi.leitura(_prim(passa, cl_pa), {"conclusivo": conclusivo}, {"classe": {"classe": cl_s1}})
    assert trecho in r["linha"]


def test_a_margem_e_a_do_artefato_do_poder():
    d = json.loads((RAIZ / "artifacts_v2_digibrain_prototipo" / "habito_intencao" / "adendo7_poder.json").read_text(encoding="utf-8"))
    assert round(d["por_k"]["K=150"]["margem"], 3) == hi.MARGEM
    assert lr.margem_efetiva(d["sigma_planejamento"], 150) == pytest.approx(d["por_k"]["K=150"]["margem"], abs=5e-4)


# ------------------------------------------------------------------ a fumaca de ponta a ponta
def test_a_fumaca_roda_de_ponta_a_ponta(tmp_path):
    cfg = copy.deepcopy(_cfg("fumaca"))
    cfg["unidades"] = {"bases": [101], "k": 1, "prefixo": "digibrain_prototipo"}
    cfg["dias"] = 1
    pasta = tmp_path / "fumaca"
    r = hi.rodar(cfg, pasta, 1, CONFIGS / "fumaca.json")
    assert r["meta"]["modo"] == "fumaca" and len(r["registros"]) == 36 and r["resultado"]["vidas"] == 36
    meta = json.loads((pasta / "meta.json").read_text(encoding="utf-8"))
    assert set(meta["artefatos_sha256"]) == {"medidas.json", "resultado.json"}
    for nome, sha in meta["artefatos_sha256"].items():
        assert bv._sha(pasta / nome) == sha
    assert meta["bracos"]["M2c"]["credito_corrida"] is True and meta["fins_conhecidos"]["M2"] == sorted(hi.fins_conhecidos("M2"))
    assert len(list((pasta / "vidas").rglob("*.jsonl"))) == 36
    res = json.loads((pasta / "resultado.json").read_text(encoding="utf-8"))
    assert {"primario", "secundarias", "premissas", "leitura", "descritivo"} <= set(res)
    assert set(res["descritivo"]) == {"indices", "corridas_e_h", "corpo", "outros"}
    with pytest.raises(FileExistsError):
        hi.rodar(cfg, pasta, 1)


def test_resumo_no_console_cp1252_nao_quebra(monkeypatch):
    """O print do resumo com '≈' num stdout cp1252 (console Windows) nao levanta (D-C2-4-4)."""
    import io
    import run_v2_habito_intencao as hi
    import run_v2_longe_regular as lr
    r = {"modo": "m", "vidas": 1, "primario": {}, "secundarias": {}, "premissas": {}, "sorteado": {}, "leitura": "≈ 0,5"}
    for mod in (hi, lr):
        buf = io.TextIOWrapper(io.BytesIO(), encoding="cp1252", errors="strict")
        monkeypatch.setattr("sys.stdout", buf)
        mod._imprimir_resumo(r)
        buf.flush()
        assert "2248" in buf.buffer.getvalue().decode("ascii")
