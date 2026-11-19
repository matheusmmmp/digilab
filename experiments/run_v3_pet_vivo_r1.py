"""PET_VIVO, R1: o replay do rastro da cadeia (docs/PLANO_ANALISE_V3_PET_VIVO_R1.md, APROVADO; docs/TAREFA_V3_PET_VIVO.md).

Pergunta (a secao 1 do plano): quanto do que muda no corpo do pet acontece no intervalo entre as decisoes, fora do r do mesmo tick? E o
que acontece no intervalo depende do que o pet fez? Os numeros vao ao plano do R2 (o credito do intervalo). Nenhuma medida e gate.

Nenhuma vida nova: as vidas sao as ja gravadas da run do PV-2 (`artifacts_v3_pet_vivo/pv2/run/`; a secao 3 do plano), rejogadas pelo
log com a `ConfigRastro` ligada (so leitura):
  - o HOJE da run (2 400 vidas), a leitura principal;
  - o OLF-0 da run (2 400), ao lado, sem regra de leitura;
  - o HOJE da checagem do v38 (320), a INT-8, descritiva.

As conferencias que falham alto, antes de qualquer medida (a secao 3.3):
  - C-FONTE: o sha256 do `vidas.tar.gz` e do `medidas.json.gz` iguais aos do `meta.json` da run do PV-2;
  - C-G1: cada vida rejogada com o rastro ligado sai com o log igual ao do disco e as medidas iguais as do `medidas.json.gz` (as do
    orquestrador do prototipo e as `medidas_pv2`; o custo e o contrafactual ficam fora). Se falhar, o replay para: nada se ajusta;
  - C-FECHO: por receptor e por decisao, a leitura da decisao k+1 menos a da decisao k e o delta do mesmo tick mais o do intervalo;
  - C-UMA-VEZ: cada intervalo vai de k a k+1, uma vez, e o tick do fim e o tick da decisao seguinte;
  - C-IGUAL: duas execucoes saem iguais (o teste, nas sementes dos testes; aqui, a ordem das vidas e fixa e nada depende do relogio).

A analise (as secoes 4 e 5, escritas antes): as medidas do `metrics.medidas_rastro` por vida; por (conjunto, lugar), a media dos 4 donos
por unidade (base, semente) e o IC95 pelo t; os donos tambem separados, sem IC; a regra de leitura L-FORA e L-ACAO no HOJE.

A trava: o replay de verdade recusa rodar sem o "APROVADO pelo Matheus" no plano, com a pasta de saida ja existente e sem o
`tools/pre_run.py` (o plano igual ao da `origin/main`; nenhuma outra run; ate 4 processos). O `--g1 N` e a fumaca da C-G1 em N vidas da
run, sem ler nenhuma medida do rastro (a secao 3.3); o `--custo` mede o tempo por vida nas sementes dos testes, ligado e desligado.
Uso: python experiments/run_v3_pet_vivo_r1.py --config experiments/configs/v3_pet_vivo/r1.json --processos 4
"""
from __future__ import annotations

import argparse
import gzip
import json
import platform
import re
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
import run_v2_digibrain_prototipo as orq  # noqa: E402
from digilab import metrics as met  # noqa: E402
from digilab.config import CONFIG_PADRAO, CONFIG_RASTRO_LIGADA  # noqa: E402
from digilab.events import LogDeEventos  # noqa: E402
from digilab.mundo import reproduzir_mundo  # noqa: E402

