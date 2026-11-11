# TAREFA V3 — MITOLOGIA (2026-11-11)

Coordenador: Gerente da V3 (Claude Code). Worker: o mesmo. Worktree e branch: `v3-mitologia`. Status: E0 NO PR.

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
  os números da E0 (`CMIT`, todos PROPOSTOS) e a voz do oráculo por modelo, sem LLM: os 7 pedaços da lenda do macaco sob a montanha mais o
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

| evento | gatilho (PROPOSTO) | o que se vê |
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

Os números da E0 são PROPOSTOS e SEM FONTE. Cada um vem com a recomendação e o custo de errar:

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
