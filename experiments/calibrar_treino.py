"""Calibracao da sobrecarga (TAREFA_TREINO_SOMBRIO, secao 9.4). So ovos de CALIBRACAO.

Com os numeros de docs/pve_treino.json (decai 2/h acordado bem cuidado e 10 por sono completo),
o dono exigente nao chega ao limiar sombrio (60) no inicio do adulto: a sobrecarga do treino
forcado some antes da evolucao. Esta varredura mede, nos ovos de calibracao (nunca os da run),
a fracao de pets sombrios por braco para cada combinacao de decaimento e de sobrecarga por
sessao forcada.

Criterio (fixado ANTES de olhar o resultado): exigente sombrio em >= 60% dos ovos, nenhum outro
braco sombrio. Entre as combinacoes que passam, adota a mais proxima do original (menor soma das
mudancas relativas). Resultado em experiments/configs/calibracao_treino.json.

    python experiments/calibrar_treino.py
"""

from __future__ import annotations

import itertools
import json
import sys
from dataclasses import replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import digilab.treino_vida as tv  # noqa: E402
from digilab.config import CONFIG_TREINO  # noqa: E402
from digilab.evolucao import ovo  # noqa: E402
from digilab.temperamento import sortear  # noqa: E402

OVOS_CALIBRACAO = (3101, 3202, 3303, 3404, 3505)
GRADE = {"decai_sobrecarga_hora_bem_cuidado": (2.0, 1.0, 0.5, 0.25),
         "decai_sobrecarga_sono_completo": (10.0, 5.0, 2.0),
         "sobrecarga_forcar": (15.0, 20.0, 25.0, 30.0)}
FRACAO_EXIGENTE = 0.6


def medir(ct) -> dict:
    saida = {}
    for b in tv.BRACOS_TREINO:
        sombrios, fria, maxs = 0, 0, []
        for s in OVOS_CALIBRACAO:
            esp, _ = ovo(s)
            v = tv.simular_vida_treino(b, s, 14, esp, sortear(s), ct=ct)
            m = v.motor
            sombrios += bool(m.sombria)
            fria += bool(m.fala_fria)
            maxs.append(m.transicoes["adulto"]["sobrecarga"])
        saida[b] = {"sombria": sombrios / len(OVOS_CALIBRACAO), "fala_fria": fria / len(OVOS_CALIBRACAO),
                    "sobrecarga_no_adulto": maxs}
    return saida


def main() -> int:
    linhas = []
    base = {k: getattr(CONFIG_TREINO, k) for k in GRADE}
    for vals in itertools.product(*GRADE.values()):
        mud = dict(zip(GRADE, vals))
        ct = replace(CONFIG_TREINO, **mud)
        tv_ct = ct
        res = medir(tv_ct)
        passa = res["exigente"]["sombria"] >= FRACAO_EXIGENTE and all(
            res[b]["sombria"] == 0 for b in tv.BRACOS_TREINO if b != "exigente")
        distancia = sum(abs(mud[k] - base[k]) / base[k] for k in GRADE)
        linhas.append({"mudancas": mud, "passa": passa, "distancia": distancia, "resultado": res})
        print(f"{mud} passa={passa} exigente={res['exigente']['sombria']:.1f} "
              f"outros={[res[b]['sombria'] for b in tv.BRACOS_TREINO if b != 'exigente']}", flush=True)
    ok = sorted((l for l in linhas if l["passa"]), key=lambda l: l["distancia"])
    escolha = ok[0] if ok else None
    (RAIZ / "experiments" / "configs" / "calibracao_treino.json").write_text(json.dumps({
        "descricao": __doc__.strip().splitlines()[0], "ovos_calibracao": OVOS_CALIBRACAO,
        "criterio": f"exigente sombrio >= {FRACAO_EXIGENTE}; nenhum outro braco sombrio; a mais proxima do original",
        "original": base, "grade": GRADE, "escolha": escolha, "varredura": linhas,
    }, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8", newline="\n")
    print("escolha:", escolha["mudancas"] if escolha else "NENHUMA combinacao passa")
    return 0


if __name__ == "__main__":
    sys.exit(main())
