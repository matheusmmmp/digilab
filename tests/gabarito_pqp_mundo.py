"""Gabarito das vidas do MUNDO FISICO de hoje que o J5 vai tocar (docs/TAREFA_V2_PET_QUE_PENSA.md, etapa 3, o mundo; e a etapa 2b, as
classes por arvore): gravado com o codigo da main ANTES de entrar a fruta na mao, a troca de tipo por arvore, os candidatos de arvore
lembrada (PP-1) e as classes por arvore no alvo aprendido (PP-2). Com as chaves novas desligadas, estas vidas tem de sair iguais, byte a
byte (G2).

As vidas (o `simular_vida_mundo` direto, 3 dias, o atencioso no comedouro e longe, as sementes dos testes):
- os dois layouts, sem o corpo e com o corpo quimico (a digestao e a Vida, o regime "quimica" do plano);
- os efeitos do plano do J5: a x faz bem (o humor sobe `efeito_humor_ruim`), as outras neutras (x = a, b e c, uma por semente e lugar);
- tres cerebros: o instinto do mundo; o P0 com lobos e o alvo aprendido (o prior: usa o padrao do motor); o P1 da consequencia no ponto
  T3, com os canais, o alvo aprendido e a rota do humor no mundo (`presenca_fruta_mundo`), com o corpo no cerebro quando o motor o tem.

O que se confere: a impressao do gabarito dos dois pets (log, estado, estado() com o corpo, acoes, rngs, politica, o registro do mundo
fisico inteiro).

    python tests/gabarito_pqp_mundo.py      # grava tests/gabaritos/pqp_mundo_vidas_de_hoje.json (so com o codigo de antes)
"""
from __future__ import annotations

import json
import sys
from dataclasses import replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import bancada_v2 as bv  # noqa: E402
import gabarito_dois_pets as gdp  # noqa: E402

from digilab.config import (CONFIG_CONSEQUENCIA, CONFIG_FRUTAS, CONFIG_LOBOS, CONFIG_MUNDO_LIGADA, CONFIG_PADRAO,  # noqa: E402
                            LAYOUT_MUNDO_AFASTADO, ConfigCorpo)
from digilab.donos import criar_dono  # noqa: E402
from digilab.events import FRUTAS  # noqa: E402
from digilab.instinto_mundo import PoliticaInstintoMundo  # noqa: E402
from digilab.motor_corpo import com_corpo  # noqa: E402
from digilab.mundo import DonoComLugar, MotorMundo, simular_vida_mundo  # noqa: E402
from digilab.policies.lobos import PoliticaLobos  # noqa: E402

ARQUIVO = RAIZ / "tests" / "gabaritos" / "pqp_mundo_vidas_de_hoje.json"
DIAS = 3
SEMENTES = (101, 202)                                   # so as dos testes
LAYOUTS = {"padrao": CONFIG_MUNDO_LIGADA, "afastado": replace(CONFIG_MUNDO_LIGADA, layout=LAYOUT_MUNDO_AFASTADO)}
CORPOS = {"sem": None, "quimica": ConfigCorpo(ligada=True, digestao=True, vida=True)}
CEREBROS = ("instinto", "P0-alvo", "P1-alvo")
LUGARES = ("comedouro", "longe")
MotorMundoCorpo = com_corpo(MotorMundo)
P0_ALVO = replace(CONFIG_LOBOS, alvo_aprendido=True)
P1_ALVO = replace(bv.cfg_lobos_do_ponto("T3"), alvo_aprendido=True, presenca_fruta_mundo=True)
CC_CANAIS = replace(CONFIG_CONSEQUENCIA, canais_ligados=True)


def efeito_do_plano(x: str) -> dict:
    """os efeitos antes da mudanca do plano do J5 (secao 2): a x faz bem, as outras neutras"""
    return {f: (-CONFIG_FRUTAS.efeito_humor_ruim if f == x else 0.0) for f in FRUTAS}


def x_do_caso(lugar: str, semente: int) -> str:
    return FRUTAS[(SEMENTES.index(semente) + 2 * LUGARES.index(lugar)) % len(FRUTAS)]


def casos():
    for layout in LAYOUTS:
        for corpo in CORPOS:
            for cerebro in CEREBROS:
                for lugar in LUGARES:
                    for s in SEMENTES:
                        yield f"{layout}|{corpo}|{cerebro}|{lugar}|{s}", (layout, corpo, cerebro, lugar, s)


def fabricas(layout: str, corpo: str, cerebro: str, x: str, **kw_motor):
    cm, cc = LAYOUTS[layout], CORPOS[corpo]
    if cerebro == "instinto":
        fp = lambda cfg=None: PoliticaInstintoMundo(cfg or CONFIG_PADRAO)  # noqa: E731
    elif cerebro == "P0-alvo":
        fp = lambda cfg=None: PoliticaLobos(cfg or CONFIG_PADRAO, P0_ALVO, cfg_mundo=cm)  # noqa: E731
    else:
        fp = lambda cfg=None: bv.PoliticaDoBraco(PoliticaLobos(cfg or CONFIG_PADRAO, P1_ALVO, cfg_mundo=cm, cfg_corpo=cc),  # noqa: E731
                                                 bv.braco_de("P1"), CC_CANAIS)
    ef = efeito_do_plano(x)
    if cc is None:
        fm = lambda p, cfg, s: MotorMundo(p, cfg, s, obediencia_desligada=True, cfg_mundo=cm, efeito_frutas=ef, **kw_motor)  # noqa: E731
    else:
        fm = lambda p, cfg, s: MotorMundoCorpo(p, cfg, s, obediencia_desligada=True, cfg_mundo=cm, efeito_frutas=ef,  # noqa: E731
                                               cfg_corpo=cc, **kw_motor)
    return fp, fm


def vida(layout: str, corpo: str, cerebro: str, lugar: str, semente: int, **kw_motor):
    fp, fm = fabricas(layout, corpo, cerebro, x_do_caso(lugar, semente), **kw_motor)
    dono = DonoComLugar(criar_dono("atencioso"), lugar, semente, "atencioso", LAYOUTS[layout])
    return simular_vida_mundo("atencioso", dono, fp(CONFIG_PADRAO), semente, DIAS, 16 * DIAS, fm, rotulo_dono="atencioso")


def impressao_de(caso, **kw_motor) -> dict:
    v = vida(*caso, **kw_motor)
    return gdp.impressao(v.motor, v.interacoes)


def main() -> None:
    gab = {chave: impressao_de(caso) for chave, caso in casos()}
    ARQUIVO.write_text(json.dumps(gab, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(f"{len(gab)} vidas -> {ARQUIVO}")


if __name__ == "__main__":
    main()
