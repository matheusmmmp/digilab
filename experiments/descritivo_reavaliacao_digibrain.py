"""O descritivo da reavaliacao do DigiBrain modular (66xxx; o #432), so com os artefatos que ja existem: le os medidas.json da
reavaliacao, do piloto do conserto e da avaliacao unica (o #420), todos no git. Exploratorio e pos hoc, como o descritivo #199: nenhuma
vida, nenhum replay, nenhuma faixa nova, nenhum teste de hipotese e nenhum gate. Nada muda na leitura do adendo 4 nem nos valores
PROPOSTOS.

As tres perguntas do Gerente (2026-10-29):
  1. o episodio contra a racao: por que o G-MVP fica em 0,81 por episodio e em 0,41 por racao nas mesmas vidas do M3*;
  2. o habito ao contrario (o G-ABLA-P2, M2 - M1 < 0): em que celulas e em que acoes, ao lado do #420 e do piloto;
  3. o A11 ao lado: os descritivos do item 1, so como comparacao.

Cada numero e uma soma ou uma media por vida (as vidas com valor), salvo onde dito. A identidade da secao 1 e exata sobre as somas:
  taxa da racao (somas) = (racoes fechadas por episodio fechado) x (taxa do episodio, somas) x (episodios por racao elegivel).

    python experiments/descritivo_reavaliacao_digibrain.py
grava artifacts_v2_digibrain_prototipo/descritivo_reavaliacao/descritivo.json
"""
from __future__ import annotations

import json
import math
import statistics
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402

PASTA = RAIZ / "artifacts_v2_digibrain_prototipo"
ENTRADA = PASTA / "reavaliacao" / "medidas.json"
RESULTADO = PASTA / "reavaliacao" / "resultado.json"
PILOTO = PASTA / "conserto" / "piloto" / "medidas.json"
AVALIACAO = PASTA / "avaliacao" / "medidas.json"
SAIDA = PASTA / "descritivo_reavaliacao" / "descritivo.json"
ROTULO = "descritivo exploratorio, pos hoc: sem teste de hipotese, sem gate e sem leitura de superioridade (como o #199)"
DIAS = 14
LIMIAR = orq.G_MVP["taxa_vida"]                       # 0,5: a vida "com a cadeia" (as duas medidas)
ACOES_R = ("comer", "explorar", "brincar", "aliviar")    # metrics.ACOES_R_POSSIVEL, na ordem da tabela


def _media(xs) -> float | None:
    xs = [x for x in xs if x is not None]
    return statistics.fmean(xs) if xs else None


def _mediana(xs) -> float | None:
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else None


def _razao(a: float, b: float) -> float | None:
    return a / b if b else None


def _faixa_d0(d0: int, g: dict) -> str:
    """a distancia da racao mais proxima na abertura do episodio: na visao, so no cheiro, alem do cheiro"""
    if d0 <= g["raio_visao"]:
        return "na_visao"
    return "no_cheiro" if d0 <= g["corte_d0"] else "alem_do_cheiro"


def _somar(dicts) -> dict:
    out: dict = {}
    for d in dicts:
        for k, n in d.items():
            out[k] = out.get(k, 0) + n
    return dict(sorted(out.items()))


def _refeicoes(v: dict) -> int:
    x = v["cadeia"]["refeicoes_por_dia"] * DIAS
    n = round(x)
    if abs(x - n) > 1e-6:
        raise RuntimeError(f"refeicoes de racao nao inteiras na vida {v['vida']}: {x!r}")
    return n


