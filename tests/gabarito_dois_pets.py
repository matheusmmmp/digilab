"""Gabarito das vidas do MUNDO FISICO de hoje, com e sem o corpo, nos dois layouts, para o G2 da frente dos dois pets
(docs/TAREFA_V2_DOIS_PETS.md, etapa 0; docs/futuro/dois_pets.md, secao 10): gravado com o codigo da main ANTES de separar o `Mundo` do
`MotorMundo` (etapa 1). Depois da separacao, com um pet so, estas vidas tem de sair iguais, byte a byte.

Duas fontes de vida:
- **a bancada** (`experiments/bancada_v2.py`), nos mundos `fisico` e `fisico_afastado`: o P0 com lobos e com o instinto do mundo, o P0z,
  e P0, P1 e P3 nos regimes "hoje" (sem o corpo) e "quimica" (o corpo com a digestao e a Vida), 2 donos, os 3 lugares, 2 sementes; mais o
  P1 e o P3 na montagem completa;
- **o `simular_vida_mundo` direto**, para o que a bancada nao monta no mundo fisico: o corpo inteiro da etapa 6 (os drives novos, com a
  curiosidade e a novidade do mundo) e a bola deixada perto do pet (a bola rola), com o instinto do mundo e com os lobos aprendendo, nos
  dois layouts.

O que se confere: a impressao do gabarito do mundo (log, estado, estado() com o corpo, acoes, rngs, politica), o registro do mundo fisico
inteiro (`resumo_mundo_fisico`, as rngs do mundo incluidas) e, com os drives novos, o registro da novidade (`_vistos_em`).

    python tests/gabarito_dois_pets.py      # grava tests/gabaritos/dois_pets_vidas_de_hoje.json (so com o codigo de antes)
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import replace
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import bancada_v2 as bv  # noqa: E402
import gabarito_mundo as gm  # noqa: E402

from digilab.config import (CONFIG_CORPO_DRIVES, CONFIG_LOBOS_APRENDIZ, CONFIG_MUNDO_LIGADA, CONFIG_PADRAO,  # noqa: E402
                            LAYOUT_MUNDO_AFASTADO, ConfigCorpo)
from digilab.donos import criar_dono  # noqa: E402
from digilab.instinto_mundo import PoliticaInstintoMundo  # noqa: E402
from digilab.motor_corpo import com_corpo  # noqa: E402
from digilab.mundo import DeixarBola, DonoComLugar, MotorMundo, simular_vida_mundo  # noqa: E402
from digilab.policies.lobos import PoliticaLobos  # noqa: E402

ARQUIVO = RAIZ / "tests" / "gabaritos" / "dois_pets_vidas_de_hoje.json"
DIAS = 3
SEMENTES = (101, 202)                                   # so as dos testes
MUNDOS = ("fisico", "fisico_afastado")
BRACOS = (("P0-hoje", "lobos"), ("P0", "instinto"), ("P0z", "lobos"), ("P1-hoje", "lobos"), ("P3-hoje", "lobos"),
          ("P0-quimica", "lobos"), ("P1-quimica", "lobos"), ("P3-quimica", "lobos"))
BRACOS_COMPLETA = ("P1-hoje", "P1-quimica", "P3-quimica")
DONOS = ("atencioso", "aleatorio")
LUGARES = ("comedouro", "perto", "longe")
BANCADAS = {"simples": bv.Bancada(DIAS, 16 * DIAS), "completa": bv.Bancada(DIAS, 16 * DIAS, montagem="completa")}

# as vidas diretas
LAYOUTS = {"padrao": CONFIG_MUNDO_LIGADA, "afastado": replace(CONFIG_MUNDO_LIGADA, layout=LAYOUT_MUNDO_AFASTADO)}
CORPOS = {"sem": None, "quimica": ConfigCorpo(ligada=True, digestao=True, vida=True), "drives": CONFIG_CORPO_DRIVES}
CEREBROS = ("instinto", "lobos")
MotorMundoCorpo = com_corpo(MotorMundo)


def _sha(texto: str) -> str:
    return hashlib.sha256(texto.encode()).hexdigest()


def impressao(motor, interacoes: int | None = None) -> dict:
    """a impressao do gabarito do mundo, o registro do mundo fisico inteiro e, com os drives novos, o registro da novidade"""
    d = gm.impressao(motor, interacoes)
    d["fisico"] = _sha(json.dumps(motor.resumo_mundo_fisico(), sort_keys=True, default=repr))
    vistos = getattr(motor, "_vistos_em", None)
    d["vistos"] = None if vistos is None else _sha(json.dumps(sorted(vistos.items())))
    return d


class DonoComBolaPerto:
    """O dono com lugar que, a cada 4 passos, troca a ultima acao do passo por deixar a bola a 2 celulas do pet (o orcamento fecha igual;
    o mesmo de tests/test_corpo_no_mundo.py): a bola ao alcance, para o brincar e a rolagem entrarem nas vidas."""

    def __init__(self, base) -> None:
        self.base = base
        self.nome = base.nome

    def decidir(self, visao, rng):
        saida = list(self.base.decidir(visao, rng))
        if saida and visao.passo % 4 == 0:
            px, py = visao.estado["mundo"]["pet"]
            saida[-1] = DeixarBola(min(1023, px + 32), py)
        return saida


def casos_bancada():
    for nome_b in BANCADAS:
        for mundo in MUNDOS:
            for braco, cerebro in BRACOS:
                if nome_b == "completa" and (mundo != "fisico" or braco not in BRACOS_COMPLETA):
                    continue
                for dono in DONOS:
                    for lugar in LUGARES:
                        for s in SEMENTES:
                            yield (f"bancada|{nome_b}|{mundo}|{braco}~{cerebro}|{dono}|{lugar}|{s}",
                                   (nome_b, bv.EspecVida(dono, braco, s, None, mundo, cerebro, lugar)))


def casos_diretos():
    for layout in LAYOUTS:
        for corpo in CORPOS:
            for cerebro in CEREBROS:
                for lugar in ("perto", "longe"):
                    for s in SEMENTES:
                        yield f"direta|{layout}|{corpo}|{cerebro}|{lugar}|{s}", (layout, corpo, cerebro, lugar, s)


def fabricas_diretas(layout: str, corpo: str, cerebro: str):
    cm, cc = LAYOUTS[layout], CORPOS[corpo]
    if cerebro == "instinto":
        fp = lambda cfg=None: PoliticaInstintoMundo(cfg or CONFIG_PADRAO)  # noqa: E731
    else:
        fp = lambda cfg=None: PoliticaLobos(cfg or CONFIG_PADRAO, CONFIG_LOBOS_APRENDIZ, cfg_mundo=cm)  # noqa: E731
    if cc is None:
        fm = lambda p, cfg, s: MotorMundo(p, cfg, s, obediencia_desligada=True, cfg_mundo=cm)  # noqa: E731
    else:
        fm = lambda p, cfg, s: MotorMundoCorpo(p, cfg, s, obediencia_desligada=True, cfg_mundo=cm, cfg_corpo=cc)  # noqa: E731
    return fp, fm


def vida_direta(layout: str, corpo: str, cerebro: str, lugar: str, semente: int):
    fp, fm = fabricas_diretas(layout, corpo, cerebro)
    dono = DonoComBolaPerto(DonoComLugar(criar_dono("atencioso"), lugar, semente, "atencioso", LAYOUTS[layout]))
    return simular_vida_mundo("atencioso", dono, fp(CONFIG_PADRAO), semente, DIAS, 16 * DIAS, fm, rotulo_dono="atencioso")


def casos():
    yield from casos_bancada()
    yield from casos_diretos()


def vida_de_hoje(chave: str, caso) -> dict:
    if chave.startswith("bancada|"):
        nome_b, espec = caso
        v = BANCADAS[nome_b].vida(espec)
    else:
        v = vida_direta(*caso)
    return impressao(v.motor, v.interacoes)


def gerar() -> dict:
    return {chave: vida_de_hoje(chave, caso) for chave, caso in casos()}


if __name__ == "__main__":
    g = gerar()
    ARQUIVO.write_text(json.dumps(g, sort_keys=True, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"{ARQUIVO}: {len(g)} vidas")
