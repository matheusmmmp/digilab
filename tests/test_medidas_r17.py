"""V2, W-MEDIDAS-R17 (docs/V2_RODADA_17.md): as medidas do mundo físico, do corpo e do banheiro em `digilab/metrics.py`, testadas em dados
sintéticos com a resposta conhecida. O motor do mundo e o corpo novo ainda não estão na main: as entradas são listas simples de eventos,
descritas no docstring de cada função.

Planos: docs/PLANO_ANALISE_V2_MUNDO_FISICO.md (seção 5.1 e adendo 1, A1.8), docs/PLANO_ANALISE_V2_CORPO_DRIVES.md (seção 5 e adendo 1)
e docs/PLANO_ANALISE_V2_BANHEIRO.md (seções 4 e 8).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.config import TICKS_POR_DIA  # noqa: E402
from digilab.metrics import (JANELA_8_14, alivios_ate_criterio, alivios_por_dia, contraste_distancia, cuidado_preservado,  # noqa: E402
                             curva_sobrevivencia, custo_viagem, deficit_fome_energia, dia_do_criterio, drives_novos,
                             inclinacao_generalizacao, inclinacao_permanencia, janela_dias, p_comer_so_fruta, permanencia_media,
                             taxa_no_abandono, taxa_recente, tempo_livre_be, variedade_recente, visitas_manchas)

D8 = 7 * TICKS_POR_DIA            # o primeiro tick do dia 8


def _visita(perm, censurada=False, **x):
    return {"arvore": "t", "inicio": 0, "fim": perm, "permanencia": perm, "censurada": censurada, **x}


# --- o mundo físico


def test_janela_dos_dias():
    assert janela_dias(8, 14) == JANELA_8_14 == (10080, 20160)
    assert janela_dias(1, 1) == (0, 1440)
    for a, b in ((0, 3), (5, 4)):
        with pytest.raises(ValueError):
            janela_dias(a, b)


def test_deficit_fome_energia():
    decisoes = [(0, 0.0, 0.0),                     # dia 1: fora
                (D8, 1.0, 1.0), (D8 + 15, 0.5, 0.7), (20159, 0.2, 0.0),
                (20160, 0.0, 0.0)]                  # dia 15: fora
    r = deficit_fome_energia(decisoes)
    assert r["n"] == 3 and r["d_fe"] == pytest.approx((0.0 + 0.4 + 0.9) / 3)
    assert deficit_fome_energia(decisoes, janela_dias(1, 14))["n"] == 4
    with pytest.raises(ValueError):
        deficit_fome_energia([(0, 0.5, 0.5)])                       # nada na janela
    with pytest.raises(ValueError):
        deficit_fome_energia([(D8, 1.2, 0.5)])                      # fora da escala


def test_custo_de_viagem():
    c = custo_viagem({"a": (0, 0), "b": (48, 64), "c": (208, 64)})
    assert c == {"a": 5.0, "b": 5.0, "c": 10.0}                     # 80 e 160 subunidades
    with pytest.raises(ValueError):
        custo_viagem({"a": (0, 0)})


def test_taxa_recente():
    quedas = [8639, 8640, 9000, 10079, 10080]
    assert taxa_recente(quedas, D8) == pytest.approx(3 / 24)        # [8640, 10080)
    assert taxa_recente(quedas, 100) is None                         # a janela comeca antes do nascimento


def test_visitas_as_manchas():
    arvores = {"t": (100, 100), "u": (900, 400)}
    traj = [(0, 0, 0),
            (10000, 100, 100), (10050, 0, 0),                        # comeca no dia 7: fora da janela
            (D8, 100, 100), (D8 + 15, 110, 100), (D8 + 30, 148, 100),  # d = 0, 10 e 48 (na borda, dentro)
            (D8 + 45, 149, 100),                                     # d = 49: sai
            (D8 + 60, 100, 130), (D8 + 75, 0, 0),                    # entra e sai na decisao seguinte
            (20200, 100, 100)]                                       # comeca depois da janela
    vs = visitas_manchas(traj, arvores, tick_fim=20500, quedas=[D8 - 1, D8 + 59])
    assert [(v["inicio"], v["fim"], v["permanencia"], v["decisoes_dentro"], v["censurada"]) for v in vs] == [
        (D8, D8 + 45, 45, 3, False), (D8 + 60, D8 + 75, 15, 1, False)]
    assert all(v["arvore"] == "t" and v["custo_viagem"] == 854 / 16 for v in vs)   # isqrt(800^2 + 300^2) = 854
    assert [v["taxa_recente"] for v in vs] == [1 / 24, 2 / 24]
    # a que nao termina ate o fim da vida sai censurada; a de uma entrada so no fim nao tem decisao dentro
    c = visitas_manchas([(0, 0, 0), (D8, 100, 100), (D8 + 15, 100, 101)], arvores, tick_fim=D8 + 100)
    assert [(v["permanencia"], v["censurada"], v["decisoes_dentro"]) for v in c] == [(100, True, 1)]
    assert visitas_manchas([(0, 0, 0), (D8, 100, 100)], arvores, tick_fim=D8 + 100) == []
    with pytest.raises(ValueError):
        visitas_manchas([(5, 0, 0), (5, 1, 1)], arvores, tick_fim=10)


def test_inclinacao_da_permanencia_pelo_layout():
    """Tres arvores: custo 10, 10 e 20 celulas; o pet fica 30, 30 e 60 minutos. A inclinacao e 3 min por celula."""
    arvores = {"a": (0, 240), "b": (160, 240), "c": (480, 240)}
    fora = (300, 400)
    traj = [(0, *fora), (D8, 0, 240), (D8 + 30, *fora), (D8 + 45, 160, 240), (D8 + 75, *fora), (D8 + 90, 480, 240),
            (D8 + 150, *fora)]
    vs = visitas_manchas(traj, arvores, tick_fim=20160)
    assert [(v["arvore"], v["custo_viagem"], v["permanencia"]) for v in vs] == [("a", 10.0, 30), ("b", 10.0, 30), ("c", 20.0, 60)]
    r = inclinacao_permanencia(vs, "custo_viagem")
    assert r["n"] == 3 and r["inclinacao"] == pytest.approx(3.0)


def test_inclinacoes_g_perm_e_g_oport():
    vs = [_visita(10, custo_viagem=1.0, taxa_recente=2.0), _visita(20, custo_viagem=2.0, taxa_recente=1.0),
          _visita(30, custo_viagem=3.0, taxa_recente=0.0), _visita(999, True, custo_viagem=9.0, taxa_recente=9.0),
          _visita(40, custo_viagem=4.0, taxa_recente=None)]
    g = inclinacao_permanencia(vs, "custo_viagem")
    assert (g["n"], g["censuradas"], g["inclinacao"]) == (4, 1, pytest.approx(10.0))
    o = inclinacao_permanencia(vs, "taxa_recente")
    assert (o["n"], o["sem_valor"], o["inclinacao"]) == (3, 1, pytest.approx(-10.0))   # dias ricos, sai antes
    um = inclinacao_permanencia([_visita(10, custo_viagem=1.0), _visita(20, custo_viagem=1.0)], "custo_viagem")
    assert um["inclinacao"] is None and um["motivo"]
    with pytest.raises(ValueError):
        inclinacao_permanencia(vs, "permanencia")


def test_taxa_no_abandono():
    vs = [{"inicio": 900, "fim": 1000, "permanencia": 100, "censurada": False},
          {"inicio": 1900, "fim": 2000, "permanencia": 100, "censurada": False},
          {"inicio": 2900, "fim": 3000, "permanencia": 100, "censurada": True}]
    ganhos = [(975, 0.05), (999, 0.05), (1000, 0.1), (1969, 1.0)]  # o do tick 1000 e o do 1969 ficam fora das janelas de 30 min
    r = taxa_no_abandono(vs, ganhos, horas_acordado=12.0)
    assert r["media_vida"] == pytest.approx(0.1)                    # 1,2 em 12 h
    assert r["razoes"] == [pytest.approx(2.0), 0.0] and r["razao_media"] == pytest.approx(1.0)
    assert taxa_no_abandono(vs, [], 12.0)["razao_media"] is None


def test_permanencia_media_e_g_dist():
    assert permanencia_media([_visita(10), _visita(30), _visita(500, True)]) == 20
    assert permanencia_media([_visita(500, True)]) is None
    assert contraste_distancia(60, 40, 35, 30) == 15                # o P1 fica 20 min a mais, o P0 so 5
    assert contraste_distancia(60, None, 35, 30) is None


# --- o corpo e os drives


def test_be_e_oc():
    decisoes = [(D8, "tempo_livre", "brincar"), (D8 + 15, "bola_no_cenario", "explorar"), (D8 + 30, "tempo_livre", "ocioso"),
                (D8 + 45, "tempo_livre", "chamar_atencao"), (D8 + 60, "tempo_livre", "comer"),
                (D8 + 75, "fome_urgente", "comer"),                  # fora do tempo livre
                (0, "tempo_livre", "brincar")]                       # fora da janela
    r = tempo_livre_be(decisoes)
    assert (r["n"], r["be"], r["oc"]) == (5, pytest.approx(0.4), pytest.approx(0.4))
    assert r["por_acao"]["comer"] == pytest.approx(0.2)
    assert tempo_livre_be([(D8, "sono", "dormir")])["be"] is None


def test_cuidado_preservado():
    d = [(D8, True, 0.5, 0.2), (D8 + 15, False, 0.9, 0.6), (D8 + 30, False, 1.0, 1.0), (D8 + 45, True, 0.6, 0.2), (0, True, 0.0, 0.0)]
    r = cuidado_preservado(d)
    assert (r["n"], r["privacao"], r["saude_media"], r["fome_media"]) == (4, 0.5, pytest.approx(0.75), pytest.approx(0.5))


def test_drives_novos():
    a = [(D8, True, {"tedio": 0.8, "solidao": 0.1, "estresse": 0.75}),
         (D8 + 15, True, {"tedio": 0.5, "solidao": 0.9, "estresse": 0.2}),
         (D8 + 30, False, {"tedio": 1.0, "solidao": 1.0, "estresse": 1.0})]   # dormindo: entra na media, nao na fracao
    r = drives_novos(a)
    assert (r["n"], r["n_acordado"]) == (3, 2)
    assert r["drives"]["tedio"]["media"] == pytest.approx(2.3 / 3)
    assert {k: v["fracao_acima"] for k, v in r["drives"].items()} == {"estresse": 0.5, "solidao": 0.5, "tedio": 0.5}
    with pytest.raises(ValueError):
        drives_novos([(D8, True, {"tedio": 0.5}), (D8 + 15, True, {"solidao": 0.5})])


def test_variedade_recente():
    atv = [(10000, "bola"), (10010, "bola"), (10020, "brincar"), (10030, "explorar"), (10040, "bola")]
    j = (0, 20160)
    assert variedade_recente(atv, [10030, D8], janela_tedio=8, janela=j)["media"] == pytest.approx(2.5)  # {bola, brincar}; +explorar
    assert variedade_recente(atv, [10030, D8], janela_tedio=2, janela=j)["media"] == pytest.approx(2.0)
    assert variedade_recente(atv, [10030, D8], janela_tedio=1, janela=j)["media"] == pytest.approx(1.0)
    assert variedade_recente(atv, [10030, D8])["n"] == 1                       # so a do dia 8 na janela padrao
    with pytest.raises(ValueError):
        variedade_recente([(1, "comer")], [5])


def test_p_comer_so_fruta():
    d = [(D8, ["a"], True), (D8 + 15, ["a"], False), (D8 + 30, ["a", "b"], True), (D8 + 45, ["b"], True)]
    r = p_comer_so_fruta(d, ["a", "b", "c"])
    assert r == {"a": {"n": 2, "p": 0.5}, "b": {"n": 1, "p": 1.0}, "c": {"n": 0, "p": None}}


def test_inclinacao_da_generalizacao():
    sem = {"a": 0.8, "b": 0.6, "c": 0.5}
    assert inclinacao_generalizacao(sem, {"a": 0.2, "b": 0.5, "c": 0.3}, "a")["inclinacao"] == pytest.approx(0.25)
    assert inclinacao_generalizacao(sem, {"a": 0.2, "b": 0.6, "c": 0.5}, "a")["inclinacao"] == pytest.approx(0.0)   # especifico
    assert inclinacao_generalizacao(sem, {"a": 0.2, "b": 0.0, "c": -0.1}, "a")["inclinacao"] == pytest.approx(1.0)  # generaliza
    falta = inclinacao_generalizacao({**sem, "c": None}, {"a": 0.2, "b": 0.5, "c": 0.3}, "a")
    assert falta["inclinacao"] == pytest.approx(0.1 / 0.6) and falta["faltam"] == 1
    nao_pegou = inclinacao_generalizacao(sem, {"a": 0.9, "b": 0.5, "c": 0.3}, "a")
    assert nao_pegou["indefinida"] and nao_pegou["inclinacao"] is None
    assert inclinacao_generalizacao({**sem, "a": None}, {"a": 0.2, "b": 0.5, "c": 0.3}, "a")["indefinida"]
    with pytest.raises(ValueError):
        inclinacao_generalizacao(sem, {"a": 0.2, "b": 0.5}, "a")


# --- o banheiro


def test_alivios_por_dia_e_acidentes():
    al = [(0, True, False), (100, False, True), (2880, True, False), (4319, True, True)]
    p = alivios_por_dia(al, dias=3)
    assert [(o["n"], o["no_banheiro"], o["fracao"], o["urgentes"], o["fracao_urgentes"]) for o in p] == [
        (2, 1, 0.5, 1, 0.5), (0, 0, None, 0, None), (2, 2, 1.0, 1, 0.5)]
    with pytest.raises(ValueError):
        alivios_por_dia([(4320, True, False)], dias=3)
    assert alivios_ate_criterio(p, 1) == 2 and alivios_ate_criterio(p, 2) == 2 and alivios_ate_criterio(p, None) == 4


def test_dia_do_criterio_com_censura():
    assert dia_do_criterio([0.5, 0.8, 0.9, 1.0, None, 1.0]) == {"dia": 2, "censurado": False, "tau": 5, "t_estrela": 2}
    assert dia_do_criterio([0.9, 0.9, None, 0.9, 0.9, 0.9, 0.5])["dia"] == 4              # o dia sem alivio quebra
    c = dia_do_criterio([0.9, 0.9, 0.7, 0.9, 0.9])                                         # so os dois ultimos: nao da
    assert c == {"dia": None, "censurado": True, "tau": 4, "t_estrela": 4}
    assert dia_do_criterio([0.0, 0.0, 0.0, 0.79, 0.8, 0.8, 0.8])["dia"] == 5
    with pytest.raises(ValueError):
        dia_do_criterio([0.9, 0.9])


def test_a_vida_inteira_ate_o_criterio():
    """14 dias, 4 alivios por dia: fora do banheiro ate o dia 4, 3 de 4 dentro nos dias 5 e 6, todos a partir do 7: o dia e o 7."""
    al = []
    for d in range(14):
        dentro = 0 if d < 4 else 3 if d < 6 else 4
        al += [(d * TICKS_POR_DIA + 60 * k, k < dentro, d < 2 and k == 0) for k in range(4)]
    p = alivios_por_dia(al, 14)
    c = dia_do_criterio([o["fracao"] for o in p])
    assert (c["dia"], c["tau"], c["t_estrela"]) == (7, 13, 7)
    assert alivios_ate_criterio(p, c["dia"]) == 28 and sum(o["urgentes"] for o in p) == 2


def test_curva_de_sobrevivencia_e_rmst():
    vidas = [{"dia": 1, "censurado": False, "tau": 5}, {"dia": 2, "censurado": False, "tau": 5},
             {"dia": 2, "censurado": False, "tau": 5}, {"dia": None, "censurado": True, "tau": 5}]
    r = curva_sobrevivencia(vidas)
    assert r["s"] == [1.0, 0.75, 0.25, 0.25, 0.25, 0.25]
    assert (r["mediana"], r["fracao_censurada"]) == (2, 0.25)
    assert r["rmst"] == pytest.approx((1 + 2 + 2 + 5) / 4)                                 # a media de T*
    muitas = curva_sobrevivencia([vidas[0]] + [vidas[3]] * 3)
    assert muitas["mediana"] is None
    with pytest.raises(ValueError):
        curva_sobrevivencia([vidas[0], {"dia": 1, "censurado": False, "tau": 6}])
