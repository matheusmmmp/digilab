"""A run da C2 da V3, o habito com o credito na corrida do comportamento (docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md, adendo 7;
docs/TAREFA_V3_HABITO_INTENCAO.md, HI-1 a HI-8). Pergunta: o "ganhou, fica" do P2 sai ao contrario porque o credito cai no passo? As vidas
sao as da C1 (experiments/run_v2_longe_regular.py: o cenario do MVP, os 4 donos, 14 dias, 16 interacoes por dia, o motor que grava o corpo
para a C5, o G1, o T-CENARIO-1, o G-MECANISMO e o credito em toda vida, por opcao ou, no M2c, por corrida).

O desenho (A7.2 e A7.3): as celulas 4 donos x 3 lugares (`longe_fixo`, comedouro e longe), os bracos M1, M2 e M2c (o M2 com a
`credito_corrida`; SUBCHAVES_C2 do orquestrador do prototipo), todos sem o M-MEM e com a `intencao_suspensa` desligada, as bases 75101,
75202, 75303, 75404 e 75505, o prefixo `digibrain_prototipo`, K DECIDIDO (A7.6, AD7-1). A run roda uma vez, sem calibracao nem piloto.

A analise (A7.4 a A7.8), no `resultado.json`: o primario P-A (M2c - M2 no indice "ganhou, fica" de hoje, nas 8 celulas do `longe_fixo`
e do comedouro, o IC95 pelo t sobre as unidades), as premissas (P-CORRIDA e G-PESA do habito), as secundarias S1 (M2c - M1) e S2
(M2 - M1), a classe de cada contraste (A6.6, com a margem de A7.6), a leitura da tabela de 1.4 da tarefa (A7.7) e o descritivo de A7.8
(o indice da DX-5 e por acao, o do longe sorteado, o por corrida, as corridas e o H, a G-PESA, o corpo e os fins), sem gate.

A trava (A7.10): o adendo 7 APROVADO no cabecalho (`exigir_adendo_aprovado`; enquanto ele estiver PROPOSTO, a run e recusada), a faixa
75101...75505 reservada em `experiments/bancada/faixas.py`, so as bases, o K, os dias e o orcamento do adendo, no maximo 4 processos, e
nenhuma gravacao por cima de uma pasta que ja existe. Na fumaca (as sementes dos testes 101...505) a run roda sem a faixa e sem o K, com
menos dias se a config pedir.

A conferencia dos fins (a licao do #507): todo fim de intencao no registro tem de ser um dos que a `estado.py` pode dar com a config do
braco (as chaves de `EstadoDinamico.fins`), e a contagem do registro tem de ser a do proprio estado, vida a vida; senao, falha alto.

    python experiments/run_v2_habito_intencao.py --config experiments/configs/v2_habito_intencao/habito_intencao.json --processos 4
"""
from __future__ import annotations

import argparse
import json
import platform
import statistics
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402
import run_v2_longe_regular as lr  # noqa: E402
from bancada.faixas import FAIXAS_RESERVADAS  # noqa: E402
from digilab.config import CONFIG_PADRAO, TICKS_POR_DIA  # noqa: E402
from digilab.metrics import JANELA_8_14, ic_t, janela_dias, repeticao_apos_alivio  # noqa: E402

