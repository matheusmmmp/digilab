# Design — voz própria: hábitos, gostos e memórias na fala do pet

Status: **para aprovação**. Nada foi implementado. Todo número abaixo é PROPOSTO (sem fonte) até você aprovar.

## 1. O problema

Na revisão de 2026-09-29, as falas saíram genéricas e presas a um contexto estreito.

**Causa.** Desde a fala-v4, a fala do balão (`servidor/fala_llm.py`) deixa a LLM escrever só a moldura; o miolo é a frase pronta do motivo da **última** decisão. A fala livre da aba Conversar (`digilab_fala_livre`) tem mais contexto, mas também só o **presente**: estado, desejo, os últimos 3 motivos, algumas memórias recentes e vínculo. Em nenhum dos dois o pet sabe **quem ele se tornou**. Então dois pets de donos diferentes falam quase igual.

**Objetivo.** O pet fala da própria história: hábitos que percebe em si e no dono, gostos que aprendeu, momentos marcantes. E às vezes fala sem ser chamado. Cada pet soa diferente porque a vida de cada um foi diferente.

**Trava que não muda.** Toda afirmação precisa de um fato por trás. Os fatos saem do registro (verdadeiros e reproduzíveis). A LLM escolhe **o que** trazer e **como** dizer. O verificador que já existe barra o que não tem fato.

## 2. Fatos novos (a "história" do pet)

Um extrator determinístico lê o registro e devolve os fatos novos. É uma função pura do log: mesmo registro, mesmos fatos.
- No web: `motor/historia.ts`, a partir do registro do jogo.
- No Python: `digilab/historia.py`, para a avaliação offline com as vidas de pesquisa.

Os fatos entram no bloco de fatos da fala livre, com ids próprios.

| id | tipo | exemplo de texto | como sai do registro |
|---|---|---|---|
| H | hábito meu | "quase sempre durmo depois de comer" | sequência A→B: P(B em até 30 min depois de A) ≥ 0,6, com ≥ 10 ocorrências de A e lift ≥ 1,5 sobre a taxa de B |
| H | hábito meu | "à noite eu chamo mais você" | uma ação num período do dia (manhã, tarde, noite, madrugada) com taxa ≥ 2× a média do dia e ≥ 10 ocorrências |
| O | hábito do dono | "você costuma aparecer de manhã" | período com ≥ 40% das ações do dono, em ≥ 3 dias diferentes |
| O | hábito do dono | "você me dá mais carinho que comida" | ação de cuidado com ≥ 35% das ações do dono |
| O | hábito do dono | "quando faço manha, você cede com petisco" | petisco ÷ (petisco + bronca) nas manhas ≥ 0,6, com ≥ 5 manhas (pets v4) |
| O | hábito do dono | "você atende meus chamados rápido" / "demora" | mediana da demora nos chamados ≤ 5 min ou ≥ 12 min, com ≥ 5 chamados |
| P | gosto | "gosto de brincar" / "não curto emburrar" | ação cujo valor aprendido (bandit) mais sobe acima do instinto, e a que mais cai, na sonda do caráter |
| P | gosto | "meu treino favorito é esquiva" | exercício com ≥ 35% das sessões, com ≥ 6 sessões |
| P | gosto | "quero revanche contra o Devidramon" | o último rival que o venceu e ainda não foi vencido depois |
| L | marco | "virei Champion no dia 2", "perdi para o Piedmon 3 vezes antes de vencer", "me machuquei e você me tratou", "você sumiu por 9 h no dia 3" | eventos do registro: evoluções, primeira derrota e primeira vitória na campanha, lesões, ausências ≥ 6 h de jogo sem o dono agir, a forma sombria, a geração |

**Limites.** O extrator não cria texto livre: cada fato é montado de um molde fixo por tipo. O servidor recebe os fatos estruturados, valida o formato como já faz (chaves e tamanhos) e escreve o texto.

**Ordem.** Até 12 fatos de história por fala, na ordem: marcos recentes, hábitos, gostos e hábitos do dono. Um fato já citado nas últimas 5 falas vai para o fim, para o pet não repetir sempre o mesmo assunto.

## 3. Quando o pet fala sozinho (fala espontânea)

