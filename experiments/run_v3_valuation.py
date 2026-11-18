"""VALUATION V2: a ablacao do Valuation, uma vez (docs/PLANO_ANALISE_V3_VALUATION.md; docs/TAREFA_V3_VALUATION.md).

Pergunta (a secao 1 do plano): qual elo do Valuation faz o REL da C4 fechar menos episodios de fome dentro da janela que a baseline trivial
da A1? Uma ablacao por hipotese, cada uma contra o REL completo, na mesma unidade (base, semente), nas 4 celulas do `longe_fixo`.

Os bracos (a secao 3 do plano), cada um mudando UMA coisa do REL (`SUBCHAVES_C4["REL"]`):
  - REL: nada (o controle);
  - B: `epsilon = 0` nos inatos (o g_exp fora dos pesos);
  - C: `controle_mem = "sem"` (o braco SEM da C4: nenhum lugar lembrado);
  - E: o vies do `W0[comer]` de -17S/16 para -S/2 (D-VAL-8);
  - F: a `ConfigAblacaoValuation(ve_z=True)` (o V e o E fora do z);
  - G: a `ConfigAblacaoValuation(maior_peso=True)` (o maior peso no lugar do sorteio);
  - R: `lambda_sono = 0` nos inatos (o reflexo do sono nunca dispara; D-VAL-7).
O braco A (a `ConfigDecisaoNaComida`) fica FORA (`FORA`, o adendo 1 do plano, D-VAL-11): com ele o pet decide fora da grade de 15 ticks, e
as medidas da A1 (`orq.medidas`: a decisao k no tick k x 15; a janela do episodio em decisoes) recusam a vida. Medi-lo pede mudar a metrica
da A1, que o pedido proibe. Pedir o braco falha alto.

A vida de cada braco e a da C4 (`run_v2_memoria_autobio.viver`, refeita aqui so para montar o cerebro do braco): o `MotorGravaCorpo`, o
pet sozinho, 14 dias, orcamento de 16 por dia, o coletor das categorias; o replay do disco (G1), o T-CENARIO-1, as conferencias da C4 e a
conferencia da ablacao (a secao 3 do plano: a ablacao fez o que diz, senao falha alto). As medidas sao as da C4 (`orq.medidas` com o
conserto, `lr.medidas_do_corpo`, `ma.medidas_memoria`) mais os descritivos da secao 5.3 (`descritivo_valuation`).

A analise (as secoes 5 a 7): o primario braco - REL na taxa por episodio, o t sobre as unidades, o Holm sobre os p unilaterais da familia
(alfa 0,025), a classe de A6.6 com a margem 0,032 e a leitura de cada hipotese; a guarda do bem-estar (a privacao e a exaustao, sem gate);
os descritivos, com a fracao do gap da A1 que cada braco cobre.

A trava (a secao 0 do plano): a run de verdade recusa rodar sem o "APROVADO pelo Matheus" no cabecalho do plano, sem o adendo 1 APROVADO
(o braco A fora), sem a faixa em FAIXAS_RESERVADAS e com a pasta de saida ja existente. A fumaca usa as sementes dos testes.
Uso: python experiments/run_v3_valuation.py --config experiments/configs/v3_valuation/ablacao.json --processos 4
"""
from __future__ import annotations

import argparse
import gzip
import io
import json
import platform
import shutil
import subprocess
import sys
import tarfile
import time
from dataclasses import replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import exportar_gabarito_lobos as gl  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402
import run_v2_longe_regular as lr  # noqa: E402
import run_v2_memoria_autobio as ma  # noqa: E402
from bancada.faixas import FAIXAS_RESERVADAS  # noqa: E402
from bancada.regras_mundo import simular_vida_fisico  # noqa: E402
from digilab.config import (CONFIG_ABLACAO_VALUATION, CONFIG_DIGIBRAIN_INATOS, CONFIG_PADRAO, ConfigAblacaoValuation,  # noqa: E402
                            ConfigDigibrainInatos)
from digilab.digibrain import DigiBrain  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.metrics import holm  # noqa: E402
from digilab.mundo import DonoComLugar  # noqa: E402
from digilab.temperamento import NEUTRO  # noqa: E402

