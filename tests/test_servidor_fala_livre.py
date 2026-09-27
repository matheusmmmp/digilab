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
    assert cod == 200 and r["fala"] == "Tava com fome." and r["versao_app"] == "exp-fala-livre" and r["erro"] is None
    respostas += ['{"afirmacoes": [{"tipo": "causa", "trecho": "tava com fome"}]}', '{"sustentada": true, "fato": "E1"}']
    cod, v = _post(url + ROTA_VERIF, {"fala": r["fala"], "fatos_citados": r["fatos_citados"], "fatos": r["fatos"],
                                      "semente": 5})
    assert cod == 200 and v["nao_suportadas"] == 0 and v["manipulacao"] is False
    with urllib.request.urlopen(url + ROTA_STATUS, timeout=5) as resp:
        assert json.loads(resp.read())["versao_app"] == "exp-fala-livre"


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
