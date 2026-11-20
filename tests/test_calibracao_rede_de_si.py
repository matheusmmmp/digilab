"""V2, REDE-DE-SI-CALIBRACAO: o orquestrador da calibracao do `passo` da rede de si e do piloto (docs/PLANO_ANALISE_V2_REDE_DE_SI.md,
secoes 5, 6 e 8). So as sementes dos testes: a run nas bases 43101...43505 precisa do sim do Matheus.

O que se confere:
- a config da calibracao e a do plano (o ponto da K2, o gasto do passo 0, a grade, o poder, o bootstrap) e as recusas (a validacao,
  outras bases, o prefixo, o corpo fora do passo 0, a pasta que existe);
- a regra do `passo` (secao 5), a margem (secao 6) e o N efetivo em dados com a resposta conhecida;
- a medida da grade numa vida real (com o passo 0, a rede e a persistencia) e a grade de uma unidade (a mesma vida em todo passo, G-OBS);
- a fumaca inteira (a grade, a regra, o piloto, a margem e, com a margem negativa, a leitura de que a validacao nao roda).
"""
from __future__ import annotations

import json
import sys
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v2_calibracao_rede_de_si as rc  # noqa: E402
from digilab.metrics import mae_previsao, previsao_persistencia  # noqa: E402

CFG = RAIZ / "experiments" / "configs" / "v2_rede_de_si" / "calibracao.json"
FUMACA = RAIZ / "experiments" / "configs" / "v2_rede_de_si" / "fumaca_calibracao.json"


def _cfg(caminho=CFG) -> dict:
    return json.loads(caminho.read_text(encoding="utf-8"))


# ------------------------------------------------------------------ 1. a config


def test_a_config_da_calibracao_e_a_do_plano():
    c = _cfg()
    assert rc.modo_da_config(c) == "calibracao"
    assert c["plano"] == rc.PLANO and (RAIZ / c["plano"]).is_file()
    assert c["unidades"] == {"bases": [43101, 43202, 43303, 43404, 43505], "k": 4, "prefixo": "rede_de_si"}
    assert c["grade_passo"] == [16, 64, 256] and c["dias"] == 14 and c["orcamento"] == 224
    assert c["montagem"] == "completa" and c["ponto"] == "T3"
    assert len(bv.unidades_derivadas(c["unidades"]["bases"], c["unidades"]["k"], "rede_de_si")) == 20
    for p in c["grade_passo"]:
        cb = rc.config_bancada(c, p, [b for b, _ in rc.BRACOS_PILOTO], ["bola", "iguais_frutas"])
        assert bv.cfg_rede_da_config(cb).passo == p


def test_o_ponto_e_o_da_k2_e_o_corpo_e_o_do_passo0():
    c = _cfg()
    k2 = json.loads((RAIZ / "artifacts_v2_calibracao_conjunta" / "escolha.json").read_text(encoding="utf-8"))["ponto"]
    assert c["lobos"] == {"memoria_ganho": k2["g"], "w0_pedido": k2["w0_pedido"], "w0_info": k2["w0_info"]}
    assert c["consequencia"] == {"ganho": k2["ganho"], "canais_ligados": True}
    passo0 = json.loads((RAIZ / c["passo0"]).read_text(encoding="utf-8"))["escolha"]
    assert passo0["fechou"] and c["corpo"] == passo0["corpo"]


def test_a_fumaca_e_a_mesma_config_nas_sementes_dos_testes():
    c, f = _cfg(), _cfg(FUMACA)
    assert rc.modo_da_config(f) == "fumaca"
    for k in ("lobos", "consequencia", "corpo", "passo0", "grade_passo", "montagem", "ponto", "sonda"):
        assert f[k] == c[k], k


@pytest.mark.parametrize("mexe,erro", [
    (lambda c: c["unidades"].update(bases=[44101, 44202, 44303, 44404, 44505]), bv.SementeSemPlano),   # a validacao
    (lambda c: c["unidades"].update(bases=[43101, 43202]), bv.SementeSemPlano),
    (lambda c: c["unidades"].update(prefixo="corpo"), ValueError),
    (lambda c: c["corpo"].update(gasto_basal_acordado=375), ValueError),
    (lambda c: c.update(grade_passo=[64, 16]), ValueError),
    (lambda c: c.update(dias=7), ValueError),
    (lambda c: c["poder"].update(replicas=100), ValueError),
    (lambda c: c.update(extra=1), ValueError),
])
def test_as_recusas(mexe, erro):
    c = _cfg()
    mexe(c)
    with pytest.raises(erro):
        rc.modo_da_config(c)


def test_recusa_a_pasta_que_existe(tmp_path):
    with pytest.raises(FileExistsError):
        rc.rodar(_cfg(FUMACA), tmp_path, 1)


