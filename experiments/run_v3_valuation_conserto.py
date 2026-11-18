"""VALUATION V3: o conserto do reflexo do sono, uma vez (docs/PLANO_ANALISE_V3_VALUATION_CONSERTO.md; docs/TAREFA_V3_VALUATION.md).

Pergunta (a secao 1 do plano): a guarda da fome urgente no reflexo do sono (`ConfigConsertoValuation.guarda_fome_reflexo`, D-VAL-16) fecha
mais episodios de fome no `longe_fixo` sem piorar a privacao, a exaustao e a taxa do comedouro e do longe?

Os bracos (a secao 4), na mesma unidade (base, semente), nas 12 celulas da C4 (os 4 donos x comedouro, longe e `longe_fixo`; D-VAL-19):
  - REL: o REL da C4 e da V2 (o controle);
  - CON: o REL com a chave do conserto ligada; uma mudanca so.

A vida e a da V2 (`run_v3_valuation`: o `MotorGravaCorpo`, o pet sozinho, 14 dias, orcamento 16, o coletor das categorias), com o replay do
disco, o T-CENARIO-1, as conferencias da C4 e a conferencia do conserto (a secao 3: decisao a decisao, o reflexo e o que a regra diz pela
energia e pela fome urgente; senao falha alto). A energia de cada decisao vem de um involucro so de leitura no `Arbitragem.reflexo` (a
conta e pura: ele nao muda a vida); a fome urgente, do motivo.

A analise (a secao 5, escrita antes): P (CON - REL na taxa por episodio do `longe_fixo`, "> 0" e p unilateral < 0,025), G1 e G2 (a
privacao e a exaustao, no `longe_fixo` e nas 12 celulas, nenhuma "> 0"), G3 (a taxa do comedouro e do longe, nenhuma "< 0"); o veredito
passa so com todas. O D ("desliga nao muda") e o teste do gabarito, antes da run. Ao lado, os descritivos da V2 e a fracao das decisoes
com a energia abaixo de `lambda_sono` em que a fome estava urgente.

A trava: a run de verdade recusa rodar sem o "APROVADO pelo Matheus" no cabecalho do plano, sem a faixa em FAIXAS_RESERVADAS e com a pasta
de saida ja existente. A fumaca usa as sementes dos testes.
Uso: python experiments/run_v3_valuation_conserto.py --config experiments/configs/v3_valuation/conserto.json --processos 4
"""
from __future__ import annotations

import argparse
import gzip
import json
import platform
import shutil
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
import run_v3_valuation as V  # noqa: E402
from bancada.faixas import FAIXAS_RESERVADAS  # noqa: E402
from bancada.regras_mundo import simular_vida_fisico  # noqa: E402
from digilab.config import (CONFIG_CONSERTO_VALUATION, CONFIG_CONSERTO_VALUATION_LIGADO, CONFIG_DIGIBRAIN_INATOS,  # noqa: E402
                            CONFIG_PADRAO)
from digilab.digibrain import DigiBrain  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.mundo import DonoComLugar  # noqa: E402
from digilab.temperamento import NEUTRO  # noqa: E402

PLANO = "docs/PLANO_ANALISE_V3_VALUATION_CONSERTO.md"
FASE = "conserto"
PREFIXO = orq.PREFIXO
BASES = (73101, 73202, 73303, 73404, 73505)                   # secao 4 (D-VAL-18, aprovada em 2026-11-17)
FAIXA = (73101, 73505)
K_POR_BASE = 40
DIAS, ORCAMENTO_POR_DIA = V.DIAS, V.ORCAMENTO_POR_DIA
SAIDA = "artifacts_v3_valuation/conserto"                     # secao 6
MAX_PROCESSOS = V.MAX_PROCESSOS
CELULAS = ma.CELULAS                                          # as 12 da C4 (D-VAL-19)
PRIMARIO, COMEDOURO, LONGE = ma.PRIMARIO, ma.GUARDA, ma.SORTEADO
BRACOS = ("REL", "CON")
CONTROLE, TRATADO = "REL", "CON"
MARGEM = V.MARGEM                                             # D-VAL-20: a classe com o 0,032 da V2
ALFA = 0.025                                                  # secao 5: um primario so, unilateral
GAP_A1 = V.GAP_A1
EPISODIO, PRIVACAO, EXAUSTAO = V.EPISODIO, V.PRIVACAO, V.EXAUSTAO
CHAVES_CONFIG = V.CHAVES_CONFIG
S = CONFIG_DIGIBRAIN_INATOS.escala


