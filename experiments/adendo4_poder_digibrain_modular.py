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
from digilab.metrics import holm, ic_percentil, t_unilateral  # noqa: E402
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


def ep_monte_carlo(p: float, replicas: int) -> dict:
    """a incerteza de uma taxa simulada: o erro padrao binomial e o intervalo de Wilson de 95 %"""
    z = 1.959963984540054
    ep = math.sqrt(p * (1 - p) / replicas)
    centro = (p + z * z / (2 * replicas)) / (1 + z * z / replicas)
    meio = z * math.sqrt(p * (1 - p) / replicas + z * z / (4 * replicas * replicas)) / (1 + z * z / replicas)
    return {"ep": ep, "wilson95": [centro - meio, centro + meio]}


FAMILIAS = {"G-ABLA": orq.FAMILIA_ABLA, "G-MOD": orq.FAMILIA_MOD, "G-DX": orq.FAMILIA_DX}
# o metodo por contraste da proposta (A4.4): o t sobre as unidades (C), salvo no G-MOD-EMB, cujas unidades de uma base dependem umas das
# outras pela serie E doadora (a secao 2: o doador e a unidade seguinte da mesma base), e por isso o t sobre as medias de base (D)
METODO_PROPOSTO = {n: "C" for n in orq.FAMILIA_ABLA + orq.FAMILIA_MOD + orq.FAMILIA_DX} | {"G-MOD-EMB": "D"}
REPLICAS_FAMILIA = 4000


def familias_holm(unidades: list[dict], efeitos: dict, rng: random.Random) -> dict:
    """o Holm no nivel da familia (alfa 0,05): as unidades do piloto sorteadas inteiras (a correlacao entre os contrastes da mesma unidade
    fica), cada contraste centrado e deslocado para o efeito dado (0 = a nula verdadeira). Por familia e por metodo (A, C e o proposto):
    a taxa de algum contraste nulo rejeitado (o erro da familia, FWER) e o poder de cada contraste nao nulo"""
    medias = {n: statistics.fmean(u[n] for u in unidades) for ns in FAMILIAS.values() for n in ns}
    metodos = ("A", "C", "proposto")
    fwer = {f: {m: 0 for m in metodos} for f in FAMILIAS}
    poder = {f: {m: {n: 0 for n in ns if efeitos.get(n)} for m in metodos} for f, ns in FAMILIAS.items()}
    for _ in range(REPLICAS_FAMILIA):
        sorteio = [[unidades[rng.randrange(len(unidades))] for _ in range(K_REAVALIACAO)] for _ in range(N_BASES)]
        for f, ns in FAMILIAS.items():
            ps = {"A": {}, "C": {}, "D": {}}
            for n in ns:
                grupos = [[u[n] - medias[n] + efeitos.get(n, 0.0) for u in g] for g in sorteio]
                medias_b = _medias_bootstrap(grupos, REAMOSTRAGENS, rng)
                ps["A"][n] = sum(1 for m in medias_b if m <= 0.0) / REAMOSTRAGENS
                ps["C"][n] = _t_p([x for g in grupos for x in g])
                ps["D"][n] = _t_p([statistics.fmean(g) for g in grupos])
            ps["proposto"] = {n: ps[METODO_PROPOSTO[n]][n] for n in ns}
            for m in metodos:
                h = holm(ps[m], 0.05)
                fwer[f][m] += any(h[n]["rejeita"] for n in ns if not efeitos.get(n))
                for n in poder[f][m]:
                    poder[f][m][n] += h[n]["rejeita"]
    return {"efeitos": efeitos, "replicas": REPLICAS_FAMILIA,
            "fwer": {f: {m: {"taxa": c / REPLICAS_FAMILIA, **ep_monte_carlo(c / REPLICAS_FAMILIA, REPLICAS_FAMILIA)} for m, c in d.items()}
                     for f, d in fwer.items()},
            "poder": {f: {m: {n: c / REPLICAS_FAMILIA for n, c in d.items()} for m, d in dm.items()} for f, dm in poder.items()}}


