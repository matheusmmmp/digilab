"""Eventos.

O log de eventos e a unica fonte de verdade. O estado do pet nunca e
salvo: ele e sempre reconstruido rodando o log de novo a partir do
nascimento, com a mesma semente. Se o replay divergir, e bug, e o teste
quebra.

So dois tipos de evento entram no log:

  AcaoUsuario  - o que a pessoa fez, e quando
  Avanco       - quanto tempo passou desde o evento anterior

As acoes do pet NAO entram no log. Elas sao derivadas: sao exatamente o
que a politica produz ao reprocessar o log. E por isso que o log e um
dado de pesquisa e nao so um save file.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from typing import Iterator, Sequence


class AcaoUsuario(str, Enum):
    ALIMENTAR = "alimentar"
    LIMPAR = "limpar"
    BRINCAR = "brincar"
    ACARICIAR = "acariciar"
    ELOGIAR = "elogiar"
    REPREENDER = "repreender"


class AcaoPet(str, Enum):
    OCIOSO = "ocioso"
    DORMIR = "dormir"
    COMER = "comer"
    BRINCAR = "brincar"
    CHAMAR_ATENCAO = "chamar_atencao"
    EXPLORAR = "explorar"
    EMBURRAR = "emburrar"


@dataclass(frozen=True)
class Evento:
    """Um evento no log. `tick` e o tempo absoluto desde o nascimento."""

    tick: int
    tipo: str  # "avanco" | "acao_usuario"
    valor: str | int

    def para_dict(self) -> dict:
        return {"tick": self.tick, "tipo": self.tipo, "valor": self.valor}

    @staticmethod
    def de_dict(d: dict) -> "Evento":
        return Evento(tick=int(d["tick"]), tipo=str(d["tipo"]), valor=d["valor"])


def avanco(tick: int, ticks: int) -> Evento:
    if ticks <= 0:
        raise ValueError(f"avanco precisa ser positivo, recebeu {ticks}")
    return Evento(tick=tick, tipo="avanco", valor=int(ticks))


def acao_usuario(tick: int, acao: AcaoUsuario) -> Evento:
    return Evento(tick=tick, tipo="acao_usuario", valor=acao.value)


class LogDeEventos:
    """Lista append-only de eventos, serializavel como JSONL."""

    def __init__(self, eventos: Sequence[Evento] | None = None) -> None:
        self._eventos: list[Evento] = list(eventos or [])

    def anexar(self, evento: Evento) -> None:
        if self._eventos and evento.tick < self._eventos[-1].tick:
            raise ValueError(
                f"evento fora de ordem: tick {evento.tick} vem depois de "
                f"{self._eventos[-1].tick}"
            )
        self._eventos.append(evento)

    def __iter__(self) -> Iterator[Evento]:
        return iter(self._eventos)

    def __len__(self) -> int:
        return len(self._eventos)

    def __getitem__(self, i: int) -> Evento:
        return self._eventos[i]

    def para_jsonl(self) -> str:
        return "\n".join(json.dumps(e.para_dict(), ensure_ascii=False) for e in self._eventos)

    @staticmethod
    def de_jsonl(texto: str) -> "LogDeEventos":
        eventos = [
            Evento.de_dict(json.loads(linha))
            for linha in texto.splitlines()
            if linha.strip()
        ]
        return LogDeEventos(eventos)
