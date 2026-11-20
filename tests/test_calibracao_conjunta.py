"""V2, K2 (docs/TAREFA_V2_K2_CALIBRACAO_CONJUNTA.md; plano docs/PLANO_CALIBRACAO_CONJUNTA_V2.md): o orquestrador da calibracao conjunta.
So as sementes dos testes. As regras de escolha em dados sinteticos com a resposta conhecida; os modos (a validacao 30101...30505 nunca);
a sonda da informacao (so le); o poder por simulacao contra a formula; e uma fumaca das cinco etapas, com o replay do disco.
"""
from __future__ import annotations

import copy
import json
import random
import sys
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v2_calibracao_conjunta as k2  # noqa: E402
from digilab.config import CONFIG_FRUTAS_LIGADA, CONFIG_LOBOS, CONFIG_LOBOS_APRENDIZ, CONFIG_PADRAO  # noqa: E402
from digilab.events import AcaoPet  # noqa: E402
from digilab.policies.lobos import PoliticaLobos  # noqa: E402
from digilab.policy import Observacao, Transicao  # noqa: E402
from digilab.state import Estado  # noqa: E402

S = CONFIG_LOBOS.escala
SEM_MONTAGEM = pytest.mark.skipif("montagem" not in bv.CHAVES_CONFIG,
                                  reason="a bancada ainda nao tem a chave 'montagem' (BANCADA-MONTAGEM, chat D)")
FUMACA = json.loads((RAIZ / "experiments/configs/v2_calibracao_conjunta/fumaca.json").read_text(encoding="utf-8"))
CALIBRACAO = json.loads((RAIZ / "experiments/configs/v2_calibracao_conjunta/calibracao.json").read_text(encoding="utf-8"))


def _p(valores_por_ponto: dict) -> dict:
    boot = {"reamostragens": 400, "semente": 1, "nivel": 0.95}
    return {v: {"ic": k2.ic(xs, boot)} for v, xs in valores_por_ponto.items()}


# ------------------------------------------------------------------ as regras (secao 3), resposta conhecida


def test_regra_menor_acima_escolhe_o_menor_que_passa():
    pontos = _p({256: [0.0, 0.01, 0.02, 0.0], 512: [0.2, 0.25, 0.3, 0.22], 768: [0.5, 0.6, 0.55, 0.52]})
    r = k2.regra_menor_acima(pontos, 0.069)
    assert r == {**r, "escolhido": 512, "fechou": True, "passam": [512, 768]}


def test_regra_menor_acima_reserva_maior_limite_inferior():
    pontos = _p({256: [0.0, 0.01, 0.02, 0.0], 512: [0.03, 0.05, 0.04, 0.06], 768: [0.02, 0.03, 0.02, 0.04]})
    r = k2.regra_menor_acima(pontos, 0.069)
    assert r["escolhido"] == 512 and not r["fechou"]
    empate = {256: {"ic": {"ic_inferior": 0.01}}, 512: {"ic": {"ic_inferior": 0.01}}}
    assert k2.regra_menor_acima(empate, 0.069)["escolhido"] == 256          # empate na reserva: o menor
    sem = {256: {"ic": {"ic_inferior": None}}, 512: {"ic": {"ic_inferior": None}}}
    assert k2.regra_menor_acima(sem, 0.0)["escolhido"] == 256


def test_regra_menor_acima_estrito_no_limiar():
    assert not k2.regra_menor_acima({0: {"ic": {"ic_inferior": 0.0}}}, 0.0)["fechou"]     # A2: "> 0", nao ">= 0"


def test_regra_do_ganho():
    p = {4: {"vidas_no_teto": 0, "razao_media": 2.9}, 8: {"vidas_no_teto": 0, "razao_media": 1.7}, 16: {"vidas_no_teto": 2, "razao_media": 1.1}}
    assert k2.regra_ganho(p)["escolhido"] == 8 and k2.regra_ganho(p)["fechou"]
    p[16]["vidas_no_teto"] = 0
    assert k2.regra_ganho(p)["escolhido"] == 16
    empate = {4: {"vidas_no_teto": 0, "razao_media": 1.5}, 8: {"vidas_no_teto": 0, "razao_media": 1.5}}
    assert k2.regra_ganho(empate)["escolhido"] == 4
    reserva = {4: {"vidas_no_teto": 3, "razao_media": 1.0}, 8: {"vidas_no_teto": 1, "razao_media": 2.0}, 16: {"vidas_no_teto": 1, "razao_media": 1.5}}
    r = k2.regra_ganho(reserva)
    assert r["escolhido"] == 16 and not r["fechou"]