PLANO = "docs/PLANO_ANALISE_V3_VALUATION.md"
FASE = "valuation"
PREFIXO = orq.PREFIXO                                         # a derivacao da C4 e da A1 (secao 4)
BASES = (99101, 99202, 99303, 99404, 99505)                   # secao 4 (D-VAL-9, aprovada em 2026-11-16)
FAIXA = (99101, 99505)
K_POR_BASE = 40                                               # secao 4: N = 200 unidades
DIAS, ORCAMENTO_POR_DIA = 14, 16                              # secao 2 (os da C4)
SAIDA = "artifacts_v3_valuation/ablacao"                      # secao 8
MAX_PROCESSOS = 4                                             # V3-D8
LUGAR = "longe_fixo"                                          # secao 2: so o longe_fixo
DONOS = orq.DONOS
CELULAS = tuple((d, LUGAR) for d in DONOS)
BRACOS_PLANO = ("REL", "A", "B", "C", "E", "F", "G", "R")     # secao 3
FORA = {"A": "a ConfigDecisaoNaComida tira a decisao da grade de 15 ticks, e as medidas da A1 (a decisao k no tick k x 15, a janela em "
             "decisoes) recusam a vida; medi-la pede mudar a metrica da A1 (o adendo 1 do plano, D-VAL-11)"}
BRACOS = tuple(b for b in BRACOS_PLANO if b not in FORA)
HIPOTESES = BRACOS[1:]
CONTROLE = "REL"
MARGEM = ma.MARGEM                                            # 6.2: o 0,032 da C4 e da A1, SEM FONTE
ALFA_FAMILIA = ma.ALFA_FAMILIA                                # 6.1 (D-VAL-10): 0,025 unilateral, na familia
VIES_COMER_E = -CONFIG_DIGIBRAIN_INATOS.escala // 2           # secao 3 (D-VAL-8): o vies do comer no braco E, -S/2
GAP_A1 = -0.083                                               # REL - TRIV da A1 (RESULTADO_V3_BASELINE_TRIVIAL, secao 3; o PR #943)
CHAVES_CONFIG = lr.CHAVES_CONFIG
EPISODIO = ma.EPISODIO
PRIVACAO = lambda r: r["privacao"]                            # noqa: E731
EXAUSTAO = lambda r: r["exaustao"]                            # noqa: E731
STATUS_ADENDO_1 = "**Status do adendo 1: APROVADO pelo Matheus"


# ================================================================== os bracos
def montar(braco: str) -> dict:
    """a ConfigDigibrain, os inatos e a ablacao do braco (a secao 3 do plano): o REL e uma mudanca so. O braco fora falha alto."""
    if braco in FORA:
        raise ValueError(f"o braco {braco!r} esta fora da run: {FORA[braco]}")
    if braco not in BRACOS:
        raise ValueError(f"braco {braco!r}: so {BRACOS}")
    cd, inatos, ab = orq.config_do_braco("REL", conserto=True), CONFIG_DIGIBRAIN_INATOS, CONFIG_ABLACAO_VALUATION
    if braco == "B":
        inatos = replace(inatos, epsilon=0)
    elif braco == "C":
        cd = replace(cd, controle_mem="sem")
    elif braco == "E":
        inatos = inatos_e()
    elif braco == "F":
        ab = ConfigAblacaoValuation(ve_z=True)
    elif braco == "G":
        ab = ConfigAblacaoValuation(maior_peso=True)
    elif braco == "R":
        inatos = replace(inatos, lambda_sono=0)
    return {"cd": cd, "inatos": inatos, "ablacao": ab}


def inatos_e() -> ConfigDigibrainInatos:
    """os inatos do braco E: so o vies da linha do comer muda (D-VAL-8); o `u_fome` e as outras linhas ficam"""
    base = CONFIG_DIGIBRAIN_INATOS
    w0 = tuple((b, tuple((c, VIES_COMER_E if c == "vies" else w) for c, w in linha)) if b == "comer" else (b, linha) for b, linha in base.w0)
    if w0 == base.w0:
        raise RuntimeError("inatos_e: o W0 do comer nao mudou")
    return replace(base, w0=w0)


