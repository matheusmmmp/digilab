"""BANCADA-EXPERIMENTO (docs/TAREFA_V2_BANCADA_EXPERIMENTO.md): faixas reservadas, o ponto T3 nomeado na bancada e o orquestrador do
experimento maior (docs/PLANO_ANALISE_V2_EXPERIMENTO_MAIOR.md, secoes 5 e 6). Gates: G1 de toda vida da fumaca; os contrastes e o Holm
em dados sinteticos com resposta conhecida; a fumaca recusa sementes de validacao sem plano. So as sementes dos testes."""

import json
import sys
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v2_experimento_maior as em  # noqa: E402
from digilab.config import CONFIG_LOBOS_APRENDIZ  # noqa: E402
from digilab.metrics import (bootstrap_ic, contraste_pareado, dentro_da_margem, holm, inclinacao_mmq,  # noqa: E402
                             t_unilateral, tamanho_amostra)

BOOT = {"reamostragens": 2000, "semente": 101, "nivel": 0.95}
LEITURAS = {"confirma", "refuta", "inconclusivo", "inconclusivo_por_duracao", "confirma_parcialmente", "nao_testavel"}


# ------------------------------------------------------------------ faixas reservadas


def test_faixas_novas_reservadas():
    for s, onde in ((18101, "revisao"), (18505, "revisao"), (19101, "N6"), (19505, "N6"), (20101, "N6"), (20505, "N6"),
                    (16101, "N11"), (17505, "N11")):
        fonte = bv.na_faixa_reservada(s)
        assert fonte and onde in fonte, (s, fonte)
    los = sorted((lo, hi) for lo, hi, _ in bv.FAIXAS_RESERVADAS)
    assert all(a[1] < b[0] for a, b in zip(los, los[1:]))                     # faixas disjuntas
    # as unidades derivadas do experimento maior continuam fora de toda faixa (o teste das frutas confere o resto)
    for u in bv.unidades_derivadas(bv.BASES_EXPERIMENTO_MAIOR["calibracao"] + bv.BASES_EXPERIMENTO_MAIOR["validacao"], 50):
        assert bv.na_faixa_reservada(u["semente"]) is None and bv.na_faixa_reservada(u["genoma"]) is None


# ------------------------------------------------------------------ o ponto do aprendiz


def test_ponto_t3_nomeado_sem_mudar_o_padrao():
    t3 = bv.cfg_lobos_do_ponto("T3")
    assert t3.teto == 16 * 2 ** CONFIG_LOBOS_APRENDIZ.bits_ponto_fixo == 16384
    assert replace(t3, teto=CONFIG_LOBOS_APRENDIZ.teto) == CONFIG_LOBOS_APRENDIZ          # so o teto muda (sem traco)
    assert bv.cfg_lobos_do_ponto() == bv.cfg_lobos_do_ponto("L1") == CONFIG_LOBOS_APRENDIZ
    assert bv.PONTO_PADRAO == "L1" and bv.PONTO_N5_EXPERIMENTO == "T3"
    base = {"dias": 2, "orcamento": 16}
    assert bv.bancada_da_config(base).cfg_lobos == CONFIG_LOBOS_APRENDIZ                  # sem "ponto": as runs antigas
    assert bv.bancada_da_config({**base, "ponto": "L1"}).cfg_lobos == CONFIG_LOBOS_APRENDIZ
    assert bv.bancada_da_config({**base, "ponto": "T3"}).cfg_lobos == t3
    # o T3 nomeado e o T3 da revisao do aprendiz (experiments/configs/v2_revisao/calibracao.json) sao o mesmo aprendiz
    rev = json.loads((RAIZ / "experiments/configs/v2_revisao/calibracao.json").read_text(encoding="utf-8"))
    assert bv.bancada_da_config({**base, **rev["pontos"]["T3"]}).cfg_lobos == t3
    # a chave "lobos" troca campos por cima do ponto
    c = bv.bancada_da_config({**base, "ponto": "T3", "lobos": {"w0_info": 512}}).cfg_lobos
    assert c.teto == 16384 and c.w0_info == 512
    cfg = {"bracos": ["P0"], "donos": ["atencioso"], "sementes": [101], "dias": 1, "orcamento": 16, "sonda": {}, "bootstrap": {},
           "ponto": "T9"}
    with pytest.raises(ValueError):
        bv.validar_config(cfg)
    with pytest.raises(ValueError):
        bv.cfg_lobos_do_ponto("T9")


