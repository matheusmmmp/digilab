"""As entradas da DC5 (CONVERSA_PET; docs/PLANO_ANALISE_V3_CONVERSA_DC5.md, secao 5, APROVADO pelo Matheus em 2026-11-10).

O pet, o cenario, o dono e o sorteio sao os da DC4 (`entradas_dc4`, que nao muda): o LAB+F da DC3 com o dono que atende, o E3 (as falas do
`dec-v3` por pedido), o E2 (as decisoes que nao sao fala, com as lembrancas com episodio) e as janelas R da conversa. O que muda:
- **as sementes** sao da faixa da DC5 (secao 7, D-DC5-1), com o rotulo `conversa_dc5` em todo `derivar_semente`: nenhuma entrada da DC4 se
  repete;
- **o conjunto ES** (secao 5, D-DC5-11): `n_sequencias_es` janelas de `falas_por_sequencia_es` decisoes seguidas da mesma vida, no mesmo
  estagio, sem sobreposicao entre elas, de qualquer formato. Cada janela vira uma sequencia de falas espontaneas: a voz-v4 recebe as falas
  anteriores da janela (3.4), e a voz do jogo nao.

Se faltar decisao num estrato, o sorteio falha alto e roda mais vidas da mesma base, como na DC4.
"""
from __future__ import annotations

import random
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import entradas_dc4 as en4  # noqa: E402

from digilab.config import CONFIG_VOZ_V4, CONTEUDOS_FALA  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402

PREFIXO = "conversa_dc5"                 # o rotulo de todo `derivar_semente` da DC5 (secao 7)
DONOS = en4.DONOS
TURNOS = en4.TURNOS
FaltaDecisao = en4.FaltaDecisao


def semente_da_vida(base: int, i: int) -> int:
    return derivar_semente(PREFIXO, base, "vida", i)


def rng_do_fluxo(base: int, fluxo: str) -> random.Random:
    return random.Random(derivar_semente(PREFIXO, base, fluxo))


def viver(base: int, i: int, dias: int, orcamento_por_dia: int) -> dict:
    return en4.viver_semente(i, semente_da_vida(base, i), DONOS[i % len(DONOS)], dias, orcamento_por_dia)


def _sequencias_es(vidas: list[dict], n: int, tamanho: int, rng: random.Random) -> list[tuple[int, int]]:
    """n janelas (vida, k0) de `tamanho` decisoes seguidas no mesmo estagio, sem sobreposicao (o ES, secao 5)"""
    cands = [(v["i"], k0) for v in vidas for k0 in range(len(v["decisoes"]) - tamanho + 1)
             if len({d["estagio"] for d in v["decisoes"][k0:k0 + tamanho]}) == 1]
    out = []
    for i, k0 in rng.sample(cands, len(cands)):
        if all(i != i2 or abs(k0 - k2) >= tamanho for i2, k2 in out):
            out.append((i, k0))
            if len(out) == n:
                return out
    raise FaltaDecisao(f"ES: {len(out)} sequencias, o plano pede {n}")


def sortear(vidas: list[dict], base: int, n_e3_por_pedido: int, n_e2: int, min_ep_e2: int, n_sequencias: int, n_es: int,
            tamanho_es: int) -> dict:
    return {"E3": en4._e3(vidas, n_e3_por_pedido, rng_do_fluxo(base, "sorteio_e3")),
            "E2": en4._e2(vidas, n_e2, min_ep_e2, rng_do_fluxo(base, "sorteio_e2")),
            "R": en4._sequencias(vidas, n_sequencias, rng_do_fluxo(base, "sorteio_r")),
            "ES": _sequencias_es(vidas, n_es, tamanho_es, rng_do_fluxo(base, "sorteio_es"))}


def exportar(base: int, dias: int, orcamento_por_dia: int, n_e3_por_pedido: int, n_e2: int, min_ep_e2: int, n_sequencias: int, n_es: int,
             tamanho_es: int = CONFIG_VOZ_V4.falas_por_sequencia_es, viver_vida=viver) -> dict:
    """as vidas em ordem ate o sorteio fechar (como a DC4) e as entradas: E3, E2, as sequencias da conversa e as do ES"""
    vidas, faltas = [viver_vida(base, i, dias, orcamento_por_dia) for i in range(en4.N_VIDAS_INICIAL)], []
    while True:
        try:
            s = sortear(vidas, base, n_e3_por_pedido, n_e2, min_ep_e2, n_sequencias, n_es, tamanho_es)
            break
        except FaltaDecisao as err:
            faltas.append({"vidas": len(vidas), "falta": str(err)})
            if len(vidas) >= en4.MAX_VIDAS:
                raise FaltaDecisao(f"{err} (com {len(vidas)} vidas, o maximo e {en4.MAX_VIDAS})") from err
            vidas.append(viver_vida(base, len(vidas), dias, orcamento_por_dia))
    por = {v["i"]: v for v in vidas}
    pega = lambda r: (por[r[0]], por[r[0]]["decisoes"][r[1]])   # noqa: E731
    e3 = [en4._entrada(f"E3-{n:03d}", "E3", *pega(r)) for n, r in enumerate(s["E3"])]
    e2 = [en4._entrada(f"E2-{n:03d}", "E2", *pega(r)) for n, r in enumerate(s["E2"])]
    seqs = [{"id": f"Q{n}", "vida": i, "k0": k0,
             "entradas": [en4._entrada(f"Q{n}-t{t}", "R", por[i], por[i]["decisoes"][k0 + t]) for t in range(TURNOS)]}
            for n, (i, k0) in enumerate(s["R"])]
    es = [{"id": f"S{n}", "vida": i, "k0": k0,
           "entradas": [en4._entrada(f"S{n}-f{t}", "ES", por[i], por[i]["decisoes"][k0 + t]) for t in range(tamanho_es)]}
          for n, (i, k0) in enumerate(s["ES"])]
    if min_ep_e2 and sum(en4.lembranca_com_episodio(e["conceitos"]) for e in e2) < min_ep_e2:
        raise RuntimeError("o E2 sem as lembrancas com episodio que o plano pede")
    return {"base": base, "prefixo": PREFIXO, "braco_pet": en4.BRACO_PET, "modo_dono": en4.MODO_DONO, "lugar": en4.dc3.LUGAR, "dias": dias,
            "orcamento_por_dia": orcamento_por_dia, "n_vidas": len(vidas), "vidas_a_mais": faltas,
            "vidas": [{k: v[k] for k in ("i", "dono", "semente", "dias", "atendimentos", "log_sha256")}
                      | {"decisoes": len(v["decisoes"]), "falas": {p: sum(d["conteudo"] == p for d in v["decisoes"]) for p in CONTEUDOS_FALA}}
                      for v in vidas],
            "E3": e3, "E2": e2, "sequencias": seqs, "sequencias_es": es}
