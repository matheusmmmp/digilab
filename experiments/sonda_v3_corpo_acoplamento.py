"""CORPO_ACOPLAMENTO, etapa 1 (docs/TAREFA_V3_CORPO_ACOPLAMENTO.md): por que a energia baixa e a fome urgente coincidem? So descritiva.

A VALUATION achou que, no REL, 63,5 % das decisoes com a energia abaixo de `lambda_sono` (S/4) tem a fome urgente (a urgencia da fome
do M-AFETO acima do `urgencia_lambda`; docs/RESULTADO_V3_VALUATION_CONSERTO.md, secao 3). Esta sonda refaz a mesma vida (a do
`run_v3_valuation_conserto.viver`: o MotorGravaCorpo, o pet sozinho, 14 dias, orcamento 16, as 12 celulas da C4) com as sementes dos
testes (101, 202, 303, 404, 505) e corta as decisoes com as duas por causa.

A instrumentacao so le: o corpo da vida ganha, na instancia, invólucros que anotam de onde vem cada variacao do cansaco (o basal do dia,
o da noite, o descanso do sono, a falta de combustivel, as atividades do pet, o andar e o brincar do dono) e cada ingestao. Os
invólucros chamam o metodo de sempre, sem tocar em rng nem no estado; o teste confere que o log sai byte a byte o da vida sem eles. Uma
variacao do cansaco sem fonte conhecida falha alto, e a soma das fontes tem de dar o cansaco de cada decisao, exata.

O corte (a secao 1 da tarefa), decisao a decisao. Para cada decisao com as duas, a janela vai da ultima decisao descansada (o cansaco ate
C/2, a energia em S/2 ou mais) ate ela, e o cansaco que entrou na janela se reparte em quatro fontes: o `tempo_acordado` (o basal do dia
e o da noite), a `falta_combustivel` (a ponte ME-1), as `atividades` (o brincar e o explorar do pet e o brincar do dono) e o `andar`. A
classe da decisao e a fonte que mais pos cansaco na janela (o empate vai a primeira, nesta ordem: falta, atividades, andar, tempo); a
`parte_media` e a fracao media de cada fonte. Ao lado, sem ordem, as marcas (cada uma e uma fracao das decisoes com as duas):
  - `fome_antes`: a fome ja estava urgente na entrada do trecho cansado (as decisoes seguidas com a energia baixa) e assim seguiu ate a
    decisao; senao a fome veio depois, dentro do trecho;
  - `dormindo`, `combustivel_em_falta` (abaixo do `falta_limiar`, a ponte ligada) e `fome_no_teto` (a falta da fome em C);
  - `adiou`: desde que a fome ficou urgente, o pet viu comida e escolheu outra coisa que nao o comer;
  - `andar_na_fome`: sem o andar desde que a fome ficou urgente, a decisao nao teria a energia baixa (a comida longe);
  - `<fonte>_necessaria`: sem essa fonte na janela, a decisao nao teria a energia baixa (uma conta aditiva: o corte em 0 e em C fica de
    fora; perto do limiar quase toda fonte e necessaria, por isso a classe vai pela parte, nao por aqui).
Ao lado ainda: o balanco do metabolismo (as contas do corpo e a comida descartada com a fome em zero), o cansaco por fonte por dia e a
subida da fome por tick, dormindo e acordado.

Uso: python experiments/sonda_v3_corpo_acoplamento.py [--chave-d] [--saida <arquivo>]
  (sem a chave: sonda.json, a etapa 1; com --chave-d: sonda_chave_d.json, a etapa 2, a opcao D ligada)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import run_v2_longe_regular as lr  # noqa: E402
import run_v3_valuation_conserto as VC  # noqa: E402
from bancada.regras_mundo import simular_vida_fisico  # noqa: E402
from digilab.config import CONFIG_ACOPLAMENTO_CORPO_LIGADA, CONFIG_PADRAO, TICKS_POR_DIA, ConfigAcoplamentoCorpo  # noqa: E402
from digilab.corpo import div_arred  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.mundo import DonoComLugar  # noqa: E402
from digilab.temperamento import NEUTRO  # noqa: E402

SEMENTES = (101, 202, 303, 404, 505)          # as dos testes (CLAUDE.md): nenhuma faixa de pesquisa
BRACOS = ("REL", "CON")                       # o REL e a vida de hoje; o CON (a chave do conserto ligada) so ao lado
CELULAS = VC.CELULAS
DIAS, ORCAMENTO_POR_DIA = VC.DIAS, VC.ORCAMENTO_POR_DIA
SAIDA = "artifacts_v3_corpo_acoplamento/sonda.json"
SAIDA_CHAVE = "artifacts_v3_corpo_acoplamento/sonda_chave_d.json"
C_CORPO = 450000                              # a escala C do corpo (ConfigCorpo.escala); conferida em cada vida
CORPO_CONFERIDO = ("gasto_basal_acordado", "gasto_basal_dormindo", "gasto_atividades_num", "gasto_atividades_den", "falta_limiar",
                   "falta_cansaco", "conversao_num", "conversao_den")
FONTES_BASAL = {"dia": "basal_dia", "noite": "basal_noite", "dormindo": "sono"}
FONTES = ("basal_dia", "basal_noite", "sono", "falta_combustivel", "atividades", "andar", "outros")
CLASSES = ("falta_combustivel", "atividades", "andar", "tempo_acordado")
LADOS = ("fome_antes", "dormindo", "combustivel_em_falta", "fome_no_teto", "nunca_descansou", "adiou", "andar_na_fome",
         "falta_combustivel_necessaria", "atividades_necessarias", "andar_necessario")
ATIVIDADES_PET = ("brincar", "explorar")


# ================================================================== a instrumentacao (so le)
class Contabil:
    """o cansaco por fonte, acumulado, e as ingestoes; os invólucros na instancia do corpo chamam o metodo de sempre"""

    def __init__(self, corpo) -> None:
        self.corpo = corpo
        self.acum = {f: 0 for f in FONTES}
        self.ingerido = 0
        self.ctx: list[str] = []
        self.ticks_falta = 0
        o_somar, o_passo, o_pet, o_dono, o_andar, o_ingerir = (corpo._somar, corpo.passo, corpo.acao_pet, corpo.acao_dono,
                                                               corpo.estimulo_andar, corpo._ingerir)
        cfg = corpo.cfg

        def somar(deltas, rubrica="gasto_atividade"):
            antes = corpo.q["cansaco"]
            o_somar(deltas, rubrica)
            d = corpo.q["cansaco"] - antes
            if d:
                if not self.ctx:
                    raise RuntimeError(f"sonda: o cansaco mudou {d} sem fonte conhecida (deltas {deltas})")
                topo = self.ctx[-1]
                if topo.startswith("passo:"):
                    fonte = FONTES_BASAL[topo[6:]] if rubrica == "gasto_basal" else "falta_combustivel"
                else:
                    fonte = topo
                if fonte == "falta_combustivel":
                    self.ticks_falta += 1
                self.acum[fonte] += d

        def passo(antes, *a, **k):
            noite = cfg.e_noite(antes.tick % TICKS_POR_DIA)
            self.ctx.append("passo:" + ("dormindo" if antes.dormindo else ("noite" if noite else "dia")))
            try:
                return o_passo(antes, *a, **k)
            finally:
                self.ctx.pop()

        def com(fonte, f):
            def g(*a, **k):
                self.ctx.append(fonte(*a) if callable(fonte) else fonte)
                try:
                    return f(*a, **k)
                finally:
                    self.ctx.pop()
            return g

        def ingerir(q):
            self.ingerido += q
            return o_ingerir(q)

        corpo._somar = somar
        corpo.passo = passo
        corpo.acao_pet = com(lambda acao, *a: "atividades" if acao.value in ATIVIDADES_PET else "outros", o_pet)
        corpo.acao_dono = com(lambda acao, *a: "atividades" if acao.value == "brincar" else "outros", o_dono)
        corpo.estimulo_andar = com("andar", o_andar)
        corpo._ingerir = ingerir


class MotorSonda(lr.MotorGravaCorpo):
    """o MotorGravaCorpo com a contabilidade do cansaco no corpo; guarda, no comeco de cada tick (o que a decisao do tick ve), o cansaco,
    a fome, o combustivel, o sono, o acumulado por fonte e o ingerido"""

    def __init__(self, *a, **k) -> None:
        super().__init__(*a, **k)
        self.contabil = Contabil(self.corpo)
        self.serie_sonda: list[tuple] = []

    def _laco(self, ticks: int):
        produzidas: list = []
        for _ in range(ticks):
            if self.corpo is not self.contabil.corpo:
                raise RuntimeError("sonda: o motor trocou o corpo; a contabilidade ficaria de fora")
            q, c = self.corpo.q, self.contabil
            self.serie_sonda.append((self._estado.tick, q["cansaco"], q["fome"], q["combustivel"], bool(self._estado.dormindo),
                                     dict(c.acum), c.ingerido))
            produzidas.extend(super()._laco(1))
        return produzidas


def viver(braco: str, dono: str, lugar: str, semente: int, dias: int = DIAS, orcamento_por_dia: int = ORCAMENTO_POR_DIA,
          instrumentar: bool = True, cfg_acoplamento: ConfigAcoplamentoCorpo | None = None):
    """a vida do `run_v3_valuation_conserto.viver` (o mesmo cerebro, o mesmo motor, o mesmo dono), com o MotorSonda no lugar do
    MotorGravaCorpo quando `instrumentar`. `cfg_acoplamento` (a etapa 2, a opcao D) vai ao motor; sem ela, nada muda. Devolve (o motor,
    o registro, a energia baixa de cada decisao)."""
    fp, fm0 = VC.fabricas(braco, dono, semente, dias, orcamento_por_dia)
    cc = VC.orq.bancada(dias, orcamento_por_dia).cfg_corpo_de(VC.bv.EspecVida(dono, VC.gl.BRACO_V11, semente))

    extra = {} if cfg_acoplamento is None else {"cfg_acoplamento_corpo": cfg_acoplamento}

    def fm(politica, cfg, s):
        if not instrumentar and not extra:
            return fm0(politica, cfg, s)
        classe = MotorSonda if instrumentar else lr.MotorGravaCorpo
        return classe(politica, cfg, s, NEUTRO, "brasa", obediencia_desligada=True, cfg_mundo=VC.orq.CM, cfg_corpo=cc, **extra)

    registro = fp(CONFIG_PADRAO)
    c = VC.orq.cerebro_de(registro)
    reflexo = c.m.arb.reflexo
    baixas: list[bool] = []

    def reflexo_e_ler(sens, urgencias=None):
        baixas.append(sens["leitura"]["energia"] < c.inatos.lambda_sono)
        return reflexo(sens, urgencias)

    c.m.arb.reflexo = reflexo_e_ler
    d = DonoComLugar(criar_dono(dono), lugar, semente, dono, VC.orq.CM)
    motor, _ = simular_vida_fisico(d, registro, semente, dias, orcamento_por_dia * dias, dono, fm)
    del c.m.arb.reflexo
    return motor, registro, baixas


# ================================================================== o corte (puro, sobre as series)
def limiar_cansaco(C: int, S: int, lambda_sono: int) -> int:
    """o menor cansaco (em C) com a leitura da energia (S - div_arred(q S, C)) abaixo de `lambda_sono`"""
    lo, hi = 0, C
    while lo < hi:
        m = (lo + hi) // 2
        if S - div_arred(m * S, C) < lambda_sono:
            hi = m
        else:
            lo = m + 1
    return lo


def decisoes_da_vida(motor, registro, baixas: list[bool]) -> list[dict]:
    """uma linha por decisao: a energia baixa (a leitura do reflexo), a fome urgente (o motivo), o sono, a acao, a comida vista, o
    cansaco, a fome, o combustivel e o acumulado por fonte no tick da decisao. Confere a contabilidade e a energia baixa."""
    c = VC.orq.cerebro_de(registro)
    passo = CONFIG_PADRAO.intervalo_decisao_ticks
    serie = motor.serie_sonda
    if len(baixas) != len(c.motivos):
        raise RuntimeError(f"sonda: {len(baixas)} leituras do reflexo para {len(c.motivos)} decisoes")
    corpo = motor.corpo
    C, S = corpo.C, corpo.S
    lim = limiar_cansaco(C, S, c.inatos.lambda_sono)
    lam = c.inatos.urgencia_lambda
    q0 = serie[0][1]
    out = []
    for k, (x, baixa) in enumerate(zip(c.motivos, baixas)):
        tick, cansaco, fome, comb, dormindo, acum, ingerido = serie[k * passo]
        if tick != k * passo or x["k"] != k:
            raise RuntimeError(f"sonda: a decisao {k} nao caiu no tick {k * passo}")
        if q0 + sum(acum.values()) != cansaco:
            raise RuntimeError(f"sonda: as fontes nao somam o cansaco na decisao {k}: {q0} + {acum} != {cansaco}")
        if (cansaco >= lim) != baixa:
            raise RuntimeError(f"sonda: a energia baixa da decisao {k} ({baixa}) nao bate com o cansaco {cansaco} (limiar {lim})")
        out.append({"k": k, "baixa": baixa, "urgente": x["afeto"]["urgencias"]["fome"] > lam, "dormindo": dormindo,
                    "acao": x["acao"], "comida_vista": bool(x["contexto"]["comida_vista"]), "cansaco": cansaco, "fome": fome,
                    "combustivel": comb, "acum": acum, "ingerido": ingerido})
    return out


def cortar(dec: list[dict], lim: int, C: int, falta_limiar: int) -> dict:
    """o corte por causa das decisoes com as duas (a docstring do modulo). Puro: so le as linhas."""
    n = len(dec)
    metade = C // 2                                     # descansado: o cansaco ate C/2 (a energia em S/2 ou mais)
    cont = {cl: 0 for cl in CLASSES}
    cruz = {cl: {"fome_antes": 0, "fome_depois": 0} for cl in CLASSES}
    lados = {k: 0 for k in LADOS}
    desde_comer, janelas = [], []
    parte = {cl: 0.0 for cl in CLASSES}
    n_baixa = n_ambas = baixa_sem_fome_em_falta = 0
    entrada = None                                       # a entrada do trecho cansado corrente
    ultima_comida = None                                 # a ultima decisao em que o ingerido subiu
    r = 0                                                # a ultima decisao descansada
    u = None                                             # o comeco da fome urgente corrente
    for d, x in enumerate(dec):
        if d and x["ingerido"] != dec[d - 1]["ingerido"]:
            ultima_comida = d
        if x["cansaco"] <= metade:
            r = d
        u = (u if u is not None else d) if x["urgente"] else None
        if not x["baixa"]:
            entrada = None
            continue
        entrada = d if entrada is None else entrada
        n_baixa += 1
        if not x["urgente"]:
            baixa_sem_fome_em_falta += x["combustivel"] < falta_limiar
            continue
        n_ambas += 1
        soma = {f: x["acum"][f] - dec[r]["acum"][f] for f in FONTES}
        sem = lambda f: x["cansaco"] - soma[f] < lim       # noqa: E731
        entra = {"tempo_acordado": soma["basal_dia"] + soma["basal_noite"], "falta_combustivel": soma["falta_combustivel"],
                 "atividades": soma["atividades"], "andar": soma["andar"]}
        if soma["outros"] or min(entra.values()) < 0:
            raise RuntimeError(f"sonda: uma fonte de cansaco com sinal trocado na decisao {d}: {soma}")
        total = sum(entra.values())
        if total <= 0:
            raise RuntimeError(f"sonda: a decisao {d} tem a energia baixa sem cansaco entrando desde o descanso: {soma}")
        classe = max(CLASSES, key=lambda cl: (entra[cl], -CLASSES.index(cl)))          # a fonte que mais pos cansaco na janela
        for cl in CLASSES:
            parte[cl] += entra[cl] / total
        janelas.append(d - r)
        fome_antes = dec[entrada]["urgente"] and u <= entrada
        cont[classe] += 1
        cruz[classe]["fome_antes" if fome_antes else "fome_depois"] += 1
        marcas = {"fome_antes": fome_antes, "dormindo": x["dormindo"], "combustivel_em_falta": x["combustivel"] < falta_limiar,
                  "fome_no_teto": x["fome"] == C, "nunca_descansou": r == 0 and dec[0]["cansaco"] > metade,
                  "adiou": any(dec[j]["comida_vista"] and dec[j]["acao"] != "comer" for j in range(u, d)),
                  "andar_na_fome": x["cansaco"] - (x["acum"]["andar"] - dec[u]["acum"]["andar"]) < lim,
                  "falta_combustivel_necessaria": sem("falta_combustivel"), "atividades_necessarias": sem("atividades"),
                  "andar_necessario": sem("andar")}
        for k, v in marcas.items():
            lados[k] += bool(v)
        desde_comer.append(None if ultima_comida is None else d - ultima_comida)
    sem_comer = sum(1 for v in desde_comer if v is None)
    return {"decisoes": n, "energia_baixa": n_baixa, "ambas": n_ambas, "classes": cont, "cruzado": cruz, "lados": lados,
            "decisoes_desde_comer": sorted(v for v in desde_comer if v is not None), "ambas_sem_ter_comido": sem_comer,
            "parte_somada": parte, "janelas": sorted(janelas), "baixa_sem_fome_combustivel_em_falta": baixa_sem_fome_em_falta}


def ritmos(motor) -> dict:
    """a fome e o cansaco por tick, dormindo e acordado, sem os ticks com ingestao (a soma da serie, exata)"""
    s = motor.serie_sonda
    acc = {"dormindo": [0, 0, 0, 0], "acordado": [0, 0, 0, 0]}          # ticks, d fome, d cansaco, ticks com a fome subindo o fome_tick
    sobe = motor.corpo.t.fome_por_tick
    for a, b in zip(s, s[1:]):
        if b[6] != a[6] or b[2] == a[2] == 0 or max(a[2], b[2]) >= motor.corpo.C:
            continue                                  # a ingestao, a fome no zero ou no teto (o corte) ficam de fora
        lado = acc["dormindo" if a[4] else "acordado"]
        lado[0] += 1
        lado[1] += b[2] - a[2]
        lado[2] += b[1] - a[1]
        lado[3] += b[2] - a[2] == sobe
    return {k: {"ticks": v[0], "d_fome": v[1], "d_cansaco": v[2], "ticks_fome_tick": v[3]} for k, v in acc.items()}


# ================================================================== a sonda
def uma_vida(braco: str, dono: str, lugar: str, semente: int, dias: int = DIAS, cfg_acoplamento=None) -> dict:
    motor, registro, baixas = viver(braco, dono, lugar, semente, dias, cfg_acoplamento=cfg_acoplamento)
    dec = decisoes_da_vida(motor, registro, baixas)
    c = VC.orq.cerebro_de(registro)
    lim = limiar_cansaco(motor.corpo.C, motor.corpo.S, c.inatos.lambda_sono)
    if motor.corpo.C != C_CORPO:
        raise RuntimeError(f"sonda: a escala do corpo e {motor.corpo.C}, a sonda soma em {C_CORPO}")
    corte = cortar(dec, lim, motor.corpo.C, motor.corpo.cc.falta_limiar)
    serie = motor.serie_sonda
    return {"vida": f"{braco}|{dono}|{lugar}|{semente}", "braco": braco, "dono": dono, "lugar": lugar, "semente": semente,
            **corte, "ritmos": ritmos(motor), "ticks": len(serie), "ticks_falta_combustivel": motor.contabil.ticks_falta,
            "ticks_combustivel_abaixo_do_limiar": sum(1 for x in serie if x[3] < motor.corpo.cc.falta_limiar),
            "refeicoes_em_c": serie[-1][6] / motor.corpo.C, "acum_final": serie[-1][5],
            "ticks_dormindo": sum(1 for x in serie if x[4]),
            "corpo": {k: getattr(motor.corpo.cc, k) for k in CORPO_CONFERIDO} | {"fome_por_tick": motor.corpo.t.fome_por_tick},
            "metabolismo": {**motor.corpo.contas_metabolismo, "descartado_fome_zero": motor.corpo.descartado_total,
                            "digerido": motor.corpo.digerido_total}}


def somar(vidas: list[dict]) -> dict:
    """as contagens somadas e as fracoes sobre as decisoes com as duas"""
    if not vidas:
        raise ValueError("sonda: nenhuma vida para somar")
    t = {"vidas": len(vidas), "decisoes": 0, "energia_baixa": 0, "ambas": 0, "ambas_sem_ter_comido": 0, "ticks": 0,
         "ticks_falta_combustivel": 0, "baixa_sem_fome_combustivel_em_falta": 0, "ticks_dormindo": 0, "ticks_combustivel_abaixo_do_limiar": 0,
         "corpo": vidas[0]["corpo"],
         "metabolismo": {k: 0 for k in vidas[0]["metabolismo"]}, "classes": {cl: 0 for cl in CLASSES},
         "cruzado": {cl: {"fome_antes": 0, "fome_depois": 0} for cl in CLASSES}, "acum_final": {f: 0 for f in FONTES},
         "lados": {k: 0 for k in vidas[0]["lados"]}, "ritmos": {lado: {"ticks": 0, "d_fome": 0, "d_cansaco": 0, "ticks_fome_tick": 0}
                                                                for lado in ("dormindo", "acordado")},
         "parte_somada": {cl: 0.0 for cl in CLASSES}}
    for v in vidas:
        if v["corpo"] != vidas[0]["corpo"]:
            raise ValueError(f"sonda: o corpo de {v['vida']} nao e o das outras vidas: {v['corpo']}")
        for k in ("decisoes", "energia_baixa", "ambas", "ambas_sem_ter_comido", "ticks", "ticks_falta_combustivel",
                  "baixa_sem_fome_combustivel_em_falta", "ticks_dormindo", "ticks_combustivel_abaixo_do_limiar"):
            t[k] += v[k]
        for cl in CLASSES:
            t["classes"][cl] += v["classes"][cl]
            for lado in ("fome_antes", "fome_depois"):
                t["cruzado"][cl][lado] += v["cruzado"][cl][lado]
        for f in FONTES:
            t["acum_final"][f] += v["acum_final"][f]
        for cl in CLASSES:
            t["parte_somada"][cl] += v["parte_somada"][cl]
        for k in t["metabolismo"]:
            t["metabolismo"][k] += v["metabolismo"][k]
        for k in t["lados"]:
            t["lados"][k] += v["lados"][k]
        for lado in ("dormindo", "acordado"):
            for k in ("ticks", "d_fome", "d_cansaco", "ticks_fome_tick"):
                t["ritmos"][lado][k] += v["ritmos"][lado][k]
    a = t["ambas"]
    t["fracao_ambas_na_energia_baixa"] = a / t["energia_baixa"] if t["energia_baixa"] else None
    t["fracao_por_classe"] = {cl: (x / a if a else None) for cl, x in t["classes"].items()}
    t["fracao_lados"] = {k: (x / a if a else None) for k, x in t["lados"].items()}
    t["por_tick"] = {lado: {"fome": r["d_fome"] / r["ticks"], "cansaco": r["d_cansaco"] / r["ticks"]} if r["ticks"] else None
                     for lado, r in t["ritmos"].items()}
    sem_fome = t["energia_baixa"] - a
    t["fracao_combustivel_em_falta_na_baixa_sem_fome"] = t["baixa_sem_fome_combustivel_em_falta"] / sem_fome if sem_fome else None
    dias = t["ticks"] / TICKS_POR_DIA
    t["metabolismo_em_c_por_dia"] = {k: x / C_CORPO / dias for k, x in t["metabolismo"].items()}
    t["cansaco_em_c_por_dia"] = {f: x / C_CORPO / dias for f, x in t["acum_final"].items()}
    # o orcamento do combustivel (C por dia): o teto do que a digestao converte (ela so poe no combustivel o que tira da fome, e a fome
    # sobe o fome_tick por tick, mais o brincar do dono) contra a demanda do basal (no sono medido) e das atividades e do andar (o
    # cansaco delas vezes o fator do gasto, ME-3)
    cc, dorm = t["corpo"], t["ticks_dormindo"] / t["ticks"]
    t["fracao_ticks_dormindo_todos"] = dorm
    demanda_basal = (cc["gasto_basal_acordado"] * (1 - dorm) + cc["gasto_basal_dormindo"] * dorm) * TICKS_POR_DIA / C_CORPO
    demanda_ativ = (t["cansaco_em_c_por_dia"]["atividades"] + t["cansaco_em_c_por_dia"]["andar"]) * cc["gasto_atividades_num"] / cc["gasto_atividades_den"]
    t["orcamento_combustivel_em_c_por_dia"] = {
        "teto_da_conversao_pelo_fome_tick": cc["fome_por_tick"] * TICKS_POR_DIA / C_CORPO * cc["conversao_num"] / cc["conversao_den"],
        "demanda_basal": demanda_basal, "demanda_atividades_e_andar": demanda_ativ, "demanda_total": demanda_basal + demanda_ativ,
        "gasto_real": t["metabolismo_em_c_por_dia"]["gasto_basal"] + t["metabolismo_em_c_por_dia"]["gasto_atividade"]}
    t["parte_media"] = {cl: (x / a if a else None) for cl, x in t["parte_somada"].items()}
    jan = sorted(x for v in vidas for x in v["janelas"])
    t["janela_mediana_decisoes"] = jan[len(jan) // 2] if jan else None
    t["fracao_fome_tick"] = {lado: (r["ticks_fome_tick"] / r["ticks"] if r["ticks"] else None) for lado, r in t["ritmos"].items()}
    desde = sorted(x for v in vidas for x in v["decisoes_desde_comer"])
    t["decisoes_desde_comer_mediana"] = desde[len(desde) // 2] if desde else None
    t["fracao_ticks_combustivel_em_falta"] = t["ticks_falta_combustivel"] / t["ticks"]      # os ticks em que a ponte subiu o cansaco
    t["fracao_ticks_combustivel_abaixo_do_limiar"] = t["ticks_combustivel_abaixo_do_limiar"] / t["ticks"]   # no comeco do tick
    refeicoes = sorted(v["refeicoes_em_c"] for v in vidas)
    t["refeicoes_em_c_por_vida"] = {"min": refeicoes[0], "mediana": refeicoes[len(refeicoes) // 2], "max": refeicoes[-1]}
    t["fracao_por_classe_cruzada"] = {cl: {k: (x / a if a else None) for k, x in c.items()} for cl, c in t["cruzado"].items()}
    t["fracao_ticks_dormindo"] = t["ritmos"]["dormindo"]["ticks"] / (t["ritmos"]["dormindo"]["ticks"] + t["ritmos"]["acordado"]["ticks"])
    return t


def rodar(sementes=SEMENTES, bracos=BRACOS, celulas=CELULAS, dias: int = DIAS, cfg_acoplamento=None) -> dict:
    vidas = [uma_vida(b, d, lu, s, dias, cfg_acoplamento) for b in bracos for s in sementes for d, lu in celulas]
    agreg = {}
    for b in bracos:
        vb = [v for v in vidas if v["braco"] == b]
        agreg[b] = {"todas": somar(vb), **{lugar: somar([v for v in vb if v["lugar"] == lugar])
                                            for lugar in sorted({lu for _, lu in celulas})}}
    return {"vidas": vidas, "agregado": agreg}


def _git(*a) -> str:
    return subprocess.run(["git", *a], cwd=RAIZ, capture_output=True, text=True, check=True).stdout.strip()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--saida", default=None, help=f"padrao: {SAIDA}, ou {SAIDA_CHAVE} com --chave-d")
    ap.add_argument("--chave-d", action="store_true", help="a etapa 2: a ConfigAcoplamentoCorpo ligada (a falta de combustivel sobe a fome)")
    a = ap.parse_args()
    padrao = SAIDA_CHAVE if a.chave_d else SAIDA
    a.saida = a.saida or padrao
    ca = CONFIG_ACOPLAMENTO_CORPO_LIGADA if a.chave_d else None
    saida = RAIZ / a.saida
    if saida.exists():
        raise SystemExit(f"{saida} ja existe: a sonda nao sobrescreve")
    t0 = time.perf_counter()
    r = rodar(cfg_acoplamento=ca)
    r["meta"] = {"comando": "python experiments/sonda_v3_corpo_acoplamento.py" + (" --chave-d" if a.chave_d else "")
                 + (f" --saida {a.saida}" if a.saida != padrao else ""),
                 "acoplamento": None if ca is None else {"ligada": ca.ligada, "falta_fome": ca.falta_fome},
                 "commit": _git("rev-parse", "HEAD"), "git_limpo": _git("status", "--porcelain") == "",
                 "sementes": list(SEMENTES), "bracos": list(BRACOS), "celulas": [list(c) for c in CELULAS], "dias": DIAS,
                 "orcamento_por_dia": ORCAMENTO_POR_DIA, "python": platform.python_version(), "processos": 1,
                 "duracao_s": round(time.perf_counter() - t0, 1)}
    saida.parent.mkdir(parents=True, exist_ok=True)
    texto = json.dumps(r, ensure_ascii=False, indent=1, sort_keys=True)
    saida.write_text(texto, encoding="utf-8", newline="\n")
    print(f"{saida}: sha256 {hashlib.sha256(texto.encode()).hexdigest()}")
    for b in BRACOS:
        t = r["agregado"][b]["todas"]
        print(b, "ambas/baixa", round(t["fracao_ambas_na_energia_baixa"], 3), {k: round(v, 3) for k, v in t["fracao_por_classe"].items()},
              {k: round(v, 3) for k, v in t["fracao_lados"].items()})


if __name__ == "__main__":
    main()
