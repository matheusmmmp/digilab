"""A sonda das duas TVs (GOSTO_VISUAL, P1e; docs/ESPEC_GOSTO_VISUAL_P1.md, secao 7; docs/futuro/gosto_visual_pet.md, secao 5; GV-11).

Uma ferramenta so de leitura, com a maquinaria das sondas da INDIVIDUALIDADE (experiments/sondas_individualidade.py): num tick T da vida,
uma COPIA do pet sai do replay do log ate T (`reproduzir_mundo(..., ate_tick=T)`, com as fabricas da vida); cada replica e uma copia profunda
dela, com a rng de politica trocada por uma derivada (`gosto-visual-politica`). Na copia, o `MotorMundo.ligar_duas_tvs` (a ConfigDuasTVs)
tira a TV da vida de cena e poe duas TVs fixas, a do perfil A (id 2) e a do B (id 3), a mesma distancia do pet, em direcoes opostas, a
direcao sorteada pela rng propria do motor (`duas-tvs-posicao`). A copia anda JANELA_TICKS, um tick por vez, e a sonda le, a cada tick, qual
TV o pet olha (`MotorMundo.tv_olhada`). A vida real nao e tocada (o G2: o log e o estado da vida saem os mesmos com e sem a sonda; a sonda
confere o log e falha alto se ele mudou).

O que a sonda grava, por replica (as medidas sao do plano, docs/PLANO_ANALISE_V3_GOSTO_VISUAL.md, secao 4, e moram em digilab/metrics.py):
  - `olhadas`: a sequencia da janela em trechos [id ou None, ticks];
  - `ticks`: os ticks olhando a A e a B; `primeira`: "A", "B" ou None (nao olhou nenhuma);
  - `agrado`: o que o cerebro da copia calcula para os dois perfis no momento, sem andar nada: o inato (contra o otimo do genoma) e o de
    agora (o otimo mais o deslocamento da exposicao), na escala S;
  - as decisoes da janela (a acao e o id da TV da unidade escolhida) e a posicao das TVs.

Os perfis (sete inteiros em [0, C], na ordem de CANAIS_TELA) sao os do plano: o A em C/5 e o B em 4C/5 em todos os canais, simetricos em
volta do meio (o otimo do genoma vazio, C/2): no controle, o agrado inato das duas e o mesmo. Nenhum programa da grade e igual a eles (os
perfis da grade sao sorteados; a sonda confere). Todos os numeros abaixo sao PROPOSTOS, SEM FONTE (ferramenta de medida, nao mecanica do
pet: nao entram no `config.py`; os da ConfigDuasTVs estao la). O termo `gosto` da P1d fica fora da sonda (D-GV-P1d-4): a sonda so le."""
from __future__ import annotations

import copy
import random
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import sondas_individualidade as si  # noqa: E402  (registra a copia profunda dos embrulhos de politica)
from digilab.config import CANAIS_TELA, CONFIG_DUAS_TVS_LIGADA, CONFIG_TV_LIGADA  # noqa: E402
from digilab.corpo import div_arred  # noqa: E402
from digilab.mundo import reproduzir_mundo  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402
from digilab.tv import IDS_DUAS_TVS  # noqa: E402

