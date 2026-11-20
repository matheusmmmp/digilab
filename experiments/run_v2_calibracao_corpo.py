"""V2, CORPO-CALIBRACAO: a calibracao do corpo (docs/PLANO_ANALISE_V2_CORPO_DRIVES.md, secao 6, secao 7 e adendos 1 a 3; autorizada pelo
Matheus em 2026-10-12). Pela bancada (experiments/bancada_v2.py), nos mundos `bola` e `padrao`, nas unidades derivadas das bases
33101...33505 (K = 4, prefixo "corpo") ou, na fumaca, nas sementes dos testes. As da validacao (34101...34505) nunca: o modo vem das
sementes e recusa o resto. O passo 0 (A3.2b, o m_gasto do metabolismo) roda antes, pela bancada (`bancada_v2.py --passo0`); o gasto
escolhido entra aqui fixo, pela chave `corpo` da config.

As etapas, numa run so:
    grade    so o P0-c, (m_sobe, m_reduz) em {1/2, 1, 2}^2 (6.1), as 8 celulas (4 donos x 2 mundos): 72 vidas por unidade
    regra    (6.2) passo 1: a faixa dos drives no P0-c, os dois mundos juntos (tedio e solidao: a fracao das decisoes acordado com a falta
             >= 0,75 em [0,10; 0,50]; estresse <= 0,20); passo 2: dos que passam, o mais perto de (1, 1) pela soma de |log2|, empate no
             menor m_sobe; sem nenhum, o mais perto do centro das faixas, "nao fechou". Passo 3: no ponto, o menor w_novos de {1, 2, 4} com
             a mediana da parcela dos drives novos em [0,25; 0,75], nas decisoes de tempo livre com sinal das vidas do P0-c (a sonda); sem
             nenhum, o de mediana mais perto de 0,5, "nao fechou"
    piloto   (6.3) no ponto: os blocos da secao 4 e dos adendos 1 e 2 (G-HOJE, corpo com os acoplados, tapa, G e P1-cw): 120 vidas por
             unidade. So para as margens, o N e o custo; os numeros dele nao sao evidencia
    sensib.  (6.4) o P1-c-tapa com o recompensa_tapa em -0,5 e -2,0; (A1.2) o P0-c com a janela do tedio em 4 e 16. So relato
    N        (secao 7) as margens pela regra registrada; o menor K de 4 a 10 por base com poder simulado >= 0,8 em cada gate (bootstrap das
             diferencas por unidade do piloto, 2.000 replicas por K); o N e o maior entre os gates; o custo medido

A regra da grade so le o P0-c (6.2, PCD-4): nem a BE do P1 nem contraste entre bracos. Toda vida e gravada e rejogada do disco bit a bit
(Bancada.conferir_replay); o replay de medicao tambem confere. A run se recusa a rodar se a pasta de saida existe (secao 11).

    python experiments/run_v2_calibracao_corpo.py --config experiments/configs/v2_corpo/calibracao.json --processos 8
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import random
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v2_experimento_maior as em  # noqa: E402
from digilab.config import ConfigCorpo  # noqa: E402
from digilab.metrics import contraste_pareado  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402

PLANO = "docs/PLANO_ANALISE_V2_CORPO_DRIVES.md"
SAIDA_PADRAO = "artifacts_v2_corpo/calibracao/grade_piloto"
PREFIXO = "corpo"
BASES_CALIBRACAO = (33101, 33202, 33303, 33404, 33505)    # secao 10 (PCD-7)
BASES_VALIDACAO = (34101, 34202, 34303, 34404, 34505)     # secao 8: precisa de outro sim; aqui, recusada
K_CALIBRACAO = 4
DONOS_V1 = ("atencioso", "relapso", "aleatorio", "incoerente")   # secao 2
MUNDOS = ("bola", "padrao")                               # secao 2
DIAS_PLANO = 14
ORCAMENTO_PLANO = 224
GRADE_M = (0.5, 1.0, 2.0)                                 # 6.1: m_sobe e m_reduz
GRADE_W = (1, 2, 4)                                       # 6.1: w_novos
GRADE_SOL = (1.0, 2.0, 4.0)                               # A5.2: m_sol, so a subida da solidao (sem a chave na config: so o 1)
FAIXA_TEDIO_SOLIDAO = (0.10, 0.50)                        # 6.2, passo 1
TETO_ESTRESSE = 0.20
FAIXA_PARCELA = (0.25, 0.75)                              # 6.2, passo 3
SENSIBILIDADE_TAPA = (-0.5, -2.0)                         # 6.4: 1/2x e 2x do -1,0 (CD-10)
SENSIBILIDADE_JANELA = (4, 16)                            # A1.2
PODER_PLANO = {"k_min": 4, "k_max": 10, "replicas": 2000, "alvo": 0.8}   # secao 7
ALFA_EFEITO = 0.025      # "ganha" = limite inferior do IC95 > 0: o teste t unilateral a 2,5% (a conta do adendo 2 da V1)
ALFA_NAO_INFERIOR = 0.025   # G-CUIDADO: o limite superior do IC95 < a margem
ALFA_EQUIVALENCIA = 0.05    # G-HOJE (b): o IC90 dentro de +- a margem (dois testes unilaterais a 5%)
NOVOS_W = bv.NOVOS_W

# o piloto (6.3, adendos 1 e 2): (braco, mundos); os acoplados ao P0-q da mesma celula (3.2)
BLOCO_G_HOJE = ("P0-hoje", "P1-hoje", "P3-hoje", "P0-quimica", "P1-quimica", "P3-quimica")
BLOCO_CORPO = ("P0-q", "P1-q", "P0-c", "P1-c")
ACOPLADOS = ("P1-q", "P1-c")                              # P1-q^ac e P1-c^ac, do P0-q, filtro nenhum
BLOCO_TAPA = ("P0-c-tapa", "P1-c-tapa")                   # so no mundo bola (3.3)
BLOCO_G = ("P1-c-tapaX", "P1-c-frutas")                   # so no iguais_frutas (A1.1); no piloto, so o custo
BLOCO_CW = ("P1-cw",)                                     # A2.5; no piloto, so o custo
ROT_AC = {b: f"{b}<P0-q:nenhum" for b in ACOPLADOS}
VIDAS_POR_UNIDADE_VALIDACAO = 120                         # 104 + 8 (bloco G) + 8 (P1-cw)

# os campos da ConfigCorpo que a grade escala (6.1 e A1.2)
CAMPOS_SOBE = ("tedio_sobe", "solidao_sobe")              # x m_sobe; o estresse_divisor / m_sobe (a subida do estresse)
CAMPOS_REDUZ = ("tedio_bola", "tedio_brincar", "tedio_explorar", "tedio_dono", "carinho_solidao", "carinho_estresse")
CAMPOS_PASSO0 = ("gasto_basal_acordado", "gasto_basal_dormindo", "gasto_atividades_num", "gasto_atividades_den")

CHAVES_CONFIG = {"descricao", "plano", "donos", "unidades", "mundos", "dias", "orcamento", "ponto", "montagem", "lobos", "consequencia",
                 "sonda", "bootstrap", "corpo", "passo0", "grade", "faixas", "poder", "sensibilidade"}


# ================================================================== a config
def rotulo(m) -> str:
    return f"{m:g}"


def nome_ponto(ms: float, mr: float, msol: float = 1.0) -> str:
    """O nome do ponto; com m_sol != 1 (A5.2), o sufixo "_sol_<m>" (o m_sol = 1 tem o nome de antes)."""
    return f"sobe_{rotulo(ms)}_reduz_{rotulo(mr)}" + ("" if msol == 1.0 else f"_sol_{rotulo(msol)}")


def grade_sol(cfg: dict) -> tuple:
    """Os m_sol da config (A5.2, a chave "m_solidao" da grade) ou so o 1 (a grade da 6.1)."""
    return tuple(float(m) for m in cfg["grade"].get("m_solidao", [1.0]))


def pontos_da_grade(cfg: dict) -> list[tuple]:
    """Os pontos (m_sobe, m_reduz, m_sol) da grade, na ordem m_sobe, m_reduz, m_sol."""
    return [(ms, mr, msol) for ms in cfg["grade"]["m_sobe"] for mr in cfg["grade"]["m_reduz"] for msol in grade_sol(cfg)]


def _arred(x: float) -> int:
    """metade para longe do zero (o div_arred para positivos): 225 x 1/2 = 113 (registro)"""
    return int(math.floor(x + 0.5))


def corpo_do_ponto(cfg: dict, ms: float, mr: float, msol: float = 1.0) -> dict:
    """Os numeros da ConfigCorpo no ponto (m_sobe, m_reduz, m_sol), sobre os PROPOSTOS da tarefa e o gasto do passo 0 (fixo): as subidas
    x m_sobe (o divisor do estresse / m_sobe), a da solidao x m_sobe x m_sol (A5.2) e as reducoes x m_reduz (6.1, com as bases do tedio
    da regra nova, A1.2)."""
    base = ConfigCorpo()
    out = dict(cfg["corpo"])
    for c in CAMPOS_SOBE:
        out[c] = _arred(getattr(base, c) * ms * (msol if c == "solidao_sobe" else 1.0))
    out["estresse_divisor"] = _arred(base.estresse_divisor / ms)
    for c in CAMPOS_REDUZ:
        out[c] = _arred(getattr(base, c) * mr)
    return out


def modo_da_config(cfg: dict) -> str:
    """'fumaca' (sementes dos testes) ou 'calibracao' (as bases 33101...33505, K = 4, o plano). O resto falha alto."""
    faltam = CHAVES_CONFIG - {"descricao", "plano"} - set(cfg)
    sobram = set(cfg) - CHAVES_CONFIG
    if faltam or sobram:
        raise ValueError(f"config: faltam {sorted(faltam)}, sobram {sorted(sobram)}")
    u = cfg["unidades"]
    bases = tuple(u["bases"])
    if u.get("prefixo") != PREFIXO:
        raise ValueError(f"unidades: o prefixo do plano e {PREFIXO!r} (secao 4), nao {u.get('prefixo')!r}")
    if set(cfg["corpo"]) != set(CAMPOS_PASSO0):
        raise ValueError(f"corpo: so o gasto do passo 0 {CAMPOS_PASSO0} (a grade escala o resto)")
    if tuple(cfg["mundos"]) != MUNDOS or set(cfg["donos"]) - set(DONOS_V1) or not cfg["donos"]:
        raise ValueError("mundos e donos do plano: bola e padrao, os 4 da v1")
    if set(bases) & set(range(BASES_VALIDACAO[0], BASES_VALIDACAO[-1] + 1)):
        raise bv.SementeSemPlano("as bases da validacao (34101...34505) precisam de outro sim do Matheus")
    if set(bases) <= bv.SEMENTES_TESTE:
        return "fumaca"
    if bases != BASES_CALIBRACAO:
        raise bv.SementeSemPlano(f"bases {list(bases)}: so as dos testes (fumaca) ou {list(BASES_CALIBRACAO)} (calibracao, secao 10)")
    erros = []
    if cfg.get("plano") != PLANO:
        erros.append(f"plano {cfg.get('plano')!r}")
    if u["k"] != K_CALIBRACAO:
        erros.append(f"K {u['k']}")
    if tuple(sorted(cfg["donos"])) != tuple(sorted(DONOS_V1)):
        erros.append("donos")
    if cfg["dias"] != DIAS_PLANO or cfg["orcamento"] != ORCAMENTO_PLANO:
        erros.append("dias ou orcamento")
    if (tuple(cfg["grade"]["m_sobe"]) != GRADE_M or tuple(cfg["grade"]["m_reduz"]) != GRADE_M
            or tuple(cfg["grade"]["w_novos"]) != GRADE_W
            or ("m_solidao" in cfg["grade"] and grade_sol(cfg) != GRADE_SOL)):
        erros.append("grade")
    if (tuple(cfg["faixas"]["tedio_solidao"]) != FAIXA_TEDIO_SOLIDAO or cfg["faixas"]["estresse_max"] != TETO_ESTRESSE
            or tuple(cfg["faixas"]["parcela_novos"]) != FAIXA_PARCELA):
        erros.append("faixas")
    if {k: cfg["poder"][k] for k in PODER_PLANO} != PODER_PLANO:
        erros.append("poder")
    if (tuple(cfg["sensibilidade"]["recompensa_tapa"]) != SENSIBILIDADE_TAPA
            or tuple(cfg["sensibilidade"]["janela_tedio"]) != SENSIBILIDADE_JANELA):
        erros.append("sensibilidade")
    if cfg["bootstrap"] != {"reamostragens": 10000, "semente": 4242, "nivel": 0.95}:
        erros.append("bootstrap (secao 8: 10.000 reamostragens, semente 4242)")
    passo0 = json.loads((RAIZ / cfg["passo0"]).read_text(encoding="utf-8"))
    if passo0["escolha"]["corpo"] != cfg["corpo"]:
        erros.append(f"o corpo da config nao e o do passo 0 ({cfg['passo0']})")
    if erros:
        raise ValueError(f"a calibracao segue o plano a letra: {erros}")
    return "calibracao"


def config_bancada(cfg: dict, corpo: dict, bracos: list[str], mundos: list[str], lobos: dict | None = None) -> dict:
    out = {"bracos": list(bracos), "donos": list(cfg["donos"]), "unidades": dict(cfg["unidades"]), "mundos": list(mundos),
           "dias": cfg["dias"], "orcamento": cfg["orcamento"], "ponto": cfg["ponto"], "montagem": cfg["montagem"],
           "lobos": {**cfg["lobos"], **(lobos or {})}, "consequencia": dict(cfg["consequencia"]), "sonda": dict(cfg["sonda"]),
           "bootstrap": dict(cfg["bootstrap"]), "corpo": dict(corpo)}
    if cfg.get("plano"):
        out["plano"] = cfg["plano"]
    return bv.validar_config(out)


def pesos_com_novos(pesos: tuple, w: int) -> tuple:
    """A pesos_drives_corpo com os drives novos (NOVOS_W) em w e os outros como estao (6.1, w_novos)."""
    return tuple((nome, w if nome in NOVOS_W else peso) for nome, peso in pesos)


_BANCADAS: dict = {}


def bancada(cfg: dict, corpo: dict, w_novos: int = 1, lobos: dict | None = None) -> bv.Bancada:
    chave = json.dumps([cfg, corpo, w_novos, lobos], sort_keys=True)
    if chave not in _BANCADAS:
        b = bv.bancada_da_config(config_bancada(cfg, corpo, ["P0-c"], list(cfg["mundos"]), lobos))
        if w_novos != 1:
            b = replace(b, cfg_consequencia=replace(b.cfg_consequencia,
                                                    pesos_drives_corpo=pesos_com_novos(b.cfg_consequencia.pesos_drives_corpo, w_novos)))
        _BANCADAS[chave] = b
    return _BANCADAS[chave]


# ================================================================== as vidas
def _guardar(b: bv.Bancada, v: bv.VidaBancada, dir_vidas: Path) -> None:
    """Grava o log e o estado interno e confere o replay a partir do texto do disco (G1)."""
    caminho = dir_vidas / f"{v.nome}.jsonl"
    bv._gravar(caminho, v.motor.log.para_jsonl())
    bv._gravar(dir_vidas / f"{v.nome}.politica.json", bv._interno(v.motor))
    b.conferir_replay(v, caminho.read_text(encoding="utf-8"))


def compacta(med: dict, unidade: dict, rotulo_ponto: str, tempo: dict, cerebro_teto: int | None) -> dict:
    """O registro de uma vida que a analise le: a BE e o cuidado (toda vida), os drives novos com as contagens, o tedio medio, o
    metabolismo, as parcelas dos novos (so na grade), os efeitos do tapa e o custo."""
    corpo = med.get("corpo") or {}
    dn = (corpo.get("drives_novos") or {})
    jan = dn.get("janela") if dn.get("disponivel") else None
    drives = None
    if jan is not None:
        drives = {"n_acordado": jan["n_acordado"],
                  **{d: {"media": v["media"], "acima": None if v["fracao_acima"] is None else round(v["fracao_acima"] * jan["n_acordado"])}
                     for d, v in jan["drives"].items()}}
    comp = med["comportamento"]
    met = corpo.get("metabolismo")
    return {"vida": med["vida"], "braco": med["braco"], "dono": med["dono"], "mundo": med["mundo"], "semente": med["semente"],
            "genoma": med["genoma"], "base": unidade["base"], "k": unidade["k"], "ponto": rotulo_ponto, "origem": med["origem"],
            "filtro": med["filtro"], "be": comp["be"]["be"], "be_n": comp["be"]["n"], "por_acao": comp["be"]["por_acao"],
            "privacao": comp["cuidado"]["privacao"], "saude": comp["cuidado"]["saude_media"], "fome": comp["cuidado"]["fome_media"],
            "drives": drives,
            "metabolismo": None if met is None else {k: met[k] for k in ("acordado", "acordado_com_falta", "fracao", "disparos")},
            "novos_livres": (med.get("dominancia") or {}).get("novos_livres"),
            "dominancia": {"origem": med["dominancia"].get("origem"), "tempo_livre": med["dominancia"]["na_janela"]["tempo_livre"]},
            "tapa": corpo.get("tapa"), "gestos": corpo.get("gestos"), "interacoes": med["interacoes"],
            "pesos_no_teto": cerebro_teto, "tempo": tempo}


def _teto(v: bv.VidaBancada) -> int | None:
    cerebro = bv.do_braco(v.motor.politica).cerebro
    f = getattr(cerebro, "pesos_no_teto", None)
    return None if f is None or not getattr(cerebro, "_aprende", False) else f()


def _medir(b: bv.Bancada, v: bv.VidaBancada, sonda: dict, piso):
    c0, p0 = time.process_time(), time.perf_counter()
    med = b.medir(v, sonda, piso)
    return med, time.process_time() - c0, time.perf_counter() - p0


def _vida(b: bv.Bancada, espec: bv.EspecVida, dir_vidas: Path):
    c0, p0 = time.process_time(), time.perf_counter()
    v = b.vida(espec)
    _guardar(b, v, dir_vidas)
    return v, time.process_time() - c0, time.perf_counter() - p0


def _registrar(b, v, cv, pv, sonda, piso, unidade, rp, completas, compactas):
    """Mede e guarda a vida; a chave e o nome dela, com o ponto na frente fora da grade e do piloto (as sensibilidades repetem a vida
    com o mesmo nome e outro corpo ou cerebro: sem o ponto, uma sobrescreveria a outra)."""
    med, cm, pm = _medir(b, v, sonda, piso)
    med["unidade"] = {"base": unidade["base"], "k": unidade["k"]}
    chave = v.nome if rp == "piloto" or rp.startswith("sobe_") else f"{rp}|{v.nome}"
    if chave in completas:
        raise RuntimeError(f"vida repetida no registro: {chave}")
    completas[chave] = med
    compactas[chave] = compacta(med, unidade, rp, {"vida_cpu": cv, "vida_parede": pv, "medir_cpu": cm, "medir_parede": pm}, _teto(v))
    return med


def tarefa_grade(cfg: dict, ms: float, mr: float, msol: float, unidade: dict, pasta: str) -> tuple[dict, dict]:
    """As 8 celulas de uma unidade num ponto (m_sobe, m_reduz, m_sol): so o P0-c (6.2, PCD-4)."""
    b = bancada(cfg, corpo_do_ponto(cfg, ms, mr, msol))
    completas, compactas = {}, {}
    for mundo in cfg["mundos"]:
        for dono in cfg["donos"]:
            v, cv, pv = _vida(b, bv.EspecVida(dono, "P0-c", unidade["semente"], unidade["genoma"], mundo), Path(pasta) / "vidas")
            _registrar(b, v, cv, pv, cfg["sonda"], None, unidade, nome_ponto(ms, mr, msol), completas, compactas)
    return completas, compactas


def tarefa_piloto(cfg: dict, corpo: dict, w_novos: int, unidade: dict, pasta: str) -> tuple[dict, dict]:
    """O piloto de uma unidade no ponto (6.3): os blocos G-HOJE, corpo (com o P1-q^ac e o P1-c^ac do P0-q), tapa, G e P1-cw, e as
    sensibilidades (6.4, A1.2). O P0 de cada celula primeiro (o piso do acerto, como no `rodar` da bancada)."""
    b = bancada(cfg, corpo, w_novos)
    s, g = unidade["semente"], unidade["genoma"]
    completas, compactas = {}, {}

    def correr(bb, bracos, mundos, rp, piso_de=None):
        dv = Path(pasta) / ("vidas" if rp == "piloto" else f"{rp}/vidas")      # as sensibilidades em pastas proprias
        for mundo in mundos:
            for dono in cfg["donos"]:
                piso = None
                for braco in bracos:
                    v, cv, pv = _vida(bb, bv.EspecVida(dono, braco, s, g, mundo), dv)
                    med = _registrar(bb, v, cv, pv, cfg["sonda"], piso, unidade, rp, completas, compactas)
                    if braco == piso_de:
                        piso = med["acerto_total"]
                    if braco == "P0-q":
                        for destino in ACOPLADOS:
                            c0, p0 = time.process_time(), time.perf_counter()
                            va = bb.acoplar(v, destino, "nenhum")
                            _guardar(bb, va, dv)
                            _registrar(bb, va, time.process_time() - c0, time.perf_counter() - p0, cfg["sonda"], piso, unidade, rp,
                                       completas, compactas)
    correr(b, BLOCO_G_HOJE, cfg["mundos"], "piloto", "P0-hoje")
    correr(b, BLOCO_CORPO, cfg["mundos"], "piloto", "P0-q")
    correr(b, BLOCO_TAPA, ["bola"], "piloto", "P0-c-tapa")
    correr(b, BLOCO_G, ["iguais_frutas"], "piloto")
    correr(b, BLOCO_CW, cfg["mundos"], "piloto")
    for r in SENSIBILIDADE_TAPA:
        correr(bancada(cfg, corpo, w_novos, {"recompensa_tapa": r}), ("P1-c-tapa",), ["bola"], f"tapa_{rotulo(r)}")
    for j in SENSIBILIDADE_JANELA:
        correr(bancada(cfg, {**corpo, "janela_tedio": j}, w_novos), ("P0-c",), cfg["mundos"], f"janela_{j}")
    return completas, compactas


def _executar(tarefas: list[tuple], processos: int) -> list:
    if processos <= 1:
        return [f(*a) for f, a in tarefas]
    with ProcessPoolExecutor(max_workers=processos) as pool:
        futuros = [pool.submit(f, *a) for f, a in tarefas]
        return [fu.result() for fu in futuros]


# ================================================================== a regra da grade (funcoes puras)
def faixa_da_grade(registros: list[dict]) -> dict:
    """6.2, passo 1, num ponto: a fracao das decisoes acordado com a falta >= 0,75, por drive, nas vidas do P0-c dos dois mundos juntos
    (a soma das contagens sobre a soma das decisoes acordado)."""
    regs = [r for r in registros if r["braco"] == "P0-c" and r["origem"] is None]
    if not regs or any(r["drives"] is None for r in regs):
        raise ValueError("a faixa pede o P0-c com os drives novos em toda vida")
    n = sum(r["drives"]["n_acordado"] for r in regs)
    out = {"vidas": len(regs), "n_acordado": n}
    for d in ("tedio", "solidao", "estresse"):
        out[d] = sum(r["drives"][d]["acima"] for r in regs) / n
        out[f"{d}_media"] = sum(r["drives"][d]["media"] for r in regs) / len(regs)
    lo, hi = FAIXA_TEDIO_SOLIDAO
    out["passa"] = lo <= out["tedio"] <= hi and lo <= out["solidao"] <= hi and out["estresse"] <= TETO_ESTRESSE
    return out


def escolha_da_grade(faixas: dict) -> dict:
    """6.2, passo 2: dos pontos que passam, o mais perto de (1, 1) pela soma de |log2|; empate, o menor m_sobe (e depois o menor
    m_reduz, registro). Sem nenhum: a menor distancia das fracoes ao centro das faixas (|f - 0,30| no tedio e na solidao, |f - 0,10| no
    estresse, somadas), "nao fechou". `faixas` = {(m_sobe, m_reduz): faixa_da_grade} ou, com o m_sol (A5.2), {(m_sobe, m_reduz, m_sol):
    ...}: o mais perto de (1, 1, 1), e no empate o menor m_sobe, depois o menor m_sol, depois o menor m_reduz."""
    if len({len(p) for p in faixas}) != 1 or len(next(iter(faixas))) not in (2, 3):
        raise ValueError(f"pontos da grade: todos (m_sobe, m_reduz) ou todos (m_sobe, m_reduz, m_sol): {sorted(faixas)}")
    dist = lambda p: sum(abs(math.log2(m)) for m in p)  # noqa: E731
    desempate = lambda q: (q[0], q[2], q[1]) if len(q) == 3 else (q[0], q[1])  # noqa: E731
    passam = [p for p, f in faixas.items() if f["passa"]]
    if passam:
        p = min(passam, key=lambda q: (dist(q), *desempate(q)))
        return {"ponto": list(p), "fechou": True, "passam": [list(q) for q in sorted(passam)]}
    centro = (FAIXA_TEDIO_SOLIDAO[0] + FAIXA_TEDIO_SOLIDAO[1]) / 2
    afast = lambda q: abs(faixas[q]["tedio"] - centro) + abs(faixas[q]["solidao"] - centro) + abs(faixas[q]["estresse"] - TETO_ESTRESSE / 2)  # noqa: E731,E501
    p = min(faixas, key=lambda q: (afast(q), dist(q), *desempate(q)))
    return {"ponto": list(p), "fechou": False, "passam": [], "registro": "nao fechou", "distancia_ao_centro": afast(p)}


def mediana(xs: list[float]) -> float | None:
    if not xs:
        return None
    o = sorted(xs)
    m = len(o) // 2
    return o[m] if len(o) % 2 else (o[m - 1] + o[m]) / 2


def escolha_w(registros: list[dict]) -> dict:
    """6.2, passo 3: nas decisoes de tempo livre com sinal das vidas do P0-c no ponto (a sonda; o P0 nao aprende), a parcela dos drives
    novos em |D_antes - D_depois| com os novos pesados por w: w * A / (w * A + B), A e B as somas |c_d| dos novos e dos outros com w = 1
    (a parcela do adendo 2, com o valor absoluto). O menor w de {1, 2, 4} com a mediana em [0,25; 0,75]; sem nenhum, o de mediana mais
    perto de 0,5, "nao fechou"."""
    pares = [tuple(x) for r in registros if r["braco"] == "P0-c" and r["origem"] is None for x in (r["novos_livres"] or [])]
    if not pares:
        raise ValueError("o w_novos pede decisoes de tempo livre com sinal no P0-c")
    medianas = {w: mediana([w * a / (w * a + b) for a, b in pares if w * a + b > 0]) for w in GRADE_W}
    lo, hi = FAIXA_PARCELA
    passam = [w for w in GRADE_W if medianas[w] is not None and lo <= medianas[w] <= hi]
    if passam:
        return {"w_novos": passam[0], "fechou": True, "medianas": {str(w): m for w, m in medianas.items()}, "decisoes": len(pares)}
    w = min(GRADE_W, key=lambda x: (abs(medianas[x] - 0.5), x))
    return {"w_novos": w, "fechou": False, "registro": "nao fechou", "medianas": {str(x): m for x, m in medianas.items()},
            "decisoes": len(pares)}


# ================================================================== as margens, o N e o poder (secao 7)
def por_unidade(registros: list[dict], braco_a: str, braco_b: str, medida, mundos: tuple, ponto: str = "piloto") -> dict:
    """{semente: a media nas celulas (dono x mundo) de (a - b)}; `medida` e uma chave do registro ou uma funcao dele. Falta de celula
    ou valor None falha alto: o pareamento e por unidade e celula (secao 4)."""
    pega = medida if callable(medida) else (lambda r: r[medida])
    idx = {}
    for r in registros:
        if r["ponto"] != ponto or r["braco"] not in (braco_a, braco_b) or r["mundo"] not in mundos:
            continue
        chave = (r["semente"], r["dono"], r["mundo"], r["braco"])
        if chave in idx:
            raise RuntimeError(f"vida repetida: {chave}")
        idx[chave] = pega(r)
    out = {}
    for s in sorted({k[0] for k in idx}):
        ds = []
        for mundo in mundos:
            for dono in sorted({k[1] for k in idx}):
                a, b = idx.get((s, dono, mundo, braco_a)), idx.get((s, dono, mundo, braco_b))
                if a is None or b is None:
                    raise RuntimeError(f"unidade {s}, celula {dono}/{mundo}: falta {braco_a} ou {braco_b}")
                ds.append(a - b)
        out[s] = sum(ds) / len(ds)
    return out


def media_braco(registros: list[dict], braco: str, medida, mundos: tuple, ponto: str = "piloto") -> float:
    """A media sobre as unidades da media nas celulas, num braco."""
    pega = medida if callable(medida) else (lambda r: r[medida])
    por = {}
    for r in registros:
        if r["ponto"] == ponto and r["braco"] == braco and r["mundo"] in mundos:
            por.setdefault(r["semente"], []).append(pega(r))
    if not por:
        raise RuntimeError(f"sem vidas do {braco} em {mundos}")
    vals = [sum(v) / len(v) for v in por.values()]
    return sum(vals) / len(vals)


def tedio(r: dict) -> float:
    return r["drives"]["tedio"]["media"]


def margens(regs: list[dict]) -> dict:
    """Secao 7, a regra registrada: Delta_BE = 1/2 |BE(P0-q) - BE(P1-q)| no bola; Delta_priv = 1/4 da privacao media do P0-q e
    Delta_saude = 1/4 de (1 - saude media do P0-q), no bola (o mundo do G-CUIDADO); Delta_TED = 1/2 do tedio medio do P0-c no bola (o
    mundo do G-TED); as do G-HOJE (b), a metade das do efeito e do cuidado."""
    difs = por_unidade(regs, "P0-q", "P1-q", "be", ("bola",))
    d_be = 0.5 * abs(sum(difs.values()) / len(difs))
    priv = media_braco(regs, "P0-q", "privacao", ("bola",))
    saude = media_braco(regs, "P0-q", "saude", ("bola",))
    ted = media_braco(regs, "P0-c", tedio, ("bola",))
    return {"delta_be": d_be, "delta_priv": 0.25 * priv, "delta_saude": 0.25 * (1.0 - saude), "delta_ted": 0.5 * ted,
            "g_hoje": {"be": d_be / 2, "privacao": 0.25 * priv / 2, "saude": 0.25 * (1.0 - saude) / 2},
            "referencias": {"privacao_p0q": priv, "saude_p0q": saude, "tedio_p0c": ted}}


def _t_p(m: float, var: float, n: int, alvo: float) -> float:
    """p unilateral de H0: media >= alvo contra media < alvo (o teste t), com var = variancia amostral; var 0: 0 ou 1."""
    if var == 0.0:
        return 0.0 if m < alvo else 1.0
    return em.t_unilateral((alvo - m) / math.sqrt(var / n), n - 1)


def poder_conjunto(colunas: list[list[float]], n: int, replicas: int, semente: int, rotulo_rng: str, decide) -> float | None:
    """O bootstrap das unidades com os contrastes juntos (a mesma unidade em todos), centrados em 0: cada replica sorteia n unidades e
    `decide(medias, variancias, n)` diz se a replica passa. Para a nao inferioridade e a equivalencia (secao 7)."""
    k = len(colunas[0])
    if k < 2 or n < 2 or any(len(c) != k for c in colunas):
        return None
    cent = [[x - sum(c) / k for x in c] for c in colunas]
    rng = random.Random(derivar_semente(rotulo_rng, semente))
    ok = 0
    for _ in range(replicas):
        idx = [rng.randrange(k) for _ in range(n)]
        ms, vs = [], []
        for c in cent:
            ys = [c[i] for i in idx]
            m = sum(ys) / n
            ms.append(m)
            vs.append(sum((y - m) ** 2 for y in ys) / (n - 1))
        ok += decide(ms, vs, n)
    return ok / replicas


def nao_inferior(margens_: list[float]):
    """G-CUIDADO: todas com o limite superior do IC95 < a margem (o teste t unilateral a 2,5% contra media >= margem)."""
    return lambda ms, vs, n: all(_t_p(m, v, n, mg) <= ALFA_NAO_INFERIOR for m, v, mg in zip(ms, vs, margens_))


def equivalente(margens_: list[float]):
    """G-HOJE (b): todas com o IC90 dentro de +- a margem (os dois testes unilaterais a 5%)."""
    return lambda ms, vs, n: all(_t_p(m, v, n, mg) <= ALFA_EQUIVALENCIA and _t_p(-m, v, n, mg) <= ALFA_EQUIVALENCIA
                                 for m, v, mg in zip(ms, vs, margens_))


def tabela_k(poder_de, poder: dict, n_bases: int) -> dict:
    """O menor K de k_min a k_max por base com poder >= alvo; sem chegar, K = k_max, com o poder declarado (subpotenciado)."""
    tabela = []
    for k in range(poder["k_min"], poder["k_max"] + 1):
        tabela.append({"k": k, "n": n_bases * k, "poder": poder_de(n_bases * k)})
    chega = [t for t in tabela if t["poder"] is not None and t["poder"] >= poder["alvo"]]
    escolhido = chega[0] if chega else tabela[-1]
    return {"k": escolhido["k"], "n": escolhido["n"], "poder": escolhido["poder"], "chega_ao_alvo": bool(chega), "tabela": tabela}


def gates_do_n(regs: list[dict], mg: dict, poder: dict, semente: int, n_bases: int) -> dict:
    """Secao 7: o K de cada gate pelo poder simulado sobre as diferencas por unidade do piloto. Os efeitos (PR-1, PR-3, PR-4, PR-5) com as
    diferencas centradas e deslocadas para a margem (o em.poder_simulado, unilateral a 2,5%: o limite inferior do IC95 > 0; o Holm dos
    secundarios nao entra na simulacao, registro); a nao inferioridade (PR-2) e as equivalencias (G-HOJE (b)) centradas em 0, com os
    contrastes juntos."""
    R = poder["replicas"]
    ef = {
        "G-PARADO (PR-1)": (por_unidade(regs, "P1-c", "P1-q", "be", ("bola",)), mg["delta_be"]),
        "G-SEP (PR-3)": (por_unidade(regs, ROT_AC["P1-c"], ROT_AC["P1-q"], "be", ("bola",)), mg["delta_be"]),
        "G-PADRAO (PR-4)": (por_unidade(regs, "P1-c", "P1-q", "be", ("padrao",)), mg["delta_be"]),
        "G-TED (PR-5)": (por_unidade(regs, "P0-c", "P1-c", tedio, ("bola",)), mg["delta_ted"]),
    }
    out = {}
    for nome, (difs, delta) in ef.items():
        d = list(difs.values())
        out[nome] = {"margem": delta, "media_piloto": sum(d) / len(d), "dp_piloto": _dp(d),
                     **tabela_k(lambda n, d=d, delta=delta: em.poder_simulado(d, delta, n, ALFA_EFEITO, R, semente), poder, n_bases)}
    priv = list(por_unidade(regs, "P1-c", "P1-q", "privacao", ("bola",)).values())
    sau = list(por_unidade(regs, "P1-q", "P1-c", "saude", ("bola",)).values())
    out["G-CUIDADO (PR-2)"] = {"margens": [mg["delta_priv"], mg["delta_saude"]], "media_piloto": [sum(priv) / len(priv), sum(sau) / len(sau)],
                               **tabela_k(lambda n: poder_conjunto([priv, sau], n, R, semente, "corpo-poder-cuidado",
                                                                   nao_inferior([mg["delta_priv"], mg["delta_saude"]])), poder, n_bases)}
    cols, margs, nomes = [], [], []
    for p0, p1 in (("P0-quimica", "P0-hoje"), ("P1-quimica", "P1-hoje"), ("P3-quimica", "P3-hoje")):
        for medida, chave in (("be", "be"), ("privacao", "privacao"), ("saude", "saude")):
            cols.append(list(por_unidade(regs, p0, p1, medida, MUNDOS).values()))
            margs.append(mg["g_hoje"][chave])
            nomes.append(f"{p0} - {p1} em {medida}")
    out["G-HOJE (b)"] = {"contrastes": nomes, "margens": margs, "media_piloto": [sum(c) / len(c) for c in cols],
                         **tabela_k(lambda n: poder_conjunto(cols, n, R, semente, "corpo-poder-hoje", equivalente(margs)), poder, n_bases)}
    ks = [g["k"] for g in out.values()]
    sub = [nome for nome, g in out.items() if not g["chega_ao_alvo"]]
    k = max(ks)
    return {"gates": out, "k": k, "n": n_bases * k, "subpotenciados": sub,
            "regra": "o maior K entre os gates (secao 7); um gate que nem em K = 10 chega a 0,8 sai subpotenciado, com o poder",
            "alfas": {"efeito": ALFA_EFEITO, "nao_inferior": ALFA_NAO_INFERIOR, "equivalencia": ALFA_EQUIVALENCIA}}


def _dp(xs: list[float]) -> float | None:
    if len(xs) < 2:
        return None
    m = sum(xs) / len(xs)
    return (sum((x - m) ** 2 for x in xs) / (len(xs) - 1)) ** 0.5


def descritivo(regs: list[dict], boot: dict) -> dict:
    """Os contrastes do piloto, SO como relato (6.3: nao sao evidencia)."""
    out = {}
    for nome, a, b, medida, mundos in (("P1-c - P1-q em BE (bola)", "P1-c", "P1-q", "be", ("bola",)),
                                       ("P1-c - P1-q em BE (padrao)", "P1-c", "P1-q", "be", ("padrao",)),
                                       ("P1-c^ac - P1-q^ac em BE (bola)", ROT_AC["P1-c"], ROT_AC["P1-q"], "be", ("bola",)),
                                       ("P1-c - P1-q em privacao (bola)", "P1-c", "P1-q", "privacao", ("bola",)),
                                       ("P1-q - P1-c em saude (bola)", "P1-q", "P1-c", "saude", ("bola",)),
                                       ("P0-c - P1-c no tedio (bola)", "P0-c", "P1-c", tedio, ("bola",)),
                                       ("P1-cw - P1-c em BE (bola)", "P1-cw", "P1-c", "be", ("bola",))):
        difs = por_unidade(regs, a, b, medida, mundos)
        r = contraste_pareado({s: [d] for s, d in difs.items()}, boot["reamostragens"], boot["semente"])
        out[nome] = {"media": r["media"], "dp_unidades": _dp(list(difs.values())), "ic95": r["ic95"], "n": r["n"]}
    medias = {}
    for braco in sorted({r["braco"] for r in regs if r["ponto"] == "piloto"}):
        rs = [r for r in regs if r["ponto"] == "piloto" and r["braco"] == braco]
        medias[braco] = {"vidas": len(rs), "be": _m([r["be"] for r in rs]), "privacao": _m([r["privacao"] for r in rs]),
                         "saude": _m([r["saude"] for r in rs]), "fome": _m([r["fome"] for r in rs]),
                         "tedio": _m([tedio(r) for r in rs if r["drives"]]),
                         "falta_combustivel": _m([r["metabolismo"]["fracao"] for r in rs if r["metabolismo"]]),
                         "pesos_no_teto": _m([r["pesos_no_teto"] for r in rs if r["pesos_no_teto"] is not None]),
                         "vidas_com_peso_no_teto": sum(1 for r in rs if r["pesos_no_teto"])}
    out["por_braco"] = medias
    return out


def _m(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def sensibilidades(regs: list[dict]) -> dict:
    """6.4 e A1.2, so relato: o P1-c-tapa com o recompensa_tapa em -0,5, -1,0 (o piloto) e -2,0 (os efeitos do tapa da 5.4 e as vidas
    com peso no teto); o P0-c com a janela do tedio em 4, 8 (o piloto) e 16 (a fracao das decisoes acordado com o tedio >= 0,75)."""
    tapa = {}
    for rotulo_ponto, valor in (("tapa_-0.5", -0.5), ("piloto", -1.0), ("tapa_-2", -2.0)):
        rs = [r for r in regs if r["ponto"] == rotulo_ponto and r["braco"] == "P1-c-tapa"]
        tapa[rotulo(valor)] = {"vidas": len(rs),
                               "vidas_com_peso_no_teto": sum(1 for r in rs if r["pesos_no_teto"]),
                               "pesos_no_teto_medio": _m([r["pesos_no_teto"] for r in rs]),
                               "tapas_janela_medio": _m([r["tapa"]["tapas"] for r in rs]),
                               "reducao_solidao": {g: _m([r["tapa"]["medo_da_mao"][g]["reducao_solidao"] for r in rs])
                                                   for g in ("depois_tapa", "sem_tapa")},
                               "chamar_atencao": {g: _m([r["tapa"]["chamar_atencao"][g]["fracao"] for r in rs])
                                                  for g in ("depois_tapa", "sem_tapa")},
                               "carinho_sinal": {g: _m([r["tapa"]["carinho_sinal"][g] for r in rs]) for g in ("depois_tapa", "sem_tapa")},
                               "estresse_acima": _m([r["tapa"]["estresse_acima"]["fracao"] for r in rs]),
                               "be": _m([r["be"] for r in rs])}
    janela = {}
    for rotulo_ponto, j in (("janela_4", 4), ("piloto", 8), ("janela_16", 16)):
        rs = [r for r in regs if r["ponto"] == rotulo_ponto and r["braco"] == "P0-c" and r["origem"] is None]
        n = sum(r["drives"]["n_acordado"] for r in rs)
        janela[str(j)] = {"vidas": len(rs), "tedio_acima": sum(r["drives"]["tedio"]["acima"] for r in rs) / n if n else None,
                          "tedio_medio": _m([tedio(r) for r in rs])}
    return {"recompensa_tapa": tapa, "janela_tedio": janela,
            "nota": "so relato (6.4, A1.2): nada e escolhido por elas; o recompensa_tapa fica no valor da bronca (PCD-6)"}


def custo(registros: list[dict], k: int | None, n_bases: int, processos: int) -> dict:
    """O custo medido por vida e braco (CPU e parede; a vida com a gravacao e o replay do disco, e a medicao) e a estimativa da validacao
    no K escolhido, com os 120 por unidade (104 + 8 do bloco G + 8 do P1-cw), pelo custo medio das vidas do piloto."""
    por = {}
    for r in registros:
        c = por.setdefault(f"{r['ponto']}|{r['braco']}", {"vidas": 0, "cpu_s": 0.0, "parede_s": 0.0})
        t = r["tempo"]
        c["vidas"] += 1
        c["cpu_s"] += t["vida_cpu"] + t["medir_cpu"]
        c["parede_s"] += t["vida_parede"] + t["medir_parede"]
    for c in por.values():
        c["cpu_s_por_vida"] = c["cpu_s"] / c["vidas"]
    out = {"por_ponto_e_braco": por, "cpu_s_total": sum(c["cpu_s"] for c in por.values())}
    piloto = [r for r in registros if r["ponto"] == "piloto"]
    if k is not None and piloto:
        cpu_vida = sum(r["tempo"]["vida_cpu"] + r["tempo"]["medir_cpu"] for r in piloto) / len(piloto)
        n = n_bases * k
        vidas = n * VIDAS_POR_UNIDADE_VALIDACAO
        out["validacao_estimada"] = {"k": k, "n": n, "vidas": vidas, "cpu_s_por_vida": cpu_vida, "cpu_h": vidas * cpu_vida / 3600,
                                     "parede_h_em_processos": {"processos": processos, "h": vidas * cpu_vida / 3600 / processos}}
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
        raise FileExistsError(f"{pasta} ja existe: a run se recusa a gravar por cima (secao 11)")
    unidades = bv.unidades_derivadas(cfg["unidades"]["bases"], int(cfg["unidades"]["k"]), PREFIXO)
    pontos = pontos_da_grade(cfg)
    for p in pontos:                                        # toda config de ponto valida antes da primeira vida
        config_bancada(cfg, corpo_do_ponto(cfg, *p), ["P0-c"], list(cfg["mundos"]))
    pasta.mkdir(parents=True)
    inicio = time.time()
    meta = {"modo": modo, "plano": PLANO, "plano_sha256": _sha_arquivo(RAIZ / PLANO), "config": cfg,
            "config_arquivo": None if caminho_config is None else _relativo(caminho_config),
            "config_sha256": None if caminho_config is None else _sha_arquivo(caminho_config),
            "orquestrador_sha256": _sha_arquivo(Path(__file__)), "git_head": _git("rev-parse", "HEAD"),
            "git_limpo": _git("status", "--porcelain") == "", "processos": processos, "unidades": unidades,
            "passo0": cfg["passo0"], "passo0_sha256": _sha_arquivo(RAIZ / cfg["passo0"]) if (RAIZ / cfg["passo0"]).exists() else None,
            "corpo_dos_pontos": {nome_ponto(*p): corpo_do_ponto(cfg, *p) for p in pontos},
            "bancada": bv.meta(config_bancada(cfg, corpo_do_ponto(cfg, 1.0, 1.0), ["P0-c"], list(cfg["mundos"]))),
            "saida": _relativo(pasta),
            "inicio": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(inicio))}
    meta["sha256"] = {"corpo.py": meta["bancada"]["corpo_sha256"], "config.py": meta["bancada"]["config_sha256"],
                      "lobos.py": meta["bancada"]["lobos_sha256"], "engine.py": meta["bancada"]["engine_sha256"],
                      "plano": meta["plano_sha256"], "config": meta["config_sha256"]}
    bv._gravar(pasta / "meta.json", bv._dump(meta))

    # ---- a grade (6.1), so o P0-c
    tarefas = [(tarefa_grade, (cfg, *p, u, str(pasta / "grade" / nome_ponto(*p)))) for p in pontos for u in unidades]
    t0 = time.perf_counter()
    saidas = _executar(tarefas, processos)
    meta["grade_parede_s"] = time.perf_counter() - t0
    grade = {nome_ponto(*p): {} for p in pontos}
    completas = {nome_ponto(*p): {} for p in pontos}
    for (_, (_, ms, mr, msol, _, _)), (comp, compa) in zip(tarefas, saidas):
        completas[nome_ponto(ms, mr, msol)].update(comp)
        grade[nome_ponto(ms, mr, msol)].update(compa)
    for nome, comp in completas.items():
        bv._gravar(pasta / "grade" / nome / "medidas.json", bv._dump(dict(sorted(comp.items()))))
    com_sol = "m_solidao" in cfg["grade"]                   # A5.2: os pontos com o terceiro eixo
    chave = (lambda p: p) if com_sol else (lambda p: p[:2])  # noqa: E731
    faixas = {chave(p): faixa_da_grade(list(grade[nome_ponto(*p)].values())) for p in pontos}
    esc = escolha_da_grade(faixas)
    p = tuple(esc["ponto"]) + (() if com_sol else (1.0,))
    w = escolha_w(list(grade[nome_ponto(*p)].values()))
    corpo = corpo_do_ponto(cfg, *p)
    resultado = {"modo": modo, "plano": PLANO,
                 "faixas": {nome_ponto(*q): f for q, f in faixas.items()},
                 "regra_passo2": ("dos que passam, o mais perto de (1, 1, 1) pela soma de |log2|; empate, o menor m_sobe, depois o menor "
                                  "m_sol, depois o menor m_reduz (A5.2)") if com_sol else
                                 "dos que passam, o mais perto de (1, 1) pela soma de |log2|; empate, o menor m_sobe (6.2)",
                 "escolha": {**esc, "nome": nome_ponto(*p), "corpo": corpo}, "w_novos": w}

    # ---- o piloto (6.3) e as sensibilidades (6.4, A1.2), no ponto
    tarefas = [(tarefa_piloto, (cfg, corpo, w["w_novos"], u, str(pasta / "piloto"))) for u in unidades]
    t0 = time.perf_counter()
    saidas = _executar(tarefas, processos)
    meta["piloto_parede_s"] = time.perf_counter() - t0
    comp_piloto, piloto = {}, {}
    for comp, compa in saidas:
        comp_piloto.update(comp)
        piloto.update(compa)
    bv._gravar(pasta / "piloto" / "medidas.json", bv._dump(dict(sorted(comp_piloto.items()))))
    regs = list(piloto.values())

    # ---- G-P0C (mecanismo): o P0-c e o P0-q decidem igual em toda celula do piloto
    acoes_q = {(r["semente"], r["dono"], r["mundo"]): r["por_acao"] for r in regs if r["ponto"] == "piloto" and r["braco"] == "P0-q"}
    acoes_c = {(r["semente"], r["dono"], r["mundo"]): r["por_acao"] for r in regs if r["ponto"] == "piloto" and r["braco"] == "P0-c"}
    resultado["g_p0c"] = {"celulas": len(acoes_q), "iguais": sum(acoes_q[k] == acoes_c.get(k) for k in acoes_q),
                          "passa": acoes_q == acoes_c and bool(acoes_q),
                          "nota": "a decisao a decisao (o log) e conferida nos testes da bancada (G-P0C); aqui, as acoes da BE por celula"}
    if not resultado["g_p0c"]["passa"]:
        raise RuntimeError("G-P0C: o P0-c nao decide como o P0-q no piloto (o corpo vazou para o instinto)")

    mg = margens(regs)
    n_bases = len(cfg["unidades"]["bases"])
    n = gates_do_n(regs, mg, cfg["poder"], cfg["bootstrap"]["semente"], n_bases)
    resultado.update({"margens": mg, "n": n, "piloto_descritivo": descritivo(regs, cfg["bootstrap"]),
                      "sensibilidades": sensibilidades(regs),
                      "custo": custo([r for g in grade.values() for r in g.values()] + regs, n["k"], n_bases, processos)})
    return _fechar(pasta, meta, {"grade": grade, "piloto": piloto}, resultado, inicio)


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
        raise SystemExit("a fumaca precisa de --saida (fora de artifacts_v2_corpo/calibracao)")
    r = rodar(cfg, saida, a.processos, caminho)["resultado"]
    print(json.dumps({"escolha": r["escolha"], "w_novos": r["w_novos"], "margens": r["margens"],
                      "n": {k: r["n"][k] for k in ("k", "n", "subpotenciados")}}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