PLANO = "docs/PLANO_ANALISE_V3_PET_VIVO_R1.md"
ORQUESTRADOR = "experiments/run_v3_pet_vivo_r1.py"
STATUS = "**Status: APROVADO pelo Matheus"
FASE = "r1"
SAIDA = "artifacts_v3_pet_vivo/r1/run"
SAIDA_CUSTO = "artifacts_v3_pet_vivo/r1/custo.json"
FONTE = "artifacts_v3_pet_vivo/pv2/run"                      # o meta.json e o medidas.json.gz da run do PV-2, no git
VIDAS_PADRAO = Path(r"D:\Trab\digilab\v3-pet-vivo-pv2-run") / FONTE / "vidas.tar.gz"     # os logs, fora do git (a secao 3.2)
BASES = (26101, 26202, 26303, 26404, 26505)                  # as da run do PV-2: nenhuma vida nova, nenhuma faixa nova
K_POR_BASE, K_V38 = 40, 8
DIAS, ORCAMENTO_POR_DIA = orq.DIAS, orq.ORCAMENTO_POR_DIA
PREFIXO = orq.PREFIXO
MAX_PROCESSOS = 4                                            # V3-D8
CELULAS = tuple(tuple(c) for c in json.loads((RAIZ / FONTE / "meta.json").read_text(encoding="utf-8"))["celulas"])   # as 12 da run
LUGARES = ("comedouro", "longe_fixo", "longe")
LONGES = ("longe", "longe_fixo")
CONJUNTOS = (("run", "HOJE"), ("run", "OLF-0"), ("v38", "HOJE"))      # a secao 3.1 (RA-2)
PRINCIPAL = ("run", "HOJE")
CORTE_FORA_ALTO, CORTE_FORA_BAIXO = 0.5, 0.25                # RA-5 (SEM FONTE): a L-FORA
CORTE_ETA2 = 0.05                                            # RA-5 (SEM FONTE): a L-ACAO
CORTE_CUSTO_H = 4.0                                          # RA-6: a projecao de parede com 4 processos
CHAVES_CONFIG = {"descricao", "plano", "fase", "unidades", "dias", "orcamento_por_dia"}
FORA_DO_G1 = ("custo", "contrafactual", "se")                # o que a C-G1 nao compara: o relogio e o leitor da SE-C
NOME_VIDA = re.compile(r"^vidas/(run|v38)/[A-Z0-9-]+/[a-z]+_[a-z_]+_\d+\.jsonl$")
RASTRO = {"cfg_rastro": CONFIG_RASTRO_LIGADA}


class RastroDivergiu(RuntimeError):
    pass


# ================================================================== as vidas e a fonte
def lugares_do(grupo: str) -> tuple:
    return LONGES if grupo == "v38" else LUGARES


def vidas_esperadas(unidades: list[dict]) -> list[tuple]:
    """(grupo, braco, dono, lugar, unidade) de cada vida dos tres conjuntos, na ordem fixa"""
    out = []
    for grupo, braco in CONJUNTOS:
        for u in unidades:
            if grupo == "v38" and u["k"] >= K_V38:
                continue
            out += [(grupo, braco, dono, lugar, u) for dono, lugar in CELULAS if lugar in lugares_do(grupo)]
    return out


def nome_da_vida(grupo: str, braco: str, dono: str, lugar: str, semente: int) -> str:
    return f"{grupo}|{braco}|{dono}|{lugar}|{semente}"


def membro_da_vida(grupo: str, braco: str, dono: str, lugar: str, semente: int) -> str:
    return f"vidas/{grupo}/{braco}/{dono}_{lugar}_{semente}.jsonl"


def conferir_fonte(vidas_tar: Path, raiz: Path = RAIZ) -> dict:
    """C-FONTE: o meta.json da run do PV-2 (no git) e os sha256 do `vidas.tar.gz` e do `medidas.json.gz`. Devolve o meta"""
    meta = json.loads((raiz / FONTE / "meta.json").read_text(encoding="utf-8"))
    esperado = meta["artefatos_sha256"]
    for nome, caminho in (("vidas.tar.gz", vidas_tar), ("medidas.json.gz", raiz / FONTE / "medidas.json.gz")):
        if not caminho.is_file():
            raise FileNotFoundError(f"C-FONTE: {caminho} nao existe (a secao 3.2 do plano diz como refazer as vidas)")
        if bv._sha(caminho) != esperado[nome]:
            raise RastroDivergiu(f"C-FONTE: o sha256 de {caminho} nao e o do meta.json da run do PV-2")
    return meta


