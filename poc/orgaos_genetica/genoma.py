"""Os genes da POC: parametros inatos do orgao digestivo e do hormonio, e o cruzamento de dois genomas.

Regras (as do desenho em `docs/futuro/ecossistema_genetico.md`, so como guia; nada aqui as implementa no projeto):
- codificacao direta (EG-3): um gene e um inteiro, com faixa declarada; fora da faixa falha alto;
- recombinacao por gene (EG-4): a media dos pais mais uma mutacao pequena, numa rng propria derivada da semente do cruzamento;
- o aprendido nunca entra (EG-5): o genoma so tem os genes abaixo, e o cruzamento so aceita `Genoma`.

Todos os numeros sao exemplos da POC, SEM FONTE.
"""
from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass

# a escala dos quimicos da POC (energia, fome, estomago, saciedade vao de 0 a ESCALA); exemplo, nao e o C = 450000 do corpo
ESCALA = 10000


@dataclass(frozen=True)
class Gene:
    nome: str
    minimo: int
    maximo: int
    padrao: int
    passo_mutacao: int   # o tamanho de uma mutacao (para cima ou para baixo)
    o_que_faz: str


# PROPOSTO, SEM FONTE: valores de exemplo, escolhidos so para que a POC tenha dinamica visivel em poucas centenas de ticks
GENES: tuple[Gene, ...] = (
    Gene("taxa_digestao", 200, 2000, 800, 90, "quanto alimento o estomago digere por tick"),
    Gene("conversao_pct", 30, 90, 60, 3, "a porcentagem do digerido que vira energia"),
    Gene("gasto_basal", 5, 40, 15, 2, "a energia gasta por tick"),
    Gene("ganho_fome", 10, 60, 25, 3, "o quanto a fome sobe por tick, sem hormonio"),
    Gene("sensibilidade_saciedade", 0, 1000, 500, 50, "o ganho do receptor do hormonio, em milesimos"),
    Gene("decaimento_saciedade", 4, 60, 20, 3, "a constante de decaimento do hormonio: perde 1/d por tick"),
)
NOMES = tuple(g.nome for g in GENES)
_POR_NOME = {g.nome: g for g in GENES}

# a chance de mutacao por gene, em milesimos; PROPOSTO, SEM FONTE
MUTACAO_POR_MIL = 150


def derivar_semente(*rotulos: object) -> int:
    """Copia local de `digilab.protocol.derivar_semente` (sha256 dos rotulos), para a POC nao importar o pacote principal."""
    texto = "|".join(str(r) for r in rotulos)
    return int.from_bytes(hashlib.sha256(texto.encode("utf-8")).digest()[:8], "big")


@dataclass(frozen=True)
class Genoma:
    valores: tuple[int, ...]

    def __post_init__(self) -> None:
        if len(self.valores) != len(GENES):
            raise ValueError(f"genoma com {len(self.valores)} genes, esperados {len(GENES)}")
        for g, v in zip(GENES, self.valores):
            if type(v) is not int:
                raise TypeError(f"gene {g.nome} nao e inteiro: {v!r}")
            if not g.minimo <= v <= g.maximo:
                raise ValueError(f"gene {g.nome} = {v} fora da faixa [{g.minimo}, {g.maximo}]")

    def __getitem__(self, nome: str) -> int:
        if nome not in _POR_NOME:
            raise KeyError(f"gene desconhecido: {nome}")
        return self.valores[NOMES.index(nome)]

    def como_dict(self) -> dict[str, int]:
        return dict(zip(NOMES, self.valores))

    def sha256(self) -> str:
        return hashlib.sha256(json.dumps(self.como_dict(), sort_keys=True).encode("ascii")).hexdigest()

    @classmethod
    def de_dict(cls, d: dict[str, int]) -> "Genoma":
        if set(d) != set(NOMES):
            raise ValueError(f"genes diferentes dos declarados: sobram {set(d) - set(NOMES)}, faltam {set(NOMES) - set(d)}")
        return cls(tuple(d[n] for n in NOMES))


def padrao() -> Genoma:
    return Genoma(tuple(g.padrao for g in GENES))


def sortear(semente: int) -> Genoma:
    """Um genoma de ovo: cada gene uniforme na faixa, numa rng propria."""
    rng = random.Random(derivar_semente("poc-genoma-ovo", semente))
    return Genoma(tuple(rng.randint(g.minimo, g.maximo) for g in GENES))


@dataclass(frozen=True)
class Cruzamento:
    filho: Genoma
    mutacoes: tuple[tuple[str, int], ...]   # (gene, delta) de cada mutacao sorteada, para o relato


def cruzar(pai: Genoma, mae: Genoma, semente: int, mutacao_por_mil: int = MUTACAO_POR_MIL) -> Cruzamento:
    """O filho: por gene, a media inteira dos pais (empate arredonda para o par, sem float) mais, com chance `mutacao_por_mil`, um
    passo de mutacao para cima ou para baixo, cortado na faixa. So recebe genomas: nada do que os pais viveram entra."""
    if not isinstance(pai, Genoma) or not isinstance(mae, Genoma):
        raise TypeError("cruzar so aceita Genoma; estado aprendido ou fisiologico nao se herda")
    if not 0 <= mutacao_por_mil <= 1000:
        raise ValueError(f"mutacao_por_mil fora de [0, 1000]: {mutacao_por_mil}")
    rng = random.Random(derivar_semente("poc-heranca", semente, pai.sha256(), mae.sha256()))
    valores, mutacoes = [], []
    for g, a, b in zip(GENES, pai.valores, mae.valores):
        q, r = divmod(a + b, 2)
        v = q + (r and (q % 2))          # meia unidade: arredonda para o par
        # duas chamadas por gene, sempre, para o fluxo da rng nao depender de ter havido mutacao
        sorteio, sinal = rng.randrange(1000), rng.choice((-1, 1))
        if sorteio < mutacao_por_mil:
            novo = min(g.maximo, max(g.minimo, v + sinal * g.passo_mutacao))
            if novo != v:
                mutacoes.append((g.nome, novo - v))
            v = novo
        valores.append(v)
    return Cruzamento(Genoma(tuple(valores)), tuple(mutacoes))
