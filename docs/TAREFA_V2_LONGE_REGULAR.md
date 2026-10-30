# TAREFA V2 — LONGE_REGULAR: o longe com lugares fixos, para separar a distância da falta de regularidade (2026-10-30)

Coordenador: Gerente (Claude Code). Worker: a definir. Worktree e branch: `v3-longe-regular-<etapa>` (V3-D2; a C1 da V3). Status: **ABERTA; as LR-1 a LR-7
DECIDIDAS pelo Matheus em 2026-10-30, todas pela recomendação** ("segue as recomendações", no chat do Gerente da V3), com as C1-E1 e
C1-E2 do `docs/PLANO_V3.md`, seção 2.3. Nenhum código e nenhuma vida ainda.

Categoria: experimento (com uma etapa de código no dono da pesquisa). Origem: Matheus, 2026-10-30: a recomendação R1 da análise que
cruzou a triagem de literatura com o estado do projeto (o arquivo `triagem_texto_completo/ANALISE_LACUNAS_E_ROADMAP.md`, fora do
repositório). O Matheus pediu a tarefa ("Sim, escrever a R1").

## 0. Os cinco pontos

| ponto | resposta |
|---|---|
| a capacidade | saber **por que** o modular falha no longe: pela distância, ou porque o longe da pesquisa não tem nada que se possa aprender |
| o marco que desbloqueia | a leitura do hábito (o P2). A `docs/PROPOSTA_LONGE_DIGIBRAIN_MODULAR.md` (seção 6) diz que consertar o longe primeiro "separa as duas explicações do hábito". Com a L-2 negativa, o longe não foi consertado |
| a evidência | um contraste registrado antes (o M-MEM no longe com lugares fixos) e uma leitura descritiva por faixa de distância |
| as dependências reais | o código da reavaliação e da L-2 na `main`; uma faixa de sementes nova. **Não depende do A** nem do motor |
| se o gate falhar | o resultado é registrado como está. Uma falha também informa: a memória não ajuda à distância nem com regularidade, e a causa fica na viagem ou na percepção (seção 1.3) |

## 1. Pergunta

**No longe, o M-MEM ajuda quando a ração volta sempre aos mesmos poucos lugares?** E, separando pela distância da ração na abertura,
quanto da queda do longe vem da distância e quanto da direção sorteada a cada ração?

### 1.1 Por que agora (os dados do projeto)

Da `docs/PROPOSTA_LONGE_DIGIBRAIN_MODULAR.md`, seção 1.1 (o M3\*, a reavaliação 66xxx, descritivo):

| a distância da ração mais próxima na abertura (d0) | comedouro: n, taxa por episódio | longe: n, taxa por episódio |
|---|---|---|
| na visão (até 6 células) | 1 565, 0,91 | 433, 0,84 |
| **só no cheiro (de 6 a 24 células)** | 1 736, **0,74** | 1 629, **0,41** |
| além do cheiro (mais de 24 células) | 12, 0,00 | 441, 0,21 |

**Na mesma faixa de distância, o lugar fixo fecha 0,74 e o lugar sorteado fecha 0,41.**

**Por que isso ainda não separa as causas:**
- os dois estilos também diferem nas rações por episódio (3,79 contra 7,81);
- e nas ofertas que mudam na janela (25 contra 280 episódios);
- o comedouro fica perto da casa, e o longe muda de direção a cada ração.

**Hoje, o M-MEM só pode ajudar onde a ração volta ao mesmo lugar.** O G-ABLA-MEM só se mede no comedouro (o plano do protótipo, seção
5.2), e no longe sorteado o lugar lembrado nunca tem a ração de volta: das 6 939 visitas, 6 932 saem vazias.

### 1.2 O que a literatura sugere

