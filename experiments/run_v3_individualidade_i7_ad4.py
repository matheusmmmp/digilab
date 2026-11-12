"""O orquestrador do adendo 4 do I7 da INDIVIDUALIDADE: o humor decide? (docs/PLANO_ANALISE_V3_INDIVIDUALIDADE_I7.md, secao 18,
DECIDIDO pelo Matheus em 2026-11-12, AD4-1 a AD4-8 pela recomendacao).

Cada pet novo (AD4-2: os bracos REL e REL+F, os donos atencioso, relapso e aleatorio, as sementes da faixa 95101...95505) tem a vida de
base vivida aqui e os ramos (18.3), todos pelo laco do `simular_vida_fisico`, com o sorteio amarrado do adendo 2 (14.3, AD4-4):
  - N, o nulo, com os gravadores ligados: o log tem de ser o da vida de base, byte a byte (G-AD4-0). O N tambem grava, em cada passo do
    dono, o humor, a energia, a fome e a acao em curso do pet (so de leitura: o `estado()` do motor antes de o dono agir);
  - G, o gemeo, e R°, o amarrado sem evento (G-AD4-1), como no adendo 2;
  - Rb(t): o tapa em M_baixo(t), o primeiro passo do dono do dia t com uma decisao acordada e o humor abaixo de 0,58 (18.2, AD4-3);
  - Ra(t): o tapa em M_alto(t), o primeiro passo do dono do dia t com uma decisao acordada e o humor em 0,58 ou acima.
O corte 0,58 e a mediana do humor da descoberta do adendo 3, registrada na secao 17 (D-IND-AD4-3), e nao e recalculado. O dia t (de 1 a
14) cobre os ticks [(t - 1) x 1440, t x 1440), como nos momentos das sondas do I7.

A medida (18.4): o grupo de cada ramo pelo SEQ (16.2: "absorve" com D = 0 nos quatro dias da janela, "afasta" com D > 0 nos quatro,
"misto" fora) e, por braco, Delta_H = a fracao "afasta" do Rb menos a do Ra, sobre os pares em que os dois ramos tem grupo, com o IC95 do
bootstrap sobre as sementes (2 000 reamostras, a rng `individualidade-i7-ad4-boot`). Os descritivos da 18.5 e da 18.6 ficam no
`analise.json`. Nada no `digilab/`, no `engine.py`, no cerebro nem no `simular_vida_fisico` muda.

A trava (18 e 18.8): a run so roda com o cabecalho "APROVADO pelo Matheus", o adendo 4 DECIDIDO no cabecalho, a secao nova do registro
(`## 19. O registro do adendo 4`, uma vez), as bases e o K da AD4-2 dentro da faixa reservada do adendo, no maximo 4 processos e nada por
cima de uma pasta. A fumaca (as sementes dos testes, 101...505) segue o mesmo caminho.

    python experiments/run_v3_individualidade_i7_ad4.py --config experiments/configs/v3_individualidade/individualidade_i7_ad4.json --processos 4
"""
from __future__ import annotations

import argparse
import gzip
import io
import json
import platform
import random
import statistics
import sys
import tarfile
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402
import run_v2_memoria_autobio as ma  # noqa: E402
import run_v3_individualidade_i5 as i5  # noqa: E402
import run_v3_individualidade_i7 as r7  # noqa: E402
import run_v3_individualidade_i7_ad2 as a2  # noqa: E402
import sondas_individualidade as so  # noqa: E402
from bancada.regras_mundo import simular_vida_fisico  # noqa: E402
from digilab import metrics as M  # noqa: E402
from digilab.config import CONFIG_PADRAO  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.mundo import DonoComLugar  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402

PLANO = r7.PLANO
MARCA_ADENDO = "**O adendo 4 (seção 18) está DECIDIDO pelo Matheus"
TITULO_REGISTRO = "## 19. O registro do adendo 4"
FASE = "individualidade-i7-ad4"
BASES = (95101, 95202, 95303, 95404, 95505)                                           # AD4-2
K_POR_BASE, PREFIXO, LUGAR = r7.K_POR_BASE, r7.PREFIXO, r7.LUGAR
FONTE_FAIXA = "INDIVIDUALIDADE, I7, adendo 4"
BRACOS, DONOS = r7.BRACOS, r7.DONOS
DIAS, ORCAMENTO_POR_DIA, DECISOES_POR_DIA = r7.DIAS, r7.ORCAMENTO_POR_DIA, r7.DECISOES_POR_DIA
IDADES, JANELA = r7.IDADES, r7.JANELA
CORTE_HUMOR = 0.58                       # AD4-3: a mediana do humor da descoberta do adendo 3 (secao 17), DECIDIDA com o adendo
FAIXA_NULO = 0.05                        # AD4-7, PROPOSTA, SEM FONTE: o nulo e o IC95 inteiro dentro de [-0,05; +0,05]
MAX_PROCESSOS = r7.MAX_PROCESSOS
BOOTSTRAP = 2000
SAIDA = "artifacts_v3_individualidade_i7_ad4"
CHAVES_CONFIG = r7.CHAVES_CONFIG
RAMOS = ("Rb", "Ra")
TAPA = r7.TAPA
DORMIR = "dormir"
LEITURAS = ("energia", "fome", "humor")


