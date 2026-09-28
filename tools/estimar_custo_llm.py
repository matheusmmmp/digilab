"""Estimativa de custo e capacidade da LLM no modo livre gravado, por usuarios simultaneos.

    python tools/estimar_custo_llm.py            # grava artifacts_custo_llm/estimativa.json e tabela.md

Fontes de cada numero:
  - precos por milhao de tokens: servidor/fala_llm.PRECOS_USD_POR_MTOK (tabela do repo; conferir na pagina
    de precos da Anthropic antes de orcar)
  - latencia de modelo local: artifacts_fala/.../falas.jsonl e artifacts_fala_livre/rodada2/tempos_*.json
    (medidas na maquina do Matheus, uma chamada por vez, sem lote)
  - tamanho do pedido: artifacts_fala_livre/rodada2 (caracteres dos fatos) + prompt de sistema; tokens
    estimados por cima (1 token a cada 3 caracteres em portugues) -> PROPOSTO, sem fonte
  - chamadas por hora de jogo ativo: PROPOSTO, sem fonte (tres cenarios)
"""
from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from servidor.fala_llm import MAX_TOKENS_SAIDA, PRECOS_USD_POR_MTOK  # noqa: E402

SAIDA = RAIZ / "artifacts_custo_llm"
HORAS_MES = 730                       # 24 * 365 / 12
USUARIOS = [1, 10, 100, 1_000, 10_000, 100_000]

# PROPOSTO, sem fonte: chamadas a LLM por hora de jogo ativo
CENARIOS = {
    "enxuto": {"chamadas_h": 4, "nota": "so travessuras/chamados decididos pela LLM (~2-3/h no cronograma) + 1 fala"},
    "tipico": {"chamadas_h": 10, "nota": "travessuras + reacoes ao dono + algumas falas na conversa"},
    "intenso": {"chamadas_h": 30, "nota": "LLM decide a cada acao do dono e conversa muito"},
}
# pesquisa: vidas simuladas como na confirmatoria (160 ovos x 5 bracos x 14 dias)
VIDAS_CONFIRMATORIA = 160 * 5
DIAS_VIDA = 14
PASSOS_DIA = 96                       # dono decide a cada 15 min (ConfigDonos)
EVENTOS_DIA = 10                      # PROPOSTO, sem fonte: travessuras/decisoes da LLM por dia simulado


def tokens_pedido() -> tuple[int, int]:
    falas = RAIZ / "artifacts_fala_livre" / "rodada2" / "falas_qwen2.5-3b.jsonl"
    linhas = [json.loads(x) for x in falas.read_text(encoding="utf-8").splitlines() if x.strip()]
    if not linhas:
        raise ValueError("sem falas medidas")
    chars_fatos = max(sum(len(f["texto"]) for f in x["fatos"]) for x in linhas)   # pior caso medido
    chars_sistema = 2000              # PROPOSTO: prompt de sistema + esquema, por cima
    entrada = -(-(chars_fatos + chars_sistema) // 3)
    return entrada, MAX_TOKENS_SAIDA  # saida pelo teto do servidor (pior caso)


def latencias_locais() -> dict:
    out = {}
    base = RAIZ / "artifacts_fala_livre" / "rodada2"
    for arq in sorted(base.glob("tempos_*.json")):
        d = json.loads(arq.read_text(encoding="utf-8"))["latencias_s"]
        todas = [x for v in d.values() for x in v]
        out[arq.stem.removeprefix("tempos_")] = {"n": len(todas), "p50_s": statistics.median(todas)}
    if not out:
        raise ValueError("sem latencias medidas")
    return out


def main() -> int:
    ent, sai = tokens_pedido()
    custo_chamada = {m: (ent * pi + sai * po) / 1e6 for m, (pi, po) in PRECOS_USD_POR_MTOK.items()}
    lat = latencias_locais()
    api = {}
    for c, cfg in CENARIOS.items():
        api[c] = {m: {str(n): round(n * HORAS_MES * cfg["chamadas_h"] * custo_chamada[m], 2) for n in USUARIOS}
                  for m in custo_chamada}
    # uma GPU local, chamadas em fila (sem lote): usuarios simultaneos que ela aguenta
    capacidade = {mod: {c: int(3600 / v["p50_s"] / cfg["chamadas_h"]) for c, cfg in CENARIOS.items()}
                  for mod, v in lat.items()}
    pesquisa = {}
    for nome, chamadas_vida in (("llm_a_cada_passo", DIAS_VIDA * PASSOS_DIA), ("llm_so_em_eventos", DIAS_VIDA * EVENTOS_DIA)):
        total = VIDAS_CONFIRMATORIA * chamadas_vida
        pesquisa[nome] = {"chamadas": total,
                          "usd": {m: round(total * custo_chamada[m], 2) for m in custo_chamada},
                          "horas_gpu_local": {mod: round(total * v["p50_s"] / 3600, 1) for mod, v in lat.items()}}
    res = {"tokens_por_chamada": {"entrada": ent, "saida": sai},
           "usd_por_chamada": {m: round(v, 6) for m, v in custo_chamada.items()},
           "cenarios": CENARIOS, "custo_api_usd_mes_por_usuarios_simultaneos": api,
           "latencia_local_medida": lat, "capacidade_uma_gpu_usuarios_simultaneos": capacidade,
           "pesquisa_vidas_da_confirmatoria": pesquisa,
           "premissas": {"horas_mes": HORAS_MES, "usuarios_simultaneos": "media 24h; custo escala com horas-usuario"}}
    SAIDA.mkdir(exist_ok=True)
    (SAIDA / "estimativa.json").write_text(json.dumps(res, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    ln = [f"tokens/chamada: {ent} entrada, {sai} saida (pior caso)", "",
          "| cenario | modelo | " + " | ".join(f"{n:,}" for n in USUARIOS) + " |",
          "|---|---|" + "---:|" * len(USUARIOS)]
    for c in api:
        for m in api[c]:
            ln.append(f"| {c} | {m} | " + " | ".join(f"{api[c][m][str(n)]:,.0f}" for n in USUARIOS) + " |")
    (SAIDA / "tabela.md").write_text("\n".join(ln) + "\n", encoding="utf-8")
    print(json.dumps({k: res[k] for k in ("tokens_por_chamada", "usd_por_chamada", "latencia_local_medida",
                                          "capacidade_uma_gpu_usuarios_simultaneos", "pesquisa_vidas_da_confirmatoria")},
                     indent=1))
    print("\n".join(ln))
    return 0


if __name__ == "__main__":
    sys.exit(main())
