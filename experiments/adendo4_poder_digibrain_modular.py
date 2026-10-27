"""O adendo 4 do plano do DigiBrain modular (docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md, A4): o poder do G-MVP por episodio e o
comportamento dos testes da reavaliacao sob a hipotese nula, so pela reamostragem das unidades do piloto do conserto (#429). Nenhuma vida
roda: o script le artifacts_v2_digibrain_prototipo/conserto/piloto/medidas.json e grava
artifacts_v2_digibrain_prototipo/conserto/adendo4/poder.json.

Quatro contas, todas com a mesma estrutura da reavaliacao (5 bases, K unidades por base):
  1. o poder do G-MVP por episodio (o limite inferior do IC95 >= 0,8) por K, pelo `poder_por_k` do orquestrador, sem mudanca, com dois
     valores verdadeiros supostos: o do plano (0,8 + metade da margem do piloto) e o observado no piloto. Mais o valor no limiar exato;
  2. sob a nula verdadeira (as diferencas do piloto centradas em 0), com K = 10: a taxa de rejeicao de cada teste e a cobertura do IC95.
     A) o do plano (secao 5.2.1): o bootstrap agrupado por base, p = a fracao das medias reamostradas <= 0;
     C) o t pareado sobre as 5K unidades (o `t_pareado` que o `contraste_pareado` ja relata como conferencia);
     D) o t sobre as 5 medias de base (gl = 4);
  3. o poder, com K = 10, dos contrastes com efeito positivo no piloto, pelo t pareado sobre as unidades (o metodo C), com o efeito de
     planejamento do plano (a metade do efeito do piloto);
  4. a largura do IC95 do G-MVP por episodio com K = 10, pelo bootstrap do plano (A) e pelo t sobre as unidades (C).

    python experiments/adendo4_poder_digibrain_modular.py
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

import run_v2_digibrain_prototipo as orq  # noqa: E402
from digilab.metrics import ic_percentil, t_unilateral  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402

PILOTO = RAIZ / "artifacts_v2_digibrain_prototipo" / "conserto" / "piloto" / "medidas.json"
SAIDA = RAIZ / "artifacts_v2_digibrain_prototipo" / "conserto" / "adendo4" / "poder.json"
SEMENTE = 4242
N_BASES = 5
K_REAVALIACAO = 10
KS_MVP = (4, 10, 20, 40, 80, 150, 250, 400, 600, 800, 1000)
REPLICAS_NULA = 2000
REAMOSTRAGENS = 1000
ALFAS = (0.0125, 0.025, 0.05)
ALFA_DO_CONTRASTE = {n: 0.0125 for n in orq.FAMILIA_ABLA} | {n: 0.025 for n in orq.FAMILIA_MOD + orq.FAMILIA_DX}


def _t_p(valores: list[float]) -> float:
    """o p unilateral do t (positivo = a direcao prevista); sem variacao, 1 (como o contraste_pareado, que nao faz o t)"""
    n = len(valores)
    m = statistics.fmean(valores)
    dp = statistics.stdev(valores)
    return 1.0 if dp == 0.0 else t_unilateral(m / (dp / math.sqrt(n)), n - 1)


def _t_quantil(gl: int, p: float = 0.975) -> float:
    """o quantil da t de Student pela bissecao sobre t_unilateral"""
    lo, hi = 0.0, 50.0
    for _ in range(100):
        meio = (lo + hi) / 2
        lo, hi = (meio, hi) if t_unilateral(meio, gl) > 1.0 - p else (lo, meio)
    return (lo + hi) / 2


def _bases(rng: random.Random, pool: list[float], k: int) -> list[list[float]]:
    return [[pool[rng.randrange(len(pool))] for _ in range(k)] for _ in range(N_BASES)]


def _medias_bootstrap(grupos: list[list[float]], reamostragens: int, rng: random.Random) -> list[float]:
    """o bootstrap do plano (o _p_bootstrap do orquestrador): reamostra as bases, a media = a soma das somas / a soma das contagens"""
    somas, cont = [sum(g) for g in grupos], [len(g) for g in grupos]
    n = len(grupos)
    out = []
    for _ in range(reamostragens):
        s = c = 0
        for _ in range(n):
            i = rng.randrange(n)
            s += somas[i]
            c += cont[i]
        out.append(s / c)
    return out


def nula(difs: list[float], rng: random.Random) -> dict:
    media = statistics.fmean(difs)
    pool = [d - media for d in difs]
    if all(abs(d) < 1e-12 for d in pool):
        return {"motivo": "sem variacao no piloto"}
    rejeita = {m: {a: 0 for a in ALFAS} for m in "ACD"}
    cobre_a = cobre_c = 0
    tq_c = _t_quantil(N_BASES * K_REAVALIACAO - 1)
    for _ in range(REPLICAS_NULA):
        grupos = _bases(rng, pool, K_REAVALIACAO)
        medias = _medias_bootstrap(grupos, REAMOSTRAGENS, rng)
        p_a = sum(1 for m in medias if m <= 0.0) / REAMOSTRAGENS
        lo, hi = ic_percentil(medias, 0.95)
        cobre_a += lo <= 0.0 <= hi
        todas = [x for g in grupos for x in g]
        p_c = _t_p(todas)
        meio = tq_c * statistics.stdev(todas) / math.sqrt(len(todas))
        cobre_c += abs(statistics.fmean(todas)) <= meio
        p_d = _t_p([statistics.fmean(g) for g in grupos])
        for a in ALFAS:
            rejeita["A"][a] += p_a <= a
            rejeita["C"][a] += p_c <= a
            rejeita["D"][a] += p_d <= a
    return {"n_piloto": len(difs), "dp_piloto": statistics.stdev(difs),
            "rejeicao_sob_a_nula": {m: {str(a): rejeita[m][a] / REPLICAS_NULA for a in ALFAS} for m in rejeita},
            "cobertura_ic95": {"A": cobre_a / REPLICAS_NULA, "C": cobre_c / REPLICAS_NULA}}


def poder_t(difs: list[float], alfa: float, rng: random.Random) -> dict:
    media = statistics.fmean(difs)
    efeito = media / 2
    pool = [d - media + efeito for d in difs]
    acertos = 0
    for _ in range(REPLICAS_NULA):
        acertos += _t_p([x for g in _bases(rng, pool, K_REAVALIACAO) for x in g]) <= alfa
    return {"efeito_piloto": media, "efeito_planejamento": efeito, "alfa": alfa, "poder_k10": acertos / REPLICAS_NULA}


def largura_mvp(fracoes: list[float], rng: random.Random) -> dict:
    tq = _t_quantil(N_BASES * K_REAVALIACAO - 1)
    la, lc = [], []
    for _ in range(500):
        grupos = _bases(rng, fracoes, K_REAVALIACAO)
        lo, hi = ic_percentil(_medias_bootstrap(grupos, REAMOSTRAGENS, rng), 0.95)
        la.append(hi - lo)
        todas = [x for g in grupos for x in g]
        lc.append(2 * tq * statistics.stdev(todas) / math.sqrt(len(todas)))
    return {"k": K_REAVALIACAO, "largura_mediana_A": statistics.median(la), "largura_mediana_C": statistics.median(lc)}


def main() -> None:
    medidas = json.loads(PILOTO.read_text(encoding="utf-8"))
    reg = [r for r in medidas.values() if r["braco"] != "A11"]
    fc = orq.fracao_com_cadeia_ep(reg)["por_unidade"]
    fracoes = [fc[k] for k in sorted(fc)]
    frac = statistics.fmean(fracoes)
    limiar = orq.G_MVP_EP["limiar"]
    contrastes = {**orq.CONTRASTES_ABLA, **orq.CONTRASTES_MOD, **orq.contrastes_dx(orq.CELULAS_LONGE)}
    difs = {n: list(orq.por_unidade(reg, a, b, med, cel).values()) for n, (a, b, med, cel) in contrastes.items()}

    cfg_poder = json.loads((RAIZ / "experiments/configs/v2_digibrain_prototipo/piloto_conserto.json").read_text(encoding="utf-8"))["poder"]
    unidades = [{"G-MVP": v} for v in fracoes]
    verdades = {"plano": limiar + (frac - limiar) / 2, "observado": frac, "limiar": limiar}
    mvp = {nome: {str(k): orq.poder_por_k(unidades, {}, k, cfg_poder, {}, v)["poder_mvp"] for k in KS_MVP}
           for nome, v in verdades.items()}

    rng = random.Random(derivar_semente("adendo4-digibrain", SEMENTE))
    sob_nula = {n: nula(v, rng) for n, v in {**difs, "G-MVP-EP": [f - limiar for f in fracoes]}.items()}
    poder = {n: poder_t(v, ALFA_DO_CONTRASTE[n], rng) for n, v in difs.items() if statistics.fmean(v) > 0}
    out = {"fonte": str(PILOTO.relative_to(RAIZ)).replace("\\", "/"), "n_bases": N_BASES, "k_reavaliacao": K_REAVALIACAO,
           "g_mvp_ep": {"fracao_piloto": frac, "por_unidade": fracoes, "dp": statistics.stdev(fracoes), "limiar": limiar,
                        "verdades": verdades, "poder_por_k": mvp, "replicas": cfg_poder["replicas"],
                        "reamostragens_internas": cfg_poder["reamostragens_internas"]},
           "sob_a_nula": {"replicas": REPLICAS_NULA, "reamostragens": REAMOSTRAGENS, "contrastes": sob_nula},
           "poder_t_k10": poder, "largura_ic95_g_mvp_ep": largura_mvp(fracoes, rng)}
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_bytes((json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True) + "\n").encode("utf-8"))   # LF, o mesmo sha no git
    print(f"gravado {SAIDA.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
