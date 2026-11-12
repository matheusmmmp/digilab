"""Gabarito do G-PAR-CO6, Python x TS (docs/ESPEC_V3_COOPERACAO_CO6.md, secao 4): a mesma reputacao e o mesmo `k`, tick a tick.

  sinteticos  uma sequencia de chamadas a Cooperacao com a CO6 ligada (atos que fazem reputacao positiva e negativa, testemunhados ou
              nao; encontros dentro e fora do raio de cada um; a idade cruzando o fim do bebe e da crianca), com o `k` de cada pet e a
              reputacao de cada um vista pelo outro depois de cada `fim_do_tick_k`: o passo, o decaimento e o teto por estagio;
  vidas       as 7 vidas do gabarito da CO3 (exportar_gabarito_cooperacao: as 5 da CO1 e as 2 do cerebro aleatorio), refeitas com a CO6
              ligada: o `k` de cada presente no fim de cada tick, a reputacao e o peso dos deveres da percepcao social de cada decisao,
              e o resumo da cooperacao. O TS as rejoga do registro com o traco da CO3 (o engine e o cerebro de fora).

O G-SEM-DECISAO-CO6 no Python: o sha256 do resumo de cada vida sem a chave `cooperacao` e o do gabarito da CO3 (a CO6 so muda a percepcao
social, que o A e o instinto nao leem). O exportador falha alto se diferir.

    python experiments/exportar_gabarito_co6_par.py              # grava web/app/test/gabaritos/co6_python.json.gz
    python experiments/exportar_gabarito_co6_par.py --conferir   # refaz e compara com o gravado (falha alto se diferir)
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

import exportar_gabarito_cooperacao as ec  # noqa: E402
import exportar_gabarito_grupo as eg  # noqa: E402
import exportar_gabarito_grupo_traco as et  # noqa: E402

from digilab.config import CONFIG_COOPERACAO_CO6, TICKS_POR_DIA  # noqa: E402
from digilab.cooperacao import Cooperacao  # noqa: E402

ARQUIVO = RAIZ / "web" / "app" / "test" / "gabaritos" / "co6_python.json.gz"


def _consumo(ident: int, fa: float, fd: float) -> dict:
    return {"id": ident, "fome_antes": fa, "fome_depois": fd, "humor_antes": 0.5, "humor_depois": 0.5}


def sinteticos() -> dict:
    """as chamadas e, depois de cada `k`, o `k` e a reputacao de cada pet"""
    perto = {"A": [0, 0], "B": [10, 0]}
    meio = {"A": [0, 0], "B": [100, 0]}                 # dentro do raio de B (120), fora do de A (96): um nao ve o outro
    raios = {"A": 96, "B": 120}
    dia = TICKS_POR_DIA
    chamadas = [
        # B deixa a comida para A, que a come: a contencao de B, testemunhada por A (reputacao de B vista por A positiva)
        {"f": "decisao", "tick": 5, "ident": "B", "maduras": [1], "outros": ["A"], "fome": 0.6, "consumo": None, "pos": perto},
        {"f": "decisao", "tick": 6, "ident": "A", "maduras": [1], "outros": ["B"], "fome": 0.3, "consumo": _consumo(1, 0.3, 0.6),
         "pos": perto},
        {"f": "k", "de": 6, "ate": 20, "pos": perto, "nasceu": {"A": 0, "B": 0}},        # bebes: o teto 0
        {"f": "k", "de": 20, "ate": 30, "pos": perto, "nasceu": {"A": -dia, "B": -dia}},  # criancas: A tem encontro, B nao
        {"f": "k", "de": 30, "ate": 40, "pos": meio, "nasceu": {"A": -dia, "B": -dia}},   # fora do raio de A: sem encontro, decai
        {"f": "k", "de": 40, "ate": 340, "pos": perto, "nasceu": {"A": -dia, "B": -dia}},  # o teto da crianca
        {"f": "k", "de": 340, "ate": 360, "pos": perto, "nasceu": {"A": -3 * dia + 350, "B": -dia}},   # A vira adolescente no meio
        # A pega a comida de B com fome (a disputa "anti", testemunhada por B): a reputacao de A vista por B negativa
        {"f": "decisao", "tick": 360, "ident": "B", "maduras": [2], "outros": ["A"], "fome": 0.2, "consumo": None, "pos": perto},
        {"f": "decisao", "tick": 360, "ident": "A", "maduras": [2], "outros": ["B"], "fome": 0.5, "consumo": _consumo(2, 0.5, 0.9),
         "pos": perto},
        {"f": "fim", "tick": 360, "disputas": [{"vencedor": "A", "perdedor": "B", "comida": 2}], "contatos": [],
         "acoes": {"A": "comer", "B": "emburrar"}, "pos": perto},
        {"f": "k", "de": 360, "ate": 380, "pos": perto, "nasceu": {"A": -3 * dia, "B": -7 * dia}},     # B adulto, reputacao de A < 0
        {"f": "k", "de": 380, "ate": 1900, "pos": meio, "nasceu": {"A": -3 * dia, "B": -7 * dia}},     # a meia-vida longa
    ]
    c = Cooperacao(CONFIG_COOPERACAO_CO6)
    serie = []
    for ch in chamadas:
        pos = {k: tuple(v) for k, v in ch["pos"].items()}
        if ch["f"] == "decisao":
            c.decisao(ch["tick"], ch["ident"], ch["maduras"], ch["outros"], ch["fome"], ch["consumo"], pos, raios)
        elif ch["f"] == "fim":
            c.fim_do_tick(ch["tick"], ch["disputas"], ch["contatos"], ch["acoes"], pos, raios)
        else:
            for t in range(ch["de"], ch["ate"]):
                c.fim_do_tick_k(t, pos, raios, {i: t - n for i, n in ch["nasceu"].items()})
                serie.append([t, c.peso_dever("A"), c.peso_dever("B"), c.reputacao("A", "B", t), c.reputacao("B", "A", t)])
    return {"chamadas": chamadas, "raios": raios, "serie": serie, "resumo": et._jsonavel(c.resumo(["A", "B"], 1900))}


def vida(v: tuple, sha_co3: str) -> dict:
    """uma vida da CO3 com a CO6 ligada: o `k` no fim de cada tick e a percepcao da CO6 de cada decisao"""
    serie: list = []
    original = Cooperacao.fim_do_tick_k

    def gravar(self, tick, posicoes, raios, idades):
        original(self, tick, posicoes, raios, idades)
        serie.append([tick, {i: self.peso_dever(i) for i in sorted(posicoes)}])
    Cooperacao.fim_do_tick_k = gravar
    try:
        g = ec._grupo(*v, CONFIG_COOPERACAO_CO6)
    finally:
        Cooperacao.fim_do_tick_k = original
    sha = ec._sha_sem_coop(g)
    if sha != sha_co3:
        raise SystemExit(f"G-SEM-DECISAO-CO6: a CO6 ligada mudou a vida {v}: {sha} x {sha_co3}")
    if [t for t, _ in serie] != list(range(g.tick)):
        raise SystemExit(f"o `k` nao andou em todo tick na vida {v}")
    percepcao = {i: [[op["tick_mundo"], op["social"]["reputacao"], op["social"]["peso_dever"]]
                     for op in m.traco if op["op"] == "decisao" and op["social"] is not None]
                 for i, m in sorted(g.motores.items())}
    semente, layout, corpo, cerebros, *_ = v
    return {"semente": semente, "layout": layout, "cerebros": list(cerebros), "k": serie, "percepcao": percepcao,
            "cooperacao": et._jsonavel(g.resumo()["cooperacao"])}


def gerar() -> dict:
    co3 = json.loads(gzip.decompress(ec.ARQUIVO.read_bytes()).decode())
    vidas_v = list(eg.VIDAS) + list(ec.VIDAS_NOVAS)
    if len(vidas_v) != len(co3["vidas"]):
        raise SystemExit("as vidas da CO3 mudaram")
    vidas = []
    for v, vc in zip(vidas_v, co3["vidas"]):
        if vc["semente"] != v[0] or vc["cerebros"] != list(v[3]):
            raise SystemExit(f"a vida da CO3 nao e a esperada: {vc['semente']} x {v[0]}")
        vidas.append(vida(v, vc["resumo_sha256"]))
    return {"fonte": "experiments/exportar_gabarito_co6_par.py", "vidas": vidas, "sinteticos": sinteticos()}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--conferir", action="store_true", help="refaz e compara com o gabarito gravado")
    args = ap.parse_args()
    g = gerar()
    texto = json.dumps(g, sort_keys=True, separators=(",", ":"))
    if args.conferir:
        gravado = json.loads(gzip.decompress(ARQUIVO.read_bytes()).decode())
        if gravado != json.loads(texto):
            raise SystemExit(f"o gabarito do G-PAR-CO6 mudou: {ARQUIVO}")
        print(f"igual ao gravado: {ARQUIVO}")
        return
    ARQUIVO.write_bytes(gzip.compress(texto.encode(), mtime=0))
    for v in g["vidas"]:
        ks = [max(k.values()) for _, k in v["k"]]
        print(f"vida {v['semente']} {v['cerebros']}: k maximo {max(ks)}, k final {v['k'][-1][1]}, "
              f"reputacao {v['cooperacao']['reputacao']}")
    print(f"sinteticos: k final {g['sinteticos']['serie'][-1]}")
    print(f"gravado: {ARQUIVO} ({ARQUIVO.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