Os gatilhos de hoje (acabou de lutar, desejo novo…) continuam. Entram gatilhos novos, cada um com o fato que o disparou marcado como `G`:

| gatilho | quando |
|---|---|
| reencontro | o dono volta depois de ≥ 3 h de jogo sem agir |
| hábito novo | um fato H ou O aparece pela primeira vez (cruzou o limiar): "percebi que eu sempre…" |
| aniversário | 1 dia de jogo depois de uma evolução |
| revanche | antes de lutar contra o rival do gosto "revanche" |
| marco | logo depois de um marco (evolução, lesão tratada, vitória sobre o chefe) |

**Ritmo.** No máximo 1 fala espontânea a cada 2 h de jogo, e nunca durante uma janela aberta de chamado ou aviso. A fala aparece no balão, com o ícone da verificação.

**O balão de todo toque** (o motivo da decisão, fala-v6) continua como está: é rápido e sempre honesto. A voz nova é a fala espontânea e a Conversar.

## 4. O pedido à LLM e a verificação

- **Modelo:** o mesmo gemma2:9b local aprovado; o prompt ganha uma versão nova, `livre-v3`.
- **O que o prompt diz:**
  - "você pode falar da sua história, dos seus hábitos e dos do seu dono";
  - "escolha **um** fato da história ou do gatilho e fale dele do seu jeito, no tom do estágio";
  - "cite os ids".
- **Verificador:** o de hoje, com uma extensão. Os tipos H, O, P e L passam a sustentar afirmações sobre costume, gosto e lembrança (`TIPOS_QUE_SUSTENTAM`); uma afirmação de hábito sem fato H ou O é "sem fato".
- **Registro:** a fala e os fatos citados vão para o log de apresentação do pet, como hoje (modo livre gravado). O motor e o save não mudam.

## 5. Crescer com o estágio

- **Bebê:** só emote, como hoje.
- **Criança:** até 1 fato de história, em frase curta.
- **Adolescente:** 1 fato, com opinião ("acho que…").
- **Adulto:** até 2 fatos ligados ("desde que você começou a aparecer de manhã, eu…").

Fica para uma segunda etapa: o pet pegar expressões do dono na Conversar. Exige guardar as falas do jogador no log do pet e filtrar o que pode ser repetido.

## 6. Como medir (antes de ligar no jogo)

Uma avaliação offline, como as rodadas da fala livre (`experiments/avaliar_voz.py`):
- **Amostra:** vidas da V3/V3c (donos variados e personas), com o extrator em Python, e 200 falas espontâneas no gemma2:9b.
- **Gates (PROPOSTOS):**
  - **honestidade:** falas com afirmação sem fato ≤ 5% (a rodada 2 teve 3%);
  - **história:** ≥ 50% das falas citam um fato H, O, P ou L;
  - **variedade entre pets:** num mesmo gatilho, pets de donos diferentes citam fatos diferentes em ≥ 70% dos pares;
  - **repetição:** um mesmo pet não repete o mesmo fato em mais de 2 de 5 falas seguidas.
- **Avaliação cega:** 30 falas voz-nova × 30 falas fala-v6 misturadas, para você marcar "qual parece mais vivo".
- **Artefatos:** `artifacts_voz/` com as falas, os fatos, a verificação e o resumo.

## 7. Partes (um commit cada, depois da aprovação)

1. `digilab/historia.py`: o extrator. Testes de cada regra em registros montados à mão e de que o mesmo registro dá os mesmos fatos.
2. Fatos H, O, P e L no `digilab_fala_livre` (formato, limites, verificador) e o prompt `livre-v3`.
3. `experiments/avaliar_voz.py` e a rodada offline. **Paro aqui** para você ver os números e a avaliação cega.
4. Web: `motor/historia.ts` (os mesmos testes de regra), os gatilhos novos na fala espontânea e o ritmo.

## 8. O que você precisa decidir

1. Os limiares da seção 2 e o ritmo da seção 3 (tudo PROPOSTO).
2. Se o pet pode falar de hábitos **do dono** ou só dos dele. Eu recomendo que sim: é o que mais surpreende ("você sempre some no fim de semana").
3. Se a etapa de pegar expressões do dono entra agora ou depois. Eu recomendo depois, porque pede cuidado com o que o jogador escreve.