def bloco_racao_episodio(vs: list[dict]) -> dict:
    """a secao 1 sobre um conjunto de vidas: as duas fracoes do G-MVP, a tabela 2 x 2, as taxas, a identidade, as racoes por episodio,
    onde as racoes e os episodios nao fecham (a visao, a distancia, a janela, as trocas de meta) e as refeicoes"""
    if not vs:
        raise RuntimeError("bloco sem vidas")
    g = orq.geometria()
    t_r = [v["cadeia"]["taxa"] for v in vs]
    t_w = [v["cadeia_w"]["taxa"] for v in vs]
    t_e = [v["episodios_fome"]["taxa"] for v in vs]
    tabela = {"racao_e_episodio": 0, "so_episodio": 0, "so_racao": 0, "nenhuma": 0, "sem_valor": 0}
    for r, e in zip(t_r, t_e):
        if r is None or e is None:
            tabela["sem_valor"] += 1
        else:
            tabela[{(True, True): "racao_e_episodio", (False, True): "so_episodio", (True, False): "so_racao",
                    (False, False): "nenhuma"}[(r >= LIMIAR, e >= LIMIAR)]] += 1
    el = sum(v["cadeia"]["elegiveis"] for v in vs)
    fe = sum(v["cadeia"]["fechadas"] for v in vs)
    el_w = sum(v["cadeia_w"]["elegiveis"] for v in vs)
    fe_w = sum(v["cadeia_w"]["fechadas"] for v in vs)
    ep = sum(v["episodios_fome"]["n"] for v in vs)
    ef = sum(v["episodios_fome"]["fechados"] for v in vs)
    if el_w != el:
        raise RuntimeError("as racoes elegiveis da W fixa e da W(d) diferem")
    identidade = {"fechadas_por_episodio_fechado": _razao(fe, ef), "taxa_episodio": _razao(ef, ep),
                  "episodios_por_racao_elegivel": _razao(ep, el), "taxa_racao": _razao(fe, el)}
    if el and ef and ep:
        prod = identidade["fechadas_por_episodio_fechado"] * identidade["taxa_episodio"] * identidade["episodios_por_racao_elegivel"]
        if not math.isclose(prod, identidade["taxa_racao"], rel_tol=1e-12):
            raise RuntimeError("a identidade da secao 1 nao fecha")
    nj = {k: sum(v["racao_na_janela"][k] for v in vs) for k in ("elegiveis", "visiveis_em_k0", "entraram_na_visao")}
    if nj["elegiveis"] != el:
        raise RuntimeError("as racoes elegiveis da janela nao sao as da cadeia")
    nj["nunca_na_visao"] = nj["elegiveis"] - nj["visiveis_em_k0"] - nj["entraram_na_visao"]
    nj["frac"] = {k: _razao(nj[k], nj["elegiveis"]) for k in ("visiveis_em_k0", "entraram_na_visao", "nunca_na_visao")}
    nj["d_min_celulas_media_por_vida"] = _media(v["racao_na_janela"]["d_min_media_celulas"] for v in vs)
    faixas: dict = {f: {"n": 0, "fechados": 0, "janela_vencida": 0, "vida_acabou": 0, "saciado_por_outra_comida": 0}
                    for f in ("na_visao", "no_cheiro", "alem_do_cheiro")}
    for v in vs:
        for _k, d0, _w, _fim, motivo in v["episodios_fome"]["episodios"]:
            f = faixas[_faixa_d0(d0, g)]
            f["n"] += 1
            f["fechados" if motivo == "fechou" else motivo] += 1
    for f in faixas.values():
        f["taxa"] = _razao(f["fechados"], f["n"])
    if sum(f["n"] for f in faixas.values()) != ep:
        raise RuntimeError("os episodios da lista nao sao os contados")
    lat_depois = [x for v in vs for x in v["episodios_fome"]["latencias_depois_da_janela"]]
    refe = sum(_refeicoes(v) for v in vs)
    fora = sum(v["episodios_fome"]["fora_de_episodio"] for v in vs)
    sem_fechar = sum(v["episodios_fome"]["no_episodio_sem_fechar"] for v in vs)
    if ef + fora + sem_fechar != refe:
        raise RuntimeError("as refeicoes de racao nao somam as dos episodios e as de fora")
    out = {
        "vidas": len(vs),
        "frac_vidas_com_cadeia": {"racao": _razao(sum(1 for t in t_r if t is not None and t >= LIMIAR), sum(1 for t in t_r if t is not None)),
                                  "racao_w_d": _razao(sum(1 for t in t_w if t is not None and t >= LIMIAR),
                                                      sum(1 for t in t_w if t is not None)),
                                  "episodio": _razao(sum(1 for t in t_e if t is not None and t >= LIMIAR),
                                                     sum(1 for t in t_e if t is not None))},
        "tabela_2x2": tabela,
        "taxa_por_vida": {"racao": {"media": _media(t_r), "mediana": _mediana(t_r)},
                          "racao_w_d": {"media": _media(t_w), "mediana": _mediana(t_w)},
                          "episodio": {"media": _media(t_e), "mediana": _mediana(t_e)}},
        "somas": {"racoes_elegiveis": el, "racoes_fechadas": fe, "racoes_fechadas_w_d": fe_w, "episodios": ep, "episodios_fechados": ef},
        "identidade": identidade,
        "racoes_elegiveis_por_episodio": _razao(el, ep),
        "taxa_racao_w_d": _razao(fe_w, el),
        "racao_na_janela_w_d": nj,
        "episodios_por_distancia": faixas,
        "episodios_motivos": _somar(v["episodios_fome"]["motivos"] for v in vs),
        "episodios_oferta_mudou": sum(v["episodios_fome"]["oferta_mudou"] for v in vs),
        "latencia_depois_da_janela": {"n": len(lat_depois), "mediana_decisoes": _mediana(lat_depois)},
        "refeicoes_de_racao": {"total": refe, "fecharam_um_episodio": ef, "fora_de_episodio": fora, "no_episodio_sem_fechar": sem_fechar,
                               "por_dia_por_vida": refe / len(vs) / DIAS},
    }
    tem = {"fins" in v for v in vs}
    if tem == {True}:
        fins = _somar(v["fins"] for v in vs)
        out["fins_das_intencoes"] = {"total": fins, "por_vida": {k: n / len(vs) for k, n in fins.items()}}
    elif tem != {False}:
        raise RuntimeError("vidas com e sem os fins das intencoes no mesmo bloco")
    tem = {"cheiro" in v for v in vs}
    if tem == {True}:
        fb = _somar(v["cheiro"]["fins_busca"] for v in vs)
        out["fins_da_busca_pelo_cheiro"] = {"total": fb, "por_vida": {k: n / len(vs) for k, n in fb.items()}}
    elif tem != {False}:
        raise RuntimeError("vidas com e sem o cheiro no mesmo bloco")
    return out


