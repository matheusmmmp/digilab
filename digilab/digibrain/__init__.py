"""O DigiBrain modular (docs/ESPEC_DIGIBRAIN_MODULAR.md; docs/TAREFA_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md): um arquivo por modulo da DM-3,
atras da `ConfigDigibrain` (digilab/config.py), desligada por padrao. O A (digilab/policies/lobos.py) e o engine.py nao mudam.

Etapa 0: so o esqueleto. O M-ADAPT (adapt.py) cumpre o `Protocol` `Politica` e encaminha aos modulos; os modulos (sens, afeto, estado,
impulso, mem, arb, plast e os ganchos vazios) levantam NotImplementedError. Nada no motor, na bancada nem no jogo usa o pacote ainda.

A aritmetica do pacote e so inteira (a DM-2; o G-INT confere pela AST: sem float, sem `/` e sem `math`), e nenhum arquivo importa o
digilab/corpo.py (a G-RECEPTOR)."""
from .adapt import DigiBrain, DigibrainDesligado, Intencao, Modulos

__all__ = ["DigiBrain", "DigibrainDesligado", "Intencao", "Modulos"]
