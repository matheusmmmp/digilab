"""Painel do E1 com a V21D (docs/PLANO_ANALISE_V21D.md): a V21D so entra pela config, e com as chaves desligadas
nada muda; metricas novas (r2 por categoria, kappa de Fleiss, QD, ICC)."""
from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

from digilab.combate_v2.v21.bots import ADULTOS, FORMAS, GAMBITS_MURALHA_V21D, GAMBITS_VIGIA_V21D  # noqa: E402
from digilab.combate_v2.v21.catalogo import LINHA_DA_FORMA  # noqa: E402
from digilab.config import CONFIG_COMBATE_V2C, CONFIG_COMBATE_V21C, ConfigArenaPesquisa, ConfigCombateV21C, ConfigCombateV21D  # noqa: E402
from digilab.metrics import icc_um_fator, kappa_fleiss, qualidade_diversidade, r2_por_categoria  # noqa: E402
from run_educacao import lutador_painel  # noqa: E402
from run_poder import regras_de  # noqa: E402

CFG_E1 = RAIZ / "experiments" / "configs" / "linhagem" / "natureza_criacao.json"
CFG_V21D = RAIZ / "experiments" / "configs" / "linhagem" / "natureza_criacao_v21d.json"
CHAVES = ("preparo_sob_pele_oculto", "muralha_lista_espelho", "vigia_bate_em_quem_recua", "vigia_recua_do_preparo_sob_pele")


def _cfg(p):
    return json.loads(p.read_text(encoding="utf-8"))


def test_regras_do_e1_continuam_v21c():
    r = regras_de(_cfg(CFG_E1))
    assert type(r.v21) is ConfigCombateV21C and r.v21 == CONFIG_COMBATE_V21C and r.base == CONFIG_COMBATE_V2C


def test_regras_da_v21d_ligam_so_as_quatro_chaves():
    r = regras_de(_cfg(CFG_V21D))
    assert type(r.v21) is ConfigCombateV21D and r.base == CONFIG_COMBATE_V2C
    d = asdict(r.v21)
    assert all(d[k] for k in CHAVES)
    assert not any(d[k] for k in ("investida_erra_contra_recuo", "preparo_prende", "tita_bate_em_quem_recua"))
    assert {k: v for k, v in d.items() if k in asdict(CONFIG_COMBATE_V21C)} == asdict(CONFIG_COMBATE_V21C)


def test_config_v21d_so_difere_do_e1_nas_chaves():
    c, d = _cfg(CFG_E1), _cfg(CFG_V21D)
    for k in ("rotulo_partidas", "M_B_por_bot", "bootstrap", "donos", "dias"):
        assert c[k] == d[k], k
    assert c["rodadas"]["especie_fixa"] == d["rodadas"]["especie_fixa"]
    assert c["combate"]["regras_base"] == d["combate"]["regras_base"]
    extra = {k: v for k, v in d["combate"]["regras_v21"].items() if k not in c["combate"]["regras_v21"]}
    val = json.loads((RAIZ / "experiments" / "configs" / "v21d" / "validacao.json").read_text(encoding="utf-8"))
    assert extra == val["regras_v21"]


def _spec(adulta):
    return {"forma": {"estagio": "adulto", "ramo": "arisco", "linha": LINHA_DA_FORMA[adulta], "adulta": adulta},
            "temp_ovo": {}, "carater": {}, "condicao": 1.0, "pontos": {}, "disciplina": 0, "especie": "brasa"}


def test_pet_do_painel_usa_a_lista_das_regras():
    carena = ConfigArenaPesquisa(condicao_neutra=True)
    c21, c21d = regras_de(_cfg(CFG_E1)).v21, regras_de(_cfg(CFG_V21D)).v21
    for f in FORMAS:
        assert lutador_painel("x", _spec(f), carena, c21).gambits == ADULTOS[f], f
    assert lutador_painel("x", _spec("muralha"), carena, c21d).gambits == GAMBITS_MURALHA_V21D
    assert lutador_painel("x", _spec("vigia"), carena, c21d).gambits == GAMBITS_VIGIA_V21D[(True, True)]
    for f in set(FORMAS) - {"muralha", "vigia"}:
        assert lutador_painel("x", _spec(f), carena, c21d).gambits == ADULTOS[f], f


def test_r2_por_categoria():
    r = r2_por_categoria([0.0, 0.0, 1.0, 1.0], ["a", "a", "b", "b"])
    assert r["r2"] == 1.0 and r["n_categorias"] == 2
    assert r2_por_categoria([0.0, 1.0, 0.0, 1.0], ["a", "a", "b", "b"])["r2"] == 0.0
    with pytest.raises(ValueError):
        r2_por_categoria([1.0], ["a", "b"])


def test_r2_reproduz_a_analise_dono_ambiente():
    """0,9585 (640 pets, 14 categorias) e 0,9290 (atencioso e permissivo), do artefato do E1"""
    pasta = RAIZ / "artifacts_linhagem" / "natureza_criacao" / "especie_fixa"
    pets = json.loads((pasta / "pets.json").read_text(encoding="utf-8"))
    taxa = json.loads((pasta / "resultado.json").read_text(encoding="utf-8"))["taxa_por_celula"]
    ref = json.loads((RAIZ / "artifacts_linhagem" / "dono_ambiente" / "resultado.json").read_text(encoding="utf-8"))
    ff = ref["rodadas"]["especie_fixa"]["forma_final"]

    def cat(p):
        return "morto" if p["morta"] else (p["forma"]["adulta"] or f"adolescente:{p['forma']['linha']}")
    chaves = sorted((int(k.split("|")[0]), k.split("|")[1], int(k.split("|")[2])) for k in taxa)
    for rot, donos in (("todos", None), ("so_donos_sem_mortes", {"atencioso", "permissivo"})):
        ks = [k for k in chaves if donos is None or k[1] in donos]
        r = r2_por_categoria([taxa[f"{g}|{b}|{r}"] for g, b, r in ks], [cat(pets[f"{b}@g{g}r{r}"]) for g, b, r in ks])
        assert r["r2"] == ff[rot]["r2"] and r["n_categorias"] == ff[rot]["n_formas"]


def test_kappa_fleiss():
    k = kappa_fleiss([["a", "a"], ["b", "b"]])
    assert k["kappa"] == 1.0 and k["concordancia_pares"] == 1.0
    k = kappa_fleiss([["a", "b"], ["b", "a"]])
    assert k["concordancia_pares"] == 0.0 and k["kappa"] == -1.0
    with pytest.raises(ValueError):
        kappa_fleiss([["a", "a"], ["a", "a"]])
    with pytest.raises(ValueError):
        kappa_fleiss([["a", "b"], ["a"]])


def test_qualidade_diversidade():
    q = qualidade_diversidade([0.2, 0.4, 0.9, 0.1], ["x", "x", "y", "fora"], ["x", "y", "z", "w"])
    assert q["cobertura"] == 0.5 and abs(q["qd_score"] - 1.2) < 1e-12 and q["n_por_nicho"] == {"x": 2, "y": 1}


def test_icc_um_fator():
    assert icc_um_fator([[1.0, 1.0], [3.0, 3.0], [5.0, 5.0]]) == 1.0
    assert icc_um_fator([[1.0, 3.0], [3.0, 1.0]]) < 0
    with pytest.raises(ValueError):
        icc_um_fator([[1.0, 1.0], [1.0, 1.0]])
