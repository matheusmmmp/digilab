"""V2, N5, lado do mundo: a informacao do dono sobre as frutas e a medida N1 da saciedade (docs/TAREFA_V2_N5_MUNDO.md, secao 4).

G1: replay pelo log bit a bit com informacoes.
G2: sem informacao no log (chave desligada, ou ligada sem informante) = a vida das frutas de hoje, byte a byte; e a vida da validacao do
    N4 gravada em disco, rejogada com o codigo novo, da as medidas gravadas.
O evento nao altera o estado nem o orcamento, nao e contato e nao chega ao aprendiz como sinal; fica so para a percepcao, por uma janela.
N1: em dados sinteticos com a preferencia andando junto com a fome, a medida nova recupera a queda especifica conhecida e a medida antiga
    (sem a preferencia) nao.
"""
from __future__ import annotations

import json
import random
import sys
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.ambiente import MotorAmbiente  # noqa: E402
from digilab.config import (CONFIG_FRUTAS, CONFIG_FRUTAS_LIGADA, CONFIG_INFORMACAO, CONFIG_INFORMACAO_LIGADA,  # noqa: E402
                            CONFIG_PADRAO, ConfigFrutas)
from digilab.donos import criar_dono  # noqa: E402
from digilab.events import ACOES_FRUTAS, ACOES_INFORMACAO, FRUTAS, AcaoUsuario, LogDeEventos, informacao_de, informar  # noqa: E402
from digilab.frutas import (DonoInformante, InformacaoSemChave, MotorFrutas, OfertasFrutas, PoliticaInstintoFrutas,  # noqa: E402
                            fabricas_frutas, reproduzir_frutas, simular_vida_frutas)
from digilab.metrics import saciedade_especifica, saciedade_especifica_n1  # noqa: E402
from digilab.policy import Observacao, PoliticaInstinto  # noqa: E402
from digilab.protocol import informacao_nao_referendados, validar_parametros_informacao  # noqa: E402

DONOS = ("atencioso", "relapso", "aleatorio", "incoerente")
SEMENTES = (11, 22, 33)                 # so dos testes: nenhuma faixa reservada
CF, CI = CONFIG_FRUTAS_LIGADA, CONFIG_INFORMACAO_LIGADA
CHAVES_INFO = ("informacoes", "decisoes_com_informacao")


def _nucleo(m) -> tuple:
    return (m._estado, tuple(m.acoes_recentes(10**9)), m._rng_politica.getstate(), m._rng_ambiente.getstate(),
            m._rng_fruta.getstate())


def _vida(dono: str, s: int, ci=CI, modo: str | None = "certo", dias: int = 3, orc: int = 48, cf: ConfigFrutas = CF):
    fp, fm = fabricas_frutas(cfg_frutas=cf, cfg_informacao=ci)
    inf = DonoInformante.do_genoma(modo, s, cf) if modo else None
    v = simular_vida_frutas(f"{dono}-n5", criar_dono(dono), fp(), s, dias, orc, fm, OfertasFrutas(cf), rotulo_dono=dono, informante=inf)
    return v, fp, fm, inf


def _motor(ci=CI, s: int = 5) -> MotorFrutas:
    fp, fm = fabricas_frutas(cfg_frutas=CF, cfg_informacao=ci)
    return fm(fp(CONFIG_PADRAO), CONFIG_PADRAO, s)


# ------------------------------------------------------------------ registro e enum


def test_parametros_registrados_e_enum_no_fim():
    validar_parametros_informacao()
    assert informacao_nao_referendados() == ["ConfigInformacao.janela_min"] and CONFIG_INFORMACAO.ligada is False
    assert list(AcaoUsuario)[-6:] == list(ACOES_INFORMACAO) and list(AcaoUsuario)[17:20] == list(ACOES_FRUTAS)
    assert [informacao_de(a) for a in ACOES_INFORMACAO] == [(f, c) for f in FRUTAS for c in ("bem", "mal")]
    assert informar("b", "mal") is AcaoUsuario.INFORMAR_FRUTA_B_MAL
    with pytest.raises(ValueError):
        informar("d", "bem")
    from digilab.state import Estado
    assert Observacao.de_estado(Estado()).info_frutas == (0.0, 0.0, 0.0)


def test_chaves_falham_alto():
    with pytest.raises(InformacaoSemChave):
        _motor(CONFIG_INFORMACAO).observar(AcaoUsuario.INFORMAR_FRUTA_A_BEM)
    with pytest.raises(ValueError):
        MotorAmbiente(PoliticaInstinto(), CONFIG_PADRAO, 5).observar(AcaoUsuario.INFORMAR_FRUTA_A_BEM)
    with pytest.raises(ValueError):
        fp, fm = fabricas_frutas(cfg_frutas=CONFIG_FRUTAS, cfg_informacao=CI)
        fm(fp(CONFIG_PADRAO), CONFIG_PADRAO, 5)


