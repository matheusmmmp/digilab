"""V2, corpo, etapa 6, a parte do motor (docs/TAREFA_V2_CORPO_DRIVES.md, secoes 7, 8 e 14; o contrato dos ganchos combinado com o B).

O tapa (`AcaoUsuario.TAPA`, no fim do enum), o repasse dele ao cerebro, o carinho pelo corpo (`mudanca_no_corpo`), o tedio pela atividade,
os `vistos_novos` do mundo para a curiosidade e o `DonoComGestos`. O corpo e o real (o do B, #247), por um espiao (`CorpoEspiao`) que so
anota as chamadas do motor. O G2 (desligado, as vidas de hoje byte a byte) e o dos gabaritos de sempre, que a suite confere (test_corpo,
test_corpo_no_mundo, test_mundo e os demais); aqui ficam o enum, o tapa sem a chave e o G1 com os gestos. So as sementes dos testes.
"""
from __future__ import annotations

import json
import sys
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab import motor_corpo  # noqa: E402
from digilab.ambiente import DonoComBola, MotorAmbiente, PoliticaInstintoBola  # noqa: E402
from digilab.config import (CONFIG_BOLA_LIGADA, CONFIG_CORPO_DRIVES, CONFIG_FRUTAS_LIGADA, CONFIG_MUNDO_LIGADA,  # noqa: E402
                            CONFIG_PADRAO, ConfigCorpo)
from digilab.corpo import Corpo  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.educacao import reproduzir_educacao  # noqa: E402
from digilab.events import (ACOES_CORPO, ACOES_PEDIDO, AcaoPet, AcaoUsuario, LogDeEventos, acao_usuario,  # noqa: E402
                            avanco)
from digilab.frutas import MotorFrutas, OfertasFrutas, PoliticaInstintoFrutas, simular_vida_frutas  # noqa: E402
from digilab.gestos import (CanalComGestos, CanalMundoComGestos, DonoComGestos, SemGesto,  # noqa: E402
                            simular_vida_gestos)
from digilab.instinto_mundo import PoliticaInstintoMundo  # noqa: E402
from digilab.motor_corpo import GestoSemChave, PercepcaoCorpo, com_corpo  # noqa: E402
from digilab.mundo import DonoComLugar, MotorMundo, reproduzir_mundo, simular_vida_mundo  # noqa: E402
from digilab.policy import PoliticaInstinto  # noqa: E402
from digilab.treino import MotorComFeedback, reproduzir_com_feedback, simular_vida  # noqa: E402

CFG = CONFIG_PADRAO
CM = CONFIG_MUNDO_LIGADA
DIAS = 3
ORC = 16 * DIAS


# ================================================================== o corpo de teste (o contrato com o B)
class CorpoEspiao(Corpo):
    """O Corpo real (o do B, etapa 6) que so anota as chamadas do motor: os gestos, a atividade e a novidade. Nada muda na quimica."""

    def __init__(self, *a, **kw) -> None:
        super().__init__(*a, **kw)
        self.chamadas = []

    def acao_dono(self, acao):
        self.chamadas.append(("dono", acao.value))
        super().acao_dono(acao)

    def atividade(self, nome):
        self.chamadas.append(("atividade", nome))
        super().atividade(nome)

    def estimulo_novidade(self, n):
        self.chamadas.append(("novidade", n))
        super().estimulo_novidade(n)


# as sub-chaves da etapa 6: cada uma exige a anterior (digestao -> vida -> drives_novos -> gestos)
NOVOS = ConfigCorpo(ligada=True, digestao=True, vida=True, drives_novos=True)
GESTOS = CONFIG_CORPO_DRIVES
ORGAOS = ConfigCorpo(ligada=True, digestao=True, vida=True)


@pytest.fixture
def corpo_de_teste(monkeypatch):
    monkeypatch.setattr(motor_corpo, "Corpo", CorpoEspiao)


