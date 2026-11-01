"""V2, MUNDO-VALIDACAO: a validacao do mundo fisico, uma vez (docs/PLANO_ANALISE_V2_MUNDO_FISICO.md, secoes 7 e 8; adendo 1: A1.2, A1.3,
A1.5, A1.8 e os numeros congelados na A1.9; autorizada pelo Matheus em 2026-10-12). Pela bancada (experiments/bancada_v2.py), no mundo da
calibracao (`fisico`, `mult_queda` = 1, o motor de sempre: o desempate do cheiro do #232 nao entra), nas unidades derivadas das bases
32101...32505 (K = 8, prefixo "mundo", N = 40) ou, na fumaca, nas sementes dos testes. As da calibracao (31101...31505) nunca.

Por unidade, as 12 celulas (4 donos x 3 lugares) com:
    P0, P0z, P1                      malha fechada (o dono so cuida, PMF-3)
    P0^ac, P1^ac                     acoplados ao P0z da mesma celula, filtro nenhum (A1.2)
    P0 e P1 no layout afastado       o bloco do G-DIST (A1.8)
= 84 vidas por unidade. Os gates (por unidade, a media das 12 celulas; o bootstrap de 10.000 com a semente 4242):
    G-MUNDO   P0z - P0 em D_FE, limite inferior do IC95 > 0 (a premissa; falhando, o P1 nao e lido)
    G-MF1r    P0 - P1 em D_FE, as categorias da secao 8 com Delta_MF (ganha, "abaixo de Delta", perde, equivalente, inconclusivo)
    Holm (alfa 0,05) sobre G-MF2r (P0^ac - P1^ac em D_FE), G-MF3r (P0 - P1 em privacao), G-PERM, G-OPORT e G-DIST (A1.3, A1.8)
O G-MF3r e lido como subpotenciado (A1.9), e o G-PERM, o G-OPORT e o G-DIST sem Delta nem poder (A1.9), declarados. A leitura da A1.5.

Toda vida e gravada e rejogada do disco bit a bit (Bancada.conferir_replay); o replay da medicao tambem confere. A run se recusa a rodar
se a pasta de saida existe.

    python experiments/run_v2_validacao_mundo.py --config experiments/configs/v2_mundo/validacao.json --processos 8
"""
from __future__ import annotations

import argparse
import json
import platform
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v2_calibracao_mundo as rc  # noqa: E402
from digilab.metrics import contraste_distancia, holm, inclinacao_permanencia, permanencia_media  # noqa: E402

PLANO = rc.PLANO
SAIDA_PADRAO = "artifacts_v2_mundo/validacao"
CALIBRACAO = "artifacts_v2_mundo/calibracao/resultado.json"   # A1.9: o m, o Delta_MF e o K congelados
BASES_VALIDACAO = rc.BASES_VALIDACAO
K_VALIDACAO = 8
MUNDO, MUNDO_AFASTADO = "fisico", "fisico_afastado"
SUFIXO_AFASTADO = "@afastado"
ROT_P0AC, ROT_P1AC = rc.ROT_P0AC, rc.ROT_P1AC
BRACOS_FECHADOS = ("P0", "P0z", "P1")
CHAVES_CONFIG = {"descricao", "plano", "donos", "unidades", "mundo", "mundo_afastado", "lugares", "dias", "orcamento", "ponto", "montagem",
                 "lobos", "consequencia", "sonda", "bootstrap", "m", "delta_mf", "acoplados", "bracos_afastado", "holm",
                 "chaves_desligadas"}
HOLM = ("G-MF2r", "G-MF3r", "G-PERM", "G-OPORT", "G-DIST")


