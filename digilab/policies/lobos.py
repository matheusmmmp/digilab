"""Politica com lobos nomeados (V2, L0: docs/TAREFA_V2_L0_LOBOS.md, 2026-10-01).

O aprendiz da V2. Quatro lobos, que sao ESTAGIOS internos com nome, nao interfaces plugaveis
(docs/digibrain 07, secao 2):

  PERCEPCAO        Observacao -> entradas x = (1, Estado.vetor, min(1, ticks sem cuidado / escala)).
                   Os mesmos floats que o instinto e o bandit leem hoje.
  MEMORIA/EMOCAO   presente como lobo nomeado: conta o que o dono fez (elogios, broncas, cuidados) e
                   as decisoes. Contribuicao zero em toda decisao (L0). L2 enche.
  IMPULSOS         as regras do PoliticaInstinto (policy.py), executadas pelo PROPRIO codigo do
                   instinto com uma rng-sonda (nao consome a rng do motor): devolvem a regra que
                   disparou e os CANDIDATOS, na ordem do instinto (uma acao nas regras deterministas;
                   comer/chamar na fome moderada; ocioso/explorar/brincar/chamar no tempo livre).
  DECISAO          pesos INTEIROS w[regra][acao][entrada], em ponto fixo com escala S = 2**bits,
                   iniciados no prior do instinto (os coeficientes das regras, vezes S). Peso efetivo
                   de cada candidato = ativacao linear sum_j (w_j / S) * x_j, somada da esquerda para a
                   direita. A acao sai por sorteio proporcional com UMA chamada de rng.random(),
                   exatamente a conta de random.choices(k=1) que o instinto faz. Unico lobo que
                   aprende (L1); aqui o aprendizado esta desligado e os pesos nunca mudam.

Por que a vida sai byte a byte igual a do instinto com os pesos no prior (restricao de desenho da
tarefa, secao 3):
  - regra determinista = um candidato so: nenhuma chamada de rng, como no instinto;
  - S e potencia de dois, entao w_j / S e exato e devolve os MESMOS floats que o instinto escreve
    (3.0; 2.0 + 2.0 * energia; 1.0 + 3.0 * humor; 1.0), somados na mesma ordem e sem somatorio
    compensado (laco explicito, nao sum());
  - o sorteio replica random.choices: cumulativa por itertools.accumulate, total = ultima + 0.0,
    bisect_right(cumulativa, random() * total, 0, n - 1). Na fome moderada os pesos [1.0, 1.0] dao
    "comer se 2 * u < 1.0", que e "comer se u < 0.5", a conta literal do instinto.

Motivo (base do gate G4 da fase 1): a cada decisao, a contribuicao de cada lobo por candidato. Peso
efetivo = impulsos (prior) + decisao (pesos menos prior) + memoria e emocao (zero). O sorteio e feito
SOBRE essa soma, entao a soma fecha com a decisao por construcao; `estado_interno()["motivos"]`
guarda todas.

Sem funcoes transcendentais (nada de math): paridade com a web quando o L1 for portado.
"""

from __future__ import annotations

import random
from bisect import bisect_right
from dataclasses import fields
from itertools import accumulate

from ..config import CONFIG_LOBOS, CONFIG_PADRAO, Config, ConfigLobos
from ..events import AcaoPet, AcaoUsuario
from ..policy import Observacao, PoliticaInstinto, Transicao

ACOES = tuple(AcaoPet)
LOBOS = ("percepcao", "memoria_emocao", "impulsos", "decisao")
# as regras do instinto, na ordem em que ele as testa (policy.py: ultima_regra)
REGRAS = ("sono_exaustao", "sono_continuar", "sono_noite", "pedido_necessidade", "abandono",
          "fome_moderada", "tempo_livre")
# entradas da percepcao: vies + Estado.vetor (ordem congelada em state.py) + tempo sem cuidado
ENTRADAS = ("vies", "fome", "higiene", "energia", "humor", "saude", "sujeira", "dormindo", "hora",
            "ticks_sem_cuidado")
N_ENTRADAS = len(ENTRADAS)

