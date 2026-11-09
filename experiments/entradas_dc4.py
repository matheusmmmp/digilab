"""As entradas da DC4 (CONVERSA_PET; docs/PLANO_ANALISE_V3_CONVERSA_DC4.md, secao 3): vidas do pet de teste no Python e o sorteio estratificado.

**O pet** e o LAB+F da DC3 (`run_v3_conversa_dc3.config_do_braco("LAB+F")`, a `fala_unidades` ligada) no cenario da DC3 (o comedouro, 14 dias,
orcamento 16), com o dono que atende (`DonoQueAtende`, o modo `atende`). A vida e a do `run_v3_conversa_dc3.viver`, sem mudar nada; aqui so se
le, por decisao: o motivo, o episodio recuperado (copiado da memoria na hora da lembranca, o gancho de leitura do
`exportar_decodificador._capturando`), o tick da decisao e o estagio do pet nesse tick (`treino_stats.estagio_no_tick`, o estagio de hoje do pet
de pesquisa). Os conceitos sao o `decodificar_v2` de cada decisao, e o pedido da voz e o que a pagina monta (`montador_voz_rede`, o espelho do
`falaRede.ts`), validado pelo `conceitos.validar` do servidor (falha alto).

**As sementes** (secao 7, DC4-1): da base da fase (20262200 na calibracao, 20262500 na validacao; 101 a 505 so na fumaca), cada fluxo com a sua,
por `derivar_semente`: a vida i tem a semente `derivar_semente(PREFIXO, base, "vida", i)` e o dono `DONOS[i % 4]` (os 4 donos sem ensino, em
rodizio); o sorteio do E3, o do E2 e o das sequencias da conversa tem cada um a sua rng.

**O sorteio** (secao 3):
- E3: as decisoes de fala (o `dec-v3`), `n_e3_por_pedido` por pedido (fome, higiene, solidao), sorteadas sem reposicao;
- E2: as decisoes que nao sao fala (o `dec-v2`), `n_e2` no total, estratificadas pela intencao da I-a (rodizio pela ordem do catalogo), com
  pelo menos `min_ep_e2` lembrancas com `episodio` ativas (a `lembranca` com `episodio` e valor >= o limiar, que a voz ve), sorteadas primeiro;
- R: `n_sequencias` janelas de 6 decisoes seguidas da mesma vida, no mesmo estagio, com pelo menos uma fala e uma decisao que nao e fala, sem
  sobreposicao. Cada conversa da fase e um roteiro com uma sequencia: o turno t leva a entrada da decisao t da janela.

Se faltar decisao num estrato, o sorteio **falha alto** e roda mais vidas da mesma base, na ordem (i = N_VIDAS_INICIAL, N_VIDAS_INICIAL + 1, ...),
ate completar, sem trocar o estrato; passando de MAX_VIDAS, levanta. As vidas a mais ficam no `entradas.json`.
"""
from __future__ import annotations

import random
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import exportar_decodificador as ed  # noqa: E402
import montador_voz_rede as mv  # noqa: E402
import run_v3_conversa_dc3 as dc3  # noqa: E402

from digilab.config import CONFIG_DECODIFICADOR, CONTEUDOS_FALA  # noqa: E402
from digilab.digibrain.decodificador import CATALOGO, decodificar_v2  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402
from digilab.treino_stats import estagio_no_tick  # noqa: E402
from digilab_fala_livre import conceitos as dec  # noqa: E402

PREFIXO = "conversa_dc4"                 # o rotulo de todo `derivar_semente` da DC4 (secao 7)
DONOS = dc3.DONOS                        # os 4 donos sem ensino, em rodizio pelas vidas (D-CP-DC4a, no registro)
BRACO_PET = dc3.TRATADO                  # o LAB+F
MODO_DONO = dc3.ATENDE                   # o dono que atende
TURNOS = 6                               # secao 3: o roteiro tem 6 mensagens do dono
N_VIDAS_INICIAL = 4                      # PROPOSTO, SEM FONTE: uma vida por dono antes de olhar se o sorteio fecha
MAX_VIDAS = 40                           # PROPOSTO, SEM FONTE: a parada da busca por mais vidas (falha alto)
FALA = dc3.FALA


class FaltaDecisao(RuntimeError):
    """Um estrato sem decisoes bastantes nas vidas que existem: o chamador roda mais uma vida da mesma base."""


def semente_da_vida(base: int, i: int) -> int:
    return derivar_semente(PREFIXO, base, "vida", i)


def rng_do_fluxo(base: int, fluxo: str) -> random.Random:
    """a rng de um fluxo do sorteio (secao 7: cada fluxo com a sua)"""
    return random.Random(derivar_semente(PREFIXO, base, fluxo))


