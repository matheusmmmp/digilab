# TAREFA V3 — CORPO_ACOPLAMENTO (2026-11-18)

Coordenador: a sessão do Matheus que abriu esta (Claude Code). Worker: Claude Code, Opus 5.5, sessão lateral. Worktree e branch:
`v3-corpo-acoplamento` (a etapa 1) e `v3-corpo-acoplamento-e2` (a etapa 2). Status: **ABERTA; a etapa 1 (#994) e a etapa 2 entregues; as
D-CA-1 a D-CA-7 APROVADAS (Matheus, 2026-11-18); a D-CA-8 PROPOSTA (seção 11.4).**

Categoria: arquitetura (os PRs vão como implementação: ver o desvio no `docs/registro/2026-11.md`). Origem: Matheus, 2026-11-18: redesenhar o corpo
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

**As D-CA-1 a D-CA-7 foram APROVADAS pelo Matheus em 2026-11-18 ("Aprovo a D-CA-1 a D-CA-7, siga para a etapa 2").** O texto abaixo é o
que ele aprovou, sem mudança; o que veio depois está na seção 11.

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

## 11. Etapa 2: a opção D atrás da chave (2026-11-18)

O pedido (as D-CA-2, D-CA-5, D-CA-6 e D-CA-7 aprovadas):
1. o gabarito das vidas de hoje, num commit próprio;
2. a subchave da opção D no Python e no TS, desligada, com paridade;
3. a sonda com a chave ligada, nas sementes dos testes, como descritivo.

Nenhuma run de pesquisa rodou, e nenhum pet do jogo liga a chave.

### 11.1 O que entrou

- **O gabarito de antes** (o commit `fd784619`, antes de qualquer código): `tests/gabarito_corpo_acoplamento.py` grava
  `tests/gabaritos/corpo_acoplamento_de_hoje.json`.
  - São as vidas da VALUATION: o REL, os quatro donos, o `longe_fixo` e o comedouro, a semente 101, 3 dias.
  - De cada vida, o sha256 do log, do estado do cérebro, do resumo do mundo físico e da série do corpo.
  - O `tests/test_gabarito_corpo_acoplamento.py` confere com a chave padrão e com a desligada passada explícita.
- **A chave no Python:** a `ConfigAcoplamentoCorpo` (`digilab/config.py`), com `ligada` e `falta_fome`.
  - O status fica em `PARAMETROS_ACOPLAMENTO_CORPO`: a `ligada` DECIDIDA pela D-CA-2; o `falta_fome` = 500 PROPOSTO, SEM FONTE (o 500 do
    `falta_cansaco` de hoje).
  - Ela é uma config própria, como a `ConfigLutaCorpo`, para o dump da `ConfigCorpo` não mudar. Um campo novo ali mudaria os gabaritos do
    corpo e do cérebro A sem mudar vida nenhuma.
  - Ligada, o emissor `falta_combustivel` sobe a fome em vez do cansaço (`grafo_do_corpo`). Ela exige o metabolismo e entra pelo
    `Corpo(cfg_acoplamento=...)` e pelo `MotorCorpo(cfg_acoplamento_corpo=...)`.
  - Os testes estão em `tests/test_corpo_acoplamento_chave.py`.
- **A chave no TS:** a `ConfigAcoplamentoCorpo` em `web/app/motor/corpo.ts`, com as mesmas conferências, pelo `Corpo({acoplamento})` e pelo
  `grafoDoCorpo`.
  - A paridade vem do `experiments/exportar_gabarito_corpo_acoplamento.py`, que grava `tests/gabaritos/corpo_acoplamento_python.json`, um
    arquivo próprio: o `corpo_quimica_python.json` não muda.
  - O `web/app/test/corpo_acoplamento.test.ts` rejoga três corpos: o do v11 sem o mundo, o do v11 com o mundo, e a etapa 6 com o
    metabolismo. De cada um, a tabela, o relato, a grade de casos e a sequência de 3 000 operações com o sha256.
  - O motor do jogo (`motor_corpo.ts`, `motor.ts`) não muda: nenhum pet liga a chave (D-CA-7).
- **A sonda** ganhou o `--chave-d` e a taxa de base: a fome urgente em todas as decisões e nas com a energia boa.
  - Os dois artefatos novos rodaram no `59aad74e`, com a árvore limpa:
    - `artifacts_v3_corpo_acoplamento/sonda_e2_hoje.json`, a chave desligada, sha256 `1b785c33…`;
    - `artifacts_v3_corpo_acoplamento/sonda_chave_d.json`, a chave ligada, sha256 `b9600350…`.
  - O `sonda.json` da etapa 1 fica como estava. A `sonda_e2_hoje.json` repete os números dele e acrescenta os campos novos.

### 11.2 Os números (o `agregado.REL.todas` dos dois artefatos; 60 vidas cada)

| medida | hoje (`sonda_e2_hoje`) | com a D (`sonda_chave_d`) |
|---|---|---|
| decisões com a energia baixa (`energia_baixa`) | 15 906 (0,197 das decisões) | **11 127** (0,138) |
| decisões com as duas (`ambas`) | 12 070 (0,150 das decisões) | **8 466** (0,105) |
| a fome urgente na energia baixa (`fracao_ambas_na_energia_baixa`) | 0,759 | **0,761** |
| a fome urgente na energia boa (`fracao_fome_urgente_na_energia_boa`) | 0,248 | 0,328 |
| a fome urgente em todas as decisões (`fracao_fome_urgente_nas_decisoes`) | 0,349 | 0,388 |
| o cansaço da falta de combustível, C por dia | 0,829 | **0** |
| a classe `tempo_acordado` | 0,222 | 0,990 |
| os ticks dormindo (`fracao_ticks_dormindo_todos`) | 0,465 | **0,375** |
| as atividades e o andar, cansaço em C por dia | 0,634 e 0,279 | 0,694 e 0,324 |
| o combustível abaixo de C/4, nos ticks (`fracao_ticks_combustivel_abaixo_do_limiar`) | | 0,419 |
| a fome no teto, nas decisões com as duas | 0,577 | 0,695 |
| o andar desde a fome urgente necessário (`andar_na_fome`) | 0,732 | 0,814 |
| o pet dormindo, nas decisões com as duas | 0,176 | 0,039 |
| a conversão e o descarte, C por dia | 1,041 e 0,386 | 1,187 e 0,439 |

Por lugar, a fome urgente na energia baixa fica perto de onde estava:
- comedouro: 0,537 → 0,614;
- longe: 0,845 → 0,838;
- `longe_fixo`: 0,821 → 0,791.

No CON, ela sobe de 0,767 para 0,830, e as decisões com as duas, de 22 027 para 23 615 (`agregado.CON.todas`).

### 11.3 A leitura (descritiva; nenhuma classe, nenhum gate)

- **A D faz o que promete no corpo.** O jejum deixa de cansar: o cansaço da falta vai a 0. As decisões com a energia baixa caem 30 %, e as
  com as duas também caem 30 %: de 201 para 141 por vida.
- **A coincidência condicional não cai.** Nas decisões com a energia baixa que sobram, a fome está urgente na mesma fração, 0,761.
  - O acoplamento é real hoje: a fome urgente é 0,759 na energia baixa contra 0,248 na boa.
  - Com a D, ele fica menor (0,761 contra 0,328), mas continua.
- **O que sobra não é do corpo, pela leitura da sonda:**
  - a energia baixa vem do tempo acordado em 0,990;
  - o pet dorme menos (0,375 dos ticks);
  - o pet anda e explora mais (as atividades e o andar sobem);
  - o andar desde a fome urgente pesa em 0,814;
  - a fome chega ao teto em 0,695.

  O pet faminto sai atrás de comida, anda, e cansa. Esse caminho é do comportamento, não da química. É uma interpretação: a sonda não
  separa o cérebro do corpo.
- **A D mexe no sono, como a D-CA-7 previu:** os ticks dormindo vão de 0,465 a 0,375. O I-PAD da LONGE_GEOMETRIA, que vem do sono, não se
  transfere sem medir.
- **No CON, a D piora a coincidência** (0,830): o pet que não dorme com a fome urgente fica com mais fome.
- **O que não demonstra:** são cinco sementes, sem IC e sem classe. Nada sobre a privação, a exaustão e a taxa por episódio da VALUATION
  (os gates de uma run). Nada sobre o jogo.

### 11.4 O que a D-CA-6 pede agora, e a decisão nova

A D-CA-6 diz: "só depois, se o descritivo mostrar a coincidência caindo", o plano de análise com uma faixa nova. O descritivo é misto: a
contagem cai 30 %, e a fração não cai. A regra não decide sozinha, e por isso a run não foi preparada.

- **D-CA-8 (PROPOSTA). O que vem depois da D:**
  - **(a)** Seguir para o plano de análise da D, pela contagem. O primário seria as decisões com as duas por vida, e os gates os da
    VALUATION: a exaustão, a privação e a taxa por episódio. A faixa seria pedida ao coordenador.
  - **(b)** Somar a E (a digestão converte a comida inteira) na mesma bancada e repetir a sonda antes do plano.
  - **(c)** Aceitar que o que sobra é do comportamento e levar a pergunta ao cérebro: o pet faminto que anda até cansar.
  - **Recomendação:** a (a). A D já tira 30 % dos conflitos e a ponte que os causava no corpo. O que sobra pede uma medida com IC, e a run
    da D responde se a exaustão e a privação melhoram de fato.
    - A (b) mexe no combustível, que não é mais o que cansa.
    - A (c) é outra frente.
  - **Custo de errar:**
    - na (a), queimar uma faixa numa mudança que não mexe na fração que motivou a tarefa;
    - na (b), mais uma etapa de código sem medida;
    - na (c), deixar no corpo uma ponte que hoje é a maior fonte de cansaço.
