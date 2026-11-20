"""Fala livre por LLM local (experimento `exp-fala-livre`, docs/PLANO_VERSAO_FALA_LIVRE.md).

Pacote FORA de `digilab/`: nada do pet (motor, politica, vinculo, combate, treino) importa daqui (teste por
AST). A fala e so apresentacao: le o estado do pet, nunca escreve nele. So Ollama local; nenhuma API paga.
"""

VERSAO_APP = "fala-livre"      # "exp-fala-livre" durante o experimento (os artefatos de artifacts_fala_livre/ guardam esse rotulo)
