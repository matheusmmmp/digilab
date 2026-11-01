"""M-PERS, a personalidade adquirida (a C4, M5: docs/ESPEC_MEMORIA_AUTOBIOGRAFICA_DIGIBRAIN_MODULAR.md, secao 6.2; subchave `facetas_mem`,
desligada por padrao).

**As tres facetas** (MA-5), cada uma um inteiro em [-teto, teto] (o teto e S/4), todas em 0 no nascimento:
  - `cautela_comida`  (positiva = mais cautela com a comida; o termo F, no M-IMPULSO, e `-mul(f, S)` no `comer` de classe ainda sem
    episodio positivo);
  - `apego_dono`      (o termo F e `mul(f, S)` no `chamar_atencao`);
  - `ousadia_longe`   (o termo F e `mul(f, S)` no `explorar` com alvo fora da vista: o lugar lembrado e o cheiro).
**A mudanca** (`mudar_faceta`, na consolidacao diaria): um passo de no maximo `eta_faceta` (S/64), cortado no teto; cada mudanca guarda
a faceta, o dia, o passo, o valor antes e depois e os ids dos episodios da evidencia (ME-4). Um valor que o corte deixa igual nao e
mudanca e nao entra no registro.
**O que o modulo nao tem:** acesso a `ConfigDigibrainInatos` nem ao genoma (DM-6, ME-7, EG-5): ele recebe o passo e o teto como inteiros
na construcao e so le e escreve as proprias tres facetas. O temperamento inato (o registro de parametros inatos) fica fora do alcance
dele; um teste confere pela AST e compara o registro no nascimento e no fim da vida. Sem rng. Aritmetica so inteira."""
from __future__ import annotations

from ._comum import clamp, sem_equacao

FACETAS = ("cautela_comida", "apego_dono", "ousadia_longe")
# o sentido do passo em relacao ao sinal da soma dos sigma da evidencia (PROPOSTO, SEM FONTE; ver o registro de desvios): a cautela com a
# comida cresce quando os episodios de comer deixaram sigma negativo (a positiva e mais cautela, 6.2); as outras andam no sinal da soma
SENTIDO = {"cautela_comida": -1, "apego_dono": 1, "ousadia_longe": 1}


class Personalidade:
    """o M-PERS (docstring do modulo). Sem `ligada`, nao ha faceta: a leitura e o neutro (0) e a mudanca falha alto"""

    NEUTRO = 0

    def __init__(self, eta: int = 0, teto: int = 0, ligada: bool = False) -> None:
        if ligada and not 0 < eta <= teto:
            raise ValueError(f"M-PERS: o passo {eta!r} e o teto {teto!r} (0 < passo <= teto)")
        self.ligada, self.eta, self.teto = ligada, eta, teto
        self.valores = dict.fromkeys(FACETAS, self.NEUTRO)
        self.mudancas: list[dict] = []

    def faceta(self, nome: str) -> int:
        if not self.ligada:                           # sem a subchave: o neutro, qualquer nome (o gancho do prototipo)
            return self.NEUTRO
        if nome not in FACETAS:
            raise KeyError(f"M-PERS: faceta {nome!r}")
        return self.valores[nome]

    def mudar_faceta(self, nome: str, passo: int, episodios, dia: int | None = None) -> dict | None:
        """anda a faceta `passo` (|passo| <= eta), cortada em [-teto, teto]; devolve a mudanca registrada ou None se o valor nao mudou"""
        if not self.ligada:
            raise sem_equacao("M-PERS", "mudar_faceta")
        if nome not in FACETAS:
            raise KeyError(f"M-PERS: faceta {nome!r}")
        if type(passo) is not int or abs(passo) > self.eta:
            raise ValueError(f"M-PERS: o passo {passo!r} passa de eta_faceta ({self.eta})")
        ids = [e for e in episodios]
        if passo != 0 and not ids:
            raise ValueError("M-PERS: uma mudanca de faceta sem os ids dos episodios que a causaram")
        antes = self.valores[nome]
        depois = clamp(antes + passo, -self.teto, self.teto)
        if depois == antes:
            return None
        self.valores[nome] = depois
        reg = {"faceta": nome, "dia": dia, "passo": passo, "antes": antes, "depois": depois, "episodios": ids}
        self.mudancas.append(reg)
        return reg

    def estado_interno(self) -> dict:
        return {"valores": dict(self.valores), "mudancas": [dict(m) for m in self.mudancas]}