# ================================================================== a config
def modo_da_config(cfg: dict) -> str:
    """'fumaca' (as sementes dos testes) ou 'validacao' (as bases 32101...32505, K = 8, o plano e os numeros da A1.9). O resto falha alto:
    as bases da calibracao ja foram usadas, e qualquer outra faixa nao e deste plano."""
    faltam = CHAVES_CONFIG - {"descricao", "plano"} - set(cfg)
    sobram = set(cfg) - CHAVES_CONFIG
    if faltam or sobram:
        raise ValueError(f"config: faltam {sorted(faltam)}, sobram {sorted(sobram)}")
    u = cfg["unidades"]
    bases = tuple(u["bases"])
    erros = []
    if u.get("prefixo") != rc.PREFIXO or cfg["mundo"] != MUNDO or cfg["mundo_afastado"] != MUNDO_AFASTADO:
        erros.append("prefixo ou mundos")
    if cfg["acoplados"] != rc.PILOTO_PLANO["acoplados"] or cfg["bracos_afastado"] != ["P0", "P1"]:
        erros.append("acoplados (A1.2) ou bloco afastado (A1.8)")
    if cfg["holm"] != {"alfa": 0.05}:
        erros.append("holm (alfa 0,05)")
    if set(cfg["chaves_desligadas"]) != set(rc.CHAVES_DESLIGADAS):
        erros.append("chaves_desligadas")
    if set(cfg["donos"]) - set(rc.DONOS_V1) or set(cfg["lugares"]) - set(rc.LUGARES) or not cfg["donos"] or not cfg["lugares"]:
        erros.append("donos ou lugares")
    if erros:
        raise ValueError(f"config fora do plano: {erros}")
    if set(bases) & set(range(rc.BASES_CALIBRACAO[0], rc.BASES_CALIBRACAO[-1] + 1)):
        raise bv.SementeSemPlano("as bases da calibracao (31101...31505) ja foram usadas: a validacao e em 32101...32505")
    if set(bases) <= bv.SEMENTES_TESTE:
        return "fumaca"
    if bases != BASES_VALIDACAO:
        raise bv.SementeSemPlano(f"bases {list(bases)}: so as dos testes (fumaca) ou {list(BASES_VALIDACAO)} (validacao, secao 11)")
    cal = json.loads((RAIZ / CALIBRACAO).read_text(encoding="utf-8"))
    if cfg.get("plano") != PLANO:
        erros.append(f"plano {cfg.get('plano')!r}")
    if u["k"] != K_VALIDACAO or cal["n"]["k"] != K_VALIDACAO:
        erros.append(f"K {u['k']} (A1.9: {cal['n']['k']})")
    if cfg["m"] != cal["m_escolhido"] or cfg["delta_mf"] != cal["delta_mf"]:
        erros.append("m ou Delta_MF diferentes dos da calibracao (A1.9)")
    if tuple(sorted(cfg["donos"])) != tuple(sorted(rc.DONOS_V1)) or tuple(cfg["lugares"]) != rc.LUGARES:
        erros.append("donos ou lugares")
    if cfg["dias"] != rc.DIAS_PLANO or cfg["orcamento"] != rc.ORCAMENTO_PLANO:
        erros.append("dias ou orcamento")
    if cfg["bootstrap"] != {"reamostragens": 10000, "semente": 4242, "nivel": 0.95}:
        erros.append("bootstrap (secao 7)")
    calcfg = json.loads((RAIZ / "experiments/configs/v2_mundo/calibracao.json").read_text(encoding="utf-8"))
    for k in ("ponto", "montagem", "lobos", "consequencia", "sonda"):
        if cfg[k] != calcfg[k]:
            erros.append(f"{k} diferente da calibracao")
    if erros:
        raise ValueError(f"a validacao segue o plano e a A1.9 a letra: {erros}")
    return "validacao"


def config_bancada(cfg: dict) -> dict:
    """A config da bancada: os dois layouts, o m da A1.9, os acoplados ao P0z."""
    out = {"bracos": list(BRACOS_FECHADOS), "donos": list(cfg["donos"]), "unidades": dict(cfg["unidades"]),
           "mundos": [cfg["mundo"], cfg["mundo_afastado"]], "lugares": list(cfg["lugares"]), "dias": cfg["dias"],
           "orcamento": cfg["orcamento"], "ponto": cfg["ponto"], "montagem": cfg["montagem"], "lobos": dict(cfg["lobos"]),
           "consequencia": dict(cfg["consequencia"]), "sonda": dict(cfg["sonda"]), "bootstrap": dict(cfg["bootstrap"]),
           "mundo": {"mult_queda": cfg["m"]}, "acoplados": [dict(a) for a in cfg["acoplados"]]}
    if cfg.get("plano"):
        out["plano"] = cfg["plano"]
    return bv.validar_config(out)


