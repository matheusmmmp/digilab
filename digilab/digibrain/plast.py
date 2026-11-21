"""M-PLAST, a plasticidade (docs/ESPEC_DIGIBRAIN_MODULAR.md, secoes 2.3, 2.4 e 4.8). Duas regras locais, inteiras, multiplicadas pelo
`g_apr` do M-AFETO.

**P1, o modelo do desfecho** (subchave `p1`): por classe c (racao, a, b, c, podre, bola) e por receptor r, o quanto a leitura muda ao
consumir: `d[c,r] <- clamp(d[c,r] + mul(mul(g_apr, eta_d), Delta_r - d[c,r]), -S, S)`, com Delta = os receptores logo depois menos os da
decisao. E a conta do `ModeloMundo` (digilab/modelo_mundo.py) com o ganho a mais: com g_apr = S, a mesma (conferido por teste). Como nele:
  - so o consumo do `comer` (e o brincar com a bola) atualiza o desfecho; o "achou e comeu" do explorar nao;
  - a energia e corrigida pelo andar previsto, `div_arred(andar x d, S)`, com d a distancia percebida da decisao ate onde o pet parou (a
    raiz inteira) e `andar` o custo aprendido nas decisoes de comer com d > 0, `andar <- andar + mul(mul(g_apr, eta_d), amostra - andar)`,
    amostra = `div_arred((energia depois - energia antes) x S, d)`.
O incentivo (o "querer", secao 2.3; PE-7): `G = clamp(div_arred(c_G x valor_previsto(corpo, d[c]), S_V), 0, G_max)`, com o
`valor_previsto` do A (o `sinal_corpo` do estado de agora para o previsto: revaloriza com o estado sem reaprender), e o M-IMPULSO o
multiplica pela proximidade do item. Sem o P1, o incentivo e 0 e o desfecho fica em 0.

**P2, o habito** (subchave `p2`; o hebbiano de tres fatores): por comportamento b e caracteristica j, `H[b,j]`, com partida 0. Quando uma
opcao acaba (o credito por opcao, PE-3; o M-ESTADO), so na linha do comportamento dela:
  `H[b*,j] <- clamp(H[b*,j] + mul(mul(g_apr, eta_h), mul(r_n, e_j)), -H_max, H_max)`,
com e_j = z_j da decisao que comecou a opcao (a elegibilidade), r_n a soma dos r_n das consequencias dela (cortada em [-S, S]) e o g_apr
da ultima decisao dela. O termo do habito de cada comportamento e `sum_j mul(H[b,j], z_j)`. Sem o P2, o termo e 0 e H fica em 0.
Com a subchave `fala_unidades` (docs/PLANO_ANALISE_V3_CONVERSA_DC3.md, 3.1), a linha do `chamar_atencao` da lugar a tres, uma por unidade de
fala (`chamar_atencao/fome`, `/higiene`, `/solidao`, no lugar dela, na mesma ordem), e a opcao de fala credita a linha do seu conteudo; a
regra e a mesma. Desligada, as linhas sao as de hoje.
Com a subchave `olhar` (GOSTO_VISUAL, P1d; espec, secao 5.3), o desfecho ganha a classe `tela` (o quanto olhar muda cada receptor, o
`consequencia_olhar` em cada opcao de olhar) e o H ganha a linha `olhar`, as duas no fim. Desligada, as de hoje.
Com a subchave `unidades_sociais` (SOCIAL_PAR M1; docs/ESPEC_SOCIAL_PAR_M1.md, secao 3.4), o desfecho ganha as classes `seguir` e
`onde_comeu`, no fim: cada decisao de uma unidade social vai ao `consequencia_p1` com a classe igual ao tipo (o Delta dos receptores da
decisao, com a energia corrigida pelo andar previsto), e o incentivo delas e o da classe. O H nao muda (a linha e a do explorar).
**O critico** (docs/TAREFA_V3_PLASTICIDADE_EVOLUIDA.md, secao 9.1, o C0; so com a `ConfigCritico` ligada, `critico`): o P2 recebe o
erro de diferenca temporal no lugar do r_n cru. O `creditar` guarda a opcao que acabou; o `fechar_pendentes(z2)`, que o M-ADAPT chama com
as caracteristicas da decisao em que a opcao acaba (ou da seguinte, quando ela acaba na consequencia), calcula
`delta = clamp(r_n + mul(gamma, V(z2)) - V(e), -S, S)`, com `V(z) = sum_j mul(v_j, z_j)`, e faz as duas atualizacoes, com o passo
multiplicado pelo g_apr da opcao como nas outras regras:
  `v_j <- clamp(v_j + mul(mul(mul(g_apr, eta_v), delta), e_j), -S, S)`     (o TD(0) do V, com o delta lido antes)
  `H[b*,j] <- clamp(H[b*,j] + mul(mul(g_apr, eta_h), mul(delta, e_j)), -H_max, H_max)`.
A opcao que acaba na ultima consequencia da vida nao tem decisao seguinte e fica sem credito. Desligada, o P2 de hoje, byte a byte.
Sem rng."""
from __future__ import annotations

