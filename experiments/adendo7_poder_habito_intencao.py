"""O poder e a margem do primario da C2, o habito com o credito na corrida do comportamento (o adendo 7 do
docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md; a HI-4 da docs/TAREFA_V3_HABITO_INTENCAO.md): so le dois `medidas.json` que estao no
git, nenhuma vida, nenhum replay, nenhuma semente da faixa 75101...75505. O sha256 de cada fonte e conferido contra o registrado no
RESULTADO antes de qualquer conta:
  - a reavaliacao (66101 a 66505, 7 200 vidas; RESULTADO, secao 8): o M1 e o M2 do conserto, no comedouro, no perto e no longe;
  - a run da C1 (71101 a 71505, 3 600 vidas; RESULTADO, secao 13): o M0, o M2 e o M3* no `longe_fixo` e no longe, sem o M1.

O primario P-A e M2c - M2 no indice "ganhou, fica" de hoje (`repeticao.indice`, dias 8 a 14), pareado por unidade (base, k): a unidade e
a media das 8 celulas do `longe_fixo` e do comedouro (uma vida por dono e lugar) da diferenca celula a celula. O M2c nao existe; a
dispersao de um contraste do mesmo indice entre dois bracos que diferem num modulo e lida onde existe, sempre com a media das 4 celulas
de um lugar por unidade:
  - o G-ABLA-P2 (M2 - M1) da reavaliacao, no comedouro (a celula comum com a C2), no longe e no perto;
  - o M3* - M2 e o M2 - M0 da C1 no `longe_fixo` (o lugar novo; nenhum dos dois e o contraste da C2, so a escala da dispersao ali).
O sigma de planejamento e o maior dp de 4 celulas, com a folga de 20 % da A5.9. Ele e conservador para a media de 8 celulas (que, com as
duas metades independentes, teria a variancia da media das duas).

A margem sai do poder (a conta da A6.5, sem mudanca): para cada K, o menor delta com poder >= 0,8 do criterio (o limite inferior do IC95
do t acima de 0), pela aproximacao normal do t nao central. Ao lado, por simulacao (2 000 replicas, semente 4242; as diferencas do
comedouro, centradas, na escala do sigma de planejamento, deslocadas e sorteadas com reposicao em K unidades; o IC pela conta do
metrics.ic_t): o poder na margem e a fracao com o IC95 inteiro dentro de (-margem, +margem) com o efeito verdadeiro 0, com o sigma de
planejamento e com o sigma observado no comedouro.
Saem tambem o nivel do indice por braco e lugar, as celulas sem indice (None), o comprimento das corridas que o M2 e o M1 da C1 e da
reavaliacao teriam (nao gravado nelas: so o que a `repeticao` ja tem) e o custo por vida.

Todos os numeros sao PROPOSTOS, SEM FONTE; nenhum e gate.

    python experiments/adendo7_poder_habito_intencao.py
grava artifacts_v2_digibrain_prototipo/habito_intencao/adendo7_poder.json
"""
from __future__ import annotations

import json
import math
import random
import statistics
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import adendo6_poder_longe_regular as a6  # noqa: E402
import bancada_v2 as bv  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402
from digilab.metrics import assimetria_g1, ic_t, quantil_t  # noqa: E402

FONTES = {"reavaliacao": (RAIZ / "artifacts_v2_digibrain_prototipo" / "reavaliacao" / "medidas.json", "73ae8a8a"),    # RESULTADO, 8
          "c1": (RAIZ / "artifacts_v2_digibrain_prototipo" / "longe_regular" / "run" / "medidas.json", "5a4fb207")}   # RESULTADO, 13
SAIDA = RAIZ / "artifacts_v2_digibrain_prototipo" / "habito_intencao" / "adendo7_poder.json"
FOLGA = a6.FOLGA                            # 1,2, como na A5.9 e na A6.5
KS = (50, 100, 150, 200, 300)               # unidades (base, k): multiplos de 5, as cinco bases da faixa
PODER_ALVO = a6.PODER_ALVO
REPLICAS = a6.REPLICAS
SEMENTE = a6.SEMENTE
BRACOS_C2 = ("M1", "M2", "M2c")             # a HI-1
LUGARES_C2 = ("longe_fixo", "comedouro", "longe")                     # a HI-2: os dois primeiros no primario, o longe descritivo
VIDAS_POR_UNIDADE = len(LUGARES_C2) * len(orq.DONOS) * len(BRACOS_C2)   # 36
UNIDADES = {"reavaliacao": 50, "c1": 150}
INDICE = lambda v: v["repeticao"]["indice"]          # noqa: E731


