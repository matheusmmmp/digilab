"""Evolucao do pet de pesquisa ate a forma adulta do combate V2.1.

docs/ESPEC_EVOLUCAO_COMBATE.md, secao Pesquisa. Tudo e funcao pura do log de
uma vida ja gravada (nada aqui roda vida nova nem mexe em engine.py):

  ovo (semente da coorte)      especie e temperamento; IGUAIS em todos os bracos (ovos pareados)
  bebe -> crianca (180 min)    cuidado = fracao dos chamados do bebe atendidos na janela
  crianca -> adolescente (900) linha = eixo dominante do carater
  adolescente -> adulto (1980) forma = sinal do eixo complementar (sparring: cumprido na simulacao)

Carater (catalogo_pets.json): desvio da politica APRENDIDA em relacao ao instinto,
num conjunto FIXO de estados-sonda (os mesmos da metrica de divergencia). A base da
comparacao e a MESMA politica recem-nascida (bandit sem nenhuma atualizacao), nao o
instinto puro: o bandit novo ja difere do instinto pelo ruido de Thompson (na semente
101, "paciente" saia -0,8 a -1,0 em TODOS os donos contra o instinto), e isso nao e
aprendizado. Para cada acao do pet, media sobre as sondas de p_politica(a) - p_base(a); cada acao vai
para o traco de combate de ConfigArena.mapa_pet_combate e cada eixo junta seus
tracos (ConfigEvolucaoPesquisa.eixo_traco). A politica e a do tick da transicao:
o log e rejogado so ate ali.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Callable

from .combate_v2.v21.catalogo import Forma, forma_adulta, linha_do_adolescente, ramo_da_crianca
from .config import CONFIG_ARENA, CONFIG_CATALOGO, CONFIG_EVOLUCAO_PESQUISA, CONFIG_PADRAO, ConfigEvolucaoPesquisa
from .events import AcaoUsuario, LogDeEventos
from .metrics import distribuicoes_de_acao, estados_sonda
from .protocol import derivar_semente


def ovo(semente: int, cfg: ConfigEvolucaoPesquisa | None = None) -> tuple[str, dict]:
    """(especie, temperamento) do ovo da semente da coorte: o mesmo em todos os bracos."""
    cfg = cfg or CONFIG_EVOLUCAO_PESQUISA
    rng = random.Random(derivar_semente("ovo-v21", semente))
    especie = CONFIG_CATALOGO.especies_ativas[rng.randrange(len(CONFIG_CATALOGO.especies_ativas))]
    a = cfg.amplitude_temperamento
    temperamento = {eixo: rng.uniform(-a, a) for eixo in CONFIG_CATALOGO.temperamento}
    return especie, temperamento


def fracao_cuidado_bebe(log: LogDeEventos, cfg: ConfigEvolucaoPesquisa | None = None) -> tuple[float, int, int]:
    """(fracao, atendidos, chamados). Chamados em horario fixo (cronograma); atendido se o dono
    faz uma das acoes do tipo dentro da janela, sem reaproveitar a mesma acao para dois chamados."""
    cfg = cfg or CONFIG_EVOLUCAO_PESQUISA
    acoes = [(e.tick, str(e.valor)) for e in log if e.tipo == "acao_usuario" and e.tick < cfg.dur_bebe_min
             + cfg.janela_chamado_min]
    usadas: set[int] = set()
    chamados = sorted((t, tipo) for tipo, iv in cfg.chamados_bebe_min.items()
                      for t in range(iv, cfg.dur_bebe_min, iv))
    atendidos = 0
    for t, tipo in chamados:
        for i, (ta, a) in enumerate(acoes):
            if i not in usadas and t <= ta <= t + cfg.janela_chamado_min and a in cfg.atende[tipo]:
                usadas.add(i)
                atendidos += 1
                break
    return (atendidos / len(chamados) if chamados else 1.0), atendidos, len(chamados)


def politica_no_tick(log: LogDeEventos, fabrica: Callable, semente: int, tick: int):
    """Rejoga o log so ate `tick` (corta o avanco que o atravessa) e devolve a politica ali."""
    from .treino import MotorComFeedback

    motor = MotorComFeedback(politica=fabrica(CONFIG_PADRAO), cfg=CONFIG_PADRAO, semente=semente)
    for e in log:
        if e.tick >= tick:
            break
        if e.tipo == "avanco":
            motor._avancar(min(int(e.valor), tick - e.tick))
        elif e.tipo == "acao_usuario":
            motor._aplicar_acao_usuario(AcaoUsuario(e.valor))
        else:
            raise ValueError(f"tipo de evento desconhecido no log: {e.tipo!r}")
    return motor.politica


def carater(politica, base, n_estados: int, amostras: int, semente_sonda: int,
            cfg: ConfigEvolucaoPesquisa | None = None) -> tuple[dict, dict]:
    """(carater por eixo em [-1, 1], desvio bruto por eixo) de `politica` contra `base`
    (a mesma politica sem aprendizado), com numeros aleatorios comuns."""
    cfg = cfg or CONFIG_EVOLUCAO_PESQUISA
    estados = estados_sonda(n_estados, semente_sonda)
    dp = distribuicoes_de_acao(politica, estados, amostras, semente_sonda)
    di = distribuicoes_de_acao(base, estados, amostras, semente_sonda)
    mapa = dict(CONFIG_ARENA.mapa_pet_combate)
    por_traco: dict[str, float] = {}
    for a, traco in mapa.items():
        desvio = sum(p[a] - q[a] for p, q in zip(dp, di)) / len(estados)
        por_traco[traco] = por_traco.get(traco, 0.0) + desvio
    bruto = {eixo: sum(por_traco[t] for t in ts) / len(ts) for eixo, ts in cfg.eixo_traco.items()}
    return {e: max(-1.0, min(1.0, v / cfg.escala_carater)) for e, v in bruto.items()}, bruto


@dataclass(frozen=True)
class Evolucao:
    especie: str
    temperamento: dict
    cuidado: float
    chamados: tuple[int, int]             # (atendidos, total)
    carater_adolescente: dict              # medido ao fim da crianca: decide a linha
    carater_adulto: dict                   # medido ao fim do adolescente: decide a forma e os stats
    desvio_bruto_adulto: dict
    forma: Forma
    condicao: float
    saude_final: float = field(default=1.0)

    def para_dict(self) -> dict:
        f = self.forma
        return {"especie": self.especie, "temperamento": self.temperamento, "cuidado": self.cuidado,
                "chamados_atendidos": self.chamados[0], "chamados": self.chamados[1],
                "carater_adolescente": self.carater_adolescente, "carater_adulto": self.carater_adulto,
                "desvio_bruto_adulto": self.desvio_bruto_adulto,
                "forma": {"ramo": f.ramo, "linha": f.linha, "adulta": f.adulta, "rotulo": f.rotulo},
                "condicao": self.condicao, "saude_final": self.saude_final}


def evoluir(log: LogDeEventos, fabrica: Callable, semente: int, n_estados: int, amostras: int,
            semente_sonda: int, saude_final: float, cfg: ConfigEvolucaoPesquisa | None = None) -> Evolucao:
    cfg = cfg or CONFIG_EVOLUCAO_PESQUISA
    especie, temp = ovo(semente, cfg)
    frac, atend, tot = fracao_cuidado_bebe(log, cfg)
    ramo = ramo_da_crianca(frac)
    t_adol = cfg.dur_bebe_min + cfg.dur_crianca_min
    t_adul = t_adol + cfg.dur_adolescente_min
    dist_base = fabrica(CONFIG_PADRAO)            # mesma politica, recem-nascida (sem aprendizado)
    car_adol, _ = carater(politica_no_tick(log, fabrica, semente, t_adol), dist_base, n_estados, amostras,
                          semente_sonda, cfg)
    linha = linha_do_adolescente(car_adol)
    car_adul, bruto = carater(politica_no_tick(log, fabrica, semente, t_adul), fabrica(CONFIG_PADRAO), n_estados,
                              amostras, semente_sonda, cfg)
    adulta = forma_adulta(linha, car_adul, cfg.sparring_simulado)
    if adulta is None:
        raise ValueError("sparring simulado abaixo do minimo: o pet nao chegaria a adulto")
    cat = CONFIG_CATALOGO
    condicao = cat.condicao_mult_min + (cat.condicao_mult_max - cat.condicao_mult_min) * max(0.0, min(1.0, saude_final))
    return Evolucao(especie, temp, frac, (atend, tot), car_adol, car_adul, bruto,
                    Forma(especie, "adulto", ramo, linha, adulta), condicao, saude_final)
