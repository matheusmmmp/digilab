"""O registro do genoma (V3 G0, etapa E1; docs/TAREFA_V3_GENOMA_G0.md, secoes 3.1 e 8; G0-1 a G0-7 DECIDIDAS em 2026-11-04).

So o registro: o `Genoma`, a ida e volta com o evento `genoma` e as falhas altas. O motor, o `mundo.py`, a bancada e o replay NAO o
conhecem ainda (E2 e E3). Biblioteca padrao e inteiros, textos e listas no evento.

- **G0-2:** cinco secoes, na ordem fixa `SECOES`. Uma secao desconhecida ou faltando falha alto.
- **G0-3:** cada secao so na forma `"hoje"` (o fenotipo sai da semente e da config, como hoje; sem valores).
- **G0-4:** o evento `genoma`, tick 0, valor = JSON canonico de `{"versao": 1, "secoes": {nome: {"forma": "hoje"}}}`
  (`sort_keys`, ASCII, o mesmo do hash do protocol.py); o sha256 desse JSON identifica o genoma.
- **EG-5:** nenhum campo vem do aprendido (politica, memoria, carater): so as cinco secoes inatas existem.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field

from .events import Evento

TIPO_EVENTO = "genoma"
VERSAO = 1
SECOES = ("temperamento", "especie", "frutas", "paladar", "inatos")   # G0-2; a ordem fixa
FORMAS = ("hoje",)                                                   # G0-3; "valores" fica para o G1


class GenomaInvalido(ValueError):
    """O evento ou o registro do genoma esta fora do formato (falha alto)."""


def _inteiro(x: object, nome: str) -> int:
    if type(x) is not int:
        raise GenomaInvalido(f"{nome} nao e inteiro: {x!r}")
    return x


@dataclass(frozen=True)
class Genoma:
    """Uma forma por secao. O genoma vazio (`Genoma()`) e `"hoje"` em todas."""

    secoes: dict = field(default_factory=lambda: {s: "hoje" for s in SECOES})

    def __post_init__(self) -> None:
        if not isinstance(self.secoes, dict):
            raise GenomaInvalido(f"secoes e um dict: {self.secoes!r}")
        desconhecidas = sorted(str(s) for s in self.secoes if s not in SECOES)
        if desconhecidas:
            raise GenomaInvalido(f"secao desconhecida: {desconhecidas}")
        faltando = [s for s in SECOES if s not in self.secoes]
        if faltando:
            raise GenomaInvalido(f"secao faltando: {faltando}")
        for nome in SECOES:
            if self.secoes[nome] not in FORMAS:
                raise GenomaInvalido(f"forma desconhecida na secao {nome!r}: {self.secoes[nome]!r}")
        object.__setattr__(self, "secoes", {s: self.secoes[s] for s in SECOES})

    def json(self) -> str:
        """O JSON canonico (sort_keys, ASCII, sem espacos): o valor do evento e a base do sha256."""
        carga = {"versao": VERSAO, "secoes": {s: {"forma": f} for s, f in self.secoes.items()}}
        return json.dumps(carga, sort_keys=True, ensure_ascii=True, separators=(",", ":"))

    def sha256(self) -> str:
        return hashlib.sha256(self.json().encode("ascii")).hexdigest()

    def evento(self) -> Evento:
        return Evento(tick=0, tipo=TIPO_EVENTO, valor=self.json())

    @staticmethod
    def de_evento(evento: Evento) -> "Genoma":
        if evento.tipo != TIPO_EVENTO:
            raise GenomaInvalido(f"nao e um evento {TIPO_EVENTO!r}: {evento.tipo!r}")
        if evento.tick != 0:
            raise GenomaInvalido(f"o genoma e do tick 0: {evento.tick!r}")
        if not isinstance(evento.valor, str):
            raise GenomaInvalido(f"o valor do genoma e texto JSON: {evento.valor!r}")
        try:
            d = json.loads(evento.valor)
        except ValueError as e:
            raise GenomaInvalido(f"JSON invalido: {e}") from e
        if not isinstance(d, dict) or set(d) != {"versao", "secoes"}:
            raise GenomaInvalido(f"campos do evento: esperados versao e secoes, vieram {sorted(d) if isinstance(d, dict) else d!r}")
        if _inteiro(d["versao"], "versao") != VERSAO:
            raise GenomaInvalido(f"versao desconhecida: {d['versao']}")
        if not isinstance(d["secoes"], dict):
            raise GenomaInvalido("secoes e um objeto")
        formas = {}
        for nome, sec in d["secoes"].items():
            if nome not in SECOES:
                raise GenomaInvalido(f"secao desconhecida: {nome!r}")
            if not isinstance(sec, dict) or set(sec) != {"forma"}:
                raise GenomaInvalido(f"secao {nome!r}: so o campo forma (campo a mais ou faltando): {sec!r}")
            formas[nome] = sec["forma"]
        g = Genoma(formas)
        if g.json() != evento.valor:   # o evento tem de ser o canonico (sem espaco, ordem, ASCII)
            raise GenomaInvalido("o JSON do evento nao e o canonico")
        return g
