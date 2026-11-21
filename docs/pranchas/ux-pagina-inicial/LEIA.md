# Prancha: a página de entrada

**Status: a página A foi a ESCOLHIDA pelo Matheus em 2026-11-12** ("A, a clara", em resposta a "Qual das duas páginas de entrada segue
adiante?"). O esboço B fica na pasta só como registro. As PI-2 a PI-4 continuam abertas. É a tela 6 do `docs/PLANO_V3_CONTA.md` (seção 3: "uma página inicial curta"), da etapa
CN6. O código só vem depois desta prancha aprovada.

**A POC em código (2026-11-12):** `web/app/poc/home/`, descrita em [`POC.md`](POC.md), com as capturas `capturas/poc_390.jpg` e
`capturas/poc_1440.jpg`. Ela resolve o que a seção "O que não foi feito" abaixo deixou: as larguras intermediárias, o movimento, o
contraste medido e a passagem para o jogo (PI-4, PROPOSTO).

**Os pedidos do Matheus (2026-11-12):**
- o primeiro: "monte um layout de página web de entrada, falando sobre o jogo e indicando a começar imediatamente";
- o segundo, com quatro imagens de referência: "Quero que monte a página com esse design mais clean, cyber futurismo, um laboratório
  de IA mesmo misturado com game e estética dos pets sendo fofos, uma página seguindo um pouco a ideia do 'Explore 14k'".

- o terceiro, com mais uma imagem (uma página de jogo escura, com o personagem no meio do nome): "Gere também um esboço usando como
  referência essa imagem";
- o quarto, sobre a captura da rodada 2 e uma captura da página do Valorant: "Baseado nessa prancha, corrija tentando deixar um
  pouco com as formas retas da página do Valorant".

**Há duas páginas na pasta; a A é a que segue:** a **A** (`inicial.html`, clara, de laboratório, já com as formas retas) e a **B**
(`inicial_b.html`, o esboço escuro). As duas dizem as mesmas coisas. A rodada 1 (escura, na pele dos menus) saiu. É só desenho: uma página HTML estática (`inicial.html`), que rola, com a
quebra a 900 px.

## O que veio de cada referência

| a referência | o que a página tomou dela |
|---|---|
| **"Explore 14K"** | a estrutura: a imagem grande com o título em caixa alta e um botão só; as seções numeradas, com o losango e o título no meio; a imagem em moldura no centro; a faixa larga de ponta a ponta; o texto ao lado de uma ficha; a faixa azul do fim, com três colunas |
| **o anel com circuitos** | o espécime: o pet dentro do anel, com as trilhas saindo para os lados |
| **a malha com o "00"** | a malha fina no fundo, as riscas diagonais, os cantos cortados, a borda em degraus da faixa azul |
| **"Design Futures"** | o claro quase branco, com uma cor só de destaque, e os rótulos pequenos espaçados |
| **a página do Valorant** (rodada 3) | só as formas: os cortes retos em degrau entre as faixas, os títulos em caixa alta alinhados a um lado, a moldura de oito lados em camadas no lugar do anel, os botões com a moldura deslocada, os quadradinhos na margem. As cores não vieram |
| **a página escura do jogo de gatos** (esboço B) | a moldura fina com a aba; o nome gigante com o pet por cima das letras; o rabisco inclinado; as riscas; os ladrilhos de cor; o celular com fichas. Não vieram "tap to earn", NFT, moeda por dinheiro nem contagem regressiva: o jogo não tem nada disso |

## A página A, de cima para baixo

| o bloco | o que tem |
|---|---|
| **o herói** | a ilha de verdade (uma captura do jogo); "Crie um Digimon que decide sozinho"; **"Começar agora"**; "No navegador · Sem conta · Sem instalar"; "Já tenho conta: entrar". Embaixo a imagem acaba num corte reto, em degrau, e a linha do Agumon fica sobre uma régua de laboratório: Koromon, Agumon, Greymon, MetalGreymon e WarGreymon, do In-Training ao Mega (pedido do Matheus; a linha é a do jogo, `motor/nomes.ts` e `motor/arena/formas.ts`) |
| **01 · Laboratório aberto** | "Um cérebro que você pode ver": o Agumon na moldura de oito lados, a captura real do DigiBrain e a ficha "escolha de agora" |
| **a faixa larga** | uma captura do jogo de ponta a ponta: a ilha e o treino |
| **02 · Primeiro dia** | "Do ovo ao primeiro cuidado", os quatro brasões e a ficha dos três passos |
| **03 · O jogo** | a faixa azul: "O ovo está esperando", três colunas (cuidar, treinar, lutar) e o botão de novo |
| **o que o jogo não faz** | sem gacha, sem vantagem à venda, sem culpa, conta opcional |
| **o rodapé** | Termos, Privacidade, Créditos e o crédito do Digimon UP (Bandai) |

**Começar na hora:** o botão está na primeira dobra, na faixa azul do fim e, no celular, numa barra fixa embaixo. Leva direto ao jogo,
sem formulário, porque a CN-1 decidiu que o jogo abre sem conta.

## O esboço B, de cima para baixo

| o bloco | o que tem |
|---|---|
| **o palco** | a ilha escurecida, "DIGI LAB" gigante com o Agumon por cima das letras, "Jogar agora" no canto, a frase embaixo, a ficha dos quatro brasões e o botão redondo |
| **o primeiro dia** | "O ovo é seu", com os bebês soltos pelos lados |
| **a fileira** | os Digimon em ladrilhos de cor, de tamanhos diferentes, e a ilha no horizonte |
| **o DigiBrain** | "Veja o que ele pensa" ao lado de um celular com a captura real do DigiBrain e fichas flutuando |
| **o fim** | "O ovo está esperando", o botão e o rodapé |

É um esboço: o desktop está arrumado; o celular só empilha os blocos e não foi acertado.

## As cores e as fontes

- **As cores** são as do tema claro do jogo (`--dl-*`, cópias de `web/app/src/estilo/tokens.css`): o branco, o azul-gelo, o
  azul-marinho do texto, o azul da ação e o ciano do aprendido. Não há cor nova. A única fora dos tokens é a da nota amarela, que é
  etiqueta da prancha e some com `?sem`.
- **As fontes** são as do guia (seção 4.2): Rajdhani nos títulos, Barlow no texto e DotGothic16 (a do visor) nos rótulos pequenos.

## As capturas (`capturas/`)

Da A: `inicial_1440` (a página inteira, com as notas), `inicial_1440_limpa` (sem as notas), `inicial_1440_dobra` (a primeira dobra a
1440 × 900), `inicial_390` (a página inteira no celular) e `inicial_390_dobra` (a primeira dobra a 390 × 844). Do esboço B, os mesmos cinco nomes com `inicial_b_`.

## O que é real e o que é desenho

- **As imagens do jogo** são capturas que já estavam no repositório: a ilha (2026-11-06), a ilha com o treino (2026-11-11) e o scan do
  DigiBrain do pet de teste.
- **Os pets** são o primeiro quadro (parado) da folha de cada Digimon, em pixels inteiros.
- **Exemplo de layout, nunca dado:** "explorar 48 %, comer 31 %, dormir 21 %" e a ficha "Agumon · Rookie · Coragem".
- **Cada afirmação da página** tem a origem no cabeçalho do `gerar.py`. A página não diz "sem anúncios", porque a CN-12 prevê o vídeo
  pedido pelo jogador para a voz.

## O que a prancha pede ao Matheus

- **PI-1, qual das duas: DECIDIDA, a A** (Matheus, 2026-11-12: "A, a clara"). A pergunta era: a **A** (clara, de laboratório, com as formas retas) ou a **B** (o esboço escuro). **Recomendo a A:** ela é a
  que responde aos seus quatro pedidos juntos, usa só cores que não têm outro sentido no jogo e já está acertada no celular. A B tem
  mais impacto na primeira dobra, e o palco dela (o nome gigante com o pet por cima) pode entrar na A. Custo de errar: baixo, é desenho.
- **PI-2, a frase principal:** "Crie um Digimon que decide sozinho". A outra opção põe o aprendizado na frente ("que aprende com
  você"). Recomendo a primeira: é o que o jogador vê no primeiro minuto. Custo de errar: baixo.
- **PI-3, onde a página mora:** **na raiz do site, com o jogo num caminho próprio.** A outra opção é o jogo na raiz e esta página em
  `/sobre`. Custo de errar: médio, porque muda o endereço que as pessoas guardam; fecha com a sessão da conta, na CN6.
- **PI-4, a página clara e o jogo escuro:** a página usa o tema claro do jogo (`--dl-*`), e os menus do jogo são escuros (Vidro). A
  passagem de uma para o outro, ao clicar em "Começar agora", não foi desenhada. Recomendo aceitar a diferença: a página é a vitrine e o
  jogo é o jogo. Custo de errar: baixo a médio; se a troca parecer brusca, cabe uma tela de carregamento clara.

- **PI-5, as cores dos ladrilhos: não se aplica mais** (a B não foi a escolhida). A pergunta era: os ladrilhos usam o verde do "ok", o rosa da "necessidade", o amarelo do
  "destaque" e o roxo da "sombria", que têm sentido fixo no jogo (guia, seção 3). Para usá-los como enfeite seria preciso criar quatro
  cores de brasão, que hoje não existem. Custo de errar: médio, se o jogador ler o rosa como um chamado.

## Como gerar e capturar

```bash
python docs/pranchas/ux-pagina-inicial/gerar.py    # o HTML (precisa do Pillow e dos sprites)
python docs/pranchas/ux-pagina-inicial/gerar_b.py  # o HTML do esboço B
sh docs/pranchas/ux-pagina-inicial/capturar.sh     # as capturas da A, em D:\Trab\digilab\capturas_ux_pagina_inicial\ (fora do git)
sh docs/pranchas/ux-pagina-inicial/capturar_b.sh   # as do esboço B, na mesma pasta (rodar depois da A, que limpa a pasta)
```

As capturas precisam dos sprites em `D:\Trab\digilab\Assets` (fora do git) e da rede, para as fontes. `?sem` tira as notas amarelas.

## O que não foi feito

- Nenhum revisor viu a prancha, e o contraste não foi medido. O ponto mais fraco é o texto claro sobre a foto do herói.
- As páginas dos Termos, da Privacidade e dos Créditos não estão aqui: os links do rodapé não levam a nada.
- A passagem da página para o jogo (PI-4), a imagem de compartilhamento e os textos para os buscadores.
- As larguras entre 390 e 1440 não foram capturadas; a quebra é uma só, a 900 px.
- O celular do esboço B não foi acertado nem conferido depois do último ajuste.
- Nada se mexe: a prancha é parada. Qualquer animação fica para o código, com a regra do guia (seção 11).
