"""A run da LONGE_GEOMETRIA: a regularidade do longe separada da geometria (docs/PLANO_ANALISE_V3_LONGE_GEOMETRIA.md, PROPOSTO;
docs/TAREFA_V3_LONGE_GEOMETRIA.md). Pergunta: o ganho da memoria do modular no `longe_fixo` vem de a racao voltar aos mesmos lugares (a
regularidade) ou de onde e a partir de onde ela e posta (o lado leste e a ancora no comedouro)? As vidas sao as da C1
(experiments/run_v2_longe_regular.py: o cenario do MVP, os 4 donos, 14 dias, 16 interacoes por dia, o motor que grava o corpo para a C5,
o G1, o T-CENARIO-1, o G-MECANISMO e o credito em toda vida), com a conferencia da memoria da C4 no PAD.

O desenho (secao 3): as celulas 4 donos x 4 lugares (`longe_um`, o `longe_fixo` com 1 ponto; `longe_fixo`; `longe_ancora`, um ponto novo a
cada racao sorteado como os do `longe_fixo`; `longe`, o sorteado de sempre), os bracos PAD (o REL da C4), M3* (o "M3" do conserto), M2 e
M0, todos com a `intencao_suspensa` e o sono que segura desligados, K = 200 unidades (40 por base) nas bases 93101, 93202, 93303, 93404 e
93505 (faixa PROPOSTA, a confirmar), o prefixo `digibrain_prototipo`: 200 x 64 = 12 800 vidas. A run roda uma vez, sem calibracao nem piloto.

A analise (secoes 5 a 8), no `resultado.json`: os primarios I-M3 e I-PAD (o ganho da memoria por episodio no `longe_fixo` menos o mesmo no
`longe_ancora`, pareados por unidade, o IC95 pelo t e o Holm sobre os dois p unilaterais), as premissas (G-PESA da memoria e G-ELEGIVEL-EP
no M3* e no PAD, nos dois estilos), a classe de cada contraste (a regra da A6.6 com a margem da secao 6), a leitura da secao 7 e o
descritivo da secao 8 (a conferencia da construcao nas vidas, as taxas por faixa de d0, as visitas, a escada um -> tres -> nenhum, a
geometria sem aprendizado no M0, o corpo e por dono), sem gate. A decomposicao da D-C1-3 (secao 8, item 3) sai num script a parte, depois
da run, que rejoga as vidas do disco (como o experiments/descritivo_dc13_longe_fixo.py da C1).

A trava (secao 0 do plano): o plano APROVADO pelo Matheus no cabecalho (`exigir_plano_aprovado`), a faixa 93101...93505 reservada em
`experiments/bancada/faixas.py`, so as bases, o K, os dias e o orcamento do plano, no maximo 4 processos, e nenhuma gravacao por cima de uma
pasta que ja existe. Na fumaca (as sementes dos testes 101...505) a run roda sem a faixa, sem o K e sem a aprovacao, com menos dias se a
config pedir.

    python experiments/run_v3_longe_geometria.py --config experiments/configs/v3_longe_geometria/longe_geometria.json --processos 4
"""
from __future__ import annotations

import argparse
import json
import math
import platform
import statistics
import sys
import time
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
from digilab.config import CONFIG_PADRAO, N_PONTOS_LONGE_FIXO, N_PONTOS_LONGE_UM  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.metrics import holm  # noqa: E402
from digilab.mundo import DonoComLugar, centro_da_celula, distancia  # noqa: E402
from digilab.temperamento import NEUTRO  # noqa: E402

