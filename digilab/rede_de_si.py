"""A rede de si: o automodelo em observacao (V2; docs/TAREFA_V2_REDE_DE_SI.md, etapas 1 e 2; etapa 2 do ego, docs/futuro/ego_existencia.md).

A rede preve o proprio pet, so olhando. Ela nao entra na escolha nem na fala (isso e a etapa 3 do ego); o embrulho `PoliticaComRede` a
deixa observar a vida sem muda-la (G-OBS). E-6: a Decisao aprende por reforco, a rede de si por erro de previsao, e nenhuma outra peca
aprende.

**O que a rede ve (sem acesso privilegiado).** So o que o pet tem:
- os receptores do corpo (`Observacao.corpo`, a `PercepcaoCorpo`, na escala S), todos os que existirem, na ordem dos campos;
- a acao que o proprio pet escolheu;
- o contexto que a observacao ja mostra: a bola, a comida boa e o pedido vigente, cada um 0 ou S (`contexto`);
- a idade em faixas, pelo proprio relogio: as decisoes que ja viveu.
Fica de fora: o quimico, o `Estado`, os pesos do cerebro, a regra do instinto e a sonda. O modulo so importa `config` e `events`.

**A cabeca do corpo.** Para cada horizonte n (RS-1) e cada receptor r, `p = corte(div_arred(soma w_j x_j, S), 0, S)`, com x = os
receptores de agora, a acao em um-quente x S, o contexto e o vies S. O prior e a persistencia (RS-2): o peso do proprio receptor e S, os
outros 0. Depois de n decisoes, com a leitura real, o LMS em inteiros: `w_j += div_arred(passo x (real - p) x x_j, S x S)`, cortado em
w0 +- teto.

**A cabeca da autoria.** Por acao, `q_a = corte(div_arred(soma v_j y_j, S), 0, S)`, com y = os receptores, o contexto, a faixa de idade
em um-quente x S e o vies S; o alvo e o um-quente (x S) da acao escolhida, pelo mesmo LMS, na hora. O prior e uniforme: o vies S / A.
As estimativas contrafactuais sao a mesma conta com o contexto alterado: sem o pedido (pedido = 0) e ao nascer (a primeira faixa).

**O erro exposto (E-11, sem leitor nesta tarefa).** Por receptor e horizonte, o erro absoluto recente (`e += div_arred((|erro| - e) x
fator, S)`) e a surpresa (o erro de agora menos o recente, antes de atualizar).

**Os numeros.** So inteiros, nenhuma funcao transcendental e nenhuma rng (G-INT). As duas cabecas somam menos de `maximo_pesos` (G-PESOS):
com R receptores, A acoes, C = 3 entradas de contexto, F faixas e H horizontes, `R x H x (R + A + C + 1) + A x (R + C + F + 1)`. Com o
corpo da bola (R = 10, A = 8, H = 3, F = 4): 660 + 144 = 804.
"""

from __future__ import annotations

from dataclasses import fields

from .config import CONFIG_REDE_DE_SI, ConfigRedeDeSi
from .events import FRUTAS, AcaoPet

ACOES = tuple(AcaoPet)
CONTEXTO = ("bola", "comida", "pedido")
TIPOS_COMIDA_BOA = ("racao",) + FRUTAS          # os tipos maduros entre os `vistos` do mundo fisico (a podre vem com `_podre`)

# Status dos campos da ConfigRedeDeSi (conferido por teste). Todos PROPOSTOS, sem fonte, nenhum referendado.
PARAMETROS_REDE_DE_SI: dict[str, tuple[str, str]] = {
    "ligada": ("DECIDIDO", "RS-5: a rede observa por um embrulho somente leitura; desligada por padrao"),
    "escala": ("PROPOSTO", "S do cerebro A e dos receptores do corpo (TAREFA_V2_CORPO_DRIVES, secao 10)"),
    "passo": ("PROPOSTO", "PLANO_ANALISE_V2_REDE_DE_SI, secao 5: a grade {S/64, S/16, S/4}; S/16 no meio, sem fonte"),
    "teto": ("PROPOSTO", "4 S, sem fonte"),
    "horizontes": ("DECIDIDO", "RS-1: n em {1, 4, 16} decisoes"),
    "faixas_idade": ("PROPOSTO", "1, 3 e 7 dias de 96 decisoes, sem fonte"),
    "fator_erro": ("PROPOSTO", "S/16, sem fonte (o erro recente das ultimas ~16 resolucoes)"),
    "maximo_pesos": ("PROPOSTO", "a tarefa, secao 2: as duas cabecas somam menos de mil"),
}


