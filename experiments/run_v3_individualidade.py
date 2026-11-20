"""O orquestrador do I2 da INDIVIDUALIDADE: a linha de base descritiva (docs/PLANO_ANALISE_V3_INDIVIDUALIDADE.md, APROVADO em 2026-11-07).

Cada unidade (base, k) vive com os quatro donos nos bracos REL e REL+F, no `comedouro`, 14 dias, com a bateria de sondas do I1
(experiments/sondas_individualidade.py, o longe a 16 celulas do I2a). Toda vida e gravada, rejogada do disco (G1) e conferida: o cenario, o
mecanismo, a memoria do braco e o G2 da bateria. Os tracos de cada replica saem de `metrics.tracos_individualidade`. A analise (secao 4 do
plano): R_pet, R_dia e R_rep com o IC95 bootstrap sobre os pets, o eta2 do dono com o bootstrap sobre as sementes, as facetas (REL+F), a
sindrome, a norma de reacao e a regra dos tracos para o I3 (7.4). Descritiva: nao ha gate.

A trava (secao 9 do plano): a run de pesquisa so roda com o cabecalho do plano "APROVADO pelo Matheus", a faixa 85101...85505 em
FAIXAS_RESERVADAS, a secao do registro da run no plano, as bases e o K do plano, no maximo 4 processos e nada por cima de uma pasta que ja
existe. A fumaca (as sementes dos testes, 101...505) roda sem a faixa e sem o registro, com 1 a 14 dias.

    python experiments/run_v3_individualidade.py --config experiments/configs/v3_individualidade/individualidade.json --processos 4
"""
from __future__ import annotations

import argparse
import json
import platform
import random
import statistics
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402
import run_v2_memoria_autobio as ma  # noqa: E402
import sondas_individualidade as si  # noqa: E402
from bancada.faixas import FAIXAS_RESERVADAS  # noqa: E402
from digilab import metrics as M  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402

PLANO = "docs/PLANO_ANALISE_V3_INDIVIDUALIDADE.md"
MARCA_APROVADO = "**Status: APROVADO pelo Matheus"
TITULO_REGISTRO = "## 12. O registro da run"                                          # secao 10 do plano: a secao nova no fim
FASE = "individualidade"
FAIXA = (85101, 85505)                                                                # IP-9
BASES = (85101, 85202, 85303, 85404, 85505)                                           # IP-9
K_POR_BASE = 12                                                                       # IP-6
PREFIXO = orq.PREFIXO                                                                 # o esquema (base, k) da C4
BRACOS = ("REL", "REL+F")                                                             # IP-1
DONOS = orq.DONOS                                                                     # IP-2
LUGAR = "comedouro"                                                                   # IP-2
DIAS, ORCAMENTO_POR_DIA = ma.DIAS, ma.ORCAMENTO_POR_DIA                               # os da C4 (secao 0 do plano: 14 dias, 16 por dia)
REPLICAS = si.REPLICAS                                                                # IP-7
MAX_PROCESSOS = 4                                                                     # V3-D8
BOOTSTRAP = 2000                                                                      # secao 4.2
BINARIOS = ("neofilia", "ousadia")
FACETA_DO_TRACO = {"apego": "apego_dono", "neofilia": "cautela_comida", "ousadia": "ousadia_longe"}   # secao 4.4
SAIDA = "artifacts_v3_individualidade"
CHAVES_CONFIG = {"descricao", "fase", "plano", "unidades", "dias", "orcamento_por_dia"}


# ================================================================== a trava
def _plano() -> str:
    return (RAIZ / PLANO).read_text(encoding="utf-8")


def exigir_plano_aprovado(texto: str) -> None:
    """o cabecalho do plano (o primeiro paragrafo depois do titulo) tem a marca "APROVADO pelo Matheus" e a secao do registro existe"""
    linhas = texto.splitlines()
    status = next((x for x in linhas[1:12] if x.startswith("**Status:")), None)
    if status is None or not status.startswith(MARCA_APROVADO):
        raise RuntimeError("o plano do I2 sem o status APROVADO pelo Matheus no cabecalho: nenhuma vida da faixa")
    if sum(1 for x in linhas if x.startswith(TITULO_REGISTRO)) != 1:
        raise RuntimeError(f"o plano do I2 sem a secao {TITULO_REGISTRO!r} (o registro da run, secao 10): nenhuma vida da faixa")


