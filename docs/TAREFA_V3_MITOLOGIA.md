# TAREFA V3 — MITOLOGIA (2026-11-11)

Coordenador: Gerente da V3 (Claude Code). Worker: o mesmo. Worktree e branch: `v3-mitologia`. Status: E0 na `main` (#792); E1 no PR.

Categoria: implementacao. Origem: Matheus, 2026-11-11: "faz o oráculo com voz, o evento do hybris e a brincadeira variada". É a primeira
etapa da mitologia (a E0 e a D-MM-16), só no web, atrás da chave `mitologia`.

## 1. Pergunta

Um deus, dois eventos sutis e uma entidade que percebe cabem no jogo de hoje, como função pura do log, sem mexer no motor, no cérebro nem
na luta?

Não é uma hipótese de pesquisa. É a primeira peça jogável da pesquisa de 2026-11-11 sobre moral, mitologia e felicidade, que está no vault
Obsidian `DigiLab Research`, em `20 Temas`. A fonte desta etapa é a seção 5 da nota "Síntese — moral, mitologia e felicidade".

## 2. Depende de

Do que já está na `main`:
- a luta da POC (pets v21), com o `_lutarPoc` e o `vida5.lutas`;
- o mundo físico, com o `Mundo.decisoes` e o `brincou_com_bola`;
- o corpo com o tédio pela variedade (o DS-4: bola, brincar, explorar e o dono brincar);
- a faixa das dicas do Professor Agumon;
- o sprite `bot_oraculo` no atlas UP.

Das decisões do Matheus, todas de 2026-11-11:
- **as D-MM-1 a D-MM-18:** a D-MM-4 (a Diversão encarnada pelo Piedmon), a D-MM-9 (reabrir "lendas não interessa"), a D-MM-11 (a), a
  D-MM-16 (a E0) e a D-MM-18 (a hybris do par);
- **as respostas 2 e 3:** o Jijimon ganha voz só para a mitologia, e a lenda é um mito próprio no molde de Wukong, sem nomear a obra na
  fala e com o crédito na tela de créditos;
- **a ordem desta etapa:** a Síntese punha a E0 depois do SOM_UP (#781) e dos Bits (#762/#765). O Matheus pediu a E0 agora (D-E0-1).

## 3. Mudança mínima

**O motor (`web/app/motor/`):**
- **`lendas.ts`, novo.** É uma função pura sobre o pet refeito do log: `lendas(m)`, `hybrisDe`, `variadaDe` e `detalheNoTick`. Traz também
  os números da E0 (`CMIT`, DECIDIDOS) e a voz do oráculo por modelo, sem LLM: os 7 pedaços da lenda do macaco sob a montanha mais o
  fecho.
- **`motor.ts`:** um registro derivado, `forcaLutas`, com a força do pet na entrada de cada luta da POC (a soma dos 6 stats de
  `statsDoPet`) e o resultado. Ele fica fora do save e da assinatura, como o `vida5` (D-E0-2).
- **`index.ts`:** exporta o `lendas.ts`.

**A tela (`web/app/src/`):**
- **`mitologia.ts`, novo:** a chave `mitologia`, desligada por padrão (`CHAVE-mitologia`), e o que o oráculo já contou a cada pet
  (`CHAVE-mitologia-ouvidas`). As duas coisas ficam fora do save.
- **`componentes/BalaoOraculo.tsx`, novo:** a fala do Jijimon, com o retrato `bot_oraculo` e o botão "Entendi". Ele espera uma dica do
  Professor Agumon que esteja na frente, e fica fora da luta e das telas cheias.
- **`telas/pet/ilha/mitologia.ts`, novo:** a nuvem dourada sobre o ninho, por um dia de jogo, depois da brincadeira variada.
- **Os arquivos que já existiam:**
  - `App.tsx` monta o balão;
  - `ilha/vista.ts` monta a nuvem;
  - em `TelaConfig.tsx` entram a linha "Mitologia" nos Ajustes e o crédito da lenda em Sobre;
  - em `estilo/abertas.css` entra a posição do balão: no celular, acima da barra das ações; no desktop, no centro, acima dela.

**Os eventos:**

| evento | gatilho (DECIDIDO) | o que se vê |
|---|---|---|
| **a hybris** (do par dono e pet, D-MM-18) | uma derrota para um **líder da Campanha** com `total` ≥ 1,3 × a força do pet na entrada; no máximo uma por dia de jogo | o Jijimon conta o próximo pedaço da lenda (`parte` = as hybris anteriores); contada inteira, ele fecha |
| **a brincadeira variada** | num dia de jogo, 3 atividades de tédio diferentes (bola, brincar, explorar e o dono brincar), a mesma regra do `atividadeMundo`; no máximo uma por dia | a nuvem dourada para sobre o ninho por um dia de jogo, sem texto e sem som |

**O que não muda:**
- `digilab/` (o Python), o `engine.py`, o cérebro, o núcleo da luta e o equilíbrio (LP5);
- o log, o save, a assinatura e o `VERSAO_PET`: nenhuma versão de pet nova;
- os gabaritos: a suíte inteira do Vitest passa sem tocar em nenhum (D-E0-3).

## 4. Experimento e gate (se houver run)

Não há run, e por isso não há plano de análise nem faixa de sementes. O que se mede é só o seguinte:
- o Vitest de `test/lendas.test.ts`;
- o e2e `e2e/oraculo_mitologia.spec.ts`, a 390 e a 1280 px;
- o Matheus jogando.

## 5. Entrega

- **Os testes:**
  - em `web/app`: `npm test`, `npm run tipos` e o e2e da frente;
  - o Python não muda.
- **O registro:** a seção de 2026-11-11 em `docs/registro/2026-11.md` (D-E0-1 a D-E0-6), com a D-MM-9 registrada.
- **A entrega:** o PR contra a `main`, com o relato no corpo. O merge é só do Matheus.

## 6. Fora desta tarefa

- **A moral:** a pontuação pró-social, os deveres e o escudo, os pesos no genoma (M0), a run (M1 e M2) e o estágio moral.
- **Os outros deuses e o resto da mitologia:**
  - os outros quatro deuses do aro e o Myotismon como termômetro;
  - a aura;
  - a autocorreção.
- **A fala:** a voz do oráculo pela LLM, no modo livre gravado. Ela espera o G-NATURAL da DC5 (D-MM-11).
- **A hybris fora da Campanha:** os torneios, a Arena e a Liga.
- **A visita entre donos, o gosto musical e o Python.**

## 7. Critérios de aceitação

- **O `test/lendas.test.ts` passa (14 testes).** Ele cobre:
  - a regra da hybris, com o limite, o tipo de rival, o resultado e a uma por dia;
  - a da brincadeira variada, com a repetição, o dia novo e a uma por dia;
  - a nuvem por um dia;
  - a voz em pedaços, na ordem e com o fecho, sem nomear a obra;
  - uma vida de verdade que dá os dois eventos;
  - o replay pelo `Motor.reproduzir`, que dá o mesmo `forcaLutas`, as mesmas lendas e a mesma assinatura;
  - o `forcaLutas` fora da assinatura.
- **A suíte inteira do Vitest passa sem mudar nenhum gabarito.**
- **O `npm run tipos` passa.**
- **O `e2e/oraculo_mitologia.spec.ts` passa (4 testes):**
  - os pedaços na ordem, a 390 e a 1280 px, e o que já foi contado não se repete depois de recarregar;
  - desligada, a chave não deixa o oráculo falar;
  - um pet que o oráculo ainda não conhecia começa calado.

## 8. Precisa do Matheus

**DECIDIDAS pelo Matheus em 2026-11-11 ("Aprovo os números"):** as quatro valem como recomendadas. Seguem SEM FONTE.

| decisão | recomendação | custo de errar |
|---|---|---|
| **D-E0-4a** a hybris pede o líder com ≥ 1,3 × a força do pet | ficar com 1,3 e ajustar jogando | baixo: só muda quando o oráculo fala; com 1,3, o Rookie da vida de teste (força 60) aciona contra o Gazimon (96) |
| **D-E0-4b** no máximo uma hybris por dia de jogo | ficar | baixo: sem o teto, a vida de teste contava a lenda inteira numa tarde (15 derrotas em 1,4 dia) |
| **D-E0-4c** 3 atividades diferentes num dia dão a brincadeira variada | ficar | baixo: a nuvem é só vista e dura um dia |
| **D-E0-5** um pet que o oráculo ainda não conhecia começa calado: as derrotas de antes de ligar a chave não falam, mas o pedaço da lenda segue o `parte` do log | ficar | baixo: a alternativa contaria de uma vez a história inteira de um pet antigo |

## 9. Resultado da E0 (2026-11-11)

- **Os números do teste:**
  - o `test/lendas.test.ts` tem 14 testes;
  - a suíte do Vitest tem 119 arquivos e 1142 testes, todos passando, com os gabaritos iguais;
  - o e2e da frente tem 4 testes, todos passando.
- **A vida de teste:** é o Rookie de semente 101, com as lutas contra o Gazimon na Campina (`e2e/gerar_save_oraculo.mjs`). Ela dá uma
  brincadeira variada no tick 570 e duas hybris, nos ticks 705 e 1440.
- **As capturas** a 390 e a 1280 px (o balão e a nuvem) foram mandadas ao Matheus na sessão e ficaram fora do repositório.

## 10. E1: os sinais dos deuses, o Códice e os segredos (2026-11-11)

**A origem:** o Matheus pediu "features, easter eggs, coisas que fomentem essa mitologia" e escolheu, de uma lista, sete itens: o Códice das
lendas, os sinais dos cinco deuses, o Myotismon como termômetro, a pedra do macaco, os 7 toques no Jijimon, o dia 81 e as pegadas na mata.

**As regras da E0 continuam:**
- tudo fica atrás da mesma chave `mitologia`;
- tudo é função pura do pet refeito do log, sem mudar o motor, o cérebro, a luta, o log, o save, a assinatura nem o `VERSAO_PET`;
- as falas são por modelo, sem LLM e sem nomear a obra.

**O que entrou:**

| peça | gatilho (DECIDIDO pelo Matheus em 2026-11-11, "Aprovo os gatilhos"; SEM FONTE) | o que se vê |
|---|---|---|
| **Coragem** (brasa) | vencer um líder da Campanha com `total` ≥ a força do pet | uma chama que não queima, perto do ninho, por um dia |
| **Amizade** (cirro) | 3 dias seguidos com ≥ 3 carinhos e ≥ 2 brincadeiras do dono | duas flores que se viram uma para a outra, por um dia |
| **Conhecimento** (ferrugem) | um dia com ≥ 6 explorações do pet | um marco com um risco dourado, por um dia |
| **Sinceridade** (limo) | um dia com ≥ 3 chamados atendidos | um broto verde, por um dia |
| **Diversão** (o macaco, Piedmon) | a brincadeira variada da E0 | a nuvenzinha dourada, por um dia |
| **o Myotismon** (fora do aro) | no último dia, ≥ 12 ações do dono com a mais repetida em ≥ 75 %, ou ≥ 6 lutas contra o mesmo rival | morcegos sobre o ninho e a ilha mais escura; variar devolve a luz |
| **a pedra do macaco** | sempre na mata, na célula (56, 20), com a chave ligada; é "achada" quando o pet termina uma decisão ou é solto a ≤ 2 células dela, de noite | a pedra com uma racha dourada; o Jijimon conta de onde o macaco nasceu, uma vez |
| **as pegadas** | a 60ª exploração da vida | uma trilha do ninho até a pedra; o Jijimon dá a pista ("numa noite clara"), uma vez |
| **o dia 81** | o 81º dia de vida | os cinco sinais juntos o dia inteiro; o Jijimon fala das 81 provações, uma vez |
| **o enigma** | 7 toques seguidos (em 3 s) no retrato do Jijimon no Códice | uma pergunta com 3 opções; quem acerta ganha um pêssego dourado perto do ninho por um dia |
| **o Códice das lendas** | no Diário, aba Registro, só com a chave | os pedaços da lenda ouvidos, os sinais vistos (com quantas vezes) e os segredos achados; o resto aparece como "???" com uma pista |

**Os arquivos:**
- **novos:**
  - `web/app/motor/lendas_e1.ts`, com os números `CMIT_E1`;
  - `web/app/src/componentes/Codice.tsx`;
  - `web/app/test/lendas_e1.test.ts`, com 15 testes;
  - `web/app/e2e/mitologia_e1.spec.ts`, `web/app/e2e/gerar_save_mitologia_e1.mjs` e `web/app/e2e/save_mitologia_e1.json`;
- **mudados:**
  - `web/app/src/telas/pet/ilha/mitologia.ts`, onde a `NuvemDoDia` virou `SinaisDaIlha`;
  - `web/app/src/mitologia.ts`, com o "já ouvi" por pet virando um registro (o número antigo vira `h`), a fila do oráculo e o enigma;
  - `web/app/src/componentes/BalaoOraculo.tsx`, que agora fala da fila;
  - `web/app/src/telas/diario/TelaRegistro.tsx`, que monta o Códice;
  - `web/app/src/telas/pet/ilha/vista.ts`;
  - `web/app/motor/index.ts`;
  - em CSS, `estilo/abertas.css` (o Códice) e `estilo/pet_home.css` (o escurecimento);
  - `TelaConfig.tsx`, com o resumo da linha "Mitologia".

**Os testes:**
- o `test/lendas_e1.test.ts` tem 15 testes, todos passando;
- a suíte inteira do Vitest tem 129 arquivos e 1250 testes, todos passando, sem mudar nenhum gabarito;
- o `npm run tipos` passa;
- o e2e da E1 e o da E0 juntos têm 9 testes, todos passando: a pedra contada uma vez, o Códice com o vivido e os "???", o enigma por 7
  toques (errar, acertar e continuar decifrado depois de recarregar) e a chave desligada sem nada.
- Uma rodada do e2e da E0 falhou uma vez por um erro de console que não se repetiu em outras cinco.

**A calibração jogando** (D-E1-3, só leitura de vidas de teste, sem run de pesquisa):
- Na vida comum de 10 dias (sementes 101, 202, 303 e 505, com o dono de roteiro), o pet nunca sai da casa e do jardim. Por isso, o
  Conhecimento por "as 4 regiões num dia" e as pegadas por "30 explorações na mata" nunca disparariam. A Amizade por "1 dia" saía todo
  dia.
- Com os gatilhos da tabela, em 10 dias aparecem: Conhecimento de 1 a 7 vezes, Amizade 3, Diversão de 1 a 6 e Sinceridade 1.
- As pegadas abrem em uns 3 dias no pet curioso (a semente 101) e em semanas nos outros.

## 11. A chave começa ligada (2026-11-11)

**O pedido do Matheus:** "quero que a mitologia sempre esteja ativa, ela pode ser desligada, mas já começa ligada".

**O que mudou:**
- **O padrão da chave virou ligada.** Em `web/app/src/mitologia.ts`, o `mitologiaLigada` lê `CHAVE-mitologia !== "0"`: sem nada gravado,
  a chave fica ligada, e só o "0" desliga. Quem desligou nos Ajustes continua desligado.
- **Os pets que já existiam:**
  - as derrotas de antes continuam caladas (D-E0-5);
  - a pedra, as pegadas e o dia 81 já vividos o oráculo conta uma vez cada.
- **Os e2e:**
  - o "desligada" agora grava "0";
  - o `oraculo_mitologia.spec.ts` ganhou o teste "sem nada gravado, a chave começa ligada".
- **O que isso muda em relação à E0:** a regra "desligada por padrão, o jogo de hoje" (seção 3) deixou de valer.
  - O que entra na tela de quem não mexeu nos Ajustes:
    - o balão do oráculo, quando houver o que contar;
    - os sinais e a pedra na ilha;
    - o escurecimento do Myotismon;
    - o Códice no Diário.
  - O log, o save, a assinatura e os gabaritos continuam iguais.

## 12. E2: Piedmon e a montanha (2026-11-11)

**A origem:** era a opção da lista da E1 que ficou de fora. O Matheus pediu "segue as outras pendências".

O Piedmon encarna o deus da Diversão, o do macaco (D-MM-4). A E2 faz dele o fecho da lenda. É só tela, como função pura do pet refeito do
log (`web/app/motor/lendas_e2.ts`, `montanhaDe`). Nada muda no motor, na luta, no log nem no save.

| peça | gatilho | o que se vê |
|---|---|---|
| **antes da luta** | o cartão de um dos dois Piedmon na Campanha (`npc_tier3_soberano` na Cidadela, `npc_v5_piedmon` na Montanha Espiral), com a chave ligada | uma linha do Jijimon no cartão |
| **a derrota** | a primeira derrota para o Piedmon | o Jijimon fala do riso e da queda, uma vez |
| **a lenda fechada** | a primeira vitória sobre o Piedmon com uma hybris antes (num tick anterior) | o Jijimon diz que o macaco saiu da montanha, uma vez; o aro dourado fica sobre a pedra para sempre; o Códice ganha "A montanha" |
| **a vitória sem queda** | a primeira vitória sobre o Piedmon sem nenhuma hybris antes | o Jijimon diz que a lenda só se fecha para quem conheceu a montanha por dentro, uma vez |

**Os arquivos:**
- **novos:** `web/app/motor/lendas_e2.ts` e `web/app/test/lendas_e2.test.ts`, este com 5 testes;
- **mudados:**
  - `web/app/src/mitologia.ts`, onde o "já ouvi" ganha `piedmon`, `semQueda` e `montanha`, e a fila do oráculo fala deles;
  - `web/app/src/telas/lutar/palcoPoc/TelaLugaresPoc.tsx`, com a linha no cartão;
  - `web/app/src/telas/pet/ilha/mitologia.ts`, com o aro;
  - `web/app/src/componentes/Codice.tsx`;
  - `web/app/src/estilo/luta_poc.css`;
  - `web/app/motor/index.ts`;
  - `web/app/e2e/mitologia_e1.spec.ts`, onde a montanha aparece escondida sem o Piedmon vencido.

**Os testes:**
- o `test/lendas_e2.test.ts` tem 5 testes, todos passando;
- a suíte inteira do Vitest tem 135 arquivos e 1334 testes, todos passando;
- o `npm run tipos` passa;
- o e2e da mitologia e o da Campanha (`luta_poc_lp3`) têm 13 testes, todos passando.