# ================================================================== a trava
def _plano() -> str:
    return (RAIZ / PLANO).read_text(encoding="utf-8")


def exigir_plano_decidido(texto: str) -> None:
    """o cabecalho APROVADO do I7, o adendo 4 DECIDIDO no cabecalho e a secao do registro do adendo (uma vez)"""
    r7.exigir_plano_aprovado(texto)
    linhas = texto.splitlines()
    if not any(x.startswith(MARCA_ADENDO) for x in linhas[:40]):
        raise RuntimeError("o plano do I7 sem o adendo 4 DECIDIDO no cabecalho: nenhuma vida")
    if sum(1 for x in linhas if x.startswith(TITULO_REGISTRO)) != 1:
        raise RuntimeError(f"o plano do I7 sem a secao {TITULO_REGISTRO!r} (o registro do adendo 4): nenhuma vida")


def modo_da_config(cfg: dict, texto_plano: str | None = None) -> str:
    """'fumaca' (as sementes dos testes) ou a fase do adendo (a faixa da AD4-2; a trava); o resto falha alto"""
    faltam, sobram = (CHAVES_CONFIG - {"descricao"}) - set(cfg), set(cfg) - CHAVES_CONFIG
    if faltam or sobram:
        raise ValueError(f"config: faltam {sorted(faltam)}, sobram {sorted(sobram)}")
    if cfg["fase"] != FASE:
        raise ValueError(f"fase {cfg['fase']!r}: so {FASE!r}")
    if cfg["vidas"] is not None:
        raise ValueError("o adendo 4 vive as proprias vidas de base: `vidas` e null")
    u = cfg["unidades"]
    bases = tuple(u["bases"])
    if u.get("prefixo") != PREFIXO or cfg["orcamento_por_dia"] != ORCAMENTO_POR_DIA or type(u.get("k")) is not int or u["k"] < 1:
        raise ValueError("config fora do plano: o prefixo, o orcamento ou o K")
    if cfg["dias"] != DIAS:
        raise ValueError(f"dias {cfg['dias']}: o I7 vive {DIAS} dias")
    if cfg.get("plano") != PLANO:
        raise ValueError(f"plano {cfg.get('plano')!r}")
    if bases and set(bases) <= bv.SEMENTES_TESTE:
        return "fumaca"
    if bases != BASES:
        raise bv.SementeSemPlano(f"bases {list(bases)}: so as dos testes (fumaca) ou as da AD4-2 {list(BASES)}")
    for b in bases:
        fonte = bv.na_faixa_reservada(b)
        if fonte is None or FONTE_FAIXA not in fonte:
            raise bv.SementeSemPlano(f"a base {b} fora da faixa reservada do adendo 4 ({FONTE_FAIXA!r} em experiments/bancada/faixas.py)")
    exigir_plano_decidido(_plano() if texto_plano is None else texto_plano)
    if u["k"] != K_POR_BASE:
        raise ValueError(f"a run segue o plano a letra: K {u['k']}")
    return FASE


# ================================================================== o N com o humor de cada passo do dono
class DonoLendo(a2.DonoAmarravel):
    """o embrulho do adendo 2 que, alem de gravar as rngs do dono, le o estado do pet em cada passo do dono (so de leitura, antes de o dono
    agir): {tick: {"energia", "fome", "humor", "acao"}}"""

    def __init__(self, *a, **k) -> None:
        super().__init__(*a, **k)
        self.leituras: dict[int, dict] = {}

    def decidir(self, visao, rng):
        e = self.caixa["motor"].estado()
        tick = visao.estado["tick"]
        if e["tick"] != tick:
            raise RuntimeError(f"a leitura do passo: o motor no tick {e['tick']}, o passo no {tick}")
        self.leituras[tick] = {**{c: float(e[c]) for c in LEITURAS}, "acao": e["acao_atual"]}
        return super().decidir(visao, rng)


