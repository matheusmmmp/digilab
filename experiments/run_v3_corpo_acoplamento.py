"""CORPO_ACOPLAMENTO: a opcao D numa run, uma vez (docs/PLANO_ANALISE_V3_CORPO_ACOPLAMENTO.md; docs/TAREFA_V3_CORPO_ACOPLAMENTO.md).

Pergunta (a secao 1 do plano): com a `ConfigAcoplamentoCorpo` ligada (a falta de combustivel sobe a fome, e nao o cansaco), a vida da
VALUATION tem menos decisoes em que o pet precisa comer e descansar ao mesmo tempo, sem piorar a privacao, a exaustao e a taxa de
fechamento dos episodios de fome?

Os bracos (a secao 4), na mesma unidade (base, semente), nas 12 celulas da C4:
  - REL: o REL da C4 e da VALUATION (o controle), o corpo de hoje;
  - D: o REL com a ConfigAcoplamentoCorpo ligada; uma mudanca so.

A vida e a da VALUATION (`run_v3_valuation_conserto.viver`, com o conserto desligado nos dois bracos): o pet sozinho, 14 dias, orcamento 16.
O motor e o `MotorSonda` (experiments/sonda_v3_corpo_acoplamento.py), o MotorGravaCorpo com a contabilidade do cansaco so de leitura (o teste
da sonda confere que a vida sai byte a byte a de sempre). Cada vida passa pelo replay do disco, pelo T-CENARIO-1, pelas conferencias da C4,
pela do reflexo da VALUATION e pela do corpo do braco (a secao 3: a ponte do braco no grafo, a fonte de cansaco da falta zerada no D);
senao falha alto.

A analise (a secao 5, escrita antes): P (os conflitos, a fracao das decisoes com a energia abaixo de `lambda_sono` e a fome urgente, media
das 12 celulas: REL - D na classe "> 0", que e o D - REL "< 0" do plano, e p unilateral < 0,025 pelo t sobre as unidades), G1 e G2 (a
privacao e a exaustao, no `longe_fixo` e nas 12 celulas, nenhuma "> 0" em D - REL) e G3 (a taxa por episodio, no `longe_fixo` e nas 12
celulas, nenhuma "< 0" em D - REL). O veredito passa so com todas. O D ("desliga nao muda") e o teste do gabarito, antes da run.

A trava: a run de verdade passa pelo `tools/pre_run.py` (o plano no disco igual ao da `origin/main`, a faixa, nenhuma outra run, no maximo
4 processos) e recusa rodar sem o "APROVADO pelo Matheus" no cabecalho do plano, sem a faixa em FAIXAS_RESERVADAS e com a pasta de saida
ja existente. A fumaca usa as sementes dos testes e nao passa pelo pre_run.
Uso: python experiments/run_v3_corpo_acoplamento.py --config experiments/configs/v3_corpo_acoplamento/run.json --processos 4
"""
from __future__ import annotations

import argparse
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
import run_v2_longe_regular as lr  # noqa: E402
import run_v2_memoria_autobio as ma  # noqa: E402
import run_v3_valuation as V  # noqa: E402
import run_v3_valuation_conserto as VC  # noqa: E402
import pre_run  # noqa: E402
import sonda_v3_corpo_acoplamento as SA  # noqa: E402
from bancada.faixas import FAIXAS_RESERVADAS  # noqa: E402
from bancada.regras_mundo import simular_vida_fisico  # noqa: E402
from digilab.config import (CONFIG_ACOPLAMENTO_CORPO, CONFIG_ACOPLAMENTO_CORPO_LIGADA, CONFIG_CONSERTO_VALUATION,  # noqa: E402
                            CONFIG_DIGIBRAIN_INATOS, CONFIG_PADRAO)
from digilab.digibrain import DigiBrain  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.mundo import DonoComLugar  # noqa: E402
from digilab.temperamento import NEUTRO  # noqa: E402

