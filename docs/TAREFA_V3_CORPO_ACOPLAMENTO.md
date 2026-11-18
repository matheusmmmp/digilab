# TAREFA V3 — CORPO_ACOPLAMENTO (2026-11-18)

Coordenador: a sessão do Matheus que abriu esta (Claude Code). Worker: Claude Code, Opus 5.5, sessão lateral. Worktree e branch:
`v3-corpo-acoplamento`. Status: **ABERTA; a etapa 1 (só papel) entregue, todas as decisões PROPOSTAS.**

Categoria: arquitetura (o PR da etapa 1 vai como implementação: ver o desvio D-CA-R1). Origem: Matheus, 2026-11-18: redesenhar o corpo
para que a fome e a energia não disputem a mesma decisão. A etapa 1 é só papel: o diagnóstico do acoplamento, as opções atrás de chave e
as decisões D-CA-n.

## 1. Pergunta

Por que a energia baixa e a fome urgente chegam juntas à mesma decisão, e qual mudança no corpo as separa sem mexer no `engine.py`?

A pergunta vem do fechamento da VALUATION (`docs/RESULTADO_V3_VALUATION_CONSERTO.md`, seção 3): no REL, **0,635** das decisões com a
energia abaixo de `lambda_sono` (S/4) têm a fome urgente. Por isso o conserto do reflexo do sono falhou na G2: o pet não pode comer e
descansar ao mesmo tempo. O Matheus concluiu que o gargalo é o corpo, e não o algoritmo.

## 2. Depende de

