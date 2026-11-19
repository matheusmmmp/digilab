"""CORPO C3, a ponte com teto (docs/PLANO_ANALISE_V3_CORPO_C3.md, APROVADO pelo Matheus em 2026-11-19, com as D-C3-1 a D-C3-8 DECIDIDAS).

Pergunta (secao 1): a ponte da D com teto mantem o ganho de forrageio da D e tira o dano da fome que o pet nao tem como resolver?

Os bracos (secao 2): o CTRL (o corpo de hoje, o REL da VALUATION), a D (a referencia pareada, a da C2) e a D com teto
(`ConfigTetoFomeCorpo`): o DTL no limiar da privacao (382 500) e o DTB em C/2 (225 000, SEM FONTE). As vidas sao as da C2
(`run_v3_corpo`): o bloco I com o pet sozinho nas 12 celulas da C4 x 200 unidades (106001...106200, k = 1), o bloco II com um par VIVO
por unidade e braco (106301...106400, k = 1, prefixo corpo_par). Este orquestrador e proprio para o `run_v3_corpo.py` da C2 ficar
intacto (o sha256 dele esta no meta.json da C2); as pecas das vidas e da analise vem de la.

A analise (secao 5): o F (a taxa por episodio no `longe_fixo`, braco - CTRL) com o Holm sobre o DTL e o DTB; as guardas B (a privacao em
cada lugar e nas 12 celulas, a exaustao no `longe_fixo` e nas 12, a saude nas 12 e nas 6 celulas do relapso e do aleatorio, D-C3-4) e o
S2 (D-C3-5); o S1 so descritivo. O descritivo: braco - D, por dono, a decomposicao da privacao, a fracao dos ticks com a ponte no teto e
a pergunta do incoerente (D-C3-6: as vidas iguais as do atencioso e a sensibilidade nas 11 celulas distintas).

A trava (secao 0): sem o "APROVADO pelo Matheus" no cabecalho do plano, sem a faixa em FAIXAS_RESERVADAS, com a pasta de saida ja
existente ou fora das bases do plano, o orquestrador recusa; a run passa antes pelo `tools/pre_run.py`. A fumaca usa as sementes dos testes.

Uso: python experiments/run_v3_corpo_c3.py --config experiments/configs/v3_corpo_c3/run.json --processos 4
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import statistics
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tools"))

import bancada_v2 as bv  # noqa: E402
import pre_run  # noqa: E402
import run_v3_corpo as C2  # noqa: E402
from bancada.faixas import FAIXAS_RESERVADAS  # noqa: E402
from bancada.regras_mundo import simular_vida_fisico  # noqa: E402
from digilab.config import (CONFIG_ACOPLAMENTO_CORPO, CONFIG_ACOPLAMENTO_CORPO_LIGADA, CONFIG_CONSERTO_VALUATION,  # noqa: E402
                            CONFIG_DIGESTAO_CORPO, CONFIG_DIGIBRAIN_INATOS, CONFIG_GRUPO_LIGADA, CONFIG_PADRAO, CONFIG_TETO_FOME_BAIXO,
                            CONFIG_TETO_FOME_CORPO, CONFIG_TETO_FOME_LIMIAR)
from digilab.digibrain import DigiBrain  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.grupo import RegistroGrupo, reproduzir_grupo, sementes_do_grupo  # noqa: E402
from digilab.metrics import JANELA_8_14, holm, janela_dias  # noqa: E402
from digilab.mundo import DonoComLugar  # noqa: E402
from digilab.temperamento import NEUTRO  # noqa: E402

orq, ma, lr, V, VC, CA, A0, SA, pc, e6 = C2.orq, C2.ma, C2.lr, C2.V, C2.VC, C2.CA, C2.A0, C2.SA, C2.pc, C2.e6
PLANO = "docs/PLANO_ANALISE_V3_CORPO_C3.md"
ORQUESTRADOR = "experiments/run_v3_corpo_c3.py"
FASE = "corpo_c3"
PREFIXO, PREFIXO_PAR = C2.PREFIXO, C2.PREFIXO_PAR
BASES_I = tuple(range(106001, 106201))                        # secao 4, D-C3-7 e D-C3-8: 200 sementes independentes
BASES_II = tuple(range(106301, 106401))                       # o bloco II: 100 pares
FAIXA = (106001, 106400)
K_POR_BASE = 1
DIAS, ORCAMENTO_POR_DIA = C2.DIAS, C2.ORCAMENTO_POR_DIA
SAIDA = "artifacts_v3_corpo/c3"                               # secao 6
MAX_PROCESSOS = C2.MAX_PROCESSOS
CELULAS = C2.CELULAS
PRIMARIO = C2.PRIMARIO
LUGARES_PRIVACAO = C2.LUGARES_PRIVACAO
CONTROLE, REFERENCIA = "CTRL", "D"
COM_TETO = ("DTL", "DTB")
BRACOS = (CONTROLE, REFERENCIA, *COM_TETO)
CONTRA_CTRL = (REFERENCIA, *COM_TETO)
TETOS = {CONTROLE: CONFIG_TETO_FOME_CORPO, REFERENCIA: CONFIG_TETO_FOME_CORPO, "DTL": CONFIG_TETO_FOME_LIMIAR, "DTB": CONFIG_TETO_FOME_BAIXO}
DONOS_SEM_COMIDA = ("relapso", "aleatorio")                   # D-C3-4: os donos que deixam faltar comida (o diagnostico da C2.5)
CELULAS_SEM_COMIDA = tuple(c for c in CELULAS if c[0] in DONOS_SEM_COMIDA)
CELULA_COPIA = ("incoerente", "comedouro")                    # D-C3-6: a celula que saiu igual a do atencioso na C2
CELULAS_DISTINTAS = tuple(c for c in CELULAS if c != CELULA_COPIA)
MARGEM, ALFA, FRACAO_DELTA_S = C2.MARGEM, C2.ALFA, C2.FRACAO_DELTA_S
EPISODIO, PRIVACAO, EXAUSTAO = C2.EPISODIO, C2.PRIVACAO, C2.EXAUSTAO
SAUDE = lambda r: r["saude_media"]                            # noqa: E731
LIMIAR = CONFIG_PADRAO.limiar_privacao
CHAVES_CONFIG = C2.CHAVES_CONFIG
S = CONFIG_DIGIBRAIN_INATOS.escala


# ================================================================== os bracos (secao 2)
def montar(braco: str) -> dict:
    """as chaves do braco: o acoplamento (a D nos tres tratados) e o teto; a digestao e o conserto sao os de hoje"""
    if braco not in BRACOS:
        raise ValueError(f"braco {braco!r}: so {BRACOS}")
    return {"acoplamento": CONFIG_ACOPLAMENTO_CORPO if braco == CONTROLE else CONFIG_ACOPLAMENTO_CORPO_LIGADA,
            "digestao": CONFIG_DIGESTAO_CORPO, "conserto": CONFIG_CONSERTO_VALUATION, "teto": TETOS[braco]}


def _kw_corpo(m: dict) -> dict:
    return {"cfg_acoplamento_corpo": m["acoplamento"], "cfg_digestao_corpo": m["digestao"], "cfg_teto_fome_corpo": m["teto"]}


def fabricas(braco: str, dono: str, semente: int, dias: int, orcamento_por_dia: int) -> tuple:
    """as fabricas da C2 (`run_v3_corpo.fabricas`), com as chaves deste braco"""
    m = montar(braco)
    cc = orq.bancada(dias, orcamento_por_dia).cfg_corpo_de(bv.EspecVida(dono, VC.gl.BRACO_V11, semente))
    cd = orq.config_do_braco("REL", conserto=True)

    def fp(cfg=None):
        return orq.Registro(DigiBrain(cfg or CONFIG_PADRAO, cd, orq.CM, inatos=CONFIG_DIGIBRAIN_INATOS, semente=semente,
                                      cfg_conserto=m["conserto"]), S)

    def fm(politica, cfg, s):
        return SA.MotorSonda(politica, cfg, s, NEUTRO, "brasa", obediencia_desligada=True, cfg_mundo=orq.CM, cfg_corpo=cc, **_kw_corpo(m))

    return fp, fm


def viver(braco: str, dono: str, lugar: str, semente: int, dias: int, orcamento_por_dia: int):
    """uma vida do bloco I, a da C2 (`run_v3_corpo.viver`), com as fabricas deste braco"""
    fp, fm = fabricas(braco, dono, semente, dias, orcamento_por_dia)
    registro = fp(CONFIG_PADRAO)
    c, categorias = orq.cerebro_de(registro), ma.Categorias()
    agir, reflexo = c.agir, c.m.arb.reflexo
    baixas: list[bool] = []

    def agir_e_ler(obs, rng):
        acao = agir(obs, rng)
        for e in c.m.mem.recente:
            categorias.setdefault(e["id"], list(e["categoria"]))
        return acao

    def reflexo_e_ler(sens, urgencias=None):
        baixas.append(sens["leitura"]["energia"] < c.inatos.lambda_sono)
        return reflexo(sens, urgencias)

    c.agir, c.m.arb.reflexo = agir_e_ler, reflexo_e_ler
    d = DonoComLugar(criar_dono(dono), lugar, semente, dono, orq.CM)
    motor, _ = simular_vida_fisico(d, registro, semente, dias, orcamento_por_dia * dias, dono, fm)
    del c.agir, c.m.arb.reflexo
    return motor, registro, (fp, fm), categorias, baixas


def conferir_braco(braco: str, corpo, arb) -> None:
    """o corpo e o M-ARB da vida tem as chaves do braco (falha alta)"""
    m = montar(braco)
    if corpo.ca != m["acoplamento"] or corpo.cd != m["digestao"] or corpo.ctf != m["teto"]:
        raise RuntimeError(f"{braco}: o corpo tem {corpo.ca}, {corpo.cd} e {corpo.ctf}, o braco pede {m}")
    if arb.cv != m["conserto"]:
        raise RuntimeError(f"{braco}: o M-ARB tem o conserto {arb.cv}, o braco pede {m['conserto']}")
    alvo = dict(corpo.grafo.emissor("falta_combustivel").efeitos)
    esperado = {"cansaco": corpo.cc.falta_cansaco} if braco == CONTROLE else {"fome": m["acoplamento"].falta_fome}
    if alvo != esperado:
        raise RuntimeError(f"{braco}: a ponte da falta de combustivel e {alvo}, o braco pede {esperado}")
    if braco not in COM_TETO and corpo.ticks_teto:
        raise RuntimeError(f"{braco}: o teto cortou a ponte sem a chave ({corpo.ticks_teto} ticks)")


def conferir_vida(braco: str, motor, registro, baixas: list[bool]) -> None:
    """secao 7: as chaves, a ponte, o cansaco sem a falta (bracos com a D) e o reflexo de hoje, decisao a decisao"""
    arb = orq.cerebro_de(registro).m.arb
    conferir_braco(braco, motor.corpo, arb)
    if braco != CONTROLE and (motor.contabil.acum["falta_combustivel"] or motor.contabil.ticks_falta):
        raise RuntimeError(f"{braco}: o cansaco subiu pela falta de combustivel com a D ligada")
    VC.conferir_conserto("REL", registro, baixas)
    if arb.suaves != 0:
        raise RuntimeError(f"{braco}: o reflexo suave somou peso sem a chave")


def medidas_c3(motor, registro, dias: int) -> dict:
    """as medidas novas da secao 5: a saude (D-C3-4), a decomposicao da privacao e a ponte no teto. Pelo Estado de cada decisao
    (`Registro.estados`: fome, higiene, energia, humor, saude), na janela dos dias 8 a 14 (na fumaca, mais curta, a vida toda: a regra do
    `orq.medidas`)"""
    passo = CONFIG_PADRAO.intervalo_decisao_ticks
    ini, fim = JANELA_8_14 if dias >= 14 else janela_dias(1, dias)
    es = [e for k, e in enumerate(registro.estados) if ini <= k * passo < fim]
    if not es:
        raise ValueError("sem decisao na janela")
    n = len(es)
    priv = [e for e in es if min(e[0], e[1], e[2]) < LIMIAR]
    return {"saude_media": statistics.fmean(e[4] for e in es),
            "saude_baixa": sum(1 for e in es if e[4] < LIMIAR) / n,
            "decomposicao": {"so_fome": sum(1 for e in priv if e[0] < LIMIAR <= min(e[1], e[2])) / n,
                             "so_energia": sum(1 for e in priv if e[2] < LIMIAR <= min(e[0], e[1])) / n,
                             "fome_e_energia": sum(1 for e in priv if e[0] < LIMIAR and e[2] < LIMIAR) / n,
                             "com_higiene": sum(1 for e in priv if e[1] < LIMIAR) / n,
                             "fome_baixa": sum(1 for e in es if e[0] < LIMIAR) / n},
            "ticks_teto": motor.corpo.ticks_teto, "fracao_ticks_teto": motor.corpo.ticks_teto / (dias * 1440)}


def _vida(cfg: dict, braco: str, dono: str, lugar: str, unidade: dict, pasta: str) -> dict:
    c0, p0 = time.process_time(), time.perf_counter()
    motor, registro, fab, categorias, baixas = viver(braco, dono, lugar, unidade["semente"], cfg["dias"], cfg["orcamento_por_dia"])
    arquivo = Path(pasta) / "vidas" / braco / f"{dono}_{lugar}_{unidade['semente']}.jsonl"
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    texto = motor.log.para_jsonl()
    arquivo.write_text(texto, encoding="utf-8", newline="\n")
    orq.conferir_replay(motor, fab, unidade["semente"], arquivo.read_text(encoding="utf-8"))
    orq.conferir_cenario(motor, registro)
    orq.conferir_mecanismo("REL", registro, None)
    ma.conferir_memoria("REL", orq.cerebro_de(registro))
    fins = ma.conferir_fins("REL", registro)
    conferir_vida(braco, motor, registro, baixas)
    med = orq.medidas(motor, registro, "REL", cfg["dias"], True)
    return {"vida": f"{braco}|{dono}|{lugar}|{unidade['semente']}", "braco": braco, "dono": dono, "lugar": lugar,
            "semente": unidade["semente"], "base": unidade["base"], "k": unidade["k"], **med,
            "corpo": lr.medidas_do_corpo(motor, registro, cfg["dias"]), "fins_conferidos": fins,
            "memoria": ma.medidas_memoria(registro, cfg["dias"], categorias),
            "valuation": V.descritivo_valuation(registro, med), "acoplamento": CA.medidas_acoplamento(motor, registro, baixas),
            **medidas_c3(motor, registro, cfg["dias"]), "descartado": motor.corpo.descartado_total,
            "log_sha256": hashlib.sha256(texto.encode("utf-8")).hexdigest(),
            "custo": {"vida_cpu": time.process_time() - c0, "vida_parede": time.perf_counter() - p0}}


def tarefa(cfg: dict, unidade: dict, pasta: str) -> list[dict]:
    return [_vida(cfg, b, dono, lugar, unidade, pasta) for b in BRACOS for dono, lugar in CELULAS]


# ================================================================== o bloco II: o substrato social
def fabricas_par(braco: str, semente_pet: int) -> tuple:
    """o pet de hoje da SOCIAL_PAR A0, com as chaves do braco (a C2, `run_v3_corpo.fabricas_par`)"""
    m = montar(braco)
    _, fm0 = A0.fabricas_do_jogo(A0.DONO, semente_pet, A0.CCO)
    cd = orq.config_do_braco(e6.BRACO, conserto=True)

    def fp(cfg=None):
        return DigiBrain(cfg or CONFIG_PADRAO, cd, e6.CM, semente=semente_pet, cfg_cooperacao=A0.CCO, cfg_conserto=m["conserto"])

    def fm(politica, cfg, s, **kw):
        return fm0(politica, cfg, s, **_kw_corpo(m), **kw)
    return fp, fm


def viver_par(braco: str, s: int, dias: int) -> tuple:
    ss = sementes_do_grupo(s, CONFIG_GRUPO_LIGADA.ids)
    t0, direcao = pc.sortear_perturbacao(s, A0.T0_MIN, A0.T0_MAX, A0.PASSO)
    pert = ("A", "B", t0, direcao, A0.D0)
    membros = []
    for ident in ("A", "B"):
        fp, fm = fabricas_par(braco, ss[ident])
        membros.append(pc.Membro(ident, "vivo", fm, fp, A0._dono(ss[ident]), A0.DONO, "digibrain"))
    v = pc.viver_par(A0.CM, s, membros, dias, perturbacao=pert, cfg_intervencao=A0.CI, cfg_cooperacao=A0.CCO)
    return v, ss, pert


def par(cfg: dict, braco: str, u: dict, pasta: str) -> dict:
    """um par VIVO do braco: as chaves nos dois pets, o replay pelo `reproduzir_grupo` e as medidas da janela da A0"""
    import gzip
    s, dias = u["semente"], cfg["pares"]["dias"]
    v, ss, pert = viver_par(braco, s, dias)
    for i in ("A", "B"):
        mo = v.grupo.motores[i]
        conferir_braco(braco, mo.corpo, mo.politica.m.arb)
    lido = RegistroGrupo.de_jsonl(v.grupo.registro.para_jsonl())
    r = reproduzir_grupo(lido, {i: fabricas_par(braco, ss[i]) for i in ("A", "B")}, A0.CM, cfg_cooperacao=A0.CCO, cfg_intervencao=A0.CI)
    if r.registro != v.grupo.registro or [tuple(r.motores[i].pet) for i in "AB"] != [tuple(v.grupo.motores[i].pet) for i in "AB"]:
        raise RuntimeError(f"o par {s} do {braco} nao se refaz pelo replay")
    arquivo = Path(pasta) / "pares" / braco / f"{u['base']}-{u['k']:04d}.jsonl.gz"
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    with gzip.GzipFile(arquivo, "wb", compresslevel=6, mtime=0) as f:
        f.write(v.grupo.registro.para_jsonl().encode("utf-8"))
    chutes = {i: len(pc.chutes(v, i)) for i in ("A", "B")}
    return {"par": f"{braco}|{u['base']}-{u['k']:04d}", "braco": braco, "base": u["base"], "k": u["k"], "semente": s,
            "perturbacao": list(pert), "chutes": chutes, "chutes_por_dia": (chutes["A"] + chutes["B"]) / dias,
            "janela": A0._janela(v), "arquivo_sha256": hashlib.sha256(arquivo.read_bytes()).hexdigest()}


def tarefa_par(cfg: dict, u: dict, pasta: str) -> list[dict]:
    return [par(cfg, b, u, pasta) for b in BRACOS]


# ================================================================== a analise (secao 5, escrita antes)
def _difs(registros: list[dict], medida, celulas, a: str, b: str = CONTROLE) -> dict:
    return orq.por_unidade(registros, a, b, medida, celulas)


def _celulas(lugar: str | None, base=CELULAS) -> tuple:
    return base if lugar is None else tuple(c for c in base if c[1] == lugar)


def _guarda(registros: list[dict], medida, celulas, nome_lugar: str, braco: str, reprova: str) -> dict:
    e = ma.estimativa(_difs(registros, medida, celulas, braco), MARGEM)
    return {**e, "contraste": f"{braco} - CTRL", "lugar": nome_lugar, "reprova_com": reprova, "passa": e["classe"]["classe"] != reprova}


def _s(pares: list[dict], medida, braco: str, reprova: str) -> dict:
    """a guarda do substrato da C2 (`run_v3_corpo._s`), com o delta de 10 % do nivel do CTRL"""
    v: dict = {b: {} for b in BRACOS}
    for p in pares:
        x = medida(p)
        if x is not None:
            v[p["braco"]][(p["base"], p["semente"])] = x
    comuns = sorted(set(v[braco]) & set(v[CONTROLE]))
    nivel = None if not comuns else sum(v[CONTROLE][k] for k in comuns) / len(comuns)
    delta = None if nivel is None else FRACAO_DELTA_S * abs(nivel)
    ic = orq.ic_t([v[braco][k] - v[CONTROLE][k] for k in comuns])
    cl = lr.classe({"ic_inferior": ic["ic_inferior"], "ic_superior": ic["ic_superior"], "motivo": ic["motivo"]}, delta or 0.0)
    return {"n": ic["n"], "media": ic["media"], "dp": ic["dp"], "ic95": {"ic_inferior": ic["ic_inferior"], "ic_superior": ic["ic_superior"]},
            "nivel_ctrl": nivel, "delta": delta, "classe": cl, "contraste": f"{braco} - CTRL", "reprova_com": reprova,
            "passa": cl["classe"] != reprova}


def guardas_b(registros: list[dict], braco: str, base=CELULAS) -> dict:
    """as oito guardas do bem-estar (secao 5): a privacao nos 3 lugares e nas 12, a exaustao no `longe_fixo` e nas 12, a saude nas 12 e
    nas 6 dos donos que deixam faltar comida. `base`: as celulas (as 12, ou as 11 distintas na sensibilidade da D-C3-6)"""
    nome = "as 12 celulas" if base == CELULAS else f"as {len(base)} celulas"
    return {**{f"privacao_{onde}": _guarda(registros, PRIVACAO, _celulas(lugar, base), lugar or nome, braco, "> 0")
               for onde, lugar in LUGARES_PRIVACAO},
            "exaustao_longe_fixo": _guarda(registros, EXAUSTAO, _celulas(PRIMARIO, base), PRIMARIO, braco, "> 0"),
            "exaustao_12_celulas": _guarda(registros, EXAUSTAO, base, nome, braco, "> 0"),
            "saude_12_celulas": _guarda(registros, SAUDE, base, nome, braco, "< 0"),
            "saude_sem_comida": _guarda(registros, SAUDE, tuple(c for c in base if c in CELULAS_SEM_COMIDA),
                                        "as celulas do relapso e do aleatorio", braco, "< 0")}


def criterios(registros: list[dict], pares: list[dict], boot: dict = orq.BOOTSTRAP) -> dict:
    out = {}
    for b in CONTRA_CTRL:
        c = orq.contraste_t(_difs(registros, EPISODIO, _celulas(PRIMARIO), b), boot)
        ic = {"ic_inferior": c["ic95"]["ic_inferior"], "ic_superior": c["ic95"]["ic_superior"], "motivo": c["motivo"]}
        F = {"contraste": f"{b} - CTRL, a taxa por episodio, longe_fixo", **c, "classe": ma.classe(ic, MARGEM), "margem": MARGEM}
        out[b] = {"F": F, "B": guardas_b(registros, b), "S": {"S2_tempo_ate_o_reencontro": _s(pares, C2.T_REENCONTRO, b, "> 0")}}
    h = holm({b: out[b]["F"]["p_unilateral"] for b in COM_TETO}, ALFA)        # D-C3-1, secao 5: so os bracos com teto
    for b in COM_TETO:
        out[b]["F"]["holm"] = h[b]
    out[REFERENCIA]["F"]["holm"] = None                                        # a D e a referencia: fora do Holm
    return out


def leitura_do_braco(cb: dict) -> dict:
    """a tabela da secao 5: ganho, perda, nulo ou indeterminado"""
    F = cb["F"]
    classe_f = F["classe"]["classe"]
    piora = [n for n, g in cb["B"].items() if not g["passa"]] + [n for n, g in cb["S"].items() if not g["passa"]]
    if classe_f == "indeterminado":
        leitura = "indeterminado"
    elif classe_f == "> 0" and F["holm"]["rejeita"]:
        leitura = "ganho" if not piora else "perda"
    else:
        leitura = "nulo"
    return {"leitura": leitura, "reprovadas": piora}


def veredito(cr: dict) -> dict:
    por_braco = {b: leitura_do_braco(cr[b]) for b in COM_TETO}
    ganhos = [b for b, x in por_braco.items() if x["leitura"] == "ganho"]
    return {"bracos": por_braco, "ganhos": ganhos,
            "geral": "ao menos um teto com ganho: a C4 (secao 8)" if ganhos else "nenhum teto com ganho: volta ao Matheus (secao 8)",
            "proximo": "ganho vai a C4, a validacao; perda ou nulo dos dois volta ao Matheus, com a opcao de nao mudar o corpo"}


def _sem_classe(e: dict) -> dict:
    return {k: v for k, v in e.items() if k != "classe"}


DESCRITIVOS_C3 = {**CA.DESCRITIVOS, "saude_media": SAUDE, "saude_baixa": lambda r: r["saude_baixa"],
                  "fracao_ticks_teto": lambda r: r["fracao_ticks_teto"],
                  **{f"privacao_{k}": (lambda k: lambda r: r["decomposicao"][k])(k)
                     for k in ("so_fome", "so_energia", "fome_e_energia", "com_higiene", "fome_baixa")}}


def descritivo(registros: list[dict], pares: list[dict]) -> dict:
    """os descritivos da secao 5, sem classe: por lugar (niveis, braco - CTRL e braco - D), por dono, o bloco II e o incoerente"""
    lugares = (("longe_fixo", PRIMARIO), ("12_celulas", None), ("comedouro", "comedouro"), ("longe", "longe"))
    out: dict = {}
    for onde, lugar in lugares:
        cs = _celulas(lugar)
        out[onde] = {n: {"niveis": {b: _sem_classe(ma.estimativa(orq.por_unidade(registros, b, None, f, cs))) for b in BRACOS},
                         **{f"{b} - CTRL": _sem_classe(ma.estimativa(_difs(registros, f, cs, b))) for b in CONTRA_CTRL},
                         **{f"{b} - D": _sem_classe(ma.estimativa(_difs(registros, f, cs, b, REFERENCIA))) for b in COM_TETO}}
                     for n, f in DESCRITIVOS_C3.items()}
    por_dono = {}
    for dono, lugar in CELULAS:
        cs = ((dono, lugar),)
        por_dono[f"{dono}|{lugar}"] = {n: {"niveis": {b: ma.estimativa(orq.por_unidade(registros, b, None, f, cs))["media"] for b in BRACOS},
                                           **{f"{b} - CTRL": _sem_classe(ma.estimativa(_difs(registros, f, cs, b))) for b in CONTRA_CTRL}}
                                       for n, f in (("privacao", PRIVACAO), ("saude_media", SAUDE), ("exaustao", EXAUSTAO),
                                                    ("refeicoes_por_dia", lambda r: r["cadeia"]["refeicoes_por_dia"]))}
    out["por_dono"] = por_dono
    out["bloco_II"] = {b: {"pares": sum(1 for p in pares if p["braco"] == b),
                           "S1_chutes_por_dia": _sem_classe(_s(pares, C2.CHUTES, b, "< 0")) if b != CONTROLE else None,
                           "chutes_por_dia_media": C2._media([p["chutes_por_dia"] for p in pares if p["braco"] == b]),
                           "fracao_pares_com_chute": C2._media([float(p["chutes"]["A"] + p["chutes"]["B"] > 0) for p in pares if p["braco"] == b]),
                           "fracao_janela_cabe": C2._media([float(p["janela"]["cabe"]) for p in pares if p["braco"] == b]),
                           "t_reencontro_media": C2._media([C2.T_REENCONTRO(p) for p in pares if p["braco"] == b and C2.T_REENCONTRO(p) is not None])}
                       for b in BRACOS}
    out["incoerente"] = incoerente(registros)
    return out


def incoerente(registros: list[dict]) -> dict:
    """D-C3-6 (a) e (c): as vidas do incoerente iguais as do atencioso (o sha256 do log), por lugar e braco; e as guardas das celulas
    refeitas nas 11 celulas distintas (sem a copia), ao lado das oficiais. O (b), o porque, e lido no codigo e vai no resultado."""
    idx = {(r["braco"], r["dono"], r["lugar"], r["semente"]): r["log_sha256"] for r in registros}
    iguais = {}
    for b in BRACOS:
        for lugar in ("comedouro", "longe", "longe_fixo"):
            ss = sorted({s for (bb, d, l, s) in idx if bb == b and l == lugar})
            iguais[f"{b}|{lugar}"] = {"iguais": sum(1 for s in ss if idx[(b, "atencioso", lugar, s)] == idx[(b, "incoerente", lugar, s)]),
                                      "vidas": len(ss)}
    sens = {b: {n: {k: g[k] for k in ("media", "ic95", "classe", "passa")} for n, g in guardas_b(registros, b, CELULAS_DISTINTAS).items()}
            for b in CONTRA_CTRL}
    return {"vidas_iguais_ao_atencioso": iguais, "celulas_distintas": [list(c) for c in CELULAS_DISTINTAS], "guardas_11_celulas": sens}


def analisar(registros: list[dict], pares: list[dict], boot: dict = orq.BOOTSTRAP) -> dict:
    cr = criterios(registros, pares, boot)
    return {"criterios": cr, "veredito": veredito(cr), "descritivo": descritivo(registros, pares),
            "nao_demonstra": ["nada sobre o jogo web (a chave fica desligada nele)",
                              "nada sobre outros tetos alem do limiar e de C/2, nem sobre a ponte dividida ou o transbordo (D-C3-3)",
                              "nada sobre a E e a C5 com o teto",
                              "nada sobre o social alem do substrato: nenhum mecanismo social entra"]}


# ================================================================== a trava e a run
def modo_da_config(cfg: dict) -> str:
    faltam, sobram = (CHAVES_CONFIG - {"descricao"}) - set(cfg), set(cfg) - CHAVES_CONFIG
    if faltam or sobram:
        raise ValueError(f"config: faltam {sorted(faltam)}, sobram {sorted(sobram)}")
    if cfg["fase"] != FASE:
        raise ValueError(f"fase {cfg['fase']!r}: so {FASE!r}")
    u, p = cfg["unidades"], cfg["pares"]
    if u.get("prefixo") != PREFIXO or p.get("prefixo") != PREFIXO_PAR or cfg["orcamento_por_dia"] != ORCAMENTO_POR_DIA:
        raise ValueError("config fora do plano: os prefixos ou o orcamento (secao 4)")
    for x in (u, p):
        if type(x.get("k")) is not int or x["k"] < 1:
            raise ValueError(f"config: o K {x.get('k')!r}")
    bases, bases_par = tuple(u["bases"]), tuple(p["bases"])
    if bases and set(bases) <= bv.SEMENTES_TESTE and set(bases_par) <= bv.SEMENTES_TESTE:
        if not 1 <= cfg["dias"] <= DIAS or not 1 <= p["dias"] <= A0.DIAS:
            raise ValueError(f"fumaca com {cfg['dias']} e {p['dias']} dias: de 1 a {DIAS} e de 1 a {A0.DIAS}")
        return "fumaca"
    if bases != BASES_I or bases_par != BASES_II:
        raise bv.SementeSemPlano("bases fora do plano: so as dos testes (fumaca) ou as da secao 4")
    if not any((lo, hi) == FAIXA for lo, hi, _ in FAIXAS_RESERVADAS):
        raise bv.SementeSemPlano(f"a faixa {FAIXA} nao esta em FAIXAS_RESERVADAS (secao 4)")
    CA.exigir_aprovado((RAIZ / PLANO).read_text(encoding="utf-8"))
    erros = [m for m, ok in ((f"dias {cfg['dias']} (o plano: {DIAS})", cfg["dias"] == DIAS),
                             (f"dias do par {p['dias']} (o plano: {A0.DIAS})", p["dias"] == A0.DIAS),
                             (f"plano {cfg.get('plano')!r}", cfg.get("plano") == PLANO),
                             (f"K {u['k']} e {p['k']} (o plano: {K_POR_BASE})", u["k"] == K_POR_BASE and p["k"] == K_POR_BASE)) if not ok]
    if erros:
        raise ValueError(f"a run segue o plano a letra: {erros}")
    return FASE


def rodar(cfg: dict, pasta: Path, processos: int, caminho_config: Path | None = None) -> dict:
    if processos > MAX_PROCESSOS:
        raise ValueError(f"no maximo {MAX_PROCESSOS} processos (V3-D8)")
    modo = modo_da_config(cfg)
    if pasta.exists():
        raise FileExistsError(f"{pasta} ja existe: a run se recusa a gravar por cima (uma vez; secao 6)")
    unidades = bv.unidades_derivadas(cfg["unidades"]["bases"], int(cfg["unidades"]["k"]), PREFIXO)
    unidades_par = bv.unidades_derivadas(cfg["pares"]["bases"], int(cfg["pares"]["k"]), PREFIXO_PAR)
    pasta.mkdir(parents=True)
    inicio = time.time()
    rc = orq.rc
    meta = {"modo": modo, "fase": FASE, "plano": PLANO, "plano_sha256": rc._sha_arquivo(RAIZ / PLANO), "config": cfg,
            "config_arquivo": None if caminho_config is None else rc._relativo(caminho_config),
            "config_sha256": None if caminho_config is None else rc._sha_arquivo(caminho_config),
            "comando": " ".join(["python", *sys.argv]) if sys.argv and sys.argv[0] else None,
            "python": platform.python_version(), "node": V._versao_node(),
            "orquestrador_sha256": rc._sha_arquivo(Path(__file__)), "orquestrador_c2_sha256": rc._sha_arquivo(Path(C2.__file__)),
            **{f"{n}_sha256": rc._sha_arquivo(Path(mod.__file__)) for n, mod in (("acoplamento", CA), ("social_par_a0", A0), ("sonda", SA),
                                                                                ("valuation_conserto", VC), ("valuation_v2", V),
                                                                                ("prototipo", orq), ("c4", ma), ("longe_regular", lr))},
            "git_head": rc._git("rev-parse", "HEAD"), "git_limpo": rc._git("status", "--porcelain") == "", "processos": processos,
            "unidades": unidades, "unidades_par": unidades_par, "celulas": [list(c) for c in CELULAS],
            "bracos": {b: {k: vars(v) for k, v in montar(b).items()} for b in BRACOS}, "faixa": list(FAIXA),
            "sha256": {n: rc._sha_arquivo(RAIZ / "digilab" / n) for n in ("config.py", "corpo.py", "motor_corpo.py", "engine.py", "metrics.py",
                                                                         "mundo.py", "grupo.py")}
            | {f"digibrain/{q.name}": rc._sha_arquivo(q) for q in sorted((RAIZ / "digilab" / "digibrain").glob("*.py"))},
            "inicio": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(inicio))}
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    t0 = time.perf_counter()
    registros = [r for s in rc._executar([(tarefa, (cfg, u, str(pasta))) for u in unidades], processos) for r in s]
    meta["vidas_parede_s"] = time.perf_counter() - t0
    if len(registros) != len(unidades) * len(BRACOS) * len(CELULAS):
        raise RuntimeError(f"{len(registros)} vidas, eram {len(unidades) * len(BRACOS) * len(CELULAS)}")
    t1 = time.perf_counter()
    pares = [r for s in rc._executar([(tarefa_par, (cfg, u, str(pasta))) for u in unidades_par], processos) for r in s]
    meta["pares_parede_s"] = time.perf_counter() - t1
    if len(pares) != len(unidades_par) * len(BRACOS):
        raise RuntimeError(f"{len(pares)} pares, eram {len(unidades_par) * len(BRACOS)}")
    bv._gravar(pasta / "medidas.json", bv._dump(sorted(registros, key=lambda r: r["vida"])))
    bv._gravar(pasta / "pares.json", bv._dump(sorted(pares, key=lambda r: r["par"])))
    lidos = json.loads((pasta / "medidas.json").read_text(encoding="utf-8"))
    pares_lidos = json.loads((pasta / "pares.json").read_text(encoding="utf-8"))
    resultado = {"modo": modo, "fase": FASE, "plano": PLANO, "unidades": len(unidades), "unidades_par": len(unidades_par),
                 "vidas": len(lidos), "pares": len(pares_lidos), **analisar(lidos, pares_lidos)}
    bv._gravar(pasta / "resultado.json", bv._dump(resultado))
    V.tar_deterministico(pasta / "vidas", pasta / "vidas.tar.gz")
    V.tar_deterministico(pasta / "pares", pasta / "pares.tar.gz")
    nomes = ["medidas.json", "pares.json", "resultado.json", "vidas.tar.gz", "pares.tar.gz"]
    meta["fim"] = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
    meta["duracao_s"] = time.time() - inicio
    meta["artefatos_sha256"] = {n: bv._sha(pasta / n) for n in nomes}
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    return {"meta": meta, "registros": registros, "pares": pares, "resultado": resultado}


def _resumo(r: dict) -> str:
    """o resumo no console, ASCII puro"""
    return json.dumps({"modo": r["modo"], "vidas": r["vidas"], "pares": r["pares"], "veredito": r["veredito"],
                       "F": {b: {k: r["criterios"][b]["F"][k] for k in ("media", "ic95", "p_unilateral")} for b in CONTRA_CTRL}},
                      indent=1, ensure_ascii=True, default=str)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--config", required=True)
    ap.add_argument("--saida", default=None)
    ap.add_argument("--processos", type=int, default=1)
    a = ap.parse_args()
    caminho = Path(a.config)
    cfg = json.loads(caminho.read_text(encoding="utf-8"))
    if modo_da_config(cfg) == "fumaca":
        if a.saida is None:
            raise SystemExit(f"a fumaca precisa de --saida (fora de {SAIDA})")
    else:
        pre_run.exigir(ORQUESTRADOR, a.config, a.processos)             # o plano da origin/main e a V3-D8, antes de tudo
    print(_resumo(rodar(cfg, Path(a.saida) if a.saida else RAIZ / SAIDA, a.processos, caminho)["resultado"]))


if __name__ == "__main__":
    main()
