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
    # treino (TAREFA_TREINO_SOMBRIO): um botao por exercicio. So o MotorTreino sabe aplicar;
    # no motor da v1 (state.aplicar_acao_usuario) elas levantam erro. Donos da v1 usam ACOES_V1.
    TREINAR_LEVANTAR_PEDRA = "treinar_levantar_pedra"
    TREINAR_CORRIDA = "treinar_corrida"
    TREINAR_ALVO = "treinar_alvo"
    TREINAR_ESQUIVA = "treinar_esquiva"
    TREINAR_MEDITAR = "treinar_meditar"
    TREINAR_RESISTENCIA = "treinar_resistencia"
    # educacao-v1 (docs/DESIGN_EDUCACAO_HERANCA_LESOES.md): so o MotorEducacao sabe aplicar; nos motores
    # anteriores levantam erro. Ficam no fim do enum para nao mexer em nada que dependa da ordem.
    PETISCO = "petisco"
    LEVAR_AO_BANHEIRO = "levar_ao_banheiro"
    TRATAR_LESAO = "tratar_lesao"


# as 6 acoes da v1, na ordem original: donos sorteiam daqui (list(AcaoUsuario) mudaria a
# canonica, que sorteia entre todas)
ACOES_V1 = (AcaoUsuario.ALIMENTAR, AcaoUsuario.LIMPAR, AcaoUsuario.BRINCAR, AcaoUsuario.ACARICIAR,
            AcaoUsuario.ELOGIAR, AcaoUsuario.REPREENDER)
ACOES_TREINO = tuple(a for a in AcaoUsuario if a.value.startswith("treinar_"))
ACOES_EDUCACAO = (AcaoUsuario.PETISCO, AcaoUsuario.LEVAR_AO_BANHEIRO, AcaoUsuario.TRATAR_LESAO)


def exercicio_de(acao: AcaoUsuario) -> str:
    if acao not in ACOES_TREINO:
        raise ValueError(f"acao nao e de treino: {acao}")
    return acao.value[len("treinar_"):]


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


def luta(tick: int, rival: str, semente: int) -> Evento:
    """educacao-v1: luta fora da arena de pesquisa. So rival e semente: o resultado e a lesao saem do
    replay da partida. So o reproduzir_educacao entende; os replays antigos levantam erro."""
    if "|" in rival:
        raise ValueError(f"nome de rival com '|': {rival!r}")
    return Evento(tick=tick, tipo="luta", valor=f"{rival}|{int(semente)}")


def ler_luta(evento: Evento) -> tuple[str, int]:
    if evento.tipo != "luta":
        raise ValueError(f"evento nao e luta: {evento.tipo!r}")
    rival, semente = str(evento.valor).rsplit("|", 1)
    return rival, int(semente)


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