C = CONFIG_TV_LIGADA.escala
PERFIL_A = tuple(C // 5 for _ in CANAIS_TELA)              # PROPOSTO, SEM FONTE: o programa calmo (0,2 C em todo canal)
PERFIL_B = tuple(4 * C // 5 for _ in CANAIS_TELA)          # PROPOSTO, SEM FONTE: o programa agitado (0,8 C em todo canal)
ROTULO = {IDS_DUAS_TVS[0]: "A", IDS_DUAS_TVS[1]: "B"}
JANELA_TICKS = si.JANELA_TICKS                             # PROPOSTO, SEM FONTE: 240 ticks, 16 decisoes (a janela das sondas do I1)
REPLICAS = si.REPLICAS                                     # PROPOSTO, SEM FONTE: 3
FLUXO_POLITICA = "gosto-visual-politica"


def cerebro_da_copia(motor):
    """o cerebro embaixo dos embrulhos de politica do motor (o objeto com o gancho `olhando_tela` e o M-SENS)"""
    o = motor.politica
    for _ in range(8):
        if hasattr(o, "m") and hasattr(o, "olhando_tela") and hasattr(o.m, "sens"):
            return o
        filhos = [v for k, v in vars(o).items() if k in ("_pm", "_pf", "_pb", "_p", "_interna")]
        if len(filhos) != 1:
            raise RuntimeError(f"a sonda nao achou o cerebro com o olhar embaixo de {type(o).__name__}")
        o = filhos[0]
    raise RuntimeError("a sonda nao achou o cerebro com o olhar")


def niveis_do_perfil(perfil: tuple, S: int) -> dict[str, int]:
    """o perfil na escala do cerebro, como os receptores `tela_<canal>` o leem: div_arred(S x I, C)"""
    return {c: div_arred(S * v, C) for c, v in zip(CANAIS_TELA, perfil)}


def agrados(cerebro) -> dict:
    """o agrado dos dois perfis no cerebro da copia, sem andar nada (o inato e o de agora, com a exposicao)"""
    sens = cerebro.m.sens
    out = {}
    for rot, p in (("A", PERFIL_A), ("B", PERFIL_B)):
        n = niveis_do_perfil(p, cerebro.S)
        out[rot] = {"inato": sens.agrado_inato(n), "agora": sens.agrado(n)}
    return out


def copia_em(motor, fabricas_vida: tuple, semente: int, tick: int):
    """o pet no tick, pelo replay do log da vida (nao toca o motor da vida)"""
    fp, fm = fabricas_vida
    m = reproduzir_mundo(motor.log, fp, semente=semente, fabrica_motor=fm, ate_tick=tick)
    if m.estado()["tick"] != tick:
        raise RuntimeError(f"o replay parou no tick {m.estado()['tick']}, nao no {tick}")
    return m


def _trechos(seq: list) -> list[list]:
    out: list[list] = []
    for x in seq:
        if out and out[-1][0] == x:
            out[-1][1] += 1
        else:
            out.append([x, 1])
    return out


def ler_replica(m, replica: int) -> dict:
    """liga as duas TVs na copia, anda a janela um tick por vez e le qual TV o pet olha"""
    programas = getattr(m.mundo.tv, "programas", ())
    if PERFIL_A in programas or PERFIL_B in programas:
        raise RuntimeError("um perfil da sonda e um programa da grade: a sonda pede programas que o dono nunca mostrou")
    c = cerebro_da_copia(m)
    ag = agrados(c)
    pos = m.ligar_duas_tvs(CONFIG_DUAS_TVS_LIGADA, (PERFIL_A, PERFIL_B), replica)
    n0 = len(c.motivos)
    seq = []
    for _ in range(JANELA_TICKS):
        m.avancar(1)
        seq.append(m.tv_olhada())
    if any(x is not None and x not in ROTULO for x in seq):
        raise RuntimeError(f"a sonda viu o pet olhar uma TV que nao e das duas: {sorted({x for x in seq if x is not None})}")
    decisoes = [{"acao": d["acao"], "olha": d["olhar"]["olha"]} for d in c.motivos[n0:]]
    if not decisoes:
        raise RuntimeError("a janela da sonda nao teve decisao")
    primeira = next((ROTULO[x] for x in seq if x is not None), None)
    return {"replica": replica, "olhadas": [[None if x is None else ROTULO[x], n] for x, n in _trechos(seq)],
            "ticks": {"A": sum(1 for x in seq if x == IDS_DUAS_TVS[0]), "B": sum(1 for x in seq if x == IDS_DUAS_TVS[1])},
            "primeira": primeira, "agrado": ag, "decisoes": decisoes, "posicao": pos, "dormiu": m.estado()["dormindo"]}


def sonda(motor, fabricas_vida: tuple, semente: int, dias: tuple, replicas: int = REPLICAS) -> dict:
    """a sonda nos dias pedidos, no momento das sondas da INDIVIDUALIDADE (a primeira decisao acordada a partir das 10 h, ate as 18 h; sem
    nenhuma, o dia fica sem sonda). Nada do motor da vida muda (G2: o log e conferido)."""
    if not dias or len(set(dias)) != len(dias) or any(type(d) is not int or d < 0 for d in dias):
        raise ValueError(f"os dias da sonda: inteiros >= 0, sem repeticao: {dias!r}")
    if type(replicas) is not int or replicas < 1:
        raise ValueError(f"replicas >= 1: {replicas!r}")
    log_antes = motor.log.para_jsonl()
    momento = dict(si.momentos(motor, max(dias) + 1))
    saida = []
    for dia in dias:
        tick = momento[dia]
        reg = {"dia": dia, "tick": tick, "replicas": []}
        if tick is not None:
            base = copia_em(motor, fabricas_vida, semente, tick)
            for r in range(replicas):
                m = copy.deepcopy(base)
                m._rng_politica = random.Random(derivar_semente(FLUXO_POLITICA, semente, dia, r))
                reg["replicas"].append(ler_replica(m, r))
        saida.append(reg)
    if motor.log.para_jsonl() != log_antes:
        raise RuntimeError("a sonda mudou o log da vida (G2)")
    return {"semente": semente, "dias": list(dias), "replicas": replicas, "hora": si.HORA_SONDA, "janela_ticks": JANELA_TICKS,
            "perfis": {"A": list(PERFIL_A), "B": list(PERFIL_B)}, "por_dia": saida}
