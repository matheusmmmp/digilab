"""O `ganho_conteudo` da DC3a (docs/PLANO_ANALISE_V3_CONVERSA_DC3.md, secao 3.1): o numero que faz a soma das tres unidades de fala no dia 1
do LAB+F ficar perto da do `chamar_atencao` no dia 1 do LAB. So nas sementes dos testes (101 a 505), nunca na faixa 79101...79505; nao e
dado da DC3 (secao 9: nenhuma calibracao e nenhum piloto alem deste numero).

A conta (a leitura da condicao, registrada como D-CP-DC3a-2): as falas do dia 1 (as decisoes de `chamar_atencao`), somadas nas 20 vidas do
cenario da run (os 4 donos com o dono que ignora, o comedouro, as 5 sementes, 14 dias, orcamento 16, pelo `viver` do orquestrador da DC3),
no LAB e no LAB+F com cada ganho da grade (de S/4 a 4S, de S/4 em S/4). O escolhido e o de razao LAB+F / LAB mais perto de 1 (empate: o
menor ganho). Grava `artifacts_v3_conversa_dc3/ganho_conteudo.json`; o numero vai a mao ao `ConfigFalaUnidades` (PROPOSTO, SEM FONTE).

    python experiments/calibrar_ganho_conteudo_dc3.py --processos 4
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v3_conversa_dc3 as dc  # noqa: E402
from digilab.config import CONFIG_DIGIBRAIN_INATOS, ConfigFalaUnidades  # noqa: E402

S = CONFIG_DIGIBRAIN_INATOS.escala
SEMENTES = (101, 202, 303, 404, 505)
GRADE = tuple(i * S // 4 for i in range(1, 17))                       # S/4 a 4S, PROPOSTA, SEM FONTE
DIAS = dc.DIAS
SAIDA = RAIZ / "artifacts_v3_conversa_dc3" / "ganho_conteudo.json"


def falas_do_dia_1(braco: str, ganho: int | None, semente: int, dono: str) -> int:
    """as falas do dia 1 de uma vida (o dono que ignora, 14 dias)"""
    cf = None if ganho is None else ConfigFalaUnidades(ganho_conteudo=ganho)
    _, registro, _, _, _ = dc.viver(braco, dc.IGNORA, dono, semente, DIAS, dc.ORCAMENTO_POR_DIA, cf)
    ms = dc.orq.cerebro_de(registro).motivos[:dc.DECISOES_POR_DIA]
    return sum(1 for m in ms if m["acao"] == dc.FALA)


def calibrar(processos: int) -> dict:
    if not set(SEMENTES) <= bv.SEMENTES_TESTE:                         # pragma: no cover - a regra das sementes
        raise bv.SementeSemPlano("a calibracao do ganho_conteudo so nas sementes dos testes")
    tarefas = [(falas_do_dia_1, (dc.CONTROLE, None, s, d)) for s in SEMENTES for d in dc.DONOS]
    tarefas += [(falas_do_dia_1, (dc.TRATADO, g, s, d)) for g in GRADE for s in SEMENTES for d in dc.DONOS]
    res = dc.orq.rc._executar(tarefas, processos)
    n = len(SEMENTES) * len(dc.DONOS)
    lab = sum(res[:n])
    por_ganho = {}
    for i, g in enumerate(GRADE):
        f = sum(res[n * (i + 1): n * (i + 2)])
        por_ganho[str(g)] = {"falas_dia_1": f, "razao": f / lab if lab else None}
    escolhido = min(GRADE, key=lambda g: (abs(por_ganho[str(g)]["razao"] - 1), g))
    return {"plano": dc.PLANO, "secao": "3.1", "sementes": list(SEMENTES), "donos": list(dc.DONOS), "modo": dc.IGNORA, "lugar": dc.LUGAR,
            "dias": DIAS, "orcamento_por_dia": dc.ORCAMENTO_POR_DIA, "vidas_por_braco": n, "lab_falas_dia_1": lab,
            "grade": list(GRADE), "por_ganho": por_ganho, "escolhido": escolhido,
            "regra": "a razao LAB+F / LAB das falas do dia 1 mais perto de 1; empate: o menor ganho", "status": "PROPOSTO, SEM FONTE"}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--processos", type=int, default=1)
    a = ap.parse_args()
    if a.processos > dc.MAX_PROCESSOS:
        raise SystemExit(f"no maximo {dc.MAX_PROCESSOS} processos (V3-D8)")
    r = calibrar(a.processos)
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(r, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: r[k] for k in ("lab_falas_dia_1", "escolhido")}), SAIDA)


if __name__ == "__main__":
    main()
