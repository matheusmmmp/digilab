"""V2, CEREBRO-C: a ligacao do DigiBrain C (digilab/policies/cerebro_c.py) na bancada, SEM mudar experiments/bancada_v2.py (a bancada e
do chat D, que liga o cerebro de vez na rodada; docs/TAREFA_V2_CEREBRO_C.md, secao 1).

`BancadaComC` e a `Bancada` com o cerebro "cerebro_c" a mais: a mesma vida, o mesmo motor, a mesma regra do mundo, a mesma fonte do sinal
(`PoliticaDoBraco`), so o cerebro dentro dela muda. E a receita para o chat D:
  - `CEREBROS` ganha "cerebro_c";
  - em `Bancada.politica`, para esse cerebro: `PoliticaDoBraco(PoliticaCerebroC(cfg, cc, cb, cf), braco, self.cfg_consequencia)`, com o
    aprendizado desligado no P0 (fonte "nenhuma"), `cb`/`cf` como nos lobos (o mundo so com a chave dele) e `cc` a ConfigCerebroC do
    ponto calibrado do C;
  - os bracos do N6 e do N7 ficam fora (decisao C-2): o C recusa memoria e pedido.
Nada mais na bancada muda: o motor, o replay (`rejogar` usa `fabrica_politica`, que passa por `politica`) e as medidas leem os ganchos e o
estado interno pelos mesmos nomes.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

import bancada_v2 as bv  # noqa: E402
from digilab.config import CONFIG_CEREBRO_C_APRENDIZ, ConfigCerebroC  # noqa: E402
from digilab.policies.cerebro_c import PoliticaCerebroC  # noqa: E402

CEREBRO_C = "cerebro_c"


@dataclass(frozen=True)
class BancadaComC(bv.Bancada):
    cfg_cerebro_c: ConfigCerebroC = CONFIG_CEREBRO_C_APRENDIZ     # o C dos bracos que aprendem (o P0 desliga o aprendizado)

    def politica(self, espec: bv.EspecVida, cfg=None) -> bv.PoliticaDoBraco:
        if espec.cerebro != CEREBRO_C:
            return super().politica(espec, cfg)
        b = bv.braco_de(espec.braco)
        mundo = bv.mundo_de(espec.mundo)
        if b.memoria is not None or b.pedido:
            raise ValueError(f"braco {b.rotulo}: os blocos N6 e N7 ficam fora da comparacao dos cerebros (decisao C-2)")
        if b.fonte == "informacao" and not mundo.frutas:
            raise ValueError(f"braco {b.rotulo}: a informacao e sobre as frutas; precisa de um mundo das frutas, nao {espec.mundo!r}")
        cc = self.cfg_cerebro_c if b.fonte != "nenhuma" else replace(self.cfg_cerebro_c, aprendizado_ligado=False)
        cb = self.cfg_bola if mundo.bola is not None else None
        cf = self.cfg_frutas if mundo.frutas else None
        return bv.PoliticaDoBraco(PoliticaCerebroC(cfg, cc, cb, cf), b, self.cfg_consequencia)