PLANO = orq.PLANO
PREFIXO = orq.PREFIXO                                                                 # A7.3 (o da reavaliacao, da L-2 e da C1)
FASE = "habito_intencao"
ADENDO = 7
BASES = (75101, 75202, 75303, 75404, 75505)                                           # A7.3 (HI-6)
K_POR_BASE = 30                                                                       # A7.6, DECIDIDO (AD7-1): 150 unidades
FAIXA = (75101, 75505)
SAIDA = "artifacts_v2_digibrain_prototipo/habito_intencao/run"                        # A7.10: a pasta-mae ja tem o adendo7_poder.json
DIAS, ORCAMENTO_POR_DIA = orq.DIAS, orq.ORCAMENTO_POR_DIA                             # A7.2
MAX_PROCESSOS = 4                                                                     # A7.9 (V3-D8)
DONOS = orq.DONOS
PRIMARIOS = ("longe_fixo", "comedouro")                                               # A7.2 (HI-2): os lugares do primario
LUGARES = PRIMARIOS + ("longe",)                                                      # o longe sorteado, so descritivo
BRACOS = ("M1", "M2", "M2c")                                                          # A7.2 (HI-1)
CELULAS = tuple((d, lu) for d in DONOS for lu in LUGARES)
CELULAS_PRIMARIO = tuple((d, lu) for d in DONOS for lu in PRIMARIOS)
CHAVES_CONFIG = lr.CHAVES_CONFIG
MARGEM = 0.011                                                                        # A7.6, DECIDIDA (AD7-1), SEM FONTE: o "~ 0"
P_CORRIDA_LIMIAR = 1.1                                                                # A7.5 (a P-CORRIDA da tarefa, 4.3), SEM FONTE
G_PESA_LIMIAR = orq.G_PESA["limiar"]                                                  # 0,01 (A7.5)
LIMIAR_G1, RESSALVA_G1 = orq.LIMIAR_G1, orq.RESSALVA_G1                               # A7.4: o g1 como em A4.4.6
ACOES_INDICE = ("comer", "explorar")                                                  # A7.8, item 1: o indice por acao (a tarefa, 4.4)
JANELAS_CORPO = lr.JANELAS_CORPO


# ================================================================== a config e a trava
def _plano() -> str:
    return (RAIZ / PLANO).read_text(encoding="utf-8")


def exigir_faixa_reservada() -> None:
    """a faixa 75101...75505 esta em FAIXAS_RESERVADAS (A7.3, A7.10); sem ela a run nao tem fonte para as sementes"""
    if not any((lo, hi) == FAIXA for lo, hi, _ in FAIXAS_RESERVADAS):
        raise bv.SementeSemPlano(f"a faixa {FAIXA[0]}...{FAIXA[1]} nao esta em FAIXAS_RESERVADAS (A7.3)")


def modo_da_config(cfg: dict) -> str:
    """'fumaca' (as sementes dos testes) ou 'habito_intencao', que segue o adendo 7 a letra (A7.10): outra base, outro K, outros dias ou
    outro orcamento falham alto, sementes fora da faixa e dos testes levantam SementeSemPlano, e o adendo sem o APROVADO recusa a run"""
    faltam, sobram = (CHAVES_CONFIG - {"descricao"}) - set(cfg), set(cfg) - CHAVES_CONFIG
    if faltam or sobram:
        raise ValueError(f"config: faltam {sorted(faltam)}, sobram {sorted(sobram)}")
    if cfg["fase"] != FASE:
        raise ValueError(f"fase {cfg['fase']!r}: so {FASE!r}")
    u = cfg["unidades"]
    bases = tuple(u["bases"])
    if u.get("prefixo") != PREFIXO or cfg["orcamento_por_dia"] != ORCAMENTO_POR_DIA or type(u.get("k")) is not int or u["k"] < 1:
        raise ValueError("config fora do plano: o prefixo (A7.3), o orcamento (A7.2) ou o K")
    if bases and set(bases) <= bv.SEMENTES_TESTE:
        if not 1 <= cfg["dias"] <= DIAS:
            raise ValueError(f"fumaca com {cfg['dias']} dias: de 1 a {DIAS}")
        return "fumaca"
    if bases != BASES:
        raise bv.SementeSemPlano(f"bases {list(bases)}: so as dos testes (fumaca) ou {list(BASES)} (A7.3)")
    exigir_faixa_reservada()
    orq.exigir_adendo_aprovado(_plano(), ADENDO)
    erros = []
    if cfg["dias"] != DIAS:
        erros.append(f"dias {cfg['dias']} (o plano: {DIAS})")
    if cfg.get("plano") != PLANO:
        erros.append(f"plano {cfg.get('plano')!r}")
    if u["k"] != K_POR_BASE:
        erros.append(f"K por base {u['k']} (o plano: {K_POR_BASE})")
    if erros:
        raise ValueError(f"a {FASE} segue o adendo {ADENDO} a letra: {erros}")
    return FASE


