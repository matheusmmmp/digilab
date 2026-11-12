"""A TV do mundo (V3, GOSTO_VISUAL, P1c; docs/ESPEC_GOSTO_VISUAL_P1.md, secoes 1.1 e 1.2; a ConfigTV, desligada por padrao).

Componente puro: nao sabe de pet nem de corpo. O `Mundo` (digilab/mundo.py) e dono de uma `TV` quando o motor liga a ConfigTV; o motor
pergunta o que ela passa num tick (`em(tick)`) e decide se o pet olha.

A fonte "grade" (a TV do jogo, a unica da pesquisa; GV-20): na construcao, a rng propria `tv-programas` (derivar_semente com a semente do
mundo; nenhum outro fluxo muda) sorteia os `n_programas` perfis, sete inteiros uniformes em [0, escala] cada, na ordem de CANAIS_TELA. Depois
ela sorteia a grade, um programa por vez, na ordem do tempo: o primeiro uniforme entre os programas e cada seguinte um outro (nunca o mesmo),
a duracao uniforme em [programa_min_ticks, programa_max_ticks] e, para cada cena de `cena_ticks`, um deslocamento por canal uniforme em
[-variacao, variacao]. A grade so depende da semente: e estendida ate o tick perguntado, sempre na mesma ordem, entao o mesmo tick da o
mesmo programa nao importa quem pergunta nem quando. No tick t, cada canal e o perfil do programa mais o deslocamento da cena, cortado em
[0, escala]. O dono troca o canal (`trocar_canal`, o evento do log): o programa escolhido passa no lugar do da grade ate o fim do programa
da grade (as cenas sao as da grade; a grade nao muda nem consome sorteio).

A fonte "evento" (o modo livre gravado, secao 1.2): o que a TV passa e o ultimo `sentido_tela` ate o tick, cada nivel n em [0, 15] vira
div_arred(n x escala, 15); sem nenhum, a TV esta desligada (`em` da None). A grade nao existe e nada se sorteia. A TV desligada de novo (a
decisao A da captura ligada ao cerebro, D-GV-TVJOGO-1; o motor confere a ConfigTVJogo.desligar): o `sentido_tela` `fonte|desligada` (os
niveis None) a desliga ate o proximo.

`ResumoTela` e o resumo do GV-15, do lado de quem grava o evento (o P0 no jogo, na P1f): a media de cada janela de `janela` amostras (uma
por segundo real; o padrao e ConfigTV.janela_resumo_s, 10) em 16 niveis por canal, e o evento so quando algum nivel muda.
"""

from __future__ import annotations

import bisect
import math
import random

from .config import CONFIG_TV, ConfigTV
from .corpo import CANAIS_TELA, div_arred
from .events import FONTES_SENTIDO_TELA, N_CANAIS_TELA, NIVEL_MAX_TELA, Evento, sentido_tela
from .protocol import derivar_semente

if len(CANAIS_TELA) != N_CANAIS_TELA:                  # pragma: no cover - conferido na carga
    raise RuntimeError("os canais da tela do corpo e o formato do evento sentido_tela divergem")

# o id da TV do Mundo (uma so por mundo, na P1d) nas linhas da classe `tela` que o motor entrega ao cerebro (`ver_tela`) e no `olhando_tela`
ID_TV = 1
# os ids das duas TVs da sonda (P1e; `MotorMundo.ligar_duas_tvs`): o perfil A na 2 e o B na 3; nenhum e o da TV da vida, entao o cerebro nao
# traz para a sonda o `gosto` da TV que ele olhava antes
IDS_DUAS_TVS = (2, 3)


class TVSemChave(ValueError):
    """A TV (trocar_canal, sentido_tela) sem a ConfigTV ligada, com a fonte errada, sem o mundo ou no grupo."""


class DuasTVsSemLugar(RuntimeError):
    """As duas TVs da sonda (`MotorMundo.ligar_duas_tvs`) nao cabem em nenhuma das direcoes tentadas a partir do pet (a D-GV-P1e-3). E um
    RuntimeError, como antes do adendo 2 da GV3b (D-GV-GV3B2): quem nao trata o caso falha alto como falhava; a sonda com a regra
    "sem_sonda" (docs/PLANO_ANALISE_V3_GOSTO_VISUAL_ADENDO2.md) trata so esta classe. Leva o pet e a direcao sorteada."""

    def __init__(self, mensagem: str, pet: tuple, direcao_sorteada: int) -> None:
        super().__init__(mensagem)
        self.pet = tuple(pet)
        self.direcao_sorteada = direcao_sorteada