def descrever(braco: str) -> dict:
    """o que o braco muda, para o meta (a secao 8: os bracos com as subchaves e os inatos de cada um)"""
    m = montar(braco)
    base = CONFIG_DIGIBRAIN_INATOS
    return {"subchaves": orq.SUBCHAVES_C4["REL"] | ({"controle_mem": "sem"} if braco == "C" else {}),
            "inatos_mudados": {f: getattr(m["inatos"], f) for f in ("epsilon", "lambda_sono", "w0") if getattr(m["inatos"], f) != getattr(base, f)},
            "ablacao": {"ve_z": m["ablacao"].ve_z, "maior_peso": m["ablacao"].maior_peso}}


def fabricas(braco: str, dono: str, semente: int, dias: int, orcamento_por_dia: int) -> tuple:
    """(a fabrica do cerebro, a do motor) da vida: o motor e o da C4 (o `MotorGravaCorpo`) em todo braco; o cerebro e o REL com a mudanca
    do braco. No REL, as fabricas sao as da C4 (`orq.fabricas("REL", ..., conserto=True)` e o `fm` do `ma.viver`): o teste confere."""
    m = montar(braco)
    cc = orq.bancada(dias, orcamento_por_dia).cfg_corpo_de(bv.EspecVida(dono, gl.BRACO_V11, semente))

    def fp(cfg=None):
        return orq.Registro(DigiBrain(cfg or CONFIG_PADRAO, m["cd"], orq.CM, inatos=m["inatos"], semente=semente, cfg_ablacao=m["ablacao"]),
                            CONFIG_DIGIBRAIN_INATOS.escala)

    def fm(politica, cfg, s):
        return lr.MotorGravaCorpo(politica, cfg, s, NEUTRO, "brasa", obediencia_desligada=True, cfg_mundo=orq.CM, cfg_corpo=cc)

    return fp, fm


def viver(braco: str, dono: str, lugar: str, semente: int, dias: int, orcamento_por_dia: int):
    """uma vida: a do `ma.viver` (o coletor das categorias no cerebro), com as fabricas do braco. Devolve (o motor, o registro, as fabricas,
    as categorias)."""
    fp, fm = fabricas(braco, dono, semente, dias, orcamento_por_dia)
    registro = fp(CONFIG_PADRAO)
    c, categorias = orq.cerebro_de(registro), ma.Categorias()
    agir = c.agir

    def agir_e_ler(obs, rng):
        acao = agir(obs, rng)
        for e in c.m.mem.recente:
            categorias.setdefault(e["id"], list(e["categoria"]))
        return acao

    c.agir = agir_e_ler
    d = DonoComLugar(criar_dono(dono), lugar, semente, dono, orq.CM)
    motor, _ = simular_vida_fisico(d, registro, semente, dias, orcamento_por_dia * dias, dono, fm)
    del c.agir
    return motor, registro, (fp, fm), categorias


# ================================================================== as conferencias da ablacao (secao 3; falha alta)
def conferir_ablacao(braco: str, registro) -> None:
    """a ablacao do braco fez o que diz, pelo registro do cerebro: o cerebro e o do braco (os inatos, as subchaves e a ablacao nos dois
    modulos) e, decisao a decisao, o B sem o acrescimo do g_exp, o C sem o lugar lembrado, o G sem sorteio e o R sem reflexo. O F (o V e o
    E fora do z) e conferido pela chave nos dois modulos aqui e, conta a conta, no tests/test_valuation.py (o motivo nao guarda o z)."""
    c = orq.cerebro_de(registro)
    m = montar(braco)
    if c.inatos != m["inatos"] or c.cd != m["cd"] or c.m.impulso.ab != m["ablacao"] or c.m.arb.ab != m["ablacao"]:
        raise RuntimeError(f"{braco}: o cerebro da vida nao e o do braco (os inatos, as subchaves ou a ablacao)")
    for x in c.motivos:
        if braco == "B" and any(u["w"] != (u["a"] if u["a"] > 0 else 0) for u in x["unidades"]):
            raise RuntimeError(f"B: um peso diferente da ativacao na decisao {x['k']} (epsilon = 0)")
        if braco == "C" and any(u["chave"][1] == "ponto" for u in x["unidades"]):
            raise RuntimeError(f"C: uma unidade do lugar lembrado na decisao {x['k']}")
        if braco == "G" and x["u"] is not None:
            raise RuntimeError(f"G: um sorteio na decisao {x['k']}")
        if braco == "R" and x["reflexo"]:
            raise RuntimeError(f"R: um reflexo do sono na decisao {x['k']}")
    if braco == "G" and c.m.arb.sorteios != 0:
        raise RuntimeError("G: o M-ARB contou sorteios")
    if braco == "R" and c.m.arb.reflexos != 0:
        raise RuntimeError("R: o M-ARB contou reflexos")
    if braco == "E" and dict(dict(c.inatos.w0)["comer"])["vies"] != VIES_COMER_E:
        raise RuntimeError("E: o vies do comer nao e o do braco")


