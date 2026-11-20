"""Gabarito das vidas de hoje que o planejador do J5 vai tocar (docs/TAREFA_V2_PET_QUE_PENSA.md, etapa 2): gravado com o codigo da main
(3f69e80) ANTES do lobo `planejamento`. Com `g_plano` 0, estas vidas tem de sair iguais, byte a byte (G2), e os motivos e as falas tambem.

As vidas (o `simular_vida_mundo` direto, 4 dias, o atencioso, as sementes dos testes), com o mundo do J5 ligado (os troncos vistos, os
candidatos de arvore lembrada, a fruta na mao e a troca de tipo no protocolo do plano, no dia 2):
- o corpo quimico (a digestao e a Vida) e o mesmo com o metabolismo (PP-3);
- os cerebros: o instinto do mundo; o P0 com lobos, o alvo aprendido e as classes por arvore; o P1 do plano (T3, canais, alvo aprendido,
  classes por arvore, presenca da fruta) e o mesmo P1 embrulhado no `PoliticaComMotivo` (os motivos e as falas de adulto);
- o layout padrao (o afastado so no P1).

O que se confere: a impressao do gabarito dos dois pets e, no P1 com o motivo, o sha256 dos motivos e das falas.

    python tests/gabarito_pet_que_pensa_plano.py      # grava tests/gabaritos/pet_que_pensa_plano_vidas_de_hoje.json (so com o codigo de antes)
"""
from __future__ import annotations

import hashlib
import json
import random
import sys
from dataclasses import replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import bancada_v2 as bv  # noqa: E402
import gabarito_dois_pets as gdp  # noqa: E402
import gabarito_pqp_mundo as gq  # noqa: E402

from digilab.config import (CONFIG_DONOS, CONFIG_PADRAO, CONFIG_PQP_MUNDO_LIGADA, LAYOUT_MUNDO_AFASTADO, TICKS_POR_DIA)  # noqa: E402
from digilab.donos import Visao, criar_dono  # noqa: E402
from digilab.events import FRUTAS, dar_fruta, trocar_arvores  # noqa: E402
from digilab.expressao import expressar  # noqa: E402
from digilab.instinto_mundo import PoliticaInstintoMundo  # noqa: E402
from digilab.motivo import PoliticaComMotivo  # noqa: E402
from digilab.motor_corpo import com_corpo  # noqa: E402
from digilab.mundo import CanalMundo, DonoComLugar, MotorMundo  # noqa: E402
from digilab.policies.lobos import PoliticaLobos  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402

ARQUIVO = RAIZ / "tests" / "gabaritos" / "pet_que_pensa_plano_vidas_de_hoje.json"
DIAS = 4
DIA_MUDANCA = 2
N_MAO = 2
SEMENTES = (101, 202)                                   # so as dos testes
LAYOUTS = {"padrao": gq.LAYOUTS["padrao"], "afastado": replace(gq.LAYOUTS["padrao"], layout=LAYOUT_MUNDO_AFASTADO)}
CORPOS = {"quimica": gq.CORPOS["quimica"], "metabolismo": replace(gq.CORPOS["quimica"], metabolismo=True)}
CEREBROS = ("instinto", "P0-arv", "P1-plano", "P1-plano-motivo")
LUGARES = ("comedouro", "longe")
MotorMundoCorpo = com_corpo(MotorMundo)
P0_ARV = replace(gq.P0_ALVO, alvo_por_arvore=True)
P1_PLANO = replace(gq.P1_ALVO, alvo_por_arvore=True)


def _sha(texto: str) -> str:
    return hashlib.sha256(texto.encode()).hexdigest()


def casos():
    for corpo in CORPOS:
        for cerebro in CEREBROS:
            for lugar in LUGARES:
                for s in SEMENTES:
                    yield f"padrao|{corpo}|{cerebro}|{lugar}|{s}", ("padrao", corpo, cerebro, lugar, s)
    for corpo in CORPOS:
        for s in SEMENTES:
            yield f"afastado|{corpo}|P1-plano|comedouro|{s}", ("afastado", corpo, "P1-plano", "comedouro", s)


def xy_do_caso(lugar: str, semente: int) -> tuple[str, str]:
    """a fruta x que faz bem antes da mudanca (a do gabarito do A) e a y com que ela troca"""
    x = gq.x_do_caso(lugar, semente)
    return x, FRUTAS[(FRUTAS.index(x) + 1) % len(FRUTAS)]


