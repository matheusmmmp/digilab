"""A competicao entre as regras urgentes no cerebro A (V3-3/V3-4; docs/TAREFA_V2_V3_COMPETICAO.md, secoes 3 e 5), etapa 1:
- G-R1-REGRAS: as regras que valem e os candidatos sao o espelho do PoliticaInstinto (observacoes aleatorias);
- G2: desligada (None ou ConfigCompeticao()), a vida de hoje, contra o gabarito do E0 (`tests/gabaritos/competicao_vidas_de_hoje.json`);
- G-R1-UMA-REGRA: ligada, uma vida em que nenhuma decisao abre e a vida de hoje (o log e o motor);
- G-R1-SEGURANCA: ligada, com o sono_exaustao a decisao e dormir, forcada, sem sorteio;
- G-R1-CREDITO: cada tabela que propos recebe a L1 so nas suas propostas, com os P da disputa e o W sem o kappa;
- G1: ligada, o replay bit a bit (do log serializado);
- o R1-congelado (o aprendizado desligado): a disputa sem credito, os pesos no prior;
- o motivo honesto: o motivo_lobos de cada decisao aberta cita a regra de onde veio a acao e confere o "aprendido decidiu";
- o n_pesos igual com e sem a chave, e a chave falha alto fora do v11 sem o mundo."""
from __future__ import annotations

import json
import random
import sys
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "tests"))
sys.path.insert(0, str(RAIZ / "experiments"))

import gabarito_competicao as gc  # noqa: E402

from digilab.config import (CONFIG_COMPETICAO, CONFIG_COMPETICAO_LIGADA, CONFIG_FRUTAS_LIGADA, CONFIG_LOBOS, CONFIG_PADRAO,  # noqa: E402
                            ConfigCompeticao)
from digilab.events import AcaoPet, LogDeEventos  # noqa: E402
from digilab.motivo import motivo_lobos  # noqa: E402
from digilab.policies.lobos import (PARAMETROS_COMPETICAO, PoliticaLobos, atualizar_pesos, candidatos_da_regra,  # noqa: E402
                                    propostas_da_disputa, regras_que_valem)
from digilab.policy import Observacao, PoliticaInstinto  # noqa: E402


def _obs(rng: random.Random) -> Observacao:
    v = (rng.random(), rng.random(), rng.random(), rng.random(), rng.random(), rng.random(), float(rng.random() < 0.4), rng.random())
    return Observacao(vetor_estado=v, ticks_desde_cuidado=rng.randrange(0, 600), total_cuidados=0)


def _cerebro(vida):
    p = vida.motor.politica
    return getattr(p, "cerebro", p)


@pytest.fixture(scope="module")
def ligada():
    return replace(gc.bancada(), cfg_competicao=CONFIG_COMPETICAO_LIGADA)


@pytest.fixture(scope="module")
def vida_relapso(ligada):
    return ligada.vida(gc.espec("relapso", 101))


def test_g_r1_regras_o_espelho_do_instinto():
    rng = random.Random(17)
    inst = PoliticaInstinto(CONFIG_PADRAO)
    for _ in range(20_000):
        obs = _obs(rng)
        acao = inst.agir(obs, random.Random(3))
        valem = regras_que_valem(obs, CONFIG_PADRAO)
        assert valem[0] == inst.ultima_regra and valem[-1] == "tempo_livre"
        if valem[0] != "tempo_livre":
            assert acao in candidatos_da_regra(valem[0], obs)


def test_as_propostas_seguem_a_v3_4_e_a_cr_3():
    obs = Observacao(vetor_estado=(0.1, 0.9, 0.9, 0.5, 1.0, 0.0, 0.0, 0.5), ticks_desde_cuidado=0, total_cuidados=0)
    assert propostas_da_disputa(("sono_exaustao", "pedido_necessidade", "fome_moderada", "tempo_livre"), obs) is None
    assert propostas_da_disputa(("fome_moderada", "tempo_livre"), obs) is None
    assert propostas_da_disputa(("sono_continuar", "sono_noite", "tempo_livre"), obs) is None
    assert propostas_da_disputa(("pedido_necessidade", "fome_moderada", "tempo_livre"), obs) == {
        AcaoPet.CHAMAR_ATENCAO: "pedido_necessidade", AcaoPet.COMER: "fome_moderada"}