# ================================================================== a vida
def fins_conhecidos(braco: str) -> frozenset:
    """os fins que a `estado.py` pode dar com a config do braco: as chaves de `EstadoDinamico.fins` (a contagem que o proprio estado
    mantem; com a `intencao_cheiro`, o "achou"; com a `intencao_suspensa`, os da L-2). A lista nao e escrita a mao (a licao do #507); quem monta o estado e o `orq.fins_do_estado`."""
    return orq.fins_do_estado(braco)


def conferir_fins(braco: str, registro) -> dict:
    """A7.8, item 6: os fins das intencoes da vida, por motivo. Falha alto com um fim que a `estado.py` nao da com a config do braco, com
    a contagem do registro diferente da do estado (`EstadoDinamico.fins`), ou com uma retomada ou um `n_susp` (a `intencao_suspensa` fica
    desligada em todos os bracos, A7.2)."""
    c = orq.cerebro_de(registro)
    if c.cd.intencao_suspensa:
        raise RuntimeError(f"{braco}: a intencao_suspensa esta ligada (A7.2: a C2 roda com ela desligada)")
    conhecidos = fins_conhecidos(braco)
    contagem = {m: 0 for m in sorted(conhecidos)}
    for k, m in enumerate(c.motivos):
        if m.get("retomou"):
            raise RuntimeError(f"{braco}, decisao {k}: uma retomada com a intencao_suspensa desligada")
        for f in m["fins"]:
            if "n_susp" in f:
                raise RuntimeError(f"{braco}, decisao {k}: uma intencao com n_susp com a intencao_suspensa desligada")
            if f["motivo"] not in conhecidos:
                raise RuntimeError(f"{braco}, decisao {k}: o fim {f['motivo']!r} nao e dos conhecidos {sorted(conhecidos)}")
            contagem[f["motivo"]] += 1
    if contagem != dict(sorted(c.m.estado.fins.items())):
        raise RuntimeError(f"{braco}: os fins do registro {contagem} nao sao os do estado {dict(sorted(c.m.estado.fins.items()))}")
    return contagem


def corridas_da_vida(registro) -> list[dict]:
    """as corridas do comportamento da vida (A7.5 e A7.8), a mesma definicao em todo braco: as decisoes seguidas do mesmo `escolha[0]`,
    com o r = a soma dos r_n delas cortada em [-S, S] a cada soma (a do `estado.py`, 3.1 da tarefa). So as fechadas por uma troca de
    comportamento (a aberta no fim da vida fica fora, como no credito). No M2c elas sao, uma a uma, as entregues ao P2 (conferido)."""
    c = orq.cerebro_de(registro)
    S, ms = c.S, c.motivos
    out, atual = [], None
    for k, m in enumerate(ms):
        b = m["escolha"][0]
        if atual is not None and atual["b"] == b:
            atual["n"] += 1
        else:
            if atual is not None:
                out.append(atual)
            atual = {"b": b, "inicio": k, "n": 1, "r": 0}
        if m["consequencia"] is None:          # so a ultima decisao da vida, que fica na corrida aberta (fora do credito)
            if k != len(ms) - 1:
                raise RuntimeError(f"a decisao {k} sem a consequencia")
            continue
        atual["r"] = max(-S, min(S, atual["r"] + m["consequencia"]["r_n"]))
    if c.cd.credito_corrida:
        entregues = [{"b": x["b"], "inicio": x["inicio"], "n": x["n"], "r": x["r"]} for m in ms for x in m["corridas"]]
        if entregues != out:
            raise RuntimeError("as corridas entregues ao P2 nao sao as da vida, uma a uma")
    return out


