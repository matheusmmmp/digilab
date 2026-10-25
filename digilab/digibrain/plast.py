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
Sem rng."""
from __future__ import annotations

from ..config import CARACTERISTICAS_DIGIBRAIN, COMPORTAMENTOS_DIGIBRAIN, CONFIG_DIGIBRAIN_INATOS, ConfigDigibrain, ConfigDigibrainInatos
from ..modelo_mundo import raiz_inteira
from ..policies.lobos import div_arred, valor_previsto
from ._comum import clamp, mul

CLASSES_DESFECHO = ("racao", "a", "b", "c", "podre", "bola")


class Plasticidade:
    """o M-PLAST (docstring do modulo)"""

    def __init__(self, cfg_digibrain: ConfigDigibrain, inatos: ConfigDigibrainInatos | None = None) -> None:
        self.p = inatos or CONFIG_DIGIBRAIN_INATOS
        self.cd = cfg_digibrain
        self.S = self.p.escala
        self.receptores: tuple | None = None
        self.desfecho: dict | None = None             # classe -> [d_r na ordem dos receptores]
        self.andar = 0
        self.H = {b: [0] * len(CARACTERISTICAS_DIGIBRAIN) for b in COMPORTAMENTOS_DIGIBRAIN}
        self.consumos = {c: 0 for c in CLASSES_DESFECHO}
        self.amostras_andar = 0
        self.creditos = 0

    def montar(self, receptores: tuple) -> None:
        if self.receptores is None:
            self.receptores = tuple(receptores)
            self.desfecho = {c: [0] * len(self.receptores) for c in CLASSES_DESFECHO}
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
        """P1 na consequencia de comer (o andar e o consumo) ou de brincar com a bola (o consumo). `classe` = o que foi consumido (None:
        nada). Devolve o registro da atualizacao do desfecho (None sem consumo)."""
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

    def consumo(self, classe: str, delta: list, g_apr: int) -> dict:
        """um consumo percebido da classe: o desfecho anda em direcao a `delta` (os receptores, na ordem do layout)"""
        if classe not in CLASSES_DESFECHO:
            raise ValueError(f"M-PLAST: classe {classe!r}")
        if len(delta) != len(self.receptores) or any(type(v) is not int for v in delta):
            raise ValueError(f"M-PLAST: delta {delta!r} fora do layout {self.receptores}")
        dt = self.desfecho[classe]
        antes = list(dt)
        for i, v in enumerate(delta):
            dt[i] = clamp(self._passo(dt[i], v, g_apr), -self.S, self.S)
        self.consumos[classe] += 1
        return {"regra": "P1", "classe": classe, "antes": antes, "depois": list(dt), "abs": sum(abs(b - a) for a, b in zip(antes, dt))}

    # ------------------------------------------------------------ P2
    def creditar(self, op: dict) -> dict | None:
        """P2 numa opcao que acabou: so a linha do comportamento dela. Devolve o registro (None sem o P2)."""
        if not self.cd.p2:
            return None
        p, S = self.p, self.S
        b = op["chave"][0]
        r_n = op["r"]
        passo = mul(op["g_apr"], p.eta_h, S)
        linha = self.H[b]
        antes = list(linha)
        for j, e in enumerate(op["e"]):
            if e == 0:
                continue
            linha[j] = clamp(linha[j] + mul(passo, mul(r_n, e, S), S), -p.h_max, p.h_max)
        self.creditos += 1
        return {"regra": "P2", "b": b, "r_n": r_n, "abs": sum(abs(x - y) for x, y in zip(antes, linha))}

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
        return {"receptores": None if self.receptores is None else list(self.receptores), "desfecho": self.desfecho,
                "andar": self.andar, "H": {b: list(v) for b, v in self.H.items()}, "consumos": dict(self.consumos),
                "amostras_andar": self.amostras_andar, "creditos": self.creditos}
