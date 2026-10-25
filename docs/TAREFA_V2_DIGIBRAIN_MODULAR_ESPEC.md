# TAREFA V2 — DIGIBRAIN_MODULAR_ESPEC: a especificação técnica do DigiBrain modular (2026-10-24)

Coordenador: Gerente (Claude Code). Worker: o C (arquitetura e método; Opus). Worktree e branch: `v2-modular-espec`. Status:
**DESPACHADA em 2026-10-25,** com as DM-1 a DM-9 DECIDIDAS (seção 8). Nenhum código. **O gate é a revisão do Matheus** (seção 4).

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
- as decisões DM-1 a DM-9 de `docs/ARQUITETURA_DIGIBRAIN_MODULAR.md` (seção 13), todas DECIDIDAS, com as condições do Matheus repetidas
  na seção 8 deste documento.

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
8. **o orçamento** (PROPOSTO e SEM FONTE): o CPU por decisão no navegador e o tamanho do log, a medir no protótipo;
9. **o substrato neural, numa seção própria** (a condição da DM-1): os neurônios ou unidades, as conexões, a ativação, a plasticidade
   e **como o aprendizado altera o comportamento ao longo da vida.** Integradores, impulsos e regras de arbitragem, por si só, não
   bastam para caracterizar o protótipo como cérebro neural. Onde a literatura (a skill `literatura-digilab`; só referência
   verificada) e a especificação ainda não sustentarem uma escolha, o ponto fica marcado como **decisão a pesquisar antes de
   implementar**, numa lista própria no fim do documento;
10. **a memória autobiográfica consolidada como etapa própria** (a condição da DM-3): aqui só a interface do M-MEM mínimo (episódios
    de alimentação) e o gancho pelo qual a memória consolidada terá influência causal nas decisões e nas facetas adquiridas
    (`docs/TAREFA_V2_MEMORIA_AUTOBIOGRAFICA.md`);
11. **a comparação com a visão do produto e da pesquisa**, numa seção curta: o que cada módulo entrega ao MVP (`docs/PRODUTO_VISAO.md`)
    e à pergunta da pesquisa (`docs/PLANO_V2_PESQUISA.md`), para a revisão do Matheus.

## 4. Experimento e gate

Não há run. **O gate é a revisão:** o Matheus aprova a especificação, ou a devolve com os pontos abertos. A revisão compara a
especificação com a visão do produto e da pesquisa. **Nenhuma implementação nem experimento é aprovado antes dela, e o protótipo não
começa até ela acontecer** (Matheus, 2026-10-25).

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
- Toda conta usa a aritmética da DM-2, e a paridade Python/TS **não é apresentada como evidência de aprendizagem** nem de qualidade
  comportamental (a condição da DM-2).
- O substrato neural tem a seção própria do item 9, e cada escolha ainda sem fonte está na lista das decisões a pesquisar.
- As peças do A têm, uma a uma, a escolha justificada com evidência; o documento mostra em que o modular **não é o A reorganizado**
  (a condição da DM-7).
- A versão de pet do modular é a **v13** (DM-5); a v12 fica com o MVP e o A.
- Todo número novo está marcado PROPOSTO e SEM FONTE.

## 8. Decisões do Matheus (2026-10-25)

As DM-1 a DM-9 estão DECIDIDAS pelas recomendações de `docs/ARQUITETURA_DIGIBRAIN_MODULAR.md` (seção 13), com estas condições dele
(texto resumido sem mudar o sentido; a tabela da arquitetura tem a redação completa):

- **DM-1:** integradores com vazamento em ponto fixo para o estado dinâmico inicial, **mas o substrato neural é especificado
  separadamente** (unidades, conexões, ativação, plasticidade, como o aprendizado altera o comportamento ao longo da vida). O que a
  literatura e a especificação não sustentarem fica explícito como decisão a pesquisar antes de implementar.
- **DM-2:** referência Python e espelho TS em ponto fixo com G-PAR; **a paridade não é evidência de aprendizagem** nem de qualidade.
- **DM-3:** os módulos do laço do MVP e a memória episódica mínima de alimentação; a memória autobiográfica consolidada é **etapa
  própria**, com influência causal futura nas decisões e nas facetas adquiridas.
- **DM-4:** as rotas versionadas aceitas como propostas.
- **DM-5:** **v13** para o primeiro pet com o cérebro modular; a v12 permanece como o MVP com o A.
- **DM-6:** o aprendido afeta as facetas adquiridas, nunca o temperamento inato.
- **DM-7:** o reaproveitamento do A decidido na especificação, módulo a módulo, com evidência; **o modular não é só o A reorganizado.**
- **DM-9:** o NORNBRAIN só para estudo; as licenças do CfC e do NCP conferidas antes de qualquer reúso.

**O que ainda vai a ele:** as decisões que a especificação abrir (a lista do item 9 da seção 3), levadas com recomendação e custo de errar.

## 9. Entrega (2026-10-25)

`docs/ESPEC_DIGIBRAIN_MODULAR.md`, pelo C (Claude Code, Opus 5.5), no branch `v2-modular-espec`. Os 11 itens da seção 3:
- os contratos, na seção 4;
- as formas do estado, na seção 3;
- o corpo, na seção 6;
- o motivo, na seção 7;
- as peças do A, na seção 8;
- os testes, na seção 10;
- a versão, na seção 11;
- o orçamento, na seção 12;
- o substrato neural, na seção 2;
- a memória, na seção 9;
- a comparação com a visão, na seção 13.

**As 16 decisões a pesquisar** estão na seção 15, nove delas antes do protótipo. **O gate continua sendo a revisão do Matheus.**
