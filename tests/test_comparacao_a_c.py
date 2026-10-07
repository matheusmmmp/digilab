"""V2, COMPARACAO-A-C (docs/TAREFA_V2_COMPARACAO_A_C.md): o orquestrador da comparacao A x C.

O que se confere: os pontos sao os dos artefatos e o A e o do experimento maior chave a chave; pela BancadaAC, a vida do A e a da bancada
do experimento maior e a do C e a da BancadaComC no ponto dele, byte a byte; o P0 e comum; o acoplado da mesma experiencia rejoga o
registro do P1 do A com o C (G1); a sonda do aprendido do A concorda com o motivo e e zero no P0; a familia, o Holm de dois, o N e a
tabela do M6 em dados com resposta conhecida; os modos recusam o que nao e deles; a fumaca de ponta a ponta.
"""
from __future__ import annotations

import json
import math
import sys
from dataclasses import replace
from pathlib import Path
from statistics import NormalDist

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import cerebro_c_bancada as cbc  # noqa: E402
import run_v2_comparacao_cerebros as ac  # noqa: E402
import run_v2_experimento_maior as em  # noqa: E402
from digilab.config import CONFIG_CEREBRO_C_APRENDIZ, CONFIG_CONSEQUENCIA  # noqa: E402

FUMACA = json.loads((RAIZ / "experiments/configs/v2_comparacao_cerebros/fumaca_ac.json").read_text(encoding="utf-8"))
PILOTO = json.loads((RAIZ / "experiments/configs/v2_comparacao_cerebros/piloto_ac.json").read_text(encoding="utf-8"))
CURTA = {**FUMACA, "dias": 2, "orcamento": 32}


def _bancada(cfg=CURTA) -> ac.BancadaAC:
    return ac.bancada_da_config(cfg)


# ------------------------------------------------------------------ os pontos e a bancada


def test_pontos_dos_artefatos():
    a = json.loads((RAIZ / ac.ESCOLHA_A).read_text(encoding="utf-8"))["ponto"]
    c = json.loads((RAIZ / ac.ESCOLHA_C).read_text(encoding="utf-8"))["ponto"]
    assert ac.ponto_a() == a and ac.ponto_c() == c
    assert (c["passo"], c["teto"], c["w0_info"], c["ganho"]) == (128, 4096, 256, 4)          # tarefa, secao 1
    assert (a["g"], a["ganho"], a["w0_info"], a["w0_pedido"]) == (512, 4, 256, 256)
    b = _bancada()
    assert b.cfg_cerebro_c == replace(CONFIG_CEREBRO_C_APRENDIZ, passo=128, teto=4096, w0_info=256)
    assert ac.delta_do_experimento_maior() == pytest.approx(0.1986268570547561, abs=0)


def test_o_a_e_o_da_validacao_unica_chave_a_chave():
    """A bancada do A e a do experimento maior (config_da_bancada da validacao unica): o mesmo aprendiz, o mesmo sinal, o K4 e a montagem."""
    cfg_em = json.loads((RAIZ / ac.CONFIG_EXPERIMENTO_MAIOR).read_text(encoding="utf-8"))
    ref = bv.bancada_da_config({**em.config_da_bancada(cfg_em, ["P1"], ["descasado"], []), "dias": 2, "orcamento": 32})
    b = _bancada()
    for campo in ref.__dataclass_fields__:
        assert getattr(b, campo) == getattr(ref, campo), campo
    assert b.montagem == "completa" and b.julgamento_fruta and b.cfg_consequencia.canais_ligados
    assert b.cfg_consequencia == replace(CONFIG_CONSEQUENCIA, ganho=4, canais_ligados=True)


@pytest.mark.parametrize("mundo", ac.MUNDOS)
def test_vidas_do_a_e_do_c_sao_as_das_bancadas_de_origem(mundo):
    b = _bancada()
    cfg_em = json.loads((RAIZ / ac.CONFIG_EXPERIMENTO_MAIOR).read_text(encoding="utf-8"))
    ref_a = bv.bancada_da_config({**em.config_da_bancada(cfg_em, ["P1"], [mundo], []), "dias": 2, "orcamento": 32})
    ref_c = cbc.BancadaComC(2, 32, cfg_lobos=ref_a.cfg_lobos, cfg_consequencia=ref_a.cfg_consequencia, julgamento_fruta=True,
                            montagem="completa", cfg_cerebro_c=b.cfg_cerebro_c)
    for braco in ac.BRACOS:
        a = b.vida(bv.EspecVida("atencioso", braco, 101, 202, mundo))
        assert bv.resumo_motor(a.motor) == bv.resumo_motor(ref_a.vida(bv.EspecVida("atencioso", braco, 101, 202, mundo)).motor)
        assert bv._interno(a.motor) == bv._interno(ref_a.vida(bv.EspecVida("atencioso", braco, 101, 202, mundo)).motor)
        c = b.vida(bv.EspecVida("atencioso", braco, 101, 202, mundo, cbc.CEREBRO_C))
        rc = ref_c.vida(bv.EspecVida("atencioso", braco, 101, 202, mundo, cbc.CEREBRO_C))
        assert bv.resumo_motor(c.motor) == bv.resumo_motor(rc.motor) and bv._interno(c.motor) == bv._interno(rc.motor)
        # o C nunca recebe as pecas da montagem do A
        assert b.braco(c.espec) == bv.braco_de(braco)