def viver_n(braco: str, dono: str, semente: int, dias: int, orcamento_por_dia: int) -> dict:
    """o ramo N do adendo 2 (os gravadores ligados) com as leituras de cada passo do dono"""
    fp, fm = i5.fabricas_vida(braco, dono, semente, dias, orcamento_por_dia)
    caixa: dict = {}
    base = r7._lendo_estado(fm, caixa, None)

    def fabrica(politica, cfg, s):
        m = base(politica, cfg, s)
        m._rng_politica = a2.RngGravador(caixa, m._rng_politica.getstate())
        caixa["rng_pol"] = m._rng_politica
        return m
    d = DonoLendo(DonoComLugar(criar_dono(dono), LUGAR, semente, dono, orq.CM), caixa, None, None, "gravar", None)
    motor, _ = simular_vida_fisico(d, fp(CONFIG_PADRAO), semente, dias, orcamento_por_dia * dias, dono, fabrica)
    return {"log": motor.log.para_jsonl(), "decisoes": motor.decisoes_mundo, "estados": caixa["estados"], "aplicado": d.aplicado,
            "tabela_pol": caixa["rng_pol"].tabela, "tabela_dono": d.estados, "leituras": d.leituras}


def passos_acordados(leituras: dict, decisoes: list[dict], t: int) -> list[int]:
    """os passos do dono do dia t (de 1 a 14) cujo intervalo [passo, passo + PASSO_DONO) tem uma decisao acordada do pet, em ordem"""
    ini, fim = (t - 1) * so.TICKS_POR_DIA, t * so.TICKS_POR_DIA
    acordadas = {d["tick"] - d["tick"] % so.PASSO_DONO for d in decisoes if ini <= d["tick"] < fim and d["acao"] != DORMIR}
    return sorted(p for p in leituras if ini <= p < fim and p in acordadas)


def momentos_do_humor(leituras: dict, decisoes: list[dict], t: int, corte: float = CORTE_HUMOR) -> tuple[int | None, int | None]:
    """(M_baixo(t), M_alto(t)) da 18.2: o primeiro passo acordado do dia t com o humor abaixo do corte e o primeiro em ou acima dele"""
    baixo = alto = None
    for p in passos_acordados(leituras, decisoes, t):
        h = leituras[p]["humor"]
        if h < corte and baixo is None:
            baixo = p
        if h >= corte and alto is None:
            alto = p
        if baixo is not None and alto is not None:
            break
    return baixo, alto


def conferir_momento(leituras: dict, decisoes: list[dict], t: int, m: int, baixo: bool, corte: float = CORTE_HUMOR) -> None:
    """G-AD4-5: o humor do momento esta do lado certo do corte e nenhum passo acordado anterior do dia t cumpre a mesma condicao"""
    lado = (lambda h: h < corte) if baixo else (lambda h: h >= corte)
    ps = passos_acordados(leituras, decisoes, t)
    if m not in ps or not lado(leituras[m]["humor"]) or any(lado(leituras[p]["humor"]) for p in ps if p < m):
        raise RuntimeError(f"G-AD4-5: o momento {m} do dia {t} ({'baixo' if baixo else 'alto'}) nao e o da 18.2")


