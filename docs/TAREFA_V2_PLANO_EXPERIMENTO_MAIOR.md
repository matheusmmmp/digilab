# TAREFA V2 — PLANO-EXPERIMENTO-MAIOR (2026-10-01)

Coordenador: chat "Principais jogos Digimon com diálogo". Worker: chat C. Worktree e branch: `v2-plano-experimento-maior`. Status:
ABERTA. **Só papel: nenhuma run, nenhum código.**

## 1. Pergunta

Escrever, antes de existir qualquer dado, o plano de análise do **experimento maior** (`docs/ROADMAP_V2.md`, R6.1): braços P0, P1, P2, P2e,
P3 × condições casado, descasado e mutável, no mesmo aprendiz (`docs/PLANO_V2_PESQUISA.md`, seção 2; `docs/ARQUITETURA_V2_VALIDACAO.md`,
seção 6).

## 2. Depende de

Nada para escrever. A run só acontece depois de N3, N4 e N5.

## 3. Entrega

1. **`docs/PLANO_ANALISE_V2_EXPERIMENTO_MAIOR.md`**:
   - as **predições registradas antes**: P0 vence no casado; P1 vence P0 no descasado e no mutável se a vida for longa; P2 chega lá com
     menos consequências que P1; P2e piora e se recupera quando o mundo refuta; P3 fica perto de P0. Para cada uma, a medida, o teste e o
     que conta como confirmar ou refutar;
   - medidas da bancada (`desempenho_no_ambiente`, `custo_da_plasticidade`, acerto na tarefa, G4 do aprendido, G6) e o "só cuidado" acoplado;
   - como cada condição é construída (o casado é o mundo padrão; o descasado e o mutável dependem das frutas: deixe como contrato que o N4 e a
     bancada de mundos cumprem);
   - tamanho da amostra e por quê, usando o que a análise de poder da v1 ensinou (`docs/PLANO_ANALISE.md`, `artifacts_poder/`), sem
     inventar número;
   - sementes **14101…14505** (calibração) e **15101…15505** (validação, uma vez).
2. **`docs/digibrain/integration/11_PROMPT_CLAUDE_SCIENCE_PLASTICIDADE.md`** (fora do repositório, em `D:\Trab\digilab\docs\`): o prompt
   da busca verificada sobre **decomposição da plasticidade por fonte** (consequência × ensino contextual × feedback explícito) no mesmo
   agente, no formato dos prompts 09 e 10, para o projeto poder dizer "não localizamos" ou citar quem já fez (D5).

## 4. Regras

Referências só VERIFICADAS (`docs/referencias/`); nenhuma alegação de novidade (`literatura-digilab`); números só com artefato. No fim do
plano, as decisões que só o Matheus pode tomar, com recomendação e custo de errar.

## 5. Fora desta tarefa

Rodar qualquer coisa; mexer em código; o N5 (dono informante).