def test_o_c_no_p1_e_o_da_calibracao_dele():
    """O P1 do C nao depende do K4, da montagem nem da chave dos canais: e a vida da calibracao do C (bancada_c do orquestrador dela)."""
    import run_v2_calibracao_cerebro_c as calc
    c = ac.ponto_c()
    ref = calc.bancada_c({"dias": 2, "orcamento": 32}, c["ganho"], c["passo"], c["teto"], c["w0_info"])
    b = _bancada()
    for mundo in ac.MUNDOS:
        e = bv.EspecVida("atencioso", "P1", 101, 202, mundo, cbc.CEREBRO_C)
        assert bv.resumo_motor(b.vida(e).motor) == bv.resumo_motor(ref.vida(e).motor)


@pytest.mark.parametrize("mundo", ac.MUNDOS)
def test_p0_comum(mundo):
    b = _bancada()
    a = b.vida(bv.EspecVida("atencioso", "P0", 303, 404, mundo))
    c = b.vida(bv.EspecVida("atencioso", "P0", 303, 404, mundo, cbc.CEREBRO_C))
    i = b.vida(bv.EspecVida("atencioso", "P0", 303, 404, mundo, "instinto"))
    assert bv.resumo_motor(a.motor) == bv.resumo_motor(c.motor) == bv.resumo_motor(i.motor)
    assert ac.legibilidade_a(bv.do_braco(a.motor.politica).cerebro)["aprendido_decidiu"] == 0
    assert ac.legibilidade_c(bv.do_braco(c.motor.politica).cerebro)["aprendido_decidiu"] == 0


@pytest.mark.parametrize("mundo", ac.MESMA_EXPERIENCIA)
def test_mesma_experiencia(mundo):
    b = _bancada()
    a = b.vida(bv.EspecVida("atencioso", "P1", 101, 202, mundo))
    c = ac.acoplar_no_c(b, a)
    assert c.espec.cerebro == cbc.CEREBRO_C and c.origem == a.nome and c.filtro == "nenhum"
    assert c.motor.log.para_jsonl() == a.motor.log.para_jsonl()          # o mesmo registro
    b.conferir_replay(c, c.motor.log.para_jsonl())                         # G1
    # o C rejogado no registro do A nao e o C fechado (as acoes do pet diferem; o mundo e o mesmo)
    fechado = b.vida(bv.EspecVida("atencioso", "P1", 101, 202, mundo, cbc.CEREBRO_C))
    assert c.motor.acoes_recentes(10**9) != fechado.motor.acoes_recentes(10**9) or c.motor.log.para_jsonl() != fechado.motor.log.para_jsonl()
    d = ac.divergencia_acoplada(b, a, c, {"estados": 6, "amostras": 10, "semente": 101})
    assert len(d) == 2 and all(x >= 0.0 for x in d)
    with pytest.raises(ValueError):
        ac.acoplar_no_c(b, c)


def test_legibilidade_do_a_concorda_com_o_motivo_e_conta():
    b = _bancada({**FUMACA, "dias": 4, "orcamento": 64})
    v = b.vida(bv.EspecVida("atencioso", "P1", 101, 202, "descasado"))
    leg = ac.legibilidade_a(bv.do_braco(v.motor.politica).cerebro)      # falha alto se a sonda e o motivo divergirem
    assert 0 < leg["aprendido_decidiu"] <= leg["decisoes_com_escolha"] < leg["decisoes"]
    assert leg["aprendido_com_fator"] <= leg["aprendido_decidiu"]
    vc = b.vida(bv.EspecVida("atencioso", "P1", 101, 202, "descasado", cbc.CEREBRO_C))
    lc = ac.legibilidade_c(bv.do_braco(vc.motor.politica).cerebro)
    assert 0 < lc["aprendido_decidiu"] == lc["aprendido_decidiu_com_escolha"] and lc["aprendido_com_fator"] is None


