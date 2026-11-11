"""O I7 da INDIVIDUALIDADE (docs/PLANO_ANALISE_V3_INDIVIDUALIDADE_I7.md): as medidas do ramo em `digilab/metrics.py` contra casos feitos a
mao; o orquestrador (experiments/run_v3_individualidade_i7.py): a trava, o log do E° (o tapa inserido), as estatisticas sobre somas feitas a
mao, a leitura (7.2 e o adendo 1) em ICs sinteticos e os ramos de um pet de ponta a ponta, com as conferencias G-I7-0 a 3. Vidas so com as
sementes dos testes (101...505): nenhuma vida do I2 e vivida aqui."""
from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v3_individualidade_i7 as r7  # noqa: E402
from digilab import metrics as M  # noqa: E402

CONFIG = RAIZ / "experiments/configs/v3_individualidade/individualidade_i7.json"
FUMACA = RAIZ / "experiments/configs/v3_individualidade/individualidade_i7_fumaca.json"
APROVADO = "**Status: APROVADO pelo Matheus em 2026-11-10.**"


# ================================================================== as medidas (metrics.py)
def test_distancias_do_ramo_dia_a_dia():
    ramo = {1: [1, 0], 2: [1, 1], 3: None}
    orig = {1: [1, 0], 2: [0, 1], 3: [1, 0]}
    assert M.distancias_ramo(ramo, orig, [1, 2, 3, 4]) == {1: 0.0, 2: 0.5, 3: None, 4: None}


def test_razao_de_somas_e_nao_media_de_razoes():
    assert M.razao_de_somas([(0.2, 0.4), (0.3, 0.0), (None, 1.0), (0.5, None)]) == pytest.approx(0.5 / 0.4)
    assert M.razao_de_somas([(0.2, 0.0)]) is None              # a soma do gemeo 0
    assert M.razao_de_somas([]) is None
    assert M.soma_presente([(0.2, 0.4), (0.3, None)]) == 0.2


def test_inclinacao_ou_none():
    assert M.inclinacao_ou_none([1, 2, 3, 4], [1.0, 2.0, 3.0, 4.0]) == pytest.approx(1.0)
    assert M.inclinacao_ou_none([1, 2, 3], [None, 2.0, 4.0]) == pytest.approx(2.0)
    assert M.inclinacao_ou_none([1, 2], [None, 2.0]) is None


def test_distancia_do_estado_feita_a_mao():
    a = M.folhas_estado({"x": 1, "y": [1, 2], "z": {}})
    assert a == {"x": 1, "y.0": 1, "y.1": 2, "z.{}": None}
    b = M.folhas_estado({"x": 1, "y": [1, 3, 4], "z": {}})
    # os caminhos: x, y.0, y.1, y.2, z.{} (5); diferem y.1 e y.2 (so num)
    assert M.distancia_estado(a, b) == pytest.approx(2 / 5)
    assert M.distancia_estado(a, a) == 0.0
    assert M.distancia_estado({"p": None}, {}) == 1.0         # o caminho com None so num lado conta


def test_efeito_comum_para_o_mesmo_lado_e_para_lados_opostos():
    orig = [[2, 2], [2, 2]]
    assert M.efeito_comum([[4, 0], [4, 0]], orig) == pytest.approx(1.0)      # os dois pets para o mesmo lado
    assert M.efeito_comum([[4, 0], [0, 4]], orig) == pytest.approx(0.0)      # cada um para um lado
    assert M.efeito_comum([[2, 2]], [[2, 2]]) is None                        # sem mudanca, a media e 0


def test_reencontro_no_dia():
    d = [{"tick": 15 * i, "acao": "comer", "x": 0, "y": 0} for i in range(96)]
    outro = [dict(x) for x in d]
    assert M.reencontrou(outro, d, 1)
    outro[3]["x"] = 16
    assert not M.reencontrou(outro, d, 1)


