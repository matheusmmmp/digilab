"""O C0 da PLASTICIDADE_EVOLUIDA (docs/TAREFA_V3_PLASTICIDADE_EVOLUIDA.md, secoes 9.1 e 9.2): o critico do P2 atras da ConfigCritico
(digilab/digibrain/plast.py), o G2 (desligada, as vidas de hoje byte a byte: tests/gabaritos/critico_de_hoje.json), a conta do erro de
diferenca temporal a mao, o estado e o replay, as duas medidas novas do metrics.py (a entropia do sorteio e para onde vai o credito do
habito), o orquestrador da triagem (experiments/run_v3_plasticidade_c0.py), a leitura, a trava e a fumaca nas sementes dos testes."""
from __future__ import annotations

import json
import math
import sys
from dataclasses import fields, replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import bancada_v2 as bv  # noqa: E402
import gabarito_critico  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402
import run_v3_plasticidade_c0 as C0  # noqa: E402
import run_v3_plasticidade_e0 as E0  # noqa: E402
from digilab import metrics as met  # noqa: E402
from digilab.config import (CARACTERISTICAS_DIGIBRAIN, CONFIG_CRITICO, CONFIG_CRITICO_LIGADA, CONFIG_DIGIBRAIN_INATOS,  # noqa: E402
                            CONFIG_DIGIBRAIN_LIGADA, CONFIG_ELOGIO_LIGADA, CONFIG_PADRAO, PARAMETROS_CRITICO, ConfigCritico,
                            ConfigDigibrain)
from digilab.digibrain import DigiBrain  # noqa: E402
from digilab.digibrain._comum import clamp, mul  # noqa: E402
from digilab.digibrain.plast import Plasticidade  # noqa: E402

FUMACA = json.loads((RAIZ / "experiments/configs/v3_plasticidade_c0/fumaca.json").read_text(encoding="utf-8"))
RUN = json.loads((RAIZ / "experiments/configs/v3_plasticidade_c0/run.json").read_text(encoding="utf-8"))
S = CONFIG_DIGIBRAIN_INATOS.escala
N = len(CARACTERISTICAS_DIGIBRAIN)


