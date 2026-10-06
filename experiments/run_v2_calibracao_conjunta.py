"""V2, K2: a calibracao conjunta do cerebro A (docs/TAREFA_V2_K2_CALIBRACAO_CONJUNTA.md; plano docs/PLANO_CALIBRACAO_CONJUNTA_V2.md, decisoes
K-1 a K-11). Pela bancada (experiments/bancada_v2.py), nas unidades derivadas das bases 14101...14505 (K = 4) ou, na fumaca, nas sementes
dos testes. As validacoes (15101...15505) nunca: o modo vem das sementes e recusa o resto.

Etapas (secao 3 do plano), cada uma com a regra de escolha registrada e a de reserva:
    A1  g (ganho da memoria)       MR, descasado, aprendizado desligado    menor g com IC95 inferior da fracao decidida pela memoria > 0,069
    A2  w0_pedido                  P0+ped, iguais_frutas (+ P0 de referencia)  menor w0 com IC95 inferior da deferencia na fome_moderada > 0
    B   ganho do P1                P1 completo, as tres condicoes           sem vida no teto, menor razao da deriva (dia 14 / dia 7); empate, menor
    C   w0_info                    P2 completo, descasado, dias 1-7         menor w0 com IC95 inferior da fracao decidida pela informacao > 0,069
    D   piloto no ponto escolhido  os 44 por unidade da secao 4             delta, deltas dos blocos, sigma2_d, N da validacao (secao 5.3)

Nenhuma regra le a taxa_fruta_ruim nem um contraste entre bracos (tarefa, secao 2). Toda vida e rejogada do disco bit a bit (a bancada).

    python experiments/run_v2_calibracao_conjunta.py --config experiments/configs/v2_calibracao_conjunta/calibracao.json
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
from statistics import NormalDist

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v2_experimento_maior as em  # noqa: E402
from digilab.ambiente import reproduzir_ambiente  # noqa: E402
from digilab.config import CONFIG_PADRAO, TICKS_POR_DIA  # noqa: E402
from digilab.events import LogDeEventos  # noqa: E402
from digilab.frutas import DonoPedinte  # noqa: E402
from digilab.metrics import bootstrap_ic, fracao_da_fruta, tamanho_amostra  # noqa: E402

PLANO = "docs/PLANO_CALIBRACAO_CONJUNTA_V2.md"
SAIDA_PADRAO = "artifacts_v2_calibracao_conjunta"
S = 1024
# secao 2 do plano: as grades PROPOSTAS (na calibracao, so estas; a fumaca pode trocar)
GRADES_PLANO = {"g": (S // 4, S // 2, 3 * S // 4), "w0_pedido": (S // 4, S // 2, 3 * S // 4), "ganho": (4, 8, 16),
                "w0_info": (S // 4, S // 2, 3 * S // 4)}
LIMIAR_DECIDIDA = 0.069          # A1 e C: a fracao de motivos que citavam memoria na v1 (artifacts_v1_memoria_espacos/espacos.json)
LIMIAR_DEFERENCIA = 0.0          # A2: G-ARB na fome_moderada (N7-4)
ZONA_A2 = "fome_moderada"
DIAS_C = 7                       # C: dias 1-7
K_CALIBRACAO = 4                 # K-9
DIAS_PLANO = 14
DONO = "atencioso"
CONDICOES = ("casado_frutas", "descasado", "mutavel")
TETO_HORAS_VALIDACAO = 12.0      # K-10
VIDAS_POR_UNIDADE = 44           # secao 4
ALFA, PODER = 0.05, 0.8
REPLICAS_PODER = 2000
CHAVES = {"descricao", "plano", "unidades", "sementes", "genomas", "dias", "orcamento", "sonda", "bootstrap", "grades", "canais",
          "etapas", "saida", "ponto", "ponto_fixo"}
ETAPAS = ("A1", "A2", "B", "C", "D")

# ------------------------------------------------------------------ os bracos do cerebro A montado (secao 1)
# Decisao do Matheus (2026-10-05, opcao 1; docs/TAREFA_V2_BANCADA_MONTAGEM.md): os bracos continuam P0 a P3, e a chave da bancada
# "montagem": "completa" liga em cada um as pecas da tabela da secao 1 (memoria com o g da config em P1-P3; canais em P1 e P2; w0_info so
# nos P2; w0_pedido onde ha pedido); o P0 fica com nada (K-1). As ablacoes da K-7 sao o P1c-mem (g = 0) e o P1c-can (escalar), o P1
# completo menos uma peca. A tabela abaixo fica para o caso de um braco completo ter outro nome.
MONTAGEM = "completa"
BRACO_COMPLETO = {"P0": "P0", "P1": "P1", "P2": "P2", "P2e": "P2e", "P2a": "P2a", "P3": "P3"}
ABLACAO = {"memoria": "P1c-mem", "canais": "P1c-can"}
FILTRO_SO_CUIDADO = "sem_ensino"


def _dump(obj) -> str:
    return json.dumps(obj, indent=1, sort_keys=True, ensure_ascii=False, default=repr) + "\n"


def _gravar(caminho: Path, texto: str) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(texto, encoding="utf-8", newline="\n")


# ------------------------------------------------------------------ config, modo e pecas


def modo_e_unidades(cfg: dict) -> tuple[str, list[dict]]:
    """fumaca (as sementes dos testes) ou calibracao (as bases 14101...14505, K = 4, 14 dias, as grades do plano). O resto falha alto,
    as sementes de validacao incluidas."""
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
        if set(u) - {"bases", "k"}:
            raise ValueError(f"unidades: so 'bases' e 'k' (o prefixo e o do experimento maior, K-9): {u}")
        bases = set(u["bases"])
        unidades = bv.unidades_derivadas(u["bases"], int(u["k"]))
    else:
        bases = set(cfg["sementes"]) | {g for g in cfg.get("genomas", []) if g is not None}
        unidades = [{"genoma": g, "semente": int(s), "base": None, "k": None} for g in cfg.get("genomas", [None]) for s in cfg["sementes"]]
    cal = set(bv.BASES_EXPERIMENTO_MAIOR["calibracao"])
    if bases <= bv.SEMENTES_TESTE:
        modo = "fumaca"
    elif bases == cal and "unidades" in cfg:
        modo = "calibracao"
    else:
        raise bv.SementeSemPlano(f"sementes {sorted(bases)}: so as dos testes (fumaca) ou exatamente as bases de calibracao {sorted(cal)}, "
                                 "derivadas (K2); a validacao 15101...15505 nunca")
    if modo == "calibracao":
        if cfg.get("plano") != PLANO or not (RAIZ / PLANO).is_file():
            raise bv.SementeSemPlano(f"calibracao: precisa do campo 'plano' = {PLANO!r}")
        if int(cfg["unidades"]["k"]) != K_CALIBRACAO:
            raise ValueError(f"calibracao: K = {K_CALIBRACAO} por base (K-9), nao {cfg['unidades']['k']}")
        if int(cfg["dias"]) != DIAS_PLANO:
            raise ValueError(f"calibracao: {DIAS_PLANO} dias, nao {cfg['dias']}")
        if "grades" in cfg and {k: tuple(v) for k, v in cfg["grades"].items()} != GRADES_PLANO:
            raise ValueError("calibracao: as grades sao as do plano (secao 2)")
        if cfg.get("etapas", list(ETAPAS)) != list(ETAPAS):
            raise ValueError("calibracao: as cinco etapas, na ordem do plano")
        if cfg.get("ponto", bv.PONTO_N5_EXPERIMENTO) != "T3":
            raise ValueError("calibracao: o ponto T3 (teto 16 S, R1)")
        if "ponto_fixo" in cfg:
            raise ValueError("calibracao: nada fixado de fora; cada parametro sai da sua etapa")
    return modo, unidades


def grades(cfg: dict) -> dict:
    g = {k: tuple(v) for k, v in cfg.get("grades", {}).items()}
    sobram = set(g) - set(GRADES_PLANO)
    if sobram:
        raise ValueError(f"grades desconhecidas: {sorted(sobram)}")
    return {**GRADES_PLANO, **g}


def pecas_pendentes(cfg: dict) -> list[str]:
    """O que a calibracao precisa da bancada e ainda nao esta na main (PR do chat D, BANCADA-K4-CANAIS). Vazio = pode rodar."""
    faltam = []
    if "montagem" not in bv.CHAVES_CONFIG:
        faltam.append("chave 'montagem' na bancada (BANCADA-MONTAGEM, chat D; opcao 1 de 2026-10-05)")
        if not em.K4_DONO_JULGA_FRUTA:
            faltam.append("K4 na bancada (K-11)")
        return faltam
    b = bv.bancada_da_config({"dias": 2, "orcamento": 8, "ponto": "T3", "lobos": {"memoria_ganho": S // 2}, "montagem": MONTAGEM})
    for logico in ("P1", "P2", "P2e", "P2a", "P3"):
        if BRACO_COMPLETO[logico] not in bv.BRACOS:
            faltam.append(f"braco completo {BRACO_COMPLETO[logico]} na bancada (K-1)")
            continue
        c = bv.do_braco(b.politica(bv.EspecVida(DONO, BRACO_COMPLETO[logico], 101, None, "descasado"))).cerebro
        if c._memoria is None:
            faltam.append(f"memoria no braco completo {BRACO_COMPLETO[logico]} (K-1)")
    if not em.K4_DONO_JULGA_FRUTA:
        faltam.append("K4 na bancada: o dono do P3 julga a fruta (K-11; BANCADA-K4-CANAIS, chat D)")
    if cfg.get("canais", True):
        cc = bv.bancada_da_config({"dias": 2, "orcamento": 8, "consequencia": {"canais_ligados": True}}).cfg_consequencia
        if not getattr(cc, "canais_ligados", False):
            faltam.append("canais na bancada (C4, #169)")
    return faltam


def config_bancada(cfg: dict, nome: str, bracos, mundos, lobos: dict, consequencia: dict | None = None,
                   acoplados=()) -> dict:
    cb = {"descricao": f"K2 {nome}: {cfg.get('descricao', '')}", "bracos": list(bracos), "mundos": list(mundos), "donos": [DONO],
          "dias": cfg["dias"], "orcamento": cfg["orcamento"], "sonda": cfg["sonda"], "bootstrap": cfg["bootstrap"],
          "ponto": cfg.get("ponto", bv.PONTO_N5_EXPERIMENTO), "lobos": dict(lobos), "acoplados": list(acoplados),
          "julgamento_fruta": em.K4_DONO_JULGA_FRUTA, "montagem": MONTAGEM}
    for k in ("plano", "unidades", "sementes", "genomas"):
        if k in cfg:
            cb[k] = cfg[k]
    if "unidades" in cfg:
        cb["plano"] = PLANO
    if consequencia:
        cb["consequencia"] = dict(consequencia)
    return cb


def rodar_bancada(cb: dict, pasta: Path) -> dict:
    t = time.perf_counter()
    r = bv.rodar(cb, pasta)
    r["segundos"] = time.perf_counter() - t
    return r


# ------------------------------------------------------------------ estatistica das regras


def ic(valores: list, boot: dict) -> dict:
    """IC 95% bootstrap sobre as unidades com valor (secao 3: "IC 95%" das regras); None sem 2 unidades com valor."""
    v = [x for x in valores if x is not None]
    if len(v) < 2:
        return {"media": v[0] if v else None, "ic_inferior": None, "ic_superior": None, "n": len(v), "sem_valor": len(valores) - len(v)}
    return {**bootstrap_ic(v, boot["reamostragens"], boot["semente"], boot["nivel"]), "sem_valor": len(valores) - len(v)}


def regra_menor_acima(pontos: dict, limiar: float) -> dict:
    """A regra das etapas A1, A2 e C: o MENOR valor da grade com o limite inferior do IC acima do limiar. Reserva (nenhum passa): o de
    maior limite inferior (empate: o menor valor); sem IC em nenhum ponto, o menor valor."""
    ordem = sorted(pontos)
    passam = [v for v in ordem if pontos[v]["ic"]["ic_inferior"] is not None and pontos[v]["ic"]["ic_inferior"] > limiar]
    if passam:
        return {"escolhido": passam[0], "fechou": True, "regra": f"menor valor com IC95 inferior > {limiar}", "passam": passam}
    lis = {v: pontos[v]["ic"]["ic_inferior"] for v in ordem}
    com = [v for v in ordem if lis[v] is not None]
    if not com:
        return {"escolhido": ordem[0], "fechou": False, "regra": "reserva: nenhum ponto com IC; o menor valor", "passam": []}
    melhor = max(com, key=lambda v: (lis[v], -v))
    return {"escolhido": melhor, "fechou": False, "regra": "reserva: o de maior limite inferior", "passam": []}


def regra_ganho(pontos: dict) -> dict:
    """Etapa B (secao 3.3): entre os ganhos sem nenhuma vida no teto, o de menor razao da deriva (media das tres condicoes); empate, o
    menor ganho. Reserva (todo ganho com vida no teto; o plano nao a escreve, REGISTRO_DESVIOS): o de menos vidas no teto, depois a
    menor razao, depois o menor ganho (a regra de reserva do N3)."""
    def razao(v):
        r = pontos[v]["razao_media"]
        return math.inf if r is None else r
    ordem = sorted(pontos)
    sem_teto = [v for v in ordem if pontos[v]["vidas_no_teto"] == 0]
    if sem_teto:
        return {"escolhido": min(sem_teto, key=lambda v: (razao(v), v)), "fechou": True,
                "regra": "sem vida no teto, menor razao da deriva; empate, menor ganho", "sem_teto": sem_teto}
    return {"escolhido": min(ordem, key=lambda v: (pontos[v]["vidas_no_teto"], razao(v), v)), "fechou": False,
            "regra": "reserva: menos vidas no teto, depois menor razao, depois menor ganho", "sem_teto": []}


# ------------------------------------------------------------------ medidas por vida


def _vidas_de(r: dict, braco: str) -> list:
    """(nome, vida, medidas) das vidas de malha fechada do braco."""
    return [(n, v, r["medidas"][n]) for n, v in sorted(r["vidas"].items()) if v.origem is None and v.espec.braco == braco]


def deferencia_zona(m: dict, zona: str = ZONA_A2) -> float | None:
    """A2: deferencia na zona, dias 1..dias_pedido (as janelas inicial e final do bloco N7, juntas: o G-ARB)."""
    por = m["n7"]["deferencia"]["por_janela"]
    conf = sum(por[j][zona]["conflitos"] for j in ("inicial", "final"))
    pelo = sum(por[j][zona]["pelo_pedido"] for j in ("inicial", "final"))
    return (pelo / conf) if conf else None


def razao_deriva(derivas: list[list[float]], dias: int) -> float | None:
    """A razao da deriva de uma celula: media da deriva no fim do dia `dias` / media no fim do dia `dias // 2` (G6 da L1 e do N3; a conta
    de run_revisao_aprendiz.celulas)."""
    meio = dias // 2 - 1
    d7 = sum(d[meio] for d in derivas) / len(derivas)
    d14 = sum(d[-1] for d in derivas) / len(derivas)
    return (d14 / d7) if d7 > 0 else None


class _SondaInfo:
    """Embrulho do braco no replay da etapa C: antes de cada sub-decisao da fruta pergunta ao cerebro a escolha sem o termo da
    informacao (PoliticaLobos.escolha_sem_info, so le) e guarda (decisao k, frutas, informacao vigente, escolha, escolha sem info)."""

    def __init__(self, interna) -> None:
        self.interna = interna
        self.k = -1
        self.registros: list[tuple[int, int, bool, str, str | None]] = []

    def agir(self, obs, rng):
        self.k += 1
        return self.interna.agir(obs, rng)

    def observar(self, transicao) -> None:
        self.interna.observar(transicao)

    def receber_acao_dono(self, acao, tick) -> None:
        self.interna.receber_acao_dono(acao, tick)

    def estado_interno(self) -> dict:
        return self.interna.estado_interno()

    def escolher_fruta(self, presentes, incentivos, u):
        sem, vigente = self.interna.cerebro.escolha_sem_info(presentes, incentivos, u)
        f = self.interna.escolher_fruta(presentes, incentivos, u)
        self.registros.append((self.k, len(presentes), vigente, f, sem))
        return f

    def __getattr__(self, nome):
        interna = self.__dict__.get("interna")
        if interna is None:
            raise AttributeError(nome)
        return getattr(interna, nome)


def fracao_decidida_pela_informacao(bancada: bv.Bancada, vida, dias_janela: int) -> dict:
    """C: rejoga a vida com a sonda, confere que a vida e o estado interno sao os mesmos (a sonda so le), e devolve, sobre as sub-decisoes
    com duas frutas ou mais e informacao vigente nos dias 1..dias_janela (a mesma regua da memoria, A1), quantas a informacao decidiu."""
    sondas = []

    def fab(cfg=None):
        s = _SondaInfo(bancada.politica(vida.espec, cfg))
        sondas.append(s)
        return s
    m = reproduzir_ambiente(LogDeEventos.de_jsonl(vida.motor.log.para_jsonl()), fab, semente=vida.espec.semente,
                            fabrica_motor=bancada.fabrica_motor(vida.espec))
    if bv.resumo_motor(m) != bv.resumo_motor(vida.motor) or bv._interno(m) != bv._interno(vida.motor):
        raise bv.ReplayDivergiu(f"{vida.nome}: a sonda da informacao mudou a vida")
    passo, fim = CONFIG_PADRAO.intervalo_decisao_ticks, dias_janela * TICKS_POR_DIA
    eleg = [r for r in sondas[0].registros if r[1] >= 2 and r[2] and r[0] * passo < fim]
    mudou = sum(1 for r in eleg if r[3] != r[4])
    return {"elegiveis": len(eleg), "decididas": mudou, "fracao": (mudou / len(eleg)) if eleg else None,
            "subdecisoes": len(sondas[0].registros)}


# ------------------------------------------------------------------ etapas A1, A2, B, C


def etapa_a1(cfg: dict, saida: Path, grade) -> dict:
    pontos = {}
    for g in grade:
        r = rodar_bancada(config_bancada(cfg, f"A1 g={g}", ["MR"], ["descasado"], {"memoria_ganho": g}), saida / "A1" / f"g{g}")
        vals = [m["n6"]["fracao_decidida"] for _, _, m in _vidas_de(r, "MR")]
        pontos[g] = {"valores": vals, "ic": ic(vals, cfg["bootstrap"]), "segundos": r["segundos"], "vidas": len(r["vidas"])}
    escolha = regra_menor_acima(pontos, LIMIAR_DECIDIDA)
    return {"etapa": "A1", "parametro": "memoria_ganho", "onde": "MR, descasado", "medida": "fracao decidida pela memoria (G-CITA)",
            "limiar": LIMIAR_DECIDIDA, "pontos": pontos, **escolha}


def etapa_a2(cfg: dict, saida: Path, grade) -> dict:
    pontos = {}
    for w in grade:
        r = rodar_bancada(config_bancada(cfg, f"A2 w0_pedido={w}", ["P0+ped"], ["iguais_frutas"], {"w0_pedido": w}),
                          saida / "A2" / f"w{w}")
        vals = [deferencia_zona(m) for _, _, m in _vidas_de(r, "P0+ped")]
        urg = sum(m["n7"]["deferencia"]["violacoes_urgentes"] for _, _, m in _vidas_de(r, "P0+ped"))
        pontos[w] = {"valores": vals, "ic": ic(vals, cfg["bootstrap"]), "violacoes_urgentes": urg, "segundos": r["segundos"],
                     "vidas": len(r["vidas"])}
    ref = rodar_bancada(config_bancada(cfg, "A2 referencia sem pedido", ["P0"], ["iguais_frutas"], {}), saida / "A2" / "referencia")
    escolha = regra_menor_acima(pontos, LIMIAR_DEFERENCIA)
    return {"etapa": "A2", "parametro": "w0_pedido", "onde": "P0+ped, iguais_frutas", "medida": f"deferencia na {ZONA_A2}, dias 1-10 (G-ARB)",
            "limiar": LIMIAR_DEFERENCIA, "pontos": pontos, "referencia": {"vidas": len(ref["vidas"]), "segundos": ref["segundos"]},
            **escolha}


def etapa_b(cfg: dict, saida: Path, grade, g: int, canais: bool) -> dict:
    pontos = {}
    for ganho in grade:
        r = rodar_bancada(config_bancada(cfg, f"B ganho={ganho}", [BRACO_COMPLETO["P1"]], CONDICOES, {"memoria_ganho": g},
                                         {"ganho": ganho, "canais_ligados": canais}), saida / "B" / f"ganho{ganho}")
        por = {}
        for mundo in CONDICOES:
            vs = [(n, v, m) for n, v, m in _vidas_de(r, BRACO_COMPLETO["P1"]) if v.espec.mundo == mundo]
            teto = [bv.do_braco(v.motor.politica).cerebro.pesos_no_teto() for _, v, _ in vs]
            derivas = [m["custo_da_plasticidade"]["deriva_por_dia"] for _, _, m in vs]
            por[mundo] = {"vidas": len(vs), "vidas_no_teto": sum(t > 0 for t in teto), "pesos_no_teto": teto,
                          "razao_deriva": razao_deriva(derivas, int(cfg["dias"]))}
        razoes = [por[c]["razao_deriva"] for c in CONDICOES]
        pontos[ganho] = {"por_condicao": por, "vidas_no_teto": sum(por[c]["vidas_no_teto"] for c in CONDICOES),
                         "razao_media": (sum(razoes) / len(razoes)) if None not in razoes else None,
                         "segundos": r["segundos"], "vidas": len(r["vidas"])}
    escolha = regra_ganho(pontos)
    return {"etapa": "B", "parametro": "ganho", "onde": "P1 completo, casado_frutas + descasado + mutavel",
            "medida": "vidas no teto; razao da deriva dia 14 / dia 7, media das tres condicoes", "pontos": pontos, **escolha}


def etapa_c(cfg: dict, saida: Path, grade, g: int, ganho: int, canais: bool) -> dict:
    pontos = {}
    dias_janela = min(DIAS_C, int(cfg["dias"]))
    for w in grade:
        cb = config_bancada(cfg, f"C w0_info={w}", [BRACO_COMPLETO["P2"]], ["descasado"], {"memoria_ganho": g, "w0_info": w},
                            {"ganho": ganho, "canais_ligados": canais})
        r = rodar_bancada(cb, saida / "C" / f"w{w}")
        bancada = bv.bancada_da_config(cb)
        sondas = {n: fracao_decidida_pela_informacao(bancada, v, dias_janela) for n, v, _ in _vidas_de(r, BRACO_COMPLETO["P2"])}
        vals = [s["fracao"] for s in sondas.values()]
        pontos[w] = {"valores": vals, "ic": ic(vals, cfg["bootstrap"]), "sondas": sondas, "segundos": r["segundos"],
                     "vidas": len(r["vidas"])}
    escolha = regra_menor_acima(pontos, LIMIAR_DECIDIDA)
    return {"etapa": "C", "parametro": "w0_info", "onde": f"P2 completo, descasado, dias 1-{dias_janela}",
            "medida": "fracao das sub-decisoes com duas frutas ou mais e informacao vigente decididas pela informacao (sonda)",
            "limiar": LIMIAR_DECIDIDA, "pontos": pontos, **escolha}


# ------------------------------------------------------------------ etapa D: o piloto e o adendo


def poder_formula(sigma: float, delta: float, n: int, alfa: float) -> float | None:
    """Poder unilateral da aproximacao normal: Phi(sqrt(n) delta / sigma - z_(1-alfa))."""
    if sigma is None or delta is None or delta <= 0 or n is None:
        return None
    if sigma == 0:
        return 1.0
    z = NormalDist()
    return z.cdf(math.sqrt(n) * delta / sigma - z.inv_cdf(1.0 - alfa))


# A conta do poder simulado mora no orquestrador do experimento maior desde a V1-VALIDACAO-UNICA (o adendo 2 tira o N dela); a mesma
# funcao, a mesma rng: a K2 reproduz.
poder_simulado = em.poder_simulado


def _logico(rotulo: str) -> str:
    """O rotulo da bancada no nome logico do plano (o inverso de BRACO_COMPLETO; os acoplados mantem o formato destino<origem:filtro)."""
    inv = {v: k for k, v in BRACO_COMPLETO.items()}
    if "<" in rotulo:
        destino, resto = rotulo.split("<", 1)
        origem, filtro = resto.split(":", 1)
        return f"{inv.get(destino, destino)}<{inv.get(origem, origem)}:{filtro}"
    return inv.get(rotulo, rotulo)


def indice_logico(*runs) -> dict:
    """(nome logico, mundo, unidade) -> medidas, de varias runs da bancada; repetido falha alto."""
    idx = {}
    for r in runs:
        for m in r["medidas"].values():
            if m["dono"] != DONO:
                continue
            chave = (_logico(m["braco"]), m["mundo"], (m["genoma"], m["semente"]))
            if chave in idx:
                raise ValueError(f"vida repetida no indice: {chave}")
            idx[chave] = m
    return idx


def _difs(idx, unidades, mundo, f, mais, menos) -> tuple[list[float], int]:
    out, falta = [], 0
    for u in unidades:
        ku = (u["genoma"], u["semente"])
        a, b = f(idx[(mais, mundo, ku)]), f(idx[(menos, mundo, ku)])
        if a is None or b is None:
            falta += 1
            continue
        out.append(a - b)
    return out, falta


def _sigma(vs: list[float]) -> float | None:
    if len(vs) < 2:
        return None
    m = sum(vs) / len(vs)
    return math.sqrt(sum((x - m) ** 2 for x in vs) / (len(vs) - 1))


def secundario(idx, unidades, nome, familia, mundo, f, mais, menos, delta, alfa_passo, n) -> dict:
    vs, falta = _difs(idx, unidades, mundo, f, mais, menos)
    sigma = _sigma(vs)
    pw = poder_formula(sigma, delta, n, alfa_passo)
    return {"nome": nome, "familia": familia, "mundo": mundo, "d": f"{mais} - {menos}", "media_piloto": (sum(vs) / len(vs)) if vs else None,
            "sigma_d": sigma, "n_unidades": len(vs), "sem_valor": falta, "delta": delta, "alfa": alfa_passo,
            "poder_com_n": pw, "subpotenciado": (pw is None or pw < 0.5)}


def taxa(janela):
    return lambda m: m["frutas"]["taxa_fruta_ruim"][janela]["taxa"]


def fracao_x_por_vida(bancada: bv.Bancada, r: dict) -> dict:
    """N7 (G-MARCA, G-MARCA-E): a fracao de X na extincao (os dias depois de dias_pedido), de toda vida do bloco, com ou sem pedido, pela
    mesma conta do medidas_n7 da bancada (os motivos do cerebro; a decisao k no tick k x 15; X sorteada pela semente da unidade). O P3 sem
    pedido nao tem o bloco n7 nas medidas, e o G-MARCA-E precisa dele: por isso a conta e a mesma para todos aqui."""
    passo, T = CONFIG_PADRAO.intervalo_decisao_ticks, TICKS_POR_DIA
    ini, fim = min(bancada.cfg_pedido.dias_pedido, bancada.dias) * T, bancada.dias * T
    out = {}
    for v in r["vidas"].values():
        cerebro = bv.do_braco(v.motor.politica).cerebro
        consumos = [(k * passo, m["fruta"]["escolhida"], m["fruta"]["presentes"]) for k, m in enumerate(cerebro.motivos) if "fruta" in m]
        x = DonoPedinte.sortear_fruta(v.espec.semente)
        fx = fracao_da_fruta(consumos, x, {"extincao": (ini, fim)})["extincao"]
        out[(_logico(v.rotulo_braco), v.espec.mundo, (v.espec.genoma, v.espec.semente))] = {"fx": fx["taxa"], "n": fx["n"]}
    return out


def fracao_x_extincao(m):
    return m["fx"]


def deferencia_final(m):
    c = m["n7"]["deferencia"]["por_janela"]["final"]["total"]
    return c["deferencia"]


def contratos(bancada: bv.Bancada, runs: dict, unidades: list[dict], k2: bool) -> dict:
    """Os contratos K1-K9 do experimento maior (secao 3) conferidos nas vidas do piloto (secao 3.5 do plano)."""
    principal = runs["principal"]
    out = {}
    # K1: o P0 da bancada (lobos) e o instinto byte a byte, nas tres condicoes
    difere = 0
    for u in unidades:
        for mundo in CONDICOES:
            esp = bv.EspecVida(DONO, "P0", u["semente"], u["genoma"], mundo)
            lobos = [v for v in principal["vidas"].values() if v.origem is None and v.espec == esp]
            inst = bancada.vida(replace(esp, cerebro="instinto"))
            difere += bv.resumo_motor(lobos[0].motor) != bv.resumo_motor(inst.motor)
    out["K1_P0_e_o_instinto"] = {"passa": difere == 0, "vidas_diferentes": difere}
    out["K2_humor_da_fruta_no_P1"] = {"passa": k2}
    # K3: P2 e P2e informam nos mesmos ticks, conteudo oposto
    ruins = 0
    for u in unidades:
        for mundo in CONDICOES:
            ku = (u["genoma"], u["semente"])
            a = principal["idx"][("P2", mundo, ku)]["frutas"]["informacoes"]
            b = principal["idx"][("P2e", mundo, ku)]["frutas"]["informacoes"]
            ok = [(x["tick"], x["fruta"]) for x in a] == [(x["tick"], x["fruta"]) for x in b] and \
                all(x["conteudo"] != y["conteudo"] for x, y in zip(a, b))
            ruins += not ok
    out["K3_P2_e_P2e_mesmos_ticks_conteudo_oposto"] = {"passa": ruins == 0, "celulas_ruins": ruins}
    out["K4_dono_julga_fruta"] = {"passa": em.K4_DONO_JULGA_FRUTA}
    # K5 e K7: as ofertas de fruta sao as mesmas em todo braco e em todo acoplado da unidade, no mesmo mundo
    ofertas = {}
    for v in principal["vidas"].values():
        evs = tuple((e.tick, str(e.valor)) for e in v.motor.log if e.tipo == "acao_usuario" and str(e.valor) in bv.EVENTOS_DO_MUNDO)
        ofertas.setdefault((v.espec.mundo, v.espec.genoma, v.espec.semente), set()).add(evs)
    distintas = sum(len(s) > 1 for s in ofertas.values())
    out["K5_K7_mesmas_ofertas_nos_bracos_e_acoplados"] = {"passa": distintas == 0, "celulas_com_ofertas_distintas": distintas}
    # K6: casado e descasado com efeitos opostos fruta a fruta, por genoma
    opostos = 0
    for u in unidades:
        e_c = bancada.efeitos_reais(bv.EspecVida(DONO, "P0", u["semente"], u["genoma"], "casado_frutas"))["antes"]
        e_d = bancada.efeitos_reais(bv.EspecVida(DONO, "P0", u["semente"], u["genoma"], "descasado"))["antes"]
        opostos += all(e_c[f] == -e_d[f] for f in e_c)
    out["K6_condicoes_por_genoma"] = {"passa": opostos == len(unidades), "unidades_com_efeitos_opostos": opostos}
    # K8: o registro do consumo e a medida da secao 4.1
    sem = sum(1 for m in principal["medidas"].values() if m["frutas"] is not None and m["frutas"]["consumos"] !=
              m["frutas"]["taxa_fruta_ruim"]["total"]["n"])
    out["K8_registro_do_consumo"] = {"passa": sem == 0, "vidas_com_contagem_diferente": sem}
    out["K9_G1"] = {"passa": True, "como": "toda vida e todo acoplado rejogados do disco bit a bit pela bancada (bv.rodar)"}
    return out


def etapa_d(cfg: dict, saida: Path, unidades: list[dict], escolhidos: dict, canais: bool) -> dict:
    g, w0p, ganho, w0i = escolhidos["g"], escolhidos["w0_pedido"], escolhidos["ganho"], escolhidos["w0_info"]
    lobos = {"memoria_ganho": g, "w0_pedido": w0p, "w0_info": w0i}
    cons = {"ganho": ganho, "canais_ligados": canais}
    bc = BRACO_COMPLETO
    t0 = time.perf_counter()
    runs = {}
    principal = config_bancada(cfg, "D principal", [bc[b] for b in ("P0", "P1", "P2", "P2e", "P2a", "P3")], CONDICOES, lobos, cons,
                               [{"origem": bc[b], "destino": "P0", "filtro": FILTRO_SO_CUIDADO} for b in ("P2", "P2e", "P3")])
    runs["principal"] = rodar_bancada(principal, saida / "D" / "principal")
    runs["sem_memoria"] = rodar_bancada(config_bancada(cfg, "D ablacao P1 sem memoria", [ABLACAO["memoria"]], ("descasado", "mutavel"),
                                                       lobos, cons), saida / "D" / "ablacao_sem_memoria")
    runs["escalar"] = None
    if canais:
        runs["escalar"] = rodar_bancada(config_bancada(cfg, "D ablacao P1 escalar", [ABLACAO["canais"]], ("descasado", "mutavel"), lobos,
                                                       cons), saida / "D" / "ablacao_escalar")
    runs["n6"] = rodar_bancada(config_bancada(cfg, "D bloco N6", ["MR"], ["descasado"], {"memoria_ganho": g}, None,
                                              [{"origem": "MR", "destino": d, "filtro": "nenhum"} for d in ("M0", "MT", "ME")]),
                               saida / "D" / "bloco_n6")
    runs["n7"] = rodar_bancada(config_bancada(cfg, "D bloco N7", ["P0", "P0+ped", "P1+ped", "P3+ped", "P3"], ["iguais_frutas"], lobos,
                                              cons, [{"origem": "P3+ped", "destino": "P0", "filtro": FILTRO_SO_CUIDADO}]),
                               saida / "D" / "bloco_n7")
    # a referencia do mundo padrao (descritiva) com os bracos simples: sem frutas a memoria nao tem o que guardar (a bancada recusa
    # braco com memoria fora das frutas); os canais seguem a config
    runs["padrao"] = rodar_bancada(config_bancada(cfg, "D referencia padrao", ["P0", "P1", "P3"], ["padrao"], lobos, cons),
                                   saida / "D" / "referencia_padrao")
    segundos = time.perf_counter() - t0
    n_vidas = sum(len(r["vidas"]) for r in runs.values() if r is not None)
    boot = cfg["bootstrap"]

    # os seis primarios e a equivalencia (secao 6 do experimento maior), com os nomes logicos
    idx_p = indice_logico(runs["principal"])
    runs["principal"]["idx"] = idx_p
    regra = em.delta_da_regra(idx_p, unidades)
    delta = regra["delta"]
    primarios = {c.nome: em.calcular_contraste(idx_p, unidades, c, boot) for c in em.PRIMARIOS}
    eq = em.calcular_contraste(idx_p, unidades, em.EQUIVALENCIA, boot)
    tam = em.tamanhos(primarios, delta, ALFA, PODER)
    alfa_passo = ALFA / len(em.PRIMARIOS)
    for nome, c in primarios.items():
        vs = [x for gr in c["valores"].values() for x in gr]
        n = tam["por_contraste"][nome]["n"]
        tam["por_contraste"][nome]["poder_simulado"] = poder_simulado(vs, delta, n, alfa_passo, REPLICAS_PODER, boot["semente"])
        tam["por_contraste"][nome]["sigma2_d"] = None if tam["por_contraste"][nome]["sigma_d"] is None else \
            tam["por_contraste"][nome]["sigma_d"] ** 2
    vs_eq = [x for gr in eq["valores"].values() for x in gr]
    sig_eq = _sigma(vs_eq)
    n_eq = tamanho_amostra(sig_eq, delta, ALFA, PODER, 5) if (sig_eq is not None and delta) else None
    n_val = tam["n_validacao"]

    # os blocos: os deltas pelas regras dos planos deles (N6, secao 7; N7, secao 7) e o poder dos secundarios com o N escolhido
    idx_6 = indice_logico(runs["n6"])
    idx_7 = indice_logico(runs["n7"])
    t_m0 = [taxa("final")(idx_6[("M0<MR:nenhum", "descasado", (u["genoma"], u["semente"]))]) for u in unidades]
    t_m0 = [x for x in t_m0 if x is not None]
    delta_n6 = (sum(t_m0) / len(t_m0)) / 2.0 if t_m0 else None
    fx_7 = fracao_x_por_vida(bv.bancada_da_config(principal), runs["n7"])
    fx = [fx_7[(f"P0<P3+ped:{FILTRO_SO_CUIDADO}", "iguais_frutas", (u["genoma"], u["semente"]))]["fx"] for u in unidades]
    fx = [x for x in fx if x is not None]
    delta_n7 = (sum(fx) / len(fx)) / 2.0 if fx else None
    idx_completo = dict(idx_p)
    sec = {}
    a3 = ALFA / 3
    sec["G-CAUSAL"] = secundario(idx_6, unidades, "G-CAUSAL", "N6", "descasado", taxa("final"), "M0<MR:nenhum", "MR", delta_n6, a3, n_val)
    sec["G-REC"] = secundario(idx_6, unidades, "G-REC", "N6", "descasado", taxa("final"), "MT<MR:nenhum", "MR", delta_n6, a3, n_val)
    sec["G-EMB"] = secundario(idx_6, unidades, "G-EMB", "N6", "descasado", taxa("final"), "ME<MR:nenhum", "MR", delta_n6, a3, n_val)
    sec["G-EROSAO"] = secundario(idx_7, unidades, "G-EROSAO", "N7", "iguais_frutas", deferencia_final, "P0+ped", "P1+ped", delta_n7, a3,
                                 n_val)
    sec["G-MARCA"] = secundario(fx_7, unidades, "G-MARCA", "N7", "iguais_frutas", fracao_x_extincao,
                                f"P0<P3+ped:{FILTRO_SO_CUIDADO}", "P3+ped", delta_n7, a3, n_val)
    sec["G-MARCA-E"] = secundario(fx_7, unidades, "G-MARCA-E", "N7", "iguais_frutas", fracao_x_extincao, "P3", "P3+ped", delta_n7, a3,
                                  n_val)
    # as ablacoes da K-7 no P1 (descasado: final; mutavel: depois da troca)
    for nome_ab, run_ab in (("memoria", runs["sem_memoria"]), ("canais", runs["escalar"])):
        for mundo, janela in (("descasado", "final"), ("mutavel", "depois_da_troca")):
            chave = f"ablacao_{nome_ab}_{mundo}"
            if run_ab is None:
                sec[chave] = {"nome": chave, "familia": "ablacoes", "leitura": "nao testavel (sem a peca na main, K-6)"}
                continue
            ix = indice_logico(run_ab)
            junto = {**{("sem", mu, ku): m for (b, mu, ku), m in ix.items()},
                     **{("completo", mu, ku): m for (b, mu, ku), m in idx_completo.items() if b == "P1"}}
            sec[chave] = secundario(junto, unidades, chave, "ablacoes", mundo, taxa(janela), "sem", "completo", delta, ALFA, n_val)
    # N5, descritivo: P2 - P2a no descasado
    p2a = em.calcular_contraste(idx_p, unidades, em.Contraste("P2_menos_P2a", 3, "descasado", "consumos_ate_metade", "P2a", "P2"), boot)

    seg_vida = segundos / n_vidas
    horas = (VIDAS_POR_UNIDADE * n_val * seg_vida / 3600.0) if n_val else None
    return {"etapa": "D", "ponto": escolhidos, "canais": canais, "vidas": n_vidas, "segundos": segundos, "segundos_por_vida": seg_vida,
            "delta": regra, "delta_n6": {"delta": delta_n6, "regra": "metade da taxa_fruta_ruim final do M0<MR (N6, secao 7)", "n": len(t_m0)},
            "delta_n7": {"delta": delta_n7, "regra": "metade da fracao de X na extincao do P0<P3+ped:sem_ensino (N7, secao 7)", "n": len(fx)},
            "primarios_piloto": primarios, "equivalencia_piloto": {**eq, "sigma_d": sig_eq, "n_ic90": n_eq},
            "tamanho_amostra": tam, "n_validacao": n_val, "k_validacao": (n_val // 5) if n_val else None,
            "horas_validacao_estimadas": horas, "teto_horas": TETO_HORAS_VALIDACAO,
            "cabe_no_teto": (horas is not None and horas <= TETO_HORAS_VALIDACAO),
            "secundarios": sec, "n5_descritivo_P2a_menos_P2": p2a,
            "contratos": contratos(bv.bancada_da_config(principal), runs, unidades,
                                   bv.bancada_da_config(principal).cfg_consequencia.humor_na_fruta)}


# ------------------------------------------------------------------ o todo


def rodar(cfg: dict, saida: Path | None = None) -> dict:
    modo, unidades = modo_e_unidades(cfg)
    gr = grades(cfg)
    canais = bool(cfg.get("canais", True))
    if modo == "calibracao":
        faltam = pecas_pendentes(cfg)
        if faltam:
            raise NotImplementedError("calibracao sem as pecas da bancada: " + "; ".join(faltam))
    saida = Path(saida or cfg.get("saida", SAIDA_PADRAO))
    if not saida.is_absolute():
        saida = RAIZ / saida
    etapas = cfg.get("etapas", list(ETAPAS))
    t0 = time.perf_counter()
    res: dict = {"modo": modo, "unidades": len(unidades), "canais": canais}
    escolhidos: dict = dict(cfg.get("ponto_fixo", {}))
    if "A1" in etapas:
        res["A1"] = etapa_a1(cfg, saida, gr["g"])
        escolhidos["g"] = res["A1"]["escolhido"]
        _gravar(saida / "A1" / "resultado.json", _dump(res["A1"]))
    if "A2" in etapas:
        res["A2"] = etapa_a2(cfg, saida, gr["w0_pedido"])
        escolhidos["w0_pedido"] = res["A2"]["escolhido"]
        _gravar(saida / "A2" / "resultado.json", _dump(res["A2"]))
    if "B" in etapas:
        res["B"] = etapa_b(cfg, saida, gr["ganho"], escolhidos["g"], canais)
        escolhidos["ganho"] = res["B"]["escolhido"]
        _gravar(saida / "B" / "resultado.json", _dump(res["B"]))
    if "C" in etapas:
        res["C"] = etapa_c(cfg, saida, gr["w0_info"], escolhidos["g"], escolhidos["ganho"], canais)
        escolhidos["w0_info"] = res["C"]["escolhido"]
        _gravar(saida / "C" / "resultado.json", _dump(res["C"]))
    _gravar(saida / "escolha.json", _dump({"ponto": escolhidos, "fecharam": {e: res[e]["fechou"] for e in ("A1", "A2", "B", "C")
                                                                             if e in res}}))
    if "D" in etapas:
        res["D"] = etapa_d(cfg, saida, unidades, escolhidos, canais)
        _gravar(saida / "D" / "resultado.json", _dump(res["D"]))
        _gravar(saida / "adendo.json", _dump(adendo(res, unidades)))
    res["ponto"] = escolhidos
    res["segundos"] = time.perf_counter() - t0
    _gravar(saida / "meta.json", _dump({"config": cfg, "modo": modo, "plano": PLANO, "plano_sha256": bv._sha(RAIZ / PLANO),
                                       "orquestrador_sha256": bv._sha(Path(__file__)), "python": platform.python_version(),
                                       "plataforma": platform.platform(), "segundos": res["segundos"], "ponto": escolhidos}))
    return res


def adendo(res: dict, unidades: list[dict]) -> dict:
    """O conteudo do adendo (secao 5.3 do plano), para ser commitado no experimento maior antes da validacao."""
    d = res["D"]
    return {"parametros": {e: {"parametro": res[e]["parametro"], "escolhido": res[e]["escolhido"], "regra": res[e]["regra"],
                               "fechou": res[e]["fechou"]} for e in ("A1", "A2", "B", "C")},
            "delta": d["delta"]["delta"], "delta_n6": d["delta_n6"]["delta"], "delta_n7": d["delta_n7"]["delta"],
            "primarios": {n: {k: c.get(k) for k in ("sigma_d", "sigma2_d", "n", "poder_simulado")}
                          for n, c in d["tamanho_amostra"]["por_contraste"].items()},
            "equivalencia": {"sigma_d": d["equivalencia_piloto"]["sigma_d"], "n_ic90": d["equivalencia_piloto"]["n_ic90"]},
            "n_validacao": d["n_validacao"], "k_validacao_por_base": d["k_validacao"], "bases_validacao": bv.BASES_EXPERIMENTO_MAIOR["validacao"],
            "secundarios": {n: {k: s.get(k) for k in ("familia", "sigma_d", "poder_com_n", "subpotenciado", "leitura")} for n, s in
                            d["secundarios"].items()},
            "horas_validacao_estimadas": d["horas_validacao_estimadas"], "cabe_no_teto_K10": d["cabe_no_teto"],
            "unidades_calibracao": len(unidades)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="calibracao conjunta do cerebro A (docs/PLANO_CALIBRACAO_CONJUNTA_V2.md)")
    ap.add_argument("--config", required=True)
    ap.add_argument("--saida", default=None)
    a = ap.parse_args(argv)
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    r = rodar(cfg, a.saida)
    print(f"{r['modo']}: ponto {r['ponto']}; " + (f"N da validacao {r['D']['n_validacao']}, {r['D']['horas_validacao_estimadas']:.1f} h"
                                                   if "D" in r and r["D"]["horas_validacao_estimadas"] is not None else "sem D"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
