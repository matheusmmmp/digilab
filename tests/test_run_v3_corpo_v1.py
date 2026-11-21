"""O orquestrador da V1-a, o teto baixo no pet do jogo (experiments/run_v3_corpo_v1.py; docs/PLANO_ANALISE_V3_CORPO_V1.md): o pet v38
com as chaves do braco, o CTRL igual ao pet v38 da PET_VIVO byte a byte, a conferencia do pet, a regra da C4 sem o S2, as premissas sem
a dos pares, a trava da config e uma fumaca nas sementes dos testes, com o relogio fora das medidas."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import pv2  # noqa: E402
import run_v3_corpo_c3 as C3  # noqa: E402
import run_v3_corpo_c4 as C4  # noqa: E402
import run_v3_corpo_v1 as R  # noqa: E402

FUMACA = json.loads((RAIZ / "experiments/configs/v3_corpo_v1/fumaca.json").read_text(encoding="utf-8"))
RUN = json.loads((RAIZ / "experiments/configs/v3_corpo_v1/run.json").read_text(encoding="utf-8"))
GUARDAS = {"saude_12_celulas", "saude_sem_comida", C4.G_TAXA, "tempo_bem_comedouro", "tempo_bem_longe", "tempo_bem_longe_fixo"}


def _sha(motor) -> str:
    return hashlib.sha256(motor.log.para_jsonl().encode("utf-8")).hexdigest()


def test_os_bracos_as_celulas_e_a_margem_sao_os_da_c4():
    assert R.BRACOS == ("CTRL", "DTB") and R.TRATADO in C3.COM_TETO
    assert len(R.CELULAS) == 12 and len(R.CELULAS_DISTINTAS) == 11 and len(R.CELULAS_SEM_COMIDA) == 6
    assert (R.MARGEM, R.ALFA) == (C4.MARGEM, C4.ALFA) == (0.032, 0.025)       # D-V1A-5: a margem nao muda
    assert R.PISOS == {k: v for k, v in C4.PISOS.items() if k != "pares_com_a_janela_min"}
    with pytest.raises(ValueError):
        R._vida(FUMACA, "D", "relapso", "comedouro", {"semente": 101, "base": 101, "k": 0}, "nao_usa")


@pytest.mark.parametrize("dono, lugar, semente", [("relapso", "longe_fixo", 101), ("atencioso", "comedouro", 202)])
def test_o_ctrl_e_o_pet_v38_da_pet_vivo_byte_a_byte(dono, lugar, semente):
    motor, registro, _fab, _cat, baixas = R.viver("CTRL", dono, lugar, semente, 2, R.ORCAMENTO_POR_DIA)
    hoje, registro_hoje, _ = pv2.viver("HOJE", dono, lugar, semente, 2, v38=True)
    assert _sha(motor) == _sha(hoje) and registro.estados == registro_hoje.estados
    R.conferir_vida("CTRL", motor, registro, baixas)


def test_o_dtb_tem_as_chaves_do_corpo_e_o_mesmo_pet():
    motor, registro, _fab, _cat, baixas = R.viver("DTB", "relapso", "longe_fixo", 101, 2, R.ORCAMENTO_POR_DIA)
    R.conferir_vida("DTB", motor, registro, baixas)
    assert motor.corpo.ca.ligada and motor.corpo.ctf.teto == 225_000
    ctrl, *_ = R.viver("CTRL", "relapso", "longe_fixo", 101, 2, R.ORCAMENTO_POR_DIA)
    assert _sha(motor) != _sha(ctrl)                                          # a chave muda a vida


def test_a_conferencia_recusa_o_pet_da_bancada_e_o_braco_trocado():
    motor, registro, _fab, _cat, baixas = C3.viver("CTRL", "relapso", "longe_fixo", 101, 1, R.ORCAMENTO_POR_DIA)
    with pytest.raises(RuntimeError, match="nao e o v38"):
        R.conferir_vida("CTRL", motor, registro, baixas)
    motor, registro, _fab, _cat, baixas = R.viver("CTRL", "relapso", "longe_fixo", 101, 1, R.ORCAMENTO_POR_DIA)
    with pytest.raises(RuntimeError):
        R.conferir_vida("DTB", motor, registro, baixas)


def _prim(c12="> 0", c11="> 0", p12=0.001, p11=0.001):
    return {"12_celulas": {"classe": {"classe": c12}, "p_unilateral": p12}, "11_celulas": {"classe": {"classe": c11}, "p_unilateral": p11}}


def _g(reprova=()):
    return {n: {"passa": n not in reprova} for n in GUARDAS}


def _cel(ressalva=()):
    return {f"{d}|{lugar}": {"passa": f"{d}|{lugar}" not in ressalva} for d, lugar in R.CELULAS_SEM_COMIDA}


def _prem(descumpre=()):
    de = {"tempo_bem_fora_do_piso_e_do_teto": C4.P_PRIMARIA, "ponte_no_teto": C4.P_BRACO, "episodios_de_fome": C4.G_TAXA,
          "chutes_no_longe_fixo": "descritivo_dos_chutes"}
    return {n: {"mede": m, "cumpre": n not in descumpre} for n, m in de.items()}


@pytest.mark.parametrize("args, leitura", [
    ((_prim(), _g(), _cel(), _prem()), "confirma"),
    ((_prim(), _g(), _cel(("aleatorio|comedouro",)), _prem()), "confirma com ressalva"),
    ((_prim(), _g(("tempo_bem_comedouro",)), _cel(), _prem()), "nao confirma"),
    ((_prim(), _g(("saude_sem_comida",)), _cel(("aleatorio|comedouro",)), _prem()), "nao confirma"),
    # a previsao do plano: um ganho dentro da margem sai "≈ 0", e a regra le "nao confirma"
    ((_prim(c12="≈ 0", c11="≈ 0"), _g(), _cel(), _prem()), "nao confirma"),
    ((_prim(c11="≈ 0"), _g(), _cel(), _prem()), "nao confirma"),
    ((_prim(c12="< 0"), _g(), _cel(), _prem()), "nao confirma"),
    ((_prim(p11=0.03), _g(), _cel(), _prem()), "nao confirma"),
    ((_prim(c12="indeterminado"), _g(("saude_12_celulas",)), _cel(), _prem()), "indeterminado"),
    ((_prim(), _g(), _cel(), _prem(("tempo_bem_fora_do_piso_e_do_teto",))), "indeterminado"),
    ((_prim(), _g(), _cel(), _prem(("ponte_no_teto",))), "indeterminado"),
    ((_prim(), _g(), _cel(), _prem(("episodios_de_fome",))), "indeterminado"),
    ((_prim(), _g(), _cel(), _prem(("chutes_no_longe_fixo",))), "confirma"),
])
def test_a_regra_de_leitura_e_a_da_c4_sem_o_s2(args, leitura):
    v = R.leitura(*args)
    assert v["leitura"] == leitura and v["proximo"] == R.PROXIMO and "V1" in v["proximo"]


def _vida(braco, lugar, **kw):
    base = {"braco": braco, "lugar": lugar, "tempo_bem": 0.6, "episodios_fome": {"n": 12}, "fracao_ticks_teto": 0.3 if braco == "DTB" else 0.0,
            "chutes": 2}
    return {**base, **kw}


def test_as_premissas_sao_as_da_c4_sem_a_dos_pares():
    vidas = [_vida(b, lugar) for b in R.BRACOS for lugar in R.LUGARES for _ in range(10)]
    p = R.premissas(vidas)
    assert set(p) == {"tempo_bem_fora_do_piso_e_do_teto", "ponte_no_teto", "episodios_de_fome", "chutes_no_longe_fixo"}
    assert all(x["cumpre"] for x in p.values())
    no_teto = [_vida(b, lugar, tempo_bem=1.0 if i == 0 else 0.6) for b in R.BRACOS for lugar in R.LUGARES for i in range(10)]
    assert not R.premissas(no_teto)["tempo_bem_fora_do_piso_e_do_teto"]["cumpre"]
    sem_corte = [_vida(b, lugar, fracao_ticks_teto=0.01) for b in R.BRACOS for lugar in R.LUGARES for _ in range(10)]
    assert not R.premissas(sem_corte)["ponte_no_teto"]["cumpre"]


def test_a_trava_e_a_config():
    assert R.modo_da_config(FUMACA) == "fumaca"
    assert tuple(RUN["unidades"]["bases"]) == R.BASES and len(R.BASES) == 200 and RUN["unidades"]["k"] == R.K_POR_BASE == 1
    assert (R.BASES[0], R.BASES[-1]) == R.FAIXA and "pares" not in RUN
    assert any((lo, hi) == R.FAIXA for lo, hi, _ in bv.FAIXAS_RESERVADAS)
    assert not set(R.BASES) & set(C4.BASES_I + C4.BASES_II + C3.BASES_I + C3.BASES_II)
    with pytest.raises(bv.SementeSemPlano):
        R.modo_da_config({**RUN, "unidades": {**RUN["unidades"], "bases": RUN["unidades"]["bases"][:100]}})
    with pytest.raises(ValueError):
        R.modo_da_config({**FUMACA, "fase": "corpo_c4"})
    with pytest.raises(ValueError):
        R.modo_da_config({**FUMACA, "pares": {"bases": [101]}})


def test_a_run_so_roda_com_o_plano_aprovado():
    assert R.modo_da_config(RUN) == R.FASE
    assert "APROVADO pelo Matheus" in (RAIZ / R.PLANO).read_text(encoding="utf-8")


def test_a_fumaca_roda_com_o_relogio_fora_das_medidas(tmp_path):
    cfg = {**FUMACA, "unidades": {**FUMACA["unidades"], "bases": [101]}}
    r = R.rodar(cfg, tmp_path / "f", 1)
    res = r["resultado"]
    assert res["vidas"] == len(R.BRACOS) * len(R.CELULAS) and "pares" not in res
    assert set(res["primaria"]) == {"12_celulas", "11_celulas"} and set(res["guardas"]) == GUARDAS
    assert set(res["saude_por_celula"]) == {f"{d}|{lugar}" for d, lugar in R.CELULAS_SEM_COMIDA}
    assert set(res["premissas"]) == {"tempo_bem_fora_do_piso_e_do_teto", "ponte_no_teto", "episodios_de_fome", "chutes_no_longe_fixo"}
    assert res["veredito"]["leitura"] in ("confirma", "confirma com ressalva", "nao confirma", "indeterminado")
    d = res["descritivo"]
    assert set(d["chutes"]) == set(R.LUGARES) and "privacao_comedouro" in d["as_oito_guardas_da_c3"]
    assert {"fome_media", "fome_acima_do_teto", "tempo_bem_perto_do_teto", "tempo_bem"} <= set(d["por_lugar"]["12_celulas"])
    assert set(d["por_dono"]) == {f"{dn}|{lugar}" for dn, lugar in R.CELULAS}
    pasta = tmp_path / "f"
    for n in ("medidas.json", "custos.json", "resultado.json", "vidas.tar.gz", "meta.json"):
        assert (pasta / n).exists()
    assert not (pasta / "vidas").exists() and r["meta"]["pasta_crua_apagada"] == {"vidas": res["vidas"]}
    medidas = json.loads((pasta / "medidas.json").read_text(encoding="utf-8"))
    custos = json.loads((pasta / "custos.json").read_text(encoding="utf-8"))
    assert all("custo" not in m and 0.0 <= m["tempo_bem"] <= 1.0 and 0.0 <= m["fome_media"] <= 1.0 and m["chutes"] >= 0 for m in medidas)
    assert set(custos) == {m["vida"] for m in medidas} and all(set(c) == {"vida_cpu", "vida_parede"} for c in custos.values())
    with pytest.raises(FileExistsError):
        R.rodar(cfg, pasta, 1)
    # sem o relogio, as medidas e o resultado de uma replica saem iguais byte a byte
    r2 = R.rodar(cfg, tmp_path / "g", 1)
    assert r2["meta"]["artefatos_sha256"]["medidas.json"] == r["meta"]["artefatos_sha256"]["medidas.json"]
    assert r2["meta"]["artefatos_sha256"]["resultado.json"] == r["meta"]["artefatos_sha256"]["resultado.json"]
