"""V2, CEREBRO-B: a ligacao do DigiBrain B (digilab/policies/cerebro_b.py) na bancada, SEM mudar experiments/bancada_v2.py (o mesmo
caminho do C, experiments/cerebro_c_bancada.py; docs/TAREFA_V2_CEREBRO_B.md, secao 1).

`BancadaComB` e a `Bancada` com o cerebro "cerebro_b" a mais: a mesma vida, o mesmo motor, a mesma regra do mundo, a mesma fonte do sinal
(`PoliticaDoBraco`), so o cerebro dentro dela muda. O B roda em todos os bracos que aprendem (P1, P2, P2e, P2a, P3) e, com o aprendizado
desligado, no P0 (o instinto byte a byte, o P0 comum aos tres cerebros). Os bracos do N6 e do N7 ficam fora (decisao C-2). A receita para
a bancada e a do C: `CEREBROS` ganha "cerebro_b" e, em `Bancada.politica`, `PoliticaDoBraco(PoliticaCerebroB(cfg, cb_cfg, cb, cf), braco,
self.cfg_consequencia)`. Nada mais muda: o motor, o replay (`rejogar` passa por `politica`) e as medidas leem os ganchos e o estado
interno pelos mesmos nomes.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

import bancada_v2 as bv  # noqa: E402
from digilab.config import CONFIG_CEREBRO_B_APRENDIZ, ConfigCerebroB  # noqa: E402
from digilab.policies.cerebro_b import PoliticaCerebroB  # noqa: E402

CEREBRO_B = "cerebro_b"


@dataclass(frozen=True)
class BancadaComB(bv.Bancada):
    cfg_cerebro_b: ConfigCerebroB = CONFIG_CEREBRO_B_APRENDIZ     # o B dos bracos que aprendem (o P0 desliga o aprendizado)

    def politica(self, espec: bv.EspecVida, cfg=None) -> bv.PoliticaDoBraco:
        if espec.cerebro != CEREBRO_B:
            return super().politica(espec, cfg)
        b = bv.braco_de(espec.braco)
        mundo = bv.mundo_de(espec.mundo)
        if b.memoria is not None or b.pedido:
            raise ValueError(f"braco {b.rotulo}: os blocos N6 e N7 ficam fora da comparacao dos cerebros (decisao C-2)")
        if b.fonte == "informacao" and not mundo.frutas:
            raise ValueError(f"braco {b.rotulo}: a informacao e sobre as frutas; precisa de um mundo das frutas, nao {espec.mundo!r}")
        cfg_b = self.cfg_cerebro_b if b.fonte != "nenhuma" else replace(self.cfg_cerebro_b, aprendizado_ligado=False)
        cb = self.cfg_bola if mundo.bola is not None else None
        cf = self.cfg_frutas if mundo.frutas else None
        return bv.PoliticaDoBraco(PoliticaCerebroB(cfg, cfg_b, cb, cf), b, self.cfg_consequencia)
