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

**Mentir se aprende, como a travessura** (pedido do Matheus: "caso você não repreenda a mentira, ele aprende a mentir mais"). A mentira segue o Sistema A da educação (chamados falsos), com as mesmas peças:

- **Toda fala espontânea abre uma janela de fala** de 30 min de jogo (PROPOSTO), no mesmo lugar das janelas de chamado e aviso: uma janela por vez. O dono vê a fala, **nunca** se ela é mentira; julga pelas barras e pelo que sabe do pet, como no chamado falso.
- **Desfechos:**

  | o dono, na janela | a fala era mentira | a fala era verdade |
  |---|---|---|
  | bronca | **acerto**: disciplina +25 (o mesmo passo da travessura) e a mentira não conta como impune | bronca sem motivo: vínculo −0,05 (igual à bronca num chamado real) |
  | petisco ou elogio | **premiou a mentira**: +2 mentiras impunes | nada de novo (o efeito normal da ação) |
  | nada até o prazo | **passou impune**: +1 mentira impune | nada |

- **Chance de mentir** numa fala espontânea (a mesma forma da fração de chamados falsos):

      p = 0                                                  se h = 1, ou com 3 broncas certas seguidas em mentiras no estágio
      p = min(0,8, 0,5 × (1 − h) × (1 − disciplina/100) + 0,05 × mentiras_impunes)   no resto

  Um sombrio com sobrecarga 80 e disciplina 0 começa com h = 0,24 e p = 0,38. A cada mentira que passa impune, sobe 0,05. Um pet com h = 1 nunca começa a mentir, então nunca acumula mentira impune. As mentiras impunes voltam a 0 na evolução, como os petiscos cedidos. Todos os números são PROPOSTOS.
- **A honestidade que o jogo mostra** é `1 − p / 0,8`: ela cai com a vista grossa e sobe com a disciplina.
- **Onde vive.**
  - A mentira muda o motor (disciplina, vínculo, janela), então **é do motor**, não só da apresentação.
  - O `MotorEducacao` ganha a janela de fala e a `rng_mentira`, derivada da semente.
  - A fala espontânea entra no registro do jogo como um evento novo, `f`, com o tick e se foi mentira. Ela é sorteada no motor e reproduzida no replay.
  - A LLM só escreve a frase. Se ela falhar, o pet diz o molde fixo da mentira: a fala sempre acontece e o motor não depende da LLM.
- **Na pesquisa.**
  - `ConfigMentira.ligada` fica **desligada** por padrão, e a V3 e a confirmatória não mudam.
  - Ligada, os donos simulados reagem pela política deles:
    - o disciplinador dá bronca quando a fala contradiz as barras;
    - o permissivo dá petisco;
    - o ausente não vê.
  - Assim dá para medir quanto cada estilo de dono cria um mentiroso.

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
- **Nomes próprios:** podem entrar (decisão do Matheus, 2026-09-29). A entrada leva o nome do meme e das pessoas ou personagens dele, como a internet os conhece. A entrada descreve o meme; não inventa fato sobre a pessoa.
- **O que não entra:** memes ofensivos, políticos ou de ódio. O almanaque é revisado a mão e versionado.
- **Quando entra na fala:** na fala espontânea, com chance de 0,15 (PROPOSTO), sorteada na rng da fala, uma entrada do almanaque vira o fato `W` ("coisa que ouvi no Digimundo"). Na Conversar, entra quando o jogador puxa o assunto.
- **Verificação:** `W` sustenta afirmações sobre o mundo e a internet, **nunca** sobre a vida do pet ou do dono. "Ouvi falar do Nyan Cat" passa; "eu comi um bolo" citando `W` é "sem fato".
- **No jogo:** dá para desligar em Ajustes ("o pet comenta coisas da internet"), ligado por padrão.

## 11. Corpus de personalidade Digimon (pedido do Matheus, 2026-09-29; em montagem em outro chat)

O Matheus monta, em outro chat, um corpus do conteúdo narrativo dos jogos de Digimon de PS1 e WonderSwan. Ele traz, por Digimon: fontes, traços de personalidade, jeito de falar (pronome e terminações em japonês, bordões), interações e até 3 citações curtas traduzidas para PT-BR. Uma auditoria separada marca cada item com [VERIFICADO], [PARCIAL], [OUTRA MÍDIA], [INFERÊNCIA], [DIVERGENTE], [SEM FONTE] ou [FONTE INVÁLIDA], e dá um veredito por jogo.

