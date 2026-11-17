# Prancha: o dono inventa uma palavra e o pet aprende (F4)

**Status: APROVADA pelo Matheus em 2026-11-17** ("Aprovo (Recomendado)", em resposta à D-PD-5). A espec é a `docs/ESPEC_V3_PALAVRA_DONO.md`. As decisões de partida (D-PD-1 a
D-PD-4) estão DECIDIDAS, e esta prancha as segue: a palavra liga pelo corpo, a tela diz "liga" e nunca "entende", só texto, Python com
paridade.

É só desenho: HTML estático, sem código do jogo. Os tokens, a HUD, a janela solta e o painel são das pranchas dos lugares, da conta e das
janelas, e o que é novo está em `palavra.css`. Não há cor nova.

## As telas

| a tela | o que mostra | as capturas (`capturas/`) |
|---|---|---|
| `dizer_1920` | o arco do pet (a IT3) com o item novo **Dizer…**, e o painel com o campo, as palavras já ditas como atalho e as vagas | `vidro` e `militar` |
| `ouviu_1920` | o balão do dono (tracejado) sobre o pet; no canto, o caso em que o corpo vence (o balão apagado, com o motivo) | `vidro` e `militar` |
| `liga_1920` | o cartão "Growlmon liga 'zorp' a brincar" (uma vez) e a janela Hábitos com a seção Palavras | `vidro` e `militar` |
| `dizer_390` | o celular: o arco com os pedidos e o Dizer…, e o campo numa folha | `vidro` e `militar` |
| `habitos_390` | o celular: o cartão no alto e a folha Hábitos | `vidro` e `militar` |

## O que é real e o que é desenho

- **Ainda não existe no jogo:** o arco (IT3), os comandos Come, Dorme, Brinca e Cava (EN-9), e o painel de hábitos (WD-1). A prancha os
  desenha como os planos decidiram.
- **Exemplo de layout, nunca dado:** "zorp", "nana", "vem", as forças das barras, as horas e o Growlmon.
- **As 4 vagas e o traço da barra (`H_max/4`)** estão PROPOSTOS, SEM FONTE.

## Como gerar e capturar

```bash
python docs/pranchas/ux-palavra-dono/gerar.py    # os HTML
sh docs/pranchas/ux-palavra-dono/capturar.sh     # as capturas, em capturas/ (jpg)
```

As capturas precisam dos sprites em `D:\Trab\digilab\Assets` (fora do git) e da rede, para as fontes. A pele vem de `?pele=vidro|xcom`,
`?sem` tira as notas amarelas no desktop, e no celular as notas só aparecem com `?notas`.

## O que não foi feito

- Nenhum revisor viu a prancha, e o contraste não foi medido.
- O arco no celular, com o pet perto da borda direita, foi desenhado deslocado para a esquerda. A regra de onde o arco abre perto da borda
  fica para a IT3.
- O teclado do aparelho aberto sobre a folha não foi desenhado.
