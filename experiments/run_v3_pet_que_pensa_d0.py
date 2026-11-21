"""O D0 do pet que pensa (docs/TAREFA_V3_PET_QUE_PENSA.md, secao 4): o replay descritivo, so leitura, sem gate, sem classe, sem vida nova.

Pergunta: nas vidas ja gravadas, em quantas decisoes o planejador poderia decidir (as que nao sao o reflexo do sono, o sono que segura
nem a escolha segurada), e quantas tem conflito (a fome urgente com a energia na faixa do reflexo suave, em [lambda_sono/2,
lambda_sono))? Por lugar e por dono, no corpo de hoje (o HOJE da run do PV-2, 2 400 vidas) e no v38 (o HOJE da checagem do v38, 320).
O OLF-0 fica de fora: o D0 pede o corpo de hoje e o v38.

As vidas sao as do R1, do R-a e do R-sono, rejogadas pelo log com a `ConfigRastro` ligada, com as conferencias do R-sono
(`run_v3_pet_vivo_sono.rejogar`: a C-G1, a C-FECHO, a C-UMA-VEZ, a C-REFLEXO e a C-SOMA, que falham alto) e a C-FONTE do R1. Por vida,
a `metrics.medidas_d0_plano`, com o `lambda_sono` e o `urgencia_lambda` dos inatos do cerebro da vida (o v38 tem os do E1).

  python experiments/run_v3_pet_que_pensa_d0.py --config experiments/configs/v3_pet_que_pensa/d0.json --processos 4 \
      --vidas D:\\Trab\\digilab\\guarda_vidas\\pv2_run\\vidas.tar.gz
  python experiments/run_v3_pet_que_pensa_d0.py --g1 2 --vidas ...    # a fumaca: 2 vidas com todas as conferencias, sem gravar

O replay se recusa a rodar sem a tarefa APROVADA, com a pasta de saida existente, sem o `pre_run` e com menos de 10 GB livres.
"""
from __future__ import annotations

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
import run_v3_pet_vivo_sono as sono  # noqa: E402
from digilab import metrics as met  # noqa: E402
from digilab.config import CONFIG_PADRAO  # noqa: E402
from digilab.events import LogDeEventos  # noqa: E402
from digilab.mundo import reproduzir_mundo  # noqa: E402

orq = r1.orq
TAREFA = "docs/TAREFA_V3_PET_QUE_PENSA.md"
STATUS = "**Status: APROVADO pelo Matheus"
ORQUESTRADOR = "experiments/run_v3_pet_que_pensa_d0.py"
FASE = "d0"
SAIDA = "artifacts_v3_pet_que_pensa/d0/run"
CONJUNTOS = (("run", "HOJE"), ("v38", "HOJE"))           # o corpo de hoje e o v38 (a secao 4 da tarefa)
CHAVES_CONFIG = r1.CHAVES_CONFIG


def piso_de(lambda_sono: int) -> int:
    """o piso duro do reflexo no desenho (PQ3-4): `lambda_sono // 2` (S/8; PROPOSTO, SEM FONTE)"""
    return lambda_sono // 2


class D0Divergiu(RuntimeError):
    """o D0 sem o que a medida le, ou a soma das decisoes nao fecha"""


def conferir_d0(vida: str, d0: dict, cs: dict) -> None:
    """a C-D0 (falha alto): o D0 conta as mesmas decisoes do R-sono, e o reflexo dele e o REFLEXO mais o SEGURA do caminho do sono
    (nas decisoes de dormir, que sao as unicas com o reflexo)"""
    if d0["n"] != cs["n"]:
        raise D0Divergiu(f"C-D0, {vida}: {d0['n']} decisoes no D0 e {cs['n']} no caminho do sono")
    if (d0["fora"]["REFLEXO"], d0["fora"]["SEGURA"]) != (cs["decisoes"]["REFLEXO"], cs["decisoes"]["SEGURA"]):
        raise D0Divergiu(f"C-D0, {vida}: o reflexo do D0 nao e o do caminho do sono")
    if d0["abertas_hoje"] + sum(d0["fora"].values()) != d0["n"]:
        raise D0Divergiu(f"C-D0, {vida}: as abertas e as de fora nao somam as decisoes")


