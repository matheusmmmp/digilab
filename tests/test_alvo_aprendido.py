"""V2, dois pets, etapa 4, primeira metade: o alvo aprendido no cerebro A (docs/TAREFA_V2_DOIS_PETS.md; docs/futuro/dois_pets.md,
secao 8, DP-8).

Com `ConfigLobos.alvo_aprendido`, o `escolher_alvo` dos lobos escolhe a CLASSE do candidato (comida, comida podre, cheiro, vagar, casa,
continuar, bola; e `seguir` e `onde_comeu`, que o motor oferece a partir da etapa 3 do A). O peso efetivo de cada classe presente e
max(0, w) / S, mais 1 na classe do alvo padrao do motor; o w comeca em `w0_alvo` (o peso pequeno). Aprende so pela consequencia, pela
regra da sub-decisao da fruta. Gates:
- G2: com a chave desligada, a vida de hoje (os gabaritos do mundo, na suite; aqui, o gancho devolve None);
- no prior, o P0 com lobos e o instinto do mundo byte a byte (o P0 tem o aprendizado desligado e usa o padrao do motor);
- G1: a vida do P1 com a chave, rejogada do log;
- a conta exata do alvo aprendido; o sinal do dono nao mexe nele;
- as falhas altas.
So as sementes dos testes. A percepcao social e o modelo dos outros esperam a etapa 3 do A.
"""
from __future__ import annotations

import hashlib
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
from digilab.config import (CONFIG_BANHEIRO_LIGADA, CONFIG_CONSEQUENCIA, CONFIG_CORPO_BANHEIRO, CONFIG_LOBOS,  # noqa: E402
                            CONFIG_MUNDO_LIGADA, CONFIG_PADRAO, ConfigLobos)
from digilab.donos import criar_dono  # noqa: E402
from digilab.events import AcaoPet, AcaoUsuario  # noqa: E402
from digilab.instinto_mundo import PoliticaInstintoMundo  # noqa: E402
from digilab.mundo import (Alvo, DonoComLugar, MotorMundo, PercepcaoMundo, alvo_padrao_de, fabricas_mundo,  # noqa: E402
                           reproduzir_mundo, simular_vida_mundo)
from digilab.policies import lobos as lb  # noqa: E402
from digilab.policies.lobos import PoliticaLobos, sinal_homeostatico  # noqa: E402
from digilab.policy import Observacao, Transicao  # noqa: E402

CM = CONFIG_MUNDO_LIGADA
S = CONFIG_LOBOS.escala
SEMENTES = (101, 202)
DONOS = ("atencioso", "aleatorio")
LUGARES = ("comedouro", "perto", "longe")
CL_T3 = bv.cfg_lobos_do_ponto("T3")
COM_ALVO = replace(CL_T3, alvo_aprendido=True)
P0_COM_ALVO = replace(CONFIG_LOBOS, alvo_aprendido=True)
CC = CONFIG_CONSEQUENCIA


# ================================================================== ajudas
def resumo(m, politica: bool = False) -> str:
    d = {"log": m.log.para_jsonl(), "estado": m.estado(), "estado_bruto": repr(m._estado), "acoes": m.acoes_recentes(10**9),
         "rng_ambiente": m._rng_ambiente.getstate(), "rng_politica": m._rng_politica.getstate(), "mundo": m.resumo_mundo_fisico()}
    if politica:
        d["politica"] = m.politica.estado_interno()
    return hashlib.sha256(json.dumps(d, sort_keys=True, default=repr).encode()).hexdigest()


def vida(fab, dono="atencioso", lugar="perto", semente=101, dias=3):
    fp, fm = fabricas_mundo(CM, fab)
    dl = DonoComLugar(criar_dono(dono), lugar, semente, dono, CM)
    return simular_vida_mundo(dono, dl, fp(CONFIG_PADRAO), semente, dias, 16 * dias, fm, rotulo_dono=dono), fp, fm


def braco(rotulo: str, cl: ConfigLobos):
    return lambda cfg=None: bv.PoliticaDoBraco(PoliticaLobos(cfg or CONFIG_PADRAO, cl, cfg_mundo=CM), bv.braco_de(rotulo), CC)


def perc(vistos=(), cheiro=0, direcao=0) -> PercepcaoMundo:
    vs = tuple(sorted(((i + 1 if t != "bola" else 0), t, 5 * (i + 1), 0, 5 * (i + 1)) for i, t in enumerate(vistos)))
    return PercepcaoMundo(200, 240, 0, tuple(sorted(vs, key=lambda v: (v[4], v[1], v[0]))), cheiro, direcao, None)