# ------------------------------------------------------------------ a config e a chave
def test_a_config_do_critico():
    assert set(PARAMETROS_CRITICO) == {f.name for f in fields(ConfigCritico)}
    assert all(st == "PROPOSTO" and "SEM FONTE" in fonte for st, fonte in PARAMETROS_CRITICO.values())
    assert CONFIG_CRITICO == ConfigCritico() and not CONFIG_CRITICO.ligada and CONFIG_CRITICO_LIGADA == replace(CONFIG_CRITICO, ligada=True)
    assert (CONFIG_CRITICO.eta_v, CONFIG_CRITICO.gamma) == (S // 16, 15 * S // 16)
    assert "critico" not in {f.name for f in fields(ConfigDigibrain)}          # o dump do modular (o gabarito de paridade) nao muda
    for errada in ({"ligada": 1}, {"eta_v": 0}, {"eta_v": S + 1}, {"eta_v": 1.5}, {"gamma": -1}, {"gamma": S + 1}):
        with pytest.raises((TypeError, ValueError)):
            ConfigCritico(**errada)


def test_o_g2_desligada_as_vidas_de_hoje_saem_iguais_byte_a_byte():
    gravado = json.loads(gabarito_critico.ARQUIVO.read_text(encoding="utf-8"))
    assert len(gravado) == 16 and gabarito_critico.gerar() == gravado
    # a ConfigCritico desligada, passada ao cerebro, tambem e a vida de hoje
    motor, registro, _ = E0.viver("hoje", "APRENDE", "relapso", "longe_fixo", 101, 3, critico=CONFIG_CRITICO)
    c = orq.cerebro_de(registro)
    assert gabarito_critico._sha(gabarito_critico._texto(c.motivos)) == gravado["APRENDE|relapso|longe_fixo|101"]["motivos"]
    assert c.cr is None and c.m.plast.cr is None and "critico" not in c.m.plast.estado_interno()
    assert not hasattr(c.m.plast, "V") and not any("critico" in m for m in c.motivos)


def test_o_critico_recusa_as_combinacoes_sem_teste():
    for cd in (replace(CONFIG_DIGIBRAIN_LIGADA, p2=False), replace(CONFIG_DIGIBRAIN_LIGADA, credito_corrida=True),
               replace(CONFIG_DIGIBRAIN_LIGADA, fala_unidades=True), replace(CONFIG_DIGIBRAIN_LIGADA, olhar=True),
               replace(CONFIG_DIGIBRAIN_LIGADA, unidades_sociais=True)):
        with pytest.raises(ValueError, match="critico"):
            Plasticidade(cd, critico=CONFIG_CRITICO_LIGADA)
    with pytest.raises(TypeError):
        Plasticidade(CONFIG_DIGIBRAIN_LIGADA, critico=True)
    with pytest.raises(ValueError, match="ConfigElogio"):
        DigiBrain(CONFIG_PADRAO, CONFIG_DIGIBRAIN_LIGADA, cfg_critico=CONFIG_CRITICO_LIGADA, cfg_elogio=CONFIG_ELOGIO_LIGADA)
    with pytest.raises(TypeError):
        DigiBrain(CONFIG_PADRAO, CONFIG_DIGIBRAIN_LIGADA, cfg_critico="ligada")
    sem = Plasticidade(CONFIG_DIGIBRAIN_LIGADA)
    with pytest.raises(RuntimeError):
        sem.fechar_pendentes([0] * N)
    with pytest.raises(RuntimeError):
        sem.valor([0] * N)


# ------------------------------------------------------------------ a conta do erro de diferenca temporal
def _z(**v) -> list:
    return [v.get(c, 0) for c in CARACTERISTICAS_DIGIBRAIN]


def test_a_conta_do_critico_a_mao():
    cr = CONFIG_CRITICO_LIGADA
    p = Plasticidade(CONFIG_DIGIBRAIN_LIGADA, critico=cr)
    inatos = p.p
    e, z2 = _z(vies=S, u_fome=S // 2), _z(vies=S)
    # a opcao fica guardada: nada muda ate o z de depois
    reg = p.creditar({"chave": ("comer", "comida", 7), "r": 400, "g_apr": S, "e": e})
    assert reg == {"regra": "P2-critico", "b": "comer", "r_n": 400, "pendente": True, "abs": 0}
    assert p.habito_zero() and p.V == [0] * N and len(p.pendentes) == 1 and p.creditos == 0
    # o primeiro credito: V = 0, entao delta = r
    (f,) = p.fechar_pendentes(z2)
    assert (f["v0"], f["v1"], f["delta"]) == (0, 0, 400) and p.pendentes == [] and p.creditos == 1
    passo_v, passo_h = mul(mul(S, cr.eta_v, S), 400, S), mul(S, inatos.eta_h, S)
    j_vies, j_fome = CARACTERISTICAS_DIGIBRAIN.index("vies"), CARACTERISTICAS_DIGIBRAIN.index("u_fome")
    assert p.V[j_vies] == mul(passo_v, S, S) == 25 and p.V[j_fome] == mul(passo_v, S // 2, S)
    assert p.H["comer"][j_vies] == mul(passo_h, mul(400, S, S), S) and p.H["comer"][j_fome] == mul(passo_h, mul(400, S // 2, S), S)
    assert f["abs"] == sum(abs(x) for x in p.H["comer"]) and f["abs_v"] == sum(abs(x) for x in p.V)
    assert all(v == 0 for b, linha in p.H.items() if b != "comer" for v in linha)
    # o segundo, igual: agora o V preve parte da recompensa, e o delta e menor que o r (o erro de previsao)
    v0, v1 = p.valor(e), p.valor(z2)
    assert v0 == mul(p.V[j_vies], S, S) + mul(p.V[j_fome], S // 2, S) and v1 == p.V[j_vies] and v0 > 0
    p.creditar({"chave": ("comer", "comida", 8), "r": 400, "g_apr": S, "e": e})
    (f2,) = p.fechar_pendentes(z2)
    assert (f2["v0"], f2["v1"]) == (v0, v1) and f2["delta"] == clamp(400 + mul(cr.gamma, v1, S) - v0, -S, S) and f2["delta"] != 400
    # a recompensa que nao veio, onde o V esperava: o delta e negativo com o r em 0
    p.creditar({"chave": ("comer", "comida", 9), "r": 0, "g_apr": S, "e": e})
    (f3,) = p.fechar_pendentes(_z())
    assert f3["v1"] == 0 and f3["delta"] == -f3["v0"] < 0
    # o estado do V e das pendentes vai no estado interno
    p.creditar({"chave": ("dormir", None, None), "r": -50, "g_apr": S, "e": e})
    est = p.estado_interno()["critico"]
    assert est == {"eta_v": cr.eta_v, "gamma": cr.gamma, "V": p.V, "pendentes": [{"b": "dormir", "r": -50, "g_apr": S, "e": e}]}
    with pytest.raises(ValueError):
        p.creditar({"chave": ("dormir", None, None), "r": 0, "g_apr": S, "e": e[:-1]})


def test_os_cortes_do_critico():
    p = Plasticidade(CONFIG_DIGIBRAIN_LIGADA, critico=replace(CONFIG_CRITICO_LIGADA, eta_v=S))
    e = _z(vies=S)
    for _ in range(40):                                                         # o r no teto, muitas vezes: o V e o H ficam nos cortes
        p.creditar({"chave": ("comer", "comida", 1), "r": S, "g_apr": 2 * S, "e": e})
        (f,) = p.fechar_pendentes(_z())
        assert -S <= f["delta"] <= S
    assert all(-S <= v <= S for v in p.V) and all(abs(h) <= p.p.h_max for h in p.H["comer"])
    # com o gamma em 0 e o V em 0 o delta e o r: o P2 de hoje, so que adiado
    hoje, com = Plasticidade(CONFIG_DIGIBRAIN_LIGADA), Plasticidade(CONFIG_DIGIBRAIN_LIGADA, critico=replace(CONFIG_CRITICO_LIGADA, gamma=0))
    op = {"chave": ("brincar", "bola", 3), "r": 300, "g_apr": S, "e": _z(vies=S, bola_vista=S)}
    hoje.creditar(op)
    com.creditar(op)
    com.fechar_pendentes(_z(vies=S))
    assert com.H == hoje.H and not com.habito_zero()


# ------------------------------------------------------------------ o critico numa vida
def test_a_vida_com_o_critico_replay_e_contabilidade():
    motor, registro, fab = C0.viver("CRITICO", "relapso", "longe_fixo", 101, 3)
    orq.conferir_replay(motor, fab, 101, motor.log.para_jsonl())               # o estado do V vai no estado interno, e o replay o refaz
    E0.conferir_vida("hoje", "APRENDE", motor, registro, C0.CRITICO_DO_C0)
    c = orq.cerebro_de(registro)
    conta = C0.conferir_critico("teste", registro)
    assert conta["fechadas"] == c.m.plast.creditos > 0 and conta["v_abs"] > 0 and conta["pendentes_no_fim"] in (0, 1)
    assert motor.politica.estado_interno()["modulos"]["plast"]["critico"]["V"] == c.m.plast.V
    assert all(set(m["critico"]) == {"fechados", "V"} for m in c.motivos)
    # a opcao que acaba na consequencia da decisao k fecha na decisao k + 1, com o V(z) dela
    k = next(i for i, m in enumerate(c.motivos) if m["critico"]["fechados"])
    assert any(cr.get("pendente") for cr in c.motivos[k - 1]["consequencia"]["creditos"])
    # o braco HOJE e o CONGELADO nao tem o critico, e a conferencia recusa a vida trocada
    hoje, registro_hoje, _ = C0.viver("HOJE", "relapso", "longe_fixo", 101, 3)
    E0.conferir_vida("hoje", "APRENDE", hoje, registro_hoje)
    assert orq.cerebro_de(registro_hoje).cr is None
    with pytest.raises(E0.E0Divergiu, match="critico"):
        E0.conferir_vida("hoje", "APRENDE", motor, registro)
    with pytest.raises(E0.E0Divergiu, match="critico"):
        E0.conferir_vida("hoje", "APRENDE", hoje, registro_hoje, C0.CRITICO_DO_C0)
    assert E0.assinatura_da_vida(motor, registro) != E0.assinatura_da_vida(hoje, registro_hoje)   # o habito aprendido e outro
    with pytest.raises(ValueError):
        C0.viver("APRENDE", "relapso", "longe_fixo", 101, 1)


# ------------------------------------------------------------------ as duas medidas novas (metrics.py)
def test_a_entropia_do_sorteio():
    r = met.entropia_do_sorteio([[1, 1], None, [1, 1, 1, 1], [1023, 1], None])
    h_baixa = -(1023 / 1024) * math.log2(1023 / 1024) - (1 / 1024) * math.log2(1 / 1024)
    assert (r["n"], r["sorteios"], r["frac_sorteio"], r["limiar"]) == (5, 3, 0.6, 0.1) and h_baixa < 0.1
    assert r["media_bits"] == pytest.approx((1 + 2 + h_baixa) / 3) and r["frac_abaixo"] == pytest.approx(1 / 3)
    assert r["media_bits_decisao"] == pytest.approx((1 + 2 + h_baixa) / 5)
    assert met.entropia_do_sorteio([[3, 0, 1]])["media_bits"] == pytest.approx(met.entropia_bits([3, 1]))   # o peso 0 nao conta
    vazio = met.entropia_do_sorteio([None, None])
    assert vazio["media_bits"] is None and vazio["frac_abaixo"] is None and vazio["frac_sorteio"] == 0.0
    assert met.entropia_do_sorteio([])["frac_sorteio"] is None
    with pytest.raises(ValueError):
        met.entropia_do_sorteio([[5, 0]])


def test_o_credito_do_habito_por_linha():
    cs = [{"regra": "P2", "b": "dormir", "r_n": 0, "abs": 0}, {"regra": "P2", "b": "dormir", "r_n": 9, "abs": 2},
          {"regra": "P2", "b": "comer", "r_n": 90, "abs": 6}, {"regra": "P2-critico", "b": "comer", "r_n": 1, "pendente": True, "abs": 0}]
    r = met.credito_do_habito_por_linha(cs)
    assert (r["n"], r["abs"], r["linha"]) == (3, 8, "dormir") and r["por_linha"] == {"comer": {"n": 1, "abs": 6}, "dormir": {"n": 2, "abs": 2}}
    assert r["frac_n"] == pytest.approx(2 / 3) and r["frac_abs"] == 0.25
    assert met.credito_do_habito_por_linha(cs, "brincar")["frac_abs"] == 0.0
    nada = met.credito_do_habito_por_linha([])
    assert nada["frac_n"] is None and nada["frac_abs"] is None
    assert met.credito_do_habito_por_linha(cs[:1])["frac_abs"] is None            # ha credito, mas nenhum moveu o habito
    with pytest.raises(ValueError):
        met.credito_do_habito_por_linha([{"b": "comer"}])


def test_as_medidas_novas_entram_na_vida_do_e0():
    motor, registro, _ = E0.viver("hoje", "APRENDE", "relapso", "longe_fixo", 101, 2)
    m = E0.medir(2, motor, registro)
    assert 0.0 < m["entropia_bits"] and 0.0 <= m["entropia_frac_baixa"] <= 1.0 and 0.0 < m["frac_sorteio"] < 1.0
    assert 0.0 <= m["credito_dormir_n"] <= 1.0 and m["credito_abs"] == m["habito_abs"]     # sem corte no H, o credito e o habito
    motor, registro, _ = E0.viver("hoje", "CONGELADO", "relapso", "longe_fixo", 101, 2)
    m = E0.medir(2, motor, registro)
    assert m["credito_dormir"] is None and m["credito_dormir_n"] is None and m["entropia_bits"] > 0   # o CONGELADO nao credita


# ------------------------------------------------------------------ a analise e a leitura da secao 9.1
def _registros(d_critico: float, unidades=(1, 2, 3, 4, 5, 6)) -> list[dict]:
    out = []
    for u in unidades:
        ruido = (u % 3 - 1) / 1000
        for braco, d in (("HOJE", 0.0), ("CRITICO", d_critico), ("CONGELADO", 0.0)):
            for dono, lugar in C0.CELULAS:
                extra = ((u * 5) % 3 - 1) / 2000 if braco == "CRITICO" else 0.0
                crit = {"v_abs": 100, "fechadas": 50, "pendentes_no_fim": 1, "creditos_que_movem": 5, "delta_abs_medio": 9.0, "r_abs_medio": 8.0}
                out.append({"braco": braco, "semente": u, "dono": dono, "lugar": lugar, "tempo_bem": 0.5 + ruido + d + extra,
                            "aprendido_decidiu": 0.02, "credito_dormir": None if braco == "CONGELADO" else 0.1,
                            "credito_dormir_n": None if braco == "CONGELADO" else 0.5, "entropia_bits": 1.5, "entropia_frac_baixa": 0.0,
                            "saude_8_14": 0.8, "exaustao_8_14": 0.1, "habito_abs": 0 if braco == "CONGELADO" else 30,
                            "critico": crit if braco == "CRITICO" else None,
                            "vida_sha256": f"{'HOJE' if braco == 'CRITICO' and u == 1 else braco}|{u}|{dono}|{lugar}"})
    return out


@pytest.mark.parametrize("d, leitura, passa", [(0.0, C0.L_NADA, False), (0.05, C0.L_AUMENTA, True), (0.01, C0.L_AUMENTA, False),
                                               (-0.05, C0.L_FORA, False)])
def test_a_leitura_da_secao_9_1(d, leitura, passa):
    res = C0.analisar(_registros(d))
    assert res["leitura"]["leitura"] == leitura and res["leitura"]["segue"] == C0.SEGUE[leitura]
    assert res["leitura"]["corte_pq3_9"]["passa"] is passa and res["leitura"]["corte_pq3_9"]["delta"] == 0.032
    v = res["valor_do_aprendizado"]
    assert v["sem_o_critico"]["media"] == pytest.approx(0.0) and v["com_o_critico"]["media"] == pytest.approx(d, abs=1e-9)
    assert v["contraste"]["media"] == pytest.approx(d, abs=1e-9) and v["contraste"]["n"] == 6
    assert set(res["tempo_bem"]) == set(C0.BRACOS) and res["unidades"] == 6
    assert res["ao_lado"]["credito_dormir"] == {"HOJE": pytest.approx(0.1), "CRITICO": pytest.approx(0.1), "CONGELADO": None}
    assert res["ao_lado"]["entropia_bits"]["CRITICO"] == pytest.approx(1.5)
    assert res["o_critico_nas_vidas"] == {"vidas": 36, "vidas_iguais_as_de_hoje": 6, "v_abs_medio": 100.0, "creditos_que_movem": 180,
                                          "fechadas": 1800, "pendentes_no_fim": 36}
    assert res["critico"] == {"ligada": True, "eta_v": 64, "gamma": 960}


def test_a_analise_do_c0_falha_alto_e_a_leitura_sem_ic():
    rs = _registros(0.0)
    with pytest.raises(C0.C0Divergiu, match="vidas"):
        C0.analisar(rs[:-1])
    with pytest.raises(C0.C0Divergiu, match="repetida"):
        C0.analisar(rs + rs[:1])
    assert C0.analisar(_registros(0.05, unidades=(1,)))["leitura"]["leitura"] == C0.L_SEM_IC


# ------------------------------------------------------------------ a trava e a fumaca
def test_a_trava_do_c0():
    assert C0.BRACOS == ("HOJE", "CRITICO", "CONGELADO") and C0.CELULAS == E0.CELULAS and C0.N_VIDAS == 180
    assert C0.modo_da_config(FUMACA) == "fumaca" and C0.modo_da_config(RUN) == C0.FASE == "plasticidade_c0"
    e0_run = json.loads((RAIZ / "experiments/configs/v3_plasticidade_e0/run.json").read_text(encoding="utf-8"))
    assert RUN["unidades"] == e0_run["unidades"] and RUN["faixa"] == e0_run["faixa"] == [110001, 110200]   # as mesmas unidades do E0
    assert RUN["plano"] == C0.PLANO and "## 9. Adendo 1" in (RAIZ / C0.PLANO).read_text(encoding="utf-8")
    for errada in ({**RUN, "fase": "plasticidade_e0"}, {**RUN, "configs": ["hoje"]}, {**RUN, "dias": 7}, {**FUMACA, "dias": 15}):
        with pytest.raises(ValueError):
            C0.modo_da_config(errada)
    with pytest.raises(bv.SementeSemPlano):
        C0.modo_da_config({**RUN, "unidades": {**RUN["unidades"], "bases": RUN["unidades"]["bases"][:9]}})
    with pytest.raises(ValueError):
        E0.modo_da_config(RUN)                                                  # a config do C0 nao roda o E0
    with pytest.raises(ValueError, match="processos"):
        C0.rodar(FUMACA, Path("nao_usa"), 5)


def test_a_fumaca_do_c0(tmp_path):
    cfg = {**FUMACA, "dias": 2, "unidades": {**FUMACA["unidades"], "bases": [101, 202]}}
    r = C0.rodar(cfg, tmp_path / "f", 1)
    res, pasta = r["resultado"], tmp_path / "f"
    vidas = 2 * len(C0.BRACOS) * len(C0.CELULAS)
    assert res == {"modo": "fumaca", "fase": C0.FASE, "vidas": vidas, "bracos": list(C0.BRACOS), "conferencias": "passam"}
    for n in ("medidas.json", "custos.json", "resultado.json", "vidas.tar.gz", "meta.json"):
        assert (pasta / n).exists()
    assert not (pasta / "vidas").exists() and r["meta"]["pasta_crua_apagada"] == {"vidas": vidas}
    medidas = json.loads((pasta / "medidas.json").read_text(encoding="utf-8"))
    assert all("custo" not in m and (m["critico"] is not None) == (m["braco"] == "CRITICO") for m in medidas)
    assert all(m["habito_abs"] == 0 and m["credito_dormir"] is None for m in medidas if m["braco"] == "CONGELADO")
    assert all(m["critico"]["fechadas"] > 0 for m in medidas if m["braco"] == "CRITICO")
    assert r["meta"]["bracos"]["CRITICO"]["critico"] == {"ligada": True, "eta_v": 64, "gamma": 960} and r["meta"]["bracos"]["HOJE"]["critico"] is None
    assert r["meta"]["custo"]["vidas_da_run"] == 180
    analise = C0.analisar(medidas)                                             # de ponta a ponta; nenhuma medida da fumaca e lida
    assert analise["unidades"] == 2 and analise["leitura"]["leitura"] in C0.SEGUE and analise["o_critico_nas_vidas"]["vidas"] == 12
    with pytest.raises(FileExistsError):
        C0.rodar(cfg, pasta, 1)
    r2 = C0.rodar(cfg, tmp_path / "g", 1)
    for n in ("medidas.json", "resultado.json", "vidas.tar.gz"):
        assert r2["meta"]["artefatos_sha256"][n] == r["meta"]["artefatos_sha256"][n]
