"""O poder e a margem dos primarios da LONGE_GEOMETRIA (docs/PLANO_ANALISE_V3_LONGE_GEOMETRIA.md, secao 6): so le o medidas.json da C1
(71101 a 71505, 3 600 vidas) e o da C4 (77101 a 77505, 14 400 vidas, no git como medidas.json.gz), nenhuma vida, nenhum replay, nenhuma
faixa nova. O sha256 de cada fonte e conferido contra o registrado no RESULTADO (secoes 13 e 16) antes de qualquer conta.

Os primarios (secao 5) sao interacoes: o ganho da memoria (A - B por episodio, a media das 4 celulas por unidade) no `longe_fixo` menos o
mesmo ganho no `longe_ancora`, pareados por unidade. O `longe_ancora` ainda nao existe; a dispersao da interacao e lida na interacao mais
parecida que existe, a do `longe_fixo` contra o longe sorteado, nas mesmas unidades:
  - I-M3: (M3* - M2) no `longe_fixo` - (M3* - M2) no longe, na C1 (150 unidades);
  - I-PAD: (REL - SEM) no `longe_fixo` - (REL - SEM) no longe, na C4 (200 unidades). O controle da LONGE_GEOMETRIA e o M2, nao o SEM;
    a C4 nao tem o M2, e o SEM e o braco dela mais perto de "sem memoria" (o episodio guardado e nunca lido, sem lugar lembrado).
O sigma de planejamento e o maior dos dois, com a folga de 20 % da A5.9 (a A6.5, como esta).

A margem sai do poder, como na A6.5: para cada K, o menor delta com poder >= 0,8 do criterio de A6.4 (o limite inferior do IC95 do t
acima de 0), pela aproximacao normal do t nao central; ao lado, a conferencia por simulacao (2 000 replicas, semente 4242; as diferencas
por unidade da proxy do I-M3, centradas, na escala do sigma de planejamento, deslocadas para delta e sorteadas com reposicao em K
unidades). O Holm da familia de dois (secao 5) pede o p de 0,0125 para o primeiro dos dois; a margem com o alfa do primeiro sai ao lado
(a conservadora).

Saem tambem as proxies observadas (a media da interacao fixo - sorteado em cada fonte), que dao a escala do que se procura, e o custo por
vida das duas runs.

Todos os numeros sao PROPOSTOS, SEM FONTE; nenhum e gate.

    python experiments/poder_longe_geometria.py
grava artifacts_v3_longe_geometria/poder.json
"""
from __future__ import annotations

import gzip
import hashlib
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

FONTES = {
    "c1": {"arquivo": RAIZ / "artifacts_v2_digibrain_prototipo" / "longe_regular" / "run" / "medidas.json", "sha_json": "5a4fb207",
           "par": ("M3", "M2"), "unidades": 150},
    "c4": {"arquivo": RAIZ / "artifacts_v2_digibrain_prototipo" / "memoria_autobio" / "run" / "medidas.json.gz", "sha_json": "869ff397",
           "par": ("REL", "SEM"), "unidades": 200},
}
SAIDA = RAIZ / "artifacts_v3_longe_geometria" / "poder.json"
FOLGA = 1.2                                   # A6.5 (a A5.9)
KS = (100, 150, 200, 300)                     # unidades (base, k): multiplos de 5, as cinco bases da faixa
PODER_ALVO = 0.8
ALFA_UNILATERAL, ALFA_HOLM_PRIMEIRO = 0.025, 0.0125
REPLICAS = 2000
SEMENTE = 4242
VIDAS_POR_UNIDADE = 4 * 4 * 4                 # 4 bracos x 4 donos x 4 lugares (secao 3.3)
EPISODIO = lambda v: v["episodios_fome"]["taxa"]   # noqa: E731


def ler(fonte: dict) -> tuple[dict, str]:
    """o medidas.json da fonte (descomprimido se .gz), com o sha256 do json conferido contra o registrado no RESULTADO"""
    bruto = fonte["arquivo"].read_bytes()
    texto = gzip.decompress(bruto) if fonte["arquivo"].suffix == ".gz" else bruto
    sha = hashlib.sha256(texto).hexdigest()
    if not sha.startswith(fonte["sha_json"]):
        raise RuntimeError(f"{fonte['arquivo']}: o medidas.json nao e o registrado no RESULTADO ({sha[:8]}, era {fonte['sha_json']})")
    return json.loads(texto), sha


def ganho_por_unidade(medidas: dict, lugar: str, a: str, b: str, n_unidades: int) -> dict:
    """{(base, k): a media nas 4 celulas do lugar de (a - b) na taxa por episodio, no mesmo dono}; falha alto com par faltando ou vida repetida"""
    vidas: dict = {}
    for v in medidas.values():
        if v["lugar"] == lugar and v["braco"] in (a, b):
            x = EPISODIO(v)
            if x is None:
                raise RuntimeError(f"{v['vida']}: a taxa por episodio sem valor")
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
    if len(por) != n_unidades or any(len(xs) != len(orq.DONOS) for xs in por.values()):
        raise RuntimeError(f"{lugar}: {len(por)} unidades, eram {n_unidades} com as quatro celulas")
    return {u: statistics.fmean(xs) for u, xs in por.items()}


def _resumo(xs: list[float]) -> dict:
    ic = ic_t(xs)
    return {"unidades": len(xs), "media": ic["media"], "dp": ic["dp"], "ic95_t": [ic["ic_inferior"], ic["ic_superior"]],
            "g1": assimetria_g1(xs)}