def obs_de(fome=0.8, energia=0.7, humor=0.5, ticks=30) -> Observacao:
    return Observacao(vetor_estado=(fome, 0.8, energia, humor, 1.0, 0.0, 0.0, 0.5), ticks_desde_cuidado=ticks, total_cuidados=0)


class U:
    """uma rng que devolve sempre o mesmo u"""

    def __init__(self, u: float) -> None:
        self.u = u

    def random(self) -> float:
        return self.u


# ================================================================== a chave e a tabela
def test_tabela_de_classes_e_pesos():
    p = PoliticaLobos(CONFIG_PADRAO, COM_ALVO, cfg_mundo=CM)
    sem = PoliticaLobos(CONFIG_PADRAO, CL_T3, cfg_mundo=CM)
    chaves = {f"{r}:{a.value}" for r, acoes in lb.REGRAS_ALVO.items() for a in acoes}
    assert set(p._prior_alvo_mundo) == chaves
    assert all(t == {c: COM_ALVO.w0_alvo for c in lb.CLASSES_ALVO[AcaoPet(k.split(":")[1])]} for k, t in p._prior_alvo_mundo.items())
    assert lb.CLASSES_ALVO[AcaoPet.EXPLORAR][-2:] == ("seguir", "onde_comeu")      # o lugar das classes da etapa 3
    assert p.n_pesos() - sem.n_pesos() == 4 + 4 + 8 + 8 + 12 == 36
    assert p.n_pesos() == 756 + 36 and COM_ALVO.w0_alvo == S // 16
    e = p.estado_interno()
    assert e["pesos_alvo_mundo"] == e["pesos_alvo_mundo_prior"] and "pesos_alvo_mundo" not in sem.estado_interno()


def test_falhas_altas_da_chave():
    with pytest.raises(ValueError, match="sem o mundo fisico"):
        PoliticaLobos(CONFIG_PADRAO, COM_ALVO)
    with pytest.raises(ValueError, match="w0_alvo"):
        PoliticaLobos(CONFIG_PADRAO, replace(COM_ALVO, w0_alvo=-1), cfg_mundo=CM)
    with pytest.raises(ValueError, match="teto"):              # o corpo com o banheiro ja usa 998 de 1000
        PoliticaLobos(CONFIG_PADRAO, COM_ALVO, cfg_mundo=CM, cfg_corpo=CONFIG_CORPO_BANHEIRO, cfg_banheiro=CONFIG_BANHEIRO_LIGADA)


def test_o_padrao_do_motor_e_a_funcao_pura(monkeypatch):
    """o MotorMundo escolhe o padrao pela mesma funcao que o cerebro le (mundo.alvo_padrao_de), em toda decisao com alvo do P0"""
    import digilab.mundo as mundo
    chamadas = []
    original = mundo.alvo_padrao_de

    def espiao(acao, cands, p, cmf):
        a = original(acao, cands, p, cmf)
        chamadas.append((acao, a))
        return a
    monkeypatch.setattr(mundo, "alvo_padrao_de", espiao)
    v, _, _ = vida(braco("P0", P0_COM_ALVO), "aleatorio", "longe", 202, dias=2)
    com_alvo = [d for d in v.motor.decisoes_mundo if d["acao"] in ("explorar", "comer", "brincar")]
    assert com_alvo and len(chamadas) == len(com_alvo)
    assert [a.value for a, _ in chamadas] == [d["acao"] for d in com_alvo]


# ================================================================== G2 e o P0
def test_g2_chave_desligada_devolve_none():
    p = PoliticaLobos(CONFIG_PADRAO, CL_T3, cfg_mundo=CM)
    p.agir(obs_de(), U(0.5))
    assert p.escolher_alvo(AcaoPet.EXPLORAR, [Alvo("vagar", 1, 1), Alvo("casa", 2, 2)], perc(), 65535) is None
    assert "alvo_mundo" not in p._registro_decisao


@pytest.mark.parametrize("dono", DONOS)
def test_p0_com_a_chave_e_o_instinto_do_mundo_byte_a_byte(dono):
    """no prior, o P0 (o aprendizado desligado) com a chave usa o padrao do motor: e o instinto do mundo, byte a byte"""
    for lugar in LUGARES:
        for semente in SEMENTES:
            a, _, _ = vida(lambda cfg=None: PoliticaInstintoMundo(cfg or CONFIG_PADRAO), dono, lugar, semente)
            b, _, _ = vida(braco("P0", P0_COM_ALVO), dono, lugar, semente)
            assert resumo(a.motor) == resumo(b.motor), (dono, lugar, semente)
            assert b.motor.politica.estado_interno()["pesos_alvo_mundo"] == b.motor.politica.estado_interno()["pesos_alvo_mundo_prior"]