from ..config import (CARACTERISTICAS_DIGIBRAIN, COMPORTAMENTO_OLHAR, COMPORTAMENTOS_DIGIBRAIN, CONFIG_DIGIBRAIN_INATOS, CONTEUDOS_FALA, ConfigCritico,
                      ConfigDigibrain, ConfigDigibrainInatos, TIPOS_ALVO_SOCIAIS)
from ..modelo_mundo import raiz_inteira
from .base import div_arred, valor_previsto
from ._comum import clamp, mul

CLASSES_DESFECHO = ("racao", "a", "b", "c", "podre", "bola")
CLASSE_TELA = "tela"                            # o olhar (P1d): a classe do desfecho de olhar, so com a subchave `olhar`


def linha_da_opcao(chave: tuple, fala_unidades: bool) -> str:
    """a linha de H que a opcao credita: a do comportamento; com a `fala_unidades`, a opcao de fala credita a do conteudo"""
    if fala_unidades and chave[0] == "chamar_atencao":
        if chave[1] not in CONTEUDOS_FALA:
            raise ValueError(f"M-PLAST: a opcao de fala sem conteudo: {chave!r}")
        return f"chamar_atencao/{chave[1]}"
    return chave[0]


class Plasticidade:
    """o M-PLAST (docstring do modulo)"""

    def __init__(self, cfg_digibrain: ConfigDigibrain, inatos: ConfigDigibrainInatos | None = None, dc_cheiro: bool = False,
                 critico: ConfigCritico | None = None) -> None:
        self.p = inatos or CONFIG_DIGIBRAIN_INATOS
        self.cd = cfg_digibrain
        self.S = self.p.escala
        self.receptores: tuple | None = None
        self.desfecho: dict | None = None             # classe -> [d_r na ordem dos receptores]
        self.andar = 0
        linhas = [b for b in COMPORTAMENTOS_DIGIBRAIN] + ([COMPORTAMENTO_OLHAR] if self.cd.olhar else [])   # o olhar (P1d), no fim
        self.classes = CLASSES_DESFECHO + ((CLASSE_TELA,) if self.cd.olhar else ())   # a classe `tela` do desfecho (P1d), no fim
        self.classes += TIPOS_ALVO_SOCIAIS if self.cd.unidades_sociais else ()        # o SOCIAL_PAR M1: as classes sociais, no fim
        if self.cd.fala_unidades:                     # as tres linhas da fala no lugar da do chamar (a ordem fixa)
            i = linhas.index("chamar_atencao")
            linhas[i:i + 1] = [f"chamar_atencao/{c}" for c in CONTEUDOS_FALA]
        # o PV-2 (`dc_cheiro`): a coluna do dC do cheiro no fim do z, e do H (desligado, o H de hoje)
        self.H = {b: [0] * (len(CARACTERISTICAS_DIGIBRAIN) + (1 if dc_cheiro else 0)) for b in linhas}
        self.consumos = {c: 0 for c in self.classes}
        self.amostras_andar = 0
        self.creditos = 0
        # o critico (o C0): so com a ConfigCritico ligada; desligada, nenhum estado novo
        self.cr: ConfigCritico | None = None
        if critico is not None:
            if not isinstance(critico, ConfigCritico):
                raise TypeError(f"M-PLAST: critico e uma ConfigCritico: {critico!r}")
            if critico.ligada:
                if not self.cd.p2 or self.cd.credito_corrida or self.cd.fala_unidades or self.cd.olhar or self.cd.unidades_sociais:
                    raise ValueError("o critico so com o P2 ligado, e nao se combina com a credito_corrida, a fala_unidades, o olhar nem "
                                     "as unidades_sociais (docs/TAREFA_V3_PLASTICIDADE_EVOLUIDA.md, 9.1: PROPOSTO, sem teste da combinacao)")
                self.cr = critico
                self.V = [0] * len(next(iter(self.H.values())))
                self.pendentes: list[dict] = []

    def montar(self, receptores: tuple) -> None:
        if self.receptores is None:
            self.receptores = tuple(receptores)
            self.desfecho = {c: [0] * len(self.receptores) for c in self.classes}
        elif tuple(receptores) != self.receptores:
            raise ValueError(f"M-PLAST: receptores {receptores}, montado com {self.receptores}")

    # ------------------------------------------------------------ o que vai ao M-IMPULSO
    def incentivo(self, pc, classe: str, drives: tuple) -> int:
        """o incentivo da classe, antes da proximidade: clamp(div_arred(c_G x valor_previsto, S_V), 0, G_max). Sem o P1, 0."""
        if not self.cd.p1:
            return 0
        p = self.p
        delta = dict(zip(self.receptores, self.desfecho[classe]))
        v = valor_previsto(pc, delta, drives, p.ganho_r, self.S)
        return clamp(div_arred(p.c_g * v, p.s_v), 0, p.g_max_incentivo)

    def habito(self, b: str, z: list) -> int:
        """o termo do habito do comportamento b: sum_j mul(H[b,j], z_j). Sem o P2, 0."""
        if not self.cd.p2:
            return 0
        total = 0
        for h, zj in zip(self.H[b], z):
            if h:
                total += mul(h, zj, self.S)
        return total

    # ------------------------------------------------------------ P1
    def _passo(self, valor: int, alvo: int, g_apr: int) -> int:
        return valor + mul(mul(g_apr, self.p.eta_d, self.S), alvo - valor, self.S)

    def consequencia_p1(self, acao: str, classe: str | None, l0: list, l1: list, pos0: tuple, pos1: tuple, g_apr: int) -> dict | None:
        """P1 na consequencia de comer (o andar e o consumo), de brincar com a bola (o consumo) ou, com a `unidades_sociais`, de explorar
        uma unidade social (a classe e o tipo). `classe` = o que foi consumido (None: nada). Devolve o registro da atualizacao do desfecho
        (None sem consumo)."""
        if not self.cd.p1:
            return None
        S = self.S
        d = raiz_inteira((pos1[0] - pos0[0]) * (pos1[0] - pos0[0]) + (pos1[1] - pos0[1]) * (pos1[1] - pos0[1]))
        ie = self.receptores.index("energia") if "energia" in self.receptores else None
        if acao == "comer" and d > 0 and ie is not None:
            amostra = div_arred((l1[ie] - l0[ie]) * S, d)
            self.andar = self._passo(self.andar, amostra, g_apr)
            self.amostras_andar += 1
        if classe is None:
            return None
        delta = [b - a for a, b in zip(l0, l1)]
        if ie is not None:
            delta[ie] -= div_arred(self.andar * d, S)
        return self.consumo(classe, delta, g_apr)

    def consequencia_olhar(self, l0: list, l1: list, g_apr: int) -> dict | None:
        """P1 na consequencia de olhar (P1d; espec, secao 5.3, a consequencia): o desfecho da classe `tela` anda para o Delta dos
        receptores, como no comer (sem o andar: olhar e parado). Sem o P1, None."""
        if not self.cd.p1:
            return None
        if CLASSE_TELA not in self.classes:
            raise RuntimeError("M-PLAST: a consequencia de olhar sem a subchave olhar")
        return self.consumo(CLASSE_TELA, [b - a for a, b in zip(l0, l1)], g_apr)

    def consumo(self, classe: str, delta: list, g_apr: int) -> dict:
        """um consumo percebido da classe: o desfecho anda em direcao a `delta` (os receptores, na ordem do layout)"""
        if classe not in self.classes:
            raise ValueError(f"M-PLAST: classe {classe!r}")
        if len(delta) != len(self.receptores) or any(type(v) is not int for v in delta):
            raise ValueError(f"M-PLAST: delta {delta!r} fora do layout {self.receptores}")
        dt = self.desfecho[classe]
        antes = list(dt)
        for i, v in enumerate(delta):
            dt[i] = clamp(self._passo(dt[i], v, g_apr), -self.S, self.S)
        self.consumos[classe] += 1
        return {"regra": "P1", "classe": classe, "antes": antes, "depois": list(dt), "abs": sum(abs(b - a) for a, b in zip(antes, dt))}

    def elogio_p1(self, classe: str, delta: list, g: int, g_apr: int) -> dict | None:
        """o carinho no desfecho da classe consumida (ELOGIO, D-EL-12; so com a ConfigElogio ligada): SOMA a ele o que o carinho mudou nos
        receptores (`delta`, na ordem do layout), com o ganho `g` (na escala S, ja com o peso da janela) e o passo do P1:
        `d[c,r] <- clamp(d[c,r] + mul(mul(g_apr, eta_d), div_arred(g x delta_r, S)), -S, S)`. Nao puxa para o alvo (o que a fruta ensinou
        fica) e nao conta como consumo. Sem o P1, None."""
        if not self.cd.p1:
            return None
        if classe not in self.classes:
            raise ValueError(f"M-PLAST: classe {classe!r}")
        if len(delta) != len(self.receptores) or any(type(v) is not int for v in delta):
            raise ValueError(f"M-PLAST: delta {delta!r} fora do layout {self.receptores}")
        S = self.S
        passo = mul(g_apr, self.p.eta_d, S)
        dt = self.desfecho[classe]
        antes = list(dt)
        for i, v in enumerate(delta):
            if v:
                dt[i] = clamp(dt[i] + mul(passo, div_arred(g * v, S), S), -S, S)
        return {"regra": "P1-elogio", "classe": classe, "antes": antes, "depois": list(dt), "abs": sum(abs(b - a) for a, b in zip(antes, dt))}

    # ------------------------------------------------------------ P2
    def creditar(self, op: dict) -> dict | None:
        """P2 numa opcao que acabou: so a linha do comportamento dela. Devolve o registro (None sem o P2)."""
        if not self.cd.p2:
            return None
        p, S = self.p, self.S
        b = linha_da_opcao(op["chave"], self.cd.fala_unidades)
        r_n = op["r"]
        if self.cr is not None:                       # o critico: a opcao espera o z de depois (o `fechar_pendentes`)
            if len(op["e"]) != len(self.V):
                raise ValueError(f"M-PLAST: a elegibilidade da opcao {op['chave']!r} fora do layout do V")
            self.pendentes.append({"b": b, "r": r_n, "g_apr": op["g_apr"], "e": list(op["e"])})
            return {"regra": "P2-critico", "b": b, "r_n": r_n, "pendente": True, "abs": 0}
        passo = mul(op["g_apr"], p.eta_h, S)
        linha = self.H[b]
        antes = list(linha)
        for j, e in enumerate(op["e"]):
            if e == 0:
                continue
            linha[j] = clamp(linha[j] + mul(passo, mul(r_n, e, S), S), -p.h_max, p.h_max)
        self.creditos += 1
        return {"regra": "P2", "b": b, "r_n": r_n, "abs": sum(abs(x - y) for x, y in zip(antes, linha))}

    # ------------------------------------------------------------ o critico (so com a ConfigCritico ligada)
    def valor(self, z: list) -> int:
        """V(z) = sum_j mul(v_j, z_j)"""
        if self.cr is None:
            raise RuntimeError("M-PLAST: o V sem a ConfigCritico ligada")
        if len(z) != len(self.V):
            raise ValueError(f"M-PLAST: z com {len(z)} caracteristicas, o V tem {len(self.V)}")
        return sum(mul(v, zj, self.S) for v, zj in zip(self.V, z) if v)

    def fechar_pendentes(self, z_depois: list) -> list[dict]:
        """as opcoes guardadas pelo `creditar` recebem o credito pelo erro de diferenca temporal, com `z_depois` as caracteristicas
        da decisao em que acabam (ou da seguinte). Na ordem em que acabaram; devolve um registro por opcao"""
        if self.cr is None:
            raise RuntimeError("M-PLAST: fechar_pendentes sem a ConfigCritico ligada")
        p, S, cr = self.p, self.S, self.cr
        out = []
        for op in self.pendentes:
            v0, v1 = self.valor(op["e"]), self.valor(z_depois)
            delta = clamp(op["r"] + mul(cr.gamma, v1, S) - v0, -S, S)
            passo_v = mul(mul(op["g_apr"], cr.eta_v, S), delta, S)
            passo_h = mul(op["g_apr"], p.eta_h, S)
            linha = self.H[op["b"]]
            antes_h, antes_v = list(linha), list(self.V)
            for j, e in enumerate(op["e"]):
                if e == 0:
                    continue
                self.V[j] = clamp(self.V[j] + mul(passo_v, e, S), -S, S)
                linha[j] = clamp(linha[j] + mul(passo_h, mul(delta, e, S), S), -p.h_max, p.h_max)
            self.creditos += 1
            out.append({"regra": "P2-critico", "b": op["b"], "r_n": op["r"], "v0": v0, "v1": v1, "delta": delta,
                        "abs": sum(abs(x - y) for x, y in zip(antes_h, linha)), "abs_v": sum(abs(x - y) for x, y in zip(antes_v, self.V))})
        self.pendentes = []
        return out

    # ------------------------------------------------------------ leituras
    def desfecho_zero(self) -> bool:
        return self.andar == 0 and (self.desfecho is None or all(v == 0 for dt in self.desfecho.values() for v in dt))

    def habito_zero(self) -> bool:
        return all(v == 0 for linha in self.H.values() for v in linha)

    def no_teto(self) -> tuple[int, int]:
        """(quantos H em +-H_max, quantos H): o G6 da V2 (PE-10)"""
        vs = [v for linha in self.H.values() for v in linha]
        return sum(1 for v in vs if abs(v) == self.p.h_max), len(vs)

    def estado_interno(self) -> dict:
        out = {"receptores": None if self.receptores is None else list(self.receptores), "desfecho": self.desfecho,
               "andar": self.andar, "H": {b: list(v) for b, v in self.H.items()}, "consumos": dict(self.consumos),
               "amostras_andar": self.amostras_andar, "creditos": self.creditos}
        if self.cr is not None:                       # o critico: desligado, nenhum campo novo
            out["critico"] = {"eta_v": self.cr.eta_v, "gamma": self.cr.gamma, "V": list(self.V),
                              "pendentes": [dict(op, e=list(op["e"])) for op in self.pendentes]}
        return out
