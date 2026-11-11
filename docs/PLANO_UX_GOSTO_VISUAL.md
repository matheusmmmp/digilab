# PLANO_UX_GOSTO_VISUAL — o pet assistindo TV: o menu, a vista e a leitura do gosto

**Status: APROVADO pelo Matheus em 2026-11-11** ("Sim, segue a prancha", em resposta a "Aprova as dez recomendações do plano para eu
seguir para a prancha?"): as UX-GV-1 a UX-GV-10 valem pela recomendação. A prancha está em `docs/pranchas/ux-gosto-visual/`; o código só
vem depois da prancha aprovada. Os números de interface continuam PROPOSTOS, SEM FONTE. Data: 2026-11-11. Autor: Gerente da UX_TELA_PET (Claude Code, Fable 5.2), branch
`v3-ux-gosto-visual`, criado de `origin/v3-gosto-visual-tv`.

Projeto pessoal do Matheus. Nada aqui alega novidade.

**O que este plano não faz:** não muda o motor, o log, o save nem o módulo do gosto (`web/app/src/gostoVisual/gosto.ts`). Não decide
nenhuma das GV-1 a GV-14 da ideia (`docs/futuro/gosto_visual_pet.md`). Tudo continua atrás de `?gosto_visual=1`; desligado, o jogo é o
de hoje.

---

## 0. Em uma página

- **O objetivo do dono:** olhar para o pet na frente da TV e entender, sem explicação, o que ele está vendo, o que sente agora e do que
  ele gosta. E entender que o gosto é do pet, não um espelho do dono (GV-14).
- **A proposta em três papéis** (a UX-GV-1):
  - **o cantinho na ilha** é a vista principal: o pet, a TV e a reação dele, no próprio habitat;
  - **o painel da TV** é o controle e a leitura: ligar, parar, a privacidade e o gosto. Ele segue o sistema de painéis de hoje (à direita
    a partir de 900 px, uma folha baixa no celular) e toma o lugar do cartão do canto;
  - **a janela pequena** é a companhia quando o jogo sai de vista: só o pet, a reação, uma linha e dois botões.
- **A TV vira um lugar da ilha** (a UX-GV-2): tocar na TV abre o painel, como o saco, o portão e a barraca. Não entra item novo na
  navegação.
- **A leitura do gosto em dois níveis** (a UX-GV-4): primeiro uma frase ("Gosta mais de cores fortes e som calmo"); um toque abre o
  porquê, com três origens que têm nome de jogo e forma própria: **de nascença**, **de tanto ver** e **do carinho**. O que passa agora
  fica numa faixa separada, só com a TV ligada.
- **A TV aparece em três quartos** (a UX-GV-3): hoje a tela fica de lado para a câmera. A recomendação é girar a TV para a tela aparecer
  e o pet continuar de perfil.
- **A privacidade em uma olhada** (a UX-GV-6): a TV do jogo é o botão principal; a tela do dono é o segundo, com uma frase fixa antes
  de ligar e um selo com o botão Parar enquanto a captura dura.
- **As decisões abertas** são 10, da UX-GV-1 à UX-GV-10 (seção 9), cada uma com a recomendação e o custo de errar.

---

## 1. O ponto de partida

### 1.1 O que existe (PRs empilhados, fora da main)

- **O P0 (#805):** o cartão "TV do pet" no canto inferior esquerdo (`GostoVisual.tsx`), com:
  - quatro botões: Mostrar minha tela, Ligar a TV do jogo, Fazer carinho e Janela pequena;
  - o palco com o pet e o balão da reação;
  - as frases "Gosta mais de" e "De nascença";
  - o tempo assistindo junto e a contagem de carinhos;
  - sete barras (cor, brilho, movimento, detalhe, volume, ritmo, timbre), cada uma com três marcas (nascença, hoje, agora);
  - a janela pequena flutuante de 360 × 620 (`janelaPequena.ts`).
- **O cantinho (#820):** um tapete e duas almofadas na frente da TV de tubo do #814 (`ilha/cantinhoTv.ts`). Com a TV ligada, o pet
  desenhado anda até a almofada, senta e olha. As reações mudam a pose, e o balão fica sobre ele. A tela mostra a captura ou os programas
  sintéticos.
- **Os dados que a interface tem hoje** (princípio 1 do guia: só mostrar o que existe):
  - o inato por componente, o ponto ótimo e a largura (`gosto.ts`, `inatoDaSemente`);
  - o estado aprendido: os desvios por componente, os segundos juntos e os carinhos (`EstadoGosto`);
  - a leitura do segundo: agrado, interesse, novidade, vontade, olhando e a reação (`Leitura`);
  - as seis reações: adorando, olhando, enjoou, não gosta, curioso e distraído (`Reacao`, com o texto em `estadoTv.ts`, `BALAO`);
  - a origem (a tela ou a TV do jogo) e o nome do programa (`estadoTv.ts`).
- **O que não existe:** o histórico do gosto no tempo. O P0 guarda só o estado de agora. O plano não desenha gráfico de evolução (a
  UX-GV-9).

### 1.2 Os problemas vistos

| nº | o problema | onde o plano responde |
|---|---|---|
| 1 | O cartão cobre o HUD no canto e não segue o sistema de painéis. | seções 2 e 3 (o painel da TV) |
| 2 | A tela da TV aparece de lado para a câmera. | seção 6 (a UX-GV-3) |
| 3 | No celular, o balão fica pequeno, às vezes sob o emote do jogo, e o toque erra o pet sentado. | seções 5 e 7 |
| 4 | No cartão, o balão do "não curti" aparece espelhado com o pet. | seção 5.3 |
| 5 | As sete barras com três marcas são densas, e as origens do gosto não ficam claras. | seção 4 |
| 6 | Há três vistas do mesmo pet sem papel definido. | seção 2 (a UX-GV-1) |
| 7 | A privacidade não se entende em uma olhada. | seção 3.2 (a UX-GV-6) |

Outros problemas que a leitura do P0 mostrou:

| nº | o problema | onde o plano responde |
|---|---|---|
| 8 | "Mostrar minha tela" é o botão forte, e a TV do jogo é o fraco. A GV-1 recomenda o contrário. | seção 3.2 |
| 9 | "Fazer carinho" do cartão não é o Carinho do jogo. O dono tem dois carinhos e não sabe a diferença. | seção 3.4 (a UX-GV-7) |
| 10 | "Hoje" soma a nascença, a exposição e o carinho numa marca só. A GV-14 pede as partes separadas. | seção 4 |
| 11 | O contador "carinhos: N" ao lado do gosto sugere uma pontuação. O jogo não premia acertar o gosto. | seção 4.4 |
| 12 | A reação só existe como texto visual no balão. O leitor de tela a recebe a cada segundo ou não a recebe. | seção 8 |

---

## 2. A arquitetura da informação

### 2.1 O papel de cada vista (a UX-GV-1)

| vista | o papel | o que mostra | o que não mostra |
|---|---|---|---|
| **o cantinho na ilha** | ver o pet reagindo | o pet sentado, a TV com a imagem, a pose e o sinal da reação | botões, barras, texto longo |
| **o painel da TV** | controlar e entender | ligar e parar, a privacidade, a frase do gosto, o porquê | outro desenho do pet (ele já está à esquerda, na ilha) |
| **a janela pequena** | fazer companhia fora do jogo | o pet, a reação, uma linha do gosto, Carinho e Parar | as barras e o porquê |

- **O cartão do canto sai.** O que ele tinha vai para o painel da TV. O palco do cartão (a segunda imagem do pet) só continua na
  janela pequena, onde a ilha não aparece.
- **Por que assim:** a regra do layout diz que nada cobre o pet na tela Pet, e que a informação secundária mora em painéis
  (`docs/UI_GUIDELINES.md`, §8). Duas imagens do mesmo pet na mesma tela obrigam o dono a escolher para onde olhar. SEM FONTE para o
  efeito medido; é a regra da casa.

### 2.2 O que fica sempre visível e o que fica a um toque

| nível | com a TV desligada | com a TV ligada |
|---|---|---|
| **sempre, na ilha** | a TV e o cantinho, como um lugar | o pet sentado, a imagem na TV, a pose e o sinal da reação |
| **sempre, no painel aberto** | os dois botões de ligar e a frase da privacidade | o que está passando, a reação em palavras, a frase do gosto, Parar |
| **a um toque** | "Do que ele gosta" (a frase e o porquê) | "Por quê" (as origens por componente) e "O que está passando" (os números de agora) |
| **a dois toques** | — | o painel do DigiBrain, quando o P1 levar o gosto para o cérebro (seção 4.5) |

### 2.3 A entrada (a UX-GV-2)

- **A TV é um lugar da ilha.** Tocar na TV ou no cantinho abre o painel da TV, pelo mesmo caminho do toque nos lugares
  (`ToqueLugar.tsx`): no desktop o clique, e no celular o toque.
- **Pelo teclado:** o toque nos lugares é só pelo ponteiro, e os outros lugares têm o item da navegação como caminho de teclado. A TV
  não tem. Por isso entra um botão "TV" na pilha da direita (a partir de 900 px) e entre os botões quadrados da borda (no celular), só
  com a chave ligada. Ele também resolve o dono que não achou a TV na ilha.
- **Sem item novo no trilho nem na barra de baixo.** A navegação continua com Pet, Crescer, Lutar e Diário.
- **No minimapa** (só no desktop), a TV ganha um ponto, como os outros lugares.
- **Com a chave desligada**, a TV continua o enfeite do #814: sem toque, sem painel e sem ponto no minimapa.

---

## 3. Os fluxos

### 3.1 Ligar a TV do jogo

1. O dono toca na TV. A câmera vai ao cantinho (a viagem dos lugares, `src/viagem.ts`), e o painel abre.
2. O painel mostra dois botões. **"Ligar a TV"** é o principal.
3. O dono liga. O pet anda até a almofada, senta e olha. O painel passa a mostrar o que está passando ("TV do jogo, desenho animado").
4. A reação aparece no pet (seção 5) e, em palavras, no painel.

### 3.2 Compartilhar a tela (a UX-GV-6)

1. No painel, o segundo botão é **"Mostrar minha tela"**.
2. Antes do seletor do navegador, o painel mostra a frase fixa da privacidade, sempre no mesmo lugar:
   > Ele só sente cores, brilho, movimento e som: sete números por segundo. Nenhuma imagem é guardada e nada sai deste computador.
3. O dono confirma. O Chrome abre o seletor dele (a aba, a janela ou a tela, e a caixa do áudio). O jogo não imita nem cobre esse
   seletor.
4. Se o dono cancela no seletor, o painel volta ao passo 1, sem mensagem de erro.
5. Durante a captura, um **selo** fica visível nas três vistas: "Vendo a sua tela" e o botão **Parar**. O selo usa a forma do chamado
   (posição fixa e texto), sem piscar.
6. Se o dono não marcou o áudio, uma linha diz: "Ele não está ouvindo. Para ouvir, compartilhe de novo e marque o áudio."
7. Onde o navegador não deixa capturar (o navegador do app, o Firefox, o celular), o botão "Mostrar minha tela" some e fica só a TV
   do jogo. Nada de botão que falha ao clicar.

**Por que a TV do jogo primeiro:** a GV-1 recomenda começar por ela, e ela não tem risco de privacidade. No P0 a ordem está invertida.

### 3.3 Abrir a janela pequena

1. No painel, com a TV ligada, o botão **"Janela pequena"** aparece no rodapé. Com a TV desligada ele não aparece: sem TV, a janela
   não tem o que mostrar.
2. A janela abre (360 × 620, a do P0) com o pet, a reação, a linha "Gosta mais de", o selo da captura e dois botões: Carinho e Parar.
3. Na página, o painel mostra "Ele está na janela pequena" e o botão "Trazer de volta". A ilha continua mostrando o pet no cantinho.
4. Fechar a janela pequena não para a TV. Parar a TV fecha a janela pequena.
5. Onde a janela flutuante não existe (fora do Chrome e do Edge no desktop), o botão não aparece.

### 3.4 Fazer carinho durante a exibição (a UX-GV-7)

- **Um carinho só.** A recomendação é que o carinho da TV seja o Carinho do jogo: o botão do dock ou o toque no pet. O módulo do gosto
  só observa que houve um carinho enquanto o pet olhava. O botão "Fazer carinho" do cartão sai.
- **Por quê:** é o desenho do P1 (o carinho mexe no corpo, e o cérebro credita a mudança ao que o pet olhava; `ESPEC_GOSTO_VISUAL_P1`,
  seção 5.3), e o dono não precisa aprender dois carinhos.
- **O retorno:** o pet reage ao carinho como sempre. No painel, a origem "do carinho" pulsa uma vez (sem pulso com movimento reduzido).
- **Na janela pequena**, o botão Carinho chama a mesma ação.
- **O custo:** o carinho do jogo entra no log, e hoje o do cartão não entra. É a regra de "o treino nunca vem só de clicar carinho" que
  pede cuidado: aqui o carinho é a ação de sempre, com o efeito de sempre, e a associação com a TV é só do protótipo.

### 3.5 Desligar

- **Parar** fica visível no painel, no selo e na janela pequena.
- Fechar o painel (o "×" ou o Esc) **não** desliga a TV: o pet continua assistindo, e o selo continua na tela. O dono pode cuidar do pet
  com a TV ligada.
- Parar o compartilhamento pela barra do próprio Chrome também desliga, com a mesma volta.
- Desligada, o pet levanta e volta para onde o motor diz, e a imagem some da TV.

---

## 4. A leitura do gosto em linguagem de jogo (a UX-GV-4 e a UX-GV-5)

### 4.1 O nível 1: uma frase

- **"Gosta mais de: cores fortes e som calmo."** É a frase de hoje (`gostaMaisDe`), calculada só do total, como pede a GV-14.
- **Uma segunda linha, só quando difere:** "De nascença, preferia cores suaves." Se o gosto de hoje é o de nascença, a linha não
  aparece.
- **Sem número.** O agrado e o interesse não viram porcentagem na frase.

### 4.2 O nível 2: o porquê, com três origens

Um toque em "Por quê" abre a lista por componente. Cada linha tem um trilho só, com os dois extremos escritos (por exemplo "suave" e
"forte"), e até três marcas com forma própria:

| a origem | o nome na tela | a forma (sem cor nova) | de onde vem o dado |
|---|---|---|---|
| o inato | **de nascença** | um traço vertical sólido, fixo | `inato.otimo` |
| a exposição | **de tanto ver** (ou "de tanto ouvir") | uma seta pontilhada que sai da nascença | o desvio da exposição |
| a consequência | **do carinho** | a malha ciano tracejada, a marca do "aprendido com o dono" (§3 do guia) | o desvio do carinho |

- **O ponto de hoje** é o fim das setas: um losango, com o rótulo "hoje".
- **O P0 já guarda as duas parcelas separadas** (`EstadoGosto.exposicao` e `EstadoGosto.carinho`, em `gosto.ts`); só a tela as soma na
  marca "hoje". Mostrar as duas origens não muda o módulo nem o gosto já guardado (a UX-GV-5). *Corrigido em 2026-11-11: a primeira
  versão deste plano dizia que o módulo somava as duas.*
- **Menos linhas:** por padrão aparecem só os componentes em que o pet tem um gosto marcado ou em que o gosto mudou. "Ver todos" abre os
  sete, em dois grupos: **Imagem** (cor, brilho, movimento, detalhe) e **Som** (volume, ritmo, timbre). Sem som na captura, o grupo Som
  diz "ele não está ouvindo" em vez de barras vazias.
- **Os nomes:** "detalhe" fica; "timbre" vira "som grave ou agudo"; "ritmo" vira "som parado ou agitado". Nada de "vetor", "agrado" ou
  "habituação" na tela.

### 4.3 O que passa agora, separado

- **Uma faixa própria, "O que está passando",** só com a TV ligada: as mesmas linhas, com um ponto que anda (o "agora" do P0).
- **Fora da lista do gosto.** No P0 o "agora" divide o trilho com a nascença e o hoje, e o dono lê três marcas sem saber qual é dele,
  qual é do pet e qual é da tela. Separadas, a lista de cima é o pet e a faixa de baixo é a tela.
- **A ponte entre as duas** é a reação em palavras: "Está adorando: tem as cores de que ele gosta." A frase usa só o componente que
  mais pesou na leitura do segundo.

### 4.4 O que a tela não faz (a GV-14)

- **Não pontua.** Sai o contador "carinhos: N" de perto do gosto. O tempo junto continua ("Assistiram juntos: 2 h 10 min"), porque é
  companhia e não acerto.
- **Não comemora o acerto.** O "adorando" não ganha confete, som de prêmio, moeda, feito nem medalha.
- **Não compara o dono com o pet.** Nada de "vocês combinam" ou "igual a você".
- **Não pede ao dono para escolher entre dois programas pelo pet.** A comparação por pares feita pelo dono está fora (a ideia, seção 6).
- **Diz de quem é.** O título da leitura é "Do que o Agumon gosta" (o nome da forma, como manda o `web/app/CLAUDE.md`), e a origem "de
  nascença" aparece primeiro.

### 4.5 A conversa com o DigiBrain e com o paladar

- **Hoje (o P0):** o gosto mora fora do motor. A leitura fica só no painel da TV, com um aviso discreto de protótipo.
- **Com o P1:** o gosto entra no cérebro e no corpo (o `GenomaVisao`, o órgão da tela, o P1 e o P2 do M-PLAST). A leitura completa passa
  a morar no painel do DigiBrain, ao lado do paladar, com a mesma gramática: o inato fixo e o aprendido separado. O painel da TV fica
  com a frase e um atalho "ver no DigiBrain".
- **A mesma gramática do paladar:** as três origens, as três formas e os mesmos nomes. O dono que aprendeu a ler o gosto pela comida lê
  o gosto pela TV sem aprender de novo.
- **O hábito** (quando ele costuma olhar) é a terceira parte do aprendido no P1. Este plano reserva uma linha para ele no DigiBrain e
  não a desenha, porque o dado ainda não existe.

---

## 5. As reações do pet

### 5.1 Uma reação, três sinais

| a reação | a pose no cantinho (já no #820) | o sinal sobre o pet | em palavras, no painel |
|---|---|---|---|
| adorando | pula de leve | um coração | "Está adorando" |
| olhando | sentado, de frente para a TV | nenhum | "Está assistindo" |
| curioso | inclina a cabeça | uma interrogação | "Ficou curioso" |
| enjoou | vira para o outro lado | um bocejo ("…") | "Enjoou disso" |
| não gosta | vira para o outro lado | um "x" | "Não curtiu" |
| distraído | olha em volta | nenhum | "Não está prestando atenção" |

- **A pose é o sinal principal.** Ela se lê de longe e no celular, onde o balão de texto fica pequeno.
- **O sinal sobre o pet é um ícone, não um balão de texto.** Ele usa o mesmo desenho e o mesmo lugar dos emotes de hoje (`reacao.ts`).
- **As palavras ficam no painel** e no leitor de tela (seção 8).

### 5.2 A fila: um sinal por vez

- **A ordem de quem aparece:** o chamado do pet, depois a fala do jogo, depois o emote do jogo, e só então o sinal da TV.
- **Quando o jogo mostra um emote ou uma fala, o sinal da TV espera.** A pose continua, e é ela que segura a leitura.
- **O sinal da TV só muda quando a reação muda,** e fica no mínimo 3 s (PROPOSTO, SEM FONTE). No P0 a leitura é por segundo, e o balão
  pode trocar a cada segundo.

### 5.3 O que muda no 3D e na janela pequena

- **No 3D:** sai o balão de texto sobre o pet; entra o ícone no lugar dos emotes. A pose fica.
- **Na janela pequena:** o balão de texto fica, porque ali há espaço e não há emote do jogo. O balão sai de dentro do elemento que
  espelha o pet, e o "não curti" deixa de aparecer invertido (o problema 4).
- **O toque no pet sentado** (o problema 3): a área de toque é a da almofada inteira, com pelo menos 44 px, e não só a do sprite.

---

## 6. A câmera e o enquadramento do cantinho (a UX-GV-3)

- **O problema:** a TV do #814 olha para a praça, e na ilha com água isso dá o oeste. A câmera olha do sul. O dono vê a TV de lado e
  não vê a imagem.
- **As três saídas:**

| a saída | o que o dono vê | o custo |
|---|---|---|
| **(a) girar a TV para o sul** | a tela de frente e o pet de costas | a reação do pet some: ele é um sprite de papel, e de costas não há rosto |
| **(b) girar a câmera ao abrir o lugar** | a tela de frente, com a câmera vindo do oeste | a câmera da ilha não gira hoje (só anda e aproxima); é uma mecânica de câmera nova, e o resto da ilha fica de lado |
| **(c) a TV em três quartos** | a tela em três quartos e o pet de perfil, olhando para ela | muda o giro de um enfeite; a almofada e o tapete acompanham |

- **A recomendação é a (c):** a TV gira cerca de 40° para o sul (PROPOSTO, SEM FONTE), e o cantinho gira junto. O pet de perfil é a
  pose que o sprite já tem. Ao abrir o lugar, a câmera só anda até o cantinho e aproxima, como nos outros lugares.
- **A pergunta ao Matheus:** o giro novo vale sempre ou só com a chave ligada? A recomendação é valer sempre: é só vista, e uma TV que
  muda de giro conforme um parâmetro da página confunde. O custo é a ilha de hoje mudar um enfeite de posição sem a chave.
- **O enquadramento com o painel aberto:** a partir de 900 px o painel ocupa a direita, então a câmera centra o cantinho na parte livre
  à esquerda, como a viagem dos lugares já faz. No celular, a câmera centra o cantinho acima da folha.

---

## 7. Desktop e celular juntos

**Tokens e componentes:** só os que existem. O painel usa a pele dos menus (`--hx-*`, `hx-painel`, `hx-btn`, `hx-medidor`, `hx-aba`).
O sinal sobre o pet e o balão da janela pequena usam os do habitat (`--dl-*`). A marca "do carinho" usa `--dl-learned` sobre
`--dl-learned-bg`. Nenhuma cor hex nova e nenhuma fonte nova. As classes `gv-*` do P0 saem junto com o cartão, menos as da janela
pequena.

### 7.1 A 1440 px (e de 900 px para cima)

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│ [◉ Agumon ROOKIE]        [● Vendo a sua tela  ■ Parar]        [D3 07:42]                 │
│ ┌────┐                                              ┌ TV ───────────────────────────  × ┐│
│ │Pet │                                              │ Passando: a sua tela              ││
│ │Cre │            ♥                                 │ Está adorando: tem as cores de    ││
│ │Lut │          (pet)   ┌──────┐                    │ que ele gosta.                    ││
│ │Diá │        ~almofada~│  TV  │                    │ [■ Parar]        [Janela pequena] ││
│ ├────┤       ~~ tapete ~└──────┘                    ├ Do que o Agumon gosta ────────────┤│
│ │Con │                                              │ Gosta mais de: cores fortes e som ││
│ │Aju │                                              │ calmo.                            ││
│ └────┘                                              │ De nascença, preferia cores suaves││
│                                                     │ ▸ Por quê                         ││
│                                                     │   Cor   suave ─┃┄┄┄▷▒▒◆── forte   ││
│                                                     │   Som   calmo ─◆┃──────── agitado ││
│                                                     │   ┃ de nascença ┄▷ de tanto ver   ││
│                                                     │   ▒ do carinho  ◆ hoje            ││
│                                                     │ ▸ O que está passando             ││
│                                                     ├───────────────────────────────────┤│
│                                                     │ Assistiram juntos: 2 h 10 min     ││
│                                                     │ Ele só sente cores, brilho,       ││
│                                                     │ movimento e som. Nada é guardado. ││
│      [Alimentar][Brincar][Limpar][Carinho][Tapa][Tratar][Mais]                           │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

- **O painel** tem a largura dos painéis grandes de hoje. A ilha fica escurecida só de leve, porque aqui o pet é o assunto.
- **Em 900 px** o painel é o mesmo, mais estreito; a lista do porquê mostra uma linha por componente, sem a legenda lado a lado.
- **A pilha da direita** (Estado, Evolução, Últimas ações) sai enquanto o painel da TV está aberto, como com os outros painéis grandes.
- **O dock continua visível:** o Carinho do jogo é o carinho da TV (seção 3.4).

### 7.2 A 390 px

```
┌──────────────────────────────┐
│ [◉]  [● Vendo a tela ■ Parar]│
│                              │
│            ♥                 │
│          (pet)  ┌────┐       │
│        ~almof.~ │ TV │       │
│                 └────┘       │
│                              │
├ TV ─────────────────────── × ┤
│ Está adorando: tem as cores  │
│ de que ele gosta.            │
│ Gosta mais de: cores fortes  │
│ e som calmo.          [mais ▴]│
├──────────────────────────────┤
│ [Alim][Brin][Limp][Cari][Mais]│
└──────────────────────────────┘
```

- **Uma folha baixa em vez do modal centralizado.** A regra de hoje abaixo de 900 px é o modal sobre o habitat escurecido, mas aqui o
  modal cobriria o pet, que é o assunto. A folha recolhida mostra duas linhas (a reação e o gosto) e cabe acima do dock. "Mais" a
  estica até cerca de metade da tela (PROPOSTO, SEM FONTE; o precedente é a folha dos lugares), com o porquê e a privacidade.
- **É um desvio da regra do layout,** e por isso é a UX-GV-8.
- **Sem a janela pequena e sem "Mostrar minha tela"** no celular: o navegador não tem nenhuma das duas. Fica só a TV do jogo.
- **Alvos de toque de 44 px** em tudo, e a folha respeita o `env(safe-area-inset-bottom)`.

### 7.3 A janela pequena (360 × 620)

```
┌──────────────────────────┐
│ ● Vendo a sua tela       │
│                          │
│    ╭ Está adorando ╮     │
│    ╰──────╮────────╯     │
│         (pet)            │
│                          │
│ Gosta mais de: cores     │
│ fortes e som calmo.      │
│                          │
│ [ Carinho ]   [ ■ Parar ]│
└──────────────────────────┘
```

- **Sem barras, sem o porquê e sem rolagem.** Quem quer entender volta ao painel.
- **A janela é sempre escura** (a pele dos menus), para não disputar com o que o dono está assistindo.

---

## 8. A acessibilidade

- **O contraste:** os da seção 4.1 do guia; os tokens usados já os cumprem. O selo da captura e o texto da privacidade usam o texto
  principal, não o esmaecido.
- **Nada só por cor:** as três origens diferem pela forma (o traço sólido, a seta pontilhada, a malha tracejada) e pelo nome escrito.
  As seis reações diferem pela pose, pelo ícone e pelo texto.
- **O foco:** ao abrir, o foco vai ao título do painel; o Esc fecha e devolve o foco ao botão "TV"; a ordem de tabulação é
  a visual. A folha do celular e a janela pequena seguem a mesma regra.
- **O teclado:** o botão "TV" da pilha abre o painel (seção 2.3); Parar é sempre um botão com foco; nada depende do hover.
- **O leitor de tela, as reações:** uma região `role="status"` (educada) no painel, que anuncia só quando a reação muda, e no máximo
  uma vez a cada 5 s (PROPOSTO, SEM FONTE). O ícone sobre o pet é decorativo (`aria-hidden`), porque o painel já diz o mesmo.
- **O leitor de tela, o gosto:** cada linha do porquê é uma frase, não uma barra muda. Por exemplo: "Cor: de nascença, suave. Hoje,
  forte. Mudou de tanto ver e com o carinho." A faixa do agora não é anunciada a cada segundo; ela tem um resumo sob pedido.
- **O leitor de tela, a captura:** ligar e parar a captura são anunciados uma vez ("O pet está vendo a sua tela", "A TV foi desligada").
- **O movimento reduzido:** sem o pulinho do "adorando", sem o pulso do carinho e sem a viagem de câmera (corte). O ponto do "agora"
  salta em vez de deslizar. A imagem na TV continua, porque é o conteúdo.
- **O texto a 200 %:** o painel rola por dentro; a folha recolhida mantém as duas linhas e corta com reticências só a segunda.
- **A imagem da tela na TV:** ela é decorativa para o leitor de tela (`aria-hidden`); o que importa já está no "Passando".

---

## 9. As decisões (APROVADAS pela recomendação em 2026-11-11)

Todas valem pela recomendação. Nenhum número daqui é de jogo; os de interface são PROPOSTOS, SEM FONTE.

| id | a decisão | a recomendação | o custo de errar |
|---|---|---|---|
| **UX-GV-1** | O papel das três vistas. | O cantinho é a vista, o painel da TV é o controle e a leitura, a janela pequena é a companhia. O cartão do canto sai. | Mantendo o cartão, o HUD continua coberto e o pet aparece duas vezes. Tirando o cartão, quem usa o P0 sem a ilha 3D (a reserva sem WebGL) perde o palco: o painel precisa de um palco pequeno nesse caso. |
| **UX-GV-2** | A entrada: a TV como lugar da ilha. | Sim, pelo toque na TV, mais um botão "TV" na pilha para o teclado; sem item novo na navegação. | Só com o toque, o teclado não chega à TV e o dono novo pode não a achar. Um item na navegação resolveria isso, mas incha o trilho por causa de um protótipo. O botão na pilha é mais um elemento no HUD. |
| **UX-GV-3** | O giro da TV. | A TV em três quartos, cerca de 40° para o sul, valendo sempre. | Com a TV de frente, o pet fica de costas e a reação some. Com o giro só atrás da chave, a ilha tem duas formas. Valendo sempre, a ilha de hoje muda um enfeite sem a chave. |
| **UX-GV-4** | A leitura do gosto em dois níveis. | A frase primeiro; o porquê a um toque; o agora numa faixa separada. | Com tudo aberto, volta a densidade do P0. Com o porquê escondido demais, o dono lê só "gosta de X" e conclui que foi ele quem ensinou (o risco da GV-14). |
| **UX-GV-5** | As origens separadas: "de tanto ver" e "do carinho". | Separar na tela; o módulo do protótipo já guarda as duas parcelas. | Sem separar, a tela não cumpre a GV-14. Separando, são mais marcas por linha, e a leitura fica densa se as duas setas forem pequenas. |
| **UX-GV-6** | A privacidade: a ordem dos botões, a frase e o selo. | A TV do jogo como botão principal; a frase fixa antes do seletor; o selo com Parar nas três vistas. | Com a tela do dono como botão principal, o primeiro clique de quem chega já pede a captura. Com avisos demais, o dono para de ler. |
| **UX-GV-7** | O carinho da TV é o Carinho do jogo. | Sim, um carinho só. | Unindo, o carinho dado na frente da TV entra no log e mexe no pet de verdade; o dono pode dar carinho só para puxar o gosto. Mantendo dois, o dono não sabe a diferença, e o P1 vai unir de qualquer jeito. |
| **UX-GV-8** | No celular, a folha baixa em vez do modal. | A folha, recolhida em duas linhas. | É um desvio da regra do layout de 2026-10-30. Com o modal da regra, o pet fica coberto na única tela em que ele é o assunto. |
| **UX-GV-9** | A evolução do gosto no tempo. | Fora desta etapa: mostrar só "de nascença" e "hoje". O histórico entra quando o P1 tiver o dado. | Um gráfico agora exigiria guardar uma série no navegador, que é mais estado derivado da tela do dono (a GV-10). Sem ele, a mudança lenta do gosto passa despercebida. |
| **UX-GV-10** | As reações: o ícone no lugar do balão de texto no 3D, a fila e o mínimo de 3 s. | Sim às três. | Com o balão de texto, continua a colisão com os emotes e a leitura ruim no celular. Com o ícone só, a diferença entre "enjoou" e "não curtiu" depende do painel aberto. |

---

## 10. O custo em determinismo e em e2e

- **Determinismo:** nenhum. Nada entra no motor, no log nem no save. A única ligação nova com o jogo é a UX-GV-7: se aprovada, o módulo
  do gosto passa a **ler** que houve um carinho; ele não escreve nada.
- **A chave:** tudo atrás de `?gosto_visual=1`, menos o giro da TV, se a UX-GV-3 valer sempre. Um teste confere que, desligada, a tela é
  a de hoje.
- **Os testes de hoje que mudam** na etapa de código: `gosto_visual_p0.test.ts` (o cartão sai) e `gosto_visual_tv.test.ts` (o giro e o
  balão). Se a UX-GV-3 valer sempre, mudam também os que conferem o giro da TV na grade.
- **Os e2e novos** (na etapa de código): abrir o painel pela TV; ligar a TV do jogo e ver o pet ir ao cantinho; fechar o painel com a
  TV ligada; parar; a folha a 390 px; o movimento reduzido. A captura da tela real não entra no e2e, porque o seletor é do navegador.
- **Os revisores da frente:** `rev-a11y` no painel e na folha, `rev-cena` no cantinho com o painel aberto e fechado, e `rev-replay` para
  conferir que nada entrou no registro.

---

## 11. As etapas depois deste plano

1. **O ok do Matheus** às UX-GV-1 a UX-GV-10.
2. **A prancha** (pelo `ux-designer`), com o painel a 1440, a 900 e a 390, a janela pequena e o cantinho em três quartos, nas duas
   peles.
3. **O ok do Matheus** à prancha.
4. **O código** (pelo `ux-implementador`), numa etapa por vista: o painel e a entrada, o cantinho e as reações, a janela pequena.
5. **A conferência** pelo `ux-browser-tester` e pelos revisores.

---

## 12. As referências

Só as verificadas da ideia (`docs/futuro/gosto_visual_pet.md`) e da nota do vault `BUSCA_GOSTO_VISUAL_2026-11-10.md`. Este plano não
verificou nenhuma fonte nova.

| o que o plano usa | a fonte |
|---|---|
| A exposição desloca o gosto ("de tanto ver"). | Zajonc 1968, `10.1037/h0025848` |
| A consequência dá valor ao que veio antes ("do carinho"), por analogia com o paladar. | Provenza 1995, `10.2307/4002498`. SEM FONTE para a mesma associação com imagens num agente. |
| O novo puxa o olhar, e o semifamiliar fica com o agrado ("curioso" e "enjoou" são coisas diferentes de "gosta"). | Gustafsson et al. 2021, `10.3758/s13420-021-00484-3` |
| O dono é quem informa o que o animal vê e gosta, o que mostra o tamanho do risco da GV-14. | Montgomery et al. 2025, `10.1038/s41598-025-06580-y` |
| A comparação por pares feita pelo dono ensina o gosto do dono. | Christiano et al. 2017 (já no projeto) |
| A tela é a maior fonte de vazamento de informação privada nas câmeras vestíveis. | Korayem et al. 2016, `10.1145/2858036.2858417` |
| O estado derivado também é dado privado. | Chung e Badhe 2026, arXiv:2606.10173 (preprint) |

**SEM FONTE** (escolhas de desenho deste plano, pelas regras da casa e não pela literatura):
- os dois níveis da leitura e a faixa separada do agora;
- as três formas das origens e os nomes "de tanto ver" e "do carinho";
- o ícone no lugar do balão, a fila dos sinais e o mínimo de 3 s;
- a folha baixa no celular e os tamanhos;
- a TV em três quartos e os 40°;
- a frase da privacidade e o selo;
- o intervalo de 5 s do leitor de tela.

---

## 13. A etapa 1 do código: o painel da TV e a entrada (2026-11-11, Gerente da UX_TELA_PET, Claude Code, Fable 5.2, branch `v3-ux-gosto-visual-c1`)

**O que mudou** (tudo atrás de `?gosto_visual=1`):
- **O cartão do canto saiu** (UX-GV-1). O estado dele foi para a sessão da TV (`web/app/src/gostoVisual/sessaoTv.ts`), fora dos componentes,
  porque o painel fecha e a TV continua ligada.
- **O painel da TV** (`PainelTv.tsx`) abre pelo sistema de painéis da tela Pet: a linha "TV" na pilha a partir de 900 px, e o item "TV" no
  leque do retrato abaixo disso (UX-GV-2). No celular ele é uma folha baixa, recolhida em duas linhas, com o "Mais" (UX-GV-8).
- **A ordem dos botões** (UX-GV-6): "Ligar a TV" é o principal. "Mostrar minha tela" e a frase da privacidade só aparecem onde o navegador
  captura. Cancelar no seletor do Chrome não mostra erro.
- **O selo da captura** fica fixo no topo enquanto a tela do dono é lida, com o Parar.
- **A leitura em dois níveis** (UX-GV-4 e 5): a frase "Gosta mais de"; "De nascença, preferia…" só quando difere; o porquê com as três
  origens separadas (`leituraGosto.ts`), a lista curta e o "Ver todos" em Imagem e Som; "O que está passando" numa faixa à parte.
- **O motivo na frase da reação** (a PR-3): `motivoDaReacao` devolve o componente que mais pesou ("tem as cores de que ele gosta") ou o
  que mais atrapalhou ("as cores são vivas demais para ele").
- **Um carinho só** (UX-GV-7): o botão "Fazer carinho" e a contagem de carinhos saíram. A sessão lê quando foi o último Carinho do jogo
  (`ultimoCarinhoEm`, em `telas/pet/reacao.ts`, só vista) e não escreve nada no motor.
- **O leitor de tela:** uma região de status diz a TV ligando e desligando, e a reação quando ela muda, no máximo uma vez a cada 5 s.

**Os testes:** `web/app/test/gosto_visual_painel.test.ts` (13 testes) e `web/app/e2e/gosto_visual_painel.spec.ts` (2 testes).

**Não feito nesta etapa:**
- o toque na TV da ilha, o ícone no lugar do balão, a fila dos sinais e o giro da TV: são da etapa 2 (o cantinho e as reações);
- a janela pequena nova: é da etapa 3. Hoje ela abre com a vista antiga do P0, com o Carinho do jogo e o Parar;
- a câmera indo ao cantinho ao abrir o painel (etapa 2);
- com "Exibir detalhes do pet" desligado, a pilha some no desktop e a linha "TV" vai junto;
- nenhum revisor (`rev-a11y`, `rev-cena`, `rev-replay`) viu a etapa, e o contraste não foi medido.

Os desvios estão em `docs/registro/2026-11.md`, D-UXGV-14 a 18.

---

## 14. A etapa 2 do código: o cantinho e as reações (2026-11-11, Gerente da UX_TELA_PET, Claude Code, Fable 5.2, branch `v3-ux-gosto-visual-c2`)

**O pedido do Matheus (2026-11-11):** "Sim, segue a etapa 2".

**O que mudou:**
- **A TV em três quartos** (UX-GV-3): a frente da TV fica a 40° do sul, virada para o lado do meio da ilha (`TV_TRES_QUARTOS`, em
  `ilha/constantes.ts`; a conta em `ilha/grade.ts`). Vale sempre, com ou sem a chave. O cantinho gira junto, porque nasce do giro da TV.
- **O toque na TV abre o painel** (UX-GV-2): `gostoVisual/ToqueTv.tsx`, com o mesmo gesto do toque nos lugares. A área de toque tem pelo
  menos 44 px. O toque na TV é dela, e a barraca atrás não abre. Com o mouse, o cursor vira a mão.
- **O ícone no lugar do balão** (UX-GV-10): o balão de texto saiu do 3D. O sinal é um ícone das grades do jogo, sobre a cabeça do pet:
  o coração (adorando), a interrogação (curioso), as reticências (enjoou) e o "x" (não curtiu). "Assistindo" e "distraído" ficam só
  na pose.
- **A fila e o mínimo de 3 s** (`gostoVisual/sinalTv.ts`): o emote do jogo, a fala e o chamado do pet passam na frente. O sinal só troca
  depois de 3 s na tela.
- **A câmera vai ao cantinho** com o painel da TV aberto, em 0,6 s, e volta ao fechar. A partir de 900 px o cantinho fica à esquerda do
  painel; abaixo disso, acima da folha. Com "reduzir movimento" a troca é direta.
- **Com "Exibir detalhes do pet" desligado,** a pilha fica só com a linha "TV".
- **O foco ao ligar e ao parar:** o botão que tinha o foco sai da tela, e o foco vai para o botão novo (Parar ou Ligar a TV). Antes ele
  caía fora do painel, e o Esc não fechava. O defeito era da etapa 1.

**Fora da chave** (`?gosto_visual=1`), o jogo muda em um ponto: o giro da TV. O resto chega ao jogo por dois campos opcionais da cena
(`CENA.sinalTv` e `CENA.mundo.tvEm`), que ficam vazios sem o protótipo.

**Os testes:** `web/app/test/gosto_visual_cantinho.test.ts` (17 testes) e um terceiro teste em `web/app/e2e/gosto_visual_painel.spec.ts`
(o toque na TV, a câmera, o sinal e a pilha sem os detalhes).

**As capturas do jogo** estão em `docs/pranchas/ux-gosto-visual/capturas_codigo/`: `etapa2_painel_camera_1440.jpg`,
`etapa2_sinal_fechado_1440.jpg` e `etapa2_folha_390.jpg`.

**Não feito nesta etapa:**
- a janela pequena nova, que é da etapa 3;
- a área de toque da almofada inteira para o pet sentado (seção 5.3): o toque no pet continua o do sprite;
- a planta sem água foi conferida só pelos testes, não na tela;
- "Mostrar minha tela" com a captura de verdade continua sem teste;
- nenhum revisor (`rev-a11y`, `rev-cena`, `rev-replay`) viu a etapa, e o contraste do ícone sobre a cena não foi medido.

**Pontos para o Matheus ver:**
- **O pet dormindo vai à almofada** e "assiste" de olho fechado. O comportamento é do cantinho do P0 (#820), e esta etapa não o mudou.
- **O chamado segura o sinal** enquanto durar. Um pet com fome por muito tempo fica sem o ícone da TV, e a reação segue no painel.

Os desvios estão em `docs/registro/2026-11.md`, D-UXGV-19 a 24.

---

## 15. A etapa 3 do código: a janela pequena (2026-11-11, Gerente da UX_TELA_PET, Claude Code, Fable 5.2, branch `v3-ux-gosto-visual-c3`)

**O pedido do Matheus (2026-11-11):** "Sim, etapa 3".

**O que mudou** (tudo atrás de `?gosto_visual=1`):
- **O miolo novo** (`web/app/src/gostoVisual/JanelaTv.tsx`), como a prancha `janela_360`: o pet, a reação num balão, a linha "Gosta mais
  de" e dois botões, Carinho e Parar. Saíram as barras, o "de nascença", o tempo junto e a rolagem.
- **O balão fica fora do elemento que espelha o pet** (o problema 4): o "Não curtiu" não aparece mais invertido. Ele diz a reação em
  palavras e troca no ritmo do sinal, no mínimo a cada 3 s.
- **No alto,** o selo "Vendo a sua tela" enquanto a tela do dono é lida; na TV do jogo, a linha "Passando: a TV do jogo" com o programa.
- **A janela é sempre escura,** na pele dos menus (tokens `--hx-*`), e acompanha a pele escolhida: Vidro ou Militar.
- **O Carinho é o do jogo** (UX-GV-7), e entra no registro como o do botão.
- **O teclado:** ao abrir, o foco vai ao Carinho. O Esc fecha a janela, e a TV continua.
- **O leitor de tela** ouve a reação por uma região de status, no mesmo ritmo do painel (uma vez a cada 5 s, no máximo).
- **A vista `PetAssistindo` e as classes `gv-*`** do cartão do P0 saíram do código e do CSS.

**Os testes:** `web/app/test/gosto_visual_janela.test.ts` (11 testes) e um quarto teste em `web/app/e2e/gosto_visual_painel.spec.ts`, que
abre a janela flutuante de verdade no Chrome.

**As capturas do jogo** estão em `docs/pranchas/ux-gosto-visual/capturas_codigo/`: `etapa3_janela_360_vidro.jpg` e
`etapa3_janela_360_militar.jpg`.

**Não feito nem conferido:**
- a janela com a tela do dono de verdade ("Mostrar minha tela") não foi testada, porque o seletor é do navegador; o selo dela está
  coberto só pelo teste da vista;
- a janela não foi aberta num Chrome com tela (só no Chrome sem tela do e2e), então ficar por cima das outras janelas não foi visto;
- o pet aparece um pouco à direita do meio, porque o quadro que a cena entrega não é centrado;
- nenhum revisor (`rev-a11y`, `rev-cena`, `rev-replay`) viu a etapa, e o contraste não foi medido.

Com esta etapa, as três vistas do plano estão no código. Os desvios estão em `docs/registro/2026-11.md`, D-UXGV-25 a 28.