def _por(vs: list[dict], fn) -> dict:
    """o bloco no total, por dono, por lugar e por celula"""
    return {"todas": fn(vs),
            "por_dono": {d: fn([v for v in vs if v["dono"] == d]) for d in orq.DONOS},
            "por_lugar": {lu: fn([v for v in vs if v["lugar"] == lu]) for lu in orq.LUGARES},
            "por_celula": {f"{d}|{lu}": fn([v for v in vs if v["dono"] == d and v["lugar"] == lu]) for d, lu in orq.CELULAS}}


def _sem_r(v: dict) -> dict | None:
    """os pares "ganhou, fica" cuja primeira decisao e de uma acao sem r possivel (dormir, chamar a atencao, ocioso, emburrar): todos do
    lado r <= 0. Derivados do total e da DX-5: o lado r > 0 e o mesmo nos dois (so as acoes com r possivel tem r > 0)."""
    tot, rp = v["repeticao"], v["repeticao_r_possivel"]["total"]
    if tot["n_pos"] != rp["n_pos"]:
        raise RuntimeError(f"o lado r > 0 do total e o da DX-5 diferem na vida {v['vida']}")
    n = tot["n_nao_pos"] - rp["n_nao_pos"]
    if n < 0:
        raise RuntimeError(f"pares sem r negativos na vida {v['vida']}")
    if n == 0:
        return {"pares": 0, "fica": None, "frac_dos_pares": 0.0}
    if rp["n_nao_pos"] == 0:
        fica = tot["p_nao_pos"]
    elif tot["p_pos"] is not None and rp["indice"] is not None:
        p_nao_rp = tot["p_pos"] - rp["indice"]
        fica = (tot["p_nao_pos"] * tot["n_nao_pos"] - p_nao_rp * rp["n_nao_pos"]) / n
    else:
        fica = None
    return {"pares": n, "fica": fica, "frac_dos_pares": n / (tot["n_pos"] + tot["n_nao_pos"])}


def bloco_habito(vs: list[dict]) -> dict:
    """o indice "ganhou, fica" de um braco num conjunto de vidas: o total (a medida do G-ABLA-P2), e, com a DX-5, por acao com r
    possivel e nos pares das acoes sem r"""
    out = {"vidas": len(vs), "indice": _media(v["repeticao"]["indice"] for v in vs),
           "p_pos": _media(v["repeticao"]["p_pos"] for v in vs), "p_nao_pos": _media(v["repeticao"]["p_nao_pos"] for v in vs),
           "pares_por_vida": _media(v["repeticao"]["n_pos"] + v["repeticao"]["n_nao_pos"] for v in vs)}
    tem = {"repeticao_r_possivel" in v for v in vs}
    if tem == {True}:
        out["r_possivel"] = {"indice": _media(v["repeticao_r_possivel"]["total"]["indice"] for v in vs)}
        for a in ACOES_R:
            out["r_possivel"][a] = {"indice": _media(v["repeticao_r_possivel"]["por_acao"][a]["indice"] for v in vs),
                                    "vidas_com_indice": sum(1 for v in vs if v["repeticao_r_possivel"]["por_acao"][a]["indice"] is not None),
                                    "pares_por_vida": _media(v["repeticao_r_possivel"]["por_acao"][a]["n_pos"]
                                                             + v["repeticao_r_possivel"]["por_acao"][a]["n_nao_pos"] for v in vs)}
        sr = [_sem_r(v) for v in vs]
        out["sem_r"] = {"fica": _media(s["fica"] for s in sr), "frac_dos_pares": _media(s["frac_dos_pares"] for s in sr),
                        "pares_por_vida": _media(s["pares"] for s in sr)}
    elif tem != {False}:
        raise RuntimeError("vidas com e sem a DX-5 no mesmo bloco")
    return out


