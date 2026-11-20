"""A cooperacao entre dois pets do mesmo dono: os atos sociais derivados e a pontuacao (V3; docs/TAREFA_V3_COOPERACAO.md, etapa CO3,
secao 3.1; a nota "Moral do pet", A3, no vault; D-MM-8, CO-2, CO-3, CO-9).

So mede. O Grupo (digilab/grupo.py), com a ConfigCooperacao ligada, chama `decisao` logo depois de cada pet decidir na vez sorteada e
`fim_do_tick` depois do toque e da disputa; nada aqui muda o mundo, o corpo ou o cerebro (o G-SEM-DECISAO), e tudo sai do replay: nada e
estado salvo. O espelho em TS e web/app/motor/cooperacao.ts, conferido pelo G-PAR-COOP.

Os atos (so os que ja acontecem no Grupo; nenhuma acao nova, CO-2), cada um com o autor i e o alvo j:
  disputa    o registro `disputas` do Grupo: i comeu a comida que j tinha como alvo. Sinal -1 ("anti") se a fome de j (o `fome_antes` da
             ultima decisao dele) estava abaixo do `piso_fome`; 0 ("neutro") se nao. O efeito e o que j deixou de comer: o ganho que i teve.
  contencao  numa decisao de i, j esta a vista de i, ha uma comida madura so a vista (c) e i nao a come; se j come c antes da proxima
             decisao de i, e o ato (no tick em que j come). Sinal +1. O efeito e o ganho de j.
  encostar   o contato do tick em que i "encostou" em j (i seguiu j) com j emburrado visto de fora (a acao visivel de j e `emburrar`).
             Sinal +1. O efeito e 0: o toque ainda nao mexe no corpo (o degrau 3 dos dois pets), e um ato que nao muda o corpo do outro
             vale 0 (a trava do farm, A3).
O ganho de uma refeicao, na escala S: max(0, floor(S x ((fome_depois - fome_antes) + (humor_depois - humor_antes)) + 1/2)), do registro do
consumo (o bem-estar do corpo de quem comeu, medido pelo motor).

A pontuacao (inteiros na escala S): valor = sinal x efeito; a repeticao n do mesmo ato com o mesmo alvo na janela (o dia do mundo) entra com
div_arred(valor, 2**n); a conta decai tick a tick pela meia-vida (o passo_meia_vida do corpo, com o sinal de fora), guardada em ponto fixo
de BITS_FRACAO bits abaixo de S e lida arredondada (div_arred) na escala S: na escala S pura, o passo minimo de 1 por tick do corpo apagaria
um valor de centenas em centenas de ticks, e nao em dias (D-CO3-4). A intencao pesa zero
(`peso_int` = 0, D-CO0-3). A reputacao de i vista por k e a mesma conta, so com os atos de i que k testemunhou: k ve i no momento do ato
(a distancia ate o raio da visao de k, com as posicoes daquele momento), e a repeticao conta so entre os testemunhados.

A CO6 (docs/ESPEC_V3_COOPERACAO_CO6.md; so com a subchave `co6`): o peso dos deveres `k` de cada pet, pela convivencia (Alger e Weibull
2013, 10.3982/ecta10637, a forma; os numeros sao PROPOSTOS, SEM FONTE). O Grupo chama `fim_do_tick_k` no fim de TODO tick (com ou sem
decisao), depois da medida do tick, com as posicoes, os raios e a idade (o tick do proprio pet) de cada presente. Para cada pet i, em ordem
de id: ha encontro se algum outro j esta a ate o raio da visao de i e a ate o de j (um ve o outro) e a reputacao de j vista por i e positiva
naquele tick; com encontro, `k_i` ganha `k_passo`; sem, decai um tick pela meia-vida da pontuacao (CO6-3); e fica no teto do estagio da
idade (CO6-4). Guardado como a pontuacao, em ponto fixo de BITS_FRACAO bits abaixo de S, e lido arredondado na escala S. O `k` so le a
reputacao (feita so dos atos testemunhados) e a posicao: nada do estado interno do outro (o G-RECEPTOR-SOCIAL). Nada aqui muda a decisao.

So biblioteca padrao.
"""