def politica(cerebro: str, layout: str, corpo: str, cfg_lobos=None, embrulho=None):
    """a politica do caso; `cfg_lobos` troca a ConfigLobos do P1 (o teste liga o g_plano com ela) e `embrulho` envolve o cerebro"""
    cm, cc = LAYOUTS[layout], CORPOS[corpo]
    if cerebro == "instinto":
        p = PoliticaInstintoMundo(CONFIG_PADRAO)
    elif cerebro == "P0-arv":
        p = PoliticaLobos(CONFIG_PADRAO, cfg_lobos or P0_ARV, cfg_mundo=cm)
    else:
        p = bv.PoliticaDoBraco(PoliticaLobos(CONFIG_PADRAO, cfg_lobos or P1_PLANO, cfg_mundo=cm, cfg_corpo=cc), bv.braco_de("P1"),
                               gq.CC_CANAIS)
        if cerebro == "P1-plano-motivo":
            p = PoliticaComMotivo(p)
    return embrulho(p) if embrulho is not None else p


def vida(layout: str, corpo: str, cerebro: str, lugar: str, semente: int, cfg_lobos=None, embrulho=None):
    """o atencioso, 4 dias; no primeiro passo do dono depois das 8 h do dia 2 com o pet acordado, a x na mao 2 vezes e a troca x <-> y
    (o protocolo do plano, PP-5, pelo canal do mundo, fora do orcamento). Devolve (motor, politica, tick da mudanca)."""
    x, y = xy_do_caso(lugar, semente)
    cm = LAYOUTS[layout]
    p = politica(cerebro, layout, corpo, cfg_lobos, embrulho)
    m = MotorMundoCorpo(p, CONFIG_PADRAO, semente, obediencia_desligada=True, cfg_mundo=cm, efeito_frutas=gq.efeito_do_plano(x),
                        cfg_corpo=CORPOS[corpo], cfg_pqp=CONFIG_PQP_MUNDO_LIGADA)
    dono = DonoComLugar(criar_dono("atencioso"), lugar, semente, "atencioso", cm)
    rng = random.Random(derivar_semente("dono", semente, "atencioso"))
    orcamento = 16 * DIAS
    canal = CanalMundo(m, orcamento, CONFIG_DONOS.max_interacoes_por_passo)
    passos = DIAS * TICKS_POR_DIA // CONFIG_DONOS.passo_ticks
    mudanca = None
    for passo in range(passos):
        m.avancar(CONFIG_DONOS.passo_ticks)
        mi, ma = canal.limites(passo, passos)
        canal.aplicar(dono.decidir(Visao(estado=m.estado(), passo=passo, passos_totais=passos, orcamento=orcamento, gasto=canal.gasto,
                                         minimo_obrigatorio=mi, maximo_permitido=ma), rng), passo, passos)
        t = m._estado.tick
        if mudanca is None and t >= DIA_MUDANCA * TICKS_POR_DIA + 8 * 60 and not m._estado.dormindo:
            for _ in range(N_MAO):
                m.observar(dar_fruta(x))
            m.observar(trocar_arvores(x, y))
            mudanca = t
    canal.fechar()
    if mudanca is None:
        raise RuntimeError("a mudanca do plano nao aconteceu na vida do gabarito")
    return m, p, mudanca


def motivos_de(p) -> dict:
    """os motivos e as falas de adulto de um PoliticaComMotivo"""
    mot = [[m.acao, list(m.fatores), list(m.evento_ref), m.intensidade, m.exploracao, m.tick] for m in p.motivos]
    falas = [expressar(m, "adulto", h).conteudo for m, h in zip(p.motivos, p.humores)]
    return {"motivos": _sha(json.dumps(mot)), "falas": _sha(json.dumps(falas, ensure_ascii=False)), "n": len(mot)}


def impressao_de(caso, cfg_lobos=None, embrulho=None) -> dict:
    m, p, mudanca = vida(*caso, cfg_lobos=cfg_lobos, embrulho=embrulho)
    d = gdp.impressao(m)
    d["mudanca"] = mudanca
    alvo = p if embrulho is None else getattr(p, "_interna", p)
    if isinstance(alvo, PoliticaComMotivo):
        d.update(motivos_de(alvo))
    return d


def main() -> None:
    gab = {chave: impressao_de(caso) for chave, caso in casos()}
    ARQUIVO.write_text(json.dumps(gab, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(f"{len(gab)} vidas -> {ARQUIVO}")


if __name__ == "__main__":
    main()
