"""CONVERSA_PET, F2: o resumo da espera (experiments/resumo_espera_f2.py), com dados falsos. Falha alto em campo faltando."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))

import resumo_espera_f2 as r  # noqa: E402
from digilab.metrics import ic_wilson, quantis  # noqa: E402


def reg(situacao="conversa", envio=0.0, chamada=0.0, balao=1000.0, verif=2000.0, descartada=False, conversa=2, turno=1, fria=False, erro=None):
    conv = situacao == "conversa"
    return {"situacao": situacao, "t_envio": envio, "t_chamada": chamada, "t_primeira": balao, "t_balao": balao, "t_verif": verif,
            "descartada": descartada, "rede": True if conv else None, "modelo": "falso", "erro": erro, "latencia_s": 1.0,
            "conversa": conversa if conv else None, "turno": turno if conv else None, "fria": fria if conv else None}


def test_medidas_t1_a_t4():
    regs = [reg(envio=100.0, chamada=600.0, balao=3100.0, verif=4100.0)]
    assert r.valores_da_medida(regs, "T1") == [3.0]
    assert r.valores_da_medida(regs, "T2") == [3.0]          # T2 = T1 hoje
    assert r.valores_da_medida(regs, "T3") == [1.0]
    assert r.valores_da_medida(regs, "T4") == [0.5]


def test_sem_verificacao_fica_fora_do_t3_e_espontanea_fora_dos_t():
    regs = [reg(verif=None), reg(situacao="espontanea")]
    assert r.valores_da_medida(regs, "T3") == []
    assert r.valores_da_medida(regs, "T1") == [1.0]


def test_quantis_e_curva_pelo_posto_mais_proximo():
    vals = [float(i) for i in range(1, 121)]                 # 1..120 s
    res = r.resumo_de(vals)
    assert res["n"] == 120
    assert (res["p50"], res["p95"]) == tuple(quantis(vals, [0.5, 0.95]))
    assert res["p95"] == 114.0 and res["p95_vizinhos"] == [113.0, 115.0]   # o 114.o de 120, como no plano
    assert res["acima"]["2"]["k"] == 118 and res["acima"]["8"]["k"] == 112
    assert res["acima"]["8"]["ic95"] == ic_wilson(112, 120)
    assert res["acima_L"] is res["acima"]["8"]


def test_espontaneas_descartadas():
    regs = [reg(situacao="espontanea", descartada=True, balao=None, verif=None, chamada=None),
            reg(situacao="espontanea", balao=4000.0), reg(situacao="espontanea", balao=2000.0)]
    e = r.espontaneas(regs)
    assert (e["disparadas"], e["descartadas"]) == (3, 1)
    assert e["fracao_descartada"] == pytest.approx(1 / 3)
    assert e["ic95"] == ic_wilson(1, 3)
    assert e["pedido_balao_s"]["n"] == 2


def test_fria_separada_da_quente():
    regs = [reg(conversa=1, fria=True, balao=30000.0, verif=31000.0), reg(conversa=2, balao=1000.0), reg(conversa=3, balao=2000.0, verif=3000.0)]
    res = r.resumir(regs)
    assert res["fria"]["T1"]["n"] == 1 and res["fria"]["T1"]["p50"] == 30.0
    assert res["quente"]["T1"]["n"] == 2 and res["quente"]["T1"]["p95"] == 2.0


def test_campo_faltando_levanta(tmp_path):
    ok = reg()
    quebrado = dict(ok)
    del quebrado["t_balao"]
    p = tmp_path / "turnos.jsonl"
    p.write_text(json.dumps(ok) + "\n" + json.dumps(quebrado) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="t_balao"):
        r.ler_turnos(p)


def test_arquivo_vazio_json_ruim_e_tempo_negativo_levantam(tmp_path):
    p = tmp_path / "turnos.jsonl"
    p.write_text("\n", encoding="utf-8")
    with pytest.raises(ValueError, match="sem nenhuma linha"):
        r.ler_turnos(p)
    p.write_text("{nao e json\n", encoding="utf-8")
    with pytest.raises(ValueError, match="nao e JSON"):
        r.ler_turnos(p)
    with pytest.raises(ValueError, match="negativo"):
        r.valores_da_medida([reg(envio=5000.0, balao=1000.0)], "T1")
    with pytest.raises(ValueError, match="sem numero de conversa"):
        r.resumir([reg(conversa=None)])


def test_ler_e_resumir_de_ponta_a_ponta(tmp_path):
    p = tmp_path / "turnos.jsonl"
    p.write_text("\n".join(json.dumps(reg(conversa=1 + i // 6, fria=i < 6, balao=1000.0 * (i + 1), verif=1000.0 * (i + 2))) for i in range(12)) + "\n", encoding="utf-8")
    res = r.resumir(r.ler_turnos(p))
    assert res["n_conversas_turnos"] == 12 and res["quente"]["T1"]["n"] == 6 and res["fria"]["T1"]["n"] == 6


def test_conversa_fora_da_voz_da_rede_falha_alto():
    """F2, o risco do pet sem decisao do modular: a conversa que nao saiu pela rede nao e a medida desenhada"""
    x = reg()
    x["rede"] = False
    with pytest.raises(ValueError):
        r.resumir([x])


def test_decomposicao_divide_o_t1_quente():
    # a conversa 1 (fria) fica fora; a 2 sai 1 s antes de a verificacao repetida da 1 acabar (trava 1 s); a 3 sai com a trava livre
    a = {**reg(envio=0.0, chamada=0.0, balao=8000.0, verif=12000.0, fria=True, conversa=1), "latencia_s": 5.0}
    b = {**reg(envio=11000.0, chamada=11000.0, balao=19000.0, verif=23000.0), "latencia_s": 2.0}
    c = {**reg(envio=30000.0, chamada=30000.0, balao=36000.0, verif=40000.0), "latencia_s": 2.5}
    d = r.decomposicao([a, b, c])
    assert d["n"] == 2 and d["turnos_com_trava"] == 1
    assert sorted([d["trava"]["p50"], d["trava"]["p95"]]) == [0.0, 1.0]
    # b: 8 s ate o balao = 2 de geracao + 1 de trava + 5 de resto; c: 6 = 2,5 + 0 + 3,5
    assert set(quantis(sorted([5.0, 3.5]), [0.5, 0.95])) == {d["resto"]["p50"], d["resto"]["p95"]}


def test_decomposicao_falha_alto_sem_t_verif_anterior():
    a = reg(verif=None)
    with pytest.raises(ValueError):
        r.decomposicao([a, reg(chamada=5000.0, balao=6000.0)])
