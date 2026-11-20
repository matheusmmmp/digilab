"""O risco da S-3 para o v11 (docs/TAREFA_V2_W_PORTE_CEREBRO_A.md, secao 6, a primeira linha; etapa 1): o pet v11 aprende a ficar parado?

Descritivo, NAO e run de pesquisa: sem plano de analise, sem gate e sem faixa reservada; so as sementes dos testes (101...505). Compara,
nas mesmas sementes e donos, o v11 (P1-c-tapa, o cerebro aprendendo pela consequencia no corpo) com o instinto no mesmo corpo
(P0-c-tapa), em vidas de 14 dias com o orcamento da calibracao do corpo (224). A medida: a fracao de cada acao nas decisoes da regra
`tempo_livre`, na vida inteira e no ultimo terco. Se brincar e explorar cairem no v11, a PW-1 volta ao Matheus antes da etapa 4.

    python experiments/medir_v11_parado.py      # grava artifacts_v2_w_porte/medida_parado.json
"""
from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import exportar_gabarito_lobos as G  # noqa: E402

SAIDA = RAIZ / "artifacts_v2_w_porte" / "medida_parado.json"
DIAS, ORCAMENTO = 14, 224
DONOS = ("atencioso", "relapso", "aleatorio", "incoerente")
BRACOS = ("P0-c-tapa", "P1-c-tapa")
ACOES = ("ocioso", "explorar", "brincar", "chamar_atencao")


def fracoes(motivos: list) -> dict:
    livre = [m["acao"] for m in motivos if m["regra"] == "tempo_livre"]
    if not livre:
        raise RuntimeError("vida sem decisao de tempo livre")
    terco = livre[len(livre) * 2 // 3:]
    return {"n": len(livre), "vida": {a: livre.count(a) / len(livre) for a in ACOES},
            "ultimo_terco": {a: terco.count(a) / len(terco) for a in ACOES}}


def main() -> None:
    b = G.bancada_v11(DIAS, ORCAMENTO)
    vidas = []
    for dono in DONOS:
        for s in sorted(bv.SEMENTES_TESTE):
            par = {"dono": dono, "semente": s}
            for br in BRACOS:
                v = b.vida(bv.EspecVida(dono, br, s))
                par[br] = fracoes(v.motor.politica.estado_interno()["motivos"])
            vidas.append(par)
    resumo = {}
    for parte in ("vida", "ultimo_terco"):
        resumo[parte] = {}
        for a in ACOES:
            d = [p["P1-c-tapa"][parte][a] - p["P0-c-tapa"][parte][a] for p in vidas]
            resumo[parte][a] = {"P0": statistics.mean(p["P0-c-tapa"][parte][a] for p in vidas),
                                "P1": statistics.mean(p["P1-c-tapa"][parte][a] for p in vidas),
                                "dif_media": statistics.mean(d), "dif_min": min(d), "dif_max": max(d),
                                "pares_p1_menor": sum(x < 0 for x in d)}
    SAIDA.parent.mkdir(exist_ok=True)
    SAIDA.write_text(json.dumps({"dias": DIAS, "orcamento": ORCAMENTO, "pares": len(vidas), "resumo": resumo, "vidas": vidas},
                                indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    for parte, r in resumo.items():
        print(parte)
        for a, x in r.items():
            print(f"  {a:15s} P0 {x['P0']:.3f}  P1 {x['P1']:.3f}  dif {x['dif_media']:+.3f} [{x['dif_min']:+.3f}; {x['dif_max']:+.3f}]"
                  f"  P1<P0 em {x['pares_p1_menor']}/{len(vidas)}")


if __name__ == "__main__":
    main()
