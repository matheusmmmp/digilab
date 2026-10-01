"""Politica com lobos nomeados (V2: L0 docs/TAREFA_V2_L0_LOBOS.md; L1 docs/TAREFA_V2_L1_DECISAO.md, 2026-10-01).

O aprendiz da V2. Quatro lobos, que sao ESTAGIOS internos com nome, nao interfaces plugaveis
(docs/digibrain 07, secao 2):

  PERCEPCAO        Observacao -> entradas x = (1, Estado.vetor, min(1, ticks sem cuidado / escala)).
                   Os mesmos floats que o instinto e o bandit leem hoje.
  MEMORIA/EMOCAO   presente como lobo nomeado: conta o que o dono fez (elogios, broncas, cuidados) e
                   as decisoes. Contribuicao zero em toda decisao (L0 e L1). L2 enche.
  IMPULSOS         as regras do PoliticaInstinto (policy.py), executadas pelo PROPRIO codigo do
                   instinto com uma rng-sonda (nao consome a rng do motor): devolvem a regra que
                   disparou e os CANDIDATOS, na ordem do instinto (uma acao nas regras deterministas;
                   comer/chamar na fome moderada; ocioso/explorar/brincar/chamar no tempo livre).
  DECISAO          pesos INTEIROS w[regra][acao][entrada], em ponto fixo com escala S = 2**bits,
                   iniciados no prior do instinto (os coeficientes das regras, vezes S). Peso efetivo
                   de cada candidato = ativacao linear sum_j (w_j / S) * x_j, somada da esquerda para a
                   direita. A acao sai por sorteio proporcional com UMA chamada de rng.random(),
                   exatamente a conta de random.choices(k=1) que o instinto faz. Unico lobo que
                   aprende (L1).

L0 (aprendizado desligado): os pesos nunca mudam e a vida sai byte a byte igual a do instinto
(restricao de desenho da tarefa L0, secao 3):
  - regra determinista = um candidato so: nenhuma chamada de rng, como no instinto;
  - S e potencia de dois, entao w_j / S e exato e devolve os MESMOS floats que o instinto escreve
    (3.0; 2.0 + 2.0 * energia; 1.0 + 3.0 * humor; 1.0), somados na mesma ordem e sem somatorio
    compensado (laco explicito, nao sum());
  - o sorteio replica random.choices: cumulativa por itertools.accumulate, total = ultima + 0.0,
    bisect_right(cumulativa, random() * total, 0, n - 1). Na fome moderada os pesos [1.0, 1.0] dao
    "comer se 2 * u < 1.0", que e "comer se u < 0.5", a conta literal do instinto.

L1 (aprendizado ligado, docs/PLANO_ANALISE_V2_L1.md, secao 2): o feedback do dono como VANTAGEM, nao
recompensa fixa (MacGlashan et al., COACH, arXiv:1701.06049). A cada sinal f creditado a uma decisao
(regra r, entradas X, probabilidades P da politica NO MOMENTO da decisao, acao escolhida a*):

    dw[r][a][j] = arred( f_S * passo * X_j * (S*1[a = a*] - P_a) / (S * S * W_a) )

tudo inteiro (f_S = f*S; X_j = arred(x_j*S); P_a = arred(p(a)*S); W_a = max(1, arred(w_eff(a)*S));
arred = inteiro mais proximo, meio longe do zero). Em unidades de 1.0: dw ~ f * passo * x_j *
(1[a = a*] - p(a)) / w_eff(a), a direcao do gradiente de log p(a*) da politica proporcional com o
sinal do dono no lugar da vantagem. A dependencia da politica atual esta em (1 - p(a*)): elogio a
acao ja provavel mexe pouco. Um sinal escalar; janela de credito igual a da v1 (elogio/bronca
creditam a ultima decisao; cada chamar_atencao fica pendente e o primeiro cuidado dentro da janela
paga 1 - L/janela; pendente expirado paga recompensa_pedido_ignorado). Teto |w - w0| <= teto por
peso; piso no peso efetivo dos candidatos (so com o aprendizado ligado). Regras com um candidato nao
tem o que aprender (1[a = a*] - p(a) = 0).

A regra de atualizacao e o credito moram na base `Aprendiz`, compartilhada com o controle de
capacidade equivalente sem lobos (policies/camada_unica.py, D2 de docs/DEFINICOES_V2.md): a mesma
funcao `atualizar_pesos`, o mesmo piso, teto e janela.

Motivo (base do gate G4 da fase 1): a cada decisao, a contribuicao de cada lobo por candidato. Peso
efetivo = impulsos (prior) + decisao (pesos menos prior) + memoria e emocao (zero) + piso (zero fora
do L1). O sorteio e feito SOBRE essa soma, entao a soma fecha com a decisao por construcao;
`estado_interno()["motivos"]` guarda todas (a sonda de divergencia tambem chama agir e acrescenta
motivos: gravar o estado interno antes de sondar).

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
PARAMETROS_LOBOS_L1: dict[str, tuple[str, str]] = {
    "passo": ("PROPOSTO", "sem fonte; calibrado nas sementes 3101...3505 (PLANO_ANALISE_V2_L1, secao 5)"),
    "teto": ("PROPOSTO", "sem fonte; calibrado nas sementes 3101...3505 (PLANO_ANALISE_V2_L1, secao 5)"),
    "piso_peso": ("PROPOSTO", "sem fonte; S/16, da ordem do piso_prior do bandit (0,05)"),
    "janela_latencia_ticks": ("PROPOSTO", "= ConfigBandit.janela_latencia_ticks (janela de credito da v1)"),
    "recompensa_pedido_ignorado": ("PROPOSTO", "= ConfigBandit.recompensa_pedido_ignorado"),
    "recompensa_elogio": ("PROPOSTO", "= ConfigBandit.recompensa_elogio"),
    "recompensa_repreensao": ("PROPOSTO", "= ConfigBandit.recompensa_repreensao"),
}
PARAMETROS_LOBOS = {**PARAMETROS_LOBOS_L0, **PARAMETROS_LOBOS_L1}

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
FEEDBACK = frozenset({AcaoUsuario.ELOGIAR, AcaoUsuario.REPREENDER})


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


# ------------------------------------------------------------------ percepcao, ativacao, sorteio, inteiros


def percepcao(obs: Observacao, escala_ticks_desde_cuidado: float) -> list[float]:
    """Lobo de percepcao: (1, Estado.vetor, min(1, ticks sem cuidado / escala)), N_ENTRADAS floats."""
    x = [1.0, *obs.vetor_estado, min(1.0, obs.ticks_desde_cuidado / escala_ticks_desde_cuidado)]
    if len(x) != N_ENTRADAS:
        raise ValueError(f"percepcao com {len(x)} entradas, esperadas {N_ENTRADAS}")
    return x


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


def termos(pesos: list[int], x: list[float], escala: int) -> list[float]:
    """Os termos (w_j / S) * x_j da ativacao, um por entrada (a contribuicao de cada entrada)."""
    if len(pesos) != len(x):
        raise ValueError(f"{len(pesos)} pesos para {len(x)} entradas")
    return [(w / escala) * xj for w, xj in zip(pesos, x)]


def sortear(pesos: list[float], u: float) -> int:
    """Indice sorteado com os pesos, dado u = rng.random(): a conta de random.choices(k=1), passo a passo."""
    cumulativa = list(accumulate(pesos))
    total = cumulativa[-1] + 0.0
    if total <= 0.0:
        raise ValueError(f"soma dos pesos nao positiva: {pesos}")
    return bisect_right(cumulativa, u * total, 0, len(cumulativa) - 1)


def arred(x: float) -> int:
    """Inteiro mais proximo, meio longe do zero (simetrico; round() do Python e meio-para-par)."""
    if x >= 0.0:
        return int(x + 0.5)
    return -int(-x + 0.5)


def div_arred(n: int, d: int) -> int:
    """n / d em inteiros, arredondado ao mais proximo, meio longe do zero. d > 0."""
    if d <= 0:
        raise ValueError(f"divisor nao positivo: {d}")
    q, r = divmod(abs(n), d)
    if 2 * r >= d:
        q += 1
    return q if n >= 0 else -q


def atualizar_pesos(pesos: dict, prior: dict, registro: dict, f_S: int, passo: int, teto: int, S: int) -> int:
    """A regra de atualizacao do L1, em inteiros, aplicada a tabela `pesos[acao] -> list[int]` de uma regra
    (ou contexto): dw[a][j] = arred(f_S * passo * X_j * (S*1[a=a*] - P_a) / (S*S*W_a)), cortado em prior +- teto.
    `registro` = {"candidatos", "acao", "X", "P", "W"} da decisao creditada. Devolve quantos cortes no teto."""
    cortes = 0
    escolhida = registro["acao"]
    for a in registro["candidatos"]:
        fator = (S if a is escolhida else 0) - registro["P"][a]
        if fator == 0:
            continue
        w, w0 = pesos[a], prior[a]
        denominador = S * S * registro["W"][a]
        for j, X in enumerate(registro["X"]):
            if X == 0:
                continue
            delta = div_arred(f_S * passo * X * fator, denominador)
            if delta == 0:
                continue
            novo = w[j] + delta
            if novo > w0[j] + teto:
                novo = w0[j] + teto
                cortes += 1
            elif novo < w0[j] - teto:
                novo = w0[j] - teto
                cortes += 1
            w[j] = novo
    return cortes


# ------------------------------------------------------------------ memoria e emocao (L0: so contadores)


class MemoriaEmocao:
    """Lobo nomeado, sem efeito na decisao no L0 e no L1. So registra o que passou por ele."""

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


# ------------------------------------------------------------------ a base: pesos inteiros + credito do L1


class Aprendiz:
    """Base dos aprendizes da V2: tabela de pesos inteiros `_pesos[grupo][acao][entrada]` iniciada no prior
    `_prior`, e o credito do feedback do L1 (janela da v1). Quem herda define `agir` (que deixa em
    `_registro_decisao` o registro da decisao: grupo, candidatos, acao, X, P, W) e `estado_interno`."""

    nome = "aprendiz"

    def __init__(self, cfg: Config | None, cfg_lobos: ConfigLobos | None, prior: dict) -> None:
        self.cfg = cfg or CONFIG_PADRAO
        self.cl = cfg_lobos or CONFIG_LOBOS
        if self.cl.bits_ponto_fixo < 1:
            raise ValueError("bits_ponto_fixo precisa ser >= 1")
        self._escala = self.cl.escala
        self._prior = prior
        self._pesos = {g: {a: list(v) for a, v in acoes.items()} for g, acoes in prior.items()}
        n = self.n_pesos()
        if n >= self.cl.maximo_pesos:
            raise ValueError(f"{n} pesos, teto {self.cl.maximo_pesos}")
        self.memoria = MemoriaEmocao()
        self.motivos: list[dict] = []
        self._aprende = bool(self.cl.aprendizado_ligado)
        if self._aprende:
            if self.cl.passo <= 0 or self.cl.teto <= 0 or self.cl.piso_peso <= 0 or self.cl.janela_latencia_ticks <= 0:
                raise ValueError("passo, teto, piso_peso e janela_latencia_ticks precisam ser positivos")
            for nome in ("passo", "teto", "piso_peso", "janela_latencia_ticks"):
                if type(getattr(self.cl, nome)) is not int:
                    raise TypeError(f"ConfigLobos.{nome} precisa ser inteiro")
        self._piso = self.cl.piso_peso / self._escala
        self._tick_ultimo_cuidado = 0
        self._tick_ultima_decisao = -1
        self._registro_decisao: dict | None = None
        self._ultima: dict | None = None              # registro da ultima decisao (para elogio/bronca)
        self._pendentes: list[tuple[int, dict]] = []  # chamados pendentes: (tick, registro)
        self._n_recompensas = {"elogio": 0, "repreensao": 0, "latencia": 0, "ignorado": 0}
        self._n_atualizacoes = 0
        self._cortes_teto = 0

    # ------------------------------------------------------------- leitura

    @property
    def ultimo_motivo(self) -> dict | None:
        return self.motivos[-1] if self.motivos else None

    @property
    def aprende(self) -> bool:
        return self._aprende

    def n_pesos(self) -> int:
        return sum(len(v) for acoes in self._pesos.values() for v in acoes.values())

    def pesos_mudaram(self) -> bool:
        return self._pesos != self._prior

    def desvio_maximo(self) -> int:
        """max |w - w0| sobre todos os pesos (o quanto o aprendizado se afastou do prior)."""
        return max(abs(w - w0) for g in self._pesos for a in self._pesos[g]
                   for w, w0 in zip(self._pesos[g][a], self._prior[g][a]))

    def pesos_no_teto(self) -> int:
        """Quantos pesos estao exatamente no teto (|w - w0| == teto)."""
        return sum(abs(w - w0) == self.cl.teto for g in self._pesos for a in self._pesos[g]
                   for w, w0 in zip(self._pesos[g][a], self._prior[g][a]))

    def percepcao(self, obs: Observacao) -> list[float]:
        return percepcao(obs, self.cl.escala_ticks_desde_cuidado)

    # ------------------------------------------------------------- decisao: pedacos comuns

    def _pesos_efetivos(self, grupo: str, candidatos: tuple[AcaoPet, ...], x: list[float]) -> tuple[dict, dict]:
        """(contribuicoes por termo, peso efetivo por candidato). Termos: impulsos (prior), decisao (pesos menos
        prior), memoria_emocao (zero), piso (so com o aprendizado ligado)."""
        prior, pesos = self._prior[grupo], self._pesos[grupo]
        c = {
            "impulsos": {a: ativacao(prior[a], x, self._escala) for a in candidatos},
            "decisao": {a: ativacao([w - w0 for w, w0 in zip(pesos[a], prior[a])], x, self._escala) for a in candidatos},
            "memoria_emocao": self.memoria.contribuicao(candidatos),
        }
        soma = {a: c["impulsos"][a] + c["decisao"][a] + c["memoria_emocao"][a] for a in candidatos}
        if self._aprende:
            c["piso"] = {a: (self._piso - soma[a] if soma[a] < self._piso else 0.0) for a in candidatos}
        else:
            c["piso"] = {a: 0.0 for a in candidatos}
        efetivos = {a: c["impulsos"][a] + c["decisao"][a] + c["memoria_emocao"][a] + c["piso"][a] for a in candidatos}
        return c, efetivos

    def _registrar(self, grupo: str, candidatos: tuple[AcaoPet, ...], acao: AcaoPet, x: list[float], pesos: dict,
                   contrib: dict, u: float | None, extra: dict | None = None) -> None:
        """Guarda o registro da decisao (para o credito) e o motivo (para o G4)."""
        aprendido = None
        registro = None
        if self._aprende:
            S = self._escala
            prior, tabela = self._prior[grupo], self._pesos[grupo]
            aprendido = {a.value: termos([w - w0 for w, w0 in zip(tabela[a], prior[a])], x, S) for a in candidatos}
            total = 0.0
            for a in candidatos:
                total = total + pesos[a]
            registro = {
                "regra": grupo, "candidatos": candidatos, "acao": acao,
                "X": [arred(xj * S) for xj in x],
                "P": {a: arred(pesos[a] / total * S) for a in candidatos},
                "W": {a: max(1, arred(pesos[a] * S)) for a in candidatos},
            }
        self._registro_decisao = registro
        maior = max(LOBOS[1:], key=lambda lobo: (contrib[lobo][acao], -LOBOS.index(lobo)))
        self.motivos.append({
            "n": len(self.motivos), "regra": grupo, "candidatos": [a.value for a in candidatos],
            "percepcao": dict(zip(ENTRADAS, x)),
            "contribuicoes": {lobo: {a.value: v for a, v in por_acao.items()} for lobo, por_acao in contrib.items()},
            "pesos": {a.value: v for a, v in pesos.items()},
            "u": u, "acao": acao.value, "lobo_decisivo": maior, "aprendido": aprendido, **(extra or {}),
        })

    # ------------------------------------------------------------- credito (janela da v1)

    def observar(self, transicao: Transicao) -> None:
        self.memoria.decisao()
        if not self._aprende:
            return
        obs = transicao.observacao
        tick = obs.ticks_desde_cuidado + self._tick_ultimo_cuidado
        if obs.ticks_desde_cuidado < 0 or tick <= self._tick_ultima_decisao:
            raise RuntimeError(f"relogio inconsistente: decisao em {tick}, anterior {self._tick_ultima_decisao}")
        self._tick_ultima_decisao = tick
        self._expirar(tick)
        registro = self._registro_decisao
        if registro is None or registro["acao"] is not transicao.acao:
            raise RuntimeError("registro da decisao nao corresponde a acao observada")
        self._ultima = registro
        if transicao.acao is AcaoPet.CHAMAR_ATENCAO:
            self._pendentes.append((tick, registro))

    def receber_acao_dono(self, acao: AcaoUsuario, tick: int) -> None:
        """Gancho do MotorComFeedback. L0: o feedback so passa pela memoria. L1: credita a decisao (janela da v1)."""
        self.memoria.acao_dono(acao, tick)
        if not self._aprende:
            return
        if tick < self._tick_ultimo_cuidado:
            raise RuntimeError(f"acao do dono no passado: {tick} < {self._tick_ultimo_cuidado}")
        self._tick_ultimo_cuidado = tick
        self._expirar(tick)
        S = self._escala
        if acao in FEEDBACK:
            if self._ultima is None:
                return                                   # feedback antes da primeira decisao nao tem a quem creditar
            if acao is AcaoUsuario.ELOGIAR:
                self._aplicar_sinal(self._ultima, arred(self.cl.recompensa_elogio * S))
                self._n_recompensas["elogio"] += 1
            else:
                self._aplicar_sinal(self._ultima, arred(self.cl.recompensa_repreensao * S))
                self._n_recompensas["repreensao"] += 1
        elif acao in CUIDADOS:
            janela = self.cl.janela_latencia_ticks
            for tick_pedido, registro in self._pendentes:
                self._aplicar_sinal(registro, S - div_arred((tick - tick_pedido) * S, janela))
                self._n_recompensas["latencia"] += 1
            self._pendentes = []
        # outras acoes do dono (treino etc.) nao creditam nada: so a memoria as conta

    def _expirar(self, tick: int) -> None:
        janela = self.cl.janela_latencia_ticks
        vivos = []
        for tick_pedido, registro in self._pendentes:
            if tick - tick_pedido > janela:
                self._aplicar_sinal(registro, arred(self.cl.recompensa_pedido_ignorado * self._escala))
                self._n_recompensas["ignorado"] += 1
            else:
                vivos.append((tick_pedido, registro))
        self._pendentes = vivos

    def _aplicar_sinal(self, registro: dict, f_S: int) -> None:
        g = registro["regra"]
        self._cortes_teto += atualizar_pesos(self._pesos[g], self._prior[g], registro, f_S, self.cl.passo, self.cl.teto,
                                             self._escala)
        self._n_atualizacoes += 1

    # ------------------------------------------------------------- serializacao

    def _estado_aprendizado(self) -> dict:
        def registro_dict(r):
            if r is None:
                return None
            return {"regra": r["regra"], "candidatos": [a.value for a in r["candidatos"]], "acao": r["acao"].value,
                    "X": list(r["X"]), "P": {a.value: v for a, v in r["P"].items()}, "W": {a.value: v for a, v in r["W"].items()}}
        return {
            "passo": self.cl.passo, "teto": self.cl.teto, "piso_peso": self.cl.piso_peso,
            "n_atualizacoes": self._n_atualizacoes, "cortes_teto": self._cortes_teto,
            "recompensas": dict(self._n_recompensas),
            "desvio_maximo": self.desvio_maximo(), "pesos_no_teto": self.pesos_no_teto(),
            "tick_ultimo_cuidado": self._tick_ultimo_cuidado, "tick_ultima_decisao": self._tick_ultima_decisao,
            "pendentes": [[t, registro_dict(r)] for t, r in self._pendentes],
            "ultima": registro_dict(self._ultima),
        }

    def estado_interno(self) -> dict:
        return {
            "nome": self.nome,
            "parametros_aprendidos": self.n_pesos(),
            "aprendizado_ligado": self._aprende,
            "escala": self._escala,
            "entradas": list(ENTRADAS),
            "pesos": {g: {a.value: list(v) for a, v in acoes.items()} for g, acoes in self._pesos.items()},
            "pesos_prior": {g: {a.value: list(v) for a, v in acoes.items()} for g, acoes in self._prior.items()},
            "memoria_emocao": self.memoria.para_dict(),
            "n_decisoes": len(self.motivos),
            "motivos": [dict(m) for m in self.motivos],
            "aprendizado": self._estado_aprendizado(),
        }


# ------------------------------------------------------------------ a politica com lobos


class PoliticaLobos(Aprendiz):
    """Politica com lobos nomeados sob o Protocol Politica (agir, observar, estado_interno) e o gancho
    receber_acao_dono do MotorComFeedback. Nao altera engine.py. L0: aprendizado desligado (padrao);
    L1: ConfigLobos(aprendizado_ligado=True), so o lobo de decisao aprende."""

    nome = "lobos"

    def __init__(self, cfg: Config | None = None, cfg_lobos: ConfigLobos | None = None) -> None:
        cl = cfg_lobos or CONFIG_LOBOS
        super().__init__(cfg, cl, self._tabela_prior(cl.escala))
        self._instinto = PoliticaInstinto(self.cfg)
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

    @property
    def ultima_regra(self) -> str | None:
        """Regra do instinto (lobo de impulsos) que decidiu a ultima chamada de agir(). Somente leitura."""
        return self._ultima_regra

    def contribuicoes(self, regra: str, candidatos: tuple[AcaoPet, ...], x: list[float]) -> dict[str, dict[AcaoPet, float]]:
        """Contribuicao de cada lobo ao peso efetivo de cada candidato (o motivo). `piso` so entra no L1."""
        return self._pesos_efetivos(regra, candidatos, x)[0]

    def agir(self, obs: Observacao, rng: random.Random) -> AcaoPet:
        x = self.percepcao(obs)
        regra, candidatos = impulsos(self._instinto, obs)
        contrib, pesos = self._pesos_efetivos(regra, candidatos, x)
        if len(candidatos) == 1:
            u, acao = None, candidatos[0]
        else:
            u = rng.random()
            acao = candidatos[sortear([pesos[a] for a in candidatos], u)]
        self._ultima_regra = regra
        self._registrar(regra, candidatos, acao, x, pesos, contrib, u)
        return acao


def validar_parametros_lobos(cfg: ConfigLobos | None = None) -> None:
    """Todo campo da ConfigLobos tem status registrado; nenhum campo registrado sem existir."""
    campos = {f.name for f in fields(cfg or CONFIG_LOBOS)}
    if campos != set(PARAMETROS_LOBOS):
        raise ValueError(f"sem registro: {sorted(campos - set(PARAMETROS_LOBOS))}; "
                         f"registro sem campo: {sorted(set(PARAMETROS_LOBOS) - campos)}")
    for nome, (status, fonte) in PARAMETROS_LOBOS.items():
        if status not in ("PROPOSTO", "DECIDIDO") or not fonte:
            raise ValueError(f"{nome}: status {status!r} ou fonte vazia")
