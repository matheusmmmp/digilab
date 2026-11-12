"""A CO7 da cooperacao (docs/ESPEC_V3_COOPERACAO_CO7.md): os deveres como escudo, o teste da universalizacao e a culpa e a inveja.

- o G2: com a CO7 desligada, as vidas do grupo com a CO6 ligada (o modular nos dois pets) saem byte a byte contra o gabarito gravado antes
  da mudanca (experiments/exportar_gabarito_co7.py, tests/gabaritos/co7_vidas_de_hoje.json.gz); a ConfigCooperacao da CO7 no grupo, com o
  cerebro sem ela, tambem;
- o G-ESCUDO: com a CO7 ligada, nenhuma decisao escolhe comer a comida proibida quando o escudo vale, contado em todas as decisoes das vidas
  do gabarito do G-PAR-CO7 (experiments/exportar_gabarito_co7_par.py);
- o G-RECEPTOR-SOCIAL: as contas so leem o que e fisico e o proprio estado (a percepcao social, as comidas a vista, as proprias leituras);
- os casos a mao: o escudo e a excecao do proprio piso, a universalizacao com o teto, e a culpa e a inveja;
- o gabarito do G-PAR-CO7 (o do TS) refeito sai igual."""
from __future__ import annotations

import ast
import gzip
import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "experiments"))

import exportar_gabarito_co7 as e7  # noqa: E402
import exportar_gabarito_co7_par as ep  # noqa: E402

from digilab.config import (CONFIG_COOPERACAO, CONFIG_COOPERACAO_CO6, CONFIG_COOPERACAO_CO7, CONFIG_MUNDO_MVP,  # noqa: E402
                            PARAMETROS_COOPERACAO, ConfigCooperacao)
from digilab.digibrain import dever as dv  # noqa: E402
from digilab.mundo import PercepcaoSocial  # noqa: E402

GABARITO = json.loads(gzip.decompress(e7.ARQUIVO.read_bytes()).decode())
PAR = json.loads(gzip.decompress(ep.ARQUIVO.read_bytes()).decode())
CFG = CONFIG_COOPERACAO_CO7
S = CFG.escala


@pytest.mark.parametrize("i", range(len(e7.VIDAS)))
def test_g2_co7_desligada_vidas_com_a_co6(i):
    v = e7.VIDAS[i]
    assert GABARITO["vidas"][i]["semente"] == v[0]
    assert json.loads(json.dumps(e7.vida(v), sort_keys=True)) == GABARITO["vidas"][i]


def test_g2_a_co7_no_grupo_sem_ela_no_cerebro_e_a_vida_da_co6():
    """a subchave co7 no grupo nao muda nada sozinha: so o cerebro com ela usa os sinais"""
    assert json.loads(json.dumps(e7.vida(e7.VIDAS[0], CONFIG_COOPERACAO_CO7), sort_keys=True))["pets"] == GABARITO["vidas"][0]["pets"]


# ------------------------------------------------------------------ a chave
def test_a_chave_desligada_por_padrao_e_so_com_a_co6():
    assert CONFIG_COOPERACAO.co7 is False and CONFIG_COOPERACAO_CO6.co7 is False
    with pytest.raises(ValueError, match="co7 so liga"):
        ConfigCooperacao(ligada=True, co7=True)
    with pytest.raises(ValueError, match="piso_privacao_s"):
        ConfigCooperacao(ligada=True, co6=True, co7=True, piso_privacao_s=400)
    for nome in ("co7", "limiar_escudo", "r_escudo_celulas", "piso_privacao_s", "w_univ", "limiar_humor", "w_culpa", "w_inveja",
                 "janela_inveja"):
        assert nome in PARAMETROS_COOPERACAO
    assert CFG.limiar_escudo == CFG.k_teto_crianca == S // 4               # CO7-2: o teto da crianca


# ------------------------------------------------------------------ os casos a mao
def _ps(outros=(), onde_comeu=(), k=300):
    return PercepcaoSocial(tuple(outros), tuple(onde_comeu), (), None, (("B", 10),), k)