# ================================================================== os descritivos da secao 5.3
def descritivo_valuation(registro, med: dict) -> dict:
    """por vida: as fracoes das decisoes dos episodios de fome em `dormir` e em `comer`, a fracao dos episodios com a janela vencida, as
    intencoes de comer trocadas numa decisao de reflexo e a fracao das decisoes do episodio (fora do reflexo, com sorteio) em que uma
    unidade do comer tinha o maior peso e saiu outra"""
    ms = orq.cerebro_de(registro).motivos
    eps = med["episodios_fome"]["episodios"]
    ks = sorted({k for k_i, _d0, _w, fim, _m in eps for k in range(k_i, fim + 1)})
    if any(k >= len(ms) for k in ks):
        raise RuntimeError("um episodio de fome fora das decisoes da vida")
    dormir = sum(1 for k in ks if ms[k]["acao"] == "dormir")
    comer = sum(1 for k in ks if ms[k]["acao"] == "comer")
    sorteadas = [ms[k] for k in ks if not ms[k]["reflexo"] and ms[k]["u"] is not None]
    perdeu = 0
    for x in sorteadas:
        topo = max(range(len(x["unidades"])), key=lambda i: (x["unidades"][i]["w"], -i))
        if x["unidades"][topo]["chave"][0] == "comer" and x["escolha"][0] != "comer":
            perdeu += 1
    trocadas = sum(1 for x in ms if x["reflexo"] for f in x["fins"] if f["motivo"] == "trocou" and f["chave"][0] == "comer")
    vencidas = sum(1 for e in eps if e[4] == "janela_vencida")
    return {"decisoes_no_episodio": len(ks), "dormir_no_episodio": dormir / len(ks) if ks else None,
            "comer_no_episodio": comer / len(ks) if ks else None, "janela_vencida": vencidas / len(eps) if eps else None,
            "comer_trocado_no_reflexo": trocadas, "sorteadas_no_episodio": len(sorteadas),
            "comer_no_topo_perdeu": perdeu / len(sorteadas) if sorteadas else None}


# ================================================================== a vida
def _vida(cfg: dict, braco: str, dono: str, lugar: str, unidade: dict, pasta: str) -> dict:
    """uma vida: vivida, gravada, rejogada do disco (G1), conferida (as da C4 e a da ablacao) e medida"""
    c0, p0 = time.process_time(), time.perf_counter()
    motor, registro, fab, categorias = viver(braco, dono, lugar, unidade["semente"], cfg["dias"], cfg["orcamento_por_dia"])
    arquivo = Path(pasta) / "vidas" / braco / f"{dono}_{lugar}_{unidade['semente']}.jsonl"
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    arquivo.write_text(motor.log.para_jsonl(), encoding="utf-8", newline="\n")
    orq.conferir_replay(motor, fab, unidade["semente"], arquivo.read_text(encoding="utf-8"))
    orq.conferir_cenario(motor, registro)
    orq.conferir_mecanismo(braco, registro, None)
    ma.conferir_memoria("SEM" if braco == "C" else "REL", orq.cerebro_de(registro))
    fins = ma.conferir_fins("REL", registro)
    conferir_ablacao(braco, registro)
    med = orq.medidas(motor, registro, braco, cfg["dias"], True)
    return {"vida": f"{braco}|{dono}|{lugar}|{unidade['semente']}", "braco": braco, "dono": dono, "lugar": lugar,
            "semente": unidade["semente"], "base": unidade["base"], "k": unidade["k"], **med,
            "corpo": lr.medidas_do_corpo(motor, registro, cfg["dias"]), "fins_conferidos": fins,
            "memoria": ma.medidas_memoria(registro, cfg["dias"], categorias), "valuation": descritivo_valuation(registro, med),
            "custo": {"vida_cpu": time.process_time() - c0, "vida_parede": time.perf_counter() - p0}}


