"""O que os modulos do DigiBrain modular dividem na etapa 0 (docs/TAREFA_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md): o erro dos modulos ainda sem
equacao. Nenhuma conta."""
from __future__ import annotations


def sem_equacao(modulo: str, metodo: str) -> NotImplementedError:
    """o erro de um modulo sem equacao: a etapa 0 so tem o esqueleto (docs/ESPEC_DIGIBRAIN_MODULAR.md, secao 4)"""
    return NotImplementedError(f"{modulo}.{metodo}: sem equacao na etapa 0 do prototipo (docs/ESPEC_DIGIBRAIN_MODULAR.md, secao 4)")
