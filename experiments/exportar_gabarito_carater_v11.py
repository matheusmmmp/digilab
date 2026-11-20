"""O gabarito do carater dos pets v11 para a web (docs/TAREFA_V2_W_PORTE_CEREBRO_A.md, etapa 4 parte 3; PW-4 opcao (b)).

O carater e o da medida da PW-4 (experiments/medir_carater_v11.py, `carater`), com a escala e o deslocamento proprios do v11 da calibracao
(artifacts_v2_w_porte/carater_v11_calibracao.json, PROPOSTOS): as 32 sondas com os receptores do corpo (a rng `sonda-corpo`), a
distribuicao de acoes do cerebro e a do cerebro recem-nascido (o instinto), por numeros aleatorios comuns, o desvio bruto por eixo, o
carater, a linha e a forma adulta. Nas quatro vidas v11 do gabarito dos lobos (experiments/exportar_gabarito_lobos.py), com o cerebro
rejogado ate o fim da crianca (900 min) e ate o fim do adolescente (1980 min), como `politica_no_tick`.

    python experiments/exportar_gabarito_carater_v11.py      # grava web/app/test/gabaritos/carater_v11_python.json
"""
from __future__ import annotations

import json
import random
import sys
from dataclasses import replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import exportar_gabarito_lobos as eg  # noqa: E402
import medir_carater_v11 as mc  # noqa: E402

from digilab.combate_v2.v21.catalogo import forma_adulta, linha_do_adolescente  # noqa: E402
from digilab.config import CONFIG_PADRAO  # noqa: E402
from digilab.evolucao import politica_no_tick  # noqa: E402
from digilab.metrics import distribuicoes_de_acao, estados_sonda  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402

ARQUIVO = RAIZ / "web" / "app" / "test" / "gabaritos" / "carater_v11_python.json"
CALIBRACAO = RAIZ / "artifacts_v2_w_porte" / "carater_v11_calibracao.json"
MOMENTOS = (("adolescente", mc.T_ADOL), ("adulto", mc.T_ADUL))


def gerar() -> dict:
    if sys.version_info < (3, 12):
        raise RuntimeError("o gabarito do carater precisa do sum() do Python 3.12 ou mais novo (a soma compensada, que o TS porta em somaPy)")
    ccp, _ = mc.constantes_web()
    cal = json.loads(CALIBRACAO.read_text(encoding="utf-8"))
    ccp_v11 = {**ccp, "escala": cal["escala_v11"]}
    desloc = cal["desloc_v11"]
    b = eg.bancada_v11()
    vidas = []
    estados = None
    base_dist = None
    for dono, semente in eg.VIDAS_V11:
        espec = bv.EspecVida(dono, eg.BRACO_V11, semente)
        v = b.vida(espec)
        cc = b.cfg_corpo_de(espec)
        rng = random.Random(derivar_semente("sonda-corpo", ccp["semente"]))
        sondas = [replace(o, corpo=bv.percepcao_da_sonda(o, cc, rng)) for o in estados_sonda(ccp["estados"], ccp["semente"])]
        base = bv.do_braco(b.politica(espec, CONFIG_PADRAO))
        if estados is None:
            estados = sondas
            base_dist = distribuicoes_de_acao(base, sondas, ccp["amostras"], ccp["semente"])
        elif [(o.vetor_estado, o.ticks_desde_cuidado, o.corpo) for o in sondas] != [(o.vetor_estado, o.ticks_desde_cuidado, o.corpo)
                                                                                 for o in estados]:
            raise RuntimeError("as sondas do carater dependem da vida: deveriam ser as mesmas nas quatro")
        momentos = []
        linha = None
        for quando, tick in MOMENTOS:
            pol = bv.do_braco(politica_no_tick(v.motor.log, b.fabrica_politica(espec), semente, tick, b.fabrica_motor(espec)))
            dist = distribuicoes_de_acao(pol, sondas, ccp["amostras"], ccp["semente"])
            car, bruto = mc.carater(pol, base, sondas, ccp_v11, desloc[quando])
            m = {"quando": quando, "tick": tick, "dist": dist, "bruto": bruto, "carater": car}
            if quando == "adolescente":
                linha = linha_do_adolescente(car)
                m["linha"] = linha
            else:
                m["forma"] = forma_adulta(linha, car, mc.CFG_EVO.sparring_simulado)
            momentos.append(m)
        vidas.append({"dono": dono, "semente": semente, "momentos": momentos})
    return {"versao": 1, "escala": cal["escala_v11"], "desloc": desloc, "ccp": ccp,
            "sondas": [{"vetor": list(o.vetor_estado), "ticks_desde_cuidado": o.ticks_desde_cuidado,
                        "corpo": {r: x for r, x in o.corpo.__dict__.items() if x is not None}}
                       for o in estados],
            "dist_base": base_dist, "vidas": vidas}


if __name__ == "__main__":
    g = gerar()
    ARQUIVO.write_text(json.dumps(g, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")
    print(f"{ARQUIVO} ({ARQUIVO.stat().st_size // 1024} KiB)")
    for v in g["vidas"]:
        print(v["dono"], v["semente"], v["momentos"][0]["linha"], v["momentos"][1]["forma"])
