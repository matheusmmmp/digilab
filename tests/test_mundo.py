"""V2, mundo fisico, etapa 2 (docs/TAREFA_V2_MUNDO_FISICO.md, secoes 2 a 8 e os gates da secao 10; MF-1 a MF-4).

G1: toda vida com o mundo, rejogada do log, da o mesmo estado, as mesmas posicoes e os mesmos objetos, bit a bit. G2: com a chave
desligada, as vidas de hoje byte a byte (tests/gabaritos/mundo_vidas_de_hoje.json, gravado antes, PR #217), com o MotorMundo
desligado no lugar do motor da bola e das frutas. G-ENGINE: engine.py com o sha256 de antes; ambiente.py e frutas.py sem mudanca nesta
etapa. G-MEC: os mecanismos. G-NUMS: P0 e P1 da mesma semente veem as mesmas quedas. So as sementes dos testes.
"""
from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import bancada_v2 as bv  # noqa: E402
import gabarito_mundo as gm  # noqa: E402
from digilab.config import (CONFIG_BOLA_LIGADA, CONFIG_EDUCACAO, CONFIG_FRUTAS_LIGADA, CONFIG_LOBOS_APRENDIZ, CONFIG_MUNDO,  # noqa: E402
                            CONFIG_MUNDO_LIGADA, CONFIG_PADRAO, LAYOUT_MUNDO_AFASTADO, LAYOUT_MUNDO_PADRAO, ConfigMundo)
from digilab.donos import criar_dono  # noqa: E402
from digilab.educacao import reproduzir_educacao  # noqa: E402
from digilab.events import (AcaoPet, AcaoUsuario, Evento, LogDeEventos, deixar_bola, deixar_comida,  # noqa: E402
                            ler_deixar_bola, ler_deixar_comida)
from digilab.frutas import MotorFrutas  # noqa: E402
from digilab.mundo import (DIR16, ESTILOS_LUGAR, Alvo, DeixarComida, DonoComLugar, GestoForaDoMundo, MotorMundo,  # noqa: E402
                           MundoSemChave, cheiro_em, deslocar, direcao_do_cheiro, distancia, fabricas_mundo, passo_ate,
                           regiao_de, reproduzir_mundo, simular_vida_mundo)
from digilab.policies.lobos import PoliticaLobos  # noqa: E402
from digilab.protocol import ENGINE_SHA256_V0, sha256_engine  # noqa: E402
from digilab.state import _limitar  # noqa: E402

CM = CONFIG_MUNDO_LIGADA
SEMENTES = (101, 202)                     # so dos testes
DONOS = ("atencioso", "relapso", "aleatorio", "incoerente")
NINHO = (4 * 16 + 8, 15 * 16 + 8)
I_FOME, I_ENERGIA, I_HUMOR = 0, 2, 3
# ambiente.py e frutas.py nao mudam na etapa 2 (G-ENGINE). Quem mudar estes arquivos depois atualiza a constante, com o motivo no PR.
SEM_QUEDAS = replace(CM, mult_queda=1e-12)          # nenhuma fruta cai: so a comida do teste
SHA_AMBIENTE = "e21799de3c2c24266fc4239ba76217f16488a4e393ed3d8ce263150dabeec3dd"
SHA_FRUTAS = "d0b248d2bbbd1e64ec4901aa74b84610763064c266a1a839214ed7bd88bdc808"


def _sha(texto: str) -> str:
    return hashlib.sha256(texto.encode()).hexdigest()


class Cerebro:
    """Cerebro de teste: a acao vem de `acao(obs, rng)`; o alvo, se dado, de `alvo(acao, candidatos, percepcao, u)`. Registra o que
    ve, as transicoes, o dono e a consequencia do mundo."""

    nome = "teste"

    def __init__(self, acao, alvo=None) -> None:
        self._acao = acao
        if alvo is not None:
            self.escolher_alvo = alvo
        self.vistas, self.transicoes, self.dono, self.conseq, self.frutas = [], [], [], [], []

    def agir(self, obs, rng):
        self.vistas.append(obs)
        return self._acao(obs, rng)

    def observar(self, transicao) -> None:
        self.transicoes.append(transicao)

    def receber_acao_dono(self, acao, tick) -> None:
        self.dono.append((acao, tick))

    def consequencia_mundo(self, acao, ocorrido, obs_depois) -> None:
        self.conseq.append((acao, ocorrido, obs_depois))

    def fruta_comida(self, fruta, obs) -> None:
        self.frutas.append(fruta)

    def estado_interno(self) -> dict:
        return {"nome": self.nome}


def sempre(acao):
    return lambda obs, rng: acao


def aleatoria(obs, rng):
    return rng.choice(list(AcaoPet))


