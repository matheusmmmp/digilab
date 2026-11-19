"""CONVERSA_PET, F2, D-ES-4 (a saida (0), Matheus, 2026-11-18): `verificar_na_chamada: false` no pedido da voz pela rede devolve a fala sem a
verificacao dentro da chamada. Sem o campo, a resposta e a de hoje (a DC4 e a DC5 nao o mandam). Cliente falso, sem chamada paga."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "tests"))

from test_dc2b import ROTA, dec2, extr, lemb, pedido  # noqa: E402
from test_servidor_fala_livre import _post, servidor  # noqa: E402,F401

FALA = '{"fala": "Lembro que comi ração e foi bom!", "fatos_citados": ["C1"]}'


def test_sem_o_campo_a_resposta_e_a_de_hoje_com_a_verificacao(servidor):
    url, respostas, pedidos = servidor
    respostas += [FALA, json.dumps(extr(("lembranca", "lembranca", "Lembro que comi ração e foi bom")))]
    cod, r = _post(url + ROTA, pedido(dec2(lemb())))
    assert cod == 200 and r["erro"] is None
    assert r["verificacao"]["versao"] == "verif-v8"
    assert len(pedidos) == 2                                   # a voz e o verificador


def test_com_verificar_na_chamada_false_so_a_voz_e_chamada(servidor):
    url, respostas, pedidos = servidor
    respostas += [FALA]
    cod, r = _post(url + ROTA, pedido(dec2(lemb()), verificar_na_chamada=False))
    assert cod == 200 and r["erro"] is None and r["fala"] == "Lembro que comi ração e foi bom!"
    assert r["verificacao"] is None
    assert len(pedidos) == 1                                   # so a voz


def test_verificar_na_chamada_true_e_igual_a_sem_o_campo(servidor):
    url, respostas, pedidos = servidor
    respostas += [FALA, json.dumps(extr(("lembranca", "lembranca", "Lembro que comi ração e foi bom")))]
    cod, r = _post(url + ROTA, pedido(dec2(lemb()), verificar_na_chamada=True))
    assert cod == 200 and r["verificacao"]["versao"] == "verif-v8" and len(pedidos) == 2


@pytest.mark.parametrize("valor", [0, "false", None, [False]])
def test_valor_que_nao_e_booleano_e_400_sem_chamar_a_llm(servidor, valor):
    url, _, pedidos = servidor
    cod, r = _post(url + ROTA, pedido(dec2(lemb()), verificar_na_chamada=valor))
    assert cod == 400 and "verificar_na_chamada" in r["erro"] and pedidos == []


def test_o_campo_fora_da_rede_e_400(servidor):
    url, _, pedidos = servidor
    d = {"estado": {"identidade": {"estagio": "adulto"}}, "situacao": "conversa", "fala_jogador": "oi", "semente": 3,
         "verificar_na_chamada": False}
    cod, r = _post(url + ROTA, d)
    assert cod == 400 and "verificar_na_chamada" in r["erro"] and pedidos == []