PLANO = "docs/PLANO_ANALISE_V3_LONGE_GEOMETRIA.md"
PREFIXO = orq.PREFIXO                                                                 # 3.4 (o da C1)
FASE = "longe_geometria"
BASES = (93101, 93202, 93303, 93404, 93505)                                           # 3.4, PROPOSTA (LG-6)
K_POR_BASE = 40                                                                       # 3.4 e 6, PROPOSTO (LG-5): 200 unidades
FAIXA = (93101, 93505)
SAIDA = "artifacts_v3_longe_geometria/run"                                            # a pasta-mae tem o poder.json
DIAS, ORCAMENTO_POR_DIA = orq.DIAS, orq.ORCAMENTO_POR_DIA                             # secao 2 (o cenario da C1)
MAX_PROCESSOS = 4                                                                     # secao 11 (V3-D8)
DONOS = orq.DONOS
LUGARES = ("longe_um", "longe_fixo", "longe_ancora", "longe")                         # 3.1
ESTILO_DO_LUGAR = {"longe_um": ("longe_fixo", N_PONTOS_LONGE_UM), "longe_fixo": ("longe_fixo", N_PONTOS_LONGE_FIXO),
                   "longe_ancora": ("longe_ancora", N_PONTOS_LONGE_FIXO), "longe": ("longe", N_PONTOS_LONGE_FIXO)}
FIXO, ANCORA, UM, SORTEADO = "longe_fixo", "longe_ancora", "longe_um", "longe"
BRACOS = ("PAD", "M3", "M2", "M0")                                                    # 3.3; o "M3" e o M3*
BRACO_DO_ORQ = {"PAD": "REL", "M3": "M3", "M2": "M2", "M0": "M0"}                     # o PAD e o REL da C4 (SUBCHAVES_C4)
COM_MEMORIA = ("PAD", "M3")
FAMILIA = (("I-M3", "M3"), ("I-PAD", "PAD"))                                          # 5: o primario, com o Holm
CONTROLE = "M2"
CELULAS = tuple((d, lu) for d in DONOS for lu in LUGARES)
CHAVES_CONFIG = lr.CHAVES_CONFIG
MARGEM = 0.034                                                                        # 6, PROPOSTA (LG-5), SEM FONTE: o "~ 0"
ALFA_FAMILIA = 0.025                                                                  # 5: unilateral, na familia (o Holm)
G_PESA_LIMIAR = orq.G_PESA["limiar"]                                                  # 5: o 0,01 da A6.4, SEM FONTE
G_ELEGIVEL_EP = orq.G_ELEGIVEL_EP                                                     # 5: a de A6.4, como esta
FAIXAS_D0 = lr.FAIXAS_D0
EPISODIO = lr.EPISODIO


# ================================================================== a config e a trava
def _plano() -> str:
    return (RAIZ / PLANO).read_text(encoding="utf-8")


def exigir_plano_aprovado(plano: str) -> None:
    """a trava da secao 0: a primeira linha de status do plano diz "APROVADO pelo Matheus"; o PROPOSTO de hoje recusa a run"""
    status = [x for x in plano.splitlines() if x.startswith("**Status:")]
    if not status or not status[0].startswith("**Status: APROVADO pelo Matheus"):
        raise RuntimeError(f"o plano {PLANO} nao esta APROVADO pelo Matheus no cabecalho (secao 0): {status[:1] or 'sem a linha do status'}")


def exigir_faixa_reservada() -> None:
    """a faixa 93101...93505 esta em FAIXAS_RESERVADAS (3.4); sem ela a run nao tem fonte para as sementes"""
    if not any((lo, hi) == FAIXA for lo, hi, _ in FAIXAS_RESERVADAS):
        raise bv.SementeSemPlano(f"a faixa {FAIXA[0]}...{FAIXA[1]} nao esta em FAIXAS_RESERVADAS (3.4)")


