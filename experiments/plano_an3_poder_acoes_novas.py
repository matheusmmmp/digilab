"""O poder e a margem da guarda G-COMEDOURO-AN da AN4, a run unica do passeio (docs/PLANO_ANALISE_V3_ACOES_NOVAS.md, secoes 6 e 9; a
secao 4 da docs/TAREFA_V3_ACOES_NOVAS.md): so le artefatos que estao no git, nenhuma vida, nenhum replay, nenhuma semente da faixa
78101...78505. O sha256 de cada fonte e conferido contra o registrado no RESULTADO antes de qualquer conta:
  - a run da C4 (77101 a 77505, 14 400 vidas; docs/RESULTADO_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md, secao 16): o `medidas.json.gz` (o
    descomprimido tem o sha256 do `meta.json`) e o `meta.json` (o tempo de parede com 4 processos).

O braco LAB da AN4 e o REL da C4 (`SUBCHAVES_C4["REL"]`, a configuracao do pet de teste); o LAB+P e o mesmo com a `passeio` ligada. O
LAB+P nao existe. A dispersao de um contraste da mesma medida (a taxa de fechamento por episodio de fome, `episodios_fome.taxa`, a de A6.4
do plano do prototipo), na mesma unidade (base, k) e com a media das 4 celulas de um lugar, e lida na C4, entre o REL e os bracos que
diferem dele numa subchave ou num controle da memoria:
  - no comedouro (o lugar da guarda): REL+F - REL (uma subchave a mais por cima do REL, o desenho do LAB+P - LAB), REL - RELsN, REL - REC,
    REL - EMB; ao lado, sem entrar no sigma, o REL - SEM (a memoria inteira tirada, nao uma subchave);
  - no `longe_fixo` (a secundaria): os mesmos, so ao lado.
O sigma de planejamento e o maior dp das quatro fontes do comedouro, com a folga de 20 % da A5.9.

A margem sai do poder (a conta da A6.5, um contraste so, alfa 0,025 unilateral): para cada K, o menor delta com poder >= 0,8 de o limite
do IC95 do t ficar do lado do efeito (aqui, o limite superior abaixo de 0 com o efeito verdadeiro -delta), pela aproximacao normal do t
nao central. Por simulacao (2 000 replicas, semente 4242; as diferencas REL+F - REL do comedouro, centradas, na escala do sigma de
planejamento, deslocadas e sorteadas com reposicao em K unidades): o poder em -delta da classe "< 0" de A6.6 (o limite superior abaixo de 0
e o IC fora de (-delta, +delta)), o falso "< 0" com o efeito verdadeiro 0, e, com o efeito verdadeiro 0, a fracao com o IC95 inteiro dentro
de (-delta, +delta), com o sigma de planejamento e com o observado.

Saem tambem o nivel da taxa por episodio e da fracao de decisoes `explorar` no REL por lugar, a dispersao do REL+F - REL na fracao
`explorar` (a escala de um contraste de comportamento, so contexto do movimento, que a C4 nao mede), os episodios por vida, o custo por vida
do REL e a estimativa de parede.

Todos os numeros sao PROPOSTOS, SEM FONTE; nenhum e gate.

    python experiments/plano_an3_poder_acoes_novas.py
grava artifacts_v3_acoes_novas/plano_an3_poder.json
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
import adendo7_poder_habito_intencao as a7  # noqa: E402
import adendo9_poder_memoria_autobio as a9  # noqa: E402
import bancada_v2 as bv  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402
from digilab.metrics import quantil_t  # noqa: E402

PASTA_C4 = RAIZ / "artifacts_v2_digibrain_prototipo" / "memoria_autobio" / "run"
MEDIDAS_C4 = (PASTA_C4 / "medidas.json.gz", "8b48d0a2", "869ff397")   # RESULTADO, 16: o .gz e o descomprimido
META_C4 = (PASTA_C4 / "meta.json", "6315784c")
SAIDA = RAIZ / "artifacts_v3_acoes_novas" / "plano_an3_poder.json"
FOLGA = a6.FOLGA                            # 1,2, como na A5.9 e na A6.5
KS = (50, 100, 150, 200, 300, 400)          # unidades (base, k): multiplos de 5, as cinco bases da faixa
PODER_ALVO = a6.PODER_ALVO
REPLICAS = a6.REPLICAS
SEMENTE = a6.SEMENTE
ALFA = 0.025                                # unilateral, um contraste so (o da guarda das C3 e C4)
BRACOS_AN4 = ("LAB", "LAB+P")
LUGARES_AN4 = ("comedouro", "longe_fixo")   # a guarda e a secundaria
VIDAS_POR_UNIDADE = len(LUGARES_AN4) * len(orq.DONOS) * len(BRACOS_AN4)   # 16
UNIDADES_C4 = 200
VIDAS_C4 = 14400
EPISODIO = a6.EPISODIO
EXPLORAR = lambda v: v["exploracao"]                                    # noqa: E731
N_EPISODIOS = lambda v: len(v["episodios_fome"]["episodios"])           # noqa: E731
CONTRASTES_SIGMA = (("REL+F", "REL"), ("REL", "RELsN"), ("REL", "REC"), ("REL", "EMB"))
AO_LADO = (("REL", "SEM"),)


def _sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def ler_medidas() -> dict:
    caminho, pre_gz, pre_json = MEDIDAS_C4
    bruto = caminho.read_bytes()
    if not _sha_bytes(bruto).startswith(pre_gz):
        raise RuntimeError(f"o {caminho.name} da C4 nao e o registrado: {_sha_bytes(bruto)}")
    texto = gzip.decompress(bruto)
    if not _sha_bytes(texto).startswith(pre_json):
        raise RuntimeError(f"o medidas.json da C4 descomprimido nao e o registrado: {_sha_bytes(texto)}")
    return json.loads(texto)


def ler_meta() -> dict:
    caminho, prefixo = META_C4
    return a9._ler(caminho, prefixo, "c4")


def simular(difs: list[float], verdadeiro: float, k: int, margem: float, rng: random.Random) -> dict:
    """a simulacao da A6.5, lida pela classe de A6.6: em cada replica, K unidades sorteadas com reposicao das diferencas centradas e
    deslocadas para o efeito verdadeiro; o IC95 do t; a classe "< 0" (o limite superior abaixo de 0 e o IC fora de (-margem, +margem)) e o
    "dentro da margem" (o IC inteiro em (-margem, +margem))"""
    m = statistics.fmean(difs)
    base = [x - m + verdadeiro for x in difs]
    t95 = quantil_t(k - 1, 0.95)
    menor, dentro = 0, 0
    for _ in range(REPLICAS):
        xs = [rng.choice(base) for _ in range(k)]
        media, dp = statistics.fmean(xs), statistics.stdev(xs)
        meia = t95 * dp / math.sqrt(k)
        lo, hi = media - meia, media + meia
        dentro_ = lo > -margem and hi < margem
        dentro += dentro_
        menor += hi < 0 and not dentro_
    return {"classe_menor_que_0": menor / REPLICAS, "ic_dentro_da_margem": dentro / REPLICAS}


def calcular(c4: dict, meta: dict) -> dict:
    if len(c4) != VIDAS_C4:
        raise RuntimeError(f"a C4 tem {len(c4)} vidas, nao {VIDAS_C4}")
    disp: dict = {}
    for lugar in LUGARES_AN4:
        for a, b in CONTRASTES_SIGMA + AO_LADO:
            xs, fora = a7.diferencas(c4, lugar, a, b, EPISODIO, UNIDADES_C4)
            disp[f"c4|{lugar}|{a} - {b}"] = {**a7._resumo(xs), "celulas_fora": fora,
                                              "no_sigma": lugar == "comedouro" and (a, b) in CONTRASTES_SIGMA}
    fontes_sigma = [n for n, d in disp.items() if d["no_sigma"]]
    sigma_max = max(disp[n]["dp"] for n in fontes_sigma)
    sigma_fonte = max(fontes_sigma, key=lambda n: disp[n]["dp"])
    sigma = sigma_max * FOLGA
    plan_fonte = "c4|comedouro|REL+F - REL"         # a subchave a mais por cima do REL, o desenho do LAB+P - LAB
    difs = a7.diferencas(c4, "comedouro", "REL+F", "REL", EPISODIO, UNIDADES_C4)[0]
    plan = [x * sigma / disp[plan_fonte]["dp"] for x in difs]
    rng = random.Random(SEMENTE)
    por_k = {}
    for k in KS:
        m = a9.margem_do_poder(sigma, k, ALFA)
        no_dano = simular(plan, -m, k, m, rng)
        no_zero = simular(plan, 0.0, k, m, rng)
        no_zero_obs = simular(difs, 0.0, k, m, rng)
        por_k[f"K={k}"] = {"margem": m, "poder_normal_na_margem": a9.poder_normal(m, sigma, k, ALFA),
                           "dano_igual_a_margem_classe_menor_que_0": no_dano["classe_menor_que_0"],
                           "verdadeiro_0_classe_menor_que_0": no_zero["classe_menor_que_0"],
                           "verdadeiro_0_ic_dentro_da_margem": no_zero["ic_dentro_da_margem"],
                           "verdadeiro_0_sigma_observado_ic_dentro_da_margem": no_zero_obs["ic_dentro_da_margem"],
                           "vidas": k * VIDAS_POR_UNIDADE}
    niveis = {f"c4|{lu}|REL": {"episodio": a7.nivel(c4, lu, "REL", EPISODIO), "explorar": a7.nivel(c4, lu, "REL", EXPLORAR),
                               "episodios_por_vida": a7.nivel(c4, lu, "REL", N_EPISODIOS)} for lu in LUGARES_AN4}
    explorar = {f"c4|{lu}|REL+F - REL": a7._resumo(a7.diferencas(c4, lu, "REL+F", "REL", EXPLORAR, UNIDADES_C4)[0])
                for lu in LUGARES_AN4}
    custo = {"vidas": 0, "cpu": 0.0}
    for v in c4.values():
        if v["braco"] == "REL" and v["lugar"] in LUGARES_AN4:
            custo["vidas"] += 1
            custo["cpu"] += v["custo"]["vida_cpu"]
    custo["cpu_por_vida"] = custo["cpu"] / custo["vidas"]
    parede = {"vidas": VIDAS_C4, "processos": meta["processos"], "vidas_parede_s": meta["vidas_parede_s"],
              "s_por_vida": meta["vidas_parede_s"] / VIDAS_C4}
    estimativa = {f"K={k}": {"vidas": k * VIDAS_POR_UNIDADE, "parede_s_pela_c4": k * VIDAS_POR_UNIDADE * parede["s_por_vida"]}
                  for k in KS}
    return {"rotulo": "o poder e a margem da guarda G-COMEDOURO-AN (LAB+P - LAB na taxa de fechamento por episodio, nas 4 celulas do "
                      "comedouro), PROPOSTOS para o PLANO_ANALISE_V3_ACOES_NOVAS; aproximacao normal do t nao central, com a "
                      "conferencia por simulacao; sem gate",
            "fonte": {orq.rc._relativo(MEDIDAS_C4[0]): bv._sha(MEDIDAS_C4[0]), orq.rc._relativo(META_C4[0]): bv._sha(META_C4[0])},
            "script": {"arquivo": orq.rc._relativo(Path(__file__)), "sha256": bv._sha(Path(__file__))},
            "unidade": "a media das 4 celulas do lugar (uma vida por dono) da diferenca a - b na medida, por unidade (base, k); as "
                       "celulas com a taxa None num dos bracos ficam fora, contadas",
            "dispersao_episodio": disp, "sigma_max_comedouro": sigma_max, "fonte_do_sigma_max": sigma_fonte, "folga": FOLGA,
            "sigma_planejamento": sigma, "alfa": ALFA, "fonte_da_simulacao": plan_fonte, "poder_alvo": PODER_ALVO,
            "replicas": REPLICAS, "semente": SEMENTE, "por_k": por_k, "niveis_rel": niveis,
            "dispersao_explorar_contexto": explorar, "custo_rel": custo, "parede_4_processos_c4": parede,
            "estimativa_parede": estimativa, "vidas_por_unidade_an4": VIDAS_POR_UNIDADE, "bracos_an4": list(BRACOS_AN4),
            "lugares_an4": list(LUGARES_AN4)}


if __name__ == "__main__":
    d = calcular(ler_medidas(), ler_meta())
    bv._gravar(SAIDA, bv._dump(d))
    print(f"gravado {orq.rc._relativo(SAIDA)} (sha256 {bv._sha(SAIDA)})")