# ================================================================== os bracos
def montar(braco: str) -> dict:
    """a ConfigDigibrain, os inatos e o conserto do braco: o CON e o REL com a chave ligada"""
    if braco not in BRACOS:
        raise ValueError(f"braco {braco!r}: so {BRACOS}")
    return {"cd": orq.config_do_braco("REL", conserto=True), "inatos": CONFIG_DIGIBRAIN_INATOS,
            "conserto": CONFIG_CONSERTO_VALUATION_LIGADO if braco == TRATADO else CONFIG_CONSERTO_VALUATION}


def fabricas(braco: str, dono: str, semente: int, dias: int, orcamento_por_dia: int) -> tuple:
    """as fabricas da V2 (`run_v3_valuation.fabricas`), com a chave do conserto no cerebro"""
    m = montar(braco)
    cc = orq.bancada(dias, orcamento_por_dia).cfg_corpo_de(bv.EspecVida(dono, gl.BRACO_V11, semente))

    def fp(cfg=None):
        return orq.Registro(DigiBrain(cfg or CONFIG_PADRAO, m["cd"], orq.CM, inatos=m["inatos"], semente=semente,
                                      cfg_conserto=m["conserto"]), S)

    def fm(politica, cfg, s):
        return lr.MotorGravaCorpo(politica, cfg, s, NEUTRO, "brasa", obediencia_desligada=True, cfg_mundo=orq.CM, cfg_corpo=cc)

    return fp, fm