def _sens(soc, fome=800, humor=600, objetos=((7, "a", 30, 0),)):
    return {"social": soc, "leitura": {"fome": fome, "humor": humor}, "pos": (100, 100),
            "objetos": [{"id": i, "tipo": t, "dx": dx, "dy": dy} for i, t, dx, dy in objetos]}


R = CFG.r_escudo_celulas * CONFIG_MUNDO_MVP.sub                               # o raio do escudo em subunidades, no mundo do produto


def _social_indo(acao="emburrar", k=300, antes=(160, 100)):
    """B em (140, 100), a 10 da comida em (130, 100), e antes em `antes`"""
    return dv.social(_ps([("B", 40, 0, 40, acao)], k=k), (100, 100), {"B": antes}, R)


UNIDADES = [{"chave": ("comer", "comida", 7)}, {"chave": ("explorar", "vagar", None)}, {"chave": ("ocioso", None, None)}]


def test_o_escudo_tira_a_comida_do_aflito_que_vai_para_ela():
    sit = dv.situacao(_sens(_social_indo()), {"fome": 200, "humor": 100}, CFG, S)
    assert sit["proibidas"] == [7] and sit["escudo"] and not sit["privacao"] and sit["unica"]
    w, reg = dv.ajustar(UNIDADES, [500, 100, 0], sit)
    assert w[0] == 0 and reg["removidas"] == [0]
    assert w[1] == 100 + sit["delta"] and reg["aprovadas"] == 1           # a unica comida: deixar aprova
    assert sit["delta"] == min(dv.mul(300, CFG.w_univ, S), 200)            # o teto na urgencia mais forte


def test_o_escudo_nao_vale_sem_aflicao_sem_ir_para_a_comida_ou_longe():
    for soc in (_social_indo(acao="comer"),                                # sem aflicao visivel
                _social_indo(antes=(135, 100)),                            # se afastou da comida
                dv.social(_ps([("B", 40, 0, 40, "emburrar")]), (100, 100), {}, R),     # nunca visto antes
                dv.social(_ps([("B", 200, 0, 200, "emburrar")]), (100, 100), {"B": (400, 100)}, R)):   # longe da comida
        assert dv.situacao(_sens(soc), {"fome": 200}, CFG, S)["proibidas"] == []


def test_a_excecao_do_proprio_piso_e_o_limiar_do_k():
    sit = dv.situacao(_sens(_social_indo(), fome=CFG.piso_privacao_s - 1), {"fome": 900}, CFG, S)
    assert sit["privacao"] and not sit["escudo"] and sit["proibidas"] == [7]
    w, reg = dv.ajustar(UNIDADES, [500, 100, 0], sit)
    assert w[0] == 500 - sit["delta"] and reg["reprovadas"] == [0]         # sem o escudo, a universalizacao ainda reprova
    abaixo = dv.situacao(_sens(_social_indo(k=CFG.limiar_escudo - 1)), {"fome": 200}, CFG, S)
    assert not abaixo["escudo"]
    assert dv.situacao(_sens(_social_indo(k=CFG.limiar_escudo)), {"fome": 200}, CFG, S)["escudo"]


def test_com_k_zero_nada_muda_e_sem_sobrar_fica_o_ocioso():
    sit = dv.situacao(_sens(_social_indo(k=0)), {"fome": 200}, CFG, S)
    assert dv.ajustar(UNIDADES, [500, 100, 0], sit)[0] == [500, 100, 0]
    so_comer = dv.ajustar(UNIDADES, [500, 0, 0], dv.situacao(_sens(_social_indo()), {"fome": 200}, CFG, S))[0]
    assert so_comer == [0, 0, 0]                                           # o _escolher do M-ARB fica com o ocioso