def rejogar(dias: int, orcamento: int, grupo: str, braco: str, dono: str, lugar: str, unidade: dict, texto: str,
            gravada: dict) -> dict:
    """uma vida rejogada pelo log, com o rastro ligado e as conferencias do R-sono; as medidas do D0"""
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
    lam, urg = c.inatos.lambda_sono, c.inatos.urgencia_lambda
    cs = met.medidas_caminho_sono(c.motivos, lam, passo)
    sono.conferir_caminhos(vida, grupo, c.motivos, cs)
    d0 = json.loads(json.dumps(met.medidas_d0_plano(c.motivos, lam, piso_de(lam), urg)))
    conferir_d0(vida, d0, cs)
    return {"vida": vida, "grupo": grupo, "braco": braco, "dono": dono, "lugar": lugar, "semente": semente, "base": unidade["base"],
            "k": unidade["k"], "lambda_sono": lam, "piso": piso_de(lam), "urgencia_lambda": urg, "d0": d0,
            "custo": {"vida_cpu": time.process_time() - c0, "vida_parede": time.perf_counter() - p0}}


def _tarefa(dias: int, orcamento: int, vida: tuple, pasta_vidas: str, gravada: dict) -> dict:
    grupo, braco, dono, lugar, unidade = vida
    texto = (Path(pasta_vidas) / r1.membro_da_vida(grupo, braco, dono, lugar, unidade["semente"])).read_text(encoding="utf-8")
    return rejogar(dias, orcamento, grupo, braco, dono, lugar, unidade, texto, gravada)


def vidas_do_d0() -> tuple:
    """as vidas do HOJE da run e do HOJE do v38, na ordem fixa do R1, e os nomes delas"""
    todas, _ = ra._vidas_e_fontes()
    vidas = [v for v in todas if (v[0], v[1]) in CONJUNTOS]
    return vidas, {r1.nome_da_vida(g, b, d, lugar, u["semente"]) for g, b, d, lugar, u in vidas}


# ================================================================== a descricao (sem gate, sem regra de leitura)
def escalares(d0: dict) -> dict:
    """as medidas de uma vida como escalares nomeados (None onde a vida nao tem a medida)"""
    n = d0["n"]
    out = {k: d0[k] for k in ("n", "F_ABERTAS_HOJE", "F_ABERTAS_PLAN_TETO", "F_ABERTAS_PLAN_PISO", "F_FAIXA", "F_CONFLITO",
                              "F_CONFLITO_NA_FAIXA", "abertas_hoje", "faixa", "conflito", "abaixo_piso")}
    out.update({f"F_FORA:{k}": v / n for k, v in d0["fora"].items()})
    a = d0["abertas_hoje"]
    out.update({"abertas:F_SORTEIO": None if a == 0 else d0["abertas_hoje_sorteio"] / a,
                "abertas:F_NADA_A_FAZER": None if a == 0 else d0["abertas_hoje_nada_a_fazer"] / a,
                "abertas:F_FOME_URGENTE": None if a == 0 else d0["abertas_hoje_fome_urgente"] / a,
                "abertas:F_DORMIR": None if a == 0 else d0["abertas_hoje_dormir"] / a,
                "F_ABAIXO_PISO": d0["abaixo_piso"] / n})
    return out


def resumo(registros: list[dict], grupo: str, braco: str, lugar: str) -> dict:
    """por medida: a media dos donos por unidade e o IC95 pelo t sobre as unidades; ao lado, a media por dono, sem IC (como no R-sono)"""
    vidas = [r for r in registros if (r["grupo"], r["braco"], r["lugar"]) == (grupo, braco, lugar)]
    if not vidas:
        raise D0Divergiu(f"nenhuma vida de {grupo}/{braco}/{lugar}")
    esc = [(r["semente"], r["dono"], escalares(r["d0"])) for r in vidas]
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