def medidas_corridas(registro, dias: int) -> dict:
    """A7.5 e A7.8, itens 3 e 4: as corridas (o numero, as decisoes nelas e, por comportamento, o numero e as decisoes), o indice
    "ganhou, fica" por corrida (o `repeticao_apos_alivio` sobre as corridas: o tick e o contexto da primeira decisao, o comportamento e o r
    da corrida; a janela dos dias 8 a 14 na primeira decisao da corrida de antes), os creditos do P2 e a norma L1 do H por comportamento
    no fim, na escala S"""
    c = orq.cerebro_de(registro)
    passo = CONFIG_PADRAO.intervalo_decisao_ticks
    ms = c.motivos
    cs = corridas_da_vida(registro)
    por_b: dict = {}
    for x in cs:
        p = por_b.setdefault(x["b"], {"corridas": 0, "decisoes": 0})
        p["corridas"] += 1
        p["decisoes"] += x["n"]
    janela = JANELA_8_14 if dias >= 14 else janela_dias(1, dias)
    rep = [(x["inicio"] * passo, orq._contexto_ganhou_fica(ms[x["inicio"]]), x["b"], x["r"]) for x in cs]
    S = c.S
    return {"n": len(cs), "decisoes": sum(x["n"] for x in cs), "media_n": statistics.fmean(x["n"] for x in cs) if cs else None,
            "por_comportamento": dict(sorted(por_b.items())), "indice_por_corrida": orq._rep_curto(repeticao_apos_alivio(rep, janela)),
            "creditos_p2": c.m.plast.creditos,
            "h_norma_l1": {b: sum(abs(v) for v in linha) / S for b, linha in sorted(c.m.plast.H.items())}}


def _vida(cfg: dict, braco: str, dono: str, lugar: str, unidade: dict, pasta: str) -> dict:
    """uma vida: vivida (o motor da C1, que grava o corpo), gravada, rejogada do disco (G1), conferida (as falhas altas, os fins) e medida"""
    c0, p0 = time.process_time(), time.perf_counter()
    motor, registro, fab = lr.viver(braco, dono, lugar, unidade["semente"], cfg["dias"], cfg["orcamento_por_dia"])
    arquivo = Path(pasta) / "vidas" / braco / f"{dono}_{lugar}_{unidade['semente']}.jsonl"
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    arquivo.write_text(motor.log.para_jsonl(), encoding="utf-8", newline="\n")
    orq.conferir_replay(motor, fab, unidade["semente"], arquivo.read_text(encoding="utf-8"))
    orq.conferir_cenario(motor, registro)
    orq.conferir_mecanismo(braco, registro, None)
    fins = conferir_fins(braco, registro)
    med = orq.medidas(motor, registro, braco, cfg["dias"], True)
    return {"vida": f"{braco}|{dono}|{lugar}|{unidade['semente']}", "braco": braco, "dono": dono, "lugar": lugar,
            "semente": unidade["semente"], "base": unidade["base"], "k": unidade["k"], **med,
            "corpo": lr.medidas_do_corpo(motor, registro, cfg["dias"]), "fins_conferidos": fins,
            "corridas": medidas_corridas(registro, cfg["dias"]),
            "custo": {"vida_cpu": time.process_time() - c0, "vida_parede": time.perf_counter() - p0}}


def tarefa(cfg: dict, unidade: dict, pasta: str) -> list[dict]:
    return [_vida(cfg, b, dono, lugar, unidade, pasta) for b in BRACOS for dono, lugar in CELULAS]


# ================================================================== a analise
def _celulas(lugares: tuple) -> tuple:
    return tuple((d, lu) for d in DONOS for lu in lugares)


def nivel(registros: list[dict], braco: str, medida, lugares: tuple = PRIMARIOS) -> dict:
    """{(base, semente): a media da medida nas celulas dos lugares} (a unidade de A7.4)"""
    return orq.por_unidade(registros, braco, None, medida, _celulas(lugares))


def diferenca(registros: list[dict], a: str, b: str, medida, lugares: tuple = PRIMARIOS) -> dict:
    """{(base, semente): a media, nas celulas dos lugares, de medida(a) - medida(b) na mesma celula} (as celulas com None num dos bracos
    ficam fora, a regra do `por_unidade`)"""
    return orq.por_unidade(registros, a, b, medida, _celulas(lugares))


def classe(ic: dict, margem: float = MARGEM) -> dict:
    """a classe de A6.6 (A7.6), na ordem, com a margem deste adendo"""
    return lr.classe(ic, margem)


