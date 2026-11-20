"""O replay do R-a (docs/PLANO_ANALISE_V3_PET_VIVO_RA.md, APROVADO): a linha de base do intervalo, so leitura.

As mesmas vidas do R1 (o HOJE e o OLF-0 da run do PV-2 e o HOJE da checagem do v38; 5 120), rejogadas pelo log com a ConfigRastro
ligada. Nenhuma vida nova, nenhuma faixa nova, nada creditado. Por vida, as medidas de `metrics.medidas_linha_base` (as linhas de
base GLOBAL, CTX, FASE, ESTADO e MOVEL-k). As conferencias que falham alto, antes de qualquer medida: as do R1 (C-FONTE, C-G1,
C-FECHO, C-UMA-VEZ) e a C-IGUAL-R1 (as linhas de base GLOBAL e CTX refeitas por decisao dao as medidas gravadas do R1, vida a vida).

  python experiments/run_v3_pet_vivo_ra.py --config experiments/configs/v3_pet_vivo/ra.json --processos 4
  python experiments/run_v3_pet_vivo_ra.py --g1 2      # a fumaca: 2 vidas reais com todas as conferencias, sem gravar medida

O replay se recusa a rodar sem o plano APROVADO, com a pasta de saida existente, sem o `pre_run` e com menos de 10 GB livres.
"""
import argparse
import gzip
import json
import platform
import shutil
import sys
import tarfile
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tools"))

import bancada_v2 as bv  # noqa: E402
import pre_run  # noqa: E402
import pv2  # noqa: E402
import run_v3_pet_vivo_r1 as r1  # noqa: E402
from digilab import metrics as met  # noqa: E402
from digilab.config import CONFIG_PADRAO  # noqa: E402
from digilab.events import LogDeEventos  # noqa: E402
from digilab.mundo import reproduzir_mundo  # noqa: E402

orq = r1.orq
PLANO = "docs/PLANO_ANALISE_V3_PET_VIVO_RA.md"
ORQUESTRADOR = "experiments/run_v3_pet_vivo_ra.py"
FASE = "ra"
SAIDA = "artifacts_v3_pet_vivo/ra/run"
FONTE_R1 = "artifacts_v3_pet_vivo/r1/run"                    # o meta.json e o medidas.json.gz do R1, no git (a C-IGUAL-R1)
LUGARES = r1.LUGARES
PRINCIPAL = r1.PRINCIPAL
CORTE_ETA2 = 0.05                                            # RB-4: o da RA-5, SEM FONTE
PISO_DISCO_GB = 10                                           # o planejamento das runs de 2026-11-19, SEM FONTE
CORTE_CUSTO_H = 2.0                                          # a secao 8 do plano: a projecao de parede com 4 processos
LINHAS = met.LINHAS_BASE_FIXAS + tuple(f"MOVEL-{k}" for k in met.KS_MOVEL)
LINHAS_SONO = tuple(x for x in LINHAS if x not in ("GLOBAL", "CTX"))      # L-SONO: FASE, ESTADO e cada MOVEL-k
LINHAS_ALEM = tuple(x for x in LINHAS if x != "CTX")                      # L-ALEM, o ramo "so o sono"
CHAVES_CONFIG = r1.CHAVES_CONFIG


class LinhaBaseDivergiu(RuntimeError):
    """a C-IGUAL-R1 falhou: as linhas de base do R1 refeitas nao dao as medidas gravadas do R1"""


def ler_r1(nomes: set, raiz: Path = RAIZ) -> dict:
    """as medidas do rastro gravadas pelo R1, por vida (o `acao` de cada uma), conferido o sha256 do `meta.json` do R1"""
    pasta = raiz / FONTE_R1
    meta = json.loads((pasta / "meta.json").read_text(encoding="utf-8"))
    if bv._sha(pasta / "medidas.json.gz") != meta["artefatos_sha256"]["medidas.json.gz"]:
        raise LinhaBaseDivergiu("C-FONTE: o medidas.json.gz do R1 nao e o do meta.json dele")
    with gzip.open(pasta / "medidas.json.gz", "rt", encoding="utf-8") as f:
        todas = {r["vida"]: r["rastro"]["acao"] for r in json.load(f)}
    faltam = sorted(nomes - set(todas))
    if faltam:
        raise LinhaBaseDivergiu(f"C-IGUAL-R1: {len(faltam)} vidas sem medida no R1: {faltam[:3]}")
    return {n: todas[n] for n in nomes}


