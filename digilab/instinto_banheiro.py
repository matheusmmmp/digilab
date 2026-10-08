"""O instinto do alivio (V2; docs/TAREFA_V2_BANHEIRO.md, secao 4, etapa 2; BN-1 decidida em 2026-10-07).

O pet sente a vontade de fazer as necessidades pelo receptor do corpo (`Observacao.corpo.vontade`, a concentracao na escala S; o quimico e
do `corpo.py`, sub-chave `banheiro`). O `PoliticaInstintoBanheiro` e o instinto do mundo fisico (`PoliticaInstintoMundo`) com tres pontos
a mais:
- **a regra urgente** (`alivio_urgente`): acordado e com a vontade acima de `limiar_urgente` (0,90), alivia ja, sem sorteio. Vem logo
  depois das regras de sono e antes do pedido de necessidade. O alvo e sempre `aqui` (o acidente). E a regra que o pet nao aprende (um
  candidato so);
- **o tempo livre** (as regras `tempo_livre`, `bola_no_cenario` e `fruta_no_cenario`): com a vontade acima de `limiar_moderada` (0,50),
  `aliviar` entra como candidato novo, no fim, com peso `w_vontade x vontade`, na mesma chamada de `rng.choices`;
- **o alvo herdado** (`escolher_alvo`, o gancho do MotorMundo): no `aliviar`, `banheiro` com peso `w_banheiro_0 / S` e `aqui` com
  `w_aqui_0 / S` (S/4 e S: o pet nasce preferindo `aqui` 4 a 1), sorteados com o u do motor (inteiro em [0, 2^16), u / 2^16), a conta de
  `random.choices` passo a passo. Na regra urgente, `aqui`. Nas outras acoes, None (o padrao do motor).
Dormindo (as regras de sono), nao alivia.

O motor com o banheiro (o mapa, a necessidade, o limpador, o candidato `banheiro`) e a etapa 3, do A. O contrato do alvo: no `aliviar`, o
motor sorteia u da rng `alvo` e passa ao gancho os dois candidatos, um `Alvo` de tipo `banheiro` (o ponto mais proximo do banheiro) e um
de tipo `aqui` (a posicao do pet); o gancho devolve um deles.
"""

from __future__ import annotations

import random
from bisect import bisect_right
from itertools import accumulate

from .config import CONFIG_PADRAO, Config, ConfigBanheiro, ConfigBola, ConfigCorpo, ConfigFrutas
from .events import AcaoPet
from .instinto_mundo import PoliticaInstintoMundo
from .policy import Observacao

REGRA_ALIVIO_URGENTE = "alivio_urgente"
ALVOS_ALIVIO = ("banheiro", "aqui")
ESCALA_U_ALVO = 1 << 16                  # o u do alvo do MotorMundo: inteiro em [0, 2^16)

# Status dos campos da ConfigBanheiro (conferido por teste). Todos PROPOSTOS, sem fonte, nenhum referendado.
PARAMETROS_BANHEIRO: dict[str, tuple[str, str]] = {
    "ligada": ("DECIDIDO", "BN-1 a BN-6 (TAREFA_V2_BANHEIRO, secao 10): desligada por padrao, a vida de hoje"),
    "limpador": ("PROPOSTO", "TAREFA_V2_BANHEIRO, secao 3: desligado por padrao; o desenho 2 x 2 o liga (secao 6)"),
    "w_vontade": ("PROPOSTO", "secao 4: sem fonte; o plano calibra (m_w, PLANO_ANALISE_V2_BANHEIRO, 6.2)"),
    "limiar_urgente": ("PROPOSTO", "secao 4: 0,90, sem fonte"),
    "limiar_moderada": ("PROPOSTO", "secao 4: 0,50, sem fonte"),
    "w_banheiro_0": ("PROPOSTO", "secao 4: S/4, o pet nasce preferindo `aqui` 4 a 1, sem fonte"),
    "w_aqui_0": ("PROPOSTO", "secao 4: S, sem fonte"),
}


def sortear_alvo(pesos: list[float], u: int) -> int:
    """O indice sorteado com os pesos, dado o u inteiro do motor: a conta de random.choices(k=1) com u / 2^16 no lugar de rng.random()
    (a mesma de lobos.sortear; conferido por teste)."""
    if type(u) is not int or not 0 <= u < ESCALA_U_ALVO:
        raise ValueError(f"u do alvo fora de inteiros em [0, 2^16): {u!r}")
    cumulativa = list(accumulate(pesos))
    total = cumulativa[-1] + 0.0
    if total <= 0.0:
        raise ValueError(f"soma dos pesos do alvo nao positiva: {pesos}")
    return bisect_right(cumulativa, (u / ESCALA_U_ALVO) * total, 0, len(cumulativa) - 1)