def test_razao_da_deriva_e_a_da_revisao():
    derivas = [[0.1, 0.2, 0.3, 0.4], [0.3, 0.2, 0.5, 0.6]]
    assert k2.razao_deriva(derivas, 4) == pytest.approx(((0.4 + 0.6) / 2) / ((0.2 + 0.2) / 2))
    assert k2.razao_deriva([[0.0, 0.0, 0.1, 0.1]], 4) is None


def test_poder_simulado_bate_com_a_formula():
    rng = random.Random(5)
    difs = [rng.gauss(0.0, 0.2) for _ in range(200)]
    sigma = k2._sigma(difs)
    n = k2.tamanho_amostra(sigma, 0.06, 0.05 / 6, 0.8)
    assert k2.poder_formula(sigma, 0.06, n, 0.05 / 6) == pytest.approx(0.8, abs=0.01)
    assert k2.poder_simulado(difs, 0.06, n, 0.05 / 6, 2000, 7) == pytest.approx(0.8, abs=0.05)


# ------------------------------------------------------------------ modos: so testes ou calibracao; a validacao nunca


def test_modos_e_recusas():
    assert k2.modo_e_unidades(FUMACA)[0] == "fumaca"
    modo, unidades = k2.modo_e_unidades(CALIBRACAO)
    assert modo == "calibracao" and len(unidades) == 20
    assert unidades == bv.unidades_derivadas(bv.BASES_EXPERIMENTO_MAIOR["calibracao"], 4)
    with pytest.raises(bv.SementeSemPlano):
        k2.modo_e_unidades({**CALIBRACAO, "unidades": {"bases": list(bv.BASES_EXPERIMENTO_MAIOR["validacao"]), "k": 4}})
    with pytest.raises(bv.SementeSemPlano):
        k2.modo_e_unidades({**CALIBRACAO, "unidades": {"bases": [14101, 15101], "k": 4}})
    with pytest.raises(bv.SementeSemPlano):
        k2.modo_e_unidades({**CALIBRACAO, "unidades": {"bases": [14101, 14202], "k": 4}})      # parte das bases
    with pytest.raises(bv.SementeSemPlano):
        k2.modo_e_unidades({**CALIBRACAO, "plano": "docs/PLANO_ANALISE_V2_N6.md"})
    for troca in ({"unidades": {"bases": CALIBRACAO["unidades"]["bases"], "k": 5}}, {"dias": 7}, {"grades": {"ganho": [4, 8]}},
                  {"etapas": ["A1"]}, {"ponto": "L1"}, {"ponto_fixo": {"g": 256}}):
        with pytest.raises(ValueError):
            k2.modo_e_unidades({**CALIBRACAO, **troca})
    with pytest.raises(ValueError):
        k2.modo_e_unidades({**FUMACA, "desconhecida": 1})


def test_calibracao_recusa_sem_as_pecas_da_bancada():
    faltam = k2.pecas_pendentes(CALIBRACAO)
    if faltam:
        with pytest.raises(NotImplementedError):
            k2.rodar(CALIBRACAO, RAIZ / "artifacts_fumaca" / "nao_deve_existir")
        assert not (RAIZ / "artifacts_fumaca" / "nao_deve_existir").exists()


# ------------------------------------------------------------------ a sonda da informacao (etapa C): so le

E = Estado(fome=0.4, higiene=1.0, energia=1.0, humor=0.8, tick=12 * 60, tick_ultimo_cuidado=12 * 60 - 10)


class _Rng:
    def __init__(self, u):
        self.u = u

    def random(self):
        return self.u


def _comendo(w0_info: int, info: tuple) -> PoliticaLobos:
    obs = replace(Observacao.de_estado(E), fruta=0.5, frutas_cenario=(1.0, 1.0, 0.0), info_frutas=info)
    for u in (1.0 - 1e-12, 0.0, 0.5, 0.25, 0.75):
        p = PoliticaLobos(CONFIG_PADRAO, replace(CONFIG_LOBOS_APRENDIZ, w0_info=w0_info), None, CONFIG_FRUTAS_LIGADA)
        if p.agir(obs, _Rng(u)) is AcaoPet.COMER:
            p.observar(Transicao(Observacao.de_estado(E), AcaoPet.COMER, Observacao.de_estado(E)))
            return p
    raise AssertionError("nenhum u levou a comer")


