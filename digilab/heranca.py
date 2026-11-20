"""Geracoes e heranca (educacao-v1, sistema B; docs/DESIGN_EDUCACAO_HERANCA_LESOES.md, secao 3).

Herda:
  - temperamento do motor (4 eixos) e temperamento do ovo (eixos do catalogo): media dos pais + N(0, sigma),
    cortado na faixa de cada um;
  - especie: sorteada entre as dos pais.
Nao herda nada aprendido (bandit, memoria, carater, disciplina, vinculo) nem tracos da camada 3.
Sorteio numa rng propria, `rng_heranca`, derivada da semente da heranca: nao toca ambiente, politica,
travessura nem combate. Ordem fixa: a especie, depois os eixos do motor (EIXOS), depois os do ovo (ordenados).

O log do filho comeca com o evento `origem` (tick 0): sha256 dos logs dos pais, os tracos herdaveis de cada
um, a semente da heranca e quem cruzou. O replay (educacao.reproduzir_educacao) recalcula a heranca a partir
do evento e falha alto se o motor tiver outro temperamento ou especie; `conferir_pais` confere os hashes
quando os logs dos pais estao a mao. Pais de donos diferentes: permitido (o cruzamento e local, pelos arquivos).
"""

from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass

from .config import CONFIG_EVOLUCAO_PESQUISA, CONFIG_HERANCA, ConfigHeranca
from .events import Evento, LogDeEventos
from .protocol import derivar_semente
from .temperamento import EIXOS, Temperamento

ORDEM_ESTAGIOS = ("bebe", "crianca", "adolescente", "adulto")


class HerancaInvalida(ValueError):
    pass


def sha_log(log: LogDeEventos) -> str:
    return hashlib.sha256(log.para_jsonl().encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class Genitor:
    log_sha256: str
    especie: str
    temperamento: dict          # Temperamento.para_dict()
    temperamento_ovo: dict      # eixos do catalogo (evolucao.ovo)
    estagio: str
    dono: str

    def para_dict(self) -> dict:
        return {"log_sha256": self.log_sha256, "especie": self.especie, "temperamento": dict(self.temperamento),
                "temperamento_ovo": dict(self.temperamento_ovo), "estagio": self.estagio, "dono": self.dono}


def genitor(log: LogDeEventos, especie: str, temperamento: Temperamento, temperamento_ovo: dict, estagio: str,
            dono: str) -> Genitor:
    return Genitor(sha_log(log), especie, temperamento.para_dict(), dict(temperamento_ovo), estagio, dono)


@dataclass(frozen=True)
class Origem:
    pais: tuple[Genitor, Genitor]
    semente_heranca: int
    quem_cruzou: str
    especie: str
    temperamento: Temperamento
    temperamento_ovo: dict

    def evento(self) -> Evento:
        valor = json.dumps({"pais": [p.para_dict() for p in self.pais], "semente_heranca": self.semente_heranca,
                            "quem_cruzou": self.quem_cruzou}, sort_keys=True, separators=(",", ":"))
        return Evento(tick=0, tipo="origem", valor=valor)


def _corte(x: float, a: float) -> float:
    return min(a, max(-a, x))


def cruzar(pai: Genitor, mae: Genitor, semente_heranca: int, quem_cruzou: str,
           cfg: ConfigHeranca | None = None) -> Origem:
    cfg = cfg or CONFIG_HERANCA
    minimo = ORDEM_ESTAGIOS.index(cfg.estagio_minimo_pais)
    for g in (pai, mae):
        if g.estagio not in ORDEM_ESTAGIOS or ORDEM_ESTAGIOS.index(g.estagio) < minimo:
            raise HerancaInvalida(f"genitor no estagio {g.estagio!r}: precisa de {cfg.estagio_minimo_pais!r}")
    if set(pai.temperamento_ovo) != set(mae.temperamento_ovo):
        raise HerancaInvalida("pais com eixos de temperamento do ovo diferentes")
    rng = random.Random(derivar_semente("heranca", semente_heranca))
    especie = (pai.especie, mae.especie)[rng.randrange(2)]
    temp = {e: _corte((pai.temperamento[e] + mae.temperamento[e]) / 2 + rng.gauss(0.0, cfg.sigma_temperamento), 1.0)
            for e in EIXOS}
    a = CONFIG_EVOLUCAO_PESQUISA.amplitude_temperamento
    temp_ovo = {e: _corte((pai.temperamento_ovo[e] + mae.temperamento_ovo[e]) / 2
                          + rng.gauss(0.0, cfg.sigma_temperamento), a) for e in sorted(pai.temperamento_ovo)}
    return Origem((pai, mae), semente_heranca, quem_cruzou, especie, Temperamento(**temp), temp_ovo)


def ler_origem(evento: Evento, cfg: ConfigHeranca | None = None) -> Origem:
    """Recalcula a heranca a partir do evento (o filho nao e gravado: sai da conta)."""
    if evento.tipo != "origem":
        raise HerancaInvalida(f"evento nao e origem: {evento.tipo!r}")
    d = json.loads(str(evento.valor))
    pai, mae = (Genitor(**p) for p in d["pais"])
    return cruzar(pai, mae, int(d["semente_heranca"]), str(d["quem_cruzou"]), cfg)


def conferir_pais(origem: Origem, log_pai: LogDeEventos, log_mae: LogDeEventos) -> None:
    for g, log in zip(origem.pais, (log_pai, log_mae)):
        if sha_log(log) != g.log_sha256:
            raise HerancaInvalida(f"log do genitor nao bate com o hash da origem ({g.log_sha256[:12]}...)")