# ================================================================== as vidas (um processo por unidade)
_BANCADAS: dict = {}


def _bancada(cfg: dict) -> bv.Bancada:
    chave = json.dumps(cfg, sort_keys=True)
    if chave not in _BANCADAS:
        _BANCADAS[chave] = bv.bancada_da_config(config_bancada(cfg))
    return _BANCADAS[chave]


def compacta(medida: dict, unidade: dict, m: float, tempo: dict, rotulo: str) -> dict:
    """O registro de uma vida: o da calibracao, mais o layout, o rotulo do braco na analise e as visitas (para juntar por unidade)."""
    r = rc.compacta(medida, unidade, m, tempo)
    mf = medida["mundo_fisico"]
    r.update({"braco": rotulo, "braco_bancada": medida["braco"], "mundo": medida["mundo"],
              "visitas_lista": [{k: v[k] for k in ("arvore", "inicio", "fim", "permanencia", "censurada", "custo_viagem", "taxa_recente")}
                                for v in mf["visitas"]],
              "razoes_abandono": mf["taxa_no_abandono"]["razoes"]})
    return r


def tarefa_unidade(cfg: dict, unidade: dict, pasta: str) -> tuple[dict, dict]:
    """As 84 vidas de uma unidade: gravadas, rejogadas do disco e medidas (em cada layout o P0 primeiro: o piso do acerto da celula)."""
    b = _bancada(cfg)
    dir_vidas = Path(pasta) / "vidas"
    completas, compactas = {}, {}
    for dono in cfg["donos"]:
        for lugar in cfg["lugares"]:
            feitas = []          # (vida, cpu, parede, rotulo, layout)

            def vida(braco, mundo, rotulo):
                c0, p0 = time.process_time(), time.perf_counter()
                v = b.vida(bv.EspecVida(dono, braco, unidade["semente"], unidade["genoma"], mundo, lugar=lugar))
                rc._guardar(b, v, dir_vidas)
                feitas.append((v, time.process_time() - c0, time.perf_counter() - p0, rotulo, mundo))
                return v

            for braco in BRACOS_FECHADOS:
                v = vida(braco, cfg["mundo"], braco)
                if braco == "P0z":
                    z = v
            for a in cfg["acoplados"]:
                c0, p0 = time.process_time(), time.perf_counter()
                v = b.acoplar(z, a["destino"], a["filtro"])
                rc._guardar(b, v, dir_vidas)
                feitas.append((v, time.process_time() - c0, time.perf_counter() - p0, v.rotulo_braco, cfg["mundo"]))
            for braco in cfg["bracos_afastado"]:
                vida(braco, cfg["mundo_afastado"], braco + SUFIXO_AFASTADO)
            pisos = {}
            for v, cv, pv, rotulo, mundo in sorted(feitas, key=lambda f: f[3] not in ("P0", "P0" + SUFIXO_AFASTADO)):
                med, cm, pm = rc._cronometrar(b.medir, v, cfg["sonda"], pisos.get(mundo))
                if rotulo in ("P0", "P0" + SUFIXO_AFASTADO):
                    pisos[mundo] = med["acerto_total"]
                med["unidade"] = {"base": unidade["base"], "k": unidade["k"]}
                completas[v.nome] = med
                compactas[v.nome] = compacta(med, unidade, cfg["m"],
                                             {"vida_cpu": cv, "vida_parede": pv, "medir_cpu": cm, "medir_parede": pm}, rotulo)
    return completas, compactas