def _diferenca(a: dict, b: dict) -> dict:
    """a - b, campo a campo, onde os dois tem valor"""
    out = {}
    for k, x in a.items():
        y = b.get(k)
        if isinstance(x, dict) and isinstance(y, dict):
            out[k] = _diferenca(x, y)
        elif isinstance(x, (int, float)) and isinstance(y, (int, float)) and k not in ("vidas", "vidas_com_indice"):
            out[k] = x - y
    return out


def habito(medidas: dict) -> dict:
    """a secao 2: o M1, o M2 e o M2 - M1 no total, por lugar e por celula"""
    m1 = [v for v in medidas.values() if v["braco"] == "M1"]
    m2 = [v for v in medidas.values() if v["braco"] == "M2"]
    if not m1 or not m2:
        raise RuntimeError("sem o M1 ou o M2")
    a, b = _por(m2, bloco_habito), _por(m1, bloco_habito)
    out = {"M1": b, "M2": a, "M2-M1": {}}
    for chave in ("todas", "por_dono", "por_lugar", "por_celula"):
        if chave == "todas":
            out["M2-M1"]["todas"] = _diferenca(a["todas"], b["todas"])
        else:
            out["M2-M1"][chave] = {k: _diferenca(a[chave][k], b[chave][k]) for k in a[chave]}
    return out


def _g_mvp_da_unidade(vs: list[dict], chave) -> float:
    """a fracao do G-MVP como o orquestrador: a media das celulas por unidade e a media das unidades"""
    unid: dict = {}
    for v in vs:
        unid.setdefault((v["base"], v["k"]), []).append(chave(v))
    return statistics.fmean(statistics.fmean(1.0 if x else 0.0 for x in xs) for xs in unid.values())


def conferir_com_o_resultado(medidas: dict, resultado: dict) -> dict:
    """as duas fracoes do G-MVP refeitas daqui batem com as do resultado.json da reavaliacao (falha alto se nao)"""
    m3 = [v for v in medidas.values() if v["braco"] == "M3"]
    racao = _g_mvp_da_unidade(m3, lambda v: v["com_cadeia"])
    ep = _g_mvp_da_unidade(m3, lambda v: v["episodios_fome"]["com_cadeia"])
    for nome, x, ref in (("G-MVP", racao, resultado["G-MVP"]["estimativa"]), ("G-MVP-EP", ep, resultado["G-MVP-EP"]["estimativa"])):
        if not math.isclose(x, ref, rel_tol=1e-12):
            raise RuntimeError(f"o {nome} daqui ({x!r}) nao e o do resultado.json ({ref!r})")
    return {"G-MVP": racao, "G-MVP-EP": ep}


def descrever(medidas: dict, resultado: dict, piloto: dict, avaliacao: dict) -> dict:
    decisoes = {sum(v["acoes"].values()) for v in medidas.values()}
    if len(decisoes) != 1:
        raise RuntimeError(f"vidas com numeros de decisoes diferentes: {sorted(decisoes)}")
    m3 = [v for v in medidas.values() if v["braco"] == "M3"]
    a11 = [v for v in medidas.values() if v["braco"] == "A11"]
    return {
        "rotulo": ROTULO,
        "fontes": {orq.rc._relativo(p): bv._sha(p) for p in (ENTRADA, RESULTADO, PILOTO, AVALIACAO)},
        "script": {"arquivo": orq.rc._relativo(Path(__file__)), "sha256": bv._sha(Path(__file__))},
        "vidas": len(medidas), "decisoes_por_vida": decisoes.pop(), "geometria": orq.geometria(),
        "conferencia_com_o_resultado": conferir_com_o_resultado(medidas, resultado),
        "1_episodio_contra_racao_M3": _por(m3, bloco_racao_episodio),
        "2_habito": {"reavaliacao": habito(medidas), "piloto_conserto": habito(piloto), "avaliacao_420": habito(avaliacao)},
        "3_A11_ao_lado": _por(a11, bloco_racao_episodio),
    }


def _ler(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


if __name__ == "__main__":
    d = descrever(_ler(ENTRADA), _ler(RESULTADO), _ler(PILOTO), _ler(AVALIACAO))
    bv._gravar(SAIDA, bv._dump(d))
    print(f"gravado {orq.rc._relativo(SAIDA)} (sha256 {bv._sha(SAIDA)})")