orq = VC.orq
PLANO = "docs/PLANO_ANALISE_V3_CORPO_ACOPLAMENTO.md"
ORQUESTRADOR = "experiments/run_v3_corpo_acoplamento.py"
FASE = "corpo_acoplamento"
PREFIXO = orq.PREFIXO
BASES = (100101, 100202, 100303, 100404, 100505)              # secao 4 (D-CA-10, aprovada em 2026-11-18)
FAIXA = (100101, 100505)
K_POR_BASE = 40
DIAS, ORCAMENTO_POR_DIA = V.DIAS, V.ORCAMENTO_POR_DIA
SAIDA = "artifacts_v3_corpo_acoplamento/run"                  # secao 6
MAX_PROCESSOS = V.MAX_PROCESSOS
CELULAS = ma.CELULAS                                          # as 12 da C4
PRIMARIO = ma.PRIMARIO                                        # o longe_fixo
BRACOS = ("REL", "D")
CONTROLE, TRATADO = "REL", "D"
MARGEM = V.MARGEM                                             # D-CA-12: o 0,032 da VALUATION (D-VAL-20)
ALFA = 0.025                                                  # secao 5: um primario so, unilateral
EPISODIO, PRIVACAO, EXAUSTAO = V.EPISODIO, V.PRIVACAO, V.EXAUSTAO
CONFLITOS = lambda r: r["acoplamento"]["conflitos"]           # noqa: E731
CHAVES_CONFIG = V.CHAVES_CONFIG
S = CONFIG_DIGIBRAIN_INATOS.escala


# ================================================================== os bracos
def montar(braco: str) -> dict:
    """a ConfigDigibrain e os inatos do REL da VALUATION (o conserto desligado) e o acoplamento do braco"""
    if braco not in BRACOS:
        raise ValueError(f"braco {braco!r}: so {BRACOS}")
    return {"cd": orq.config_do_braco("REL", conserto=True), "inatos": CONFIG_DIGIBRAIN_INATOS, "conserto": CONFIG_CONSERTO_VALUATION,
            "acoplamento": CONFIG_ACOPLAMENTO_CORPO_LIGADA if braco == TRATADO else CONFIG_ACOPLAMENTO_CORPO}


def fabricas(braco: str, dono: str, semente: int, dias: int, orcamento_por_dia: int) -> tuple:
    """as fabricas da VALUATION (`run_v3_valuation_conserto.fabricas` com o REL), com o MotorSonda e o acoplamento do braco no motor"""
    m = montar(braco)
    cc = orq.bancada(dias, orcamento_por_dia).cfg_corpo_de(bv.EspecVida(dono, VC.gl.BRACO_V11, semente))

    def fp(cfg=None):
        return orq.Registro(DigiBrain(cfg or CONFIG_PADRAO, m["cd"], orq.CM, inatos=m["inatos"], semente=semente,
                                      cfg_conserto=m["conserto"]), S)

    def fm(politica, cfg, s):
        return SA.MotorSonda(politica, cfg, s, NEUTRO, "brasa", obediencia_desligada=True, cfg_mundo=orq.CM, cfg_corpo=cc,
                             cfg_acoplamento_corpo=m["acoplamento"])

    return fp, fm


def viver(braco: str, dono: str, lugar: str, semente: int, dias: int, orcamento_por_dia: int):
    """uma vida: a do `run_v3_valuation_conserto.viver`, com as fabricas do braco e o involucro de leitura do reflexo (a energia abaixo de
    `lambda_sono` em cada decisao). Devolve (o motor, o registro, as fabricas, as categorias, as leituras do reflexo)."""
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


