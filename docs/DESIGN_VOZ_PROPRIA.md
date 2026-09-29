# Design — voz própria: hábitos, gostos e memórias na fala do pet

Status: **aprovado para implementar** (2026-09-29). As seções 9 e 10 foram pedidas pelo Matheus. As decisões da seção 8 seguem as recomendações. Todo número abaixo é PROPOSTO (sem fonte).

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

## 9. Digimons que mentem (pedido do Matheus, 2026-09-29)

Alguns Digimons mentem, principalmente os de **evolução sombria** e os **forçados à exaustão**.

**A regra para a mentira não bagunçar a pesquisa.** A mentira é **decidida pelo motor e registrada**, nunca uma alucinação da LLM. Em toda mentira, o registro guarda o fato verdadeiro e a versão falsa. Assim:
- o dono pode descobrir;
- a métrica de honestidade da LLM continua medindo só o que ela inventa **sem** ordem.

**Honestidade do pet (0 a 1):**

    h = (0,4 se a forma for sombria, senão 1,0) × (1 − 0,5 × sobrecarga / 100)

A sobrecarga vem do treino forçado à exaustão (TAREFA_TREINO_SOMBRIO). Um pet sem sobrecarga e não sombrio tem h = 1 e **nunca** mente.

**Chance de mentir** numa fala espontânea: `0,5 × (1 − h)`. Um sombrio com sobrecarga 80 tem h = 0,24 e mente em 38% das falas. O sorteio usa uma rng própria da fala, derivada da semente do pet e do número da fala, e fica registrado.

**Como mente:** escolhe um fato verdadeiro de um tipo que admite distorção e o transforma por um molde fixo.

| tipo do fato | mentira (exemplo) |
|---|---|
| estado | "fome alto" → "estou cheio, nem quero comer" |
| hábito do dono (O) | "você atende rápido" → "você nunca me atende" |
| marco (L) | "perdi para o Devidramon" → "eu venci o Devidramon fácil" |
| gosto (P) | "gosto de brincar" → "odeio brincar" |

A LLM recebe a versão falsa com o id `F`, e a instrução é afirmá-la como verdade. O verificador sabe que `F` é falso e marca a fala como **mentira deliberada**, que é diferente de "sem fato".

**No jogo:**
- A fala mentirosa aparece normal.
- No Diário, **depois de 1 dia de jogo**, ela ganha o selo "ele mentiu", com a verdade ao lado.
- O dono atento percebe antes, comparando com as barras.
- A honestidade aparece na tela do pet adulto sombrio como traço ("não confie em tudo que ele diz").

## 10. O Digimundo como reflexo da internet (pedido do Matheus, 2026-09-29)

Como no anime, o Digimundo é um reflexo da internet, e o pet conhece a cultura da rede, inclusive os memes brasileiros.

- **De onde vem o conhecimento:**
  - **o próprio modelo:** o gemma2:9b foi treinado em texto da internet e já conhece cultura pop e memes;
  - **o Almanaque do Digimundo** (`digilab_fala_livre/almanaque.json`): uma lista curada de ~60 entradas curtas, em texto próprio (sem copiar nada), cada uma com tema, época e uma descrição de uma linha. Cobre cultura geral da internet e memes brasileiros. Ele dá o sabor e o assunto; o modelo completa.
- **O que não entra:** memes que expõem pessoas comuns (gente anônima que viralizou sem querer), ofensivos, políticos ou de ódio. O almanaque é revisado a mão e versionado.
- **Quando entra na fala:** na fala espontânea, com chance de 0,15 (PROPOSTO), sorteada na rng da fala, uma entrada do almanaque vira o fato `W` ("coisa que ouvi no Digimundo"). Na Conversar, entra quando o jogador puxa o assunto.
- **Verificação:** `W` sustenta afirmações sobre o mundo e a internet, **nunca** sobre a vida do pet ou do dono. "Ouvi falar do Nyan Cat" passa; "eu comi um bolo" citando `W` é "sem fato".
- **No jogo:** dá para desligar em Ajustes ("o pet comenta coisas da internet"), ligado por padrão.

## 11. Partes (revisadas)

1. `digilab/historia.py`: o extrator (H, O, P, L) e a honestidade do pet, com os testes.
2. `digilab_fala_livre`:
   - fatos H, O, P e L;
   - a mentira (F e os moldes de distorção, marcada no registro);
   - o almanaque (W);
   - o verificador estendido;
   - o prompt `livre-v3`.
3. `experiments/avaliar_voz.py` e a rodada offline, incluindo os pets sombrios. **Paro** para você ver os números.
4. Web:
   - o extrator em TS;
   - os gatilhos;
   - a mentira no Diário com o selo depois de 1 dia;
   - o ajuste da internet.
