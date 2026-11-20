"""O gabarito da leitura do painel DigiBrain para a web (docs/TAREFA_V2_W_PORTE_CEREBRO_A.md, etapa 5).

A leitura (`digilab/painel_digibrain.py`) sobre as decisoes do gabarito dos lobos (web/app/test/gabaritos/lobos_python.json, do
experiments/exportar_gabarito_lobos.py, que o tests/test_gabarito_lobos_web.py confere em dia):
- `decisoes`: a leitura de cada motivo das vidas L0 (sem aprender: o aprendido e null) e das quatro vidas v11;
- `aprendido`: o "o que aprendeu" de cada desvio da secao `vontade` (por decisao e na grade).
O TS (web/app/motor/digibrain.ts) refaz as mesmas contas dos mesmos motivos e confere bit a bit (web/app/test/digibrain.test.ts).

O mapa dos pesos (`mapa_pesos`, `mapa_decisao`) vai num arquivo a parte, `mapa_digibrain_python.json`:
- `pesos`: as arestas do prior do L0 e dos pesos do fim de cada vida v11 (a tabela da decisao e a do corpo);
- `v11`: as arestas acesas de cada decisao das quatro vidas v11.

    python experiments/exportar_gabarito_painel_digibrain.py   # grava painel_digibrain_python.json e mapa_digibrain_python.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import exportar_gabarito_lobos as eg  # noqa: E402

from digilab.config import CONFIG_PADRAO  # noqa: E402
from digilab.painel_digibrain import leitura_aprendido, leitura_decisao, mapa_decisao, mapa_pesos  # noqa: E402
from digilab.policies.lobos import ConfigLobos, PoliticaLobos  # noqa: E402

ARQUIVO = RAIZ / "web" / "app" / "test" / "gabaritos" / "painel_digibrain_python.json"
ARQUIVO_MAPA = RAIZ / "web" / "app" / "test" / "gabaritos" / "mapa_digibrain_python.json"


def receptores_v11() -> list[str]:
    """os receptores novos do cerebro do v11, na ordem de `aprendido_corpo` (a do cerebro, pelo estado interno publico)"""
    b = eg.bancada_v11()
    p = b.politica(bv.EspecVida(eg.VIDAS_V11[0][0], eg.BRACO_V11, eg.VIDAS_V11[0][1]), CONFIG_PADRAO)
    return list(bv.do_braco(p).estado_interno()["corpo"]["receptores_novos"])


def gerar() -> dict:
    g = json.loads(eg.ARQUIVO.read_text(encoding="utf-8"))
    l0 = PoliticaLobos(CONFIG_PADRAO, ConfigLobos())
    interno = l0.estado_interno()
    S, prior_l0 = interno["escala"], interno["pesos_prior"]
    receptores = receptores_v11()

    def decisoes(vida: dict, rec: list[str]) -> list[dict]:
        prior = vida.get("pesos_prior", prior_l0)     # as vidas L0 do gabarito nao guardam o prior: e o mesmo (sem aprender)
        return [leitura_decisao(m, prior[m["regra"]][m["acao"]], S, rec) for m in vida["motivos"]]

    return {
        "versao": 1, "S": S, "receptores": receptores,
        "l0": [{"dono": v["dono"], "semente": v["semente"], "decisoes": decisoes(v, [])} for v in g["l0"]],
        "v11": [{"dono": v["dono"], "semente": v["semente"], "decisoes": decisoes(v, receptores)} for v in g["v11"]],
        "aprendido": [{"dono": v["dono"], "semente": v["semente"],
                       "decisoes": [leitura_aprendido(d["desvio"]) for d in v["decisoes"]],
                       "grade": [leitura_aprendido(d["desvio"]) for d in v["grade"]]} for v in g["vontade"]["vidas"]],
    }


def gerar_mapa() -> dict:
    g = json.loads(eg.ARQUIVO.read_text(encoding="utf-8"))
    interno = PoliticaLobos(CONFIG_PADRAO, ConfigLobos()).estado_interno()
    S, prior_l0 = interno["escala"], interno["pesos_prior"]
    teto = g["config_v11"]["lobos"]["teto"]
    receptores = receptores_v11()

    def zeros(t: dict) -> dict:
        return {r: {a: [0] * len(v) for a, v in acoes.items()} for r, acoes in t.items()}

    return {
        "versao": 1, "S": S, "teto": teto, "receptores": receptores,
        "l0": mapa_pesos(prior_l0, prior_l0, {}, {}, S, teto, []),
        "pesos": [{"dono": v["dono"], "semente": v["semente"],
                   "arestas": mapa_pesos(v["pesos_prior"], v["pesos"], zeros(v["pesos_corpo"]), v["pesos_corpo"], S, teto, receptores)}
                  for v in g["v11"]],
        "v11": [{"dono": v["dono"], "semente": v["semente"],
                 "decisoes": [mapa_decisao(m, v["pesos_prior"][m["regra"]][m["acao"]], S, receptores) for m in v["motivos"]]}
                for v in g["v11"]],
    }


def _gravar(g: dict, arquivo: Path = ARQUIVO) -> None:
    arquivo.write_text(json.dumps(g, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    gm = gerar_mapa()
    _gravar(gm, ARQUIVO_MAPA)
    print(f"{ARQUIVO_MAPA} ({ARQUIVO_MAPA.stat().st_size // 1024} KiB): pesos {[len(v['arestas']) for v in gm['pesos']]}, "
          f"v11 {[len(v['decisoes']) for v in gm['v11']]}")
    g = gerar()
    _gravar(g)
    print(f"{ARQUIVO} ({ARQUIVO.stat().st_size // 1024} KiB): l0 {[len(v['decisoes']) for v in g['l0']]}, "
          f"v11 {[len(v['decisoes']) for v in g['v11']]}")
