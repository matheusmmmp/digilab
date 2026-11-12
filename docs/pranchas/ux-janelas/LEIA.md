# Prancha: as janelas do pet (arrastar, esconder e arrumar)

**Status: PROPOSTA** (2026-11-12). O plano é o `docs/PLANO_UX_JANELAS.md`, com as decisões UX-JN-1 a 7. O código só vem depois desta
prancha aprovada.

É só desenho: HTML estático, sem código do jogo, só do desktop (a 390 há só a lista de Ajustes). Os tokens e a HUD em volta são os da
prancha dos lugares; a caixa dos Ajustes é a da prancha da conta. O que é novo está em `janelas.css`. Não há cor nova.

## As telas

| a tela | o que mostra | as capturas (`capturas/`) |
|---|---|---|
| `padrao_1920` | o arranjo padrão: a pilha de hoje, com cada painel como uma janela solta (a alça e o menu) | `vidro` e `militar` |
| `arrastando_1920` | "Últimas ações" na mão: o lugar de onde saiu, as guias e a sombra do encaixe | `vidro`, `militar`, `vidro_limpa` |
| `arranjo_1920` | um arranjo do jogador: o DigiBrain aberto no meio, "Últimas ações" embaixo, a Evolução escondida | `vidro`, `militar`, `vidro_limpa` |
| `menu_1920` | o menu dos três pontos e o mover pelo teclado | `vidro` e `militar` |
| `exibir_1920` | Ajustes › Exibir: uma chave por janela, os arranjos, "Arrumar as janelas" e "Voltar ao lugar" | `vidro` e `militar` |
| `arrumar_1920` | o modo arrumar (opcional): a grade, os contornos, o canto de redimensionar e a faixa das escondidas | `vidro` e `militar` |
| `exibir_390` | o celular: só as chaves | `vidro` e `militar` |

## O que é real e o que é desenho

- **Os painéis** são os de hoje (Estado atual, Evolução, Últimas ações, DigiBrain), encurtados. A imagem do DigiBrain é uma captura
  real do scan.
- **Exemplo de layout, nunca dado:** os valores dos medidores, as horas, as ações, "Ultimate · 15h 15min" e as posições das janelas.
- **O que já existe no jogo** e a prancha reusa está no cabeçalho do `gerar.py`.

## Como gerar e capturar

```bash
python docs/pranchas/ux-janelas/gerar.py    # os HTML
sh docs/pranchas/ux-janelas/capturar.sh     # as capturas, em D:\Trab\digilab\capturas_ux_janelas\ (fora do git)
```

As capturas precisam dos sprites em `D:\Trab\digilab\Assets` (fora do git) e da rede, para as fontes. A pele vem de
`?pele=vidro|xcom`; `?sem` tira as notas amarelas.

## O que não foi feito

- Nenhum revisor viu a prancha, e o contraste não foi medido.
- A pele Militar foi capturada e não foi olhada; os quadros do menu, do padrão e do modo arrumar também não foram olhados depois de
  capturados.
- O conteúdo de cada janela em outra largura (o redimensionar) não foi desenhado.