def conferir_igual_r1(vida: str, linhas: dict, acao_r1: dict) -> None:
    """C-IGUAL-R1: o eta2 e o resto por comportamento da GLOBAL e da CTX, refeitos por decisao, iguais aos do R1"""
    pares = (("GLOBAL", "eta2_global", "resto_global"), ("CTX", "eta2_contexto", "resto_contexto"))
    for nome, eta, resto in pares:
        if linhas[nome]["eta2_todas"] != acao_r1[eta]:
            raise LinhaBaseDivergiu(f"C-IGUAL-R1, {vida}: o eta2 da {nome} ({linhas[nome]['eta2_todas']!r}) nao e o do R1 ({acao_r1[eta]!r})")
        refeito = linhas[nome]["resto"]
        gravado = {b: v[resto] for b, v in acao_r1["por_comportamento"].items()}
        if refeito != gravado:
            raise LinhaBaseDivergiu(f"C-IGUAL-R1, {vida}: o resto por comportamento da {nome} nao e o do R1")


def rejogar(dias: int, orcamento: int, grupo: str, braco: str, dono: str, lugar: str, unidade: dict, texto: str, gravada: dict,
            acao_r1: dict) -> dict:
    """uma vida rejogada pelo log, com o rastro ligado: a C-G1, a C-FECHO e a C-UMA-VEZ como no R1, a C-IGUAL-R1 e as medidas das
    linhas de base"""
    c0, p0 = time.process_time(), time.perf_counter()
    semente = unidade["semente"]
    vida = r1.nome_da_vida(grupo, braco, dono, lugar, semente)
    fp, fm = pv2.fabricas(braco, dono, semente, dias, orcamento, v38=grupo == "v38", extra_cerebro=r1.RASTRO)
    motor = reproduzir_mundo(LogDeEventos.de_jsonl(texto), fp, semente=semente, fabrica_motor=fm)
    if motor.log.para_jsonl() != texto:
        raise r1.RastroDivergiu(f"C-G1, {vida}: o log rejogado nao e o do disco")
    registro = motor.politica
    c = orq.cerebro_de(registro)
    if not c.rastro:
        raise r1.RastroDivergiu(f"{vida}: o cerebro do replay sem o rastro ligado")
    refeita = json.loads(json.dumps({**orq.medidas(motor, registro, "REL", dias, True),
                                     "pv2": met.medidas_pv2(c.motivos, motor.consumos_mundo, braco != "HOJE", c.S)}))
    diferem = sorted(k for k, v in refeita.items() if k not in r1.FORA_DO_G1 and gravada.get(k) != v)
    if diferem:
        raise r1.RastroDivergiu(f"C-G1, {vida}: as medidas refeitas nao sao as gravadas: {diferem[:5]}")
    passo = CONFIG_PADRAO.intervalo_decisao_ticks
    r1.conferir_rastro(c.motivos, passo)
    lb = json.loads(json.dumps(met.medidas_linha_base(c.motivos, c.S, CONFIG_PADRAO.e_noite)))
    conferir_igual_r1(vida, lb["linhas"], acao_r1)
    return {"vida": vida, "grupo": grupo, "braco": braco, "dono": dono, "lugar": lugar, "semente": semente, "base": unidade["base"],
            "k": unidade["k"], "linha_base": lb, "custo": {"vida_cpu": time.process_time() - c0, "vida_parede": time.perf_counter() - p0}}


