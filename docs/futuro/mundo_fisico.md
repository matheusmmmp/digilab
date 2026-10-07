# Mundo físico: comida no lugar, passeios que acham frutas e a bola, e atividades do Creatures 3 e de outros jogos

Status (2026-10-07):
- **DECIDIDO pelo Matheus:**
  - o jogador **deixa a comida fisicamente** no mundo, em vez de alimentar o pet direto;
  - ao **explorar**, o pet sai pelo lugar onde está e pode **encontrar comida**: a que o jogador deixou e a que o mundo faz aparecer ("caiu
    de uma árvore");
  - a **bola é um objeto físico no mapa**, pode ser encontrada nos passeios, e o pet brinca com ela.
- **PROPOSTO:** o desenho, neste documento. Não autoriza código: entra com tarefa e plano de análise, como sempre.

Parte de duas ideias já registradas: o ambiente manipulável de `docs/TODO_INTERACAO_CORPO.md` (IDEIA de 2026-09-30) e o corpo do Creatures 3
de `docs/futuro/ego_existencia.md`, seção 2.

## 1. Por que

**Resolve o pet parado.** Sem os botões de elogiar e repreender (`docs/DECISAO_PRODUTO_SEM_ELOGIO_BRONCA.md`), o pet aprende pela
consequência. No mundo de hoje, explorar só gasta energia, e o aprendiz aprende a ficar parado (validação do N3). Com comida e bola
espalhadas pelo mapa, **explorar passa a ter um retorno esperado**: às vezes o pet acha uma fruta e come, às vezes acha a bola e brinca. Vira
uma escolha de verdade entre gastar energia procurando e ficar onde está.

**É o que a teoria de forrageamento estuda.** Quando vale a pena sair de um lugar para procurar comida em outro é a pergunta do teorema do
valor marginal (Charnov 1976, `10.1016/0040-5809(76)90040-x`, metadados conferidos no Crossref em 2026-10-07; pista). Dá ao Digilab uma
pergunta clássica de exploração contra aproveitamento, no próprio pet.

**É como o Creatures 3 faz.** As norns andam pelo mundo, acham comida, frutas e sementes, e são guiadas por cheiros (seção 3).

## 2. O desenho mínimo (PROPOSTO)

**Áreas discretas, não 2D contínuo.** Um mapa com poucas áreas ligadas, como os cômodos do Creatures 3. Por exemplo:

| área | o que tem |
|---|---|
| **casa** | o ninho, onde o pet dorme; o comedouro, onde o jogador deixa comida |
| **jardim** | uma árvore que derruba frutas de tempos em tempos |
| **campo** | espaço aberto; a bola costuma rolar para lá |
| **mata** | mais frutas, mais longe, gasta mais energia para chegar |

**Objetos físicos com lugar.** Cada objeto está numa área: a comida que o jogador deixou, as frutas caídas, a bola. O pet também está numa
área. O motor já guarda frutas fora do estado, com prazo (o `MotorFrutas` do N4); a mudança é dar a cada uma um lugar.

**O que o pet faz, sem ação nova** (`AcaoPet` não ganha membro, para não quebrar a reprodução da v1):
- **explorar:** sub-decisão de para qual área ir; ao chegar, vê o que está lá;
- **comer:** come o que está na área dele;
- **brincar:** brinca com a bola se ela estiver na área dele; a bola pode rolar para outra área;
- **dormir:** no ninho, com conforto maior;
- **chamar e ocioso:** como hoje.

**O que o jogador faz:**
- **deixa comida** num lugar (no comedouro, ou onde quiser), em vez de "alimentar";
- **deixa a bola** num lugar, ou ela é achada nos passeios;
- **acaricia e dá tapa** como estímulos no corpo (decisão de 2026-10-07);
- **informa e pede**, como no N5 e no N7.

**O que o mundo faz:**
- **a árvore derruba frutas** de tempos em tempos (o "caiu da árvore"), mais no jardim e na mata;
- **a fruta apodrece** depois de um prazo, e a podre faz mal (o "manky" do Creatures);
- **a bola rola** para outra área depois de uma brincadeira.

Todo sorteio do mundo vem da **rng de ambiente**, separada da rng do pet, como manda o projeto.

**O que o pet percebe, sem acesso privilegiado:**
- **na área dele:** o que está ali;
- **nas áreas vizinhas:** só um **cheiro** fraco de comida, como os cheiros que se espalham no Creatures 3;
- **o resto:** nada. O pet não sabe onde está tudo; aprende onde costuma achar comida.

**Reforço pelo corpo.** Achar e comer reduz a fome. Brincar com a bola reduz o tédio. A fruta podre faz mal. Andar gasta energia. Para
brincar e explorar compensarem de verdade, o corpo precisa dos drives de **tédio** e de **curiosidade**, além da fome (a decisão S-3 de
`docs/DECISAO_PRODUTO_SEM_ELOGIO_BRONCA.md`).

**Cuidado com a fome.** Se a comida está longe, o pet pode não chegar a tempo. A regra de fome urgente do instinto passa a levar o pet ao
comedouro ou à comida mais próxima que ele conhece. O jogador vê onde deixou a comida.

## 3. O que o Creatures 3 tem

Fonte: a análise dos arquivos do Creatures 3 no repositório NORNBRAIN (`docs/reference/game-files-analysis.md`, extraída pelo autor dos
arquivos do jogo; pista, não fonte primária) e o *Creatures 3 Genetics Kit Manual* (lido em 2026-10-07; CORPUS).

**As 14 ações da norn:** olhar, empurrar (ativar), puxar, desligar, aproximar-se, recuar, pegar, soltar, expressar necessidade, descansar,
andar para a esquerda, andar para a direita, comer e bater.

**Os 20 drives:**
- **corpo:** dor; três fomes (proteína, amido, gordura); frio; calor; cansaço; sono;
- **social:** solidão; aglomeração;
- **emoção:** medo; tédio; raiva; desejo sexual;
- **lugar:** saudade de casa;
- **navegação:** cinco drives que ajudam a usar elevadores e portas.

**Os 40 tipos de objeto que o cérebro reconhece:**
- **comida:** semente, planta, folha, flor, fruta, comida, podre ("manky"), detrito;
- **bichos:** inseto, praga, criatura pequena, fera;
- **coisas:** brinquedo, botão, dispensador, ferramenta, poção, máquina, aparelho, veículo;
- **lugares:** porta, elevador, teletransporte, ninho, ovo, casa de cada espécie;
- **seres:** a mão do jogador, outras norns, grendels e ettins.

**Cheiros que se espalham pelo mapa:** som, luz, calor, água, nutriente, proteína, carboidrato, gordura, flores, máquinas, cada espécie e a
casa de cada espécie. A norn segue o cheiro para achar comida e para voltar para casa.

**Ações involuntárias:** encolher de dor, espirrar, tossir, tremer de frio, adormecer, gemer ao morrer.

## 4. Atividades para o Digilab, do Creatures 3 e de outros jogos

As referências a outros jogos são **inspiração de desenho, não evidência**. Pela regra da skill `literatura-digilab`, Digimon, Monster
Rancher e Pokémon nunca são citados como precedente.

| atividade | de onde | o que dá ao pet | risco ou custo |
|---|---|---|---|
| **Forragear:** achar frutas caídas, sementes, insetos comestíveis | Creatures 3 (fruta, semente, inseto); *Animal Crossing* (sacudir a árvore e a fruta cair) | fome; a pergunta do Charnov | energia para andar |
| **Brincar com a bola e brinquedos** que rolam e se acham | Creatures 3 (brinquedo); a bola da A1 | tédio | energia |
| **Evitar o que faz mal:** fruta podre, praga que pica, planta ruim | Creatures 3 (podre, praga, erva) | aprender a evitar pela punição do corpo | dor, mal-estar |
| **Dispensador com botão:** empurrar o botão solta comida | Creatures 3 (botão, dispensador; ação empurrar) | aprendizado instrumental limpo: a ação causa a recompensa | o pet pode "viciar" no botão; limitar a recarga |
| **Voltar para casa** e dormir no ninho | Creatures 3 (saudade de casa, cheiro de casa, ninho) | conforto, sono melhor | ficar longe da comida |
| **Abrigo do tempo:** frio e calor por área ou hora | Creatures 3 (frio, calor, clima) | conforto | — |
| **Fugir e se aproximar:** recuar de ameaça ou multidão, chegar perto de quem gosta | Creatures 3 (recuar, aproximar; medo, aglomeração, solidão) | medo, solidão | — |
| **Passeio com achados:** o passeio traz coisas pelo caminho | *Nintendogs* (presentes no passeio) | curiosidade | — |
| **Objetos que "anunciam" o que satisfazem** | *The Sims* (autonomia por necessidades) | o pet escolhe atividade pela necessidade | — |
| **Cultivar:** semente que vira planta que dá fruta | Creatures 3 (semente, planta) | comida no futuro, ligada ao lugar | lento |
| **Aprender com quem observa** | *Black & White* (a criatura copia o jogador; o postmortem de 2001 está na tabela verificada) | atalho de aprendizado | ver `docs/futuro/cognicao_social.md`, 5.2 |
| **Palavras:** máquina de ensinar nomes de coisas | Creatures 3 (computador de aprendizado) | vocabulário para a fala | outro sistema inteiro |
| **Banheiro e higiene num lugar** | *Tamagotchi*, *Digimon World* (só inspiração) | higiene | — |

## 5. Ordem recomendada

1. **O mundo físico mínimo:** áreas, comida deixada pelo jogador, frutas que caem, a bola como objeto, explorar como deslocamento, o cheiro
   nas vizinhas. É o que resolve o pet parado.
2. **Tédio e curiosidade no corpo**, para brincar e explorar recompensarem (junto do corpo químico do Creatures 3).
3. **Fruta podre e praga**, para o pet aprender a evitar.
4. **Dispensador com botão**, para medir aprendizado instrumental limpo.
5. **Casa, ninho e saudade.**
6. **Cultivo e palavras**, por último.

## 6. Consequências para a pesquisa

- **Mundo novo na bancada.** As runs de hoje não mudam: tudo atrás de chave, com as vidas antigas reproduzindo byte a byte. `engine.py` não
  muda; o mundo entra por subclasse do motor, como as frutas e a bola.
- **Uma chance nova para o P1.** No mundo `padrao` a consequência sozinha falhou (G-P1 da validação do N3). Num mundo em que explorar
  compensa, o aprendizado pela consequência tem o que aprender: onde procurar, quando sair, o que evitar. É o teste natural para o pet sem
  botões.
- **O dono vira quem arruma o mundo.** Ele não ensina com nota: escolhe onde deixar a comida e a bola. Separar o efeito do dono do efeito do
  mundo continua sendo o cuidado de sempre, com o "só cuidado" acoplado.
- **O automodelo ganha conteúdo.** "Onde costumo achar comida", "quanto me cansa ir à mata" e "esta fruta me faz mal" viram previsões que a
  rede de si pode errar e corrigir (`docs/futuro/ego_existencia.md`).

## 7. Decisões do Matheus

| # | decisão | recomendação |
|---|---|---|
| M-1 | Áreas discretas ou espaço 2D contínuo | áreas discretas primeiro; o 2D contínuo é o combate em tempo real e o corpo 2D, em espera |
| M-2 | Quantas áreas no começo | quatro (casa, jardim, campo, mata) |
| M-3 | "Alimentar" sai dos pets novos e vira "deixar comida" | sim, junto com a retirada dos botões |
| M-4 | A ordem da seção 5 | como está |