# ================================================================== os cerebros espioes
class _Espiao:
    def _iniciar(self):
        self.dono = []
        self.mudancas = []
        self.corpo = []
        self.mundo = []
        self.decisoes = 0

    def agir(self, obs, rng):
        self.decisoes += 1
        return super().agir(obs, rng)

    def receber_acao_dono(self, acao, tick):
        self.dono.append((tick, acao.value))

    def mudanca_no_corpo(self, antes, depois):
        self.mudancas.append((antes, depois))

    def consequencia_corpo(self, acao, ocorrido, obs_depois):
        self.corpo.append((acao, ocorrido, obs_depois))

    def consequencia_mundo(self, acao, ocorrido, obs_depois):
        self.mundo.append((acao, dict(ocorrido), obs_depois))


class EspiaoPadrao(_Espiao, PoliticaInstinto):
    def __init__(self, cfg=None):
        PoliticaInstinto.__init__(self, cfg or CFG)
        self._iniciar()


class EspiaoBola(_Espiao, PoliticaInstintoBola):
    def __init__(self, cfg=None):
        PoliticaInstintoBola.__init__(self, cfg or CFG, CONFIG_BOLA_LIGADA)
        self._iniciar()


class EspiaoFrutas(_Espiao, PoliticaInstintoFrutas):
    def __init__(self, cfg=None):
        PoliticaInstintoFrutas.__init__(self, cfg or CFG, None, CONFIG_FRUTAS_LIGADA)
        self._iniciar()


class EspiaoMundo(_Espiao, PoliticaInstintoMundo):
    def __init__(self, cfg=None):
        PoliticaInstintoMundo.__init__(self, cfg or CFG)
        self._iniciar()


# ================================================================== as vidas
def _fm_padrao(cc):
    return lambda p, cfg, s: com_corpo(MotorComFeedback)(p, cfg, s, cfg_corpo=cc)


def _fm_bola(cc):
    return lambda p, cfg, s: com_corpo(MotorAmbiente)(p, cfg, s, obediencia_desligada=True, cfg_bola=CONFIG_BOLA_LIGADA, cfg_corpo=cc)


def _fm_frutas(cc):
    return lambda p, cfg, s: com_corpo(MotorFrutas)(p, cfg, s, obediencia_desligada=True, cfg_frutas=CONFIG_FRUTAS_LIGADA, cfg_corpo=cc)


def _fm_mundo(cc, cm=CM):
    return lambda p, cfg, s: com_corpo(MotorMundo)(p, cfg, s, obediencia_desligada=True, cfg_mundo=cm, cfg_corpo=cc)


def _vida_padrao(cc, modo, dono="atencioso", semente=101, fp=EspiaoPadrao):
    fm = _fm_padrao(cc)
    v = simular_vida_gestos(dono, DonoComGestos(criar_dono(dono), modo), fp(CFG), semente, DIAS, ORC, fabrica_motor=fm,
                            rotulo_dono=dono)
    return v, fp, fm


def _vida_bola(cc, modo, dono="atencioso", semente=101):
    fm = _fm_bola(cc)
    v = simular_vida_gestos(dono, DonoComGestos(DonoComBola(dono, CONFIG_BOLA_LIGADA), modo), EspiaoBola(CFG), semente, DIAS, ORC,
                            fabrica_motor=fm, rotulo_dono=dono)
    return v, EspiaoBola, fm


def _vida_mundo(cc, modo, dono="atencioso", lugar="perto", semente=101, cm=CM):
    fm = _fm_mundo(cc, cm)
    d = DonoComGestos(DonoComLugar(criar_dono(dono), lugar, semente, dono, cm), modo)
    v = simular_vida_mundo(dono, d, EspiaoMundo(CFG), semente, DIAS, ORC, fm, rotulo_dono=dono, canal_classe=CanalMundoComGestos)
    return v, EspiaoMundo, fm


def _cerebro(m):
    p = m.politica
    while not isinstance(p, _Espiao):
        p = getattr(p, "_pm", None) or getattr(p, "_pf", None) or getattr(p, "_pb", None) or getattr(p, "_p")
    return p


def _acoes_log(m):
    return [e.valor for e in m.log if e.tipo == "acao_usuario"]


