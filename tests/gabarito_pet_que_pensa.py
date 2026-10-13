"""Gabarito das vidas de hoje do MUNDO FISICO com o corpo quimico, para o G-OBS-MM da etapa 1 do J5 (docs/TAREFA_V2_PET_QUE_PENSA.md,
etapa 0): gravado com o codigo da main ANTES de `digilab/modelo_mundo.py` existir. Com os modelos do mundo so observando (o embrulho
`PoliticaComModelo` em volta do cerebro), estas vidas tem de sair iguais, byte a byte.

Duas fontes de vida:
- **a bancada** (`experiments/bancada_v2.py`), nos mundos `fisico` e `fisico_afastado`, com o cerebro A do plano (o ponto T3, o alvo
  aprendido e a presenca da fruta no mundo): P0, P1 e P3 no regime "quimica" (e o P0 com o instinto do mundo), 2 donos, 2 lugares,
  2 sementes, nas montagens simples e completa (a completa com o ponto da K2 e os canais, como a config dos dois pets);
- **o `simular_vida_mundo` direto**, com o corpo quimico e o metabolismo (PP-3; a bancada nao liga o metabolismo no mundo fisico), com o
  instinto do mundo e com os lobos do alvo aprendido, nos dois layouts.

O que se confere: a impressao do gabarito dos dois pets (log, estado, estado() com o corpo, acoes, rngs, politica, o registro do mundo
fisico inteiro).

    python tests/gabarito_pet_que_pensa.py      # grava tests/gabaritos/pet_que_pensa_vidas_de_hoje.json (so com o codigo de antes)
"""
from __future__ import annotations

import json
import sys
from dataclasses import fields, replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import bancada_v2 as bv  # noqa: E402
import gabarito_dois_pets as gdp  # noqa: E402

from digilab.config import (CONFIG_LOBOS_APRENDIZ, CONFIG_MUNDO_LIGADA, CONFIG_PADRAO,  # noqa: E402
                            LAYOUT_MUNDO_AFASTADO)
from digilab.donos import criar_dono  # noqa: E402
from digilab.instinto_mundo import PoliticaInstintoMundo  # noqa: E402
from digilab.motor_corpo import com_corpo  # noqa: E402
from digilab.mundo import DonoComLugar, MotorMundo, simular_vida_mundo  # noqa: E402
from digilab.policies.lobos import PoliticaLobos  # noqa: E402

ARQUIVO = RAIZ / "tests" / "gabaritos" / "pet_que_pensa_vidas_de_hoje.json"
DIAS = 3
SEMENTES = (101, 202)                                   # so as dos testes
MUNDOS = ("fisico", "fisico_afastado")
BRACOS = (("P0-quimica", "lobos"), ("P1-quimica", "lobos"), ("P3-quimica", "lobos"), ("P0", "instinto"))
DONOS = ("atencioso", "aleatorio")
LUGARES = ("comedouro", "longe")
CEREBRO_PLANO = {"alvo_aprendido": True, "presenca_fruta_mundo": True}   # o habito do plano (secao 2), sem as classes por arvore (2b)
CONFIGS = {
    "simples": {"dias": DIAS, "orcamento": 16 * DIAS, "ponto": "T3", "lobos": dict(CEREBRO_PLANO)},
    "completa": {"dias": DIAS, "orcamento": 16 * DIAS, "ponto": "T3", "montagem": "completa",
                 "lobos": {"memoria_ganho": 512, "w0_pedido": 256, "w0_info": 256, **CEREBRO_PLANO},
                 "consequencia": {"ganho": 4, "canais_ligados": True}},
}

# as vidas diretas (o metabolismo)
LAYOUTS = {"padrao": CONFIG_MUNDO_LIGADA, "afastado": replace(CONFIG_MUNDO_LIGADA, layout=LAYOUT_MUNDO_AFASTADO)}
CORPO_METABOLISMO = replace(bv.CONFIG_CORPO_QUIMICA, metabolismo=True)
CEREBROS = ("instinto", "lobos")
MotorMundoCorpo = com_corpo(MotorMundo)


def bancadas(classe=bv.Bancada) -> dict:
    """as duas bancadas do gabarito; `classe` deixa o teste trocar a bancada (a que embrulha o cerebro nos modelos), com a mesma config"""
    return {nome: _como(classe, bv.bancada_da_config(c)) for nome, c in CONFIGS.items()}


def _como(classe, b: bv.Bancada):
    if classe is bv.Bancada:
        return b
    return classe(**{f.name: getattr(b, f.name) for f in fields(b)})


def casos_bancada():
    for nome_b in CONFIGS:
        for mundo in MUNDOS:
            for braco, cerebro in BRACOS:
                for dono in DONOS:
                    for lugar in LUGARES:
                        for s in SEMENTES:
                            yield (f"bancada|{nome_b}|{mundo}|{braco}~{cerebro}|{dono}|{lugar}|{s}",
                                   (nome_b, bv.EspecVida(dono, braco, s, None, mundo, cerebro, lugar)))


def casos_diretos():
    for layout in LAYOUTS:
        for cerebro in CEREBROS:
            for s in SEMENTES:
                yield f"direta|{layout}|metabolismo|{cerebro}|perto|{s}", (layout, cerebro, s)


def fabricas_diretas(layout: str, cerebro: str):
    cm = LAYOUTS[layout]
    if cerebro == "instinto":
        fp = lambda cfg=None: PoliticaInstintoMundo(cfg or CONFIG_PADRAO)  # noqa: E731
    else:
        cl = replace(CONFIG_LOBOS_APRENDIZ, alvo_aprendido=True)
        fp = lambda cfg=None: PoliticaLobos(cfg or CONFIG_PADRAO, cl, cfg_mundo=cm)  # noqa: E731
    fm = lambda p, cfg, s: MotorMundoCorpo(p, cfg, s, obediencia_desligada=True, cfg_mundo=cm, cfg_corpo=CORPO_METABOLISMO)  # noqa: E731
    return fp, fm


def vida_direta(layout: str, cerebro: str, semente: int, embrulho=None):
    """`embrulho(politica)` deixa o teste por os modelos em volta do cerebro (None: a vida de hoje)"""
    fp, fm = fabricas_diretas(layout, cerebro)
    if embrulho is not None:
        fp0 = fp
        fp = lambda cfg=None: embrulho(fp0(cfg))  # noqa: E731
    dono = gdp.DonoComBolaPerto(DonoComLugar(criar_dono("atencioso"), "perto", semente, "atencioso", LAYOUTS[layout]))
    return simular_vida_mundo("atencioso", dono, fp(CONFIG_PADRAO), semente, DIAS, 16 * DIAS, fm, rotulo_dono="atencioso")


def casos():
    yield from casos_bancada()
    yield from casos_diretos()


def vida_de_hoje(chave: str, caso, bs: dict | None = None, embrulho=None) -> dict:
    if chave.startswith("bancada|"):
        nome_b, espec = caso
        v = (bs or bancadas())[nome_b].vida(espec)
    else:
        v = vida_direta(*caso, embrulho=embrulho)
    return gdp.impressao(v.motor, v.interacoes)


def gerar() -> dict:
    bs = bancadas()
    return {chave: vida_de_hoje(chave, caso, bs) for chave, caso in casos()}


if __name__ == "__main__":
    g = gerar()
    ARQUIVO.write_text(json.dumps(g, sort_keys=True, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"{ARQUIVO}: {len(g)} vidas")