# ================================================================== o log do E°
def test_o_tapa_entra_antes_do_primeiro_evento_do_tick():
    linhas = [{"tick": 0, "tipo": "avanco", "valor": 15}, {"tick": 15, "tipo": "acao_usuario", "valor": "limpar"},
              {"tick": 15, "tipo": "avanco", "valor": 15}]
    texto = "\n".join(json.dumps(x) for x in linhas)
    saida = r7.log_com_tapa(texto, 15).splitlines()
    assert json.loads(saida[1]) == {"tick": 15, "tipo": "acao_usuario", "valor": "tapa"}
    assert saida[0] == json.dumps(linhas[0]) and saida[2:] == [json.dumps(x) for x in linhas[1:]]
    assert not r7.log_com_tapa(texto, 15).endswith("\n")       # a mesma convencao do log dado
    with pytest.raises(ValueError):
        r7.log_com_tapa(texto, 30)


# ================================================================== a trava
def _cfg(**kw) -> dict:
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    cfg.update(kw)
    return cfg


def _plano(com_registro: bool) -> str:
    texto = f"# PLANO\n\n{APROVADO} o resto\n\n## 10. O registro da análise\n\nantes\n"
    return texto + ("\n## 13. O registro da análise\n\no commit\n" if com_registro else "")


def test_a_trava_pede_o_aprovado_e_a_secao_nova_do_registro():
    r7.exigir_plano_aprovado(_plano(True))
    with pytest.raises(RuntimeError, match="13. O registro"):
        r7.exigir_plano_aprovado(_plano(False))
    with pytest.raises(RuntimeError, match="APROVADO"):
        r7.exigir_plano_aprovado(_plano(True).replace("APROVADO", "PROPOSTO"))


def test_a_config_da_run_e_a_da_fumaca():
    assert r7.modo_da_config(_cfg(), _plano(True)) == r7.FASE
    with pytest.raises(RuntimeError):
        r7.modo_da_config(_cfg(), _plano(False))
    fumaca = json.loads(FUMACA.read_text(encoding="utf-8"))
    assert r7.modo_da_config(fumaca) == "fumaca"
    with pytest.raises(ValueError, match="dias"):
        r7.modo_da_config({**fumaca, "dias": 8})
    with pytest.raises(bv.SementeSemPlano):
        r7.modo_da_config(_cfg(unidades={**_cfg()["unidades"], "bases": [99101]}), _plano(True))
    with pytest.raises(ValueError, match="K"):
        r7.modo_da_config(_cfg(unidades={**_cfg()["unidades"], "k": 3}), _plano(True))


def test_a_run_recusa_mais_de_4_processos_e_pasta_existente(tmp_path):
    fumaca = json.loads(FUMACA.read_text(encoding="utf-8"))
    with pytest.raises(ValueError, match="4 processos"):
        r7.rodar(fumaca, tmp_path / "x", 5)
    with pytest.raises(FileExistsError):
        r7.rodar(fumaca, tmp_path, 1)


# ================================================================== as estatisticas (somas feitas a mao)
def _tot(por_ramo: dict) -> dict:
    """{(b, t, k): [soma D_b, soma D_G, pares]} a partir de {(b, t, k): (D_b, D_G)}"""
    return {c: [a, g, 1] for c, (a, g) in por_ramo.items()}


def test_phi_gamma_beta_e_a_regua_crua():
    idades, janela = (2, 4), 2
    tot = _tot({("A", 2, 1): (0.1, 0.2), ("A", 2, 2): (0.3, 0.2), ("A", 4, 1): (0.2, 0.4), ("A", 4, 2): (0.2, 0.4),
                ("G", 2, 1): (0.2, 0.2), ("G", 2, 2): (0.2, 0.2), ("G", 4, 1): (0.4, 0.4), ("G", 4, 2): (0.4, 0.4)})
    v = lambda n: r7.valor(n, tot, idades, janela)  # noqa: E731
    assert v("Phi_A(2)") == pytest.approx(0.4 / 0.4) and v("Phi_A(4)") == pytest.approx(0.4 / 0.8)
    assert v("Phi_A(todas)") == pytest.approx(0.8 / 1.2)
    # r(1) = 0.3 / 0.6 = 0.5; r(2) = 0.5 / 0.6; a inclinacao em k e a diferenca
    assert v("gamma_A") == pytest.approx(0.5 / 0.6 - 0.5)
    assert v("beta_A") == pytest.approx((0.5 - 1.0) / 2)                  # por dia de idade
    assert v("gamma_cru_A") == pytest.approx(0.5 - 0.3)
    assert v("beta_cru_A") == pytest.approx((0.4 - 0.4) / 2)
    assert v("gamma_cru_G") == pytest.approx(0.0) and v("beta_cru_G") == pytest.approx((0.8 - 0.4) / 2)
    assert v("U1_A") is None                                              # sem as idades 2, 6 e 10