# ================================================================== a analise (funcoes puras)
def categoria_g_mf1(r: dict, delta: float) -> dict:
    """As categorias do G-MF1r (secao 8), exclusivas e nesta ordem: ganha (limite inferior do IC95 > 0; "ganha, abaixo de Delta" se o
    superior do IC90 < Delta), perde (superior do IC95 < 0), equivalente (o IC90 inteiro em (-Delta, +Delta)), inconclusivo."""
    ic95, ic90 = r["ic95"], r["ic90"]
    if ic95 is None or ic90 is None:
        return {"categoria": "inconclusivo", "motivo": "sem IC"}
    if ic95["ic_inferior"] > 0.0:
        return {"categoria": "ganha, abaixo de Delta" if ic90["ic_superior"] < delta else "ganha"}
    if ic95["ic_superior"] < 0.0:
        return {"categoria": "perde"}
    if -delta < ic90["ic_inferior"] and ic90["ic_superior"] < delta:
        return {"categoria": "equivalente"}
    return {"categoria": "inconclusivo"}


def _por_unidade_braco(registros: list[dict], rotulo: str) -> dict:
    out: dict = {}
    for r in registros:
        if r["braco"] == rotulo:
            out.setdefault(r["semente"], []).append(r)
    return out


def inclinacoes_por_unidade(registros: list[dict], rotulo: str, sobre: str) -> dict:
    """A inclinacao da permanencia sobre `sobre`, por unidade, com as visitas das 12 celulas do braco juntas (A1.8;
    metrics.inclinacao_permanencia)."""
    return {s: inclinacao_permanencia([v for r in rs for v in r["visitas_lista"]], sobre)
            for s, rs in sorted(_por_unidade_braco(registros, rotulo).items())}


def diferenca_inclinacoes(registros: list[dict], sobre: str, sinal: int, boot: dict) -> dict:
    """P1 - P0 nas inclinacoes, por unidade; o contraste e orientado (`sinal` x (P1 - P0), positivo = a direcao predita). As unidades
    sem inclinacao num dos bracos ficam fora, contadas."""
    p1, p0 = inclinacoes_por_unidade(registros, "P1", sobre), inclinacoes_por_unidade(registros, "P0", sobre)
    difs, sem = {}, []
    for s in sorted(set(p1) | set(p0)):
        a, b = p1.get(s, {}).get("inclinacao"), p0.get(s, {}).get("inclinacao")
        if a is None or b is None:
            sem.append(s)
            continue
        difs[s] = a - b
    r = rc.contraste({s: sinal * d for s, d in difs.items()}, boot)
    media = sum(difs.values()) / len(difs) if difs else None
    return {"p1_menos_p0": {"media": media, "ic95": _desorientar(r["ic95"], sinal), "ic90": _desorientar(r["ic90"], sinal)},
            "orientado": r, "sem_valor": len(sem), "n": len(difs),
            "inclinacao_media": {"P1": _media([x["inclinacao"] for x in p1.values()]),
                                 "P0": _media([x["inclinacao"] for x in p0.values()])}}


