"""Os testes do descritivo da D-C1-3 (adendo 10, A10.8): nas sementes dos testes (101...505), sem tocar nas vidas da C1.

Confere: que a particao de A10.4 cobre cada episodio uma vez so e que as somas fecham; que o script falha alto com codigo diferente do
`meta.json`; que duas execucoes saem iguais, byte a byte. Vive um punhado de vidas pequenas com o codigo de hoje (o `lr.viver` da C1),
grava os logs num tar, monta um `meta.json` do codigo de hoje e roda o mesmo caminho do script real (`principal`).
"""
from __future__ import annotations

import io
import json
import sys
import tarfile
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import descritivo_dc13_longe_fixo as dc  # noqa: E402
import run_v2_longe_regular as lr  # noqa: E402

SEMENTES = (101, 202, 303)                           # as sementes dos testes
DONOS = ("atencioso", "relapso")
DIAS, ORCAMENTO = 14, 16
META_DA_C1 = RAIZ / "artifacts_v2_digibrain_prototipo" / "longe_regular" / "run" / "meta.json"


def _meta_de_hoje() -> dict:
    """o meta.json do codigo de hoje, no formato do da run (para o caminho real do script)"""
    cfg = "experiments/configs/v2_longe_regular/longe_regular.json"
    real = json.loads(META_DA_C1.read_text(encoding="utf-8"))
    return {"git_head": "teste", "config": {"dias": DIAS, "orcamento_por_dia": ORCAMENTO}, "config_arquivo": cfg,
            "config_sha256": dc._sha(RAIZ / cfg),
            "sha256": {rel: dc._sha(RAIZ / "digilab" / rel) for rel in real["sha256"]},
            "orquestrador_sha256": dc._sha(RAIZ / "experiments" / "run_v2_longe_regular.py"),
            "prototipo_sha256": dc._sha(RAIZ / "experiments" / "run_v2_digibrain_prototipo.py")}


@pytest.fixture(scope="module")
def mundo(tmp_path_factory):
    pasta = tmp_path_factory.mktemp("vidas_dc13")
    cfg = {"dias": DIAS, "orcamento_por_dia": ORCAMENTO}
    medidas = {}
    for s in SEMENTES:
        for dono in DONOS:
            for braco in dc.BRACOS:
                v = lr._vida(cfg, braco, dono, dc.ESTILO, {"semente": s, "base": s, "k": 0}, str(pasta))
                medidas[v["vida"]] = json.loads(json.dumps(v))
    tar = pasta / "vidas.tar.gz"
    with tarfile.open(tar, "w:gz") as t:
        for arq in sorted((pasta / "vidas").rglob("*.jsonl")):
            t.add(arq, arcname=f"vidas/{arq.parent.name}/{arq.name}")
    return {"medidas": medidas, "tar": tar, "meta": _meta_de_hoje(), "pasta": pasta}


def _rodar(m, saida: Path) -> dict:
    return dc.principal(RAIZ, m["meta"], m["medidas"], m["tar"], saida, 1, {"teste": "sem fonte"}, None, donos=DONOS)


@pytest.fixture(scope="module")
def duas(mundo, tmp_path_factory):
    pasta = tmp_path_factory.mktemp("saidas_dc13")
    a, b = _rodar(mundo, pasta / "a" / "d.json"), _rodar(mundo, pasta / "b" / "d.json")
    dc.gravar(pasta / "a" / "d.json", a)
    dc.gravar(pasta / "b" / "d.json", b)
    return a, b, pasta


def test_a_particao_cobre_cada_episodio_uma_vez_e_as_somas_fecham(mundo, duas):
    a, _b, _p = duas
    s2 = a["estagio2"]
    assert a["vidas"] == len(SEMENTES) * len(DONOS) * len(dc.BRACOS)
    assert a["g1"] == {"vidas_refeitas": a["vidas"], "todas_iguais": True}
    for braco, cob in s2["cobertura"].items():
        gravados = [v for v in mundo["medidas"].values() if v["braco"] == braco]
        assert cob["vidas"] == len(gravados)
        assert cob["episodios"] == sum(v["episodios_fome"]["n"] for v in gravados)       # cada episodio entra uma vez
        assert sum(cob["F"].values()) == sum(v["episodios_fome"]["fechados"] for v in gravados)
        assert sum(cob["F"].values()) + sum(cob["P"].values()) == cob["episodios"]
        if braco != "M3":                                  # sem o M-MEM nao ha ida ao lugar lembrado
            assert cob["F"]["F-b"] == 0
    assert sum(sum(c["F"].values()) for c in s2["cobertura"].values()) > 0                 # o teste tem episodios fechados de verdade
    fecha = s2["soma_das_parcelas"]
    assert fecha["F"] == pytest.approx(fecha["G"], abs=1e-12)
    assert fecha["P"] == pytest.approx(fecha["G"], abs=1e-12)
    # o G recalculado e a soma das parcelas por unidade
    soma = sum(s2["A"][p]["M3-M2"]["media"] for p in dc.PARTES_F)
    assert soma == pytest.approx(a["estagio1"]["G"], abs=1e-12)
    assert a["leitura"]["linha"]


