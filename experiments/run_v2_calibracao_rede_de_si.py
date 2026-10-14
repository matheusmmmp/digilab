"""V2, REDE-DE-SI-CALIBRACAO: a calibracao do `passo` da rede de si e o piloto (docs/PLANO_ANALISE_V2_REDE_DE_SI.md, secoes 5, 6, 8 e 11;
PRS-1 a PRS-5 decididas). Pela bancada (experiments/bancada_v2.py, a chave `rede_de_si`), nas unidades derivadas das bases 43101...43505
(K_u = 4, prefixo "rede_de_si") ou, na fumaca, nas sementes dos testes. As da validacao (44101...44505) nunca: o modo vem das sementes e
recusa o resto. NAO rodada: precisa do sim do Matheus.

As etapas, numa run so:
    grade   o P1-c no mundo da bola, com o atencioso e os gestos, 14 dias, o `passo` da rede em {S/64, S/16, S/4} (secao 5). A rede so
            observa: as tres vidas de uma unidade sao a mesma vida byte a byte (G-OBS, conferido), e so a rede muda
    regra   o `passo` com o menor MAE_rede(1) nos dias 1 a 7; sai da grade o que prende pesos no teto em mais da metade das vidas; sem
            nenhum, o menor. A regra nao le a persistencia, a media historica nem contraste nenhum
    lenta   a taxa lenta da digestao (o P1-c-lenta) espera a troca no motor (a etapa 2b, do A): fica atras do no, declarada
    piloto  no `passo` escolhido, os bracos do plano que rodam: P1-c, P0-c e P1-c-tapa (bola) e P1+ped-c (iguais_frutas), as mesmas 20
            unidades. Serve so para a margem, o N e o custo (secao 6)
    N       Delta_SI = 1/2 x [MAE_pers(4) - MAE_oraculo(4)] no P1-c; se a distancia for <= S/128, a validacao nao roda e o plano volta
            ao Matheus. O menor K_u de 4 a 10 com poder simulado >= 0,8 para Delta_SI no primario (2.000 replicas por K_u); o poder dos
            secundarios no N escolhido, so relato (abaixo de 0,5, subpotenciado)

Toda vida e gravada e rejogada do disco bit a bit (Bancada.conferir_replay, com o G1-REDE); o replay de medicao tambem confere. A run se
recusa a rodar se a pasta de saida existe.

    python experiments/run_v2_calibracao_rede_de_si.py --config experiments/configs/v2_rede_de_si/calibracao.json --processos 6
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
import run_v2_calibracao_mundo as cm  # noqa: E402
from digilab.metrics import mae_previsao  # noqa: E402

PLANO = "docs/PLANO_ANALISE_V2_REDE_DE_SI.md"
SAIDA_PADRAO = "artifacts_v2_rede_de_si/calibracao"
PREFIXO = "rede_de_si"
BASES_CALIBRACAO = (43101, 43202, 43303, 43404, 43505)    # secao 8 (RS-6)
BASES_VALIDACAO = (44101, 44202, 44303, 44404, 44505)     # secao 8: precisa de outro sim; aqui, recusada
K_CALIBRACAO = 4
DIAS_PLANO = 14
ORCAMENTO_PLANO = 224
DONO = "atencioso"                                        # PRS-5
S = 1024
GRADE_PASSO = (S // 64, S // 16, S // 4)                  # secao 5
DIAS_REGRA = (1, 7)                                       # secao 5: o MAE_rede(1) nos dias 1 a 7
HORIZONTE_REGRA = 1
BRACO_GRADE = ("P1-c", "bola")                            # secao 5: o P1-c (o primario, PRS-2)
BRACOS_PILOTO = (("P1-c", "bola"), ("P0-c", "bola"), ("P1-c-tapa", "bola"), ("P1+ped-c", "iguais_frutas"))   # secao 3, sem a lenta
BRACO_LENTA = ("P1-c-lenta", "bola")                      # secao 3: espera a troca da digestao (a etapa 2b, do A)
GRADE_TAXA_LENTA = ("C//2", "C//4", "C//8")               # secao 5: a regra da taxa lenta, atras do no
LIMIAR_DISTANCIA = S // 128                               # secao 6: a distancia persistencia - oraculo <= S/128, a validacao nao roda
DELTA_BSS = 0.1                                           # secao 6
PODER_PLANO = {"k_min": 4, "k_max": 10, "replicas": 2000, "alvo": 0.8}
ALFA_G_SI = 0.025         # "a rede sabe de si" = limite inferior do IC95 > 0: o teste unilateral a 2,5% (a conta do adendo 2 da V1)
ALFAS_RELATO = [0.0125, 0.05]                             # o Holm de 4 (alfa / 4, o passo mais exigente) e o alfa sem correcao
BOOTSTRAP_PLANO = {"reamostragens": 10000, "semente": 4242, "nivel": 0.95}   # secao 7
CHAVES_CONFIG = {"descricao", "plano", "unidades", "dias", "orcamento", "ponto", "montagem", "lobos", "consequencia", "corpo",
                 "passo0", "sonda", "bootstrap", "grade_passo", "poder"}


# ================================================================== a config
def modo_da_config(cfg: dict) -> str:
    """'fumaca' (bases nas sementes dos testes) ou 'calibracao' (as bases 43101...43505, K = 4, o plano). O resto falha alto: as
    sementes da validacao precisam de outro sim, e qualquer outra faixa nao e deste plano."""
    faltam = CHAVES_CONFIG - {"descricao", "plano"} - set(cfg)
    sobram = set(cfg) - CHAVES_CONFIG
    if faltam or sobram:
        raise ValueError(f"config: faltam {sorted(faltam)}, sobram {sorted(sobram)}")
    u = cfg["unidades"]
    bases = tuple(u["bases"])
    if u.get("prefixo") != PREFIXO:
        raise ValueError(f"unidades: o prefixo do plano e {PREFIXO!r} (secao 8), nao {u.get('prefixo')!r}")
    if any(type(p) is not int or p <= 0 for p in cfg["grade_passo"]) or list(cfg["grade_passo"]) != sorted(cfg["grade_passo"]):
        raise ValueError("grade_passo: inteiros positivos em ordem crescente")
    corpo_passo0 = json.loads((RAIZ / cfg["passo0"]).read_text(encoding="utf-8"))["escolha"]["corpo"]
    if cfg["corpo"] != corpo_passo0:
        raise ValueError(f"corpo: o gasto do passo 0 ({cfg['passo0']}), {corpo_passo0}; veio {cfg['corpo']}")
    if set(bases) & set(range(BASES_VALIDACAO[0], BASES_VALIDACAO[-1] + 1)):
        raise bv.SementeSemPlano("as bases da validacao (44101...44505) precisam de outro sim do Matheus (secao 6)")
    if set(bases) <= bv.SEMENTES_TESTE:
        return "fumaca"
    if bases != BASES_CALIBRACAO:
        raise bv.SementeSemPlano(f"bases {list(bases)}: so as dos testes (fumaca) ou {list(BASES_CALIBRACAO)} (calibracao, secao 8)")
    erros = []
    if cfg.get("plano") != PLANO:
        erros.append(f"plano {cfg.get('plano')!r}")
    if u["k"] != K_CALIBRACAO:
        erros.append(f"K {u['k']}")
    if cfg["dias"] != DIAS_PLANO or cfg["orcamento"] != ORCAMENTO_PLANO:
        erros.append("dias ou orcamento")
    if tuple(cfg["grade_passo"]) != GRADE_PASSO:
        erros.append(f"grade {cfg['grade_passo']}")
    if {k: cfg["poder"].get(k) for k in PODER_PLANO} != PODER_PLANO or cfg["poder"].get("alfa") != ALFA_G_SI \
            or cfg["poder"].get("alfas_relato") != ALFAS_RELATO:
        erros.append("poder")
    if cfg["bootstrap"] != BOOTSTRAP_PLANO:
        erros.append("bootstrap (secao 7: 10.000 reamostragens, semente 4242)")
    if erros:
        raise ValueError(f"a calibracao segue o plano a letra: {erros}")
    return "calibracao"


def config_bancada(cfg: dict, passo: int, bracos: list[str], mundos: list[str]) -> dict:
    """A config da bancada de um ponto da grade (ou do piloto): o atencioso, o corpo do passo 0 e a rede de si com o `passo`."""
    out = {"bracos": list(bracos), "donos": [DONO], "unidades": dict(cfg["unidades"]), "mundos": list(mundos), "dias": cfg["dias"],
           "orcamento": cfg["orcamento"], "ponto": cfg["ponto"], "montagem": cfg["montagem"], "lobos": dict(cfg["lobos"]),
           "consequencia": dict(cfg["consequencia"]), "corpo": dict(cfg["corpo"]), "sonda": dict(cfg["sonda"]),
           "bootstrap": dict(cfg["bootstrap"]), "rede_de_si": {"passo": passo}}
    if cfg.get("plano"):
        out["plano"] = cfg["plano"]
    return bv.validar_config(out)


# ================================================================== as vidas (um processo por unidade)
_BANCADAS: dict = {}


def _bancada(cfg: dict, passo: int, bracos: tuple, mundos: tuple) -> bv.Bancada:
    chave = (json.dumps(cfg, sort_keys=True), passo, bracos, mundos)
    if chave not in _BANCADAS:
        _BANCADAS[chave] = bv.bancada_da_config(config_bancada(cfg, passo, list(bracos), list(mundos)))
    return _BANCADAS[chave]


def _guardar(b: bv.Bancada, v: bv.VidaBancada, dir_vidas: Path | None) -> str:
    """Confere o replay a partir do texto do log (G1 e G1-REDE); com a pasta, grava o log antes e confere o texto do disco."""
    texto = v.motor.log.para_jsonl()
    if dir_vidas is not None:
        caminho = dir_vidas / f"{v.nome}.jsonl"
        bv._gravar(caminho, texto)
        texto = caminho.read_text(encoding="utf-8")
    b.conferir_replay(v, texto)
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def medidas_da_grade(rede, passo: int, dias_regra: tuple = DIAS_REGRA) -> dict:
    """O que a regra da secao 5 le de uma vida num `passo`: o MAE_rede(1) nos dias 1 a 7 (sem o susto) e se a rede prende pesos no teto
    no fim da vida (as duas cabecas, |w - w0| = teto)."""
    regs = rede.registros
    por_dia = bv.TICKS_POR_DIA // bv.CONFIG_PADRAO.intervalo_decisao_ticks
    ks = range((dias_regra[0] - 1) * por_dia, min(len(regs), dias_regra[1] * por_dia))
    leituras = [r["leituras"] for r in regs]
    mae = mae_previsao(leituras, [r["corpo"][str(HORIZONTE_REGRA)] for r in regs], HORIZONTE_REGRA, ks, list(rede.receptores))
    corpo = bv._resumo_pesos([w for t in rede.pesos_corpo.values() for w in t.values()],
                             [w for t in rede.prior_corpo.values() for w in t.values()], rede.cfg.teto)
    autoria = bv._resumo_pesos(list(rede.pesos_autoria.values()), list(rede.prior_autoria.values()), rede.cfg.teto)
    return {"passo": passo, "mae_rede_1": mae["mae"], "n": mae["n"], "no_teto_corpo": corpo["no_teto"],
            "no_teto_autoria": autoria["no_teto"], "no_teto": corpo["no_teto"] + autoria["no_teto"] > 0, "cortes": rede.cortes}


def tarefa_grade(cfg: dict, unidade: dict, pasta: str) -> dict:
    """A grade de uma unidade: o P1-c com cada `passo`. As vidas sao a mesma vida (a rede so observa): o log e o motor iguais em todo
    ponto (G-OBS, falha alto); o log do primeiro ponto e gravado e rejogado do disco, os outros rejogados do texto."""
    braco, mundo = BRACO_GRADE
    espec = bv.EspecVida(DONO, braco, unidade["semente"], unidade["genoma"], mundo)
    out, resumo0, sha0 = {}, None, None
    for i, passo in enumerate(cfg["grade_passo"]):
        b = _bancada(cfg, passo, (braco,), (mundo,))
        c0 = time.process_time()
        v = b.vida(espec)
        sha = _guardar(b, v, Path(pasta) / "vidas" if i == 0 else None)
        cpu = time.process_time() - c0
        resumo = bv.resumo_motor(v.motor)
        if i == 0:
            resumo0, sha0 = resumo, sha
        elif resumo != resumo0 or sha != sha0:
            raise bv.ReplayDivergiu(f"{v.nome}: a vida muda com o passo da rede (G-OBS)")
        out[str(passo)] = {**medidas_da_grade(bv.rede_de(v.motor.politica).rede, passo), "cpu_s": cpu}
    return {"vida": bv.EspecVida(DONO, braco, unidade["semente"], unidade["genoma"], mundo).nome, "base": unidade["base"],
            "k": unidade["k"], "semente": unidade["semente"], "log_sha256": sha0, "por_passo": out}


def compacta(med: dict, unidade: dict, braco: str, mundo: str, tempo: dict) -> dict:
    """O registro de uma vida do piloto que a analise le: as medidas da secao 4 que a margem e o N usam, e o custo."""
    r = med["rede_de_si"]
    m4 = r["mae"][str(r["horizonte_primario"])]
    return {"vida": med["vida"], "braco": braco, "mundo": mundo, "semente": unidade["semente"], "base": unidade["base"],
            "k": unidade["k"], "d_si": r["d_si"], "d_media": r["d_media"],
            "mae_4": {p: m4[p]["mae"] for p in ("rede", "persistencia", "media", "oraculo")}, "n_4": m4["rede"]["n"],
            "distancia_pers_oraculo": (None if m4["persistencia"]["mae"] is None or m4["oraculo"]["mae"] is None
                                       else m4["persistencia"]["mae"] - m4["oraculo"]["mae"]),
            "bss_ped": r["autoria"]["bss_ped"]["bss"], "n_ped": r["autoria"]["bss_ped"]["n"],
            "fora_ped": r["autoria"]["bss_ped"]["fora"], "bss_nasc": r["autoria"]["bss_nasc"]["bss"],
            "n_nasc": r["autoria"]["bss_nasc"]["n"], "fora_nasc": r["autoria"]["bss_nasc"]["fora"], "cortes": r["cortes"],
            "tempo": tempo}


def tarefa_piloto(cfg: dict, passo: int, unidade: dict, pasta: str) -> tuple[dict, dict]:
    """O piloto de uma unidade no `passo` escolhido: os bracos do plano que rodam, gravados, rejogados do disco e medidos."""
    completas, compactas = {}, {}
    for braco, mundo in BRACOS_PILOTO:
        b = _bancada(cfg, passo, tuple(x for x, _ in BRACOS_PILOTO), tuple(sorted({m for _, m in BRACOS_PILOTO})))
        espec = bv.EspecVida(DONO, braco, unidade["semente"], unidade["genoma"], mundo)
        c0, p0 = time.process_time(), time.perf_counter()
        v = b.vida(espec)
        _guardar(b, v, Path(pasta) / "vidas")
        cv, pv = time.process_time() - c0, time.perf_counter() - p0
        c1, p1 = time.process_time(), time.perf_counter()
        med = b.medir(v, cfg["sonda"])
        cmm, pmm = time.process_time() - c1, time.perf_counter() - p1
        med["unidade"] = {"base": unidade["base"], "k": unidade["k"]}
        completas[v.nome] = med
        compactas[v.nome] = compacta(med, unidade, braco, mundo, {"vida_cpu": cv, "vida_parede": pv, "medir_cpu": cmm,
                                                                  "medir_parede": pmm})
    return completas, compactas


def _executar(tarefas: list[tuple], processos: int) -> list:
    if processos <= 1:
        return [f(*a) for f, a in tarefas]
    with ProcessPoolExecutor(max_workers=processos) as pool:
        futuros = [pool.submit(f, *a) for f, a in tarefas]
        return [fu.result() for fu in futuros]


# ================================================================== a regra, a margem e o N
def escolher_passo(grade: list[dict], passos: list[int]) -> dict:
    """Secao 5: sai da grade o `passo` que prende pesos no teto em mais da metade das vidas; dos que ficam, o de menor MAE_rede(1) medio
    nos dias 1 a 7 (empate, o menor passo); sem nenhum, o menor passo da grade."""
    n = len(grade)
    linhas = {}
    for p in passos:
        maes = [g["por_passo"][str(p)]["mae_rede_1"] for g in grade]
        if any(x is None for x in maes):
            raise ValueError(f"passo {p}: vida sem decisao nos dias da regra")
        teto = sum(1 for g in grade if g["por_passo"][str(p)]["no_teto"])
        linhas[str(p)] = {"mae_rede_1": sum(maes) / n, "vidas_no_teto": teto, "fora_pelo_teto": teto > n / 2}
    ficam = [p for p in passos if not linhas[str(p)]["fora_pelo_teto"]]
    if not ficam:
        return {"passo": min(passos), "fechou": False, "registro": "todo passo prende pesos no teto em mais da metade das vidas: fica o "
                "menor (secao 5)", "pontos": linhas}
    escolhido = min(ficam, key=lambda p: (linhas[str(p)]["mae_rede_1"], p))
    return {"passo": escolhido, "fechou": True, "pontos": linhas}


def _do_braco(registros: list[dict], braco: str) -> list[dict]:
    return sorted((r for r in registros if r["braco"] == braco), key=lambda r: (r["base"], r["k"]))


def margens(registros: list[dict]) -> dict:
    """Secao 6: Delta_SI = 1/2 x a media, sobre as unidades do P1-c, de MAE_pers(4) - MAE_oraculo(4); se essa distancia for <= S/128,
    a validacao nao roda. Delta_MEDIA = Delta_SI; Delta_BSS = 0,1; Delta_ADAPTA espera o P1-c-lenta."""
    p1 = _do_braco(registros, "P1-c")
    dist = [r["distancia_pers_oraculo"] for r in p1]
    if not dist or any(d is None for d in dist):
        raise ValueError("a margem pede a distancia persistencia - oraculo em toda unidade do P1-c")
    media = sum(dist) / len(dist)
    return {"distancia_pers_oraculo": media, "por_unidade": dist, "delta_si": 0.5 * media, "delta_media": 0.5 * media,
            "delta_bss": DELTA_BSS, "delta_adapta": None,
            "delta_adapta_motivo": "o P1-c-lenta espera a troca da digestao (a etapa 2b, do A); a margem sai com ele",
            "limiar": LIMIAR_DISTANCIA, "validacao_roda": media > LIMIAR_DISTANCIA,
            "regra": "1/2 x [MAE_pers(4) - MAE_oraculo(4)] no P1-c, dias 8 a 14 (PRS-4); distancia <= S/128: a validacao nao roda"}


def n_efetivo(n: int, com_valor: int, total: int) -> int:
    """O N de um gate em que algumas unidades ficam sem valor (o Brier com menos de 20 decisoes): N x a fracao com valor no piloto,
    arredondado para baixo."""
    if total <= 0:
        raise ValueError("sem unidades")
    return (n * com_valor) // total


def poder_e_n(registros: list[dict], marg: dict, poder: dict, semente: int, n_bases: int) -> dict:
    """O K_u pelo poder simulado no G-SI (as diferencas D_SI por unidade do P1-c, deslocadas para Delta_SI) e, no N escolhido, o poder
    dos secundarios (so relato; abaixo de 0,5, subpotenciado). Os do Brier com o N efetivo descontado das unidades sem valor."""
    p1 = _do_braco(registros, "P1-c")
    ped = _do_braco(registros, "P1+ped-c")
    k = cm.escolher_k([r["d_si"] for r in p1], marg["delta_si"], poder, semente, n_bases)
    n = k["n"]
    secundarios = {"G-MEDIA": {"contraste": "D_MEDIA no P1-c", **cm.relato_poder([r["d_media"] for r in p1], marg["delta_media"], n,
                                                                                  poder, semente)},
                   "G-ADAPTA": {"poder": None, "motivo": marg["delta_adapta_motivo"]}}
    for nome, campo in (("G-AUT-PED", "bss_ped"), ("G-AUT-NASC", "bss_nasc")):
        vals = [r[campo] for r in ped if r[campo] is not None]
        if len(vals) < 2:
            secundarios[nome] = {"poder": None, "com_valor": len(vals), "total": len(ped),
                                 "motivo": "menos de 2 unidades do P1+ped-c com o Brier (R-5): sem poder a simular"}
            continue
        ne = n_efetivo(n, len(vals), len(ped))
        secundarios[nome] = {"contraste": f"{campo.upper()} no P1+ped-c", "com_valor": len(vals), "total": len(ped), "n_efetivo": ne,
                             **cm.relato_poder(vals, marg["delta_bss"], ne, poder, semente)}
    return {"n": k, "secundarios": secundarios}


def custo(registros: list[dict], grade: list[dict], k: int | None, n_bases: int, processos: int) -> dict:
    """O custo medido por vida e braco (CPU e parede; a vida com o replay do disco, e a medicao) e a estimativa da validacao no K
    escolhido: os cinco bracos por unidade, o P1-c-lenta pelo custo do P1-c."""
    por: dict = {}
    for r in registros:
        c = por.setdefault(r["braco"], {"vidas": 0, "cpu_s": 0.0, "parede_s": 0.0})
        t = r["tempo"]
        c["vidas"] += 1
        c["cpu_s"] += t["vida_cpu"] + t["medir_cpu"]
        c["parede_s"] += t["vida_parede"] + t["medir_parede"]
    for c in por.values():
        c["cpu_s_por_vida"] = c["cpu_s"] / c["vidas"]
    out = {"por_braco": por, "grade_cpu_s_por_vida": (sum(p["cpu_s"] for g in grade for p in g["por_passo"].values())
                                                      / max(1, sum(len(g["por_passo"]) for g in grade)))}
    if k is not None and "P1-c" in por:
        unidades = k * n_bases
        por_unidade = sum(c["cpu_s_por_vida"] for c in por.values()) + por["P1-c"]["cpu_s_por_vida"]   # + o P1-c-lenta
        out["validacao"] = {"k": k, "unidades": unidades, "vidas": unidades * (len(BRACOS_PILOTO) + 1),
                            "cpu_h": unidades * por_unidade / 3600, "parede_h_estimada": unidades * por_unidade / 3600 / max(1, processos),
                            "processos": processos}
    return out


def descritivo_piloto(registros: list[dict], boot: dict) -> dict:
    """Os numeros do piloto por braco (so descritivos: o piloto nao e evidencia, secao 6): D_SI, D_MEDIA e os MAE a 4 decisoes, com o
    IC das unidades; o Brier com as unidades fora contadas."""
    out = {}
    for braco, _ in BRACOS_PILOTO:
        rs = _do_braco(registros, braco)
        if not rs:
            continue
        linha = {"unidades": len(rs)}
        for campo in ("d_si", "d_media"):
            vals = {f"{r['base']}/{r['k']}": r[campo] for r in rs if r[campo] is not None}
            linha[campo] = cm.contraste(vals, boot) if len(vals) >= 2 else None
        linha["mae_4_medio"] = {p: sum(r["mae_4"][p] for r in rs) / len(rs) for p in ("rede", "persistencia", "media", "oraculo")}
        for campo in ("bss_ped", "bss_nasc"):
            vals = [r[campo] for r in rs if r[campo] is not None]
            linha[campo] = {"media": sum(vals) / len(vals) if vals else None, "com_valor": len(vals), "fora": len(rs) - len(vals)}
        out[braco] = linha
    return out


# ================================================================== a run
def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=RAIZ, capture_output=True, text=True, check=True).stdout.strip()


def _sha_arquivo(caminho: Path) -> str:
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


def rodar(cfg: dict, pasta: Path, processos: int, caminho_config: Path | None = None) -> dict:
    modo = modo_da_config(cfg)
    if pasta.exists():
        raise FileExistsError(f"{pasta} ja existe: a run se recusa a gravar por cima (secao 11)")
    unidades = bv.unidades_derivadas(cfg["unidades"]["bases"], int(cfg["unidades"]["k"]), PREFIXO)
    for p in cfg["grade_passo"]:                       # todo ponto monta antes de qualquer vida (falha alto cedo)
        config_bancada(cfg, p, [b for b, _ in BRACOS_PILOTO], sorted({m for _, m in BRACOS_PILOTO}))
    pasta.mkdir(parents=True)
    inicio = time.time()
    cb0 = config_bancada(cfg, cfg["grade_passo"][0], [b for b, _ in BRACOS_PILOTO], sorted({m for _, m in BRACOS_PILOTO}))
    meta = {"modo": modo, "plano": PLANO, "plano_sha256": _sha_arquivo(RAIZ / PLANO), "config": cfg,
            "config_arquivo": None if caminho_config is None else cm._relativo(caminho_config),
            "config_sha256": None if caminho_config is None else _sha_arquivo(caminho_config),
            "orquestrador_sha256": _sha_arquivo(Path(__file__)), "git_head": _git("rev-parse", "HEAD"),
            "git_limpo": _git("status", "--porcelain") == "", "processos": processos, "unidades": unidades,
            "bancada": bv.meta(cb0), "inicio": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(inicio))}
    meta["sha256"] = {"rede_de_si.py": meta["bancada"]["rede_de_si_sha256"], "lobos.py": meta["bancada"]["lobos_sha256"],
                      "corpo.py": meta["bancada"]["corpo_sha256"], "config.py": meta["bancada"]["config_sha256"],
                      "engine.py": meta["bancada"]["engine_sha256"], "plano": meta["plano_sha256"], "config": meta["config_sha256"]}
    bv._gravar(pasta / "meta.json", bv._dump(meta))

    # ---- a grade do passo (secao 5)
    t0 = time.perf_counter()
    grade = _executar([(tarefa_grade, (cfg, u, str(pasta / "grade"))) for u in unidades], processos)
    meta["grade_parede_s"] = time.perf_counter() - t0
    escolha = escolher_passo(grade, list(cfg["grade_passo"]))
    escolha.update({"regra": "o menor MAE_rede(1) nos dias 1 a 7, sem o passo que prende pesos no teto em mais da metade das vidas; sem "
                             "nenhum, o menor (secao 5)",
                    "taxa_lenta": {"taxa": None, "grade": list(GRADE_TAXA_LENTA), "no": bv.NOS_PENDENTES.get("digestao_lenta"),
                                   "registro": "o P1-c-lenta espera a troca da digestao no motor (a etapa 2b, do A): a regra da taxa "
                                               "lenta (secao 5) roda quando o no sair, nas mesmas sementes"}})
    bv._gravar(pasta / "grade" / "grade.json", bv._dump(grade))
    bv._gravar(pasta / "escolha.json", bv._dump(escolha))

    # ---- o piloto (secao 6), no passo escolhido
    t1 = time.perf_counter()
    saidas = _executar([(tarefa_piloto, (cfg, escolha["passo"], u, str(pasta / "piloto"))) for u in unidades], processos)
    meta["piloto_parede_s"] = time.perf_counter() - t1
    completas, piloto = {}, {}
    for comp, compa in saidas:
        completas.update(comp)
        piloto.update(compa)
    bv._gravar(pasta / "piloto" / "medidas.json", bv._dump(dict(sorted(completas.items()))))
    regs = list(piloto.values())
    marg = margens(regs)
    poder = {**cfg["poder"]}
    n_bases = len(cfg["unidades"]["bases"])
    resultado = {"modo": modo, "plano": PLANO, "passo": escolha["passo"], "escolha": escolha, "margens": marg,
                 "bracos_piloto": [b for b, _ in BRACOS_PILOTO],
                 "bracos_fora": {BRACO_LENTA[0]: bv.NOS_PENDENTES.get("digestao_lenta")},
                 "piloto_descritivo": descritivo_piloto(regs, cfg["bootstrap"])}
    if marg["validacao_roda"]:
        pn = poder_e_n(regs, marg, poder, cfg["bootstrap"]["semente"], n_bases)
        resultado.update(pn)
        resultado["custo"] = custo(regs, grade, pn["n"]["k"], n_bases, processos)
    else:
        resultado["leitura"] = ("a distancia persistencia - oraculo no P1-c fica em S/128 ou menos: a persistencia ja e quase o teto, e nao "
                                "ha o que aprender a 4 decisoes. Pela secao 6, a validacao nao roda e o plano volta ao Matheus.")
        resultado["custo"] = custo(regs, grade, None, n_bases, processos)
    meta["fim"] = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
    meta["duracao_s"] = time.time() - inicio
    meta["python"] = platform.python_version()
    bv._gravar(pasta / "medidas.json", bv._dump({"piloto": dict(sorted(piloto.items()))}))
    bv._gravar(pasta / "resultado.json", bv._dump(resultado))
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    return {"meta": meta, "grade": grade, "escolha": escolha, "piloto": piloto, "resultado": resultado}


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
        raise SystemExit("a fumaca precisa de --saida (fora de artifacts_v2_rede_de_si/calibracao)")
    r = rodar(cfg, saida, a.processos, caminho)["resultado"]
    print(json.dumps({"passo": r["passo"], "fechou": r["escolha"]["fechou"], "pontos": r["escolha"]["pontos"],
                      "margens": {k: r["margens"][k] for k in ("distancia_pers_oraculo", "delta_si", "validacao_roda")},
                      "n": None if "n" not in r else {k: r["n"][k] for k in ("k", "n", "poder", "chega_ao_alvo")}},
                     indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
