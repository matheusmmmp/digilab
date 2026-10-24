# TAREFA V2 — DIGIBRAIN_MODULAR_ESPEC: a especificação técnica do DigiBrain modular (2026-10-24)

Coordenador: Gerente (Claude Code). Worker: a definir (trabalho de arquitetura e método). Worktree e branch: `v2-modular-espec`. Status:
**ABERTA, só papel.** Nenhum código.

Categoria: arquitetura. Origem: Matheus, 2026-10-24, o PROMPT MESTRE (seções 1 e 6). A direção modular está DECIDIDA, e esta tarefa
especifica os detalhes técnicos.

## 0. Os cinco pontos

| ponto | resposta |
|---|---|
| a capacidade | o contrato de cada módulo do DigiBrain, com a forma do estado e as regras de atualização, antes de qualquer código |
| o marco que desbloqueia | o protótipo (`docs/TAREFA_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md`) e a memória (`docs/TAREFA_V2_MEMORIA_AUTOBIOGRAFICA.md`) |
| a evidência | um documento de especificação revisável, com os testes de mecanismo planejados por módulo e as decisões levadas ao Matheus |
| as dependências reais | `docs/ARQUITETURA_DIGIBRAIN_MODULAR.md` e as decisões DM-1 a DM-9 dele |
| se o gate falhar | a especificação volta ao Matheus com o ponto que não fechou; o protótipo não começa sem ela |

## 1. Pergunta

Qual é, módulo a módulo, o contrato do DigiBrain modular? O que entra, o que guarda, o que sai, como atualiza, com que rng e em que
aritmética, para que o protótipo seja testável e o replay continue bit a bit?

## 2. Depende de

- `docs/ARQUITETURA_DIGIBRAIN_MODULAR.md`;
- as decisões DM-1 (a forma do estado), DM-2 (a referência e a paridade), DM-3 (o primeiro protótipo) e DM-7 (as peças do A).

## 3. Mudança mínima

Um documento novo, `docs/ESPEC_DIGIBRAIN_MODULAR.md`, com:
1. **o contrato de cada módulo** da seção 2 da arquitetura: as entradas, o estado, as saídas, a regra de atualização, a rng (derivada
   por `derivar_semente`), a aritmética (inteira ou ponto fixo, DM-2) e o que vai ao registro da decisão;
2. **as formas candidatas do estado dinâmico** (DM-1): o integrador com vazamento em ponto fixo, e uma forma recorrente. Para cada uma:
   as equações, o custo por decisão e o que se testaria;
3. **a ligação do corpo:**
   - quais receptores entram em cada módulo;
   - quais ganhos o M-AFETO dá ao M-PLAST e ao M-ARB;
   - a G-RECEPTOR mantida;
4. **o motivo por módulo:** as contribuições de cada um na decisão, para a sonda "quem decidiu" e para a fidelidade da fala;
5. **as peças do A, uma a uma** (DM-7): o instinto, a L1, o traço, o planejador, a disputa e o N6. Para cada uma: reaproveitar,
   adaptar ou deixar, com a evidência;
6. **os testes de mecanismo planejados**, com resposta conhecida, por módulo;
7. **a versão e o protocolo:** a versão de pet (DM-5), as ações no fim do enum, e nenhuma mudança no `engine.py`;
8. **o orçamento** (PROPOSTO e SEM FONTE): o CPU por decisão no navegador e o tamanho do log, a medir no protótipo.

## 4. Experimento e gate

Não há run. **O gate é a revisão:** o Matheus aprova a especificação, ou a devolve com os pontos abertos.

## 5. Entrega

- Um PR `arquitetura` com o `ESPEC_DIGIBRAIN_MODULAR.md` e as decisões listadas.
- O registro do mês.

## 6. Fora desta tarefa

- qualquer código;
- a topologia final;
- o genoma (só os ganchos dos parâmetros inatos);
- a memória detalhada, que tem tarefa própria (só a interface do M-MEM entra aqui).

## 7. Critérios de aceitação

- Cada módulo do protótipo tem um contrato completo e pelo menos um teste de mecanismo planejado.
- Toda conta usa a aritmética da DM-2.
- Todo número novo está marcado PROPOSTO e SEM FONTE.

## 8. Precisa do Matheus

As DM-1 a DM-9 de `docs/ARQUITETURA_DIGIBRAIN_MODULAR.md` (seção 13), mais as que a especificação abrir.