def test_o_script_falha_alto_com_codigo_diferente_do_meta(mundo, tmp_path):
    meta = json.loads(json.dumps(mundo["meta"]))
    assert dc.conferir_codigo(RAIZ, meta)["iguais_ao_meta"] is True
    primeiro = sorted(meta["sha256"])[0]
    meta["sha256"][primeiro] = "0" * 64
    with pytest.raises(RuntimeError, match="nao e o da run"):
        dc.conferir_codigo(RAIZ, meta)
    with pytest.raises(RuntimeError, match=primeiro):
        dc.principal(RAIZ, meta, mundo["medidas"], mundo["tar"], tmp_path / "x" / "d.json", 1, {}, None, donos=DONOS)
    assert not (tmp_path / "x").exists()
    # o meta.json da C1 de verdade: o codigo de hoje nao e o do 7683c0e (11 modulos mudaram), e o script nao roda com ele
    real = json.loads(META_DA_C1.read_text(encoding="utf-8"))
    with pytest.raises(RuntimeError, match="nao e o da run"):
        dc.conferir_codigo(RAIZ, real)


def test_o_g1_falha_alto_com_a_medida_gravada_diferente(mundo, tmp_path):
    medidas = json.loads(json.dumps(mundo["medidas"]))
    vida = sorted(medidas)[0]
    medidas[vida]["reflexos"] += 1
    with pytest.raises(RuntimeError, match="G1 do descritivo"):
        dc.principal(RAIZ, mundo["meta"], medidas, mundo["tar"], tmp_path / "y" / "d.json", 1, {}, None, donos=DONOS)


def test_duas_execucoes_saem_iguais_byte_a_byte(duas):
    a, b, pasta = duas
    assert a == b
    assert (pasta / "a" / "d.json").read_bytes() == (pasta / "b" / "d.json").read_bytes()


def test_roda_uma_vez(mundo, duas):
    _a, _b, pasta = duas
    with pytest.raises(FileExistsError):
        _rodar(mundo, pasta / "a" / "d.json")


def test_a_regra_de_leitura_na_ordem_de_a10_5():
    def est(media, lo, hi, G=0.05):
        cls = "> 0" if lo > 0 else ("< 0" if hi < 0 else "indeterminado")
        return {"media": media, "s": media / G, "ic95": {"ic_inferior": lo, "ic_superior": hi}, "classe": {"classe": cls}}

    def s2(d1, **h):
        base = {k: est(0.0, -0.01, 0.01) for k in ("H1", "H1'", "H2", "H3", "F-d_sem_modulo")}
        base.update(h)
        return {"hipoteses": base, "D1": {"M3-M2": {"classe_sinal": d1[0], "ic95": {"ic_inferior": d1[1], "ic_superior": d1[2]}}},
                "A": {"F-c": {"M3-M2": {"classe": {"classe": "indeterminado"}}}}}

    s1 = {"H4": {"cumpre": False}}
    assert "aponta para H1" in dc.ler(s1, s2(("< 0", -2, -1), H1=est(0.04, 0.03, 0.05)))["linha"]
    # F-a explica, mas sem D1 "< 0": nao aponta H1
    r = dc.ler(s1, s2(("indeterminado", -1, 1), H1=est(0.04, 0.03, 0.05)))
    assert r["H1_sem_D1"] and r["linha"].startswith("indeterminado")
    assert "mistura de posicao e custo" in dc.ler(s1, s2(("< 0", -2, -1), H1=est(0.04, 0.03, 0.05), H3=est(0.03, 0.02, 0.04)))["linha"]
    assert dc.ler(s1, s2(("> 0", 1, 2), H2=est(0.02, 0.01, 0.03), H3=est(0.02, 0.01, 0.03)))["linha"].startswith("mistura")
    assert dc.ler({"H4": {"cumpre": True}}, s2(("< 0", -2, -1), H1=est(0.04, 0.03, 0.05)))["linha"].startswith("o ganho e da medida")
