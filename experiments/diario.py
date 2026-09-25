"""Diario: motivo e expressao, decisao a decisao. Ferramenta de INSPECAO, nao interface de jogo.

    python experiments/diario.py --log artifacts_ablacao/vidas/atencioso-bandit@101.jsonl
    python experiments/diario.py --partida artifacts_combate_v2/amostra_replay.jsonl --indice 0 --estagio adulto

Vida: a semente e a politica saem do nome do arquivo (<braco>@<semente>.jsonl;
braco terminado em "-instinto" = PoliticaInstinto, senao bandit), ou de
--semente/--politica. O estagio vem da idade (PROVISORIO, ConfigExpressao).

Partida: o log do combate V2 (um arquivo pode ter varias partidas; --indice
escolhe). Os lutadores sao os bots do cabecalho; hash diferente = erro. O
estagio e parametro explicito.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.config import TICKS_POR_DIA  # noqa: E402
from digilab.events import LogDeEventos  # noqa: E402
from digilab.expressao import ESTAGIOS, estagio_por_idade, expressar  # noqa: E402
from digilab.memoria import PoliticaBanditMemoria  # noqa: E402
from digilab.memoria_espacos import PoliticaBanditEspacos  # noqa: E402
from digilab.motivo import motivos_de_partida, motivos_de_vida  # noqa: E402
from digilab.policies import PoliticaBandit  # noqa: E402
from digilab.policy import PoliticaInstinto  # noqa: E402

FABRICAS = {"bandit": lambda c: PoliticaBandit(c), "instinto": lambda c: PoliticaInstinto(c),
            "bandit_memoria": lambda c: PoliticaBanditMemoria(c),
            "bandit_espacos": lambda c: PoliticaBanditEspacos(c)}


def inferir(caminho: Path) -> tuple[int, str]:
    """Semente e politica pelo nome; vidas em artifacts_v1_memoria/ usam bandit_memoria."""
    m = re.fullmatch(r"(.+)@(\d+)\.jsonl", caminho.name)
    if not m:
        raise ValueError(f"nao consigo inferir braco/semente de {caminho.name!r}; use --semente e --politica")
    if "artifacts_v1_memoria_espacos" in caminho.parts:
        return int(m.group(2)), "bandit_espacos"
    if "artifacts_v1_memoria" in caminho.parts:
        return int(m.group(2)), "bandit_memoria"
    return int(m.group(2)), "instinto" if m.group(1).endswith("-instinto") else "bandit"


def diario_vida(caminho: Path, semente: int | None = None, politica: str | None = None) -> list[dict]:
    s_inf, p_inf = inferir(caminho) if semente is None or politica is None else (None, None)
    semente = semente if semente is not None else s_inf
    politica = politica or p_inf
    if politica not in FABRICAS:
        raise ValueError(f"politica desconhecida: {politica!r}")
    log = LogDeEventos.de_jsonl(caminho.read_text(encoding="utf-8"))
    _, emb = motivos_de_vida(log, FABRICAS[politica], semente)
    linhas = []
    for m, humor in zip(emb.motivos, emb.humores):
        est = estagio_por_idade(m.tick / TICKS_POR_DIA)
        linhas.append({"tick": m.tick, "dia": m.tick // TICKS_POR_DIA + 1, "estagio": est, "humor": humor,
                       "motivo": m.para_dict(), "expressao": expressar(m, est, humor).conteudo})
    return linhas


def ler_partidas(caminho: Path) -> list[list[dict]]:
    partidas, atual = [], []
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        if not linha.strip():
            continue
        ev = json.loads(linha)
        if ev.get("tipo") == "cabecalho" and atual:
            partidas.append(atual)
            atual = []
        atual.append(ev)
    if atual:
        partidas.append(atual)
    return partidas


def diario_partida(log: list[dict], estagio: str) -> list[dict]:
    from digilab.combate_v2.bots import bot

    if estagio not in ESTAGIOS:
        raise ValueError(f"estagio desconhecido: {estagio!r}")
    cab = log[0]
    lutadores = (bot(cab["a"]), bot(cab["b"]))
    if (lutadores[0].hash(), lutadores[1].hash()) != (cab["hash_a"], cab["hash_b"]):
        raise ValueError("lutadores do log nao sao os bots atuais (hash diferente)")
    return [{"turno": t, "lado": lado, "bot": (cab["a"], cab["b"])[lado], "estagio": estagio,
             "motivo": m.para_dict(), "expressao": expressar(m, estagio).conteudo}
            for t, lado, m, _ in motivos_de_partida(log, lutadores)]


def formatar(linhas: list[dict]) -> str:
    out = []
    for l in linhas:
        m = l["motivo"]
        quando = f"t{l['tick']:>6} D{l['dia']:<2}" if "tick" in l else f"turno {l['turno']:>2} {l['bot']:>11}"
        causa = "exploracao" if m["exploracao"] else (",".join(m["fatores"]) or "-")
        refs = ",".join(map(str, m["evento_ref"])) or "-"
        out.append(f"{quando} {l['estagio']:<11} {m['acao']:<15} [{causa} | ref {refs}]  {l['expressao']}")
    return "\n".join(out) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--log", type=Path)
    g.add_argument("--partida", type=Path)
    ap.add_argument("--estagio", choices=ESTAGIOS)
    ap.add_argument("--indice", type=int, default=0)
    ap.add_argument("--semente", type=int)
    ap.add_argument("--politica", choices=sorted(FABRICAS))
    ap.add_argument("--saida", type=Path, help="grava o texto aqui (e .jsonl ao lado) em vez de imprimir")
    ap.add_argument("--formato", choices=("texto", "jsonl"), default="texto")
    a = ap.parse_args(argv)
    if a.log:
        linhas = diario_vida(a.log, a.semente, a.politica)
    else:
        if not a.estagio:
            ap.error("--partida exige --estagio")
        partidas = ler_partidas(a.partida)
        if not 0 <= a.indice < len(partidas):
            raise IndexError(f"--indice {a.indice} fora de 0..{len(partidas) - 1}")
        linhas = diario_partida(partidas[a.indice], a.estagio)
    texto = formatar(linhas) if a.formato == "texto" else "".join(json.dumps(l, ensure_ascii=False) + "\n" for l in linhas)
    if a.saida:
        a.saida.parent.mkdir(parents=True, exist_ok=True)
        a.saida.write_text(texto, encoding="utf-8", newline="\n")
    else:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stdout.write(texto)
    return 0


if __name__ == "__main__":
    sys.exit(main())
