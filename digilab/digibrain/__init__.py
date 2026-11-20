"""O DigiBrain modular (docs/ESPEC_DIGIBRAIN_MODULAR.md; docs/TAREFA_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md): um arquivo por modulo da DM-3,
atras da `ConfigDigibrain` (digilab/config.py), desligada por padrao. O A (digilab/policies/lobos.py) e o engine.py nao mudam: o pacote
reaproveita do A, por importacao, so as contas inteiras (`div_arred`) e a interface do corpo (`sinal_corpo`, `valor_previsto`,
`falta_receptor`, `leitura_receptor`).

Etapa 1a: os modulos com as equacoes da espec (M-SENS, M-AFETO, M-ESTADO, M-IMPULSO, M-MEM, M-ARB, M-PLAST e o M-ADAPT, que cumpre o
`Protocol` `Politica`), os ganchos vazios (M-PERS, M-GEN, M-EXPR) e os valores de partida em `ConfigDigibrainInatos` (PROPOSTOS, SEM
FONTE). Nada no motor, na bancada de hoje nem no jogo usa o pacote: so o orquestrador do prototipo
(experiments/run_v2_digibrain_prototipo.py) o monta, com a chave ligada.

A aritmetica do pacote e so inteira (a DM-2; o G-INT confere pela AST: sem float, sem `/` e sem `math`), nenhum arquivo importa o
digilab/corpo.py (a G-RECEPTOR) e a direcao do cheiro fica no motor (o G-SEM-DIRECAO: o pacote so le se ha cheiro).

O import e preguicoso (LIMPEZA, LZ2): o `DigiBrain` e os outros nomes de `__all__` vem do `adapt.py` so quando alguem os pede, entao
importar o `base.py` (as contas inteiras e a interface do corpo, que o lobos.py tambem usa) nao puxa o pacote inteiro."""
import importlib

__all__ = ["DigiBrain", "DigibrainDesligado", "Intencao", "Modulos"]


def __getattr__(nome: str):
    if nome in __all__:
        return getattr(importlib.import_module(".adapt", __name__), nome)
    raise AttributeError(f"o modulo {__name__!r} nao tem o atributo {nome!r}")
