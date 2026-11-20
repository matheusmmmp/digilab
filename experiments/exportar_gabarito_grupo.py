"""Gabarito do grupo de dois pets, Python x TS (docs/TAREFA_V3_COOPERACAO.md, etapa CO1; o G-PAR-GRUPO da CO2).

Gravado com o codigo da `main` ANTES de qualquer mudanca da frente: o `motor/grupo.ts` da CO2 tem de reproduzir estes numeros. O lado de
um pet so (o G-HOJE do Python) ja tem gabarito: tests/gabaritos/dois_pets_vidas_de_hoje.json, que o tests/test_grupo.py confere com o
`simular_grupo` de um pet.

Exporta, de digilab/grupo.py:
  ordem   a vez sorteada (DP-2): derivar_semente("mundo-ordem", s) e o Fisher-Yates por randrange sobre listas de 2 e de 3 ids, em
          sementes pequenas e de 64 bits, 40 sorteios cada (o que o TS tem de repetir com o random.Random do Python);
  vidas   vidas de 3 dias de dois pets do mesmo dono sintetico, sem os sentidos do degrau 1b (a ConfigSentidos de hoje, desligada):
          o cabecalho e os eventos do registro do grupo, as vezes sorteadas, os contatos, as disputas e o resumo do grupo (o mundo e,
          de cada pet, o estado, as acoes, as rngs, o mundo fisico, o estado interno do cerebro e o log). O sha256 do resumo vai junto,
          para a conferencia rapida.

As vidas (semente do grupo, layout, corpo, cerebro de A e de B, dono de A e de B, entrada de B em dias, lugar da comida do dono):
  101  padrao    sem     lobos     lobos     atencioso  relapso    0  perto      os dois aprendendo, donos diferentes no cuidado
  202  afastado  sem     instinto  lobos     atencioso  atencioso  0  comedouro  o instinto e o aprendiz, o comedouro comum
  303  padrao    drives  lobos     lobos     atencioso  aleatorio  0  perto      o corpo dos drives novos (a curiosidade, o tedio, a solidao)
  404  padrao    sem     lobos     lobos     atencioso  atencioso  1  comedouro  o segundo pet entra no dia 1 (o relogio de cada pet)
  505  padrao    sem     instinto  instinto  atencioso  atencioso  0  comedouro  dois instintos no comedouro comum (a disputa)

    python experiments/exportar_gabarito_grupo.py          # grava web/app/test/gabaritos/grupo_python.json.gz
    python experiments/exportar_gabarito_grupo.py --conferir   # refaz e compara com o gravado (falha alto se diferir)
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import random
import sys
from dataclasses import replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.config import (CONFIG_CORPO_DRIVES, CONFIG_GRUPO_LIGADA, CONFIG_LOBOS_APRENDIZ, CONFIG_MUNDO_LIGADA,  # noqa: E402
                            CONFIG_PADRAO, LAYOUT_MUNDO_AFASTADO, TICKS_POR_DIA)
from digilab.donos import criar_dono  # noqa: E402
from digilab.grupo import ROTULO_ORDEM, PetDoGrupo, sementes_do_grupo, simular_grupo  # noqa: E402
from digilab.instinto_mundo import PoliticaInstintoMundo  # noqa: E402
from digilab.motor_corpo import com_corpo  # noqa: E402
from digilab.mundo import DonoComLugar, MotorMundo  # noqa: E402
from digilab.policies.lobos import PoliticaLobos  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402

ARQUIVO = RAIZ / "web" / "app" / "test" / "gabaritos" / "grupo_python.json.gz"
DIAS = 3
LAYOUTS = {"padrao": CONFIG_MUNDO_LIGADA, "afastado": replace(CONFIG_MUNDO_LIGADA, layout=LAYOUT_MUNDO_AFASTADO)}
CORPOS = {"sem": None, "drives": CONFIG_CORPO_DRIVES}
MotorMundoCorpo = com_corpo(MotorMundo)
# (semente, layout, corpo, (cerebro A, cerebro B), (dono A, dono B), entrada de B em dias, lugar da comida do dono)
VIDAS = ((101, "padrao", "sem", ("lobos", "lobos"), ("atencioso", "relapso"), 0, "perto"),
         (202, "afastado", "sem", ("instinto", "lobos"), ("atencioso", "atencioso"), 0, "comedouro"),
         (303, "padrao", "drives", ("lobos", "lobos"), ("atencioso", "aleatorio"), 0, "perto"),
         (404, "padrao", "sem", ("lobos", "lobos"), ("atencioso", "atencioso"), 1, "comedouro"),
         (505, "padrao", "sem", ("instinto", "instinto"), ("atencioso", "atencioso"), 0, "comedouro"))
SEMENTES_ORDEM = (101, 202, 2 ** 40 + 7, 2 ** 63 - 25)
SORTEIOS_ORDEM = 40


def _fabricas(layout: str, corpo: str, cerebro: str):
    """as fabricas do tests/test_grupo.py (`fabricas`), com o motor aceitando o mundo e a entrada do grupo"""
    cm, cc = LAYOUTS[layout], CORPOS[corpo]
    if cerebro == "instinto":
        fp = lambda cfg=None: PoliticaInstintoMundo(cfg or CONFIG_PADRAO)  # noqa: E731
    elif cerebro == "lobos":
        fp = lambda cfg=None: PoliticaLobos(cfg or CONFIG_PADRAO, CONFIG_LOBOS_APRENDIZ, cfg_mundo=cm, cfg_corpo=cc)  # noqa: E731
    else:
        raise ValueError(f"cerebro desconhecido: {cerebro!r}")
    if cc is None:
        fm = lambda p, cfg, s, **kw: MotorMundo(p, cfg, s, obediencia_desligada=True, cfg_mundo=cm, **kw)  # noqa: E731
    else:
        fm = lambda p, cfg, s, **kw: MotorMundoCorpo(p, cfg, s, obediencia_desligada=True, cfg_mundo=cm,  # noqa: E731
                                                     cfg_corpo=cc, **kw)
    return fp, fm


def _sha(texto: str) -> str:
    return hashlib.sha256(texto.encode()).hexdigest()


def _json(obj) -> str:
    return json.dumps(obj, sort_keys=True, default=repr)


def ordem() -> list[dict]:
    """o sorteio da vez (Grupo._sortear), fora do grupo: a semente do fluxo e as ordens de 40 ticks seguidos, para 2 e para 3 ids"""
    casos = []
    for s in SEMENTES_ORDEM:
        for ids in (["A", "B"], ["A", "B", "C"]):
            semente_fluxo = derivar_semente(ROTULO_ORDEM, s)
            rng = random.Random(semente_fluxo)
            ordens = []
            for _ in range(SORTEIOS_ORDEM):
                o = list(ids)
                for k in range(len(o) - 1, 0, -1):
                    j = rng.randrange(k + 1)
                    o[k], o[j] = o[j], o[k]
                ordens.append(o)
            casos.append({"semente": s, "ids": ids, "semente_fluxo": semente_fluxo, "ordens": ordens})
    return casos


def vida(semente: int, layout: str, corpo: str, cerebros: tuple, donos: tuple, entrada_b: int, lugar: str) -> dict:
    pets = []
    sementes = sementes_do_grupo(semente, CONFIG_GRUPO_LIGADA.ids)
    for ident, cerebro, dono, entrada in (("A", cerebros[0], donos[0], 0), ("B", cerebros[1], donos[1], entrada_b * TICKS_POR_DIA)):
        fp, fm = _fabricas(layout, corpo, cerebro)
        d = DonoComLugar(criar_dono(dono), lugar, sementes[ident], dono, LAYOUTS[layout])
        pets.append(PetDoGrupo(ident, entrada, fp, fm, d, dono, cerebro))
    g = simular_grupo(LAYOUTS[layout], semente, pets, DIAS)
    resumo = json.loads(_json(g.resumo()))
    registro = {"cabecalho": g.registro.cabecalho,
                "eventos": [{"tick": e.tick, "tipo": e.tipo, "valor": e.valor, "destino": e.destino, "pet": e.pet, "origem": e.origem}
                            for e in g.registro.eventos]}
    return {"semente": semente, "layout": layout, "corpo": corpo, "cerebros": list(cerebros), "donos": list(donos),
            "entrada_b_dias": entrada_b, "lugar": lugar, "dias": DIAS, "sementes": sementes, "interacoes": g.interacoes,
            "registro": json.loads(_json(registro)), "n_ordens": len(g.ordens), "n_contatos": len(g.contatos),
            "n_disputas": len(g.disputas), "resumo_sha256": _sha(_json(resumo)), "resumo": resumo}


def gerar() -> dict:
    return {"fonte": "experiments/exportar_gabarito_grupo.py", "ordem": ordem(),
            "vidas": [vida(*v) for v in VIDAS]}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--conferir", action="store_true", help="refaz e compara com o gabarito gravado")
    args = ap.parse_args()
    g = gerar()
    texto = json.dumps(g, sort_keys=True, separators=(",", ":"))
    if args.conferir:
        gravado = json.loads(gzip.decompress(ARQUIVO.read_bytes()).decode())
        if gravado != json.loads(texto):
            raise SystemExit(f"o gabarito do grupo mudou: {ARQUIVO}")
        print(f"igual ao gravado: {ARQUIVO}")
        return
    ARQUIVO.write_bytes(gzip.compress(texto.encode(), mtime=0))
    for v in g["vidas"]:
        print(f"vida {v['semente']}: {v['n_ordens']} vezes sorteadas, {v['n_contatos']} contatos, {v['n_disputas']} disputas, "
              f"resumo {v['resumo_sha256'][:12]}")
    print(f"gravado: {ARQUIVO} ({ARQUIVO.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