def exigir_faixa_reservada() -> None:
    if not any((lo, hi) == FAIXA for lo, hi, _ in FAIXAS_RESERVADAS):
        raise bv.SementeSemPlano(f"a faixa {FAIXA[0]}...{FAIXA[1]} nao esta em FAIXAS_RESERVADAS (IP-9)")


def modo_da_config(cfg: dict, texto_plano: str | None = None) -> str:
    """'fumaca' (as sementes dos testes) ou 'individualidade' (o plano a letra; a trava); o resto falha alto"""
    faltam, sobram = (CHAVES_CONFIG - {"descricao"}) - set(cfg), set(cfg) - CHAVES_CONFIG
    if faltam or sobram:
        raise ValueError(f"config: faltam {sorted(faltam)}, sobram {sorted(sobram)}")
    if cfg["fase"] != FASE:
        raise ValueError(f"fase {cfg['fase']!r}: so {FASE!r}")
    u = cfg["unidades"]
    bases = tuple(u["bases"])
    if u.get("prefixo") != PREFIXO or cfg["orcamento_por_dia"] != ORCAMENTO_POR_DIA or type(u.get("k")) is not int or u["k"] < 1:
        raise ValueError("config fora do plano: o prefixo, o orcamento ou o K")
    if bases and set(bases) <= bv.SEMENTES_TESTE:
        if not 1 <= cfg["dias"] <= DIAS:
            raise ValueError(f"fumaca com {cfg['dias']} dias: de 1 a {DIAS}")
        return "fumaca"
    if bases != BASES:
        raise bv.SementeSemPlano(f"bases {list(bases)}: so as dos testes (fumaca) ou {list(BASES)} (IP-9)")
    exigir_faixa_reservada()
    exigir_plano_aprovado(_plano() if texto_plano is None else texto_plano)
    erros = [f"dias {cfg['dias']}"] if cfg["dias"] != DIAS else []
    erros += [f"K {u['k']}"] if u["k"] != K_POR_BASE else []
    erros += [f"plano {cfg.get('plano')!r}"] if cfg.get("plano") != PLANO else []
    if erros:
        raise ValueError(f"a run segue o plano a letra: {erros}")
    return FASE


# ================================================================== a vida
def tracos_da_bateria(bateria: dict) -> list[dict]:
    """uma linha por (dia, replica) com sonda: os seis tracos (None = janela invalida)"""
    linhas = []
    for d in bateria["por_dia"]:
        if d["tick"] is None:
            continue
        for r in range(bateria["replicas"]):
            linhas.append({"dia": d["dia"], "replica": r,
                           **M.tracos_individualidade({j: d["janelas"][j][r] for j in M.JANELAS_INDIVIDUALIDADE})})
    return linhas


def descritivo_da_bateria(bateria: dict) -> dict:
    """secao 8: a latencia da acao-chave e a distancia andada por janela, os dias sem sonda e o susto no corpo no fim do susto"""
    lat, andou, susto_corpo = {}, {}, []
    for d in bateria["por_dia"]:
        if d["tick"] is None:
            continue
        for j, reps in d["janelas"].items():
            for r in reps:
                if r["latencia"] is not None:
                    lat.setdefault(j, []).append(r["latencia"])
                andou.setdefault(j, []).append(round(((r["pos1"][0] - r["pos0"][0]) ** 2 + (r["pos1"][1] - r["pos0"][1]) ** 2) ** 0.5))
                if j == "susto":
                    susto_corpo.append(r["corpo_fim"].get("susto") if isinstance(r["corpo_fim"], dict) else None)
    return {"latencias": lat, "andou": andou, "dias_sem_sonda": sum(1 for d in bateria["por_dia"] if d["tick"] is None),
            "susto_corpo_fim": susto_corpo}


def _facetas_finais(braco: str, c) -> dict | None:
    if braco not in ma.COM_FACETAS:
        return None
    if not c.motivos:
        raise RuntimeError("REL+F sem decisao: sem facetas para ler")
    return dict(c.motivos[-1]["faceta"]["valores"])