# ================================================================== os ramos de um pet
def tarefa_pet(braco: str, dono: str, unidade: dict, dias: int, orcamento_por_dia: int, idades: tuple = IDADES,
               janela: int = JANELA) -> dict:
    """a vida de base e todos os ramos de um pet, com as conferencias G-AD4-0 a 5"""
    p0 = time.perf_counter()
    semente = unidade["semente"]
    rot = f"{braco}|{dono}|{semente}"
    custo: dict = {}

    def cronometrar(nome, fazer):
        t0 = time.perf_counter()
        r = fazer()
        custo[nome] = time.perf_counter() - t0
        return r

    motor_base, *_ = cronometrar("base", lambda: ma.viver(braco, dono, LUGAR, semente, dias, orcamento_por_dia))
    texto = motor_base.log.para_jsonl()
    if r7._contar_tapas(texto):
        raise RuntimeError(f"{rot}: a vida de base tem tapa")
    n = cronometrar("N", lambda: a2._duas_vezes(lambda: viver_n(braco, dono, semente, dias, orcamento_por_dia), f"{rot} N"))
    if n["log"] != texto:                                                  # G-AD4-0
        raise bv.ReplayDivergiu(f"G-AD4-0: {rot}: o ramo N nao e a vida de base")
    if i5.decisoes_por_dia(n["decisoes"], dias) != [DECISOES_POR_DIA] * dias:
        raise RuntimeError(f"G-AD4-0: {rot}: as decisoes por dia nao sao {DECISOES_POR_DIA}")
    todos = list(range(1, dias + 1))

    def amarrar(t, lado):
        return {"pol": n["tabela_pol"], "dono": n["tabela_dono"],
                "sem_par": derivar_semente("individualidade-i7-ad4-amarrado", semente, braco, dono, t, lado)}

    g = cronometrar("G", lambda: a2._duas_vezes(lambda: a2.viver_ramo(
        braco, dono, semente, dias, orcamento_por_dia, rng_nascimento=derivar_semente("individualidade-i7-gemeo", semente, braco, dono)),
        f"{rot} G"))
    r0 = cronometrar("R0", lambda: a2._duas_vezes(lambda: a2.viver_ramo(braco, dono, semente, dias, orcamento_por_dia,
                                                                           amarrar=amarrar(0, "0")), f"{rot} R°"))
    if r0["log"] != n["log"] or r0["decisoes"] != n["decisoes"] or r0["estados"] != n["estados"]:   # G-AD4-1
        raise RuntimeError(f"G-AD4-1: {rot}: o R° nao e o N")
    if r0["amarrado"]["sem_par"] or r0["amarrado"]["passos_descasados"] or r0["amarrado"]["par"] != len(n["tabela_pol"]):
        raise RuntimeError(f"G-AD4-1: {rot}: o R° com chave sem par ou passo descasado: {r0['amarrado']}")
    vidas = {("N", None): n, ("G", None): g, ("R0", None): r0}
    momentos: dict = {}
    sem_par_de_momentos = []

    def tapa(motor):
        motor.observar(TAPA)
    for t in idades:
        mb, mal = momentos_do_humor(n["leituras"], n["decisoes"], t)
        momentos[t] = {"Rb": mb, "Ra": mal}
        if mb is None or mal is None:
            sem_par_de_momentos.append(t)
            continue
        for b, m, lado in (("Rb", mb, "b"), ("Ra", mal, "a")):
            conferir_momento(n["leituras"], n["decisoes"], t, m, b == "Rb")
            v = cronometrar(f"{b}{t}", lambda: a2._duas_vezes(
                lambda: a2.viver_ramo(braco, dono, semente, dias, orcamento_por_dia, m, tapa, amarrar=amarrar(t, lado)), f"{rot} {b}({t})"))
            if v["aplicado"] != 1:                                         # G-AD4-4
                raise RuntimeError(f"G-AD4-4: {rot} {b}({t}): o tapa foi aplicado {v['aplicado']} vezes")
            if [d for d in v["decisoes"] if d["tick"] < m] != [d for d in n["decisoes"] if d["tick"] < m]:   # G-AD4-3
                raise RuntimeError(f"G-AD4-3: {rot} {b}({t}): as decisoes antes do momento nao sao as do original")
            if r7._contar_tapas(v["log"]) != [m]:
                raise RuntimeError(f"G-AD4-4: {rot} {b}({t}): os tapas do log sao {r7._contar_tapas(v['log'])}")
            vidas[(b, t)] = v
    perfis = {("N", None): r7._perfis(n["decisoes"], todos), ("G", None): r7._perfis(g["decisoes"], todos)}
    parciais = {}
    linhas = []
    for (b, t), v in sorted(vidas.items(), key=lambda kv: (kv[0][0], kv[0][1] or 0)):
        m = None if t is None else momentos[t][b]
        linha = {"braco": braco, "dono": dono, "semente": semente, "base": unidade["base"], "k": unidade["k"], "ramo": b, "idade": t,
                 "momento": m, "log_sha256": r7._sha(v["log"]), "decisoes_sha256": r7._sha_decisoes(v["decisoes"]),
                 "amarrado": v.get("amarrado"),
                 "conferencias": {"G-AD4-0": b == "N", "G-AD4-1": b == "R0", "G-AD4-2": True, "G-AD4-3": b in RAMOS,
                                  "G-AD4-4": b in RAMOS, "G-AD4-5": b in RAMOS}}
        if t is not None:
            usados = [d for d in range(t + 1, t + janela + 1) if d <= dias]
            perfis[(b, t)] = r7._perfis(v["decisoes"], usados)
            parciais[(b, t)] = r7._perfis(v["decisoes"], [t], m)[t]
            parciais[("N", (b, t))] = r7._perfis(n["decisoes"], [t], m)[t]
            linha["leitura_no_momento"] = n["leituras"][m]
            outro = momentos[t]["Ra" if b == "Rb" else "Rb"]
            linha["outro_momento"] = outro
        linhas.append(linha)
    custo["pet_parede"] = time.perf_counter() - p0
    return {"vida": rot, "braco": braco, "dono": dono, "semente": semente, "base": unidade["base"], "k": unidade["k"], "log_base": texto,
            "momentos": {str(t): momentos[t] for t in idades}, "sem_par_de_momentos": sem_par_de_momentos, "perfis": perfis,
            "parciais": parciais, "ramos": linhas, "custo": custo}


