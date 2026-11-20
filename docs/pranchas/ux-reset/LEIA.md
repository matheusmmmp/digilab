# Prancha: o reset e as duas pontuações

**Status: APROVADA** pelo Matheus em 2026-11-19, pela recomendação (UX-RS-1 a 7, seção 8 do `docs/PLANO_UX_RESET.md`). As regras vêm do `docs/PLANO_V3_MMO.md`
(seções 8 e 9; MMO-15 a MMO-19 APROVADAS em 2026-11-11). A tela é da MMO8 e só começa depois da aprovação.

É só desenho: HTML estático, sem código do jogo. Os tokens e os moldes são os da prancha dos lugares (`../ux-lugares-menus/lugares.css` e
`movel.css`), os da conta (`../ux-conta/conta.css`: o painel, a folha, a caixa de perigo, o aceite) e os do cais (`../ux-cais/cais.css`: a
tabela e as abas). O que é novo está em `reset.css`. Não há cor nova.

## As telas

| a tela | o que mostra | as capturas (`capturas/`) |
|---|---|---|
| `reset` | Aposentar: o pet, a escada do nível do reset, o bônus com as travas, o que vai e o que fica | `_1920_` e `_390_`, `vidro` e `militar`; `reset_1920_vidro_limpa` |
| `confirmar` | a confirmação (o aceite) e, ao lado, o reset feito | `_1920_` e `_390_` |
| `estados` | sem bônus, nível 2, nível 3, sem os 200 pontos, Bits da semana já pagos, sem conta | `_1920_` |
| `perfil` | o perfil com o Respeito do Tamer e os pontos do Digimon, e de onde vem o Respeito | `_1920_` e `_390_`; `perfil_1920_vidro_limpa` |
| `rankings` | as abas do cais: os Tamers pelo Respeito e o máximo histórico dos Digimon | `_1920_` e `_390_` (só os Digimon) |
| `estados_perfil` | sem conta, sem resposta, o Tamer novo, o ranking dos Digimon vazio | `_1920_` |

## O que é real e o que é desenho

- **O fundo** é a captura do jogo de 2026-11-06 da prancha dos lugares.
- **Os sprites** são os do projeto (`Assets/arena_up`, fora do git): WarGrowlmon e Gallantmon pelo quadro 0 da folha.
- **Os textos** são desta prancha; a regra por trás de cada um está no cabeçalho do `gerar.py`.
- **Exemplo de layout, nunca dado:** os apelidos, os pontos, o Respeito, as posições, "Dia 41", "2ª geração", os saldos.
- **PROPOSTOS do plano (SEM FONTE):** 300/600/1 000 de Respeito e 150/400/800 Bits por nível; os 200 pontos conferidos; um reset pago
  por semana; "Tamer Lendário" em 10 000; um nível a cada 1 000 de Respeito; 100 por líder, 500 a Liga, 100 por título, 20 por selo.

## Como gerar e capturar

```bash
python docs/pranchas/ux-reset/gerar.py    # os HTML
sh docs/pranchas/ux-reset/capturar.sh     # as capturas, em D:\Trab\digilab\capturas_ux_reset\ (fora do git)
```

As capturas precisam dos sprites em `D:\Trab\digilab\Assets` (fora do git) e da rede, para as fontes. A pele vem de
`?pele=vidro|xcom`; no desktop `?sem` tira as notas amarelas, e no celular elas só aparecem com `?notas`.

## O que não foi feito

- Nenhum revisor viu a prancha, e o contraste não foi medido.
- A escolha do brasão, Gerações e a tela do cruzamento são as de hoje e não foram redesenhadas.
- "Ver todas" nos dois rankings não está desenhada; o celular a 360 não foi capturado.