# Status de cada parametro da ConfigLobos (config.py). Todos PROPOSTOS, sem fonte, nenhum referendado.
PARAMETROS_LOBOS_L0: dict[str, tuple[str, str]] = {
    "aprendizado_ligado": ("PROPOSTO", "L0 desligado (TAREFA_V2_L0_LOBOS, secao 3); o L1 liga"),
    "bits_ponto_fixo": ("PROPOSTO", "sem fonte; potencia de dois para a divisao exata (secao 3, restricao de desenho)"),
    "escala_ticks_desde_cuidado": ("PROPOSTO", "mesmo valor de ConfigBandit.escala_ticks_desde_cuidado"),
    "maximo_pesos": ("PROPOSTO", "PLANO_V2_PESQUISA, fase 1b: abaixo de mil pesos, para o replay"),
}

# Prior do instinto em unidades de 1.0 (vira inteiro vezes S): regra -> acao -> entrada -> coeficiente.
# So os candidatos de cada regra tem coeficiente; o resto da tabela e zero. Os numeros sao os literais de
# PoliticaInstinto.agir: pesos do tempo livre {ocioso 3, explorar 2 + 2 energia, brincar 1 + 3 humor,
# chamar 1}; na fome moderada "comer se u < 0.5" = pesos iguais; nas deterministas o unico candidato.
# A igualdade com o codigo do instinto e conferida por teste (tests/test_lobos.py) e pelo gate G2.
PRIOR_INSTINTO: dict[str, dict[AcaoPet, dict[str, int]]] = {
    "sono_exaustao": {AcaoPet.DORMIR: {"vies": 1}},
    "sono_continuar": {AcaoPet.DORMIR: {"vies": 1}},
    "sono_noite": {AcaoPet.DORMIR: {"vies": 1}},
    "pedido_necessidade": {AcaoPet.CHAMAR_ATENCAO: {"vies": 1}},
    "abandono": {AcaoPet.EMBURRAR: {"vies": 1}, AcaoPet.CHAMAR_ATENCAO: {"vies": 1}},
    "fome_moderada": {AcaoPet.COMER: {"vies": 1}, AcaoPet.CHAMAR_ATENCAO: {"vies": 1}},
    "tempo_livre": {AcaoPet.OCIOSO: {"vies": 3}, AcaoPet.EXPLORAR: {"vies": 2, "energia": 2},
                    AcaoPet.BRINCAR: {"vies": 1, "humor": 3}, AcaoPet.CHAMAR_ATENCAO: {"vies": 1}},
}

CUIDADOS = frozenset({AcaoUsuario.ALIMENTAR, AcaoUsuario.LIMPAR, AcaoUsuario.BRINCAR, AcaoUsuario.ACARICIAR,
                      AcaoUsuario.PETISCO, AcaoUsuario.LEVAR_AO_BANHEIRO, AcaoUsuario.TRATAR_LESAO})


# ------------------------------------------------------------------ impulsos: sonda do instinto


class _RngSonda:
    """Substituto de random.Random que registra como o instinto usa a rng, sem consumir a rng do motor.

    Devolve sempre o mesmo u em random(); em choices() guarda populacao e pesos e devolve o primeiro.
    Qualquer outro uso levanta erro (falhar alto)."""

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


def impulsos(instinto: PoliticaInstinto, obs: Observacao) -> tuple[str, tuple[AcaoPet, ...]]:
    """Lobo de impulsos: a regra do instinto que dispara nesta observacao e os candidatos, na ordem dele.

    Executa o codigo do proprio PoliticaInstinto com uma rng-sonda. Regra determinista: um candidato.
    Um `random() < t` (fome moderada): os dois lados, com u = 0 e u -> 1. Um choices(): a populacao."""
    sonda = _RngSonda(0.0)
    a0 = instinto.agir(obs, sonda)
    regra = instinto.ultima_regra
    if regra is None:
        raise RuntimeError("instinto nao registrou a regra")
    if sonda.escolha is not None:
        if sonda.chamadas_random:
            raise NotImplementedError("instinto usou random() e choices() na mesma decisao")
        return regra, tuple(sonda.escolha[0])
    if sonda.chamadas_random == 0:
        return regra, (a0,)
    if sonda.chamadas_random > 1:
        raise NotImplementedError("instinto chamou random() mais de uma vez")
    a1 = instinto.agir(obs, _RngSonda(1.0 - 1e-15))
    if a1 is a0:
        raise NotImplementedError("instinto chamou random() sem que o resultado dependesse dele")
    return regra, (a0, a1)


# ------------------------------------------------------------------ decisao: ativacao e sorteio


