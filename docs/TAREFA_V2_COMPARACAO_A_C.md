# TAREFA V2 — COMPARACAO-A-C: piloto, adendo de tamanho e validação da comparação dos cérebros (2026-10-06)

> **V2, congelado em 2026-10-30** (tag `v2-final`). O estado em que este documento fica na V3 está em `docs/FECHAMENTO_V2.md`; o
> plano da V3, em `docs/PLANO_V3.md`.

Coordenador: chat "Principais jogos Digimon com diálogo". Worker: chat D. Worktree e branch: `v2-comparacao-a-c`. Status: ABERTA.
Etapa K3/V2 do `docs/ROADMAP_V2.md`. Plano: `docs/PLANO_ANALISE_V2_COMPARACAO_CEREBROS.md`, decisões C-1 a C-10 e adendo 1.

## 1. Quem compara

- **A:** os lobos, no ponto da K2 (`artifacts_v2_calibracao_conjunta/escolha.json`).
- **C:** o cérebro Fly-like, no ponto da calibração dele (`artifacts_v2_comparacao_cerebros/calibracao_C/escolha.json`; passo 128, teto
  4096, `w0_info` 256).
- **B:** **sai**, por "não aprende", pela seção 7 do plano e pela decisão de 2026-10-06 no `REGISTRO_DESVIOS`. "A comparação segue com os
  outros."

**O que muda na família com a saída do B** (registre isso no adendo 2 do plano antes de rodar, como interpretação):
- a família primária fica com **CC-1 e CC-2** (C − A no P1: a `taxa_fruta_ruim` final no descasado e depois da troca no mutável), num
  **Holm de dois**, bilateral, α = 0,05;
- CB-1 e CB-2 ficam registrados como "não testáveis: o B não fecha";
- o N do adendo de tamanho usa o α do passo mais exigente desse Holm, α/2;
- o empate é o IC 90% dentro de ±Δ, com o Δ do adendo 2 do experimento maior;
- os secundários são os da seção 4, sem os que envolvem o B.

## 2. Passos (seção 8 do plano)

1. **Piloto (seção 6.3):** A e C, cada um no seu ponto, nas unidades de 28101…28505 (K = 4, prefixo `comparacao-cerebros`). O A entra só
   como referência. Reaproveite as vidas do C que já existem no ponto escolhido, se a config for a mesma.
2. **Adendo 2 do plano da comparação**, commitado **antes** da validação:
   - os pontos e as regras que os escolheram;
   - o Δ, o σ²_d de CC-1 e CC-2, o N (fórmula e conferência por simulação, arredondado para cima ao múltiplo de 5) e as unidades;
   - o tempo estimado, sem os braços do B.
   **Se passar de 12 h, pare e pergunte pelo PR.**
3. **Validação:** uma vez, nas bases 29101…29505, com toda vida rejogada do disco.
   - **Braços:** A e C em P1, P2, P2e e P3 nas três condições, mais os acoplados `sem_ensino`, o P0 comum e o acoplado da mesma
     experiência (o C no registro do P1 do A).
   - **Não toque** nas sementes do experimento maior (30101…30505 e a queimada 15101…15505).
4. **Resultado** em `docs/RESULTADO_V2_COMPARACAO_CEREBROS.md`:
   - os contrastes, com a leitura (C melhor, A melhor ou empate);
   - os secundários e os descritivos: legibilidade, deriva, custo e divergência acoplada;
   - a **tabela do critério M6** da seção 5, preenchida até onde os dados permitem: desempenho, legibilidade, determinismo inteiro e
     porte, custo;
   - a escolha é do Matheus; o relatório só preenche a tabela e recomenda.

## 3. Regras

- O B não roda.
- Nada se ajusta olhando a validação.
- Refazer só por erro de execução, com sementes novas registradas antes.
- Nenhuma alegação de novidade.
- `lobos.py` e `cerebro_c.py` não mudam.

## 4. Entrega

Um PR (piloto, adendo, validação e resultado) com o relato no corpo e a suíte inteira, mais uma seção no fim do `CLAUDE.md` e outra no fim
do `REGISTRO_DESVIOS.md`. Merge só pelo Matheus.
