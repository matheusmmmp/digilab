"""Ensaio QUALITATIVO da M3 (nao e avaliacao, sem gate): as 8 mensagens de diagnostico/conversa_estagios.py, no gemma2:9b local,
nos estados de adolescente e adulto, com o livre-v2 (o prompt de hoje) e o conversa-v1, lado a lado.
Mesmo estado, mesmas sementes de diagnostico (7000+i adolescente, 7100+i adulto; NAO sao faixas do plano), historico que cresce a
cada turno (so do estagio), sem estilo da especie, sem comando. Uma run, um processo.

    python artifacts_conversa_pet/m3_ensaio/ensaio.py artifacts_conversa_pet/m3_ensaio
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from digilab_fala_livre.gerar import gerar  # noqa: E402
from digilab_fala_livre.ollama import ClienteOllama  # noqa: E402
from digilab_fala_livre.prompt import VERSAO_CONVERSA_V1, VERSAO_PROMPT  # noqa: E402

_spec = importlib.util.spec_from_file_location("conversa_estagios", RAIZ / "artifacts_conversa_pet/diagnostico/conversa_estagios.py")
_ce = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ce)           # so para ler MSGS e estado(); o main dele nao roda (guardado por __name__)
MSGS, estado = _ce.MSGS, _ce.estado


def conversa(cli, versao, estagio, forma, semente0):
    hist, saida = [], []
    for i, m in enumerate(MSGS):
        h = [(j, p, estagio) for j, p in hist] if versao == VERSAO_CONVERSA_V1 else list(hist)
        r = gerar(cli, estado(estagio, forma), "conversa", m, h, semente=semente0 + i, versao=versao)
        hist.append((m, r.fala))
        saida.append({"jogador": m, "pet": r.fala, "fatos": list(r.fatos_citados), "lat": r.latencia_s, "erro": r.erro})
        print(f"{versao:12} {estagio:11} {m!r:45} -> {r.fala!r} {list(r.fatos_citados)} {r.erro or ''}", flush=True)
    return saida


def main(destino: Path):
    cli = ClienteOllama("gemma2:9b")
    out = {}
    for estagio, forma, s0 in (("adolescente", "Growlmon", 7000), ("adulto", "WarGrowlmon", 7100)):
        out[estagio] = {v: conversa(cli, v, estagio, forma, s0) for v in (VERSAO_PROMPT, VERSAO_CONVERSA_V1)}
    (destino / "ensaio.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    md = ["# Ensaio qualitativo da M3 (não é avaliação, sem gate)", "",
          "`gemma2:9b` local, temperatura 0,7, sementes de diagnóstico 7000+ (adolescente) e 7100+ (adulto), as 8 mensagens de",
          "`artifacts_conversa_pet/diagnostico/conversa_estagios.py`, o mesmo estado à mão, histórico do próprio ensaio.", ""]
    for estagio, d in out.items():
        md += [f"## {estagio}", "", "| jogador | livre-v2 | conversa-v1 |", "|---|---|---|"]
        for a, b in zip(d[VERSAO_PROMPT], d[VERSAO_CONVERSA_V1]):
            fmt = lambda x: (x["pet"] + (f" `{','.join(x['fatos'])}`" if x["fatos"] else "") + (f" **erro: {x['erro']}**" if x["erro"] else "")).replace("|", "/")
            md.append(f"| {a['jogador']} | {fmt(a)} | {fmt(b)} |")
        for v in (VERSAO_PROMPT, VERSAO_CONVERSA_V1):
            n = [len(x["pet"]) for x in d[v]]
            md.append(f"\n{v}: tamanho médio da fala {sum(n) / len(n):.0f} caracteres (min {min(n)}, max {max(n)}); "
                      f"{sum('?' in x['pet'] for x in d[v])} de {len(n)} com pergunta.")
        md.append("")
    (destino / "ensaio.md").write_text("\n".join(md), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
