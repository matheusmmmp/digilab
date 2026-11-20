"""O sono que segura do DigiBrain modular (docs/TAREFA_V3_SONO_SEGURA.md): a `ConfigSonoSegura`, o reflexo do M-ARB com a histerese e uma
vida do laboratorio (o braco REL, o do jogo) em que o pet dormindo so acorda com a energia acima de `lambda_acordar` ou com a fome
urgente. A chave desligada (a vida de hoje byte a byte) esta no tests/test_gabarito_sono_segura.py."""
from __future__ import annotations

import sys
from dataclasses import fields
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import run_v2_digibrain_prototipo as orq  # noqa: E402

from digilab.config import (CONFIG_DIGIBRAIN_INATOS, CONFIG_SONO_SEGURA, CONFIG_SONO_SEGURA_LIGADA, PARAMETROS_SONO_SEGURA,  # noqa: E402
                            ConfigSonoSegura)
from digilab.digibrain.arb import Arbitragem  # noqa: E402

S = CONFIG_DIGIBRAIN_INATOS.escala
URG = CONFIG_DIGIBRAIN_INATOS.urgencia_lambda


def _sens(energia: int, dormindo: bool) -> dict:
    return {"leitura": {"energia": energia}, "contexto": {"dormindo": S if dormindo else 0}}


def test_a_config_padrao_desligada_e_o_status_de_cada_campo():
    assert CONFIG_SONO_SEGURA.ligada is False and CONFIG_SONO_SEGURA_LIGADA.ligada is True
    assert CONFIG_SONO_SEGURA.lambda_acordar == 922 and CONFIG_SONO_SEGURA.lambda_acordar / S > 0.9 > (CONFIG_SONO_SEGURA.lambda_acordar - 1) / S
    assert {f.name for f in fields(ConfigSonoSegura)} == set(PARAMETROS_SONO_SEGURA)
    assert all(st in ("PROPOSTO", "DECIDIDO") and "SEM FONTE" in fonte for st, fonte in PARAMETROS_SONO_SEGURA.values())
    with pytest.raises(TypeError):
        ConfigSonoSegura(ligada=1)
    with pytest.raises(ValueError):
        ConfigSonoSegura(lambda_acordar=CONFIG_DIGIBRAIN_INATOS.lambda_sono)
    with pytest.raises(ValueError):
        ConfigSonoSegura(lambda_acordar=S + 1)


def test_desligada_o_reflexo_de_hoje():
    arb = Arbitragem()
    assert arb.reflexo(_sens(255, False)) is True
    assert arb.reflexo(_sens(256, True)) is False           # dormindo nao segura: so a energia abaixo de S/4
    assert arb.reflexo(_sens(900, True), {"fome": 0}) is False


def test_ligada_a_histerese():
    arb = Arbitragem(sono=CONFIG_SONO_SEGURA_LIGADA)
    calmo, urgente = {"fome": URG}, {"fome": URG + 1}
    assert arb.reflexo(_sens(255, False), calmo) is True     # o reflexo de sempre
    assert arb.reflexo(_sens(255, True), urgente) is True    # abaixo de S/4, nem a fome acorda
    assert arb.reflexo(_sens(256, False), calmo) is False    # acordado, nada a segurar
    assert arb.reflexo(_sens(921, True), calmo) is True      # dormindo, abaixo de 90 %: segue dormindo
    assert arb.reflexo(_sens(922, True), calmo) is False     # passou de 90 %: acorda
    assert arb.reflexo(_sens(600, True), urgente) is False   # a fome urgente acorda
    with pytest.raises(RuntimeError, match="urgencia da fome"):
        arb.reflexo(_sens(600, True))