def viver(braco: str, dono: str, lugar: str, semente: int, dias: int, orcamento_por_dia: int):
    """uma vida: a do `run_v3_valuation.viver`, com as fabricas do braco e o involucro de leitura do reflexo (a energia abaixo de
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


# ================================================================== a conferencia do conserto (secao 3; falha alta)
def conferir_conserto(braco: str, registro, baixas: list[bool]) -> dict:
    """o cerebro e o do braco e, decisao a decisao, o reflexo e o que a regra diz: no REL, a energia abaixo de `lambda_sono`; no CON, ela
    e a fome nao urgente. Devolve as contagens para o descritivo."""
    c = orq.cerebro_de(registro)
    m = montar(braco)
    if c.inatos != m["inatos"] or c.cd != m["cd"] or c.m.arb.cv != m["conserto"] or c.m.arb.sono.ligada:
        raise RuntimeError(f"{braco}: o cerebro da vida nao e o do braco (os inatos, as subchaves, o conserto ou o sono que segura)")
    if len(baixas) != len(c.motivos):
        raise RuntimeError(f"{braco}: {len(baixas)} leituras do reflexo para {len(c.motivos)} decisoes")
    lam = c.inatos.urgencia_lambda
    n_baixa = n_baixa_urgente = 0
    for x, baixa in zip(c.motivos, baixas):
        urgente = x["afeto"]["urgencias"]["fome"] > lam
        esperado = baixa and not (urgente and braco == TRATADO)
        if x["reflexo"] != esperado:
            raise RuntimeError(f"{braco}: o reflexo da decisao {x['k']} e {x['reflexo']}, a regra diz {esperado} "
                               f"(energia baixa {baixa}, fome urgente {urgente})")
        n_baixa += baixa
        n_baixa_urgente += baixa and urgente
    return {"decisoes_energia_baixa": n_baixa, "energia_baixa_fome_urgente": n_baixa_urgente,
            "fracao_fome_urgente": n_baixa_urgente / n_baixa if n_baixa else None}


# ================================================================== a vida
def _vida(cfg: dict, braco: str, dono: str, lugar: str, unidade: dict, pasta: str) -> dict:
    c0, p0 = time.process_time(), time.perf_counter()
    motor, registro, fab, categorias, baixas = viver(braco, dono, lugar, unidade["semente"], cfg["dias"], cfg["orcamento_por_dia"])
    arquivo = Path(pasta) / "vidas" / braco / f"{dono}_{lugar}_{unidade['semente']}.jsonl"
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    arquivo.write_text(motor.log.para_jsonl(), encoding="utf-8", newline="\n")
    orq.conferir_replay(motor, fab, unidade["semente"], arquivo.read_text(encoding="utf-8"))
    orq.conferir_cenario(motor, registro)
    orq.conferir_mecanismo(braco, registro, None)
    ma.conferir_memoria("REL", orq.cerebro_de(registro))
    fins = ma.conferir_fins("REL", registro)
    reflexo = conferir_conserto(braco, registro, baixas)
    med = orq.medidas(motor, registro, "REL", cfg["dias"], True)
    return {"vida": f"{braco}|{dono}|{lugar}|{unidade['semente']}", "braco": braco, "dono": dono, "lugar": lugar,
            "semente": unidade["semente"], "base": unidade["base"], "k": unidade["k"], **med,
            "corpo": lr.medidas_do_corpo(motor, registro, cfg["dias"]), "fins_conferidos": fins,
            "memoria": ma.medidas_memoria(registro, cfg["dias"], categorias),
            "valuation": {**V.descritivo_valuation(registro, med), **reflexo},
            "custo": {"vida_cpu": time.process_time() - c0, "vida_parede": time.perf_counter() - p0}}


def tarefa(cfg: dict, unidade: dict, pasta: str) -> list[dict]:
    return [_vida(cfg, b, dono, lugar, unidade, pasta) for b in BRACOS for dono, lugar in CELULAS]


# ================================================================== a analise (secao 5, escrita antes)
def _celulas(lugar: str | None) -> tuple:
    return CELULAS if lugar is None else tuple(c for c in CELULAS if c[1] == lugar)


def _difs(registros: list[dict], medida, lugar: str | None) -> dict:
    return orq.por_unidade(registros, TRATADO, CONTROLE, medida, _celulas(lugar))


def _guarda(registros: list[dict], medida, lugar: str | None, reprova: str) -> dict:
    """uma guarda: CON - REL com a classe de A6.6 (D-VAL-20); reprova com a classe `reprova`"""
    e = ma.estimativa(_difs(registros, medida, lugar), MARGEM)
    return {**e, "lugar": lugar or "as 12 celulas", "reprova_com": reprova, "passa": e["classe"]["classe"] != reprova}


def criterios(registros: list[dict], boot: dict = orq.BOOTSTRAP) -> dict:
    difs = _difs(registros, EPISODIO, PRIMARIO)
    c = orq.contraste_t(difs, boot)
    ic = {"ic_inferior": c["ic95"]["ic_inferior"], "ic_superior": c["ic95"]["ic_superior"], "motivo": c["motivo"]}
    cl = ma.classe(ic, MARGEM)
    p = c["p_unilateral"]
    passa_p = cl["classe"] == "> 0" and p is not None and p < ALFA
    trivial = cl["classe"] == "≈ 0" and cl["sinal"] == "+"
    P = {"contraste": "CON - REL, a taxa de fechamento por episodio, nas 4 celulas do longe_fixo", **c, "classe": cl, "margem": MARGEM,
         "margem_efetiva": lr.margem_efetiva(ma.estimativa(difs, MARGEM)["dp"], c["n"]), "alfa": ALFA, "passa": passa_p,
         "efeito_trivial": trivial, "fracao_do_gap_a1": None if c["media"] is None else c["media"] / -GAP_A1}
    G1 = {"longe_fixo": _guarda(registros, PRIVACAO, PRIMARIO, "> 0"), "12_celulas": _guarda(registros, PRIVACAO, None, "> 0")}
    G2 = {"longe_fixo": _guarda(registros, EXAUSTAO, PRIMARIO, "> 0"), "12_celulas": _guarda(registros, EXAUSTAO, None, "> 0")}
    G3 = {"comedouro": _guarda(registros, EPISODIO, COMEDOURO, "< 0"), "longe": _guarda(registros, EPISODIO, LONGE, "< 0")}
    return {"P": P, "G1": G1, "G2": G2, "G3": G3}


def veredito(cr: dict) -> dict:
    """a regra da secao 5: passa so com P, G1, G2 e G3 (o D e o teste do gabarito, antes da run); o efeito trivial conta como falha"""
    falhas = [] if cr["P"]["passa"] else ["P (efeito trivial)" if cr["P"]["efeito_trivial"] else "P"]
    falhas += [f"{g} ({onde})" for g in ("G1", "G2", "G3") for onde, x in cr[g].items() if not x["passa"]]
    return {"leitura": "passa" if not falhas else ("efeito trivial" if falhas == ["P (efeito trivial)"] else "falha"),
            "falhas": falhas,
            "checkpoint_v3": "o conserto passa: a V4 (contra a TRIV) espera o Matheus" if not falhas else
            "o conserto nao passa: a fase para com o relato (a regra do pedido)"}


DESCRITIVOS = {**V.DESCRITIVOS,
               "fracao_fome_urgente_na_energia_baixa": lambda r: r["valuation"]["fracao_fome_urgente"],
               "decisoes_energia_baixa": lambda r: r["valuation"]["decisoes_energia_baixa"]}


def descritivo(registros: list[dict]) -> dict:
    """os descritivos da 5.3 da V2 e o da fome urgente, no `longe_fixo` e nas 12 celulas: o nivel de cada braco e CON - REL, sem classe"""
    sem_classe = lambda e: {k: v for k, v in e.items() if k != "classe"}   # noqa: E731
    out = {}
    for onde, lugar in (("longe_fixo", PRIMARIO), ("12_celulas", None)):
        out[onde] = {n: {"niveis": {b: sem_classe(ma.estimativa(orq.por_unidade(registros, b, None, f, _celulas(lugar)))) for b in BRACOS},
                         "CON - REL": sem_classe(ma.estimativa(_difs(registros, f, lugar)))}
                     for n, f in DESCRITIVOS.items()}
    out["acoes_somadas_longe_fixo"] = {b: V._somar([r for r in registros if r["braco"] == b and r["lugar"] == PRIMARIO], lambda r: r["acoes"])
                                       for b in BRACOS}
    return out


def analisar(registros: list[dict], boot: dict = orq.BOOTSTRAP) -> dict:
    cr = criterios(registros, boot)
    return {"criterios": cr, "veredito": veredito(cr), "descritivo": descritivo(registros),
            "nao_demonstra": ["nada contra a TRIV (a V4)", "nada sobre o jogo web", "nada sobre outro limiar alem do urgencia_lambda de hoje",
                              "nada com o sono que segura ligado", "nada fora dos 14 dias e do mundo do MVP"]}


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
            "orquestrador_sha256": rc._sha_arquivo(Path(__file__)), "valuation_v2_sha256": rc._sha_arquivo(Path(V.__file__)),
            "prototipo_sha256": rc._sha_arquivo(Path(orq.__file__)), "c4_sha256": rc._sha_arquivo(Path(ma.__file__)),
            "longe_regular_sha256": rc._sha_arquivo(Path(lr.__file__)),
            "git_head": rc._git("rev-parse", "HEAD"), "git_limpo": rc._git("status", "--porcelain") == "", "processos": processos,
            "unidades": unidades, "celulas": [list(c) for c in CELULAS],
            "bracos": {b: {"subchaves": orq.SUBCHAVES_C4["REL"], "guarda_fome_reflexo": montar(b)["conserto"].guarda_fome_reflexo}
                       for b in BRACOS},
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
    lidos = json.loads((pasta / "medidas.json").read_text(encoding="utf-8"))
    resultado = {"modo": modo, "fase": FASE, "plano": PLANO, "unidades": len(unidades), "vidas": len(lidos), **analisar(lidos)}
    bv._gravar(pasta / "resultado.json", bv._dump(resultado))
    nomes = ["medidas.json", "resultado.json"]
    if (pasta / "medidas.json").stat().st_size > 100 * 2**20:
        with open(pasta / "medidas.json", "rb") as f, open(pasta / "medidas.json.gz", "wb") as s, \
                gzip.GzipFile(filename="", mode="wb", fileobj=s, mtime=0, compresslevel=9) as gz:
            shutil.copyfileobj(f, gz)
        nomes.append("medidas.json.gz")
    V.tar_deterministico(pasta / "vidas", pasta / "vidas.tar.gz")
    nomes.append("vidas.tar.gz")
    meta["fim"] = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
    meta["duracao_s"] = time.time() - inicio
    meta["artefatos_sha256"] = {n: bv._sha(pasta / n) for n in nomes}
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    return {"meta": meta, "registros": registros, "resultado": resultado}


def _resumo(r: dict) -> str:
    """o resumo no console, ASCII puro"""
    cr = r["criterios"]
    return json.dumps({"modo": r["modo"], "vidas": r["vidas"], "veredito": r["veredito"],
                       "P": {k: cr["P"][k] for k in ("media", "ic95", "p_unilateral", "passa")},
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
    if modo_da_config(cfg) == "fumaca" and a.saida is None:
        raise SystemExit(f"a fumaca precisa de --saida (fora de {SAIDA})")
    print(_resumo(rodar(cfg, Path(a.saida) if a.saida else RAIZ / SAIDA, a.processos, caminho)["resultado"]))


if __name__ == "__main__":
    main()
