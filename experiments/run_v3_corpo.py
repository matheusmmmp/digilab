"""CORPO C2, a ablacao do corpo (docs/PLANO_ANALISE_V3_CORPO.md, APROVADO pelo Matheus em 2026-11-18, com as D-CO-1 a D-CO-10 DECIDIDAS).

Pergunta (secao 1): alguma das opcoes do mapa (docs/MAPA_CORPO.md) reduz a tensao entre a fome e a energia sem piorar o bem-estar?

Os bracos (secao 2): o CTRL (o REL da VALUATION, o corpo de hoje) e, cada um mudando so a sua chave:
- D: a falta de combustivel sobe a fome (`ConfigAcoplamentoCorpo` ligada, a run do #1002);
- DE: a D e a digestao inteira (`ConfigDigestaoCorpo.inteira`);
- DC5: a D e o reflexo suave (`ConfigConsertoValuation.reflexo_suave`).

O bloco I (secoes 3 e 4): o pet sozinho, a vida do `run_v3_corpo_acoplamento.viver` (a da VALUATION), 4 bracos x as 12 celulas da C4 x
200 unidades independentes (bases 104001...104200, k = 1). O bloco II: o substrato social, um par VIVO por unidade e braco no instrumento
da SOCIAL_PAR A0 (`run_v3_social_par_a0`: o pet de hoje com a CO7, a perturbacao, a janela de 96 decisoes), 100 unidades (bases
104301...104400, k = 1, prefixo corpo_par), com as chaves do braco nos dois pets.

A analise (secao 5): o primario F e o braco - CTRL na taxa por episodio do `longe_fixo`, o t sobre as unidades, o Holm sobre os 3 p
unilaterais; as guardas B (a privacao em cada lugar e nas 12 celulas, a exaustao no `longe_fixo` e nas 12) e S (S1 os chutes por dia, S2
o T* ate o reencontro), vinculantes; a leitura de cada braco: ganho, perda, nulo ou indeterminado.

A trava (secao 0): sem o "APROVADO pelo Matheus" no cabecalho do plano, sem a faixa em FAIXAS_RESERVADAS, com a pasta de saida ja
existente ou fora das bases do plano, o orquestrador recusa; a run passa antes pelo `tools/pre_run.py`. A fumaca usa as sementes dos testes.

Uso: python experiments/run_v3_corpo.py --config experiments/configs/v3_corpo/run.json --processos 4
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import platform
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tools"))

import bancada_v2 as bv  # noqa: E402
import exportar_gabarito_co6 as e6  # noqa: E402
import pre_run  # noqa: E402
import run_v2_longe_regular as lr  # noqa: E402
import run_v2_memoria_autobio as ma  # noqa: E402
import run_v3_corpo_acoplamento as CA  # noqa: E402
import run_v3_social_par_a0 as A0  # noqa: E402
import run_v3_valuation as V  # noqa: E402
import run_v3_valuation_conserto as VC  # noqa: E402
import sonda_v3_corpo_acoplamento as SA  # noqa: E402
from bancada import parceiro as pc  # noqa: E402
from bancada.faixas import FAIXAS_RESERVADAS  # noqa: E402
from bancada.regras_mundo import simular_vida_fisico  # noqa: E402
from digilab.config import (CONFIG_ACOPLAMENTO_CORPO, CONFIG_ACOPLAMENTO_CORPO_LIGADA, CONFIG_CONSERTO_VALUATION,  # noqa: E402
                            CONFIG_DIGESTAO_CORPO, CONFIG_DIGESTAO_CORPO_INTEIRA, CONFIG_DIGIBRAIN_INATOS, CONFIG_GRUPO_LIGADA,
                            CONFIG_PADRAO, CONFIG_REFLEXO_SUAVE)
from digilab.digibrain import DigiBrain  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.grupo import RegistroGrupo, reproduzir_grupo, sementes_do_grupo  # noqa: E402
from digilab.metrics import holm  # noqa: E402
from digilab.mundo import DonoComLugar  # noqa: E402
from digilab.temperamento import NEUTRO  # noqa: E402

orq = VC.orq
PLANO = "docs/PLANO_ANALISE_V3_CORPO.md"
ORQUESTRADOR = "experiments/run_v3_corpo.py"
FASE = "corpo"
PREFIXO, PREFIXO_PAR = orq.PREFIXO, "corpo_par"
BASES_I = tuple(range(104001, 104201))                        # secao 4, D-CO-5 e D-CO-7: 200 sementes independentes
BASES_II = tuple(range(104301, 104401))                       # o bloco II: 100 pares
FAIXA = (104001, 104400)
K_POR_BASE = 1
DIAS, ORCAMENTO_POR_DIA = V.DIAS, V.ORCAMENTO_POR_DIA
SAIDA = "artifacts_v3_corpo/ablacao"                          # secao 6
MAX_PROCESSOS = V.MAX_PROCESSOS
CELULAS = ma.CELULAS                                          # as 12 da C4
PRIMARIO = ma.PRIMARIO                                        # o longe_fixo
LUGARES_PRIVACAO = (("comedouro", ma.GUARDA), ("longe", ma.SORTEADO), ("longe_fixo", PRIMARIO), ("12_celulas", None))   # D-CO-10
CONTROLE = "CTRL"
TRATADOS = ("D", "DE", "DC5")
BRACOS = (CONTROLE, *TRATADOS)
MARGEM = V.MARGEM                                             # o 0,032 da C4, da A1 e da VALUATION, SEM FONTE
ALFA = 0.025                                                  # secao 5: o Holm sobre os 3 bracos (D-CO-9)
FRACAO_DELTA_S = 0.10                                         # D-CO-6: o delta de S1 e S2, 10 % do nivel do CTRL, SEM FONTE
EPISODIO, PRIVACAO, EXAUSTAO = V.EPISODIO, V.PRIVACAO, V.EXAUSTAO
CHAVES_CONFIG = {"descricao", "fase", "plano", "dias", "orcamento_por_dia", "unidades", "pares"}
S = CONFIG_DIGIBRAIN_INATOS.escala


# ================================================================== os bracos (secao 2)
def montar(braco: str) -> dict:
    """as chaves do braco: o acoplamento (a D), a digestao (a E) e o conserto do M-ARB (a C5); o resto e o REL da VALUATION"""
    if braco not in BRACOS:
        raise ValueError(f"braco {braco!r}: so {BRACOS}")
    return {"acoplamento": CONFIG_ACOPLAMENTO_CORPO if braco == CONTROLE else CONFIG_ACOPLAMENTO_CORPO_LIGADA,
            "digestao": CONFIG_DIGESTAO_CORPO_INTEIRA if braco == "DE" else CONFIG_DIGESTAO_CORPO,
            "conserto": CONFIG_REFLEXO_SUAVE if braco == "DC5" else CONFIG_CONSERTO_VALUATION}


def _kw_corpo(m: dict) -> dict:
    return {"cfg_acoplamento_corpo": m["acoplamento"], "cfg_digestao_corpo": m["digestao"]}


# ================================================================== o bloco I: o pet sozinho
def fabricas(braco: str, dono: str, semente: int, dias: int, orcamento_por_dia: int) -> tuple:
    """as fabricas do `run_v3_corpo_acoplamento.fabricas` (o REL da VALUATION, o MotorSonda), com as tres chaves do braco"""
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
    """uma vida do bloco I: a do `run_v3_corpo_acoplamento.viver`, com as fabricas do braco e a leitura da energia baixa por decisao"""
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
    if corpo.ca != m["acoplamento"] or corpo.cd != m["digestao"]:
        raise RuntimeError(f"{braco}: o corpo tem o acoplamento {corpo.ca} e a digestao {corpo.cd}, o braco pede {m}")
    if arb.cv != m["conserto"]:
        raise RuntimeError(f"{braco}: o M-ARB tem o conserto {arb.cv}, o braco pede {m['conserto']}")
    alvo = dict(corpo.grafo.emissor("falta_combustivel").efeitos)
    esperado = {"cansaco": corpo.cc.falta_cansaco} if braco == CONTROLE else {"fome": m["acoplamento"].falta_fome}
    if alvo != esperado:
        raise RuntimeError(f"{braco}: a ponte da falta de combustivel e {alvo}, o braco pede {esperado}")
    if braco == "DE" and corpo.descartado_total != 0:
        raise RuntimeError(f"{braco}: a digestao inteira descartou comida ({corpo.descartado_total})")


def conferir_vida(braco: str, motor, registro, baixas: list[bool]) -> None:
    """secao 7: as chaves, a ponte, o cansaco sem a falta (bracos com a D) e o reflexo de cada braco, decisao a decisao"""
    arb = orq.cerebro_de(registro).m.arb
    conferir_braco(braco, motor.corpo, arb)
    if braco != CONTROLE and (motor.contabil.acum["falta_combustivel"] or motor.contabil.ticks_falta):
        raise RuntimeError(f"{braco}: o cansaco subiu pela falta de combustivel com a D ligada")
    if braco == "DC5":
        if arb.reflexos != 0 or arb.suaves != sum(baixas):
            raise RuntimeError(f"DC5: {arb.reflexos} reflexos e {arb.suaves} pesos suaves, com {sum(baixas)} decisoes de energia baixa")
    else:
        VC.conferir_conserto("REL", registro, baixas)           # o reflexo de hoje, decisao a decisao
        if arb.suaves != 0:
            raise RuntimeError(f"{braco}: o reflexo suave somou peso sem a chave")


def _vida(cfg: dict, braco: str, dono: str, lugar: str, unidade: dict, pasta: str) -> dict:
    c0, p0 = time.process_time(), time.perf_counter()
    motor, registro, fab, categorias, baixas = viver(braco, dono, lugar, unidade["semente"], cfg["dias"], cfg["orcamento_por_dia"])
    arquivo = Path(pasta) / "vidas" / braco / f"{dono}_{lugar}_{unidade['semente']}.jsonl"
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    arquivo.write_text(motor.log.para_jsonl(), encoding="utf-8", newline="\n")
    orq.conferir_replay(motor, fab, unidade["semente"], arquivo.read_text(encoding="utf-8"))
    orq.conferir_cenario(motor, registro)
    orq.conferir_mecanismo("REL", registro, None)
    ma.conferir_memoria("REL", orq.cerebro_de(registro))
    fins = ma.conferir_fins("REL", registro)
    conferir_vida(braco, motor, registro, baixas)
    med = orq.medidas(motor, registro, "REL", cfg["dias"], True)
    arb = orq.cerebro_de(registro).m.arb
    return {"vida": f"{braco}|{dono}|{lugar}|{unidade['semente']}", "braco": braco, "dono": dono, "lugar": lugar,
            "semente": unidade["semente"], "base": unidade["base"], "k": unidade["k"], **med,
            "corpo": lr.medidas_do_corpo(motor, registro, cfg["dias"]), "fins_conferidos": fins,
            "memoria": ma.medidas_memoria(registro, cfg["dias"], categorias),
            "valuation": V.descritivo_valuation(registro, med), "acoplamento": CA.medidas_acoplamento(motor, registro, baixas),
            "c5": {"suaves": arb.suaves}, "descartado": motor.corpo.descartado_total,
            "custo": {"vida_cpu": time.process_time() - c0, "vida_parede": time.perf_counter() - p0}}


def tarefa(cfg: dict, unidade: dict, pasta: str) -> list[dict]:
    return [_vida(cfg, b, dono, lugar, unidade, pasta) for b in BRACOS for dono, lugar in CELULAS]


# ================================================================== o bloco II: o substrato social
def fabricas_par(braco: str, semente_pet: int) -> tuple:
    """o pet de hoje da SOCIAL_PAR A0 (`run_v3_social_par_a0.fabricas_do_jogo`: o modular com a CO7), com as chaves do braco"""
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
def _celulas(lugar: str | None) -> tuple:
    return CELULAS if lugar is None else tuple(c for c in CELULAS if c[1] == lugar)


def _difs(registros: list[dict], medida, lugar: str | None, a: str, b: str = CONTROLE) -> dict:
    return orq.por_unidade(registros, a, b, medida, _celulas(lugar))


def _guarda(registros: list[dict], medida, lugar: str | None, braco: str, reprova: str) -> dict:
    e = ma.estimativa(_difs(registros, medida, lugar, braco), MARGEM)
    return {**e, "contraste": f"{braco} - CTRL", "lugar": lugar or "as 12 celulas", "reprova_com": reprova,
            "passa": e["classe"]["classe"] != reprova}


def _por_par(pares: list[dict], medida) -> dict:
    """{(base, semente): medida(braco)} por braco; o par sem valor (None) fica fora"""
    out: dict = {b: {} for b in BRACOS}
    for p in pares:
        x = medida(p)
        if x is not None:
            out[p["braco"]][(p["base"], p["semente"])] = x
    return out


def _s(pares: list[dict], medida, braco: str, reprova: str) -> dict:
    """uma guarda do substrato (D-CO-6): braco - CTRL por par, nos pares com valor nos dois, com a classe de A6.6 e o delta de 10 % do
    nivel do CTRL nesses pares"""
    v = _por_par(pares, medida)
    comuns = sorted(set(v[braco]) & set(v[CONTROLE]))
    nivel = None if not comuns else sum(v[CONTROLE][k] for k in comuns) / len(comuns)
    delta = None if nivel is None else FRACAO_DELTA_S * abs(nivel)
    difs = {k: v[braco][k] - v[CONTROLE][k] for k in comuns}
    ic = orq.ic_t([d for _, d in sorted(difs.items())])
    cl = lr.classe({"ic_inferior": ic["ic_inferior"], "ic_superior": ic["ic_superior"], "motivo": ic["motivo"]}, delta or 0.0)
    return {"n": ic["n"], "media": ic["media"], "dp": ic["dp"], "ic95": {"ic_inferior": ic["ic_inferior"], "ic_superior": ic["ic_superior"]},
            "nivel_ctrl": nivel, "delta": delta, "classe": cl, "contraste": f"{braco} - CTRL", "reprova_com": reprova,
            "passa": cl["classe"] != reprova}


CHUTES = lambda p: p["chutes_por_dia"]                                                        # noqa: E731
T_REENCONTRO = lambda p: p["janela"]["t_perto"] if p["janela"]["cabe"] else None              # noqa: E731


def criterios(registros: list[dict], pares: list[dict], boot: dict = orq.BOOTSTRAP) -> dict:
    out = {}
    for b in TRATADOS:
        c = orq.contraste_t(_difs(registros, EPISODIO, PRIMARIO, b), boot)
        ic = {"ic_inferior": c["ic95"]["ic_inferior"], "ic_superior": c["ic95"]["ic_superior"], "motivo": c["motivo"]}
        F = {"contraste": f"{b} - CTRL, a taxa por episodio, longe_fixo", **c, "classe": ma.classe(ic, MARGEM), "margem": MARGEM}
        B = {**{f"privacao_{onde}": _guarda(registros, PRIVACAO, lugar, b, "> 0") for onde, lugar in LUGARES_PRIVACAO},
             "exaustao_longe_fixo": _guarda(registros, EXAUSTAO, PRIMARIO, b, "> 0"),
             "exaustao_12_celulas": _guarda(registros, EXAUSTAO, None, b, "> 0")}
        Sg = {"S1_chutes_por_dia": _s(pares, CHUTES, b, "< 0"), "S2_tempo_ate_o_reencontro": _s(pares, T_REENCONTRO, b, "> 0")}
        out[b] = {"F": F, "B": B, "S": Sg}
    h = holm({b: out[b]["F"]["p_unilateral"] for b in TRATADOS}, ALFA)
    for b in TRATADOS:
        out[b]["F"]["holm"] = h[b]
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
    por_braco = {b: leitura_do_braco(cr[b]) for b in TRATADOS}
    ganhos = [b for b, x in por_braco.items() if x["leitura"] == "ganho"]
    return {"bracos": por_braco, "ganhos": ganhos,
            "geral": "ao menos um braco com ganho" if ganhos else "tensao nao localizada por estas opcoes (secao 1): o programa para no CHECKPOINT C2.5",
            "proximo": "o CHECKPOINT C2.5: o diagnostico vai ao Matheus; perda vai ao Matheus pelo trade-off"}


def descritivo(registros: list[dict], pares: list[dict]) -> dict:
    """os descritivos da secao 5, por braco e lugar, sem classe; os do bloco II"""
    sem_classe = lambda e: {k: v for k, v in e.items() if k != "classe"}   # noqa: E731
    lugares = (("longe_fixo", PRIMARIO), ("12_celulas", None), ("comedouro", ma.GUARDA), ("longe", ma.SORTEADO))
    out = {}
    for onde, lugar in lugares:
        out[onde] = {n: {"niveis": {b: sem_classe(ma.estimativa(orq.por_unidade(registros, b, None, f, _celulas(lugar)))) for b in BRACOS},
                         **{f"{b} - CTRL": sem_classe(ma.estimativa(_difs(registros, f, lugar, b))) for b in TRATADOS}}
                     for n, f in CA.DESCRITIVOS.items()}
    out["bloco_II"] = {b: {"pares": sum(1 for p in pares if p["braco"] == b),
                           "chutes_por_dia_media": _media([p["chutes_por_dia"] for p in pares if p["braco"] == b]),
                           "chutes_A_media": _media([p["chutes"]["A"] for p in pares if p["braco"] == b]),
                           "chutes_B_media": _media([p["chutes"]["B"] for p in pares if p["braco"] == b]),
                           "fracao_pares_com_chute": _media([float(p["chutes"]["A"] + p["chutes"]["B"] > 0) for p in pares if p["braco"] == b]),
                           "fracao_janela_cabe": _media([float(p["janela"]["cabe"]) for p in pares if p["braco"] == b]),
                           "t_reencontro_media": _media([T_REENCONTRO(p) for p in pares if p["braco"] == b and T_REENCONTRO(p) is not None])}
                       for b in BRACOS}
    return out


def _media(xs: list) -> float | None:
    return None if not xs else sum(xs) / len(xs)


def analisar(registros: list[dict], pares: list[dict], boot: dict = orq.BOOTSTRAP) -> dict:
    cr = criterios(registros, pares, boot)
    return {"criterios": cr, "veredito": veredito(cr), "descritivo": descritivo(registros, pares),
            "nao_demonstra": ["nada sobre o jogo web (as chaves ficam desligadas nele)",
                              "nada sobre a calibracao do cuidado (E1 e E2) nem sobre o I-PAD da LONGE_GEOMETRIA",
                              "nada sobre outros tamanhos nem sobre combinacoes fora dos bracos",
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
            "orquestrador_sha256": rc._sha_arquivo(Path(__file__)),
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
                       "F": {b: {k: r["criterios"][b]["F"][k] for k in ("media", "ic95", "p_unilateral")} for b in TRATADOS}},
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