def tarefa(cfg: dict, unidade: dict, pasta: str) -> list[dict]:
    return [_vida(cfg, b, dono, lugar, unidade, pasta) for b in BRACOS for dono, lugar in CELULAS]


# ================================================================== a analise (secoes 5 a 7)
def _contraste(registros: list[dict], braco: str, medida, rotulo: str, boot: dict) -> dict:
    difs = ma.diferenca(registros, braco, CONTROLE, medida, LUGAR)
    c = orq.contraste_t(difs, boot)
    ic = {"ic_inferior": c["ic95"]["ic_inferior"], "ic_superior": c["ic95"]["ic_superior"], "motivo": c["motivo"]}
    return {"contraste": rotulo, **c, "classe": ma.classe(ic, MARGEM), "margem": MARGEM,
            "margem_efetiva": lr.margem_efetiva(ma.estimativa(difs, MARGEM)["dp"], c["n"])}


def ler_hipotese(c: dict) -> str:
    """a regra da secao 7, escrita antes: confirmada, efeito trivial, refutada ou indeterminada"""
    classe, sinal, rejeita = c["classe"]["classe"], c["classe"]["sinal"], c["holm"]["rejeita"]
    if classe == "> 0" and rejeita:
        return "confirmada"
    if classe == "≈ 0" and sinal == "+" and rejeita:
        return "efeito trivial"
    if classe in ("≈ 0", "< 0"):
        return "refutada"
    return "indeterminada"


def primario(registros: list[dict], boot: dict) -> dict:
    """6.1: braco - REL na taxa por episodio, nas 4 celulas do `longe_fixo`, o t sobre as unidades; o Holm sobre os p unilaterais da
    familia (alfa 0,025); a leitura de cada hipotese (secao 7) e a fracao do gap da A1"""
    cs = {f"{b} - REL": _contraste(registros, b, EPISODIO, f"{b} - REL, a taxa de fechamento por episodio, nas 4 celulas do longe_fixo", boot)
          for b in HIPOTESES}
    h = holm({n: c["p_unilateral"] for n, c in cs.items()}, ALFA_FAMILIA)
    out = {}
    for n, c in cs.items():
        c = {**c, "holm": h[n]}
        out[n] = {**c, "leitura": ler_hipotese(c), "fracao_do_gap_a1": None if c["media"] is None else c["media"] / -GAP_A1}
    return out


def guarda_bem_estar(registros: list[dict]) -> dict:
    """5.2: braco - REL na privacao e na exaustao, com a classe de A6.6; "piora" com a classe "> 0". Sem gate na V2."""
    out = {}
    for b in HIPOTESES:
        priv = ma.estimativa(ma.diferenca(registros, b, CONTROLE, PRIVACAO, LUGAR), MARGEM)
        exa = ma.estimativa(ma.diferenca(registros, b, CONTROLE, EXAUSTAO, LUGAR), MARGEM)
        out[b] = {"privacao": priv, "exaustao": exa,
                  "piora": priv["classe"]["classe"] == "> 0" or exa["classe"]["classe"] == "> 0"}
    return out


