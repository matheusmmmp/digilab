"""LLM nas ferramentas de pesquisa (fora de digilab/, que fica so com stdlib).

Reusa os provedores do servidor de fala (servidor/fala_llm.py: Ollama local sem custo, Claude com custo).
Com Claude, o gasto tem teto TOTAL proprio, separado do da fala: tools/gasto_llm_pesquisa.json (fora do git).
Falha alto: resposta incompleta, JSON invalido ou teto de gasto atingido levantam erro.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from servidor.fala_llm import (ControleGasto, ProvedorClaude, ProvedorOllama, criar_cliente_claude,  # noqa: E402
                               MODELO_OLLAMA_PADRAO, MODELO_PADRAO, URL_OLLAMA_PADRAO)

ARQUIVO_GASTO_PESQUISA = Path(__file__).with_name("gasto_llm_pesquisa.json")


class LLMFalhou(RuntimeError):
    pass


def abrir_provedor(nome: str, modelo: str | None = None, limite_usd: float = 2.0,
                   url_ollama: str = URL_OLLAMA_PADRAO):
    """(provedor, controle de gasto | None). Sem o provedor pronto: erro (nada de cair em outro calado)."""
    if nome == "ollama":
        p = ProvedorOllama(modelo or MODELO_OLLAMA_PADRAO, url_ollama)
        ok, motivo = p.disponivel()
        if not ok:
            raise LLMFalhou(f"Ollama indisponivel: {motivo}")
        return p, None
    if nome == "claude":
        cliente = criar_cliente_claude()
        if cliente is None:
            raise LLMFalhou("sem credencial da API do Claude (ANTHROPIC_API_KEY)")
        return ProvedorClaude(cliente, modelo or MODELO_PADRAO), ControleGasto(limite_usd, arquivo=ARQUIVO_GASTO_PESQUISA)
    raise ValueError(f"provedor desconhecido: {nome!r}")


def chamar_json(provedor, gasto, sistema: str, pedido: str, esquema: dict, semente: int) -> tuple[dict, str]:
    """(objeto JSON devolvido, modelo). Com custo: reserva o pior caso antes e acerta pelo uso real."""
    custo_max = None
    if getattr(provedor, "tem_custo", False):
        if gasto is None:
            raise LLMFalhou("provedor com custo sem controle de gasto")
        custo_max = provedor.custo_maximo(sistema, pedido)
        if not gasto.reservar(custo_max):
            raise LLMFalhou(f"teto de gasto atingido (US$ {gasto.gasto:.4f} de US$ {gasto.limite:.2f})")
    try:
        r = provedor.gerar(sistema, pedido, esquema, semente)
    except Exception:
        if custo_max is not None:
            gasto.acertar(custo_max, custo_max)       # pode ter cobrado: conta o pior caso
        raise
    if custo_max is not None:
        real = provedor.custo_real(r)
        gasto.acertar(custo_max, custo_max if real is None else real)
    if not r.completa:
        raise LLMFalhou(f"resposta incompleta ({r.motivo_parada})")
    try:
        return json.loads(r.texto), r.modelo
    except json.JSONDecodeError as err:
        raise LLMFalhou(f"JSON invalido do modelo: {err}") from err