def _tarefa(dias: int, orcamento: int, vida: tuple, pasta_vidas: str, gravada: dict, acao_r1: dict) -> dict:
    grupo, braco, dono, lugar, unidade = vida
    texto = (Path(pasta_vidas) / r1.membro_da_vida(grupo, braco, dono, lugar, unidade["semente"])).read_text(encoding="utf-8")
    return rejogar(dias, orcamento, grupo, braco, dono, lugar, unidade, texto, gravada, acao_r1)


# ================================================================== a analise (secoes 5 e 6 do plano, escritas antes)
def escalares(lb: dict) -> dict:
    """as medidas de uma vida como escalares nomeados (None onde a vida nao tem a medida)"""
    out = {}
    for nome, v in lb["linhas"].items():
        out[f"resto_dormir|{nome}"] = v["resto_dormir"]
        out[f"eta2_todas|{nome}"] = v["eta2_todas"]
        out[f"eta2_acordado|{nome}"] = v["eta2_acordado"]
        out.update({f"resto:{b}|{nome}": x for b, x in v["resto"].items()})
    out.update({f"n:{b}": x for b, x in lb["contagem"].items()})
    out.update({f"no_eta2:{b}": 1.0 if b in lb["acordados_no_eta2"] else 0.0 for b in lb["contagem"] if b != "dormir"})
    out["fracao_noite"] = lb["fase"]["noite"] / lb["n"]
    return out


def resumo(registros: list[dict], grupo: str, braco: str, lugar: str) -> dict:
    """por medida: a media dos donos por unidade e o IC95 pelo t sobre as unidades; ao lado, a media por dono, sem IC (como no R1)"""
    vidas = [r for r in registros if (r["grupo"], r["braco"], r["lugar"]) == (grupo, braco, lugar)]
    if not vidas:
        raise LinhaBaseDivergiu(f"nenhuma vida de {grupo}/{braco}/{lugar}")
    esc = [(r["semente"], r["dono"], escalares(r["linha_base"])) for r in vidas]
    out = {}
    for nome in sorted({n for _, _, e in esc for n in e}):
        por_unidade: dict = {}
        por_dono: dict = {}
        for s, d, e in esc:
            por_unidade.setdefault(s, []).append(e.get(nome))
            por_dono.setdefault(d, []).append(e.get(nome))
        medias = [m for m in (r1._media(v) for _, v in sorted(por_unidade.items())) if m is not None]
        ic = met.ic_t(medias)
        out[nome] = {"n": ic["n"], "media": ic["media"], "dp": ic["dp"], "ic_inferior": ic["ic_inferior"],
                     "ic_superior": ic["ic_superior"], "motivo": ic.get("motivo"),
                     "por_dono": {d: r1._media(v) for d, v in sorted(por_dono.items())}}
    return {"vidas": len(vidas), "unidades": len({s for s, _, _ in esc}), "medidas": out}