# ------------------------------------------------------------------ estatistica com resposta conhecida


def test_t_de_student_e_holm_conhecidos():
    assert t_unilateral(2.0, 10) == pytest.approx(0.036694, abs=1e-6)                     # tabela da t
    assert t_unilateral(2.228, 10) == pytest.approx(0.025, abs=1e-4)
    assert t_unilateral(-1.0, 5) == pytest.approx(1 - t_unilateral(1.0, 5))
    # o exemplo classico: com alfa 0,05 e 4 hipoteses, rejeita so as duas menores
    h = holm({"a": 0.01, "b": 0.04, "c": 0.03, "d": 0.005}, 0.05)
    assert [k for k in sorted(h, key=lambda k: h[k]["ordem"])] == ["d", "a", "c", "b"]
    assert {k for k, v in h.items() if v["rejeita"]} == {"d", "a"}
    assert [h[k]["limiar"] for k in "dacb"] == pytest.approx([0.0125, 0.05 / 3, 0.025, 0.05])
    assert [h[k]["p_ajustado"] for k in "dacb"] == pytest.approx([0.02, 0.03, 0.06, 0.06])
    h = holm({"x": 0.001, "y": 0.04, "z": 0.012}, 0.05)
    assert [h[k]["rejeita"] for k in "xzy"] == [True, True, True]
    # parou na segunda (0,03 > 0,05/2): a terceira nao rejeita, embora 0,04 <= 0,05 (o limiar dela)
    h = holm({"x": 0.001, "y": 0.03, "z": 0.04}, 0.05)
    assert h["x"]["rejeita"] and not h["y"]["rejeita"] and not h["z"]["rejeita"] and h["z"]["limiar"] == 0.05
    # p None conta como 1: a familia nao encolhe
    h = holm({"x": 0.02, "y": None}, 0.05)
    assert h["x"]["limiar"] == 0.025 and h["x"]["rejeita"] and not h["y"]["rejeita"]
    with pytest.raises(ValueError):
        holm({}, 0.05)


def test_contraste_pareado_reamostra_as_sementes():
    # um valor por semente: as medias sao as do bootstrap_ic (mesma rng, mesma soma)
    vs = [0.3, -0.1, 0.2, 0.05, 0.4, 0.15]
    r = contraste_pareado({i: [v] for i, v in enumerate(vs)}, 2000, 7)
    ic = bootstrap_ic(vs, 2000, 7, 0.95)
    assert (r["ic95"]["ic_inferior"], r["ic95"]["ic_superior"]) == (ic["ic_inferior"], ic["ic_superior"])
    assert r["ic90"]["ic_inferior"] >= r["ic95"]["ic_inferior"] and r["ic90"]["ic_superior"] <= r["ic95"]["ic_superior"]
    assert r["t_pareado"]["gl"] == 5 and 0 < r["t_pareado"]["p_unilateral"] < 0.5
    # tudo positivo: p do bootstrap 0
    assert contraste_pareado({1: [0.1], 2: [0.2], 3: [0.3]}, 500, 1)["p_unilateral"] == 0.0
    # os valores de uma semente andam juntos: as medias possiveis sao so 1, -1 e (3 - 1) / 4 = 0,5
    r = contraste_pareado({"s1": [1.0, 1.0, 1.0], "s2": [-1.0]}, 2000, 3)
    assert r["n"] == 4 and r["n_grupos"] == 2 and r["media"] == 0.5
    assert {r["ic95"]["ic_inferior"], r["ic95"]["ic_superior"]} <= {1.0, -1.0, 0.5}
    # menos de 2 grupos: sem bootstrap, com o motivo
    r = contraste_pareado({"s": [0.1, 0.2]}, 500, 1)
    assert r["ic95"] is None and r["p_unilateral"] is None and r["motivo"]