# ================================================================== o enum e o tapa sem a chave
def test_tapa_no_fim_do_enum_e_as_de_antes_nao_andaram():
    todos = list(AcaoUsuario)
    # o tapa foi o ultimo ate o J5, que pos a fruta na mao e a troca de tipo depois dele (docs/TAREFA_V2_PET_QUE_PENSA.md, etapa 3)
    assert todos[29] is AcaoUsuario.TAPA and AcaoUsuario.TAPA.value == "tapa" and ACOES_CORPO == (AcaoUsuario.TAPA,)
    assert todos[26:29] == list(ACOES_PEDIDO) and len(todos) >= 30


def test_tapa_nos_motores_de_hoje_e_no_reproduzir_de_hoje_falha_alto():
    m = MotorComFeedback(PoliticaInstinto(CFG), CFG, 101)
    with pytest.raises(ValueError):
        m.observar(AcaoUsuario.TAPA)
    log = LogDeEventos([avanco(0, 30), acao_usuario(30, AcaoUsuario.TAPA)])
    with pytest.raises(ValueError):
        reproduzir_com_feedback(log, PoliticaInstinto, CFG, 101)
    with pytest.raises(ValueError):                                  # o motor das frutas de hoje (educacao no meio)
        reproduzir_educacao(log, lambda cfg=None: PoliticaInstintoFrutas(cfg or CFG, None, CONFIG_FRUTAS_LIGADA), CFG, 101,
                            fabrica_motor=lambda p, cfg, s: MotorFrutas(p, cfg, s, obediencia_desligada=True,
                                                                        cfg_frutas=CONFIG_FRUTAS_LIGADA))


def test_tapa_no_corpo_sem_gestos_falha_alto():
    for cc in (ConfigCorpo(ligada=True), None):                       # corpo sem gestos; corpo desligado (o motor de baixo)
        m = com_corpo(MotorComFeedback)(PoliticaInstinto(CFG), CFG, 101, cfg_corpo=cc)
        m.avancar(30)
        with pytest.raises(ValueError) as e:
            m.observar(AcaoUsuario.TAPA)
        if cc is not None:
            assert isinstance(e.value, GestoSemChave)


def test_sem_gestos_o_carinho_e_o_de_hoje_repassado_e_sem_mudanca_no_corpo():
    v = simular_vida("atencioso", criar_dono("atencioso"), EspiaoPadrao(CFG), 101, DIAS, ORC, rotulo_dono="atencioso",
                     fabrica_motor=_fm_padrao(ConfigCorpo(ligada=True)))
    c = _cerebro(v.motor)
    assert not c.mudancas and v.motor.mudancas == 0
    assert sum(a == "acariciar" for _, a in c.dono) == _acoes_log(v.motor).count("acariciar")


# ================================================================== o tapa e o carinho com gestos
@pytest.mark.parametrize("mundo", ["padrao", "bola", "mundo"])
def test_tapa_e_carinho_com_gestos(corpo_de_teste, mundo):
    cc = GESTOS
    v, _, _ = {"padrao": _vida_padrao, "bola": _vida_bola, "mundo": _vida_mundo}[mundo](cc, "tapa", "aleatorio")
    m = v.motor
    c = _cerebro(m)
    log = _acoes_log(m)
    n_tapa, n_carinho = log.count("tapa"), log.count("acariciar")
    assert n_tapa > 0 and n_carinho > 0 and "elogiar" not in log and "repreender" not in log
    # o tapa chega ao cerebro por receber_acao_dono, no tick dele; o carinho nao chega (so pelo corpo)
    ticks_tapa = [e.tick for e in m.log if e.tipo == "acao_usuario" and e.valor == "tapa"]
    assert [t for t, a in c.dono if a == "tapa"] == ticks_tapa
    assert not any(a == "acariciar" for _, a in c.dono)
    # o carinho chama o mudanca_no_corpo, um por carinho, com o corpo antes e depois; o tapa nao (CD-9)
    assert len(c.mudancas) == n_carinho == m.mudancas
    for antes, depois in c.mudancas:
        assert isinstance(antes.corpo, PercepcaoCorpo) and isinstance(depois.corpo, PercepcaoCorpo)
        assert depois.corpo.humor >= antes.corpo.humor                 # a tristeza do carinho (-27000), cortada em 0
        assert (antes.mundo is not None) == (mundo == "mundo")
    assert any(d.corpo.humor > a.corpo.humor for a, d in c.mudancas)
    # o corpo recebeu cada gesto uma vez
    dono_no_corpo = [x for k, x in m.corpo.chamadas if k == "dono"]
    assert dono_no_corpo.count("tapa") == n_tapa and dono_no_corpo.count("acariciar") == n_carinho
    # o orcamento fecha igual, e o tapa conta como contato
    contatos = sum(1 for e in m.log if (e.tipo == "acao_usuario" and e.valor != "por_bola") or e.tipo == "deixar_comida")
    assert v.interacoes == ORC and m._estado.total_cuidados == contatos