def test_a_culpa_e_a_inveja():
    aflito = _social_indo()
    assert dv.culpa_inveja(_sens(aflito, humor=CFG.limiar_humor), CFG) == (CFG.w_culpa, 0)
    assert dv.culpa_inveja(_sens(_social_indo(acao="comer"), humor=900), CFG) == (0, 0)
    comeu = dv.social(_ps([], [("B", 5, 5, CFG.janela_inveja)]), (0, 0), {}, R)
    assert dv.culpa_inveja(_sens(comeu, humor=CFG.limiar_humor - 1), CFG) == (0, CFG.w_inveja)
    velho = dv.social(_ps([], [("B", 5, 5, CFG.janela_inveja + 1)]), (0, 0), {}, R)
    assert dv.culpa_inveja(_sens(velho, humor=0), CFG) == (0, 0)
    assert dv.culpa_inveja(_sens(None), CFG) == (0, 0)
    with pytest.raises(ValueError, match="peso dos deveres"):
        dv.social(PercepcaoSocial((), (), ()), (0, 0), {}, R)              # a CO7 sem a CO6 no grupo: falha alto


# ------------------------------------------------------------------ o G-RECEPTOR-SOCIAL
def test_g_receptor_social_as_contas_so_leem_o_fisico_e_o_proprio():
    arvore = ast.parse((RAIZ / "digilab" / "digibrain" / "dever.py").read_text(encoding="utf-8"))
    importa = {n.module for n in ast.walk(arvore) if isinstance(n, ast.ImportFrom)}
    assert importa == {"__future__", "_comum"}                             # nada do corpo, do motor ou de outro cerebro
    # da percepcao social, so os campos fisicos e o proprio k (a reputacao, que e memoria, nao entra nas contas da CO7)
    lidos = {n.attr for n in ast.walk(arvore) if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id == "ps"}
    assert lidos == {"outros", "onde_comeu", "peso_dever"}


# ------------------------------------------------------------------ o G-ESCUDO e o G-PAR-CO7
def test_o_gabarito_do_g_par_co7_e_o_de_hoje():
    assert json.loads(json.dumps(ep.gerar(), sort_keys=True)) == PAR


def test_g_escudo_nenhuma_decisao_faz_o_ato_proibido():
    valendo = 0
    for v in PAR["vidas"]:
        for es in v["escolhas"].values():
            for acao, escolha, d in es:
                if d is None or not d["escudo"] or not d["proibidas"]:
                    continue
                valendo += 1
                assert not (escolha[0] == "comer" and escolha[1] == "comida" and escolha[2] in d["proibidas"]), (v["semente"], escolha, d)
    assert valendo >= 5                                                    # o gabarito tem decisoes em que o escudo vale (o relato da o numero)
    reprovou = sum(len(d["reprovadas"]) for v in PAR["vidas"] for es in v["escolhas"].values() for _, _, d in es if d)
    aprovou = sum(1 for v in PAR["vidas"] for es in v["escolhas"].values() for _, _, d in es if d and d["aprovadas"])
    assert reprovou > 0 and aprovou > 0


# ------------------------------------------------------------------ os ganchos da bancada (docs/PLANO_ANALISE_V3_COOPERACAO.md)
def test_os_ganchos_da_bancada_nao_mudam_o_padrao_e_desligam_cada_parte():
    from dataclasses import replace
    from digilab.cooperacao import Cooperacao
    assert (CFG.fator_teto_k, CFG.co7_escudo, CFG.co7_universalizacao, CFG.co7_afeto) == (S, True, True, True)
    meio = Cooperacao(replace(CFG, fator_teto_k=S // 2))
    zero = Cooperacao(replace(CFG, fator_teto_k=0))
    cheio = Cooperacao(CFG)
    for idade in (0, 1440, 3 * 1440, 7 * 1440):
        assert meio.teto_k(idade) == (cheio.teto_k(idade) + 1) // 2 and zero.teto_k(idade) == 0
    sens = _sens(_social_indo())
    so_univ = dv.situacao(sens, {"fome": 200}, replace(CFG, co7_escudo=False), S)
    assert not so_univ["escudo"] and so_univ["delta"] > 0 and so_univ["proibidas"] == [7]
    so_escudo = dv.situacao(sens, {"fome": 200}, replace(CFG, co7_universalizacao=False), S)
    assert so_escudo["escudo"] and so_escudo["delta"] == 0
    assert dv.culpa_inveja(_sens(_social_indo(), humor=900), replace(CFG, co7_afeto=False)) == (0, 0)