def test_escolha_sem_info_so_le_e_bate_com_a_escolha_sem_informacao():
    for u in (0.05, 0.3, 0.6, 0.95):
        p = _comendo(3 * S // 4, (-1.0, 0.0, 0.0))
        antes = copy.deepcopy(p.estado_interno())
        sem, vigente = p.escolha_sem_info(["a", "b"], {"a": 0.5, "b": 0.4}, u)
        assert vigente and p.estado_interno() == antes
        # a escolha sem informacao e a de um cerebro igual com a informacao neutra
        q = _comendo(3 * S // 4, (0.0, 0.0, 0.0))
        assert sem == q.escolher_fruta(["a", "b"], {"a": 0.5, "b": 0.4}, u)
    p = _comendo(3 * S // 4, (-1.0, 0.0, 0.0))
    # com "mal" forte na fruta a, algum u escolhe diferente com e sem a informacao
    assert any(_comendo(3 * S // 4, (-1.0, 0.0, 0.0)).escolha_sem_info(["a", "b"], {"a": 0.5, "b": 0.4}, u)[0] !=
               _comendo(3 * S // 4, (-1.0, 0.0, 0.0)).escolher_fruta(["a", "b"], {"a": 0.5, "b": 0.4}, u) for u in (0.1, 0.2, 0.3, 0.4))
    assert _comendo(0, (-1.0, 0.0, 0.0)).escolha_sem_info(["a", "b"], {"a": 0.5, "b": 0.4}, 0.3) == (None, False)   # sem w0_info
    sem_vig = _comendo(3 * S // 4, (0.0, 0.0, 1.0)).escolha_sem_info(["a", "b"], {"a": 0.5, "b": 0.4}, 0.3)
    assert sem_vig[1] is False                                       # informacao so na fruta ausente: nao vigente nesta escolha
    del p


# ------------------------------------------------------------------ fumaca das cinco etapas


@SEM_MONTAGEM
def test_fumaca_das_cinco_etapas(tmp_path):
    cfg = {**FUMACA, "dias": 2, "orcamento": 32, "sonda": {"estados": 8, "amostras": 8, "semente": 101},
           "bootstrap": {"reamostragens": 200, "semente": 101, "nivel": 0.95},
           "grades": {"g": [256, 512], "w0_pedido": [512], "ganho": [4, 8], "w0_info": [512]}}
    r = k2.rodar(cfg, tmp_path)
    assert r["modo"] == "fumaca" and set(r["ponto"]) == {"g", "w0_pedido", "ganho", "w0_info"}
    for e in k2.ETAPAS:
        assert (tmp_path / e / "resultado.json").is_file()
    for f in ("escolha.json", "adendo.json", "meta.json"):
        assert (tmp_path / f).is_file()
    assert r["A1"]["escolhido"] in (256, 512) and r["B"]["escolhido"] in (4, 8)
    # o ponto de cada etapa e o que as seguintes usaram
    meta_c = json.loads((tmp_path / "C" / "w512" / "meta.json").read_text(encoding="utf-8"))
    assert meta_c["cfg_lobos"]["memoria_ganho"] == r["ponto"]["g"]
    assert meta_c["config"]["consequencia"]["ganho"] == r["ponto"]["ganho"]
    d = r["D"]
    assert d["vidas"] == 2 * (18 + 9 + 2 + 2 + 4 + 6 + 3)              # a secao 4: 44 por unidade (as ablacoes como vidas de P1)
    contratos = {k: v["passa"] for k, v in d["contratos"].items()}
    assert all(v for k, v in contratos.items() if k != "K4_dono_julga_fruta")
    assert set(d["tamanho_amostra"]["por_contraste"]) == {c.nome for c in k2.em.PRIMARIOS}
    ad = json.loads((tmp_path / "adendo.json").read_text(encoding="utf-8"))
    assert ad["parametros"]["B"]["escolhido"] == r["ponto"]["ganho"] and ad["unidades_calibracao"] == 2
    # as vidas da bancada foram gravadas e rejogadas do disco (G1); o log no disco e o da vida
    vidas = list((tmp_path / "D" / "principal" / "vidas").glob("*.jsonl"))
    assert len(vidas) == 2 * (18 + 9)


# ------------------------------------------------------------------ os bracos completos do cerebro A (K-1) na bancada


@SEM_MONTAGEM
def test_bracos_completos_do_cerebro_a():
    """A tabela da secao 1 (K-1) na montagem completa: memoria com o g em P1-P3, canais em P1 e P2 (nao no P3), w0_info so nos P2."""
    b = bv.bancada_da_config({"dias": 2, "orcamento": 16, "ponto": "T3", "montagem": "completa", "julgamento_fruta": True,
                              "lobos": {"memoria_ganho": S // 2, "w0_info": S // 2}, "consequencia": {"canais_ligados": False}})
    for logico, rotulo in k2.BRACO_COMPLETO.items():
        pol = b.politica(bv.EspecVida("atencioso", rotulo, 101, None, "descasado"))
        c = pol.cerebro
        if logico == "P0":
            assert c._memoria is None and not c._aprende
            continue
        assert c._memoria is not None and c.cl.memoria_ganho == S // 2 and c._aprende
        assert pol.cfg_consequencia.canais_ligados == (logico != "P3")
        assert (c._peso_info is not None) == logico.startswith("P2")
    assert k2.pecas_pendentes({"canais": True}) == []
