# TAREFA V3 — PET_VIVO (2026-11-07)

Coordenador: o Gerente da V3 (Claude Code, Opus 5.5). Worker da etapa 0 (os planos da 0b e da 0c): Claude Code, Opus 5.5. Worktree e
branch: `v3-pet-vivo` (as etapas seguintes com sufixo, como `v3-pet-vivo-0b-codigo`). Status: **ABERTA; o plano da 0b e da 0c
APROVADO, e as PV-0-1 a PV-0-11 DECIDIDAS pela recomendação (2026-11-08, repassado pelo Gerente da V3; seção 8).** Nenhuma vida nova, nenhuma faixa.

Categoria: documentacao. Origem: Matheus, 2026-11-07: "Sim, a etapa 0", em resposta a "Aprovo a etapa 0 da PET_VIVO e despacho a
verificação e a auditoria?". A rodada está no vault DigiLab Research, `20 Temas/Pet vivo.md`, seção 5. A nota substitui o antigo
`rodada_pet_vivo.md` do PR #703, que foi fechado em 2026-11-08, porque os documentos de pesquisa ficam no vault (decisão do Matheus).

## 1. Pergunta

**O pet modular escolhe pelo que sente por dentro? Se não, a culpa é dos pesos, do número de alvos por comportamento ou de um sinal do
corpo fraco demais?**

- A pergunta vem do incômodo do Matheus: "não sinto que é um pet que está realmente pensando e agindo conforme os estímulos que ele tem
  dentro da rede neural dele" e "não representa ainda artificial life" (vault DigiLab Research, `20 Temas/Pet vivo.md`, seção 1; o levantamento em
  `DigiLab — Revisão de escopo/LEVANTAMENTO_CEREBRO_MODULAR_2026-11-07.md`, seção 4).
- Ela vem também da crítica às análises (vault DigiLab Research, `20 Temas/Pet vivo.md`, seção 4): o sorteio proporcional favorece quem tem mais
  unidades, e nenhum gate de hoje mede "age pelo estado". Todo gate de hoje é de forrageio.
- É a etapa 0 da rodada, só papel e vidas já gravadas:
  - **0a**, a verificação das referências da revisão I (vault DigiLab Research, `DigiLab — Revisão de escopo/REVISAO_I_PET_VIVO_2026-11-07.md`): é de
    outra sessão (`v3-pet-vivo-referencias`), na tabela `v3c5`, no PR #705;
  - **0b**, a auditoria da escolha: o plano está neste PR;
  - **0c**, a medida de "age pelo estado": o plano está neste PR.

## 2. Depende de