**Verificadas na C0** (`docs/referencias/v3c0_referencias_verificadas.csv`, #482), com as ressalvas de cada linha. Servem como
direção, não como tamanho de efeito.

- **Ho, Dautenhahn e Nehaniv:** CEC 2005 (`10.1109/cec.2005.1554734`); a tese de Ho, 2005, Univ. de Hertfordshire
  (`10.18745/th.14271`); AISB 2006 (UHRA eprint 12716, sem DOI); Connection Science 2008 (`10.1080/09540090801889469`). Agentes com
  glicose, umidade, energia e temperatura num mundo com estações.
  - A memória que refaz o caminho exato falha quando os recursos mudam de lugar.
  - A memória de eventos com regras do ambiente estende a vida.
  - A memória só supera o agente reativo quando guarda também os eventos negativos.
  - São 10 execuções por condição, sem teste de hipótese.
- **Giannakakis, Khajehabdollahi e Levina (ALIFE 2023, `10.1162/isal_a_00606`; a extensão em Artificial Life 2024,
  `10.1162/artl_a_00458`):** a plasticidade que a evolução escolhe só compensa quando o ambiente muda numa faixa
  intermediária; sem estrutura, aprender não paga.

### 1.3 O que cada resultado diria (escrito antes; a forma final vai no plano)

| se | a leitura |
|---|---|
| M3\* − M2 > 0 no longe com lugares fixos, e ≈ 0 no longe sorteado | a falha do longe é do cenário: não há o que lembrar. O hábito passa a ser lido também no longe com lugares fixos |
| M3\* − M2 ≈ 0 nos dois | a memória não ajuda à distância nem com regularidade. A causa fica na viagem e na decisão (as trocas de meta) ou na percepção (o cheiro, a L-1) |
| a taxa por episódio do longe com lugares fixos ≈ a do longe sorteado em todos os braços, na mesma faixa de d0 | a distância domina, e a regularidade não importa para o pet de hoje |

## 2. Depende de

- **A `main` com:**
  - o protótipo modular, a reavaliação e a L-2 (#432, #437, #438, #445, #454);
  - a proposta do próximo passo (#455).
- **A L-2 fechada como negativa:** a P-1, a LP-2 e a LP-3 do #455, pelo Matheus em 2026-10-30.
  - Esta tarefa usa a chave `intencao_suspensa` **desligada.**
  - A lição da LP-2 vale para as medidas daqui.
- **Uma faixa de sementes nova,** pedida ao coordenador (LR-5).
- **As decisões LR-1 a LR-7.**

## 3. Mudança mínima

### 3.1 O que muda (etapa 1, código)

- **`digilab/mundo.py`:** um estilo novo no `DonoComLugar`, **`longe_fixo`** (o nome é PROPOSTO), e a entrada dele em `ESTILOS_LUGAR`.
  - **Na construção:**
    - o dono sorteia uma vez os `n_pontos` lugares fixos da vida (LR-1), cada um a uma distância entre `longe_min_celulas` e
      `longe_max_celulas` **do comedouro** (LR-2), em direções distintas entre as 16;
    - a rng é própria: `derivar_semente("dono-lugar-fixo", semente, rotulo_dono)`. Assim, os outros três estilos não consomem nenhum
      sorteio novo.
  - **A cada `alimentar`:** a ração cai num dos pontos, por um sorteio uniforme na mesma rng. Fica no `lugares` como hoje, com o `pet`
    da hora.
- **`digilab/config.py`:** o `n_pontos_longe_fixo` (PROPOSTO, SEM FONTE) no `ConfigMundo`, com status e fonte.
- **A bancada:**
  - o `experiments/bancada/config.py` aceita o estilo novo pela validação que já existe;
  - o orquestrador da run é novo (`experiments/run_v2_longe_regular.py`, PROPOSTO) e reaproveita as medidas da avaliação da L-2.
- **Os testes:**
  - os pontos sorteados são os mesmos no replay;
  - toda ração do `longe_fixo` cai num dos pontos;
  - os pontos ficam na faixa de distância;
  - **os três estilos de hoje saem byte a byte** contra um gabarito gravado num commit próprio, antes da mudança.

### 3.2 O que NÃO muda

- `digilab/engine.py`, o motor, o mundo, o corpo e o cheiro.
- O cérebro modular, o A e as subchaves (`intencao_suspensa` fica desligada).
- Os estilos `comedouro`, `perto` e `longe`.
- **O jogo web: nada.**
  - O dono com lugar é da pesquisa; no jogo, quem põe a comida é o jogador.
  - A célula "longe do jogo" (a L-4 (b), a PL-4: "não agora") é **outra coisa**: é mais fácil por construção. Aqui a distância fica a
    mesma do longe da pesquisa, e só a regularidade muda.

## 4. Experimento e gate

- **O plano de análise:** um **adendo 6** ao `docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md` (LR-7), commitado antes da primeira
  vida. Ele reusa as medidas, a unidade (base, semente) e o IC do t da reavaliação e da L-2.
- **As células:** `longe_fixo` e `longe`, lado a lado, com os mesmos donos da reavaliação.
  - O comedouro e o perto **não** rodam: já têm dado e não respondem à pergunta.
- **Os braços (LR-4):** M0, M2 e M3\*, todos com a `intencao_suspensa` desligada.
- **A medida principal:** a taxa de fechamento **por episódio**, como manda a PL-3. A taxa por ração do longe não informa.
- **O contraste primário (LR-3), PROPOSTO:**
  - M3\* − M2, por episódio, **só nas células do `longe_fixo`**, com o IC95 do t sobre as unidades;
  - a previsão é > 0, e a margem sai do poder, com a variância da reavaliação.
- **Descritivo, sem gate:**
  - o mesmo contraste no `longe` sorteado;
  - as taxas por faixa de d0 (na visão, só no cheiro, além do cheiro) por estilo e por braço;
  - as visitas ao lugar lembrado que acham a ração;
  - as trocas de meta por vida;
  - **a fração do tempo com alguma variável do corpo fora da faixa** (a R5 da análise). Sai do replay, sem vida nova.
- **As medidas seguem a lição da LP-2:** a retomada de uma busca não conta como troca, e uma medida definida por um grupo que o próprio
  mecanismo cria não serve de contraste.
- **As sementes:** uma faixa nova (LR-5); a calibração não roda, porque nada se calibra aqui. A run roda uma vez.
- **A máquina:** no máximo 4 processos, como na reavaliação (#432).
- **GPU:** não.

## 5. Entrega

- **Etapa 0 (este documento):** a tarefa e as decisões LR-1 a LR-7 com o Matheus.
- **Etapa 1 (código):**
  - primeiro o gabarito dos três estilos, num commit próprio;
  - depois o estilo novo, os testes, o espelho do parâmetro em `config.py` e a suíte inteira.
- **Etapa 2 (plano):** o adendo 6, commitado antes da run.
- **Etapa 3 (run):** uma vez, com o `RESULTADO` numa seção do `docs/RESULTADO_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md` (ou num arquivo próprio,
  se o plano pedir).
- **Os testes:** `python -m pytest tests/ -q`. A web não muda, então não há `npm`.
- **O registro:** uma seção própria no fim de `docs/registro/AAAA-MM.md` e uma linha no fim do `docs/REGISTRO_DESVIOS.md`, por etapa.
- **Um PR por etapa,** contra a `main`, com o corpo no modelo `.github/pull_request_template.md`. O merge é só do Matheus.

## 6. Fora desta tarefa

- **Consertar o longe.** Esta tarefa só mede de onde vem a falha.
- **Mecanismos novos no cérebro:**
  - redecidir por evento (a R3 da análise);
  - o lugar lembrado pela consistência (a L-3);
  - o cheiro por fonte (a L-1).
- **A frente do hábito.** Ela usa o resultado daqui; o braço de crédito na intenção (a R2) fica na tarefa dela.
- **Os episódios negativos na memória** (a R4). Esse braço vai para a `docs/TAREFA_V2_MEMORIA_AUTOBIOGRAFICA.md`.
- **O A11, o M4 e as variantes M4-emb e M4-con.**
- **A célula "longe do jogo"** (a PL-4 segue "não agora").

## 7. Critérios de aceitação

- O gabarito dos estilos `comedouro`, `perto` e `longe` está gravado antes da mudança, e um teste confere que eles saem byte a byte.
- Um teste confere que toda ração do `longe_fixo` cai num dos `n_pontos` pontos, e que cada ponto fica na faixa de distância do
  comedouro.
- O replay de uma vida com o `longe_fixo` é bit a bit (o G1).
- O adendo 6 está na `main` antes da primeira vida, com o contraste primário, a margem e a regra de leitura da seção 1.3.
- Cada número do resultado sai de um artefato em disco com sha256.
- A faixa de sementes está na `FAIXAS_RESERVADAS` antes da run.

## 8. Decisões do Matheus

**Todas DECIDIDAS em 2026-10-30, pela recomendação** ("segue as recomendações"). O `n_pontos_longe_fixo` = 3 continua
SEM FONTE no `config.py`; a faixa 71101…71505 foi conferida livre (nem em `FAIXAS_RESERVADAS` nem em `FAIXAS_QUEIMADAS`, em nenhum
branch) e entra na tabela num commit próprio, na etapa 1.

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| **LR-1** | quantos lugares fixos por vida | **3,** sorteados uma vez na vida (PROPOSTO, SEM FONTE). É uma regularidade parcial: a memória tem o que aprender, mas não basta ir a um ponto só | 1 ponto: vira um "comedouro longe", e o ganho da memória pode vir só de nunca precisar escolher; muitos pontos: volta perto do sorteado |
| **LR-2** | a âncora da distância | **o comedouro** (a casa do pet), com a faixa de 20 a 30 células do longe de hoje. O d0 de cada episódio é medido e lido por faixa | ancorar no pet: o lugar deixa de ser fixo, e a pergunta se perde |
| **LR-3** | o contraste primário | **M3\* − M2 por episódio, só no `longe_fixo`,** com a previsão > 0; o resto descritivo | tudo descritivo: nada se decide com o resultado; vários primários: o Holm come o poder |
| **LR-4** | os braços | **M0, M2 e M3\*,** com a `intencao_suspensa` desligada | sem o M2: não há ablação da memória; com o M4 e o A11: mais vidas sem pergunta |
| **LR-5** | a faixa de sementes | **71101…71505,** se o coordenador confirmar que está livre (não está na `FAIXAS_RESERVADAS` de 2026-10-30) | reusar a 66xxx ou a 67xxx: a validação deixa de ser única |
| **LR-6** | a ordem | **antes da frente do hábito,** ou junto com o plano dela | o hábito depois, sem isto: a leitura do P2 fica no cenário confundido, que a proposta do longe quis evitar |
| **LR-7** | onde fica o plano | **um adendo 6 ao plano do protótipo,** que já tem os braços, as medidas e a unidade | um plano novo: repete a seção de medidas e pode divergir dela |

## Resultado da etapa 1 (código; 2026-10-30, worker Claude Code, Sonnet 5.5, worktree `v3-longe-regular-codigo`)

Só código e testes; nenhuma vida de pesquisa. Quatro commits, nesta ordem:

1. **A faixa 71101…71505** em `FAIXAS_RESERVADAS` (`experiments/bancada/faixas.py`), com a fonte (LR-5, PR #495). Conferida livre antes:
   nenhuma faixa nem config a usava.
2. **O gabarito dos estilos `comedouro`, `perto` e `longe`**, gravado antes da mudança: `tests/gabarito_lugar_estilos.py` gera
   `tests/gabaritos/lugar_estilos_antes.json` (36 vidas: instinto e lobos × 3 estilos × 2 donos × 3 sementes, com o log, o estado, as
   rngs, o estado da política e os lugares das rações), e `tests/test_gabarito_lugar_estilos.py` confere byte a byte.
3. **O estilo `longe_fixo`** (`digilab/mundo.py`, `digilab/config.py`):
   - `N_PONTOS_LONGE_FIXO = 3` em `digilab/config.py` (LR-1; PROPOSTO, SEM FONTE), parâmetro `n_pontos` do `DonoComLugar` (validado entre
     1 e 16). Fica **fora do `ConfigMundo`**: um campo novo no `asdict` quebrava 4 gabaritos do web mesmo com o estilo desligado;
   - o `DonoComLugar` sorteia na construção os pontos fixos com a rng própria `derivar_semente("dono-lugar-fixo", semente, rotulo_dono)`, e
     cada `alimentar` sorteia um ponto uniformemente na mesma rng; os outros estilos não criam nem consomem essa rng;
   - `ESTILOS_LUGAR` ganhou o `longe_fixo`; `ESTILOS_LUGAR_V2` guarda os três de antes para as runs que os iteram (o protótipo e a análise
     dos empates do cheiro); a bancada aceita o estilo pela validação que já existia (`ESTILOS_LUGAR`);
   - `tests/test_longe_fixo.py` (33 testes): pontos iguais no replay e numa construção nova; toda ração cai num ponto; os pontos ficam a 20 a
     30 células do comedouro, em direções distintas; o sorteio por ração é uniforme; o replay é bit a bit (o G1), inclusive pela bancada.
4. **Os documentos:** esta seção e o desvio em `docs/registro/2026-10.md`.

**O achado que muda a leitura (desvio 1 do registro):** o comedouro está na célula (10, 15) do mapa de 64 × 30. Sem corte do mapa, só
**5 das 16 direções** têm um ponto a 20 células (os índices 14, 15, 0, 1 e 2, o leste) e **3** a 30 células (15, 0 e 1). Os 3 pontos
saem dessas, então ficam todos a leste do comedouro; a distância mínima entre dois pontos é de cerca de 7,8 células (média de 17,9 em 2 000
sementes). O `longe` sorteado ancora no pet, usa as 16 direções e corta o ponto na borda. O adendo 6 precisa dizer isso; a LR-2 fica como
decidida e o ponto vai ao Matheus.

Os testes e a contagem da suíte inteira estão no corpo do PR.

## Resultado da etapa 3a (código; 2026-10-30, worker Claude Code, Sonnet 5.5, worktree `v3-longe-regular-orquestrador`)

**O que entrou** (nenhuma vida da faixa 71101…71505 rodou; nada no web nem no `digilab/engine.py`):
1. **As medidas da C5** em `digilab/metrics.py` (`viabilidade_do_corpo`, AD6-4): por tick, os cinco estados do corpo, "fora da faixa" abaixo
   de 0,15 (o `limiar_privacao` que já está no `config.py`: nenhum número novo), a fração dos ticks com ao menos uma variável fora e a
   menor necessidade (média e mínimo), na vida e nos dias 8 a 14. `tests/test_viabilidade_do_corpo.py` (5 testes, vidas pequenas à mão).
2. **O orquestrador** `experiments/run_v2_longe_regular.py` (commit próprio), com `experiments/configs/v2_longe_regular/` (`longe_regular.json`
   e `fumaca.json`):
   - as 8 células (4 donos × `longe_fixo` e `longe`), os braços M0, M2 e M3\* com a `intencao_suspensa` desligada, K = 150 (30 por base) nas
     bases 71101, 71202, 71303, 71404 e 71505, o prefixo `digibrain_prototipo`, 14 dias, orçamento 16: 3 600 vidas;
   - a trava: o adendo 6 APROVADO no cabeçalho, a faixa em `FAIXAS_RESERVADAS`, no máximo 4 processos, `SementeSemPlano` para outra base
     ou sementes fora da faixa e dos testes, falha alto para outro K, outros dias, outro orçamento, outro prefixo ou outro plano, e nada
     por cima de uma pasta que já existe;
   - por vida: o G1, o T-CENARIO-1, o G-MECANISMO, o crédito por opção, a conferência da LP-2 (nenhum `retomou` nem `n_susp`) e as
     medidas do conserto, da C5 e das trocas de meta;
   - o `resultado.json`: o primário (A6.4), as premissas, a classe de A6.6 e a leitura de A6.7, e o descritivo de A6.8 (faixas de d₀,
     visitas, trocas, C5 e os outros); o `meta.json` com o sha256 de cada artefato.
   - `tests/test_longe_regular.py` (39 testes): o desenho, a trava, a classe, a leitura, o motor que grava o corpo (a vida não muda),
     as trocas de meta e a fumaça de ponta a ponta.
3. **Os desvios** (5, sem número novo) em `docs/registro/2026-10.md`: em especial o 1, o "por tick do replay" lido como o estado no começo de
   cada tick, medido na vida e conferido pelo G1.

**A fumaça e o tempo estimado da run** (sementes dos testes 101 e 202, K = 2 por base, 14 dias, 96 vidas, 4 processos):
- 55 s de parede para as vidas (0,58 s por vida) e 2,22 s de CPU por vida (`longe_fixo` 2,20 e `longe` 2,24);
- **a run (3 600 vidas, 4 processos): cerca de 35 min de parede e 2,2 h de CPU**, dentro da estimativa de A6.9 (de 37 min a 1 h),
  um pouco abaixo; a análise sobre 3 600 vidas não foi medida em escala (a da fumaça leva segundos). O tempo real vai ao RESULTADO.

Os testes e a contagem da suíte inteira estão no corpo do PR.
