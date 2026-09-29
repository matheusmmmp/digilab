"""educacao-v1, Fase 2 parte 7: personas de dono e modo livre gravado."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "tools"))

from digilab.config import CONFIG_EDUCACAO_LIGADA  # noqa: E402
from digilab.donos_educacao import simular_vida_educacao  # noqa: E402
from digilab.educacao import fabricas_educacao, reproduzir_educacao  # noqa: E402
from digilab.events import LogDeEventos  # noqa: E402
from digilab.evolucao import ovo  # noqa: E402
from digilab.personas import PersonaInvalida, carregar_lote, validar_persona  # noqa: E402
from digilab.temperamento import sortear  # noqa: E402
from digilab.treino import reproduzir_com_feedback  # noqa: E402
from servidor.fala_llm import RespostaProvedor  # noqa: E402

LOTE = RAIZ / "experiments" / "personas" / "exemplo_manual.json"
S = 4301


@pytest.fixture(scope="module")
def personas():
    ps, sha = carregar_lote(LOTE)
    assert len(sha) == 64
    return {p.nome: p for p in ps}


def _base():
    return json.loads(LOTE.read_text(encoding="utf-8"))["personas"][0]


@pytest.mark.parametrize("mexe", [
    lambda d: d.pop("limiar_cuidado"),
    lambda d: d.update(extra=1),
    lambda d: d.update(prob_ceder_petisco=1.2),
    lambda d: d.update(prob_atender_janela=True),
    lambda d: d.update(horarios=[[10, 10]]),
    lambda d: d.update(horarios=[[10, 25]]),
    lambda d: d.update(horarios=[]),
    lambda d: d.update(nome="Com Espaco"),
    lambda d: d.update(perfil_treino="relaxado"),
])
def test_persona_invalida_falha_alto(mexe):
    d = _base()
    validar_persona(d)
    mexe(d)
    with pytest.raises(PersonaInvalida):
        validar_persona(d)


def _vida(braco, persona=None, decisor=None, dias=3):
    esp, _ = ovo(S)
    return simular_vida_educacao(braco, S, dias, esp, sortear(S), persona=persona, decisor_externo=decisor)


def test_persona_vive_com_o_mesmo_orcamento_e_rejoga(personas):
    ref = _vida("atencioso")
    vidas = {n: _vida(f"persona:{n}", p) for n, p in personas.items()}
    assert {v.interacoes for v in vidas.values()} == {ref.interacoes}
    esp, _ = ovo(S)
    fp, fm = fabricas_educacao(S, esp, sortear(S), ce=CONFIG_EDUCACAO_LIGADA)
    for v in vidas.values():
        r = reproduzir_educacao(v.motor.log, fp, semente=S, fabrica_motor=fm)
        assert r.estado() == v.motor.estado() and r.historico_janelas == v.motor.historico_janelas
    atend = {n: sum(v.dono.respostas.values()) for n, v in vidas.items()}
    assert atend["treinador-rigido"] > atend["plantonista"]
    assert vidas["treinador-rigido"].dono.respostas["petisco"] == 0


def test_braco_de_persona_com_nome_errado(personas):
    with pytest.raises(KeyError):
        _vida("persona:outra", personas["plantonista"])


class _DecisorFixo:
    def __init__(self, valor=True):
        self.valor, self.chamadas = valor, 0

    def __call__(self, ctx):
        assert ctx["ponto"] == "slot_falso" and 0 < ctx["fracao_falso"] <= 1
        self.chamadas += 1
        return self.valor, {"fonte": "teste", "versao": "0"}


def test_modo_livre_grava_e_replay_le_do_log():
    dec = _DecisorFixo(True)
    v = _vida("permissivo", decisor=dec)
    m = v.motor
    decs = [e for e in m.log if e.tipo == "decisao_externa"]
    assert dec.chamadas == len(decs) > 0 and m.modo_livre
    esp, _ = ovo(S)
    fp, fm = fabricas_educacao(S, esp, sortear(S), ce=CONFIG_EDUCACAO_LIGADA)
    r = reproduzir_educacao(m.log, fp, semente=S, fabrica_motor=fm)
    assert r.estado() == m.estado() and r.historico_janelas == m.historico_janelas and r.modo_livre
    assert r.vinculo.serie == m.vinculo.serie
    # sempre-falso gera mais manha que a rng
    assert m.contagem["falsos"] > _vida("permissivo").motor.contagem["falsos"]
    # log sem uma decisao: o replay falha alto; com decisor na fabrica tambem; o replay antigo recusa
    i = next(k for k, e in enumerate(m.log) if e.tipo == "decisao_externa")
    faltando = LogDeEventos([e for k, e in enumerate(m.log) if k != i])
    with pytest.raises(ValueError):
        reproduzir_educacao(faltando, fp, semente=S, fabrica_motor=fm)
    _, fm_dec = fabricas_educacao(S, esp, sortear(S), ce=CONFIG_EDUCACAO_LIGADA, decisor_externo=dec)
    with pytest.raises(ValueError):
        reproduzir_educacao(m.log, fp, semente=S, fabrica_motor=fm_dec)
    with pytest.raises(ValueError):
        reproduzir_com_feedback(m.log, fp, semente=S, fabrica_motor=fm)


def test_sem_decisor_nada_de_evento_nem_modo_livre():
    m = _vida("permissivo").motor
    assert not m.modo_livre and all(e.tipo != "decisao_externa" for e in m.log)


def test_decisor_entropia_devolve_bool():
    from decisor_livre import DecisorEntropia
    d = DecisorEntropia()
    ctx = {"fracao_falso": 0.5}
    vals = {d(ctx)[0] for _ in range(200)}
    assert vals == {True, False}
    assert d({"fracao_falso": 0.0})[0] is False


class _ProvedorFalso:
    """responde dentro das faixas e do perfil pedidos (lidos do pedido); a primeira resposta e invalida"""
    tem_custo = False
    nome = "falso"

    def __init__(self):
        self.n = 0

    def gerar(self, sistema, pedido, esquema, semente):
        import re
        self.n += 1
        if self.n == 1:
            return RespostaProvedor("{\"nome\": \"quebrada\"}", True, "fim", "falso-1")
        d = _base()
        d["nome"] = "gerada"                           # repetido de proposito: vira gerada-2, gerada-3
        for k, a, b in re.findall(r"(prob_\w+|limiar_cuidado) entre ([\d.]+) e ([\d.]+)", pedido):
            d[k] = round((float(a) + float(b)) / 2, 3)
        d["perfil_treino"] = re.search(r"perfil_treino = (\w+)", pedido).group(1)
        return RespostaProvedor(json.dumps(d), True, "fim", "falso-1")


def test_gerador_de_personas_valida_refaz_desduplica_e_varia():
    from gerar_personas import esquema_json, gerar, plano
    assert set(esquema_json()["required"]) == set(_base())
    ps, modelo, planos = gerar(_ProvedorFalso(), None, 6, 1)
    assert modelo == "falso-1" and [p["nome"] for p in ps] == ["gerada", "gerada-2", "gerada-3", "gerada-4", "gerada-5", "gerada-6"]
    for p in ps:
        validar_persona(p)
    assert {p["perfil_treino"] for p in ps} == {"atencioso", "exigente"}
    assert len({json.dumps(p["faixas"], sort_keys=True) for p in plano(81, 7)}) == 81     # fatorial completo
    assert len({p["rotina"] for p in plano(16, 7)}) == 16


def test_horario_que_atravessa_a_meia_noite():
    d = _base()
    d["horarios"] = [[22, 2], [18, 0]]
    p = validar_persona(d)
    assert [h for h in range(24) if p.presente(h)] == [0, 1, 18, 19, 20, 21, 22, 23]
