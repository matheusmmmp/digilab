"""O poder e a margem do primario da C3, a escolha refeita so por evento (o adendo 8 do docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md;
a secao 4.5 da docs/TAREFA_V3_REDECIDIR_EVENTO.md): so le artefatos que estao no git, nenhuma vida, nenhum replay, nenhuma semente da
faixa 76101...76505. O sha256 de cada fonte e conferido contra o registrado no RESULTADO antes de qualquer conta:
  - a run da C1 (71101 a 71505, 3 600 vidas; RESULTADO, secao 13): o M0, o M2 e o M3* no `longe_fixo` e no longe, a fonte do sigma;
  - a run da C2 (75101 a 75505, 5 400 vidas; RESULTADO, secao 14): o M2 e o M2c no `longe_fixo`, no comedouro e no longe, so ao lado
    (o contraste de uma subchave no mesmo cerebro, a dispersao do comedouro da guarda, o custo por vida);
  - os `meta.json` das duas runs: o tempo de parede com 4 processos, para a estimativa das horas.

O primario P-R e M3*R - M3* na taxa de fechamento por episodio de fome (`episodios_fome.taxa`, a medida de A6.4), pareado por unidade
(base, k): a unidade e a media das 4 celulas do `longe_fixo` (uma vida por dono) da diferenca celula a celula. O M3*R nao existe; a
dispersao de um contraste da mesma medida, no mesmo lugar, entre bracos que diferem em um ou dois modulos, e lida na C1:
  - o M3* - M2 (o M-MEM), o M2 - M0 (o P1 e o P2) e o M3* - M0 no `longe_fixo`;
  - o M3* - M2 no longe sorteado (o S2), e, da C2, o M2c - M2 no `longe_fixo` e no comedouro, so ao lado (nao entram no sigma).
O sigma de planejamento e o maior dp das tres fontes do `longe_fixo` da C1, com a folga de 20 % da A5.9.

A margem sai do poder (a conta da A6.5, sem mudanca; as funcoes do adendo 6): para cada K, o menor delta com poder >= 0,8 do criterio (o
limite inferior do IC95 do t acima de 0), pela aproximacao normal do t nao central. Ao lado, por simulacao (2 000 replicas, semente 4242;
as diferencas M3* - M2 do `longe_fixo` da C1, centradas, na escala do sigma de planejamento, deslocadas e sorteadas com reposicao em K
unidades; o IC pela conta do metrics.ic_t): o poder na margem e, com o efeito verdadeiro 0, a fracao com o IC95 inteiro dentro de
(-margem, +margem) com o sigma de planejamento e com o sigma observado do M3* - M2, e a fracao com o IC inteiro acima de 0.
Saem tambem o nivel da taxa por episodio por braco e lugar, as decisoes sem o reflexo por vida (o denominador da P-SEGURA), as trocas de
meta de hoje do M3* e do M2 (o espaco do mecanismo) e o custo por vida.

Todos os numeros sao PROPOSTOS, SEM FONTE; nenhum e gate.

    python experiments/adendo8_poder_redecidir_evento.py
grava artifacts_v2_digibrain_prototipo/redecidir_evento/adendo8_poder.json
"""
from __future__ import annotations

import json
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
from digilab.config import CONFIG_PADRAO, TICKS_POR_DIA  # noqa: E402

PASTA_C1 = RAIZ / "artifacts_v2_digibrain_prototipo" / "longe_regular" / "run"
PASTA_C2 = RAIZ / "artifacts_v2_digibrain_prototipo" / "habito_intencao" / "run"
FONTES = {"c1": (PASTA_C1 / "medidas.json", "5a4fb207"),          # RESULTADO, 13
          "c2": (PASTA_C2 / "medidas.json", "93b136d6")}          # RESULTADO, 14
METAS = {"c1": (PASTA_C1 / "meta.json", "b2cb111a"),             # os meta.json das duas runs (o tempo de parede com 4 processos)
         "c2": (PASTA_C2 / "meta.json", "5ab56d67")}