- **Na `main`:** nada além do que já está. A rodada, o levantamento e a revisão I estão no vault DigiLab Research, fora do repositório
  (o PR #703 foi fechado em 2026-11-08). Este PR os cita pelo caminho no vault, sem link.
- **Do Matheus:**
  - o APROVADO do `docs/PLANO_ANALISE_V3_PET_VIVO.md`;
  - as PV-0-1 a PV-0-11 (seção 8), antes do PR do código.
- **Da 0a:** a tabela `docs/referencias/v3c5_referencias_verificadas.csv`. Até ela existir, toda referência nova do plano fica marcada
  como "pista, a verificar". Nenhuma conta do plano depende dela.

## 3. Mudança mínima

**Esta etapa só escreve documentos:**
- esta tarefa;
- o plano `docs/PLANO_ANALISE_V3_PET_VIVO.md`;
- os desvios, numa seção no fim de `docs/registro/2026-11.md`, e o índice gerado.

**Não mudam:** o `engine.py`, o modular, o corpo, o mundo, a web, as medidas por vida de nenhuma run, os documentos do vault e os
arquivos da INDIVIDUALIDADE. A pasta `D:\Trab\digilab\v3-memoria-run` só é lida.

## 4. Experimento e gate (se houver run)

- **Plano de análise:** `docs/PLANO_ANALISE_V3_PET_VIVO.md`, PROPOSTO neste PR. É um descritivo pós hoc no molde da D-C1-3 (o adendo 11
  do `docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md`).
- **Sementes reservadas:** nenhuma. Não há vida nova: o replay refaz vidas já gravadas, a C4 (77101…77505) e a AN0 (as sementes dos
  testes).
- **Métrica e gate:** a 0b não tem gate, só uma regra de leitura escrita antes (o plano, seção 5). A 0c propõe uma medida para servir de
  gate nas runs da etapa 2, ao lado do forrageio (o plano, seção 7). Todos os números são PROPOSTOS.
- **GPU:** não.

## 5. Entrega

- **Testes:** não se aplicam nesta etapa, que só tem documentos. O PR do código (seção 7) terá os testes dele.
- **Registro:** os desvios D-PV0-1 a D-PV0-7, em `docs/registro/2026-11.md`.
- **PR** contra a `main`, com o relato no modelo. Merge só pelo Matheus.

## 6. Fora desta tarefa

- **Vidas novas:** nenhuma vida nova, nenhuma semente nova, nenhuma faixa.
- **Mecanismos:** nenhum (o PV-1 a PV-5, a normalização do sorteio, o corpo como modulador). Eles são da etapa 2, depois da escolha do
  Matheus na etapa 1.
- **O código do descritivo e das medidas:** fica para um PR seguinte, depois do APROVADO do plano.
- **A verificação das referências:** é a 0a, de outra sessão.
- **Números DECIDIDOS:** nenhum. Os cortes da regra de leitura e o Δ do contrafactual são PROPOSTOS e SEM FONTE.
- **A calibração dos pesos inatos:** a regra "calibração no fim" segue valendo. A auditoria pode apontar os pesos, mas não os muda.

## 7. Critérios de aceitação

- `docs/PLANO_ANALISE_V3_PET_VIVO.md` existe, com o status PROPOSTO e:
  - as vidas e as conferências que falham alto;
  - as medidas de cada decisão da 0b;
  - as três hipóteses e a regra de leitura, escritas antes;
  - a medida da 0c e como ela vira gate;
  - o que fica para o PR do código.
- As PV-0-1 a PV-0-11 estão na seção 8, cada uma com a recomendação e o custo de errar.
- Os links relativos dos documentos mudados resolvem: `python tools/verificar_relato.py --arquivo corpo.md --base origin/main` sai com 0
  falhas.
- `python tools/conferir_saude.py` passa.

## 8. Precisa do Matheus

**As PV-0-1 a PV-0-11 estão DECIDIDAS pela recomendação, em 2026-11-08.** O Matheus respondeu "Aprovo todas" à pergunta "Aprova o
plano do #704 e as PV-0-1 a PV-0-11 pela recomendação?". Depois de ler as decisões explicadas no vault (DigiLab Research,
`30 Decisões e protocolo/PET_VIVO — decisões PV-0.md`), ele respondeu "Continua valendo". As duas respostas foram dadas no chat do
Gerente da V3. O registro está nos dois comentários do PR #704 de 2026-11-08 (05:05 e 05:07 UTC). Eles foram escritos pela sessão do Gerente com a
conta `matheusmmmp`, sem app. **Esta sessão não ouviu o Matheus diretamente:** a confirmação dele vale no merge (a regra da memória das
aprovações repassadas da C4, 2026-11-01).