**Arquivo.** `digilab_fala_livre/corpus_especies.json`, versionado (o sha vai para o registro de cada fala). Uma entrada por espécie:

    { "especie": "Devimon",              // o nome da forma, igual ao do catálogo do jogo
      "jogos": ["Digimon World (PS1)"],
      "tracos": [{"texto": "arrogante, despreza os fracos", "marca": "VERIFICADO", "fonte": "url"}],
      "fala":   [{"texto": "fala com ironia", "marca": "VERIFICADO", "fonte": "url"}],
      "interacoes": [{"com": "Angemon", "texto": "...", "marca": "PARCIAL", "fonte": "url"}],
      "citacoes": [{"pt": "...", "original": "...", "fonte": "url", "fan_translation": true, "marca": "VERIFICADO"}],
      "honestidade_especie": null }      // só com traço verificado de enganador (ver abaixo)

**O que entra.**
- Entram os itens [VERIFICADO] e [VERIFICADO EM OUTRA FONTE] (com a fonte corrigida), e só de jogos com veredito APTO ou APTO COM RESSALVAS.
- [PARCIAL] entra só na parte que tem suporte, reescrita na auditoria.
- [OUTRA MÍDIA] (do anime) entra só se o Matheus liberar, marcado como anime.
- [INFERÊNCIA], [DIVERGENTE], [SEM FONTE] e [FONTE INVÁLIDA] ficam de fora.
- O carregador aplica esse filtro, e um teste falha se entrar item de marca proibida.

**Como a fala usa o corpus.** O corpus dá o **jeito** da espécie, não fatos da vida do pet. O pet é a forma atual dele; um Devimon soa como Devimon, qualquer que seja o dono.
- **Traços e jeito de falar** vão para o bloco de estilo do prompt ("você é um Devimon: ..."). São guia de tom e **não sustentam** afirmação nenhuma: "eu comi" citando o corpus é "sem fato", como no W.
- **Citações** são só referência de tom, dadas ao modelo como exemplo.
  - O pet **não repete citação**: um filtro reprova a fala com 6 ou mais palavras seguidas iguais às de uma citação do corpus. Isso respeita o direito autoral e evita que o pet vire uma gravação.
  - Continua o limite do corpus: até 3 citações de 1–2 frases por espécie.
- **Interações** entram quando o outro Digimon está em cena: o rival de uma luta ou um NPC da campanha. Exemplo: o pet Angemon, antes de lutar com o Devimon, pode puxar a rixa. É **estilo**, não fato: não diz que aconteceu com ele.
- **NPCs e chefes da campanha** também ganham voz pelo corpus, na fala de antes e depois da luta.
- **Espécie sem entrada no corpus:** segue só com o tom do estágio, como hoje. O relatório da parte 3 mostra quantas formas do jogo têm entrada.

**Honestidade da espécie.**
- Uma espécie com traço **verificado** de enganador ou trapaceiro (exemplo esperado: Piedmon) ganha um multiplicador na honestidade da seção 9: `honestidade_especie` = 0,7 (PROPOSTO).
- Sem esse traço verificado, fica 1.
- O mentiroso do Digilab continua vindo principalmente da criação (sombrio, exaustão). A espécie só dá o empurrão que o jogo original justifica.

**No web.** O servidor local guarda o corpus e o usa em `/api/fala-livre`. O jogo recebe só `honestidade_especie` num mapa exportado, conferido contra o Python como as outras constantes (`mapa_constantes.json`).

**Enquanto o corpus não chega.** As partes 1 e 2 são feitas com um corpus de exemplo pequeno (2 espécies, marcado como exemplo), só para testar o carregador e o filtro. A rodada da parte 3 espera o corpus auditado.

## 12. Partes (revisadas)

1. Python:
   - `digilab/historia.py`: o extrator (H, O, P, L), com os testes;
   - `ConfigMentira`, a honestidade e a janela de fala no `MotorEducacao` (desligada por padrão; V3 e confirmatória intactas);
   - as reações dos donos simulados.
2. `digilab_fala_livre`:
   - fatos H, O, P e L;
   - a mentira (F e os moldes de distorção, marcada no registro);
   - o almanaque (W);
   - o corpus de espécies (o carregador com o filtro de marcas, o bloco de estilo, o filtro contra repetir citação);
   - o verificador estendido;
   - o prompt `livre-v3`.
3. `experiments/avaliar_voz.py` e a rodada offline, incluindo os pets sombrios e o corpus auditado. **Paro** para você ver os números.
4. Web:
   - o extrator em TS;
   - os gatilhos;
   - a janela de fala e o evento `f` no motor TS (com a paridade com o Python);
   - a mentira no Diário com o selo depois de 1 dia;
   - o ajuste da internet.
