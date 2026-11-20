"""A bancada da V2, módulo `passo0`.

O passo 0 do corpo.

Parte do pacote `experiments/bancada/` (rodada de saúde, etapa 3; docs/TAREFA_V2_SAUDE.md). O texto de cada definição é o de antes,
movido de `experiments/bancada_v2.py` sem mudança (tools/dividir_bancada.py; a prova pela AST em docs/historico/bancada_mapa.json).
O `experiments/bancada_v2.py` continua sendo a porta de entrada: ele reexporta todo nome daqui.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

from digilab.config import ConfigCorpo

from . import RAIZ


# o passo 0 da calibracao do corpo (PLANO_ANALISE_V2_CORPO_DRIVES, adendo 3, A3.2 e A3.2b; ME-7; PCD-9): so o P0-q, com o metabolismo, nas
# 20 unidades da calibracao (bases 33101...33505, K = 4) e nas 8 celulas; um m_gasto, o mesmo no basal (375 acordado, 187 dormindo) e no
# gasto de cada atividade sobre o combustivel (o fator `gasto_atividades_num/den` do #275), em {1/4, 1/2, 1}: 3 pontos, 480 vidas. O
# cansaco nao muda (ME-1, ME-3). Fica o ponto mais perto de 1 (|log2|) com a fracao do tempo acordado com a falta em [0,05; 0,30], nas 8
# celulas juntas; sem nenhum, o de fracao mais perto do centro da faixa, "nao fechou". A faixa e PROPOSTA, SEM FONTE.
PASSO0_MULTIPLICADORES = ((1, 4), (1, 2), (1, 1))           # (num, den): 1/4, 1/2, 1 (PCD-9; o 2 da A3.2 saiu)
PASSO0_FAIXA = (0.05, 0.30)
PASSO0_BRACO = "P0-q"
PASSO0_CAMPOS = ("gasto_basal_acordado", "gasto_basal_dormindo", "gasto_atividades_num", "gasto_atividades_den")


def _escalar(v: int, num: int, den: int) -> int:
    """v x num/den, arredondado (metade para cima, o div_arred para positivos): 375/2 = 188, 187/2 = 94, 375/4 = 94 e 187/4 = 47 (A3.2b)"""
    return (v * num + den // 2) // den


PASSO0_CHAVES_EXTRAS = ("multiplicadores", "passo0_anterior")    # adendo 5 (A5.1): a grade fina e os pontos ja medidos


def grade_passo0(cfg: dict) -> tuple:
    """Os (num, den) do passo 0: os da config (`multiplicadores`, o passo 0 fino do adendo 5) ou os da PCD-9. Fracoes em (0, 1], sem
    repeticao (falha alto)."""
    grade = tuple(tuple(m) for m in cfg.get("multiplicadores", PASSO0_MULTIPLICADORES))
    if not grade or len(set(grade)) != len(grade) or any(len(m) != 2 or not 0 < m[0] <= m[1] for m in grade):
        raise ValueError(f"multiplicadores do passo 0: fracoes (num, den) em (0, 1], sem repeticao: {grade}")
    return grade


def pontos_passo0(cfg: dict) -> list[tuple[str, dict]]:
    """As configs do passo 0 a partir da `cfg` (a da calibracao do corpo com o P0-q), uma por (num, den) da grade (`grade_passo0`), pela
    chave "corpo": o basal (`gasto_basal_acordado`, `gasto_basal_dormindo`) x num/den, arredondado, e o fator das atividades
    (`gasto_atividades_num/den`) = num/den (o corpo arredonda cada gasto por div_arred). A `cfg` nao pode trazer esses campos: o passo 0 e
    quem os escala. As chaves so do passo 0 (a grade, os pontos ja medidos) nao vao para a config de cada ponto."""
    if cfg.get("bracos") != [PASSO0_BRACO]:
        raise ValueError(f"o passo 0 roda so o {PASSO0_BRACO}: {cfg.get('bracos')}")
    escalados = set(cfg.get("corpo", {})) & set(PASSO0_CAMPOS)
    if escalados:
        raise ValueError(f"o passo 0 escala {PASSO0_CAMPOS}; a config nao pode fixa-los: {sorted(escalados)}")
    base = ConfigCorpo()
    resto = {k: v for k, v in cfg.items() if k not in PASSO0_CHAVES_EXTRAS}
    pontos = []
    for num, den in grade_passo0(cfg):
        corpo = {**cfg.get("corpo", {}), "gasto_basal_acordado": _escalar(base.gasto_basal_acordado, num, den),
                 "gasto_basal_dormindo": _escalar(base.gasto_basal_dormindo, num, den),
                 "gasto_atividades_num": num, "gasto_atividades_den": den}
        pontos.append((f"gasto_{num}_{den}", {**resto, "corpo": corpo}))
    return pontos


def fracao_falta_passo0(medidas: dict) -> dict:
    """A fracao do tempo acordado com a falta nas 8 celulas juntas (A3.2): a soma dos ticks acordados com falta sobre a soma dos ticks
    acordados, nas vidas do P0-q (sem acoplados) com o metabolismo. Uma vida sem a medida falha alto."""
    falta = acordado = vidas = 0
    for m in medidas.values():
        if m.get("origem") is not None or m["braco"] != PASSO0_BRACO:
            continue
        met = (m.get("corpo") or {}).get("metabolismo")
        if met is None:
            raise ValueError(f"{m['vida']}: sem a medida do metabolismo")
        falta += met["acordado_com_falta"]
        acordado += met["acordado"]
        vidas += 1
    if not acordado:
        raise ValueError("o passo 0 sem tick acordado")
    return {"vidas": vidas, "acordado": acordado, "acordado_com_falta": falta, "fracao": falta / acordado}


def escolha_passo0(fracoes: dict, grade: tuple | None = None) -> dict:
    """A regra do passo 0 (A3.2, escrita antes): `fracoes` = {(num, den): fracao do tempo acordado com a falta}. Fica o ponto mais perto de
    1 pela |log2(num/den)| com a fracao em PASSO0_FAIXA; num empate de |log2| (nao ha na grade da PCD-9), o menor gasto (como o "menor
    m_sobe" da 6.2). Sem nenhum, o
    de fracao mais perto do centro da faixa, com "nao fechou". `grade` = os pontos que a regra le (a da PCD-9; no adendo 5, os sete: os
    quatro novos e os tres ja medidos); ponto faltando ou fora dela falha alto."""
    grade = PASSO0_MULTIPLICADORES if grade is None else tuple(tuple(m) for m in grade)
    if set(fracoes) != set(grade):
        raise ValueError(f"o passo 0 pede os pontos {grade}: {sorted(fracoes)}")
    lo, hi = PASSO0_FAIXA
    distancia = lambda p: abs(math.log2(p[0] / p[1]))  # noqa: E731
    passam = [p for p in sorted(grade, key=lambda q: q[0] / q[1]) if lo <= fracoes[p] <= hi]
    if passam:
        p = min(passam, key=lambda q: (distancia(q), q[0] / q[1]))
        return {"ponto": list(p), "fechou": True, "fracao": fracoes[p], "passam": [list(q) for q in passam]}
    centro = (lo + hi) / 2
    p = min(grade, key=lambda q: (abs(fracoes[q] - centro), distancia(q), q[0] / q[1]))
    return {"ponto": list(p), "fechou": False, "fracao": fracoes[p], "passam": [], "registro": "nao fechou"}


def _rodar_ponto_passo0(c: dict, pasta: str) -> dict:
    """Um ponto do passo 0 pela `rodar` de sempre (num processo do pool); devolve so as medidas (a vida nao atravessa o pool)."""
    return rodar(c, Path(pasta))["medidas"]


def rodar_passo0(cfg: dict, pasta: Path, processos: int = 1) -> dict:
    """O passo 0 inteiro (A3.2 e A3.2b): cada ponto de `pontos_passo0` pela `rodar` de sempre, em `pasta/<ponto>/` (vidas gravadas e
    rejogadas do disco, medidas, meta), a fracao das 8 celulas juntas por ponto e a escolha pela regra; grava `pasta/passo0.json`. Toda
    config de ponto e validada antes da primeira vida (as sementes fora das dos testes pedem o plano). Recusa uma pasta que ja existe
    (PLANO_ANALISE_V2_CORPO_DRIVES, secao 11). Com `processos` > 1, os pontos rodam em paralelo (cada vida e independente e
    determinista). Com `passo0_anterior` (o adendo 5, A5.1), a regra le tambem os pontos daquele passo0.json, com as mesmas sementes:
    um ponto repetido, uma config de outras unidades ou de outro corpo falham alto."""
    if pasta.exists():
        raise FileExistsError(f"{pasta}: a pasta de saida do passo 0 ja existe")
    pontos = pontos_passo0(cfg)
    grade = grade_passo0(cfg)
    for _, c in pontos:
        validar_config(c)
    anteriores = {}
    if cfg.get("passo0_anterior"):
        ant = json.loads((RAIZ / cfg["passo0_anterior"]).read_text(encoding="utf-8"))
        for nome, p in ant["pontos"].items():
            mult = tuple(p["m_gasto"])
            if mult in grade:
                raise ValueError(f"o ponto {mult} ja foi medido em {cfg['passo0_anterior']}")
            anteriores[nome] = p
        fora_do_gasto = lambda c: ({k: v for k, v in c.items() if k not in ("corpo", "descricao")},  # noqa: E731
                                   {k: v for k, v in c["corpo"].items() if k not in PASSO0_CAMPOS})
        for nome, p in anteriores.items():                  # cada ponto anterior, pela config que o meta dele gravou
            base = json.loads((RAIZ / Path(cfg["passo0_anterior"]).parent / nome / "meta.json").read_text(encoding="utf-8"))["config"]
            if fora_do_gasto(base) != fora_do_gasto(pontos[0][1]) or {k: base["corpo"][k] for k in PASSO0_CAMPOS} != p["corpo"]:
                raise ValueError(f"o passo 0 anterior ({cfg['passo0_anterior']}, {nome}) nao tem a mesma config fora do gasto")
    tarefas = [(_rodar_ponto_passo0, (c, str(pasta / nome))) for nome, c in pontos]
    if processos <= 1:
        medidas = [f(*a) for f, a in tarefas]
    else:
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=processos) as pool:
            futuros = [pool.submit(f, *a) for f, a in tarefas]
            medidas = [fu.result() for fu in futuros]
    fracoes, por_ponto = {}, {}
    for (nome, c), mult, med in zip(pontos, grade, medidas):
        f = fracao_falta_passo0(med)
        fracoes[mult] = f["fracao"]
        por_ponto[nome] = {"m_gasto": list(mult), "corpo": {k: c["corpo"][k] for k in PASSO0_CAMPOS}, **f}
    for nome, p in anteriores.items():
        fracoes[tuple(p["m_gasto"])] = p["fracao"]
    escolha = escolha_passo0(fracoes, tuple(fracoes))
    nome = f"gasto_{escolha['ponto'][0]}_{escolha['ponto'][1]}"
    todos = {**por_ponto, **{n: {**p, "anterior": cfg["passo0_anterior"]} for n, p in anteriores.items()}}
    saida = {"plano": cfg.get("plano"), "faixa": list(PASSO0_FAIXA), "pontos": todos,
             "escolha": {**escolha, "nome": nome, "corpo": todos[nome]["corpo"]}}
    _gravar(pasta / "passo0.json", _dump(saida))
    return saida


# os nomes de outros módulos do pacote que só rodam dentro das funções: importados depois das definições, para o pacote
# não ter importação circular (tools/dividir_bancada.py)
from .config import validar_config  # noqa: E402
from .rodar import _dump, _gravar, rodar  # noqa: E402
