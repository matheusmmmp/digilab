# Prancha: a página de entrada

**Status: PROPOSTA, rodada 2** (2026-11-12). É a tela 6 do `docs/PLANO_V3_CONTA.md` (seção 3: "uma página inicial curta"), da etapa
CN6. O código só vem depois desta prancha aprovada.

**Os pedidos do Matheus (2026-11-12):**
- o primeiro: "monte um layout de página web de entrada, falando sobre o jogo e indicando a começar imediatamente";
- o segundo, com quatro imagens de referência: "Quero que monte a página com esse design mais clean, cyber futurismo, um laboratório
  de IA mesmo misturado com game e estética dos pets sendo fofos, uma página seguindo um pouco a ideia do 'Explore 14k'".

A rodada 1 (escura, na pele dos menus) foi trocada por esta. É só desenho: uma página HTML estática (`inicial.html`), que rola, com a
quebra a 900 px.

## O que veio de cada referência

| a referência | o que a página tomou dela |
|---|---|
| **"Explore 14K"** | a estrutura: a imagem grande com o título em caixa alta e um botão só; as seções numeradas, com o losango e o título no meio; a imagem em moldura no centro; a faixa larga de ponta a ponta; o texto ao lado de uma ficha; a faixa azul do fim, com três colunas |
| **o anel com circuitos** | o espécime: o pet dentro do anel, com as trilhas saindo para os lados |
| **a malha com o "00"** | a malha fina no fundo, as riscas diagonais, os cantos cortados, a borda em degraus da faixa azul |
| **"Design Futures"** | o claro quase branco, com uma cor só de destaque, e os rótulos pequenos espaçados |

## A página, de cima para baixo

| o bloco | o que tem |
|---|---|
| **o herói** | a ilha de verdade (uma captura do jogo); "Crie um Digimon que decide sozinho"; **"Começar agora"**; "No navegador · Sem conta · Sem instalar"; "Já tenho conta: entrar". Embaixo a imagem se desfaz no branco, e seis pets ficam na borda, sobre uma régua de laboratório |
| **01 · Laboratório aberto** | "Um cérebro que você pode ver": o Agumon no anel, a captura real do DigiBrain e a ficha "escolha de agora" |
| **a faixa larga** | uma captura do jogo de ponta a ponta: a ilha e o treino |
| **02 · Primeiro dia** | "Do ovo ao primeiro cuidado", os quatro brasões e a ficha dos três passos |
| **03 · O jogo** | a faixa azul: "O ovo está esperando", três colunas (cuidar, treinar, lutar) e o botão de novo |
| **o que o jogo não faz** | sem gacha, sem vantagem à venda, sem culpa, conta opcional |
| **o rodapé** | Termos, Privacidade, Créditos e o crédito do Digimon UP (Bandai) |

**Começar na hora:** o botão está na primeira dobra, na faixa azul do fim e, no celular, numa barra fixa embaixo. Leva direto ao jogo,
sem formulário, porque a CN-1 decidiu que o jogo abre sem conta.

## As cores e as fontes

- **As cores** são as do tema claro do jogo (`--dl-*`, cópias de `web/app/src/estilo/tokens.css`): o branco, o azul-gelo, o
  azul-marinho do texto, o azul da ação e o ciano do aprendido. Não há cor nova. A única fora dos tokens é a da nota amarela, que é
  etiqueta da prancha e some com `?sem`.
- **As fontes** são as do guia (seção 4.2): Rajdhani nos títulos, Barlow no texto e DotGothic16 (a do visor) nos rótulos pequenos.

## As capturas (`capturas/`)

`inicial_1440` (a página inteira, com as notas), `inicial_1440_limpa` (sem as notas), `inicial_1440_dobra` (a primeira dobra a
1440 × 900), `inicial_390` (a página inteira no celular) e `inicial_390_dobra` (a primeira dobra a 390 × 844).

## O que é real e o que é desenho

- **As imagens do jogo** são capturas que já estavam no repositório: a ilha (2026-11-06), a ilha com o treino (2026-11-11) e o scan do
  DigiBrain do pet de teste.
- **Os pets** são o primeiro quadro (parado) da folha de cada Digimon, em pixels inteiros.
- **Exemplo de layout, nunca dado:** "explorar 48 %, comer 31 %, dormir 21 %" e a ficha "Agumon · Rookie · Coragem".
- **Cada afirmação da página** tem a origem no cabeçalho do `gerar.py`. A página não diz "sem anúncios", porque a CN-12 prevê o vídeo
  pedido pelo jogador para a voz.

## O que a prancha pede ao Matheus

- **PI-1, a prancha inteira (rodada 2):** aprovar para a CN6 usá-la. Recomendo aprovar; o custo de errar é baixo, é desenho.
- **PI-2, a frase principal:** "Crie um Digimon que decide sozinho". A outra opção põe o aprendizado na frente ("que aprende com
  você"). Recomendo a primeira: é o que o jogador vê no primeiro minuto. Custo de errar: baixo.
- **PI-3, onde a página mora:** **na raiz do site, com o jogo num caminho próprio.** A outra opção é o jogo na raiz e esta página em
  `/sobre`. Custo de errar: médio, porque muda o endereço que as pessoas guardam; fecha com a sessão da conta, na CN6.
- **PI-4, a página clara e o jogo escuro:** a página usa o tema claro do jogo (`--dl-*`), e os menus do jogo são escuros (Vidro). A
  passagem de uma para o outro, ao clicar em "Começar agora", não foi desenhada. Recomendo aceitar a diferença: a página é a vitrine e o
  jogo é o jogo. Custo de errar: baixo a médio; se a troca parecer brusca, cabe uma tela de carregamento clara.

## Como gerar e capturar

```bash
python docs/pranchas/ux-pagina-inicial/gerar.py    # o HTML (precisa do Pillow e dos sprites)
sh docs/pranchas/ux-pagina-inicial/capturar.sh     # as capturas, em D:\Trab\digilab\capturas_ux_pagina_inicial\ (fora do git)
```

As capturas precisam dos sprites em `D:\Trab\digilab\Assets` (fora do git) e da rede, para as fontes. `?sem` tira as notas amarelas.

## O que não foi feito

- Nenhum revisor viu a prancha, e o contraste não foi medido. O ponto mais fraco é o texto claro sobre a foto do herói.
- As páginas dos Termos, da Privacidade e dos Créditos não estão aqui: os links do rodapé não levam a nada.
- A passagem da página para o jogo (PI-4), a imagem de compartilhamento e os textos para os buscadores.
- As larguras entre 390 e 1440 não foram capturadas; a quebra é uma só, a 900 px.
- Nada se mexe: a prancha é parada. Qualquer animação fica para o código, com a regra do guia (seção 11).
