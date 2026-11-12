# Prancha: a página de entrada

**Status: PROPOSTA** (2026-11-12). É a tela 6 do `docs/PLANO_V3_CONTA.md` (seção 3: "uma página inicial curta"), da etapa CN6. O
código só vem depois desta prancha aprovada.

**O pedido do Matheus (2026-11-12):** "monte um layout de página web de entrada, falando sobre o jogo e indicando a começar
imediatamente".

É só desenho: uma página HTML estática (`inicial.html`), que rola, com a quebra a 900 px. Os tokens são os da prancha dos lugares
(`../ux-lugares-menus/lugares.css`, cópias de `web/app/src/estilo/tokens.css`); o que é novo está em `inicial.css`. Não há cor nova.

## A página, de cima para baixo

| o bloco | o que tem |
|---|---|
| **a barra** | a marca, três âncoras, "Entrar" (discreto) e "Jogar" |
| **o herói** | "Crie um Digimon que decide sozinho"; uma frase; **"Começar agora"**; "No navegador · Sem conta · Sem instalar"; "Já tenho conta: entrar"; uma captura real do jogo |
| **como começa** | três passos: o brasão, o ovo, cuidar e ensinar |
| **o jogo** | três faixas com captura: o DigiBrain; treinar, lutar e evoluir; "comece agora, guarde depois" (a conta opcional) |
| **o que o jogo não faz** | sem gacha, sem vantagem à venda, sem culpa, sem conta obrigatória |
| **o fim** | "O ovo está esperando" e o botão de novo |
| **o rodapé** | Termos, Privacidade, Créditos e o crédito do Digimon UP (Bandai) |

**Começar na hora:** o botão principal aparece na primeira dobra, no meio, no fim e, no celular, numa barra fixa embaixo. Ele leva
direto ao jogo, sem formulário, porque a CN-1 decidiu que o jogo abre sem conta.

## As capturas (`capturas/`)

`inicial_1440_vidro` e `_militar` (a página inteira, com as notas), `inicial_1440_vidro_limpa` (sem as notas), `inicial_1440_dobra_*`
(a primeira dobra a 1440 × 900), `inicial_390_*` (a página inteira no celular) e `inicial_390_dobra_*` (a primeira dobra a 390 × 844).

## O que é real e o que é desenho

- **As imagens do jogo** são capturas que já estavam no repositório: a ilha com o treino (2026-11-11), o scan do DigiBrain do pet de
  teste e a arena. A da conta é a prancha `ux-conta`, que ainda não é código.
- **Cada afirmação da página** tem a origem no cabeçalho do `gerar.py`. A página não diz "sem anúncios", porque a CN-12 prevê o vídeo
  pedido pelo jogador para a voz.
- **Os textos** são desta prancha e são PROPOSTOS.

## O que a prancha pede ao Matheus

- **PI-1, a prancha inteira:** aprovar para a CN6 usá-la. Recomendo aprovar; o custo de errar é baixo, é desenho.
- **PI-2, a frase principal:** "Crie um Digimon que decide sozinho". A outra opção é pôr o aprendizado na frente ("Crie um Digimon
  que aprende com você"). Recomendo a primeira: é o que o jogador vê no primeiro minuto. Custo de errar: baixo.
- **PI-3, onde a página mora:** **na raiz do site, com o jogo num caminho próprio.** A outra opção é o jogo na raiz e esta página em
  `/sobre`. Recomendo a raiz: quem chega por um link vê o que é antes de carregar o jogo. Custo de errar: médio, porque muda o endereço
  que as pessoas guardam; decide-se com a sessão da conta, na CN6.
- **PI-4, a pele da página:** escura, na pele Vidro, como os menus. A linguagem clara do guia (seção 2) fica para o jogo. Custo de
  errar: baixo.

## Como gerar e capturar

```bash
python docs/pranchas/ux-pagina-inicial/gerar.py    # o HTML
sh docs/pranchas/ux-pagina-inicial/capturar.sh     # as capturas, em D:\Trab\digilab\capturas_ux_pagina_inicial\ (fora do git)
```

As capturas precisam dos sprites em `D:\Trab\digilab\Assets` (fora do git) e da rede, para as fontes. A pele vem de
`?pele=vidro|xcom`, e `?sem` tira as notas amarelas.

## O que não foi feito

- Nenhum revisor viu a prancha, e o contraste não foi medido.
- As páginas dos Termos, da Privacidade e dos Créditos não estão aqui: os links do rodapé não levam a nada.
- Não há imagem de compartilhamento (a que aparece quando o link é colado numa conversa) nem os textos para os buscadores.
- As larguras entre 390 e 1440 não foram capturadas; a quebra é uma só, a 900 px.
