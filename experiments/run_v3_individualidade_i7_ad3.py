"""O orquestrador do adendo 3 do I7 da INDIVIDUALIDADE: o que separa absorver de se afastar (docs/PLANO_ANALISE_V3_INDIVIDUALIDADE_I7.md,
secao 16, DECIDIDO pelo Matheus em 2026-11-11, AD3-1 a AD3-6 pela recomendacao). Nenhuma vida nova (AD3-2).

Duas amostras (16.1):
  - a descoberta: as vidas do adendo 2 (`artifacts_v3_individualidade_i7_ad2/`), os ramos E e R, dois conjuntos;
  - a confirmacao: as vidas do I7b (`artifacts_v3_individualidade_i7/` e as vidas do I2), os ramos E.
O grupo de cada ramo (16.2) sai do `perfis.jsonl.gz` gravado, pelo SEQ: "absorve" (D = 0 nos quatro dias da janela), "afasta" (D > 0 nos
quatro), "misto" fora. Os candidatos (16.3) saem do replay do log do original ate o tick do momento (o `reproduzir_mundo` com `ate_tick`,
que para antes do primeiro evento do tick: o estado antes do tapa), so de leitura: a energia, a fome, o humor e a acao em curso.

Duas fases, nesta ordem (16.3 e 16.6):
  1. `--fase candidatos`: le os candidatos das duas amostras, grava o `candidatos.jsonl` e o `niveis.json` (as medianas e a acao mais comum,
     da descoberta) e para. O registro (a secao 17 do plano) recebe os niveis antes da fase 2.
  2. `--fase leitura`: le o `candidatos.jsonl`, confere que os niveis estao no registro, e grava o `analise.json`: o Delta de cada
     candidato com o IC95 do bootstrap sobre as sementes, a leitura da 16.4 e os descritivos da 16.5.

    python experiments/run_v3_individualidade_i7_ad3.py --fase candidatos --processos 4
    python experiments/run_v3_individualidade_i7_ad3.py --fase leitura
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
import run_v3_individualidade_i5 as i5  # noqa: E402
import run_v3_individualidade_i7 as r7  # noqa: E402
import run_v3_individualidade_i7_ad2 as a2  # noqa: E402
from digilab import metrics as M  # noqa: E402
from digilab.mundo import reproduzir_mundo  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402

PLANO = r7.PLANO
MARCA_ADENDO = "**O adendo 3 (seção 16) está DECIDIDO pelo Matheus"
TITULO_REGISTRO = "## 17. O registro do adendo 3"
MARCA_NIVEIS = "- **Os níveis da descoberta"                                  # a linha que a fase 2 exige no registro (16.3)
FASE = "individualidade-i7-ad3"
SAIDA = "artifacts_v3_individualidade_i7_ad3"
DIAS, ORCAMENTO_POR_DIA, IDADES, JANELA = r7.DIAS, r7.ORCAMENTO_POR_DIA, r7.IDADES, r7.JANELA
BOOTSTRAP = 2000
MAX_PROCESSOS = r7.MAX_PROCESSOS
DRIVES = ("energia", "fome", "humor")
CANDIDATOS = ("C-DONO", "C-ENERGIA", "C-FOME", "C-HUMOR", "C-ACAO", "C-IDADE", "C-BRACO")
AMOSTRAS = {   # amostra: (pasta dos perfis e ramos, as vidas, os ramos lidos)
    "descoberta": (Path("artifacts_v3_individualidade_i7_ad2"), Path("artifacts_v3_individualidade_i7_ad2/vidas.tar.gz"), ("E", "R")),
    "confirmacao": (Path("artifacts_v3_individualidade_i7"), Path("artifacts_v3_individualidade/vidas.tar.gz"), ("E",)),
}


# ================================================================== a trava
def exigir_plano(texto: str, fase: str) -> None:
    """o cabecalho APROVADO do I7, o adendo 3 DECIDIDO, a secao 17 (uma vez) e, na fase 2, os niveis no registro"""
    r7.exigir_plano_aprovado(texto)
    linhas = texto.splitlines()
    if not any(x.startswith(MARCA_ADENDO) for x in linhas[:40]):
        raise RuntimeError("o plano do I7 sem o adendo 3 DECIDIDO no cabecalho: nada roda")
    if sum(1 for x in linhas if x.startswith(TITULO_REGISTRO)) != 1:
        raise RuntimeError(f"o plano do I7 sem a secao {TITULO_REGISTRO!r}: nada roda")
    if fase == "leitura":
        secao = texto[texto.index(TITULO_REGISTRO):]
        if MARCA_NIVEIS not in secao:
            raise RuntimeError("o registro do adendo 3 sem os niveis da descoberta (16.3): a leitura nao roda")


# ================================================================== os grupos e os candidatos de um pet
def grupos_do_pet(p: dict, ramos: tuple, idades: tuple = IDADES, janela: int = JANELA, dias: int = DIAS) -> dict:
    """{(ramo, t): {"grupo": "absorve" | "afasta" | "misto" | None, "imediato_zero": bool | None}} pelo SEQ (16.2 e 16.5)"""
    x = a2.distancias_do_pet(p, "SEQ", idades, janela, dias)
    out = {}
    for (b, t), por_dia in x["D"].items():
        if b not in ramos:
            continue
        c = M.trajetoria_janela([por_dia[d] for d in sorted(por_dia)])
        g = {"sempre0": "absorve", "nunca0": "afasta", "misto": "misto", None: None}[c]
        d0 = x["D0"].get((b, t))
        out[(b, t)] = {"grupo": g, "imediato_zero": None if d0 is None else d0 == 0}
    return out


def estado_no_momento(braco: str, dono: str, semente: int, texto: str, momento: int) -> dict:
    """o estado do original no tick do momento, antes do tapa (o replay para antes do primeiro evento do tick)"""
    fp, fm = i5.fabricas_vida(braco, dono, semente, DIAS, ORCAMENTO_POR_DIA)
    m = reproduzir_mundo(orq.LogDeEventos.de_jsonl(texto), fp, semente=semente, fabrica_motor=fm, ate_tick=momento)
    e = m.estado()
    if e["tick"] != momento:
        raise RuntimeError(f"{braco}|{dono}|{semente}: o replay parou no tick {e['tick']}, o momento e {momento}")
    return {**{d: float(e[d]) for d in DRIVES}, "acao": e["acao_atual"]}


def tarefa_pet(amostra: str, braco: str, dono: str, semente: int, texto: str, momentos: dict) -> list[dict]:
    """os candidatos de um pet nos momentos dados ({t: tick}); uma linha por t"""
    return [{"amostra": amostra, "braco": braco, "dono": dono, "semente": semente, "idade": t, "momento": tk,
             **estado_no_momento(braco, dono, semente, texto, tk)} for t, tk in sorted(momentos.items())]


def tarefa(lote: list[tuple]) -> list[dict]:
    return [linha for args in lote for linha in tarefa_pet(*args)]


# ================================================================== a fase 1: os candidatos
def _momentos(ramos_jsonl: Path, ramos: tuple) -> dict:
    """{(braco, dono, semente): {t: momento}} dos ramos perturbados do ramos.jsonl (o momento e o mesmo nos ramos de um t)"""
    out: dict = {}
    for linha in ramos_jsonl.read_text(encoding="utf-8").splitlines():
        r = json.loads(linha)
        if r["ramo"] in ramos and r["idade"] is not None:
            d = out.setdefault((r["braco"], r["dono"], r["semente"]), {})
            if d.setdefault(r["idade"], r["momento"]) != r["momento"]:
                raise RuntimeError(f"{r['braco']}|{r['dono']}|{r['semente']} t={r['idade']}: dois momentos")
    return out


def niveis_da_descoberta(linhas: list[dict], grupos: dict) -> dict:
    """as medianas dos drives e a acao mais comum, sobre os ramos da descoberta com grupo (E e R juntos; 16.3)"""
    vals = {d: [] for d in DRIVES}
    acoes: dict = {}
    for c in linhas:
        if c["amostra"] != "descoberta":
            continue
        for b in AMOSTRAS["descoberta"][2]:
            g = grupos.get(("descoberta", c["braco"], c["dono"], c["semente"], b, c["idade"]))
            if g is None or g["grupo"] not in ("absorve", "afasta"):
                continue
            for d in DRIVES:
                vals[d].append(c[d])
            acoes[c["acao"]] = acoes.get(c["acao"], 0) + 1
    if not acoes:
        raise RuntimeError("a descoberta sem ramos com grupo")
    acao = max(sorted(acoes), key=lambda a: acoes[a])
    return {"medianas": {d: statistics.median(v) for d, v in vals.items()}, "acao_mais_comum": acao, "acoes": acoes}


def ler_grupos(raiz: Path) -> dict:
    """{(amostra, braco, dono, semente, ramo, t): {grupo, imediato_zero}} das duas amostras"""
    out = {}
    for amostra, (pasta, _, ramos) in AMOSTRAS.items():
        pets = r7.ler_perfis(raiz / pasta / "perfis.jsonl.gz")
        for (br, dono, s), p in pets.items():
            for (b, t), g in grupos_do_pet(p, ramos).items():
                out[(amostra, br, dono, s, b, t)] = g
    return out


def fase_candidatos(raiz: Path, pasta: Path, processos: int) -> dict:
    if processos > MAX_PROCESSOS:
        raise ValueError(f"no maximo {MAX_PROCESSOS} processos (V3-D8)")
    if pasta.exists():
        raise FileExistsError(f"{pasta} ja existe: a fase 1 se recusa a gravar por cima")
    pasta.mkdir(parents=True)
    rc = orq.rc
    meta = {"fase": FASE, "plano": PLANO, "plano_sha256": rc._sha_arquivo(RAIZ / PLANO), "orquestrador_sha256": rc._sha_arquivo(Path(__file__)),
            "git_head": rc._git("rev-parse", "HEAD"), "git_limpo": rc._git("status", "--porcelain") == "", "processos": processos,
            "lidos_sha256": {f"{a}/{n}": bv._sha(raiz / p / n) for a, (p, _, _) in AMOSTRAS.items() for n in ("perfis.jsonl.gz", "ramos.jsonl")}
                            | {f"{a}/vidas": bv._sha(raiz / v) for a, (_, v, _) in AMOSTRAS.items()},
            "inicio": time.strftime("%Y-%m-%dT%H:%M:%S")}
    lotes = []
    for amostra, (p, vidas, ramos) in AMOSTRAS.items():
        mom = _momentos(raiz / p / "ramos.jsonl", ramos)
        textos = i5.ler_vidas(raiz / vidas, sorted(mom))
        lotes += [[(amostra, br, dono, s, textos[(br, dono, s)], ts)] for (br, dono, s), ts in sorted(mom.items())]
    t0 = time.perf_counter()
    linhas = [x for r in rc._executar([(tarefa, (lote,)) for lote in lotes], processos) for x in r]
    meta["parede_s"] = time.perf_counter() - t0
    linhas.sort(key=lambda c: (c["amostra"], c["braco"], c["dono"], c["semente"], c["idade"]))
    with (pasta / "candidatos.jsonl").open("w", encoding="utf-8", newline="\n") as f:
        for c in linhas:
            f.write(json.dumps(c, sort_keys=True) + "\n")
    niveis = niveis_da_descoberta(linhas, ler_grupos(raiz))
    bv._gravar(pasta / "niveis.json", bv._dump(niveis))
    meta["fim"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    meta["python"] = platform.python_version()
    meta["artefatos_sha256"] = {n: bv._sha(pasta / n) for n in ("candidatos.jsonl", "niveis.json")}
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    return {"meta": meta, "niveis": niveis, "linhas": len(linhas)}


# ================================================================== a fase 2: a leitura
def nivel(c: dict, cand: str, niveis: dict) -> bool:
    """True = o primeiro nivel do candidato (16.3)"""
    med = niveis["medianas"]
    return {"C-DONO": c["dono"] == "relapso", "C-ENERGIA": c["energia"] < med["energia"], "C-FOME": c["fome"] > med["fome"],
            "C-HUMOR": c["humor"] < med["humor"], "C-ACAO": c["acao"] == niveis["acao_mais_comum"], "C-IDADE": c["idade"] <= 4,
            "C-BRACO": c["braco"] == "REL+F"}[cand]


def registros(candidatos: list[dict], grupos: dict, amostra: str, ramo: str) -> list[dict]:
    """os ramos de um conjunto com grupo absorve ou afasta, cada um com os candidatos do original no momento"""
    out = []
    for c in candidatos:
        if c["amostra"] != amostra:
            continue
        g = grupos.get((amostra, c["braco"], c["dono"], c["semente"], ramo, c["idade"]))
        if g is not None and g["grupo"] in ("absorve", "afasta"):
            out.append({**c, "afasta": g["grupo"] == "afasta", "imediato_zero": g["imediato_zero"]})
    return out


def delta(regs: list[dict], cand: str, niveis: dict) -> float | None:
    """a fracao "se afasta" no primeiro nivel menos a fracao no segundo; None se um nivel fica vazio"""
    a = [r["afasta"] for r in regs if nivel(r, cand, niveis)]
    b = [r["afasta"] for r in regs if not nivel(r, cand, niveis)]
    return None if not a or not b else sum(a) / len(a) - sum(b) / len(b)


def bootstrap_delta(regs: list[dict], cand: str, niveis: dict, rotulo: tuple, boot: int) -> list[float] | None:
    """o IC95 percentil do Delta, reamostrando as sementes com repeticao (os pets de uma semente vao juntos)"""
    por: dict = {}
    for r in regs:
        por.setdefault(r["semente"], []).append(r)
    sementes = sorted(por)
    rng = random.Random(derivar_semente("individualidade-i7-ad3-boot", *rotulo, cand))
    vs = []
    for _ in range(boot):
        amostra = [r for s in (rng.choice(sementes) for _ in sementes) for r in por[s]]
        v = delta(amostra, cand, niveis)
        if v is not None:
            vs.append(v)
    ic = r7._percentis(vs)
    return None if ic is None else list(ic)


def lado(ic) -> int:
    """+1 se o IC95 fica inteiro acima de 0, -1 se inteiro abaixo, 0 fora disso"""
    if ic is None:
        return 0
    return 1 if ic[0] > 0 else (-1 if ic[1] < 0 else 0)


def leitura(ics: dict) -> dict:
    """a frase de cada candidato (16.4); ics = {cand: {"descoberta|E": ic, "descoberta|R": ic, "confirmacao|E": ic}}"""
    out = {}
    for cand, x in ics.items():
        de, dr, ce = lado(x["descoberta|E"]), lado(x["descoberta|R"]), lado(x["confirmacao|E"])
        if cand == "C-DONO":                          # visto na descoberta antes do plano: so a confirmacao (16.4, D-IND-AD3-2)
            out[cand] = "separa" if ce != 0 else "nao separa nesta analise"
        elif de != 0 and de == dr == ce:
            out[cand] = "separa"
        elif de != 0 and de == dr:
            out[cand] = "so na descoberta: nao se confirma nos pets do I7b"
        else:
            out[cand] = "nao separa nesta analise"
    return out


def descritivos(conjuntos: dict, niveis: dict, separam: list[str]) -> dict:
    out: dict = {"cruzada": {}, "imediato": {}, "drives": {}}
    for nome, regs in conjuntos.items():
        for i, a in enumerate(separam):                  # 16.5: a tabela cruzada dos que separam, dois a dois
            for b in separam[i + 1:]:
                cel = {}
                for va in (True, False):
                    for vb in (True, False):
                        sub = [r["afasta"] for r in regs if nivel(r, a, niveis) == va and nivel(r, b, niveis) == vb]
                        cel[f"{a}={va}|{b}={vb}"] = {"n": len(sub), "fracao_afasta": sum(sub) / len(sub) if sub else None}
                out["cruzada"].setdefault(nome, {})[f"{a} x {b}"] = cel
        im = {}
        for z in (True, False):                          # 16.5: o efeito imediato
            sub = [r["afasta"] for r in regs if r["imediato_zero"] is z]
            im["resto do dia t igual" if z else "resto do dia t diferente"] = {"n": len(sub), "fracao_afasta": sum(sub) / len(sub) if sub else None}
        out["imediato"][nome] = im
        dr = {}
        for g in (True, False):                          # 16.5: os drives em nivel
            sub = [r for r in regs if r["afasta"] is g]
            dr["afasta" if g else "absorve"] = {d: ({"media": statistics.fmean(v), "quartis": statistics.quantiles(v, n=4)} if len(v) >= 2 else None)
                                                for d in DRIVES for v in [[r[d] for r in sub]]}
        out["drives"][nome] = dr
    return out


def fase_leitura(raiz: Path, pasta: Path, boot: int = BOOTSTRAP) -> dict:
    if (pasta / "analise.json").exists():
        raise FileExistsError(f"{pasta}/analise.json ja existe: a leitura se recusa a gravar por cima")
    meta = json.loads((pasta / "meta.json").read_text(encoding="utf-8"))
    for n, s in meta["artefatos_sha256"].items():
        if bv._sha(pasta / n) != s:
            raise RuntimeError(f"{n} mudou depois da fase 1")
    candidatos = [json.loads(x) for x in (pasta / "candidatos.jsonl").read_text(encoding="utf-8").splitlines()]
    niveis = json.loads((pasta / "niveis.json").read_text(encoding="utf-8"))
    grupos = ler_grupos(raiz)
    conjuntos = {"descoberta|E": registros(candidatos, grupos, "descoberta", "E"),
                 "descoberta|R": registros(candidatos, grupos, "descoberta", "R"),
                 "confirmacao|E": registros(candidatos, grupos, "confirmacao", "E")}
    pontos = {c: {k: delta(r, c, niveis) for k, r in conjuntos.items()} for c in CANDIDATOS}
    ics = {c: {k: bootstrap_delta(r, c, niveis, tuple(k.split("|")), boot) for k, r in conjuntos.items()} for c in CANDIDATOS}
    le = leitura(ics)
    separam = [c for c in CANDIDATOS if le[c] == "separa"]
    contagens = {k: {"n": len(r), "afasta": sum(x["afasta"] for x in r)} for k, r in conjuntos.items()}
    res = {"fase": FASE, "plano": PLANO, "niveis": niveis, "contagens": contagens, "delta": pontos, "ic95": ics, "leitura": le,
           "descritivos": descritivos(conjuntos, niveis, separam), "bootstrap": boot,
           "multiplicidade": "7 candidatos sem correcao; a repeticao na confirmacao faz o papel (16.4)",
           "leitura_feita": {"orquestrador_sha256": orq.rc._sha_arquivo(Path(__file__)), "git_head": orq.rc._git("rev-parse", "HEAD"),
                             "git_limpo": orq.rc._git("status", "--porcelain") == ""}}
    bv._gravar(pasta / "analise.json", bv._dump(res))
    meta["analise_sha256"] = bv._sha(pasta / "analise.json")
    bv._gravar(pasta / "meta.json", bv._dump(meta))
    return res


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--fase", choices=("candidatos", "leitura"), required=True)
    ap.add_argument("--processos", type=int, default=1)
    ap.add_argument("--raiz", default=None, help="a raiz dos artefatos lidos (a fumaca aponta para outra)")
    ap.add_argument("--saida", default=None)
    a = ap.parse_args()
    raiz = Path(a.raiz) if a.raiz else RAIZ
    fumaca = a.raiz is not None
    if not fumaca:
        exigir_plano((RAIZ / PLANO).read_text(encoding="utf-8"), a.fase)
    elif a.saida is None:
        raise SystemExit("a fumaca precisa de --saida")
    pasta = Path(a.saida) if a.saida else RAIZ / SAIDA
    if a.fase == "candidatos":
        r = fase_candidatos(raiz, pasta, a.processos)
        print(json.dumps({"linhas": r["linhas"], "niveis": r["niveis"], "parede_s": r["meta"]["parede_s"]}, indent=1, ensure_ascii=True))
    else:
        r = fase_leitura(raiz, pasta)
        print(json.dumps({"contagens": r["contagens"], "leitura": r["leitura"]}, indent=1, ensure_ascii=True))


if __name__ == "__main__":
    main()