def ler_gravadas(nomes: set, raiz: Path = RAIZ) -> dict:
    """as medidas gravadas das vidas pedidas, do `medidas.json.gz` da run do PV-2. Falha alto se faltar alguma"""
    with gzip.open(raiz / FONTE / "medidas.json.gz", "rt", encoding="utf-8") as f:
        todas = json.load(f)
    out = {r["vida"]: r for r in todas if r["vida"] in nomes}
    faltam = sorted(nomes - set(out))
    if faltam:
        raise RastroDivergiu(f"{len(faltam)} vidas sem medida gravada na run do PV-2: {faltam[:3]}")
    return out


def extrair(vidas_tar: Path, membros: set, destino: Path) -> None:
    """os logs pedidos, do tar da run para `destino` (so nomes do molde `vidas/<grupo>/<braco>/<dono>_<lugar>_<semente>.jsonl`)"""
    achados = set()
    with tarfile.open(vidas_tar, "r:gz") as tar:
        for m in tar:
            if m.name not in membros:
                continue
            if not m.isfile() or not NOME_VIDA.match(m.name):
                raise RastroDivergiu(f"membro fora do molde no tar das vidas: {m.name!r}")
            alvo = destino / m.name
            alvo.parent.mkdir(parents=True, exist_ok=True)
            alvo.write_bytes(tar.extractfile(m).read())
            achados.add(m.name)
    faltam = sorted(membros - achados)
    if faltam:
        raise RastroDivergiu(f"{len(faltam)} vidas fora do tar da run do PV-2: {faltam[:3]}")


# ================================================================== o replay de uma vida
def conferir_rastro(motivos: list[dict], passo: int) -> None:
    """C-FECHO e C-UMA-VEZ numa vida (falha alto): toda decisao menos a ultima tem o rastro; o intervalo da decisao k vai de k a k+1 e
    acaba no tick da decisao seguinte; por receptor, a leitura da decisao k+1 menos a da decisao k e o delta do mesmo tick mais o do
    intervalo; a soma dos canais do intervalo e o r dele."""
    if len(motivos) < 2:
        raise RastroDivergiu("a vida com menos de duas decisoes nao tem intervalo")
    if "cadeia" in motivos[-1]:
        raise RastroDivergiu("a ultima decisao da vida nao fecha e nao tem rastro")
    sem = [k for k, m in enumerate(motivos[:-1]) if "cadeia" not in m]
    if sem:
        raise RastroDivergiu(f"a decisao {sem[0]} sem o rastro ({len(sem)} ao todo)")
    pares = set()
    for k, m in enumerate(motivos[:-1]):
        c = m["cadeia"]
        inter = c["intervalo"]
        if c["id"] != k or (inter["de"], inter["ate"]) != (k, k + 1) or (k, k + 1) in pares:
            raise RastroDivergiu(f"C-UMA-VEZ: o intervalo da decisao {k} e {inter['de']}..{inter['ate']}")
        pares.add((k, k + 1))
        if inter["tick_de"] is not None and (inter["tick_ate"] is None or inter["tick_ate"] - inter["tick_de"] != passo):
            raise RastroDivergiu(f"C-UMA-VEZ: o intervalo da decisao {k} vai do tick {inter['tick_de']} ao {inter['tick_ate']}")
        if sum(inter["canais"].values()) != inter["r"]:
            raise RastroDivergiu(f"a soma dos canais do intervalo da decisao {k} nao e o r dele")
        if k + 2 < len(motivos):                      # a leitura da decisao k+1 esta no rastro dela
            seg = motivos[k + 1]["cadeia"]
            if inter["tick_ate"] != seg["tick"]:
                raise RastroDivergiu(f"C-UMA-VEZ: o intervalo da decisao {k} acaba no tick {inter['tick_ate']}, e a seguinte e do {seg['tick']}")
            for r, l0 in c["leitura"].items():
                if inter["ja_contado"]:
                    continue
                if seg["leitura"][r] - l0 != c["mesmo_tick"]["delta"][r] + inter["delta"][r]:
                    raise RastroDivergiu(f"C-FECHO: o receptor {r} nao fecha entre as decisoes {k} e {k + 1}")


