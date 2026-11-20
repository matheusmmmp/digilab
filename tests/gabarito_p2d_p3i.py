"""Gabarito das vidas de hoje para a P2D-P3I, parte A (docs/TAREFA_V2_P2D_P3I.md, secao 2): gravado com o codigo da main ANTES do modo
"informacao" do julgador da fruta. Com o modo desligado (o julgamento como elogio e bronca, o de hoje), estas vidas tem de sair iguais
depois, byte a byte: a bancada com o K4 (P0 a P3, os tres mundos das frutas, montagem simples e completa) e o simular_vida_frutas com o
julgador fora do orcamento (com e sem o canal da informacao no motor), estado interno da politica e julgamentos incluidos.

    python tests/gabarito_p2d_p3i.py      # grava tests/gabaritos/p2d_p3i_vidas_de_hoje.json (so com o codigo de antes)
"""
from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
from digilab.config import (CONFIG_FRUTAS_LIGADA, CONFIG_INFORMACAO_LIGADA, CONFIG_LOBOS_APRENDIZ,  # noqa: E402
                            ConfigJulgamentoFruta)
from digilab.donos import criar_dono  # noqa: E402
from digilab.frutas import JulgadorFruta, OfertasFrutas, PoliticaInstintoFrutas, fabricas_frutas, simular_vida_frutas  # noqa: E402
from digilab.policies.lobos import PoliticaLobos  # noqa: E402

ARQUIVO = RAIZ / "tests" / "gabaritos" / "p2d_p3i_vidas_de_hoje.json"
SEMENTES_BANCADA = ((101, None), (202, 202))          # so dos testes
SEMENTES = (11, 22, 33)
MUNDOS = ("casado_frutas", "descasado", "mutavel")
BRACOS = ("P0", "P1", "P2", "P3")
DONOS_BANCADA = ("atencioso", "aleatorio")
DONOS = ("atencioso", "relapso", "aleatorio", "incoerente")
CF, CI = CONFIG_FRUTAS_LIGADA, CONFIG_INFORMACAO_LIGADA
CJ_FORA = ConfigJulgamentoFruta(ligada=True, no_orcamento=False)
LOBOS_T3 = bv.cfg_lobos_do_ponto("T3", {"w0_info": 256, "memoria_ganho": 512})
BANCADAS = {"simples": bv.Bancada(4, 64, cfg_lobos=LOBOS_T3, julgamento_fruta=True),
            "completa": bv.Bancada(4, 64, cfg_lobos=LOBOS_T3, julgamento_fruta=True, montagem="completa")}
CEREBROS = {
    "instinto": lambda cfg=None: PoliticaInstintoFrutas(cfg, None, CF),
    "lobos": lambda cfg=None: PoliticaLobos(cfg, replace(CONFIG_LOBOS_APRENDIZ, w0_info=256), None, CF),
}


def _sha(texto: str) -> str:
    return hashlib.sha256(texto.encode()).hexdigest()


def impressao(motor, interacoes: int, julgados=None) -> dict:
    """o que tem de ficar igual: log, estado, estado() do motor, acoes, rngs, frutas, estado interno da politica, a conta do dono e os
    julgamentos"""
    return {
        "log": _sha(motor.log.para_jsonl()),
        "estado": _sha(repr(motor._estado)),
        "estado_motor": _sha(json.dumps(motor.estado(), sort_keys=True, default=repr)),
        "acoes": _sha(repr(motor.acoes_recentes(10**9))),
        "rngs": _sha(repr((motor._rng_politica.getstate(), motor._rng_ambiente.getstate(), motor._rng_fruta.getstate()))),
        "frutas": _sha(json.dumps(motor.resumo_frutas(), sort_keys=True, default=repr)),
        "politica": _sha(json.dumps(motor.politica.estado_interno(), sort_keys=True, default=repr)),
        "interacoes": interacoes,
        "julgados": None if julgados is None else _sha(repr(julgados)),
    }


def vida_frutas(cerebro: str, canal_info: bool, dono: str, s: int):
    """o simular_vida_frutas com o julgador fora do orcamento (o K4 de hoje: elogio e bronca), com ou sem o canal da informacao"""
    kw = {"cfg_informacao": CI} if canal_info else {}
    fp, fm = fabricas_frutas(cfg_frutas=CF, politica_fabrica=CEREBROS[cerebro], cfg_julgamento=CJ_FORA, **kw)
    j = JulgadorFruta.do_genoma(s, CF, CJ_FORA)
    v = simular_vida_frutas(f"{dono}-p3i", criar_dono(dono), fp(), s, 3, 48, fm, OfertasFrutas(CF), rotulo_dono=dono, julgador=j)
    return v, j


def casos():
    for nome_b in BANCADAS:
        for mundo in MUNDOS:
            for braco in BRACOS:
                for dono in DONOS_BANCADA:
                    for s, g in SEMENTES_BANCADA:
                        yield f"bancada|{nome_b}|{mundo}|{braco}|{dono}|{s}", ("bancada", (nome_b, bv.EspecVida(dono, braco, s, g, mundo)))
    for cerebro in CEREBROS:
        for canal in (False, True):
            for dono in DONOS:
                for s in SEMENTES:
                    yield f"frutas|{cerebro}|{'info' if canal else 'sem'}|{dono}|{s}", ("frutas", (cerebro, canal, dono, s))


def vida_de_hoje(tipo, caso) -> dict:
    if tipo == "bancada":
        nome_b, espec = caso
        v = BANCADAS[nome_b].vida(espec)
        return impressao(v.motor, v.interacoes, v.julgamentos)
    v, j = vida_frutas(*caso)
    return impressao(v.motor, v.interacoes, j.julgados)


def gerar() -> dict:
    return {chave: vida_de_hoje(*caso) for chave, caso in casos()}


if __name__ == "__main__":
    g = gerar()
    ARQUIVO.write_text(json.dumps(g, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(f"{len(g)} vidas -> {ARQUIVO}")
