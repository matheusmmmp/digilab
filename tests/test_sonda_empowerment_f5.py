"""A sonda do E(P) da F5 (docs/ESPEC_V3_SONDA_EMPOWERMENT.md, secao 7): T-E1 a T-E4 nas contas puras, num mundo de brinquedo feito a
mao; T-E5 (o G-S0) e T-E6 (o G-S1) numa semente dos testes, a primeira vida da AN0 da PET_VIVO. Nenhuma medida roda aqui (SE2)."""
from __future__ import annotations

import hashlib
import random
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "experiments"))

import sonda_empowerment_f5 as sd  # noqa: E402

S = 1024
RECS = ("fome", "energia")                     # o brinquedo: dois receptores, a energia no indice 1
IE = 1


def _desfecho(**por_classe) -> dict:
    out = {c: [0, 0] for c in sd.CLASSES_DESFECHO}
    out.update(por_classe)
    return out


# ------------------------------------------------------------------ T-E1: a conta feita no papel
def test_te1_o_e_e_o_cont_batem_com_a_conta_no_papel():
    # racao a 3 de P, a a 4 de P; da racao ate a a, 5 (o triangulo 3-4-5)
    P = (0, 0)
    pontos = [("racao", (3, 0)), ("a", (0, 4))]
    alc = sd.alcance(P, pontos, 10)
    assert alc == {"racao": (3, (3, 0)), "a": (4, (0, 4))}
    assert sd.cont_de(alc) == 2
    # leitura: fome 100 (faixa 0), energia 600 (faixa 2). A racao sobe a fome em 200; a a sobe em 200 tambem; o andar e 0.
    #   []           -> fome 100, en 600 -> (0, 2)
    #   [racao]      -> fome 300          -> (1, 2)
    #   [a]          -> fome 300          -> (1, 2)   o mesmo corpo da racao: conta um so
    #   [racao, a]   -> fome 500          -> (1, 2)   500 < 512: ainda a faixa 1
    #   [a, racao]   -> fome 500          -> (1, 2)
    d = _desfecho(racao=[200, 0], a=[200, 0])
    assert sd.corpos(alc, [100, 600], d, 0, IE, S) == {(0, 2), (1, 2)}
    assert sd.e_de(alc, [100, 600], d, 0, IE, S) == 2
    # com a a subindo a fome em 300: [a] 400 (1), [racao, a] 600 (2) -> tres corpos
    d = _desfecho(racao=[200, 0], a=[300, 0])
    assert sd.corpos(alc, [100, 600], d, 0, IE, S) == {(0, 2), (1, 2), (2, 2)}
    # o andar: -S/2 por subunidade x S, ou seja, cada subunidade custa 512/1024 de energia; o caminho [racao] e 3 -> -2 (div_arred(-1536,
    # 1024) = -2, meio longe do zero); [racao, a] e 3 + 5 = 8 -> -4. A energia 600 fica na faixa 2 nos dois: o andar nao muda o E aqui
    assert sd.e_de(alc, [100, 600], d, -512, IE, S) == 3
    # perto do limite: a energia 513 cai para 511 com [racao] e com [a] (faixa 1), para 509 com [racao, a] e 508 com [a, racao]
    assert sd.corpos(alc, [100, 513], d, -512, IE, S) == {(0, 2), (1, 1), (2, 1)}


def test_te1_o_andar_entra_somado_como_no_lobos():
    alc = {"racao": (10, (10, 0))}
    # andar negativo (andar cansa): a energia desce com o caminho
    assert sd.corpos(alc, [0, 300], _desfecho(), -S, IE, S) == {(0, 1)}               # 300 - 10 = 290, ainda >= 256: a faixa 1
    assert sd.corpos(alc, [0, 260], _desfecho(), -S, IE, S) == {(0, 1), (0, 0)}       # 260 - 10 = 250 < 256: a faixa 0


def test_te1_os_objetos_vistos_sao_relativos_ao_pet():
    pontos = sd.pontos_de([], [{"classe": "a", "dx": -5, "dy": 2}, {"classe": "tela", "dx": 0, "dy": 0}], (100, 50))
    assert pontos == [("a", (95, 52))]


def test_te1_so_os_episodios_de_consumo_entram():
    eps = [{"origem": "consumo", "classe": "racao", "ponto": [1, 2]}, {"origem": "visita", "classe": "nao_havia", "ponto": [3, 4]},
           {"origem": "evento", "classe": "sem_alvo", "ponto": [5, 6]}, {"origem": "consumo", "classe": "bola", "ponto": [7, 8]}]
    assert sd.pontos_de(eps, [], (0, 0)) == [("racao", (1, 2)), ("bola", (7, 8))]


def test_te1_o_horizonte_dois_tem_no_maximo_37_sequencias():
    alc = {c: (1, (i, 0)) for i, c in enumerate(sd.CLASSES_DESFECHO)}
    # cada classe sobe a fome num degrau diferente e a energia noutro: o maximo de corpos distintos e limitado pelas faixas (4 x 4)
    d = {c: [100 * (i + 1), -60 * i] for i, c in enumerate(sd.CLASSES_DESFECHO)}
    assert sd.e_de(alc, [0, 1023], d, 0, IE, S) <= 37


