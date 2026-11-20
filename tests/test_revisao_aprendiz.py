"""V2, REVISAO-APRENDIZ (docs/TAREFA_V2_REVISAO_APRENDIZ.md): as alavancas atras de campos, com o padrao de hoje byte a byte.

- o traco de elegibilidade (ConfigLobos.traco_decisoes, traco_fator): o sinal chega as decisoes anteriores com lambda**k; sem traco,
  o credito de hoje; o chamado fica preso ao chamado;
- a bancada le as chaves "lobos" e "frutas" da config (o teto, o traco, o w_fruta e as ofertas); sem elas, a bancada de sempre;
- G1 com as alavancas ligadas. Sementes so dos testes (101...505).
"""
from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
from digilab.config import (CONFIG_CONSEQUENCIA, CONFIG_FRUTAS_LIGADA, CONFIG_LOBOS, CONFIG_LOBOS_APRENDIZ,  # noqa: E402
                            CONFIG_PADRAO)
from digilab.events import AcaoPet, AcaoUsuario  # noqa: E402
from digilab.policies import lobos  # noqa: E402
from digilab.policies.lobos import PoliticaLobos, div_arred, validar_parametros_lobos  # noqa: E402
from digilab.policy import Observacao, Transicao  # noqa: E402
from digilab.state import Estado  # noqa: E402

