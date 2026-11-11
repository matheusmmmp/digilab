"""Gabarito do grupo de dois pets na ilha com agua, Python x TS (docs/TAREFA_V3_COOPERACAO.md, etapa CO4a; o G-PAR-GRUPO na agua).

Os pets do jogo nascem na ilha com agua (o `mvp_agua` das v22 e v23), em que so a agua barra o pet e cada um anda pelo controlador do contrato
(CONFIG_CONTRATO_AGUA). A CO4a deixa o controlador sozinho valer no grupo (digilab/mundo.py, MotorMundo; motor/mundo.ts, Mundo): cada pet anda
pelo dele, contra a agua do mundo partilhado. Este gabarito grava, no molde do grupo_traco_python.json.gz da CO2a, tres vidas de dois pets
nesse mundo: o registro do grupo, o traco por decisao de cada pet (com o registro do contrato no `ocorrido`) e o resumo do grupo.

    python experiments/exportar_gabarito_grupo_agua.py              # grava web/app/test/gabaritos/grupo_agua_python.json.gz
    python experiments/exportar_gabarito_grupo_agua.py --conferir   # refaz e compara com o gravado (falha alto se diferir)
"""
from __future__ import annotations

import argparse
import gzip
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import exportar_gabarito_grupo as eg  # noqa: E402
import exportar_gabarito_grupo_traco as et  # noqa: E402

from digilab.config import (CONFIG_CONTRATO_AGUA, CONFIG_CORPO_DRIVES, CONFIG_GRUPO_LIGADA, CONFIG_LOBOS_APRENDIZ,  # noqa: E402
                            CONFIG_MUNDO_MVP_AGUA, CONFIG_PADRAO, TICKS_POR_DIA)
from digilab.donos import criar_dono  # noqa: E402
from digilab.grupo import PetDoGrupo, sementes_do_grupo, simular_grupo  # noqa: E402
from digilab.instinto_mundo import PoliticaInstintoMundo  # noqa: E402
from digilab.mundo import DonoComLugar  # noqa: E402
from digilab.policies.lobos import PoliticaLobos  # noqa: E402

ARQUIVO = RAIZ / "web" / "app" / "test" / "gabaritos" / "grupo_agua_python.json.gz"
CM = CONFIG_MUNDO_MVP_AGUA
CORPOS = {"sem": None, "drives": CONFIG_CORPO_DRIVES}
# (semente, corpo, (cerebro A, cerebro B), (dono A, dono B), lugar da comida do dono)
VIDAS = ((101, "sem", ("lobos", "lobos"), ("atencioso", "atencioso"), "comedouro"),
         (202, "sem", ("instinto", "lobos"), ("atencioso", "relapso"), "perto"),
         (303, "drives", ("lobos", "lobos"), ("atencioso", "aleatorio"), "comedouro"))


def _fabricas(corpo: str, cerebro: str):
    cc = CORPOS[corpo]
    if cerebro == "instinto":
        fp = lambda cfg=None: PoliticaInstintoMundo(cfg or CONFIG_PADRAO)  # noqa: E731
    elif cerebro == "lobos":
        fp = lambda cfg=None: PoliticaLobos(cfg or CONFIG_PADRAO, CONFIG_LOBOS_APRENDIZ, cfg_mundo=CM, cfg_corpo=cc)  # noqa: E731
    else:
        raise ValueError(f"cerebro desconhecido: {cerebro!r}")
    if cc is None:
        fm = lambda p, cfg, s, **kw: et.MotorGrupoGravado(p, cfg, s, obediencia_desligada=True, cfg_mundo=CM,  # noqa: E731
                                                          cfg_contrato=CONFIG_CONTRATO_AGUA, **kw)
    else:
        fm = lambda p, cfg, s, **kw: et.MotorGrupoGravadoCorpo(p, cfg, s, obediencia_desligada=True, cfg_mundo=CM,  # noqa: E731
                                                               cfg_contrato=CONFIG_CONTRATO_AGUA, cfg_corpo=cc, **kw)
    return fp, fm


def grupo(semente: int, corpo: str, cerebros: tuple, donos: tuple, lugar: str):
    sementes = sementes_do_grupo(semente, CONFIG_GRUPO_LIGADA.ids)
    pets = []
    for ident, cerebro, dono in (("A", cerebros[0], donos[0]), ("B", cerebros[1], donos[1])):
        fp, fm = _fabricas(corpo, cerebro)
        d = DonoComLugar(criar_dono(dono), lugar, sementes[ident], dono, CM)
        pets.append(PetDoGrupo(ident, 0, fp, fm, d, dono, cerebro))
    return simular_grupo(CM, semente, pets, eg.DIAS)


def vida(v: tuple) -> dict:
    g = grupo(*v)
    r = json.loads(eg._json(g.resumo()))
    semente, corpo, cerebros, donos, lugar = v
    return {"semente": semente, "corpo": corpo, "cerebros": list(cerebros), "donos": list(donos), "lugar": lugar,
            "resumo_sha256": eg._sha(eg._json(r)),
            "registro": {"cabecalho": g.registro.cabecalho, "eventos": [e.para_dict() for e in g.registro.eventos]},
            "tracos": {i: et._jsonavel(m.traco) for i, m in sorted(g.motores.items())},
            "resumo": {"tick": r["tick"], "mundo": r["mundo"], "ordens": r["ordens"], "contatos": r["contatos"], "disputas": r["disputas"],
                       "pets": {i: {k: p[k] for k in ("fisico", "social", "entrada", "log")} for i, p in r["pets"].items()}}}


def gerar() -> dict:
    return {"fonte": "experiments/exportar_gabarito_grupo_agua.py", "layout": CM.layout.nome, "vidas": [vida(v) for v in VIDAS]}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--conferir", action="store_true", help="refaz e compara com o gabarito gravado")
    args = ap.parse_args()
    g = gerar()
    texto = json.dumps(g, sort_keys=True, separators=(",", ":"))
    if args.conferir:
        gravado = json.loads(gzip.decompress(ARQUIVO.read_bytes()).decode())
        if gravado != json.loads(texto):
            raise SystemExit(f"o gabarito do grupo na agua mudou: {ARQUIVO}")
        print(f"igual ao gravado: {ARQUIVO}")
        return
    ARQUIVO.write_bytes(gzip.compress(texto.encode(), mtime=0))
    for v in g["vidas"]:
        n = {i: sum(1 for o in t if o["op"] == "decisao") for i, t in v["tracos"].items()}
        com_contrato = sum(1 for t in v["tracos"].values() for o in t if o["op"] == "decisao" and o["ocorrido"] and "contrato" in o["ocorrido"])
        print(f"vida {v['semente']}: decisoes {n}, com o contrato {com_contrato}, contatos {len(v['resumo']['contatos'])}, "
              f"disputas {len(v['resumo']['disputas'])}")
    print(f"gravado: {ARQUIVO} ({ARQUIVO.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
