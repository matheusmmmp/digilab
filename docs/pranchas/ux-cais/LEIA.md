# Prancha: o cais e a semana

**Status: PROPOSTA** (espera a aprovação do Matheus: UX-CA-1 a 7, seção 7 do `docs/PLANO_UX_CAIS.md`). As regras vêm do
`docs/PLANO_V3_MMO.md` (MMO-9, MMO-13 e MMO-14 APROVADAS) e do servidor da MMO5 (`servidor_web/src/envio/semanas.ts`). A tela é da
MMO5 e ainda não foi feita.

É só desenho: HTML estático, sem código do jogo. Os tokens e os moldes são os da prancha dos lugares
(`../ux-lugares-menus/lugares.css` e `movel.css`) e os da conta (`../ux-conta/conta.css`: os estados, os botões). O que é novo está em
`cais.css`. Não há cor nova.

## As telas

| a tela | o que mostra | as capturas (`capturas/`) |
|---|---|---|
| `cais` | a semana aberta: as datas e o estado, os estágios, as primeiras linhas e a de quem olha | `_1920_`, `_390_` e `_360_`, `vidro` e `militar`; `cais_1920_vidro_limpa` (sem as notas) |
| `estados` | os seis estados: buscando, sem resposta, sem conta, tabela vazia, estágio em que não lutou, fechando | `_1920_` |
| `sem_conta` | "As tabelas pedem a conta" na folha baixa do celular | `_390_` |
| `fechada` | a semana fechada, com o resultado de quem olha, e "Conferir a semana" aberto ao lado | `_1920_`; `_390_` (só a tabela) |
| `segredo` | "Conferir a semana" no celular | `_390_` |
| `trancado` | o cais antes do nível 10: o cadeado, "Nv 10" e o marco no balão | `_1920_` |
| `destravado` | o cartão de destrave do cais | `_1920_` |

## O que é real e o que é desenho

- **O fundo** é a captura do jogo de 2026-11-06 da prancha dos lugares, de antes do cais 3D: o lugar do cais nela é só de layout.
- **As caixas** são as da prancha da conta; o cadeado e o cartão de destrave, os da prancha dos lugares.
- **Os textos** são desta prancha; a regra por trás de cada um está no cabeçalho do `gerar.py`.
- **Exemplo de layout, nunca dado:** os apelidos, os pontos, as posições, "14 Tamers", as datas, as horas e o segredo.
- **PROPOSTOS, SEM FONTE:** a folga de 1 h do fechamento, as 100 linhas por tabela e as 12 semanas listadas (`semanas.ts`).

## Como gerar e capturar

```bash
python docs/pranchas/ux-cais/gerar.py    # os HTML
sh docs/pranchas/ux-cais/capturar.sh     # as capturas, em D:\Trab\digilab\capturas_ux_cais\ (fora do git)
```

As capturas precisam dos sprites em `D:\Trab\digilab\Assets` (fora do git) e da rede, para as fontes. A pele vem de
`?pele=vidro|xcom`; no desktop `?sem` tira as notas amarelas, e no celular elas só aparecem com `?notas`.

## O que não foi feito

- Nenhum revisor viu a prancha, e o contraste não foi medido.
- "Ver todas" aberta e a troca de semana pelas setas não estão desenhadas.
- O cais trancado e o destravado só estão a 1920.