def test_g2_desligada_e_a_vida_de_hoje():
    """None (a bancada de hoje) e a ConfigCompeticao desligada dao as vidas do gabarito do E0"""
    g = json.loads(gc.ARQUIVO.read_text(encoding="utf-8"))
    desligada = replace(gc.bancada(), cfg_competicao=CONFIG_COMPETICAO)
    for dono, s in (("relapso", 101), ("aleatorio", 202)):
        assert gc.impressao(desligada.vida(gc.espec(dono, s)).motor) == g[f"v11|{dono}|{s}"]


def test_g_r1_uma_regra_vida_sem_abertura_e_a_de_hoje(ligada):
    """o atencioso 101 nao abre nenhuma decisao no R0 (a etapa 0): ligada, a vida e a mesma ate o fim (o log e o motor; o estado interno
    ganha so o contador da competicao)"""
    g = json.loads(gc.ARQUIVO.read_text(encoding="utf-8"))["v11|atencioso|101"]
    v = ligada.vida(gc.espec("atencioso", 101))
    imp = gc.impressao(v.motor)
    assert imp["log"] == g["log"] and imp["resumo"] == g["resumo"]
    assert _cerebro(v).estado_interno()["competicao"] == {"kappa": 16, "abertas": 0}


def test_g_r1_seguranca_e_a_disputa(vida_relapso):
    cer = _cerebro(vida_relapso)
    abertas = 0
    for m in cer.motivos:
        p = m["percepcao"]
        if p["energia"] < 0.25:                                   # o sono_exaustao: forcado, sem sorteio
            assert m["regra"] == "sono_exaustao" and m["acao"] == "dormir" and m["u"] is None and "competicao" not in m
        if "competicao" in m:
            abertas += 1
            c = m["competicao"]
            assert len(m["candidatos"]) >= 2 and m["u"] is not None and len(c["regras"]) >= 2
            assert c["propostas"][c["acao_do_instinto"]] == m["regra"]
            for a in m["candidatos"]:                             # o kappa so nas propostas da regra do instinto
                k = c["kappa"] if c["propostas"][a] == m["regra"] else 1
                assert m["pesos"][a] == k * c["pesos_sem_kappa"][a]
    assert abertas == cer.estado_interno()["competicao"]["abertas"] > 0


def test_g_r1_credito_por_tabela():
    """uma decisao aberta sintetica: pedido (chamar) x fome moderada (comer); so as duas linhas mudam, cada uma pela L1 com o P da disputa"""
    cer = PoliticaLobos(CONFIG_PADRAO, replace(CONFIG_LOBOS, aprendizado_ligado=True), cfg_competicao=CONFIG_COMPETICAO_LIGADA)
    S = cer._escala
    antes = {g: {a: list(v) for a, v in t.items()} for g, t in cer._pesos.items()}
    ch, co = AcaoPet.CHAMAR_ATENCAO, AcaoPet.COMER
    X = [S, 100, 200, 300, 400, 500, 0, 0, 600, 700]
    reg = {"regra": "pedido_necessidade", "candidatos": (ch, co), "acao": ch, "X": X[:len(antes["tempo_livre"][ch])],
           "P": {ch: 963, co: S - 963}, "W": {ch: S, co: S},
           "competicao": {"tabelas": {"pedido_necessidade": (ch,), "fome_moderada": (co,)}, "kappa": 16}}
    assert (S - reg["P"][ch]) - reg["P"][co] == 0                 # os fatores da decisao somam zero
    cer._aplicar_sinal(reg, 2 * S)
    for g, t in cer._pesos.items():
        for a, v in t.items():
            if (g, a) in (("pedido_necessidade", ch), ("fome_moderada", co)):
                continue
            assert v == antes[g][a], (g, a)
    esperado_ch = {a: list(v) for a, v in antes["pedido_necessidade"].items()}
    atualizar_pesos(esperado_ch, cer._prior["pedido_necessidade"], {**reg, "candidatos": (ch,)}, 2 * S, cer.cl.passo, cer.cl.teto, S)
    esperado_co = {a: list(v) for a, v in antes["fome_moderada"].items()}
    atualizar_pesos(esperado_co, cer._prior["fome_moderada"], {**reg, "candidatos": (co,)}, 2 * S, cer.cl.passo, cer.cl.teto, S)
    assert cer._pesos["pedido_necessidade"][ch] == esperado_ch[ch] != antes["pedido_necessidade"][ch]
    assert cer._pesos["fome_moderada"][co] == esperado_co[co] != antes["fome_moderada"][co]
    assert cer._pesos["pedido_necessidade"][ch][0] > antes["pedido_necessidade"][ch][0]   # a escolhida sobe com sinal positivo
    assert cer._pesos["fome_moderada"][co][0] < antes["fome_moderada"][co][0]             # a outra desce