- Da `main` em `34894b50` (o merge do #984). Nada mais.
- Das decisões D-CA-1 a D-CA-7 (seção 8), antes da etapa 2.

## 3. Mudança mínima

- **Na etapa 1 (este PR):** nenhum código do pacote `digilab/` nem do `web/app/` muda. Entram:
  - a sonda descritiva, `experiments/sonda_v3_corpo_acoplamento.py`;
  - o teste dela, `tests/test_corpo_acoplamento.py`;
  - o artefato, `artifacts_v3_corpo_acoplamento/sonda.json`;
  - este documento e a seção do desvio no `docs/registro/2026-11.md`.
- **O que nunca muda:** o `digilab/engine.py`, as runs da v1 e as versões antigas do pet. Toda mecânica da etapa 2 entra atrás de chave
  desligada, com o gabarito das vidas de hoje gravado antes, num commit próprio.

## 4. Experimento e gate (se houver run)

- **Na etapa 1, nenhuma run de pesquisa e nenhuma faixa.** A sonda usa as sementes dos testes (101, 202, 303, 404 e 505), um processo,
  e só lê a vida (seção 9.1).
- **Na etapa 2:** a sonda com a chave ligada, nas mesmas sementes, como descritivo. Uma run de pesquisa só com o plano de análise
  `docs/PLANO_ANALISE_V3_CORPO_ACOPLAMENTO.md` commitado antes e uma faixa nova pedida ao coordenador (D-CA-6).
- GPU: não.

## 5. Entrega

- **Testes:** `python -m pytest tests/ -q`; em `web/app`: `npm test`, `npm run tipos` e `npm run e2e`, se a frente tocar a web (a etapa 1
  não toca).
- **Registro:** uma seção própria no fim do arquivo do mês, `docs/registro/AAAA-MM.md` (rodada de saúde, etapa 2).
  - **Não edite o índice `docs/REGISTRO_DESVIOS.md`:** ele é gerado (`python tools/gerar_indice_desvios.py`) por quem faz o merge.
  - Um conflito no índice se resolve rodando o gerador, nunca à mão (`docs/TAREFA_V3_INDICE_DESVIOS.md`).
  - O resumo da etapa vai no corpo do PR e numa seção no fim do documento da frente (o `RESULTADO_V3_*.md` da run ou o `TAREFA_V3_*.md`
    da etapa), nunca no `CLAUDE.md` (rodada de saúde, etapa 1).
- **O PR** vai contra a `main`, com o resumo e os números, cada um com o artefato. Avisar o coordenador. O merge é só do Matheus.
- **O corpo do PR** segue o `.github/pull_request_template.md`; o CI (`tools/verificar_relato.py`) confere os campos e a evidência da
  categoria.

## 6. Fora desta tarefa

- A calibração de qualquer número novo. Os números da seção 10 são exemplos para dimensionar as opções, todos PROPOSTOS e SEM FONTE.
- O cérebro: o reflexo do sono, a guarda do conserto e as unidades do M-ARB ficam como estão. A pergunta é do corpo.
- O jogo web: nenhuma versão nova do pet nesta tarefa, até a validação (D-CA-7).
- Uma ação nova do pet (a opção C), salvo se o Matheus a escolher (D-CA-3).

## 7. Critérios de aceitação

1. A sonda roda do zero e reproduz o artefato: `python experiments/sonda_v3_corpo_acoplamento.py --saida <outra pasta>` dá o mesmo
   conteúdo, menos o commit, o `git_limpo` e a duração do `meta`.
2. `python -m pytest tests/test_corpo_acoplamento.py -q` passa: a instrumentação só lê (a vida sai byte a byte a de sempre), a contabilidade
   do cansaço fecha decisão a decisão e o corte faz o que diz numa sequência feita à mão.
3. Cada número da seção 9 está no `artifacts_v3_corpo_acoplamento/sonda.json`, no campo citado.
4. Cada opção da seção 10 diz o que muda, o que quebra e o custo, e cada decisão da seção 8 traz a recomendação e o custo de errar.

## 8. Precisa do Matheus

Todas as decisões são PROPOSTAS. A etapa 2 só começa com elas.

- **D-CA-1. Aceitar o diagnóstico.** As duas chegam juntas por uma causa comum: ficar sem comer.
  - A fome que o cérebro lê é um relógio, que sobe a cada tick, dormindo ou acordado.
  - O mesmo jejum esvazia o combustível, e a ponte ME-1 (a falta de combustível) sobe o cansaço.
  - Nem o tempo acordado sozinho, nem o adiamento, nem o andar explicam a maior parte (seção 9).
  - **Recomendação:** aceitar.
  - **Custo de errar:** a etapa 2 mexeria na peça errada. A sonda com a chave ligada, antes de qualquer run, mostra o erro cedo e barato.
- **D-CA-2. A opção da etapa 2.**
  - **Recomendação:** a opção D, em que a falta de combustível sobe a fome, e não o cansaço. A E (a digestão converte a comida inteira) fica
    como a segunda, e as duas podem ir juntas, cada uma com a sua subchave.
  - **Custo de errar:** a D reabre a ME-1, uma decisão de 2026-10-11 (D-CA-5). Se o cansaço pela fome for desejado como comportamento, o pet
    perde esse traço. Os dois custos ficam atrás da chave e não chegam a nenhum pet sem a validação.
- **D-CA-3. As opções A (comer restaura a energia) e C (a ação combinada) ficam fora.**
  - **Recomendação:** não seguir.
    - A A trata o sintoma: no jejum longo, que é o caso dominante, não há comida ao alcance para restaurar nada.
    - A C custa uma ação nova em todo o cérebro e na web, e não fecha o déficit.
  - **Custo de errar:** baixo. As duas continuam possíveis depois da D, se a coincidência que sobrar for de outro tipo.
- **D-CA-4. A opção B (dormir desacelera a fome) parte de uma premissa que não vale hoje.**
  - O que dormindo cai à metade é o gasto do combustível. A fome lida sobe igual, como mostra a seção 9.3.
  - Sozinha, a B piora o acoplamento: a digestão só converte o que tira da fome, então uma fome mais lenta baixa o teto do combustível.
  - **Recomendação:** não seguir sozinha. Só como subchave junto da E, e só se a sonda pedir.
  - **Custo de errar:** a fome do pet que dorme pouco mudaria sem ganho no acoplamento.
- **D-CA-5. Reabrir a ME-1 atrás de chave.**
  - A ME-1 (2026-10-11, `docs/TAREFA_V2_METABOLISMO.md`) fez da falta de combustível "a única ponte" para o pet, pelo cansaço.
  - A D move essa ponte para a fome, só com a chave ligada. Desligada, a ME-1 vale como hoje.
  - **Recomendação:** autorizar a reabertura, só atrás da chave.
  - **Custo de errar:** pequeno enquanto a chave estiver desligada. Ligada no jogo, os números do equilíbrio do cuidado (E1 e E2, v38 e v39)
    precisam de nova calibração.
- **D-CA-6. Como medir a etapa 2.**
  - **Recomendação:**
    1. o código atrás da chave, no Python e no TS juntos, com o gabarito antes;
    2. a sonda com a chave ligada, nas sementes dos testes, como descritivo;
    3. só depois, se o descritivo mostrar a coincidência caindo, um plano de análise com uma faixa nova (pedida ao coordenador) e os gates
       da VALUATION: a exaustão, a privação e a taxa por episódio.
  - **Custo de errar:** rodar a validação sem o descritivo queimaria uma faixa numa mudança que talvez não separe as duas.
- **D-CA-7. O jogo.**
  - **Recomendação:** a chave entra no `web/app/motor/corpo.ts` com paridade, desligada. A versão nova do pet só vem depois da validação
    e com uma nova rodada de equilíbrio do cuidado.
  - **Custo de errar:** um pet com o corpo novo, sem calibração, dormiria menos e comeria em outro ritmo. As metas do cuidado (as 52
    linhas do E2) mudariam sem medida.

## 9. Etapa 1: o diagnóstico (2026-11-18)

### 9.1 A sonda

- **O que roda:** `python experiments/sonda_v3_corpo_acoplamento.py`.
  - Faz 120 vidas: o REL e o CON × as 12 células da C4 × as sementes 101, 202, 303, 404 e 505.
  - Cada vida é a do `run_v3_valuation_conserto.viver`: o MotorGravaCorpo, o pet sozinho, 14 dias, orçamento 16.
  - Rodou num processo, em 181 s, com a árvore limpa no `28dd69cb` (o `meta` do artefato).
- **O artefato:** `artifacts_v3_corpo_acoplamento/sonda.json`, sha256 `f4f5962c…ecbf4`. Os números abaixo são do
  `agregado.REL.todas`, salvo onde outro campo é citado.
- **Como ela lê:** o corpo da vida ganha, na instância, invólucros que anotam de onde vem cada variação do cansaço:
  - o basal do dia e o da noite;
  - o descanso do sono;
  - a falta de combustível;
  - as atividades (o brincar e o explorar do pet e o brincar do dono);
  - o andar.

  A soma das fontes fecha o cansaço de cada decisão, exata. Uma variação sem fonte falha alto, e o teste confere que o log sai byte a byte o
  da vida sem a sonda.
- **O corte:** decisão a decisão. A janela de cada decisão com as duas vai da última decisão descansada (o cansaço até C/2) até ela. A
  classe é a fonte que mais pôs cansaço nessa janela. As marcas estão na docstring da sonda.

### 9.2 Os números

**Nas sementes dos testes, a coincidência é maior que na faixa da VALUATION:** 12 070 das 15 906 decisões com a energia baixa têm a fome
urgente, **0,759** (`fracao_ambas_na_energia_baixa`). Na faixa 73xxx, ela foi 0,635. Por vida, a fração vai de 0,021 a 0,98 (mediana
0,75; a conta sai das `vidas`).

Por lugar:

| lugar | coincidência | combustível em falta, com as duas | classe `falta_combustivel` |
|---|---|---|---|
| comedouro | 0,537 | 0,967 | 0,579 |
| longe | 0,845 | 0,974 | 0,787 |
| `longe_fixo` | 0,821 | 0,978 | 0,832 |

**O corte das 12 070 decisões com as duas, por causa** (`fracao_por_classe`, `parte_media`, `fracao_lados`):

| causa | classe (a fonte que mais pôs cansaço) | parte média do cansaço da janela |
|---|---|---|
| **a falta de combustível (a ponte ME-1)** | **0,767** | **0,406** |
| o tempo acordado (o basal do dia e da noite) | 0,222 | 0,343 |
| as atividades | 0,011 | 0,182 |
| o andar | 0,000 | 0,069 |

**As marcas, nas mesmas 12 070:**
- o combustível abaixo de C/4, com a ponte ligada: **0,974**. Nas decisões com a energia baixa e sem a fome urgente, ele está em falta em
  0,553 (`fracao_combustivel_em_falta_na_baixa_sem_fome`);
- a fome já urgente na entrada do trecho cansado: **0,993**. A fome vem antes da energia baixa, quase sempre;
- a fome no teto (a falta da fome em C): 0,577;
- o pet dormindo na decisão: 0,176;
- o pet viu comida, depois de a fome ficar urgente, e não escolheu comer (`adiou`): **0,116**;
- 603 decisões com as duas antes de o pet comer pela primeira vez, 581 delas no `longe_fixo` (`ambas_sem_ter_comido`, nos agregados por
  lugar);
- mediana de 57 decisões desde a última refeição (`decisoes_desde_comer_mediana`).

**O balanço, em C por dia** (`cansaco_em_c_por_dia`, `metabolismo_em_c_por_dia`, `orcamento_combustivel_em_c_por_dia`):
- **O cansaço que entra:**
  - a falta de combustível, **0,829**, a maior fonte;
  - as atividades, 0,634;
  - o basal do dia, 0,563;
  - o basal da noite, 0,526;
  - o andar, 0,279.

  O sono tira 2,787. A ponte está ligada em 0,518 dos ticks (`fracao_ticks_combustivel_em_falta`).
- **O combustível:**
  - a digestão converte 1,041;
  - a comida descartada com a fome em zero soma 0,386 (`descartado_fome_zero`);
  - o gasto real é de 1,083 (o basal 0,531 e as atividades 0,552).
- **O orçamento:**
  - o teto da conversão pelo relógio da fome é 1,200 (375 por tick × 1 440 / C);
  - a demanda é de 1,467: o basal, no sono medido (0,465 dos ticks), dá 0,737, e as atividades e o andar dão 0,730.
  - **A demanda passa o teto em 0,267 C por dia, mesmo com o pet que come tudo o que a fome deixa.**

### 9.3 As hipóteses do pedido, uma a uma

1. **"As duas sobem com o tempo acordado": em parte.**
   - A fome lida é um relógio. Ela sobe o `fome_tick` (375 por tick) em 0,998 dos ticks dormindo e em 0,999 acordado, fora a ingestão e os
     cortes (`fracao_fome_tick`).
   - O basal acordado é a classe de 0,222 e 34 % do cansaço da janela.
   - O tempo pesa, mas não é o que faz as duas coincidirem em 3 de cada 4 decisões.
2. **"As atividades gastam o combustível e a energia juntos": sim, pelo caminho do combustível, não pelo do cansaço direto.**
   - Como cansaço direto, as atividades e o andar são a classe de só 0,011 (25 % da parte).
   - Pelo ME-3, elas gastam 0,730 C por dia de combustível que a fome não vê: a fome não sobe com o gasto.
   - Esse gasto faz o déficit estrutural, e o déficit liga a ponte.
3. **"O pet adia o comer até a fome ficar urgente": pouco.**
   - A fome vem antes em 0,993, mas o pet que viu comida e não comeu é só 0,116.
   - O resto é o pet que não tem comida à vista: no `longe_fixo`, 581 decisões com as duas antes da primeira refeição.
4. **"A comida longe custa energia para chegar": pouco como custo.**
   - O andar é a classe de 0 e 7 % da parte.
   - O lugar pesa por outro caminho: longe, o pet come menos, e o combustível fica mais tempo em falta (0,552 dos ticks no longe e 0,454 no
     comedouro, no `agregado.REL.<lugar>`).
   - O que custa é o não comer, não o caminho.

**Duas causas que a sonda trouxe:**
5. **A ponte ME-1 é a causa principal:** é a classe de 0,767 e a maior fonte de cansaço do dia (0,829 C).
   - O mesmo jejum que deixa a fome urgente esvazia o combustível, e abaixo de C/4 o cansaço sobe +500 por tick, o de um tick acordado de dia.
   - É uma coincidência por construção: a energia baixa é, na maior parte, fome por outro nome.
6. **A digestão só converte o que tira da fome** (`Corpo._digerir`).
   - Com a fome em zero, a comida sobra e é descartada: 0,386 C por dia, enquanto o combustível passa metade do tempo em falta.
   - O teto da conversão é o relógio da fome. Com a demanda acima dele, o déficit não fecha, coma o pet o quanto comer.

**O CON (o conserto ligado), ao lado:** a coincidência é 0,767 (`agregado.CON.todas`).
- O tempo acordado passa a ser a classe de 0,602 e a falta de combustível, de 0,392, porque o pet fica mais tempo acordado com a energia
  baixa.
- O combustível segue em falta em 0,951 delas.
- O conserto mudou quem dorme, não a causa.

### 9.4 O que o diagnóstico não demonstra

- **Não é contrafactual.** As marcas "sem esta fonte, a decisão não teria a energia baixa" são uma conta aditiva sobre a vida que
  aconteceu: o pet não se comportaria igual com outro corpo. Perto do limiar, quase toda fonte sai "necessária" (de 0,966 a 0,998). Por
  isso a classe vai pela parte.
- **Nada fora das sementes dos testes:** cinco sementes, 120 vidas. A diferença para os 0,635 da 73xxx não foi investigada.
- **Nada sobre o jogo web:** o pet do jogo usa o mesmo corpo do v11 (`web/app/motor/constantes.ts`, `CCO_V11`), com a ME-1. A vida dele,
  com o dono de verdade e sem os quatro donos da bancada, não foi medida.
- **Nada sobre o cérebro A.**

## 10. As opções de desenho (todas PROPOSTAS, cada uma atrás de uma subchave desligada da `ConfigCorpo`)

Comum a todas:
- **A chave desligada** dá a vida de hoje byte a byte. O gabarito das vidas de hoje é gravado antes, num commit próprio, e um teste o
  confere.
- **A paridade:** a mudança entra no `digilab/corpo.py` e no `web/app/motor/corpo.ts` juntos. O `tests/gabaritos/corpo_quimica_python.json`
  ganha uma seção nova, e as de hoje não mudam. O `web/app/test/metabolismo.test.ts` e o `corpo.test.ts` passam com a chave desligada.
- **O que só quebra com a chave ligada:**
  - a calibração do cuidado (`docs/RESULTADO_V3_EQUILIBRIO_CUIDADO_E1.md` e `_E2.md`; as 52 linhas de meta da v38 e da v39);
  - a transferência da LONGE_GEOMETRIA: o I-PAD (+0,071) vem quase todo do sono (P-a, s = 0,96, `docs/RESULTADO_V3_LONGE_GEOMETRIA.md`).
    Um corpo que dorme menos muda esse caminho. O resultado registrado continua válido para o corpo de hoje e não vale para o novo sem medir.

| opção | o que muda no corpo | o que a sonda diz, sem simular | o que quebra além do comum | custo |
|---|---|---|---|---|
| **A. comer restaura a energia** (pedido) | a comida madura também tira cansaço (um efeito novo no `estimulo_consumo_mundo`) | trata o sintoma: em 0,577 das decisões com as duas, a fome está no teto, e falta a comida, não o efeito dela | o cansaço deixa de querer dizer "precisa dormir"; o sono do pet que come cai | baixo no código; alto na leitura do pet |
| **B. dormir desacelera mais a fome** (pedido) | o `fome_tick` vira dois emissores, acordado e dormindo (o dormindo menor) | **a premissa não vale hoje:** dormindo, só o combustível gasta a metade. Sozinha, piora: o teto da conversão cairia de 1,200 para cerca de 0,921 C por dia (1,2 × (1 − 0,465/2), uma conta sobre o artefato), abaixo da demanda de 1,467 | a fome do pet que dorme | baixo |
| **C. uma ação combinada** (pedido) | uma `AcaoPet` nova (comer e descansar), com o efeito das duas | não fecha o déficit | o `digilab/events.py` e todo o cérebro (as unidades do M-ARB, o M-MEM, o log), a web, os gabaritos do cérebro e o glossário das ações; o `engine.py` não muda, mas o enum do log muda | alto |
| **D. a falta de combustível sobe a fome, não o cansaço** (da sonda) | o emissor `falta_combustivel` troca o alvo: abaixo de C/4, +k na fome em vez de +500 no cansaço | tira a maior fonte de cansaço (0,829 C por dia, a classe de 0,767). A fome sobe mais justo quando o combustível falta, e o teto da conversão sobe com ela: ao preço de hoje, até 1,200 + 0,829 = 2,029 C por dia, acima da demanda. A energia baixa volta a querer dizer cansaço | reabre a ME-1 (D-CA-5). O pet sente o jejum como fome, mais cedo | médio: uma linha do grafo no Python e no TS, a seção nova do gabarito do corpo, a sonda com a chave |
| **E. a digestão converte a comida inteira** (da sonda) | o alimento vai ao combustível pela quantidade comida, não pelo que tira da fome; a fome cai como hoje | os 0,386 C por dia descartados viram combustível: 1,041 + 0,386 = 1,427, perto da demanda de 1,467. A ponte segue ligada no pet que não come (o `longe_fixo`) | a contabilidade do metabolismo (o `descartado_teto` passa a contar) e a reserva | médio |
| **F. as atividades sobem a fome pelo que gastam** (da sonda) | o ME-3 tira do combustível e põe a mesma fração na fome | a fome passa a ver o gasto. O teto sobe 0,730 C por dia, mas a fome fica urgente mais cedo: mais decisões com a fome urgente, e a ponte segue | as metas do cuidado da fome | médio |

**A leitura:** a D é a única opção que ataca as duas pontas.
- Tira o cansaço que o jejum causa, que é o que faz as duas coincidirem.
- Fecha o déficit pela própria fome: a fome sobe com a falta, e a conversão sobe com a fome.

A E fecha o déficit sem tirar a ponte. A A, a B e a C não atacam a causa. O tamanho da D, o k, é um número novo, PROPOSTO, SEM FONTE, para
a etapa 2 (o 500 de hoje é o ponto de partida natural).