def ativacao(pesos: list[int], x: list[float], escala: int) -> float:
    """sum_j (w_j / S) * x_j, da esquerda para a direita, sem somatorio compensado (laco, nao sum()).

    w_j / S e exato porque S e potencia de dois; com os pesos no prior, cada termo e o mesmo float que o
    instinto escreve e a soma segue a mesma ordem."""
    if len(pesos) != len(x):
        raise ValueError(f"{len(pesos)} pesos para {len(x)} entradas")
    acumulado = 0.0
    for w, xj in zip(pesos, x):
        acumulado = acumulado + (w / escala) * xj
    return acumulado


def sortear(pesos: list[float], u: float) -> int:
    """Indice sorteado com os pesos, dado u = rng.random(): a conta de random.choices(k=1), passo a passo."""
    cumulativa = list(accumulate(pesos))
    total = cumulativa[-1] + 0.0
    if total <= 0.0:
        raise ValueError(f"soma dos pesos nao positiva: {pesos}")
    return bisect_right(cumulativa, u * total, 0, len(cumulativa) - 1)


# ------------------------------------------------------------------ memoria e emocao (L0: so contadores)


class MemoriaEmocao:
    """Lobo nomeado, sem efeito na decisao no L0. So registra o que passou por ele."""

    def __init__(self) -> None:
        self.elogios = 0
        self.broncas = 0
        self.cuidados = 0
        self.outras_acoes_dono = 0
        self.decisoes = 0
        self.tick_ultima_acao_dono: int | None = None

    def acao_dono(self, acao: AcaoUsuario, tick: int) -> None:
        if acao is AcaoUsuario.ELOGIAR:
            self.elogios += 1
        elif acao is AcaoUsuario.REPREENDER:
            self.broncas += 1
        elif acao in CUIDADOS:
            self.cuidados += 1
        else:
            self.outras_acoes_dono += 1
        self.tick_ultima_acao_dono = tick

    def decisao(self) -> None:
        self.decisoes += 1

    def contribuicao(self, candidatos: tuple[AcaoPet, ...]) -> dict[AcaoPet, float]:
        return {a: 0.0 for a in candidatos}

    def para_dict(self) -> dict:
        return {"elogios": self.elogios, "broncas": self.broncas, "cuidados": self.cuidados,
                "outras_acoes_dono": self.outras_acoes_dono, "decisoes": self.decisoes,
                "tick_ultima_acao_dono": self.tick_ultima_acao_dono}


# ------------------------------------------------------------------ a politica


