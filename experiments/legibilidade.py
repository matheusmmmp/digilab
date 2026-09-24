"""Legibilidade do motivo (Parte A): quanto o pet consegue dizer POR QUE agiu.

    python experiments/legibilidade.py

Vida: as 40 vidas de artifacts_ablacao/vidas (4 donos x {bandit, instinto} x 5
sementes), reprocessadas do log com PoliticaComMotivo (somente leitura).
Combate: o round-robin da bateria canonica do combate V2 regerado com as
mesmas sementes de validacao e a mesma funcao de partidas (_partidas_par).
Saida em artifacts_expressao/: legibilidade.json e diarios/ (um log de cada
braco da ablacao, semente 101; partidas entre bots em cada estagio).
"""

from __future__ import annotations

import hashlib
import json
import platform
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

from diario import FABRICAS, diario_partida, diario_vida, formatar, inferir, ler_partidas  # noqa: E402
from digilab.combate_v2.bots import TODOS, bot  # noqa: E402
from digilab.events import LogDeEventos  # noqa: E402
from digilab.expressao import ESTAGIOS  # noqa: E402
from digilab.motivo import motivos_de_vida  # noqa: E402
from run_bateria_combate import _partidas_par  # noqa: E402

SAIDA = RAIZ / "artifacts_expressao"
VIDAS = RAIZ / "artifacts_ablacao" / "vidas"
CFG_BATERIA = RAIZ / "experiments" / "configs" / "bateria_canonico.json"


def _gravar(caminho: Path, texto: str) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(texto, encoding="utf-8", newline="\n")


def vida() -> dict:
    por_braco: dict[str, dict] = {}
    for arq in sorted(VIDAS.glob("*@*.jsonl")):
        semente, pol = inferir(arq)
        braco = arq.name.split("@")[0]
        log = LogDeEventos.de_jsonl(arq.read_text(encoding="utf-8"))
        _, emb = motivos_de_vida(log, FABRICAS[pol], semente)
        b = por_braco.setdefault(braco, {"politica": pol, "decisoes": 0, "com_fator": 0, "valor_decidiu": 0,
                                         "formula_literal_com_fator": 0, "fatores": Counter(),
                                         "dois_fatores": 0, "com_evento_ref": 0, "sementes": []})
        b["sementes"].append(semente)
        for m, d in zip(emb.motivos, emb.diagnosticos):
            b["decisoes"] += 1
            b["com_fator"] += bool(m.fatores)
            b["dois_fatores"] += len(m.fatores) == 2
            b["com_evento_ref"] += bool(m.evento_ref)
            b["valor_decidiu"] += bool(d["valor_decidiu"])
            b["formula_literal_com_fator"] += d["fator_formula_literal"] is not None
            for f in m.fatores:
                b["fatores"][f] += 1
    saida = {}
    for braco, b in sorted(por_braco.items()):
        n = b["decisoes"]
        saida[braco] = {
            "politica": b["politica"], "sementes": b["sementes"], "decisoes": n,
            "fracao_com_fator": b["com_fator"] / n,
            "fracao_dois_fatores": b["dois_fatores"] / n,
            "fracao_com_evento_ref": b["com_evento_ref"] / n,
            "fracao_valor_decidiu": b["valor_decidiu"] / n if b["politica"] == "bandit" else None,
            "fracao_formula_literal_com_fator": b["formula_literal_com_fator"] / n if b["politica"] == "bandit" else None,
            "fatores_mais_frequentes": [[f, c, c / n] for f, c in b["fatores"].most_common(6)],
        }
    return saida