def alvo_aleatorio(acao, cands, perc, u):
    """qualquer candidato, ou um ponto lembrado no explorar, ou o padrao"""
    k = u % (len(cands) + 2)
    if k < len(cands):
        return cands[k]
    if k == len(cands) and acao is AcaoPet.EXPLORAR:
        return Alvo.ponto((u * 7) % 1024, (u * 13) % 480)
    return None


def motor_de(cerebro, semente=101, cm=CM, **kw):
    _, fm = fabricas_mundo(cm, **kw)
    return fm(cerebro, CONFIG_PADRAO, semente)


def _resumo(m) -> str:
    return json.dumps({"log": m.log.para_jsonl(), "estado": m.estado(), "estado_bruto": repr(m._estado),
                       "acoes": m.acoes_recentes(10**9), "rng_ambiente": m._rng_ambiente.getstate(),
                       "rng_politica": m._rng_politica.getstate(), "mundo": m.resumo_mundo_fisico(),
                       "politica": m.politica.estado_interno()}, sort_keys=True, default=repr)


# ================================================================== G-ENGINE
def _sha_arquivo(rel: str) -> str:
    return hashlib.sha256((RAIZ / rel).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def test_g_engine_engine_ambiente_e_frutas_intocados():
    assert sha256_engine() == ENGINE_SHA256_V0
    assert _sha_arquivo("digilab/ambiente.py") == SHA_AMBIENTE
    assert _sha_arquivo("digilab/frutas.py") == SHA_FRUTAS


# ================================================================== G2
def _impressao_g2(motor, interacoes) -> dict:
    """a impressao de tests/gabarito_mundo.py; as frutas so quando o motor as tem ligadas (o MotorMundo desligado no mundo da bola tem o
    resumo_frutas do MotorFrutas desligado, que o MotorAmbiente nao tem)"""
    d = gm.impressao(motor, interacoes)
    if getattr(motor, "cf", None) is not None and not motor.cf.ligada:
        bola = dict(motor.contagem_bola) if hasattr(motor, "contagem_bola") else None
        d["mundo"] = _sha(json.dumps({"frutas": None, "bola": bola}, sort_keys=True, default=repr))
    del d["motor"]
    return d


def test_g2_vidas_de_hoje_com_o_mundo_desligado(monkeypatch):
    """as 96 vidas do gabarito, com o MotorMundo desligado no lugar do MotorAmbiente (bola) e do MotorFrutasMundo (frutas); o padrao
    nao usa a cadeia do mundo e sai igual pelo codigo de sempre"""

    class MotorFrutasMundoComMundo(MotorMundo, bv.MotorFrutasMundo):
        pass

    monkeypatch.setattr(bv, "MotorAmbiente", MotorMundo)
    monkeypatch.setattr(bv, "MotorFrutasMundo", MotorFrutasMundoComMundo)
    gravado = json.loads(gm.ARQUIVO.read_text(encoding="utf-8"))
    vistos = {"MotorMundo": 0, "MotorFrutasMundoComMundo": 0}
    difs = []
    for chave, (nome_b, espec) in gm.casos():
        v = gm.BANCADAS[nome_b].vida(espec)
        nome = type(v.motor).__name__
        if nome in vistos:
            vistos[nome] += 1
            assert not v.motor.cmf.ligada and not hasattr(v.motor, "_rng_arvores")
        esperado = {k: x for k, x in gravado[chave].items() if k != "motor"}
        if _impressao_g2(v.motor, v.interacoes) != esperado:
            difs.append(chave)
    assert not difs, difs[:10]
    assert vistos["MotorMundo"] == 24 and vistos["MotorFrutasMundoComMundo"] == 48


def test_desligado_e_o_motor_frutas_sem_nada_novo():
    from digilab.ambiente import PoliticaInstintoBola
    fm = lambda p, cfg, s, cls: cls(p, cfg, s, obediencia_desligada=True)  # noqa: E731
    a = fm(PoliticaInstintoBola(CONFIG_PADRAO), CONFIG_PADRAO, 101, MotorFrutas)
    b = fm(PoliticaInstintoBola(CONFIG_PADRAO), CONFIG_PADRAO, 101, MotorMundo)
    for m in (a, b):
        m.avancar(600)
        m.observar(AcaoUsuario.ALIMENTAR)               # sem o mundo o alimentar de hoje vale
        m.avancar(300)
    assert a.estado() == b.estado() and a._estado == b._estado
    assert a._rng_ambiente.getstate() == b._rng_ambiente.getstate()
    assert a._rng_politica.getstate() == b._rng_politica.getstate()
    assert type(b.politica).__name__ == "_PoliticaComFrutas"           # nem o embrulho do mundo
    assert not hasattr(b, "_rng_arvores") and not hasattr(b, "pet")
    with pytest.raises(MundoSemChave):
        b.deixar_comida("racao", 10, 10)
    with pytest.raises(MundoSemChave):
        b.deixar_bola(10, 10)


# ================================================================== G1
def _vida(cerebro_fab, dono, estilo, semente, dias=3, orcamento=48):
    fp, fm = fabricas_mundo(CM, politica_fabrica=cerebro_fab)
    d = DonoComLugar(criar_dono(dono), estilo, semente, dono)
    return simular_vida_mundo(dono, d, fp(CONFIG_PADRAO), semente, dias, orcamento, fm, rotulo_dono=dono), fp, fm


CEREBROS = {
    "instinto": None,
    "aleatorio": lambda cfg=None: Cerebro(aleatoria, alvo_aleatorio),
    "lobos": lambda cfg=None: PoliticaLobos(cfg or CONFIG_PADRAO, CONFIG_LOBOS_APRENDIZ),
}


@pytest.mark.parametrize("cerebro", sorted(CEREBROS))
@pytest.mark.parametrize("semente", SEMENTES)
def test_g1_replay_bit_a_bit(cerebro, semente):
    for dono in DONOS:
        for estilo in ESTILOS_LUGAR:
            v, fp, fm = _vida(CEREBROS[cerebro], dono, estilo, semente)
            assert v.interacoes == 48
            r = reproduzir_mundo(LogDeEventos.de_jsonl(v.motor.log.para_jsonl()), fp, semente=semente, fabrica_motor=fm)
            assert _resumo(r) == _resumo(v.motor), (cerebro, dono, estilo)


def test_g1_cobre_o_mundo():
    """as vidas do G1 passam pelos caminhos do mundo: quedas, consumos de racao e de fruta, o achou e comeu, a bola rolando, comida
    podre, visitas e trocas de regiao"""
    tot = {"quedas": 0, "racao": 0, "fruta": 0, "achou": 0, "podre": 0, "rolagens": 0, "visitas": 0, "regioes": 0, "continuar": 0}
    for semente in SEMENTES:
        for dono in DONOS:
            for estilo in ESTILOS_LUGAR:
                m = _vida(CEREBROS["aleatorio"], dono, estilo, semente)[0].motor
                tot["quedas"] += len(m.quedas)
                tot["racao"] += sum(c["tipo"] == "racao" for c in m.consumos_mundo)
                tot["fruta"] += sum(c["tipo"] != "racao" for c in m.consumos_mundo)
                tot["achou"] += sum(c["como"] == "achou" for c in m.consumos_mundo)
                tot["podre"] += sum(c["situacao"] == "podre" for c in m.consumos_mundo)
                tot["rolagens"] += len(m.rolagens)
                tot["visitas"] += len(m.visitas)
                tot["regioes"] += len(m.regioes)
                tot["continuar"] += sum(d["alvo"] == "continuar" for d in m.decisoes_mundo)
    assert all(n > 0 for n in tot.values()), tot


# ================================================================== G-NUMS
def _quedas(m) -> list:
    return [{k: q[k] for k in ("tick", "arvore", "sorteadas", "pontos")} for q in m.quedas]


@pytest.mark.parametrize("semente", SEMENTES)
def test_g_nums_mesmas_quedas_em_qualquer_cerebro_e_dono(semente):
    base = None
    for cerebro in sorted(CEREBROS):
        for dono, estilo in (("atencioso", "perto"), ("aleatorio", "longe"), ("relapso", "comedouro")):
            m = _vida(CEREBROS[cerebro], dono, estilo, semente)[0].motor
            q = _quedas(m)
            assert q, "nenhuma queda em 3 dias"
            base = base or q
            assert q == base, (cerebro, dono, estilo)


# ================================================================== G-MEC
def test_mf2_comer_sem_comida_nao_da_fome():
    come, fica = Cerebro(sempre(AcaoPet.COMER)), Cerebro(sempre(AcaoPet.OCIOSO))
    a, b = motor_de(come, cm=SEM_QUEDAS), motor_de(fica, cm=SEM_QUEDAS)
    for m in (a, b):
        m.avancar(1500)
    assert [o.vetor_estado for o in come.vistas] == [o.vetor_estado for o in fica.vistas]
    assert a._estado == b._estado and a._rng_ambiente.getstate() == b._rng_ambiente.getstate()
    assert all(t.observacao_seguinte.vetor_estado[I_FOME] == t.observacao.vetor_estado[I_FOME] for t in come.transicoes)


def test_andar_desconta_a_energia_pela_distancia():
    c = Cerebro(sempre(AcaoPet.EXPLORAR), lambda acao, cands, perc, u: Alvo.ponto(1000, 400))
    m = motor_de(c)
    m.avancar(16)
    (acao, oc, depois), t = c.conseq[0], c.transicoes[0]
    alcance = CM.velocidade * CONFIG_PADRAO.intervalo_decisao_ticks
    assert oc["deslocamento"] == distancia(oc["para"][0] - NINHO[0], oc["para"][1] - NINHO[1])
    assert abs(oc["deslocamento"] - alcance) <= 1 and not oc["chegou"]
    e0 = t.observacao.vetor_estado[I_ENERGIA]
    esperado = max(0.0, _limitar(e0 - 0.015) - CM.custo_energia_por_subunidade * oc["deslocamento"])
    assert depois.vetor_estado[I_ENERGIA] == esperado == t.observacao_seguinte.vetor_estado[I_ENERGIA]
    assert depois.vetor_estado[I_HUMOR] == _limitar(t.observacao.vetor_estado[I_HUMOR] + 0.01)
    assert oc["energia_gasta"] == _limitar(e0 - 0.015) - esperado
    # parado nao gasta nada alem do efeito da acao
    c2 = Cerebro(sempre(AcaoPet.BRINCAR))
    m2 = motor_de(c2)
    m2.avancar(16)
    assert c2.conseq[0][1]["deslocamento"] == 0 and c2.conseq[0][1]["alvo"] is None


def test_mf1_achou_e_comeu_so_com_fome_abaixo_do_limite():
    for fome, come in ((0.80, True), (0.90, False)):
        c = Cerebro(sempre(AcaoPet.EXPLORAR), lambda acao, cands, perc, u: Alvo.ponto(NINHO[0] + 40, NINHO[1]))
        m = motor_de(c)
        m.deixar_comida("racao", NINHO[0] + 45, NINHO[1])
        m._estado = replace(m._estado, fome=fome)
        m.avancar(1)
        oc, depois = c.conseq[0][1], c.conseq[0][2]
        assert oc["chegou"]
        if come:
            assert oc["comeu"]["como"] == "achou" and oc["comeu"]["tipo"] == "racao"
            assert depois.vetor_estado[I_FOME] == min(1.0, fome + CONFIG_PADRAO.ganho_alimentar)
            assert not m.comidas
        else:
            assert oc["comeu"] is None and len(m.comidas) == 1
            assert depois.vetor_estado[I_FOME] == fome


def test_comer_vai_a_comida_e_o_obs_depois_ja_tem_tudo():
    c = Cerebro(sempre(AcaoPet.COMER))
    m = motor_de(c)
    m.deixar_comida("racao", NINHO[0] + 50, NINHO[1] + 10)
    m.avancar(1)
    acao, oc, depois = c.conseq[0]
    t = c.transicoes[0]
    assert oc["alvo"]["tipo"] == "comida" and oc["chegou"] and oc["comeu"]["situacao"] == "madura"
    f0, e0 = t.observacao.vetor_estado[I_FOME], t.observacao.vetor_estado[I_ENERGIA]
    assert depois.vetor_estado[I_FOME] == min(1.0, f0 + CONFIG_PADRAO.ganho_alimentar)       # sem o +0,05 desfeito
    assert depois.vetor_estado[I_ENERGIA] == max(0.0, e0 - CM.custo_energia_por_subunidade * oc["deslocamento"])
    assert t.observacao_seguinte == depois and depois.mundo is not None and t.observacao.mundo is not None
    assert m.pet == (NINHO[0] + 50, NINHO[1] + 10)


def test_fruta_madura_e_podre_tem_o_efeito_da_tabela():
    efeito = {"a": -0.1, "b": 0.0, "c": 0.1}
    for espera, situacao in ((0, "madura"), (CM.maduro_fruta_min // 15 + 1, "podre")):
        # dorme `espera` decisoes e depois come; so um cerebro escolhe a podre
        c = Cerebro(lambda obs, rng: AcaoPet.DORMIR if len(c.vistas) <= espera else AcaoPet.COMER,
                    lambda acao, cands, perc, u: next(a for a in cands if a.tipo == "comida"))
        m = motor_de(c, cm=SEM_QUEDAS, efeito_frutas=efeito)
        m.deixar_comida("a", NINHO[0] + 20, NINHO[1])
        m.avancar(15 * espera + 1)
        com = m.consumos_mundo[0]
        assert com["situacao"] == situacao and com["tipo"] == "a" and len(m.consumos_mundo) == 1
        if situacao == "madura":
            assert com["fome_depois"] == min(1.0, com["fome_antes"] + CM.nutricao_fruta)
            assert com["humor_depois"] == _limitar(com["humor_antes"] - 0.1)
        else:
            assert com["fome_depois"] == com["fome_antes"]
            assert com["humor_depois"] == _limitar(com["humor_antes"] + CM.efeito_podre)
        assert c.frutas == ["a"]                         # o fruta_comida da E2


def test_o_padrao_nunca_come_podre_e_a_podre_nao_tem_cheiro():
    espera = CM.maduro_racao_min // 15 + 1
    c = Cerebro(lambda obs, rng: AcaoPet.DORMIR if len(c.vistas) <= espera else AcaoPet.COMER)
    m = motor_de(c, cm=SEM_QUEDAS)
    m.deixar_comida("racao", NINHO[0] + 30, NINHO[1])
    m.avancar(15 * espera + 1)
    p = c.vistas[-1].mundo
    assert [v[1] for v in p.vistos] == ["racao_podre"] and p.cheiro == 0 and p.direcao_cheiro == 0
    assert m.consumos_mundo == [] and c.conseq[-1][1]["alvo"] is None and m.pet == NINHO


def test_frutas_caem_apodrecem_e_somem_nos_prazos():
    c = Cerebro(sempre(AcaoPet.DORMIR))
    m = motor_de(c, semente=202)
    m.avancar(4 * 1440)
    assert m.quedas
    raio = CM.raio_queda_celulas * CM.sub
    for q in m.quedas:
        arv = next(a for a in m.arvores if a["id"] == q["arvore"])
        assert CM.frutas_por_queda_min <= q["sorteadas"] <= CM.frutas_por_queda_max == 3
        assert q["tick"] % CM.passo_mundo_ticks == 0 and len(q["colocadas"]) <= q["sorteadas"]
        for x, y in q["pontos"]:
            assert distancia(x - arv["x"], y - arv["y"]) <= raio + 1 and 0 <= x < 1024 and 0 <= y < 480
    for ident in {q["arvore"] for q in m.quedas}:
        ticks = [q["tick"] for q in m.quedas if q["arvore"] == ident]
        assert all(b - a >= CM.recarga_min for a, b in zip(ticks, ticks[1:]))
    colocadas = {i for q in m.quedas for i in q["colocadas"]}
    sumidas = {s["id"]: s for s in m.sumidas}
    for i in colocadas & set(sumidas):
        s = sumidas[i]
        assert s["sumiu_em"] == s["tick_posta"] + CM.maduro_fruta_min + CM.prazo_podre_min
    assert colocadas & set(sumidas)
    for comida in m.comidas.values():
        idade = m._estado.tick - comida["tick_posta"]
        assert m.situacao(comida, m._estado.tick) == ("madura" if idade < 720 else "podre")
    # nunca mais de 4 no chao por arvore, em nenhum passo do mundo
    for q in m.quedas:
        vivas = [s for s in list(m.comidas.values()) + m.sumidas
                 if s["origem"] == q["arvore"] and s["tick_posta"] <= q["tick"] and m.situacao(s, q["tick"]) is not None]
        assert len(vivas) <= CM.max_frutas_por_arvore


def test_a_bola_rola_e_para_dentro_do_mapa():
    rolagens = 0
    for semente in SEMENTES:
        c = Cerebro(sempre(AcaoPet.BRINCAR))
        m = motor_de(c, semente=semente)
        for _ in range(40):
            m.deixar_bola(*m.pet)                         # a bola no pe do pet: ele chega e chuta
            m._estado = replace(m._estado, energia=1.0)
            m.avancar(15)
        assert m.rolagens
        for r in m.rolagens:
            (x0, y0), (x1, y1) = r["de"], r["para"]
            assert 0 <= x1 < 1024 and 0 <= y1 < 480
            assert distancia(x1 - x0, y1 - y0) <= CM.bola_max_celulas * CM.mult_bola_campo * CM.sub + 1
        b = m.bola_mundo
        fim = b["t0"] + -(-b["d"] // CM.atrito)
        assert m.bola_em(fim) == (b["x1"], b["y1"]) == m.bola_em(fim + 100)
        if b["d"] > CM.atrito:
            assert m.bola_em(b["t0"] + 1) != (b["x1"], b["y1"])
        humor = [oc["brincou_com_bola"] for _, oc, _ in c.conseq]
        assert all(humor)
        rolagens += len(m.rolagens)
    assert rolagens == 80


def test_o_canto_corta_a_bola_e_o_passo():
    assert deslocar(5, 5, 8, 400, CM) == (0, 5) and deslocar(1020, 470, 14, 400, CM) == (1023, 479)
    assert passo_ate(0, 0, 3000, 0, 60, CM) == (60, 0) and passo_ate(10, 10, 20, 20, 60, CM) == (20, 20)


class Sentinela:
    """embrulha uma rng e falha se quem a chama e codigo do digilab/mundo.py (MF-4)"""

    def __init__(self, rng) -> None:
        self._r = rng

    def __getattr__(self, nome):
        attr = getattr(self._r, nome)
        if not callable(attr):
            return attr

        def chamada(*a, **kw):
            if sys._getframe(1).f_code.co_filename.replace("\\", "/").endswith("digilab/mundo.py"):
                raise AssertionError(f"o mundo chamou {nome} numa rng do engine")
            return attr(*a, **kw)
        return chamada


def test_mf4_nenhuma_rng_do_mundo_toca_o_ambiente_nem_o_pet():
    for semente in SEMENTES:
        fp, fm = fabricas_mundo(CM, politica_fabrica=CEREBROS["aleatorio"])
        m = fm(fp(), CONFIG_PADRAO, semente)
        m._rng_ambiente, m._rng_politica = Sentinela(m._rng_ambiente), Sentinela(m._rng_politica)
        for passo in range(200):
            m.avancar(60)
            if passo % 7 == 0:
                m.deixar_comida("racao", *m.pet)
            if passo % 11 == 0:
                m.deixar_bola(*m.pet)
        assert m.consumos_mundo and m.rolagens and m.quedas


def test_continuar_o_alvo_pendente():
    longe = Alvo.ponto(900, 100)
    c = Cerebro(sempre(AcaoPet.EXPLORAR), lambda acao, cands, perc, u: longe if len(c.vistas) == 1 else None)
    m = motor_de(c, cm=SEM_QUEDAS)
    m.avancar(31)
    assert c.vistas[1].mundo.alvo_pendente == "ponto"
    oc2 = c.conseq[1][1]
    assert oc2["alvo"] == {"tipo": "continuar", "x": 900, "y": 100, "id": None, "de": "ponto"}
    # outra acao no meio: o pendente some
    c3 = Cerebro(lambda obs, rng: AcaoPet.OCIOSO if len(c3.vistas) == 2 else AcaoPet.EXPLORAR,
                 lambda acao, cands, perc, u: longe if len(c3.vistas) == 1 else None)
    m3 = motor_de(c3, cm=SEM_QUEDAS)
    m3.avancar(31)
    assert c3.vistas[1].mundo.alvo_pendente == "ponto" and c3.vistas[2].mundo.alvo_pendente is None
    assert c3.conseq[-1][1]["alvo"]["tipo"] == "vagar"


def test_alvo_invalido_falha_alto():
    for alvo in (Alvo("comida", 10, 10, 99), Alvo.ponto(2000, 10), Alvo.ponto(10.0, 10)):
        m = motor_de(Cerebro(sempre(AcaoPet.EXPLORAR), lambda acao, cands, perc, u, a=alvo: a))
        with pytest.raises(ValueError):
            m.avancar(1)
    m = motor_de(Cerebro(sempre(AcaoPet.COMER), lambda acao, cands, perc, u: Alvo.ponto(10, 10)))
    with pytest.raises(ValueError):
        m.avancar(1)


def test_u_sorteado_sempre_nas_tres_acoes():
    """numeros comuns: a rng do alvo anda uma vez por explorar, comer e brincar, haja candidato ou nao, e nunca nas outras"""
    import random as _r
    from digilab.protocol import derivar_semente
    m = motor_de(Cerebro(aleatoria))
    m.avancar(3000)
    n = sum(1 for d in m.decisoes_mundo if d["acao"] in ("explorar", "comer", "brincar"))
    ref = _r.Random(derivar_semente("alvo", 101))
    for _ in range(n):
        ref.randrange(1 << 16)
    assert 0 < n < len(m.decisoes_mundo) and ref.getstate() == m._rng_alvo.getstate()


# ================================================================== percepcao
def test_percepcao_vistos_cheiro_e_direcao():
    c = Cerebro(sempre(AcaoPet.DORMIR))
    m = motor_de(c, cm=SEM_QUEDAS)
    x, y = NINHO
    for k in range(10):
        m.deixar_comida("racao", x + 10 + k, y)
    m.deixar_comida("a", x, y - 90)
    m.deixar_comida("b", x + 200, y)                       # fora da visao, dentro do cheiro
    m.avancar(1)
    p = c.vistas[0].mundo
    assert (p.x, p.y, p.regiao) == (x, y, 0)
    assert len(p.vistos) == CM.max_vistos and [v[4] for v in p.vistos] == sorted(v[4] for v in p.vistos)
    assert all(v[4] <= CM.raio_visao_celulas * CM.sub for v in p.vistos)
    fontes = [(c_["x"], c_["y"], 64 if c_["tipo"] == "racao" else 32) for c_ in m.comidas.values()]
    assert p.cheiro == cheiro_em(x, y, fontes, CM)
    assert p.direcao_cheiro == 1                           # o cheiro mais forte a leste (L)
    assert direcao_do_cheiro(x, y, [(x, y - 16, 32)], CM)[1] == 3 and direcao_do_cheiro(x, y, [], CM) == (0, 0)
    # a conta inteira empata N e NE com a fruta a 90 ao norte (25 = 25): no empate vence a ordem fixa (NE vem antes de N)
    assert cheiro_em(x, y - 16, [(x, y - 90, 32)], CM) == cheiro_em(x + 11, y - 11, [(x, y - 90, 32)], CM)
    assert direcao_do_cheiro(x, y, [(x, y - 90, 32)], CM)[1] == 2
    assert cheiro_em(0, 0, [(100, 0, 64)], CM) == 64 * (384 - 100) // 384
    assert cheiro_em(0, 0, [(384, 0, 64)], CM) == 0
    assert c.vistas[0].bola == 0.0 and c.vistas[0].fruta == 0.0     # os campos de hoje no padrao


def test_dir16_inteira_e_simetrica():
    assert len(DIR16) == 16 and DIR16[0] == (1024, 0) and DIR16[4] == (0, -1024)
    for i, (cx, cy) in enumerate(DIR16):
        assert DIR16[(i + 8) % 16] == (-cx, -cy) and abs(cx * cx + cy * cy - 1024 * 1024) < 2 * 1024


# ================================================================== o dono
def test_deixar_comida_e_contato_e_deixar_bola_nao():
    c = Cerebro(sempre(AcaoPet.OCIOSO))
    m = motor_de(c)
    m.avancar(100)
    antes = m._estado
    m.deixar_comida("racao", 300, 200)
    assert m._estado.tick_ultimo_cuidado == 100 and m._estado.total_cuidados == antes.total_cuidados + 1
    assert m._estado.fome == antes.fome and c.dono == [(AcaoUsuario.ALIMENTAR, 100)]
    m.avancar(50)
    antes = m._estado
    m.deixar_bola(400, 200)
    assert m._estado == antes and len(c.dono) == 1
    assert [e.tipo for e in m.log][-3:] == ["deixar_comida", "avanco", "deixar_bola"]


def test_gestos_de_hoje_e_cenario_antigo_falham_alto():
    m = motor_de(Cerebro(sempre(AcaoPet.OCIOSO)))
    for acao in (AcaoUsuario.ALIMENTAR, AcaoUsuario.POR_BOLA, AcaoUsuario.TIRAR_BOLA, AcaoUsuario.OFERECER_FRUTA_A):
        with pytest.raises(GestoForaDoMundo):
            m.observar(acao)
    m.observar(AcaoUsuario.LIMPAR)                       # o resto do dono continua
    with pytest.raises(ValueError):
        motor_de(Cerebro(sempre(AcaoPet.OCIOSO)), cfg_frutas=CONFIG_FRUTAS_LIGADA)
    with pytest.raises(ValueError):
        motor_de(Cerebro(sempre(AcaoPet.OCIOSO)), cfg_bola=CONFIG_BOLA_LIGADA)
    with pytest.raises(ValueError):
        motor_de(Cerebro(sempre(AcaoPet.OCIOSO)), cfg_educacao=replace(CONFIG_EDUCACAO, ligada=True))
    with pytest.raises(ValueError):
        motor_de(Cerebro(sempre(AcaoPet.OCIOSO)), efeito_frutas={"a": 0.0})


def test_eventos_novos_validam_e_so_o_replay_do_mundo_entende():
    assert deixar_comida(5, "a", 3, 4) == Evento(5, "deixar_comida", "a|3|4") and deixar_bola(5, 0, 479).valor == "0|479"
    assert ler_deixar_comida(deixar_comida(5, "racao", 1023, 0)) == ("racao", 1023, 0)
    assert ler_deixar_bola(deixar_bola(5, 7, 8)) == (7, 8)
    for args in (("x", 1, 1), ("a", 1024, 1), ("a", 1, 480), ("a", -1, 1), ("a", 1.0, 1), ("a", True, 1)):
        with pytest.raises(ValueError):
            deixar_comida(0, *args)
    for valor in ("a|1", "a|1|2|3", "a|1.5|2", "z|1|2", "a| 1|2", "a|-1|2"):
        with pytest.raises(ValueError):
            ler_deixar_comida(Evento(0, "deixar_comida", valor))
    with pytest.raises(ValueError):
        ler_deixar_bola(Evento(0, "deixar_bola", "1|2|3"))
    m = motor_de(Cerebro(sempre(AcaoPet.OCIOSO)))
    m.avancar(10)
    m.deixar_comida("racao", 100, 100)
    from digilab.engine import reproduzir
    with pytest.raises(ValueError):
        reproduzir(m.log)
    _, fm = fabricas_mundo(CM)
    with pytest.raises(ValueError):
        reproduzir_educacao(m.log, lambda cfg=None: Cerebro(sempre(AcaoPet.OCIOSO)), fabrica_motor=fm)
    with pytest.raises(ValueError):
        reproduzir_mundo(LogDeEventos([Evento(0, "luta", "x|1")]), lambda cfg=None: Cerebro(sempre(AcaoPet.OCIOSO)),
                         fabrica_motor=fm)


def test_dono_com_lugar_por_estilo_e_numeros_comuns():
    estado = {"tick": 0, "mundo": {"pet": (500, 240)}}
    lugares = {}
    for estilo in ESTILOS_LUGAR:
        d = DonoComLugar(criar_dono("atencioso"), estilo, 101, "atencioso")
        lugares[estilo] = [d.lugar(estado) for _ in range(200)]
    assert set(lugares["comedouro"]) == {(10 * 16 + 8, 15 * 16 + 8)}
    assert all(distancia(x - 500, y - 240) <= 2 * 16 + 1 for x, y in lugares["perto"])
    assert all(distancia(x - 500, y - 240) <= 30 * 16 + 1 for x, y in lugares["longe"])
    # o ponto a 20-30 celulas so fica mais perto quando o corte do mapa o puxa para a borda
    assert all(distancia(x - 500, y - 240) >= 20 * 16 - 1 or y in (0, 479) or x in (0, 1023) for x, y in lugares["longe"])
    assert sum(distancia(x - 500, y - 240) >= 20 * 16 - 1 for x, y in lugares["longe"]) > 100
    canto = DonoComLugar(criar_dono("atencioso"), "longe", 101, "atencioso")
    assert all(0 <= x < 1024 and 0 <= y < 480 for x, y in (canto.lugar({"mundo": {"pet": (5, 5)}}) for _ in range(100)))
    # o braco nao entra: a mesma semente e o mesmo rotulo do dono dao os mesmos desvios; outro rotulo, outros
    a, b = (DonoComLugar(criar_dono("atencioso"), "perto", 101, "atencioso") for _ in range(2))
    assert [a.lugar(estado) for _ in range(50)] == [b.lugar(estado) for _ in range(50)]
    outro = DonoComLugar(criar_dono("atencioso"), "perto", 101, "relapso")
    assert [outro.lugar(estado) for _ in range(50)] != [DonoComLugar(criar_dono("atencioso"), "perto", 101,
                                                                     "atencioso").lugar(estado) for _ in range(50)]
    with pytest.raises(ValueError):
        DonoComLugar(criar_dono("atencioso"), "sofa", 101, "atencioso")


def test_o_alimentar_vira_deixar_comida_e_o_orcamento_fecha():
    for dono in DONOS:
        v, _, _ = _vida(CEREBROS["instinto"], dono, "perto", 101)
        m = v.motor
        eventos = [e for e in m.log if e.tipo != "avanco"]
        assert v.interacoes == len(eventos) == 48
        assert not any(e.tipo == "acao_usuario" and e.valor == "alimentar" for e in eventos)
        assert len(m.deixadas) == sum(e.tipo == "deixar_comida" for e in eventos) > 0


# ================================================================== o que o motor registra (plano, adendo 1, A1.8)
def test_registra_regiao_visitas_e_trocas():
    j1 = next(a for a in LAYOUT_MUNDO_PADRAO.arvores if a[0] == "J1")
    alvo = Alvo.ponto(j1[1] * 16 + 8, j1[2] * 16 + 8)
    c = Cerebro(lambda obs, rng: AcaoPet.EXPLORAR if len(c.vistas) <= 12 else AcaoPet.OCIOSO,
                lambda acao, cands, perc, u: alvo if len(c.vistas) <= 8 else Alvo.ponto(*NINHO))
    m = motor_de(c)
    m.avancar(15 * 20)
    assert len(m.decisoes_mundo) == 20
    assert [d["regiao"] for d in m.decisoes_mundo][:3] == [0, 0, 0]
    assert {(r["de"], r["para"]) for r in m.regioes} == {(0, 1), (1, 0)}
    v = m.visitas[0]
    assert v["arvore"] == "J1" and v["saida"] > v["chegada"] and v["decisoes"] >= 1
    entrou = next(d for d in m.decisoes_mundo if "J1" in d["manchas"])
    assert entrou["tick"] == v["chegada"]


def test_layout_afastado():
    assert [a[0] for a in LAYOUT_MUNDO_AFASTADO.arvores] == [a[0] for a in LAYOUT_MUNDO_PADRAO.arvores]
    cm_af = ConfigMundo(ligada=True, layout=LAYOUT_MUNDO_AFASTADO)
    for (i, x, y, f), (_, xa, ya, fa) in zip(LAYOUT_MUNDO_PADRAO.arvores, LAYOUT_MUNDO_AFASTADO.arvores):
        assert f == fa and regiao_de(x * 16, CM) == regiao_de(xa * 16, cm_af)
        _, x0, x1 = next(r for r in LAYOUT_MUNDO_PADRAO.regioes if r[1] <= x <= r[2])
        cx = (x0 + x1 + 1) // 2
        assert xa == min(x1, max(x0, cx + 2 * (x - cx))) and ya == min(29, max(0, 15 + 2 * (y - 15)))
    m = motor_de(Cerebro(sempre(AcaoPet.DORMIR)), cm=cm_af)
    m.avancar(2 * 1440)
    assert m.quedas and {a["id"]: (a["x"], a["y"]) for a in m.arvores}["J2"] == (33 * 16 + 8, 25 * 16 + 8)


def test_config_padrao_desligada():
    assert CONFIG_MUNDO.ligada is False and CM.ligada is True
    with pytest.raises(ValueError):
        ConfigMundo(celulas_x=32)
    with pytest.raises(ValueError):
        ConfigMundo(mult_queda=0.0)
