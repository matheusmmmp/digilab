"""Filtro do alfabeto no corpus de especies (2026-09-30): traco, jeito de falar e interacao com letra fora do alfabeto
latino ficam fora do bloco de estilo (contados em descartados["NAO LATINO"]); o arquivo e o sha256 nao mudam."""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "tests"))

from digilab_fala_livre import corpus  # noqa: E402
from test_voz_fala_livre import EXEMPLO, _corpus, _esp  # noqa: E402

JP = {"texto": "Pronome おいら; fala casual", "marca": "VERIFICADO", "fonte": "x"}
PT = {"texto": "fala casual e animada", "marca": "VERIFICADO", "fonte": "x"}


def test_latino():
    assert corpus.latino("Olá, você aí! ção") and corpus.latino("1, 2, 3 … !") and not corpus.latino("Pronome おいら")


def test_item_nao_latino_fica_fora_do_estilo_e_e_contado(tmp_path):
    esp, _, _ = corpus.carregar(_corpus(tmp_path, [_esp(fala=[JP, PT], tracos=[JP])]))
    p = esp["Piedmon"]
    assert p.fala == ("fala casual e animada",) and p.tracos == () and p.descartados == {"NAO LATINO": 2}
    assert corpus.latino(corpus.bloco_estilo(p))
    sem, _, _ = corpus.carregar(_corpus(tmp_path, [_esp(fala=[JP, PT], tracos=[JP])]), so_latino=False)
    assert len(sem["Piedmon"].fala) == 2 and not corpus.latino(corpus.bloco_estilo(sem["Piedmon"]))


def test_citacao_pt_nao_latina_tambem_fica_fora(tmp_path):
    c = [{"pt": "ぼく、いいよ！", "original": "o", "fonte": "x", "fan_translation": True, "marca": "VERIFICADO"}]
    esp, _, _ = corpus.carregar(_corpus(tmp_path, [_esp(citacoes=c)]))
    assert esp["Piedmon"].citacoes == () and esp["Piedmon"].descartados == {"NAO LATINO": 1}


def test_corpus_do_jogo_so_manda_latino_ao_prompt_e_o_sha_nao_muda():
    esp, meta, sha = corpus.carregar()
    assert all(corpus.latino(corpus.bloco_estilo(e, None)) for e in esp.values())
    for e in esp.values():
        for com, texto, _ in e.interacoes:
            assert corpus.latino(texto), (e.especie, com)
    fora = sum(e.descartados.get("NAO LATINO", 0) for e in esp.values())
    sem, _, sha2 = corpus.carregar(so_latino=False)
    assert sha == sha2 and fora > 0
    assert sum(len(e.fala) + len(e.tracos) + len(e.interacoes) + len(e.citacoes) for e in sem.values()) == \
        sum(len(e.fala) + len(e.tracos) + len(e.interacoes) + len(e.citacoes) for e in esp.values()) + fora


def test_corpus_de_exemplo_nao_muda():
    """as rodadas 1-4 da voz usaram o corpus de exemplo: nenhum item dele cai no filtro"""
    esp, _, _ = corpus.carregar(EXEMPLO)
    assert all("NAO LATINO" not in e.descartados for e in esp.values())