def leitura(resumos: dict) -> dict:
    """a regra da secao 6, escrita antes, no HOJE da run, pelos limites do IC95 nos 3 lugares (o corte da RB-4, SEM FONTE)"""
    r = {lugar: resumos[f"{PRINCIPAL[0]}|{PRINCIPAL[1]}|{lugar}"]["medidas"] for lugar in LUGARES}

    def lim(nome, lado):
        vals = {lugar: r[lugar][nome][lado] for lugar in LUGARES}
        if any(v is None for v in vals.values()):
            raise LinhaBaseDivergiu(f"a regra de leitura sem o IC de {nome}: {vals}")
        return vals
    sono = {}
    for nome in LINHAS_SONO:
        inf, sup = lim(f"resto_dormir|{nome}", "ic_inferior"), lim(f"resto_dormir|{nome}", "ic_superior")
        if all(v > 0 for v in inf.values()):
            texto = "preserva o sono"
        elif any(v <= 0 for v in sup.values()):
            texto = "apaga o sono"
        else:
            texto = "indeterminado"
        sono[nome] = {"leitura": texto, "ic_inferior": inf, "ic_superior": sup}
    inf_estado = lim("eta2_acordado|ESTADO", "ic_inferior")
    sups = {nome: lim(f"eta2_acordado|{nome}", "ic_superior") for nome in LINHAS_ALEM}
    if sum(1 for v in inf_estado.values() if v > CORTE_ETA2) >= 2:
        alem = "ha o que creditar alem do sono"
    elif all(v < CORTE_ETA2 for s in sups.values() for v in s.values()):
        alem = "so o sono"
    else:
        alem = "indeterminado"
    return {"L-SONO": sono,
            "L-ALEM": {"leitura": alem, "eta2_acordado_estado_inferior": inf_estado, "eta2_acordado_superior": sups, "corte": CORTE_ETA2},
            "nao_demonstra": ["nada sobre o credito: uma linha de base que preserva o sono nao mostra que ensinar o sono ajuda",
                              "nada sobre o corpo depois da C3, nem sobre o jogo web, nem fora dos 14 dias e dos lugares da C4",
                              "a medida primaria de bem-estar segue em aberto",
                              "a FASE e a ESTADO sao leituras com a vida inteira, e nao mecanismos que o cerebro teria ao vivo",
                              "o ocioso e o emburrar tem poucas decisoes por vida e ficam so como descritivo"]}


def analisar(registros: list[dict]) -> dict:
    """os resumos dos tres conjuntos em cada lugar deles (falha alto se faltar algum) e a regra de leitura no HOJE da run"""
    resumos = {f"{g}|{b}|{lugar}": resumo(registros, g, b, lugar) for g, b in r1.CONJUNTOS for lugar in r1.lugares_do(g)}
    return {"resumos": resumos, "leitura": leitura(resumos)}


# ================================================================== a run
def exigir_aprovado(plano: str) -> None:
    linhas = [x for x in plano.splitlines() if x.startswith("**Status:")]
    if not linhas or not linhas[0].startswith(r1.STATUS):
        raise RuntimeError(f"{PLANO} nao esta APROVADO pelo Matheus: {linhas[:1] or 'sem a linha do status'}")


def conferir_config(cfg: dict) -> None:
    faltam, sobram = (CHAVES_CONFIG - {"descricao"}) - set(cfg), set(cfg) - CHAVES_CONFIG
    if faltam or sobram:
        raise ValueError(f"config: faltam {sorted(faltam)}, sobram {sorted(sobram)}")
    u = cfg["unidades"]
    erros = [m for m, ok in ((f"fase {cfg['fase']!r}", cfg["fase"] == FASE), (f"plano {cfg['plano']!r}", cfg["plano"] == PLANO),
                             (f"bases {u.get('bases')}", tuple(u.get("bases", ())) == r1.BASES),
                             (f"K {u.get('k')}", u.get("k") == r1.K_POR_BASE), (f"prefixo {u.get('prefixo')!r}", u.get("prefixo") == r1.PREFIXO),
                             (f"dias {cfg['dias']}", cfg["dias"] == r1.DIAS),
                             (f"orcamento {cfg['orcamento_por_dia']}", cfg["orcamento_por_dia"] == r1.ORCAMENTO_POR_DIA)) if not ok]
    if erros:
        raise ValueError(f"o replay segue o plano a letra (as vidas da run do PV-2): {erros}")


def exigir_disco(pasta: Path) -> float:
    """o espaco livre no disco da saida, em GB; falha alto abaixo do piso"""
    livre = shutil.disk_usage(pasta if pasta.exists() else pasta.anchor).free / 2 ** 30
    if livre < PISO_DISCO_GB:
        raise RuntimeError(f"so {livre:.1f} GB livres em {pasta.anchor}; o piso e {PISO_DISCO_GB} GB")
    return livre


def _vidas_e_fontes() -> tuple:
    unidades = bv.unidades_derivadas(list(r1.BASES), r1.K_POR_BASE, r1.PREFIXO)
    vidas = r1.vidas_esperadas(unidades)
    return vidas, {r1.nome_da_vida(g, b, d, lugar, u["semente"]) for g, b, d, lugar, u in vidas}


