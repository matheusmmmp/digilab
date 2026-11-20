"""Decisores do modo livre gravado (excecao ao determinismo, CLAUDE.md 2026-09-28).

O MotorEducacao pergunta ao decisor so no slot de chamado sem necessidade real ("faco manha agora?").
Cada resposta vai para o log como `decisao_externa`; o replay le do log. Dois decisores:
  DecisorEntropia  acaso real do sistema operacional (sem semente): mesma chance que a rng usaria
  DecisorLLM       o modelo decide no papel do pet, vendo temperamento, disciplina e necessidades
Nenhum dos dois vale para a confirmatoria nem para protocolos com hash: analise exploratoria.
"""
from __future__ import annotations

import random

from llm_pesquisa import chamar_json

VERSAO_PROMPT_DECISOR = "decisor-slot-falso-v1"

SISTEMA_PET = (
    "Voce e um bichinho virtual (estilo Digimon) decidindo se faz MANHA agora: chamar o dono sem precisar de nada. "
    "Leve em conta seu temperamento (eixos de -1 a 1), sua disciplina (0 a 100: alta = educado) e quantas vezes o "
    "dono ja cedeu com petisco (quanto mais, mais vale a pena fazer manha). Responda SO o JSON pedido."
)
ESQUEMA_DECISAO = {"type": "object", "properties": {"chamado_falso": {"type": "boolean"}},
                   "required": ["chamado_falso"], "additionalProperties": False}


class DecisorEntropia:
    def __init__(self) -> None:
        self._rng = random.SystemRandom()

    def __call__(self, ctx: dict) -> tuple[bool, dict]:
        return self._rng.random() < ctx["fracao_falso"], {"fonte": "entropia-os", "versao": "v1"}


class DecisorLLM:
    def __init__(self, provedor, gasto=None) -> None:
        self.provedor, self.gasto = provedor, gasto
        self.chamadas = 0

    def __call__(self, ctx: dict) -> tuple[bool, dict]:
        t = ", ".join(f"{k} {v:+.2f}" for k, v in ctx["temperamento"].items())
        n = ", ".join(f"{k} {v:.2f}" for k, v in ctx["necessidades"].items())
        pedido = (f"Estagio {ctx['estagio']}. Temperamento: {t}. Disciplina {ctx['disciplina']}. "
                  f"O dono ja cedeu com petisco {ctx['petiscos_cedidos']} vezes. Necessidades (0-1, alto = bem): {n}. "
                  f"Voce poderia pedir {ctx['pedido']}, mas nao precisa. Faz manha agora?")
        d, modelo = chamar_json(self.provedor, self.gasto, SISTEMA_PET, pedido, ESQUEMA_DECISAO, ctx["tick"])
        self.chamadas += 1
        if set(d) != {"chamado_falso"} or not isinstance(d["chamado_falso"], bool):
            raise ValueError(f"decisao malformada do modelo: {d!r}")
        return d["chamado_falso"], {"fonte": f"llm:{modelo}", "versao": VERSAO_PROMPT_DECISOR}