def test_o_tapa_nao_muda_drive_e_conta_como_contato(corpo_de_teste):
    cc = GESTOS
    m = com_corpo(MotorComFeedback)(EspiaoPadrao(CFG), CFG, 101, cfg_corpo=cc)
    m.avancar(100)
    antes = m._estado
    m.observar(AcaoUsuario.TAPA)
    depois = m._estado
    assert (depois.fome, depois.higiene, depois.energia, depois.humor, depois.saude) == \
        (antes.fome, antes.higiene, antes.energia, antes.humor, antes.saude)
    assert depois.tick_ultimo_cuidado == antes.tick and depois.total_cuidados == antes.total_cuidados + 1
    assert _cerebro(m).dono == [(antes.tick, "tapa")] and not _cerebro(m).mudancas


def test_gestos_no_motor_da_personalidade_contam_no_indice_e_no_vinculo(corpo_de_teste):
    """nas frutas (MotorPersonalidade no meio): o indice dos eventos anda com o tapa e o carinho (um por evento do log) e o vinculo os
    recebe"""
    cc = GESTOS
    fm = _fm_frutas(cc)
    v = simular_vida_frutas("atencioso", DonoComGestos(criar_dono("atencioso"), "tapa"), EspiaoFrutas(CFG), 101, DIAS, ORC, fm,
                            OfertasFrutas(CONFIG_FRUTAS_LIGADA), rotulo_dono="atencioso")
    m = v.motor
    assert _acoes_log(m).count("tapa") > 0 and m._n_eventos == len(list(m.log))
    r = reproduzir_educacao(m.log, lambda cfg=None: EspiaoFrutas(cfg or CFG), CFG, 101, fabrica_motor=fm)
    assert r.vinculo.para_dict() == m.vinculo.para_dict() and r._estado == m._estado


# ================================================================== o DonoComGestos
@pytest.mark.parametrize("dono", ["atencioso", "relapso", "aleatorio", "incoerente"])
def test_dono_com_gestos_mesma_rng_e_mesmo_orcamento(corpo_de_teste, dono):
    cc = GESTOS
    hoje = simular_vida(dono, criar_dono(dono), PoliticaInstinto(CFG), 101, DIAS, ORC, rotulo_dono=dono,
                        fabrica_motor=_fm_padrao(ConfigCorpo(ligada=True)))
    base = _acoes_log(hoje.motor)
    for modo in ("tapa", "sem_tapa"):
        d = DonoComGestos(criar_dono(dono), modo)
        v = simular_vida_gestos(dono, d, PoliticaInstinto(CFG), 101, DIAS, ORC, fabrica_motor=_fm_padrao(cc), rotulo_dono=dono)
        assert v.interacoes == ORC
        log = _acoes_log(v.motor)
        assert "elogiar" not in log and "repreender" not in log
        assert d.trocas["acariciar"] > 0 and log.count("acariciar") >= d.trocas["acariciar"]
        if modo == "tapa":
            assert log.count("tapa") == d.trocas["tapa"] and d.trocas["sem_gesto"] == 0
            assert len(log) == ORC
        else:
            assert "tapa" not in log and d.trocas["tapa"] == 0
            assert len(log) + d.trocas["sem_gesto"] == ORC
    assert "elogiar" in base and "repreender" in base                    # o dono de hoje tinha o que trocar