# ------------------------------------------------------------------ T-E2: sem episodio e sem objeto
def test_te2_sem_nada_ao_alcance_e_um_e_o_cont_zero():
    alc = sd.alcance((0, 0), sd.pontos_de([], [], (0, 0)), 1024)
    assert alc == {}
    assert sd.e_de(alc, [500, 500], _desfecho(racao=[400, 0]), -S, IE, S) == 1
    assert sd.cont_de(alc) == 0


# ------------------------------------------------------------------ T-E3: o pet que nao aprendeu nada
@pytest.mark.parametrize("leitura", [[0, 0], [300, 700], [1023, 1023], [255, 256]])
def test_te3_com_o_desfecho_zero_e_o_andar_zero_o_e_e_um(leitura):
    alc = {c: (7 * (i + 1), (i, i)) for i, c in enumerate(sd.CLASSES_DESFECHO)}
    assert sd.e_de(alc, leitura, _desfecho(), 0, IE, S) == 1
    assert sd.cont_de(alc) == 6


# ------------------------------------------------------------------ T-E4: o limite do d_max
def test_te4_fora_do_d_max_nao_entra_e_no_limite_entra():
    pontos = [("racao", (30, 40)), ("a", (30, 41))]                 # 50 e raiz_inteira(2581) = 50 tambem; (31, 41): 51
    assert set(sd.alcance((0, 0), pontos, 50)) == {"racao", "a"}
    assert set(sd.alcance((0, 0), pontos, 49)) == set()
    assert set(sd.alcance((0, 0), [("racao", (31, 41))], 50)) == set()
    assert sd.alcance((0, 0), [("racao", (31, 41))], 51) == {"racao": (51, (31, 41))}


def test_te4_o_ponto_mais_perto_e_no_empate_o_primeiro():
    pontos = [("racao", (0, 10)), ("racao", (10, 0)), ("racao", (0, 5))]
    assert sd.alcance((0, 0), pontos, 100) == {"racao": (5, (0, 5))}
    assert sd.alcance((0, 0), pontos[:2], 100) == {"racao": (10, (0, 10))}


# ------------------------------------------------------------------ as medidas, no papel
def test_os_pares_seguem_a_contagem_de_kendall():
    linhas = [[[0, 0], 3, 1], [[1, 0], 2, 2], [[2, 0], 2, 0], [[3, 0], 3, 1]]
    # (0,1) E> C< disc; (0,2) E> C> conc; (0,3) empate nos dois; (1,2) E= C> emp_E; (1,3) E< C> disc; (2,3) E< C< conc
    assert sd.pares(linhas) == {"conc": 2, "disc": 2, "emp_E": 1, "emp_CONT": 0, "emp_ambos": 1}


def test_a_leitura_segue_os_limiares_em_inteiros():
    def m(amp2, n, disc, pares):
        return {"M_S1": {"amplitude_2_ou_mais": [amp2, n]}, "M_S2": {"discordantes": [disc, pares]}}
    assert sd.leitura(m(9, 100, 50, 100))["plano"] is True               # 9/100 < 1/10
    assert sd.leitura(m(10, 100, 50, 100))["plano"] is False             # 10/100 nao e < 1/10
    assert sd.leitura(m(50, 100, 4, 100))["igual_ao_cont"] is True       # 4/100 < 1/20
    assert sd.leitura(m(50, 100, 5, 100))["igual_ao_cont"] is False
    assert "H-EMP-1" in sd.leitura(m(50, 100, 5, 100))["linha"]
    assert sd.leitura(m(50, 100, 0, 0))["igual_ao_cont"] is None


def test_o_plano_pelas_entradas_segue_a_secao_4_do_plano():
    def m(amp2, cont1, n=100):
        return {"M_S1": {"amplitude_2_ou_mais": [amp2, n], "CONT_do_lugar_do_pet_ate_1": [cont1, n]},
                "M_S2": {"discordantes": [50, 100]}}
    assert sd.leitura(m(5, 51))["plano_pelas_entradas"] is True and "opcao (b)" in sd.leitura(m(5, 51))["linha"]
    assert sd.leitura(m(5, 50))["plano_pelas_entradas"] is False and "acaba" in sd.leitura(m(5, 50))["linha"]
    assert sd.leitura(m(50, 90))["plano_pelas_entradas"] is False


def test_a_m_s3_compara_com_o_acaso_dos_empates():
    dec = [{"P": [[[0, 0], 1, 0], [[1, 1], 3, 1], [[2, 2], 3, 1], [[3, 3], 2, 1]], "candidatos": [[1, 1], [2, 2], [3, 3]],
            "alvo": [1, 1]},
           {"P": [[[0, 0], 1, 0], [[1, 1], 1, 1], [[2, 2], 2, 1]], "candidatos": [[1, 1], [2, 2]], "alvo": [1, 1]},
           {"P": [[[0, 0], 1, 0], [[1, 1], 1, 1]], "candidatos": [[1, 1]], "alvo": [1, 1]}]      # um candidato so: fora
    s3 = sd.medir(dec)["M_S3"]
    assert s3["decisoes"] == 2 and s3["acertos"] == 1
    assert (s3["acaso_num"], s3["acaso_den"]) == (7, 6)                  # 2/3 + 1/2


