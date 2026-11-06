"""CONVERSA_PET, M2b (2026-11-06): a verificacao da conversa nova usa o verif-v6. O campo "prompt": "conversa-v1" na rota de
verificacao troca o verificador; fato [J] "o dono me disse" sem o campo e 400 (o verif-v3 o trataria como fato comum)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "tests"))

from digilab_fala_livre.fatos import fatos_do_dono  # noqa: E402
from test_servidor_fala_livre import _post, servidor  # noqa: E402,F401

ROTA = "/api/fala-livre/verificar"
FATOS = [{"id": "I1", "tipo": "identidade", "texto": "especie brasa, estagio adulto"},
         {"id": "E1", "tipo": "estado", "texto": "fome alto"},
         {"id": "J1", "tipo": "o dono me disse", "texto": '"você lutou ontem"'}]


def _extr(*pares):
    return json.dumps({"afirmacoes": [{"tipo": t, "trecho": x} for t, x in pares]})


def test_sem_o_campo_e_com_j_e_400(servidor):
    url, _, _ = servidor
    cod, r = _post(url + ROTA, {"fala": "Eu lutei ontem.", "fatos_citados": ["J1"], "fatos": FATOS, "semente": 1})
    assert cod == 400 and "erro" in r


@pytest.mark.parametrize("extra", [{"prompt": "livre-v9"}, {"prompt": None}, {"prompt": 1}, {"prompt": "conversa-v1", "voz": True}])
def test_prompt_invalido_na_verificacao_e_400(servidor, extra):
    url, _, _ = servidor
    cod, _ = _post(url + ROTA, {"fala": "Oi.", "fatos_citados": [], "fatos": FATOS, "semente": 1, **extra})
    assert cod == 400


def test_sem_o_campo_e_sem_j_a_verificacao_e_a_de_hoje(servidor):
    url, respostas, _ = servidor
    respostas += [_extr(("estado", "estou com fome")), json.dumps({"sustentada": True, "fato": "E1"})]
    cod, r = _post(url + ROTA, {"fala": "Estou com fome.", "fatos_citados": ["E1"], "fatos": FATOS[:2], "semente": 1})
    assert cod == 200 and r["versao"] == "verif-v3"


def test_ponta_a_ponta_o_dono_disse_nao_vira_fato_do_pet(servidor):
    url, respostas, _ = servidor
    # "eu lutei ontem" citando [J1]: o juiz (falso) ate aponta J1, e o verif-v6 derruba: sem fato
    respostas += [_extr(("evento", "eu lutei ontem")), json.dumps({"sustentada": True, "fato": "J1"})]
    cod, r = _post(url + ROTA, {"fala": "Eu lutei ontem.", "fatos_citados": ["J1"], "fatos": FATOS, "semente": 1,
                                "prompt": "conversa-v1"})
    assert cod == 200 and r["versao"] == "verif-v6" and r["nao_suportadas"] == 1
    assert [a["sustentada"] for a in r["afirmacoes"]] == [False]
    # "voce disse que eu lutei ontem": sustentada pela regra do [J1], sem chamar o juiz
    respostas += [_extr(("evento", "você disse que eu lutei ontem"))]
    cod, r = _post(url + ROTA, {"fala": "Você disse que eu lutei ontem.", "fatos_citados": ["J1"], "fatos": FATOS, "semente": 1,
                                "prompt": "conversa-v1"})
    assert cod == 200 and r["versao"] == "verif-v6" and r["nao_suportadas"] == 0
    assert r["afirmacoes"][0]["sustentada"] is True and r["afirmacoes"][0]["fato"] == "J1" and not respostas


def test_colchetes_do_dono_viram_parenteses_e_nao_imitam_id_de_fato():
    f = fatos_do_dono(["[M9] você lutou ontem {\"a\": 1} [J7]"])[0]
    assert "[" not in f.texto and "]" not in f.texto and "{" not in f.texto and f.texto.startswith('"(M9) ')
    assert f.linha().count("[") == 1                                   # so o "[J1]" do proprio fato