def estimativa(difs: dict, margem: float = MARGEM) -> dict:
    """o descritivo de um valor por unidade: a media, o dp e o IC95 pelo t (A4.4.6) sobre as unidades, com a classe de A6.6"""
    ic = ic_t([v for _, v in sorted(difs.items())])
    return {"n": ic["n"], "media": ic["media"], "dp": ic["dp"], "ic95": {"ic_inferior": ic["ic_inferior"], "ic_superior": ic["ic_superior"]},
            "classe": classe(ic, margem), "motivo": ic["motivo"]}


INDICE = lambda r: r["repeticao"]["indice"]                                     # noqa: E731
INDICE_DX5 = lambda r: r["repeticao_r_possivel"]["total"]["indice"]             # noqa: E731
INDICE_CORRIDA = lambda r: r["corridas"]["indice_por_corrida"]["indice"]        # noqa: E731
EPISODIO = lr.EPISODIO


def _contraste(registros: list[dict], a: str, b: str, rotulo: str, boot: dict) -> dict:
    difs = diferenca(registros, a, b, INDICE)
    c = orq.contraste_t(difs, boot)
    ic = {"ic_inferior": c["ic95"]["ic_inferior"], "ic_superior": c["ic95"]["ic_superior"], "motivo": c["motivo"]}
    return {"contraste": rotulo, **c, "classe": classe(ic), "margem": MARGEM, "margem_efetiva": lr.margem_efetiva(estimativa(difs)["dp"], c["n"])}


def primario(registros: list[dict], boot: dict) -> dict:
    """A7.4: o P-A, M2c - M2 no indice de hoje, nas 8 celulas do `longe_fixo` e do comedouro, o IC95 pelo t sobre as unidades; passa se o
    limite inferior > 0. Ao lado: o p unilateral, o g1 com a ressalva, o IC percentil do bootstrap (rotulado) e a margem efetiva."""
    c = _contraste(registros, "M2c", "M2", "P-A: M2c - M2, o indice 'ganhou, fica' de hoje, nas 8 celulas do longe_fixo e do comedouro", boot)
    return {**c, "passa": c["ic95"]["ic_inferior"] is not None and c["ic95"]["ic_inferior"] > 0}


def secundarias(registros: list[dict], boot: dict) -> dict:
    """A7.4: S1 (M2c - M1, previsao > 0) e S2 (M2 - M1, sem previsao de sinal), as mesmas celulas e o mesmo teste, sem gate"""
    return {"S1": {**_contraste(registros, "M2c", "M1", "S1: M2c - M1, o indice de hoje, nas 8 celulas", boot), "previsao": "> 0"},
            "S2": {**_contraste(registros, "M2", "M1", "S2: M2 - M1, o indice de hoje, nas 8 celulas", boot), "previsao": None}}


def premissas(registros: list[dict]) -> dict:
    """A7.5: a P-CORRIDA (no M2c, nas 8 celulas, a media das decisoes por corrida creditada na vida, por unidade; o limite inferior do
    IC95 pelo t > 1,1) e a G-PESA do habito (no M2c, nas 8 celulas, a fracao das decisoes com `habito_decidiu`; o limite inferior > 0,01).
    Se uma falha, o primario e inconclusivo por premissa."""
    corrida = estimativa(nivel(registros, "M2c", lambda r: r["corridas"]["media_n"]))
    corrida["passa"] = corrida["ic95"]["ic_inferior"] is not None and corrida["ic95"]["ic_inferior"] > P_CORRIDA_LIMIAR
    corrida["limiar"] = P_CORRIDA_LIMIAR
    pesa = estimativa(nivel(registros, "M2c", lambda r: r["influencia"]["habito"]))
    pesa["passa"] = pesa["ic95"]["ic_inferior"] is not None and pesa["ic95"]["ic_inferior"] > G_PESA_LIMIAR
    pesa["limiar"] = G_PESA_LIMIAR
    return {"P-CORRIDA": corrida, "G-PESA-habito": pesa, "conclusivo": corrida["passa"] and pesa["passa"]}