SAIDA = RAIZ / "artifacts_v2_digibrain_prototipo" / "redecidir_evento" / "adendo8_poder.json"
FOLGA = a6.FOLGA                            # 1,2, como na A5.9 e na A6.5
KS = (50, 100, 150, 200, 300)               # unidades (base, k): multiplos de 5, as cinco bases da faixa
PODER_ALVO = a6.PODER_ALVO
REPLICAS = a6.REPLICAS
SEMENTE = a6.SEMENTE
BRACOS_C3 = ("M3", "M3R", "M2", "M2R")      # a RD-1 (o "M3" e o M3*)
LUGARES_C3 = ("longe_fixo", "comedouro", "longe")                     # a RD-5: o primario, a guarda e o descritivo
VIDAS_POR_UNIDADE = len(LUGARES_C3) * len(orq.DONOS) * len(BRACOS_C3)   # 48
UNIDADES = {"c1": 150, "c2": 150}
EPISODIO = a6.EPISODIO
DECISOES_POR_VIDA = orq.DIAS * TICKS_POR_DIA // CONFIG_PADRAO.intervalo_decisao_ticks


def _resumo(xs: list[float]) -> dict:
    return a7._resumo(xs)


def _ler(caminho: Path, prefixo: str, nome: str) -> dict:
    sha = bv._sha(caminho)
    if not sha.startswith(prefixo):
        raise RuntimeError(f"o {caminho.name} de {nome} nao e o registrado: {sha}")
    return json.loads(caminho.read_text(encoding="utf-8"))


