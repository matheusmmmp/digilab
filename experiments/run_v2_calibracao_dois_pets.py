"""V2, DOIS-PETS-CALIBRACAO: a calibracao do K e o piloto dos dois pets (docs/PLANO_ANALISE_V2_DOIS_PETS.md, secoes 5, 6, 8 e 11;
aprovados pelo Matheus em 2026-10-12, para rodar DEPOIS que a validacao do mundo fisico passar). Pela bancada do grupo
(experiments/bancada_v2.py, `Bancada.grupo`), no mundo `fisico`, nas unidades derivadas das bases 39101...39505 (K_u = 4, prefixo
"dois_pets") ou, na fumaca, nas sementes dos testes. As da validacao (40101...40505) nunca: o modo vem das sementes e recusa o resto.

As etapas, numa run so:
    K       o A informativo sozinho ("A-so", P1), `dias_a` = 10 dias, nas 20 unidades (secao 5, PDP-3). A vida ate o dia K e a mesma para
            todo K <= 10: uma run serve a grade inteira. Regra (G-K): o MENOR K de {3, 5, 7} com o limite superior do IC95 de R_A no dia K
            (bootstrap sobre as unidades) abaixo de metade da R_A do dia 1. Nenhum K passa: para, sem piloto, e volta ao Matheus
    piloto  no K escolhido, os quatro bracos (B so, B + Ainf, B + Aemb, B + Aing), o B com `dias_b` = 14 dias, nas mesmas 20 unidades
            (secao 6). Confere que o A do B + Ainf ate o dia K e o "A-so" da mesma unidade, decisao a decisao (falha alto)
    margem  Delta_S = 1/2 x [R_B(B so) - R_A(Ainf, dias K-6 a K)] (a janela cortada no dia 1); distancia <= `margem.distancia_minima`
            (0,05): a validacao nao roda e o plano volta ao Matheus
    N       o menor K_u de 4 a 10 com poder simulado >= 0,8 no G-SOCIAL, R_B(B + Aemb) - R_B(B + Ainf) por unidade (o bootstrap das
            diferencas do piloto, centradas e deslocadas para Delta_S, 2.000 replicas por K_u; o teste t unilateral a `poder.alfa`, a conta
            do A1.4 do mundo); o poder do G-COMPANHIA e do G-INGENUO no N escolhido, so relato (abaixo de 0,5, subpotenciado); o custo
            medido por grupo e a estimativa da validacao

A agregacao da R entre unidades e decisao registrada na config (`taxa.modo`, `metrics.taxa_agregada`): a unidade sem consumo de fruta
madura na janela nao tem taxa (nao e zero). `taxa.n_minimo` e o consumo somado minimo numa janela da regra; abaixo dele a regra le
"exposicao baixa" e nao passa. Nada aqui le a R_B para escolher o K (PDP-3): a etapa K so roda o A. O piloto serve so para a margem, o N
e o custo; os numeros dele nao entram como evidencia. Todo grupo e gravado e rejogado do disco bit a bit (`conferir_replay_grupo`); o
replay de medicao tambem confere. A run se recusa a rodar se a pasta de saida existe (secao 11).

    python experiments/run_v2_calibracao_dois_pets.py --config experiments/configs/v2_dois_pets/calibracao.json --processos 6
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
from digilab.config import TICKS_POR_DIA  # noqa: E402
from digilab.metrics import MODOS_TAXA_AGREGADA, bootstrap_taxa_agregada, taxa_agregada  # noqa: E402

PLANO = "docs/PLANO_ANALISE_V2_DOIS_PETS.md"
SAIDA_PADRAO = "artifacts_v2_dois_pets/calibracao"        # secao 11
PREFIXO = "dois_pets"                                      # secao 8
BASES_CALIBRACAO = (39101, 39202, 39303, 39404, 39505)     # secao 8 (PDP-6)
BASES_VALIDACAO = (40101, 40202, 40303, 40404, 40505)      # secao 8: a validacao roda uma vez, por outra config; aqui, recusada
K_CALIBRACAO = 4                                           # secao 8: K_u = 4, 20 unidades
GRADE_K = (3, 5, 7)                                        # secao 5
DIAS_A = 10                                                # secao 5: o A sozinho, 10 dias
DIAS_B = 14                                                # secao 3: o B vive 14 dias com o A
JANELA_RA_DIAS = 7                                         # secao 6: R_A(Ainf, dias K - 6 a K)
BRACOS_PILOTO = ("B-so", "B+Ainf", "B+Aemb", "B+Aing")    # secao 6
DONO = "atencioso"                                         # secao 2
LUGAR = "comedouro"                                        # secao 2 (PMF-4 do mundo)
ORCAMENTO_POR_DIA = 16                                     # secao 2 (DP-7)
MUNDO = "fisico"
JANELAS_K = {"letra": {"inicio": (1,), "bloco": 1},          # secao 5 a letra: o dia K contra o dia 1
             "dois_dias": {"inicio": (1, 2), "bloco": 2}}     # a alternativa do PR (so por adendo): os dias K-1 e K contra os dias 1 e 2
MARGEM_PLANO = {"distancia_minima": 0.05}                  # secao 6 (PROPOSTO)
PODER_PLANO = {"k_min": 4, "k_max": 10, "replicas": 2000, "alvo": 0.8}   # secao 6
BOOTSTRAP_PLANO = {"reamostragens": 10000, "semente": 4242, "nivel": 0.95}  # secao 7
CONTRASTES = {"G-SOCIAL": ("B+Aemb", "B+Ainf"),             # secao 7: primario
              "G-COMPANHIA": ("B-so", "B+Ainf"),            # secundarios (Holm)
              "G-INGENUO": ("B+Aing", "B+Ainf")}
CHAVES_CONFIG = {"descricao", "plano", "unidades", "dono", "lugar", "orcamento_por_dia", "ponto", "montagem", "lobos", "consequencia",
                 "mundo", "calibracao_k", "piloto", "taxa", "margem", "poder", "bootstrap", "adendo_janelas"}


# ================================================================== a config
def modo_da_config(cfg: dict) -> str:
    """'fumaca' (bases nas sementes dos testes) ou 'calibracao' (as bases 39101...39505, K_u = 4, o plano a letra). O resto falha alto:
    as sementes da validacao sao de outra config e de uma vez so, e qualquer outra faixa nao e deste plano."""
    faltam = CHAVES_CONFIG - {"descricao", "plano", "adendo_janelas"} - set(cfg)
    sobram = set(cfg) - CHAVES_CONFIG
    if faltam or sobram:
        raise ValueError(f"config: faltam {sorted(faltam)}, sobram {sorted(sobram)}")
    u = cfg["unidades"]
    if set(u) != {"bases", "k", "prefixo"} or u["prefixo"] != PREFIXO:
        raise ValueError(f"unidades: {{'bases', 'k', 'prefixo': {PREFIXO!r}}} (secao 8), nao {u}")
    bases = tuple(u["bases"])
    if cfg["taxa"].get("modo") not in MODOS_TAXA_AGREGADA or type(cfg["taxa"].get("n_minimo")) is not int or cfg["taxa"]["n_minimo"] < 1:
        raise ValueError(f"taxa: o modo em {MODOS_TAXA_AGREGADA} e o n_minimo inteiro >= 1, nao {cfg['taxa']}")
    ck = cfg["calibracao_k"]
    if set(ck) != {"grade_k", "dias_a", "janelas"} or ck["janelas"] not in JANELAS_K:
        raise ValueError(f"calibracao_k: {{'grade_k', 'dias_a', 'janelas' em {sorted(JANELAS_K)}}}, nao {ck}")
    grade = list(ck["grade_k"])
    if not grade or grade != sorted(set(grade)) or grade[0] < JANELAS_K[ck["janelas"]]["bloco"] or grade[-1] > ck["dias_a"]:
        raise ValueError(f"grade do K {grade}: crescente, sem repetir, do bloco da janela aos dias do A ({ck['dias_a']})")
    if tuple(cfg["piloto"]["bracos"]) != BRACOS_PILOTO:
        raise ValueError(f"bracos do piloto: {list(BRACOS_PILOTO)} (secao 6)")
    if set(bases) & set(range(BASES_VALIDACAO[0], BASES_VALIDACAO[-1] + 1)):
        raise bv.SementeSemPlano("as bases da validacao (40101...40505) rodam uma vez, pela config da validacao: nunca na calibracao")
    if set(bases) <= bv.SEMENTES_TESTE:
        return "fumaca"
    if bases != BASES_CALIBRACAO:
        raise bv.SementeSemPlano(f"bases {list(bases)}: so as dos testes (fumaca) ou {list(BASES_CALIBRACAO)} (calibracao, secao 8)")
    erros = []
    if cfg.get("plano") != PLANO:
        erros.append(f"plano {cfg.get('plano')!r}")
    if u["k"] != K_CALIBRACAO:
        erros.append(f"K_u {u['k']}")
    if (cfg["dono"], cfg["lugar"], cfg["orcamento_por_dia"]) != (DONO, LUGAR, ORCAMENTO_POR_DIA):
        erros.append("dono, lugar ou orcamento (secao 2)")
    if tuple(grade) != GRADE_K or ck["dias_a"] != DIAS_A:
        erros.append("grade do K ou dias do A (secao 5)")
    if ck["janelas"] != "letra" and cfg.get("adendo_janelas") is None:
        erros.append("janelas fora da letra da secao 5 sem o adendo do plano (campo adendo_janelas)")
    if cfg["piloto"]["dias_b"] != DIAS_B:
        erros.append("dias do B (secao 3)")
    if cfg["montagem"] != "completa":
        erros.append("montagem (secao 2: o cerebro A com a montagem completa)")
    if cfg["margem"] != MARGEM_PLANO:
        erros.append("margem (secao 6)")
    if {k: cfg["poder"].get(k) for k in PODER_PLANO} != PODER_PLANO:
        erros.append("poder (secao 6)")
    if cfg["bootstrap"] != BOOTSTRAP_PLANO:
        erros.append("bootstrap (secao 7: 10.000 reamostragens, semente 4242)")
    if erros:
        raise ValueError(f"a calibracao segue o plano a letra: {erros}")
    return "calibracao"


def config_grupo(cfg: dict, bracos: list[str], k: int, dias: int) -> dict:
    """A config da bancada do grupo de uma etapa, conferida pela bancada (`validar_config_grupo`: o plano, a montagem completa fora das
    sementes dos testes, as faixas queimadas)."""
    out = {"tipo": "grupo", "bracos": list(bracos), "unidades": dict(cfg["unidades"]), "k_dias": k, "dias": dias,
           "orcamento_por_dia": cfg["orcamento_por_dia"], "dono": cfg["dono"], "lugar": cfg["lugar"], "ponto": cfg["ponto"],
           "montagem": cfg["montagem"], "lobos": dict(cfg["lobos"]), "consequencia": dict(cfg["consequencia"]),
           "mundo": dict(cfg["mundo"])}
    if cfg.get("plano"):
        out["plano"] = cfg["plano"]
    return bv.validar_config_grupo(out)


def bancada_da_etapa(cg: dict) -> bv.Bancada:
    return bv.bancada_da_config({**cg, "orcamento": int(cg["orcamento_por_dia"]) * int(cg["dias"])})


def teto_dos_pesos(cfg: dict) -> dict:
    """O degrau 1 cabe no teto? O cerebro de cada pet de cada braco (o A informativo e o embaralhado P1, o ingenuo P0, o B P1), montado
    pela bancada do grupo como a run o monta (a montagem completa, o alvo aprendido, as entradas sociais, o modelo dos outros e a rota do
    humor, `presenca_fruta_mundo`): os pesos, o teto, os canais e a memoria (so nos mundos das frutas). Acima do teto, o cerebro ja falha
    alto ao nascer; aqui sai o numero."""
    b = bancada_da_etapa(config_grupo(cfg, list(BRACOS_PILOTO), cfg["calibracao_k"]["grade_k"][0], cfg["piloto"]["dias_b"]))
    bg = b.bancada_grupo()
    out = {}
    for braco in ("A-so",) + BRACOS_PILOTO:
        k = 0 if braco == "A-so" else cfg["calibracao_k"]["grade_k"][0]
        eg = bv.EspecGrupo(braco, 101, k, cfg["dono"], cfg["lugar"])
        for ident, braco_pet, _ in bv._entradas(eg):
            espec = b.espec_do_pet(eg, ident)
            c = bv.do_braco(bg.politica(espec)).cerebro
            cl = c.cl
            out[f"{braco}/{ident}"] = {"braco_pet": braco_pet, "pesos": c.n_pesos(), "teto": cl.maximo_pesos,
                                       "cabe": c.n_pesos() < cl.maximo_pesos, "canais": bg.canais_no_pet(espec),
                                       "memoria": getattr(c, "_memoria", None) is not None, "alvo_aprendido": cl.alvo_aprendido,
                                       "entradas_sociais": cl.entradas_sociais, "modelo_outros": cl.modelo_outros,
                                       "presenca_fruta_mundo": cl.presenca_fruta_mundo, "aprende": c.aprende}
    if not all(v["cabe"] for v in out.values()):
        raise RuntimeError(f"o degrau 1 passa do teto de pesos: {out}")
    return out


# ================================================================== os grupos (um processo por unidade)
def _cronometrar(f, *a):
    c0, p0 = time.process_time(), time.perf_counter()
    r = f(*a)
    return r, time.process_time() - c0, time.perf_counter() - p0


def _guardar(b: bv.Bancada, v: bv.VidaGrupo, dir_grupos: Path) -> None:
    """Grava o registro do grupo e confere o replay a partir do texto do disco (G1-GRUPO)."""
    caminho = dir_grupos / f"{v.nome}.jsonl"
    bv._gravar(caminho, v.grupo.registro.para_jsonl())
    b.conferir_replay_grupo(v, caminho.read_text(encoding="utf-8"))


def _rastro_ate(m, tick_fim: int) -> tuple:
    """O que o pet fez antes de `tick_fim` (relogio do mundo): as decisoes, os consumos e o log do pet ate o tick dele."""
    return ([d for d in m.decisoes_mundo if d["tick"] < tick_fim], [c for c in m.consumos_mundo if c["tick"] < tick_fim],
            [e for e in m.log if e.tick + m.entrada_mundo < tick_fim])


def tarefa_k(cfg: dict, unidade: dict, pasta: str) -> tuple[str, dict, dict]:
    """O "A-so" de uma unidade: o A informativo sozinho, `dias_a` dias, gravado, rejogado do disco e medido."""
    cg = config_grupo(cfg, ["A-so"], 0, cfg["calibracao_k"]["dias_a"])
    b = bancada_da_etapa(cg)
    v, cv, pv = _cronometrar(b.grupo, bv.EspecGrupo("A-so", unidade["semente"], 0, cfg["dono"], cfg["lugar"]))
    _guardar(b, v, Path(pasta) / "grupos")
    med, cmed, pmed = _cronometrar(b.medir_grupo, v)
    med["unidade"] = {"base": unidade["base"], "k": unidade["k"]}
    return v.nome, med, {"grupo_cpu": cv, "grupo_parede": pv, "medir_cpu": cmed, "medir_parede": pmed}


def tarefa_piloto(cfg: dict, k: int, unidade: dict, pasta: str, pasta_k: str) -> dict:
    """Os quatro bracos de uma unidade no K escolhido, gravados, rejogados do disco e medidos. O "A-so" e refeito so como conferencia: o
    registro dele tem de ser o da etapa K, byte a byte, e o A do B + Ainf ate o dia K tem de ser ele (as decisoes, os consumos e o log)."""
    ck = config_grupo(cfg, ["A-so"], 0, cfg["calibracao_k"]["dias_a"])
    bk = bancada_da_etapa(ck)
    a_so = bk.grupo(bv.EspecGrupo("A-so", unidade["semente"], 0, cfg["dono"], cfg["lugar"]))
    gravado = (Path(pasta_k) / "grupos" / f"{a_so.nome}.jsonl").read_text(encoding="utf-8")
    if gravado != a_so.grupo.registro.para_jsonl():
        raise bv.ReplayDivergiu(f"{a_so.nome}: o A-so refeito no piloto nao e o da etapa K")
    cg = config_grupo(cfg, list(BRACOS_PILOTO), k, cfg["piloto"]["dias_b"])
    b = bancada_da_etapa(cg)
    out = {}
    for braco in BRACOS_PILOTO:
        v, cv, pv = _cronometrar(b.grupo, bv.EspecGrupo(braco, unidade["semente"], k, cfg["dono"], cfg["lugar"]))
        _guardar(b, v, Path(pasta) / "grupos")
        if braco == "B+Ainf":
            fim = k * TICKS_POR_DIA
            if _rastro_ate(v.grupo.motores["A"], fim) != _rastro_ate(a_so.grupo.motores["A"], fim):
                raise RuntimeError(f"{v.nome}: o A ate o dia {k} nao e o A-so da unidade (secao 5: a vida ate o dia K e a mesma)")
        med, cmed, pmed = _cronometrar(b.medir_grupo, v)
        med["unidade"] = {"base": unidade["base"], "k": unidade["k"]}
        out[v.nome] = (med, {"grupo_cpu": cv, "grupo_parede": pv, "medir_cpu": cmed, "medir_parede": pmed})
    return out


def _executar(tarefas: list[tuple], processos: int) -> list:
    if processos <= 1:
        return [f(*a) for f, a in tarefas]
    with ProcessPoolExecutor(max_workers=processos) as pool:
        futuros = [pool.submit(f, *a) for f, a in tarefas]
        return [fu.result() for fu in futuros]


# ================================================================== a analise (funcoes puras)
def contagem(med_pet: dict, janelas: list[str]) -> tuple[int, int]:
    """(n, ruins) de um pet somados nas janelas dele (`taxa_fruta_ruim` do `medir_grupo`)."""
    t = med_pet["taxa_fruta_ruim"]
    return sum(t[j]["n"] for j in janelas), sum(t[j]["ruins"] for j in janelas)


def janela_ra(k: int) -> list[str]:
    """Os dias K - 6 a K do A (secao 6), cortados no dia 1."""
    return [f"dia_{d}" for d in range(max(1, k - JANELA_RA_DIAS + 1), k + 1)]


def regra_k(medidas_a: list[dict], grade: list[int], taxa: dict, boot: dict, janelas: str = "letra") -> dict:
    """G-K na calibracao (secao 5): por K da grade, a R_A no dia K (o ponto e o IC95 do bootstrap sobre as unidades) contra metade da
    R_A do dia 1 (o ponto). Passa com o limite superior abaixo da metade e o consumo somado das duas janelas >= `taxa.n_minimo`. O K
    escolhido e o MENOR que passa; nenhum, None. Com `janelas` = "dois_dias" (so por adendo), os dias K-1 e K contra os dias 1 e 2."""
    jan = JANELAS_K[janelas]
    pets = [m["pets"]["A"] for m in medidas_a]
    dia1 = taxa_agregada([contagem(p, [f"dia_{d}" for d in jan["inicio"]]) for p in pets], taxa["modo"])
    por_k = {}
    for k in grade:
        dias_k = [f"dia_{d}" for d in range(k - jan["bloco"] + 1, k + 1)]
        dk = bootstrap_taxa_agregada([contagem(p, dias_k) for p in pets], taxa["modo"], boot["reamostragens"], boot["semente"],
                                     boot["nivel"])
        exposicao = dia1["n"] >= taxa["n_minimo"] and dk["n"] >= taxa["n_minimo"]
        limiar = None if dia1["taxa"] is None else 0.5 * dia1["taxa"]
        superior = None if dk["ic"] is None else dk["ic"]["ic_superior"]
        passa = exposicao and limiar is not None and superior is not None and superior < limiar
        leitura = ("exposicao baixa" if not exposicao else "sem IC" if superior is None or limiar is None
                   else "aprendeu" if passa else "nao aprendeu")
        por_k[str(k)] = {"dias": dias_k, "r_a_dia_k": dk, "limiar": limiar, "passa": passa, "leitura": leitura}
    passam = [k for k in grade if por_k[str(k)]["passa"]]
    so_exposicao = not passam and all(v["leitura"] == "exposicao baixa" for v in por_k.values())
    return {"regra": "o menor K de {3, 5, 7} com o limite superior do IC95 de R_A no dia K abaixo de metade da R_A do dia 1 (secao 5)",
            "janelas": janelas, "dias_inicio": [f"dia_{d}" for d in jan["inicio"]], "r_a_dia_1": dia1, "por_k": por_k,
            "k": passam[0] if passam else None, "fechou": bool(passam), "so_exposicao_baixa": so_exposicao,
            "taxa": dict(taxa), "unidades": len(pets)}


def por_unidade_rb(medidas: list[dict], braco_a: str, braco_b: str) -> dict:
    """{semente: R_B(a) - R_B(b)} nos 7 primeiros dias do B (a taxa da unidade, PDP-2). A unidade sem consumo do B num dos dois bracos
    sai, contada: o contraste e por unidade e a taxa sem consumo nao existe."""
    idx = {}
    for m in medidas:
        chave = (m["semente"], m["braco"])
        if chave in idx:
            raise RuntimeError(f"grupo repetido: {chave}")
        idx[chave] = m["pets"]["B"]["taxa_fruta_ruim"]["primeiros_7"]["taxa"]
    difs, sem = {}, []
    for s in sorted({m["semente"] for m in medidas}):
        if (s, braco_a) not in idx or (s, braco_b) not in idx:
            raise RuntimeError(f"unidade {s}: falta {braco_a} ou {braco_b}")
        a, b = idx[(s, braco_a)], idx[(s, braco_b)]
        if a is None or b is None:
            sem.append(s)
        else:
            difs[s] = a - b
    return {"difs": difs, "sem_consumo": sem}


def margem(medidas: list[dict], k: int, taxa: dict, distancia_minima: float) -> dict:
    """Secao 6: Delta_S = 1/2 x [R_B(B so) - R_A(Ainf, dias K-6 a K)], as duas pela agregacao da config. A distancia <= o minimo: a
    validacao nao roda."""
    b_so = taxa_agregada([contagem(m["pets"]["B"], ["primeiros_7"]) for m in medidas if m["braco"] == "B-so"], taxa["modo"])
    jan = janela_ra(k)
    a_inf = taxa_agregada([contagem(m["pets"]["A"], jan) for m in medidas if m["braco"] == "B+Ainf"], taxa["modo"])
    if b_so["taxa"] is None or a_inf["taxa"] is None:
        return {"r_b_so": b_so, "r_a_inf": a_inf, "janela_a": jan, "distancia": None, "delta_s": None, "valida": False,
                "leitura": "sem consumo: a margem nao existe"}
    d = b_so["taxa"] - a_inf["taxa"]
    valida = d > distancia_minima
    return {"r_b_so": b_so, "r_a_inf": a_inf, "janela_a": jan, "distancia": d, "delta_s": 0.5 * d, "valida": valida,
            "distancia_minima": distancia_minima,
            "leitura": "a margem existe" if valida else
            f"distancia <= {distancia_minima}: o A nao sabe muito mais que o B ingenuo; a validacao nao roda e o plano volta ao Matheus"}


def custo(tempos: list[tuple[str, dict]], k_u: int | None, n_bases: int, processos: int) -> dict:
    """O custo medido por grupo e braco (CPU e parede; o grupo com a gravacao e o replay do disco, e a medicao) e a estimativa da
    validacao no K_u escolhido: os quatro bracos por unidade (R-7)."""
    por = {}
    for braco, t in tempos:
        c = por.setdefault(braco, {"grupos": 0, "cpu_s": 0.0, "parede_s": 0.0})
        c["grupos"] += 1
        c["cpu_s"] += t["grupo_cpu"] + t["medir_cpu"]
        c["parede_s"] += t["grupo_parede"] + t["medir_parede"]
    for c in por.values():
        c["cpu_s_por_grupo"] = c["cpu_s"] / c["grupos"]
        c["parede_s_por_grupo"] = c["parede_s"] / c["grupos"]
    out = {"por_braco": por, "cpu_s_total": sum(c["cpu_s"] for c in por.values())}
    if k_u is not None and all(b in por for b in BRACOS_PILOTO):
        n = n_bases * k_u
        cpu = sum(por[b]["cpu_s_por_grupo"] for b in BRACOS_PILOTO) * n
        out["validacao_estimada"] = {"k_u": k_u, "n": n, "grupos": n * len(BRACOS_PILOTO), "cpu_h": cpu / 3600,
                                     "parede_h_em_processos": {"processos": processos, "horas": cpu / 3600 / processos}}
    return out


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=RAIZ, capture_output=True, text=True, check=True).stdout.strip()


def _sha_arquivo(caminho: Path) -> str:
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


def _relativo(caminho: Path) -> str:
    c = caminho.resolve()
    return c.relative_to(RAIZ).as_posix() if c.is_relative_to(RAIZ) else c.as_posix()


# ================================================================== a run
def rodar(cfg: dict, pasta: Path, processos: int = 1, caminho_config: Path | None = None) -> dict:
    modo = modo_da_config(cfg)
    if pasta.exists():
        raise FileExistsError(f"{pasta} ja existe: a run se recusa a gravar por cima (secao 11)")
    unidades = bv.unidades_derivadas(cfg["unidades"]["bases"], int(cfg["unidades"]["k"]), PREFIXO)
    teto = teto_dos_pesos(cfg)
    pasta.mkdir(parents=True)
    inicio = time.time()
    b_meta = bv.meta(config_grupo(cfg, ["A-so"], 0, cfg["calibracao_k"]["dias_a"]))
    meta = {"modo": modo, "plano": PLANO, "plano_sha256": _sha_arquivo(RAIZ / PLANO), "config": cfg,
            "config_arquivo": None if caminho_config is None else _relativo(caminho_config),
            "config_sha256": None if caminho_config is None else _sha_arquivo(caminho_config),
            "orquestrador_sha256": _sha_arquivo(Path(__file__)), "git_head": _git("rev-parse", "HEAD"),
            "git_limpo": _git("status", "--porcelain") == "", "processos": processos, "unidades": unidades, "teto_dos_pesos": teto,
            "bancada": b_meta, "inicio": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(inicio)),
            "sha256": {"mundo.py": b_meta["mundo_sha256"], "grupo.py": _sha_arquivo(RAIZ / "digilab" / "grupo.py"),
                       "lobos.py": b_meta["lobos_sha256"], "config.py": b_meta["config_sha256"], "engine.py": b_meta["engine_sha256"]}}
    bv._gravar(pasta / "meta.json", bv._dump(meta))

    # ---- o K (secao 5): so o A sozinho
    pasta_k = pasta / "k"
    t0 = time.perf_counter()
    saidas = _executar([(tarefa_k, (cfg, u, str(pasta_k))) for u in unidades], processos)
    meta["k_parede_s"] = time.perf_counter() - t0
    medidas_k = {nome: med for nome, med, _ in saidas}
    bv._gravar(pasta_k / "medidas.json", bv._dump(dict(sorted(medidas_k.items()))))
    tempos = [("A-so", t) for _, _, t in saidas]
    gk = regra_k(list(medidas_k.values()), list(cfg["calibracao_k"]["grade_k"]), cfg["taxa"], cfg["bootstrap"],
                 cfg["calibracao_k"]["janelas"])
    bv._gravar(pasta / "k.json", bv._dump(gk))
    resultado = {"modo": modo, "plano": PLANO, "k": gk["k"], "fechou_k": gk["fechou"], "g_k": gk}
    if not gk["fechou"]:
        resultado["leitura"] = (("nenhum K passa, e em todos pela exposicao: o A come pouca fruta madura nas janelas da regra (consumo "
                                 "somado abaixo de taxa.n_minimo), e a regra nao mede o aprendizado. " if gk["so_exposicao_baixa"] else
                                 "nenhum K passa: o A nao aprende no mundo fisico em 7 dias, e nao ha o que transmitir. ")
                                + "O plano para e volta ao Matheus (secao 5); sem piloto.")
        resultado["custo"] = custo(tempos, None, len(cfg["unidades"]["bases"]), processos)
        return _fechar(pasta, meta, resultado, inicio)

    # ---- o piloto (secao 6), no K escolhido
    k = gk["k"]
    pasta_p = pasta / "piloto"
    t0 = time.perf_counter()
    saidas = _executar([(tarefa_piloto, (cfg, k, u, str(pasta_p), str(pasta_k))) for u in unidades], processos)
    meta["piloto_parede_s"] = time.perf_counter() - t0
    medidas_p = {}
    for s in saidas:
        for nome, (med, t) in s.items():
            medidas_p[nome] = med
            tempos.append((med["braco"], t))
    bv._gravar(pasta_p / "medidas.json", bv._dump(dict(sorted(medidas_p.items()))))
    regs = list(medidas_p.values())
    mg = margem(regs, k, cfg["taxa"], cfg["margem"]["distancia_minima"])
    resultado["margem"] = mg
    n_bases = len(cfg["unidades"]["bases"])
    if not mg["valida"]:
        resultado["leitura"] = mg["leitura"]
        resultado["custo"] = custo(tempos, None, n_bases, processos)
        return _fechar(pasta, meta, resultado, inicio)
    semente = cfg["bootstrap"]["semente"]
    social = por_unidade_rb(regs, *CONTRASTES["G-SOCIAL"])
    n = cm.escolher_k(list(social["difs"].values()), mg["delta_s"], cfg["poder"], semente, n_bases)
    relato = {}
    for nome in ("G-COMPANHIA", "G-INGENUO"):
        pu = por_unidade_rb(regs, *CONTRASTES[nome])
        relato[nome] = {"contraste": " - ".join(CONTRASTES[nome]), "sem_consumo": pu["sem_consumo"],
                        **cm.relato_poder(list(pu["difs"].values()), mg["delta_s"], n["n"], cfg["poder"], semente)}
    resultado.update({"n": {**n, "contraste": "R_B(B+Aemb) - R_B(B+Ainf), por unidade (G-SOCIAL)",
                            "sem_consumo": social["sem_consumo"], "unidades_com_valor": len(social["difs"])},
                      "poder_relato": relato, "custo": custo(tempos, n["k"], n_bases, processos)})
    return _fechar(pasta, meta, resultado, inicio)


def _fechar(pasta: Path, meta: dict, resultado: dict, inicio: float) -> dict:
    meta["fim"] = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
    meta["duracao_s"] = time.time() - inicio
    meta["python"] = platform.python_version()
    bv._gravar(pasta / "resultado.json", bv._dump(resultado))
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    return {"meta": meta, "resultado": resultado}


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
        raise SystemExit("a fumaca precisa de --saida (fora de artifacts_v2_dois_pets/calibracao)")
    saida = Path(a.saida) if a.saida else RAIZ / SAIDA_PADRAO
    r = rodar(cfg, saida, a.processos, caminho)["resultado"]
    print(json.dumps({"k": r["k"], "fechou_k": r["fechou_k"],
                      "margem": None if "margem" not in r else {c: r["margem"][c] for c in ("distancia", "delta_s", "valida")},
                      "n": None if "n" not in r else {c: r["n"][c] for c in ("k", "n", "poder", "chega_ao_alvo")}},
                     indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