def test_as_chaves_cobrem_o_que_a_estatistica_soma():
    idades, janela = r7.IDADES, r7.JANELA
    todas = set(r7.todas_as_chaves(idades, janela))
    for nome in r7.nomes_todos(idades):
        assert set(r7.chaves_de(nome, idades, janela)) <= todas, nome
    tot = {c: [0.1 * (1 + c[2]), 0.3, 1] for c in todas}
    for nome in r7.nomes_todos(idades):             # a estatistica so com as chaves dela da o mesmo que com todas
        so = {c: tot[c] for c in r7.chaves_de(nome, idades, janela)}
        assert r7.valor(nome, so, idades, janela) == r7.valor(nome, tot, idades, janela), nome


# ================================================================== a leitura (7.2 e o adendo 1)
def _ic_base(idades=r7.IDADES) -> dict:
    """um braco sem nada declarado: todo IC contem 0 (ou 1 no Phi), e o tapa pegou na idade 2"""
    ic = {f"Phi_{b}({t})": [0.5, 1.2] for b in ("A", "E") for t in idades}
    ic.update({f"Phi0_E({t})": [-0.1, 0.1] for t in idades})
    ic["Phi0_E(2)"] = [0.1, 0.3]
    ic.update({n: [-0.1, 0.1] for n in ("gamma_A", "gamma_E", "beta_A", "beta_E", "gamma_cru_A", "gamma_cru_E", "beta_cru_A",
                                        "beta_cru_E", "U1_A", "U2_A", "U1_E", "U2_E")})
    return ic


def test_a_condicao_do_evento_bloqueia_as_frases_e_as_hipoteses():
    ic = _ic_base()
    ic["Phi0_E(2)"] = [-0.1, 0.1]
    ic.update({"gamma_E": [-0.3, -0.1], "gamma_cru_E": [-0.3, -0.1]})
    ic.update({f"Phi_A({t})": [0.3, 0.7] for t in r7.IDADES})
    fr = r7.leitura(ic, r7.IDADES)
    assert fr["E"] == "o tapa nao mudou o dia" and fr["hipotese"].startswith("nenhuma hipotese se declara")


def test_h_can_h_amp_h_caos_e_h_trans():
    ic = _ic_base()
    ic.update({"gamma_E": [-0.3, -0.1], "gamma_cru_E": [-0.3, -0.1]})
    ic.update({f"Phi_A({t})": [0.3, 0.7] for t in r7.IDADES})
    assert r7.leitura(ic, r7.IDADES)["hipotese"] == "H-CAN"
    amp = _ic_base()
    amp.update({"gamma_E": [0.1, 0.3], "gamma_cru_E": [0.1, 0.3], "beta_E": [-0.3, -0.1], "beta_cru_E": [-0.3, -0.1]})
    assert r7.leitura(amp, r7.IDADES)["hipotese"] == "H-AMP"
    caos = _ic_base()
    caos.update({f"Phi_{b}({t})": [0.85, 1.1] for b in ("A", "E") for t in r7.IDADES})
    assert r7.leitura(caos, r7.IDADES)["hipotese"] == "H-CAOS"
    # a H-TRANS no lugar da H-CAN quando as duas valem (12.1)
    trans = dict(ic)
    trans.update({"Phi_A(2)": [0.85, 0.95], "Phi_A(10)": [0.2, 0.5], "beta_A": [-0.1, -0.05], "beta_cru_A": [-0.2, -0.1]})
    assert r7.leitura(trans, r7.IDADES)["hipotese"] == "H-TRANS"