def test_g1_replay_ligada(ligada, vida_relapso):
    """o replay do log serializado refaz a vida ligada bit a bit (o conferir_replay da bancada, com o texto do disco)"""
    ligada.conferir_replay(vida_relapso, vida_relapso.motor.log.para_jsonl())
    r = ligada.rejogar(LogDeEventos.de_jsonl(vida_relapso.motor.log.para_jsonl()), vida_relapso.espec)
    assert _cerebro_motor(r).motivos == _cerebro(vida_relapso).motivos


def _cerebro_motor(motor):
    p = motor.politica
    return getattr(p, "cerebro", p)


def test_r1_congelado_disputa_sem_credito(ligada):
    """o P0-c-tapa (o mesmo corpo e o mesmo dono do v11, o aprendizado desligado) com a chave: as decisoes abrem, e os pesos ficam no prior"""
    v = ligada.vida(gc.espec("relapso", 101).__class__("relapso", "P0-c-tapa", 101))
    cer = _cerebro(v)
    assert any("competicao" in m for m in cer.motivos)
    assert cer._pesos == cer._prior


def test_o_motivo_honesto(vida_relapso):
    cer = _cerebro(vida_relapso)
    vistos = {"impulsos": 0, "decisao": 0}
    for k, m in enumerate(cer.motivos):
        if "competicao" not in m:
            continue
        mot, diag = motivo_lobos(m, 15 * k, None)
        assert mot.acao == m["acao"]
        assert diag["competicao"]["regra_da_acao"] == m["competicao"]["propostas"][m["acao"]]
        assert (diag["lobo"] == "decisao") == m["competicao"]["aprendido_decidiu"]
        vistos[diag["lobo"]] += 1
    assert vistos["impulsos"] > 0 and vistos["decisao"] > 0


def test_n_pesos_e_a_chave_fora_do_v11():
    assert {f for f in ConfigCompeticao.__dataclass_fields__} == set(PARAMETROS_COMPETICAO)
    cl = replace(CONFIG_LOBOS, aprendizado_ligado=True)
    assert (PoliticaLobos(CONFIG_PADRAO, cl).n_pesos()
            == PoliticaLobos(CONFIG_PADRAO, cl, cfg_competicao=CONFIG_COMPETICAO_LIGADA).n_pesos())
    with pytest.raises(ValueError, match="v11 sem o mundo"):
        PoliticaLobos(CONFIG_PADRAO, cl, cfg_frutas=CONFIG_FRUTAS_LIGADA, cfg_competicao=CONFIG_COMPETICAO_LIGADA)
    with pytest.raises(ValueError):
        ConfigCompeticao(ligada=True, kappa_instinto=0)
    with pytest.raises(TypeError):
        ConfigCompeticao(ligada=1)