def leitura(prim: dict, prem: dict, s1: dict) -> dict:
    """A7.7, a tabela da secao 1.4 da tarefa, na ordem (a primeira linha que serve). No P-A o primario manda: '> 0' e o primario passar;
    senao a classe de A6.6. O S1 entra pela classe de A6.6."""
    pa = "> 0" if prim["passa"] else prim["classe"]["classe"]
    sec = s1["classe"]["classe"]
    base = {"P-A": pa, "S1": sec, "ressalva_primario": prim["ressalva_assimetria"]}
    if not prem["conclusivo"]:
        return {**base, "linha": "inconclusivo por premissa (A7.5): a corrida nao ficou mais longa que o passo, ou o habito nao pesou; "
                                 "nada se decide", "o_que_se_faz": "registrado; nada se decide"}
    if pa == "> 0" and sec == "> 0":
        return {**base, "linha": "nestas condicoes, o credito no passo explica a falha: com a corrida, o habito faz o que se previa",
                "o_que_se_faz": "a corrida vira candidata a substituir o credito de hoje; volta ao Matheus. Nao vai ao jogo sem a L3"}
    if pa == "> 0":
        return {**base, "linha": "o credito no passo explica parte da falha, mas o habito ainda nao sobe o 'ganhou, fica' acima do sem-habito",
                "o_que_se_faz": "registrado; a C3 (o gatilho) fica como o proximo teste, em separado"}
    if pa == "≈ 0":
        return {**base, "linha": "nestas condicoes, a unidade de credito nao e a causa. Fica a H-P2a: o indice mede a sensibilidade ao resultado",
                "o_que_se_faz": "volta ao Matheus a medida do P2, nao um mecanismo novo"}
    if pa == "< 0":
        return {**base, "linha": "a corrida piora o indice", "o_que_se_faz": "registrado como esta; a corrida fica fora"}
    return {**base, "linha": "registrado como indeterminado; nada se decide", "o_que_se_faz": "registrado como indeterminado"}


# ------------------------------------------------------------------ o descritivo (A7.8; sem gate)
PARES = (("M2c", "M2"), ("M2c", "M1"), ("M2", "M1"))


def _contrastes(registros: list[dict], medida, lugares_por=("primario",) + LUGARES, pares=PARES) -> dict:
    """os contrastes por par de bracos, nas 8 celulas do primario e em cada lugar, com a classe de A6.6"""
    alvo = {"primario": PRIMARIOS, **{lu: (lu,) for lu in LUGARES}}
    return {f"{lu}|{a} - {b}": estimativa(diferenca(registros, a, b, medida, alvo[lu])) for lu in lugares_por for a, b in pares}


def _niveis(registros: list[dict], medida, bracos: tuple = BRACOS) -> dict:
    alvo = {"primario": PRIMARIOS, **{lu: (lu,) for lu in LUGARES}}
    return {f"{lu}|{b}": estimativa(nivel(registros, b, medida, alvo[lu])) for lu in alvo for b in bracos}


def indices(registros: list[dict]) -> dict:
    """A7.8, itens 1 a 3: o indice de hoje por lugar (o longe sorteado, onde o G-ABLA-P2 falhou, entra aqui), o da DX-5 (so as acoes com
    r possivel) no total e por acao (comer e explorar), e o indice por corrida; os niveis por braco e os contrastes dos tres pares"""
    por_acao = {a: (lambda r, a=a: r["repeticao_r_possivel"]["por_acao"][a]["indice"]) for a in ACOES_INDICE}
    return {"de_hoje": {"niveis": _niveis(registros, INDICE), "contrastes": _contrastes(registros, INDICE)},
            "dx5_total": {"niveis": _niveis(registros, INDICE_DX5), "contrastes": _contrastes(registros, INDICE_DX5)},
            "dx5_por_acao": {a: {"niveis": _niveis(registros, f), "contrastes": _contrastes(registros, f)} for a, f in por_acao.items()},
            "por_corrida": {"niveis": _niveis(registros, INDICE_CORRIDA), "contrastes": _contrastes(registros, INDICE_CORRIDA)}}


