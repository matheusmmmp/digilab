# TAREFA V2 — DIGIBRAIN_MODULAR_PRODUTO: a integração progressiva do DigiBrain modular no jogo (2026-10-24)

Coordenador: Gerente (Claude Code). Worker: a definir (o A, dono da web, com o dono do protótipo). Worktree e branch:
`v2-modular-produto-<etapa>`. Status: **ABERTA, só papel.** Começa depois do MVP e de um protótipo avaliado.

Categoria: implementacao. Origem: Matheus, 2026-10-24, o PROMPT MESTRE (seções 1, 7 e 9): o cérebro modular é o alvo do produto, e o A não
é o cérebro final da web.

## 0. Os cinco pontos

| ponto | resposta |
|---|---|
| a capacidade | o pet do jogo decide com o DigiBrain modular, módulo a módulo, com o mesmo replay e o mesmo painel |
| o marco que desbloqueia | o primeiro produto jogável com o cérebro modular |
| a evidência | o G-PAR de cada módulo contra o gabarito da referência; o replay; o e2e dos cenários do MVP com o cérebro novo; a medida de custo no navegador |
| as dependências reais | o MVP (o mundo no jogo); o protótipo avaliado; as DM-2 e DM-5 (a referência e a versão) |
| se o gate falhar | o módulo que falha não entra; o jogo continua com o cérebro anterior (o A v11, ou o último módulo que passou). O fallback para o A só pelos critérios da `docs/TAREFA_V2_CEREBRO_A_BASELINE.md` |

## 1. Pergunta

Como o cérebro modular substitui o A no jogo sem quebrar os saves, o replay, o painel e a experiência básica?

## 2. Depende de

- `docs/TAREFA_V2_MVP_MUNDO_PRODUTO.md` entregue;
- `docs/TAREFA_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md` avaliado;
- as DM-2 e DM-5.

## 3. Mudança mínima (PROPOSTA)

1. **Um módulo de cada vez,** na ordem que o protótipo justificar: cada um com o espelho TS em ponto fixo, os gabaritos e o G-PAR.
2. **Uma versão de pet nova** para o primeiro cérebro modular no jogo (DM-5). As anteriores ficam intactas.
3. **O adaptador do MVP** (a Observação e a Intenção) como a única fronteira entre o cérebro e o motor do jogo.
4. **O painel DigiBrain:**
   - hoje ele só conhece a estrutura do A (PW-7, `docs/TAREFA_V2_W_PORTE_CEREBRO_A.md`);
   - ele passa a mostrar as contribuições por módulo, a partir do motivo.
5. **A fala:** só com a fidelidade da `docs/TAREFA_V2_MEMORIA_AUTOBIOGRAFICA.md` (etapa M6).

## 4. Experimento e gate

Não há run. Os gates são de engenharia: o G2, o G1, o G-PAR por módulo, o e2e do MVP com o cérebro novo e o custo no navegador (o
orçamento da especificação).

## 5. Entrega

- Um PR por módulo, com os testes do `web/app` e a contagem.
- As capturas.
- O registro.

## 6. Fora desta tarefa

- os módulos que o protótipo ainda não avaliou;
- dois pets e qualquer coisa online;
- a genética.

## 7. Critérios de aceitação

- Um pet novo nasce com o cérebro modular, come a comida posta no cenário e aprende com isso.
- Os saves antigos abrem iguais.
- O replay é bit a bit.
- O painel mostra o motivo por módulo.

## 8. Precisa do Matheus

- a ordem dos módulos no jogo;
- quando o ovo novo passa a nascer com o cérebro modular;
- o que fazer com os pets v11 existentes (continuam com o A).
