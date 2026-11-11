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

from servidor.fala_llm import LIMITE_USD_LIVRE_PADRAO, MAX_TOKENS_SAIDA, PRECOS_USD_POR_MTOK  # noqa: E402

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


# CONVERSA_PET M5 (PLANO_ANALISE_V3_CONVERSA_PET, secoes 2 e 7): a comparacao cega gemma2:9b x haiku-5-5 x sonnet-5-5 da fala livre.
# 12 roteiros x 8 turnos x (calibracao + validacao) = 192 turnos por braco, 384 nos dois; ~2 600 tokens de entrada e ~100 de saida
# por turno (estimativa do plano, PROPOSTA, sem medida ainda). Teto separado PROPOSTO: US$ 3 (servidor/fala_llm.LIMITE_USD_LIVRE_PADRAO).
TURNOS_LIVRE_POR_BRACO = 12 * 8 * 2
TOKENS_TURNO_LIVRE = (2600, 100)
MODELOS_LIVRE = ("claude-haiku-5-5", "claude-sonnet-5-5")


# CONVERSA_PET DC4a (docs/PLANO_ANALISE_V3_CONVERSA_DC4.md, secao 8, DC4-5 e DC4-6): a voz da rede com o Haiku 5.5 e o Sonnet 5.5. 81 chamadas da voz por
# braco na calibracao (30 + 15 espontaneas e 36 turnos) e 162 na validacao (60 + 30 e 72), 243 no total; o verificador e local. O pedido e o maior que a
# DC4 pode mandar, medido pelo `prompt.mensagens_voz` de hoje (pedido_dc4_pior_caso); a saida, os ~100 tokens do plano (PROPOSTO, sem medida).
CHAMADAS_DC4_POR_BRACO = {"calibracao": 30 + 15 + 2 * 3 * 6, "validacao": 60 + 30 + 4 * 3 * 6}
SAIDA_DC4 = 100