def rodar(cfg: dict, pasta: Path, processos: int, vidas_tar: Path, caminho_config: Path | None = None) -> dict:
    if processos > r1.MAX_PROCESSOS:
        raise ValueError(f"no maximo {r1.MAX_PROCESSOS} processos (V3-D8)")
    conferir_config(cfg)
    exigir_aprovado((RAIZ / PLANO).read_text(encoding="utf-8"))
    if pasta.exists():
        raise FileExistsError(f"{pasta} ja existe: o replay se recusa a gravar por cima (uma vez)")
    livre = exigir_disco(RAIZ)
    fonte = r1.conferir_fonte(vidas_tar)
    vidas, nomes = _vidas_e_fontes()
    gravadas = r1.ler_gravadas(nomes)
    do_r1 = ler_r1(nomes)
    pasta.mkdir(parents=True)
    inicio = time.time()
    rc = orq.rc
    meta = {"fase": FASE, "plano": PLANO, "plano_sha256": rc._sha_arquivo(RAIZ / PLANO), "config": cfg,
            "config_arquivo": None if caminho_config is None else rc._relativo(caminho_config),
            "config_sha256": None if caminho_config is None else rc._sha_arquivo(caminho_config),
            "comando": " ".join(["python", *sys.argv]) if sys.argv and sys.argv[0] else None, "python": platform.python_version(),
            "orquestrador_sha256": rc._sha_arquivo(Path(__file__)), "r1_sha256": rc._sha_arquivo(Path(r1.__file__)),
            "pv2_sha256": rc._sha_arquivo(Path(pv2.__file__)),
            "git_head": rc._git("rev-parse", "HEAD"), "git_limpo": rc._git("status", "--porcelain") == "", "processos": processos,
            "conjuntos": [list(c) for c in r1.CONJUNTOS], "vidas": len(vidas), "disco_livre_gb": livre,
            "fonte": {"pasta": r1.FONTE, "vidas_tar": str(vidas_tar), "git_head": fonte["git_head"],
                      "artefatos_sha256": fonte["artefatos_sha256"], "r1": FONTE_R1,
                      "r1_medidas_sha256": bv._sha(RAIZ / FONTE_R1 / "medidas.json.gz")},
            "linhas": list(LINHAS), "ks": list(met.KS_MOVEL), "piso": met.PISO_LINHA_BASE, "cortes": {"eta2": CORTE_ETA2},
            "sha256": {n: rc._sha_arquivo(RAIZ / "digilab" / n) for n in ("config.py", "engine.py", "metrics.py", "mundo.py", "corpo.py")}
            | {f"digibrain/{p.name}": rc._sha_arquivo(p) for p in sorted((RAIZ / "digilab" / "digibrain").glob("*.py"))},
            "inicio": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(inicio))}
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    temp = pasta / "_vidas"
    r1.extrair(vidas_tar, {r1.membro_da_vida(g, b, d, lugar, u["semente"]) for g, b, d, lugar, u in vidas}, temp)
    t0 = time.perf_counter()
    try:
        tarefas = []
        for v in vidas:
            nome = r1.nome_da_vida(v[0], v[1], v[2], v[3], v[4]["semente"])
            tarefas.append((_tarefa, (cfg["dias"], cfg["orcamento_por_dia"], v, str(temp), gravadas[nome], do_r1[nome])))
        registros = rc._executar(tarefas, processos)
    finally:
        shutil.rmtree(temp, ignore_errors=True)
    meta["vidas_parede_s"] = time.perf_counter() - t0
    if len(registros) != len(vidas):
        raise RuntimeError(f"{len(registros)} vidas, eram {len(vidas)}")
    bv._gravar(pasta / "medidas.json", bv._dump(sorted(registros, key=lambda r: r["vida"])))
    lidos = json.loads((pasta / "medidas.json").read_text(encoding="utf-8"))
    resultado = {"fase": FASE, "plano": PLANO, "vidas": len(lidos), **analisar(lidos)}
    bv._gravar(pasta / "resultado.json", bv._dump(resultado))
    with open(pasta / "medidas.json", "rb") as f, open(pasta / "medidas.json.gz", "wb") as s, \
            gzip.GzipFile(filename="", mode="wb", fileobj=s, mtime=0, compresslevel=9) as gz:
        shutil.copyfileobj(f, gz)
    meta["fim"] = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
    meta["duracao_s"] = time.time() - inicio
    meta["artefatos_sha256"] = {n: bv._sha(pasta / n) for n in ("medidas.json", "medidas.json.gz", "resultado.json")}
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    return {"meta": meta, "registros": registros, "resultado": resultado}