def _vida(dono: str, semente: int, sono):
    """a vida do laboratorio (REL, comedouro, 4 dias), com o reflexo de cada decisao gravado: (energia, dormindo, u_fome, reflexo)"""
    fp, fm = orq.fabricas("REL", dono, semente, 4, orq.ORCAMENTO_POR_DIA, conserto=True, sono=sono)
    reflexos = []

    def fp_gravando(cfg=None):
        reg = fp(cfg)
        arb = orq.cerebro_de(reg).m.arb
        original = arb.reflexo

        def reflexo(sens, urgencias=None):
            r = original(sens, urgencias) if urgencias is not None else original(sens)
            reflexos.append((sens["leitura"]["energia"], sens["contexto"]["dormindo"] > 0, None if urgencias is None else urgencias["fome"], r))
            return r
        arb.reflexo = reflexo
        return reg

    from bancada.regras_mundo import simular_vida_fisico
    from digilab.donos import criar_dono
    from digilab.mundo import DonoComLugar
    registro = fp_gravando()
    motor, _ = simular_vida_fisico(DonoComLugar(criar_dono(dono), "comedouro", semente, dono, orq.CM), registro, semente, 4,
                                   orq.ORCAMENTO_POR_DIA * 4, dono, fm)
    return orq.cerebro_de(registro).motivos, reflexos, motor


@pytest.mark.parametrize("dono", ["atencioso", "relapso"])
def test_a_vida_dorme_ate_passar_de_90_por_cento_salvo_a_fome_urgente(dono):
    motivos, reflexos, _ = _vida(dono, 101, CONFIG_SONO_SEGURA_LIGADA)
    assert len(motivos) == len(reflexos) == 4 * 96
    lam = CONFIG_SONO_SEGURA.lambda_acordar
    acordou_cheio = acordou_fome = acordou_dono = 0
    for k in range(1, len(motivos)):
        energia, dormindo, u_fome, r = reflexos[k]
        if dormindo and energia < lam and u_fome <= URG:
            assert r and motivos[k]["acao"] == "dormir" and motivos[k]["reflexo"], k
        if motivos[k - 1]["acao"] == "dormir" and motivos[k]["acao"] != "dormir":   # acordou nesta decisao
            if not dormindo:                                                           # o dono o acordou (o brincar tira o dormindo)
                assert any(g[0] == "brincar" for g in motivos[k]["gestos"]), k
                acordou_dono += 1
                continue
            assert energia >= lam or u_fome > URG, (k, energia, u_fome)
            acordou_cheio += energia >= lam
            acordou_fome += energia < lam
    assert acordou_cheio > 0 and acordou_dono > 0
    # e menos cochilos que a vida de hoje, com a mesma semente
    hoje, _, _ = _vida(dono, 101, None)

    def cochilos(ms):
        return sum(1 for i, m in enumerate(ms) if m["acao"] == "dormir" and (i == 0 or ms[i - 1]["acao"] != "dormir"))
    assert cochilos(motivos) < cochilos(hoje) / 2


def test_o_replay_da_vida_com_a_chave_ligada():
    """o G1 do orquestrador: a vida com a chave ligada, rejogada do log, sai igual"""
    motor, reg, fabricas_vida = orq.viver("REL", "atencioso", "comedouro", 202, 2, orq.ORCAMENTO_POR_DIA, conserto=True,
                                          sono=CONFIG_SONO_SEGURA_LIGADA)
    orq.conferir_replay(motor, fabricas_vida, 202, motor.log.para_jsonl())


def test_o_gabarito_do_ts_esta_em_dia_e_as_vidas_diferem_das_de_hoje():
    """o web/app/test/gabaritos/digibrain_modular_sono_segura.json.gz (exportar_gabarito_digibrain_modular.py --sono) e o do codigo"""
    import gzip
    import json

    import exportar_gabarito_digibrain_modular as G
    dados = G.sono_segura()
    # o conteudo, nao os bytes do .gz (outro zlib comprime o mesmo texto em bytes diferentes)
    assert gzip.decompress(dados) == gzip.decompress((G.PASTA / G.ARQUIVO_SONO).read_bytes())
    g = json.loads(gzip.decompress(dados))
    assert g["config_sono_segura"] == {"ligada": True, "lambda_acordar": CONFIG_SONO_SEGURA.lambda_acordar}
    assert [(v["dono"], v["lugar"], v["semente"]) for v in g["vidas"]] == list(G.VIDAS_SONO)
    assert all(v["difere_de_hoje"] is True and len(v["decisoes"]) == 384 for v in g["vidas"])
