"""As fases da L-2 do longe (docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md, adendo 5, APROVADO pelo Matheus em 2026-10-29;
docs/ESPEC_LONGE_L2_DIGIBRAIN_MODULAR.md, secao 7): o piloto, que so mede o rho para a regra do K (A5.8), e a avaliacao, uma vez, com o K
fixado (A5.9). As vidas sao as do orquestrador do prototipo (experiments/run_v2_digibrain_prototipo.py: o cenario do MVP, os 4 donos, os 3
lugares, 14 dias, 16 interacoes por dia, o G1, o T-CENARIO-1, o G-MECANISMO e o credito por opcao em toda vida) com as medidas do
conserto, mais as da L-2 (A5.3). Os bracos (A5.1): o M3* e o M3*+S (o par primario), o M0 e o M0+S (o par descritivo); o "M3" e o M3* do
conserto (SUBCHAVES_CONSERTO), e o "+S" liga a `intencao_suspensa` (SUBCHAVES_L2).

As fases (o campo "fase" da config; a faixa 67101...67505, reservada para a L-2):
    l2_piloto     bases 67101 e 67202, K = 5 por base (10 unidades), os 4 bracos: o sigma, o rho e o sigma_d das 10 comparacoes do C-L2-3
                  e o K pela regra da A5.8. Nenhum criterio e lido nele
    l2_avaliacao  bases 67303, 67404 e 67505, com o K da A5.9 (o K do piloto, ou o aprovado pelo Matheus), os 4 bracos, uma vez: os
                  criterios C-L2-1 a C-L2-4 (A5.4) e a regra da parte (a) (A5.5)
As duas exigem o adendo 5 APROVADO no cabecalho (`exigir_adendo_aprovado`) e recusam as sementes de qualquer outra fase (o piloto, as da
avaliacao). Na fumaca (as sementes dos testes) as fases rodam sem a faixa, sem a trava e sem o K, com menos dias se a config pedir.

    python experiments/run_v2_digibrain_l2.py --config experiments/configs/v2_digibrain_prototipo/l2_piloto.json --processos 4
"""
from __future__ import annotations

import argparse
import json
import math
import platform
import re
import statistics
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import poder_l2_digibrain as pw  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402
from digilab.metrics import ic_t, n_min_decisoes  # noqa: E402
from digilab.mundo import distancia  # noqa: E402

PLANO = orq.PLANO
PREFIXO = orq.PREFIXO
BASES = {"l2_piloto": (67101, 67202), "l2_avaliacao": (67303, 67404, 67505)}          # A5.2
K_PILOTO = 5                                                                          # A5.2: 10 unidades
SAIDA = {"l2_piloto": "artifacts_v2_digibrain_prototipo/l2/piloto", "l2_avaliacao": "artifacts_v2_digibrain_prototipo/l2/avaliacao"}
BRACOS = ("M3", "M3+S", "M0", "M0+S")                                                 # A5.1
PAR_PRIMARIO, PAR_DESCRITIVO = ("M3", "M3+S"), ("M0", "M0+S")
DIAS, ORCAMENTO_POR_DIA = orq.DIAS, orq.ORCAMENTO_POR_DIA
CHAVES_CONFIG = {"descricao", "plano", "fase", "unidades", "dias", "orcamento_por_dia"}
# a regra do K (A5.8), PROPOSTA, SEM FONTE
GRADE_K = (12, 21, 30, 51, 102, 201)
ALVO_PODER = 0.8
K_MAX_SEM_MATHEUS = 100
MARGEM_TAXAS, MARGEM_CORPO = pw.MARGEM_EP, pw.MARGEM_CORPO                            # -0,03 e +0,02 (C-L2-3)
COMPARACOES_C3 = tuple([(m, lu) for m in ("episodio", "racao") for lu in ("comedouro", "perto")]
                       + [(m, lu) for m in ("exaustao", "privacao") for lu in orq.LUGARES])
# os criterios (A5.4), copiados da espec como estao: PROPOSTOS, SEM FONTE
C1_FRACAO = 0.5               # C-L2-1: as buscas trocadas mais as expiradas caem pelo menos a metade
C4_EXPIROU_MAX = 0.25         # C-L2-4: no maximo 25 % das suspensoes acabam em "expirou"
C4_DIFERENCA_MAX = 0.10       # C-L2-4: a fracao das retomadas em meta ou achou nao fica mais de 0,10 abaixo da das nunca suspensas
BUSCA, IDA = ["comer", "cheiro"], ["comer", "comida"]
PADRAO_K = re.compile(r"^\*\*K fixado: (\d+) unidades\*\*")


