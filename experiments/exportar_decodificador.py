"""O gabarito do decodificador de conceitos `dec-v1` para a web (docs/TAREFA_V3_CONVERSA_PET.md, DC1; docs/research/ESPEC_DECODIFICADOR_FALA.md).

DC2b: cada decisao leva tambem o `dec-v2` (o conceito `lembranca` com o `episodio` {acao, classe, desfecho}); o episodio recuperado de cada decisao e
copiado da memoria do cerebro NA hora da lembranca (um gancho de leitura na exportacao: `Memoria.lembrar` embrulhado, que nao muda a vida) e vai no
gabarito (`episodios`, o episodio completo e `fonte`) para o TS decodificar os mesmos episodios.

Vidas curtas do braco REL do modular (as do gabarito da LM0, `exportar_gabarito_digibrain_modular`: lugares `longe_fixo` e `comedouro`, donos
`atencioso` e `relapso`, sementes dos testes 101 e 202, 4 dias), refeitas aqui, mais as seis vidas dos fins `sumiu` e `desistiu` (LM4), lidas do
gabarito delas. Por decisao grava a saida de `decodificar(motivo)` (digilab/digibrain/decodificador.py). O TS (web/app/motor/digibrain/decodificador.ts)
decodifica os MESMOS motivos (que web/app/test/gabaritos/digibrain_modular_*.json.gz ja guardam, conferidos aqui contra a vida refeita) e confere
bit a bit (web/app/test/decodificador.test.ts). Sementes dos testes; nao sao vidas de pesquisa e nenhuma faixa e reservada. Sem rodada com numero.

    python experiments/exportar_decodificador.py        # grava web/app/test/gabaritos/decodificador_python.json.gz
"""
from __future__ import annotations

import copy
import gzip
import json
import sys
from contextlib import contextmanager
from dataclasses import asdict, replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import exportar_gabarito_digibrain_modular as lm  # noqa: E402

from digilab.config import CONFIG_DECODIFICADOR, CONFIG_DIGIBRAIN_INATOS  # noqa: E402
from digilab.digibrain import mem as mem_py  # noqa: E402
from digilab.digibrain.decodificador import CATALOGO, decodificar, decodificar_v2  # noqa: E402

ARQUIVO = RAIZ / "web" / "app" / "test" / "gabaritos" / "decodificador_python.json.gz"


def _gz(nome: str) -> dict:
    with gzip.open(lm.PASTA / nome, "rt", encoding="utf-8") as f:
        return json.load(f)


def _vida(origem: str, dono: str, lugar: str, semente: int, motivos: list, episodios: list) -> dict:
    """`episodios[i]`: o episodio recuperado na decisao i (copia completa) ou None; o `dec-v2` o usa"""
    if len(episodios) != len(motivos):
        raise RuntimeError(f"{origem} {dono}/{lugar}/{semente}: {len(episodios)} lembrancas para {len(motivos)} decisoes")
    return {"origem": origem, "dono": dono, "lugar": lugar, "semente": semente,
            "decisoes": [decodificar(m) for m in motivos], "episodios": episodios,
            "decisoes_v2": [decodificar_v2(m, e) for m, e in zip(motivos, episodios)]}


@contextmanager
def _capturando():
    """embrulha `Memoria.lembrar` (so le) e junta, a cada decisao, o episodio recuperado (copia) ou None"""
    original, juntos = mem_py.Memoria.lembrar, []

    def lembrar(self, sens):
        r = original(self, sens)
        e = None if r["recuperado"] is None else next(x for x in self._guardados() if x["id"] == r["recuperado"])
        juntos.append(None if e is None else json.loads(json.dumps(copy.deepcopy(e))))
        return r
    mem_py.Memoria.lembrar = lembrar
    try:
        yield juntos
    finally:
        mem_py.Memoria.lembrar = original


def _viver_e_capturar(dono: str, lugar: str, semente: int, inatos=None):
    with _capturando() as juntos:
        _, cerebro, _ = lm.viver(dono, lugar, semente, gravar=False, inatos=inatos)
    return [lm.paraj(m) for m in cerebro.motivos], list(juntos)


def gerar() -> dict:
    vidas = []
    for lugar in lm.LUGARES:
        gab = {(v["dono"], v["semente"]): v for v in _gz(f"{lm.PREFIXO}{lugar}.json.gz")["vidas"]}
        for dono in lm.DONOS:
            for semente in lm.SEMENTES:
                motivos, episodios = _viver_e_capturar(dono, lugar, semente)
                if motivos != [d["motivo"] for d in gab[(dono, semente)]["decisoes"]]:
                    raise RuntimeError(f"a vida {lugar}/{dono}/{semente} refeita difere do gabarito da LM0: rode o exportador da LM0 antes")
                vidas.append(_vida(f"{lm.PREFIXO}{lugar}.json.gz", dono, lugar, semente, motivos, episodios))
    for v in _gz(lm.ARQUIVO_FINS)["vidas"]:
        inatos = replace(CONFIG_DIGIBRAIN_INATOS, **v["inatos"]) if v["inatos"] else None
        motivos, episodios = _viver_e_capturar(v["dono"], v["lugar"], v["semente"], inatos)
        if motivos != [d["motivo"] for d in v["decisoes"]]:
            raise RuntimeError(f"a vida dos fins {v['lugar']}/{v['dono']}/{v['semente']} refeita difere do gabarito da LM4")
        vidas.append(_vida(lm.ARQUIVO_FINS, v["dono"], v["lugar"], v["semente"], motivos, episodios))
    return {"versao": 2, "catalogo": list(CATALOGO), "config": json.loads(json.dumps(asdict(CONFIG_DECODIFICADOR))), "vidas": vidas}


def bytes_do_arquivo(g: dict | None = None) -> bytes:
    texto = json.dumps(g or gerar(), sort_keys=True, separators=(",", ":")) + chr(10)
    return gzip.compress(texto.encode("utf-8"), compresslevel=9, mtime=0)


if __name__ == "__main__":
    b = bytes_do_arquivo()
    ARQUIVO.write_bytes(b)
    print(f"{ARQUIVO} ({len(b) / 1024:.0f} KiB)")
