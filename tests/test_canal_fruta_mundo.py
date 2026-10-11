"""A rota do canal do humor no mundo fisico (CANAIS-REFORCO; decisao do Matheus, 2026-10-11): `ConfigLobos.presenca_fruta_mundo`.

Com a chave, a decisao de comer do cerebro A no mundo fisico le a fruta madura a vista (um peso por fruta, prior 0, em toda regra em que
comer e candidato: a FRUTA-NO-CENARIO parte B no mundo fisico). Sao os pesos que leem a identidade da fruta: com os canais, o canal do humor
(a E2) vai a eles, e comer a fruta que mexe no humor deixa de falhar alto.

- G2: com a chave desligada, a vida de hoje (os gabaritos, na suite); com a chave e os canais no mundo `iguais` (o humor da fruta e zero),
  a mesma vida byte a byte e os pesos novos em zero; no P0, sempre a mesma vida;
- a conta exata: a presenca pela percepcao, o termo no peso efetivo e um passo da regra pelo canal do humor;
- a falha real do D (o A so, semente 505, nos dois pets): sem a chave falha alto, com ela roda (o G1 do grupo e conferido pela bancada) e o
  peso do tipo ruim desce;
- os pesos: 990 no degrau 1 dos dois pets (o alvo aprendido e as entradas sociais), abaixo de mil.
So as sementes dos testes.
"""
from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import bancada_v2 as bv  # noqa: E402
from digilab.config import CONFIG_LOBOS, CONFIG_LOBOS_APRENDIZ, CONFIG_PADRAO, ConfigLobos  # noqa: E402
from digilab.events import FRUTAS, AcaoPet  # noqa: E402
from digilab.mundo import PercepcaoMundo  # noqa: E402
from digilab.policies.lobos import PARAMETROS_LOBOS, PoliticaLobos, div_arred, presenca_no_mundo  # noqa: E402
from test_bancada_dois_pets import CFG  # noqa: E402
from test_grupo import CM  # noqa: E402

S = CONFIG_LOBOS.escala
T3 = bv.cfg_lobos_do_ponto("T3")


def _cerebro(cl=None):
    return PoliticaLobos(CONFIG_PADRAO, cl or replace(CONFIG_LOBOS_APRENDIZ, presenca_fruta_mundo=True), cfg_mundo=CM)


def _pm(*tipos):
    return PercepcaoMundo(0, 0, 0, tuple((k, t, 1, 1, 1) for k, t in enumerate(tipos)), 0, 0, None)


# ================================================================== a chave
def test_a_chave_no_registro_e_as_falhas_altas():
    assert PARAMETROS_LOBOS["presenca_fruta_mundo"][0] == "PROPOSTO" and CONFIG_LOBOS.presenca_fruta_mundo is False
    with pytest.raises(ValueError, match="mundo fisico"):
        PoliticaLobos(CONFIG_PADRAO, replace(CONFIG_LOBOS, presenca_fruta_mundo=True))
    with pytest.raises(TypeError):
        PoliticaLobos(CONFIG_PADRAO, replace(CONFIG_LOBOS, presenca_fruta_mundo=1), cfg_mundo=CM)


def test_os_pesos():
    base = PoliticaLobos(CONFIG_PADRAO, CONFIG_LOBOS, cfg_mundo=CM).n_pesos()
    assert _cerebro().n_pesos() == base + 3
    degrau1 = replace(CONFIG_LOBOS_APRENDIZ, alvo_aprendido=True, entradas_sociais=True, modelo_outros=True, presenca_fruta_mundo=True)
    assert PoliticaLobos(CONFIG_PADRAO, degrau1, cfg_mundo=CM).n_pesos() == 990 < CONFIG_LOBOS.maximo_pesos


# ================================================================== a conta exata
def test_a_presenca_pela_percepcao_do_mundo():
    assert presenca_no_mundo(_pm("a", "c_podre", "bola", "racao")) == (1.0, 0.0, 0.0)
    assert presenca_no_mundo(_pm("b", "c", "b")) == (0.0, 1.0, 1.0)
    assert presenca_no_mundo(_pm()) == (0.0,) * len(FRUTAS)
    with pytest.raises(RuntimeError):
        presenca_no_mundo(None)


@pytest.mark.parametrize("regra,cand", [("fruta_no_cenario", (AcaoPet.OCIOSO, AcaoPet.COMER)),
                                        ("fome_moderada", (AcaoPet.COMER, AcaoPet.CHAMAR_ATENCAO))])