def intensidades_dos_niveis(niveis: tuple[int, ...], escala: int) -> dict[str, int]:
    """os sete niveis do evento (0 a 15) na escala do corpo: div_arred(n x escala, 15)"""
    return {c: div_arred(n * escala, NIVEL_MAX_TELA) for c, n in zip(CANAIS_TELA, niveis)}


class TV:
    """A TV de um Mundo: a posicao (o centro da celula), a fonte, a grade (so na fonte "grade") e os registros (as trocas de canal e os
    sentidos gravados), derivados: o replay os refaz pelo log."""

    def __init__(self, cfg: ConfigTV, semente: int, x: int, y: int) -> None:
        if not isinstance(cfg, ConfigTV) or not cfg.ligada:
            raise TVSemChave(f"a TV precisa da ConfigTV ligada: {cfg!r}")
        self.cfg = cfg
        self.x, self.y = x, y
        self.trocas_canal: list[dict] = []
        self.sentidos: list[dict] = []
        self._sentido: tuple[str, tuple[int, ...]] | None = None
        self.rng: random.Random | None = None
        self.programas: tuple[tuple[int, ...], ...] = ()
        self.grade: list[dict] = []                    # os programas da grade ja sorteados: inicio, fim, programa, cenas
        self._inicios: list[int] = []
        self._dono: dict | None = None                 # o canal do dono: {"segmento", "programa"}, ate o fim daquele programa da grade
        if cfg.fonte == "grade":
            r = self.rng = random.Random(derivar_semente("tv-programas", semente))
            self.programas = tuple(tuple(r.randint(0, cfg.escala) for _ in CANAIS_TELA) for _ in range(cfg.n_programas))

    # ------------------------------------------------------------ a grade
    def _estender(self, tick: int) -> None:
        cfg, r, g = self.cfg, self.rng, self.grade
        while not g or g[-1]["fim"] <= tick:
            inicio = g[-1]["fim"] if g else 0
            n = cfg.n_programas
            p = r.randrange(n) if not g else (g[-1]["programa"] + 1 + r.randrange(n - 1)) % n
            dur = r.randint(cfg.programa_min_ticks, cfg.programa_max_ticks)
            v = cfg.variacao
            cenas = tuple(tuple(r.randint(-v, v) for _ in CANAIS_TELA) for _ in range(-(-dur // cfg.cena_ticks)))
            g.append({"inicio": inicio, "fim": inicio + dur, "programa": p, "cenas": cenas})
            self._inicios.append(inicio)

    def _segmento(self, tick: int) -> int:
        if type(tick) is not int or tick < 0:
            raise ValueError(f"tick da TV inteiro >= 0: {tick!r}")
        self._estender(tick)
        return bisect.bisect_right(self._inicios, tick) - 1

    def programa_em(self, tick: int) -> int | None:
        """o programa que passa no tick (o do dono, se ele trocou o canal neste programa da grade); None fora da fonte "grade" """
        if self.cfg.fonte != "grade":
            return None
        i = self._segmento(tick)
        d = self._dono
        return d["programa"] if d is not None and d["segmento"] == i else self.grade[i]["programa"]

    def em(self, tick: int) -> dict[str, int] | None:
        """o que a TV passa no tick, um inteiro em [0, escala] por canal (na ordem de CANAIS_TELA); None com a TV desligada (a fonte
        "evento" antes do primeiro sentido_tela)"""
        cfg = self.cfg
        if cfg.fonte == "evento":
            return None if self._sentido is None else intensidades_dos_niveis(self._sentido[1], cfg.escala)
        i = self._segmento(tick)
        seg = self.grade[i]
        d = self._dono
        perfil = self.programas[d["programa"] if d is not None and d["segmento"] == i else seg["programa"]]
        cena = seg["cenas"][(tick - seg["inicio"]) // cfg.cena_ticks]
        return {c: min(cfg.escala, max(0, p + o)) for c, p, o in zip(CANAIS_TELA, perfil, cena)}

    # ------------------------------------------------------------ os eventos
    def trocar_canal(self, programa: int, tick: int) -> dict:
        """o dono poe o programa `programa` (so na fonte "grade"); vale ate o fim do programa da grade que passa no tick"""
        if self.cfg.fonte != "grade":
            raise TVSemChave(f"trocar_canal com a fonte {self.cfg.fonte!r}: o canal so existe na TV do jogo (a fonte \"grade\")")
        if type(programa) is not int or not 0 <= programa < self.cfg.n_programas:
            raise ValueError(f"trocar_canal para um programa que nao existe (0 a {self.cfg.n_programas - 1}): {programa!r}")
        antes = self.programa_em(tick)
        i = self._segmento(tick)
        self._dono = {"segmento": i, "programa": programa}
        reg = {"tick": tick, "programa": programa, "antes": antes, "ate": self.grade[i]["fim"]}
        self.trocas_canal.append(reg)
        return reg

    def sentir(self, fonte: str, niveis: tuple[int, ...] | None, tick: int) -> None:
        """o modo livre gravado (so na fonte "evento"): a partir do tick, a TV passa estes niveis; None, a TV desligada (a decisao A,
        D-GV-TVJOGO-1: `em` volta a dar None; quem confere a chave e o motor)"""
        if self.cfg.fonte != "evento":
            raise TVSemChave(f"sentido_tela com a fonte {self.cfg.fonte!r}: o modo livre gravado e a fonte \"evento\"")
        if fonte not in FONTES_SENTIDO_TELA:
            raise ValueError(f"fonte do sentido_tela em {FONTES_SENTIDO_TELA}: {fonte!r}")
        self._sentido = None if niveis is None else (fonte, tuple(niveis))
        self.sentidos.append({"tick": tick, "fonte": fonte, "niveis": None if niveis is None else list(niveis)})

    def resumo(self) -> dict:
        return {"x": self.x, "y": self.y, "fonte": self.cfg.fonte, "trocas_canal": [dict(t) for t in self.trocas_canal],
                "sentidos": [dict(s) for s in self.sentidos]}


class TVFixa:
    """Uma das duas TVs da sonda (P1e; docs/ESPEC_GOSTO_VISUAL_P1.md, secao 7): passa sempre o mesmo perfil, sete inteiros em [0, escala] na
    ordem de CANAIS_TELA. Sem grade, sem cena, sem rng e sem evento: so existe na copia do pet que a sonda faz (`MotorMundo.ligar_duas_tvs`)."""

    def __init__(self, perfil: tuple[int, ...], escala: int, x: int, y: int) -> None:
        perfil = tuple(perfil)
        if len(perfil) != len(CANAIS_TELA) or any(type(v) is not int or not 0 <= v <= escala for v in perfil):
            raise ValueError(f"o perfil da TV da sonda: {len(CANAIS_TELA)} inteiros em [0, {escala}]: {perfil!r}")
        self.perfil, self.escala, self.x, self.y = perfil, escala, x, y

    def em(self, tick: int) -> dict[str, int]:
        if type(tick) is not int or tick < 0:
            raise ValueError(f"tick da TV inteiro >= 0: {tick!r}")
        return dict(zip(CANAIS_TELA, self.perfil))

    def programa_em(self, tick: int) -> None:
        return None

    def resumo(self) -> dict:
        return {"x": self.x, "y": self.y, "fonte": "fixa", "perfil": list(self.perfil)}


# ================================================================== o resumo do GV-15 (quem grava o evento)
def nivel_da_media(amostras: list[float]) -> int:
    """a media de uma janela de amostras em [0, 1] num dos 16 niveis: floor(media x 15 + 1/2) (o Math.round do TS para positivos)"""
    if not amostras:
        raise ValueError("janela da tela sem amostras")
    for a in amostras:
        if type(a) not in (int, float) or not 0.0 <= a <= 1.0 or math.isnan(a):
            raise ValueError(f"amostra da tela fora de [0, 1]: {a!r}")
    return min(NIVEL_MAX_TELA, int(math.floor(sum(amostras) / len(amostras) * NIVEL_MAX_TELA + 0.5)))


class ResumoTela:
    """GV-15: recebe um vetor por segundo real (sete numeros em [0, 1], na ordem de CANAIS_TELA) e, a cada `janela` vetores, a media em 16
    niveis; devolve o evento `sentido_tela` so quando algum nivel muda (o primeiro sempre). O tick do evento e o de quem fecha a janela."""

    def __init__(self, fonte: str, janela: int = CONFIG_TV.janela_resumo_s) -> None:
        if fonte not in FONTES_SENTIDO_TELA:
            raise ValueError(f"fonte do sentido_tela em {FONTES_SENTIDO_TELA}: {fonte!r}")
        if type(janela) is not int or janela < 1:
            raise ValueError(f"janela do resumo inteira >= 1: {janela!r}")
        self.fonte, self.janela = fonte, janela
        self._amostras: list[tuple[float, ...]] = []
        self.ultimo: tuple[int, ...] | None = None

    def amostra(self, tick: int, vetor) -> Evento | None:
        if len(vetor) != N_CANAIS_TELA:
            raise ValueError(f"o vetor da tela tem {N_CANAIS_TELA} canais, veio {len(vetor)}")
        self._amostras.append(tuple(vetor))
        if len(self._amostras) < self.janela:
            return None
        niveis = tuple(nivel_da_media([a[k] for a in self._amostras]) for k in range(N_CANAIS_TELA))
        self._amostras = []
        if niveis == self.ultimo:
            return None
        self.ultimo = niveis
        return sentido_tela(tick, self.fonte, niveis)