def rejogar(dias: int, orcamento: int, grupo: str, braco: str, dono: str, lugar: str, unidade: dict, texto: str, gravada: dict,
            so_g1: bool = False) -> dict:
    """uma vida da run do PV-2 rejogada pelo log, com o rastro ligado: a C-G1 contra as medidas gravadas, a C-FECHO, a C-UMA-VEZ e,
    fora do `so_g1`, as medidas do rastro"""
    c0, p0 = time.process_time(), time.perf_counter()
    semente = unidade["semente"]
    vida = nome_da_vida(grupo, braco, dono, lugar, semente)
    fp, fm = pv2.fabricas(braco, dono, semente, dias, orcamento, v38=grupo == "v38", extra_cerebro=RASTRO)
    motor = reproduzir_mundo(LogDeEventos.de_jsonl(texto), fp, semente=semente, fabrica_motor=fm)
    if motor.log.para_jsonl() != texto:
        raise RastroDivergiu(f"C-G1, {vida}: o log rejogado nao e o do disco")
    registro = motor.politica
    c = orq.cerebro_de(registro)
    if not c.rastro:
        raise RastroDivergiu(f"{vida}: o cerebro do replay sem o rastro ligado")
    refeita = json.loads(json.dumps({**orq.medidas(motor, registro, "REL", dias, True),
                                     "pv2": met.medidas_pv2(c.motivos, motor.consumos_mundo, braco != "HOJE", c.S)}))
    diferem = sorted(k for k, v in refeita.items() if k not in FORA_DO_G1 and gravada.get(k) != v)
    if diferem:
        raise RastroDivergiu(f"C-G1, {vida}: as medidas refeitas nao sao as gravadas: {diferem[:5]}")
    conferir_rastro(c.motivos, CONFIG_PADRAO.intervalo_decisao_ticks)
    out = {"vida": vida, "grupo": grupo, "braco": braco, "dono": dono, "lugar": lugar, "semente": semente, "base": unidade["base"],
           "k": unidade["k"]}
    if not so_g1:
        out["rastro"] = met.medidas_rastro(c.motivos)
    out["custo"] = {"vida_cpu": time.process_time() - c0, "vida_parede": time.perf_counter() - p0}
    return out


def _tarefa(dias: int, orcamento: int, vida: tuple, pasta_vidas: str, gravada: dict, so_g1: bool = False) -> dict:
    grupo, braco, dono, lugar, unidade = vida
    texto = (Path(pasta_vidas) / membro_da_vida(grupo, braco, dono, lugar, unidade["semente"])).read_text(encoding="utf-8")
    return rejogar(dias, orcamento, grupo, braco, dono, lugar, unidade, texto, gravada, so_g1)


# ================================================================== a analise (secoes 4 e 5, escritas antes)
def escalares(r: dict) -> dict:
    """as medidas de uma vida como escalares nomeados (None onde a vida nao tem a medida)"""
    out = {"F_sinal": r["fora"]["F_sinal"], "soma_r": r["fora"]["soma_r"], "soma_r_int": r["fora"]["soma_r_int"],
           "eta2_global": r["acao"]["eta2_global"], "eta2_contexto": r["acao"]["eta2_contexto"],
           "media_r_int_n": r["acao"]["media_r_int_n"], "dormir_r_tick_nao_zero": r["acao"]["dormir_r_tick_nao_zero"],
           "dono_fracao_com_gesto": r["dono"]["fracao_com_gesto"], "dono_r_int_n_com": r["dono"]["r_int_n_com"],
           "dono_r_int_n_sem": r["dono"]["r_int_n_sem"], "troca_fracao": r["troca"]["fracao_trocas"],
           "troca_duracao_media": r["troca"]["duracao_media"], "troca_pelo_reflexo": r["troca"]["trocas_pelo_reflexo"],
           "intencoes": r["troca"]["intencoes"]}
    out.update({f"F_receptor:{x}": v["F"] for x, v in r["fora"]["receptores"].items()})
    out.update({f"F_canal:{x}": v["F"] for x, v in r["fora"]["canais"].items()})
    out.update({f"muda_tick:{x}": v["tick"] for x, v in r["muda"].items()})
    out.update({f"muda_intervalo:{x}": v["intervalo"] for x, v in r["muda"].items()})
    out.update({f"media_contexto:{x}": v for x, v in r["acao"]["media_contexto"].items()})
    for b, v in r["acao"]["por_comportamento"].items():
        out.update({f"r_int_n:{b}": v["r_int_n"], f"resto_global:{b}": v["resto_global"], f"resto_contexto:{b}": v["resto_contexto"]})
    out.update({f"duracao:{x}": v for x, v in r["troca"]["duracao"].items()})
    out.update({f"fins:{x}": v for x, v in r["troca"]["fins"].items()})
    out.update({f"gesto_n:{x}": v["n"] for x, v in r["dono"]["por_gesto"].items()})
    out.update({f"gesto_r_int_n:{x}": v["r_int_n"] for x, v in r["dono"]["por_gesto"].items()})
    return out


