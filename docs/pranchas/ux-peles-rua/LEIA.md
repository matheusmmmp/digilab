# Prancha: peles de rua, três modelos base

**PR-1 DECIDIDA pelo Matheus em 2026-11-20** ("Zine e Estêncil", em resposta a "Qual modelo de pele segue adiante?"): o **Zine** é o principal e o **Estêncil** é a opção escura. O Arcade não segue e fica na pasta só como registro. **PR-2 a PR-6 DECIDIDAS pelo Matheus em 2026-11-20, pela recomendação** ("Sim, aprovo", em resposta a "Aprova as PR-2 a PR-6 pela recomendação para eu começar o código pelo Estêncil?"). O plano é o `docs/PLANO_UX_PELES_RUA.md`.

É só desenho: HTML estático, sem código do jogo. Três modelos de pele para os menus, no lugar ou ao lado do Vidro e do Militar de hoje:
**1 · Estêncil** (cartaz de rua), **2 · Zine** (colagem de papel) e **3 · Arcade** (adesivo e pixel).

## Como a prancha é montada

Do mesmo jeito que uma pele no jogo: a estrutura das telas é uma só e a pele entra por cima.

| o arquivo | o que tem |
|---|---|
| `base.css` | o esqueleto: as posições e a estrutura das telas, iguais nos três modelos. Nenhuma cor |
| `gerar.py` | as telas e o bloco de tokens de cada modelo (o dicionário `MODELOS`) |
| `estencil.css`, `zine.css`, `arcade.css` | a forma de cada modelo: os cantos, a letra, a textura, os enfeites. Só usam os tokens |
| `gerar_r2.py`, `r2.css`, `estencil_r2.css`, `zine_r2.css` | a rodada 2: as outras telas, só nos dois modelos escolhidos |

## As telas

| a tela | o que mostra | as capturas (`capturas/`) |
|---|---|---|
| `<modelo>_pet` | a tela do pet a 1920 × 950: o topo, o trilho, as janelas, o aviso, a fala, as ações e o minimapa | `_pet` e `_pet_limpa` (sem as notas) |
| `<modelo>_lugar` | Crescer › Treinar: o cabeçalho, as abas, o destaque, os exercícios, os medidores, o botão trancado | `_lugar` e `_lugar_limpa` |
| `<modelo>_celular` | o celular a 390 × 844: a tela do pet e a folha de um lugar | `_celular` |
| `<modelo>_folha` | a folha do modelo: a paleta, as letras, o traço, os botões, as etiquetas, os medidores | `_folha` |
| `comparacao` | o Vidro e o Militar de hoje e os três modelos, no mesmo recorte | `comparacao` |
| `<modelo>_ajustes` (rodada 2) | Ajustes e a parte Exibir: as linhas, as chaves, os volumes | `_ajustes` |
| `<modelo>_lutar` (rodada 2) | Lutar › Arena: os oito rivais, os oito mapas, a aba trancada, o Lutar | `_lutar` |
| `<modelo>_diario` (rodada 2) | Diário › Registro: o topo, o Códice, os filtros, as linhas | `_diario` |
| `<modelo>_scan` (rodada 2) | o DigiBrain aberto e um chamado com "Atender" | `_scan` |
| `<modelo>_estados` (rodada 2) | cada peça nos estados: normal, com o mouse, pressionada, com o foco, desligada, escolhida, trancada | `_estados` |

`<modelo>` é `estencil`, `zine` ou `arcade`; as telas da rodada 2 só existem no `zine` e no `estencil`.

## O que é real e o que é desenho

- **O fundo** é uma captura do jogo de 2026-11-20, sem a HUD (`img/cena_1920.jpg`). As duas peles de hoje na comparação também são
  capturas do jogo desse dia (`img/hoje_vidro.jpg` e `img/hoje_militar.jpg`).
- **O pet** é o primeiro quadro do clipe parado do Agumon, do atlas de clipes que o jogo usa. O recorte fica em `_spr/`, fora do git.
- **As peças** são as da tela do pet e de Crescer › Treinar de hoje; os nomes e os ganhos dos exercícios são os do jogo.
- **Exemplo de layout, nunca dado:** os valores dos medidores, as horas, os Bits, "Tamer Nv 4", "Tô com fome." e o porquê do agora.
- **As cores e as duas fontes novas** (Saira Stencil One e Bungee) são propostas. A cor da nota amarela e o cinza da prancha de
  comparação são da prancha, não de pele nenhuma.

## Como gerar e capturar

```bash
python docs/pranchas/ux-peles-rua/gerar.py    # os HTML e o recorte do sprite
python docs/pranchas/ux-peles-rua/gerar_r2.py # os HTML da rodada 2
sh docs/pranchas/ux-peles-rua/capturar.sh     # as capturas em capturas/ (e em D:\Trab\digilab\capturas_ux_peles_rua\, fora do git)
```

Precisa do Pillow, de `D:\Trab\digilab\Assets` (fora do git) e da rede, para as fontes. `?sem` tira as notas amarelas. O `gerar.py`
imprime o contraste dos pares principais de cada modelo.

## As capturas do jogo (`capturas_codigo/`)

As duas peles já estão no jogo: a Estêncil (`web/app/src/estilo/pele-estencil.css`; a seção 10 do `docs/PLANO_UX_PELES_RUA.md`) e o
Zine (`web/app/src/estilo/pele-zine.css`; a seção 11). A pasta `capturas_codigo/` guarda as capturas do jogo com elas, de 2026-11-20:
- `estencil_*.jpg`, a 1920 × 950: a tela do pet (parado, com fome, chamando e falando), o painel do porquê, Treinar, Lutar, Diário,
  Ajustes, Visual, Exibir, o DigiBrain e Conversar; e `estencil_celular.jpg`, com cinco telas do celular a 390 × 844;
- `lado_a_lado_*.jpg`: o desenho em cima e o jogo embaixo, na Estêncil (a tela do pet, um lugar, Lutar, Diário, Ajustes e o DigiBrain);
- `zine_*.jpg`, a 1920 × 950: a tela do pet (parado, com fome, chamando e falando), Treinar, Lutar, Diário, Ajustes, Visual e o
  DigiBrain; e `zine_celular.jpg`, com cinco telas do celular a 390 × 844;
- `lado_a_lado_zine_*.jpg`: o desenho em cima e o jogo embaixo, no Zine (a tela do pet, um lugar, Lutar, Diário e Ajustes).

Não são geradas pelo `capturar.sh`: saíram de um teste temporário do Playwright sobre o jogo, com o save do
`e2e/pele_estencil.spec.ts`. A conferência do jogo contra a prancha foi feita por uma sessão revisora; os relatórios dela estão fora
do git, em `D:\Trab\digilab\capturas_ux_peles_rua\revisao\` (a Estêncil) e em `D:\Trab\digilab\capturas_ux_peles_rua\revisao_zine\` (o Zine).

## O que não foi feito

- Conversar, as outras abas dos lugares, as telas que abrem sozinhas e a conta não foram desenhados.
- As telas da rodada 2 só a 1920; o celular a 360; o movimento entre os estados.
- O desenho da rede no scan e as linhas do Registro vêm de capturas do jogo de 2026-11-20 (`img/scan_rede.jpg`).
- O contraste foi calculado pelos tokens, não medido na tela.