def test_margem_inclinacao_e_tamanho():
    assert dentro_da_margem({"ic_inferior": -0.1, "ic_superior": 0.1}, 0.2)
    assert not dentro_da_margem({"ic_inferior": -0.1, "ic_superior": 0.2}, 0.2)                  # aberto na borda
    assert not dentro_da_margem(None, 0.2) and not dentro_da_margem({"ic_inferior": 0, "ic_superior": 0}, None)
    assert inclinacao_mmq([1, 2, 3, 4], [0.1, 0.3, 0.5, 0.7]) == pytest.approx(0.2)
    # ((z_{1-0,05/6} + z_0,8) * 0,2 / 0,1)^2 = 41,9 -> 42 -> 45 (multiplo de 5)
    assert tamanho_amostra(0.2, 0.1, 0.05 / 6, 0.8, 5) == 45
    assert tamanho_amostra(0.2, 0.1, 0.05 / 6, 0.8) == 42
    with pytest.raises(ValueError):
        tamanho_amostra(0.2, 0.0, 0.05, 0.8)


# ------------------------------------------------------------------ as leituras (secao 5), em contrastes montados a mao


def _c(lo95, hi95, lo90=None, hi90=None):
    return {"ic95": {"ic_inferior": lo95, "ic_superior": hi95}, "ic90": {"ic_inferior": lo90 if lo90 is not None else lo95,
                                                                           "ic_superior": hi90 if hi90 is not None else hi95}}


SIM, NAO = {"rejeita": True}, {"rejeita": False}


def test_leituras_por_predicao():
    d = 0.1
    assert em.leitura_positiva(_c(0.01, 0.3), SIM, d) == "confirma"
    assert em.leitura_positiva(_c(-0.3, -0.01), NAO, d) == "refuta"                       # IC 95% abaixo de 0
    assert em.leitura_positiva(_c(-0.2, 0.2, -0.05, 0.05), NAO, d) == "refuta"           # IC 90% dentro de (-d, +d)
    assert em.leitura_positiva(_c(-0.2, 0.2, -0.05, 0.05), NAO, d, refuta_por_equivalencia=False) == "inconclusivo"   # predicao 3
    assert em.leitura_positiva(_c(-0.2, 0.3, -0.15, 0.25), NAO, d) == "inconclusivo"
    # predicao 2
    assert em.leitura_p2({"descasado": "confirma", "mutavel": "confirma"}, {"descasado": False, "mutavel": False}, True) == "confirma"
    assert em.leitura_p2({"descasado": "confirma", "mutavel": "inconclusivo"}, {"descasado": False, "mutavel": False},
                         True) == "confirma_parcialmente"
    assert em.leitura_p2({"descasado": "confirma", "mutavel": "refuta"}, {"descasado": False, "mutavel": False}, True) == "refuta"
    assert em.leitura_p2({"descasado": "refuta", "mutavel": "inconclusivo"}, {"descasado": False, "mutavel": True},
                         True) == "inconclusivo_por_duracao"
    assert em.leitura_p2({"descasado": "inconclusivo", "mutavel": "inconclusivo"}, {"descasado": False, "mutavel": False},
                         True) == "inconclusivo"
    assert em.leitura_p2({"descasado": "confirma", "mutavel": "confirma"}, {"descasado": True, "mutavel": True}, False) == "nao_testavel"
    # predicao 4
    assert em.leitura_p4(_c(0.1, 0.2), SIM, _c(0.1, 0.2), SIM, d) == "confirma"
    assert em.leitura_p4(_c(0.1, 0.2), SIM, _c(-0.3, -0.1), NAO, d) == "refuta"             # piora e nao se recupera
    assert em.leitura_p4(_c(0.1, 0.2), SIM, _c(-0.2, 0.2, -0.05, 0.05), NAO, d) == "refuta"  # recupera so ate o P0
    assert em.leitura_p4(_c(-0.1, 0.2), NAO, _c(-0.3, -0.1), NAO, d) == "inconclusivo"     # sem a piora nao ha o que refutar
    # predicao 5 (equivalencia)
    assert em.leitura_equivalencia(_c(-0.15, 0.15, -0.05, 0.08), d) == "confirma"
    assert em.leitura_equivalencia(_c(0.12, 0.3), d) == "refuta"
    assert em.leitura_equivalencia(_c(-0.3, -0.11), d) == "refuta"
    assert em.leitura_equivalencia(_c(-0.05, 0.2, -0.02, 0.15), d) == "inconclusivo"
    assert em.leitura_equivalencia(_c(-0.01, 0.01), None) == "inconclusivo"