def corridas_e_h(registros: list[dict]) -> dict:
    """A7.8, item 4: o comprimento medio das corridas e os creditos do P2 por vida, o H no teto (`pesos_no_teto`) e a norma L1 do H por
    comportamento no fim, por braco e lugar; as corridas por comportamento (um grupo que a propria corrida cria: so somadas por braco e
    lugar, sem contraste; a LP-2)"""
    comportamentos = sorted({b for r in registros for b in r["corridas"]["h_norma_l1"]})
    por_b = {}
    for lu in LUGARES:
        for b in BRACOS:
            vs = [r["corridas"]["por_comportamento"] for r in registros if r["lugar"] == lu and r["braco"] == b]
            soma = {}
            for v in vs:
                for c, x in v.items():
                    s = soma.setdefault(c, {"corridas": 0, "decisoes": 0})
                    s["corridas"] += x["corridas"]
                    s["decisoes"] += x["decisoes"]
            por_b[f"{lu}|{b}"] = {c: {**s, "media_n": s["decisoes"] / s["corridas"]} for c, s in sorted(soma.items())}
    return {"media_n": _niveis(registros, lambda r: r["corridas"]["media_n"]),
            "creditos_p2": _niveis(registros, lambda r: r["corridas"]["creditos_p2"], ("M2", "M2c")),
            "pesos_no_teto": _niveis(registros, lambda r: r["pesos_no_teto"], ("M2", "M2c")),
            "h_norma_l1": {c: _niveis(registros, lambda r, c=c: r["corridas"]["h_norma_l1"][c], ("M2", "M2c")) for c in comportamentos},
            "por_comportamento_somado": por_b}


def corpo(registros: list[dict]) -> dict:
    """A7.8, item 5: a taxa de fechamento por episodio (a do adendo 6) e as medidas da C5 (AD6-4, como estao), em nivel e nos contrastes
    dos tres pares; a privacao de hoje ao lado"""
    out = {"limiar": lr.LIMIAR_CORPO, "status": "as definicoes da AD6-4, DECIDIDAS, SEM FONTE",
           "episodio": {"niveis": _niveis(registros, EPISODIO), "contrastes": _contrastes(registros, EPISODIO)},
           "privacao_de_hoje": {"niveis": _niveis(registros, lambda r: r["privacao"])}}
    for j in JANELAS_CORPO:
        for m in ("fracao_fora", "menor_media", "menor_minimo"):
            f = lambda r, j=j, m=m: r["corpo"][j][m]          # noqa: E731
            out[f"{j}|{m}"] = {"niveis": _niveis(registros, f), "contrastes": _contrastes(registros, f)}
    return out


def outros(registros: list[dict]) -> dict:
    """A7.8, item 6: a G-PESA do habito por braco e lugar (M2 e M2c), os fins das intencoes somados por braco e lugar, os episodios por
    vida, a exaustao; por dono, so a media do indice de hoje"""
    fins = {}
    for lu in LUGARES:
        for b in BRACOS:
            soma: dict = {}
            for r in registros:
                if r["lugar"] == lu and r["braco"] == b:
                    for m, n in r["fins_conferidos"].items():
                        soma[m] = soma.get(m, 0) + n
            fins[f"{lu}|{b}"] = dict(sorted(soma.items()))
    por_dono = {}
    for d in DONOS:
        for lu in LUGARES:
            for b in BRACOS:
                vs = [INDICE(r) for r in registros if r["dono"] == d and r["lugar"] == lu and r["braco"] == b and INDICE(r) is not None]
                if vs:
                    por_dono[f"{d}|{lu}|{b}"] = statistics.fmean(vs)
    return {"g_pesa_habito": _niveis(registros, lambda r: r["influencia"]["habito"], ("M2", "M2c")),
            "fins_somados": fins, "episodios_por_vida": _niveis(registros, lambda r: r["episodios_fome"]["n"]),
            "exaustao": _niveis(registros, lambda r: r["exaustao"]), "indice_por_dono": por_dono,
            "celulas_sem_indice": {f"{lu}|{b}": sum(1 for r in registros if r["lugar"] == lu and r["braco"] == b and INDICE(r) is None)
                                   for lu in LUGARES for b in BRACOS}}


