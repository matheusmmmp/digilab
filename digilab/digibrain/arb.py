"""M-ARB, a arbitragem (docs/ESPEC_DIGIBRAIN_MODULAR.md, secoes 4.7 e 7; PE-5: o sorteio proporcional).

1. **O reflexo do sono:** com a leitura da energia abaixo de `lambda_sono`, dormir, sem sorteio (fora da disputa, como o `sono_exaustao`
   da V3-4).
2. **Os pesos:** `w[b,o] = a[b,o] + mul(g_exp, epsilon)` nas unidades com a > 0; 0 nas outras (a unidade a 0 nao concorre).
3. **O sorteio:** com dois candidatos (pesos > 0) ou mais, uma chamada `rng.random()` (a de politica, a unica do cerebro); com a soma
   inteira T, o alvo `min(int(u x T), T - 1)` (o `min` guarda o arredondamento de u x T perto de 1) e a escolha e a primeira unidade cuja
   soma acumulada passa dele, na ordem fixa. E a conta do `sortear` do A, em inteiros. Com um candidato so, ele, sem sorteio; com nenhum,
   ocioso, sem sorteio, e o registro marca o "nada a fazer".
**As sondas "quem decidiu"** (secao 7), so de leitura: a mesma decisao com o termo de um modulo zerado, sorteada com o mesmo u:
  sem_incentivo, sem_habito, sem_memoria, sem_persistencia; sem_afeto (o g_exp neutro, e0); so_inato (sem os quatro termos aprendidos e de
  estado). O modulo decidiu se a escolha muda. Sem a memoria (sem_memoria e so_inato), a unidade do lugar lembrado sai inteira: ela so
  existe porque o M-MEM recuperou o lugar (PROPOSTO). Sem u (um candidato so na decisao), uma sonda com dois candidatos ou mais fica com o de
  maior peso (o primeiro no empate), PROPOSTO; no reflexo, nenhuma sonda decide.
**A C4, M4** (docs/ESPEC_MEMORIA_AUTOBIOGRAFICA_DIGIBRAIN_MODULAR.md, secao 6.1; `Arbitragem(autobio=True)`): a sonda `sem_memoria` tira
tambem o termo `lembranca` (e `so_inato`, que tira o aprendido); a sonda nova `sem_lembranca` tira so ele, com `lembranca_decidiu`.
Mesmo u, nenhuma rng nova. Desligada, as sondas sao as de hoje.
**A C4, M5** (secao 6.2; `Arbitragem(facetas=True)`, so com a memoria autobiografica): a sonda nova `sem_faceta` tira so o termo `faceta`,
com `faceta_decidiu`; `so_inato` tira tambem a faceta (e aprendida). Mesmo u, nenhuma rng nova.
**A escolha segurada** (a C3, docs/ESPEC_REDECIDIR_EVENTO_DIGIBRAIN_MODULAR.md, secao 2; so com a subchave `redecidir_evento`): sem evento,
o M-ADAPT passa o candidato (`segurar`, a chave da escolha anterior); com ele na lista e peso positivo, o M-ARB o escolhe sem sorteio e sem
chamar a rng, e, como no reflexo, nenhuma sonda decide. Fora da lista ou com peso 0 (RE-2), o sorteio de hoje, e o registro marca `fora`."""
from __future__ import annotations

from ..config import CONFIG_DIGIBRAIN_INATOS, ConfigDigibrainInatos
from ._comum import chave_json, mul, phi

SONDAS = {"sem_incentivo": ("incentivo",), "sem_habito": ("habito",), "sem_memoria": ("memoria",), "sem_persistencia": ("persistencia",),
          "sem_afeto": (), "so_inato": ("incentivo", "habito", "memoria", "persistencia")}
DECIDIU = {"sem_incentivo": "incentivo_decidiu", "sem_habito": "habito_decidiu", "sem_memoria": "memoria_decidiu",
           "sem_persistencia": "persistencia_decidiu", "sem_afeto": "afeto_decidiu", "so_inato": "aprendido_decidiu"}


def sortear_inteiro(pesos: list[int], u) -> int:
    """o indice sorteado: a primeira soma acumulada que passa de min(int(u x T), T - 1)"""
    total = sum(pesos)
    if total <= 0:
        raise ValueError(f"M-ARB: soma dos pesos nao positiva: {pesos}")
    alvo = min(int(u * total), total - 1)
    acumulado = 0
    for i, w in enumerate(pesos):
        acumulado += w
        if acumulado > alvo:
            return i
    raise RuntimeError("M-ARB: o sorteio passou do fim")   # pragma: no cover - alvo < T