def _media(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def _desorientar(ic: dict | None, sinal: int) -> dict | None:
    if ic is None or sinal == 1:
        return ic
    return {"ic_inferior": -ic["ic_superior"], "ic_superior": -ic["ic_inferior"], "nivel": ic["nivel"]}


def g_dist(registros: list[dict], boot: dict) -> dict:
    """G-DIST (A1.8), por unidade: [P1(afastado) - P1(padrao)] - [P0(afastado) - P0(padrao)] na permanencia media das visitas das 12
    celulas juntas (metrics.contraste_distancia). As unidades sem valor ficam fora, contadas."""
    perm = {}
    for rotulo in ("P0", "P1", "P0" + SUFIXO_AFASTADO, "P1" + SUFIXO_AFASTADO):
        perm[rotulo] = {s: permanencia_media([v for r in rs for v in r["visitas_lista"]])
                        for s, rs in _por_unidade_braco(registros, rotulo).items()}
    difs, sem = {}, 0
    for s in sorted(perm["P0"]):
        d = contraste_distancia(perm["P1" + SUFIXO_AFASTADO].get(s), perm["P1"].get(s), perm["P0" + SUFIXO_AFASTADO].get(s),
                                perm["P0"].get(s))
        if d is None:
            sem += 1
        else:
            difs[s] = d
    return {**rc.contraste(difs, boot), "sem_valor": sem,
            "permanencia_media": {k: _media(list(v.values())) for k, v in perm.items()}}


def razao_abandono(registros: list[dict], boot: dict) -> dict:
    """Medida 2 (A1.8, so descritiva): por unidade e braco, a media das razoes (a taxa nos 30 min antes de sair / a media da vida) das
    12 celulas juntas; P1 - P0 com IC."""
    por = {}
    for rotulo in ("P0", "P1"):
        por[rotulo] = {s: _media([x for r in rs for x in r["razoes_abandono"]]) for s, rs in _por_unidade_braco(registros, rotulo).items()}
    difs = {s: por["P1"][s] - por["P0"][s] for s in por["P0"] if por["P0"][s] is not None and por["P1"].get(s) is not None}
    return {"P0": _media(list(por["P0"].values())), "P1": _media(list(por["P1"].values())), "p1_menos_p0": rc.contraste(difs, boot),
            "sem_valor": len(por["P0"]) - len(difs)}


def descritivos(registros: list[dict], celulas: list, boot: dict) -> dict:
    """Os descritivos da secao 5.3 que saem do registro (sem gate): os niveis por braco; P0 - P1 e P0z - P0 por lugar e por dono; o
    lugar como cuidado no P0 (longe - comedouro, perto - comedouro)."""
    niveis = {}
    for rotulo in sorted({r["braco"] for r in registros}):
        rs = [r for r in registros if r["braco"] == rotulo]
        niveis[rotulo] = {k: _media([r[k] for r in rs]) for k in ("d_fe", "d_fe_vida", "privacao_janela", "consumos", "visitas",
                                                                  "horas_acordado", "permanencia_media")}
        niveis[rotulo]["vidas"] = len(rs)
    sub = {}
    for nome, a, b in (("P0 - P1", "P0", "P1"), ("P0z - P0", "P0z", "P0"), ("P0^ac - P1^ac", ROT_P0AC, ROT_P1AC)):
        for chave, valores in (("lugar", sorted({c[1] for c in celulas})), ("dono", sorted({c[0] for c in celulas}))):
            for x in valores:
                cel = [c for c in celulas if c[1 if chave == "lugar" else 0] == x]
                r = rc.contraste(rc.por_unidade(registros, a, b, "d_fe", cel), boot)
                sub.setdefault(nome, {}).setdefault(chave, {})[x] = {"media": r["media"], "ic95": r["ic95"]}
    lugar = {}
    p0 = {(r["semente"], r["dono"], r["lugar"]): r["d_fe"] for r in registros if r["braco"] == "P0"}
    for x in ("perto", "longe"):
        if not any(k[2] == x for k in p0) or not any(k[2] == "comedouro" for k in p0):
            continue
        difs = {}
        for s in sorted({k[0] for k in p0}):
            ds = [p0[(s, d, x)] - p0[(s, d, "comedouro")] for d in sorted({k[1] for k in p0})
                  if (s, d, x) in p0 and (s, d, "comedouro") in p0]
            difs[s] = sum(ds) / len(ds)
        r = rc.contraste(difs, boot)
        lugar[f"{x} - comedouro"] = {"media": r["media"], "ic95": r["ic95"]}
    return {"niveis": niveis, "por_lugar_e_dono": sub, "lugar_como_cuidado_P0": lugar}


def leitura_a15(g_mundo: dict, g_mf1: dict, mf2_passa: bool) -> str:
    """A regra de decisao da A1.5 (e a da secao 8 com o G-MUNDO falhando)."""
    if not g_mundo["passa"]:
        return ("G-MUNDO falha na validacao: a premissa nao se repetiu fora da calibracao, e o P1 nao e lido. O mundo volta para revisao "
                "(secao 8).")
    c = g_mf1["categoria"]
    if c.startswith("ganha"):
        if mf2_passa:
            return "o P1 ganha, e o ganho e do pet: aparece tambem com o cuidado fixo (A1.5, primeira linha)."
        return ("o P1 ganha, mas o ganho pode vir do dono reagindo ao que o P1 faz: o G-MF2r nao passa (A1.5, segunda linha; registrado ao "
                "lado, sem trocar a categoria).")
    return (f"G-MF1r {c}: a consequencia imediata nao aprende a procurar neste mundo (A1.5, terceira linha; secao 8). Resultado "
            "negativo, registrado.")


def analisar(registros: list[dict], cfg: dict) -> dict:
    celulas = [(d, lg) for d in cfg["donos"] for lg in cfg["lugares"]]
    boot, delta = cfg["bootstrap"], cfg["delta_mf"]
    fech = [r for r in registros if r["mundo"] == cfg["mundo"]]
    gm = rc.contraste(rc.por_unidade(fech, "P0z", "P0", "d_fe", celulas), boot)
    g_mundo = {"contraste": "P0z - P0 em D_FE", **gm, "passa": gm["ic95"] is not None and gm["ic95"]["ic_inferior"] > 0.0}
    g1 = rc.contraste(rc.por_unidade(fech, "P0", "P1", "d_fe", celulas), boot)
    g_mf1 = {"contraste": "P0 - P1 em D_FE", "delta_mf": delta, **g1, **categoria_g_mf1(g1, delta)}
    sec = {
        "G-MF2r": {"contraste": "P0^ac - P1^ac em D_FE", "regra": "limite inferior do IC95 > 0",
                   **rc.contraste(rc.por_unidade(fech, ROT_P0AC, ROT_P1AC, "d_fe", celulas), boot)},
        "G-MF3r": {"contraste": "P0 - P1 em privacao", "regra": "limite inferior do IC95 > 0",
                   "declarado": "subpotenciado (A1.9: poder 0,03 a 0,11 no N = 40)",
                   **rc.contraste(rc.por_unidade(fech, "P0", "P1", "privacao_janela", celulas), boot)},
        "G-PERM": {"contraste": "inclinacao da permanencia sobre o custo de viagem, P1 - P0", "regra": "limite inferior do IC95 > 0",
                   "declarado": "sem Delta nem poder (A1.9)", **diferenca_inclinacoes(fech, "custo_viagem", 1, boot)},
        "G-OPORT": {"contraste": "inclinacao da permanencia sobre a taxa recente, P1 - P0", "regra": "limite superior do IC95 < 0",
                    "declarado": "sem Delta nem poder (A1.9)", **diferenca_inclinacoes(fech, "taxa_recente", -1, boot)},
        "G-DIST": {"contraste": "[P1(afastado) - P1(padrao)] - [P0(afastado) - P0(padrao)] na permanencia media",
                   "regra": "limite inferior do IC95 > 0", "declarado": "sem Delta nem poder (A1.9)", **g_dist(registros, boot)},
    }

    def p_de(nome):
        g = sec[nome]
        return (g["orientado"] if "orientado" in g else g)["p_unilateral"]

    h = holm({n: p_de(n) for n in HOLM}, cfg["holm"]["alfa"])
    for n in HOLM:
        g = sec[n]
        ic = (g["orientado"] if "orientado" in g else g)["ic95"]
        g["passa_ic"] = ic is not None and ic["ic_inferior"] > 0.0           # orientado: a regra de cada gate vira "inferior > 0"
        g["holm"] = h[n]
        g["passa"] = g["passa_ic"] and h[n]["rejeita"]
    return {"G-MUNDO": g_mundo, "G-MF1r": g_mf1, "secundarios": sec, "holm_alfa": cfg["holm"]["alfa"],
            "leitura": leitura_a15(g_mundo, g_mf1, sec["G-MF2r"]["passa"]),
            "p1_lido": g_mundo["passa"],
            "medida_2_razao_abandono": razao_abandono(fech, boot),
            "descritivos": descritivos(fech, celulas, boot),
            "nao_medidos": ["ganho liquido por hora de busca", "latencia ate achar", "frutas das arvores comidas", "deslocamento por regiao",
                            "tempo livre por acao", "fome urgente", "o teto do P1", "tempo de desistencia (secao 9)"]}


# ================================================================== a run
def rodar(cfg: dict, pasta: Path, processos: int, caminho_config: Path | None = None) -> dict:
    modo = modo_da_config(cfg)
    if pasta.exists():
        raise FileExistsError(f"{pasta} ja existe: a validacao roda uma vez e se recusa a gravar por cima (secao 12)")
    unidades = bv.unidades_derivadas(cfg["unidades"]["bases"], int(cfg["unidades"]["k"]), rc.PREFIXO)
    cb = config_bancada(cfg)
    b = bv.bancada_da_config(cb)
    if b.cfg_mundo.mult_queda != cfg["m"]:
        raise RuntimeError("o m da bancada nao e o da config")
    desligadas = rc.conferir_desligadas(b, cb, unidades[0])
    pasta.mkdir(parents=True)
    inicio = time.time()
    meta = {"modo": modo, "plano": PLANO, "plano_sha256": rc._sha_arquivo(RAIZ / PLANO), "config": cfg,
            "config_arquivo": None if caminho_config is None else rc._relativo(caminho_config),
            "config_sha256": None if caminho_config is None else rc._sha_arquivo(caminho_config),
            "calibracao_sha256": rc._sha_arquivo(RAIZ / CALIBRACAO),
            "orquestrador_sha256": rc._sha_arquivo(Path(__file__)), "git_head": rc._git("rev-parse", "HEAD"),
            "git_limpo": rc._git("status", "--porcelain") == "", "processos": processos, "unidades": unidades,
            "chaves_desligadas_conferidas": desligadas, "bancada": bv.meta(cb),
            "inicio": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(inicio))}
    meta["sha256"] = {"mundo.py": meta["bancada"]["mundo_sha256"], "config.py": meta["bancada"]["config_sha256"],
                      "lobos.py": meta["bancada"]["lobos_sha256"], "engine.py": meta["bancada"]["engine_sha256"],
                      "plano": meta["plano_sha256"], "config": meta["config_sha256"]}
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    t0 = time.perf_counter()
    saidas = rc._executar([(tarefa_unidade, (cfg, u, str(pasta))) for u in unidades], processos)
    meta["vidas_parede_s"] = time.perf_counter() - t0
    completas, regs = {}, {}
    for comp, compa in saidas:
        completas.update(comp)
        regs.update(compa)
    bv._gravar(pasta / "medidas_completas.json", bv._dump(dict(sorted(completas.items()))))
    resultado = {"modo": modo, "plano": PLANO, **analisar(list(regs.values()), cfg),
                 "custo": rc.custo(list(regs.values()), None, len(cfg["unidades"]["bases"]), 12, processos)}
    meta["fim"] = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
    meta["duracao_s"] = time.time() - inicio
    meta["python"] = platform.python_version()
    bv._gravar(pasta / "medidas.json", bv._dump(dict(sorted(regs.items()))))
    bv._gravar(pasta / "resultado.json", bv._dump(resultado))
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    return {"meta": meta, "medidas": regs, "resultado": resultado}


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
        raise SystemExit("a fumaca precisa de --saida (fora de artifacts_v2_mundo/validacao)")
    saida = Path(a.saida) if a.saida else RAIZ / SAIDA_PADRAO
    r = rodar(cfg, saida, a.processos, caminho)["resultado"]
    print(json.dumps({"G-MUNDO": {k: r["G-MUNDO"][k] for k in ("media", "ic95", "passa")},
                      "G-MF1r": {k: r["G-MF1r"][k] for k in ("media", "ic95", "ic90", "categoria")},
                      "secundarios": {n: {"passa": g["passa"], "p": g["holm"]["p"]} for n, g in r["secundarios"].items()},
                      "leitura": r["leitura"]}, indent=2))


if __name__ == "__main__":
    main()
