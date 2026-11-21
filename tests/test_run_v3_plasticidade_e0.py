"""O E0 da PLASTICIDADE_EVOLUIDA (experiments/run_v3_plasticidade_e0.py; docs/TAREFA_V3_PLASTICIDADE_EVOLUIDA.md, secoes 2 e 3): a
montagem das 25 configs (um gene por vez, os limites da config), o braco CONGELADO com os termos em 0, a config de hoje no APRENDE igual
ao pet v38 de hoje byte a byte, o resumo do E0 no metrics.py, a leitura da secao 3, a trava da config (a faixa pendente) e uma fumaca nas
sementes dos testes."""
from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import fields, replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import pv2  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402
import run_v3_plasticidade_e0 as R  # noqa: E402
from digilab import metrics as met  # noqa: E402
from digilab.config import CONFIG_DIGIBRAIN_INATOS, ConfigDigibrainInatos, inatos_e1  # noqa: E402

FUMACA = json.loads((RAIZ / "experiments/configs/v3_plasticidade_e0/fumaca.json").read_text(encoding="utf-8"))
RUN = json.loads((RAIZ / "experiments/configs/v3_plasticidade_e0/run.json").read_text(encoding="utf-8"))
GENES_DA_TAREFA = ("eta_d", "eta_h", "h_max", "c_g", "g_max_incentivo", "g0", "w_pers", "w_mem", "w_lem",
                   "tau_hab", "epsilon", "lambda_sono")


def _sha(motor) -> str:
    return hashlib.sha256(motor.log.para_jsonl().encode("utf-8")).hexdigest()


# ------------------------------------------------------------------ as 25 configs
def test_os_genes_as_celulas_e_o_tamanho_sao_os_da_tarefa():
    assert R.GENES == GENES_DA_TAREFA and len(R.GENES) == 12 and R.DISPUTA == {"tau_hab", "epsilon", "lambda_sono"}
    inteiros = {f.name for f in fields(ConfigDigibrainInatos) if type(getattr(CONFIG_DIGIBRAIN_INATOS, f.name)) is int}
    assert set(R.GENES) <= inteiros
    assert R.CELULAS == tuple((d, lugar) for d in ("atencioso", "relapso") for lugar in ("comedouro", "longe", "longe_fixo"))
    assert R.BRACOS == ("APRENDE", "CONGELADO") and len(R.CONFIGS) == 25 and R.N_VIDAS == 3000
    assert R.INATOS_V38 == inatos_e1() and R.DIAS == 14 and R.N_BASES == 10


