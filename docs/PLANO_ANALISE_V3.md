# Plano de análise V3 — educação, lesões e evolução por vitórias (exploratório)

Status: **registrado antes da run**. O Matheus delegou as escolhas em 2026-09-28 ("faça o que você recomenda e siga para a Fase 3"). Valores que não vêm de uma decisão dele nem de regra já existente estão marcados PROPOSTO.

**Natureza.** A análise é **exploratória**. A confirmatória (`PLANO_ANALISE.md`, commit 89738ab) refutou a hipótese central na condição neutra e continua sendo o resultado confirmatório. Aqui a pergunta é outra: *com os caminhos novos do cuidado até a luta, o cuidado passa a pesar?* Os resultados daqui não reinterpretam a confirmatória. Eles orientam a próxima pergunta confirmatória, se houver uma.

## 1. Decisões fechadas antes da run

| Item | Valor | Status |
|---|---|---|
| disciplina por aviso de banheiro atendido | 0 | DECIDIDO (delegado) |
| efeito da qualificação por vitórias | **condição para chegar a adulto**: sem pelo menos 10 lutas com taxa de 0,8 ou mais no estágio adolescente, o pet continua adolescente e luta no painel como adolescente (sem forma adulta) | DECIDIDO (delegado) |

## 2. O que a vida de pesquisa ganha

A vida é a de `simular_vida_educacao`: 14 dias, duração `teste`, orçamento igual entre os braços. A educação e as lesões ficam ligadas.

1. **Sparring de verdade** (hoje é dado como "cumprido"):
   - na adolescência, 10 lutas em horários fixos, iguais para todos os braços: a cada 30 min a partir de 30 min depois do início do estágio;
   - o rival é o **adolescente da mesma linha e espécie, com caráter neutro e sem treino** (um colega da mesma idade);
   - o pet luta com o que é naquele momento: a linha, o caráter medido no início do adolescente, o treino acumulado, a condição pela saúde e a disciplina;
   - regras da campanha (V21C), stats absolutos e condição real (a luta acontece na vida, não na arena).
   - PROPOSTO, sem fonte.
2. **Disciplina na luta**:
   - ε do pet = ε dos bots (0,05) + (1 − disciplina/100) × 0,10, ou seja, um pet sem educação ignora os próprios gambits com mais frequência;
   - vale na vida e no painel, com a disciplina do fim da vida;
   - não toca a resolução do combate: só o ε do `Lutador`, como já acontece com a forma sombria.
   - PROPOSTO, sem fonte.
3. **Os donos tratam lesão**, tudo PROPOSTO, sem fonte:
   - `tratar_lesao` passa na frente da resposta à janela;
   - o atencioso, o exigente, o incoerente, o permissivo e o lutador tratam sempre que presentes; o relapso trata só na visita;
   - o **aleatório** passa a sortear entre todos os botões de cuidado (os 6 da v1 e os 3 novos), por ser o controle "aperta qualquer botão".
4. **Morte**: um pet morto não luta no painel. Conta **0** em todas as partidas, e as mortes são relatadas à parte.
5. **Braço novo: "lutador"** (estilo de jogo "lutar"): cuida como o atencioso e faz **20** sparrings no lugar de 10, com os mesmos horários mais 10 depois. Serve para o gate de equilíbrio.

## 3. Desenho

- **Braços** (7): atencioso, aleatório, relapso, incoerente, exigente, permissivo e lutador.
- **Ovos**: 80, sementes 70001–70080 (novas, longe das já usadas). Fumaça com 69001–69002.
- **Painel**: desenho B, igual ao da confirmatória:
  - 8 formas adultas × 4 espécies da bateria V21C;
  - 50 partidas por bot, sementes que dependem só do ovo, do bot e de k;
  - condição **neutra** como principal e real como descritiva;
  - o pet que não se qualificou entra como adolescente.
- **Estatística**: igual à confirmatória. Bootstrap percentil sobre os ovos (10 000 reamostragens, semente 20260928) e a leitura pela seção 5 do plano original (Δ = 0,10). Sem Holm: é exploratório, e todas as comparações são relatadas.

## 4. Perguntas (todas exploratórias)

- **E1**: atencioso − aleatório no painel B, condição neutra, com educação e lesões. A pergunta da confirmatória, agora com os caminhos novos.
- **E2**: atencioso − permissivo. A educação (bronca) pesa além da presença?
- **E3**: relapso − aleatório e incoerente − aleatório (descritivos).
- **Mecanismo** (descritivo, por braço):
  - fração de pets qualificados para adulto;
  - taxa de vitória no sparring;
  - disciplina final;
  - lesões e mortes;
  - forma alcançada.

## 5. Gate de equilíbrio dos estilos de jogo (ConfigEquilibrio, PROPOSTO)

- **Estilos**: cuidar = atencioso, treinar = exigente, lutar = lutador.
- **Critério 1**: a taxa média de cada estilo contra o painel B, na condição neutra, fica entre 0,40 e 0,60.
- **Critério 2**: nenhum estilo vence os outros dois por mais de 0,15, comparando as médias contra o painel.
- **Critério 3**: nenhum dos 7 braços domina todos os outros, ou seja, nenhum tem IC95 da diferença inteiro acima de 0 contra cada um dos demais.
- **Se o gate reprovar**: isso vira **achado**, não é corrigido na mesma run. A calibração entra num registro de desvio e numa run nova.

## 6. Saída

- **Onde**: `artifacts_educacao/` (resultado.json, pets.json, meta.json). As partidas e as vidas ficam fora do git, como na confirmatória.
- **Script**: `experiments/run_educacao.py`.
- **Protocolo**: a run grava o `hash_parametros_educacao()` e o sha256 das fontes.

## 7. Adendo V3b (registrado antes da run V3b, depois de ver a V3)

O Matheus pediu os dois ajustes que recomendei ao ler a V3 (2026-09-28). A V3 fica como está (commit 371c402). O adendo corrige dois defeitos de desenho que a V3 mostrou; não é repescagem de resultado.

1. **O estilo lutar não tinha efeito.** As lutas não mudavam nem a política nem o estado, e o lutador saiu idêntico ao atencioso (−0,0004).
   - Correção: `ConfigLesoes.luta_treina`, em que cada luta fora da arena de pesquisa conta como uma sessão de treino.
   - A sessão usa exercício em rodízio, a fadiga, os tetos e o intervalo mínimo do treino; o pet não recusa a luta.
   - Vale para todos os braços. O lutador faz 20 lutas e os outros 10.
   - PROPOSTO, sem fonte.
2. **O estilo treinar (exigente) destruía a saúde pelo orçamento** (saúde final 0,02). As sessões no teto tiram verba do cuidado, e as janelas da educação apertam mais.
   - Correção: o braço novo **treinador**, com as mesmas sessões do exigente, mas o slot de treino vira cuidado quando alguma necessidade está abaixo do limiar do atencioso.
   - O exigente continua como está, porque é braço da confirmatória. O gate passa a usar treinar = treinador.
   - PROPOSTO, sem fonte.
3. **Desenho**: os mesmos 80 ovos e o mesmo rótulo de partidas da V3, pareados; 8 braços (os 7 e o treinador). Saída em `artifacts_educacao_v3b/`, config em `experiments/configs/educacao_v3b.json`.
4. **O que olhar**:
   - as mesmas comparações, mais treinador − atencioso e treinador − exigente;
   - o gate com os estilos novos;
   - quanto a luta treinou (`lutas_que_treinaram`).
   - A leitura continua exploratória.
