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

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| PW-1 | o que entra no v11 | **DECIDIDO (Matheus, 2026-10-17): como recomendado.** O da seção 3: núcleo, consequência no corpo, carinho e tapa; sem mundo físico, frutas, dois pets e planejamento | levar mais: cada peça traz uma validação negativa ou aberta para dentro do jogo, e corrigir pede um v12 |
| PW-2 | o ponto do aprendiz | **DECIDIDO (Matheus, 2026-10-17): como recomendado.** O worker da etapa 1 propõe a partir da calibração do corpo e da conjunta, com a ressalva de que nada foi validado no jogo | um ponto sem base: deriva até o teto e um pet que muda demais ou nada |
| PW-3 | a vontade com o A | definir no Python primeiro (o D-W4 do #201: a ação de maior desvio aprendido sobre o prior, com a margem de hoje) | sem vontade, o vínculo B e a tela do desejo mudam; definir só na web perde a paridade |
| PW-4 | a escala do caráter no v11 | medir primeiro; manter se as linhas e formas ficarem perto das do v10 | formas concentradas, e o equilíbrio do combate sai do lugar |
| PW-5 | a percepção no painel | lista das entradas que mais pesaram, **não barra** | uma barra de percepção não corresponde a nenhuma conta do cérebro |
| PW-6 | memória e emoção no painel | uma barra (o lobo do A) e a emoção de hoje do pet como selo à parte, com a fonte | duas barras sem fonte separada: uma delas seria inventada |
| PW-7 | o painel nos pets v1 a v10 | **não**: só v11. Os antigos têm o bandit, e um painel para eles seria outro desenho | mostrar o bandit com os nomes dos lobos mistura dois cérebros na mesma tela |
| PW-8 | o PR #201 | fechar como substituído por esta tarefa, com um comentário apontando para cá | deixá-lo aberto: dois planos do mesmo porte, com recomendações opostas na consequência |

## 8. Fora desta tarefa

- O J5 e o lobo `planejamento` no jogo.
- O mundo físico com tela, as frutas, o paladar e os dois pets (cada um vira uma versão de pet própria quando a pesquisa fechar).
- Qualquer aumento de escala do cérebro (mais pesos, mais neurônios). O teto de pesos tem desenho próprio
  (`docs/DECISAO_V2_TETO_PESOS.md`).
- Mudar os pets v1 a v10, as assinaturas ou os gabaritos que existem.
