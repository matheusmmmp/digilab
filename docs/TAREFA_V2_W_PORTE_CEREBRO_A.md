# TAREFA V2 — W-PORTE: o cérebro A no jogo web, com o painel DigiBrain (2026-10-17)

Coordenador: esta sessão. Worker: a abrir, um por etapa. Worktree e branch: `v2-w-porte-cerebro-a` (o plano); cada etapa de código na
sua. Status: **ABERTA, só papel.** Nenhum código foi escrito para esta tarefa.

**Decisão que abre a tarefa (Matheus, 2026-10-17):** o porte do cérebro A para a web **sai da pausa**, e o jogo ganha o **painel
DigiBrain**: o pet na tela e, ao lado, a reação do cérebro a cada decisão (a referência visual é a imagem
`docs/estilo_up/referencias/digibrain_painel_referencia.webp`, o quadro da direita). A pausa vinha de 2026-10-07
(`docs/V2_RODADA_16.md`, seção 6: esperar o J5). **O J5 continua no Python**; o v11 não espera por ele.

**Esta tarefa substitui o `docs/PLANO_PORTE_V2_WEB.md` (PR #201, aberto desde 2026-10-07).** O #201 foi escrito antes de três
mudanças: a saída do elogio e da bronca (`docs/DECISAO_PRODUTO_SEM_ELOGIO_BRONCA.md`), o corpo químico portado para TS
(`web/app/motor/corpo.ts`) e o mundo físico portado para TS (`web/app/motor/mundo.ts`). O que o #201 tem de útil e continua valendo
(seção 0, as funções do bandit; seção 3, a paridade e a aritmética; D-W3, D-W4, D-W5 e D-W7) é citado aqui pela seção; a PW-8 decide o
destino dele.

## 1. Pergunta

Levar o DigiBrain escolhido (o A, M6) para o jogo, como pets v11, de forma que **o que o painel mostra seja o que o cérebro fez**: a
mesma decisão, os mesmos pesos e os mesmos motivos do Python, com paridade. É a etapa W do `docs/ROADMAP_V2.md`. Não é run de pesquisa.

## 2. Depende de

- **Na `main`, já:** `corpo.ts` (o corpo do Creatures 3, com paridade), `mundo.ts` (o mundo físico, com paridade), o cérebro A em
  `digilab/policies/lobos.py` com o motivo por lobo (`_pesos_efetivos`: `impulsos`, `decisao`, `memoria_emocao`, e os termos das
  chaves ligadas).
- **Decisões do Matheus:** PW-1 e PW-2 decididas em 2026-10-17 (seção 7); PW-3 a PW-8 abertas. As etapas 1 e 2 podem começar.
- **Prancha:** o painel não tem prancha em `docs/estilo_up/pranchas/` (hoje só o Mapa). A etapa 5 começa pelas duas pranchas
  (`DigiBrainDesktop.html` e `DigiBrain390.html`), no estilo de `docs/estilo_up/DIRETRIZES_REPLICAR.md`.

## 3. O que entra no v11 (a recomendação de PW-1)

| peça | no v11 | por quê |
|---|---|---|
| percepção, impulsos, decisão (L0) | **sim** | é o cérebro; desligado o aprendizado, é o instinto byte a byte (G2 da L0) |
| aprendizado pela **consequência no corpo** | **sim**, com o corpo de `corpo.ts` ligado nos v11 | é a decisão de produto (o pet aprende sozinho); a S-3 pedia drives que recompensem brincar e o contato, e o corpo já os tem (tédio, curiosidade, solidão) |
| carinho e tapa como gestos | **sim** | S-2, DECIDIDO (2026-10-07) |
| elogio e bronca | **não** | decisão de produto de 2026-10-07; os v1 a v10 seguem com os botões (S-1) |
| memória e emoção | **sim, como lobo**, contribuição de hoje (zero fora das frutas) | D-W7 do #201: a fala livre e a emoção leem a memória por espaços |
| mundo físico (mapa, alvo aprendido) | **não** no v11 | o J1 é negativo (o P1 perde do instinto) e o alvo aprendido atrapalha (#296); o mundo não tem tela. Vira v12 se o J1 virar |
| frutas, paladar, N5, N6, N7 | **não** | D-W6 do #201; o paladar não fechou a calibração (#316) |
| dois pets | **não** | J7 inconclusivo por premissa |
| planejamento (J5) | **não** | sem calibração nem validação; o rótulo "pensa" é risco registrado |

**O ponto do aprendiz (PW-2):** o worker da etapa 1 lê a calibração do corpo (`docs/RESULTADO_V2_CALIBRACAO_CORPO.md`) e a conjunta
(`docs/RESULTADO_V2_CALIBRACAO_CONJUNTA.md`, que escolheu o ganho 4 do P1 **sem fechar**) e propõe o ponto, com a ressalva escrita de
que nenhum dos dois foi validado no jogo. Nenhum número novo nasce na web.

## 4. O painel DigiBrain

Um quadro, à direita do Pet no desktop e numa aba ou gaveta no celular (pranchas da etapa 5). Só nos pets v11 (PW-7).

| parte | o que mostra | de onde vem (sem inventar) |
|---|---|---|
| **barras por lobo** | o quanto cada lobo pesou na **ação escolhida** na última decisão: impulsos (o instinto), decisão (o aprendido, w − w0), memória e emoção, e o corpo (as entradas do corpo, quando ligadas) | o motivo por lobo de `_pesos_efetivos`, normalizado pelo peso efetivo da ação escolhida; o aprendido pode ser negativo e a barra mostra o sinal |
| **percepção** | o que o pet leu: as duas ou três entradas de maior \|w·x\| na ação escolhida (por exemplo "fome alta", "tédio") | a percepção `x` e os pesos; **não é barra** (PW-5): a percepção não soma no peso efetivo |
| **estado atual** | a regra que disparou e a ação, em texto do jogo ("Com fome, foi comer") | a regra do lobo impulsos e a ação |
| **as outras opções** | os candidatos da decisão com a chance de cada um | as probabilidades P da política no momento da decisão |
| **últimas ações** | as decisões recentes, com a hora do jogo | o log de eventos (event sourcing: nada novo é salvo) |
| **"o que aprendeu"** | as ações que mais se afastaram do instinto desde o nascimento | o desvio dos pesos sobre o prior (a mesma base da vontade, PW-3, e do caráter, PW-4) |
| **"ao vivo"** | aceso só quando o motor está correndo; num replay, mostra "replay" | o estado do `Motor` |
| **o desenho do cérebro** | o mapa do cérebro do pet, com os lobos acendendo na decisão | a sessão do connectome (`docs/futuro/connectome_cerebro_a.md`, quando estiver na `main`); até lá, um ícone estático, nunca uma animação que finja atividade |

**Regras do painel:**
- Todo número do painel sai do motor por `useJogo()`. A tela não calcula nada que o Python não calcule; o que precisar de conta nova
  (a normalização das barras, a escolha das entradas da percepção) entra no motor TS e no Python, com gabarito.
- **Sem rótulo que prometa mais do que o cérebro faz.** Nada de "pensando" ou "sentindo" para o que é uma soma de pesos. Os nomes dos
  lobos são os do código, em português de tela.
- **A memória e a emoção** são um lobo só no A. Mostrar duas barras (como na imagem de referência) exige separar a emoção da web
  (a emoção por categoria dos pets v4+) e dizer de onde cada uma vem (PW-6).

## 5. Etapas de código, na ordem, com os gates

| etapa | o quê | onde | gate |
|---|---|---|---|
| 0 | o registro: este documento, a linha do painel e o destino do #201 | docs | o Matheus aprova PW-1 e PW-2 |
| 1 | **os gabaritos do Python, antes do TS:** um exportador que roda vidas do v11 (a configuração da seção 3) e grava decisões, pesos, motivos, P e assinatura | `experiments/exportar_gabarito_lobos.py`, `web/app/test/gabaritos/lobos_python.json` (o nome previsto em `docs/DEFINICOES_V2.md`) | o gabarito sai igual em duas execuções |
| 2 | **o núcleo em TS:** percepção, sonda do instinto, decisão em inteiros, sorteio igual ao `random.choices`, motivo | `web/app/motor/lobos.ts` | **G-PAR-L0:** com o aprendizado desligado, decisão a decisão igual ao instinto do TS e ao gabarito |
| 3 | **o aprendizado pela consequência do corpo** e os gestos (carinho, tapa) | `lobos.ts` sobre `corpo.ts` | **G-PAR-L1:** pesos e motivos iguais ao gabarito, bit a bit no Node |
| 4 | **o pet v11:** `VERSAO_PET` 11, o `Motor` usa os lobos e o corpo; a vontade (PW-3) e o caráter (PW-4) definidos primeiro no Python | `motor/constantes.ts`, `motor/motor.ts`, `carater.ts`, `vinculo.ts` | as assinaturas dos v1 a v10 não mudam (`npm test`); `constantes.test.mjs` confere as constantes novas |
| 5 | **o painel DigiBrain:** pranchas primeiro, depois o componente | `docs/estilo_up/pranchas/`, `web/app/src/componentes/DigiBrain.tsx` | `npm run tipos`, `npm test` e um e2e com captura de tela no desktop e em 390 px |
| 6 | a fala e a voz do v11: o que a LLM lê do cérebro (o motivo no lugar do θ do bandit) | `src/falaLivre.ts` | o prompt novo gravado com versão; o modo livre gravado continua no log |

Cada etapa é um PR, com o relato no corpo. O merge é só do Matheus.

## 6. Riscos

| risco | o que se sabe | o que fazer |
|---|---|---|
| o pet do v11 aprende a ficar parado | o N3 no `padrao` ensinou a evitar brincar e explorar (S-3); o corpo tem os drives que corrigem isso, mas a validação do corpo não rodou | na etapa 1, medir no Python a distribuição de ações do v11 numa vida longa contra o instinto; se brincar e explorar caírem, a PW-1 volta ao Matheus antes da etapa 4 |
| o instinto decide quase tudo | na L1 o instinto decidiu ~80% (G4); o painel vai mostrar a barra do impulso quase sempre cheia | é o comportamento real; o painel não esconde. O "o que aprendeu" é onde a diferença aparece |
| a paridade no navegador | o Chrome difere do Node no último bit de `exp` e `log` | o núcleo dos lobos é inteiro; nenhum `Math.exp`/`log` no núcleo (seção 3.2 do #201) |
| o tamanho do save e do replay | o v11 refaz a vida pelo log, com o corpo por baixo a cada tick | medir na etapa 4 o tempo de replay de uma vida longa no celular |
| a forma adulta muda | o caráter vem do desvio da política; o A pode desviar diferente do bandit | PW-4: medir antes, como pedia o D-W5 |

## 7. Decisões do Matheus

**DECIDIDAS: PW-1 e PW-2 em 2026-10-17, PW-3 a PW-8 em 2026-10-18, todas como recomendado** (a coluna "recomendação" é o que vale).

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| PW-1 | o que entra no v11 | **DECIDIDO (Matheus, 2026-10-17): como recomendado.** O da seção 3: núcleo, consequência no corpo, carinho e tapa; sem mundo físico, frutas, dois pets e planejamento | levar mais: cada peça traz uma validação negativa ou aberta para dentro do jogo, e corrigir pede um v12 |
| PW-2 | o ponto do aprendiz | **DECIDIDO (Matheus, 2026-10-17): como recomendado.** O worker da etapa 1 propõe a partir da calibração do corpo e da conjunta, com a ressalva de que nada foi validado no jogo | um ponto sem base: deriva até o teto e um pet que muda demais ou nada |
| PW-3 | a vontade com o A | **DECIDIDO (Matheus, 2026-10-18): como recomendado.** definir no Python primeiro (o D-W4 do #201: a ação de maior desvio aprendido sobre o prior, com a margem de hoje) | sem vontade, o vínculo B e a tela do desejo mudam; definir só na web perde a paridade |
| PW-4 | a escala do caráter no v11 | **DECIDIDO (Matheus, 2026-10-18): como recomendado.** medir primeiro; manter se as linhas e formas ficarem perto das do v10. **Depois da medida (seção 12, não ficou perto): DECIDIDO (Matheus, 2026-10-18), opção (b):** "uma escala própria do v11 (~0,015) com o deslocamento remedido antes de ligar" (seção 15) | formas concentradas, e o equilíbrio do combate sai do lugar |
| PW-5 | a percepção no painel | **DECIDIDO (Matheus, 2026-10-18): como recomendado.** lista das entradas que mais pesaram, **não barra** | uma barra de percepção não corresponde a nenhuma conta do cérebro |
| PW-6 | memória e emoção no painel | **DECIDIDO (Matheus, 2026-10-18): como recomendado.** uma barra (o lobo do A) e a emoção de hoje do pet como selo à parte, com a fonte | duas barras sem fonte separada: uma delas seria inventada |
| PW-7 | o painel nos pets v1 a v10 | **DECIDIDO (Matheus, 2026-10-18): como recomendado.** **não**: só v11. Os antigos têm o bandit, e um painel para eles seria outro desenho | mostrar o bandit com os nomes dos lobos mistura dois cérebros na mesma tela |
| PW-8 | o PR #201 | **DECIDIDO (Matheus, 2026-10-18): como recomendado.** fechar como substituído por esta tarefa, com um comentário apontando para cá | deixá-lo aberto: dois planos do mesmo porte, com recomendações opostas na consequência |

## 8. Fora desta tarefa

- O J5 e o lobo `planejamento` no jogo.
- O mundo físico com tela, as frutas, o paladar e os dois pets (cada um vira uma versão de pet própria quando a pesquisa fechar).
- Qualquer aumento de escala do cérebro (mais pesos, mais neurônios). O teto de pesos tem desenho próprio
  (`docs/DECISAO_V2_TETO_PESOS.md`).
- Mudar os pets v1 a v10, as assinaturas ou os gabaritos que existem.

## 9. Etapa 1, entregue (2026-10-17)

- **O ponto (PW-2):** é o da calibração do corpo, sem número novo (`docs/registro/2026-10.md`, 2026-10-17). Nada foi validado.
- **O gabarito:** `python experiments/exportar_gabarito_lobos.py` grava `web/app/test/gabaritos/lobos_python.json` (2 MB).
  - Duas vidas L0, sem aprender e sem corpo, e quatro vidas v11, uma por dono, com 3 dias e 288 decisões cada.
  - Cada vida traz o log, os motivos de cada decisão, os pesos, os pesos do corpo, o aprendizado e o sha256 do estado interno.
  - O arquivo sai igual em duas execuções.
  - `tests/test_gabarito_lobos_web.py` confere que ele está em dia e que é o v11: sem elogio nem bronca, com carinho, tapa e consequência, e o cérebro aprendendo.
- **O risco S-3** (`python experiments/medir_v11_parado.py`, artefato `artifacts_v2_w_porte/medida_parado.json`):
  - 20 pares (4 donos × as 5 sementes dos testes), com 14 dias e orçamento 224;
  - compara o v11 (P1-c-tapa) com o instinto no mesmo corpo (P0-c-tapa);
  - a medida é a fração de cada ação no tempo livre.

  | ação | instinto | v11 | diferença média [mín; máx] | pares com o v11 abaixo |
  |---|---|---|---|---|
  | ocioso | 0,266 | 0,169 | −0,097 [−0,241; +0,211] | 13/20 |
  | explorar | 0,290 | 0,416 | +0,126 [−0,038; +0,349] | 2/20 |
  | brincar | 0,348 | 0,352 | +0,004 [−0,299; +0,353] | 11/20 |
  | chamar | 0,096 | 0,062 | −0,034 [−0,130; +0,380] | 16/20 |

  - **Leitura descritiva:** na média, o v11 **não** fica mais parado. O ocioso cai, o explorar sobe e o brincar fica igual. O último terço da vida vai no mesmo sentido.
  - **A dispersão entre pets é grande:** em alguns pares, o brincar cai 0,3; em outros, sobe 0,35.
  - **Pela regra da seção 6, a PW-1 não volta ao Matheus.** A dispersão fica registrada para a PW-4 (o caráter) e para o painel ("o que aprendeu").
- **O corpo do ponto em TS (2026-10-18):** o metabolismo foi portado para o `corpo.ts` (a etapa 4 da `TAREFA_V2_METABOLISMO`, seção 10), com o corpo do ponto do v11 como constante (`CCO_V11`) e paridade bit a bit; o laço do corpo das vidas v11 em TS fica para a etapa 4, que precisa do `Motor` com o corpo por tick e da sujeira da rng do Python.

## 10. Etapa 2, entregue (2026-10-17)

- **O núcleo em TS:** `web/app/motor/lobos.ts`, o porte de `digilab/policies/lobos.py` com o aprendizado desligado (L0), sem as chaves
  do mundo, das frutas, do corpo e do plano.
  - a percepção (`percepcao`), a sonda do instinto (`impulsos`, sobre `agirInstinto`, o `PoliticaInstinto.agir` com a regra), a tabela
    de pesos inteiros no prior (`tabelaPrior`, S = 2^10), o peso efetivo (`ativacao`), o sorteio do `random.choices` (`sortear`) e o
    motivo com os campos de `_registrar` (`CerebroA.agir`, `motivos`);
  - com o aprendizado ligado, `CerebroA` falha alto: é a etapa 3. Os contadores da memória e emoção também ficam para a etapa 3; aqui o
    lobo só contribui com zero, como no Python;
  - nenhum `Math.exp` ou `Math.log` no núcleo (o teste lê o fonte);
  - a constante nova `CLB` (`bits`, `escalaTdc`, `maxPesos`) é conferida por `constantes.test.mjs` contra a `ConfigLobos`.
- **G-PAR-L0, passa** (`web/app/test/lobos.test.ts`, no Node):
  - as duas vidas da seção `l0` do gabarito, 576 decisões, passam pelas sete regras do instinto;
  - em cada decisão, a regra, os candidatos, as contribuições por lobo, os pesos efetivos, o `u`, a ação e o lobo decisivo são iguais
    ao gabarito, bit a bit (`toStrictEqual`, que compara os números por `Object.is`). A rng é chamada uma vez só nas regras com mais de
    um candidato;
  - a decisão é a do instinto do TS: o suporte de `distInstinto` (`bandit.ts`) é o dos candidatos, peso / total é a probabilidade dele
    bit a bit, e o instinto com o mesmo `u` escolhe a mesma ação, com os mesmos pesos;
  - a observação de cada decisão é refeita da percepção gravada, e a percepção refeita é conferida contra a gravada antes do resto;
  - os controles negativos: um peso mexido no último bit é pego, e também o mesmo erro nos pesos do instinto.
- **Leitura de "igual ao instinto do TS":** o TS tinha só `distInstinto`, que dá a distribuição e não a regra. A sonda precisa da regra e
  da ordem dos candidatos, então `agirInstinto` espelha o `PoliticaInstinto.agir` linha a linha, e o teste amarra os dois instintos do TS
  (no gabarito e numa grade de 13.824 observações). Nenhum número novo.
- **O que não foi conferido:** o `sha_interno` (é o `estado_interno` inteiro, com os contadores da memória, que ficam para a etapa 3) e
  a seção `v11` do gabarito (aprendizado e corpo, G-PAR-L1, etapa 3).
- `npm run tipos` limpo; `npm test` com 33 arquivos e 370 testes passando (13 deles no `lobos.test.ts`).

## 11. PW-4: a medida do caráter, registrada antes de medir (2026-10-18, worker B)

Pedido do Gerente: medir a escala do caráter no v11 contra o v10 (linhas e formas) e não mudar nada se ficar perto. Esta seção fixa a
medida e o critério de "perto" **antes** da primeira vida. É uma medida descritiva com as sementes dos testes, sem run de pesquisa.

- **Os pets:** 4 donos (atencioso, relapso, aleatório, incoerente) × 5 sementes (101…505), 20 por versão, 2 dias com 16 interações por dia.
  - **o v10:** o bandit do Python (`PoliticaBandit`, o algoritmo do bandit da web) com os donos de sempre, com elogio e bronca
    (`simular_vida`);
  - **o v11:** a vida do gabarito da etapa 1 (`P1-c-tapa` no ponto da PW-2: o corpo, o carinho, o tapa e a consequência).
- **O caráter, pelo método da web** (`carater.ts`, `caraterPolitica`):
  - o desvio da política sobre a mesma política recém-nascida (no A, o instinto), em 32 sondas × 100 amostras com a semente 9001;
  - o eixo é a média dos traços, ÷ 0,05, mais o `DESLOC_CARATER` da web do estágio, cortado em [−1, 1];
  - é medido no fim da criança (900 min) e no fim do adolescente (1980 min);
  - no A, as sondas ganham os receptores do corpo pela rng `sonda-corpo` da mesma semente, como a deriva da bancada.
- **A linha e a forma:** `linha_do_adolescente` e `forma_adulta` do catálogo (com o sparring suficiente).
- **O que se mede:**
  - a distribuição das 4 linhas e das 8 formas adultas;
  - o desvio bruto por eixo (a mediana de |bruto|) e a fração de eixos cortados em ±1.
- **"Perto" são as três condições juntas:**
  - **(a) as linhas:** a distância de variação total entre o v11 e o v10 fica dentro do 95º percentil da mesma distância com os rótulos
    de versão permutados entre os 40 pets (10.000 permutações, rng `pw4-permutacao`);
  - **(b) as formas:** o mesmo;
  - **(c) a escala:** a razão das medianas de |bruto| (v11 / v10, os dois estágios juntos) fica em [½, 2], e a fração de eixos cortados do
    v11 fica no máximo 0,10 acima da do v10.
- **A decisão:** se as três passam, nada muda (`CCP.escala` e `DESLOC_CARATER` ficam). Se alguma falha, o resultado é registrado e vai ao
  Matheus, sem mudar nada aqui.
- **Os limites conhecidos:**
  - são 20 pets por versão, então o teste por permutação tem pouco poder;
  - a web do v10 usa o bandit da web (outra rng, com o temperamento), e o `DESLOC_CARATER` foi calibrado nele; aqui o lado do v10 é o
    mesmo algoritmo no Python.

## 12. PW-3 e PW-4, entregues no Python (2026-10-18, worker B)

### PW-3, a vontade com o A

A definição é a do D-W4 do #201, sem número novo:
- **`PoliticaLobos.desvio_aprendido(obs)`:** para cada ação que o instinto propõe no tempo livre, o desvio aprendido sobre o prior.
  - É a contribuição do lobo de decisão no peso efetivo: `ativacao(w − w0, x)` mais, com o corpo, o mesmo nas entradas novas.
  - Usa a mesma conta e a mesma ordem de soma do `_pesos_efetivos`.
  - É pura: não muda peso, motivo, registro, memória nem rng.
  - Fora do v11 (mundo físico, frutas, entradas sociais, pedido, plano), falha alto.
- **`desejo.desejo_lobos(obs, cerebro, tick)`:**
  - a necessidade de sempre vem primeiro;
  - sem ela, a vontade é a ação de maior desvio, se a margem para a segunda for ≥ `limiar_vontade` (0,1, a de hoje);
  - o desempate é o do bandit (a primeira de `ACOES_PET_HOJE`), e a intensidade é min(1, margem);
  - o recém-nascido, e o cérebro sem aprender, não têm vontade.
  - O `desejo_de` de sempre não muda.
- **O gabarito da web:** `lobos_python.json` ganhou a seção `vontade`. As seções `l0` e `v11` saem iguais (conferido), e o teste do TS da
  etapa 2 passa.
  - **por decisão:** em cada decisão das 4 vidas do v11, o desejo e o desvio de cada ação, antes de o cérebro decidir. Saem do replay do
    log com um espião que só lê, e o replay é conferido contra o sha do estado interno;
  - **a grade:** 32 sondas com os receptores do corpo, contra o cérebro do fim de cada vida.
  - Nas 288 decisões de cada vida, a vontade aparece em 139 (atencioso), 207 (relapso), 174 (aleatório) e 220 (incoerente), e a necessidade
    em 17, 28, 94 e 18. A vontade do fim da vida é `ocioso` no atencioso e no incoerente e `explorar` no relapso e no aleatório.
- **Testes:** `tests/test_vontade_lobos.py`, 9.
- **Para a etapa 4 (o A, em TS):** o motor dos v11 chama a vontade do cérebro no lugar do `Bandit.desejo`, com a mesma conta, e confere
  contra a seção `vontade` do gabarito.

### PW-4, a escala do caráter

Pela medida e pelo critério da seção 11 (`python experiments/medir_carater_v11.py` → `artifacts_v2_w_porte/carater_v11.json`; 20 pets por
versão), **o v11 não fica "perto" do v10.** As linhas e as formas ficam; a escala não.

| | v10 (bandit) | v11 (A) | o critério |
|---|---|---|---|
| linhas: brigão, guardião, caçador, colosso | 0,10, 0,45, 0,20, 0,25 | 0,10, 0,60, 0,10, 0,20 | TVD 0,15, contra o 95º percentil nulo 0,35 (p 0,82): **passa** |
| formas adultas | muralha 0,35; emboscador e vigia 0,15; espelho e titã 0,10; as outras 0,05 | espelho e muralha 0,30; vigia 0,15; emboscador 0,10; duelista, furioso e titã 0,05; sentinela 0 | TVD 0,20, contra 0,45 (p 0,94): **passa** |
| a mediana de \|bruto\| por eixo | 0,0092 | 0,0027 | a razão é 0,30, fora de [½, 2]: **falha** |
| eixos cortados em ±1 | 0,006 | 0 | passa |

**A leitura:**
- **O A desvia do instinto cerca de um terço do que o bandit desvia do bandit recém-nascido**, nas mesmas sondas, no fim da criança e do
  adolescente.
  - Com a escala 0,05, o desvio dele vira um caráter de poucos centésimos.
  - Quem decide a linha passa a ser quase só o `DESLOC_CARATER` (o deslocamento fixo por estágio da web).
- **Com o desvio zerado,** a linha seria guardião e a forma seria a do deslocamento:
  - no v11, 60% das linhas e 50% das formas saem iguais a essas;
  - no v10, 45% e 40%.
  - Isto é só descritivo, fora do critério.
- **As linhas e as formas ficam perto** porque o deslocamento domina nos dois, não porque o caráter do A meça o mesmo que o do bandit.

**Os limites:**
- são 20 pets por versão, e o teste por permutação tem pouco poder;
- o lado do v10 é o bandit do Python, e o `DESLOC_CARATER` foi calibrado no bandit da web;
- as vidas têm 2 dias, só até o adulto;
- os dois lados têm 100% de ramo arisco (os donos simulados não atendem o bebê, um defeito conhecido).

**Nada mudou.** A decisão volta ao Matheus (PW-4); o pedido está no corpo do PR.

## 13. Etapa 3, entregue (2026-10-18)

- **O aprendizado em TS:** `web/app/motor/lobos.ts`, sobre o núcleo da etapa 2.
  - A aritmética inteira: `arred`, a regra da L1 com o teto (`atualizarPesos`) e o piso no peso efetivo. Os produtos têm de caber nos inteiros exatos do double, senão falha alto.
  - O crédito da consequência: `sinalHomeostatico` (o N3 da transição, conferido), `observarConsequencia`, `consequenciaCorpo` e o `sinal_corpo` sobre os receptores, com os canais ligados (`sinalCorpoCanais`, a soma telescópica e o contrato K-6).
  - As entradas do corpo: os receptores novos (tédio, solidão, estresse, dor e susto) numa tabela à parte, só no tempo livre, com prior 0.
  - Os gestos: o carinho por `mudancaNoCorpo` e o tapa por `receberAcaoDono`, com `recompensa_tapa`.
  - A `MemoriaEmocao` (os contadores), os canais e o `estadoInterno`.
  - O braço `P1-c-tapa` é a `BracoConsequencia`: o sinal da própria ação em `observar`; do dono, só o tapa chega ao cérebro.
  - A constante nova `CLB_V11` (o ponto do v11) é conferida por `constantes.test.mjs` contra a `config_v11` do gabarito. A lista `experimento` do teste agora filtra as raízes que só o TS tem, como já fazia a `pares`.
- **G-PAR-L1, passa** (`web/app/test/lobos_v11.test.ts`, no Node). Nas quatro vidas da seção `v11`, 1.152 decisões:
  - decisão a decisão, o motivo inteiro é o do Python, bit a bit (`toStrictEqual`): regra, candidatos, percepção e percepção do corpo, contribuições, pesos efetivos, `u`, ação, lobo decisivo, `aprendido`, `aprendido_corpo` e `sinal_corpo`;
  - no fim, batem os `pesos`, o prior, os `pesos_corpo`, o `aprendizado`, a `memoria_emocao`, os `canais` e o `corpo`;
  - a cobertura: 516 créditos de peso, 72 carinhos e 44 tapas creditados, o piso ativo em 344 candidatos e sete regras. O teto de 16 S nunca é atingido nas vidas; o corte fica coberto pelo teste de unidade;
  - os controles negativos: um receptor mexido em 1 num gancho e o tapa com outra recompensa são pegos.
- **O desvio (registro de 2026-10-18):** o corpo do v11 tem o **metabolismo**, que o `corpo.ts` ainda não tem. O laço do motor com o corpo não roda em TS. Por isso o gate rejoga os **ganchos** que o motor do Python fez ao cérebro, gravados pelo exportador num replay do log e conferidos contra a vida, e não o log com o motor.
- **O gabarito** ganhou os `ganchos`, a `memoria_emocao`, os `canais` e a `config_v11` (as configs que as vidas usaram de fato). As chaves de antes não mudaram. O `tests/test_gabarito_lobos_web.py` confere os ganchos. O cérebro do Python não mudou.
- **Para a etapa 4:** o `Motor` do v11 precisa do laço do corpo, e o corpo do ponto tem o metabolismo. Há dois caminhos: portar o metabolismo antes (a etapa 4 do metabolismo), ou mudar o ponto do v11 para o corpo sem ele, o que muda o gabarito e o PW-2. A decisão é do Matheus.
- `npm run tipos` limpo; `npm test` com 34 arquivos e 387 testes passando (17 deles no `lobos_v11.test.ts`); `tests/test_gabarito_lobos_web.py` passa.

## 14. Etapa 4, parte 1, entregue (2026-10-18): o laço do corpo em TS e o gate do laço

A etapa 4 vai em três PRs, na ordem do pedido: (1) o laço do corpo e a rng, com o gate; (2) a vontade e o caráter no Python, que já
estão no PR #329 (PW-3 e PW-4); (3) o v11 no `Motor`. Este é o primeiro.

- **O laço:** `web/app/motor/motor_corpo.ts` (`MotorCorpo`), o porte do `_laco`, do `_decidir`, do `_aplicar_acao_usuario` e do
  `_gesto` de `digilab/motor_corpo.py`. O motor portado é o do v11 do Python: `com_corpo(MotorComFeedback)` no mundo `padrao`.
  - Ele roda sobre o `corpo.ts` (o metabolismo, #333) e o `lobos.ts` (o aprendizado, #327), com o `avancarTick`, o `aplicarAcaoDono` e o
    `efeitoAcaoPet` de `estado.ts` para o que não é drive.
  - O G-BYPASS do Python também foi portado: um drive mudado por fora do corpo falha alto.
  - O `aplicarEvento` é o passo do replay, e o `estadoDict` é o `motor.estado()` do Python.
  - As ações do dono são alimentar, limpar, brincar, carinho e tapa. O elogio e a bronca falham alto.
- **A rng:** o `RandomPy` do `mundo.ts` (o MT do CPython), reusado nas duas rng do `engine.Motor`. Nenhum número novo.
- **O gate do laço** (`web/app/test/laco_v11.test.ts`, no Node): as 4 vidas da seção `v11` rodam pelo laço, evento a evento do log.
  - Os 3.648 ganchos que o laço faz ao cérebro são os do Python, bit a bit (`toStrictEqual`). Eles incluem a observação com os receptores,
    a transição, o ocorrido do corpo, a ação do dono com o tick e o antes e depois do carinho.
  - Batem também os 1.152 motivos e, no fim, os pesos, o prior, os pesos do corpo, o aprendizado, a memória e emoção e os canais.
  - O `motor.estado()` do fim bate inteiro: os drives, a sujeira, o sono, os cuidados, a ação atual e o corpo (a química, a digestão, o
    estágio, a janela do tédio e o metabolismo). As ações do pet batem com o tick.
  - O mesmo log dá a mesma vida duas vezes.
  - Os controles negativos: outra semente do motor muda os ganchos, e um limpar trocado por alimentar muda o fim.
- **O gabarito novo:** `web/app/test/gabaritos/lobos_laco_python.json`, do mesmo exportador, com o fim de cada vida do v11. O
  `lobos_python.json` não mudou. O `tests/test_gabarito_lobos_web.py` confere que os dois estão em dia.
- **O achado do #333:** o `configCorpo` falha alto com `banheiro: true`.
- **O replay de uma vida longa** (risco da seção 6; `web/app/test/medir_replay_v11.mjs`, artefato
  `artifacts_v2_w_porte/replay_v11.json`):
  - a vida tem 60 dias e 6.719 eventos, com 294 KB de log em JSON;
  - o replay leva 217 ms (a mediana de 5), 3,6 ms por dia, no Node 24 de um i7-14700KF;
  - é só descritivo; o tempo no celular fica para o e2e da etapa 5.
- **Para a parte 3 (o v11 no `Motor`):** ela espera o merge do #329 (o gabarito da vontade) e a decisão da PW-4. O #329 mediu e achou
  que a escala do caráter não fica perto da do v10, e recomenda a (b), uma escala própria do v11. A semente do pet do jogo e o tick de
  nascimento (`TICK_INICIAL`) entram no laço como parâmetros: o laço já aceita um estado de nascimento.
- `npm run tipos` limpo; `npm test` com 36 arquivos e 426 testes (9 deles no `laco_v11.test.ts`); `tests/test_gabarito_lobos_web.py`
  passa (3).

## 15. Etapa 4, parte 3: a escala e o deslocamento próprios do v11, registrados antes de medir (2026-10-18)

Pela PW-4 (b). Esta seção fixa o método e o critério **antes** da primeira vida. Só as sementes dos testes (os 20 pets da seção 11: 4 donos ×
101…505, 2 dias, 16 interações por dia); sem run de pesquisa. Os números saem PROPOSTOS.

- **A escala do v11:** `CCP.escala` × a razão das medianas de |bruto| (v11 / v10) de `artifacts_v2_w_porte/carater_v11.json`, arredondada a
  três casas (≈ 0,015).
- **O deslocamento do v11, pelo método de 2026-09-25** (`docs/registro/2026-09.md`), com a escala nova e o bruto dos pets v11:
  - **adolescente:** um deslocamento por eixo que leve as 4 linhas para perto de 25%;
  - **adulto:** em cada linha, menos a mediana do eixo complementar dos pets daquela linha (as formas perto de 50/50).
- **O critério, as três juntas:**
  - cada linha entre 15% e 35% dos 20 pets;
  - a forma de cima (sinal positivo do complementar) entre 35% e 65% dos pets;
  - a razão das medianas de |bruto| / escala (v11 com a escala nova, v10 com 0,05) em [½, 2], e a fração de eixos cortados do v11 no
    máximo 0,10 acima da do v10.
- **Se fechar,** os números entram no TS como `CCP_V11` e `DESLOC_CARATER_V11`, só nos pets v11. **Se não fechar,** vão ao Matheus sem ligar.
- **Limite conhecido:** a calibração e a conferência usam os mesmos 20 pets (não há sementes de teste de sobra); a conferência é otimista.

### A medida e o porte, entregues (2026-10-18): o PR da parte 3a

A parte 3 ficou em dois PRs. Este (3a) traz a medida da PW-4 (b), a vontade e o caráter do v11 em TS, com gabarito. O v11 no `Motor`
(`VERSAO_PET` 11, o laço do corpo, o vínculo B, a tela do desejo e os botões) fica para a parte 3b, que espera uma decisão (abaixo).

- **A medida** (`python experiments/calibrar_carater_v11.py` → `artifacts_v2_w_porte/carater_v11_calibracao.json`), sobre os brutos dos
  20 pets v11 e 20 pets v10 da medida da seção 12 (nada simulado de novo):
  - **a escala:** 0,05 × 0,2966 = **0,015**;
  - **o deslocamento do adolescente:** atento −0,0117, impetuoso +0,0142, paciente −0,0167, resistente +0,0142;
  - **o do adulto:** atento −0,7917, impetuoso +0,2604, paciente +0,25, resistente 0.
- **Pelo critério da seção 15, NÃO fecha** (os números ficam PROPOSTOS e vão ao Matheus):

  | condição | medida | faixa | |
  |---|---|---|---|
  | as linhas | brigão 0,20, guardião 0,30, caçador 0,30, colosso 0,20 | cada uma em [0,15; 0,35] | **passa** |
  | a forma de cima | 0,65 | [0,35; 0,65] | **passa**, no limite |
  | a escala | razão das medianas 0,99; eixos cortados 0,1375 (v10: 0,006) | razão em [½, 2]; cortados ≤ 0,106 | **falha** |

- **A leitura:**
  - a escala põe a mediana do v11 no lugar da do v10, mas a cauda do A é mais longa. Os pets do dono aleatório desviam muito mais no eixo
    resistente (até 3,06 vezes a escala) e batem em ±1;
  - o eixo resistente (comer e emburrar) não sai do zero em 16 dos 20 pets no fim da criança e em 13 no fim do adolescente: o tempo
    livre não propõe essas ações. Por isso toda a linha caçador sai **sentinela** (a mediana do complementar é 0, e todo pet fica do lado ≥ 0), e o emboscador não aparece;
  - o deslocamento do adulto no eixo atento (−0,79) é grande: é a mediana dos colossos, que desviam muito no atento;
  - os 20 pets calibram e conferem ao mesmo tempo, e a conferência é otimista.
- **A vontade em TS** (`CerebroA.desvioAprendido` e `desejoLobos` em `web/app/motor/lobos.ts`): bate bit a bit com a seção `vontade` do
  gabarito (`web/app/test/vontade_lobos.test.ts`), nas 288 decisões de cada uma das 4 vidas, rejogadas pelo laço do corpo, e na grade de
  32 sondas. É pura: o laço com e sem o espião dá a mesma vida. A necessidade de sempre saiu do `Bandit.desejo` para uma função
  (`necessidade`), sem mudar a conta dos v2 a v10.
- **O caráter do v11 em TS** (`caraterV11` em `web/app/motor/carater.ts`): o método do Python, não o da web dos v3 a v10, com as sondas de
  `metrics.estados_sonda`, o corpo da rng `sonda-corpo`, as distribuições pelo `RandomPy` e o cérebro recém-nascido como base. O cérebro
  é sondado por `CerebroA.amostrar`, que sorteia como o `agir` sem mexer no cérebro.
  - O gabarito novo é `web/app/test/gabaritos/carater_v11_python.json` (`python experiments/exportar_gabarito_carater_v11.py`): as 4 vidas
    v11, no fim da criança e do adolescente, com a distribuição, o bruto, o caráter, a linha e a forma.
  - Bate bit a bit (`web/app/test/carater_v11.test.ts`, 6 testes).
  - **O achado:** o `sum()` do Python 3.12 em diante soma floats com compensação (Neumaier). O TS porta essa soma (`somaPy`), e o exportador e
    a calibração recusam o Python 3.10 e o 3.11.
- **As constantes novas** `CCP_V11` e `DESLOC_CARATER_V11` são conferidas por `constantes.test.mjs` contra o artefato da calibração.
  Os pets v1 a v10, as assinaturas e os gabaritos não mudaram.
- `npm run tipos` limpo; `npm test` com 38 arquivos e 439 testes; os testes Python tocados passam (8).

**As duas decisões do #339, DECIDIDAS (Matheus, 2026-10-18), pelas opções do PR:**
- **O caráter:** opção (a), aceitar os números PROPOSTOS. O v11 usa a escala 0,015 e os deslocamentos medidos. O custo aceito: 14% dos
  eixos batem em ±1, e o caçador sai sempre sentinela.
- **A parte 3b:** opção (a), o v11 é o v10 sem as camadas que dependem da bronca ou que o laço recusa.
  - Ficam: a evolução (com o caráter do v11), o combate e tudo acima, o treino sem obediência e o vínculo B pelo desejo atendido.
  - Saem: a educação (as janelas, o petisco e o banheiro), a mentira e a obediência.
  - A lesão fica, e o tratar só cura.

**Para a parte 3b, a decisão que falta:** o que o v11 do jogo herda dos v4 a v10. O laço do corpo recusa a educação (as janelas, as
travessuras e a disciplina, resolvidas com a bronca e o petisco), a obediência e o treino com obediência. E a mentira dos v7 é julgada
com a bronca. O pedido está no corpo do PR.
