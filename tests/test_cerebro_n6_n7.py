"""V2, CEREBRO-N6-N7 (docs/TAREFA_V2_CEREBRO_N6_N7.md, etapa C1): a memoria de episodios (N6) e a arbitragem do pedido (N7) nos lobos,
atras de chaves. So testes de mecanismo, so as sementes dos testes (nenhuma faixa reservada).

- G2: com as chaves desligadas (memoria desligada, ganho 0, w0_pedido 0), as 192 vidas do gabarito gravado ANTES da mudança saem iguais,
  estado interno incluido (tests/gabarito_cerebro_n6_n7.py).
- Memoria: os espacos da v1 (4 + 2, 12 h, o desempate); um episodio ruim recente com a fruta X baixa a chance de escolher X so com a
  memoria ligada; a sonda contrafactual reproduz a decisao sem memoria; recencia e embaralhado; o M0 (ligada, ganho 0) e o P0 nas
  decisoes; G1 com memoria.
- Arbitragem: com pedido vigente, a decisao urgente nao muda (G-URG); na fome moderada o pedido pesa na medida do w0_pedido; o peso do
  pedido aprende pela consequencia e pelo dono; sem o campo do pedido no mundo, nada muda.
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import bancada_v2 as bv  # noqa: E402
import gabarito_cerebro_n6_n7 as gab  # noqa: E402
from digilab.config import (CONFIG_CONSEQUENCIA, CONFIG_FRUTAS_LIGADA, CONFIG_LOBOS, CONFIG_LOBOS_APRENDIZ,  # noqa: E402
                            CONFIG_PADRAO, TICKS_POR_DIA)
from digilab.events import FRUTAS, AcaoPet, AcaoUsuario  # noqa: E402
from digilab.policies.lobos import (MemoriaEpisodios, PoliticaLobos, desarranjo_n6,  # noqa: E402
                                    validar_parametros_lobos)
from digilab.policy import Observacao, Transicao  # noqa: E402
from digilab.state import Estado  # noqa: E402

S = CONFIG_LOBOS.escala
CF = CONFIG_FRUTAS_LIGADA


@dataclass(frozen=True)
class ObsComPedido(Observacao):
    """A Observacao com o campo do pedido do N7 (o lado do mundo e do chat A; o nome e o do plano, secao 2)."""
    pedido_frutas: tuple = (0.0, 0.0, 0.0)


class _Rng:
    def __init__(self, u):
        self.u = u

    def random(self):
        return self.u


def _lobos(aprende: bool = False, **kw) -> PoliticaLobos:
    base = CONFIG_LOBOS_APRENDIZ if aprende else CONFIG_LOBOS
    return PoliticaLobos(CONFIG_PADRAO, replace(base, **kw), None, CF)


def _obs(tick: int, presentes: str = "", fome: float = 1.0, humor: float = 0.8, energia: float = 1.0, pedido: str = "",
         fruta: float = 0.5, **kw) -> ObsComPedido:
    e = Estado(fome=fome, higiene=1.0, energia=energia, humor=humor, tick=tick, tick_ultimo_cuidado=tick - 10, **kw)
    o = Observacao.de_estado(e)
    pres = tuple(1.0 if f in presentes else 0.0 for f in FRUTAS)
    ped = tuple(-1.0 if f in pedido else 0.0 for f in FRUTAS)
    return ObsComPedido(o.vetor_estado, o.ticks_desde_cuidado, o.total_cuidados, fruta=fruta if presentes else 0.0,
                        frutas_cenario=pres, pedido_frutas=ped)


def _p_escolha(p: PoliticaLobos, presentes: list, fruta: str, n: int = 400) -> float:
    inc = {f: 0.5 for f in presentes}
    return sum(p.escolher_fruta(presentes, inc, (k + 0.5) / n) == fruta for k in range(n)) / n


def _p_comer(p: PoliticaLobos) -> float:
    pesos = p.motivos[-1]["pesos"]
    return pesos["comer"] / sum(pesos.values())


# ------------------------------------------------------------------ G2: a vida de hoje, por gabarito gravado antes


def test_g2_chaves_desligadas_e_a_vida_de_hoje():
    g = json.loads(gab.ARQUIVO.read_text(encoding="utf-8"))
    agora = gab.gerar()
    assert set(agora) == set(g) and len(g) == 192
    diferentes = [k for k in g if agora[k] != g[k]]
    assert diferentes == []


def test_registro_e_recusas():
    validar_parametros_lobos()
    assert (CONFIG_LOBOS.memoria_ligada, CONFIG_LOBOS.memoria_ganho, CONFIG_LOBOS.w0_pedido) == (False, 0, 0)
    for ruim in ({"memoria_modo": "outro"}, {"memoria_ganho": S}, {"memoria_ganho": -1}, {"memoria_ganho": 0.5},
                 {"memoria_modo": "embaralhada"}, {"memoria_modo": "embaralhada", "memoria_permutacao": ("a", "b", "c")},
                 {"memoria_permutacao": ("b", "c", "a")}, {"w0_pedido": -1}, {"memoria_janela_recencia_ticks": 0}):
        with pytest.raises((ValueError, TypeError)):
            _lobos(**ruim)
    # sem ver as frutas, nada existe (as formas de hoje)
    e = PoliticaLobos(CONFIG_PADRAO, replace(CONFIG_LOBOS, memoria_ligada=True, w0_pedido=S // 2)).estado_interno()
    assert "memoria" not in e and "peso_pedido" not in e


def test_desarranjo():
    vistos = set()
    for s in range(101, 140):
        d = desarranjo_n6(s)
        assert d == desarranjo_n6(s) and sorted(d) == sorted(FRUTAS) and all(x != f for x, f in zip(d, FRUTAS))
        vistos.add(d)
    assert len(vistos) == 2


# ------------------------------------------------------------------ N6: os espacos


def test_espacos_regra_da_v1():
    m = MemoriaEpisodios(4, 2, 720)
    m.codificar(0, "a", -512)
    m.codificar(15, "a", -256)                    # mais fraca, mesma fruta: descartada
    assert [e["valencia"] for e in m.curto] == [-512] and m.contagem["descartada"] == 1
    m.codificar(30, "a", 512)                     # igual: a mais recente substitui
    assert [e["tick"] for e in m.curto] == [30]
    m.codificar(45, "b", -1024)
    m.codificar(60, "c", 0)                       # a neutra entra (codificada), com intensidade 0
    assert len(m.curto) == 3 and len(m.episodios) == 5
    m.promover(30 + 719)
    assert len(m.curto) == 3 and m.longo == []
    m.promover(60 + 720)                          # todos vencem: o longo fica com os dois mais fortes; a neutra perde
    assert m.curto == [] and sorted(e["fruta"] for e in m.longo) == ["a", "b"] and m.contagem["esquecida"] == 1
    assert m.recuperar("b", 2000, "relevante", 240, {})["valencia"] == -1024
    assert m.recuperar("b", 2000, "recencia", 240, {}) is None          # velho demais para a janela
    assert m.recuperar("c", 2000, "embaralhada", 240, {"c": "b"})["fruta"] == "b"


# ------------------------------------------------------------------ N6: a memoria muda a escolha so ligada


def _comer_so(p: PoliticaLobos, fruta: str, tick: int, delta_humor: float) -> None:
    obs = _obs(tick, fruta)
    assert p.agir(obs, _Rng(1.0 - 1e-12)) is AcaoPet.COMER and p.ultima_regra == "fruta_no_cenario"
    if p.aprende:
        p.observar_consequencia(Transicao(obs, AcaoPet.COMER, obs), 0, CONFIG_CONSEQUENCIA)
    assert p.escolher_fruta([fruta], {fruta: 0.5}, 0.5) == fruta
    p.fruta_comida(fruta, Observacao.de_estado(replace(Estado(fome=1.0, higiene=1.0, energia=1.0, humor=0.8, tick=tick),
                                                       humor=0.8 + delta_humor)))


@pytest.mark.parametrize("ganho,esperado", [(0, 0.5), (S // 4, 0.75 / 1.75), (S // 2, 0.5 / 1.5), (3 * S // 4, 0.25 / 1.25)])
def test_episodio_ruim_baixa_a_fruta_na_medida_do_ganho(ganho, esperado):
    p = _lobos(memoria_ligada=True, memoria_ganho=ganho)
    _comer_so(p, "a", 9 * 60, -0.1)
    ep = p.estado_interno()["memoria"]["episodios"]
    assert ep == [{"tick": 9 * 60, "fruta": "a", "valencia": -S, "intensidade": S}]
    p.agir(_obs(9 * 60 + 15, "ab"), _Rng(0.0))
    assert _p_escolha(p, ["a", "b"], "a") == pytest.approx(esperado, abs=0.01)
    desligada = _lobos()
    desligada.agir(_obs(9 * 60 + 15, "ab"), _Rng(0.0))
    assert _p_escolha(desligada, ["a", "b"], "a") == 0.5


def test_sonda_contrafactual_reproduz_a_decisao_sem_memoria():
    p, sem = _lobos(memoria_ligada=True, memoria_ganho=S // 2), _lobos()
    _comer_so(p, "a", 9 * 60, -0.1)
    p.agir(_obs(9 * 60 + 15, "ab"), _Rng(0.0))
    sem.agir(_obs(9 * 60 + 15, "ab"), _Rng(0.0))
    mudou = 0
    for k in range(200):
        u = (k + 0.5) / 200
        f = p.escolher_fruta(["a", "b"], {"a": 0.5, "b": 0.5}, u)
        sonda = p.motivos[-1]["fruta"]["sonda_memoria"]
        assert sonda["escolha_sem_memoria"] == sem.escolher_fruta(["a", "b"], {"a": 0.5, "b": 0.5}, u)
        assert sonda["mudou"] == (sonda["escolha_sem_memoria"] != f) and sonda["recuperou"]
        mudou += sonda["mudou"]
    assert mudou > 0 and p.estado_interno()["memoria"]["sondas"]["mudou"] == mudou


def test_recencia_e_embaralhado_nos_lobos():
    rec = _lobos(memoria_ligada=True, memoria_ganho=S // 2, memoria_modo="recencia")
    _comer_so(rec, "a", 9 * 60, -0.1)
    rec.agir(_obs(9 * 60 + 255, "ab"), _Rng(0.0))                   # 255 min depois: fora da janela de 240
    assert _p_escolha(rec, ["a", "b"], "a") == 0.5
    perm = ("b", "c", "a")                                            # pi(a) = b, pi(b) = c, pi(c) = a
    emb = _lobos(memoria_ligada=True, memoria_ganho=S // 2, memoria_modo="embaralhada", memoria_permutacao=perm)
    _comer_so(emb, "a", 9 * 60, -0.1)
    emb.agir(_obs(9 * 60 + 15, "ac"), _Rng(0.0))
    # a pista c recupera o episodio ruim de a (pi(c) = a): quem perde peso e a c, nao a a
    assert _p_escolha(emb, ["a", "c"], "a") == pytest.approx(1 / 1.5, abs=0.01)
    m = emb.motivos[-1]["fruta"]["memoria_emocao"]
    assert m["c"]["episodio"]["fruta"] == "a" and m["a"]["episodio"] is None


def test_relogio_vira_o_dia():
    p = _lobos(memoria_ligada=True)
    _comer_so(p, "a", TICKS_POR_DIA - 15, -0.1)
    _comer_so(p, "b", TICKS_POR_DIA + 15, 0.1)
    assert [e["tick"] for e in p.estado_interno()["memoria"]["episodios"]] == [TICKS_POR_DIA - 15, TICKS_POR_DIA + 15]


# ------------------------------------------------------------------ N6 pela bancada: M0 = P0 nas decisoes; G1; codificacao


def _bancada(**kw) -> bv.Bancada:
    return bv.Bancada(4, 64, cfg_lobos=replace(CONFIG_LOBOS_APRENDIZ, **kw))


@pytest.mark.parametrize("semente", (101, 202))
def test_m0_e_o_p0_nas_decisoes_e_codifica_todo_consumo(semente):
    espec = bv.EspecVida("atencioso", "P0", semente, None, "descasado")
    p0 = bv.Bancada(4, 64).vida(espec).motor
    # desde a BANCADA-LIGA-N6-N7 a memoria e do braco: o M0 (memoria ligada, ganho 0) no lugar do P0 com a chave na config
    m0 = bv.Bancada(4, 64).vida(replace(espec, braco="M0")).motor
    assert bv.resumo_motor(m0) == bv.resumo_motor(p0)
    e0, em = p0.politica.estado_interno(), m0.politica.estado_interno()
    for m in em["motivos"]:                                           # so o estado do lobo de memoria difere (G2 do plano)
        if "fruta" in m:
            m["fruta"].pop("memoria_emocao", None)
            m["fruta"].pop("sonda_memoria", None)
    # so o estado do lobo de memoria e o rotulo do braco (M0 x P0) diferem
    assert {k: v for k, v in em.items() if k not in ("memoria", "bancada")} == {k: v for k, v in e0.items() if k != "bancada"}
    assert (em["bancada"]["braco"], e0["bancada"]["braco"]) == ("M0", "P0")
    eps = em["memoria"]["episodios"]
    assert [(e["tick"], e["fruta"]) for e in eps] == [(c["tick"], c["fruta"]) for c in m0.consumos] and eps
    for e, c in zip(eps, m0.consumos):                                # o sinal da valencia segue o efeito no humor
        assert (e["valencia"] < 0) == (c["efeito_humor"] < 0) or c["efeito_humor"] == 0.0


def test_mr_pela_bancada_g1_e_a_memoria_age():
    b = _bancada(memoria_ganho=S // 2)                                     # o ganho da config; o braco MR liga a memoria
    mudou = 0
    for s in (101, 202, 303):
        v = b.vida(bv.EspecVida("atencioso", "MR", s, None, "descasado"))   # a bancada rejoga do texto do log (G1, estado interno)
        mudou += v.motor.politica.estado_interno()["memoria"]["sondas"]["mudou"]
    assert mudou > 0


# ------------------------------------------------------------------ N7: G-URG, fome moderada, escolha, aprendizado


@pytest.mark.parametrize("cond", [dict(fome=0.2), dict(energia=0.2), dict(fome=0.4, ticks_extra=1000)])
def test_g_urg_regras_urgentes_nao_leem_o_pedido(cond):
    extra = cond.pop("ticks_extra", 0)
    for u in (0.0, 0.5, 1.0 - 1e-12):
        com, sem = _lobos(w0_pedido=3 * S // 4), _lobos()
        o = _obs(12 * 60, "a", pedido="a", **cond)
        if extra:
            o = replace(o, ticks_desde_cuidado=extra)
        a1, a2 = com.agir(o, _Rng(u)), sem.agir(o, _Rng(u))
        assert com.ultima_regra in ("sono_exaustao", "pedido_necessidade", "abandono")
        assert a1 is a2 and "pedido" not in com.motivos[-1] and com.motivos[-1]["pesos"] == sem.motivos[-1]["pesos"]


@pytest.mark.parametrize("w0,esperado", [(0, 0.5), (S // 4, 0.75 / 1.75), (S // 2, 0.5 / 1.5), (3 * S // 4, 0.25 / 1.25)])
def test_fome_moderada_o_pedido_pesa_na_medida_do_w0(w0, esperado):
    p = _lobos(w0_pedido=w0)
    p.agir(_obs(12 * 60, "a", fome=0.4, pedido="a"), _Rng(0.0))
    assert p.ultima_regra == "fome_moderada" and _p_comer(p) == pytest.approx(esperado)
    # pedido numa fruta que nao esta sozinha no cenario: o pet pode comer a outra, o pedido nao pesa em comer
    q = _lobos(w0_pedido=w0)
    q.agir(_obs(12 * 60, "ab", fome=0.4, pedido="a"), _Rng(0.0))
    assert _p_comer(q) == pytest.approx(0.5)


def test_sonda_de_quem_decidiu_e_fruta_no_cenario():
    p = _lobos(w0_pedido=S // 2)
    decidiu = 0
    for k in range(100):
        u = (k + 0.5) / 100
        a = p.agir(_obs(12 * 60 + 15 * k, "a", fome=0.4, pedido="a"), _Rng(u))
        ped = p.motivos[-1]["pedido"]
        sem = _lobos()
        assert ped["acao_sem_pedido"] == sem.agir(_obs(12 * 60 + 15 * k, "a", fome=0.4, pedido="a"), _Rng(u)).value
        decidiu += ped["pedido_decidiu"] and a is not AcaoPet.COMER
    assert decidiu > 0
    f = _lobos(w0_pedido=S // 2)
    f.agir(_obs(12 * 60, "a", pedido="a"), _Rng(0.0))
    assert f.ultima_regra == "fruta_no_cenario" and f.motivos[-1]["pesos"]["comer"] == pytest.approx(6.0 * 0.5 - 0.5)


def test_pedido_na_escolha_da_fruta():
    p = _lobos(w0_pedido=S // 2)
    p.agir(_obs(12 * 60, "ab", pedido="a"), _Rng(0.0))
    assert _p_escolha(p, ["a", "b"], "a") == pytest.approx(0.0625 / 0.5625, abs=0.01)   # a: 0,5 - 0,5 -> o piso 1/16; b: 0,5
    assert p.motivos[-1]["fruta"]["pedido"] == {"a": -1.0, "b": 0.0}


def test_peso_do_pedido_aprende_pelo_dono_e_pela_consequencia():
    # P3: bronca depois de comer X com pedido vigente -> o pedido pesa mais
    p = _lobos(aprende=True, w0_pedido=S // 2)
    o = _obs(12 * 60, "a", fome=0.4, pedido="a")
    assert p.agir(o, _Rng(0.0)) is AcaoPet.COMER
    p.observar(Transicao(o, AcaoPet.COMER, o))
    p.receber_acao_dono(AcaoUsuario.REPREENDER, 12 * 60 + 1)
    assert p.estado_interno()["peso_pedido"] > S // 2
    # P1: comer X com fome da sinal positivo (nutricao) -> o pedido pesa menos (a necessidade corroi)
    q = _lobos(aprende=True, w0_pedido=S // 2)
    o = _obs(12 * 60, "a", fome=0.4, pedido="a")
    assert q.agir(o, _Rng(0.0)) is AcaoPet.COMER
    q.observar_consequencia(Transicao(o, AcaoPet.COMER, o), 0, CONFIG_CONSEQUENCIA)
    q.escolher_fruta(["a"], {"a": 0.5}, 0.5)
    q.fruta_comida("a", Observacao.de_estado(Estado(fome=0.5, higiene=1.0, energia=1.0, humor=0.8, tick=12 * 60)))
    assert q.estado_interno()["peso_pedido"] < S // 2
    # P0 (aprendizado desligado): ninguem mexe
    r = _lobos(w0_pedido=S // 2)
    r.agir(o, _Rng(0.0))
    r.receber_acao_dono(AcaoUsuario.REPREENDER, 12 * 60 + 1)
    assert r.estado_interno()["peso_pedido"] == S // 2


def test_sem_o_campo_do_pedido_no_mundo_nada_muda():
    """Sem pedido no mundo nada muda. Desde a BANCADA-LIGA-N6-N7 o pedido e do braco: num braco sem pedido (o P1) o w0_pedido da
    config nao chega ao cerebro (a vida e o estado interno de hoje); no P1+ped chega."""
    for s in (101, 202):
        espec = bv.EspecVida("atencioso", "P1", s, None, "descasado")
        hoje = bv.Bancada(4, 64).vida(espec).motor
        com = _bancada(w0_pedido=S // 2).vida(espec).motor
        assert bv.resumo_motor(com) == bv.resumo_motor(hoje)
        assert "peso_pedido" not in com.politica.estado_interno()
        ped = _bancada(w0_pedido=S // 2).politica(replace(espec, braco="P1+ped")).cerebro
        assert ped.estado_interno()["peso_pedido"] == S // 2


def test_determinismo_com_memoria_e_pedido():
    def vida():
        p = _lobos(aprende=True, memoria_ligada=True, memoria_ganho=S // 2, w0_pedido=S // 2)
        for k in range(30):
            o = _obs(9 * 60 + 15 * k, "ab" if k % 3 else "a", fome=0.4 if k % 2 else 1.0, pedido="a" if k < 15 else "")
            a = p.agir(o, _Rng(((k * 37) % 100) / 100))
            if a is AcaoPet.COMER:
                p.observar_consequencia(Transicao(o, a, o), 0, CONFIG_CONSEQUENCIA)
                f = p.escolher_fruta(["a", "b"] if k % 3 else ["a"], {"a": 0.5, "b": 0.4}, ((k * 53) % 100) / 100)
                p.fruta_comida(f, Observacao.de_estado(Estado(fome=0.5, humor=0.7 if f == "a" else 0.9, tick=o.ticks_desde_cuidado)))
            else:
                p.observar_consequencia(Transicao(o, a, o), 0, CONFIG_CONSEQUENCIA)
        return json.dumps(p.estado_interno(), sort_keys=True, default=repr)
    assert vida() == vida()