def tipos_do_alivio(candidatos: list) -> list[str]:
    """Os tipos dos candidatos do alvo do `aliviar`: exatamente `banheiro` e `aqui` (em qualquer ordem); outra coisa falha alto."""
    tipos = [c.tipo for c in candidatos]
    if sorted(tipos) != sorted(ALVOS_ALIVIO):
        raise ValueError(f"candidatos do alvo do aliviar: esperava {ALVOS_ALIVIO}, veio {tipos}")
    return tipos


def vontade_de(obs: Observacao, S: int) -> float:
    """A vontade lida pelo receptor (leitura / S). Sem o corpo, ou com o corpo sem o banheiro, falha alto."""
    pc = obs.corpo
    if pc is None or pc.vontade is None:
        raise RuntimeError("banheiro: Observacao sem o receptor da vontade (o corpo com a sub-chave banheiro)")
    v = pc.vontade
    if type(v) is not int or not 0 <= v <= S:
        raise ValueError(f"receptor da vontade fora de inteiros em [0, {S}]: {v!r}")
    return v / S


class PoliticaInstintoBanheiro(PoliticaInstintoMundo):
    """O instinto do mundo fisico com o alivio (docstring do modulo)."""

    nome = "instinto_banheiro"

    def __init__(self, cfg: Config | None = None, cfg_banheiro: ConfigBanheiro | None = None, cfg_corpo: ConfigCorpo | None = None,
                 cfg_bola: ConfigBola | None = None, cfg_frutas: ConfigFrutas | None = None, sem_explorar: bool = False) -> None:
        super().__init__(cfg or CONFIG_PADRAO, cfg_bola, cfg_frutas, sem_explorar)
        if cfg_banheiro is None or not cfg_banheiro.ligada:
            raise ValueError("PoliticaInstintoBanheiro sem a ConfigBanheiro ligada")
        if cfg_corpo is None or not cfg_corpo.banheiro:
            raise ValueError("PoliticaInstintoBanheiro sem o corpo com a sub-chave banheiro (a vontade)")
        self.cb = cfg_banheiro
        self.S = cfg_corpo.escala_receptor
        for nome in ("w_banheiro_0", "w_aqui_0"):
            v = getattr(cfg_banheiro, nome)
            if v >= 1 << 30:                                  # pragma: no cover - so para o float w / S ser exato
                raise ValueError(f"ConfigBanheiro.{nome} grande demais: {v}")
        self._vontade = 0.0                                   # a vontade da ultima decisao (o tempo livre a le)

    def _dormindo(self, obs: Observacao) -> bool:
        """As regras de sono do PoliticaInstinto, com os mesmos literais e na mesma ordem (nao usam a rng)."""
        fome, higiene, energia, humor, saude, sujeira, dormindo, hora = obs.vetor_estado
        return (energia < 0.25 or (dormindo > 0.5 and energia < 0.85)
                or (self.cfg.e_noite(int(hora * 1440)) and energia < 0.55))

    def agir(self, obs: Observacao, rng: random.Random) -> AcaoPet:
        self._vontade = vontade_de(obs, self.S)
        if not self._dormindo(obs) and self._vontade > self.cb.limiar_urgente:
            self._ultima_regra = REGRA_ALIVIO_URGENTE                # sem sorteio: a rng nao anda
            return AcaoPet.ALIVIAR
        return super().agir(obs, rng)

    def _pesos_tempo_livre(self, energia: float, humor: float, obs: Observacao) -> dict:
        pesos = super()._pesos_tempo_livre(energia, humor, obs)     # os do mundo, na mesma ordem
        if self._vontade > self.cb.limiar_moderada:
            pesos[AcaoPet.ALIVIAR] = self.cb.w_vontade * self._vontade    # candidato novo, no fim (a regra fica a do tempo livre)
        return pesos

    def escolher_alvo(self, acao: AcaoPet, candidatos: list, percepcao, u: int):
        """O alvo herdado do `aliviar` (docstring do modulo); nas outras acoes, None (o padrao do motor)."""
        if acao is not AcaoPet.ALIVIAR:
            return None
        tipos = tipos_do_alivio(candidatos)
        if self._ultima_regra == REGRA_ALIVIO_URGENTE:
            return candidatos[tipos.index("aqui")]
        herdado = {"banheiro": self.cb.w_banheiro_0, "aqui": self.cb.w_aqui_0}
        return candidatos[sortear_alvo([herdado[t] / self.S for t in tipos], u)]

    def estado_interno(self) -> dict:
        d = super().estado_interno()
        d["nome"] = self.nome
        d["banheiro"] = {"w_vontade": self.cb.w_vontade, "limiar_urgente": self.cb.limiar_urgente,
                         "limiar_moderada": self.cb.limiar_moderada, "w_banheiro_0": self.cb.w_banheiro_0,
                         "w_aqui_0": self.cb.w_aqui_0}
        return d
