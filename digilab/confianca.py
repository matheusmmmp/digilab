"""Confianca de combate e desgaste por rival repetido (MVP M1, docs/DESIGN_MVP_M1_CONFIANCA.md, 2026-09-29).

Um ESTADO derivado dos eventos de luta que ja existem (nao e eixo de personalidade nem evento novo no log): o
replay recalcula tudo a partir das lutas. Nenhuma rng. Tudo PROPOSTO (ConfigConfianca), sem fonte.

  novidade por rival (2.1):  m[rival] <- m[rival] * exp(-dt_rival / tau_hab) + 1     (depois da luta)
                             novidade = exp(-lambda * m[rival] antes da luta)          (1 no primeiro encontro)
  confianca c em [-1, 1] (2.2), 0 no ovo:
                             c <- c * exp(-dt / tau_conf)                              (antes da luta)
                             c <- corte(c + eta_s * novidade * sinal, -1, 1)           (vitoria +1, derrota -1, empate 0)
                             eta_s = eta (sinal > 0); eta * (1 + k_sens * sensibilidade) (sinal < 0)
  epsilon do lutador (2.3):  + kappa * max(0, -c)  (a confianca positiva nao reduz o epsilon)
  frases de estado (2.5):    confiante (c >= limiar), inseguro (c <= -limiar), entediado do rival (as ultimas n lutas
                             com novidade <= limiar_tedio), neutro; a frase mostrada so troca depois de
                             `histerese_frase_min` na faixa nova. O "porque" aponta para as lutas do registro.

web/app/motor/confianca.ts e o espelho (mesmas formulas, mesma ordem de operacoes; gabarito de paridade em
web/app/test/gabaritos/confianca_python.json).
"""

from __future__ import annotations

import math

from .config import CONFIG_CONFIANCA, ConfigConfianca

ESTADOS = ("confiante", "inseguro", "entediado", "neutro")


# ------------------------------------------------------------------ funcoes puras
def novidade(m_antes: float, lam: float) -> float:
    """novidade de enfrentar um rival com contador de encontros `m_antes` (1.0 no primeiro encontro)"""
    if m_antes < 0.0:
        raise ValueError(f"contador de encontros negativo: {m_antes}")
    return math.exp(-lam * m_antes)


def atualizar_encontros(m: float, dt: int, tau: float) -> float:
    """contador de encontros do rival depois de mais uma luta, `dt` minutos depois da anterior contra ele"""
    if dt < 0:
        raise ValueError(f"dt negativo: {dt}")
    return m * math.exp(-dt / tau) + 1.0


def decair_confianca(c: float, dt: int, tau: float) -> float:
    """a confianca decai para 0 com o tempo de jogo sem lutar"""
    if dt < 0:
        raise ValueError(f"dt negativo: {dt}")
    return c * math.exp(-dt / tau)


def atualizar_confianca(c: float, dt: int, sinal: int, nov: float, sensibilidade: float,
                        cfg: ConfigConfianca = CONFIG_CONFIANCA) -> float:
    """confianca depois de uma luta `dt` minutos depois da ultima (sinal +1 vitoria, -1 derrota, 0 empate)"""
    if sinal not in (-1, 0, 1):
        raise ValueError(f"sinal da luta invalido: {sinal!r}")
    if not -1.0 <= sensibilidade <= 1.0:
        raise ValueError(f"sensibilidade fora de [-1, 1]: {sensibilidade}")
    c = decair_confianca(c, dt, cfg.tau_confianca_min)
    eta = cfg.eta_confianca * (1.0 + cfg.k_sensibilidade * sensibilidade) if sinal < 0 else cfg.eta_confianca
    return max(-1.0, min(1.0, c + eta * nov * sinal))


def epsilon_confianca(c: float, kappa: float) -> float:
    """termo da insegura no epsilon do lutador do pet: kappa * max(0, -c)"""
    if not -1.0 <= c <= 1.0:
        raise ValueError(f"confianca fora de [-1, 1]: {c}")
    return kappa * max(0.0, -c)


def faixa(c: float, novidades: tuple, cfg: ConfigConfianca = CONFIG_CONFIANCA) -> str:
    """faixa bruta (sem histerese): confiante e inseguro pela confianca; entediado pelas ultimas n lutas"""
    if c >= cfg.limiar_frase:
        return "confiante"
    if c <= -cfg.limiar_frase:
        return "inseguro"
    if len(novidades) >= cfg.n_tedio and all(n <= cfg.limiar_tedio for n in novidades[-cfg.n_tedio:]):
        return "entediado"
    return "neutro"


def tick_saida_faixa(tick: int, c: float, cfg: ConfigConfianca = CONFIG_CONFIANCA) -> int | None:
    """primeiro tick em que |c| decaido fica abaixo do limiar da frase (None se ja esta abaixo)"""
    if abs(c) < cfg.limiar_frase:
        return None
    return tick + math.ceil(cfg.tau_confianca_min * math.log(abs(c) / cfg.limiar_frase))


