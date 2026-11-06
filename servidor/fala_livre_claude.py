"""Cliente Claude da fala livre (CONVERSA_PET, M5; decisao D5 de 2026-11-06): a mesma interface do `ClienteOllama`, para a
comparacao cega gemma2:9b x claude-haiku-5-5 x claude-sonnet-5-5.

    ClienteClaude(modelo, gasto).conversar(mensagens, esquema, max_tokens, semente) -> Resposta

- as mensagens de sistema viram o `system`; a saida estruturada vai por `output_config.format` com o MESMO esquema JSON;
  esforco `low`; sem temperatura nem semente (a API nao aceita): a semente fica so no log do chamador;
- falha (rede, recusa, `max_tokens`, teto de gasto, modelo sem preco, chave ausente) sobe como `ErroClaude`, que e `OSError`:
  o `gerar` e o `gerar_com_revisao` ja capturam `OSError` e caem na fala generica, como com o Ollama. JSON invalido volta
  como texto e o `saida.ler` levanta, como com o Ollama;
- gasto: o `ControleGasto` de `fala_llm.py`, em arquivo PROPRIO (`gasto_fala_livre.json`, fora do git) e teto proprio.
  Reserva o pior caso antes e acerta pelo `usage`; chamada que falha sem `usage` conta o maximo reservado;
- a chave so vem do ambiente (`ANTHROPIC_API_KEY` ou o perfil do `ant`), nunca da pagina nem de arquivo do repo.

O SDK `anthropic` so e importado na primeira chamada (o servidor sobe sem ele quando o provedor e o Ollama).
Nenhuma chamada de rede acontece na importacao deste modulo.
"""

from __future__ import annotations

import math
import time
from pathlib import Path

from digilab_fala_livre.ollama import Resposta
from servidor.fala_llm import LIMITE_USD_LIVRE_PADRAO, PRECOS_USD_POR_MTOK, ControleGasto, custo_usd  # noqa: F401  (PROPOSTO: US$ 3, plano secao 7)

ARQUIVO_GASTO_LIVRE = Path(__file__).with_name("gasto_fala_livre.json")     # fora do git
ESFORCO = "low"
# PROPOSTO, SEM FONTE: piso de max_tokens por chamada. O modelo pode pensar antes de responder (adaptativo) e o `max_tokens`
# conta o pensamento; com o teto de saida do Ollama (dezenas de tokens) a resposta seria cortada. O piso entra no pior caso reservado.
PISO_MAX_TOKENS = 1024
TIMEOUT_S = 60.0
MODELOS_CLAUDE_LIVRE = ("claude-haiku-5-5", "claude-sonnet-5-5")


class ErroClaude(OSError):
    """Falha do cliente Claude (rede, recusa, corte, teto, credencial): o chamador cai na fala generica."""


def _partir(mensagens: list[dict]) -> tuple[str, list[dict]]:
    """(system, mensagens user/assistant). Falha alto se a lista nao tem turno de conversa ou tem papel desconhecido."""
    sistema, resto = [], []
    for m in mensagens:
        papel = m["role"]
        if papel == "system":
            sistema.append(m["content"])
        elif papel in ("user", "assistant"):
            resto.append({"role": papel, "content": m["content"]})
        else:
            raise ValueError(f"papel de mensagem desconhecido: {papel!r}")
    if not resto or resto[0]["role"] != "user":
        raise ValueError("a conversa precisa comecar por uma mensagem do jogador (user)")
    return "\n\n".join(sistema), resto


class ClienteClaude:
    """`gasto` e um `ControleGasto`; `sdk` (um objeto com `.messages.create`) e injetavel para teste;
    `permitido()` devolve False quando o provedor esta desligado (modo remoto sem --claude-remoto)."""

    def __init__(self, modelo: str, gasto: ControleGasto | None = None, sdk=None, permitido=None,
                 timeout: float = TIMEOUT_S) -> None:
        if modelo not in PRECOS_USD_POR_MTOK:
            raise ValueError(f"modelo sem preco conhecido: {modelo!r}; sem preco nao da para garantir o teto de gasto")
        self.modelo = modelo
        self.gasto = gasto if gasto is not None else ControleGasto(LIMITE_USD_LIVRE_PADRAO, ARQUIVO_GASTO_LIVRE)
        self._sdk = sdk
        self._permitido = permitido or (lambda: True)
        self.timeout = timeout
        self.carregado = True            # mesma superficie do ClienteOllama para o status

    def _cliente(self):
        if self._sdk is None:
            try:
                import anthropic
            except ImportError as err:
                raise ErroClaude("SDK anthropic nao instalado (pip install -r servidor/requirements.txt)") from err
            try:
                self._sdk = anthropic.Anthropic(timeout=self.timeout)        # ANTHROPIC_API_KEY ou o perfil do ant
            except Exception as err:    # credencial ausente: o SDK levanta na construcao
                raise ErroClaude(f"sem credencial da API: {err}") from err
        return self._sdk

    def custo_maximo(self, sistema: str, mensagens: list[dict], max_tokens: int) -> float:
        # entrada estimada por cima: 1 token a cada 2 caracteres, mais folga (mesma regra do ProvedorClaude)
        chars = len(sistema) + sum(len(m["content"]) for m in mensagens)
        return custo_usd(self.modelo, math.ceil((chars + 400) / 2), max(max_tokens, PISO_MAX_TOKENS))

    def conversar(self, mensagens: list[dict], esquema: dict, max_tokens: int, semente: int) -> Resposta:
        # `semente` nao vai para a API (ela nao aceita semente nem temperatura); o chamador a registra no log
        if not self._permitido():
            raise ErroClaude("API do Claude desligada neste modo (remoto sem --claude-remoto)")
        sistema, conversa = _partir(mensagens)
        teto_saida = max(max_tokens, PISO_MAX_TOKENS)
        custo_max = self.custo_maximo(sistema, conversa, max_tokens)
        if not self.gasto.reservar(custo_max):
            raise ErroClaude(f"teto de gasto da fala livre atingido (US$ {self.gasto.limite:.2f})")
        t0 = time.perf_counter()
        try:
            sdk = self._cliente()
            resp = sdk.messages.create(model=self.modelo, max_tokens=teto_saida, system=sistema, messages=conversa,
                                       output_config={"effort": ESFORCO, "format": {"type": "json_schema", "schema": esquema}})
        except ErroClaude:
            self.gasto.acertar(custo_max, 0.0)           # nada saiu da maquina
            raise
        except Exception as err:                          # rede, 4xx/5xx, timeout: pode ter sido cobrado
            self.gasto.acertar(custo_max, custo_max)
            raise ErroClaude(f"{type(err).__name__}: {err}") from err
        uso = getattr(resp, "usage", None)
        ent, sai = getattr(uso, "input_tokens", None), getattr(uso, "output_tokens", None)
        if ent is None or sai is None:
            self.gasto.acertar(custo_max, custo_max)      # sem usage: conta o maximo
        else:
            self.gasto.acertar(custo_max, custo_usd(self.modelo, ent, sai))
        if resp.stop_reason == "refusal":
            raise ErroClaude("recusa (stop_reason=refusal)")
        if resp.stop_reason == "max_tokens":
            raise ErroClaude(f"resposta cortada por max_tokens ({teto_saida})")
        texto = next((b.text for b in resp.content if b.type == "text"), "")
        return Resposta(texto, getattr(resp, "model", self.modelo), time.perf_counter() - t0, ent, sai,
                        resp.stop_reason == "end_turn")