def test_a_regua_crua_e_a_forma_em_u_seguram_as_frases():
    ic = _ic_base()
    ic.update({"gamma_E": [-0.3, -0.1], "gamma_cru_E": [-0.05, 0.05]})          # a razao cai, o cru nao (12.2)
    ic.update({f"Phi_A({t})": [0.3, 0.7] for t in r7.IDADES})
    fr = r7.leitura(ic, r7.IDADES)
    assert fr["E"]["gamma"].startswith("a inclinacao vem da regua") and fr["hipotese"] != "H-CAN"
    u = _ic_base()
    u.update({"U1_E": [0.1, 0.2], "U2_E": [0.1, 0.3], "beta_E": [-0.3, -0.1], "beta_cru_E": [-0.3, -0.1],
              "gamma_E": [0.1, 0.3], "gamma_cru_E": [0.1, 0.3]})
    fr = r7.leitura(u, r7.IDADES)
    assert fr["E"]["beta"] == "o afastamento muda com a idade sem ser em linha (U)" and fr["hipotese"] != "H-AMP"


def test_as_frases_de_cada_idade():
    ic = _ic_base()
    ic["Phi_A(2)"], ic["Phi_A(4)"] = [0.85, 0.95], [0.2, 0.4]
    fr = r7.leitura(ic, r7.IDADES)["A"]["idades"]
    assert fr["2"] == ["a historia ate o dia t sobrevive a outro acaso", "o ramo vira um gemeo"]
    assert fr["4"] == ["a historia ate o dia t sobrevive a outro acaso"]
    assert fr["6"] == ["nao se distingue de 1 nesta analise"]


# ================================================================== os ramos de um pet, de ponta a ponta
@pytest.fixture(scope="module")
def um_pet():
    import run_v2_memoria_autobio as ma
    dias = 6
    motor, *_ = ma.viver("REL", "atencioso", r7.LUGAR, 101, dias, r7.ORCAMENTO_POR_DIA)
    texto = motor.log.para_jsonl()
    r = r7.tarefa_pet("REL", "atencioso", {"semente": 101, "base": 101, "k": 0}, texto, dias, r7.ORCAMENTO_POR_DIA, idades=(2,))
    return texto, r, dias


def test_os_ramos_de_um_pet_passam_nas_conferencias(um_pet):
    texto, r, _ = um_pet
    ramos = {(x["ramo"], x["idade"]): x for x in r["ramos"]}
    assert set(ramos) == {("N", None), ("G", None), ("A", 2), ("E", 2), ("E0", 2)}
    assert ramos[("N", None)]["log_sha256"] == r7._sha(texto)                    # G-I7-0
    assert ramos[("G", None)]["decisoes_sha256"] != ramos[("N", None)]["decisoes_sha256"]
    assert ramos[("E", 2)]["log_sha256"] != ramos[("N", None)]["log_sha256"]       # o tapa a mais (G-I7-3)
    assert r["momentos"]["2"] % 15 == 0 and r["sem_ramo"] == []


def test_o_artefato_dos_perfis_volta_igual(um_pet, tmp_path):
    _, r, dias = um_pet
    caminho = tmp_path / "p.jsonl.gz"
    with gzip.open(caminho, "wt", encoding="utf-8") as f:
        for linha in r7.linhas_perfis(r):
            f.write(json.dumps(linha, sort_keys=True) + "\n")
    pets = r7.ler_perfis(caminho)
    r7.conferir_lidos(pets, [r])
    ag = r7.agregados(pets, "REL", "SEQ", (2,), r7.JANELA, dias)
    p = r7.pontos(ag, (2,), r7.JANELA)
    assert p["Phi_A(2)"] is not None and p["Phi_A(2)"] >= 0
    ic = r7.bootstrap(ag, ["Phi_A(2)"], ("REL", "SEQ"), (2,), r7.JANELA, 20)
    assert ic["Phi_A(2)"] is None or ic["Phi_A(2)"][0] <= ic["Phi_A(2)"][1]


def test_o_ramo_de_cada_chave_do_custo():
    assert [r7._ramo_do_custo(k) for k in ("N", "G", "A2", "A10", "E4", "E10", "E04", "E010")] == ["N", "G", "A", "A", "E", "E", "E0", "E0"]
