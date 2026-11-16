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
chamar a rng, e, como no reflexo, nenhuma sonda decide. Fora da lista ou com peso 0 (RE-2), o sorteio de hoje, e o registro marca `fora`.
**O sono que segura** (docs/TAREFA_V3_SONO_SEGURA.md; `Arbitragem(sono=ConfigSonoSegura(ligada=True))`): o reflexo tambem vale com o pet
dormindo (o `contexto["dormindo"]` do M-SENS, o `dormindo` do vetor de estado) e a energia abaixo de `lambda_acordar`, salvo com a fome
urgente (a urgencia da fome acima do `urgencia_lambda`, a guarda do passeio). O dono que acorda o pet tira o `dormindo`, e a decisao
seguinte ja nao segura. Nenhuma rng nova; desligada, o reflexo de hoje.
**A guarda da fome urgente no brincar** (docs/PLANO_V3_EQUILIBRIO_CUIDADO.md, EQ-7; `escolher(..., sem_brincar=True)`, que o M-ADAPT passa so
com a `ConfigEquilibrioCuidado.guarda_fome_brincar` ligada e a fome urgente): o peso de todas as unidades do brincar vira 0, no sorteio e nas
sondas, antes de contar os candidatos. Nenhuma rng nova; sem ela (o padrao), o sorteio de hoje."""
from __future__ import annotations

from ..config import CONFIG_DIGIBRAIN_INATOS, CONFIG_SONO_SEGURA, ConfigDigibrainInatos, ConfigSonoSegura
from . import dever as _dever
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

    def __init__(self, inatos: ConfigDigibrainInatos | None = None, autobio: bool = False, facetas: bool = False,
                 sono: ConfigSonoSegura | None = None) -> None:
        self.p = inatos or CONFIG_DIGIBRAIN_INATOS
        self.sono = sono or CONFIG_SONO_SEGURA
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
        self.dever = None                             # a CO7 (`ligar_dever`): a ConfigCooperacao; None desligada
        self.sorteios = 0
        self.reflexos = 0
        self.nada_a_fazer = 0

    def ligar_dever(self, cfg) -> None:
        """a CO7: o escudo e o peso da universalizacao (digilab/digibrain/dever.py) sobre os pesos, antes do sorteio e em cada sonda"""
        if not cfg.co7:
            raise ValueError("M-ARB: os deveres so com a subchave co7")
        self.dever = cfg

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

    def reflexo(self, sens: dict, urgencias: dict | None = None) -> bool:
        """o reflexo do sono: a leitura da energia abaixo de `lambda_sono` (a conta de sempre, sem rng). O M-ADAPT a chama uma vez por
        decisao e passa o valor ao M-ESTADO e ao `escolher` (a L-2, secao 2.3). Com o sono que segura, tambem o pet dormindo com a energia
        abaixo de `lambda_acordar` e sem a fome urgente; as `urgencias` sao as do M-AFETO da decisao (so lidas com a chave ligada)"""
        energia = sens["leitura"].get("energia")
        if energia is None:
            raise RuntimeError("M-ARB: o reflexo do sono le a energia, e ela nao esta na percepcao do corpo")
        if energia < self.p.lambda_sono:
            return True
        if not self.sono.ligada:
            return False
        if urgencias is None or "fome" not in urgencias:
            raise RuntimeError("M-ARB: o sono que segura le a urgencia da fome, e ela nao veio do M-AFETO")
        return sens["contexto"]["dormindo"] > 0 and energia < self.sono.lambda_acordar and urgencias["fome"] <= self.p.urgencia_lambda

    @staticmethod
    def _sem_brincar(unidades: list[dict], w: list[int]) -> list[int]:
        """a guarda da fome urgente no brincar (EQ-7): o peso 0 nas unidades do brincar"""
        return [0 if x["acao"] == "brincar" else wi for x, wi in zip(unidades, w)]

    def escolher(self, unidades: list[dict], afeto: dict, sens: dict, rng, reflexo: bool | None = None,
                 segurar: tuple | None = None, sem_brincar: bool = False) -> dict:
        p = self.p
        if reflexo is None:
            reflexo = self.reflexo(sens)
        if type(sem_brincar) is not bool:
            raise TypeError(f"M-ARB: sem_brincar e bool: {sem_brincar!r}")
        w = self.pesos([x["a"] for x in unidades], afeto["g_exp"])
        sit, reg = None, None
        if self.dever is not None and sens["social"] is not None:     # a CO7: o escudo e a universalizacao, antes de tudo
            sit = _dever.situacao(sens, afeto["urgencias"], self.dever, self.S)
            w, reg = _dever.ajustar(unidades, w, sit)
        if sem_brincar:                              # a guarda da fome urgente no brincar (EQ-7), depois da CO7 (D-EQ2-2)
            w = self._sem_brincar(unidades, w)
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
            ws = self.pesos(ativ, g_exp)
            if sit is not None:                      # a CO7: a sonda com o mesmo escudo e a mesma universalizacao
                ws = _dever.ajustar(unidades, ws, sit)[0]
            j = self._escolher(unidades, self._sem_brincar(unidades, ws) if sem_brincar else ws, u)
            sondas[nome] = chave_json(unidades[j]["chave"])
            sondas[self.decidiu[nome]] = j != i
        out = {"indice": i, "unidade": unidades[i], "u": u, "reflexo": reflexo, "nada_a_fazer": not reflexo and all(x == 0 for x in w),
               "pesos": w, "sondas": sondas, "segurada": segura is not None, "fora": segurar is not None and segura is None}
        if self.dever is not None:                    # a CO7: desligada, nenhum campo novo
            out["dever"] = None if sit is None else {**sit, "removidas": [chave_json(unidades[j]["chave"]) for j in reg["removidas"]],
                                                     "reprovadas": [chave_json(unidades[j]["chave"]) for j in reg["reprovadas"]],
                                                     "aprovadas": reg["aprovadas"]}
        return out

    def estado_interno(self) -> dict:
        return {"sorteios": self.sorteios, "reflexos": self.reflexos, "nada_a_fazer": self.nada_a_fazer}
