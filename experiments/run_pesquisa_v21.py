"""Pesquisa do combate V2.1 (docs/ESPEC_EVOLUCAO_COMBATE.md, secao Pesquisa).

    python experiments/run_pesquisa_v21.py

Usa as 40 vidas ja gravadas em artifacts_ablacao/vidas (4 donos x {bandit, instinto}
x 5 sementes; mesmas sementes, orcamento e duracao da arena v1) e, sem rodar vida
nova:
  1. evolui cada pet ate a forma adulta (digilab/evolucao.py): ovos pareados
     (especie e temperamento pela semente, iguais entre bracos), cuidado no bebe,
     carater pelo desvio da politica aprendida nas sondas;
  2. distribuicao de linhas e formas adultas por braco (a forma e variavel de resultado);
  3. arena V2.1 so com adultos: dentro de cada semente e politica, todos os pares de
     donos, N partidas por par com lados trocados; gambits canonicos da forma (8 regras
     para todos: capacidade igual entre bracos);
  4. ablacao: a mesma arena com tecnicas e passivas desligadas (separa forma de estilo);
  5. replay de uma amostra de partidas, do disco, bit a bit.
Saida em artifacts_v21_pesquisa/. Codigo de saida 0 (sem gate proprio: o resultado e
descritivo; os numeros sao PROPOSTOS).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
import sys
from collections import Counter
from dataclasses import asdict, replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

from diario import FABRICAS  # noqa: E402
from digilab.combate_v2.v21.bots import ADULTOS  # noqa: E402
from digilab.combate_v2.v21.catalogo import perfil  # noqa: E402
from digilab.combate_v2.v21.gambits import CONDICAO_DO_VIGIA, ListaGambits  # noqa: E402
from digilab.combate_v2.v21.partida import Lutador, jogar, reproduzir  # noqa: E402
from digilab.combate_v2.v21.regras import TECNICAS  # noqa: E402
from digilab.config import (CONFIG_CATALOGO, CONFIG_COMBATE_V2, CONFIG_COMBATE_V21,  # noqa: E402
                            CONFIG_EVOLUCAO_PESQUISA)
from digilab.events import LogDeEventos  # noqa: E402
from digilab.evolucao import evoluir  # noqa: E402
from digilab.metrics import bootstrap_ic  # noqa: E402
from digilab.protocol import ENGINE_SHA256_V0, PROTOCOLO_ARENA_V1, derivar_semente, sha256_engine  # noqa: E402
from digilab.treino import reproduzir_com_feedback  # noqa: E402

VIDAS = RAIZ / "artifacts_ablacao" / "vidas"
SAIDA = RAIZ / "artifacts_v21_pesquisa"
DONOS = PROTOCOLO_ARENA_V1.v("bracos")
POLITICAS = ("bandit", "instinto")


def _dump(o) -> str:
    return json.dumps(o, ensure_ascii=False, indent=2, sort_keys=True)


def lutador(nome: str, ev, ablacao: bool) -> Lutador:
    p = perfil(ev.forma, ev.temperamento, ev.carater_adulto, ev.condicao)
    g = ADULTOS[ev.forma.adulta]
    if ablacao:
        # tecnicas e passivas desligadas: as regras que dependem delas saem da lista
        p = replace(p, tecnica=None, passiva=None)
        regras = tuple(r for r in g.regras if r.acao not in TECNICAS.values()
                       and all(c.nome != CONDICAO_DO_VIGIA for c in r.condicoes))
        g = ListaGambits(regras, g.final, g.estagio)
    return Lutador(nome, p, g, CONFIG_COMBATE_V2.epsilon_bots)


def arena(evos: dict, politica: str, n: int, ablacao: bool, amostra: list | None = None) -> dict:
    """{semente: {(dono_a, dono_b): pontos medios de a}} com lados trocados na metade."""
    saida = {}
    for s in PROTOCOLO_ARENA_V1.v("sementes_coorte"):
        lut = {d: lutador(f"{d}-{politica}@{s}", evos[(d, politica, s)], ablacao) for d in DONOS}
        por_par = {}
        for i, a in enumerate(DONOS):
            for b in DONOS[i + 1:]:
                pts = []
                for k in range(n):
                    sp = derivar_semente("pesquisa-v21", "ablacao" if ablacao else "arena", s, a, b, k)
                    if k < n // 2:
                        p = jogar(lut[a], lut[b], sp)
                        pts.append(p.pontos_a)
                    else:
                        p = jogar(lut[b], lut[a], sp)
                        pts.append(1.0 - p.pontos_a)
                    if amostra is not None and k == 0:
                        amostra.append((s, politica, ablacao, p))
                por_par[f"{a}|{b}"] = sum(pts) / len(pts)
        saida[s] = por_par
    return saida


def resumo_arena(por_semente: dict) -> dict:
    boot = (PROTOCOLO_ARENA_V1.v("bootstrap_reamostragens"), PROTOCOLO_ARENA_V1.v("bootstrap_semente"),
            PROTOCOLO_ARENA_V1.v("nivel_confianca"))
    central = [por_semente[s]["atencioso|aleatorio"] for s in sorted(por_semente)]
    media_braco = {}
    for d in DONOS:
        vals = []
        for pares in por_semente.values():
            for par, v in pares.items():
                a, b = par.split("|")
                if d == a:
                    vals.append(v)
                elif d == b:
                    vals.append(1.0 - v)
        media_braco[d] = sum(vals) / len(vals)
    return {"atencioso_vs_aleatorio": bootstrap_ic(central, *boot), "por_semente": central,
            "media_de_cada_braco_contra_os_outros": media_braco,
            "pares_por_semente": {str(s): v for s, v in por_semente.items()}}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--partidas", type=int, default=100, help="por par por semente (par; lados trocados)")
    a = ap.parse_args(argv)
    if a.partidas % 2:
        raise ValueError("partidas precisa ser par")
    if sha256_engine() != ENGINE_SHA256_V0:
        raise RuntimeError("engine.py alterado")
    SAIDA.mkdir(parents=True, exist_ok=True)

    # 1. evolucao
    evos, formas = {}, []
    for arq in sorted(VIDAS.glob("*@*.jsonl")):
        m = re.fullmatch(r"(.+)-(bandit|instinto)@(\d+)\.jsonl", arq.name)
        dono, pol, s = m.group(1), m.group(2), int(m.group(3))
        log = LogDeEventos.de_jsonl(arq.read_text(encoding="utf-8"))
        saude = reproduzir_com_feedback(log, FABRICAS[pol], semente=s).estado()["saude"]
        ev = evoluir(log, FABRICAS[pol], s, PROTOCOLO_ARENA_V1.v("estados_sonda"),
                     PROTOCOLO_ARENA_V1.v("amostras_por_estado"), PROTOCOLO_ARENA_V1.v("semente_sonda"), saude)
        evos[(dono, pol, s)] = ev
        formas.append({"dono": dono, "politica": pol, "semente": s, **ev.para_dict()})
        print(f"  {dono:10s} {pol:8s} {s}: {ev.forma.rotulo}", flush=True)
    (SAIDA / "formas.json").write_text(_dump(formas), encoding="utf-8", newline="\n")

    # 2. distribuicao
    dist = {pol: {d: {"ramo": dict(Counter(f["forma"]["ramo"] for f in formas if f["dono"] == d and f["politica"] == pol)),
                      "linha": dict(Counter(f["forma"]["linha"] for f in formas if f["dono"] == d and f["politica"] == pol)),
                      "adulta": dict(Counter(f["forma"]["adulta"] for f in formas if f["dono"] == d and f["politica"] == pol)),
                      "cuidado_medio": sum(f["cuidado"] for f in formas if f["dono"] == d and f["politica"] == pol) / 5,
                      "carater_adulto_medio": {e: sum(f["carater_adulto"][e] for f in formas
                                                     if f["dono"] == d and f["politica"] == pol) / 5
                                               for e in CONFIG_CATALOGO.carater}}
                  for d in DONOS} for pol in POLITICAS}
    linhas_iguais = sum(len({evos[(d, "bandit", s)].forma.linha for d in DONOS}) == 1
                        for s in PROTOCOLO_ARENA_V1.v("sementes_coorte"))

    # 3-4. arena e ablacao
    amostra: list = []
    res = {}
    for pol in POLITICAS:
        for abl in (False, True):
            chave = f"{pol}{'_sem_tecnicas_passivas' if abl else ''}"
            print(f"arena {chave} ...", flush=True)
            res[chave] = resumo_arena(arena(evos, pol, a.partidas, abl, amostra))

    # 5. replay da amostra, do disco
    (SAIDA / "amostra_replay.jsonl").write_text("".join(p.para_jsonl() for *_, p in amostra), encoding="utf-8",
                                                newline="\n")
    linhas = (SAIDA / "amostra_replay.jsonl").read_text(encoding="utf-8").splitlines()
    logs, atual = [], []
    for ln in linhas:
        ev = json.loads(ln)
        if ev["tipo"] == "cabecalho" and atual:
            logs.append(atual)
            atual = []
        atual.append(ev)
    logs.append(atual)
    for (s, pol, abl, p), log in zip(amostra, logs):
        da, db = p.nome_a.split("-")[0], p.nome_b.split("-")[0]
        reproduzir(log, lutador(p.nome_a, evos[(da, pol, s)], abl), lutador(p.nome_b, evos[(db, pol, s)], abl))

    fontes = [RAIZ / "digilab" / "evolucao.py"] + sorted((RAIZ / "digilab" / "combate_v2" / "v21").glob("*.py"))
    h = hashlib.sha256()
    for f in fontes:
        h.update(f.name.encode() + b"\0" + f.read_bytes().replace(b"\r\n", b"\n") + b"\0")
    resumo = {
        "descricao": __doc__.splitlines()[0],
        "distribuicao_formas": dist,
        "sementes_com_a_mesma_linha_nos_4_donos_bandit": linhas_iguais,
        "arena": res,
        "replay_amostra_bit_a_bit": len(logs),
        "partidas_por_par_por_semente": a.partidas,
        "config_evolucao": asdict(CONFIG_EVOLUCAO_PESQUISA),
        "config_combate_v21": asdict(CONFIG_COMBATE_V21),
        "fontes_sha256": h.hexdigest(),
        "vidas": "artifacts_ablacao/vidas (protocolo arena-v1-ablacao)",
        "avisos": ["todos os numeros de ConfigEvolucaoPesquisa sao PROPOSTOS",
                   "bateria V2.1 REPROVADA (artifacts_combate_v21/gates.json): a arena herda isso",
                   "interpretacoes em docs/REGISTRO_DESVIOS.md"],
        "ambiente": {"python": platform.python_version(), "plataforma": platform.platform()},
    }
    (SAIDA / "resumo.json").write_text(_dump(resumo), encoding="utf-8", newline="\n")
    print(_dump({k: resumo[k] for k in ("sementes_com_a_mesma_linha_nos_4_donos_bandit", "replay_amostra_bit_a_bit")}))
    for chave, r in res.items():
        ic = r["atencioso_vs_aleatorio"]
        print(f"  {chave:32s} atencioso x aleatorio {ic['media']:.3f} IC95 [{ic['ic_inferior']:.3f}, {ic['ic_superior']:.3f}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