def modo_da_config(cfg: dict) -> str:
    """'fumaca' (as sementes dos testes) ou 'longe_geometria', que segue o plano a letra: outra base, outro K, outros dias ou outro
    orcamento falham alto, sementes fora da faixa e dos testes levantam SementeSemPlano, e o plano sem o APROVADO recusa a run"""
    faltam, sobram = (CHAVES_CONFIG - {"descricao"}) - set(cfg), set(cfg) - CHAVES_CONFIG
    if faltam or sobram:
        raise ValueError(f"config: faltam {sorted(faltam)}, sobram {sorted(sobram)}")
    if cfg["fase"] != FASE:
        raise ValueError(f"fase {cfg['fase']!r}: so {FASE!r}")
    u = cfg["unidades"]
    bases = tuple(u["bases"])
    if u.get("prefixo") != PREFIXO or cfg["orcamento_por_dia"] != ORCAMENTO_POR_DIA or type(u.get("k")) is not int or u["k"] < 1:
        raise ValueError("config fora do plano: o prefixo (3.4), o orcamento (secao 2) ou o K")
    if bases and set(bases) <= bv.SEMENTES_TESTE:
        if not 1 <= cfg["dias"] <= DIAS:
            raise ValueError(f"fumaca com {cfg['dias']} dias: de 1 a {DIAS}")
        return "fumaca"
    if bases != BASES:
        raise bv.SementeSemPlano(f"bases {list(bases)}: so as dos testes (fumaca) ou {list(BASES)} (3.4)")
    exigir_faixa_reservada()
    exigir_plano_aprovado(_plano())
    erros = []
    if cfg["dias"] != DIAS:
        erros.append(f"dias {cfg['dias']} (o plano: {DIAS})")
    if cfg.get("plano") != PLANO:
        erros.append(f"plano {cfg.get('plano')!r}")
    if u["k"] != K_POR_BASE:
        erros.append(f"K por base {u['k']} (o plano: {K_POR_BASE})")
    if erros:
        raise ValueError(f"a {FASE} segue o plano a letra: {erros}")
    return FASE


# ================================================================== a vida
def dono_do_lugar(dono: str, lugar: str, semente: int) -> DonoComLugar:
    """o DonoComLugar do lugar: o `longe_um` e o `longe_fixo` com N_PONTOS_LONGE_UM pontos (3.1); os outros, o estilo de mesmo nome"""
    estilo, n = ESTILO_DO_LUGAR[lugar]
    return DonoComLugar(criar_dono(dono), estilo, semente, dono, orq.CM, n_pontos=n)


def viver(braco: str, dono: str, lugar: str, semente: int, dias: int, orcamento_por_dia: int):
    """uma vida: (o motor, o registro, as fabricas, o dono); o cerebro e o do conserto (o PAD e o REL da C4, SUBCHAVES_C4), o motor e o
    MotorGravaCorpo da C1, o sono que segura desligado (o `sono` None de orq.fabricas)"""
    fp, _ = orq.fabricas(BRACO_DO_ORQ[braco], dono, semente, dias, orcamento_por_dia, conserto=True)
    cc = orq.bancada(dias, orcamento_por_dia).cfg_corpo_de(bv.EspecVida(dono, gl.BRACO_V11, semente))

    def fm(politica, cfg, s):
        return lr.MotorGravaCorpo(politica, cfg, s, NEUTRO, "brasa", obediencia_desligada=True, cfg_mundo=orq.CM, cfg_corpo=cc)

    registro = fp(CONFIG_PADRAO)
    d = dono_do_lugar(dono, lugar, semente)
    motor, _ = simular_vida_fisico(d, registro, semente, dias, orcamento_por_dia * dias, dono, fm)
    return motor, registro, (fp, fm), d


def direcao_do_comedouro(x: int, y: int) -> int:
    """a direcao das 16 do ponto visto do comedouro (o angulo mais proximo; o DIR16 gira no sentido do y que cresce para baixo)"""
    cx, cy = centro_da_celula(orq.CM.layout.comedouro, orq.CM)
    return round(-math.degrees(math.atan2(y - cy, x - cx)) / 22.5) % 16