def tarefa(lote: list[tuple], dias: int, orcamento_por_dia: int) -> list[dict]:
    return [tarefa_pet(b, d, u, dias, orcamento_por_dia) for b, d, u in lote]


# ================================================================== a analise
def grupos_do_pet(p: dict, idades: tuple = IDADES, janela: int = JANELA, dias: int = DIAS) -> dict:
    """{(ramo, t): {"grupo", "imediato_zero", "D"}} pelo SEQ (16.2), contra o N; e {("G", t): soma da regua} para o Phi descritivo"""
    orig = a2._um_perfil(p["perfis"][("N", None)], "SEQ")
    gem = a2._um_perfil(p["perfis"][("G", None)], "SEQ")
    dg = M.distancias_ramo(gem, orig, list(range(1, dias + 1)))
    out = {}
    for t in idades:
        usados = [d for d in range(t + 1, t + janela + 1) if d <= dias]
        for b in RAMOS:
            if (b, t) not in p["perfis"]:
                continue
            por_dia = M.distancias_ramo(a2._um_perfil(p["perfis"][(b, t)], "SEQ"), orig, usados)
            c = M.trajetoria_janela([por_dia[d] for d in sorted(por_dia)])
            pr, po = p["parciais"][(b, t)], p["parciais"][("N", (b, t))]   # um resto do dia t fora do I5 (poucas acordadas) vem None
            ram = None if pr is None else a2._presente(pr.get("SEQ"))
            ori = None if po is None else a2._presente(po.get("SEQ"))
            d0 = None if ram is None or ori is None else M.distancia_tv(ram, ori)
            out[(b, t)] = {"grupo": {"sempre0": "absorve", "nunca0": "afasta", "misto": "misto", None: None}[c],
                           "imediato_zero": None if d0 is None else d0 == 0,
                           "phi": [(por_dia[d], dg.get(d)) for d in sorted(por_dia)]}
    return out


def pares(pets: dict, linhas_ramos: list[dict]) -> list[dict]:
    """um registro por par (pet, t) com os dois ramos e os dois grupos; as leituras dos dois momentos vem do ramos.jsonl"""
    leit = {(r["braco"], r["dono"], r["semente"], r["ramo"], r["idade"]): r for r in linhas_ramos if r["ramo"] in RAMOS}
    out = []
    for (br, dono, s), p in sorted(pets.items()):
        gr = grupos_do_pet(p)
        for t in IDADES:
            if ("Rb", t) not in gr or ("Ra", t) not in gr:
                continue
            lb, la = leit[(br, dono, s, "Rb", t)], leit[(br, dono, s, "Ra", t)]
            out.append({"braco": br, "dono": dono, "semente": s, "idade": t, "grupo_b": gr[("Rb", t)]["grupo"],
                        "grupo_a": gr[("Ra", t)]["grupo"], "imediato_b": gr[("Rb", t)]["imediato_zero"],
                        "imediato_a": gr[("Ra", t)]["imediato_zero"], "momento_b": lb["momento"], "momento_a": la["momento"],
                        "leitura_b": lb["leitura_no_momento"], "leitura_a": la["leitura_no_momento"],
                        "phi_b": gr[("Rb", t)]["phi"], "phi_a": gr[("Ra", t)]["phi"],
                        "amarrado_b": lb["amarrado"], "amarrado_a": la["amarrado"]})
    return out


def _com_grupo(x: dict) -> bool:
    return x["grupo_b"] in ("absorve", "afasta") and x["grupo_a"] in ("absorve", "afasta")


def delta(ps: list[dict]) -> float | None:
    """Delta_H (18.4): a fracao "afasta" do Rb menos a do Ra, sobre os pares com os dois grupos"""
    xs = [x for x in ps if _com_grupo(x)]
    if not xs:
        return None
    return (sum(x["grupo_b"] == "afasta" for x in xs) - sum(x["grupo_a"] == "afasta" for x in xs)) / len(xs)


