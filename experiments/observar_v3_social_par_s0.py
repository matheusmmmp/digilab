"""SOCIAL_PAR S0: a observacao descritiva do que os dois pets fazem juntos, sobre as vidas da run do A0 (sem vida nova).

As vidas nao se guardam inteiras (o event sourcing): a run do A0 guardou, por par, a semente, a perturbacao, as gravacoes de P e o sha256
do registro e das posicoes de cada condicao. Este script refaz a VIVO de cada par com o codigo da run e confere o sha256 contra o
`.json.gz` do par; se um par nao bate, para (nada se le de uma vida que nao e a da run). So leitura: nenhuma medida da run muda, nenhum
numero novo entra em resultado, e nada aqui e teste.

    python experiments/observar_v3_social_par_s0.py --processos 4
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import platform
import subprocess
import sys
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tools"))

import run_v3_social_par_a0 as a0  # noqa: E402
from bancada import parceiro as pc  # noqa: E402
from digilab.config import CONFIG_GRUPO_LIGADA  # noqa: E402
from digilab.grupo import sementes_do_grupo  # noqa: E402
from digilab.mundo import celula_de  # noqa: E402

RUN = RAIZ / "artifacts_v3_social_par_a0" / "run"
SAIDA = RAIZ / "artifacts_v3_social_par_s" / "s0"
PERTO = a0.RAIO_PERTO                       # 6 celulas, o raio perto do A0
CONTATO = a0.RAIO_CONTATO                   # 1 celula
MAX_PROCESSOS = 4
EXEMPLOS = 3                                # quantos exemplos de cada caso raro se guardam por par


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _cheb(pa, pb, cm) -> int:
    (ax, ay), (bx, by) = celula_de(*pa, cm), celula_de(*pb, cm)
    return max(abs(ax - bx), abs(ay - by))


def _dever(motivos: list, passos: list) -> dict:
    """a CO7 de um pet na vida inteira: o que o registro do dever (o `motivos[k]["dever"]`) diz, decisao a decisao"""
    c, ex = Counter(), []
    for k, m in enumerate(motivos):
        d = m.get("dever")
        if d is None:
            continue
        c["com_dever"] += 1
        for chave in ("escudo", "privacao", "unica"):
            c[chave] += bool(d.get(chave))
        for chave in ("culpa", "inveja"):
            c[f"{chave}>0"] += (d.get(chave) or 0) > 0
        for chave in ("removidas", "proibidas", "reprovadas"):
            if d.get(chave):
                c[f"{chave}_nao_vazia"] += 1
                if len(ex) < EXEMPLOS:
                    ex.append({"k": k, "tick": passos[k], "acao": m.get("acao"), chave: d[chave], "culpa": d.get("culpa"),
                               "inveja": d.get("inveja"), "delta": d.get("delta")})
        c["aprovadas>0"] += (d.get("aprovadas") or 0) > 0
    return {"contagem": dict(c), "exemplos": ex}


def observar_par(arquivo: str) -> dict:
    """refaz a VIVO de um par, confere o sha256 e devolve as contagens da observacao (secao 2 da OBSERVACAO_V3_SOCIAL_PAR.md)"""
    with gzip.open(arquivo, "rt", encoding="utf-8") as f:
        disco = json.load(f)
    s, pert = disco["semente"], tuple(disco["perturbacao"])
    ss = sementes_do_grupo(s, CONFIG_GRUPO_LIGADA.ids)
    v = a0._viver(s, [a0._vivo("A", ss), a0._vivo("B", ss)], pert)
    if a0._sha_vida(v) != disco["sha256"]["VIVO"]:
        raise RuntimeError(f"S0: a VIVO do par {disco['par']} nao se refaz com o sha256 da run")
    return observar_vida(v, disco["par"])


def observar_vida(v: pc.VidaPar, nome: str) -> dict:
    """as contagens da observacao de uma vida de par ja vivida (com o t0 feito); o `observar_par` e a SOCIAL_PAR S (o descritivo da
    riqueza) a usam"""
    cm = v.grupo.mundo.cmf
    dec = {i: v.grupo.motores[i].decisoes_mundo for i in "AB"}
    pos = v.posicoes
    n = len(v.passos)
    if any(len(dec[i]) != n or len(pos[i]) != n for i in "AB"):
        raise RuntimeError(f"S0: o par {nome} nao tem uma decisao por passo")
    d = [_cheb(pos["A"][k], pos["B"][k], cm) for k in range(n)]
    acao = {i: [x["acao"] for x in dec[i]] for i in "AB"}
    k0 = pc.indice_do_passo(v, v.t0)

    # 1 e 2: a acao de cada pet pela distancia ao outro no comeco da decisao (o fim do passo anterior); o passo da perturbacao fica fora
    perto = {i: Counter() for i in "AB"}
    longe = {i: Counter() for i in "AB"}
    # 3: a dupla de acoes, perto e em toda a vida (para a esperada pela independencia dentro do par)
    junto, toda = Counter(), Counter()
    for k in range(1, n):
        if k == k0:
            continue
        alvo = perto if d[k - 1] <= PERTO else longe
        for i in "AB":
            alvo[i][acao[i][k]] += 1
        par_ac = f"{acao['A'][k]}|{acao['B'][k]}"
        toda[par_ac] += 1
        if d[k - 1] <= PERTO:
            junto[par_ac] += 1
    # 4: depois de uma aproximacao: o pet X encurta a distancia com o proprio passo (o outro parado na posicao do fim do passo anterior);
    # o que o outro faz na decisao seguinte, contra o que ele faz em toda a vida
    depois = {i: Counter() for i in "AB"}
    for k in range(1, n - 1):
        if k == k0 or k + 1 == k0 or d[k - 1] <= CONTATO:
            continue
        for x, y in (("A", "B"), ("B", "A")):
            if _cheb(pos[x][k], pos[y][k - 1], cm) < d[k - 1]:
                depois[y][acao[y][k + 1]] += 1
    # quem fecha a distancia depois da perturbacao, ate o raio perto (as decisoes da janela em que cada passo encurta)
    fecha = Counter()
    for k in range(k0 + 1, min(n, k0 + a0.JANELA + 1)):
        if d[k - 1] <= PERTO:
            break
        fecha["passos"] += 1
        for x, y in (("A", "B"), ("B", "A")):
            ganho = d[k - 1] - _cheb(pos[x][k], pos[y][k - 1], cm)
            fecha[f"{x}_encurta"] += ganho > 0
            fecha[f"{x}_alonga"] += ganho < 0
            fecha[f"{x}_ganho"] += ganho
    # 6: o mundo comum: as disputas pela comida (a que um comeu e o outro tinha como alvo) e o comer
    disputas = v.grupo.disputas
    comeu = {i: sum(1 for x in dec[i] if x["comeu"]) for i in "AB"}
    comer_junto = sum(1 for k in range(1, n) if acao["A"][k] == acao["B"][k] == "comer" and d[k] <= CONTATO)
    vistos = {i: len(v.grupo.motores[i].vistos_comer) for i in "AB"}
    contatos = Counter(f"{c['tipos'][c['pets'][0]]}|{c['tipos'][c['pets'][1]]}" for c in v.grupo.contatos)
    brincar = {i: sum(1 for a in acao[i] if a == "brincar") for i in "AB"}
    chutes = {i: sum(1 for x in dec[i] if x["brincou_com_bola"]) for i in "AB"}
    # 5: a CO7, nos dois pets
    co7 = {}
    for i in "AB":
        mot = getattr(v.grupo.motores[i].politica, "motivos", None)
        co7[i] = None if mot is None or len(mot) != n else _dever(mot, v.passos)
    hist = Counter(min(x, 30) for x in d)
    return {"par": nome, "n": n, "k0": k0, "acoes": {i: dict(Counter(acao[i])) for i in "AB"},
            "perto": {i: dict(perto[i]) for i in "AB"}, "longe": {i: dict(longe[i]) for i in "AB"},
            "junto": dict(junto), "toda": dict(toda), "depois_da_aproximacao": {i: dict(depois[i]) for i in "AB"},
            "fecha_a_distancia": dict(fecha), "distancia_hist": {str(k): c for k, c in sorted(hist.items())},
            "fracao_perto": sum(1 for x in d if x <= PERTO) / n, "fracao_contato": sum(1 for x in d if x <= CONTATO) / n,
            "disputas": {"n": len(disputas), "exemplos": disputas[:EXEMPLOS]}, "comeu": comeu, "comer_junto_em_contato": comer_junto,
            "vistos_comer": vistos, "contatos": dict(contatos), "brincar": brincar, "chutes": chutes, "co7": co7}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--processos", type=int, default=1)
    a = ap.parse_args()
    if not 1 <= a.processos <= MAX_PROCESSOS:
        raise SystemExit(f"de 1 a {MAX_PROCESSOS} processos (V3-D8)")
    if (SAIDA / "observacao.json").exists():
        raise SystemExit(f"{SAIDA / 'observacao.json'} ja existe: a observacao roda uma vez")
    arquivos = sorted(str(p) for p in (RUN / "vidas").glob("*.json.gz"))
    if len(arquivos) != 210:
        raise SystemExit(f"esperava os 210 pares da run do A0, achei {len(arquivos)}")
    inicio, t = time.strftime("%Y-%m-%dT%H:%M:%S"), time.perf_counter()
    with ProcessPoolExecutor(a.processos) as ex:
        pares = list(ex.map(observar_par, arquivos))
    parede = time.perf_counter() - t
    SAIDA.mkdir(parents=True, exist_ok=True)
    (SAIDA / "observacao.json").write_text(json.dumps({"pares": pares}, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    meta = {"fase": "social_par_s0", "inicio": inicio, "fim": time.strftime("%Y-%m-%dT%H:%M:%S"), "parede_s": parede,
            "comando": " ".join(["python"] + sys.argv), "processos": a.processos, "python": platform.python_version(),
            "git_head": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=RAIZ).stdout.strip(),
            "git_limpo": not subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, cwd=RAIZ).stdout.strip(),
            "fonte": {"run_meta_sha256": _sha(RUN / "meta.json"), "run_medidas_sha256": _sha(RUN / "medidas.json"), "pares": len(arquivos)},
            "script_sha256": _sha(Path(__file__)), "observacao_sha256": _sha(SAIDA / "observacao.json")}
    (SAIDA / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
    print(json.dumps({k: meta[k] for k in ("parede_s", "git_head", "git_limpo", "observacao_sha256")}, indent=1))


if __name__ == "__main__":
    main()
