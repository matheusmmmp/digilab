"""Rotas da fala livre no servidor local (exp-fala-livre), com um Ollama falso."""

from __future__ import annotations

import io
import json
import sys
import threading
import urllib.error
import urllib.request
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "tests"))

from digilab_fala_livre.ollama import ClienteOllama  # noqa: E402
from servidor import servidor_local  # noqa: E402
from servidor.fala_livre import ROTA_FALA, ROTA_STATUS, ROTA_VERIF, ServicoFalaLivre  # noqa: E402
from test_fala_livre import ESTADO  # noqa: E402


class _Resp(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _ollama_falso(respostas: list[str], pedidos: list):
    def abrir(req, timeout):
        pedidos.append(json.loads(req.data.decode("utf-8")))
        return _Resp(json.dumps({"message": {"content": respostas.pop(0)}, "done": True,
                                 "done_reason": "stop", "model": "falso"}).encode())
    return abrir


@pytest.fixture
def servidor():
    pedidos, respostas = [], []
    servidor_local.Tratador.fala_livre.cliente = ClienteOllama("falso", abrir=_ollama_falso(respostas, pedidos))
    srv = ThreadingHTTPServer(("127.0.0.1", 0), partial(servidor_local.Tratador, directory=str(servidor_local.PASTA_SERVIDA)))
    th = threading.Thread(target=srv.serve_forever, daemon=True)
    th.start()
    yield f"http://127.0.0.1:{srv.server_address[1]}", respostas, pedidos
    srv.shutdown()


def _post(url, corpo):
    req = urllib.request.Request(url, data=json.dumps(corpo).encode(), method="POST",
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as err:
        return err.code, json.loads(err.read())


def test_rota_instalada_por_um_unico_gancho():
    fonte = (RAIZ / "servidor" / "servidor_local.py").read_text(encoding="utf-8")
    assert fonte.count("GANCHO fala-livre") == 1 and fonte.count("fala_livre") == 1
    assert ROTA_FALA in servidor_local.ROTAS_REMOTAS and isinstance(servidor_local.Tratador.fala_livre, ServicoFalaLivre)


def test_fala_e_verificacao_pelo_servidor(servidor):
    url, respostas, pedidos = servidor
    respostas += ['{"fala": "Tava com fome.", "fatos_citados": ["R1"]}']
    cod, r = _post(url + ROTA_FALA, {"estado": ESTADO, "situacao": "conversa", "fala_jogador": "por que?",
                                     "historico": [["oi", "Oi."]], "semente": 5})
    assert cod == 200 and r["fala"] == "Tava com fome." and r["versao_app"] == "fala-livre" and r["erro"] is None
    respostas += ['{"afirmacoes": [{"tipo": "causa", "trecho": "tava com fome"}]}', '{"sustentada": true, "fato": "E1"}']
    cod, v = _post(url + ROTA_VERIF, {"fala": r["fala"], "fatos_citados": r["fatos_citados"], "fatos": r["fatos"],
                                      "semente": 5})
    assert cod == 200 and v["nao_suportadas"] == 0 and v["manipulacao"] is False
    with urllib.request.urlopen(url + ROTA_STATUS, timeout=5) as resp:
        assert json.loads(resp.read())["versao_app"] == "fala-livre"


@pytest.mark.parametrize("corpo", [{"estado": ESTADO, "situacao": "outra"},
                                   {"estado": {**ESTADO, "x": 1}, "situacao": "espontanea"},
                                   {"estado": ESTADO, "situacao": "conversa"},
                                   {"estado": ESTADO, "situacao": "conversa", "fala_jogador": "a" * 500},
                                   {"estado": ESTADO, "situacao": "espontanea", "semente": -1}])
def test_pedido_invalido_da_400_sem_chamar_a_llm(servidor, corpo):
    url, _, pedidos = servidor
    cod, r = _post(url + ROTA_FALA, corpo)
    assert cod == 400 and "invalido" in r["erro"] and pedidos == []


def test_rota_antiga_continua(servidor):
    url, _, _ = servidor
    cod, _r = _post(url + "/api/fala", {"motivo": {}, "estagio": "adulto"})
    assert cod in (200, 400)          # a rota da moldura continua sendo tratada pelo servidor original


VOZ = {"identidade": {"estagio": "adulto", "especie": "Amizade", "forma": "Angemon"},
       "estado": {"fome": 0.8, "humor": 0.7}, "vinculo": 0.6,
       "historia": [{"tipo": "O", "regra": "demora", "chave": "O:demora", "texto": "você atende meus chamados rápido",
                     "dados": {"rapido": True}}]}


def test_voz_livre_v6_com_autocorrecao_estilo_e_ida_e_volta(servidor):
    url, respostas, pedidos = servidor
    respostas += ['{"fala": "Ontem você me deu um bolo! E você atende rápido.", "fatos_citados": ["O1"]}',
                  '{"afirmacoes": [{"tipo": "evento", "trecho": "Ontem você me deu um bolo"},'
                  ' {"tipo": "costume", "trecho": "você atende rápido"}]}',
                  '{"sustentada": false, "fato": ""}', '{"sustentada": true, "fato": "O1"}']
    cod, r = _post(url + ROTA_FALA, {"estado": VOZ, "situacao": "espontanea", "semente": 3, "voz": True})
    assert cod == 200 and r["versao_prompt"] == "livre-v6" and r["erro"] is None
    assert r["invencoes"] == ["Ontem você me deu um bolo"] and r["revisoes"] == 0      # inventar pode: nao revisa
    assert r["especie_corpus"] == "Angemon" and "ESTILO DA ESPÉCIE" in pedidos[0]["messages"][-1]["content"]
    assert r["verificacao"]["versao"] == "verif-v5" and len(r["corpus_sha256"]) == 64
    respostas += ['{"afirmacoes": []}']
    cod, v = _post(url + ROTA_VERIF, {"fala": r["fala"], "fatos_citados": r["fatos_citados"], "fatos": r["fatos"],
                                      "semente": 3, "voz": True})
    assert cod == 200 and v["versao"] == "verif-v5"                     # os fatos com meta voltam sem 400


def test_voz_almanaque_sorteado_pelo_servidor_e_nao_pela_pagina(servidor):
    url, respostas, _ = servidor
    cod, r = _post(url + ROTA_FALA, {"estado": {**VOZ, "almanaque": {"id": "m01"}}, "situacao": "espontanea",
                                     "voz": True})
    assert cod == 400
    import random as _r
    from digilab_fala_livre import almanaque
    s = next(s for s in range(500) if almanaque.sortear(_r.Random(s)) is not None)
    respostas += ['{"fala": "Ouvi falar disso!", "fatos_citados": ["W1"]}', '{"afirmacoes": []}']
    cod, r = _post(url + ROTA_FALA, {"estado": VOZ, "situacao": "espontanea", "semente": s, "voz": True, "internet": True})
    assert cod == 200 and any(f["id"] == "W1" for f in r["fatos"]) and not any(f["id"] == "O1" for f in r["fatos"])


def test_verificar_recusa_meta_de_tipo_errado(servidor):
    url, _, pedidos = servidor
    ruim = [{"id": "F1", "tipo": "dizer agora", "texto": "x", "mentira": "sim"}]
    cod, _r = _post(url + ROTA_VERIF, {"fala": "x", "fatos_citados": [], "fatos": ruim, "voz": True})
    assert cod == 400 and pedidos == []