def bootstrap_delta(ps: list[dict], rotulo: tuple, boot: int = BOOTSTRAP) -> list[float] | None:
    """o IC95 percentil do Delta_H, reamostrando as sementes com repeticao, com a rng `individualidade-i7-ad4-boot` (18.4)"""
    por: dict = {}
    for x in ps:
        por.setdefault(x["semente"], []).append(x)
    sementes = sorted(por)
    if not sementes:
        return None
    rng = random.Random(derivar_semente("individualidade-i7-ad4-boot", *rotulo))
    vs = []
    for _ in range(boot):
        amostra = [x for s in (rng.choice(sementes) for _ in sementes) for x in por[s]]
        v = delta(amostra)
        if v is not None:
            vs.append(v)
    return r7._percentis(vs)


def leitura(ic: list[float] | None) -> str:
    """a frase da 18.4 pelo IC95 do Delta_H"""
    if ic is None:
        return "sem pares com grupo"
    lo, hi = ic
    if lo > 0:
        return "H-HUMOR"
    if hi < 0:
        return "o contrario: o tapa com o humor alto pesa mais"
    if -FAIXA_NULO <= lo and hi <= FAIXA_NULO:
        return "H-SINAL"
    return "Delta_H nao se distingue nesta analise"


def _fracao_afasta(xs: list[dict], lado: str) -> dict:
    ys = [x for x in xs if _com_grupo(x)]
    return {"n": len(ys), "afasta": (sum(x[f"grupo_{lado}"] == "afasta" for x in ys) / len(ys)) if ys else None}


def descritivos(ps: list[dict], pets_por_braco: dict, braco: str) -> dict:
    """18.5 e 18.6, sem frase"""
    xs = [x for x in ps if x["braco"] == braco]
    out: dict = {}
    tem = len(xs)
    total = pets_por_braco[braco] * len(IDADES)
    out["pares_existentes"] = {"pares": tem, "pet_dias": total, "fracao": tem / total if total else None,
                               "por_dono": {d: sum(x["dono"] == d for x in xs) for d in DONOS},
                               "por_idade": {str(t): sum(x["idade"] == t for x in xs) for t in IDADES}}
    ordem_b = [x for x in xs if x["momento_b"] < x["momento_a"]]
    ordem_a = [x for x in xs if x["momento_a"] < x["momento_b"]]
    out["ordem"] = {"fracao_baixo_antes": len(ordem_b) / tem if tem else None,
                    "delta_baixo_antes": delta(ordem_b), "delta_alto_antes": delta(ordem_a)}
    dist = sorted(abs(x["momento_b"] - x["momento_a"]) for x in xs)
    out["distancia_ticks"] = {"mediana": statistics.median(dist) if dist else None,
                              "quartis": statistics.quantiles(dist, n=4) if len(dist) >= 2 else None}
    out["leituras"] = {}
    for c in ("energia", "fome", "humor"):
        for lado in ("b", "a"):
            v = [x[f"leitura_{lado}"][c] for x in xs]
            out["leituras"][f"{c}|{lado}"] = {"media": statistics.fmean(v) if v else None,
                                              "quartis": statistics.quantiles(v, n=4) if len(v) >= 2 else None}
    dif = [abs(x["leitura_b"]["energia"] - x["leitura_a"]["energia"]) for x in xs]
    if dif:
        med = statistics.median(dif)
        perto = [x for x, d in zip(xs, dif) if d < med]
        out["sensibilidade_energia"] = {"mediana_da_diferenca": med, "pares": len(perto), "delta": delta(perto)}
    else:
        out["sensibilidade_energia"] = None
    out["acao_dormir"] = {lado: (sum(x[f"leitura_{lado}"]["acao"] == DORMIR for x in xs) / tem if tem else None) for lado in ("b", "a")}
    out["por_dono"] = {d: {"Rb": _fracao_afasta([x for x in xs if x["dono"] == d], "b"),
                           "Ra": _fracao_afasta([x for x in xs if x["dono"] == d], "a"),
                           "delta": delta([x for x in xs if x["dono"] == d])} for d in DONOS}
    out["por_idade"] = {str(t): delta([x for x in xs if x["idade"] == t]) for t in IDADES}
    imed: dict = {}
    for lado in ("b", "a"):
        for z in (True, False):
            ys = [x for x in xs if x[f"imediato_{lado}"] is z and x[f"grupo_{lado}"] in ("absorve", "afasta")]
            imed[f"{lado}|resto do dia t {'igual' if z else 'diferente'}"] = {
                "n": len(ys), "afasta": (sum(x[f"grupo_{lado}"] == "afasta" for x in ys) / len(ys)) if ys else None}
    out["imediato"] = imed
    out["amarrado"] = {}
    for lado in ("b", "a"):
        sem, tot = sum(x[f"amarrado_{lado}"]["sem_par"] for x in xs), sum(x[f"amarrado_{lado}"]["par"] + x[f"amarrado_{lado}"]["sem_par"] for x in xs)
        out["amarrado"][lado] = {"fracao_sem_par": sem / tot if tot else None}
    out["Phi"] = {lado: M.razao_de_somas([pr for x in xs for pr in x[f"phi_{lado}"]]) for lado in ("b", "a")}
    return out