class Arbitragem:
    """o M-ARB (docstring do modulo)"""

    def __init__(self, inatos: ConfigDigibrainInatos | None = None, autobio: bool = False, facetas: bool = False) -> None:
        self.p = inatos or CONFIG_DIGIBRAIN_INATOS
        self.sondas = SONDAS
        self.decidiu = DECIDIU
        if autobio:                                   # a C4, M4 (6.1): sem_memoria tira tambem a lembranca; sem_lembranca tira so ela
            self.sondas = {**{n: t + ("lembranca",) if n in ("sem_memoria", "so_inato") else t for n, t in SONDAS.items()},
                           "sem_lembranca": ("lembranca",)}
            self.decidiu = {**DECIDIU, "sem_lembranca": "lembranca_decidiu"}
        if facetas:                                   # a C4, M5 (6.2): sem_faceta tira so o termo F; so_inato tira tambem (e aprendido)
            self.sondas = {**{n: t + ("faceta",) if n == "so_inato" else t for n, t in self.sondas.items()}, "sem_faceta": ("faceta",)}
            self.decidiu = {**self.decidiu, "sem_faceta": "faceta_decidiu"}
        self.S = self.p.escala
        self.sorteios = 0
        self.reflexos = 0
        self.nada_a_fazer = 0

    def pesos(self, ativacoes: list[int], g_exp: int) -> list[int]:
        extra = mul(g_exp, self.p.epsilon, self.S)
        return [a + extra if a > 0 else 0 for a in ativacoes]

    @staticmethod
    def _ocioso(unidades: list[dict]) -> int:
        return next(i for i, u in enumerate(unidades) if u["acao"] == "ocioso")

    def _escolher(self, unidades: list[dict], w: list[int], u) -> int:
        positivos = [i for i, x in enumerate(w) if x > 0]
        if not positivos:
            return self._ocioso(unidades)
        if len(positivos) == 1:
            return positivos[0]
        if u is None:
            return max(positivos, key=lambda i: (w[i], -i))
        return sortear_inteiro(w, u)

    def reflexo(self, sens: dict) -> bool:
        """o reflexo do sono: a leitura da energia abaixo de `lambda_sono` (a conta de sempre, sem rng). O M-ADAPT a chama uma vez por
        decisao e passa o valor ao M-ESTADO e ao `escolher` (a L-2, secao 2.3)"""
        energia = sens["leitura"].get("energia")
        if energia is None:
            raise RuntimeError("M-ARB: o reflexo do sono le a energia, e ela nao esta na percepcao do corpo")
        return energia < self.p.lambda_sono

    def escolher(self, unidades: list[dict], afeto: dict, sens: dict, rng, reflexo: bool | None = None,
                 segurar: tuple | None = None) -> dict:
        p = self.p
        if reflexo is None:
            reflexo = self.reflexo(sens)
        w = self.pesos([x["a"] for x in unidades], afeto["g_exp"])
        if reflexo and segurar is not None:
            raise RuntimeError("M-ARB: a escolha segurada com o reflexo do sono (o reflexo e evento)")
        segura = None if segurar is None else next((j for j, x in enumerate(unidades) if x["chave"] == segurar and w[j] > 0), None)
        if segura is not None:
            i = segura
            u = None
        elif reflexo:
            i = next(j for j, x in enumerate(unidades) if x["acao"] == "dormir")
            u = None
            self.reflexos += 1
        else:
            n_pos = sum(1 for x in w if x > 0)
            u = rng.random() if n_pos >= 2 else None
            if u is not None:
                self.sorteios += 1
            if n_pos == 0:
                self.nada_a_fazer += 1
            i = self._escolher(unidades, w, u)
        sondas: dict = {}
        for nome, tirar in self.sondas.items():
            if reflexo or segura is not None:
                sondas[nome] = chave_json(unidades[i]["chave"])
                sondas[self.decidiu[nome]] = False
                continue
            ativ = [0 if ("memoria" in tirar and x.get("tipo") == "ponto") else phi(x["soma"] - sum(x["termos"][t] for t in tirar), p.a_max)
                    for x in unidades]
            g_exp = p.e0 if nome == "sem_afeto" else afeto["g_exp"]
            j = self._escolher(unidades, self.pesos(ativ, g_exp), u)
            sondas[nome] = chave_json(unidades[j]["chave"])
            sondas[self.decidiu[nome]] = j != i
        return {"indice": i, "unidade": unidades[i], "u": u, "reflexo": reflexo, "nada_a_fazer": not reflexo and all(x == 0 for x in w),
                "pesos": w, "sondas": sondas, "segurada": segura is not None, "fora": segurar is not None and segura is None}

    def estado_interno(self) -> dict:
        return {"sorteios": self.sorteios, "reflexos": self.reflexos, "nada_a_fazer": self.nada_a_fazer}
