"""O gabarito da subchave `fala_unidades` para a web (DC3d da CONVERSA_PET, docs/TAREFA_V3_CONVERSA_PET.md, secao DC3d; o plano
docs/PLANO_ANALISE_V3_CONVERSA_DC3.md, 3.1 e o adendo 1, A1.1): vidas curtas no comedouro com o cerebro do laboratorio (o REL da C4, o mesmo do
`exportar_gabarito_digibrain_modular.py`) com a `fala_unidades` ligada (o braco LAB+F da DC3, `run_v3_conversa_dc3.config_do_braco`). O TS
(`web/app/motor/digibrain/`, o espelho da DC3d) rejoga o log de cada vida e confere, decisao a decisao, a acao, o motivo e a assinatura do
estado de cada modulo, e no fim o sha256 do estado interno inteiro do cerebro.

As vidas: os donos `atencioso` e `relapso`, cada um no modo `ignora` (o dono de hoje) e no `atende` (o `DonoQueAtende` da DC3, que cuida do
conteudo de cada fala no mesmo passo, sem rng nova: e ele que faz o credito da fala ate a decisao seguinte, A1.1, ver o cuidado), nas sementes dos
testes (101 a 505), 3 dias. Nao sao vidas de pesquisa e nenhuma faixa e reservada. O arquivo traz tambem as constantes da fala (`CONTEUDOS_FALA`,
`TERMO_DO_CONTEUDO`, a `ConfigFalaUnidades`) e a `ConfigDigibrain` da vida, que o TS confere folha a folha.

    python experiments/exportar_gabarito_fala_unidades.py            # grava web/app/test/gabaritos/digibrain_fala_unidades.json.gz
"""
from __future__ import annotations

import gzip
import hashlib
import sys
from dataclasses import asdict, replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import exportar_gabarito_digibrain_modular as E  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402
import run_v3_conversa_dc3 as dc3  # noqa: E402
from bancada.regras_mundo import simular_vida_fisico  # noqa: E402

from digilab.config import (CONFIG_DIGIBRAIN_INATOS, CONFIG_FALA_UNIDADES, CONFIG_PADRAO, CONTEUDOS_FALA,  # noqa: E402
                            TERMO_DO_CONTEUDO)
from digilab.digibrain.adapt import DigiBrain  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.mundo import DonoComLugar  # noqa: E402

ARQUIVO = E.PASTA / "digibrain_fala_unidades.json.gz"
LUGAR = dc3.LUGAR                                     # o comedouro (DC3-1)
DONOS = ("atencioso", "relapso")
MODOS = dc3.MODOS                                     # ("ignora", "atende")
SEMENTES = (101, 202, 303, 404, 505)                  # as dos testes
DIAS = 3


def config_fala():
    """a ConfigDigibrain da vida: o LAB+F da DC3, que e a do laboratorio (o REL da C4) com a `fala_unidades` ligada e nada mais"""
    cd = dc3.config_do_braco(dc3.TRATADO)
    if cd != replace(E.config_laboratorio(), fala_unidades=True):
        raise RuntimeError("o LAB+F da DC3 nao e o laboratorio do gabarito do modular com a fala_unidades")
    return cd


def viver(dono: str, modo: str, semente: int, gravar: bool = True):
    """a vida: (o motor, o cerebro, o gravador ou None, o dono que atende ou None). O motor e o do `orq.fabricas` (o mesmo do gabarito do modular)"""
    _, fm = orq.fabricas(E.BRACO, dono, semente, DIAS, orq.ORCAMENTO_POR_DIA, conserto=True)
    registro = orq.Registro(DigiBrain(CONFIG_PADRAO, config_fala(), orq.CM, semente=semente), CONFIG_DIGIBRAIN_INATOS.escala)
    cerebro = orq.cerebro_de(registro)
    g = E.Gravador(cerebro) if gravar else None
    try:
        base = criar_dono(dono)
        atende = dc3.DonoQueAtende(base, cerebro.motivos) if modo == dc3.ATENDE else None
        d = DonoComLugar(atende if atende is not None else base, LUGAR, semente, dono, orq.CM)
        motor, _ = simular_vida_fisico(d, registro, semente, DIAS, orq.ORCAMENTO_POR_DIA * DIAS, dono, fm)
    finally:
        if g is not None:
            g.soltar()
    return motor, cerebro, g, atende


def _vida(dono: str, modo: str, semente: int) -> dict:
    motor, cerebro, g, atende = viver(dono, modo, semente)
    ms = cerebro.motivos
    decisoes = [{"k": k, "acao": ms[k]["acao"], "assinatura": g.assinaturas[k], "motivo": E.paraj(ms[k])} for k in range(len(ms))]
    falas = [m["escolha"][1] for m in ms if m["acao"] == dc3.FALA]
    return {"dono": dono, "modo": modo, "lugar": LUGAR, "semente": semente, "dias": DIAS, "decisoes": decisoes,
            "falas": {c: falas.count(c) for c in CONTEUDOS_FALA},
            "atendimentos": None if atende is None else len(atende.atendimentos),
            "log": [ev.para_dict() for ev in motor.log], "log_sha256": hashlib.sha256(motor.log.para_jsonl().encode("utf-8")).hexdigest(),
            "estado": hashlib.sha256(E._texto(E.paraj(cerebro.estado_interno())).encode("utf-8")).hexdigest(),
            "assinatura_final": g.assinar()}


def gerar() -> dict:
    vidas = [_vida(d, mo, s) for d in DONOS for mo in MODOS for s in SEMENTES]
    for v in vidas:
        if None in v["falas"] or sum(v["falas"].values()) == 0:
            raise RuntimeError(f"a vida {v['dono']}/{v['modo']}/{v['semente']} nao falou com conteudo")
    return {"versao": 1, "braco": dc3.TRATADO, "config_digibrain": asdict(config_fala()),
            "conteudos_fala": list(CONTEUDOS_FALA), "termo_do_conteudo": [list(t) for t in TERMO_DO_CONTEUDO],
            "config_fala_unidades": asdict(CONFIG_FALA_UNIDADES), "vidas": vidas}


def texto() -> bytes:
    return E.texto_do_arquivo(gerar()).encode("utf-8")


def arquivo(bruto: bytes | None = None) -> bytes:
    """o gz (mtime 0, nivel 9) do texto"""
    return gzip.compress(texto() if bruto is None else bruto, compresslevel=9, mtime=0)


if __name__ == "__main__":
    ARQUIVO.write_bytes(arquivo())
    print("gravado", ARQUIVO, ARQUIVO.stat().st_size, "bytes")
