"""Gabarito da cooperacao, Python x TS (docs/TAREFA_V3_COOPERACAO.md, etapa CO3; o G-PAR-COOP e o G-SEM-DECISAO).

As vidas de dois pets do grupo com a ConfigCooperacao ligada: as cinco da CO1 (exportar_gabarito_grupo.VIDAS) e duas com o cerebro aleatorio
do gabarito do mundo (CerebroAleatorio: escolhe qualquer candidato, o `seguir` inclusive, e emburra), para haver contatos de quem seguiu o
outro e contencoes. De cada vida: o registro do grupo, o traco por decisao de cada pet (o do exportar_gabarito_grupo_traco, com o alvo
escolhido pelo gancho) e o resumo da cooperacao (os atos, a pontuacao e a reputacao), mais as vezes, os contatos e as disputas.

O G-SEM-DECISAO no Python: o sha256 do resumo do grupo sem a chave `cooperacao` e o mesmo com a medida desligada (nas cinco da CO1, o do
gabarito grupo_python.json.gz; nas duas novas, o de uma segunda vida com a medida desligada). O exportador falha alto se diferir.

    python experiments/exportar_gabarito_cooperacao.py              # grava web/app/test/gabaritos/cooperacao_python.json.gz
    python experiments/exportar_gabarito_cooperacao.py --conferir   # refaz e compara com o gravado (falha alto se diferir)
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
from exportar_gabarito_mundo import CerebroAleatorio  # noqa: E402

from digilab.config import CONFIG_COOPERACAO_LIGADA, CONFIG_GRUPO_LIGADA, CONFIG_PADRAO, TICKS_POR_DIA  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.grupo import PetDoGrupo, sementes_do_grupo, simular_grupo  # noqa: E402
from digilab.mundo import DonoComLugar  # noqa: E402

ARQUIVO = RAIZ / "web" / "app" / "test" / "gabaritos" / "cooperacao_python.json.gz"
ARQUIVO_CO1 = RAIZ / "web" / "app" / "test" / "gabaritos" / "grupo_python.json.gz"
# as duas vidas novas, no formato de eg.VIDAS: os dois cerebros aleatorios no comedouro comum, e um aleatorio com um lobos
VIDAS_NOVAS = ((101, "padrao", "sem", ("aleatorio", "aleatorio"), ("atencioso", "atencioso"), 0, "comedouro"),
               (202, "padrao", "sem", ("aleatorio", "lobos"), ("relapso", "atencioso"), 0, "comedouro"))


def _fabricas(layout: str, corpo: str, cerebro: str):
    if cerebro != "aleatorio":
        return et._fabricas(layout, corpo, cerebro)
    _, fm = et._fabricas(layout, corpo, "instinto")
    return (lambda cfg=None: CerebroAleatorio(cfg or CONFIG_PADRAO)), fm


def _grupo(semente, layout, corpo, cerebros, donos, entrada_b, lugar, cfg_cooperacao):
    pets = []
    sementes = sementes_do_grupo(semente, CONFIG_GRUPO_LIGADA.ids)
    for ident, cerebro, dono, entrada in (("A", cerebros[0], donos[0], 0), ("B", cerebros[1], donos[1], entrada_b * TICKS_POR_DIA)):
        fp, fm = _fabricas(layout, corpo, cerebro)
        d = DonoComLugar(criar_dono(dono), lugar, sementes[ident], dono, eg.LAYOUTS[layout])
        pets.append(PetDoGrupo(ident, entrada, fp, fm, d, dono, cerebro))
    return simular_grupo(eg.LAYOUTS[layout], semente, pets, eg.DIAS, cfg_cooperacao=cfg_cooperacao)


def _sha_sem_coop(g) -> str:
    r = json.loads(eg._json(g.resumo()))
    r.pop("cooperacao", None)
    return eg._sha(eg._json(r))


def vida(v: tuple, sha_desligada: str) -> dict:
    g = _grupo(*v, CONFIG_COOPERACAO_LIGADA)
    sha = _sha_sem_coop(g)
    if sha != sha_desligada:
        raise SystemExit(f"G-SEM-DECISAO: a medida ligada mudou a vida {v}: {sha} x {sha_desligada}")
    r = g.resumo()
    semente, layout, corpo, cerebros, donos, entrada_b, lugar = v
    return {"semente": semente, "layout": layout, "corpo": corpo, "cerebros": list(cerebros), "donos": list(donos),
            "entrada_b_dias": entrada_b, "lugar": lugar, "resumo_sha256": sha,
            "registro": {"cabecalho": g.registro.cabecalho, "eventos": [e.para_dict() for e in g.registro.eventos]},
            "tracos": {i: et._jsonavel(m.traco) for i, m in sorted(g.motores.items())},
            "ordens": r["ordens"], "contatos": r["contatos"], "disputas": r["disputas"], "tick": r["tick"],
            "cooperacao": et._jsonavel(r["cooperacao"])}


def _consumo(ident: int, fa: float, fd: float, ha: float, hd: float) -> dict:
    return {"id": ident, "fome_antes": fa, "fome_depois": fd, "humor_antes": ha, "humor_depois": hd}


def sinteticos() -> dict:
    """Uma sequencia de chamadas a Cooperacao que cobre o que as vidas nao cobrem: a disputa "anti" (o perdedor abaixo do piso), a podre
    (ganho 0), o encostar sem testemunha, a repeticao no dia e a janela nova, duas oportunidades abertas e a meia-vida longa. O TS faz as
    mesmas chamadas e confere o resumo."""
    from digilab.cooperacao import Cooperacao
    perto = {"A": [0, 0], "B": [10, 0]}
    longe = {"A": [0, 0], "B": [300, 0]}
    raios = {"A": 96, "B": 96}
    chamadas = [
        {"f": "decisao", "tick": 10, "ident": "A", "maduras": [5], "outros": ["B"], "fome": 0.3, "consumo": None, "pos": perto},
        {"f": "decisao", "tick": 10, "ident": "B", "maduras": [5], "outros": ["A"], "fome": 0.3, "consumo": _consumo(5, 0.3, 0.6, 0.5, 0.5),
         "pos": perto},
        {"f": "decisao", "tick": 25, "ident": "A", "maduras": [7, 8], "outros": ["B"], "fome": 0.5, "consumo": _consumo(7, 0.5, 0.8, 0.4, 0.45),
         "pos": perto},
        {"f": "decisao", "tick": 25, "ident": "B", "maduras": [8], "outros": ["A"], "fome": 0.2, "consumo": None, "pos": longe},
        {"f": "fim", "tick": 25, "disputas": [{"vencedor": "A", "perdedor": "B", "comida": 7}],
         "contatos": [{"pets": ["A", "B"], "tipos": {"A": "encostou", "B": "encostaram"}}], "acoes": {"A": "comer", "B": "emburrar"},
         "pos": longe},
        {"f": "decisao", "tick": 40, "ident": "A", "maduras": [8], "outros": ["B"], "fome": 0.7, "consumo": None, "pos": perto},
        {"f": "decisao", "tick": 55, "ident": "B", "maduras": [8], "outros": ["A"], "fome": 0.25, "consumo": _consumo(8, 0.25, 0.5, 0.5, 0.5),
         "pos": perto},
        {"f": "decisao", "tick": 70, "ident": "B", "maduras": [9], "outros": ["A"], "fome": 0.4, "consumo": _consumo(9, 0.4, 0.4, 0.5, 0.3),
         "pos": perto},
        {"f": "decisao", "tick": 70, "ident": "A", "maduras": [], "outros": ["B"], "fome": 0.6, "consumo": None, "pos": perto},
        {"f": "fim", "tick": 70, "disputas": [{"vencedor": "B", "perdedor": "A", "comida": 9}], "contatos": [], "acoes": {"A": "explorar",
         "B": "comer"}, "pos": perto},
        {"f": "decisao", "tick": 1500, "ident": "A", "maduras": [12], "outros": ["B"], "fome": 0.5, "consumo": None, "pos": perto},
        {"f": "decisao", "tick": 1500, "ident": "B", "maduras": [12], "outros": ["A"], "fome": 0.3, "consumo": _consumo(12, 0.3, 0.6, 0.5, 0.5),
         "pos": perto},
    ]
    c = Cooperacao(CONFIG_COOPERACAO_LIGADA)
    for ch in chamadas:
        if ch["f"] == "decisao":
            c.decisao(ch["tick"], ch["ident"], ch["maduras"], ch["outros"], ch["fome"], ch["consumo"],
                      {k: tuple(v) for k, v in ch["pos"].items()}, raios)
        else:
            c.fim_do_tick(ch["tick"], ch["disputas"], ch["contatos"], ch["acoes"], {k: tuple(v) for k, v in ch["pos"].items()}, raios)
    return {"chamadas": chamadas, "raios": raios, "resumo": et._jsonavel(c.resumo(["A", "B"], 2 * TICKS_POR_DIA + 100))}


def gerar() -> dict:
    co1 = json.loads(gzip.decompress(ARQUIVO_CO1.read_bytes()).decode())
    vidas = []
    for v, vc in zip(eg.VIDAS, co1["vidas"]):
        if vc["semente"] != v[0]:
            raise SystemExit(f"a vida da CO1 nao e a de eg.VIDAS: {vc['semente']} x {v[0]}")
        vidas.append(vida(v, vc["resumo_sha256"]))
    for v in VIDAS_NOVAS:
        vidas.append(vida(v, _sha_sem_coop(_grupo(*v, None))))
    return {"fonte": "experiments/exportar_gabarito_cooperacao.py", "vidas": vidas, "sinteticos": sinteticos()}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--conferir", action="store_true", help="refaz e compara com o gabarito gravado")
    args = ap.parse_args()
    g = gerar()
    texto = json.dumps(g, sort_keys=True, separators=(",", ":"))
    if args.conferir:
        gravado = json.loads(gzip.decompress(ARQUIVO.read_bytes()).decode())
        if gravado != json.loads(texto):
            raise SystemExit(f"o gabarito da cooperacao mudou: {ARQUIVO}")
        print(f"igual ao gravado: {ARQUIVO}")
        return
    ARQUIVO.write_bytes(gzip.compress(texto.encode(), mtime=0))
    for v in g["vidas"]:
        atos = v["cooperacao"]["atos"]
        por = {a: sum(1 for x in atos if x["ato"] == a) for a in ("disputa", "contencao", "encostar")}
        print(f"vida {v['semente']} {v['cerebros']}: atos {por}, pontuacao {v['cooperacao']['pontuacao']}, "
              f"contatos {len(v['contatos'])}, disputas {len(v['disputas'])}")
    print(f"gravado: {ARQUIVO} ({ARQUIVO.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
