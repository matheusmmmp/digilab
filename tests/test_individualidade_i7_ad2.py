"""O adendo 2 do I7 da INDIVIDUALIDADE (docs/PLANO_ANALISE_V3_INDIVIDUALIDADE_I7.md, secao 14): as medidas novas em `digilab/metrics.py`
contra casos feitos a mao; o orquestrador (experiments/run_v3_individualidade_i7_ad2.py): a trava, o sorteio amarrado, o rho sobre somas
feitas a mao, a leitura (14.4) em ICs sinteticos e os ramos de um pet de ponta a ponta, com as conferencias G-AD2-0 a 4. Vidas so com as
sementes dos testes (101...505)."""
from __future__ import annotations

import gzip
import json
import random
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v3_individualidade_i7_ad2 as a2  # noqa: E402
from digilab import metrics as M  # noqa: E402

CONFIG = RAIZ / "experiments/configs/v3_individualidade/individualidade_i7_ad2.json"
FUMACA = RAIZ / "experiments/configs/v3_individualidade/individualidade_i7_ad2_fumaca.json"


# ================================================================== as medidas (metrics.py)
def test_trajetoria_da_janela():
    assert M.trajetoria_janela([0.0, 0.0, None, 0.0]) == "sempre0"
    assert M.trajetoria_janela([0.1, 0.2, 0.3, None]) == "nunca0"
    assert M.trajetoria_janela([0.0, 0.2]) == "misto"
    assert M.trajetoria_janela([None, None]) is None
    with pytest.raises(ValueError):
        M.trajetoria_janela([-0.1])


def test_fracao_amarrada_e_razao_de_somas():
    assert M.fracao_amarrada([(0.1, 0.4), (0.0, 0.1), (None, 0.3), (0.2, None)]) == pytest.approx(0.1 / 0.5)
    assert M.fracao_amarrada([(0.1, 0.0)]) is None
    assert M.fracao_amarrada([]) is None


# ================================================================== a trava
def _cfg(caminho=CONFIG) -> dict:
    return json.loads(caminho.read_text(encoding="utf-8"))


def test_a_fumaca_passa_e_a_run_pede_o_registro():
    assert a2.modo_da_config(_cfg(FUMACA)) == "fumaca"
    texto = a2._plano()
    assert any(x.startswith(a2.MARCA_ADENDO) for x in texto.splitlines()[:30])
    if a2.TITULO_REGISTRO not in texto:
        with pytest.raises(RuntimeError, match="registro do adendo 2"):
            a2.modo_da_config(_cfg())
    com = texto + f"\n{a2.TITULO_REGISTRO}\n\no registro.\n"
    assert a2.modo_da_config(_cfg(), texto_plano=com) == a2.FASE
    sem_adendo = com.replace(a2.MARCA_ADENDO, "**O adendo 2 (seção 14) está PROPOSTO")
    with pytest.raises(RuntimeError, match="DECIDIDO"):
        a2.modo_da_config(_cfg(), texto_plano=sem_adendo)


def test_a_config_fora_do_plano_falha_alto():
    c = _cfg()
    c["unidades"] = {**c["unidades"], "bases": [85101, 85202, 85303, 85404, 85505]}
    with pytest.raises(bv.SementeSemPlano):
        a2.modo_da_config(c)
    c = _cfg(FUMACA)
    c["vidas"] = "artifacts_v3_individualidade/vidas.tar.gz"
    with pytest.raises(ValueError, match="vidas"):
        a2.modo_da_config(c)
    c = _cfg(FUMACA)
    c["fase"] = "individualidade-i7"
    with pytest.raises(ValueError, match="fase"):
        a2.modo_da_config(c)


def test_as_bases_estao_na_faixa_do_adendo():
    for b in a2.BASES:
        assert a2.FONTE_FAIXA in bv.na_faixa_reservada(b)
    assert tuple(_cfg()["unidades"]["bases"]) == a2.BASES


# ================================================================== o sorteio amarrado (14.3)
class _Motor:
    class _E:
        tick = 0
    _estado = _E()