from __future__ import annotations

import math

from .config import TICKS_POR_DIA, ConfigCooperacao
from .corpo import passo_meia_vida
from .expressao import estagio_por_idade
from .mundo import distancia, div_arred

ATOS = ("disputa", "contencao", "encostar")
BITS_FRACAO = 16                                  # a conta guarda valor x 2**16 (D-CO3-4)
TIPOS_MADUROS = ("racao", "a", "b", "c")          # o tipo de uma comida madura na percepcao (a podre vem com "_podre"; a bola, "bola")


def ganho_da_refeicao(consumo: dict, escala: int) -> int:
    """o bem-estar que a refeicao deu a quem comeu, na escala S (nunca negativo: a podre nao da nada)"""
    delta = (consumo["fome_depois"] - consumo["fome_antes"]) + (consumo["humor_depois"] - consumo["humor_antes"])
    return max(0, math.floor(escala * delta + 0.5))


def decair(v: int, ticks: int, k: int) -> int:
    """`ticks` passos da meia-vida sobre v, com o sinal de fora (o passo_meia_vida do corpo vale para v >= 0)"""
    if ticks < 0:
        raise ValueError(f"a pontuacao nao volta no tempo: {ticks}")
    sinal, q = (1, v) if v >= 0 else (-1, -v)
    for _ in range(ticks):
        if q == 0:
            break
        q = passo_meia_vida(q, k)
    return sinal * q