# ------------------------------------------------------------------ a analise inteira em medidas sinteticas


DIAS_SINT = 4


def _medida(braco, mundo, u, taxas, consumos=10, censurado=False, saude=0.9, fora=1.0, por_dia=None):
    tf = {j: {"taxa": t} for j, t in taxas.items()}
    for d in range(1, DIAS_SINT + 1):
        tf[f"dia_{d}"] = {"taxa": (por_dia or {}).get(d, taxas.get("final"))}
    return {"vida": f"{braco}~{mundo}@{u}", "braco": braco, "dono": "atencioso", "semente": 1000 + u, "genoma": 5000 + u,
            "mundo": mundo, "saude_media": saude, "fracao_fora_de_privacao": fora,
            "frutas": {"taxa_fruta_ruim": tf,
                       "consumos_ate_metade": {"consumos": consumos, "censurado": censurado, "sem_referencia": False}}}


def _sintetico(efeitos: dict, n: int = 10, falta: bool = False) -> tuple[dict, list[dict]]:
    """Medidas sinteticas com efeitos conhecidos: `efeitos[(braco, mundo)]` = (inicio, final, depois_da_troca, consumos), com um
    ruido pequeno e fixo por unidade (+-0,01) para o IC nao degenerar. Cada braco com dono tem o "so cuidado" igual ao P1."""
    unidades = [{"genoma": 5000 + u, "semente": 1000 + u, "base": None, "k": None} for u in range(n)]
    medidas = {}
    for u in range(n):
        r = 0.01 * ((u % 3) - 1)
        for (b, m), (ini, fin, dep, cons) in efeitos.items():
            taxas = {"inicio": ini + r, "final": fin + r, "depois_da_troca": dep + r if dep is not None else None}
            if falta and u == 0 and b == "P1" and m == "descasado":
                taxas["final"] = None                                                  # uma unidade sem consumo na janela
            medidas[f"{b}|{m}|{u}"] = _medida(b, m, u, taxas, cons + u % 2)
        for b in em.COM_DONO:
            for m in em.MUNDOS:
                ini, fin, dep, cons = efeitos[("P1", m)]
                taxas = {"inicio": ini + r, "final": fin + r, "depois_da_troca": dep + r if dep is not None else None}
                medidas[f"{b}aco|{m}|{u}"] = _medida(em.rotulo_so_cuidado(b), m, u, taxas, cons + u % 2)
    return medidas, unidades


def _efeitos(troca: dict | None = None):
    base = {
        ("P0", "casado_frutas"): (0.20, 0.20, None, 10), ("P1", "casado_frutas"): (0.40, 0.50, None, 10),
        ("P2", "casado_frutas"): (0.30, 0.30, None, 10), ("P2e", "casado_frutas"): (0.30, 0.30, None, 10),
        ("P3", "casado_frutas"): (0.20, 0.20, None, 10),
        ("P0", "descasado"): (0.60, 0.60, None, 30), ("P1", "descasado"): (0.40, 0.20, None, 20),
        ("P2", "descasado"): (0.30, 0.10, None, 8), ("P2e", "descasado"): (0.80, 0.30, None, 25),
        ("P3", "descasado"): (0.60, 0.61, None, 30),
        ("P0", "mutavel"): (0.20, 0.60, 0.60, 30), ("P1", "mutavel"): (0.30, 0.20, 0.20, 20),
        ("P2", "mutavel"): (0.30, 0.20, 0.20, 20), ("P2e", "mutavel"): (0.30, 0.20, 0.20, 20),
        ("P3", "mutavel"): (0.20, 0.60, 0.60, 30),
    }
    base.update(troca or {})
    return base