def diferencas(medidas: dict, lugar: str, a: str, b: str, f, unidades: int) -> tuple[list[float], int]:
    """a - b na medida f, celula a celula, com a media das 4 celulas do lugar por unidade (base, k); as celulas com None num dos bracos
    ficam fora (a regra do `por_unidade` do orquestrador), contadas. Devolve (as diferencas por unidade, as celulas fora)."""
    vidas: dict = {}
    for v in medidas.values():
        if v["lugar"] == lugar and v["braco"] in (a, b):
            chave = ((v["base"], v["k"], v["dono"]), v["braco"])
            if chave in vidas:
                raise RuntimeError(f"vida repetida: {v['vida']}")
            vidas[chave] = f(v)
    por: dict = {}
    fora = 0
    for (celula, braco), x in vidas.items():
        if braco != a:
            continue
        if (celula, b) not in vidas:
            raise RuntimeError(f"a vida {b} do par {celula} falta")
        y = vidas[(celula, b)]
        por.setdefault(celula[:2], [])
        if x is None or y is None:
            fora += 1
            continue
        por[celula[:2]].append(x - y)
    if len(por) != unidades:
        raise RuntimeError(f"as unidades nao sao {unidades}: {len(por)}")
    return [statistics.fmean(xs) for _, xs in sorted(por.items()) if xs], fora


def nivel(medidas: dict, lugar: str, braco: str, f) -> dict:
    """o nivel do indice num braco e lugar: a media das celulas com valor por unidade, e as celulas sem valor"""
    por: dict = {}
    fora = 0
    for v in medidas.values():
        if v["lugar"] == lugar and v["braco"] == braco:
            x = f(v)
            por.setdefault((v["base"], v["k"]), [])
            if x is None:
                fora += 1
            else:
                por[(v["base"], v["k"])].append(x)
    xs = [statistics.fmean(v) for _, v in sorted(por.items()) if v]
    return {**_resumo(xs), "celulas_sem_indice": fora}


def _resumo(xs: list[float]) -> dict:
    ic = ic_t(xs)
    return {"unidades": len(xs), "media": ic["media"], "dp": ic["dp"], "ic95_t": [ic["ic_inferior"], ic["ic_superior"]],
            "g1": assimetria_g1(xs)}


def simular(difs: list[float], verdadeiro: float, k: int, rng: random.Random) -> list[tuple[float, float]]:
    """a simulacao da A6.5, sem mudanca (a do adendo 6)"""
    m = statistics.fmean(difs)
    base = [x - m + verdadeiro for x in difs]
    t = quantil_t(k - 1, 0.95)
    out = []
    for _ in range(REPLICAS):
        xs = [rng.choice(base) for _ in range(k)]
        media = statistics.fmean(xs)
        meia = t * statistics.stdev(xs) / math.sqrt(k)
        out.append((media - meia, media + meia))
    return out


