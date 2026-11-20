"""V2, CALIBRACAO-CEREBRO-C: a calibracao do cerebro C, Fly-like (docs/TAREFA_V2_CALIBRACAO_CEREBROS_B_C.md; grades e regras do adendo 1,
secao 1.2, de docs/PLANO_ANALISE_V2_COMPARACAO_CEREBROS.md, conferido pelo coordenador). Pela bancada com o C ligado
(experiments/cerebro_c_bancada.py, BancadaComC), nas unidades derivadas das bases 28101...28505 (K = 4, prefixo "comparacao-cerebros")
ou, na fumaca, nas sementes dos testes. As de validacao (29101...29505) e as do experimento maior nunca: o modo vem das sementes e recusa
o resto.

Etapas em cadeia (adendo 1.2), cada uma com a regra de escolha do adendo e a de reserva:
    C-A  passo  {32, 64, 128}        teto 4S, w0_info 0     P1 x {casado_frutas, descasado, mutavel}    regra da K-4 (estabilidade)
    C-B  teto   {1024, 4096, 16384}  o passo da C-A         P1 x as tres (o 4S reusa a C-A)             a mesma
    C-C  w0_info {256, 512, 768}     passo e teto escolhidos P2 x as tres (+ o w0_info 0, descritivo)   regra da K-3 (manipulacao)
    piloto  o "nao aprende" da secao 7 do plano, no P1 do ponto escolhido

Nas pecas comuns, o ponto do A da K2 (artifacts_v2_calibracao_conjunta/escolha.json): o ganho da consequencia. O C nao le a montagem
(ela e do cerebro A) nem a chave dos canais (no C eles sao a arquitetura). Nenhuma regra le a taxa_fruta_ruim nem um contraste entre
bracos ou cerebros (tarefa, secao 2). Teto de vidas: as da K2 do A (1260); a grade e contada antes de rodar e, se passar, nada roda.
Toda vida e gravada e rejogada do disco bit a bit (Bancada.conferir_replay); o replay das medidas tambem confere.

    python experiments/run_v2_calibracao_cerebro_c.py --config experiments/configs/v2_calibracao_cerebro_c/calibracao.json
"""
from __future__ import annotations

import argparse
import json
import math
import platform
import sys
import time
from dataclasses import replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import cerebro_c_bancada as cbc  # noqa: E402
import run_v2_calibracao_conjunta as k2  # noqa: E402
from digilab.config import CONFIG_CEREBRO_C_APRENDIZ, CONFIG_CONSEQUENCIA, CONFIG_PADRAO, TICKS_POR_DIA  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402

