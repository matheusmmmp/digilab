# Memória episódica e autobiográfica

Quatro marcos diferentes, que não se provam uns pelos outros:
1. **registrado** (o evento está no log);
2. **codificado** (virou episódio segmentado);
3. **recuperado** (volta quando é relevante);
4. **causal** (muda a decisão com o estado atual igual).

## Nas fontes

- **VERIFICADA:** Castro e Gudwin 2013 (`10.4018/jse.2013010102`): a cena recuperada informa a escolha na navegação (marco 4,
  numa criatura simulada).
- **CORPUS:** Sakabe et al. 2025: detecção, codificação e consulta de episódios no CST (marcos 2 e 3).
- **VERIFICADA:** Adams 2021 (Dwarf Fortress): história acumulada legível ao jogador. É a camada de **memória
  autobiográfica de alto nível**: o que o jogador vê, não como o agente decide.

## No DigiLab hoje (REPOSITÓRIO)

| marco | existe? | onde |
|---|---|---|
| 1. registrado | sim, tudo (event sourcing) | o log da vida |
| 2. codificado | sim, como fatos H/O/P/L | `digilab/historia.py` (voz própria) |
| 3. recuperado | sim, para a fala | a voz cita fatos da história |
| 4. causal | **não** pela história; a memória por espaços decide, com efeito pequeno (6,9% dos motivos, sem efeito no bootstrap) | `memoria_espacos.py`; `artifacts_v1_memoria/bootstrap_sementes.json` |

## Hipóteses

| ID | pergunta | teste mínimo |
|---|---|---|
| H-MEM-001 | recuperar um episódio relevante muda a escolha com o estado atual igual, além de uma janela de recência | recuperação relevante × nenhuma × recência × embaralhada; diferença de escolha, sucesso, custo |
| H-MEM-02 | a memória autobiográfica (o que o jogador vê) e a memória causal (o que decide) podem ser a mesma estrutura sem mentir | toda frase sobre o passado aponta para um episódio que de fato mudou uma decisão |

H-MEM-02 liga a pesquisa à legibilidade (G4): hoje a voz conta a história, mas a história não decide.