def calcular(reav: dict, c1: dict) -> dict:
    fontes_dif = {}
    for lugar in ("comedouro", "longe", "perto"):
        xs, fora = diferencas(reav, lugar, "M2", "M1", INDICE, UNIDADES["reavaliacao"])
        fontes_dif[f"reavaliacao|{lugar}|M2 - M1"] = (xs, fora)
    for a, b in (("M3", "M2"), ("M2", "M0")):
        xs, fora = diferencas(c1, "longe_fixo", a, b, INDICE, UNIDADES["c1"])
        fontes_dif[f"c1|longe_fixo|{a} - {b}"] = (xs, fora)
    disp = {n: {**_resumo(xs), "celulas_fora": fora} for n, (xs, fora) in fontes_dif.items()}
    sigma_max = max(d["dp"] for d in disp.values())
    sigma = sigma_max * FOLGA
    plan_fonte = "reavaliacao|comedouro|M2 - M1"       # a celula comum com a C2, o contraste do mesmo modulo (o P2)
    difs = fontes_dif[plan_fonte][0]
    escala = sigma / disp[plan_fonte]["dp"]
    plan = [x * escala for x in difs]
    rng = random.Random(SEMENTE)
    por_k = {}
    for k in KS:
        m = a6.margem_do_poder(sigma, k)
        r_poder = simular(plan, m, k, rng)
        r_zero = simular(plan, 0.0, k, rng)
        r_zero_obs = simular(difs, 0.0, k, rng)             # o sigma observado no comedouro, sem a folga nem o maximo
        por_k[f"K={k}"] = {"margem": m, "poder_normal_na_margem": a6.poder_normal(m, sigma, k),
                           "poder_simulado_na_margem": sum(1 for a, _ in r_poder if a > 0) / REPLICAS,
                           "verdadeiro_0_ic_dentro_da_margem": sum(1 for a, b in r_zero if a > -m and b < m) / REPLICAS,
                           "verdadeiro_0_ic_acima_de_0": sum(1 for a, _ in r_zero if a > 0) / REPLICAS,
                           "verdadeiro_0_sigma_comedouro_ic_dentro_da_margem": sum(1 for a, b in r_zero_obs if a > -m and b < m) / REPLICAS,
                           "vidas": k * VIDAS_POR_UNIDADE}
    niveis = {f"reavaliacao|{lu}|{b}": nivel(reav, lu, b, INDICE) for lu in ("comedouro", "longe") for b in ("M1", "M2")}
    niveis |= {f"c1|{lu}|{b}": nivel(c1, lu, b, INDICE) for lu in ("longe_fixo", "longe") for b in ("M0", "M2", "M3")}
    custo: dict = {}
    for nome, med, bracos in (("reavaliacao", reav, ("M1", "M2")), ("c1", c1, ("M2",))):
        for v in med.values():
            if v["braco"] not in bracos:
                continue
            c = custo.setdefault(f"{nome}|{v['lugar']}", {"vidas": 0, "cpu": 0.0, "parede": 0.0})
            c["vidas"] += 1
            c["cpu"] += v["custo"]["vida_cpu"]
            c["parede"] += v["custo"]["vida_parede"]
    for c in custo.values():
        c["cpu_por_vida"] = c["cpu"] / c["vidas"]
        c["parede_por_vida_1_processo"] = c["parede"] / c["vidas"]
    return {"rotulo": "o poder e a margem do primario da C2 (P-A: M2c - M2 no indice 'ganhou, fica' de hoje, nas 8 celulas do longe_fixo "
                      "e do comedouro), PROPOSTOS para o adendo 7; aproximacao normal do t nao central, com a conferencia por simulacao; "
                      "sem gate",
            "fonte": {orq.rc._relativo(p): bv._sha(p) for p, _ in FONTES.values()},
            "script": {"arquivo": orq.rc._relativo(Path(__file__)), "sha256": bv._sha(Path(__file__))},
            "unidade": "a media das 4 celulas do lugar (uma vida por dono) da diferenca a - b no indice de hoje, por unidade (base, k); "
                       "as celulas com o indice None num dos bracos ficam fora, contadas",
            "dispersao_indice": disp, "sigma_max_4_celulas": sigma_max, "folga": FOLGA, "sigma_planejamento": sigma,
            "fonte_da_simulacao": plan_fonte, "poder_alvo": PODER_ALVO, "replicas": REPLICAS, "semente": SEMENTE,
            "por_k": por_k, "nivel_indice": niveis, "custo_por_fonte_e_lugar": {n: custo[n] for n in sorted(custo)},
            "vidas_por_unidade_c2": VIDAS_POR_UNIDADE}


if __name__ == "__main__":
    lidos = {}
    for nome, (caminho, prefixo) in FONTES.items():
        sha = bv._sha(caminho)
        if not sha.startswith(prefixo):
            raise RuntimeError(f"o medidas.json de {nome} nao e o registrado: {sha}")
        lidos[nome] = json.loads(caminho.read_text(encoding="utf-8"))
    d = calcular(lidos["reavaliacao"], lidos["c1"])
    bv._gravar(SAIDA, bv._dump(d))
    print(f"gravado {orq.rc._relativo(SAIDA)} (sha256 {bv._sha(SAIDA)})")