S = CONFIG_LOBOS.escala
TRACO = replace(CONFIG_LOBOS_APRENDIZ, traco_decisoes=2, traco_fator=S // 2)


class _Rng:
    def __init__(self, u):
        self.u = u

    def random(self):
        return self.u


def _espiao(monkeypatch) -> list:
    chamadas = []
    original = lobos.Aprendiz._aplicar_sinal

    def espiao(self, registro, f_S, consequencia=False):
        chamadas.append((id(registro), f_S, consequencia))
        original(self, registro, f_S, consequencia)
    monkeypatch.setattr(lobos.Aprendiz, "_aplicar_sinal", espiao)
    return chamadas


def _decidir(p, tick: int, fome: float = 0.4) -> dict:
    """Uma decisao com sorteio (fome moderada: comer x chamar), observada pela via do dono; devolve o registro."""
    e = Estado(fome=fome, higiene=1.0, energia=1.0, humor=0.8, tick=tick, tick_ultimo_cuidado=0)
    obs = Observacao.de_estado(e)
    a = p.agir(obs, _Rng(0.0))
    reg = p._registro_decisao
    p.observar(Transicao(obs, a, obs))
    return reg


def test_registro_e_padrao():
    validar_parametros_lobos()
    assert CONFIG_LOBOS.traco_decisoes == 0 and CONFIG_LOBOS.traco_fator == 0
    for ruim in ({"traco_decisoes": 2, "traco_fator": 0}, {"traco_decisoes": 2, "traco_fator": S},
                 {"traco_decisoes": -1}, {"traco_decisoes": 2, "traco_fator": 0.5}):
        with pytest.raises((ValueError, TypeError)):
            PoliticaLobos(CONFIG_PADRAO, replace(CONFIG_LOBOS_APRENDIZ, **ruim))


def test_elogio_chega_as_decisoes_anteriores_com_lambda(monkeypatch):
    chamadas = _espiao(monkeypatch)
    p = PoliticaLobos(CONFIG_PADRAO, TRACO)
    regs = [_decidir(p, 15 * (k + 1)) for k in range(4)]
    p.receber_acao_dono(AcaoUsuario.ELOGIAR, 15 * 4 + 1)
    f = round(CONFIG_LOBOS_APRENDIZ.recompensa_elogio * S)
    assert chamadas == [(id(regs[3]), f, False), (id(regs[2]), div_arred(f * (S // 2), S), False),
                        (id(regs[1]), div_arred(f * (S // 2) ** 2, S ** 2), False)]
    assert p.estado_interno()["aprendizado"]["recompensas"]["traco"] == 2


def test_sem_traco_o_credito_de_hoje(monkeypatch):
    chamadas = _espiao(monkeypatch)
    p = PoliticaLobos(CONFIG_PADRAO, CONFIG_LOBOS_APRENDIZ)
    regs = [_decidir(p, 15 * (k + 1)) for k in range(4)]
    p.receber_acao_dono(AcaoUsuario.ELOGIAR, 61)
    assert chamadas == [(id(regs[3]), S, False)] and "traco" not in p.estado_interno()["aprendizado"]["recompensas"]


def test_consequencia_com_traco_e_o_chamado_preso(monkeypatch):
    chamadas = _espiao(monkeypatch)
    p = PoliticaLobos(CONFIG_PADRAO, TRACO)
    e = Estado(fome=0.4, higiene=1.0, energia=1.0, humor=0.8, tick=15, tick_ultimo_cuidado=0)
    regs = []
    for k in range(3):
        obs = Observacao.de_estado(replace(e, tick=15 * (k + 1)))
        a = p.agir(obs, _Rng(0.0))
        regs.append(p._registro_decisao)
        p.observar_consequencia(Transicao(obs, a, obs), 100, CONFIG_CONSEQUENCIA)
    assert chamadas[-3:] == [(id(regs[2]), 100, True), (id(regs[1]), 50, True), (id(regs[0]), 25, True)]
    # o chamado (latencia) credita so o pedido, sem traco
    chamadas.clear()
    p2 = PoliticaLobos(CONFIG_PADRAO, TRACO)
    _decidir(p2, 15)
    _decidir(p2, 30)
    obs = Observacao.de_estado(Estado(fome=0.2, tick=45, tick_ultimo_cuidado=0))     # pedido de necessidade: chamar
    assert p2.agir(obs, _Rng(0.0)) is AcaoPet.CHAMAR_ATENCAO
    reg = p2._registro_decisao
    p2.observar(Transicao(obs, AcaoPet.CHAMAR_ATENCAO, obs))
    p2.receber_acao_dono(AcaoUsuario.ALIMENTAR, 50)
    assert [c for c in chamadas if c[0] != id(reg)] == []


# ------------------------------------------------------------------ a bancada


def test_bancada_sem_chaves_e_a_de_sempre():
    base = {"dias": 3, "orcamento": 48}
    assert bv.bancada_da_config(base) == bv.Bancada(3, 48)
    b = bv.bancada_da_config({**base, "lobos": {"teto": 4096, "traco_decisoes": 4, "traco_fator": 768},
                              "frutas": {"w_fruta": 12.0, "horarios_oferta": [540, 630, 720]}})
    assert b.cfg_lobos == replace(CONFIG_LOBOS_APRENDIZ, teto=4096, traco_decisoes=4, traco_fator=768)
    assert b.cfg_frutas == replace(CONFIG_FRUTAS_LIGADA, w_fruta=12.0, horarios_oferta=(540, 630, 720))


@pytest.mark.parametrize("lobos_cfg,frutas_cfg", [({"teto": 4096}, {}), ({"traco_decisoes": 4, "traco_fator": 768}, {}),
                                                  ({}, {"w_fruta": 12.0}),
                                                  ({}, {"horarios_oferta": [540, 630, 720, 810, 900, 990, 1080, 1170]})])
def test_g1_com_cada_alavanca(lobos_cfg, frutas_cfg, tmp_path):
    cfg = {"bracos": ["P0", "P1", "P3"], "donos": ["atencioso"], "unidades": {"bases": [101], "k": 2},
           "mundos": ["casado_frutas", "descasado"], "dias": 3, "orcamento": 48,
           "sonda": {"estados": 8, "amostras": 8, "semente": 101}, "bootstrap": {"reamostragens": 100, "semente": 101, "nivel": 0.95}}
    if lobos_cfg:
        cfg["lobos"] = lobos_cfg
    if frutas_cfg:
        cfg["frutas"] = frutas_cfg
    r = bv.rodar(cfg, tmp_path)                       # rodar rejoga toda vida do disco bit a bit (falha alto se divergir)
    assert len(r["vidas"]) == 12
    if "horarios_oferta" in frutas_cfg:
        for v in r["vidas"].values():               # uma oferta em cada um dos 8 horarios de cada dia
            ticks = {e.tick for e in v.motor.log if e.tipo == "acao_usuario" and str(e.valor).startswith("oferecer")}
            assert len(ticks) == 8 * 3


# ------------------------------------------------------------------ o orquestrador (fumaca nas sementes dos testes)


def test_orquestrador_fumaca(tmp_path):
    import json
    import run_revisao_aprendiz as rr
    cfg = json.loads((RAIZ / "experiments/configs/v2_revisao/calibracao.json").read_text(encoding="utf-8"))
    assert rr.carregar(RAIZ / "experiments/configs/v2_revisao/calibracao.json")["bases"] == list(rr.BASES_REVISAO)
    outra = tmp_path / "outra.json"                  # so as bases da revisao (o plano, secao 2)
    outra.write_text(json.dumps({**cfg, "bases": [101, 202, 303, 404, 505]}), encoding="utf-8")
    with pytest.raises(ValueError):
        rr.carregar(outra)
    fumaca = {**cfg, "bases": [101, 202], "k": 1, "dias": 4, "orcamento": 64,
              "sonda": {"estados": 8, "amostras": 8, "semente": 101}, "bootstrap": {"reamostragens": 200, "semente": 101, "nivel": 0.95},
              "pontos": {"base": {}, "T1": {"lobos": {"teto": 2048}}, "J1": {"lobos": {"traco_decisoes": 2, "traco_fator": 512}},
                         "X1": {"frutas": {"w_fruta": 12.0}}}}
    rec = rr.executar(fumaca, tmp_path, {"config": "fumaca"})
    for f in ("meta.json", "avaliacao.json", "diagnostico.json", "recomendacao.json", "varredura.jsonl", "base/resultado.json"):
        assert (tmp_path / f).is_file()
    assert set(rec["por_alavanca"]) == {"teto", "janela", "exposicao"}
    res = json.loads((tmp_path / "base/resultado.json").read_text(encoding="utf-8"))
    vida = next(x for x in res["vidas"].values() if x["braco"] == "P1")
    assert 0.0 <= vida["m1_decidiu"] <= 1.0 and "consequencia" in vida["recompensas"]