def _media(xs: list) -> float | None:
    xs = [x for x in xs if x is not None]
    return None if not xs else sum(xs) / len(xs)


def resumo(registros: list[dict], grupo: str, braco: str, lugar: str) -> dict:
    """por medida: a media dos donos por unidade (as vidas sem a medida ficam fora da media da unidade) e o IC95 pelo t sobre as
    unidades; ao lado, a media por dono, sem IC"""
    vidas = [r for r in registros if (r["grupo"], r["braco"], r["lugar"]) == (grupo, braco, lugar)]
    if not vidas:
        raise RastroDivergiu(f"nenhuma vida de {grupo}/{braco}/{lugar}")
    esc = [(r["semente"], r["dono"], escalares(r["rastro"])) for r in vidas]
    nomes = sorted({n for _, _, e in esc for n in e})
    out = {}
    for nome in nomes:
        por_unidade: dict = {}
        por_dono: dict = {}
        for s, d, e in esc:
            por_unidade.setdefault(s, []).append(e.get(nome))
            por_dono.setdefault(d, []).append(e.get(nome))
        medias = [m for m in (_media(v) for _, v in sorted(por_unidade.items())) if m is not None]
        ic = met.ic_t(medias)
        out[nome] = {"n": ic["n"], "media": ic["media"], "dp": ic["dp"], "ic_inferior": ic["ic_inferior"],
                     "ic_superior": ic["ic_superior"], "motivo": ic.get("motivo"),
                     "por_dono": {d: _media(v) for d, v in sorted(por_dono.items())}}
    return {"vidas": len(vidas), "unidades": len({s for s, _, _ in esc}), "medidas": out}


def leitura(resumos: dict) -> dict:
    """a regra da secao 5, escrita antes, no HOJE da run, pelos limites do IC95 nos 3 lugares (os cortes da RA-5, SEM FONTE)"""
    r = {lugar: resumos[f"{PRINCIPAL[0]}|{PRINCIPAL[1]}|{lugar}"]["medidas"] for lugar in LUGARES}

    def lim(nome, lado):
        vals = {lugar: r[lugar][nome][lado] for lugar in LUGARES}
        if any(v is None for v in vals.values()):
            raise RastroDivergiu(f"a regra de leitura sem o IC de {nome}: {vals}")
        return vals
    f_inf, f_sup = lim("F_sinal", "ic_inferior"), lim("F_sinal", "ic_superior")
    if all(v >= CORTE_FORA_ALTO for v in f_inf.values()):
        fora = "a maior parte do sinal esta fora do r"
    elif all(v < CORTE_FORA_BAIXO for v in f_sup.values()):
        fora = "o intervalo e pequeno"
    else:
        fora = "parte do sinal esta fora"
    g_inf, c_inf, c_sup = lim("eta2_global", "ic_inferior"), lim("eta2_contexto", "ic_inferior"), lim("eta2_contexto", "ic_superior")
    n_c = sum(1 for v in c_inf.values() if v > CORTE_ETA2)
    n_g = sum(1 for v in g_inf.values() if v > CORTE_ETA2)
    if n_c >= 2:
        acao = "o intervalo distingue a acao mesmo acordado"
    elif n_g >= 2 and all(v < CORTE_ETA2 for v in c_sup.values()):
        acao = "o sinal do intervalo e o sono, e a linha de base por contexto o apaga"
    elif n_g == 0 and n_c == 0 and all(v < CORTE_ETA2 for v in c_sup.values()) \
            and all(r[lugar]["eta2_global"]["ic_superior"] < CORTE_ETA2 for lugar in LUGARES):
        acao = "o intervalo e decaimento igual para toda acao"
    else:
        acao = "indeterminado"
    return {"L-FORA": {"leitura": fora, "ic_inferior": f_inf, "ic_superior": f_sup,
                       "cortes": {"alto": CORTE_FORA_ALTO, "baixo": CORTE_FORA_BAIXO}},
            "L-ACAO": {"leitura": acao, "eta2_global_inferior": g_inf, "eta2_contexto_inferior": c_inf,
                       "eta2_contexto_superior": c_sup, "corte": CORTE_ETA2},
            "nao_demonstra": ["nada sobre o jogo web nem sobre o v38 alem da checagem descritiva",
                              "nada fora dos 14 dias, do mundo do MVP e dos lugares da C4",
                              "nada sobre o credito: medir que o sinal existe nao mostra que credita-lo ajuda",
                              "nada sobre o efeito do dono: a M-DONO e coincidencia no tempo, nao causa"]}


