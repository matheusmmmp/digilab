"""Varredura de calibracao do combate V2 (NAO CANONICA).

So usa as sementes de CALIBRACAO do JSON da bateria; recusa rodar com as de
validacao. Testa variantes de ConfigCombateV2 (dicionarios de substituicao)
e grava (--saida, JSONL) os indicadores dos gates G1, G2, G4 e G5 com N reduzido. Serve para
escolher os numeros; a decisao final e registrada em
experiments/configs/calibracao_combate_v2.json e validada pela bateria.

    python experiments/calibrar_combate_v2.py --config experiments/configs/bateria_calibracao.json \\
        --variantes experiments/configs/calibracao/variantes_combate_v2.json --saida artifacts_combate_v2/calibracao_varredura.jsonl
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from dataclasses import replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import digilab.combate_v2.bots as bots_mod  # noqa: E402
import digilab.combate_v2.gambits as gambits_mod  # noqa: E402
import digilab.combate_v2.lutador as lutador_mod  # noqa: E402
import digilab.combate_v2.partida as partida_mod  # noqa: E402
import digilab.combate_v2.regras as regras_mod  # noqa: E402
from digilab.combate_v2.bots import ADAPTATIVO, FIXOS, ORACULO, TODOS, bot  # noqa: E402
from digilab.combate_v2.gambits import PESADO_AUTOMATICO  # noqa: E402
from digilab.combate_v2.partida import jogar  # noqa: E402
from digilab.config import CONFIG_BATERIA_COMBATE, CONFIG_COMBATE_V2  # noqa: E402
from digilab.metrics import equilibrio_simetrico, matriz_taxas, suporte  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402

MODULOS = (regras_mod, gambits_mod, lutador_mod, partida_mod, bots_mod)


def usar_config(cfg) -> None:
    for m in MODULOS:
        m.CONFIG_COMBATE_V2 = cfg


def avaliar(cfg, sementes, n) -> dict:
    usar_config(cfg)
    bs = {x: bot(x, cfg=cfg) for x in TODOS}
    conf, turnos, lim, dec = [], [], 0, {x: {} for x in TODOS}
    nomes = list(TODOS)
    for i, a in enumerate(nomes):
        for b in nomes[i:]:
            for s in sementes:
                for k in range(n):
                    sp = derivar_semente("calibracao", s, a, b, k)
                    p = jogar(bs[a], bs[b], sp, cfg) if k < n // 2 else jogar(bs[b], bs[a], sp, cfg)
                    pts = p.pontos_a if k < n // 2 else 1 - p.pontos_a
                    conf.append((a, b, pts))
                    turnos.append(p.turnos)
                    lim += p.motivo_fim == "limite"
                    for ev in p.log:
                        if ev["tipo"] == "turno":
                            for ac, mo, dono in ((ev["a"], ev["ma"], p.nome_a), (ev["b"], ev["mb"], p.nome_b)):
                                if mo != PESADO_AUTOMATICO:
                                    dec[dono][ac] = dec[dono].get(ac, 0) + 1
    t = matriz_taxas(conf)
    eq = equilibrio_simetrico(t, list(FIXOS), CONFIG_BATERIA_COMBATE.iteracoes_fictitious_play)
    sup = suporte(eq["estrategia"], CONFIG_BATERIA_COMBATE.peso_minimo_suporte)
    dom = [x for x in FIXOS if all(t[x][y] > 0.5 for y in FIXOS if y != x)]
    cont = {}
    for x in sup:
        for ac, c in dec[x].items():
            cont[ac] = cont.get(ac, 0) + c
    tot = sum(cont.values())
    acoes = [a.value for a in regras_mod.ACOES_ESCOLHIVEIS]
    mortas = [a for a in acoes if cont.get(a, 0) / tot < CONFIG_BATERIA_COMBATE.fracao_min_acao]
    usar_config(CONFIG_COMBATE_V2)
    return {
        "dominantes": dom, "suporte": sup, "estrategia": {k: round(v, 3) for k, v in eq["estrategia"].items()},
        "mediana_turnos": statistics.median(turnos), "fracao_limite": round(lim / len(turnos), 3),
        "acoes_mortas": mortas, "adapt_x_aleat": round(t[ADAPTATIVO]["aleatorio"], 3),
        "oraculo_vs_fixos": round(sum(t[ORACULO][y] for y in FIXOS) / 5, 3),
        "adapt_vs_fixos": round(sum(t[ADAPTATIVO][y] for y in FIXOS) / 5, 3),
        "matriz_fixos": {x: {y: round(t[x][y], 2) for y in FIXOS} for x in FIXOS},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True, type=Path)
    ap.add_argument("--n", type=int, default=40)
    ap.add_argument("--variantes", type=Path, required=True, help="JSON: {nome: {campo: valor}}")
    ap.add_argument("--saida", type=Path, required=True, help="JSONL com uma linha por variante")
    args = ap.parse_args()
    cfg = json.loads(args.config.read_text(encoding="utf-8"))
    if cfg["conjunto"] != "calibracao":
        raise SystemExit("calibracao so roda com conjunto = calibracao")
    sementes = cfg["sementes_calibracao"]
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    with args.saida.open("w", encoding="utf-8", newline="\n") as f:
        for nome, subs in json.loads(args.variantes.read_text(encoding="utf-8")).items():
            r = avaliar(replace(CONFIG_COMBATE_V2, **subs), sementes, args.n)
            linha = {"variante": nome, "subs": subs, "sementes": sementes, "n_por_par_por_semente": args.n, **r}
            f.write(json.dumps(linha, sort_keys=True) + "\n")
            print(nome, "dom", r["dominantes"], "sup", r["suporte"], "med", r["mediana_turnos"],
                  "lim", r["fracao_limite"], "mortas", r["acoes_mortas"])


if __name__ == "__main__":
    main()