def test_o_gravador_e_o_amarrado():
    caixa = {"motor": _Motor()}
    ref = random.Random(7)
    g = a2.RngGravador(caixa, random.Random(7).getstate())
    us = []
    for tick in (0, 0, 15, 30):
        caixa["motor"]._estado.tick = tick
        us.append(g.random())
    assert us == [ref.random() for _ in range(4)]                       # o mesmo fluxo
    assert g.tabela == {(0, 0): us[0], (0, 1): us[1], (15, 0): us[2], (30, 0): us[3]}
    am = a2.RngAmarrado(caixa, g.tabela, 99)
    caixa["motor"]._estado.tick = 15
    assert am.random() == us[2]                                          # a mesma chave, o mesmo numero
    assert am.random() == random.Random(99).random()                     # (15, 1) sem par: a rng propria
    assert (am.par, am.sem_par) == (1, 1)
    with pytest.raises(RuntimeError, match="so usa random"):
        am.choice([1, 2])
    with pytest.raises(RuntimeError, match="so usa random"):
        g.randrange(3)


def test_o_estado_comprimido_volta_igual():
    r = random.Random(123)
    r.random()
    e = r.getstate()
    assert a2._descomprimir(a2._comprimir(e)) == e


# ================================================================== o rho e as estatisticas
def test_o_rho_sobre_somas_feitas_a_mao():
    idades, janela = (2, 4), 2
    tot = {("rho", 2, 1): [0.1, 0.4, 1], ("rho", 2, 2): [0.1, 0.1, 1], ("rho", 4, 1): [0.3, 0.5, 1], ("rho", 4, 2): [0.0, 0.0, 0]}
    assert a2.valor("rho", tot, idades, janela) == pytest.approx(0.5 / 1.0)
    assert a2.valor("rho(2)", tot, idades, janela) == pytest.approx(0.2 / 0.5)
    todas = set(a2.todas_as_chaves(a2.IDADES, a2.JANELA))
    cheio = {c: [0.1 * (1 + c[2]), 0.3, 1] for c in todas}
    for nome in a2.nomes_todos(a2.IDADES):
        assert set(a2.chaves_de(nome, a2.IDADES, a2.JANELA)) <= todas, nome
        so = {c: cheio[c] for c in a2.chaves_de(nome, a2.IDADES, a2.JANELA)}
        assert a2.valor(nome, so, a2.IDADES, a2.JANELA) == a2.valor(nome, cheio, a2.IDADES, a2.JANELA), nome


# ================================================================== a leitura (14.4)
def _ic(rho, phi_s=(0.5, 1.2), pegou_r=True) -> dict:
    ic = {f"Phi0_E({t})": [-0.1, 0.1] for t in a2.IDADES}
    ic["Phi0_E(2)"] = [0.1, 0.3]
    ic.update({f"Phi0_R({t})": [-0.1, 0.1] for t in a2.IDADES})
    if pegou_r:
        ic["Phi0_R(2)"] = [0.1, 0.3]
    ic.update({f"Phi_S({t})": list(phi_s) for t in a2.IDADES})
    ic.update({"rho": list(rho), "gamma_R": [-0.1, 0.1], "gamma_cru_R": [-0.1, 0.1]})
    return ic


def test_as_hipoteses_do_rho():
    assert a2.leitura(_ic((0.05, 0.15)), a2.IDADES)["hipotese"] == "H-SORT"
    assert a2.leitura(_ic((0.85, 1.1)), a2.IDADES)["hipotese"] == "H-HIST"
    assert a2.leitura(_ic((0.3, 0.6)), a2.IDADES)["hipotese"] == "os dois pesam"
    assert a2.leitura(_ic((0.1, 0.3)), a2.IDADES)["hipotese"] == "rho nao se separa do limiar nesta analise"
    sem = _ic((0.05, 0.15))
    sem["Phi0_E(2)"] = [-0.1, 0.1]
    assert a2.leitura(sem, a2.IDADES)["hipotese"].startswith("nenhuma hipotese se declara")