def pedido_dc4_pior_caso() -> dict:
    """os caracteres do maior pedido da voz na DC4: o dec-v3 com os 12 conceitos ativos (metade com confianca baixa, a lembranca com episodio),
    o adulto, a conversa com o comando e 5 trocas antes (o 6.o turno do roteiro), cada fala do dono com 300 caracteres e cada do pet com 320,
    sem o estilo da especie (o pet do Python nao tem forma). Os tokens por cima: 1 a cada 3 caracteres (a regra deste arquivo) e a reserva do
    `ClienteClaude.custo_maximo` (1 a cada 2, mais 400)."""
    from digilab_fala_livre import conceitos as dec
    from digilab_fala_livre.prompt import mensagens_voz
    cs = [{"nome": n, "valor": 900, "confianca": 300 if i % 2 else 900} for i, n in enumerate(dec.NOMES) if n != "lembranca"]
    cs.append({"nome": "lembranca", "valor": 900, "confianca": 900, "alvo": "ep123456",
               "episodio": {"acao": "chamar_atencao", "classe": "nao_havia", "desfecho": "neutro"}})
    c = dec.validar({"versao": "dec-v3", "k": 99999, "intencao": "solidao", "conceitos": cs})
    hist = [("d" * 300, "p" * 320, "adulto")] * 5
    msgs = mensagens_voz(c, "adulto", "conversa", "j" * 300, hist, estilo=None, comando=True)
    chars = sum(len(m["content"]) for m in msgs)
    return {"caracteres": chars, "tokens_por_3_chars": -(-chars // 3), "tokens_reserva_claude": -(-(chars + 400) // 2)}


def custo_dc4() -> dict:
    ped = pedido_dc4_pior_caso()
    total = sum(CHAMADAS_DC4_POR_BRACO.values())
    usd = {m: round(total * (ped["tokens_por_3_chars"] * PRECOS_USD_POR_MTOK[m][0] + SAIDA_DC4 * PRECOS_USD_POR_MTOK[m][1]) / 1e6, 4)
           for m in MODELOS_LIVRE}
    return {"chamadas_por_braco": {**CHAMADAS_DC4_POR_BRACO, "total": total}, "pedido_pior_caso": ped, "tokens_saida": SAIDA_DC4,
            "usd_por_braco": usd, "usd_total_dois_bracos": round(sum(usd.values()), 4), "teto_usd": LIMITE_USD_LIVRE_PADRAO,
            "status": "PROPOSTO: o pedido medido pelo prompt de hoje no pior caso; a saida do plano, sem medida (a DC4b mede pelo usage)"}


CALIBRACAO_DC4 = RAIZ / "artifacts_v3_conversa_dc4" / "calibracao"
CALIBRACAO_DC4_V3B = RAIZ / "artifacts_v3_conversa_dc4" / "calibracao_v3b"


def custo_dc4_medido() -> dict | None:
    """DC4b: o custo pelo `usage` real da calibracao (falas.jsonl e meta.json) e a projecao da validacao (162 chamadas por braco), pela media
    por chamada e pela chamada mais cara de cada braco, contra o teto e o gasto ja acumulado. None sem a calibracao no disco."""
    if not (CALIBRACAO_DC4 / "meta.json").exists():
        return None
    meta = json.loads((CALIBRACAO_DC4 / "meta.json").read_text(encoding="utf-8"))
    regs = _falas(CALIBRACAO_DC4)
    return _projecao(regs, meta["gasto"]["fim_usd"], meta["gasto"]["limite_usd"],
                     "artifacts_v3_conversa_dc4/calibracao/falas.jsonl (usage) e meta.json (gasto acumulado)")


def _falas(pasta: Path) -> list[dict]:
    return [json.loads(x) for x in (pasta / "falas.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]


def custo_dc4_medido_v3b() -> dict | None:
    """DC4b, a voz-v3b (decisao do Matheus em 2026-11-09): a mesma projecao, com as falas do dec-v3 da recalibracao (calibracao_v3b) no lugar
    das da calibracao (as do dec-v2 nao mudam, a voz-v2 e a mesma) e o gasto acumulado do fim da recalibracao. None sem ela no disco."""
    if not (CALIBRACAO_DC4_V3B / "meta.json").exists():
        return None
    meta = json.loads((CALIBRACAO_DC4_V3B / "meta.json").read_text(encoding="utf-8"))
    novas = {r["id"]: r for r in _falas(CALIBRACAO_DC4_V3B)}
    regs = [novas.pop(r["id"]) if r["versao_dec"] == "dec-v3" else r for r in _falas(CALIBRACAO_DC4)]
    if novas or any(r["versao_dec"] == "dec-v3" and r.get("versao_prompt") != "voz-v3b" for r in regs):
        raise ValueError("a recalibracao da voz-v3b nao cobre exatamente as falas do dec-v3 da calibracao")
    return _projecao(regs, meta["gasto"]["fim_usd"], meta["gasto"]["limite_usd"],
                     "artifacts_v3_conversa_dc4/calibracao_v3b/falas.jsonl (usage do dec-v3, voz-v3b), calibracao/falas.jsonl (usage do "
                     "dec-v2) e calibracao_v3b/meta.json (gasto acumulado)")


def _projecao(regs: list[dict], acumulado: float, limite: float, fonte: str) -> dict:
    bracos, proj_media, proj_max = {}, 0.0, 0.0
    for b, m in (("H", "claude-haiku-5-5"), ("S", "claude-sonnet-5-5")):
        us = [r["usage"] for r in regs if r["braco"] == b and r["usage"]["entrada"] is not None]
        if not us:
            raise ValueError(f"a calibracao sem usage no braco {b}")
        cs = [(u["entrada"] * PRECOS_USD_POR_MTOK[m][0] + u["saida"] * PRECOS_USD_POR_MTOK[m][1]) / 1e6 for u in us]
        n_val = CHAMADAS_DC4_POR_BRACO["validacao"]
        bracos[b] = {"modelo": m, "chamadas_com_usage": len(us), "chamadas": sum(r["braco"] == b for r in regs),
                     "entrada_media": round(statistics.mean(u["entrada"] for u in us), 1), "entrada_max": max(u["entrada"] for u in us),
                     "saida_media": round(statistics.mean(u["saida"] for u in us), 1), "saida_max": max(u["saida"] for u in us),
                     "usd_calibracao": round(sum(cs), 6), "usd_validacao_pela_media": round(n_val * statistics.mean(cs), 4),
                     "usd_validacao_pela_maior": round(n_val * max(cs), 4)}
        proj_media += n_val * statistics.mean(cs)
        proj_max += n_val * max(cs)
    return {"bracos": bracos, "gasto_acumulado_usd": acumulado, "teto_usd": limite,
            "validacao_pela_media_usd": round(proj_media, 4), "validacao_pela_maior_usd": round(proj_max, 4),
            "folga_pela_media_usd": round(limite - acumulado - proj_media, 4),
            "folga_pela_maior_usd": round(limite - acumulado - proj_max, 4),
            "fonte": fonte}


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
    ent_l, sai_l = TOKENS_TURNO_LIVRE
    livre = {"turnos_por_braco": TURNOS_LIVRE_POR_BRACO, "tokens_por_turno": {"entrada": ent_l, "saida": sai_l},
             "usd_por_braco": {m: round(TURNOS_LIVRE_POR_BRACO * (ent_l * PRECOS_USD_POR_MTOK[m][0]
                                                                  + sai_l * PRECOS_USD_POR_MTOK[m][1]) / 1e6, 4)
                               for m in MODELOS_LIVRE},
             "teto_usd_proposto": LIMITE_USD_LIVRE_PADRAO, "status": "PROPOSTO, sem medida: tokens do plano, secao 7"}
    livre["usd_total_dois_bracos"] = round(sum(livre["usd_por_braco"].values()), 4)
    res = {"fala_livre_comparacao_d5": livre, "voz_da_rede_dc4": custo_dc4(), "tokens_por_chamada": {"entrada": ent, "saida": sai},
           "usd_por_chamada": {m: round(v, 6) for m, v in custo_chamada.items()},
           "cenarios": CENARIOS, "custo_api_usd_mes_por_usuarios_simultaneos": api,
           "latencia_local_medida": lat, "capacidade_uma_gpu_usuarios_simultaneos": capacidade,
           "pesquisa_vidas_da_confirmatoria": pesquisa,
           "premissas": {"horas_mes": HORAS_MES, "usuarios_simultaneos": "media 24h; custo escala com horas-usuario"}}
    medido = custo_dc4_medido()                     # DC4b: num artefato proprio da calibracao (posterior ao plano da DC4), fora da estimativa
    if medido is not None:
        (CALIBRACAO_DC4 / "custo_medido.json").write_text(json.dumps(medido, indent=2, ensure_ascii=False) + chr(10), encoding="utf-8")
        print(json.dumps({"voz_da_rede_dc4_medido": medido}, indent=1))
    medido_v3b = custo_dc4_medido_v3b()             # DC4b, a voz-v3b: num artefato da recalibracao; o da calibracao nao muda
    if medido_v3b is not None:
        (CALIBRACAO_DC4_V3B / "custo_medido.json").write_text(json.dumps(medido_v3b, indent=2, ensure_ascii=False) + chr(10), encoding="utf-8")
        print(json.dumps({"voz_da_rede_dc4_medido_v3b": medido_v3b}, indent=1))
    SAIDA.mkdir(exist_ok=True)
    (SAIDA / "estimativa.json").write_text(json.dumps(res, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    ln = [f"tokens/chamada: {ent} entrada, {sai} saida (pior caso)", "",
          "| cenario | modelo | " + " | ".join(f"{n:,}" for n in USUARIOS) + " |",
          "|---|---|" + "---:|" * len(USUARIOS)]
    for c in api:
        for m in api[c]:
            ln.append(f"| {c} | {m} | " + " | ".join(f"{api[c][m][str(n)]:,.0f}" for n in USUARIOS) + " |")
    (SAIDA / "tabela.md").write_text("\n".join(ln) + "\n", encoding="utf-8")
    print(json.dumps({k: res[k] for k in ("fala_livre_comparacao_d5", "voz_da_rede_dc4", "tokens_por_chamada", "usd_por_chamada", "latencia_local_medida",
                                          "capacidade_uma_gpu_usuarios_simultaneos", "pesquisa_vidas_da_confirmatoria")},
                     indent=1))
    print("\n".join(ln))
    return 0


if __name__ == "__main__":
    sys.exit(main())