def lugares_da_vida(d: DonoComLugar) -> dict:
    """a conferencia da construcao nas vidas (8, item 1): as racoes postas, os pontos distintos, a contagem por direcao vista do comedouro
    e o histograma da distancia ao comedouro em celulas inteiras"""
    cm = orq.CM
    cx, cy = centro_da_celula(cm.layout.comedouro, cm)
    por_dir: dict = {}
    hist: dict = {}
    for lg in d.lugares:
        x, y = lg["x"], lg["y"]
        k = str(direcao_do_comedouro(x, y))
        por_dir[k] = por_dir.get(k, 0) + 1
        c = str(distancia(x - cx, y - cy) // cm.sub)
        hist[c] = hist.get(c, 0) + 1
    return {"racoes": len(d.lugares), "distintos": len({(lg["x"], lg["y"]) for lg in d.lugares}),
            "por_direcao": dict(sorted(por_dir.items(), key=lambda kv: int(kv[0]))),
            "distancia_celulas": dict(sorted(hist.items(), key=lambda kv: int(kv[0])))}


def _vida(cfg: dict, braco: str, dono: str, lugar: str, unidade: dict, pasta: str) -> dict:
    """uma vida: vivida, gravada, rejogada do disco (G1), conferida (as falhas altas; a memoria da C4 no PAD) e medida"""
    c0, p0 = time.process_time(), time.perf_counter()
    motor, registro, fab, d = viver(braco, dono, lugar, unidade["semente"], cfg["dias"], cfg["orcamento_por_dia"])
    arquivo = Path(pasta) / "vidas" / braco / f"{dono}_{lugar}_{unidade['semente']}.jsonl"
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    arquivo.write_text(motor.log.para_jsonl(), encoding="utf-8", newline="\n")
    orq.conferir_replay(motor, fab, unidade["semente"], arquivo.read_text(encoding="utf-8"))
    orq.conferir_cenario(motor, registro)
    orq.conferir_mecanismo(BRACO_DO_ORQ[braco], registro, None)
    c = orq.cerebro_de(registro)
    if c.cd.intencao_suspensa or c.m.arb.sono.ligada:
        raise RuntimeError(f"{braco}: a intencao_suspensa ou o sono que segura ligados (3.3: os dois ficam desligados)")
    if braco == "PAD":
        ma.conferir_memoria("REL", c)
    med = orq.medidas(motor, registro, BRACO_DO_ORQ[braco], cfg["dias"], True)
    return {"vida": f"{braco}|{dono}|{lugar}|{unidade['semente']}", "braco": braco, "dono": dono, "lugar": lugar,
            "semente": unidade["semente"], "base": unidade["base"], "k": unidade["k"], **med,
            "corpo": lr.medidas_do_corpo(motor, registro, cfg["dias"]), "metas": lr.trocas_de_meta(registro),
            "lugares": lugares_da_vida(d),
            "custo": {"vida_cpu": time.process_time() - c0, "vida_parede": time.perf_counter() - p0}}


def tarefa(cfg: dict, unidade: dict, pasta: str) -> list[dict]:
    return [_vida(cfg, b, dono, lugar, unidade, pasta) for b in BRACOS for dono, lugar in CELULAS]


# ================================================================== a analise
def _celulas(lugar: str) -> tuple:
    return tuple((d, lugar) for d in DONOS)


def nivel(registros: list[dict], braco: str, medida, lugar: str) -> dict:
    """{(base, semente): a media da medida nas 4 celulas do lugar}"""
    return orq.por_unidade(registros, braco, None, medida, _celulas(lugar))


def ganho(registros: list[dict], a: str, b: str, lugar: str, medida=EPISODIO) -> dict:
    """{(base, semente): a media, nas 4 celulas do lugar, de medida(a) - medida(b) no mesmo dono}"""
    return orq.por_unidade(registros, a, b, medida, _celulas(lugar))


def interacao(registros: list[dict], a: str, b: str, lugar_1: str, lugar_2: str, medida=EPISODIO) -> dict:
    """{(base, semente): ganho(a - b) no lugar_1 - ganho(a - b) no lugar_2}, so nas unidades com os dois (as outras ficam fora, contadas
    no relato pelo n)"""
    g1, g2 = ganho(registros, a, b, lugar_1, medida), ganho(registros, a, b, lugar_2, medida)
    return {u: g1[u] - g2[u] for u in sorted(set(g1) & set(g2))}


def estimativa(difs: dict) -> dict:
    return lr.estimativa(difs, MARGEM)


def primarios(registros: list[dict], boot: dict) -> dict:
    """secao 5: I-M3 e I-PAD, a interacao do ganho da memoria (X - M2 por episodio) entre o `longe_fixo` e o `longe_ancora`, o t sobre as
    unidades; o Holm (alfa 0,025 unilateral na familia) sobre os dois p unilaterais; cada um passa se o Holm o rejeita e o limite inferior
    do IC95 fica acima de 0. Ao lado: o IC95, o g1 com a ressalva, o bootstrap rotulado, a classe e a margem efetiva."""
    cs = {}
    for nome, braco in FAMILIA:
        difs = interacao(registros, braco, CONTROLE, FIXO, ANCORA)
        c = orq.contraste_t(difs, boot)
        ic = {"ic_inferior": c["ic95"]["ic_inferior"], "ic_superior": c["ic95"]["ic_superior"], "motivo": c["motivo"]}
        cs[nome] = {"contraste": f"({braco} - {CONTROLE}) no {FIXO} - ({braco} - {CONTROLE}) no {ANCORA}, taxa por episodio", **c,
                    "classe": lr.classe(ic, MARGEM), "margem": MARGEM, "margem_efetiva": lr.margem_efetiva(estimativa(difs)["dp"], c["n"])}
    h = holm({n: c["p_unilateral"] for n, c in cs.items()}, ALFA_FAMILIA)
    return {n: {**c, "holm": h[n], "passa": h[n]["rejeita"] and c["ic95"]["ic_inferior"] is not None and c["ic95"]["ic_inferior"] > 0}
            for n, c in cs.items()}


def premissas(registros: list[dict]) -> dict:
    """secao 5: a G-PESA da memoria (o limite inferior do IC95 pelo t > 0,01) e a G-ELEGIVEL-EP (80 % das vidas com 3 episodios ou mais),
    no M3* e no PAD, no `longe_fixo` e no `longe_ancora`. Se uma falha num braco, o primario dele e inconclusivo por premissa."""
    out = {}
    for b in COM_MEMORIA:
        partes = {}
        for lu in (FIXO, ANCORA):
            pesa = estimativa(nivel(registros, b, lambda r: r["influencia"]["memoria"], lu))
            pesa["passa"] = pesa["ic95"]["ic_inferior"] is not None and pesa["ic95"]["ic_inferior"] > G_PESA_LIMIAR
            pesa["limiar"] = G_PESA_LIMIAR
            vs = [r for r in registros if r["braco"] == b and r["lugar"] == lu]
            frac = sum(1 for r in vs if r["episodios_fome"]["n"] >= G_ELEGIVEL_EP["episodios"]) / len(vs)
            partes[lu] = {"G-PESA-memoria": pesa, "G-ELEGIVEL-EP": {"frac_vidas": frac, "vidas": len(vs), "limiar": G_ELEGIVEL_EP["frac_vidas"],
                                                                    "passa": frac >= G_ELEGIVEL_EP["frac_vidas"]}}
        out[b] = {**partes, "conclusivo": all(p["G-PESA-memoria"]["passa"] and p["G-ELEGIVEL-EP"]["passa"] for p in partes.values())}
    return out


def leitura_de(prim: dict, conclusivo: bool, m_ancora: dict) -> dict:
    """a regra de leitura da secao 7, na ordem (a primeira linha que serve), para um primario: a classe do I (com '> 0' so se o primario
    passa) e a da M-ANCORA (X - M2 no `longe_ancora`)"""
    i = "> 0" if prim["passa"] else prim["classe"]["classe"]
    if i == "> 0" and not prim["passa"]:
        i = "indeterminado"
    m = m_ancora["classe"]["classe"]
    base = {"I": i, "M-ANCORA": m}
    if not conclusivo:
        return {**base, "linha": "inconclusivo por premissa: a memoria nao pesou, ou os donos nao deram racao com fome; registrado como esta"}
    if i == "indeterminado":
        linha = "registrado como indeterminado; nada se decide com ele"
    elif i == "< 0":
        linha = "a regularidade atrapalha a memoria: contra a previsao"
    elif i == "> 0" and m in ("≈ 0", "< 0"):
        linha = ("a regularidade explica o ganho: a memoria paga quando os lugares se repetem, com o lado e a ancora iguais; a leitura da C1 "
                 "e da C4 fica de pe, sem a mistura")
    elif i == "> 0" and m == "> 0":
        linha = "a memoria paga com a geometria do longe_fixo mesmo sem repeticao, e paga mais com ela"
    elif i == "≈ 0" and m == "> 0":
        linha = ("a geometria explica o ganho, nao a regularidade: a memoria ganha porque a racao cai sempre do mesmo lado do comedouro, "
                 "repetindo ou nao; a frase 'a memoria paga com mundo regular' nao se sustenta")
    elif i == "≈ 0" and m in ("≈ 0", "< 0"):
        linha = "a memoria nao ganha em nenhum dos dois: contra a C1; diagnosticar antes de ler"
    else:
        linha = "combinacao fora das linhas escritas na secao 7: registrada como esta; nada se decide com ela"
    return {**base, "linha": linha}


def leitura(prims: dict, prem: dict, m_ancora: dict) -> dict:
    """a secao 7 para o I-M3 e o I-PAD; se discordarem, as duas ficam registradas, e a do PAD vale para o jogo"""
    out = {nome: leitura_de(prims[nome], prem[b]["conclusivo"], m_ancora[b]) for nome, b in FAMILIA}
    out["concordam"] = out["I-M3"]["linha"] == out["I-PAD"]["linha"]
    out["vale_para_o_jogo"] = "I-PAD"
    return out


# ------------------------------------------------------------------ o descritivo (secao 8; sem gate)
def conferencia_da_construcao(registros: list[dict]) -> dict:
    """8, item 1: por lugar (somas sobre as vidas do M0, que nao muda onde a racao cai; todo braco ve as mesmas racoes so se o dono der o
    mesmo numero delas), a contagem por direcao vista do comedouro, o histograma da distancia e os pontos distintos por racao"""
    out = {}
    for lu in LUGARES:
        vs = [r["lugares"] for r in registros if r["braco"] == "M0" and r["lugar"] == lu]
        por_dir, hist = {}, {}
        for v in vs:
            for k, n in v["por_direcao"].items():
                por_dir[k] = por_dir.get(k, 0) + n
            for k, n in v["distancia_celulas"].items():
                hist[k] = hist.get(k, 0) + n
        racoes = sum(v["racoes"] for v in vs)
        out[lu] = {"vidas": len(vs), "racoes": racoes, "distintos_por_racao": sum(v["distintos"] for v in vs) / racoes if racoes else None,
                   "por_direcao": dict(sorted(por_dir.items(), key=lambda kv: int(kv[0]))),
                   "distancia_celulas": dict(sorted(hist.items(), key=lambda kv: int(kv[0])))}
    return out


def faixas_d0(registros: list[dict]) -> dict:
    """8, item 2: por lugar x braco x faixa de d0, os episodios (n), os fechados e a taxa (somas sobre as vidas). A ressalva da LP-2: a
    faixa depende do cerebro; a leitura entre lugares e primeiro a do M0."""
    g = orq.geometria()
    soma = {(lu, b): {f: [0, 0] for f in FAIXAS_D0} for lu in LUGARES for b in BRACOS}
    for r in registros:
        for _k, d0, _w, _fim, motivo in r["episodios_fome"]["episodios"]:
            acum = soma[(r["lugar"], r["braco"])][lr._faixa(d0, g)]
            acum[0] += 1
            acum[1] += motivo == "fechou"
    return {"ressalva": "a faixa de d0 depende do cerebro (LP-2): a leitura entre lugares e primeiro a do M0",
            "por_lugar_braco_faixa": {f"{lu}|{b}": {f: {"n": n, "fechados": fe, "taxa": fe / n if n else None}
                                                    for f, (n, fe) in soma[(lu, b)].items()} for lu in LUGARES for b in BRACOS}}


def visitas(registros: list[dict]) -> dict:
    """8, item 4: nos bracos com M-MEM, por lugar, as visitas ao lugar lembrado, as vazias (a regra corrigida e a v1) e a fracao que acha"""
    out = {}
    for b in COM_MEMORIA:
        for lu in LUGARES:
            vs = [r for r in registros if r["braco"] == b and r["lugar"] == lu]
            v, z, z1 = (sum(r[k] for r in vs) for k in ("visitas_lugar_lembrado", "visitas_vazias", "visitas_vazias_v1"))
            out[f"{b}|{lu}"] = {"vidas": len(vs), "visitas": v, "vazias": z, "vazias_v1": z1, "frac_acha": (v - z) / v if v else None}
    return out


def _niveis(registros: list[dict], medida, bracos: tuple = BRACOS) -> dict:
    return {f"{lu}|{b}": estimativa(nivel(registros, b, medida, lu)) for lu in LUGARES for b in bracos}


def corpo(registros: list[dict]) -> dict:
    """8, item 6 (a C5, como na C1): a fracao dos ticks fora da faixa e a menor necessidade, por lugar e braco, e o ganho X - M2"""
    out = {"limiar": lr.LIMIAR_CORPO}
    for j in lr.JANELAS_CORPO:
        for m in ("fracao_fora", "menor_media", "menor_minimo"):
            f = lambda r, j=j, m=m: r["corpo"][j][m]          # noqa: E731
            out[f"{j}|{m}"] = {"niveis": _niveis(registros, f),
                               "ganhos": {f"{lu}|{b} - M2": estimativa(ganho(registros, b, "M2", lu, f)) for lu in LUGARES for b in COM_MEMORIA}}
    return out


def descritivo(registros: list[dict]) -> dict:
    """a secao 8 e as secundarias da secao 1 (R-UM, GEO-M0, M-ANCORA), sem gate"""
    escada = {b: {lu: estimativa(ganho(registros, b, CONTROLE, lu)) for lu in LUGARES} for b in COM_MEMORIA}
    r_um = {b: estimativa(interacao(registros, b, CONTROLE, UM, FIXO)) for b in COM_MEMORIA}
    geo = {}
    for b in BRACOS:
        anc, sort = nivel(registros, b, EPISODIO, ANCORA), nivel(registros, b, EPISODIO, SORTEADO)
        geo[b] = estimativa({u: anc[u] - sort[u] for u in sorted(set(anc) & set(sort))})
    return {"conferencia_da_construcao": conferencia_da_construcao(registros),
            "R-UM": {"contraste": f"(X - {CONTROLE}) no {UM} - (X - {CONTROLE}) no {FIXO}", "previsao": "> 0", **r_um},
            "GEO": {"contraste": f"a taxa por episodio no {ANCORA} - no {SORTEADO}, por braco (a leitura principal e a do M0)",
                    "previsao": None, **geo},
            "escada_do_ganho": {"contraste": f"X - {CONTROLE} por lugar (um -> tres -> nenhum, com a mesma ancora; e o sorteado)", **escada},
            "faixas_d0": faixas_d0(registros), "visitas": visitas(registros), "corpo": corpo(registros),
            "episodio_por_lugar_braco": _niveis(registros, EPISODIO),
            "g_pesa_memoria": _niveis(registros, lambda r: r["influencia"]["memoria"], COM_MEMORIA),
            "episodios_por_vida": _niveis(registros, lambda r: r["episodios_fome"]["n"]),
            "por_dono": {f"{d}|{lu}|{b}": statistics.fmean(v for v in (EPISODIO(r) for r in registros
                                                                       if r["dono"] == d and r["lugar"] == lu and r["braco"] == b) if v is not None)
                         for d in DONOS for lu in LUGARES for b in BRACOS
                         if any(EPISODIO(r) is not None for r in registros if r["dono"] == d and r["lugar"] == lu and r["braco"] == b)}}


def analisar(registros: list[dict], boot: dict = orq.BOOTSTRAP) -> dict:
    """a analise das secoes 5 a 8, com a classe de cada contraste e a leitura"""
    prims, prem = primarios(registros, boot), premissas(registros)
    m_ancora = {b: estimativa(ganho(registros, b, CONTROLE, ANCORA)) for b in COM_MEMORIA}
    return {"primarios": prims, "premissas": prem, "M-ANCORA": m_ancora, "leitura": leitura(prims, prem, m_ancora),
            "descritivo": descritivo(registros),
            "nao_demonstra": ["que o longe fica consertado", "que o modular supera o A", "prontidao de algum cerebro",
                              "a separacao do lado e da ancora (secao 10)", "tamanho de efeito fora das condicoes da run"]}


# ================================================================== a run
def rodar(cfg: dict, pasta: Path, processos: int, caminho_config: Path | None = None) -> dict:
    if processos > MAX_PROCESSOS:
        raise ValueError(f"no maximo {MAX_PROCESSOS} processos (a maquina; V3-D8 e secao 11)")
    modo = modo_da_config(cfg)
    if pasta.exists():
        raise FileExistsError(f"{pasta} ja existe: a run se recusa a gravar por cima (uma vez; secao 7)")
    unidades = bv.unidades_derivadas(cfg["unidades"]["bases"], int(cfg["unidades"]["k"]), PREFIXO)
    pasta.mkdir(parents=True)
    inicio = time.time()
    rc = orq.rc
    meta = {"modo": modo, "fase": FASE, "plano": PLANO, "plano_sha256": rc._sha_arquivo(RAIZ / PLANO), "config": cfg,
            "config_arquivo": None if caminho_config is None else rc._relativo(caminho_config),
            "config_sha256": None if caminho_config is None else rc._sha_arquivo(caminho_config),
            "orquestrador_sha256": rc._sha_arquivo(Path(__file__)), "prototipo_sha256": rc._sha_arquivo(Path(orq.__file__)),
            "c1_sha256": rc._sha_arquivo(Path(lr.__file__)), "c4_sha256": rc._sha_arquivo(Path(ma.__file__)),
            "git_head": rc._git("rev-parse", "HEAD"), "git_limpo": rc._git("status", "--porcelain") == "", "processos": processos,
            "unidades": unidades, "celulas": [list(c) for c in CELULAS], "lugares": {lu: list(e) for lu, e in ESTILO_DO_LUGAR.items()},
            "bracos": {b: {"orquestrador": BRACO_DO_ORQ[b], **{**orq.SUBCHAVES_CONSERTO, **orq.SUBCHAVES_C4}[BRACO_DO_ORQ[b]]} for b in BRACOS},
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
    resultado = {"modo": modo, "fase": FASE, "plano": PLANO, "unidades": len(unidades), "vidas": len(lidos), **analisar(list(lidos.values()))}
    bv._gravar(pasta / "resultado.json", bv._dump(resultado))
    meta["fim"] = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
    meta["duracao_s"] = time.time() - inicio
    meta["python"] = platform.python_version()
    meta["artefatos_sha256"] = {n: bv._sha(pasta / n) for n in ("medidas.json", "resultado.json")}
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    return {"meta": meta, "registros": registros, "resultado": resultado}


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
        raise SystemExit("a fumaca precisa de --saida (fora de artifacts_v3_longe_geometria/)")
    saida = Path(a.saida) if a.saida else RAIZ / SAIDA
    r = rodar(cfg, saida, a.processos, caminho)["resultado"]
    print(json.dumps({k: r[k] for k in ("modo", "vidas", "primarios", "premissas", "M-ANCORA", "leitura")}, indent=1, ensure_ascii=True,
                     default=str)[:4000])


if __name__ == "__main__":
    main()