def test_as_frases_do_s_e_do_amarrado():
    assert a2.leitura(_ic((0.3, 0.6), (0.85, 1.1)), a2.IDADES)["S"] == "deslocar o fluxo em um sorteio faz do pet um gemeo"
    assert a2.leitura(_ic((0.3, 0.6), (0.2, 0.5)), a2.IDADES)["S"] == "deslocar o fluxo em um sorteio nao basta para um gemeo"
    assert a2.leitura(_ic((0.3, 0.6)), a2.IDADES)["S"] == "nao se distingue do limiar nesta analise"
    fr = a2.leitura(_ic((0.05, 0.15), pegou_r=False), a2.IDADES)
    assert fr["condicao_do_amarrado"] == "com o sorteio amarrado, o tapa nao mudou o dia" and fr["hipotese"] == "H-SORT"
    ic = _ic((0.3, 0.6))
    ic.update({"gamma_R": [0.1, 0.2], "gamma_cru_R": [-0.1, 0.1]})
    assert a2.leitura(ic, a2.IDADES)["gamma_R"].startswith("a inclinacao vem da regua")


# ================================================================== os ramos de um pet, de ponta a ponta
@pytest.fixture(scope="module")
def um_pet():
    dias = 6
    r = a2.tarefa_pet("REL", "atencioso", {"semente": 101, "base": 101, "k": 0}, dias, a2.ORCAMENTO_POR_DIA, idades=(2,))
    return r, dias


def test_os_ramos_de_um_pet_passam_nas_conferencias(um_pet):
    r, _ = um_pet
    ramos = {(x["ramo"], x["idade"]): x for x in r["ramos"]}
    assert set(ramos) == {("N", None), ("G", None), ("R0", None), ("E", 2), ("R", 2), ("S", 2)}
    assert ramos[("N", None)]["log_sha256"] == a2.r7._sha(r["log_base"])            # G-AD2-0
    assert ramos[("R0", None)]["log_sha256"] == ramos[("N", None)]["log_sha256"]     # G-AD2-1
    assert ramos[("R0", None)]["amarrado"]["sem_par"] == 0
    assert ramos[("G", None)]["decisoes_sha256"] != ramos[("N", None)]["decisoes_sha256"]
    assert ramos[("E", 2)]["log_sha256"] != ramos[("N", None)]["log_sha256"]         # o tapa a mais (G-AD2-4)
    assert ramos[("S", 2)]["log_sha256"] != ramos[("E", 2)]["log_sha256"]            # o S sem tapa
    assert set(ramos[("R", 2)]["amarrado"]) == {"par", "sem_par", "passos", "passos_descasados"}
    assert set(ramos[("E", 2)]["arb_fim_do_dia_t"]) == {"sorteios", "reflexos"}
    assert r["sem_ramo"] == []


def test_a_analise_de_um_pet(um_pet, tmp_path):
    r, dias = um_pet
    caminho = tmp_path / "p.jsonl.gz"
    with gzip.open(caminho, "wt", encoding="utf-8") as f:
        for linha in a2.r7.linhas_perfis(r):
            f.write(json.dumps(linha, sort_keys=True) + "\n")
    pets = a2.r7.ler_perfis(caminho)
    a2.r7.conferir_lidos(pets, [r])
    linhas = json.loads(json.dumps(r["ramos"]))
    ag = a2.agregados(pets, "REL", "SEQ", (2,), a2.JANELA, dias)
    p = a2.pontos(ag, (2,), a2.JANELA)
    assert p["Phi_E(2)"] is not None and p["Phi_R(2)"] is not None and p["Phi_S(2)"] is not None
    ic = a2.bootstrap(ag, ["rho", "Phi_S(2)"], ("REL", "SEQ"), (2,), a2.JANELA, 20)
    assert set(ic) == {"rho", "Phi_S(2)"}
    d = a2.descritivo(pets, ag, linhas, "REL", "SEQ", (2,), a2.JANELA, dias)
    assert set(d["tudo_ou_nada"]) == {"E", "R"} and d["tudo_ou_nada"]["E"]["total"]["n"] == 1
    assert d["amarrado_R"]["total"]["fracao_sem_par"] is not None
    assert set(d["reencontro_dia_final"]) == {"E", "R", "S"}