# ------------------------------------------------------------------ 2. a regra, a margem e o N


def _grade(valores: dict) -> list[dict]:
    """valores: passo -> [(mae, no_teto), ...] por unidade"""
    n = len(next(iter(valores.values())))
    return [{"por_passo": {str(p): {"mae_rede_1": v[i][0], "no_teto": v[i][1]} for p, v in valores.items()}} for i in range(n)]


def test_a_regra_do_passo():
    g = _grade({16: [(10, False), (12, False)], 64: [(8, False), (9, True)], 256: [(5, True), (5, True)]})
    e = rc.escolher_passo(g, [16, 64, 256])
    # o 256 sai (2 de 2 vidas no teto); o 64 fica (1 de 2 nao passa da metade) e tem o menor MAE
    assert e["passo"] == 64 and e["fechou"] and e["pontos"]["256"]["fora_pelo_teto"] and not e["pontos"]["64"]["fora_pelo_teto"]
    assert e["pontos"]["64"]["mae_rede_1"] == 8.5
    empate = rc.escolher_passo(_grade({16: [(7, False)], 64: [(7, False)]}), [16, 64])
    assert empate["passo"] == 16                                          # empate: o menor passo
    todos = rc.escolher_passo(_grade({16: [(1, True)], 64: [(2, True)]}), [16, 64])
    assert todos["passo"] == 16 and not todos["fechou"]
    with pytest.raises(ValueError):
        rc.escolher_passo(_grade({16: [(None, False)]}), [16])


def _reg(braco, base, k, **kw):
    r = {"braco": braco, "base": base, "k": k, "d_si": 0.0, "d_media": 0.0, "distancia_pers_oraculo": 0.0, "bss_ped": None,
         "bss_nasc": None, "d_adapta": 0.0, "distancia_cong_oraculo": 0.0, "mae_4": {"rede": 0, "persistencia": 0, "media": 0, "oraculo": 0}}
    r.update(kw)
    return r


def test_a_margem():
    regs = [_reg("P1-c", 101, i, distancia_pers_oraculo=d) for i, d in enumerate([10.0, 20.0, 30.0])] + [_reg("P0-c", 101, 9)]
    m = rc.margens(regs)
    assert m["distancia_pers_oraculo"] == 20.0 and m["delta_si"] == 10.0 and m["delta_media"] == 10.0
    assert m["delta_bss"] == 0.1 and m["delta_adapta"] is None and m["validacao_roda"]            # sem P1-c-lenta
    no_limiar = rc.margens([_reg("P1-c", 101, 0, distancia_pers_oraculo=8.0)])
    assert not no_limiar["validacao_roda"]                               # <= S/128 (8): a validacao nao roda
    assert not rc.margens([_reg("P1-c", 101, 0, distancia_pers_oraculo=-3.0)])["validacao_roda"]
    with pytest.raises(ValueError):
        rc.margens([_reg("P1-c", 101, 0, distancia_pers_oraculo=None)])


def test_n_efetivo_e_o_poder():
    assert rc.n_efetivo(20, 15, 20) == 15 and rc.n_efetivo(30, 1, 4) == 7
    with pytest.raises(ValueError):
        rc.n_efetivo(10, 0, 0)
    regs = [_reg("P1-c", b, k, d_si=10.0 + (k - 1.5) * 2, d_media=5.0 + k) for b in (101, 202) for k in range(4)]
    regs += [_reg("P1+ped-c", b, k, bss_ped=(0.2 if k < 2 else None), bss_nasc=0.1 * k) for b in (101, 202) for k in range(4)]
    marg = {"delta_si": 10.0, "delta_media": 10.0, "delta_bss": 0.1, "delta_adapta": None}
    poder = {**_cfg()["poder"], "replicas": 200}
    pn = rc.poder_e_n(regs, marg, poder, 4242, 2)
    assert pn["n"]["chega_ao_alvo"] and pn["n"]["k"] == 4 and pn["n"]["n"] == 8      # D_SI ~10 com dispersao 2: o K minimo basta
    ped = pn["secundarios"]["G-AUT-PED"]
    assert (ped["com_valor"], ped["total"], ped["n_efetivo"]) == (4, 8, 4)
    assert pn["secundarios"]["G-ADAPTA"]["poder"] is None           # sem P1-c-lenta nem Delta_ADAPTA
    sem = rc.poder_e_n([r for r in regs if r["braco"] == "P1-c"] + [_reg("P1+ped-c", 101, 0, bss_ped=0.3)], marg, poder, 4242, 2)
    assert sem["secundarios"]["G-AUT-PED"]["poder"] is None and sem["secundarios"]["G-AUT-NASC"]["com_valor"] == 0