def test_analise_sintetica_tudo_confirma():
    medidas, unidades = _sintetico(_efeitos(), falta=True)
    a = em.analisar(medidas, unidades, {"dias": DIAS_SINT, "bootstrap": BOOT}, "fumaca", k2=True)
    assert a["delta"]["delta"] == pytest.approx(0.30, abs=0.005)                            # metade da taxa do P0 no descasado
    assert all(c["holm"]["rejeita"] for c in a["primarios"].values())
    assert {k: v["leitura"] for k, v in a["predicoes"].items()} == {"1": "confirma", "2": "confirma", "3": "confirma",
                                                                     "4": "confirma", "5": "confirma"}
    # a unidade sem consumo na janela nao some: entra em sem_valor do contraste que a usa
    assert len(a["primarios"]["p2_descasado"]["sem_valor"]) == 1 and a["primarios"]["p2_descasado"]["n"] == 9
    assert a["primarios"]["p1_casado"]["media"] == pytest.approx(0.30)
    # o P2 e o P2e diferem do proprio so cuidado (igual ao P1) e a saude e a mesma: ensino
    assert a["separacao_do_cuidado"]["p3_consumos"]["P2"]["leitura"] == "ensino"
    assert a["predicoes"]["5"]["k4"] is False and "aviso" in a["predicoes"]["5"]
    assert a["tamanho_amostra"]["n_validacao"] % 5 == 0


def test_analise_sintetica_refuta_e_nao_testavel():
    ef = _efeitos({("P1", "casado_frutas"): (0.10, 0.05, None, 10),         # a plasticidade melhora ate o casado: refuta a 1
                     ("P1", "descasado"): (0.80, 0.85, None, 20),             # o P1 come mais a ruim que o P0: refuta a 2
                     ("P3", "descasado"): (0.95, 0.99, None, 30)})            # P3 - P0 = +0,39 > delta: refuta a 5
    medidas, unidades = _sintetico(ef)
    a = em.analisar(medidas, unidades, {"dias": DIAS_SINT, "bootstrap": BOOT}, "fumaca", k2=True)
    p = {k: v["leitura"] for k, v in a["predicoes"].items()}
    assert p["1"] == "refuta" and p["2"] == "refuta" and p["5"] == "refuta"
    assert not a["primarios"]["p1_casado"]["holm"]["rejeita"]
    # sem o K2 a predicao 2 nao e testavel (e nao sai como refutada)
    a = em.analisar(medidas, unidades, {"dias": DIAS_SINT, "bootstrap": BOOT}, "fumaca", k2=False)
    assert a["predicoes"]["2"]["leitura"] == "nao_testavel"
    # delta dado (o do adendo) vale no lugar da regra
    a = em.analisar(medidas, unidades, {"dias": DIAS_SINT, "bootstrap": BOOT, "delta": 0.5}, "validacao", k2=True)
    assert a["delta"]["delta"] == 0.5 and a["status"] == "resultado" and a["predicoes"]["5"]["leitura"] == "confirma"