class PoliticaLobos:
    """Politica com lobos nomeados sob o Protocol Politica (agir, observar, estado_interno) e o gancho
    receber_acao_dono do MotorComFeedback. Nao altera engine.py. L0: aprendizado desligado."""

    nome = "lobos"

    def __init__(self, cfg: Config | None = None, cfg_lobos: ConfigLobos | None = None) -> None:
        self.cfg = cfg or CONFIG_PADRAO
        self.cl = cfg_lobos or CONFIG_LOBOS
        if self.cl.aprendizado_ligado:
            raise NotImplementedError("aprendizado ligado e o L1: nao existe nesta versao (L0)")
        if self.cl.bits_ponto_fixo < 1:
            raise ValueError("bits_ponto_fixo precisa ser >= 1")
        self._instinto = PoliticaInstinto(self.cfg)
        self._escala = self.cl.escala
        self._prior = self._tabela_prior(self._escala)
        self._pesos = {r: {a: list(v) for a, v in acoes.items()} for r, acoes in self._prior.items()}
        n = self.n_pesos()
        if n >= self.cl.maximo_pesos:
            raise ValueError(f"{n} pesos, teto {self.cl.maximo_pesos}")
        self.memoria = MemoriaEmocao()
        self.motivos: list[dict] = []
        self._ultima_regra: str | None = None

    @staticmethod
    def _tabela_prior(escala: int) -> dict[str, dict[AcaoPet, list[int]]]:
        tabela = {}
        for regra in REGRAS:
            por_acao = {}
            for a in ACOES:
                coefs = PRIOR_INSTINTO[regra].get(a, {})
                desconhecidas = set(coefs) - set(ENTRADAS)
                if desconhecidas:
                    raise ValueError(f"entrada desconhecida no prior: {desconhecidas}")
                por_acao[a] = [int(coefs.get(e, 0)) * escala for e in ENTRADAS]
            tabela[regra] = por_acao
        return tabela

    # ------------------------------------------------------------- leitura

    @property
    def ultima_regra(self) -> str | None:
        """Regra do instinto (lobo de impulsos) que decidiu a ultima chamada de agir(). Somente leitura."""
        return self._ultima_regra

    @property
    def ultimo_motivo(self) -> dict | None:
        return self.motivos[-1] if self.motivos else None

    def n_pesos(self) -> int:
        return sum(len(v) for acoes in self._pesos.values() for v in acoes.values())

    def pesos_mudaram(self) -> bool:
        return self._pesos != self._prior

    # ------------------------------------------------------------- lobos

    def percepcao(self, obs: Observacao) -> list[float]:
        x = [1.0, *obs.vetor_estado, min(1.0, obs.ticks_desde_cuidado / self.cl.escala_ticks_desde_cuidado)]
        if len(x) != N_ENTRADAS:
            raise ValueError(f"percepcao com {len(x)} entradas, esperadas {N_ENTRADAS}")
        return x

    def contribuicoes(self, regra: str, candidatos: tuple[AcaoPet, ...], x: list[float]) -> dict[str, dict[AcaoPet, float]]:
        """Contribuicao de cada lobo ao peso efetivo de cada candidato (o motivo)."""
        prior, pesos = self._prior[regra], self._pesos[regra]
        return {
            "impulsos": {a: ativacao(prior[a], x, self._escala) for a in candidatos},
            "decisao": {a: ativacao([w - w0 for w, w0 in zip(pesos[a], prior[a])], x, self._escala) for a in candidatos},
            "memoria_emocao": self.memoria.contribuicao(candidatos),
        }

    # ------------------------------------------------------------- Politica

    def agir(self, obs: Observacao, rng: random.Random) -> AcaoPet:
        x = self.percepcao(obs)
        regra, candidatos = impulsos(self._instinto, obs)
        contrib = self.contribuicoes(regra, candidatos, x)
        pesos = {a: contrib["impulsos"][a] + contrib["decisao"][a] + contrib["memoria_emocao"][a] for a in candidatos}
        if len(candidatos) == 1:
            u, acao = None, candidatos[0]
        else:
            u = rng.random()
            acao = candidatos[sortear([pesos[a] for a in candidatos], u)]
        maior = max(LOBOS[1:], key=lambda lobo: (contrib[lobo][acao], -LOBOS.index(lobo)))
        self._ultima_regra = regra
        self.motivos.append({
            "n": len(self.motivos), "regra": regra, "candidatos": [a.value for a in candidatos],
            "percepcao": dict(zip(ENTRADAS, x)),
            "contribuicoes": {lobo: {a.value: v for a, v in por_acao.items()} for lobo, por_acao in contrib.items()},
            "pesos": {a.value: v for a, v in pesos.items()},
            "u": u, "acao": acao.value, "lobo_decisivo": maior,
        })
        return acao

    def observar(self, transicao: Transicao) -> None:
        self.memoria.decisao()

    def receber_acao_dono(self, acao: AcaoUsuario, tick: int) -> None:
        """Gancho do MotorComFeedback. No L0 o feedback so passa pela memoria: os pesos nao mudam."""
        self.memoria.acao_dono(acao, tick)

    def estado_interno(self) -> dict:
        return {
            "nome": self.nome,
            "parametros_aprendidos": self.n_pesos(),
            "aprendizado_ligado": self.cl.aprendizado_ligado,
            "escala": self._escala,
            "entradas": list(ENTRADAS),
            "pesos": {r: {a.value: list(v) for a, v in acoes.items()} for r, acoes in self._pesos.items()},
            "pesos_prior": {r: {a.value: list(v) for a, v in acoes.items()} for r, acoes in self._prior.items()},
            "memoria_emocao": self.memoria.para_dict(),
            "n_decisoes": len(self.motivos),
            "motivos": [dict(m) for m in self.motivos],
        }


def validar_parametros_lobos(cfg: ConfigLobos | None = None) -> None:
    """Todo campo da ConfigLobos tem status registrado; nenhum campo registrado sem existir."""
    campos = {f.name for f in fields(cfg or CONFIG_LOBOS)}
    if campos != set(PARAMETROS_LOBOS_L0):
        raise ValueError(f"sem registro: {sorted(campos - set(PARAMETROS_LOBOS_L0))}; "
                         f"registro sem campo: {sorted(set(PARAMETROS_LOBOS_L0) - campos)}")
    for nome, (status, fonte) in PARAMETROS_LOBOS_L0.items():
        if status not in ("PROPOSTO", "DECIDIDO") or not fonte:
            raise ValueError(f"{nome}: status {status!r} ou fonte vazia")