def viver(base: int, i: int, dias: int, orcamento_por_dia: int) -> dict:
    """a vida i da base (a semente derivada e o dono do rodizio)"""
    return viver_semente(i, semente_da_vida(base, i), DONOS[i % len(DONOS)], dias, orcamento_por_dia)


def viver_semente(i: int, semente: int, dono: str, dias: int, orcamento_por_dia: int) -> dict:
    """uma vida do LAB+F com o dono que atende: as decisoes com o `dec-v2`, o conteudo da fala, o tick, o estagio e o pedido da voz montado"""
    with ed._capturando() as episodios:
        motor, registro, _, atende, leituras = dc3.viver(BRACO_PET, MODO_DONO, dono, semente, dias, orcamento_por_dia)
    c = dc3.orq.cerebro_de(registro)
    ms, ticks = c.motivos, leituras["tick_decisao"]
    if not (len(ms) == len(ticks) == len(episodios)):
        raise RuntimeError(f"vida {i}: {len(ms)} decisoes, {len(ticks)} ticks e {len(episodios)} lembrancas")
    dc3.conferir_fala(BRACO_PET, c)
    decisoes = []
    for k, (m, ep, tick) in enumerate(zip(ms, episodios, ticks)):
        d2 = decodificar_v2(m, ep)
        conteudo = m["escolha"][1] if m["acao"] == FALA else None
        pedido = mv.conceitos_da_voz(d2, conteudo)
        dec.validar(pedido)                           # o que o servidor faria: fora do formato, falha alto (400 no jogo)
        decisoes.append({"k": k, "tick": tick, "estagio": estagio_no_tick(tick), "acao": m["acao"], "conteudo": conteudo,
                         "intencao_ia": d2["intencao"], "dec_v2": d2, "conceitos": pedido})
    return {"i": i, "dono": dono, "semente": semente, "dias": dias, "decisoes": decisoes,
            "atendimentos": len(atende.atendimentos) if atende is not None else None,
            "log_sha256": __import__("hashlib").sha256(motor.log.para_jsonl().encode("utf-8")).hexdigest()}


def lembranca_com_episodio(conceitos: dict) -> bool:
    """a `lembranca` com `episodio` e valor >= o limiar (a voz a ve, secao 3)"""
    return any(c["nome"] == "lembranca" and "episodio" in c and c["valor"] >= CONFIG_DECODIFICADOR.limiar_valor
               for c in conceitos["conceitos"])


def _todas(vidas: list[dict]):
    for v in vidas:
        for d in v["decisoes"]:
            yield v, d


def _ref(v: dict, d: dict) -> tuple[int, int]:
    return v["i"], d["k"]


def _e3(vidas: list[dict], n: int, rng: random.Random) -> list[tuple[int, int]]:
    out = []
    for p in CONTEUDOS_FALA:
        cands = [_ref(v, d) for v, d in _todas(vidas) if d["conteudo"] == p]
        if len(cands) < n:
            raise FaltaDecisao(f"E3/{p}: {len(cands)} decisoes de fala, o plano pede {n}")
        out += rng.sample(cands, n)
    return out


def _rodizio(por_estrato: dict[str, list], n: int, rng: random.Random, rotulo: str) -> list:
    """n itens em rodizio pelos estratos (a ordem do catalogo), cada estrato embaralhado pela rng; falha alto sem itens bastantes"""
    listas = {e: rng.sample(por_estrato[e], len(por_estrato[e])) for e in CATALOGO if por_estrato.get(e)}
    if set(por_estrato) - set(CATALOGO):
        raise ValueError(f"{rotulo}: estrato fora do catalogo: {sorted(set(por_estrato) - set(CATALOGO))}")
    out = []
    while len(out) < n:
        andou = False
        for e in listas:
            if listas[e] and len(out) < n:
                out.append(listas[e].pop(0))
                andou = True
        if not andou:
            raise FaltaDecisao(f"{rotulo}: {len(out)} decisoes, o plano pede {n}")
    return out


def _e2(vidas: list[dict], n: int, min_ep: int, rng: random.Random) -> list[tuple[int, int]]:
    """primeiro as `min_ep` lembrancas com episodio, depois o resto do total, as duas em rodizio pela intencao da I-a"""
    def estratos(filtro) -> dict:
        out: dict = {}
        for v, d in _todas(vidas):
            if d["conteudo"] is None and filtro(d):
                out.setdefault(d["intencao_ia"], []).append(_ref(v, d))
        return out
    com_ep = _rodizio(estratos(lambda d: lembranca_com_episodio(d["conceitos"])), min_ep, rng, "E2/lembranca com episodio")
    ja = set(com_ep)
    resto = {e: [r for r in rs if r not in ja] for e, rs in estratos(lambda d: True).items()}
    return com_ep + _rodizio(resto, n - min_ep, rng, "E2")