def test_analise_sintetica_inconclusivo_por_duracao():
    # P0 - P1 no fim em torno de zero (IC 90% dentro da margem: cada condicao, sozinha, refuta), mas a diferenca ainda cresce nos
    # ultimos dias: pela predicao 2 o resultado e inconclusivo por duracao, nao refutado
    ef = _efeitos({("P1", "descasado"): (0.60, 0.60, None, 20), ("P1", "mutavel"): (0.60, 0.60, 0.60, 20)})
    medidas, unidades = _sintetico(ef)
    for k, m in medidas.items():
        u = int(k.rsplit("|", 1)[1])
        if m["braco"] in ("P0", "P1") and m["mundo"] in ("descasado", "mutavel"):
            ruido = 0.3 * (1 if u % 2 else -1) * (1 if m["braco"] == "P0" else 0)
            m["frutas"]["taxa_fruta_ruim"]["final"]["taxa"] = 0.6 + ruido
            if m["frutas"]["taxa_fruta_ruim"]["depois_da_troca"]["taxa"] is not None:
                m["frutas"]["taxa_fruta_ruim"]["depois_da_troca"]["taxa"] = 0.6 + ruido
            for d in range(1, DIAS_SINT + 1):                                 # P0 - P1 = 0,05 * d (+ ruido por unidade)
                m["frutas"]["taxa_fruta_ruim"][f"dia_{d}"]["taxa"] = 0.5 + (0.05 * d + 0.002 * u if m["braco"] == "P0" else 0.0)
    a = em.analisar(medidas, unidades, {"dias": DIAS_SINT, "bootstrap": BOOT}, "fumaca", k2=True)
    p2 = a["predicoes"]["2"]
    assert p2["por_condicao"] == {"descasado": "refuta", "mutavel": "refuta"}
    assert p2["inclinacao_final"]["descasado"]["cresce"] and p2["leitura"] == "inconclusivo_por_duracao"
    assert p2["inclinacao_final"]["descasado"]["media"] == pytest.approx(0.05)


def test_cruzamento_das_curvas():
    serie = lambda vs: [{"dia": i + 1, "media": v, "n": 1} for i, v in enumerate(vs)]  # noqa: E731
    assert em.dia_do_cruzamento(serie([0.8, 0.6, 0.4, 0.3]), serie([0.5, 0.5, 0.5, 0.5])) == 3
    assert em.dia_do_cruzamento(serie([0.4, 0.3]), serie([0.5, 0.5])) is None               # nunca esteve acima
    assert em.dia_do_cruzamento(serie([0.8, None, 0.4]), serie([0.5, 0.5, 0.5])) == 3


# ------------------------------------------------------------------ modos e recusa de sementes


def _cfg(**kw):
    c = {"unidades": {"bases": [101, 202], "k": 1}, "dias": 4, "orcamento": 64, "sonda": {"estados": 5, "amostras": 5, "semente": 101}}
    c.update(kw)
    return c


def test_a_fumaca_recusa_sementes_de_validacao_sem_plano(tmp_path):
    assert em.modo_e_unidades(_cfg())[0] == "fumaca"
    val = list(bv.BASES_EXPERIMENTO_MAIOR["validacao"])
    with pytest.raises(bv.SementeSemPlano):
        em.modo_e_unidades(_cfg(unidades={"bases": val, "k": 1}))
    with pytest.raises(bv.SementeSemPlano):                                                 # nem com outro plano
        em.modo_e_unidades(_cfg(unidades={"bases": val, "k": 1}, plano="docs/PLANO_ANALISE_V2_N5.md"))
    with pytest.raises(bv.SementeSemPlano):                                                 # nem rodando
        em.rodar(_cfg(unidades={"bases": val, "k": 1}), tmp_path / "x")
    assert not (tmp_path / "x").exists()
    with pytest.raises(bv.SementeSemPlano):                                                 # misturar faixas
        em.modo_e_unidades(_cfg(unidades={"bases": [101, val[0]], "k": 1}))
    with pytest.raises(bv.SementeSemPlano):                                                 # faixa de outro experimento (N5)
        em.modo_e_unidades(_cfg(unidades={"bases": [12101], "k": 1}, plano=em.PLANO))
    com_plano = dict(unidades={"bases": val, "k": 2}, plano=em.PLANO, dias=14)
    with pytest.raises(ValueError):                                                         # validacao sem o delta do adendo
        em.modo_e_unidades(_cfg(**com_plano))
    assert em.modo_e_unidades(_cfg(**com_plano, delta=0.12))[0] == "validacao"
    with pytest.raises(ValueError):                                                         # a vida e de 14 dias (E5)
        em.modo_e_unidades(_cfg(**{**com_plano, "dias": 10}, delta=0.12))
    cal = dict(unidades={"bases": list(bv.BASES_EXPERIMENTO_MAIOR["calibracao"]), "k": 1}, plano=em.PLANO, dias=14)
    assert em.modo_e_unidades(_cfg(**cal))[0] == "calibracao"
    with pytest.raises(ValueError):                                                         # na calibracao o delta e medido
        em.modo_e_unidades(_cfg(**cal, delta=0.1))
    with pytest.raises(ValueError):                                                         # sem unidades derivadas, so a fumaca
        em.modo_e_unidades({**{k: v for k, v in _cfg(**cal).items() if k != "unidades"}, "sementes": [14101]})
    with pytest.raises(ValueError):
        em.modo_e_unidades(_cfg(donos=["relapso"]))
    with pytest.raises(ValueError):
        em.modo_e_unidades(_cfg(chave_estranha=1))