def analisar(registros: list[dict]) -> dict:
    """os resumos dos tres conjuntos em cada lugar deles (falha alto se faltar algum) e a regra de leitura no HOJE da run"""
    resumos = {f"{g}|{b}|{lugar}": resumo(registros, g, b, lugar) for g, b in CONJUNTOS for lugar in lugares_do(g)}
    return {"resumos": resumos, "leitura": leitura(resumos)}


# ================================================================== a run
def exigir_aprovado(plano: str) -> None:
    linhas = [x for x in plano.splitlines() if x.startswith("**Status:")]
    if not linhas or not linhas[0].startswith(STATUS):
        raise RuntimeError(f"{PLANO} nao esta APROVADO pelo Matheus: {linhas[:1] or 'sem a linha do status'}")


def conferir_config(cfg: dict) -> None:
    faltam, sobram = (CHAVES_CONFIG - {"descricao"}) - set(cfg), set(cfg) - CHAVES_CONFIG
    if faltam or sobram:
        raise ValueError(f"config: faltam {sorted(faltam)}, sobram {sorted(sobram)}")
    u = cfg["unidades"]
    erros = [m for m, ok in ((f"fase {cfg['fase']!r}", cfg["fase"] == FASE), (f"plano {cfg['plano']!r}", cfg["plano"] == PLANO),
                             (f"bases {u.get('bases')}", tuple(u.get("bases", ())) == BASES), (f"K {u.get('k')}", u.get("k") == K_POR_BASE),
                             (f"prefixo {u.get('prefixo')!r}", u.get("prefixo") == PREFIXO), (f"dias {cfg['dias']}", cfg["dias"] == DIAS),
                             (f"orcamento {cfg['orcamento_por_dia']}", cfg["orcamento_por_dia"] == ORCAMENTO_POR_DIA)) if not ok]
    if erros:
        raise ValueError(f"o replay segue o plano a letra (as vidas da run do PV-2): {erros}")