# ================================================================== G1 e a vida do P1
def test_g1_e_a_vida_do_p1_com_o_alvo_aprendido():
    for semente in SEMENTES:
        v, fp, fm = vida(braco("P1", COM_ALVO), "atencioso", "perto", semente, dias=4)
        r = reproduzir_mundo(v.motor.log, fp, CONFIG_PADRAO, semente, fm)
        assert resumo(r, True) == resumo(v.motor, True)
        e = v.motor.politica.estado_interno()
        assert e["pesos_alvo_mundo"] != e["pesos_alvo_mundo_prior"]                 # aprendeu
        escolhas = [m["alvo_aprendido"] for m in e["motivos"] if "alvo_aprendido" in m]
        assert escolhas and any(x["alvo"] not in (None, x["padrao"]) for x in escolhas)   # e tentou fora do padrao
        sem, _, _ = vida(braco("P1", CL_T3), "atencioso", "perto", semente, dias=4)
        assert resumo(sem.motor) != resumo(v.motor)


# ================================================================== a conta exata
def _explorar(p: PoliticaLobos, cands, percepcao, u: int):
    a = p.agir(obs_de(), U(0.5))                       # tempo livre: 3, 3,4, 2,5, 1; u 0,5 cai no explorar
    assert a is AcaoPet.EXPLORAR and p.ultima_regra == "tempo_livre"
    return p.escolher_alvo(a, cands, percepcao, u)


def test_conta_exata_pela_consequencia():
    """casa (a classe que o padrao nao usa) sorteada no fim da roleta; o sinal da consequencia, na regra da fruta, sobe ou desce o
    peso dela, e o da classe do padrao vai ao contrario"""
    p = PoliticaLobos(CONFIG_PADRAO, COM_ALVO, cfg_mundo=CM)
    cands = [Alvo("vagar", 300, 240), Alvo("casa", 40, 40)]
    pm = perc()
    assert alvo_padrao_de(AcaoPet.EXPLORAR, cands, pm, CM).tipo == "vagar"
    # pesos: vagar 1 + 64/1024 = 1,0625; casa 0,0625. u / 2^16 x 1,125 >= 1,0625 desde u = 61896
    assert _explorar(PoliticaLobos(CONFIG_PADRAO, COM_ALVO, cfg_mundo=CM), cands, pm, 61895).tipo == "vagar"
    alvo = _explorar(p, cands, pm, 61896)
    assert alvo.tipo == "casa"
    sub = p._registro_decisao["alvo_mundo"]
    assert sub["candidatos"] == ("vagar", "casa") and sub["acao"] == "casa"
    assert sub["P"] == {"vagar": lb.arred(1.0625 / 1.125 * S), "casa": lb.arred(0.0625 / 1.125 * S)}
    assert sub["W"] == {"vagar": 1088, "casa": 64}
    antes = obs_de()
    depois = obs_de(energia=0.66)
    t = Transicao(antes, AcaoPet.EXPLORAR, depois)
    f = sinal_homeostatico(t, S, CC)
    p.observar_consequencia(t, f, CC)
    assert p._pesos_alvo_mundo == p._prior_alvo_mundo                        # o credito espera o gancho do mundo
    p.consequencia_mundo(AcaoPet.EXPLORAR, {"acao": "explorar", "alvo": {"tipo": "casa"}, "chegou": False, "deslocamento": 0,
                                            "comeu": None, "brincou_com_bola": False}, depois)
    assert f < 0
    tab = p._pesos_alvo_mundo["tempo_livre:explorar"]
    esperado = dict(p._prior_alvo_mundo["tempo_livre:explorar"])
    for c in sub["candidatos"]:
        fator = (S if c == "casa" else 0) - sub["P"][c]
        esperado[c] += lb.div_arred(f * COM_ALVO.passo * S * fator, S * S * sub["W"][c])
    assert tab == esperado and tab["casa"] < COM_ALVO.w0_alvo and tab["vagar"] > COM_ALVO.w0_alvo
    assert all(t2 == p._prior_alvo_mundo[k] for k, t2 in p._pesos_alvo_mundo.items() if k != "tempo_livre:explorar")
    assert p.estado_interno()["aprendizado"]["ultima"]["alvo_mundo"]["acao"] == "casa"