DESCRITIVOS = {
    "taxa_por_episodio": EPISODIO,
    "refeicoes_por_dia": lambda r: r["cadeia"]["refeicoes_por_dia"],
    "janela_vencida": lambda r: r["valuation"]["janela_vencida"],
    "dormir_no_episodio": lambda r: r["valuation"]["dormir_no_episodio"],
    "comer_no_episodio": lambda r: r["valuation"]["comer_no_episodio"],
    "reflexos": lambda r: r["reflexos"],
    "latencia_media": lambda r: r["latencia_media"],
    "comer_trocado_no_reflexo": lambda r: r["valuation"]["comer_trocado_no_reflexo"],
    "comer_no_topo_perdeu": lambda r: r["valuation"]["comer_no_topo_perdeu"],
    "episodios_por_vida": lambda r: r["episodios_fome"]["n"],
    "privacao": PRIVACAO,
    "exaustao": EXAUSTAO,
}


def descritivo(registros: list[dict]) -> dict:
    """5.3: o nivel de cada braco e braco - REL, por unidade, com o IC95 pelo t ao lado e sem classe; as sondas, em nivel"""
    sem_classe = lambda e: {k: v for k, v in e.items() if k != "classe"}   # noqa: E731
    out = {n: {"niveis": {b: sem_classe(ma.estimativa(ma.nivel(registros, b, f, LUGAR))) for b in BRACOS},
               "contrastes": {f"{b} - REL": sem_classe(ma.estimativa(ma.diferenca(registros, b, CONTROLE, f, LUGAR))) for b in HIPOTESES}}
           for n, f in DESCRITIVOS.items()}
    out["sondas"] = {m: {b: sem_classe(ma.estimativa(ma.nivel(registros, b, lambda r, m=m: r["influencia"][m], LUGAR))) for b in BRACOS}
                     for m in ma.MODULOS}
    out["acoes_somadas"] = {b: _somar([r for r in registros if r["braco"] == b and r["lugar"] == LUGAR], lambda r: r["acoes"]) for b in BRACOS}
    return out


def _somar(registros: list[dict], ler) -> dict:
    """a soma, campo a campo, do dicionario que `ler` tira de cada vida"""
    soma: dict = {}
    for r in registros:
        for k, v in ler(r).items():
            soma[k] = soma.get(k, 0) + v
    return dict(sorted(soma.items()))


def analisar(registros: list[dict], boot: dict = orq.BOOTSTRAP) -> dict:
    prim = primario(registros, boot)
    confirmadas = [n for n, c in prim.items() if c["leitura"] == "confirmada"]
    return {"primario": prim, "guarda_bem_estar": guarda_bem_estar(registros), "descritivo": descritivo(registros),
            "leitura": {"confirmadas": confirmadas,
                        "checkpoint_v2_5": "causa nao localizada: a frente para" if not confirmadas else
                        "as confirmadas vao a V3 como candidatas, com a guarda do bem-estar; qual conserto entra e do Matheus"},
            "fora": FORA,
            "nao_demonstra": ["as interacoes entre as ablacoes (uma mudanca por braco)", "um nulo vale so para o valor testado (E e R)",
                              "nada fora das 4 celulas do longe_fixo, do mundo do MVP e dos 14 dias", "nada sobre o jogo web",
                              "que uma ablacao confirmada e o conserto (a V3)", "a hipotese D (P1 e P2, a A2)",
                              "a hipotese A (fora da run: o adendo 1, D-VAL-11)"]}


# ================================================================== a trava e a run
def exigir_aprovado(plano: str) -> None:
    """a trava da secao 0: o cabecalho diz "APROVADO pelo Matheus", e o adendo 1 (o braco A fora) tambem"""
    status = [x for x in plano.splitlines() if x.startswith("**Status:")]
    if not status or not status[0].startswith("**Status: APROVADO pelo Matheus"):
        raise RuntimeError(f"o plano {PLANO} nao esta APROVADO pelo Matheus no cabecalho (secao 0): {status[:1] or 'sem a linha do status'}")
    if FORA and not any(x.startswith(STATUS_ADENDO_1) for x in plano.splitlines()):
        raise RuntimeError(f"o plano {PLANO} sem o adendo 1 APROVADO: a run tira os bracos {sorted(FORA)} (D-VAL-11)")


def exigir_faixa_reservada() -> None:
    if not any((lo, hi) == FAIXA for lo, hi, _ in FAIXAS_RESERVADAS):
        raise bv.SementeSemPlano(f"a faixa {FAIXA} nao esta em FAIXAS_RESERVADAS (secao 4)")


