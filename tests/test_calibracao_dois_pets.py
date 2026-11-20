"""A calibracao do K e o piloto dos dois pets (experiments/run_v2_calibracao_dois_pets.py; docs/PLANO_ANALISE_V2_DOIS_PETS.md, secoes
5, 6, 8 e 11), preparados sem rodar: so as sementes dos testes.

- a config da calibracao e a do plano (as bases 39101...39505, K_u = 4, o prefixo dois_pets, o `plano`), o ponto da K2 e o m da
  calibracao do mundo; a fumaca nas sementes dos testes; as recusas (a validacao, outras faixas, a queimada, fora da letra, a pasta que
  ja existe);
- o degrau 1 cabe no teto de pesos (990 < 1000) com a montagem completa e a rota do humor, em todo pet de todo braco;
- a taxa agregada e o bootstrap sobre as unidades, a regra do K, a margem e o contraste por unidade em dados com a resposta conhecida;
- a fumaca inteira (a etapa K para pela exposicao nas sementes dos testes) e o piloto direto num K da grade: o A do B + Ainf ate o dia K
  e o A-so, e a rota do humor credita a fruta ruim no A com os canais.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v2_calibracao_dois_pets as cd  # noqa: E402
from digilab.metrics import bootstrap_taxa_agregada, taxa_agregada  # noqa: E402

CONFIGS = RAIZ / "experiments" / "configs" / "v2_dois_pets"


def _cfg(nome: str = "calibracao") -> dict:
    return json.loads((CONFIGS / f"{nome}.json").read_text(encoding="utf-8"))


# ================================================================== a config
def test_a_config_da_calibracao_e_a_do_plano():
    c = _cfg()
    assert cd.modo_da_config(c) == "calibracao"
    assert c["plano"] == cd.PLANO and (RAIZ / c["plano"]).is_file()
    assert c["unidades"] == {"bases": [39101, 39202, 39303, 39404, 39505], "k": 4, "prefixo": "dois_pets"}
    assert (c["dono"], c["lugar"], c["orcamento_por_dia"]) == ("atencioso", "comedouro", 16)
    assert c["calibracao_k"] == {"grade_k": [3, 5, 7], "dias_a": 10, "janelas": "dois_dias"}     # adendo 1.1 (PDC-1)
    assert "adendo 1.1" in c["adendo_janelas"] and "### 1.1" in (RAIZ / c["plano"]).read_text(encoding="utf-8")
    assert c["piloto"] == {"bracos": ["B-so", "B+Ainf", "B+Aemb", "B+Aing"], "dias_b": 14}
    assert c["montagem"] == "completa" and c["ponto"] == "T3"
    assert len(bv.unidades_derivadas(c["unidades"]["bases"], c["unidades"]["k"], "dois_pets")) == 20
    # a config de cada etapa passa pela checagem da bancada do grupo (o plano e a montagem completa fora das sementes dos testes)
    cd.config_grupo(c, ["A-so"], 0, 10)
    cd.config_grupo(c, list(cd.BRACOS_PILOTO), 3, 14)


def test_o_ponto_e_o_da_k2_e_o_mundo_e_o_da_calibracao_do_mundo():
    c = _cfg()
    k2 = json.loads((RAIZ / "artifacts_v2_calibracao_conjunta" / "escolha.json").read_text(encoding="utf-8"))["ponto"]
    assert c["lobos"] == {"memoria_ganho": k2["g"], "w0_pedido": k2["w0_pedido"], "w0_info": k2["w0_info"]}
    assert c["consequencia"] == {"ganho": k2["ganho"], "canais_ligados": True}
    mundo = json.loads((RAIZ / "artifacts_v2_mundo" / "calibracao" / "resultado.json").read_text(encoding="utf-8"))
    assert c["mundo"] == {"mult_queda": mundo["m_escolhido"]}


def test_a_fumaca_e_a_mesma_config_nas_sementes_dos_testes():
    c, f = _cfg(), _cfg("fumaca_calibracao")
    assert cd.modo_da_config(f) == "fumaca"
    assert set(f["unidades"]["bases"]) <= bv.SEMENTES_TESTE and "plano" not in f
    assert {k: v for k, v in f.items() if k not in ("descricao", "plano", "unidades")} == \
        {k: v for k, v in c.items() if k not in ("descricao", "plano", "unidades")}


def test_as_recusas():
    c = _cfg()
    for bases in ([40101, 40202, 40303, 40404, 40505], [39101], [31101, 31202, 31303, 31404, 31505]):
        with pytest.raises(bv.SementeSemPlano):
            cd.modo_da_config({**c, "unidades": {**c["unidades"], "bases": bases}})
    for troca in ({"plano": None}, {"unidades": {**c["unidades"], "k": 3}}, {"montagem": "simples"},
                  {"margem": {"distancia_minima": 0.1}}, {"calibracao_k": {**c["calibracao_k"], "grade_k": [3, 5]}},
                  {"adendo_janelas": None}, {"bootstrap": {**c["bootstrap"], "semente": 1}}):
        with pytest.raises(ValueError, match="a letra"):
            cd.modo_da_config({**c, **troca})
    cd.modo_da_config({**c, "calibracao_k": {**c["calibracao_k"], "janelas": "dois_dias"}, "adendo_janelas": "adendo 1"})
    for ruim in ({"taxa": {"modo": "media", "n_minimo": 20}}, {"taxa": {"modo": "razao_das_somas", "n_minimo": 0}},
                 {"calibracao_k": {**c["calibracao_k"], "janelas": "tres"}}, {"piloto": {**c["piloto"], "bracos": ["B-so"]}},
                 {"extra": 1}):
        with pytest.raises(ValueError):
            cd.modo_da_config({**c, **ruim})
    with pytest.raises(bv.SementeSemPlano, match="queimada"):          # a faixa queimada, pela bancada do grupo
        cd.config_grupo({**_cfg("fumaca_calibracao"), "unidades": {"bases": [15101], "k": 1, "prefixo": "dois_pets"}}, ["A-so"], 0, 10)


def test_a_run_recusa_a_pasta_que_existe(tmp_path):
    with pytest.raises(FileExistsError):
        cd.rodar(_cfg("fumaca_calibracao"), tmp_path)


# ================================================================== o teto de pesos
def test_o_degrau_1_cabe_no_teto_com_a_montagem_completa_e_a_rota_do_humor():
    t = cd.teto_dos_pesos(_cfg())
    assert set(t) == {"A-so/A", "B-so/B", "B+Ainf/A", "B+Ainf/B", "B+Aemb/A", "B+Aemb/B", "B+Aing/A", "B+Aing/B"}
    for nome, v in t.items():
        assert v["pesos"] == 990 and v["teto"] == 1000 and v["cabe"], nome
        assert v["alvo_aprendido"] and v["entradas_sociais"] and v["modelo_outros"] and v["presenca_fruta_mundo"], nome
        assert not v["memoria"], nome                                    # a memoria so existe nos mundos das frutas
        assert v["canais"] == (v["braco_pet"] == "P1") == v["aprende"], nome   # o ingenuo e P0: sem canais e sem aprender


# ================================================================== a taxa agregada (metrics)
def test_a_taxa_agregada_e_o_bootstrap_sobre_as_unidades():
    c = [(2, 1), (0, 0), (4, 0)]
    assert taxa_agregada(c, "razao_das_somas") == {"taxa": 1 / 6, "n": 6, "unidades": 3, "unidades_com_valor": 2,
                                                    "modo": "razao_das_somas"}
    assert taxa_agregada(c, "media_das_unidades")["taxa"] == 0.25
    assert taxa_agregada([(0, 0), (0, 0)], "razao_das_somas")["taxa"] is None
    for ruim in ([(1, 2)], [(-1, 0)], [(1.0, 0)]):
        with pytest.raises(ValueError):
            taxa_agregada(ruim, "razao_das_somas")
    with pytest.raises(ValueError, match="modo"):
        taxa_agregada(c, "mediana")
    b = bootstrap_taxa_agregada([(4, 2)] * 6, "razao_das_somas", 500, 4242)
    assert b["ic"] == {"ic_inferior": 0.5, "ic_superior": 0.5, "nivel": 0.95}       # unidades iguais: o IC e o ponto
    assert b == bootstrap_taxa_agregada([(4, 2)] * 6, "razao_das_somas", 500, 4242)  # deterministico
    b = bootstrap_taxa_agregada([(1, 1)] + [(0, 0)] * 9, "razao_das_somas", 500, 4242)
    assert b["ic"] is None and b["reamostras_sem_valor"] > 0                         # nao descarta reamostra em silencio


# ================================================================== a regra do K, a margem e o contraste (dados com a resposta conhecida)
def _medida_a(por_dia: dict[int, tuple[int, int]], dias: int = 10) -> dict:
    t = {f"dia_{d}": {"n": por_dia.get(d, (0, 0))[0], "ruins": por_dia.get(d, (0, 0))[1]} for d in range(1, dias + 1)}
    return {"pets": {"A": {"taxa_fruta_ruim": t}}}


BOOT = {"reamostragens": 2000, "semente": 4242, "nivel": 0.95}
TAXA = {"modo": "razao_das_somas", "n_minimo": 20}


def test_a_regra_do_k_pega_o_menor_que_passa():
    # dia 1: tudo ruim (R = 1, limiar 0,5); dia 3: metade (IC encosta no limiar, nao passa); dia 5 e 7: nada ruim (passa)
    medidas = [_medida_a({1: (2, 2), 3: (2, 1), 5: (2, 0), 7: (2, 0)}) for _ in range(20)]
    r = cd.regra_k(medidas, [3, 5, 7], TAXA, BOOT)
    assert r["r_a_dia_1"]["taxa"] == 1.0 and r["k"] == 5 and r["fechou"]
    assert [r["por_k"][k]["leitura"] for k in ("3", "5", "7")] == ["nao aprendeu", "aprendeu", "aprendeu"]
    assert r["por_k"]["3"]["r_a_dia_k"]["ic"]["ic_superior"] == 0.5 and r["por_k"]["3"]["limiar"] == 0.5


def test_a_regra_do_k_le_exposicao_baixa_e_para():
    medidas = [_medida_a({1: (1, 1), 3: (1, 0), 5: (1, 0), 7: (1, 0)}) for _ in range(10)]   # 10 consumos por janela, n_minimo 20
    r = cd.regra_k(medidas, [3, 5, 7], TAXA, BOOT)
    assert r["k"] is None and not r["fechou"] and r["so_exposicao_baixa"]
    assert all(v["leitura"] == "exposicao baixa" for v in r["por_k"].values())
    assert cd.regra_k(medidas, [3, 5, 7], {**TAXA, "n_minimo": 10}, BOOT)["k"] == 3


def test_as_janelas_de_dois_dias_somam_os_dias():
    medidas = [_medida_a({1: (1, 1), 2: (1, 1), 4: (1, 0), 5: (1, 0)}) for _ in range(10)]
    r = cd.regra_k(medidas, [3, 5, 7], TAXA, BOOT, janelas="dois_dias")
    assert r["dias_inicio"] == ["dia_1", "dia_2"] and r["r_a_dia_1"]["n"] == 20
    assert r["por_k"]["5"]["dias"] == ["dia_4", "dia_5"] and r["k"] == 5


def _medida_grupo(braco: str, semente: int, b: tuple[int, int] | None = None, a: dict | None = None) -> dict:
    pets = {}
    if b is not None:
        pets["B"] = {"taxa_fruta_ruim": {"primeiros_7": {"n": b[0], "ruins": b[1], "taxa": b[1] / b[0] if b[0] else None}}}
    if a is not None:
        pets["A"] = {"taxa_fruta_ruim": {f"dia_{d}": {"n": n, "ruins": r} for d, (n, r) in a.items()}}
    return {"braco": braco, "semente": semente, "pets": pets}


def test_a_janela_do_a_na_margem():
    assert cd.janela_ra(3) == ["dia_1", "dia_2", "dia_3"]
    assert cd.janela_ra(7) == [f"dia_{d}" for d in range(1, 8)]
    assert cd.janela_ra(9) == [f"dia_{d}" for d in range(3, 10)]


def test_a_margem_e_a_distancia_minima():
    a = {d: (2, 0) for d in range(1, 18)}
    regs = [_medida_grupo("B-so", s, b=(4, 2)) for s in range(5)] + [_medida_grupo("B+Ainf", s, b=(4, 1), a=a) for s in range(5)]
    m = cd.margem(regs, 3, TAXA, 0.05)
    assert m["distancia"] == 0.5 and m["delta_s"] == 0.25 and m["valida"]
    a = {d: (2, 1) for d in range(1, 18)}
    regs = [_medida_grupo("B-so", s, b=(10, 5)) for s in range(5)] + [_medida_grupo("B+Ainf", s, b=(4, 1), a=a) for s in range(5)]
    m = cd.margem(regs, 3, TAXA, 0.05)
    assert m["distancia"] == 0.0 and not m["valida"] and "volta ao Matheus" in m["leitura"]


def test_o_contraste_por_unidade_tira_a_unidade_sem_consumo_e_conta():
    regs = [_medida_grupo("B+Aemb", 1, b=(4, 2)), _medida_grupo("B+Ainf", 1, b=(4, 1)),
            _medida_grupo("B+Aemb", 2, b=(0, 0)), _medida_grupo("B+Ainf", 2, b=(4, 1))]
    r = cd.por_unidade_rb(regs, "B+Aemb", "B+Ainf")
    assert r == {"difs": {1: 0.25}, "sem_consumo": [2]}
    with pytest.raises(RuntimeError, match="falta"):
        cd.por_unidade_rb(regs[:3], "B+Aemb", "B+Ainf")


# ================================================================== a fumaca e o piloto, nas sementes dos testes
def test_a_fumaca_inteira_para_na_etapa_k(tmp_path):
    """Nas sementes dos testes (5 unidades) o A sozinho come pouca fruta madura por dia: a regra le exposicao baixa e para sem piloto.
    O que se confere aqui e o encanamento: os A-so gravados e rejogados do disco, o k.json, o meta com os sha256 da secao 11."""
    pasta = tmp_path / "fumaca"
    r = cd.rodar(_cfg("fumaca_calibracao"), pasta)
    assert (pasta / "k.json").is_file() and (pasta / "resultado.json").is_file() and (pasta / "k" / "medidas.json").is_file()
    assert len(list((pasta / "k" / "grupos").glob("*.jsonl"))) == 5
    meta = json.loads((pasta / "meta.json").read_text(encoding="utf-8"))
    assert set(meta["sha256"]) == {"mundo.py", "grupo.py", "lobos.py", "config.py", "engine.py"}
    assert meta["modo"] == "fumaca" and set(meta["teto_dos_pesos"]) >= {"B+Ainf/A", "B+Ainf/B"}
    res = r["resultado"]
    assert res["k"] is None and res["g_k"]["so_exposicao_baixa"] and "exposicao" in res["leitura"]
    assert "margem" not in res and res["custo"]["por_braco"]["A-so"]["grupos"] == 5


def test_o_piloto_num_k_da_grade(tmp_path):
    """O piloto de uma unidade no K = 3: os quatro bracos gravados, rejogados e medidos; o A do B + Ainf ate o dia K e o A-so da etapa K
    (conferido dentro da tarefa). A unidade da base 202 tem o A comendo a fruta ruim com os canais: a rota do humor (#269) credita o peso
    da presenca dela, sem falhar."""
    cfg = _cfg("fumaca_calibracao")
    u = bv.unidades_derivadas([202], 1, "dois_pets")[0]
    cd.tarefa_k(cfg, u, str(tmp_path / "k"))
    out = cd.tarefa_piloto(cfg, 3, u, str(tmp_path / "p"), str(tmp_path / "k"))
    assert sorted(m["braco"] for m, _ in out.values()) == sorted(cd.BRACOS_PILOTO)
    assert len(list((tmp_path / "p" / "grupos").glob("*.jsonl"))) == 4
    for med, _ in out.values():
        assert med["k"] == 3 and med["pets"]["B"]["dias_vividos"] == 14
    b = cd.bancada_da_etapa(cd.config_grupo(cfg, list(cd.BRACOS_PILOTO), 3, 14))
    v = b.grupo(bv.EspecGrupo("B+Ainf", u["semente"], 3))
    ruim = b.efeitos_do_grupo(v.espec)["ruim"]
    a = v.grupo.motores["A"]
    comeu = [c for c in a.consumos_mundo if c["tipo"] == ruim and c["situacao"] == "madura"]
    cerebro = bv.do_braco(a.politica).cerebro
    assert comeu and b.bancada_grupo().canais_no_pet(b.espec_do_pet(v.espec, "A"))
    assert cerebro._pesos_comer_fruta[ruim] != 0


def test_o_a_do_piloto_tem_de_ser_o_a_so(tmp_path):
    cfg = _cfg("fumaca_calibracao")
    u = bv.unidades_derivadas([101], 1, "dois_pets")[0]
    cd.tarefa_k(cfg, u, str(tmp_path / "k"))
    (arq,) = (tmp_path / "k" / "grupos").glob("*.jsonl")
    arq.write_text(arq.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    with pytest.raises(bv.ReplayDivergiu, match="A-so"):
        cd.tarefa_piloto(cfg, 3, u, str(tmp_path / "p"), str(tmp_path / "k"))