class Conta:
    """Uma pontuacao: o valor no ultimo tick e as repeticoes de cada (janela, ato, alvo)."""

    def __init__(self, cfg: ConfigCooperacao) -> None:
        self.cfg = cfg
        self.bruto = 0                                  # o valor x 2**BITS_FRACAO no ultimo tick
        self.tick = 0
        self.repeticoes: dict[tuple, int] = {}
        self._lido: tuple[int, int] | None = None      # (tick, bruto decaido ate ele): o decaimento e passo a passo, e partir dele e exato

    def _bruto_em(self, tick: int) -> int:
        base_tick, base = self.tick, self.bruto
        if self._lido is not None and base_tick <= self._lido[0] <= tick:
            base_tick, base = self._lido
        v = decair(base, tick - base_tick, self.cfg.k_meia_vida_pontuacao)
        self._lido = (tick, v)
        return v

    def em(self, tick: int) -> int:
        """o valor no tick, na escala S"""
        return div_arred(self._bruto_em(tick), 2 ** BITS_FRACAO)

    def somar(self, tick: int, ato: str, alvo: str, valor: int) -> tuple[int, int, int]:
        """(a repeticao, a contribuicao, o valor depois, na escala S)"""
        self.bruto = self._bruto_em(tick)
        self.tick = tick
        self._lido = None
        chave = (tick // self.cfg.janela_novidade, ato, alvo)
        n = self.repeticoes.get(chave, 0)
        self.repeticoes[chave] = n + 1
        contribuicao = div_arred(valor, 2 ** n)
        self.bruto += contribuicao * 2 ** BITS_FRACAO
        return n, contribuicao, self.em(tick)


class Cooperacao:
    """A medida da cooperacao de um grupo (a ConfigCooperacao ligada). So le o que o Grupo passa; nao muda nada."""

    def __init__(self, cfg: ConfigCooperacao) -> None:
        if not isinstance(cfg, ConfigCooperacao) or not cfg.ligada:
            raise ValueError("a Cooperacao so existe com a ConfigCooperacao ligada")
        self.cfg = cfg
        self.atos: list[dict] = []
        self._pontuacao: dict[str, Conta] = {}
        self._reputacao: dict[tuple[str, str], Conta] = {}
        self._fome: dict[str, float] = {}                         # o fome_antes da ultima decisao de cada pet
        self._oportunidades: dict[str, list[tuple]] = {}          # autor -> [(tick, alvo, comida)] da ultima decisao dele
        self._ganhos: dict[tuple, int] = {}                       # (tick, quem, comida) -> o ganho, so no tick
        self._k: dict[str, int] = {}                              # a CO6: o `k` de cada pet x 2**BITS_FRACAO, no fim do ultimo tick

    # ------------------------------------------------------------ o que o Grupo chama
    def decisao(self, tick: int, ident: str, maduras: list[int], outros_vistos: list[str], fome_antes: float, consumo: dict | None,
                posicoes: dict[str, tuple[int, int]], raios: dict[str, int]) -> None:
        """o pet `ident` acabou de decidir (e de andar e comer) no tick: `maduras` sao os ids das comidas maduras que ele via ao decidir,
        `outros_vistos` os outros pets a vista dele, `consumo` o registro do que ele comeu nesta decisao (ou None); `posicoes` e `raios`,
        os de todos os presentes agora"""
        self._fome[ident] = fome_antes
        if consumo is not None:
            ganho = ganho_da_refeicao(consumo, self.cfg.escala)
            self._ganhos[(tick, ident, consumo["id"])] = ganho
            for autor in sorted(self._oportunidades):
                if autor == ident:
                    continue
                for op in list(self._oportunidades[autor]):
                    if op[1] == ident and op[2] == consumo["id"]:
                        self._oportunidades[autor].remove(op)
                        self._ato(tick, "contencao", autor, ident, consumo["id"], 1, ganho, posicoes, raios)
        comeu = None if consumo is None else consumo["id"]
        novas = []
        if len(maduras) == 1 and maduras[0] != comeu:
            novas = [(tick, j, maduras[0]) for j in sorted(outros_vistos)]
        self._oportunidades[ident] = novas

    def fim_do_tick(self, tick: int, disputas: list[dict], contatos: list[dict], acoes: dict[str, str],
                    posicoes: dict[str, tuple[int, int]], raios: dict[str, int]) -> None:
        """o fim de um tick com decisao: as disputas e os contatos deste tick, a acao visivel e a posicao de cada presente"""
        for d in disputas:
            i, j = d["vencedor"], d["perdedor"]
            chave = (tick, i, d["comida"])
            if chave not in self._ganhos:
                raise ValueError(f"disputa sem a refeicao do vencedor no tick: {d}")
            if j not in self._fome:
                raise ValueError(f"disputa com um perdedor que nunca decidiu: {d}")
            sinal = -1 if self._fome[j] < self.cfg.piso_fome else 0
            self._ato(tick, "disputa", i, j, d["comida"], sinal, self._ganhos[chave], posicoes, raios)
        for c in contatos:
            a, b = c["pets"]
            for eu, outro in ((a, b), (b, a)):
                if c["tipos"][eu] == "encostou" and acoes[outro] == "emburrar":
                    self._ato(tick, "encostar", eu, outro, None, 1, 0, posicoes, raios)
        self._ganhos = {k: v for k, v in self._ganhos.items() if k[0] != tick}

    def fim_do_tick_k(self, tick: int, posicoes: dict[str, tuple[int, int]], raios: dict[str, int], idades: dict[str, int]) -> None:
        """a CO6: o fim de TODO tick, depois da medida do tick; `idades` e o tick do proprio pet (a idade, que da o estagio e o teto)"""
        if not self.cfg.co6:
            raise RuntimeError("o peso dos deveres (fim_do_tick_k) exige a subchave co6 da ConfigCooperacao")
        if set(idades) != set(posicoes) or set(raios) != set(posicoes):
            raise ValueError(f"posicoes, raios e idades de presentes diferentes: {sorted(posicoes)} {sorted(raios)} {sorted(idades)}")
        um = 2 ** BITS_FRACAO
        for i in sorted(posicoes):
            xi, yi = posicoes[i]
            encontro = False
            for j in sorted(posicoes):
                if j == i:
                    continue
                d = distancia(posicoes[j][0] - xi, posicoes[j][1] - yi)
                if d <= raios[i] and d <= raios[j] and self.reputacao(j, i, tick) > 0:
                    encontro = True
                    break
            k = self._k.get(i, 0)
            k = k + self.cfg.k_passo * um if encontro else decair(k, 1, self.cfg.k_meia_vida_pontuacao)
            self._k[i] = min(k, self.teto_k(idades[i]) * um)

    def teto_k(self, idade: int) -> int:
        """o teto do `k` no estagio da idade em ticks do proprio pet (CO6-4; o estagio provisorio da ConfigExpressao)"""
        if type(idade) is not int or idade < 0:
            raise ValueError(f"idade em ticks, inteira e nao negativa: {idade!r}")
        estagio = estagio_por_idade(idade / TICKS_POR_DIA)
        teto = getattr(self.cfg, f"k_teto_{estagio}")
        # a dose da bancada (fator_teto_k; S no jogo): com S, o teto da CO6-4, exato
        return teto if self.cfg.fator_teto_k == self.cfg.escala else div_arred(teto * self.cfg.fator_teto_k, self.cfg.escala)

    def peso_dever(self, ident: str) -> int:
        """o `k` do pet no fim do ultimo tick, na escala S (0 antes do primeiro tick dele)"""
        if not self.cfg.co6:
            raise RuntimeError("o peso dos deveres exige a subchave co6 da ConfigCooperacao")
        return div_arred(self._k.get(ident, 0), 2 ** BITS_FRACAO)

    # ------------------------------------------------------------ a conta
    def _conta(self, tabela: dict, chave) -> Conta:
        if chave not in tabela:
            tabela[chave] = Conta(self.cfg)
        return tabela[chave]

    def _ato(self, tick: int, ato: str, autor: str, alvo: str, comida: int | None, sinal: int, efeito: int,
             posicoes: dict[str, tuple[int, int]], raios: dict[str, int]) -> None:
        if ato not in ATOS or sinal not in (-1, 0, 1) or type(efeito) is not int or efeito < 0:
            raise ValueError(f"ato invalido: {ato} {sinal} {efeito}")
        valor = sinal * efeito
        ax, ay = posicoes[autor]
        testemunhas = sorted(k for k in posicoes if k != autor
                             and distancia(posicoes[k][0] - ax, posicoes[k][1] - ay) <= raios[k])
        n, contribuicao, p = self._conta(self._pontuacao, autor).somar(tick, ato, alvo, valor)
        reputacao = {}
        for k in testemunhas:
            nk, ck, rk = self._conta(self._reputacao, (autor, k)).somar(tick, ato, alvo, valor)
            reputacao[k] = {"repeticao": nk, "contribuicao": ck, "depois": rk}
        self.atos.append({"tick": tick, "ato": ato, "autor": autor, "alvo": alvo, "comida": comida, "sinal": sinal, "efeito": efeito,
                          "valor": valor, "repeticao": n, "contribuicao": contribuicao, "pontuacao_depois": p,
                          "testemunhas": testemunhas, "reputacao": reputacao})

    # ------------------------------------------------------------ leitura
    def pontuacao(self, ident: str, tick: int) -> int:
        c = self._pontuacao.get(ident)
        return 0 if c is None else c.em(tick)

    def reputacao(self, ident: str, vista_por: str, tick: int) -> int:
        c = self._reputacao.get((ident, vista_por))
        return 0 if c is None else c.em(tick)

    def resumo(self, ids: list[str], tick: int) -> dict:
        """os atos, a pontuacao de cada pet e a reputacao de cada um vista por cada outro, no tick"""
        r = {"atos": self.atos, "pontuacao": {i: self.pontuacao(i, tick) for i in ids},
             "reputacao": {i: {k: self.reputacao(i, k, tick) for k in ids if k != i} for i in ids}}
        if self.cfg.co6:                                          # a CO6: desligada, o resumo de hoje
            r["peso_dever"] = {i: self.peso_dever(i) for i in ids}
        return r
