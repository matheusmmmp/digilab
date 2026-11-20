"""O replay do R-sono (docs/PLANO_ANALISE_V3_PET_VIVO_SONO.md, APROVADO): o sono vem do reflexo ou dos pesos, so leitura.

As mesmas vidas do R1 e do R-a (o HOJE e o OLF-0 da run do PV-2 e o HOJE da checagem do v38; 5 120), rejogadas pelo log com a
ConfigRastro ligada. Nenhuma vida nova, nenhuma faixa nova, nada creditado. Por vida, as medidas de `metrics.medidas_caminho_sono`
(o caminho de cada decisao de dormir, o do episodio, a margem no sorteio). As conferencias que falham alto, antes de qualquer
medida: as do R1 (C-FONTE, C-G1, C-FECHO, C-UMA-VEZ), a C-REFLEXO (sem o sono que segura, o reflexo e so a energia abaixo de
`lambda_sono`, e fora dele a energia nao esta abaixo) e a C-SOMA (os caminhos somam o dormir da vida).

  python experiments/run_v3_pet_vivo_sono.py --config experiments/configs/v3_pet_vivo/sono.json --processos 4
  python experiments/run_v3_pet_vivo_sono.py --g1 2      # a fumaca: 2 vidas reais com todas as conferencias, sem gravar medida

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
import run_v3_pet_vivo_ra as ra  # noqa: E402
from digilab import metrics as met  # noqa: E402
from digilab.config import CONFIG_DIGIBRAIN_INATOS, CONFIG_PADRAO  # noqa: E402
from digilab.events import LogDeEventos  # noqa: E402
from digilab.mundo import reproduzir_mundo  # noqa: E402

orq = r1.orq
PLANO = "docs/PLANO_ANALISE_V3_PET_VIVO_SONO.md"
ORQUESTRADOR = "experiments/run_v3_pet_vivo_sono.py"
FASE = "sono"
SAIDA = "artifacts_v3_pet_vivo/sono/run"
LUGARES = r1.LUGARES
PRINCIPAL = r1.PRINCIPAL
CORTE_REFLEXO = 0.10                                         # SN-3: o limite de cima da F_PESOS abaixo dele nos 3 lugares; SEM FONTE
CORTE_SORTEIO = 0.25                                         # SN-3: o limite de baixo da F_PESOS acima dele em 2 lugares; SEM FONTE
LUGARES_SORTEIO = 2
CORTE_CUSTO_H = 2.0                                          # SN-4: a projecao de parede com 4 processos
SEM_SEGURA = ("run",)                                        # os grupos com o sono que segura desligado (o v38 o liga)
CHAVES_CONFIG = r1.CHAVES_CONFIG
LAMBDA_SONO = CONFIG_DIGIBRAIN_INATOS.lambda_sono
LEITURA_REFLEXO = "quase tudo reflexo: a alavanca e o corpo"
LEITURA_SORTEIO = "boa parte passa pelo sorteio: vale um teste de recompensa"
LEITURA_MISTO = "misto"


class SonoDivergiu(RuntimeError):
    """uma conferencia do R-sono falhou (a C-REFLEXO ou a C-SOMA), ou a analise ficou sem o que a regra le"""


def conferir_caminhos(vida: str, grupo: str, motivos: list[dict], cs: dict) -> None:
    """C-REFLEXO e C-SOMA numa vida (falha alto). Sem o sono que segura (a run): nenhum SEGURA, e nenhuma decisao sem reflexo com a
    energia abaixo de `lambda_sono`. Em todo grupo: os caminhos somam as decisoes de dormir com o rastro, por decisao e por episodio"""
    if grupo in SEM_SEGURA:
        if cs["decisoes"]["SEGURA"]:
            raise SonoDivergiu(f"C-REFLEXO, {vida}: {cs['decisoes']['SEGURA']} decisoes com o reflexo e a energia em lambda_sono ou acima")
        if cs["sem_reflexo_exausto"]:
            raise SonoDivergiu(f"C-REFLEXO, {vida}: {cs['sem_reflexo_exausto']} decisoes sem o reflexo com a energia abaixo de lambda_sono")
    dormir = sum(1 for m in motivos if "cadeia" in m and m["escolha"][0] == "dormir")
    reflexos = sum(1 for m in motivos if "cadeia" in m and m["reflexo"])
    if not (sum(cs["decisoes"].values()) == sum(cs["ticks_episodio"].values()) // cs["passo"] == cs["dormir"] == dormir):
        raise SonoDivergiu(f"C-SOMA, {vida}: os caminhos nao somam as {dormir} decisoes de dormir")
    if cs["decisoes"]["REFLEXO"] + cs["decisoes"]["SEGURA"] != reflexos:
        raise SonoDivergiu(f"C-SOMA, {vida}: os caminhos do reflexo nao somam as {reflexos} decisoes com o reflexo")
    if sum(cs["ticks_decisao"].values()) != dormir * cs["passo"]:
        raise SonoDivergiu(f"C-SOMA, {vida}: os ticks dos caminhos nao somam os ticks de sono")


def rejogar(dias: int, orcamento: int, grupo: str, braco: str, dono: str, lugar: str, unidade: dict, texto: str,
            gravada: dict) -> dict:
    """uma vida rejogada pelo log, com o rastro ligado: a C-G1, a C-FECHO e a C-UMA-VEZ como no R1, a C-REFLEXO, a C-SOMA e as
    medidas do caminho do sono"""
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
    cs = json.loads(json.dumps(met.medidas_caminho_sono(c.motivos, LAMBDA_SONO, passo)))
    conferir_caminhos(vida, grupo, c.motivos, cs)
    return {"vida": vida, "grupo": grupo, "braco": braco, "dono": dono, "lugar": lugar, "semente": semente, "base": unidade["base"],
            "k": unidade["k"], "sono": cs, "custo": {"vida_cpu": time.process_time() - c0, "vida_parede": time.perf_counter() - p0}}


def _tarefa(dias: int, orcamento: int, vida: tuple, pasta_vidas: str, gravada: dict) -> dict:
    grupo, braco, dono, lugar, unidade = vida
    texto = (Path(pasta_vidas) / r1.membro_da_vida(grupo, braco, dono, lugar, unidade["semente"])).read_text(encoding="utf-8")
    return rejogar(dias, orcamento, grupo, braco, dono, lugar, unidade, texto, gravada)


# ================================================================== a analise (secoes 5 e 6 do plano, escritas antes)
def escalares(cs: dict) -> dict:
    """as medidas de uma vida como escalares nomeados (None onde a vida nao tem a medida)"""
    dormir = cs["dormir"]
    ticks = dormir * cs["passo"]
    out = {"F_PESOS": cs["F_PESOS"], "F_PESOS_DEC": cs["F_PESOS_DEC"], "dormir": dormir, "fracao_dormir": dormir / cs["n"]}
    for caminho in met.CAMINHOS_SONO:
        out[f"decisoes:{caminho}"] = cs["decisoes"][caminho]
        out[f"episodios:{caminho}"] = cs["episodios"][caminho]
        out[f"fracao_decisoes:{caminho}"] = None if dormir == 0 else cs["decisoes"][caminho] / dormir
        out[f"ticks_decisao:{caminho}"] = cs["ticks_decisao"][caminho]
        out[f"ticks_episodio:{caminho}"] = cs["ticks_episodio"][caminho]
        out[f"fracao_ticks_episodio:{caminho}"] = None if ticks == 0 else cs["ticks_episodio"][caminho] / ticks
    out.update({f"margem:{k}": v for k, v in cs["margem"].items()})
    out.update({f"acordado:{k}": v for k, v in cs["acordado"].items()})
    return out


def resumo(registros: list[dict], grupo: str, braco: str, lugar: str) -> dict:
    """por medida: a media dos donos por unidade e o IC95 pelo t sobre as unidades; ao lado, a media por dono, sem IC (como no R1)"""
    vidas = [r for r in registros if (r["grupo"], r["braco"], r["lugar"]) == (grupo, braco, lugar)]
    if not vidas:
        raise SonoDivergiu(f"nenhuma vida de {grupo}/{braco}/{lugar}")
    esc = [(r["semente"], r["dono"], escalares(r["sono"])) for r in vidas]
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
    """a regra da secao 6, escrita antes, no HOJE da run, pelos limites do IC95 da F_PESOS nos 3 lugares (os cortes da SN-3, SEM
    FONTE)"""
    f = {lugar: resumos[f"{PRINCIPAL[0]}|{PRINCIPAL[1]}|{lugar}"]["medidas"]["F_PESOS"] for lugar in LUGARES}
    inf = {lugar: v["ic_inferior"] for lugar, v in f.items()}
    sup = {lugar: v["ic_superior"] for lugar, v in f.items()}
    if any(v is None for v in (*inf.values(), *sup.values())):
        raise SonoDivergiu(f"a regra de leitura sem o IC da F_PESOS: {inf}, {sup}")
    if all(v < CORTE_REFLEXO for v in sup.values()):
        texto = LEITURA_REFLEXO
    elif sum(1 for v in inf.values() if v > CORTE_SORTEIO) >= LUGARES_SORTEIO:
        texto = LEITURA_SORTEIO
    else:
        texto = LEITURA_MISTO
    return {"L-CAMINHO": {"leitura": texto, "F_PESOS": {lugar: v["media"] for lugar, v in f.items()}, "ic_inferior": inf,
                          "ic_superior": sup, "cortes": {"reflexo": CORTE_REFLEXO, "sorteio": CORTE_SORTEIO,
                                                         "lugares_sorteio": LUGARES_SORTEIO}},
            "nao_demonstra": ["nada sobre a recompensa: o replay diz por onde o pet dorme, e nao o que o dono mudaria",
                              "nada sobre o que e melhor para o pet: a medida primaria (Tempo bem) nao entra aqui",
                              "nada sobre o corpo depois da C3 ou da C4, nem sobre o jogo web, nem fora dos 14 dias e dos lugares da C4",
                              "o v38 e descritivo: 2 lugares, 40 unidades, com o sono que segura ligado",
                              "os cortes sao SEM FONTE"]}


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


def rodar(cfg: dict, pasta: Path, processos: int, vidas_tar: Path, caminho_config: Path | None = None) -> dict:
    if processos > r1.MAX_PROCESSOS:
        raise ValueError(f"no maximo {r1.MAX_PROCESSOS} processos (V3-D8)")
    conferir_config(cfg)
    exigir_aprovado((RAIZ / PLANO).read_text(encoding="utf-8"))
    if pasta.exists():
        raise FileExistsError(f"{pasta} ja existe: o replay se recusa a gravar por cima (uma vez)")
    livre = ra.exigir_disco(RAIZ)
    fonte = r1.conferir_fonte(vidas_tar)
    vidas, nomes = ra._vidas_e_fontes()
    gravadas = r1.ler_gravadas(nomes)
    pasta.mkdir(parents=True)
    inicio = time.time()
    rc = orq.rc
    meta = {"fase": FASE, "plano": PLANO, "plano_sha256": rc._sha_arquivo(RAIZ / PLANO), "config": cfg,
            "config_arquivo": None if caminho_config is None else rc._relativo(caminho_config),
            "config_sha256": None if caminho_config is None else rc._sha_arquivo(caminho_config),
            "comando": " ".join(["python", *sys.argv]) if sys.argv and sys.argv[0] else None, "python": platform.python_version(),
            "orquestrador_sha256": rc._sha_arquivo(Path(__file__)), "r1_sha256": rc._sha_arquivo(Path(r1.__file__)),
            "ra_sha256": rc._sha_arquivo(Path(ra.__file__)), "pv2_sha256": rc._sha_arquivo(Path(pv2.__file__)),
            "git_head": rc._git("rev-parse", "HEAD"), "git_limpo": rc._git("status", "--porcelain") == "", "processos": processos,
            "conjuntos": [list(c) for c in r1.CONJUNTOS], "vidas": len(vidas), "disco_livre_gb": livre,
            "fonte": {"pasta": r1.FONTE, "vidas_tar": str(vidas_tar), "git_head": fonte["git_head"],
                      "artefatos_sha256": fonte["artefatos_sha256"]},
            "caminhos": list(met.CAMINHOS_SONO), "caminhos_pesos": list(met.CAMINHOS_PESOS), "lambda_sono": LAMBDA_SONO,
            "passo": CONFIG_PADRAO.intervalo_decisao_ticks,
            "cortes": {"reflexo": CORTE_REFLEXO, "sorteio": CORTE_SORTEIO, "lugares_sorteio": LUGARES_SORTEIO},
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
            tarefas.append((_tarefa, (cfg["dias"], cfg["orcamento_por_dia"], v, str(temp), gravadas[nome])))
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
    """a fumaca: as `n` primeiras vidas do HOJE da run, rejogadas com todas as conferencias (a C-REFLEXO e a C-SOMA entre elas);
    devolve so a conferencia e o tempo, nenhuma medida do caminho do sono"""
    r1.conferir_fonte(vidas_tar)
    vidas, _ = ra._vidas_e_fontes()
    total = len(vidas)
    vidas = [v for v in vidas if (v[0], v[1]) == PRINCIPAL][:n]
    nomes = {r1.nome_da_vida(g, b, d, lugar, u["semente"]) for g, b, d, lugar, u in vidas}
    gravadas = r1.ler_gravadas(nomes)
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
                    gravadas[nome])
        custos.append(r["custo"]["vida_parede"])
    por_vida = sum(custos) / len(custos)
    return {"vidas": len(vidas), "conferencias": "passam", "parede_por_vida_s": por_vida,
            "projecao_parede_h_4_processos": total * por_vida / r1.MAX_PROCESSOS / 3600, "corte_h": CORTE_CUSTO_H}


def _resumo(r: dict) -> str:
    lc = r["leitura"]["L-CAMINHO"]
    f = "; ".join(f"{lugar} {v:.3f}" for lugar, v in lc["F_PESOS"].items())
    return f"{r['vidas']} vidas; L-CAMINHO: {lc['leitura']} (F_PESOS: {f})"


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