def calcular(c1: dict, c2: dict, metas: dict) -> dict:
    fontes_sigma = {}
    for a, b in (("M3", "M2"), ("M2", "M0"), ("M3", "M0")):
        xs, fora = a7.diferencas(c1, "longe_fixo", a, b, EPISODIO, UNIDADES["c1"])
        fontes_sigma[f"c1|longe_fixo|{a} - {b}"] = (xs, fora)
    ao_lado = {}
    xs, fora = a7.diferencas(c1, "longe", "M3", "M2", EPISODIO, UNIDADES["c1"])
    ao_lado["c1|longe|M3 - M2"] = (xs, fora)
    for lu in ("longe_fixo", "comedouro"):
        xs, fora = a7.diferencas(c2, lu, "M2c", "M2", EPISODIO, UNIDADES["c2"])
        ao_lado[f"c2|{lu}|M2c - M2"] = (xs, fora)
    disp = {n: {**_resumo(xs), "celulas_fora": fora, "no_sigma": True} for n, (xs, fora) in fontes_sigma.items()}
    disp |= {n: {**_resumo(xs), "celulas_fora": fora, "no_sigma": False} for n, (xs, fora) in ao_lado.items()}
    sigma_max = max(disp[n]["dp"] for n in fontes_sigma)
    sigma = sigma_max * FOLGA
    plan_fonte = "c1|longe_fixo|M3 - M2"          # o contraste do cerebro do primario (o M3*), no lugar do primario
    difs = fontes_sigma[plan_fonte][0]
    escala = sigma / disp[plan_fonte]["dp"]
    plan = [x * escala for x in difs]
    rng = random.Random(SEMENTE)
    por_k = {}
    for k in KS:
        m = a6.margem_do_poder(sigma, k)
        r_poder = a7.simular(plan, m, k, rng)
        r_zero = a7.simular(plan, 0.0, k, rng)
        r_zero_obs = a7.simular(difs, 0.0, k, rng)        # o sigma observado do M3* - M2, sem a folga nem o maximo
        por_k[f"K={k}"] = {"margem": m, "poder_normal_na_margem": a6.poder_normal(m, sigma, k),
                           "poder_simulado_na_margem": sum(1 for a, _ in r_poder if a > 0) / REPLICAS,
                           "verdadeiro_0_ic_dentro_da_margem": sum(1 for a, b in r_zero if a > -m and b < m) / REPLICAS,
                           "verdadeiro_0_ic_acima_de_0": sum(1 for a, _ in r_zero if a > 0) / REPLICAS,
                           "verdadeiro_0_sigma_observado_ic_dentro_da_margem": sum(1 for a, b in r_zero_obs if a > -m and b < m) / REPLICAS,
                           "vidas": k * VIDAS_POR_UNIDADE}
    niveis = {f"c1|{lu}|{b}": a7.nivel(c1, lu, b, EPISODIO) for lu in ("longe_fixo", "longe") for b in ("M0", "M2", "M3")}
    niveis |= {f"c2|{lu}|{b}": a7.nivel(c2, lu, b, EPISODIO) for lu in ("longe_fixo", "comedouro", "longe") for b in ("M2", "M2c")}
    # as decisoes sem o reflexo por vida (o denominador da P-SEGURA) e as trocas de meta de hoje (o espaco do mecanismo), na C1
    sem_reflexo: dict = {}
    trocas: dict = {}
    for v in c1.values():
        if v["braco"] not in ("M2", "M3"):
            continue
        chave = f"{v['lugar']}|{v['braco']}"
        sem_reflexo.setdefault(chave, []).append((DECISOES_POR_VIDA - v["reflexos"]) / DECISOES_POR_VIDA)
        t = trocas.setdefault(chave, {"vidas": 0, "trocou": 0, "reflexo": 0, "dormir_sorteio": 0, "outra_unidade": 0})
        t["vidas"] += 1
        for tipo in v["metas"]["trocas"]:
            t["trocou"] += v["metas"]["fins"][tipo]["trocou"]
            for motivo in ("reflexo", "dormir_sorteio", "outra_unidade"):
                t[motivo] += v["metas"]["trocas"][tipo][motivo]
    for t in trocas.values():
        t["fora_do_reflexo"] = t["dormir_sorteio"] + t["outra_unidade"]
        t["frac_fora_do_reflexo"] = t["fora_do_reflexo"] / t["trocou"] if t["trocou"] else None
        t["trocou_por_vida"] = t["trocou"] / t["vidas"]
    sem_reflexo_resumo = {c: {"vidas": len(xs), "media": statistics.fmean(xs), "minimo": min(xs)} for c, xs in sorted(sem_reflexo.items())}
    custo: dict = {}
    for nome, med, bracos in (("c1", c1, ("M2", "M3")), ("c2", c2, ("M2",))):
        for v in med.values():
            if v["braco"] not in bracos:
                continue
            c = custo.setdefault(f"{nome}|{v['lugar']}|{v['braco']}", {"vidas": 0, "cpu": 0.0, "parede": 0.0})
            c["vidas"] += 1
            c["cpu"] += v["custo"]["vida_cpu"]
            c["parede"] += v["custo"]["vida_parede"]
    for c in custo.values():
        c["cpu_por_vida"] = c["cpu"] / c["vidas"]
        c["parede_por_vida_1_processo"] = c["parede"] / c["vidas"]
    parede = {}
    for nome, med in (("c1", c1), ("c2", c2)):
        m = metas[nome]
        parede[nome] = {"vidas": len(med), "processos": m["processos"], "vidas_parede_s": m["vidas_parede_s"],
                        "s_por_vida": m["vidas_parede_s"] / len(med)}
    estimativa = {f"K={k}": {"vidas": k * VIDAS_POR_UNIDADE,
                             **{f"parede_s_pela_{n}": k * VIDAS_POR_UNIDADE * p["s_por_vida"] for n, p in parede.items()}} for k in KS}
    return {"rotulo": "o poder e a margem do primario da C3 (P-R: M3*R - M3* na taxa de fechamento por episodio, nas 4 celulas do "
                      "longe_fixo), PROPOSTOS para o adendo 8; aproximacao normal do t nao central, com a conferencia por simulacao; "
                      "sem gate",
            "fonte": {orq.rc._relativo(p): bv._sha(p) for p, _ in (*FONTES.values(), *METAS.values())},
            "script": {"arquivo": orq.rc._relativo(Path(__file__)), "sha256": bv._sha(Path(__file__))},
            "unidade": "a media das 4 celulas do lugar (uma vida por dono) da diferenca a - b na taxa por episodio, por unidade (base, k); "
                       "as celulas com a taxa None num dos bracos ficam fora, contadas",
            "dispersao_episodio": disp, "sigma_max_longe_fixo_c1": sigma_max, "folga": FOLGA, "sigma_planejamento": sigma,
            "fonte_da_simulacao": plan_fonte, "poder_alvo": PODER_ALVO, "replicas": REPLICAS, "semente": SEMENTE,
            "por_k": por_k, "nivel_episodio": niveis, "decisoes_por_vida": DECISOES_POR_VIDA,
            "frac_decisoes_sem_reflexo_c1": sem_reflexo_resumo, "trocas_de_meta_c1": {c: trocas[c] for c in sorted(trocas)},
            "custo_por_fonte_lugar_braco": {n: custo[n] for n in sorted(custo)}, "parede_4_processos": parede,
            "estimativa_parede": estimativa, "vidas_por_unidade_c3": VIDAS_POR_UNIDADE}


if __name__ == "__main__":
    lidos = {nome: _ler(caminho, prefixo, nome) for nome, (caminho, prefixo) in FONTES.items()}
    d = calcular(lidos["c1"], lidos["c2"], {nome: _ler(caminho, prefixo, nome) for nome, (caminho, prefixo) in METAS.items()})
    bv._gravar(SAIDA, bv._dump(d))
    print(f"gravado {orq.rc._relativo(SAIDA)} (sha256 {bv._sha(SAIDA)})")
