"""Treino, fadiga, forcar e sobrecarga (docs/TAREFA_TREINO_SOMBRIO.md, secoes 1 e 2).

Estado proprio do pet (barreira 2: nada disto entra em CondicaoFisica nem no Estado do
motor). Sem rng (barreira 4): ganho, fadiga e sobrecarga sao contas deterministicas; a
unica aleatoriedade (o pet "enrolar") e a obediencia, sorteada fora daqui na
rng_obediencia do MotorPersonalidade. Funcao pura dos eventos: o MotorTreino chama
`avancar` em cada decisao do pet e antes de cada sessao, com o estado do motor naquele
tick; o replay repete as mesmas chamadas.

Regras (dados em ConfigTreino, de docs/pve_treino.json):
  ganho = ganho_base * aptidao_especie[stat] * (1 - pontos_no_stat / teto_por_stat) * m
          m = 1 - fadiga/100 (normal) ou mult_forcar (fadiga >= limite_forcar: forcar_treino)
          cortado pelos tetos: por stat, pelo total do estagio e pelo total da vida
  fadiga +20 por sessao (tambem na forcada; cap 100); recupera acordado (10/h); zera ao dormir
  forcar: sobrecarga +15, estresse +10 (o -0,05 de vinculo e aplicado pelo motor)
  enrolar (obediencia contra): sessao sem ganho e sem fadiga; se era forcada, os custos entram
  sobrecarga em [0, 100]: decai 2/h acordado com as necessidades atendidas e 10 por sono
          completo (>= sono_completo_ticks); NAO zera na evolucao
  evolucao (troca de estagio): fadiga e estresse zeram; pontos e sobrecarga ficam
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .config import CONFIG_EVOLUCAO_PESQUISA, CONFIG_TREINO, STATS_V21, ConfigEvolucaoPesquisa, ConfigTreino


class TreinoInvalido(ValueError):
    pass


class ToqueRejeitado(TreinoInvalido):
    """Sessao antes do intervalo minimo: o canal nao deixa chegar ao motor (nao consome orcamento)."""


def estagio_no_tick(tick: int, cfg: ConfigEvolucaoPesquisa | None = None) -> str:
    cfg = cfg or CONFIG_EVOLUCAO_PESQUISA
    if tick < 0:
        raise TreinoInvalido(f"tick negativo: {tick}")
    if tick < cfg.dur_bebe_min:
        return "bebe"
    if tick < cfg.dur_bebe_min + cfg.dur_crianca_min:
        return "crianca"
    if tick < cfg.dur_bebe_min + cfg.dur_crianca_min + cfg.dur_adolescente_min:
        return "adolescente"
    return "adulto"


@dataclass(frozen=True)
class Sessao:
    tick: int
    exercicio: str
    estagio: str
    forcada: bool
    enrolou: bool
    fadiga_antes: float
    ganho: dict = field(default_factory=dict)

    def para_dict(self) -> dict:
        return {"tick": self.tick, "exercicio": self.exercicio, "estagio": self.estagio, "forcada": self.forcada,
                "enrolou": self.enrolou, "fadiga_antes": self.fadiga_antes, "ganho": dict(self.ganho)}


class TreinoPet:
    def __init__(self, especie: str, cfg: ConfigTreino | None = None, cfg_evo: ConfigEvolucaoPesquisa | None = None):
        self.cfg = cfg or CONFIG_TREINO
        self.cfg_evo = cfg_evo or CONFIG_EVOLUCAO_PESQUISA
        if especie not in self.cfg.aptidao_especie:
            raise TreinoInvalido(f"especie sem aptidao de treino: {especie!r}")
        for ex, (pri, sec) in self.cfg.exercicios.items():
            if pri not in STATS_V21 or sec not in STATS_V21:
                raise TreinoInvalido(f"exercicio {ex!r} com stat desconhecido")
        self.especie = especie
        self.pontos = {k: 0.0 for k in STATS_V21}
        self.pontos_estagio = {e: 0.0 for e in self.cfg.teto_por_estagio}
        self.fadiga = 0.0
        self.sobrecarga = 0.0
        self.estresse = 0.0
        self.tick = 0
        self.estagio = estagio_no_tick(0, self.cfg_evo)
        self.dormindo = False
        self.inicio_sono: int | None = None
        self.bem_cuidado = True
        self.ultimo_toque: int | None = None
        self.sessoes: list[Sessao] = []

    # ------------------------------------------------------------ tempo
    def avancar(self, tick: int, dormindo: bool, bem_cuidado: bool) -> None:
        """Integra de self.tick ate `tick` com o estado ANTERIOR (sono e cuidado); depois aplica a
        troca de estagio e as transicoes de sono que valem a partir de `tick`."""
        if tick < self.tick:
            raise TreinoInvalido(f"tempo voltou: {tick} < {self.tick}")
        c = self.cfg
        dt = tick - self.tick
        if dt and not self.dormindo:
            self.fadiga = max(0.0, self.fadiga - c.recupera_fadiga_por_hora * dt / 60.0)
            if self.bem_cuidado:
                self.sobrecarga = max(0.0, self.sobrecarga - c.decai_sobrecarga_hora_bem_cuidado * dt / 60.0)
        self.tick = tick
        est = estagio_no_tick(tick, self.cfg_evo)
        if est != self.estagio:                       # evolucao: contadores zeram, sobrecarga fica
            self.estagio = est
            self.fadiga = 0.0
            self.estresse = 0.0
        if dormindo and not self.dormindo:
            self.fadiga = 0.0
            self.inicio_sono = tick
        elif not dormindo and self.dormindo:
            if self.inicio_sono is not None and tick - self.inicio_sono >= c.sono_completo_ticks:
                self.sobrecarga = max(0.0, self.sobrecarga - c.decai_sobrecarga_sono_completo)
            self.inicio_sono = None
        self.dormindo = dormindo
        self.bem_cuidado = bem_cuidado

    # ------------------------------------------------------------ leitura
    def pode_tocar(self, tick: int) -> bool:
        return self.ultimo_toque is None or tick - self.ultimo_toque >= self.cfg.intervalo_minimo_ticks

    @property
    def forcaria(self) -> bool:
        return self.fadiga >= self.cfg.limite_forcar

    @property
    def pede_pausa(self) -> bool:
        return self.fadiga >= self.cfg.limiar_pausa

    @property
    def total(self) -> float:
        return sum(self.pontos.values())

    # ------------------------------------------------------------ sessao
    def sessao(self, tick: int, exercicio: str, obedece: bool) -> Sessao:
        c = self.cfg
        if tick != self.tick:
            raise TreinoInvalido(f"sessao no tick {tick} sem avancar o treino ate ele ({self.tick})")
        if exercicio not in c.exercicios:
            raise TreinoInvalido(f"exercicio desconhecido: {exercicio!r}")
        if self.estagio not in c.teto_por_estagio:
            raise TreinoInvalido(f"{self.estagio} nao treina")
        if not self.pode_tocar(tick):
            raise ToqueRejeitado(f"sessao no tick {tick}: intervalo minimo desde {self.ultimo_toque}")
        forcada = self.forcaria
        fadiga_antes = self.fadiga
        self.ultimo_toque = tick
        if forcada:
            self.sobrecarga = min(c.sobrecarga_max, self.sobrecarga + c.sobrecarga_forcar)
            self.estresse += c.estresse_forcar
        if not obedece:
            s = Sessao(tick, exercicio, self.estagio, forcada, True, fadiga_antes)
            self.sessoes.append(s)
            return s
        mult = c.mult_forcar if forcada else 1.0 - self.fadiga / 100.0
        apt = c.aptidao_especie[self.especie]
        ganho = {}
        pri, sec = c.exercicios[exercicio]
        for stat, base in ((pri, c.ganho_principal), (sec, c.ganho_secundario)):
            g = base * apt[stat] * (1.0 - self.pontos[stat] / c.teto_por_stat) * mult
            g = min(g, c.teto_por_stat - self.pontos[stat],
                    c.teto_por_estagio[self.estagio] - self.pontos_estagio[self.estagio], c.teto_vida - self.total)
            g = max(0.0, g)
            self.pontos[stat] += g
            self.pontos_estagio[self.estagio] += g
            ganho[stat] = g
        self.fadiga = min(100.0, self.fadiga + c.fadiga_por_sessao)
        s = Sessao(tick, exercicio, self.estagio, forcada, False, fadiga_antes, ganho)
        self.sessoes.append(s)
        return s

    def para_dict(self) -> dict:
        return {"especie": self.especie, "pontos": dict(self.pontos), "pontos_estagio": dict(self.pontos_estagio),
                "total": self.total, "fadiga": self.fadiga, "sobrecarga": self.sobrecarga, "estresse": self.estresse,
                "sessoes": len(self.sessoes), "forcadas": sum(s.forcada for s in self.sessoes),
                "enroladas": sum(s.enrolou for s in self.sessoes)}