# ------------------------------------------------------------------ o estado
class ConfiancaCombate:
    """Contadores de encontros por rival (com o ultimo tick de cada um), a confianca `c` e o tick da ultima luta.
    `historico` guarda cada luta (tick, rival, sinal, novidade, c depois): e o que as frases citam."""

    def __init__(self, cfg: ConfigConfianca = CONFIG_CONFIANCA) -> None:
        self.cfg = cfg
        self.encontros: dict[str, float] = {}
        self.ultimo_tick: dict[str, int] = {}
        self.c = 0.0
        self.tick_c: int | None = None
        self.historico: list[dict] = []

    def novidade_de(self, rival: str, tick: int) -> float:
        """novidade que uma luta contra `rival` no tick teria (sem registrar)"""
        return novidade(self._encontros_em(rival, tick), self.cfg.lambda_novidade)

    def _encontros_em(self, rival: str, tick: int) -> float:
        if rival not in self.encontros:
            return 0.0
        return self.encontros[rival] * math.exp(-(tick - self.ultimo_tick[rival]) / self.cfg.tau_habituacao_min)

    def valor(self, tick: int) -> float:
        """a confianca no tick (decaida desde a ultima luta), sem mudar o estado"""
        if self.tick_c is None:
            return self.c
        return decair_confianca(self.c, tick - self.tick_c, self.cfg.tau_confianca_min)

    def registrar(self, tick: int, rival: str, sinal: int, sensibilidade: float) -> dict:
        """uma luta: novidade pelo contador do rival, confianca decaida e empurrada. Devolve {novidade, c}."""
        if self.tick_c is not None and tick < self.tick_c:
            raise ValueError(f"luta no tick {tick} antes da ultima ({self.tick_c})")
        m_antes = self._encontros_em(rival, tick)
        nov = novidade(m_antes, self.cfg.lambda_novidade)
        dt = 0 if self.tick_c is None else tick - self.tick_c
        self.c = atualizar_confianca(self.c, dt, sinal, nov, sensibilidade, self.cfg)
        self.tick_c = tick
        # o contador decai desde a ultima luta contra ESTE rival (m_antes ja esta decaido) e soma 1
        self.encontros[rival] = m_antes + 1.0
        self.ultimo_tick[rival] = tick
        self.historico.append({"tick": tick, "rival": rival, "sinal": sinal, "novidade": nov, "c": self.c})
        return {"novidade": nov, "c": self.c}

    def para_dict(self) -> dict:
        return {"c": self.c, "tick_c": self.tick_c, "encontros": dict(self.encontros), "ultimo_tick": dict(self.ultimo_tick),
                "lutas": len(self.historico)}

    # -------------------------------------------------------------- frases de estado (2.5)
    def _intervalos(self, tick: int) -> list[tuple[int, int, str]]:
        """[(inicio, fim, faixa)] das faixas brutas ao longo do tempo ate `tick`, ja com as iguais juntadas"""
        cfg = self.cfg
        brutos: list[tuple[int, str]] = []
        h = self.historico
        for i, x in enumerate(h):
            novs = tuple(y["novidade"] for y in h[max(0, i + 1 - cfg.n_tedio):i + 1])
            fim = h[i + 1]["tick"] if i + 1 < len(h) else tick
            f = faixa(x["c"], novs, cfg)
            brutos.append((x["tick"], f))
            if f in ("confiante", "inseguro"):
                sai = tick_saida_faixa(x["tick"], x["c"], cfg)
                if sai is not None and sai < fim:
                    brutos.append((sai, faixa(0.0, novs, cfg)))
        saida: list[tuple[int, int, str]] = []
        for k, (ini, f) in enumerate(brutos):
            fim = brutos[k + 1][0] if k + 1 < len(brutos) else tick
            if fim <= ini:
                continue
            if saida and saida[-1][2] == f:
                saida[-1] = (saida[-1][0], fim, f)
            else:
                saida.append((ini, fim, f))
        return saida

    def estado(self, tick: int) -> dict:
        """a frase de estado mostrada no tick, com histerese: {estado, desde, c, lutas (ticks das lutas da causa)}"""
        if self.tick_c is not None and tick < self.tick_c:
            raise ValueError(f"tick {tick} antes da ultima luta ({self.tick_c})")
        mostrada, desde = "neutro", None
        for ini, fim, f in self._intervalos(tick):
            if f != mostrada and fim - ini >= self.cfg.histerese_frase_min:
                mostrada, desde = f, ini + self.cfg.histerese_frase_min
        return {"estado": mostrada, "desde": desde, "c": self.valor(tick), "lutas": self._causa(mostrada)}

    def _causa(self, estado: str) -> list[int]:
        """ticks das lutas do registro que puseram o pet no estado (do mais recente ao mais antigo)"""
        h = self.historico
        if estado == "entediado":
            return [x["tick"] for x in reversed(h[-self.cfg.n_tedio:])]
        if estado == "neutro":
            return []
        sinal = 1 if estado == "confiante" else -1
        lutas = []
        for x in reversed(h):
            if x["c"] * sinal <= 0.0:
                break
            if x["sinal"] == sinal:
                lutas.append(x["tick"])
        return lutas
