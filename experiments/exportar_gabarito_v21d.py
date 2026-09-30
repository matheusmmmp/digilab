"""Gabarito de paridade Python x web do combate V21D (docs/VALIDACAO_V21D.md): partidas jogadas no Python com as regras
da validacao V21C, sem chave (v21c) e com as quatro chaves da variante a_c_e2v_v (experiments/configs/v21d/validacao.json).

Cada partida grava os dois lutadores (tipo, forma ou linha, especie), o perfil de cada um, os turnos (acao e motivo dos
dois lados), o sha256 dos turnos e o fim (pontos, motivo, vida final). O teste web (web/app/test/paridade_v21d.test.ts)
refaz cada partida no motor em TS: as decisoes por regra, a leitura do vigia e a resolucao sao do TS; so as acoes de
exploracao (epsilon) vem do gabarito, porque a rng do Python (Mersenne) nao e a da web (mulberry32). O sha dos turnos do
TS tem de ser o do Python, e o fim tambem.

Partidas: os 36 pares das 8 formas adultas (com os espelhos) em duas combinacoes de especie, os 4 adolescentes contra as 8
formas adultas e as 4 sombrias contra as 8 formas adultas; as mesmas sementes nas duas variantes.

So le digilab/: nada no pacote muda.

uso: python experiments/exportar_gabarito_v21d.py [saida.json]
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import run_bateria_v21 as rb  # noqa: E402
from digilab.combate_v2.v21 import bots  # noqa: E402
from digilab.combate_v2.v21.bots import FORMAS, SOMBRIOS  # noqa: E402
from digilab.combate_v2.v21.catalogo import LINHA_DA_FORMA, carater_canonico  # noqa: E402
from digilab.combate_v2.v21.partida import jogar  # noqa: E402
from digilab.config import CONFIG_CATALOGO  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402

SAIDA = RAIZ / "web" / "app" / "test" / "gabaritos" / "combate_v21d_python.json"
CFG_V21C = RAIZ / "experiments" / "configs" / "v21c" / "validacao.json"
CFG_V21D = RAIZ / "experiments" / "configs" / "v21d" / "validacao.json"
LINHAS = ("brigao", "guardiao", "cacador", "colosso")
CAMPOS_PERFIL = ("hp_max", "guts_inicial", "guts_max", "regen", "mult_perto", "mult_disparo", "mult_guarda")


def cfg(variante: str) -> dict:
    c = rb.carregar(CFG_V21C)
    if variante == "v21c":
        return c
    d = json.loads(CFG_V21D.read_text(encoding="utf-8"))
    return {**c, "regras_v21": {**c["regras_v21"], **d["regras_v21"]}}


def regras(variante: str):
    return rb.regras_de(cfg(variante))


def lutador(desc: dict, r):
    """desc: {"tipo": "adulto", "forma", "especie"} (normal ou sombria) ou {"tipo": "adolescente", "linha", "especie"}
    (carater canonico da primeira forma adulta da linha, como o E4)"""
    if desc["tipo"] == "adulto":
        return bots.lutador_adulto(desc["forma"], desc["especie"], r.v21, nome=f"{desc['forma']}@{desc['especie']}")
    forma = next(f for f in FORMAS if LINHA_DA_FORMA[f] == desc["linha"])
    return bots.lutador_adolescente(desc["linha"], desc["especie"], carater_canonico(forma, r.v21), r.v21)


def turnos_texto(log) -> str:
    return ";".join(f"{e['a']},{e['ma']},{e['b']},{e['mb']}" for e in log if e["tipo"] == "turno")


def confrontos() -> list[tuple[dict, dict]]:
    esp = list(CONFIG_CATALOGO.especies_ativas)
    out = []
    k = 0
    for i, fa in enumerate(FORMAS):
        for fb in FORMAS[i:]:
            for j in (0, 1):
                out.append(({"tipo": "adulto", "forma": fa, "especie": esp[(k + j) % 4]},
                            {"tipo": "adulto", "forma": fb, "especie": esp[(k + 2 * j + 1) % 4]}))
            k += 1
    for i, linha in enumerate(LINHAS):
        for j, fb in enumerate(FORMAS):
            out.append(({"tipo": "adolescente", "linha": linha, "especie": esp[(i + j) % 4]},
                        {"tipo": "adulto", "forma": fb, "especie": esp[(i + 2 * j) % 4]}))
    for i, s in enumerate(SOMBRIOS):
        for j, fb in enumerate(FORMAS):
            out.append(({"tipo": "adulto", "forma": s, "especie": esp[(i + j + 1) % 4]},
                        {"tipo": "adulto", "forma": fb, "especie": esp[(i + j) % 4]}))
    return out


def gerar() -> dict:
    partidas = []
    for variante in ("v21c", "a_c_e2v_v"):
        r = regras(variante)
        for n, (da, db) in enumerate(confrontos()):
            a, b = lutador(da, r), lutador(db, r)
            semente = derivar_semente("gabarito-v21d", n)
            p = jogar(a, b, semente, r)
            txt = turnos_texto(p.log)
            fim = p.log[-1]
            partidas.append({
                "variante": variante, "n": n, "semente": str(semente), "a": da, "b": db,
                "perfil_a": {k: getattr(a.perfil, k) for k in CAMPOS_PERFIL},
                "perfil_b": {k: getattr(b.perfil, k) for k in CAMPOS_PERFIL},
                "epsilon": [a.epsilon, b.epsilon],
                "turnos": txt, "sha256_turnos": hashlib.sha256(txt.encode("utf-8")).hexdigest(),
                "pontos_a": p.pontos_a, "motivo": p.motivo_fim, "n_turnos": p.turnos,
                "hp_a": fim["hp_a"], "hp_b": fim["hp_b"]})
    d = json.loads(CFG_V21D.read_text(encoding="utf-8"))
    return {"nota": "paridade Python x web do combate V21D (docs/VALIDACAO_V21D.md); gerado por "
                    "experiments/exportar_gabarito_v21d.py. Turnos: 'a,ma,b,mb' separados por ';' (ma/mb: indice da "
                    "regra, 'exploracao' ou 'pesado_automatico')",
            "chaves_v21d": d["regras_v21"], "hashes": {v: rb.hashes(cfg(v)) for v in ("v21c", "a_c_e2v_v")},
            "listas_v21d": {f: bots.gambits_adulto(f, regras("a_c_e2v_v").v21).para_dict() for f in ("muralha", "vigia")},
            "partidas": partidas,
            "resumo": {v: {"partidas": sum(x["variante"] == v for x in partidas),
                           "com_exploracao": sum(x["variante"] == v and "exploracao" in x["turnos"] for x in partidas),
                           "diferentes_da_v21c": None if v == "v21c" else sum(
                               x["sha256_turnos"] != y["sha256_turnos"]
                               for x, y in zip([p for p in partidas if p["variante"] == v],
                                               [p for p in partidas if p["variante"] == "v21c"]))}
                       for v in ("v21c", "a_c_e2v_v")}}


def main() -> int:
    saida = Path(sys.argv[1]) if len(sys.argv) > 1 else SAIDA
    g = gerar()
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text(json.dumps(g, ensure_ascii=False, indent=0) + "\n", encoding="utf-8", newline="\n")
    print(f"{saida}: {len(g['partidas'])} partidas; {g['resumo']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
