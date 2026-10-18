"""A validacao do J5 (docs/PLANO_ANALISE_V2_PET_QUE_PENSA.md, secao 7, com os adendos 5 e 6): o orquestrador, SEM rodar a validacao (so a
fumaca nas sementes dos testes).

O que se confere:
- a config da validacao e a do plano: as bases 46101...46505 com o K_u do adendo 6 e os numeros congelados da calibracao (o ganho_gosto,
  o g_plano, as margens, o limiar da G-APRENDEU e o resto da config do piloto), e as recusas quando um deles difere;
- as categorias dos primarios e a regra das premissas em dados com a resposta conhecida;
- a leitura da secao 7;
- a fumaca inteira: as vidas, a analise recontada das medidas gravadas e a recusa da pasta que ja existe.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from experiments import bancada_v2 as bv  # noqa: E402
from experiments.bancada import sha256_do_pacote  # noqa: E402
from experiments import run_v2_validacao_pet_que_pensa as vp  # noqa: E402

CONFIGS = RAIZ / "experiments" / "configs" / "v2_pet_que_pensa"


def _cfg(nome: str) -> dict:
    return json.loads((CONFIGS / f"{nome}.json").read_text(encoding="utf-8"))


def test_a_config_da_validacao_e_a_do_plano():
    c = vp.validar(_cfg("validacao_ao_lado"))
    assert c["unidades"] == {"bases": list(bv.BASES_PET_QUE_PENSA["validacao"]), "k": 10, "prefixo": "pet_que_pensa"}
    assert c["paladar"] is True and c["fruta_ao_lado"] is True
    assert (c["consequencia"]["ganho_gosto"], c["g_plano"], c["validacao"]["limiar_aprendeu"]) == (512, 1024, 0.25)
    e = vp.conferir_congelados(c)
    assert e["delta_t1"] == c["validacao"]["margens"]["delta_t1"] and e["k"] == 10


@pytest.mark.parametrize("mudar", [
    lambda c: c["consequencia"].update(ganho_gosto=1024),
    lambda c: c.update(g_plano=512),
    lambda c: c["validacao"]["margens"].update(delta_t1=0.3),
    lambda c: c["unidades"].update(k=4),
    lambda c: c["validacao"].update(limiar_aprendeu=1 / 3),
    lambda c: c["lobos"].update(memoria_ganho=256),
])
def test_um_numero_diferente_da_calibracao_falha(mudar):
    c = _cfg("validacao_ao_lado")
    mudar(c)
    with pytest.raises(ValueError):
        vp.validar(c)


def test_as_recusas():
    c = _cfg("validacao_ao_lado")
    with pytest.raises(bv.SementeSemPlano):
        vp.validar({**c, "unidades": {**c["unidades"], "bases": list(bv.BASES_PQP_AO_LADO)}})
    with pytest.raises(ValueError, match="4 bracos"):
        vp.validar({**c, "bracos": ["P1"]})
    with pytest.raises(ValueError, match="bootstrap"):
        vp.validar({**c, "validacao": {**c["validacao"], "bootstrap": {"reamostragens": 2000, "semente": 4242}}})
    with pytest.raises(ValueError, match="calibracao"):
        vp.validar({**c, "validacao": {k: v for k, v in c["validacao"].items() if k != "calibracao"}})


def _c(lo95, hi95, lo90, hi90):
    return {"ic95": {"ic_inferior": lo95, "ic_superior": hi95}, "ic90": {"ic_inferior": lo90, "ic_superior": hi90}}


def test_as_categorias_dos_primarios():
    assert vp.categoria_primario(_c(0.05, 0.4, 0.08, 0.35), 0.2, True)["categoria"] == "passa"
    assert vp.categoria_primario(_c(0.01, 0.15, 0.02, 0.12), 0.2, True)["categoria"] == "passa, abaixo de Delta"
    assert vp.categoria_primario(_c(0.05, 0.4, 0.08, 0.35), 0.2, False)["categoria"] == "inconclusivo"     # o Holm nao rejeita
    assert vp.categoria_primario(_c(-0.4, -0.05, -0.35, -0.08), 0.2, False)["categoria"] == "oposto"
    assert vp.categoria_primario(_c(-0.25, 0.22, -0.15, 0.15), 0.2, False)["categoria"] == "equivalente"
    assert vp.categoria_primario(_c(-0.3, 0.5, -0.25, 0.45), 0.2, False)["categoria"] == "inconclusivo"
    assert vp.categoria_primario({"ic95": None, "ic90": None, "motivo": "x"}, 0.2, False)["categoria"] == "inconclusivo"


def test_as_premissas_de_cada_contraste():
    ok = {"passa": True}
    prem = {"G-APRENDEU": {b: ok for b in bv.BRACOS_PQP},
            "G-OPORTUNIDADE": {f"{b}/{p}": ok for b in bv.BRACOS_PQP for p in ("T1", "T2")},
            "G-EXPOSICAO": {b: ok for b in bv.BRACOS_PQP}}
    assert vp.premissa_do_gate(prem, "G-T1", ("P1-plan", "P1"))["passa"]
    prem["G-OPORTUNIDADE"]["P1-plan/T2"] = {"passa": False}
    assert vp.premissa_do_gate(prem, "G-T1", ("P1-plan", "P1"))["passa"]                       # o T1 nao le o T2
    assert vp.premissa_do_gate(prem, "G-T2", ("P1-plan", "P1-plan-desfecho"))["falham"] == ["G-OPORTUNIDADE P1-plan/T2"]
    prem["G-EXPOSICAO"]["P1"] = {"passa": False}
    assert vp.premissa_do_gate(prem, "G-T1", ("P1-plan", "P1"))["passa"]                       # a exposicao e so do T2
    prem["G-APRENDEU"]["P1"] = {"passa": False}
    assert vp.premissa_do_gate(prem, "G-T1", ("P1-plan", "P1"))["falham"] == ["G-APRENDEU P1"]


def test_a_leitura():
    def g(cat, falham=()):
        return {"categoria": cat, "premissas": {"falham": list(falham)}}
    sec = {n: {"ic95": None} for n in vp.SECUNDARIOS}
    assert "G-T1 e G-T2 passam" in vp.leitura({"G-T1": g("passa"), "G-T2": g("passa, abaixo de Delta")}, sec)[0]
    assert vp.leitura({"G-T1": g("passa"), "G-T2": g("inconclusivo")}, sec)[0].startswith("So o G-T1 passa")
    assert vp.leitura({"G-T1": g("inconclusivo"), "G-T2": g("equivalente")}, sec)[0].startswith("Nenhum primario passa: o planejador")
    r = vp.leitura({"G-T1": g("inconclusivo"), "G-T2": g("inconclusivo por premissa", ["G-OPORTUNIDADE P1-plan/T2"])}, sec)
    assert "so vale para o primario com as premissas de pe (G-T1)" in r[0] and "G-OPORTUNIDADE P1-plan/T2" in r[1]
    sec["G-T2-HAB"] = {"ic95": {"ic_inferior": -0.3, "ic_superior": -0.1}}
    assert any("assinatura nao separa" in x for x in vp.leitura({"G-T1": g("passa"), "G-T2": g("passa")}, sec))


def test_a_fumaca_da_validacao(tmp_path):
    cfg = _cfg("fumaca_validacao")
    pasta = tmp_path / "val"
    r = vp.rodar(cfg, pasta)
    medidas = {}
    for b in bv.BRACOS_PQP:
        medidas.update(json.loads((pasta / b / "medidas.json").read_text(encoding="utf-8")))
    assert len(medidas) == len(bv.BRACOS_PQP) * 2 * len(cfg["sementes"]) == r["custo"]["vidas"]
    gravado = json.loads((pasta / "validacao.json").read_text(encoding="utf-8"))
    refeito = json.loads(bv._dump(vp.analisar(medidas, cfg)))
    assert {k: gravado[k] for k in refeito} == refeito
    assert set(r["primarios"]) == {"G-T1", "G-T2"} and set(r["secundarios"]) == set(vp.SECUNDARIOS)
    assert all(g["categoria"] in ("passa", "passa, abaixo de Delta", "oposto", "equivalente", "inconclusivo", "inconclusivo por premissa")
               for g in r["primarios"].values())
    meta = json.loads((pasta / "meta.json").read_text(encoding="utf-8"))
    assert meta["bancada_sha256"] == sha256_do_pacote() and meta["validacao"] == cfg["validacao"]
    with pytest.raises(FileExistsError, match="uma vez"):
        vp.rodar(cfg, pasta)
