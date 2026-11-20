"""V2, corpo, etapa 6 (lado do cerebro): o G-RISCO da secao 13 e o G-MEC do cerebro A (docs/TAREFA_V2_CORPO_DRIVES.md, secoes 8, 12 e 13).

G-RISCO, em estados controlados, com os numeros PROPOSTOS:
  - com o tedio alto e a energia alta, o sinal de brincar com a bola e positivo (a conta da secao 9: +1440); repetida, a bola vale menos;
  - com a curiosidade alta, explorar e achar uma novidade da sinal positivo; explorar sem achar nada da so o cansaco;
  - com a solidao alta, o carinho da sinal positivo a ultima decisao; o tapa da o sinal direto, negativo, a ultima decisao;
  - numa vida curta do P1 com o corpo (sementes dos testes, 4 dias, mundo da bola): p(brincar | tedio > 0,5, bola vista) no fim e maior
    que no comeco. So a direcao, sem IC e sem gate de efeito.
G-MEC do cerebro: o tapa credita `recompensa_tapa` a ultima decisao em quem aprende e em nada no P0; o carinho e cuidado (acerta o relogio
e paga os chamados); e o G1 com os drives novos e os gestos.

O motor da etapa 6 (o tapa no log, o aviso da atividade ao corpo, o `mudanca_no_corpo`) e do A (CORPO-GESTOS): a vida curta usa o
MotorCorpo do mundo da bola, `com_corpo(MotorAmbiente)`, que avisa a atividade ao corpo uma vez por decisao.
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

import bancada_v2 as bv  # noqa: E402
from digilab.ambiente import DonoComBola, MotorAmbiente  # noqa: E402
from digilab.config import (CONFIG_BOLA_LIGADA, CONFIG_CONSEQUENCIA, CONFIG_CORPO_DRIVES, CONFIG_LOBOS, CONFIG_PADRAO,  # noqa: E402
                            ConfigCorpo)
from digilab.corpo import Corpo  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.educacao import reproduzir_educacao  # noqa: E402
from digilab.events import AcaoPet, AcaoUsuario  # noqa: E402
from digilab.motor_corpo import PercepcaoCorpo, com_corpo  # noqa: E402
from digilab.policies import lobos as lb  # noqa: E402
from digilab.policies.lobos import PoliticaLobos, _RngSonda  # noqa: E402
from digilab.policy import Observacao, Transicao  # noqa: E402
from digilab.state import Estado  # noqa: E402
from digilab.treino import MotorComFeedback, reproduzir_com_feedback, simular_vida  # noqa: E402

CFG = CONFIG_PADRAO
S = CONFIG_LOBOS.escala
CC = CONFIG_CONSEQUENCIA
CL_T3 = bv.cfg_lobos_do_ponto("T3")
NOVOS = ConfigCorpo(ligada=True, digestao=True, vida=True, drives_novos=True)       # sem os gestos
GESTOS = CONFIG_CORPO_DRIVES
SEMENTES = (11, 22, 33, 101, 202, 303, 404, 505)                 # todas as sementes dos testes
# o ponto (m_sobe, m_reduz) = (2, 1/2) da grade da calibracao (PLANO_ANALISE_V2_CORPO_DRIVES, 6.1): com os numeros PROPOSTOS (1, 1) o
# tedio do P1 no mundo da bola nunca passa de ~0,3 (o pet explora e brinca o bastante) e a condicao "tedio > 0,5" da secao 13 fica vazia
NOVOS_RISCO = replace(NOVOS, tedio_sobe=900, solidao_sobe=450, estresse_divisor=128, tedio_bola=67500, tedio_brincar=22500,
                      tedio_explorar=45000, tedio_dono=45000, carinho_solidao=90000, carinho_estresse=45000)


class TapaDeTeste:
    """o AcaoUsuario.TAPA do A (etapa 6, events.py): o corpo e o cerebro o leem pelo valor"""
    value = "tapa"


def _obs(corpo: Corpo, ticks: int = 0, **kw) -> Observacao:
    """a observacao que o MotorCorpo monta: o Estado e a leitura da quimica, e os receptores"""
    h = corpo.drives()
    return Observacao(vetor_estado=(h["fome"], h["higiene"], h["energia"], h["humor"], h["saude"], 0.0, 0.0, 0.5),
                      ticks_desde_cuidado=ticks, total_cuidados=0, corpo=PercepcaoCorpo(**corpo.receptores()), **kw)


class Espiao(PoliticaLobos):
    def __init__(self, *a, **kw) -> None:
        super().__init__(*a, **kw)
        self.creditos = []

    def _creditar(self, registro, f_S, anteriores, consequencia=False) -> None:
        self.creditos.append((registro["acao"], f_S))
        super()._creditar(registro, f_S, anteriores, consequencia)


def _decidir(lob: PoliticaLobos, corpo: Corpo, acao: AcaoPet, u: float, **kw) -> Observacao:
    o = _obs(corpo, **kw)
    assert lob.agir(o, _RngSonda(u)) is acao, lob.motivos[-1]["pesos"]
    return o


# ================================================================== G-RISCO, estados controlados
def test_risco_brincar_com_a_bola_com_tedio_alto_da_sinal_positivo():
    """a conta da secao 9 pelo corpo de verdade e pelo cerebro: tedio 0,75 e cansaco 0,20, ganho 4: +1440 (o N3 de hoje: -34). Com a
    bola repetida (DS-4) o sinal cai"""
    corpo = Corpo.de_estado(Estado(), CFG, NOVOS)
    corpo.q.update(tedio=337500, cansaco=90000)
    lob = Espiao(CFG, CL_T3, cfg_bola=CONFIG_BOLA_LIGADA, cfg_corpo=NOVOS)
    sinais = []
    for _ in range(2):
        antes = _decidir(lob, corpo, AcaoPet.BRINCAR, 0.5, bola=1.0)
        corpo.acao_pet(AcaoPet.BRINCAR)
        corpo.atividade("bola")
        corpo.estimulo_bola(CONFIG_BOLA_LIGADA.ganho_humor_bola)
        depois = _obs(corpo)
        t = Transicao(antes, AcaoPet.BRINCAR, depois)
        lob.observar_consequencia(t, lb.sinal_homeostatico(t, S, CC), CC)
        lob.consequencia_corpo(AcaoPet.BRINCAR, {"acao": "brincar", "estimulos": [("pet", "brincar"), ("bola",)]}, depois)
        sinais.append(lob.motivos[-1]["sinal_corpo"]["f"])
        if len(sinais) == 1:
            assert lb.sinal_homeostatico(t, S, CC) == -34
        corpo.q.update(tedio=337500, cansaco=90000)
    assert sinais[0] == 1440 and 0 < sinais[1] < sinais[0]
    assert [f for _, f in lob.creditos] == sinais


def test_risco_explorar_com_novidade_da_sinal_positivo_e_sem_novidade_so_o_cansaco():
    def explorar(n: int) -> int:
        corpo = Corpo.de_estado(Estado(), CFG, NOVOS, com_mundo=True)
        corpo.q.update(curiosidade=400000, cansaco=90000)     # tedio em 0: a atividade de explorar nao tem o que reduzir
        antes = _obs(corpo)
        corpo.acao_pet(AcaoPet.EXPLORAR)
        corpo.atividade("explorar")
        corpo.estimulo_novidade(n)
        depois = _obs(corpo)
        drives = ("fome", "higiene", "energia", "tedio", "curiosidade", "solidao", "estresse")
        f = lb.sinal_corpo(antes.corpo, depois.corpo, drives, CC.ganho, S)
        assert lb.sinal_corpo(antes.corpo, depois.corpo, ("fome", "higiene", "energia"), CC.ganho, S) == lb.sinal_homeostatico(
            Transicao(antes, AcaoPet.EXPLORAR, depois), S, CC)
        return f, lb.sinal_homeostatico(Transicao(antes, AcaoPet.EXPLORAR, depois), S, CC)
    com, _ = explorar(1)
    sem, hoje = explorar(0)
    assert com > 0 > sem == hoje                                      # sem novidade: so o cansaco, o sinal de hoje


def test_risco_carinho_com_solidao_alta_e_tapa_na_ultima_decisao():
    """o carinho (mudanca_no_corpo) credita o sinal pelo corpo, positivo, a ultima decisao; o tapa credita recompensa_tapa (-1,0 x S)"""
    corpo = Corpo.de_estado(Estado(), CFG, GESTOS)
    corpo.q.update(solidao=400000, estresse=100000)
    lob = Espiao(CFG, CL_T3, cfg_corpo=GESTOS)
    antes = _decidir(lob, corpo, AcaoPet.OCIOSO, 0.1, ticks=30)
    lob.observar(Transicao(antes, AcaoPet.OCIOSO, _obs(corpo, ticks=30)))
    lob.consequencia_corpo(AcaoPet.OCIOSO, {"acao": "ocioso", "estimulos": [("pet", "ocioso")]}, _obs(corpo, ticks=30))
    o_antes = _obs(corpo, ticks=45)
    corpo.acao_dono(AcaoUsuario.ACARICIAR)
    o_depois = _obs(corpo, ticks=0)
    lob.mudanca_no_corpo(o_antes, o_depois)
    f_carinho = lb.sinal_corpo(o_antes.corpo, o_depois.corpo, ("fome", "higiene", "energia", "tedio", "solidao", "estresse", "dor"),
                               CC.ganho, S)
    assert f_carinho > 0 and lob.creditos == [(AcaoPet.OCIOSO, f_carinho)]
    lob.receber_acao_dono(TapaDeTeste(), 60)
    assert lob.creditos[-1] == (AcaoPet.OCIOSO, -S)
    rec = lob.estado_interno()["aprendizado"]["recompensas"]
    assert rec["carinho"] == 1 and rec["tapa"] == 1
    assert lob.estado_interno()["aprendizado"]["tick_ultimo_cuidado"] == 60


def test_tapa_nao_mexe_no_p0_e_o_carinho_e_cuidado():
    """no P0 (sem aprender) nada e creditado; o carinho acerta o relogio do cuidado e paga o chamado pendente pela latencia"""
    corpo = Corpo.de_estado(Estado(), CFG, GESTOS)
    p0 = Espiao(CFG, CONFIG_LOBOS, cfg_corpo=GESTOS)
    antes = _decidir(p0, corpo, AcaoPet.OCIOSO, 0.1)
    p0.observar(Transicao(antes, AcaoPet.OCIOSO, _obs(corpo)))
    p0.consequencia_corpo(AcaoPet.OCIOSO, {"acao": "ocioso", "estimulos": []}, _obs(corpo))
    p0.receber_acao_dono(TapaDeTeste(), 10)
    p0.mudanca_no_corpo(_obs(corpo, ticks=20), _obs(corpo, ticks=0))
    assert p0.creditos == [] and not p0.pesos_mudaram() and p0.memoria.cuidados == 1
    # o chamado pendente e pago pelo carinho, como por qualquer cuidado
    lob = Espiao(CFG, CL_T3, cfg_corpo=GESTOS)
    corpo.q.update(fome=400000)                                     # fome em 0,11: o instinto chama (pedido de necessidade)
    antes = _decidir(lob, corpo, AcaoPet.CHAMAR_ATENCAO, 0.1, ticks=10)
    lob.observar(Transicao(antes, AcaoPet.CHAMAR_ATENCAO, _obs(corpo, ticks=10)))
    lob.consequencia_corpo(AcaoPet.CHAMAR_ATENCAO, {"acao": "chamar_atencao", "estimulos": []}, _obs(corpo, ticks=10))
    lob.mudanca_no_corpo(_obs(corpo, ticks=40), _obs(corpo, ticks=0))
    rec = lob.estado_interno()["aprendizado"]["recompensas"]
    assert rec["latencia"] == 1 and lob.estado_interno()["aprendizado"]["pendentes"] == []
    sem_corpo = PoliticaLobos(CFG, CL_T3)
    with pytest.raises(RuntimeError, match="sem a chave do corpo"):
        sem_corpo.mudanca_no_corpo(_obs(corpo, ticks=5), _obs(corpo, ticks=0))


# ================================================================== G-RISCO, a vida curta do P1 com o corpo
def _vida_bola(semente: int, dono: str = "atencioso", dias: int = 4, cc: ConfigCorpo = NOVOS):
    pols = []

    def fp(cfg=None):
        c = PoliticaLobos(cfg or CFG, CL_T3, cfg_bola=CONFIG_BOLA_LIGADA, cfg_corpo=cc)
        pols.append(c)
        return bv.PoliticaDoBraco(c, bv.braco_de("P1"), CC)

    fm = lambda p, cfg, s: com_corpo(MotorAmbiente)(p, cfg, s, obediencia_desligada=True, cfg_bola=CONFIG_BOLA_LIGADA, cfg_corpo=cc)  # noqa: E731
    v = simular_vida(dono, DonoComBola(dono, CONFIG_BOLA_LIGADA), fp(CFG), semente, dias, 16 * dias, fabrica_motor=fm, rotulo_dono=dono)
    return v.motor, pols[-1], fp, fm


def test_risco_vida_curta_do_p1_aprende_a_brincar_com_tedio_e_bola():
    """p(brincar | tedio > 0,5, bola vista) nas decisoes do fim da vida (dias 3 e 4) e maior que nas do comeco (dias 1 e 2), juntando as
    sementes dos testes, no ponto (2, 1/2) da grade do plano (NOVOS_RISCO). So a direcao. E o achado: com os numeros PROPOSTOS o estado
    nao aparece"""
    for semente in (101, 202):
        _, lob, _, _ = _vida_bola(semente)
        assert max(mt["percepcao_corpo"]["tedio"] for mt in lob.estado_interno()["motivos"]) < 0.5
    contagem = {"comeco": [0, 0], "fim": [0, 0]}
    for semente in SEMENTES:
        m, lob, _, _ = _vida_bola(semente, cc=NOVOS_RISCO)
        motivos = lob.estado_interno()["motivos"]
        assert len(motivos) == len(m.acoes_recentes(10**9)) == m.consequencias
        for k, mt in enumerate(motivos):
            if mt["percepcao"]["bola"] > 0 and mt["percepcao_corpo"]["tedio"] > 0.5 and "brincar" in mt["candidatos"]:
                fase = "comeco" if k < len(motivos) // 2 else "fim"
                contagem[fase][0] += mt["acao"] == "brincar"
                contagem[fase][1] += 1
        assert any(v != [0] * len(v) for g in lob.estado_interno()["pesos_corpo"].values() for v in g.values())
    assert contagem["comeco"][1] >= 3 and contagem["fim"][1] >= 3, contagem
    p = {fase: b / n for fase, (b, n) in contagem.items()}
    assert p["fim"] > p["comeco"], (p, contagem)


# ================================================================== G1 com os drives novos e os gestos
def _resumo(m) -> str:
    d = {"log": m.log.para_jsonl(), "estado": m.estado(), "bruto": repr(m._estado), "acoes": m.acoes_recentes(10**9),
         "rng": [m._rng_ambiente.getstate(), m._rng_politica.getstate()], "politica": m.politica.estado_interno()}
    return hashlib.sha256(json.dumps(d, sort_keys=True, default=repr).encode()).hexdigest()


@pytest.mark.parametrize("cc", [NOVOS, GESTOS], ids=["novos", "gestos"])
def test_g1_com_os_drives_novos(cc):
    """o P1 e o P3 com o corpo da etapa 6 no MotorCorpo do mundo padrao e no da bola com o aviso da atividade: replay bit a bit, a
    quimica nova, a janela do tedio e o estado interno (as entradas novas aprendidas) incluidos"""
    for rotulo in ("P1", "P3"):
        def fp(cfg=None, rotulo=rotulo):
            return bv.PoliticaDoBraco(PoliticaLobos(cfg or CFG, CL_T3, cfg_corpo=cc), bv.braco_de(rotulo), CC)
        k = com_corpo(MotorComFeedback)
        fm = lambda p, cfg, s: k(p, cfg, s, cfg_corpo=cc)  # noqa: E731
        v = simular_vida("atencioso", criar_dono("atencioso"), fp(CFG), 202, 3, 48, fabrica_motor=fm, rotulo_dono="atencioso")
        r = reproduzir_com_feedback(v.motor.log, fp, CFG, 202, fabrica_motor=fm)
        assert _resumo(v.motor) == _resumo(r), rotulo
        assert v.motor.corpo.q["tedio"] > 0 and "janela_tedio" in v.motor.estado()["corpo"]
    m, _, fp, fm = _vida_bola(202, dias=3)
    r = reproduzir_educacao(m.log, fp, CFG, 202, fabrica_motor=fm)
    assert _resumo(m) == _resumo(r)
    assert m.corpo.janela_tedio