def rodar(cfg: dict, pasta: Path, processos: int, vidas_tar: Path, caminho_config: Path | None = None) -> dict:
    if processos > MAX_PROCESSOS:
        raise ValueError(f"no maximo {MAX_PROCESSOS} processos (V3-D8)")
    conferir_config(cfg)
    exigir_aprovado((RAIZ / PLANO).read_text(encoding="utf-8"))
    if pasta.exists():
        raise FileExistsError(f"{pasta} ja existe: o replay se recusa a gravar por cima (uma vez)")
    fonte = conferir_fonte(vidas_tar)
    unidades = bv.unidades_derivadas(list(BASES), K_POR_BASE, PREFIXO)
    vidas = vidas_esperadas(unidades)
    gravadas = ler_gravadas({nome_da_vida(g, b, d, lugar, u["semente"]) for g, b, d, lugar, u in vidas})
    pasta.mkdir(parents=True)
    inicio = time.time()
    rc = orq.rc
    meta = {"fase": FASE, "plano": PLANO, "plano_sha256": rc._sha_arquivo(RAIZ / PLANO), "config": cfg,
            "config_arquivo": None if caminho_config is None else rc._relativo(caminho_config),
            "config_sha256": None if caminho_config is None else rc._sha_arquivo(caminho_config),
            "comando": " ".join(["python", *sys.argv]) if sys.argv and sys.argv[0] else None, "python": platform.python_version(),
            "orquestrador_sha256": rc._sha_arquivo(Path(__file__)), "pv2_sha256": rc._sha_arquivo(Path(pv2.__file__)),
            "git_head": rc._git("rev-parse", "HEAD"), "git_limpo": rc._git("status", "--porcelain") == "", "processos": processos,
            "conjuntos": [list(c) for c in CONJUNTOS], "celulas": [list(c) for c in CELULAS], "vidas": len(vidas),
            "fonte": {"pasta": FONTE, "vidas_tar": str(vidas_tar), "git_head": fonte["git_head"],
                      "artefatos_sha256": fonte["artefatos_sha256"]},
            "cortes": {"fora_alto": CORTE_FORA_ALTO, "fora_baixo": CORTE_FORA_BAIXO, "eta2": CORTE_ETA2},
            "sha256": {n: rc._sha_arquivo(RAIZ / "digilab" / n) for n in ("config.py", "engine.py", "metrics.py", "mundo.py", "corpo.py")}
            | {f"digibrain/{p.name}": rc._sha_arquivo(p) for p in sorted((RAIZ / "digilab" / "digibrain").glob("*.py"))},
            "inicio": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(inicio))}
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    temp = pasta / "_vidas"
    extrair(vidas_tar, {membro_da_vida(g, b, d, lugar, u["semente"]) for g, b, d, lugar, u in vidas}, temp)
    t0 = time.perf_counter()
    try:
        registros = rc._executar([(_tarefa, (cfg["dias"], cfg["orcamento_por_dia"], v, str(temp),
                                             gravadas[nome_da_vida(v[0], v[1], v[2], v[3], v[4]["semente"])])) for v in vidas], processos)
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


def fumaca_g1(n: int, vidas_tar: Path) -> dict:
    """a fumaca da C-G1 (a secao 3.3): as `n` primeiras vidas do HOJE da run, rejogadas com o rastro ligado; so a conferencia e o
    tempo, nenhuma medida do rastro"""
    conferir_fonte(vidas_tar)
    unidades = bv.unidades_derivadas(list(BASES), K_POR_BASE, PREFIXO)
    vidas = [v for v in vidas_esperadas(unidades) if (v[0], v[1]) == PRINCIPAL][:n]
    gravadas = ler_gravadas({nome_da_vida(g, b, d, lugar, u["semente"]) for g, b, d, lugar, u in vidas})
    custos = []
    with tarfile.open(vidas_tar, "r:gz") as tar:
        textos = {}
        querem = {membro_da_vida(g, b, d, lugar, u["semente"]) for g, b, d, lugar, u in vidas}
        for m in tar:
            if m.name in querem:
                textos[m.name] = tar.extractfile(m).read().decode("utf-8")
                if len(textos) == len(querem):
                    break
    for g, b, d, lugar, u in vidas:
        r = rejogar(DIAS, ORCAMENTO_POR_DIA, g, b, d, lugar, u, textos[membro_da_vida(g, b, d, lugar, u["semente"])],
                    gravadas[nome_da_vida(g, b, d, lugar, u["semente"])], so_g1=True)
        custos.append(r["custo"]["vida_parede"])
    return {"vidas": len(vidas), "c_g1": "passa", "parede_por_vida_s": sum(custos) / len(custos)}


def _vida_de_teste(semente: int, rastro: bool, dias: int, dono: str = "atencioso", lugar: str = "longe_fixo"):
    """uma vida vivida nas sementes dos testes (o HOJE do PV-2), com ou sem o rastro: (o motor, o registro, as fabricas, a parede)"""
    from bancada.regras_mundo import simular_vida_fisico
    from digilab.donos import criar_dono
    from digilab.mundo import DonoComLugar
    fab = pv2.fabricas("HOJE", dono, semente, dias, ORCAMENTO_POR_DIA, extra_cerebro=RASTRO if rastro else None)
    registro = fab[0](CONFIG_PADRAO)
    d = DonoComLugar(criar_dono(dono), lugar, semente, dono, orq.CM)
    t = time.perf_counter()
    motor, _ = simular_vida_fisico(d, registro, semente, dias, ORCAMENTO_POR_DIA * dias, dono, fab[1])
    return motor, registro, fab, time.perf_counter() - t


