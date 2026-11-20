"""O poder e a margem do contraste primario da C1, o longe regular (o adendo 6 do docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md;
a LR-3 da docs/TAREFA_V2_LONGE_REGULAR.md): so le o medidas.json da reavaliacao (66101 a 66505, as 7 200 vidas; no git), nenhuma vida,
nenhum replay, nenhuma faixa nova. O sha256 da fonte e conferido contra o registrado no RESULTADO (secao 8) antes de qualquer conta.

O contraste e M3* - M2 na taxa de fechamento por episodio (o G-MVP-EP, A3.3), pareado por unidade (base, k): a unidade e a media das 4
celulas do lugar (uma vida por dono) da diferenca celula a celula, como o G-ABLA-MEM da reavaliacao. O longe_fixo ainda nao existe;
a dispersao dele e lida em dois lugares que existem:
  - o longe sorteado (a mesma distancia, os mesmos donos; o lugar mais parecido);
  - o comedouro (o lugar fixo, onde a memoria pesa).
O sigma de planejamento e o maior dos dois, com a folga de 20 % da A5.9 (o sigma de 50 unidades tambem e estimado).

A margem sai do poder: para cada K (unidades), o menor efeito delta com poder >= 0,8 do criterio (o limite inferior do IC95 do t acima
de 0), pela aproximacao normal do t nao central da A5.6 (um pouco otimista com poucas unidades). Ao lado, duas conferencias por
simulacao (2 000 replicas, semente 4242; as 50 diferencas por unidade do longe, centradas, na escala do sigma de planejamento, deslocadas
e sorteadas com reposicao em K unidades; o IC pela conta do metrics.ic_t):
  - o poder com o efeito verdadeiro igual a margem;
  - o "aproximadamente 0" do longe sorteado (a C1-E1): a fracao das replicas com o IC95 inteiro dentro de (-margem, +margem), e a com o
    IC95 inteiro abaixo de 0, com o efeito verdadeiro 0 e com o observado na reavaliacao (aqui com o sigma do proprio longe).
Saem tambem a mesma diferenca por racao no comedouro (a medida do G-ABLA-MEM, +0,136), o d0 dos episodios do longe por braco, a G-PESA
da memoria no longe e o custo por vida.

Todos os numeros sao PROPOSTOS, SEM FONTE; nenhum e gate.

    python experiments/adendo6_poder_longe_regular.py
grava artifacts_v2_digibrain_prototipo/longe_regular/adendo6_poder.json
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

import bancada_v2 as bv  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402
from digilab.metrics import assimetria_g1, ic_t, quantil_t  # noqa: E402

ENTRADA = RAIZ / "artifacts_v2_digibrain_prototipo" / "reavaliacao" / "medidas.json"
SHA_ENTRADA = "73ae8a8a"                    # o prefixo registrado no RESULTADO, secao 8 (o medidas.json da reavaliacao)
SAIDA = RAIZ / "artifacts_v2_digibrain_prototipo" / "longe_regular" / "adendo6_poder.json"
FOLGA = 1.2                                 # o sigma 20 % maior, como na A5.9
KS = (50, 100, 150, 200, 300, 450)          # unidades (base, k): multiplos de 5, as cinco bases da faixa
PODER_ALVO = 0.8
REPLICAS = 2000
SEMENTE = 4242
BRACOS_C1 = ("M0", "M2", "M3")              # a LR-4
VIDAS_POR_UNIDADE = 2 * len(orq.DONOS) * len(BRACOS_C1)   # longe_fixo e longe, os 4 donos, os 3 bracos
FAIXAS = ("na_visao", "no_cheiro", "alem_do_cheiro")
EPISODIO = lambda v: v["episodios_fome"]["taxa"]   # noqa: E731
RACAO = lambda v: v["cadeia"]["taxa"]              # noqa: E731


def _phi(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def poder_normal(delta: float, sigma: float, k: int) -> float:
    """P(o limite inferior do IC95 do t > 0) com o efeito verdadeiro delta: 1 - Phi(t_0,975;K-1 - (delta / sigma) raiz(K)) (a A5.6)"""
    return 1.0 - _phi(quantil_t(k - 1, 0.95) - delta / sigma * math.sqrt(k))


def margem_do_poder(sigma: float, k: int) -> float:
    """o menor delta com poder_normal >= PODER_ALVO, por bissecao (o poder cresce com delta)"""
    lo, hi = 0.0, 1.0
    if poder_normal(hi, sigma, k) < PODER_ALVO:
        raise RuntimeError(f"nem delta = 1 chega ao poder alvo com K = {k}")
    for _ in range(100):
        meio = (lo + hi) / 2.0
        lo, hi = (meio, hi) if poder_normal(meio, sigma, k) < PODER_ALVO else (lo, meio)
    return hi


def diferencas(medidas: dict, lugar: str, a: str, b: str, f) -> list[float]:
    """a - b na medida f, celula a celula, com a media das 4 celulas do lugar por unidade (base, k)"""
    vidas: dict = {}
    for v in medidas.values():
        if v["lugar"] == lugar and v["braco"] in (a, b):
            x = f(v)
            if x is None:
                raise RuntimeError(f"{v['vida']}: a medida sem valor")
            chave = ((v["base"], v["k"], v["dono"]), v["braco"])
            if chave in vidas:
                raise RuntimeError(f"vida repetida: {v['vida']}")
            vidas[chave] = x
    por: dict = {}
    for (celula, braco), x in vidas.items():
        if braco == a:
            if (celula, b) not in vidas:
                raise RuntimeError(f"a vida {b} do par {celula} falta")
            por.setdefault(celula[:2], []).append(x - vidas[(celula, b)])
    if len(por) != 50 or any(len(xs) != len(orq.DONOS) for xs in por.values()):
        raise RuntimeError("as unidades da reavaliacao nao sao 50 com as quatro celulas do lugar")
    return [statistics.fmean(xs) for _, xs in sorted(por.items())]


def nivel(medidas: dict, lugar: str, braco: str, f) -> list[float]:
    """a media das 4 celulas do lugar por unidade, num braco"""
    por: dict = {}
    for v in medidas.values():
        if v["lugar"] == lugar and v["braco"] == braco:
            por.setdefault((v["base"], v["k"]), []).append(f(v))
    if len(por) != 50 or any(len(xs) != len(orq.DONOS) for xs in por.values()):
        raise RuntimeError("as unidades da reavaliacao nao sao 50 com as quatro celulas do lugar")
    return [statistics.fmean(xs) for _, xs in sorted(por.items())]


def _resumo(xs: list[float]) -> dict:
    ic = ic_t(xs)
    return {"unidades": len(xs), "media": ic["media"], "dp": ic["dp"], "ic95_t": [ic["ic_inferior"], ic["ic_superior"]],
            "g1": assimetria_g1(xs)}


def simular(difs: list[float], verdadeiro: float, k: int, rng: random.Random) -> list[tuple[float, float]]:
    """as diferencas centradas e deslocadas para o efeito verdadeiro, K sorteadas com reposicao; o IC95 do t (a conta do metrics.ic_t,
    com o quantil calculado uma vez por K) em cada replica"""
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


def calcular(medidas: dict) -> dict:
    difs = {lu: diferencas(medidas, lu, "M3", "M2", EPISODIO) for lu in ("longe", "comedouro")}
    disp = {lu: _resumo(xs) for lu, xs in difs.items()}
    sigma = max(d["dp"] for d in disp.values()) * FOLGA
    escala = sigma / disp["longe"]["dp"]
    plan = [x * escala for x in difs["longe"]]
    obs = disp["longe"]["media"]
    rng = random.Random(SEMENTE)
    por_k = {}
    for k in KS:
        m = margem_do_poder(sigma, k)
        r_poder = simular(plan, m, k, rng)
        linha = {"margem": m, "poder_normal_na_margem": poder_normal(m, sigma, k),
                 "poder_simulado_na_margem": sum(1 for a, _ in r_poder if a > 0) / REPLICAS,
                 "vidas": k * VIDAS_POR_UNIDADE, "sorteado": {}}
        for rotulo, verdadeiro in (("verdadeiro_0", 0.0), ("verdadeiro_observado", obs)):
            r = simular(difs["longe"], verdadeiro, k, rng)
            linha["sorteado"][rotulo] = {"ic_dentro_da_margem": sum(1 for a, b in r if a > -m and b < m) / REPLICAS,
                                         "ic_abaixo_de_0": sum(1 for _, b in r if b < 0) / REPLICAS,
                                         "ic_acima_de_0": sum(1 for a, _ in r if a > 0) / REPLICAS}
        por_k[f"K={k}"] = linha
    # o d0 dos episodios do longe sorteado por braco (somas sobre as vidas), a G-PESA da memoria e o custo por vida
    g = orq.geometria()
    faixas: dict = {}
    custo: dict = {}
    for v in medidas.values():
        if v["braco"] not in BRACOS_C1:
            continue
        if v["lugar"] == "longe":
            fx = faixas.setdefault(v["braco"], {x: {"n": 0, "fechados": 0} for x in FAIXAS})
            for _k, d0, _w, _fim, motivo in v["episodios_fome"]["episodios"]:
                x = "na_visao" if d0 <= g["raio_visao"] else ("no_cheiro" if d0 <= g["corte_d0"] else "alem_do_cheiro")
                fx[x]["n"] += 1
                fx[x]["fechados"] += motivo == "fechou"
        c = custo.setdefault(v["lugar"], {"vidas": 0, "cpu": 0.0, "parede": 0.0})
        c["vidas"] += 1
        c["cpu"] += v["custo"]["vida_cpu"]
        c["parede"] += v["custo"]["vida_parede"]
    for fx in faixas.values():
        for x in fx.values():
            x["taxa"] = x["fechados"] / x["n"] if x["n"] else None
    for c in custo.values():
        c["cpu_por_vida"] = c["cpu"] / c["vidas"]
        c["parede_por_vida_1_processo"] = c["parede"] / c["vidas"]
    return {"rotulo": "o poder e a margem do contraste primario da C1 (M3* - M2, por episodio, so no longe_fixo), PROPOSTOS para o "
                      "adendo 6; aproximacao normal do t nao central, com a conferencia por simulacao; sem gate",
            "fonte": {orq.rc._relativo(ENTRADA): bv._sha(ENTRADA)},
            "script": {"arquivo": orq.rc._relativo(Path(__file__)), "sha256": bv._sha(Path(__file__))},
            "unidade": "a media das 4 celulas do lugar (uma vida por dono) da diferenca M3 - M2, por unidade (base, k)",
            "M3_menos_M2_por_episodio": disp,
            "M3_menos_M2_por_racao_comedouro": _resumo(diferencas(medidas, "comedouro", "M3", "M2", RACAO)),
            "folga": FOLGA, "sigma_planejamento": sigma, "poder_alvo": PODER_ALVO, "replicas": REPLICAS, "semente": SEMENTE,
            "por_k": por_k, "longe_por_d0": faixas,
            "g_pesa_memoria_M3_longe": _resumo(nivel(medidas, "longe", "M3", lambda v: v["influencia"]["memoria"])),
            "custo_por_lugar": {lu: custo[lu] for lu in sorted(custo)}, "vidas_por_unidade_c1": VIDAS_POR_UNIDADE}


if __name__ == "__main__":
    sha = bv._sha(ENTRADA)
    if not sha.startswith(SHA_ENTRADA):
        raise RuntimeError(f"o medidas.json da reavaliacao nao e o registrado: {sha}")
    d = calcular(json.loads(ENTRADA.read_text(encoding="utf-8")))
    bv._gravar(SAIDA, bv._dump(d))
    print(f"gravado {orq.rc._relativo(SAIDA)} (sha256 {bv._sha(SAIDA)})")