# ------------------------------------------------------------------ fumaca de ponta a ponta (G1)


def test_fumaca_do_experimento_maior(tmp_path):
    cfg = _cfg(ponto="T3", lobos={"w0_info": 512}, bootstrap={"reamostragens": 500, "semente": 101, "nivel": 0.95})
    r = em.rodar(cfg, tmp_path)
    n_u = 2
    # 5 bracos + 3 so cuidado, nos 3 mundos; e a referencia do padrao (P0, P1, P3)
    assert len(r["frutas"]["vidas"]) == n_u * (len(em.BRACOS) + len(em.COM_DONO)) * len(em.MUNDOS)
    assert len(r["padrao"]["vidas"]) == n_u * len(em.BRACOS_PADRAO)
    # G1: toda vida rejogada do disco bit a bit (a bancada ja confere ao gravar; aqui de novo, do arquivo)
    banc = bv.bancada_da_config(em.config_da_bancada(cfg, em.BRACOS, em.MUNDOS, []))
    for nome, v in r["frutas"]["vidas"].items():
        texto = (tmp_path / "frutas" / "vidas" / f"{nome}.jsonl").read_text(encoding="utf-8")
        banc.conferir_replay(v, texto)
    assert banc.cfg_lobos.teto == 16384 and banc.cfg_lobos.w0_info == 512
    meta = json.loads((tmp_path / "frutas" / "meta.json").read_text(encoding="utf-8"))
    assert meta["ponto"] == "T3" and meta["cfg_lobos"]["teto"] == 16384
    resumo = json.loads((tmp_path / "resumo.json").read_text(encoding="utf-8"))
    assert resumo["modo"] == "fumaca" and resumo["status"].startswith("piloto")
    assert set(resumo["predicoes"]) == {"1", "2", "3", "4", "5"}
    assert all(p["leitura"] in LEITURAS for p in resumo["predicoes"].values())
    assert resumo["contratos"] == {"K2_humor_da_fruta_no_P1": True, "K4_dono_julga_fruta": False}
    c = json.loads((tmp_path / "contrastes.json").read_text(encoding="utf-8"))
    assert set(c["primarios"]) == {x.nome for x in em.PRIMARIOS}
    assert sorted(x["holm"]["ordem"] for x in c["primarios"].values()) == list(range(1, 7))
    assert c["equivalencia"]["nome"] == "p5_equivalencia" and "holm" not in c["equivalencia"]
    # a informacao chega: o P2 e o P2e nao sao o P1 (o w0_info faz a escolha pender)
    regs = {nome: v.motor.log.para_jsonl() for nome, v in r["frutas"]["vidas"].items()}
    assert any(regs[n] != regs[n.replace("-P2~", "-P1~")] for n in regs if "-P2~" in n and "<" not in n)
    tabelas = json.loads((tmp_path / "frutas" / "tabelas.json").read_text(encoding="utf-8"))
    assert {"taxa_fruta_ruim_final", "consumos_ate_metade"} <= set(tabelas["atencioso"])