PLANO = "docs/PLANO_ANALISE_V2_COMPARACAO_CEREBROS.md"
TAREFA = "docs/TAREFA_V2_CALIBRACAO_CEREBROS_B_C.md"
SAIDA_PADRAO = "artifacts_v2_comparacao_cerebros/calibracao_C"
ESCOLHA_K2 = "artifacts_v2_calibracao_conjunta/escolha.json"     # o ponto do A da K2: as pecas comuns (o ganho)
META_K2 = "artifacts_v2_calibracao_conjunta/meta.json"           # o tempo da K2 do A (o teto de tempo e 4x)
PREFIXO = "comparacao-cerebros"                                  # adendo 1.2 e tarefa, secao 1
K_CALIBRACAO = 4
DIAS_PLANO = 14
DONO = "atencioso"
CONDICOES = ("casado_frutas", "descasado", "mutavel")
S = 1024
# adendo 1.2: as grades, em cadeia (sem grade cruzada), e o que fica fixo em cada etapa
GRADES_ADENDO = {"passo": (S // 32, S // 16, S // 8), "teto": (S, 4 * S, 16 * S), "w0_info": (S // 4, S // 2, 3 * S // 4)}
FIXOS_C_A = {"teto": 4 * S, "w0_info": 0}
W0_INFO_REFERENCIA = 0           # C-C: o w0_info 0, so descritivo (nao entra na regra)
LIMIAR_DECIDIDA = 0.069          # K-3: a mesma regua da K2 (artifacts_v1_memoria_espacos/espacos.json)
DIAS_K3 = 7                      # K-3: dias 1-7 (PLANO_CALIBRACAO_CONJUNTA_V2, secao 3.4)
LIMIAR_NAO_APRENDE = 0.01        # secao 7: a parte aprendida muda a escolha em menos de 1% das decisoes (PROPOSTO)
TETO_VIDAS = 1260                # tarefa, secao 1: as vidas que o A gastou na K2
FATOR_TEMPO = 4.0                # tarefa, secao 1: o teto de tempo e 4x o da K2 do A
CHAVES = {"descricao", "plano", "unidades", "sementes", "genomas", "dias", "orcamento", "sonda", "bootstrap", "grades", "saida"}


class GradeAcimaDoTeto(RuntimeError):
    """A grade passa do teto de vidas: pare e escreva um adendo antes (tarefa, secao 1)."""


def _dump(obj) -> str:
    return json.dumps(obj, indent=1, sort_keys=True, ensure_ascii=False, default=repr) + "\n"


def _gravar(caminho: Path, texto: str) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(texto, encoding="utf-8", newline="\n")


# ------------------------------------------------------------------ config, modo e unidades


def unidades_comparacao(bases, k_por_base: int) -> list[dict]:
    """A regra E3 da bancada (bv.unidades_derivadas) com o prefixo da comparacao: semente derivar_semente(PREFIXO, b, k) e genoma
    derivar_semente(PREFIXO + "-genoma", b, k). A bancada so aceita os prefixos dos planos dela, e ela nao muda nesta tarefa; a conta e a
    mesma, e falha alto com colisao ou com um valor numa faixa reservada."""
    if k_por_base < 1:
        raise ValueError("K precisa ser >= 1")
    bases = list(bases)
    if len(set(bases)) != len(bases):
        raise ValueError(f"base repetida: {bases}")
    out = [{"base": b, "k": k, "semente": derivar_semente(PREFIXO, b, k), "genoma": derivar_semente(f"{PREFIXO}-genoma", b, k)}
           for b in bases for k in range(k_por_base)]
    valores = [u["semente"] for u in out] + [u["genoma"] for u in out]
    if len(set(valores)) != len(valores):
        raise ValueError("colisao entre sementes e genomas derivados")
    for v in valores:
        if bv.na_faixa_reservada(v):
            raise ValueError(f"valor derivado {v} cai numa faixa reservada ({bv.na_faixa_reservada(v)})")
    return out


def modo_e_unidades(cfg: dict) -> tuple[str, list[dict]]:
    """fumaca (as sementes dos testes) ou calibracao (exatamente as bases 28101...28505, K = 4, 14 dias, as grades do adendo). O resto
    falha alto, as sementes de validacao da comparacao e as do experimento maior incluidas."""
    sobram = set(cfg) - CHAVES
    if sobram:
        raise ValueError(f"config: chaves desconhecidas {sorted(sobram)}")
    for k in ("dias", "orcamento", "sonda", "bootstrap"):
        if k not in cfg:
            raise ValueError(f"config: falta {k!r}")
    if ("sementes" in cfg) == ("unidades" in cfg):
        raise ValueError("config: ou 'sementes' (so na fumaca) ou 'unidades' (bases x K derivadas)")
    if "unidades" in cfg:
        u = cfg["unidades"]
        if set(u) != {"bases", "k"}:
            raise ValueError(f"unidades: so 'bases' e 'k' (o prefixo e o da comparacao, {PREFIXO!r}): {u}")
        bases = set(u["bases"])
        cal = set(bv.BASES_COMPARACAO["calibracao"])
        if bases != cal:
            raise bv.SementeSemPlano(f"bases {sorted(bases)}: so exatamente as de calibracao da comparacao {sorted(cal)}; a validacao "
                                     f"{bv.BASES_COMPARACAO['validacao']} e as dos outros planos nunca")
        modo = "calibracao"
        unidades = unidades_comparacao(u["bases"], int(u["k"]))
    else:
        bases = set(int(s) for s in cfg["sementes"]) | {int(g) for g in cfg.get("genomas", []) if g is not None}
        if not bases <= bv.SEMENTES_TESTE:
            raise bv.SementeSemPlano(f"sementes {sorted(bases - bv.SEMENTES_TESTE)}: na fumaca so as dos testes "
                                     f"{sorted(bv.SEMENTES_TESTE)}; a calibracao vai por 'unidades'")
        modo = "fumaca"
        unidades = [{"genoma": g, "semente": int(s), "base": None, "k": None} for g in cfg.get("genomas", [None]) for s in cfg["sementes"]]
    if modo == "calibracao":
        if cfg.get("plano") != PLANO or not (RAIZ / PLANO).is_file():
            raise bv.SementeSemPlano(f"calibracao: precisa do campo 'plano' = {PLANO!r}")
        if int(cfg["unidades"]["k"]) != K_CALIBRACAO:
            raise ValueError(f"calibracao: K = {K_CALIBRACAO} por base (adendo 1.2), nao {cfg['unidades']['k']}")
        if int(cfg["dias"]) != DIAS_PLANO:
            raise ValueError(f"calibracao: {DIAS_PLANO} dias, nao {cfg['dias']}")
        if "grades" in cfg:
            raise ValueError("calibracao: as grades sao as do adendo 1.2 (sem a chave 'grades')")
    return modo, unidades


def grades(cfg: dict) -> dict:
    g = {k: tuple(int(x) for x in v) for k, v in cfg.get("grades", {}).items()}
    sobram = set(g) - set(GRADES_ADENDO)
    if sobram:
        raise ValueError(f"grades desconhecidas: {sorted(sobram)}")
    return {**GRADES_ADENDO, **g}


def ganho_da_k2() -> int:
    """O ganho da consequencia do ponto do A da K2 (C-1: a fonte do sinal e comum)."""
    p = RAIZ / ESCOLHA_K2
    if not p.is_file():
        raise FileNotFoundError(f"{ESCOLHA_K2}: o ponto do A da K2 (o ganho comum) nao esta no disco")
    return int(json.loads(p.read_text(encoding="utf-8"))["ponto"]["ganho"])


def segundos_da_k2() -> float:
    p = RAIZ / META_K2
    if not p.is_file():
        raise FileNotFoundError(f"{META_K2}: o tempo da K2 do A (o teto de tempo) nao esta no disco")
    return float(json.loads(p.read_text(encoding="utf-8"))["segundos"])


def vidas_planejadas(gr: dict, n_unidades: int) -> dict:
    """As vidas da grade, contadas antes de rodar: C-A (P1), C-B sem o ponto que repete a C-A, C-C (P2) com o w0_info 0 de referencia. O
    piloto reusa as vidas do P1 no ponto escolhido (o w0_info nao age no P1, que nao tem informante)."""
    por_ponto = n_unidades * len(CONDICOES)
    c_b = len([t for t in gr["teto"] if t != FIXOS_C_A["teto"]])
    c_c = len(set(gr["w0_info"]) | {W0_INFO_REFERENCIA})
    return {"C-A": len(gr["passo"]) * por_ponto, "C-B": c_b * por_ponto, "C-C": c_c * por_ponto,
            "total": (len(gr["passo"]) + c_b + c_c) * por_ponto}


class Contador:
    """As vidas que a run gastou (cada vida de malha fechada; os replays de conferencia e de medida nao contam). Falha alto antes de
    passar do teto."""

    def __init__(self, teto: int) -> None:
        self.teto, self.n = teto, 0

    def gastar(self) -> None:
        if self.n + 1 > self.teto:
            raise GradeAcimaDoTeto(f"passaria de {self.teto} vidas")
        self.n += 1


# ------------------------------------------------------------------ a bancada do C num ponto e as vidas


def bancada_c(cfg: dict, ganho: int, passo: int, teto: int, w0_info: int) -> cbc.BancadaComC:
    cc = replace(CONFIG_CEREBRO_C_APRENDIZ, passo=int(passo), teto=int(teto), w0_info=int(w0_info))
    return cbc.BancadaComC(int(cfg["dias"]), int(cfg["orcamento"]), cfg_consequencia=replace(CONFIG_CONSEQUENCIA, ganho=int(ganho)),
                           cfg_cerebro_c=cc)


def estatisticas_c(cerebro, dias_k3: int) -> dict:
    """Do cerebro C da vida (o vivo, nao um replay): o teto e as sondas do aprendido e da informacao gravadas no motivo (contrato 1.1).
    A decisao k cai no tick k x intervalo (uma decisao por intervalo, como na K2)."""
    passo_t, fim = CONFIG_PADRAO.intervalo_decisao_ticks, dias_k3 * TICKS_POR_DIA
    mot = cerebro.motivos
    multi = [m for m in mot if m["u"] is not None]
    fr2 = fr2_apr = eleg = dec = 0
    for k, m in enumerate(mot):
        f = m.get("fruta")
        if f is None or len(f["presentes"]) < 2:
            continue
        fr2 += 1
        fr2_apr += bool(f["sonda"]["aprendido_decidiu"])
        if k * passo_t < fim and any(v != 0.0 for v in f["info"].values()):
            eleg += 1
            dec += bool(f["sonda"]["info_decidiu"])
    return {"pesos_no_teto": cerebro.pesos_no_teto(), "desvio_maximo": cerebro.desvio_maximo(), "pesos_mudaram": cerebro.pesos_mudaram(),
            "decisoes": len(mot), "aprendido_decidiu": sum(bool(m["sonda"]["aprendido_decidiu"]) for m in mot),
            "decisoes_com_escolha": len(multi), "aprendido_decidiu_com_escolha": sum(bool(m["sonda"]["aprendido_decidiu"]) for m in multi),
            "frutas_2mais": fr2, "frutas_2mais_aprendido_decidiu": fr2_apr,
            "k3_elegiveis": eleg, "k3_decididas_pela_informacao": dec}


def rodar_ponto(cfg: dict, bancada: cbc.BancadaComC, braco: str, unidades: list[dict], pasta: Path, contador: Contador) -> dict:
    """As vidas do braco nas tres condicoes, por unidade: gravadas, rejogadas do disco bit a bit, medidas (o replay da medida tambem
    confere) e com as estatisticas do C. Grava medidas.json; devolve {nome: medidas}."""
    t = time.perf_counter()
    medidas = {}
    for u in unidades:
        for mundo in CONDICOES:
            contador.gastar()
            v = bancada.vida(bv.EspecVida(DONO, braco, u["semente"], u["genoma"], mundo, cbc.CEREBRO_C))
            caminho = pasta / "vidas" / f"{v.nome}.jsonl"
            _gravar(caminho, v.motor.log.para_jsonl())
            bancada.conferir_replay(v, caminho.read_text(encoding="utf-8"))
            m = bancada.medir(v, cfg["sonda"])
            m["cerebro_c"] = estatisticas_c(bv.do_braco(v.motor.politica).cerebro, min(DIAS_K3, int(cfg["dias"])))
            m["unidade"] = {"base": u["base"], "k": u["k"], "semente": u["semente"], "genoma": u["genoma"]}
            medidas[v.nome] = m
    _gravar(pasta / "medidas.json", _dump(medidas))
    return {"medidas": medidas, "segundos": time.perf_counter() - t, "vidas": len(medidas)}


def _por_unidade(medidas: dict) -> dict:
    out: dict = {}
    for m in medidas.values():
        out.setdefault(m["unidade"]["semente"], []).append(m)
    return out


# ------------------------------------------------------------------ as regras do adendo


def resumo_estabilidade(medidas: dict, dias: int) -> dict:
    """K-4 num ponto: vidas com compartimento no teto e a razao da deriva (dia 14 / dia 7; a conta da K2, k2.razao_deriva) por condicao e
    a media das tres (a K-4 da K2, secao 3.3 do plano da calibracao conjunta). A razao das tres juntas (as 60 vidas numa conta so) fica
    so descritiva."""
    por = {}
    for mundo in CONDICOES:
        ms = [m for m in medidas.values() if m["mundo"] == mundo]
        derivas = [m["custo_da_plasticidade"]["deriva_por_dia"] for m in ms]
        teto = [m["cerebro_c"]["pesos_no_teto"] for m in ms]
        por[mundo] = {"vidas": len(ms), "vidas_no_teto": sum(t > 0 for t in teto), "pesos_no_teto": teto,
                      "razao_deriva": k2.razao_deriva(derivas, dias) if ms else None}
    razoes = [por[c]["razao_deriva"] for c in CONDICOES]
    todas = [m["custo_da_plasticidade"]["deriva_por_dia"] for m in medidas.values()]
    return {"por_condicao": por, "vidas_no_teto": sum(por[c]["vidas_no_teto"] for c in CONDICOES),
            "razao_media": (sum(razoes) / len(razoes)) if None not in razoes else None,
            "razao_juntas_descritiva": k2.razao_deriva(todas, dias) if todas else None}


def regra_estabilidade(pontos: dict) -> dict:
    """K-4 (adendo 1.2): entre os pontos sem nenhuma vida com compartimento no teto, o de menor razao da deriva; empate, o menor valor.
    Se nenhum escapar do teto: o de menos vidas no teto; desempate pela menor razao, depois o menor valor."""
    def razao(v):
        r = pontos[v]["razao_media"]
        return math.inf if r is None else r
    ordem = sorted(pontos)
    sem_teto = [v for v in ordem if pontos[v]["vidas_no_teto"] == 0]
    if sem_teto:
        return {"escolhido": min(sem_teto, key=lambda v: (razao(v), v)), "fechou": True,
                "regra": "sem vida no teto, menor razao da deriva; empate, menor valor", "sem_teto": sem_teto}
    return {"escolhido": min(ordem, key=lambda v: (pontos[v]["vidas_no_teto"], razao(v), v)), "fechou": False,
            "regra": "reserva: menos vidas no teto, depois menor razao, depois menor valor", "sem_teto": []}


def fracoes_k3(medidas: dict) -> list:
    """K-3 por unidade: as sub-decisoes da fruta com duas frutas ou mais e informacao vigente nos dias 1-7, das tres condicoes juntas;
    fracao = decididas pela informacao (sonda info_decidiu) / elegiveis. Unidade sem elegivel fica None (o IC conta a parte)."""
    out = []
    for _, ms in sorted(_por_unidade(medidas).items()):
        eleg = sum(m["cerebro_c"]["k3_elegiveis"] for m in ms)
        dec = sum(m["cerebro_c"]["k3_decididas_pela_informacao"] for m in ms)
        out.append((dec / eleg) if eleg else None)
    return out


def regra_manipulacao(pontos: dict, limiar: float) -> dict:
    """K-3 (adendo 1.2): o menor w0_info em que a fracao decidida pela informacao passa do limiar (o limite inferior do IC 95%, a K-3 do
    plano da calibracao conjunta, secao 3.4). Se nenhum passar: o de maior fracao (o texto do adendo); empate, o menor valor."""
    ordem = sorted(pontos)
    passam = [v for v in ordem if pontos[v]["ic"]["ic_inferior"] is not None and pontos[v]["ic"]["ic_inferior"] > limiar]
    if passam:
        return {"escolhido": passam[0], "fechou": True, "regra": f"menor valor com IC95 inferior > {limiar}", "passam": passam}
    medias = {v: pontos[v]["ic"]["media"] for v in ordem}
    com = [v for v in ordem if medias[v] is not None]
    if not com:
        return {"escolhido": ordem[0], "fechou": False, "regra": "reserva: nenhum ponto com fracao; o menor valor", "passam": []}
    return {"escolhido": max(com, key=lambda v: (medias[v], -v)), "fechou": False, "regra": "reserva: o de maior fracao",
            "passam": []}


def nao_aprende(medidas: dict, boot: dict, dias: int) -> dict:
    """Secao 7 do plano, no piloto (o P1 no ponto escolhido): "nao aprende" se a deriva ao instinto no dia 14 tem o limite inferior do
    IC 95% <= 0, ou se a parte aprendida muda a escolha em menos de 1% das decisoes (limite superior do IC 95% < 0,01). Unidade = semente
    (as tres condicoes juntas: a deriva media e a fracao das decisoes somadas)."""
    der, frac, frac_esc = [], [], []
    for _, ms in sorted(_por_unidade(medidas).items()):
        der.append(sum(m["custo_da_plasticidade"]["deriva_por_dia"][dias - 1] for m in ms) / len(ms))
        frac.append(sum(m["cerebro_c"]["aprendido_decidiu"] for m in ms) / sum(m["cerebro_c"]["decisoes"] for m in ms))
        n_esc = sum(m["cerebro_c"]["decisoes_com_escolha"] for m in ms)
        frac_esc.append((sum(m["cerebro_c"]["aprendido_decidiu_com_escolha"] for m in ms) / n_esc) if n_esc else None)
    d, f = k2.ic(der, boot), k2.ic(frac, boot)
    deriva_nula = d["ic_inferior"] is not None and d["ic_inferior"] <= 0.0
    muda_pouco = f["ic_superior"] is not None and f["ic_superior"] < LIMIAR_NAO_APRENDE
    return {"deriva_dia_final": d, "fracao_aprendido_decidiu": f, "fracao_aprendido_decidiu_com_escolha_descritiva": k2.ic(frac_esc, boot),
            "deriva_nula": deriva_nula, "muda_menos_de_1pct": muda_pouco, "nao_aprende": deriva_nula or muda_pouco,
            "limiar": LIMIAR_NAO_APRENDE, "unidades": len(der)}


# ------------------------------------------------------------------ as etapas


def etapa_estabilidade(cfg, saida, contador, nome, parametro, grade, fixos, ganho, unidades, reusar=None) -> dict:
    pontos, medidas_por_ponto = {}, {}
    for v in grade:
        p = {**fixos, parametro: v}
        if reusar and v in reusar:
            medidas_por_ponto[v] = reusar[v]["medidas"]
            pontos[v] = {**resumo_estabilidade(reusar[v]["medidas"], int(cfg["dias"])), "ponto": p, "reusado_de": reusar[v]["de"],
                         "segundos": 0.0, "vidas": len(reusar[v]["medidas"])}
            continue
        b = bancada_c(cfg, ganho, p["passo"], p["teto"], p["w0_info"])
        r = rodar_ponto(cfg, b, "P1", unidades, saida / nome / f"{parametro}{v}", contador)
        medidas_por_ponto[v] = r["medidas"]
        pontos[v] = {**resumo_estabilidade(r["medidas"], int(cfg["dias"])), "ponto": p, "segundos": r["segundos"], "vidas": r["vidas"]}
    escolha = regra_estabilidade(pontos)
    res = {"etapa": nome, "parametro": parametro, "onde": "P1, casado_frutas + descasado + mutavel", "fixos": fixos,
           "medida": "vidas com compartimento no teto; razao da deriva dia 14 / dia 7, media das tres condicoes", "pontos": pontos,
           **escolha}
    return {"resultado": res, "medidas": medidas_por_ponto}


def etapa_manipulacao(cfg, saida, contador, grade, fixos, ganho, unidades) -> dict:
    pontos, ref = {}, None
    for v in sorted(set(grade) | {W0_INFO_REFERENCIA}):
        b = bancada_c(cfg, ganho, fixos["passo"], fixos["teto"], v)
        r = rodar_ponto(cfg, b, "P2", unidades, saida / "C-C" / f"w0_info{v}", contador)
        vals = fracoes_k3(r["medidas"])
        ponto = {"ponto": {**fixos, "w0_info": v}, "valores": vals, "ic": k2.ic(vals, cfg["bootstrap"]),
                 "elegiveis": sum(m["cerebro_c"]["k3_elegiveis"] for m in r["medidas"].values()),
                 "decididas": sum(m["cerebro_c"]["k3_decididas_pela_informacao"] for m in r["medidas"].values()),
                 "vidas_no_teto": sum(m["cerebro_c"]["pesos_no_teto"] > 0 for m in r["medidas"].values()),
                 "segundos": r["segundos"], "vidas": r["vidas"]}
        if v in grade:
            pontos[v] = ponto
        if v == W0_INFO_REFERENCIA:
            ref = ponto
    escolha = regra_manipulacao(pontos, LIMIAR_DECIDIDA)
    return {"etapa": "C-C", "parametro": "w0_info", "onde": f"P2, as tres condicoes, dias 1-{min(DIAS_K3, int(cfg['dias']))}",
            "fixos": fixos, "medida": "fracao das sub-decisoes com duas frutas ou mais e informacao vigente decididas pela informacao "
            "(sonda info_decidiu), por unidade, as tres condicoes juntas", "limiar": LIMIAR_DECIDIDA, "pontos": pontos,
            "referencia_w0_info_0_descritiva": ref, **escolha}


def rodar(cfg: dict, saida: Path | None = None, teto_vidas: int = TETO_VIDAS) -> dict:
    modo, unidades = modo_e_unidades(cfg)
    gr = grades(cfg)
    plan = vidas_planejadas(gr, len(unidades))
    if plan["total"] > teto_vidas:
        raise GradeAcimaDoTeto(f"a grade pede {plan['total']} vidas, acima do teto de {teto_vidas}: escreva um adendo antes de rodar")
    ganho = ganho_da_k2()
    seg_k2 = segundos_da_k2()
    saida = Path(saida or cfg.get("saida", SAIDA_PADRAO))
    if not saida.is_absolute():
        saida = RAIZ / saida
    contador = Contador(teto_vidas)
    t0 = time.perf_counter()
    dias = int(cfg["dias"])
    # C-A: o passo, com teto 4S e w0_info 0
    a = etapa_estabilidade(cfg, saida, contador, "C-A", "passo", gr["passo"], dict(FIXOS_C_A), ganho, unidades)
    _gravar(saida / "C-A" / "resultado.json", _dump(a["resultado"]))
    passo = a["resultado"]["escolhido"]
    # C-B: o teto, com o passo da C-A; o 4S ja rodou na C-A (o mesmo ponto), entao reusa aquelas vidas
    reusar = {FIXOS_C_A["teto"]: {"medidas": a["medidas"][passo], "de": f"C-A/passo{passo}"}} if FIXOS_C_A["teto"] in gr["teto"] else None
    b = etapa_estabilidade(cfg, saida, contador, "C-B", "teto", gr["teto"], {"passo": passo, "w0_info": FIXOS_C_A["w0_info"]}, ganho,
                           unidades, reusar)
    _gravar(saida / "C-B" / "resultado.json", _dump(b["resultado"]))
    teto = b["resultado"]["escolhido"]
    # C-C: o w0_info, com passo e teto escolhidos (mais o w0_info 0, descritivo)
    c = etapa_manipulacao(cfg, saida, contador, gr["w0_info"], {"passo": passo, "teto": teto}, ganho, unidades)
    _gravar(saida / "C-C" / "resultado.json", _dump(c))
    w0 = c["escolhido"]
    ponto = {"passo": passo, "teto": teto, "w0_info": w0, "ganho": ganho}
    # o piloto: o "nao aprende" no P1 do ponto escolhido (as vidas da C-B nesse teto: o w0_info nao age no P1, sem informante)
    piloto = {"onde": f"P1, as tres condicoes, ponto passo {passo}, teto {teto} (vidas da C-B; o w0_info nao age no P1)",
              **nao_aprende(b["medidas"][teto], cfg["bootstrap"], dias)}
    _gravar(saida / "piloto.json", _dump(piloto))
    segundos = time.perf_counter() - t0
    fechou = {"C-A": a["resultado"]["fechou"], "C-B": b["resultado"]["fechou"], "C-C": c["fechou"]}
    res = {"modo": modo, "unidades": len(unidades), "ponto": ponto, "fecharam": fechou, "nao_aprende": piloto["nao_aprende"],
           "vidas": contador.n, "vidas_planejadas": plan, "teto_vidas": teto_vidas, "segundos": segundos,
           "teto_segundos": FATOR_TEMPO * seg_k2, "dentro_do_teto_de_tempo": segundos <= FATOR_TEMPO * seg_k2}
    _gravar(saida / "escolha.json", _dump({"ponto": ponto, "fecharam": fechou, "nao_aprende": piloto["nao_aprende"],
                                          "cerebro_fecha": not piloto["nao_aprende"]}))
    _gravar(saida / "meta.json", _dump({"config": cfg, "modo": modo, "plano": PLANO, "plano_sha256": bv._sha(RAIZ / PLANO),
                                       "tarefa": TAREFA, "orquestrador_sha256": bv._sha(Path(__file__)),
                                       "cerebro_c_sha256": bv._sha(RAIZ / "digilab" / "policies" / "cerebro_c.py"),
                                       "escolha_k2": ESCOLHA_K2, "python": platform.python_version(), "plataforma": platform.platform(),
                                       **{k: res[k] for k in ("ponto", "vidas", "vidas_planejadas", "teto_vidas", "segundos",
                                                              "teto_segundos", "dentro_do_teto_de_tempo", "unidades")},
                                       "unidades_lista": unidades}))
    return res


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="calibracao do cerebro C (adendo 1.2 de docs/PLANO_ANALISE_V2_COMPARACAO_CEREBROS.md)")
    ap.add_argument("--config", required=True)
    ap.add_argument("--saida", default=None)
    a = ap.parse_args(argv)
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    r = rodar(cfg, a.saida)
    print(f"{r['modo']}: ponto {r['ponto']}; fecharam {r['fecharam']}; nao aprende {r['nao_aprende']}; {r['vidas']} vidas, "
          f"{r['segundos']:.0f} s (teto {r['teto_segundos']:.0f} s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
