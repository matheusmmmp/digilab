# TAREFA V3 — INDIVIDUALIDADE (2026-11-07)

Coordenador: Matheus (sessão direta). Worker da etapa I0: Claude Code, Opus 5.5, worktree `v3-individualidade`. Worktree e branch:
`v3-individualidade` (as etapas seguintes com sufixo, como `v3-individualidade-i0`). Status: **ABERTA; a proposta na `main` (#676);
as IN-1 a IN-8 DECIDIDAS em 2026-11-07, pela recomendação; o I0 (a conferência) na `main` (#684); o I1 (a bateria como ferramenta)
na `main` (#695); o plano do I2 APROVADO (#700); o I2a na `main` (#707); o I2b (a run da linha de base, faixa 85101…85505)
na `main` (#718); o adendo 1 na `main` (#746); o plano do I5 APROVADO, na `main` (#747); o I5a na `main` (#751); o I5b na `main` (#768); o plano do I7 e o adendo 1 na `main` (#755, #769); o I7a (as medidas e
o orquestrador) entregue.**

Categoria: documentacao. Origem: Matheus, 2026-11-07: depois da conversa sobre o connectome e a escala, direcionar a pesquisa para o
temperamento herdado, o sinal do dono, a memória de episódios e o hábito, com uma medida comum de individualidade.

## 1. Pergunta

**O pet modular fica diferente dos outros de um jeito estável, e quanto disso vem do genoma, do dono e da interação?** A proposta inteira
está em `docs/futuro/individualidade_pet.md`. Ela junta o G1 do `docs/futuro/ecossistema_genetico.md` (a variância herdável) e uma
pergunta nova sobre o aprendiz modular (o dono), sem reabrir a leitura da v1 (`docs/LEITURA_CONSOLIDADA_DONO.md`).

## 2. Depende de

- Na `main`: nada além do que já está (`3d79072`).
- Do Matheus: as IN-1 a IN-8 (`docs/futuro/individualidade_pet.md`, seção 8), antes de qualquer etapa depois desta.
- Para o I3 e o I4: o Gate I no modular (GI-4; IN-4).

## 3. Mudança mínima

Esta etapa só escreve documentos: a proposta em `docs/futuro/individualidade_pet.md` e esta tarefa. Não mudam `engine.py`, o modular,
a web, o genoma (G0), as facetas (M5) nem o P2 (D-C2-4-2).

## 4. Experimento e gate (se houver run)

Nenhum nesta etapa. As etapas I2 a I5 terão o plano em `docs/PLANO_ANALISE_V3_INDIVIDUALIDADE.md`, commitado antes da primeira vida, e
uma faixa pedida ao coordenador. Nenhum número é decidido aqui.

## 5. Entrega

- Testes: não se aplicam (só documentos).
- PR contra a `main` com o relato no modelo. Merge só pelo Matheus.

## 6. Fora desta tarefa

Escalar a rede até o tamanho de um conectoma; um mecanismo novo de hábito; a calibração; a web até o I6; os dois pets
(`docs/futuro/individualidade_pet.md`, seção 6).

## 7. Critérios de aceitação

- `docs/futuro/individualidade_pet.md` existe, com a medida, o desenho, os passos I0 a I6 e as IN-1 a IN-8, cada uma com a recomendação e
  o custo de errar.
- Toda referência citada está em `docs/referencias/referencias_verificadas.csv` ou no `docs/research/digibrain/sources/`.
- Os links relativos dos documentos mudados resolvem (o CI da categoria documentacao).

## 8. Precisa do Matheus

As IN-1 a IN-8 estão DECIDIDAS (2026-11-07, pela recomendação). O I1 começa com o sim do Matheus.

## Resultado da proposta (2026-11-07, Claude Code, Opus 5.5, branch `v3-individualidade`)

A proposta e esta tarefa estão na `main` (#676, `df04915`).

## Resultado da etapa I0 (2026-11-07, Claude Code, Opus 5.5, branch `v3-individualidade-i0`)

- **As decisões:** as IN-1 a IN-8, pela recomendação. O Matheus escreveu "Agora siga com as recomendações" nesta sessão, depois do
  merge do #676.
- **A conferência das sondas** (`docs/futuro/individualidade_pet.md`, seção 3.1, "a conferência do I0"):
  - cinco das seis sondas saem de gestos ou estados que o motor já tem: comida nova, longe, bola, susto e tédio;
  - **a sonda "o dono chama" foi trocada por "o dono some"**, porque não existe ação de chamar do dono no `AcaoUsuario` (o desvio
    D-IND-I0-1). A troca lê o `chamar_atencao`, a ação em que a faceta `apego_dono` entra;
  - o susto sai do `tapa` só na cópia, nunca na vida real.
- **O dono das vidas:** o `CanalSemEnsino` das vidas da C1 e da C4 já cumpre a IN-6, e os quatro donos do protótipo são as personas.
- **Ficam para o I1:**
  - a forma da cópia: a cópia profunda ou o replay do prefixo, pela que passar no G2 e custar menos;
  - se o corpo das vidas da C4 liga os drives novos, porque o tédio depende disso.

## Resultado da etapa I1 (2026-11-07, Claude Code, Opus 5.5, branch `v3-individualidade-i1`)

- **A ferramenta:** `experiments/sondas_individualidade.py`, fora do `digilab/`. O `engine.py`, o cérebro e a web não mudam.
  - A vida é a da C4 (`run_v2_memoria_autobio.viver`), com o braço, o dono, o lugar, a semente e os dias como argumentos.
  - Por dia, o momento é o passo do dono em que cai a primeira decisão acordada da vida real a partir das 10 h, até as 18 h.
  - A cópia sai do replay do log até esse tick (`reproduzir_mundo(..., ate_tick=T)`). Cada réplica é uma cópia profunda dela, com a rng
    de política e a da posição derivadas por `derivar_semente`.
  - As decisões da janela (240 ticks) saem do registro do cérebro: as ações, a contagem, a latência da ação-chave (o `comer` da comida
    posta, pelo id) e as posições.
- **As janelas:** cinco, e não seis. O "dono some" e o "tédio" são a mesma janela sem estímulo, a `nula`, lida por dois traços
  (D-IND-I1-1). A `nula` também é o controle das outras.
- **O que o I0 deixou aberto, resolvido:**
  - a cópia é o replay do prefixo mais a cópia profunda por réplica (D-IND-I1-3);
  - o corpo das vidas da C4 liga os drives novos e os gestos (`drives_novos=True`, `gestos=True`), então o tédio e o susto existem.
- **O contato:** a comida nova e o longe usam o `deixar_comida` do motor, que é contato do dono, como no jogo (D-IND-I1-2). A bola não é
  contato.
- **Os números da ferramenta** (a hora, as janelas, as réplicas e as distâncias) são PROPOSTOS, SEM FONTE, no topo do módulo. Ela mede,
  não é mecânica do pet, e por isso eles não entram no `config.py`. O plano do I2 pode trocá-los antes da run.
- **O que o I1 não calcula:** nenhuma métrica. A bateria só grava as decisões de cada janela. A repetibilidade de cada traço, a divisão
  da variância e a norma de reação são do I2 e vão para o `digilab/metrics.py` ("métricas existem uma vez só"), com o plano registrado
  antes.
- **O gabarito:** nenhuma vida de hoje muda (o G2 prova isso por teste), então não há gabarito "antes" para gravar num commit próprio. O
  gabarito novo é o da própria bateria e nasce com ela.
- **Testes:** `tests/test_sondas_individualidade.py`, 8 testes.
  - o G2: a vida com e sem a bateria sai com o mesmo log e o mesmo resumo;
  - o tapa só na cópia; o determinismo; a cópia para no tick;
  - as cinco janelas e as réplicas em todo dia com sonda; o momento cai numa decisão acordada;
  - a sonda desconhecida falha alto;
  - o gabarito (o sha256 da bateria de uma vida de teste, em `tests/gabaritos/sondas_individualidade.json`).

## O plano do I2 (2026-11-07, Claude Code, Opus 5.5, branch `v3-individualidade-i2-plano`)

O `docs/PLANO_ANALISE_V3_INDIVIDUALIDADE.md` está APROVADO pelo Matheus (2026-11-07, "Aprovo todas"), com as IP-1 a IP-9 decididas pela
recomendação.
- O desenho: o REL e o REL+F, os quatro donos, o `comedouro`, 14 dias e 60 sementes pareadas, num total de 480 vidas.
- As medidas: seis traços e, por traço, o R_pet, o R_dia e o R_rep, o η² do dono, as facetas, a síndrome e a norma de reação.
- A regra escrita antes para os traços que entram no I3.
- O longe passa a 16 células do pet, fora da visão e dentro do cheiro.
- A faixa foi pedida ao Gerente. Nenhuma vida roda antes do APROVADO, da faixa, do I2a e do registro.

## Resultado da etapa I2a (2026-11-07, Claude Code, Opus 5.5, branch `v3-individualidade-i2a`)

O plano (#700) e a faixa 85101…85505 estão APROVADOS. O I2a é o código antes da run. Nenhuma vida da faixa rodou.
- **A bateria** (`experiments/sondas_individualidade.py`), num commit próprio:
  - o longe passou a 16 células do pet (`DIST_LONGE`, IP-3), e a janela grava a `dist0`;
  - o gabarito do I1 passava na `main` antes da troca, e o novo foi regravado no mesmo commit, com os dois sha256 na mensagem;
  - na fumaça (semente de teste 101), o `comer` do longe sobe de 0 para 5 em 42 janelas.
- **As métricas** (`digilab/metrics.py`, seção 4.6 do plano), com `tests/test_metrics_individualidade.py` (10 testes feitos à mão):
  - `tracos_individualidade` (os seis traços de uma réplica);
  - `icc1_grupos` e `icc1_estatisticas` (o ICC(1) com grupos desiguais, o n₀ e o truncamento), com `estatisticas_grupo`;
  - `eta2_grupos`, `spearman` e `reta_mmq`.
- **O orquestrador** `experiments/run_v3_individualidade.py`, com a config em `experiments/configs/v3_individualidade/individualidade.json`:
  - toda vida passa pelo G1, o cenário, o mecanismo, a memória do braço e o G2 da bateria;
  - a análise da seção 4 do plano tem o bootstrap sobre os pets (e sobre as sementes no η²), e a regra 7.4 roda no REL;
  - a trava: o cabeçalho APROVADO, a seção `## 12. O registro da run` (que só entra no I2b), a faixa, as bases, o K e os dias, no máximo
    4 processos e nada por cima de uma pasta;
  - testes: `tests/test_run_v3_individualidade.py`, 8 testes (a trava nos dois sentidos, a recusa de hoje sem o registro, a análise num
    caso sintético, a regra 7.4 e a fumaça de ponta a ponta com as sementes dos testes).
- **A lista do G2 separado da memória** (`tests/test_memoria_autobio.py`) ganhou o orquestrador, com o motivo.

## Resultado da etapa I2b (2026-11-08, Claude Code, Opus 5.5, branch `v3-individualidade-i2b`)

- **O registro:** a seção 12 do plano entrou antes da primeira vida (`0b3901f`). A suíte do dia deu 5108 passed e 7 skipped.
- **A run:** única, 480 vidas na faixa 85101…85505, com 4 processos e 2 h 42 min. O resultado está em
  `docs/RESULTADO_V3_INDIVIDUALIDADE.md`:
  - o R_pet é baixo (0,02 a 0,28); o R_dia exclui 0 em cinco traços, mas não no susto;
  - o η²_dono é alto na neofilia, na ousadia e no apego;
  - as três facetas acompanham o traço no sentido contrário ao esperado;
  - os seis traços ficam para o I3 pela regra 7.4.
- **Os desvios:** D-IND-I2b-1 (o incoerente idêntico ao atencioso no `comedouro`) e D-IND-I2b-2 (o custo dobrado).

## Depois do I2: as decisões, o adendo 1 e o plano do I5 (2026-11-09, Claude Code, Opus 5.5)

- **As decisões do Matheus** (D-IND-I2c-1 a 3, no registro):
  - o I5 vem primeiro, porque não depende do Gate I. O Gate I continua pausado pela DM-8, e o I3 e o I4 esperam;
  - o incoerente sai das etapas seguintes;
  - as facetas invertidas, dentro do dono, só descritivo.
- **O adendo 1 do plano do I2** (seção 13; o resultado na seção 7 do `RESULTADO_V3_INDIVIDUALIDADE.md`, #746): dentro do dono, nenhuma
  faceta acompanha o traço, e as facetas ficam no teto (192). A inversão do I2 vem da diferença entre os donos.
- **O plano do I5:** `docs/PLANO_ANALISE_V3_INDIVIDUALIDADE_I5.md`, APROVADO pelo Matheus em 2026-11-09 ("Aprovo todas"), com as IH-1 a IH-7 decididas pela recomendação. É o hábito como medida, sobre as
  vidas do I2 rejogadas do log: três perfis por dia (SEQ, LUGAR e HORA) e a distintividade de cada pet contra o dono e o mundo da
  semente.

## Resultado da etapa I5a (2026-11-10, Claude Code, Opus 5.5, branch `v3-individualidade-i5a`)

- **As medidas** (`digilab/metrics.py`, IH-7): `perfis_habito_dia` (SEQ, LUGAR e HORA de um dia, com o mínimo de 16 decisões
  acordadas), `distancia_entre_dias` (o D_si), `distancia_mesmo_dia` (o D_dono, o D_mundo e o D_braço), `distintividade_habito` (os H) e
  `media_habito`. Os testes, contra casos feitos à mão, estão em `tests/test_individualidade_i5.py`.
- **O orquestrador:** `experiments/run_v3_individualidade_i5.py`, com as configs `individualidade_i5.json` (a análise) e
  `individualidade_i5_fumaca.json`.
  - Ele lê o `vidas.tar.gz` do I2, rejoga cada vida e confere que o log refeito é o do disco e que há 96 decisões por dia.
  - Grava o `perfis.jsonl`, e a análise sai desse arquivo.
  - **A trava:** o cabeçalho APROVADO, a seção 11 do plano (o registro), o pacote, as bases e o K do I2, no máximo 4 processos e nada
    por cima de uma pasta.
- **A fumaça** (as sementes 101 e 202, K = 2, 14 dias, 24 vidas, 4 processos): o replay custou 3,1 s por vida, e a fumaça inteira
  1 min 36 s. Duas fumaças seguidas deram a mesma análise. Estimativa para as 360 vidas do I2: uns 5 min de replay com 4 processos.
- **As leituras do plano** estão no registro: D-IND-I5a-1 a 3.

## Resultado da etapa I5b (2026-11-10, Claude Code, Opus 5.5, branch `v3-individualidade-i5b`)

- **A análise única do I5** rodou sobre as 360 vidas do I2, com o registro antes (`977b33c`) e todos os logs refeitos iguais aos do disco.
  O resultado está no `docs/RESULTADO_V3_INDIVIDUALIDADE.md`, seção 8, e o artefato em `artifacts_v3_individualidade_i5/`.
- **O achado:** o H_dono não se distingue de zero em nenhum perfil nem braço, e o H_mundo fica acima de zero em todos. O pet se parece
  com os outros pets do mesmo dono tanto quanto com ele mesmo em outro dia: o que separa os pets é o dono (D-IND-I5b-1).
- **As expectativas:** a E1 não se confirma, a E2 sai ao contrário e a E3 se confirma sem separar a SEQ.
- **O custo:** 2,0 s por vida, 3 min 53 s ao todo com 4 processos.

## As etapas seguintes

| etapa | o quê | entrega |
|---|---|---|
| I1 | a bateria como ferramenta (`experiments/bancada/`), só leitura, com o gabarito e o G2 | código e testes, PR próprio |
| I2 | a linha de base descritiva no modular de hoje | `docs/PLANO_ANALISE_V3_INDIVIDUALIDADE.md` e uma faixa pedida antes; a run; o `RESULTADO_V3_INDIVIDUALIDADE.md` |
| Gate I | o Gate I no modular (IN-4), entre o I2 e o I3 | pela `docs/TAREFA_V2_GATE_I.md`, com os critérios no modular |
| I3, I4, I5, I6 | o temperamento, o dono, o hábito como medida e a ficha | pela proposta, seção 5 |
| I7 | o desenvolvimento contrafactual: a mesma vida com uma coisa diferente num dia, e o quanto o pet se afasta depois | `docs/PLANO_ANALISE_V3_INDIVIDUALIDADE_I7.md` (APROVADO); o I7a e o I7b, depois do I5b |

## O plano do I7, o desenvolvimento contrafactual (2026-11-10, Claude Code, Opus 5.5, branch `v3-individualidade-i7-plano`)

- **De onde vem:** a conversa de 2026-11-10 sobre como tirar da frente um achado. O Matheus escolheu a Q3, o desenvolvimento
  contrafactual, pela recomendação.
- **O plano:** `docs/PLANO_ANALISE_V3_INDIVIDUALIDADE_I7.md`, APROVADO pelo Matheus em 2026-11-10 ("Aprovo todas"), com as IR-1 a
  IR-9 decididas pela recomendação.
  - Cada pet do I2 é vivido de novo com uma única coisa diferente num dia (outra rng de política, ou um tapa), nos dias 2, 4, 6, 8 e 10.
  - O afastamento do ramo é medido pelos perfis do I5, contra um gêmeo com outro acaso desde o nascimento.
  - Três hipóteses rivais ficam escritas antes: a canalização, o ciclo que se reforça e o caos.
- **Sem mecanismo novo** (IN-7). O I7a depende do I5a na `main` (#751), e o I7b roda depois do I5b.

## O adendo 1 do plano do I7 (2026-11-10, Claude Code, Opus 5.5, branch `v3-individualidade-i7-adendo1`)

- **O adendo** está DECIDIDO pelo Matheus em 2026-11-10 ("E daí a gente parte para seguir as recomendações"), na seção 12 do
  `docs/PLANO_ANALISE_V3_INDIVIDUALIDADE_I7.md`, depois da conferência das 29 referências (vault, seções 9 e 10). Ele traz:
  - uma quarta hipótese, a H-TRANS (caos cedo, canalização depois);
  - a régua crua e a forma em U como condições das frases;
  - a expectativa da malha fechada;
  - dois descritivos: o estado interno e o efeito comum do tapa.

  As decisões A1-1 a A1-5 estão DECIDIDAS, todas pela recomendação.
- **A D-IND-I5b-1** (o dono separa os pets) está confirmada pelo Matheus.

## Resultado da etapa I7a (2026-11-10, Claude Code, Opus 5.5, branch `v3-individualidade-i7a`)

- **As medidas** (`digilab/metrics.py`, a seção do I7):
  - `distancias_ramo` (a D_b(d));
  - `razao_de_somas` (o Φ) e `soma_presente` (a régua crua);
  - `inclinacao_ou_none` (o γ e o β);
  - `folhas_estado` e `distancia_estado` (o estado interno, 12.5, PROPOSTA);
  - `efeito_comum` (o C_E) e `reencontrou`.

  Os testes, contra casos feitos à mão, estão em `tests/test_individualidade_i7.py`.
- **O orquestrador:** `experiments/run_v3_individualidade_i7.py`, com as configs `individualidade_i7.json` (a run) e
  `individualidade_i7_fumaca.json`.
  - **Os ramos:**
    - o N, o G, o A(t) e o E(t) vividos pelo laço do dono, com o embrulho do ramo (`DonoRamo`);
    - o E°(t), o log do I2 com o tapa inserido, rejogado.
  - **As conferências:** o G-I7-0 a 3 falham alto, e cada ramo é vivido duas vezes (IR-6).
  - **A análise:** o bootstrap sobre as sementes soma agregados por semente; a leitura segue a 7.2 com o adendo 1 (a H-TRANS, a régua
    crua e o U).
  - **A trava:** o cabeçalho APROVADO, a seção `## 13. O registro da análise`, as bases e o K do I2, os 14 dias, no máximo 4 processos
    e nada por cima de uma pasta.
- **A fumaça** (as sementes 101 e 202, K = 1, 14 dias, 12 pets, 4 processos, com a suíte inteira de outra sessão rodando ao lado):
  - todas as conferências passaram;
  - levou 12 min 20 s de parede, 62 s por pet com 4 processos e 244 s por pet dentro de cada processo;
  - uma pet sozinha, num processo, levou 93 s (cada ramo, vivido duas vezes, 5 s).
- **O custo passa do dobro da estimativa do plano** (45 s por pet e 1 h 10 min). A projeção para as 360 pets é de cerca de 6 h com 4
  processos. Pela seção 8 do plano, a IR-6 volta ao Matheus antes da run.
- **As leituras do plano** estão no registro: D-IND-I7a-1 a 8.