def test_o_dono_nao_ensina_o_alvo():
    """o P3: o elogio depois de uma decisao com alvo aprendido muda a decisao, nao o alvo (so a consequencia o ensina)"""
    p = PoliticaLobos(CONFIG_PADRAO, COM_ALVO, cfg_mundo=CM)
    cands = [Alvo("vagar", 300, 240), Alvo("casa", 40, 40)]
    _explorar(p, cands, perc(), 65535)
    depois = obs_de()
    p.observar(Transicao(obs_de(), AcaoPet.EXPLORAR, depois))
    p.consequencia_mundo(AcaoPet.EXPLORAR, {"acao": "explorar", "alvo": {"tipo": "casa"}, "chegou": False, "deslocamento": 0,
                                            "comeu": None, "brincou_com_bola": False}, depois)
    pesos = {g: {a: list(v) for a, v in t.items()} for g, t in p._pesos.items()}
    p.receber_acao_dono(AcaoUsuario.ELOGIAR, 40)
    assert p._pesos != pesos and p._pesos_alvo_mundo == p._prior_alvo_mundo


def test_classes_da_comida_e_as_da_etapa_3():
    """a comida boa e a podre sao classes separadas (o padrao nunca come a podre); seguir e onde_comeu ja tem lugar na tabela"""
    p = PoliticaLobos(CONFIG_PADRAO, COM_ALVO, cfg_mundo=CM)
    p.agir(obs_de(), U(0.5))
    pm = perc(["a_podre", "racao"])                    # ids 1 (podre) e 2
    cands = [Alvo("comida", 205, 240, 1), Alvo("comida", 210, 240, 2)]
    p._ultima_regra, p._registro_decisao["acao"] = "fruta_no_cenario", AcaoPet.COMER
    a = p.escolher_alvo(AcaoPet.COMER, cands, pm, 0)
    sub = p._registro_decisao["alvo_mundo"]
    assert sub["candidatos"] == ("comida_podre", "comida") and alvo_padrao_de(AcaoPet.COMER, cands, pm, CM).id == 2
    assert sub["P"]["comida"] > sub["P"]["comida_podre"] and a.id in (1, 2)
    # explorar com os candidatos sociais da etapa 3 (o motor ainda nao os da): a tabela os aceita
    p2 = PoliticaLobos(CONFIG_PADRAO, COM_ALVO, cfg_mundo=CM)
    cands = [Alvo("vagar", 300, 240), Alvo("casa", 40, 40), Alvo("seguir", 220, 250), Alvo("onde_comeu", 100, 100)]
    assert _explorar(p2, cands, perc(), 65535).tipo == "onde_comeu"
    assert p2._registro_decisao["alvo_mundo"]["candidatos"] == ("vagar", "casa", "seguir", "onde_comeu")


def test_falhas_altas_do_alvo():
    p = PoliticaLobos(CONFIG_PADRAO, COM_ALVO, cfg_mundo=CM)
    p.agir(obs_de(), U(0.5))
    with pytest.raises(ValueError, match="fora das de explorar"):
        p.escolher_alvo(AcaoPet.EXPLORAR, [Alvo("vagar", 1, 1), Alvo("bola", 2, 2, 0)], perc(), 0)
    with pytest.raises(ValueError, match="u do alvo"):
        p.escolher_alvo(AcaoPet.EXPLORAR, [Alvo("vagar", 1, 1)], perc(), 1 << 16)
    with pytest.raises(RuntimeError, match="sem tabela"):
        p.escolher_alvo(AcaoPet.COMER, [Alvo("cheiro", 1, 1)], perc([], 30, 2), 0)      # comer nao e candidato no tempo livre
    # sem alvo padrao (comer sem nada visto e sem cheiro), None, como hoje
    p._ultima_regra, p._registro_decisao["acao"] = "fome_moderada", AcaoPet.COMER
    assert p.escolher_alvo(AcaoPet.COMER, [], perc(), 0) is None and "alvo_mundo" not in p._registro_decisao


def test_mesmas_chamadas_mesmo_estado():
    def rodar() -> str:
        rng = random.Random(7)
        p = PoliticaLobos(CONFIG_PADRAO, COM_ALVO, cfg_mundo=CM)
        for _ in range(300):
            o = obs_de(energia=rng.uniform(0.3, 1.0), humor=rng.random())
            a = p.agir(o, rng)
            if a is AcaoPet.EXPLORAR and p.ultima_regra == "tempo_livre":
                p.escolher_alvo(a, [Alvo("vagar", 300, 240), Alvo("casa", 40, 40)], perc(), rng.randrange(1 << 16))
            d = obs_de(energia=max(0.0, o.vetor_estado[2] - 0.02), humor=o.vetor_estado[3])
            t = Transicao(o, a, d)
            p.observar_consequencia(t, sinal_homeostatico(t, S, CC), CC)
            if a in lb.ACOES_COM_ALVO_MUNDO:
                p.consequencia_mundo(a, {"acao": a.value, "alvo": None, "chegou": False, "deslocamento": 0, "comeu": None,
                                         "brincou_com_bola": False}, d)
        return json.dumps(p.estado_interno(), sort_keys=True, default=repr)
    assert rodar() == rodar()