# ================================================================== a conferencia do corpo (secao 3; falha alta)
def conferir_corpo(braco: str, motor) -> None:
    """o corpo da vida tem a ponte do braco: o cansaco no REL, a fome no D; no D, nenhum tick subiu o cansaco pela falta"""
    m = montar(braco)
    corpo = motor.corpo
    if corpo.ca != m["acoplamento"]:
        raise RuntimeError(f"{braco}: o corpo da vida tem o acoplamento {corpo.ca}, o braco pede {m['acoplamento']}")
    alvo = dict(corpo.grafo.emissor("falta_combustivel").efeitos)
    esperado = {"fome": m["acoplamento"].falta_fome} if braco == TRATADO else {"cansaco": corpo.cc.falta_cansaco}
    if alvo != esperado:
        raise RuntimeError(f"{braco}: a ponte da falta de combustivel e {alvo}, o braco pede {esperado}")
    if braco == TRATADO and (motor.contabil.acum["falta_combustivel"] or motor.contabil.ticks_falta):
        raise RuntimeError(f"{braco}: o cansaco subiu pela falta de combustivel com a chave ligada")


def medidas_acoplamento(motor, registro, baixas: list[bool]) -> dict:
    """os conflitos (o primario) e os descritivos da secao 5, pela sonda: a fome urgente na energia baixa e na boa, o sono, o cansaco por
    fonte e o combustivel abaixo de C/4"""
    dec = SA.decisoes_da_vida(motor, registro, baixas)          # confere a contabilidade e a energia baixa, decisao a decisao
    c = orq.cerebro_de(registro)
    lim = SA.limiar_cansaco(motor.corpo.C, motor.corpo.S, c.inatos.lambda_sono)
    corte = SA.cortar(dec, lim, motor.corpo.C, motor.corpo.cc.falta_limiar)
    serie = motor.serie_sonda
    n, baixa, ambas, urg = corte["decisoes"], corte["energia_baixa"], corte["ambas"], corte["fome_urgente"]
    boas = n - baixa
    return {"decisoes": n, "energia_baixa": baixa, "ambas": ambas, "fome_urgente": urg, "conflitos": ambas / n,
            "fracao_fome_urgente_na_energia_baixa": ambas / baixa if baixa else None,
            "fracao_fome_urgente_na_energia_boa": (urg - ambas) / boas if boas else None,
            "fracao_energia_baixa": baixa / n, "classes": corte["classes"],
            "fracao_ticks_dormindo": sum(1 for x in serie if x[4]) / len(serie),
            "fracao_ticks_combustivel_abaixo": sum(1 for x in serie if x[3] < motor.corpo.cc.falta_limiar) / len(serie),
            "cansaco_por_fonte": dict(serie[-1][5])}


# ================================================================== a vida
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
    VC.conferir_conserto("REL", registro, baixas)               # o reflexo e o do REL nos dois bracos, decisao a decisao
    conferir_corpo(braco, motor)
    med = orq.medidas(motor, registro, "REL", cfg["dias"], True)
    return {"vida": f"{braco}|{dono}|{lugar}|{unidade['semente']}", "braco": braco, "dono": dono, "lugar": lugar,
            "semente": unidade["semente"], "base": unidade["base"], "k": unidade["k"], **med,
            "corpo": lr.medidas_do_corpo(motor, registro, cfg["dias"]), "fins_conferidos": fins,
            "memoria": ma.medidas_memoria(registro, cfg["dias"], categorias),
            "valuation": V.descritivo_valuation(registro, med), "acoplamento": medidas_acoplamento(motor, registro, baixas),
            "custo": {"vida_cpu": time.process_time() - c0, "vida_parede": time.perf_counter() - p0}}


def tarefa(cfg: dict, unidade: dict, pasta: str) -> list[dict]:
    return [_vida(cfg, b, dono, lugar, unidade, pasta) for b in BRACOS for dono, lugar in CELULAS]


# ================================================================== a analise (secao 5, escrita antes)
def _celulas(lugar: str | None) -> tuple:
    return CELULAS if lugar is None else tuple(c for c in CELULAS if c[1] == lugar)


def _difs(registros: list[dict], medida, lugar: str | None, a: str = TRATADO, b: str = CONTROLE) -> dict:
    return orq.por_unidade(registros, a, b, medida, _celulas(lugar))