def test_dono_com_gestos_troca_so_elogio_e_bronca():
    class Fixo:
        nome = "fixo"

        def decidir(self, visao, rng):
            return [AcaoUsuario.ALIMENTAR, AcaoUsuario.ELOGIAR, AcaoUsuario.REPREENDER, AcaoUsuario.ACARICIAR]

    assert DonoComGestos(Fixo(), "tapa").decidir(None, None) == [AcaoUsuario.ALIMENTAR, AcaoUsuario.ACARICIAR, AcaoUsuario.TAPA,
                                                                  AcaoUsuario.ACARICIAR]
    sem = DonoComGestos(Fixo(), "sem_tapa").decidir(None, None)
    assert sem == [AcaoUsuario.ALIMENTAR, AcaoUsuario.ACARICIAR, SemGesto(AcaoUsuario.REPREENDER), AcaoUsuario.ACARICIAR]
    with pytest.raises(ValueError):
        DonoComGestos(Fixo(), "com_tapa")


def test_canal_com_gestos_conta_o_sem_gesto_e_recusa_o_desconhecido():
    m = MotorComFeedback(PoliticaInstinto(CFG), CFG, 101)
    c = CanalComGestos(m, 4, 4)
    c.aplicar([AcaoUsuario.ALIMENTAR, SemGesto(AcaoUsuario.REPREENDER)], 0, 2)
    assert c.gasto == 2 and c.sem_gesto == 1 and _acoes_log(m) == ["alimentar"]
    with pytest.raises(TypeError):
        c.aplicar(["x", "y"], 1, 2)


# ================================================================== os drives novos: a atividade e a novidade
@pytest.mark.parametrize("mundo", ["padrao", "bola"])
def test_atividade_uma_por_decisao_de_brincar_ou_explorar(corpo_de_teste, mundo):
    cc = NOVOS
    v, _, _ = {"padrao": _vida_padrao, "bola": _vida_bola}[mundo](cc, "sem_tapa")
    m = v.motor
    c = _cerebro(m)
    esperadas = []
    for acao, oc, _ in c.corpo:
        if acao is AcaoPet.BRINCAR:
            esperadas.append("bola" if ("bola",) in oc["estimulos"] else "brincar")
        elif acao is AcaoPet.EXPLORAR:
            esperadas.append("explorar")
    assert [x for k, x in m.corpo.chamadas if k == "atividade" and x != "dono_brinca"] == esperadas and esperadas
    if mundo == "bola":
        assert "bola" in esperadas
    assert not any(k == "novidade" for k, _ in m.corpo.chamadas) and m.corpo.com_mundo is False
    # a atividade vem antes do consequencia_corpo: o ocorrido ja a traz
    for acao, oc, _ in c.corpo:
        assert any(e[0] == "atividade" for e in oc["estimulos"]) == (acao in (AcaoPet.BRINCAR, AcaoPet.EXPLORAR))


class _MundoAnotado(com_corpo(MotorMundo)):
    """anota o que o pet ve ao decidir e depois da consequencia (para refazer a regra da novidade por fora)"""

    def _antes_da_decisao(self):
        p = super()._antes_da_decisao()
        self.anotado.append(("antes", self._estado.tick, [v[0] for v in p.vistos], None))
        return p

    def _consequencia(self, acao):
        oc = super()._consequencia(acao)
        if oc is not None:
            self.anotado.append(("depois", self._estado.tick, [v[0] for v in self._perceber(self._estado.tick).vistos], (acao, oc)))
        return oc