def analisar(registros: list[dict]) -> dict:
    """os resumos dos dois conjuntos em cada lugar deles (falha alto se faltar algum), sem regra de leitura (o D0 e descritivo)"""
    resumos = {f"{g}|{b}|{lugar}": resumo(registros, g, b, lugar) for g, b in CONJUNTOS for lugar in r1.lugares_do(g)}
    return {"resumos": resumos,
            "nao_demonstra": ["nada sobre o planejador decidir: o D0 conta onde ele poderia entrar, nas vidas de hoje, sem ele",
                              "nada sobre o Tempo bem, a saude ou a exaustao: so o D1 mede",
                              "o v38 da so os limites (o piso e o teto) das abertas com o desenho: o dormindo nao esta no motivo",
                              "nada fora dos 14 dias, do mundo do MVP e dos lugares da C4, nem sobre o jogo web",
                              "o piso lambda_sono/2 e a fome urgente pelo urgencia_lambda sao PROPOSTOS, SEM FONTE"]}


# ================================================================== a run
def exigir_aprovada(texto: str) -> None:
    linhas = [x for x in texto.splitlines() if x.startswith("**Status:")]
    if not linhas or not linhas[0].startswith(STATUS):
        raise RuntimeError(f"{TAREFA} nao esta APROVADA pelo Matheus: {linhas[:1] or 'sem a linha do status'}")


def conferir_config(cfg: dict) -> None:
    faltam, sobram = (CHAVES_CONFIG - {"descricao"}) - set(cfg), set(cfg) - CHAVES_CONFIG
    if faltam or sobram:
        raise ValueError(f"config: faltam {sorted(faltam)}, sobram {sorted(sobram)}")
    u = cfg["unidades"]
    erros = [m for m, ok in ((f"fase {cfg['fase']!r}", cfg["fase"] == FASE), (f"plano {cfg['plano']!r}", cfg["plano"] == TAREFA),
                             (f"bases {u.get('bases')}", tuple(u.get("bases", ())) == r1.BASES),
                             (f"K {u.get('k')}", u.get("k") == r1.K_POR_BASE), (f"prefixo {u.get('prefixo')!r}", u.get("prefixo") == r1.PREFIXO),
                             (f"dias {cfg['dias']}", cfg["dias"] == r1.DIAS),
                             (f"orcamento {cfg['orcamento_por_dia']}", cfg["orcamento_por_dia"] == r1.ORCAMENTO_POR_DIA)) if not ok]
    if erros:
        raise ValueError(f"o D0 rejoga as vidas da run do PV-2 a letra: {erros}")


