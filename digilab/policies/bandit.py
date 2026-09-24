"""Bandit contextual linear com Thompson sampling (Etapa 3).

Implementa o `Protocol` `Politica` do v0 sem tocar em engine.py.

Decisao
-------
Para cada acao a, com contexto x (features da Observacao):

    score(a) = log p0(a|x) + theta~_a . x + G_a

  p0      prior da PoliticaInstinto, misturado com uniforme (piso_prior)
  theta~  amostra de Thompson da posterior N(theta^_a, v2 * A_a^-1)
  G_a     ruido de Gumbel

Com theta = 0 (recem-nascido), argmax(log p0 + G) e EXATAMENTE uma amostra
de p0 (truque Gumbel-max): o pet nasce se comportando como o instinto, nao
de forma aleatoria. O aprendizado desloca as preferencias a partir dai.

Recompensa
----------
  explicita  elogiar / repreender credita a decisao mais recente
  implicita  cada chamar_atencao fica pendente; o primeiro cuidado do dono
             (alimentar, limpar, brincar, acariciar) dentro da janela paga
             1 - latencia/janela; pendente que expira paga
             recompensa_pedido_ignorado

O tick absoluto de cada decisao e reconstruido como
ticks_desde_cuidado + tick do ultimo cuidado (que a politica recebe pelo
gancho do dono). Inconsistencia levanta erro.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

from ..config import CONFIG_BANDIT, CONFIG_PADRAO, Config, ConfigBandit
from ..events import AcaoPet, AcaoUsuario
from ..policy import Observacao, PoliticaInstinto, Transicao

ACOES = tuple(AcaoPet)
CUIDADOS_QUE_ATENDEM = frozenset(
    {AcaoUsuario.ALIMENTAR, AcaoUsuario.LIMPAR, AcaoUsuario.BRINCAR, AcaoUsuario.ACARICIAR}
)
FEEDBACK = frozenset({AcaoUsuario.ELOGIAR, AcaoUsuario.REPREENDER})


# ------------------------------------------------------------ prior por sonda


class _RngSonda:
    """Substituto de random.Random que registra como a politica usa a rng.

    Permite extrair a distribuicao EXATA da PoliticaInstinto sem duplicar
    suas regras. Qualquer uso fora do previsto levanta erro.
    """

    def __init__(self, u: float) -> None:
        self.u = u
        self.chamadas_random = 0
        self.escolha: tuple[list, list] | None = None

    def random(self) -> float:
        self.chamadas_random += 1
        return self.u

    def choices(self, populacao, weights=None, k=1):
        if self.escolha is not None or k != 1 or weights is None:
            raise NotImplementedError("sonda so suporta um unico choices(k=1) ponderado")
        self.escolha = (list(populacao), list(weights))
        return [populacao[0]]

    def __getattr__(self, nome):
        raise NotImplementedError(f"sonda nao suporta rng.{nome}")


def distribuicao_instinto(instinto: PoliticaInstinto, obs: Observacao, iteracoes: int) -> dict[AcaoPet, float]:
    sonda = _RngSonda(0.0)
    a0 = instinto.agir(obs, sonda)
    if sonda.escolha is not None:
        if sonda.chamadas_random:
            raise NotImplementedError("instinto usou random() e choices() na mesma decisao")
        pop, pesos = sonda.escolha
        total = float(sum(pesos))
        dist = {a: 0.0 for a in ACOES}
        for a, w in zip(pop, pesos):
            dist[a] += w / total
        return dist
    if sonda.chamadas_random == 0:
        return {a: (1.0 if a is a0 else 0.0) for a in ACOES}
    if sonda.chamadas_random > 1:
        raise NotImplementedError("instinto chamou random() mais de uma vez")

    # um unico `rng.random() < t`: bisseccao recupera t
    fim = _RngSonda(1.0 - 1e-15)
    a1 = instinto.agir(obs, fim)
    if a1 is a0:
        return {a: (1.0 if a is a0 else 0.0) for a in ACOES}
    lo, hi = 0.0, 1.0
    for _ in range(iteracoes):
        meio = 0.5 * (lo + hi)
        if instinto.agir(obs, _RngSonda(meio)) is a0:
            lo = meio
        else:
            hi = meio
    t = 0.5 * (lo + hi)
    dist = {a: 0.0 for a in ACOES}
    dist[a0] += t
    dist[a1] += 1.0 - t
    return dist


# ------------------------------------------------------------ algebra minima


def _identidade(n: int, escala: float) -> list[list[float]]:
    return [[escala if i == j else 0.0 for j in range(n)] for i in range(n)]


def _matvec(m: list[list[float]], v: list[float]) -> list[float]:
    return [sum(mij * vj for mij, vj in zip(linha, v)) for linha in m]


def _cholesky(m: list[list[float]]) -> list[list[float]]:
    n = len(m)
    L = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            s = m[i][j] - sum(L[i][k] * L[j][k] for k in range(j))
            if i == j:
                if s <= 0.0:
                    raise ArithmeticError(f"matriz nao positiva definida (pivo {s})")
                L[i][j] = math.sqrt(s)
            else:
                L[i][j] = s / L[j][j]
    return L


# ------------------------------------------------------------------ politica


def features(obs: Observacao, cfg: ConfigBandit) -> list[float]:
    fome, higiene, energia, humor, saude, sujeira, dormindo, hora = obs.vetor_estado
    angulo = 2.0 * math.pi * hora
    return [
        1.0,
        fome,
        higiene,
        energia,
        humor,
        saude,
        sujeira,
        dormindo,
        math.sin(angulo),
        math.cos(angulo),
        min(1.0, obs.ticks_desde_cuidado / cfg.escala_ticks_desde_cuidado),
    ]


N_FEATURES = 11


@dataclass
class _Braco:
    A_inv: list[list[float]]
    b: list[float]
    n: int = 0
    _chol: list[list[float]] | None = None
    _theta: list[float] | None = None

    def theta(self) -> list[float]:
        if self._theta is None:
            self._theta = _matvec(self.A_inv, self.b)
        return self._theta

    def chol(self) -> list[list[float]]:
        if self._chol is None:
            self._chol = _cholesky(self.A_inv)
        return self._chol

    def atualizar(self, x: list[float], r: float) -> None:
        # Sherman-Morrison: (A + x x^T)^-1
        Ax = _matvec(self.A_inv, x)
        denom = 1.0 + sum(xi * axi for xi, axi in zip(x, Ax))
        d = len(x)
        for i in range(d):
            for j in range(d):
                self.A_inv[i][j] -= Ax[i] * Ax[j] / denom
        for i in range(d):
            self.b[i] += r * x[i]
        self.n += 1
        self._chol = None
        self._theta = None


class PoliticaBandit:
    """Thompson sampling linear por acao, prior no instinto. Nao altera engine.py."""

    nome = "bandit_thompson"

    def __init__(self, cfg: Config | None = None, cfg_bandit: ConfigBandit | None = None) -> None:
        self.cfg = cfg or CONFIG_PADRAO
        self.cb = cfg_bandit or CONFIG_BANDIT
        self._instinto = PoliticaInstinto(self.cfg)
        self._n_features = self.n_features()
        self._bracos = {
            a: _Braco(A_inv=_identidade(self._n_features, 1.0 / self.cb.lambda_regularizacao),
                      b=[0.0] * self._n_features)
            for a in ACOES
        }
        self._tick_ultimo_cuidado = 0
        self._tick_ultima_decisao = -1
        self._ultima: tuple[list[float], AcaoPet] | None = None
        self._pendentes: list[tuple[int, list[float]]] = []
        self._n_recompensas = {"elogio": 0, "repreensao": 0, "latencia": 0, "ignorado": 0}
        self._ultima_decisao: dict | None = None

    # ------------------------------------------------------------- features
    # Subclasses (ex.: memoria) acrescentam features sobrescrevendo os dois
    # metodos abaixo; a base e exatamente o bandit da v1.

    def n_features(self) -> int:
        return N_FEATURES

    def _features(self, obs: Observacao) -> list[float]:
        return features(obs, self.cb)

    # ------------------------------------------------------------- Politica

    @property
    def ultima_decisao(self) -> dict | None:
        """O que decidiu a ultima chamada de agir(): features x, pesos amostrados
        theta~ por acao, log(prior) e Gumbel por acao, acao escolhida. Somente
        leitura; nao entra em estado_interno() nem muda decisao (digilab.motivo)."""
        return self._ultima_decisao

    def prior(self, obs: Observacao) -> dict[AcaoPet, float]:
        p = distribuicao_instinto(self._instinto, obs, self.cb.iteracoes_bisseccao_prior)
        eps = self.cb.piso_prior
        return {a: (1.0 - eps) * p[a] + eps / len(ACOES) for a in ACOES}

    def agir(self, obs: Observacao, rng: random.Random) -> AcaoPet:
        x = self._features(obs)
        p0 = self.prior(obs)
        escala = math.sqrt(self.cb.variancia_amostra)
        melhor, melhor_score = None, -math.inf
        amostras, log_prior, gumbels = {}, {}, {}
        for a in ACOES:
            braco = self._bracos[a]
            theta = braco.theta()
            L = braco.chol()
            z = [rng.gauss(0.0, 1.0) for _ in range(self._n_features)]
            Lz = _matvec(L, z)
            valor = sum((t + escala * lz) * xi for t, lz, xi in zip(theta, Lz, x))
            u = rng.random()
            while u <= 0.0:  # pragma: no cover - random() pode devolver 0.0
                u = rng.random()
            gumbel = -math.log(-math.log(u))
            amostras[a] = [t + escala * lz for t, lz in zip(theta, Lz)]
            log_prior[a] = math.log(p0[a])
            gumbels[a] = gumbel
            score = math.log(p0[a]) + valor + gumbel
            if score > melhor_score:
                melhor, melhor_score = a, score
        if melhor is None:
            raise ArithmeticError("nenhuma acao com score finito")
        self._ultima_decisao = {"x": x, "acao": melhor, "amostras": amostras,
                                "log_prior": log_prior, "gumbel": gumbels}
        return melhor

    def observar(self, transicao: Transicao) -> None:
        obs = transicao.observacao
        tick = obs.ticks_desde_cuidado + self._tick_ultimo_cuidado
        if obs.ticks_desde_cuidado < 0 or tick <= self._tick_ultima_decisao:
            raise RuntimeError(
                f"relogio inconsistente: decisao em {tick}, anterior {self._tick_ultima_decisao}"
            )
        self._tick_ultima_decisao = tick
        self._expirar(tick)
        x = self._features(obs)
        self._ultima = (x, transicao.acao)
        if transicao.acao is AcaoPet.CHAMAR_ATENCAO:
            self._pendentes.append((tick, x))

    def receber_acao_dono(self, acao: AcaoUsuario, tick: int) -> None:
        if tick < self._tick_ultimo_cuidado:
            raise RuntimeError(f"acao do dono no passado: {tick} < {self._tick_ultimo_cuidado}")
        self._tick_ultimo_cuidado = tick
        self._expirar(tick)
        if acao in FEEDBACK:
            if self._ultima is None:
                return  # feedback antes da primeira decisao nao tem a quem creditar
            x, a = self._ultima
            if acao is AcaoUsuario.ELOGIAR:
                self._bracos[a].atualizar(x, self.cb.recompensa_elogio)
                self._n_recompensas["elogio"] += 1
            else:
                self._bracos[a].atualizar(x, self.cb.recompensa_repreensao)
                self._n_recompensas["repreensao"] += 1
        elif acao in CUIDADOS_QUE_ATENDEM:
            janela = self.cb.janela_latencia_ticks
            for tick_pedido, x in self._pendentes:
                latencia = tick - tick_pedido
                self._bracos[AcaoPet.CHAMAR_ATENCAO].atualizar(x, 1.0 - latencia / janela)
                self._n_recompensas["latencia"] += 1
            self._pendentes = []
        else:  # pragma: no cover - enum fechado
            raise ValueError(f"acao de dono desconhecida: {acao}")

    def _expirar(self, tick: int) -> None:
        janela = self.cb.janela_latencia_ticks
        vivos = []
        for tick_pedido, x in self._pendentes:
            if tick - tick_pedido > janela:
                self._bracos[AcaoPet.CHAMAR_ATENCAO].atualizar(x, self.cb.recompensa_pedido_ignorado)
                self._n_recompensas["ignorado"] += 1
            else:
                vivos.append((tick_pedido, x))
        self._pendentes = vivos

    # ------------------------------------------------------ serializacao

    def estado_interno(self) -> dict:
        return {
            "nome": self.nome,
            "parametros_aprendidos": sum(len(br.b) for br in self._bracos.values()),
            "n_features": self._n_features,
            "atualizacoes_por_acao": {a.value: br.n for a, br in self._bracos.items()},
            "recompensas": dict(self._n_recompensas),
            "theta": {a.value: br.theta() for a, br in self._bracos.items()},
            "A_inv": {a.value: [list(l) for l in br.A_inv] for a, br in self._bracos.items()},
            "b": {a.value: list(br.b) for a, br in self._bracos.items()},
            "tick_ultimo_cuidado": self._tick_ultimo_cuidado,
            "tick_ultima_decisao": self._tick_ultima_decisao,
            "pendentes": [[t, list(x)] for t, x in self._pendentes],
            "ultima": None if self._ultima is None else [list(self._ultima[0]), self._ultima[1].value],
        }

    @staticmethod
    def de_estado_interno(d: dict, cfg: Config | None = None, cfg_bandit: ConfigBandit | None = None) -> "PoliticaBandit":
        if d.get("nome") != PoliticaBandit.nome:
            raise ValueError(f"estado interno de outra politica: {d.get('nome')!r}")
        if d["n_features"] != N_FEATURES:
            raise ValueError("numero de features incompativel")
        p = PoliticaBandit(cfg, cfg_bandit)
        for a in ACOES:
            br = p._bracos[a]
            br.A_inv = [list(map(float, l)) for l in d["A_inv"][a.value]]
            br.b = list(map(float, d["b"][a.value]))
            br.n = int(d["atualizacoes_por_acao"][a.value])
            br._chol = None
            br._theta = None
        p._n_recompensas = dict(d["recompensas"])
        p._tick_ultimo_cuidado = int(d["tick_ultimo_cuidado"])
        p._tick_ultima_decisao = int(d["tick_ultima_decisao"])
        p._pendentes = [(int(t), list(map(float, x))) for t, x in d["pendentes"]]
        p._ultima = None if d["ultima"] is None else (list(map(float, d["ultima"][0])), AcaoPet(d["ultima"][1]))
        return p