@pytest.mark.parametrize("janela", [1440, 60])
def test_vistos_novos_e_a_novidade_refeitos_por_fora(corpo_de_teste, janela):
    cc = replace(NOVOS, janela_novidade=janela)
    vistos_algum = 0
    for semente in (101, 202, 303):
        fm = lambda p, cfg, s: _MundoAnotado(p, cfg, s, obediencia_desligada=True, cfg_mundo=CM, cfg_corpo=cc)  # noqa: E731
        _MundoAnotado.anotado = []
        d = DonoComGestos(DonoComLugar(criar_dono("atencioso"), "perto", semente, "atencioso", CM), "sem_tapa")
        v = simular_vida_mundo("atencioso", d, EspiaoMundo(CFG), semente, DIAS, ORC, fm, rotulo_dono="atencioso",
                               canal_classe=CanalMundoComGestos)
        m = v.motor
        assert m.corpo.com_mundo is True
        # a regra, refeita: novo = visto depois de explorar e nao visto nas ultimas `janela` ticks (inclusive ao decidir)
        ultimo: dict[int, int] = {}
        novidades = []
        for fase, tick, ids, extra in _MundoAnotado.anotado:
            if fase == "depois":
                acao, oc = extra
                esperado = []
                if acao is AcaoPet.EXPLORAR:
                    esperado = [i for i in ids if i not in ultimo or tick - ultimo[i] >= janela]
                    novidades.append(len(esperado))
                assert [i for i, _ in oc["vistos_novos"]] == esperado, (tick, acao)
            for i in ids:
                ultimo[i] = tick
        assert [n for k, n in m.corpo.chamadas if k == "novidade"] == novidades
        vistos_algum += sum(novidades)
        # o consequencia_mundo ve os vistos_novos, e a atividade ja aplicada (antes do obs_depois)
        c = _cerebro(m)
        assert all("vistos_novos" in oc for _, oc, _ in c.mundo)
        assert all(oc["vistos_novos"] == [] for a, oc, _ in c.mundo if a is not AcaoPet.EXPLORAR)
        exploracoes = sum(a is AcaoPet.EXPLORAR for a, _, _ in c.mundo)
        assert sum(k == "atividade" and x == "explorar" for k, x in m.corpo.chamadas) == exploracoes
    assert vistos_algum > 0


def test_sem_drives_novos_o_ocorrido_do_mundo_e_o_de_hoje(corpo_de_teste):
    v, _, _ = _vida_mundo(ORGAOS, "sem_tapa")
    c = _cerebro(v.motor)
    assert c.mundo and all("vistos_novos" not in oc for _, oc, _ in c.mundo)
    assert not any(k in ("atividade", "novidade") for k, _ in v.motor.corpo.chamadas)


# ================================================================== G1 com os gestos e os drives novos
def _resumo(m) -> str:
    extra = m.resumo_mundo_fisico() if isinstance(m, MotorMundo) else None
    return json.dumps({"estado": m.estado(), "q": m.corpo.q, "bruto": repr(m._estado), "mundo": extra,
                       "rng": m._rng_ambiente.getstate(), "acoes": m.acoes_recentes(10**9), "chamadas": m.corpo.chamadas,
                       "vistos": m._vistos_em, "mudancas": m.mudancas, "consequencias": m.consequencias}, sort_keys=True, default=repr)


@pytest.mark.parametrize("modo", ["tapa", "sem_tapa"])
def test_g1_replay_bit_a_bit_com_gestos(corpo_de_teste, modo):
    cc = GESTOS
    v, fp, fm = _vida_padrao(cc, modo)
    r = reproduzir_com_feedback(LogDeEventos.de_jsonl(v.motor.log.para_jsonl()), fp, CFG, 101, fabrica_motor=fm)
    assert _resumo(r) == _resumo(v.motor)
    v, fp, fm = _vida_bola(cc, modo)
    r = reproduzir_educacao(LogDeEventos.de_jsonl(v.motor.log.para_jsonl()), fp, CFG, 101, fabrica_motor=fm)
    assert _resumo(r) == _resumo(v.motor)
    for dono, lugar in (("atencioso", "perto"), ("aleatorio", "longe")):
        v, fp, fm = _vida_mundo(cc, modo, dono, lugar, 202)
        r = reproduzir_mundo(LogDeEventos.de_jsonl(v.motor.log.para_jsonl()), fp, CFG, 202, fabrica_motor=fm)
        assert _resumo(r) == _resumo(v.motor)
        assert _cerebro(r).dono == _cerebro(v.motor).dono and len(_cerebro(r).mudancas) == len(_cerebro(v.motor).mudancas)
