# TAREFA V2 — LONGE_REGULAR: o longe com lugares fixos, para separar a distância da falta de regularidade (2026-10-30)

Coordenador: Gerente (Claude Code). Worker: a definir. Worktree e branch: `v2-longe-regular`. Status: **ABERTA, só papel.** Nenhum
código e nenhuma vida. As decisões LR-1 a LR-7 (seção 8) estão abertas.

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

São pistas, não fontes: as referências abaixo foram **lidas na triagem de 2026-10-30, mas ainda não estão na lista verificada** do
projeto. Antes de qualquer citação, elas passam pela verificação Crossref da skill `literatura-digilab`. Até lá, valem como SEM FONTE.

- **Ho, Dautenhahn e Nehaniv (CEC 2005; AISB 2006; a tese de 2005, Univ. de Hertfordshire):** agentes com glicose, umidade, energia e
  temperatura num mundo com estações.
  - A memória que refaz o caminho exato falha quando os recursos mudam de lugar.
  - A memória de eventos com regras do ambiente estende a vida.
  - A memória só supera o agente reativo quando guarda também os eventos negativos.
  - São 10 execuções por condição, sem teste de hipótese.
- **Giannakakis et al. (ALIFE 2023):** a plasticidade que a evolução escolhe só compensa quando o ambiente muda numa faixa
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

## 8. Precisa do Matheus

Todas PROPOSTAS, com a recomendação primeiro.

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| **LR-1** | quantos lugares fixos por vida | **3,** sorteados uma vez na vida (PROPOSTO, SEM FONTE). É uma regularidade parcial: a memória tem o que aprender, mas não basta ir a um ponto só | 1 ponto: vira um "comedouro longe", e o ganho da memória pode vir só de nunca precisar escolher; muitos pontos: volta perto do sorteado |
| **LR-2** | a âncora da distância | **o comedouro** (a casa do pet), com a faixa de 20 a 30 células do longe de hoje. O d0 de cada episódio é medido e lido por faixa | ancorar no pet: o lugar deixa de ser fixo, e a pergunta se perde |
| **LR-3** | o contraste primário | **M3\* − M2 por episódio, só no `longe_fixo`,** com a previsão > 0; o resto descritivo | tudo descritivo: nada se decide com o resultado; vários primários: o Holm come o poder |
| **LR-4** | os braços | **M0, M2 e M3\*,** com a `intencao_suspensa` desligada | sem o M2: não há ablação da memória; com o M4 e o A11: mais vidas sem pergunta |
| **LR-5** | a faixa de sementes | **71101…71505,** se o coordenador confirmar que está livre (não está na `FAIXAS_RESERVADAS` de 2026-10-30) | reusar a 66xxx ou a 67xxx: a validação deixa de ser única |
| **LR-6** | a ordem | **antes da frente do hábito,** ou junto com o plano dela | o hábito depois, sem isto: a leitura do P2 fica no cenário confundido, que a proposta do longe quis evitar |
| **LR-7** | onde fica o plano | **um adendo 6 ao plano do protótipo,** que já tem os braços, as medidas e a unidade | um plano novo: repete a seção de medidas e pode divergir dela |