def div_arred(n: int, d: int) -> int:
    """n / d em inteiros, arredondado ao mais proximo, meio longe do zero. d > 0. A mesma conta de lobos.div_arred e corpo.div_arred
    (conferido por teste); copiada para a rede nao depender do cerebro nem do corpo."""
    if d <= 0:
        raise ValueError(f"divisor nao positivo: {d}")
    q, r = divmod(abs(n), d)
    if 2 * r >= d:
        q += 1
    return q if n >= 0 else -q


def _corte(v: int, S: int) -> int:
    return 0 if v < 0 else (S if v > S else v)


def contexto(obs, S: int) -> list[int]:
    """O contexto que a observacao ja mostra (0 ou S): a bola no cenario (ou vista no mundo fisico), a comida boa (a fruta do cenario, ou a
    racao e a fruta madura vistas) e o pedido vigente do dono (alguma fruta com -1 em `pedido_frutas`)."""
    mundo = getattr(obs, "mundo", None)
    vistos = [v[1] for v in mundo.vistos] if mundo is not None else []
    bola = obs.bola > 0 or "bola" in vistos
    comida = obs.fruta > 0 or any(v > 0 for v in obs.frutas_cenario) or any(t in TIPOS_COMIDA_BOA for t in vistos)
    pedido = any(v < 0 for v in obs.pedido_frutas)
    return [S if bola else 0, S if comida else 0, S if pedido else 0]


def n_pesos(R: int, cfg: ConfigRedeDeSi = CONFIG_REDE_DE_SI) -> int:
    """A contagem das duas cabecas com R receptores (o layout da docstring do modulo)."""
    A, C, F, H = len(ACOES), len(CONTEXTO), len(cfg.faixas_idade) + 1, len(cfg.horizontes)
    return R * H * (R + A + C + 1) + A * (R + C + F + 1)


