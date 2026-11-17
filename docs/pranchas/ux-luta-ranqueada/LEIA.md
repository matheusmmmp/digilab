# Prancha: a luta ranqueada

**Status: PROPOSTA, à espera do Matheus** (UX-LR-1 a UX-LR-6, na seção 7 do `docs/PLANO_UX_LUTA_RANQUEADA.md`). As regras vêm do
`docs/PLANO_V3_MMO.md` (MMO-5 a MMO-9, MMO-13 e MMO-14 APROVADAS) e do servidor da MMO4 (`servidor_web/src/envio/sementes.ts`). A tela é
da MMO4, depois da aprovação.

É só desenho: HTML estático, sem código do jogo. Os tokens e os moldes são os da prancha dos lugares
(`../ux-lugares-menus/lugares.css` e `movel.css`) e os da conta (`../ux-conta/conta.css`: os estados, os passos, os botões). O que é novo
está em `ranqueada.css`. Não há cor nova.

## As telas

| a tela | o que mostra | as capturas (`capturas/`) |
|---|---|---|
| `arena` | a aba Arena com a escolha "Treino / Ranqueada": o placar, os rivais com o valor, o mapa, o aviso e o botão | `_1920_`, `_390_` e `_360_`, `vidro` e `militar`; `arena_1920_vidro_limpa` (sem as notas) |
| `estados` | os seis estados do pedido: pedindo, sem resposta, limite de hoje, trancada, sem conta, versão antiga | `_1920_` |
| `limite` | o limite de hoje na folha baixa do celular | `_390_` |
| `resultado` | os cinco resultados: a prévia, conferido (vitória e derrota), o servidor viu outra luta, ainda não enviada | `_1920_`; `_390_` (conferido); `celulares_vidro` (as cinco do celular lado a lado) |
| `pendente` | "ainda não enviada" na folha baixa do celular | `_390_` |

## O que é real e o que é desenho

- **O fundo** é a captura do jogo de 2026-11-06 da prancha dos lugares; a HUD em volta é a de lá, simplificada.
- **A caixa** é a da aba Arena da prancha dos lugares. O rival e o mapa são os da Arena de hoje (`TelaLugaresPoc.tsx`).
- **Os textos** são desta prancha; a regra por trás de cada um está no cabeçalho do `gerar.py`.
- **Exemplo de layout, nunca dado:** os oito rivais, "7/10", "60 pontos", "3 rivais vencidos", "Faltam 3 h 12 min".
- **PROPOSTOS, SEM FONTE (plano MMO):** os 20 pontos da faixa Champion, a metade para o rival repetido e as 10 lutas por dia.

## Como gerar e capturar

```bash
python docs/pranchas/ux-luta-ranqueada/gerar.py    # os HTML
sh docs/pranchas/ux-luta-ranqueada/capturar.sh     # as capturas, em D:\Trab\digilab\capturas_ux_luta_ranqueada\ (fora do git)
```

As capturas precisam dos sprites em `D:\Trab\digilab\Assets` (fora do git) e da rede, para as fontes. A pele vem de
`?pele=vidro|xcom`; no desktop `?sem` tira as notas amarelas, e no celular elas só aparecem com `?notas`.

## O que não foi feito

- Nenhum revisor viu a prancha, e o contraste não foi medido.
- O retrato do rival não aparece na linha do resultado.
- As tabelas da semana e o cais (MMO5) não estão aqui.
