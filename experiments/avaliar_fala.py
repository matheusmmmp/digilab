"""Avaliacao da fala por LLM (Parte C, C6): quanto a LLM inventa causa.

    python experiments/avaliar_fala.py                         # Ollama local, qwen2.5:3b, 200 motivos
    python experiments/avaliar_fala.py --modelo llama3.2:3b
    python experiments/avaliar_fala.py --provedor claude --aceito-custo   # usa a API (respeita o teto)

Motivos reais: vidas de artifacts_ablacao/vidas (bandit e instinto) e partidas de
artifacts_combate_v2/amostra_replay.jsonl e artifacts_combate_v21/amostra_replay.jsonl
(tecnicas e condicoes do V2.1), metade com fator e metade sem, nos
estagios adolescente e adulto. Para cada um, gera a fala e registra se a validacao
aprovou ou barrou (e por que).

Saida em artifacts_fala/<provedor>_<modelo>/:
  falas.jsonl       uma linha por motivo: motivo, estagio, fala da LLM, aprovada, motivo da queda
  resumo.json       fracao aprovada, barrada por motivo, tempo medio
  revisao.csv       50 falas APROVADAS sorteadas para revisao humana: a validacao nao pega
                    sinonimos, entao a pergunta e "cita causa fora dos fatores?" (preencher s/n)
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import sys
import time
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

from diario import FABRICAS, inferir, ler_partidas  # noqa: E402
from digilab.combate_v2.bots import bot  # noqa: E402
from digilab.events import LogDeEventos  # noqa: E402
from digilab.combate_v2.v21.bots import lutador_adulto  # noqa: E402
from digilab.motivo import motivos_de_partida, motivos_de_partida_v21, motivos_de_vida  # noqa: E402
from servidor.fala_llm import GeradorFala, escolher_provedor, template  # noqa: E402

SEMENTE_AMOSTRA = 20260924


def coletar_motivos(n: int, semente: int = SEMENTE_AMOSTRA) -> list[tuple]:
    """[(motivo, estagio, humor)] reais, metade com fator e metade sem, estagios adolescente/adulto."""
    pool = []
    for arq in sorted((RAIZ / "artifacts_ablacao" / "vidas").glob("*@101.jsonl")):
        s, pol = inferir(arq)
        _, emb = motivos_de_vida(LogDeEventos.de_jsonl(arq.read_text(encoding="utf-8")), FABRICAS[pol], s)
        pool += [(m, h) for m, h in zip(emb.motivos, emb.humores)]
    for log in ler_partidas(RAIZ / "artifacts_combate_v2" / "amostra_replay.jsonl")[:60]:
        lut = (bot(log[0]["a"]), bot(log[0]["b"]))
        pool += [(m, None) for _, _, m, _ in motivos_de_partida(log, lut) if m.acao != "pesado"]
    for log in ler_partidas(RAIZ / "artifacts_combate_v21" / "amostra_replay.jsonl")[:60]:
        lut = tuple(lutador_adulto(*log[0][x].split("@")) for x in ("a", "b"))
        pool += [(m, None) for _, _, m, _ in motivos_de_partida_v21(log, lut) if m.acao != "pesado"]
    rng = random.Random(semente)
    com = [x for x in pool if x[0].fatores and not x[0].exploracao]
    sem = [x for x in pool if not x[0].fatores or x[0].exploracao]
    escolhidos = rng.sample(com, min(n // 2, len(com))) + rng.sample(sem, min(n - n // 2, len(sem)))
    rng.shuffle(escolhidos)
    return [(m, "adulto" if i % 2 else "adolescente", h) for i, (m, h) in enumerate(escolhidos)]


def avaliar(gerador: GeradorFala, motivos: list[tuple]) -> tuple[list[dict], dict]:
    linhas, quedas, tempos = [], Counter(), []
    for m, est, humor in motivos:
        t0 = time.perf_counter()
        r = gerador.gerar(m, est, humor)
        tempos.append(time.perf_counter() - t0)
        aprovada = r.fonte == "llm"
        if not aprovada:
            quedas[r.detalhe.split(":")[0]] += 1
        linhas.append({"motivo": m.para_dict(), "estagio": est, "fala": r.texto if aprovada else None,
                       "template": template(m, est, humor), "aprovada": aprovada, "queda": None if aprovada else r.detalhe})
    n = len(linhas)
    com = [l for l in linhas if l["motivo"]["fatores"]]
    resumo = {
        "n": n, "aprovadas": sum(l["aprovada"] for l in linhas), "fracao_aprovada": sum(l["aprovada"] for l in linhas) / n,
        "fracao_aprovada_com_fator": sum(l["aprovada"] for l in com) / len(com) if com else None,
        "fracao_aprovada_sem_fator": sum(l["aprovada"] for l in linhas if l not in com) / (n - len(com)) if n > len(com) else None,
        "quedas_por_tipo": dict(quedas), "tempo_medio_s": sum(tempos) / n, "tempo_max_s": max(tempos),
    }
    return linhas, resumo


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--provedor", choices=("ollama", "claude"), default="ollama")
    ap.add_argument("--modelo", default=None)
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--aceito-custo", action="store_true", help="obrigatorio com --provedor claude (chamadas pagas)")
    a = ap.parse_args(argv)
    if a.provedor == "claude" and not a.aceito_custo:
        raise SystemExit("com --provedor claude cada fala e paga: repita com --aceito-custo (o teto de gasto vale)")
    provedor, gasto, motivo = escolher_provedor(a.provedor, a.modelo)
    if provedor is None or not provedor.disponivel()[0]:
        raise SystemExit(f"provedor indisponivel: {motivo or provedor.disponivel()[1]}")
    gerador = GeradorFala(provedor, limite_por_minuto=10_000, gasto=gasto)
    motivos = coletar_motivos(a.n)
    linhas, resumo = avaliar(gerador, motivos)
    resumo.update({"provedor": provedor.nome, "modelo": provedor.modelo, "semente_amostra": SEMENTE_AMOSTRA,
                   "gasto": gasto.para_dict() if gasto else None})
    saida = RAIZ / "artifacts_fala" / f"{provedor.nome}_{provedor.modelo.replace(':', '-')}"
    saida.mkdir(parents=True, exist_ok=True)
    (saida / "falas.jsonl").write_text("".join(json.dumps(l, ensure_ascii=False) + "\n" for l in linhas),
                                       encoding="utf-8", newline="\n")
    (saida / "resumo.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    aprovadas = [l for l in linhas if l["aprovada"]]
    amostra = random.Random(SEMENTE_AMOSTRA).sample(aprovadas, min(50, len(aprovadas)))
    with (saida / "revisao.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["acao", "fatores_do_motivo", "estagio", "fala_da_llm", "frase_pronta", "cita_causa_fora_dos_fatores (s/n)"])
        for l in amostra:
            w.writerow([l["motivo"]["acao"], ", ".join(l["motivo"]["fatores"]) or "(nenhum)", l["estagio"], l["fala"], l["template"], ""])
    print(json.dumps(resumo, ensure_ascii=False, indent=2))
    print(f"arquivos em {saida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
