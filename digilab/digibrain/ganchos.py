"""Os ganchos que ficam vazios no prototipo: M-PERS, M-GEN e M-EXPR (docs/ESPEC_DIGIBRAIN_MODULAR.md, secao 4.9). Esqueleto da etapa 0:
sem numero e sem equacao."""
from __future__ import annotations

from ._comum import sem_equacao


class Personalidade:
    """M-PERS: as facetas; o temperamento inato fica fora do alcance delas (DM-6)"""

    def faceta(self, nome: str) -> int:
        raise sem_equacao("M-PERS", "faceta")

    def mudar_faceta(self, nome: str, passo: int, episodios) -> None:
        raise sem_equacao("M-PERS", "mudar_faceta")


class ParametrosInatos:
    """M-GEN: o registro unico dos parametros inatos, por modulo, que o genoma futuro escreve; o aprendido nunca entra nele (EG-5)"""

    def do_modulo(self, modulo: str) -> dict:
        raise sem_equacao("M-GEN", "do_modulo")


class Expressao:
    """M-EXPR: le so o registro da decisao, fora do cerebro, e nao decide nada"""

    def expressar(self, registro):
        raise sem_equacao("M-EXPR", "expressar")
