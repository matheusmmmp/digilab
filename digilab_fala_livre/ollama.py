"""Chamada SO ao Ollama local (TAREFA_FALA_LIVRE, barreira 5: nenhuma API paga).

`ClienteOllama` recusa qualquer URL que nao seja da propria maquina. `abrir` e injetavel para testes.
"""

from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass

URL_PADRAO = "http://localhost:11434"
HOSTS_LOCAIS = ("localhost", "127.0.0.1", "::1")
TIMEOUT_S = 30.0
TIMEOUT_CARGA_S = 180.0     # primeira chamada carrega o modelo (os de 7-9B demoram)
MANTER = "10m"
TEMPERATURA = 0.7


class NaoLocal(ValueError):
    """URL de LLM fora da maquina: proibido neste experimento."""


@dataclass(frozen=True)
class Resposta:
    texto: str
    modelo: str
    latencia_s: float
    tokens_entrada: int | None
    tokens_saida: int | None
    completa: bool


class ClienteOllama:
    def __init__(self, modelo: str, url: str = URL_PADRAO, abrir=None) -> None:
        host = urllib.parse.urlparse(url).hostname
        if host not in HOSTS_LOCAIS:
            raise NaoLocal(f"so Ollama local: {url}")
        self.modelo, self.url = modelo, url.rstrip("/")
        self._abrir = abrir or urllib.request.urlopen
        self.carregado = False

    def _post(self, caminho: str, corpo: dict, timeout: float) -> dict:
        req = urllib.request.Request(self.url + caminho, data=json.dumps(corpo).encode("utf-8"), method="POST",
                                     headers={"Content-Type": "application/json"})
        with self._abrir(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def conversar(self, mensagens: list[dict], esquema: dict, max_tokens: int, semente: int) -> Resposta:
        corpo = {"model": self.modelo, "messages": mensagens, "format": esquema, "stream": False,
                 "keep_alive": MANTER,
                 "options": {"temperature": TEMPERATURA, "seed": semente, "num_predict": max_tokens}}
        t0 = time.perf_counter()
        d = self._post("/api/chat", corpo, TIMEOUT_S if self.carregado else TIMEOUT_CARGA_S)
        self.carregado = True
        motivo = d.get("done_reason", "stop" if d.get("done") else "incompleto")
        return Resposta(d.get("message", {}).get("content", ""), d.get("model", self.modelo),
                        time.perf_counter() - t0, d.get("prompt_eval_count"), d.get("eval_count"), motivo == "stop")

    def descarregar(self) -> None:
        """Tira o modelo da GPU (a avaliacao roda um modelo por vez: so um cabe nos 6 GB)."""
        self._post("/api/generate", {"model": self.modelo, "keep_alive": 0}, TIMEOUT_S)
        self.carregado = False