def _guarda(registros: list[dict], medida, lugar: str | None, reprova: str) -> dict:
    """uma guarda: D - REL com a classe de A6.6 (D-CA-12); reprova com a classe `reprova`"""
    e = ma.estimativa(_difs(registros, medida, lugar), MARGEM)
    return {**e, "contraste": "D - REL", "lugar": lugar or "as 12 celulas", "reprova_com": reprova, "passa": e["classe"]["classe"] != reprova}


def criterios(registros: list[dict], boot: dict = orq.BOOTSTRAP) -> dict:
    # o p unilateral do contraste_t e para a media > 0: a P sai pelo REL - D ("> 0"), o D - REL "< 0" do plano
    difs = _difs(registros, CONFLITOS, None, CONTROLE, TRATADO)
    c = orq.contraste_t(difs, boot)
    ic = {"ic_inferior": c["ic95"]["ic_inferior"], "ic_superior": c["ic95"]["ic_superior"], "motivo": c["motivo"]}
    cl = ma.classe(ic, MARGEM)
    p = c["p_unilateral"]
    passa_p = cl["classe"] == "> 0" and p is not None and p < ALFA
    trivial = cl["classe"] == "≈ 0" and cl["sinal"] == "+"
    P = {"contraste": "REL - D, os conflitos (a fracao das decisoes com a energia baixa e a fome urgente), media das 12 celulas", **c,
         "classe": cl, "margem": MARGEM, "margem_efetiva": lr.margem_efetiva(ma.estimativa(difs, MARGEM)["dp"], c["n"]), "alfa": ALFA,
         "passa": passa_p, "efeito_trivial": trivial,
         "d_menos_rel": {"media": None if c["media"] is None else -c["media"],
                         "ic95": None if ic["ic_inferior"] is None else [-ic["ic_superior"], -ic["ic_inferior"]]}}
    G1 = {"longe_fixo": _guarda(registros, PRIVACAO, PRIMARIO, "> 0"), "12_celulas": _guarda(registros, PRIVACAO, None, "> 0")}
    G2 = {"longe_fixo": _guarda(registros, EXAUSTAO, PRIMARIO, "> 0"), "12_celulas": _guarda(registros, EXAUSTAO, None, "> 0")}
    G3 = {"longe_fixo": _guarda(registros, EPISODIO, PRIMARIO, "< 0"), "12_celulas": _guarda(registros, EPISODIO, None, "< 0")}
    return {"P": P, "G1": G1, "G2": G2, "G3": G3}


def veredito(cr: dict) -> dict:
    """a regra da secao 5: passa so com P, G1, G2 e G3 (o D e o teste do gabarito, antes da run); o efeito trivial conta como falha"""
    falhas = [] if cr["P"]["passa"] else ["P (efeito trivial)" if cr["P"]["efeito_trivial"] else "P"]
    falhas += [f"{g} ({onde})" for g in ("G1", "G2", "G3") for onde, x in cr[g].items() if not x["passa"]]
    return {"leitura": "passa" if not falhas else ("efeito trivial" if falhas == ["P (efeito trivial)"] else "falha"),
            "falhas": falhas,
            "proximo": "a D passa: ligar num pet do jogo espera o Matheus e uma rodada nova do cuidado (D-CA-7)" if not falhas else
            "a D nao passa: o resultado fica registrado como esta, e a chave continua desligada"}


DESCRITIVOS = {**V.DESCRITIVOS,
               "conflitos": CONFLITOS,
               "fracao_fome_urgente_na_energia_baixa": lambda r: r["acoplamento"]["fracao_fome_urgente_na_energia_baixa"],
               "fracao_fome_urgente_na_energia_boa": lambda r: r["acoplamento"]["fracao_fome_urgente_na_energia_boa"],
               "fracao_energia_baixa": lambda r: r["acoplamento"]["fracao_energia_baixa"],
               "fracao_ticks_dormindo": lambda r: r["acoplamento"]["fracao_ticks_dormindo"],
               "fracao_ticks_combustivel_abaixo": lambda r: r["acoplamento"]["fracao_ticks_combustivel_abaixo"]}


