# Mundo físico: comida no lugar, passeios que acham frutas e a bola, e atividades do Creatures 3 e de outros jogos

Status (2026-10-07):
- **DECIDIDO pelo Matheus:**
  - o jogador **deixa a comida fisicamente** no mundo, em vez de alimentar o pet direto;
  - ao **explorar**, o pet sai pelo lugar onde está e pode **encontrar comida**: a que o jogador deixou e a que o mundo faz aparecer ("caiu
    de uma árvore");
  - a **bola é um objeto físico no mapa**, pode ser encontrada nos passeios, e o pet brinca com ela;
  - o mapa é **2D e contínuo**, com regiões que passam uma para a outra como os cômodos do Creatures 3, e **não áreas fechadas**;
  - o jogador deixa a comida **arrastando e soltando** (drag and drop) no ponto do mapa 2D que quiser;
  - **Animal Crossing** e **Nintendogs** são as referências de desenho do mapa e dos passeios (seção 3);
  - a tela usa a **vista inclinada** do Animal Crossing: câmera acima e à frente do chão, objetos de pé, o fundo menor que a frente
    (protótipo visual em `docs/futuro/mundo_fisico_vistas.html`).
- **PROPOSTO:** o resto do desenho, neste documento. Não autoriza código: entra com tarefa e plano de análise, como sempre.

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

**É como o Creatures 3 faz.** As norns andam pelo mundo, acham comida, frutas e sementes, e são guiadas por cheiros (seção 4).

## 2. O desenho mínimo

### 2.1 O mapa (DECIDIDO: 2D contínuo, sem áreas fechadas)

**Um mapa 2D contínuo com regiões que passam uma para a outra.** O pet anda por qualquer ponto; as regiões têm nome e cara própria, como
os cômodos do Creatures 3, mas não têm porta nem parede entre elas. Por exemplo:

| região | o que tem |
|---|---|
| **casa** | o ninho, onde o pet dorme; um comedouro, o lugar de costume para deixar comida (não o único) |
| **jardim** | árvores que derrubam frutas ao redor do tronco |
| **campo** | espaço aberto; é onde a bola mais rola |
| **mata** | mais árvores e mais frutas, mais longe da casa; chegar lá gasta mais energia |

**Posições em inteiros.** Como todo o motor, a posição usa ponto fixo inteiro: o mapa é uma grade de células, e cada célula tem
subunidades. A distância também é inteira (por exemplo, a raiz inteira, `math.isqrt` no Python e a mesma conta em inteiros no TypeScript),
para a mesma vida dar o mesmo caminho nas duas linguagens.

**Quem anda é o motor; o cérebro escolhe para onde.** O cérebro não controla passo a passo. Ele escolhe um **alvo**, e o motor leva o pet
em linha reta, com velocidade fixa por tick e gasto de energia por distância. Assim o espaço contínuo não aumenta o número de escolhas do
cérebro, e o `AcaoPet` não ganha membro (para não quebrar a reprodução da v1).

### 2.2 O que o pet faz

Sub-decisões das ações de hoje:
- **explorar:** escolhe para onde ir: seguir o cheiro mais forte, ir a um lugar que lembra (onde já achou comida), vagar numa direção
  sorteada pela rng do pet, ou voltar para casa. No caminho, vê o que aparece;
- **comer:** vai até a comida que está vendo e come;
- **brincar:** vai até a bola que está vendo e brinca; a bola rola para outro ponto;
- **dormir:** no ninho, com conforto maior; fora dele, com menos;
- **chamar e ocioso:** como hoje.

### 2.3 O que o jogador faz

- **Deixa comida arrastando e soltando** (DECIDIDO): arrasta a comida da bandeja e solta em qualquer ponto do mapa: no comedouro, perto do
  pet, ou longe, para ele ir procurar. A comida fica ali como objeto até o pet comer ou ela estragar.
- **Deixa a bola** do mesmo jeito, ou a joga (o arremesso do Nintendogs, seção 3); a bola também aparece nos passeios.
- **Acaricia e dá tapa** como estímulos no corpo (decisão de 2026-10-07).
- **Informa e pede**, como no N5 e no N7.

**No registro, o gesto vira evento com posição inteira.** O soltar da comida vira um evento `deixar_comida(tipo, x, y)` com a posição já
arredondada para a grade. O arrasto na tela não entra no registro, só onde a comida caiu; assim a vida reproduz byte a byte.

**Onde o dono deixa a comida também é cuidado.** Deixar no comedouro, perto do pet ou longe são estilos de cuidado diferentes. Nos donos
simulados, isso vira um parâmetro da política do dono, sorteado pela rng do dono.

### 2.4 O que o mundo faz

- **As árvores derrubam frutas** de tempos em tempos, em pontos ao redor do tronco, como no Animal Crossing; mais na mata do que no jardim;
- **a árvore recarrega:** depois de derrubar, leva um tempo para dar fruta de novo;
- **a fruta apodrece** depois de um prazo, e a podre faz mal (o "manky" do Creatures);
- **a bola rola** depois de uma brincadeira, com atrito em inteiros, e para num ponto novo; às vezes some num canto e reaparece num passeio.

Todo sorteio do mundo vem da **rng de ambiente**, separada da rng do pet, como manda o projeto. O motor já guarda frutas fora do estado, com
prazo (o `MotorFrutas` do N4); a mudança é dar a cada uma uma posição.

### 2.5 O que o pet percebe, sem acesso privilegiado

- **o que está perto:** os objetos dentro de um raio de visão;
- **o que está longe:** só um **cheiro**, que enfraquece com a distância. O motor soma, em inteiros, o cheiro de cada comida que ainda não
  apodreceu; o pet sente a intensidade e a direção em que ela cresce. É uma versão simples dos cheiros que se espalham no Creatures 3; com
  poucos objetos, a soma direta é barata e exata;
- **o resto:** nada. O pet não sabe onde está tudo; aprende onde costuma achar comida.

**Reforço pelo corpo.** Achar e comer reduz a fome. Brincar com a bola reduz o tédio. A fruta podre faz mal. Andar gasta energia, mais
quanto mais longe. Para brincar e explorar compensarem de verdade, o corpo precisa dos drives de **tédio** e de **curiosidade**, além da
fome (a decisão S-3 de `docs/DECISAO_PRODUTO_SEM_ELOGIO_BRONCA.md`).

**Cuidado com a fome.** Se a comida está longe, o pet pode não chegar a tempo. A regra de fome urgente do instinto passa a levar o pet à
comida mais próxima que ele vê ou cheira. O jogador vê no mapa onde deixou a comida.

### 2.6 Na tela

**Vista inclinada (DECIDIDO, M-2).** Como no Animal Crossing: a câmera fica acima e à frente do chão, olhando inclinada. O fundo do mapa
aparece menor e mais alto, com o horizonte ao fundo; árvores, pet, ninho, comida e bola ficam de pé, cada um com sombra no chão, e o que
está mais perto da câmera é desenhado por cima. A fruta caindo e a bola quicando mostram a altura acima da sombra. O protótipo
`docs/futuro/mundo_fisico_vistas.html` mostra esta vista ao lado da vista de lado do Creatures 3, que foi descartada.

**A vista é só desenho.** O motor continua num plano 2D de posições inteiras; a projeção inclinada é feita só na web. Quando o jogador
solta a comida na tela, a web converte o ponto da tela para o ponto do chão antes de gerar o evento `deixar_comida(tipo, x, y)`. A
pesquisa no Python não depende da vista.

- **Desktop:** o mapa ocupa a área principal, com a câmera seguindo o pet; a bandeja de comida e a bola ficam na lateral, para arrastar.
- **Celular (390 px):** o mapa na tela inteira, arrastável com o dedo; a bandeja abre embaixo. Arrastar a comida e arrastar o mapa precisam
  de gestos que não se confundam (começar o arrasto na bandeja).
- **Pranchas:** não há prancha do mapa ainda; precisa de uma, desktop e 390 px, antes do código.

## 3. Referências de desenho: Animal Crossing e Nintendogs

São **inspiração de desenho, não evidência**. Servem para o jogo ter cara e ritmo conhecidos; não sustentam nenhuma afirmação da pesquisa.

| de onde | o que tem | o que o Digilab pega |
|---|---|---|
| **Animal Crossing** | mapa contínuo visto de cima; árvores frutíferas que, sacudidas, derrubam frutas ao redor do tronco; a fruta fica no chão até alguém pegar; a árvore leva dias para dar fruta de novo; às vezes cai uma colmeia, e as vespas picam; plantar uma fruta faz nascer uma árvore | o mapa 2D visto de cima; a fruta que cai ao redor da árvore; a recarga da árvore; a "praga" que pica como coisa a evitar; o cultivo, mais tarde |
| **Animal Crossing** | objetos soltos no chão são coisas físicas que se pegam e se largam | a comida e a bola como objetos com posição |
| **Nintendogs** | a caneta como mão: acariciar, jogar a bola e o frisbee, e o cão vai buscar | o arrastar e soltar como gesto do jogador; jogar a bola |
| **Nintendogs** | passeios em que o cão acha presentes pelo caminho e encontra outros cães | o passeio com achados: comida, a bola, objetos novos |
| **Nintendogs** | o cão come e bebe da tigela que o jogador enche | o comedouro como lugar de costume da comida |
| **Nintendogs** | o cão aprende truques pela voz do jogador | as palavras, mais tarde (seção 5) |

## 4. O que o Creatures 3 tem

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

## 5. Atividades para o Digilab, do Creatures 3 e de outros jogos

As referências a outros jogos são **inspiração de desenho, não evidência**. Pela regra da skill `literatura-digilab`, Digimon, Monster
Rancher e Pokémon nunca são citados como precedente.

| atividade | de onde | o que dá ao pet | risco ou custo |
|---|---|---|---|
| **Forragear:** achar frutas caídas, sementes, insetos comestíveis | Creatures 3 (fruta, semente, inseto); *Animal Crossing* (a fruta que cai ao redor da árvore) | fome; a pergunta do Charnov | energia para andar |
| **Brincar com a bola e brinquedos** que rolam e se acham | Creatures 3 (brinquedo); *Nintendogs* (jogar a bola e o frisbee); a bola da A1 | tédio | energia |
| **Evitar o que faz mal:** fruta podre, praga que pica, planta ruim | Creatures 3 (podre, praga, erva); *Animal Crossing* (a colmeia que cai da árvore) | aprender a evitar pela punição do corpo | dor, mal-estar |
| **Dispensador com botão:** empurrar o botão solta comida | Creatures 3 (botão, dispensador; ação empurrar) | aprendizado instrumental limpo: a ação causa a recompensa | o pet pode "viciar" no botão; limitar a recarga |
| **Voltar para casa** e dormir no ninho | Creatures 3 (saudade de casa, cheiro de casa, ninho) | conforto, sono melhor | ficar longe da comida |
| **Abrigo do tempo:** frio e calor por região ou hora | Creatures 3 (frio, calor, clima) | conforto | — |
| **Fugir e se aproximar:** recuar de ameaça ou multidão, chegar perto de quem gosta | Creatures 3 (recuar, aproximar; medo, aglomeração, solidão) | medo, solidão | — |
| **Passeio com achados:** o passeio traz coisas pelo caminho | *Nintendogs* (presentes no passeio) | curiosidade | — |
| **Objetos que "anunciam" o que satisfazem** | *The Sims* (autonomia por necessidades) | o pet escolhe atividade pela necessidade | — |
| **Cultivar:** semente que vira planta que dá fruta | Creatures 3 (semente, planta); *Animal Crossing* (plantar a fruta) | comida no futuro, ligada ao lugar | lento |
| **Aprender com quem observa** | *Black & White* (a criatura copia o jogador; o postmortem de 2001 está na tabela verificada) | atalho de aprendizado | ver `docs/futuro/cognicao_social.md`, 5.2 |
| **Palavras:** nomes de coisas e pedidos | Creatures 3 (computador de aprendizado); *Nintendogs* (truques pela voz) | vocabulário para a fala | outro sistema inteiro |
| **Banheiro e higiene num lugar** | *Tamagotchi*, *Digimon World* (só inspiração) | higiene | — |

## 6. Ordem recomendada

1. **O mundo físico mínimo:** o mapa 2D contínuo com as regiões, a comida arrastada e solta pelo jogador, as frutas que caem das árvores,
   a bola como objeto, explorar como deslocamento até um alvo, a visão e o cheiro. É o que resolve o pet parado.
2. **Tédio e curiosidade no corpo**, para brincar e explorar recompensarem (junto do corpo químico do Creatures 3).
3. **Fruta podre e praga**, para o pet aprender a evitar.
4. **Dispensador com botão**, para medir aprendizado instrumental limpo.
5. **Casa, ninho e saudade.**
6. **Cultivo e palavras**, por último.

## 7. Consequências para a pesquisa

- **Mundo novo na bancada.** As runs de hoje não mudam: tudo atrás de chave, com as vidas antigas reproduzindo byte a byte. `engine.py` não
  muda; o mundo entra por subclasse do motor, como as frutas e a bola.
- **A posição entra no estado e no registro.** A posição do pet, das frutas e da bola passam a fazer parte da vida; o soltar da comida entra
  no registro com posição inteira. A paridade Python × TypeScript passa a cobrir também o movimento e o cheiro.
- **Uma chance nova para o P1.** No mundo `padrao` a consequência sozinha falhou (G-P1 da validação do N3). Num mundo em que explorar
  compensa, o aprendizado pela consequência tem o que aprender: onde procurar, quando sair, o que evitar. É o teste natural para o pet sem
  botões.
- **O dono vira quem arruma o mundo.** Ele não ensina com nota: escolhe onde soltar a comida e a bola. Separar o efeito do dono do efeito do
  mundo continua sendo o cuidado de sempre, com o "só cuidado" acoplado; o lugar onde o dono solta a comida é uma variável nova do cuidado.
- **O automodelo ganha conteúdo.** "Onde costumo achar comida", "quanto me cansa ir à mata" e "esta fruta me faz mal" viram previsões que a
  rede de si pode errar e corrigir (`docs/futuro/ego_existencia.md`).

## 8. Decisões do Matheus

| # | decisão | estado ou recomendação |
|---|---|---|
| M-1 | Áreas discretas ou mapa 2D contínuo | **DECIDIDO: mapa 2D contínuo**, com regiões que passam uma para a outra como os cômodos do Creatures 3 (2026-10-07) |
| M-2 | Vista inclinada (Animal Crossing) ou de lado (Creatures 3) | **DECIDIDO: vista inclinada**, como no Animal Crossing (2026-10-07, seção 2.6; protótipo em `mundo_fisico_vistas.html`) |
| M-3 | Como o jogador deixa a comida | **DECIDIDO: arrastar e soltar** em qualquer ponto do mapa, substituindo o "alimentar" nos pets novos; os pets v1 a v10 seguem iguais (2026-10-07) |
| M-4 | Quantas regiões no começo | quatro (casa, jardim, campo, mata) |
| M-5 | A ordem da seção 6 | como está |