def analisar(registros: list[dict], boot: dict = orq.BOOTSTRAP) -> dict:
    """a analise de A7.4 a A7.8, com a classe de cada contraste e a leitura"""
    prim, sec, prem = primario(registros, boot), secundarias(registros, boot), premissas(registros)
    return {"primario": prim, "secundarias": sec, "premissas": prem, "leitura": leitura(prim, prem, sec["S1"]),
            "descritivo": {"indices": indices(registros), "corridas_e_h": corridas_e_h(registros), "corpo": corpo(registros),
                           "outros": outros(registros)},
            "nao_demonstra": ["que o modular supera o A", "prontidao do prototipo", "tamanho de efeito fora das condicoes da run",
                              "o efeito do gatilho de reavaliacao (a C3)"]}


# ================================================================== a run
def rodar(cfg: dict, pasta: Path, processos: int, caminho_config: Path | None = None) -> dict:
    if processos > MAX_PROCESSOS:
        raise ValueError(f"no maximo {MAX_PROCESSOS} processos (a maquina; V3-D8 e A7.9)")
    modo = modo_da_config(cfg)
    if pasta.exists():
        raise FileExistsError(f"{pasta} ja existe: a run se recusa a gravar por cima (uma vez; A7.10)")
    unidades = bv.unidades_derivadas(cfg["unidades"]["bases"], int(cfg["unidades"]["k"]), PREFIXO)
    pasta.mkdir(parents=True)
    inicio = time.time()
    rc = orq.rc
    meta = {"modo": modo, "fase": FASE, "plano": PLANO, "plano_sha256": rc._sha_arquivo(RAIZ / PLANO), "config": cfg,
            "config_arquivo": None if caminho_config is None else rc._relativo(caminho_config),
            "config_sha256": None if caminho_config is None else rc._sha_arquivo(caminho_config),
            "orquestrador_sha256": rc._sha_arquivo(Path(__file__)), "prototipo_sha256": rc._sha_arquivo(Path(orq.__file__)),
            "longe_regular_sha256": rc._sha_arquivo(Path(lr.__file__)),
            "git_head": rc._git("rev-parse", "HEAD"), "git_limpo": rc._git("status", "--porcelain") == "", "processos": processos,
            "unidades": unidades, "celulas": [list(c) for c in CELULAS],
            "bracos": {b: {**orq.SUBCHAVES_CONSERTO, **orq.SUBCHAVES_C2}[b] for b in BRACOS},
            "fins_conhecidos": {b: sorted(fins_conhecidos(b)) for b in BRACOS},
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
    bv._gravar(pasta / "medidas.json", bv._dump({r["vida"]: r for r in sorted(registros, key=lambda r: r["vida"])}))
    lidos = json.loads((pasta / "medidas.json").read_text(encoding="utf-8"))       # a analise sai do artefato gravado
    resultado = {"modo": modo, "fase": FASE, "plano": PLANO, "unidades": len(unidades), "vidas": len(lidos),
                 **analisar(list(lidos.values()))}
    bv._gravar(pasta / "resultado.json", bv._dump(resultado))
    meta["fim"] = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
    meta["duracao_s"] = time.time() - inicio
    meta["python"] = platform.python_version()
    meta["artefatos_sha256"] = {n: bv._sha(pasta / n) for n in ("medidas.json", "resultado.json")}
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    return {"meta": meta, "registros": registros, "resultado": resultado}


def _imprimir_resumo(r: dict) -> None:
    """O resumo no console: ASCII puro (ensure_ascii), para nao quebrar num console cp1252 com '≈' na leitura; os artefatos gravados nao passam por aqui."""
    print(json.dumps({k: r[k] for k in ("modo", "vidas", "primario", "secundarias", "premissas", "leitura")}, indent=1, ensure_ascii=True,
                     default=str)[:4000])


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
    saida = Path(a.saida) if a.saida else RAIZ / SAIDA
    r = rodar(cfg, saida, a.processos, caminho)["resultado"]
    _imprimir_resumo(r)


if __name__ == "__main__":
    main()
