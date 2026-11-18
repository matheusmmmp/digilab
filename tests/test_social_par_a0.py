"""SOCIAL_PAR, A0 e B0: o codigo antes da run (docs/PLANO_ANALISE_V3_SOCIAL_PAR_A0.md, APROVADO em 2026-11-17, secao 4).

Os gates: o T* em casos feitos a mao, a gravacao em JSON, o G-GRAV-IDENT-CO7 (com a CO7 ligada nos dois, sem perturbacao, a GRAV refaz a
VIVO com zero desvios; a E1 conferiu isso so sem a CO7), as faixas e os prefixos, e o G-ORQ (a fumaca do orquestrador em 2 pares das
sementes de teste, com o G-INSTR e o G1).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import exportar_gabarito_co6 as e6  # noqa: E402
import run_v3_social_par_a0 as a0  # noqa: E402
from bancada import parceiro as pc  # noqa: E402
from bancada.faixas import FAIXAS_RESERVADAS, PREFIXOS_UNIDADES  # noqa: E402
from digilab import metrics as mt  # noqa: E402
from digilab.config import CONFIG_COOPERACAO_CO7, CONFIG_COOPERACAO_LIGADA, CONFIG_GRUPO_LIGADA  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.events import AcaoPet  # noqa: E402
from digilab.grupo import sementes_do_grupo  # noqa: E402
from digilab.mundo import Alvo, DonoComLugar  # noqa: E402

CM = e6.CM
SS = lambda s: sementes_do_grupo(s, CONFIG_GRUPO_LIGADA.ids)  # noqa: E731


def _dono(semente_pet):
    return DonoComLugar(criar_dono("atencioso"), "comedouro", semente_pet, "atencioso", CM)


def _vivo(ident, s, gravar=False):
    fp, fm = a0.fabricas_do_jogo("atencioso", SS(s)[ident])
    return pc.Membro(ident, "vivo", fm, fp, _dono(SS(s)[ident]), "atencioso", "digibrain", gravar=gravar)


def _gravado(ident, s, base):
    return pc.Membro(ident, "gravado", a0.fabricas_do_jogo("atencioso", SS(s)[ident])[1], gravacao=base.gravacoes[ident],
                     eventos_dono=pc.eventos_do_dono(base.grupo, ident), rotulo_dono="atencioso", rotulo_cerebro="gravada")


# ------------------------------------------------------------------ o T*
def test_tempo_restrito_e_a_janela_quando_censurado():
    d = [9, 8, 7, 6, 5, 9, 9, 9]
    assert mt.tempo_restrito(d, 6, 0, 5) == 3                    # chegou no passo 3
    assert mt.tempo_restrito([9] * 8, 6, 1, 5) == 5              # censurado: a janela inteira
    assert mt.tempo_restrito(d, 6, 3, 2) == 0                    # ja estava perto
    with pytest.raises(ValueError, match="nao cabe"):
        mt.tempo_restrito([9] * 5, 6, 1, 5)                      # a janela passa do fim: falha alto, nunca um tempo menor
    with pytest.raises(ValueError):
        mt.tempo_restrito(d, 6, 0, 0)


# ------------------------------------------------------------------ a gravacao em JSON
def test_a_decisao_gravada_vai_e_volta_pelo_json():
    ds = [pc.DecisaoGravada(0, AcaoPet.EXPLORAR, AcaoPet.EXPLORAR, Alvo("seguir", 3, 4, 7, None)),
          pc.DecisaoGravada(1, AcaoPet.OCIOSO), pc.DecisaoGravada(2, AcaoPet.BRINCAR, AcaoPet.BRINCAR, Alvo("continuar", 1, 2, 0, "bola"))]
    assert [pc.DecisaoGravada.de_dict(json.loads(json.dumps(d.para_dict()))) for d in ds] == ds
    with pytest.raises(ValueError):
        pc.DecisaoGravada.de_dict({"indice": 0, "acao": "ocioso"})


# ------------------------------------------------------------------ o pet de hoje
def test_a_fabrica_do_jogo_exige_a_co7():
    with pytest.raises(ValueError, match="CO7"):
        a0.fabricas_do_jogo("atencioso", 1, CONFIG_COOPERACAO_LIGADA)
    fp, _ = a0.fabricas_do_jogo("atencioso", 1)
    assert fp(None).dever is not None                            # o modular nasce com os deveres (o jogo v39)


@pytest.mark.parametrize("s", [101, 202])
def test_g_grav_ident_co7_o_modular_com_a_co7_gravado_refaz_a_vida(s):
    from test_social_par_e1 import _identicas
    base = pc.viver_par(CM, s, [_vivo("A", s), _vivo("B", s, gravar=True)], 2, cfg_cooperacao=CONFIG_COOPERACAO_CO7)
    grav = pc.viver_par(CM, s, [_vivo("A", s), _gravado("B", s, base)], 2, cfg_cooperacao=CONFIG_COOPERACAO_CO7)
    _identicas(base, grav)


# ------------------------------------------------------------------ as faixas
def test_as_faixas_e_os_prefixos_do_a0():
    assert {"social_par", "social_par_piloto"} <= set(PREFIXOS_UNIDADES)
    faixas = {(lo, hi) for lo, hi, _ in FAIXAS_RESERVADAS}
    assert {(102101, 102505), (101101, 101505)} <= faixas


# ------------------------------------------------------------------ G-ORQ: a fumaca do orquestrador, as travas e o piloto
@pytest.fixture(scope="module")
def fumaca(tmp_path_factory):
    import run_v3_social_par_a0 as a0
    pasta = tmp_path_factory.mktemp("a0") / "fumaca"
    return a0.rodar({"modo": "fumaca", "unidades": {"bases": [101, 202], "k": 1}}, pasta, 1), pasta


def test_g_orq_a_fumaca_faz_as_cinco_vidas_com_o_g_instr_e_o_g1(fumaca):
    r, pasta = fumaca
    assert r["meta"]["vidas"] == 10 and len(r["registros"]) == 2
    assert all(x["g_instr"] and x["g1"] for x in r["registros"])
    assert sorted(p.name for p in (pasta / "vidas").iterdir()) == ["101-0000.json.gz", "202-0000.json.gz"]
    for x in r["registros"]:
        assert set(x["condicoes"]) == {"VIVO", "GRAV", "OUTRA"}
        v, g = x["condicoes"]["VIVO"], x["condicoes"]["GRAV"]
        assert v["cabe"] and g["cabe"] and v["distancia_no_t0"] == g["distancia_no_t0"]      # iguais ate o t0 (o G-INSTR)
        assert v["desvios_P"] == {}                                                             # o vivo nao tem gravacao
    res = json.loads((pasta / "resultado.json").read_text(encoding="utf-8"))
    assert set(res) >= {"premissas", "primarios", "secundarios", "leitura", "descritivo"}
    assert res["leitura"]["A0"]["classe"] == "inconclusivo por premissa"                       # 2 pares: a PA-2 pede 100


def test_g_instr_falha_alto_quando_a_grav_difere_antes_do_t0(fumaca):
    import run_v3_social_par_a0 as a0
    from dataclasses import replace
    s = 101
    ss = SS(s)
    pert = ("A", "B", 1560, 3, a0.D0)
    vivo = a0._viver(s, [a0._vivo("A", ss), a0._vivo("B", ss)], pert)
    torta = replace(vivo, posicoes={**vivo.posicoes, "B": [(0, 0)] + vivo.posicoes["B"][1:]})
    with pytest.raises(RuntimeError, match="G-INSTR"):
        a0.g_instr(vivo, torta)


def test_as_travas_do_orquestrador(tmp_path):
    import run_v3_social_par_a0 as a0
    from bancada.faixas import SementeSemPlano
    with pytest.raises(SementeSemPlano):
        a0.modo_da_config({"modo": "fumaca", "unidades": {"bases": [102101], "k": 1}})
    with pytest.raises(ValueError, match="K_RUN"):                                              # o K da run espera o piloto
        a0.modo_da_config({"modo": "run", "unidades": {"bases": list(a0.BASES["run"]), "k": 40}})
    with pytest.raises(ValueError, match="piloto"):
        a0.rodar({"modo": "piloto", "unidades": {"bases": list(a0.BASES["piloto"]), "k": 20}}, tmp_path / "p", 1)
    with pytest.raises(ValueError, match="K = 20"):
        a0.modo_da_config({"modo": "piloto", "unidades": {"bases": list(a0.BASES["piloto"]), "k": 5}})
    with pytest.raises(ValueError, match="processos"):
        a0._executar([], str(tmp_path), 5)
    (tmp_path / "ja").mkdir()
    with pytest.raises(FileExistsError):
        a0.coletar({"modo": "fumaca", "unidades": {"bases": [101], "k": 1}}, tmp_path / "ja", 1)


def test_o_piloto_nao_grava_media_e_a_regra_do_n(fumaca):
    import piloto_social_par_a0 as pl
    r, _ = fumaca
    out = pl.resumo(r["registros"], 10.0, 1)
    texto = json.dumps(out)
    assert "media" not in texto                                                                 # nenhuma media de contraste
    assert set(out["regra"]) == {"A0", "B0"}
    assert pl.regra_do_n(10.0, 4.0)["n"] == 200                                                 # 1,97 x 12 / 14,1 = 1,67 <= 2
    assert pl.regra_do_n(20.0, 4.0)["n"] == 800                                                 # 47,3 / 20 = 2,36 > 2; / 28,3 = 1,67
    r1600 = pl.regra_do_n(1000.0, 4.0)
    assert r1600["n"] == 1600 and r1600["bastou"] is False
    assert pl.regra_do_n(None, 4.0)["n"] is None