Cada decisão vem com a recomendação, que é a decidida, e o custo de errar. As seções citadas são as do plano.

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| **PV-0-1** | o lugar do plano | **um `docs/PLANO_ANALISE_V3_PET_VIVO.md` novo**, com a 0b e a 0c juntas. A PET_VIVO é uma frente nova da V3, e não uma frente herdada como a C4 | um adendo ao plano da V2 esconderia a rodada nova dentro de um arquivo de 4 000 linhas. Dois planos separados (0b e 0c) duplicariam a fonte e o replay, que são os mesmos |
| **PV-0-2** | as vidas | **a C4 (o REL e o SEM, nas 12 células: 4 800 vidas) e a AN0 (os gabaritos da LM0 e os `fins` da LM4)** (seção 2) | só a C4: tudo fica no código do `a287ba2`, de antes do jogo v17 a v19. Só a AN0: são cerca de 5 400 decisões, poucas para separar dono e lugar. Os outros braços da C4 (o REC, o EMB, o RELsN e o REL+F) somariam 9 600 vidas sem pergunta própria |
| **PV-0-3** | a fonte da C4 | **a pasta `D:\Trab\digilab\v3-memoria-run\...\memoria_autobio\run\`, só lida, com o sha256 de cada arquivo conferido contra o `meta.json`.** A cópia no git tem os mesmos sha256 e serve de reserva (D-PV0-1) | ler da pasta sem conferir: um arquivo trocado passaria. Ler só do git contraria o pedido do coordenador, mas dá o mesmo dado |
| **PV-0-4** | o código do replay | **o da C4 numa worktree destacada no `a287ba2`, como na D-C1-3; o da AN0 na `main` do PR do código, porque os gabaritos são de hoje** | com o código de hoje, a C4 refaria outra vida (9 módulos mudaram, A11.2). O G1 pegaria, mas o estágio 2 seria perdido |
| **PV-0-5** | o tamanho do contrafactual (com a regra do tempo: medido nas sementes dos testes no PR do código e declarado; acima de umas 8 h para as 960 vidas, uma subamostra menor antes da run) | **as medidas A-1 a A-3 nas 4 800 vidas; o contrafactual A-4 numa subamostra fixada antes: os k de 0 a 7 de cada base (40 unidades), nas 12 células e nos dois braços (960 vidas), mais a AN0** (seção 8) | todas as vidas no A-4: cerca de 22 refeitas por decisão em 6,5 milhões de decisões, um custo SEM MEDIDA que pode passar de um dia de máquina. Uma subamostra menor: o IC por célula fica largo demais para separar os donos |
| **PV-0-6** | o passo do contrafactual | **Δ = S/4 (256) para cima e para baixo na falta de cada receptor, com o corte em [0, S], e tudo o que sai dela refeito** (a urgência, o `g_exp`, o reflexo e o incentivo) (seção 4.4) | um Δ pequeno mede só a derivada local e pode dar ≈ 0 por arredondamento inteiro. Um Δ grande, como de 0 a S, mistura estados que o pet quase nunca vive |
| **PV-0-7** | a tabela do alívio (a coerência) | **empírica e fixada antes de medir: o canal de cada receptor no `r` das consequências de cada comportamento, nas mesmas vidas, e um alívio só conta com média > 0 e IC95 acima de 0** (seção 4.4) | uma tabela escrita à mão poria a opinião de quem escreve no lugar do corpo. A empírica mistura o contexto (come-se quando há comida), e isso fica escrito como limitação |
| **PV-0-8** | os cortes da regra de leitura | **os da seção 5: 0,10 na TV do número de alvos, 1,25 na inflação, 0,05 na sensibilidade, 1/2 na coerência e 1/3 na parte do corpo**, todos PROPOSTOS e SEM FONTE | os cortes fixados depois de ver os números convidam a escolher a hipótese. Cortes ruins dão uma leitura errada, mas registrada e conferível |
| **PV-0-9** | a medida da 0c | **a SE-C (a sensibilidade ao estado com a coerência) como candidata a gate, e a RV (a revalorização no ato, pela pista do Zhang et al. 2009) como parte dela, para a fome e a comida.** A informação mútua fica só como descritivo (seção 7) | só a SE, sem a coerência: um pet que corre para o lado errado quando tem fome contaria como "age pelo estado". Só a informação mútua: o contexto (a comida à vista) confunde o estado |
| **PV-0-10** | como a medida vira gate | **cada plano da etapa 2 põe um gate G-ESTADO (o braço do mecanismo ganha do controle na SE-C, com a margem tirada do σ da 0b) e uma guarda de forrageio (a taxa por episódio não pior que o controle, com margem). A margem só se decide nesse plano** (seção 7.4) | sem o G-ESTADO, cada mecanismo volta a ser medido só pela eficiência, e é isso que a rodada quer evitar. Sem a guarda, um mecanismo que deixa o pet mais "reativo" e com mais fome passaria |
| **PV-0-11** | a ligação com o I2 | **pelo plano, sem mexer nos arquivos da INDIVIDUALIDADE: a SE-C se calcula depois, por replay, nos logs do I2 (eles já são gravados, o plano dela, seção 5). O I2 fica como a linha de base do "antes" da individualidade, e a 0b como a do "antes" da SE-C** (seção 7.3) | mexer no orquestrador do I2 para gravar a SE-C atrasaria uma run já APROVADA e misturaria duas frentes. Sem nenhuma ligação, as duas linhas de base (individual e pelo estado) não se cruzam |

## Resultado da etapa 0, os planos da 0b e da 0c (2026-11-07, Claude Code, Opus 5.5, branch `v3-pet-vivo`)

- **Entregue:** esta tarefa e o `docs/PLANO_ANALISE_V3_PET_VIVO.md`, PROPOSTO, com as PV-0-1 a PV-0-11 com o Matheus.
- **Nenhuma vida, nenhum replay e nenhuma conta nova.** Os números citados no plano vêm de artefatos já no git, ou de fatos do código,
  com o arquivo.
- **Achado (D-PV0-1):** os artefatos da C4 também estão no git, com os mesmos sha256 da pasta de fora.
- **O ajuste de 2026-11-08 (D-PV0-6):** as citações do PR #703, fechado, passam para o vault DigiLab Research. O plano ganha
  três notas da nota `20 Temas/Pet vivo.md`: o reflexo, o Dulberg et al. 2023 e a posta por lugar. As PV-0 não mudaram.
- **A aprovação (2026-11-08):** o plano está APROVADO, e as PV-0 estão DECIDIDAS pela recomendação, por repasse do Gerente (D-PV0-7).
- **Próximo:** o merge pelo Matheus, depois o PR do código (o plano, seção 9), com o tempo do A-4 medido nas sementes dos testes.
  O replay só roda quando o Gerente liberar a vez da máquina. A fila é o I2, depois esta auditoria, depois a calibração da rodada 3
  da luta.

## Resultado da etapa do código da auditoria (2026-11-08, Claude Code, Opus 5.5, branch `v3-pet-vivo-codigo`)

O Matheus mandou seguir com as recomendações do cérebro ("E também já segue com as recomendações da parte do cérebro", 2026-11-08), por
repasse do Gerente da V3.

- **Entregue:** o código da seção 9 do plano.
  - **As contas da A-1 à A-4 e a SE-C,** no `digilab/metrics.py`, uma vez só.
  - **O script `experiments/auditoria_pet_vivo.py`,** com:
    - o replay da C4 no `a287ba2` e o da AN0 no código de hoje;
    - as conferências que falham alto;
    - o contrafactual pelo embrulho do `Impulso.unidades`, sem mudar o cérebro;
    - a regra de leitura da seção 5.
  - **Os testes:** `tests/test_metrics_pet_vivo.py` e `tests/test_auditoria_pet_vivo.py`.
- **O G1:** passa com e sem o contrafactual numa vida da AN0 (o gabarito) e numa vida da C4 (as medidas gravadas).
- **O tempo do A-4** (`artifacts_v3_pet_vivo/auditoria/tempo_a4.json`): a projeção da auditoria inteira fica entre cerca de 2,3 h e 2,9 h
  com 4 processos, abaixo do corte de umas 8 h. A subamostra não muda. O tempo de parede da máquina oscila (D-PV0C-9).
- **Os desvios:** D-PV0C-1 a D-PV0C-10.
- **Nenhum replay das 4 800 vidas.** Ele espera a vez da máquina, que o Gerente libera depois do I2.


## Etapa 1: o plano do PV-2 e as seis lacunas (2026-11-09, Claude Code, Opus 5.5, branch `v3-pet-vivo-pv2`)

**A origem:** duas decisões do Matheus em 2026-11-09, repassadas pelo Gerente da V3. Esta sessão não ouviu o Matheus diretamente.
- **A frente:** o PV-2 primeiro, a D-PV0R-7 ("Faça as recomendações").
- **As seis lacunas:** levadas ao plano ("Sim, leve ao plano").

**Entregue:** o [plano do PV-2](PLANO_ANALISE_V3_PET_VIVO_PV2.md), PROPOSTO. Ele traz:
- o mapa das seis lacunas: coberta, em parte ou depois;
- a quimiotaxia pelo dC/dt sobre o órgão do Olfato, com o placebo da hora certa e o braço separável do ganho pela fome;
- os gates, entre eles o G-ESTADO com o δ_E do σ da 0b e a guarda de forrageio;
- a lista ordenada das etapas seguintes;
- as decisões PV2-1 a PV2-10.

**O que não houve:** nenhuma vida, nenhuma faixa e nenhum código.

**Os desvios:** D-PV2P-1 a D-PV2P-4.

**Próximo (as PV2-1 a PV2-10 DECIDIDAS em 2026-11-09, D-PV2P-6):** o merge pelo Matheus. Depois, o PR do código, com o gabarito, a chave desligada e o custo medido nas sementes
dos testes.
