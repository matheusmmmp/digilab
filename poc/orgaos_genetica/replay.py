"""O log da POC e o replay: a vida sintetica e refeita so pelo log, e a trajetoria inteira tem um sha256.

Eventos (dicts com a chave `t`); qualquer outro levanta erro:
- `origem`: o genoma do pet, como dict, e o sha256 dele (o replay recalcula e confere). Se o pet nasceu de cruzamento, traz tambem
  `cruzamento` = {pai, mae, semente, mutacao_por_mil} com os genomas dos pais; o replay refaz o cruzamento e confere o filho;
- `comer`: {q}; `tick`: {n}.

Uso, sem nada pesado: `python -m orgaos_genetica.replay` de dentro de `poc/` imprime uma demonstracao pequena.
"""
from __future__ import annotations

import hashlib
import json
import random

from .fisiologia import Fisiologia
from .genoma import Genoma, cruzar, derivar_semente


def evento_origem(genoma: Genoma, pai: Genoma | None = None, mae: Genoma | None = None, semente: int | None = None,
                  mutacao_por_mil: int | None = None) -> dict:
    ev: dict = {"t": "origem", "genoma": genoma.como_dict(), "sha256": genoma.sha256()}
    if pai is not None:
        if mae is None or semente is None or mutacao_por_mil is None:
            raise ValueError("origem por cruzamento precisa de pai, mae, semente e mutacao_por_mil")
        ev["cruzamento"] = {"pai": pai.como_dict(), "mae": mae.como_dict(), "semente": semente,
                            "mutacao_por_mil": mutacao_por_mil}
    return ev


def _genoma_da_origem(ev: dict) -> Genoma:
    g = Genoma.de_dict(ev["genoma"])
    if g.sha256() != ev["sha256"]:
        raise ValueError("o sha256 do genoma na origem nao confere")
    cz = ev.get("cruzamento")
    if cz is not None:
        refeito = cruzar(Genoma.de_dict(cz["pai"]), Genoma.de_dict(cz["mae"]), cz["semente"], cz["mutacao_por_mil"]).filho
        if refeito != g:
            raise ValueError("o cruzamento refeito nao da o genoma da origem")
    return g


def reproduzir(log: list[dict]) -> tuple[Fisiologia, list[tuple[int, int, int, int]], str]:
    """Refaz a vida: devolve a fisiologia final, a trajetoria (o estado depois de cada tick) e o sha256 da trajetoria."""
    if not log or log[0].get("t") != "origem":
        raise ValueError("o log tem de comecar pela origem")
    corpo = Fisiologia(_genoma_da_origem(log[0]))
    trajetoria = [corpo.estado()]
    for i, ev in enumerate(log[1:], start=1):
        t = ev.get("t")
        if t == "comer":
            corpo.comer(ev["q"])
        elif t == "tick":
            n = ev["n"]
            if type(n) is not int or n <= 0:
                raise ValueError(f"evento {i}: tick com n invalido {n!r}")
            for _ in range(n):
                corpo.tick()
                trajetoria.append(corpo.estado())
        elif t == "origem":
            raise ValueError(f"evento {i}: segunda origem no mesmo log")
        else:
            raise ValueError(f"evento {i}: tipo desconhecido {t!r}")
    texto = json.dumps({"trajetoria": trajetoria, "contas": corpo.contas}, sort_keys=True)
    return corpo, trajetoria, hashlib.sha256(texto.encode("ascii")).hexdigest()


def entradas_sinteticas(semente: int, n_refeicoes: int = 6) -> list[dict]:
    """Refeicoes e intervalos sinteticos, numa rng propria (`poc-entradas`), separada da do genoma e da da heranca.

    As faixas (refeicao de 300 a 1500, intervalo de 20 a 60 ticks; exemplo, SEM FONTE) deixam o cenario principal equilibrado: a
    energia fica longe do teto e nada e descartado. O excesso tem teste proprio, com uma refeicao grande de proposito."""
    rng = random.Random(derivar_semente("poc-entradas", semente))
    eventos: list[dict] = []
    for _ in range(n_refeicoes):
        eventos.append({"t": "comer", "q": rng.randint(300, 1500)})
        eventos.append({"t": "tick", "n": rng.randint(20, 60)})
    return eventos


def _demo() -> None:
    from .genoma import sortear
    pai, mae = sortear(1), sortear(2)
    cz = cruzar(pai, mae, semente=3)
    log = [evento_origem(cz.filho, pai, mae, 3, 150)] + entradas_sinteticas(4)
    corpo, traj, sha = reproduzir(log)
    print("pai  ", pai.como_dict())
    print("mae  ", mae.como_dict())
    print("filho", cz.filho.como_dict(), "mutacoes:", cz.mutacoes)
    print("ticks", len(traj) - 1, "final (estomago, energia, fome, saciedade):", corpo.estado())
    print("contas", corpo.contas)
    print("sha256 da trajetoria", sha)
    print("replay igual:", reproduzir(log)[2] == sha)


if __name__ == "__main__":
    _demo()