def descritivo(registros: list[dict]) -> dict:
    """os descritivos da secao 5, no `longe_fixo`, nas 12 celulas e por lugar: o nivel de cada braco e D - REL, sem classe"""
    sem_classe = lambda e: {k: v for k, v in e.items() if k != "classe"}   # noqa: E731
    out = {}
    lugares = (("longe_fixo", PRIMARIO), ("12_celulas", None), ("comedouro", ma.GUARDA), ("longe", ma.SORTEADO))
    for onde, lugar in lugares:
        out[onde] = {n: {"niveis": {b: sem_classe(ma.estimativa(orq.por_unidade(registros, b, None, f, _celulas(lugar)))) for b in BRACOS},
                         "D - REL": sem_classe(ma.estimativa(_difs(registros, f, lugar)))}
                     for n, f in DESCRITIVOS.items()}
    out["cansaco_por_fonte_somado"] = {b: V._somar([r for r in registros if r["braco"] == b], lambda r: r["acoplamento"]["cansaco_por_fonte"])
                                       for b in BRACOS}
    return out


def analisar(registros: list[dict], boot: dict = orq.BOOTSTRAP) -> dict:
    cr = criterios(registros, boot)
    return {"criterios": cr, "veredito": veredito(cr), "descritivo": descritivo(registros),
            "nao_demonstra": ["nada sobre o jogo web (a chave fica desligada nele, D-CA-7)",
                              "nada sobre o I-PAD da LONGE_GEOMETRIA (o sono muda; medir de novo e outra run)",
                              "nada sobre a calibracao do cuidado (E1 e E2)",
                              "nada sobre outro falta_fome alem do 500, nem com o conserto da VALUATION ou o sono que segura ligados",
                              "nada fora dos 14 dias e do mundo do MVP"]}


# ================================================================== a trava e a run
def exigir_aprovado(plano: str) -> None:
    status = [x for x in plano.splitlines() if x.startswith("**Status:")]
    if not status or not status[0].startswith("**Status: APROVADO pelo Matheus"):
        raise RuntimeError(f"o plano {PLANO} nao esta APROVADO pelo Matheus no cabecalho: {status[:1] or 'sem a linha do status'}")