def combate() -> dict:
    cfg = json.loads(CFG_BATERIA.read_text(encoding="utf-8"))
    sementes, n = cfg["sementes_validacao"], cfg["partidas_por_par_por_semente"]
    bots = {x: bot(x) for x in TODOS}
    cont = {x: Counter() for x in TODOS}
    disparos = {x: Counter() for x in TODOS}
    partidas = 0
    nomes = list(TODOS)
    for i, na in enumerate(nomes):
        for nb in nomes[i:]:
            for _, _, p, _, _ in _partidas_par(bots[na], bots[nb], "rr", sementes, n):
                partidas += 1
                for ev in p.log:
                    if ev["tipo"] != "turno":
                        continue
                    for nome, m in ((p.nome_a, ev["ma"]), (p.nome_b, ev["mb"])):
                        if isinstance(m, int):
                            g = bots[nome].estilo.gambits
                            if m == len(g.regras):
                                cont[nome]["regra_final_sempre"] += 1
                            else:
                                conds = [c for c in g.regras[m].condicoes if c.nome != "sempre"]
                                cont[nome]["regra_com_fator" if conds else "regra_sem_fator"] += 1
                            disparos[nome][m] += 1
                        else:
                            cont[nome][m] += 1
    saida = {}
    for x in TODOS:
        tot = sum(cont[x].values())
        estilo = bots[x].estilo
        info = {"decisoes": tot, "fracoes": {k: v / tot for k, v in sorted(cont[x].items())}}
        if hasattr(estilo, "gambits"):
            g = estilo.gambits
            info["disparos_por_regra"] = {str(i): disparos[x][i] for i in range(len(g.regras) + 1)}
            info["regras_que_nunca_disparam"] = [
                {"indice": i, "regra": (g.regras[i] if i < len(g.regras) else g.final).para_dict()}
                for i in range(len(g.regras) + 1) if disparos[x][i] == 0
            ]
        else:
            info["nota"] = "oraculo: referencia FORA da linguagem de gambits; motivo 'oraculo' nao tem fator"
        saida[x] = info
    return {"partidas": partidas, "sementes_validacao": sementes, "partidas_por_par_por_semente": n, "por_bot": saida}


def diarios() -> list[str]:
    gerados = []
    for arq in sorted(VIDAS.glob("*@101.jsonl")):
        destino = SAIDA / "diarios" / f"vida_{arq.stem}.txt"
        _gravar(destino, formatar(diario_vida(arq)))
        gerados.append(destino.relative_to(SAIDA).as_posix())
    partidas = ler_partidas(RAIZ / "artifacts_combate_v2" / "amostra_replay.jsonl")
    escolhidas = []
    for alvo in (("adaptativo", "agressivo"), ("contragolpe", "oraculo"), ("tartaruga", "atirador")):
        idx = next(i for i, p in enumerate(partidas) if {p[0]["a"], p[0]["b"]} == set(alvo))
        escolhidas.append(idx)
    for idx in escolhidas:
        cab = partidas[idx][0]
        for est in ESTAGIOS:
            destino = SAIDA / "diarios" / f"partida{idx:03d}_{cab['a']}_x_{cab['b']}_{est}.txt"
            _gravar(destino, formatar(diario_partida(partidas[idx], est)))
            gerados.append(destino.relative_to(SAIDA).as_posix())
    return gerados


def main() -> int:
    SAIDA.mkdir(parents=True, exist_ok=True)
    resultado = {
        "descricao": "Legibilidade do motivo (TAREFA_MEMORIA_EXPRESSAO, Parte A). Somente leitura.",
        "aviso": "a bateria do combate V2 esta REPROVADA (G4, G5); a Parte A foi feita mesmo assim por "
                 "decisao do pesquisador (docs/REGISTRO_DESVIOS.md)",
        "vida": vida(),
        "combate": combate(),
        "diarios": diarios(),
        "ambiente": {"python": platform.python_version(), "plataforma": platform.platform()},
    }
    resultado["artefatos_sha256"] = {
        d: hashlib.sha256((SAIDA / d).read_bytes()).hexdigest() for d in resultado["diarios"]
    }
    _gravar(SAIDA / "legibilidade.json", json.dumps(resultado, ensure_ascii=False, indent=2, sort_keys=True))
    for braco, v in resultado["vida"].items():
        print(f"vida {braco:<22} com fator {v['fracao_com_fator']:.3f}")
    for x, c in resultado["combate"]["por_bot"].items():
        print(f"combate {x:<12} {json.dumps({k: round(v, 3) for k, v in c['fracoes'].items()})}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