# ================================================================== a config e as travas
def _plano() -> str:
    return (RAIZ / PLANO).read_text(encoding="utf-8")


def k_da_avaliacao() -> int:
    """o K da avaliacao (A5.9): o do piloto, registrado no plano numa linha "**K fixado: N unidades**" da subsecao "### A5.9"; se o piloto
    disse "volta ao Matheus", a A5.9 tem de dizer "aprovado pelo Matheus". Sem o piloto ou sem a A5.9, falha alto."""
    caminho = RAIZ / SAIDA["l2_piloto"] / "resultado.json"
    if not caminho.exists():
        raise FileNotFoundError("a avaliacao da L-2 precisa do piloto (A5.8): rode o piloto antes")
    plano = _plano()
    if "### A5.9" not in plano:
        raise RuntimeError("a avaliacao da L-2 precisa do K fixado no plano (A5.9): commit antes")
    if plano.count("\n### A5.9") != 1:
        raise RuntimeError("a A5.9 esta no plano mais de uma vez")
    secao = plano[plano.index("### A5.9"):]
    secao = secao[:secao.index("\n## ")] if "\n## " in secao else secao
    ks = [int(m.group(1)) for x in secao.splitlines() for m in [PADRAO_K.match(x)] if m]
    if len(ks) != 1:
        raise RuntimeError(f"a A5.9 tem de ter uma linha '**K fixado: N unidades**', e tem {len(ks)}")
    k = ks[0]
    regra = json.loads(caminho.read_text(encoding="utf-8"))["regra_do_k"]
    if regra["k"] is None or regra["k"] > K_MAX_SEM_MATHEUS:
        if "aprovado pelo Matheus" not in secao:
            raise RuntimeError("o piloto mandou o K ao Matheus (A5.8): a A5.9 tem de trazer o K aprovado por ele")
    elif k != regra["k"]:
        raise RuntimeError(f"o K da A5.9 ({k}) nao e o da regra do piloto ({regra['k']})")
    if k % len(BASES["l2_avaliacao"]):
        raise RuntimeError(f"o K {k} nao se divide pelas {len(BASES['l2_avaliacao'])} bases da avaliacao")
    return k


def modo_da_config(cfg: dict) -> str:
    """'fumaca' (as sementes dos testes) ou a fase ('l2_piloto', 'l2_avaliacao'), que segue o adendo 5 a letra"""
    faltam, sobram = (CHAVES_CONFIG - {"descricao"}) - set(cfg), set(cfg) - CHAVES_CONFIG
    if faltam or sobram:
        raise ValueError(f"config: faltam {sorted(faltam)}, sobram {sorted(sobram)}")
    fase = cfg["fase"]
    if fase not in BASES:
        raise ValueError(f"fase {fase!r}: so {sorted(BASES)}")
    u = cfg["unidades"]
    bases = tuple(u["bases"])
    if u.get("prefixo") != PREFIXO or cfg["orcamento_por_dia"] != ORCAMENTO_POR_DIA or type(u.get("k")) is not int or u["k"] < 1:
        raise ValueError("config fora do plano: o prefixo, o orcamento (secao 3) ou o K")
    outras = set().union(*(range(b[0], b[-1] + 1) for b in orq.BASES.values()),
                         *(range(b[0], b[-1] + 1) for f, b in BASES.items() if f != fase))
    if set(bases) & outras:
        raise bv.SementeSemPlano(f"a {fase} recusa as sementes das outras fases (A5.2)")
    if set(bases) <= bv.SEMENTES_TESTE:
        if not 1 <= cfg["dias"] <= DIAS:
            raise ValueError(f"fumaca com {cfg['dias']} dias: de 1 a {DIAS}")
        return "fumaca"
    if bases != BASES[fase]:
        raise bv.SementeSemPlano(f"bases {list(bases)}: so as dos testes (fumaca) ou {list(BASES[fase])} ({fase}, A5.2)")
    orq.exigir_adendo_aprovado(_plano(), 5)
    erros = []
    if cfg["dias"] != DIAS:
        erros.append(f"dias {cfg['dias']} (o plano: {DIAS})")
    if cfg.get("plano") != PLANO:
        erros.append(f"plano {cfg.get('plano')!r}")
    k = K_PILOTO if fase == "l2_piloto" else k_da_avaliacao() // len(BASES[fase])
    if u["k"] != k:
        erros.append(f"K por base {u['k']} (o plano: {k})")
    if erros:
        raise ValueError(f"a {fase} segue o adendo 5 a letra: {erros}")
    return fase


