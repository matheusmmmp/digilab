"""Os testes do descritivo da D-C1-3 no REL (adendo 11, A11.8): nas sementes dos testes (101...505), sem tocar nas vidas da C4.

Confere: que a particao cobre cada episodio uma vez so e que as somas fecham; que no SEM a lembranca e a memoria nunca decidem; que o
script falha alto com codigo diferente do `meta.json` e com o `medidas.json` de outro sha256; que duas execucoes saem iguais, byte a byte;
a regra de leitura e a comparacao com a C1 em casos sinteticos. Vive um punhado de vidas pequenas com o codigo de hoje (o `_vida` da C4),
grava os logs num tar, monta um `meta.json` do codigo de hoje e roda o mesmo caminho do script real (`principal`). O teste da C1
(`tests/test_descritivo_dc13.py`) segue passando sem mudanca.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import sys
import tarfile
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import descritivo_dc13_longe_fixo as dc  # noqa: E402
import descritivo_dc13_rel as dr  # noqa: E402
import run_v2_memoria_autobio as ma  # noqa: E402

SEMENTES = (101, 202)                                # as sementes dos testes
DONOS = ("atencioso", "relapso")
DIAS, ORCAMENTO = 14, 16
META_DA_C4 = RAIZ / "artifacts_v2_digibrain_prototipo" / "memoria_autobio" / "run" / "meta.json"


def _meta_de_hoje(sha_medidas: str) -> dict:
    """o meta.json do codigo de hoje, no formato do da run (para o caminho real do script)"""
    real = json.loads(META_DA_C4.read_text(encoding="utf-8"))
    cfg = real["config_arquivo"]
    caminho = lambda rel: rel if rel.startswith("digilab_fala_livre/") else f"digilab/{rel}"   # noqa: E731
    return {"git_head": "teste", "config": {"dias": DIAS, "orcamento_por_dia": ORCAMENTO}, "config_arquivo": cfg,
            "config_sha256": dc._sha(RAIZ / cfg), "sha256": {rel: dc._sha(RAIZ / caminho(rel)) for rel in real["sha256"]},
            "orquestrador_sha256": dc._sha(RAIZ / "experiments" / "run_v2_memoria_autobio.py"),
            "longe_regular_sha256": dc._sha(RAIZ / "experiments" / "run_v2_longe_regular.py"),
            "habito_intencao_sha256": dc._sha(RAIZ / "experiments" / "run_v2_habito_intencao.py"),
            "prototipo_sha256": dc._sha(RAIZ / "experiments" / "run_v2_digibrain_prototipo.py"),
            "artefatos_sha256": {"medidas.json": sha_medidas}}


@pytest.fixture(scope="module")
def mundo(tmp_path_factory):
    pasta = tmp_path_factory.mktemp("vidas_dc13_rel")
    cfg = {"dias": DIAS, "orcamento_por_dia": ORCAMENTO}
    medidas = {}
    for s in SEMENTES:
        for dono in DONOS:
            for braco in dr.BRACOS:
                v = ma._vida(cfg, braco, dono, dr.ESTILO, {"semente": s, "base": s, "k": 0}, str(pasta))
                medidas[v["vida"]] = json.loads(json.dumps(v))
    tar = pasta / "vidas.tar.gz"
    with tarfile.open(tar, "w:gz") as t:
        for arq in sorted((pasta / "vidas").rglob("*.jsonl")):
            t.add(arq, arcname=f"vidas/{arq.parent.name}/{arq.name}")
    texto = json.dumps(medidas, sort_keys=True).encode("utf-8")
    gz = pasta / "medidas.json.gz"
    gz.write_bytes(gzip.compress(texto, mtime=0))
    return {"medidas": medidas, "tar": tar, "gz": gz, "meta": _meta_de_hoje(hashlib.sha256(texto).hexdigest()), "pasta": pasta}


def _c1_sintetico() -> dict:
    """um descritivo.json da C1 minimo (so os campos que a comparacao le), com a linha 'aponta para H3'"""
    def est(s, cls):
        return {"s": s, "classe": {"classe": cls}}
    return {"leitura": {"linha": "aponta para H3, como leitura descritiva (A10.6)", "explicam_a_maior_parte": ["H3"], "contribuem": ["H1", "H3"],
                        "partes": {k: {"s": 0.1, "classe": "> 0"} for k in ("H1", "H1'", "H2", "H3")}},
            "estagio2": {"A": {p: {"M3-M2": est(0.1, "> 0")} for p in dc.PARTES_F}, "B": {p: {"M3-M2": est(-0.1, "< 0")} for p in dc.PARTES_P}}}


def _rodar(m, saida: Path, medidas: dict | None = None, c1: dict | None = None) -> dict:
    return dr.principal(RAIZ, m["meta"], medidas or m["medidas"], m["tar"], saida, 1, {"teste": "sem fonte"}, None, c1, donos=DONOS)


@pytest.fixture(scope="module")
def duas(mundo, tmp_path_factory):
    pasta = tmp_path_factory.mktemp("saidas_dc13_rel")
    c1 = _c1_sintetico()
    a, b = _rodar(mundo, pasta / "a" / "d.json", c1=c1), _rodar(mundo, pasta / "b" / "d.json", c1=c1)
    dc.gravar(pasta / "a" / "d.json", a)
    dc.gravar(pasta / "b" / "d.json", b)
    return a, b, pasta


def test_a_particao_cobre_cada_episodio_uma_vez_e_as_somas_fecham(mundo, duas):
    a, _b, _p = duas
    s2 = a["estagio2"]
    assert a["vidas"] == len(SEMENTES) * len(DONOS) * len(dr.BRACOS)
    assert a["g1"] == {"vidas_refeitas": a["vidas"], "todas_iguais": True}
    for braco, cob in s2["cobertura"].items():
        gravados = [v for v in mundo["medidas"].values() if v["braco"] == braco]
        assert cob["vidas"] == len(gravados)
        assert cob["episodios"] == sum(v["episodios_fome"]["n"] for v in gravados)       # cada episodio entra uma vez
        assert sum(cob["F"].values()) == sum(v["episodios_fome"]["fechados"] for v in gravados)
        assert sum(cob["F"].values()) + sum(cob["P"].values()) == cob["episodios"]
        for p in dr.PARTES_F:                                # os grupos de A11.4 sao exclusivos e somam a parcela
            assert sum(cob["F_por_grupo"][p].values()) == cob["F"][p]
        if braco == "SEM":                                   # sem lugar lembrado nao ha ida a ele
            assert cob["F"]["F-b"] == 0
    assert sum(sum(c["F"].values()) for c in s2["cobertura"].values()) > 0                 # o teste tem episodios fechados de verdade
    fecha = s2["soma_das_parcelas"]
    assert fecha["F"] == pytest.approx(fecha["G"], abs=1e-12)
    assert fecha["P"] == pytest.approx(fecha["G"], abs=1e-12)
    soma = sum(s2["A"][p]["REL-SEM"]["media"] for p in dc.PARTES_F)
    assert soma == pytest.approx(a["estagio1"]["G"], abs=1e-12)
    assert a["leitura"]["linha"]
    assert a["comparacao_com_a_c1"]["veredito"]


def test_o_registro_das_visitas_do_rel_tem_o_alvo_e_o_episodio(mundo, duas):
    a, _b, _p = duas
    idas = a["estagio2"]["idas"]
    assert "so o REL" in idas["rotulo"]
    todas = idas["todas"]
    assert todas["idas"] == a["estagio2"]["cobertura"]["REL"]["idas"] > 0                   # o REL tem idas ao lugar lembrado
    for chave in ("alvo_dist_ponto_celulas_media", "frac_alvo_em_ponto_fixo", "frac_visita_codificou_episodio", "sigma_media"):
        assert chave in todas
    # cada visita do REL codificou um episodio (a contagem do medidas.json: as visitas ao lugar lembrado)
    visitas = sum(v["visitas_lugar_lembrado"] for v in mundo["medidas"].values() if v["braco"] == "REL")
    assert visitas > 0 and todas["frac_visita_codificou_episodio"] > 0
    assert todas["visitas_com_mais_de_um_episodio"] == 0


def test_no_sem_a_lembranca_e_a_memoria_nunca_decidem(mundo, duas):
    a, _b, _p = duas
    for chave in a["estagio2"]["combos_por_braco"]["SEM"]:
        modulos = chave.split("|")[1].split("+")
        assert "memoria" not in modulos and "lembranca" not in modulos
    for v in mundo["medidas"].values():
        if v["braco"] == "SEM":
            assert v["memoria"]["decidiu_vida"]["memoria"] == 0 and v["memoria"]["decidiu_vida"]["lembranca"] == 0
            assert v["memoria"]["com_lembranca"] == 0
    # e o script confere por conta propria: uma sonda de memoria numa combinacao do SEM falha alto
    assert dr._grupo(("lembranca", "memoria")) == "lembranca" and dr._grupo(("memoria",)) == "memoria_lugar"


def test_os_grupos_de_a11_4_sao_exclusivos_e_na_ordem():
    assert dr._grupo(()) == "inato"
    assert dr._grupo(("lembranca",)) == "lembranca"
    assert dr._grupo(("habito", "lembranca", "memoria")) == "lembranca"
    assert dr._grupo(("aprendido", "memoria")) == "memoria_lugar"
    assert dr._grupo(("aprendido", "habito")) == "aprendido_habito"
    assert dr._grupo(("habito",)) == "aprendido_habito"
    assert dr._grupo(("incentivo",)) == "outro"
    assert dr._grupo(("aprendido", "incentivo")) == "outro"
    g = dr.regrupar({"F-a|lembranca+memoria": 2, "F-a|inato": 3, "F-c|sem_comer_dirigida": 1, "F-d|aprendido+habito": 4, "F-d|memoria": 5})
    assert g["F-a"]["lembranca"] == 2 and g["F-a"]["inato"] == 3 and g["F-c"]["sem_comer_dirigida"] == 1
    assert g["F-d"]["aprendido_habito"] == 4 and g["F-d"]["memoria_lugar"] == 5
    assert sum(sum(x.values()) for x in g.values()) == 15


def test_o_script_falha_alto_com_codigo_diferente_do_meta(mundo, tmp_path):
    meta = json.loads(json.dumps(mundo["meta"]))
    assert dr.conferir_codigo(RAIZ, meta)["iguais_ao_meta"] is True
    primeiro = sorted(meta["sha256"])[0]
    meta["sha256"][primeiro] = "0" * 64
    with pytest.raises(RuntimeError, match="nao e o da run"):
        dr.conferir_codigo(RAIZ, meta)
    with pytest.raises(RuntimeError, match=primeiro):
        dr.principal(RAIZ, meta, mundo["medidas"], mundo["tar"], tmp_path / "x" / "d.json", 1, {}, None, donos=DONOS)
    assert not (tmp_path / "x").exists()
    # um modulo da fala e a config contam igual
    meta = json.loads(json.dumps(mundo["meta"]))
    meta["sha256"]["digilab_fala_livre/fatos.py"] = "0" * 64
    with pytest.raises(RuntimeError, match="digilab_fala_livre/fatos.py"):
        dr.conferir_codigo(RAIZ, meta)
    # o meta.json da C4 de verdade: o codigo de hoje nao e o do a287ba2 (9 modulos mudaram), e o script nao roda com ele
    real = json.loads(META_DA_C4.read_text(encoding="utf-8"))
    with pytest.raises(RuntimeError, match="nao e o da run"):
        dr.conferir_codigo(RAIZ, real)


def test_o_script_falha_alto_com_o_medidas_de_outro_sha256(mundo, tmp_path):
    medidas, sha = dr.carregar_medidas(mundo["gz"], mundo["meta"])
    assert sha == mundo["meta"]["artefatos_sha256"]["medidas.json"] and len(medidas) == len(mundo["medidas"])
    outro = tmp_path / "outro.json.gz"
    alterado = json.loads(json.dumps(mundo["medidas"]))
    alterado[sorted(alterado)[0]]["reflexos"] += 1
    outro.write_bytes(gzip.compress(json.dumps(alterado, sort_keys=True).encode("utf-8"), mtime=0))
    with pytest.raises(RuntimeError, match="nao e o do meta.json"):
        dr.carregar_medidas(outro, mundo["meta"])


def test_falta_de_campo_no_medidas_falha_alto(mundo, tmp_path):
    medidas = json.loads(json.dumps(mundo["medidas"]))
    vida = sorted(medidas)[0]
    del medidas[vida]["racao_na_janela"]["entraram_na_visao"]
    with pytest.raises(RuntimeError, match="racao_na_janela.entraram_na_visao"):
        dr.principal(RAIZ, mundo["meta"], medidas, mundo["tar"], tmp_path / "w" / "d.json", 1, {}, None, donos=DONOS)
    # o numero de vidas pedido pelo adendo (1 600) e conferido
    with pytest.raises(RuntimeError, match="1600"):
        dr.principal(RAIZ, mundo["meta"], mundo["medidas"], mundo["tar"], tmp_path / "v" / "d.json", 1, {}, None, donos=DONOS,
                     vidas_esperadas=dr.VIDAS_ESPERADAS)


def test_o_g1_falha_alto_com_a_medida_gravada_diferente(mundo, tmp_path):
    medidas = json.loads(json.dumps(mundo["medidas"]))
    vida = sorted(medidas)[0]
    medidas[vida]["reflexos"] += 1
    with pytest.raises(RuntimeError, match="G1 do descritivo"):
        dr.principal(RAIZ, mundo["meta"], medidas, mundo["tar"], tmp_path / "y" / "d.json", 1, {}, None, donos=DONOS)


def test_duas_execucoes_saem_iguais_byte_a_byte(duas):
    a, b, pasta = duas
    assert a == b
    assert (pasta / "a" / "d.json").read_bytes() == (pasta / "b" / "d.json").read_bytes()
    texto = (pasta / "a" / "d.json").read_text(encoding="utf-8")
    for proibido in ("duracao", "processos", "parede", "perf_counter"):                 # sem tempo nem numero de processos
        assert proibido not in texto
    assert set(a["scripts"]) == {"experiments/descritivo_dc13_rel.py", "experiments/descritivo_dc13_longe_fixo.py"}


def test_roda_uma_vez(mundo, duas):
    _a, _b, pasta = duas
    with pytest.raises(FileExistsError):
        _rodar(mundo, pasta / "a" / "d.json")


def test_so_o_estagio_1_sai_rotulado_como_parcial(mundo, tmp_path):
    d = dr.principal(RAIZ, mundo["meta"], mundo["medidas"], mundo["tar"], tmp_path / "p" / "d.json", 1, {}, None, donos=DONOS, so_estagio1=True)
    assert "PARCIAL" in d["rotulo"] and "estagio2" not in d and d["leitura"]["linha"].startswith("nenhuma leitura")


def _est(media, lo, hi, G=0.05):
    cls = "> 0" if lo > 0 else ("< 0" if hi < 0 else "indeterminado")
    return {"media": media, "s": media / G, "ic95": {"ic_inferior": lo, "ic_superior": hi}, "classe": {"classe": cls}}


def _s2(d1, **h):
    base = {k: _est(0.0, -0.01, 0.01) for k in ("H1", "H1'", "H2", "H3", "H5", "F-d_sem_modulo")}
    base.update(h)
    return {"hipoteses": base, "D1": {"REL-SEM": {"classe_sinal": d1[0], "ic95": {"ic_inferior": d1[1], "ic_superior": d1[2]}}},
            "A": {"F-c": {"REL-SEM": {"classe": {"classe": "indeterminado"}}}}}


S1 = {"H4": {"cumpre": False}}


def test_a_regra_de_leitura_com_o_h5_e_as_lacunas_escritas():
    # uma so explica: aponta (H5 nao pede condicao de D1)
    assert "aponta para H5" in dr.ler(S1, _s2(("indeterminado", -1, 1), H5=_est(0.04, 0.03, 0.05)))["linha"]
    assert "aponta para H3" in dr.ler(S1, _s2(("> 0", 1, 2), H3=_est(0.04, 0.03, 0.05)))["linha"]
    # H1 sem D1 "< 0" nao aponta
    r = dr.ler(S1, _s2(("indeterminado", -1, 1), H1=_est(0.04, 0.03, 0.05)))
    assert r["H1_sem_D1"] and r["linha"].startswith("indeterminado")
    # H1' pede D1 sem o limite superior abaixo de 0
    assert dr.ler(S1, _s2(("< 0", -2, -1), **{"H1'": _est(0.04, 0.03, 0.05)}))["linha"].startswith("indeterminado")
    assert "aponta para H1'" in dr.ler(S1, _s2(("indeterminado", -1, 1), **{"H1'": _est(0.04, 0.03, 0.05)}))["linha"]
    # H2 pede D1 nao "< 0"
    assert dr.ler(S1, _s2(("< 0", -2, -1), H2=_est(0.04, 0.03, 0.05)))["linha"].startswith("indeterminado")
    # o par de A10.5
    assert "mistura de posicao e custo" in dr.ler(S1, _s2(("< 0", -2, -1), H1=_est(0.04, 0.03, 0.05), H3=_est(0.03, 0.02, 0.04)))["linha"]
    # a lacuna escrita em A11.5: duas que explicam fora dos pares sao mistura
    r = dr.ler(S1, _s2(("> 0", 1, 2), H5=_est(0.03, 0.02, 0.04), H3=_est(0.03, 0.02, 0.04)))
    assert r["linha"].startswith("mistura (H3, H5 explicam") and "lacuna_da_regra" not in r
    # nenhuma explica e duas contribuem: mistura
    assert dr.ler(S1, _s2(("> 0", 1, 2), H5=_est(0.01, 0.005, 0.02), H3=_est(0.01, 0.005, 0.02)))["linha"].startswith("mistura (H3, H5 contribuem")
    # uma so contribui, sem nenhuma que explique: indeterminado, com a parte registrada
    r = dr.ler(S1, _s2(("> 0", 1, 2), H5=_est(0.01, 0.005, 0.02)))
    assert r["linha"].startswith("indeterminado") and r["parte_registrada"] == "H5"
    # nada contribui: indeterminado sem parte
    r = dr.ler(S1, _s2(("> 0", 1, 2)))
    assert r["linha"].startswith("indeterminado") and "parte_registrada" not in r
    # o H4 vem antes de tudo
    assert dr.ler({"H4": {"cumpre": True}}, _s2(("> 0", 1, 2), H5=_est(0.04, 0.03, 0.05)))["linha"].startswith("o ganho e da medida")
    # a substituicao
    s2 = _s2(("indeterminado", -1, 1), **{"H1'": _est(0.04, 0.03, 0.05)})
    s2["A"]["F-c"]["REL-SEM"]["classe"]["classe"] = "< 0"
    r = dr.ler(S1, s2)
    assert r["substituicao"] and "Substituicao" in r["linha"]


def _leitura(linha, explicam, contribuem):
    return {"linha": linha, "explicam_a_maior_parte": explicam, "contribuem": contribuem,
            "partes": {k: {"s": 0.1, "classe": "> 0"} for k in dr.HIPOTESES}}


def test_a_comparacao_com_a_c1_segue_a_tabela_de_a11_5():
    c1 = _c1_sintetico()
    s2 = {"A": {p: {"REL-SEM": {"s": 0.2, "classe": {"classe": "> 0"}}} for p in dc.PARTES_F},
          "B": {p: {"REL-SEM": {"s": -0.2, "classe": {"classe": "< 0"}}} for p in dc.PARTES_P}}
    igual = dr.comparar_c1(_leitura("aponta para H3, como leitura descritiva (A11.6)", ["H3"], ["H3"]), s2, c1)
    assert igual["veredito"].startswith("o caminho se repete")
    outra = dr.comparar_c1(_leitura("aponta para H5, como leitura descritiva (A11.6)", ["H5"], ["H5"]), s2, c1)
    assert outra["veredito"].startswith("o caminho nao se transfere")
    mistura = dr.comparar_c1(_leitura("mistura (H3, H5 explicam ao mesmo tempo): registrada", ["H3", "H5"], ["H3", "H5"]), s2, c1)
    assert mistura["veredito"].startswith("o caminho nao se transfere")
    indet = dr.comparar_c1(_leitura("indeterminado: o caminho nao e nenhum dos previstos", [], []), s2, c1)
    assert indet["veredito"].startswith("o caminho do REL fica sem leitura")
    assert igual["lado_a_lado"]["hipoteses"]["H5"]["c1"] is None and igual["lado_a_lado"]["hipoteses"]["H3"]["c1"]["s"] == 0.1
    assert "sem teste entre as runs" in igual["nota"] and "ic95" not in json.dumps(igual["lado_a_lado"])