def modo_da_config(cfg: dict) -> str:
    faltam, sobram = (CHAVES_CONFIG - {"descricao"}) - set(cfg), set(cfg) - CHAVES_CONFIG
    if faltam or sobram:
        raise ValueError(f"config: faltam {sorted(faltam)}, sobram {sorted(sobram)}")
    if cfg["fase"] != FASE:
        raise ValueError(f"fase {cfg['fase']!r}: so {FASE!r}")
    u = cfg["unidades"]
    bases = tuple(u["bases"])
    if u.get("prefixo") != PREFIXO or cfg["orcamento_por_dia"] != ORCAMENTO_POR_DIA or type(u.get("k")) is not int or u["k"] < 1:
        raise ValueError("config fora do plano: o prefixo, o orcamento ou o K (secao 4)")
    if bases and set(bases) <= bv.SEMENTES_TESTE:
        if not 1 <= cfg["dias"] <= DIAS:
            raise ValueError(f"fumaca com {cfg['dias']} dias: de 1 a {DIAS}")
        return "fumaca"
    if bases != BASES:
        raise bv.SementeSemPlano(f"bases {list(bases)}: so as dos testes (fumaca) ou {list(BASES)} (secao 4)")
    if not any((lo, hi) == FAIXA for lo, hi, _ in FAIXAS_RESERVADAS):
        raise bv.SementeSemPlano(f"a faixa {FAIXA} nao esta em FAIXAS_RESERVADAS (secao 4)")
    exigir_aprovado((RAIZ / PLANO).read_text(encoding="utf-8"))
    erros = [m for m, ok in ((f"dias {cfg['dias']} (o plano: {DIAS})", cfg["dias"] == DIAS), (f"plano {cfg.get('plano')!r}", cfg.get("plano") == PLANO),
                             (f"K por base {u['k']} (o plano: {K_POR_BASE})", u["k"] == K_POR_BASE)) if not ok]
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
    pasta.mkdir(parents=True)
    inicio = time.time()
    rc = orq.rc
    meta = {"modo": modo, "fase": FASE, "plano": PLANO, "plano_sha256": rc._sha_arquivo(RAIZ / PLANO), "config": cfg,
            "config_arquivo": None if caminho_config is None else rc._relativo(caminho_config),
            "config_sha256": None if caminho_config is None else rc._sha_arquivo(caminho_config),
            "comando": " ".join(["python", *sys.argv]) if sys.argv and sys.argv[0] else None,
            "python": platform.python_version(), "node": V._versao_node(),
            "orquestrador_sha256": rc._sha_arquivo(Path(__file__)), "sonda_sha256": rc._sha_arquivo(Path(SA.__file__)),
            "valuation_conserto_sha256": rc._sha_arquivo(Path(VC.__file__)), "valuation_v2_sha256": rc._sha_arquivo(Path(V.__file__)),
            "prototipo_sha256": rc._sha_arquivo(Path(orq.__file__)), "c4_sha256": rc._sha_arquivo(Path(ma.__file__)),
            "longe_regular_sha256": rc._sha_arquivo(Path(lr.__file__)),
            "git_head": rc._git("rev-parse", "HEAD"), "git_limpo": rc._git("status", "--porcelain") == "", "processos": processos,
            "unidades": unidades, "celulas": [list(c) for c in CELULAS],
            "bracos": {b: {"subchaves": orq.SUBCHAVES_C4["REL"], "acoplamento": vars(montar(b)["acoplamento"])} for b in BRACOS},
            "faixa": list(FAIXA),
            "sha256": {n: rc._sha_arquivo(RAIZ / "digilab" / n) for n in ("config.py", "corpo.py", "motor_corpo.py", "engine.py", "metrics.py",
                                                                         "mundo.py")}
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
    lidos = json.loads((pasta / "medidas.json").read_text(encoding="utf-8"))
    resultado = {"modo": modo, "fase": FASE, "plano": PLANO, "unidades": len(unidades), "vidas": len(lidos), **analisar(lidos)}
    bv._gravar(pasta / "resultado.json", bv._dump(resultado))
    V.tar_deterministico(pasta / "vidas", pasta / "vidas.tar.gz")
    nomes = ["medidas.json", "resultado.json", "vidas.tar.gz"]
    meta["fim"] = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
    meta["duracao_s"] = time.time() - inicio
    meta["artefatos_sha256"] = {n: bv._sha(pasta / n) for n in nomes}
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    return {"meta": meta, "registros": registros, "resultado": resultado}


def _resumo(r: dict) -> str:
    """o resumo no console, ASCII puro"""
    cr = r["criterios"]
    return json.dumps({"modo": r["modo"], "vidas": r["vidas"], "veredito": r["veredito"],
                       "P": {k: cr["P"][k] for k in ("media", "ic95", "p_unilateral", "passa", "d_menos_rel")},
                       "guardas": {g: {o: {"media": x["media"], "ic95": x["ic95"], "passa": x["passa"]} for o, x in cr[g].items()}
                                   for g in ("G1", "G2", "G3")}}, indent=1, ensure_ascii=True, default=str)


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
        pre_run.exigir(ORQUESTRADOR, a.config, a.processos)             # o H10 (D-IA-6: o plano da origin/main) e a V3-D8, antes de tudo
    print(_resumo(rodar(cfg, Path(a.saida) if a.saida else RAIZ / SAIDA, a.processos, caminho)["resultado"]))


if __name__ == "__main__":
    main()