def _vida(cfg: dict, braco: str, dono: str, unidade: dict, pasta: str) -> dict:
    c0, p0 = time.process_time(), time.perf_counter()
    semente = unidade["semente"]
    motor, registro, fab, bateria = si.vida_com_bateria(braco, dono, LUGAR, semente, cfg["dias"], cfg["orcamento_por_dia"], REPLICAS)
    nome = f"{dono}_{LUGAR}_{semente}"
    arquivo = Path(pasta) / "vidas" / braco / f"{nome}.jsonl"
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    arquivo.write_text(motor.log.para_jsonl(), encoding="utf-8", newline="\n")
    orq.conferir_replay(motor, fab, semente, arquivo.read_text(encoding="utf-8"))
    orq.conferir_cenario(motor, registro)
    orq.conferir_mecanismo(braco, registro, None)
    c = orq.cerebro_de(registro)
    ma.conferir_memoria(braco, c)
    bv._gravar(Path(pasta) / "vidas" / braco / f"{nome}_bateria.json", bv._dump(bateria))
    return {"vida": f"{braco}|{dono}|{LUGAR}|{semente}", "braco": braco, "dono": dono, "semente": semente, "base": unidade["base"],
            "k": unidade["k"], "tracos": tracos_da_bateria(bateria), "facetas": _facetas_finais(braco, c),
            "descritivo": descritivo_da_bateria(bateria),
            "custo": {"vida_cpu": time.process_time() - c0, "vida_parede": time.perf_counter() - p0}}


def tarefa(cfg: dict, unidade: dict, pasta: str) -> list[dict]:
    return [_vida(cfg, b, dono, unidade, pasta) for b in BRACOS for dono in DONOS]


# ================================================================== a analise
def _validos(registro: dict, traco: str) -> list[tuple[int, float]]:
    return [(x["dia"], x[traco]) for x in registro["tracos"] if x[traco] is not None]


def _media(v: list[float]) -> float:
    return sum(v) / len(v)


def _percentis(valores: list[float], nivel: float = 0.95) -> tuple[float, float] | None:
    if len(valores) < 2:
        return None
    s = sorted(valores)
    a = (1.0 - nivel) / 2.0
    return s[int(a * (len(s) - 1))], s[int(round((1.0 - a) * (len(s) - 1)))]


def _icc_seguro(estat: list) -> float | None:
    try:
        return M.icc1_estatisticas(estat)["r"]
    except ValueError:
        return None


def repetibilidade(pets: list[dict], traco: str, boot: int, rotulo: tuple) -> dict:
    """secao 4.2: R_pet (todas as janelas), R_dia (as medias do dia) e R_rep (as replicas dentro do dia), com o IC95 bootstrap sobre os pets
    (reamostra pets inteiros; uma reamostra sem variancia conta como indefinida e fica fora dos percentis)"""
    por_pet = []                                   # por pet: (estat do pet, estat das medias do dia, [estat de cada dia com >= 1 replica])
    for p in pets:
        v = _validos(p, traco)
        if not v:
            continue
        dias: dict[int, list[float]] = {}
        for dia, x in v:
            dias.setdefault(dia, []).append(x)
        por_pet.append((M.estatisticas_grupo([x for _, x in v]), M.estatisticas_grupo([_media(xs) for xs in dias.values()]),
                        [M.estatisticas_grupo(xs) for xs in dias.values()]))
    saida = {"pets": len(por_pet)}
    if len(por_pet) < 2:
        return saida | {"R_pet": None, "R_dia": None, "R_rep": None}
    medidas = {"R_pet": lambda ps: [x[0] for x in ps], "R_dia": lambda ps: [x[1] for x in ps], "R_rep": lambda ps: [e for x in ps for e in x[2]]}
    for nome, f in medidas.items():
        ponto = _icc_seguro(f(por_pet))
        rng = random.Random(derivar_semente("individualidade-boot", *rotulo, traco, nome))
        reams, indef = [], 0
        for _ in range(boot):
            r = _icc_seguro(f([por_pet[rng.randrange(len(por_pet))] for _ in por_pet]))
            if r is None:
                indef += 1
            else:
                reams.append(r)
        ic = _percentis(reams)
        saida[nome] = {"r": ponto, "ic95": None if ic is None else list(ic), "indefinidas": indef}
    return saida