# ================================================================== as medidas da L-2 (A5.3), por vida
def medidas_l2(motor, registro, episodios: list) -> dict:
    """as medidas do registro da decisao: as buscas e as idas, com os fins, o motivo da troca (o reflexo, outra unidade com racao madura a
    menos de R, outra sem) e a vencedora; o C-L2-1; as S-1 a S-4 e a S-6 (a S-5 e a exaustao e a privacao de hoje). Sem a subchave, as
    medidas da suspensao saem 0 (nada e suspenso)."""
    c = orq.cerebro_de(registro)
    ms = c.motivos
    passo = orq.CONFIG_PADRAO.intervalo_decisao_ticks
    entrada = motor.entrada_mundo
    dm = motor.decisoes_mundo
    n = len(ms)
    if len(dm) != n or any(d["tick"] - entrada != k * passo for k, d in enumerate(dm)):
        raise RuntimeError("as decisoes do mundo nao sao as do cerebro, uma por decisao, no tick k x 15")
    pos = [tuple(d["antes"]) for d in dm]
    R = orq.CM.raio_cheiro_celulas * orq.CM.sub
    g = orq.geometria()
    k_comida = {cm["id"]: (cm["tick"] - entrada) // passo for cm in motor.consumos_mundo}
    racoes = {d["id"]: d for d in motor.deixadas if d["tipo"] == "racao"}

    def oferta(k: int) -> dict:
        x, y = pos[k]
        return {i: distancia(d["x"] - x, d["y"] - y) for i, d in racoes.items()
                if orq._no_chao(d["tick"] - entrada, k_comida.get(i), k, passo, orq.CM.maduro_racao_min)}

    def tipo(chave) -> str | None:
        return {"comer/cheiro": "busca", "comer/comida": "ida"}.get(f"{chave[0]}/{chave[1]}")

    fins = {t: {} for t in ("busca", "ida")}
    trocas = {t: {"reflexo": 0, "outra_com_racao_em_R": 0, "outra_sem_racao_em_R": 0, "por_vencedora": {}} for t in ("busca", "ida")}
    suspensas = {"fins": 0, "expirou": 0, "n_susp": [], "meta_ou_achou": 0}
    nunca = {"fins": 0, "meta_ou_achou": 0}
    for k, m in enumerate(ms):
        for f in m["fins"]:
            t = tipo(f["chave"])
            if t is None:
                continue
            fins[t][f["motivo"]] = fins[t].get(f["motivo"], 0) + 1
            if f["motivo"] == "trocou":
                tr = trocas[t]
                v = "/".join(str(x) for x in m["escolha"][:2])
                tr["por_vencedora"][v] = tr["por_vencedora"].get(v, 0) + 1
                if m["reflexo"]:
                    tr["reflexo"] += 1
                elif any(d < R for d in oferta(k).values()):
                    tr["outra_com_racao_em_R"] += 1
                else:
                    tr["outra_sem_racao_em_R"] += 1
            if t == "busca":                                   # S-1 e S-2, nas buscas
                alvo = suspensas if "n_susp" in f else nunca
                alvo["fins"] += 1
                alvo["meta_ou_achou"] += f["motivo"] in ("meta", "achou")
                if "n_susp" in f:
                    suspensas["expirou"] += f["motivo"] == "expirou"
                    suspensas["n_susp"].append(f["n_susp"])
    # as suspensoes de toda intencao (S-1, o C-L2-4): os fins com o n_susp, busca e ida
    todas = [f for m in ms for f in m["fins"] if "n_susp" in f]
    # S-3, S-4 e S-6: as decisoes com a retomada
    retomadas = [k for k, m in enumerate(ms) if m.get("retomou")]
    andado = []
    for k in retomadas:
        chave = ms[k]["estado"]["I"]
        of = oferta(k)
        if chave is None or not of:
            continue
        fim = next((j for j in range(k, n) for f in ms[j]["fins"] if f["chave"] == chave and "n_susp" in f), None)
        if fim is None:
            continue
        alvo = racoes[min(of, key=lambda i: (of[i], i))]
        d0 = distancia(alvo["x"] - pos[k][0], alvo["y"] - pos[k][1])
        d1 = distancia(alvo["x"] - pos[fim][0], alvo["y"] - pos[fim][1])
        andado.append((d0 - d1) / g["passo"])
    return {
        "fins": {t: dict(sorted(v.items())) for t, v in fins.items()},
        "trocas": trocas,
        "c_l2_1": fins["busca"].get("trocou", 0) + fins["busca"].get("expirou", 0),
        "s1": {"suspensas": len(todas), "expiradas": sum(1 for f in todas if f["motivo"] == "expirou"),
               "n_susp_soma": sum(f["n_susp"] for f in todas)},
        "s2": {"buscas_suspensas": suspensas["fins"], "buscas_suspensas_meta_ou_achou": suspensas["meta_ou_achou"],
               "buscas_nunca_suspensas": nunca["fins"], "buscas_nunca_suspensas_meta_ou_achou": nunca["meta_ou_achou"]},
        "s3": {"retomadas_com_alvo": len(andado), "andado_liquido_soma": sum(andado),
               "andado_liquido_ate_zero": sum(1 for a in andado if a <= 0)},
        "s4": {"retomadas": len(retomadas), "reflexo_em_2": sum(1 for k in retomadas if any(ms[j]["reflexo"] for j in (k + 1, k + 2)
                                                                                          if j < n))},
        "s6": {"retomadas": len(retomadas), "persistencia_decidiu": sum(1 for k in retomadas if ms[k]["sondas"]["persistencia_decidiu"])},
        "m_l3": _andado_dos_episodios(episodios, pos, racoes, oferta,
                                      {(cm["tick"] - entrada) // passo: cm["id"] for cm in motor.consumos_mundo if cm["id"] in racoes}, g),
    }


def _andado_dos_episodios(episodios: list, pos: list, racoes: dict, oferta, comeu_em: dict, g: dict) -> dict:
    """o M-L3 da L0 refeito, descritivo: em cada episodio de fome, o andado liquido em direcao ao alvo (a racao comida, ou a madura mais
    perto na abertura), em passos, contra o n_min(d0); somado por vida, nos fechados e nos nao fechados"""
    out = {nome: {"episodios": 0, "liquido_soma": 0.0, "ao_menos_n_min": 0} for nome in ("fechados", "nao_fechados")}
    for k_i, d0, _w, fim, motivo in episodios:
        of = oferta(k_i)
        if not of or min(of.values()) != d0:
            raise RuntimeError(f"a oferta da abertura {k_i} nao da o d0 gravado")
        alvo = comeu_em.get(fim) if motivo == "fechou" else min(of, key=lambda i: (of[i], i))
        if alvo is None:
            raise RuntimeError(f"o episodio fechado em {fim} sem a racao comida")
        rx, ry = racoes[alvo]["x"], racoes[alvo]["y"]
        liquido = (distancia(rx - pos[k_i][0], ry - pos[k_i][1]) - distancia(rx - pos[fim][0], ry - pos[fim][1])) / g["passo"]
        o = out["fechados" if motivo == "fechou" else "nao_fechados"]
        o["episodios"] += 1
        o["liquido_soma"] += liquido
        o["ao_menos_n_min"] += liquido >= n_min_decisoes(d0, g["raio_pegar"], g["passo"])
    return out


def _vida(cfg: dict, braco: str, dono: str, lugar: str, unidade: dict, pasta: str) -> dict:
    """uma vida: vivida, gravada, rejogada do disco (G1), conferida (as falhas altas) e medida, como no orquestrador do prototipo"""
    c0, p0 = time.process_time(), time.perf_counter()
    motor, registro, fab = orq.viver(braco, dono, lugar, unidade["semente"], cfg["dias"], cfg["orcamento_por_dia"], conserto=True)
    arquivo = Path(pasta) / "vidas" / braco / f"{dono}_{lugar}_{unidade['semente']}.jsonl"
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    arquivo.write_text(motor.log.para_jsonl(), encoding="utf-8", newline="\n")
    orq.conferir_replay(motor, fab, unidade["semente"], arquivo.read_text(encoding="utf-8"))
    orq.conferir_cenario(motor, registro)
    orq.conferir_mecanismo(braco, registro, None)
    med = orq.medidas(motor, registro, braco, cfg["dias"], True)
    return {"vida": f"{braco}|{dono}|{lugar}|{unidade['semente']}", "braco": braco, "dono": dono, "lugar": lugar,
            "semente": unidade["semente"], "base": unidade["base"], "k": unidade["k"], **med,
            "l2": medidas_l2(motor, registro, med["episodios_fome"]["episodios"]),
            "custo": {"vida_cpu": time.process_time() - c0, "vida_parede": time.perf_counter() - p0}}


def tarefa(cfg: dict, unidade: dict, pasta: str) -> list[dict]:
    return [_vida(cfg, b, dono, lugar, unidade, pasta) for b in BRACOS for dono, lugar in orq.CELULAS]


# ================================================================== a analise
MEDIDAS = {"episodio": lambda r: r["episodios_fome"]["taxa"], "racao": lambda r: r["cadeia"]["taxa"],
           "exaustao": lambda r: r["exaustao"], "privacao": lambda r: r["privacao"], "c_l2_1": lambda r: r["l2"]["c_l2_1"]}


def _celulas(lugar: str) -> list:
    return [(d, lugar) for d in orq.DONOS]


def valores(registros: list[dict], braco: str, medida: str, lugar: str) -> dict:
    """{(base, semente): a media da medida nas 4 celulas do lugar} (a unidade da A5.4)"""
    return orq.por_unidade(registros, braco, None, MEDIDAS[medida], _celulas(lugar))


def _pareados(registros: list[dict], par: tuple, medida: str, lugar: str) -> tuple[list, list]:
    a, b = valores(registros, par[0], medida, lugar), valores(registros, par[1], medida, lugar)
    if set(a) != set(b):
        raise RuntimeError(f"{medida}/{lugar}: as unidades dos dois bracos do par {par} nao sao as mesmas")
    chaves = sorted(a)
    return [a[c] for c in chaves], [b[c] for c in chaves]


def _pearson(xs: list, ys: list) -> float | None:
    if len(xs) < 2:
        return None
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if sx == 0 or sy == 0:
        return None
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sx * sy)


def comparacao_do_piloto(registros: list[dict], medida: str, lugar: str) -> dict:
    """uma das 10 comparacoes do C-L2-3 no piloto (A5.8): os sigma, o rho, o sigma_d (pela formula e pelas diferencas, conferidos) e o
    poder em cada K da grade"""
    a, b = _pareados(registros, PAR_PRIMARIO, medida, lugar)
    margem = MARGEM_TAXAS if medida in ("episodio", "racao") else MARGEM_CORPO
    out = {"unidades": len(a), "margem": margem, "media_M3": statistics.fmean(a) if a else None,
           "media_M3+S": statistics.fmean(b) if b else None}
    if len(a) < 2:
        return {**out, "sigma_M3": None, "sigma_M3+S": None, "rho": None, "sigma_d": None, "poder": None, "motivo": "menos de 2 unidades"}
    sa, sb = statistics.stdev(a), statistics.stdev(b)
    rho = _pearson(a, b)
    sd = statistics.stdev([y - x for x, y in zip(a, b)])
    if rho is not None:                       # as duas contas do sigma_d (A5.8), comparadas nos quadrados (o arredondamento perto de 0)
        formula2 = sa * sa + sb * sb - 2 * rho * sa * sb
        if abs(formula2 - sd * sd) > 1e-9 * (sa * sa + sb * sb):
            raise RuntimeError(f"{medida}/{lugar}: o sigma_d pela formula ({formula2} ao quadrado) nao e o das diferencas ({sd})")
    poder = {str(k): (1.0 if sd == 0 else pw.poder(abs(margem) / sd, k)) for k in GRADE_K}
    return {**out, "sigma_M3": sa, "sigma_M3+S": sb, "rho": rho, "sigma_d": sd, "poder": poder, "motivo": None}


def regra_do_k(comparacoes: dict) -> dict:
    """a regra da A5.8: a conjuncao (o produto dos 10 poderes) em cada K da grade; o K e o menor com a conjuncao >= 0,8; acima de 100, ou
    sem K, volta ao Matheus com o custo"""
    custo = {str(kk): {"vidas": kk * len(BRACOS) * len(orq.CELULAS)} for kk in GRADE_K}
    if any(c["poder"] is None for c in comparacoes.values()):
        return {"k": None, "k_por_base": None, "volta_ao_matheus": True, "conjuncao": None, "alvo": ALVO_PODER, "grade": list(GRADE_K),
                "custo": custo, "motivo": "o piloto sem o poder de alguma comparacao"}
    conj = {str(k): math.prod(c["poder"][str(k)] for c in comparacoes.values()) for k in GRADE_K}
    k = next((k for k in GRADE_K if conj[str(k)] >= ALVO_PODER), None)
    return {"k": k, "k_por_base": None if k is None else k // len(BASES["l2_avaliacao"]),
            "volta_ao_matheus": k is None or k > K_MAX_SEM_MATHEUS, "conjuncao": conj, "alvo": ALVO_PODER, "grade": list(GRADE_K),
            "custo": custo, "motivo": None if k is not None else f"nenhum K da grade chega a {ALVO_PODER}"}


def _soma(vs: list[dict], f) -> float:
    return sum(f(r) for r in vs)


def mecanismo(registros: list[dict]) -> dict:
    """o que a suspensao fez, por braco e lugar, so de leitura (por vida: as buscas trocadas, pelo motivo, as expiradas, o C-L2-1, as
    suspensoes e as retomadas)"""
    out = {}
    for b in BRACOS:
        for lu in orq.LUGARES:
            vs = [r for r in registros if r["braco"] == b and r["lugar"] == lu]
            if not vs:
                continue
            n = len(vs)
            out[f"{b}|{lu}"] = {
                "vidas": n,
                "buscas_trocadas_por_vida": _soma(vs, lambda r: r["l2"]["fins"]["busca"].get("trocou", 0)) / n,
                "buscas_trocadas_pelo_reflexo_por_vida": _soma(vs, lambda r: r["l2"]["trocas"]["busca"]["reflexo"]) / n,
                "buscas_trocadas_por_outra_com_racao_em_R_por_vida":
                    _soma(vs, lambda r: r["l2"]["trocas"]["busca"]["outra_com_racao_em_R"]) / n,
                "buscas_expiradas_por_vida": _soma(vs, lambda r: r["l2"]["fins"]["busca"].get("expirou", 0)) / n,
                "c_l2_1_por_vida": _soma(vs, lambda r: r["l2"]["c_l2_1"]) / n,
                "intencoes_suspensas_que_acabaram_por_vida": _soma(vs, lambda r: r["l2"]["s1"]["suspensas"]) / n,
                "retomadas_por_vida": _soma(vs, lambda r: r["l2"]["s4"]["retomadas"]) / n}
    return out


def _fracao(a: float, b: float) -> float | None:
    return a / b if b else None


def _diferenca(registros: list[dict], par: tuple, medida: str, lugar: str) -> dict:
    a, b = _pareados(registros, par, medida, lugar)
    ic = ic_t([y - x for x, y in zip(a, b)])
    return {"media_a": statistics.fmean(a) if a else None, "media_b": statistics.fmean(b) if b else None, "diferenca": ic["media"],
            "ic95": {"ic_inferior": ic["ic_inferior"], "ic_superior": ic["ic_superior"]}, "unidades": ic["n"], "motivo": ic["motivo"]}


def criterios(registros: list[dict]) -> dict:
    """os criterios da A5.4 no par primario, como estao (PROPOSTOS, SEM FONTE), e a regra da parte (a) da A5.5"""
    c1 = _diferenca(registros, PAR_PRIMARIO, "c_l2_1", "longe")
    c1["passa"] = (c1["ic95"]["ic_superior"] is not None and c1["media_b"] <= C1_FRACAO * c1["media_a"]
                   and c1["ic95"]["ic_superior"] < 0)
    c2 = _diferenca(registros, PAR_PRIMARIO, "episodio", "longe")
    c2["passa"] = c2["ic95"]["ic_inferior"] is not None and c2["ic95"]["ic_inferior"] > 0
    c3 = {}
    for medida, lugar in COMPARACOES_C3:
        d = _diferenca(registros, PAR_PRIMARIO, medida, lugar)
        if medida in ("episodio", "racao"):
            d["margem"] = MARGEM_TAXAS
            d["passa"] = d["ic95"]["ic_inferior"] is not None and d["ic95"]["ic_inferior"] > MARGEM_TAXAS
        else:
            d["margem"] = MARGEM_CORPO
            d["passa"] = d["ic95"]["ic_superior"] is not None and d["ic95"]["ic_superior"] < MARGEM_CORPO
        c3[f"{medida}|{lugar}"] = d
    s = [r for r in registros if r["braco"] == "M3+S"]
    susp = _soma(s, lambda r: r["l2"]["s1"]["suspensas"])
    exp = _soma(s, lambda r: r["l2"]["s1"]["expiradas"])
    f_susp = _fracao(_soma(s, lambda r: r["l2"]["s2"]["buscas_suspensas_meta_ou_achou"]),
                     _soma(s, lambda r: r["l2"]["s2"]["buscas_suspensas"]))
    f_nunca = _fracao(_soma(s, lambda r: r["l2"]["s2"]["buscas_nunca_suspensas_meta_ou_achou"]),
                      _soma(s, lambda r: r["l2"]["s2"]["buscas_nunca_suspensas"]))
    frac_exp = _fracao(exp, susp)
    c4 = {"suspensoes": susp, "expiradas": exp, "frac_expirou": frac_exp, "frac_meta_ou_achou_suspensas": f_susp,
          "frac_meta_ou_achou_nunca_suspensas": f_nunca,
          "passa": (frac_exp is not None and f_susp is not None and f_nunca is not None and frac_exp <= C4_EXPIROU_MAX
                    and f_susp >= f_nunca - C4_DIFERENCA_MAX)}
    c3_passa = all(d["passa"] for d in c3.values())
    por_vida = mecanismo(registros)
    outra = {lu: por_vida[f"M3+S|{lu}"]["buscas_trocadas_por_outra_com_racao_em_R_por_vida"] for lu in ("longe", "comedouro")}
    parte_a = {"outra_com_racao_em_R_por_vida": outra,
               "volta_ao_matheus": c1["passa"] and c3_passa and outra["longe"] > 2 * outra["comedouro"] and not c2["passa"]}
    return {"limiares": {"C-L2-1": C1_FRACAO, "C-L2-3": {"taxas": MARGEM_TAXAS, "corpo": MARGEM_CORPO},
                         "C-L2-4": {"expirou_max": C4_EXPIROU_MAX, "diferenca_max": C4_DIFERENCA_MAX},
                         "status": "PROPOSTOS, SEM FONTE (a espec, secao 7.3; a LS-7 os aprovou sem muda-los)"},
            "C-L2-1": c1, "C-L2-2": c2, "C-L2-3": {"comparacoes": c3, "passa": c3_passa}, "C-L2-4": c4, "parte_a": parte_a,
            "leitura": {"segue_para_o_jogo": c1["passa"] and c3_passa and c4["passa"], "o_longe_melhorou": c2["passa"],
                        "nao_afirma": "nem que a L-2 conserta o longe, nem que o modular supera o A, nem prontidao (a espec, secao 8)"}}


def descritivos(registros: list[dict]) -> dict:
    """o par descritivo (M0 x M0+S) e a taxa por racao no longe, sem criterio; as S-3, S-4, S-6 e o M-L3 somados por braco e lugar"""
    extras = (("episodio", "longe"), ("c_l2_1", "longe"))
    desc = {"M0_x_M0+S": {f"{m}|{lu}": _diferenca(registros, PAR_DESCRITIVO, m, lu) for m, lu in COMPARACOES_C3 + extras},
            "racao_longe_M3_x_M3+S": _diferenca(registros, PAR_PRIMARIO, "racao", "longe")}
    somas = {}
    for b in BRACOS:
        for lu in orq.LUGARES:
            l2 = [r["l2"] for r in registros if r["braco"] == b and r["lugar"] == lu]
            if not l2:
                continue
            com_alvo = sum(x["s3"]["retomadas_com_alvo"] for x in l2)
            somas[f"{b}|{lu}"] = {
                "s3": {"retomadas_com_alvo": com_alvo,
                       "andado_liquido_medio": _fracao(sum(x["s3"]["andado_liquido_soma"] for x in l2), com_alvo),
                       "andado_ate_zero": sum(x["s3"]["andado_liquido_ate_zero"] for x in l2)},
                "s4": {"retomadas": sum(x["s4"]["retomadas"] for x in l2), "reflexo_em_2": sum(x["s4"]["reflexo_em_2"] for x in l2)},
                "s6": {"retomadas": sum(x["s6"]["retomadas"] for x in l2),
                       "persistencia_decidiu": sum(x["s6"]["persistencia_decidiu"] for x in l2)},
                "m_l3": {nome: {k: sum(x["m_l3"][nome][k] for x in l2) for k in ("episodios", "liquido_soma", "ao_menos_n_min")}
                         for nome in ("fechados", "nao_fechados")}}
    desc["somas"] = somas
    return desc


def analisar(registros: list[dict], fase: str) -> dict:
    """o piloto: as 10 comparacoes, a regra do K e o mecanismo, sem criterio; a avaliacao: os criterios, o mecanismo e os descritivos"""
    if fase == "l2_piloto":
        comps = {f"{m}|{lu}": comparacao_do_piloto(registros, m, lu) for m, lu in COMPARACOES_C3}
        return {"aviso": "o piloto so serve para a regra do K (A5.8): nenhum criterio e lido nele, e os numeros dele nao sao evidencia",
                "comparacoes": comps, "regra_do_k": regra_do_k(comps), "mecanismo": mecanismo(registros)}
    return {"criterios": criterios(registros), "mecanismo": mecanismo(registros), "descritivos": descritivos(registros)}


# ================================================================== a run
def rodar(cfg: dict, pasta: Path, processos: int, caminho_config: Path | None = None) -> dict:
    if processos > 4:
        raise ValueError("no maximo 4 processos (a maquina; o adendo 5)")
    modo = modo_da_config(cfg)
    fase = cfg["fase"]
    if pasta.exists():
        raise FileExistsError(f"{pasta} ja existe: a run se recusa a gravar por cima (uma vez)")
    unidades = bv.unidades_derivadas(cfg["unidades"]["bases"], int(cfg["unidades"]["k"]), PREFIXO)
    pasta.mkdir(parents=True)
    inicio = time.time()
    rc = orq.rc
    meta = {"modo": modo, "fase": fase, "plano": PLANO, "plano_sha256": rc._sha_arquivo(RAIZ / PLANO), "config": cfg,
            "config_arquivo": None if caminho_config is None else rc._relativo(caminho_config),
            "config_sha256": None if caminho_config is None else rc._sha_arquivo(caminho_config),
            "orquestrador_sha256": rc._sha_arquivo(Path(__file__)), "prototipo_sha256": rc._sha_arquivo(Path(orq.__file__)),
            "git_head": rc._git("rev-parse", "HEAD"), "git_limpo": rc._git("status", "--porcelain") == "", "processos": processos,
            "unidades": unidades, "bracos": {b: {**orq.SUBCHAVES_CONSERTO, **orq.SUBCHAVES_L2}[b] for b in BRACOS},
            "inatos": json.loads(json.dumps(orq.CONFIG_DIGIBRAIN_INATOS.__dict__)),
            "sha256": {n: rc._sha_arquivo(RAIZ / "digilab" / n) for n in ("config.py", "engine.py", "metrics.py")}
            | {f"digibrain/{p.name}": rc._sha_arquivo(p) for p in sorted((RAIZ / "digilab" / "digibrain").glob("*.py"))},
            "inicio": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(inicio))}
    if fase == "l2_avaliacao" and modo == "l2_avaliacao":
        meta["k_fixado"] = k_da_avaliacao()
        meta["piloto_resultado_sha256"] = rc._sha_arquivo(RAIZ / SAIDA["l2_piloto"] / "resultado.json")
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    t0 = time.perf_counter()
    registros = [r for s in rc._executar([(tarefa, (cfg, u, str(pasta))) for u in unidades], processos) for r in s]
    meta["vidas_parede_s"] = time.perf_counter() - t0
    resultado = {"modo": modo, "fase": fase, "plano": PLANO, **analisar(registros, fase)}
    meta["fim"] = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
    meta["duracao_s"] = time.time() - inicio
    meta["python"] = platform.python_version()
    bv._gravar(pasta / "medidas.json", bv._dump({r["vida"]: r for r in sorted(registros, key=lambda r: r["vida"])}))
    bv._gravar(pasta / "resultado.json", bv._dump(resultado))
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    return {"meta": meta, "registros": registros, "resultado": resultado}


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
        raise SystemExit("a fumaca precisa de --saida (fora de artifacts_v2_digibrain_prototipo/)")
    saida = Path(a.saida) if a.saida else RAIZ / SAIDA[cfg["fase"]]
    r = rodar(cfg, saida, a.processos, caminho)["resultado"]
    print(json.dumps({k: v for k, v in r.items() if k != "descritivos"}, indent=1, ensure_ascii=False, default=str)[:4000])


if __name__ == "__main__":
    main()
