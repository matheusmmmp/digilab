"""Gate S1 da TAREFA_TREINO_SOMBRIO: as 4 formas sombrias entram na bateria V2.1.

Round-robin das 12 formas adultas (8 normais + 4 sombrias), os dois lados da mesma
especie, sementes de VALIDACAO da bateria V2.1, lados trocados na metade (mesma
funcao de partidas da bateria canonica). Bots: os canonicos das formas normais; as
sombrias lutam com os gambits da forma normal de estilo mais proximo
(bots.GAMBIT_BASE_SOMBRIA) e epsilon minimo 0,2.

  S1  nenhuma forma sombria vence (> 0,5) TODOS os 8 arquetipos normais.
      Relatorio a parte: devastador contra os estilos passivos (espelho, muralha,
      sentinela, vigia).
  E1  (continua valendo) sem forma dominante e suporte do equilibrio >= minimo, agora
      com as 12 formas no pool.

Saida em artifacts_treino/bateria_sombria/. Codigo de saida: 0 se S1 passa, 2 se falha.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

from digilab.combate_v2.v21.bots import FORMAS, SOMBRIOS, lutador_adulto  # noqa: E402
from digilab.combate_v2.v21.regras import Regras  # noqa: E402
from digilab.config import CONFIG_BATERIA_V21, CONFIG_CATALOGO, CONFIG_SOMBRIO  # noqa: E402
from digilab.metrics import equilibrio_simetrico, matriz_taxas, suporte  # noqa: E402
from digilab.protocol import ENGINE_SHA256_V0, sha256_engine  # noqa: E402
from run_bateria_v21 import _dump, _gravar, hashes, partidas_par  # noqa: E402

PASSIVOS = ("espelho", "muralha", "sentinela", "vigia")


def executar(caminho_cfg: Path) -> int:
    cfg = json.loads(caminho_cfg.read_text(encoding="utf-8"))
    for k in ("saida", "sementes", "partidas_por_par_por_semente"):
        if k not in cfg:
            raise KeyError(f"config da bateria sombria sem {k!r}")
    if cfg["partidas_por_par_por_semente"] % 2:
        raise ValueError("partidas por par precisa ser par")
    if sha256_engine() != ENGINE_SHA256_V0:
        raise RuntimeError("engine.py alterado")
    saida = RAIZ / cfg["saida"]
    saida.mkdir(parents=True, exist_ok=True)
    sementes, n = list(cfg["sementes"]), cfg["partidas_por_par_por_semente"]
    especies = list(CONFIG_CATALOGO.especies_ativas)
    todas = tuple(FORMAS) + tuple(SOMBRIOS)
    r = Regras()
    confrontos = []
    for esp in especies:
        print(f"  {esp} ...", flush=True)
        lut = {f: lutador_adulto(f, esp) for f in todas}
        for i, fa in enumerate(todas):
            for fb in todas[i:]:
                for _, _, pts, _ in partidas_par(lut[fa], lut[fb], f"sombria|{esp}", sementes, n, r):
                    confrontos.append((fa, fb, pts))
    taxa = matriz_taxas(confrontos)
    cb = CONFIG_BATERIA_V21

    vence_todos = {s: all(taxa[s][x] > 0.5 for x in FORMAS) for s in SOMBRIOS}
    ok_s1 = not any(vence_todos.values())
    eq = equilibrio_simetrico(taxa, list(todas), cb.iteracoes_fictitious_play)
    sup = suporte(eq["estrategia"], cb.peso_minimo_suporte)
    dominantes = [x for x in todas if all(taxa[x][y] > 0.5 for y in todas if y != x)]
    ok_e1 = not dominantes and len(sup) >= cb.suporte_minimo_e1
    resumo = {
        "S1_ok": ok_s1,
        "S1_vence_todos_os_normais": vence_todos,
        "sombria_x_normais": {s: {x: taxa[s][x] for x in FORMAS} for s in SOMBRIOS},
        "media_sombria_contra_normais": {s: sum(taxa[s][x] for x in FORMAS) / len(FORMAS) for s in SOMBRIOS},
        "media_normal_da_linha_contra_normais": {x: sum(taxa[x][y] for y in FORMAS if y != x) / (len(FORMAS) - 1)
                                                 for x in FORMAS},
        "devastador_x_passivos": {x: taxa["devastador"][x] for x in PASSIVOS},
        "E1_com_sombrias": {"ok": ok_e1, "dominantes": dominantes, "suporte": sup, "estrategia": eq["estrategia"],
                            "suporte_minimo": cb.suporte_minimo_e1},
        "sementes": sementes, "partidas_por_par_por_semente": n, "especies": especies,
        "n_partidas": len(confrontos), "epsilon_minimo_sombria": CONFIG_SOMBRIO.epsilon_minimo,
        "hashes": hashes(cfg),
    }
    _gravar(saida / "matriz.json", _dump({"taxa": taxa, "unidade": "pontos da linha contra a coluna; "
                                                                    "agregado nas especies ativas"}))
    _gravar(saida / "gates.json", _dump(resumo))
    print(f"  [{'ok' if ok_s1 else 'REPROVA'}] S1: sombria que vence todos os normais: "
          f"{[s for s, v in vence_todos.items() if v] or 'nenhuma'}")
    print(f"  [{'ok' if ok_e1 else 'REPROVA'}] E1 com sombrias: dominantes {dominantes}, suporte {sup}")
    print("  devastador x passivos:", {k: round(v, 3) for k, v in resumo["devastador_x_passivos"].items()})
    return 0 if ok_s1 else 2


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=Path, default=RAIZ / "experiments" / "configs" / "bateria_sombria.json")
    sys.exit(executar(ap.parse_args().config))