def test_o_termo_no_peso_efetivo_em_toda_regra_com_comer(regra, cand):
    c = _cerebro()
    x = [1.0] + [0.0] * 10 + [1.0]                              # a entrada `fruta` (comida boa a vista) acesa: comer acima do piso
    c._presenca_na_decisao = (0.0, 0.0, 1.0)
    _, antes = c._pesos_efetivos(regra, cand, x)
    c._pesos_comer_fruta["c"] = -256
    _, depois = c._pesos_efetivos(regra, cand, x)
    assert antes[AcaoPet.COMER] - depois[AcaoPet.COMER] == 0.25
    outra = next(a for a in cand if a is not AcaoPet.COMER)
    assert depois[outra] == antes[outra]


def test_um_passo_pelo_canal_do_humor_so_mexe_na_fruta_presente():
    c = _cerebro()
    reg = {"regra": "fruta_no_cenario", "candidatos": (AcaoPet.OCIOSO, AcaoPet.COMER), "acao": AcaoPet.COMER, "X": [S] + [0] * 11,
           "P": {AcaoPet.OCIOSO: 600, AcaoPet.COMER: 424}, "W": {AcaoPet.OCIOSO: 3072, AcaoPet.COMER: 2200},
           "presenca": {"a": 0, "b": 0, "c": S}}
    corpo_antes = {a: list(v) for a, v in c._pesos["fruta_no_cenario"].items()}
    c._aplicar_sinal(reg, 900, consequencia=True, alvos={"corpo": 0, "fruta": -204})
    esperado = div_arred(-204 * c.cl.passo * S * (S - 424), S * S * 2200)
    assert c._pesos_comer_fruta == {"a": 0, "b": 0, "c": esperado} and esperado < 0
    assert c._pesos["fruta_no_cenario"] == corpo_antes          # o canal do corpo era 0: a tabela da regra nao mexe
    c._aplicar_sinal(reg, 300, consequencia=True, alvos={"corpo": 300, "fruta": 0})
    assert c._pesos_comer_fruta["c"] == esperado                # o canal do corpo nao mexe na presenca


# ================================================================== G2
def _bancada(cl: ConfigLobos, dias=2):
    return bv.Bancada(dias, 16 * dias, cfg_lobos=cl, montagem="completa")


@pytest.mark.parametrize("braco", ["P0", "P1"])
def test_g2_no_mundo_iguais_com_os_canais_a_mesma_vida(braco):
    """no mundo fisico de hoje (iguais: o humor da fruta e zero) o canal do humor e zero: com a chave e os canais, a mesma vida byte a
    byte, e os pesos da presenca ficam em zero"""
    com, sem = _bancada(replace(T3, presenca_fruta_mundo=True), 4), _bancada(T3, 4)
    vistas = 0
    for s in (101, 202):
        for lugar in ("comedouro", "perto"):
            e = bv.EspecVida("atencioso", braco, s, None, "fisico", "lobos", lugar)
            vc, vs = com.vida(e), sem.vida(e)
            assert bv.resumo_motor(vc.motor) == bv.resumo_motor(vs.motor)
            ei = vc.motor.politica.estado_interno()
            assert ei["pesos_comer_fruta"] == {f: 0 for f in FRUTAS}
            assert ei["pesos"] == vs.motor.politica.estado_interno()["pesos"]
            vistas += sum(1 for m in ei["motivos"] if m.get("mundo", {}).get("comeu") in FRUTAS)
    if braco == "P1":
        assert vistas > 0                                       # o pet comeu fruta: o caminho foi exercitado


# ================================================================== a falha real do D (o A so, semente 505)
def _bancada_grupo(lobos: dict):
    cfg = {**CFG, "montagem": "completa", "lobos": lobos}
    return bv.bancada_da_config({**cfg, "orcamento": cfg["orcamento_por_dia"] * cfg["dias"]})


def test_sem_a_chave_a_fruta_que_mexe_no_humor_falha_alto(monkeypatch):
    monkeypatch.setattr(bv, "NOS_PENDENTES", {k: v for k, v in bv.NOS_PENDENTES.items() if k != "canais_fruta_mundo"})
    with pytest.raises(RuntimeError, match="CANAIS-REFORCO"):
        _bancada_grupo({}).grupo(bv.EspecGrupo("A-so", 505, 0))


def test_com_a_chave_o_a_so_roda_e_o_tipo_ruim_desce(monkeypatch):
    monkeypatch.setattr(bv, "NOS_PENDENTES", {k: v for k, v in bv.NOS_PENDENTES.items() if k != "canais_fruta_mundo"})
    vg = _bancada_grupo({"presenca_fruta_mundo": True}).grupo(bv.EspecGrupo("A-so", 505, 0))   # o G1 do grupo e conferido aqui
    e = vg.grupo.motores["A"].politica._pm.estado_interno()
    ruim = bv.tipo_ruim(505)
    assert e["pesos_comer_fruta"][ruim] < 0
    assert all(w == 0 for f, w in e["pesos_comer_fruta"].items() if f != ruim)
    assert e["canais"]["por_alvo"]["fruta"] < 0