def eta2_dono(pets: list[dict], traco: str, boot: int, rotulo: tuple) -> dict:
    """secao 4.3: o eta2 do dono nas medias por pet; o IC95 reamostra sementes (a semente leva os quatro donos juntos)"""
    media = {(p["dono"], p["semente"]): _media([x for _, x in _validos(p, traco)]) for p in pets if _validos(p, traco)}
    sementes = sorted({s for _, s in media})

    def eta(ss: list) -> float | None:
        grupos = [[media[(d, s)] for s in ss if (d, s) in media] for d in DONOS]
        grupos = [g for g in grupos if g]
        try:
            return M.eta2_grupos(grupos)
        except ValueError:
            return None

    ponto = eta(sementes)
    rng = random.Random(derivar_semente("individualidade-boot", *rotulo, traco, "eta2"))
    reams = [r for r in (eta([sementes[rng.randrange(len(sementes))] for _ in sementes]) for _ in range(boot)) if r is not None] \
        if len(sementes) >= 2 else []
    ic = _percentis(reams)
    return {"eta2": ponto, "ic95": None if ic is None else list(ic), "sementes": len(sementes)}


def _spearman_seguro(xs: list, ys: list) -> float | None:
    try:
        return M.spearman(xs, ys)
    except ValueError:
        return None


def facetas(pets: list[dict], boot: int) -> dict:
    """secao 4.4 (so o REL+F): o Spearman entre a media do traco e a faceta no fim da vida, com o IC95 bootstrap sobre os pets"""
    saida = {}
    for traco, faceta in FACETA_DO_TRACO.items():
        pares = [(_media([x for _, x in _validos(p, traco)]), p["facetas"][faceta]) for p in pets if _validos(p, traco)]
        rng = random.Random(derivar_semente("individualidade-boot", "REL+F", traco, faceta))
        ponto = _spearman_seguro([a for a, _ in pares], [b for _, b in pares]) if len(pares) >= 3 else None
        reams = []
        if len(pares) >= 3:
            for _ in range(boot):
                am = [pares[rng.randrange(len(pares))] for _ in pares]
                r = _spearman_seguro([a for a, _ in am], [b for _, b in am])
                if r is not None:
                    reams.append(r)
        ic = _percentis(reams)
        saida[traco] = {"faceta": faceta, "spearman": ponto, "ic95": None if ic is None else list(ic), "pets": len(pares)}
    return saida


def sindrome(pets: list[dict]) -> dict:
    """secao 4.5: a matriz de Spearman entre os seis tracos, nas medias por pet (os pets com os seis definidos)"""
    medias = []
    for p in pets:
        m = {t: _validos(p, t) for t in M.TRACOS_INDIVIDUALIDADE}
        if all(m.values()):
            medias.append({t: _media([x for _, x in v]) for t, v in m.items()})
    return {"pets": len(medias), "matriz": {a: {b: (_spearman_seguro([m[a] for m in medias], [m[b] for m in medias])
                                                    if len(medias) >= 3 else None) for b in M.TRACOS_INDIVIDUALIDADE}
                                            for a in M.TRACOS_INDIVIDUALIDADE}}


def norma_de_reacao(pets: list[dict], traco: str) -> dict:
    """secao 4.5: por pet, a reta da media do dia contra o dia; a media e a variancia das inclinacoes, no braco e por dono"""
    por_dono: dict[str, list[float]] = {}
    for p in pets:
        dias: dict[int, list[float]] = {}
        for dia, x in _validos(p, traco):
            dias.setdefault(dia, []).append(x)
        if len(dias) >= 2:
            ds = sorted(dias)
            por_dono.setdefault(p["dono"], []).append(M.reta_mmq(ds, [_media(dias[d]) for d in ds])[1])

    def resumo(v: list[float]) -> dict:
        return {"n": len(v), "media": _media(v) if v else None, "variancia": statistics.variance(v) if len(v) >= 2 else None}

    return {"braco": resumo([b for v in por_dono.values() for b in v]), "por_dono": {d: resumo(v) for d, v in sorted(por_dono.items())}}