# ------------------------------------------------------------------ G1


@pytest.mark.parametrize("modo", ("certo", "errado"))
@pytest.mark.parametrize("dono", DONOS)
def test_g1_replay_bit_a_bit(dono, modo):
    for s in SEMENTES:
        v, fp, fm, _ = _vida(dono, s, modo=modo)
        assert v.informacoes > 0
        r = reproduzir_frutas(LogDeEventos.de_jsonl(v.motor.log.para_jsonl()), fp, semente=s, fabrica_motor=fm)
        assert _nucleo(r) == _nucleo(v.motor) and r.resumo_frutas() == v.motor.resumo_frutas() and r.estado() == v.motor.estado()


# ------------------------------------------------------------------ G2


@pytest.mark.parametrize("dono", DONOS)
def test_g2_sem_informacao_no_log_igual_a_vida_das_frutas(dono):
    for s in SEMENTES:
        a, _, _, _ = _vida(dono, s, ci=CONFIG_INFORMACAO, modo=None)
        b, _, _, _ = _vida(dono, s, ci=CI, modo=None)
        assert a.motor.log.para_jsonl() == b.motor.log.para_jsonl() and _nucleo(a.motor) == _nucleo(b.motor)
        rb = {k: v for k, v in b.motor.resumo_frutas().items() if k not in CHAVES_INFO}
        assert a.motor.resumo_frutas() == rb and b.motor.informacoes == []
        assert "informacao" not in a.motor.estado()


def test_g2_a_vida_gravada_do_n4_reproduz_as_medidas():
    """A vida `atencioso-frutas@11101` da validacao do N4 (em disco), rejogada com o codigo novo e a informacao desligada, da as medidas
    gravadas em artifacts_v2_n4/validacao/vidas.json."""
    base = RAIZ / "artifacts_v2_n4" / "validacao"
    log = LogDeEventos.de_jsonl((base / "ponto" / "vidas" / "atencioso-frutas@11101.jsonl").read_text(encoding="utf-8"))
    gravado = json.loads((base / "vidas.json").read_text(encoding="utf-8"))["frutas"]["atencioso-frutas@11101"]
    cf = replace(CF, w_fruta=6.0, k_saciedade=1.0, duracao_min=120)
    fp, fm = fabricas_frutas(cfg_frutas=cf, cfg_informacao=CONFIG_INFORMACAO)
    r = reproduzir_frutas(log, fp, semente=11101, fabrica_motor=fm)
    rf = r.resumo_frutas()
    assert rf["contagem"] == gravado["contagem"] and r._estado.saude == gravado["saude_final"]
    assert [[c["avaliacao"], c["consumo_recente_antes"], c["fome_antes"]] for c in rf["consumos"]] == gravado["consumos"]
    assert rf["genoma"] == gravado["genoma"] and rf["incentivo"] == gravado["incentivo_final"]


# ------------------------------------------------------------------ o evento nao toca estado, orcamento nem aprendiz


@pytest.mark.parametrize("dono", DONOS)
def test_informar_nao_muda_a_vida_nem_o_orcamento(dono):
    """Com o instinto (que nao le a informacao), a vida com o informante e a vida sem ele sao a mesma: estado, acoes e rngs; o canal
    fecha o mesmo orcamento; so o log ganha as informacoes."""
    for s in SEMENTES:
        com, _, _, _ = _vida(dono, s, modo="certo")
        sem, _, _, _ = _vida(dono, s, modo=None)
        assert _nucleo(com.motor) == _nucleo(sem.motor) and com.interacoes == sem.interacoes == 48
        n_com = sum(1 for e in com.motor.log if e.tipo == "acao_usuario")
        n_sem = sum(1 for e in sem.motor.log if e.tipo == "acao_usuario")
        assert n_com == n_sem + com.informacoes and com.informacoes > 0


class _Espiao(PoliticaInstintoFrutas):
    def __init__(self, *a, **k) -> None:
        super().__init__(*a, **k)
        self.recebidas: list = []

    def receber_acao_dono(self, acao, tick) -> None:
        self.recebidas.append(acao)


def test_informar_nao_e_contato_nem_chega_ao_aprendiz():
    pol = _Espiao(CONFIG_PADRAO, None, CF)
    m = MotorFrutas(pol, CONFIG_PADRAO, 5, cfg_frutas=CF, cfg_informacao=CI, obediencia_desligada=True)
    m.avancar(30)
    antes = m._estado
    m.observar(AcaoUsuario.INFORMAR_FRUTA_A_MAL)
    assert m._estado == antes and pol.recebidas == []
    m.observar(AcaoUsuario.ALIMENTAR)
    assert pol.recebidas == [AcaoUsuario.ALIMENTAR]                 # o gancho funciona; a informacao e que nao passa por ele