class RedeDeSi:
    """A rede de si (docstring do modulo). `observar(obs, acao)` uma vez por decisao, na ordem da vida."""

    def __init__(self, cfg: ConfigRedeDeSi | None = None) -> None:
        self.cfg = cfg or CONFIG_REDE_DE_SI
        if not self.cfg.ligada:
            raise ValueError("RedeDeSi com a ConfigRedeDeSi desligada")
        self.S = self.cfg.escala
        self.horizontes = tuple(self.cfg.horizontes)
        self.receptores: tuple | None = None          # o layout, fixado na primeira observacao
        self.k = 0                                    # as decisoes ja vividas (o relogio do pet)
        self.pesos_corpo: dict | None = None          # str(n) -> receptor -> pesos
        self.prior_corpo: dict | None = None
        self.pesos_autoria: dict | None = None        # acao -> pesos
        self.prior_autoria: dict | None = None
        self.pendentes: dict = {str(n): [] for n in self.horizontes}   # previsoes que esperam a leitura real: (k, x, p)
        self.erro_recente: dict | None = None         # str(n) -> receptor -> erro absoluto recente
        self.surpresa: dict | None = None             # str(n) -> receptor -> a ultima surpresa resolvida
        self.cortes = 0
        self.atualizacoes = 0
        self.registros: list[dict] = []

    # ---------------------------------------------------------- o layout e as entradas
    def _montar(self, pc) -> None:
        self.receptores = tuple(f.name for f in fields(pc) if getattr(pc, f.name) is not None)
        R, S = len(self.receptores), self.S
        total = n_pesos(R, self.cfg)
        if total >= self.cfg.maximo_pesos:
            raise ValueError(f"rede de si com {R} receptores: {total} pesos, teto {self.cfg.maximo_pesos} (G-PESOS)")
        jc = R + len(ACOES) + len(CONTEXTO) + 1
        self.prior_corpo = {str(n): {r: [S if j == i else 0 for j in range(jc)] for i, r in enumerate(self.receptores)}
                            for n in self.horizontes}
        ja = R + len(CONTEXTO) + len(self.cfg.faixas_idade) + 1 + 1
        vies = div_arred(S, len(ACOES))
        self.prior_autoria = {a.value: [0] * (ja - 1) + [vies] for a in ACOES}
        self.pesos_corpo = {n: {r: list(w) for r, w in t.items()} for n, t in self.prior_corpo.items()}
        self.pesos_autoria = {a: list(w) for a, w in self.prior_autoria.items()}
        self.erro_recente = {str(n): {r: 0 for r in self.receptores} for n in self.horizontes}
        self.surpresa = {str(n): {r: 0 for r in self.receptores} for n in self.horizontes}

    def leituras(self, pc) -> list[int]:
        """Os receptores do layout, inteiros em [0, S]; um receptor a mais ou a menos que no layout falha alto."""
        presentes = tuple(f.name for f in fields(pc) if getattr(pc, f.name) is not None)
        if presentes != self.receptores:
            raise ValueError(f"rede de si: receptores {presentes}, layout {self.receptores}")
        ls = [getattr(pc, r) for r in self.receptores]
        for r, v in zip(self.receptores, ls):
            if type(v) is not int or not 0 <= v <= self.S:
                raise ValueError(f"rede de si: receptor {r!r} fora de inteiros em [0, {self.S}]: {v!r}")
        return ls

    def faixa(self, k: int) -> int:
        return sum(1 for limite in self.cfg.faixas_idade if k >= limite)

    def _x_corpo(self, ls: list[int], acao: AcaoPet, ctx: list[int]) -> list[int]:
        return ls + [self.S if a is acao else 0 for a in ACOES] + ctx + [self.S]

    def _y_autoria(self, ls: list[int], ctx: list[int], faixa: int) -> list[int]:
        return ls + ctx + [self.S if f == faixa else 0 for f in range(len(self.cfg.faixas_idade) + 1)] + [self.S]

    # ---------------------------------------------------------- as contas
    def _saida(self, w: list[int], x: list[int]) -> int:
        soma = 0
        for wj, xj in zip(w, x):
            soma += wj * xj
        return _corte(div_arred(soma, self.S), self.S)

    def _lms(self, w: list[int], w0: list[int], x: list[int], erro: int) -> None:
        S, passo, teto = self.S, self.cfg.passo, self.cfg.teto
        for j, xj in enumerate(x):
            if xj == 0 or erro == 0 or passo == 0:
                continue
            novo = w[j] + div_arred(passo * erro * xj, S * S)
            if novo > w0[j] + teto:
                novo = w0[j] + teto
                self.cortes += 1
            elif novo < w0[j] - teto:
                novo = w0[j] - teto
                self.cortes += 1
            w[j] = novo
        self.atualizacoes += 1

    def prever_corpo(self, n: int, x: list[int]) -> list[int]:
        t = self.pesos_corpo[str(n)]
        return [self._saida(t[r], x) for r in self.receptores]

    def autoria(self, y: list[int]) -> list[int]:
        return [self._saida(self.pesos_autoria[a.value], y) for a in ACOES]

    # ---------------------------------------------------------- a observacao de uma decisao
    def observar(self, obs, acao: AcaoPet) -> dict:
        """Uma decisao: 1) as previsoes de n decisoes atras recebem a leitura real (o LMS, o erro recente e a surpresa); 2) a autoria
        estima a escolha (e as duas contrafactuais) e aprende com a acao escolhida; 3) a cabeca do corpo preve os n horizontes.
        Devolve o registro da decisao (tambem guardado em `registros`)."""
        if not isinstance(acao, AcaoPet):
            raise TypeError(f"acao do pet esperada, veio {acao!r}")
        pc = getattr(obs, "corpo", None)
        if pc is None:
            raise RuntimeError("rede de si: Observacao sem o corpo (a rede le os receptores; precisa do MotorCorpo)")
        if self.receptores is None:
            self._montar(pc)
        S, k = self.S, self.k
        ls = self.leituras(pc)
        ctx = contexto(obs, S)
        surpresas = {}
        for n in self.horizontes:
            fila = self.pendentes[str(n)]
            if fila and fila[0][0] == k - n:
                _, x, p = fila.pop(0)
                rec, sur = self.erro_recente[str(n)], self.surpresa[str(n)]
                t, t0 = self.pesos_corpo[str(n)], self.prior_corpo[str(n)]
                for i, r in enumerate(self.receptores):
                    erro = ls[i] - p[i]
                    self._lms(t[r], t0[r], x, erro)
                    e = abs(erro)
                    sur[r] = e - rec[r]
                    rec[r] += div_arred((e - rec[r]) * self.cfg.fator_erro, S)
                surpresas[str(n)] = [sur[r] for r in self.receptores]
        faixa = self.faixa(k)
        y = self._y_autoria(ls, ctx, faixa)
        q = self.autoria(y)
        q_sem_pedido = self.autoria(self._y_autoria(ls, ctx[:2] + [0], faixa))
        q_ao_nascer = self.autoria(self._y_autoria(ls, ctx, 0))
        for a, qa in zip(ACOES, q):
            self._lms(self.pesos_autoria[a.value], self.prior_autoria[a.value], y, (S if a is acao else 0) - qa)
        x = self._x_corpo(ls, acao, ctx)
        previsoes = {}
        for n in self.horizontes:
            p = self.prever_corpo(n, x)
            self.pendentes[str(n)].append((k, x, p))
            previsoes[str(n)] = p
        reg = {"k": k, "acao": acao.value, "leituras": ls, "contexto": ctx, "faixa": faixa, "corpo": previsoes,
               "autoria": q, "autoria_sem_pedido": q_sem_pedido, "autoria_ao_nascer": q_ao_nascer, "surpresa": surpresas}
        self.registros.append(reg)
        self.k = k + 1
        return reg

    def n_pesos(self) -> int:
        if self.receptores is None:
            raise RuntimeError("rede de si sem layout: nenhuma observacao ainda")
        return (sum(len(w) for t in self.pesos_corpo.values() for w in t.values())
                + sum(len(w) for w in self.pesos_autoria.values()))

    def estado(self) -> dict:
        """Tudo o que a rede guarda (o replay o refaz bit a bit, G1-REDE)."""
        return {"receptores": None if self.receptores is None else list(self.receptores), "k": self.k,
                "pesos_corpo": self.pesos_corpo, "pesos_corpo_prior": self.prior_corpo, "pesos_autoria": self.pesos_autoria,
                "pesos_autoria_prior": self.prior_autoria,
                "pendentes": {n: [[kk, list(x), list(p)] for kk, x, p in f] for n, f in self.pendentes.items()},
                "erro_recente": self.erro_recente, "surpresa": self.surpresa, "cortes": self.cortes,
                "atualizacoes": self.atualizacoes, "registros": self.registros}


class PoliticaComRede:
    """O embrulho somente leitura (RS-5): repassa ao cerebro tudo, sem mudar nada, e entrega a rede so a observacao da decisao e a acao
    que o cerebro escolheu (depois que ele escolheu; a rede nao toca na rng). Todo o resto (observar, os ganchos do dono, do corpo e do
    mundo, o estado interno) vai ao cerebro por `__getattr__`, entao o que existe nele existe aqui, e o que nao existe tambem nao."""

    def __init__(self, interna, cfg_rede: ConfigRedeDeSi | None = None) -> None:
        self._interna = interna
        self.rede = RedeDeSi(cfg_rede or CONFIG_REDE_DE_SI)

    def agir(self, obs, rng):
        acao = self._interna.agir(obs, rng)
        self.rede.observar(obs, acao)
        return acao

    def __getattr__(self, nome: str):
        interna = self.__dict__.get("_interna")
        if interna is None:
            raise AttributeError(nome)
        return getattr(interna, nome)
