"""V2, MUNDO-CALIBRACAO: a calibracao do mundo fisico (docs/PLANO_ANALISE_V2_MUNDO_FISICO.md, secao 6 e adendo 1, A1.4; autorizada pelo
Matheus em 2026-10-12). Pela bancada (experiments/bancada_v2.py), no mundo `fisico` (o MotorMundo, condicao iguais), nas unidades
derivadas das bases 31101...31505 (K = 4, prefixo "mundo") ou, na fumaca, nas sementes dos testes. As da validacao (32101...32505) nunca:
o modo vem das sementes e recusa o resto.

As etapas, numa run so:
    grade   P0 e P0z, m em {1/2, 1, 2} sobre o p_queda do jardim e da mata (ConfigMundo.mult_queda), 12 celulas (dono x lugar)
    regra   o MENOR m com o limite inferior do IC95 de (P0z - P0) em D_FE acima de 0 (secao 6, PMF-5); sem nenhum, para e relata
    piloto  no m escolhido: P1, P0^ac e P1^ac (acoplados ao P0z da mesma celula, filtro nenhum; A1.4), 36 vidas por unidade
    N       Delta_MF = 1/2 x (P0z - P0) em D_FE; o menor K de 4 a 10 por base com poder simulado >= 0,8 no G-MF1r (bootstrap das
            diferencas P0 - P1 do piloto, centradas e deslocadas para Delta_MF, 2.000 replicas por K); o poder do G-MF2r e do G-MF3r
            no N escolhido, so relato; o custo medido por vida e a estimativa da validacao

O P1 nao entra na escolha do mundo (PMF-5): a regra so le o P0 e o P0z. O piloto serve so para o N. Toda vida e gravada e rejogada do
disco bit a bit (Bancada.conferir_replay); o replay de medicao tambem confere. A run se recusa a rodar se a pasta de saida existe.

    python experiments/run_v2_calibracao_mundo.py --config experiments/configs/v2_mundo/calibracao.json --processos 6
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v2_experimento_maior as em  # noqa: E402
from digilab.metrics import contraste_pareado  # noqa: E402

PLANO = "docs/PLANO_ANALISE_V2_MUNDO_FISICO.md"
SAIDA_PADRAO = "artifacts_v2_mundo/calibracao"
PREFIXO = "mundo"
BASES_CALIBRACAO = (31101, 31202, 31303, 31404, 31505)    # secao 11 (PMF-6)
BASES_VALIDACAO = (32101, 32202, 32303, 32404, 32505)     # secao 7: precisa de outro sim; aqui, recusada
K_CALIBRACAO = 4
GRADE_M = (0.5, 1.0, 2.0)                                 # secao 6
DONOS_V1 = ("atencioso", "relapso", "aleatorio", "incoerente")   # secao 2
LUGARES = ("comedouro", "perto", "longe")                 # PMF-4
DIAS_PLANO = 14
ORCAMENTO_PLANO = 224
MUNDO = "fisico"                                          # PMF-7: o mundo "iguais"
BRACOS_GRADE = ("P0", "P0z")                              # secao 6: so o instinto escolhe o mundo
PILOTO_PLANO = {"bracos": ["P1"], "acoplados": [{"origem": "P0z", "destino": "P0", "filtro": "nenhum"},
                                                 {"origem": "P0z", "destino": "P1", "filtro": "nenhum"}]}   # A1.4
PODER_PLANO = {"k_min": 4, "k_max": 10, "replicas": 2000, "alvo": 0.8}                                     # A1.4
ALFA_G_MF1 = 0.025      # "o P1 ganha" = limite inferior do IC95 > 0: o teste unilateral a 2,5% (a mesma conta do adendo 2 da V1)
ROT_P0AC = "P0<P0z:nenhum"
ROT_P1AC = "P1<P0z:nenhum"
BRACOS_VALIDACAO = ("P0", "P0z", "P1", ROT_P0AC, ROT_P1AC)   # A1.2: 60 vidas por unidade
BRACOS_AFASTADO = ("P0", "P1")                               # A1.8: o bloco do layout afastado, +24 vidas por unidade
CHAVES_DESLIGADAS = ("banheiro", "corpo", "metabolismo", "gestos", "grupo", "alvo_aprendido", "entradas_sociais", "modelo_outros",
                     "presenca_fruta_mundo", "pesos_janela", "rede_de_si", "julgamento_fruta", "calendario_informacao_pedido")
CHAVES_CONFIG = {"descricao", "plano", "donos", "unidades", "mundo", "lugares", "dias", "orcamento", "ponto", "montagem", "lobos",
                 "consequencia", "sonda", "bootstrap", "grade_m", "piloto", "poder", "chaves_desligadas"}


# ================================================================== a config
def rotulo_m(m: float) -> str:
    return f"{m:g}"


def modo_da_config(cfg: dict) -> str:
    """'fumaca' (bases nas sementes dos testes) ou 'calibracao' (as bases 31101...31505, K = 4, o plano). O resto falha alto: as
    sementes da validacao precisam de outro sim, e qualquer outra faixa nao e deste plano."""
    faltam = CHAVES_CONFIG - {"descricao", "plano"} - set(cfg)
    sobram = set(cfg) - CHAVES_CONFIG
    if faltam or sobram:
        raise ValueError(f"config: faltam {sorted(faltam)}, sobram {sorted(sobram)}")
    u = cfg["unidades"]
    bases = tuple(u["bases"])
    if u.get("prefixo") != PREFIXO:
        raise ValueError(f"unidades: o prefixo do plano e {PREFIXO!r} (secao 4), nao {u.get('prefixo')!r}")
    if cfg["mundo"] != MUNDO:
        raise ValueError(f"o mundo do plano e {MUNDO!r} (PMF-7), nao {cfg['mundo']!r}")
    if set(cfg["chaves_desligadas"]) != set(CHAVES_DESLIGADAS):
        raise ValueError(f"chaves_desligadas: o registro tem de ser {sorted(CHAVES_DESLIGADAS)}")
    if set(cfg["donos"]) - set(DONOS_V1) or set(cfg["lugares"]) - set(LUGARES) or not cfg["donos"] or not cfg["lugares"]:
        raise ValueError("donos e lugares do plano: os 4 da v1 e comedouro, perto, longe")
    if any(m <= 0 for m in cfg["grade_m"]) or list(cfg["grade_m"]) != sorted(cfg["grade_m"]):
        raise ValueError("grade_m: positiva e em ordem crescente (a regra pega o menor)")
    if set(bases) & set(range(BASES_VALIDACAO[0], BASES_VALIDACAO[-1] + 1)):
        raise bv.SementeSemPlano("as bases da validacao (32101...32505) precisam de outro sim do Matheus (tarefa, item 5)")
    if set(bases) <= bv.SEMENTES_TESTE:
        return "fumaca"
    if bases != BASES_CALIBRACAO:
        raise bv.SementeSemPlano(f"bases {list(bases)}: so as dos testes (fumaca) ou {list(BASES_CALIBRACAO)} (calibracao, secao 11)")
    erros = []
    if cfg.get("plano") != PLANO:
        erros.append(f"plano {cfg.get('plano')!r}")
    if u["k"] != K_CALIBRACAO:
        erros.append(f"K {u['k']}")
    if tuple(sorted(cfg["donos"])) != tuple(sorted(DONOS_V1)) or tuple(cfg["lugares"]) != LUGARES:
        erros.append("donos ou lugares")
    if cfg["dias"] != DIAS_PLANO or cfg["orcamento"] != ORCAMENTO_PLANO:
        erros.append("dias ou orcamento")
    if tuple(cfg["grade_m"]) != GRADE_M:
        erros.append(f"grade {cfg['grade_m']}")
    if cfg["piloto"] != PILOTO_PLANO:
        erros.append("piloto")
    if {k: cfg["poder"][k] for k in PODER_PLANO} != PODER_PLANO or cfg["poder"].get("alfa") != ALFA_G_MF1:
        erros.append("poder")
    if cfg["bootstrap"] != {"reamostragens": 10000, "semente": 4242, "nivel": 0.95}:
        erros.append("bootstrap (secao 7: 10.000 reamostragens, semente 4242)")
    if erros:
        raise ValueError(f"a calibracao segue o plano a letra: {erros}")
    return "calibracao"


def config_bancada(cfg: dict, m: float, bracos: list[str], acoplados: list[dict] | None = None) -> dict:
    """A config da bancada de um ponto m da grade (ou do piloto): o mundo fisico com o `mult_queda` = m."""
    out = {"bracos": list(bracos), "donos": list(cfg["donos"]), "unidades": dict(cfg["unidades"]), "mundos": [cfg["mundo"]],
           "lugares": list(cfg["lugares"]), "dias": cfg["dias"], "orcamento": cfg["orcamento"], "ponto": cfg["ponto"],
           "montagem": cfg["montagem"], "lobos": dict(cfg["lobos"]), "consequencia": dict(cfg["consequencia"]),
           "sonda": dict(cfg["sonda"]), "bootstrap": dict(cfg["bootstrap"]), "mundo": {"mult_queda": m}}
    if cfg.get("plano"):
        out["plano"] = cfg["plano"]
    if acoplados:
        out["acoplados"] = [dict(a) for a in acoplados]
    return bv.validar_config(out)


def conferir_desligadas(b: bv.Bancada, cfg_b: dict, unidade: dict) -> dict:
    """As chaves novas que o plano nao pede, desligadas de fato em todo braco do plano (falha alto): o que cada um monta."""
    if "corpo" in cfg_b or "julgamento_fruta" in cfg_b or b.julgamento_fruta:
        raise RuntimeError("a config liga o corpo ou o julgamento da fruta")
    if b.cfg_consequencia.pesos_janela:
        raise RuntimeError("pesos_janela ligada na consequencia")
    out = {}
    for braco in ("P0", "P0z", "P1"):
        espec = bv.EspecVida(cfg_b["donos"][0], braco, unidade["semente"], unidade["genoma"], MUNDO, lugar=cfg_b["lugares"][0])
        br = bv.braco_de(braco)
        if br.regime is not None or br.banheiro is not None or br.metabolismo or br.gestos is not None or br.pesos_janela:
            raise RuntimeError(f"braco {braco}: corpo, banheiro, metabolismo, gestos ou pesos_janela")
        if b.cfg_corpo_de(espec) is not None or b.cfg_banheiro_de(espec) is not None:
            raise RuntimeError(f"braco {braco}: a bancada monta o corpo ou o banheiro")
        cl = bv.cfg_lobos_do_braco(b.cfg_lobos, b.braco(espec), espec.semente, b.montagem)
        ligadas = [k for k in ("alvo_aprendido", "entradas_sociais", "modelo_outros", "presenca_fruta_mundo") if getattr(cl, k)]
        if ligadas:
            raise RuntimeError(f"braco {braco}: chaves ligadas no cerebro {ligadas}")
        out[braco] = {"alvo_aprendido": cl.alvo_aprendido, "entradas_sociais": cl.entradas_sociais, "modelo_outros": cl.modelo_outros,
                      "presenca_fruta_mundo": cl.presenca_fruta_mundo, "corpo": None, "banheiro": None}
    return out


# ================================================================== as vidas (um processo por unidade e ponto)
_BANCADAS: dict = {}


def _bancada(cfg: dict, m: float) -> bv.Bancada:
    chave = (json.dumps(cfg, sort_keys=True), m)
    if chave not in _BANCADAS:
        _BANCADAS[chave] = bv.bancada_da_config(config_bancada(cfg, m, ["P0", "P0z", "P1"], cfg["piloto"]["acoplados"]))
    return _BANCADAS[chave]


def _guardar(b: bv.Bancada, v: bv.VidaBancada, dir_vidas: Path) -> None:
    """Grava o log e o estado interno e confere o replay a partir do texto do disco (G1)."""
    caminho = dir_vidas / f"{v.nome}.jsonl"
    bv._gravar(caminho, v.motor.log.para_jsonl())
    bv._gravar(dir_vidas / f"{v.nome}.politica.json", bv._interno(v.motor))
    b.conferir_replay(v, caminho.read_text(encoding="utf-8"))


def compacta(medida: dict, unidade: dict, m: float, tempo: dict) -> dict:
    """O registro de uma vida que a analise le: as medidas do plano (secao 5 e A1.8) e o custo."""
    mf = medida["mundo_fisico"]
    return {"vida": medida["vida"], "braco": medida["braco"], "dono": medida["dono"], "lugar": medida["lugar"],
            "semente": medida["semente"], "genoma": medida["genoma"], "base": unidade["base"], "k": unidade["k"], "m": m,
            "origem": medida["origem"], "filtro": medida["filtro"], "d_fe": mf["d_fe"]["d_fe"], "d_fe_n": mf["d_fe"]["n"],
            "d_fe_vida": mf["d_fe_vida"]["d_fe"], "privacao_janela": mf["cuidado"]["privacao"],
            "saude_janela": mf["cuidado"]["saude_media"], "permanencia_media": mf["permanencia_media"],
            "permanencia_custo": mf["permanencia_custo"], "permanencia_taxa": mf["permanencia_taxa"],
            "taxa_no_abandono": mf["taxa_no_abandono"], "visitas": len(mf["visitas"]), "consumos": mf["consumos"],
            "quedas": mf["quedas"], "deixadas": mf["deixadas"], "horas_acordado": mf["horas_acordado"],
            "interacoes": medida["interacoes"], "retirados": medida["retirados"], "eventos_mundo": medida["eventos_mundo"],
            "acerto_total": medida["acerto_total"], "deriva_final": medida["deriva_final"], "tempo": tempo}


def _cronometrar(f, *a):
    c0, p0 = time.process_time(), time.perf_counter()
    r = f(*a)
    return r, time.process_time() - c0, time.perf_counter() - p0


def tarefa_grade(cfg: dict, m: float, unidade: dict, pasta: str) -> tuple[dict, dict]:
    """As 12 celulas de uma unidade num ponto m: o P0 e o P0z, gravados, rejogados do disco e medidos (o P0 primeiro: o piso do
    acerto da celula, como no `rodar` da bancada)."""
    b = _bancada(cfg, m)
    dir_vidas = Path(pasta) / "vidas"
    completas, compactas = {}, {}
    for dono in cfg["donos"]:
        for lugar in cfg["lugares"]:
            vidas = {}
            for braco in BRACOS_GRADE:
                espec = bv.EspecVida(dono, braco, unidade["semente"], unidade["genoma"], cfg["mundo"], lugar=lugar)
                c0, p0 = time.process_time(), time.perf_counter()
                v = b.vida(espec)
                _guardar(b, v, dir_vidas)
                vidas[braco] = (v, time.process_time() - c0, time.perf_counter() - p0)
            piso = None
            for braco in BRACOS_GRADE:
                v, cv, pv = vidas[braco]
                med, cm, pm = _cronometrar(b.medir, v, cfg["sonda"], piso)
                if braco == "P0":
                    piso = med["acerto_total"]
                med["unidade"] = {"base": unidade["base"], "k": unidade["k"]}
                completas[v.nome] = med
                compactas[v.nome] = compacta(med, unidade, m, {"vida_cpu": cv, "vida_parede": pv, "medir_cpu": cm, "medir_parede": pm})
    return completas, compactas


def tarefa_piloto(cfg: dict, m: float, unidade: dict, pasta: str, pasta_grade: str, pisos: dict) -> tuple[dict, dict]:
    """O piloto de uma unidade no m escolhido (A1.4): o P1 em malha fechada e os acoplados P0^ac e P1^ac ao P0z da mesma celula. O P0z
    e refeito so como origem: o log dele tem de ser o da grade, byte a byte (falha alto), e nao e gravado de novo."""
    b = _bancada(cfg, m)
    dir_vidas = Path(pasta) / "vidas"
    completas, compactas = {}, {}
    for dono in cfg["donos"]:
        for lugar in cfg["lugares"]:
            z = b.vida(bv.EspecVida(dono, "P0z", unidade["semente"], unidade["genoma"], cfg["mundo"], lugar=lugar))
            gravado = (Path(pasta_grade) / "vidas" / f"{z.nome}.jsonl").read_text(encoding="utf-8")
            if gravado != z.motor.log.para_jsonl():
                raise bv.ReplayDivergiu(f"{z.nome}: o P0z refeito no piloto nao e o da grade")
            feitas = []
            for braco in cfg["piloto"]["bracos"]:
                c0, p0 = time.process_time(), time.perf_counter()
                v = b.vida(bv.EspecVida(dono, braco, unidade["semente"], unidade["genoma"], cfg["mundo"], lugar=lugar))
                _guardar(b, v, dir_vidas)
                feitas.append((v, time.process_time() - c0, time.perf_counter() - p0))
            for a in cfg["piloto"]["acoplados"]:
                if a["origem"] != "P0z":
                    raise ValueError(f"acoplado do piloto fora do plano: {a}")
                c0, p0 = time.process_time(), time.perf_counter()
                v = b.acoplar(z, a["destino"], a["filtro"])
                _guardar(b, v, dir_vidas)
                feitas.append((v, time.process_time() - c0, time.perf_counter() - p0))
            piso = pisos[(unidade["semente"], dono, lugar)]
            for v, cv, pv in feitas:
                med, cm, pm = _cronometrar(b.medir, v, cfg["sonda"], piso)
                med["unidade"] = {"base": unidade["base"], "k": unidade["k"]}
                completas[v.nome] = med
                compactas[v.nome] = compacta(med, unidade, m, {"vida_cpu": cv, "vida_parede": pv, "medir_cpu": cm, "medir_parede": pm})
    return completas, compactas


def _executar(tarefas: list[tuple], processos: int) -> list:
    """Roda as tarefas (funcao, argumentos) em ordem; com mais de um processo, num pool (cada vida e independente e determinista)."""
    if processos <= 1:
        return [f(*a) for f, a in tarefas]
    with ProcessPoolExecutor(max_workers=processos) as pool:
        futuros = [pool.submit(f, *a) for f, a in tarefas]
        return [fu.result() for fu in futuros]


# ================================================================== a analise (funcoes puras)
def por_unidade(registros: list[dict], braco_a: str, braco_b: str, medida: str, celulas: list[tuple[str, str]]) -> dict:
    """{semente: a media, nas celulas, de (a - b)} na medida (secao 4: a estatistica por unidade). Falta de celula ou valor None falha
    alto: o pareamento e por unidade e celula."""
    idx = {}
    for r in registros:
        chave = (r["semente"], r["dono"], r["lugar"], r["braco"])
        if chave in idx:
            raise RuntimeError(f"vida repetida: {chave}")
        idx[chave] = r[medida]
    out = {}
    for s in sorted({r["semente"] for r in registros}):
        ds = []
        for dono, lugar in celulas:
            a, b = idx.get((s, dono, lugar, braco_a)), idx.get((s, dono, lugar, braco_b))
            if a is None or b is None:
                raise RuntimeError(f"unidade {s}, celula {dono}/{lugar}: falta {braco_a} ou {braco_b} em {medida}")
            ds.append(a - b)
        out[s] = sum(ds) / len(ds)
    return out


def contraste(difs: dict, boot: dict) -> dict:
    """O contraste pareado sobre as unidades (o bootstrap da secao 7: 10.000 reamostragens, semente 4242)."""
    return contraste_pareado({s: [d] for s, d in difs.items()}, boot["reamostragens"], boot["semente"])


def premissa(registros: list[dict], celulas: list, boot: dict) -> dict:
    """G-MUNDO na calibracao: P0z - P0 em D_FE, por unidade; passa com o limite inferior do IC95 acima de 0."""
    difs = por_unidade(registros, "P0z", "P0", "d_fe", celulas)
    r = contraste(difs, boot)
    passa = r["ic95"] is not None and r["ic95"]["ic_inferior"] > 0.0
    return {"contraste": "P0z - P0 em D_FE", "por_unidade": {str(k): v for k, v in difs.items()}, **r, "passa": passa}


def escolher_m(premissas: dict) -> float | None:
    """Secao 6: o MENOR m em que a premissa passa; None se nenhum passa."""
    passam = sorted(m for m, p in premissas.items() if p["passa"])
    return passam[0] if passam else None


def escolher_k(difs: list[float], delta: float, poder: dict, semente: int, n_bases: int) -> dict:
    """A1.4: o menor K de k_min a k_max por base com poder simulado >= alvo no G-MF1r (o bootstrap das diferencas P0 - P1, centradas e
    deslocadas para Delta_MF, `replicas` por K; o teste t unilateral a `alfa`, a conta do adendo 2 da V1). Sem chegar: K = k_max,
    com o poder declarado."""
    tabela = []
    for k in range(poder["k_min"], poder["k_max"] + 1):
        n = n_bases * k
        tabela.append({"k": k, "n": n, "poder": em.poder_simulado(difs, delta, n, poder["alfa"], poder["replicas"], semente)})
    chega = [t for t in tabela if t["poder"] is not None and t["poder"] >= poder["alvo"]]
    escolhido = chega[0] if chega else tabela[-1]
    return {"k": escolhido["k"], "n": escolhido["n"], "poder": escolhido["poder"], "chega_ao_alvo": bool(chega),
            "tabela": tabela, "alfa": poder["alfa"], "alvo": poder["alvo"], "replicas": poder["replicas"], "semente": semente}


def relato_poder(difs: list[float], delta: float | None, n: int, poder: dict, semente: int) -> dict:
    """O poder de um secundario no N escolhido (A1.4, so relato), nos alfas do relato; abaixo de 0,5, subpotenciado."""
    if delta is None or delta <= 0:
        return {"delta": delta, "poder": None, "motivo": "delta <= 0: sem alternativa para simular"}
    por_alfa = {str(a): em.poder_simulado(difs, delta, n, a, poder["replicas"], semente) for a in poder["alfas_relato"]}
    return {"delta": delta, "n": n, "poder": por_alfa,
            "subpotenciado": {a: (p is None or p < 0.5) for a, p in por_alfa.items()}}


def custo(registros: list[dict], k: int | None, n_bases: int, n_celulas: int, processos: int) -> dict:
    """O custo medido por vida e braco (CPU e parede; a vida com a gravacao e o replay do disco, e a medicao) e a estimativa da
    validacao no K escolhido: 60 vidas por unidade (A1.2) e mais 24 com o bloco do layout afastado (A1.8), este estimado pelo custo do
    P0 e do P1 no layout padrao."""
    por = {}
    for r in registros:
        c = por.setdefault(r["braco"], {"vidas": 0, "cpu_s": 0.0, "parede_s": 0.0})
        t = r["tempo"]
        c["vidas"] += 1
        c["cpu_s"] += t["vida_cpu"] + t["medir_cpu"]
        c["parede_s"] += t["vida_parede"] + t["medir_parede"]
    for c in por.values():
        c["cpu_s_por_vida"] = c["cpu_s"] / c["vidas"]
        c["parede_s_por_vida"] = c["parede_s"] / c["vidas"]
    out = {"por_braco": por, "cpu_s_total": sum(c["cpu_s"] for c in por.values()),
           "parede_s_total_somado": sum(c["parede_s"] for c in por.values())}
    if k is not None and all(b in por for b in BRACOS_VALIDACAO):
        n = n_bases * k
        base = sum(por[b]["cpu_s_por_vida"] for b in BRACOS_VALIDACAO) * n_celulas * n
        afastado = sum(por[b]["cpu_s_por_vida"] for b in BRACOS_AFASTADO) * n_celulas * n
        out["validacao_estimada"] = {"k": k, "n": n, "vidas": n * n_celulas * len(BRACOS_VALIDACAO),
                                     "vidas_com_afastado": n * n_celulas * (len(BRACOS_VALIDACAO) + len(BRACOS_AFASTADO)),
                                     "cpu_h": base / 3600, "cpu_h_com_afastado": (base + afastado) / 3600,
                                     "parede_h_em_processos": {"processos": processos, "sem_afastado": base / 3600 / processos,
                                                               "com_afastado": (base + afastado) / 3600 / processos}}
    return out


def descritivo_piloto(registros: list[dict], celulas: list, boot: dict) -> dict:
    """Os contrastes do piloto, SO como relato (secao 6: nao entram no resultado como evidencia sobre o P1)."""
    out = {}
    for nome, a, b, medida in (("P0 - P1 em D_FE (G-MF1r)", "P0", "P1", "d_fe"),
                               ("P0^ac - P1^ac em D_FE (G-MF2r)", ROT_P0AC, ROT_P1AC, "d_fe"),
                               ("P0 - P1 em privacao (G-MF3r)", "P0", "P1", "privacao_janela")):
        difs = por_unidade(registros, a, b, medida, celulas)
        r = contraste(difs, boot)
        media = sum(difs.values()) / len(difs)
        dp = (sum((d - media) ** 2 for d in difs.values()) / (len(difs) - 1)) ** 0.5 if len(difs) > 1 else None
        out[nome] = {"media": r["media"], "dp_unidades": dp, "ic95": r["ic95"], "n": r["n"]}
    return out


# ================================================================== a run
def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=RAIZ, capture_output=True, text=True, check=True).stdout.strip()


def _relativo(caminho: Path) -> str:
    c = caminho.resolve()
    return c.relative_to(RAIZ).as_posix() if c.is_relative_to(RAIZ) else c.as_posix()


def _sha_arquivo(caminho: Path) -> str:
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


def rodar(cfg: dict, pasta: Path, processos: int, caminho_config: Path | None = None) -> dict:
    modo = modo_da_config(cfg)
    if pasta.exists():
        raise FileExistsError(f"{pasta} ja existe: a run se recusa a gravar por cima (secao 12)")
    unidades = bv.unidades_derivadas(cfg["unidades"]["bases"], int(cfg["unidades"]["k"]), PREFIXO)
    celulas = [(d, lg) for d in cfg["donos"] for lg in cfg["lugares"]]
    desligadas = {}
    for m in cfg["grade_m"]:
        cb = config_bancada(cfg, m, ["P0", "P0z", "P1"], cfg["piloto"]["acoplados"])
        desligadas[rotulo_m(m)] = conferir_desligadas(bv.bancada_da_config(cb), cb, unidades[0])
    pasta.mkdir(parents=True)
    inicio = time.time()
    meta = {"modo": modo, "plano": PLANO, "plano_sha256": _sha_arquivo(RAIZ / PLANO), "config": cfg,
            "config_arquivo": None if caminho_config is None else _relativo(caminho_config),
            "config_sha256": None if caminho_config is None else _sha_arquivo(caminho_config),
            "orquestrador_sha256": _sha_arquivo(Path(__file__)), "git_head": _git("rev-parse", "HEAD"),
            "git_limpo": _git("status", "--porcelain") == "", "processos": processos, "unidades": unidades,
            "chaves_desligadas_conferidas": desligadas,
            "bancada": bv.meta(config_bancada(cfg, cfg["grade_m"][0], ["P0", "P0z", "P1"], cfg["piloto"]["acoplados"])),
            "inicio": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(inicio))}
    meta["sha256"] = {"mundo.py": meta["bancada"]["mundo_sha256"], "config.py": meta["bancada"]["config_sha256"],
                      "lobos.py": meta["bancada"]["lobos_sha256"], "engine.py": meta["bancada"]["engine_sha256"],
                      "plano": meta["plano_sha256"], "config": meta["config_sha256"]}
    bv._gravar(pasta / "meta.json", bv._dump(meta))

    # ---- a grade (secao 6)
    tarefas = [(tarefa_grade, (cfg, m, u, str(pasta / "grade" / f"m_{rotulo_m(m)}"))) for m in cfg["grade_m"] for u in unidades]
    t_grade = time.perf_counter()
    saidas = _executar(tarefas, processos)
    meta["grade_parede_s"] = time.perf_counter() - t_grade
    grade: dict = {rotulo_m(m): {} for m in cfg["grade_m"]}
    completas: dict = {rotulo_m(m): {} for m in cfg["grade_m"]}
    for (_, (_, m, _, _)), (comp, compa) in zip(tarefas, saidas):
        completas[rotulo_m(m)].update(comp)
        grade[rotulo_m(m)].update(compa)
    for m in cfg["grade_m"]:
        bv._gravar(pasta / "grade" / f"m_{rotulo_m(m)}" / "medidas.json", bv._dump(dict(sorted(completas[rotulo_m(m)].items()))))
    premissas = {m: premissa(list(grade[rotulo_m(m)].values()), celulas, cfg["bootstrap"]) for m in cfg["grade_m"]}
    m_escolhido = escolher_m(premissas)
    resultado = {"modo": modo, "plano": PLANO, "regra": "o menor m com o limite inferior do IC95 de (P0z - P0) em D_FE > 0 (secao 6)",
                 "premissa_por_m": {rotulo_m(m): p for m, p in premissas.items()},
                 "m_escolhido": m_escolhido, "fechou": m_escolhido is not None}
    medidas = {"grade": grade, "piloto": {}}
    if m_escolhido is None:
        resultado["leitura"] = ("nenhum m passa a premissa: explorar nao compensa nem para o instinto com os numeros da tarefa. Para "
                                "tudo, sem piloto (secao 6, PMF-5); o desenho do mundo volta para o Matheus.")
        resultado["custo"] = custo([r for g in grade.values() for r in g.values()], None, len(cfg["unidades"]["bases"]),
                                   len(celulas), processos)
        return _fechar(pasta, meta, medidas, resultado, inicio)

    # ---- o piloto do N (A1.4), so no m escolhido
    rm = rotulo_m(m_escolhido)
    pisos = {(r["semente"], r["dono"], r["lugar"]): r["acerto_total"] for r in grade[rm].values() if r["braco"] == "P0"}
    tarefas = [(tarefa_piloto, (cfg, m_escolhido, u, str(pasta / "piloto"), str(pasta / "grade" / f"m_{rm}"),
                                {k: v for k, v in pisos.items() if k[0] == u["semente"]})) for u in unidades]
    t_piloto = time.perf_counter()
    saidas = _executar(tarefas, processos)
    meta["piloto_parede_s"] = time.perf_counter() - t_piloto
    comp_piloto, piloto = {}, {}
    for comp, compa in saidas:
        comp_piloto.update(comp)
        piloto.update(compa)
    bv._gravar(pasta / "piloto" / "medidas.json", bv._dump(dict(sorted(comp_piloto.items()))))
    medidas["piloto"] = piloto

    # ---- o Delta, o N, o poder e o custo
    regs = list(grade[rm].values()) + list(piloto.values())
    delta_mf = 0.5 * premissas[m_escolhido]["media"]
    difs_g1 = list(por_unidade(regs, "P0", "P1", "d_fe", celulas).values())
    n_bases = len(cfg["unidades"]["bases"])
    semente_poder = cfg["bootstrap"]["semente"]
    n = escolher_k(difs_g1, delta_mf, cfg["poder"], semente_poder, n_bases)
    prem_priv = por_unidade(list(grade[rm].values()), "P0z", "P0", "privacao_janela", celulas)
    delta_priv = 0.5 * sum(prem_priv.values()) / len(prem_priv)
    resultado.update({
        "delta_mf": delta_mf, "delta_mf_regra": "1/2 x a media de (P0z - P0) em D_FE no m escolhido (secao 6, A1.4)",
        "n": n,
        "poder_relato": {
            "G-MF2r": {"contraste": "P0^ac - P1^ac em D_FE", **relato_poder(
                list(por_unidade(regs, ROT_P0AC, ROT_P1AC, "d_fe", celulas).values()), delta_mf, n["n"], cfg["poder"], semente_poder)},
            "G-MF3r": {"contraste": "P0 - P1 em privacao", "delta_origem": "1/2 x a media de (P0z - P0) em privacao no m escolhido "
                       "(o plano nao da o Delta nessa escala; leitura registrada, so relato)", **relato_poder(
                list(por_unidade(regs, "P0", "P1", "privacao_janela", celulas).values()), delta_priv, n["n"], cfg["poder"],
                semente_poder)},
            "G-PERM, G-OPORT, G-DIST": "nao calculado: o plano nao da o Delta das inclinacoes, e o layout afastado nao roda no piloto"},
        "piloto_descritivo": descritivo_piloto(regs, celulas, cfg["bootstrap"]),
        "custo": custo(regs, n["k"], n_bases, len(celulas), processos)})
    return _fechar(pasta, meta, medidas, resultado, inicio)


def _fechar(pasta: Path, meta: dict, medidas: dict, resultado: dict, inicio: float) -> dict:
    meta["fim"] = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
    meta["duracao_s"] = time.time() - inicio
    meta["python"] = platform.python_version()
    bv._gravar(pasta / "medidas.json", bv._dump(medidas))
    bv._gravar(pasta / "resultado.json", bv._dump(resultado))
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    return {"meta": meta, "medidas": medidas, "resultado": resultado}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--config", required=True)
    ap.add_argument("--saida", default=None)
    ap.add_argument("--processos", type=int, default=1)
    a = ap.parse_args()
    caminho = Path(a.config)
    cfg = json.loads(caminho.read_text(encoding="utf-8"))
    modo = modo_da_config(cfg)
    saida = Path(a.saida) if a.saida else RAIZ / SAIDA_PADRAO
    if modo == "fumaca" and a.saida is None:
        raise SystemExit("a fumaca precisa de --saida (fora de artifacts_v2_mundo/calibracao)")
    r = rodar(cfg, saida, a.processos, caminho)["resultado"]
    print(json.dumps({"m_escolhido": r["m_escolhido"], "fechou": r["fechou"],
                      "premissa": {m: {"media": p["media"], "ic95": p["ic95"], "passa": p["passa"]}
                                   for m, p in r["premissa_por_m"].items()},
                      "delta_mf": r.get("delta_mf"), "n": {k: r["n"][k] for k in ("k", "n", "poder", "chega_ao_alvo")} if "n" in r
                      else None}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
