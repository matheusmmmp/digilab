# POC: a página de entrada em código

**Status: POC, fora do build do jogo.** É a página A desta pasta (escolhida pelo Matheus em 2026-11-12, PI-1: "A, a clara"), feita em React
+ TypeScript + CSS, em `web/app/poc/home/`. Nenhuma dependência nova, nenhuma rota do app mudou, e o motor, o save e os gabaritos não foram
tocados. O plano de design foi mostrado ao Matheus antes do código e aprovado na sessão ("Sim, pode seguir", 2026-11-12).

```bash
cd web/app
npm run poc                                     # a página em http://localhost:5173/home/ (com os pets do atlas, só no dev)
npm run poc:build                               # o build em web/dist_poc/ (sem o atlas: os pets viram caixas marcadas)
npx playwright test -c playwright.poc.config.ts e2e_poc/home.spec.ts   # o e2e (depois do poc:build)
node poc/home/capturar.mjs                      # as capturas nas seis larguras (com o npm run poc rodando; DIGILAB_URL_HOME muda o endereço)
node poc/home/medir_contraste.mjs saida.json    # o contraste de cada texto contra o fundo real
```

## O que mudou da prancha para a POC, e por quê

| o quê | na prancha | na POC | por quê |
|---|---|---|---|
| **os pets** | o primeiro quadro da folha (o Greymon e o WarGreymon escolhidos à mão, `REGIAO` e `ARQ` do `gerar.py`) | o ciclo parado (Idle) do atlas do jogo, a 120 ms, num canvas em escala inteira | é o que o jogo mostra. No atlas, o Greymon já está de olho aberto no quadro 0, e o WarGreymon vem sem a poeira do golpe, então o `REGIAO` e o `ARQ` não são mais necessários |
| **a régua no celular** | três pets (Koromon, Agumon, Greymon) | os cinco, em escala 1, em duas fileiras | a linha inteira, do In-Training ao Mega, cabe a 360 px |
| **"Cuidar" na faixa azul** | o Tokomon | o Tanemon | o Tokomon não está no atlas do jogo; o Tanemon é um In-Training do jogo (limo) |
| **a ficha "Escolha de agora"** | as porcentagens marcadas como exemplo só na nota amarela | um selo "exemplo" na própria ficha | a página diz "Nada ali é texto inventado" logo acima, e a nota amarela não vai ao ar (guia, princípio 1) |
| **o véu do herói** | navy-deep a 90 % até 30 % da largura, 34 % em 62 % | 92 % até 40 %, 86 % até 66 %, some em 92 %; o título um pouco menor nas larguras grandes (92 px no máximo, era 104) | o "que decide sozinho" em ciano passava sobre a grama clara: o pior pixel dava 1,93:1 a 1440 px |
| **"Entrar"** | `#/config/conta`, que não existe no jogo | o caminho do jogo (`JOGO`), por enquanto | a conta vem com a CN2; o texto fica, como na prancha |
| **as imagens** | os arquivos das outras pranchas | cópias em WebP por largura (`srcset`), em `poc/home/img/` | o herói pesa 17 kB no celular, 50 kB a 1920 px |
| **as fontes** | também a Saira Condensed, como reserva | só as três do guia | guia, seção 4.2 |

## As larguras (PROPOSTO, SEM FONTE)

A quebra continua a 900 px. Dentro de cada lado:

| largura | o que muda |
|---|---|
| **até 420** (o 360 e o 390) | uma coluna; "O que o jogo não faz" em uma coluna; a barra fixa embaixo |
| **até 599** | a régua em escala 1, em duas fileiras |
| **600 a 899** (o 768) | o conteúdo em 640 px; a régua em escala 2 numa fileira só; as três colunas da faixa azul lado a lado; as fichas do espécime com no máximo 460 px, e a captura do DigiBrain no tamanho natural, sem esticar |
| **900 a 1199** (o 1024) | o desktop: a moldura de oito lados em 260 px e as fichas encostadas nas bordas |
| **1440** | a prancha |
| **de 1600** (o 1920) | o conteúdo em 1200 px; a foto e a faixa larga de ponta a ponta |

Nenhuma das seis larguras rola na horizontal (`capturar.mjs` mede `scrollWidth`; o e2e confere a 360, descendo a página inteira). A página
não usa `overflow-x: hidden` no `body` para esconder transbordo.

## O movimento (guia, seção 11)