def medir_custo(sementes: tuple = (101, 202), dias: int = DIAS, rodadas: int = 3) -> dict:
    """M-CUSTO: o tempo de parede por vida nas sementes dos testes, com o rastro ligado e desligado (a vida vivida), alternando os dois
    em `rodadas` e ficando com o menor tempo de cada vida (o menor e o menos sujo pela carga da maquina); e a projecao do replay dos tres
    conjuntos com 4 processos, pelo tempo por vida da fumaca da C-G1 quando ela e dada, ou pelo da vida ligada"""
    tempos: dict = {}
    for _ in range(rodadas):
        for s in sementes:
            for rastro in (False, True):
                motor, registro, _, dt = _vida_de_teste(s, rastro, dias)
                if rastro:
                    t = time.perf_counter()
                    met.medidas_rastro(orq.cerebro_de(registro).motivos)
                    tempos.setdefault((s, "medidas"), []).append(time.perf_counter() - t)
                tempos.setdefault((s, rastro), []).append(dt)
    des = sum(min(tempos[(s, False)]) for s in sementes) / len(sementes)
    lig = sum(min(tempos[(s, True)]) for s in sementes) / len(sementes)
    medidas = sum(min(tempos[(s, "medidas")]) for s in sementes) / len(sementes)
    n = len(vidas_esperadas(bv.unidades_derivadas(list(BASES), K_POR_BASE, PREFIXO)))
    return {"sementes": list(sementes), "dias": dias, "rodadas": rodadas, "desligado_s": des, "ligado_s": lig, "medidas_s": medidas,
            "razao_ligado_desligado": lig / des, "vidas_do_replay": n, "corte_h": CORTE_CUSTO_H}


def _resumo(r: dict) -> str:
    lei = r["leitura"]
    return f"{r['vidas']} vidas; L-FORA: {lei['L-FORA']['leitura']}; L-ACAO: {lei['L-ACAO']['leitura']}"


def main() -> None:
    ap_ = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap_.add_argument("--config", default=None)
    ap_.add_argument("--saida", default=None)
    ap_.add_argument("--vidas", default=str(VIDAS_PADRAO), help="o vidas.tar.gz da run do PV-2")
    ap_.add_argument("--processos", type=int, default=1)
    ap_.add_argument("--g1", type=int, default=None, help="a fumaca da C-G1 em N vidas da run, sem medida do rastro")
    ap_.add_argument("--custo", action="store_true", help="o tempo por vida nas sementes dos testes, ligado e desligado")
    a = ap_.parse_args()
    if a.custo:
        r = medir_custo()
        if a.g1 is not None:                          # com a fumaca: a projecao do replay pelo tempo por vida rejogada da run
            r["fumaca_g1"] = fumaca_g1(a.g1, Path(a.vidas))
            r["projecao_parede_h_4_processos"] = r["vidas_do_replay"] * r["fumaca_g1"]["parede_por_vida_s"] / MAX_PROCESSOS / 3600
        bv._gravar(RAIZ / SAIDA_CUSTO, bv._dump(r))
        print(bv._dump(r))
        return
    if a.g1 is not None:
        print(bv._dump(fumaca_g1(a.g1, Path(a.vidas))))
        return
    if a.config is None:
        raise SystemExit("o replay pede --config (ou --g1 N, ou --custo)")
    caminho = Path(a.config)
    cfg = json.loads(caminho.read_text(encoding="utf-8"))
    conferir_config(cfg)
    pre_run.exigir(ORQUESTRADOR, a.config, a.processos)
    print(_resumo(rodar(cfg, Path(a.saida) if a.saida else RAIZ / SAIDA, a.processos, Path(a.vidas), caminho)["resultado"]))


if __name__ == "__main__":
    main()