def _sequencias(vidas: list[dict], n: int, rng: random.Random) -> list[tuple[int, int]]:
    """n janelas (vida, k0) de TURNOS decisoes seguidas no mesmo estagio, com fala e nao fala, sem sobreposicao"""
    cands = []
    for v in vidas:
        ds = v["decisoes"]
        for k0 in range(len(ds) - TURNOS + 1):
            j = ds[k0:k0 + TURNOS]
            falas = sum(d["conteudo"] is not None for d in j)
            if len({d["estagio"] for d in j}) == 1 and 0 < falas < TURNOS:
                cands.append((v["i"], k0))
    out = []
    for i, k0 in rng.sample(cands, len(cands)):
        if all(i != i2 or abs(k0 - k2) >= TURNOS for i2, k2 in out):
            out.append((i, k0))
            if len(out) == n:
                return out
    raise FaltaDecisao(f"R: {len(out)} sequencias, o plano pede {n}")


def sortear(vidas: list[dict], base: int, n_e3_por_pedido: int, n_e2: int, min_ep_e2: int, n_sequencias: int) -> dict:
    """{E3, E2, R}: as referencias (vida, k) sorteadas; FaltaDecisao se um estrato nao fecha"""
    return {"E3": _e3(vidas, n_e3_por_pedido, rng_do_fluxo(base, "sorteio_e3")),
            "E2": _e2(vidas, n_e2, min_ep_e2, rng_do_fluxo(base, "sorteio_e2")),
            "R": _sequencias(vidas, n_sequencias, rng_do_fluxo(base, "sorteio_r"))}


def _entrada(eid: str, conjunto: str, v: dict, d: dict) -> dict:
    return {"id": eid, "conjunto": conjunto, "vida": v["i"], "dono": v["dono"], "semente_vida": v["semente"], "k": d["k"], "tick": d["tick"],
            "estagio": d["estagio"], "pedido_rede": d["conteudo"], "intencao_ia": d["intencao_ia"],
            "conceitos": d["conceitos"], "estado": mv.estado_da_voz(d["estagio"])}


def exportar(base: int, dias: int, orcamento_por_dia: int, n_e3_por_pedido: int, n_e2: int, min_ep_e2: int, n_sequencias: int,
             viver_vida=viver) -> dict:
    """as vidas em ordem ate o sorteio fechar (N_VIDAS_INICIAL primeiro; depois uma a uma, falhando alto alem de MAX_VIDAS) e as entradas.
    `viver_vida` e injetavel so para o teste da busca por mais vidas."""
    vidas, faltas = [viver_vida(base, i, dias, orcamento_por_dia) for i in range(N_VIDAS_INICIAL)], []
    while True:
        try:
            s = sortear(vidas, base, n_e3_por_pedido, n_e2, min_ep_e2, n_sequencias)
            break
        except FaltaDecisao as err:
            faltas.append({"vidas": len(vidas), "falta": str(err)})
            if len(vidas) >= MAX_VIDAS:
                raise FaltaDecisao(f"{err} (com {len(vidas)} vidas, o maximo e {MAX_VIDAS})") from err
            vidas.append(viver_vida(base, len(vidas), dias, orcamento_por_dia))
    por = {v["i"]: v for v in vidas}
    pega = lambda r: (por[r[0]], por[r[0]]["decisoes"][r[1]])   # noqa: E731
    e3 = [_entrada(f"E3-{n:03d}", "E3", *pega(r)) for n, r in enumerate(s["E3"])]
    e2 = [_entrada(f"E2-{n:03d}", "E2", *pega(r)) for n, r in enumerate(s["E2"])]
    seqs = [{"id": f"Q{n}", "vida": i, "k0": k0,
             "entradas": [_entrada(f"Q{n}-t{t}", "R", por[i], por[i]["decisoes"][k0 + t]) for t in range(TURNOS)]}
            for n, (i, k0) in enumerate(s["R"])]
    if min_ep_e2 and sum(lembranca_com_episodio(e["conceitos"]) for e in e2) < min_ep_e2:
        raise RuntimeError("o E2 sem as lembrancas com episodio que o plano pede")
    return {"base": base, "prefixo": PREFIXO, "braco_pet": BRACO_PET, "modo_dono": MODO_DONO, "lugar": dc3.LUGAR, "dias": dias,
            "orcamento_por_dia": orcamento_por_dia, "n_vidas": len(vidas), "vidas_a_mais": faltas,
            "vidas": [{k: v[k] for k in ("i", "dono", "semente", "dias", "atendimentos", "log_sha256")}
                      | {"decisoes": len(v["decisoes"]), "falas": {p: sum(d["conteudo"] == p for d in v["decisoes"]) for p in CONTEUDOS_FALA}}
                      for v in vidas],
            "E3": e3, "E2": e2, "sequencias": seqs}
