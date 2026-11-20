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

import json
import math
import time
from pathlib import Path

from digilab_fala_livre.ollama import Resposta
from servidor.fala_llm import LIMITE_USD_LIVRE_PADRAO, PRECOS_USD_POR_MTOK, ControleGasto, custo_usd  # noqa: F401  (PROPOSTO: US$ 3, plano secao 7)

ARQUIVO_GASTO_LIVRE = Path(__file__).with_name("gasto_fala_livre.json")     # fora do git
ESFORCO = "low"
# PROPOSTO, SEM FONTE: piso de max_tokens por chamada (era 1024 com o pensamento ligado; com ele desligado o JSON da fala cabe no
# teto por estagio, 80 a 360, e o piso so da folga ao tokenizador do Claude). Entra no pior caso reservado.
PISO_MAX_TOKENS = 512
# Fala de chat sem pensar (latencia e conta): Haiku 5.5 aceita `disabled` (com esforco high ou abaixo); no Sonnet 5.5 o `disabled`
# da 400 e o lugar dele e `between_tools` (so com esforco high ou abaixo, sem outro campo). Modelo fora da tabela nao liga.
PENSAMENTO = {"claude-haiku-5-5": {"type": "disabled"}, "claude-sonnet-5-5": {"type": "between_tools"}}
# O `output_config.format` nao aceita limites de string, array nem numero, e exige `additionalProperties: false` em todo objeto
# (skill claude-api, tool-use-concepts, "JSON Schema Limitations"). O limite de caracteres da fala fica por conta do `saida.aparar`
# e o catalogo do comando (enum) por conta do `saida.ler`, ambos depois da chamada.
PALAVRAS_NAO_ACEITAS = frozenset({"minLength", "maxLength", "minItems", "maxItems", "minimum", "maximum", "exclusiveMinimum",
                                  "exclusiveMaximum", "multipleOf", "uniqueItems", "pattern"})
TIMEOUT_S = 60.0
MODELOS_CLAUDE_LIVRE = ("claude-haiku-5-5", "claude-sonnet-5-5")


class ErroClaude(OSError):
    """Falha do cliente Claude (rede, recusa, corte, teto, credencial): o chamador cai na fala generica."""


def traduzir_esquema(esq):
    """Copia do esquema do Ollama sem as palavras que a API do Claude nao aceita e com `additionalProperties: false`."""
    if isinstance(esq, list):
        return [traduzir_esquema(x) for x in esq]
    if not isinstance(esq, dict):
        return esq
    out = {k: traduzir_esquema(v) for k, v in esq.items() if k not in PALAVRAS_NAO_ACEITAS}
    if out.get("type") == "object" and "properties" in out:
        out["additionalProperties"] = False
    return out


def impor_limites(texto: str, esq: dict) -> str:
    """O Ollama para a geracao no `maxLength` do esquema (a fala vem cortada e o `saida.aparar` deixa so o inteiro). A API do
    Claude nao aceita `maxLength`, entao a fala longa e cortada aqui no mesmo ponto, antes do `aparar`. Texto que nao e JSON
    de objeto passa intacto: o `saida.ler` levanta, como com o Ollama."""
    try:
        obj = json.loads(texto)
    except ValueError:
        return texto
    if not isinstance(obj, dict):
        return texto
    mudou = False
    for nome, p in (esq.get("properties") or {}).items():
        lim = p.get("maxLength") if isinstance(p, dict) else None
        if lim is not None and isinstance(obj.get(nome), str) and len(obj[nome]) > lim:
            obj[nome], mudou = obj[nome][:lim], True
    return json.dumps(obj, ensure_ascii=False) if mudou else texto


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
        if modelo not in PENSAMENTO:
            raise ValueError(f"modelo sem regra de pensamento: {modelo!r}; so {', '.join(PENSAMENTO)}")
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
                                       thinking=PENSAMENTO[self.modelo],
                                       output_config={"effort": ESFORCO,
                                                      "format": {"type": "json_schema", "schema": traduzir_esquema(esquema)}})
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
        return Resposta(impor_limites(texto, esquema), getattr(resp, "model", self.modelo), time.perf_counter() - t0, ent, sai,
                        resp.stop_reason == "end_turn")