def test_cada_config_mexe_um_gene_so_na_metade_e_no_dobro():
    base = R.INATOS_V38
    assert list(R.CONFIGS)[0] == R.HOJE and R.CONFIGS[R.HOJE]["inatos"] == base
    vistos = set()
    for nome, c in R.CONFIGS.items():
        if nome == R.HOJE:
            continue
        diferentes = [f.name for f in fields(base) if getattr(base, f.name) != getattr(c["inatos"], f.name)]
        assert diferentes == [c["gene"]] and nome == f"{c['gene']}_{c['fator']}"
        hoje = getattr(base, c["gene"])
        assert c["valor_hoje"] == hoje and c["pedido"] == (hoje // 2 if c["fator"] == "metade" else hoje * 2)
        assert getattr(c["inatos"], c["gene"]) == c["valor"] and c["cortado"] == (c["valor"] != c["pedido"])
        vistos.add((c["gene"], c["fator"]))
    assert vistos == {(g, f) for g in R.GENES for f in R.FATORES}
    # com os valores de hoje nenhum gene bate num limite: as 24 configs sao a metade e o dobro exatos
    assert not any(c["cortado"] for c in R.CONFIGS.values())


def test_os_limites_sao_os_que_a_config_valida():
    base = R.INATOS_V38
    for gene in R.GENES:
        lo, hi = R.limites(gene, base)
        for limite, passo in ((lo, -1), (hi, 1)):
            if limite is None:
                continue
            replace(base, **{gene: limite})                                    # no limite, a config aceita
            with pytest.raises(ValueError):
                replace(base, **{gene: limite + passo})                        # um passo alem, recusa
    with pytest.raises(KeyError):
        R.limites("tau_v", base)


def test_o_corte_nos_limites_e_o_gene_que_nao_mexe():
    # o g_max colado no g0: a metade do g0 e cortada no g_min, e o dobro no g_max
    apertado = replace(R.INATOS_V38, g_min=768, g_max=1536)
    cs = R.montar_configs(apertado)
    assert (cs["g0_metade"]["pedido"], cs["g0_metade"]["valor"], cs["g0_metade"]["cortado"]) == (512, 768, True)
    assert (cs["g0_dobro"]["pedido"], cs["g0_dobro"]["valor"], cs["g0_dobro"]["cortado"]) == (2048, 1536, True)
    assert cs["tau_hab_metade"]["valor"] == 60 and not cs["tau_hab_metade"]["cortado"]
    assert R.montar_configs(replace(R.INATOS_V38, tau_hab=20))["tau_hab_metade"]["valor"] == 15
    # o limite deixa o gene no valor de hoje: falha alto, em vez de repetir a config de hoje em silencio
    with pytest.raises(R.GeneSemMexer, match="g0"):
        R.montar_configs(replace(R.INATOS_V38, g_min=1024))
    with pytest.raises(R.GeneSemMexer, match="tau_hab"):
        R.montar_configs(replace(R.INATOS_V38, tau_hab=15))


# ------------------------------------------------------------------ os bracos e o pet
def test_o_congelado_desliga_so_o_p1_e_o_p2():
    a, c = R.config_digibrain("APRENDE"), R.config_digibrain("CONGELADO")
    assert a == orq.config_do_braco("REL", None, True) and a.p1 and a.p2
    assert c == replace(a, p1=False, p2=False)
    with pytest.raises(ValueError):
        R.config_digibrain("M0")


@pytest.mark.parametrize("dono, lugar, semente", [("relapso", "longe_fixo", 101), ("atencioso", "comedouro", 202)])
def test_a_config_de_hoje_no_aprende_e_o_pet_v38_byte_a_byte(dono, lugar, semente):
    motor, registro, _ = R.viver("hoje", "APRENDE", dono, lugar, semente, 2)
    hoje, registro_hoje, _ = pv2.viver("HOJE", dono, lugar, semente, 2, v38=True)
    assert motor.log.para_jsonl() == hoje.log.para_jsonl() and registro.estados == registro_hoje.estados
    assert json.dumps(motor.politica.estado_interno(), sort_keys=True) == json.dumps(hoje.politica.estado_interno(), sort_keys=True)
    R.conferir_vida("hoje", "APRENDE", motor, registro)


def test_o_congelado_zera_os_termos_e_o_estado_do_aprendizado():
    motor, registro, fab = R.viver("hoje", "CONGELADO", "relapso", "longe_fixo", 101, 2)
    R.conferir_vida("hoje", "CONGELADO", motor, registro)
    c = orq.cerebro_de(registro)
    assert not c.cd.p1 and not c.cd.p2 and c.m.plast.desfecho_zero() and c.m.plast.habito_zero() and c.m.plast.creditos == 0
    assert all(u["termos"]["incentivo"] == 0 and u["termos"]["habito"] == 0 for m in c.motivos for u in m["unidades"])
    orq.conferir_replay(motor, fab, 101, motor.log.para_jsonl())
    m = R.medir(2, motor, registro)
    assert m["habito_abs"] == 0 and m["creditos_p2"] == 0 and 0.0 <= m["tempo_bem"] <= 1.0
    # o APRENDE das mesmas sementes aprende: o habito sai de 0
    motor_a, registro_a, _ = R.viver("hoje", "APRENDE", "relapso", "longe_fixo", 101, 2)
    assert R.medir(2, motor_a, registro_a)["habito_abs"] > 0 and not orq.cerebro_de(registro_a).m.plast.habito_zero()
    # a conferencia recusa o braco trocado e a config trocada
    with pytest.raises(R.E0Divergiu):
        R.conferir_vida("hoje", "CONGELADO", motor_a, registro_a)
    with pytest.raises(R.E0Divergiu):
        R.conferir_vida("eta_d_dobro", "APRENDE", motor_a, registro_a)


def test_o_gene_da_config_chega_ao_cerebro():
    motor, registro, _ = R.viver("lambda_sono_dobro", "APRENDE", "relapso", "longe_fixo", 101, 1)
    c = orq.cerebro_de(registro)
    assert c.inatos.lambda_sono == 2 * R.INATOS_V38.lambda_sono and c.inatos == R.CONFIGS["lambda_sono_dobro"]["inatos"]
    R.conferir_vida("lambda_sono_dobro", "APRENDE", motor, registro)
    hoje, registro_hoje, _ = R.viver("hoje", "APRENDE", "relapso", "longe_fixo", 101, 1)
    # o log sozinho nao distingue (so tem o dono e o tempo, e o dono simulado nao le o pet): a vida muda no estado de cada decisao
    assert _sha(motor) == _sha(hoje) and registro.estados != registro_hoje.estados
    assert R.assinatura_da_vida(motor, registro) != R.assinatura_da_vida(hoje, registro_hoje)


def test_os_tres_genes_do_g_apr_modulado_ficam_fora():
    """D-PE-7 (o Matheus, 2026-11-21: "Sim, tira os tres"): o pet v38 tem a `modula_g_apr` desligada, o g_apr e o g0, e o beta_e, o g_min
    e o g_max nao entram em conta nenhuma. Eles sairam da lista; o g0, que chega ao P1 e ao P2, fica"""
    assert not R.config_digibrain("APRENDE").modula_g_apr
    assert not {"beta_e", "g_min", "g_max"} & set(R.GENES) and "g0" in R.GENES
    assert not any(n.startswith(("beta_e", "g_min_", "g_max_metade", "g_max_dobro")) for n in R.CONFIGS)
    for gene in ("beta_e", "g_min", "g_max"):
        with pytest.raises(KeyError):
            R.limites(gene, R.INATOS_V38)
    hoje, registro_hoje, _ = R.viver("hoje", "APRENDE", "relapso", "longe_fixo", 101, 2)
    motor, registro, _ = R.viver("g0_dobro", "APRENDE", "relapso", "longe_fixo", 101, 2)
    assert registro.estados != registro_hoje.estados


# ------------------------------------------------------------------ a medida (metrics.py)
def test_a_saude_nas_decisoes():
    dec = [(0, 1.0), (15, 0.5), (30, 0.0)]
    assert met.saude_nas_decisoes(dec, (0, 30)) == {"n": 2, "media": 0.75}
    with pytest.raises(ValueError):
        met.saude_nas_decisoes(dec, (100, 200))
    with pytest.raises(ValueError):
        met.saude_nas_decisoes([(0, 1.5)], (0, 15))


def _valores():
    """4 unidades, 3 configs: `hoje`; `a`, que sobe o APRENDE em 0,10 e nao mexe no CONGELADO; `b`, igual a de hoje mais um ruido"""
    hoje_a = {1: 0.50, 2: 0.60, 3: 0.55, 4: 0.65}
    hoje_c = {1: 0.50, 2: 0.58, 3: 0.56, 4: 0.64}
    ruido = {1: 0.01, 2: -0.01, 3: 0.02, 4: -0.02}
    return {"hoje": {"APRENDE": hoje_a, "CONGELADO": hoje_c},
            "a": {"APRENDE": {u: v + 0.10 + ruido[u] / 10 for u, v in hoje_a.items()}, "CONGELADO": dict(hoje_c)},
            "b": {"APRENDE": {u: v + ruido[u] for u, v in hoje_a.items()}, "CONGELADO": {u: v - ruido[u] for u, v in hoje_c.items()}}}


def test_o_resumo_do_e0_pareia_por_unidade():
    r = met.sensibilidade_um_por_vez(_valores(), "hoje")
    assert r["referencia"] == "hoje" and r["unidades"] == 4 and set(r["configs"]) == {"hoje", "a", "b"}
    h, a, b = r["configs"]["hoje"], r["configs"]["a"], r["configs"]["b"]
    assert h["contraste_aprende"] is None and h["contraste_valor"] is None
    assert h["aprende"]["media"] == pytest.approx(0.575) and h["congelado"]["media"] == pytest.approx(0.57)
    assert h["valor"]["media"] == pytest.approx(0.005) and h["valor"]["fora_de_zero"] is False
    # o valor do aprendizado e a diferenca pareada, e o contraste do valor e a diferenca das diferencas
    assert a["valor"]["media"] == pytest.approx(0.105) and a["valor"]["fora_de_zero"] is True and a["valor"]["ic_inferior"] > 0
    assert a["contraste_aprende"]["media"] == pytest.approx(0.10) and a["contraste_aprende"]["fora_de_zero"] is True
    assert a["contraste_valor"]["media"] == pytest.approx(0.10) and a["contraste_valor"]["fora_de_zero"] is True
    ic = met.ic_t([0.10 + x / 10 for x in (0.01, -0.01, 0.02, -0.02)])
    assert a["contraste_aprende"]["ic_inferior"] == pytest.approx(ic["ic_inferior"]) and a["contraste_aprende"]["n"] == 4
    assert b["contraste_aprende"]["media"] == pytest.approx(0.0) and b["contraste_aprende"]["fora_de_zero"] is False
    assert b["contraste_valor"]["fora_de_zero"] is False
    assert r["acaso"] == {"contrastes_por_familia": 2, "nivel": 0.95, "esperados_por_acaso_por_familia": pytest.approx(0.1),
                          "fora_de_zero": {"contraste_aprende": 1, "contraste_valor": 1}}
    # com as 25 configs: 24 contrastes por familia e 1,2 esperado por acaso (o "1 ou 2" da secao 3)
    v = _valores()
    grande = {"hoje": v["hoje"], **{f"c{i}": v["b"] for i in range(24)}}
    assert met.sensibilidade_um_por_vez(grande, "hoje")["acaso"]["esperados_por_acaso_por_familia"] == pytest.approx(1.2)


def test_o_resumo_do_e0_falha_alto():
    v = _valores()
    with pytest.raises(ValueError, match="referencia"):
        met.sensibilidade_um_por_vez(v, "ontem")
    with pytest.raises(ValueError, match="bracos"):
        met.sensibilidade_um_por_vez({**v, "a": {"APRENDE": v["a"]["APRENDE"]}}, "hoje")
    faltando = {u: x for u, x in v["a"]["CONGELADO"].items() if u != 4}
    with pytest.raises(ValueError, match="unidades"):
        met.sensibilidade_um_por_vez({**v, "a": {"APRENDE": v["a"]["APRENDE"], "CONGELADO": faltando}}, "hoje")
    with pytest.raises(TypeError):
        met.sensibilidade_um_por_vez({**v, "a": {"APRENDE": v["a"]["APRENDE"], "CONGELADO": {**v["a"]["CONGELADO"], 4: None}}}, "hoje")
    # uma unidade so: sem IC, e o `fora_de_zero` fica None
    um = {n: {b: {1: x[1]} for b, x in bs.items()} for n, bs in v.items()}
    r = met.sensibilidade_um_por_vez(um, "hoje")
    assert r["configs"]["a"]["contraste_aprende"]["fora_de_zero"] is None and r["acaso"]["fora_de_zero"]["contraste_aprende"] == 0


# ------------------------------------------------------------------ a leitura da secao 3
def _registros(efeitos: dict, valor_base: float = 0.0, unidades=(1, 2, 3, 4, 5, 6)) -> list[dict]:
    """registros sinteticos das 25 configs: `efeitos[config]` = (o que soma ao APRENDE, o que soma ao CONGELADO); `valor_base`, o valor do
    aprendizado de toda config. Um ruido pequeno por unidade e config, igual nos dois bracos (o valor do aprendizado fica sem ruido)"""
    out = []
    for i, config in enumerate(R.CONFIGS):
        da, dc = efeitos.get(config, (0.0, 0.0))
        for u in unidades:
            ruido = ((u * 7 + i * 3) % 5 - 2) / 1000
            for braco, d in (("APRENDE", da + valor_base), ("CONGELADO", dc)):
                for dono, lugar in R.CELULAS:
                    extra = (u % 3 - 1) / 10000 if braco == "APRENDE" else 0.0      # media 0 nas 6 unidades
                    out.append({"config": config, "braco": braco, "semente": u, "dono": dono, "lugar": lugar,
                                "tempo_bem": 0.5 + ruido + d + extra, "saude_8_14": 0.8, "exaustao_8_14": 0.1, "aprendido_decidiu": 0.02,
                                "vida_sha256": f"{'hoje' if config.startswith(('h_max', 'tau_hab')) else config}|{braco}|{u}|{dono}|{lugar}"})
    return out


@pytest.mark.parametrize("efeitos, valor_base, leitura, mexem_valor", [
    ({}, 0.0, R.L_ESTRUTURAL, []),
    # um gene do aprendizado sobe o APRENDE e nao o CONGELADO: o valor muda e fica acima de 0 naquela config
    ({"eta_h_dobro": (0.10, 0.0)}, 0.0, R.L_BUSCAR, ["eta_h"]),
    # um gene da disputa sobe os dois bracos igual: o "Tempo bem" muda, o valor do aprendizado segue em 0
    ({"lambda_sono_metade": (0.10, 0.10)}, 0.0, R.L_REFLEXOS, []),
    # um gene da disputa muda o valor para baixo, e nenhum valor fica acima de 0
    ({"epsilon_dobro": (-0.10, 0.0)}, 0.0, R.L_REFLEXOS, ["epsilon"]),
    # um gene fora da disputa sobe os dois bracos igual: a tabela da secao 3 nao previu
    ({"w_pers_dobro": (0.10, 0.10)}, 0.0, R.L_FORA, []),
    # o valor do aprendizado acima de 0 em toda config, e nenhum gene o muda: tambem fora da tabela (so a disputa mexe no nivel)
    ({"lambda_sono_metade": (0.10, 0.10)}, 0.05, R.L_FORA, []),
])
def test_a_leitura_da_secao_3(efeitos, valor_base, leitura, mexem_valor):
    res = R.analisar(_registros(efeitos, valor_base))
    ler = res["leitura"]
    assert ler["leitura"] == leitura and ler["segue"] == R.SEGUE[leitura]
    assert ler["genes_que_mexem_no_valor_do_aprendizado"] == mexem_valor
    assert ler["acaso"]["contrastes_por_familia"] == 24 and ler["acaso"]["esperados_por_acaso_por_familia"] == pytest.approx(1.2)
    assert res["sensibilidade"]["unidades"] == 6 and len(res["configs"]) == 25 and set(res["ao_lado"]) == set(R.CONFIGS)
    assert res["ao_lado"]["hoje"]["saude_8_14"] == {"APRENDE": pytest.approx(0.8), "CONGELADO": pytest.approx(0.8)}
    # as vidas iguais as da config de hoje (a `vida_sha256`): o gene inerte tem todas iguais, na metade e no dobro
    assert res["genes_inertes"] == ["h_max", "tau_hab"] and res["iguais_a_hoje"]["h_max_dobro"]["APRENDE"] == {"vidas": 36, "iguais": 36}
    assert res["iguais_a_hoje"]["eta_d_dobro"] == {b: {"vidas": 36, "iguais": 0} for b in R.BRACOS} and "hoje" not in res["iguais_a_hoje"]
    tabela = res["genes_pelo_efeito"]
    assert [g["gene"] for g in tabela] != [] and len(tabela) == 12 and tabela == sorted(tabela, key=lambda g: -g["efeito"])
    if efeitos:
        gene = next(iter(efeitos)).rsplit("_", 1)[0]
        assert tabela[0]["gene"] == gene and tabela[0]["efeito"] == pytest.approx(0.10, abs=0.01) and tabela[0]["fora_de_zero"]
        assert (leitura == R.L_FORA) == (ler["nota"] is not None)


def test_a_ressalva_do_acaso_e_a_leitura_sem_ic():
    um = R.analisar(_registros({"eta_h_dobro": (0.10, 0.0)}))["leitura"]["acaso"]
    assert um["fora_de_zero"] == {"contraste_aprende": 1, "contraste_valor": 1}
    assert um["ressalva"] == {"contraste_aprende": True, "contraste_valor": True}      # 1 fora de zero, 1,2 esperado: nao e achado
    tres = R.analisar(_registros({"eta_h_dobro": (0.10, 0.0), "c_g_dobro": (0.10, 0.0), "g0_metade": (0.10, 0.0)}))["leitura"]["acaso"]
    assert tres["fora_de_zero"]["contraste_valor"] == 3 and tres["ressalva"]["contraste_valor"] is False
    assert R.analisar(_registros({}))["leitura"]["acaso"]["ressalva"] == {"contraste_aprende": False, "contraste_valor": False}
    sem = R.analisar(_registros({}, unidades=(1,)))["leitura"]
    assert sem["leitura"] == R.L_SEM_IC


def test_a_analise_falha_alto_com_vida_faltando_ou_repetida():
    rs = _registros({})
    with pytest.raises(R.E0Divergiu, match="vidas"):
        R.analisar(rs[:-1])
    with pytest.raises(R.E0Divergiu, match="repetida"):
        R.analisar(rs + rs[:1])


# ------------------------------------------------------------------ a trava
def test_a_trava_e_a_faixa():
    assert R.modo_da_config(FUMACA) == "fumaca"
    # PE-5: as 10 primeiras bases da faixa que a coordenadora reservou
    assert RUN["faixa"] == [110001, 110200] and RUN["unidades"]["bases"] == list(range(110001, 110011)) and RUN["unidades"]["k"] == 1
    assert any((lo, hi) == (110001, 110200) and "PLASTICIDADE_EVOLUIDA" in fonte for lo, hi, fonte in bv.FAIXAS_RESERVADAS)
    assert RUN["dias"] == R.DIAS and "configs" not in RUN
    assert RUN["plano"] == R.PLANO and "APROVADO pelo Matheus" in (RAIZ / R.PLANO).read_text(encoding="utf-8")
    assert R.modo_da_config(RUN) == R.FASE
    certa, bases = RUN, RUN["unidades"]["bases"]
    for errada in ({**certa, "unidades": {**certa["unidades"], "bases": bases[:9]}},                    # 9 bases
                   {**certa, "unidades": {**certa["unidades"], "bases": bases[:9] + [110201]}},         # uma base fora da faixa
                   {**certa, "unidades": {**certa["unidades"], "bases": bases[:9] + [bases[0]]}},       # base repetida
                   {**certa, "faixa": [110001, 110100]},                                                # a faixa nao e a reservada
                   {**certa, "faixa": "PENDENTE"}, {**certa, "unidades": {**certa["unidades"], "bases": []}}):   # a faixa pendente
        with pytest.raises(bv.SementeSemPlano):
            R.modo_da_config(errada)
    for errada in ({**certa, "dias": 7}, {**certa, "configs": ["hoje"]}, {**certa, "unidades": {**certa["unidades"], "k": 2}},
                   {**FUMACA, "fase": "recompensa"}, {**FUMACA, "pares": {}}, {**FUMACA, "configs": ["eta_d_dobro"]},
                   {**FUMACA, "configs": ["hoje", "nao_existe"]}, {**FUMACA, "dias": 15}):
        with pytest.raises(ValueError):
            R.modo_da_config(errada)
    with pytest.raises(ValueError, match="processos"):
        R.rodar(FUMACA, Path("nao_usa"), 5)


# ------------------------------------------------------------------ a fumaca
def test_a_fumaca_roda_com_o_relogio_fora_das_medidas(tmp_path):
    cfg = {**FUMACA, "dias": 1, "configs": ["hoje", "eta_h_dobro"], "unidades": {**FUMACA["unidades"], "bases": [101, 202]}}
    r = R.rodar(cfg, tmp_path / "f", 1)
    res, pasta = r["resultado"], tmp_path / "f"
    vidas = 2 * 2 * len(R.BRACOS) * len(R.CELULAS)
    assert res == {"modo": "fumaca", "fase": R.FASE, "vidas": vidas, "configs": ["hoje", "eta_h_dobro"], "conferencias": "passam"}
    for n in ("medidas.json", "custos.json", "resultado.json", "vidas.tar.gz", "meta.json"):
        assert (pasta / n).exists()
    assert not (pasta / "vidas").exists() and r["meta"]["pasta_crua_apagada"] == {"vidas": vidas}
    medidas = json.loads((pasta / "medidas.json").read_text(encoding="utf-8"))
    custos = json.loads((pasta / "custos.json").read_text(encoding="utf-8"))
    assert all("custo" not in m and 0.0 <= m["tempo_bem"] <= 1.0 and 0.0 <= m["saude_8_14"] <= 1.0 and 0.0 <= m["aprendido_decidiu"] <= 1.0
               for m in medidas)
    assert all(m["habito_abs"] == 0 and m["creditos_p2"] == 0 for m in medidas if m["braco"] == "CONGELADO")
    assert all(len(m["vida_sha256"]) == 64 and len(m["log_sha256"]) == 64 for m in medidas)
    assert set(custos) == {m["vida"] for m in medidas} and all(set(c) == {"vida_cpu", "vida_parede"} for c in custos.values())
    assert r["meta"]["custo"]["vidas_da_run"] == 3000 and r["meta"]["custo"]["projecao_parede_h_4_processos"] > 0
    assert [c["nome"] for c in r["meta"]["configs"]] == ["hoje", "eta_h_dobro"] and r["meta"]["bracos"]["CONGELADO"]["p1"] is False
    # a analise roda de ponta a ponta sobre as medidas gravadas (duas unidades: ha IC); nenhuma medida da fumaca e lida como resultado
    analise = R.analisar(medidas, R.configs_da_run(cfg))
    assert analise["sensibilidade"]["unidades"] == 2 and analise["leitura"]["leitura"] in R.SEGUE and len(analise["genes_pelo_efeito"]) == 1
    with pytest.raises(FileExistsError):
        R.rodar(cfg, pasta, 1)
    # sem o relogio, as medidas e o resultado de uma replica saem iguais byte a byte
    r2 = R.rodar(cfg, tmp_path / "g", 1)
    for n in ("medidas.json", "resultado.json", "vidas.tar.gz"):
        assert r2["meta"]["artefatos_sha256"][n] == r["meta"]["artefatos_sha256"][n]