# ------------------------------------------------------------------ analise com resposta conhecida


def test_tamanho_pela_formula_com_holm_de_dois():
    delta, sigma = 0.2, 0.3
    vals = [sigma * x for x in (-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5)]
    s_amostra = math.sqrt(sum(v * v for v in vals) / (len(vals) - 1))
    prim = {"CC-1": {"valores": {"1": vals}}, "CC-2": {"valores": {"1": [v / 2 for v in vals]}}}
    t = ac.tamanho(prim, delta, None)
    z = NormalDist().inv_cdf
    n = math.ceil(((z(1 - 0.05 / 2 / 2) + z(0.8)) * s_amostra / delta) ** 2)
    assert t["por_contraste"]["CC-1"]["n_formula"] == max(5, -(-n // 5) * 5)
    assert t["alfa_passo_bilateral"] == 0.025 and t["alfa_por_lado"] == 0.0125
    assert t["n_validacao"] == t["por_contraste"]["CC-1"]["n_formula"] and t["k_validacao"] == t["n_validacao"] // 5


def test_p_bilateral_simetrico():
    boot = {"reamostragens": 2000, "semente": 7, "nivel": 0.95}
    g = {i: [x] for i, x in enumerate([0.3, 0.5, 0.2, 0.4, 0.6, 0.1])}
    p = ac.p_bilateral(g, boot)
    assert p == ac.p_bilateral({k: [-v[0]] for k, v in g.items()}, boot) and p < 0.01
    assert ac.p_bilateral({i: [0.0] for i in range(5)}, boot) == 1.0       # tudo zero: nao rejeita


def _prim(leitura):
    return {k: {"leitura_m6": leitura[i]} for i, k in enumerate(ac.PRIMARIOS)}


def _leg(dif, empate):
    return {"c_menos_a": {"media": dif, "empate": empate, "vence": None if empate else ("C" if dif > 0 else "A")},
            "por_cerebro": {"A": {"media": 0.2}, "C": {"media": 0.2 + dif}}}


def _cst(rcpu, rlog):
    rel = {}
    for k, r in (("us_por_decisao", rcpu), ("bytes_log_por_dia", rlog)):
        emp = abs(r) < ac.LIMIAR_CUSTO
        rel[k] = {"c_sobre_a_menos_1": r, "empate": emp, "vence": None if emp else ("C" if r < 0 else "A")}
    return {"relativo": rel}


def test_tabela_m6_de_cima_para_baixo():
    assert ac.tabela_m6(_prim(["C melhor", "empate"]), _leg(0.0, True), _cst(0, 0))[-1] == {"recomendacao": "C"}
    assert ac.tabela_m6(_prim(["A melhor", "A melhor"]), _leg(0.3, False), _cst(0, 0))[-1] == {"recomendacao": "A"}
    assert ac.tabela_m6(_prim(["empate", "empate"]), _leg(0.1, False), _cst(0, 0))[-1] == {"recomendacao": "C"}
    assert ac.tabela_m6(_prim(["empate", "empate"]), _leg(0.01, True), _cst(-0.5, -0.3))[-1] == {"recomendacao": "C"}
    assert ac.tabela_m6(_prim(["empate", "empate"]), _leg(0.01, True), _cst(0.1, -0.1))[-1] == {"recomendacao": "A"}  # passo 5
    t = ac.tabela_m6(_prim(["C melhor", "A melhor"]), _leg(0.0, True), _cst(0, 0))
    assert t[-1] == {"recomendacao": "?"} and "conflito" in t[1]["resultado"]


def test_leitura_dos_contrastes():
    c = {"media": -0.05, "ic95": {"ic_inferior": -0.1, "ic_superior": -0.01}, "ic90": {"ic_inferior": -0.09, "ic_superior": -0.02}}
    assert ac.leitura(c, True, 0.2) == "empate"            # secao 4: dentro da margem e empate, mesmo passando no Holm
    assert ac.leitura(c, False, 0.2) == "empate"
    assert ac.leitura(c, True, 0.05) == "C melhor"         # fora da margem e passando no Holm
    assert ac.leitura(c, False, 0.05) == "inconclusivo"
    assert ac.leitura(c, None, 0.05) == "C melhor"         # secundario: o IC 95% inteiro de um lado (descritivo)


# ------------------------------------------------------------------ modos


def test_modos_recusam():
    with pytest.raises(bv.SementeSemPlano):
        ac.modo_e_unidades({**FUMACA, "unidades": {"bases": [30101, 30202, 30303, 30404, 30505], "k": 1, "prefixo": ac.PREFIXO}})
    with pytest.raises(bv.SementeSemPlano):
        ac.modo_e_unidades({**FUMACA, "unidades": {"bases": [15101, 15202, 15303, 15404, 15505], "k": 1, "prefixo": ac.PREFIXO}})
    with pytest.raises(ValueError):
        ac.modo_e_unidades({**FUMACA, "unidades": {"bases": [101], "k": 1, "prefixo": "experimento-maior"}})
    with pytest.raises(ValueError):
        ac.modo_e_unidades({**PILOTO, "unidades": {**PILOTO["unidades"], "k": 2}})
    with pytest.raises(ValueError):
        ac.modo_e_unidades({**PILOTO, "delta": 0.2})
    assert ac.modo_e_unidades(PILOTO)[0] == "piloto" and len(ac.modo_e_unidades(PILOTO)[1]) == 20
    val = {**PILOTO, "unidades": {"bases": list(bv.BASES_COMPARACAO["validacao"]), "k": 1, "prefixo": ac.PREFIXO}}
    with pytest.raises(ValueError):
        ac.modo_e_unidades(val)                             # sem o campo do adendo 2


def test_validacao_roda_uma_vez(tmp_path):
    val = {**PILOTO, "unidades": {"bases": list(bv.BASES_COMPARACAO["validacao"]), "k": 1, "prefixo": ac.PREFIXO}, "adendo": 2}
    if "## Adendo 2" not in (RAIZ / ac.PLANO).read_text(encoding="utf-8"):
        pytest.skip("o adendo 2 ainda nao esta no plano")
    (tmp_path / "resumo.json").write_text("{}", encoding="utf-8")
    with pytest.raises(ac.ValidacaoJaFeita):
        ac.rodar(val, tmp_path)


def test_fumaca_de_ponta_a_ponta(tmp_path):
    cfg = {**FUMACA, "unidades": {"bases": [101, 202], "k": 1, "prefixo": ac.PREFIXO}, "dias": 2, "orcamento": 32}
    r = ac.rodar(cfg, tmp_path, log=lambda s: None)
    assert r["modo"] == "fumaca" and len(r["medidas"]) == 2 * ac.vidas_por_unidade() == 2 * 47
    a = r["analise"]
    assert set(a["primarios"]) == {"CC-1", "CC-2"} and set(a["nao_testaveis"]) == {"CB-1", "CB-2"}
    assert {c["holm"]["limiar"] for c in a["primarios"].values()} == {0.025, 0.05}
    assert len(a["secundarios"]) == 4 * 3 - 2 + 4
    assert a["m6"][0]["passo"] == 0 and "recomendacao" in a["m6"][-1]
    assert a["tamanho_amostra"]["n_validacao"] % 5 == 0
    for nome in ("medidas.json", "analise.json", "resumo.json", "meta.json"):
        assert (tmp_path / nome).is_file()
    assert len(list((tmp_path / "vidas").glob("*.jsonl"))) == 2 * 47
    meta = json.loads((tmp_path / "meta.json").read_text(encoding="utf-8"))
    assert meta["ponto_c"] == ac.ponto_c() and meta["config_bancada_a"]["montagem"] == "completa"


def test_config_da_validacao_e_a_do_adendo_2():
    """O N do adendo 2 (5, K = 1) sai do piloto gravado e e o da config da validacao; as unidades sao as da tabela do adendo."""
    val = json.loads((RAIZ / "experiments/configs/v2_comparacao_cerebros/validacao_ac.json").read_text(encoding="utf-8"))
    piloto = json.loads((RAIZ / "artifacts_v2_comparacao_cerebros/piloto/resumo.json").read_text(encoding="utf-8"))
    assert piloto["tamanho_amostra"]["n_validacao"] == 5 * val["unidades"]["k"] == 5
    modo, unidades = ac.modo_e_unidades(val)
    assert modo == "validacao" and val["adendo"] == 2
    plano = (RAIZ / ac.PLANO).read_text(encoding="utf-8")
    for u in unidades:
        assert f"| {u['base']} | {u['semente']} | {u['genoma']} |" in plano
    assert {k: v for k, v in val.items() if k not in ("descricao", "adendo", "unidades", "saida", "simulacao")} == \
        {k: v for k, v in PILOTO.items() if k not in ("descricao", "adendo", "unidades", "saida", "simulacao")}
