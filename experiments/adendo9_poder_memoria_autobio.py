"""O poder e a margem do primario da C4, a validacao causal da memoria autobiografica (o adendo 9 do
docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md; a secao 4 da docs/TAREFA_V2_MEMORIA_AUTOBIOGRAFICA.md): so le artefatos que estao no
git, nenhuma vida, nenhum replay, nenhuma semente da faixa 77101...77505. O sha256 de cada fonte e conferido contra o registrado no RESULTADO
antes de qualquer conta:
  - a run da C1 (71101 a 71505, 3 600 vidas; RESULTADO, secao 13): o M0, o M2 e o M3* no `longe_fixo` e no longe;
  - a run da C3 (76101 a 76505, 7 200 vidas; RESULTADO, secao 15): o M3*, o M3*R, o M2 e o M2R no `longe_fixo`, no comedouro e no longe;
  - a run da C2 (75101 a 75505, 5 400 vidas; RESULTADO, secao 14): so o tempo de parede e o custo por vida;
  - os `meta.json` das tres runs: o tempo de parede com 4 processos, para a estimativa das horas.

O primario e a familia de tres contrastes REL - SEM, REL - REC e REL - EMB na taxa de fechamento por episodio de fome
(`episodios_fome.taxa`, a medida de A6.4), pareados por unidade (base, k): a unidade e a media das 4 celulas do `longe_fixo` (uma vida por
dono) da diferenca celula a celula, com o Holm sobre os tres p unilaterais (alfa 0,025 na familia). Nenhum braco da C4 existe; a dispersao
de um contraste da mesma medida, no mesmo lugar, entre bracos do modular que diferem em um modulo ou numa regra, e lida na C1 e na C3:
  - da C1: o M3* - M2 (o M-MEM), o M2 - M0 (o P1 e o P2) e o M3* - M0 no `longe_fixo`;
  - da C3: o M3*R - M3* e o M2R - M2 no `longe_fixo` (uma regra do M-ARB no mesmo cerebro, a dispersao observada mais nova);
  - ao lado, sem entrar no sigma: o M3*R - M3* no comedouro (a escala da guarda) e o M3* - M2 da C1 e o M3*R - M3* da C3 no longe
    sorteado (a escala da secundaria da C4-E2 no sorteado).
O sigma de planejamento e o maior dp das cinco fontes do `longe_fixo`, com a folga de 20 % da A5.9.

A margem sai do poder (a conta da A6.5, com o alfa de cada teste trocado): para cada K, o menor delta com poder >= 0,8 do criterio mais
duro do Holm (o primeiro passo, alfa/3 = 0,00833 unilateral: o limite inferior do IC de 98,33 % do t acima de 0), pela aproximacao normal
do t nao central; ao lado, a mesma conta com o alfa de um contraste so (0,025, a das secundarias). Por simulacao (2 000 replicas, semente
4242; as diferencas M3* - M2 do `longe_fixo` da C1, centradas, na escala do sigma de planejamento, deslocadas e sorteadas com reposicao em K
unidades): o poder no primeiro passo do Holm na margem, o poder dos tres contrastes juntos (o Holm de verdade, com tres efeitos iguais a
margem, cada um com o seu sorteio), e, com o efeito verdadeiro 0, a fracao com o IC95 inteiro dentro de (-margem, +margem) com o sigma de
planejamento e com o observado.

Saem tambem o nivel da taxa por episodio por braco e lugar, a G-PESA da memoria do M3* (a escala da premissa P-PESA), as visitas ao lugar
lembrado (o espaco da C4-E1) e o custo por vida.

Todos os numeros sao PROPOSTOS, SEM FONTE; nenhum e gate.

    python experiments/adendo9_poder_memoria_autobio.py
grava artifacts_v2_digibrain_prototipo/memoria_autobio/adendo9_poder.json
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
import adendo7_poder_habito_intencao as a7  # noqa: E402
import bancada_v2 as bv  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402
from digilab.metrics import holm, quantil_t  # noqa: E402

PASTA_C1 = RAIZ / "artifacts_v2_digibrain_prototipo" / "longe_regular" / "run"
PASTA_C2 = RAIZ / "artifacts_v2_digibrain_prototipo" / "habito_intencao" / "run"
PASTA_C3 = RAIZ / "artifacts_v2_digibrain_prototipo" / "redecidir_evento" / "run"
FONTES = {"c1": (PASTA_C1 / "medidas.json", "5a4fb207"),          # RESULTADO, 13
          "c3": (PASTA_C3 / "medidas.json", "d5b7c974")}          # RESULTADO, 15
METAS = {"c1": (PASTA_C1 / "meta.json", "b2cb111a"),             # os meta.json das tres runs (o tempo de parede com 4 processos)
         "c2": (PASTA_C2 / "meta.json", "5ab56d67"),
         "c3": (PASTA_C3 / "meta.json", "b9024ace")}
SAIDA = RAIZ / "artifacts_v2_digibrain_prototipo" / "memoria_autobio" / "adendo9_poder.json"
FOLGA = a6.FOLGA                            # 1,2, como na A5.9 e na A6.5
KS = (100, 150, 200, 250, 300)              # unidades (base, k): multiplos de 5, as cinco bases da faixa
PODER_ALVO = a6.PODER_ALVO
REPLICAS = a6.REPLICAS
SEMENTE = a6.SEMENTE
ALFA_FAMILIA = 0.025                        # unilateral, a do primario de um contraste so das C1 a C3
N_FAMILIA = 3                               # REL - SEM, REL - REC, REL - EMB
BRACOS_C4 = ("REL", "SEM", "REC", "EMB", "RELsN", "REL+F")             # o adendo 9 (A9.2)
LUGARES_C4 = ("longe_fixo", "comedouro", "longe")                      # o primario, a guarda e o descritivo
VIDAS_POR_UNIDADE = len(LUGARES_C4) * len(orq.DONOS) * len(BRACOS_C4)   # 72
UNIDADES = {"c1": 150, "c3": 150}
EPISODIO = a6.EPISODIO
PESA_MEMORIA = lambda v: v["influencia"]["memoria"]                     # noqa: E731


def _resumo(xs: list[float]) -> dict:
    return a7._resumo(xs)


def _ler(caminho: Path, prefixo: str, nome: str) -> dict:
    sha = bv._sha(caminho)
    if not sha.startswith(prefixo):
        raise RuntimeError(f"o {caminho.name} de {nome} nao e o registrado: {sha}")
    return json.loads(caminho.read_text(encoding="utf-8"))


def nivel_bilateral(alfa_unilateral: float) -> float:
    """o nivel do IC bilateral cujo limite inferior e o teste unilateral de nivel alfa (o quantil_t pede o bilateral)"""
    return 1.0 - 2.0 * alfa_unilateral


def poder_normal(delta: float, sigma: float, k: int, alfa: float) -> float:
    """P(o limite inferior do IC unilateral de nivel alfa > 0) com o efeito verdadeiro delta: 1 - Phi(t_1-alfa;K-1 - (delta / sigma) raiz(K))
    (a A5.6 com o alfa como parametro; com alfa = 0,025 e a de a6.poder_normal)"""
    return 1.0 - a6._phi(quantil_t(k - 1, nivel_bilateral(alfa)) - delta / sigma * math.sqrt(k))


def margem_do_poder(sigma: float, k: int, alfa: float) -> float:
    """o menor delta com poder_normal >= PODER_ALVO, por bissecao (o poder cresce com delta)"""
    lo, hi = 0.0, 1.0
    if poder_normal(hi, sigma, k, alfa) < PODER_ALVO:
        raise RuntimeError(f"nem delta = 1 chega ao poder alvo com K = {k}")
    for _ in range(100):
        meio = (lo + hi) / 2.0
        lo, hi = (meio, hi) if poder_normal(meio, sigma, k, alfa) < PODER_ALVO else (lo, meio)
    return hi


def _p_unilateral(xs: list[float]) -> float:
    """o p unilateral do t sobre as unidades (P(T >= t)), pela aproximacao normal so na simulacao (gl >= 99: a diferenca e < 0,001)"""
    t = statistics.fmean(xs) / (statistics.stdev(xs) / math.sqrt(len(xs)))
    return 1.0 - a6._phi(t)


def simular(difs: list[float], verdadeiro: float, k: int, rng: random.Random) -> dict:
    """a simulacao da A6.5, com o Holm: cada replica sorteia tres conjuntos de K unidades (um por contraste) do mesmo efeito verdadeiro;
    o primeiro passo (o limite inferior do IC de nivel 1 - 2 alfa/3 acima de 0, no primeiro conjunto), os tres juntos pelo Holm e, no
    primeiro conjunto, o IC95 (a classe de A6.6)"""
    m = statistics.fmean(difs)
    base = [x - m + verdadeiro for x in difs]
    t95 = quantil_t(k - 1, 0.95)
    t_holm = quantil_t(k - 1, nivel_bilateral(ALFA_FAMILIA / N_FAMILIA))
    out = {"primeiro_passo": 0, "holm_tres": 0, "ic95": []}
    for _ in range(REPLICAS):
        conj = [[rng.choice(base) for _ in range(k)] for _ in range(N_FAMILIA)]
        xs = conj[0]
        media, dp = statistics.fmean(xs), statistics.stdev(xs)
        out["primeiro_passo"] += media - t_holm * dp / math.sqrt(k) > 0
        h = holm({str(i): _p_unilateral(c) for i, c in enumerate(conj)}, ALFA_FAMILIA)
        out["holm_tres"] += all(v["rejeita"] for v in h.values())
        meia = t95 * dp / math.sqrt(k)
        out["ic95"].append((media - meia, media + meia))
    return out


def calcular(c1: dict, c3: dict, metas: dict) -> dict:
    fontes_sigma = {}
    for a, b in (("M3", "M2"), ("M2", "M0"), ("M3", "M0")):
        fontes_sigma[f"c1|longe_fixo|{a} - {b}"] = a7.diferencas(c1, "longe_fixo", a, b, EPISODIO, UNIDADES["c1"])
    for a, b in (("M3R", "M3"), ("M2R", "M2")):
        fontes_sigma[f"c3|longe_fixo|{a} - {b}"] = a7.diferencas(c3, "longe_fixo", a, b, EPISODIO, UNIDADES["c3"])
    ao_lado = {"c3|comedouro|M3R - M3": a7.diferencas(c3, "comedouro", "M3R", "M3", EPISODIO, UNIDADES["c3"]),
               "c1|longe|M3 - M2": a7.diferencas(c1, "longe", "M3", "M2", EPISODIO, UNIDADES["c1"]),
               "c3|longe|M3R - M3": a7.diferencas(c3, "longe", "M3R", "M3", EPISODIO, UNIDADES["c3"])}
    disp = {n: {**_resumo(xs), "celulas_fora": fora, "no_sigma": True} for n, (xs, fora) in fontes_sigma.items()}
    disp |= {n: {**_resumo(xs), "celulas_fora": fora, "no_sigma": False} for n, (xs, fora) in ao_lado.items()}
    sigma_max = max(disp[n]["dp"] for n in fontes_sigma)
    sigma_fonte = max(fontes_sigma, key=lambda n: disp[n]["dp"])
    sigma = sigma_max * FOLGA
    plan_fonte = "c1|longe_fixo|M3 - M2"          # o contraste do M-MEM, no lugar do primario (a fonte da simulacao das C1 a C3)
    difs = fontes_sigma[plan_fonte][0]
    escala = sigma / disp[plan_fonte]["dp"]
    plan = [x * escala for x in difs]
    alfa_passo = ALFA_FAMILIA / N_FAMILIA
    rng = random.Random(SEMENTE)
    por_k = {}
    for k in KS:
        m = margem_do_poder(sigma, k, alfa_passo)
        r_poder = simular(plan, m, k, rng)
        r_zero = simular(plan, 0.0, k, rng)
        r_zero_obs = simular(difs, 0.0, k, rng)          # o sigma observado do M3* - M2, sem a folga nem o maximo
        por_k[f"K={k}"] = {"margem": m, "margem_um_contraste": margem_do_poder(sigma, k, ALFA_FAMILIA),
                           "poder_normal_na_margem": poder_normal(m, sigma, k, alfa_passo),
                           "poder_simulado_primeiro_passo": r_poder["primeiro_passo"] / REPLICAS,
                           "poder_simulado_holm_tres": r_poder["holm_tres"] / REPLICAS,
                           "verdadeiro_0_ic_dentro_da_margem": sum(1 for a, b in r_zero["ic95"] if a > -m and b < m) / REPLICAS,
                           "verdadeiro_0_holm_rejeita_tres": r_zero["holm_tres"] / REPLICAS,
                           "verdadeiro_0_primeiro_passo": r_zero["primeiro_passo"] / REPLICAS,
                           "verdadeiro_0_sigma_observado_ic_dentro_da_margem":
                               sum(1 for a, b in r_zero_obs["ic95"] if a > -m and b < m) / REPLICAS,
                           "vidas": k * VIDAS_POR_UNIDADE}
    niveis = {f"c1|{lu}|{b}": a7.nivel(c1, lu, b, EPISODIO) for lu in ("longe_fixo", "longe") for b in ("M0", "M2", "M3")}
    niveis |= {f"c3|{lu}|{b}": a7.nivel(c3, lu, b, EPISODIO) for lu in LUGARES_C4 for b in ("M3", "M3R", "M2", "M2R")}
    pesa = {f"c1|{lu}|M3": a7.nivel(c1, lu, "M3", PESA_MEMORIA) for lu in ("longe_fixo", "longe")}
    pesa |= {f"c3|{lu}|M3": a7.nivel(c3, lu, "M3", PESA_MEMORIA) for lu in LUGARES_C4}
    visitas: dict = {}
    for nome, med in (("c1", c1), ("c3", c3)):
        for v in med.values():
            if v["braco"] != "M3":
                continue
            x = visitas.setdefault(f"{nome}|{v['lugar']}|M3", {"vidas": 0, "visitas": 0, "vazias": 0})
            x["vidas"] += 1
            x["visitas"] += v["visitas_lugar_lembrado"]
            x["vazias"] += v["visitas_vazias"]["vazias"] if isinstance(v["visitas_vazias"], dict) else v["visitas_vazias"]
    custo: dict = {}
    for nome, med in (("c1", c1), ("c3", c3)):
        for v in med.values():
            if v["braco"] != "M3":
                continue
            c = custo.setdefault(f"{nome}|{v['lugar']}|M3", {"vidas": 0, "cpu": 0.0, "parede": 0.0})
            c["vidas"] += 1
            c["cpu"] += v["custo"]["vida_cpu"]
            c["parede"] += v["custo"]["vida_parede"]
    for c in custo.values():
        c["cpu_por_vida"] = c["cpu"] / c["vidas"]
        c["parede_por_vida_1_processo"] = c["parede"] / c["vidas"]
    vidas_da_run = {"c1": len(c1), "c2": 5400, "c3": len(c3)}       # a C2 so pelo meta.json (5 400 vidas, RESULTADO 14)
    parede = {}
    for nome, m in metas.items():
        parede[nome] = {"vidas": vidas_da_run[nome], "processos": m["processos"], "vidas_parede_s": m["vidas_parede_s"],
                        "s_por_vida": m["vidas_parede_s"] / vidas_da_run[nome]}
    estimativa = {f"K={k}": {"vidas": k * VIDAS_POR_UNIDADE,
                             **{f"parede_s_pela_{n}": k * VIDAS_POR_UNIDADE * p["s_por_vida"] for n, p in parede.items()}} for k in KS}
    return {"rotulo": "o poder e a margem do primario da C4 (REL - SEM, REL - REC e REL - EMB na taxa de fechamento por episodio, nas 4 "
                      "celulas do longe_fixo, com o Holm), PROPOSTOS para o adendo 9; aproximacao normal do t nao central, com a "
                      "conferencia por simulacao; sem gate",
            "fonte": {orq.rc._relativo(p): bv._sha(p) for p, _ in (*FONTES.values(), *METAS.values())},
            "script": {"arquivo": orq.rc._relativo(Path(__file__)), "sha256": bv._sha(Path(__file__))},
            "unidade": "a media das 4 celulas do lugar (uma vida por dono) da diferenca a - b na taxa por episodio, por unidade (base, k); "
                       "as celulas com a taxa None num dos bracos ficam fora, contadas",
            "dispersao_episodio": disp, "sigma_max_longe_fixo": sigma_max, "fonte_do_sigma_max": sigma_fonte, "folga": FOLGA,
            "sigma_planejamento": sigma, "alfa_familia": ALFA_FAMILIA, "n_familia": N_FAMILIA, "alfa_primeiro_passo": alfa_passo,
            "fonte_da_simulacao": plan_fonte, "poder_alvo": PODER_ALVO, "replicas": REPLICAS, "semente": SEMENTE,
            "por_k": por_k, "nivel_episodio": niveis, "g_pesa_memoria_m3": pesa, "visitas_lugar_lembrado_m3": visitas,
            "custo_m3_por_fonte_lugar": {n: custo[n] for n in sorted(custo)}, "parede_4_processos": parede,
            "estimativa_parede": estimativa, "vidas_por_unidade_c4": VIDAS_POR_UNIDADE, "bracos_c4": list(BRACOS_C4)}


if __name__ == "__main__":
    lidos = {nome: _ler(caminho, prefixo, nome) for nome, (caminho, prefixo) in FONTES.items()}
    d = calcular(lidos["c1"], lidos["c3"], {nome: _ler(caminho, prefixo, nome) for nome, (caminho, prefixo) in METAS.items()})
    bv._gravar(SAIDA, bv._dump(d))
    print(f"gravado {orq.rc._relativo(SAIDA)} (sha256 {bv._sha(SAIDA)})")
