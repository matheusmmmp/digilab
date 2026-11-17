"""Testes do orquestrador da EVIDENCIA A1 (experiments/run_v3_baseline_trivial.py): a trava, a regra da grade, a leitura, o tar
determinístico e as duas fumaças (a calibração com uma grade de 2 pontos; a validação com os limiares lidos dela)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "experiments"))
import bancada_v2 as bv  # noqa: E402
import run_v3_baseline_trivial as bt  # noqa: E402

CONFIGS = RAIZ / "experiments" / "configs" / "v3_baseline_trivial"


def _cfg(nome: str) -> dict:
    return json.loads((CONFIGS / f"{nome}.json").read_text(encoding="utf-8"))


def test_as_configs_das_etapas_seguem_o_plano():
    for nome, etapa in (("calibracao", "calibracao"), ("validacao", "validacao")):
        c = _cfg(nome)
        assert c["etapa"] == etapa and tuple(c["unidades"]["bases"]) == bt.BASES[etapa] and c["unidades"]["k"] == bt.K_POR_BASE[etapa]
    assert bt.modo_da_config(_cfg("fumaca_calibracao")) == "fumaca" and bt.modo_da_config(_cfg("fumaca_validacao")) == "fumaca"


def test_as_faixas_estao_reservadas_e_nao_colidem():
    for etapa in bt.ETAPAS:
        bt.exigir_faixa_reservada(etapa)
        outras = [(lo, hi) for lo, hi, _ in bv.FAIXAS_RESERVADAS if (lo, hi) != bt.FAIXA[etapa]]
        assert all(hi < bt.FAIXA[etapa][0] or lo > bt.FAIXA[etapa][1] for lo, hi in outras)


def test_a_trava_recusa_o_plano_sem_o_aprovado():
    with pytest.raises(RuntimeError, match="APROVADO"):
        bt.exigir_plano_aprovado("# plano\n\n**Status: PROPOSTO, aguardando o Matheus**\n")
    bt.exigir_plano_aprovado("# plano\n\n**Status: APROVADO pelo Matheus em 2026-11-16**\n")


def test_semente_fora_da_faixa_falha_alto():
    c = _cfg("validacao")
    c["unidades"]["bases"] = [12345]
    with pytest.raises(bv.SementeSemPlano):
        bt.modo_da_config(c)


def _reg(ponto, semente, dono, taxa):
    return {"ponto": list(ponto), "braco": bt.TRIV, "dono": dono, "lugar": bt.PRIMARIO, "semente": semente, "base": 1,
            "episodios_fome": {"taxa": taxa}}


def test_a_regra_da_grade_escolhe_a_maior_media_e_desempata_pelo_menor(monkeypatch):
    monkeypatch.setattr(bt, "GRADE", {"fome": (0.4, 0.5), "energia": (0.2,), "tedio": (1.0,)})
    regs = [_reg(p, s, d, t) for p, t in (((0.4, 0.2, 1.0), 0.6), ((0.5, 0.2, 1.0), 0.7)) for s in (1, 2) for d in bt.DONOS]
    assert bt.escolher_ponto(regs)["escolhido"]["fome"] == 0.5
    regs = [_reg(p, s, d, 0.6) for p in ((0.4, 0.2, 1.0), (0.5, 0.2, 1.0)) for s in (1, 2) for d in bt.DONOS]
    assert bt.escolher_ponto(regs)["escolhido"]["fome"] == 0.4                     # o empate exato fica com o menor


def test_a_leitura_escrita_antes():
    def prim(lo, hi):
        return {"classe": bt.classe({"ic_inferior": lo, "ic_superior": hi, "motivo": None}), "ic95": {"ic_inferior": lo, "ic_superior": hi}}
    assert bt.leitura(prim(0.05, 0.08)) == {"classe": "> 0", "exclui_trivial": True, "texto": bt.leitura(prim(0.05, 0.08))["texto"]}
    assert bt.leitura(prim(0.01, 0.05))["exclui_trivial"] is False and bt.leitura(prim(0.01, 0.05))["classe"] == "> 0"
    assert bt.leitura(prim(-0.01, 0.02))["classe"] == "≈ 0"
    assert bt.leitura(prim(-0.08, -0.04))["classe"] == "< 0"
    assert bt.leitura(prim(-0.05, 0.05))["classe"] == "indeterminado"


def test_o_tar_e_igual_byte_a_byte(tmp_path):
    for raiz in (tmp_path / "a", tmp_path / "b"):
        (raiz / "vidas" / "X").mkdir(parents=True)
        (raiz / "vidas" / "X" / "v1.jsonl").write_text("1\n")
        (raiz / "vidas" / "X" / "v0.jsonl").write_text("0\n")
        bt.tar_deterministico(raiz / "vidas", raiz / "vidas.tar.gz")
    assert (tmp_path / "a" / "vidas.tar.gz").read_bytes() == (tmp_path / "b" / "vidas.tar.gz").read_bytes()


def test_as_fumacas_rodam_e_a_validacao_le_os_limiares_da_calibracao(tmp_path, monkeypatch):
    monkeypatch.setattr(bt, "GRADE", {"fome": (0.5,), "energia": (0.2, 0.3), "tedio": (1.0,)})
    cal = bt.rodar(_cfg("fumaca_calibracao"), tmp_path / "cal", 1)
    assert cal["resultado"]["vidas"] == 2 * len(bt.DONOS) and len(cal["resultado"]["pontos"]) == 2
    assert set(cal["meta"]["artefatos_sha256"]) == {"medidas.json", "resultado.json"}
    val = bt.rodar(_cfg("fumaca_validacao"), tmp_path / "val", 1, pasta_cal=tmp_path / "cal")
    m = val["meta"]
    assert m["bracos"][bt.TRIV] == cal["resultado"]["escolhido"] and m["calibracao"]["resultado_sha256"] == cal["meta"]["artefatos_sha256"]["resultado.json"]
    assert {"medidas.json", "resultado.json", "vidas.tar.gz"} <= set(m["artefatos_sha256"]) and m["python"] and "comando" in m
    assert val["resultado"]["vidas"] == len(bt.BRACOS) * len(bt.CELULAS)
    assert val["resultado"]["leitura"]["classe"] in ("> 0", "≈ 0", "< 0", "indeterminado")
    with pytest.raises(FileExistsError):
        bt.rodar(_cfg("fumaca_validacao"), tmp_path / "val", 1, pasta_cal=tmp_path / "cal")
    (tmp_path / "cal" / "resultado.json").write_text("{}")                         # a calibracao adulterada falha alto
    with pytest.raises(RuntimeError, match="nao confere"):
        bt.rodar(_cfg("fumaca_validacao"), tmp_path / "val2", 1, pasta_cal=tmp_path / "cal")