def fumaca(n: int, vidas_tar: Path) -> dict:
    """a fumaca: as `n` primeiras vidas do HOJE da run, rejogadas com todas as conferencias (a C-IGUAL-R1 entre elas); devolve so a
    conferencia e o tempo, nenhuma medida da linha de base"""
    r1.conferir_fonte(vidas_tar)
    vidas, _ = _vidas_e_fontes()
    total = len(vidas)
    vidas = [v for v in vidas if (v[0], v[1]) == PRINCIPAL][:n]
    nomes = {r1.nome_da_vida(g, b, d, lugar, u["semente"]) for g, b, d, lugar, u in vidas}
    gravadas, do_r1 = r1.ler_gravadas(nomes), ler_r1(nomes)
    querem = {r1.membro_da_vida(g, b, d, lugar, u["semente"]) for g, b, d, lugar, u in vidas}
    textos = {}
    with tarfile.open(vidas_tar, "r:gz") as tar:
        for m in tar:
            if m.name in querem:
                textos[m.name] = tar.extractfile(m).read().decode("utf-8")
                if len(textos) == len(querem):
                    break
    custos = []
    for g, b, d, lugar, u in vidas:
        nome = r1.nome_da_vida(g, b, d, lugar, u["semente"])
        r = rejogar(r1.DIAS, r1.ORCAMENTO_POR_DIA, g, b, d, lugar, u, textos[r1.membro_da_vida(g, b, d, lugar, u["semente"])],
                    gravadas[nome], do_r1[nome])
        custos.append(r["custo"]["vida_parede"])
    por_vida = sum(custos) / len(custos)
    return {"vidas": len(vidas), "conferencias": "passam", "parede_por_vida_s": por_vida,
            "projecao_parede_h_4_processos": total * por_vida / r1.MAX_PROCESSOS / 3600, "corte_h": CORTE_CUSTO_H}


def _resumo(r: dict) -> str:
    lei = r["leitura"]
    sono = "; ".join(f"{n}: {v['leitura']}" for n, v in lei["L-SONO"].items())
    return f"{r['vidas']} vidas; L-SONO: {sono}; L-ALEM: {lei['L-ALEM']['leitura']}"


def main() -> None:
    ap_ = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap_.add_argument("--config", default=None)
    ap_.add_argument("--saida", default=None)
    ap_.add_argument("--vidas", default=str(r1.VIDAS_PADRAO), help="o vidas.tar.gz da run do PV-2")
    ap_.add_argument("--processos", type=int, default=1)
    ap_.add_argument("--g1", type=int, default=None, help="a fumaca em N vidas da run: as conferencias e o tempo, sem medida")
    a = ap_.parse_args()
    if a.g1 is not None:
        print(bv._dump(fumaca(a.g1, Path(a.vidas))))
        return
    if a.config is None:
        raise SystemExit("o replay pede --config (ou --g1 N)")
    caminho = Path(a.config)
    cfg = json.loads(caminho.read_text(encoding="utf-8"))
    conferir_config(cfg)
    pre_run.exigir(ORQUESTRADOR, a.config, a.processos)
    print(_resumo(rodar(cfg, Path(a.saida) if a.saida else RAIZ / SAIDA, a.processos, Path(a.vidas), caminho)["resultado"]))


if __name__ == "__main__":
    main()
