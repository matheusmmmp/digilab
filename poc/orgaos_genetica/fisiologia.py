"""O orgao digestivo e o hormonio da POC, em inteiros.

Quimicos, todos em [0, ESCALA]:
- `estomago`: o alimento ainda nao digerido;
- `energia`: sobe com o que se digere (`conversao_pct` do digerido) e cai pelo `gasto_basal` a cada tick;
- `fome`: sobe `ganho_fome` por tick e cai na mesma quantidade do que se digere;
- `saciedade`: o hormonio. A digestao o emite (a mesma quantidade digerida) e ele decai 1/`decaimento_saciedade` por tick.

A resposta fisiologica que o hormonio altera: o ganho de fome por tick. O receptor le a saciedade com o ganho `sensibilidade_saciedade`
(em milesimos) e corta essa fracao do ganho de fome. Sem refeicao, a saciedade e 0 e a fome sobe no ritmo inato.

Ordem dentro de um tick (declarada, fixa): digestao -> emissao do hormonio -> receptor corta o ganho de fome -> decaimento do hormonio
-> gasto basal. O que passa do teto e descartado e contado, como o corte da digestao do corpo de hoje; nada some em silencio.

Desenho da POC, inspirado no conceito de bioquimica do Creatures; SEM FONTE para os numeros e para as relacoes, que nao se alegam
biologicas.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .genoma import ESCALA, Genoma

QUIMICOS = ("estomago", "energia", "fome", "saciedade")


@dataclass
class Fisiologia:
    genoma: Genoma
    estomago: int = 0
    energia: int = ESCALA // 2
    fome: int = ESCALA // 2
    saciedade: int = 0
    # as contas, para conferir a conservacao: o que entrou, o que se digeriu e o que se descartou por teto
    contas: dict[str, int] = field(default_factory=lambda: {
        "ingerido": 0, "digerido": 0, "descarte_estomago": 0, "descarte_energia": 0, "fome_cortada_hormonio": 0, "ticks": 0})

    def _conferir(self) -> None:
        for q in QUIMICOS:
            v = getattr(self, q)
            if type(v) is not int or not 0 <= v <= ESCALA:
                raise AssertionError(f"quimico {q} = {v!r} fora de [0, {ESCALA}]")

    def comer(self, quantidade: int) -> None:
        if type(quantidade) is not int or quantidade <= 0:
            raise ValueError(f"quantidade de comida invalida: {quantidade!r}")
        cabe = ESCALA - self.estomago
        entra = min(cabe, quantidade)
        self.estomago += entra
        self.contas["ingerido"] += quantidade
        self.contas["descarte_estomago"] += quantidade - entra
        self._conferir()

    def receptor_saciedade(self) -> int:
        """A fracao (em milesimos) do ganho de fome que o hormonio corta agora, no maximo 1000."""
        return min(1000, self.genoma["sensibilidade_saciedade"] * self.saciedade // ESCALA)

    def tick(self) -> None:
        g = self.genoma
        # 1. digestao: o estomago passa ate `taxa_digestao`; a fome cai o mesmo tanto; a energia ganha a conversao
        digerido = min(self.estomago, g["taxa_digestao"])
        self.estomago -= digerido
        self.fome = max(0, self.fome - digerido)
        ganho_e = digerido * g["conversao_pct"] // 100
        self.contas["descarte_energia"] += max(0, self.energia + ganho_e - ESCALA)
        self.energia = min(ESCALA, self.energia + ganho_e)
        self.contas["digerido"] += digerido
        # 2. emissao do hormonio pela digestao
        self.saciedade = min(ESCALA, self.saciedade + digerido)
        # 3. o receptor corta parte do ganho de fome
        corte = self.receptor_saciedade()
        ganho_f = g["ganho_fome"] * (1000 - corte) // 1000
        self.contas["fome_cortada_hormonio"] += g["ganho_fome"] - ganho_f
        self.fome = min(ESCALA, self.fome + ganho_f)
        # 4. decaimento do hormonio (pelo menos 1 enquanto houver, para nao ficar preso num resto pequeno)
        if self.saciedade:
            self.saciedade -= max(1, self.saciedade // g["decaimento_saciedade"])
        # 5. gasto basal
        self.energia = max(0, self.energia - g["gasto_basal"])
        self.contas["ticks"] += 1
        self._conferir()

    def estado(self) -> tuple[int, int, int, int]:
        return (self.estomago, self.energia, self.fome, self.saciedade)