FORMAS = {
    "normal": lambda r: r.gauss(0.0, 1.0),
    "exponencial (assimetria +2)": lambda r: r.expovariate(1.0) - 1.0,
    "exponencial invertida (assimetria -2)": lambda r: 1.0 - r.expovariate(1.0),
    "lognormal sigma 1 (assimetria ~6)": lambda r: math.exp(r.gauss(0.0, 1.0)) - math.exp(0.5),
    "lognormal invertida": lambda r: math.exp(0.5) - math.exp(r.gauss(0.0, 1.0)),
    "t com 3 gl (cauda pesada)": lambda r: r.gauss(0.0, 1.0) / math.sqrt(sum(r.gauss(0.0, 1.0) ** 2 for _ in range(3)) / 3),
    "gama k 4 invertida (assimetria -1)": lambda r: 4.0 - r.gammavariate(4.0, 1.0),
    "gama k 16 invertida (assimetria -0,5)": lambda r: 16.0 - r.gammavariate(16.0, 1.0),
}


def assimetria(valores: list[float]) -> float | None:
    """o coeficiente de assimetria amostral (g1, o momento de ordem 3 sobre o dp ao cubo); None sem variacao"""
    m = statistics.fmean(valores)
    m2 = statistics.fmean((x - m) ** 2 for x in valores)
    return None if m2 == 0.0 else statistics.fmean((x - m) ** 3 for x in valores) / m2 ** 1.5


def sensibilidade_forma(rng: random.Random) -> dict:
    """o erro do tipo I do t sobre as unidades (C) e do bootstrap do plano (A) com formas de distribuicao fixas, de media 0, no lugar das 6
    unidades do piloto: o t nao depende da escala, so da forma, e as 6 unidades do piloto quase nao informam a forma"""
    out = {}
    for nome, gerar in FORMAS.items():
        rej = {m: {a: 0 for a in ALFAS} for m in "AC"}
        for _ in range(REPLICAS_NULA):
            grupos = [[gerar(rng) for _ in range(K_REAVALIACAO)] for _ in range(N_BASES)]
            medias_b = _medias_bootstrap(grupos, REAMOSTRAGENS, rng)
            p = {"A": sum(1 for m in medias_b if m <= 0.0) / REAMOSTRAGENS, "C": _t_p([x for g in grupos for x in g])}
            for m in rej:
                for a in ALFAS:
                    rej[m][a] += p[m] <= a
        out[nome] = {m: {str(a): rej[m][a] / REPLICAS_NULA for a in ALFAS} for m in rej}
    return {"replicas": REPLICAS_NULA, "formas": out}


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
    for v in sob_nula.values():
        if "rejeicao_sob_a_nula" in v:
            v["ep_monte_carlo"] = {m: {a: ep_monte_carlo(p, REPLICAS_NULA)["ep"] for a, p in d.items()}
                                   for m, d in v["rejeicao_sob_a_nula"].items()}
    chaves = sorted(set.intersection(*(set(orq.por_unidade(reg, a, b, med, cel)) for a, b, med, cel in contrastes.values())))
    por_u = {n: orq.por_unidade(reg, a, b, med, cel) for n, (a, b, med, cel) in contrastes.items()}
    unidades_juntas = [{n: por_u[n][k] for n in contrastes} for k in chaves]
    planejamento = {n: statistics.fmean(difs[n]) / 2 for n in difs if statistics.fmean(difs[n]) > 0}
    familia = {"nula_global": familias_holm(unidades_juntas, {}, rng),
               "nula_parcial": familias_holm(unidades_juntas, planejamento, rng)}
    out = {"fonte": str(PILOTO.relative_to(RAIZ)).replace("\\", "/"), "n_bases": N_BASES, "k_reavaliacao": K_REAVALIACAO,
           "g_mvp_ep": {"fracao_piloto": frac, "por_unidade": fracoes, "dp": statistics.stdev(fracoes), "limiar": limiar,
                        "verdades": verdades, "poder_por_k": mvp, "replicas": cfg_poder["replicas"],
                        "reamostragens_internas": cfg_poder["reamostragens_internas"]},
           "sob_a_nula": {"replicas": REPLICAS_NULA, "reamostragens": REAMOSTRAGENS, "contrastes": sob_nula},
           "poder_t_k10": poder, "largura_ic95_g_mvp_ep": largura_mvp(fracoes, rng),
           "familias_holm": familia, "metodo_proposto": METODO_PROPOSTO, "sensibilidade_forma": sensibilidade_forma(rng),
           "assimetria_piloto": {n: assimetria(v) for n, v in {**difs, "G-MVP-EP": fracoes}.items()}}
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_bytes((json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True) + "\n").encode("utf-8"))   # LF, o mesmo sha no git
    print(f"gravado {SAIDA.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
