# TAREFA V2 — CEREBRO_A_BASELINE: os critérios para manter o cérebro A como baseline e para recorrer a ele como fallback (2026-10-24)

Coordenador: Gerente (Claude Code). Worker: a definir (método). Status: **ABERTA, só papel.** Os critérios são PROPOSTOS. Eles precisam ser
decididos pelo Matheus **antes** da avaliação do protótipo modular. As decisões AF-1 a AF-6 estão na seção 8.

Categoria: arquitetura. Origem: Matheus, 2026-10-24, o PROMPT MESTRE (seção 1, "Papel do cérebro A").
- O A não está descartado, mas não é o cérebro final da web.
- Ele fica como **baseline** histórico e experimental, como **controle** quando responder a uma pergunta útil, e como **fallback
  condicionado.**
- A passagem ao fallback não se decide por impressão nem pelo fracasso de uma primeira implementação.

## 0. Os cinco pontos

| ponto | resposta |
|---|---|
| a capacidade | uma regra decidida antes, que diz quando o A serve de baseline e quando o produto volta para ele |
| o marco que desbloqueia | a avaliação do protótipo modular sem viés, e o fim das rodadas que só validam o A |
| a evidência | os critérios escritos e decididos; depois, o relatório de avaliação do protótipo contra eles |
| as dependências reais | nenhuma para escrever; a avaliação depende do protótipo |
| se o gate falhar | se o protótipo falhar nos critérios de implementação, ele se conserta; só a limitação da arquitetura, demonstrada como abaixo, vai ao Matheus como pedido de fallback |

## 1. O A como baseline e controle

- **Os resultados do A continuam valendo** como evidência sobre o A. Nada se apaga.
- **Uma rodada nova do A só entra** com uma função explícita, de uma destas:
  - **baseline:** comparar um módulo novo com a peça do A que faz a mesma coisa, nos mesmos cenários;
  - **controle:** um braço de um plano em que o A responde a uma pergunta do modular;
  - **compatibilidade:** os pets v11 do jogo continuam funcionando;
  - **avaliação do fallback:** esta tarefa.
- **Não entram** rodadas cujo único propósito seja validar o A como destino do produto. A seção 9 de `docs/AUDITORIA_V2_PRODUTO_MODULAR.md`
  lista o que pausa.

## 2. O que é um protótipo "representativo"

O fallback só se discute depois de um protótipo que cumpra **todos** estes pontos:
1. **ele implementa a especificação** (`docs/ESPEC_DIGIBRAIN_MODULAR.md`) nos módulos da DM-3, cada um com os testes de mecanismo
   passando;
2. **ele roda os cenários do MVP** com o replay bit a bit e o motivo por módulo;
3. **ele teve rodadas de diagnóstico e conserto** depois da primeira avaliação (AF-3);
4. **o custo foi medido** no navegador.

## 3. Falha de implementação × limitação da arquitetura

| pergunta de diagnóstico | se a resposta for "não" | leitura |
|---|---|---|
| **D1:** os testes de mecanismo de cada módulo passam? | conserta o módulo | **falha de implementação** |
| **D2:** desligar cada módulo muda o comportamento no sentido que a especificação prevê (a ablação)? | a ligação está errada ou o módulo não pesa; diagnosticar a fiação antes de culpar a arquitetura | **falha de implementação**, até prova em contrário |
| **D3:** com os parâmetros postos à mão (um oráculo), a arquitetura **consegue** expressar o comportamento-alvo do MVP? | se nem o oráculo consegue, a arquitetura não tem como | **limitação da arquitetura** |
| **D4:** com o oráculo conseguindo, a aprendizagem chega lá? | a regra de aprendizagem ou os seus parâmetros falham | **falha de implementação** ou de calibração (se conserta), não da arquitetura |
| **D5:** o custo cabe no orçamento do navegador? | otimizar; se nenhuma otimização couber, é limitação | **limitação**, só depois da otimização |
| **D6:** na comparação com o A nos mesmos cenários, com o plano antes, o modular fica equivalente ou melhor nas medidas do MVP? | registrar; isso **sozinho não é limitação**: o modular pode perder para o A e ainda ser o alvo, por estado, memória e modulação, que o A não tem | informação para o Matheus |

**O fallback para o A só pode ser pedido** quando D1, D2 e D4 estiverem resolvidos e D3 ou D5 mostrarem limitação, com o relatório. **A
decisão é do Matheus.**

## 4. Os números

**Nenhum número desta tarefa está decidido.** São todos PROPOSTOS e SEM FONTE:
- a margem de equivalência da D6;
- o orçamento de CPU por decisão no navegador e o tamanho do log por dia (D5);
- o número mínimo de rodadas de diagnóstico (AF-3);
- a fração mínima de vidas em que a cadeia do MVP acontece (o G-MVP do protótipo).

O plano da avaliação os fixa antes da run, com a decisão do Matheus.

## 5. Entrega

- Esta tarefa decidida (AF-1 a AF-6).
- Depois, o relatório de avaliação do protótipo contra os critérios, em `docs/RESULTADO_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md`.

## 6. Fora desta tarefa

- rodar qualquer coisa;
- mudar o A;
- a escolha de módulos (é da especificação).

## 7. Critérios de aceitação

- Os critérios estão decididos antes da avaliação.
- Cada rodada nova do A cita a função dela (baseline, controle, compatibilidade ou fallback).

## 8. Precisa do Matheus

Todas PROPOSTAS, com a recomendação primeiro.

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| **AF-1** | os critérios D1 a D6 | **como estão:** o fallback só por D3 ou D5, depois de D1, D2 e D4 resolvidos | o fallback pelo D6 sozinho: o produto volta ao A porque a primeira versão do modular perdeu, que é o que o pedido proíbe |
| **AF-2** | o que é "representativo" | **os quatro pontos da seção 2** | um protótipo menor: uma limitação de implementação parece da arquitetura |
| **AF-3** | quantas rodadas de diagnóstico e conserto antes de discutir o fallback | **duas** (PROPOSTO, SEM FONTE) | uma: a primeira implementação decide; muitas: o produto espera |
| **AF-4** | o orçamento do navegador (D5) | **fixado na especificação, medido no protótipo,** a partir do custo do A v11 no mesmo aparelho | sem orçamento: o D5 vira impressão |
| **AF-5** | as rodadas do A em curso | **as da seção 9 da auditoria** (pausar o piloto e a validação da P4; o Gate I só com o A como baseline) | continuar: a pesquisa segue validando o A |
| **AF-6** | o A no jogo enquanto o modular não entra | **os pets v11 continuam com o A,** sem mudança | trocar antes: o jogo fica sem cérebro que funcione |
