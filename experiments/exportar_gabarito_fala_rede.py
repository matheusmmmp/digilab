"""O gabarito do montador do pedido da voz pela rede (CONVERSA_PET, DC4a; docs/PLANO_ANALISE_V3_CONVERSA_DC4.md, secao 10, item 1).

Vidas curtas do LAB+F da DC3 no comedouro com o dono que atende (`entradas_dc4.viver_semente`, a vida das entradas da DC4), nas sementes dos
testes (101 e 202, os donos atencioso e relapso, 3 dias). Por decisao grava a entrada do montador (o `dec-v2` do `decodificar_v2` e o conteudo
da fala, ou null) e a saida do espelho Python (`montador_voz_rede.conceitos_da_voz`). O TS (`web/app/test/fala_rede_montador.test.ts`) passa as
mesmas entradas pelo `conceitosDaVoz` de `web/app/src/falaRede.ts` (com um motor que so devolve o `dec-v2` e o conteudo) e confere que sai o
mesmo pedido. A paridade do `dec-v2` (decodificador) e a do conteudo da fala (a `fala_unidades`) ja tem os gabaritos delas; aqui e so o
montador. O arquivo traz tambem casos feitos a mao do alvo fora do catalogo (`comida`, `cheiro`) e do `ep<N>`.

Nao sao vidas de pesquisa e nenhuma faixa e reservada.

    python experiments/exportar_gabarito_fala_rede.py        # grava web/app/test/gabaritos/fala_rede_montador.json.gz
"""
from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import entradas_dc4 as en  # noqa: E402
import montador_voz_rede as mv  # noqa: E402

ARQUIVO = RAIZ / "web" / "app" / "test" / "gabaritos" / "fala_rede_montador.json.gz"
VIDAS = (("atencioso", 101), ("relapso", 202))
DIAS = 3


def _a_mao() -> list[dict]:
    """os casos do alvo: o tipo da opcao da fome (fora do catalogo) sai; a classe e o `ep<N>` ficam; o episodio vai como veio"""
    d2 = {"versao": "dec-v2", "k": 7, "intencao": "fome", "conceitos": [
        {"nome": "fome", "valor": 900, "confianca": 700, "alvo": "comida"},
        {"nome": "aversao", "valor": 600, "confianca": 300, "alvo": "bola"},
        {"nome": "curiosidade", "valor": 520, "confianca": 600, "alvo": "cheiro"},
        {"nome": "lembranca", "valor": 800, "confianca": 800, "alvo": "ep12", "episodio": {"acao": "comer", "classe": "racao", "desfecho": "bom"}},
        {"nome": "agitacao", "valor": 10, "confianca": 10, "alvo": "ep1234567"}]}
    return [{"origem": "a_mao", "dec_v2": d2, "conteudo": c, "pedido": mv.conceitos_da_voz(d2, c)} for c in (None, "fome", "higiene", "solidao")]


def gerar() -> dict:
    casos = []
    for i, (dono, semente) in enumerate(VIDAS):
        v = en.viver_semente(i, semente, dono, DIAS, en.dc3.orq.ORCAMENTO_POR_DIA)
        casos += [{"origem": f"{dono}/{semente}", "dec_v2": d["dec_v2"], "conteudo": d["conteudo"], "pedido": d["conceitos"]} for d in v["decisoes"]]
    falas = [c for c in casos if c["conteudo"] is not None]
    if {c["conteudo"] for c in falas} != set(mv.CONTEUDOS_FALA):
        raise RuntimeError("as vidas do gabarito sem falas dos tres conteudos")
    return {"versao": 1, "classes_alvo": list(mv.CLASSES_ALVO), "versao_dec_fala": mv.VERSAO_DEC_FALA, "casos": _a_mao() + casos}


def arquivo() -> bytes:
    texto = json.dumps(gerar(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return gzip.compress(texto.encode("utf-8"), compresslevel=9, mtime=0)


if __name__ == "__main__":
    ARQUIVO.write_bytes(arquivo())
    print("gravado", ARQUIVO, ARQUIVO.stat().st_size, "bytes")