def modo_da_config(cfg: dict) -> str:
    """'fumaca' (as sementes dos testes, de 1 a 14 dias) ou 'valuation', que segue o plano a letra: outra base, outro K, outros dias ou
    outro orcamento falham alto, sementes fora da faixa e dos testes levantam SementeSemPlano, e o plano sem o APROVADO recusa a run"""
    faltam, sobram = (CHAVES_CONFIG - {"descricao"}) - set(cfg), set(cfg) - CHAVES_CONFIG
    if faltam or sobram:
        raise ValueError(f"config: faltam {sorted(faltam)}, sobram {sorted(sobram)}")
    if cfg["fase"] != FASE:
        raise ValueError(f"fase {cfg['fase']!r}: so {FASE!r}")
    u = cfg["unidades"]
    bases = tuple(u["bases"])
    if u.get("prefixo") != PREFIXO or cfg["orcamento_por_dia"] != ORCAMENTO_POR_DIA or type(u.get("k")) is not int or u["k"] < 1:
        raise ValueError("config fora do plano: o prefixo, o orcamento ou o K (secoes 2 e 4)")
    if bases and set(bases) <= bv.SEMENTES_TESTE:
        if not 1 <= cfg["dias"] <= DIAS:
            raise ValueError(f"fumaca com {cfg['dias']} dias: de 1 a {DIAS}")
        return "fumaca"
    if bases != BASES:
        raise bv.SementeSemPlano(f"bases {list(bases)}: so as dos testes (fumaca) ou {list(BASES)} (secao 4)")
    exigir_faixa_reservada()
    exigir_aprovado((RAIZ / PLANO).read_text(encoding="utf-8"))
    erros = [m for m, ok in ((f"dias {cfg['dias']} (o plano: {DIAS})", cfg["dias"] == DIAS), (f"plano {cfg.get('plano')!r}", cfg.get("plano") == PLANO),
                             (f"K por base {u['k']} (o plano: {K_POR_BASE})", u["k"] == K_POR_BASE)) if not ok]
    if erros:
        raise ValueError(f"a run segue o plano a letra: {erros}")
    return FASE


def tar_deterministico(pasta_vidas: Path, destino: Path) -> None:
    """o vidas.tar.gz igual byte a byte para as mesmas vidas (o da A1): nomes em ordem, mtime 0, dono 0, modo 0644, o gzip com mtime 0"""
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w", format=tarfile.PAX_FORMAT) as tar:
        for f in sorted(p for p in pasta_vidas.rglob("*") if p.is_file()):
            dados = f.read_bytes()
            info = tarfile.TarInfo(f.relative_to(pasta_vidas.parent).as_posix())
            info.size, info.mtime, info.mode, info.uid, info.gid, info.uname, info.gname = len(dados), 0, 0o644, 0, 0, "", ""
            tar.addfile(info, io.BytesIO(dados))
    with open(destino, "wb") as saida, gzip.GzipFile(filename="", mode="wb", fileobj=saida, mtime=0, compresslevel=9) as gz:
        gz.write(buf.getvalue())