def rodar(cfg: dict, pasta: Path, processos: int, vidas_tar: Path, caminho_config: Path | None = None) -> dict:
    if processos > r1.MAX_PROCESSOS:
        raise ValueError(f"no maximo {r1.MAX_PROCESSOS} processos (V3-D8)")
    conferir_config(cfg)
    exigir_aprovada((RAIZ / TAREFA).read_text(encoding="utf-8"))
    if pasta.exists():
        raise FileExistsError(f"{pasta} ja existe: o replay se recusa a gravar por cima (uma vez)")
    livre = ra.exigir_disco(RAIZ)
    fonte = r1.conferir_fonte(vidas_tar)
    vidas, nomes = vidas_do_d0()
    gravadas = r1.ler_gravadas(nomes)
    pasta.mkdir(parents=True)
    inicio = time.time()
    rc = orq.rc
    meta = {"fase": FASE, "tarefa": TAREFA, "tarefa_sha256": rc._sha_arquivo(RAIZ / TAREFA), "config": cfg,
            "config_arquivo": None if caminho_config is None else rc._relativo(caminho_config),
            "config_sha256": None if caminho_config is None else rc._sha_arquivo(caminho_config),
            "comando": " ".join(["python", *sys.argv]) if sys.argv and sys.argv[0] else None, "python": platform.python_version(),
            "orquestrador_sha256": rc._sha_arquivo(Path(__file__)), "r1_sha256": rc._sha_arquivo(Path(r1.__file__)),
            "ra_sha256": rc._sha_arquivo(Path(ra.__file__)), "sono_sha256": rc._sha_arquivo(Path(sono.__file__)),
            "pv2_sha256": rc._sha_arquivo(Path(pv2.__file__)),
            "git_head": rc._git("rev-parse", "HEAD"), "git_limpo": rc._git("status", "--porcelain") == "", "processos": processos,
            "conjuntos": [list(c) for c in CONJUNTOS], "vidas": len(vidas), "disco_livre_gb": livre,
            "fonte": {"pasta": r1.FONTE, "vidas_tar": str(vidas_tar), "git_head": fonte["git_head"],
                      "artefatos_sha256": fonte["artefatos_sha256"]},
            "fora_da_disputa": list(met.FORA_DA_DISPUTA_D0), "passo": CONFIG_PADRAO.intervalo_decisao_ticks,
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
    resultado = {"fase": FASE, "tarefa": TAREFA, "vidas": len(lidos), **analisar(lidos)}
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
    """a fumaca: as `n` primeiras vidas do HOJE da run e as `n` primeiras do v38, rejogadas com todas as conferencias; devolve so a
    conferencia e o tempo, nenhuma medida do D0"""
    r1.conferir_fonte(vidas_tar)
    todas, _ = vidas_do_d0()
    vidas: list = []
    for c in CONJUNTOS:
        vidas += [v for v in todas if (v[0], v[1]) == c][:n]
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
        r = rejogar(r1.DIAS, r1.ORCAMENTO_POR_DIA, g, b, d, lugar, u, textos[r1.membro_da_vida(g, b, d, lugar, u["semente"])],
                    gravadas[r1.nome_da_vida(g, b, d, lugar, u["semente"])])
        custos.append(r["custo"]["vida_parede"])
    por_vida = sum(custos) / len(custos)
    return {"vidas": len(vidas), "conferencias": "passam", "parede_por_vida_s": por_vida,
            "projecao_parede_h_4_processos": len(todas) * por_vida / r1.MAX_PROCESSOS / 3600}


def _resumo(r: dict) -> str:
    partes = []
    for chave, v in r["resumos"].items():
        m = v["medidas"]
        partes.append(f"{chave}: abertas hoje {m['F_ABERTAS_HOJE']['media']:.3f}, teto com o plano {m['F_ABERTAS_PLAN_TETO']['media']:.3f}, "
                      f"conflito {m['F_CONFLITO']['media']:.4f}")
    return f"{r['vidas']} vidas\n" + "\n".join(partes)


def main() -> None:
    ap_ = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap_.add_argument("--config", default=None)
    ap_.add_argument("--saida", default=None)
    ap_.add_argument("--vidas", default=str(r1.VIDAS_PADRAO), help="o vidas.tar.gz da run do PV-2")
    ap_.add_argument("--processos", type=int, default=1)
    ap_.add_argument("--g1", type=int, default=None, help="a fumaca em N vidas de cada conjunto: as conferencias e o tempo, sem medida")
    a = ap_.parse_args()
    if a.g1 is not None:
        print(bv._dump(fumaca(a.g1, Path(a.vidas))))
        return
    if a.config is None:
        raise SystemExit("o D0 pede --config (ou --g1 N)")
    caminho = Path(a.config)
    cfg = json.loads(caminho.read_text(encoding="utf-8"))
    conferir_config(cfg)
    pre_run.exigir(ORQUESTRADOR, a.config, a.processos)
    print(_resumo(rodar(cfg, Path(a.saida) if a.saida else RAIZ / SAIDA, a.processos, Path(a.vidas), caminho)["resultado"]))


if __name__ == "__main__":
    main()
