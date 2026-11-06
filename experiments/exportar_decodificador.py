"""O gabarito do decodificador de conceitos `dec-v1` para a web (docs/TAREFA_V3_CONVERSA_PET.md, DC1; docs/research/ESPEC_DECODIFICADOR_FALA.md).

Vidas curtas do braco REL do modular (as do gabarito da LM0, `exportar_gabarito_digibrain_modular`: lugares `longe_fixo` e `comedouro`, donos
`atencioso` e `relapso`, sementes dos testes 101 e 202, 4 dias), refeitas aqui, mais as seis vidas dos fins `sumiu` e `desistiu` (LM4), lidas do
gabarito delas. Por decisao grava a saida de `decodificar(motivo)` (digilab/digibrain/decodificador.py). O TS (web/app/motor/digibrain/decodificador.ts)
decodifica os MESMOS motivos (que web/app/test/gabaritos/digibrain_modular_*.json.gz ja guardam, conferidos aqui contra a vida refeita) e confere
bit a bit (web/app/test/decodificador.test.ts). Sementes dos testes; nao sao vidas de pesquisa e nenhuma faixa e reservada. Sem rodada com numero.

    python experiments/exportar_decodificador.py        # grava web/app/test/gabaritos/decodificador_python.json.gz
"""
from __future__ import annotations

import gzip
import json
import sys
from dataclasses import asdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import exportar_gabarito_digibrain_modular as lm  # noqa: E402

from digilab.config import CONFIG_DECODIFICADOR  # noqa: E402
from digilab.digibrain.decodificador import CATALOGO, decodificar  # noqa: E402

ARQUIVO = RAIZ / "web" / "app" / "test" / "gabaritos" / "decodificador_python.json.gz"


def _gz(nome: str) -> dict:
    with gzip.open(lm.PASTA / nome, "rt", encoding="utf-8") as f:
        return json.load(f)


def _vida(origem: str, dono: str, lugar: str, semente: int, motivos: list) -> dict:
    return {"origem": origem, "dono": dono, "lugar": lugar, "semente": semente,
            "decisoes": [decodificar(m) for m in motivos]}


def gerar() -> dict:
    vidas = []
    for lugar in lm.LUGARES:
        gab = {(v["dono"], v["semente"]): v for v in _gz(f"{lm.PREFIXO}{lugar}.json.gz")["vidas"]}
        for dono in lm.DONOS:
            for semente in lm.SEMENTES:
                _, cerebro, _ = lm.viver(dono, lugar, semente, gravar=False)
                motivos = [lm.paraj(m) for m in cerebro.motivos]
                if motivos != [d["motivo"] for d in gab[(dono, semente)]["decisoes"]]:
                    raise RuntimeError(f"a vida {lugar}/{dono}/{semente} refeita difere do gabarito da LM0: rode o exportador da LM0 antes")
                vidas.append(_vida(f"{lm.PREFIXO}{lugar}.json.gz", dono, lugar, semente, motivos))
    for v in _gz(lm.ARQUIVO_FINS)["vidas"]:
        vidas.append(_vida(lm.ARQUIVO_FINS, v["dono"], v["lugar"], v["semente"], [d["motivo"] for d in v["decisoes"]]))
    return {"versao": 1, "catalogo": list(CATALOGO), "config": json.loads(json.dumps(asdict(CONFIG_DECODIFICADOR))), "vidas": vidas}


def bytes_do_arquivo(g: dict | None = None) -> bytes:
    texto = json.dumps(g or gerar(), sort_keys=True, separators=(",", ":")) + "\n"
    return gzip.compress(texto.encode("utf-8"), compresslevel=9, mtime=0)


if __name__ == "__main__":
    b = bytes_do_arquivo()
    ARQUIVO.write_bytes(b)
    print(f"{ARQUIVO} ({len(b) / 1024:.0f} KiB)")