def _versao_node() -> str | None:
    """a run nao usa o Node; a versao fica no meta, ou None sem o Node"""
    try:
        return subprocess.run(["node", "--version"], capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def rodar(cfg: dict, pasta: Path, processos: int, caminho_config: Path | None = None) -> dict:
    if processos > MAX_PROCESSOS:
        raise ValueError(f"no maximo {MAX_PROCESSOS} processos (V3-D8)")
    modo = modo_da_config(cfg)
    if pasta.exists():
        raise FileExistsError(f"{pasta} ja existe: a run se recusa a gravar por cima (uma vez; secao 8)")
    unidades = bv.unidades_derivadas(cfg["unidades"]["bases"], int(cfg["unidades"]["k"]), PREFIXO)
    pasta.mkdir(parents=True)
    inicio = time.time()
    rc = orq.rc
    meta = {"modo": modo, "fase": FASE, "plano": PLANO, "plano_sha256": rc._sha_arquivo(RAIZ / PLANO), "config": cfg,
            "config_arquivo": None if caminho_config is None else rc._relativo(caminho_config),
            "config_sha256": None if caminho_config is None else rc._sha_arquivo(caminho_config),
            "comando": " ".join(["python", *sys.argv]) if sys.argv and sys.argv[0] else None,
            "python": platform.python_version(), "node": _versao_node(),
            "orquestrador_sha256": rc._sha_arquivo(Path(__file__)), "prototipo_sha256": rc._sha_arquivo(Path(orq.__file__)),
            "c4_sha256": rc._sha_arquivo(Path(ma.__file__)), "longe_regular_sha256": rc._sha_arquivo(Path(lr.__file__)),
            "git_head": rc._git("rev-parse", "HEAD"), "git_limpo": rc._git("status", "--porcelain") == "", "processos": processos,
            "unidades": unidades, "celulas": [list(c) for c in CELULAS], "bracos": {b: descrever(b) for b in BRACOS}, "fora": FORA,
            "faixa": list(FAIXA),
            "sha256": {n: rc._sha_arquivo(RAIZ / "digilab" / n) for n in ("config.py", "engine.py", "metrics.py", "mundo.py")}
            | {f"digibrain/{p.name}": rc._sha_arquivo(p) for p in sorted((RAIZ / "digilab" / "digibrain").glob("*.py"))},
            "inicio": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(inicio))}
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    t0 = time.perf_counter()
    registros = [r for s in rc._executar([(tarefa, (cfg, u, str(pasta))) for u in unidades], processos) for r in s]
    meta["vidas_parede_s"] = time.perf_counter() - t0
    esperadas = len(unidades) * len(BRACOS) * len(CELULAS)
    if len(registros) != esperadas:
        raise RuntimeError(f"{len(registros)} vidas, eram {esperadas}")
    bv._gravar(pasta / "medidas.json", bv._dump([r for r in sorted(registros, key=lambda r: r["vida"])]))
    lidos = json.loads((pasta / "medidas.json").read_text(encoding="utf-8"))       # a analise sai do artefato gravado
    resultado = {"modo": modo, "fase": FASE, "plano": PLANO, "unidades": len(unidades), "vidas": len(lidos), **analisar(lidos)}
    bv._gravar(pasta / "resultado.json", bv._dump(resultado))
    nomes = ["medidas.json", "resultado.json"]
    if (pasta / "medidas.json").stat().st_size > 100 * 2**20:                          # o .gz so acima de 100 MB (o da A1)
        with open(pasta / "medidas.json", "rb") as f, open(pasta / "medidas.json.gz", "wb") as s, \
                gzip.GzipFile(filename="", mode="wb", fileobj=s, mtime=0, compresslevel=9) as gz:
            shutil.copyfileobj(f, gz)
        nomes.append("medidas.json.gz")
    tar_deterministico(pasta / "vidas", pasta / "vidas.tar.gz")
    nomes.append("vidas.tar.gz")
    meta["fim"] = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
    meta["duracao_s"] = time.time() - inicio
    meta["artefatos_sha256"] = {n: bv._sha(pasta / n) for n in nomes}
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    return {"meta": meta, "registros": registros, "resultado": resultado}


def _resumo(r: dict) -> str:
    """o resumo no console, ASCII puro (o '≈' quebra o console cp1252, o #518)"""
    return json.dumps({"modo": r["modo"], "vidas": r["vidas"], "leitura": r["leitura"],
                       "primario": {n: {k: c[k] for k in ("media", "ic95", "leitura")} for n, c in r["primario"].items()}},
                      indent=1, ensure_ascii=True, default=str)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--config", required=True)
    ap.add_argument("--saida", default=None)
    ap.add_argument("--processos", type=int, default=1)
    a = ap.parse_args()
    caminho = Path(a.config)
    cfg = json.loads(caminho.read_text(encoding="utf-8"))
    if modo_da_config(cfg) == "fumaca" and a.saida is None:
        raise SystemExit(f"a fumaca precisa de --saida (fora de {SAIDA})")
    r = rodar(cfg, Path(a.saida) if a.saida else RAIZ / SAIDA, a.processos, caminho)["resultado"]
    print(_resumo(r))


if __name__ == "__main__":
    main()