def poder_normal(delta: float, sigma: float, k: int, alfa: float = ALFA_UNILATERAL) -> float:
    """P(o limite inferior do IC (1 - 2 alfa) do t > 0) com o efeito verdadeiro delta (a A5.6, com o alfa do criterio)"""
    return 1.0 - a6._phi(quantil_t(k - 1, 1.0 - 2.0 * alfa) - delta / sigma * math.sqrt(k))


def margem_do_poder(sigma: float, k: int, alfa: float = ALFA_UNILATERAL) -> float:
    """o menor delta com poder_normal >= PODER_ALVO, por bissecao (o poder cresce com delta)"""
    lo, hi = 0.0, 1.0
    if poder_normal(hi, sigma, k, alfa) < PODER_ALVO:
        raise RuntimeError(f"nem delta = 1 chega ao poder alvo com K = {k}")
    for _ in range(100):
        meio = (lo + hi) / 2.0
        lo, hi = (meio, hi) if poder_normal(meio, sigma, k, alfa) < PODER_ALVO else (lo, meio)
    return hi


def calcular(fontes: dict) -> dict:
    """fontes: {"c1": (medidas, sha), "c4": (medidas, sha)}"""
    proxies, interacoes = {}, {}
    for nome, (medidas, _sha) in fontes.items():
        f = FONTES[nome]
        a, b = f["par"]
        fixo = ganho_por_unidade(medidas, "longe_fixo", a, b, f["unidades"])
        sort = ganho_por_unidade(medidas, "longe", a, b, f["unidades"])
        xs = [fixo[u] - sort[u] for u in sorted(fixo)]
        interacoes[nome] = xs
        proxies[nome] = {"contraste": f"({a} - {b}) no longe_fixo - ({a} - {b}) no longe, por unidade",
                         "ganho_no_longe_fixo": _resumo([fixo[u] for u in sorted(fixo)]),
                         "ganho_no_longe": _resumo([sort[u] for u in sorted(sort)]),
                         "interacao": _resumo(xs),
                         "correlacao_fixo_sorteado": statistics.correlation([fixo[u] for u in sorted(fixo)], [sort[u] for u in sorted(sort)])}
    sigma = max(p["interacao"]["dp"] for p in proxies.values()) * FOLGA
    base = interacoes["c1"]
    escala = sigma / proxies["c1"]["interacao"]["dp"]
    plan = [x * escala for x in base]
    rng = random.Random(SEMENTE)
    por_k = {}
    for k in KS:
        m = margem_do_poder(sigma, k)
        r = a6.simular(plan, m, k, rng)
        por_k[f"K={k}"] = {"margem": m, "margem_holm_primeiro": margem_do_poder(sigma, k, ALFA_HOLM_PRIMEIRO),
                           "poder_normal_na_margem": poder_normal(m, sigma, k),
                           "poder_simulado_na_margem": sum(1 for lo, _ in r if lo > 0) / a6.REPLICAS,
                           "vidas": k * VIDAS_POR_UNIDADE}
    custo = {}
    for nome, (medidas, _sha) in fontes.items():
        cpu = [v["custo"]["vida_cpu"] for v in medidas.values()]
        parede = [v["custo"]["vida_parede"] for v in medidas.values()]
        custo[nome] = {"vidas": len(cpu), "cpu_por_vida": statistics.fmean(cpu), "parede_por_vida_1_processo": statistics.fmean(parede)}
    return {"rotulo": "o poder e a margem dos primarios da LONGE_GEOMETRIA (I-M3 e I-PAD), PROPOSTOS para a secao 6 do plano; a "
                      "dispersao pela proxy fixo - sorteado da C1 e da C4; aproximacao normal do t nao central, com a conferencia por "
                      "simulacao; sem gate",
            "fonte": {orq.rc._relativo(FONTES[n]["arquivo"]): {"sha256_json": sha, "sha256_arquivo": bv._sha(FONTES[n]["arquivo"])}
                      for n, (_m, sha) in fontes.items()},
            "script": {"arquivo": orq.rc._relativo(Path(__file__)), "sha256": bv._sha(Path(__file__))},
            "unidade": "a media das 4 celulas do lugar (uma vida por dono) da diferenca entre os bracos, por unidade (base, k); a interacao "
                       "e a diferenca de duas dessas medias, na mesma unidade",
            "proxies": proxies, "folga": FOLGA, "sigma_planejamento": sigma, "poder_alvo": PODER_ALVO,
            "alfa_unilateral": ALFA_UNILATERAL, "alfa_holm_primeiro": ALFA_HOLM_PRIMEIRO, "replicas": a6.REPLICAS, "semente": SEMENTE,
            "por_k": por_k, "custo_por_fonte": custo, "vidas_por_unidade": VIDAS_POR_UNIDADE}


if __name__ == "__main__":
    lidas = {n: ler(f) for n, f in FONTES.items()}
    d = calcular(lidas)
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    bv._gravar(SAIDA, bv._dump(d))
    print(f"gravado {orq.rc._relativo(SAIDA)} (sha256 {bv._sha(SAIDA)})")
    print(json.dumps({"sigma": d["sigma_planejamento"], "proxies": {n: p["interacao"] for n, p in d["proxies"].items()},
                      "por_k": d["por_k"]}, indent=1, ensure_ascii=True))
