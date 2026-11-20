"""Gabarito dos grupos de hoje com os orgaos do Olfato social e da Audicao ligados e SEM o Olfato da comida, para o G2 do G-SEM-DIRECAO
(docs/futuro/dois_pets.md, secao 5.6; docs/TAREFA_V2_DOIS_PETS.md, etapa 8b): gravado com o codigo ANTES dos candidatos `cheiro_seguir` e
`cheiro_virar`. Com o orgao, a direcao do outro e dos sons sai da percepcao dos sentidos (`obs.social.sentidos`), que nenhum cerebro le
hoje; sem o Olfato da comida, a percepcao do mundo e os candidatos sao os de hoje. Estes grupos tem de sair iguais, byte a byte.

Os grupos: o `simular_grupo` direto, os dois pets com o instinto do mundo ou com os lobos aprendendo (com o corpo), o corpo inteiro da
etapa 6 com o Olfato social (`outro_pet`) e a Audicao (duas narinas, dois ouvidos), o B entrando no dia 0 ou no dia 1, os donos atencioso
e aleatorio (o aleatorio faz o pet chamar e emburrar), 2 sementes.

    python tests/gabarito_orgao_sem_direcao.py      # grava tests/gabaritos/orgao_sem_direcao_vidas_de_hoje.json (so com o codigo de antes)
"""
from __future__ import annotations

import json
import sys
from dataclasses import replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "tests"))

import gabarito_sentidos as gs  # noqa: E402

from digilab.config import (CONFIG_CORPO_DRIVES, CONFIG_GRUPO_LIGADA, CONFIG_LOBOS_APRENDIZ, CONFIG_OLFATO, CONFIG_OUVIDO,  # noqa: E402
                            CONFIG_PADRAO, CONFIG_SENTIDOS_LIGADA, TICKS_POR_DIA)
from digilab.donos import criar_dono  # noqa: E402
from digilab.grupo import PetDoGrupo, sementes_do_grupo, simular_grupo  # noqa: E402
from digilab.instinto_mundo import PoliticaInstintoMundo  # noqa: E402
from digilab.motor_corpo import com_corpo  # noqa: E402
from digilab.mundo import DonoComLugar, MotorMundo  # noqa: E402
from digilab.policies.lobos import PoliticaLobos  # noqa: E402

ARQUIVO = RAIZ / "tests" / "gabaritos" / "orgao_sem_direcao_vidas_de_hoje.json"
DIAS = 2
SEMENTES = (101, 202)                                   # so as dos testes
CEREBROS = ("instinto", "lobos")
ENTRADAS_B = (0, 1)
DONOS = ("atencioso", "aleatorio")
CM = gs.gdp.LAYOUTS["padrao"]
OLFATO_SOCIAL = replace(CONFIG_OLFATO, ligada=True, outro_pet=True)       # sem o Olfato da comida
OUVIDO = replace(CONFIG_OUVIDO, ligada=True)
MotorMundoCorpo = com_corpo(MotorMundo)


def fabricas(cerebro: str):
    if cerebro == "instinto":
        fp = lambda cfg=None: PoliticaInstintoMundo(cfg or CONFIG_PADRAO)  # noqa: E731
    else:
        fp = lambda cfg=None: PoliticaLobos(cfg or CONFIG_PADRAO, CONFIG_LOBOS_APRENDIZ, cfg_mundo=CM,  # noqa: E731
                                            cfg_corpo=CONFIG_CORPO_DRIVES)
    fm = lambda p, cfg, s, **kw: MotorMundoCorpo(p, cfg, s, obediencia_desligada=True, cfg_mundo=CM,  # noqa: E731
                                                 cfg_corpo=CONFIG_CORPO_DRIVES, cfg_olfato=OLFATO_SOCIAL, cfg_ouvido=OUVIDO, **kw)
    return fp, fm


def grupo(cerebro: str, entrada_b: int, dono: str, s: int):
    sementes = sementes_do_grupo(s, CONFIG_GRUPO_LIGADA.ids)
    pets = []
    for ident, entrada in (("A", 0), ("B", entrada_b * TICKS_POR_DIA)):
        fp, fm = fabricas(cerebro)
        d = DonoComLugar(criar_dono(dono), "perto", sementes[ident], dono, CM)
        pets.append(PetDoGrupo(ident, entrada, fp, fm, d, dono, cerebro))
    return simular_grupo(CM, s, pets, DIAS, cfg_sentidos=CONFIG_SENTIDOS_LIGADA)


def casos():
    for cerebro in CEREBROS:
        for entrada_b in ENTRADAS_B:
            for dono in DONOS:
                for s in SEMENTES:
                    yield f"{cerebro}|B{entrada_b}|{dono}|{s}", (cerebro, entrada_b, dono, s)


def impressao(g) -> dict:
    corpos = {i: m.corpo.para_dict() for i, m in g.motores.items()}
    return {**gs.impressao(g), "corpos": gs._sha(gs._texto(corpos))}


def gerar() -> dict:
    return {chave: impressao(grupo(*caso)) for chave, caso in casos()}


if __name__ == "__main__":
    g = gerar()
    ARQUIVO.write_text(json.dumps(g, sort_keys=True, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"{ARQUIVO}: {len(g)} grupos")