def analisar(pets: dict, linhas_ramos: list[dict], boot: int = BOOTSTRAP) -> dict:
    ps = pares(pets, linhas_ramos)
    pets_por_braco = {b: sum(1 for (br, _, _) in pets if br == b) for b in BRACOS}
    out: dict = {"idades": list(IDADES), "janela": JANELA, "bootstrap": boot, "corte_humor": CORTE_HUMOR, "faixa_nulo": FAIXA_NULO,
                 "multiplicidade": "2 bracos, sem correcao (18.4)", "por_braco": {}}
    for b in BRACOS:
        xs = [x for x in ps if x["braco"] == b]
        ic = bootstrap_delta(xs, (b, "Delta_H"), boot)
        out["por_braco"][b] = {"delta_H": delta(xs), "ic95": ic, "pares_com_grupo": sum(_com_grupo(x) for x in xs),
                               "leitura": leitura(ic), "descritivo": descritivos(ps, pets_por_braco, b)}
    return out


# ================================================================== a run
def rodar(cfg: dict, pasta: Path, processos: int, caminho_config: Path | None = None, boot: int = BOOTSTRAP) -> dict:
    if processos > MAX_PROCESSOS:
        raise ValueError(f"no maximo {MAX_PROCESSOS} processos (V3-D8)")
    modo = modo_da_config(cfg)
    if pasta.exists():
        raise FileExistsError(f"{pasta} ja existe: a run se recusa a gravar por cima")
    unidades = bv.unidades_derivadas(cfg["unidades"]["bases"], int(cfg["unidades"]["k"]), PREFIXO)
    pasta.mkdir(parents=True)
    inicio = time.time()
    rc = orq.rc
    meta = {"modo": modo, "fase": FASE, "plano": PLANO, "plano_sha256": rc._sha_arquivo(RAIZ / PLANO), "config": cfg,
            "config_arquivo": None if caminho_config is None else rc._relativo(caminho_config),
            "config_sha256": None if caminho_config is None else rc._sha_arquivo(caminho_config),
            "comando": " ".join(["python"] + [Path(sys.argv[0]).as_posix()] + sys.argv[1:]),
            "orquestrador_sha256": rc._sha_arquivo(Path(__file__)),
            "orquestrador_ad2_sha256": rc._sha_arquivo(RAIZ / "experiments" / "run_v3_individualidade_i7_ad2.py"),
            "orquestrador_i7_sha256": rc._sha_arquivo(RAIZ / "experiments" / "run_v3_individualidade_i7.py"),
            "git_head": rc._git("rev-parse", "HEAD"), "git_limpo": rc._git("status", "--porcelain") == "",
            "processos": processos, "unidades": unidades, "bracos": list(BRACOS), "donos": list(DONOS), "lugar": LUGAR, "bootstrap": boot,
            "idades": list(IDADES), "janela": JANELA, "corte_humor": CORTE_HUMOR,
            "sha256": {n: rc._sha_arquivo(RAIZ / "digilab" / n) for n in ("config.py", "engine.py", "metrics.py", "mundo.py")},
            "inicio": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(inicio))}
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    lotes = [[(b, d, u)] for u in unidades for b in BRACOS for d in DONOS]
    t0 = time.perf_counter()
    registros = [r for s in rc._executar([(tarefa, (lote, cfg["dias"], cfg["orcamento_por_dia"])) for lote in lotes], processos) for r in s]
    meta["vidas_parede_s"] = time.perf_counter() - t0
    if len(registros) != len(lotes):
        raise RuntimeError(f"{len(registros)} pets, eram {len(lotes)}")
    registros = sorted(registros, key=lambda r: r["vida"])
    with tarfile.open(pasta / "vidas.tar.gz", "w:gz") as tar:
        for r in registros:
            dados = r["log_base"].encode("utf-8")
            info = tarfile.TarInfo(i5.nome_da_vida(r["braco"], r["dono"], r["semente"]))
            info.size = len(dados)
            tar.addfile(info, io.BytesIO(dados))
    with gzip.open(pasta / "perfis.jsonl.gz", "wt", encoding="utf-8", newline="\n") as f:
        for r in registros:
            for linha in linhas_perfis(r):
                f.write(json.dumps(linha, sort_keys=True) + "\n")
    linhas_ramos = [linha for r in registros for linha in r["ramos"]]
    with (pasta / "ramos.jsonl").open("w", encoding="utf-8", newline="\n") as f:
        for linha in linhas_ramos:
            f.write(json.dumps(linha, sort_keys=True) + "\n")
    pets = ler_perfis(pasta / "perfis.jsonl.gz")
    lidas = [json.loads(x) for x in (pasta / "ramos.jsonl").read_text(encoding="utf-8").splitlines()]
    resultado = {"modo": modo, "fase": FASE, "plano": PLANO, "pets": len(pets), **analisar(pets, lidas, boot=boot)}
    resultado["sem_par_de_momentos"] = {f"{r['braco']}|{r['dono']}|{r['semente']}": r["sem_par_de_momentos"]
                                        for r in registros if r["sem_par_de_momentos"]}
    bv._gravar(pasta / "analise.json", bv._dump(resultado))
    custos = [r["custo"]["pet_parede"] for r in registros]
    bv._gravar(pasta / "custo.json", bv._dump({"pets": len(custos), "parede_media_pet_s": sum(custos) / len(custos),
                                               "parede_max_pet_s": max(custos), "total_parede_s": meta["vidas_parede_s"],
                                               "nota": "cada ramo e vivido duas vezes (G-AD4-2); a base, uma"}))
    meta["fim"] = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
    meta["duracao_s"] = time.time() - inicio
    meta["python"] = platform.python_version()
    meta["artefatos_sha256"] = {n: bv._sha(pasta / n) for n in ("vidas.tar.gz", "perfis.jsonl.gz", "ramos.jsonl", "analise.json", "custo.json")}
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    return {"meta": meta, "registros": registros, "resultado": resultado}