def test_percepcao_por_janela_renova_e_troca():
    ci = replace(CI, janela_min=60)
    m = _motor(ci)
    vistos = []
    pol = m.politica._pf

    class _Olho:
        def __init__(self, interna):
            self.interna = interna

        def agir(self, obs, rng):
            vistos.append((m._estado.tick, obs.info_frutas))
            return self.interna.agir(obs, rng)

        def __getattr__(self, n):
            return getattr(self.interna, n)

    m.politica._pf = _Olho(pol)
    m.avancar(1)
    m.observar(AcaoUsuario.INFORMAR_FRUTA_B_MAL)
    assert m.estado()["informacao"] == {"a": 0.0, "b": -1.0, "c": 0.0}
    m.avancar(30)
    m.observar(AcaoUsuario.INFORMAR_FRUTA_B_BEM)                  # o contrario troca o valor e renova o prazo
    assert m.estado()["informacao"]["b"] == 1.0 and m.informacao["b"][1] == 31 + 60
    m.avancar(120)
    assert m.estado()["informacao"] == {"a": 0.0, "b": 0.0, "c": 0.0}
    na_janela = [v for t, v in vistos if 1 <= t < 31]
    depois = [v for t, v in vistos if 31 <= t < 91]
    fora = [v for t, v in vistos if t >= 91]
    assert na_janela and all(v == (0.0, -1.0, 0.0) for v in na_janela)
    assert depois and all(v == (0.0, 1.0, 0.0) for v in depois)
    assert fora and all(v == (0.0, 0.0, 0.0) for v in fora)
    assert [i["conteudo"] for i in m.informacoes] == ["mal", "bem"]


def test_informante_certo_e_errado_nos_mesmos_ticks_com_conteudo_oposto():
    _, _, _, certo = _vida("atencioso", 11, modo="certo")
    _, _, _, errado = _vida("atencioso", 11, modo="errado")
    assert [(t, f) for t, f, _ in certo.feitas] == [(t, f) for t, f, _ in errado.feitas] and certo.feitas
    assert all(c1 != c2 for (_, _, c1), (_, _, c2) in zip(certo.feitas, errado.feitas))
    inf = DonoInformante("certo", {"a": -0.1, "b": 0.0, "c": 0.2})
    assert [inf.conteudo(f) for f in FRUTAS] == ["mal", "bem", "bem"]
    assert [DonoInformante("errado", inf.efeito_humor).conteudo(f) for f in FRUTAS] == ["bem", "mal", "mal"]
    with pytest.raises(ValueError):
        DonoInformante("sorteado", inf.efeito_humor)
    with pytest.raises(ValueError):           # N5-ACOPLADO: o acoplado existe, mas so pelo construtor `acoplado`
        DonoInformante("acoplado", inf.efeito_humor).acoes_do_passo(15, [])


# ------------------------------------------------------------------ N1


def _sinteticos(n: int = 400, k: float = 0.6, semente: int = 7):
    """avaliacao = preferencia - k x recente (sem a fome); a fome anda junto com a preferencia, como no mundo (come-se mais o que se prefere)"""
    rng = random.Random(semente)
    linhas = []
    for _ in range(n):
        pref = rng.uniform(0.2, 1.0)
        recente = rng.uniform(0.0, 0.8) * pref                     # as preferidas acumulam mais consumo recente
        fome = min(1.0, 0.3 + 0.5 * pref + rng.uniform(-0.1, 0.1))
        linhas.append((pref - k * recente, pref, recente, fome))
    return linhas


def test_n1_recupera_a_queda_especifica_sem_confundir_com_a_preferencia():
    k = 0.6
    dados = _sinteticos(k=k)
    novo = saciedade_especifica_n1(dados)
    assert novo["beta_recente"] == pytest.approx(-k, abs=1e-9)
    assert novo["beta_fome"] == pytest.approx(0.0, abs=1e-9) and novo["beta_pref"] == pytest.approx(1.0, abs=1e-9)
    assert novo["queda_por_unidade"] == pytest.approx(k, abs=1e-9)
    antigo = saciedade_especifica([(a, r, f) for a, _, r, f in dados])
    assert abs(antigo["beta_fome"]) > 0.1                          # sem a preferencia, a fome leva a culpa


def test_n1_com_ruido_e_falha_alto():
    rng = random.Random(3)
    dados = [(a + rng.gauss(0.0, 0.02), p, r, f) for a, p, r, f in _sinteticos(n=600, k=0.4, semente=11)]
    novo = saciedade_especifica_n1(dados)
    assert novo["beta_recente"] == pytest.approx(-0.4, abs=0.05) and abs(novo["beta_fome"]) < 0.05
    with pytest.raises(ValueError):
        saciedade_especifica_n1(dados[:4])