def regra_i3(rep: dict, validas: dict, uns: dict) -> dict:
    """secao 7.4, no REL: sai o traco com (a) menos de 50 % de janelas validas, (b) binario com a fracao de 1 fora de [5 %, 95 %] ou (c) o IC95
    do R_rep inteiro abaixo de 0,05; menos de tres que ficam voltam ao Matheus"""
    decisao = {}
    for t in M.TRACOS_INDIVIDUALIDADE:
        motivos = []
        if validas[t] < 0.5:
            motivos.append("a: menos de 50 % de janelas validas")
        if t in BINARIOS and (uns[t] is None or not 0.05 <= uns[t] <= 0.95):
            motivos.append("b: a fracao de 1 fora de [5 %, 95 %]")
        ic = (rep[t].get("R_rep") or {}).get("ic95") if isinstance(rep[t].get("R_rep"), dict) else None
        if ic is not None and ic[1] < 0.05:
            motivos.append("c: o IC95 do R_rep inteiro abaixo de 0,05")
        decisao[t] = {"fica": not motivos, "motivos": motivos}
    ficam = [t for t, d in decisao.items() if d["fica"]]
    return {"por_traco": decisao, "ficam": ficam, "volta_ao_matheus": len(ficam) < 3}


def analisar(registros: list[dict], boot: int = BOOTSTRAP) -> dict:
    saida = {}
    for braco in BRACOS:
        pets = [r for r in registros if r["braco"] == braco]
        janelas = [x for p in pets for x in p["tracos"]]
        validas = {t: (sum(1 for x in janelas if x[t] is not None) / len(janelas) if janelas else 0.0) for t in M.TRACOS_INDIVIDUALIDADE}
        uns = {}
        for t in BINARIOS:
            v = [x[t] for x in janelas if x[t] is not None]
            uns[t] = sum(v) / len(v) if v else None
        rep = {t: repetibilidade(pets, t, boot, (braco,)) for t in M.TRACOS_INDIVIDUALIDADE}
        b = {"pets": len(pets), "janelas": len(janelas), "fracao_validas": validas, "fracao_de_1": uns, "repetibilidade": rep,
             "eta2_dono": {t: eta2_dono(pets, t, boot, (braco,)) for t in M.TRACOS_INDIVIDUALIDADE},
             "medias_entre_pets": {t: _resumo_medias(pets, t) for t in M.TRACOS_INDIVIDUALIDADE},
             "sindrome": sindrome(pets), "norma_de_reacao": {t: norma_de_reacao(pets, t) for t in M.TRACOS_INDIVIDUALIDADE},
             "descritivo": _descritivo(pets)}
        if braco in ma.COM_FACETAS:
            b["facetas"] = facetas(pets, boot)
        if braco == "REL":
            b["regra_i3"] = regra_i3(rep, validas, uns)
        saida[braco] = b
    return {"por_braco": saida,
            "nao_demonstra": ["que o pet tem personalidade (os tracos sao nomes de medida)", "que o modular supera o A",
                              "qualquer efeito do genoma (o genoma e vazio nesta run)", "que o mecanismo e novo"]}


def _resumo_medias(pets: list[dict], traco: str) -> dict:
    m = [_media([x for _, x in _validos(p, traco)]) for p in pets if _validos(p, traco)]
    return {"n": len(m), "media": _media(m) if m else None, "desvio": statistics.stdev(m) if len(m) >= 2 else None}


def _descritivo(pets: list[dict]) -> dict:
    out = {}
    for dono in DONOS:
        ps = [p for p in pets if p["dono"] == dono]
        lat = {j: [x for p in ps for x in p["descritivo"]["latencias"].get(j, [])] for j in M.JANELAS_INDIVIDUALIDADE}
        andou = {j: [x for p in ps for x in p["descritivo"]["andou"].get(j, [])] for j in M.JANELAS_INDIVIDUALIDADE}
        out[dono] = {"latencia_media": {j: (_media(v) if v else None) for j, v in lat.items()},
                     "andou_media": {j: (_media(v) if v else None) for j, v in andou.items()},
                     "dias_sem_sonda": sum(p["descritivo"]["dias_sem_sonda"] for p in ps)}
    return out


