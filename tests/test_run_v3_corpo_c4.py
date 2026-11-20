"""O orquestrador da C4, a validacao do teto baixo (experiments/run_v3_corpo_c4.py; docs/PLANO_ANALISE_V3_CORPO_C4.md): so o CTRL e o
DTB, a regra de leitura escrita antes (a primaria nas 12 e nas 11 celulas, as guardas, a ressalva e as premissas), a trava da config, o
pacote conferido antes de apagar a pasta crua e uma fumaca dos dois blocos, nas sementes dos testes, com o relogio fora das medidas."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v3_corpo_c3 as C3  # noqa: E402
import run_v3_corpo_c4 as R  # noqa: E402

FUMACA = json.loads((RAIZ / "experiments/configs/v3_corpo_c4/fumaca.json").read_text(encoding="utf-8"))
RUN = json.loads((RAIZ / "experiments/configs/v3_corpo_c4/run.json").read_text(encoding="utf-8"))


def test_so_o_ctrl_e_o_dtb_com_as_chaves_da_c3():
    assert R.BRACOS == ("CTRL", "DTB") and R.TRATADO in C3.COM_TETO
    assert len(R.CELULAS) == 12 and len(R.CELULAS_DISTINTAS) == 11 and len(R.CELULAS_SEM_COMIDA) == 6
    with pytest.raises(ValueError):
        R._vida(FUMACA, "D", "relapso", "comedouro", {"semente": 101, "base": 101, "k": 0}, "nao_usa")


def _prim(c12="> 0", c11="> 0", p12=0.001, p11=0.001):
    return {"12_celulas": {"classe": {"classe": c12}, "p_unilateral": p12}, "11_celulas": {"classe": {"classe": c11}, "p_unilateral": p11}}


def _g(reprova=()):
    nomes = ("saude_12_celulas", "saude_sem_comida", R.G_TAXA, "tempo_bem_comedouro", "tempo_bem_longe", "tempo_bem_longe_fixo", R.G_S2)
    return {n: {"passa": n not in reprova} for n in nomes}


def _cel(ressalva=()):
    return {f"{d}|{lugar}": {"passa": f"{d}|{lugar}" not in ressalva} for d, lugar in R.CELULAS_SEM_COMIDA}


def _prem(descumpre=()):
    de = {"tempo_bem_fora_do_piso_e_do_teto": R.P_PRIMARIA, "ponte_no_teto": R.P_BRACO, "episodios_de_fome": R.G_TAXA,
          "janela_do_reencontro": R.G_S2, "chutes_no_longe_fixo": "descritivo_dos_chutes"}
    return {n: {"mede": m, "cumpre": n not in descumpre} for n, m in de.items()}


@pytest.mark.parametrize("args, leitura", [
    ((_prim(), _g(), _cel(), _prem()), "confirma"),
    ((_prim(), _g(), _cel(("aleatorio|comedouro",)), _prem()), "confirma com ressalva"),
    ((_prim(), _g(("tempo_bem_comedouro",)), _cel(), _prem()), "nao confirma"),
    ((_prim(), _g((R.G_TAXA,)), _cel(("aleatorio|comedouro",)), _prem()), "nao confirma"),
    ((_prim(c11="≈ 0"), _g(), _cel(), _prem()), "nao confirma"),
    ((_prim(c12="< 0"), _g(), _cel(), _prem()), "nao confirma"),
    ((_prim(p11=0.03), _g(), _cel(), _prem()), "nao confirma"),
    ((_prim(c12="indeterminado"), _g(("saude_12_celulas",)), _cel(), _prem()), "indeterminado"),
    ((_prim(c12="indeterminado", c11="≈ 0"), _g(), _cel(), _prem()), "nao confirma"),
    ((_prim(), _g(), _cel(), _prem(("tempo_bem_fora_do_piso_e_do_teto",))), "indeterminado"),
    ((_prim(), _g(), _cel(), _prem(("ponte_no_teto",))), "indeterminado"),
    # a guarda sem premissa nao reprova e nao passa: a leitura nao chega a "confirma"
    ((_prim(), _g((R.G_S2,)), _cel(), _prem(("janela_do_reencontro",))), "indeterminado"),
    ((_prim(), _g(), _cel(), _prem(("episodios_de_fome",))), "indeterminado"),
    # os chutes sao so descritivo: a premissa deles nao muda a leitura
    ((_prim(), _g(), _cel(), _prem(("chutes_no_longe_fixo",))), "confirma"),
])
def test_a_regra_de_leitura_escrita_antes(args, leitura):
    assert R.leitura(*args)["leitura"] == leitura


def test_a_leitura_lista_o_que_reprova_e_o_que_fica_em_ressalva():
    v = R.leitura(_prim(), _g(("saude_sem_comida",)), _cel(("aleatorio|comedouro",)), _prem(("chutes_no_longe_fixo",)))
    assert v["reprovadas"] == ["saude_sem_comida"] and v["celulas_em_ressalva"] == ["aleatorio|comedouro"]
    assert v["premissas_descumpridas"] == ["chutes_no_longe_fixo"] and v["inconclusivas_por_premissa"] == []


def _vida(braco, lugar, **kw):
    base = {"braco": braco, "lugar": lugar, "tempo_bem": 0.6, "episodios_fome": {"n": 12}, "fracao_ticks_teto": 0.3 if braco == "DTB" else 0.0,
            "chutes": 2}
    return {**base, **kw}


def test_as_premissas_contam_o_evento_contra_o_piso():
    vidas = [_vida(b, lugar) for b in R.BRACOS for lugar in R.LUGARES for _ in range(10)]
    pares = [{"braco": b, "janela": {"cabe": True}} for b in R.BRACOS for _ in range(10)]
    p = R.premissas(vidas, pares)
    assert all(x["cumpre"] for x in p.values())
    assert p["ponte_no_teto"]["valores"]["comedouro"] == pytest.approx(0.3)
    assert {x["mede"] for x in p.values()} == {R.P_PRIMARIA, R.P_BRACO, R.G_TAXA, R.G_S2, "descritivo_dos_chutes"}
    # uma vida em 10 no teto da medida passa do piso de 5 %
    no_teto = [_vida(b, lugar, tempo_bem=1.0 if i == 0 else 0.6) for b in R.BRACOS for lugar in R.LUGARES for i in range(10)]
    assert not R.premissas(no_teto, pares)["tempo_bem_fora_do_piso_e_do_teto"]["cumpre"]
    poucos = [_vida(b, lugar, episodios_fome={"n": 3}) for b in R.BRACOS for lugar in R.LUGARES for _ in range(10)]
    assert not R.premissas(poucos, pares)["episodios_de_fome"]["cumpre"]
    sem_corte = [_vida(b, lugar, fracao_ticks_teto=0.01) for b in R.BRACOS for lugar in R.LUGARES for _ in range(10)]
    assert not R.premissas(sem_corte, pares)["ponte_no_teto"]["cumpre"]
    sem_bola = [_vida(b, lugar, chutes=0) for b in R.BRACOS for lugar in R.LUGARES for _ in range(10)]
    assert not R.premissas(sem_bola, pares)["chutes_no_longe_fixo"]["cumpre"]
    fora = [{"braco": b, "janela": {"cabe": i > 2}} for b in R.BRACOS for i in range(10)]
    assert not R.premissas(vidas, fora)["janela_do_reencontro"]["cumpre"]


def test_a_trava_e_a_config():
    assert R.modo_da_config(FUMACA) == "fumaca"
    assert tuple(RUN["unidades"]["bases"]) == R.BASES_I and tuple(RUN["pares"]["bases"]) == R.BASES_II
    assert len(R.BASES_I) == 200 and len(R.BASES_II) == 500 and RUN["unidades"]["k"] == RUN["pares"]["k"] == R.K_POR_BASE == 1
    assert R.BASES_I[0] == R.FAIXA[0] and R.BASES_II[-1] == R.FAIXA[1]
    assert any((lo, hi) == R.FAIXA for lo, hi, _ in bv.FAIXAS_RESERVADAS)
    assert not set(R.BASES_I + R.BASES_II) & set(C3.BASES_I + C3.BASES_II)
    errada = {**RUN, "pares": {**RUN["pares"], "bases": RUN["pares"]["bases"][:100]}}
    with pytest.raises(bv.SementeSemPlano):
        R.modo_da_config(errada)
    with pytest.raises(ValueError):
        R.modo_da_config({**FUMACA, "fase": "corpo_c3"})


def test_o_pacote_e_conferido_antes_de_apagar_a_pasta_crua(tmp_path):
    for nome in ("a", "b"):
        pasta = tmp_path / nome / "vidas"
        (pasta / "CTRL").mkdir(parents=True)
        (pasta / "CTRL" / "x.jsonl").write_text("um\n", encoding="utf-8", newline="\n")
        (pasta / "CTRL" / "y.jsonl").write_text("dois\n", encoding="utf-8", newline="\n")
        R.V.tar_deterministico(pasta, tmp_path / nome / "vidas.tar.gz")
    assert R.conferir_e_apagar(tmp_path / "a" / "vidas", tmp_path / "a" / "vidas.tar.gz") == 2
    assert not (tmp_path / "a" / "vidas").exists()
    (tmp_path / "b" / "vidas" / "CTRL" / "y.jsonl").write_text("mudou\n", encoding="utf-8", newline="\n")
    with pytest.raises(RuntimeError):
        R.conferir_e_apagar(tmp_path / "b" / "vidas", tmp_path / "b" / "vidas.tar.gz")
    assert (tmp_path / "b" / "vidas").exists()


def test_a_fumaca_roda_os_dois_blocos_com_o_relogio_fora_das_medidas(tmp_path):
    cfg = {**FUMACA, "unidades": {**FUMACA["unidades"], "bases": [101]}, "pares": {**FUMACA["pares"], "bases": [101], "dias": 1}}
    r = R.rodar(cfg, tmp_path / "f", 1)
    res = r["resultado"]
    assert res["vidas"] == len(R.BRACOS) * len(R.CELULAS) and res["pares"] == len(R.BRACOS)
    assert set(res["primaria"]) == {"12_celulas", "11_celulas"}
    assert set(res["guardas"]) == {"saude_12_celulas", "saude_sem_comida", R.G_TAXA, "tempo_bem_comedouro", "tempo_bem_longe",
                                   "tempo_bem_longe_fixo", R.G_S2}
    assert set(res["saude_por_celula"]) == {f"{d}|{lugar}" for d, lugar in R.CELULAS_SEM_COMIDA}
    assert res["veredito"]["leitura"] in ("confirma", "confirma com ressalva", "nao confirma", "indeterminado")
    assert set(res["descritivo"]["chutes"]) == set(R.LUGARES) and "privacao_comedouro" in res["descritivo"]["as_oito_guardas_da_c3"]
    pasta = tmp_path / "f"
    for n in ("medidas.json", "custos.json", "pares.json", "resultado.json", "vidas.tar.gz", "pares.tar.gz", "meta.json"):
        assert (pasta / n).exists()
    assert not (pasta / "vidas").exists() and not (pasta / "pares").exists()
    assert r["meta"]["pasta_crua_apagada"] == {"vidas": res["vidas"], "pares": res["pares"]}
    medidas = json.loads((pasta / "medidas.json").read_text(encoding="utf-8"))
    custos = json.loads((pasta / "custos.json").read_text(encoding="utf-8"))
    assert all("custo" not in m and 0.0 <= m["tempo_bem"] <= 1.0 and m["chutes"] >= 0 for m in medidas)
    assert set(custos) == {m["vida"] for m in medidas} and all(set(c) == {"vida_cpu", "vida_parede"} for c in custos.values())
    with pytest.raises(FileExistsError):
        R.rodar(cfg, pasta, 1)
    # D-C4-8: sem o relogio, as medidas de uma replica saem iguais byte a byte
    r2 = R.rodar(cfg, tmp_path / "g", 1)
    assert r2["meta"]["artefatos_sha256"]["medidas.json"] == r["meta"]["artefatos_sha256"]["medidas.json"]
    assert r2["meta"]["artefatos_sha256"]["resultado.json"] == r["meta"]["artefatos_sha256"]["resultado.json"]