# ------------------------------------------------------------------ T-E5 e T-E6: numa semente dos testes
_CACHE: dict = {}


def _vida():
    if not _CACHE:
        gab = sd.gabaritos()
        x = sd.vidas()[0]
        _CACHE["gab"] = gab["vidas"][(x[0], x[1], x[2], x[3])]
        _CACHE["x"] = x
        _CACHE["com"] = sd.sondar((*x, _CACHE["gab"]))                   # ja conferiu o G-S0 contra o gabarito
        motor, cerebro, col = sd.viver(*x[:4], False)
        _CACHE["sem"] = sd.assinatura(motor, cerebro)
        assert col is None
    return _CACHE


def test_te5_a_vida_sai_igual_com_e_sem_o_coletor():
    c = _vida()
    assert c["com"]["log_sha256"] == c["sem"]["log"]
    sd.conferir_gs0(c["sem"], c["gab"], "sem o coletor")
    assert len(c["com"]["decisoes"]) == len(c["sem"]["motivos"]) == len(c["gab"]["decisoes"])


def test_te5_o_g_s0_falha_alto_com_o_gabarito_errado():
    c = _vida()
    errado = {**c["gab"], "log": "0" * 64, "log_sha256": "0" * 64}
    with pytest.raises(RuntimeError, match="G-S0"):
        sd.conferir_gs0(c["sem"], errado, "errado")


def test_te5_cada_decisao_tem_o_lugar_do_pet_primeiro_e_e_de_1_a_37():
    for d in _vida()["com"]["decisoes"]:
        assert d["P"][0][0] == d["lugar"]
        assert all(1 <= e <= 37 and 0 <= c <= 6 for _, e, c in d["P"])
        assert len({tuple(x[0]) for x in d["P"]}) == len(d["P"])
        assert all(c in [x[0] for x in d["P"]] for c in d["candidatos"])


def test_te6_a_leitura_nao_mexe_em_rng():
    """o coletor confere o G-S1 em cada leitura (falha alto); aqui, um coletor que gasta a rng tem de ser pego"""
    c = _vida()
    assert len(c["com"]["decisoes"]) > 0                                # cada leitura passou pelo G-S1
    orig = sd.ler_decisao

    def gasta(sens, unidades, plast, memoria):
        random.random()
        return orig(sens, unidades, plast, memoria)

    sd.ler_decisao = gasta
    try:
        with pytest.raises(RuntimeError, match="G-S1"):
            sd.viver(*c["x"][:4], True)
    finally:
        sd.ler_decisao = orig


def test_duas_execucoes_saem_iguais():
    c = _vida()
    x = c["x"]
    outra = sd.sondar((*x, c["gab"]))
    h = [hashlib.sha256(repr(v["decisoes"]).encode()).hexdigest() for v in (c["com"], outra)]
    assert h[0] == h[1]


def test_a_medida_espera_o_plano(tmp_path, monkeypatch):
    monkeypatch.setattr(sd, "PLANO", tmp_path / "nao_existe.md")
    with pytest.raises(SystemExit, match="D-F5-8"):
        sd.principal(1, tmp_path / "saida")


# ================================================================== a (b2) do adendo 1
def test_b2_a_sonda_nao_muda_a_vida_na_ilha():
    """o G-S0 da (b2): a vida no mundo com arvores sai igual com e sem o coletor, e ha uma leitura por decisao"""
    x = ("atencioso", "comedouro", 101)
    m, c, _ = sd.viver_b2(*x, False)
    m2, c2, col = sd.viver_b2(*x, True)
    a = sd.assinatura_b2(m, c)
    assert sd.assinatura_b2(m2, c2) == a
    assert len(col.registros) == a["decisoes"] == col.leituras_rng


def test_b2_vidas_sao_as_oito_celulas_da_an0():
    assert len(sd.vidas_b2()) == 8 and {s for _, _, s in sd.vidas_b2()} <= {101, 202}


def test_b2_a_medida_espera_o_gabarito(tmp_path):
    with pytest.raises(SystemExit, match="gabarito"):
        sd.principal_b2(1, tmp_path / "saida", tmp_path / "nao_existe.json")


def test_b2_a_medida_espera_o_adendo_aprovado(tmp_path, monkeypatch):
    falso = tmp_path / "adendo.md"
    falso.write_text("**Status: PROPOSTO.**\n", encoding="utf-8")
    monkeypatch.setattr(sd, "ADENDO1", falso)
    with pytest.raises(SystemExit, match="D-F5-8"):
        sd.principal_b2(1, tmp_path / "saida", tmp_path / "nao_existe.json")