# ================================================================== a run
def rodar(cfg: dict, pasta: Path, processos: int, caminho_config: Path | None = None, boot: int = BOOTSTRAP) -> dict:
    if processos > MAX_PROCESSOS:
        raise ValueError(f"no maximo {MAX_PROCESSOS} processos (V3-D8)")
    modo = modo_da_config(cfg)
    if pasta.exists():
        raise FileExistsError(f"{pasta} ja existe: a run se recusa a gravar por cima")
    unidades = bv.unidades_derivadas(cfg["unidades"]["bases"], int(cfg["unidades"]["k"]), PREFIXO)
    pasta.mkdir(parents=True)
    inicio = time.time()
    rc = orq.rc
    meta = {"modo": modo, "fase": FASE, "plano": PLANO, "plano_sha256": rc._sha_arquivo(RAIZ / PLANO), "config": cfg,
            "config_arquivo": None if caminho_config is None else rc._relativo(caminho_config),
            "config_sha256": None if caminho_config is None else rc._sha_arquivo(caminho_config),
            "orquestrador_sha256": rc._sha_arquivo(Path(__file__)), "bateria_sha256": rc._sha_arquivo(Path(si.__file__)),
            "memoria_autobio_sha256": rc._sha_arquivo(Path(ma.__file__)), "prototipo_sha256": rc._sha_arquivo(Path(orq.__file__)),
            "git_head": rc._git("rev-parse", "HEAD"), "git_limpo": rc._git("status", "--porcelain") == "", "processos": processos,
            "unidades": unidades, "bracos": list(BRACOS), "donos": list(DONOS), "lugar": LUGAR, "replicas": REPLICAS, "bootstrap": boot,
            "sha256": {n: rc._sha_arquivo(RAIZ / "digilab" / n) for n in ("config.py", "engine.py", "metrics.py", "mundo.py")}
            | {f"digibrain/{p.name}": rc._sha_arquivo(p) for p in sorted((RAIZ / "digilab" / "digibrain").glob("*.py"))},
            "inicio": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(inicio))}
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    t0 = time.perf_counter()
    registros = [r for s in rc._executar([(tarefa, (cfg, u, str(pasta))) for u in unidades], processos) for r in s]
    meta["vidas_parede_s"] = time.perf_counter() - t0
    esperadas = len(unidades) * len(BRACOS) * len(DONOS)
    if len(registros) != esperadas:
        raise RuntimeError(f"{len(registros)} vidas, eram {esperadas}")
    with (pasta / "tracos.jsonl").open("w", encoding="utf-8", newline="\n") as f:
        for r in sorted(registros, key=lambda r: r["vida"]):
            for x in r["tracos"]:
                for t in M.TRACOS_INDIVIDUALIDADE:
                    if x[t] is not None:
                        f.write(json.dumps({"braco": r["braco"], "dono": r["dono"], "base": r["base"], "k": r["k"], "dia": x["dia"],
                                            "replica": x["replica"], "traco": t, "valor": x[t]}, sort_keys=True) + "\n")
    bv._gravar(pasta / "medidas.json", bv._dump({r["vida"]: r for r in sorted(registros, key=lambda r: r["vida"])}))
    lidos = json.loads((pasta / "medidas.json").read_text(encoding="utf-8"))       # a analise sai do artefato gravado
    resultado = {"modo": modo, "fase": FASE, "plano": PLANO, "unidades": len(unidades), "vidas": len(lidos), **analisar(list(lidos.values()), boot)}
    bv._gravar(pasta / "analise.json", bv._dump(resultado))
    custos = [r["custo"]["vida_parede"] for r in registros]
    bv._gravar(pasta / "custo.json", bv._dump({"vidas": len(custos), "parede_media_s": _media(custos), "parede_max_s": max(custos),
                                               "total_parede_s": meta["vidas_parede_s"]}))
    meta["fim"] = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
    meta["duracao_s"] = time.time() - inicio
    meta["python"] = platform.python_version()
    meta["artefatos_sha256"] = {n: bv._sha(pasta / n) for n in ("medidas.json", "tracos.jsonl", "analise.json", "custo.json")}
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
        raise SystemExit(f"a fumaca precisa de --saida (fora de {SAIDA}/)")
    r = rodar(cfg, Path(a.saida) if a.saida else RAIZ / SAIDA, a.processos, caminho)["resultado"]
    print(json.dumps({"modo": r["modo"], "vidas": r["vidas"], "regra_i3": r["por_braco"]["REL"].get("regra_i3")}, indent=1,
                     ensure_ascii=True, default=str)[:3000])


if __name__ == "__main__":
    main()