# ================================================================== os perfis gravados (as chaves do par N viram texto)
def _chave(c) -> str:
    b, t = c
    if b == "N" and isinstance(t, tuple):
        return f"N|{t[0]}|{t[1]}"
    return f"{b}|{'' if t is None else t}"


def _de_chave(s: str):
    partes = s.split("|")
    if partes[0] == "N" and len(partes) == 3:
        return ("N", (partes[1], int(partes[2])))
    return (partes[0], None if partes[1] == "" else int(partes[1]))


def linhas_perfis(r: dict) -> list[dict]:
    """uma linha por pet, com os perfis e os parciais, as chaves em texto"""
    return [{"braco": r["braco"], "dono": r["dono"], "semente": r["semente"],
             "perfis": {_chave(c): {str(d): v for d, v in por_dia.items()} for c, por_dia in r["perfis"].items()},
             "parciais": {_chave(c): v for c, v in r["parciais"].items()}}]


def ler_perfis(caminho: Path) -> dict:
    pets = {}
    with gzip.open(caminho, "rt", encoding="utf-8") as f:
        for linha in f:
            x = json.loads(linha)
            pets[(x["braco"], x["dono"], x["semente"])] = {
                "perfis": {_de_chave(c): {int(d): v for d, v in por_dia.items()} for c, por_dia in x["perfis"].items()},
                "parciais": {_de_chave(c): v for c, v in x["parciais"].items()}}
    return pets


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--config", required=True)
    ap.add_argument("--saida", default=None)
    ap.add_argument("--processos", type=int, default=1)
    a = ap.parse_args()
    caminho = Path(a.config)
    cfg = json.loads(caminho.read_text(encoding="utf-8"))
    modo = modo_da_config(cfg)
    if modo == "fumaca" and a.saida is None:
        raise SystemExit(f"a fumaca precisa de --saida (fora de {SAIDA}/)")
    r = rodar(cfg, Path(a.saida) if a.saida else RAIZ / SAIDA, a.processos, caminho)
    res = r["resultado"]
    print(json.dumps({"modo": res["modo"], "pets": res["pets"], "custo_medio_pet_s": r["meta"]["vidas_parede_s"] / res["pets"],
                      "leitura": {b: {"delta_H": v["delta_H"], "ic95": v["ic95"], "leitura": v["leitura"],
                                      "pares_com_grupo": v["pares_com_grupo"]} for b, v in res["por_braco"].items()}},
                     indent=1, ensure_ascii=True))


if __name__ == "__main__":
    main()
