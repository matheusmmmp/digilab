# V2 — rodada 4: verificação de pendências e prompts dos workers (2026-10-04)

A divisão da rodada 4 está em `docs/V2_RODADA_3.md` e as quatro tarefas na `main` desde 2026-10-02 (#129). Este documento registra o
estado em 2026-10-04 e traz os prompts prontos para abrir os quatro chats.

## 1. Verificação das pendências (2026-10-04)

| onde | o que se viu | leitura |
|---|---|---|
| PRs no GitHub | nenhum aberto; o último de pesquisa foi o #129 (2026-10-02); depois só o #130 (ideia da aura do herói, mesclado) | a rodada 4 **não começou** |
| branches e worktrees do clone `v2` | nenhuma com commit fora da `main` nem arquivo modificado; nenhum branch `v2-n3`, `v2-n4`, `v2-bancada-mundos` ou `v2-plano-experimento-maior` | nenhum worker tem trabalho pela metade |
| branch local `voz-sem-japones` | só commits de merge à frente da `main`; PR #93 fechado | nada a recuperar |
| pastas `v2-equilibrio-geral`, `v2-excecao-e3`, `v2-excecao-espelho`, `v2-futuro-df` | vazias, sem git | sobras; podem ser apagadas |
| pasta `v1` (só leitura, branch `voz-revanche`, PR #91 mesclado) | 3 arquivos que **não estão na `main`**: `docs/deepdive_pesquisas_brasileiras_digilab.md`, `docs/prompt_contexto_digilab.md`, `tools/inventario_sprites.py`; os outros não versionados são versões antigas de arquivos que a `main` já revisou | decisão do Matheus (seção 5) |

As worktrees dos quatro workers foram criadas a partir da `main` (48b2a05): `D:\Trab\digilab\v2-n4-frutas`, `v2-n3-consequencia`,
`v2-plano-experimento-maior` e `v2-bancada-mundos`, cada uma no branch do mesmo nome. Abra cada chat **na pasta da worktree**.

## 2. Ordem e conflitos

- Os quatro começam já. Dependências da rodada: o D monta o mundo `bola` agora e deixa `descasado` e `mutavel` como contrato até as frutas do
  A entrarem; o C só escreve; o B não depende de ninguém.
- **`digilab/ambiente.py`** é do chat A nesta rodada. O D usa o `MotorAmbiente` como está; se precisar mudar algo nele, combina com o A pelo
  coordenador antes.
- **`digilab/policies/lobos.py`** é só do chat B.
- `CLAUDE.md` e `docs/REGISTRO_DESVIOS.md`: cada worker acrescenta a própria seção no fim; no conflito, mantêm-se todas.
- Sementes (fechadas no `V2_RODADA_3.md`): N3 8101…8505 / 9101…9505; N4 10101…10505 / 11101…11505; experimento maior 14101…14505 /
  15101…15505 (o C só cita). O D não usa faixa reservada.

## 3. Pistas de literatura para esta rodada

Achadas numa busca de 2026-10-03, com DOI conferido no Crossref (metadados e resumo). **Não estão na tabela verificada do projeto**: são
pista, não evidência. Ler o artigo antes de citar.

- Para o B: Yoshida et al. 2024, *Neural Networks*, `10.1016/j.neunet.2024.106379`. Entre as recompensas homeostáticas testadas, a
  diferença na função de drive foi a melhor. A referência verificada do N3 continua Keramati e Gutkin 2014.
- Para o C, risco de novidade na pergunta maior: Giannakakis et al. 2023, ALIFE, `10.1162/isal_a_00606` (a variabilidade do ambiente
  controla quanto o agente depende de plasticidade); Wright et al. 2022, *Biological Reviews*, `10.1111/brv.12879` (aprendizado como norma
  de reação); Giannakakis et al. 2024, *Artificial Life*, `10.1162/artl_a_00458` (gargalos levam a regras interpretáveis).
- Para o C, braços do dono: Celemin et al. 2023, `10.1007/s00521-022-08118-z` (professores imperfeitos, correção e avaliação); Christofi
  et al. 2025, `10.1109/ro-man63969.2025.11217920` (como pessoas escolhem entre demonstrar e avaliar).

## 4. Prompts

### Chat A — N4, frutas no mundo (pasta `D:\Trab\digilab\v2-n4-frutas`)

> Você é o worker A da rodada 4 da V2 do Digilab. Antes de tudo, rode `git fetch origin` e `git merge --ff-only origin/main`. Leia o `CLAUDE.md` inteiro, `docs/V2_TRABALHO_PARALELO.md`, `docs/V2_RODADA_4_PROMPTS.md`,
> `docs/TAREFA_V2_N4_FRUTAS.md` e `docs/DEFINICOES_FRUTAS_V2.md`. Trabalhe só nesta worktree (branch `v2-n4-frutas`). O aprendiz fica
> desligado: frutas como sub-decisão de comer, dois registros por fruta (`incentivo` e `avaliacao`), saciedade específica, preferência
> inata e neofobia no genoma com rng própria, efeito ruim no humor fora de `em_privacao`, ofertas fora do sorteio do dono aleatório e fora
> do orçamento (B1, B2). `digilab/ambiente.py` é seu nesta rodada; não toque em `lobos.py`, `engine.py`, `AcaoPet` nem na web.
> PR 1: `docs/PLANO_ANALISE_V2_N4.md` commitado antes de qualquer run, código e calibração 10101…10505. PR 2: validação 11101…11505, uma
> vez, sem reajustar olhando a validação. Falha é registrada e não para a V2. Ao terminar cada PR: `python -m pytest tests/ -q` inteiro,
> seção no fim do `CLAUDE.md` e do `docs/REGISTRO_DESVIOS.md`, números cada um com o artefato, aviso ao coordenador. Pare depois do PR 2.
> Merge só quando o Matheus pedir.

### Chat B — N3, consequência como reforço (pasta `D:\Trab\digilab\v2-n3-consequencia`)

> Você é o worker B da rodada 4 da V2 do Digilab. Antes de tudo, rode `git fetch origin` e `git merge --ff-only origin/main`. Leia o `CLAUDE.md` inteiro, `docs/V2_TRABALHO_PARALELO.md`, `docs/V2_RODADA_4_PROMPTS.md`,
> `docs/TAREFA_V2_N3_CONSEQUENCIA.md` e `docs/RESULTADO_V2_L1.md`. Trabalhe só nesta worktree (branch `v2-n3-consequencia`). Implemente a
> fonte `consequencia` da bancada: o sinal é a redução do déficit homeostático pela própria ação, medida na transição que o aprendiz já
> recebe, sem nada do dono. A regra de atualização é a da L1, sem mudança; só a fonte muda. `lobos.py` é seu; não toque em `engine.py`,
> `AcaoPet`, bandit, `ambiente.py` nem na web. No plano, decida e justifique os drives (fome, higiene, energia; humor fora), a forma do
> sinal e a janela de crédito. A seção 3 do `V2_RODADA_4_PROMPTS.md` tem uma pista sobre a forma do sinal, que não está na tabela
> verificada. Braços: P0, P1, P3 e o "só cuidado" acoplado. PR 1: `docs/PLANO_ANALISE_V2_N3.md` commitado antes de qualquer run, código e
> calibração 8101…8505. PR 2: validação 9101…9505, uma vez. Falha é registrada e não para a V2. Ao terminar cada PR: pytest inteiro, seção
> no fim do `CLAUDE.md` e do `REGISTRO_DESVIOS`, números com artefato, aviso ao coordenador. Pare depois do PR 2. Merge só pelo Matheus.

### Chat C — plano do experimento maior (pasta `D:\Trab\digilab\v2-plano-experimento-maior`)

> Você é o worker C da rodada 4 da V2 do Digilab. Antes de tudo, rode `git fetch origin` e `git merge --ff-only origin/main`. Só papel: nenhuma run e nenhum código. Leia o `CLAUDE.md` inteiro,
> `docs/V2_TRABALHO_PARALELO.md`, `docs/V2_RODADA_4_PROMPTS.md`, `docs/TAREFA_V2_PLANO_EXPERIMENTO_MAIOR.md`, `docs/ARQUITETURA_V2_VALIDACAO.md`
> (seção 6) e `docs/PLANO_V2_PESQUISA.md`. Use a skill `literatura-digilab` antes de escrever qualquer frase sobre literatura. Trabalhe só
> nesta worktree (branch `v2-plano-experimento-maior`). Entrega 1: `docs/PLANO_ANALISE_V2_EXPERIMENTO_MAIOR.md`, com as cinco predições
> registradas antes, a medida e o teste de cada uma, as condições casado, descasado e mutável como contrato com o N4 e a bancada de
> mundos, o tamanho de amostra justificado pela análise de poder da v1 sem inventar número, e as sementes 14101…14505 e 15101…15505.
> Entrega 2: `D:\Trab\digilab\docs\digibrain\integration\11_PROMPT_CLAUDE_SCIENCE_PLASTICIDADE.md`, no formato dos prompts 09 e 10. O
> prompt pede a busca verificada sobre a decomposição da plasticidade por fonte no mesmo agente. Ponha nele as pistas da seção 3 do
> `V2_RODADA_4_PROMPTS.md` como primeiras a conferir, porque estão perto da pergunta maior. Referências só VERIFICADAS no plano, e nenhuma
> alegação de novidade. No fim do plano, as decisões do Matheus com recomendação e custo de errar. Um PR, aviso ao coordenador, pare.
> Merge só pelo Matheus.

### Chat D — bancada: mundos e condições (pasta `D:\Trab\digilab\v2-bancada-mundos`)

> Você é o worker D da rodada 4 da V2 do Digilab. Antes de tudo, rode `git fetch origin` e `git merge --ff-only origin/main`. Leia o `CLAUDE.md` inteiro, `docs/V2_TRABALHO_PARALELO.md`, `docs/V2_RODADA_4_PROMPTS.md`,
> `docs/TAREFA_V2_BANCADA_MUNDOS.md` e `docs/RESULTADO_V2_A1.md`. Trabalhe só nesta worktree (branch `v2-bancada-mundos`). Infraestrutura,
> sem run de pesquisa: mundo `bola` na bancada com B1 e B2 (o dono aleatório nunca sorteia `por_bola`; a bola fora do orçamento), contrato
> de `casado`, `descasado` e `mutavel` (os dois últimos com `NotImplementedError` até as frutas do chat A), e modo acoplado que preserva os
> eventos do mundo. Use o `MotorAmbiente` como está: `ambiente.py` é do chat A nesta rodada, e qualquer mudança nele passa antes pelo
> coordenador. Não toque em `lobos.py`, `engine.py` nem na web. Gates: G1 em todo mundo novo; mundo `bola` com as regras da A1 reproduz a
> A1 byte a byte; testes de B1 e B2; acoplado com mundo reproduz. Só sementes de teste, nenhuma faixa reservada. Um PR: pytest inteiro,
> seção no fim do `CLAUDE.md` e do `REGISTRO_DESVIOS`, aviso ao coordenador, pare. Merge só pelo Matheus.

## 5. Decisões do Matheus

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| R4-1 | Os 3 arquivos que só existem na `v1` | ler e trazer à `main` o que servir (o levantamento de pesquisas brasileiras parece ser fonte do corpus DigiBrain); apagar o resto | ficam fora do git e se perdem com a pasta |
| R4-2 | Remover worktrees de frentes já mescladas (`v2-merge*`, `v2-coord-r1`…`r4`, `v2-l0-lobos`, `v2-l1-*`, `v2-a1-bola-impl`, `v2-bancada`, `v2-frutas-definicoes` e outras) e as 4 pastas vazias | remover; nenhuma tem trabalho fora da `main` | nenhum: o git guarda tudo |

## 6. Depois desta rodada (rodada 5, pelo `ROADMAP_V2.md`)

Com o N3 e o N4 mesclados: B faz o **N5** (dono informante, P2 e P2e, informação pela percepção e nunca como reforço); A apoia o N5 com os
eventos de informação no motor da V2; C escreve o plano do **N6** (memória, quatro marcos); D faz o **N7** (arbitragem, duas prioridades).
Reservas: N5 12101…12505 / 13101…13505. O experimento maior (rodada 6) espera N3, N4 e N5.