- **Os pets** tocam o ciclo parado a 120 ms (o `ms_por_quadro` do atlas), só enquanto estão na tela.
- **As seções** entram uma vez ao rolar: 180 ms, `ease-out`, subindo 12 px. O herói não anima.
- **Os botões:** ao passar o mouse, a moldura deslocada encosta; ao pressionar, o botão desce 2 px em 80 ms. Nada pisca nem pulsa.
- **Com `prefers-reduced-motion`,** os pets ficam no quadro 0, as seções já aparecem no lugar, e a cortina não abre: o link segue direto.
  Conferido no Chrome: sem a preferência, o canvas muda de quadro e 9 blocos esperam a rolagem; com ela, nenhum muda e nenhum fica escondido.

## A passagem para o jogo (PI-4, PROPOSTO)

Ao clicar em "Começar agora" ou "Jogar", uma cortina `--dl-navy-deep` sobe de baixo em 360 ms, com a borda em degrau da faixa azul. No
meio dela aparecem o Agumon no ciclo parado e "Abrindo a ilha". Depois de 420 ms a página navega para o jogo. O claro vira escuro no próprio
gesto, antes dos menus Vidro. O clique com Ctrl, Shift ou o botão do meio abre o jogo noutra aba, sem cortina. Voltar pelo histórico
(bfcache) deve reabrir a página sem a cortina (o código trata o `pageshow`; não foi conferido).

**Onde a página mora (PI-3, PROPOSTO):** na raiz do site, com o jogo em `/jogo/` (a constante `JOGO = "/jogo/#/pet"` em `Home.tsx`). O
build da POC não tem o jogo: no e2e, a rota `/jogo/` responde uma página vazia.

## Acessibilidade

- **Foco:** contorno de 3 px, `--dl-action` no claro e `--dl-learned` sobre a foto, na faixa azul e na barra do topo; 9 px de folga nos
  botões, para passar da moldura. Conferido no Chrome a 375 px.
- **Ordem de tabulação** igual à visual: "Pular para o conteúdo" (aparece só com o foco), a marca, os links do topo, "Entrar", "Jogar",
  "Começar agora", "Já tenho conta: entrar", e assim por diante. A barra fixa do celular é a última; enquanto está escondida, fica com
  `visibility: hidden`, fora da tabulação.
- **Alvos de 44 px** em todos os links e botões; "Começar agora" tem 60 px de altura.
- **Contraste:** `medir_contraste.mjs` deixa todo o texto transparente, captura a página inteira e mede cada linha de texto contra cada
  pixel do fundo real. Resultado em 2026-11-12, nas seis larguras: **nenhum trecho abaixo de 4,5:1 no pior pixel.** No herói, o pior pixel
  de cada texto fica entre 6,55 e 11,23. O menor da página é 5,01 ("Um cérebro que você pode ver", em `--dl-action-press` sobre o branco
  com a malha). Os retângulos medidos são recuados 2 px em cima e embaixo, senão a borda do selo "exemplo" contava como fundo.
- **Imagens:** os pets com o nome da forma no `aria-label` (os decorativos, com o nome escrito ao lado, ficam `aria-hidden`); as barras
  da escolha com "explorar: 48 de 100".

## Sem o atlas

O atlas do Digimon UP fica fora do git, e o Vite da POC só o serve no dev. No build, cada pet vira uma caixa tracejada vermelha
"sprite · Agumon", do tamanho da caixa do ciclo (guia, princípio 8). O console recebe um aviso, não um erro, e o build nem pede o atlas,
porque um 404 viraria erro de console no e2e. As caixas das seis formas estão copiadas em `pet.tsx`; se o atlas mudar e o Digimon ou a
caixa não baterem, o pet mostra "erro" na tela.

## As capturas

`capturas/poc_390.jpg` e `capturas/poc_1440.jpg` são a página inteira, com o movimento reduzido (tudo no lugar). As outras larguras (360,
768, 1024, 1920) e as primeiras dobras ficam em `D:\Trab\digilab\capturas_ux_home_poc\`, fora do git.

## O que não foi feito

- O contraste foi medido só no Chrome, com `deviceScaleFactor` 1. O zoom de 200 % e um leitor de tela não foram testados.
- Nenhum celular de verdade; só o Chrome com a largura emulada.
- Os links do rodapé (Termos, Privacidade, Créditos) continuam sem destino, como na prancha.
- A imagem de compartilhamento e os textos para os buscadores além do `description`.
- A cortina só leva a `/jogo/`, que ainda não existe; ligar a página ao jogo de verdade é da CN6 (PI-3).
- Sem JavaScript, a página é só um aviso com o link "Começar agora" (`<noscript>`): o conteúdo é todo do React.
- O atlas inteiro tem 8 MB: serve para a POC, mas uma página pública pediria uma folha só com os seis pets.