# ------------------------------------------------------------------ 3. a grade numa vida real


def test_a_medida_da_grade_e_a_mesma_vida_em_todo_passo(tmp_path):
    c = _cfg(FUMACA)
    u = bv.unidades_derivadas([101], 1, "rede_de_si")[0]
    g = rc.tarefa_grade(c, u, str(tmp_path))
    assert set(g["por_passo"]) == {"16", "64", "256"} and len(g["log_sha256"]) == 64
    assert (tmp_path / "vidas" / f"{g['vida']}.jsonl").is_file()
    for p in g["por_passo"].values():
        assert p["n"] == 7 * 96 and p["mae_rede_1"] > 0 and isinstance(p["no_teto"], bool)
    # a taxa lenta: o P1-c-lenta com cada taxa da grade, a troca conferida, a fome dos dias 8 a 10
    assert set(g["lenta"]) == {str(t) for t in rc.GRADE_TAXA_LENTA} and g["fome_p1c_dias_8_10"] is not None
    assert all(x["fome_dias_8_10"] is not None for x in g["lenta"].values())
    # com o passo 0 a rede e a persistencia: o MAE da regra e o da persistencia, exato
    b = bv.bancada_da_config(rc.config_bancada(c, 64, ["P1-c"], ["bola"]))
    b0 = replace(b, cfg_rede=replace(b.cfg_rede, passo=0))
    v = b0.vida(bv.EspecVida("atencioso", "P1-c", u["semente"], u["genoma"], "bola"))
    rede = bv.rede_de(v.motor.politica).rede
    m = rc.medidas_da_grade(rede, 0)
    leituras = [r["leituras"] for r in rede.registros]
    pers = mae_previsao(leituras, previsao_persistencia(leituras), 1, range(7 * 96), list(rede.receptores))   # os dias 1 a 7
    assert m["mae_rede_1"] == pers["mae"] and m["cortes"] == 0 and m["no_teto"] is False


# ------------------------------------------------------------------ 4. a fumaca inteira


def test_a_fumaca_inteira(tmp_path):
    saida = tmp_path / "cal"
    r = rc.rodar(_cfg(FUMACA), saida, 1, FUMACA)
    for nome in ("meta.json", "escolha.json", "resultado.json", "medidas.json", "grade/grade.json", "piloto/medidas.json"):
        assert (saida / nome).is_file(), nome
    res = r["resultado"]
    assert res["passo"] in (16, 64, 256) and res["passo"] == r["escolha"]["passo"]
    assert res["taxa_lenta"] in rc.GRADE_TAXA_LENTA and res["taxa_lenta"] == res["escolha"]["taxa_lenta"]["taxa"]
    assert len(r["piloto"]) == 3 * len(rc.BRACOS_PILOTO)
    assert {p["braco"] for p in r["piloto"].values()} == {b for b, _ in rc.BRACOS_PILOTO}
    m = res["margens"]
    assert m["delta_si"] == 0.5 * m["distancia_pers_oraculo"]
    if m["validacao_roda"]:
        assert "n" in res and res["custo"]["validacao"]["k"] == res["n"]["k"]
    else:
        assert "n" not in res and "volta ao Matheus" in res["leitura"]
    meta = json.loads((saida / "meta.json").read_text(encoding="utf-8"))
    assert meta["modo"] == "fumaca" and set(meta["sha256"]) >= {"rede_de_si.py", "lobos.py", "corpo.py", "config.py", "engine.py"}
    assert meta["bancada"]["cfg_rede"]["ligada"]


def test_a_regra_da_taxa_lenta():
    C = rc.C
    taxas = [C // 2, C // 4, C // 8]

    def g(p1, l2, l4, l8):
        return {"fome_p1c_dias_8_10": p1, "lenta": {str(C // 2): {"fome_dias_8_10": l2}, str(C // 4): {"fome_dias_8_10": l4},
                                                    str(C // 8): {"fome_dias_8_10": l8}}}
    # C//2 muda 30 (nao passa de S/16 = 64); C//4 muda 80; C//8 muda 200: fica a MAIOR que passa, C//4
    e = rc.escolher_taxa_lenta([g(900, 870, 820, 700), g(900, 870, 820, 700)], taxas)
    assert e["taxa"] == C // 4 and e["fechou"] and not e["pontos"][str(C // 2)]["passa"] and e["pontos"][str(C // 4)]["passa"]
    nenhuma = rc.escolher_taxa_lenta([g(900, 890, 880, 870)], taxas)
    assert nenhuma["taxa"] == C // 8 and not nenhuma["fechou"]
    with pytest.raises(ValueError):
        rc.escolher_taxa_lenta([g(None, 1, 1, 1)], taxas)
