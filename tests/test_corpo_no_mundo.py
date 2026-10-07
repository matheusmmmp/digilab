"""V2, o MotorMundo no MotorCorpo (docs/TAREFA_V2_CORPO_DRIVES.md, secoes 2, 9 e 12; os estimulos do mundo do #236).

G2: com o corpo desligado na frente do MotorMundo, as vidas do mundo fisico de hoje byte a byte (tests/gabaritos/corpo_mundo_vidas_de_hoje.json,
gravado antes, com o snapshot de origin/main). G-HOJE (a) no mundo fisico: o corpo ligado, em malha aberta, contra o MotorMundo de hoje, tick
a tick. G1 com o corpo e o mundo. Os ganchos: o `consequencia_mundo` com o `obs.corpo` e os estimulos ja aplicados, o `consequencia_corpo`
uma vez por decisao. E a bancada montando o mundo fisico com o corpo. So as sementes dos testes.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import bancada_v2 as bv  # noqa: E402
import gabarito_corpo_mundo as gcm  # noqa: E402
from digilab.config import (CONFIG_CONSEQUENCIA, CONFIG_LOBOS_APRENDIZ, CONFIG_MUNDO_LIGADA, CONFIG_PADRAO,  # noqa: E402
                            LAYOUT_MUNDO_AFASTADO, ConfigCorpo)
from digilab.corpo import div_arred  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.events import LogDeEventos  # noqa: E402
from digilab.events import AcaoPet, AcaoUsuario, ler_deixar_bola, ler_deixar_comida  # noqa: E402
from digilab.instinto_mundo import PoliticaInstintoMundo  # noqa: E402
from digilab.motor_corpo import ForaDoCorpo, MotorCorpo, PercepcaoCorpo, com_corpo  # noqa: E402
from digilab.mundo import DeixarBola, DonoComLugar, MotorMundo, reproduzir_mundo, simular_vida_mundo  # noqa: E402
from digilab.policies import lobos  # noqa: E402
from digilab.policies.lobos import PoliticaLobos  # noqa: E402

CFG = CONFIG_PADRAO
CM = CONFIG_MUNDO_LIGADA
SO_QUIMICA = ConfigCorpo(ligada=True)
COM_ORGAOS = ConfigCorpo(ligada=True, digestao=True, vida=True)
DONOS = ("atencioso", "relapso", "aleatorio", "incoerente")
LUGARES = ("comedouro", "perto", "longe")
TOL = 1e-9                                  # secao 12, G-HOJE (a)
DRIVES = ("fome", "higiene", "energia", "humor")
MotorMundoCorpo = com_corpo(MotorMundo)


# ================================================================== as vidas
class DonoComBolaPerto:
    """O dono com lugar que, a cada 4 passos, troca a ultima acao do passo por deixar a bola a 2 celulas do pet (o orcamento fecha
    igual): poe a bola ao alcance, para o brincar com a bola entrar nas vidas do teste."""

    def __init__(self, base) -> None:
        self.base = base
        self.nome = base.nome

    def decidir(self, visao, rng):
        saida = list(self.base.decidir(visao, rng))
        if saida and visao.passo % 4 == 0:
            px, py = visao.estado["mundo"]["pet"]
            saida[-1] = DeixarBola(min(1023, px + 32), py)
        return saida


def _fp_instinto(cfg=None):
    return PoliticaInstintoMundo(cfg or CFG)


def _fp_lobos(cfg=None):
    return PoliticaLobos(cfg or CFG, CONFIG_LOBOS_APRENDIZ, cfg_mundo=CM)


def _fabrica(cc: ConfigCorpo | None, corpo: bool = True, cm=CM):
    if not corpo:
        return lambda p, cfg, s: MotorMundo(p, cfg, s, obediencia_desligada=True, cfg_mundo=cm)
    return lambda p, cfg, s: MotorMundoCorpo(p, cfg, s, obediencia_desligada=True, cfg_mundo=cm, cfg_corpo=cc)


def _dono(dono: str, lugar: str, semente: int, bola: bool, cm=CM):
    d = DonoComLugar(criar_dono(dono), lugar, semente, dono, cm)
    return DonoComBolaPerto(d) if bola else d


def _vida(dono: str, lugar: str, semente: int, cc: ConfigCorpo | None, fp=_fp_instinto, corpo: bool = True, dias: int = 3,
          bola: bool = False, cm=CM):
    fm = _fabrica(cc, corpo, cm)
    v = simular_vida_mundo(dono, _dono(dono, lugar, semente, bola, cm), fp(CFG), semente, dias, 16 * dias, fm, rotulo_dono=dono)
    return v.motor, fm


# ================================================================== G2
def test_g2_vidas_do_mundo_de_hoje_com_o_corpo_desligado(monkeypatch):
    """as 144 vidas do gabarito (gravado antes, com origin/main), pela bancada, com o MotorCorpo desligado na frente do MotorMundo; e as
    mesmas sem o MotorCorpo (o MotorMundo de agora, com o gancho do obs_depois)"""
    gravado = json.loads(gcm.ARQUIVO.read_text(encoding="utf-8"))
    assert len(gravado) == 144
    for com_mixin in (False, True):
        if com_mixin:
            monkeypatch.setattr(bv, "MotorMundo", MotorMundoCorpo)
        difs = []
        for chave, (nome_b, espec) in gcm.casos():
            v = gcm.BANCADAS[nome_b].vida(espec)
            m = v.motor
            assert isinstance(m, MotorCorpo) == com_mixin
            if com_mixin:
                assert not m.cc.ligada and not hasattr(m, "corpo") and "corpo" not in m.estado()
            atual = gcm.impressao(m, v.interacoes)
            if {k: x for k, x in atual.items() if k != "motor"} != {k: x for k, x in gravado[chave].items() if k != "motor"}:
                difs.append(chave)
        assert not difs, (com_mixin, difs[:10])


# ================================================================== G-HOJE (a), malha aberta no mundo fisico
class Forcada:
    """O pet de teste: as acoes de uma vida de hoje, na ordem; o alvo e o padrao do motor. Guarda as transicoes (o sinal do N3)."""

    nome = "forcada"

    def __init__(self, acoes) -> None:
        self._acoes = list(acoes)
        self.transicoes = []

    def agir(self, obs, rng):
        return self._acoes.pop(0)

    def observar(self, t) -> None:
        self.transicoes.append(t)

    def receber_acao_dono(self, acao, tick) -> None:
        return None

    def estado_interno(self) -> dict:
        return {"nome": self.nome}


def _malha_aberta(dono: str, lugar: str, semente: int, cc: ConfigCorpo, bola: bool = False, cm=CM) -> dict:
    """A vida de hoje no mundo fisico, rejogada com as acoes do pet forcadas em dois motores lado a lado: o MotorMundo de hoje (float) e o
    mesmo com o corpo, tick a tick, com os mesmos gestos do dono no mesmo lugar."""
    hoje, _ = _vida(dono, lugar, semente, None, corpo=False, bola=bola, cm=cm)
    acoes = [a for _, a in hoje.acoes_recentes(10**9)]
    fa, fb = Forcada(acoes), Forcada(acoes)
    a = _fabrica(None, corpo=False, cm=cm)(fa, CFG, semente)
    b = _fabrica(cc, cm=cm)(fb, CFG, semente)
    t = b.corpo.t
    erro = {d: 0.0 for d in DRIVES + ("saude",)}
    viradas = []

    def confere(no_tick: bool) -> None:
        ea, eb = a._estado, b._estado
        assert (ea.tick, ea.sujeira, ea.dormindo) == (eb.tick, eb.sujeira, eb.dormindo)
        assert a.pet == b.pet
        for d in erro:
            erro[d] = max(erro[d], abs(getattr(ea, d) - getattr(eb, d)))
        if no_tick and ea.em_privacao(CFG) != b.corpo.em_privacao():
            viradas.append((ea.tick, dict(b.corpo.q)))
        for d in DRIVES:
            assert abs(getattr(ea, d) - getattr(eb, d)) <= TOL, (dono, lugar, semente, ea.tick, d)
        limite = TOL + len(viradas) * (t.dano_privacao - t.dano_cura) / b.corpo.C
        assert abs(ea.saude - eb.saude) <= limite, (dono, lugar, semente, ea.tick)

    for ev in hoje.log:
        if ev.tipo == "avanco":
            for _ in range(int(ev.valor)):
                a._avancar(1)
                b._avancar(1)
                confere(True)
        elif ev.tipo == "acao_usuario":
            acao = AcaoUsuario(ev.valor)
            a._aplicar_acao_usuario(acao)
            b._aplicar_acao_usuario(acao)
            confere(False)
        elif ev.tipo == "deixar_comida":
            a._aplicar_deixar_comida(*ler_deixar_comida(ev))
            b._aplicar_deixar_comida(*ler_deixar_comida(ev))
            confere(False)
        elif ev.tipo == "deixar_bola":
            a._aplicar_deixar_bola(*ler_deixar_bola(ev))
            b._aplicar_deixar_bola(*ler_deixar_bola(ev))
            confere(False)
        else:
            raise ValueError(ev.tipo)
    assert a._estado == hoje._estado, "o motor de hoje com as acoes forcadas tem de ser a vida de hoje"
    assert a._rng_ambiente.getstate() == b._rng_ambiente.getstate(), "o corpo nao sorteia"
    ra, rb = a.resumo_mundo_fisico(), b.resumo_mundo_fisico()
    for k in ("pet", "bola", "comidas", "quedas", "sumidas", "deixadas", "bolas_deixadas", "rolagens", "visitas", "rngs"):
        assert ra[k] == rb[k], k
    assert [(c["id"], c["situacao"], c["como"]) for c in ra["consumos"]] == [(c["id"], c["situacao"], c["como"]) for c in rb["consumos"]]
    S, ganho = 1024, CONFIG_CONSEQUENCIA.ganho
    sinais = [(lobos.sinal_homeostatico(x, S, CONFIG_CONSEQUENCIA), lobos.sinal_homeostatico(y, S, CONFIG_CONSEQUENCIA))
              for x, y in zip(fa.transicoes, fb.transicoes)]
    return {"erro": erro, "viradas": viradas, "limiar": t.limiar_privacao, "sinais": sinais, "folga": 3 * div_arred(ganho * (2 * S + 1), S),
            "motor": b, "hoje": a}


@pytest.mark.parametrize("cc", [SO_QUIMICA, COM_ORGAOS], ids=["quimica", "orgaos"])
def test_g_hoje_a_malha_aberta_no_mundo_fisico(cc):
    total = iguais = 0
    for dono in DONOS:
        for lugar in LUGARES:
            for semente in (101, 202):
                r = _malha_aberta(dono, lugar, semente, cc)
                assert all(r["erro"][d] <= TOL for d in DRIVES), r["erro"]
                for _, q in r["viradas"]:              # toda virada do receptor de privacao e um quimico exatamente no limiar
                    assert any(q[n] == r["limiar"] for n in ("fome", "desconforto", "cansaco")), q
                for x, y in r["sinais"]:
                    assert abs(x - y) <= r["folga"], (x, y)
                total += len(r["sinais"])
                iguais += sum(x == y for x, y in r["sinais"])
    assert total and iguais / total >= 0.99, (iguais, total)


def test_g_hoje_a_cobre_os_estimulos_do_mundo():
    """a malha aberta passa pelo andar, a racao, a fruta, o achou e comeu, o comer sem comida e a bola; e no layout afastado"""
    vistos = set()
    for semente in (101, 202, 303):
        r = _malha_aberta("atencioso", "perto", semente, COM_ORGAOS, bola=True)
        m = r["motor"]
        vistos |= {(c["tipo"] if c["tipo"] == "racao" else "fruta", c["como"]) for c in m.consumos_mundo}
        if m.rolagens:
            vistos.add("bola")
        if any(d["acao"] == "comer" and d["comeu"] is None for d in m.decisoes_mundo):
            vistos.add("comer_sem_comida")
        if any(d["deslocamento"] > 0 for d in m.decisoes_mundo):
            vistos.add("andar")
        assert m.corpo.digerido_total > 0
    assert {("racao", "comer"), ("fruta", "comer"), "bola", "comer_sem_comida", "andar"} <= vistos, vistos
    assert any(isinstance(x, tuple) and x[1] == "achou" for x in vistos), vistos
    r = _malha_aberta("aleatorio", "longe", 202, SO_QUIMICA, cm=__import__("dataclasses").replace(CM, layout=LAYOUT_MUNDO_AFASTADO))
    assert r["motor"].quedas


# ================================================================== os ganchos
class ComGanchos(PoliticaInstintoMundo):
    """O instinto do mundo com os dois ganchos, que so anotam"""

    def __init__(self, *a, **kw) -> None:
        super().__init__(*a, **kw)
        self.decisoes = 0
        self.mundo = []
        self.corpo = []

    def agir(self, obs, rng):
        self.decisoes += 1
        return super().agir(obs, rng)

    def consequencia_mundo(self, acao, ocorrido, obs_depois) -> None:
        self.mundo.append((acao, ocorrido, obs_depois))

    def consequencia_corpo(self, acao, ocorrido, obs_depois) -> None:
        self.corpo.append((acao, ocorrido, obs_depois))


def test_ganchos_o_mundo_ve_o_corpo_com_os_estimulos_aplicados():
    capturado = {}

    class Espiao(MotorMundoCorpo):
        def _consequencia(self, acao):
            self._ult = super()._consequencia(acao)
            return self._ult

        def _observacao_depois_mundo(self):
            o = super()._observacao_depois_mundo()
            if self._ult is not None:                   # o mundo so chama o consequencia_mundo nas decisoes com alvo
                capturado.setdefault("pares", []).append((o, dict(self.corpo.q), self._estado))
            return o

    for semente in (101, 202):
        fp = lambda cfg=None: ComGanchos(cfg or CFG)  # noqa: E731
        fm = lambda p, cfg, s: Espiao(p, cfg, s, obediencia_desligada=True, cfg_mundo=CM, cfg_corpo=COM_ORGAOS)  # noqa: E731
        capturado.clear()
        v = simular_vida_mundo("atencioso", _dono("atencioso", "perto", semente, True), fp(CFG), semente, 3, 48, fm,
                               rotulo_dono="atencioso")
        m = v.motor
        cerebro = m._pm_cerebro()
        n = len(m.acoes_recentes(10**9))
        # o consequencia_corpo: uma chamada por decisao, sempre; o consequencia_mundo: so nas de explorar, comer e brincar
        assert cerebro.decisoes == n == len(cerebro.corpo) == m.consequencias > 0
        com_alvo = [d for d in m.decisoes_mundo if d["acao"] in ("explorar", "comer", "brincar")]
        assert len(cerebro.mundo) == len(com_alvo) > 0
        for (acao, oc, depois), (o, q, e) in zip(cerebro.mundo, capturado["pares"]):
            assert depois is o and isinstance(depois.corpo, PercepcaoCorpo) and depois.mundo is not None
            # os receptores e os drives do obs_depois sao os do corpo depois dos estimulos da propria acao
            assert depois.corpo.energia == 1024 - div_arred(q["cansaco"] * 1024, m.corpo.C)
        # o ocorrido do consequencia_corpo traz os estimulos do mundo, na ordem: o pet, o andar, a comida, a bola
        estimulos = [oc["estimulos"] for _, oc, _ in cerebro.corpo]
        for (acao, oc, _), est in zip(cerebro.corpo, estimulos):
            assert est[0] == ("pet", acao.value)
            nomes = [x[0] for x in est[1:]]
            assert nomes == sorted(nomes, key=["andar", "comida", "bola"].index)
            if acao.value in ("explorar", "comer", "brincar"):
                assert nomes[0] == "andar"
            else:
                assert nomes == []
        assert sum(any(x[0] == "comida" for x in est) for est in estimulos) == len(m.consumos_mundo) > 0
        assert sum(("bola",) in est for est in estimulos) == len(m.rolagens)


def test_o_andar_a_comida_e_a_bola_mexem_no_corpo_na_conta_exata():
    """por decisao com alvo, de antes a depois da consequencia do mundo: o cansaco sobe 75 por subunidade andada; a racao madura tira
    202500 da fome (o alimentar), a fruta madura 67500, a podre poe 45000 de tristeza e nada na fome; a bola tira 67500 da tristeza.
    Sem a digestao, direto no quimico (cortado em [0, C])."""
    deltas = []

    class Espiao(MotorMundoCorpo):
        def _consequencia(self, acao):
            antes = dict(self.corpo.q)
            oc = super()._consequencia(acao)
            if oc is not None:
                deltas.append((antes, dict(self.corpo.q), oc))
            return oc

    for semente in (101, 202, 303):
        fm = lambda p, cfg, s: Espiao(p, cfg, s, obediencia_desligada=True, cfg_mundo=CM, cfg_corpo=SO_QUIMICA)  # noqa: E731
        fp = lambda cfg=None: ComGanchos(cfg or CFG)  # noqa: E731
        simular_vida_mundo("atencioso", _dono("atencioso", "perto", semente, True), fp(CFG), semente, 3, 48, fm, rotulo_dono="atencioso")
    C = 450000
    corta = lambda x: min(C, max(0, x))  # noqa: E731
    vistos = set()
    for antes, depois, oc in deltas:
        assert depois["cansaco"] == corta(antes["cansaco"] + 75 * oc["deslocamento"])
        fome, tristeza = antes["fome"], antes["tristeza"]
        if oc["comeu"] is not None:
            c = oc["comeu"]
            if c["situacao"] == "podre":
                tristeza = corta(tristeza + 45000)
                vistos.add("podre")
            elif c["tipo"] == "racao":
                fome = corta(fome - 202500)
                vistos.add("racao")
            else:
                fome = corta(fome - 67500)
                vistos.add("fruta")
        if oc["brincou_com_bola"]:
            tristeza = corta(tristeza - 67500)
            vistos.add("bola")
        assert (depois["fome"], depois["tristeza"]) == (fome, tristeza), oc
        assert depois["desconforto"] == antes["desconforto"] and depois["dano"] == antes["dano"]
    assert {"racao", "bola"} <= vistos, vistos
    assert any(oc["deslocamento"] > 0 for _, _, oc in deltas)


def test_mf2_comer_sem_comida_nao_da_fome_no_corpo():
    """o comer sem comida no alcance: o corpo nao recebe o efeito do comer de hoje (acao_pet com o mundo), e a consequencia do mundo nao
    mexe na fome"""
    vistos = []

    class Espiao(MotorMundoCorpo):
        def _decidir(self, intervalo, produzidas):
            antes = self.corpo.q["fome"]
            super()._decidir(intervalo, produzidas)
            ult = self.decisoes_mundo[-1]
            if ult["acao"] == "comer" and ult["comeu"] is None:
                vistos.append((antes, self.corpo.q["fome"]))

    for dono, lugar, semente in (("relapso", "longe", 202), ("aleatorio", "longe", 101), ("relapso", "comedouro", 303)):
        fm = lambda p, cfg, s: Espiao(p, cfg, s, obediencia_desligada=True, cfg_mundo=CM, cfg_corpo=SO_QUIMICA)  # noqa: E731
        simular_vida_mundo(dono, _dono(dono, lugar, semente, False), _fp_instinto(CFG), semente, 3, 48, fm, rotulo_dono=dono)
    assert vistos, "as vidas tem de ter um comer sem comida"
    assert all(a == b for a, b in vistos)


def test_bypass_no_mundo_falha_alto():
    """um MotorMundo que escreve um drive fora dos estimulos da consequencia (a higiene) falha alto"""

    class IntrusoMundo(MotorMundo):
        def _consequencia(self, acao):
            from dataclasses import replace as rp
            oc = super()._consequencia(acao)
            self._estado = rp(self._estado, higiene=max(0.0, self._estado.higiene - 0.01))
            return oc

    fm = lambda p, cfg, s: com_corpo(IntrusoMundo)(p, cfg, s, obediencia_desligada=True, cfg_mundo=CM, cfg_corpo=SO_QUIMICA)  # noqa: E731
    with pytest.raises(ForaDoCorpo):
        simular_vida_mundo("atencioso", _dono("atencioso", "perto", 101, False), _fp_instinto(CFG), 101, 1, 16, fm,
                           rotulo_dono="atencioso")


# ================================================================== G1
@pytest.mark.parametrize("cc", [SO_QUIMICA, COM_ORGAOS], ids=["quimica", "orgaos"])
def test_g1_replay_bit_a_bit_com_o_corpo_no_mundo(cc):
    for fp in (_fp_instinto, _fp_lobos):
        for dono, lugar, bola in (("atencioso", "perto", True), ("aleatorio", "longe", False), ("relapso", "comedouro", False)):
            m, fm = _vida(dono, lugar, 202, cc, fp=fp, bola=bola)
            r = reproduzir_mundo(m.log, fp, CFG, 202, fabrica_motor=fm)
            for x in (m, r):
                x._resumo = json.dumps({"estado": x.estado(), "q": x.corpo.q, "bruto": repr(x._estado), "mundo": x.resumo_mundo_fisico(),
                                        "politica": x.politica.estado_interno(), "rng": x._rng_ambiente.getstate(),
                                        "acoes": x.acoes_recentes(10**9)}, sort_keys=True, default=repr)
            assert m._resumo == r._resumo, (fp.__name__, dono, lugar)


# ================================================================== a bancada monta o mundo fisico com o corpo
def test_a_bancada_monta_o_mundo_fisico_com_o_corpo(monkeypatch):
    """sem mudar a bancada: a fabrica dela com o MotorMundo trocado pelo MotorMundo com o corpo ligado. Os bracos P0 (lobos e instinto),
    P0z, P1 e P3 rodam, o P1 aprende pela consequencia e o G1 da bancada passa (o replay do log pelo reproduzir_mundo)"""

    class ComCorpo(MotorMundoCorpo):
        def __init__(self, *a, **kw) -> None:
            super().__init__(*a, cfg_corpo=COM_ORGAOS, **kw)

    monkeypatch.setattr(bv, "MotorMundo", ComCorpo)
    b = bv.Bancada(2, 32)
    for braco, cerebro in (("P0", "lobos"), ("P0", "instinto"), ("P0z", "lobos"), ("P1", "lobos"), ("P3", "lobos")):
        for mundo in ("fisico", "fisico_afastado"):
            v = b.vida(bv.EspecVida("atencioso", braco, 101, None, mundo, cerebro, "perto"))
            m = v.motor
            assert isinstance(m, ComCorpo) and m.cc.ligada and "corpo" in m.estado()
            r = b.rejogar(LogDeEventos.de_jsonl(m.log.para_jsonl()), v.espec)
            assert bv.resumo_motor(r) == bv.resumo_motor(m) and bv._interno(r) == bv._interno(m)
            assert json.dumps(r.estado(), sort_keys=True, default=repr) == json.dumps(m.estado(), sort_keys=True, default=repr)
            assert r.corpo.q == m.corpo.q and r.resumo_mundo_fisico() == m.resumo_mundo_fisico()
            if braco == "P1":
                assert m.politica.estado_interno() != b.vida(bv.EspecVida("atencioso", "P0", 101, None, mundo, "lobos", "perto")
                                                              ).motor.politica.estado_interno()
